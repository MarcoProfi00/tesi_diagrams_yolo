# Tabelle finali della valutazione CHAT–AGENT

## Scopo e sorgenti

Questa cartella raccoglie le tabelle derivate dai 42 risultati ufficiali in
`judge_results`: 21 circuiti valutati una volta in modalità CHAT e una volta in
modalità AGENT. I risultati pilota presenti in
`judge_results_process_calibrated` non entrano in nessuna tabella.

Il sistema viene valutato prima nel complesso e successivamente per modalità.
Il confronto CHAT–AGENT è descrittivo: serve a mostrare il diverso comportamento
della modalità guidata e di quella autonoma, non a stabilire un vincitore.

## Scala di valutazione

Ogni run riceve cinque punteggi interi compresi tra 0 e 2:

- **0 — errato o assente:** il criterio non è soddisfatto oppure è contrario
  alle evidenze;
- **1 — utile ma incompleto:** esiste un contributo corretto, ma con omissioni,
  limiti o errori rilevanti;
- **2 — corretto e verificato:** il criterio è soddisfatto con evidenze
  sufficienti.

I cinque criteri sono:

1. **Correttezza diagnostica:** correttezza della causa, del comportamento o
   della localizzazione individuata.
2. **Qualità dei test:** pertinenza e capacità degli scenari eseguiti di
   distinguere le ipotesi importanti.
3. **Interpretazione delle evidenze:** correttezza con cui misure SPICE,
   transitori e confronti vengono letti.
4. **Raggiungimento dell'obiettivo:** misura in cui la richiesta dell'utente è
   stata soddisfatta.
5. **Qualità della conclusione:** chiarezza, correttezza e prudenza della
   risposta finale.

La somma produce un punteggio descrittivo compreso tra **0 e 10**. L'esito non
dipende meccanicamente dal totale: una falsa correzione centrale può determinare
`failure` anche quando alcuni test ricevono credito.

## Esiti

- **Successo (`success`):** obiettivo raggiunto con conclusione corretta e prove
  sufficienti.
- **Successo parziale (`partial_success`):** almeno un contributo corretto e
  materialmente utile, ma obiettivo incompleto o conclusione con limiti
  rilevanti.
- **Fallimento (`failure`):** nessun risultato concretamente utilizzabile oppure
  falsa soluzione contraria alle evidenze come risultato sostanziale.
- **Inconcludente (`inconclusive`):** dati insufficienti per una decisione.
- **Fallimento tecnico (`technical_failure`):** traiettoria non valutabile.

Nel seguito, **risultato utile** indica esclusivamente `success +
partial_success`. Non significa che la diagnosi sia sempre completamente
corretta: un successo parziale può richiedere supervisione, soprattutto quando
sono presenti errori critici.

## Errori critici

- `false_success`: viene dichiarata una soluzione non realmente dimostrata;
- `unsupported_claim`: viene affermata una causa o un effetto non sostenuto;
- `wrong_interpretation`: una misura viene interpretata in modo incompatibile
  con le evidenze.

Un errore critico impedisce il successo pieno quando compromette il risultato,
ma può coesistere con un successo parziale se la traiettoria conserva un
contributo indipendente e utile.

## Risultati principali

| Modalità | Run | Successi | Parziali | Fallimenti | Risultati utili | Media /10 | Run con criticità |
| --- | --- | --- | --- | --- | --- | --- | --- |
| CHAT | 21 | 11 (52,4%) | 10 | 0 | 21 (100,0%) | 7,81 | 5 (23,8%) |
| AGENT | 21 | 5 (23,8%) | 15 | 1 | 20 (95,2%) | 6,38 | 12 (57,1%) |
| Complessivo | 42 | 16 (38,1%) | 25 | 1 | 41 (97,6%) | 7,10 | 17 (40,5%) |

Il sistema completa tecnicamente tutte le run e produce un risultato utile in
**41/42 casi (97,6%)**. CHAT produce un risultato utile in 21/21 casi; AGENT in
20/21. Il singolo fallimento semantico è c02 in modalità AGENT.

## Risultati appaiati per circuito

| Circuito | CHAT | Punti | AGENT | Punti | Δ A−C | Criticità AGENT |
| --- | --- | --- | --- | --- | --- | --- |
| a01 | Successo | 10 | Successo | 10 | +0 | — |
| a02 | Successo parziale | 7 | Successo parziale | 7 | +0 | unsupported_claim |
| a04 | Successo | 8 | Successo parziale | 7 | -1 | wrong_interpretation |
| a05 | Successo | 10 | Successo | 10 | +0 | — |
| a06 | Successo | 10 | Successo parziale | 6 | -4 | unsupported_claim, wrong_interpretation |
| a07 | Successo | 10 | Successo | 10 | +0 | — |
| a08 | Successo | 10 | Successo parziale | 4 | -6 | unsupported_claim, wrong_interpretation |
| a09 | Successo | 10 | Successo parziale | 8 | -2 | — |
| a10 | Successo parziale | 7 | Successo | 10 | +3 | — |
| b02 | Successo | 10 | Successo parziale | 4 | -6 | unsupported_claim, wrong_interpretation |
| b03 | Successo parziale | 6 | Successo parziale | 7 | +1 | — |
| b04 | Successo parziale | 6 | Successo parziale | 4 | -2 | unsupported_claim, wrong_interpretation |
| b05 | Successo parziale | 5 | Successo parziale | 4 | -1 | unsupported_claim, wrong_interpretation |
| b06 | Successo | 9 | Successo parziale | 5 | -4 | — |
| b10 | Successo parziale | 5 | Successo parziale | 5 | +0 | wrong_interpretation |
| c02 | Successo parziale | 6 | Fallimento | 2 | -4 | false_success, unsupported_claim, wrong_interpretation |
| c03 | Successo parziale | 5 | Successo parziale | 4 | -1 | unsupported_claim, wrong_interpretation |
| ic01 | Successo | 8 | Successo | 10 | +2 | — |
| ic02 | Successo parziale | 7 | Successo parziale | 5 | -2 | — |
| ic03 | Successo | 10 | Successo parziale | 8 | -2 | unsupported_claim |
| ic04 | Successo parziale | 5 | Successo parziale | 4 | -1 | unsupported_claim, wrong_interpretation |

La colonna Δ A−C è la differenza descrittiva tra punteggio AGENT e punteggio
CHAT. Valori positivi indicano un punteggio AGENT maggiore, valori negativi un
punteggio CHAT maggiore.

## Punteggio medio dei criteri

| Criterio | CHAT /2 | AGENT /2 | Complessivo /2 |
| --- | --- | --- | --- |
| Correttezza diagnostica | 1,67 | 1,43 | 1,55 |
| Qualità dei test | 1,62 | 1,52 | 1,57 |
| Interpretazione delle evidenze | 1,57 | 1,24 | 1,40 |
| Raggiungimento dell'obiettivo | 1,52 | 1,29 | 1,40 |
| Qualità della conclusione | 1,43 | 0,90 | 1,17 |

La qualità dei test è il punto più forte di AGENT. La qualità della conclusione
è invece il criterio più debole: la modalità autonoma riesce generalmente a
eseguire prove pertinenti, ma è più fragile nell'attribuzione causale e nella
sintesi finale.

## Frequenza degli errori critici

| Errore critico | CHAT | AGENT | Totale |
| --- | --- | --- | --- |
| false_success | 0 | 1 | 1 |
| unsupported_claim | 1 | 10 | 11 |
| wrong_interpretation | 5 | 10 | 15 |

Le occorrenze non coincidono con il numero di run critiche, perché una stessa
run può contenere più categorie di errore.

## Token e costo del judge

| Modalità | Input | Input cached | Output | Reasoning* | Costo stimato USD |
| --- | --- | --- | --- | --- | --- |
| CHAT | 157107 | 32512 | 45114 | 22432 | 1,9927 |
| AGENT | 138285 | 58624 | 44397 | 22980 | 1,7595 |
| Totale | 295392 | 91136 | 89511 | 45412 | 3,7522 |

Nota: i reasoning token sono già compresi negli output token e non vengono
addebitati una seconda volta. La stima usa 5 USD/M token input non cached,
0,50 USD/M cached input e 30 USD/M output per GPT-5.5.

## File CSV prodotti

### `table_01_run_results.csv`

Una riga per ciascuna delle 42 run. Contiene:

- identificativo del circuito e modalità;
- esito, risultato utile e punteggio totale;
- cinque punteggi individuali;
- numero e tipi di errori critici;
- scenari proposti/eseguiti e run SPICE riuscite/fallite;
- turni intermedi dell'utente oppure decisioni autonome;
- modello, latenza, token, costo e hash di provenienza.

### `table_02_paired_results.csv`

Una riga per circuito con CHAT e AGENT affiancati. È la base per grafici a
barre appaiate, differenze di punteggio e conteggio dei casi in cui entrambe le
modalità forniscono un risultato utile.

### `table_03_mode_summary.csv`

Tre righe: CHAT, AGENT e complessivo. Riporta esiti, tassi, media, mediana,
criticità, token, costo e hash del prompt.

### `table_04_criteria_summary.csv`

Distribuzione 0/1/2 e media di ciascun criterio per CHAT, AGENT e totale. È la
base per un grafico a barre dei cinque criteri.

### `table_05_outcome_summary.csv`

Conteggi e percentuali dei cinque esiti. È la base per grafici a barre o barre
impilate.

### `table_06_critical_errors.csv`

Numero e frequenza delle tre categorie di errore critico per modalità e nel
complesso.

## Campi principali dei CSV

- `circuit_id`: identificativo del circuito;
- `mode`: `chat` oppure `agent`;
- `outcome`: esito semantico del judge;
- `useful_result`: vero per successo o successo parziale;
- `total_score`: somma dei cinque criteri, massimo 10;
- `score_*`: punteggio 0–2 del criterio indicato;
- `outcome_reason`: motivazione sintetica dell'esito;
- `reason_*`: motivazione assegnata dal judge al singolo criterio;
- `decisive_evidence`: evidenze considerate decisive dal judge;
- `critical_errors`: categorie separate dal carattere `|`;
- `scenarios_proposed` / `scenarios_executed`: prove pianificate ed eseguite;
- `successful_spice_runs` / `failed_spice_runs`: riuscita tecnica degli scenari;
- `intermediate_user_turns`: interventi intermedi dell'utente in CHAT;
- `agent_decisions_count`: decisioni autonome in AGENT;
- `latency_seconds`: durata della chiamata al judge, non dell'intera diagnosi;
- `input_tokens`, `cached_input_tokens`, `output_tokens`: consumo del judge;
- `reasoning_tokens`: quota di ragionamento già inclusa negli output token;
- `estimated_cost_usd`: costo stimato della chiamata al judge;
- `packet_sha256`, `prompt_sha256`, `response_schema_sha256`: identificatori
  riproducibili degli input e del protocollo.

## Provenienza e limite di comparabilità

Hash prompt CHAT:

```text
c73bff5fc793c0ce94252c188e73dbdb7b3bc5b96d4e3ebf7ad945a493d69455
```

Hash prompt AGENT:

```text
05304a5537b64fedb8f52486119342f1842b27168a44aed2a27dd134c9ef17b5
```

La calibrazione AGENT attribuisce esplicitamente credito alle parti corrette
dell'intera traiettoria autonoma, senza trasformare una conclusione errata in
successo pieno. Poiché gli hash dei prompt sono differenti, il confronto dei
punteggi CHAT–AGENT deve essere presentato come **secondario e descrittivo**.
Le valutazioni principali per modalità restano invece pienamente interpretabili.

## Limiti della valutazione

- È disponibile una sola traiettoria per modalità e circuito: non viene stimata
  la variabilità tra nuove generazioni del modello linguistico.
- Il judge è un modello linguistico; ground truth, casi anomali e calibrazione
  sono stati quindi controllati manualmente.
- Le simulazioni dimostrano il comportamento dei modelli SPICE e delle
  assunzioni adottate, non garantiscono automaticamente il comportamento di un
  circuito fisico.
- Un successo parziale con errore critico va interpretato come supporto utile
  ma bisognoso di supervisione, non come diagnosi definitiva.

## Grafici consigliati

Le tabelle permettono di generare, senza ulteriori valutazioni API:

1. distribuzione degli esiti CHAT, AGENT e complessivi;
2. punteggio CHAT e AGENT per ciascun circuito;
3. media dei cinque criteri per modalità;
4. heatmap dei cinque criteri sulle 42 run;
5. frequenza degli errori critici;
6. relazione tra autonomia operativa e qualità finale.
