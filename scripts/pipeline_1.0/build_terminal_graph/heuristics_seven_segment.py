from .ids import normalize_class_name


SEGMENT_LABELS = {"a", "b", "c", "d", "e", "f", "g", "h", "dp"}


def _is_seven_segment_display(component: dict) -> bool:
    return (
        normalize_class_name(component.get("class_name")) == "integrated_circuit"
        and component.get("component_subtype") == "seven_segment_display"
    )


def _bbox_values(component: dict):
    bbox = component.get("body_bbox") or component.get("bbox")
    if not bbox or len(bbox) != 4:
        return None
    return [float(v) for v in bbox]


def _horizontal_overlap_ratio(a: list[float], b: list[float]) -> float:
    overlap = max(0.0, min(a[3], b[3]) - max(a[1], b[1]))
    min_height = max(1.0, min(a[3] - a[1], b[3] - b[1]))
    return overlap / min_height


def _are_adjacent_displays(left: dict, right: dict) -> bool:
    left_bbox = _bbox_values(left)
    right_bbox = _bbox_values(right)
    if left_bbox is None or right_bbox is None:
        return False

    if left_bbox[0] > right_bbox[0]:
        left_bbox, right_bbox = right_bbox, left_bbox

    gap = right_bbox[0] - left_bbox[2]
    left_width = max(1.0, left_bbox[2] - left_bbox[0])
    right_width = max(1.0, right_bbox[2] - right_bbox[0])
    max_gap = max(80.0, 0.65 * min(left_width, right_width))

    return 0 <= gap <= max_gap and _horizontal_overlap_ratio(left_bbox, right_bbox) >= 0.55


def _segment_terminal_by_label(component: dict) -> dict[str, str]:
    by_label = {}
    for term in component.get("terminals", []):
        label = str(term.get("pin_label_text") or "").strip().lower()
        if label not in SEGMENT_LABELS:
            continue
        if term.get("terminal_id"):
            by_label.setdefault(label, term["terminal_id"])
    return by_label


def build_seven_segment_shared_segment_edges(components: list[dict]):
    displays = [comp for comp in components if _is_seven_segment_display(comp)]
    edges = []

    for i, left in enumerate(displays):
        for right in displays[i + 1:]:
            if not _are_adjacent_displays(left, right):
                continue

            left_by_label = _segment_terminal_by_label(left)
            right_by_label = _segment_terminal_by_label(right)
            for label in sorted(set(left_by_label) & set(right_by_label)):
                edges.append((left_by_label[label], right_by_label[label]))

    return edges
