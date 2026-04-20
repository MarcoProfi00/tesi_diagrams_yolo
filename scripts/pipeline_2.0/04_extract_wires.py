"""
04_extract_wires.py

Scopo:
    Estrarre i wire dal diagramma mascherando i componenti
    e preservando localmente le zone dei terminali.

Output principali:
    - component_mask
    - masked_gray
    - binary
    - closed
    - filtered
    - skeleton
"""

from pathlib import Path
import os
import json
import cv2
import numpy as np
from skimage.morphology import skeletonize

# =========================================================
# PATHS / INPUT-OUTPUT
# =========================================================
PROJECT_ROOT = Path(__file__).resolve().parents[2]
PIPELINE_DATASET = os.environ.get("PIPELINE_DATASET", "pipeline2.0/batch_v6_operational_amplifier")

INPUT_DIR = PROJECT_ROOT / "outputs" / PIPELINE_DATASET / "03_estimate_terminals"
OUTPUT_DIR = PROJECT_ROOT / "outputs" / PIPELINE_DATASET / "04_extract_wires"

# =========================================================
# COMPONENT MASKING
# =========================================================
MASK_DEBUG_DIR = OUTPUT_DIR / "mask_debug"
COMPONENT_MASK_DIR = OUTPUT_DIR / "component_mask"
TERMINAL_KEEP_DEBUG_DIR = OUTPUT_DIR / "terminal_keep_debug"
MASKED_DIR = OUTPUT_DIR / "masked_gray"
BINARY_DIR = OUTPUT_DIR / "binary"
CLOSED_DIR = OUTPUT_DIR / "closed"
BRIDGED_DIR = OUTPUT_DIR / "bridged"
FILTERED_DIR = OUTPUT_DIR / "filtered"
SKELETON_DIR = OUTPUT_DIR / "skeleton"


MASK_SHRINK_FACTOR = 1.0
CLASS_MASK_PADDING = {
    "Analog_Meter": 8,
    "Connector": 6,
    "Switch": 4,
    "Transformer": 4,
}

# =========================================================
# TERMINAL KEEP ZONES
# =========================================================
TERMINAL_KEEP_RADIUS = 10
TERMINAL_KEEP_LINE_THICKNESS = 7
TERMINAL_KEEP_INWARD_LEN = 14
TERMINAL_KEEP_OUTWARD_LEN = 12
OPAMP_AUX_KEEP_RADIUS = 5
OPAMP_AUX_KEEP_LINE_THICKNESS = 5
OPAMP_AUX_KEEP_INWARD_LEN = 0
OPAMP_AUX_KEEP_OUTWARD_LEN = 12

CLASS_TERMINAL_KEEP_OVERRIDES = {
    # Questi simboli hanno molto "corpo" interno e, se preserviamo troppo
    # dentro al bbox, rischiamo di riaprire il simbolo nello skeleton.
    "Analog_Meter": {
        "radius": 8,
        "thickness": 6,
        "inward_len": 4,
        "outward_len": 14,
    },
    "Connector": {
        "radius": 8,
        "thickness": 6,
        "inward_len": 3,
        "outward_len": 14,
    },
    "Switch": {
        "radius": 8,
        "thickness": 6,
        "inward_len": 2,
        "outward_len": 16,
    },
    "Transformer": {
        "radius": 8,
        "thickness": 6,
        "inward_len": 4,
        "outward_len": 14,
    },
}

# =========================================================
# MORPHOLOGY
# =========================================================
CLOSING_KERNEL_SIZE = 3
CLOSING_ITERATIONS = 1
ENABLE_FRAGMENTED_WIRE_BRIDGE = True
FRAGMENTED_WIRE_BRIDGE_KERNEL_LENGTH = 15
FRAGMENTED_WIRE_BRIDGE_KERNEL_THICKNESS = 3
FRAGMENTED_WIRE_BRIDGE_ITERATIONS = 1

# =========================================================
# SMALL COMPONENT FILTER
# =========================================================
ENABLE_SMALL_COMPONENT_FILTER = True
MIN_COMPONENT_AREA = 40

# utility geometriche
# Clamp point.
def clamp_point(x, y, w, h):
    x = max(0, min(w - 1, int(round(x))))
    y = max(0, min(h - 1, int(round(y))))
    return x, y



# Shrink bounding box.
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


# Expand bounding box.
def expand_bbox(bbox, pad=0):
    x1, y1, x2, y2 = bbox
    return [x1 - pad, y1 - pad, x2 + pad, y2 + pad]

# costruzione maschere
# Build base component mask.
def build_base_component_mask(image_shape, components):
    h, w = image_shape[:2]
    mask = np.zeros((h, w), dtype=np.uint8)

    for comp in components:
        if not comp.get("use_for_masking", False):
            continue

        bbox = shrink_bbox(comp["bbox"], shrink_factor=MASK_SHRINK_FACTOR)
        bbox = expand_bbox(
            bbox,
            pad=int(CLASS_MASK_PADDING.get(str(comp.get("class_name", "")).strip(), 0)),
        )
        x1, y1, x2, y2 = map(int, bbox)

        x1 = max(0, min(w - 1, x1))
        y1 = max(0, min(h - 1, y1))
        x2 = max(0, min(w - 1, x2))
        y2 = max(0, min(h - 1, y2))

        cv2.rectangle(mask, (x1, y1), (x2, y2), 255, thickness=-1)

    return mask

# Terminal keep params.
def terminal_keep_params(term):
    name = str(term.get("name", "")).lower()
    class_name = str(term.get("component_class_name", "")).strip()

    if name in {"aux1", "aux2"}:
        return {
            "radius": OPAMP_AUX_KEEP_RADIUS,
            "thickness": OPAMP_AUX_KEEP_LINE_THICKNESS,
            "inward_len": OPAMP_AUX_KEEP_INWARD_LEN,
            "outward_len": OPAMP_AUX_KEEP_OUTWARD_LEN,
        }

    if class_name in CLASS_TERMINAL_KEEP_OVERRIDES:
        return dict(CLASS_TERMINAL_KEEP_OVERRIDES[class_name])

    return {
        "radius": TERMINAL_KEEP_RADIUS,
        "thickness": TERMINAL_KEEP_LINE_THICKNESS,
        "inward_len": TERMINAL_KEEP_INWARD_LEN,
        "outward_len": TERMINAL_KEEP_OUTWARD_LEN,
    }


# Terminal keep segment.
def terminal_keep_segment(term):
    x = float(term["x"])
    y = float(term["y"])
    rel = term.get("relative_position")
    params = terminal_keep_params(term)

    inward_len = params["inward_len"]
    outward_len = params["outward_len"]

    if rel == "left":
        p1 = (x - outward_len, y)
        p2 = (x + inward_len, y)
    elif rel == "right":
        p1 = (x - inward_len, y)
        p2 = (x + outward_len, y)
    elif rel == "top":
        p1 = (x, y - outward_len)
        p2 = (x, y + inward_len)
    elif rel == "bottom":
        p1 = (x, y - inward_len)
        p2 = (x, y + outward_len)
    else:
        p1 = (x, y)
        p2 = (x, y)

    return p1, p2


# Carve terminal keep zones.
def carve_terminal_keep_zones(mask, terminals):
    h, w = mask.shape[:2]
    keep_debug = np.zeros_like(mask)

    for term in terminals:
        params = terminal_keep_params(term)

        x = int(round(term["x"]))
        y = int(round(term["y"]))
        x, y = clamp_point(x, y, w, h)

        cv2.circle(mask, (x, y), params["radius"], 0, thickness=-1)
        cv2.circle(keep_debug, (x, y), params["radius"], 255, thickness=-1)

        p1f, p2f = terminal_keep_segment(term)
        p1 = clamp_point(p1f[0], p1f[1], w, h)
        p2 = clamp_point(p2f[0], p2f[1], w, h)

        cv2.line(mask, p1, p2, 0, thickness=params["thickness"])
        cv2.line(keep_debug, p1, p2, 255, thickness=params["thickness"])

    return mask, keep_debug


# Build component mask.
def build_component_mask(image_shape, components, terminals):
    mask = build_base_component_mask(image_shape, components)
    mask, keep_debug = carve_terminal_keep_zones(mask, terminals)
    return mask, keep_debug

# debug outputs
# Save mask debug view.
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


# Save terminal keep debug view.
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

# post-processing wires
# Remove small connected components.
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


# Bridge fragmented wires.
def bridge_fragmented_wires(binary_img):
    if not ENABLE_FRAGMENTED_WIRE_BRIDGE:
        return binary_img.copy(), {
            "enabled": False,
            "kernel_length": None,
            "kernel_thickness": None,
            "iterations": None,
        }

    h_kernel = cv2.getStructuringElement(
        cv2.MORPH_RECT,
        (
            FRAGMENTED_WIRE_BRIDGE_KERNEL_LENGTH,
            FRAGMENTED_WIRE_BRIDGE_KERNEL_THICKNESS,
        ),
    )
    v_kernel = cv2.getStructuringElement(
        cv2.MORPH_RECT,
        (
            FRAGMENTED_WIRE_BRIDGE_KERNEL_THICKNESS,
            FRAGMENTED_WIRE_BRIDGE_KERNEL_LENGTH,
        ),
    )

    bridged = cv2.morphologyEx(
        binary_img,
        cv2.MORPH_CLOSE,
        h_kernel,
        iterations=FRAGMENTED_WIRE_BRIDGE_ITERATIONS,
    )
    bridged = cv2.morphologyEx(
        bridged,
        cv2.MORPH_CLOSE,
        v_kernel,
        iterations=FRAGMENTED_WIRE_BRIDGE_ITERATIONS,
    )

    return bridged, {
        "enabled": True,
        "kernel_length": FRAGMENTED_WIRE_BRIDGE_KERNEL_LENGTH,
        "kernel_thickness": FRAGMENTED_WIRE_BRIDGE_KERNEL_THICKNESS,
        "iterations": FRAGMENTED_WIRE_BRIDGE_ITERATIONS,
        "notes": "Closing anisotropo orizzontale+verticale per ricucire tratti tratteggiati o frammentati.",
    }


# Extract wires from image.
def extract_wires_from_image(image_bgr, components, terminals):
    # 1. grayscale
    gray = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2GRAY)

    # 2. component mask + terminal keep zones
    component_mask, terminal_keep_debug = build_component_mask(
        image_bgr.shape, components, terminals
    )

    # 3. apply mask
    masked_gray = gray.copy()
    masked_gray[component_mask > 0] = 255

    # 4. threshold
    _, binary = cv2.threshold(
        masked_gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU
    )

    # 5. closing
    kernel = cv2.getStructuringElement(
        cv2.MORPH_RECT, (CLOSING_KERNEL_SIZE, CLOSING_KERNEL_SIZE)
    )
    closed = cv2.morphologyEx(
        binary,
        cv2.MORPH_CLOSE,
        kernel,
        iterations=CLOSING_ITERATIONS,
    )

    # 6. bridge fragmented dashed wires
    bridged, bridge_info = bridge_fragmented_wires(closed)

    # 7. small component filter
    if ENABLE_SMALL_COMPONENT_FILTER:
        filtered, kept_components, removed_components = remove_small_connected_components(
            bridged,
            min_area=MIN_COMPONENT_AREA,
        )
    else:
        filtered = bridged.copy()
        kept_components = None
        removed_components = None

    # 8. skeletonization
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
        bridged,
        filtered,
        skeleton,
        filter_info,
        keep_info,
        bridge_info,
    )

# main
# Run the entrypoint for this pipeline stage.
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
    BRIDGED_DIR.mkdir(parents=True, exist_ok=True)
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
            bridged,
            filtered,
            skeleton,
            filter_info,
            keep_info,
            bridge_info,
        ) = extract_wires_from_image(image_bgr, components, terminals)

        stem = json_path.stem

        mask_debug_path = MASK_DEBUG_DIR / f"{stem}_mask_debug.jpg"
        component_mask_path = COMPONENT_MASK_DIR / f"{stem}_component_mask.png"
        terminal_keep_debug_path = TERMINAL_KEEP_DEBUG_DIR / f"{stem}_terminal_keep_debug.jpg"
        masked_path = MASKED_DIR / f"{stem}_masked_gray.png"
        binary_path = BINARY_DIR / f"{stem}_binary.png"
        closed_path = CLOSED_DIR / f"{stem}_closed.png"
        bridged_path = BRIDGED_DIR / f"{stem}_bridged.png"
        filtered_path = FILTERED_DIR / f"{stem}_filtered.png"
        skeleton_path = SKELETON_DIR / f"{stem}_skeleton.png"

        save_mask_debug(image_bgr, component_mask, mask_debug_path)
        save_terminal_keep_debug(image_bgr, terminal_keep_debug, terminal_keep_debug_path)
        cv2.imwrite(str(component_mask_path), component_mask)
        cv2.imwrite(str(masked_path), masked_gray)
        cv2.imwrite(str(binary_path), binary)
        cv2.imwrite(str(closed_path), closed)
        cv2.imwrite(str(bridged_path), bridged)
        cv2.imwrite(str(filtered_path), filtered)
        cv2.imwrite(str(skeleton_path), skeleton)

        output_data = dict(data)
        output_data["wire_extraction"] = {
            "mask_shrink_factor": MASK_SHRINK_FACTOR,
            "terminal_keep": keep_info,
            "closing_kernel_size": CLOSING_KERNEL_SIZE,
            "closing_iterations": CLOSING_ITERATIONS,
            "fragmented_wire_bridge": bridge_info,
            "small_component_filter": filter_info,
            "mask_debug_path": str(mask_debug_path),
            "component_mask_path": str(component_mask_path),
            "terminal_keep_debug_path": str(terminal_keep_debug_path),
            "masked_gray_path": str(masked_path),
            "binary_path": str(binary_path),
            "closed_path": str(closed_path),
            "bridged_path": str(bridged_path),
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
