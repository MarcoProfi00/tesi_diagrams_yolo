# Caption figure principali

## fig01_score_medio_per_modello

Figura 1 - Score medio per modello sui circuiti analizzati. Il grafico riporta il punteggio medio assegnato dal judge a ciascun modello, aggregando tutte le run disponibili e considerando entrambe le modalita di input. I modelli sono ordinati dal migliore al peggiore rispetto allo score medio. Un valore piu alto indica una migliore capacita diagnostica complessiva.

## fig02_score_modello_input_type

Figura 2 - Effetto dell'immagine per modello. Il grafico collega, per ciascun modello, lo score medio ottenuto con JSON + datasheet e con JSON + immagine + datasheet. Lo spostamento verso destra indica un miglioramento con l'aggiunta dell'immagine; lo spostamento verso sinistra indica un peggioramento. Le etichette numeriche riportano il delta tra le due modalita, rendendo immediato capire quali modelli beneficiano dell'informazione visiva e quali no.

## fig03_delta_immagine_per_circuito

Figura 3 - Variazione dello score con l'aggiunta dell'immagine per circuito. Le barre verdi indicano circuiti in cui JSON + immagine + datasheet migliora lo score medio rispetto a JSON + datasheet; le barre rosse indicano circuiti in cui l'immagine peggiora la prestazione media. La linea orizzontale a zero separa i miglioramenti dai peggioramenti e permette di vedere che l'effetto dell'immagine dipende dal circuito, non e sistematico.

## fig04_score_medio_per_circuito

Figura 4 - Score medio per circuito. Il grafico ordina i circuiti dal punteggio medio piu alto al piu basso, aggregando tutti i modelli e le due modalita di input. Un valore alto indica un caso mediamente piu semplice per i modelli; un valore basso evidenzia un circuito piu critico, con diagnosi meno immediata o maggiore ambiguita.

## fig05_heatmap_modello_circuito

Figura 5 - Robustezza dei modelli sui diversi circuiti. La heatmap mostra lo score medio ottenuto da ciascun modello su ciascun circuito, aggregando le due modalita di input. Le righe sono ordinate dal modello con score medio complessivo piu alto a quello piu basso, mentre le colonne seguono la difficolta media dei circuiti. Il grafico permette di vedere se un modello e stabile su piu circuiti o se crolla su casi specifici.

## fig06_top1_top3_accuracy_modello

Figura 6 - Accuratezza Top-1 e Top-3 per modello. Il grafico confronta, per ciascun modello, la percentuale di diagnosi corrette al primo tentativo (Top-1) e la percentuale di casi in cui la causa corretta compare almeno tra le prime tre ipotesi (Top-3). Una Top-1 elevata indica maggiore affidabilita nella diagnosi principale; una Top-3 elevata indica utilita come supporto al troubleshooting anche quando la causa corretta non viene messa al primo posto.

## fig07_errori_gravi_medi_per_modello

Figura 7 - Errori gravi medi per modello. Il grafico riporta il numero medio di errori gravi commessi da ciascun modello nelle run valutate dal judge. Valori piu bassi indicano maggiore affidabilita pratica; valori piu alti segnalano un rischio maggiore di indicazioni diagnostiche scorrette o fuorvianti.

## fig08_score_vs_costo

Figura 8 - Compromesso tra score medio e costo per diagnosi. Il costo e mostrato in USD reali, senza scala logaritmica. I modelli sono divisi in due pannelli con la stessa scala verticale: a sinistra la fascia economica, a destra la fascia alta. In questo modo il grafico mantiene leggibili le differenze tra modelli economici senza nascondere il costo molto piu alto del modello di fascia superiore.

## fig09_costo_medio_per_modello

Figura 9 - Costo medio del modello per diagnosi. Il grafico riporta il costo medio stimato del solo modello generativo per ciascuna diagnosi, escludendo il costo del judge. I modelli sono ordinati dal meno costoso al piu costoso, cosi da rendere immediato il confronto economico diretto tra le diverse alternative.
