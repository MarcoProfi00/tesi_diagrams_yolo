# Revisione manuale degli errori critici del judge

## Stato e scopo

Revisione completata il 29 luglio 2026 sugli artefatti ufficiali
dell'esperimento CHAT–AGENT.

L'aggregazione contiene 34 valutazioni, corrispondenti a una run CHAT e una
run AGENT per ciascuno dei 17 circuiti. Il judge ha segnalato almeno un errore
critico in 10 valutazioni:

- `a06`: CHAT e AGENT;
- `a10`: AGENT;
- `b02`: AGENT;
- `b04`: AGENT;
- `b05`: AGENT;
- `b10`: CHAT e AGENT;
- `c02`: CHAT e AGENT.

La revisione riguarda tutti i 18 flag positivi presenti in queste valutazioni.
Non modifica i summary, i judge, gli esiti o i punteggi ufficiali.

## Metodo

Per ogni valutazione sono stati confrontati:

1. il sintomo o obiettivo iniziale;
2. l'intera interazione CHAT o la sequenza decisionale AGENT;
3. gli scenari realmente eseguiti e le azioni applicate;
4. le misure SPICE della base run e degli scenari;
5. la conclusione prodotta dal sistema;
6. la motivazione del relativo flag nel file judge.

La verifica usa i file ufficiali:

```text
evaluation/<circuito>/<modalità>_summary.json
evaluation/<circuito>/<modalità>_judge.json
```

Sono state adottate tre categorie:

- **confermato**: gli artefatti sostengono il rilievo del judge;
- **dubbio**: esiste un problema reale, ma le evidenze non permettono di
  confermare integralmente la motivazione del flag;
- **non confermato**: gli artefatti completi contengono evidenze che
  contraddicono la motivazione del flag.

La revisione considera anche gli artefatti completi del summary. Il pacchetto
compatto fornito al judge rimuove alcuni metadati non elettrici, fra cui i campi
`source` e `label_text` di `values_bound`. Questa differenza è rilevante per
interpretare due dei flag discussi di seguito.

## Risultato complessivo

| Errore critico | Flag revisionati | Confermati | Dubbi | Non confermati |
|---|---:|---:|---:|---:|
| `false_success` | 4 | 4 | 0 | 0 |
| `unsupported_claims` | 10 | 7 | 1 | 2 |
| `wrong_interpretation` | 4 | 4 | 0 | 0 |
| **Totale** | **18** | **15** | **1** | **2** |

Quindici flag su diciotto, pari all'83,3%, trovano conferma diretta negli
artefatti completi. Considerando anche il caso dubbio, sedici flag su diciotto
non risultano smentiti. Questo dato descrive la precisione dei flag positivi
revisionati; non misura eventuali falsi negativi, perché le 24 valutazioni
senza errori critici non sono state incluse in questo controllo mirato.

## Sintesi per valutazione

| Circuito | Modalità | Punteggio | Esito | Flag positivi | Esito della revisione | Plausibilità complessiva |
|---|---|---:|---|---|---|---|
| `a06` | CHAT | 50 | `partial_success` | `false_success`, `unsupported_claims` | entrambi confermati, con una precisazione sul guadagno | Plausibile ma conservativa |
| `a06` | AGENT | 60 | `partial_success` | `unsupported_claims`, `wrong_interpretation` | uno dubbio, uno confermato | Plausibile |
| `a10` | AGENT | 85 | `success` | `unsupported_claims` | confermato, ma marginale | Plausibile |
| `b02` | AGENT | 60 | `partial_success` | `false_success`, `unsupported_claims` | entrambi confermati | Plausibile, lievemente generosa |
| `b04` | AGENT | 35 | `failure` | tutti e tre | tutti confermati | Pienamente plausibile |
| `b05` | AGENT | 60 | `partial_success` | `unsupported_claims`, `wrong_interpretation` | entrambi confermati | Plausibile |
| `b10` | CHAT | 85 | `success` | `unsupported_claims` | non confermato sugli artefatti completi | Esito plausibile |
| `b10` | AGENT | 80 | `success` | `unsupported_claims` | confermato | Plausibile |
| `c02` | CHAT | 65 | `partial_success` | `unsupported_claims` | non confermato sugli artefatti completi | Esito plausibile |
| `c02` | AGENT | 50 | `partial_success` | tutti e tre | tutti confermati | Pienamente plausibile |

## Revisione dettagliata

### `a06` — CHAT

**Obiettivo.** Diagnosticare un'uscita distorta e, dopo le richieste
successive dell'utente, verificare una soluzione con THD inferiore al 10% e
guadagno utile.

**Evidenze principali.**

- Base run: ingresso `SIN(0 1 100)`.
- Scenario 1: ingresso ridotto a 100 mV.
- Scenario 4: ingresso ridotto a 50 mV e guadagno Vpp pari a circa `62,75`.
- Scenario 5: ingresso ridotto a 20 mV e guadagno Vpp pari a circa `77,89`.
- Tutti gli scenari riescono in SPICE, ma restano `partially_resolved`.
- Nello scenario 5, `base_thd` e `scenario_thd` sono `null` e
  `quality_available` è `false`.
- I valori THD `83,0%` e `9,79%` vengono inseriti dall'utente e non sono
  ricalcolati o registrati dal comparatore SPICE.

**`false_success`: confermato.** La risposta finale dichiara una
“correzione verificata nei fatti”, nonostante il requisito THD non sia
verificato negli artefatti automatici e lo scenario resti
`partially_resolved`. La risposta esplicita il limite, ma usa comunque una
formulazione conclusiva più forte della prova disponibile.

**`unsupported_claims`: confermato con precisazione.** La THD usata per
dimostrare il successo proviene dall'utente e, secondo il protocollo congelato,
deve essere verificata sulle misure SPICE. Il guadagno Vpp `77,89`, invece, è
presente nel confronto automatico; il rilievo del judge è quindi corretto per
la THD, ma non deve essere esteso al semplice rapporto di guadagno.

**Valutazione complessiva.** `partial_success` è appropriato. Il punteggio
50/100 è conservativo, ma difendibile perché la diagnosi di sovrapilotaggio è
utile mentre il requisito quantitativo finale non è stato verificato dal
workflow.

### `a06` — AGENT

**Obiettivo.** Diagnosticare autonomamente la distorsione dell'uscita.

**Evidenze principali.**

- Riducendo l'ingresso da 1 Vpk a 50 mVpk, la THD automatica passa da
  `0,8302` a `0,2238` e il guadagno resta circa `62,75`.
- `quality_improved` è vero, ma `quality_acceptable` è falso.
- Portando `Rresistor22_3` a 100 kΩ, la THD resta alta, pari a `0,7527`.
- La conclusione identifica correttamente il sovrapilotaggio, ma descrive il
  BJT come quasi interdetto a causa di `VBE≈0,117 V` e `gm` quasi nullo.
- Le tensioni operative riportano `N002=3,664 V` e `N003=3,024458 V`, quindi
  la differenza base-emettitore è circa `0,640 V`.

**`unsupported_claims`: dubbio.** Lo stdout completo contiene realmente
`vbe=0,117031`, `gm=5,54364e-11` e `ic=5,22697e-7`; i numeri non sono
inventati. Questi dettagli non compaiono però nel pacchetto compatto del judge
e vengono usati fuori contesto come prova del punto di lavoro. Il problema
causale esiste, ma non è corretto sostenere che i valori citati siano
completamente assenti dagli artefatti completi.

**`wrong_interpretation`: confermato.** Le tensioni nodali e le correnti
ricavabili dai rami di emettitore e collettore non descrivono un transistor
quasi interdetto. Il valore isolato del report del dispositivo viene
interpretato erroneamente come descrizione del punto operativo generale,
indebolendo la localizzazione sul bias.

**Valutazione complessiva.** `partial_success` e 60/100 sono plausibili. Il
sovrapilotaggio è dimostrato quantitativamente, mentre la seconda parte della
diagnosi sul bias è tecnicamente incoerente.

### `a10` — AGENT

**Obiettivo.** Accendere contemporaneamente lampada e LED nella stessa
simulazione stabile.

**Evidenze principali.**

Lo scenario chiude lo switch e collega `N002` a `N003` e `N004`. La
simulazione `.op` produce:

- `v(N003): ≈0 → 4,999954 V`;
- `v(N004): 0 → 4,999947 V`;
- `v(N005): ≈0 → 0,721391 V`;
- corrente della lampada: `0 → 19,9998 mA`;
- corrente del ramo LED: `0 → 12,9653 mA`;
- corrente della batteria: `0 → −32,9651 mA`.

L'attivazione simultanea dei due rami è quindi verificata.

**`unsupported_claims`: confermato, ma marginale.** Nella motivazione
iniziale viene affermato che, con lo switch aperto, `N002` riceva già i 5 V.
Nella base run `v(N002)` è invece mancante e lo switch aperto non viene emesso
nella netlist. L'imprecisione non invalida l'evidenza ottenuta nello scenario.

**Valutazione complessiva.** `success` e 85/100 sono plausibili. La prova
funzionale principale è corretta e completa.

### `b02` — AGENT

**Obiettivo.** Spiegare perché i due LED rimangano accesi invece di
lampeggiare alternativamente.

**Evidenze principali.**

- Base run: entrambi i LED sono `steady_on`, duty cycle 1 e corrente pari a
  circa `15,483 mA`.
- I nodi simmetrici hanno valori uguali e i due transistor conducono
  contemporaneamente.
- Due test con condizioni iniziali asimmetriche producono soltanto impulsi
  transitori non periodici; `temporal_met` è falso.
- I due test di startup producono anche picchi anomali, fino a tensioni
  dell'ordine dei kilovolt e correnti LED dell'ordine degli ampere, non
  discussi dall'AGENT.
- Portando entrambe le resistenze di base da 2,2 kΩ a 22 kΩ, il lampeggio
  resta non periodico e `temporal_met` rimane falso.
- La conclusione dichiara localizzata la causa nel bias eccessivo, ma non
  riporta una correzione verificata.

**`false_success`: confermato.** Sebbene non venga dichiarata una riparazione,
la causa viene presentata come localizzata in modo conclusivo. Nessuno
scenario distingue definitivamente il bias da altre cause di parametrizzazione
o startup.

**`unsupported_claims`: confermato.** Le resistenze da 2,2 kΩ costituiscono
un'ipotesi plausibile, non una causa verificata. Lo scenario mirato a 22 kΩ non
produce il comportamento richiesto.

**Valutazione complessiva.** `partial_success` è appropriato. Il punteggio
60/100 è plausibile e, considerando le anomalie transitorie non discusse,
lievemente generoso.

### `b04` — AGENT

**Obiettivo.** Verificare se una batteria più scarica riceva più corrente di
carica.

**Evidenze principali.**

| Condizione | `i(VVBAT_TEST)` |
|---|---:|
| Base, batteria a 12 V | `−12,4225 mA` |
| Scenario 1, batteria a 10 V | `−10,2715 mA` |
| Scenario 2, batteria a 8 V | `−8,43212 mA` |

In entrambi gli scenari il modulo della corrente diminuisce e l'aspettativa
`magnitude_increased` è falsa. Il picco di `Ddiode7_4` cresce soltanto da
`0,33475 A` a circa `0,33660 A`, variazione che non dimostra un aumento della
corrente assorbita dalla batteria. Il terzo scenario viene respinto come
duplicato.

**`false_success`: confermato.** La conclusione risponde affermativamente al
quesito, nonostante la misura principale non dimostri l'aumento richiesto.

**`unsupported_claims`: confermato.** La localizzazione in un percorso di
rettifica e controllo SCR-transistor poco efficace non è verificata mediante
un test specifico su tale sottosistema.

**`wrong_interpretation`: confermato.** La conclusione attribuisce ai dati un
aumento della corrente mentre il relativo modulo diminuisce in entrambi gli
scenari.

**Valutazione complessiva.** `failure` e 35/100 sono pienamente plausibili.
Gli scenari sono pertinenti, ma la risposta finale interpreta al contrario
l'evidenza centrale.

### `b05` — AGENT

**Obiettivo.** Diagnosticare l'assenza di audio nelle cuffie.

**Evidenze principali.**

- Nella base run lo switch S1 è aperto e i nodi e le correnti sono
  praticamente nulli.
- Chiudendo S1, `N004≈−9 V` e nella cuffia equivalente compaiono circa
  `3,724 mA`.
- Applicando segnali sui nodi di ingresso e sui nodi interni, l'uscita in
  cuffia rimane fra 0 e poche decine di nanovolt: il trasferimento AC è
  praticamente nullo.
- Invertendo la batteria, la corrente nella cuffia scende a circa `10⁻16 A` e
  falliscono le aspettative di corrente decisive.
- Con transistor PNP aventi gli emettitori a massa, il rail negativo originale
  è compatibile con la conduzione; è l'inversione verso il rail positivo a
  spegnere lo stadio.

**`unsupported_claims`: confermato.** La polarità originale viene presentata
come causa localizzata dell'interdizione dei PNP, ma lo scenario costruito per
verificarla non sostiene questa spiegazione.

**`wrong_interpretation`: confermato.** La conclusione afferma che la polarità
originale mantenga i transistor quasi interdetti, mentre proprio con tale
polarità e S1 chiuso compaiono bias e corrente nella cuffia. Invertendo la
batteria, la corrente si annulla quasi completamente.

**Valutazione complessiva.** `partial_success` e 60/100 sono plausibili.
L'AGENT identifica correttamente lo switch aperto e dimostra l'assenza di
trasferimento AC, ma associa questi risultati a una causa fisica errata.

### `b10` — CHAT

**Obiettivo.** Spiegare perché il nodo A misuri 1 V mentre B sia quasi a zero.

**Evidenze principali.**

- Base: `v(N001)=1 V` e `v(N002)=0,001 V`.
- Lo switch è aperto.
- Chiudendolo, `v(N002)` passa da `0,001 V` a `0,999 V` e `v(N005)` da
  `0,002 V` a `1 V`.
- La conclusione identifica correttamente l'isolamento introdotto dallo switch.

**`unsupported_claims`: non confermato sugli artefatti completi.** Il judge
sostiene che le provenienze
`manual_assumption_symbolic_switch_model/test_bench` non siano documentate.
Nel summary completo, invece, `values_bound` le riporta esplicitamente per le
sorgenti di test, le resistenze, i condensatori e la sorgente di offset.

La motivazione del judge è comprensibile rispetto al pacchetto compatto,
perché `run_judge.py` rimuove i campi `source` e `label_text` prima della
valutazione. Il flag non è però confermato quando si controllano gli artefatti
completi.

**Valutazione complessiva.** `success` è appropriato e il punteggio 85/100
resta plausibile. Il rilievo sulla provenienza dei valori non deve essere usato
come prova di un errore tecnico della diagnosi.

### `b10` — AGENT

**Obiettivo ed evidenze principali.** Sono gli stessi della modalità CHAT. La
chiusura dello switch porta B da `0,001 V` a `0,999 V`, confermando la causa
locale principale.

**`unsupported_claims`: confermato.** L'AGENT attribuisce il valore di B pari
a circa 1 mV anche alla sorgente:

```text
Vvoltage_source31_1 N005 N002 DC 0.001
```

Questa sorgente impone solamente `V(N005)−V(N002)=1 mV` e, con lo switch
aperto, non stabilisce il valore assoluto di B. Il valore di `N002` deriva dal
bilancio fra la resistenza di perdita da 1 GΩ e le sorgenti di corrente del
banco di test.

**Valutazione complessiva.** `success` e 80/100 sono plausibili. La causa
principale è corretta e verificata; l'errore riguarda il meccanismo secondario
che determina il millivolt residuo.

### `c02` — CHAT

**Obiettivo.** Capire perché due LED sembrino restare entrambi accesi anziché
lampeggiare alternativamente.

**Evidenze principali.**

- Nella base run entrambi i LED sono `blinking`, con periodo regolare e
  frequenza di circa `1,668 Hz`.
- Non emergono errori topologici o componenti saltati.
- Riducendo C1 da 10 µF a 4,7 µF, i LED restano `blinking` e le frequenze
  salgono a circa `2,273 Hz`.
- Lo scenario ha `meaningful_improvement_count=0`, esito
  `partially_resolved` e `stop_automation=false`.
- La CHAT interpreta correttamente C1 come parametro di temporizzazione e non
  come soluzione definitiva.

**`unsupported_claims`: non confermato sugli artefatti completi.** Il judge
afferma che la provenienza `manual_testbench_assumption` dei condensatori non
sia documentata. Nel summary completo, `values_bound` riporta invece
esplicitamente tale sorgente per entrambi i condensatori da 10 µF.

Anche in questo caso il pacchetto compatto elimina il campo `source`, rendendo
il rilievo comprensibile dal punto di vista del judge ma non confermato dalla
revisione degli artefatti completi.

**Valutazione complessiva.** `partial_success` è appropriato e 65/100 è
plausibile. La simulazione esclude un blocco nel modello, ma non identifica la
causa del comportamento osservato sul montaggio reale.

### `c02` — AGENT

**Obiettivo.** Diagnosticare e correggere la mancata alternanza percepita dei
due LED.

**Evidenze principali.**

- La base run mostra già entrambi i LED `blinking` regolarmente a circa
  `1,668 Hz`.
- Lo scenario riduce entrambi i condensatori da 10 µF a 1 µF.
- La frequenza sale a circa `166,7 Hz`.
- Le aspettative verificate controllano correnti non nulle, variazioni di
  alcuni nodi e il lampeggio regolare di un solo LED.
- Non vengono misurate fase relativa, sovrapposizione temporale, simultaneità
  o percezione visiva.
- `meaningful_improvement_count` è pari a 0.
- Nonostante ciò, l'AGENT dichiara stato `resolved`, “ampia sovrapposizione
  visiva” nella base e alternanza “molto più evidente” nello scenario.

**`false_success`: confermato.** Le aspettative soddisfatte non rappresentano
il sintomo. Lo scenario dimostra che il circuito continua a oscillare, non che
l'alternanza sia più evidente o meno simultanea.

**`unsupported_claims`: confermato.** Le affermazioni su sovrapposizione e
maggiore evidenza visiva non sono sostenute da metriche relazionali fra i due
LED.

**`wrong_interpretation`: confermato.** Cambiamenti nodali e lampeggio regolare
vengono letti come prova della soluzione. Inoltre l'aumento a circa 166,7 Hz
non dimostra una migliore percepibilità dell'alternanza.

**Valutazione complessiva.** `partial_success` e 50/100 sono pienamente
plausibili. L'AGENT riconosce correttamente che topologia e oscillazione
funzionano, ma causa, correzione e dichiarazione di risoluzione non sono
verificate.

## Interpretazione della revisione

La revisione conferma tutti i casi di `false_success` e
`wrong_interpretation`. Il judge risulta quindi particolarmente affidabile nel
riconoscere conclusioni incompatibili con le misure SPICE o dichiarazioni di
risoluzione non dimostrate.

Le sole due contestazioni nette riguardano `unsupported_claims` in `b10` CHAT
e `c02` CHAT. In entrambi i casi l'affermazione è supportata nel summary
completo da un campo di provenienza rimosso durante la costruzione del
pacchetto. Questi casi documentano un limite informativo dell'input compatto,
non richiedono la modifica retroattiva dei risultati ufficiali e devono essere
riportati come parte del controllo di validità del judge.

Il caso dubbio `a06` AGENT deriva invece da evidenze interne contraddittorie:
il valore citato compare nello stdout completo, ma la sua interpretazione non
è coerente con le tensioni operative. Anche qui non vi sono motivi per
alterare il punteggio ufficiale; è sufficiente documentare l'ambiguità.
