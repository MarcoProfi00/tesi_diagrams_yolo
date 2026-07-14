# Experiment 3 viewer - Batch A inventory

Workspace:

```text
outputs/pipeline2.0/batchA/experiment3_viewer
```

| Circuito | Prima fase | Base SPICE | Base .tran | Scenari | Viewer base |
| --- | --- | --- | --- | ---: | --- |
| `a01` | si | success | no | 2 | no |
| `a02` | si | success | no | 2 | no |
| `a03` | no | failed | no | 0 | no |
| `a04` | si | success | si | 0 | no |
| `a05` | si | success | no | 2 | no |
| `a06` | si | success | si | 0 | no |
| `a07` | si | success | si | 2 | no |
| `a08` | si | success | si | 5 | no |
| `a09` | si | success | no | 3 | no |
| `a10` | si | success | no | 4 | no |

Nota: `a03` resta copiato per completezza Batch A, ma e escluso dalla prima fase viewer.

Gli scenari provenienti da `experiment2_feed_nodes` sono conservati separatamente in `_sources/experiment2_feed_nodes/` e non sono fusi automaticamente negli scenari attivi.
