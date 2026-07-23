# Valutazione CHAT e AGENT

Questa cartella raccoglie il nuovo esperimento per confrontare le modalità **CHAT** e **AGENT** della Pipeline 2.0.

## Obiettivo

Verificare se, partendo dal sintomo indicato dall'utente, il sistema:

- individua una causa plausibile e corretta;
- localizza il problema nel componente, nodo o ramo giusto;
- sceglie scenari diagnostici utili;
- interpreta correttamente i risultati SPICE;
- formula una conclusione coerente con le prove disponibili.

## Circuiti e modello

Saranno valutati 14 circuiti:

- batchA: `a01`, `a02`, `a04`, `a05`, `a06`, `a07`, `a08`, `a09`, `a10`;
- batchB: `b02`, `b03`, `b04`, `b05`, `b10`.

Per ogni circuito verrà eseguita una volta la modalità CHAT e una volta la modalità AGENT, per un totale di **28 esecuzioni**.

Il modello utilizzato dall'agente sarà **GPT-5.4**.

Non verranno introdotti guasti artificiali: ogni esecuzione partirà dal circuito e dal sintomo già definiti per il caso.

## File minimi per ogni circuito

```text
evaluation/
└── a01/
    ├── gold.yaml
    ├── chat_summary.json
    ├── chat_judge.json
    ├── agent_summary.json
    └── agent_judge.json
```

### `gold.yaml`

Scheda di riferimento comune alle due modalità. Contiene:

- sintomo;
- cause considerate accettabili;
- localizzazione attesa;
- test diagnostici utili;
- risultato che permetterebbe di considerare il problema localizzato o risolto;
- eventuali ambiguità del caso.

### `chat_summary.json` e `agent_summary.json`

Riepilogo automatico dell'esecuzione:

- diagnosi iniziale;
- scenari eseguiti;
- ipotesi verificata da ogni scenario;
- azione effettuata;
- risultato della simulazione;
- interpretazione dell'agente;
- diagnosi finale;
- stato finale;
- eventuale correzione verificata;
- numero di scenari ed esecuzioni SPICE riuscite o fallite.

I due riepiloghi vengono creati insieme con:

```powershell
.venv312\Scripts\python.exe experiment_ai\chat_agent_evaluation\build_case_summaries.py `
  --workspace chat_agent_evaluation `
  --circuit a01
```

Lo script riceve il workspace e il circuito, trova automaticamente le cartelle
CHAT e AGENT e salva i risultati in:

```text
experiment_ai/chat_agent_evaluation/evaluation/<circuito>/
```

Non contiene sintomi, nodi, componenti o scenari specifici. Tutte le
informazioni vengono lette dagli artefatti della run. Se viene rieseguito,
aggiorna i due riepiloghi senza modificare gli output originali della pipeline.

### `chat_judge.json` e `agent_judge.json`

Contengono i punteggi assegnati dal judge e una breve motivazione.

## Criteri del judge

Ogni criterio riceve un punteggio da 0 a 4.

| Criterio | Peso | Cosa viene confrontato |
|---|---:|---|
| Correttezza della diagnosi | 30% | Causa finale e cause accettabili nella scheda gold |
| Correttezza della localizzazione | 20% | Componenti, nodi o ramo indicati e localizzazione attesa |
| Qualità degli scenari | 20% | Utilità e capacità diagnostica degli scenari eseguiti |
| Interpretazione delle evidenze | 20% | Interpretazione dell'agente e risultati reali delle simulazioni |
| Correttezza della conclusione | 10% | Stato finale e livello di certezza consentito dalle prove |

Scala utilizzata:

- `0`: errato o assente;
- `1`: prevalentemente errato;
- `2`: parzialmente corretto;
- `3`: corretto con piccole carenze;
- `4`: completamente corretto e verificato.

Il punteggio pesato finale viene riportato su 100.

## Errori critici

Il judge segnala separatamente:

- `false_resolution`: il sistema dichiara il problema risolto senza una correzione verificata;
- `unsupported_claims`: la conclusione utilizza valori, componenti o collegamenti non presenti nelle evidenze;
- `wrong_interpretation`: il risultato di uno scenario viene interpretato in modo contrario ai dati.

## Fine dell'esecuzione

In modalità CHAT, dopo gli scenari, verrà richiesto esplicitamente:

> Concludi esperimento.

La risposta finale non dovrà proporre altri scenari, ma riassumere:

- stato finale: `resolved`, `localized`, `partially_localized`, `topology_issue` oppure `inconclusive`;
- causa;
- localizzazione;
- evidenze principali;
- eventuali evidenze contrarie;
- presenza o assenza di una correzione verificata;
- conclusione finale per l'utente.

In modalità AGENT gli stessi campi verranno ricavati dallo stato finale dell'esecuzione autonoma.

## Flusso operativo

Per ciascun circuito:

1. preparare `gold.yaml`;
2. eseguire CHAT con il sintomo;
3. concludere CHAT e generare `chat_summary.json`;
4. far valutare il riepilogo al judge;
5. eseguire AGENT con lo stesso sintomo;
6. generare `agent_summary.json`;
7. far valutare il riepilogo al judge;
8. confrontare punteggi, esito e numero di scenari delle due modalità.

I file completi prodotti dalla pipeline rimangono nelle rispettive cartelle di output. Nei riepiloghi vengono riportate soltanto le informazioni necessarie al judge.
