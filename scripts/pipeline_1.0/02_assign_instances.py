"""
Passo 02: assegnazione degli identificativi di istanza.

Per ogni JSON prodotto dal passo 01:
    1. legge i componenti rilevati;
    2. li raggruppa per class_id;
    3. assegna un instance_id stabile dentro ogni classe;
    4. salva il JSON aggiornato nella cartella del passo 02;
    5. salva anche un'immagine debug con gli instance_id.
"""

from pathlib import Path
import os
import json
from collections import defaultdict
import cv2

# =========================================================
# CONFIGURAZIONE
# =========================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]
PIPELINE_DATASET = os.environ.get(
    "PIPELINE_DATASET",
    "pipeline1.0/batchA"
)

INPUT_DIR = PROJECT_ROOT / "outputs" / PIPELINE_DATASET / "01_detect_components"
OUTPUT_DIR = PROJECT_ROOT / "outputs" / PIPELINE_DATASET / "02_assign_instances"
DEBUG_IMAGES_DIR = OUTPUT_DIR / "debug_images"

# Ordinamento delle istanze:
# "yx" = dall'alto verso il basso, poi da sinistra a destra
# "xy" = da sinistra a destra, poi dall'alto verso il basso
SORT_ORDER = "xy"

SAVE_DEBUG_IMAGES = True


# Compute center.
def compute_center(bbox):
    x1, y1, x2, y2 = bbox
    xc = (x1 + x2) / 2.0
    yc = (y1 + y2) / 2.0
    return xc, yc


# Sort components.
def sort_components(components, sort_order="yx"):
    # Costruisce la chiave di ordinamento per assegnare id stabili.
    def key_fn(comp):
        bbox = comp["bbox"]
        xc, yc = compute_center(bbox)

        if sort_order == "xy":
            return (xc, yc)
        return (yc, xc)

    return sorted(components, key=key_fn)


# Assign instances to image.
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


# Draw components with instances.
def draw_components_with_instances(image_bgr, components):
    out = image_bgr.copy()
    box_color = (220, 170, 40)
    text_color = (35, 35, 35)
    label_bg_color = (245, 245, 245)
    font = cv2.FONT_HERSHEY_SIMPLEX
    font_scale = 0.46
    font_thickness = 1
    box_thickness = 2
    padding_x = 5
    padding_y = 4

    for comp in components:
        x1, y1, x2, y2 = comp["bbox"]
        x1, y1, x2, y2 = map(int, [x1, y1, x2, y2])

        instance_id = comp.get("instance_id", "N/A")
        class_name = comp.get("class_name", "unknown")
        conf = comp.get("conf", 0.0)

        label = f"{instance_id} | {class_name} | {conf:.2f}"

        cv2.rectangle(out, (x1, y1), (x2, y2), box_color, box_thickness)

        (text_w, text_h), baseline = cv2.getTextSize(label, font, font_scale, font_thickness)
        label_x1 = max(0, x1)
        label_y2 = max(text_h + 2 * padding_y + baseline, y1)
        label_y1 = max(0, label_y2 - (text_h + 2 * padding_y + baseline))
        label_x2 = min(out.shape[1] - 1, label_x1 + text_w + 2 * padding_x)

        overlay = out.copy()
        cv2.rectangle(overlay, (label_x1, label_y1), (label_x2, label_y2), label_bg_color, -1)
        cv2.addWeighted(overlay, 0.88, out, 0.12, 0, out)
        cv2.rectangle(out, (label_x1, label_y1), (label_x2, label_y2), box_color, 1)
        cv2.putText(
            out,
            label,
            (label_x1 + padding_x, label_y2 - baseline - padding_y),
            font,
            font_scale,
            text_color,
            font_thickness,
            cv2.LINE_AA,
        )

    return out


# Salva l'immagine debug con gli instance_id.
def save_debug_image(updated_data: dict, output_image_path: Path):
    image_path = Path(updated_data["image_path"])
    image_bgr = cv2.imread(str(image_path))

    if image_bgr is None:
        print(f"Attenzione: impossibile leggere immagine per debug -> {image_path}")
        return

    debug_img = draw_components_with_instances(image_bgr, updated_data["components"])
    cv2.imwrite(str(output_image_path), debug_img)


# Run the entrypoint for this pipeline stage.
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
