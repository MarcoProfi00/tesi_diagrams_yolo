"""Parsing e metriche pure per confrontare run SPICE base e scenario."""

from __future__ import annotations

import csv
from pathlib import Path
import re

from scenario_expectations import COMPARISON_TOLERANCE


def normalize_quantity_name(name: str) -> str:
    """Normalizza una grandezza, incluse tensioni differenziali tra due nodi."""
    text = str(name).strip()
    if re.search(r"(?i)#branch$", text) and "(" not in text:
        return f"i({text})"
    match = re.match(r"(?i)^([vip])\(([^)]+)\)$", text)
    if not match:
        return text
    kind = match.group(1).lower()
    target = match.group(2).strip()
    if kind == "v":
        # La forma v(N1,N2) viene resa canonica eliminando gli spazi tra i nodi.
        voltage_nodes = [node.strip().upper() for node in target.split(",")]
        return f"v({','.join(voltage_nodes)})"
    return f"{kind}({target})"


def quantity_lookup_key(name: str) -> str:
    """Crea una chiave case-insensitive per confrontare grandezze SPICE."""
    return normalize_quantity_name(name).lower()


def parse_float(text: str) -> float | None:
    """Converte una stringa SPICE in float quando possibile."""
    try:
        return float(text)
    except ValueError:
        return None


def parse_ngspice_stdout(stdout_path: Path) -> dict[str, float]:
    """
    Estrae valori principali da uno stdout ngspice `.op`.

    Supporta:
    - tensioni nodo: `v(N001)`;
    - correnti sorgenti: `i(vvcc#branch)`;
    - correnti/potenze dispositivi nelle tabelle: `i(Rlamp13_1)`, `p(Rlamp13_1)`.
    """
    if not stdout_path.exists():
        return {}

    values: dict[str, float] = {}
    lines = stdout_path.read_text(encoding="utf-8", errors="replace").splitlines()
    in_node_table = False
    in_source_table = False
    current_devices: list[str] = []

    for raw_line in lines:
        line = raw_line.strip()
        lower = line.lower()

        if not line:
            # ngspice spesso lascia una riga vuota tra l'intestazione e i dati
            # delle tabelle, quindi non chiudiamo la sezione su una riga vuota.
            continue

        if lower.startswith("node") and "voltage" in lower:
            in_node_table = True
            in_source_table = False
            current_devices = []
            continue

        if lower.startswith("source") and "current" in lower:
            in_source_table = True
            in_node_table = False
            current_devices = []
            continue

        if set(line.replace("\t", "").replace(" ", "")) <= {"-"}:
            continue

        parts = line.split()
        if len(parts) < 2:
            continue

        if parts[0].lower() == "device":
            current_devices = parts[1:]
            in_node_table = False
            in_source_table = False
            continue

        if in_node_table:
            value = parse_float(parts[-1])
            if value is not None:
                values[quantity_lookup_key(f"v({parts[0]})")] = value
            continue

        if in_source_table:
            value = parse_float(parts[-1])
            if value is not None:
                source_name = parts[0]
                values[quantity_lookup_key(f"i({source_name})")] = value
            continue

        if current_devices and len(parts) == len(current_devices) + 1:
            property_name = parts[0].lower()
            for device_name, value_text in zip(current_devices, parts[1:]):
                value = parse_float(value_text)
                if value is None:
                    continue
                if property_name in {"i", "id"}:
                    values[quantity_lookup_key(f"i({device_name})")] = value
                elif property_name == "p":
                    values[quantity_lookup_key(f"p({device_name})")] = value

    return values


def count_ngspice_stderr_warnings(stderr_path: Path) -> float | None:
    """
    Conta i warning nello stderr ngspice.

    Serve per scenari che vogliono verificare se una modifica riduce problemi
    numerici, per esempio `singular matrix`. Restituiamo un numero per riusare
    lo stesso confronto base/scenario gia usato per tensioni e correnti.
    """
    if not stderr_path.exists():
        return None

    lines = stderr_path.read_text(encoding="utf-8", errors="replace").splitlines()
    warning_count = 0
    for line in lines:
        if line.strip().lower().startswith("warning:"):
            warning_count += 1
    return float(warning_count)


def is_voltage_quantity(quantity: str) -> bool:
    """Riconosce tensioni `v(N1)` e tensioni differenziali `v(N1,N2)`."""
    return voltage_quantity_nodes(quantity) is not None


def is_internal_device_current_quantity(quantity: str) -> bool:
    """Riconosce una corrente interna diodo/LED esportata da ngspice nel CSV."""
    normalized = normalize_quantity_name(quantity)
    return bool(re.fullmatch(r"@[^\s\[\]]+\[id\]", normalized, flags=re.IGNORECASE))


def voltage_quantity_nodes(quantity: str) -> tuple[str, ...] | None:
    """Estrae uno o due nodi da una grandezza di tensione SPICE valida."""
    normalized = normalize_quantity_name(quantity)
    match = re.fullmatch(r"(?i)v\(([^)]+)\)", normalized)
    if not match:
        return None
    nodes = tuple(node.strip().upper() for node in match.group(1).split(","))
    if len(nodes) not in {1, 2} or any(not node for node in nodes):
        return None
    return nodes


def is_stderr_quantity(quantity: str) -> bool:
    """Riconosce richieste di confronto sui warning stderr."""
    return quantity.strip().lower() in {"stderr", "ngspice_stderr", "stderr_warnings", "warning_count"}


def parse_tran_csv_metrics(
    csv_path: Path,
    requested_quantities: list[str] | None = None,
) -> dict[str, dict[str, float]]:
    """
    Estrae metriche semplici dal CSV transitorio pulito.

    Per ogni colonna numerica calcoliamo:
    - min
    - max
    - mean
    - vpp
    - final
    - abs_peak

    Per le richieste `v(N1,N2)` calcoliamo prima, campione per campione,
    `v(N1) - v(N2)`. Questo evita l'errore di sottrarre due Vpp gia aggregati.
    """
    if not csv_path.exists():
        return {}

    try:
        with csv_path.open(encoding="utf-8", newline="") as handle:
            reader = csv.DictReader(handle)
            rows = list(reader)
    except (OSError, csv.Error):
        return {}

    if not rows:
        return {}

    differential_columns: dict[str, tuple[str, str]] = {}
    for quantity in requested_quantities or []:
        nodes = voltage_quantity_nodes(str(quantity))
        if nodes is None or len(nodes) != 2:
            continue
        output_key = quantity_lookup_key(str(quantity))
        differential_columns[output_key] = (
            f"v({nodes[0].lower()})",
            f"v({nodes[1].lower()})",
        )

    values_by_column: dict[str, list[float]] = {}
    for row in rows:
        row_values: dict[str, float] = {}
        for column_name, value_text in row.items():
            if column_name is None:
                continue
            column_key = column_name.strip().lower()
            if not column_key or column_key == "time":
                continue
            value = parse_float(str(value_text).strip())
            if value is None:
                continue
            values_by_column.setdefault(column_key, []).append(value)
            row_values[column_key] = value

        # La differenza usa soltanto campioni in cui entrambe le tensioni sono
        # presenti, preservando l'allineamento temporale delle due colonne.
        for output_key, (positive_key, negative_key) in differential_columns.items():
            if positive_key not in row_values or negative_key not in row_values:
                continue
            values_by_column.setdefault(output_key, []).append(
                row_values[positive_key] - row_values[negative_key]
            )

    metrics: dict[str, dict[str, float]] = {}
    for column_key, values in values_by_column.items():
        if not values:
            continue
        minimum = min(values)
        maximum = max(values)
        mean = sum(values) / len(values)
        metrics[column_key] = {
            "min": minimum,
            "max": maximum,
            "mean": mean,
            "vpp": maximum - minimum,
            # `final` serve alle misure OP prive della tabella stdout;
            # `abs_peak` conserva l'evidenza di attivazione transitoria.
            "final": values[-1],
            "abs_peak": max(abs(minimum), abs(maximum)),
        }

    return metrics


def classify_change(base_value: float | None, scenario_value: float | None) -> str:
    """Classifica una variazione semplice tra base e scenario."""
    if base_value is None or scenario_value is None:
        return "missing"
    if (
        abs(base_value) < COMPARISON_TOLERANCE
        and abs(scenario_value) >= COMPARISON_TOLERANCE
    ):
        return "activated"
    if (
        abs(base_value) >= COMPARISON_TOLERANCE
        and abs(scenario_value) < COMPARISON_TOLERANCE
    ):
        return "deactivated"
    if abs(scenario_value - base_value) < COMPARISON_TOLERANCE:
        return "unchanged"
    return "changed"
