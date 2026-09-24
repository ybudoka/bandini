# Enfermé dans six commerces

← [les jalons livrés](README.md) · [le plan](../plan.md)

## Fiche

_Titre d'origine dans le plan : On est enfermé dans six commerces (**correctif**, taille 1) — **livré le 13 sept. 2026**_

_Bug signalé par Martin :_ « chez Ti-Paul, il est impossible de sortir. »

⚠️ **C'était vrai, et ce n'était pas que chez Ti-Paul : six pièces étaient sans issue.** La
cause tenait en deux lignes de `combat.js` — **le comptoir passait avant la porte** — et en
deux rayons qui ne se parlaient pas : `pointSousLaMain()` attrape le point le plus proche
dans **1,6 tuile autour** de soi, quand `porteDevant()` n'accepte que la tuile collée à la
porte. Dans une pièce dont la porte est au mur du bas, il n'y a donc **qu'une seule tuile
d'où l'on peut sortir** : qu'un point d'action tombe à moins de 1,6 tuile de celle-là, et
ACTION sert le comptoir — toujours. Chez Ti-Paul, le point du journal était **sur** la tuile
de sortie (distance 0,00) ; Rosa, le kiosque, le phare et les deux boutiques génériques
étaient à 1,00 ou 1,41.

⚠️ Et il n'y avait **aucun repli** : `utiliserPoint()` rend `true` dès qu'il trouve un point
— même sans menu à ouvrir, il affiche « PLUS TARD » et rend `true`. Aucune deuxième pression
ne finissait par sortir. On quittait vers le titre, ou on restait.

**Deux corrections, et il fallait les deux** — l'une répare aujourd'hui, l'autre empêche
demain :

- **La porte ne se laisse plus voler** : sur la tuile de sortie, ACTION sort. Un comptoir se
  sert d'un pas de côté ; une porte, non.
- ⚠️ **Un juge Python sur `INTERIEURS`**, parce que c'est là que le mal se crée : aucun point
  d'action à moins de `RAYON_POINT` (1,6 tuile) de la tuile de sortie. Il rougissait **six
  fois** le jour où il a été écrit, et il lève maintenant **à l'import** (`_verifier_piece`),
  comme les autres règles de plan — une pièce fautive ne se charge plus.
- **Les six pièces se sont redessinées** : le comptoir recule d'une tuile, et le journal du
  dépanneur s'en va contre son mur, sur sa propre étagère.
- **Juges (3 neufs)** : aucun point à moins de 1,6 tuile de la sortie (une pièce à la fois,
  par `parametrize`) ; on ressort de **chaque** pièce de la ville en appuyant sur ACTION là où
  l'on arrive ; et un troisième qui **remet le piège à la main** — un point d'action posé pile
  sur la tuile de sortie — pour que la correction du jeu ait son propre juge, indépendant du
  dessin des pièces. Ce dernier rougit dès qu'on remet le comptoir avant la porte.

## Notes

bug de Martin (« chez Ti-Paul, impossible de sortir ») : `utiliserPoint` passait **avant**
la porte et attrape tout point à 1,6 tuile — or il n'y a qu'une tuile d'où sortir, et il
rend `true` même quand il n'a qu'un « PLUS TARD » à dire. **Deux corrections, et il fallait
les deux** : la porte passe maintenant avant le comptoir (un comptoir se sert d'un pas de
côté, une porte non), et un **juge Python** interdit tout point d'action à moins de
`RAYON_POINT` (1,6 tuile) de la tuile de sortie — il rougissait six fois le jour où il a été
écrit. Les six pièces se sont redessinées (le comptoir recule, le journal du dépanneur s'en
va contre son mur). 3 juges neufs, dont un qui **remet le piège à la main**
