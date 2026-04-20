from pathlib import Path
import os
import json
import cv2
import numpy as np

"""
05_build_terminal_graph.py

Scopo:
    Costruire il JSON canonico del circuito a partire dallo skeleton dei fili.

Idea:
    - il passo 03 stima i terminali dei componenti
    - il passo 04 estrae i fili e salva lo skeleton
    - questo passo 05 aggancia ogni terminale al filo più vicino
      e poi collega tra loro i terminali che cadono sullo stesso filo

Output principale:
    Un solo JSON per immagine, pensato per essere letto da un'AI.
    Il JSON contiene solo le informazioni utili alla comprensione del circuito:

    - image_id
    - image_name
    - components -> lista dei componenti con terminali semantici minimali
    - graph      -> collegamenti terminale -> terminali collegati
    - warnings   -> piccole segnalazioni utili (terminali isolati / unmatched / suspicious)

Nota importante:
    Internamente usiamo ancora le connected components dello skeleton,
    ma NON salviamo net / net_id / net_index come output finale.
    Le connected components servono solo come mezzo tecnico per costruire
    il grafo finale tra terminali.

Nota sul debug:
    Le immagini di debug vengono comunque salvate su disco, ma i loro path
    NON vengono scritti nel JSON finale.
"""

# =========================================================
# PATHS / INPUT-OUTPUT
# =========================================================
PROJECT_ROOT = Path(__file__).resolve().parents[2]
PIPELINE_DATASET = os.environ.get("PIPELINE_DATASET", "pipeline2.0/batch_v6_operational_amplifier")

INPUT_DIR = PROJECT_ROOT / "outputs" / PIPELINE_DATASET / "04_extract_wires"
OUTPUT_DIR = PROJECT_ROOT / "outputs" / PIPELINE_DATASET / "05_build_terminal_graph"

# Cartelle per le immagini di debug.
DEBUG_TERMINAL_OVERLAY_DIR = OUTPUT_DIR / "debug_terminal_overlay"
DEBUG_SKELETON_OVERLAY_DIR = OUTPUT_DIR / "debug_skeleton_overlay"

# =========================================================
# MATCH TERMINALE -> FILO
# =========================================================
# Finestra di ricerca principale, coerente con il lato del terminale.
TERMINAL_SEARCH_OUTWARD = 16
TERMINAL_SEARCH_INWARD = 4
TERMINAL_DIRECTIONAL_HALFSPAN = 5

# Fallback semplice: se la finestra direzionale non trova nulla,
# cerchiamo in un piccolo quadrato attorno al terminale.
TERMINAL_SQUARE_FALLBACK_RADIUS = 12

# Se il pixel etichettato trovato è troppo lontano dal terminale,
# lo marchiamo come sospetto nel debug.
MAX_REASONABLE_SNAP_DISTANCE = 24.0

# =========================================================
# DEBUG VISIVO
# =========================================================
SAVE_DEBUG_IMAGES = True
TEXT_FONT_SCALE = 0.42
TEXT_THICKNESS = 1
TEXT_OUTLINE_THICKNESS = 3
TERMINAL_RADIUS = 4
SNAP_RADIUS = 3

MATCHED_TERMINAL_COLOR = (0, 180, 0)      # verde
UNMATCHED_TERMINAL_COLOR = (0, 0, 255)    # rosso
SUSPICIOUS_TERMINAL_COLOR = (0, 165, 255) # arancione
SNAP_POINT_COLOR = (255, 0, 0)            # blu
LINK_COLOR = (255, 0, 255)                # magenta
TEXT_COLOR = (255, 255, 0)                # giallo
TEXT_OUTLINE_COLOR = (0, 0, 0)            # nero


# =========================================================
# UTILITY BASE
# =========================================================
# Carica una immagine binaria da disco.
def load_binary_image(path: Path) -> np.ndarray:
    img = cv2.imread(str(path), cv2.IMREAD_GRAYSCALE)
    if img is None:
        raise FileNotFoundError(f"Immagine non trovata o non leggibile: {path}")

    # Normalizziamo a 0/255 per evitare ambiguità.
    return np.where(img > 0, 255, 0).astype(np.uint8)


# Clamp di una finestra dentro i limiti immagine.
def clamp_window(x1, y1, x2, y2, w, h):
    return (
        max(0, min(w, int(round(x1)))),
        max(0, min(h, int(round(y1)))),
        max(0, min(w, int(round(x2)))),
        max(0, min(h, int(round(y2)))),
    )


# Disegna testo con contorno, utile per rendere leggibili le etichette.
def draw_outlined_text(
    image,
    text,
    origin,
    color=TEXT_COLOR,
    outline_color=TEXT_OUTLINE_COLOR,
    font_scale=TEXT_FONT_SCALE,
    thickness=TEXT_THICKNESS,
    outline_thickness=TEXT_OUTLINE_THICKNESS,
):
    cv2.putText(
        image,
        text,
        origin,
        cv2.FONT_HERSHEY_SIMPLEX,
        font_scale,
        outline_color,
        outline_thickness,
        cv2.LINE_AA,
    )
    cv2.putText(
        image,
        text,
        origin,
        cv2.FONT_HERSHEY_SIMPLEX,
        font_scale,
        color,
        thickness,
        cv2.LINE_AA,
    )


# Normalizza il nome classe per usarlo in una chiave semplice.
def normalize_class_name(class_name: str) -> str:
    class_name = str(class_name or "component").strip().lower()
    class_name = class_name.replace(" ", "_")
    return class_name


# Costruisce un id di componente leggibile, ad esempio:
#   Mosfet + 16.2 -> mosfet16.2
def make_simple_component_id(instance_id: str, class_name: str) -> str:
    return f"{normalize_class_name(class_name)}{instance_id}"


# Normalizza un id pubblico per usarlo come chiave semplice.
# Esempio:
#   16.2:G -> 16.2_G
# Manteniamo le MAIUSCOLE del terminale per non perdere G/S/D, B/C/E.
def normalize_public_terminal_id(value: str) -> str:
    value = str(value or "").strip()
    value = value.replace(":", "_")
    value = value.replace(" ", "")
    return value


# Restituisce l'id pubblico migliore del terminale, riusando quanto creato nel 03.
def get_preferred_terminal_public_id(term: dict) -> str:
    return (
        term.get("display_terminal_id")
        or term.get("semantic_terminal_id")
        or term.get("terminal_id")
        or f"{term.get('instance_id', 'unknown')}:{term.get('name', 't')}"
    )


# Restituisce il nome corto migliore del terminale, riusando quanto creato nel 03.
def get_preferred_terminal_public_name(term: dict) -> str:
    return (
        term.get("display_name")
        or term.get("semantic_terminal_name")
        or term.get("name")
        or "t"
    )


# Costruisce la chiave umana semplice del terminale.
# Esempi:
#   display_terminal_id = 16.2:G        -> mosfet16.2_G
#   display_terminal_id = 2.1:positive -> battery2.1_positive
#   display_terminal_id assente         -> resistor22.1_t1
def make_simple_terminal_key(term: dict) -> str:
    class_name = normalize_class_name(term.get("component_class_name"))
    public_terminal_id = normalize_public_terminal_id(
        get_preferred_terminal_public_id(term)
    )
    return f"{class_name}{public_terminal_id}"


# =========================================================
# GEOMETRIA DI RICERCA ATTORNO AL TERMINALE
# =========================================================
# Costruisce una finestra direzionale coerente con il lato del terminale.
def get_directional_window(term: dict, labels_shape, outward=16, inward=4, halfspan=5):
    h, w = labels_shape[:2]
    x = int(round(term["x"]))
    y = int(round(term["y"]))
    rel = term.get("relative_position")

    if rel == "left":
        return clamp_window(x - outward, y - halfspan, x + inward + 1, y + halfspan + 1, w, h)
    if rel == "right":
        return clamp_window(x - inward, y - halfspan, x + outward + 1, y + halfspan + 1, w, h)
    if rel == "top":
        return clamp_window(x - halfspan, y - outward, x + halfspan + 1, y + inward + 1, w, h)
    if rel == "bottom":
        return clamp_window(x - halfspan, y - inward, x + halfspan + 1, y + outward + 1, w, h)

    # Fallback molto semplice: se manca relative_position,
    # usiamo una finestra quadrata centrata sul terminale.
    return clamp_window(x - outward, y - outward, x + outward + 1, y + outward + 1, w, h)


# Finestra quadrata di fallback.
def get_square_window(term: dict, labels_shape, radius=12):
    h, w = labels_shape[:2]
    x = int(round(term["x"]))
    y = int(round(term["y"]))
    return clamp_window(x - radius, y - radius, x + radius + 1, y + radius + 1, w, h)


# =========================================================
# LETTURA DELLE LABEL NELLA FINESTRA
# =========================================================
# Restituisce tutte le label positive (quindi esclude lo sfondo = 0)
# trovate dentro una finestra.
def collect_labels_in_window(labels: np.ndarray, window):
    x1, y1, x2, y2 = window
    roi = labels[y1:y2, x1:x2]
    unique_labels = np.unique(roi)
    return [int(v) for v in unique_labels if int(v) > 0]


# Trova il pixel etichettato più vicino al terminale dentro una finestra.
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


# =========================================================
# MATCH DI UN SINGOLO TERMINALE
# =========================================================
# Versione volutamente semplice:
# 1. prova finestra direzionale
# 2. se non trova nulla, prova finestra quadrata
# 3. se ancora nulla, terminale unmatched

def match_terminal_to_skeleton_label(labels: np.ndarray, term: dict):
    # Primo tentativo: finestra direzionale
    dir_window = get_directional_window(
        term,
        labels.shape,
        outward=TERMINAL_SEARCH_OUTWARD,
        inward=TERMINAL_SEARCH_INWARD,
        halfspan=TERMINAL_DIRECTIONAL_HALFSPAN,
    )
    dir_labels = collect_labels_in_window(labels, dir_window)
    nearest = find_nearest_labeled_pixel(labels, term, dir_window)

    if nearest is not None:
        return {
            "terminal_id": term["terminal_id"],
            "candidate_labels": dir_labels,
            "matched_label": int(nearest["label"]),
            "match_mode": "directional",
            "search_window": [int(v) for v in dir_window],
            "snap_point": nearest["snap_point"],
            "snap_distance": nearest["snap_distance"],
            "is_suspicious": float(nearest["snap_distance"]) > float(MAX_REASONABLE_SNAP_DISTANCE),
        }

    # Secondo tentativo: piccolo quadrato attorno al terminale
    sq_window = get_square_window(term, labels.shape, radius=TERMINAL_SQUARE_FALLBACK_RADIUS)
    sq_labels = collect_labels_in_window(labels, sq_window)
    nearest = find_nearest_labeled_pixel(labels, term, sq_window)

    if nearest is not None:
        return {
            "terminal_id": term["terminal_id"],
            "candidate_labels": sq_labels,
            "matched_label": int(nearest["label"]),
            "match_mode": "square_fallback",
            "search_window": [int(v) for v in sq_window],
            "snap_point": nearest["snap_point"],
            "snap_distance": nearest["snap_distance"],
            "is_suspicious": float(nearest["snap_distance"]) > float(MAX_REASONABLE_SNAP_DISTANCE),
        }

    # Nessun match trovato.
    return {
        "terminal_id": term["terminal_id"],
        "candidate_labels": [],
        "matched_label": None,
        "match_mode": "unmatched",
        "search_window": None,
        "snap_point": None,
        "snap_distance": None,
        "is_suspicious": True,
    }


# =========================================================
# COSTRUZIONE DEI GRUPPI INTERNI DI FILO
# =========================================================
# Trasforma il debug terminale -> label in una struttura:
#   label -> [terminal_id, terminal_id, ...]
# Questa struttura serve solo internamente.
def build_label_to_terminal_ids(match_debug_by_terminal_id: dict):
    label_to_terminal_ids = {}

    for terminal_id, match_info in match_debug_by_terminal_id.items():
        matched_label = match_info.get("matched_label")
        if matched_label is None:
            continue
        label_to_terminal_ids.setdefault(int(matched_label), []).append(terminal_id)

    cleaned = {}
    for label, terminal_ids in label_to_terminal_ids.items():
        cleaned[int(label)] = sorted(set(terminal_ids))

    return cleaned


# =========================================================
# COSTRUZIONE DEL GRAFO FINALE TRA TERMINALI
# =========================================================
# Per ogni gruppo di filo:
# - se il gruppo contiene almeno 2 terminali
# - allora ogni terminale è collegato a tutti gli altri terminali del gruppo

def build_terminal_graph(terminals, label_to_terminal_ids: dict):
    graph = {term["terminal_id"]: [] for term in terminals}

    for _, terminal_ids in label_to_terminal_ids.items():
        unique_ids = sorted(set(terminal_ids))
        if len(unique_ids) < 2:
            continue

        for source_id in unique_ids:
            others = [target_id for target_id in unique_ids if target_id != source_id]
            graph[source_id].extend(others)

    for terminal_id in graph:
        graph[terminal_id] = sorted(set(graph[terminal_id]))

    return graph


# Costruisce la mappa original_id -> simple_id.
def build_simple_id_map(terminals: list[dict]):
    original_to_simple = {}
    for term in terminals:
        original_to_simple[term["terminal_id"]] = make_simple_terminal_key(term)
    return original_to_simple


# Converte il grafo interno in un dizionario semplice e leggibile.
def build_simple_terminal_graph(terminal_graph: dict, original_to_simple: dict):
    public_graph = {}

    for original_source_id, original_target_ids in terminal_graph.items():
        public_source_id = original_to_simple.get(original_source_id, original_source_id)
        public_target_ids = [original_to_simple.get(target_id, target_id) for target_id in original_target_ids]
        public_graph[public_source_id] = sorted(set(public_target_ids))

    public_graph = {key: public_graph[key] for key in sorted(public_graph.keys())}
    return public_graph


# Converte una lista di id interni in una lista di id semplici.
def build_simple_list(values: list[str], original_to_simple: dict):
    return sorted([original_to_simple.get(v, v) for v in values])


# =========================================================
# COSTRUZIONE DEI COMPONENTI CANONICI
# =========================================================
# Produce una vista semplificata dei componenti.
# Nel JSON finale teniamo solo:
# - component_id
# - instance_id
# - class_name
# - terminals con terminal_id, name e relative_position
# NIENTE bbox, coordinate o altri dettagli geometrici.
def build_canonical_components(components: list[dict]):
    canonical_components = []

    for comp in components:
        class_name = comp.get("class_name")
        instance_id = comp.get("instance_id")

        canonical_terminals = []
        for term in comp.get("terminals", []):
            canonical_terminals.append({
                "terminal_id": make_simple_terminal_key(term),
                "name": get_preferred_terminal_public_name(term),
                "relative_position": term.get("relative_position"),
            })

        canonical_components.append({
            "component_id": make_simple_component_id(instance_id, class_name),
            "instance_id": instance_id,
            "class_name": class_name,
            "terminals": canonical_terminals,
        })

    return canonical_components


# =========================================================
# DEBUG VISIVO
# =========================================================
# Sceglie il colore del terminale in base allo stato del match.
def get_terminal_debug_color(match_info: dict):
    if match_info.get("matched_label") is None:
        return UNMATCHED_TERMINAL_COLOR
    if match_info.get("is_suspicious", False):
        return SUSPICIOUS_TERMINAL_COLOR
    return MATCHED_TERMINAL_COLOR


# Disegna overlay sul diagramma originale.
def draw_terminal_overlay(image_bgr, terminals, terminal_match_debug, original_to_simple):
    out = image_bgr.copy()

    for term in terminals:
        terminal_id = term["terminal_id"]
        simple_id = original_to_simple.get(terminal_id, terminal_id)
        info = terminal_match_debug.get(terminal_id, {})

        tx = int(round(term["x"]))
        ty = int(round(term["y"]))
        color = get_terminal_debug_color(info)

        cv2.circle(out, (tx, ty), TERMINAL_RADIUS, color, -1)
        cv2.circle(out, (tx, ty), TERMINAL_RADIUS + 1, (0, 0, 0), 1)

        snap_point = info.get("snap_point")
        if snap_point is not None:
            sx, sy = map(int, snap_point)
            cv2.circle(out, (sx, sy), SNAP_RADIUS, SNAP_POINT_COLOR, -1)
            cv2.circle(out, (sx, sy), SNAP_RADIUS + 1, (255, 255, 255), 1)
            cv2.line(out, (tx, ty), (sx, sy), LINK_COLOR, 1)

        label_text = simple_id
        if info.get("matched_label") is None:
            label_text += " [none]"
        elif info.get("is_suspicious", False):
            label_text += f" [d={info.get('snap_distance')}]"

        draw_outlined_text(out, label_text, (tx + 8, max(16, ty - 6)))

    return out


# Disegna overlay sullo skeleton, utile per capire se il match cade davvero sul filo.
def draw_skeleton_overlay(skeleton_binary, terminals, terminal_match_debug, original_to_simple):
    out = cv2.cvtColor(skeleton_binary, cv2.COLOR_GRAY2BGR)

    for term in terminals:
        terminal_id = term["terminal_id"]
        simple_id = original_to_simple.get(terminal_id, terminal_id)
        info = terminal_match_debug.get(terminal_id, {})

        tx = int(round(term["x"]))
        ty = int(round(term["y"]))
        color = get_terminal_debug_color(info)

        cv2.circle(out, (tx, ty), TERMINAL_RADIUS, color, -1)
        cv2.circle(out, (tx, ty), TERMINAL_RADIUS + 1, (255, 255, 255), 1)

        snap_point = info.get("snap_point")
        if snap_point is not None:
            sx, sy = map(int, snap_point)
            cv2.circle(out, (sx, sy), SNAP_RADIUS, SNAP_POINT_COLOR, -1)
            cv2.circle(out, (sx, sy), SNAP_RADIUS + 1, (255, 255, 255), 1)
            cv2.line(out, (tx, ty), (sx, sy), LINK_COLOR, 1)

        draw_outlined_text(out, simple_id, (tx + 8, max(16, ty - 6)))

    return out


# =========================================================
# MAIN LOGIC PER UNA SINGOLA IMMAGINE
# =========================================================
# Costruisce il grafo dei terminali a partire da:
# - terminals del passo 03
# - skeleton del passo 04

def build_terminal_graph_for_image(data: dict):
    terminals = data.get("terminals", [])
    components = data.get("components", [])
    wire_extraction = data.get("wire_extraction", {})
    skeleton_path = wire_extraction.get("skeleton_path")

    if not skeleton_path:
        raise ValueError("skeleton_path mancante nel JSON del passo 04.")

    skeleton = load_binary_image(Path(skeleton_path))

    # Connected components dello skeleton.
    # Ogni label > 0 rappresenta un tratto di filo connesso.
    _, labels, _, _ = cv2.connectedComponentsWithStats(skeleton, connectivity=8)

    # Match semplice: ogni terminale viene agganciato alla label dello skeleton
    # trovata nella sua zona locale.
    terminal_match_debug = {}
    for term in terminals:
        terminal_match_debug[term["terminal_id"]] = match_terminal_to_skeleton_label(labels, term)

    unmatched_terminals = sorted([
        terminal_id
        for terminal_id, info in terminal_match_debug.items()
        if info.get("matched_label") is None
    ])

    suspicious_matches = sorted([
        terminal_id
        for terminal_id, info in terminal_match_debug.items()
        if info.get("is_suspicious", False) and info.get("matched_label") is not None
    ])

    original_to_simple = build_simple_id_map(terminals)

    # Gruppi di terminali che insistono sullo stesso tratto di filo.
    label_to_terminal_ids = build_label_to_terminal_ids(terminal_match_debug)

    # Grafo finale interno e sua vista canonica leggibile.
    terminal_graph = build_terminal_graph(terminals, label_to_terminal_ids)
    simple_terminal_graph = build_simple_terminal_graph(terminal_graph, original_to_simple)

    # Terminali isolati nel grafo finale.
    unconnected_terminals = sorted([
        terminal_id
        for terminal_id, neighbors in simple_terminal_graph.items()
        if len(neighbors) == 0
    ])

    canonical_components = build_canonical_components(components)

    warnings = {
        "unconnected_terminals": unconnected_terminals,
        "unmatched_terminals": build_simple_list(unmatched_terminals, original_to_simple),
        "suspicious_matches": build_simple_list(suspicious_matches, original_to_simple),
    }

    return {
        "components": canonical_components,
        "graph": simple_terminal_graph,
        "warnings": warnings,
        "skeleton_binary": skeleton,
        "terminal_match_debug": terminal_match_debug,
        "simple_id_map": original_to_simple,
    }


# =========================================================
# MAIN
# =========================================================
# Run dell'entrypoint del nuovo passo 05.
def main() -> None:
    if not INPUT_DIR.exists():
        raise FileNotFoundError(f"Cartella input non trovata: {INPUT_DIR}")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    if SAVE_DEBUG_IMAGES:
        DEBUG_TERMINAL_OVERLAY_DIR.mkdir(parents=True, exist_ok=True)
        DEBUG_SKELETON_OVERLAY_DIR.mkdir(parents=True, exist_ok=True)

    json_files = sorted(INPUT_DIR.glob("*.json"))
    if not json_files:
        raise FileNotFoundError(f"Nessun file JSON trovato in: {INPUT_DIR}")

    print(f"Input directory : {INPUT_DIR}")
    print(f"Output directory: {OUTPUT_DIR}")
    print(f"File trovati    : {len(json_files)}\n")

    for i, json_path in enumerate(json_files, start=1):
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        graph_info = build_terminal_graph_for_image(data)

        # -------------------------------------------------
        # 1) Eventuali immagini di debug
        # -------------------------------------------------
        if SAVE_DEBUG_IMAGES:
            image_path = Path(data["image_path"])
            image_bgr = cv2.imread(str(image_path))
            if image_bgr is not None:
                terminal_overlay = draw_terminal_overlay(
                    image_bgr,
                    data.get("terminals", []),
                    graph_info["terminal_match_debug"],
                    graph_info["simple_id_map"],
                )
                terminal_overlay_path = DEBUG_TERMINAL_OVERLAY_DIR / f"{json_path.stem}_terminal_overlay.jpg"
                cv2.imwrite(str(terminal_overlay_path), terminal_overlay)

            skeleton_overlay = draw_skeleton_overlay(
                graph_info["skeleton_binary"],
                data.get("terminals", []),
                graph_info["terminal_match_debug"],
                graph_info["simple_id_map"],
            )
            skeleton_overlay_path = DEBUG_SKELETON_OVERLAY_DIR / f"{json_path.stem}_skeleton_overlay.jpg"
            cv2.imwrite(str(skeleton_overlay_path), skeleton_overlay)

        # -------------------------------------------------
        # 2) Salvataggio JSON canonico del passo 05
        # -------------------------------------------------
        output_data = {
            "image_id": data.get("image_id"),
            "image_name": data.get("image_name"),
            "components": graph_info["components"],
            "graph": graph_info["graph"],
            "warnings": graph_info["warnings"],
        }

        out_json_path = OUTPUT_DIR / json_path.name
        with open(out_json_path, "w", encoding="utf-8") as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)

        print(
            f"[{i}/{len(json_files)}] {json_path.name} -> "
            f"componenti={len(output_data['components'])}, "
            f"nodi_grafo={len(output_data['graph'])}, "
            f"isolati={len(output_data['warnings']['unconnected_terminals'])}, "
            f"unmatched={len(output_data['warnings']['unmatched_terminals'])}"
        )

    print("\nCompletato.")
    print(f"JSON salvati in: {OUTPUT_DIR}")
    if SAVE_DEBUG_IMAGES:
        print(f"Debug overlay diagramma in: {DEBUG_TERMINAL_OVERLAY_DIR}")
        print(f"Debug overlay skeleton in: {DEBUG_SKELETON_OVERLAY_DIR}")


if __name__ == "__main__":
    main()
