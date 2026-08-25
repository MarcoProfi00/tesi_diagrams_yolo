from __future__ import annotations

import random
import shutil
from pathlib import Path

import albumentations as A
import cv2
import numpy as np
import yaml


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATASET_ROOT = PROJECT_ROOT / "data" / "datasets" / "dataset_v3"
SOURCE_ROOT = DATASET_ROOT / "rf_yolo_1024_rgb"
DEST_ROOT = DATASET_ROOT / "rf_yolo_1024_rgb_aug"

IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}


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


def clamp_box(box: list[float]) -> list[float] | None:
    x, y, w, h = box

    x = min(max(x, 0.0), 1.0)
    y = min(max(y, 0.0), 1.0)
    w = min(max(w, 0.0), 1.0)
    h = min(max(h, 0.0), 1.0)

    if w <= 0.0001 or h <= 0.0001:
        return None
    return [x, y, w, h]


def add_light_noise(image: np.ndarray) -> np.ndarray:
    sigma = random.uniform(4.0, 10.0)
    noise = np.random.normal(0, sigma, image.shape).astype(np.float32)
    out = image.astype(np.float32) + noise
    out = np.clip(out, 0, 255).astype(np.uint8)
    return out


def add_light_brightness_contrast(image: np.ndarray) -> np.ndarray:
    alpha = random.uniform(0.95, 1.08)  # contrast
    beta = random.uniform(-10.0, 10.0)  # brightness
    out = cv2.convertScaleAbs(image, alpha=alpha, beta=beta)
    return out


def build_transform() -> A.Compose:
    return A.Compose(
        [
            A.Affine(
                scale=(0.97, 1.03),
                translate_percent={"x": (-0.03, 0.03), "y": (-0.03, 0.03)},
                rotate=(-7, 7),
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
            min_visibility=0.30,
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

    transform = build_transform()

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

        # Se ci sono box, proviamo più volte per evitare di perderli tutti
        for _ in range(5):
            candidate = transform(image=image, bboxes=bboxes, class_labels=class_labels)

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

        # Brightness/contrast lieve
        if random.random() < 0.70:
            aug_image = add_light_brightness_contrast(aug_image)

        # Rumore leggero
        if random.random() < 0.45:
            aug_image = add_light_noise(aug_image)

        aug_rows: list[list[float]] = []
        for cls_id, box in zip(aug_classes, aug_boxes):
            fixed_box = sanitize_yolo_box(list(box))
            if fixed_box is not None:
                aug_rows.append([float(cls_id), *fixed_box])

        aug_img_name = f"{stem}_aug1{img_path.suffix.lower()}"
        aug_lbl_name = f"{stem}_aug1.txt"

        cv2.imwrite(str(dst_img_dir / aug_img_name), aug_image)
        write_yolo_labels(dst_lbl_dir / aug_lbl_name, aug_rows)

        created_augmented += 1

    return copied_originals, created_augmented


def count_images(folder: Path) -> int:
    return len([p for p in folder.iterdir() if p.suffix.lower() in IMAGE_EXTS])

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

    # train: originali + augmentate
    print("[INFO] Elaborazione train con augmentation...")
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
