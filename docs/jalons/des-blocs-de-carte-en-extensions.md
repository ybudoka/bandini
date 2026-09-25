# Des blocs de carte en extensions

← [les jalons livrés](README.md) · [le plan](../plan.md)

## Fiche

_Demandé par Martin le 25 sept. 2026 : « des blocs de cartes qu'on puisse ajouter comme des extensions au
jeu »._

_Ce que ça donne :_ ajouter un morceau de ville — un chalet dans les bois, un ciné-parc, un centre d'achat,
une île — c'est **écrire un fichier**, comme ajouter une mission : le bloc arrive avec son plan, ses lieux,
ses pièces, ses barrières, et la ville d'avant ne bouge pas d'une tuile.

**Aujourd'hui, c'est déjà fait deux fois — à la main.** L'Île-aux-Corneilles (`app/ile.py`) et l'aéroport
(`app/aeroport.py`) sont chacun un **plan dessiné**, recopié tuile pour tuile par `poser`, **en tout dernier
dans `carte.generer`, sans un dé** : tout ce qui tire une place dans une liste de tuiles l'a déjà tirée, la
ville d'avant reste identique, et un juge la bâtit avec et sans le bloc pour comparer. Chacun a ses
bâtiments, ses zones, ses barrières (`carte.BARRIERES`), ses missions à venir (`MISSIONS_A_VENIR`). La
recette est dans la mémoire du projet (« agrandir la carte sous la trame ») : ce qu'on a appris en payant
26 juges rouges la fois où une rangée de la trame a bougé.

✅ **Tranché par Martin, le 25 sept. 2026 : « la carte fait un black-out et charge le nouveau morceau, et
ça continue. »** Un bloc n'est donc **pas** greffé à la ville comme l'île et l'aéroport : c'est **une carte à
part**, et on y passe par un **fondu au noir** — exactement comme on entre dans une pièce, mais dehors, et au
volant.

**Le jeu sait déjà le faire à moitié.** Entrer dans une pièce (`Jeu.entrer` → `chargerPiece` →
`Monde.entrer`) met la ville **de côté** (`B.exterieur` : la carte, ses entités, l'endroit d'où l'on vient),
charge une petite carte **au noir**, pose les joueurs (le deuxième aussi, en coop), change la toune, rend
l'hélico sourd ; `Monde.restaurer` rend la ville telle qu'on l'a laissée. Ce qui manque au bloc :

- **Un bloc = un fichier** dans `app/blocs/`, qui déclare `BLOC = {…}` : son **plan** (les glyphes de la
  carte, avec ses voies, ses lampes, ses zones — une vraie carte de dehors, pas une pièce), ses **lieux**,
  ses **pièces**, ses **barrières**, et, facultatifs, ses **personnages** et ses **missions**. Il est bâti
  à part : **la ville ne bouge pas d'une tuile**, jamais, quel que soit le nombre de blocs — le problème des
  26 juges disparaît.
- **Des passages**, des deux côtés : dans la ville, un bout de chemin qui sort de la carte, le quai du
  traversier, une rampe de pont ; dans le bloc, l'endroit où l'on arrive et celui par où l'on repart. On
  les franchit **à pied ou en char** — c'est la grande différence avec une porte.
- **Le fondu** : au noir, la ville se met de côté, le bloc se charge (`/api/carte/bloc/<slug>`, avec son
  ETag, sur le modèle de `/api/mission/<slug>`), les joueurs et **le char où l'on est** (avec ses passagers)
  sont posés au passage d'arrivée, et ça continue. Au retour, la ville revient telle qu'on l'a laissée.
- **Le poids** : chaque bloc voyage **à part**, à la demande, et se garde hors ligne **à l'usage** (comme
  les missions). La carte de la ville n'en grossit pas — c'est même une réponse à la dette « les districts
  chargés autour du joueur ».

✅ **Tranché aussi (Martin, 25 sept. 2026 : « ça m'a l'air bon ») — ce que le fondu emporte :**

- **La police** : les étoiles passent le fondu, mais la poursuite **reprend au bord** du bloc — les agents
  d'avant ne suivent pas, de nouveaux arrivent du bloc. Sinon un passage deviendrait un bouton « semer ».
- **Le temps** : l'heure continue de tourner dans le bloc ; la nuit tombe au même moment partout.
- **La mission** : une mission dans un bloc a son GPS qui pointe **le passage** tant qu'on est en ville (et
  l'inverse).
- **L'île et l'aéroport** restent où ils sont : ils marchent, et les déménager ne rapporterait rien. Les
  blocs, c'est pour ce qui vient.

**En vagues, chacune jouable, testée, déployée :**

1. **Le passage à pied, vers un bloc d'essai** : `app/blocs/`, un bloc minuscule (une clairière et un
   chemin), `/api/carte/bloc/<slug>` avec son ETag, le fondu dans les deux sens, la ville rendue telle
   qu'on l'a laissée. Le juge : `/api/carte` ne change pas d'un octet.
2. **En char, et à deux** : le char et ses passagers passent, le deuxième joueur aussi ; les étoiles
   passent et la poursuite reprend au bord.
3. **Un vrai dehors** : le trafic, les piétons, la police, les lampes et la nuit du bloc — tout ce qui lit
   « la carte » lit la carte courante.
4. **Le premier vrai bloc** : un de ceux que le plan attend (la deuxième planque, la cabane à sucre, le
   ciné-parc ou le centre d'achat — à choisir par Martin), avec la sauvegarde qui se réveille dedans et le
   hors-ligne à l'usage.

⚠️ **Ce qui guette** :

- **Une carte de dehors complète** a ses voies, son trafic, ses piétons, sa police, ses lampes, sa nuit :
  tout ce qui lit « la carte » doit lire **la carte courante**, pas « la ville » (les pièces l'ont déjà
  obligé pour une partie du code, pas pour le trafic ni la police).
- **La sauvegarde** : dormir dans un bloc (la deuxième planque) doit se recharger **dans** le bloc.
- **Les règles de ville valent dans un bloc** (rien devant une porte, une lampe par devanture, pas de sable
  hors plage déclarée) : le juge les passe sur chaque bloc comme sur la ville.

**Ce qu'il porte** : la deuxième planque (« plus loin » : un chalet au bout d'un chemin, derrière un
fondu), la cabane à sucre, le ciné-parc, le centre d'achat hanté — quatre lignes du plan qui ont chacune
« poser en dernier, sans dé » dans leur fiche. En bloc, elles ne touchent plus du tout à la ville.

**Juges** : ajouter un bloc ne change pas une octet de `/api/carte` ; on passe un passage à pied et en char,
et on revient à l'endroit exact d'où l'on est parti ; le char et ses passagers passent avec nous (le
deuxième joueur aussi) ; `/api/carte/bloc/<slug>` revalide en 304 et rend 404 pour un bloc inconnu ; un
bloc hors ligne déjà visité se recharge ; une partie sauvegardée dans un bloc s'y réveille.

## Notes

**Vague 1 livrée (25 sept. 2026) : à pied, vers la clairière du lac.** Au bord nord des Érables, sur le
trottoir de ceinture, une plaque « LAC ↑ » ; on pousse vers le haut de la carte, noir, et on est dans **la
clairière du lac** (`app/blocs/clairiere.py`, 40 × 26 : un lac, sa grève, un petit quai de bois, un
chemin, des arbres). Le chemin du sud, sous sa plaque « VILLE ↓ », ramène au passage exact d'où l'on était
parti. Captures : `captures/blocs/` (le passage, la clairière, la clairière de nuit).

- **Côté serveur** : `app/blocs/` (un bloc par fichier, `BLOCS`), `carte_du_bloc` au format de la ville,
  `/api/carte/bloc/<slug>` avec son ETag et 404 pour un inconnu, un gabarit `data-url-bloc` hors de la
  coquille hors ligne, et le paquet des définitions qui ne nomme que les passages (`blocs`).
- **Côté navigateur** : `static/js/blocs.js` — la carte demandée **d'avance** à l'approche (14 tuiles), le
  passage qui ne s'ouvre qu'une fois la carte arrivée (pousser avant, c'est pousser contre un bord),
  `Jeu.entrerDansLeBloc` / `sortirDuBloc` sur le modèle des pièces, mais **dehors** (`B.bloc`, jamais
  `B.interieur`) ; les arbres du bloc sont des entités de décor (`creerDecor`), la ville revient avec les
  siens (`reindexerDecor`).
- ⚠️ **Trois choses que le banc a montrées, et que la fiche ne prévoyait pas :**
  - **Arrêté ou tombé dans le bloc**, le jeu cherchait le poste ou l'hôpital **dans la clairière**.
    `Jeu.revenirEnVille()` (la pièce, puis le bloc) sert maintenant l'hôpital, la prison et les deux
    téléportations de la triche — et `commencer()`, qu'une partie relancée depuis une pièce bâtissait
    sur la pièce (un défaut d'avant les blocs, réparé au passage).
  - **Des passants de la ville naissaient dans les bois** (un livreur, un policier de ronde, et la nuit un
    exhibitionniste) : un bloc dit maintenant s'il a des gens (`gens`, faux pour la clairière) —
    `Entites.peupler` et la ronde de `Police.peuplerAgents` s'y taisent. Recherché, on te cherche quand
    même (la poursuite qui reprend au bord est la vague 2).
  - **Un réseau mort était redemandé à chaque image** — soixante requêtes par seconde près du passage.
    Après une panne, on attend cinq secondes (`Blocs.RELANCE`).
  - Et **un faux vert évité** : le faux `fetch` du banc servait la carte de la ville à toute adresse
    contenant `/api/carte` — la ville entière serait arrivée en guise de clairière. Il sert les blocs à
    part, avant, avec leur 404 et leurs pannes.
- **La sauvegarde** faite dans le bloc retient le passage en ville : une partie rouverte se réveille au bord
  d'où l'on était parti (se réveiller DANS un bloc viendra avec sa planque, vague 4).
- **Juges** : `tests/test_blocs.py` (7 : le bloc tient debout, un bloc mal fait se voit, la ville ne change
  pas d'un octet sans bloc, la route et son 304/404, le paquet ne nomme que les passages, le gabarit hors de
  la coquille, la carte du bloc a ce que `Monde.charger` lit) et `tests/test_blocs_js.py` (11, joués au
  clavier : l'aller et le retour, longer le trottoir ne passe pas, au volant non, la carte pas encore
  arrivée puis le réseau revenu, personne ne naît, jour, nuit et police sans tomber, arrêté → le poste,
  tombé → l'hôpital, la sauvegarde, les arbres, les plaques). **Sept mutations, toutes rouges.**

**Vague 2 livrée (25 sept. 2026) : au volant, à deux, et la police qui reprend au bord.** Capture :
`captures/blocs/4-en-char-dans-la-clairiere.png`.

- **Le char passe**, avec **tout ce qui est dedans** (`dansVehicule` : le deuxième joueur passager, un
  client, un protégé de mission) ; il arrive tourné vers l'intérieur du bloc, et revient tourné vers la
  ville, au même endroit le long du bord. **Le deuxième joueur à pied passe aussi**, comme par une porte.
- **Un char touche le bord à sa demi-longueur** (mesuré au banc : l'auto s'arrête à 14 px du bord nord, le
  camion à 20, la moto à 10, le vélo à 8 — la moitié de leur `longueur`) ; le seuil suit la fiche de chaque
  char (`Blocs.marge`). ⚠️ **Et il doit faire FACE au bord** (à 45° près) : une auto qui longe le trottoir
  de ceinture roule à 8 px du bord, sous son seuil — sans cette condition, on passait en roulant.
- **L'élan continue, à moitié**, et suit le nouveau cap : l'arrivée de la clairière est à dix tuiles du
  lac, et à pleine vitesse le passage jetait le char à l'eau.
- **La police reprend au bord** : les étoiles passent ; les agents d'avant restent de leur côté ; ceux qui te
  suivent **passent le même bord**, trois secondes après toi (`Blocs.DELAI_POURSUIVANTS`), un par étoile et
  trois au plus, en poursuite. Dans un bloc sans passants, aucun agent ne naît au hasard d'un bosquet
  (`Police.peuplerAgents` s'y tait, recherché ou non).
- ⚠️ **Un bogue que le juge des arbres a attrapé** : la liste des voyageurs était devenue `B.entites`, et
  `creerDecor` y ajoutait les arbres du bloc — les deux cents arbres de la clairière se faisaient « poser »
  en file, tous les 14 px, comme un deuxième joueur. La carte a maintenant sa propre copie.
- **Juges** (`tests/test_blocs_js.py`, 18 en tout) : l'aller et le retour **en auto, en camion, en moto et à
  vélo** (le char revient posé en entier dans la carte, tourné vers la ville), un char qui longe le bord ne
  passe pas, ce qui est dans le char passe avec lui, le deuxième joueur passe, la poursuite reprend au bord.
  **Six mutations, toutes rouges** (dont une qui ne rougissait pas au premier essai : le recul du char, que
  le juge regardait 120 images trop tard — il le regarde maintenant à la première image en ville).

**Vague 3 livrée (25 sept. 2026) : le premier vrai bloc — le chalet du rang, la deuxième planque**
(choisi par Martin). Le détail est dans la fiche de [la deuxième planque](une-deuxieme-planque-plus-loin.md#notes).
Ce que la mécanique des blocs y a gagné, pour tous les blocs à venir :

- **Des bâtiments** : un bloc déclare ses `portes` et ses `pieces` (bâties par `carte._piece`, vérifiées au
  chargement) ; on y entre exactement comme en ville.
- **Des matériaux** : un bloc peint ses glyphes autrement (`materiaux` — le bois rond du chalet) sans
  changer de glyphe ; `Monde` met en cache sous `F@bois_rond`.
- **La mémoire** : un bloc se souvient de ce qu'on y laisse, le temps de la partie (`Blocs.garder`,
  `souvenir`) — le char garé au chalet y est encore en revenant.
- **Le réveil dans un bloc** : `partie.bloc`, et un fondu qui ATTEND la carte (`Jeu.transiter`, `attente`,
  jamais plus de dix secondes) — hors ligne, on retombe au passage en ville.
- ⚠️ La vague « un vrai dehors » (trafic, passants, police, nuit d'un bloc) attend un bloc qui en a
  besoin : le chalet n'a ni rue ni voisin. Elle viendra avec le ciné-parc ou le centre d'achat.
