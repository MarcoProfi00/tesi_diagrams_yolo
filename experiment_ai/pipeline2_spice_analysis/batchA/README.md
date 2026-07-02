# Batch A - Pipeline 2.0 SPICE analysis

Questo file riassume lo stato finale del primo esperimento sul Batch A dopo
l'esecuzione della Pipeline 2.0 fino a SPICE/ngspice e dopo la prima prova con
agente diagnostico, web chat e scenari controllati.

Non e un output automatico della pipeline. E un riepilogo di lavoro per noi,
basato sui file reali prodotti in:

```text
outputs/pipeline2.0/batchA/
```

e sui markdown di analisi circuito per circuito presenti in questa cartella.

## Stato generale

Il Batch A e stato completato sui circuiti:

```text
a01, a02, a03, a04, a05, a06, a07, a08, a09, a10
```

Per ogni circuito sono disponibili:

```text
01_graph.json
02_normalized_circuit.json
03_node_map.json
04_values_bound.json
06_component_rules.json
07_netlist.cir
07_spice_emit_report.json
08_spice_run.json
08_ngspice_stdout.txt
08_ngspice_stderr.txt
```

Per i circuiti con `.tran` riuscita sono disponibili anche:

```text
08_tran_raw.csv
08_tran.csv
08_tran_plot.png
```

## Cosa significa "emessi / saltati"

La colonna `Emessi / saltati` si riferisce allo step:

```text
07_spice_emit.py
```

Questo step prende le regole prodotte da `06_component_rules.json` e prova a
scrivere la netlist SPICE finale.

Un componente e `emesso` quando diventa una riga reale nella netlist `.cir`.

Esempi:

```spice
Rresistor22_1 N008 N003 100k
Ccapacitor4_1 N001 N002 1u
Qnpn_transistor18_1 N009 N008 N003 BC547
Vbattery2_1 N002 N001 DC 12
```

Queste righe vengono lette da ngspice e partecipano alla simulazione.

Un componente e `saltato` quando non diventa una riga SPICE simulabile. Questo
puo succedere per motivi diversi:

- componente strutturale, come `GND`, `Connector` o `Terminal`;
- componente di misura, come un voltmetro trattato solo come punto di lettura;
- switch aperto, che viene lasciato come circuito aperto;
- valore mancante, per esempio lampada senza resistenza equivalente;
- modello o profilo non ancora supportato;
- terminali non validi o collassati sullo stesso nodo.

Quindi:

```text
emessi = componenti effettivamente simulati da ngspice
saltati = componenti riconosciuti dalla pipeline ma non scritti come elementi attivi nella netlist
```

Un numero alto di `saltati` non e automaticamente un errore. Per esempio GND e
Connector vengono spesso saltati correttamente, perche servono a costruire i
nodi ma non sono componenti elettrici da simulare.

Diventa invece diagnostico quando vengono saltati componenti importanti del
circuito, come una lampada, una bobina, una LDR o un transistor. In quel caso il
risultato SPICE va letto come parziale.

## Tabella riassuntiva

| Circuito | Stato 08 | Analisi | Emessi / saltati | Warning 07 | Nota principale |
| --- | --- | --- | ---: | ---: | --- |
| `a01` | success | `.op` | 5 / 4 | 1 | Circuito eseguito; switch aperto non emesso; utile come caso base con LED/lampada e supply manuale. |
| `a02` | success | `.op` | 3 / 4 | 1 | Circuito eseguito; switch aperto non emesso; caso semplice con batteria, resistenza e condensatore. |
| `a03` | failed | `.op` | 9 / 3 | 3 | Fallimento utile: graph incompleto, nodi singleton, nessun nodo `0`, rele non modellato come dispositivo unico. |
| `a04` | success | `.op`, `.tran 0.1ms 50ms` | 11 / 1 | 0 | Amplificatore BJT riuscito; output transitorio coerente e plot disponibile. |
| `a05` | success | `.op` | 2 / 6 | 1 | Eseguito in modo minimale; meter trattato come misura/elemento non centrale; switch aperto non emesso. |
| `a06` | success | `.op`, `.tran 0.1ms 50ms` | 13 / 7 | 0 | Amplificatore BJT con `VCC/VEE`; transitorio riuscito, ma ingresso grande da leggere con cautela. |
| `a07` | success | `.op`, `.tran 0.1ms 40ms` | 3 / 6 | 2 | Caso diagnosticamente utile: i rami reagiscono se pilotati, ma la base run manca di una vera sorgente/ingresso reale. |
| `a08` | success | `.op`, `.tran 0.5ms 300ms` | 8 / 2 | 0 | Circuito con sorgente quadra, transistor e LED; transitorio riuscito e plot disponibile. |
| `a09` | success | `.op` | 6 / 6 | 1 | SPICE riesce; scenari controllati mostrano che LED e lampada reagiscono se alimentati, mentre la base run non trasferisce alimentazione ai rami finali. |
| `a10` | success | `.op` | 4 / 5 | 1 | Circuito eseguito; switch aperto non emesso; caso base con LED/lampada. |

## Risultato complessivo

Dal punto di vista tecnico, il Batch A contiene:

```text
9 circuiti con ngspice success
1 circuito con ngspice failed
```

Il circuito fallito e:

```text
a03
```

Questo fallimento non va considerato inutile. Al contrario, `a03` e uno dei casi
piu importanti per progettare l'agente diagnostico, perche mostra come la
pipeline deve comportarsi quando il Graph JSON non basta per produrre una
simulazione affidabile.

## Circuiti riusciti direttamente

Questi circuiti producono un risultato ngspice `success`:

```text
a01, a02, a04, a05, a06, a07, a08, a09, a10
```

Tra questi, i casi piu forti per validare la parte SPICE sono:

```text
a04
a06
a08
```

Perche includono:

- transistor BJT;
- modelli SPICE;
- `.tran`;
- CSV pulito;
- plot PNG;
- risultati dinamici interpretabili.

## Circuiti con transitorio

I circuiti con analisi `.tran` sono:

```text
a04
a06
a07
a08
```

Questi sono importanti perche dimostrano che la Pipeline 2.0 non produce solo
netlist statiche, ma riesce anche a:

- eseguire una simulazione nel tempo;
- esportare CSV;
- pulire il CSV ngspice;
- generare un plot PNG leggibile.

## Circuiti riusciti ma diagnosticamente delicati

Alcuni circuiti hanno `ngspice success`, ma vanno interpretati con prudenza.

### a07

`a07` viene eseguito, ma il report segnala:

```text
led12.1: terminals collapse to the same SPICE node; not emitted
switch25.1: open switch not emitted
```

Gli scenari controllati hanno poi mostrato che il ramo LED e il ramo VAC
reagiscono quando vengono pilotati separatamente. La conclusione piu utile e
che la base run manca soprattutto di una vera sorgente/ingresso reale, piu che
di un guasto dei rami finali.

E un caso utile per insegnare all'agente a distinguere:

```text
ngspice success != circuito reale completamente validato
```

### a09

`a09` viene eseguito e la base run e coerente con la netlist generata, ma i
rami finali non ricevono alimentazione utile.

Questo e un caso utile per l'agente perche:

- SPICE non fallisce;
- il risultato e numericamente valido rispetto alla netlist;
- gli scenari controllati mostrano che il ramo LED reagisce quando `N005` viene
  alimentato;
- il ramo lampada reagisce quando `N004` viene alimentato e lo switch e chiuso;
- il problema principale e il mancato trasferimento di alimentazione verso i
  rami finali nella base run.

Quindi l'agente deve confrontare:

```text
graph + node map + risultato SPICE + scenari controllati
```

prima di concludere.

## Circuito fallito: a03

`a03` e il caso principale di fallimento SPICE nel Batch A.

Da `08_spice_run.json`:

```json
{
  "status": "failed",
  "exit_code": 1,
  "message": "ngspice exited with errors."
}
```

Il graph rileva una struttura complessa:

- due `Battery`, anche se nell'immagine sembra esserci una sola batteria fisica;
- `Inductor` per la bobina del rele;
- `Switch` per il contatto del rele;
- `Signal_Source` e `Lamp` sul lato AC;
- nessun nodo di massa;
- quattro nodi singleton.

Da `03_node_map.json`:

```text
ground_groups_count = 0
singleton_nodes_count = 4
```

I nodi singleton sono:

```text
N001 = battery2.1_negative
N004 = battery2.2_positive
N010 = signal_source23.1_t1
N011 = switch25.1_t1
```

Da `07_spice_emit_report.json`, i componenti saltati sono:

```text
inductor10.1
lamp13.1
variable_resistor30.1
```

ngspice fallisce con:

```text
DC solution failed
singular matrix: check node n007
singular matrix: check node n006
The operating point could not be simulated successfully
```

Interpretazione:

```text
La netlist e fedele al graph, ma il graph non rappresenta un circuito SPICE
completo e referenziato. Il fallimento e quindi diagnostico, non un semplice
errore da nascondere.
```

Questo e il caso piu importante per l'agente: dovra spiegare il fallimento e
proporre scenari controllati, non correggere silenziosamente il `values.yaml`.

## Cosa abbiamo imparato dal Batch A

### 1. La pipeline deve restare fedele al Graph JSON

`values.yaml` deve simulare il futuro OCR:

```text
legge valori, sigle e label
```

Non deve:

- correggere collegamenti;
- unire componenti letti separatamente;
- inventare valori non visibili;
- trasformare un componente in un altro se il graph lo ha classificato
  diversamente.

Esempio: in `a03`, anche se l'immagine mostra `D1 DIODE`, il graph lo legge come
`LED`, quindi la Pipeline 2.0 lo tratta come `LED`.

### 2. SPICE success non significa sempre circuito corretto

Un run ngspice riuscito dimostra che la netlist e numericamente eseguibile, ma
non dimostra da solo che il graph rappresenti perfettamente l'immagine.

Esempi:

- `a09`: SPICE riesce, ma la topologia e sospetta;
- `a07`: SPICE riesce, ma alcuni componenti sono saltati.

### 3. SPICE failed puo essere un risultato utile

`a03` dimostra che un fallimento SPICE puo diventare materiale diagnostico:

- nodi flottanti;
- componenti mancanti;
- assenza di ground;
- graph incompleto;
- modello funzionale del rele assente.

Questi dati sono esattamente cio che l'agente dovra leggere.

### 4. Lo step 08 e il punto giusto per agganciare l'agente

Dopo `08_spice_run.py`, abbiamo:

```text
netlist
report emissione
stdout ngspice
stderr ngspice
status success/failed
eventuali CSV e plot
```

Quindi l'agente puo ragionare sia su successi sia su fallimenti.

## Ruolo dei markdown circuito

I file:

```text
a01.md
a02.md
a03.md
a04.md
a05.md
a06.md
a07.md
a08.md
a09.md
a10.md
```

sono note manuali per noi. Non fanno parte della pipeline automatica.

Servono a:

- capire i risultati SPICE;
- validare che la pipeline stia producendo output coerenti;
- ragionare sui casi limite;
- progettare il comportamento futuro dell'agente.

In pratica, questi markdown sono il prototipo manuale di cio che l'agente dovra
fare automaticamente:

```text
leggere output tecnici
spiegare risultato
distinguere fatti, assunzioni e ipotesi
proporre scenari controllati
```

## Stato dell'agente e della web chat

Nel primo esperimento non ci siamo fermati allo step `08`.

Sono stati provati anche:

```text
09_web_chat.py
10_diagnostic_context.py
11_agent_diagnosis.py
12_controlled_scenarios.py
```

La web chat permette di:

- leggere la base run;
- interrogare l'agente con un sintomo utente;
- proporre scenari diagnostici;
- eseguire scenari controllati in cartelle separate;
- confrontare base run e scenario run senza modificare gli output originali.

Questa parte resta sperimentale, ma e gia sufficiente per validare il flusso
diagnostico manuale assistito dall'agente.

## Prossimo passo consigliato

Dopo questo primo esperimento sul Batch A, il passo piu sensato e consolidare
la valutazione.

Ordine consigliato:

1. Congelare i markdown `a01.md`-`a10.md` come report del primo esperimento.
2. Aggiornare una tabella sintetica con esito base, scenari eseguiti e diagnosi
   finale per ogni circuito.
3. Definire metriche semplici per la tesi, per esempio success/fail SPICE,
   numero scenari, scenario risolutivo, caso topologico, caso inconclusivo.
4. Solo dopo, migliorare la visualizzazione web e la parte animata del circuito.

## Sintesi finale

Batch A e completo per il primo esperimento Pipeline 2.0 + SPICE + agente.

Il risultato complessivo e buono:

- la pipeline genera netlist per tutti i circuiti;
- ngspice viene eseguito su tutti i circuiti;
- i successi sono spiegabili;
- il fallimento di `a03` e diagnostico e utile;
- i casi delicati come `a07`, `a09` e `a10` mostrano perche servono scenari
  controllati;
- i markdown manuali documentano il comportamento atteso dell'agente e i limiti
  della diagnosi.

Questo Batch A e quindi una base solida per passare dalla conversione
Graph JSON -> SPICE alla valutazione piu sistematica della diagnosi AI.
