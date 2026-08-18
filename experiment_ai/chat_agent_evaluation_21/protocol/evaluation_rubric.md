# Protocollo di valutazione CHAT e AGENT

## Obiettivo

La valutazione risponde prima alla domanda principale della tesi:

> Il sistema diagnostico, considerato nel suo complesso, produce risultati
> tecnicamente corretti e utili sui circuiti analizzati?

Solo in un secondo momento confronta le due modalita' disponibili:

- **CHAT**, guidata dall'utente;
- **AGENT**, autonoma.

Le due esecuzioni dello stesso circuito vengono giudicate separatamente con gli
stessi criteri. I risultati vengono poi riuniti in una tabella appaiata, con una
riga per circuito e colonne CHAT e AGENT.

## Unita' di valutazione

Il corpus contiene 21 circuiti e 42 esecuzioni congelate. Ogni esecuzione e'
una distinta unita' di valutazione.

Il judge riceve:

1. la richiesta iniziale dell'utente;
2. una ground truth tecnica priva delle note che anticipano il risultato;
3. gli scenari proposti ed eseguiti;
4. le azioni applicate e le misure SPICE;
5. la conclusione finale.

I campi strutturati con le etichette interne della pipeline, come
`resolved_candidate`, non vengono forniti al judge e non costituiscono ground
truth. Se una conclusione finale cita una di queste etichette, il judge la
tratta come una normale affermazione del sistema da verificare sui dati.

## 1. Stato tecnico oggettivo

Lo stato tecnico viene calcolato dagli artefatti e non dal judge:

- `completed`: risposta finale presente e nessuna run SPICE eseguita fallita;
- `completed_with_errors`: risposta finale presente, ma almeno una run SPICE
  eseguita e' fallita;
- `technical_failure`: manca una traiettoria finale valutabile.

Una run SPICE fallita non rende automaticamente errata la diagnosi, ma non puo'
essere usata come prova dell'ipotesi testata.

## 2. Valutazione semantica

Il judge assegna a ciascun criterio un punteggio intero `0`, `1` o `2`.

### Correttezza diagnostica

- `0`: causa, comportamento o localizzazione sostanzialmente errati;
- `1`: diagnosi utile ma incompleta, incerta o con errori rilevanti;
- `2`: diagnosi corretta e coerente con la ground truth.

### Qualita' delle prove

- `0`: scenari inadeguati al sintomo o tecnicamente non validi;
- `1`: almeno una prova utile, ma percorso incompleto o con tentativi deboli;
- `2`: prove pertinenti che distinguono efficacemente le ipotesi importanti.

### Interpretazione delle evidenze

- `0`: risultati SPICE ignorati o interpretati in modo contrario ai dati;
- `1`: interpretazione prevalentemente utile ma incompleta o troppo forte;
- `2`: misure interpretate correttamente, includendo limiti e incertezze.

### Raggiungimento dell'obiettivo

- `0`: richiesta dell'utente non soddisfatta;
- `1`: risultato utile ma obiettivo raggiunto solo in parte;
- `2`: tutti gli obiettivi espliciti sono raggiunti e verificati.

Una correzione e' obbligatoria soltanto quando la richiesta la richiede. Nei
casi esplicativi o di caratterizzazione puo' essere corretto concludere che il
circuito funziona gia' o che il sintomo non e' riprodotto.

### Qualita' della conclusione

- `0`: risposta assente, errata o fuorviante;
- `1`: risposta utile ma con omissioni o certezza non ben calibrata;
- `2`: risposta chiara, corretta e proporzionata alle evidenze.

Il totale descrittivo varia da 0 a 10, ma non determina da solo l'esito.

### Principi di calibrazione

I punteggi valutano la sufficienza delle evidenze rispetto alla richiesta, non
la lunghezza o l'esaustivita' della traiettoria:

- gli scenari non eseguiti non abbassano da soli la qualita' delle prove;
- una o due prove decisive possono ottenere `2` se distinguono le ipotesi
  importanti;
- la stessa omissione incide su piu' criteri soltanto quando compromette
  ciascuno di essi in modo autonomo;
- le `success_conditions` guidano il confronto tecnico, ma non sono una
  checklist di elementi tutti equivalenti: la loro importanza dipende dalla
  domanda esplicita dell'utente e dalle evidenze decisive;
- omissioni secondarie non annullano una diagnosi o una correzione altrimenti
  corretta, mentre errori che cambiano causalita', interpretazione o risultato
  restano pienamente penalizzati.
- la conclusione finale non azzera automaticamente le parti corrette della
  traiettoria: ipotesi, prove e localizzazioni intermedie materialmente utili
  ricevono credito nei rispettivi criteri;
- una traiettoria con evidenze miste puo' ricevere `1` nei criteri interessati:
  `0` e' riservato ai casi privi di un contributo corretto concretamente utile
  per quel criterio.

## 3. Esito della singola esecuzione

- `success`: obiettivo raggiunto e dimostrato con evidenze sufficienti;
- `partial_success`: almeno un risultato diagnostico corretto, materialmente
  utile e sostenuto dalle evidenze, ma obiettivo incompleto o conclusione con
  limiti ed errori rilevanti;
- `failure`: obiettivo non raggiunto e nessun contributo corretto concretamente
  utilizzabile, oppure falsa correzione contraria alle evidenze che costituisce
  l'esito sostanziale della traiettoria;
- `inconclusive`: gli artefatti non permettono una decisione affidabile;
- `technical_failure`: traiettoria non valutabile tecnicamente.

Un errore critico puo' impedire l'esito `success` anche con un totale numerico
alto. Non impone automaticamente `failure`: puo' coesistere con
`partial_success` quando la traiettoria conserva un contributo diagnostico
corretto e materialmente utile.

Fa eccezione un `false_success` centrale: quando la conclusione presenta come
verificata una correzione contraria alle evidenze o all'obiettivo, l'esito e'
`failure`. Osservazioni incidentali corrette, la semplice esecuzione di uno
scenario o un cambiamento elettrico non bastano a trasformarlo in
`partial_success`. Quest'ultimo resta possibile soltanto se la traiettoria
contiene anche un risultato corretto indipendente che soddisfa concretamente
una parte primaria della richiesta.

## 4. Errori critici

Il judge puo' segnalare:

- `false_success`: viene dichiarata una risoluzione non dimostrata;
- `unsupported_claim`: viene affermata una causa o un effetto non sostenuto;
- `wrong_interpretation`: una misura SPICE viene interpretata in modo
  incompatibile con i dati.

Gli errori critici sono riservati ad affermazioni che cambiano materialmente
la diagnosi o l'esito. Dettagli periferici non verificabili nel pacchetto non
sono da soli errori critici.

## 5. Risultati complessivi del sistema

La valutazione principale riporta:

- tasso di completamento tecnico;
- tasso di successo stretto (`success`);
- tasso di risultato utile (`success` + `partial_success`);
- distribuzione dei cinque criteri;
- frequenza degli errori critici.

A livello dei 21 circuiti vengono inoltre contati:

- successo di entrambe le modalita';
- successo di una sola modalita';
- nessun successo.

Questi indicatori descrivono il sistema complessivo, non una competizione fra
le modalita'.

## 6. Confronto secondario CHAT-AGENT

La tabella appaiata usa una riga per circuito e affianca:

- esito CHAT ed esito AGENT;
- cinque punteggi CHAT e cinque punteggi AGENT;
- scenari e run SPICE;
- interventi dell'utente in CHAT;
- decisioni autonome in AGENT;
- errori critici.

Il confronto sintetico conta i casi `CHAT migliore`, `equivalenti` e `AGENT
migliore`. Il circuito `b03` viene segnalato perche' le due domande sono
equivalenti nell'obiettivo ma non testualmente identiche.

## 7. Limite sperimentale

E' disponibile una sola esecuzione per modalita' e circuito. I risultati
descrivono quindi le 42 traiettorie congelate e non stimano la variabilita' di
nuove generazioni del modello linguistico.
