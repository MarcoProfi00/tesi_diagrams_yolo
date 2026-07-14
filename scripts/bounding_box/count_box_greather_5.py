from __future__ import annotations

from pathlib import Path
from collections import defaultdict

SOURCE_ROOT = Path("data/rf_yolov7_1024_rgb_v1")


def scan_label_file(label_path: Path):
    """
    Restituisce:
    - total_lines
    - valid_box_lines (5 valori)
    - segment_like_lines (>5 valori)
    - invalid_lines (<5 valori o formati strani)
    - segment_examples
    """
    if not label_path.exists():
        return 0, 0, 0, 0, []

    text = label_path.read_text(encoding="utf-8").strip()
    if not text:
        return 0, 0, 0, 0, []

    total_lines = 0
    valid_box_lines = 0
    segment_like_lines = 0
    invalid_lines = 0
    segment_examples = []

    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue

        total_lines += 1
        parts = line.split()

        if len(parts) == 5:
            valid_box_lines += 1
        elif len(parts) > 5:
            segment_like_lines += 1
            if len(segment_examples) < 3:
                segment_examples.append(line)
        else:
            invalid_lines += 1

    return total_lines, valid_box_lines, segment_like_lines, invalid_lines, segment_examples


def main():
    if not SOURCE_ROOT.exists():
        raise FileNotFoundError(f"Dataset non trovato: {SOURCE_ROOT}")

    label_files = sorted(SOURCE_ROOT.rglob("labels/*.txt"))

    total_files = 0
    files_with_segments = 0
    total_lines = 0
    total_box_lines = 0
    total_segment_lines = 0
    total_invalid_lines = 0

    segment_file_report = []

    split_stats = defaultdict(lambda: {
        "files": 0,
        "lines": 0,
        "boxes": 0,
        "segments": 0,
        "invalid": 0,
        "files_with_segments": 0,
    })

    for label_path in label_files:
        total_files += 1

        # split = train / valid / test
        split_name = "unknown"
        parts = label_path.parts
        if "train" in parts:
            split_name = "train"
        elif "valid" in parts:
            split_name = "valid"
        elif "test" in parts:
            split_name = "test"

        (
            n_total,
            n_boxes,
            n_segments,
            n_invalid,
            examples
        ) = scan_label_file(label_path)

        split_stats[split_name]["files"] += 1
        split_stats[split_name]["lines"] += n_total
        split_stats[split_name]["boxes"] += n_boxes
        split_stats[split_name]["segments"] += n_segments
        split_stats[split_name]["invalid"] += n_invalid

        total_lines += n_total
        total_box_lines += n_boxes
        total_segment_lines += n_segments
        total_invalid_lines += n_invalid

        if n_segments > 0:
            files_with_segments += 1
            split_stats[split_name]["files_with_segments"] += 1

            segment_file_report.append({
                "file": label_path,
                "split": split_name,
                "segment_lines": n_segments,
                "examples": examples,
            })

    print("=== REPORT GENERALE ===")
    print(f"Dataset: {SOURCE_ROOT}")
    print(f"File label trovati: {total_files}")
    print(f"Totale righe label: {total_lines}")
    print(f"Righe detection normali (5 valori): {total_box_lines}")
    print(f"Righe con >5 valori (segment/poligoni): {total_segment_lines}")
    print(f"Righe invalide (<5 valori o strane): {total_invalid_lines}")
    print(f"File che contengono almeno una riga segment-like: {files_with_segments}")

    print("\n=== REPORT PER SPLIT ===")
    for split in ["train", "valid", "test", "unknown"]:
        if split not in split_stats:
            continue
        s = split_stats[split]
        print(f"\n[{split}]")
        print(f"  File label: {s['files']}")
        print(f"  Totale righe: {s['lines']}")
        print(f"  Box normali: {s['boxes']}")
        print(f"  Segment-like: {s['segments']}")
        print(f"  Invalide: {s['invalid']}")
        print(f"  File con segmenti: {s['files_with_segments']}")

    print("\n=== FILE CON SEGMENTI (primi 30) ===")
    for item in segment_file_report[:30]:
        print(f"\nFile: {item['file']}")
        print(f"Split: {item['split']}")
        print(f"Righe segment-like: {item['segment_lines']}")
        for ex in item["examples"]:
            print(f"  Esempio: {ex}")

    if len(segment_file_report) > 30:
        print(f"\n... altri {len(segment_file_report) - 30} file con segmenti non mostrati ...")


if __name__ == "__main__":
    main()