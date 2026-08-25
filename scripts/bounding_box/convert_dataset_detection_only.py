from __future__ import annotations

import shutil
from pathlib import Path
import yaml

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATASETS_ROOT = PROJECT_ROOT / "data" / "datasets"
SOURCE_ROOT = DATASETS_ROOT / "dataset_v1" / "rf_yolov7_1024_rgb_v1"
DEST_ROOT = DATASETS_ROOT / "dataset_v2" / "rf_yolo_1024_rgb"

IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}


def polygon_to_yolo_bbox(coords: list[float]) -> list[float] | None:
    """
    coords = [x1, y1, x2, y2, ..., xn, yn] normalizzati in [0,1]
    ritorna [xc, yc, w, h]
    """
    if len(coords) < 6 or len(coords) % 2 != 0:
        return None

    xs = coords[0::2]
    ys = coords[1::2]

    xmin = min(xs)
    xmax = max(xs)
    ymin = min(ys)
    ymax = max(ys)

    xc = (xmin + xmax) / 2.0
    yc = (ymin + ymax) / 2.0
    w = xmax - xmin
    h = ymax - ymin

    if w <= 1e-6 or h <= 1e-6:
        return None

    return [xc, yc, w, h]


def clamp_box(box: list[float]) -> list[float] | None:
    x, y, w, h = box
    x = min(max(x, 0.0), 1.0)
    y = min(max(y, 0.0), 1.0)
    w = min(max(w, 0.0), 1.0)
    h = min(max(h, 0.0), 1.0)

    if w <= 1e-6 or h <= 1e-6:
        return None
    return [x, y, w, h]


def convert_label_file(src_label: Path, dst_label: Path) -> tuple[int, int]:
    """
    ritorna:
    - num_boxes_keep
    - num_segments_converted
    """
    if not src_label.exists():
        dst_label.write_text("", encoding="utf-8")
        return 0, 0

    text = src_label.read_text(encoding="utf-8").strip()
    if not text:
        dst_label.write_text("", encoding="utf-8")
        return 0, 0

    out_lines = []
    num_boxes_keep = 0
    num_segments_converted = 0

    for line in text.splitlines():
        parts = line.strip().split()
        if len(parts) < 5:
            continue

        cls_id = int(float(parts[0]))
        values = [float(x) for x in parts[1:]]

        # Caso detection standard: 4 coordinate
        if len(values) == 4:
            box = clamp_box(values)
            if box is not None:
                x, y, w, h = box
                out_lines.append(f"{cls_id} {x:.6f} {y:.6f} {w:.6f} {h:.6f}")
                num_boxes_keep += 1
            continue

        # Caso segmentation polygon: 6+ coordinate, numero pari
        box = polygon_to_yolo_bbox(values)
        if box is not None:
            box = clamp_box(box)
            if box is not None:
                x, y, w, h = box
                out_lines.append(f"{cls_id} {x:.6f} {y:.6f} {w:.6f} {h:.6f}")
                num_segments_converted += 1

    dst_label.write_text("\n".join(out_lines), encoding="utf-8")
    return num_boxes_keep, num_segments_converted


def copy_images_and_convert_labels(split: str) -> tuple[int, int]:
    src_img_dir = SOURCE_ROOT / split / "images"
    src_lbl_dir = SOURCE_ROOT / split / "labels"

    dst_img_dir = DEST_ROOT / split / "images"
    dst_lbl_dir = DEST_ROOT / split / "labels"

    dst_img_dir.mkdir(parents=True, exist_ok=True)
    dst_lbl_dir.mkdir(parents=True, exist_ok=True)

    total_boxes = 0
    total_segments = 0

    for img_path in sorted(src_img_dir.iterdir()):
        if img_path.suffix.lower() not in IMAGE_EXTS:
            continue

        shutil.copy2(img_path, dst_img_dir / img_path.name)

        label_path = src_lbl_dir / f"{img_path.stem}.txt"
        dst_label = dst_lbl_dir / f"{img_path.stem}.txt"

        n_box, n_seg = convert_label_file(label_path, dst_label)
        total_boxes += n_box
        total_segments += n_seg

    return total_boxes, total_segments


def copy_data_yaml():
    src_yaml = SOURCE_ROOT / "data.yaml"
    dst_yaml = DEST_ROOT / "data.yaml"

    if src_yaml.exists():
        data = yaml.safe_load(src_yaml.read_text(encoding="utf-8"))
        if isinstance(data.get("names"), dict):
            names = [data["names"][k] for k in sorted(data["names"].keys(), key=lambda x: int(x))]
            data["names"] = names
            data["nc"] = len(names)
        dst_yaml.write_text(yaml.safe_dump(data, sort_keys=False, allow_unicode=True), encoding="utf-8")


def main():
    if not SOURCE_ROOT.exists():
        raise FileNotFoundError(f"Dataset sorgente non trovato: {SOURCE_ROOT}")

    if DEST_ROOT.exists():
        shutil.rmtree(DEST_ROOT)
    DEST_ROOT.mkdir(parents=True, exist_ok=True)

    global_boxes = 0
    global_segments = 0

    for split in ["train", "valid", "test"]:
        print(f"[INFO] Processing split: {split}")
        n_box, n_seg = copy_images_and_convert_labels(split)
        global_boxes += n_box
        global_segments += n_seg
        print(f"       detection già rettangoli: {n_box}")
        print(f"       poligoni convertiti:      {n_seg}")

    copy_data_yaml()

    print()
    print("=== COMPLETATO ===")
    print(f"Dataset sorgente:     {SOURCE_ROOT}")
    print(f"Dataset convertito:   {DEST_ROOT}")
    print(f"Box già detection:    {global_boxes}")
    print(f"Poligoni convertiti:  {global_segments}")


if __name__ == "__main__":
    main()
