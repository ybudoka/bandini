# Les klaxons de Ti-Guy

← [le plan](../plan.md) · [les jalons livrés](README.md)

## Fiche

_Demandé par Martin le 30 sept. 2026 : « trouve-moi plein d'idées de klaxon à installer ; je veux que celui
existant soit plus gras et plus fort ». Il a choisi, parmi dix-sept idées, les quatre ci-dessous._

**Aujourd'hui** Ti-Guy pose UN klaxon (`garage.PIECES`, `klaxon`), « Gens du pays », joué par deux dents de
scie à 0,18 (`Son.SFX.gensDuPays`) : un kazoo patriotique, deux fois plus faible que le klaxon ordinaire.

- **« Gens du pays » plus gras et plus fort** : trois dents de scie désaccordées, une sous-octave carrée,
  une saturation douce et un passe-bas (le cuivre d'une corne à air, pas le kazoo), le coup de glissade au
  début de chaque note, et le volume au niveau du klaxon ordinaire. Toute la famille des airs en profite.
- **Un klaxon à la fois, au choix** (`garage.KLAXONS`) : une ligne par klaxon au menu de Ti-Guy ; en poser
  un autre remplace le premier. `v.mods.klaxon` devient le slug du klaxon (un vieux `true` = « Gens du pays »).
- **Le Parrain** et **La Cucaracha** : deux airs de plus, joués comme « Gens du pays ».
- **La corne à air de 18 roues** (ElevenLabs) : les passants se tassent de deux fois plus loin, et
  l'orignal détale de deux fois plus loin.
- **La voix de Ti-Guy** : il a enregistré ses engueulades dans le klaxon — « Tasse-toé ! », « Enweye,
  avance ! »… — tirées à l'empreinte, jamais deux fois la même de suite.
- **Le faux whoop-whoop de police** : le trafic devant change de voie pour te laisser passer, comme devant
  une auto-patrouille ; mais un vrai policier à portée d'oreille, et c'est un délit (une étoile).

⚠️ **Ce qui guette** : un son neuf va dans un LIEU (`audio.LIEUX`, le premier écran est plein) ; le poids
du paquet (`test_definitions`) avec les voix neuves ; la sauvegarde des chars (`v.mods`) et la fourrière
(la valeur du klaxon posé).

**Juges** : chaque klaxon joue le sien et seulement le sien ; en poser un remplace l'autre ; un vieux
`klaxon: true` joue encore « Gens du pays » ; la corne tasse plus loin ; le whoop fait changer de voie et
chauffe devant un policier, pas sans lui ; « Gens du pays » sort plus fort qu'avant (mesuré au rendu).

## Notes
