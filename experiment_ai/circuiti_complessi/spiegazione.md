# Protocollo sperimentale per il confronto di modelli AI nel troubleshooting circuitale

## 1. Obiettivo dell’esperimento

L’obiettivo dell’esperimento è valutare se una rappresentazione strutturata del circuito, fornita sotto forma di JSON/graph, consente a modelli linguistici leggeri o meno costosi di ottenere prestazioni diagnostiche comparabili a modelli più avanzati che ricevono direttamente anche l’immagine dello schema elettrico.

In particolare, si vuole confrontare la qualità delle risposte diagnostiche ottenute fornendo ai modelli due diverse configurazioni di input:

1. **JSON + datasheet**
2. **JSON + immagine dello schema + datasheet**

Il confronto permette di valutare:

- quanto il JSON topologico aiuta il modello nella comprensione del circuito;
- quanto migliora la diagnosi quando, oltre al JSON, viene fornita anche l’immagine;
- quali modelli offrono il miglior compromesso tra qualità, costo e latenza;
- se modelli mini/nano possono essere sufficienti per compiti di troubleshooting circuitale;
- quanto i modelli sono robusti su circuiti di natura diversa.

---

## 2. Idea generale

Per ogni circuito viene simulato un sintomo realistico, ad esempio:

- lo speaker non emette audio;
- il motore non gira;
- il generatore sonoro non produce suono.

Non si assume necessariamente che il circuito reale sia errato. Il sintomo rappresenta uno scenario di troubleshooting: il modello deve analizzare il circuito e proporre le cause più probabili del problema, ordinandole per rilevanza e indicando controlli pratici.

Il modello riceve:

- il datasheet o un estratto rigoroso del datasheet;
- la rappresentazione JSON del circuito;
- opzionalmente, anche l’immagine dello schema elettrico;
- il sintomo da analizzare.

---

## 3. Modelli confrontati

I modelli scelti appartengono principalmente alle famiglie mini e nano, con l’aggiunta di un modello più avanzato come baseline.

| Modello | Categoria | Ruolo nell’esperimento |
|---|---|---|
| `gpt-4o-mini` | modello economico precedente | Baseline leggera già testata nei primi esperimenti. |
| `gpt-4.1-mini` | modello mini 4.1 | Modello leggero ma affidabile, già risultato buono nei test preliminari. |
| `gpt-4.1-nano` | modello nano 4.1 | Test limite per valutare quanto il JSON semplifica il compito. |
| `gpt-5-nano` | modello nano moderno | Verifica delle prestazioni ottenibili con un modello moderno ultra-leggero. |
| `gpt-5-mini` | modello mini moderno | Compromesso tra costo, qualità e capacità di ragionamento. |
| `gpt-5.4-nano` | modello nano moderno | Modello compatto già testato, con risultati variabili a seconda del circuito. |
| `gpt-5.4-mini` | modello mini moderno | Modello mini più recente, potenzialmente molto competitivo. |
| `gpt-5.4` | modello avanzato | Baseline forte per valutare il limite superiore della qualità. |

---

## 4. Configurazioni di input

Ogni modello viene testato con due configurazioni.

## 4.1 JSON + datasheet

In questa configurazione il modello riceve:

- il JSON del circuito;
- il datasheet;
- il sintomo.

L’obiettivo è verificare quanto il modello riesce a usare la rappresentazione strutturata del circuito.

Questa configurazione misura principalmente:

- capacità di interpretare il graph;
- capacità di collegare pin, componenti e net;
- capacità di usare il datasheet in modo coerente;
- capacità diagnostica senza immagine.

## 4.2 JSON + immagine + datasheet

In questa configurazione il modello riceve:

- il JSON del circuito;
- l’immagine dello schema;
- il datasheet;
- il sintomo.

L’obiettivo è valutare se l’aggiunta dell’immagine migliora la diagnosi rispetto al solo JSON.

Questa configurazione permette al modello di:

- verificare visivamente componenti e valori;
- correggere eventuali limiti del JSON;
- usare sia la topologia strutturata sia la rappresentazione visiva;
- riconoscere ambiguità tra immagine e graph.

---

## 5. Circuiti analizzati

I circuiti scelti coprono più tipologie funzionali, in modo da non limitare l’esperimento a un solo dominio.

| Circuito | IC principale | Tipo circuito | Sintomo usato |
|---|---|---|---|
| `ic3` | TDA1553Q | Amplificatore audio BTL | Il circuito non produce audio sugli altoparlanti. |
| `ic7` | TDA1516BQ | Amplificatore audio BTL mono | Il circuito non produce audio sullo speaker. |
| `ic9` | NE555 x2 | Generatore sonoro ding-dong | Il circuito non produce suono sullo speaker. |
| `ic13` | L298 | Driver H-bridge per motore DC | Il motore M non gira. |
| `ic11` | TC4423 | Driver motore DC con dual MOSFET driver | Il motore M1 non gira. |

Eventuali circuiti aggiuntivi potranno essere inseriti successivamente per aumentare la varietà e la complessità del dataset.

---

## 6. Esecuzioni sperimentali

Per ogni circuito vengono eseguite due serie di test.

## 6.1 Test con JSON + datasheet

Per ogni circuito e per ogni modello:

input = JSON + datasheet + sintomo
Il risultato viene salvato nella cartella: results_json/

# 6.2 Test con JSON + immagine + datasheet
Per ogni circuito e per ogni modello:
input = JSON + immagine + datasheet + sintomo
Il risultato viene salvato nella cartella:
results_json_img/

# 7. Matrice sperimentale
| Circuito | Modello        | JSON + datasheet | JSON + immagine + datasheet |
| -------- | -------------- | ---------------- | --------------------------- |
| `ic3`    | `gpt-4o-mini`  | sì               | sì                          |
| `ic3`    | `gpt-4.1-mini` | sì               | sì                          |
| `ic3`    | `gpt-4.1-nano` | sì               | sì                          |
| `ic3`    | `gpt-5-nano`   | sì               | sì                          |
| `ic3`    | `gpt-5-mini`   | sì               | sì                          |
| `ic3`    | `gpt-5.4-nano` | sì               | sì                          |
| `ic3`    | `gpt-5.4-mini` | sì               | sì                          |
| `ic3`    | `gpt-5.4`      | sì               | sì                          |

# 8. Informazioni salvate per ogni esecuzione
Ogni file risultato deve contenere almeno:
| Campo             | Descrizione                             |
| ----------------- | --------------------------------------- |
| `MODELLO`         | Nome del modello utilizzato.            |
| `CIRCUITO`        | Identificativo del circuito.            |
| `INPUT`           | Tipologia di input usato.               |
| `JSON`            | Percorso del file JSON, se usato.       |
| `IMMAGINE`        | Percorso dell’immagine, se usata.       |
| `DATASHEET`       | Percorso del datasheet testuale.        |
| `PROBLEMA`        | Sintomo fornito al modello.             |
| `LATENCY_SECONDS` | Tempo di esecuzione della chiamata API. |
| `USAGE`           | Token usati dalla chiamata.             |
| `RISPOSTA`        | Output testuale generato dal modello.   |

# 9. Token e costo
Per ogni run vengono salvati:

- input tokens;
- output tokens;
- total tokens;
- eventuali cached tokens;
- costo stimato.

La formula generale per il costo è:
costo = input_tokens / 1_000_000 × prezzo_input + output_tokens / 1_000_000 × prezzo_output

Il costo va calcolato usando i prezzi API corrispondenti al modello utilizzato.

# 10. Latenza

La latenza viene misurata direttamente nello script tramite cronometro.

La metrica salvata è: LATENCY_SECONDS
Questa metrica rappresenta il tempo totale impiegato dalla chiamata API, dalla richiesta fino alla ricezione della risposta.

La latenza è importante perché due modelli con qualità simile possono avere efficienza pratica molto diversa.

Per i risultati preliminari ottenuti prima dell’aggiunta di LATENCY_SECONDS, la latenza non può essere ricavata in modo rigoroso dai token. Tali risultati vengono quindi considerati preliminari e non usati nei grafici finali relativi al tempo di esecuzione.

# 11. Valutazione tramite judge

Dopo aver raccolto tutti gli output, verrà usato un modello judge separato per valutare in modo uniforme le risposte generate.

Il judge riceverà:

- immagine del circuito;
- JSON del circuito;
- datasheet;
- sintomo;
- output del modello da valutare.

Il judge dovrà assegnare punteggi su più criteri, senza sapere quale modello ha generato la risposta, per ridurre il bias.

# 12. Criteri di valutazione

Ogni risposta verrà valutata secondo criteri numerici.
| Criterio                | Descrizione                                                                                               |
| ----------------------- | --------------------------------------------------------------------------------------------------------- |
| Comprensione circuito   | Il modello capisce la funzione generale del circuito e i blocchi principali.                              |
| Uso datasheet           | Il modello usa correttamente pinout, funzioni dei pin, soglie e condizioni operative lette dal datasheet. |
| Uso JSON / immagine     | Il modello usa realmente i collegamenti presenti nell’input, senza basarsi solo su conoscenza generica.   |
| Accuratezza diagnostica | Le cause proposte sono coerenti con il sintomo e con il circuito.                                         |
| Priorità cause          | Le cause più probabili vengono ordinate correttamente.                                                    |
| Controlli pratici       | Il modello propone verifiche realistiche e utili sul circuito reale.                                      |
| Assenza allucinazioni   | Il modello non inventa componenti, collegamenti, valori o difetti non supportati.                         |

Scala proposta:
| Punteggio | Significato                       |
| --------: | --------------------------------- |
|         0 | Assente o errato                  |
|         1 | Debole o molto generico           |
|         2 | Buono ma con limiti               |
|         3 | Molto buono, corretto e specifico |

Score massimo: 7 criteri × 3 punti = 21 punti

# 13. Output atteso del judge
Il judge dovrebbe restituire un output strutturato, ad esempio in formato JSON: 
```
{
  "circuit_understanding": 0,
  "datasheet_use": 0,
  "json_image_use": 0,
  "diagnostic_accuracy": 0,
  "cause_priority": 0,
  "practical_checks": 0,
  "hallucination_absence": 0,
  "overall_score": 0,
  "top1_correct": true,
  "top3_contains_correct": true,
  "major_errors": [],
  "short_explanation": ""
}
```
# 14. Dataset finale

Alla fine, tutti i risultati verranno raccolti in una tabella unica.

Esempio di struttura:
| Circuito | Modello        | Input type                  | Score | Top-1 correct | Top-3 correct | Input tokens | Output tokens | Costo | Latenza |
| -------- | -------------- | --------------------------- | ----: | ------------- | ------------- | -----------: | ------------: | ----: | ------: |
| `ic3`    | `gpt-4.1-mini` | JSON + datasheet            |       |               |               |              |               |       |         |
| `ic3`    | `gpt-4.1-mini` | JSON + immagine + datasheet |       |               |               |              |               |       |         |

Analisi aggregate
# 15. Metriche aggregate per modello

Per ogni modello verranno calcolati:
| Metrica             | Significato                                                            |
| ------------------- | ---------------------------------------------------------------------- |
| Score medio         | Qualità media delle risposte.                                          |
| Score mediano       | Prestazione tipica, meno sensibile agli outlier.                       |
| Deviazione standard | Stabilità del modello sui vari circuiti.                               |
| Top-1 accuracy      | Percentuale di casi in cui la prima causa proposta è corretta.         |
| Top-3 accuracy      | Percentuale di casi in cui la causa corretta compare tra le prime tre. |
| Errori gravi medi   | Frequenza media di errori rilevanti.                                   |
| Costo medio         | Costo medio per esecuzione.                                            |
| Latenza media       | Tempo medio di risposta.                                               |
| Quality per dollar  | Rapporto qualità/costo.                                                |
| Quality per second  | Rapporto qualità/latenza.                                              |

# 16. Metriche aggregate per input type
Si confronteranno separatamente: JSON + datasheet

contro: JSON + immagine + datasheet

Per ogni configurazione si calcoleranno:
- score medio;
- score mediano;
- deviazione standard;
- accuratezza top-1;
- accuratezza top-3;
- costo medio;
- latenza media.

Questo permetterà di misurare quanto l’aggiunta dell’immagine migliora le prestazioni rispetto al solo JSON.

# 17. Metriche per criterio

Oltre allo score totale, si analizzeranno i singoli criteri.
| Modello        | Comprensione circuito | Uso datasheet | Uso JSON/immagine | Accuratezza diagnostica | Priorità cause | Controlli pratici | Assenza allucinazioni |
| -------------- | --------------------: | ------------: | ----------------: | ----------------------: | -------------: | ----------------: | --------------------: |
| `gpt-4.1-mini` |                       |               |                   |                         |                |                   |                       |
| `gpt-5.4-nano` |                       |               |                   |                         |                |                   |                       |

Grafici possibili
## 18. Score medio per modello

Tipo grafico: bar chart

Asse X: modello

Asse Y: score medio

Obiettivo:
- confrontare la qualità diagnostica media dei modelli;
- individuare i modelli migliori in termini assoluti.
## 19. Score medio per input type

Tipo grafico: bar chart

Asse X: input type

Asse Y: score medio

Confronto:

JSON + datasheet
vs
JSON + immagine + datasheet

Obiettivo:

- misurare il contributo dell’immagine;
- capire se il JSON da solo è sufficiente in molti casi.
## 20. Score per modello e input type

Tipo grafico: grouped bar chart

Asse X: modello

Barre: 
- JSON + datasheet
- JSON + immagine + datasheet

Asse Y: score medio

Obiettivo:

- confrontare, per ogni modello, quanto migliora aggiungendo l’immagine;
- vedere se i modelli nano beneficiano più o meno dei modelli mini.
## 21. Delta di miglioramento con immagine

Per ogni modello si può calcolare:

- delta_score = score(JSON + immagine + datasheet) - score(JSON + datasheet)

Tipo grafico: bar chart

Obiettivo:

- misurare il guadagno dovuto all’immagine;
- capire quali modelli sfruttano meglio l’informazione visiva.
# 22. Costo medio per modello

Tipo grafico: bar chart

Asse X: modello

Asse Y: costo medio per run

Obiettivo:

- confrontare il costo economico medio dei modelli;
- evidenziare i modelli più convenienti.
## 23. Latenza media per modello

Tipo grafico: bar chart

Asse X: modello

Asse Y: latenza media in secondi

Obiettivo:

- confrontare la velocità dei modelli;
- valutare la praticabilità in uno scenario reale.
## 24. Score vs costo

Tipo grafico: scatter plot

Asse X: costo medio

Asse Y: score medio

Ogni punto rappresenta un modello.

Obiettivo:

- individuare il miglior compromesso qualità/prezzo;
- evidenziare modelli che costano poco ma ottengono score elevati.
## 25. Score vs latenza

Tipo grafico: scatter plot

Asse X: latenza media

Asse Y: score medio

Obiettivo:

- individuare modelli veloci ma accurati;
- valutare il compromesso qualità/tempo.
## 26. Quality per dollar

Formula: quality_per_dollar = score_medio / costo_medio

Tipo grafico: bar chart

Obiettivo:

- mostrare quale modello produce più qualità per unità di costo.
## 27. Quality per second

Formula: quality_per_second = score_medio / latenza_media

Tipo grafico: bar chart

Obiettivo:

- mostrare quale modello produce più qualità per unità di tempo.
## 28. Heatmap modello × circuito

Tipo grafico: heatmap

Righe: modelli

Colonne: circuiti

Valore: score medio

Obiettivo:

- capire quali circuiti sono più difficili;
- individuare modelli robusti su più tipologie circuitali.

## 29. Heatmap modello × criterio

Tipo grafico: heatmap

Righe: modelli

Colonne: criteri di valutazione

Valore: score medio del criterio

Obiettivo:

- evidenziare punti forti e deboli di ogni modello;
- distinguere modelli che capiscono il circuito da modelli che fanno diagnosi generiche.

## 30. Top-1 accuracy per modello

Tipo grafico: bar chart

Asse X: modello

Asse Y: percentuale top-1 corretta

Obiettivo:

- valutare se il modello identifica subito la causa più probabile.
## 31. Top-3 accuracy per modello

Tipo grafico: bar chart

Asse X: modello

Asse Y: percentuale top-3 corretta

Obiettivo:
- valutare se il modello include comunque la causa corretta tra le principali.

## 32. Errori gravi per modello

Tipo grafico: bar chart

Asse X: modello

Asse Y: numero medio di errori gravi

Obiettivo:

- misurare affidabilità e rischio di risposte fuorvianti;
- identificare modelli che allucinano collegamenti o interpretano male il JSON.
## 33. Boxplot degli score per modello

Tipo grafico: boxplot

Asse X: modello

Asse Y: score

Obiettivo:

- osservare distribuzione, mediana e variabilità degli score;
- capire se un modello è stabile oppure molto variabile tra circuiti diversi.
## 34. Boxplot degli score per input type

Tipo grafico: boxplot

Asse X: input type

Asse Y: score

Obiettivo:
- confrontare la distribuzione delle prestazioni tra JSON-only e JSON+immagine.
## 35. Distribuzione della latenza

Tipo grafico: boxplot o histogram

Obiettivo:

- analizzare la variabilità dei tempi di risposta;
- capire se alcuni modelli hanno latenze molto instabili.
## 36. Distribuzione del costo

Tipo grafico: boxplot o bar chart

Obiettivo:

- analizzare quanto costa mediamente una diagnosi;
- valutare differenze tra modelli mini, nano e baseline avanzata.