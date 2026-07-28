# Valutazione CHAT e AGENT

Questa cartella raccoglie l'esperimento usato per confrontare le modalità
**CHAT** e **AGENT** della Pipeline 2.0.

## Obiettivo

L'esperimento verifica se il sistema, partendo da un sintomo o da un obiettivo
espresso dall'utente:

- raggiunge il risultato richiesto;
- formula una diagnosi e una localizzazione tecnicamente corrette;
- sceglie scenari utili;
- interpreta correttamente i risultati SPICE;
- produce una conclusione coerente con le evidenze.

Il confronto riguarda due modalità d'interazione:

- **CHAT**: workflow guidato, nel quale l'utente seleziona gli scenari e pone
  domande successive;
- **AGENT**: workflow autonomo, nel quale il sistema decide, esegue e conclude
  senza guida intermedia.

La valutazione considera l'intera traiettoria, non soltanto la risposta finale.

## Dataset definitivo

Sono inclusi 17 circuiti:

- batch A: `a01`, `a02`, `a04`, `a05`, `a06`, `a07`, `a08`, `a09`, `a10`;
- batch B: `b02`, `b03`, `b04`, `b05`, `b06`, `b10`;
- casi aggiuntivi: `c02`, `c03`.

Per ogni circuito è stata eseguita una volta la modalità CHAT e una volta la
modalità AGENT, per un totale di **34 esecuzioni**. Il modello usato dal
sistema diagnostico è **GPT-5.4**.

Non sono stati introdotti guasti artificiali. Ogni esecuzione parte dal
circuito validato e dal sintomo o obiettivo definito per il caso.

Le esecuzioni sono congelate: non devono essere sostituite dopo aver osservato
i risultati, salvo errori tecnici che abbiano impedito la creazione degli
artefatti.

### Note sul protocollo

In 16 casi CHAT e AGENT hanno ricevuto lo stesso testo. In `b03` le domande
sono formulate diversamente, ma richiedono entrambe di verificare i tre LED
durante il passaggio della batteria da scarica a carica. I risultati verranno
quindi aggregati sia con tutti i 17 circuiti sia escludendo `b03`.

Uno scenario AGENT di `a08` ha prodotto un errore SPICE. Il fallimento rimane
nel dataset e contribuisce alla valutazione dell'affidabilità.

## Struttura dei file

```text
evaluation/
└── a01/
    ├── chat_summary.json
    ├── agent_summary.json
    ├── chat_judge.json
    └── agent_judge.json
```

Non vengono utilizzate schede gold specifiche per circuito. Il judge valuta
la coerenza fra obiettivo, azioni, risultati SPICE e conclusione presenti
nella singola traiettoria.

## Summary delle esecuzioni

### `chat_summary.json` e `agent_summary.json`

I summary contengono:

- sintomo iniziale;
- evidenze della simulazione base;
- conversazione CHAT o decisioni AGENT;
- scenari proposti ed eseguiti;
- azioni applicate;
- esito di ngspice;
- confronto quantitativo fra base e scenario;
- interpretazione del sistema;
- conclusione e stato finali;
- simulazioni riuscite o fallite.

I due summary vengono creati insieme con:

```powershell
.venv312\Scripts\python.exe experiment_ai\chat_agent_evaluation\build_case_summaries.py `
  --workspace chat_agent_evaluation `
  --circuit a01
```

Lo script non contiene casi hardcoded e non assegna punteggi. Legge gli
artefatti della run e salva i riepiloghi in:

```text
experiment_ai/chat_agent_evaluation/evaluation/<circuito>/
```

## Pacchetto inviato al judge

Prima della valutazione, `run_judge.py` riduce ogni summary a un pacchetto
essenziale. Include:

- traccia completa dell'interazione o dell'esecuzione autonoma;
- contesto elettrico e simulazione base;
- soltanto gli scenari realmente eseguiti;
- azioni applicate e misure SPICE base/scenario;
- conclusione finale della singola esecuzione.

`interaction_trace` include tutti i messaggi dell'utente e le risposte
analitiche intermedie di CHAT; gli avvii degli scenari sono rappresentati come
eventi strutturati perché i risultati completi sono già in
`executed_scenarios`. Per AGENT include la richiesta iniziale, tutte le
decisioni autonome, gli scenari proposti e i relativi risultati. La conclusione
terminale compare una sola volta in `final`. Le eventuali affermazioni tecniche
dell'utente devono comunque essere verificate sulle misure SPICE. Per ogni
scenario include inoltre
misure base/scenario, aspettative, stato operativo delle quantità ed esito
calcolato dalla pipeline. Le ulteriori prove strutturate prodotte dal confronto
(per esempio proprietà temporali, guadagno o qualità) vengono incluse
dinamicamente in `comparison_evidence`; eventuali sequenze molto lunghe sono
compattate senza eliminare le metriche riassuntive. Per gli scenari transitori
vengono inclusi anche i profili di tutti i LED presenti nel viewer, non soltanto
quello indicato dall'eventuale aspettativa temporale. Include inoltre l'intero
blocco finale del summary, con le eventuali evidenze strutturate che sostengono
la conclusione. La regola è identica per CHAT e AGENT e non dipende dal
circuito o dai componenti. Il judge deve controllarne la coerenza senza
trattare le sole etichette automatiche come ground truth indipendente.

Prima dell'invio vengono rimossi anche eventuali campi `mode` e neutralizzati
i segmenti `web/chat` o `web/agent` citati nei percorsi testuali, senza
alterare misure, netlist o contenuto tecnico.

Il lungo output testuale di ngspice non viene inviato integralmente: lo script
estrae le tensioni nodali e le correnti delle sorgenti in
`base_operating_point`. Il netlist, gli errori, le misure degli scenari e le
altre prove strutturate restano disponibili. Questa riduzione evita dump
ridondanti dei modelli SPICE.

Per controllare il pacchetto senza chiamare alcun modello:

```powershell
.venv312\Scripts\python.exe experiment_ai\chat_agent_evaluation\run_judge.py `
  --circuit c03 `
  --mode both
```

Il comando mostra dimensione, hash, stima approssimativa dei token in ingresso,
campi e scenari inclusi. Per stampare il JSON completo si può aggiungere
`--show-packet`. Nessun pacchetto intermedio viene salvato e nessuna API viene
chiamata.

Le istruzioni congelate del valutatore sono in `judge_prompt_v1.md`; il formato
ammesso della risposta è in `judge_response_schema_v1.json`.

Una singola valutazione reale si esegue soltanto con il flag esplicito `--run`:

```powershell
.venv312\Scripts\python.exe experiment_ai\chat_agent_evaluation\run_judge.py `
  --circuit c03 `
  --mode chat `
  --run `
  --judge-model gpt-5.5
```

Lo script valida il JSON, calcola il totale, registra modello, versione del
prompt e hash SHA-256 del summary, quindi salva `chat_judge.json`. Non
sovrascrive una valutazione esistente senza `--force`. La configurazione
congelata dell'esperimento usa `gpt-5.5` con reasoning effort `medium`.

Prima di qualsiasi chiamata API, il preflight controlla entrambi i pacchetti,
gli hash congelati di prompt e schema, la configurazione del modello e
l'eventuale presenza di file di output. Se uno dei controlli fallisce, nessuna
valutazione viene avviata. Questo evita anche il caso in cui `--mode both`
consumi token per la prima modalità prima di scoprire un conflitto sulla
seconda.

## Principio di valutazione

Il judge valuta separatamente ogni summary. CHAT e AGENT non vengono mostrati
insieme e la modalità viene nascosta durante la valutazione.

Il judge deve applicare questa regola:

> I risultati SPICE e i confronti numerici hanno precedenza sulle etichette
> automatiche e sulle affermazioni del sistema valutato.

Etichette interne come `resolved_candidate`, `partially_resolved`,
`best_scenario` o `stop_automation` non costituiscono ground truth.

La valutazione riguarda il comportamento nell'ambiente simulato e non contiene
regole specifiche per circuito o tipologia di componente. Il judge controlla
prima che azioni, confronti e aspettative rappresentino adeguatamente
l'obiettivo dell'utente; controlla poi che le misure ne dimostrino il
raggiungimento. Non deve introdurre soglie o prestazioni non richieste e non
modellate, ma deve pretendere una verifica esplicita quando tali requisiti fanno
parte dell'obiettivo.

Il completamento dipende dal tipo di richiesta: una diagnosi non richiede una
correzione se l'utente non l'ha chiesta; una verifica funzionale deve coprire
tutti i comportamenti richiesti; una configurazione deve raggiungere una
condizione misurata. Nelle richieste composte tutti i sotto-obiettivi espliciti
concorrono all'esito. Il numero di scenari non viene premiato o penalizzato da
solo: contano pertinenza, copertura e utilità delle prove.

## Tipo di compito ed esito

Il judge identifica il tipo di richiesta:

- `diagnosis`: individuare la causa di un problema;
- `functional_verification`: verificare il comportamento del circuito;
- `configuration_goal`: ottenere una condizione richiesta.

L'esito complessivo assume uno dei seguenti valori:

- `success`: obiettivo raggiunto e verificato;
- `partial_success`: risultato utile ma incompleto;
- `failure`: obiettivo non raggiunto o conclusione errata;
- `inconclusive`: evidenze insufficienti.

## Criteri del judge

Ogni criterio riceve un punteggio intero da 0 a 4 e ha peso **20%**.

| Criterio | Peso | Significato |
|---|---:|---|
| Raggiungimento dell'obiettivo | 20% | Quanto è stato soddisfatto il bisogno dell'utente |
| Correttezza tecnica | 20% | Correttezza di diagnosi, localizzazione e ragionamento elettrico |
| Qualità degli scenari | 20% | Utilità e validità delle azioni eseguite |
| Interpretazione delle evidenze | 20% | Coerenza fra risultati SPICE e interpretazione |
| Qualità della conclusione | 20% | Chiarezza e livello di certezza appropriato |

Scala:

- `0`: errato o assente;
- `1`: prevalentemente errato;
- `2`: parzialmente corretto;
- `3`: corretto con carenze minori;
- `4`: completamente corretto e verificato.

Il judge assegna soltanto i cinque punteggi. Lo script calcola il totale:

```text
punteggio su 100 = somma dei cinque punteggi × 5
```

Il totale viene sempre accompagnato dai cinque punteggi separati.

## Errori critici

Il judge segnala:

- `false_success`: successo dichiarato senza evidenze sufficienti;
- `unsupported_claims`: cause, valori o collegamenti non supportati;
- `wrong_interpretation`: risultati interpretati in modo contrario ai dati.

Ogni errore contiene un valore booleano e una breve motivazione.

## Formato del risultato judge

Ogni valutazione viene salvata in `chat_judge.json` o `agent_judge.json`.

```json
{
  "schema_version": 1,
  "metadata": {
    "circuit_id": "c03",
    "mode": "agent",
    "judge_model": "MODELLO_JUDGE",
    "reasoning_effort": "medium",
    "prompt_version": "v1",
    "packet_schema_version": 3,
    "prompt_sha256": "...",
    "response_schema_sha256": "...",
    "packet_sha256": "...",
    "summary_sha256": "..."
  },
  "task": {
    "type": "diagnosis",
    "outcome": "partial_success",
    "outcome_reason": "..."
  },
  "criteria": {
    "task_achievement": {
      "score": 3,
      "reason": "..."
    },
    "technical_correctness": {
      "score": 3,
      "reason": "..."
    },
    "scenario_quality": {
      "score": 2,
      "reason": "..."
    },
    "evidence_interpretation": {
      "score": 2,
      "reason": "..."
    },
    "conclusion_quality": {
      "score": 3,
      "reason": "..."
    }
  },
  "critical_errors": {
    "false_success": {
      "present": false,
      "reason": ""
    },
    "unsupported_claims": {
      "present": false,
      "reason": ""
    },
    "wrong_interpretation": {
      "present": true,
      "reason": "..."
    }
  },
  "evidence": [
    "..."
  ],
  "final_assessment": "...",
  "computed_score": {
    "weighted_total": 65,
    "maximum": 100
  }
}
```

Il judge produce tipo di compito, esito, criteri, errori, evidenze e giudizio
finale. Lo script aggiunge i metadati, calcola il punteggio e registra l'hash
del summary valutato.

## Metriche operative oggettive

Le seguenti metriche vengono lette direttamente dai summary e non sono
decise dal judge:

- scenari proposti ed eseguiti;
- simulazioni SPICE riuscite e fallite;
- azioni applicate o fallite;
- numero di turni CHAT;
- numero di decisioni AGENT;
- presenza di una correzione verificata dal workflow;
- tempo e costo, se disponibili.

Queste metriche vengono riportate separatamente dal punteggio semantico.

## Controllo del judge

Una valutazione viene ripetuta soltanto in caso di errore tecnico, chiamata
fallita o JSON non valido.

Per controllare l'affidabilità del judge:

- si revisionano manualmente i casi con errori critici;
- si controllano alcuni casi rappresentativi semplici e complessi;
- si ripete la valutazione su un sottoinsieme fissato, senza scegliere il
  risultato più favorevole.

Le eventuali divergenze vengono documentate come limite e non corrette
selettivamente.

## Processo operativo

1. congelare le 34 esecuzioni;
2. generare e validare i due summary di ogni circuito;
3. costruire un input anonimo per il judge;
4. valutare separatamente ogni summary;
5. validare il JSON restituito;
6. calcolare il punteggio su 100;
7. estrarre le metriche operative;
8. aggregare i risultati appaiati CHAT-AGENT;
9. ripetere l'aggregazione escludendo `b03`;
10. revisionare i casi critici e il sottoinsieme di stabilità.

## Risultati aggregati

Il confronto finale deve riportare:

- media e mediana dei punteggi;
- differenza appaiata AGENT meno CHAT per circuito;
- vittorie, pareggi e sconfitte;
- punteggi medi per criterio;
- frequenze di `success`, `partial_success`, `failure` e `inconclusive`;
- errori critici;
- scenari medi eseguiti;
- simulazioni SPICE riuscite e fallite;
- quantità di interazione richiesta nelle due modalità.

Grafici consigliati:

1. punteggi CHAT e AGENT appaiati per circuito;
2. punteggi medi dei cinque criteri;
3. distribuzione degli esiti e degli errori critici.

I file completi della pipeline restano nel workspace. I summary contengono le
informazioni necessarie per valutare l'intera traiettoria diagnostica.
