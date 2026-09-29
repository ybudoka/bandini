# Les 4 roues

← [le plan](../plan.md) · [les jalons livrés](README.md)

## Fiche

_Demande de Martin (28 sept. 2026) :_ « je veux aussi des 4 roues ».

**Tranché avec Martin le même jour** :

- **Où on les trouve** : **dans les Friches** (deux ou trois garés près des cabanons, à voler), **au chalet du
  rang** (le tien, garé à la deuxième planque, pour faire le tour du lac) et **chez le concessionnaire** (le lot
  d'usagés des Friches — le jalon « Les concessionnaires », en cours dans une autre session).
- **Ce qui le distingue d'une moto** — les quatre à la fois :
  - **rapide hors route** : plein régime sur l'herbe, la friche, le sable et la neige, là où les chars
    ralentissent ; un peu moins vite qu'une moto sur l'asphalte ;
  - **stable** : quatre roues, il ne se couche pas ; on n'en est éjecté qu'en frappant fort ;
  - **deux places** : un passager derrière (la coop à deux, ou un personnage en mission) ;
  - **il saute** : les rampes et les buttes le font voler, comme la moto.
- **Une activité dès le départ** : **une course dans les Friches**, sur le modèle de la course de motoneige —
  des fanions le long des sentiers, un chrono, une prime ; le 4 roues attend au départ.

**Les vagues**, chacune jouable, jugée et livrée seule :

1. **Le véhicule** : sa fiche au catalogue (`vehicules.py`), son dessin, sa conduite (hors route, stable, deux
   places, les sauts), et ses places garées — les Friches et le chalet du rang.
2. **La course des Friches** : le défi, ses fanions le long des sentiers, son chrono et sa prime.
3. **Chez le concessionnaire** : au lot d'usagés des Friches, quand ce jalon-là sera livré.

⚠️ **Ce que ça touche** (à relire avant de coder) :
- **Le modèle est la motoneige** (`docs/jalons/la-motoneige.md`, `vehicules.py` : `hors_neige`, `ejecte`) :
  un véhicule qui va vite sur SON terrain et moins ailleurs.
- **Les Friches sont dans la bande nord**, bâtie avec ses propres dés : ce qu'on y pose (des 4 roues garés,
  des fanions) se pose SANS DÉ, ou avec des dés à part, sinon la bande glisse (`test_canton`, « la bande ne
  bouge pas »). Et la bande est dans la bulle de naissance du terminus : le hasard du départ se rebat (mémoire
  « Juge vert par chance de graine »).
- **Le chalet du rang est un bloc** (`app/blocs/rang.py`) : `Monde.carte` y est le bloc (mémoire « Monde.carte est
  le bloc »).
- **Le catalogue des véhicules** est lu par beaucoup de juges (le trafic, la fourrière, la liste du quai, les
  dessins) : un véhicule neuf doit dire s'il roule dans le trafic (`freq` 0 : non), et avoir son dessin.

## Notes

### Vague 1 — le véhicule, garé dans les Friches et au chalet — **livrée le 29 sept. 2026**

- ⚠️ **Mesuré avant de coder : aucun char ne ralentissait hors route.** L'herbe, la friche et le sable ne
  changeaient rien à la vitesse ; seule la motoneige ralentissait, sur l'asphalte. Martin a tranché (28 sept.) :
  **« les chars ralentissent »**. Chaque fiche porte `hors_route`, la part de son allure gardée sur la TERRE
  (`terre` dans la légende : herbe, friche, sable, allées) : auto 0,66, camion et autobus 0,6, moto et vélo
  0,8 (`vehicules.HORS_ROUTE_DE_CLASSE`) ; ce qui flotte, la motoneige et le 4 roues, 1. Lu par
  `Vehicules.allureDuSol` (avec `hors_neige`), pour le joueur et la police qui le poursuit : le trafic roule
  sur ses rails.
- **Le 4 roues** (`quatre_roues`, classe `moto`) : 4,4 px par image (la moto : 5,2), 70 PV, deux places,
  1 400 $, `freq` 0. **Stable** : `ejecte` porte maintenant un SEUIL à lui (4,2), au lieu du 2,6 de toutes les
  motos — un juge le prouve au banc, le même choc à 3,6 éjecte de la moto et pas de lui. **Il saute** comme
  tout ce qui roule assez vite (rien à faire : aucune rampe ne filtre les classes). **Deux places** : le jeu ne
  refuse personne de toute façon (la coop et un protégé montent dans n'importe quoi), et le passager ne se
  DESSINE pas encore — une dette.
- **Son dessin** (`MACHINE_QUATRE_ROUES`) : quatre pneus aux coins, deux ailes de couleur, le réservoir, la
  selle, les porte-bagages et le guidon large ; le pilote se voit (`deuxRoues`). ⚠️ Le phare et le feu sont
  AU-DESSUS des ailes : plus bas, ils ne se voyaient ensemble qu'à la moitié des caps (`test_poses_vehicules`).
- **Garés** : trois dans les Friches, chacun à côté d'un cabanon (le premier, celui du milieu, le dernier),
  calculés sur la carte finie sans un dé (`app/quatre_roues.py`, clé `quatre_roues`) ; et le tien au chalet du
  rang (`blocs/rang.py`, à plus de 48 px de la place du char, sinon la planque le garde pour SON char). Ils
  **naissent à l'approche** (`static/js/quatreroues.js`), hors de l'écran, hors de la suite des numéros, de
  couleur donnée — rien au démarrage : la bande est dans la bulle de naissance du terminus.
- **Juges** : `test_quatre_roues.py`, `test_quatre_roues_js.py`. Deux mutations rouges (le seuil d'éjection, la
  terre qui ne ralentit plus).
- **Reste** : la course des Friches (vague 2), le concessionnaire (vague 3), et le passager qu'on voit.

### Vague 2 — la course des Friches — **livrée le 29 sept. 2026**

- **La piste** (`quatre_roues.course`, lue sur la carte finie, sans dé) : les Friches sont deux grands terrains
  (au nord et au sud du boulevard du milieu), chacun traversé d'un sentier en croix. Départ au bout SUD de la
  croix du bas — près de la ville, à côté de la cour de Ti-Pout —, puis huit fanions : les bouts ouest et nord
  de la croix du bas, les bouts ouest, nord, est et sud de celle du haut, le bout est de celle du bas, et retour
  au départ. ⚠️ Les croix se trouvent par leur ÉTENDUE (les deux composantes d'allée les plus larges dans les
  deux sens) : la cour de Ti-Pout est en allée elle aussi.
- **Le défi** (`missions.DEFIS`, `quatre_roues`) : l'épreuve `balises` de la motoneige, généralisée — sa course
  se lit dans `regles.course` (`B.defs[...]`, la motoneige par défaut), et le refus dit le véhicule (« EN 4
  ROUES SEULEMENT »). Un lieu de défi neuf, `course:<clé>` : le panneau se plante au départ de la piste.
  60 s, 100 $. ⚠️ Il s'ouvre après le tour des Érables, comme la motoneige : son panneau ne se plante pas au
  démarrage (la bande est dans la bulle de naissance du terminus). Toute l'année. ⚠️ Le lieu neuf est à
  laisser passer AUSSI là où l'on plante les panneaux des défis qui s'ouvrent (`planterLesPanneauxOuverts`) :
  oublié, le panneau ne naissait jamais — c'est le saut des triches vers les défis (`test_debug_js`) qui l'a vu.
- **Faisable, et prouvé sans pilote** : le chemin réel, roulé sans traverser un grillage ni un décor solide
  (un juge le cherche en largeur d'abord), fait 626 tuiles — 38 s à la pleine vitesse du 4 roues ; le chrono
  en laisse 60 pour les virages. ⚠️ Pas de pilote de juge au banc : celui de la motoneige ne gagne qu'une graine
  sur huit. Au banc, la mécanique : le 4 roues posé au départ, les fanions dans l'ordre, la prime payée — et le
  témoin, refusé en auto. Une mutation rouge (l'épreuve qui relirait la course de la motoneige).
- **Reste** : le concessionnaire (vague 3), et le passager qu'on voit.
