"""Creazione degli identificativi pubblici usati nel JSON finale dello step 05."""


def normalize_class_name(class_name: str) -> str:
    """Normalizza il nome classe per usarlo in una chiave semplice."""
    class_name = str(class_name or "component").strip().lower()
    class_name = class_name.replace(" ", "_")
    return class_name


def make_simple_component_id(instance_id: str, class_name: str) -> str:
    """Costruisce l'id componente del JSON finale, ad esempio mosfet16.2."""
    return f"{normalize_class_name(class_name)}{instance_id}"


def normalize_public_terminal_id(value: str) -> str:
    """
    Normalizza un id terminale mantenendo le maiuscole semantiche.

    Esempio: 16.2:G -> 16.2_G. Non convertiamo in lowercase per non perdere
    ruoli come G/S/D, B/C/E, VCC, GND.
    """
    value = str(value or "").strip()
    value = value.replace(":", "_")
    value = value.replace(" ", "")
    return value


def get_preferred_terminal_public_id(term: dict) -> str:
    """
    Recupera l'id piu' semantico disponibile per un terminale.

    Priorita':
      1. display_terminal_id;
      2. semantic_terminal_id;
      3. terminal_id;
      4. fallback instance_id:name.
    """
    return (
        term.get("display_terminal_id")
        or term.get("semantic_terminal_id")
        or term.get("terminal_id")
        or f"{term.get('instance_id', 'unknown')}:{term.get('name', 't')}"
    )


def get_preferred_terminal_public_name(term: dict) -> str:
    """
    Restituisce il nome corto migliore del terminale prodotto dallo step 03.

    Priorita':
      1. display_name;
      2. semantic_terminal_name;
      3. name;
      4. "t".
    """
    return (
        term.get("display_name")
        or term.get("semantic_terminal_name")
        or term.get("name")
        or "t"
    )


def make_simple_terminal_key(term: dict) -> str:
    """
    Costruisce la chiave del grafo finale.

    Esempi:
      - display_terminal_id = 16.2:G       -> mosfet16.2_G
      - display_terminal_id = 2.1:positive -> battery2.1_positive
      - display_terminal_id assente        -> resistor22.1_t1
    """
    class_name = normalize_class_name(term.get("component_class_name"))
    public_terminal_id = normalize_public_terminal_id(
        get_preferred_terminal_public_id(term)
    )
    return f"{class_name}{public_terminal_id}"


def build_simple_id_map(terminals: list[dict]):
    """Costruisce la mappa terminal_id interno -> id pubblico semplice."""
    original_to_simple = {}
    for term in terminals:
        original_to_simple[term["terminal_id"]] = make_simple_terminal_key(term)
    return original_to_simple


def build_simple_terminal_graph(terminal_graph: dict, original_to_simple: dict):
    """Converte il grafo interno in un dizionario leggibile per l'output."""
    public_graph = {}

    for original_source_id, original_target_ids in terminal_graph.items():
        public_source_id = original_to_simple.get(original_source_id, original_source_id)
        public_target_ids = [original_to_simple.get(target_id, target_id) for target_id in original_target_ids]
        public_graph[public_source_id] = sorted(set(public_target_ids))

    public_graph = {key: public_graph[key] for key in sorted(public_graph.keys())}
    return public_graph


def build_simple_list(values: list[str], original_to_simple: dict):
    """Converte una lista di id interni in una lista di id pubblici."""
    return sorted([original_to_simple.get(v, v) for v in values])
