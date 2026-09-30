# Le lave-auto qu'on traverse, en vitre

← [les jalons livrés](README.md) · [le plan](../plan.md)

## Fiche

_Demandé par Martin le 30 sept. 2026 : « le lave auto doit etre comme le garage mais en vitre, on doit passer
dedans, se faire laver et ressortir de l'autre coté »._

_Ce que ça donne :_ le lave-auto devient un **tunnel vitré qui traverse son bâtiment, de la rue à la ruelle**. On
s'arrête devant le rideau de verre, on paie, le rideau monte ; un **convoyeur** tire le char tout seul sous un toit
de verre — jets, brosses, rinçage, séchoir, qu'on voit d'en haut —, le rideau du fond monte et on ressort dans la
ruelle, une étoile de moins.

**Aujourd'hui** (30 sept. 2026, mesuré sur la ville de la graine) :
- Le lave-auto ([les enseignes qui ouvrent pour vrai](les-enseignes-qui-ouvrent-pour-vrai.md)) reprend la porte
  d'un commerce ordinaire (`app/enseignes.py`, `poser`) : aux Érables, porte des piétons en (33, 191), bâtiment de
  huit tuiles de large (x 29 à 36) et quatre rangées de fond (la façade 191, trois de toit 188-190), une rangée de
  dalle (187) puis la ruelle (185-186) derrière.
- Le lavage est une **baie peinte sur la chaussée** (`ville["lave_auto"]`, 3 × 2 tuiles en (32, 196)) : on y roule
  au pas 1,5 s, on paie 12 $, une étoile tombe (`static/js/enseignes.js`, `majLaveAuto`). Rien n'est solide : les
  autres chars y passent, et on ne voit aucun bâtiment s'ouvrir.
- Le garage sait déjà ce qu'il faut : un rideau qui monte (`Monde.majPortesDeGarage`), un char **admis** et lui seul
  qui passe sous un toit (`Monde.seuilOuvert`, lu par `Vehicules.tuileInterdite`), la patrouille qui bute devant. Ses
  rideaux vivent dans `ville["portes_garage"]`, que six endroits lisent comme des ateliers (le menu du garage, les
  livraisons, la fourrière…).

**Tranché avec Martin (30 sept. 2026)** :
- **De la rue à la ruelle** : on entre par la façade, on ressort par l'arrière du bâtiment.
- **Un convoyeur** : on lâche le volant, le rail tire le char.
- **La police voit, elle n'entre pas** : c'est de la vitre, on ne s'y cache pas ; seul le char du joueur entre, la
  patrouille fait le tour par la ruelle ; l'étoile tombe à la sortie, lavé. En fuite, c'est un pari.
- **Un objet à part** : le tunnel reprend la mécanique du rideau de garage, mais n'entre pas dans `portes_garage`.

### Où il se pose (Python)

⚠️ **SUR LA VILLE FINIE ET SANS UN DÉ**, comme le rideau de Ti-Guy : ni tuile, ni bâtiment, ni décor ne bouge avant
les tirages ; ce qui s'en va (décor, lampe) s'en va après.

- La **baie de chaussée disparaît** (`_baie`). Le lave-auto choisit sa façade comme aujourd'hui (une mesure, la plus
  proche du cœur des Érables), avec une condition de plus : **le bâtiment se traverse**.
  - deux tuiles de vitrine ou de mur (`W`, `F`) côte à côte sur la façade, jamais la porte des piétons ;
  - derrière elles, du **toit du même bâtiment** sur toute sa profondeur, de 3 à 8 rangées façade comprise (l'autobus
    fait 48 px : trois rangées ; au-delà de huit, le convoyeur s'éternise) ;
  - derrière le toit, du **roulable jusqu'à la ruelle** (`x`) — la dalle d'une marge, comme en (29-36, 187) —, sans
    meuble qu'on ne déplace pas.
- Les deux colonnes du tunnel se prennent **du côté du bâtiment qui laisse au bureau la plus grande part d'un seul
  tenant** avec la porte des piétons dedans : le bureau ne se coupe pas en deux.
- **Deux rideaux vitrés** : l'entrée sur la rangée de la façade, la sortie sur la dernière rangée de toit, côté
  ruelle. Ce qui est posé devant l'un et derrière l'autre (décor, lampadaire) s'en va.
- **Le bureau reste** : la pièce des piétons se mesure sur ce qui reste du bâtiment une fois le tunnel ôté (le juge
  `la pièce a les mesures de son bâtiment`, et [des intérieurs fidèles à l'extérieur](des-interieurs-fideles-a-l-exterieur.md)).
- Le navigateur reçoit `ville["lave_auto"] = {"x", "l": 2, "entree", "sortie"}` (les rangées des deux rideaux).
- Aucune façade qui se traverse : pas de lave-auto, et rien ne plante (comme les autres enseignes).

### Le passage (navigateur)

- **L'entrée** : devant le rideau vitré, au pas, avec 12 $, on paie et il monte ; sans l'argent, il reste baissé
  (« LE LAVAGE : 12 $ — PAS ASSEZ »). Seul le char du joueur est admis ; le tunnel reste un mur pour tout autre char
  et pour les piétons.
- **Le convoyeur** : le centre du char passe le seuil, le volant se fige, le char s'aligne sur le rail et avance vers
  la ruelle à vitesse lente et constante ; le rideau d'entrée redescend derrière lui. Selon sa place dans le tunnel :
  **prélavage** (les jets), **brosses** (qui tournent), **rinçage**, **séchoir**. Environ 5 à 6 s.
- **Le verre** : un toit vitré teinté, avec ses reflets ; dessous, le char, l'eau, la mousse, les brosses. **Rien ne
  cache** : `Monde.abrite` reste faux, l'hélico et les patrouilles voient à travers, les phares passent.
- **La sortie** : le rideau du fond monte, on reprend la main quand le pare-chocs arrière a passé le seuil, **une
  étoile tombe** (`Police.unCranDeMoins`, comme aujourd'hui). Le char reste luisant un moment.
- **Sens unique** : le rideau du fond ne s'ouvre qu'au char sur le rail ; de la ruelle, rien ne s'ouvre.
- **Pendant le lavage**, on ne descend pas (« PAS PENDANT LE LAVAGE »). Si le char brûle, si le joueur meurt ou si une
  scène prend la main, le rail s'arrête et les deux rideaux se lèvent.
- **Les sons** : les brosses d'aujourd'hui (`Son.SFX.brosses`), et deux bruitages neufs par ElevenLabs — le jet d'eau
  et le séchoir — dans un lieu chargé au premier geste (`audio.LIEUX`).

### Les juges

- **Python** (`tests/test_enseignes.py`, la ville prise dans `tests/villes.py`) : le tunnel existe aux Érables ; ses
  deux rideaux sont sur le même bâtiment, du toit continu entre eux ; derrière la sortie, du roulable jusqu'à une
  ruelle ; la baie de chaussée n'existe plus ; le bureau garde la porte des piétons et ses mesures ; les juges « ce
  module ne déplace rien » restent verts ; `test_definitions` (le poids du paquet).
- **Au banc, sous Node** : on arrive au pas, on paie, le rail mène le char à la ruelle en moins de N secondes sans
  toucher au volant ; une étoile tombe ; une auto-patrouille bute sur le rideau ; sans argent, rien ne s'ouvre ; de la
  ruelle, rien ne s'ouvre ; descendre pendant le lavage est refusé ; le char détruit dans le tunnel lève les rideaux.
  Chaque règle retirée une fois, pour voir son juge rougir.
- **À l'œil** : une capture Chromium du tunnel en plein lavage, ouverte dans Aperçu avant de livrer.

## Notes
