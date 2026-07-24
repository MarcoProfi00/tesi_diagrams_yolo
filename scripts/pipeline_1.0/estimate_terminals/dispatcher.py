"""
Sceglie quale strategia usare in base ai metadati YAML della classe.

Il dispatcher non calcola direttamente tutti i punti terminali: decide quale
strategia chiamare, restituisce la definizione astratta dei terminali e passa al
processor le informazioni necessarie per stimare le coordinate reali.
"""
from .config import OPAMP_POINT_MODE, THREE_TERMINAL_POINT_MODE
from .geometry import geom_infer_orientation_from_bbox
from .strategies_basic import (
    detect_breaker_terminals,
    detect_two_terminal_orientation_capacitor,
    detect_two_terminal_orientation_led,
    detect_two_terminal_orientation_inductor,
    detect_two_terminal_orientation_resistor,
    detect_two_terminal_orientation_round_source,
    detect_two_terminal_orientation_variable_resistor,
    detect_switch_terminals,
    resolve_one_terminal_orientation,
    strategy_detect_connected_side,
    strategy_detect_two_terminal_orientation_generic,
    strategy_detect_two_terminal_orientation_switch,
)
from .strategies_terminal_class import detect_terminal_auto_one_or_two
from .strategies_three_terminal import strategy_detect_three_terminal_orientation
from .strategies_opamp import detect_opamp_terminals
from .strategies_connector import detect_connector_terminals
from .strategies_structured_symbols import (
    detect_analog_meter_terminals,
    detect_transformer_terminals,
)
from .strategies_integrated_circuit import detect_integrated_circuit_terminals
from .strategies_speaker import detect_speaker_terminals


# Estrae dalla sezione "orientations" dello yaml la definizione terminale
# corretta per l'orientazione scelta.
def _get_oriented_terminals(meta: dict, orientation: str):
    terminals_def = meta.get("orientations", {}).get(orientation)
    if terminals_def is None:
        raise ValueError(f"Nessuna definizione terminali per orientazione '{orientation}'")
    return terminals_def


# Stabilisce come sono localizzati i punti terminali, indipendentemente dal
# numero di terminali. Questa scelta dice al processor se usare centro bbox,
# side-peak, punto assoluto prodotto dalla strategia, logica opamp, ecc.
def resolve_terminal_point_mode(meta: dict):
    # Il metadata puo' forzare esplicitamente la modalita' di localizzazione.
    explicit_mode = meta.get("terminal_point_mode")
    if explicit_mode is not None:
        return explicit_mode

    # Altrimenti scegliamo una modalita' implicita tramite terminal_strategy e
    # class_name, cosi' il YAML resta piu' compatto per i casi standard.
    strategy = meta.get("terminal_strategy", "")
    class_name = meta.get("name", "")

    if strategy == "three_terminal_by_side_pattern":
        return THREE_TERMINAL_POINT_MODE

    if strategy == "opamp_by_orientation_and_optional_supply":
        return OPAMP_POINT_MODE

    if strategy == "connector_by_projection":
        return "bbox_side_center"

    if strategy in {"analog_meter_by_posts", "transformer_external_wires"}:
        return "strategy_absolute_point"

    if strategy == "integrated_circuit_wire_contacts":
        return "strategy_absolute_point"

    if strategy == "speaker_by_connected_side":
        return "strategy_absolute_point"

    if strategy in {
        "two_terminal_led",
        "two_terminal_variable_resistor",
        "one_terminal_by_orientation",
    }:
        return "two_terminal_side_peak"


    if class_name in {"LED", "Diode", "Push_Button"}:
        return "two_terminal_side_peak"

    return "bbox_side_center"


# Sceglie il risolutore giusto per l'orientazione dei componenti a 2 terminali perchè alcuni hanno una logica a parte
def _resolve_two_terminal_orientation(strategy: str, class_name: str, image_binary, bbox, default_orientation: str):
    # I componenti a due terminali sembrano simili, ma graficamente sono molto
    # diversi: resistenze, condensatori, LED, induttori e sorgenti rotonde hanno
    # tutti segnali visivi differenti per stimare l'asse di connessione.
    if strategy == "two_terminal_capacitor" or class_name in {"Capacitor", "Polarized_Capacitor"}:
        return detect_two_terminal_orientation_capacitor(
            image_binary,
            bbox,
            default_orientation=default_orientation,
        )

    if strategy == "two_terminal_switch" or class_name in {"Switch", "Push_Button"}:
        return strategy_detect_two_terminal_orientation_switch(
            image_binary,
            bbox,
            default_orientation=default_orientation,
        )

    if strategy == "two_terminal_led" or class_name == "LED":
        return detect_two_terminal_orientation_led(
            image_binary,
            bbox,
            default_orientation=default_orientation,
        )

    if class_name == "Diode":
        return strategy_detect_two_terminal_orientation_generic(
            image_binary,
            bbox,
            default_orientation=default_orientation,
        )

    if class_name == "Inductor":
        return detect_two_terminal_orientation_inductor(
            image_binary,
            bbox,
            default_orientation=default_orientation,
        )

    if class_name == "Resistor":
        return detect_two_terminal_orientation_resistor(
            image_binary,
            bbox,
            default_orientation=default_orientation,
        )

    if (
        strategy == "two_terminal_round_source"
        or class_name in {"Signal_Source", "Voltage_Source", "Current_Source", "Meter"}
    ):
        return detect_two_terminal_orientation_round_source(
            image_binary,
            bbox,
            default_orientation=default_orientation,
        )

    if strategy == "two_terminal_variable_resistor" or class_name == "Variable_Resistor":
        return detect_two_terminal_orientation_variable_resistor(
            image_binary,
            bbox,
            default_orientation=default_orientation,
        )

    return strategy_detect_two_terminal_orientation_generic(
        image_binary,
        bbox,
        default_orientation=default_orientation,
    )


# =========================================================
# DISPATCHER DELLE STRATEGIE
# =========================================================
# Restituisce la definizione astratta dei terminali e l'orientazione tramite metadata
def get_terminals_definition(meta: dict, bbox, image_binary=None):
    strategy = meta.get("terminal_strategy", "fixed")

    # fixed -> nessuna stima geometrica: il metadata contiene gia' la lista
    # terminali completa e il processor usera' i lati indicati.
    if strategy == "fixed":
        return meta.get("terminals", []), None, None, None

    # auto_by_aspect_ratio -> orientazione dedotta dal rapporto altezza/larghezza
    # del bbox, con eccezione Transformer che preferisce una lettura grafica.
    if strategy == "auto_by_aspect_ratio":
        class_name = meta.get("name", "")
        default_orientation = meta.get("default_orientation", "horizontal")

        if image_binary is not None and class_name == "Transformer":
            orientation, side_scores = strategy_detect_two_terminal_orientation_generic(
                image_binary,
                bbox,
                default_orientation=default_orientation,
            )
            return _get_oriented_terminals(meta, orientation), orientation, None, side_scores

        orientation = geom_infer_orientation_from_bbox(
            bbox,
            default_orientation=default_orientation,
        )
        return _get_oriented_terminals(meta, orientation), orientation, None, None

    # one_terminal_by_orientation -> componenti con un solo terminale effettivo:
    # si cerca il lato collegato e si sceglie l'orientazione corrispondente.
    if strategy == "one_terminal_by_orientation":
        if image_binary is None:
            raise ValueError("one_terminal_by_orientation richiede image_binary.")

        if meta.get("name") == "GND":
            default_orientation = meta.get("default_orientation", "up")
            return _get_oriented_terminals(meta, default_orientation), default_orientation, "top", {
                "decision_mode": "gnd_fixed_top"
            }

        connected_side, side_scores = strategy_detect_connected_side(image_binary, bbox)

        if connected_side is not None:
            terminals_def, orientation = resolve_one_terminal_orientation(meta, connected_side)
            return terminals_def, orientation, connected_side, side_scores

        default_orientation = meta.get("default_orientation")
        if default_orientation is None:
            raise ValueError("Manca default_orientation per one_terminal_by_orientation.")

        return _get_oriented_terminals(meta, default_orientation), default_orientation, None, side_scores

    if strategy in {
        "two_terminal_by_connection_axis",
        "two_terminal_capacitor",
        "two_terminal_switch",
        "two_terminal_led",
        "two_terminal_round_source",
        "two_terminal_variable_resistor",
    }:
        # Famiglia dei componenti a due terminali. Prima scegliamo
        # l'orientazione, poi recuperiamo dal metadata i due terminali associati.
        if image_binary is None:
            raise ValueError(f"{strategy} richiede image_binary.")

        default_orientation = meta.get("default_orientation", "horizontal")
        class_name = meta.get("name", "")

        if class_name == "Breaker":
            terminals_def, orientation, side_scores = detect_breaker_terminals(
                image_binary,
                bbox,
            )
            if terminals_def is not None:
                return terminals_def, orientation, None, side_scores

        if class_name in {"Switch", "Push_Button"}:
            terminals_def, orientation, side_scores = detect_switch_terminals(
                image_binary,
                bbox,
                default_orientation=default_orientation,
            )
            if terminals_def is not None:
                return terminals_def, orientation, None, side_scores

        orientation, side_scores = _resolve_two_terminal_orientation(
            strategy=strategy,
            class_name=class_name,
            image_binary=image_binary,
            bbox=bbox,
            default_orientation=default_orientation,
        )

        return _get_oriented_terminals(meta, orientation), orientation, None, side_scores

    # terminal_auto_one_or_two -> classe terminal che può comportarsi come mono o bi terminale
    if strategy == "terminal_auto_one_or_two":
        # Il simbolo Terminal puo' rappresentare un singolo morsetto oppure un
        # piccolo passaggio a due contatti: la decisione dipende dai fili visibili.
        if image_binary is None:
            raise ValueError("terminal_auto_one_or_two richiede image_binary.")

        terminals_def, orientation, side_scores = detect_terminal_auto_one_or_two(
            image_binary,
            bbox,
        )
        return terminals_def, orientation, None, side_scores

    # integrated circuit
    if strategy == "integrated_circuit_wire_contacts":
        # IC: i terminali sono contatti/pin distribuiti sui lati del body.
        # La strategia produce punti assoluti, poi l'OCR dei pin li arricchisce.
        if image_binary is None:
            raise ValueError("integrated_circuit_wire_contacts richiede image_binary.")

        terminals_def, orientation, side_scores = detect_integrated_circuit_terminals(
            meta,
            image_binary,
            bbox,
        )
        return terminals_def, orientation, None, side_scores

    # connector
    if strategy == "connector_by_projection":
        # Connector: proietta i contatti lungo il bordo del connettore invece di
        # assumere semplicemente il centro dei lati.
        if image_binary is None:
            raise ValueError("connector_by_projection richiede image_binary.")

        default_orientation = meta.get("default_orientation", "vertical")
        terminals_def, orientation, side_scores = detect_connector_terminals(
            meta,
            image_binary,
            bbox,
            default_orientation=default_orientation,
        )
        return terminals_def, orientation, None, side_scores

    # analog meter
    if strategy == "analog_meter_by_posts":
        # Analog meter: cerca i due post esterni del simbolo, che non sempre
        # coincidono con i punti centrali del bbox.
        if image_binary is None:
            raise ValueError("analog_meter_by_posts richiede image_binary.")

        terminals_def, orientation, connected_side, side_scores = detect_analog_meter_terminals(
            image_binary,
            bbox,
        )
        return terminals_def, orientation, connected_side, side_scores

    # speaker
    if strategy == "speaker_by_connected_side":
        # Speaker: prima capisce da quale lato arrivano i fili, poi genera i due
        # terminali coerenti con quel lato collegato.
        if image_binary is None:
            raise ValueError("speaker_by_connected_side richiede image_binary.")

        terminals_def, orientation, connected_side, side_scores = detect_speaker_terminals(
            meta,
            image_binary,
            bbox,
        )
        return terminals_def, orientation, connected_side, side_scores

    # transformer
    if strategy == "transformer_external_wires":
        # Transformer: i terminali esterni possono trovarsi fuori dal corpo del
        # simbolo, quindi usa una strategia dedicata sui fili visibili.
        if image_binary is None:
            raise ValueError("transformer_external_wires richiede image_binary.")

        terminals_def, orientation, connected_side, side_scores = detect_transformer_terminals(
            image_binary,
            bbox,
        )
        return terminals_def, orientation, connected_side, side_scores

    # Operational Amplifier.
    if strategy == "opamp_by_orientation_and_optional_supply":
        # Opamp: identifica orientazione, ingressi/uscita obbligatori e pin di
        # alimentazione opzionali quando sono disegnati.
        if image_binary is None:
            raise ValueError("opamp_by_orientation_and_optional_supply richiede image_binary.")

        default_orientation = meta.get("default_orientation", "right")
        terminals_def, orientation, side_scores = detect_opamp_terminals(
            meta,
            image_binary,
            bbox,
            default_orientation=default_orientation,
        )
        return terminals_def, orientation, None, side_scores

    if strategy == "three_terminal_by_side_pattern":
        # Transistor/MOSFET: stima il lato singolo e la coppia laterale per
        # riconoscere una geometria a tre terminali.
        if image_binary is None:
            raise ValueError("three_terminal_by_side_pattern richiede image_binary.")

        default_orientation = meta.get("default_orientation", "right")
        class_name = meta.get("name", "")

        orientation, side_scores = strategy_detect_three_terminal_orientation(
            image_binary,
            bbox,
            class_name=class_name,
            default_orientation=default_orientation,
        )
        return _get_oriented_terminals(meta, orientation), orientation, None, side_scores

    raise ValueError(f"Strategia terminali non supportata: {strategy}")
