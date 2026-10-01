# Les sauts de triche retrouvent la foire l'hiver

← [les jalons livrés](README.md) · [le plan](../plan.md)

## Fiche

La suite complète du 30 sept. 2026 : cinq juges des sauts de triche (`test_debug_js.py` :
chaque mission, chaque défi, chaque donneur, le panneau du défi, sortir du char) rougissent
depuis « la foire fermée l'hiver » (068ee261) — une partie commence en janvier, la foire est
cadenassée, et LANCER UN DÉFI ou CHEZ UN DONNEUR n'y entrent plus (le tir, les canards, le
Bonimenteur). Tranché par Martin (1er oct.) : la triche ouvre la foire — sauter à un défi ou
à un donneur de la foire la déverrouille, comme LANCER UN DÉFI ouvre déjà un défi caché ;
les juges de la foire fermée restent tels quels.

- ⚠️ Sur le dev du 1er oct., les mêmes juges tombent aussi sur s01 et sur Gilles (porte de
  la fourrière) : à démêler, chaque échec a sa cause.

## Notes

**Livré le 1er oct. 2026** (`static/js/hud.js`, `foire.js`, `histoire.js`, `base.js` ; juges dans
`tests/test_triches_manquantes_js.py`, les bascules dans `test_debug_js.py` et `test_classeur_js.py`).
Deux causes, pas une — la bissection l'a dit.

- **La foire fermée l'hiver** (068ee261). Une bascule de plus dans TOUJOURS, FOIRE OUVERTE L'HIVER
  (`triches.foire`, sauvée avec la partie). `Foire.fermee()` la lit — donc tout ce qui lit `fermee()`
  (les manèges, les comptoirs, l'arche, la foule, la file) voit la foire ouverte —, et
  `Histoire.absentLHiver` aussi : le Bonimenteur revient (`majSaisonniers(true)` au saut, comme au
  dégel). Le derby (`hors_hiver`) suit la foire. Un saut vers un défi de la foire, son derby ou chez le
  Bonimenteur L'ALLUME tout seul, l'hiver seulement : l'été, rien à ouvrir. L'éteindre recadenasse.
- **Gilles dans la cour de la fourrière** (9833b7bd, « chacun à sa place »). Il se tient maintenant dans
  le lot, qui est de l'asphalte : `placeAupres` ne voulait pas de chaussée et le saut disait
  INTROUVABLE (s01, s08, s12 avec lui). À défaut d'une tuile hors chaussée, le saut prend l'asphalte —
  jamais sous un char saisi.
- Sept mutations (la triche lue par `fermee`, le saut de défi qui ouvre, l'été qui n'allume rien, le
  Bonimenteur présent et reposé, le repli sur l'asphalte, pas sous un char) rougissent chacune leur juge.
  ⚠️ « Pas sous un char » passait à vide au premier jet : aucun char saisi au départ ; le juge en gare un.
