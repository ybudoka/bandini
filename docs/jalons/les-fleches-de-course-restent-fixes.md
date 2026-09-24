# Les flèches de course restent fixes

← [les jalons livrés](README.md) · [le plan](../plan.md)

## Fiche

Retour de Martin (22 sept. 2026), sur [les courses](les-courses-suivre-les-fleches.md) : « les flèches
clignotent quand on avance, il faudrait qu'elles restent fixes ».

Deux causes, dans `Histoire.flechesALEcran` :

- **Elles sont posées depuis le char**, pas sur la piste : une flèche tous les deux points à partir de
  celui où l'on est. À chaque tuile avancée, tout le jeu de flèches change de parité et saute de 16 px
  — d'avant en arrière, à chaque tuile.
- **Leur lueur bat**, et la phase de chaque flèche se lit à son rang devant le char : quand on avance,
  son rang change, et sa lumière saute d'un coup.

La correction : chaque flèche a sa place **sur le circuit** (un point sur deux du tracé, compté depuis
la ligne de départ) et n'en bouge plus ; celles qu'on dépasse disparaissent derrière le char, les
nouvelles naissent loin devant, hors de l'écran. Et une **lumière fixe** — le halo et la lampe de nuit
restent, le battement part.

- ⚠️ Le juge regarde deux images de suite, le char avancé d'une tuile : une flèche qui existe aux deux
  est au même pixel du monde, avec la même lumière.

## Notes

**Livré le 22 sept. 2026.** `Histoire.flechesALEcran` prend un point sur deux **du circuit** (son
indice sur la piste, pas son rang devant le char) ; la lueur ne bat plus, ni sur le trait, ni sur la
lampe de nuit (`lampesDeCourse`).

- ⚠️ Un circuit fermé, pas à pas sur la grille, a toujours un nombre **pair** de points (les cinq :
  412, 306, 380, 392, 366) : la ligne de départ se franchit sans que le pas de 32 px casse. Aucune
  garde pour le cas impair — il n'arrive pas.
- Juge : `test_les_fleches_restent_fixes_quand_on_avance` (caméra tenue fixe, le char avancé tuile par
  tuile : mêmes flèches, même place, même lumière, moins celles qu'on dépasse). Rouge avant (15 images
  sur 30) ; il rougit si on les repose depuis le char, et si la lueur se remet à battre.
