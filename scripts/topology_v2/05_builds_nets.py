from pathlib import Path
import json
import cv2
import numpy as np

# =========================================================
# CONFIGURAZIONE
# =========================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

INPUT_DIR = PROJECT_ROOT / "outputs" / "topology_v2" / "04_extract_wires"
OUTPUT_DIR = PROJECT_ROOT / "outputs" / "topology_v2" / "05_build_nets"

LABEL_MAP_DIR = OUTPUT_DIR / "label_maps"
NET_MAP_DIR = OUTPUT_DIR / "net_map"
OVERLAY_DIR = OUTPUT_DIR / "overlay"
TERMINAL_DEBUG_DIR = OUTPUT_DIR / "terminal_debug"

# Terminale -> componente connessa sullo skeleton
TERMINAL_SEARCH_RADIUS = 12
TERMINAL_DIRECTIONAL_HALFSPAN = 5

# Filtro candidate nets
MIN_NET_PIXELS = 8
MIN_CONNECTED_TERMINALS = 1

# Ordinamento net:
# "xy" = da sinistra a destra, poi dall'alto verso il basso
# "yx" = dall'alto verso il basso, poi da sinistra a destra
NET_SORT_ORDER = "xy"

SAVE_DEBUG_IMAGES = True

# Palette semplice per visualizzazione
NET_COLORS = [
    (255, 0, 0),
    (0, 255, 0),
    (0, 0, 255),
    (255, 255, 0),
    (255, 0, 255),
    (0, 255, 255),
    (255, 128, 0),
    (128, 0, 255),
    (0, 128, 255),
    (128, 255, 0),
]


def load_binary_image(path: Path):
    img = cv2.imread(str(path), cv2.IMREAD_GRAYSCALE)
    if img is None:
        raise FileNotFoundError(f"Immagine non trovata o non leggibile: {path}")

    binary = np.where(img > 0, 255, 0).astype(np.uint8)
    return binary


def get_sort_key(item, sort_order="xy"):
    x1, y1, x2, y2 = item["bbox"]
    xc = (x1 + x2) / 2.0
    yc = (y1 + y2) / 2.0

    if sort_order == "yx":
        return (yc, xc)
    return (xc, yc)


def find_connected_components(skeleton_binary: np.ndarray):
    num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(
        skeleton_binary, connectivity=8
    )
    return num_labels, labels, stats, centroids


def clamp_window(x1, y1, x2, y2, w, h):
    return (
        max(0, min(w, x1)),
        max(0, min(h, y1)),
        max(0, min(w, x2)),
        max(0, min(h, y2)),
    )


def get_directional_window(term: dict, labels_shape, radius=12, halfspan=5):
    h, w = labels_shape[:2]
    x = int(round(term["x"]))
    y = int(round(term["y"]))
    rel = term.get("relative_position")

    if rel == "left":
        x1, y1, x2, y2 = clamp_window(x - radius, y - halfspan, x + radius + 1, y + halfspan + 1, w, h)
    elif rel == "right":
        x1, y1, x2, y2 = clamp_window(x - radius, y - halfspan, x + radius + 1, y + halfspan + 1, w, h)
    elif rel == "top":
        x1, y1, x2, y2 = clamp_window(x - halfspan, y - radius, x + halfspan + 1, y + radius + 1, w, h)
    elif rel == "bottom":
        x1, y1, x2, y2 = clamp_window(x - halfspan, y - radius, x + halfspan + 1, y + radius + 1, w, h)
    else:
        x1, y1, x2, y2 = clamp_window(x - radius, y - radius, x + radius + 1, y + radius + 1, w, h)

    return x1, y1, x2, y2


def get_square_window(term: dict, labels_shape, radius=12):
    h, w = labels_shape[:2]
    x = int(round(term["x"]))
    y = int(round(term["y"]))
    return clamp_window(x - radius, y - radius, x + radius + 1, y + radius + 1, w, h)


def collect_labels_in_window(labels: np.ndarray, window):
    x1, y1, x2, y2 = window
    roi = labels[y1:y2, x1:x2]
    unique_labels = np.unique(roi)
    return [int(v) for v in unique_labels if int(v) > 0]


def find_nearest_labeled_pixel(labels: np.ndarray, term: dict, window):
    x1, y1, x2, y2 = window
    roi = labels[y1:y2, x1:x2]
    ys, xs = np.where(roi > 0)
    if len(xs) == 0:
        return None

    abs_xs = xs + x1
    abs_ys = ys + y1

    tx = float(term["x"])
    ty = float(term["y"])

    d2 = (abs_xs - tx) ** 2 + (abs_ys - ty) ** 2
    best_idx = int(np.argmin(d2))

    px = int(abs_xs[best_idx])
    py = int(abs_ys[best_idx])
    lbl = int(labels[py, px])
    dist = float(np.sqrt(d2[best_idx]))

    return {
        "label": lbl,
        "snap_point": [px, py],
        "snap_distance": round(dist, 3),
    }


def terminal_to_candidate_labels(labels: np.ndarray, terminals, radius=12, directional_halfspan=5):
    """
    Per ogni terminale prova prima un intorno direzionale coerente col lato del terminale,
    poi fa fallback a una finestra quadrata. Salva sia i label candidati sia il label
    principale ottenuto con snap al pixel di skeleton più vicino.
    """
    primary_label_to_terminal_ids = {}
    terminal_debug = {}

    for term in terminals:
        term_id = term["terminal_id"]

        dir_window = get_directional_window(
            term,
            labels.shape,
            radius=radius,
            halfspan=directional_halfspan,
        )
        dir_labels = collect_labels_in_window(labels, dir_window)
        nearest = find_nearest_labeled_pixel(labels, term, dir_window)
        match_mode = "directional"

        if nearest is None:
            sq_window = get_square_window(term, labels.shape, radius=radius)
            sq_labels = collect_labels_in_window(labels, sq_window)
            nearest = find_nearest_labeled_pixel(labels, term, sq_window)
            match_mode = "square_fallback"
            candidate_labels = sq_labels
            used_window = sq_window
        else:
            candidate_labels = dir_labels
            used_window = dir_window

        primary_label = None
        snap_point = None
        snap_distance = None

        if nearest is not None:
            primary_label = int(nearest["label"])
            snap_point = nearest["snap_point"]
            snap_distance = nearest["snap_distance"]
            primary_label_to_terminal_ids.setdefault(primary_label, set()).add(term_id)

        terminal_debug[term_id] = {
            "candidate_labels": candidate_labels,
            "primary_label": primary_label,
            "match_mode": match_mode,
            "search_window": [int(v) for v in used_window],
            "snap_point": snap_point,
            "snap_distance": snap_distance,
            "relative_position": term.get("relative_position"),
        }

    return primary_label_to_terminal_ids, terminal_debug


def build_candidate_nets(stats, label_to_terminal_ids):
    candidates = []
    num_labels = stats.shape[0]

    for lbl in range(1, num_labels):  # 0 = background
        x = int(stats[lbl, cv2.CC_STAT_LEFT])
        y = int(stats[lbl, cv2.CC_STAT_TOP])
        w = int(stats[lbl, cv2.CC_STAT_WIDTH])
        h = int(stats[lbl, cv2.CC_STAT_HEIGHT])
        area = int(stats[lbl, cv2.CC_STAT_AREA])

        connected_terminal_ids = sorted(list(label_to_terminal_ids.get(lbl, set())))

        candidate = {
            "source_label": int(lbl),
            "pixel_count": area,
            "bbox": [x, y, x + w - 1, y + h - 1],
            "connected_terminal_ids": connected_terminal_ids,
            "n_connected_terminals": len(connected_terminal_ids),
        }
        candidates.append(candidate)

    return candidates


def filter_candidate_nets(candidates):
    kept = []
    rejected = []

    for cand in candidates:
        keep = True
        reject_reasons = []

        if cand["pixel_count"] < MIN_NET_PIXELS:
            keep = False
            reject_reasons.append("too_few_pixels")

        if cand["n_connected_terminals"] < MIN_CONNECTED_TERMINALS:
            keep = False
            reject_reasons.append("no_connected_terminals")

        cand_copy = dict(cand)
        cand_copy["reject_reasons"] = reject_reasons

        if keep:
            kept.append(cand_copy)
        else:
            rejected.append(cand_copy)

    return kept, rejected


def relabel_kept_nets(original_labels: np.ndarray, kept_candidates, sort_order="xy"):
    kept_sorted = sorted(kept_candidates, key=lambda x: get_sort_key(x, sort_order=sort_order))

    relabeled = np.zeros_like(original_labels, dtype=np.int32)
    nets = []

    for idx, cand in enumerate(kept_sorted, start=1):
        old_label = cand["source_label"]
        relabeled[original_labels == old_label] = idx

        net = {
            "net_id": f"N{idx}",
            "net_index": idx,
            "source_label": old_label,
            "pixel_count": cand["pixel_count"],
            "bbox": cand["bbox"],
            "connected_terminal_ids": cand["connected_terminal_ids"],
            "n_connected_terminals": cand["n_connected_terminals"],
        }
        nets.append(net)

    return relabeled, nets


def draw_net_map(relabeled_map: np.ndarray, nets):
    h, w = relabeled_map.shape
    canvas = np.zeros((h, w, 3), dtype=np.uint8)

    for net in nets:
        idx = net["net_index"]
        color = NET_COLORS[(idx - 1) % len(NET_COLORS)]
        canvas[relabeled_map == idx] = color

        x1, y1, x2, y2 = net["bbox"]
        cx = int((x1 + x2) / 2)
        cy = int((y1 + y2) / 2)

        cv2.putText(
            canvas,
            net["net_id"],
            (cx, cy),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.45,
            color,
            1,
            cv2.LINE_AA,
        )

    return canvas


def draw_overlay(image_bgr, relabeled_map: np.ndarray, nets):
    overlay = image_bgr.copy()

    for net in nets:
        idx = net["net_index"]
        color = NET_COLORS[(idx - 1) % len(NET_COLORS)]

        mask = relabeled_map == idx
        overlay[mask] = color

        x1, y1, x2, y2 = net["bbox"]
        cx = int((x1 + x2) / 2)
        cy = int((y1 + y2) / 2)

        cv2.putText(
            overlay,
            net["net_id"],
            (cx, cy),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.45,
            color,
            1,
            cv2.LINE_AA,
        )

    blended = cv2.addWeighted(image_bgr, 0.65, overlay, 0.35, 0)
    return blended


def draw_terminal_debug(image_bgr, terminals, terminal_debug, relabeled_map, nets):
    out = image_bgr.copy()
    index_to_net_id = {net["net_index"]: net["net_id"] for net in nets}

    for term in terminals:
        term_id = term["terminal_id"]
        info = terminal_debug.get(term_id, {})

        tx = int(round(term["x"]))
        ty = int(round(term["y"]))
        cv2.circle(out, (tx, ty), 4, (0, 255, 0), -1)

        snap_point = info.get("snap_point")
        primary_label = info.get("primary_label")

        if snap_point is None or primary_label is None:
            cv2.putText(
                out,
                f"{term_id}: none",
                (tx + 6, max(0, ty - 6)),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.35,
                (0, 0, 255),
                1,
                cv2.LINE_AA,
            )
            continue

        sx, sy = map(int, snap_point)
        cv2.circle(out, (sx, sy), 3, (255, 255, 0), -1)
        cv2.line(out, (tx, ty), (sx, sy), (0, 255, 255), 1)

        net_idx = int(relabeled_map[sy, sx]) if 0 <= sy < relabeled_map.shape[0] and 0 <= sx < relabeled_map.shape[1] else 0
        net_id = index_to_net_id.get(net_idx, f"src{primary_label}")

        cv2.putText(
            out,
            f"{term_id}->{net_id}",
            (tx + 6, max(0, ty - 6)),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.35,
            (0, 255, 255),
            1,
            cv2.LINE_AA,
        )

    return out


def main() -> None:
    if not INPUT_DIR.exists():
        raise FileNotFoundError(f"Cartella input non trovata: {INPUT_DIR}")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    LABEL_MAP_DIR.mkdir(parents=True, exist_ok=True)
    NET_MAP_DIR.mkdir(parents=True, exist_ok=True)
    OVERLAY_DIR.mkdir(parents=True, exist_ok=True)
    TERMINAL_DEBUG_DIR.mkdir(parents=True, exist_ok=True)

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

        wire_extraction = data.get("wire_extraction", {})
        skeleton_path = Path(wire_extraction["skeleton_path"])

        skeleton_binary = load_binary_image(skeleton_path)
        terminals = data.get("terminals", [])

        num_labels, labels, stats, centroids = find_connected_components(skeleton_binary)

        label_to_terminal_ids, terminal_to_labels = terminal_to_candidate_labels(
            labels,
            terminals,
            radius=TERMINAL_SEARCH_RADIUS,
            directional_halfspan=TERMINAL_DIRECTIONAL_HALFSPAN,
        )

        candidates = build_candidate_nets(stats, label_to_terminal_ids)
        kept_candidates, rejected_candidates = filter_candidate_nets(candidates)

        relabeled_map, nets = relabel_kept_nets(
            labels,
            kept_candidates,
            sort_order=NET_SORT_ORDER,
        )

        stem = json_path.stem

        label_map_path = LABEL_MAP_DIR / f"{stem}_net_labels.npy"
        np.save(label_map_path, relabeled_map)

        output_data = dict(data)
        output_data["nets"] = nets
        output_data["n_nets"] = len(nets)
        output_data["net_building"] = {
            "notes": "Versione topology_v1. Le candidate nets vengono ricavate dalle connected components dello skeleton del 04. L'associazione terminale->net usa prima una ricerca direzionale coerente col lato del terminale, poi fallback a una finestra quadrata locale.",
            "terminal_search_radius": TERMINAL_SEARCH_RADIUS,
            "terminal_directional_halfspan": TERMINAL_DIRECTIONAL_HALFSPAN,
            "min_net_pixels": MIN_NET_PIXELS,
            "min_connected_terminals": MIN_CONNECTED_TERMINALS,
            "net_sort_order": NET_SORT_ORDER,
            "n_connected_components_total": max(0, int(num_labels) - 1),
            "n_candidate_components": len(candidates),
            "n_kept_nets": len(kept_candidates),
            "n_rejected_components": len(rejected_candidates),
            "n_terminals": len(terminals),
            "n_terminals_with_primary_label": sum(1 for v in terminal_to_labels.values() if v.get("primary_label") is not None),
            "n_terminals_unmatched": sum(1 for v in terminal_to_labels.values() if v.get("primary_label") is None),
            "label_map_path": str(label_map_path),
            "terminal_to_candidate_labels": terminal_to_labels,
            "rejected_candidates": rejected_candidates,
        }

        if SAVE_DEBUG_IMAGES:
            net_map = draw_net_map(relabeled_map, nets)
            overlay = draw_overlay(image_bgr, relabeled_map, nets)
            terminal_debug_img = draw_terminal_debug(image_bgr, terminals, terminal_to_labels, relabeled_map, nets)

            net_map_path = NET_MAP_DIR / f"{stem}_net_map.png"
            overlay_path = OVERLAY_DIR / f"{stem}_net_overlay.jpg"
            terminal_debug_path = TERMINAL_DEBUG_DIR / f"{stem}_terminal_debug.jpg"

            cv2.imwrite(str(net_map_path), net_map)
            cv2.imwrite(str(overlay_path), overlay)
            cv2.imwrite(str(terminal_debug_path), terminal_debug_img)

            output_data["net_building"]["net_map_path"] = str(net_map_path)
            output_data["net_building"]["overlay_path"] = str(overlay_path)
            output_data["net_building"]["terminal_debug_path"] = str(terminal_debug_path)

        out_json_path = OUTPUT_DIR / json_path.name
        with open(out_json_path, "w", encoding="utf-8") as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)

        print(
            f"[{i}/{len(json_files)}] {json_path.name} -> "
            f"cc_total={max(0, int(num_labels) - 1)}, candidate={len(candidates)}, "
            f"nets={len(nets)}, rejected={len(rejected_candidates)}"
        )

    print("\nCompletato.")
    print(f"Risultati salvati in: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
