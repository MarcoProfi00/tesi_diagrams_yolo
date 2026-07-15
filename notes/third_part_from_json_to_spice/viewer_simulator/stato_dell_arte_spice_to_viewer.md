# Stato dell'arte unificato - da graph/netlist SPICE a viewer, simulazione e diagnosi

Questo documento unifica il materiale di:

- `stato_dell_arte_spice_to_viewer.docx`
- `stato_dell_arte_spice_to_viewer_addendum.md`

ed e pensato come riferimento unico per la parte di tesi legata a:

```text
immagine / graph JSON -> netlist SPICE -> ngspice -> viewer / simulatore visuale -> diagnosi AI
```

L'obiettivo non e coprire tutta l'EDA o tutta la computer vision sugli
schematici, ma fissare in modo chiaro:

- cosa esiste gia nello stato dell'arte;
- dove il nostro progetto si allinea ai lavori esistenti;
- dove invece propone una combinazione ancora poco coperta;
- quali strumenti e paper conviene citare per Experiment 3.

## Sintesi esecutiva

Fra il 2024 e il 2026 lo stato dell'arte ha fatto un salto notevole nella
conversione:

```text
immagine di schematico -> netlist SPICE/HSPICE/Spectre
```

I lavori piu forti in questa direzione sono `SINA`, `Netlistify` e
`Image2Net`. Il loro contributo principale non e solo il riconoscimento dei
componenti, ma soprattutto:

- ricostruzione della connettivita;
- distinzione fra crossing e vere connessioni;
- ricostruzione topologica;
- verifica della correttezza della netlist con metriche strutturali.

Quasi tutta questa letteratura e pero ancora `image-first`: parte
dall'immagine e mira ad arrivare alla netlist.

Il nostro progetto e diverso in un punto cruciale. Il centro del lavoro non e
fare una computer vision piu forte, ma stabilizzare e valorizzare una
rappresentazione intermedia:

```text
immagine -> graph JSON -> mappa nodi -> netlist SPICE -> simulazione -> viewer -> diagnosi
```

Questa impostazione e meno comune, ma molto solida per una tesi, perche rende
ogni passaggio:

- leggibile;
- auditabile;
- confrontabile;
- riusabile in esperimenti successivi.

Sul lato `SPICE + AI`, i lavori recenti mostrano che gli LLM funzionano meglio
quando ragionano su artefatti grounded:

- netlist;
- risultati di simulazione;
- testbench;
- confronti strutturali;
- misure elettriche.

Questo rafforza la scelta di usare `ngspice` come motore numerico di verita e
di costruire sopra un layer di reporting, scenari e viewer.

Infine, sul problema inverso:

```text
netlist -> schematico / viewer
```

esistono riferimenti importanti, ma ancora nessuna soluzione che coincida bene
con cio che ci serve in Experiment 3:

- viewer web locale;
- base run e scenario run;
- differenze topologiche visibili;
- overlay di tensioni, correnti e transitori;
- componenti strutturali extra-netlist ancora leggibili;
- integrazione diretta nella web chat.

Per questo la scelta migliore non e integrare un simulatore esterno completo,
ma costruire un viewer nativo piccolo, `netlist-first`, grounded su `ngspice`
e arricchito dal contesto strutturale del graph JSON.

## 1. Filone immagine -> netlist

### SINA

`SINA` e uno dei riferimenti piu forti sul problema `schematic image ->
netlist`. La pipeline combina deep learning, connected-component labeling, OCR
e assegnazione dei reference designator per produrre netlist SPICE a partire da
schematici sia IC-level sia PCB-level.

Per la nostra tesi e utile per due motivi:

- mostra che la conversione automatica verso una netlist simulabile e ormai un
  obiettivo realistico;
- conferma che la difficolta maggiore non e solo "vedere" i componenti, ma
  ricostruire bene la topologia elettrica.

Limite rispetto al nostro progetto:

- resta centrato su `immagine -> netlist`;
- non entra davvero nel problema `graph sporco -> artefatto elettrico
  eseguibile e spiegabile`;
- non affronta come primo obiettivo un viewer run-aware integrato con
  simulazione e scenari.

Fonte:

- <https://arxiv.org/abs/2607.01609>

### Netlistify

`Netlistify` e importante perche tratta il problema con una forte attenzione
alla struttura della pipeline e alla valutazione della connettivita. Non si
limita a una accuracy finale unica, ma separa detection, orientation,
connectivity e ricostruzione del netlist.

Per la nostra tesi e particolarmente utile come riferimento metodologico:

- conferma che la valutazione deve essere multilivello;
- giustifica l'idea di misurare la qualita del flusso non solo con un esito
  finale, ma anche con metriche topologiche e pin-level.

Fonte:

- paper: <https://research.nvidia.com/labs/electronic-design-automation/papers/netlistify_mlcad25.pdf>
- repository: <https://github.com/NYCU-AI-EDA/Netlistify>

### Image2Net

`Image2Net` e uno dei lavori piu interessanti perche spinge molto sulla
valutazione strutturale della netlist, usando una misura di distanza fondata su
grafo eterogeneo. Questo e rilevante perche sposta il focus dal semplice testo
della netlist alla sua struttura elettrica reale.

Per il nostro progetto questo si traduce in un messaggio forte:

```text
non basta confrontare stringhe SPICE;
conviene confrontare nodi, dispositivi, porte e connettivita.
```

Fonte:

- <https://arxiv.org/html/2508.13157v1>

### Altri lavori utili del filone

Restano utili anche lavori come `CircuitSchematicImageInterpreter`,
`Img2Sim` e altri approcci modulari o graph-based, perche mostrano che una
rappresentazione intermedia strutturata e spesso piu robusta di un flusso
puramente end-to-end.

Il valore per la tesi non e copiarli, ma usarli per sostenere che il nostro
passaggio:

```text
graph JSON rumoroso -> descrizione circuitale canonica -> netlist eseguibile
```

e una direzione legittima e originale.

Fonte utile:

- <https://pubs.aip.org/aip/aml/article/2/1/016109/3132693/Digitizing-images-of-electrical-circuit-schematics>

## 2. Il contributo specifico del nostro progetto

Quasi tutta la letteratura recente e `image-first`.

Il nostro progetto invece e piu precisamente:

```text
JSON-first oppure graph-first
```

L'assunzione pratica e che la computer vision produca gia un artefatto
intermedio:

- componenti riconosciuti;
- terminali;
- relazioni topologiche;
- qualche informazione di stato o classe.

Il contributo principale non e quindi "riconoscere meglio l'immagine", ma:

1. normalizzare il graph JSON;
2. ricostruire i nodi elettrici;
3. associare valori, modelli e stati mancanti;
4. generare netlist SPICE eseguibili;
5. validare con `ngspice`;
6. costruire report, scenari e viewer su questi artefatti.

Questa e la parte in cui la tesi ha piu spazio originale, perche tratta il
circuito come problema di `data engineering del circuito`, non solo come
computer vision.

## 3. SPICE come motore di verita

`ngspice` e il perno piu naturale per questo progetto.

Motivi:

- e open source;
- e ampiamente usato;
- supporta analogico, mixed-signal e batch mode;
- produce risultati numerici leggibili e salvabili;
- si integra bene in pipeline automatiche.

La scelta architetturale corretta e:

```text
ngspice = sorgente di verita numerica
viewer = rappresentazione e interpretazione dei risultati
agente = lettura grounded di struttura e simulazione
```

Questo evita di costruire un secondo simulatore con comportamenti potenzialmente
diversi.

Fonte:

- <https://ngspice.sourceforge.io/>

## 4. SPICE + AI grounded

I lavori recenti su `SPICE + AI` suggeriscono una direzione chiara: gli LLM
sono piu utili quando lavorano su artefatti verificabili.

### Auto-SPICE / Masala-CHAI

Questa linea di lavoro e utile perche mostra l'importanza della verifica
post-generazione e del confronto strutturale delle netlist. Non basta produrre
un testo plausibile: bisogna controllare se il circuito generato o modificato
ha senso elettrico.

Fonte:

- <https://arxiv.org/html/2411.14299v1>

### SPICEAssistant

`SPICEAssistant` mostra bene che il feedback simulativo migliora il
ragionamento dell'LLM. Questo e molto vicino alla nostra idea di agente che
legge:

- netlist;
- warning;
- stdout/stderr di `ngspice`;
- risultati `.op` e `.tran`;
- confronto fra base run e scenario run.

Fonte:

- <https://arxiv.org/html/2507.10639v1>

### AMSnet-q

`AMSnet-q` e rilevante perche tratta la netlist come oggetto su cui costruire
classificazione, testbench, labeling e analisi. Questo rafforza la tesi che la
netlist non e solo output finale, ma base strutturale per tool successivi.

Fonte:

- <https://arxiv.org/html/2605.01404v1>

### Implicazione pratica per la tesi

La diagnosi AI non dovrebbe essere formulata come:

```text
LLM che indovina il circuito da testo libero
```

ma come:

```text
LLM che ragiona su graph, netlist, esiti SPICE, scenari e viewer
```

Questa formulazione e piu robusta, piu misurabile e piu difendibile.

## 5. Il problema inverso: netlist -> schematico / viewer

Questa e la parte piu vicina a Experiment 3.

Finora molte pipeline si fermano a:

```text
netlist generata e simulabile
```

ma per un essere umano questo non basta sempre. I designer ragionano molto
meglio su rappresentazioni visuali del circuito. Da qui nasce il problema
inverso:

```text
come trasformare una netlist in una rappresentazione leggibile,
topologicamente corretta e utile per l'analisi?
```

### Schemato

`Schemato` affronta proprio il problema `netlist -> schematico`, convertendo
netlist in file LTspice `.asc` oppure in output LaTeX/CircuiTikz. E un
riferimento importante perche dimostra che:

- il problema esiste davvero;
- non e banale neppure con LLM;
- la leggibilita umana del circuito e ancora un collo di bottiglia reale.

Per la nostra tesi, pero, Schemato resta piu un confronto che una soluzione da
adottare:

- mira a esportare verso un CAD esterno;
- non e progettato come viewer locale integrato nella web chat;
- non e centrato sul mostrare i risultati `ngspice` della run selezionata.

Fonte:

- <https://arxiv.org/abs/2411.13899>

### Weave

`Weave` e forse il riferimento piu forte e piu vicino alla filosofia di
Experiment 3 sul lato `netlist -> schematico`.

Il lavoro propone:

- conversione deterministica da netlist SPICE a schematico LTspice `.asc`;
- layout a strati;
- verifica round-trip di equivalenza topologica.

Il punto forte qui non e solo il disegno, ma la garanzia che lo schematico
prodotto mantenga davvero la connettivita della netlist di origine.

Questo e molto importante per la nostra tesi, perche rafforza la regola:

```text
correttezza topologica prima della bellezza grafica
```

Differenze rispetto al nostro progetto:

- Weave produce schematici LTspice;
- noi vogliamo un viewer web;
- noi dobbiamo integrare anche tensioni, correnti, transitori, scenari e
  componenti strutturali extra-netlist.

Quindi Weave non sostituisce Experiment 3, ma lo legittima fortemente sul
piano metodologico.

Fonte:

- <https://arxiv.org/abs/2607.03835>

## 6. Viewer e simulatori esistenti

### CircuitJS / Falstad

`CircuitJS1` e il riferimento visuale piu forte per un simulatore circuitale nel
browser:

- UI molto efficace;
- animazioni intuitive;
- feedback visivo immediato;
- integrazione di scope e segnali temporali.

Pero va usato con attenzione:

- e un simulatore completo;
- ha un proprio motore;
- non e `ngspice`;
- il repository e sotto licenza `GPL-2.0`.

Quindi per la tesi la posizione migliore e:

```text
CircuitJS/Falstad = riferimento UX
non = backend di simulazione del progetto
```

Fonte:

- <https://github.com/pfalstad/circuitjs1>

### Qucs-S

`Qucs-S` dimostra che `ngspice` puo stare dietro una GUI unificata moderna.
Questo e utile come argomento a favore della nostra separazione fra:

- motore di simulazione;
- interfaccia grafica.

Tuttavia Qucs-S e un ambiente completo esterno, non un piccolo viewer da
incorporare nella nostra web chat.

Fonte:

- <https://ra3xdh.github.io/>

### Xschem

`Xschem` e molto utile per il flusso:

```text
schema disegnato -> netlist Spice
```

quindi e un riferimento di ambiente EDA, ma non risolve il nostro problema
centrale:

```text
netlist + risultati SPICE -> viewer integrato e comparabile
```

Fonte:

- <https://xschem.sourceforge.io/stefan/index.html>

## 7. Strumenti utili ma non risolutivi

### Lcapy

`Lcapy` e interessante perche puo semi-automatizzare schematici da netlist e
offre analisi simbolica.

E utile come:

- riferimento metodologico;
- supporto per circuiti lineari;
- possibile strumento secondario di confronto.

Non e pero una soluzione diretta per Experiment 3, perche non nasce come
viewer web interattivo grounded sulla singola run `ngspice`.

Fonte:

- <https://lcapy.readthedocs.io/en/latest/>

### Schemdraw

`Schemdraw` e ottimo per produrre schematici puliti da Python. E molto adatto
se vogliamo:

- creare figure statiche;
- generare schematici puliti per documentazione;
- fare un prototipo grafico controllato.

Ma non risolve da solo:

- parsing della netlist;
- layout automatico generale;
- confronto base/scenario;
- overlay di misure `ngspice`.

Fonte:

- <https://schemdraw.readthedocs.io/en/latest/>

## 8. Cosa manca ancora nello stato dell'arte

Il punto piu importante per Experiment 3 e che manca ancora una soluzione
piccola e pulita che combini davvero:

```text
run SPICE selezionata
-> viewer web locale
-> base run e scenario run
-> differenze topologiche visibili
-> valori ngspice sovrapposti
-> componenti strutturali extra-netlist leggibili
```

I lavori e gli strumenti esistenti coprono bene singoli pezzi:

- `immagine -> netlist`;
- `netlist -> schematico CAD`;
- `schematic capture -> netlist`;
- `simulatore browser con motore proprio`.

La combinazione che interessa a noi resta invece poco presidiata:

```text
viewer run-aware, netlist-first, ngspice-grounded, integrato nella web chat
```

Questo e esattamente lo spazio in cui Experiment 3 puo essere interessante e
originale.

## 9. Implicazioni dirette per Experiment 3

Lo stato dell'arte rafforza tre scelte architetturali.

### 1. La netlist della run selezionata deve essere la sorgente primaria

La regola deve essere:

```text
il viewer parte sempre da 07_netlist.cir della run selezionata
```

Questo vale per:

- base run;
- scenari topologici;
- scenari non topologici;
- run `.op`;
- run `.tran`.

### 2. Il viewer deve essere arricchito dal layer strutturale

La netlist da sola non basta sempre. Alcuni elementi importanti per la lettura
umana del circuito non compaiono come dispositivi SPICE attivi:

- connector;
- pin numerati;
- switch aperti non emessi;
- simboli GND multipli;
- componenti strutturali.

Per questo il viewer deve essere arricchito con:

- `03_node_map.json`;
- `04_values_bound.json`;
- `06_component_rules.json`;
- eventualmente `02_normalized_circuit.json`.

### 3. Il contratto dati centrale deve essere un modello intermedio

Il cuore di Experiment 3 non dovrebbe essere l'HTML ma un file tipo:

```text
13_viewer_model.json
```

Questa scelta rende il sistema:

- testabile;
- confrontabile;
- estendibile;
- integrabile sia in HTML locale sia nella web chat.

## 10. Posizionamento metodologico della tesi

La formulazione piu forte e piu pulita del contributo e questa:

```text
Il lavoro non punta principalmente a riconoscere meglio lo schema come immagine.
Punta a trasformare un grafo elettrico gia riconosciuto, ma rumoroso o
incompleto, in un artefatto circuitale eseguibile, verificabile, visualizzabile
e spiegabile.
```

In termini di esperimenti:

- `Experiment 1`: diagnosi con scenari iniziali;
- `Experiment 2`: scenari piu potenti e modifiche controllate della netlist;
- `Experiment 3`: viewer/simulatore visuale grounded sulla netlist della run;
- `Experiment 4`: confronto tra chat guidata e agente autonomo controllato.

In questa progressione, Experiment 3 ha un ruolo molto chiaro:

```text
rendere visibile e confrontabile il comportamento elettrico
che finora esiste soprattutto come file SPICE, stdout e CSV.
```

## 11. Limiti e confini dichiarabili

Lo stato dell'arte suggerisce anche alcuni limiti che conviene dichiarare
esplicitamente nella tesi.

### Limiti realistici

- il viewer non ricostruisce lo schematico originale pixel-perfect;
- alcuni componenti complessi possono essere rappresentati come blocchi;
- la corrente puo essere disponibile solo dove la netlist o i risultati la
  rendono ricostruibile in modo robusto;
- i macromodelli o le approssimazioni SPICE possono limitare la diagnosi;
- la generalizzazione a circuiti molto complessi o industriali resta una
  frontiera aperta.

### Formula consigliata per Experiment 3

```text
Experiment 3 non ricostruisce lo schematico grafico originale.
Costruisce invece una rappresentazione elettricamente equivalente alla netlist
SPICE della run selezionata, arricchita con il contesto strutturale utile alla
diagnosi.
```

## 12. Conclusione finale

Lo stato dell'arte supporta bene una tesi che separi con chiarezza:

- computer vision e graph extraction;
- ricostruzione elettrica;
- generazione e validazione SPICE;
- diagnosi grounded;
- visualizzazione della run simulata.

La zona piu originale e meglio difendibile del progetto non e costruire un
ennesimo simulatore, ma questa combinazione specifica:

```text
graph JSON -> netlist SPICE -> ngspice -> viewer run-aware -> diagnosi AI
```

Con questa impostazione:

- `SINA`, `Netlistify` e `Image2Net` coprono bene il lato image-first;
- `Auto-SPICE`, `SPICEAssistant` e `AMSnet-q` coprono bene il lato
  SPICE-grounded AI;
- `Schemato` e `Weave` coprono bene il problema inverso `netlist -> schematico`;
- `CircuitJS`, `Qucs-S`, `Lcapy`, `Schemdraw` e `Xschem` aiutano a posizionare
  le scelte di tooling.

Il vuoto che resta, e che Experiment 3 puo occupare, e questo:

```text
un viewer nativo, leggero, netlist-first, grounded su ngspice e integrato
nella web chat, capace di mostrare base run e scenario run come circuiti
equivalenti leggibili.
```

## Riferimenti essenziali

- SINA: <https://arxiv.org/abs/2607.01609>
- Netlistify paper: <https://research.nvidia.com/labs/electronic-design-automation/papers/netlistify_mlcad25.pdf>
- Netlistify repository: <https://github.com/NYCU-AI-EDA/Netlistify>
- Image2Net: <https://arxiv.org/html/2508.13157v1>
- Circuit schematic digitization: <https://pubs.aip.org/aip/aml/article/2/1/016109/3132693/Digitizing-images-of-electrical-circuit-schematics>
- Auto-SPICE / Masala-CHAI: <https://arxiv.org/html/2411.14299v1>
- SPICEAssistant: <https://arxiv.org/html/2507.10639v1>
- AMSnet-q: <https://arxiv.org/html/2605.01404v1>
- ngspice: <https://ngspice.sourceforge.io/>
- CircuitJS1: <https://github.com/pfalstad/circuitjs1>
- Qucs-S: <https://ra3xdh.github.io/>
- Lcapy: <https://lcapy.readthedocs.io/en/latest/>
- Schemdraw: <https://schemdraw.readthedocs.io/en/latest/>
- Schemato: <https://arxiv.org/abs/2411.13899>
- Weave: <https://arxiv.org/abs/2607.03835>
- Xschem: <https://xschem.sourceforge.io/stefan/index.html>
