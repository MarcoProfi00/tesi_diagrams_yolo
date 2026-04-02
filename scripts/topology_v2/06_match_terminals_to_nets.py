from pathlib import Path
import json
import cv2
import numpy as np

# =========================================================
# CONFIGURAZIONE
# =========================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

INPUT_DIR = PROJECT_ROOT / "outputs" / "topology_v2" / "05_build_nets"
OUTPUT_DIR = PROJECT_ROOT / "outputs" / "topology_v2" / "06_match_terminals_to_nets"
DEBUG_DIR = OUTPUT_DIR / "debug_images"

# Ricerca base attorno al terminale.
# Idea: non usare solo un cerchio, ma prima una ricerca direzionale coerente
# con il lato del terminale (left/right/top/bottom), poi fallback circolari.
BASE_DIRECTIONAL_LEN = 18
BASE_DIRECTIONAL_HALFSPAN = 6
BASE_CIRCLE_RADIUS = 10
BASE_FALLBACK_RADIUS = 24

# Per classi più difficili conviene cercare più lontano.
CLASS_SEARCH_OVERRIDES = {
    "Switch": {
        "directional_len": 30,
        "directional_halfspan": 10,
        "circle_radius": 14,
        "fallback_radius": 30,
    },
    "Inductor": {
        "directional_len": 30,
        "directional_halfspan": 10,
        "circle_radius": 14,
        "fallback_radius": 30,
    },
    "Meter": {
        "directional_len": 22,
        "directional_halfspan": 8,
        "circle_radius": 12,
        "fallback_radius": 26,
    },
    "Current_Source": {
        "directional_len": 22,
        "directional_halfspan": 8,
        "circle_radius": 12,
        "fallback_radius": 26,
    },
    "Voltage_Source": {
        "directional_len": 22,
        "directional_halfspan": 8,
        "circle_radius": 12,
        "fallback_radius": 26,
    },
}

# Qualità del match.
CONFIDENT_DISTANCE_HIGH = 6.0
CONFIDENT_DISTANCE_MEDIUM = 12.0
LOW_CONFIDENCE_DISTANCE = 12.0
VERY_LOW_CONFIDENCE_DISTANCE = 24.0

SAVE_DEBUG_IMAGES = True


# ---------------------------------------------------------
# Utility base
# ---------------------------------------------------------

def load_label_map(path: Path) -> np.ndarray:
    if not path.exists():
        raise FileNotFoundError(f"Label map non trovata: {path}")
    return np.load(path)


def build_net_index_map(nets):
    out = {}
    for net in nets:
        out[int(net["net_index"])] = net
    return out


def build_source_label_to_net_index_map(nets):
    out = {}
    for net in nets:
        out[int(net["source_label"])] = int(net["net_index"])
    return out


def clamp_window(x1, y1, x2, y2, w, h):
    return (
        max(0, min(w, x1)),
        max(0, min(h, y1)),
        max(0, min(w, x2)),
        max(0, min(h, y2)),
    )


def get_class_search_params(term: dict):
    params = {
        "directional_len": BASE_DIRECTIONAL_LEN,
        "directional_halfspan": BASE_DIRECTIONAL_HALFSPAN,
        "circle_radius": BASE_CIRCLE_RADIUS,
        "fallback_radius": BASE_FALLBACK_RADIUS,
    }
    params.update(CLASS_SEARCH_OVERRIDES.get(term.get("component_class_name"), {}))
    return params


# ---------------------------------------------------------
# Finestre / maschere di ricerca
# ---------------------------------------------------------

def build_directional_rect(term: dict, shape, radius: int, halfspan: int):
    h, w = shape[:2]
    x = int(round(term["x"]))
    y = int(round(term["y"]))
    rel = term.get("relative_position")

    if rel in {"left", "right"}:
        return clamp_window(x - radius, y - halfspan, x + radius + 1, y + halfspan + 1, w, h)
    if rel in {"top", "bottom"}:
        return clamp_window(x - halfspan, y - radius, x + halfspan + 1, y + radius + 1, w, h)
    return clamp_window(x - radius, y - radius, x + radius + 1, y + radius + 1, w, h)


def collect_labels_in_rect(label_map: np.ndarray, rect):
    x1, y1, x2, y2 = rect
    roi = label_map[y1:y2, x1:x2]
    labels = np.unique(roi)
    labels = [int(v) for v in labels if int(v) > 0]
    return labels


def collect_labels_in_circle(label_map: np.ndarray, x: int, y: int, radius: int):
    h, w = label_map.shape[:2]
    x1 = max(0, x - radius)
    y1 = max(0, y - radius)
    x2 = min(w, x + radius + 1)
    y2 = min(h, y + radius + 1)

    roi = label_map[y1:y2, x1:x2]
    yy, xx = np.ogrid[y1:y2, x1:x2]
    mask = (xx - x) ** 2 + (yy - y) ** 2 <= radius ** 2

    vals = roi[mask]
    labels = np.unique(vals)
    labels = [int(v) for v in labels if int(v) > 0]
    return labels, [x1, y1, x2, y2]


# ---------------------------------------------------------
# Distanze / snap
# ---------------------------------------------------------

def nearest_label_by_pixel_distance(label_map: np.ndarray, x: int, y: int, candidate_labels, rect=None, radius=None):
    if rect is not None:
        x1, y1, x2, y2 = rect
    else:
        h, w = label_map.shape[:2]
        x1 = max(0, x - radius)
        y1 = max(0, y - radius)
        x2 = min(w, x + radius + 1)
        y2 = min(h, y + radius + 1)

    roi = label_map[y1:y2, x1:x2]

    best_label = None
    best_distance = None
    best_point = None

    for lbl in candidate_labels:
        ys, xs = np.where(roi == lbl)
        if len(xs) == 0:
            continue

        xs_global = xs + x1
        ys_global = ys + y1
        d2 = (xs_global - x) ** 2 + (ys_global - y) ** 2
        idx = int(np.argmin(d2))
        dist = float(np.sqrt(d2[idx]))

        if best_distance is None or dist < best_distance:
            best_distance = dist
            best_label = int(lbl)
            best_point = [int(xs_global[idx]), int(ys_global[idx])]

    return best_label, best_distance, best_point


def choose_best_label(label_map: np.ndarray, x: int, y: int, candidate_labels, preferred_label=None, rect=None, radius=None):
    if not candidate_labels:
        return None, None, None, None

    candidate_labels = sorted(set(int(v) for v in candidate_labels if int(v) > 0))

    if preferred_label is not None and preferred_label in candidate_labels:
        chosen_lbl, dist, point = nearest_label_by_pixel_distance(
            label_map, x, y, [preferred_label], rect=rect, radius=radius
        )
        return chosen_lbl, dist, point, "preferred_label"

    if len(candidate_labels) == 1:
        chosen_lbl, dist, point = nearest_label_by_pixel_distance(
            label_map, x, y, candidate_labels, rect=rect, radius=radius
        )
        return chosen_lbl, dist, point, "single_candidate"

    chosen_lbl, dist, point = nearest_label_by_pixel_distance(
        label_map, x, y, candidate_labels, rect=rect, radius=radius
    )
    return chosen_lbl, dist, point, "nearest_candidate"


# ---------------------------------------------------------
# Confidence / warning del match
# ---------------------------------------------------------

def classify_match_confidence(match_status: str, distance_px, search_stage: str, preferred_net_index, component_class_name: str):
    if match_status == "unmatched":
        return "none", ["unmatched_terminal"]

    warnings = []
    distance = None if distance_px is None else float(distance_px)

    if match_status == "matched_preferred" and distance is not None and distance <= CONFIDENT_DISTANCE_HIGH:
        confidence = "high"
    elif distance is not None and distance <= CONFIDENT_DISTANCE_MEDIUM:
        confidence = "medium"
    else:
        confidence = "low"

    if preferred_net_index is None:
        warnings.append("no_preferred_net_from_05")
    if match_status != "matched_preferred":
        warnings.append("matched_without_preferred_label")
    if search_stage in {"directional_fallback", "circle_fallback"}:
        warnings.append("used_fallback_search")
    if search_stage == "circle_primary":
        warnings.append("used_circle_search")
    if distance is not None and distance > LOW_CONFIDENCE_DISTANCE:
        warnings.append("large_snap_distance")
    if distance is not None and distance > VERY_LOW_CONFIDENCE_DISTANCE:
        warnings.append("very_large_snap_distance")
    if component_class_name in {"Switch", "Inductor"} and distance is not None and distance > CONFIDENT_DISTANCE_MEDIUM:
        warnings.append("sensitive_class_large_distance")

    return confidence, warnings


# ---------------------------------------------------------
# Matching terminale -> net
# ---------------------------------------------------------

def get_preferred_net_index(term: dict, source_label_to_net_index: dict, net_building_terminal_debug: dict):
    term_id = term["terminal_id"]
    debug = net_building_terminal_debug.get(term_id, {})
    source_label = debug.get("primary_label")
    if source_label is None:
        return None
    return source_label_to_net_index.get(int(source_label))


def run_search_stage(label_map: np.ndarray, term: dict, stage: dict, preferred_net_index=None):
    x = int(round(term["x"]))
    y = int(round(term["y"]))

    if stage["kind"] == "directional":
        rect = build_directional_rect(
            term,
            label_map.shape,
            radius=stage["radius"],
            halfspan=stage["halfspan"],
        )
        candidate_labels = collect_labels_in_rect(label_map, rect)
        chosen_lbl, dist, point, decision = choose_best_label(
            label_map,
            x,
            y,
            candidate_labels,
            preferred_label=preferred_net_index,
            rect=rect,
        )
        search_window = [int(v) for v in rect]
    elif stage["kind"] == "circle":
        candidate_labels, search_window = collect_labels_in_circle(
            label_map,
            x,
            y,
            radius=stage["radius"],
        )
        chosen_lbl, dist, point, decision = choose_best_label(
            label_map,
            x,
            y,
            candidate_labels,
            preferred_label=preferred_net_index,
            radius=stage["radius"],
        )
    else:
        raise ValueError(f"Stage non supportato: {stage['kind']}")

    return {
        "candidate_labels": candidate_labels,
        "chosen_label": chosen_lbl,
        "distance": dist,
        "snap_point": point,
        "decision_mode": decision,
        "search_window": search_window,
    }


def build_search_plan(term: dict):
    params = get_class_search_params(term)
    directional_len = int(params["directional_len"])
    directional_halfspan = int(params["directional_halfspan"])
    circle_radius = int(params["circle_radius"])
    fallback_radius = int(params["fallback_radius"])

    return [
        {
            "name": "directional_primary",
            "kind": "directional",
            "radius": directional_len,
            "halfspan": directional_halfspan,
        },
        {
            "name": "circle_primary",
            "kind": "circle",
            "radius": circle_radius,
        },
        {
            "name": "directional_fallback",
            "kind": "directional",
            "radius": max(directional_len + 8, fallback_radius),
            "halfspan": directional_halfspan + 3,
        },
        {
            "name": "circle_fallback",
            "kind": "circle",
            "radius": fallback_radius,
        },
    ]


def finalize_match_result(result: dict):
    confidence, warnings = classify_match_confidence(
        match_status=result["match_status"],
        distance_px=result["match_distance_px"],
        search_stage=result["search_stage"],
        preferred_net_index=result["preferred_net_index_from_05"],
        component_class_name=result.get("component_class_name"),
    )
    result["match_confidence"] = confidence
    result["match_warnings"] = warnings
    result["is_suspicious_match"] = confidence == "low"
    return result


def match_terminal_to_net(term: dict, label_map: np.ndarray, net_index_map: dict, source_label_to_net_index: dict, net_building_terminal_debug: dict):
    preferred_net_index = get_preferred_net_index(term, source_label_to_net_index, net_building_terminal_debug)

    result = {
        "terminal_id": term["terminal_id"],
        "instance_id": term["instance_id"],
        "component_class_name": term.get("component_class_name"),
        "relative_position": term.get("relative_position"),
        "x": term["x"],
        "y": term["y"],
        "preferred_net_index_from_05": preferred_net_index,
        "preferred_net_id_from_05": net_index_map.get(preferred_net_index, {}).get("net_id") if preferred_net_index is not None else None,
        "candidate_net_ids": [],
        "candidate_net_indices": [],
        "matched_net_id": None,
        "matched_net_index": None,
        "match_status": "unmatched",
        "match_distance_px": None,
        "snap_point": None,
        "search_stage": None,
        "search_window": None,
        "search_kind": None,
        "match_confidence": "none",
        "match_warnings": ["unmatched_terminal"],
        "is_suspicious_match": True,
    }

    for stage in build_search_plan(term):
        stage_result = run_search_stage(label_map, term, stage, preferred_net_index=preferred_net_index)
        candidate_labels = stage_result["candidate_labels"]

        if candidate_labels:
            result["candidate_net_indices"] = sorted(set(int(v) for v in candidate_labels))
            result["candidate_net_ids"] = [
                net_index_map[idx]["net_id"]
                for idx in result["candidate_net_indices"]
                if idx in net_index_map
            ]
            result["search_stage"] = stage["name"]
            result["search_window"] = stage_result["search_window"]
            result["search_kind"] = stage["kind"]

            chosen_idx = stage_result["chosen_label"]
            if chosen_idx is None:
                continue

            result["matched_net_index"] = int(chosen_idx)
            result["matched_net_id"] = net_index_map[int(chosen_idx)]["net_id"]
            result["match_distance_px"] = None if stage_result["distance"] is None else round(float(stage_result["distance"]), 3)
            result["snap_point"] = stage_result["snap_point"]

            decision_mode = stage_result["decision_mode"]
            if decision_mode == "preferred_label":
                result["match_status"] = "matched_preferred"
            elif decision_mode == "single_candidate":
                result["match_status"] = "matched_single"
            else:
                result["match_status"] = "matched_nearest"

            return finalize_match_result(result)

    return finalize_match_result(result)


# ---------------------------------------------------------
# Update strutture output
# ---------------------------------------------------------

def update_components_with_terminal_matches(components, terminal_match_map):
    updated_components = []

    for comp in components:
        comp_copy = dict(comp)
        updated_terminals = []

        for term in comp.get("terminals", []):
            term_copy = dict(term)
            match_info = terminal_match_map.get(term["terminal_id"], {})

            term_copy["candidate_net_ids"] = match_info.get("candidate_net_ids", [])
            term_copy["candidate_net_indices"] = match_info.get("candidate_net_indices", [])
            term_copy["preferred_net_index_from_05"] = match_info.get("preferred_net_index_from_05")
            term_copy["preferred_net_id_from_05"] = match_info.get("preferred_net_id_from_05")
            term_copy["matched_net_id"] = match_info.get("matched_net_id")
            term_copy["matched_net_index"] = match_info.get("matched_net_index")
            term_copy["match_status"] = match_info.get("match_status", "unmatched")
            term_copy["match_distance_px"] = match_info.get("match_distance_px")
            term_copy["snap_point"] = match_info.get("snap_point")
            term_copy["search_stage"] = match_info.get("search_stage")
            term_copy["search_window"] = match_info.get("search_window")
            term_copy["search_kind"] = match_info.get("search_kind")
            term_copy["match_confidence"] = match_info.get("match_confidence", "none")
            term_copy["match_warnings"] = match_info.get("match_warnings", [])
            term_copy["is_suspicious_match"] = match_info.get("is_suspicious_match", False)

            updated_terminals.append(term_copy)

        comp_copy["terminals"] = updated_terminals
        updated_components.append(comp_copy)

    return updated_components


def build_connections(terminals_with_matches):
    connections = []
    for term in terminals_with_matches:
        if term.get("matched_net_id") is None:
            continue

        connections.append({
            "terminal_id": term["terminal_id"],
            "instance_id": term["instance_id"],
            "component_class_name": term.get("component_class_name"),
            "net_id": term["matched_net_id"],
            "net_index": term["matched_net_index"],
            "match_status": term["match_status"],
            "match_distance_px": term["match_distance_px"],
            "snap_point": term.get("snap_point"),
            "match_confidence": term.get("match_confidence"),
            "match_warnings": term.get("match_warnings", []),
            "is_suspicious_match": term.get("is_suspicious_match", False),
        })
    return connections


# ---------------------------------------------------------
# Debug images
# ---------------------------------------------------------

def get_debug_color(term: dict):
    if term.get("matched_net_id") is None:
        return (0, 0, 255)

    confidence = term.get("match_confidence")
    if confidence == "high":
        return (0, 255, 0)
    if confidence == "medium":
        return (0, 255, 255)
    return (0, 140, 255)


def draw_debug_overlay(image_bgr, terminals_with_matches):
    out = image_bgr.copy()

    for term in terminals_with_matches:
        x = int(round(term["x"]))
        y = int(round(term["y"]))
        matched_net_id = term.get("matched_net_id")
        confidence = term.get("match_confidence", "none")
        snap_point = term.get("snap_point")

        color = get_debug_color(term)

        if matched_net_id is None:
            label = f"{term['terminal_id']}: none"
        else:
            label = f"{term['terminal_id']}->{matched_net_id} [{confidence}]"

        cv2.circle(out, (x, y), 5, color, -1)

        if snap_point is not None:
            sx, sy = int(snap_point[0]), int(snap_point[1])
            cv2.circle(out, (sx, sy), 4, (255, 255, 255), -1)
            cv2.line(out, (x, y), (sx, sy), color, 1, cv2.LINE_AA)

        cv2.putText(
            out,
            label,
            (x + 8, max(y - 8, 0)),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.42,
            color,
            1,
            cv2.LINE_AA,
        )

    return out


# ---------------------------------------------------------
# Main
# ---------------------------------------------------------

def main() -> None:
    if not INPUT_DIR.exists():
        raise FileNotFoundError(f"Cartella input non trovata: {INPUT_DIR}")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    DEBUG_DIR.mkdir(parents=True, exist_ok=True)

    json_files = sorted(INPUT_DIR.glob("*.json"))
    if not json_files:
        raise FileNotFoundError(f"Nessun file JSON trovato in: {INPUT_DIR}")

    print(f"Input directory : {INPUT_DIR}")
    print(f"Output directory: {OUTPUT_DIR}")
    print(f"File trovati    : {len(json_files)}\n")

    for i, json_path in enumerate(json_files, start=1):
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        image_path = Path(data["image_path"])
        image_bgr = cv2.imread(str(image_path))
        if image_bgr is None:
            print(f"Attenzione: immagine non leggibile -> {image_path}")
            continue

        nets = data.get("nets", [])
        net_building = data.get("net_building", {})
        label_map_path = Path(net_building["label_map_path"])
        label_map = load_label_map(label_map_path)

        net_index_map = build_net_index_map(nets)
        source_label_to_net_index = build_source_label_to_net_index_map(nets)
        net_building_terminal_debug = net_building.get("terminal_to_candidate_labels", {})
        terminals = data.get("terminals", [])

        terminals_with_matches = []
        terminal_match_map = {}

        for term in terminals:
            match_info = match_terminal_to_net(
                term,
                label_map,
                net_index_map,
                source_label_to_net_index,
                net_building_terminal_debug,
            )

            term_copy = dict(term)
            term_copy.update({
                "candidate_net_ids": match_info["candidate_net_ids"],
                "candidate_net_indices": match_info["candidate_net_indices"],
                "preferred_net_index_from_05": match_info["preferred_net_index_from_05"],
                "preferred_net_id_from_05": match_info["preferred_net_id_from_05"],
                "matched_net_id": match_info["matched_net_id"],
                "matched_net_index": match_info["matched_net_index"],
                "match_status": match_info["match_status"],
                "match_distance_px": match_info["match_distance_px"],
                "snap_point": match_info["snap_point"],
                "search_stage": match_info["search_stage"],
                "search_window": match_info["search_window"],
                "search_kind": match_info["search_kind"],
                "match_confidence": match_info["match_confidence"],
                "match_warnings": match_info["match_warnings"],
                "is_suspicious_match": match_info["is_suspicious_match"],
            })

            terminals_with_matches.append(term_copy)
            terminal_match_map[term["terminal_id"]] = match_info

        updated_components = update_components_with_terminal_matches(
            data.get("components", []),
            terminal_match_map,
        )

        connections = build_connections(terminals_with_matches)
        n_matched = sum(1 for t in terminals_with_matches if t.get("matched_net_id") is not None)
        n_unmatched = len(terminals_with_matches) - n_matched
        confidence_counts = {
            "high": sum(1 for t in terminals_with_matches if t.get("match_confidence") == "high"),
            "medium": sum(1 for t in terminals_with_matches if t.get("match_confidence") == "medium"),
            "low": sum(1 for t in terminals_with_matches if t.get("match_confidence") == "low"),
            "none": sum(1 for t in terminals_with_matches if t.get("match_confidence") == "none"),
        }
        suspicious_terminal_ids = [
            t["terminal_id"]
            for t in terminals_with_matches
            if t.get("is_suspicious_match", False)
        ]

        output_data = dict(data)
        output_data["components"] = updated_components
        output_data["terminals"] = terminals_with_matches
        output_data["connections"] = connections
        output_data["n_connections"] = len(connections)
        output_data["terminal_net_matching"] = {
            "notes": "Versione topology_v1 con confidence del match. Il matching usa prima la net preferita suggerita dal 05 se esiste, poi ricerca direzionale coerente col lato del terminale e infine fallback circolari più ampi. Ogni terminale viene etichettato come high/medium/low confidence per evidenziare i match deboli.",
            "base_directional_len": BASE_DIRECTIONAL_LEN,
            "base_directional_halfspan": BASE_DIRECTIONAL_HALFSPAN,
            "base_circle_radius": BASE_CIRCLE_RADIUS,
            "base_fallback_radius": BASE_FALLBACK_RADIUS,
            "class_search_overrides": CLASS_SEARCH_OVERRIDES,
            "confidence_rules": {
                "high": "matched_preferred con distanza <= 6 px",
                "medium": "altri match con distanza <= 12 px",
                "low": "distanza > 12 px oppure match senza preferred net / con fallback pesante",
            },
            "n_terminals": len(terminals_with_matches),
            "n_matched_terminals": n_matched,
            "n_unmatched_terminals": n_unmatched,
            "n_high_confidence": confidence_counts["high"],
            "n_medium_confidence": confidence_counts["medium"],
            "n_low_confidence": confidence_counts["low"],
            "n_none_confidence": confidence_counts["none"],
            "n_suspicious_matches": len(suspicious_terminal_ids),
            "suspicious_terminal_ids": suspicious_terminal_ids,
        }

        if SAVE_DEBUG_IMAGES:
            debug_img = draw_debug_overlay(image_bgr, terminals_with_matches)
            debug_path = DEBUG_DIR / f"{json_path.stem}_terminal_net_matches.jpg"
            cv2.imwrite(str(debug_path), debug_img)
            output_data["terminal_net_matching"]["debug_image_path"] = str(debug_path)

        out_json_path = OUTPUT_DIR / json_path.name
        with open(out_json_path, "w", encoding="utf-8") as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)

        print(
            f"[{i}/{len(json_files)}] {json_path.name} -> "
            f"matched={n_matched}, unmatched={n_unmatched}, "
            f"high={confidence_counts['high']}, medium={confidence_counts['medium']}, low={confidence_counts['low']}"
        )

    print("\nCompletato.")
    print(f"Risultati salvati in: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
