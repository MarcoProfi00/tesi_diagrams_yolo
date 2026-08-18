# Pipeline 2.0 - agente diagnostico autonomo controllato

Sei il controller diagnostico di una pipeline Graph JSON -> SPICE/ngspice.
Devi scegliere il prossimo test controllato oppure fermarti con una conclusione.

## Sintomo utente
Nella simulazione il LED commuta, ma il lampeggio non risulta regolare durante l’avvio. Quale potrebbe essere il problema e come posso risolverlo?

## Vincoli obbligatori
- Rispondi con un solo oggetto JSON valido, senza Markdown o testo esterno.
- Non inventare nodi, componenti, valori o risultati.
- Usa soltanto queste primitive: add_resistor_between_nodes, add_voltage_source_between_nodes, change_component_value, change_source_value, close_switch, connect_nodes, drive_node_voltage, feed_nodes_from_source_node, set_initial_node_voltage.
- Ogni scenario deve essere self-contained e partire dalla base run.
- Puoi proporre al massimo 2 scenari indipendenti.
- Budget residuo: 4 run scenario.
- Se il budget e zero devi restituire decision=stop.
- Prima di una conclusione diagnostica devi eseguire almeno uno scenario controllato
  quando il budget e disponibile: la sola base run localizza un sospetto, ma non lo verifica.
- Con budget disponibile usa final_status="resolved" solo dopo uno scenario con
  diagnostic_outcome.status=resolved_candidate e stop_automation=true.
- Puoi invece fermarti con final_status="localized" dopo uno scenario diagnostico
  forte che verifica la causa ma non rappresenta una riparazione del circuito.
- Se il sintomo utente richiede esplicitamente di correggere, risolvere, attivare,
  disattivare o ripristinare un comportamento, prova una correzione distinta e
  sostenuta dagli artefatti finche ne esiste una non ancora verificata.
- Quando l'utente chiede una correzione e resta budget, `decision=stop` non e
  ammessa finche non esiste una correzione verificata: passa a un'ipotesi
  elettricamente distinta e sostenuta dagli artefatti. Se nessuna risolve il
  sintomo, fermati con `inconclusive` soltanto a budget esaurito e lascia
  `verified_correction` vuoto.
- Se uno scenario migliora il sintomo ma viola un vincolo richiesto (per esempio
  perde regolarita, spegne un componente da preservare o degrada l'uscita), trattalo
  come evidenza diagnostica e non come correzione finale.
- Non consumare altro budget per trasformare una localizzazione gia verificata in
  una correzione topologica inventata o non sostenuta dagli artefatti.
- Non usare resolved_candidate come prova automatica di soluzione definitiva.
- Distingui una soluzione da una semplice localizzazione della causa.
- Ogni scenario deve dichiarare analysis="op" oppure analysis="tran".
- Ogni scenario deve dichiarare intent="correction" oppure intent="diagnostic".
- Usa intent="correction" soltanto per una modifica che mira a migliorare o
  risolvere direttamente il sintomo utente.
- Se una modifica mira direttamente a correggere il sintomo, dichiarala subito
  con intent="correction": non eseguire prima la stessa modifica come test
  diagnostico per poi tentare di ripeterla.
- Usa intent="diagnostic" per isolare o confermare una causa, compresi i test
  che riducono intenzionalmente una risposta o disattivano un comportamento.
- Uno scenario diagnostic puo confermare un'ipotesi, ma non puo giustificare
  final_status="resolved" ne arrestare il ciclo come correzione verificata.
- Usa analysis="tran" per ampiezza, Vpp, guadagno, frequenza, forma d'onda e
  qualsiasi sintomo dinamico. Usa analysis="op" soltanto per il punto di lavoro DC.
- Con analysis="tran" puoi dichiarare la mappa opzionale `measure` per scegliere
  la misura di ogni grandezza: `tran_vpp` per una tensione letta da 08_tran.csv,
  `op` per tensioni, correnti o potenze lette dal punto di lavoro, `tran_abs_peak` per
  il picco assoluto di una corrente interna `@dNOME[id]` letta da 08_tran.csv.
- `tran_vpp` accetta sia `v(NODO)` rispetto a massa sia `v(NODO1,NODO2)` per
  carichi flottanti: nel secondo caso usa la differenza campione per campione.
- Se `measure` non e presente resta valido il comportamento standard: le tensioni
  sono confrontate sul Vpp, mentre correnti e potenze restano osservazioni OP.
- In uno scenario misto puoi usare una corrente come criterio expect soltanto
  dichiarandola esplicitamente: `measure: {"i(R...)":"op"}` per una corrente
  OP oppure `measure: {"@dled...[id]":"tran_abs_peak"}` per verificare che
  un LED/diodo si sia attivato almeno una volta durante la run TRAN.
- Un voltmetro VAC, un segnale AC o una tensione alternata devono essere verificati
  con analysis="tran" e `tran_vpp`: un valore DC non dimostra il funzionamento AC.
- Per sintomi di amplificazione o guadagno, ogni scenario con intent="correction" deve includere
  `gain: {"input":"v(NODO_IN)","output":"v(NODO_OUT)"}`; entrambe le
  tensioni devono essere presenti in compare e possono anche usare la forma
  differenziale `v(NODO1,NODO2)`. Valuta il guadagno come
  Vpp(output) / Vpp(input), senza confondere due nodi entrambi di uscita.
- Per verificare propagazione o attenuazione di un segnale, anche uno scenario
  diagnostico deve aggiungere `gain.min_ratio` con una soglia positiva motivata
  dall'obiettivo dello scenario. Non usare il solo `changed` per concludere che
  un segnale non nullo ma trascurabile arrivi utilmente all'uscita.
- Quando aggiungi una sorgente `SIN(...)` a un nodo o tra due nodi gia esistenti,
  ricava prima dalla base run la tensione di punto operativo dello stesso nodo o
  della stessa coppia. Se la differenza DC e significativa, conserva quel valore
  come primo parametro di `SIN` e sovrapponi soltanto l'ampiezza AC richiesta.
  Usa offset zero solo se il nodo/la coppia e gia circa a 0 V oppure se lo
  scenario deve esplicitamente cambiare il bias DC.
- Per un test di propagazione iniettato direttamente sulla base di un BJT, usa
  un vero piccolo segnale di pochi millivolt (normalmente 1-10 mV di picco,
  salvo evidenze contrarie) e conserva il bias DC misurato. Decine di millivolt
  sulla base possono portare il transistor in interdizione o saturazione e non
  isolano piu il percorso lineare del segnale.
- Non ripetere le stesse azioni elettriche di una run gia eseguita soltanto per
  aggiungere gain, measure, expect o una soglia: reinterpreta le misure esistenti.
  Dopo un trasferimento insufficiente, sposta il confine di isolamento a un nodo
  intermedio giustificato oppure testa una causa elettricamente distinta.
- Non inserire due `change_source_value` sullo stesso target nella stessa run:
  la seconda assegnazione sovrascrive la prima e non costituisce uno sweep.
  Usa scenari separati per punti operativi statici diversi, oppure una sola
  sorgente `PWL(...)`/`SIN(...)` quando vuoi davvero una variazione temporale.
- Se il trasferimento fallisce con una sorgente SIN provata a una sola ampiezza,
  prima di concludere un guasto strutturale mantieni lo stesso percorso e la
  stessa frequenza e prova un'ampiezza significativamente diversa. Se anche il
  nuovo livello fallisce e resta budget, continua lo sweep; fermati appena il
  trasferimento diventa sufficiente. Non ripetere lo stesso stimolo aggiungendo
  soltanto una forzatura su un nodo di alimentazione.
- Prima di attribuire un'uscita assoluta debole a un guasto, verifica se il
  circuito sta gia amplificando un ingresso molto piccolo.
- Per sintomi di distorsione, clipping, saturazione o segnale poco pulito,
  ogni scenario transitorio deve dichiarare quality="thd" e il blocco gain
  deve identificare ingresso e uscita.
- La pipeline calcola la THD sulle armoniche 2-5 nelle ultime tre oscillazioni
  complete della sorgente SIN. Una correzione e risolutiva soltanto se la THD
  diminuisce almeno del 20%, scende sotto il 10% e il guadagno fondamentale
  non viene annullato.
- Se la metrica THD non e disponibile o resta sopra soglia, considera lo
  scenario parziale e continua con un test diverso, per esempio sul bias.
- Ogni scenario deve avere una lista compare non vuota con grandezze osservabili.
- Per scenari con piu rami o uscite, includi in compare almeno una grandezza per ciascuno.
- Se il sintomo combina un obiettivo AC/VAC e lo stato di un LED o di una
  lampada, ogni scenario deve verificarli insieme: usa un test misto con
  `tran_vpp` sul segnale e una misura diretta `op` sul componente.
- Due scenari separati che attivano un solo target ciascuno non verificano il
  funzionamento simultaneo: prima di fermarti esegui una singola run self-contained
  con entrambi gli stimoli e con entrambi i criteri soddisfatti.
- In questo caso non usare l'inattivita intenzionale di uno dei due target come
  prova sufficiente: lo scenario deve applicare gli stimoli indipendenti adatti.
- Se l'obiettivo richiede di attivare o spegnere un componente, includi in compare
  almeno una misura diretta del componente, preferendo i(NOME_SPICE).
- Se l'obiettivo richiede di mantenere invariato un altro componente, includi in
  compare anche una sua misura diretta: le sole tensioni di nodo non ne verificano lo stato.
- Ricava NOME_SPICE dalla netlist 07_netlist.cir; non usare l'id Graph JSON dentro i(...) o p(...).
- Non richiedere i(Q...) per un transistor BJT: questa misura diretta non e
  disponibile nel confronto corrente. Usa la corrente di una resistenza sul
  collettore o sull'emettitore come misura osservabile del ramo.
- Richiedi p(NOME_SPICE) soltanto se la potenza dello stesso dispositivo e gia
  disponibile negli output ngspice forniti; non aggiungere misure ridondanti.
- Ogni scenario deve avere un oggetto expect non vuoto. Le chiavi devono essere
  grandezze presenti in compare e i valori ammessi sono: activated, deactivated,
  changed, unchanged, increased, decreased, magnitude_increased,
  magnitude_decreased, nonzero.
- `activated` significa esclusivamente passaggio da una grandezza inattiva o
  nulla nella base run a una grandezza attiva nello scenario. Prima di usarlo,
  controlla sempre la misura base della stessa quantita negli artefatti o nella
  cronologia: se e gia diversa da zero, anche se debole, impulsiva o irregolare,
  `activated` e semanticamente errato e non potra essere soddisfatto.
- Quando la quantita base e gia non nulla, usa `changed`, `magnitude_increased`,
  `magnitude_decreased` o `nonzero` secondo l'effetto realmente richiesto. Per
  lampeggio, periodicita e duty cycle, affida la verifica dello stato dinamico a
  `temporal_expect`; non usare `activated` come suo sostituto.
- Inserisci in expect soltanto i comportamenti indispensabili per verificare
  l'obiettivo o preservare componenti richiesti dall'utente. Le altre misure
  possono restare in compare come osservazioni senza aspettativa.
- Una variazione direzionale minima non dimostra una correzione: per fermare
  il ciclo serve almeno un miglioramento relativo del 10%, oppure una vera
  attivazione/disattivazione del comportamento richiesto.
- Usa expect per descrivere sia l'effetto cercato sia i vincoli da preservare,
  per esempio corrente gia presente del target `magnitude_increased` e corrente
  del componente protetto `unchanged`. Usa `activated` soltanto se gli artefatti
  mostrano che la corrente base del target e davvero nulla o inattiva.
- Usa unchanged soltanto se il sintomo utente chiede esplicitamente di mantenere
  o preservare un altro componente o comportamento; altrimenti ometti quel
  vincolo e lascia la grandezza soltanto in compare.
- Se ngspice segnala nodi flottanti o matrice singolare, non usare la tensione
  assoluta di quei nodi come vincolo unchanged: il riferimento comune puo traslare.
  Preferisci correnti dirette e variazioni strettamente legate all'obiettivo.
- In analisi .op un condensatore non fornisce un percorso conduttivo DC: non
  proporre come chiusura del circuito un cammino che termina soltanto su un condensatore.
- Per una run .tran usa le tracce disponibili e confronta almeno l'uscita o il ramo
  direttamente coinvolto nell'obiettivo, oltre agli eventuali nodi intermedi.
- Per sintomi di ricarica o carica batteria, non usare la sola corrente di una
  sorgente `V...` come prova della carica: il suo segno dipende dalla convenzione
  SPICE e dalla sua polarita. Una correzione deve usare `.tran` e misurare anche
  un componente del percorso di carica direttamente giustificato dalla netlist
  (per esempio `@dNOME[id]` del raddrizzatore con `tran_abs_peak`). La corrente
  della sorgente puo essere soltanto un'evidenza di supporto, con segno spiegato.
- Per obiettivi che chiedono lampeggio, periodicita, regolarita, duty cycle o durata
  di accensione, ogni scenario deve dichiarare `temporal_expect`.
  Questo blocco usa il profilo transitorio del componente nel viewer: `target`,
  `required_state` opzionale, `require_regular_period` opzionale,
  `min_duty_cycle` opzionale tra 0 e 1 e `min_relative_duty_increase` opzionale.
- Scegli soglie coerenti con il sintomo: per esempio un lampeggio chiaramente visibile
  puo richiedere stato `blinking`, periodicita regolare e un duty cycle minimo.
  Se un test aumenta il duty cycle ma perde la periodicita richiesta, non e risolutivo.
- Quando usi `set_initial_node_voltage` per rompere un equilibrio simmetrico,
  scegli una tensione iniziale fisicamente ammissibile ma chiaramente separata
  dal punto di lavoro del nodo mostrato dagli artefatti. Una variazione di pochi
  punti percentuali attorno allo stesso bias non e un test sufficiente; preferisci
  un riferimento gia documentato nel circuito, senza inventarne uno.
- Se il sintomo riguarda l'avvio di un circuito dinamico e il punto operativo DC
  mantiene artificialmente la simmetria, puoi aggiungere
  `skip_operating_point: true` a `set_initial_node_voltage`. In questo caso ngspice
  usa `.tran ... UIC`: la condizione deve introdurre una reale asimmetria iniziale,
  per esempio un valore non nullo su uno dei nodi simmetrici. Non usare questa
  opzione per mascherare errori di topologia, alimentazione o componenti.
  Se esistono due nodi di controllo simmetrici, inizializzali nello stesso
  scenario a due livelli distinti e fisicamente ammissibili; lasciare entrambi
  implicitamente allo stesso valore non rompe la simmetria.
  Un nodo interno di controllo non e un ingresso di alimentazione: se una base
  BJT ha un punto di lavoro sotto il rail, non inizializzarla al rail completo.
  Ricava livelli moderati dal bias misurato e dal ruolo del dispositivo (per
  esempio, con una base al silicio attorno a 0.8 V e alimentazione a 5 V, usa
  un livello basso su un ramo e circa 1-1.5 V sull'altro, non 5 V).
  Per due basi BJT simmetriche, il primo test di avvio deve usare sul ramo basso
  il riferimento di massa gia presente, normalmente 0 V, e sull'altro un livello
  moderato vicino o poco sopra il bias misurato. Non scegliere un valore basso
  intermedio arbitrario se la massa e gia il riferimento elettrico documentato.
- Se un test iniziale `.ic` produce un profilo `transient_pulse`, oppure rende
  dinamiche grandezze prima statiche senza ottenere ancora periodicita regolare,
  considera promettente l'ipotesi di startup. Prima di cambiare componenti prova
  una sola seconda coppia di condizioni iniziali, materialmente diversa ma
  fisicamente ammissibile, sempre dalla base run. Solo se anche quel test non
  produce il comportamento richiesto passa a ipotesi sui valori dei componenti.
- Se un LED o un altro target presenta gia qualunque impulso o corrente non nulla
  nella base run, non usare `activated`, neppure se il profilo base e classificato
  `transient_pulse`, debole o irregolare. Confronta la sua traccia transitoria,
  scegli un'aspettativa di variazione coerente e usa `temporal_expect` per lo
  stato dinamico richiesto.
  `temporal_expect.target` deve contenere un solo identificatore testuale, non
  una lista; se sono coinvolti piu LED, confronta le correnti di tutti.
- Un solo scenario negativo basato esclusivamente su condizioni iniziali non
  dimostra un errore di valori o topologia. In assenza di altre evidenze
  strutturali, concludi `inconclusive` oppure continua con un test distinto.
- Non dichiarare verified_correction se i confronti non misurano direttamente sia
  il componente target sia gli eventuali componenti che devono restare attivi.
- Se final_status="resolved", verified_correction deve descrivere la correzione
  realmente verificata da uno scenario con intent="correction".
- Preferisci modifiche minime su componenti, valori e collegamenti gia esistenti.
- Usa nuove sorgenti o nuovi rami resistivi solo quando le evidenze tecniche li giustificano.
- Non usare `drive_node_voltage` su un nodo gia vincolato a una sorgente attiva,
  direttamente o tramite uno switch/collegamento quasi ideale chiuso nello stesso
  scenario: produrrebbe generatori in conflitto e correnti prive di significato.
- Usa feed_nodes_from_source_node solo da un nodo che gli output mostrano gia alimentato.
- Usa connect_nodes per una ipotesi di continuita mancante senza attribuire a un nodo il ruolo di sorgente.
- I pin distinti dello stesso connector rappresentano reti funzionali separate finche
  gli artefatti non dimostrano una continuita prevista. Se alimentano rami diversi,
  verifica prima ciascun ramo con la sorgente appropriata e non collegarli per comodita.
- Un pin collegato soltanto a uno switch verso massa non diventa un ingresso di
  alimentazione senza un'evidenza esplicita nella node map, nella netlist o nelle label.
- Non proporre connect_nodes e feed_nodes_from_source_node sulla stessa relazione tra nodi nella stessa decisione.
- Considera add_resistor_between_nodes una ipotesi distinta: aggiunge un vero accoppiamento resistivo, non un filo quasi ideale.
- Non riproporre azioni gia presenti nella cronologia cambiando soltanto titolo,
  aspettative o un valore quasi identico: uno scenario duplicato non produce nuova evidenza.
- Non usare add_resistor_between_nodes con pochi milliohm per imitare connect_nodes.
  Usalo per un vero ramo resistivo plausibile, come bias, pull-up, pull-down o shunt.
- Dopo uno scenario rifiutato come duplicato scegli una relazione, un componente
  o una ipotesi fisica realmente diversa.

## Schema delle azioni consentite
- drive_node_voltage: type, target, value
- set_initial_node_voltage: type, target, value, skip_operating_point opzionale booleano (solo analysis=tran; condizione iniziale senza sorgente permanente; con `true` abilita `.tran ... UIC`)
- change_source_value: type, target, value
- change_component_value: type, target, value
- close_switch: type, target, resistance opzionale
- connect_nodes: type, from, to, resistance opzionale
- feed_nodes_from_source_node: type, source_node, target_nodes, resistance opzionale
- add_voltage_source_between_nodes: type, positive, negative, value
- add_resistor_between_nodes: type, from, to, value

## Formati ammessi
{"decision":"run_scenarios","reason":"...","scenarios":[{"title":"...","hypothesis":"...","intent":"correction","analysis":"tran","actions":[{"type":"change_component_value","target":"Rtarget","value":"10k"}],"compare":["v(NOUT)"],"expect":{"v(NOUT)":"magnitude_increased"},"temporal_expect":{"target":"Dled1","required_state":"blinking","require_regular_period":true,"min_duty_cycle":0.10}}]}

oppure

{"decision":"stop","reason":"...","final_status":"resolved|localized|partially_localized|topology_issue|inconclusive","final_answer":"Sintesi breve della conclusione.","final_cause":"Causa tecnica individuata, senza ripetizioni.","verified_correction":"Correzione verificata dagli scenari, oppure stringa vuota se non verificata."}

## Decisioni e risultati precedenti
```json
[
  {
    "decision_number": 1,
    "decision": {
      "decision": "run_scenarios",
      "reason": "La base run mostra che il LED gia commuta ma con profilo transient_pulse e periodicita non regolare durante l’avvio; in un astabile 555 con R1=R2=C=1k/1k/1uF il sospetto piu forte e una condizione iniziale simmetrica imposta dal transient operating point, che non rompe subito l’equilibrio interno. Prima di concludere serve un test controllato di startup con condizioni iniziali asimmetriche, senza inventare topologie o valori.",
      "scenarios": [
        {
          "title": "Avvio asimmetrico del nodo timing e del control per rompere la simmetria iniziale",
          "hypothesis": "L’irregolarita iniziale dipende dal fatto che ngspice calcola un punto operativo iniziale con condensatori scarichi e stati interni quasi simmetrici; imponendo una reale asimmetria iniziale fisicamente ammissibile il 555 dovrebbe entrare subito in oscillazione regolare.",
          "intent": "correction",
          "analysis": "tran",
          "actions": [
            {
              "type": "set_initial_node_voltage",
              "target": "N001",
              "value": "0V",
              "skip_operating_point": true
            },
            {
              "type": "set_initial_node_voltage",
              "target": "N002",
              "value": "1V",
              "skip_operating_point": true
            }
          ],
          "compare": [
            "v(N001)",
            "v(N002)",
            "v(N005)",
            "v(N006)",
            "@dled12_1[id]"
          ],
          "measure": {
            "@dled12_1[id]": "tran_abs_peak"
          },
          "expect": {
            "v(N005)": "changed",
            "v(N006)": "changed",
            "@dled12_1[id]": "nonzero"
          },
          "temporal_expect": {
            "target": "Dled12_1",
            "required_state": "blinking",
            "require_regular_period": true,
            "min_duty_cycle": 0.1
          }
        }
      ]
    },
    "prompt_path": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\ic_chat_agent_evaluation\\web\\agent\\ic01\\experiment_chat\\autonomous_prompt_1.md",
    "response_paths": [
      "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\ic_chat_agent_evaluation\\web\\agent\\ic01\\experiment_chat\\autonomous_response_1_attempt_1.txt"
    ],
    "scenario_results": [
      {
        "scenario_id": "agent_scenario_1",
        "scenario_dir": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\ic_chat_agent_evaluation\\web\\agent\\ic01\\scenarios\\agent_scenario_1",
        "run_dir": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\ic_chat_agent_evaluation\\web\\agent\\ic01\\scenarios\\agent_scenario_1\\run",
        "status": "spice_success",
        "spice_executed": true,
        "spice_status": "success",
        "spice_exit_code": 0,
        "comparison_summary": {
          "requested_count": 5,
          "changed_count": 5,
          "activated_count": 0,
          "missing_count": 0,
          "expected_count": 3,
          "expectations_met_count": 3,
          "expectations_failed_count": 0,
          "expectations_missing_count": 0,
          "meaningful_improvement_count": 0,
          "quality_required": false,
          "quality_available": false,
          "quality_improved": false,
          "quality_acceptable": false,
          "quality_output_preserved": false,
          "base_thd": null,
          "scenario_thd": null,
          "gain_required": false,
          "gain_available": false,
          "gain_sufficient": false,
          "scenario_gain": null,
          "min_gain_ratio": null,
          "temporal_required": true,
          "temporal_available": true,
          "temporal_met": false
        },
        "diagnostic_outcome": {
          "status": "partially_resolved",
          "technical_label": "Temporal criteria not satisfied",
          "label": "Criteri temporali non soddisfatti",
          "reason": "Almeno un criterio temporale non e soddisfatto.",
          "user_message": "Lo scenario conferma utilmente l'ipotesi sul ramo o nodo testato.",
          "stop_automation": false,
          "confidence": "low",
          "next_step": "Il comportamento temporale non soddisfa ancora l'obiettivo: prova un'altra correzione."
        },
        "viewer": {
          "model": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\ic_chat_agent_evaluation\\web\\agent\\ic01\\scenarios\\agent_scenario_1\\run\\13_viewer_model.json",
          "layout": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\ic_chat_agent_evaluation\\web\\agent\\ic01\\scenarios\\agent_scenario_1\\run\\14_viewer_layout.json",
          "svg": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\ic_chat_agent_evaluation\\web\\agent\\ic01\\scenarios\\agent_scenario_1\\run\\15_viewer.svg"
        },
        "viewer_error": null,
        "executed_scenarios_count": 1
      }
    ]
  }
]
```

## Evidenze tecniche correnti
## 03_node_map.json
```text
{
  "circuit_id": "ic01",
  "source_format": "pipeline2.0_node_map",
  "nodes": [
    {
      "node_id": "0",
      "kind": "ground",
      "terminals": [
        "capacitor4.1_t2",
        "capacitor4.2_t2",
        "capacitor4.3_t2",
        "gnd9.1_t1",
        "integrated_circuit11.1_bottom_2",
        "led12.1_cathode"
      ],
      "terminal_count": 6,
      "source_groups": [
        [
          "capacitor4.1_t2",
          "capacitor4.2_t2",
          "capacitor4.3_t2",
          "gnd9.1_t1",
          "integrated_circuit11.1_bottom_2",
          "led12.1_cathode"
        ]
      ]
    },
    {
      "node_id": "N001",
      "kind": "normal",
      "terminals": [
        "capacitor4.1_t1",
        "integrated_circuit11.1_bottom_1",
        "integrated_circuit11.1_left_2",
        "resistor22.1_t2"
      ],
      "terminal_count": 4
    },
    {
      "node_id": "N002",
      "kind": "normal",
      "terminals": [
        "capacitor4.2_t1",
        "integrated_circuit11.1_right_2"
      ],
      "terminal_count": 2
    },
    {
      "node_id": "N003",
      "kind": "normal",
      "terminals": [
        "capacitor4.3_t1",
        "integrated_circuit11.1_top_1",
        "integrated_circuit11.1_top_2",
        "resistor22.2_t1",
        "terminal26.1_t1"
      ],
      "terminal_count": 5
    },
    {
      "node_id": "N004",
      "kind": "normal",
      "terminals": [
        "integrated_circuit11.1_left_1",
        "resistor22.1_t1",
        "resistor22.2_t2"
      ],
      "terminal_count": 3
    },
    {
      "node_id": "N005",
      "kind": "normal",
      "terminals": [
        "integrated_circuit11.1_right_1",
        "resistor22.3_t1"
      ],
      "terminal_count": 2
    },
    {
      "node_id": "N006",
      "kind": "normal",
      "terminals": [
        "led12.1_anode",
        "resistor22.3_t2"
      ],
      "terminal_count": 2
    }
  ],
  "terminal_to_node": {
    "capacitor4.1_t1": "N001",
    "capacitor4.1_t2": "0",
    "capacitor4.2_t1": "N002",
    "capacitor4.2_t2": "0",
    "capacitor4.3_t1": "N003",
    "capacitor4.3_t2": "0",
    "gnd9.1_t1": "0",
    "integrated_circuit11.1_bottom_1": "N001",
    "integrated_circuit11.1_bottom_2": "0",
    "integrated_circuit11.1_left_1": "N004",
    "integrated_circuit11.1_left_2": "N001",
    "integrated_circuit11.1_right_1": "N005",
    "integrated_circuit11.1_right_2": "N002",
    "integrated_circuit11.1_top_1": "N003",
    "integrated_circuit11.1_top_2": "N003",
    "led12.1_anode": "N006",
    "led12.1_cathode": "0",
    "resistor22.1_t1": "N004",
    "resistor22.1_t2": "N001",
    "resistor22.2_t1": "N003",
    "resistor22.2_t2": "N004",
    "resistor22.3_t1": "N005",
    "resistor22.3_t2": "N006",
    "terminal26.1_t1": "N003"
  },
  "component_terminal_nodes": {
    "capacitor4.1": {
      "t1": "N001",
      "t2": "0"
    },
    "capacitor4.2": {
      "t1": "N002",
      "t2": "0"
    },
    "capacitor4.3": {
      "t1": "N003",
      "t2": "0"
    },
    "gnd9.1": {
      "t1": "0"
    },
    "integrated_circuit11.1": {
      "left_1": "N004",
      "left_2": "N001",
      "right_1": "N005",
      "right_2": "N002",
      "top_1": "N003",
      "top_2": "N003",
      "bottom_1": "N001",
      "bottom_2": "0"
    },
    "led12.1": {
      "anode": "N006",
      "cathode": "0"
    },
    "resistor22.1": {
      "t1": "N004",
      "t2": "N001"
    },
    "resistor22.2": {
      "t1": "N003",
      "t2": "N004"
    },
    "resistor22.3": {
      "t1": "N005",
      "t2": "N006"
    },
    "terminal26.1": {
      "t1": "N003"
    }
  },
  "warnings": {
    "ground_groups_count": 1,
    "multiple_ground_groups_merged_as_node_0": false,
    "singleton_nodes": [],
    "original_warnings": {
      "unconnected_terminals": [],
      "unmatched_terminals": [],
      "suspicious_matches": []
    },
    "normalization_warnings": []
  },
  "stats": {
    "nodes_count": 7,
    "normal_nodes_count": 6,
    "ground_nodes_count": 1,
    "ground_groups_count": 1,
    "terminal_to_node_count": 24,
    "singleton_nodes_count": 0
  }
}

```

## 06_component_rules.json
```text
{
  "circuit_id": "ic01",
  "source_format": "pipeline2.0_component_rules",
  "values_source": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\data\\batchPipeline2.0\\batchICChatAgentEvaluation\\values\\ic01_values.yaml",
  "spice_classes_source": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\metadata\\pipeline2_spice_classes.yaml",
  "supplies": {
    "VCC_9": {
      "status": "spice_ready",
      "spice_prefix": "V",
      "emit_as": "independent_voltage_source",
      "nodes": [
        "N003",
        "0"
      ],
      "parameters": {
        "terminal": "terminal26.1_t1",
        "type": "dc",
        "value": 9,
        "unit": "V",
        "reference": 0,
        "source": "manual_from_image_label",
        "label_text": "+9 V DC",
        "viewer_override": {
          "visual_class": "voltage_source",
          "label": "+9 V",
          "display_value": "9 V DC"
        },
        "node": "N003"
      }
    }
  },
  "components": {
    "capacitor4.1": {
      "class_name": "Capacitor",
      "status": "spice_ready",
      "spice_support": "direct",
      "spice_prefix": "C",
      "emit_as": "capacitor",
      "node_order": [
        "t1",
        "t2"
      ],
      "nodes": [
        "N001",
        "0"
      ],
      "parameters": {
        "value": 1,
        "unit": "uf",
        "source": "manual_from_image_label",
        "label_text": "C1 1 uF",
        "viewer_override": {
          "label": "C1",
          "display_value": "1 uF"
        }
      }
    },
    "capacitor4.2": {
      "class_name": "Capacitor",
      "status": "spice_ready",
      "spice_support": "direct",
      "spice_prefix": "C",
      "emit_as": "capacitor",
      "node_order": [
        "t1",
        "t2"
      ],
      "nodes": [
        "N002",
        "0"
      ],
      "parameters": {
        "value": 1,
        "unit": "uf",
        "source": "manual_from_image_label",
        "label_text": "C2 1 uF",
        "viewer_override": {
          "label": "C2",
          "display_value": "1 uF"
        }
      }
    },
    "capacitor4.3": {
      "class_name": "Capacitor",
      "status": "spice_ready",
      "spice_support": "direct",
      "spice_prefix": "C",
      "emit_as": "capacitor",
      "node_order": [
        "t1",
        "t2"
      ],
      "nodes": [
        "N003",
        "0"
      ],
      "parameters": {
        "value": 1,
        "unit": "uf",
        "source": "manual_from_image_label",
        "label_text": "C3 1 uF",
        "viewer_override": {
          "label": "C3",
          "display_value": "1 uF"
        }
      }
    },
    "gnd9.1": {
      "class_name": "GND",
      "status": "not_emitted",
      "spice_support": "structural",
      "reason": "GND terminals are already mapped to SPICE node 0."
    },
    "integrated_circuit11.1": {
      "class_name": "Integrated_Circuit",
      "status": "spice_ready",
      "spice_support": "subcircuit",
      "spice_prefix": "X",
      "emit_as": "subcircuit",
      "node_order": [
        "THRES",
        "CONT",
        "TRIG",
        "RESET",
        "OUT",
        "DISC",
        "VCC",
        "GND"
      ],
      "nodes": [
        "N001",
        "N002",
        "N001",
        "N003",
        "N005",
        "N004",
        "N003",
        "0"
      ],
      "parameters": {
        "model": "TLC555_6",
        "source": "ti_official_slfj002e_pspice_model",
        "label_text": "IC1 555 Timer; modello ufficiale TI TLC555_6 Rev. E",
        "viewer_override": {
          "label": "IC1",
          "display_value": "TLC555",
          "tooltip": "IC1 TLC555; modello ufficiale TI PSpice Rev. E SLFJ002E"
        },
        "spice_override": {
          "emit_as": "subcircuit",
          "pin_order": [
            "THRES",
            "CONT",
            "TRIG",
            "RESET",
            "OUT",
            "DISC",
            "VCC",
            "GND"
          ],
          "node_refs": {
            "THRES": "integrated_circuit11.1_left_2",
            "CONT": "integrated_circuit11.1_right_2",
            "TRIG": "integrated_circuit11.1_bottom_1",
            "RESET": "integrated_circuit11.1_top_1",
            "OUT": "integrated_circuit11.1_right_1",
            "DISC": "integrated_circuit11.1_left_1",
            "VCC": "integrated_circuit11.1_top_2",
            "GND": "integrated_circuit11.1_bottom_2"
          },
          "resolved_node_refs": {
            "THRES": "N001",
            "CONT": "N002",
            "TRIG": "N001",
            "RESET": "N003",
            "OUT": "N005",
            "DISC": "N004",
            "VCC": "N003",
            "GND": "0"
          }
        }
      },
      "reason": "Explicit YAML override emitted as a SPICE subcircuit."
    },
    "led12.1": {
      "class_name": "LED",
      "status": "spice_ready",
      "spice_support": "model",
      "spice_prefix": "D",
      "emit_as": "diode",
      "node_order": [
        "anode",
        "cathode"
      ],
      "nodes": [
        "N006",
        "0"
      ],
      "parameters": {
        "model": "LED_RED",
        "source": "manual_assumption_standard_red_led",
        "label_text": "LED rosso standard; part number non specificato",
        "viewer_override": {
          "label": "LED",
          "display_value": "red",
          "tooltip": "LED rosso standard assunto; part number non indicato nello schema"
        }
      }
    },
    "resistor22.1": {
      "class_name": "Resistor",
      "status": "spice_ready",
      "spice_support": "direct",
      "spice_prefix": "R",
      "emit_as": "resistor",
      "node_order": [
        "t1",
        "t2"
      ],
      "nodes": [
        "N004",
        "N001"
      ],
      "parameters": {
        "value": 1,
        "unit": "kohm",
        "source": "manual_from_image_label",
        "label_text": "R2 1 kohm",
        "viewer_override": {
          "label": "R2",
          "display_value": "1 kohm"
        }
      }
    },
    "resistor22.2": {
      "class_name": "Resistor",
      "status": "spice_ready",
      "spice_support": "direct",
      "spice_prefix": "R",
      "emit_as": "resistor",
      "node_order": [
        "t1",
        "t2"
      ],
      "nodes": [
        "N003",
        "N004"
      ],
      "parameters": {
        "value": 1,
        "unit": "kohm",
        "source": "manual_from_image_label",
        "label_text": "R1 1 kohm",
        "viewer_override": {
          "label": "R1",
          "display_value": "1 kohm"
        }
      }
    },
    "resistor22.3": {
      "class_name": "Resistor",
      "status": "spice_ready",
      "spice_support": "direct",
      "spice_prefix": "R",
      "emit_as": "resistor",
      "node_order": [
        "t1",
        "t2"
      ],
      "nodes": [
        "N005",
        "N006"
      ],
      "parameters": {
        "value": 1,
        "unit": "kohm",
        "source": "manual_from_image_label",
        "label_text": "R3 1 kohm",
        "viewer_override": {
          "label": "R3",
          "display_value": "1 kohm"
        }
      }
    },
    "terminal26.1": {
      "class_name": "Terminal",
      "status": "not_emitted",
      "spice_support": "structural",
      "reason": "External terminal/label; useful for nodes and interface handling."
    }
  },
  "simulation": {
    "analyses": [
      "tran"
    ],
    "tran": {
      "step": "5us",
      "stop": "100ms"
    }
  },
  "stats": {
    "components_total": 10,
    "spice_ready_components": 8,
    "not_emitted_components": 2,
    "measurement_components": 0,
    "missing_components": 0,
    "unsupported_components": 0,
    "pin_aware_components": 0,
    "invalid_components": 0,
    "supplies_ready_count": 1
  }
}

```

## 07_netlist.cir
```text
* pipeline2.0 netlist
* circuit: ic01

VVCC_9 N003 0 DC 9
Ccapacitor4_1 N001 0 1u
Ccapacitor4_2 N002 0 1u
Ccapacitor4_3 N003 0 1u
Xintegrated_circuit11_1 N001 N002 N001 N003 N005 N004 N003 0 TLC555_6
Dled12_1 N006 0 LED_RED
Rresistor22_1 N004 N001 1k
Rresistor22_2 N003 N004 1k
Rresistor22_3 N005 N006 1k

.model LED_RED D
.include "07_external_models.lib"

.save all
.tran 5us 100ms

.control
set wr_singlescale
set wr_vecnames
save all @dled12_1[id]
run
wrdata 08_tran.csv time v(N001) v(N002) v(N003) v(N004) v(N005) v(N006) @dled12_1[id]
.endc
.end

```

## 07_spice_emit_report.json
```text
{
  "circuit_id": "ic01",
  "source_format": "pipeline2.0_spice_emit_report",
  "emitted_elements": 9,
  "skipped_elements": 2,
  "skipped_components": [
    "gnd9.1",
    "terminal26.1"
  ],
  "informational_skips": [
    "gnd9.1: structural component not emitted",
    "terminal26.1: structural component not emitted"
  ],
  "measurement_points": [],
  "analyses": [
    "tran"
  ],
  "transient_export": {
    "path": "08_tran.csv",
    "nodes": [
      "N001",
      "N002",
      "N003",
      "N004",
      "N005",
      "N006"
    ],
    "device_currents": [
      "@dled12_1[id]"
    ]
  },
  "models": [
    "LED_RED",
    "TLC555_6"
  ],
  "warnings": [],
  "external_model_sources": [
    {
      "model": "TLC555_6",
      "kind": "file",
      "file": "spice_models/ti/tlc555/slfj002e/TLC555_6.LIB",
      "sha256": "7C091782CC4931DDA4FEBF25605083F47161C5E1592C076689B04B70DD749034"
    }
  ],
  "ngspice_defines": {
    "ngbehavior": "ps"
  }
}

```

## 08_ngspice_stdout.txt
```text
Note: gnd in a subcircuit is not set to 0 automatically

Note: Compatibility modes selected: ps


Circuit: * pipeline2.0 netlist

Reducing trtol to 1 for xspice 'A' devices
Doing analysis at TEMP = 27.000000 and TNOM = 27.000000

Using SPARSE 1.3 as Direct Linear Solver

Initial Transient Solution
--------------------------

Node                                   Voltage
----                                   -------
n003                                         9
n001                                   0.37893
n002                                 0.0581163
xintegrated_circuit11_1.resi                 9
xintegrated_circuit11_1.trgi          0.378927
xintegrated_circuit11_1.thri          0.378927
xintegrated_circuit11_1.conti         0.326105
xintegrated_circuit11_1.qff                  1
xintegrated_circuit11_1.gout       5.31855e-07
xintegrated_circuit11_1.trgo        0.00247082
xintegrated_circuit11_1.xmn3.10            0.14
xintegrated_circuit11_1.23            0.186463
xintegrated_circuit11_1.thrs        -0.0039892
xintegrated_circuit11_1.xmn5.10            0.14
xintegrated_circuit11_1.25            0.150433
xintegrated_circuit11_1.reso        0.00031436
xintegrated_circuit11_1.15           0.0377662
xintegrated_circuit11_1.xmp9.10            8.15
xintegrated_circuit11_1.xmp6.10            8.15
xintegrated_circuit11_1.trgs          0.754236
xintegrated_circuit11_1.xmp5.10            8.15
xintegrated_circuit11_1.thro           8.46572
xintegrated_circuit11_1.xmp1.10            8.86
xintegrated_circuit11_1.29                8.86
xintegrated_circuit11_1.xib.gb_int1     3.77573e-08
xintegrated_circuit11_1.xrsff.xu1.out_vmeas_0    -1.13852e-15
xintegrated_circuit11_1.xrsff.xu1.eout_int1    -1.13852e-15
xintegrated_circuit11_1.30        -1.13852e-15
xintegrated_circuit11_1.xrsff.xu2.out_vmeas_2               1
xintegrated_circuit11_1.xrsff.xu2.eout_int1               1
xintegrated_circuit11_1.xrsff.xu2.1        0.122699
xintegrated_circuit11_1.xrsff.xu2.e1_int1        0.122699
n004                                   4.68946
n005                                   8.52024
xintegrated_circuit11_1.trgc         0.0870928
xintegrated_circuit11_1.32          -0.0249399
xintegrated_circuit11_1.33             0.18685
xintegrated_circuit11_1.34             4.66305
n006                                  0.708287
b.xintegrated_circuit11_1.xrsff.xu2.be1#branch               0
b.xintegrated_circuit11_1.xrsff.xu2.beout#branch               0
v.xintegrated_circuit11_1.xrsff.xu2.v_eout#branch    -2.00594e-12
b.xintegrated_circuit11_1.xrsff.xu1.beout#branch               0
v.xintegrated_circuit11_1.xrsff.xu1.v_eout#branch    -1.13852e-16
b.xintegrated_circuit11_1.xib.bgb#branch               0
v.xintegrated_circuit11_1.xmp1.v1#branch     1.78919e-11
v.xintegrated_circuit11_1.xmn5.v1#branch     4.41926e-09
v.xintegrated_circuit11_1.xmn3.v1#branch      7.8362e-07
e.xintegrated_circuit11_1.xrsff.xu2.e1#branch               0
e.xintegrated_circuit11_1.xrsff.xu2.eout#branch    -2.00594e-12
e.xintegrated_circuit11_1.xrsff.xu1.eout#branch    -1.13852e-16
v.xintegrated_circuit11_1.xmp5.v1#branch     8.39576e-12
v.xintegrated_circuit11_1.xmp6.v1#branch     8.99957e-12
v.xintegrated_circuit11_1.xmp9.v1#branch     9.14969e-12
vvcc_9#branch                       -0.0171681

 Reference value :  2.30777e-02
 Reference value :  6.71178e-02

No. of Data Rows : 24426
Note: Simulation executed from .control section 

```

## 08_ngspice_stderr.txt
```text
Warning: Model issue on line 118 :
  .model xintegrated_circuit11_1.xmn17:tlc55x_nmosd_hv nmos level=3 l=10u  ...
unrecognized parameter (lambda) - ignored

Warning: Model issue on line 118 :
  .model xintegrated_circuit11_1.xmn16:tlc55x_nmosd_hv nmos level=3 l=10u  ...
unrecognized parameter (lambda) - ignored

Warning: Model issue on line 204 :
  .model xintegrated_circuit11_1.xmp16:tlc55x_pmosd_hv pmos level=3 l=10u  ...
unrecognized parameter (lambda) - ignored

Note: Starting dynamic gmin stepping
Warning: Dynamic gmin stepping failed
Note: Starting true gmin stepping
Warning: True gmin stepping failed
Note: Starting source stepping
Warning: source stepping failed
Note: Transient op started
Note: Transient op finished successfully

```

## 10_diagnostic_context.json
```text
{
  "source_format": "pipeline2.0_diagnostic_context_manifest",
  "batch_name": "batchICChatAgentEvaluation",
  "experiment_name": "ic_chat_agent_evaluation",
  "circuit_id": "ic01",
  "user_problem": "Nella simulazione il LED commuta, ma il lampeggio non risulta regolare durante l’avvio. Quale potrebbe essere il problema e come posso risolverlo?",
  "pipeline2_output_dir": "outputs\\demo_workspaces\\ic_chat_agent_evaluation\\web\\agent\\ic01",
  "summary": {
    "spice_status": "success",
    "spice_exit_code": 0,
    "spice_message": "ngspice completed successfully.",
    "emitted_elements": 9,
    "skipped_elements": 2,
    "emit_warnings_count": 0,
    "skipped_components_count": 2,
    "node_count": 7,
    "ground_groups_count": 1,
    "singleton_nodes_count": 0,
    "bound_components": 7,
    "missing_components": 0,
    "unsupported_components": 1,
    "spice_ready_components": 8,
    "rules_missing_components": 0,
    "has_tran_csv": true,
    "has_tran_plot": true,
    "led_profiles": {
      "Dled12_1": {
        "state": "transient_pulse",
        "regular_period": false,
        "frequency_hz": null,
        "duty_cycle": 0.5147793334970933,
        "on_fraction": 0.5147793334970933,
        "pulse_count": 63,
        "voltage_min": -0.0342456757,
        "voltage_max": 0.708918299,
        "anode_node": "N006",
        "cathode_node": "0"
      }
    }
  },
  "artifacts": {
    "graph": {
      "step": "01",
      "available": true,
      "path": "outputs\\demo_workspaces\\ic_chat_agent_evaluation\\web\\agent\\ic01\\01_graph.json",
      "role": "Graph JSON copied from Pipeline 1.0."
    },
    "normalized_circuit": {
      "step": "02",
      "available": true,
      "path": "outputs\\demo_workspaces\\ic_chat_agent_evaluation\\web\\agent\\ic01\\02_normalized_circuit.json",
      "role": "Normalized circuit representation used by Pipeline 2.0."
    },
    "node_map": {
      "step": "03",
      "available": true,
      "path": "outputs\\demo_workspaces\\ic_chat_agent_evaluation\\web\\agent\\ic01\\03_node_map.json",
      "role": "Maps component terminals to SPICE node names."
    },
    "values_bound": {
      "step": "04",
      "available": true,
      "path": "outputs\\demo_workspaces\\ic_chat_agent_evaluation\\web\\agent\\ic01\\04_values_bound.json",
      "role": "Values and labels bound to graph components."
    },
    "component_rules": {
      "step": "06",
      "available": true,
      "path": "outputs\\demo_workspaces\\ic_chat_agent_evaluation\\web\\agent\\ic01\\06_component_rules.json",
      "role": "SPICE conversion rules for each component."
    },
    "netlist": {
      "step": "07",
      "available": true,
      "path": "outputs\\demo_workspaces\\ic_chat_agent_evaluation\\web\\agent\\ic01\\07_netlist.cir",
      "role": "Generated SPICE netlist."
    },
    "spice_emit_report": {
      "step": "07",
      "available": true,
      "path": "outputs\\demo_workspaces\\ic_chat_agent_evaluation\\web\\agent\\ic01\\07_spice_emit_report.json",
      "role": "Report of emitted, skipped and warning components."
    },
    "spice_run": {
      "step": "08",
      "available": true,
      "path": "outputs\\demo_workspaces\\ic_chat_agent_evaluation\\web\\agent\\ic01\\08_spice_run.json",
      "role": "Structured ngspice execution report."
    },
    "ngspice_stdout": {
      "step": "08",
      "available": true,
      "path": "outputs\\demo_workspaces\\ic_chat_agent_evaluation\\web\\agent\\ic01\\08_ngspice_stdout.txt",
      "role": "Raw ngspice stdout log."
    },
    "ngspice_stderr": {
      "step": "08",
      "available": true,
      "path": "outputs\\demo_workspaces\\ic_chat_agent_evaluation\\web\\agent\\ic01\\08_ngspice_stderr.txt",
      "role": "Raw ngspice stderr log."
    },
    "tran_csv": {
      "step": "08",
      "available": true,
      "path": "outputs\\demo_workspaces\\ic_chat_agent_evaluation\\web\\agent\\ic01\\08_tran.csv",
      "role": "Clean transient CSV, when .tran data is available."
    },
    "tran_plot_png": {
      "step": "08",
      "available": true,
      "path": "outputs\\demo_workspaces\\ic_chat_agent_evaluation\\web\\agent\\ic01\\08_tran_plot.png",
      "role": "Transient plot PNG, when generated."
    },
    "tran_plot_svg": {
      "step": "08",
      "available": false,
      "path": null,
      "role": "Transient plot SVG fallback, when generated."
    }
  },
  "executed_scenarios": [
    {
      "scenario_dir": "outputs\\demo_workspaces\\ic_chat_agent_evaluation\\web\\agent\\ic01\\scenarios\\agent_scenario_1",
      "scenario_id": "agent_scenario_1",
      "title": "Avvio asimmetrico del nodo timing e del control per rompere la simmetria iniziale",
      "status": "spice_success",
      "spice_status": "success",
      "diagnostic_outcome": {
        "status": "partially_resolved",
        "technical_label": "Temporal criteria not satisfied",
        "label": "Criteri temporali non soddisfatti",
        "reason": "Almeno un criterio temporale non e soddisfatto.",
        "user_message": "Lo scenario conferma utilmente l'ipotesi sul ramo o nodo testato.",
        "stop_automation": false,
        "confidence": "low",
        "next_step": "Il comportamento temporale non soddisfa ancora l'obiettivo: prova un'altra correzione."
      },
      "comparison_summary": {
        "requested_count": 5,
        "changed_count": 5,
        "activated_count": 0,
        "missing_count": 0,
        "expected_count": 3,
        "expectations_met_count": 3,
        "expectations_failed_count": 0,
        "expectations_missing_count": 0,
        "meaningful_improvement_count": 0,
        "quality_required": false,
        "quality_available": false,
        "quality_improved": false,
        "quality_acceptable": false,
        "quality_output_preserved": false,
        "base_thd": null,
        "scenario_thd": null,
        "gain_required": false,
        "gain_available": false,
        "gain_sufficient": false,
        "scenario_gain": null,
        "min_gain_ratio": null,
        "temporal_required": true,
        "temporal_available": true,
        "temporal_met": false
      },
      "led_profiles": {
        "Dled12_1": {
          "state": "transient_pulse",
          "regular_period": false,
          "frequency_hz": null,
          "duty_cycle": 0.5291957548121545,
          "on_fraction": 0.5291957548121545,
          "pulse_count": 61,
          "voltage_min": -0.0325760812,
          "voltage_max": 0.708946253,
          "anode_node": "N006",
          "cathode_node": "0"
        }
      },
      "artifacts": {
        "scenario_definition": {
          "available": true,
          "path": "outputs\\demo_workspaces\\ic_chat_agent_evaluation\\web\\agent\\ic01\\scenarios\\agent_scenario_1\\scenario.json",
          "role": "Scenario selected by the user and saved before execution."
        },
        "scenario_status": {
          "available": true,
          "path": "outputs\\demo_workspaces\\ic_chat_agent_evaluation\\web\\agent\\ic01\\scenarios\\agent_scenario_1\\scenario_status.json",
          "role": "Current scenario status, SPICE status and diagnostic outcome."
        },
        "controlled_scenario_report": {
          "available": true,
          "path": "outputs\\demo_workspaces\\ic_chat_agent_evaluation\\web\\agent\\ic01\\scenarios\\agent_scenario_1\\12_controlled_scenarios.json",
          "role": "Report produced by the controlled scenario runner."
        },
        "scenario_comparison": {
          "available": true,
          "path": "outputs\\demo_workspaces\\ic_chat_agent_evaluation\\web\\agent\\ic01\\scenarios\\agent_scenario_1\\scenario_comparison.json",
          "role": "Base-vs-scenario comparison used to evaluate the scenario."
        }
      }
    }
  ],
  "scenario_outcome_summary": {
    "available": true,
    "best_scenario_id": "agent_scenario_1",
    "best_outcome_status": "partially_resolved",
    "best_stop_automation": false,
    "ranking_status": "verified_best",
    "interpretation_rule": "If a user asks which scenario resolves the problem, prefer the scenario with outcome_status='resolved_candidate' and stop_automation=true. Partially resolved scenarios without verified expectations are supporting diagnostics and must not be ranked only by changed_count.",
    "scenarios": [
      {
        "scenario_id": "agent_scenario_1",
        "title": "Avvio asimmetrico del nodo timing e del control per rompere la simmetria iniziale",
        "status": "spice_success",
        "spice_status": "success",
        "outcome_status": "partially_resolved",
        "outcome_label": "Criteri temporali non soddisfatti",
        "outcome_technical_label": "Temporal criteria not satisfied",
        "outcome_reason": "Almeno un criterio temporale non e soddisfatto.",
        "stop_automation": false,
        "comparison_summary": {
          "requested_count": 5,
          "changed_count": 5,
          "activated_count": 0,
          "missing_count": 0,
          "expected_count": 3,
          "expectations_met_count": 3,
          "expectations_failed_count": 0,
          "expectations_missing_count": 0,
          "meaningful_improvement_count": 0,
          "quality_required": false,
          "quality_available": false,
          "quality_improved": false,
          "quality_acceptable": false,
          "quality_output_preserved": false,
          "base_thd": null,
          "scenario_thd": null,
          "gain_required": false,
          "gain_available": false,
          "gain_sufficient": false,
          "scenario_gain": null,
          "min_gain_ratio": null,
          "temporal_required": true,
          "temporal_available": true,
          "temporal_met": false
        },
        "quantity_summary": {
          "changed": [
            "v(N001)",
            "v(N002)",
            "v(N005)",
            "v(N006)",
            "@dled12_1[id]"
          ],
          "unchanged": [],
          "missing": []
        },
        "led_profiles": {
          "Dled12_1": {
            "state": "transient_pulse",
            "regular_period": false,
            "frequency_hz": null,
            "duty_cycle": 0.5291957548121545,
            "on_fraction": 0.5291957548121545,
            "pulse_count": 61,
            "voltage_min": -0.0325760812,
            "voltage_max": 0.708946253,
            "anode_node": "N006",
            "cathode_node": "0"
          }
        },
        "ranking_verified": true,
        "score": 35
      }
    ]
  },
  "scenario_budget": {
    "max_executable_scenarios": 5,
    "executed_scenarios_count": 1,
    "remaining_executable_scenarios": 4,
    "budget_exhausted": false,
    "last_scenario_available": false,
    "policy": "At most 5 scenarios can be executed for the same circuit. When only one scenario remains, the agent should propose a single final scenario. When no scenario remains, the agent must stop proposing new scenarios and provide a final diagnostic conclusion."
  },
  "image_access": {
    "included_by_default": false,
    "can_be_requested": true,
    "path": "outputs\\demo_workspaces\\ic_chat_agent_evaluation\\input\\images\\ic01.jpg",
    "policy": "Only request the image if structured outputs suggest that the Graph JSON may be incomplete or wrong."
  },
  "agent_mode": "graph_grounded_readonly",
  "agent_rules": [
    "Treat this file as a manifest, not as the full diagnostic evidence.",
    "Load the referenced artifacts needed for the answer.",
    "Use graph, node map, component rules, netlist, stdout and stderr as evidence.",
    "If executed_scenarios are available, use them as evidence for questions about scenario outcomes.",
    "Do not invent values, connections, models or simulation results.",
    "Do not use the image unless image_access is explicitly requested.",
    "If Graph JSON inconsistency is suspected, explain which structured outputs suggest it.",
    "In read-only mode, do not modify netlists and do not execute scenarios.",
    "Never exceed 5 executed scenarios for the same circuit.",
    "When the scenario budget is exhausted, stop proposing new scenarios and provide a final diagnostic conclusion."
  ]
}

```
