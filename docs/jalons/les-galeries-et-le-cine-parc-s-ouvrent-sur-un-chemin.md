# Les Galeries et le ciné-parc s'ouvrent sur un chemin

← [les jalons livrés](README.md) · [le plan](../plan.md)

## Fiche

Martin, 27 sept. 2026, une capture du panneau « GALERIES ← » sous les yeux : « je veux des ouvertures de chemin
pour ces endroits ». Le rang s'ouvre au bout d'une vraie rue (`carte.OUVERTURES_DE_RUE`) ; les Galeries (y 60 à
64) et le ciné-parc (y 94 à 98) n'avaient que le trottoir de ceinture, contre le noir du bord ouest. On poussait
contre un trottoir.

Le trottoir s'ouvre au milieu de chaque passage : trois tuiles d'asphalte à x 0 (les Galeries, y 61 à 63 ; le
ciné-parc, y 95 à 97), un bout de trottoir de chaque côté. Le chemin part de la rue de l'ouest et va jusqu'au bord.
Comme le rang : repeint **en dernier et sans un dé**, et **jamais dans `voie`** (la circulation ne s'engage pas
dans un cul-de-sac au bord de la carte).

## Notes

- **Livré le 27 sept. 2026.** Six tuiles ajoutées à `carte.OUVERTURES_DE_RUE`, posées par `ouvrir_les_rues` à la fin
  de `carte.generer`. Les passages eux-mêmes n'ont pas bougé (`blocs/galeries.py`, `blocs/cineparc.py`).
- Juge : `tests/test_rang.py::test_les_galeries_et_le_cine_parc_s_ouvrent_sur_un_chemin` (trottoir, trois tuiles
  d'asphalte, trottoir ; le chemin touche la rue de l'ouest ; rien dans `voie`). Vu dans Chromium : le panneau
  « GALERIES ← » est posé sur le chemin, le trottoir reprend au-dessus et au-dessous.
- ⚠️ **La bande nord** (docs/jalons/la-ville-s-agrandit-au-nord.md) décalera la ville de `DECALAGE_NORD` : ces
  ouvertures sont écrites dans les coordonnées de la ville d'avant, comme celle du rang, et se décalent avec elle.
