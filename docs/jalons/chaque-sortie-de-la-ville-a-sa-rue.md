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
