# Les véhicules vus de profil

← [les jalons livrés](README.md) · [le plan](../plan.md)

## Fiche

_Titre d'origine dans le plan : Les véhicules vus de profil, comme les piétons (**correctif**, taille 5)_

_Demande de Martin :_ « une refonte complète des véhicules. Je les veux comme les piétons,
de profil. »

**Tout ce qui est debout dans Bandini est dessiné debout — sauf le char.** Le passant fait
12 × 16 et il est ancré à ses **pieds** (`ancre: [6, 15]`) ; l'arbre fait 18 × 26, le tronc
en bas ; le lampadaire, 8 × 30 ; le banc se voit de côté, avec ses pattes ; le feu de
circulation a son poteau (13 × 24) ; et les clôtures nord-sud ont été refaites **vues par la
tranche** le 13 septembre, parce que Martin l'a demandé en disant déjà exactement ça. La
ville, elle, est un **sol** : de l'asphalte, des toits, et l'ombre d'un mur qui tombe vers le
sud. Le char est la **dernière chose que le jeu regarde d'aplomb** — et le code le dit
lui-même, en toutes lettres, dans M9 : « Vu d'en haut, un char est un TOIT (…) ce n'est pas
le pare-brise qui nomme un véhicule à douze pixels de large, c'est ce qu'il porte sur le
dos. » C'était vrai. Ça cesse de l'être le jour où on ne le regarde plus d'en haut.

⚠️ **C'est un correctif, pas un ajout** : rien de neuf n'apparaît dans le jeu. Les mêmes
douze véhicules, redessinés pour qu'ils regardent dans le même sens que tout le reste.

**Mesuré avant d'écrire :**

- **12 véhicules, 32 variantes de couleur, 1 900 lignes** de grilles de pixels dans
  `sprites.js`. C'est ça qu'on jette et qu'on redessine.
- Le char tourne par **32 caps cuites** (`Atlas.cuireRotations`), une tous les 11,25°. Le
  parc entier, cuit, pèse **1 024 canevas — 6 Mo**.
- Et il ne s'en sert presque jamais : sur **3 129 relevés** de chars en marche (600 images de
  trafic), **94,5 % sont à moins de 2° d'un cap cardinal**, 97 % à moins de 10°. La rotation
  libre coûte six mégaoctets pour **3 % du temps**.

**La règle : une vue = un dessin, pas une rotation.** Le char choisit sa pose comme le
passant choisit sa face — `regarder()` tient déjà la règle en une ligne
(`Math.abs(dx) >= Math.abs(dy)`). Trois dessins par véhicule : **de profil** (miroité pour
l'autre sens), **de dos** (il s'éloigne), **de face** (il vient). L'atlas tombe de 1 024 caps
à **96**, et de 6 Mo à **0,3 Mo**.

**⚠️ Et voici ce que ça coûte, dans l'ordre où ça fait mal.**

1. ⚠️ **Le dessin cesse de dire l'encombrement.** Un char fait 28 px de long ; de profil, ces
   28 px se voient. **De dos, non** : il devient un objet de 14 px de large, et ses 28 px
   d'asphalte disparaissent de l'écran. Or se garer dans une case, juger l'espace entre deux
   chars, reculer dans une ruelle, tout ça se joue **à l'œil**. C'est le vrai prix de la
   demande, et il se paie en jeu, pas en pixels. Deux parades, à décider :
   - **l'ombre au sol permanente**, à l'empreinte exacte du catalogue, sous tous les chars,
     tout le temps — elle n'existe aujourd'hui qu'en vol (`v.z > 0`). Dix lignes, et elle
     rend à l'œil la longueur que le dessin ne montre plus ;
   - le **trois-quarts** au lieu du profil pur pour les vues de dos et de face : on voit
     alors un bout du toit qui fuit, donc un bout de la longueur.
   - **Recommandation : les deux, l'ombre d'abord** — c'est elle le filet, et elle se mesure.
2. ⚠️ **L'ancre change de sens.** Un char est cuit **centré** (`ancre: [16, 8]`) ; un passant
   est ancré à ses pieds, et c'est ce qui le pose au sol et le trie par y (`y de tri = y`,
   `y de dessin = y - z`). Un char debout s'ancre pareil, à sa ligne de sol, sinon il flotte.
   Ça touche le tri, l'ombre, le saut de rampe, et **la remorqueuse**, qui pose sa charge au
   pixel et dans l'axe.
3. ⚠️ **Les 3 % obliques sont exactement les virages** — le seul moment où l'on regarde
   vraiment un char tourner. Trois poses y font donc un **saut**. Le passant a le même défaut
   et personne ne le voit : il tourne en un pas, le char met une seconde et demie. Les
   parades, par prix croissant : accepter le saut ; ajouter deux poses de trois-quarts (**5
   poses, 160 caps, 0,5 Mo**) ; ou **pencher** le dessin de quelques degrés pendant le virage
   — ⚠️ mais au-delà d'une quinzaine de degrés, un profil penché redevient une vue d'en haut
   de travers, et on a refait le problème qu'on venait de régler.
4. ⚠️ **Le char sera TRAPU, et il faut le vouloir.** Le passant est dessiné à **9,1 px/m**
   (16 px pour 1,75 m) ; le char à **6,2 px/m** (28 px pour 4,5 m). À l'échelle du passant,
   un toit d'auto (1,45 m) fait **13 px de haut pour 28 px de long** — un vrai char en ferait
   41 de long. **On ne peut pas l'allonger : c'est la rue qui tient la longueur** (les voies,
   les cases de stationnement, les lignes d'arrêt, tout le trafic). Donc un char court et
   haut, comme dans les jeux de petites autos. Et un passant plus grand que le toit d'une
   auto, ce qui est vrai dans la vie.
5. ⚠️ **Les quatre dessins de M9 sont à jeter**, et c'est le gros du travail. Le camion,
   l'autobus, l'ambulance et la remorqueuse ont été dessinés **pour être des toits** : les
   nervures de la caisse, les trappes, la croix rouge, le bras de levage. De profil, ce qui
   nomme un véhicule est sa **silhouette** — la caisse haute, les fenêtres en bande de
   l'autobus, le gyrophare, le bras qui dépasse à l'arrière.
6. ⚠️ **Le conducteur cesse d'être peint dans le véhicule, et c'est un cadeau.** La palette du
   vélo porte déjà une peau (`s`) et des cheveux (`h`) : le cycliste est **cuit dans le
   vélo**, de la même couleur pour toujours. De profil, il redevient ce qu'il aurait dû être
   — un passant **assis dessus**, avec ses propres couleurs, ce qui applique aux deux-roues
   le correctif des « sortes de gens ». Et dans une auto, on verra enfin **une tête derrière
   la vitre**.
7. ⚠️ **L'épave et le vélo plié se servent de la rotation libre** pour dire « il est tombé »
   (`v.angle += (rng - 0.5) * 1.6`). Debout, ça demande une pose de plus : **couchée** —
   exactement ce que le passant a déjà (`couche` : une image, pas un canevas qui tourne).
8. ⚠️ **La physique ne bouge pas d'un pixel**, et c'est ce qui rend la fiche faisable :
   `cercles()`, les masques, les voies, les cases de stationnement, le crochet, les défonces,
   le trafic — tout continue de voir un rectangle vu d'en haut. On ne touche **qu'au
   dessin**. En revanche, les juges qui mesurent des **pixels** changent (l'ombre en vol, le
   « nez » du char) ; ceux qui mesurent des **positions** — la charge de la remorqueuse collée
   et dans l'axe — tiennent tels quels.
9. ⚠️ **Ça se fait AVANT d'ajouter des véhicules.** M12 promet un tramway et un traversier, et
   le bateau attend son sprite en dette. Chaque véhicule dessiné avant la refonte se dessine
   deux fois.

**Juges** : chaque véhicule a ses trois poses, aucune manquante et aucune empruntée à un
autre ; la pose suit le cap avec **la même règle que la face d'un passant** (un seul code,
pas deux jeux de seuils) ; l'ancre est la ligne de sol, mesurée — un char au sol ne flotte
pas d'un pixel ; l'ombre au sol a l'empreinte du catalogue, pour tous les chars, tout le
temps ; le tri par y met le char devant le passant qu'il dépasse et derrière celui qu'il
croise ; une épave et un vélo plié ont leur pose couchée ; la remorqueuse pose toujours sa
charge au pixel et dans l'axe ; et **l'atlas du parc entier reste sous 0,5 Mo** (mesuré :
6 Mo aujourd'hui).

## Notes

demande de Martin : « une refonte complète des véhicules. Je les veux comme les piétons, de
profil ». Tout ce qui est **debout** dans le jeu est dessiné debout — le passant ancré à ses
pieds, l'arbre, le lampadaire, le banc, le feu et son poteau, les clôtures nord-sud vues par
la tranche — et le char est la **dernière chose regardée d'aplomb**. Trois poses (profil
miroité, dos, face) choisies comme la face d'un passant, au lieu de 32 caps cuites : l'atlas
du parc passe de **1 024 canevas et 6 Mo à 96 et 0,3 Mo**.

- ⚠️ Mesuré : **94,5 %** des chars en marche sont à moins de 2° d'un cap cardinal — la
  rotation libre coûte 6 Mo pour 3 % du temps.
- ⚠️ De dos, les 28 px de longueur ne se voient plus : l'ombre au sol permanente est le
  filet — **livrée**, permanente, à l'empreinte du catalogue, orientée comme le char. **Dix
  chars sur douze sont debout** (auto, taxi, police, sport, luxe, ambulance, camion,
  remorqueuse, autobus) : trois poses au vocabulaire du passant, choisies par le même code
  que sa face, ancre à la ligne de sol. Puis, sur « raffine les designs » de Martin, **le
  modelé** : rehaut `C` et ombre `D` dérivés de la couleur de caisse par une seule formule
  (`nuances`, dans `base.js`, partagée entre les palettes et la naissance d'un char), moyeu
  `M`, chrome `B`, reflet `G` et ombre `E` de vitre — en majuscules, parce qu'aucune palette
  n'en a. Le taxi et la police ont retrouvé leur livrée sur la carrosserie commune.
- ⚠️ **L'aperçu est à trancher par Martin** (l'artefact « La flotte debout »).
- ⚠️ Cette ligne est repassée trois fois à « à faire » sous mes marqueurs : des plans
  reconstruits depuis une base plus vieille. **Livré en entier** : les douze véhicules
  debout, modelés (rehaut, ombre, moyeu, chrome, reflet — `nuances` partagée), et le vélo et
  la moto avec un **passant assis** dessus, aux couleurs du joueur ou d'un archétype de rue.
  Sur retour de Martin, la sport est basse, les roues dans les ailes.
- ⚠️ La tête du pilote ne consomme pas un dé (`hash2` de sa position) : un choix cosmétique
  ne perturbe pas la simulation. Restent, hors fiche : le bateau qui n'a pas de sprite
  (dette), et la pose couchée de l'épave — `debout()` la choisit déjà si un sprite la
  déclare.
- ⚠️ **Correctif, 15 sept. 2026** (retour de Martin : « corrige les ombres pour les
  véhicules en nord-sud ») : l'ombre posait l'empreinte du catalogue **à plat**, donc un
  char qui roule vers le nord traînait ses 28 px de long — **quinze pixels sous ses roues,
  pour un dessin haut de onze** : on lisait une remorque. Or **le sol se voit de biais**, et
  le jeu le disait déjà ailleurs : l'ombre d'un passant fait 12 × 6 pour un corps rond.
  L'axe nord-sud est donc écrasé du **même** biais (`OMBRE.profondeur`, 0,5), appliqué au
  dessin **après** la rotation (sinon une empreinte en diagonale est cisaillée au lieu
  d'être posée à plat) ; l'empreinte en X, celle que le dessin montre, ne bouge pas d'un
  pixel. Et l'écart a deux composantes : au sol elle tombe **à l'est** (la lumière vient du
  nord-ouest) et **pas au sud** — rien ne dépasse devant les roues d'un char posé ; ce qui
  s'échappe vers le sud-est, c'est l'altitude. 3 juges : la fiche, « un seul biais pour
  toute la ville » (le passant et le char comparés), et la règle mesurée — **une ombre ne
  dépasse jamais la ligne de sol de plus que la hauteur du dessin qui la jette**, sur les
  quatre caps et tous les véhicules debout ; rouge avant (« auto vers le nord : l'ombre
  traîne 15 px sous ses roues, et le dessin n'est haut que de 13 px »).
- ⚠️ **Deuxième correctif, 15 sept. 2026** (« améliore les virages et valide la direction
  des phares quand je pilote »). **Les virages** : le char tournait d'un nombre fixe de
  radians par image, quelle que soit sa vitesse — le cercle qu'il décrivait valait donc
  `vitesse / braquage` et **grandissait avec elle** : mesuré sur une berline, 1,4 tuile au
  pas et **12,6 tuiles à fond**. Un coin de rue en demande une et demie ; à pleine vitesse
  le coin était impossible, et `majTrafic` l'écrivait déjà noir sur blanc (« il ratait son
  virage et finissait sur le trottoir d'en face »). Une vraie auto décrit **toujours le même
  cercle** à volant fixe : la rotation est maintenant `vitesse / rayon_braquage`, et la
  fiche déclare un **rayon en pixels** (22 px pour une berline, une tuile et demie ; 40 pour
  un autobus) au lieu de radians par image — les valeurs sont les anciennes inversées, le
  caractère de chaque char ne bouge pas. Mesuré après : **1,4 tuile au pas, 3,2 à fond** (le
  volant perd de la prise à haute vitesse, `braquage_vite`).
- ⚠️ **Le volant se tourne, il ne se claque pas** : la direction passait de 0 à 1 en une
  image — au clavier, chaque appui était un coup de butée à butée ; il prend et se recentre
  en un dixième de seconde.
- ⚠️ **Et un char pivote sur son arrière**, pas sur son nombril : le nez balaie, le train
  arrière suit (le décalage n'est pris que si la place est libre). L'**adhérence** suit le
  reste : à rotation trois fois plus vive, l'ancienne valeur aurait mis le char en travers
  de 34° en permanence — 0,30 pour une auto (glisse 6–11°), 0,22 pour les lourds qui
  labourent, **0,18 pour la sport** qui reste de loin la plus glissante, 0,40 pour le luxe.
  **Les phares** : validés, rien à corriger — l'ancre est exactement au milieu (le miroir ne
  décale pas d'un pixel), le blanc est devant et le rouge derrière dans les onze sprites, et
  les seules lampes blanches visibles de dos sont les **gyrophares** de l'ambulance et de la
  remorqueuse, sur l'axe du toit. Un juge le tient maintenant, sur les 72 caps du cadran. 4
  juges de banc + 3 de fiche ; rouge avant sur les trois règles (le cercle qui passe de 22,6
  à 201,6 px, le volant qui claque à la butée en une image, le nez et le coffre qui
  parcourent le même chemin). 1580 tests
