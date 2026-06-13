# Agente diagnostico dopo SPICE

Questo documento riassume l'idea aggiornata per integrare un agente AI nella
pipeline JSON -> SPICE.

La scelta progettuale principale e:

```text
01 -> 02 -> 03 -> 04 -> 06 -> 07 -> 08 -> agente
```

L'agente non sostituisce la pipeline. Si appoggia agli output gia prodotti,
soprattutto allo step `08`, cioe l'esecuzione reale di ngspice.

## Punto di aggancio

L'agente deve partire dopo `08_spice_run.py`.

Motivo:

- prima di `08` abbiamo solo una netlist generata;
- dopo `08` abbiamo anche il risultato reale di SPICE;
- quindi l'agente puo confrontare il circuito previsto con il comportamento
  simulato.

Lo step `08` produce fatti grezzi:

```text
08_spice_run.json
08_ngspice_stdout.txt
08_ngspice_stderr.txt
```

L'agente legge questi file insieme agli altri output della pipeline.

## Input dell'agente

Per ogni circuito, l'agente dovrebbe ricevere:

```text
problema utente
03_node_map.json
04_values_bound.json
06_component_rules.json
07_netlist.cir
07_spice_emit_report.json
08_spice_run.json
08_ngspice_stdout.txt
08_ngspice_stderr.txt
path immagine originale
```

Esempio di problema utente:

```text
La lampada non si accende.
```

L'agente deve usare questi dati come evidenza. Non deve inventare collegamenti,
valori o componenti assenti.

## Cosa deve fare l'agente

L'agente deve aiutare l'utente a capire il risultato della pipeline e della
simulazione.

Compiti principali:

- spiegare se ngspice e stato eseguito correttamente;
- leggere tensioni e correnti dal risultato SPICE;
- collegare i nodi SPICE ai terminali reali tramite `03_node_map.json`;
- rispondere al problema dell'utente usando i dati disponibili;
- proporre scenari simulativi controllati quando il risultato base non risolve
  il problema.

## Esempio: a01

Problema:

```text
La lampada non si accende.
```

Output SPICE base:

```text
Lamp current = 0 A
N002 = 0 V
N004 = 0 V
```

Node map:

```text
N002 = connector5.1_pin2
N004 = lamp13.1_t1 + resistor22.1_t2
```

Diagnosi dell'agente:

```text
La simulazione conferma che la lampada non conduce corrente.
Il ramo lampada parte da connector5.1_pin2.
Nella simulazione base, quel pin non e alimentato.
```

Possibile scenario proposto:

```text
Applicare 5 V a connector5.1_pin2 e rieseguire SPICE.
```

## Scenari controllati

L'agente puo proporre scenari, ma non deve modificare liberamente la netlist.

La pipeline dovrebbe offrire un piccolo insieme di azioni consentite. L'agente
sceglie quali azioni usare, ma la pipeline le traduce in SPICE in modo
controllato e riproducibile.

Azioni scenario possibili:

```text
drive_node_voltage
close_switch
open_switch
add_pullup
add_pulldown
change_source_value
```

Esempio scenario JSON:

```json
{
  "scenario_id": "drive_lamp_input",
  "actions": [
    {
      "type": "drive_node_voltage",
      "target_terminal": "connector5.1_pin2",
      "value": 5,
      "unit": "V",
      "reason": "Test whether the lamp branch works when the connector pin is driven."
    }
  ]
}
```

La pipeline puo trasformare questo scenario in una netlist separata, per
esempio aggiungendo una sorgente:

```spice
Vscenario_connector5_1_pin2 N002 0 DC 5
```

Importante:

```text
base circuit != scenario circuit
```

Il circuito base resta quello riconosciuto e valorizzato dalla pipeline. Lo
scenario e una modifica simulativa controllata, utile per testare un'ipotesi.

## Ruolo dell'agente e ruolo della pipeline

L'agente decide cosa provare e perche.

La pipeline decide come applicare lo scenario in modo sicuro.

Schema:

```text
utente descrive problema
-> agente legge output 08 e contesto tecnico
-> agente propone scenario JSON
-> pipeline valida lo scenario
-> pipeline genera netlist scenario
-> ngspice esegue lo scenario
-> agente confronta base vs scenario
-> agente spiega il risultato
```

Questa separazione evita che l'agente inventi netlist arbitrarie.

## Livelli di implementazione

### Livello 1: agente diagnostico solo lettura

Legge i file prodotti dalla pipeline e risponde all'utente.

Non modifica niente.

Comando possibile:

```powershell
python scripts\pipeline_2.0\agent\diagnostic_agent.py --batch batchA --circuit a01 --question "La lampada non si accende"
```

Output possibile:

```text
outputs/pipeline2.0/batchA/a01/agent_diagnosis.md
```

Questo livello e sufficiente per una prima demo.

### Livello 2: agente che propone scenari

L'agente non esegue ancora nulla, ma produce scenari JSON.

Output possibile:

```text
outputs/pipeline2.0/batchA/a01/proposed_scenarios.json
```

Esempio:

```json
{
  "scenarios": [
    {
      "scenario_id": "drive_lamp_input",
      "actions": [
        {
          "type": "drive_node_voltage",
          "target_terminal": "connector5.1_pin2",
          "value": 5,
          "unit": "V"
        }
      ]
    }
  ]
}
```

### Livello 3: agente con strumenti

L'agente puo chiedere alla pipeline di:

- creare uno scenario;
- rigenerare la netlist;
- eseguire ngspice;
- confrontare base e scenario;
- produrre una risposta finale.

Questa versione e piu potente, ma va implementata dopo aver validato bene la
pipeline base su piu circuiti.

## Perche gli scenari devono essere generali

Non dobbiamo scrivere scenari speciali per `a01`, `a02` o `a10`.

Dobbiamo definire azioni generiche che funzionano su tutti i batch.

Esempi:

```text
drive_node_voltage -> applica una tensione DC a un nodo/terminale
close_switch       -> modella uno switch come quasi corto circuito
open_switch        -> modella uno switch come circuito aperto
add_pullup         -> aggiunge una resistenza verso una supply
add_pulldown       -> aggiunge una resistenza verso GND
```

Poi l'agente sceglie l'azione in base al problema utente e ai risultati SPICE.

## Possibile forma del contesto per GPT

Prima di chiamare il modello, conviene costruire un contesto ordinato.

Possibile struttura:

```text
[USER PROBLEM]
...

[IMAGE PATH]
...

[NODE MAP SUMMARY]
...

[VALUES]
...

[COMPONENT RULES]
...

[NETLIST]
...

[SPICE RUN REPORT]
...

[NGSPICE STDOUT]
...

[NGSPICE STDERR]
...

[TASK]
Explain the likely cause of the user's problem using only the provided evidence.
If useful, propose one or more controlled simulation scenarios.
```

Gli output tecnici e i prompt verso il modello possono essere in inglese. La
risposta all'utente puo essere in italiano.

## API key e implementazione

Per usare un agente basato su un modello OpenAI serve una API key.

La prima implementazione puo essere uno script Python semplice:

```text
scripts/pipeline_2.0/agent/diagnostic_agent.py
```

Responsabilita minime:

- leggere i file del circuito;
- leggere la domanda utente;
- costruire il contesto;
- chiamare il modello;
- salvare la risposta.

Variabile ambiente:

```text
OPENAI_API_KEY
```

Comando indicativo:

```powershell
python scripts\pipeline_2.0\agent\diagnostic_agent.py --batch batchA --circuit a01 --question "La lampada non si accende"
```

## Cosa non fare ora

Per ora non conviene:

- far modificare liberamente la netlist all'agente;
- implementare subito tutti gli scenari;
- costruire subito una chat completa;
- costruire subito il sito;
- interpretare a mano tutti i possibili errori SPICE.

Prima conviene validare la pipeline su altri circuiti:

```text
a02
a10
altri circuiti semplici del batchA
```

Solo dopo ha senso implementare gli scenari.

## Roadmap consigliata

1. Validare `08` su `a02` e `a10`.
2. Estendere gradualmente a nuovi circuiti del batchA.
3. Capire quali problemi ricorrono spesso.
4. Definire poche azioni scenario generali.
5. Implementare `11_diagnostic_context.py` come pacchetto per l'agente.
6. Creare agente diagnostico solo lettura.
7. Aggiungere proposta di scenari JSON.
8. Aggiungere esecuzione automatica degli scenari.
9. Solo alla fine valutare chat o interfaccia web.

## Sintesi

L'agente deve essere agganciato dopo `08`, perche deve ragionare sui risultati
reali di ngspice.

La pipeline produce fatti strutturati. L'agente usa quei fatti per spiegare il
problema, proporre scenari e confrontare simulazioni.

La forma piu sicura e generale e:

```text
AI agent = decide cosa provare e perche
pipeline = applica lo scenario in modo controllato
ngspice = verifica numericamente
agent = spiega il confronto tra base e scenario
```

