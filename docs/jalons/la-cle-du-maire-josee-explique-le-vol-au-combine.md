# La clé du maire : Josée explique le vol au combiné

← [les jalons livrés](README.md) · [le plan](../plan.md)

## Fiche

Martin (29 sept.) : « ajoute cette explication en vocal dans le jeu » — comment voler la clé
du garde du jardin dans v01. Josée la donne AU COMBINÉ, étape par étape (répliques
`pendant`, voix générées) : en route, le trou de la palissade au nord (la grille a son
garde) ; à la villa, attendre caché derrière la palissade (le chemin n'est pas privé), le
suivre dans une longue ligne droite et jamais près d'un coin (il s'y tourne), se glisser
dans son dos et ACTION, reculer dans le noir au « ? ». Pourquoi : la mission ne disait que
« passe derrière eux », et la règle du vol (dans le dos, tout près) ne s'apprenait nulle
part.

## Notes

- **Livré le 29 sept. 2026** (`app/missions/v01.py`). Quand on arrive sur le chemin de la villa
  (objectif 1), Josée appelle et donne le mode d'emploi en cinq répliques, ville figée tant qu'elle
  parle : la grille a son garde, le trou au nord ; attendre dehors, collé sur la palissade (le chemin
  n'est pas privé) ; le garde du jardin qui s'arrête et se retourne à chaque coin ; le suivre dans une
  longue ligne droite, se coller dans son dos et se servir ; les lampes, reculer dans le noir. Le texte
  de l'objectif dit le bouton : « VOLE LA CLÉ DU GARDE : ACTION DANS SON DOS, SANS ÊTRE VU » (60 caractères au plus : une ligne).
- ⚠️ **Les slugs de voix se comptent à leur place** : les répliques neuves s'insèrent avant « La clé
  est à toi » (objectif 2), dont la voix a été renommée de `josee-v01-9` à `josee-v01-13` sans être
  refaite. `josee-v01-8` à `-12` sont neuves (1 479 caractères au compteur ElevenLabs, la 11 refaite plus courte comprise, eleven_v3).
- **À voir par Martin** : les cinq voix (générées, pas écoutées), et si c'est trop long d'un coup au
  combiné.
