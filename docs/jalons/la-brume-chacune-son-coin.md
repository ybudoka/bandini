# La Brume : chacune son coin

← [les jalons livrés](README.md) · [le plan](../plan.md)

## Fiche

Demande de Martin (21 sept. 2026), devant une capture du quai la nuit, avec treize filles de la
Brume en grappe sur les planches : « il faudrait éviter qu'il y ait des attroupements comme ça ».

La cause : `Entites.peupler` compte la foule **sans** les piétons qui ont un `metier`, et la fille
de la Brume en a un (`compagnie`). La nuit, en zone `brume`, 18 % des naissances sont des filles :
elles ne comptent jamais contre le plafond, ne rentrent jamais par une porte (`quelquUnRentre` ne
prend que les flâneurs) et ne s'oublient qu'hors de la bulle. Plus on reste la nuit sur le quai,
plus il y en a — chaque passant qui rentre chez lui laisse une place, et une chance sur cinq que
ce soit une fille de plus.

Le correctif : **un plafond à elles** (quelques-unes dans la bulle, pas treize) et **un écart**
(chacune son coin : pas de fille neuve près d'une autre). Quand l'une ou l'autre règle refuse, la
naissance devient un passant ordinaire.

- ⚠️ Pas un dé de plus : la règle se lit **après** le tirage des 18 %, et un refus retombe sur la
  naissance ordinaire qui tire ce qu'elle tirait déjà.
- ⚠️ Le juge rougit sans la règle (mutations : sans plafond, sans écart).

## Notes

Livré le 21 sept. 2026. `Entites.peupler` demande à `coinDeBrumeLibre` avant de faire naître une
fille : **trois au plus** dans la bulle (`BRUME_MAX`), et **dix tuiles** entre deux coins
(`BRUME_ECART = 160` px, un tiers d'écran — l'écart se mesure de poste à poste). La règle se lit
après le dé des 18 % ; un refus fait naître le passant ordinaire à la place.

- Deux juges dans `tests/test_brume_js.py`, sur une nuit qui dure (500 places laissées par des
  passants rentrés chez eux) : `test_la_nuit_la_brume_ne_fait_pas_d_attroupement` garde toutes les
  filles et regarde le plafond ; `test_chacune_son_coin` n'en garde qu'une à la fois, pour que le
  plafond ne masque pas l'écart.
- Mutations : sans plafond, **9** filles dans la bulle ; sans écart, des coins à 16 px ; sans la
  règle, **101** filles — la grappe de la capture de Martin.
- Suite complète sur `78e480d` + ce correctif : 3 334 verts, 2 rouges — `test_moteur_js::test_la_foule_ne_se_traverse_plus`
  et `test_histoire_js::test_les_cravates_de_m2_arrivent_quand_madame_thibodeau_a_fini_de_parler`, **rouges aussi sur
  `78e480d` sans lui** : pas de lui.
