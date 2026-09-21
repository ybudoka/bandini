# Le petit train et la montagne russe de la foire

← [les jalons livrés](README.md) · [le plan](../plan.md)

## Notes

demande de Martin : « ajoute un petit train qui fait le tour de la foire et une énorme
montagne russe ». **Le petit train** : une voie fermée de 138 tuiles à trois tuiles du bord
de l'enceinte (la palissade rentre de deux), un glyphe de sol `T` cuit avec le sol, qui lit
ses voisines — droite, quatre courbes en quart de cercle, des planches au passage à niveau
—, une locomotive et quatre wagons d'enfants au pas d'un enfant qui court.

- ⚠️ Elle **coupe l'allée d'entrée** : la première chose qu'on voit en passant l'arche,
  c'est le train.
- ⚠️ **Il s'arrête devant quelqu'un et siffle** — il sonde le long des rails, courbes
  comprises —, et on ne passe pas au travers d'un wagon (une boîte orientée, la règle du
  décor). **Le Colosse** : 150 px au sommet de la chaîne (la grande roue en fait 92), 38
  tuiles de large — plus large que l'écran —, une chaîne, une plongée, un looping de 44 px
  de rayon, une bosse, une gare sous un auvent rayé.
- ⚠️ **Python trace la voie entière en (x, y, z) et la juge** (hauteur, looping de 360°, un
  pied sous chaque bout de voie en l'air) ; le navigateur la peint en deux images cuites et
  fait rouler quatre chariots **par l'énergie** (v²/2 + g·z, moins un frottement), pas par
  un tableau de vitesses.
- ⚠️ **Mesuré : à un frottement de 0,0006, le chariot arrivait en haut du looping à la
  vitesse plancher** — il ne l'aurait pas passé sans elle ; à 0,0002 il y passe à 2,4 px par
  image, et le juge exige que ce soit la gravité qui le passe, pas la ceinture.
- ⚠️ **Deux dessins jetés après les avoir REGARDÉS** : la chaîne posée sur la ligne de
  devant traversait le looping en diagonale et on voyait un nœud — en trois-quarts, ce qui
  monte monte vers le HAUT de l'écran, donc la chaîne va au fond et le looping devant ; et
  des tréteaux croisillonnés serré se lisaient comme des pylônes de haute tension — deux
  tubes et une entretoise.
- ⚠️ **Un nom qui en écrasait un autre** : la vitesse de la chaîne et la tranche de voie de
  la chaîne s'appelaient toutes deux `chaine`, et en fusionnant la fiche dans le paquet la
  tranche devenait 0,55 (`vitesse_chaine`).
- ⚠️ Ni le train ni les chariots ne sont dans `B.entites` (la leçon des bêtes) : ils se
  trient au dessin avec le reste (`Foire.ajouterVisibles`) — les deux moitiés de la montagne
  à leur rangée, pour qu'on marche entre l'aller et le retour — et les 24 pieds sont des
  décors `invisible` qui arrêtent sans se peindre (peints avec la structure : une image au
  lieu de vingt-quatre).
- ⚠️ **Elle se juge à sa BOÎTE pour s'afficher** : son sommet dépasse de neuf tuiles, et le
  tri des entités l'aurait effacée dès que son pied sortait par le bas de l'écran.
  L'enceinte passe de 50 × 21 à 52 × 31 (une rangée de voie de chaque côté, cinq rangs de
  montagne) ; ⚠️ le juge « compacte » mesurait une SURFACE, il mesure maintenant le VIDE —
  le plus grand carré de gazon où il n'y a rien : 7 × 7 sur la foire en ligne, 6 × 6
  maintenant. Deux guirlandes de nuit (la gare, le looping), en fin de liste pour ne jamais
  éteindre un kiosque au plafond de 25 lumières. Sans un dé. Nouveau script `foire.js`. 12
  juges neufs (`test_foire.py`), rouge-avant prouvé par onze mutations ; 2379 tests.
