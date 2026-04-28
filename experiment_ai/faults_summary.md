## Fault manifest

| Circuito | Fault ID | Tipo guasto | Modifica immagine | Scenario sintetico | Componente/terminale target | Diagnosi attesa | Pipeline capture 0-2 | Note |
|---|---|---|---|---|---|---|---:|---|
| C01 | F01_led_open | open_connection | Filo tra resistenza superiore e LED cancellato | Il LED non si accende | `led12.1` | Ramo LED interrotto: `led12.1_anode` e `resistor22.2_t2` risultano scollegati | 2 | Guasto chiaramente catturato dal JSON; test valutabile lato AI |
| C01 | F02_led_lamp_branch_short | short/fused_nodes | Disegnato un ponte tra il ramo superiore LED e il ramo inferiore lampada a valle delle resistenze | LED e lampada si attivano insieme | `led12.1`, `lamp13.1` | Rami LED e lampada fusi nello stesso nodo: `resistor22.2_t2`, `resistor22.1_t2`, `led12.1_anode` e `lamp13.1_t1` risultano collegati insieme | 2 | Guasto chiaramente catturato dal JSON; test valutabile lato AI |
| C02 | F01_top_rail_open | open_connection | Rail superiore interrotto | I rami a destra non ricevono alimentazione |  | Rail superiore interrotto |  |  |
| C02 | F02_bottom_return_open | open_connection | Rail inferiore interrotto | Il circuito non si chiude correttamente |  | Ritorno inferiore interrotto |  |  |
| C03 | F01_switch_open_state | switch_state | Nessuna modifica, switch aperto | Il percorso A-B tramite switch non conduce |  | Switch aperto, continuità assente |  |  |
| C03 | F02_capacitor_branch_open | open_connection | Ramo capacitivo interrotto | Nodo centrale non accoppiato correttamente |  | Ramo capacitivo interrotto |  |  |
| C04 | F01_feedback_open | open_connection | Feedback opamp-R2 interrotto | Uscita instabile o saturata |  | Feedback interrotto |  |  |
| C04 | F02_noninv_input_floating | floating_node | Filo e GND dell’ingresso positivo rimossi | Ingresso positivo senza riferimento |  | Ingresso positivo flottante |  |  |
| C05 | F01_base_q2_open | open_connection | Collegamento verso base Q2 interrotto | Q2 non viene pilotato correttamente |  | Nodo/base Q2 interrotto |  |  |
| C05 | F02_output_short_to_gnd | short/fused_nodes | Corto tra VOUT e GND/rail negativo | Uscita bloccata bassa |  | Uscita cortocircuitata verso nodo basso |  |  |
| C06 | F01_inductor_open | open_connection | Collegamento verso induttore L interrotto | Trasformatore non pilotato |  | Percorso L/primario interrotto |  |  |
| C06 | F02_secondary_switch_open | switch_state | Nessuna modifica, switch secondario aperto | Non compare uscita sul secondario |  | Switch secondario aperto |  |  |
| C07 | F01_fuse_to_output_open | open_connection | Collegamento verso/dopo F1 interrotto | Ramo di uscita verso terminale finale non conduce |  | Ramo fusibile/uscita interrotto |  |  |
| C07 | F02_control_path_open | open_connection | Ramo D1/Q1/D2 interrotto | Controllo di carica non funziona |  | Percorso di controllo interrotto |  |  |


## Scala Pipeline capture

| Punteggio | Significato |
|---:|---|
| 2 | Il guasto è chiaramente rappresentato nel JSON. Per esempio manca il collegamento, compare il corto, lo switch è open, il nodo è flottante. |
| 1 | Il guasto è rappresentato solo parzialmente o in modo ambiguo. Il JSON suggerisce un’anomalia, ma non è chiarissimo. |
| 0 | Il guasto non è stato catturato dal JSON oppure la pipeline ha prodotto un errore che rende il test non valutabile. |