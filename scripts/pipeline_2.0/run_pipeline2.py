"""
Entry point della pipeline 2.0.

Parte dai Graph JSON gia prodotti dal passo 06
della pipeline 1.0 e genera gli artefatti elettrici successivi:

- normalizzazione del JSON;
- costruzione della mappa dei nodi elettrici;
- associazione dei valori tramite YAML;
- generazione di netlist SPICE complete o parziali;
- esecuzione opzionale di ngspice;
- report elettrico finale;
- contesto diagnostico strutturato.

La pipeline resta unica per Batch A, Batch B, Batch C1, Batch C2 e batch futuri.
`05_device_profiles.py` e ancora un'estensione dichiarativa non integrata nel
flusso eseguito da questo entry point.
"""

from __future__ import annotations

import argparse
import importlib.util
from pathlib import Path
import sys
from types import ModuleType


SCRIPT_DIR = Path(__file__).resolve().parent
MODULE_DIR = SCRIPT_DIR / "json_to_spice"

# Gli step caricati da file possono condividere moduli interni non numerati.
# Inserire una sola volta la directory mantiene validi sia la CLI sia gli
# import effettuati dall'orchestratore unificato.
if str(MODULE_DIR) not in sys.path:
    sys.path.insert(0, str(MODULE_DIR))


def load_step_module(filename: str, module_name: str) -> ModuleType:
    """
    Carica un modulo da file.

    I file della pipeline sono numerati, per esempio 01_io.py, quindi non sono
    importabili con la sintassi Python standard.
    """
    module_path = MODULE_DIR / filename
    spec = importlib.util.spec_from_file_location(module_name, module_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Impossibile caricare modulo: {module_path}")

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


io = load_step_module("01_io.py", "pipeline2_io")
normalize = load_step_module("02_normalize.py", "pipeline2_normalize")
node_map = load_step_module("03_node_map.py", "pipeline2_node_map")
values = load_step_module("04_values.py", "pipeline2_values")
component_rules = load_step_module("06_component_rules.py", "pipeline2_component_rules")
spice_emit = load_step_module("07_spice_emit.py", "pipeline2_spice_emit")
spice_run = load_step_module("08_spice_run.py", "pipeline2_spice_run")
diagnostic_context = load_step_module("10_build_diagnostic_context.py", "pipeline2_diagnostic_context")


def run_technical_pipeline(
    input_json: str | Path,
    output_dir: str | Path,
    values_path: str | Path,
    run_spice: bool = False,
    ngspice_executable: str | None = None,
) -> dict[str, object]:
    """Esegue gli step tecnici 01-08 usando percorsi espliciti.

    Questa funzione contiene l'unica implementazione della conversione
    Graph JSON -> SPICE. I launcher possono quindi scegliere liberamente la
    posizione di input e output senza duplicare la logica elettrica.
    """
    input_json = Path(input_json).resolve()
    output_dir = Path(output_dir).resolve()
    values_path = Path(values_path).resolve()

    graph_copy_path = io.copy_source_graph(input_json, output_dir)

    raw_graph = io.load_json(input_json)
    normalized = normalize.normalize_circuit_graph(raw_graph)
    normalized_path = io.write_json(output_dir / "02_normalized_circuit.json", normalized)
    node_map_data = node_map.build_node_map(normalized)
    node_map_path = io.write_json(output_dir / "03_node_map.json", node_map_data)
    values_data = values.load_simple_yaml(values_path)
    values_bound = values.build_values_bound(
        normalized_circuit=normalized,
        node_map=node_map_data,
        values_data=values_data,
        values_source=values_path,
    )
    values_bound_path = io.write_json(output_dir / "04_values_bound.json", values_bound)
    spice_classes_path = io.PROJECT_ROOT / "metadata" / "pipeline2_spice_classes.yaml"
    spice_classes = values.load_simple_yaml(spice_classes_path)
    spice_models_path = io.PROJECT_ROOT / "metadata" / "pipeline2_spice_models.yaml"
    spice_models = values.load_simple_yaml(spice_models_path)
    component_rules_data = component_rules.build_component_rules(
        values_bound=values_bound,
        spice_classes=spice_classes,
        spice_classes_source=spice_classes_path,
    )
    component_rules_path = io.write_json(
        output_dir / "06_component_rules.json",
        component_rules_data,
    )
    netlist_path, spice_emit_report = spice_emit.write_spice_outputs(
        output_dir=output_dir,
        component_rules=component_rules_data,
        spice_models=spice_models,
        spice_models_source=spice_models_path,
    )
    spice_emit_report_path = io.write_json(
        output_dir / "07_spice_emit_report.json",
        spice_emit_report,
    )
    spice_run_report_path = None
    spice_run_report = None
    if run_spice:
        spice_run_report = spice_run.run_ngspice(
            output_dir=output_dir,
            executable=ngspice_executable,
        )
        spice_run_report_path = io.write_json(
            output_dir / "08_spice_run.json",
            spice_run_report,
        )

    return {
        "input_json": input_json,
        "values_path": values_path,
        "output_dir": output_dir,
        "graph_copy_path": graph_copy_path,
        "normalized": normalized,
        "normalized_path": normalized_path,
        "node_map": node_map_data,
        "node_map_path": node_map_path,
        "values_bound": values_bound,
        "values_bound_path": values_bound_path,
        "component_rules": component_rules_data,
        "component_rules_path": component_rules_path,
        "netlist_path": netlist_path,
        "spice_emit_report": spice_emit_report,
        "spice_emit_report_path": spice_emit_report_path,
        "spice_run_report": spice_run_report,
        "spice_run_report_path": spice_run_report_path,
    }


def run_one_circuit(
    batch_name: str,
    circuit_id: str,
    run_spice: bool = False,
    ngspice_executable: str | None = None,
    experiment_name: str | None = None,
) -> Path:
    """Esegue la Pipeline 2.0 storica su un circuito del repository."""
    input_json = io.resolve_pipeline1_graph_json(batch_name, circuit_id)
    output_dir = io.prepare_circuit_output(batch_name, circuit_id, experiment_name)
    values_path = values.find_manual_values_path(io.PROJECT_ROOT, batch_name, circuit_id)
    result = run_technical_pipeline(
        input_json=input_json,
        output_dir=output_dir,
        values_path=values_path,
        run_spice=run_spice,
        ngspice_executable=ngspice_executable,
    )

    normalized = result["normalized"]
    normalized_path = result["normalized_path"]
    node_map_data = result["node_map"]
    node_map_path = result["node_map_path"]
    values_bound = result["values_bound"]
    values_bound_path = result["values_bound_path"]
    component_rules_data = result["component_rules"]
    component_rules_path = result["component_rules_path"]
    netlist_path = result["netlist_path"]
    spice_emit_report = result["spice_emit_report"]
    spice_emit_report_path = result["spice_emit_report_path"]
    spice_run_report = result["spice_run_report"]
    spice_run_report_path = result["spice_run_report_path"]

    diagnostic_context_data = diagnostic_context.build_diagnostic_context(
        output_dir=output_dir,
        batch_name=batch_name,
        circuit_id=circuit_id,
        project_root=io.PROJECT_ROOT,
        experiment_name=experiment_name,
    )
    diagnostic_context_path = io.write_json(
        output_dir / "10_diagnostic_context.json",
        diagnostic_context_data,
    )

    stats = normalized.get("stats", {})
    node_stats = node_map_data.get("stats", {})
    values_stats = values_bound.get("stats", {})
    rules_stats = component_rules_data.get("stats", {})
    emit_warnings = spice_emit_report.get("warnings") or []
    spice_run_summary = ""
    if spice_run_report:
        spice_run_summary = (
            f"; run -> {spice_run_report_path} "
            f"(status={spice_run_report.get('status')}, "
            f"exit_code={spice_run_report.get('exit_code')})"
        )
    print(
        f"{batch_name}/{experiment_name + '/' if experiment_name else ''}{circuit_id}: "
        f"normalized -> {normalized_path} "
        f"(components={stats.get('components_count')}, "
        f"terminals={stats.get('terminals_count')}, "
        f"edges={stats.get('undirected_edges_count')}); "
        f"node_map -> {node_map_path} "
        f"(nodes={node_stats.get('nodes_count')}, "
        f"ground_groups={node_stats.get('ground_groups_count')}); "
        f"values -> {values_bound_path} "
        f"(bound={values_stats.get('bound_components')}, "
        f"missing={values_stats.get('missing_components')}, "
        f"unsupported={values_stats.get('unsupported_components')}); "
        f"rules -> {component_rules_path} "
        f"(ready={rules_stats.get('spice_ready_components')}, "
        f"not_emitted={rules_stats.get('not_emitted_components')}, "
        f"missing={rules_stats.get('missing_components')}, "
        f"unsupported={rules_stats.get('unsupported_components')}); "
        f"spice -> {netlist_path} "
        f"(emitted={spice_emit_report.get('emitted_elements')}, "
        f"skipped={spice_emit_report.get('skipped_elements')}, "
        f"warnings={len(emit_warnings)}, "
        f"report={spice_emit_report_path})"
        f"{spice_run_summary}; "
        f"context -> {diagnostic_context_path}"
    )

    return output_dir


def parse_args() -> argparse.Namespace:
    """Legge gli argomenti da terminale."""
    parser = argparse.ArgumentParser(
        description="Pipeline 2.0: normalizzazione Graph JSON."
    )
    parser.add_argument(
        "--batch",
        required=True,
        help="Nome batch dentro outputs/pipeline1.0, per esempio batchA.",
    )
    parser.add_argument(
        "--circuits",
        nargs="+",
        required=True,
        help="Lista circuiti da processare, per esempio a01 a02 a10.",
    )
    parser.add_argument(
        "--run-spice",
        action="store_true",
        help="Esegue anche lo step 08 con ngspice dopo la generazione della netlist.",
    )
    parser.add_argument(
        "--ngspice-executable",
        default=None,
        help="Path o nome dell'eseguibile ngspice da usare, per esempio ngspice_con.",
    )
    parser.add_argument(
        "--experiment",
        default=None,
        help=(
            "Nome esperimento opzionale. Se indicato, gli output vengono scritti in "
            "outputs/pipeline2.0/<batch>/<experiment>/<circuit>/."
        ),
    )
    return parser.parse_args()


def main() -> None:
    """Entry point da terminale."""
    args = parse_args()
    for circuit_id in args.circuits:
        run_one_circuit(
            batch_name=args.batch,
            circuit_id=circuit_id,
            run_spice=args.run_spice,
            ngspice_executable=args.ngspice_executable,
            experiment_name=args.experiment,
        )


if __name__ == "__main__":
    main()
