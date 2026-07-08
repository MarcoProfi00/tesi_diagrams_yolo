# Template comparabile - Experiment 1 / Experiment 2

Questo file definisce una struttura comune da usare sia per i markdown di
`experiment1` sia per quelli di `experiment2`.

L'obiettivo non e rendere i due esperimenti identici in tutto, ma fare in modo
che abbiano:

- la stessa ossatura logica;
- gli stessi campi minimi confrontabili;
- una parte libera finale per i dettagli specifici del singolo esperimento.

## Principio guida

Le sezioni utili per futuri confronti, score, tabelle o grafici devono stare
sempre nella stessa zona del file e con nomi stabili.

I dettagli piu narrativi o le note storiche specifiche possono vivere dopo,
in sezioni dedicate.

## Ossatura comune consigliata

### 1. Titolo

```text
# a0X - Experiment 1
oppure
# a0X - Experiment 2
```

### 2. Structured experiment record

Questa sezione deve esistere sempre.

Campi minimi consigliati:

```yaml
experiment_id:
batch:
circuit:
status:
included:
excluded_reason:
base_reference:
runtime_experiment_root:
additional_runtime_roots:
primary_primitive:
secondary_primitives:
first_user_prompt:
topological_scenario_proposed_in_first_response:
topological_scenarios_count_first_response:
proposed_scenarios_count_first_response:
executed_scenarios_count:
topological_scenarios_executed_count:
best_outcome_status:
best_scenario_id:
needs_image:
notes_for_results:
```

Note:

- in `experiment1`, `primary_primitive` puo essere `null` oppure indicare la
  famiglia prevalente di scenari non topologici;
- in `experiment1`, `topological_*` puo valere `0` o `false`;
- in `experiment2`, questi campi devono riflettere davvero il ruolo delle
  primitive topologiche o di eccitazione forte.

### 3. Riferimenti

Sezione breve e stabile:

- riferimento base;
- root runtime principale;
- eventuali root runtime secondarie/storiche.

### 4. Obiettivo locale dell'esperimento

Una sezione breve che dica:

- quale domanda locale stiamo testando;
- perche questo circuito e utile;
- qual e il focus dell'esperimento su questo caso.

### 5. Contesto iniziale

Campi stabili:

- base run di riferimento;
- prompt allineato: si/no;
- history/registry attivi: si/no;
- eventuali note preliminari.

### 6. Domanda iniziale

Sempre presente:

```text
### Domanda utente
```

con il testo del sintomo iniziale dato in chat.

### 7. Valutazione della prima risposta

Sempre presente:

- cosa ha capito l'agente;
- quali evidenze ha usato;
- se la prima risposta e convincente;
- se emerge gia una ipotesi topologica o una direzione forte.

### 8. Prima tripletta di scenari proposti

Tabella stabile:

| Scenario | Titolo | Action types | Famiglia | Topologico | Eseguibile | Valutazione |
| --- | --- | --- | --- | --- | --- | --- |

Questa e una delle sezioni piu importanti per confrontare Experiment 1 e
Experiment 2.

### 9. Scenari eseguiti

Tabella stabile:

| Scenario | Actions | Outcome | Evidenza chiave | Valutazione |
| --- | --- | --- | --- | --- |

Se serve, i singoli scenari possono poi avere sottosezioni dedicate sotto la
tabella.

### 10. Cronologia domanda/risposta

Qui documentiamo solo i passaggi davvero significativi:

- domanda utente;
- risposta dell'agente;
- scenario proposto;
- scenario eseguito;
- interpretazione.

Non serve copiare ogni log grezzo: serve una narrazione tecnica confrontabile.

### 11. Cosa abbiamo imparato

Tre sottosezioni stabili:

```text
## Cosa abbiamo imparato

### Sul comportamento dell'agente
### Sulla primitiva o famiglia di scenari
### Sul circuito
```

In `experiment1`, la seconda voce puo riferirsi anche a scenari non topologici.

### 12. Conclusione locale

Sezione breve ma confrontabile:

- il circuito richiedeva o no uno scenario topologico;
- la famiglia di scenari usata e stata utile oppure no;
- quale limite resta aperto.

### 13. Artefatti da citare

Sezione breve e stabile con i file principali.

## Regola pratica

La parte comparabile deve stare nella meta alta del file.

Le note specifiche del singolo esperimento, per esempio:

- dettagli completi della netlist;
- note storiche su una sottofase;
- confronto tra root runtime distinte;
- motivazioni metodologiche piu lunghe;

vanno bene, ma conviene spostarle dopo la parte comparabile oppure in appendice.

## Strategia consigliata di riallineamento

Per allineare i markdown esistenti:

1. non riscrivere subito tutto il contenuto tecnico;
2. portare prima tutti i file sulla stessa ossatura;
3. spostare poi i dettagli gia presenti nelle sezioni nuove;
4. lasciare in appendice o in sezioni dedicate il materiale troppo specifico
   del singolo esperimento.

## Caso pilota consigliato

Usare `a01` come primo caso pilota, perche:

- ha sia `experiment1` sia `experiment2` gia ricchi;
- in `experiment2` contiene anche una sottofase storica da trattare con cura;
- mostra bene la differenza tra scenario non topologico di isolamento e
  scenario topologico/semantico.
