Ti fornisco il JSON topologico di un circuito estratto automaticamente da un diagramma elettrico.

Il JSON contiene:
- componenti
- terminali
- grafo dei collegamenti tra terminali
- eventuali stati dei componenti, come switch open/closed
- eventuali warning della pipeline

Scenario:
LED e lampada si attivano insieme, ma dovrebbero attivarsi singolarmente.


Componente o terminale di interesse:
[INSERISCI ID LETTO DALLA DEBUG IMAGE]

Voglio che tu analizzi SOLO il JSON e faccia diagnosi del problema.

Regole:
- non usare immagini;
- non inventare valori elettrici non presenti;
- non inventare collegamenti non presenti;
- se qualcosa non è deducibile dal JSON, scrivilo esplicitamente;
- distingui tra deduzione certa dal JSON, ipotesi plausibile e informazione non deducibile;
- considera gli stati di switch/breaker separatamente dalla sola connettività dei fili;
- non assumere automaticamente che più simboli GND siano lo stesso nodo, a meno che il JSON lo renda esplicito.

Produci markdown con sezioni:
- Sintomo
- Componente coinvolto
- Nodi coinvolti
- Percorso atteso
- Analisi del JSON
- Possibili cause
- Diagnosi finale
- Limiti dell’analisi

Ecco il JSON:
[JSON]