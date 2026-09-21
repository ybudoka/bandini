# Un menu qui ne choisit rien

← [les jalons livrés](README.md) · [le plan](../plan.md)

## Notes

retour de Martin, capture à l'appui (« il n'y a pas de sélection dans ce menu ») : au
comptoir des **hommes de Sal**, aucune ligne n'est surlignée, HAUT et BAS ne bougent rien,
ACTION ne donne pas un sou. La collecte était le **seul menu du jeu posé à la main** —
`B.menu = menuDette(...)` au lieu de `Hud.ouvrirMenu` — donc ouvert **sans curseur** :
`undefined`, que HAUT et BAS transforment en `NaN` (`(undefined + 1) % 4`), et un curseur
`NaN` ne surligne aucune ligne, n'en choisit aucune et ne revient jamais. Deux dégâts de
plus par la même porte manquée : les boutons de l'écran tactile continuaient d'annoncer
FRAPPE et ACTION au lieu de RETOUR et CHOISIR (`Entree.contexte('menu')` est dans
`ouvrirMenu`), et le petit son du menu ne sortait pas. **On ne pouvait pas payer Sal**, au
moment le plus tendu du jeu.

- ⚠️ Deux autres choses tenaient sur la même capture. **L'en-tête** : même passé par la
  porte, ce menu s'ouvrait sur « LA DETTE », une ligne qui se lit et ne se choisit pas — le
  menu n'a l'air d'avoir aucune sélection, et ACTION n'y répond qu'un bip. La règle
  existait, mais **à la main** (les OPTIONS portent `curseur: 1` parce que leur première
  ligne est un diagnostic) et **cinq menus l'avaient oublié** : la dette, le carnet du
  poste, l'avocat, le comptoir du fond, la revente de contrebande. Elle se tient maintenant
  **une fois**, dans `ouvrirMenu` : le curseur se pose sur la première ligne qui porte un
  `faire`.
- ⚠️ Une ligne **hors de portée** reste un choix — le curseur s'y pose et c'est le prix qui
  dit non ; un menu qui **nomme** son curseur le garde (le JOURNAL s'ouvre en haut de sa
  liste et s'y promène) ; un menu où il n'y a rien à choisir (le BILAN) reste en haut. **Le
  fond** : la boîte d'un menu ne couvre qu'à 92 %, et ce qui est clair derrière la traverse
  — la bulle d'un passant qui parlait sous le comptoir s'imprimait **en travers** de « TOUT
  REGLER », illisible sur la capture. La pause posait déjà son voile avant son menu ; un
  menu en jeu fige le monde autant qu'elle et a maintenant le même (mesuré après, au
  navigateur : le fantôme de la bulle tombe à **3 niveaux sur 255**, sous la lecture). 3
  juges de banc, rouges avant : le menu de Sal se joue pour de vrai (il s'ouvre sur
  l'acompte, BAS descend d'un cran, ACTION donne 2000 $, la dette baisse d'autant, ils s'en
  vont, et le bouton dit CHOISIR) ; un menu s'ouvre sur une ligne qu'on peut choisir dans
  les quatre cas ; la rue s'efface sous un menu ouvert, et le voile passe **avant** la
  boîte.
