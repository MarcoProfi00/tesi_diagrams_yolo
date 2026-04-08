# Per ogni file JSON in "outputs/topology_v1/01_detect_components/":
#   1. legge i componenti rilevati
#   2. li raggruppa per class_id
#   3. assegna le singole istanze
#   4. salva il nuovo json in "outputs/topology_v1/02_assign_instances/"
#   5. salva anche una immagine debug con instance_id

from pathlib import Path
import json
from collections import defaultdict
import cv2

# =========================================================
# CONFIGURAZIONE
# =========================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

INPUT_DIR = PROJECT_ROOT / "outputs" / "topology_v3.1_mosfet_transistor" / "01_detect_components"
OUTPUT_DIR = PROJECT_ROOT / "outputs" / "topology_v3.1_mosfet_transistor" / "02_assign_instances"
DEBUG_IMAGES_DIR = OUTPUT_DIR / "debug_images"

# Ordinamento delle istanze:
# "yx" = dall'alto verso il basso, poi da sinistra a destra
# "xy" = da sinistra a destra, poi dall'alto verso il basso
SORT_ORDER = "xy"

SAVE_DEBUG_IMAGES = True


def compute_center(bbox):
    x1, y1, x2, y2 = bbox
    xc = (x1 + x2) / 2.0
    yc = (y1 + y2) / 2.0
    return xc, yc


def sort_components(components, sort_order="yx"):
    def key_fn(comp):
        bbox = comp["bbox"]
        xc, yc = compute_center(bbox)

        if sort_order == "xy":
            return (xc, yc)
        return (yc, xc)

    return sorted(components, key=key_fn)


def assign_instances_to_image(data: dict, sort_order="yx") -> dict:
    components = data.get("components", [])
    grouped = defaultdict(list)

    for comp in components:
        class_id = comp["class_id"]
        grouped[class_id].append(comp)

    updated_components = []

    for class_id, comps in grouped.items():
        comps_sorted = sort_components(comps, sort_order=sort_order)

        for idx, comp in enumerate(comps_sorted, start=1):
            comp_copy = dict(comp)
            comp_copy["instance_id"] = f"{class_id}.{idx}"
            updated_components.append(comp_copy)

    updated_components = sort_components(updated_components, sort_order=sort_order)

    output = dict(data)
    output["components"] = updated_components
    output["instance_assignment_sort_order"] = sort_order
    output["n_components"] = len(updated_components)

    return output


def draw_components_with_instances(image_bgr, components):
    out = image_bgr.copy()

    for comp in components:
        x1, y1, x2, y2 = comp["bbox"]
        x1, y1, x2, y2 = map(int, [x1, y1, x2, y2])

        instance_id = comp.get("instance_id", "N/A")
        class_name = comp.get("class_name", "unknown")
        conf = comp.get("conf", 0.0)

        label = f"{instance_id} | {class_name} | {conf:.2f}"

        cv2.rectangle(out, (x1, y1), (x2, y2), (0, 255, 0), 2)
        cv2.putText(
            out,
            label,
            (x1, max(y1 - 8, 0)),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.50,
            (0, 255, 0),
            2,
            cv2.LINE_AA
        )

    return out


def save_debug_image(updated_data: dict, output_image_path: Path):
    image_path = Path(updated_data["image_path"])
    image_bgr = cv2.imread(str(image_path))

    if image_bgr is None:
        print(f"Attenzione: impossibile leggere immagine per debug -> {image_path}")
        return

    debug_img = draw_components_with_instances(image_bgr, updated_data["components"])
    cv2.imwrite(str(output_image_path), debug_img)


def main() -> None:
    if not INPUT_DIR.exists():
        raise FileNotFoundError(f"Cartella input non trovata: {INPUT_DIR}")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    DEBUG_IMAGES_DIR.mkdir(parents=True, exist_ok=True)

    json_files = sorted(INPUT_DIR.glob("*.json"))

    if not json_files:
        raise FileNotFoundError(f"Nessun file JSON trovato in: {INPUT_DIR}")

    print(f"Input directory : {INPUT_DIR}")
    print(f"Output directory: {OUTPUT_DIR}")
    print(f"File trovati    : {len(json_files)}")
    print(f"SORT_ORDER      : {SORT_ORDER}\n")

    for i, json_path in enumerate(json_files, start=1):
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        updated_data = assign_instances_to_image(data, sort_order=SORT_ORDER)

        out_json_path = OUTPUT_DIR / json_path.name
        with open(out_json_path, "w", encoding="utf-8") as f:
            json.dump(updated_data, f, indent=2, ensure_ascii=False)

        if SAVE_DEBUG_IMAGES:
            out_img_path = DEBUG_IMAGES_DIR / f"{json_path.stem}_instances.jpg"
            save_debug_image(updated_data, out_img_path)

        n_components = len(updated_data.get("components", []))
        print(f"[{i}/{len(json_files)}] {json_path.name} -> {n_components} componenti")

    print("\nCompletato.")
    print(f"Risultati JSON salvati in: {OUTPUT_DIR}")
    if SAVE_DEBUG_IMAGES:
        print(f"Immagini debug salvate in: {DEBUG_IMAGES_DIR}")


if __name__ == "__main__":
    main()