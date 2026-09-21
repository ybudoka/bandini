# La nuit ne se vide pas

← [les jalons livrés](README.md) · [le plan](../plan.md)

## Fiche

_Titre d'origine dans le plan : La nuit ne se vide pas (**correctif**, taille 1) — **livré le 13 sept. 2026**_

_Demande de Martin :_ « la nuit, il devrait y avoir moins de monde et de voitures sur les
routes. »

Le mécanisme existe depuis M8 — chaque district a un `rythme` (nuit, matin, soir) que
`Monde.rythme()` applique aux piétons et aux véhicules. ⚠️ **Mais il ne fait presque rien, et
dans le Faubourg il ne fait littéralement rien.**

| District | Piétons | Véhicules en circulation |
|---|---|---|
| **Le Faubourg** | 26 → **19,5** | 9 → **9** |
| Les Quais | 20 → 14 | 8 → 5,6 |
| Les Érables | 14 → 7 | 7 → 3,5 |
| La Pointe | 12 → 4,2 | 4 → 1,4 |
| La Shop | 11 → 1,6 | 9 → 1,3 |

⚠️ **Le Faubourg ne perd pas une seule voiture la nuit**, et c'est arithmétique, pas une
impression : il en déclare 12, son rythme de nuit vaut 0,75, et le plafond `vehicules_max`
vaut **9**. Or 12 × 0,75 = 9. `min(9, 9)` le jour, `min(9, 9)` la nuit — **le plafond mord
avant le rythme**, et la nuit n'existe pas. C'est le quartier où l'on passe le plus de temps,
et c'est le seul où la valeur tombe pile sur le plafond.

⚠️ **Et il garde 19 piétons à 3 h du matin.** Un rythme de 0,75 enlève un quart du monde : ça
ne se voit pas. Une nuit, c'est un trottoir vide et deux phares au loin.

- **Les rythmes de nuit descendent**, et le Faubourg le premier. La Shop à 0,15 est le bon
  exemple : elle se vide pour de vrai, et c'est exactement ce qui la rend inquiétante — le
  reste de la ville devrait avoir le droit d'être inquiétant aussi.
- ⚠️ **Le plafond doit s'appliquer avant le rythme, pas après.** `min(plafond, déclaré) ×
rythme`, et non `min(plafond, déclaré × rythme)`. Sinon tout district généreux le jour se
  retrouve coincé au plafond la nuit, et la correction des nombres ne suffira pas.
- ⚠️ **La police, elle, ne suit aucun rythme.** `zone.police` est lu tel quel : autant
  d'agents à 4 h du matin qu'à midi. Une ville déserte patrouillée comme en plein jour, ça se
  remarque tout de suite — et à l'inverse, une police plus rare la nuit rend la nuit
  intéressante.
- **Les chars stationnés restent**, et c'est juste : on ne rentre pas son char dans sa poche.
  Mais leur répartition devrait tourner — plus dans les entrées des Érables la nuit, moins sur
  les rues commerçantes.
- **Ce que ça donne, et c'est le vrai gain** : la nuit devient un **choix**. Moins de monde,
  c'est moins de témoins, donc moins d'étoiles pour le même geste. Le jeu a déjà tout ce qu'il
  faut pour ça — les témoins, les cônes de vision réduits la nuit — il ne manquait que des
  rues vraiment vides pour que ça se sente.
- **Juges** : dans **chaque** district, la nuit compte strictement moins de piétons et moins
  de véhicules que le jour (un test qui aurait rougi sur le Faubourg) ; le plafond ne masque
  jamais le rythme ; et la police suit le rythme comme le reste.

## Notes

demande de Martin.

- ⚠️ Le rythme de nuit existe depuis M8 mais ne fait presque rien : le Faubourg garde **9
  véhicules sur 9** (12 × 0,75 = 9, pile le plafond) et **19 piétons sur 26**. Le plafond
  s'applique **après** le rythme au lieu d'avant, et la police n'en suit aucun
