from pathlib import Path
import json
import cv2
import numpy as np
from skimage.morphology import skeletonize

# =========================================================
# CONFIGURAZIONE
# =========================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

INPUT_DIR = PROJECT_ROOT / "outputs" / "topology_v2" / "03_estimate_terminals"
OUTPUT_DIR = PROJECT_ROOT / "outputs" / "topology_v2" / "04_extract_wires"

MASK_DEBUG_DIR = OUTPUT_DIR / "mask_debug"
COMPONENT_MASK_DIR = OUTPUT_DIR / "component_mask"
TERMINAL_KEEP_DEBUG_DIR = OUTPUT_DIR / "terminal_keep_debug"
MASKED_DIR = OUTPUT_DIR / "masked_gray"
BINARY_DIR = OUTPUT_DIR / "binary"
CLOSED_DIR = OUTPUT_DIR / "closed"
FILTERED_DIR = OUTPUT_DIR / "filtered"
SKELETON_DIR = OUTPUT_DIR / "skeleton"

# Mascheramento componenti
MASK_SHRINK_FACTOR = 0.88

# Preservazione terminali: non solo un cerchio, ma una piccola "capsula"
# direzionata lungo il lato stimato del terminale.
TERMINAL_KEEP_RADIUS = 10
TERMINAL_KEEP_LINE_THICKNESS = 7
TERMINAL_KEEP_INWARD_LEN = 14
TERMINAL_KEEP_OUTWARD_LEN = 12

# Morfologia
CLOSING_KERNEL_SIZE = 3
CLOSING_ITERATIONS = 1

# Filtro opzionale per piccoli componenti connessi
ENABLE_SMALL_COMPONENT_FILTER = True
MIN_COMPONENT_AREA = 40


def clamp_point(x, y, w, h):
    x = max(0, min(w - 1, int(round(x))))
    y = max(0, min(h - 1, int(round(y))))
    return x, y



def shrink_bbox(bbox, shrink_factor=0.88):
    x1, y1, x2, y2 = bbox
    xc = (x1 + x2) / 2.0
    yc = (y1 + y2) / 2.0
    w = (x2 - x1) * shrink_factor
    h = (y2 - y1) * shrink_factor

    new_x1 = xc - w / 2.0
    new_y1 = yc - h / 2.0
    new_x2 = xc + w / 2.0
    new_y2 = yc + h / 2.0

    return [new_x1, new_y1, new_x2, new_y2]



def build_base_component_mask(image_shape, components):
    h, w = image_shape[:2]
    mask = np.zeros((h, w), dtype=np.uint8)

    for comp in components:
        if not comp.get("use_for_masking", False):
            continue

        bbox = shrink_bbox(comp["bbox"], shrink_factor=MASK_SHRINK_FACTOR)
        x1, y1, x2, y2 = map(int, bbox)

        x1 = max(0, min(w - 1, x1))
        y1 = max(0, min(h - 1, y1))
        x2 = max(0, min(w - 1, x2))
        y2 = max(0, min(h - 1, y2))

        cv2.rectangle(mask, (x1, y1), (x2, y2), 255, thickness=-1)

    return mask



def terminal_keep_segment(term):
    x = float(term["x"])
    y = float(term["y"])
    rel = term.get("relative_position")

    if rel == "left":
        p1 = (x - TERMINAL_KEEP_OUTWARD_LEN, y)
        p2 = (x + TERMINAL_KEEP_INWARD_LEN, y)
    elif rel == "right":
        p1 = (x - TERMINAL_KEEP_INWARD_LEN, y)
        p2 = (x + TERMINAL_KEEP_OUTWARD_LEN, y)
    elif rel == "top":
        p1 = (x, y - TERMINAL_KEEP_OUTWARD_LEN)
        p2 = (x, y + TERMINAL_KEEP_INWARD_LEN)
    elif rel == "bottom":
        p1 = (x, y - TERMINAL_KEEP_INWARD_LEN)
        p2 = (x, y + TERMINAL_KEEP_OUTWARD_LEN)
    else:
        # fallback prudente: se il lato non è disponibile, almeno preserva il cerchio
        p1 = (x, y)
        p2 = (x, y)

    return p1, p2



def carve_terminal_keep_zones(mask, terminals):
    h, w = mask.shape[:2]
    keep_debug = np.zeros_like(mask)

    for term in terminals:
        x = int(round(term["x"]))
        y = int(round(term["y"]))
        x, y = clamp_point(x, y, w, h)

        cv2.circle(mask, (x, y), TERMINAL_KEEP_RADIUS, 0, thickness=-1)
        cv2.circle(keep_debug, (x, y), TERMINAL_KEEP_RADIUS, 255, thickness=-1)

        p1f, p2f = terminal_keep_segment(term)
        p1 = clamp_point(p1f[0], p1f[1], w, h)
        p2 = clamp_point(p2f[0], p2f[1], w, h)

        cv2.line(mask, p1, p2, 0, thickness=TERMINAL_KEEP_LINE_THICKNESS)
        cv2.line(keep_debug, p1, p2, 255, thickness=TERMINAL_KEEP_LINE_THICKNESS)

    return mask, keep_debug



def build_component_mask(image_shape, components, terminals):
    mask = build_base_component_mask(image_shape, components)
    mask, keep_debug = carve_terminal_keep_zones(mask, terminals)
    return mask, keep_debug



def save_mask_debug(image_bgr, mask, out_path: Path):
    overlay = image_bgr.copy()
    red_layer = np.zeros_like(image_bgr)
    red_layer[:, :, 2] = 255

    alpha = 0.35
    mask_bool = mask > 0
    overlay[mask_bool] = cv2.addWeighted(
        image_bgr[mask_bool], 1 - alpha, red_layer[mask_bool], alpha, 0
    )

    cv2.imwrite(str(out_path), overlay)



def save_terminal_keep_debug(image_bgr, keep_debug, out_path: Path):
    overlay = image_bgr.copy()
    green_layer = np.zeros_like(image_bgr)
    green_layer[:, :, 1] = 255

    alpha = 0.35
    keep_bool = keep_debug > 0
    overlay[keep_bool] = cv2.addWeighted(
        image_bgr[keep_bool], 1 - alpha, green_layer[keep_bool], alpha, 0
    )

    cv2.imwrite(str(out_path), overlay)



def remove_small_connected_components(binary_img, min_area=40):
    num_labels, labels, stats, _ = cv2.connectedComponentsWithStats(binary_img, connectivity=8)

    filtered = np.zeros_like(binary_img)
    kept_components = 0
    removed_components = 0

    for label_idx in range(1, num_labels):
        area = stats[label_idx, cv2.CC_STAT_AREA]

        if area >= min_area:
            filtered[labels == label_idx] = 255
            kept_components += 1
        else:
            removed_components += 1

    return filtered, kept_components, removed_components



def extract_wires_from_image(image_bgr, components, terminals):
    gray = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2GRAY)

    component_mask, terminal_keep_debug = build_component_mask(
        image_bgr.shape, components, terminals
    )

    masked_gray = gray.copy()
    masked_gray[component_mask > 0] = 255

    _, binary = cv2.threshold(
        masked_gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU
    )

    kernel = cv2.getStructuringElement(
        cv2.MORPH_RECT, (CLOSING_KERNEL_SIZE, CLOSING_KERNEL_SIZE)
    )
    closed = cv2.morphologyEx(
        binary,
        cv2.MORPH_CLOSE,
        kernel,
        iterations=CLOSING_ITERATIONS,
    )

    if ENABLE_SMALL_COMPONENT_FILTER:
        filtered, kept_components, removed_components = remove_small_connected_components(
            closed,
            min_area=MIN_COMPONENT_AREA,
        )
    else:
        filtered = closed.copy()
        kept_components = None
        removed_components = None

    skeleton_bool = skeletonize(filtered > 0)
    skeleton = (skeleton_bool.astype(np.uint8)) * 255

    filter_info = {
        "enabled": ENABLE_SMALL_COMPONENT_FILTER,
        "min_component_area": MIN_COMPONENT_AREA,
        "kept_components": kept_components,
        "removed_components": removed_components,
    }

    keep_info = {
        "terminal_keep_radius": TERMINAL_KEEP_RADIUS,
        "terminal_keep_line_thickness": TERMINAL_KEEP_LINE_THICKNESS,
        "terminal_keep_inward_len": TERMINAL_KEEP_INWARD_LEN,
        "terminal_keep_outward_len": TERMINAL_KEEP_OUTWARD_LEN,
        "notes": "Ogni terminale preserva un cerchio locale e una piccola capsula direzionata lungo il lato stimato, per tollerare terminali non perfettamente sul cavo.",
    }

    return (
        component_mask,
        terminal_keep_debug,
        masked_gray,
        binary,
        closed,
        filtered,
        skeleton,
        filter_info,
        keep_info,
    )



def main() -> None:
    if not INPUT_DIR.exists():
        raise FileNotFoundError(f"Cartella input non trovata: {INPUT_DIR}")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    MASK_DEBUG_DIR.mkdir(parents=True, exist_ok=True)
    COMPONENT_MASK_DIR.mkdir(parents=True, exist_ok=True)
    TERMINAL_KEEP_DEBUG_DIR.mkdir(parents=True, exist_ok=True)
    MASKED_DIR.mkdir(parents=True, exist_ok=True)
    BINARY_DIR.mkdir(parents=True, exist_ok=True)
    CLOSED_DIR.mkdir(parents=True, exist_ok=True)
    FILTERED_DIR.mkdir(parents=True, exist_ok=True)
    SKELETON_DIR.mkdir(parents=True, exist_ok=True)

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

        components = data.get("components", [])
        terminals = data.get("terminals", [])

        (
            component_mask,
            terminal_keep_debug,
            masked_gray,
            binary,
            closed,
            filtered,
            skeleton,
            filter_info,
            keep_info,
        ) = extract_wires_from_image(image_bgr, components, terminals)

        stem = json_path.stem

        mask_debug_path = MASK_DEBUG_DIR / f"{stem}_mask_debug.jpg"
        component_mask_path = COMPONENT_MASK_DIR / f"{stem}_component_mask.png"
        terminal_keep_debug_path = TERMINAL_KEEP_DEBUG_DIR / f"{stem}_terminal_keep_debug.jpg"
        masked_path = MASKED_DIR / f"{stem}_masked_gray.png"
        binary_path = BINARY_DIR / f"{stem}_binary.png"
        closed_path = CLOSED_DIR / f"{stem}_closed.png"
        filtered_path = FILTERED_DIR / f"{stem}_filtered.png"
        skeleton_path = SKELETON_DIR / f"{stem}_skeleton.png"

        save_mask_debug(image_bgr, component_mask, mask_debug_path)
        save_terminal_keep_debug(image_bgr, terminal_keep_debug, terminal_keep_debug_path)
        cv2.imwrite(str(component_mask_path), component_mask)
        cv2.imwrite(str(masked_path), masked_gray)
        cv2.imwrite(str(binary_path), binary)
        cv2.imwrite(str(closed_path), closed)
        cv2.imwrite(str(filtered_path), filtered)
        cv2.imwrite(str(skeleton_path), skeleton)

        output_data = dict(data)
        output_data["wire_extraction"] = {
            "notes": (
                "Versione topology_v1. Maschera i componenti e preserva per ogni terminale "
                "una zona locale direzionata, in modo da tollerare terminali stimati non "
                "perfettamente appoggiati sul cavo. Il testo non è ancora rimosso esplicitamente."
            ),
            "mask_shrink_factor": MASK_SHRINK_FACTOR,
            "terminal_keep": keep_info,
            "closing_kernel_size": CLOSING_KERNEL_SIZE,
            "closing_iterations": CLOSING_ITERATIONS,
            "small_component_filter": filter_info,
            "mask_debug_path": str(mask_debug_path),
            "component_mask_path": str(component_mask_path),
            "terminal_keep_debug_path": str(terminal_keep_debug_path),
            "masked_gray_path": str(masked_path),
            "binary_path": str(binary_path),
            "closed_path": str(closed_path),
            "filtered_path": str(filtered_path),
            "skeleton_path": str(skeleton_path),
        }

        out_json_path = OUTPUT_DIR / json_path.name
        with open(out_json_path, "w", encoding="utf-8") as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)

        print(f"[{i}/{len(json_files)}] {json_path.name} -> wire extraction completata")
        if ENABLE_SMALL_COMPONENT_FILTER:
            print(
                f"    filtro componenti piccoli -> kept={filter_info['kept_components']}, "
                f"removed={filter_info['removed_components']}"
            )

    print("\nCompletato.")
    print(f"Risultati salvati in: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
