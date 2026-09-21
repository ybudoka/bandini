# Les donneurs qu'on ne voyait pas

← [les jalons livrés](README.md) · [le plan](../plan.md)

## Notes

bug de Martin (« je n'arrive pas à faire la mission sergent Bouchard, je vais à la cantine,
mais je ne vois pas quoi faire ») — et il avait raison deux fois. D'abord le **nom** : Marco
l'envoie au « casse-croûte » (le Faubourg, à côté du poste), pas à la **Cantine des Quais**,
un autre bâtiment à l'autre bout de la ville. Ensuite, et c'est le vrai bug : **Bouchard et
Josée n'existaient nulle part**. Ce sont les deux seuls donneurs qui se tiennent DEDANS
(`ou: point:sergent`, `point:contact`), et `creerDonneurs()` ne posait que ceux de la rue
(`porte:`) : on poussait la porte, la salle était vide, et il fallait deviner qu'un **point
invisible** attendait au fond à droite. Ils sont maintenant **posés en entrant**
(`creerDonneursDedans`, appelée par `Jeu.entrer` juste après le commis et les clients), ils
naissent et meurent avec la pièce comme tout le monde, et la table Python→piece ne se
recopie plus en JS : `personnageDuPoint` / `pieceDuPoint` la **déduisent** du `ou` de
`missions.py`.

- ⚠️ Josée pointe une **table** (personne ne se tient debout sur une table) : `placeDebout`
  prend la tuile libre voisine la plus proche du milieu de la pièce — le fond d'un coin, ce
  n'est pas une scène.
- ⚠️ Le GPS a fallu le corriger du même coup (`ouTrouver`) : dedans, un donneur vit en
  coordonnées de **pièce**, et le poser tel quel sur la minicarte envoyait la flèche à six
  tuiles du coin de la ville. Et une **bulle de bande dessinée** dit qui attend après toi —
  voir la ligne suivante. ACTION dedans vise maintenant **la personne avant le comptoir**,
  et le HUD la nomme (« PARLER À SERGENT BOUCHARD »). 2 juges de banc (on entre, quelqu'un
  est là, debout hors des meubles, à portée de son point, et il parle ; il ne suit pas dans
  la rue)
