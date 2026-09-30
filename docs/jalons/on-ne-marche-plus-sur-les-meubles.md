# On ne marche plus sur les meubles

← [les jalons livrés](README.md) · [le plan](../plan.md)

## Fiche

Martin (30 sept. 2026) : « on ne doit pas pouvoir marcher sur les meubles ». Jusqu'ici c'était
voulu : un meuble d'intérieur (`c` comptoir, `l` lit, `a` table, `h` chaise…) est `solide 3`,
un obstacle BAS qui arrête un char mais pas un piéton — par peur qu'un meuble coince le joueur
dans une pièce (`carte.py`, « Dedans : les planchers et les meubles »). Le mobilier de rue et les
décors de la planque, eux, sont déjà solides.

Le changement : un bit `MEUBLE` dans les masques du piéton, du joueur (et des agents) et des
chemins à pied ; l'escalier `/` reste marchable (on y marche pour monter). Côté serveur,
`marchable()` ne compte plus un meuble, et le juge des pièces mesure l'atteignable sans passer
dessus : un coin coupé derrière un comptoir est permis (le commis y reste), un point d'action,
un client ou une tuile de sortie coincés ne le sont pas.

- ⚠️ La sonde du 30 sept. : 14 pièces sur 126 se coupent ; à redessiner celles dont un point
  n'est plus atteignable (le hacker de l'électronique, repeindre au garage, le journal du
  kiosque, fouiller dans deux logements). La ville et les blocs ne se coupent nulle part
  (aucun meuble en ville ; la villa garde ses trois morceaux).
- ⚠️ Se lever d'un lit pose déjà les pieds à côté (`seLever`) ; les gens assis ou couchés
  naissent dans leur meuble et n'en sont pas éjectés (collision par bord de tuile).

## Notes

**Livré le 30 sept. 2026.**

- **La règle** (`monde.js`) : un bit `MEUBLE` dans `MASQUE_PIETON`, `MASQUE_NAGEUR` (le joueur,
  les agents) et `MASQUE_A_PIED` (le A*). Le paquet ne change pas : un meuble reste `solide 3`, et
  `bloque` lit son glyphe (`meubleQuiBarre`) — un chantier, une fête ou un bloc qui change une
  tuile n'a rien à tenir à jour. L'escalier (`/`, `MARCHE_DESSUS`) se foule toujours.
- **Côté serveur** : `marchable` et `franchissable` refusent le meuble (un meuble n'est pas un
  pont, comme l'était la clôture). `_verifier_piece` part de l'apparition : un point se touche
  depuis la porte, un client n'est jamais muré, et seul le personnel (`COULISSES` : commis,
  soignant, croupier) se tient dans l'arrière du comptoir.
- **Le meubleur des pièces posées** (logements, commerces) demande `_atteint` au lieu de ses
  voisines : un coin qui mure la pièce se reprend (sans chaises, sinon vide ; un 3 × 5 fermait
  tout sous sa table), un petit meuble d'appoint ou la plante du seuil ne se pose pas s'il coupe
  quoi que ce soit, un client naît où on le rejoint.
- **Redessinés** : le garage (l'établi recule d'une tuile, on rejoint le coin où l'on repeint),
  le kiosque (la plante cède sa place au journal), l'électronique (une étagère de moins au bout
  du comptoir : on passe à l'arrière-boutique), et une pièce de l'étage de la villa dont la porte
  donnait sur une rangée d'étagères.
- **Se lever d'un lit** (`seLever`) préfère une place d'où l'on peut continuer dans le sens de la
  poussée : au pied du lit de l'urgence il y a une chaise.
- Juges : `test_meubles_js.py` (le comptoir du terminus arrête le joueur, chaque meuble de la
  légende barre à pied sauf l'escalier, le A* n'enjambe pas le guichet) — les trois rougissent sans
  le bit ; `test_un_interieur_est_une_piece_habitable` suit la nouvelle règle.
