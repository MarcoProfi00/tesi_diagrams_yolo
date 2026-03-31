# Legge la labels map del json 05, per ogni terminale guarda intorno al suo punto (x,y), controlla se in quella zona c'è una net
#   se c'è una sola net -> la assegna
#   se ce ne sono più di una -> sceglie quella più vicina
#   se non c'è nessuna net -> unmatched

from pathlib import Path
import json
import cv2
import numpy as np

# =========================================================
# CONFIGURAZIONE
# =========================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

INPUT_DIR = PROJECT_ROOT / "outputs" / "topology" / "05_build_nets"
OUTPUT_DIR = PROJECT_ROOT / "outputs" / "topology" / "06_match_terminals_to_nets"
DEBUG_DIR = OUTPUT_DIR / "debug_images"

MATCH_RADIUS = 8
FALLBACK_RADIUS = 16
SAVE_DEBUG_IMAGES = True


def load_label_map(path: Path) -> np.ndarray:
    if not path.exists():
        raise FileNotFoundError(f"Label map non trovata: {path}")
    return np.load(path)


def build_net_index_map(nets):
    """
    Restituisce un dict:
    {
        1: {"net_id": "N1", ...},
        2: {"net_id": "N2", ...},
        ...
    }
    """
    out = {}
    for net in nets:
        out[int(net["net_index"])] = net
    return out


def get_candidate_labels_in_radius(label_map: np.ndarray, x: int, y: int, radius: int):
    h, w = label_map.shape

    x1 = max(0, x - radius)
    y1 = max(0, y - radius)
    x2 = min(w, x + radius + 1)
    y2 = min(h, y + radius + 1)

    window = label_map[y1:y2, x1:x2]

    # maschera circolare
    yy, xx = np.ogrid[y1:y2, x1:x2]
    circle_mask = (xx - x) ** 2 + (yy - y) ** 2 <= radius ** 2

    values = window[circle_mask]
    unique_labels = np.unique(values)
    unique_labels = [int(v) for v in unique_labels if int(v) > 0]

    return unique_labels, (x1, y1, x2, y2), circle_mask


def nearest_label_by_pixel_distance(label_map: np.ndarray, x: int, y: int, candidate_labels, radius: int):
    """
    Tra più net candidate sceglie quella con il pixel più vicino al terminale.
    """
    h, w = label_map.shape

    x1 = max(0, x - radius)
    y1 = max(0, y - radius)
    x2 = min(w, x + radius + 1)
    y2 = min(h, y + radius + 1)

    window = label_map[y1:y2, x1:x2]

    best_label = None
    best_distance = None

    for lbl in candidate_labels:
        ys, xs = np.where(window == lbl)
        if len(xs) == 0:
            continue

        xs_global = xs + x1
        ys_global = ys + y1

        dists = np.sqrt((xs_global - x) ** 2 + (ys_global - y) ** 2)
        min_dist = float(np.min(dists))

        if best_distance is None or min_dist < best_distance:
            best_distance = min_dist
            best_label = int(lbl)

    return best_label, best_distance


def match_terminal_to_net(term: dict, label_map: np.ndarray, net_index_map: dict):
    x = int(round(term["x"]))
    y = int(round(term["y"]))

    # primo tentativo
    candidate_labels, _, _ = get_candidate_labels_in_radius(label_map, x, y, MATCH_RADIUS)

    used_radius = MATCH_RADIUS
    used_fallback = False

    # fallback
    if not candidate_labels and FALLBACK_RADIUS > MATCH_RADIUS:
        candidate_labels, _, _ = get_candidate_labels_in_radius(label_map, x, y, FALLBACK_RADIUS)
        used_radius = FALLBACK_RADIUS
        used_fallback = True

    result = {
        "terminal_id": term["terminal_id"],
        "instance_id": term["instance_id"],
        "x": term["x"],
        "y": term["y"],
        "candidate_net_ids": [],
        "candidate_net_indices": [],
        "matched_net_id": None,
        "matched_net_index": None,
        "match_status": "unmatched",
        "match_distance_px": None,
        "used_radius": used_radius,
        "used_fallback": used_fallback,
    }

    if not candidate_labels:
        return result

    candidate_net_indices = sorted(candidate_labels)
    candidate_net_ids = [
        net_index_map[idx]["net_id"]
        for idx in candidate_net_indices
        if idx in net_index_map
    ]

    result["candidate_net_indices"] = candidate_net_indices
    result["candidate_net_ids"] = candidate_net_ids

    if len(candidate_net_indices) == 1:
        chosen_idx = candidate_net_indices[0]
        chosen_net = net_index_map[chosen_idx]

        result["matched_net_index"] = chosen_idx
        result["matched_net_id"] = chosen_net["net_id"]
        result["match_status"] = "matched_single"
        result["match_distance_px"] = 0.0
        return result

    chosen_idx, dist = nearest_label_by_pixel_distance(
        label_map=label_map,
        x=x,
        y=y,
        candidate_labels=candidate_net_indices,
        radius=used_radius
    )

    if chosen_idx is None:
        return result

    chosen_net = net_index_map[chosen_idx]
    result["matched_net_index"] = chosen_idx
    result["matched_net_id"] = chosen_net["net_id"]
    result["match_status"] = "matched_nearest"
    result["match_distance_px"] = round(float(dist), 3) if dist is not None else None

    return result


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
            term_copy["matched_net_id"] = match_info.get("matched_net_id")
            term_copy["matched_net_index"] = match_info.get("matched_net_index")
            term_copy["match_status"] = match_info.get("match_status", "unmatched")
            term_copy["match_distance_px"] = match_info.get("match_distance_px")
            term_copy["used_radius"] = match_info.get("used_radius")
            term_copy["used_fallback"] = match_info.get("used_fallback", False)

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
            "net_id": term["matched_net_id"],
            "net_index": term["matched_net_index"],
            "match_status": term["match_status"],
            "match_distance_px": term["match_distance_px"],
        })

    return connections


def draw_debug_overlay(image_bgr, terminals_with_matches):
    out = image_bgr.copy()

    for term in terminals_with_matches:
        x = int(round(term["x"]))
        y = int(round(term["y"]))

        matched_net_id = term.get("matched_net_id")
        status = term.get("match_status", "unmatched")

        if matched_net_id is None:
            color = (0, 0, 255)  # rosso
            label = f"{term['terminal_id']} -> NONE"
        else:
            color = (0, 255, 0)  # verde
            label = f"{term['terminal_id']} -> {matched_net_id}"

        if status == "matched_nearest":
            color = (0, 255, 255)  # giallo

        cv2.circle(out, (x, y), 6, color, -1)
        cv2.putText(
            out,
            label,
            (x + 8, max(y - 8, 0)),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.42,
            color,
            1,
            cv2.LINE_AA
        )

    return out


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
        terminals = data.get("terminals", [])

        terminals_with_matches = []
        terminal_match_map = {}

        for term in terminals:
            match_info = match_terminal_to_net(term, label_map, net_index_map)

            term_copy = dict(term)
            term_copy.update({
                "candidate_net_ids": match_info["candidate_net_ids"],
                "candidate_net_indices": match_info["candidate_net_indices"],
                "matched_net_id": match_info["matched_net_id"],
                "matched_net_index": match_info["matched_net_index"],
                "match_status": match_info["match_status"],
                "match_distance_px": match_info["match_distance_px"],
                "used_radius": match_info["used_radius"],
                "used_fallback": match_info["used_fallback"],
            })

            terminals_with_matches.append(term_copy)
            terminal_match_map[term["terminal_id"]] = match_info

        updated_components = update_components_with_terminal_matches(
            data.get("components", []),
            terminal_match_map
        )

        connections = build_connections(terminals_with_matches)

        n_matched = sum(1 for t in terminals_with_matches if t.get("matched_net_id") is not None)
        n_unmatched = len(terminals_with_matches) - n_matched

        output_data = dict(data)
        output_data["components"] = updated_components
        output_data["terminals"] = terminals_with_matches
        output_data["connections"] = connections
        output_data["n_connections"] = len(connections)
        output_data["terminal_net_matching"] = {
            "match_radius": MATCH_RADIUS,
            "fallback_radius": FALLBACK_RADIUS,
            "n_terminals": len(terminals_with_matches),
            "n_matched_terminals": n_matched,
            "n_unmatched_terminals": n_unmatched,
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
            f"matched={n_matched}, unmatched={n_unmatched}, connections={len(connections)}"
        )

    print("\nCompletato.")
    print(f"Risultati salvati in: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()