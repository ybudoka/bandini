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

**Ce qui manque, c'est d'en faire un système** — le même passage que les missions ont fait le 20 sept.
2026 (« une mission, un fichier, comme des blocs Lego ») :

- **Un bloc = un fichier** dans `app/blocs/` (l'île et l'aéroport y déménagent), qui déclare `BLOC = {…}` :
  son **plan** (les glyphes de la carte), son **ancre** (où il s'accroche : des rangées **sous** la carte,
  une colonne à l'est, un îlot **dans** la baie, une clairière réservée dans les bois), ses **lieux** (ce que
  `carte.SPECIAUX` et `Histoire.resoudre` connaîtront), ses **pièces** (`_piece`), ses **barrières**, ses
  **zones**, et, facultatifs, ses **personnages** et ses **missions**.
- **Une liste, dans l'ordre** : les blocs se posent dans l'ordre de la liste, après tout le reste — ajouter
  un bloc à la fin ne déplace aucun bloc d'avant.
- **Des points d'ancrage réservés** : la carte garde des endroits prévus pour des blocs (un bout de rue qui
  finit en T vers le large, une clairière). Un bloc qui déborde de son ancre est refusé par un juge, pas
  découvert en jouant.
- **Le reste du jeu les voit** : le GPS, le carnet, la carte plein écran, les lignes d'autobus et le
  traversier (s'ils doivent y aller), la sauvegarde (un lieu de bloc a un identifiant stable).

⚠️ **À trancher par Martin — « extension », ça veut dire quoi ?**

1. **Des blocs toujours là** (le plus simple) : on les ajoute au dépôt, ils font partie de la ville pour
   tout le monde. « Extension » veut dire « facile à ajouter », pas « optionnel ».
2. **Des blocs qu'on allume** : un écran EXTENSIONS dans OPTIONS, chaque partie garde **sa** liste de blocs.
   ⚠️ C'est beaucoup plus cher : la carte d'une partie dépend alors de ses blocs (un paquet `/api/carte` par
   combinaison, ou une carte assemblée dans le navigateur), une vieille sauvegarde doit se charger sans le
   bloc qu'elle n'avait pas, et une mission ne peut pas dépendre d'un bloc éteint.
3. **Des blocs qui se débloquent en jouant** (entre les deux) : toujours dans la carte, mais fermés
   (barrières, comme l'aéroport) jusqu'à une mission ou un achat — c'est ce que le jeu fait déjà.

La recommandation : **1, puis 3** — c'est ce que l'île et l'aéroport sont déjà, et ça ne coûte rien à la
sauvegarde. Le 2 n'a de sens que si des blocs viennent un jour de quelqu'un d'autre que ce dépôt.

⚠️ **Ce qui guette** :

- **Le paquet** : la carte voyage à part (`/api/carte`, 50 000 octets gzip de plafond, et elle en est
  près). Chaque bloc l'alourdit : c'est le déclencheur de la dette « les districts chargés autour du
  joueur » — un bloc pourrait être le premier morceau chargé à la demande.
- **Les juges qui supposent une seule terre ou une carte = la trame** (la liste est dans la recette : la
  taille de la carte, les districts, les terres par île, la nage, les quais) — les écrire pour N blocs, pas
  pour deux.
- **Les règles de ville valent dans un bloc** (rien devant une porte, une lampe par devanture, pas de sable
  hors plage déclarée) : le juge les passe sur chaque bloc comme sur la ville.

**Ce qu'il porte** : la deuxième planque, la cabane à sucre, le centre d'achat hanté, le ciné-parc — quatre
lignes du plan qui ont chacune « poser en dernier, sans dé » dans leur fiche. Fait d'abord, il les rend
chacune plus simples : un fichier de bloc au lieu d'une greffe à la main.

**Juges** : la ville avec et sans chaque bloc est identique hors du bloc (à la tuile et au décor près) ;
chaque bloc tient dans son ancre ; chaque lieu d'un bloc est atteignable (ou fermé par une barrière
déclarée) ; l'île et l'aéroport, déménagés en blocs, donnent exactement la même carte qu'avant (l'empreinte
de `/api/carte` ne bouge pas).

## Notes

_Rien de livré._
