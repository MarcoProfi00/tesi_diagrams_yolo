# Experiment 3 - Viewer visuale Pipeline 2.0

Questo documento contiene solo la roadmap operativa dell'Experiment 3.

Lo stato dell'arte e mantenuto nel file dedicato:

```text
notes/third_part_from_json_to_spice/stato_dell_arte_spice_to_viewer.md
```

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
  -> NUOVO: come disegnare SVG/HTML con vocabolario componenti

09_web_chat.py
  -> mostra solo il viewer della run selezionata
```

## Decisioni

- `09_web_chat.py` non deve contenere logica specifica di `a01`.
- Non vanno creati renderer dedicati tipo `render_a02`, `render_a09`, ecc.
- Le coordinate immagine non sono la verita elettrica: sono solo seed di layout.
- La netlist della run resta la sorgente di verita.
- I componenti scenario senza bbox vanno posizionati vicino ai nodi coinvolti.
- Ogni nuovo circuito deve migliorare regole generali, non aggiungere codice
  specifico.

## Roadmap Essenziale

1. **Pulire `09_web_chat.py`**

   Rimuovere progressivamente:

   ```text
   render_a01_viewer_svg
   coordinate specifiche di a01
   simboli SVG hardcoded
   logica di layout/rendering
   ```

   `09` deve restare:

   ```text
   server web
   chat diagnostica
   selettore base/scenario
   caricamento viewer della run attiva
   ```

2. **Estendere `13_build_viewer_model.py`**

   Aggiungere al `13_viewer_model.json`:

   ```text
   componenti SPICE da 07_netlist.cir
   componenti strutturali da 03_node_map/06_component_rules
   nodi e connessioni
   stato switch
   componenti scenario
   misure OP/TRAN
   geometry_seed da Pipeline 1.0
   ```

3. **Rendere `14_build_viewer_layout.py` image-guided**

   Lo step 14 deve:

   ```text
   normalizzare bbox immagine -> canvas viewer
   usare terminali x/y come pin visuali
   mantenere orientamento stimato
   calcolare routes tra terminali/nodi
   creare fallback per componenti scenario senza bbox
   ```

4. **Creare `15_render_viewer_svg.py`**

   Input:

   ```text
   13_viewer_model.json
   14_viewer_layout.json
   ```

   Output:

   ```text
   15_viewer.svg / 15_viewer.html oppure frammento SVG embeddabile
   ```

5. **Collegare `15` alla web chat**

   `09_web_chat.py` deve:

   ```text
   caricare o generare 13
   caricare o generare 14
   caricare o generare 15
   mostrare il viewer nella pagina centrale
   ```

6. **Scenario hook**

   Quando l'utente scrive "esegui scenario":

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

## Milestone

1. `a01` base run renderizzata da `13 + 14 + 15`, senza coordinate hardcoded in
   `09_web_chat.py`.
2. `scenario_1` di `a01` renderizzato dalla run scenario.
3. Estensione progressiva:

```text
a01 -> a10/a09 -> a02/a05/a07 -> a08 -> a04/a06
```

4. Ogni nuovo circuito aggiunge solo:

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

Prima fase:

```text
a01, a02, a04, a05, a06, a07, a08, a09, a10
```

`a03` resta escluso dalla prima fase.

## Comando Web Chat

```powershell
python scripts\pipeline_2.0\json_to_spice\09_web_chat.py --batch batchA --experiment experiment3_viewer --circuit a01 --ngspice-executable "C:\Users\m.profilo\Spice64\bin\ngspice_con.exe"
```

## Criteri Di Successo

- viewer generato per base run e scenari;
- nessun renderer hardcoded per singolo circuito;
- differenze scenario visibili quando la topologia cambia;
- valori ngspice mostrati senza contraddire la simulazione;
- fallback chiaro quando layout o simboli non sono ancora supportati.

## Limiti Accettati

- niente ricostruzione pixel-perfect;
- layout inizialmente grezzo ma leggibile;
- componenti complessi rappresentabili come blocchi;
- CircuitJS/Falstad resta riferimento UX, non motore di simulazione.
