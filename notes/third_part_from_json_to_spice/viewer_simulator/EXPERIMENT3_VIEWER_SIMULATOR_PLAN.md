# Experiment 3 - Viewer visuale Pipeline 2.0

Questo documento registra l'architettura realizzata e la chiusura operativa
dell'Experiment 3.

Lo stato dell'arte e mantenuto nel file dedicato:

```text
notes/third_part_from_json_to_spice/viewer_simulator/stato_dell_arte_spice_to_viewer.md
```

Stato: concluso sul Batch A per `a01`, `a02`, `a04`-`a10`; `a03` resta fuori
dalla prima fase per il suo caso topologico/SPICE non stabile.

## Obiettivo

Costruire un viewer visuale integrato nella web chat per ogni run della
Pipeline 2.0:

- base run;
- scenario run;
- scenari topologici;
- scenari non topologici.

Il viewer deve mostrare il circuito equivalente della run selezionata, non
ricostruire pixel-perfect lo schematico originale.

Principio guida:

```text
viewer = netlist-grounded + image-guided
```

Quindi:

- `07_netlist.cir` e `08_*` sono la verita elettrica;
- `03_node_map.json` e `06_component_rules.json` aggiungono struttura utile;
- Pipeline 1.0 fornisce bbox, terminali e orientamento come geometry seed;
- ogni scenario produce il viewer della propria run.

## Input Da Usare

Per ogni base run o scenario run:

```text
03_node_map.json
06_component_rules.json
07_netlist.cir
08_ngspice_stdout.txt
08_tran.csv                  # se presente
scenario.json                # solo scenario
scenario_comparison.json     # solo scenario
```

Geometry seed da Pipeline 1.0:

```text
outputs/pipeline1.0/<batch>/03_estimate_terminals/<circuit>.json
outputs/pipeline1.0/<batch>/05_build_terminal_graph/<circuit>.json
outputs/pipeline1.0/<batch>/06_graph_report/<circuit>/<circuit>.json
```

`03_estimate_terminals` e il file piu importante per il layout, perche contiene:

```text
bbox
instance_id
class_name
estimated_orientation
terminali x/y
relative_position
stato switch, quando riconosciuto
```

## Architettura Script

```text
13_build_viewer_model.py
  -> cosa esiste nella run

14_build_viewer_layout.py
  -> dove posizionare componenti, terminali e collegamenti

15_render_viewer_svg.py
  -> come disegnare SVG con vocabolario componenti

09_web_chat.py
  -> genera/carica e mostra il viewer della run selezionata
```

## Decisioni

- `09_web_chat.py` non deve contenere logica specifica di `a01`.
- Non vanno creati renderer dedicati tipo `render_a02`, `render_a09`, ecc.
- Le coordinate immagine non sono la verita elettrica: sono solo seed di layout.
- La netlist della run resta la sorgente di verita.
- I componenti scenario senza bbox vanno posizionati vicino ai nodi coinvolti.
- Ogni nuovo circuito deve migliorare regole generali, non aggiungere codice
  specifico.

## Implementazione Realizzata

1. **`09_web_chat.py` come orchestratore leggero**

   `09` resta:

   ```text
   server web
   chat diagnostica
   selettore base/scenario
   caricamento o generazione viewer della run attiva
   ```

   Per una base run o scenario run invoca gli step `13`, `14` e `15` solo se
   l'artefatto e assente o non aggiornato.

2. **`13_build_viewer_model.py`**

   Il `13_viewer_model.json` contiene:

   ```text
   componenti SPICE da 07_netlist.cir
   componenti strutturali da 03_node_map/06_component_rules
   nodi e connessioni
   stato switch
   componenti scenario
   misure OP/TRAN
   geometry_seed da Pipeline 1.0
   ```

3. **`14_build_viewer_layout.py` image-guided**

   Lo step 14:

   ```text
   normalizzare bbox immagine -> canvas viewer
   usare terminali x/y come pin visuali
   mantenere orientamento stimato
   calcolare routes tra terminali/nodi
   creare fallback per componenti scenario senza bbox
   ```

4. **`15_render_viewer_svg.py`**

   Input:

   ```text
   13_viewer_model.json
   14_viewer_layout.json
   ```

   Output realizzato:

   ```text
   15_viewer.svg
   ```

5. **Integrazione nella web chat**

   `09_web_chat.py`:

   ```text
   carica o genera 13
   carica o genera 14
   carica o genera 15
   mostrare il viewer nella pagina centrale
   ```

6. **Hook scenario**

   Quando l'utente esegue uno scenario dalla chat:

   ```text
   copia base run
   applica scenario
   esegue ngspice
   genera 13 sulla run scenario
   genera 14 sulla run scenario
   genera 15 sulla run scenario
   apre la pagina sullo scenario
   ```

## Vocabolario Componenti Iniziale

Prima versione:

```text
connector
ground
resistor
capacitor
inductor
diode / led
lamp
switch open/closed
battery / voltage_source
current_source
signal_source
analog_meter
fuse
transistor
scenario_link
scenario_resistor
scenario_voltage_source
```

Ogni simbolo deve dichiarare:

```text
tipo
numero terminali
dimensione
punti terminali locali
orientamento supportato
renderer SVG
label
stati opzionali
```

## Gestione Scenari

Ogni scenario e una run autonoma.

Da supportare:

```text
change_component_value
change_source_value
close_switch
connect_nodes
feed_nodes_from_source_node
add_voltage_source_between_nodes
add_resistor_between_nodes
drive_node_voltage
```

Classificazione:

```text
non topologici:
  change_component_value
  change_source_value

topologici / visuali:
  close_switch
  connect_nodes
  feed_nodes_from_source_node
  add_voltage_source_between_nodes
  add_resistor_between_nodes
  drive_node_voltage
```

Regole:

- scenario non topologico: riusa il layout base come seed e aggiorna valori;
- scenario `close_switch`: stesso switch strutturale, stato `closed`;
- scenario topologico: usa la netlist scenario e aggiunge componenti/collegamenti;
- componenti aggiunti dallo scenario: evidenziati e posizionati vicino ai nodi
  coinvolti.

Componenti scenario senza bbox:

```text
P1 = posizione visuale del nodo A
P2 = posizione visuale del nodo B
mid = (P1 + P2) / 2
dir = normalize(P2 - P1)
normal = (-dir.y, dir.x)
pos = mid + normal * offset
```

Uso:

- `add_voltage_source_between_nodes`: sorgente scenario tra i due nodi;
- `add_resistor_between_nodes`: resistenza scenario tra i due nodi;
- `connect_nodes`: linea/link scenario tratteggiato;
- `feed_nodes_from_source_node`: linea scenario dal nodo sorgente al nodo target;
- `drive_node_voltage`: sorgente scenario tra nodo target e ground;
- `close_switch`: non aggiunge simboli, cambia stato dello switch esistente.

Fallback:

- se i nodi sono troppo vicini, usare un offset laterale fisso;
- se il componente esce dal canvas, fare clamp nel canvas;
- se ci sono piu componenti scenario tra gli stessi nodi, aumentare l'offset;
- se manca la posizione di un nodo, usare una piccola area `scenario/extra`.

## Copertura Raggiunta

1. `a01` base run e scenario renderizzati da `13 + 14 + 15`, senza coordinate
   hardcoded in `09_web_chat.py`.
2. Estensione progressiva completata:

```text
a01 -> a10/a09 -> a02/a05/a07 -> a08 -> a04/a06
```

3. I miglioramenti introdotti sono rimasti generali:

```text
nuovo simbolo
nuova regola layout
nuovo fallback
nuova gestione scenario
```

## Workspace

Workspace di Experiment 3:

```text
outputs/pipeline2.0/batchA/experiment3_viewer/
```

Circuiti coperti:

```text
a01, a02, a04, a05, a06, a07, a08, a09, a10
```

`a03` resta escluso dalla prima fase.

## Comando Web Chat

```powershell
python scripts\pipeline_2.0\json_to_spice\09_web_chat.py --batch batchA --experiment experiment3_viewer --circuit a01 --ngspice-executable "C:\Users\m.profilo\Spice64\bin\ngspice_con.exe"
```

## Criteri Di Successo

- [x] viewer generato per base run e scenari;
- [x] nessun renderer hardcoded per singolo circuito;
- [x] differenze scenario visibili quando la topologia cambia;
- [x] valori ngspice mostrati senza contraddire la simulazione;
- [x] fallback per componenti aggiunti e collegamenti scenario;
- [x] navigazione con zoom e pan, scope per transitori e piccoli ponti sugli
  attraversamenti senza giunzione.

## Limiti Accettati

- niente ricostruzione pixel-perfect;
- layout equivalente e leggibile, non pixel-perfect;
- componenti complessi rappresentabili come blocchi;
- CircuitJS/Falstad resta riferimento UX, non motore di simulazione.
