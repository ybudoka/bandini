# Les triches qui manquaient

← [les jalons livrés](README.md) · [le plan](../plan.md)

## Fiche

Martin (30 sept. 2026) : « regarde s'il ne manquerait pas certaines triches ». L'onglet
TRICHES n'avait rien pour la police, l'heure, les chars, la dette, le casier, les
propriétés, les meubles, les frénésies ni les territoires. Tranché par Martin : les quatre
paquets. Police et heure : LA POLICE OUBLIE (`Police.remiseAZero`), ÉTOILES AU MAXIMUM,
HEURE +3 H (un seul `nouveauJour` si minuit passe) — la pluie, le brouillard et les tempêtes
se lisent du jour et de l'heure, donc elles se voient ainsi. Les chars : une page FAIRE
APPARAÎTRE UN CHAR qui lit le catalogue (rien d'écrit à la main), le char posé à côté du
joueur ; RÉPARER LE CHAR. Raccourcis d'histoire : EFFACER LA DETTE, VIDER LE CASIER, TOUTES
LES PROPRIÉTÉS, TOUS LES MEUBLES — en lisant les catalogues, comme TOUS LES ITEMS. Frénésies
et territoires : une page LANCER UNE FRÉNÉSIE dans JOUER, et RENDRE LES COINS DES GANGS /
UNE NUIT DES GANGS (libérer un district reste à l'histoire, M16).

- ⚠️ Chaque ligne a son juge au bouton du menu, pas à la fonction.

## Notes

**Livré le 30 sept. 2026** (`static/js/hud.js`, `app/blocs/__init__.py` ; juges
`tests/test_triches_manquantes_js.py`, et le classement dans `test_debug_js.py` / `test_classeur_js.py`).
L'onglet TRICHES a deux sections de plus : il se lit LE JOUEUR · LES CHARS · TOUJOURS · ALLER · JOUER ·
LA VILLE · DIVERS.

- **LE JOUEUR** : TOUTES LES PROPRIÉTÉS (les commerces de `economie.proprietes`, la phase 2 comprise, et
  les planques des blocs — le paquet dit maintenant `planque: true` pour le chalet, sans charger le
  bloc), TOUS LES MEUBLES (chaque meuble qui a sa place, déjà livré — commandé « hier », donc le camion
  du matin ne l'annonce pas ; on le voit en rentrant dans la pièce), EFFACER LA DETTE (par
  `Missions.rembourser` : les hommes de Sal rentrent chez eux et l'histoire reçoit `dette_reglee`),
  VIDER LE CASIER.
- **LES CHARS** : FAIRE APPARAÎTRE UN CHAR, une page qui lit `B.defs.vehicules` sans les bateaux ; le
  char naît sur la chaussée la plus proche (huit tuiles au plus), à soi (`aToi`), à la première couleur
  de sa fiche — ⚠️ une couleur donnée ne tire pas de dé, le juge compte zéro appel à `B.rng`. Refusé
  dans une pièce. RÉPARER LE CHAR : celui qu'on conduit, sinon le plus proche ; une épave reste une épave.
- **JOUER** : LANCER UNE FRÉNÉSIE, une page des icônes de la ville ; on se pose sur l'icône et elle part
  tout de suite. ⚠️ Une réussie reste éteinte (relancée, `Frenesies.finir` la repaierait) ; refusée
  pendant une mission ou un défi, comme l'icône.
- **LA VILLE** : LA POLICE OUBLIE, ÉTOILES AU MAXIMUM (refusé au refuge de l'île, comme tout
  signalement), HEURE +3 H (minuit passé, un seul `nouveauJour` ; la pluie, le brouillard et les
  tempêtes se lisent du jour et de l'heure, c'est ainsi qu'on les voit), MOIS SUIVANT (déplacé de
  DIVERS), RENDRE LES COINS DES GANGS (la carte des gangs du premier jour ; les districts libérés le
  restent) et UNE NUIT DES GANGS (`Territoires.nuit`, tout de suite).
- ⚠️ `Surplace` n'est pas chargé au banc : l'heure avance à la main dans la triche, comme la nuit en prison.
- Sept mutations (le `aToi`, la couleur, le jour des meubles, les planques, minuit, la mission de la
  frénésie, l'épave) font chacune rougir leur juge.
