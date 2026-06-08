"""
Passo 05: costruzione del grafo terminale.

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
    - terminal_metadata -> lookup opzionale per display_name/pin degli stessi terminali
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

from pathlib import Path
import os
import json
import cv2

from build_terminal_graph.config import SAVE_DEBUG_IMAGES
from build_terminal_graph.debug_draw import draw_skeleton_overlay, draw_terminal_overlay
from build_terminal_graph.processor import build_terminal_graph_for_image

# =========================================================
# PERCORSI / INPUT-OUTPUT
# =========================================================
# Come negli altri step, il dataset puo' essere cambiato via variabile
# ambiente. Lo script legge l'output di 04 e scrive il JSON canonico di 05.
PROJECT_ROOT = Path(__file__).resolve().parents[2]
PIPELINE_DATASET = os.environ.get("PIPELINE_DATASET", "pipeline1.0/batchC/batchC1")
PIPELINE_IMAGE_IDS = [
    image_id.strip()
    for image_id in os.environ.get("PIPELINE_IMAGE_IDS", "").split(",")
    if image_id.strip()
]

INPUT_DIR = PROJECT_ROOT / "outputs" / PIPELINE_DATASET / "04_extract_wires"
OUTPUT_DIR = PROJECT_ROOT / "outputs" / PIPELINE_DATASET / "05_build_terminal_graph"

# Cartelle per le immagini di debug.
DEBUG_TERMINAL_OVERLAY_DIR = OUTPUT_DIR / "debug_terminal_overlay"
DEBUG_SKELETON_OVERLAY_DIR = OUTPUT_DIR / "debug_skeleton_overlay"


# =========================================================
# MAIN
# =========================================================
def main() -> None:
    """Entry point dello step 05."""
    if not INPUT_DIR.exists():
        raise FileNotFoundError(f"Cartella input non trovata: {INPUT_DIR}")

    # La cartella principale contiene i JSON finali; le sottocartelle debug sono
    # opzionali e dipendono dalla configurazione in build_terminal_graph/config.py.
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    if SAVE_DEBUG_IMAGES:
        DEBUG_TERMINAL_OVERLAY_DIR.mkdir(parents=True, exist_ok=True)
        DEBUG_SKELETON_OVERLAY_DIR.mkdir(parents=True, exist_ok=True)

    # Ogni JSON di input e' un circuito gia' arricchito dallo step 04 con i path
    # dello skeleton e delle immagini binarie intermedie.
    json_files = sorted(INPUT_DIR.glob("*.json"))
    if PIPELINE_IMAGE_IDS:
        # Filtro utile per rilanciare il grafo su poche immagini senza
        # rigenerare l'intero batch.
        wanted = set(PIPELINE_IMAGE_IDS)
        json_files = [json_path for json_path in json_files if json_path.stem in wanted]
    if not json_files:
        raise FileNotFoundError(f"Nessun file JSON trovato in: {INPUT_DIR}")

    print(f"Input directory : {INPUT_DIR}")
    print(f"Output directory: {OUTPUT_DIR}")
    print(f"File trovati    : {len(json_files)}")
    if PIPELINE_IMAGE_IDS:
        print(f"\nFiltro immagini : {PIPELINE_IMAGE_IDS}\n")
    else:
        print()

    for i, json_path in enumerate(json_files, start=1):
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        # Tutta la logica vera del passo 05 sta nel processor: match terminale
        # -> skeleton, euristiche di merge/split e costruzione del grafo.
        graph_info = build_terminal_graph_for_image(data)

        # -------------------------------------------------
        # 1) Eventuali immagini di debug
        # -------------------------------------------------
        if SAVE_DEBUG_IMAGES:
            # Evidenziamo nei debug i terminali isolati o non agganciati: sono i
            # punti piu' utili da controllare quando il grafo sembra sbagliato.
            problem_terminal_ids = set(graph_info["warnings"].get("unconnected_terminals", []))
            problem_terminal_ids.update(graph_info["warnings"].get("unmatched_terminals", []))

            image_path = Path(data["image_path"])
            image_bgr = cv2.imread(str(image_path))
            if image_bgr is not None:
                terminal_overlay = draw_terminal_overlay(
                    image_bgr,
                    data.get("terminals", []),
                    graph_info["terminal_match_debug"],
                    graph_info["simple_id_map"],
                    problem_terminal_ids,
                )
                terminal_overlay_path = DEBUG_TERMINAL_OVERLAY_DIR / f"{json_path.stem}_terminal_overlay.jpg"
                cv2.imwrite(str(terminal_overlay_path), terminal_overlay)

            # Overlay sullo skeleton: mostra se il punto di aggancio cade
            # davvero sul filo usato per costruire le connected components.
            skeleton_overlay = draw_skeleton_overlay(
                graph_info["skeleton_binary"],
                data.get("terminals", []),
                graph_info["terminal_match_debug"],
                graph_info["simple_id_map"],
                problem_terminal_ids,
            )
            skeleton_overlay_path = DEBUG_SKELETON_OVERLAY_DIR / f"{json_path.stem}_skeleton_overlay.jpg"
            cv2.imwrite(str(skeleton_overlay_path), skeleton_overlay)

        # -------------------------------------------------
        # 2) Salvataggio JSON canonico del passo 05
        # -------------------------------------------------
        # Il JSON finale non contiene immagini debug o label interne dello
        # skeleton: espone solo componenti, metadati terminali, grafo e warning.
        output_data = {
            "image_id": data.get("image_id"),
            "image_name": data.get("image_name"),
            "components": graph_info["components"],
            "terminal_metadata": graph_info["terminal_metadata"],
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
