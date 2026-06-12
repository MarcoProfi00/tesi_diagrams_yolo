"""
Costruzione del contesto diagnostico strutturato.

Questo modulo prepara il pacchetto tecnico da usare in una fase successiva
per l'agente o la chat diagnostica.

Per ora l'agente non viene implementato, ma la pipeline deve gia produrre un
contesto ordinato e riutilizzabile.

Sezioni previste:

- GRAPH SUMMARY;
- NODE MAP;
- VALUES AND ASSUMPTIONS;
- CONVERSION STATUS;
- SPICE NETLIST;
- SPICE RESULTS;
- ELECTRICAL CHECKS;
- DEVICE PROFILES / DATASHEET;
- WARNINGS AND LIMITS.

L'obiettivo e fornire a GPT o a un'interfaccia futura un input piu affidabile
del solo Graph JSON grezzo.
"""
