# Constitution des systèmes d'IA générative d'une juridiction
### A constitution for a court's generative AI systems

Version 0.2, 10 septembre 2026. Note de travail sans valeur normative, destinée à préparer un acte de l'institution. Aucune institution ni aucun système n'est nommé.
Working note, version 0.2 (10 September 2026), without normative value; no institution or system is named.

## Ce que c'est / What it is

Un texte en trois parties, et le code qui le rend vérifiable :

1. **Principes** (29 articles) : ce qui commande et ce qui est interdit, chaque article avec sa raison et son contrôle.
2. **Garanties techniques** (G1 à G16) : ce que le logiciel rend impossible ou obligatoire, indépendamment de toute instruction, avec une implémentation de référence.
3. **Instructions fondamentales** : le socle placé en tête du prompt système de tout système génératif de l'institution, versionné.

Three parts, and the code that makes them verifiable: principles (29 articles, each with its rationale and its check), technical safeguards (G1 to G16, with reference code), and the core instructions placed at the top of every system prompt.

## Fichiers / Files

| Fichier | Contenu | Licence |
|---|---|---|
| `CONSTITUTION.md` | Le texte intégral (préambule, définitions, principes, garanties, instructions, annexes). Full text, French. | CC BY 4.0 |
| `garanties.py` | Implémentation de référence des garanties G2, G3, G4, G7, G8, G14, G15, G16 (bibliothèque standard Python). Reference implementation. | MIT |
| `essais.py` | Contrôles exécutables (`python3 essais.py` doit se terminer par `OK`) et rejeu des essais contradictoires. Executable checks. | MIT |
| `essais_contradictoires.jsonl` | Dix cas de départ : interdictions absolues, pièces piégées, questions sans réponse. Adversarial test seed. | MIT |
| `instructions_fondamentales_v0.2.txt` | Le socle d'instructions, tel que versionné et journalisé. The core system-prompt block. | CC BY 4.0 |
| `constitution.html` | La page servie aux utilisateurs par les applications qui appliquent ce texte. The page served to users. | CC BY 4.0 |

## Cadre / Framework

Règlement (UE) 2024/1689 (annexe III, point 8 a) ; articles 3, 4, 14, 26, 27, 43, 49, 72, 73) tel que modifié par le règlement (UE) 2026/1744 ; charte éthique CEPEJ (2018) ; convention-cadre du Conseil de l'Europe (STCE 225) ; article L. 10 du code de justice administrative. Les sources sont citées, liées et reproduites mot pour mot dans le texte.

## Licences / Licenses

© 2026 Armadillo4Ever. Texte sous [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/deed.fr) (`LICENSE-TEXTE`) ; code sous [MIT](LICENSE). Les extraits cités de sources tierces restent la propriété de leurs auteurs.
