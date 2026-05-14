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
| `ic7` | TDA1516BQ | Amplificatore audio BTL mono | Il circuito non produce audio sullo speaker | TDA1516BQ | Switch M/SS risulta closed; speaker collegato tra OUT1/OUT2; warnings assenti | Schema leggibile, include +12 V, speaker 4 Ω, switch S1 e condensatori di filtro |
| `ic9` | NE555 x2 | Generatore sonoro ding-dong | Il circuito non produce suono sullo speaker | NE555 | Due NE555; alimentazione e reset collegati al nodo positivo; speaker collegato all’uscita del secondo NE555 tramite condensatore | Schema leggibile, include +9 V, due timer NE555, reti RC e speaker da 8 Ω |
| `ic13` | L298 | Driver H-bridge per motore DC | Il motore M non gira | L298 | Motore collegato tra Out 3/Out 4; pin 10 e pin 12 risultano non connessi nei warning; pin 11 collegato a terminale esterno | Schema leggibile, include +Vcc, +5 V, segnali C/D/Ven, motore tra pin 13/14, diodi D1-D4 e condensatori da 100 nF |
| `ic11` | TC4423 | Driver motore DC con dual MOSFET driver | Il motore M1 non gira | TC4423 | Motore collegato tra le due uscite del driver; pin 1 e pin 8 risultano non connessi nei warning, ma dal datasheet sono NC; ingressi Power/Direction collegati a terminali esterni con pull-up | Schema leggibile, include +5 V per pull-up ingressi, alimentazione 10–18 V, motore M1, diodi D1-D4 e condensatori C1/C2 |

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

## Circuito: `ic7`

### Problema

Il circuito non produce audio sullo speaker. Quali sono le cause più probabili?

### Ground truth / valutazione attesa

| Aspetto | Valutazione attesa |
|---|---|
| Funzione del circuito | Amplificatore audio mono in configurazione BTL basato su TDA1516BQ. |
| Causa topologica principale attesa | Verificare che il pin 11 M/SS sia realmente nello stato ON tramite S1/switch. Nel JSON lo switch risulta `closed`, quindi non deve essere considerato sicuramente aperto, ma va comunque controllata la tensione reale sul pin 11. |
| Cause secondarie plausibili | Mancanza alimentazione su pin 10, GND assente su pin 3 o pin 7, assenza segnale audio in ingresso tramite C1, speaker K1 guasto o scollegato, corti sulle uscite pin 5 e pin 9. |
| Cause non supportate | Speaker sicuramente cablato male, se dal JSON/immagine risulta collegato tra pin 5 e pin 9. Switch sicuramente aperto, se dal JSON risulta `closed`. |
| Controlli pratici attesi | Misura tensione pin 11 rispetto a GND, misura alimentazione pin 10, verifica continuità GND su pin 3 e pin 7, verifica speaker tra pin 5 e pin 9, verifica segnale audio in ingresso tramite C1, controllo corti sulle uscite. |

## Circuito: `ic9`

### Problema

Il circuito non produce suono sullo speaker. Quali sono le cause più probabili?

### Ground truth / valutazione attesa

| Aspetto | Valutazione attesa |
|---|---|
| Funzione del circuito | Generatore sonoro “ding-dong” basato su due NE555. |
| Causa topologica principale attesa | Verificare che il secondo NE555 generi un’oscillazione sul pin 3 e che questa arrivi allo speaker tramite il condensatore di uscita. |
| Cause secondarie plausibili | Mancanza +9 V sui pin 8, RESET pin 4 non alto, GND assente sui pin 1, reti RC errate su pin 2/6/7, condensatore di uscita guasto, speaker guasto o scollegato. |
| Cause non supportate | RESET sicuramente a massa, se dal grafo risulta collegato al nodo positivo. |
| Controlli pratici attesi | Misura +9 V sui pin 8, RESET alto sui pin 4, GND sui pin 1, oscillazione sul pin 3 del secondo NE555, continuità condensatore di uscita/speaker. |

## Circuito: `ic13`

### Problema

Il motore M non gira. Quali sono le cause più probabili?

### Ground truth / valutazione attesa

| Aspetto | Valutazione attesa |
|---|---|
| Funzione del circuito | Driver H-bridge per motore DC basato su L298. |
| Causa topologica principale attesa | Verificare che gli ingressi logici del bridge B, pin 10 e pin 12, ricevano comandi validi. Nel JSON risultano non collegati, quindi il motore potrebbe non ricevere alcun comando di direzione. |
| Cause secondarie plausibili | Enable B pin 11 basso o non pilotato, mancanza alimentazione motore su pin 4, mancanza +5 V logica su pin 9, GND/sense pin 15 non corretti, motore scollegato tra pin 13 e 14, diodi di flyback invertiti o guasti, motore bloccato o guasto. |
| Cause non supportate | Motore sicuramente scollegato, se dal JSON/immagine risulta collegato tra pin 13 e pin 14. Alimentazione sicuramente assente, se il grafo mostra i terminali di alimentazione presenti, anche se vanno comunque misurati nel circuito reale. |
| Controlli pratici attesi | Misura VS su pin 4, misura VSS su pin 9, verifica Enable B su pin 11, verifica livelli logici su pin 10 e pin 12, misura tensione tra pin 13 e pin 14 durante il comando, verifica continuità del motore, verifica pin 15 Sense B verso GND, controllo diodi D1-D4. |

## Circuito: `ic11`

### Problema

Il motore M1 non gira. Quali sono le cause più probabili?

### Ground truth / valutazione attesa

| Aspetto | Valutazione attesa |
|---|---|
| Funzione del circuito | Driver per motore DC basato su TC4423, dual high-speed power MOSFET driver. |
| Causa topologica principale attesa | Non emerge un errore topologico evidente dal JSON: gli ingressi Power e Direction sono collegati a terminali esterni, il pin VDD è collegato al nodo di alimentazione, il pin GND è collegato a massa, il motore è collegato tra le due uscite, e i warning riguardano pin NC. Una buona risposta deve quindi concentrarsi sui livelli reali degli ingressi Power/Direction e sulla presenza dell’alimentazione del driver. |
| Cause secondarie plausibili | Assenza alimentazione VDD sul pin 6, assenza GND sul pin 3, livelli logici non validi sui pin 2 e 4, logica invertente del TC4423 non considerata, motore o collegamento sulle uscite pin 7 e pin 5 da verificare, diodi D1-D4 nel percorso di protezione da controllare. |
| Cause non supportate | Considerare pin 1 e pin 8 non connessi come errore: dal datasheet del package 8-pin DIP sono indicati come NC. |
| Controlli pratici attesi | Verificare VDD sul pin 6, GND sul pin 3, livelli logici sui pin 2 e 4, comportamento delle uscite pin 7 e pin 5, corretto uso della logica invertente del TC4423, collegamento del motore tra le uscite. |

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

## `ic7` — confronto sintetico
| Circuito | Modello | Input | Causa principale trovata | Esito | Commento |
|---|---|---|---|---|---|
| `ic7` | `gpt-4o-mini` | JSON + datasheet | Alimentazione assente o inadeguata; pin 11 M/SS come seconda causa | Parziale | Capisce il circuito e propone cause plausibili, ma usa il JSON in modo generico e non valorizza abbastanza lo stato dello switch M/SS. |
| `ic7` | `gpt-4.1-mini` | JSON + datasheet | Pin 1 collegato a Vref/pin 4; pin 11 M/SS e alimentazione come cause secondarie | Parziale | Usa bene il JSON e individua una possibile anomalia sugli ingressi, ma potrebbe interpretare in modo troppo rigido il collegamento pin 1–Vref nella configurazione BTL. Risposta più specifica di `gpt-4o-mini`. |
| `ic7` | `gpt-4.1-nano` | JSON + datasheet | Pin 11 M/SS non in stato ON | Parziale | Risposta corretta e utile, ma abbastanza generica: controlla M/SS, alimentazione e speaker senza usare molto i terminali reali del JSON né valorizzare lo switch closed. |
| `ic7` | `gpt-5.4-nano` | JSON + datasheet | Pin 11 M/SS non realmente in stato ON; alimentazione pin 10 come seconda causa | Sì | Usa bene il JSON, cita terminali reali e interpreta correttamente lo switch closed come elemento da verificare, non come errore certo. Risposta prudente e utile. |
| `ic7` | `gpt-5.4` | Immagine + datasheet | Pin 11 M/SS non in stato ON per problema su S1 o cablaggio | Sì | Ricostruisce bene lo schema dall’immagine: alimentazione, GND, speaker BTL, ingresso C1 e pin M/SS. Segnala anche collegamenti ambigui sui pin 1/4 e 6/8 senza trattarli come certezze. |

## `ic9` — confronto sintetico

| Circuito | Modello | Input | Causa principale trovata | Esito | Commento |
|---|---|---|---|---|---|
| `ic9` | `gpt-4o-mini` | JSON + datasheet | Pin 4 RESET di uno dei NE555 basso; mancanza oscillazione sul pin 3 del secondo NE555 come seconda causa | Parziale | Capisce il circuito a due NE555 e propone controlli utili, ma usa poco il JSON e mette al primo posto una causa non molto supportata dal grafo, dato che i pin RESET sembrano collegati al nodo di alimentazione. |
| `ic9` | `gpt-4.1-mini` | JSON + datasheet | Mancata oscillazione del secondo NE555 sul pin 3; condensatore di uscita come seconda causa | Sì | Usa bene il JSON, riconosce i due NE555, il condensatore di uscita e lo speaker. Diagnosi coerente e controlli pratici utili; piccola imprecisione sul ruolo del collegamento tra IC1 e il pin 5/control voltage di IC2. |
| `ic9` | `gpt-4.1-nano` | JSON + datasheet | Secondo NE555 non oscilla sul pin 3; possibile problema nella rete RC o nei condensatori | Sì | Trova la causa principale attesa e propone controlli utili, ma usa il JSON in modo più generico rispetto a `gpt-4.1-mini` e dà ancora troppo peso al reset. |
| `ic9` | `gpt-5.4-nano` | JSON + datasheet | Mancanza VCC sui pin 8 e RESET pin 4 non alto | No | Interpreta male il JSON: sostiene che VCC e RESET non siano collegati, ma nel grafo risultano connessi al nodo di alimentazione. Riconosce il percorso verso lo speaker, ma la diagnosi principale è fuorviante. |
| `ic9` | `gpt-5.4` | Immagine + datasheet | IC2 non oscilla sul pin 3; collegamento IC2 → C4 → speaker da verificare | Sì | Ricostruisce bene lo schema dall’immagine, riconosce alimentazione/reset corretti e individua correttamente il pin 3 di IC2 come punto chiave. Segnala anche l’interconnessione IC1–IC2 come ambigua. |

## `ic13` — confronto sintetico

| Circuito | Modello | Input | Causa principale trovata | Esito | Commento |
|---|---|---|---|---|---|
| `ic13` | `gpt-4o-mini` | JSON + datasheet | Enable B pin 11 non alto; ingressi pin 10/12 non corretti come seconda causa | Parziale | Capisce il L298 e propone cause plausibili, ma non dà priorità all’evidenza più forte del JSON: pin 10 e pin 12 risultano non connessi nei warning. Alcune osservazioni sui condensatori sono imprecise. |
| `ic13` | `gpt-4.1-mini` | JSON + datasheet | Input 3 pin 10 e Input 4 pin 12 non connessi | Sì | Individua correttamente la causa più supportata dal JSON: i pin 10 e 12 risultano non connessi nei warning. Usa bene datasheet e graph; piccola imprecisione sulla mappatura GND/Sense B, ma la diagnosi principale è corretta. |
| `ic13` | `gpt-4.1-nano` | JSON + datasheet | Segnali di controllo/abilitazione assenti o mal collegati sui pin 10, 12, 11 | Parziale | Capisce il ruolo del L298 e individua i segnali di controllo come causa principale, ma interpreta male il JSON: afferma che pin 10 e 12 sono collegati a terminali esterni, mentre risultano non connessi nei warning. |
| `ic13` | `gpt-5.4-nano` | JSON + datasheet | Input 3 pin 10 e Input 4 pin 12 scollegati/flottanti | Sì | Individua correttamente la causa più supportata dal JSON: pin 10 e pin 12 risultano non connessi. Usa bene i terminali reali e dà priorità ai collegamenti del graph; piccola imprecisione sui condensatori da 100 nF, perché il JSON non contiene i valori. |
| `ic13` | `gpt-5.4` | Immagine + datasheet | Enable B pin 11 non alto; ingressi C/D pin 10/12 non in stati opposti | Sì | Ricostruisce bene lo schema dall’immagine e individua correttamente i segnali critici del bridge B. Non può rilevare i warning JSON sui pin 10/12, ma segnala comunque C/D e Ven come cause principali da verificare. |

## `ic11` — confronto sintetico

| Circuito | Modello | Input | Causa principale trovata | Esito | Commento |
|---|---|---|---|---|---|
| `ic11` | `gpt-4o-mini` | JSON + datasheet | Segnale di controllo IN A assente; alimentazione VDD insufficiente come seconda causa | Parziale | Capisce il circuito e propone cause plausibili, ma usa il JSON in modo incompleto: considera i pin NC 1 e 8 come possibile problema e non analizza bene il secondo ingresso/uscita né la logica invertente del TC4423. |
| `ic11` | `gpt-4.1-mini` | JSON + datasheet | Segnali di ingresso assenti o errati sui pin 2 e 4; VDD pin 6 come seconda causa | Sì | Individua correttamente la causa principale attesa: verificare Power/Direction sui pin 2 e 4 e l’alimentazione VDD. Usa bene il JSON, ma sbaglia sui pin 1 e 8: li considera potenziale problema anche se dal datasheet sono NC. |
| `ic11` | `gpt-4.1-nano` | JSON + datasheet | Alimentazione VDD/GND errata o assente; ingressi IN A/IN B non corretti come seconda causa | Parziale | Propone controlli plausibili e non tratta i pin NC 1/8 come errore, ma sbaglia la mappatura di alcuni pin: considera pin 6 come uscita invece che VDD e non distingue correttamente OUT B su pin 5. |
| `ic11` | `gpt-5.4-nano` | JSON + datasheet | VDD pin 6 non alimentato correttamente; ingressi IN A/IN B come seconda causa | Parziale | Riconosce il TC4423, gli ingressi e la logica invertente, ma dà priorità a un problema VDD poco supportato dal JSON: pin 6 risulta collegato al nodo di alimentazione. Inoltre confonde parzialmente la mappatura tra VDD e uscite. |
| `ic11` | `gpt-5.4` | Immagine + datasheet | Ambiguità TC4423/TC4424 e logica degli ingressi Power/Direction; uscite allo stesso potenziale come seconda causa | Sì | Ricostruisce bene lo schema dall’immagine, identifica correttamente pinout, alimentazione, ingressi e uscite. Rileva la contraddizione TC4423/TC4424, importante perché cambia la logica invertente/non invertente. |

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


## `ic7`

| Modello | Comprensione circuito | Uso datasheet | Uso JSON/immagine | Accuratezza diagnostica | Priorità cause | Controlli pratici | Assenza allucinazioni | Totale / 21 | Costo stimato |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `gpt-4o-mini` | 3 | 2 | 2 | 2 | 2 | 2 | 2 | 15 | $0.0014 |
| `gpt-4.1-mini` | 3 | 3 | 3 | 2 | 2 | 3 | 2 | 18 | $0.0049 |
| `gpt-4.1-nano` | 3 | 2 | 1 | 2 | 2 | 2 | 2 | 14 | $0.0011 |
| `gpt-5.4-nano` | 3 | 3 | 3 | 3 | 3 | 3 | 3 | 21 | $0.0036 |
| `gpt-5.4` | 3 | 3 | 3 | 3 | 3 | 3 | 3 | 21 | $0.0525 |



## `ic9`

| Modello | Comprensione circuito | Uso datasheet | Uso JSON/immagine | Accuratezza diagnostica | Priorità cause | Controlli pratici | Assenza allucinazioni | Totale / 21 | Costo stimato |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `gpt-4o-mini` | 3 | 2 | 1 | 2 | 1 | 2 | 2 | 13 | $0.0016 |
| `gpt-4.1-mini` | 3 | 3 | 3 | 3 | 3 | 3 | 2 | 20 | $0.0060 |
| `gpt-4.1-nano` | 3 | 2 | 2 | 3 | 2 | 2 | 2 | 16 | $0.0013 |
| `gpt-5.4-nano` | 3 | 2 | 1 | 1 | 0 | 2 | 0 | 9 | $0.0045 |
| `gpt-5.4` | 3 | 3 | 3 | 3 | 3 | 3 | 2 | 20 | $0.0525 |

## `ic13`

| Modello | Comprensione circuito | Uso datasheet | Uso JSON/immagine | Accuratezza diagnostica | Priorità cause | Controlli pratici | Assenza allucinazioni | Totale / 21 | Costo stimato |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `gpt-4o-mini` | 3 | 3 | 2 | 2 | 2 | 2 | 1 | 15 | $0.0014 |
| `gpt-4.1-mini` | 3 | 3 | 3 | 3 | 3 | 3 | 2 | 20 | $0.0049 |
| `gpt-4.1-nano` | 3 | 2 | 1 | 2 | 2 | 2 | 1 | 13 | $0.0011 |
| `gpt-5.4-nano` | 3 | 3 | 3 | 3 | 3 | 3 | 2 | 20 | $0.0039 |
| `gpt-5.4` | 3 | 3 | 3 | 3 | 2 | 3 | 3 | 20 | $0.0535 |

## `ic11`

| Modello | Comprensione circuito | Uso datasheet | Uso JSON/immagine | Accuratezza diagnostica | Priorità cause | Controlli pratici | Assenza allucinazioni | Totale / 21 | Costo stimato |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `gpt-4o-mini` | 2 | 2 | 1 | 2 | 2 | 2 | 1 | 12 | $0.0014 |
| `gpt-4.1-mini` | 3 | 2 | 3 | 3 | 3 | 3 | 1 | 18 | $0.0057 |
| `gpt-4.1-nano` | 2 | 1 | 1 | 2 | 2 | 2 | 1 | 11 | $0.0012 |
| `gpt-5.4-nano` | 2 | 2 | 2 | 2 | 1 | 3 | 1 | 13 | $0.0045 |
| `gpt-5.4` | 3 | 3 | 3 | 3 | 3 | 3 | 2 | 20 | $0.0515 |

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
| `ic7` | `gpt-4o-mini` | 5197 | 973 | 6170 | $0.0014 | `ic7_gpt-4o-mini_20260514_085213.txt` |
| `ic7` | `gpt-4.1-mini` | 5197 | 1778 | 6975 | $0.0049 | `ic7_gpt-4.1-mini_20260514_085402.txt` |
| `ic7` | `gpt-4.1-nano` | 5197 | 1512 | 6709 | $0.0011 | `ic7_gpt-4.1-nano_20260514_085301.txt` |
| `ic7` | `gpt-5.4-nano` | 5196 | 2083 | 7279 | $0.0036 | `ic7_gpt-5.4-nano_20260514_085436.txt` |
| `ic7` | `gpt-5.4` | 2432 | 3093 | 5525 | $0.0525 | `ic7_gpt-5.4_20260514_091644.txt` |
| `ic9` | `gpt-4o-mini` | 6981 | 930 | 7911 | $0.0016 | `ic9_gpt-4o-mini_20260514_092449.txt` |
| `ic9` | `gpt-4.1-mini` | 6981 | 2003 | 8984 | $0.0060 | `ic9_gpt-4.1-mini_20260514_092544.txt` |
| `ic9` | `gpt-4.1-nano` | 6981 | 1543 | 8524 | $0.0013 | `ic9_gpt-4.1-nano_20260514_092615.txt` |
| `ic9` | `gpt-5.4-nano` | 6980 | 2462 | 9442 | $0.0045 | `ic9_gpt-5.4-nano_20260514_092705.txt` |
| `ic9` | `gpt-5.4` | 2561 | 3075 | 5636 | $0.0525 | `ic9_gpt-5.4_20260514_092801.txt` |
| `ic13` | `gpt-4o-mini` | 5082 | 1028 | 6110 | $0.0014 | `ic13_gpt-4o-mini_20260514_101637.txt` |
| `ic13` | `gpt-4.1-mini` | 5082 | 1766 | 6848 | $0.0049 | `ic13_gpt-4.1-mini_20260514_101725.txt` |
| `ic13` | `gpt-4.1-nano` | 5082 | 1582 | 6664 | $0.0011 | `ic13_gpt-4.1-nano_20260514_101752.txt` |
| `ic13` | `gpt-5.4-nano` | 5081 | 2277 | 7358 | $0.0039 | `ic13_gpt-5.4-nano_20260514_101833.txt` |
| `ic13` | `gpt-5.4` | 2282 | 3189 | 5471 | $0.0535 | `ic13_gpt-5.4_20260514_102117.txt` |
| `ic11` | `gpt-4o-mini` | 5475 | 971 | 6446 | $0.0014 | `ic11_gpt-4o-mini_20260514_104325.txt` |
| `ic11` | `gpt-4.1-mini` | 5475 | 2182 | 7657 | $0.0057 | `ic11_gpt-4.1-mini_20260514_104429.txt` |
| `ic11` | `gpt-4.1-nano` | 5475 | 1639 | 7114 | $0.0012 | `ic11_gpt-4.1-nano_20260514_104455.txt` |
| `ic11` | `gpt-5.4-nano` | 5474 | 2713 | 8187 | $0.0045 | `ic11_gpt-5.4-nano_20260514_104530.txt` |
| `ic11` | `gpt-5.4` | 2426 | 3032 | 5458 | $0.0515 | `ic11_gpt-5.4_20260514_104633.txt` |


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