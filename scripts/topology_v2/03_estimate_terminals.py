from pathlib import Path
import json
import yaml
import cv2

PROJECT_ROOT = Path(__file__).resolve().parents[2]

INPUT_DIR = PROJECT_ROOT / "outputs" / "topology_v2" / "02_assign_instances"
OUTPUT_DIR = PROJECT_ROOT / "outputs" / "topology_v2" / "03_estimate_terminals"
DEBUG_IMAGES_DIR = OUTPUT_DIR / "debug_images"

CLASS_TERMINALS_PATH = PROJECT_ROOT / "metadata" / "class_terminals_v1.yaml"

SAVE_DEBUG_IMAGES = True
TERMINAL_RADIUS = 6
TERMINAL_OUTWARD_OFFSET = 4

ASPECT_RATIO_THRESHOLD = 1.10

SIDE_SAMPLE_THICKNESS = 10
SIDE_CENTER_RATIO = 0.35
SIDE_SCORE_MIN_PIXELS = 5
AXIS_SCORE_MARGIN = 1.15

TERMINAL_PROBE_OUT_LEN = 12
TERMINAL_PROBE_INSET = 2
TERMINAL_PROBE_HALFSPAN_RATIO = 0.22
TERMINAL_PROBE_HALFSPAN_MIN = 3
TERMINAL_PROBE_HALFSPAN_MAX = 8
TERMINAL_PROBE_AXIS_MARGIN = 1.12
TERMINAL_PROBE_MIN_SIDE_SCORE = 3

SWITCH_ANCHOR_RATIOS = (0.30, 0.50, 0.70)


def load_yaml(path: Path):
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def load_class_metadata(class_terminals_path: Path):
    data = load_yaml(class_terminals_path)
    return {int(k): v for k, v in data.items()}


def terminal_point_from_bbox(bbox, relative_position: str):
    x1, y1, x2, y2 = bbox
    xc = (x1 + x2) / 2.0
    yc = (y1 + y2) / 2.0

    if relative_position == "left":
        return [round(x1 - TERMINAL_OUTWARD_OFFSET, 2), round(yc, 2)]
    if relative_position == "right":
        return [round(x2 + TERMINAL_OUTWARD_OFFSET, 2), round(yc, 2)]
    if relative_position == "top":
        return [round(xc, 2), round(y1 - TERMINAL_OUTWARD_OFFSET, 2)]
    if relative_position == "bottom":
        return [round(xc, 2), round(y2 + TERMINAL_OUTWARD_OFFSET, 2)]
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


def build_foreground_binary(image_bgr):
    gray = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2GRAY)
    _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    return binary


def clamp_bbox_to_image(bbox, image_shape):
    h, w = image_shape[:2]
    x1, y1, x2, y2 = bbox
    x1 = int(max(0, min(w - 1, round(x1))))
    y1 = int(max(0, min(h - 1, round(y1))))
    x2 = int(max(0, min(w - 1, round(x2))))
    y2 = int(max(0, min(h - 1, round(y2))))
    return x1, y1, x2, y2


def count_foreground_pixels(binary, x1, y1, x2, y2):
    h, w = binary.shape[:2]
    x1 = max(0, min(w, x1))
    y1 = max(0, min(h, y1))
    x2 = max(0, min(w, x2))
    y2 = max(0, min(h, y2))
    if x2 <= x1 or y2 <= y1:
        return 0
    return int(cv2.countNonZero(binary[y1:y2, x1:x2]))


def detect_connected_side(binary, bbox):
    x1, y1, x2, y2 = clamp_bbox_to_image(bbox, binary.shape)
    xc = int(round((x1 + x2) / 2))
    yc = int(round((y1 + y2) / 2))
    width = max(x2 - x1, 1)
    height = max(y2 - y1, 1)
    half_band_x = max(4, int(width * SIDE_CENTER_RATIO / 2))
    half_band_y = max(4, int(height * SIDE_CENTER_RATIO / 2))

    side_scores = {
        "top": count_foreground_pixels(binary, xc - half_band_x, y1 - SIDE_SAMPLE_THICKNESS, xc + half_band_x + 1, y1),
        "bottom": count_foreground_pixels(binary, xc - half_band_x, y2 + 1, xc + half_band_x + 1, y2 + 1 + SIDE_SAMPLE_THICKNESS),
        "left": count_foreground_pixels(binary, x1 - SIDE_SAMPLE_THICKNESS, yc - half_band_y, x1, yc + half_band_y + 1),
        "right": count_foreground_pixels(binary, x2 + 1, yc - half_band_y, x2 + 1 + SIDE_SAMPLE_THICKNESS, yc + half_band_y + 1),
    }
    best_side = max(side_scores, key=side_scores.get)
    if side_scores[best_side] < SIDE_SCORE_MIN_PIXELS:
        return None, side_scores
    return best_side, side_scores


def resolve_one_terminal_orientation(meta: dict, connected_side: str):
    orientations = meta.get("orientations", {})
    for orientation_name, terminals_def in orientations.items():
        for term_def in terminals_def:
            if term_def.get("relative_position") == connected_side:
                return terminals_def, orientation_name

    default_orientation = meta.get("default_orientation")
    if default_orientation is None:
        raise ValueError("Impossibile risolvere one_terminal_by_orientation e manca default_orientation.")
    terminals_def = orientations.get(default_orientation)
    if terminals_def is None:
        raise ValueError(f"Nessuna definizione terminali per default_orientation '{default_orientation}'")
    return terminals_def, default_orientation


def get_side_scores(binary, bbox):
    x1, y1, x2, y2 = clamp_bbox_to_image(bbox, binary.shape)
    xc = int(round((x1 + x2) / 2))
    yc = int(round((y1 + y2) / 2))
    width = max(x2 - x1, 1)
    height = max(y2 - y1, 1)
    half_band_x = max(4, int(width * SIDE_CENTER_RATIO / 2))
    half_band_y = max(4, int(height * SIDE_CENTER_RATIO / 2))
    return {
        "top": count_foreground_pixels(binary, xc - half_band_x, y1 - SIDE_SAMPLE_THICKNESS, xc + half_band_x + 1, y1),
        "bottom": count_foreground_pixels(binary, xc - half_band_x, y2 + 1, xc + half_band_x + 1, y2 + 1 + SIDE_SAMPLE_THICKNESS),
        "left": count_foreground_pixels(binary, x1 - SIDE_SAMPLE_THICKNESS, yc - half_band_y, x1, yc + half_band_y + 1),
        "right": count_foreground_pixels(binary, x2 + 1, yc - half_band_y, x2 + 1 + SIDE_SAMPLE_THICKNESS, yc + half_band_y + 1),
    }


def _probe_halfspan(width, height):
    min_dim = max(1, min(width, height))
    halfspan = int(round(min_dim * TERMINAL_PROBE_HALFSPAN_RATIO))
    halfspan = max(TERMINAL_PROBE_HALFSPAN_MIN, halfspan)
    halfspan = min(TERMINAL_PROBE_HALFSPAN_MAX, halfspan)
    return halfspan


def get_local_terminal_probe_scores_center(binary, bbox):
    x1, y1, x2, y2 = clamp_bbox_to_image(bbox, binary.shape)
    xc = int(round((x1 + x2) / 2))
    yc = int(round((y1 + y2) / 2))
    width = max(x2 - x1, 1)
    height = max(y2 - y1, 1)
    halfspan = _probe_halfspan(width, height)

    return {
        "top": count_foreground_pixels(binary, xc - halfspan, y1 - TERMINAL_PROBE_OUT_LEN, xc + halfspan + 1, y1 + TERMINAL_PROBE_INSET + 1),
        "bottom": count_foreground_pixels(binary, xc - halfspan, y2 - TERMINAL_PROBE_INSET, xc + halfspan + 1, y2 + TERMINAL_PROBE_OUT_LEN + 1),
        "left": count_foreground_pixels(binary, x1 - TERMINAL_PROBE_OUT_LEN, yc - halfspan, x1 + TERMINAL_PROBE_INSET + 1, yc + halfspan + 1),
        "right": count_foreground_pixels(binary, x2 - TERMINAL_PROBE_INSET, yc - halfspan, x2 + TERMINAL_PROBE_OUT_LEN + 1, yc + halfspan + 1),
        "probe_halfspan": halfspan,
        "probe_out_len": TERMINAL_PROBE_OUT_LEN,
        "probe_inset": TERMINAL_PROBE_INSET,
        "probe_mode": "center",
    }


def get_local_terminal_probe_scores_multi_anchor(binary, bbox, anchor_ratios=SWITCH_ANCHOR_RATIOS):
    x1, y1, x2, y2 = clamp_bbox_to_image(bbox, binary.shape)
    width = max(x2 - x1, 1)
    height = max(y2 - y1, 1)
    halfspan = _probe_halfspan(width, height)

    x_anchors = [int(round(x1 + width * r)) for r in anchor_ratios]
    y_anchors = [int(round(y1 + height * r)) for r in anchor_ratios]

    top_candidates = [
        count_foreground_pixels(binary, xa - halfspan, y1 - TERMINAL_PROBE_OUT_LEN, xa + halfspan + 1, y1 + TERMINAL_PROBE_INSET + 1)
        for xa in x_anchors
    ]
    bottom_candidates = [
        count_foreground_pixels(binary, xa - halfspan, y2 - TERMINAL_PROBE_INSET, xa + halfspan + 1, y2 + TERMINAL_PROBE_OUT_LEN + 1)
        for xa in x_anchors
    ]
    left_candidates = [
        count_foreground_pixels(binary, x1 - TERMINAL_PROBE_OUT_LEN, ya - halfspan, x1 + TERMINAL_PROBE_INSET + 1, ya + halfspan + 1)
        for ya in y_anchors
    ]
    right_candidates = [
        count_foreground_pixels(binary, x2 - TERMINAL_PROBE_INSET, ya - halfspan, x2 + TERMINAL_PROBE_OUT_LEN + 1, ya + halfspan + 1)
        for ya in y_anchors
    ]

    return {
        "top": max(top_candidates) if top_candidates else 0,
        "bottom": max(bottom_candidates) if bottom_candidates else 0,
        "left": max(left_candidates) if left_candidates else 0,
        "right": max(right_candidates) if right_candidates else 0,
        "probe_halfspan": halfspan,
        "probe_out_len": TERMINAL_PROBE_OUT_LEN,
        "probe_inset": TERMINAL_PROBE_INSET,
        "probe_mode": "multi_anchor",
        "x_anchors": x_anchors,
        "y_anchors": y_anchors,
    }


def _decide_axis_from_scores(side_scores):
    lr_pair = min(side_scores["left"], side_scores["right"])
    tb_pair = min(side_scores["top"], side_scores["bottom"])
    lr_score = side_scores["left"] + side_scores["right"]
    tb_score = side_scores["top"] + side_scores["bottom"]

    if lr_pair >= TERMINAL_PROBE_MIN_SIDE_SCORE and lr_score > tb_score * TERMINAL_PROBE_AXIS_MARGIN:
        return "horizontal"
    if tb_pair >= TERMINAL_PROBE_MIN_SIDE_SCORE and tb_score > lr_score * TERMINAL_PROBE_AXIS_MARGIN:
        return "vertical"
    return None


def detect_two_terminal_orientation_generic(binary, bbox, default_orientation="horizontal"):
    side_scores = get_local_terminal_probe_scores_center(binary, bbox)
    orientation = _decide_axis_from_scores(side_scores)
    if orientation is not None:
        side_scores["decision_mode"] = "local_terminal_probes_center"
        return orientation, side_scores

    coarse_scores = get_side_scores(binary, bbox)
    coarse_orientation = None
    lr_score = coarse_scores["left"] + coarse_scores["right"]
    tb_score = coarse_scores["top"] + coarse_scores["bottom"]
    if coarse_scores["left"] >= SIDE_SCORE_MIN_PIXELS and coarse_scores["right"] >= SIDE_SCORE_MIN_PIXELS and lr_score > tb_score * AXIS_SCORE_MARGIN:
        coarse_orientation = "horizontal"
    elif coarse_scores["top"] >= SIDE_SCORE_MIN_PIXELS and coarse_scores["bottom"] >= SIDE_SCORE_MIN_PIXELS and tb_score > lr_score * AXIS_SCORE_MARGIN:
        coarse_orientation = "vertical"

    if coarse_orientation is not None:
        merged = dict(side_scores)
        merged["coarse_scores"] = coarse_scores
        merged["decision_mode"] = "coarse_side_bands_after_local"
        return coarse_orientation, merged

    side_scores["decision_mode"] = "bbox_fallback_after_local_probes"
    return infer_orientation_from_bbox(bbox, default_orientation=default_orientation), side_scores


def detect_two_terminal_orientation_capacitor(binary, bbox, default_orientation="horizontal"):
    side_scores = get_local_terminal_probe_scores_center(binary, bbox)
    orientation = _decide_axis_from_scores(side_scores)
    if orientation is not None:
        side_scores["decision_mode"] = "capacitor_center_probes"
        return orientation, side_scores

    coarse_scores = get_side_scores(binary, bbox)
    lr_score = coarse_scores["left"] + coarse_scores["right"]
    tb_score = coarse_scores["top"] + coarse_scores["bottom"]
    if coarse_scores["left"] >= SIDE_SCORE_MIN_PIXELS and coarse_scores["right"] >= SIDE_SCORE_MIN_PIXELS and lr_score > tb_score * AXIS_SCORE_MARGIN:
        merged = dict(side_scores)
        merged["coarse_scores"] = coarse_scores
        merged["decision_mode"] = "capacitor_coarse_center_bands"
        return "horizontal", merged
    if coarse_scores["top"] >= SIDE_SCORE_MIN_PIXELS and coarse_scores["bottom"] >= SIDE_SCORE_MIN_PIXELS and tb_score > lr_score * AXIS_SCORE_MARGIN:
        merged = dict(side_scores)
        merged["coarse_scores"] = coarse_scores
        merged["decision_mode"] = "capacitor_coarse_center_bands"
        return "vertical", merged

    side_scores["decision_mode"] = "capacitor_bbox_fallback"
    return infer_orientation_from_bbox(bbox, default_orientation=default_orientation), side_scores


def detect_two_terminal_orientation_switch(binary, bbox, default_orientation="horizontal"):
    side_scores = get_local_terminal_probe_scores_multi_anchor(binary, bbox)
    orientation = _decide_axis_from_scores(side_scores)
    if orientation is not None:
        side_scores["decision_mode"] = "switch_multi_anchor_probes"
        return orientation, side_scores

    coarse_scores = get_side_scores(binary, bbox)
    lr_score = coarse_scores["left"] + coarse_scores["right"]
    tb_score = coarse_scores["top"] + coarse_scores["bottom"]
    if coarse_scores["left"] >= SIDE_SCORE_MIN_PIXELS and coarse_scores["right"] >= SIDE_SCORE_MIN_PIXELS and lr_score > tb_score * AXIS_SCORE_MARGIN:
        merged = dict(side_scores)
        merged["coarse_scores"] = coarse_scores
        merged["decision_mode"] = "switch_coarse_side_bands"
        return "horizontal", merged
    if coarse_scores["top"] >= SIDE_SCORE_MIN_PIXELS and coarse_scores["bottom"] >= SIDE_SCORE_MIN_PIXELS and tb_score > lr_score * AXIS_SCORE_MARGIN:
        merged = dict(side_scores)
        merged["coarse_scores"] = coarse_scores
        merged["decision_mode"] = "switch_coarse_side_bands"
        return "vertical", merged

    # Per switch aperti il bbox è fuorviante: meglio default_orientation che aspect ratio.
    side_scores["decision_mode"] = "switch_default_orientation_fallback"
    return default_orientation, side_scores


def detect_terminal_auto_one_or_two(binary, bbox, default_side="right"):
    side_scores = get_side_scores(binary, bbox)
    left_ok = side_scores["left"] >= SIDE_SCORE_MIN_PIXELS
    right_ok = side_scores["right"] >= SIDE_SCORE_MIN_PIXELS
    top_ok = side_scores["top"] >= SIDE_SCORE_MIN_PIXELS
    bottom_ok = side_scores["bottom"] >= SIDE_SCORE_MIN_PIXELS
    lr_score = side_scores["left"] + side_scores["right"]
    tb_score = side_scores["top"] + side_scores["bottom"]

    if left_ok and right_ok and lr_score >= tb_score * AXIS_SCORE_MARGIN:
        return [{"name": "t1", "relative_position": "left"}, {"name": "t2", "relative_position": "right"}], "horizontal", side_scores
    if top_ok and bottom_ok and tb_score >= lr_score * AXIS_SCORE_MARGIN:
        return [{"name": "t1", "relative_position": "top"}, {"name": "t2", "relative_position": "bottom"}], "vertical", side_scores

    best_side = max(side_scores, key=side_scores.get)
    if side_scores[best_side] >= SIDE_SCORE_MIN_PIXELS:
        return [{"name": "t1", "relative_position": best_side}], best_side, side_scores
    return [{"name": "t1", "relative_position": default_side}], default_side, side_scores


def get_terminals_definition(meta: dict, bbox, image_binary=None):
    strategy = meta.get("terminal_strategy", "fixed")

    if strategy == "fixed":
        return meta.get("terminals", []), None, None, None

    if strategy == "auto_by_aspect_ratio":
        default_orientation = meta.get("default_orientation", "horizontal")
        orientation = infer_orientation_from_bbox(bbox, default_orientation=default_orientation)
        terminals_def = meta.get("orientations", {}).get(orientation)
        if terminals_def is None:
            raise ValueError(f"Nessuna definizione terminali per orientazione '{orientation}'")
        return terminals_def, orientation, None, None

    if strategy == "one_terminal_by_orientation":
        if image_binary is None:
            raise ValueError("one_terminal_by_orientation richiede image_binary.")
        connected_side, side_scores = detect_connected_side(image_binary, bbox)
        if connected_side is not None:
            terminals_def, orientation = resolve_one_terminal_orientation(meta, connected_side)
            return terminals_def, orientation, connected_side, side_scores
        default_orientation = meta.get("default_orientation")
        terminals_def = meta.get("orientations", {}).get(default_orientation)
        if terminals_def is None:
            raise ValueError(f"Nessuna definizione terminali per default_orientation '{default_orientation}'")
        return terminals_def, default_orientation, None, side_scores

    if strategy in {"two_terminal_by_connection_axis", "two_terminal_capacitor", "two_terminal_switch"}:
        if image_binary is None:
            raise ValueError(f"{strategy} richiede image_binary.")
        default_orientation = meta.get("default_orientation", "horizontal")
        class_name = meta.get("name", "")
        if strategy == "two_terminal_capacitor" or class_name in {"Capacitor", "Polarized_Capacitor"}:
            orientation, side_scores = detect_two_terminal_orientation_capacitor(image_binary, bbox, default_orientation=default_orientation)
        elif strategy == "two_terminal_switch" or class_name == "Switch":
            orientation, side_scores = detect_two_terminal_orientation_switch(image_binary, bbox, default_orientation=default_orientation)
        else:
            orientation, side_scores = detect_two_terminal_orientation_generic(image_binary, bbox, default_orientation=default_orientation)
        terminals_def = meta.get("orientations", {}).get(orientation)
        if terminals_def is None:
            raise ValueError(f"Nessuna definizione terminali per orientazione '{orientation}'")
        return terminals_def, orientation, None, side_scores

    if strategy == "terminal_auto_one_or_two":
        if image_binary is None:
            raise ValueError("terminal_auto_one_or_two richiede image_binary.")
        default_side = meta.get("default_orientation", "right")
        terminals_def, orientation, side_scores = detect_terminal_auto_one_or_two(image_binary, bbox, default_side=default_side)
        return terminals_def, orientation, None, side_scores

    raise ValueError(f"Strategia terminali non supportata: {strategy}")


def estimate_terminals_for_component(component: dict, class_meta: dict, image_binary):
    class_id = component["class_id"]
    meta = class_meta.get(class_id, {})
    if not component.get("use_for_terminals", False):
        return [], None, None, None

    bbox = component["bbox"]
    instance_id = component["instance_id"]
    terminals_def, estimated_orientation, connected_side, side_scores = get_terminals_definition(meta, bbox, image_binary=image_binary)

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
            "estimated_connection_side": connected_side,
            "x": x,
            "y": y,
        })
    return terminals, estimated_orientation, connected_side, side_scores


def draw_terminals(image_bgr, components, terminals):
    out = image_bgr.copy()
    for comp in components:
        x1, y1, x2, y2 = map(int, comp["bbox"])
        label = comp.get("instance_id", "N/A")
        if comp.get("estimated_orientation"):
            label = f"{label} ({comp['estimated_orientation'][0]})"
        cv2.rectangle(out, (x1, y1), (x2, y2), (0, 255, 0), 2)
        cv2.putText(out, label, (x1, max(y1 - 8, 0)), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2, cv2.LINE_AA)

    for term in terminals:
        x = int(round(term["x"]))
        y = int(round(term["y"]))
        cv2.circle(out, (x, y), TERMINAL_RADIUS, (0, 0, 255), -1)
        cv2.putText(out, term["terminal_id"], (x + 8, max(y - 8, 0)), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 0, 255), 1, cv2.LINE_AA)
    return out


def main() -> None:
    if not INPUT_DIR.exists():
        raise FileNotFoundError(f"Cartella input non trovata: {INPUT_DIR}")
    if not CLASS_TERMINALS_PATH.exists():
        raise FileNotFoundError(f"class_terminals_v1.yaml non trovato: {CLASS_TERMINALS_PATH}")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    DEBUG_IMAGES_DIR.mkdir(parents=True, exist_ok=True)
    class_meta = load_class_metadata(CLASS_TERMINALS_PATH)
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

        image_binary = build_foreground_binary(image_bgr)
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
