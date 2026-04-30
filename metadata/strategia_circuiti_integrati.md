rei due concetti:

bbox_yolo       = bbox grezzo del componente rilevato
ic_body_bbox    = rettangolo reale del corpo IC
search_bbox     = bbox espanso per cercare fili e testi vicini

Questa distinzione secondo me è importantissima.

Per esempio, nel TDA7000 hai tantissimi pin sopra e sui lati. Se il bbox ingloba anche i condensatori sopra, la ricerca dei pin diventa sporca. Invece se prima trovi il corpo rettangolare reale, poi scansioni solo le quattro fasce attorno al corpo, il problema diventa molto più stabile.

Strategia geometrica per trovare i terminali

Per ogni IC:

Prendi il bbox YOLO.
Raffina il rettangolo del corpo IC cercando linee verticali/orizzontali o il contorno rettangolare.
Crea quattro bande di ricerca:
sinistra;
destra;
alto;
basso.
In ogni banda cerca segmenti di filo che toccano il bordo del corpo.
Ogni punto di contatto diventa un terminale.

In pratica:

lato sinistro  -> cerco fili orizzontali che arrivano al bordo sinistro
lato destro    -> cerco fili orizzontali che partono dal bordo destro
lato superiore -> cerco fili verticali che arrivano al bordo alto
lato inferiore -> cerco fili verticali che partono dal bordo basso

Quindi il terminale non nasce perché “vedo un numero”, ma perché “vedo un filo che entra nel corpo IC”. L’OCR viene dopo, come informazione semantica.

Questa è la parte più importante: geometria prima, OCR dopo.

Perché non partire dall’OCR

L’OCR ti serve, ma non deve decidere da sola se un terminale esiste.

Nei tuoi esempi ci sono tanti testi vicino ai componenti:

NE555;
TDA7000;
1, 2, 3, 4, ecc.;
+12V DC;
Audio out;
No connection;
nomi di componenti vicini tipo R1, C3, D1.

Se usiamo l’OCR per creare terminali rischiamo falsi positivi. Per esempio un numero vicino al chip potrebbe essere il numero del pin, ma potrebbe anche appartenere ad altro. Quindi io farei così:

prima trovo i terminali dai fili
poi associo a ciascun terminale il testo più vicino
Cosa salvare nel JSON

Per ogni terminale IC io salverei più informazioni del solito. Per esempio:

{
  "id": "IC1.pin_3",
  "component_id": "IC1",
  "component_class_name": "Integrated_Circuit",
  "name": "pin_3",
  "x": 742.0,
  "y": 358.0,
  "relative_position": "right",
  "pin_number": "3",
  "pin_label_text": null,
  "detection_method": "ic_wire_contact",
  "confidence": 0.91,
  "ocr_confidence": 0.84
}

E nel componente IC aggiungerei qualcosa tipo:

{
  "instance_id": "IC1",
  "class_name": "Integrated_Circuit",
  "ic_marking": "NE555",
  "ic_marking_confidence": 0.88,
  "body_bbox": [...],
  "bbox": [...]
}

Questo ti prepara già per la fase successiva: agente AI / datasheet / mapping pin number → funzione.

Per esempio:

IC marking: NE555
pin_number: 3

poi in seguito l’agente può dire:

NE555 pin 3 = output

Ma questa cosa la terrei fuori dalla pipeline 01-05 per ora.

OCR: due livelli separati
Io dividerei l’OCR in due compiti.
1. Nome dell’integrato
Cercato dentro il corpo IC, nella zona centrale.
Esempi:
NE555TDA7000TDA1553ADC0804AT89S51CD4017HT8950AHT82V733LM317TLM1875
Qui conviene cercare stringhe alfanumeriche grandi, non singoli numeri.
2. Numero/nome dei pin
Cercato vicino a ogni terminale.
Per esempio, se trovo un terminale sul lato destro, faccio una piccola ROI attorno al terminale, sia dentro sia fuori dal corpo IC, e cerco testo vicino.
Il risultato può essere:
"pin_number": "3"
oppure:
"pin_label_text": "OUT"
o entrambi.

Attenzione ai pin non collegati
Nei diagrammi alcuni pin possono essere indicati ma non collegati, tipo No connection.
Qui dobbiamo decidere una politica.
Per la pipeline topologica io farei inizialmente:
crea terminali IC solo se c'è un filo collegato
Perché il grafo dello script 05 lavora sui collegamenti reali. Lo script 05 infatti prende i terminali stimati e li aggancia allo skeleton dei fili per costruire il grafo finale. 
Però potremmo salvare anche una seconda lista opzionale:
"unwired_pins_detected_by_ocr": [...]
ma non li metterei subito nel grafo.

Modifica importante nello script 04
Quando aggiungiamo gli IC, dobbiamo stare attenti alla maschera.
Lo script 04 maschera i componenti e poi preserva le zone terminali. 
Per gli IC, se mascheriamo tutto il bbox YOLO, rischiamo di cancellare anche i fili vicini o i numeri dei pin. Quindi per gli IC conviene mascherare il body_bbox raffinato, non per forza tutto il bbox.
Quindi idealmente:
bbox          = detection YOLObody_bbox     = corpo reale ICmask_bbox     = body_bbox leggermente espansoterminal_keep = zone dei pin trovati
Questo migliora molto la fase 04.

In sintesi
La pipeline ideale per gli IC secondo me è questa:
01 YOLO   rileva Integrated_Circuit come rettangolo generale02 assign instances   assegna IC1, IC2, ...03 terminal estimation   raffina il corpo IC   cerca contatti filo-corpo sui quattro lati   crea terminali variabili   associa OCR: nome IC + numero pin04 wire extraction   maschera il corpo IC   preserva i terminali trovati05 graph   collega i terminali IC ai fili come per tutti gli altri componenti
La tua idea del bbox espanso è corretta, ma la renderei più robusta così:
non “bbox espanso e qualsiasi pixel nero = terminale”ma“body bbox raffinato + bande laterali + line detector direzionale + OCR associativo”
Secondo me questa è la strada giusta per far funzionare bene NE555, TDA7000, ADC0804, microcontrollori, driver display, amplificatori e IC generici.