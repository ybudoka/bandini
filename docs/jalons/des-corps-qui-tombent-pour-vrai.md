# Des corps qui tombent pour vrai, et les bêtes qu'on écrase

← [le plan](../plan.md)

## Fiche

Demande de Martin (30 sept. 2026) : « valide et améliore les sprites des personnages qui peuvent se
faire écraser, et il faut que les chats et ratons puissent aussi se faire écraser ».

**La validation** — une planche de tous les passants du catalogue, peints par `Entites.dessiner`
comme en jeu, debout, de profil et renversés :

- **14 passants renversables restent DEBOUT une fois morts** : musicien, amuseur, jongleur,
  échassier, exhibitionniste, contractuelle, touriste, ivrogne, jogger, facteur, crieur, camelot,
  laveur, pickpocket. Leur dessin n'a pas de pose `couche`, et `imageDe` retombe sur `bas`. Le jeu
  ment : c'est un **P1**.
- Le corps couché commun (tous ceux qui portent une tenue de la garde-robe) se lit comme un
  boudin : la tête n'est qu'un pixel de peau au bout, ni bras ni cheveux.

**Ce qu'on fait** (tranché par Martin) :

- Une pose `couche` pour chacun des 14, avec ce qui le dit (les balles du jongleur, les échasses
  en travers, le sac du facteur…), et le corps commun retouché : une tête et des bras lisibles.
- **Le chat et le raton s'écrasent** sous un char lancé (au-delà de `renverse_vitesse_min`) : un
  cri, une tache, le corps aplati qui reste au sol jusqu'à ce qu'on l'oublie. **Aucune étoile** :
  les bêtes restent hors du crime. **Leur fuite ne change pas** : il faut foncer dessus ou les
  coincer. Le goéland, lui, s'envole — on ne l'atteint pas.
- ⚠️ Rien ne tire un dé : l'écrasement se lit à l'empreinte ; les bêtes restent hors de
  `B.entites`.
