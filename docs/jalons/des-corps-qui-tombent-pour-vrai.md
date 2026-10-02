# Des corps qui tombent pour vrai, et les bêtes qu'on écrase

← [les jalons livrés](README.md) · [le plan](../plan.md)

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

## Notes

✅ **Livré** (30 sept. 2026).

- **La planche d'abord** : tous les passants du catalogue peints par `Entites.dessiner`, debout, de
  profil et renversés (un script Playwright du scratchpad). C'est elle qui a trouvé les 14 morts
  debout — aucun juge ne regardait la pose d'un mort.
- ⚠️ **Remplacé le 2 oct. 2026** ([les corps couchés à l'image des debout](les-corps-couches-a-l-image-des-debout.md)) : le gabarit et les 18 poses `couche` tirées de lui sont retirés ; le corps à terre se cuit de la pose debout.
- **Le gabarit** (`SPRITES.joueur.poses.couche`, donc tout ce que la garde-robe habille) : sur le
  dos, la tête à droite, les bras en croix, une tête de cinq rangées où les cheveux entourent le
  visage et où les yeux sont fermés. Quatre variantes comparées à ×9 ; le profil tourné de 90° a
  été essayé et jeté (13 à 26 px de long, les objets pointaient en l'air).
- **Les 14, et les 4 qui avaient déjà l'ancien boudin** (racoleuse, conductrice, avocat,
  homme-sandwich) tirent leur pose du gabarit, avec ce qui les nomme : les balles du jongleur qui
  ont roulé, les échasses tombées à côté, la raclette et le seau du laveur, les feuilles du crieur,
  les lettres et la sacoche du facteur, la bouteille de l'ivrogne, le chapeau du touriste, la
  casquette de la contractuelle, le fard du mime, le capuchon du pickpocket, la pancarte de
  l'homme-sandwich. La mascotte garde la sienne.
- **Les bêtes** : `Vehicules.heurterBetes` (après `heurterPietons`, dans `avancer` et sur les
  rails) regarde `B.betes` — elles restent hors de `B.entites` — et écrase celles dont la fiche dit
  `ecrasable` (le chat, le raton ; pas le goéland) sous un char lancé au-delà de
  `renverse_vitesse_min`, jamais en l'air. `Entites.ecraserBete` : le dessin `chat_ecrase` /
  `raton_ecrase` (à plat sur le flanc, les pattes écartées, la langue, la tête à droite ou à gauche
  à l'empreinte), une tache (`decal`, selon l'option du sang), des poils qui volent, le cri. Le
  corps reste jusqu'à l'oubli ; il ne compte plus dans la naissance (`betesVivantes`) et ne se
  caresse pas. **Aucun dé, aucune étoile.**
- **Le cri** : `chat_ecrase` et `raton_ecrase`, générés par ElevenLabs (lieu `betes`, chargé à la
  première bête qui naît, hors du budget du premier écran) ; la synthèse reste le filet. À écouter.
- **Juges** : `test_corps_qui_tombent_js.py` (9). **Onze mutations, toutes rouges** — dont une qui
  a fait durcir un juge : il comptait les bêtes vivantes sans jamais les faire naître.
- ⚠️ Le train n'écrase pas encore les bêtes (`Train.heurter` ne regarde que l'index des gens).
