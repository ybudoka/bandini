# Les alliés contournent les murs

← [le plan](../plan.md)

## Fiche

Trouvé par la suite complète après [les rames ne se bloquent plus aux coins](les-rames-ne-se-bloquent-plus-aux-coins.md)
(30 sept. 2026), tranché par Martin : « des alliés qui contournent ».

Au siège du Brouillard (m98), les six alliés courent **en ligne droite** sur leur Cravate. Le jour où
le trafic a cessé de s'impasser, la bagarre s'est déplacée : les Cravates ont fui derrière un
bâtiment, et les six alliés sont restés collés au mur jusqu'à la fin — 1 KO au lieu de 4, sur les
dix graines. Avant, ils ne tenaient que parce que la fuite passait par la rue.

- ⚠️ Un allié qui n'avance plus en poursuivant demande un chemin (`Monde.demanderChemin`, l'A* que
  la police suit déjà) et le suit ; une cible injoignable, il la laisse pour une autre.

## Notes

- `Entites.pasDeLAllie` : vingt images sans avancer en courant, l'allié demande son chemin
  (`Monde.demanderChemin`, masque piéton) vers sa cible et en suit les tuiles ; un chemin
  introuvable (plus de 800 nœuds, ou muré) lui fait laisser cette cible de côté 600 images
  (`cibleDeLAllie` la saute), et il en prend une autre — ou te suit.
- Mesuré : au siège de m98, sur les dix graines, **1 KO** avant (les six alliés collés au mur),
  les juges du siège et de la ville d'après verts après. Juge dédié :
  `test_un_allie_contourne_le_mur_derriere_lequel_sa_cravate_a_fui` (un mur plein entre l'allié et
  sa Cravate, un détour de 14 tuiles) — sans le chemin, l'allié reste à 125 px.
- ⚠️ Le même juge rendait le joueur `invincible` pendant les six cents images à cinq étoiles, pas
  `intouchable` : un agent l'arrêtait, « ARRÊTÉ ! » figeait la partie et l'étape 3 ne venait jamais.
  Il tenait par où roulait le trafic ; il est intouchable le temps de tenir.
