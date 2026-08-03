"""
Generazione della netlist SPICE.

Questo modulo converte la rappresentazione normalizzata del circuito, la
node map e i valori YAML in una netlist SPICE completa o parziale.

La generazione e tollerante ai componenti incompleti:

- emette gli elementi supportati e pronti;
- registra nel report componenti saltati, warning e modelli mancanti;
- puo quindi produrre una netlist parziale, che lo step 08 valutera con ngspice.

Responsabilita:

- emettere righe SPICE per componenti supportati;
- includere modelli .model o .subckt quando dichiarati;
- aggiungere analisi base come .op o .tran quando richiesto;
- commentare componenti saltati per valori o modelli mancanti;
- produrre `07_netlist.cir` e `07_spice_emit_report.json`.
"""

from __future__ import annotations

import hashlib
import re
import math
from pathlib import Path
from typing import Any


EXTERNAL_MODELS_BUNDLE_NAME = "07_external_models.lib"


def decode_external_model(model_bytes: bytes) -> tuple[str, str]:
    """Decodifica modelli SPICE moderni o legacy senza alterare l'asset sorgente."""
    for encoding in ("utf-8-sig", "cp1252"):
        try:
            return model_bytes.decode(encoding), encoding
        except UnicodeDecodeError:
            continue
    raise ValueError("External SPICE model uses an unsupported text encoding")


def resolve_model_file(
    relative_path: str,
    spice_models_source: str | Path | None,
) -> tuple[Path, str]:
    """Risolve un modello esterno confinandolo alla cartella del registro."""
    if spice_models_source is None:
        raise ValueError("External SPICE models require the model registry source path.")

    registry_path = Path(spice_models_source).resolve()
    registry_dir = registry_path.parent if registry_path.is_file() else registry_path
    requested_path = Path(relative_path)
    if requested_path.is_absolute():
        raise ValueError(f"External SPICE model paths must be relative: {relative_path}")

    model_path = (registry_dir / requested_path).resolve()
    try:
        model_path.relative_to(registry_dir)
    except ValueError as exc:
        raise ValueError(
            f"External SPICE model escapes the registry directory: {relative_path}"
        ) from exc
    if not model_path.is_file():
        raise FileNotFoundError(f"External SPICE model not found: {model_path}")
    return model_path, requested_path.as_posix()


def validate_ngspice_defines(
    model_name: str,
    raw_defines: Any,
) -> dict[str, str]:
    """Valida le variabili ngspice dichiarate da un modello nel registro."""
    if raw_defines in (None, ""):
        return {}
    if not isinstance(raw_defines, dict):
        raise ValueError(f"{model_name}: ngspice_defines must be a mapping")

    defines: dict[str, str] = {}
    for raw_name, raw_value in raw_defines.items():
        name = str(raw_name).strip()
        value = str(raw_value).strip()
        if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", name):
            raise ValueError(f"{model_name}: invalid ngspice define name: {name!r}")
        if not value or any(character in value for character in "\r\n\x00"):
            raise ValueError(f"{model_name}: invalid value for ngspice define {name}")
        defines[name] = value
    return dict(sorted(defines.items()))


def resolve_model_entries(
    spice_models: dict[str, Any] | None = None,
    spice_models_source: str | Path | None = None,
    requested_models: set[str] | list[str] | tuple[str, ...] | None = None,
) -> dict[str, dict[str, Any]]:
    """Carica solo i modelli richiesti e ne conserva i requisiti di runtime."""
    resolved: dict[str, dict[str, Any]] = {}
    yaml_models = (spice_models or {}).get("models") or {}
    selected = (
        sorted({str(model) for model in requested_models})
        if requested_models is not None
        else sorted(str(model) for model in yaml_models)
    )

    # I modelli SPICE non vengono definiti nel codice: lo step 07 legge solo il
    # registro metadata e risolve esclusivamente quelli richiesti dalla netlist.
    for model_name in selected:
        model_data = yaml_models.get(model_name)
        if model_data is None:
            continue

        source: dict[str, Any] | None = None
        if isinstance(model_data, dict):
            line = model_data.get("line")
            lines = model_data.get("lines")
            if isinstance(lines, dict):
                line = "\n".join(str(item) for item in lines.values() if item not in (None, ""))
            model_file = model_data.get("file")
            if model_file not in (None, ""):
                model_path, portable_path = resolve_model_file(
                    str(model_file),
                    spice_models_source,
                )
                model_bytes = model_path.read_bytes()
                actual_sha256 = hashlib.sha256(model_bytes).hexdigest().upper()
                expected_sha256 = str(model_data.get("sha256") or "").strip().upper()
                if not expected_sha256:
                    raise ValueError(
                        f"{model_name}: external SPICE model requires a sha256 value"
                    )
                if actual_sha256 != expected_sha256:
                    raise ValueError(
                        f"{model_name}: external SPICE model SHA-256 mismatch "
                        f"(expected {expected_sha256}, found {actual_sha256})"
                    )
                decoded_model, model_encoding = decode_external_model(model_bytes)
                line = decoded_model.replace("\r\n", "\n").replace("\r", "\n").rstrip()
                source = {
                    "model": model_name,
                    "kind": "file",
                    "file": portable_path,
                    "sha256": actual_sha256,
                    "encoding": model_encoding,
                }
            defines = validate_ngspice_defines(
                model_name,
                model_data.get("ngspice_defines"),
            )
        else:
            line = model_data
            defines = {}
        if line:
            resolved[model_name] = {
                "text": str(line),
                "source": source,
                "ngspice_defines": defines,
            }

    return resolved


def build_model_lines(
    spice_models: dict[str, Any] | None = None,
    spice_models_source: str | Path | None = None,
    requested_models: set[str] | list[str] | tuple[str, ...] | None = None,
) -> dict[str, str]:
    """Costruisce il dizionario testuale dei modelli SPICE richiesti."""
    return {
        model_name: str(entry["text"])
        for model_name, entry in resolve_model_entries(
            spice_models=spice_models,
            spice_models_source=spice_models_source,
            requested_models=requested_models,
        ).items()
    }


def build_model_registry_fingerprint(
    spice_models: dict[str, Any],
    spice_models_source: str | Path,
) -> str:
    """Firma il registro e i file esterni, validandoli prima della cache."""
    registry_path = Path(spice_models_source).resolve()
    if not registry_path.is_file():
        raise FileNotFoundError(f"SPICE model registry not found: {registry_path}")

    resolved = resolve_model_entries(
        spice_models=spice_models,
        spice_models_source=registry_path,
    )
    digest = hashlib.sha256()
    digest.update(registry_path.read_bytes())
    for model_name, entry in sorted(resolved.items()):
        source = entry.get("source")
        if not isinstance(source, dict):
            continue
        digest.update(str(model_name).encode("utf-8"))
        digest.update(str(source.get("file") or "").encode("utf-8"))
        digest.update(str(source.get("sha256") or "").encode("ascii"))
    return digest.hexdigest()


def safe_name(raw_name: str) -> str:
    """Restituisce un frammento sicuro per il nome di un elemento SPICE."""
    return re.sub(r"[^A-Za-z0-9_]", "_", raw_name)


def element_name(prefix: str, raw_name: str) -> str:
    """Costruisce un nome di elemento SPICE con un prefisso valido."""
    return f"{prefix}{safe_name(raw_name)}"


def spice_value(value: Any, unit: str | None = None) -> str:
    """
    Converte un semplice valore scalare in testo SPICE.

    I valori YAML dovrebbero essere gia espressi nelle unita di base. Questo
    helper aggiunge soltanto alcuni suffissi comuni quando servono.
    """
    if value is None:
        return ""

    unit_text = (unit or "").strip().lower()
    suffix_by_unit = {
        "ohm": "",
        "kohm": "k",
        "mohm": "meg",
        "pf": "p",
        "nf": "n",
        "uf": "u",
        "µf": "u",
        "mf": "m",
        "khz": "k",
        "mhz": "meg",
    }
    suffix = suffix_by_unit.get(unit_text, "")
    return f"{value}{suffix}"


def source_kind(parameters: dict[str, Any]) -> str:
    """Restituisce il tipo minimo della sorgente SPICE, normalmente DC."""
    kind = str(parameters.get("type", "dc")).upper()
    if kind == "DC":
        return "DC"
    return kind


def voltage_source_expression(parameters: dict[str, Any]) -> str:
    """Costruisce l'espressione SPICE per una sorgente di tensione."""
    source_type = str(parameters.get("type", "dc")).lower()
    waveform = str(parameters.get("waveform", "")).lower()

    if source_type == "pulse" or waveform == "square":
        low_value = parameters.get("low_value", 0)
        high_value = parameters.get("high_value", parameters.get("value"))
        delay = parameters.get("delay", 0)
        rise_time = parameters.get("rise_time", 0)
        fall_time = parameters.get("fall_time", 0)
        pulse_width = parameters.get("pulse_width")
        period = parameters.get("period")
        if high_value in (None, "") or pulse_width in (None, "") or period in (None, ""):
            return f"DC {spice_value(parameters.get('value'), parameters.get('unit'))}"
        return f"PULSE({low_value} {high_value} {delay} {rise_time} {fall_time} {pulse_width} {period})"

    if source_type == "sin" or waveform == "sin":
        offset = parameters.get("offset", 0)
        amplitude = parameters.get("amplitude", parameters.get("value"))
        frequency = parameters.get("frequency")
        if amplitude in (None, "") or frequency in (None, ""):
            return f"DC {spice_value(parameters.get('value'), parameters.get('unit'))}"
        return f"SIN({offset} {amplitude} {frequency})"

    return f"{source_kind(parameters)} {spice_value(parameters.get('value'), parameters.get('unit'))}"


def emit_equivalent_ac_source(component_id: str, rule: dict[str, Any]) -> tuple[str | None, str | None]:
    """Emette l'equivalente di un trasformatore come sorgente sinusoidale."""
    nodes = rule.get("nodes") or []
    parameters = rule.get("parameters") or {}
    if len(nodes) != 2:
        return None, f"{component_id}: equivalent AC source does not have two nodes"

    rms_value = parameters.get("secondary_voltage_rms")
    frequency = parameters.get("frequency")
    if rms_value in (None, "") or frequency in (None, ""):
        return None, f"{component_id}: missing RMS voltage or frequency"

    peak_value = parameters.get("secondary_voltage_peak")
    if peak_value in (None, ""):
        peak_value = float(rms_value) * math.sqrt(2)

    offset = parameters.get("offset", 0)
    line = (
        f"{element_name('V', component_id)} {nodes[0]} {nodes[1]} "
        f"SIN({offset} {peak_value:.6g} {frequency})"
    )
    return line, None


def emit_supply(name: str, supply: dict[str, Any]) -> tuple[str | None, str | None]:
    """Emette un'alimentazione manuale come sorgente di tensione SPICE."""
    if supply.get("status") != "spice_ready":
        return None, f"{name}: supply not ready"

    nodes = supply.get("nodes") or []
    parameters = supply.get("parameters") or {}
    if len(nodes) != 2:
        return None, f"{name}: supply does not have two nodes"

    line = (
        f"{element_name('V', str(name))} "
        f"{nodes[0]} {nodes[1]} "
        f"{voltage_source_expression(parameters)}"
    )
    return line, None


def emit_direct(component_id: str, rule: dict[str, Any]) -> tuple[str | None, str | None]:
    """Emette primitive SPICE dirette come R, C, L, V e I."""
    prefix = rule.get("spice_prefix")
    nodes = rule.get("nodes") or []
    parameters = rule.get("parameters") or {}
    emit_as = rule.get("emit_as")

    if emit_as == "equivalent_ac_source":
        return emit_equivalent_ac_source(component_id, rule)

    if not prefix or len(nodes) < 2:
        return None, f"{component_id}: incomplete direct rule"

    if prefix in ("V", "I"):
        expression = voltage_source_expression(parameters) if prefix == "V" else (
            f"{source_kind(parameters)} {spice_value(parameters.get('value'), parameters.get('unit'))}"
        )
        line = f"{element_name(prefix, component_id)} {nodes[0]} {nodes[1]} {expression}"
        return line, None

    value = parameters.get("value")
    unit = parameters.get("unit")
    if emit_as in ("resistive_load", "resistor"):
        unit = parameters.get("resistance_unit") or unit
    line = f"{element_name(prefix, component_id)} {' '.join(nodes)} {spice_value(value, unit)}"
    return line, None


def emit_equivalent(component_id: str, rule: dict[str, Any]) -> tuple[str | None, str | None]:
    """Emette carichi equivalenti, attualmente modellati come resistenze."""
    nodes = rule.get("nodes") or []
    parameters = rule.get("parameters") or {}
    if len(nodes) != 2:
        return None, f"{component_id}: equivalent component does not have two nodes"

    value = parameters.get("equivalent_resistance")
    unit = parameters.get("resistance_unit") or parameters.get("unit")
    line = f"{element_name('R', component_id)} {nodes[0]} {nodes[1]} {spice_value(value, unit)}"
    return line, None


def emit_model_component(component_id: str, rule: dict[str, Any]) -> tuple[str | None, str | None]:
    """Emette componenti basati su modello, attualmente LED e diodi."""
    prefix = rule.get("spice_prefix")
    nodes = rule.get("nodes") or []
    parameters = rule.get("parameters") or {}
    model = parameters.get("model")

    if not prefix or not model or len(nodes) < 2:
        return None, f"{component_id}: incomplete model-based component"

    line = f"{element_name(prefix, component_id)} {' '.join(nodes)} {model}"
    return line, None


def emit_subcircuit(component_id: str, rule: dict[str, Any]) -> tuple[str | None, str | None]:
    """Emette una subcircuit SPICE generica con nodi dichiarati nello YAML."""
    nodes = rule.get("nodes") or []
    parameters = rule.get("parameters") or {}
    subcircuit = parameters.get("model")
    if not subcircuit or len(nodes) < 2:
        return None, f"{component_id}: incomplete subcircuit override"

    return f"{element_name('X', component_id)} {' '.join(nodes)} {subcircuit}", None


def emit_simplified(component_id: str, rule: dict[str, Any]) -> tuple[str | None, str | None]:
    """Emette componenti semplificati, come switch aperti o chiusi."""
    nodes = rule.get("nodes") or []
    strategy = rule.get("strategy")
    if len(nodes) != 2:
        return None, f"{component_id}: switch does not have two nodes"

    if strategy == "open_circuit":
        return f"* {component_id} open: not emitted", f"{component_id}: open switch not emitted"
    if strategy == "short_circuit":
        return f"{element_name('R', component_id)} {nodes[0]} {nodes[1]} 1m", None
    return None, f"{component_id}: unsupported switch strategy"


def emit_component(component_id: str, rule: dict[str, Any]) -> tuple[str | None, str | None, str | None]:
    """Emette una singola riga SPICE oppure un commento."""
    status = rule.get("status")
    support = rule.get("spice_support")
    nodes = [str(node) for node in (rule.get("nodes") or [])]

    if status == "measurement_only":
        parameters = rule.get("parameters") or {}
        input_resistance = parameters.get("input_resistance")
        if input_resistance not in (None, "") and len(nodes) == 2:
            unit = parameters.get("resistance_unit") or "ohm"
            line = f"{element_name('Rmeter_', component_id)} {nodes[0]} {nodes[1]} {spice_value(input_resistance, unit)}"
            return line, None, None
        return None, None, None

    if status != "spice_ready":
        return None, None, None

    if len(nodes) >= 2 and len(set(nodes)) == 1:
        return None, None, f"{component_id}: terminals collapse to the same SPICE node; not emitted"

    if support == "direct":
        line, warning = emit_direct(component_id, rule)
    elif support == "equivalent":
        line, warning = emit_equivalent(component_id, rule)
    elif support == "model":
        line, warning = emit_model_component(component_id, rule)
    elif support == "subcircuit":
        line, warning = emit_subcircuit(component_id, rule)
    elif support == "simplified":
        line, warning = emit_simplified(component_id, rule)
    else:
        line, warning = None, f"{component_id}: unsupported SPICE support type ({support})"

    model = None
    parameters = rule.get("parameters") or {}
    if support in ("model", "subcircuit"):
        model = parameters.get("model")

    return line, model, warning


def build_analysis_lines(simulation: dict[str, Any]) -> tuple[list[str], list[str]]:
    """Costruisce le direttive di analisi SPICE richieste dal values.yaml."""
    analyses = simulation.get("analyses") or ["op"]
    if not isinstance(analyses, list):
        analyses = [analyses]

    lines: list[str] = []
    enabled = {str(item).lower() for item in analyses}

    if "op" in enabled:
        lines.append(".op")

    if "tran" in enabled:
        lines.append(".save all")
        tran = simulation.get("tran") or {}
        step = tran.get("step", "0.1ms") if isinstance(tran, dict) else "0.1ms"
        stop = tran.get("stop", "40ms") if isinstance(tran, dict) else "40ms"
        lines.append(f".tran {step} {stop}")

    return lines, sorted(enabled)


def build_control_lines(
    analyses: list[str],
    probe_nodes: list[str],
    device_current_vectors: list[str] | None = None,
) -> list[str]:
    """Aggiunge comandi ngspice per esportare tensioni e correnti transitorie."""
    current_vectors = list(device_current_vectors or [])
    if "tran" not in analyses or (not probe_nodes and not current_vectors):
        return []

    export_vectors = [
        *(f"v({node})" for node in probe_nodes),
        *current_vectors,
    ]
    control_save = []
    if current_vectors:
        # I parametri interni dei dispositivi non rientrano in `.save all`.
        # Senza questo salvataggio esplicito ngspice espone soltanto il loro
        # ultimo valore, che `wrdata` ripeterebbe per tutta la timeline.
        control_save.append(f"save all {' '.join(current_vectors)}")
    return [
        "",
        ".control",
        "set wr_singlescale",
        "set wr_vecnames",
        *control_save,
        "run",
        f"wrdata 08_tran.csv time {' '.join(export_vectors)}",
        ".endc",
    ]


def build_spice_netlist(
    component_rules: dict[str, Any],
    spice_models: dict[str, Any] | None = None,
    spice_models_source: str | Path | None = None,
) -> dict[str, Any]:
    """Costruisce il testo della netlist e un report compatto di emissione."""
    circuit_id = component_rules.get("circuit_id") or "unknown"
    lines = [
        f"* pipeline2.0 netlist",
        f"* circuit: {circuit_id}",
        "",
    ]
    warnings: list[str] = []
    informational_skips: list[str] = []
    measurement_points: list[dict[str, Any]] = []
    skipped: list[str] = []
    models: set[str] = set()
    transient_nodes: set[str] = set()
    transient_device_currents: set[str] = set()
    emitted_elements = 0

    for supply_name, supply in (component_rules.get("supplies") or {}).items():
        line, warning = emit_supply(str(supply_name), supply)
        if line:
            lines.append(line)
            emitted_elements += 1
            for node in supply.get("nodes") or []:
                if str(node) != "0":
                    transient_nodes.add(str(node))
        if warning:
            warnings.append(warning)

    for component_id, rule in (component_rules.get("components") or {}).items():
        line, model, warning = emit_component(str(component_id), rule)
        if rule.get("status") == "measurement_only":
            measurement_points.append({
                "component_id": str(component_id),
                "kind": rule.get("measurement_kind", "voltage"),
                "nodes": rule.get("nodes") or [],
                "emit_as": rule.get("emit_as"),
                "reason": rule.get("reason"),
            })
        if line:
            lines.append(line)
            if not line.startswith("*"):
                emitted_elements += 1
                emitted_name = line.split(maxsplit=1)[0]
                if emitted_name[:1].upper() == "D":
                    # `id` e' la corrente diretta del modello diodo. Esportare
                    # tutti i diodi mantiene generale la pipeline e permette al
                    # viewer di distinguere luce LED e semplice caduta diretta.
                    # I vettori interni richiamati dal linguaggio `.control`
                    # di ngspice usano il nome canonico in minuscolo.
                    transient_device_currents.add(f"@{emitted_name.lower()}[id]")
                for node in rule.get("nodes") or []:
                    if str(node) != "0":
                        transient_nodes.add(str(node))
        else:
            skipped.append(str(component_id))
            if rule.get("status") == "not_emitted":
                informational_skips.append(f"{component_id}: structural component not emitted")
            elif rule.get("status") == "measurement_only":
                informational_skips.append(f"{component_id}: voltage probe not emitted; read voltage between its nodes")
            elif rule.get("status") == "pin_aware":
                warnings.append(f"{component_id}: requires a device profile or dedicated model")
            elif rule.get("status") == "unsupported_for_now":
                warnings.append(f"{component_id}: class not yet supported by SPICE emit")
            elif rule.get("status") == "missing_parameters":
                warnings.append(f"{component_id}: missing parameters for SPICE emission")
            elif rule.get("status") == "invalid_node_order":
                warnings.append(f"{component_id}: incomplete nodes or invalid terminal order")
        if model:
            models.add(str(model))
        if warning:
            warnings.append(warning)

    resolved_models = resolve_model_entries(
        spice_models=spice_models,
        spice_models_source=spice_models_source,
        requested_models=models,
    )
    external_model_sources: list[dict[str, Any]] = []
    external_model_texts: list[tuple[str, str]] = []
    ngspice_defines: dict[str, str] = {}
    if models:
        lines.append("")
        for model in sorted(models):
            model_entry = resolved_models.get(model)
            if model_entry:
                source = model_entry.get("source")
                if isinstance(source, dict):
                    external_model_sources.append(dict(source))
                    external_model_texts.append((model, str(model_entry["text"])))
                else:
                    lines.append(str(model_entry["text"]))
                for define_name, define_value in (
                    model_entry.get("ngspice_defines") or {}
                ).items():
                    previous_value = ngspice_defines.get(str(define_name))
                    if previous_value is not None and previous_value != str(define_value):
                        raise ValueError(
                            f"Conflicting ngspice define {define_name}: "
                            f"{previous_value!r} vs {define_value!r}"
                        )
                    ngspice_defines[str(define_name)] = str(define_value)
            else:
                warnings.append(f"{model}: SPICE model not found in pipeline2_spice_models.yaml")
                lines.append(f"* missing model: {model}")
        if external_model_texts:
            lines.append(f'.include "{EXTERNAL_MODELS_BUNDLE_NAME}"')

    analysis_lines, analyses = build_analysis_lines(component_rules.get("simulation") or {})
    probe_nodes = sorted(transient_nodes)
    current_vectors = sorted(transient_device_currents, key=str.lower)
    control_lines = build_control_lines(analyses, probe_nodes, current_vectors)
    lines.extend(["", *analysis_lines, *control_lines, ".end"])

    report = {
        "circuit_id": circuit_id,
        "source_format": "pipeline2.0_spice_emit_report",
        "emitted_elements": emitted_elements,
        "skipped_elements": len(skipped),
        "skipped_components": skipped,
        "informational_skips": informational_skips,
        "measurement_points": measurement_points,
        "analyses": analyses,
        "transient_export": {
            "path": "08_tran.csv" if "tran" in analyses and (probe_nodes or current_vectors) else None,
            "nodes": probe_nodes if "tran" in analyses else [],
            "device_currents": current_vectors if "tran" in analyses else [],
        },
        "models": sorted(models),
        "warnings": warnings,
    }
    if external_model_sources:
        report["external_model_sources"] = external_model_sources
    if ngspice_defines:
        report["ngspice_defines"] = dict(sorted(ngspice_defines.items()))

    bundle_sections = [
        (
            f"* model: {model_name}\n"
            f"{model_text.rstrip()}"
        )
        for model_name, model_text in external_model_texts
    ]
    return {
        "netlist_text": "\n".join(lines) + "\n",
        "external_model_bundle_text": (
            "* pipeline2.0 external SPICE model bundle\n\n"
            + "\n\n".join(bundle_sections)
            + "\n"
            if bundle_sections
            else "* pipeline2.0 external SPICE model bundle: no external models\n"
        ),
        "report": report,
    }


def write_spice_outputs(
    output_dir: str | Path,
    component_rules: dict[str, Any],
    spice_models: dict[str, Any] | None = None,
    spice_models_source: str | Path | None = None,
) -> tuple[Path, dict[str, Any]]:
    """Scrive `07_netlist.cir` e restituisce il report di emissione."""
    output_path = Path(output_dir)
    result = build_spice_netlist(
        component_rules,
        spice_models=spice_models,
        spice_models_source=spice_models_source,
    )
    netlist_path = output_path / "07_netlist.cir"
    netlist_path.write_text(result["netlist_text"], encoding="utf-8")
    bundle_path = output_path / EXTERNAL_MODELS_BUNDLE_NAME
    bundle_path.write_text(result["external_model_bundle_text"], encoding="utf-8")
    return netlist_path, result["report"]
