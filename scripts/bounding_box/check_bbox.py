from __future__ import annotations

import random
import shutil
from pathlib import Path

import cv2


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATASET_ROOT = PROJECT_ROOT / "data" / "datasets" / "dataset_v3" / "rf_yolo_1024_rgb"
SPLIT = "train"
OUTPUT_DIR = PROJECT_ROOT / "debug" / "preview_augmented_bboxes_strong_v3"
NUM_SAMPLES = 100
SEED = 42

IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}


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


def load_class_names(dataset_root: Path) -> dict[int, str]:
    yaml_path = dataset_root / "data.yaml"
    if not yaml_path.exists():
        return {}

    import yaml

    with yaml_path.open("r", encoding="utf-8") as f:
        data = yaml.safe_load(f)

    names = data.get("names", [])
    if isinstance(names, dict):
        return {int(k): str(v) for k, v in names.items()}

    if isinstance(names, list):
        return {i: str(name) for i, name in enumerate(names)}

    return {}


def yolo_to_xyxy(box: list[float], img_w: int, img_h: int) -> tuple[int, int, int, int]:
    _, x, y, w, h = box

    x_center = x * img_w
    y_center = y * img_h
    bw = w * img_w
    bh = h * img_h

    x1 = int(round(x_center - bw / 2))
    y1 = int(round(y_center - bh / 2))
    x2 = int(round(x_center + bw / 2))
    y2 = int(round(y_center + bh / 2))

    x1 = max(0, min(x1, img_w - 1))
    y1 = max(0, min(y1, img_h - 1))
    x2 = max(0, min(x2, img_w - 1))
    y2 = max(0, min(y2, img_h - 1))

    return x1, y1, x2, y2


def color_for_class(class_id: int) -> tuple[int, int, int]:
    random.seed(class_id + 12345)
    return (
        random.randint(40, 255),
        random.randint(40, 255),
        random.randint(40, 255),
    )


def draw_boxes(
    image,
    labels: list[list[float]],
    class_names: dict[int, str],
):
    h, w = image.shape[:2]

    for row in labels:
        cls_id = int(row[0])
        x1, y1, x2, y2 = yolo_to_xyxy(row, w, h)
        color = color_for_class(cls_id)
        class_name = class_names.get(cls_id, str(cls_id))
        text = f"{cls_id} - {class_name}"

        cv2.rectangle(image, (x1, y1), (x2, y2), color, 2)

        (tw, th), baseline = cv2.getTextSize(
            text, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1
        )

        text_y1 = max(0, y1 - th - baseline - 6)
        text_y2 = text_y1 + th + baseline + 6
        text_x2 = min(w - 1, x1 + tw + 6)

        cv2.rectangle(image, (x1, text_y1), (text_x2, text_y2), color, -1)
        cv2.putText(
            image,
            text,
            (x1 + 3, text_y2 - baseline - 3),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            (0, 0, 0),
            1,
            cv2.LINE_AA,
        )

    return image


def main() -> None:
    img_dir = DATASET_ROOT / SPLIT / "images"
    lbl_dir = DATASET_ROOT / SPLIT / "labels"

    if not img_dir.exists():
        raise FileNotFoundError(f"Cartella immagini non trovata: {img_dir}")
    if not lbl_dir.exists():
        raise FileNotFoundError(f"Cartella label non trovata: {lbl_dir}")

    image_paths = sorted([p for p in img_dir.iterdir() if p.suffix.lower() in IMAGE_EXTS])
    if not image_paths:
        raise RuntimeError("Nessuna immagine trovata.")

    sample_size = min(NUM_SAMPLES, len(image_paths))

    random.seed(SEED)
    sampled_paths = random.sample(image_paths, sample_size)

    if OUTPUT_DIR.exists():
        shutil.rmtree(OUTPUT_DIR)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    class_names = load_class_names(DATASET_ROOT)

    saved = 0
    empty_labels = 0

    for idx, img_path in enumerate(sampled_paths, start=1):
        stem = img_path.stem
        label_path = lbl_dir / f"{stem}.txt"

        image = cv2.imread(str(img_path))
        if image is None:
            print(f"[WARN] Impossibile leggere: {img_path}")
            continue

        labels = read_yolo_labels(label_path)
        if len(labels) == 0:
            empty_labels += 1

        vis = image.copy()
        vis = draw_boxes(vis, labels, class_names)

        out_name = f"{idx:03d}_{img_path.stem}.jpg"
        out_path = OUTPUT_DIR / out_name
        cv2.imwrite(str(out_path), vis)
        saved += 1

    print()
    print("=== COMPLETATO ===")
    print(f"Dataset: {DATASET_ROOT}")
    print(f"Split: {SPLIT}")
    print(f"Immagini campionate: {sample_size}")
    print(f"Preview salvate: {saved}")
    print(f"Preview senza bbox: {empty_labels}")
    print(f"Cartella output: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
