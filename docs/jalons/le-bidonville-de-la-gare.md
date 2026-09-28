# Le bidonville de la gare : l'est de la Gare de triage

← [le plan](../plan.md) · [les jalons livrés](README.md)

## Fiche

_Demande de Martin (28 sept. 2026) :_ « dans le quartier des trains, je veux plus un bidonville et des maisons
pauvres pour la partie est ».

**Ce que ça donne** : la Gare de triage (`nord.py`, district `gare`) garde ses voies sur ses quatre colonnes
d'îlots de l'ouest (le poste d'aiguillage ne bouge pas) et ses hangars au sud ; ses trois colonnes de l'est
changent de vocation.

- **Le bidonville** (lettre de plan `t`, les trois rangées du nord de l'est, un seul lot) : des cabanes de tôle
  serrées, des sentiers de terre battue entre elles, des barils où brûle un feu, des cordes à linge, des bâches
  et des pneus sur les toits pour tenir la tôle. Aucune porte qu'on pousse.
- **Les maisons pauvres** (`h`, standing `-`, les deux rangées sous le bidonville) : les maisons de la ville,
  en pauvre — les planches aux fenêtres, le fer rouillé, les lampadaires en panne, les poubelles qui débordent.
- ⚠️ **Les dés** : chaque îlot neuf se bâtit avec les SIENS (la recette du Petit-Canton, `_a_ses_des`) ; les
  Friches et le Petit-Canton ne doivent pas bouger d'une tuile.
- ⚠️ La gare n'est plus « une seule porte » : `test_nord` suit (le poste d'aiguillage reste la seule porte des
  voies).

## Notes
