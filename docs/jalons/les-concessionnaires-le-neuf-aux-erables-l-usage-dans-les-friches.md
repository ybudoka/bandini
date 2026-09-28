# Les concessionnaires : le neuf aux Érables, l'usagé dans les Friches

← [le plan](../plan.md) · [les jalons livrés](README.md)

## Fiche

_Demande de Martin (28 sept. 2026) :_ « je veux un vendeur de voitures neuves dans un quartier riche avec plusieurs
voitures dans le stationnement et un vendeur de voitures usagées dans un quartier plus pauvre ou industriel ».

**Tranché avec Martin le même jour** :

- **On achète ET on vole.** Un vendeur au comptoir vend les chars du lot ; le char payé est à toi (`aToi`) et y
  monter n'est pas un vol. Le prendre sans payer en est un.
- **Les lieux** : le neuf aux **Érables** (le cossu), l'usagé dans les **Friches** (la bande nord, pauvre et
  industrielle).
- **Les noms** : **Prestige Automobiles** (le neuf) et **Chez Ti-Pout — Autos usagées** (l'usagé).

### Ce que ça donne

**Prestige Automobiles, aux Érables.**
- ⚠️ **Pas la quincaillerie**, pourtant proposée d'abord (et acceptée) : c'est la SEULE porte `artisan` de la ville
  d'avant, et `f04` (le couteau) et `p01` (la batte) y envoient acheter ; `test_chaque_famille_de_commerce_ouvre_une_porte`
  la garde. Et la rangée commerçante des Érables n'a que deux portes (la quincaillerie, le lave-auto), toutes deux
  uniques ; le troisième îlot est la cour des Chevreuils.
- **La place** : le **stationnement de l'îlot `mm<mm`** (rangée 3, tout cossu), deux rangées de neuf cases (`^` au
  nord, `v` au sud, îlots `I`) avec leur allée — mesuré le 28 sept. 2026 à x 56-66, y 168-174 de la ville finie.
  Le salon se **bâtit sur la moitié sud** (les cases `v`), sa façade vitrée sur la rue du sud ; la moitié nord
  reste le **lot d'exposition** (neuf places, l'allée comprise). Le lot se trouve par une MESURE (le plus grand
  stationnement d'un îlot cossu des Érables), jamais par un tirage ni par des coordonnées écrites en dur.
- **Dedans** : des vitrines, un char en montre si la pièce le permet (sinon un podium vide et une plante), un
  bureau, et le vendeur en complet derrière son comptoir. La pièce à la mesure du bâtiment.
- **L'enseigne** cossue (lettres dorées, `COMMERCES_COSSUS`).
- **Le stock** : berline neuve, sport, cabriolet, luxe, au prix du catalogue (`vehicules.CATALOGUE`, 600 à 5 200 $),
  pleine vie ; l'**alarme** sur TOUS les chars du lot, la berline comprise.

**Chez Ti-Pout, dans les Friches.**
- **La place** : une cour de gravier grillagée **contre une rue** (les terrains vagues des Friches sont au milieu
  de l'herbe, loin du trottoir), avec une trouée dans le grillage pour sortir ; mesurée comme au Salon.
- **Une roulotte-bureau** (une petite pièce : un bureau, une chaise, la cafetière, Ti-Pout en chemise), des
  fanions, une pancarte « FINANCEMENT FACILE ».
- **Le stock** : compacte, familiale, camionnette, un vieux camion, en couleurs délavées, **60 % de vie**, environ
  **40 % du prix du catalogue** ; aucune alarme.

**Acheter.** Au comptoir, un menu liste les chars du lot (modèle, couleur, prix). Payer (`payer`) rend le char
dehors `aToi` ; on sort, on embarque. Le garder d'une partie à l'autre, c'est le garer à la planque
(`sauvegarderPartie`, déjà là). La place vidée se remplit **le lendemain** ; le stock du jour se calcule par
empreinte (le jour et la place), sans dé.

**Voler.** Monter dans un char du lot sans payer = `vol_vehicule` ; l'alarme chez le neuf, rien chez l'usagé.

### Les vagues

1. **Les deux lots et leurs chars** : le Salon bâti, la roulotte posée, les chars du lot qui naissent et se
   volent (l'alarme au neuf). Jouable seul : Martin voit les lots et peut voler.
2. **Le comptoir et l'achat** : les deux menus, `aToi`, le lot qui se remplit le lendemain.

### ⚠️ Ce que ça touche (à relire avant de coder)

- **Poser sur la ville finie, en dernier, sans dé** — la recette du lot du poste (`poser_les_lots_et_les_rideaux`)
  et du dojo : un module `app/concessionnaires.py`, appelé par `carte.generer` après `enseignes.poser` pour le
  Salon, et après `canton.poser` (dans `nord.poser`) pour les Friches. Ce qui s'y était posé (décor, lampe) s'en
  va ; `ville["sol"]` réécrit sur les seules rangées touchées. La clé neuve de `ville` va dans `nord.DECALAGES`
  (mémoire « La carte descend sous la bande nord »).
- **Bâtir un bâtiment neuf** (le Salon) sur la ville finie : toit, façade, porte, `toits`, `portes`,
  `devantures`, `points_interet`, et la pièce dans `interieurs`. La pièce à la mesure du bâtiment
  (`test_la_piece_a_les_mesures_de_son_batiment`).
- **Les juges « ne déplace rien »** (dojo, enseignes, carrosseries, canton, aéroport, relief…) : les comparer sans
  le module, un dé par choix (mémoire « Juges ce module ne déplace rien »).
- **Les chars du lot en JS** : le modèle de `majGaresDeService` — couleur donnée (sinon `B.rng` décale tout),
  silhouette forcée (`options.sprite`), nés dans la bulle, un marqueur à eux, et **exclus du compte des chars
  garés** (sinon les dés de `peupler` glissent ; `test_poste_et_garage_js`, `test_cabriolet_js`, `test_la_nuit_js`).
- **Les Friches touchent la bulle de naissance du terminus** (le Petit-Canton y est) : les juges qui tiennent par
  une graine (mémoire « Juge vert par chance de graine »).
- **Le poids du paquet** (`test_le_paquet_reste_leger`, `test_definitions`).
- **Voir avant de livrer** : une capture du Salon et de la cour (mémoire « Regarder une couche peinte »), et un
  juge joué au banc (acheter puis embarquer ; voler et entendre l'alarme).

## Notes
