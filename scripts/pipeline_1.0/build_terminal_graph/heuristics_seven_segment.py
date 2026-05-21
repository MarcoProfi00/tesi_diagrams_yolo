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


def _component_by_instance(components: list[dict]) -> dict[str, dict]:
    mapping = {}
    for component in components:
        instance_id = component.get("instance_id")
        if instance_id is None:
            continue
        mapping[str(instance_id)] = component
    return mapping


def _is_display_segment_terminal(term: dict, component_by_instance: dict[str, dict]) -> bool:
    instance_id = term.get("instance_id")
    if instance_id is None:
        return False
    component = component_by_instance.get(str(instance_id))
    if not component or not _is_seven_segment_display(component):
        return False
    label = str(term.get("pin_label_text") or "").strip().lower()
    return label in SEGMENT_LABELS


def split_seven_segment_segment_label_groups(
    label_to_terminal_ids: dict,
    terminals: list[dict],
    components: list[dict],
):
    term_by_id = {
        str(term.get("terminal_id")): term
        for term in terminals
        if term.get("terminal_id")
    }
    component_by_instance = _component_by_instance(components)
    rewritten_groups = []

    for terminal_ids in label_to_terminal_ids.values():
        display_terms = []
        for terminal_id in terminal_ids:
            term = term_by_id.get(str(terminal_id))
            if term is None:
                continue
            if _is_display_segment_terminal(term, component_by_instance):
                display_terms.append(term)

        display_labels = {
            str(term.get("pin_label_text") or "").strip().lower()
            for term in display_terms
        }
        if len(display_terms) < 2 or len(display_labels) < 2:
            rewritten_groups.append(list(terminal_ids))
            continue

        split_groups = {}
        for term in display_terms:
            label = str(term.get("pin_label_text") or "").strip().lower()
            split_groups.setdefault(label, []).append(str(term["terminal_id"]))

        anchor_by_label = {
            label: sum(float(term["y"]) for term in display_terms if str(term.get("pin_label_text") or "").strip().lower() == label)
            / max(
                1,
                sum(
                    1
                    for term in display_terms
                    if str(term.get("pin_label_text") or "").strip().lower() == label
                ),
            )
            for label in split_groups
        }

        for terminal_id in terminal_ids:
            terminal_id = str(terminal_id)
            if any(terminal_id in members for members in split_groups.values()):
                continue

            term = term_by_id.get(terminal_id)
            if term is None:
                continue

            try:
                y_value = float(term["y"])
            except (KeyError, TypeError, ValueError):
                continue

            label = min(
                anchor_by_label,
                key=lambda current: abs(y_value - anchor_by_label[current]),
            )
            split_groups[label].append(terminal_id)

        rewritten_groups.extend(list(split_groups.values()))

    relabeled = {}
    next_label = 1
    for group in rewritten_groups:
        unique_ids = sorted(set(group))
        if not unique_ids:
            continue
        relabeled[next_label] = unique_ids
        next_label += 1

    return relabeled


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
