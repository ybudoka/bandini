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

**Livré le 30 sept. 2026.** `garage.KLAXONS` (le catalogue), `Garage.klaxonDe` / `klaxonner` (static/js/garage.js),
la corne synthétisée (`corneA`, `Son.SFX.claironner`), `Son.Voix.crier`, `Vehicules.cederLaVoie`, le délit
`fausse_sirene` ; juges `tests/test_klaxons_de_ti_guy_js.py` (sept juges ; six mutations, toutes mordent).

- **« Gens du pays » : −31 LUFS → −11 LUFS**, mesuré au rendu (OfflineAudioContext dans Chromium, `ebur128`) :
  vingt décibels de plus, et deux au-dessus du klaxon ordinaire en jeu (−13,1). Trois dents de scie
  désaccordées (−9, 0, +8 cents), une sous-octave carrée, une saturation `tanh`, un passe-bas à 2,6 kHz, la
  note TENUE (l'ancienne s'éteignait dès la première milliseconde — c'était une pincée, pas une corne) et une
  glissade de 7 % vers la note au départ. ⚠️ Aucun juge ne mesure le volume : le rendu est une sonde, pas un
  juge (le banc Node n'a pas de Web Audio).
- **Les prix** (choisis à défaut d'un mot de Martin) : « Gens du pays » 150 $, « Le Parrain » 200 $, « La
  Cucaracha » 150 $, la corne 300 $, la voix de Ti-Guy 250 $, le whoop 400 $. Un seul à la fois ; la
  fourrière compte le klaxon posé dans le rachat.
- **La corne de 18 roues** (ElevenLabs, −7,8 LUFS en jeu, cinq décibels au-dessus du klaxon) : les passants se
  tassent jusqu'à dix tuiles devant au lieu de cinq, et l'orignal détale de deux fois plus loin.
- **La voix de Ti-Guy** passe par `Son.Voix.crier`, pas `parler` : elle ne coupe pas la réplique d'une mission
  et ne fait pas baisser la radio ; elle sort d'une bande de haut-parleur (380 Hz – 4,2 kHz). Pas encore
  arrivée : le klaxon ordinaire joue. ⚠️ Les slugs sont `ti_guy-garage-crie-<n>` — la série du paquet exige le
  préfixe `ti_guy-garage-`.
- **Le whoop-whoop** : le trafic devant (huit tuiles, dans ton couloir et ton sens) change de voie par le
  déport qui existait (`changerDeVoie`) ; sur une rue à une voie par sens, il n'a nulle part où aller et reste.
  Un policier à pied (pas un vigile) ou une auto-patrouille à douze tuiles : le délit `fausse_sirene`
  (1★, bruyant, `repit_s` 20), et « UN VRAI POLICIER A ENTENDU TA FAUSSE SIRÈNE ».
- **Les klaxons voyagent dans la SUITE du paquet** (`definitions.DANS_LA_SUITE`, clé `klaxons`, avec le texte
  de chaque commentaire) : dans le paquet, le garage passait de 561 à 1 149 octets gzip et le paquet dépassait
  son plafond de 1 075 octets bruts (241 000, tranché par Martin). Tant que la suite n'est pas arrivée, le
  klaxon ordinaire joue et le menu n'en montre aucun. ⚠️ La suite était elle-même à 32 octets de son plafond :
  `replique` ne s'écrit plus que lorsqu'elle diffère du slug.
- Deux bruitages (`corne_a_air`, `whoop_police`, lieu `klaxons`, chargé quand le klaxon est posé ; le whoop
  refait une fois — le premier sortait à −3,2 dBFS de pic — et dosé à 0,7, −11,8 LUFS en jeu) et dix voix de
  Ti-Guy, les engueulades en `[angry] [shouting]` et cie (seules les balises que v3 comprend) : générés,
  ⚠️ **pas écoutés** par une oreille humaine.
- Le banc Node connaît maintenant `createWaveShaper` et le `detune` d'un oscillateur (`tests/banc.js`).
- ⚠️ `test_il_nait_la_nuit_sur_un_sentier_du_bois_et_y_marche` (l'orignal) rougit sur `dev` sans ce jalon
  (a7296c9f) : `carte.def.chemins_des_bois` n'arrive plus au banc.
