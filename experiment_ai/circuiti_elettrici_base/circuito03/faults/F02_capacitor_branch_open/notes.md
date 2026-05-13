# Notes - C03_F02_capacitor_branch_open

## 1. Informazioni generali

| Campo | Valore |
|---|---|
| Circuito | C03_switch_capacitive_network |
| Fault ID | F02_capacitor_branch_open |
| Tipo guasto | open_connection |
| Immagine modificata | sì |
| Modifica apportata | Cancellato un collegamento su un ramo capacitivo collegato al nodo centrale |
| Scenario | Il nodo centrale non è più accoppiato correttamente |
| Componenti target | Non forniti nel prompt; target atteso `polarized_capacitor20.2` |
| Terminali rilevanti | Non forniti nel prompt; attesi `polarized_capacitor20.2_positive`, `polarized_capacitor20.2_negative`, `polarized_capacitor20.4_positive`, `terminal26.3_t1` |
| Diagnosi attesa | Ramo capacitivo interrotto: `polarized_capacitor20.2_positive` risulta scollegato |
| Pipeline capture | 2/2 |

## 2. Verifica pipeline

| Criterio | Esito |
|---|---|
| Componente target rilevato | sì, `polarized_capacitor20.2` |
| Terminale target presente nel JSON | sì, `polarized_capacitor20.2_positive` |
| Componente vicino rilevato | sì, `polarized_capacitor20.4` e `terminal26.3` |
| Terminale vicino rilevante | sì, `polarized_capacitor20.2_negative`, `polarized_capacitor20.4_positive`, `terminal26.3_t1` |
| Terminali rilevanti presenti nel JSON | sì |
| Guasto rappresentato nel grafo | sì, `polarized_capacitor20.2_positive` è senza connessioni |
| Warning coerenti | sì, `polarized_capacitor20.2_positive` compare in `unconnected_terminals` |
| Test valutabile lato AI | sì |

## 3. Motivazione Pipeline capture
Il guasto è chiaramente rappresentato nel JSON.

Il terminale `polarized_capacitor20.2_positive` risulta senza connessioni nel grafo:
- polarized_capacitor20.2_positive: []
Inoltre lo stesso terminale compare nei warning della pipeline:
unconnected_terminals:
- polarized_capacitor20.2_positive

L’altro terminale del condensatore, polarized_capacitor20.2_negative, non è scollegato: risulta collegato al nodo formato da:
- polarized_capacitor20.2_negative
- polarized_capacitor20.4_positive
- terminal26.3_t1
Questo indica che il ramo capacitivo non è completamente assente, ma è interrotto su un solo lato. In particolare, polarized_capacitor20.2 non collega più il nodo centrale al nodo laterale/ramo sinistro previsto.

## 4. Expected diagnosis
Il modello dovrebbe diagnosticare un’interruzione topologica su un ramo capacitivo.

In particolare, dovrebbe rilevare autonomamente che:

- polarized_capacitor20.2_positive è scollegato;
- polarized_capacitor20.2_positive compare nei warning unconnected_terminals;
- polarized_capacitor20.2_negative resta collegato al nodo centrale con polarized_capacitor20.4_positive e terminal26.3_t1;
quindi il condensatore polarized_capacitor20.2 non collega più correttamente il nodo centrale al ramo laterale;
- il sintomo “il nodo centrale non è più accoppiato correttamente” è compatibile con questo ramo capacitivo interrotto.

La risposta corretta deve distinguere questo guasto da altri stati presenti nel JSON, per esempio lo switch switch25.1 in stato open, che è una condizione rilevante ma non il guasto principale atteso per questo fault.

## 5. Risultati modelli

| Modello         | Sintesi risultato | Totale AI /10 | End-to-end /12 | Giudizio |
| --------------- | ----------------- | ------------: | -------------: | -------- |
| GPT-5.4 | Con prompt generale individua autonomamente `polarized_capacitor20.2` come componente critico, rileva `polarized_capacitor20.2_positive` scollegato e diagnostica l’interruzione del ramo capacitivo del nodo centrale. Distingue correttamente questo guasto dallo switch `open`. | 10 | 12 | Diagnosi corretta |
| GPT-5.3 Instant | Con prompt generale individua autonomamente `polarized_capacitor20.2_positive` come terminale scollegato e diagnostica l’interruzione del ramo capacitivo. Presenta una lieve imprecisione nella definizione del nodo centrale coinvolto. | 9 | 11 | Diagnosi corretta con lieve imprecisione topologica |
| GPT-5.2 Instant | Con prompt generale individua autonomamente `polarized_capacitor20.2` come componente critico, rileva `polarized_capacitor20.2_positive` scollegato e diagnostica l’interruzione del ramo capacitivo. Presenta una lieve imprecisione nella definizione del nodo centrale coinvolto. | 9 | 11 | Diagnosi corretta con lieve imprecisione topologica |


## 6. Osservazioni
Questo test è adatto alla diagnosi da JSON perché il guasto è rappresentato direttamente dal grafo e dai warning: un terminale di un condensatore risulta isolato.

A differenza di C03_F01_switch_open_state, qui il problema non dipende dallo stato open dello switch, ma da un terminale scollegato in un ramo capacitivo.

Il caso è utile perché verifica se il modello riesce a:

- individuare autonomamente un terminale scollegato;
- collegarlo al sintomo generale;
- non confondere il fault principale con lo stato aperto dello switch;
- distinguere tra interruzione topologica e informazioni operative non deducibili.

## GPT 5.4

GPT-5.4 fornisce una diagnosi corretta. Anche senza ricevere un componente target esplicito, individua autonomamente `polarized_capacitor20.2` come componente più direttamente coinvolto nel problema di accoppiamento del nodo centrale.

Il modello ricostruisce correttamente il nodo centrale, formato da:

- `polarized_capacitor20.2_negative`;
- `polarized_capacitor20.4_positive`;
- `terminal26.3_t1`.

Rileva inoltre che `polarized_capacitor20.2_positive` ha lista connessioni vuota e compare nei warning `unconnected_terminals`. Questo è coerente con un ramo capacitivo interrotto: il condensatore `polarized_capacitor20.2` resta collegato al nodo centrale solo da un lato, ma non collega più correttamente il nodo centrale a un ramo laterale.

Il report è anche prudente: segnala che non è deducibile dal JSON quale nodo laterale avrebbe dovuto raggiungere `polarized_capacitor20.2_positive`. Inoltre distingue correttamente questo fault dallo switch `switch25.1` in stato `open`, che è una condizione presente nel JSON ma non spiega direttamente il guasto capacitivo atteso.

### Valutazione manuale GPT-5.4 - C03_F02_capacitor_branch_open

| Criterio | Punteggio | Motivazione |
|---|---:|---|
| Sintomo capito | 2 | Capisce correttamente che il problema riguarda il mancato accoppiamento del nodo centrale ai rami laterali. |
| Uso corretto JSON | 2 | Usa correttamente grafo, terminali e warning `unconnected_terminals`, senza usare immagini o inventare collegamenti. |
| Ricostruzione topologica | 2 | Ricostruisce correttamente il nodo centrale con `polarized_capacitor20.2_negative`, `polarized_capacitor20.4_positive` e `terminal26.3_t1`, e identifica `polarized_capacitor20.2_positive` come terminale isolato. |
| Guasto individuato | 2 | Individua autonomamente il guasto atteso: ramo capacitivo interrotto su `polarized_capacitor20.2_positive`. |
| Limiti / no allucinazioni | 2 | Non inventa valori elettrici o nodi mancanti; distingue deduzioni certe, ipotesi plausibili e informazioni non deducibili. |

**Totale AI:** 10/10  
**Pipeline capture:** 2/2  
**End-to-end:** 12/12  
**Giudizio:** Diagnosi corretta.

## GPT 5.3 Instant

GPT-5.3 Instant fornisce una diagnosi sostanzialmente corretta. Anche senza ricevere un componente target esplicito, individua autonomamente `polarized_capacitor20.2_positive` come terminale completamente scollegato e lo collega al warning `unconnected_terminals`.

Il modello riconosce correttamente che il ramo associato a `polarized_capacitor20.2` è problematico: un terminale del condensatore è isolato, mentre l’altro lato appartiene al nodo formato da:

- `polarized_capacitor20.2_negative`;
- `polarized_capacitor20.4_positive`;
- `terminal26.3_t1`.

La diagnosi finale è coerente con il fault atteso: il mancato accoppiamento del nodo centrale ai rami laterali è compatibile con l’interruzione del ramo capacitivo su `polarized_capacitor20.2_positive`.

È presente però una lieve imprecisione topologica: il modello chiama “nodo centrale superiore” un nodo diverso e descrive il nodo `polarized_capacitor20.2_negative` / `polarized_capacitor20.4_positive` / `terminal26.3_t1` come sottorete isolata. Nel nostro expected, invece, questo è il nodo centrale capacitivo coinvolto nel guasto. L’imprecisione non compromette l’individuazione del fault principale.

### Valutazione manuale GPT-5.3 Instant - C03_F02_capacitor_branch_open

| Criterio | Punteggio | Motivazione |
|---|---:|---|
| Sintomo capito | 2 | Capisce che il problema riguarda il mancato accoppiamento del nodo centrale ai rami laterali. |
| Uso corretto JSON | 2 | Usa correttamente grafo e warning `unconnected_terminals`, senza usare immagini o inventare collegamenti. |
| Ricostruzione topologica | 1 | Individua il terminale isolato e i nodi principali, ma interpreta in modo leggermente impreciso il nodo centrale capacitivo coinvolto. |
| Guasto individuato | 2 | Individua autonomamente il guasto atteso: `polarized_capacitor20.2_positive` scollegato e ramo capacitivo interrotto. |
| Limiti / no allucinazioni | 2 | Non inventa valori elettrici o collegamenti mancanti; distingue correttamente deduzioni certe, ipotesi e informazioni non deducibili. |

**Totale AI:** 9/10  
**Pipeline capture:** 2/2  
**End-to-end:** 11/12  
**Giudizio:** Diagnosi corretta con lieve imprecisione topologica.

## GPT 5.2 Instant

GPT-5.2 Instant fornisce una diagnosi sostanzialmente corretta. Anche senza ricevere un componente target esplicito, individua autonomamente `polarized_capacitor20.2` come componente maggiormente coinvolto nel problema.

Il modello rileva correttamente che:

- `polarized_capacitor20.2_positive` è completamente scollegato;
- il terminale compare nei warning `unconnected_terminals`;
- `polarized_capacitor20.2_negative` è collegato al nodo formato da `polarized_capacitor20.4_positive` e `terminal26.3_t1`.

La diagnosi finale è coerente con il fault atteso: il nodo centrale non è più accoppiato correttamente perché il ramo capacitivo associato a `polarized_capacitor20.2` è interrotto su un lato.

È presente però una lieve imprecisione topologica: il modello descrive il nodo `polarized_capacitor20.2_negative` / `polarized_capacitor20.4_positive` / `terminal26.3_t1` come nodo laterale isolato e afferma che nessuno dei due terminali di `polarized_capacitor20.2` è collegato ai nodi centrali. Nel nostro expected, invece, quel nodo è proprio il nodo centrale capacitivo coinvolto nel guasto. L’imprecisione non compromette l’individuazione del terminale scollegato e della causa principale.

### Valutazione manuale GPT-5.2 Instant - C03_F02_capacitor_branch_open

| Criterio | Punteggio | Motivazione |
|---|---:|---|
| Sintomo capito | 2 | Capisce che il problema riguarda il mancato accoppiamento del nodo centrale ai rami laterali. |
| Uso corretto JSON | 2 | Usa correttamente grafo e warning `unconnected_terminals`, senza usare immagini o inventare collegamenti. |
| Ricostruzione topologica | 1 | Individua il terminale isolato e i nodi principali, ma interpreta in modo leggermente impreciso il nodo centrale capacitivo coinvolto. |
| Guasto individuato | 2 | Individua autonomamente il guasto atteso: `polarized_capacitor20.2_positive` scollegato e ramo capacitivo interrotto. |
| Limiti / no allucinazioni | 2 | Non inventa valori elettrici o collegamenti mancanti; distingue correttamente deduzioni certe, ipotesi e informazioni non deducibili. |

**Totale AI:** 9/10  
**Pipeline capture:** 2/2  
**End-to-end:** 11/12  
**Giudizio:** Diagnosi corretta con lieve imprecisione topologica.
