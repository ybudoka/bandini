# La première bagarre ne se gagne pas

← [les jalons livrés](README.md) · [le plan](../plan.md)

## Notes

retour de Martin : « la premiere mission des cravattes est trop difficile, ils font trop de
dommage ».

- ⚠️ **Mesuré au banc, et il a raison** : M2 est la **première bagarre du jeu** — le joueur
  a 100 PV et ses **poings** (8 de dégâts), en face deux Cravates sorties de l'archétype
  avec **90 PV** et le **bâton** (18 de dégâts, et `renverse`). Mesure d'avant : un joueur
  qui les laisse cogner tombe en **2,8 s**.
- ⚠️ **Et le bâton est la RÉCOMPENSE de M2** : on le rencontrait avant de le posséder — le
  dialogue promet pourtant l'inverse (« Fais-leur comprendre. **Avec tes poings, pas
  plus.** »).
- ⚠️ **On ne touche PAS à l'archétype pour régler une bagarre** : la Cravate de rue tient le
  Faubourg en M5 et vient encaisser la dette de Rocco — l'affaiblir pour arranger M2 aurait
  rendu mou tout le reste du jeu. Ce qui change, c'est **qui on envoie** : un objectif
  `tuer` porte désormais deux clés facultatives, `arme` (`""` = les poings) et `vie`, qui
  passent par-dessus la fiche de l'archétype **et seulement pour ces hommes-là**
  (`missions.py`, appliquées dans `poserLesCravates`). Les deux du kiosque arrivent donc
  **les mains vides**, à 55 PV : ils sont venus racketter une dame, pas casser un homme.
- ⚠️ `''` veut dire les poings, donc le JS teste `!== undefined` — un repli « ou sinon la
  valeur de l'archétype » aurait rendu le bâton à qui vient les mains vides, c'est-à-dire
  exactement le bogue qu'on répare. **Après** : on encaisse **6,1 s** avant de tomber au
  lieu de 2,8, et la bagarre se conclut en 2,4 à 3,8 s selon qu'on cogne bien ou mal, avec
  **28 à 92 PV** restants.
- ⚠️ Et elle reste une **bagarre** : deux hommes qu'on laisse faire ont toujours raison de
  toi. 1 juge neuf, **rouge-avant prouvé deux fois** (la fiche `batte`/90, et les 2,8 s)
  dans un **worktree isolé** ; sa moitié « il gagne » est nommée **garde-fou** dans le juge
  lui-même, parce qu'elle était **verte avant** : un banc qui cogne sans jamais rater ni
  tourner le dos chancelle ses deux hommes en continu et gagnait déjà.
