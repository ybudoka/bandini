# Chaque sortie de la ville a sa rue

← [les jalons livrés](README.md) · [le plan](../plan.md)

## Fiche

Martin, 30 sept. 2026 : « valide que toutes les sorties de la ville aient bien une rue ou une voie qui permette de
sortir. Assure-toi que dans le futur ce soit toujours respecté. »

Les sorties de la ville, ce sont les passages des blocs (`app/blocs/`) : le rang, le ciné-parc, les Galeries et la
villa, tous au bord ouest. Le rang, les Galeries et le ciné-parc ont leur ouverture de rue
(`carte.OUVERTURES_DE_RUE`) ; **la villa, arrivée après, n'en a pas** : sa rue à quatre voies s'arrête sur la rue
de l'ouest, et on pousse contre le trottoir de ceinture. Le juge des blocs ne demandait qu'une tuile « qui se
marche » — un trottoir passait.

- La villa s'ouvre : la rue traverse jusqu'au bord, ses quatre rangées repeintes en dernier et sans un dé, jamais
  dans `voie`.
- Le juge des blocs (`blocs.erreurs`, joué pour CHAQUE bloc) demande maintenant, en ville : au moins deux tuiles
  de chaussée côte à côte sur le bord du passage, et de là une chaussée qui rejoint le réseau des rues de la ville
  sans passer une rue barrée, une barrière ou un décor solide. Un bloc neuf sans sa rue rougit.

## Notes

- **Livré le 30 sept. 2026.** Les quatre sorties vérifiées : le rang (la rue des Quais), les Galeries et le
  ciné-parc (leurs chemins de trois tuiles) avaient leur rue ; **la villa n'en avait pas** — quatre tuiles de
  trottoir de ceinture au bout de sa rue. Quatre tuiles ajoutées à `carte.OUVERTURES_DE_RUE` (y 36 à 39 dans la
  ville d'avant, 146 à 149 sur la carte finie) : la rue traverse jusqu'au bord avec ses lignes (`#`, `-`, `+`,
  `-`), jamais dans `voie`. Comparée clé par clé, la ville ne change que de ces quatre tuiles.
- **Le juge** : `blocs.sortie_sans_rue`, appelé par `blocs.erreurs` pour chaque bloc de `BLOCS`
  (`tests/test_blocs.py::test_chaque_bloc_tient_debout`) — au moins deux tuiles de chaussée côte à côte sur le
  bord du passage, et de là une chaussée qui rejoint au moins la moitié de la chaussée de la ville, sans passer
  une rue barrée (`fermetures`), une barrière (`barrieres`, même celles qui s'ouvrent) ni un décor solide. Les
  quatre sorties en rejoignent 76 %. `test_une_sortie_de_la_ville_sans_rue_se_voit` : le trottoir, une seule
  tuile, une rue isolée et une rue barrée rougissent. Sans l'ouverture de la villa, le juge rougissait sur elle,
  et sur elle seule.
- ⚠️ **Un bloc neuf** ajoute l'ouverture de sa rue à `carte.OUVERTURES_DE_RUE` si aucune rue ne traverse jusqu'au
  bord — le docstring de `app/blocs/` le dit maintenant (il disait « rien d'autre à toucher »).
