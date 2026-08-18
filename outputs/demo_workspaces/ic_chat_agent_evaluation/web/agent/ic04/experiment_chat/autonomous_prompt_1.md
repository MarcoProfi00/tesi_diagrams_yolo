# Pipeline 2.0 - agente diagnostico autonomo controllato

Sei il controller diagnostico di una pipeline Graph JSON -> SPICE/ngspice.
Devi scegliere il prossimo test controllato oppure fermarti con una conclusione.

## Sintomo utente
La sirena suona, ma sembra emettere quasi sempre lo stesso tono. Cosa posso controllare per rendere più evidente il cambio di suono?

## Politica temporale della sessione
{}

## Vincoli obbligatori
- Rispondi con un solo oggetto JSON valido, senza Markdown o testo esterno.
- Non inventare nodi, componenti, valori o risultati.
- Usa soltanto queste primitive: add_resistor_between_nodes, add_voltage_source_between_nodes, change_component_value, change_source_value, close_switch, connect_nodes, drive_node_voltage, feed_nodes_from_source_node, set_initial_node_voltage.
- Ogni scenario deve essere self-contained e partire dalla base run.
- Puoi proporre al massimo 2 scenari indipendenti.
- Budget residuo: 5 run scenario.
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
- La politica temporale della sessione e' derivata una sola volta dal sintomo.
  Ogni scenario con intent="correction" deve usarla senza aggiungere, rimuovere
  o rilassare soglie. Gli scenari diagnostici non costituiscono una correzione.
- Rispetta alla lettera i vincoli negativi della richiesta. Se l'utente chiede di
  non modificare il segnale o la sorgente di ingresso, non usare
  `change_source_value`, `drive_node_voltage` o `add_voltage_source_between_nodes`,
  neppure su un nodo interno del percorso del segnale.
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
- Per sintomi di amplificazione, volume basso, propagazione o attenuazione di un
  segnale, **ogni scenario**, sia `correction` sia `diagnostic`, deve includere
  `gain: {"input":"v(NODO_IN)","output":"v(NODO_OUT)","min_ratio": NUMERO_POSITIVO}`.
  Entrambe le tensioni devono essere presenti in compare e possono anche usare la
  forma differenziale `v(NODO1,NODO2)`. `min_ratio` e' obbligatorio: scegli una
  soglia positiva motivata dall'obiettivo dello scenario. Valuta il guadagno come
  Vpp(output) / Vpp(input), senza confondere due nodi entrambi di uscita. Non usare
  il solo `changed` per concludere che un segnale non nullo ma trascurabile arrivi
  utilmente all'uscita.
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
- Prima di localizzare un'attenuazione su un tratto del circuito, confronta le
  ampiezze base ai suoi estremi: un rapporto gia prossimo all'unita non sostiene
  l'ipotesi di un collo di bottiglia significativo su quel tratto.
- Distingui sempre `expectations_met_count` da `meaningful_improvement_count`:
  una direzione corretta ma sotto la soglia relativa non verifica una correzione.
  Non riutilizzare in una correzione combinata un'azione che, provata da sola,
  non ha prodotto un miglioramento significativo, salvo che sia indispensabile
  per un altro vincolo esplicito e misurato.
- Per sintomi di distorsione, clipping, saturazione o segnale poco pulito,
  ogni scenario transitorio deve dichiarare quality="thd" e il blocco gain
  deve identificare ingresso e uscita.
- Usa `quality="thd"` soltanto quando il sintomo o un vincolo utente riguarda
  distorsione, clipping, saturazione o qualita del segnale. Non aggiungerla come
  requisito precauzionale a scenari che perseguono un obiettivo diverso.
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
  `min_duty_cycle` opzionale tra 0 e 1, `min_relative_duty_increase` opzionale,
  `max_frequency_hz` opzionale positivo e `min_relative_period_increase` opzionale.
- Scegli soglie coerenti con il sintomo: per esempio un lampeggio chiaramente visibile
  puo richiedere stato `blinking`, periodicita regolare e un duty cycle minimo.
  Un lampeggio troppo rapido richiede anche una frequenza massima oppure un aumento
  relativo minimo del periodo, espresso come frazione (`0.5` significa +50%, non
  `1.5`); una variazione generica della forma d'onda non basta.
  Se un test aumenta il duty cycle ma perde la periodicita richiesta, non e risolutivo.
- Usa `temporal_expect` soltanto per il comportamento temporale di un carico
  luminoso o pulsante richiesto dal sintomo e realmente presente in
  `temporal_profiles`. Un normale diodo non e un indicatore luminoso: la sua
  conduzione periodica non dimostra lampeggio, modulazione audio o qualita del suono.
- Se il sintomo riguarda un tono quasi costante o una modulazione audio poco
  evidente, non usare il profilo temporale di LED, diodi o lampade come criterio
  di successo. Confronta in TRAN l'escursione del nodo che controlla la
  modulazione e la tensione differenziale sul carico audio. Una correzione deve
  rafforzare la variazione di controllo senza spegnere o degradare l'uscita.
- Per una resistenza in serie tra un oscillatore modulante e un nodo di controllo,
  non assumere che aumentare la resistenza rafforzi o rallenti la modulazione:
  deduci la direzione dalle connessioni e verifica `tran_vpp` prima di concludere.
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
- La final_answer di uno stato resolved deve riferire esplicitamente la stessa
  modifica e le misure riportate in verified_correction; non fermarti a una
  raccomandazione generica sul gruppo di componenti.
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
[]
```

## Evidenze tecniche correnti
## 03_node_map.json
```text
{
  "circuit_id": "ic04",
  "source_format": "pipeline2.0_node_map",
  "nodes": [
    {
      "node_id": "0",
      "kind": "ground",
      "terminals": [
        "gnd9.1_t1",
        "integrated_circuit11.1_bottom_1",
        "integrated_circuit11.2_bottom_1",
        "polarized_capacitor20.1_negative",
        "polarized_capacitor20.2_negative",
        "polarized_capacitor20.3_negative",
        "speaker24.1_t2"
      ],
      "terminal_count": 7,
      "source_groups": [
        [
          "gnd9.1_t1",
          "integrated_circuit11.1_bottom_1",
          "integrated_circuit11.2_bottom_1",
          "polarized_capacitor20.1_negative",
          "polarized_capacitor20.2_negative",
          "polarized_capacitor20.3_negative",
          "speaker24.1_t2"
        ]
      ]
    },
    {
      "node_id": "N001",
      "kind": "normal",
      "terminals": [
        "integrated_circuit11.1_bottom_2",
        "polarized_capacitor20.2_positive"
      ],
      "terminal_count": 2
    },
    {
      "node_id": "N002",
      "kind": "normal",
      "terminals": [
        "integrated_circuit11.1_left_1",
        "led12.1_anode",
        "resistor22.1_t1",
        "resistor22.2_t2"
      ],
      "terminal_count": 4
    },
    {
      "node_id": "N003",
      "kind": "normal",
      "terminals": [
        "integrated_circuit11.1_left_2",
        "integrated_circuit11.1_left_3",
        "led12.1_cathode",
        "polarized_capacitor20.1_positive",
        "resistor22.1_t2"
      ],
      "terminal_count": 5
    },
    {
      "node_id": "N004",
      "kind": "normal",
      "terminals": [
        "integrated_circuit11.1_right_1",
        "resistor22.3_t1"
      ],
      "terminal_count": 2
    },
    {
      "node_id": "N005",
      "kind": "normal",
      "terminals": [
        "integrated_circuit11.1_top_1",
        "integrated_circuit11.1_top_2",
        "integrated_circuit11.2_top_1",
        "integrated_circuit11.2_top_2",
        "resistor22.2_t1",
        "resistor22.5_t1",
        "terminal26.1_t1"
      ],
      "terminal_count": 7
    },
    {
      "node_id": "N006",
      "kind": "normal",
      "terminals": [
        "integrated_circuit11.2_bottom_2",
        "resistor22.3_t2"
      ],
      "terminal_count": 2
    },
    {
      "node_id": "N007",
      "kind": "normal",
      "terminals": [
        "integrated_circuit11.2_left_1",
        "resistor22.4_t1",
        "resistor22.5_t2"
      ],
      "terminal_count": 3
    },
    {
      "node_id": "N008",
      "kind": "normal",
      "terminals": [
        "integrated_circuit11.2_left_2",
        "integrated_circuit11.2_left_3",
        "polarized_capacitor20.3_positive",
        "resistor22.4_t2"
      ],
      "terminal_count": 4
    },
    {
      "node_id": "N009",
      "kind": "normal",
      "terminals": [
        "integrated_circuit11.2_right_1",
        "polarized_capacitor20.4_positive"
      ],
      "terminal_count": 2
    },
    {
      "node_id": "N010",
      "kind": "normal",
      "terminals": [
        "polarized_capacitor20.4_negative",
        "speaker24.1_t1"
      ],
      "terminal_count": 2
    }
  ],
  "terminal_to_node": {
    "gnd9.1_t1": "0",
    "integrated_circuit11.1_bottom_1": "0",
    "integrated_circuit11.1_bottom_2": "N001",
    "integrated_circuit11.1_left_1": "N002",
    "integrated_circuit11.1_left_2": "N003",
    "integrated_circuit11.1_left_3": "N003",
    "integrated_circuit11.1_right_1": "N004",
    "integrated_circuit11.1_top_1": "N005",
    "integrated_circuit11.1_top_2": "N005",
    "integrated_circuit11.2_bottom_1": "0",
    "integrated_circuit11.2_bottom_2": "N006",
    "integrated_circuit11.2_left_1": "N007",
    "integrated_circuit11.2_left_2": "N008",
    "integrated_circuit11.2_left_3": "N008",
    "integrated_circuit11.2_right_1": "N009",
    "integrated_circuit11.2_top_1": "N005",
    "integrated_circuit11.2_top_2": "N005",
    "led12.1_anode": "N002",
    "led12.1_cathode": "N003",
    "polarized_capacitor20.1_negative": "0",
    "polarized_capacitor20.1_positive": "N003",
    "polarized_capacitor20.2_negative": "0",
    "polarized_capacitor20.2_positive": "N001",
    "polarized_capacitor20.3_negative": "0",
    "polarized_capacitor20.3_positive": "N008",
    "polarized_capacitor20.4_negative": "N010",
    "polarized_capacitor20.4_positive": "N009",
    "resistor22.1_t1": "N002",
    "resistor22.1_t2": "N003",
    "resistor22.2_t1": "N005",
    "resistor22.2_t2": "N002",
    "resistor22.3_t1": "N004",
    "resistor22.3_t2": "N006",
    "resistor22.4_t1": "N007",
    "resistor22.4_t2": "N008",
    "resistor22.5_t1": "N005",
    "resistor22.5_t2": "N007",
    "speaker24.1_t1": "N010",
    "speaker24.1_t2": "0",
    "terminal26.1_t1": "N005"
  },
  "component_terminal_nodes": {
    "gnd9.1": {
      "t1": "0"
    },
    "integrated_circuit11.1": {
      "left_1": "N002",
      "left_2": "N003",
      "left_3": "N003",
      "right_1": "N004",
      "top_1": "N005",
      "top_2": "N005",
      "bottom_1": "0",
      "bottom_2": "N001"
    },
    "integrated_circuit11.2": {
      "left_1": "N007",
      "left_2": "N008",
      "left_3": "N008",
      "right_1": "N009",
      "top_1": "N005",
      "top_2": "N005",
      "bottom_1": "0",
      "bottom_2": "N006"
    },
    "led12.1": {
      "anode": "N002",
      "cathode": "N003"
    },
    "polarized_capacitor20.1": {
      "positive": "N003",
      "negative": "0"
    },
    "polarized_capacitor20.2": {
      "positive": "N001",
      "negative": "0"
    },
    "polarized_capacitor20.3": {
      "positive": "N008",
      "negative": "0"
    },
    "polarized_capacitor20.4": {
      "positive": "N009",
      "negative": "N010"
    },
    "resistor22.1": {
      "t1": "N002",
      "t2": "N003"
    },
    "resistor22.2": {
      "t1": "N005",
      "t2": "N002"
    },
    "resistor22.3": {
      "t1": "N004",
      "t2": "N006"
    },
    "resistor22.4": {
      "t1": "N007",
      "t2": "N008"
    },
    "resistor22.5": {
      "t1": "N005",
      "t2": "N007"
    },
    "speaker24.1": {
      "t1": "N010",
      "t2": "0"
    },
    "terminal26.1": {
      "t1": "N005"
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
    "nodes_count": 11,
    "normal_nodes_count": 10,
    "ground_nodes_count": 1,
    "ground_groups_count": 1,
    "terminal_to_node_count": 40,
    "singleton_nodes_count": 0
  }
}

```

## 06_component_rules.json
```text
{
  "circuit_id": "ic04",
  "source_format": "pipeline2.0_component_rules",
  "values_source": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\data\\batchPipeline2.0\\batchICChatAgentEvaluation\\values\\ic04_values.yaml",
  "spice_classes_source": "C:\\Users\\m.profilo\\Desktop\\tesi_diagrams_yolo\\metadata\\pipeline2_spice_classes.yaml",
  "supplies": {
    "VCC_12": {
      "status": "spice_ready",
      "spice_prefix": "V",
      "emit_as": "independent_voltage_source",
      "nodes": [
        "N005",
        "0"
      ],
      "parameters": {
        "terminal": "terminal26.1_t1",
        "type": "dc",
        "value": 12,
        "unit": "V",
        "reference": 0,
        "source": "manual_from_image_label",
        "label_text": "+12 V DC",
        "viewer_override": {
          "visual_class": "voltage_source",
          "label": "VCC",
          "display_value": "+12 V"
        },
        "node": "N005"
      }
    }
  },
  "components": {
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
        "N003",
        "N001",
        "N003",
        "N005",
        "N004",
        "N002",
        "N005",
        "0"
      ],
      "parameters": {
        "model": "TLC555_6",
        "source": "ti_official_slfj002e_pspice_model",
        "label_text": "IC1 NE555; modello ufficiale TI TLC555_6 Rev. E",
        "viewer_override": {
          "label": "IC1",
          "display_value": "NE555",
          "tooltip": "NE555 simulato con il modello ufficiale TI TLC555_6 Rev. E SLFJ002E"
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
            "CONT": "integrated_circuit11.1_bottom_2",
            "TRIG": "integrated_circuit11.1_left_3",
            "RESET": "integrated_circuit11.1_top_1",
            "OUT": "integrated_circuit11.1_right_1",
            "DISC": "integrated_circuit11.1_left_1",
            "VCC": "integrated_circuit11.1_top_2",
            "GND": "integrated_circuit11.1_bottom_1"
          },
          "resolved_node_refs": {
            "THRES": "N003",
            "CONT": "N001",
            "TRIG": "N003",
            "RESET": "N005",
            "OUT": "N004",
            "DISC": "N002",
            "VCC": "N005",
            "GND": "0"
          }
        }
      },
      "reason": "Explicit YAML override emitted as a SPICE subcircuit."
    },
    "integrated_circuit11.2": {
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
        "N008",
        "N006",
        "N008",
        "N005",
        "N009",
        "N007",
        "N005",
        "0"
      ],
      "parameters": {
        "model": "TLC555_6",
        "source": "ti_official_slfj002e_pspice_model",
        "label_text": "Secondo NE555 (IC1 ripetuto nello schema); normalizzato a IC2",
        "viewer_override": {
          "label": "IC2",
          "display_value": "NE555",
          "tooltip": "Secondo NE555; modello ufficiale TI TLC555_6 Rev. E SLFJ002E"
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
            "THRES": "integrated_circuit11.2_left_2",
            "CONT": "integrated_circuit11.2_bottom_2",
            "TRIG": "integrated_circuit11.2_left_3",
            "RESET": "integrated_circuit11.2_top_1",
            "OUT": "integrated_circuit11.2_right_1",
            "DISC": "integrated_circuit11.2_left_1",
            "VCC": "integrated_circuit11.2_top_2",
            "GND": "integrated_circuit11.2_bottom_1"
          },
          "resolved_node_refs": {
            "THRES": "N008",
            "CONT": "N006",
            "TRIG": "N008",
            "RESET": "N005",
            "OUT": "N009",
            "DISC": "N007",
            "VCC": "N005",
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
        "N002",
        "N003"
      ],
      "parameters": {
        "model": "D_1N4001_TYP",
        "source": "manual_from_image_label_and_registered_typical_model",
        "label_text": "D1 1N4001",
        "viewer_override": {
          "visual_class": "diode",
          "label": "D1",
          "display_value": "1N4001",
          "tooltip": "Diodo 1N4001; modello tipico semplificato registrato per SPICE"
        }
      }
    },
    "polarized_capacitor20.1": {
      "class_name": "Polarized_Capacitor",
      "status": "spice_ready",
      "spice_support": "direct",
      "spice_prefix": "C",
      "emit_as": "capacitor",
      "node_order": [
        "positive",
        "negative"
      ],
      "nodes": [
        "N003",
        "0"
      ],
      "parameters": {
        "value": 10,
        "unit": "uf",
        "source": "manual_from_image_label",
        "label_text": "C1 10 uF polarizzato",
        "viewer_override": {
          "label": "C1",
          "display_value": "10 uF"
        }
      }
    },
    "polarized_capacitor20.2": {
      "class_name": "Polarized_Capacitor",
      "status": "spice_ready",
      "spice_support": "direct",
      "spice_prefix": "C",
      "emit_as": "capacitor",
      "node_order": [
        "positive",
        "negative"
      ],
      "nodes": [
        "N001",
        "0"
      ],
      "parameters": {
        "value": 10,
        "unit": "nf",
        "source": "manual_from_image_label",
        "label_text": "C2 10 nF polarizzato",
        "viewer_override": {
          "label": "C2",
          "display_value": "10 nF"
        }
      }
    },
    "polarized_capacitor20.3": {
      "class_name": "Polarized_Capacitor",
      "status": "spice_ready",
      "spice_support": "direct",
      "spice_prefix": "C",
      "emit_as": "capacitor",
      "node_order": [
        "positive",
        "negative"
      ],
      "nodes": [
        "N008",
        "0"
      ],
      "parameters": {
        "value": 100,
        "unit": "nf",
        "source": "manual_from_image_label",
        "label_text": "C3 100 nF polarizzato",
        "viewer_override": {
          "label": "C3",
          "display_value": "100 nF"
        }
      }
    },
    "polarized_capacitor20.4": {
      "class_name": "Polarized_Capacitor",
      "status": "spice_ready",
      "spice_support": "direct",
      "spice_prefix": "C",
      "emit_as": "capacitor",
      "node_order": [
        "positive",
        "negative"
      ],
      "nodes": [
        "N009",
        "N010"
      ],
      "parameters": {
        "value": 100,
        "unit": "uf",
        "source": "manual_from_image_label",
        "label_text": "C4 100 uF polarizzato",
        "viewer_override": {
          "label": "C4",
          "display_value": "100 uF"
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
        "N002",
        "N003"
      ],
      "parameters": {
        "value": 68,
        "unit": "kohm",
        "source": "manual_from_image_label",
        "label_text": "R2 68 kohm",
        "viewer_override": {
          "label": "R2",
          "display_value": "68 kohm"
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
        "N005",
        "N002"
      ],
      "parameters": {
        "value": 68,
        "unit": "kohm",
        "source": "manual_from_image_label",
        "label_text": "R1 68 kohm",
        "viewer_override": {
          "label": "R1",
          "display_value": "68 kohm"
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
        "N004",
        "N006"
      ],
      "parameters": {
        "value": 10,
        "unit": "kohm",
        "source": "manual_from_image_label",
        "label_text": "R5 10 kohm",
        "viewer_override": {
          "label": "R5",
          "display_value": "10 kohm"
        }
      }
    },
    "resistor22.4": {
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
        "N007",
        "N008"
      ],
      "parameters": {
        "value": 8.2,
        "unit": "kohm",
        "source": "manual_from_image_label",
        "label_text": "R4 8.2 kohm",
        "viewer_override": {
          "label": "R4",
          "display_value": "8.2 kohm"
        }
      }
    },
    "resistor22.5": {
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
        "N007"
      ],
      "parameters": {
        "value": 8.2,
        "unit": "kohm",
        "source": "manual_from_image_label",
        "label_text": "R3 8.2 kohm",
        "viewer_override": {
          "label": "R3",
          "display_value": "8.2 kohm"
        }
      }
    },
    "speaker24.1": {
      "class_name": "Speaker",
      "status": "spice_ready",
      "spice_support": "equivalent",
      "spice_prefix": "R",
      "emit_as": "resistive_load",
      "node_order": [
        "t1",
        "t2"
      ],
      "nodes": [
        "N010",
        "0"
      ],
      "parameters": {
        "nominal_power": 500,
        "power_unit": "mW",
        "source": "manual_from_image_label",
        "label_text": "K1 speaker 64 ohm, 500 mW",
        "spice_override": {
          "emit_as": "resistive_load",
          "equivalent_resistance": 64,
          "resistance_unit": "ohm",
          "node_order": [
            "t1",
            "t2"
          ],
          "semantic_role": "speaker_equivalent"
        },
        "viewer_override": {
          "visual_class": "speaker",
          "label": "K1",
          "display_value": "64 ohm",
          "tooltip": "Speaker 64 ohm, 500 mW; equivalente SPICE resistivo"
        },
        "equivalent_resistance": 64,
        "resistance_unit": "ohm"
      },
      "reason": "Explicit YAML override emitted as an equivalent resistive load."
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
      "step": "50us",
      "stop": "2s"
    }
  },
  "stats": {
    "components_total": 15,
    "spice_ready_components": 13,
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
* circuit: ic04

VVCC_12 N005 0 DC 12
Xintegrated_circuit11_1 N003 N001 N003 N005 N004 N002 N005 0 TLC555_6
Xintegrated_circuit11_2 N008 N006 N008 N005 N009 N007 N005 0 TLC555_6
Dled12_1 N002 N003 D_1N4001_TYP
Cpolarized_capacitor20_1 N003 0 10u
Cpolarized_capacitor20_2 N001 0 10n
Cpolarized_capacitor20_3 N008 0 100n
Cpolarized_capacitor20_4 N009 N010 100u
Rresistor22_1 N002 N003 68k
Rresistor22_2 N005 N002 68k
Rresistor22_3 N004 N006 10k
Rresistor22_4 N007 N008 8.2k
Rresistor22_5 N005 N007 8.2k
Rspeaker24_1 N010 0 64

.model D_1N4001_TYP D(IS=14n N=1.9 RS=0.08 BV=50 IBV=5u TT=2u CJO=25p)
.include "07_external_models.lib"

.save all
.tran 50us 2s

.control
set wr_singlescale
set wr_vecnames
save all @dled12_1[id]
run
wrdata 08_tran.csv time v(N001) v(N002) v(N003) v(N004) v(N005) v(N006) v(N007) v(N008) v(N009) v(N010) @dled12_1[id]
.endc
.end

```

## 07_spice_emit_report.json
```text
{
  "circuit_id": "ic04",
  "source_format": "pipeline2.0_spice_emit_report",
  "emitted_elements": 14,
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
      "N006",
      "N007",
      "N008",
      "N009",
      "N010"
    ],
    "device_currents": [
      "@dled12_1[id]"
    ]
  },
  "models": [
    "D_1N4001_TYP",
    "TLC555_6"
  ],
  "warnings": [],
  "external_model_sources": [
    {
      "model": "TLC555_6",
      "kind": "file",
      "file": "spice_models/ti/tlc555/slfj002e/TLC555_6.LIB",
      "sha256": "7C091782CC4931DDA4FEBF25605083F47161C5E1592C076689B04B70DD749034",
      "encoding": "utf-8-sig"
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
n005                                        12
xintegrated_circuit11_1.resi                12
xintegrated_circuit11_1.trgi         0.0417684
n003                                 0.0417537
xintegrated_circuit11_1.thri         0.0417537
xintegrated_circuit11_1.conti          4.60841
n001                                   4.43178
xintegrated_circuit11_1.qff                  1
xintegrated_circuit11_1.gout       2.84871e-07
xintegrated_circuit11_1.trgo           2.95168
xintegrated_circuit11_1.xmn3.10            0.14
xintegrated_circuit11_1.23            0.163845
xintegrated_circuit11_1.thrs           4.01249
xintegrated_circuit11_1.xmn5.10            0.14
xintegrated_circuit11_1.25            0.150935
xintegrated_circuit11_1.reso       0.000240912
xintegrated_circuit11_1.15           0.0395409
xintegrated_circuit11_1.xmp9.10           11.15
xintegrated_circuit11_1.xmp6.10           11.15
xintegrated_circuit11_1.trgs           2.95219
xintegrated_circuit11_1.xmp5.10           11.15
xintegrated_circuit11_1.thro            11.995
xintegrated_circuit11_1.xmp1.10           11.86
xintegrated_circuit11_1.29             11.8135
xintegrated_circuit11_1.xib.gb_int1      3.9529e-08
xintegrated_circuit11_1.xrsff.xu1.out_vmeas_0               0
xintegrated_circuit11_1.xrsff.xu1.eout_int1               0
xintegrated_circuit11_1.30                   0
xintegrated_circuit11_1.xrsff.xu2.out_vmeas_2               1
xintegrated_circuit11_1.xrsff.xu2.eout_int1               1
xintegrated_circuit11_1.xrsff.xu2.1       0.0896861
xintegrated_circuit11_1.xrsff.xu2.e1_int1       0.0896861
n002                                  0.501331
n004                                   11.9932
xintegrated_circuit11_1.trgc            2.3042
xintegrated_circuit11_1.32             1.15211
xintegrated_circuit11_1.33             3.45631
xintegrated_circuit11_1.34              8.3042
xintegrated_circuit11_2.resi                12
xintegrated_circuit11_2.trgi           5.38425
n008                                   5.38426
xintegrated_circuit11_2.thri           5.38425
xintegrated_circuit11_2.conti          10.6344
n006                                   10.7261
xintegrated_circuit11_2.qff                  1
xintegrated_circuit11_2.gout       3.12258e-07
xintegrated_circuit11_2.trgo        0.00199402
xintegrated_circuit11_2.xmn3.10            0.14
xintegrated_circuit11_2.23            0.188721
xintegrated_circuit11_2.thrs           10.0383
xintegrated_circuit11_2.xmn5.10            0.14
xintegrated_circuit11_2.25            0.150924
xintegrated_circuit11_2.reso       0.000240912
xintegrated_circuit11_2.15           0.0395409
xintegrated_circuit11_2.xmp9.10           11.15
xintegrated_circuit11_2.xmp6.10           11.15
xintegrated_circuit11_2.trgs           5.98558
xintegrated_circuit11_2.xmp5.10           11.15
xintegrated_circuit11_2.thro            11.995
xintegrated_circuit11_2.xmp1.10           11.86
xintegrated_circuit11_2.29             11.8137
xintegrated_circuit11_2.xib.gb_int1      3.9529e-08
xintegrated_circuit11_2.xrsff.xu1.out_vmeas_0               0
xintegrated_circuit11_2.xrsff.xu1.eout_int1               0
xintegrated_circuit11_2.30                   0
xintegrated_circuit11_2.xrsff.xu2.out_vmeas_2               1
xintegrated_circuit11_2.xrsff.xu2.eout_int1               1
xintegrated_circuit11_2.xrsff.xu2.1       0.0896861
xintegrated_circuit11_2.xrsff.xu2.e1_int1       0.0896861
n007                                   8.69211
n009                                   9.18721
xintegrated_circuit11_2.trgc           5.31718
xintegrated_circuit11_2.32             2.65859
xintegrated_circuit11_2.33             7.97577
xintegrated_circuit11_2.34             11.3172
n010                                   2.92065
b.xintegrated_circuit11_2.xrsff.xu2.be1#branch               0
b.xintegrated_circuit11_2.xrsff.xu2.beout#branch               0
v.xintegrated_circuit11_2.xrsff.xu2.v_eout#branch    -1.99999e-12
b.xintegrated_circuit11_2.xrsff.xu1.beout#branch               0
v.xintegrated_circuit11_2.xrsff.xu1.v_eout#branch               0
b.xintegrated_circuit11_2.xib.bgb#branch               0
b.xintegrated_circuit11_1.xrsff.xu2.be1#branch               0
b.xintegrated_circuit11_1.xrsff.xu2.beout#branch               0
v.xintegrated_circuit11_1.xrsff.xu2.v_eout#branch    -1.99999e-12
b.xintegrated_circuit11_1.xrsff.xu1.beout#branch               0
v.xintegrated_circuit11_1.xrsff.xu1.v_eout#branch               0
b.xintegrated_circuit11_1.xib.bgb#branch               0
v.xintegrated_circuit11_2.xmp1.v1#branch     6.08863e-07
v.xintegrated_circuit11_2.xmn5.v1#branch     7.58977e-08
v.xintegrated_circuit11_2.xmn3.v1#branch     8.22001e-07
v.xintegrated_circuit11_1.xmp1.v1#branch     6.11347e-07
v.xintegrated_circuit11_1.xmn5.v1#branch     7.59709e-08
v.xintegrated_circuit11_1.xmn3.v1#branch      8.0431e-07
e.xintegrated_circuit11_2.xrsff.xu2.e1#branch               0
e.xintegrated_circuit11_2.xrsff.xu2.eout#branch    -1.99999e-12
e.xintegrated_circuit11_2.xrsff.xu1.eout#branch               0
e.xintegrated_circuit11_1.xrsff.xu2.e1#branch               0
e.xintegrated_circuit11_1.xrsff.xu2.eout#branch    -1.99999e-12
e.xintegrated_circuit11_1.xrsff.xu1.eout#branch               0
v.xintegrated_circuit11_2.xmp5.v1#branch     6.16441e-12
v.xintegrated_circuit11_2.xmp6.v1#branch     1.19991e-11
v.xintegrated_circuit11_2.xmp9.v1#branch     1.21498e-11
v.xintegrated_circuit11_1.xmp5.v1#branch     9.19781e-12
v.xintegrated_circuit11_1.xmp6.v1#branch     1.19991e-11
v.xintegrated_circuit11_1.xmp9.v1#branch     1.21498e-11
vvcc_12#branch                      -0.0466151

 Reference value :  3.11198e-02
 Reference value :  1.11825e-01
 Reference value :  1.65084e-01
 Reference value :  1.81305e-01
 Reference value :  2.43648e-01
 Reference value :  3.18811e-01
 Reference value :  4.09852e-01
 Reference value :  5.22398e-01
 Reference value :  5.84563e-01
 Reference value :  6.31810e-01
 Reference value :  6.87877e-01
 Reference value :  7.43459e-01
 Reference value :  8.01348e-01
 Reference value :  8.21064e-01
 Reference value :  8.38116e-01
 Reference value :  8.53685e-01
 Reference value :  8.69305e-01
 Reference value :  8.83706e-01
 Reference value :  8.97230e-01
 Reference value :  9.12749e-01
 Reference value :  9.25661e-01
 Reference value :  9.41768e-01
 Reference value :  9.57794e-01
 Reference value :  9.79813e-01
 Reference value :  9.96040e-01
 Reference value :  1.01072e+00
 Reference value :  1.02522e+00
 Reference value :  1.03982e+00
 Reference value :  1.04484e+00
 Reference value :  1.05420e+00
 Reference value :  1.07020e+00
 Reference value :  1.08638e+00
 Reference value :  1.09992e+00
 Reference value :  1.11671e+00
 Reference value :  1.13309e+00
 Reference value :  1.15403e+00
 Reference value :  1.16941e+00
 Reference value :  1.18603e+00
 Reference value :  1.20244e+00
 Reference value :  1.21859e+00
 Reference value :  1.23323e+00
 Reference value :  1.24875e+00
 Reference value :  1.26415e+00
 Reference value :  1.34356e+00
 Reference value :  1.45140e+00
 Reference value :  1.56253e+00
 Reference value :  1.65946e+00
 Reference value :  1.75252e+00
 Reference value :  1.78989e+00
 Reference value :  1.80564e+00
 Reference value :  1.82563e+00
 Reference value :  1.84076e+00
 Reference value :  1.85724e+00
 Reference value :  1.87188e+00
 Reference value :  1.88889e+00
 Reference value :  1.90406e+00
 Reference value :  1.92420e+00
 Reference value :  1.93931e+00
 Reference value :  1.95692e+00
 Reference value :  1.97268e+00
 Reference value :  1.98439e+00
 Reference value :  1.99454e+00

No. of Data Rows : 131120
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

Warning: Model issue on line 118 :
  .model xintegrated_circuit11_2.xmn17:tlc55x_nmosd_hv nmos level=3 l=10u  ...
unrecognized parameter (lambda) - ignored

Warning: Model issue on line 118 :
  .model xintegrated_circuit11_2.xmn16:tlc55x_nmosd_hv nmos level=3 l=10u  ...
unrecognized parameter (lambda) - ignored

Warning: Model issue on line 204 :
  .model xintegrated_circuit11_2.xmp16:tlc55x_pmosd_hv pmos level=3 l=10u  ...
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
  "circuit_id": "ic04",
  "user_problem": "La sirena suona, ma sembra emettere quasi sempre lo stesso tono. Cosa posso controllare per rendere più evidente il cambio di suono?",
  "pipeline2_output_dir": "outputs\\demo_workspaces\\ic_chat_agent_evaluation\\web\\agent\\ic04",
  "summary": {
    "spice_status": "success",
    "spice_exit_code": 0,
    "spice_message": "ngspice completed successfully.",
    "emitted_elements": 14,
    "skipped_elements": 2,
    "emit_warnings_count": 0,
    "skipped_components_count": 2,
    "node_count": 11,
    "ground_groups_count": 1,
    "singleton_nodes_count": 0,
    "bound_components": 11,
    "missing_components": 0,
    "unsupported_components": 2,
    "spice_ready_components": 13,
    "rules_missing_components": 0,
    "has_tran_csv": true,
    "has_tran_plot": true,
    "led_profiles": {}
  },
  "artifacts": {
    "graph": {
      "step": "01",
      "available": true,
      "path": "outputs\\demo_workspaces\\ic_chat_agent_evaluation\\web\\agent\\ic04\\01_graph.json",
      "role": "Graph JSON copied from Pipeline 1.0."
    },
    "normalized_circuit": {
      "step": "02",
      "available": true,
      "path": "outputs\\demo_workspaces\\ic_chat_agent_evaluation\\web\\agent\\ic04\\02_normalized_circuit.json",
      "role": "Normalized circuit representation used by Pipeline 2.0."
    },
    "node_map": {
      "step": "03",
      "available": true,
      "path": "outputs\\demo_workspaces\\ic_chat_agent_evaluation\\web\\agent\\ic04\\03_node_map.json",
      "role": "Maps component terminals to SPICE node names."
    },
    "values_bound": {
      "step": "04",
      "available": true,
      "path": "outputs\\demo_workspaces\\ic_chat_agent_evaluation\\web\\agent\\ic04\\04_values_bound.json",
      "role": "Values and labels bound to graph components."
    },
    "component_rules": {
      "step": "06",
      "available": true,
      "path": "outputs\\demo_workspaces\\ic_chat_agent_evaluation\\web\\agent\\ic04\\06_component_rules.json",
      "role": "SPICE conversion rules for each component."
    },
    "netlist": {
      "step": "07",
      "available": true,
      "path": "outputs\\demo_workspaces\\ic_chat_agent_evaluation\\web\\agent\\ic04\\07_netlist.cir",
      "role": "Generated SPICE netlist."
    },
    "spice_emit_report": {
      "step": "07",
      "available": true,
      "path": "outputs\\demo_workspaces\\ic_chat_agent_evaluation\\web\\agent\\ic04\\07_spice_emit_report.json",
      "role": "Report of emitted, skipped and warning components."
    },
    "spice_run": {
      "step": "08",
      "available": true,
      "path": "outputs\\demo_workspaces\\ic_chat_agent_evaluation\\web\\agent\\ic04\\08_spice_run.json",
      "role": "Structured ngspice execution report."
    },
    "ngspice_stdout": {
      "step": "08",
      "available": true,
      "path": "outputs\\demo_workspaces\\ic_chat_agent_evaluation\\web\\agent\\ic04\\08_ngspice_stdout.txt",
      "role": "Raw ngspice stdout log."
    },
    "ngspice_stderr": {
      "step": "08",
      "available": true,
      "path": "outputs\\demo_workspaces\\ic_chat_agent_evaluation\\web\\agent\\ic04\\08_ngspice_stderr.txt",
      "role": "Raw ngspice stderr log."
    },
    "tran_csv": {
      "step": "08",
      "available": true,
      "path": "outputs\\demo_workspaces\\ic_chat_agent_evaluation\\web\\agent\\ic04\\08_tran.csv",
      "role": "Clean transient CSV, when .tran data is available."
    },
    "tran_plot_png": {
      "step": "08",
      "available": true,
      "path": "outputs\\demo_workspaces\\ic_chat_agent_evaluation\\web\\agent\\ic04\\08_tran_plot.png",
      "role": "Transient plot PNG, when generated."
    },
    "tran_plot_svg": {
      "step": "08",
      "available": false,
      "path": null,
      "role": "Transient plot SVG fallback, when generated."
    }
  },
  "executed_scenarios": [],
  "scenario_outcome_summary": {
    "available": false,
    "best_scenario_id": null,
    "best_outcome_status": null,
    "best_stop_automation": null,
    "ranking_status": "no_verified_best",
    "interpretation_rule": "If a user asks which scenario resolves the problem, prefer the scenario with outcome_status='resolved_candidate' and stop_automation=true. Partially resolved scenarios without verified expectations are supporting diagnostics and must not be ranked only by changed_count.",
    "scenarios": []
  },
  "scenario_budget": {
    "max_executable_scenarios": 5,
    "executed_scenarios_count": 0,
    "remaining_executable_scenarios": 5,
    "budget_exhausted": false,
    "last_scenario_available": false,
    "policy": "At most 5 scenarios can be executed for the same circuit. When only one scenario remains, the agent should propose a single final scenario. When no scenario remains, the agent must stop proposing new scenarios and provide a final diagnostic conclusion."
  },
  "image_access": {
    "included_by_default": false,
    "can_be_requested": true,
    "path": "outputs\\demo_workspaces\\ic_chat_agent_evaluation\\input\\images\\ic04.jpg",
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
