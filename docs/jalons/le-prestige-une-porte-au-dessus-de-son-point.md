# Le Prestige : une porte au-dessus de son point

← [les jalons livrés](README.md) · [le plan](../plan.md)

## Fiche

Martin, 29 sept. 2026.
`test_moteur_js::test_le_joueur_et_les_lieux_sont_sur_des_tuiles_marchables` est rouge sur
dev : « prestige : pas de porte au-dessus du point d'intérêt » — le concessionnaire Prestige
Automobiles (aux Érables). Trouver le commit fautif (bisect), et trancher : le juge ou le
jeu.

## Notes

### Le juge avait tort, cette fois (29 sept. 2026)

**Commit fautif** (bisect, `be1064c5..b80dce1d`) : `6a805c2f` « le Salon clôturé — son blip mène au portail ».
Le point du Salon est passé de `yf + 1` (devant la porte) à `yclo + 1` (devant le portail, côté rue).

**Qui a raison : le jeu.** La décision est écrite dans la note des concessionnaires (« Le lot devant, clôturé ») et
jugée (`test_le_point_du_salon_mene_au_portail`) : devant la porte, on est déjà DANS l'enclos ; le blip mène à
l'entrée du lot. `test_barrieres` l'exige aussi — son parcours à pied compte le fer forgé et le portail comme des
murs, et un point dans l'enclos y rougissait. Le juge du moteur portait une règle devenue fausse pour un lot
clôturé, comme elle l'était déjà pour une carrosserie (le rideau).

**Le remède** : le juge accepte, comme le rideau, le PORTAIL d'un lot au-dessus du point — à condition que la porte
du lot soit dans l'axe (même colonne, au nord du portail) et soit une vraie porte (`porteA`). Commentaire ⚠️ dans
`tests/test_moteur_js.py`.

**La preuve** : le juge reverdit ; deux mutations le font rougir avec le bon message (le point une rangée trop bas,
le point à côté du portail, sous la clôture) ; `test_concessionnaires.py`, `test_concessionnaires_js.py`,
`test_barrieres.py`, `test_moteur_js.py` verts (49) ; ruff vert. Pas de graine en jeu : la ville est la même.

**Pour Martin, mineur** : les ENDROITS CLÉS (`allerALEndroit`) posent le joueur au point et le tournent vers la
tuile au-dessus — au Salon, c'est le portail, pas la porte. Ça se tient (c'est l'entrée du lot), mais la nuit, le
portail fermé, il faut enjamber la clôture.
