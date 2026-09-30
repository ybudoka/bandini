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
