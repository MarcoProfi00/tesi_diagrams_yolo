# Pipeline 2.0 - agente diagnostico autonomo controllato

Sei il controller diagnostico di una pipeline Graph JSON -> SPICE/ngspice.
Devi scegliere il prossimo test controllato oppure fermarti con una conclusione.

## Sintomo utente
La batteria è presente ma non eroga corrente e il circuito non reagisce. Individua la causa ed esegui gli scenari necessari per verificare una correzione funzionante.

## Vincoli obbligatori
- Rispondi con un solo oggetto JSON valido, senza Markdown o testo esterno.
- Non inventare nodi, componenti, valori o risultati.
- Usa soltanto queste primitive: add_resistor_between_nodes, add_voltage_source_between_nodes, change_component_value, change_source_value, close_switch, connect_nodes, drive_node_voltage, feed_nodes_from_source_node, set_initial_node_voltage.
- Ogni scenario deve essere self-contained e partire dalla base run.
- Puoi proporre al massimo 2 scenari indipendenti.
- Budget residuo: 3 run scenario.
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
- Se una correzione e gia fallita e restano soltanto scenari duplicati oppure
  modifiche non sostenute dagli artefatti, fermati con `localized`,
  `partially_localized` o `inconclusive` e lascia `verified_correction` vuoto.
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
      "reason": "La base run mostra batteria ideale a 5 V ma corrente nulla, nodo N001 flottante e matrice singolare. Dalla netlist il polo negativo della batteria (N001) non ha un ritorno DC verso massa perché lo switch SENSE è aperto e il resto del ramo termina su Rresistor22_1 verso N004, anch'esso flottante. Serve un test controllato di correzione minima per verificare che chiudendo lo switch il circuito ottenga un percorso chiuso e la batteria eroghi corrente.",
      "scenarios": [
        {
          "title": "Chiudere lo switch SENSE per ripristinare il ritorno del negativo batteria",
          "hypothesis": "La causa del mancato funzionamento è il polo negativo della batteria isolato da massa a causa di switch25.1 aperto; chiudendo lo switch N001 viene riferito a 0 V, la batteria alimenta N002 e compare corrente nel ramo resistivo.",
          "intent": "correction",
          "analysis": "op",
          "actions": [
            {
              "type": "close_switch",
              "target": "switch25.1"
            }
          ],
          "compare": [
            "v(N001)",
            "v(N002)",
            "v(N004)",
            "i(Vbattery2_1)",
            "i(Rresistor22_1)"
          ],
          "expect": {
            "v(N004)": "nonzero",
            "i(Vbattery2_1)": "nonzero",
            "i(Rresistor22_1)": "nonzero"
          }
        }
      ]
    },
    "prompt_path": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\chat_agent_evaluation\\web\\agent\\a02\\experiment_chat\\autonomous_prompt_1.md",
    "response_paths": [
      "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\chat_agent_evaluation\\web\\agent\\a02\\experiment_chat\\autonomous_response_1_attempt_1.txt"
    ],
    "scenario_results": [
      {
        "scenario_id": "agent_scenario_1",
        "scenario_dir": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\chat_agent_evaluation\\web\\agent\\a02\\scenarios\\agent_scenario_1",
        "run_dir": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\chat_agent_evaluation\\web\\agent\\a02\\scenarios\\agent_scenario_1\\run",
        "status": "spice_success",
        "spice_executed": true,
        "spice_status": "success",
        "spice_exit_code": 0,
        "comparison_summary": {
          "requested_count": 5,
          "changed_count": 0,
          "activated_count": 0,
          "missing_count": 0,
          "expected_count": 3,
          "expectations_met_count": 0,
          "expectations_failed_count": 3,
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
          "min_gain_ratio": null
        },
        "diagnostic_outcome": {
          "status": "not_resolved",
          "technical_label": "Not resolved",
          "label": "Criteri di successo non soddisfatti",
          "reason": "Nessuno dei comportamenti attesi dichiarati dallo scenario e stato verificato.",
          "user_message": "Lo scenario non ha prodotto un cambiamento utile rispetto alla base.",
          "stop_automation": false,
          "confidence": "low",
          "next_step": "Puo avere senso un altro scenario, oppure una conclusione diagnostica piu mirata."
        },
        "viewer": {
          "model": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\chat_agent_evaluation\\web\\agent\\a02\\scenarios\\agent_scenario_1\\run\\13_viewer_model.json",
          "layout": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\chat_agent_evaluation\\web\\agent\\a02\\scenarios\\agent_scenario_1\\run\\14_viewer_layout.json",
          "svg": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\chat_agent_evaluation\\web\\agent\\a02\\scenarios\\agent_scenario_1\\run\\15_viewer.svg"
        },
        "viewer_error": null,
        "executed_scenarios_count": 1
      }
    ]
  },
  {
    "decision_number": 2,
    "decision": {
      "decision": "run_scenarios",
      "reason": "La base run e lo scenario gia eseguito mostrano che chiudere switch25.1 non cambia nulla: N001 resta a 0 V, N002 a 5 V, i(Vbattery2_1)=0 e i(Rresistor22_1)=0. Quindi il problema non e il ritorno del negativo batteria, ma l'assenza di un carico/ritorno chiuso sul lato positivo: N004 e N003 sono reti separate del connettore e nessuna delle due richiude il circuito verso N002 o massa in DC. Serve un test controllato che verifichi la correzione minima sostenuta dagli artefatti, cioe collegare il ramo resistivo al nodo di alimentazione del connettore per creare un anello reale batteria-resistenza-batteria.",
      "scenarios": [
        {
          "title": "Collegare N004 a N002 per chiudere il ramo di carico della batteria",
          "hypothesis": "Il connettore rappresenta reti distinte e il carico resistivo su N004 non e attualmente collegato al positivo batteria su N002; creando la continuita mancante tra questi due nodi il circuito si chiude come anello Vbattery2_1 -> Rresistor22_1 -> Vbattery2_1 e la batteria deve finalmente erogare corrente.",
          "intent": "correction",
          "analysis": "op",
          "actions": [
            {
              "type": "connect_nodes",
              "from": "N004",
              "to": "N002"
            },
            {
              "type": "close_switch",
              "target": "switch25.1"
            }
          ],
          "compare": [
            "v(N001)",
            "v(N002)",
            "v(N004)",
            "i(Vbattery2_1)",
            "i(Rresistor22_1)"
          ],
          "expect": {
            "v(N004)": "changed",
            "i(Vbattery2_1)": "nonzero",
            "i(Rresistor22_1)": "nonzero"
          }
        }
      ]
    },
    "prompt_path": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\chat_agent_evaluation\\web\\agent\\a02\\experiment_chat\\autonomous_prompt_2.md",
    "response_paths": [
      "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\chat_agent_evaluation\\web\\agent\\a02\\experiment_chat\\autonomous_response_2_attempt_1.txt"
    ],
    "scenario_results": [
      {
        "scenario_id": "agent_scenario_2",
        "scenario_dir": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\chat_agent_evaluation\\web\\agent\\a02\\scenarios\\agent_scenario_2",
        "run_dir": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\chat_agent_evaluation\\web\\agent\\a02\\scenarios\\agent_scenario_2\\run",
        "status": "spice_success",
        "spice_executed": true,
        "spice_status": "success",
        "spice_exit_code": 0,
        "comparison_summary": {
          "requested_count": 5,
          "changed_count": 3,
          "activated_count": 3,
          "missing_count": 0,
          "expected_count": 3,
          "expectations_met_count": 3,
          "expectations_failed_count": 0,
          "expectations_missing_count": 0,
          "meaningful_improvement_count": 2,
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
          "min_gain_ratio": null
        },
        "diagnostic_outcome": {
          "status": "resolved_candidate",
          "technical_label": "Candidate resolved",
          "label": "Criteri di successo soddisfatti",
          "reason": "Tutti i comportamenti attesi dichiarati dallo scenario sono verificati dagli output SPICE.",
          "user_message": "Lo scenario fornisce una conferma forte dell'ipotesi testata.",
          "stop_automation": true,
          "confidence": "medium",
          "next_step": "Ci sono gia evidenze forti per fermarsi qui e passare alla conclusione diagnostica."
        },
        "viewer": {
          "model": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\chat_agent_evaluation\\web\\agent\\a02\\scenarios\\agent_scenario_2\\run\\13_viewer_model.json",
          "layout": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\chat_agent_evaluation\\web\\agent\\a02\\scenarios\\agent_scenario_2\\run\\14_viewer_layout.json",
          "svg": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\outputs\\demo_workspaces\\chat_agent_evaluation\\web\\agent\\a02\\scenarios\\agent_scenario_2\\run\\15_viewer.svg"
        },
        "viewer_error": null,
        "executed_scenarios_count": 2
      }
    ]
  }
]
```

## Evidenze tecniche correnti
## 03_node_map.json
```text
{
  "circuit_id": "a02",
  "source_format": "pipeline2.0_node_map",
  "nodes": [
    {
      "node_id": "0",
      "kind": "ground",
      "terminals": [
        "capacitor4.1_t2",
        "connector5.1_pin4",
        "gnd9.1_t1",
        "gnd9.2_t1",
        "gnd9.3_t1",
        "switch25.1_t2"
      ],
      "terminal_count": 6,
      "source_groups": [
        [
          "capacitor4.1_t2",
          "gnd9.2_t1"
        ],
        [
          "connector5.1_pin4",
          "gnd9.1_t1"
        ],
        [
          "gnd9.3_t1",
          "switch25.1_t2"
        ]
      ]
    },
    {
      "node_id": "N001",
      "kind": "normal",
      "terminals": [
        "battery2.1_negative",
        "resistor22.1_t1",
        "switch25.1_t1"
      ],
      "terminal_count": 3
    },
    {
      "node_id": "N002",
      "kind": "normal",
      "terminals": [
        "battery2.1_positive",
        "connector5.1_pin1"
      ],
      "terminal_count": 2
    },
    {
      "node_id": "N003",
      "kind": "normal",
      "terminals": [
        "capacitor4.1_t1",
        "connector5.1_pin3"
      ],
      "terminal_count": 2
    },
    {
      "node_id": "N004",
      "kind": "normal",
      "terminals": [
        "connector5.1_pin2",
        "resistor22.1_t2"
      ],
      "terminal_count": 2
    }
  ],
  "terminal_to_node": {
    "battery2.1_negative": "N001",
    "battery2.1_positive": "N002",
    "capacitor4.1_t1": "N003",
    "capacitor4.1_t2": "0",
    "connector5.1_pin1": "N002",
    "connector5.1_pin2": "N004",
    "connector5.1_pin3": "N003",
    "connector5.1_pin4": "0",
    "gnd9.1_t1": "0",
    "gnd9.2_t1": "0",
    "gnd9.3_t1": "0",
    "resistor22.1_t1": "N001",
    "resistor22.1_t2": "N004",
    "switch25.1_t1": "N001",
    "switch25.1_t2": "0"
  },
  "component_terminal_nodes": {
    "battery2.1": {
      "negative": "N001",
      "positive": "N002"
    },
    "capacitor4.1": {
      "t1": "N003",
      "t2": "0"
    },
    "connector5.1": {
      "pin1": "N002",
      "pin2": "N004",
      "pin3": "N003",
      "pin4": "0"
    },
    "gnd9.1": {
      "t1": "0"
    },
    "gnd9.2": {
      "t1": "0"
    },
    "gnd9.3": {
      "t1": "0"
    },
    "resistor22.1": {
      "t1": "N001",
      "t2": "N004"
    },
    "switch25.1": {
      "t1": "N001",
      "t2": "0"
    }
  },
  "warnings": {
    "ground_groups_count": 3,
    "multiple_ground_groups_merged_as_node_0": true,
    "singleton_nodes": [],
    "original_warnings": {
      "unconnected_terminals": [],
      "unmatched_terminals": [],
      "suspicious_matches": []
    },
    "normalization_warnings": []
  },
  "stats": {
    "nodes_count": 5,
    "normal_nodes_count": 4,
    "ground_nodes_count": 1,
    "ground_groups_count": 3,
    "terminal_to_node_count": 15,
    "singleton_nodes_count": 0
  }
}

```

## 06_component_rules.json
```text
{
  "circuit_id": "a02",
  "source_format": "pipeline2.0_component_rules",
  "values_source": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\data\\batchPipeline2.0\\batchChatAgentEvaluation\\values\\a02_values.yaml",
  "spice_classes_source": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\metadata\\pipeline2_spice_classes.yaml",
  "supplies": {},
  "components": {
    "battery2.1": {
      "class_name": "Battery",
      "status": "spice_ready",
      "spice_support": "direct",
      "spice_prefix": "V",
      "emit_as": "independent_voltage_source",
      "node_order": [
        "positive",
        "negative"
      ],
      "nodes": [
        "N002",
        "N001"
      ],
      "parameters": {
        "type": "dc",
        "value": 5,
        "unit": "V",
        "source": "manual_from_vcc_label",
        "label_text": "VCC +5 V DC"
      }
    },
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
        "N003",
        "0"
      ],
      "parameters": {
        "value": 100,
        "unit": "nF",
        "source": "manual_from_image_label",
        "label_text": "100nF"
      }
    },
    "connector5.1": {
      "class_name": "Connector",
      "status": "not_emitted",
      "spice_support": "structural",
      "reason": "Connector used for nodes, labels, and external interfaces."
    },
    "gnd9.1": {
      "class_name": "GND",
      "status": "not_emitted",
      "spice_support": "structural",
      "reason": "GND terminals are already mapped to SPICE node 0."
    },
    "gnd9.2": {
      "class_name": "GND",
      "status": "not_emitted",
      "spice_support": "structural",
      "reason": "GND terminals are already mapped to SPICE node 0."
    },
    "gnd9.3": {
      "class_name": "GND",
      "status": "not_emitted",
      "spice_support": "structural",
      "reason": "GND terminals are already mapped to SPICE node 0."
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
        "N001",
        "N004"
      ],
      "parameters": {
        "value": 10000,
        "unit": "ohm",
        "source": "manual_from_image_label",
        "label_text": "10k"
      }
    },
    "switch25.1": {
      "class_name": "Switch",
      "status": "spice_ready",
      "spice_support": "simplified",
      "spice_prefix": null,
      "emit_as": null,
      "node_order": [
        "t1",
        "t2"
      ],
      "nodes": [
        "N001",
        "0"
      ],
      "parameters": {
        "state": "open",
        "state_source": "graph_json_state",
        "state_confidence": 0.95,
        "source": "graph_json_state",
        "label_text": "SENSE"
      },
      "strategy": "open_circuit"
    }
  },
  "simulation": {},
  "stats": {
    "components_total": 8,
    "spice_ready_components": 4,
    "not_emitted_components": 4,
    "measurement_components": 0,
    "missing_components": 0,
    "unsupported_components": 0,
    "pin_aware_components": 0,
    "invalid_components": 0,
    "supplies_ready_count": 0
  }
}

```

## 07_netlist.cir
```text
* pipeline2.0 netlist
* circuit: a02

Vbattery2_1 N002 N001 DC 5
Ccapacitor4_1 N003 0 100n
Rresistor22_1 N001 N004 10000
* switch25.1 open: not emitted

.op
.end

```

## 07_spice_emit_report.json
```text
{
  "circuit_id": "a02",
  "source_format": "pipeline2.0_spice_emit_report",
  "emitted_elements": 3,
  "skipped_elements": 4,
  "skipped_components": [
    "connector5.1",
    "gnd9.1",
    "gnd9.2",
    "gnd9.3"
  ],
  "informational_skips": [
    "connector5.1: structural component not emitted",
    "gnd9.1: structural component not emitted",
    "gnd9.2: structural component not emitted",
    "gnd9.3: structural component not emitted"
  ],
  "measurement_points": [],
  "analyses": [
    "op"
  ],
  "transient_export": {
    "path": null,
    "nodes": [],
    "device_currents": []
  },
  "models": [],
  "warnings": [
    "switch25.1: open switch not emitted"
  ]
}

```

## 08_ngspice_stdout.txt
```text

Note: No compatibility mode selected!


Circuit: * pipeline2.0 netlist

Doing analysis at TEMP = 27.000000 and TNOM = 27.000000

Using SPARSE 1.3 as Direct Linear Solver

No. of Data Rows : 1
	Node                                  Voltage
	----                                  -------
	----	-------
	n004                             0.000000e+00
	n003                             0.000000e+00
	n001                             0.000000e+00
	n002                             5.000000e+00

	Source	Current
	------	-------

	vbattery2_1#branch               0.000000e+00

 Capacitor models (Fixed capacitor)
      model                     C

        cap                     0
         cj                     0
       cjsw                     0
       defw                 1e-05
       defl                     0
     narrow                     0
      short                     0
        del                     0
        tc1                     0
        tc2                     0
         di                     0
      thick                     0
     bv_max                 1e+99

 Resistor models (Simple linear resistor)
      model                     R

        rsh                     0
     narrow                     0
      short                     0
        tc1                     0
        tc2                     0
        tce                     0
       defw                 1e-05
          l                 1e-05
         kf                     0
         af                     0
          r                     0
     bv_max                 1e+99
         lf                     1
         wf                     1
         ef                     1

 Capacitor: Fixed capacitor
     device         ccapacitor4_1
      model                     C
capacitance                 1e-07
      dtemp                     0
     bv_max                 1e+99
          i                     0
          p                     0

 Resistor: Simple linear resistor
     device         rresistor22_1
      model                     R
 resistance                 10000
         ac                 10000
      dtemp                     0
     bv_max                 1e+99
      noisy                     1
          i                     0
          p                     0

 Vsource: Independent voltage source
     device           vbattery2_1
         dc                     5
      acmag                     0
      pulse         -
        sin         -
        exp         -
        pwl         -
       sffm         -
         am         -
    trnoise         -
   trrandom         -
    portnum                     0
         z0                     0
        pwr                     0
       freq                     0
      phase                     0
          i                     0
          p                     0


Total analysis time (seconds) = 0.0029938

Total elapsed time (seconds) = 0.133 

Total DRAM available = 32239.535 MB.
DRAM currently available = 15874.543 MB.
Maximum ngspice program size =   14.938 MB.
Current ngspice program size =   14.938 MB.


```

## 08_ngspice_stderr.txt
```text
Warning: singular matrix:  check node n001

Note: Starting dynamic gmin stepping
Warning: singular matrix:  check node n001

Warning: Dynamic gmin stepping failed
Note: Starting true gmin stepping
Warning: singular matrix:  check node n001

Warning: singular matrix:  check node n001

Warning: singular matrix:  check node n001

Warning: singular matrix:  check node n001

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
  "batch_name": "batchChatAgentEvaluation",
  "experiment_name": "chat_agent_evaluation",
  "circuit_id": "a02",
  "user_problem": "La batteria è presente ma non eroga corrente e il circuito non reagisce. Individua la causa ed esegui gli scenari necessari per verificare una correzione funzionante.",
  "pipeline2_output_dir": "outputs\\demo_workspaces\\chat_agent_evaluation\\web\\agent\\a02",
  "summary": {
    "spice_status": "success",
    "spice_exit_code": 0,
    "spice_message": "ngspice completed successfully.",
    "emitted_elements": 3,
    "skipped_elements": 4,
    "emit_warnings_count": 1,
    "skipped_components_count": 4,
    "node_count": 5,
    "ground_groups_count": 3,
    "singleton_nodes_count": 0,
    "bound_components": 4,
    "missing_components": 0,
    "unsupported_components": 0,
    "spice_ready_components": 4,
    "rules_missing_components": 0,
    "has_tran_csv": false,
    "has_tran_plot": false,
    "led_profiles": {}
  },
  "artifacts": {
    "graph": {
      "step": "01",
      "available": true,
      "path": "outputs\\demo_workspaces\\chat_agent_evaluation\\web\\agent\\a02\\01_graph.json",
      "role": "Graph JSON copied from Pipeline 1.0."
    },
    "normalized_circuit": {
      "step": "02",
      "available": true,
      "path": "outputs\\demo_workspaces\\chat_agent_evaluation\\web\\agent\\a02\\02_normalized_circuit.json",
      "role": "Normalized circuit representation used by Pipeline 2.0."
    },
    "node_map": {
      "step": "03",
      "available": true,
      "path": "outputs\\demo_workspaces\\chat_agent_evaluation\\web\\agent\\a02\\03_node_map.json",
      "role": "Maps component terminals to SPICE node names."
    },
    "values_bound": {
      "step": "04",
      "available": true,
      "path": "outputs\\demo_workspaces\\chat_agent_evaluation\\web\\agent\\a02\\04_values_bound.json",
      "role": "Values and labels bound to graph components."
    },
    "component_rules": {
      "step": "06",
      "available": true,
      "path": "outputs\\demo_workspaces\\chat_agent_evaluation\\web\\agent\\a02\\06_component_rules.json",
      "role": "SPICE conversion rules for each component."
    },
    "netlist": {
      "step": "07",
      "available": true,
      "path": "outputs\\demo_workspaces\\chat_agent_evaluation\\web\\agent\\a02\\07_netlist.cir",
      "role": "Generated SPICE netlist."
    },
    "spice_emit_report": {
      "step": "07",
      "available": true,
      "path": "outputs\\demo_workspaces\\chat_agent_evaluation\\web\\agent\\a02\\07_spice_emit_report.json",
      "role": "Report of emitted, skipped and warning components."
    },
    "spice_run": {
      "step": "08",
      "available": true,
      "path": "outputs\\demo_workspaces\\chat_agent_evaluation\\web\\agent\\a02\\08_spice_run.json",
      "role": "Structured ngspice execution report."
    },
    "ngspice_stdout": {
      "step": "08",
      "available": true,
      "path": "outputs\\demo_workspaces\\chat_agent_evaluation\\web\\agent\\a02\\08_ngspice_stdout.txt",
      "role": "Raw ngspice stdout log."
    },
    "ngspice_stderr": {
      "step": "08",
      "available": true,
      "path": "outputs\\demo_workspaces\\chat_agent_evaluation\\web\\agent\\a02\\08_ngspice_stderr.txt",
      "role": "Raw ngspice stderr log."
    },
    "tran_csv": {
      "step": "08",
      "available": false,
      "path": null,
      "role": "Clean transient CSV, when .tran data is available."
    },
    "tran_plot_png": {
      "step": "08",
      "available": false,
      "path": null,
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
      "scenario_dir": "outputs\\demo_workspaces\\chat_agent_evaluation\\web\\agent\\a02\\scenarios\\agent_scenario_1",
      "scenario_id": "agent_scenario_1",
      "title": "Chiudere lo switch SENSE per ripristinare il ritorno del negativo batteria",
      "status": "spice_success",
      "spice_status": "success",
      "diagnostic_outcome": {
        "status": "not_resolved",
        "technical_label": "Not resolved",
        "label": "Criteri di successo non soddisfatti",
        "reason": "Nessuno dei comportamenti attesi dichiarati dallo scenario e stato verificato.",
        "user_message": "Lo scenario non ha prodotto un cambiamento utile rispetto alla base.",
        "stop_automation": false,
        "confidence": "low",
        "next_step": "Puo avere senso un altro scenario, oppure una conclusione diagnostica piu mirata."
      },
      "comparison_summary": {
        "requested_count": 5,
        "changed_count": 0,
        "activated_count": 0,
        "missing_count": 0,
        "expected_count": 3,
        "expectations_met_count": 0,
        "expectations_failed_count": 3,
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
        "min_gain_ratio": null
      },
      "led_profiles": {},
      "artifacts": {
        "scenario_definition": {
          "available": true,
          "path": "outputs\\demo_workspaces\\chat_agent_evaluation\\web\\agent\\a02\\scenarios\\agent_scenario_1\\scenario.json",
          "role": "Scenario selected by the user and saved before execution."
        },
        "scenario_status": {
          "available": true,
          "path": "outputs\\demo_workspaces\\chat_agent_evaluation\\web\\agent\\a02\\scenarios\\agent_scenario_1\\scenario_status.json",
          "role": "Current scenario status, SPICE status and diagnostic outcome."
        },
        "controlled_scenario_report": {
          "available": true,
          "path": "outputs\\demo_workspaces\\chat_agent_evaluation\\web\\agent\\a02\\scenarios\\agent_scenario_1\\12_controlled_scenarios.json",
          "role": "Report produced by the controlled scenario runner."
        },
        "scenario_comparison": {
          "available": true,
          "path": "outputs\\demo_workspaces\\chat_agent_evaluation\\web\\agent\\a02\\scenarios\\agent_scenario_1\\scenario_comparison.json",
          "role": "Base-vs-scenario comparison used to evaluate the scenario."
        }
      }
    },
    {
      "scenario_dir": "outputs\\demo_workspaces\\chat_agent_evaluation\\web\\agent\\a02\\scenarios\\agent_scenario_2",
      "scenario_id": "agent_scenario_2",
      "title": "Collegare N004 a N002 per chiudere il ramo di carico della batteria",
      "status": "spice_success",
      "spice_status": "success",
      "diagnostic_outcome": {
        "status": "resolved_candidate",
        "technical_label": "Candidate resolved",
        "label": "Criteri di successo soddisfatti",
        "reason": "Tutti i comportamenti attesi dichiarati dallo scenario sono verificati dagli output SPICE.",
        "user_message": "Lo scenario fornisce una conferma forte dell'ipotesi testata.",
        "stop_automation": true,
        "confidence": "medium",
        "next_step": "Ci sono gia evidenze forti per fermarsi qui e passare alla conclusione diagnostica."
      },
      "comparison_summary": {
        "requested_count": 5,
        "changed_count": 3,
        "activated_count": 3,
        "missing_count": 0,
        "expected_count": 3,
        "expectations_met_count": 3,
        "expectations_failed_count": 0,
        "expectations_missing_count": 0,
        "meaningful_improvement_count": 2,
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
        "min_gain_ratio": null
      },
      "led_profiles": {},
      "artifacts": {
        "scenario_definition": {
          "available": true,
          "path": "outputs\\demo_workspaces\\chat_agent_evaluation\\web\\agent\\a02\\scenarios\\agent_scenario_2\\scenario.json",
          "role": "Scenario selected by the user and saved before execution."
        },
        "scenario_status": {
          "available": true,
          "path": "outputs\\demo_workspaces\\chat_agent_evaluation\\web\\agent\\a02\\scenarios\\agent_scenario_2\\scenario_status.json",
          "role": "Current scenario status, SPICE status and diagnostic outcome."
        },
        "controlled_scenario_report": {
          "available": true,
          "path": "outputs\\demo_workspaces\\chat_agent_evaluation\\web\\agent\\a02\\scenarios\\agent_scenario_2\\12_controlled_scenarios.json",
          "role": "Report produced by the controlled scenario runner."
        },
        "scenario_comparison": {
          "available": true,
          "path": "outputs\\demo_workspaces\\chat_agent_evaluation\\web\\agent\\a02\\scenarios\\agent_scenario_2\\scenario_comparison.json",
          "role": "Base-vs-scenario comparison used to evaluate the scenario."
        }
      }
    }
  ],
  "scenario_outcome_summary": {
    "available": true,
    "best_scenario_id": "agent_scenario_2",
    "best_outcome_status": "resolved_candidate",
    "best_stop_automation": true,
    "ranking_status": "verified_best",
    "interpretation_rule": "If a user asks which scenario resolves the problem, prefer the scenario with outcome_status='resolved_candidate' and stop_automation=true. Partially resolved scenarios without verified expectations are supporting diagnostics and must not be ranked only by changed_count.",
    "scenarios": [
      {
        "scenario_id": "agent_scenario_1",
        "title": "Chiudere lo switch SENSE per ripristinare il ritorno del negativo batteria",
        "status": "spice_success",
        "spice_status": "success",
        "outcome_status": "not_resolved",
        "outcome_label": "Criteri di successo non soddisfatti",
        "outcome_technical_label": "Not resolved",
        "outcome_reason": "Nessuno dei comportamenti attesi dichiarati dallo scenario e stato verificato.",
        "stop_automation": false,
        "comparison_summary": {
          "requested_count": 5,
          "changed_count": 0,
          "activated_count": 0,
          "missing_count": 0,
          "expected_count": 3,
          "expectations_met_count": 0,
          "expectations_failed_count": 3,
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
          "min_gain_ratio": null
        },
        "quantity_summary": {
          "changed": [],
          "unchanged": [
            "v(N001)",
            "v(N002)",
            "v(N004)",
            "i(Vbattery2_1)",
            "i(Rresistor22_1)"
          ],
          "missing": []
        },
        "led_profiles": {},
        "ranking_verified": false,
        "score": 0
      },
      {
        "scenario_id": "agent_scenario_2",
        "title": "Collegare N004 a N002 per chiudere il ramo di carico della batteria",
        "status": "spice_success",
        "spice_status": "success",
        "outcome_status": "resolved_candidate",
        "outcome_label": "Criteri di successo soddisfatti",
        "outcome_technical_label": "Candidate resolved",
        "outcome_reason": "Tutti i comportamenti attesi dichiarati dallo scenario sono verificati dagli output SPICE.",
        "stop_automation": true,
        "comparison_summary": {
          "requested_count": 5,
          "changed_count": 3,
          "activated_count": 3,
          "missing_count": 0,
          "expected_count": 3,
          "expectations_met_count": 3,
          "expectations_failed_count": 0,
          "expectations_missing_count": 0,
          "meaningful_improvement_count": 2,
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
          "min_gain_ratio": null
        },
        "quantity_summary": {
          "changed": [
            "v(N004)",
            "i(Vbattery2_1)",
            "i(Rresistor22_1)"
          ],
          "unchanged": [
            "v(N001)",
            "v(N002)"
          ],
          "missing": []
        },
        "led_profiles": {},
        "ranking_verified": true,
        "score": 215
      }
    ]
  },
  "scenario_budget": {
    "max_executable_scenarios": 5,
    "executed_scenarios_count": 2,
    "remaining_executable_scenarios": 3,
    "budget_exhausted": false,
    "last_scenario_available": false,
    "policy": "At most 5 scenarios can be executed for the same circuit. When only one scenario remains, the agent should propose a single final scenario. When no scenario remains, the agent must stop proposing new scenarios and provide a final diagnostic conclusion."
  },
  "image_access": {
    "included_by_default": false,
    "can_be_requested": true,
    "path": "outputs\\demo_workspaces\\chat_agent_evaluation\\input\\images\\a02.png",
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
