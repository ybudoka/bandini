# Les terrains de banlieue

← [les jalons livrés](README.md) · [le plan](../plan.md)

## Fiche

_Titre d'origine dans le plan : Les terrains de banlieue (**ajout**, taille 2) — **livré le 14 sept. 2026**_

_Demande de Martin :_ « les terrains des résidences doivent être plus fournis — jardin,
piscine, sentier vers la rue, entrée de voiture, voiture, et autres idées. »

M8 a eu raison sur le principe et le dit dans son propre code : « la banlieue se reconnaît au
**vide** autour des maisons, pas aux maisons ». Les marges sont donc larges — jusqu'à cinq
tuiles. Mais ce vide est aujourd'hui `_jardin()` : du gazon, et un arbre ou un buisson par
dix tuiles, posés au hasard. Or un terrain de banlieue est le contraire du vide — c'est
**plein des traces de la vie de quelqu'un**.

- **L'entrée de voiture, et l'auto dedans.** Une bande d'asphalte de la rue jusqu'au côté de
  la maison. ⚠️ Et voici le meilleur morceau : elle se dessine avec les **cases de
  stationnement** qu'on vient de livrer — une case `^`/`v` tournée vers la maison. Comme
  `placeStationnee()` cherche déjà les cases pour y garer une auto dans ses lignes, **la
  voiture dans l'entrée arrive sans une ligne de code de plus**.
  - ⚠️ **Mais pas dans toutes les entrées.** Si chaque bungalow porte une case, la banlieue
    se remplit de chars stationnés et le budget d'entités y passe. Une entrée sur trois, pas
    plus ; les autres restent de l'asphalte nu — ce qui est aussi la vraie vie.
  - ⚠️ **Une entrée touche la rue**, toujours. C'est la même règle que « toute rangée de
    stationnement touche une allée » : une entrée qui ne rejoint pas la chaussée n'est pas
    une entrée, c'est un carré d'asphalte.
- **Le sentier de la porte à la rue.** `poser_porte()` réserve déjà les deux tuiles devant la
  porte ; le sentier les relie au trottoir. Sans lui, on marche sur le gazon pour entrer chez
  les gens — et c'est précisément ce qui donne l'impression du « pas fini ».
- **La piscine**, hors terre, au fond de la cour. ⚠️ Elle rencontre de plein fouet la vague
  de l'eau : une piscine de banlieue n'est pas la baie. C'est de l'**eau basse** — on y entre
  debout, on ne s'y noie pas — donc le même cas que la rive de sable que cette vague-là
  prévoit déjà. Et un juge : **une piscine ne coupe jamais le sentier** de la porte à la rue.
- **Le grillage entre deux terrains**, et c'est là que ça cesse d'être décoratif : avec la
  vague des clôtures, une haie de grillage s'enjambe. Une poursuite à pied dans Les Érables
  devient une suite de cours à traverser, au lieu d'une course en ligne droite sur le
  trottoir. **C'est la seule idée de la liste qui change le jeu**, et elle ne coûte rien de
  plus une fois les clôtures faites.
- **Le reste, qui n'est que du décor et c'est très bien** : un cabanon au fond, une corde à
  linge, un BBQ sur la galerie, une balançoire là où il y a des enfants (le jeu en a déjà).
- **Deux idées de plus, avec leur crochet** :
  - une **pancarte À VENDRE** sur un terrain de temps en temps — `economie.PROPRIETES` existe,
    et une maison à vendre devient une propriété de plus le jour où on veut en ajouter ;
  - un **chien attaché dans une cour**, qui jappe quand tu passes. ⚠️ Ce n'est pas du décor :
    un chien qui jappe est un **témoin**, il réveille la rue. À décider franchement — soit il
    alerte pour vrai, soit il ne fait qu'un bruit, mais pas « un peu ».
- ⚠️ **Le vrai coût est dans le paquet, pas à l'écran.** `decor` est une liste qui voyage :
  six objets par terrain, sur un district entier, et on sort des bornes (600 Ko bruts, 70 Ko
  gzip). **On mesure avant**, et si ça déborde, le décor de terrain se **dérive de la
  position** (`hash2`) au lieu de voyager — exactement ce qui a été fait pour les usures
  d'asphalte des stationnements.
- **Juges** : toute entrée de voiture rejoint la chaussée ; un sentier relie chaque porte de
  banlieue à la rue, sans passer par une piscine ; une case d'entrée n'apparaît que sur une
  fraction des terrains, mesurée ; et le paquet reste sous ses bornes, sinon le décor se
  dérive et ne voyage plus.

**Livré le 14 sept. 2026.** Le terrain se meuble **après la porte**, et c'est tout le
travail : le sentier part d'elle, la piscine et le cabanon se posent après le sentier. Posé
dans l'autre sens, un cabanon se retrouve sur le pas de la porte.

- **38 entrées de voiture**, et chacune **va jusqu'à la chaussée**. ⚠️ La parcelle ne touche
  pas la rue : entre les deux il y a la bande de devant, deux rangées de **gazon** en
  banlieue. Une entrée qui s'arrête au bord de la parcelle s'arrête dans l'herbe — ce n'est
  pas une entrée, c'est un carré d'asphalte.
- **Une sur trois porte une case**, donc une auto garée : **28 % mesuré**, et le juge mesure
  au lieu de croire. Si chaque bungalow en portait une, la banlieue se remplirait de chars.
- **Un sentier pour 100 % des portes.** ⚠️ La fenêtre de recherche était à six rangées, et
  les marges de banlieue vont jusqu'à cinq, plus deux de bande et deux de trottoir : quinze
  portes sur vingt-sept restaient sans sentier, et **rien ne le disait** sinon le juge.
- **La piscine est ronde**, et c'est un retour de Martin en regardant l'écran : « piscine
  ronde stp et pas 4 carrés ». Chaque tuile porte un **quart du disque** et sait lequel en
  lisant ses voisines (`bloc`) — peintes chacune pour soi, les quatre montraient quatre
  margelles. Elle est de solidité 3 : un piéton la traverse, une auto non, et **on ne s'y
  noie pas** — une piscine de banlieue n'est pas la baie, et la couleur le dit avant le
  joueur.
- **Le paquet** passe de 410 à **413 Ko** bruts et de 51 à **52 Ko** gzip, pour des plafonds
  de 600 et 70. La fiche craignait qu'il faille dériver le décor de la position : ce n'est
  pas nécessaire, et **c'est la mesure qui le dit**.

⚠️ **Trois défauts trouvés en chemin, dont deux qui n'ont rien à voir avec la banlieue** —
c'est le décalage des dés qui les a mis sous le nez des juges :

- **Une plage suivait la boîte, pas la côte.** `_terre_a_cote` promet « on ne dessine une
  rive que là où il y a un rivage », et ne tenait la promesse qu'à l'échelle du bord : une
  seule tuile de terre quelque part le long du côté, et le sable courait sur **toute** sa
  longueur, y compris là où le voisin est de l'eau. D'où des bancs de sable isolés en pleine
  baie, que `boucher_les_poches` doit noyer un à un. Le rivage se vérifie maintenant **rangée
  par rangée**.
- **Un char plus long que sa case.** Une case fait deux tuiles, 32 px ; la remorqueuse en
  fait 36. Garée là, elle dépassait, le garde-fou la poussait hors des tuiles qu'elle
  chevauche, et elle finissait **à cheval sur ses lignes** — à un centième de pixel près, ce
  qu'un juge voit et qu'un œil ne voit pas.
- ⚠️ **Le jeu plantait.** Un témoin qui court vers un agent met `e.vers` à zéro quand sa
  minuterie tombe — et la ligne suivante lisait `e.vers.x`. Une seule image sur des milliers,
  celle où il finit sa course pendant qu'il court : invisible jusqu'à ce qu'un singe tombe
  dessus.
- **Et les Skateux tiennent enfin tout leur stationnement.** Leur bande ne se découpe plus :
  c'est une **piste**. Un terrain de sept tuiles tiré au sort n'en laisse que cinq d'élan une
  fois la rampe posée, et il en faut sept — La Pointe se retrouvait sans tremplin dès que le
  découpage bougeait d'une tuile.

**Ce qui n'est pas livré, et pourquoi** : la **pancarte À VENDRE** et le **chien attaché**.
La fiche dit du chien qu'il faut trancher franchement — « soit il alerte pour vrai, soit il
ne fait qu'un bruit, mais pas *un peu* » — et un témoin de plus dans chaque cour est une
décision de jeu, pas de décor. Les deux restent au réservoir.

## Notes

demande de Martin : « les terrains des résidences doivent être plus fournis ». `_jardin()`
ne posait que du gazon et un arbre par dix tuiles — or un terrain de banlieue est le
**contraire du vide**. Maintenant : **38 entrées de voiture** qui vont jusqu'à la chaussée
(une sur trois porte une **case**, donc une auto — mesuré 28 %), un **sentier de la porte à
la rue** pour 100 % des portes, une **piscine ronde** (quatre tuiles, chacune son quart du
disque), **cabanon / corde à linge / BBQ**. Le paquet passe de 410 à **413 Ko** bruts, 52 Ko
gzip (plafonds 600 / 70).

- ⚠️ Trois défauts trouvés en chemin : une **plage qui suivait la boîte au lieu de la côte**
  (bancs de sable isolés en pleine baie), un **char plus long que sa case** qui finissait à
  cheval sur ses lignes, et un **témoin qui déréférençait `e.vers` après l'avoir mis à
  zéro** — le jeu plantait. 8 juges neufs
