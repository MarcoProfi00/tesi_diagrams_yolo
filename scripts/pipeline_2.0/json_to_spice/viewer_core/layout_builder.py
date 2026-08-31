"""
Genera un layout visuale semplice per il viewer della Pipeline 2.0.

Lo step 14 legge `13_viewer_model.json` e produce `14_viewer_layout.json`.
Il suo compito non e' ricostruire l'immagine originale, ma calcolare posizioni
leggibili per componenti, nodi e rami a partire dal modello netlist-first.
"""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal, localcontext
import math
import re
from pathlib import Path
from typing import Any

from .component_library import component_spec, normalize_component_type
from .contracts import (
    VIEWER_LAYOUT_NAME,
    VIEWER_LAYOUT_SCHEMA_VERSION,
    VIEWER_MODEL_NAME,
)
from .json_io import read_json, write_json
from .model_builder import is_variable_voltage_source


# Il canvas mantiene proporzioni stabili e riserva una fascia per la legenda.
VIEWER_CANVAS_WIDTH = 1040.0
VIEWER_CANVAS_HEIGHT = 620.0
VIEWER_LEGEND_WIDTH = 180.0
VIEWER_LEGEND_RIGHT_MARGIN = 25.0
VIEWER_LEGEND_CLEARANCE = 30.0
VIEWER_LEGEND_LEFT = VIEWER_CANVAS_WIDTH - VIEWER_LEGEND_RIGHT_MARGIN - VIEWER_LEGEND_WIDTH
VIEWER_CONTENT_WIDTH = VIEWER_LEGEND_LEFT - VIEWER_LEGEND_CLEARANCE


def legend_obstacle_bounds() -> tuple[float, float, float, float]:
    """Restituisce l'ingombro riservato alla legenda per placement e routing."""
    return (VIEWER_LEGEND_LEFT - 10.0, 14.0, VIEWER_CANVAS_WIDTH - 15.0, 222.0)


def component_label(component: dict[str, Any]) -> str:
    """Restituisce una label compatta per un componente del viewer."""
    if component.get("viewer_label") is not None:
        return str(component.get("viewer_label") or "")
    if component.get("viewer_kind") == "terminal":
        return str(component.get("display_label") or component.get("id") or "")
    kind = str(component.get("kind") or component.get("class_name") or "").lower()
    value = str(component.get("value") or "")
    if kind == "resistor":
        return value or "R"
    if kind == "diode":
        return str(component.get("spice_name") or component.get("id") or "D")
    if kind == "voltage_source":
        return value or "V"
    if "switch" in kind:
        return "SW"
    if "connector" in kind:
        return str(component.get("id") or "J")
    if "meter" in kind:
        return str(component.get("display_label") or (component.get("parameters") or {}).get("label_text") or "METER")
    return str(component.get("id") or kind or "component")


def component_nodes(component: dict[str, Any]) -> list[str]:
    """Estrae i nodi di un componente, gestendo sia liste sia mappe terminale-nodo."""
    nodes = component.get("nodes") or []
    if isinstance(nodes, dict):
        return [str(value) for value in nodes.values()]
    if isinstance(nodes, list):
        return [str(value) for value in nodes]
    return []


def classify_component(component: dict[str, Any]) -> str:
    """Classifica il componente in una categoria grafica semplice."""
    if component.get("viewer_kind"):
        return str(component["viewer_kind"])
    kind = str(component.get("kind") or component.get("class_name") or "").lower()
    class_name = str(component.get("class_name") or "").lower()
    component_id = str(component.get("id") or "").lower()
    # La netlist usa sempre il prefisso C: la classe originale conserva la
    # polarita necessaria per scegliere il simbolo corretto nel viewer.
    if class_name == "polarized_capacitor":
        return "polarized_capacitor"
    if "connector" in kind or "connector" in component_id:
        return "connector"
    if "switch" in kind or "switch" in component_id:
        return "switch"
    if component_id.startswith("gnd") or "ground" in kind:
        return "ground"
    if "meter" in kind or component.get("measurement_kind"):
        return "analog_meter"
    if is_variable_voltage_source(component):
        return "signal_source"
    if kind == "voltage_source" and component.get("is_scenario_added"):
        return "scenario_voltage_source"
    if kind in {"resistor", "diode", "voltage_source", "current_source", "capacitor", "inductor"}:
        return kind
    return "structural"


def collect_layout_components(model: dict[str, Any]) -> list[dict[str, Any]]:
    """Unisce componenti SPICE e strutturali in una lista adatta al layout."""
    items: list[dict[str, Any]] = []
    geometry_component_ids = set(((model.get("geometry_seed") or {}).get("components") or {}).keys())
    structural_ids = {
        str(component.get("id") or "")
        for component in model.get("structural_components") or []
        if isinstance(component, dict)
    }
    connector_nodes = {
        str(node_id)
        for component in model.get("structural_components") or []
        if isinstance(component, dict) and "connector" in str(component.get("class_name") or "").lower()
        for node_id in component_nodes(component)
    }
    for source, is_structural in (
        (model.get("netlist_components") or [], False),
        (model.get("structural_components") or [], True),
    ):
        for component in source:
            if not isinstance(component, dict):
                continue
            if component.get("viewer_kind") == "node_voltage_clamp":
                # Il vincolo diagnostico viene annotato sul nodo, non disegnato come batteria.
                continue
            if component.get("viewer_proxy_for"):
                # Lo strumento strutturale rappresenta gia' il suo equivalente numerico SPICE.
                continue
            if component.get("viewer_hidden"):
                # Riferimenti numerici e altri ausili SPICE non sono componenti fisici.
                continue
            if component.get("viewer_hidden_by_terminal"):
                # Il terminale strutturale mostra gia' questa alimentazione sullo schema.
                continue
            source_id = str(component.get("source_component_id") or "")
            represented_structural_id = source_id.removeprefix("scenario_")
            if component.get("is_scenario_added") and represented_structural_id in structural_ids:
                # Lo switch strutturale rappresenta gia' il resistore SPICE usato per chiuderlo.
                continue
            component_node_ids = set(component_nodes(component))
            is_external_connector_source = (
                component.get("kind") == "voltage_source"
                and not component.get("is_scenario_added")
                and source_id not in geometry_component_ids
                and "0" in component_node_ids
                and bool(component_node_ids & connector_nodes)
            )
            if is_external_connector_source:
                # La sorgente sintetica e' gia' rappresentata dall'alimentazione esterna del connector.
                continue
            item = dict(component)
            item["layout_kind"] = classify_component(component)
            item["is_structural"] = is_structural
            item["label"] = component_label(item)
            item["nodes"] = component_nodes(component)
            items.append(item)
    return items


def canvas_transform(geometry_seed: dict[str, Any]) -> dict[str, float]:
    """Adatta le bbox all'area circuito, lasciando libera la fascia della legenda."""
    image = geometry_seed.get("image") or {}
    image_width = max(float(image.get("width") or 1), 1.0)
    image_height = max(float(image.get("height") or 1), 1.0)
    canvas_width = VIEWER_CANVAS_WIDTH
    canvas_height = VIEWER_CANVAS_HEIGHT
    margin = 48.0
    bboxes = [
        component.get("bbox")
        for component in (geometry_seed.get("components") or {}).values()
        if isinstance(component, dict) and isinstance(component.get("bbox"), list) and len(component["bbox"]) == 4
    ]
    if bboxes:
        left = min(float(bbox[0]) for bbox in bboxes)
        top = min(float(bbox[1]) for bbox in bboxes)
        right = max(float(bbox[2]) for bbox in bboxes)
        bottom = max(float(bbox[3]) for bbox in bboxes)
        # Il margine e' espresso nello spazio immagine: evita simboli aderenti ai bordi del viewer.
        footprint_padding = 64.0
        source_left = max(0.0, left - footprint_padding)
        source_top = max(0.0, top - footprint_padding)
        source_right = min(image_width, right + footprint_padding)
        source_bottom = min(image_height, bottom + footprint_padding)
    else:
        source_left, source_top = 0.0, 0.0
        source_right, source_bottom = image_width, image_height
    source_width = max(source_right - source_left, 1.0)
    source_height = max(source_bottom - source_top, 1.0)
    # La legenda occupa sempre la destra del canvas e non puo' sovrapporsi al circuito.
    scale = min((VIEWER_CONTENT_WIDTH - 2 * margin) / source_width, (canvas_height - 2 * margin) / source_height)
    offset_x = (VIEWER_CONTENT_WIDTH - source_width * scale) / 2 - source_left * scale
    offset_y = (canvas_height - source_height * scale) / 2 - source_top * scale
    return {
        "scale": scale,
        "offset_x": offset_x,
        "offset_y": offset_y,
        "canvas_width": canvas_width,
        "canvas_height": canvas_height,
        "content_width": VIEWER_CONTENT_WIDTH,
        "legend_left": VIEWER_LEGEND_LEFT,
        "source_left": source_left,
        "source_top": source_top,
        "source_width": source_width,
        "source_height": source_height,
    }


def transform_point(x: Any, y: Any, transform: dict[str, float]) -> dict[str, float]:
    """Converte una coordinata immagine nella coordinata equivalente del canvas."""
    return {
        "x": round(transform["offset_x"] + float(x) * transform["scale"], 2),
        "y": round(transform["offset_y"] + float(y) * transform["scale"], 2),
    }


def transform_bbox(bbox: Any, transform: dict[str, float]) -> list[float] | None:
    """Converte una bbox immagine nel rettangolo equivalente del canvas."""
    if not isinstance(bbox, (list, tuple)) or len(bbox) != 4:
        return None
    try:
        first = transform_point(bbox[0], bbox[1], transform)
        second = transform_point(bbox[2], bbox[3], transform)
    except (TypeError, ValueError):
        return None
    return [
        min(first["x"], second["x"]),
        min(first["y"], second["y"]),
        max(first["x"], second["x"]),
        max(first["y"], second["y"]),
    ]


def visual_source_id(component: dict[str, Any]) -> str:
    """Restituisce l'id Pipeline 1.0 associato a un componente del modello."""
    return str(component.get("source_component_id") or component.get("id") or "")


def anchored_geometry_component(
    component: dict[str, Any],
    geometry_components: dict[str, Any],
) -> dict[str, Any] | None:
    """Costruisce una geometria da due port esterni dichiarati nel viewer."""
    anchor_ids = [str(item) for item in component.get("viewer_anchor_component_ids") or []]
    anchors = [geometry_components.get(anchor_id) for anchor_id in anchor_ids]
    anchors = [item for item in anchors if isinstance(item, dict)]
    nodes = [str(node) for node in component.get("nodes") or []]
    terminal_names = [str(name) for name in component.get("terminal_names") or []]
    if len(anchors) != 2 or len(nodes) < 2:
        return None

    centers = [item.get("center") or {} for item in anchors]
    try:
        center_x = sum(float(item.get("x")) for item in centers) / 2
        center_y = sum(float(item.get("y")) for item in centers) / 2
    except (TypeError, ValueError):
        return None
    bboxes = [item.get("bbox") for item in anchors]
    valid_bboxes = [item for item in bboxes if isinstance(item, list) and len(item) == 4]
    bbox = (
        [
            min(float(item[0]) for item in valid_bboxes),
            min(float(item[1]) for item in valid_bboxes),
            max(float(item[2]) for item in valid_bboxes),
            max(float(item[3]) for item in valid_bboxes),
        ]
        if valid_bboxes
        else [center_x - 10, center_y - 30, center_x + 10, center_y + 30]
    )
    terminals: dict[str, dict[str, Any]] = {}
    for index, (anchor, node_id) in enumerate(zip(anchors, nodes)):
        name = terminal_names[index] if index < len(terminal_names) else f"t{index + 1}"
        anchor_terminal = next(iter((anchor.get("terminals") or {}).values()), {})
        anchor_center = anchor.get("center") or {}
        terminals[name] = {
            "id": str(anchor_terminal.get("id") or f"{anchor_ids[index]}_t1"),
            "name": name,
            "relative_position": "top" if index == 0 else "bottom",
            "x": anchor_terminal.get("x", anchor_center.get("x")),
            "y": anchor_terminal.get("y", anchor_center.get("y")),
            "node_id": node_id,
        }
    return {
        "component_id": visual_source_id(component),
        "class_name": str(component.get("viewer_kind") or "Component"),
        "bbox": bbox,
        "center": {"x": center_x, "y": center_y},
        "estimated_orientation": "vertical" if abs(float(centers[1]["y"]) - float(centers[0]["y"])) >= abs(float(centers[1]["x"]) - float(centers[0]["x"])) else "horizontal",
        "terminals": terminals,
    }


def normalize_orientation(value: Any) -> str:
    """Riduce le orientazioni della Pipeline 1.0 alle varianti del renderer."""
    orientation = str(value or "").lower()
    if orientation in {"vertical", "up", "down"}:
        return "vertical"
    return "horizontal"


def match_geometry_terminals(
    component: dict[str, Any],
    geometry_component: dict[str, Any],
    transform: dict[str, float],
) -> list[dict[str, Any]]:
    """Associa i nodi del modello ai terminali geometrici dello stesso componente."""
    geometry_terminals = geometry_component.get("terminals") or {}
    matched: list[dict[str, Any]] = []
    used_names: set[str] = set()
    terminal_names = [str(name) for name in component.get("terminal_names") or []]

    # La corrispondenza per nodo evita di dipendere dai nomi t1, anode o pin1.
    for index, node_id in enumerate(component.get("nodes") or [], start=1):
        selected_name = ""
        selected: dict[str, Any] = {}
        logical_name = terminal_names[index - 1] if index <= len(terminal_names) else ""
        if logical_name and logical_name in geometry_terminals and logical_name not in used_names:
            selected_name = logical_name
            selected = geometry_terminals[logical_name]
        for name, terminal in geometry_terminals.items():
            if not selected and name not in used_names and str(terminal.get("node_id") or "") == str(node_id):
                selected_name = str(name)
                selected = terminal
                break
        if not selected and logical_name and logical_name not in geometry_terminals:
            # Un pin aggiunto dall'overlay SPICE non possiede coordinate OCR.
            # Parte dal centro e viene collocato dallo standardizzatore del
            # simbolo, mantenendo dichiarativi nome e nodo elettrico.
            center = geometry_component.get("center") or {}
            selected_name = logical_name
            selected = {
                "id": f"{visual_source_id(component)}_{logical_name}",
                "relative_position": "synthetic",
                "x": center.get("x"),
                "y": center.get("y"),
            }
        if not selected:
            remaining = [(name, item) for name, item in geometry_terminals.items() if name not in used_names]
            if remaining:
                selected_name, selected = remaining[0]
        if not selected:
            continue
        used_names.add(selected_name)
        point = transform_point(selected.get("x"), selected.get("y"), transform)
        matched.append(
            {
                "name": selected_name or f"t{index}",
                "terminal_id": str(selected.get("id") or ""),
                "node_id": str(node_id),
                "relative_position": str(selected.get("relative_position") or ""),
                **point,
            }
        )
    return matched


def standardize_terminals(
    terminals: list[dict[str, Any]],
    center: dict[str, float],
    component_type: str,
    orientation: str,
) -> list[dict[str, Any]]:
    """Porta i terminali sui punti di attacco standard del simbolo visuale."""
    if not terminals:
        return []
    spec = component_spec(component_type, component_type, len(terminals))
    center_x, center_y = float(center["x"]), float(center["y"])
    standardized = [dict(terminal) for terminal in terminals]

    if component_type == "integrated_circuit":
        # Per gli IC la bbox della Pipeline 1.0 e le coordinate dei pin sono
        # gia' il simbolo: non li proiettiamo su un ingombro standard.
        return standardized

    if component_type == "connector":
        # Tutti i connector usano pin centrati, equidistanti e indipendenti dalla bbox.
        ordered = sorted(standardized, key=lambda item: float(item.get("y") or 0))
        spacing = spec["pin_spacing"]
        start_y = center_y - spacing * (len(ordered) - 1) / 2
        for index, terminal in enumerate(ordered):
            terminal["x"] = center_x
            terminal["y"] = start_y + index * spacing
            terminal["pin_number"] = index + 1
        return ordered

    if component_type == "ground":
        standardized[0]["x"] = center_x
        standardized[0]["y"] = center_y - spec["height"] / 2
        return standardized[:1]

    if component_type == "antenna":
        # L'antenna ha un solo punto elettrico, posto alla base dello stelo.
        standardized[0]["x"] = center_x
        standardized[0]["y"] = center_y + spec["height"] / 2
        return standardized[:1]

    if component_type == "headset" and len(standardized) == 2:
        # Le due prese della cuffia restano sullo stesso lato, come nel simbolo
        # circuitale originale, ma conservano i rispettivi nodi elettrici.
        ordered = sorted(standardized, key=lambda item: float(item.get("y") or 0))
        for index, terminal in enumerate(ordered):
            terminal["x"] = center_x - spec["width"] / 2
            terminal["y"] = center_y + (-22.0 if index == 0 else 22.0)
        return ordered

    if component_type == "speaker" and len(standardized) == 2:
        # L'altoparlante conserva due terminali sullo stesso lato, come il
        # simbolo elettrico, lasciando il cono libero sul lato opposto.
        ordered = sorted(standardized, key=lambda item: float(item.get("y") or 0))
        for index, terminal in enumerate(ordered):
            terminal["x"] = center_x - spec["width"] / 2
            terminal["y"] = center_y + (-22.0 if index == 0 else 22.0)
        return ordered

    if component_type == "operational_amplifier" and len(standardized) >= 3:
        # Schema comune per operazionali e amplificatori audio a triangolo:
        # ingressi a sinistra, uscita a destra, alimentazioni sopra e sotto.
        by_name = {str(item.get("name") or "").lower(): item for item in standardized}
        positions = {
            "in1": (-spec["width"] / 2, -18.0),
            "inp": (-spec["width"] / 2, -18.0),
            "in2": (-spec["width"] / 2, 18.0),
            "inm": (-spec["width"] / 2, 18.0),
            "out": (spec["width"] / 2, 0.0),
            "aux1": (4.0, -spec["height"] / 2),
            "vcc": (4.0, -spec["height"] / 2),
            "aux2": (4.0, spec["height"] / 2),
            "vee": (4.0, spec["height"] / 2),
        }
        ordered: list[dict[str, Any]] = []
        used_ids: set[int] = set()
        for name, offset in positions.items():
            terminal = by_name.get(name)
            if terminal is None or id(terminal) in used_ids:
                continue
            terminal.update({"x": center_x + offset[0], "y": center_y + offset[1]})
            ordered.append(terminal)
            used_ids.add(id(terminal))
        for terminal in standardized:
            if id(terminal) not in used_ids:
                terminal.update({"x": center_x, "y": center_y})
                ordered.append(terminal)
        return ordered

    if component_type == "scr" and len(standardized) >= 3:
        # SCR standard: anodo e catodo sull'asse principale, gate in basso
        # vicino al catodo. I nomi provengono dalla node_order dello step 06.
        by_name = {str(item.get("name") or "").lower(): item for item in standardized}
        anode = by_name.get("anode") or standardized[0]
        gate = by_name.get("gate") or standardized[1]
        cathode = by_name.get("cathode") or standardized[-1]
        anode.update({"x": center_x - spec["width"] / 2, "y": center_y})
        cathode.update({"x": center_x + spec["width"] / 2, "y": center_y})
        gate.update({"x": center_x + 12.0, "y": center_y + spec["height"] / 2})
        return [anode, gate, cathode]

    if component_type == "transformer" and len(standardized) >= 4:
        # Il trasformatore conserva le quattro porte del Graph anche quando
        # SPICE emette soltanto una sorgente equivalente sul secondario.
        by_name = {str(item.get("name") or "").lower(): item for item in standardized}
        offsets = {
            "t1": (-spec["width"] / 2, -25.0),
            "t2": (spec["width"] / 2, -25.0),
            "t3": (-spec["width"] / 2, 25.0),
            "t4": (spec["width"] / 2, 25.0),
        }
        ordered: list[dict[str, Any]] = []
        for name in ("t1", "t2", "t3", "t4"):
            terminal = by_name.get(name)
            if terminal is None:
                continue
            offset_x, offset_y = offsets[name]
            terminal.update({"x": center_x + offset_x, "y": center_y + offset_y})
            ordered.append(terminal)
        return ordered

    if len(standardized) == 2:
        # I bipoli usano sempre la stessa lunghezza e rispettano l'ordine rilevato.
        ordered = sorted(
            standardized,
            key=lambda item: float(item.get("y") or 0) if orientation == "vertical" else float(item.get("x") or 0),
        )
        if orientation == "vertical":
            # Il simbolo viene ruotato dal renderer: la lunghezza elettrica resta `width`.
            ordered[0].update({"x": center_x, "y": center_y - spec["width"] / 2})
            ordered[1].update({"x": center_x, "y": center_y + spec["width"] / 2})
        else:
            ordered[0].update({"x": center_x - spec["width"] / 2, "y": center_y})
            ordered[1].update({"x": center_x + spec["width"] / 2, "y": center_y})
        return ordered

    # I componenti multi-terminale mantengono il lato relativo attorno a un ingombro standard.
    # Evitiamo atan2/sin/cos: le implementazioni libm di Windows e macOS
    # possono differire di un ULP e rendere instabili gli artefatti JSON.
    # Decimal proietta lo stesso vettore sull'ellisse in modo riproducibile.
    for terminal in standardized:
        raw_x = float(terminal.get("x") or center_x)
        raw_y = float(terminal.get("y") or center_y)
        delta_x = raw_x - center_x
        delta_y = raw_y - center_y
        with localcontext() as context:
            context.prec = 50
            decimal_x = Decimal.from_float(delta_x)
            decimal_y = Decimal.from_float(delta_y)
            distance = (decimal_x * decimal_x + decimal_y * decimal_y).sqrt()
            if distance:
                terminal["x"] = float(
                    Decimal.from_float(center_x)
                    + decimal_x / distance * Decimal.from_float(float(spec["width"]) / 2)
                )
                terminal["y"] = float(
                    Decimal.from_float(center_y)
                    + decimal_y / distance * Decimal.from_float(float(spec["height"]) / 2)
                )
            else:
                terminal["x"] = center_x + float(spec["width"]) / 2
                terminal["y"] = center_y
    return standardized


def align_integrated_circuit_terminals_to_bbox(
    terminals: list[dict[str, Any]],
    bbox: list[float] | None,
) -> list[dict[str, Any]]:
    """Porta i pin IC sul bordo della bbox senza alterarne la quota sul lato."""
    if not bbox:
        return terminals
    left, top, right, bottom = (float(value) for value in bbox)
    aligned = [dict(terminal) for terminal in terminals]
    for terminal in aligned:
        side = str(terminal.get("relative_position") or "").lower()
        if side == "left":
            terminal["x"] = left
        elif side == "right":
            terminal["x"] = right
        elif side == "top":
            terminal["y"] = top
        elif side == "bottom":
            terminal["y"] = bottom
        else:
            x = float(terminal.get("x") or (left + right) / 2)
            y = float(terminal.get("y") or (top + bottom) / 2)
            nearest_side = min(
                (
                    (abs(x - left), "left"),
                    (abs(x - right), "right"),
                    (abs(y - top), "top"),
                    (abs(y - bottom), "bottom"),
                ),
                key=lambda item: item[0],
            )[1]
            if nearest_side == "left":
                terminal["x"] = left
            elif nearest_side == "right":
                terminal["x"] = right
            elif nearest_side == "top":
                terminal["y"] = top
            else:
                terminal["y"] = bottom
    return aligned


def move_component_to_lane(component: dict[str, Any], lane_y: float) -> None:
    """Sposta un componente orizzontale e tutti i suoi terminali sulla corsia indicata."""
    delta_y = lane_y - float(component.get("y") or lane_y)
    component["y"] = lane_y
    for terminal in component.get("terminals") or []:
        terminal["y"] = float(terminal.get("y") or 0) + delta_y
    bbox = component.get("bbox")
    if isinstance(bbox, list) and len(bbox) == 4:
        component["bbox"] = [bbox[0], bbox[1] + delta_y, bbox[2], bbox[3] + delta_y]


def align_horizontal_branches(positioned: dict[str, dict[str, Any]]) -> None:
    """Propaga le quote dei pin connector lungo i rami di bipoli orizzontali."""
    node_lanes: dict[str, float] = {}
    for component in positioned.values():
        if component.get("component_type") != "connector":
            continue
        for terminal in component.get("terminals") or []:
            node_id = str(terminal.get("node_id") or "")
            if node_id and node_id != "0":
                node_lanes[node_id] = float(terminal["y"])

    # Ogni passaggio estende la corsia oltre un componente appena allineato.
    aligned: set[str] = set()
    for _ in range(max(len(positioned), 1)):
        changed = False
        for component_id, component in positioned.items():
            if component_id in aligned or component.get("orientation") != "horizontal":
                continue
            terminals = component.get("terminals") or []
            if len(terminals) != 2:
                continue
            known_lanes = [node_lanes[str(item.get("node_id"))] for item in terminals if str(item.get("node_id")) in node_lanes]
            if not known_lanes:
                continue
            lane_y = sum(known_lanes) / len(known_lanes)
            move_component_to_lane(component, lane_y)
            for terminal in terminals:
                node_id = str(terminal.get("node_id") or "")
                if node_id and node_id != "0":
                    node_lanes.setdefault(node_id, lane_y)
            aligned.add(component_id)
            changed = True
        if not changed:
            break


def connector_terminal_for_node(
    positioned: dict[str, dict[str, Any]], node_id: str
) -> dict[str, Any] | None:
    """Trova il pin di connector associato al nodo, se presente nel layout."""
    for component in positioned.values():
        if component.get("component_type") != "connector":
            continue
        for terminal in component.get("terminals") or []:
            if str(terminal.get("node_id") or "") == node_id:
                return terminal
    return None


def ground_terminals(positioned: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    """Raccoglie i terminali delle masse disponibili come ancore visuali."""
    return [
        terminal
        for component in positioned.values()
        if component.get("component_type") == "ground"
        for terminal in component.get("terminals") or []
        if str(terminal.get("node_id") or "") == "0"
    ]


def positioned_component_nodes(component: dict[str, Any]) -> set[str]:
    """Raccoglie i nodi presenti sui terminali di un componente gia' posizionato."""
    return {
        str(terminal.get("node_id") or "")
        for terminal in component.get("terminals") or []
        if terminal.get("node_id") is not None
    }


def find_parallel_reference(
    positioned: dict[str, dict[str, Any]],
    node_ids: list[str],
    component_type: str,
) -> tuple[str, dict[str, Any]] | None:
    """Trova un bipolo esistente tra gli stessi nodi del componente scenario."""
    target_nodes = set(node_ids)
    if len(target_nodes) != 2:
        return None
    candidates = [
        (component_id, component)
        for component_id, component in positioned.items()
        if component.get("component_type") == component_type
        and len(component.get("terminals") or []) == 2
        and positioned_component_nodes(component) == target_nodes
        and component.get("placement") != "parallel_branch"
    ]
    return min(candidates, key=lambda item: str(item[0])) if candidates else None


def parallel_branch_position(
    reference_id: str,
    reference: dict[str, Any],
    node_ids: list[str],
    positioned: dict[str, dict[str, Any]],
    component_type: str,
    canvas: tuple[float, float],
) -> dict[str, Any]:
    """Posiziona un nuovo bipolo su una corsia parallela libera rispetto al riferimento."""
    orientation = str(reference.get("orientation") or "horizontal")
    reference_x = float(reference.get("x") or 0)
    reference_y = float(reference.get("y") or 0)
    reference_terminals = {
        str(terminal.get("node_id") or ""): terminal
        for terminal in reference.get("terminals") or []
    }
    lane_offset = 78.0
    candidates = (
        [(reference_x, reference_y + lane_offset), (reference_x, reference_y - lane_offset)]
        if orientation == "horizontal"
        else [(reference_x + lane_offset, reference_y), (reference_x - lane_offset, reference_y)]
    )
    spec = component_spec(component_type, component_type, 2)
    obstacles = [component_symbol_bounds(component) for component in positioned.values() if component is not reference]
    canvas_width, canvas_height = canvas
    scored: list[tuple[float, float, float]] = []
    for candidate_x, candidate_y in candidates:
        probe = {
            "x": candidate_x,
            "y": candidate_y,
            "component_type": component_type,
            "orientation": orientation,
            "symbol_size": {"width": spec["width"], "height": spec["height"]},
            "terminals": [],
        }
        bounds = component_symbol_bounds(probe)
        overlap = sum(rectangle_overlap_area(bounds, obstacle) for obstacle in obstacles)
        outside = max(0.0, 24.0 - bounds[0]) + max(0.0, bounds[2] - canvas_width + 24.0)
        outside += max(0.0, 24.0 - bounds[1]) + max(0.0, bounds[3] - canvas_height + 24.0)
        scored.append((overlap * 100_000.0 + outside * 100_000.0, candidate_x, candidate_y))
    _, x, y = min(scored, key=lambda candidate: candidate[0])

    terminals: list[dict[str, Any]] = []
    for index, node_id in enumerate(node_ids, start=1):
        source_terminal = reference_terminals.get(node_id) or {}
        if orientation == "horizontal":
            terminal_x = float(source_terminal.get("x") or reference_x)
            terminal_y = y
            relative_position = str(source_terminal.get("relative_position") or ("left" if index == 1 else "right"))
        else:
            terminal_x = x
            terminal_y = float(source_terminal.get("y") or reference_y)
            relative_position = str(source_terminal.get("relative_position") or ("top" if index == 1 else "bottom"))
        terminals.append(
            {
                "name": f"t{index}",
                "node_id": node_id,
                "relative_position": relative_position,
                "x": terminal_x,
                "y": terminal_y,
            }
        )
    return {
        "x": x,
        "y": y,
        "orientation": orientation,
        "terminals": terminals,
        "placement": "parallel_branch",
        "parallel_reference_id": reference_id,
        "symbol_size": {"width": spec["width"], "height": spec["height"]},
    }


def component_visual_bounds(component: dict[str, Any]) -> tuple[float, float, float, float]:
    """Stima il rettangolo occupato da simbolo e label di un componente."""
    component_type = str(component.get("component_type") or "structural")
    center_x = float(component.get("x") or 0)
    center_y = float(component.get("y") or 0)
    terminals = component.get("terminals") or []
    bbox = component.get("bbox")
    if component_type == "integrated_circuit" and isinstance(bbox, list) and len(bbox) == 4:
        return (
            float(bbox[0]) - 12.0,
            float(bbox[1]) - 12.0,
            float(bbox[2]) + 12.0,
            float(bbox[3]) + 12.0,
        )
    if component_type == "connector" and terminals:
        spec = component_spec("connector", "connector", len(terminals))
        top = min(float(item["y"]) for item in terminals) - 36.0
        bottom = max(float(item["y"]) for item in terminals) + 32.0
        return center_x - spec["width"] / 2 - 12.0, top, center_x + spec["width"] / 2 + 12.0, bottom
    if component_type == "ground" and terminals:
        terminal_x = float(terminals[0].get("x") or center_x)
        terminal_y = float(terminals[0].get("y") or center_y)
        return terminal_x - 32.0, terminal_y - 8.0, terminal_x + 32.0, terminal_y + 40.0

    size = component.get("symbol_size") or component_spec(component_type, component.get("layout_kind"), len(terminals))
    width = float(size.get("width") or 68.0)
    height = float(size.get("height") or 46.0)
    if component.get("orientation") == "vertical":
        width, height = height, width
    left = center_x - width / 2 - 12.0
    right = center_x + width / 2 + 12.0
    top = center_y - height / 2 - 28.0
    bottom = center_y + height / 2 + 12.0
    if component.get("orientation") == "vertical":
        if component.get("label_side") == "left":
            left -= 64.0
        else:
            right += 64.0
    return left, top, right, bottom


def component_symbol_bounds(component: dict[str, Any]) -> tuple[float, float, float, float]:
    """Restituisce l'ingombro del solo simbolo, senza considerare la sua label."""
    component_type = str(component.get("component_type") or "structural")
    center_x = float(component.get("x") or 0)
    center_y = float(component.get("y") or 0)
    terminals = component.get("terminals") or []
    bbox = component.get("bbox")
    if component_type == "integrated_circuit" and isinstance(bbox, list) and len(bbox) == 4:
        return tuple(float(value) for value in bbox)
    if component_type == "connector" and terminals:
        spec = component_spec("connector", "connector", len(terminals))
        top = min(float(item["y"]) for item in terminals) - 20.0
        bottom = max(float(item["y"]) for item in terminals) + 20.0
        return center_x - spec["width"] / 2, top, center_x + spec["width"] / 2, bottom
    if component_type == "ground" and terminals:
        terminal_x = float(terminals[0].get("x") or center_x)
        terminal_y = float(terminals[0].get("y") or center_y)
        return terminal_x - 26.0, terminal_y, terminal_x + 26.0, terminal_y + 30.0

    size = component.get("symbol_size") or component_spec(component_type, component.get("layout_kind"), len(terminals))
    width = float(size.get("width") or 68.0)
    height = float(size.get("height") or 46.0)
    if component.get("orientation") == "vertical":
        width, height = height, width
    return (
        center_x - width / 2,
        center_y - height / 2,
        center_x + width / 2,
        center_y + height / 2,
    )


def translate_component(component: dict[str, Any], delta_x: float, delta_y: float) -> None:
    """Trasla simbolo e terminali insieme, preservando la geometria elettrica interna."""
    component["x"] = float(component.get("x") or 0) + delta_x
    component["y"] = float(component.get("y") or 0) + delta_y
    for terminal in component.get("terminals") or []:
        terminal["x"] = float(terminal.get("x") or 0) + delta_x
        terminal["y"] = float(terminal.get("y") or 0) + delta_y
    bbox = component.get("bbox")
    if isinstance(bbox, list) and len(bbox) == 4:
        component["bbox"] = [
            float(bbox[0]) + delta_x,
            float(bbox[1]) + delta_y,
            float(bbox[2]) + delta_x,
            float(bbox[3]) + delta_y,
        ]


def separate_supply_switch_chain_from_parallel_capacitor(
    positioned: dict[str, dict[str, Any]],
) -> None:
    """Separa una dorsale sorgente-switch da un condensatore posto in parallelo.

    La regola usa esclusivamente i nodi: se sorgente e switch sono in serie e
    i loro due nodi esterni coincidono con quelli di un condensatore, i tre
    elementi descrivono una tipica alimentazione con bypass. La dorsale viene
    spostata sul lato in cui si trova gia', senza cambiare alcun collegamento.
    """
    capacitors = [
        component
        for component in positioned.values()
        if "capacitor" in str(component.get("component_type") or "")
        and len(component.get("terminals") or []) == 2
    ]
    switches = [
        component
        for component in positioned.values()
        if str(component.get("component_type") or "") == "switch"
        and len(component.get("terminals") or []) == 2
    ]
    sources = [
        component
        for component in positioned.values()
        if str(component.get("component_type") or "") in {"battery", "voltage_source", "dc_supply"}
        and len(component.get("terminals") or []) == 2
    ]

    def terminal_nodes(component: dict[str, Any]) -> set[str]:
        return {
            str(terminal.get("node_id") or "")
            for terminal in component.get("terminals") or []
            if str(terminal.get("node_id") or "")
        }

    moved_chains: set[tuple[int, int]] = set()
    minimum_axis_clearance = 72.0
    for switch in switches:
        switch_nodes = terminal_nodes(switch)
        for source in sources:
            source_nodes = terminal_nodes(source)
            common_nodes = switch_nodes & source_nodes
            if len(common_nodes) != 1:
                continue
            common_node = next(iter(common_nodes))
            external_nodes = (switch_nodes | source_nodes) - {common_node}
            if len(external_nodes) != 2:
                continue
            chain_key = tuple(sorted((id(switch), id(source))))
            if chain_key in moved_chains:
                continue
            capacitor = next(
                (item for item in capacitors if terminal_nodes(item) == external_nodes),
                None,
            )
            if capacitor is None:
                continue

            capacitor_x = float(capacitor.get("x") or 0)
            chain_x = [float(switch.get("x") or 0), float(source.get("x") or 0)]
            chain_center_x = sum(chain_x) / len(chain_x)
            if abs(chain_center_x - capacitor_x) >= minimum_axis_clearance:
                continue

            if chain_center_x >= capacitor_x:
                delta_x = capacitor_x + minimum_axis_clearance - min(chain_x)
                right_edge = max(component_symbol_bounds(item)[2] for item in (switch, source))
                delta_x = min(delta_x, VIEWER_CONTENT_WIDTH - 12.0 - right_edge)
            else:
                delta_x = capacitor_x - minimum_axis_clearance - max(chain_x)
                left_edge = min(component_symbol_bounds(item)[0] for item in (switch, source))
                delta_x = max(delta_x, 12.0 - left_edge)

            if abs(delta_x) > 0.01:
                translate_component(switch, delta_x, 0.0)
                translate_component(source, delta_x, 0.0)
                moved_chains.add(chain_key)


def component_spacing_weight(component: dict[str, Any]) -> float:
    """Assegna un peso basso agli elementi che conviene mantenere vicini alla bbox originale."""
    component_type = str(component.get("component_type") or "")
    if component_type in {"ground", "terminal"}:
        return 0.2
    if component_type == "connector":
        return 0.45
    return 1.0


def relax_component_spacing(positioned: dict[str, dict[str, Any]]) -> None:
    """Separa gli ingombri dei simboli mantenendo ordine relativo e orientamento estratti."""
    items = [
        component
        for component in positioned.values()
        if component.get("component_type") not in {"ground", "terminal"}
    ]
    original_centers = {
        id(component): (
            float(component.get("x") or 0),
            float(component.get("y") or 0),
        )
        for component in items
    }
    clearance = 18.0
    for _ in range(14):
        moved = False
        for index, first in enumerate(items):
            for second in items[index + 1 :]:
                first_bounds = component_symbol_bounds(first)
                second_bounds = component_symbol_bounds(second)
                first_expanded = (
                    first_bounds[0] - clearance,
                    first_bounds[1] - clearance,
                    first_bounds[2] + clearance,
                    first_bounds[3] + clearance,
                )
                second_expanded = (
                    second_bounds[0] - clearance,
                    second_bounds[1] - clearance,
                    second_bounds[2] + clearance,
                    second_bounds[3] + clearance,
                )
                overlap_x = min(first_expanded[2], second_expanded[2]) - max(first_expanded[0], second_expanded[0])
                overlap_y = min(first_expanded[3], second_expanded[3]) - max(first_expanded[1], second_expanded[1])
                if overlap_x <= 0 or overlap_y <= 0:
                    continue

                first_weight = component_spacing_weight(first)
                second_weight = component_spacing_weight(second)
                total_weight = max(first_weight + second_weight, 0.1)
                if overlap_x <= overlap_y:
                    # Il verso resta quello della geometria immagine iniziale:
                    # componenti gia' separati non possono scavalcarsi durante
                    # le iterazioni successive del rilassamento.
                    direction = (
                        -1.0
                        if original_centers[id(first)][0] <= original_centers[id(second)][0]
                        else 1.0
                    )
                    first_shift = direction * overlap_x * (second_weight / total_weight) * 0.55
                    second_shift = -direction * overlap_x * (first_weight / total_weight) * 0.55
                    translate_component(first, first_shift, 0.0)
                    translate_component(second, second_shift, 0.0)
                else:
                    direction = (
                        -1.0
                        if original_centers[id(first)][1] <= original_centers[id(second)][1]
                        else 1.0
                    )
                    first_shift = direction * overlap_y * (second_weight / total_weight) * 0.55
                    second_shift = -direction * overlap_y * (first_weight / total_weight) * 0.55
                    translate_component(first, 0.0, first_shift)
                    translate_component(second, 0.0, second_shift)
                moved = True
        if not moved:
            break


def align_external_terminal_ports(positioned: dict[str, dict[str, Any]]) -> None:
    """Porta ogni port esterno fuori dal simbolo direttamente collegato.

    I bipoli del viewer hanno dimensioni standard e possono diventare piu'
    larghi della bbox trasformata. Il rilassamento non deve trascinare i port
    attraverso il circuito: questa passata usa lato e nodo del contatto
    Pipeline 1.0 per riancorarlo appena oltre il componente adiacente.
    """
    terminal_components = [
        component
        for component in positioned.values()
        if component.get("component_type") == "terminal"
        and component.get("terminals")
    ]
    gap = 14.0
    for component in terminal_components:
        terminals = component.get("terminals") or []
        primary_terminal_id = str(component.get("viewer_primary_terminal_id") or "")
        primary = next(
            (
                terminal for terminal in terminals
                if primary_terminal_id
                and str(terminal.get("terminal_id") or "") == primary_terminal_id
            ),
            terminals[0],
        )
        node_id = str(primary.get("node_id") or "")
        if not node_id:
            continue

        candidates: list[tuple[float, dict[str, Any], dict[str, Any]]] = []
        primary_x = float(primary.get("x") or component.get("x") or 0)
        primary_y = float(primary.get("y") or component.get("y") or 0)
        for other in positioned.values():
            if other is component or other.get("component_type") in {"ground", "terminal"}:
                continue
            for other_terminal in other.get("terminals") or []:
                if str(other_terminal.get("node_id") or "") != node_id:
                    continue
                distance = math.hypot(
                    float(other_terminal.get("x") or 0) - primary_x,
                    float(other_terminal.get("y") or 0) - primary_y,
                )
                candidates.append((distance, other, other_terminal))
        if not candidates:
            continue

        _, adjacent, adjacent_terminal = min(candidates, key=lambda item: item[0])
        left, top, right, bottom = component_symbol_bounds(adjacent)
        side = str(primary.get("relative_position") or "").lower()
        if side == "left":
            target_x = right + gap
            target_y = float(adjacent_terminal.get("y") or primary_y)
        elif side == "right":
            target_x = left - gap
            target_y = float(adjacent_terminal.get("y") or primary_y)
        elif side == "top":
            target_x = float(adjacent_terminal.get("x") or primary_x)
            target_y = bottom + gap
        elif side == "bottom":
            target_x = float(adjacent_terminal.get("x") or primary_x)
            target_y = top - gap
        else:
            continue
        translate_component(component, target_x - primary_x, target_y - primary_y)


def realign_parallel_branches(positioned: dict[str, dict[str, Any]]) -> None:
    """Ripristina l'allineamento dei rami paralleli dopo la separazione dagli ostacoli."""
    for component in positioned.values():
        if component.get("placement") != "parallel_branch":
            continue
        reference = positioned.get(str(component.get("parallel_reference_id") or ""))
        if not reference:
            continue
        reference_terminals = {
            str(terminal.get("node_id") or ""): terminal
            for terminal in reference.get("terminals") or []
        }
        if component.get("orientation") == "horizontal":
            translate_component(component, float(reference.get("x") or 0) - float(component.get("x") or 0), 0.0)
            for terminal in component.get("terminals") or []:
                reference_terminal = reference_terminals.get(str(terminal.get("node_id") or ""))
                if reference_terminal:
                    terminal["x"] = float(reference_terminal.get("x") or terminal.get("x") or 0)
        else:
            translate_component(component, 0.0, float(reference.get("y") or 0) - float(component.get("y") or 0))
            for terminal in component.get("terminals") or []:
                reference_terminal = reference_terminals.get(str(terminal.get("node_id") or ""))
                if reference_terminal:
                    terminal["y"] = float(reference_terminal.get("y") or terminal.get("y") or 0)


def realign_connector_bridges(positioned: dict[str, dict[str, Any]]) -> None:
    """Riancora i link tra pin al connector dopo la separazione dei simboli."""
    bridges = [
        component
        for component in positioned.values()
        if component.get("placement") == "connector_bridge"
    ]
    for connector in positioned.values():
        if connector.get("component_type") != "connector":
            continue
        connector_terminals = {
            str(terminal.get("node_id") or ""): terminal
            for terminal in connector.get("terminals") or []
        }
        matching = [
            bridge
            for bridge in bridges
            if all(
                str(terminal.get("node_id") or "") in connector_terminals
                for terminal in bridge.get("terminals") or []
            )
        ]
        matching.sort(key=lambda item: str(item.get("source_component_id") or ""))
        connector_spec = component_spec("connector", "connector", len(connector_terminals))
        for lane_index, bridge in enumerate(matching):
            lane_x = float(connector.get("x") or 0) + connector_spec["width"] / 2 + 12.0 + lane_index * 12.0
            for terminal in bridge.get("terminals") or []:
                connector_terminal = connector_terminals.get(str(terminal.get("node_id") or ""))
                if connector_terminal:
                    terminal["x"] = lane_x
                    terminal["y"] = float(connector_terminal.get("y") or 0)
            terminals = bridge.get("terminals") or []
            bridge["x"] = lane_x
            if terminals:
                bridge["y"] = sum(float(terminal.get("y") or 0) for terminal in terminals) / len(terminals)


def align_near_perpendicular_leads(positioned: dict[str, dict[str, Any]]) -> None:
    """Ripristina gli allineamenti verticali quasi esatti suggeriti dalle bbox."""
    terminals_by_node: dict[str, list[tuple[str, dict[str, Any]]]] = {}
    for component_id, component in positioned.items():
        for terminal in component.get("terminals") or []:
            node_id = str(terminal.get("node_id") or "")
            if node_id and node_id != "0":
                terminals_by_node.setdefault(node_id, []).append((component_id, terminal))

    proposed_x: dict[str, list[float]] = {}
    for terminals in terminals_by_node.values():
        for first_index, (first_id, first) in enumerate(terminals):
            for second_id, second in terminals[first_index + 1 :]:
                first_side = terminal_side(first)
                second_side = terminal_side(second)
                if {first_side, second_side} & {"top", "bottom"} == set():
                    continue
                if {first_side, second_side} & {"left", "right"} == set():
                    continue
                vertical_id, vertical_terminal = (
                    (first_id, first) if first_side in {"top", "bottom"} else (second_id, second)
                )
                horizontal_terminal = second if vertical_terminal is first else first
                if abs(float(vertical_terminal.get("x") or 0) - float(horizontal_terminal.get("x") or 0)) <= 20.0:
                    # L'asse verticale si ferma sulla corsia esterna del terminale
                    # laterale, lasciando un ultimo tratto orizzontale di 22 px.
                    horizontal_direction = terminal_outward_direction(horizontal_terminal) or (0.0, 0.0)
                    target_x = float(horizontal_terminal.get("x") or 0) + horizontal_direction[0] * 22.0
                    proposed_x.setdefault(vertical_id, []).append(target_x)

    for component_id, targets in proposed_x.items():
        if not targets or max(targets) - min(targets) > 6.0:
            continue
        component = positioned.get(component_id)
        if component:
            target_x = sum(targets) / len(targets)
            translate_component(component, target_x - float(component.get("x") or 0), 0.0)


def align_near_series_components(positioned: dict[str, dict[str, Any]]) -> None:
    """Allinea una serie orizzontale quasi rettilinea evitando piccoli gradini."""
    terminals_by_node: dict[str, list[tuple[str, dict[str, Any]]]] = {}
    for component_id, component in positioned.items():
        if component.get("is_structural") or component.get("orientation") != "horizontal":
            continue
        for terminal in component.get("terminals") or []:
            node_id = str(terminal.get("node_id") or "")
            if node_id:
                terminals_by_node.setdefault(node_id, []).append((component_id, terminal))

    proposed_y: dict[str, list[float]] = {}
    for terminals in terminals_by_node.values():
        if len(terminals) != 2:
            continue
        first_id, first = terminals[0]
        second_id, second = terminals[1]
        if {terminal_side(first), terminal_side(second)} != {"left", "right"}:
            continue
        left_id, left_terminal, right_id, right_terminal = (
            (first_id, first, second_id, second)
            if float(first.get("x") or 0) < float(second.get("x") or 0)
            else (second_id, second, first_id, first)
        )
        if terminal_side(left_terminal) != "right" or terminal_side(right_terminal) != "left":
            continue
        if abs(float(left_terminal.get("y") or 0) - float(right_terminal.get("y") or 0)) > 14.0:
            continue
        proposed_y.setdefault(right_id, []).append(float(left_terminal.get("y") or 0))

    for component_id, targets in proposed_y.items():
        if not targets or max(targets) - min(targets) > 6.0:
            continue
        component = positioned.get(component_id)
        if not component:
            continue
        target_y = sum(targets) / len(targets)
        delta_y = target_y - float(component.get("y") or 0)
        current_bounds = component_symbol_bounds(component)
        candidate_bounds = (
            current_bounds[0],
            current_bounds[1] + delta_y,
            current_bounds[2],
            current_bounds[3] + delta_y,
        )
        overlaps_symbol = any(
            other_id != component_id
            and rectangle_overlap_area(candidate_bounds, component_symbol_bounds(other)) > 1.0
            for other_id, other in positioned.items()
        )
        if not overlaps_symbol:
            translate_component(component, 0.0, delta_y)


def align_direct_battery_connector_links(positioned: dict[str, dict[str, Any]]) -> None:
    """Allinea il polo di una batteria al pin quando il nodo li collega direttamente."""
    terminals_by_node: dict[str, list[tuple[str, dict[str, Any]]]] = {}
    for component_id, component in positioned.items():
        for terminal in component.get("terminals") or []:
            node_id = str(terminal.get("node_id") or "")
            if node_id and node_id != "0":
                terminals_by_node.setdefault(node_id, []).append((component_id, terminal))

    for terminals in terminals_by_node.values():
        if len(terminals) != 2:
            continue
        first_id, first_terminal = terminals[0]
        second_id, second_terminal = terminals[1]
        first_component = positioned.get(first_id) or {}
        second_component = positioned.get(second_id) or {}
        if {str(first_component.get("component_type") or ""), str(second_component.get("component_type") or "")} != {
            "battery",
            "connector",
        }:
            continue
        battery_id, battery_terminal, connector_terminal = (
            (first_id, first_terminal, second_terminal)
            if first_component.get("component_type") == "battery"
            else (second_id, second_terminal, first_terminal)
        )
        battery = positioned.get(battery_id) or {}
        direction = terminal_outward_direction(battery_terminal)
        if battery.get("orientation") != "vertical" or not direction or direction[1] == 0:
            continue
        target_terminal_y = float(connector_terminal.get("y") or 0) - direction[1] * 22.0
        delta_y = target_terminal_y - float(battery_terminal.get("y") or 0)
        if abs(delta_y) > 70.0:
            continue
        current_bounds = component_symbol_bounds(battery)
        candidate_bounds = (
            current_bounds[0],
            current_bounds[1] + delta_y,
            current_bounds[2],
            current_bounds[3] + delta_y,
        )
        overlaps_symbol = any(
            other_id != battery_id
            and other.get("component_type") not in {"ground", "connector"}
            and rectangle_overlap_area(candidate_bounds, component_symbol_bounds(other)) > 1.0
            for other_id, other in positioned.items()
        )
        if not overlaps_symbol:
            translate_component(battery, 0.0, delta_y)


def align_connector_ground_symbols(positioned: dict[str, dict[str, Any]], model: dict[str, Any]) -> None:
    """Dispone una massa sotto un pin quando i due terminali formano un gruppo diretto."""
    direct_ground_groups = [
        set(str(terminal_id) for terminal_id in group)
        for node in model.get("nodes") or []
        if isinstance(node, dict) and str(node.get("id") or "") == "0"
        for group in node.get("source_groups") or []
        if isinstance(group, list) and len(group) == 2
    ]
    connector_terminals = [
        terminal
        for component in positioned.values()
        if component.get("component_type") == "connector"
        for terminal in component.get("terminals") or []
    ]
    ground_terminals = [
        (component, (component.get("terminals") or [{}])[0])
        for component in positioned.values()
        if component.get("component_type") == "ground" and component.get("terminals")
    ]
    for connector_terminal in connector_terminals:
        connector_id = str(connector_terminal.get("terminal_id") or "")
        for ground, ground_terminal in ground_terminals:
            ground_id = str(ground_terminal.get("terminal_id") or "")
            if not any({connector_id, ground_id} == group for group in direct_ground_groups):
                continue
            target_x = float(connector_terminal.get("x") or 0)
            target_y = float(connector_terminal.get("y") or 0) + 56.0
            candidate_bounds = (target_x - 22.0, target_y, target_x + 22.0, target_y + 30.0)
            overlaps_symbol = any(
                other is not ground
                and other.get("component_type") != "ground"
                and rectangle_overlap_area(candidate_bounds, component_symbol_bounds(other)) > 1.0
                for other in positioned.values()
            )
            if overlaps_symbol:
                continue
            ground_terminal["x"] = target_x
            ground_terminal["y"] = target_y
            ground["x"] = target_x
            ground["y"] = target_y + 15.0


def align_direct_vertical_ground_symbols(positioned: dict[str, dict[str, Any]], model: dict[str, Any]) -> None:
    """Centra una massa sul componente quando il Graph JSON ne dichiara il ritorno diretto."""
    direct_ground_groups = [
        set(str(terminal_id) for terminal_id in group)
        for node in model.get("nodes") or []
        if isinstance(node, dict) and str(node.get("id") or "") == "0"
        for group in node.get("source_groups") or []
        if isinstance(group, list) and len(group) == 2
    ]
    ground_terminals = [
        (component, (component.get("terminals") or [{}])[0])
        for component in positioned.values()
        if component.get("component_type") == "ground" and component.get("terminals")
    ]

    for component in positioned.values():
        if component.get("component_type") in {"ground", "connector"}:
            continue
        for terminal in component.get("terminals") or []:
            direction = terminal_outward_direction(terminal)
            if not direction or direction[0] != 0:
                continue
            terminal_id = str(terminal.get("terminal_id") or "")
            terminal_x = float(terminal.get("x") or 0)
            terminal_y = float(terminal.get("y") or 0)
            for ground, ground_terminal in ground_terminals:
                ground_id = str(ground_terminal.get("terminal_id") or "")
                if not any({terminal_id, ground_id} == group for group in direct_ground_groups):
                    continue
                ground_y = float(ground_terminal.get("y") or 0)
                # La massa deve restare davanti al terminale, non essere trascinata oltre il simbolo.
                if direction[1] * (ground_y - terminal_y) <= 0:
                    continue
                delta_x = terminal_x - float(ground.get("x") or 0)
                current_bounds = component_symbol_bounds(ground)
                candidate_bounds = (
                    current_bounds[0] + delta_x,
                    current_bounds[1],
                    current_bounds[2] + delta_x,
                    current_bounds[3],
                )
                overlaps_symbol = any(
                    other is not ground
                    and other.get("component_type") != "ground"
                    and rectangle_overlap_area(candidate_bounds, component_symbol_bounds(other)) > 1.0
                    for other in positioned.values()
                )
                if overlaps_symbol:
                    continue
                ground_terminal["x"] = terminal_x
                ground["x"] = terminal_x


def rectangle_overlap_area(
    first: tuple[float, float, float, float], second: tuple[float, float, float, float]
) -> float:
    """Calcola l'area comune tra due rettangoli del layout."""
    overlap_x = max(0.0, min(first[2], second[2]) - max(first[0], second[0]))
    overlap_y = max(0.0, min(first[3], second[3]) - max(first[1], second[1]))
    return overlap_x * overlap_y


def point_in_rectangle(point: tuple[float, float], rectangle: tuple[float, float, float, float]) -> bool:
    """Verifica se un punto appartiene al rettangolo indicato."""
    return rectangle[0] <= point[0] <= rectangle[2] and rectangle[1] <= point[1] <= rectangle[3]


def orthogonal_segments(
    start: tuple[float, float], end: tuple[float, float], horizontal_first: bool
) -> list[tuple[tuple[float, float], tuple[float, float]]]:
    """Scompone un collegamento ortogonale nei suoi due segmenti rettilinei."""
    elbow = (end[0], start[1]) if horizontal_first else (start[0], end[1])
    return [(start, elbow), (elbow, end)]


def segment_crosses_rectangle(
    segment: tuple[tuple[float, float], tuple[float, float]],
    rectangle: tuple[float, float, float, float],
) -> bool:
    """Rileva l'attraversamento di un ostacolo da parte di un segmento ortogonale."""
    start, end = segment
    if point_in_rectangle(start, rectangle) or point_in_rectangle(end, rectangle):
        # Gli ostacoli dei due componenti collegati sono gia' esclusi dal
        # chiamante: un estremo dentro qualunque altro simbolo e' quindi una
        # collisione reale, non un contatto elettrico intenzionale.
        return True
    if abs(start[1] - end[1]) < 0.01:
        low_x, high_x = sorted((start[0], end[0]))
        return rectangle[1] <= start[1] <= rectangle[3] and high_x >= rectangle[0] and low_x <= rectangle[2]
    low_y, high_y = sorted((start[1], end[1]))
    return rectangle[0] <= start[0] <= rectangle[2] and high_y >= rectangle[1] and low_y <= rectangle[3]


def segments_cross(
    first: tuple[tuple[float, float], tuple[float, float]],
    second: tuple[tuple[float, float], tuple[float, float]],
) -> bool:
    """Rileva un incrocio interno tra due segmenti ortogonali."""
    first_horizontal = abs(first[0][1] - first[1][1]) < 0.01
    second_horizontal = abs(second[0][1] - second[1][1]) < 0.01
    if first_horizontal == second_horizontal:
        return False
    horizontal, vertical = (first, second) if first_horizontal else (second, first)
    horizontal_x = sorted((horizontal[0][0], horizontal[1][0]))
    vertical_y = sorted((vertical[0][1], vertical[1][1]))
    crossing = (vertical[0][0], horizontal[0][1])
    if crossing in first or crossing in second:
        return False
    return horizontal_x[0] < crossing[0] < horizontal_x[1] and vertical_y[0] < crossing[1] < vertical_y[1]


def existing_wire_segments(
    positioned: dict[str, dict[str, Any]],
    node_centers: dict[str, tuple[float, float]],
) -> list[tuple[tuple[float, float], tuple[float, float]]]:
    """Stima i fili gia' presenti collegando i terminali ai centri dei nodi."""
    segments: list[tuple[tuple[float, float], tuple[float, float]]] = []
    for component in positioned.values():
        for terminal in component.get("terminals") or []:
            node_id = str(terminal.get("node_id") or "")
            if not node_id or node_id == "0" or node_id not in node_centers:
                continue
            start = (float(terminal["x"]), float(terminal["y"]))
            segments.extend(orthogonal_segments(start, node_centers[node_id], True))
    return [segment for segment in segments if segment[0] != segment[1]]


def source_candidate_score(
    source: dict[str, Any],
    routes: list[tuple[tuple[float, float], tuple[float, float]]],
    obstacles: list[tuple[float, float, float, float]],
    current_wires: list[tuple[tuple[float, float], tuple[float, float]]],
    canvas: tuple[float, float],
    preferred_side: float,
    anchor_x: float,
) -> float:
    """Assegna un costo alla candidata privilegiando spazio libero e fili corti."""
    bounds = component_visual_bounds(source)
    width, height = canvas
    score = 0.0
    if bounds[0] < 24.0 or bounds[1] < 24.0 or bounds[2] > width - 24.0 or bounds[3] > height - 24.0:
        score += 2_000_000.0
    for obstacle in obstacles:
        overlap = rectangle_overlap_area(bounds, obstacle)
        if overlap > 0:
            score += 500_000.0 + overlap * 250.0
        score += sum(30_000.0 for segment in routes if segment_crosses_rectangle(segment, obstacle))
    score += sum(4_000.0 for route in routes for wire in current_wires if segments_cross(route, wire))
    score += sum(
        abs(segment[1][0] - segment[0][0]) + abs(segment[1][1] - segment[0][1])
        for segment in routes
    )
    if (float(source["x"]) - anchor_x) * preferred_side < 0:
        score += 180.0
    return score


def scenario_source_candidates(
    anchor: tuple[float, float], preferred_side: float, aligned_center_y: float
) -> list[tuple[float, float]]:
    """Genera una griglia compatta di posizioni candidate attorno al nodo alimentato."""
    anchor_x, _ = anchor
    horizontal_offsets = [preferred_side * value for value in (100.0, 150.0, 210.0, 270.0, 330.0)]
    horizontal_offsets.extend([-preferred_side * value for value in (110.0, 170.0, 230.0)])
    horizontal_offsets.append(0.0)
    vertical_offsets = (-140.0, -70.0, 0.0, 70.0, 140.0)
    return [
        (round(anchor_x + offset_x, 2), round(aligned_center_y + offset_y, 2))
        for offset_x in horizontal_offsets
        for offset_y in vertical_offsets
    ]


def scenario_voltage_source_position(
    component: dict[str, Any],
    positioned: dict[str, dict[str, Any]],
    node_centers: dict[str, tuple[float, float]],
    canvas: tuple[float, float],
) -> dict[str, Any] | None:
    """Sceglie una zona libera per una sorgente scenario collegata tra nodo e massa."""
    nodes = [str(node_id) for node_id in component.get("nodes") or []]
    if len(nodes) != 2 or "0" not in nodes:
        return None
    non_ground_node = next((node_id for node_id in nodes if node_id != "0"), "")
    node_center = node_centers.get(non_ground_node)
    if not non_ground_node or not node_center:
        return None

    connector_terminal = connector_terminal_for_node(positioned, non_ground_node)
    anchor_x, anchor_y = (
        (float(connector_terminal["x"]), float(connector_terminal["y"]))
        if connector_terminal
        else node_center
    )
    available_grounds = ground_terminals(positioned)
    if not available_grounds:
        return None

    # Il lato opposto al pin e' solo una preferenza: il punteggio puo' scegliere altro.
    relative_position = str((connector_terminal or {}).get("relative_position") or "").lower()
    if relative_position == "right":
        preferred_side = -1.0
    elif relative_position == "left":
        preferred_side = 1.0
    else:
        preferred_side = -1.0

    obstacles = [component_visual_bounds(item) for item in positioned.values()]
    obstacles.append(legend_obstacle_bounds())
    current_wires = existing_wire_segments(positioned, node_centers)
    component_type = "signal_source" if is_variable_voltage_source(component) else "scenario_voltage_source"
    spec = component_spec(component_type, component_type, 2)
    half_length = spec["width"] / 2
    normal_is_positive = nodes[0] != "0"
    aligned_center_y = anchor_y + half_length if normal_is_positive else anchor_y - half_length
    best: dict[str, Any] | None = None
    for candidate_x, candidate_y in scenario_source_candidates(
        (anchor_x, anchor_y), preferred_side, aligned_center_y
    ):
        label_side = "left" if candidate_x < anchor_x else "right"
        top = (candidate_x, candidate_y - half_length)
        bottom = (candidate_x, candidate_y + half_length)
        for ground in available_grounds:
            ground_point = (float(ground["x"]), float(ground["y"]))
            positive_target = (anchor_x, anchor_y) if nodes[0] != "0" else ground_point
            negative_target = ground_point if nodes[1] == "0" else (anchor_x, anchor_y)
            direct_cost = abs(top[0] - positive_target[0]) + abs(top[1] - positive_target[1])
            direct_cost += abs(bottom[0] - negative_target[0]) + abs(bottom[1] - negative_target[1])
            inverse_cost = abs(bottom[0] - positive_target[0]) + abs(bottom[1] - positive_target[1])
            inverse_cost += abs(top[0] - negative_target[0]) + abs(top[1] - negative_target[1])
            positive_point, negative_point = (top, bottom) if direct_cost <= inverse_cost else (bottom, top)
            routes = orthogonal_segments(positive_target, positive_point, True)
            routes.extend(orthogonal_segments(negative_point, negative_target, False))
            source = {
                "x": candidate_x,
                "y": candidate_y,
                "component_type": component_type,
                "layout_kind": component_type,
                "symbol_size": spec,
                "orientation": "vertical",
                "label_side": label_side,
            }
            score = source_candidate_score(
                source,
                routes,
                obstacles,
                current_wires,
                canvas,
                preferred_side,
                anchor_x,
            )
            normal_terminal = positive_point if normal_is_positive else negative_point
            # L'allineamento evita che il filo sembri entrare nel fianco della batteria.
            score += abs(normal_terminal[1] - anchor_y) * 120.0
            candidate = {
                **source,
                "terminals": [
                    {"name": "positive", "node_id": nodes[0], "x": positive_point[0], "y": positive_point[1]},
                    {"name": "negative", "node_id": nodes[1], "x": negative_point[0], "y": negative_point[1]},
                ],
                "placement": "scenario_supply_scored",
                "placement_score": round(score, 2),
            }
            if best is None or score < float(best["placement_score"]):
                best = candidate
    return best


def build_image_guided_components(
    components: list[dict[str, Any]],
    geometry_seed: dict[str, Any],
    transform: dict[str, float],
) -> tuple[dict[str, dict[str, Any]], list[str]]:
    """Posiziona i componenti usando bbox e terminali della Pipeline 1.0."""
    geometry_components = geometry_seed.get("components") or {}
    positioned: dict[str, dict[str, Any]] = {}
    warnings: list[str] = []
    pending: list[dict[str, Any]] = []

    for component in components:
        component_id = str(component.get("id") or "")
        source_id = visual_source_id(component)
        geometry_component = geometry_components.get(source_id)
        if not geometry_component:
            geometry_component = anchored_geometry_component(component, geometry_components)
        if not component_id:
            continue
        if not geometry_component:
            pending.append(component)
            continue
        center = geometry_component.get("center") or {}
        position = transform_point(center.get("x"), center.get("y"), transform)
        orientation = normalize_orientation(geometry_component.get("estimated_orientation"))
        visual_class_name = str(
            component.get("viewer_kind")
            or geometry_component.get("class_name")
            or component.get("layout_kind")
            or "structural"
        )
        component_type = normalize_component_type(visual_class_name, component.get("layout_kind"))
        raw_terminals = match_geometry_terminals(component, geometry_component, transform)
        bbox = (
            transform_bbox(geometry_component.get("bbox"), transform)
            if component_type == "integrated_circuit"
            else None
        )
        # Un port esterno puo avere contatti su lati diversi (per esempio
        # segnale e ritorno a massa di un jack). Le coordinate Pipeline 1.0
        # sono gia' i suoi punti elettrici reali: appiattirle come un normale
        # bipolo crea fili fittizi e puo scegliere il contatto sbagliato.
        terminals = (
            [dict(terminal) for terminal in raw_terminals]
            if component_type == "terminal"
            else standardize_terminals(raw_terminals, position, component_type, orientation)
        )
        if component_type == "integrated_circuit":
            terminals = align_integrated_circuit_terminals_to_bbox(terminals, bbox)
        spec = component_spec(component_type, component.get("layout_kind"), len(terminals))
        symbol_size = (
            {"width": bbox[2] - bbox[0], "height": bbox[3] - bbox[1]}
            if bbox
            else {"width": spec["width"], "height": spec["height"]}
        )
        positioned[component_id] = {
            **position,
            "source_component_id": source_id,
            "layout_kind": component.get("layout_kind"),
            "visual_class_name": visual_class_name,
            "component_type": component_type,
            "symbol_size": symbol_size,
            "bbox": bbox,
            "label": component.get("label"),
            "orientation": orientation,
            "terminals": terminals,
            "viewer_primary_terminal_id": component.get("viewer_primary_terminal_id"),
            "state": (component.get("parameters") or {}).get("state") or geometry_component.get("state"),
            "is_structural": bool(component.get("is_structural")),
        }

    align_horizontal_branches(positioned)

    # I terminali gia' posizionati permettono di stimare il centro visuale di ogni nodo.
    node_seed_points: dict[str, list[tuple[float, float]]] = {}
    for positioned_component in positioned.values():
        for terminal in positioned_component.get("terminals") or []:
            node_id = str(terminal.get("node_id") or "")
            if node_id:
                node_seed_points.setdefault(node_id, []).append((float(terminal["x"]), float(terminal["y"])))
    node_centers = {
        node_id: (
            sum(point[0] for point in points) / len(points),
            sum(point[1] for point in points) / len(points),
        )
        for node_id, points in node_seed_points.items()
        if points
    }

    # I componenti aggiunti dagli scenari non hanno bbox: vengono inseriti tra i nodi coinvolti.
    for index, component in enumerate(pending):
        component_id = str(component.get("id") or "")
        component_node_ids = [str(node_id) for node_id in component.get("nodes") or []]
        component_type = (
            str(component.get("layout_kind"))
            if component.get("layout_kind") in {"scenario_voltage_source", "signal_source"}
            else normalize_component_type(
                component.get("viewer_kind") or component.get("class_name") or component.get("kind"),
                component.get("layout_kind"),
            )
        )
        first_point = node_centers.get(component_node_ids[0]) if component_node_ids else None
        second_point = node_centers.get(component_node_ids[1]) if len(component_node_ids) > 1 else None
        terminals: list[dict[str, Any]] = []
        connector_bridge: dict[str, Any] | None = None
        parallel_reference = (
            find_parallel_reference(positioned, component_node_ids, component_type)
            if component.get("is_scenario_added") and component_type not in {"connection", "scenario_voltage_source", "signal_source"}
            else None
        )
        parallel_branch = (
            parallel_branch_position(
                parallel_reference[0],
                parallel_reference[1],
                component_node_ids,
                positioned,
                component_type,
                (float(transform["canvas_width"]), float(transform["canvas_height"])),
            )
            if parallel_reference
            else None
        )
        scenario_source = (
            scenario_voltage_source_position(
                component,
                positioned,
                node_centers,
                (float(transform["canvas_width"]), float(transform["canvas_height"])),
            )
            if component_type in {"scenario_voltage_source", "signal_source"}
            else None
        )
        orientation = "horizontal"
        placement = "scenario_or_fallback"
        if scenario_source:
            x = float(scenario_source["x"])
            y = float(scenario_source["y"])
            terminals = scenario_source["terminals"]
            orientation = str(scenario_source["orientation"])
            placement = str(scenario_source["placement"])
            label_side = str(scenario_source["label_side"])
            placement_score = float(scenario_source["placement_score"])
        elif component_type == "connection" and len(component_node_ids) == 2:
            for positioned_component in positioned.values():
                if positioned_component.get("component_type") != "connector":
                    continue
                connector_terminals = {
                    str(terminal.get("node_id") or ""): terminal
                    for terminal in positioned_component.get("terminals") or []
                }
                if all(node_id in connector_terminals for node_id in component_node_ids):
                    connector_bridge = {
                        "component": positioned_component,
                        "terminals": connector_terminals,
                    }
                    break

        if scenario_source:
            # La batteria scenario ha gia' terminali e posizione coerenti con il connector.
            pass
        elif connector_bridge:
            # Un link tra pin dello stesso connector resta compatto e aderente al suo bordo.
            connector = connector_bridge["component"]
            connector_spec = component_spec("connector", "connector", len(connector.get("terminals") or []))
            x = float(connector.get("x") or 0) + connector_spec["width"] / 2 + 12.0
            first_y = float(connector_bridge["terminals"][component_node_ids[0]]["y"])
            second_y = float(connector_bridge["terminals"][component_node_ids[1]]["y"])
            y = (first_y + second_y) / 2
            terminals = [
                {"name": "t1", "node_id": component_node_ids[0], "x": x, "y": first_y},
                {"name": "t2", "node_id": component_node_ids[1], "x": x, "y": second_y},
            ]
            orientation = "vertical"
            placement = "connector_bridge"
        elif parallel_branch:
            # Un bipolo sugli stessi nodi eredita la geometria del ramo originale.
            x = float(parallel_branch["x"])
            y = float(parallel_branch["y"])
            terminals = list(parallel_branch["terminals"])
            orientation = str(parallel_branch["orientation"])
            placement = str(parallel_branch["placement"])
        elif first_point and second_point:
            dx = second_point[0] - first_point[0]
            dy = second_point[1] - first_point[1]
            distance = max((dx * dx + dy * dy) ** 0.5, 1.0)
            normal_x, normal_y = -dy / distance, dx / distance
            offset = 34.0 + (index % 3) * 22.0
            x = (first_point[0] + second_point[0]) / 2 + normal_x * offset
            y = (first_point[1] + second_point[1]) / 2 + normal_y * offset
            direction_x, direction_y = dx / distance, dy / distance
            terminals = [
                {"name": "t1", "node_id": component_node_ids[0], "x": x - direction_x * 34, "y": y - direction_y * 34},
                {"name": "t2", "node_id": component_node_ids[1], "x": x + direction_x * 34, "y": y + direction_y * 34},
            ]
        else:
            x = 520.0 + (index % 3 - 1) * 120.0
            y = 310.0 + (index // 3) * 70.0
        positioned[component_id] = {
            "x": x,
            "y": y,
            "source_component_id": visual_source_id(component),
            "layout_kind": component.get("layout_kind"),
            "visual_class_name": component.get("class_name") or component.get("kind"),
            "component_type": component_type,
            "symbol_size": parallel_branch.get("symbol_size") if parallel_branch else None,
            "label": component.get("label"),
            "orientation": orientation,
            "label_side": label_side if scenario_source else None,
            "terminals": terminals,
            "state": (component.get("parameters") or {}).get("state"),
            "is_structural": bool(component.get("is_structural")),
            "placement": placement,
            "parallel_reference_id": parallel_branch.get("parallel_reference_id") if parallel_branch else None,
            "placement_score": placement_score if scenario_source else None,
        }
        warnings.append(f"Geometria assente per {component_id}: applicato posizionamento tra nodi.")
    # Le bbox definiscono la topologia; questa passata aggiunge lo spazio necessario ai simboli reali.
    relax_component_spacing(positioned)
    realign_parallel_branches(positioned)
    align_external_terminal_ports(positioned)
    return positioned, warnings


def collect_node_points(positioned: dict[str, dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    """Raggruppa per nodo tutti i terminali geometrici disponibili."""
    node_points: dict[str, list[dict[str, Any]]] = {}
    for component_id, component in positioned.items():
        for terminal in component.get("terminals") or []:
            node_id = str(terminal.get("node_id") or "")
            if not node_id:
                continue
            node_points.setdefault(node_id, []).append(
                {
                    "component_id": component_id,
                    "terminal": terminal.get("name"),
                    "terminal_id": terminal.get("terminal_id"),
                    "relative_position": terminal.get("relative_position"),
                    "x": terminal.get("x"),
                    "y": terminal.get("y"),
                    "is_structural": component.get("is_structural"),
                    "component_type": component.get("component_type"),
                    "orientation": component.get("orientation"),
                    "placement": component.get("placement"),
                    "parallel_reference_id": component.get("parallel_reference_id"),
                }
            )
    return node_points


def build_node_positions(model: dict[str, Any], node_points: dict[str, list[dict[str, Any]]]) -> dict[str, dict[str, Any]]:
    """Calcola il punto di giunzione visuale di ogni nodo dalla media dei terminali."""
    positions: dict[str, dict[str, Any]] = {}
    for node in model.get("nodes") or []:
        if not isinstance(node, dict):
            continue
        node_id = str(node.get("id") or "")
        points = node_points.get(node_id) or []
        if not points:
            continue
        positions[node_id] = {
            "x": round(sum(float(point["x"]) for point in points) / len(points), 2),
            "y": round(sum(float(point["y"]) for point in points) / len(points), 2),
            "terminal_count": len(points),
        }
    return positions


def compact_constraint_value(value: Any) -> str:
    """Formatta il valore del vincolo lasciando leggibili anche forme SPICE complesse."""
    text = str(value or "").strip()
    match = re.fullmatch(r"([+-]?(?:\d+(?:\.\d*)?|\.\d+))\s*([A-Za-z]+)", text)
    return f"{match.group(1)} {match.group(2)}" if match else text


def build_node_constraints(
    model: dict[str, Any],
    node_positions: dict[str, dict[str, Any]],
    component_positions: dict[str, dict[str, Any]],
) -> list[dict[str, Any]]:
    """Posiziona i vincoli diagnostici vicino ai nodi senza creare componenti fittizi."""
    obstacles = [component_visual_bounds(component) for component in component_positions.values()]
    obstacles.append(legend_obstacle_bounds())
    constraints: list[dict[str, Any]] = []
    badge_width, badge_height = 104.0, 28.0
    candidate_offsets = ((72.0, -38.0), (-72.0, -38.0), (72.0, 38.0), (-72.0, 38.0), (0.0, -58.0), (0.0, 58.0))

    for component in model.get("netlist_components") or []:
        if not isinstance(component, dict) or component.get("viewer_kind") != "node_voltage_clamp":
            continue
        node_id = str(component.get("viewer_target_node") or "")
        node_position = node_positions.get(node_id)
        if not node_position:
            continue
        node_x = float(node_position["x"])
        node_y = float(node_position["y"])
        candidates: list[tuple[float, float, float, tuple[float, float, float, float]]] = []
        for offset_x, offset_y in candidate_offsets:
            label_x = node_x + offset_x
            label_y = node_y + offset_y
            bounds = (
                label_x - badge_width / 2,
                label_y - badge_height / 2,
                label_x + badge_width / 2,
                label_y + badge_height / 2,
            )
            overlap = sum(rectangle_overlap_area(bounds, obstacle) for obstacle in obstacles)
            outside = max(0.0, 12.0 - bounds[0]) + max(0.0, bounds[2] - 1028.0)
            outside += max(0.0, 12.0 - bounds[1]) + max(0.0, bounds[3] - 608.0)
            score = overlap * 100.0 + outside * 10_000.0 + abs(offset_x) + abs(offset_y)
            candidates.append((score, label_x, label_y, bounds))
        _, label_x, label_y, selected_bounds = min(candidates, key=lambda candidate: candidate[0])
        obstacles.append(selected_bounds)
        constraints.append(
            {
                "source_component_id": str(component.get("id") or ""),
                "node_id": node_id,
                "value": compact_constraint_value(component.get("viewer_forced_value") or component.get("value")),
                "x": round(node_x, 2),
                "y": round(node_y, 2),
                "label_x": round(label_x, 2),
                "label_y": round(label_y, 2),
            }
        )
    return constraints


def connect_point_group(node_id: str, points: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Collega i terminali dello stesso nodo con un albero rettilineo minimo."""
    if len(points) < 2:
        return []

    connections: list[dict[str, Any]] = []
    parallel_points = [point for point in points if point.get("placement") == "parallel_branch"]
    base_points = [point for point in points if point.get("placement") != "parallel_branch"]
    for parallel_point in parallel_points:
        reference_id = str(parallel_point.get("parallel_reference_id") or "")
        reference_point = next(
            (point for point in base_points if str(point.get("component_id") or "") == reference_id),
            None,
        )
        if not reference_point:
            base_points.append(parallel_point)
            continue
        connections.append(
            {
                "node_id": node_id,
                "from": reference_point,
                "to": parallel_point,
                "kind": "electrical",
                "placement": "parallel_branch_link",
            }
        )

    if len(base_points) < 2:
        return connections

    # Prim sulla distanza Manhattan evita le lunghe stelle generate da un unico
    # terminale e si accorda con i percorsi ortogonali usati dal renderer.
    # Quando il nodo ha altri terminali disponibili, il ramo di un condensatore
    # non parte direttamente da una sorgente: la stessa topologia resta intatta,
    # ma il filo non affianca inutilmente il simbolo circolare della sorgente.
    source_types = {"current_source", "voltage_source", "signal_source", "dc_supply", "battery"}

    def source_capacitor_branch_penalty(first: dict[str, Any], second: dict[str, Any]) -> float:
        if len(base_points) <= 2:
            return 0.0
        first_type = str(first.get("component_type") or "").lower()
        second_type = str(second.get("component_type") or "").lower()
        is_source_capacitor_pair = (
            first_type in source_types and "capacitor" in second_type
        ) or (
            second_type in source_types and "capacitor" in first_type
        )
        return 140.0 if is_source_capacitor_pair else 0.0

    connected = [base_points[0]]
    remaining = list(base_points[1:])
    while remaining:
        source, target = min(
            (
                (source_point, target_point)
                for source_point in connected
                for target_point in remaining
            ),
            key=lambda pair: (
                abs(float(pair[0]["x"]) - float(pair[1]["x"]))
                + abs(float(pair[0]["y"]) - float(pair[1]["y"]))
                + source_capacitor_branch_penalty(pair[0], pair[1]),
                str(pair[0].get("component_id") or ""),
                str(pair[1].get("component_id") or ""),
            ),
        )
        distance = abs(float(source["x"]) - float(target["x"])) + abs(
            float(source["y"]) - float(target["y"])
        )
        if distance > 0.5:
            connections.append(
                {
                    "node_id": node_id,
                    "from": source,
                    "to": target,
                    "kind": (
                        "structural"
                        if source.get("is_structural") and target.get("is_structural")
                        else "electrical"
                    ),
                }
            )
        connected.append(target)
        remaining.remove(target)
    return connections


def build_node_connections(
    node_points: dict[str, list[dict[str, Any]]],
    model: dict[str, Any],
) -> list[dict[str, Any]]:
    """Crea collegamenti terminale-terminale per ciascun nodo elettrico."""
    connections: list[dict[str, Any]] = []
    source_groups_by_node = {
        str(node.get("id") or ""): node.get("source_groups") or []
        for node in model.get("nodes") or []
        if isinstance(node, dict)
    }
    for node_id, points in node_points.items():
        source_groups = source_groups_by_node.get(node_id) or []
        if node_id != "0" or not source_groups:
            connections.extend(connect_point_group(node_id, points))
            continue

        # Le masse SPICE coincidono elettricamente, ma restano gruppi grafici separati.
        points_by_terminal = {str(point.get("terminal_id") or ""): point for point in points}
        grouped_terminal_ids: set[str] = set()
        for source_group in source_groups:
            group_points = [points_by_terminal[terminal_id] for terminal_id in source_group if terminal_id in points_by_terminal]
            grouped_terminal_ids.update(str(terminal_id) for terminal_id in source_group)
            connections.extend(connect_point_group(node_id, group_points))

        # Terminali scenario non presenti nella base vengono collegati alla massa visuale piu' vicina.
        ground_points = [point for point in points if str(point.get("component_id") or "").lower().startswith("gnd")]
        for point in points:
            if str(point.get("terminal_id") or "") in grouped_terminal_ids or not ground_points:
                continue
            nearest_ground = min(
                ground_points,
                key=lambda ground: (float(ground["x"]) - float(point["x"])) ** 2 + (float(ground["y"]) - float(point["y"])) ** 2,
            )
            if nearest_ground is not point:
                connections.extend(connect_point_group(node_id, [point, nearest_ground]))
    return connections


def compact_route_points(points: list[tuple[float, float]]) -> list[tuple[float, float]]:
    """Elimina punti duplicati e tratti consecutivi perfettamente allineati."""
    compact: list[tuple[float, float]] = []
    for point in points:
        if compact and abs(compact[-1][0] - point[0]) < 0.01 and abs(compact[-1][1] - point[1]) < 0.01:
            continue
        compact.append(point)
    changed = True
    while changed and len(compact) >= 3:
        changed = False
        simplified = [compact[0]]
        for index in range(1, len(compact) - 1):
            previous = simplified[-1]
            current = compact[index]
            following = compact[index + 1]
            same_x = (
                abs(previous[0] - current[0]) < 0.01
                and abs(current[0] - following[0]) < 0.01
                and min(previous[1], following[1]) <= current[1] <= max(previous[1], following[1])
            )
            same_y = (
                abs(previous[1] - current[1]) < 0.01
                and abs(current[1] - following[1]) < 0.01
                and min(previous[0], following[0]) <= current[0] <= max(previous[0], following[0])
            )
            if same_x or same_y:
                changed = True
                continue
            simplified.append(current)
        simplified.append(compact[-1])
        compact = simplified
    return compact


def route_segments(points: list[tuple[float, float]]) -> list[tuple[tuple[float, float], tuple[float, float]]]:
    """Trasforma una lista di punti ortogonali nei segmenti che la compongono."""
    return [(first, second) for first, second in zip(points, points[1:]) if first != second]


def parallel_segments_too_close(
    first: tuple[tuple[float, float], tuple[float, float]],
    second: tuple[tuple[float, float], tuple[float, float]],
    clearance: float = 9.0,
) -> bool:
    """Rileva tratti paralleli di nodi diversi che sembrerebbero un unico filo."""
    (first_start, first_end), (second_start, second_end) = first, second
    first_horizontal = abs(first_start[1] - first_end[1]) < 0.01
    second_horizontal = abs(second_start[1] - second_end[1]) < 0.01
    first_vertical = abs(first_start[0] - first_end[0]) < 0.01
    second_vertical = abs(second_start[0] - second_end[0]) < 0.01

    if first_horizontal and second_horizontal:
        overlap = min(max(first_start[0], first_end[0]), max(second_start[0], second_end[0])) - max(
            min(first_start[0], first_end[0]), min(second_start[0], second_end[0])
        )
        return overlap > 5.0 and abs(first_start[1] - second_start[1]) < clearance
    if first_vertical and second_vertical:
        overlap = min(max(first_start[1], first_end[1]), max(second_start[1], second_end[1])) - max(
            min(first_start[1], first_end[1]), min(second_start[1], second_end[1])
        )
        return overlap > 5.0 and abs(first_start[0] - second_start[0]) < clearance
    return False


def route_score(
    points: list[tuple[float, float]],
    obstacles: list[tuple[float, float, float, float]],
    node_id: str = "",
    occupied_segments: list[
        tuple[str, tuple[tuple[float, float], tuple[float, float]]]
    ] | None = None,
) -> float:
    """Valuta un percorso evitando simboli e ambiguita con fili di altri nodi."""
    segments = route_segments(points)
    length = sum(abs(end[0] - start[0]) + abs(end[1] - start[1]) for start, end in segments)
    crossings = sum(
        1
        for segment in segments
        for obstacle in obstacles
        if segment_crosses_rectangle(segment, obstacle)
    )
    bends = max(len(segments) - 1, 0)
    foreign_segments = [
        segment
        for occupied_node_id, segment in occupied_segments or []
        if occupied_node_id != node_id
    ]
    parallel_conflicts = sum(
        1
        for segment in segments
        for occupied in foreign_segments
        if parallel_segments_too_close(segment, occupied)
    )
    wire_crossings = sum(
        1
        for segment in segments
        for occupied in foreign_segments
        if segments_cross(segment, occupied)
    )
    return (
        crossings * 1_000_000.0
        + parallel_conflicts * 250_000.0
        + wire_crossings * 18_000.0
        + bends * 34.0
        + length
    )


def terminal_outward_direction(terminal: dict[str, Any]) -> tuple[float, float] | None:
    """Restituisce la direzione esterna naturale del terminale sul simbolo disegnato."""
    side = str(terminal.get("relative_position") or "").lower()
    directions = {
        "top": (0.0, -1.0),
        "bottom": (0.0, 1.0),
        "left": (-1.0, 0.0),
        "right": (1.0, 0.0),
    }
    return directions.get(side)


def terminal_side(terminal: dict[str, Any]) -> str:
    """Normalizza il lato del terminale per scegliere una corsia di uscita coerente."""
    side = str(terminal.get("relative_position") or "").lower()
    return side if side in {"top", "bottom", "left", "right"} else ""


def terminals_face_each_other(
    start_point: tuple[float, float],
    end_point: tuple[float, float],
    start_direction: tuple[float, float] | None,
    end_direction: tuple[float, float] | None,
) -> bool:
    """Verifica se due terminali allineati possono essere collegati da una retta naturale."""
    if not start_direction or not end_direction:
        return False
    delta_x = end_point[0] - start_point[0]
    delta_y = end_point[1] - start_point[1]
    aligned = abs(delta_x) < 0.01 or abs(delta_y) < 0.01
    if not aligned:
        return False
    start_points_to_end = start_direction[0] * delta_x + start_direction[1] * delta_y > 0
    end_points_to_start = end_direction[0] * -delta_x + end_direction[1] * -delta_y > 0
    return start_points_to_end and end_points_to_start


def near_axis_facing_route(
    start_point: tuple[float, float],
    end_point: tuple[float, float],
    start_direction: tuple[float, float] | None,
    end_direction: tuple[float, float] | None,
) -> list[tuple[float, float]] | None:
    """Collega direttamente terminali contrapposti quasi allineati dalle bbox."""
    if not start_direction or not end_direction:
        return None
    delta_x = end_point[0] - start_point[0]
    delta_y = end_point[1] - start_point[1]
    start_points_to_end = start_direction[0] * delta_x + start_direction[1] * delta_y > 0
    end_points_to_start = end_direction[0] * -delta_x + end_direction[1] * -delta_y > 0
    if not (start_points_to_end and end_points_to_start):
        return None
    # Le bbox estratte dall'immagine possono differire di pochi pixel pur rappresentando una verticale unica.
    if start_direction[0] == 0 and end_direction[0] == 0 and abs(delta_x) <= 8.0:
        return [start_point, (start_point[0], end_point[1]), end_point]
    if start_direction[1] == 0 and end_direction[1] == 0 and abs(delta_y) <= 8.0:
        return [start_point, (end_point[0], start_point[1]), end_point]
    return None


def terminal_escape_point(
    point: tuple[float, float], direction: tuple[float, float] | None
) -> tuple[float, float]:
    """Crea un breve tratto esterno al simbolo per mantenere leggibile l'ingresso del filo."""
    if not direction:
        return point
    lead_length = 22.0
    return point[0] + direction[0] * lead_length, point[1] + direction[1] * lead_length


def route_respects_terminal_directions(
    points: list[tuple[float, float]],
    start_direction: tuple[float, float] | None,
    end_direction: tuple[float, float] | None,
) -> bool:
    """Esclude percorsi che tornano subito dentro un terminale dopo esserne usciti."""
    segments = route_segments(points)
    if len(segments) >= 2 and start_direction:
        first_escape = (
            segments[0][1][0] - segments[0][0][0],
            segments[0][1][1] - segments[0][0][1],
        )
        following = (
            segments[1][1][0] - segments[1][0][0],
            segments[1][1][1] - segments[1][0][1],
        )
        if first_escape[0] * start_direction[0] + first_escape[1] * start_direction[1] > 0:
            if following[0] * start_direction[0] + following[1] * start_direction[1] < 0:
                return False
    if len(segments) >= 2 and end_direction:
        last_approach = (
            segments[-1][1][0] - segments[-1][0][0],
            segments[-1][1][1] - segments[-1][0][1],
        )
        previous = (
            segments[-2][1][0] - segments[-2][0][0],
            segments[-2][1][1] - segments[-2][0][1],
        )
        if last_approach[0] * end_direction[0] + last_approach[1] * end_direction[1] < 0:
            if previous[0] * end_direction[0] + previous[1] * end_direction[1] > 0:
                return False
    return True


def route_connection(
    connection: dict[str, Any],
    positioned: dict[str, dict[str, Any]],
    occupied_segments: list[
        tuple[str, tuple[tuple[float, float], tuple[float, float]]]
    ] | None = None,
) -> list[dict[str, float]]:
    """Trova un percorso ortogonale corto tra due terminali, evitando gli altri simboli."""
    start = connection.get("from") or {}
    end = connection.get("to") or {}
    start_point = (float(start.get("x") or 0), float(start.get("y") or 0))
    end_point = (float(end.get("x") or 0), float(end.get("y") or 0))
    start_direction = terminal_outward_direction(start)
    end_direction = terminal_outward_direction(end)
    start_side = terminal_side(start)
    end_side = terminal_side(end)
    start_escape = terminal_escape_point(start_point, start_direction)
    end_escape = terminal_escape_point(end_point, end_direction)
    endpoint_ids = {str(start.get("component_id") or ""), str(end.get("component_id") or "")}
    obstacles = [
        component_symbol_bounds(component)
        for component_id, component in positioned.items()
        if component_id not in endpoint_ids and component.get("component_type") not in {"ground", "terminal"}
    ]
    candidates: list[list[tuple[float, float]]] = []
    start_component = positioned.get(str(start.get("component_id") or "")) or {}
    end_component = positioned.get(str(end.get("component_id") or "")) or {}
    connector_bridge_pair = (
        {str(start_component.get("component_type") or ""), str(end_component.get("component_type") or "")}
        == {"connector", "connection"}
        and "connector_bridge" in {str(start_component.get("placement") or ""), str(end_component.get("placement") or "")}
        and abs(start_point[1] - end_point[1]) < 0.01
    )
    connector_ground_pair = (
        {str(start_component.get("component_type") or ""), str(end_component.get("component_type") or "")}
        == {"connector", "ground"}
        and abs(start_point[0] - end_point[0]) < 0.01
    )
    near_facing_route = near_axis_facing_route(start_point, end_point, start_direction, end_direction)
    if connector_ground_pair:
        # Una massa centrata sotto un pin usa una verticale pulita, senza corsie laterali.
        candidates.append([start_point, end_point])
    elif connector_bridge_pair:
        # I pin e la dorsale adiacente sono gia' allineati: nessuna corsia di fuga.
        candidates.append([start_point, end_point])
    elif terminals_face_each_other(start_point, end_point, start_direction, end_direction):
        candidates.append([start_point, end_point])
    elif near_facing_route:
        candidates.append(near_facing_route)
    elif start_side and start_side == end_side and start_side in {"top", "bottom"}:
        lane_y = min(start_point[1], end_point[1]) - 22.0 if start_side == "top" else max(start_point[1], end_point[1]) + 22.0
        candidates.append([start_point, (start_point[0], lane_y), (end_point[0], lane_y), end_point])
    elif start_side and start_side == end_side and start_side in {"left", "right"}:
        lane_x = min(start_point[0], end_point[0]) - 22.0 if start_side == "left" else max(start_point[0], end_point[0]) + 22.0
        candidates.append([start_point, (lane_x, start_point[1]), (lane_x, end_point[1]), end_point])
    elif abs(start_escape[0] - end_escape[0]) < 0.01 or abs(start_escape[1] - end_escape[1]) < 0.01:
        candidates.append([start_point, start_escape, end_escape, end_point])
    candidates.extend(
        [
            [start_point, start_escape, (end_escape[0], start_escape[1]), end_escape, end_point],
            [start_point, start_escape, (start_escape[0], end_escape[1]), end_escape, end_point],
        ]
    )

    # Piccole corsie parallele permettono di separare fili di nodi diversi
    # senza costringere il percorso a una deviazione ampia attorno al circuito.
    local_clearance = 12.0
    for lane_y in (
        min(start_escape[1], end_escape[1]) - local_clearance,
        max(start_escape[1], end_escape[1]) + local_clearance,
    ):
        candidates.append(
            [
                start_point,
                start_escape,
                (start_escape[0], lane_y),
                (end_escape[0], lane_y),
                end_escape,
                end_point,
            ]
        )
    for lane_x in (
        min(start_escape[0], end_escape[0]) - local_clearance,
        max(start_escape[0], end_escape[0]) + local_clearance,
    ):
        candidates.append(
            [
                start_point,
                start_escape,
                (lane_x, start_escape[1]),
                (lane_x, end_escape[1]),
                end_escape,
                end_point,
            ]
        )

    # Le corsie esterne sono un fallback: vengono usate solo se le due soluzioni a una piega incontrano un simbolo.
    padding = 24.0
    for obstacle in obstacles:
        candidates.extend(
            [
                [start_point, start_escape, (start_escape[0], obstacle[1] - padding), (end_escape[0], obstacle[1] - padding), end_escape, end_point],
                [start_point, start_escape, (start_escape[0], obstacle[3] + padding), (end_escape[0], obstacle[3] + padding), end_escape, end_point],
                [start_point, start_escape, (obstacle[0] - padding, start_escape[1]), (obstacle[0] - padding, end_escape[1]), end_escape, end_point],
                [start_point, start_escape, (obstacle[2] + padding, start_escape[1]), (obstacle[2] + padding, end_escape[1]), end_escape, end_point],
            ]
        )
    compact_candidates = [compact_route_points(candidate) for candidate in candidates]
    valid_candidates = [
        candidate
        for candidate in compact_candidates
        if route_respects_terminal_directions(candidate, start_direction, end_direction)
    ]
    if valid_candidates:
        compact_candidates = valid_candidates
    node_id = str(connection.get("node_id") or "")
    selected = min(
        compact_candidates,
        key=lambda candidate: route_score(candidate, obstacles, node_id, occupied_segments),
    )
    return [{"x": round(point[0], 2), "y": round(point[1], 2)} for point in selected]


def route_layout_connections(
    connections: list[dict[str, Any]],
    positioned: dict[str, dict[str, Any]],
) -> list[dict[str, Any]]:
    """Aggiunge a ogni collegamento il percorso preferito che il renderer deve seguire."""
    occupied_segments: list[
        tuple[str, tuple[tuple[float, float], tuple[float, float]]]
    ] = []
    for connection in connections:
        connection["route"] = route_connection(connection, positioned, occupied_segments)
        route_points = [
            (float(point["x"]), float(point["y"]))
            for point in connection.get("route") or []
            if isinstance(point, dict) and "x" in point and "y" in point
        ]
        node_id = str(connection.get("node_id") or "")
        occupied_segments.extend((node_id, segment) for segment in route_segments(route_points))

    # Se due nodi differenti devono comunque incrociarsi, il collegamento
    # disegnato per ultimo riceve un piccolo ponte visuale. Gli incroci dello
    # stesso nodo restano invece normali giunzioni elettriche.
    for current_index, connection in enumerate(connections):
        current_node = str(connection.get("node_id") or "")
        current_points = [
            (float(point["x"]), float(point["y"]))
            for point in connection.get("route") or []
            if isinstance(point, dict) and "x" in point and "y" in point
        ]
        bridges: list[dict[str, Any]] = []
        for segment_index, current_segment in enumerate(route_segments(current_points)):
            current_horizontal = abs(current_segment[0][1] - current_segment[1][1]) < 0.01
            for previous in connections[:current_index]:
                if str(previous.get("node_id") or "") == current_node:
                    continue
                previous_points = [
                    (float(point["x"]), float(point["y"]))
                    for point in previous.get("route") or []
                    if isinstance(point, dict) and "x" in point and "y" in point
                ]
                for previous_segment in route_segments(previous_points):
                    if not segments_cross(current_segment, previous_segment):
                        continue
                    previous_horizontal = abs(previous_segment[0][1] - previous_segment[1][1]) < 0.01
                    horizontal = current_segment if current_horizontal else previous_segment
                    vertical = previous_segment if current_horizontal else current_segment
                    bridges.append(
                        {
                            "segment_index": segment_index,
                            "x": round(vertical[0][0], 2),
                            "y": round(horizontal[0][1], 2),
                            "orientation": "horizontal" if current_horizontal else "vertical",
                        }
                    )
        if bridges:
            connection["wire_bridges"] = bridges
    return connections


def relocate_overlapping_ground_symbols(
    positioned: dict[str, dict[str, Any]],
    model: dict[str, Any],
) -> None:
    """Sposta una massa fuori da un simbolo quando le bbox la collocano al suo interno."""
    ground_groups = [
        set(str(terminal_id) for terminal_id in group)
        for node in model.get("nodes") or []
        if isinstance(node, dict) and str(node.get("id") or "") == "0"
        for group in node.get("source_groups") or []
        if isinstance(group, list)
    ]

    for ground in positioned.values():
        if ground.get("component_type") != "ground":
            continue
        terminal = (ground.get("terminals") or [{}])[0]
        terminal_id = str(terminal.get("terminal_id") or "")
        terminal_x = float(terminal.get("x") or ground.get("x") or 0)
        terminal_y = float(terminal.get("y") or ground.get("y") or 0)
        group = next((item for item in ground_groups if terminal_id in item), set())

        for component_id, component in positioned.items():
            if component is ground or component.get("component_type") == "ground":
                continue
            bounds = component_symbol_bounds(component)
            ground_bounds = component_symbol_bounds(ground)
            if rectangle_overlap_area(ground_bounds, bounds) <= 1.0:
                continue
            contacts = [
                candidate
                for candidate in component.get("terminals") or []
                if str(candidate.get("terminal_id") or "") in group
            ]
            if not contacts:
                continue
            contact = min(
                contacts,
                key=lambda candidate: (float(candidate.get("x") or 0) - terminal_x) ** 2
                + (float(candidate.get("y") or 0) - terminal_y) ** 2,
            )
            side = str(contact.get("relative_position") or "bottom").lower()
            contact_x = float(contact.get("x") or 0)
            contact_y = float(contact.get("y") or 0)
            symbol_gap = 4.0
            if side == "top":
                terminal_x, terminal_y = contact_x, bounds[1] - symbol_gap
            elif side == "left":
                terminal_x, terminal_y = bounds[0] - symbol_gap, contact_y
            elif side == "right":
                terminal_x, terminal_y = bounds[2] + symbol_gap, contact_y
            else:
                terminal_x, terminal_y = contact_x, bounds[3] + symbol_gap

            terminal["x"] = terminal_x
            terminal["y"] = terminal_y
            spec = component_spec("ground", "ground", 1)
            ground["x"] = terminal_x
            ground["y"] = terminal_y + float(spec["height"]) / 2
            break


def separate_ground_symbol_collisions(
    positioned: dict[str, dict[str, Any]],
) -> None:
    """Scosta lateralmente le masse che coprono simboli o altre masse.

    Il collegamento viene instradato dopo questa passata, quindi una piccola
    traslazione orizzontale produce un gomito leggibile senza cambiare il nodo
    elettrico o allungare il ramo attraverso il componente che lo blocca.
    """
    non_ground_obstacles = [
        component_symbol_bounds(component)
        for component in positioned.values()
        if component.get("component_type") != "ground"
    ]
    placed_ground_bounds: list[tuple[float, float, float, float]] = []
    grounds = sorted(
        (
            component
            for component in positioned.values()
            if component.get("component_type") == "ground"
        ),
        key=lambda component: str(component.get("source_component_id") or ""),
    )
    clearance = 8.0
    canvas_margin = 12.0

    for ground in grounds:
        obstacles = non_ground_obstacles + placed_ground_bounds
        for _ in range(4):
            current = component_symbol_bounds(ground)
            blockers = [
                obstacle
                for obstacle in obstacles
                if rectangle_overlap_area(current, obstacle) > 1.0
            ]
            if not blockers:
                break

            candidates: list[tuple[float, float, float]] = []
            for blocker in blockers:
                # Le soluzioni laterali conservano il simbolo sotto il proprio
                # ramo; quelle verticali sono soltanto fallback ai bordi.
                candidates.extend(
                    [
                        (0.0, blocker[0] - clearance - current[2], 0.0),
                        (0.0, blocker[2] + clearance - current[0], 0.0),
                        (1.0, 0.0, blocker[3] + clearance - current[1]),
                        (2.0, 0.0, blocker[1] - clearance - current[3]),
                    ]
                )

            scored: list[tuple[float, float, float]] = []
            for axis_penalty, delta_x, delta_y in candidates:
                candidate = (
                    current[0] + delta_x,
                    current[1] + delta_y,
                    current[2] + delta_x,
                    current[3] + delta_y,
                )
                if (
                    candidate[0] < canvas_margin
                    or candidate[1] < canvas_margin
                    or candidate[2] > VIEWER_CONTENT_WIDTH - canvas_margin
                    or candidate[3] > VIEWER_CANVAS_HEIGHT - canvas_margin
                ):
                    continue
                if any(rectangle_overlap_area(candidate, obstacle) > 1.0 for obstacle in obstacles):
                    continue
                score = axis_penalty * 10_000.0 + abs(delta_x) + abs(delta_y)
                scored.append((score, delta_x, delta_y))
            if not scored:
                break
            _, delta_x, delta_y = min(scored, key=lambda candidate: candidate[0])
            translate_component(ground, delta_x, delta_y)
        placed_ground_bounds.append(component_symbol_bounds(ground))


def build_viewer_layout(run_dir: Path) -> dict[str, Any]:
    """Costruisce il layout visuale a partire da `13_viewer_model.json`."""
    run_dir = run_dir.resolve()
    model = read_json(run_dir / VIEWER_MODEL_NAME)
    components = collect_layout_components(model)
    geometry_seed = model.get("geometry_seed") or {}
    transform = canvas_transform(geometry_seed)
    component_positions, warnings = build_image_guided_components(components, geometry_seed, transform)
    relocate_overlapping_ground_symbols(component_positions, model)
    align_near_perpendicular_leads(component_positions)
    align_near_series_components(component_positions)
    align_direct_battery_connector_links(component_positions)
    separate_supply_switch_chain_from_parallel_capacitor(component_positions)
    realign_connector_bridges(component_positions)
    align_connector_ground_symbols(component_positions, model)
    align_direct_vertical_ground_symbols(component_positions, model)
    separate_ground_symbol_collisions(component_positions)
    node_points = collect_node_points(component_positions)
    node_positions = build_node_positions(model, node_points)
    connections = route_layout_connections(build_node_connections(node_points, model), component_positions)
    layout_status = "image_guided" if geometry_seed.get("status") == "loaded" else "fallback"
    return {
        "source_format": "pipeline2.0_viewer_layout",
        "schema_version": VIEWER_LAYOUT_SCHEMA_VERSION,
        "metadata": {
            "run_dir": str(run_dir),
            "source_model_path": str(run_dir / VIEWER_MODEL_NAME),
            "generated_at": datetime.now().isoformat(timespec="seconds"),
        },
        "layout_status": layout_status,
        "canvas": {
            "width": int(VIEWER_CANVAS_WIDTH),
            "height": int(VIEWER_CANVAS_HEIGHT),
            "grid": 40,
            "content_width": round(VIEWER_CONTENT_WIDTH, 2),
            "legend": {"x": round(VIEWER_LEGEND_LEFT, 2), "y": 24},
        },
        "transform": transform,
        "components": component_positions,
        "nodes": node_positions,
        "node_constraints": build_node_constraints(model, node_positions, component_positions),
        "connections": connections,
        "warnings": warnings if model else [f"Viewer model mancante: {run_dir / VIEWER_MODEL_NAME}"],
    }


def write_viewer_layout(run_dir: Path) -> dict[str, Any]:
    """Genera e salva `14_viewer_layout.json` nella cartella della run."""
    layout = build_viewer_layout(run_dir)
    write_json(run_dir / VIEWER_LAYOUT_NAME, layout)
    return layout

