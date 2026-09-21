# On agit sur ce qu'on regarde

← [les jalons livrés](README.md) · [le plan](../plan.md)

## Notes

demande de Martin (20 sept. 2026) : « pour activer une interaction avec la plupart des choses,
à moins d'exception, que le personnage doive faire face à ce qu'il veut activer ».

✅ **Livré** (20 sept. 2026). Avant, ACTION servait tout ce qui était dans un rayon autour du
joueur, quel que soit son regard : on entrait dans un commerce le dos tourné, on montait dans
un char qu'on ne voyait pas.

- ⚠️ **Une règle, un seul calcul.** `faceA(e, x, y)` (`base.js`) : le regard est ce que le
  sprite MONTRE (`face`, l'un des quatre dessinés), pas l'angle fin du stick — ce que le joueur
  voit est ce que le jeu juge. Cône de ±50° (`recherche.regard`), donc les diagonales se
  recouvrent et aucune direction n'est hors de portée. Toutes les fonctions « sous la main »
  la lisent : porte, portière, autobus, manège et comptoir de jeu de la foire, édicule du métro,
  point d'un intérieur, personnage de l'histoire, homme de Sal, homme-sandwich, fille de la
  Brume, témoin, stool, étal, machine, guichet, panneau, arme par terre, bouclier, poches. Et
  l'invite du HUD lit les mêmes : le bouton ne promet jamais un geste qu'ACTION refuserait.
- ⚠️ **Deux exceptions, dites.** (1) Ce qu'on a **sous les pieds** (8 px, `dessus_px`) : la
  direction n'y est plus définie. (2) La **porte de sortie, dedans** : en entrant on regarde
  le fond de la pièce, la porte est dans le dos, et c'est le jeu qui nous y a mis — sortir reste
  le geste vif du bloquant du 13 sept. (« chez Ti-Paul, il est impossible de sortir »). Ce qui
  se ramasse en passant dessus (billets, canettes) n'a jamais passé par ACTION.
- ⚠️ **40 juges posaient le joueur « à côté » sans jamais le tourner** — moteur, histoire,
  métro, autobus, foire, distributrices, réclame, dette… : ils regardent maintenant la chose
  (`o.viser`). Celui du garage a dû déplacer son char : posé à l'est de quelqu'un qui regarde la
  porte au nord, il n'était plus à portée de rien, et la course entre la porte et la portière
  (le bug de Martin) ne se jouait plus.
- ⚠️ **Deux juges passaient à vide** : `test_forcer_la_descente_ne_casse_pas_la_ligne` (sans
  regard le joueur ne montait plus dans l'autobus, et ses non-événements restaient vrais) et le
  test de fumée des canards, qui n'a **aucune assertion** et n'appuyait plus sur rien. Repérés
  en consignant, dans une copie instrumentée, chaque refus de regard survenu pendant un ACTION
  (touche ou appel direct) sur toute la suite. Cinq boucles « cherche une portière » de
  `test_histoire_js.py` ne tenaient que par le regard par défaut (`bas`) : elles se tournent.
- `test_regard_js.py` (12 juges) : la règle et ses bords, la porte de face et dos tourné (invite
  et geste), l'exception de la sortie, la portière, les gens, le comptoir, l'arme sous les
  pieds, l'édicule, les manèges, l'étal/la machine/le guichet/le panneau, le bouclier et les
  poches. ⚠️ Vingt-cinq mutations (retirer chaque `faceA`) le font rougir, chacune.
