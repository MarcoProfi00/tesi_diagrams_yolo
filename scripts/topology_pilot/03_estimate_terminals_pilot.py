# Per ogni componente con use_for_terminals: true, legge da class_terminals.yaml: quanti terminali ha e dove stanno (left, right, top, bottom)
# Produce
# terminali dentro ogni componente (es: 22.1:t1 e 22.1:t2)
# lista globale di tutti i terminali
# immagine di debug con terminali disegnati

from pathlib import Path
import json
import yaml
import cv2

# =========================================================
# CONFIGURAZIONE
# =========================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

INPUT_DIR = PROJECT_ROOT / "outputs" / "topology" / "02_assign_instances"
OUTPUT_DIR = PROJECT_ROOT / "outputs" / "topology" / "03_estimate_terminals"
DEBUG_IMAGES_DIR = OUTPUT_DIR / "debug_images"

CLASS_TERMINALS_PATH = PROJECT_ROOT / "metadata" / "class_terminals.yaml"

SAVE_DEBUG_IMAGES = True
TERMINAL_RADIUS = 6

# Soglia per decidere verticale/orizzontale in modalità automatica
ASPECT_RATIO_THRESHOLD = 1.10


def load_yaml(path: Path):
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def load_class_metadata(class_terminals_path: Path):
    data = load_yaml(class_terminals_path)
    class_meta = {}

    for k, v in data.items():
        class_meta[int(k)] = v

    return class_meta


def terminal_point_from_bbox(bbox, relative_position: str):
    x1, y1, x2, y2 = bbox
    xc = (x1 + x2) / 2.0
    yc = (y1 + y2) / 2.0

    if relative_position == "left":
        return [round(x1, 2), round(yc, 2)]
    if relative_position == "right":
        return [round(x2, 2), round(yc, 2)]
    if relative_position == "top":
        return [round(xc, 2), round(y1, 2)]
    if relative_position == "bottom":
        return [round(xc, 2), round(y2, 2)]

    raise ValueError(f"relative_position non supportata: {relative_position}")


def infer_orientation_from_bbox(bbox, default_orientation="horizontal"):
    x1, y1, x2, y2 = bbox
    width = max(x2 - x1, 1e-6)
    height = max(y2 - y1, 1e-6)

    if height / width >= ASPECT_RATIO_THRESHOLD:
        return "vertical"
    if width / height >= ASPECT_RATIO_THRESHOLD:
        return "horizontal"

    return default_orientation


def get_terminals_definition(meta: dict, bbox):
    strategy = meta.get("terminal_strategy", "fixed")

    if strategy == "fixed":
        return meta.get("terminals", []), None

    if strategy == "auto_by_aspect_ratio":
        default_orientation = meta.get("default_orientation", "horizontal")
        orientation = infer_orientation_from_bbox(
            bbox, default_orientation=default_orientation
        )

        orientations = meta.get("orientations", {})
        terminals_def = orientations.get(orientation)

        if terminals_def is None:
            raise ValueError(
                f"Nessuna definizione terminali per orientazione '{orientation}'"
            )

        return terminals_def, orientation

    raise ValueError(f"Strategia terminali non supportata: {strategy}")


def estimate_terminals_for_component(component: dict, class_meta: dict):
    class_id = component["class_id"]
    meta = class_meta.get(class_id, {})

    if not component.get("use_for_terminals", False):
        return [], None

    bbox = component["bbox"]
    instance_id = component["instance_id"]

    terminals_def, estimated_orientation = get_terminals_definition(meta, bbox)

    terminals = []

    for term_def in terminals_def:
        term_name = term_def["name"]
        rel_pos = term_def["relative_position"]

        x, y = terminal_point_from_bbox(bbox, rel_pos)

        terminals.append({
            "terminal_id": f"{instance_id}:{term_name}",
            "instance_id": instance_id,
            "component_class_id": class_id,
            "component_class_name": component.get("class_name"),
            "name": term_name,
            "relative_position": rel_pos,
            "estimated_orientation": estimated_orientation,
            "x": x,
            "y": y
        })

    return terminals, estimated_orientation


def draw_terminals(image_bgr, components, terminals):
    out = image_bgr.copy()

    for comp in components:
        x1, y1, x2, y2 = comp["bbox"]
        x1, y1, x2, y2 = map(int, [x1, y1, x2, y2])

        label = comp.get("instance_id", "N/A")

        if comp.get("estimated_orientation"):
            label = f"{label} ({comp['estimated_orientation'][0]})"

        cv2.rectangle(out, (x1, y1), (x2, y2), (0, 255, 0), 2)
        cv2.putText(
            out,
            label,
            (x1, max(y1 - 8, 0)),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            (0, 255, 0),
            2,
            cv2.LINE_AA
        )

    for term in terminals:
        x = int(round(term["x"]))
        y = int(round(term["y"]))
        label = term["terminal_id"]

        cv2.circle(out, (x, y), TERMINAL_RADIUS, (0, 0, 255), -1)
        cv2.putText(
            out,
            label,
            (x + 8, max(y - 8, 0)),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.45,
            (0, 0, 255),
            1,
            cv2.LINE_AA
        )

    return out


def main() -> None:
    if not INPUT_DIR.exists():
        raise FileNotFoundError(f"Cartella input non trovata: {INPUT_DIR}")

    if not CLASS_TERMINALS_PATH.exists():
        raise FileNotFoundError(f"class_terminals.yaml non trovato: {CLASS_TERMINALS_PATH}")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    DEBUG_IMAGES_DIR.mkdir(parents=True, exist_ok=True)

    class_meta = load_class_metadata(CLASS_TERMINALS_PATH)
    json_files = sorted(INPUT_DIR.glob("*.json"))

    if not json_files:
        raise FileNotFoundError(f"Nessun file JSON trovato in: {INPUT_DIR}")

    print(f"Input directory : {INPUT_DIR}")
    print(f"Output directory: {OUTPUT_DIR}")
    print(f"File trovati    : {len(json_files)}\n")

    for i, json_path in enumerate(json_files, start=1):
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        components = data.get("components", [])
        all_terminals = []
        updated_components = []

        for comp in components:
            comp_copy = dict(comp)
            terminals, estimated_orientation = estimate_terminals_for_component(
                comp_copy, class_meta
            )
            comp_copy["terminals"] = terminals
            if estimated_orientation is not None:
                comp_copy["estimated_orientation"] = estimated_orientation

            updated_components.append(comp_copy)
            all_terminals.extend(terminals)

        output_data = dict(data)
        output_data["components"] = updated_components
        output_data["terminals"] = all_terminals
        output_data["n_terminals_estimated"] = len(all_terminals)

        out_json_path = OUTPUT_DIR / json_path.name
        with open(out_json_path, "w", encoding="utf-8") as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)

        if SAVE_DEBUG_IMAGES:
            image_path = Path(output_data["image_path"])
            image_bgr = cv2.imread(str(image_path))
            if image_bgr is not None:
                debug_img = draw_terminals(image_bgr, updated_components, all_terminals)
                out_img_path = DEBUG_IMAGES_DIR / f"{json_path.stem}_terminals.jpg"
                cv2.imwrite(str(out_img_path), debug_img)

        print(
            f"[{i}/{len(json_files)}] {json_path.name} -> "
            f"{len(updated_components)} componenti, {len(all_terminals)} terminali"
        )

    print("\nCompletato.")
    print(f"JSON salvati in: {OUTPUT_DIR}")
    if SAVE_DEBUG_IMAGES:
        print(f"Immagini debug salvate in: {DEBUG_IMAGES_DIR}")


if __name__ == "__main__":
    main()