#DEBUG / VISUALIZATION
SAVE_DEBUG_IMAGES = True
TERMINAL_RADIUS = 6

# COARSE SIDE SAMPLING
SIDE_SAMPLE_THICKNESS = 10
SIDE_CENTER_RATIO = 0.35
SIDE_SCORE_MIN_PIXELS = 5
AXIS_SCORE_MARGIN = 1.15


# GENERIC TERMINAL GEOMETRY
TERMINAL_OUTWARD_OFFSET = 4
ASPECT_RATIO_THRESHOLD = 1.10

# LOCAL PROBES FOR GENERIC TWO-TERMINAL COMPONENTS
TERMINAL_PROBE_OUT_LEN = 12
TERMINAL_PROBE_INSET = 2
TERMINAL_PROBE_HALFSPAN_RATIO = 0.22
TERMINAL_PROBE_HALFSPAN_MIN = 3
TERMINAL_PROBE_HALFSPAN_MAX = 8
TERMINAL_PROBE_AXIS_MARGIN = 1.12
TERMINAL_PROBE_MIN_SIDE_SCORE = 3

SWITCH_ANCHOR_RATIOS = (0.30, 0.50, 0.70)

# SPECIAL HEURISTICS FOR CLASS "Terminal"
# Probe locali vicini al bbox
TERMINAL_CLASS_PROBE_OUT_LEN = 10
TERMINAL_CLASS_PROBE_HALFSPAN_RATIO = 0.16
TERMINAL_CLASS_PROBE_HALFSPAN_MIN = 2
TERMINAL_CLASS_PROBE_HALFSPAN_MAX = 4

# =========================================================
# LED - STIMA ORIENTAZIONE
# =========================================================
# Per il LED i probe generici possono essere disturbati dalle frecce luminose.
# Usiamo quindi probe più stretti e centrati, così leggiamo soprattutto
# le vere connessioni e meno la grafica laterale del simbolo.
LED_PROBE_OUT_LEN = 12
LED_PROBE_INSET = 1

LED_PROBE_HALFSPAN_RATIO = 0.10
LED_PROBE_HALFSPAN_MIN = 2
LED_PROBE_HALFSPAN_MAX = 5

LED_CENTER_BAND_RATIO = 0.22
LED_MIN_SIDE_SCORE = 3
LED_AXIS_MARGIN = 1.15
# Probe "far" per il LED:
# servono a distinguere i veri wire esterni dalle frecce del simbolo
LED_FAR_GAP = 3
LED_FAR_LEN = 10
LED_FAR_WEIGHT = 1.0

LED_FAR_MIN_SIDE_SCORE = 2
LED_NEAR_FAR_AXIS_MARGIN = 1.10

# Decisione 1-vs-2 terminali
TERMINAL_CLASS_TWO_SIDE_MIN = 5
TERMINAL_CLASS_ONE_SIDE_MIN = 3
TERMINAL_CLASS_TWO_AXIS_MARGIN = 1.35
TERMINAL_CLASS_TWO_BALANCE_RATIO = 0.60

# Bias per porte esterne / terminali vicino al bordo immagine
TERMINAL_CLASS_BORDER_MARGIN = 14
TERMINAL_BORDER_MARGIN_RATIO = 0.04
TERMINAL_BORDER_MARGIN_MIN = 28

# Probe più lontani dal bbox per confermare continuità reale del wire
TERMINAL_CLASS_FAR_GAP = 3
TERMINAL_CLASS_FAR_LEN = 10
TERMINAL_CLASS_FAR_MIN = 2

# 3 TERMINALI - STIMA DEL PATTERN DEI LATI
THREE_TERMINAL_ANCHOR_RATIOS = (0.22, 0.50, 0.78)
THREE_TERMINAL_MIN_SIDE_SCORE = 3

THREE_TERMINAL_TEMPLATES = {
    "left": ("left", "top", "bottom"),
    "right": ("right", "top", "bottom"),
    "top": ("top", "left", "right"),
    "bottom": ("bottom", "left", "right"),
}

# Per i 3-terminali il lato "singolo" (base/gate) di solito entra circa a metà lato,
# mentre gli altri due terminali stanno sull'asse ortogonale e molto spesso verso
# il lato opposto del simbolo.
#
# Per questo facciamo due cose distinte:
#   1. stimiamo PRIMA il lato singolo usando probe centrati
#   2. stimiamo POI i punti finali con una ricerca "biased" coerente con quel lato
THREE_TERMINAL_SINGLE_SIDE_MIN_SCORE = 3
THREE_TERMINAL_SINGLE_SIDE_MARGIN = 1.08

# 3 TERMINALI - LOCALIZZAZIONE FINE DEL PUNTO SUL LATO
THREE_TERMINAL_POINT_MODE = "three_terminal_structured"

SIDE_PEAK_SCAN_MARGIN_RATIO = 0.08
SIDE_PEAK_SCAN_MARGIN_MIN = 2

SIDE_PEAK_HALFSPAN_RATIO = 0.12
SIDE_PEAK_HALFSPAN_MIN = 2
SIDE_PEAK_HALFSPAN_MAX = 6

SIDE_PEAK_OUT_LEN = 12
SIDE_PEAK_INSET = 1

SIDE_PEAK_MIN_SCORE = 2
SIDE_PEAK_KEEP_RATIO = 0.85

# Nei 3-terminali:
# - il terminale "singolo" viene cercato in una banda centrale del suo lato
# - i due terminali opposti vengono cercati verso il lato opposto al terminale singolo
THREE_TERMINAL_SINGLE_SCAN_START_RATIO = 0.25
THREE_TERMINAL_SINGLE_SCAN_END_RATIO = 0.75

THREE_TERMINAL_OPPOSITE_NEAR_RATIO = 0.52
THREE_TERMINAL_OPPOSITE_FAR_RATIO = 0.96

# =========================================================
# MOSFET - STIMA DEL LATO SINGOLO
# =========================================================
# Per i Mosfet il lato singolo (gate) conviene stimarlo con probe
# molto stretti e quasi solo esterni al bbox, altrimenti il canale
# interno del simbolo falsifica facilmente i punteggi.
MOSFET_SINGLE_SIDE_OUT_LEN = 14
MOSFET_SINGLE_SIDE_INSET = 0

MOSFET_SINGLE_SIDE_HALFSPAN_RATIO = 0.10
MOSFET_SINGLE_SIDE_HALFSPAN_MIN = 2
MOSFET_SINGLE_SIDE_HALFSPAN_MAX = 5

MOSFET_SINGLE_SIDE_MIN_SCORE = 3
MOSFET_SINGLE_SIDE_MARGIN = 1.12

# Probe "far" per confermare che il lato singolo del Mosfet
# continua davvero come wire e non è solo testo / grafica vicina.
MOSFET_SINGLE_SIDE_FAR_GAP = 2
MOSFET_SINGLE_SIDE_FAR_LEN = 10
MOSFET_SINGLE_SIDE_FAR_WEIGHT = 1.0

# Nei Mosfet verticali del dataset il gate è quasi sempre laterale.
# Per distinguere left vs right usiamo anche una striscia INTERNA
# al bbox nella zona centrale del simbolo.
MOSFET_GATE_INSIDE_X_RATIO = 0.12
MOSFET_GATE_INSIDE_X_MIN = 3
MOSFET_GATE_CENTER_Y1_RATIO = 0.30
MOSFET_GATE_CENTER_Y2_RATIO = 0.70
MOSFET_GATE_INSIDE_WEIGHT = 0.55
MOSFET_FORCE_LATERAL_GATE = True
MOSFET_LATERAL_MARGIN = 1.10

# Validazione finale dell'orientazione del Mosfet tramite supporto locale
# attorno ai 3 terminali stimati.
MOSFET_POINT_SUPPORT_RADIUS = 4
MOSFET_ORIENTATION_VALIDATION_MARGIN = 1.18
MOSFET_SINGLE_TERMINAL_WEIGHT = 1.35

# =========================================================
# ROUND SOURCES / METERS - STIMA ORIENTAZIONE
# =========================================================
# Simboli rotondi: Signal_Source, Voltage_Source, Current_Source, Meter
# Usiamo probe stretti SOLO esterni al bbox e una conferma "far".
ROUND_SOURCE_PROBE_OUT_LEN = 12
ROUND_SOURCE_CENTER_BAND_RATIO = 0.18

ROUND_SOURCE_FAR_GAP = 3
ROUND_SOURCE_FAR_LEN = 10
ROUND_SOURCE_FAR_WEIGHT = 1.0

ROUND_SOURCE_MIN_SIDE_SCORE = 2
ROUND_SOURCE_AXIS_MARGIN = 1.10

# fallback su aspect ratio solo se il bbox non è quasi quadrato
ROUND_SOURCE_BBOX_RATIO_MARGIN = 1.12


# =========================================================
# OPERATIONAL AMPLIFIER
# =========================================================
OPAMP_POINT_MODE = "opamp_structured"

# Finestre di scansione per i terminali sul lato
# "upper/lower" quando i 2 input stanno su left/right
OPAMP_SLOT_UPPER_START_RATIO = 0.18
OPAMP_SLOT_UPPER_END_RATIO = 0.42

OPAMP_SLOT_LOWER_START_RATIO = 0.58
OPAMP_SLOT_LOWER_END_RATIO = 0.82

# "left/right" quando i 2 input stanno su top/bottom
OPAMP_SLOT_LEFT_START_RATIO = 0.18
OPAMP_SLOT_LEFT_END_RATIO = 0.42

OPAMP_SLOT_RIGHT_START_RATIO = 0.58
OPAMP_SLOT_RIGHT_END_RATIO = 0.82

# centro del lato, per output e supply opzionali
OPAMP_SLOT_CENTER_START_RATIO = 0.32
OPAMP_SLOT_CENTER_END_RATIO = 0.68

# scoring orientazione
OPAMP_DIRECTIONAL_OUTWARD = 12
OPAMP_DIRECTIONAL_INWARD = 1
OPAMP_DIRECTIONAL_HALFSPAN = 3

OPAMP_OUTPUT_WEIGHT = 1.20
OPAMP_ORIENTATION_MARGIN = 1.10

# attivazione pin opzionali
OPAMP_OPTIONAL_MIN_SCORE = 2

# attivazione pin opzionali opamp
OPAMP_AUX_MIN_STEM_LENGTH = 5
OPAMP_AUX_STRONG_STEM_LENGTH = 8
OPAMP_AUX_MAX_BORDER_GAP = 4

OPAMP_AUX_MIN_INTERNAL_SUPPORT = 5

OPAMP_AUX_EXTERNAL_OUT_LEN = 10
OPAMP_AUX_MIN_EXTERNAL_SUPPORT = 4

OPAMP_AUX_CENTER_START_RATIO = 0.36
OPAMP_AUX_CENTER_END_RATIO = 0.64
OPAMP_AUX_EDGE_SKIP_RATIO = 0.04
OPAMP_AUX_TOP_STRONG_STEM_LENGTH = 5
OPAMP_AUX_CENTER_TOLERANCE = 3

OPAMP_AUX_AXIS_LINE_LEN = 14
OPAMP_AUX_AXIS_MIN_SUPPORT = 5
OPAMP_AUX_SIDE_BRANCH_MIN_SUPPORT = 6
OPAMP_AUX_MIN_DIAG_SUPPORT = 4

# Seconda fase: dopo aver capito che l'aux esiste, rifiniamo il punto per
# riportarlo sul giunto interno opamp e non sul simbolo eventualmente collegato
# sopra/sotto (terminal, source, bubble, ecc.).
OPAMP_AUX_JUNCTION_REFINE_X_RADIUS = 4
OPAMP_AUX_JUNCTION_DIAG_RADIUS = 4
