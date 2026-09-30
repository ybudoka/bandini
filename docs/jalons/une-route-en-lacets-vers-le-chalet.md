# Une route en lacets vers le chalet

← [les jalons livrés](README.md) · [le plan](../plan.md)

## Fiche

Martin (30 sept. 2026) : « est-ce techniquement possible d'avoir des courbes dans les rues ? » La ville
est une grille de tuiles de 16 px, et le champ `voie` ne connaît que `> < ^ v` : tout le trafic, la
police, les autobus, le GPS et `voies_bloquees` lisent ces flèches. Une ville courbe partout serait un
autre jeu. Martin a tranché pour **quelques routes courbes posées à part**, et la première : **la montée
vers le chalet**, dans le bloc du rang (`app/blocs/rang.py`).

Le rang est le bon endroit pour commencer : c'est un plan dessiné à part (la ville ne change pas d'un
octet), et **un bloc n'a pas de trafic** (la vague 3 des blocs), donc aucune IA n'a besoin de suivre la
courbe. Il reste un tracé, un sol et un dessin.

**Le tracé** (tranché par Martin : « Lacets dans le bois », chalet au bout du chemin). Le vieux chemin de
gravier en L (tout droit de l'entrée est jusqu'à x=17, puis au nord le long du lac) devient une route
sinueuse de 3 tuiles de large. On entre à l'est (rangées 23 à 26, le `retour` ne bouge pas), on passe
devant l'allée de la cabane à sucre (qui reste tout près de l'entrée : c'est un lieu public), on plonge au
sud-ouest dans le bois en deux grands virages, on remonte le long du lac (l'embranchement du quai reste),
et on arrive **au chalet par l'ouest, au bout du chemin**. L'allée droite qui descendait du chalet vers
l'entrée disparaît : sans ça, on y serait en 20 tuiles et les lacets ne mèneraient qu'au quai. Le
croquis d'accord (points de passage, en tuiles du bloc) :
`(80,25) (66,25.5) (52,27) (42,31) (40,37) (30,42) (18,41) (9,34) (12,26) (20,21) (30,21.5) (40,20)`.

**La surface** (tranchée par Martin) : du **gravier qui ralentit**, le `g` d'aujourd'hui (`terre`) —
une auto y ralentit, le 4 roues du chalet file. Ça donne une raison de prendre le 4 roues.

**L'approche** (tranchée par Martin : « tracé lisse ») :

- **Python, sans un dé.** `BLOC["chemins"] = [{"points": [...], "largeur": 3, "sol": "g"}]` dans
  `rang.py`. Une fonction générique de `blocs/__init__.py` échantillonne la spline (Catmull-Rom, un point
  tous les 4 px, comme la voie de la montagne russe), pose `sol` sur chaque tuile dont le centre tombe
  dans la largeur, et remet en herbe les arbres et buissons à moins d'une tuile du bord. Le chemin
  s'applique au plan **avant** `sol_du_bloc` ET `decor_du_bloc`, pour que les deux s'accordent. Le paquet
  du bloc exporte `chemins` (les points échantillonnés) pour le JS. Réutilisable par un autre bloc, et
  plus tard en ville.
- **JS.** `blocs.js` peint, juste après le sol, un ruban de gravier au **bord lisse** : deux ornières,
  une lisière d'herbe plus foncée. Le ruban déborde un peu les tuiles `g` pour couvrir leurs marches
  d'escalier, et prend la même peinture de saison que le `g` (blanc en janvier, puisqu'une partie commence
  l'hiver). La collision et la terre qui ralentit restent sur les tuiles ; l'écart visuel reste sous 12 px.

**Les juges.** Python : depuis l'arrivée, on rejoint encore les deux portes, le char, le quai et l'arrêt
de la calèche ; le plus court chemin **en char** de l'arrivée au chalet passe par les lacets (longueur
minimale) ; aucun décor solide sur la route ni sur sa lisière ; un rayon de virage minimal, pour qu'une
auto le prenne ; la ville ne change pas d'un octet ; et la mutation (retirer la règle, le juge rougit). JS :
une auto pilotée au banc le long du tracé atteint la place du char sans heurter d'arbre ; le ruban couvre
chaque tuile `g` de la route ; une capture Chromium en été et en janvier avant de livrer.

**Hors périmètre** : le trafic dans le rang (la vague 3 des blocs), une vraie pente, des courbes en ville.

- ⚠️ **La raquette en babiche** (`collectionner.py`, la bebelle du rang) se pose sur la tuile la plus loin
  à pied de l'arrivée, les arbres comptant comme des murs. Dégager la lisière de la route va sans doute la
  déplacer : c'est une règle sans dé, donc permis, mais le juge qui la place doit rester vert et la
  nouvelle place doit rester « au fond du rang ».
- ⚠️ **Le sentier de la calèche** (`CABANE["caleche"]["chemin"]`, x 48 à 75, rangées 30 à 44) et son
  raccord au chemin (x 62-63, rangées 27-28) ne bougent pas ; la route passe à l'ouest de sa boucle.
- ⚠️ **La planque** : la place du char (46,18) et le 4 roues (52,19) ne bougent pas ; l'allée courte devant
  la porte du chalet se raccorde à la route qui arrive par l'ouest.

## Notes
