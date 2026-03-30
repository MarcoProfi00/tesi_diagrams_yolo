from __future__ import annotations

import random
import shutil
from pathlib import Path

import albumentations as A
import cv2
import numpy as np
import yaml


SOURCE_ROOT = Path("data/dataset_v3/rf_yolo_1024_rgb")
DEST_ROOT = Path("data/dataset_v3/rf_yolo_1024_rgb_aug_strong")

IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}

# Parametri augmentation forte
ROTATE_MIN = 25
ROTATE_MAX = 45

TRANSLATE_MIN = 0.08
TRANSLATE_MAX = 0.15

SCALE_MIN = 0.93
SCALE_MAX = 1.07

MIN_VISIBILITY = 0.20


def read_yolo_labels(label_path: Path) -> list[list[float]]:
    if not label_path.exists():
        return []

    rows: list[list[float]] = []
    text = label_path.read_text(encoding="utf-8").strip()
    if not text:
        return []

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


def sanitize_yolo_box(box: list[float], eps: float = 1e-7) -> list[float] | None:
    x, y, w, h = map(float, box)

    if w <= eps or h <= eps:
        return None

    x_min = max(0.0, x - w / 2.0)
    y_min = max(0.0, y - h / 2.0)
    x_max = min(1.0, x + w / 2.0)
    y_max = min(1.0, y + h / 2.0)

    new_w = x_max - x_min
    new_h = y_max - y_min

    if new_w <= eps or new_h <= eps:
        return None

    new_x = (x_min + x_max) / 2.0
    new_y = (y_min + y_max) / 2.0

    return [new_x, new_y, new_w, new_h]


def add_light_noise(image: np.ndarray) -> np.ndarray:
    sigma = random.uniform(5.0, 12.0)
    noise = np.random.normal(0, sigma, image.shape).astype(np.float32)
    out = image.astype(np.float32) + noise
    out = np.clip(out, 0, 255).astype(np.uint8)
    return out


def add_light_brightness_contrast(image: np.ndarray) -> np.ndarray:
    alpha = random.uniform(0.92, 1.10)   # contrasto
    beta = random.uniform(-15.0, 15.0)   # luminosità
    out = cv2.convertScaleAbs(image, alpha=alpha, beta=beta)
    return out


def build_transform() -> A.Compose:
    # angolo forte con segno casuale
    angle = random.uniform(ROTATE_MIN, ROTATE_MAX)
    if random.random() < 0.5:
        angle = -angle

    tx = random.uniform(TRANSLATE_MIN, TRANSLATE_MAX)
    ty = random.uniform(TRANSLATE_MIN, TRANSLATE_MAX)

    if random.random() < 0.5:
        tx = -tx
    if random.random() < 0.5:
        ty = -ty

    scale = random.uniform(SCALE_MIN, SCALE_MAX)

    return A.Compose(
        [
            A.Affine(
                scale=scale,
                translate_percent={"x": (tx, tx), "y": (ty, ty)},
                rotate=(angle, angle),
                shear=0,
                fit_output=False,
                border_mode=cv2.BORDER_CONSTANT,
                fill=(255, 255, 255),
                p=1.0,
            ),
        ],
        bbox_params=A.BboxParams(
            format="yolo",
            label_fields=["class_labels"],
            min_visibility=MIN_VISIBILITY,
        ),
    )


def load_dataset_yaml(source_root: Path) -> dict:
    yaml_path = source_root / "data.yaml"
    if not yaml_path.exists():
        return {"path": ".", "train": "train/images", "val": "valid/images", "test": "test/images"}

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


def copy_split_verbatim(split_name: str) -> None:
    src_split = SOURCE_ROOT / split_name
    dst_split = DEST_ROOT / split_name

    if dst_split.exists():
        shutil.rmtree(dst_split)
    shutil.copytree(src_split, dst_split)


def ensure_clean_dest() -> None:
    if DEST_ROOT.exists():
        shutil.rmtree(DEST_ROOT)
    DEST_ROOT.mkdir(parents=True, exist_ok=True)


def process_train_split() -> tuple[int, int]:
    src_img_dir = SOURCE_ROOT / "train" / "images"
    src_lbl_dir = SOURCE_ROOT / "train" / "labels"

    dst_img_dir = DEST_ROOT / "train" / "images"
    dst_lbl_dir = DEST_ROOT / "train" / "labels"

    dst_img_dir.mkdir(parents=True, exist_ok=True)
    dst_lbl_dir.mkdir(parents=True, exist_ok=True)

    image_paths = sorted([p for p in src_img_dir.iterdir() if p.suffix.lower() in IMAGE_EXTS])

    copied_originals = 0
    created_augmented = 0

    for img_path in image_paths:
        stem = img_path.stem
        label_path = src_lbl_dir / f"{stem}.txt"

        # copia immagine originale
        shutil.copy2(img_path, dst_img_dir / img_path.name)

        # copia label originale
        if label_path.exists():
            shutil.copy2(label_path, dst_lbl_dir / label_path.name)
        else:
            (dst_lbl_dir / f"{stem}.txt").write_text("", encoding="utf-8")

        copied_originals += 1

        image = cv2.imread(str(img_path))
        if image is None:
            print(f"[WARN] Impossibile leggere immagine: {img_path}")
            continue

        raw_labels = read_yolo_labels(label_path)

        labels: list[list[float]] = []
        for row in raw_labels:
            cls_id = int(row[0])
            fixed_box = sanitize_yolo_box(row[1:])
            if fixed_box is not None:
                labels.append([float(cls_id), *fixed_box])

        bboxes = [row[1:] for row in labels]
        class_labels = [int(row[0]) for row in labels]

        transformed = None

        # Proviamo più volte perché con rotazioni forti è più facile perdere tutte le box
        for _ in range(10):
            transform = build_transform()

            try:
                candidate = transform(image=image, bboxes=bboxes, class_labels=class_labels)
            except ValueError as e:
                print(f"[WARN] Bbox non valida in {img_path.name}: {e}")
                continue

            if len(bboxes) == 0:
                transformed = candidate
                break

            if len(candidate["bboxes"]) > 0:
                transformed = candidate
                break

        if transformed is None:
            print(f"[WARN] Nessuna augmentazione valida per: {img_path.name}")
            continue

        aug_image = transformed["image"]
        aug_boxes = transformed["bboxes"]
        aug_classes = transformed["class_labels"]

        # lieve perturbazione fotometrica
        if random.random() < 0.75:
            aug_image = add_light_brightness_contrast(aug_image)

        if random.random() < 0.50:
            aug_image = add_light_noise(aug_image)

        aug_rows: list[list[float]] = []
        for cls_id, box in zip(aug_classes, aug_boxes):
            fixed_box = sanitize_yolo_box(list(box))
            if fixed_box is not None:
                aug_rows.append([float(cls_id), *fixed_box])

        aug_img_name = f"{stem}_augstrong1{img_path.suffix.lower()}"
        aug_lbl_name = f"{stem}_augstrong1.txt"

        cv2.imwrite(str(dst_img_dir / aug_img_name), aug_image)
        write_yolo_labels(dst_lbl_dir / aug_lbl_name, aug_rows)

        created_augmented += 1

    return copied_originals, created_augmented


def count_images(folder: Path) -> int:
    return len([p for p in folder.iterdir() if p.suffix.lower() in IMAGE_EXTS])


def main() -> None:
    if not SOURCE_ROOT.exists():
        raise FileNotFoundError(f"Dataset sorgente non trovato: {SOURCE_ROOT}")

    print(f"[INFO] Sorgente: {SOURCE_ROOT}")
    print(f"[INFO] Destinazione: {DEST_ROOT}")

    ensure_clean_dest()

    # valid e test invariati
    print("[INFO] Copia split valid...")
    copy_split_verbatim("valid")

    print("[INFO] Copia split test...")
    copy_split_verbatim("test")

    # train: originali + augmentate forti
    print("[INFO] Elaborazione train con augmentation forte...")
    copied_originals, created_augmented = process_train_split()

    # data.yaml
    dataset_yaml = load_dataset_yaml(SOURCE_ROOT)
    with (DEST_ROOT / "data.yaml").open("w", encoding="utf-8") as f:
        yaml.safe_dump(dataset_yaml, f, sort_keys=False, allow_unicode=True)

    train_count = count_images(DEST_ROOT / "train" / "images")
    valid_count = count_images(DEST_ROOT / "valid" / "images")
    test_count = count_images(DEST_ROOT / "test" / "images")

    print()
    print("=== COMPLETATO ===")
    print(f"Originali train copiate: {copied_originals}")
    print(f"Nuove immagini augmentate create: {created_augmented}")
    print(f"Train finale: {train_count} immagini")
    print(f"Valid finale: {valid_count} immagini")
    print(f"Test finale: {test_count} immagini")
    print(f"Dataset creato in: {DEST_ROOT}")


if __name__ == "__main__":
    main()