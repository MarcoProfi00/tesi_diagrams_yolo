## Risultati diagnosi AI

| Circuito | Fault ID | Modello | Pipeline capture | Sintomo capito | Uso corretto JSON | Ricostruzione topologica | Guasto individuato | Limiti / no allucinazioni | Totale AI /10 | End-to-end /12 | Giudizio |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| C01 | F01_led_open | GPT-5.4 | 2 | 2 | 2 | 2 | 2 | 2 | 10 | 12 | Diagnosi corretta |
| C01 | F01_led_open | GPT-5.3 Instant | 2 | 2 | 2 | 2 | 2 | 2 | 10 | 12 | Diagnosi corretta |
| C01 | F01_led_open | GPT-5.2 Instant | 2 | 2 | 2 | 2 | 2 | 2 | 10 | 12 | Diagnosi corretta |
| C01 | F02_led_lamp_branch_short | GPT-5.4 | 2 | 2 | 2 | 2 | 2 | 2 | 10 | 12 | Diagnosi corretta |
| C01 | F02_led_lamp_branch_short | GPT-5.3 Instant | 2 | 2 | 2 | 2 | 2 | 2 | 10 | 12 | Diagnosi corretta |
| C01 | F02_led_lamp_branch_short | GPT-5.2 Instant | 2 | 2 | 2 | 2 | 2 | 2 | 10 | 12 | Diagnosi corretta |
| C02 | F01_top_rail_open | GPT-5.4 | 2 | 2 | 2 | 2 | 2 | 2 | 10 | 12 | Diagnosi corretta |
| C02 | F01_top_rail_open | GPT-5.3 Instant | 2 | 2 | 2 | 2 | 2 | 2 | 10 | 12 | Diagnosi corretta |
| C02 | F01_top_rail_open | GPT-5.2 Instant | 2 | 2 | 2 | 1 | 2 | 2 | 9 | 11 | Diagnosi corretta con lieve imprecisione topologica |
| C02 | F02_bottom_return_open | GPT-5.4 | 2 | 2 | 2 | 2 | 2 | 2 | 10 | 12 | Diagnosi corretta |
| C02 | F02_bottom_return_open | GPT-5.3 Instant | 2 | 2 | 2 | 2 | 2 | 2 | 10 | 12 | Diagnosi corretta |
| C02 | F02_bottom_return_open | GPT-5.2 Instant | 2 | 2 | 2 | 2 | 2 | 2 | 10 | 12 | Diagnosi corretta |
| C03 | F01_switch_open_state | GPT-5.4 | 2 | 2 | 2 | 2 | 2 | 2 | 10 | 12 | Diagnosi corretta |
| C03 | F01_switch_open_state | GPT-5.3 Instant | 2 | 2 | 2 | 2 | 2 | 2 | 10 | 12 | Diagnosi corretta |
| C03 | F01_switch_open_state | GPT-5.2 Instant | 2 | 2 | 2 | 2 | 2 | 2 | 10 | 12 | Diagnosi corretta |
| C03 | F02_capacitor_branch_open | GPT-5.4 | 2 | 2 | 2 | 2 | 2 | 2 | 10 | 12 | Diagnosi corretta |
| C03 | F02_capacitor_branch_open | GPT-5.3 Instant | 2 | 2 | 2 | 1 | 2 | 2 | 9 | 11 | Diagnosi corretta con lieve imprecisione topologica |
| C03 | F02_capacitor_branch_open | GPT-5.2 Instant | 2 | 2 | 2 | 1 | 2 | 2 | 9 | 11 | Diagnosi corretta con lieve imprecisione topologica |
| C04 | F01_feedback_open | GPT-5.4 | 2 | 2 | 2 | 2 | 2 | 2 | 10 | 12 | Diagnosi corretta |
| C04 | F01_feedback_open | GPT-5.3 Instant | 2 | 2 | 2 | 2 | 2 | 1 | 9 | 11 | Diagnosi corretta con lieve interpretazione funzionale troppo assertiva |
| C04 | F01_feedback_open | GPT-5.2 Instant | 2 | 2 | 2 | 2 | 2 | 1 | 9 | 11 | Diagnosi corretta con lieve interpretazione funzionale troppo assertiva |
| C04 | F02_noninv_input_floating | GPT-5.4 | 2 | 2 | 2 | 2 | 2 | 2 | 10 | 12 | Diagnosi corretta |
| C04 | F02_noninv_input_floating | GPT-5.3 Instant | 2 | 2 | 2 | 2 | 2 | 1 | 9 | 11 | Diagnosi corretta con lieve interpretazione funzionale troppo assertiva |
| C04 | F02_noninv_input_floating | GPT-5.2 Instant | 2 | 2 | 2 | 2 | 2 | 1 | 9 | 11 | Diagnosi corretta con lieve interpretazione dei pin troppo assertiva |
| C05 | F01_base_q2_open | GPT-5.4 | 2 | 2 | 2 | 2 | 2 | 2 | 10 | 12 | Diagnosi corretta |
| C05 | F01_base_q2_open | GPT-5.3 Instant | 2 | 2 | 2 | 2 | 2 | 2 | 10 | 12 | Diagnosi corretta |
| C05 | F01_base_q2_open | GPT-5.2 Instant | 2 | 2 | 2 | 2 | 2 | 2 | 10 | 12 | Diagnosi corretta |
| C06 | F01_inductor_open | GPT-5.4 | 2 | 2 | 2 | 2 | 1 | 1 | 8 | 10 | Diagnosi buona ma non centrata sul guasto principale |
| C06 | F01_inductor_open | GPT-5.3 Instant | 2 | 2 | 2 | 2 | 2 | 1 | 9 | 11 | Diagnosi corretta con lieve interpretazione funzionale troppo assertiva |
| C06 | F01_inductor_open | GPT-5.2 Instant | 2 | 2 | 2 | 1 | 0 | 1 | 6 | 8 | Diagnosi parziale; guasto principale non individuato |
| C06 | F02_output_switch_open | GPT-5.4 | 2 | 2 | 2 | 2 | 2 | 2 | 10 | 12 | Diagnosi corretta |
| C06 | F02_output_switch_open | GPT-5.3 Instant | 2 | 2 | 2 | 2 | 2 | 2 | 10 | 12 | Diagnosi corretta |
| C06 | F02_output_switch_open | GPT-5.2 Instant | 2 | 2 | 2 | 2 | 2 | 1 | 9 | 11 | Diagnosi corretta con lieve interpretazione funzionale troppo assertiva |
| C07 | F01_fuse_to_output_open | GPT-5.4 | 2 | 2 | 2 | 2 | 2 | 2 | 10 | 12 | Diagnosi corretta |
| C07 | F01_fuse_to_output_open | GPT-5.3 Instant | 2 | 2 | 2 | 1 | 1 | 1 | 7 | 9 | Diagnosi parziale; guasto principale non centrato |
| C07 | F01_fuse_to_output_open | GPT-5.2 Instant | 2 | 2 | 2 | 2 | 2 | 1 | 9 | 11 | Diagnosi corretta con lieve ambiguità sul terminale finale |
| C07 | F02_control_path_open | GPT-5.4 | 2 | 2 | 2 | 2 | 2 | 2 | 10 | 12 | Diagnosi corretta |
| C07 | F02_control_path_open | GPT-5.3 Instant | 2 | 2 | 2 | 1 | 2 | 1 | 8 | 10 | Diagnosi buona ma incompleta |
| C07 | F02_control_path_open | GPT-5.2 Instant | 2 | 2 | 2 | 2 | 2 | 1 | 9 | 11 | Diagnosi corretta con lieve interpretazione funzionale troppo assertiva |

## Test non valutabili / pipeline non cattura il fault

| Circuito | Fault | Motivo | Pipeline capture | Decisione |
|---|---|---|---:|---|
| C05 | F02_output_short_to_gnd | Il corto VOUT-GND non è rappresentato nel JSON: `terminal26.4_t1` e `terminal26.3_t1` / `gnd9.1_t1` restano su nodi distinti e non sono presenti warning coerenti. | 0/2 | GPT non eseguiti; test da ripetere o sostituire |

## Rubrica valutazione AI

| Criterio | 0 | 1 | 2 |
|---|---|---|---|
| Sintomo capito | Non capisce il problema richiesto | Capisce genericamente il sintomo | Capisce chiaramente il sintomo e il componente/terminale coinvolto |
| Uso corretto JSON | Ignora il JSON o inventa collegamenti | Usa il JSON solo parzialmente | Usa correttamente componenti, terminali, collegamenti e stati |
| Ricostruzione topologica | Non ricostruisce il percorso/nodo rilevante | Ricostruzione parziale | Ricostruisce correttamente nodo, ramo o percorso interessato |
| Guasto individuato | Non trova il guasto o ne propone uno sbagliato | Trova un’anomalia vicina ma non precisa | Individua il guasto atteso: open, short, floating o switch open |
| Limiti / no allucinazioni | Inventa valori, funzioni o cause non presenti | Qualche affermazione troppo forte | Distingue bene deduzioni certe, ipotesi e limiti del JSON |

Totale AI /10 = somma dei 5 criteri
End-to-end /12 = Pipeline capture + Totale AI

## Interpretazione punteggi AI

| Totale AI /10 | Giudizio |
|---:|---|
| 9-10 | Diagnosi corretta |
| 7-8 | Diagnosi buona ma con qualche limite |
| 5-6 | Diagnosi parziale |
| 3-4 | Diagnosi debole |
| 0-2 | Diagnosi errata o non utile |

## Interpretazione end-to-end

| End-to-end /12 | Giudizio |
|---:|---|
| 11-12 | Pipeline + AI funzionano bene |
| 8-10 | Risultato buono/parziale |
| 5-7 | Risultato debole |
| 0-4 | Fallimento del processo |