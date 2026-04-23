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