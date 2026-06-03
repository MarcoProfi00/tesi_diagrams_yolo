"""
03_estimate_terminals.py

Scopo:
    Stimare i terminali dei componenti rilevati nel passo 02.

Strategie principali:
    - fixed
    - auto_by_aspect_ratio
    - one_terminal_by_orientation
    - two_terminal_by_connection_axis
    - terminal_auto_one_or_two

Casi speciali:
    - Capacitor / Polarized_Capacitor
    - Switch
    - Terminal
    - Led

    Per i componenti a 3 terminali non basta dire su quale lato cade il terminale
    ma serve anche capire dove si trova realmente lungo quel lato.
    Si usa una localizzazione "side peak": 
    prima stimiamo i lati attivi, poi cerchiamo il picco di connessione lungo il lato.
"""

from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import os
import json
import time
import cv2

from estimate_terminals.io_utils import io_load_class_metadata, img_build_foreground_binary
from estimate_terminals.processor import estimate_terminals_for_component
from estimate_terminals.debug_draw import draw_ic_ocr_summary, draw_terminals
from estimate_terminals.config import SAVE_DEBUG_IMAGES
from estimate_terminals.strategies_opamp import snap_opamp_top_aux_to_nearby_terminal
from estimate_terminals.state_switch import estimate_switch_open_closed_state
from estimate_terminals.ocr_integrated_circuit import enrich_ic_marking_ocr
from estimate_terminals.ocr_integrated_circuit_pins import (
    enrich_ic_pin_ocr,
    normalize_seven_segment_display_terminals,
)

#PATH / INPUT-OUTPUT
PROJECT_ROOT = Path(__file__).resolve().parents[2]
PIPELINE_DATASET = os.environ.get(
    "PIPELINE_DATASET",
    "pipeline1.0/batchA"
)

INPUT_DIR = PROJECT_ROOT / "outputs" / PIPELINE_DATASET / "02_assign_instances"
OUTPUT_DIR = PROJECT_ROOT / "outputs" / PIPELINE_DATASET / "03_estimate_terminals"
DEBUG_IMAGES_DIR = OUTPUT_DIR / "debug_images"

# Sottocartella dedicata alle immagini debug OCR degli Integrated Circuit.
# La separiamo dalle immagini dei terminali per mantenere la cartella
# debug_images principale piu' ordinata.
IC_OCR_DEBUG_IMAGES_DIR = DEBUG_IMAGES_DIR / "ic_ocr"

CLASS_TERMINALS_PATH = PROJECT_ROOT / "metadata" / "class_terminals_v1.yaml"


def _env_flag(name: str, default: bool = False) -> bool:
    value = str(os.environ.get(name, "")).strip().lower()
    if value in {"1", "true", "yes", "on"}:
        return True
    if value in {"0", "false", "no", "off"}:
        return False
    return default


IC_OCR_TIMING_ENABLED = _env_flag("IC_OCR_TIMING", default=False)
PIPELINE_IMAGE_IDS = {
    part.strip()
    for part in str(os.environ.get("PIPELINE_IMAGE_IDS", "")).split(",")
    if part.strip()
}


def _elapsed_ms(start_time: float) -> float:
    return round((time.perf_counter() - start_time) * 1000.0, 1)


def _collect_ic_timing(file_timing: dict, component: dict) -> None:
    if not IC_OCR_TIMING_ENABLED or component.get("class_name") != "Integrated_Circuit":
        return

    timing = component.get("_ic_timing") or {}
    pin_debug = component.get("ic_pin_ocr_debug") or {}
    pin_timing = pin_debug.get("timing_ms") or {}
    file_timing["ic_count"] += 1
    file_timing["marking_ms"] += float(timing.get("marking_ms") or 0.0)
    file_timing["pin_ms"] += float(timing.get("pin_ms") or 0.0)
    file_timing["ic_total_ms"] += float(timing.get("total_ms") or 0.0)
    file_timing["pin_side_ocr_ms"] += float(pin_timing.get("side_ocr_ms") or 0.0)
    file_timing["pin_side_fallback_ms"] += float(pin_timing.get("component_fallback_ms") or 0.0)


# =========================================================
# STATO COMPONENTI
# =========================================================
# Alcuni simboli hanno una proprieta' semantica oltre ai terminali.
# Lo switch, ad esempio, puo' essere open/closed: questa informazione nasce
# nel passo 03 perche' dipende dalla grafica del componente, non dal grafo.
def apply_component_state_if_needed(component: dict, meta: dict, image_binary):
    state_strategy = meta.get("state_strategy")

    if state_strategy is None:
        return

    if state_strategy == "switch_open_closed":
        state_info = estimate_switch_open_closed_state(image_binary, component)
        component["state"] = state_info["state"]
        component["state_confidence"] = state_info["confidence"]
        component["state_debug"] = state_info["debug"]
        return

    component["state"] = "unknown"
    component["state_confidence"] = 0.0
    component["state_debug"] = {
        "state_strategy": state_strategy,
        "reason": "unsupported_state_strategy",
    }

# =========================================================
# OCR INTEGRATED CIRCUIT
# =========================================================
def enrich_integrated_circuit_if_needed(component: dict, class_meta: dict, image_bgr):
    """
    Applica gli arricchimenti OCR solo agli Integrated_Circuit.

    Ordine:
      1. OCR nome/marking IC:
         - NE555
         - LM317T
         - TDA7000
         - ADC0804
         ecc.

      2. OCR pin:
         - pin_number
         - pin_label_text

    Regole importanti:
      - NON crea nuovi terminali;
      - NON cambia terminal_id;
      - NON cambia name/display_name;
      - aggiunge solo informazioni semantiche ai terminali già stimati.
    """

    if component.get("class_name") != "Integrated_Circuit":
        return component

    ic_meta = class_meta.get(component.get("class_id"), {}) or {}
    total_start = time.perf_counter() if IC_OCR_TIMING_ENABLED else None

    # Step 1: OCR nome/marking IC.
    marking_start = time.perf_counter() if IC_OCR_TIMING_ENABLED else None
    component = enrich_ic_marking_ocr(
        component=component,
        image_bgr=image_bgr,
        meta=ic_meta,
    )
    marking_ms = _elapsed_ms(marking_start) if marking_start is not None else None

    # Step 2: OCR pin number / pin label.
    pin_start = time.perf_counter() if IC_OCR_TIMING_ENABLED else None
    component = enrich_ic_pin_ocr(
        component=component,
        image_bgr=image_bgr,
        meta=ic_meta,
    )
    pin_ms = _elapsed_ms(pin_start) if pin_start is not None else None

    if total_start is not None:
        component["_ic_timing"] = {
            "marking_ms": marking_ms,
            "pin_ms": pin_ms,
            "total_ms": _elapsed_ms(total_start),
        }

    return component


# =========================================================
# OUTPUT JSON PUBBLICO
# =========================================================
def _round_bbox(bbox):
    if not bbox:
        return None
    return [round(float(v), 2) for v in bbox]


def _extract_body_bbox(component: dict):
    """
    Recupera il body_bbox raffinato dell'IC.

    Lo cerchiamo in più punti perché, a seconda della strategia usata,
    può essere salvato:
      1. direttamente nel componente;
      2. dentro connection_side_scores;
      3. dentro terminal_point_debug dei terminali.
    """

    # Caso migliore: body_bbox già salvato direttamente nel componente.
    body_bbox = component.get("body_bbox")
    if body_bbox:
        return _round_bbox(body_bbox)

    # Caso usato spesso dalla strategia di rilevazione terminali IC.
    side_scores = component.get("connection_side_scores") or {}
    body_bbox = side_scores.get("body_bbox")
    if body_bbox:
        return _round_bbox(body_bbox)

    # Fallback: alcuni terminali possono avere il body_bbox nel debug.
    for terminal in component.get("terminals", []):
        point_debug = terminal.get("terminal_point_debug") or {}
        body_bbox = point_debug.get("body_bbox")
        if body_bbox:
            return _round_bbox(body_bbox)

    return None


def _public_terminal(term: dict, include_pin_fields: bool = False) -> dict:
    public = {
        "terminal_id": term.get("terminal_id"),
        "instance_id": term.get("instance_id"),
        "component_class_name": term.get("component_class_name"),
        "name": term.get("name"),
        "display_name": term.get("display_name", term.get("name")),
        "display_terminal_id": term.get("display_terminal_id", term.get("terminal_id")),
        "relative_position": term.get("relative_position"),
        "x": term.get("x"),
        "y": term.get("y"),
    }

    if term.get("semantic_terminal_id") is not None:
        public["semantic_terminal_id"] = term.get("semantic_terminal_id")
    if term.get("semantic_terminal_name") is not None:
        public["semantic_terminal_name"] = term.get("semantic_terminal_name")

    if include_pin_fields:
        # ---------------------------------------------------------
        # Campi semantici OCR dei pin IC.
        #
        # Nota: questi campi NON sostituiscono il nome geometrico del
        # terminale, che rimane in name/display_name/display_terminal_id.
        # Servono solo ad arricchire il JSON con quello che leggiamo
        # vicino al pin nello schema.
        #
        # Esempi:
        #   name = "left_2", pin_number = "2", pin_label_text = "VIN"
        #   name = "right_1", pin_number = "3", pin_label_text = None
        #   name = "left_1", pin_number = None, pin_label_text = "IN"
        # ---------------------------------------------------------
        public["pin_number"] = term.get("pin_number")
        public["pin_label_text"] = term.get("pin_label_text")

        # Le confidence sono utili per debug, ma le aggiungiamo solo se
        # esistono davvero, così il JSON resta pulito.
        if term.get("pin_number_confidence") is not None:
            public["pin_number_confidence"] = term.get("pin_number_confidence")
        if term.get("pin_label_confidence") is not None:
            public["pin_label_confidence"] = term.get("pin_label_confidence")

    # Per gli IC vogliamo vedere sempre pin_number e pin_label_text,
    # anche quando uno dei due manca. Questo rende chiaro il caso LM317T
    # senza numero o TDA7000 senza label. Per gli altri campi continuiamo
    # a rimuovere i None come prima.
    keep_null_keys = set()
    if include_pin_fields:
        keep_null_keys.update({"pin_number", "pin_label_text"})

    return {
        key: value
        for key, value in public.items()
        if value is not None or key in keep_null_keys
    }


def _public_integrated_circuit(component: dict) -> dict:
    body_bbox = _extract_body_bbox(component)

    public = {
        "component_id": component.get("instance_id"),
        "instance_id": component.get("instance_id"),
        "class_id": component.get("class_id"),
        "class_name": component.get("class_name"),
        "bbox": _round_bbox(component.get("bbox")),
        "body_bbox": body_bbox,
        "use_for_terminals": component.get("use_for_terminals"),
        "use_for_masking": component.get("use_for_masking"),
        "estimated_orientation": component.get("estimated_orientation"),
        "ic_marking": component.get("ic_marking"),
        "ic_marking_confidence": component.get("ic_marking_confidence"),
        "ic_marking_engine": component.get("ic_marking_engine"),
        "ic_ocr_mode": component.get("ic_ocr_mode"),
        "ic_ocr_engines_used": component.get("ic_ocr_engines_used"),
        "ic_marking_variant": component.get("ic_marking_variant"),
        "ic_marking_bbox": _round_bbox(component.get("ic_marking_bbox")),
        "ic_marking_source_region": component.get("ic_marking_source_region"),
        "component_subtype": component.get("component_subtype"),
        "display_type": component.get("display_type"),
        "reference_designator_ocr": component.get("reference_designator_ocr"),
        "terminals": [
            _public_terminal(term, include_pin_fields=True)
            for term in component.get("terminals", [])
        ],
    }

    return {key: value for key, value in public.items() if value is not None}


def _public_component(component: dict, class_meta: dict) -> dict:
    if component.get("class_name") == "Integrated_Circuit":
        return _public_integrated_circuit(component)

    meta = class_meta.get(component.get("class_id"), {})
    output_fields = meta.get("output_fields", {}) or {}
    keep_debug = bool(output_fields.get("store_detection_debug", False))

    public = dict(component)
    public["terminals"] = [
        _public_terminal(term)
        for term in component.get("terminals", [])
    ]

    if not keep_debug:
        public.pop("connection_side_scores", None)
        public.pop("state_debug", None)
        for term in public.get("terminals", []):
            term.pop("terminal_point_debug", None)

    return public


def _public_output_components_and_terminals(components: list, class_meta: dict):
    public_components = [
        _public_component(component, class_meta)
        for component in components
    ]

    public_terminals = []
    for component in public_components:
        public_terminals.extend(component.get("terminals", []))

    return public_components, public_terminals

# =========================================================
# MAIN
# =========================================================
# Run the entrypoint for this pipeline stage.
def main() -> None:
    if not INPUT_DIR.exists():
        raise FileNotFoundError(f"Cartella input non trovata: {INPUT_DIR}")
    if not CLASS_TERMINALS_PATH.exists():
        raise FileNotFoundError(f"class_terminals_v1.yaml non trovato: {CLASS_TERMINALS_PATH}")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Le cartelle debug vengono create solo se il salvataggio immagini e' attivo.
    # Dentro debug_images manteniamo le immagini dei terminali; dentro
    # debug_images/ic_ocr salviamo solo le immagini summary OCR dei nomi IC.
    if SAVE_DEBUG_IMAGES:
        DEBUG_IMAGES_DIR.mkdir(parents=True, exist_ok=True)
        IC_OCR_DEBUG_IMAGES_DIR.mkdir(parents=True, exist_ok=True)

    class_meta = io_load_class_metadata(CLASS_TERMINALS_PATH)
    json_files = sorted(INPUT_DIR.glob("*.json"))
    if not json_files:
        raise FileNotFoundError(f"Nessun file JSON trovato in: {INPUT_DIR}")

    if PIPELINE_IMAGE_IDS:
        json_files = [
            path
            for path in json_files
            if path.stem in PIPELINE_IMAGE_IDS
        ]
        if not json_files:
            requested = ", ".join(sorted(PIPELINE_IMAGE_IDS))
            raise FileNotFoundError(
                f"Nessun file JSON trovato in {INPUT_DIR} per PIPELINE_IMAGE_IDS={requested}"
            )

    print(f"Input directory : {INPUT_DIR}")
    print(f"Output directory: {OUTPUT_DIR}")
    print(f"Class yaml      : {CLASS_TERMINALS_PATH}")
    print(f"File trovati    : {len(json_files)}\n")
    if PIPELINE_IMAGE_IDS:
        print(f"Filtro immagini : {sorted(PIPELINE_IMAGE_IDS)}\n")

    batch_timing = {
        "ic_count": 0,
        "marking_ms": 0.0,
        "pin_ms": 0.0,
        "ic_total_ms": 0.0,
        "pin_side_ocr_ms": 0.0,
        "pin_side_fallback_ms": 0.0,
    }

    for i, json_path in enumerate(json_files, start=1):
        file_timing = {
            "ic_count": 0,
            "marking_ms": 0.0,
            "pin_ms": 0.0,
            "ic_total_ms": 0.0,
            "pin_side_ocr_ms": 0.0,
            "pin_side_fallback_ms": 0.0,
        }
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        image_path = Path(data["image_path"])
        image_bgr = cv2.imread(str(image_path))
        if image_bgr is None:
            print(f"Attenzione: immagine non leggibile -> {image_path}")
            continue

        image_binary = img_build_foreground_binary(image_bgr)
        components = data.get("components", [])
        updated_components = []
        ic_component_indexes = []

        for comp_idx, comp in enumerate(components):
            comp_copy = dict(comp)
            terminals, estimated_orientation, connected_side, side_scores = estimate_terminals_for_component(comp_copy, class_meta, image_binary)
            comp_copy["terminals"] = terminals
            if estimated_orientation is not None:
                comp_copy["estimated_orientation"] = estimated_orientation
            if connected_side is not None:
                comp_copy["estimated_connection_side"] = connected_side
            if side_scores is not None:
                comp_copy["connection_side_scores"] = side_scores
            apply_component_state_if_needed(
                comp_copy,
                class_meta.get(comp_copy.get("class_id"), {}),
                image_binary,
            )

            # ---------------------------------------------------------
            # OCR Integrated Circuit.
            # ---------------------------------------------------------
            # Qui siamo ancora nello script 03, quindi abbiamo:
            # - immagine originale BGR, utile per OCR;
            # - terminali geometrici già stimati;
            # - body_bbox raffinato dentro connection_side_scores/terminal debug.
            # Non creiamo terminali nuovi: aggiungiamo campi OCR ai componenti
            # e ai terminali geometrici gia' stimati.
            # ---------------------------------------------------------
            # OCR Integrated Circuit.
            #
            # Per gli IC aggiungiamo, senza creare terminali nuovi:
            #   - ic_marking a livello componente;
            #   - pin_number / pin_label_text a livello terminale.
            #
            # L'arricchimento OCR viene lanciato dopo il loop sui componenti,
            # cosi possiamo parallelizzare gli IC della stessa immagine.
            # ---------------------------------------------------------
            updated_components.append(comp_copy)
            if comp_copy.get("class_name") == "Integrated_Circuit":
                ic_component_indexes.append(comp_idx)

            # Nota: i terminali sono gia' dentro comp_copy["terminals"].
            # enrich_integrated_circuit_if_needed li aggiorna direttamente
            # con i campi OCR senza cambiare terminal_id/name/display_name.
        if len(ic_component_indexes) <= 1:
            for comp_idx in ic_component_indexes:
                updated_components[comp_idx] = enrich_integrated_circuit_if_needed(
                    component=updated_components[comp_idx],
                    class_meta=class_meta,
                    image_bgr=image_bgr,
                )
                _collect_ic_timing(file_timing, updated_components[comp_idx])
        elif ic_component_indexes:
            with ThreadPoolExecutor(max_workers=min(2, len(ic_component_indexes))) as executor:
                futures = {
                    comp_idx: executor.submit(
                        enrich_integrated_circuit_if_needed,
                        component=updated_components[comp_idx],
                        class_meta=class_meta,
                        image_bgr=image_bgr,
                    )
                    for comp_idx in ic_component_indexes
                }
                for comp_idx in ic_component_indexes:
                    updated_components[comp_idx] = futures[comp_idx].result()
                    _collect_ic_timing(file_timing, updated_components[comp_idx])

        snap_opamp_top_aux_to_nearby_terminal(updated_components, image_binary)
        for component in updated_components:
            normalize_seven_segment_display_terminals(component)

        # ---------------------------------------------------------
        # Ricostruiamo all_terminals dopo eventuali post-processing.
        #
        # Alcune funzioni, come snap_opamp_top_aux_to_nearby_terminal,
        # possono modificare i terminali dentro updated_components.
        # Ricostruire la lista globale qui evita incoerenze tra:
        #   - components[*].terminals
        #   - terminals globale
        #   - immagini debug
        # ---------------------------------------------------------
        all_terminals = []
        for component in updated_components:
            all_terminals.extend(component.get("terminals", []))

        public_components, public_terminals = _public_output_components_and_terminals(
            updated_components,
            class_meta,
        )

        output_data = dict(data)
        output_data["components"] = public_components
        output_data["terminals"] = public_terminals
        output_data["n_terminals_estimated"] = len(public_terminals)

        out_json_path = OUTPUT_DIR / json_path.name
        with open(out_json_path, "w", encoding="utf-8") as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)

        if SAVE_DEBUG_IMAGES:
            # ---------------------------------------------------------
            # Debug generale terminali/componenti.
            # Rimane nella cartella debug_images principale.
            # ---------------------------------------------------------
            debug_img = draw_terminals(image_bgr, updated_components, all_terminals)
            out_img_path = DEBUG_IMAGES_DIR / f"{json_path.stem}_terminals.jpg"
            cv2.imwrite(str(out_img_path), debug_img)

            # ---------------------------------------------------------
            # Debug semplificato OCR dei nomi Integrated_Circuit.
            # Lo salviamo in una sottocartella separata per non mischiarlo
            # con le immagini dei terminali.
            #
            # Output esempio:
            #   debug_images/ic_ocr/ic1_ic_ocr.jpg
            # ---------------------------------------------------------
            ic_ocr_img = draw_ic_ocr_summary(image_bgr, updated_components)
            ic_ocr_img_path = IC_OCR_DEBUG_IMAGES_DIR / f"{json_path.stem}_ic_ocr.jpg"
            cv2.imwrite(str(ic_ocr_img_path), ic_ocr_img)

        print(f"[{i}/{len(json_files)}] {json_path.name} -> {len(updated_components)} componenti, {len(all_terminals)} terminali")
        if IC_OCR_TIMING_ENABLED and file_timing["ic_count"] > 0:
            for key in batch_timing:
                batch_timing[key] += file_timing[key]
            print(
                "  IC timing:"
                f" count={int(file_timing['ic_count'])}"
                f" marking={file_timing['marking_ms']:.1f}ms"
                f" pin={file_timing['pin_ms']:.1f}ms"
                f" pin_side_ocr={file_timing['pin_side_ocr_ms']:.1f}ms"
                f" pin_fallback={file_timing['pin_side_fallback_ms']:.1f}ms"
                f" total={file_timing['ic_total_ms']:.1f}ms"
            )

    print("\nCompletato.")
    print(f"JSON salvati in: {OUTPUT_DIR}")
    if IC_OCR_TIMING_ENABLED and batch_timing["ic_count"] > 0:
        avg_ic_ms = batch_timing["ic_total_ms"] / max(1, batch_timing["ic_count"])
        print(
            "IC OCR timing summary:"
            f" count={int(batch_timing['ic_count'])}"
            f" marking={batch_timing['marking_ms']:.1f}ms"
            f" pin={batch_timing['pin_ms']:.1f}ms"
            f" pin_side_ocr={batch_timing['pin_side_ocr_ms']:.1f}ms"
            f" pin_fallback={batch_timing['pin_side_fallback_ms']:.1f}ms"
            f" total={batch_timing['ic_total_ms']:.1f}ms"
            f" avg_per_ic={avg_ic_ms:.1f}ms"
        )
    if SAVE_DEBUG_IMAGES:
        print(f"Immagini debug terminali salvate in: {DEBUG_IMAGES_DIR}")
        print(f"Immagini debug OCR IC salvate in: {IC_OCR_DEBUG_IMAGES_DIR}")


if __name__ == "__main__":
    main()
