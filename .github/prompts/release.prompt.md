---
name: release
agent: agent
description: Incrementa la versió del projecte seguint les convencions de versionat semàntic i actualitza els fitxers rellevants. Assegura't que tots els tests passen després de la actualització de la versió. Executa update_coverage.py per actualitzar la cobertura dels tests al readme, ha de ser mínima del 95% (avisa si aquest pas falla). Mira d'obtenir un 96% perquè a vegades github calcula una mica a la baixa i fallen les 'Actions'. Inclou els passos necessaris per a realitzar aquesta tasca de manera eficient i sense errors. Fes commits amb missatges clars i descriptius. Fes push i crea una etiqueta (tag) per a la nova versió.
tools: ['execute', 'read', 'edit', 'search', 'web', 'agent', 'todo']
---
Define the task to achieve, including specific requirements, constraints, and success criteria.
