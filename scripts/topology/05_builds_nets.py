# Prende lo skeleton del 04
# trova le connected components
# considera ogni connected component come una papabile net
# verifica quanti terminali cadono vicino a quel componente
# tiene solo le component che hanno senso come net
# assegna ID del tipo
#   N1
#   N2
#   N3

from pathlib import Path
import json
import cv2
import numpy as np

# =========================================================
# CONFIGURAZIONE
# =========================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

INPUT_DIR = PROJECT_ROOT / "outputs" / "topology" / "04_extract_wires"
OUTPUT_DIR = PROJECT_ROOT / "outputs" / "topology" / "05_build_nets"

LABEL_MAP_DIR = OUTPUT_DIR / "label_maps"
NET_MAP_DIR = OUTPUT_DIR / "net_map"
OVERLAY_DIR = OUTPUT_DIR / "overlay"

# Parametri iniziali
TERMINAL_NET_RADIUS = 8
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


def terminal_to_candidate_labels(labels: np.ndarray, terminals, radius=8):
    """
    Per ogni terminale guarda una piccola finestra attorno al punto terminale
    e raccoglie i label di connected components presenti in quella zona.
    """
    h, w = labels.shape
    label_to_terminal_ids = {}
    terminal_to_labels = {}

    for term in terminals:
        x = int(round(term["x"]))
        y = int(round(term["y"]))

        x1 = max(0, x - radius)
        y1 = max(0, y - radius)
        x2 = min(w, x + radius + 1)
        y2 = min(h, y + radius + 1)

        window = labels[y1:y2, x1:x2]
        unique_labels = np.unique(window)
        unique_labels = [int(v) for v in unique_labels if int(v) > 0]

        terminal_to_labels[term["terminal_id"]] = unique_labels

        for lbl in unique_labels:
            label_to_terminal_ids.setdefault(lbl, set()).add(term["terminal_id"])

    return label_to_terminal_ids, terminal_to_labels


def build_candidate_nets(labels, stats, label_to_terminal_ids):
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

        if cand["pixel_count"] < MIN_NET_PIXELS:
            keep = False

        if cand["n_connected_terminals"] < MIN_CONNECTED_TERMINALS:
            keep = False

        if keep:
            kept.append(cand)
        else:
            rejected.append(cand)

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
            cv2.LINE_AA
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
            cv2.LINE_AA
        )

    blended = cv2.addWeighted(image_bgr, 0.65, overlay, 0.35, 0)
    return blended


def main() -> None:
    if not INPUT_DIR.exists():
        raise FileNotFoundError(f"Cartella input non trovata: {INPUT_DIR}")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    LABEL_MAP_DIR.mkdir(parents=True, exist_ok=True)
    NET_MAP_DIR.mkdir(parents=True, exist_ok=True)
    OVERLAY_DIR.mkdir(parents=True, exist_ok=True)

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
            labels, terminals, radius=TERMINAL_NET_RADIUS
        )

        candidates = build_candidate_nets(labels, stats, label_to_terminal_ids)
        kept_candidates, rejected_candidates = filter_candidate_nets(candidates)

        relabeled_map, nets = relabel_kept_nets(
            labels,
            kept_candidates,
            sort_order=NET_SORT_ORDER
        )

        stem = json_path.stem

        label_map_path = LABEL_MAP_DIR / f"{stem}_net_labels.npy"
        np.save(label_map_path, relabeled_map)

        output_data = dict(data)
        output_data["nets"] = nets
        output_data["n_nets"] = len(nets)
        output_data["net_building"] = {
            "terminal_net_radius": TERMINAL_NET_RADIUS,
            "min_net_pixels": MIN_NET_PIXELS,
            "min_connected_terminals": MIN_CONNECTED_TERMINALS,
            "net_sort_order": NET_SORT_ORDER,
            "n_candidate_components": len(candidates),
            "n_kept_nets": len(kept_candidates),
            "n_rejected_components": len(rejected_candidates),
            "label_map_path": str(label_map_path),
            "terminal_to_candidate_labels": terminal_to_labels,
        }

        if SAVE_DEBUG_IMAGES:
            net_map = draw_net_map(relabeled_map, nets)
            overlay = draw_overlay(image_bgr, relabeled_map, nets)

            net_map_path = NET_MAP_DIR / f"{stem}_net_map.png"
            overlay_path = OVERLAY_DIR / f"{stem}_net_overlay.jpg"

            cv2.imwrite(str(net_map_path), net_map)
            cv2.imwrite(str(overlay_path), overlay)

            output_data["net_building"]["net_map_path"] = str(net_map_path)
            output_data["net_building"]["overlay_path"] = str(overlay_path)

        out_json_path = OUTPUT_DIR / json_path.name
        with open(out_json_path, "w", encoding="utf-8") as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)

        print(
            f"[{i}/{len(json_files)}] {json_path.name} -> "
            f"candidate={len(candidates)}, nets={len(nets)}, rejected={len(rejected_candidates)}"
        )

    print("\nCompletato.")
    print(f"Risultati salvati in: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()