Ti fornisco il JSON topologico di un circuito estratto automaticamente da un diagramma elettrico.

Il JSON contiene:
- componenti;
- terminali;
- grafo dei collegamenti tra terminali;
- eventuali stati dei componenti, come switch open/closed;
- eventuali warning della pipeline.

Scenario:
Il percorso principale del circuito non conduce come previsto.

Componenti o terminali di interesse: Non specificati. Devi individuarli analizzando il JSON.

Obiettivo:
Analizza SOLO il JSON e produci una diagnosi topologica del problema.  
Non usare immagini e non assumere informazioni non presenti nel JSON.

Regole obbligatorie:
- non usare immagini;
- non inventare valori elettrici non presenti;
- non inventare collegamenti non presenti;
- non assumere che un collegamento esista se non compare nel grafo;
- se qualcosa non e' deducibile dal JSON, scrivilo esplicitamente;
- distingui chiaramente tra:
  - deduzione certa dal JSON;
  - ipotesi plausibile;
  - informazione non deducibile;
- considera gli stati di switch/breaker separatamente dalla sola connettivita' dei fili;
- non assumere automaticamente che piu' simboli GND siano lo stesso nodo, a meno che il JSON lo renda esplicito;
- usa anche eventuali warning della pipeline, se presenti.

Output:
Produci esclusivamente un **file Markdown**.  
Non aggiungere testo introduttivo, commenti fuori dal report o spiegazioni esterne.  
Il report deve iniziare direttamente con:

# Diagnosi del problema

Usa obbligatoriamente queste sezioni:

# Diagnosi del problema

## 1. Sintomo
Riporta il sintomo dichiarato.

## 2. Componente coinvolto
Indica il componente o terminale di interesse e i suoi terminali rilevanti.

## 3. Nodi coinvolti
Ricostruisci solo i nodi rilevanti per il componente indicato e per il sintomo.
Indica quali terminali risultano collegati tra loro secondo il grafo.

## 4. Percorso atteso
Descrivi quale percorso elettrico sarebbe atteso per il funzionamento del componente, restando nei limiti delle informazioni presenti nel JSON.

## 5. Analisi del JSON
Verifica se il percorso e':
- completo;
- interrotto;
- cortocircuitato;
- ambiguo/non determinabile.

Usa esplicitamente i collegamenti del grafo e gli eventuali warning.

## 6. Possibili cause
Elenca le cause compatibili con il JSON, separando:
- cause certe dal JSON;
- ipotesi plausibili;
- informazioni non deducibili.

## 7. Diagnosi finale
Concludi con una diagnosi sintetica e motivata.
La diagnosi deve indicare se il problema e' deducibile dal JSON oppure no.

## 8. Soluzioni / azioni correttive
Proponi solo azioni correttive coerenti con il JSON.
Non proporre sostituzioni di componenti o valori elettrici se non sono deducibili.
Se il problema e' topologico, indica quali collegamenti andrebbero verificati o ripristinati.

Ecco il JSON:
[INCOLLA QUI IL JSON]
