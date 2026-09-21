# Se réveiller dans un lit d’hôpital

← [les jalons livrés](README.md) · [le plan](../plan.md)

## Notes

demande de Martin : « pour le réveil à l'hôpital, je veux qu'on se réveille à l'intérieur et
dans un lit, couché, dès le premier déplacement on se lève et on peut partir ». On se
réveillait **dehors**, sur le trottoir devant la porte. Au noir de l'ellipse, la pièce de
l'hôpital se charge **comme par sa porte** (`Jeu.chargerPiece`, désormais la seule façon
d'entrer : `entrer()` y passe aussi) et le joueur prend **le lit du malade de l'urgence** —
sa tuile de tête, la pose `alite`, les pieds à `PIEDS_ALITE` ; le malade n'y est pas cette
fois. Rien ne sort du lit — ni FRAPPE, ni SPRINT, ni ACTION, ni un passant qui bouscule le
dormeur (`cede`) — sauf **la première poussée du stick**, qui pose le joueur **à côté** du
lit, du côté où l'on pousse, et on marche dans la même image.

- ⚠️ Un meuble n'arrête personne : se lever sur place, c'était se tenir debout sur
  l'oreiller. La porte d'en bas mène devant l'hôpital.
- ⚠️ **Tomber dans une pièce** (la planque, un comptoir) : on en ressort d'abord
  (`Jeu.quitterLaPiece`) — `Monde.entrer` part de la ville, et une pièce chargée par-dessus
  une pièce perdait le chemin du retour.
- ⚠️ **Arrêté pendant le fondu de l'hôpital** : la prison lève le joueur et sort de la
  pièce ; sans ça, on sortait de prison… couché dans le lit.
- ⚠️ **Pas de clignotement** dans le lit (personne à craindre, et un corps qui clignote sous
  sa couverture a l'air d'un bogue) ; la ville sans hôpital garde l'ancien réveil devant la
  porte.
- ⚠️ **Mesuré en chemin, PAS corrigé** : le `recul` d'un coup n'est **jamais** décompté pour
  le joueur (seul `majPieton` le fait) — après n'importe quel coup, il reste penché de 0,22
  rad pour de bon. Le lit le remet à zéro ; la rue, non. 3 juges neufs
  (`test_distributrices_js.py`), **rouges avant** ; chaque garde prouvée par mutation (sans
  `cede`, poussé de 3,5 px ; sans le recul remis, penché de 0,22 ; sans la garde du combat,
  le poing part du lit ; sans la sortie de prison, le juge de l'arrestation tombe). 4 juges
  d'hôpital de `test_moteur_js.py` suivent maintenant le joueur dans la pièce au lieu de le
  chercher sur le trottoir.
