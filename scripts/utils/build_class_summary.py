from pathlib import Path
from collections import Counter
import csv
import yaml

# =========================================================
# CONFIGURAZIONE
# =========================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATASET_ROOT = PROJECT_ROOT / "data" / "datasets" / "dataset_v3" / "rf_yolo_1024_rgb"
DATA_YAML = DATASET_ROOT / "data.yaml"

METADATA_DIR = PROJECT_ROOT / "metadata"
OUTPUT_GLOBAL_CSV = METADATA_DIR / "class_summary_global.csv"
OUTPUT_BY_SPLIT_CSV = METADATA_DIR / "class_summary_by_split.csv"


def load_yaml(data_yaml_path: Path):
    with open(data_yaml_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def load_class_names(data):
    names = data.get("names")
    if names is None:
        raise ValueError("Nel data.yaml non trovo la chiave 'names'.")

    if isinstance(names, list):
        return {i: name for i, name in enumerate(names)}

    if isinstance(names, dict):
        return {int(k): v for k, v in names.items()}

    raise TypeError("Formato 'names' non riconosciuto nel data.yaml.")


def resolve_labels_dir(dataset_root: Path, split_name: str) -> Path:
    return dataset_root / split_name / "labels"


def count_classes_in_dir(labels_dir: Path) -> Counter:
    counter = Counter()

    if not labels_dir.exists():
        print(f"Attenzione: cartella non trovata -> {labels_dir}")
        return counter

    txt_files = list(labels_dir.rglob("*.txt"))
    print(f"Trovati {len(txt_files)} file label in: {labels_dir}")

    for txt_file in txt_files:
        with open(txt_file, "r", encoding="utf-8") as f:
            for line in f:
                parts = line.strip().split()
                if not parts:
                    continue
                class_id = int(float(parts[0]))
                counter[class_id] += 1

    return counter


def main() -> None:
    if not DATASET_ROOT.exists():
        raise FileNotFoundError(f"Dataset root non trovata: {DATASET_ROOT}")

    if not DATA_YAML.exists():
        raise FileNotFoundError(f"data.yaml non trovato: {DATA_YAML}")

    data = load_yaml(DATA_YAML)
    class_map = load_class_names(data)

    split_names = ["train", "valid", "test"]

    split_counts = {}
    total_counts = Counter()

    print(f"PROJECT_ROOT : {PROJECT_ROOT}")
    print(f"DATASET_ROOT : {DATASET_ROOT}")
    print(f"DATA_YAML    : {DATA_YAML}\n")

    for split_name in split_names:
        labels_dir = resolve_labels_dir(DATASET_ROOT, split_name)
        print(f"{split_name.upper()} -> {labels_dir}")

        counts = count_classes_in_dir(labels_dir)
        split_counts[split_name] = counts
        total_counts.update(counts)
        print()

    METADATA_DIR.mkdir(parents=True, exist_ok=True)

    # =========================================================
    # CSV GLOBALE
    # =========================================================
    with open(OUTPUT_GLOBAL_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["class_id", "class_name", "total_count"])

        for class_id in sorted(class_map.keys()):
            writer.writerow([
                class_id,
                class_map[class_id],
                total_counts.get(class_id, 0)
            ])

    # =========================================================
    # CSV PER SPLIT
    # =========================================================
    with open(OUTPUT_BY_SPLIT_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            "class_id",
            "class_name",
            "train_count",
            "valid_count",
            "test_count",
            "total_count"
        ])

        for class_id in sorted(class_map.keys()):
            train_count = split_counts["train"].get(class_id, 0)
            valid_count = split_counts["valid"].get(class_id, 0)
            test_count = split_counts["test"].get(class_id, 0)
            total_count = train_count + valid_count + test_count

            writer.writerow([
                class_id,
                class_map[class_id],
                train_count,
                valid_count,
                test_count,
                total_count
            ])

    print("File salvati:")
    print(f"- {OUTPUT_GLOBAL_CSV}")
    print(f"- {OUTPUT_BY_SPLIT_CSV}")


if __name__ == "__main__":
    main()
