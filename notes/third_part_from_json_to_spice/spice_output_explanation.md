# Understanding ngspice Output

Questo documento serve come nota di lavoro per leggere gli output prodotti da
ngspice. Non e parte della pipeline: e una guida per noi.

L'esempio principale e `a01`, eseguito con:

```powershell
python scripts\pipeline_2.0\run_pipeline2.py --batch batchA --circuits a01 --run-spice --ngspice-executable ngspice_con
```

Gli output SPICE si trovano in:

```text
outputs/pipeline2.0/batchA/a01/
```

I file importanti sono:

```text
07_netlist.cir
08_spice_run.json
08_ngspice_stdout.txt
08_ngspice_stderr.txt
```

## File principali

### 07_netlist.cir

E la netlist SPICE generata dalla pipeline.

Per `a01`:

```spice
VVCC N001 0 DC 5
Rlamp13_1 N004 0 50
Dled12_1 N005 0 LED_RED
Rresistor22_1 N002 N004 1000
Rresistor22_2 N001 N005 220
* switch25.1 open: not emitted

.model LED_RED D

.op
.end
```

Questa netlist dice a ngspice quali componenti ci sono, tra quali nodi sono
collegati e quale analisi deve eseguire.

In questo caso viene eseguita solo:

```spice
.op
```

cioe operating point analysis: analisi statica DC.

### 08_spice_run.json

E il report della pipeline sul processo ngspice.

Campi principali:

```json
{
  "status": "success",
  "exit_code": 0,
  "stdout_path": ".../08_ngspice_stdout.txt",
  "stderr_path": ".../08_ngspice_stderr.txt"
}
```

Interpretazione:

- `status: success`: ngspice e stato eseguito correttamente.
- `exit_code: 0`: il processo e terminato senza errore.
- `stdout_path`: file con risultati e log normali.
- `stderr_path`: file con errori tecnici o diagnostici critici.

### 08_ngspice_stdout.txt

Contiene l'output normale di ngspice.

Qui troviamo:

- informazioni sull'analisi;
- tensioni dei nodi;
- correnti delle sorgenti;
- dettagli dei modelli;
- correnti e potenze dei componenti;
- tempi di esecuzione.

### 08_ngspice_stderr.txt

Contiene eventuali errori tecnici.

Se e vuoto, di solito e un buon segno: significa che ngspice non ha scritto
errori su `stderr`.

Per `a01`, `stderr` e vuoto.

## Come leggere stdout

### Intestazione

Esempio:

```text
Note: No compatibility mode selected!

Circuit: * pipeline2.0 netlist

Doing analysis at TEMP = 27.000000 and TNOM = 27.000000

Using SPARSE 1.3 as Direct Linear Solver
```

Significato:

- ngspice ha letto la netlist.
- Sta eseguendo l'analisi a temperatura nominale 27 C.
- Usa un solver numerico per risolvere il circuito.

Questa parte non e il risultato elettrico vero e proprio, ma conferma che
l'analisi e partita.

### No. of Data Rows

Esempio:

```text
No. of Data Rows : 1
```

Con `.op` ci aspettiamo una sola riga di risultati, perche ngspice calcola un
solo punto operativo statico.

Se facessimo una `.tran`, ci sarebbero molte righe, una per ogni istante
temporale.

## Tensioni dei nodi

Esempio `a01`:

```text
Node                                  Voltage
----                                  -------
n002                             0.000000e+00
n005                             7.318156e-01
n004                             0.000000e+00
n001                             5.000000e+00
```

Traduzione:

```text
N001 = 5 V
N005 = 0.7318156 V
N002 = 0 V
N004 = 0 V
```

Nota: ngspice stampa i nomi dei nodi in minuscolo (`n001`), ma sono gli stessi
nodi della netlist (`N001`).

Per capire cosa rappresentano questi nodi bisogna guardare:

```text
03_node_map.json
```

Per `a01`:

```text
N001 = connector5.1_pin1 + resistor22.2_t1
N002 = connector5.1_pin2 + resistor22.1_t1
N004 = lamp13.1_t1 + resistor22.1_t2
N005 = led12.1_anode + resistor22.2_t2
0    = ground
```

Quindi:

- `N001 = 5 V`: il pin1 del connector e alimentato a 5 V.
- `N005 = 0.7318 V`: nodo tra resistenza da 220 ohm e LED.
- `N002 = 0 V`: pin2 del connector non alimentato nella simulazione base.
- `N004 = 0 V`: nodo tra resistenza da 1k e lampada.

## Corrente delle sorgenti

Esempio:

```text
Source Current
vvcc#branch                      -1.94008e-02
```

Significa che la sorgente `VVCC` ha una corrente di circa:

```text
-0.0194008 A
```

Il segno negativo e normale nella convenzione SPICE delle sorgenti di tensione.
In pratica indica che la sorgente sta erogando corrente al circuito.

Valore assoluto:

```text
0.0194008 A = 19.4 mA
```

## Modelli

ngspice stampa anche i parametri dei modelli.

Esempio:

```text
Diode models (Junction Diode model)
model led_red
```

Questo non e un errore. Significa che il componente `Dled12_1` usa il modello
`LED_RED`, che nella netlist e definito come:

```spice
.model LED_RED D
```

Per ora il modello e molto semplice. Piu avanti potremo sostituirlo con modelli
piu realistici.

## Risultati del LED

Esempio:

```text
Diode: Junction Diode model
device              dled12_1
vd              0.731816
id             0.0194009
```

Significato:

- `vd`: tensione sul diodo/LED.
- `id`: corrente nel diodo/LED.

Per `a01`:

```text
LED voltage = 0.731816 V
LED current = 0.0194009 A = 19.4 mA
```

Questo e coerente con il ramo:

```text
5V -> 220 ohm -> LED -> GND
```

Calcolo approssimato:

```text
(5 V - 0.7318 V) / 220 ohm = 0.0194 A
```

Quindi il ramo LED e alimentato e conduce corrente.

## Risultati delle resistenze

Esempio:

```text
Resistor: Simple linear resistor
device         rresistor22_2         rresistor22_1             rlamp13_1
resistance                   220                  1000                    50
i                      0.0194008                     0                     0
p                      0.0828064                     0                     0
```

Significato:

- `rresistor22_2`: resistenza da 220 ohm.
- `rresistor22_1`: resistenza da 1k.
- `rlamp13_1`: lampada modellata come resistenza equivalente da 50 ohm.
- `i`: corrente nel componente.
- `p`: potenza dissipata.

Per `a01`:

```text
resistor22.2 current = 19.4 mA
resistor22.1 current = 0 A
lamp13.1 current = 0 A
```

Questo dice che:

- il ramo LED conduce;
- il ramo lampada non conduce;
- la lampada non e alimentata nello scenario base.

## Risultati della sorgente

Esempio:

```text
Vsource: Independent voltage source
device vvcc
dc 5
i -0.0194008
p -0.0970042
```

Significato:

- `vvcc`: sorgente da 5 V.
- `i`: corrente della sorgente.
- `p`: potenza associata alla sorgente secondo la convenzione SPICE.

Il segno negativo della potenza indica che la sorgente sta fornendo energia al
circuito.

Valore:

```text
5 V * 0.0194008 A = circa 0.097 W
```

## Interpretazione di a01

Per `a01`, ngspice conferma che la simulazione e riuscita.

Il risultato elettrico e:

```text
N001 = 5 V
N005 = 0.7318 V
LED current = 19.4 mA
Lamp current = 0 A
```

Quindi:

- il ramo LED e alimentato;
- il LED conduce corrente;
- il ramo lampada non e alimentato;
- la lampada resta spenta nello scenario base.

Guardando l'immagine del circuito:

```text
J2 pin1 -> 220R -> LED -> GND
J2 pin2 -> 1K -> Lamp -> GND
J2 pin3 -> switch EN -> GND
J2 pin4 -> GND
```

Nel file valori abbiamo una supply su:

```text
connector5.1_pin1
```

Quindi solo il ramo collegato a `pin1` riceve 5 V nella simulazione base.

Il ramo lampada parte da:

```text
connector5.1_pin2
```

ma `pin2` non ha una sorgente nella netlist base. Per questo:

```text
N002 = 0 V
N004 = 0 V
lamp current = 0 A
```

Questo risultato e coerente con la netlist generata.

## Quando un risultato e andato a buon fine

Una simulazione e tecnicamente riuscita quando:

```text
08_spice_run.json -> status = success
08_spice_run.json -> exit_code = 0
08_ngspice_stderr.txt -> vuoto o senza errori critici
08_ngspice_stdout.txt -> contiene risultati dell'analisi
```

Per `a01`, tutte queste condizioni sono vere.

## Attenzione: riuscito non significa sempre utile

Una simulazione puo terminare correttamente ma avere poco significato per il
problema dell'utente.

Esempio:

```text
ngspice success
lamp current = 0 A
```

Questo non e un errore tecnico. E un risultato utile: ci dice che, nello
scenario simulato, la lampada non riceve alimentazione.

La diagnosi o la proposta di scenari alternativi verra fatta piu avanti da un
report o da un agente, non direttamente da ngspice.

## Glossario minimo

```text
stdout
```

Output normale del programma. Qui ngspice scrive risultati e log.

```text
stderr
```

Output degli errori. Se e vuoto, di solito non ci sono errori tecnici.

```text
exit_code
```

Codice di uscita del processo. `0` significa successo.

```text
.op
```

Operating point analysis. Calcola tensioni e correnti statiche DC.

```text
node voltage
```

Tensione di un nodo rispetto a massa SPICE `0`.

```text
branch current
```

Corrente in un ramo o in una sorgente.

```text
device current
```

Corrente calcolata dentro un componente.

```text
model
```

Descrizione SPICE del comportamento di un componente non puramente resistivo,
per esempio un diodo o un transistor.

