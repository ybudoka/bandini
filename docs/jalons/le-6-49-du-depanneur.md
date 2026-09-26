# Le 6/49 du dépanneur

← [les jalons livrés](README.md) · [le plan](../plan.md)

## Fiche

_Proposé le 25 sept. 2026, ajouté au plan par Martin (« oui génial »)._

_Ce que ça donne :_ un billet de loto à 2 $ chez Ti-Paul, et le lendemain matin, le narrateur lit les
numéros dans le Clairon — presque personne ne gagne, et c'est drôle.

- **Le billet** : un article de plus au comptoir du dépanneur, six numéros tirés pour toi (ou choisis).
- **Le tirage** : fait **la nuit**, calculé du jour de la partie — pas `B.rng()` (il décalerait tout le
  hasard du jeu, règle 8 de `ecrire-drole.md`).
- **Le journal** : le Clairon du matin publie les six numéros et ce que ton billet vaut ; le narrateur les
  lit (le journal et sa voix existent).
- **Les chances** : réalistes, donc minuscules — un petit lot de temps en temps (trois bons numéros), le gros
  lot une fois dans une vie de joueur. Le Clairon titre sur le gagnant quand c'est toi.

⚠️ **Ce qui guette** : les voix des numéros (le narrateur doit dire 1 à 49 : 49 petits clips, une dépense
à trancher par Martin, ou une phrase générique) ; et un gros lot qui casserait l'économie — le plafonner.

**Juges** : le même jour, les mêmes numéros pour tout le monde ; acheter un billet ne tire aucun
`B.rng()` ; un billet gagnant paie le bon lot, une seule fois.

## Notes

_Rien de livré._
**Livré le 26 sept. 2026.**

- **Le billet** : au présentoir du Clairon chez Ti-Paul (le point `journal` du dépanneur porte `loto`),
  « UN BILLET DE 6/49 », 2 $, six numéros tirés pour toi (le choix des numéros n'y est pas : un menu de
  quarante-neuf cases pour une chance sur quatorze millions). Cinq billets par jour.
- **Le tirage** : la nuit, dans `nouveauJour` (`nuitDuLoto`) ; il ne dépend QUE du jour — le même pour
  toutes les parties —, et chaque billet se compare au tirage de son jour, paie son lot et s'en va.
  Ni le tirage ni les numéros d'un billet ne touchent `B.rng()` (jugé).
- **Le Clairon** : les six numéros et ce que vaut ton billet s'écrivent SOUS la manchette du matin (et
  quand on relit le journal). « LE GAGNANT EST D'ICI! » quand c'est toi, à cinq ou six bons numéros.
- **Les chances sont les vraies** (`app/loto.py`) : 3 bons, une fois sur 57, 10 $ ; 4, une sur mille, 75 $ ;
  5, 1 500 $ ; 6, une sur quatorze millions, 25 000 $ — plafonné. Un billet rend 14 % de son prix.
- ⚠️ **Le narrateur ne lit pas les numéros** : la voix, qui était à trancher (49 petits clips, ou une
  phrase générique), n'a rien coûté — la manchette se dit, le 6/49 s'écrit dessous. À Martin de dire s'il
  veut l'entendre.
- **Juges** : `test_loto.py` (les chances, le retour, le plafond) et `test_loto_js.py` (le même tirage pour
  deux graines, un billet qui dépend de la sienne, cinq billets par jour, `B.rng` intact, un lot payé une
  seule fois et écrit au Clairon) ; trois mutations les font rougir.
