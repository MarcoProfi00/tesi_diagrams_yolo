"""
03_estimate_terminals.py

Scopo:
    Stimare i terminali dei componenti rilevati nel passo 02.

Strategie principali:
    - fixed
    - auto_by_aspect_ratio
    - one_terminal_by_orientation
    - two_terminal_by_connection_axis
    - terminal_auto_one_or_two

Casi speciali:
    - Capacitor / Polarized_Capacitor
    - Switch
    - Terminal
    - Led

    Per i componenti a 3 terminali non basta dire su quale lato cade il terminale
    ma serve anche capire dove si trova realmente lungo quel lato.
    Si usa una localizzazione "side peak": 
    prima stimiamo i lati attivi, poi cerchiamo il picco di connessione lungo il lato.
"""

from pathlib import Path
import os
import json
import cv2

from estimate_terminals.io_utils import io_load_class_metadata, img_build_foreground_binary
from estimate_terminals.processor import estimate_terminals_for_component
from estimate_terminals.debug_draw import draw_terminals
from estimate_terminals.config import SAVE_DEBUG_IMAGES
from estimate_terminals.strategies_opamp import snap_opamp_top_aux_to_nearby_terminal

#PATH / INPUT-OUTPUT
PROJECT_ROOT = Path(__file__).resolve().parents[2]
PIPELINE_DATASET = os.environ.get("PIPELINE_DATASET", "topology_v9.1_analog_meter_connector_transformer")

INPUT_DIR = PROJECT_ROOT / "outputs" / PIPELINE_DATASET / "02_assign_instances"
OUTPUT_DIR = PROJECT_ROOT / "outputs" / PIPELINE_DATASET / "03_estimate_terminals"
DEBUG_IMAGES_DIR = OUTPUT_DIR / "debug_images"

CLASS_TERMINALS_PATH = PROJECT_ROOT / "metadata" / "class_terminals_v1.yaml"

# =========================================================
# MAIN
# =========================================================
# Run the entrypoint for this pipeline stage.
def main() -> None:
    if not INPUT_DIR.exists():
        raise FileNotFoundError(f"Cartella input non trovata: {INPUT_DIR}")
    if not CLASS_TERMINALS_PATH.exists():
        raise FileNotFoundError(f"class_terminals_v1.yaml non trovato: {CLASS_TERMINALS_PATH}")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    DEBUG_IMAGES_DIR.mkdir(parents=True, exist_ok=True)
    class_meta = io_load_class_metadata(CLASS_TERMINALS_PATH)
    json_files = sorted(INPUT_DIR.glob("*.json"))
    if not json_files:
        raise FileNotFoundError(f"Nessun file JSON trovato in: {INPUT_DIR}")

    print(f"Input directory : {INPUT_DIR}")
    print(f"Output directory: {OUTPUT_DIR}")
    print(f"Class yaml      : {CLASS_TERMINALS_PATH}")
    print(f"File trovati    : {len(json_files)}\n")

    for i, json_path in enumerate(json_files, start=1):
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        image_path = Path(data["image_path"])
        image_bgr = cv2.imread(str(image_path))
        if image_bgr is None:
            print(f"Attenzione: immagine non leggibile -> {image_path}")
            continue

        image_binary = img_build_foreground_binary(image_bgr)
        components = data.get("components", [])
        all_terminals = []
        updated_components = []

        for comp in components:
            comp_copy = dict(comp)
            terminals, estimated_orientation, connected_side, side_scores = estimate_terminals_for_component(comp_copy, class_meta, image_binary)
            comp_copy["terminals"] = terminals
            if estimated_orientation is not None:
                comp_copy["estimated_orientation"] = estimated_orientation
            if connected_side is not None:
                comp_copy["estimated_connection_side"] = connected_side
            if side_scores is not None:
                comp_copy["connection_side_scores"] = side_scores
            updated_components.append(comp_copy)
            all_terminals.extend(terminals)

        snap_opamp_top_aux_to_nearby_terminal(updated_components, image_binary)

        output_data = dict(data)
        output_data["components"] = updated_components
        output_data["terminals"] = all_terminals
        output_data["n_terminals_estimated"] = len(all_terminals)

        out_json_path = OUTPUT_DIR / json_path.name
        with open(out_json_path, "w", encoding="utf-8") as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)

        if SAVE_DEBUG_IMAGES:
            debug_img = draw_terminals(image_bgr, updated_components, all_terminals)
            out_img_path = DEBUG_IMAGES_DIR / f"{json_path.stem}_terminals.jpg"
            cv2.imwrite(str(out_img_path), debug_img)

        print(f"[{i}/{len(json_files)}] {json_path.name} -> {len(updated_components)} componenti, {len(all_terminals)} terminali")

    print("\nCompletato.")
    print(f"JSON salvati in: {OUTPUT_DIR}")
    if SAVE_DEBUG_IMAGES:
        print(f"Immagini debug salvate in: {DEBUG_IMAGES_DIR}")


if __name__ == "__main__":
    main()
