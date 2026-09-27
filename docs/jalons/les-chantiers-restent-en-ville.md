# Les chantiers restent en ville

← [les jalons livrés](README.md) · [le plan](../plan.md)

## Fiche

Trouvé le 26 sept. 2026 en corrigeant le traversier (le même trou lui laissait un pont fantôme), et
Martin : « va-y ». Dans un bloc de carte (le chalet du rang), `B.interieur` est nul et `Monde.carte` est
le BLOC. `Chantiers.maj` ne se gardait que des pièces : un jour qui change au chalet (on y dort) posait la
phase d'un chantier de la ville dans la carte du bloc, la croyait posée — et la ville ne la recevait
jamais. L'équipe et la benne naissaient dans le bloc, aux coordonnées de la ville ; `efface` et `peindre`
répondent à `Monde` quelle que soit la carte qu'il peint, et les invites « MONTER : PELLETEUSE / GRUE »
lisaient les machines de la ville avec la position du joueur dans le bloc.

## Notes

**Livré le 27 sept. 2026.** Pire que prévu : au chalet, le changement de phase ne s'écrivait pas dans le
bloc, il **plantait la boucle du jeu** — `appliquer` lisait `carte.sol[y]` à une rangée de la ville que
le bloc n'a pas (`TypeError … reading 'slice'`). Dormir au chalet un jour de chantier pouvait figer la
partie.

- **Les chantiers sont liés à LEUR carte** : `demarrer` retient la carte de la ville, et `enVille()`
  (`Monde.carte` est-elle celle-là ?) garde `maj` (la rumeur se tait), `efface`, `peindre`, les invites
  de la pelle et de la grue, et `signalDevant`. Une seule règle au lieu d'un `B.bloc` de plus à cinq
  endroits ; elle tient parce que la ville revient toujours sous le même objet (`Monde.restaurer`).
- ⚠️ Les gardes `B.interieur` restent : le juge « rien ne bouge dans une pièce » pose `B.interieur` sans
  changer de carte, et `Histoire`/`Scenes` remettent un instant la carte de la ville pendant qu'on est
  dedans.
- Le juge (`test_rien_ne_bouge_quand_on_est_dans_un_bloc_de_carte`) va au chalet pour vrai, fait passer
  deux pas de chantier, puis revient : rien posé ni né dans le bloc, `efface` muet, et la phase posée en
  ville au retour. Il rougit sans la garde de `maj` (le plantage) et sans celle d'`efface` — la première
  version ne comptait qu'un chantier encore au stade 0, et restait verte sans elle.
