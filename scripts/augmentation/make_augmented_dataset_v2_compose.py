from __future__ import annotations

import math
import random
import shutil
from pathlib import Path

import cv2
import yaml
import hashlib
import re


# =========================
# CONFIG
# =========================
SOURCE_ROOT = Path("data/dataset_v3/rf_yolo_1024_rgb")
DEST_ROOT = Path("data/dataset_v3/rf_yolo_1024_rgb_aug_compose")

IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}

# Numero di nuove immagini composte rispetto al numero di immagini originali del train.
# 0.50 = aggiunge circa il 50% di nuove immagini composte
COMPOSITE_RATIO = 0.65

# Spazio bianco tra i due diagrammi
GAP_PX = 10

# Dimensione finale del dataset
TARGET_SIZE = 1024

# Seed per riproducibilità
RANDOM_SEED = 42

PERTURB_PROB = 0.35


# =========================
# LABEL IO
# =========================
def read_yolo_labels(label_path: Path) -> list[list[float]]:
    if not label_path.exists():
        return []

    text = label_path.read_text(encoding="utf-8").strip()
    if not text:
        return []

    rows: list[list[float]] = []
    for line in text.splitlines():
        parts = line.strip().split()
        if len(parts) != 5:
            continue
        cls_id, x, y, w, h = parts
        rows.append([float(cls_id), float(x), float(y), float(w), float(h)])
    return rows


def write_yolo_labels(label_path: Path, rows: list[list[float]]) -> None:
    lines = []
    for row in rows:
        cls_id, x, y, w, h = row
        lines.append(f"{int(cls_id)} {x:.6f} {y:.6f} {w:.6f} {h:.6f}")
    label_path.write_text("\n".join(lines), encoding="utf-8")


# =========================
# BOX UTILS
# =========================
def yolo_to_abs_xywh(
    x: float,
    y: float,
    w: float,
    h: float,
    img_w: int,
    img_h: int,
) -> tuple[float, float, float, float]:
    abs_x = x * img_w
    abs_y = y * img_h
    abs_w = w * img_w
    abs_h = h * img_h
    return abs_x, abs_y, abs_w, abs_h


def abs_xywh_to_yolo(
    x: float,
    y: float,
    w: float,
    h: float,
    img_w: int,
    img_h: int,
) -> list[float]:
    return [x / img_w, y / img_h, w / img_w, h / img_h]


def clamp_box(box: list[float]) -> list[float] | None:
    x, y, w, h = box

    x = min(max(x, 0.0), 1.0)
    y = min(max(y, 0.0), 1.0)
    w = min(max(w, 0.0), 1.0)
    h = min(max(h, 0.0), 1.0)

    if w <= 1e-4 or h <= 1e-4:
        return None
    return [x, y, w, h]

def apply_tiny_final_perturbation(image):
    """
    Piccolissima perturbazione finale:
    lieve variazione di contrasto/luminosità.
    """
    alpha = random.uniform(0.98, 1.03)   # contrasto molto lieve
    beta = random.uniform(-4.0, 4.0)     # luminosità molto lieve
    return cv2.convertScaleAbs(image, alpha=alpha, beta=beta)


# =========================
# DATASET YAML
# =========================
def load_dataset_yaml(source_root: Path) -> dict:
    yaml_path = source_root / "data.yaml"
    if not yaml_path.exists():
        return {
            "path": ".",
            "train": "train/images",
            "val": "valid/images",
            "test": "test/images",
        }

    with yaml_path.open("r", encoding="utf-8") as f:
        data = yaml.safe_load(f)

    names = data.get("names", [])
    if isinstance(names, dict):
        names = [names[k] for k in sorted(names.keys(), key=lambda x: int(x))]

    return {
        "path": ".",
        "train": "train/images",
        "val": "valid/images",
        "test": "test/images",
        "nc": data.get("nc", len(names)),
        "names": names,
    }


# =========================
# FS HELPERS
# =========================
def ensure_clean_dest() -> None:
    if DEST_ROOT.exists():
        shutil.rmtree(DEST_ROOT)
    DEST_ROOT.mkdir(parents=True, exist_ok=True)


def copy_split_verbatim(split_name: str) -> None:
    src_split = SOURCE_ROOT / split_name
    dst_split = DEST_ROOT / split_name

    if dst_split.exists():
        shutil.rmtree(dst_split)
    shutil.copytree(src_split, dst_split)


def list_images(folder: Path) -> list[Path]:
    return sorted([p for p in folder.iterdir() if p.suffix.lower() in IMAGE_EXTS])


def count_images(folder: Path) -> int:
    return len(list_images(folder))

def sanitize_name_part(text: str, max_len: int = 24) -> str:
    text = re.sub(r"[^A-Za-z0-9_-]+", "_", text)
    text = text.strip("_")
    if not text:
        text = "img"
    return text[:max_len]


def make_composite_stem(idx: int, img1_path: Path, img2_path: Path) -> str:
    part1 = sanitize_name_part(img1_path.stem, max_len=24)
    part2 = sanitize_name_part(img2_path.stem, max_len=24)

    unique_src = f"{img1_path.name}|{img2_path.name}|{idx}"
    digest = hashlib.md5(unique_src.encode("utf-8")).hexdigest()[:10]

    return f"compose_{idx:04d}_{part1}_{part2}_{digest}"


# =========================
# IMAGE COMPOSITION
# =========================
"""
    Crea una nuova immagine affiancando img1 e img2 su canvas bianca,
    poi fa resize con padding a target_size x target_size
    senza deformare il contenuto.

    Restituisce:
    - final_img
    - final_rows (YOLO normalized su final_img)
"""
def compose_side_by_side(
    img1,
    labels1: list[list[float]],
    img2,
    labels2: list[list[float]],
    gap_px: int,
    target_size: int,
):
    
    h1, w1 = img1.shape[:2]
    h2, w2 = img2.shape[:2]

    canvas_h = max(h1, h2)
    canvas_w = w1 + gap_px + w2

    # Canvas bianca
    canvas = 255 * (cv2.UMat(canvas_h, canvas_w, cv2.CV_8UC3).get())

    # Centratura verticale dei due diagrammi
    y1_offset = (canvas_h - h1) // 2
    y2_offset = (canvas_h - h2) // 2

    x1_offset = 0
    x2_offset = w1 + gap_px

    canvas[y1_offset:y1_offset + h1, x1_offset:x1_offset + w1] = img1
    canvas[y2_offset:y2_offset + h2, x2_offset:x2_offset + w2] = img2

    abs_rows: list[list[float]] = []

    # Box immagine 1
    for row in labels1:
        cls_id, x, y, w, h = row
        abs_x, abs_y, abs_w, abs_h = yolo_to_abs_xywh(x, y, w, h, w1, h1)
        abs_x += x1_offset
        abs_y += y1_offset
        abs_rows.append([cls_id, abs_x, abs_y, abs_w, abs_h])

    # Box immagine 2
    for row in labels2:
        cls_id, x, y, w, h = row
        abs_x, abs_y, abs_w, abs_h = yolo_to_abs_xywh(x, y, w, h, w2, h2)
        abs_x += x2_offset
        abs_y += y2_offset
        abs_rows.append([cls_id, abs_x, abs_y, abs_w, abs_h])

    # Resize con aspect ratio preservato + padding bianco
    scale = min(target_size / canvas_w, target_size / canvas_h)
    new_w = int(round(canvas_w * scale))
    new_h = int(round(canvas_h * scale))

    resized = cv2.resize(canvas, (new_w, new_h), interpolation=cv2.INTER_AREA)

    final_img = 255 * (cv2.UMat(target_size, target_size, cv2.CV_8UC3).get())

    pad_x = (target_size - new_w) // 2
    pad_y = (target_size - new_h) // 2

    final_img[pad_y:pad_y + new_h, pad_x:pad_x + new_w] = resized

    final_rows: list[list[float]] = []
    for row in abs_rows:
        cls_id, abs_x, abs_y, abs_w, abs_h = row

        new_x = abs_x * scale + pad_x
        new_y = abs_y * scale + pad_y
        new_w_box = abs_w * scale
        new_h_box = abs_h * scale

        yolo_box = abs_xywh_to_yolo(
            new_x, new_y, new_w_box, new_h_box, target_size, target_size
        )
        clamped = clamp_box(yolo_box)
        if clamped is not None:
            final_rows.append([float(cls_id), *clamped])

    return final_img, final_rows


# =========================
# TRAIN PROCESSING
# =========================
def process_train_split() -> tuple[int, int]:
    src_img_dir = SOURCE_ROOT / "train" / "images"
    src_lbl_dir = SOURCE_ROOT / "train" / "labels"

    dst_img_dir = DEST_ROOT / "train" / "images"
    dst_lbl_dir = DEST_ROOT / "train" / "labels"

    dst_img_dir.mkdir(parents=True, exist_ok=True)
    dst_lbl_dir.mkdir(parents=True, exist_ok=True)

    image_paths = list_images(src_img_dir)
    rng = random.Random(RANDOM_SEED)

    # 1) Copia originali train
    copied_originals = 0
    for img_path in image_paths:
        stem = img_path.stem
        label_path = src_lbl_dir / f"{stem}.txt"

        shutil.copy2(img_path, dst_img_dir / img_path.name)

        if label_path.exists():
            shutil.copy2(label_path, dst_lbl_dir / label_path.name)
        else:
            (dst_lbl_dir / f"{stem}.txt").write_text("", encoding="utf-8")

        copied_originals += 1

    # 2) Crea immagini composte
    num_new = max(1, int(round(len(image_paths) * COMPOSITE_RATIO)))
    created_composites = 0

    for idx in range(num_new):
        img1_path, img2_path = rng.sample(image_paths, 2)

        img1 = cv2.imread(str(img1_path))
        img2 = cv2.imread(str(img2_path))

        if img1 is None or img2 is None:
            print(f"[WARN] Immagine non leggibile: {img1_path.name} / {img2_path.name}")
            continue

        lbl1_path = src_lbl_dir / f"{img1_path.stem}.txt"
        lbl2_path = src_lbl_dir / f"{img2_path.stem}.txt"

        labels1 = read_yolo_labels(lbl1_path)
        labels2 = read_yolo_labels(lbl2_path)

        final_img, final_rows = compose_side_by_side(
            img1=img1,
            labels1=labels1,
            img2=img2,
            labels2=labels2,
            gap_px=GAP_PX,
            target_size=TARGET_SIZE,
        )
        if random.random() < PERTURB_PROB:
            final_img = apply_tiny_final_perturbation(final_img)

        new_stem = make_composite_stem(idx, img1_path, img2_path)
        new_img_path = dst_img_dir / f"{new_stem}.jpg"
        new_lbl_path = dst_lbl_dir / f"{new_stem}.txt"

        cv2.imwrite(str(new_img_path), final_img)
        write_yolo_labels(new_lbl_path, final_rows)

        created_composites += 1

    return copied_originals, created_composites


# =========================
# MAIN
# =========================
def main() -> None:
    if not SOURCE_ROOT.exists():
        raise FileNotFoundError(f"Dataset sorgente non trovato: {SOURCE_ROOT}")

    print(f"[INFO] Dataset sorgente: {SOURCE_ROOT}")
    print(f"[INFO] Dataset destinazione: {DEST_ROOT}")

    ensure_clean_dest()

    # valid e test invariati
    print("[INFO] Copia split valid invariato...")
    copy_split_verbatim("valid")

    print("[INFO] Copia split test invariato...")
    copy_split_verbatim("test")

    # train originale + composti
    print("[INFO] Creazione train composto...")
    copied_originals, created_composites = process_train_split()

    # data.yaml aggiornato
    dataset_yaml = load_dataset_yaml(SOURCE_ROOT)
    with (DEST_ROOT / "data.yaml").open("w", encoding="utf-8") as f:
        yaml.safe_dump(dataset_yaml, f, sort_keys=False, allow_unicode=True)

    train_count = count_images(DEST_ROOT / "train" / "images")
    valid_count = count_images(DEST_ROOT / "valid" / "images")
    test_count = count_images(DEST_ROOT / "test" / "images")

    print()
    print("=== COMPLETATO ===")
    print(f"Originali train copiate: {copied_originals}")
    print(f"Nuove immagini composte create: {created_composites}")
    print(f"Train finale: {train_count} immagini")
    print(f"Valid finale: {valid_count} immagini")
    print(f"Test finale: {test_count} immagini")
    print(f"Dataset creato in: {DEST_ROOT}")


if __name__ == "__main__":
    main()