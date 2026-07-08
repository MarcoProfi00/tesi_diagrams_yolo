# Batch A - Experiment 2

Questo file e la regia manuale dell'Esperimento 2 della Pipeline 2.0.

Experiment 2 non riscrive tutta l'analisi di Experiment 1. Parte dalla base gia
studiata in:

```text
experiment_ai/pipeline2_spice_analysis/batchA/experiment1/
```

e documenta soprattutto:

- scenari piu forti che modificano in modo controllato la netlist SPICE;
- comportamento dell'agente dopo l'allineamento del prompt;
- esecuzione reale degli scenari in `experiment2`;
- conclusioni comparabili tra circuiti;
- struttura utile per futuri punteggi, tabelle e grafici.

## Obiettivo

Experiment 2 serve a verificare se la Pipeline 2.0 riesce a proporre ed
eseguire scenari controllati piu forti rispetto a Experiment 1, soprattutto
quando questi scenari cambiano la netlist SPICE in modo utile e confrontabile.

Primitive di riferimento:

```text
Scenari controllati che cambiano la netlist:
- connect_nodes
- feed_nodes_from_source_node
- add_voltage_source_between_nodes
```

Il focus operativo si e sviluppato in sottofasi successive:

```text
1. connect_nodes
2. feed_nodes_from_source_node
3. add_voltage_source_between_nodes
```

Situazione attuale sul Batch A:

- `connect_nodes` e chiusa sui casi `a01`, `a02`, `a09`, `a10`;
- `feed_nodes_from_source_node` e chiusa sui casi `a01`, `a09`, `a10`;
- `add_voltage_source_between_nodes` e chiusa sui casi `a05`, `a07`;
- `a03` resta escluso per ora;
- `a04`, `a06`, `a08` restano casi non ancora aperti in Experiment 2 e non
  appaiono prioritari per nuove primitive topologiche semplici.

Quindi questo README non descrive piu una fase di implementazione iniziale delle
primitive, ma una fase gia consolidata su tre famiglie di scenari che
modificano la netlist in modo controllato.

## Fonti da considerare autorevoli

Per Experiment 2 conviene distinguere bene tra:

1. artefatti grezzi di runtime;
2. documentazione manuale interpretativa.

Artefatti grezzi ufficiali:

```text
outputs/pipeline2.0/<batch>/experiment2/<circuit>/
outputs/pipeline2.0/<batch>/experiment2/<circuit>/experiment2_chat/
outputs/pipeline2.0/<batch>/experiment2/<circuit>/scenarios/
```

Quando una sottofase viene tenuta separata, la stessa struttura puo comparire
anche in una root dedicata, per esempio:

```text
outputs/pipeline2.0/<batch>/experiment2_feed_nodes/<circuit>/
outputs/pipeline2.0/<batch>/experiment2_feed_nodes/<circuit>/experiment2_chat/
outputs/pipeline2.0/<batch>/experiment2_feed_nodes/<circuit>/scenarios/
```

In particolare:

```text
10_diagnostic_context.json
11_agent_prompt_chat.md
11_agent_response_chat.md
experiment2_chat/chat_history.json
experiment2_chat/chat_history.md
experiment2_chat/scenario_registry.json
experiment2_chat/scenario_registry.md
scenarios/<scenario_id>/
```

Questa cartella `experiment_ai/.../experiment2/` contiene invece note manuali:

- sintesi;
- interpretazione;
- confronto tra circuiti;
- preparazione di risultati futuri per tabelle e grafici.

Quindi i markdown qui dentro non devono duplicare tutti i log. Devono
riassumerli in forma leggibile e confrontabile.

Lo stile consigliato resta quello gia usato in Experiment 1:

- domanda utente;
- risposta dell'agente;
- scenario proposto;
- scenario eseguito;
- interpretazione del risultato.

In questo modo i file restano leggibili anche come narrazione tecnica, non solo
come raccolta di metriche.

## Regola di documentazione

Per ogni circuito di Experiment 2:

- non ripetere tutta l'analisi base gia presente in Experiment 1;
- linkare sempre il markdown di Experiment 1 come riferimento base;
- documentare solo il delta rilevante per Experiment 2;
- mantenere campi stabili che in futuro possano essere trasformati in score.

## Stato batch-level

| Circuito | Incluso | Stato | Primitiva focus | Riferimento base | Nota breve |
| --- | --- | --- | --- | --- | --- |
| `a01` | si | completed | `connect_nodes` / `feed_nodes_from_source_node` | `../experiment1/a01.md` | Caso chiuso su due sottofasi: `connect_nodes N001 -> N002` valida la continuita mancante, poi `feed_nodes_from_source_node N001 -> N002` riformula la stessa evidenza come propagazione dal nodo sorgente vivo. |
| `a02` | si | completed | `connect_nodes` | `../experiment1/a02.md` | Caso chiuso: `connect_nodes N002 -> N004` attiva il ramo resistivo e la corrente di batteria. |
| `a03` | no | excluded_for_now | - | `../experiment1/a03.md` | Caso image-assisted troppo complesso per la fase iniziale di Experiment 2. |
| `a04` | si | not started | tbd | `../experiment1/a04.md` | Caso analogico gia eccitato; non prioritario per ulteriori primitive topologiche semplici. |
| `a05` | si | completed | `add_voltage_source_between_nodes` | `../experiment1/a05.md` | Caso chiuso: la nuova primitiva alimenta correttamente `VMON_INPUT` (`N003`) verso massa e localizza il sintomo come mancanza di eccitazione del circuito base; la chiusura di `TEST` resta secondaria. |
| `a06` | si | not started | tbd | `../experiment1/a06.md` | Caso analogico gia eccitato; piu adatto a scenari di bias, ampiezza o dinamica che a nuove primitive topologiche. |
| `a07` | si | completed | `add_voltage_source_between_nodes` | `../experiment1/a07.md` | Caso chiuso: il ramo LED si attiva quando `PWR` (`N002`) viene alimentato, mentre il ramo `VAC` si attiva separatamente quando viene eccitato `AC_INPUT` (`N001`); la netlist base risulta inattiva soprattutto per mancanza di eccitazione sugli ingressi esterni. |
| `a08` | si | not started | tbd | `../experiment1/a08.md` | Caso dinamico gia eccitato; piu vicino a scenari su RC, trigger o ampiezza che a modifiche topologiche semplici. |
| `a09` | si | completed | `connect_nodes` / `feed_nodes_from_source_node` | `../experiment1/a09.md` | Caso forte su due sottofasi separate: `connect_nodes` valida i due rami in modo diretto, `feed_nodes_from_source_node` conferma la propagazione da `N003` verso LED e lampada fino allo scenario combinato finale. |
| `a10` | si | completed | `connect_nodes` / `feed_nodes_from_source_node` | `../experiment1/a10.md` | Primo circuito pilota chiuso su due sottofasi: `connect_nodes` mostra la ricostruzione del percorso verso i due rami, `feed_nodes_from_source_node` rifinisce la stessa logica propagando da `N002` verso lampada e LED. |

## Campi stabili per risultati futuri

Per rendere i markdown riusabili in fase risultati, ogni circuito dovrebbe
mantenere questi campi stabili dentro un blocco YAML o equivalente:

```yaml
experiment_id:
batch:
circuit:
status:
included:
excluded_reason:
base_reference:
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

Questi campi non sono ancora uno score finale, ma sono la base giusta per:

- percentuali di successo per primitiva;
- numero medio di scenari eseguiti;
- quanti circuiti ricevono almeno uno scenario topologico nella prima risposta;
- confronto Experiment 1 vs Experiment 2;
- grafici per circuito, per primitiva e per batch.

## Metriche consigliate per la fase risultati

Quando arriveremo alla fase quantitativa, qui potremo derivare almeno:

1. `first_response_topology_hit_rate`
2. `topological_execution_rate`
3. `resolved_candidate_rate`
4. `mean_executed_scenarios_per_circuit`
5. `circuits_requiring_only_electrical_scenarios`
6. `circuits_requiring_topological_scenarios`
7. `excluded_or_image_assisted_cases`

Conviene quindi lasciare i markdown piu regolari possibile.

## File consigliati in questa cartella

```text
experiment_ai/pipeline2_spice_analysis/batchA/experiment2/
|-- README.md
|-- TEMPLATE_CIRCUIT.md
|-- a10.md
`-- a0X.md ...
```

`TEMPLATE_CIRCUIT.md` serve come base per ogni nuovo circuito toccato da
Experiment 2.

## Regola pratica

Un markdown di Experiment 2 va creato solo quando quel circuito viene davvero
aperto e discusso in modo non banale.

Quindi:

- il README batch-level tiene traccia di tutti i circuiti;
- i file per-circuit nascono solo quando iniziamo davvero a lavorarci.
