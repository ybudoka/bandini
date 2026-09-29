# Les passants restent au trottoir quand on les démêle

← [les jalons livrés](README.md) · [le plan](../plan.md)

## Fiche

Martin, 29 sept. 2026 : « garder les passants au trottoir ». Vu en réglant le juge du
signaleur ([notes](trois-juges-rouges-neufs-sur-dev.md#notes)) : une passante qui flâne
contre un corps figé (le signaleur d'un chantier) est poussée par `demeler` au bord de la
chaussée et y reste ≈ 8 s ; le trafic s'arrête pour elle jusqu'à ce qu'un char force.
`demeler` protège déjà l'enfant à vélo de ce cas, pas les autres passants. Étendre la
garde : démêler ne pousse jamais un passant sur la chaussée (il glisse le long du trottoir,
ou c'est l'autre qui cède, ou il reste collé).

- ⚠️ La foule de toute la ville en dépend : les juges « ne déplace rien », de la foule
  (`test_pietons_js`), du trafic et des passages piétons doivent rester verts sur plusieurs
  graines ; deux corps jamais sous 10 px (la mémoire « Deux corps jamais sous 10 px »).
