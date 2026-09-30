# Le quai du cargo sans sa chaîne

← [les jalons livrés](README.md) · [le plan](../plan.md)

## Fiche

Martin (30 sept. 2026), capture du quai à l'appui : « on n'a pas vraiment besoin de
l'enclos ». Le jour, la chaîne du quai du cargo (`carte.BARRIERES`, `cargo`) ferme l'enclos
où Sven tient la cale du Norvégien, et Sven dit « VIENS EN CHAR » derrière une chaîne
qu'aucun char ne passe : le jeu ment. On retire la barrière ; Sven reste, et on vient le
voir en char de jour comme de nuit.

- ⚠️ Le porte-conteneurs se range autour de la chaîne (`navires.amarrer`) : garder le même
  repère, calculé sans elle, pour ne rien déplacer (m53 compte sur la place des navires).
- ⚠️ Retirer une barrière peut déplacer la ville (vitrines.py : dix juges tombés quand elle
  avait bougé) : comparer la ville clé par clé avant et après.

## Notes

**Livré le 30 sept. 2026.** La fiche `cargo` quitte `carte.BARRIERES` : plus de chaîne autour de la cale
de Sven, plus de « LE QUAI DÉCHARGE LA NUIT », et la cale se rejoint en char à toute heure — « VIENS EN
CHAR » dit enfin vrai.

- ⚠️ **L'enclos reste, sans chaîne, comme REPÈRE.** Le calcul du rectangle (autour de la cale, jamais sur
  l'apron) devient `_Chantier.enclos_du_cargo`, et `navires.amarrer` y range le porte-conteneurs comme
  avant. La ville, comparée clé par clé avec et sans la bande nord, ne change que par `barrieres` : les
  navires, les collections et les autobus sont les mêmes.
- Les juges : `test_barrieres` juge qu'aucune barrière n'entoure la cale (il rougit si la fiche revient) ;
  `test_navires` mesure le cargo depuis la cale ; les deux juges de la chaîne de `test_quai_se_marche`
  sont partis avec elle.
- Deux rouges croisés en chemin, déjà rouges sur la base (`6c52abd1`) :
  `test_chantiers.py::test_la_ville_avec_ou_sans_chantiers_est_la_meme` (les collections) et
  `test_ville_vit.py::test_au_clignotant_rouge_le_trafic_s_arrete_puis_repart`.
