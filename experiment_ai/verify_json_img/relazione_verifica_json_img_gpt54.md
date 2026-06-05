# Relazione verifica Graph JSON rispetto alle immagini

## Obiettivo della verifica

Questa relazione documenta la verifica eseguita nella cartella `experiment_ai/verify_json_img` sui quattro batch `batchA`, `batchB`, `batchC1` e `batchC2`. L'obiettivo e valutare se il campo `graph` dei JSON prodotti dalla pipeline rappresenta correttamente i collegamenti terminale-terminale visibili nelle immagini dei circuiti.

Il controllo non misura il funzionamento elettrico del circuito, non valuta la simulabilita SPICE, non corregge i JSON e non genera netlist. Il suo scopo e piu circoscritto: stabilire se il grafo estratto sia una base topologica fedele all'immagine, quindi potenzialmente utilizzabile in una fase successiva di conversione verso una netlist.

In altre parole, la domanda verificata dal judge e:

> I collegamenti terminale-terminale dichiarati nel Graph JSON sono coerenti con i fili e i terminali visibili nell'immagine?

## Materiale analizzato

La struttura usata e la seguente:

```text
experiment_ai/verify_json_img/
|-- prompt.txt
|-- batchA/
|   |-- images/
|   |-- json/
|   `-- output_gpt5_4_final_curated/
|-- batchB/
|   |-- images/
|   |-- json/
|   `-- output_gpt5_4/
|-- batchC1/
|   |-- images/
|   |-- json/
|   `-- output_gpt5_4/
`-- batchC2/
    |-- images/
    |-- json/
    `-- output_gpt5_4/
```

Per ogni circuito il judge riceve:

- l'immagine originale del circuito;
- il Graph JSON originale prodotto dalla pipeline;
- il prompt di verifica `prompt.txt`;
- il vocabolario `metadata/class_terminals_v1.yaml`.

Lo script usato e:

```text
scripts/GPT/verifica_json_img/judge_image_graph.py
```

Il modello usato nei risultati finali e `gpt-5.4`. Il prompt finale ha hash:

```text
19f1ee29c0c6
```

Il vocabolario YAML ha hash:

```text
7e5491a8cdf0
```

## Criteri di valutazione

Il judge assegna un punteggio totale da 0 a 100, ottenuto dalla somma di quattro sottopunteggi:

| Sottopunteggio | Massimo | Significato |
|---|---:|---|
| `components` | 10 | Presenza e coerenza dei componenti usati come endpoint dei collegamenti. |
| `terminals_pins` | 25 | Correttezza di terminali, pin, polarita e ruoli terminali visibili. |
| `graph_connections` | 55 | Fedelta dei collegamenti terminale-terminale nel campo `graph`. |
| `visible_semantics` | 10 | Uso corretto di metadati visibili, warning, OCR e informazioni ausiliarie. |

La parte piu importante e `graph_connections`, perche misura direttamente se i nodi del grafo corrispondono ai fili visibili nell'immagine.

Le decisioni qualitative sono:

| Decisione | Interpretazione |
|---|---|
| `VERY_HIGH` | Il grafo e molto fedele; eventuali errori sono minori e non alterano la topologia principale. |
| `HIGH` | La struttura principale e corretta, ma esistono errori locali. |
| `MEDIUM` | Il grafo rappresenta solo parzialmente l'immagine; sono presenti errori importanti. |
| `LOW` | Il grafo e troppo incompleto o incompatibile con l'immagine. |

Il campo `usable_as_graph_base` indica se, nonostante gli errori, il grafo rimane una base utile e correggibile. In tutti i batch analizzati questo campo risulta `True` per tutti i circuiti.

## Nota metodologica sui batch

La divisione dei batch e stata mantenuta. Non e stato creato un dataset operativo aggregato: ogni batch conserva la propria cartella di output, il proprio CSV, il proprio report e i propri grafici.

Per `batchA` e stata creata una cartella finale curata:

```text
batchA/output_gpt5_4_final_curated/
```

Questa cartella contiene il Batch A completo con due sostituzioni motivate:

- `a07` e stato sostituito con il rerun `medium`, perche il run `low` aveva prodotto un falso positivo sul trasformatore;
- `a09` e stato sostituito con il rerun singolo `medium`, perche il caso e risultato stabilmente problematico ma con una lettura piu prudente rispetto al rerun precedente.

I batch `B`, `C1` e `C2` usano le rispettive cartelle:

```text
batchB/output_gpt5_4/
batchC1/output_gpt5_4/
batchC2/output_gpt5_4/
```

## Sintesi per batch

| Batch | Circuiti | Media score | Mediana | Min | Max | VERY_HIGH | HIGH | MEDIUM | LOW | Critici | Maggiori | Minori |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| A | 10 | 93.00 | 97.00 | 74 | 98 | 8 | 1 | 1 | 0 | 1 | 4 | 12 |
| B | 10 | 89.50 | 92.00 | 70 | 95 | 8 | 1 | 1 | 0 | 1 | 14 | 16 |
| C1 | 10 | 93.60 | 95.00 | 78 | 98 | 9 | 1 | 0 | 0 | 0 | 6 | 15 |
| C2 | 8 | 93.62 | 94.50 | 86 | 97 | 7 | 1 | 0 | 0 | 0 | 9 | 13 |

La lettura generale e positiva: quasi tutti i circuiti sono `VERY_HIGH` o `HIGH`, e nessun circuito e classificato `LOW`. I casi `MEDIUM` sono pochi e concentrati in errori topologici specifici, non in un collasso generale della pipeline.

## Batch A

Output finale usato:

```text
batchA/output_gpt5_4_final_curated/
```

### Grafici Batch A

**Score per circuito**

![Batch A - score per circuito](batchA/output_gpt5_4_final_curated/plots/01_score_per_circuito.png)

Questo grafico ordina i circuiti per punteggio. Il caso piu basso e `a09`, classificato `MEDIUM` con score 74. `a03` e `HIGH` con score 78. Tutti gli altri circuiti sono in fascia `VERY_HIGH`.

**Profilo errori per circuito**

![Batch A - profilo errori](batchA/output_gpt5_4_final_curated/plots/02_media_sottopunteggi_per_batch.png)

Questo grafico mostra il numero di errori critici, maggiori e minori per circuito. `a09` e l'unico circuito del batch con errore critico. `a03` ha piu errori maggiori, ma non presenta errori critici.

**Breakdown dei sottopunteggi**

![Batch A - breakdown sottopunteggi](batchA/output_gpt5_4_final_curated/plots/03_distribuzione_decisioni_per_batch.png)

Il breakdown conferma che il calo di `a09` e dovuto soprattutto al sottopunteggio `graph_connections`, cioe alla fedelta dei collegamenti. Gli altri circuiti mantengono sottopunteggi molto alti, specialmente nella parte topologica.

### Tabella Batch A

| Circuito | Score | Decisione | Critici | Maggiori | Minori | Graph connections |
|---|---:|---|---:|---:|---:|---:|
| a01 | 98 | VERY_HIGH | 0 | 0 | 1 | 55 |
| a02 | 97 | VERY_HIGH | 0 | 0 | 2 | 55 |
| a03 | 78 | HIGH | 0 | 3 | 3 | 47 |
| a04 | 98 | VERY_HIGH | 0 | 0 | 1 | 55 |
| a05 | 96 | VERY_HIGH | 0 | 0 | 1 | 54 |
| a06 | 98 | VERY_HIGH | 0 | 0 | 1 | 55 |
| a07 | 98 | VERY_HIGH | 0 | 0 | 0 | 54 |
| a08 | 97 | VERY_HIGH | 0 | 0 | 1 | 55 |
| a09 | 74 | MEDIUM | 1 | 1 | 0 | 35 |
| a10 | 96 | VERY_HIGH | 0 | 0 | 2 | 55 |

### Lettura Batch A

Il Batch A mostra una fedelta complessiva elevata: media 93.00, mediana 97.00 e 8 circuiti su 10 in fascia `VERY_HIGH`.

Il caso `a07` e importante dal punto di vista metodologico. Nel run iniziale a effort `low` era stato valutato `72 MEDIUM`, perche il judge aveva interpretato il ramo superiore del trasformatore come un filo continuo spezzato dal JSON. Dopo controllo manuale e rerun con effort `medium`, il circuito e stato rivalutato `98 VERY_HIGH`. Questa seconda lettura e coerente con l'immagine: il collegamento passa attraverso il trasformatore e non deve essere trattato come un semplice filo continuo. Per questo motivo `a07` e stato inserito nella cartella finale curata usando il risultato del rerun a effort `medium`, cioe `98 VERY_HIGH`.

Il caso `a09` e invece stabilmente problematico. Anche dopo rerun singolo con effort `medium`, resta `MEDIUM` con score 74. Gli errori principali sono:

- fusione errata tra il nodo basso di `C1`/GND e il nodo `J1 pin4`/lato sinistro di `R3`;
- mancato collegamento tra il terminale inferiore della lampada e il suo GND.

Questi errori riguardano direttamente la topologia del grafo, quindi la penalizzazione e fondata. Tuttavia il judge mantiene `usable_as_graph_base=True`: il grafo non e da scartare completamente, ma richiede correzioni locali prima di un eventuale uso per netlist.

`a03` e l'altro caso da osservare. La struttura principale resta riconoscibile, ma sono presenti errori locali: manca un collegamento nel ramo AC, la batteria e modellata in modo non ideale e lo stato dello switch non e coerente con l'immagine. Per questo il circuito resta `HIGH`, non `VERY_HIGH`.

## Batch B

Output usato:

```text
batchB/output_gpt5_4/
```

### Grafici Batch B

**Score per circuito**

![Batch B - score per circuito](batchB/output_gpt5_4/plots/01_score_per_circuito.png)

Il Batch B contiene il minimo piu basso tra i batch analizzati: `b06`, classificato `MEDIUM` con score 70. Anche `b01` scende a `HIGH` con score 80. Gli altri otto circuiti sono `VERY_HIGH`.

**Profilo errori per circuito**

![Batch B - profilo errori](batchB/output_gpt5_4/plots/02_media_sottopunteggi_per_batch.png)

Il profilo errori evidenzia due circuiti dominanti: `b06`, con un errore critico e diversi errori maggiori, e `b01`, con quattro errori maggiori. Gli altri circuiti presentano errori prevalentemente locali o semantici.

**Breakdown dei sottopunteggi**

![Batch B - breakdown sottopunteggi](batchB/output_gpt5_4/plots/03_distribuzione_decisioni_per_batch.png)

Il calo di `b06` e concentrato soprattutto su `graph_connections` e `terminals_pins`. Questo indica che il problema non e solo di classificazione semantica, ma anche di collegamenti/pin interpretati in modo non pienamente coerente.

### Tabella Batch B

| Circuito | Score | Decisione | Critici | Maggiori | Minori | Graph connections |
|---|---:|---|---:|---:|---:|---:|
| b01 | 80 | HIGH | 0 | 4 | 2 | 45 |
| b02 | 95 | VERY_HIGH | 0 | 0 | 2 | 53 |
| b03 | 92 | VERY_HIGH | 0 | 1 | 2 | 50 |
| b04 | 94 | VERY_HIGH | 0 | 1 | 1 | 53 |
| b05 | 91 | VERY_HIGH | 0 | 1 | 2 | 52 |
| b06 | 70 | MEDIUM | 1 | 5 | 1 | 38 |
| b07 | 92 | VERY_HIGH | 0 | 1 | 1 | 52 |
| b08 | 92 | VERY_HIGH | 0 | 1 | 1 | 50 |
| b09 | 95 | VERY_HIGH | 0 | 0 | 2 | 54 |
| b10 | 94 | VERY_HIGH | 0 | 0 | 2 | 54 |

### Lettura Batch B

Il Batch B ha media 89.50 e mediana 92.00. E quindi il batch piu debole tra i quattro, ma resta complessivamente buono: 8 circuiti sono `VERY_HIGH`, 1 e `HIGH` e 1 e `MEDIUM`.

`b01` e penalizzato per errori sui terminali dei BJT e sugli ingressi dell'opamp. Il judge rileva che la struttura principale e ancora leggibile, ma i ruoli di base, collettore ed emettitore risultano mappati in modo non corretto rispetto al simbolo visibile. Questo e un errore importante per una futura conversione verso SPICE, perche un transistor con terminali invertiti puo cambiare drasticamente la netlist.

`b06` e il caso piu delicato del batch. Il judge lo classifica `MEDIUM` con score 70. Nel report automatico vengono segnalati errori su rail di alimentazione/massa, pin dell'LM386, condensatore variabile e ramo di uscita. La revisione manuale suggerisce pero cautela: alcune penalizzazioni sembrano eccessive, perche il ramo batteria/massa e alcuni endpoint del circuito di sintonia e uscita possono essere interpretati diversamente dall'immagine. Il risultato `MEDIUM` va quindi letto come indicazione di caso complesso e da correggere manualmente, non come prova che l'intero grafo sia inutilizzabile.

Gli altri circuiti del Batch B mostrano soprattutto errori semantici o locali: classi non perfette, terminali di MOSFET o BJT non sempre ideali, oppure endpoint ausiliari mancanti. Tuttavia la topologia principale resta generalmente fedele.

## Batch C1

Output usato:

```text
batchC1/output_gpt5_4/
```

### Grafici Batch C1

**Score per circuito**

![Batch C1 - score per circuito](batchC1/output_gpt5_4/plots/01_score_per_circuito.png)

Il Batch C1 ha risultati molto solidi: 9 circuiti `VERY_HIGH` e un solo circuito `HIGH`, `c08`, con score 78.

**Profilo errori per circuito**

![Batch C1 - profilo errori](batchC1/output_gpt5_4/plots/02_media_sottopunteggi_per_batch.png)

Il profilo errori mostra che non sono presenti errori critici. Le criticita sono concentrate in `c08`, e in misura minore in `c05`, `c07` e `c18`.

**Breakdown dei sottopunteggi**

![Batch C1 - breakdown sottopunteggi](batchC1/output_gpt5_4/plots/03_distribuzione_decisioni_per_batch.png)

La maggior parte dei circuiti mantiene punteggi alti in tutte le componenti. `c08` scende soprattutto nella parte `graph_connections`, coerentemente con l'errore sul selettore SPDT.

### Tabella Batch C1

| Circuito | Score | Decisione | Critici | Maggiori | Minori | Graph connections |
|---|---:|---|---:|---:|---:|---:|
| c01 | 98 | VERY_HIGH | 0 | 0 | 1 | 55 |
| c02 | 95 | VERY_HIGH | 0 | 0 | 3 | 55 |
| c03 | 97 | VERY_HIGH | 0 | 0 | 2 | 55 |
| c04 | 97 | VERY_HIGH | 0 | 0 | 1 | 54 |
| c05 | 95 | VERY_HIGH | 0 | 1 | 1 | 53 |
| c06 | 95 | VERY_HIGH | 0 | 0 | 2 | 53 |
| c07 | 93 | VERY_HIGH | 0 | 1 | 1 | 51 |
| c08 | 78 | HIGH | 0 | 3 | 1 | 43 |
| c17 | 96 | VERY_HIGH | 0 | 0 | 1 | 53 |
| c18 | 92 | VERY_HIGH | 0 | 1 | 2 | 52 |

### Lettura Batch C1

Il Batch C1 e uno dei batch piu solidi per distribuzione qualitativa: nessun `MEDIUM`, nessun `LOW`, nessun errore critico. La media e 93.60, con mediana 95.00.

I circuiti con IC e pin OCR risultano generalmente ben rappresentati. Questo e un punto importante: il judge non usa datasheet esterni, ma verifica numeri di pin, lati dei package e fili visibili. Nei casi con 555, 4026, 4017 o altri integrati, il grafo e risultato quasi sempre coerente con l'immagine.

`c08` e l'unico caso sensibilmente piu basso. Il problema principale e il selettore `S1`: nell'immagine e uno switch SPDT, quindi ha un contatto comune e due rami alternativi. Nel JSON viene ridotto a uno switch a due terminali, lasciando fuori uno dei due rami verso le resistenze da 1k. Questo e un errore topologico reale: non riguarda valori o designator, ma un ramo fisico che sparisce dalla struttura del grafo.

`c05`, `c07` e `c18` hanno errori locali ma restano `VERY_HIGH`. In `c05` manca un collegamento a `+Vcc` per un resistore superiore; in `c07` un terminale del secondo pulsante risulta flottante; in `c18` manca un pin supply visibile per un opamp. Sono errori da correggere se si vuole arrivare a una netlist completa, ma non compromettono la struttura principale.

## Batch C2

Output usato:

```text
batchC2/output_gpt5_4/
```

### Grafici Batch C2

**Score per circuito**

![Batch C2 - score per circuito](batchC2/output_gpt5_4/plots/01_score_per_circuito.png)

Il Batch C2 ha 7 circuiti `VERY_HIGH` e un circuito `HIGH`, `c09`, con score 86. Non sono presenti circuiti `MEDIUM` o `LOW`.

**Profilo errori per circuito**

![Batch C2 - profilo errori](batchC2/output_gpt5_4/plots/02_media_sottopunteggi_per_batch.png)

Il profilo errori mostra che `c09` concentra il maggior numero di errori maggiori. Gli altri circuiti hanno al massimo errori locali o semantici.

**Breakdown dei sottopunteggi**

![Batch C2 - breakdown sottopunteggi](batchC2/output_gpt5_4/plots/03_distribuzione_decisioni_per_batch.png)

Il breakdown conferma che `c09` e il caso piu debole, ma con score ancora alto rispetto alla soglia `HIGH`. La maggior parte dei circuiti mantiene punteggi elevati nelle connessioni.

### Tabella Batch C2

| Circuito | Score | Decisione | Critici | Maggiori | Minori | Graph connections |
|---|---:|---|---:|---:|---:|---:|
| c09 | 86 | HIGH | 0 | 4 | 2 | 47 |
| c10 | 92 | VERY_HIGH | 0 | 1 | 2 | 51 |
| c11 | 95 | VERY_HIGH | 0 | 1 | 1 | 53 |
| c12 | 96 | VERY_HIGH | 0 | 0 | 2 | 53 |
| c13 | 95 | VERY_HIGH | 0 | 1 | 2 | 53 |
| c14 | 94 | VERY_HIGH | 0 | 1 | 1 | 52 |
| c15 | 94 | VERY_HIGH | 0 | 1 | 1 | 53 |
| c16 | 97 | VERY_HIGH | 0 | 0 | 2 | 54 |

### Lettura Batch C2

Il Batch C2 e molto stabile: media 93.62, mediana 94.50, nessun errore critico, nessun `MEDIUM` e nessun `LOW`.

`c09` e il caso piu complesso. Il grafo cattura la struttura generale del voltmetro digitale, inclusi ADC0804, AT89S51, bus dati e display, ma presenta errori nella zona dei transistor e dei display. In particolare, il judge segnala uno split del nodo comune/emettitore/massa e alcune fusioni non visibili tra uscite resistive e pin del display sinistro. Il circuito resta comunque `HIGH`: la struttura principale e riconoscibile e correggibile.

`c10` ha una mancanza legata al microfono `M1`; `c15` manca della connessione del pin 10 dell'IC al terminale esterno; altri circuiti hanno errori soprattutto semantici, come condensatori modellati come polarizzati quando nell'immagine appaiono non polarizzati. Questi errori non cancellano la topologia principale.

## Discussione complessiva

La verifica mostra che la pipeline produce Graph JSON generalmente coerenti con le immagini. La maggioranza dei circuiti e classificata `VERY_HIGH`; i pochi casi piu deboli sono spiegabili e localizzati.

Il risultato piu importante per la tesi non e solo la media dei punteggi, ma il tipo di errore osservato:

- molti errori sono semantici o locali, quindi correggibili con regole successive;
- gli errori topologici gravi sono pochi;
- nessun circuito risulta inutilizzabile come base di grafo;
- i casi peggiori evidenziano categorie precise di difficolta: switch multi-terminale, pin di transistor/opamp, carichi mancanti, fusioni o split di net.

Questa distinzione e essenziale per l'integrazione con SPICE. Un grafo puo essere molto fedele all'immagine ma non ancora direttamente simulabile. Per passare a SPICE servira un livello successivo che:

- converta componenti e terminali in primitive compatibili con una netlist;
- assegni valori elettrici quando disponibili;
- gestisca alimentazioni, masse e label globali con regole esplicite;
- decida come trattare simboli non direttamente simulabili, come connettori, speaker, lampade, strumenti, switch e terminali esterni;
- segnali i casi in cui un errore del grafo impedisce una conversione affidabile.

Il judge descritto qui non sostituisce quella fase. Serve invece come controllo preliminare: se il Graph JSON non e fedele all'immagine, una netlist SPICE generata da esso rischia di essere sbagliata gia in partenza.

## Limiti della verifica

Il metodo ha alcuni limiti che vanno dichiarati:

- il giudice e multimodale e puo commettere errori di lettura visiva, come visto nel primo run di `a07`;
- le immagini con fili molto vicini, incroci senza junction dot o simboli compressi possono produrre ambiguita;
- il judge non usa datasheet, quindi non verifica funzioni interne dei pin non visibili;
- il judge valuta cio che e disegnato, non cio che sarebbe elettricamente corretto;
- uno score alto non garantisce automaticamente una netlist SPICE valida;
- uno score medio non implica necessariamente che il grafo sia da scartare, ma indica che serve revisione manuale o correzione locale.

Il rerun di `a07` e particolarmente utile come esempio di controllo metodologico: quando un risultato del judge contraddice la lettura manuale, e opportuno rieseguire il caso con effort maggiore o trattarlo come caso ambiguo. Al contrario, `a09` e rimasto `MEDIUM` anche dopo rerun, quindi e un errore robusto del Graph JSON.

## Conclusione

Nel complesso, la verifica supporta l'idea che i Graph JSON prodotti dalla pipeline siano spesso una base topologica fedele all'immagine. La maggior parte dei circuiti risulta `VERY_HIGH`, con pochi casi `HIGH` e solo due casi `MEDIUM` nei risultati finali separati per batch: `a09` nel Batch A e `b06` nel Batch B.

Per la tesi, questi risultati possono essere interpretati cosi: la pipeline e promettente per costruire una rappresentazione graph-based dei circuiti a partire da immagini, ma il passaggio verso SPICE richiede ancora un livello di validazione e conversione. Il judge immagine-graph e quindi un controllo intermedio molto utile: non dimostra da solo la simulabilita, ma misura se il dato topologico di partenza e abbastanza fedele da giustificare il passo successivo.
