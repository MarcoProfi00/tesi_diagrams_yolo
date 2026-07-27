"""Regressioni mirate per il recupero fili e i crossover della Pipeline 1.0."""

from __future__ import annotations

import importlib.util
import importlib
import json
from pathlib import Path
import subprocess
import sys
import unittest

import cv2
import numpy as np


PROJECT_ROOT = Path(__file__).resolve().parents[2]
PIPELINE1_DIR = PROJECT_ROOT / "scripts" / "pipeline_1.0"
STEP04_PATH = PIPELINE1_DIR / "04_extract_wires.py"
if str(PIPELINE1_DIR) not in sys.path:
    sys.path.insert(0, str(PIPELINE1_DIR))


def load_pipeline1_graph_functions():
    """Carica i moduli Pipeline 1.0 senza collisioni con gli omonimi Pipeline 2.0."""
    prefix = "build_terminal_graph"
    previous_modules = {
        name: module
        for name, module in list(sys.modules.items())
        if name == prefix or name.startswith(prefix + ".")
    }
    for name in previous_modules:
        sys.modules.pop(name, None)

    try:
        crossings = importlib.import_module("build_terminal_graph.crossings")
        return (
            crossings.split_looped_orthogonal_crossing_groups,
            crossings.is_symmetric_low_span_thick_hump,
            crossings.detect_radial_wire_crossings,
            crossings.split_bridge_labels,
        )
    finally:
        for name in list(sys.modules):
            if name == prefix or name.startswith(prefix + "."):
                sys.modules.pop(name, None)
        sys.modules.update(previous_modules)


(
    split_looped_orthogonal_crossing_groups,
    is_symmetric_low_span_thick_hump,
    detect_radial_wire_crossings,
    split_bridge_labels,
) = load_pipeline1_graph_functions()

from estimate_terminals.io_utils import img_build_foreground_binary
from estimate_terminals.strategies_basic import detect_two_terminal_orientation_capacitor


def load_step04_module():
    """Carica lo step 04 per testare le keep zone senza avviare la CLI."""
    spec = importlib.util.spec_from_file_location("pipeline1_step04_wiring", STEP04_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Impossibile caricare lo step 04: {STEP04_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class EvidenceKeepTests(unittest.TestCase):
    """Verifica che una keep zone lunga richieda pixel realmente visibili."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.step04 = load_step04_module()
        cls.terminals = [
            {
                "terminal_id": "lamp:t2",
                "instance_id": "lamp",
                "component_class_name": "Lamp",
                "relative_position": "bottom",
                "x": 50,
                "y": 20,
            },
            {
                "terminal_id": "gnd:t1",
                "instance_id": "gnd",
                "component_class_name": "GND",
                "relative_position": "top",
                "x": 50,
                "y": 180,
            },
        ]

    def test_visible_long_line_is_reopened_through_a_mask(self) -> None:
        """Una linea continua esistente viene preservata, non ricostruita."""
        gray = np.full((200, 100), 255, dtype=np.uint8)
        cv2.line(gray, (50, 20), (50, 180), 0, thickness=3)
        mask = np.full_like(gray, 255)

        carved, _ = self.step04.carve_terminal_keep_zones(
            mask,
            self.terminals,
            components=[],
            source_gray=gray,
        )

        self.assertEqual(int(carved[100, 50]), 0)

    def test_blank_gap_does_not_create_a_connection(self) -> None:
        """Terminali allineati senza filo restano separati al centro."""
        gray = np.full((200, 100), 255, dtype=np.uint8)
        mask = np.full_like(gray, 255)

        carved, _ = self.step04.carve_terminal_keep_zones(
            mask,
            self.terminals,
            components=[],
            source_gray=gray,
        )

        self.assertEqual(int(carved[100, 50]), 255)


class LoopedCrossingTests(unittest.TestCase):
    """Protegge la distinzione tra crossover ad arco e nodo ortogonale."""

    @staticmethod
    def terminals():
        """Crea quattro terminali ortogonali con identificativi generici."""
        return [
            {"terminal_id": "vertical_top", "relative_position": "bottom", "x": 60, "y": 20},
            {"terminal_id": "vertical_bottom", "relative_position": "top", "x": 60, "y": 100},
            {"terminal_id": "horizontal_left", "relative_position": "right", "x": 20, "y": 60},
            {"terminal_id": "horizontal_right", "relative_position": "left", "x": 100, "y": 60},
        ]

    @staticmethod
    def crossing_skeleton(with_loop: bool):
        """Disegna un incrocio normale oppure lo stesso incrocio con arco."""
        skeleton = np.zeros((120, 120), dtype=np.uint8)
        cv2.line(skeleton, (20, 60), (100, 60), 255, thickness=1)
        cv2.line(skeleton, (60, 20), (60, 100), 255, thickness=1)
        if with_loop:
            cv2.line(skeleton, (60, 48), (78, 60), 255, thickness=1)
            cv2.line(skeleton, (78, 60), (60, 72), 255, thickness=1)
        return skeleton

    def test_looped_crossing_is_split_into_orthogonal_pairs(self) -> None:
        """Il doppio arco separa il ramo verticale da quello orizzontale."""
        groups = split_looped_orthogonal_crossing_groups(
            {1: [term["terminal_id"] for term in self.terminals()]},
            self.terminals(),
            self.crossing_skeleton(with_loop=True),
        )

        actual = {frozenset(group) for group in groups.values()}
        self.assertEqual(
            actual,
            {
                frozenset({"vertical_top", "vertical_bottom"}),
                frozenset({"horizontal_left", "horizontal_right"}),
            },
        )

    def test_plain_crossing_remains_one_group(self) -> None:
        """Un nodo senza archi laterali non viene alterato dalla nuova regola."""
        groups = split_looped_orthogonal_crossing_groups(
            {1: [term["terminal_id"] for term in self.terminals()]},
            self.terminals(),
            self.crossing_skeleton(with_loop=False),
        )

        self.assertEqual(len(groups), 1)


class RadialCrossingTests(unittest.TestCase):
    """Verifica gli incroci a X senza assumere direzioni cardinali."""

    @staticmethod
    def crossing_skeleton():
        """Disegna due diagonali sottili che si intersecano al centro."""
        skeleton = np.zeros((160, 160), dtype=np.uint8)
        cv2.line(skeleton, (30, 30), (130, 130), 255, thickness=1)
        cv2.line(skeleton, (130, 30), (30, 130), 255, thickness=1)
        return skeleton

    @staticmethod
    def crossing_ink(with_dot: bool):
        """Crea l'inchiostro originale, con pallino centrale opzionale."""
        ink = np.zeros((160, 160), dtype=np.uint8)
        cv2.line(ink, (30, 30), (130, 130), 255, thickness=3)
        cv2.line(ink, (130, 30), (30, 130), 255, thickness=3)
        if with_dot:
            cv2.circle(ink, (80, 80), 10, 255, thickness=-1)
        return ink

    @classmethod
    def crossing_labels(cls):
        """Etichetta la X come singola connected component iniziale."""
        _, labels, _, _ = cv2.connectedComponentsWithStats(
            np.where(cls.crossing_skeleton() > 0, 1, 0).astype(np.uint8),
            connectivity=8,
        )
        return labels

    def test_diagonal_x_without_dot_is_detected(self) -> None:
        """Una X semplice genera un crossing radiale ad alta confidenza."""
        crossings = detect_radial_wire_crossings(
            self.crossing_skeleton(),
            self.crossing_labels(),
            self.crossing_ink(with_dot=False),
        )

        self.assertEqual(len(crossings), 1)
        self.assertEqual(len(crossings[0]["branch_directions"]), 4)
        self.assertEqual(len(crossings[0]["branch_pairs"]), 2)

    def test_diagonal_x_with_dot_remains_a_junction(self) -> None:
        """Un pallino esplicito impedisce lo split della stessa geometria."""
        crossings = detect_radial_wire_crossings(
            self.crossing_skeleton(),
            self.crossing_labels(),
            self.crossing_ink(with_dot=True),
        )

        self.assertEqual(crossings, [])

    def test_diagonal_x_is_split_into_straight_pairs(self) -> None:
        """Lo split completo conserva le due continuita' diagonali."""
        terminals = [
            {
                "terminal_id": terminal_id,
                "instance_id": terminal_id,
                "component_class_name": "Resistor",
                "x": x,
                "y": y,
            }
            for terminal_id, x, y in (
                ("north_west", 30, 30),
                ("north_east", 130, 30),
                ("south_west", 30, 130),
                ("south_east", 130, 130),
            )
        ]
        terminal_match_debug = {
            term["terminal_id"]: {
                "matched_label": 1,
                "snap_point": [term["x"], term["y"]],
            }
            for term in terminals
        }

        groups = split_bridge_labels(
            {1: [term["terminal_id"] for term in terminals]},
            terminals,
            terminal_match_debug,
            self.crossing_skeleton(),
            self.crossing_labels(),
            wire_extraction={},
        )

        actual = {frozenset(group) for group in groups.values()}
        self.assertEqual(
            actual,
            {
                frozenset({"north_west", "south_east"}),
                frozenset({"north_east", "south_west"}),
            },
        )


class C01RegressionTests(unittest.TestCase):
    """Protegge orientazione condensatori e filtro dei falsi ponti di c01."""

    @classmethod
    def setUpClass(cls) -> None:
        image_path = (
            PROJECT_ROOT
            / "data"
            / "batchPipeline2.0"
            / "batchChatAgentEvaluation"
            / "c01.jpg"
        )
        image = cv2.imread(str(image_path))
        if image is None:
            raise RuntimeError(f"Immagine di regressione non leggibile: {image_path}")
        cls.binary = img_build_foreground_binary(image)

    def test_both_capacitors_use_horizontal_terminals(self) -> None:
        """Le due coppie di piastre verticali devono produrre pin left/right."""
        capacitor_bboxes = (
            [274.93, 113.39, 328.2, 160.71],
            [653.57, 426.51, 704.87, 476.56],
        )
        for bbox in capacitor_bboxes:
            orientation, debug = detect_two_terminal_orientation_capacitor(
                self.binary,
                bbox,
            )
            self.assertEqual(orientation, "horizontal", msg=debug)

    def test_symmetric_low_span_hump_is_rejected(self) -> None:
        """I due bordi simmetrici della giunzione d'uscita non sono ponti."""
        self.assertTrue(
            is_symmetric_low_span_thick_hump({
                "bridge_detector": "thick_hump",
                "skeleton_y_span": 1,
                "left_pixels": 104,
                "right_pixels": 103,
            })
        )

    def test_real_hump_with_vertical_shape_is_preserved(self) -> None:
        """Il ponte R6/pin 7 ha sviluppo verticale e deve sopravvivere."""
        self.assertFalse(
            is_symmetric_low_span_thick_hump({
                "bridge_detector": "thick_hump",
                "skeleton_y_span": 11,
                "left_pixels": 201,
                "right_pixels": 176,
            })
        )


class C02TopologyRegressionTests(unittest.TestCase):
    """Protegge la separazione delle due reti incrociate di c02."""

    def test_c02_diagonal_crossing_produces_two_distinct_nets(self) -> None:
        """Il processor deve associare ciascuna base al ramo diagonale giusto."""
        step04_path = (
            PROJECT_ROOT
            / "outputs"
            / "demo_workspaces"
            / "chat_agent_evaluation"
            / "pipeline1.0"
            / "04_extract_wires"
            / "c02.json"
        )
        script = (
            "import json,sys\n"
            "from pathlib import Path\n"
            "sys.path.insert(0, sys.argv[1])\n"
            "from build_terminal_graph.processor import build_terminal_graph_for_image\n"
            "data=json.loads(Path(sys.argv[2]).read_text(encoding='utf-8'))\n"
            "result=build_terminal_graph_for_image(data)\n"
            "print(json.dumps({'graph': result['graph'], 'warnings': result['warnings']}))\n"
        )
        completed = subprocess.run(
            [
                sys.executable,
                "-B",
                "-c",
                script,
                str(PIPELINE1_DIR),
                str(step04_path),
            ],
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=False,
        )
        self.assertEqual(completed.returncode, 0, msg=completed.stderr)
        actual = json.loads(completed.stdout)
        graph = actual["graph"]

        q1_net = {
            "npn_transistor18.1_B",
            *graph["npn_transistor18.1_B"],
        }
        q2_net = {
            "npn_transistor18.2_B",
            *graph["npn_transistor18.2_B"],
        }
        self.assertEqual(
            q1_net,
            {
                "npn_transistor18.1_B",
                "polarized_capacitor20.2_negative",
                "resistor22.3_t2",
            },
        )
        self.assertEqual(
            q2_net,
            {
                "npn_transistor18.2_B",
                "polarized_capacitor20.1_negative",
                "resistor22.2_t2",
            },
        )
        self.assertTrue(q1_net.isdisjoint(q2_net))
        self.assertEqual(actual["warnings"]["unconnected_terminals"], [])
        self.assertEqual(actual["warnings"]["unmatched_terminals"], [])


class B03TopologyRegressionTests(unittest.TestCase):
    """Blocca ogni variazione del wiring B03 gia' validato per la demo."""

    def test_b03_complete_graph_stays_identical(self) -> None:
        """Il processor corrente deve riprodurre archi e warning approvati."""
        step04_path = (
            PROJECT_ROOT
            / "outputs"
            / "demo_workspaces"
            / "demo_batch"
            / "pipeline1.0"
            / "04_extract_wires"
            / "b03.json"
        )
        expected_path = (
            PROJECT_ROOT
            / "outputs"
            / "pipeline1.0"
            / "batchB"
            / "05_build_terminal_graph"
            / "b03.json"
        )
        expected = json.loads(expected_path.read_text(encoding="utf-8"))

        # Lo step reale gira in un processo separato. Facciamo lo stesso nel
        # test per evitare collisioni con il package omonimo della Pipeline 2.0.
        script = (
            "import json,sys\n"
            "from pathlib import Path\n"
            "sys.path.insert(0, sys.argv[1])\n"
            "from build_terminal_graph.processor import build_terminal_graph_for_image\n"
            "data=json.loads(Path(sys.argv[2]).read_text(encoding='utf-8'))\n"
            "result=build_terminal_graph_for_image(data)\n"
            "print(json.dumps({'graph': result['graph'], 'warnings': result['warnings']}))\n"
        )
        completed = subprocess.run(
            [
                sys.executable,
                "-B",
                "-c",
                script,
                str(PIPELINE1_DIR),
                str(step04_path),
            ],
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=False,
        )
        self.assertEqual(completed.returncode, 0, msg=completed.stderr)
        actual = json.loads(completed.stdout)

        self.assertEqual(actual["graph"], expected["graph"])
        self.assertEqual(actual["warnings"], expected["warnings"])


if __name__ == "__main__":
    unittest.main()
