# Confronto modelli AI per troubleshooting circuitale

## Obiettivo dell’esperimento

Valutare se una rappresentazione topologica strutturata del circuito, fornita come JSON, consente a modelli linguistici meno recenti o meno costosi di ottenere capacità diagnostiche comparabili a modelli multimodali moderni che ricevono direttamente l’immagine del circuito.

---

# 1. Modelli confrontati

| Modello | Input utilizzato | Funzione nel confronto sperimentale |
|---|---|---|
| `gpt-4o-mini` | JSON + datasheet | Verifica se un modello precedente ed economico può sfruttare efficacemente la rappresentazione topologica. |
| `gpt-4.1-mini` | JSON + datasheet | Valuta un compromesso tra leggerezza, costo e affidabilità diagnostica. |
| `gpt-5.4-nano` | JSON + datasheet | Misura le prestazioni ottenibili con un modello moderno ma estremamente compatto. |
| `gpt-4.1-nano` | JSON + datasheet | Test limite per capire quanto il JSON semplifica il compito diagnostico. |
| `gpt-5.4` | Immagine + datasheet | Baseline multimodale moderna per il confronto con l’approccio basato su JSON. |

---

# 2. Circuiti analizzati

| Circuito | IC principale | Tipo circuito | Problema simulato / domanda | Datasheet usato | Note sul JSON | Note sull’immagine |
|---|---|---|---|---|---|---|
| `ic3` | TDA1553Q | Amplificatore audio BTL | Il circuito non produce audio sugli altoparlanti | TDA1553Q | Switch M/SS open; speaker presenti; alimentazione rappresentata come terminale | Schema leggibile, include valori componenti e +12 V |
| `ic4` |  |  |  |  |  |  |
| `ic6` |  |  |  |  |  |  |
| `ic7` |  |  |  |  |  |  |
| `ic13` |  |  |  |  |  |  |

---

# 3. Risultati grezzi per circuito

## Circuito: `ic3`

### Problema

Il circuito non produce audio sugli altoparlanti. Quali sono le cause più probabili?

### Ground truth / valutazione attesa

| Aspetto | Valutazione attesa |
|---|---|
| Funzione del circuito | Amplificatore audio stereo BTL basato su TDA1553Q |
| Causa topologica principale attesa | Pin 11 M/SS potenzialmente non abilitato a causa dello switch aperto |
| Cause secondarie plausibili | Mancanza alimentazione su pin 3/10, assenza segnale su pin 1/13, problemi speaker/corti, problemi GND |
| Cause non supportate | Speaker cablati male se dal grafo/immagine risultano correttamente tra le coppie BTL |
| Controlli pratici attesi | Misura pin 11, misura pin 3/10, continuità GND, segnale ingresso, speaker/corti |

---

# 4. Confronto risposte per circuito

## `ic3` — confronto sintetico

| Circuito | Modello | Input | Causa principale trovata | Esito | Commento |
|---|---|---|---|---|---|
| `ic3` | `gpt-4o-mini` | JSON + datasheet | Alimentazione non fornita; pin 11 M/SS come seconda causa | Parziale | Capisce il circuito e nota switch25.1 open, ma non dà priorità alla causa più supportata dal JSON. |
| `ic3` | `gpt-4.1-mini` | JSON + datasheet | Pin 11 M/SS non attivo per switch aperto | Sì | Usa bene il JSON e mette al primo posto la causa più supportata dal grafo. |
| `ic3` | `gpt-4.1-nano` | JSON + datasheet | Pin 11 in mute/stand-by | Parziale | Causa corretta, ma meno specifica sullo switch aperto e usa poco i terminali reali del JSON. |
| `ic3` | `gpt-5.4-nano` | JSON + datasheet | Mancanza alimentazione / speaker cablati male | Parziale | Trova anche il pin 11, ma interpreta male i collegamenti BTL degli speaker. |
| `ic3` | `gpt-5.4` | Immagine + datasheet | Pin 11 M/SS non in stato ON | Sì | Ricostruisce bene l’immagine e individua il pin 11 come punto più sospetto. |

---

# 5. Scoring numerico

Usare punteggi da 0 a 3 per ogni criterio.

| Punteggio | Significato |
|---|---|
| 0 | Assente o errato |
| 1 | Presente ma debole/generico |
| 2 | Buono ma con piccoli limiti |
| 3 | Ottimo/corretto/specifico |

## Criteri

| Criterio | Descrizione |
|---|---|
| Comprensione circuito | Capisce la funzione generale del circuito e i blocchi principali. |
| Uso datasheet | Usa correttamente pinout, funzioni dei pin e condizioni operative. |
| Uso JSON / immagine | Usa realmente i collegamenti disponibili nell’input, non solo conoscenza generica. |
| Accuratezza diagnostica | Trova cause coerenti con il guasto. |
| Priorità cause | Ordina correttamente le cause più probabili. |
| Controlli pratici | Propone misure utili e realistiche. |
| Assenza allucinazioni | Non inventa collegamenti, valori o componenti non presenti. |

---

# 6. Tabella punteggi per singolo circuito

## `ic3`

| Modello        | Comprensione circuito | Uso datasheet | Uso JSON/immagine | Accuratezza diagnostica | Priorità cause | Controlli pratici | Assenza allucinazioni | Totale / 21 | Costo stimato |
| -------------- | --------------------: | ------------: | ----------------: | ----------------------: | -------------: | ----------------: | --------------------: | ----------: | ------------: |
| `gpt-4o-mini`  |                     3 |             3 |                 2 |                       2 |              2 |                 2 |                     2 |          16 |       $0.0014 |
| `gpt-4.1-mini` |                     3 |             3 |                 3 |                       3 |              3 |                 3 |                     3 |          21 |       $0.0054 |
| `gpt-4.1-nano` |                     3 |             2 |                 1 |                       2 |              2 |                 2 |                     2 |          14 |       $0.0011 |
| `gpt-5.4-nano` |                     3 |             3 |                 2 |                       2 |              2 |                 3 |                     1 |          16 |       $0.0045 |
| `gpt-5.4`      |                     3 |             3 |                 3 |                       3 |              3 |                 3 |                     3 |          21 |       $0.0446 |


---

# 7. Token e costo

Formula:

costo = input_tokens / 1_000_000 * prezzo_input + output_tokens / 1_000_000 * prezzo_output

| Circuito | Modello        | Input tokens | Output tokens | Total tokens | Costo stimato | File risultato                         |
| -------- | -------------- | -----------: | ------------: | -----------: | ------------: | -------------------------------------- |
| `ic3`    | `gpt-4o-mini`  |         5705 |           845 |         6550 |       $0.0014 | `ic3_gpt-4o-mini_20260513_175319.txt`  |
| `ic3`    | `gpt-4.1-mini` |         5705 |          1955 |         7660 |       $0.0054 | `ic3_gpt-4.1-mini_20260513_182953.txt` |
| `ic3`    | `gpt-4.1-nano` |         5705 |          1406 |         7111 |       $0.0011 | `ic3_gpt-4.1-nano_20260513_191336.txt` |
| `ic3`    | `gpt-5.4-nano` |         5704 |          2685 |         8389 |       $0.0045 | `ic3_gpt-5.4-nano_20260513_191403.txt` |
| `ic3`    | `gpt-5.4`      |         2159 |          2614 |         4773 |       $0.0446 | `ic3_gpt-5.4_20260513_192516.txt`      |


# 8. Tabella aggregata per modello
| Modello        | Numero circuiti testati | Punteggio medio / 21 | Top-1 corretta | Top-3 contiene causa corretta | Errori gravi | Allucinazioni medie | Costo medio per circuito | Note |
| -------------- | ----------------------: | -------------------: | -------------: | ----------------------------: | -----------: | ------------------: | -----------------------: | ---- |
| `gpt-4o-mini`  |                         |                      |                |                               |              |                     |                          |      |
| `gpt-4.1-mini` |                         |                      |                |                               |              |                     |                          |      |
| `gpt-4.1-nano` |                         |                      |                |                               |              |                     |                          |      |
| `gpt-5.4-nano` |                         |                      |                |                               |              |                     |                          |      |
| `gpt-5.4`      |                         |                      |                |                               |              |                     |                          |      |


# 9. Grafici futuri possibili
Grafico 1 — Punteggio medio per modello

Asse X: modello
Asse Y: punteggio medio / 21

Serve per confrontare la qualità diagnostica.

Grafico 2 — Costo medio per circuito

Asse X: modello
Asse Y: costo medio

Serve per mostrare il risparmio dei modelli leggeri.

Grafico 3 — Qualità vs costo

Asse X: costo medio per circuito
Asse Y: punteggio medio

Serve per identificare il miglior compromesso qualità/prezzo.

Grafico 4 — Accuratezza Top-1

Asse X: modello
Asse Y: percentuale di circuiti in cui la causa n.1 è corretta

Serve per valutare se il modello individua subito la causa principale.

Grafico 5 — Errori/allucinazioni

Asse X: modello
Asse Y: numero medio di errori gravi o collegamenti inventati

Serve per valutare affidabilità.