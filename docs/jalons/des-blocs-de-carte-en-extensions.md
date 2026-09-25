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

⚠️ **À trancher par Martin** (ce que le fondu emporte avec lui) :

- **La police** : les étoiles passent-elles le fondu ? Proposition : oui, mais la poursuite **reprend au
  bord** du bloc (les agents d'avant ne suivent pas) — sinon un passage devient un bouton « semer ».
- **La mission** : une mission dans un bloc a son GPS qui pointe **le passage** tant qu'on est en ville.
- **Le temps** : l'heure continue de tourner dans le bloc (la nuit tombe pareil).
- **L'île et l'aéroport** restent où ils sont : ils marchent, et les déménager ne rapporterait rien. Les
  blocs, c'est pour ce qui vient.

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

_Rien de livré._
