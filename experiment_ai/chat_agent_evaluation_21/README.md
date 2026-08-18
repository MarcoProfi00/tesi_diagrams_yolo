# Valutazione unificata CHAT e AGENT

Questa cartella contiene il corpus unificato da utilizzare per la nuova
valutazione delle modalità **CHAT** e **AGENT**.

L'obiettivo è valutare il passaggio dalla ricostruzione automatica dello
schema alla diagnosi assistita: l'immagine viene trasformata in un circuito
simulabile, l'utente descrive un sintomo e il sistema usa gli scenari SPICE per
proporre o verificare una soluzione. L'applicazione offre due modalità:

- **CHAT**, nella quale l'utente sceglie e avvia le prove suggerite;
- **AGENT**, nella quale il sistema seleziona ed esegue autonomamente le prove.

La valutazione deve mostrare sia se il sistema complessivo riesce a produrre
una diagnosi utile, sia quali differenze emergono tra l'interazione guidata e
quella autonoma.

## Corpus

Il corpus comprende **21 circuiti di varia difficoltà**:

`a01`, `a02`, `a04`, `a05`, `a06`, `a07`, `a08`, `a09`, `a10`, `b02`,
`b03`, `b04`, `b05`, `b06`, `b10`, `c02`, `c03`, `ic01`, `ic02`, `ic03`,
`ic04`.

Per ogni circuito sono presenti due traiettorie:

- `chat_summary.json`: esecuzione guidata in modalità CHAT;
- `agent_summary.json`: esecuzione autonoma in modalità AGENT.

Il corpus contiene quindi **42 summary** complessivi.

## Fonti canoniche

Durante la compilazione delle schede di riferimento, le immagini devono
essere lette esclusivamente dalle cartelle congelate usate dagli esperimenti:

- circuiti `a*`, `b*` e `c*`:
  `data/batchPipeline2.0/batchChatAgentEvaluation/`;
- circuiti `ic*`:
  `data/batchPipeline2.0/batchICChatAgentEvaluation/`.

Le copie presenti in cartelle di verifiche precedenti non costituiscono la
fonte della ground truth, anche quando hanno lo stesso nome del circuito.

## Come sono stati simulati i circuiti integrati

I casi `ic01`–`ic04` non usano un integrato ideale o una logica speciale
scritta nel codice della pipeline. Per ciascuno è stato usato un macromodello
PSpice del produttore, conservato nel repository nella forma originale e
richiamato dalla Pipeline 2.0.

| Circuito | Integrato nello schema | Modello usato | File del modello TI |
|---|---|---|---|
| `ic01` | timer 555 | `TLC555_6` | `metadata/spice_models/ti/tlc555/slfj002e/TLC555_6.LIB` |
| `ic02` | amplificatore LM1875 | `LM1875_0` | `metadata/spice_models/ti/lm1875/snam066a/LM1875.lib` |
| `ic03` | regolatore LM317T | `LM317_TRANS` | `metadata/spice_models/ti/lm317/slvmc40/LM317_TRANS.LIB` |
| `ic04` | due timer NE555 | `TLC555_6` per entrambi | `metadata/spice_models/ti/tlc555/slfj002e/TLC555_6.LIB` |

Il modello del 555 è il TLC555 CMOS ufficiale TI: è compatibile per funzione e
pinout con il 555/NE555 rappresentato negli schemi, ma questa differenza di
famiglia resta un limite dichiarato dell'esperimento. LM1875 e LM317 usano i
rispettivi modelli ufficiali TI. Informazioni su versione, provenienza, hash e
compatibilità di ciascun file sono riportate nei corrispondenti `README.md`
sotto `metadata/spice_models/ti/`.

Il flusso è sempre lo stesso:

1. La Pipeline 1.0 ricostruisce componenti, terminali e collegamenti
   dall'immagine, producendo il Graph JSON.
2. Il file
   `data/batchPipeline2.0/batchICChatAgentEvaluation/values/icNN_values.yaml`
   dichiara il modello dell'integrato, l'ordine dei suoi pin e a quale
   terminale del Graph corrisponde ciascun pin. Questa è una configurazione
   dichiarativa per circuito, non un hardcoding nel programma.
3. Lo step SPICE della Pipeline 2.0 legge il modello richiesto nel registro
   `metadata/pipeline2_spice_models.yaml`, verifica l'hash del file originale
   e ne crea una copia locale della run, `07_external_models.lib`.
4. Lo stesso step genera `07_netlist.cir`: inserisce i passivi, le sorgenti e
   l'istanza `X...` del subcircuito con i nodi ottenuti dal Graph.
5. ngspice esegue quel netlist in modalità compatibile PSpice
   (`ngbehavior=ps`) e salva log, CSV transitorio e grafici.

Per esempio, nel netlist di `ic02` il modello LM1875 è istanziato così:

```spice
Xintegrated_circuit11_1 N006 N005 N001 N003 N007 LM1875_0
.include "07_external_models.lib"
```

L'ordine `N006 N005 N001 N003 N007` non è scelto dalla pipeline: deriva dal
pin order dichiarato da TI (`Vin Vip VSS VDD Vout`) e dal mapping presente in
`ic02_values.yaml`. Lo stesso meccanismo vale per tutti gli IC. Nel caso
`ic03`, il modello TI espone `IN ADJ OUT_0 OUT_1`; le ultime due porte sono
collegate allo stesso nodo OUT fisico, come documentato nel file dei valori.

Gli artefatti della simulazione base si trovano in
`outputs/demo_workspaces/ic_chat_agent_evaluation/pipeline2.0/<circuito>/`:

- `07_netlist.cir`: circuito effettivamente passato a ngspice;
- `07_external_models.lib`: bundle locale del modello verificato;
- `08_spice_run.json`: comando, esito e percorsi prodotti;
- `08_tran_raw.csv` e `08_tran.csv`: risultati transitori;
- `08_tran_plot.png`: grafico del transitorio.

Le run di CHAT e AGENT partono dalla stessa base. Uno scenario modifica solo
i valori o gli stati dichiarati dalla prova, ricrea il proprio netlist e
riesegue ngspice con lo stesso modello incluso localmente. In questo modo la
diagnosi confronta una base e uno scenario con topologia, modello e condizioni
di simulazione tracciabili.

### Cosa significa “integrazione verificata”

Per questi circuiti non abbiamo considerato sufficiente che ngspice accettasse
la sintassi del netlist. L'integrazione di un IC è stata considerata verificata
solo quando erano soddisfatti tutti questi punti:

1. il pin mapping dichiarato nel `values.yaml` coincide con simbolo, Graph e
   datasheet/modello del componente;
2. il netlist generato contiene l'istanza `X...` nell'ordine pin corretto e il
   bundle `07_external_models.lib` del modello richiesto;
3. la run base termina con `status: success` e produce il transitorio;
4. il comportamento elettrico ottenuto è coerente con la funzione del circuito;
5. le variazioni dei componenti esterni negli scenari modificano il
   comportamento previsto, senza dover cambiare o scrivere codice specifico
   per quel singolo integrato.

I quattro casi soddisfano questi criteri:

| Circuito | Evidenza di funzionamento nel circuito completo |
|---|---|
| `ic01` | Il TLC555 forma un astabile; l'uscita commuta e pilota il LED. Le modifiche al condensatore CONTROL cambiano il transitorio di avvio. |
| `ic02` | Il LM1875 riceve le rail +/-25 V e amplifica il segnale audio; il guadagno base è coerente con la controreazione R1-R2 e varia come previsto cambiando R2. |
| `ic03` | Il LM317, insieme alla rete RC esterna, genera un'uscita che varia circa fra 0.04 e 11.5 V; cambiare R1 rallenta regolarmente il lampeggio. |
| `ic04` | Le due istanze TLC555 producono modulazione lenta e tono audio; cambiare R5 tra i due stadi aumenta la separazione delle frequenze generate dal secondo timer. |

Le quattro simulazioni base sono tutte concluse correttamente. Inoltre sono
state completate con successo 17 run di scenario su questi stessi circuiti:
6 in CHAT e 11 in AGENT. Questo dimostra che i modelli sono collegati alla
nostra topologia e rispondono ai passivi esterni; non sono semplicemente file
inclusi senza effetto sul circuito.

La verifica ha comunque un perimetro preciso. Essa dimostra il comportamento
funzionale dei quattro schemi estratti, con i valori e le condizioni di prova
documentate. Non certifica automaticamente ogni variante fisica: il TLC555
non è una replica perfetta di ogni NE555 bipolare, i modelli PSpice vengono
eseguiti in compatibilità ngspice e lampada/speaker sono carichi resistivi
equivalenti. Questi limiti non invalidano l'integrazione, ma delimitano le
conclusioni presentabili nella tesi.

## Struttura

```text
chat_agent_evaluation_21/
├── dataset/                 # catalogo e metriche descrittive
├── evaluation/
│   └── <circuit_id>/
│       ├── chat_summary.json
│       └── agent_summary.json
├── judge_inputs/            # 42 pacchetti puliti e anonimi
├── judge_results/           # risultati separati del nuovo judge
├── references/              # ground truth tecnica dei 21 circuiti
├── protocol/                # criteri comuni di valutazione
├── validation/              # verifiche SPICE indipendenti aggiuntive
├── build_case_summaries.py  # genera i summary dai workspace originali
├── build_dataset.py         # genera cataloghi e metriche descrittive
├── build_judge_packets.py   # prepara gli input del judge
└── run_judge.py             # valuta una o entrambe le modalità
```

## Contenuto dei summary

Ogni summary raccoglie in forma strutturata:

- domanda iniziale;
- modello utilizzato;
- evidenze del circuito e della simulazione base;
- conversazione CHAT o decisioni autonome AGENT;
- scenari proposti ed eseguiti;
- modifiche applicate;
- risultati delle simulazioni SPICE;
- confronti tra base run e scenari;
- conclusione finale;
- riferimenti agli artefatti sorgente.

I summary non sono ground truth: descrivono ciò che CHAT o AGENT hanno fatto e
costituiscono l'oggetto da giudicare.

## Ground truth tecniche

Per ogni circuito è presente una scheda YAML in `references/`. Le **ground
truth** servono come riferimento comune e indipendente per stabilire se una
traiettoria è tecnicamente corretta.


In questo esperimento una ground truth non è una risposta modello preparata a
priori, né coincide con la conclusione prodotta da CHAT o AGENT. È una
**scheda tecnica di riferimento**: descrive ciò che si può sostenere sul
circuito e sul suo comportamento simulato, e delimita ciò che invece non può
essere affermato dai dati disponibili. Serve quindi a valutare il ragionamento
dell'agente, non a verificare una semplice corrispondenza testuale.

### Come sono state costruite

Ogni scheda è stata compilata circuito per circuito a partire dagli artefatti
congelati dell'esperimento. Il controllo ha seguito questa sequenza:

| Fase | Controllo svolto | Scopo |
|---|---|---|
| 1. Schema | Lettura dell'immagine canonica: componenti, valori, polarità, alimentazioni e funzione del circuito. | Stabilire il comportamento atteso e distinguere i dati leggibili dalle assunzioni di testbench. |
| 2. Ricostruzione | Confronto tra immagine, Graph JSON e node map. | Verificare che collegamenti, masse, terminali e pin degli IC descrivano davvero lo schema. |
| 3. Simulazione | Lettura di `values.yaml`, netlist emesso, modelli inclusi e log ngspice. | Controllare che il circuito simulato corrisponda alla topologia validata e che la run sia utilizzabile. |
| 4. Evidenza quantitativa | Analisi dei CSV transitori e, quando necessario, ricalcolo indipendente di periodo, frequenza, guadagno, potenza, clipping o distorsione. | Stabilire che cosa dimostrano effettivamente i numeri SPICE. |
| 5. Traiettorie | Confronto fra base run, scenari CHAT e scenari AGENT. | Verificare se ogni modifica prova la causa proposta e se risolve davvero il sintomo. |
| 6. Limiti | Identificazione di assunzioni, modelli semplificati, misure inappropriate e conclusioni troppo forti. | Evitare che il judge premi un risultato plausibile ma non dimostrato. |

Per i circuiti integrati, questa procedura include anche la verifica del
modello del produttore, del suo ordine di pin, del mapping dichiarato nel
`values.yaml` e dell'istanza `X...` generata nel netlist. La sezione
precedente, [Come sono stati simulati i circuiti integrati](#come-sono-stati-simulati-i-circuiti-integrati), documenta questo passaggio nel dettaglio.

### Cosa contiene una scheda

Ogni ground truth riassume:

- la descrizione funzionale del circuito e il sintomo proposto all'agente;
- le assunzioni esplicite del testbench e il perimetro del modello SPICE;
- le evidenze tecniche che una risposta deve rispettare;
- le condizioni che rendono una diagnosi o una correzione riuscita;
- una o più soluzioni accettabili, quando le evidenze supportano alternative;
- le affermazioni non supportate, gli errori di interpretazione e i limiti da
  dichiarare;
- note qualitative sul percorso seguito da CHAT e AGENT.

Questa struttura consente di riconoscere, per esempio, che una modifica può
aumentare un segnale senza risolvere il sintomo, oppure che una conclusione può
essere utile ma troppo certa rispetto ai dati. Permette anche di accettare
soluzioni diverse quando conducono a un risultato tecnicamente verificato.

### A cosa servono nella valutazione

Il judge riceve un pacchetto derivato dal `summary` della singola esecuzione e
dalla ground truth del suo circuito. Il pacchetto conserva scenari, azioni,
misure SPICE e conclusione. Per CHAT conserva anche i messaggi dell'utente
successivi alla richiesta iniziale, perché possono contenere istruzioni,
osservazioni o misure che fanno parte della traiettoria guidata. Esclude invece
le note di revisione che anticipano il verdetto e i campi strutturati con le
etichette automatiche della pipeline.

I messaggi successivi dell'utente non diventano ground truth: il judge deve
confrontarne le affermazioni con gli scenari realmente eseguiti, le misure
SPICE e il riferimento tecnico. Servono a evitare che una misura fornita
durante la conversazione o una richiesta esplicita di conclusione venga
erroneamente classificata come informazione inventata dal sistema.

Questo è importante per tre ragioni:

1. CHAT e AGENT possono scegliere scenari diversi, ma vengono giudicate con gli
   stessi criteri di correttezza.
2. Le etichette interne della pipeline, come `resolved_candidate`, descrivono
   il risultato rispetto alle soglie scelte nella singola sessione; non sono da
   sole una prova che il problema sia stato risolto.
3. Un modello linguistico può produrre percorsi leggermente diversi in una
   nuova esecuzione. Le ground truth mantengono stabile il criterio con cui le
   traiettorie effettivamente raccolte vengono interpretate e confrontate.

In sintesi, le ground truth rendono la valutazione riproducibile e leggibile:
collegano ogni punteggio a evidenze circuitali e SPICE concrete, invece di
basarlo sull'impressione generale che una risposta sembri convincente.

## Processo di valutazione

La valutazione sarà applicata separatamente alle **42 traiettorie**, usando lo
stesso protocollo per CHAT e AGENT:

1. Lo script calcola lo stato tecnico direttamente dagli artefatti.
2. Il judge riceve il pacchetto pulito della singola traiettoria.
3. Controlla se le simulazioni sono state eseguite correttamente e se gli
   scenari provano davvero il sintomo descritto dall'utente.
4. Confronta interpretazione, soluzione e conclusione con le evidenze e con i
   limiti riportati nella ground truth.
5. Assegna cinque punteggi da 0 a 2: correttezza diagnostica, qualità delle
   prove, interpretazione delle evidenze, raggiungimento dell'obiettivo e
   qualità della conclusione.
6. Produce un esito sintetico (`success`, `partial_success`, `failure`,
   `inconclusive` o `technical_failure`) e registra separatamente eventuali
   errori critici.

Il numero di decisioni, scenari, run SPICE e interventi dell'utente verrà
analizzato separatamente come misura di **autonomia e costo di interazione**.
Non deve rendere automaticamente migliore una risposta tecnicamente errata.

Infine i risultati saranno aggregati per mostrare:

- successo complessivo del sistema sulle 42 esecuzioni;
- confronto diretto CHAT–AGENT sugli stessi 21 circuiti;
- qualità media delle diagnosi e frequenza degli errori principali;
- differenze in autonomia, numero di prove ed efficienza del percorso.

I 42 giudizi rimangono separati. In seguito vengono riuniti in una tabella con
una riga per circuito e colonne CHAT/AGENT affiancate. Questo permette di
rispondere in modo semplice a due domande: il sistema riesce generalmente a
diagnosticare i circuiti? Quando conviene usare la modalità guidata e quando
quella autonoma?

### Calibrazione preliminare del judge

Prima della valutazione completa, il protocollo viene controllato manualmente
su un gruppo pilota di circuiti diversi per struttura e difficoltà. Questa
fase serve a verificare che il judge distingua davvero una prova sufficiente da
una prova incompleta e che non applichi la ground truth come una checklist
meccanica.

La calibrazione ha chiarito tre principi: gli scenari non eseguiti non sono una
penalità automatica, una stessa omissione non deve essere conteggiata
indistintamente in tutti i criteri e una o due prove decisive possono essere
sufficienti. Scala, criteri, esiti ed errori critici non vengono addolciti: le
diagnosi incompatibili con le misure SPICE restano penalizzate integralmente.

Dopo il controllo del gruppo pilota, prompt e rubric vengono congelati. Tutte
le 42 traiettorie devono quindi essere giudicate con lo stesso hash del prompt;
risultati prodotti durante la calibrazione con hash precedenti non vengono
mescolati alla valutazione finale.

## Preparazione ed esecuzione del judge

I 42 pacchetti si rigenerano con:

```powershell
.venv312\Scripts\python.exe -B experiment_ai\chat_agent_evaluation_21\build_judge_packets.py --all
```

Prima di usare l'API si può controllare una coppia senza consumare token:

```powershell
.venv312\Scripts\python.exe -B experiment_ai\chat_agent_evaluation_21\run_judge.py `
  --circuit a01 `
  --mode both
```

Per eseguire davvero il judge sulle due modalità del circuito pilota:

```powershell
.venv312\Scripts\python.exe -B experiment_ai\chat_agent_evaluation_21\run_judge.py `
  --circuit a01 `
  --mode both `
  --run
```

Il modello predefinito è `gpt-5.5` con reasoning `medium`. CHAT e AGENT
producono due file distinti sotto `judge_results/<circuit_id>/`; l'unione
avviene soltanto nella successiva tabella dei risultati.

### Prova della calibrazione orientata alla traiettoria

Dopo il controllo manuale dei casi AGENT classificati come `failure`, il
prompt è stato calibrato per distinguere una traiettoria interamente errata da
una traiettoria che contiene prove o localizzazioni corrette ma termina con una
conclusione inaffidabile. La conclusione errata continua a impedire `success` e
gli errori critici restano visibili; le parti corrette della traiettoria possono
però sostenere `partial_success`.

La nuova calibrazione viene provata soltanto su AGENT e scritta in una cartella
separata, senza sovrascrivere i giudizi precedenti:

```powershell
.venv312\Scripts\python.exe -B experiment_ai\chat_agent_evaluation_21\run_judge.py `
  --circuit a08 `
  --mode agent `
  --results-dir judge_results_process_calibrated `
  --run
```

Solo dopo il controllo manuale dei risultati pilota si decide quale
calibrazione usare nella valutazione finale. Risultati ottenuti con hash del
prompt diversi non devono essere mescolati nello stesso aggregato.

## Stato attuale

I summary rappresentano le esecuzioni congelate da valutare. In questa
cartella non sono stati copiati i judge precedenti.

Sono disponibili 21 coppie CHAT/AGENT, 21 ground truth tecniche complete e 42
pacchetti del judge. I giudizi presenti sul gruppo pilota appartengono alla
fase di calibrazione e devono essere rigenerati con `--force` dopo il
congelamento del prompt definitivo. I risultati aggregati finali non sono
ancora stati prodotti.

## Prossimi passi

1. Provare il judge su un piccolo gruppo di circuiti diversi tra loro e
   controllare manualmente che applichi correttamente le ground truth.
2. Congelare configurazione e versione del judge, quindi valutare tutte le 42
   traiettorie.
3. Controllare gli esiti anomali o incerti senza modificare retroattivamente
   summary e ground truth.
4. Generare tabelle e grafici complessivi e il confronto appaiato tra CHAT e
   AGENT.
5. Usare i risultati per scrivere metodologia, risultati, discussione e limiti
   nella tesi.

## Dataset descrittivo

Se occorre ricostruire la coppia di summary di un circuito dal relativo
workspace originale, si usa:

```powershell
.venv312\Scripts\python.exe experiment_ai\chat_agent_evaluation_21\build_case_summaries.py `
  --workspace <workspace> `
  --circuit <circuit_id>
```

Lo script scrive per impostazione predefinita nella cartella unificata
`evaluation/<circuit_id>/`. Non deve essere eseguito sulle traiettorie già
raccolte se non si intende rigenerarle esplicitamente.

Il comando:

```powershell
.venv312\Scripts\python.exe experiment_ai\chat_agent_evaluation_21\build_dataset.py
```

genera:

- `dataset/circuits.csv`: catalogo dei 21 circuiti;
- `dataset/components.csv`: inventario delle classi di componente;
- `dataset/runs.csv`: metriche oggettive delle 42 esecuzioni;
- `references/<circuit_id>.yaml`: schede tecniche da compilare prima della
  valutazione semantica.

Le schede già presenti non vengono sovrascritte. L'opzione
`--force-reference-templates` deve essere usata soltanto se si vuole
rigenerarle intenzionalmente.

La generazione del dataset non esegue il judge e non modifica le ground truth
già congelate. Il protocollo definitivo è documentato in
`protocol/evaluation_rubric.md`.

## Tabelle finali

Le tabelle ufficiali e il documento che ne spiega campi, punteggi e limiti si
generano con:

```powershell
.venv312\Scripts\python.exe -B experiment_ai\chat_agent_evaluation_21\build_result_tables.py
```

Gli output sono raccolti in `results/`: il file `RESULTS_TABLES.md` contiene il
prospetto leggibile, mentre `results/tables/` contiene i CSV destinati alle
analisi e ai grafici. Il generatore legge esclusivamente i 42 JSON presenti in
`judge_results` e ignora i risultati pilota.

Lo scheletro editoriale del capitolo di tesi è disponibile in
`results/CAPITOLO_RISULTATI.md`. Il documento separa il racconto dei risultati
dal report tecnico e contiene gli spazi previsti per tabelle, grafici,
discussione e limiti.
