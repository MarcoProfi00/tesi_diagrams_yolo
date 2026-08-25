# Batch CHAT–AGENT

Input congelati per il confronto tra le modalità CHAT e AGENT.

- Circuiti batchA: `a01`, `a02`, `a04`, `a05`, `a06`, `a07`, `a08`, `a09`, `a10`
- Circuiti batchB: `b02`, `b03`, `b04`, `b05`, `b10`
- Totale: 14 circuiti
- `a03` escluso

Le immagini sono nella radice della cartella. I valori manuali richiesti dalla
Pipeline 2.0 sono in `values/`.

Workspace di output previsto:

```text
outputs/demo_workspaces/chat_agent_evaluation/
```

Per elaborare un circuito alla volta, usare sempre lo stesso workspace e
specificare il relativo `--circuit`.
