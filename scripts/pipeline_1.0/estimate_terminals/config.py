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

INDUCTOR_ELONGATED_RATIO = 2.0

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
# Finestra centrale per i point peak del LED:
# evita che bbox larghi catturino rail o testo laterale al posto del vero pin.
LED_SIDE_PEAK_AXIS_SCAN_RATIO = 0.46

# Decisione 1-vs-2 terminali
TERMINAL_CLASS_TWO_SIDE_MIN = 5
TERMINAL_CLASS_ONE_SIDE_MIN = 3
TERMINAL_CLASS_TWO_AXIS_MARGIN = 1.35
TERMINAL_CLASS_TWO_BALANCE_RATIO = 0.60
TERMINAL_CLASS_TWO_SIDE_RELAXED_MIN = 5
TERMINAL_CLASS_TWO_SIDE_RELAXED_STRONG = 40
TERMINAL_CLASS_TWO_SIDE_RELAXED_AXIS_MARGIN = 1.20
TERMINAL_CLASS_ADJACENT_TWO_SIDE_MIN = 70
TERMINAL_CLASS_ADJACENT_TWO_SIDE_STRONG = 90
TERMINAL_CLASS_ADJACENT_THIRD_MARGIN = 1.60
TERMINAL_CLASS_ADJACENT_LOCAL_MIN = 5

# Bias per porte esterne / terminali vicino al bordo immagine
TERMINAL_CLASS_BORDER_MARGIN = 14
TERMINAL_BORDER_MARGIN_RATIO = 0.04
TERMINAL_BORDER_MARGIN_MIN = 28

# Probe più lontani dal bbox per confermare continuità reale del wire
TERMINAL_CLASS_FAR_GAP = 3
TERMINAL_CLASS_FAR_LEN = 10
TERMINAL_CLASS_FAR_MIN = 2

# Pulizia locale del binary per la classe Terminal:
# manteniamo il core del pallino e, se serve, piccoli frammenti esterni
# ben allineati ai lati del terminale.
TERMINAL_CLASS_TEXT_SUPPRESS_MARGIN_RATIO = 0.45
TERMINAL_CLASS_TEXT_SUPPRESS_MARGIN_MIN = 8
TERMINAL_CLASS_SEED_INSET_RATIO = 0.22
TERMINAL_CLASS_SEED_MIN_SIZE = 8
TERMINAL_CLASS_EXTERNAL_KEEP_GAP = 16
TERMINAL_CLASS_EXTERNAL_KEEP_OVERLAP_RATIO = 0.25
TERMINAL_CLASS_EXTERNAL_MIN_LONG_SPAN = 5
TERMINAL_CLASS_EXTERNAL_LONG_TO_SHORT_RATIO = 1.5
TERMINAL_CLASS_POLARITY_MARKER_PROBE = 12
TERMINAL_CLASS_POLARITY_MARKER_MIN_CROSS_PIXELS = 2

# Pulizia locale del binary per simboli a un terminale:
# manteniamo il componente connesso al seed centrale del simbolo e
# scartiamo testo vicino ma scollegato.
ONE_TERMINAL_TEXT_SUPPRESS_ENABLE = True
ONE_TERMINAL_TEXT_SUPPRESS_MARGIN_RATIO = 0.45
ONE_TERMINAL_TEXT_SUPPRESS_MARGIN_MIN = 8
ONE_TERMINAL_TEXT_SUPPRESS_SEED_INSET_RATIO = 0.22
ONE_TERMINAL_TEXT_SUPPRESS_SEED_MIN_SIZE = 8
ONE_TERMINAL_TEXT_SUPPRESS_SEED_PAD = 2

# Pulizia locale del binary per simboli a due terminali:
# manteniamo il componente connesso al core del simbolo e, se serve,
# piccoli stub esterni coerenti con l'asse stimato.
TWO_TERMINAL_TEXT_SUPPRESS_ENABLE = True
TWO_TERMINAL_TEXT_SUPPRESS_MARGIN_RATIO = 0.45
TWO_TERMINAL_TEXT_SUPPRESS_MARGIN_MIN = 8
TWO_TERMINAL_TEXT_SUPPRESS_SEED_INSET_RATIO = 0.18
TWO_TERMINAL_TEXT_SUPPRESS_SEED_MIN_SIZE = 10
TWO_TERMINAL_TEXT_SUPPRESS_SEED_PAD = 2
TWO_TERMINAL_EXTERNAL_KEEP_GAP = 18
TWO_TERMINAL_EXTERNAL_KEEP_OVERLAP_RATIO = 0.25
TWO_TERMINAL_EXTERNAL_MIN_LONG_SPAN = 6
TWO_TERMINAL_EXTERNAL_LONG_TO_SHORT_RATIO = 1.5

# Bias geometrico per la classe Terminal
# Molto più conservativo: i terminali piccoli / quasi quadrati
# non devono essere spinti artificialmente verso top/bottom o left/right.
TERMINAL_CLASS_NEAR_SQUARE_RATIO = 1.28

TERMINAL_CLASS_SHAPE_RATIO_STRONG = 1.70
TERMINAL_CLASS_SHAPE_RATIO_WEAK = 1.45

TERMINAL_CLASS_SHAPE_BONUS_STRONG = 1.25
TERMINAL_CLASS_SHAPE_BONUS_WEAK = 0.60

# 3 TERMINALI - STIMA DEL PATTERN DEI LATI
THREE_TERMINAL_ANCHOR_RATIOS = (0.22, 0.50, 0.78)
THREE_TERMINAL_MIN_SIDE_SCORE = 3

THREE_TERMINAL_TEMPLATES = {
    "left": ("left", "top", "bottom"),
    "right": ("right", "top", "bottom"),
    "top": ("top", "left", "right"),
    "bottom": ("bottom", "left", "right"),
}
# 3 TERMINALI - VALIDAZIONE FINALE DELL'ORIENTAZIONE
THREE_TERMINAL_POINT_VALIDATION_ENABLE = True
THREE_TERMINAL_POINT_VALIDATION_MARGIN = 1.12
THREE_TERMINAL_POINT_VALIDATION_SINGLE_WEIGHT = 1.20

THREE_TERMINAL_AXIS_PREFILTER_ENABLE = True
THREE_TERMINAL_AXIS_PREFILTER_MARGIN = 1.05

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
MOSFET_ORIENTATION_VALIDATION_MARGIN = 1.10
MOSFET_SINGLE_TERMINAL_WEIGHT = 1.35
MOSFET_SINGLE_TERMINAL_ORTHOGONAL_PENALTY = 0.80

# I 3-terminali soffrono spesso per etichette tipo M1/Q2 vicine al bbox.
# Usiamo quindi una pulizia locale dei connected components per leggere
# orientazione e gate/base su un binary meno rumoroso.
THREE_TERMINAL_TEXT_SUPPRESS_ENABLE = True
THREE_TERMINAL_TEXT_SUPPRESS_MARGIN_RATIO = 0.55
THREE_TERMINAL_TEXT_SUPPRESS_MARGIN_MIN = 8
THREE_TERMINAL_TEXT_SUPPRESS_SEED_PAD = 2
THREE_TERMINAL_SEED_INSET_RATIO = 0.14
THREE_TERMINAL_SEED_MIN_SIZE = 12

# 3 TERMINALI - RISOLUZIONE SEMANTICA DEL RAMO CON FRECCIA
# Dopo aver trovato geometricamente i 3 terminali, campioniamo una piccola
# ROI dove cade di solito la freccia del ramo alto/basso o sinistro/destro.
THREE_TERMINAL_ARROW_BRANCH_NEAR_RATIO = 0.32
THREE_TERMINAL_ARROW_BRANCH_FAR_RATIO = 0.68
THREE_TERMINAL_ARROW_PAIR_FIRST_RATIO = 0.22
THREE_TERMINAL_ARROW_PAIR_SECOND_RATIO = 0.78
THREE_TERMINAL_ARROW_PROBE_HALFSPAN_X_RATIO = 0.12
THREE_TERMINAL_ARROW_PROBE_HALFSPAN_Y_RATIO = 0.10
THREE_TERMINAL_ARROW_PROBE_HALFSPAN_MIN = 3
THREE_TERMINAL_ARROW_CONFIDENCE_MIN = 0.10

# Per i MOSFET assegniamo S/D solo se il probe della freccia/ramo e'
# sufficientemente sbilanciato. Se l'evidenza e' debole, manteniamo solo G
# e lasciamo gli altri due morsetti come t2/t3.
MOSFET_ARROW_BRANCH_CONFIDENCE_MIN = 0.10

# NPN: fallback più vicino al trunk centrale per catturare la freccia
# dell'emitter quando il probe generico è ambiguo.
NPN_ARROW_BRANCH_TRUNK_LEFT_RATIO = 0.42
NPN_ARROW_BRANCH_TRUNK_RIGHT_RATIO = 0.58
NPN_ARROW_BRANCH_TOP_RATIO = 0.30
NPN_ARROW_BRANCH_BOTTOM_RATIO = 0.70

# Se il probe speciale per la base BJT sceglie un lato ma la validazione
# geometrica dei tre terminali preferisce chiaramente il lato opposto, non
# accettiamo l'override: spesso il conteggio interno viene disturbato dal
# ramo verticale collector/emitter vicino al bordo del bbox.
NPN_BASE_OVERRIDE_POINT_VETO_MARGIN = 1.08

# Se il probe dedicato della base BJT e' molto piu' forte su un lato,
# manteniamo quel lato anche quando la validazione geometrica e' disturbata
# da fili esterni o loop vicini al bbox.
NPN_BASE_OVERRIDE_STRONG_BASE_RATIO = 2.0

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

# Rifinitura del giunto aux: una volta scelto l'asse corretto,
# cerchiamo solo la y dell'incrocio con la diagonale.
OPAMP_AUX_REFINE_Y_MIN_RATIO = 0.16
OPAMP_AUX_REFINE_Y_MAX_RATIO = 0.78
OPAMP_AUX_REFINE_LOCAL_RADIUS = 2
OPAMP_AUX_MIN_SEGMENT_DENSITY = 0.10

# Run verticale aux: tolleranza a piccoli shift/gap del tratto verticale.
OPAMP_AUX_RUN_HALFSPAN = 2
OPAMP_AUX_RUN_GAP_TOLERANCE = 2

# Se entrambi gli aux sono attivi e quasi allineati, imponiamo un asse x comune.
OPAMP_AUX_AXIS_ALIGN_MAX_DELTA = 8


# ---------------------------------------------------------
# OPAMP RESET: fase 1 solo terminali obbligatori
# ---------------------------------------------------------
# La localizzazione di in1/in2/out usa probe stretti centrati sul bordo del bbox
# ma con peso quasi tutto fuori dal bbox, così i numeri e i simboli interni
# dell'opamp disturbano molto meno.
OPAMP_MANDATORY_OUTWARD_OFFSET = 8
OPAMP_MANDATORY_SCAN_HALFSPAN = 2
OPAMP_MANDATORY_OUTWARD_LEN = 14
OPAMP_MANDATORY_INWARD_LEN = 1
OPAMP_MANDATORY_FAR_GAP = 2
OPAMP_MANDATORY_FAR_LEN = 8
OPAMP_MANDATORY_FAR_WEIGHT = 0.75

OPAMP_MANDATORY_ROW_TOL = 1
OPAMP_MANDATORY_KEEP_RATIO = 0.92
OPAMP_MANDATORY_BORDER_WEIGHT = 0.35

# ---------------------------------------------------------
# OPAMP AUX V1: rilevamento strutturale dei pin di supply
# ---------------------------------------------------------
# Cerchiamo solo rami verticali connessi davvero al lato top/bottom
# del bbox nella banda centrale dell'opamp.
OPAMP_AUX_ENABLE_V1 = True

OPAMP_AUX_SCAN_X_START_RATIO = 0.32
OPAMP_AUX_SCAN_X_END_RATIO = 0.72

OPAMP_AUX_RUN_HALFSPAN = 1
OPAMP_AUX_RUN_MIN_FG = 1
OPAMP_AUX_RUN_MAX_GAP = 1
OPAMP_AUX_RUN_MAX_DEPTH_RATIO = 0.78
OPAMP_AUX_MIN_RUN_LENGTH = 10

# piccolo margine per non fermarci subito per antialiasing
OPAMP_AUX_EDGE_BAND_RATIO = 0.05

# ---------------------------------------------------------
# OPAMP AUX V2: refine del punto sul lato obliquo
# ---------------------------------------------------------
OPAMP_AUX_DIAG_RADIUS = 4
OPAMP_AUX_REFINE_MIN_DIAG_SUPPORT = 3
OPAMP_AUX_REFINE_MIN_SEGMENT_DENSITY = 0.12

# bande plausibili dove cercare il giunto con la diagonale
OPAMP_AUX_REFINE_TOP_START_RATIO = 0.16
OPAMP_AUX_REFINE_TOP_END_RATIO = 0.62

OPAMP_AUX_REFINE_BOTTOM_START_RATIO = 0.38
OPAMP_AUX_REFINE_BOTTOM_END_RATIO = 0.86

# ---------------------------------------------------------
# OPAMP AUX V3: refine locale della x dello stelo verticale
# ---------------------------------------------------------
OPAMP_AUX_X_REFINE_RADIUS = 8
OPAMP_AUX_X_KEEP_RATIO = 0.92
OPAMP_AUX_X_REFINE_HALFSPAN = 1
OPAMP_AUX_RUN_KEEP_RATIO = 0.92

# banda verticale dove misurare la densità dello stelo
OPAMP_AUX_X_REFINE_TOP_END_RATIO = 0.40
OPAMP_AUX_X_REFINE_BOTTOM_START_RATIO = 0.60

OPAMP_AUX_X_REFINE_MIN_DENSITY = 0.18


# ---------------------------------------------------------
# OPAMP AUX V4: maschera locale dei numeri interni (4, 5)
# usata SOLO nella refine degli auxiliary
# ---------------------------------------------------------
OPAMP_AUX_MASK_INTERNAL_LABELS = True

# box orizzontale dei numeri interni nel caso opamp "right"
OPAMP_AUX_MASK_X1_RATIO = 0.34
OPAMP_AUX_MASK_X2_RATIO = 0.58

# box del "4"
OPAMP_AUX_MASK_TOP_Y1_RATIO = 0.28
OPAMP_AUX_MASK_TOP_Y2_RATIO = 0.50

# box del "5"
OPAMP_AUX_MASK_BOTTOM_Y1_RATIO = 0.50
OPAMP_AUX_MASK_BOTTOM_Y2_RATIO = 0.72

# ---------------------------------------------------------
# OPAMP AUX V5: se sopra l'opamp c'e' un piccolo Terminal (Vcc/Vdd),
# per l'aux superiore preferiamo allinearci direttamente a quel punto.
# ---------------------------------------------------------
OPAMP_AUX_SNAP_TO_NEARBY_TERMINAL = True
OPAMP_AUX_NEARBY_TERMINAL_TOP_REGION_RATIO = 0.45

