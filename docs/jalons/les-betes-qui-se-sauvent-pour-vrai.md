# Les bêtes qui se sauvent pour vrai

← [les jalons livrés](README.md) · [le plan](../plan.md)

## Fiche

Demande de Martin (22 sept. 2026) : « j'aimerais des ratons et chats plus réalistes quand ils courent
pour s'enfuir ».

Aujourd'hui, un chat qui détale est **une image fixe qui glisse** : la pose « il file » (le corps
étiré), toujours le nez au nord quelle que soit la direction de sa fuite, à vitesse constante dès la
première image — et il **disparaît net** dès qu'il sort de sa ruelle ou au bout de sa fuite, même
sous nos yeux. Le raton, pareil.

- **Il court dans le sens où il va** : le dessin se tourne vers sa course (le nez devant, la queue
  derrière), pas toujours vers le nord. Au pas aussi.
- **Une vraie foulée** : des pattes qui se voient, un cycle de galop pour le chat (allongé, puis
  ramassé), un trot dandinant pour le raton, qui tourne au rythme de la distance parcourue.
- **Un départ** : le sursaut (il se ramasse une fraction de seconde), puis il accélère — pas pleine
  vitesse à la première image. Une petite bouffée de poussière au démarrage.
- **Il ne s'évapore plus sous nos yeux** : il longe un mur au lieu de le traverser ou de disparaître,
  il peut quitter sa ruelle en fuyant, et il ne s'efface qu'une fois **hors de l'écran**.

- ⚠️ Rien ne tire un dé : la foulée se lit à la distance parcourue, les écarts à l'empreinte de la bête.
- ⚠️ Le goéland n'est pas touché (il s'envole, lui). La confiance du chat (« caresser le chat », 2e
  vague du décor) décide QUAND il part ; ce jalon ne change que COMMENT.

## Notes

✅ **Livré** (22 sept. 2026).

- **Quatre directions, comme les passants** : de profil (la gauche est le miroir de la droite), de
  dos, de face. Un **squelette**, pas une grille (`peindreBeteEnMouvement`, `sprites.js`) : le corps
  (un ovale ombré), la tête, les oreilles, quatre pattes (celles du côté loin plus sombres), la
  queue ; chaque image ne bouge que ses articulations. Le raton a son masque, son museau blanc et sa
  queue annelée en anneaux de deux pixels. ⚠️ Premier jet regardé ×6 : un chat en **belette** (trop
  long, trop haut sur pattes), une tête de raton en **bloc blanc**, des vues de dos et de face en
  **bâtons** sans pattes visibles — corrigé avant de brancher quoi que ce soit.
- **La foulée à la distance** (`poseDeBete`, `foulee_px` dans la fiche) : un chat bloqué ne court pas
  sur place. **Le sens avec une prise** (`directionDeBete`) : une course en diagonale ne clignote pas
  d'un profil à un dos.
- **Le départ** : il se ramasse (`sursaut_images`), accélère (`elan_images`, en douceur), et une
  bouffée de poussière part de ses pattes — à l'empreinte, jamais au dé.
- **Il ne s'évapore plus** (`majCourse`) : il longe un mur (on garde l'axe qui passe ; sinon un
  quart de tour, du côté qui l'éloigne du joueur), il peut quitter sa ruelle en fuyant, et il ne
  s'efface qu'**hors de l'écran** ; coincé sous nos yeux, il s'assoit et reprend sa vie de bête.
  La confiance du chat (« caresser le chat ») décide toujours QUAND il part.
- ⚠️ **Deux juges de la nuit rougissaient sur `dev`** (la ville a grandi depuis leur livraison) et
  sont réparés ici : une **table de pique-nique** posée sur la seule tuile de sable voisine d'un
  baigneur lui barrait la sortie de l'eau — il sort maintenant par une tuile libre, diagonales
  comprises (une première explication, « il perd son droit à l'eau trop tôt », était fausse : la
  mutation l'a montré, la collision ne regarde que le bord qui avance) ; et le juge du camelot
  finissait **à l'hôpital**, le joueur fauché sur la chaussée qu'il suivait — la rue est vidée.
- **Juges** : `test_betes_qui_se_sauvent_js.py` (10 : la fiche, le sens et le virage, le départ et
  la foulée, la ruelle et les murs, l'assise, le dé, et le RENDU — on espionne le peintre pendant
  qu'un chat détale sous nos yeux). **Douze mutations, toutes rouges**, après un juge durci (le sens
  mis à jour en course ne se voyait qu'avec un virage).
- **Regardé dans Chromium** : une planche ×6 de toutes les images, puis une pellicule dans le jeu —
  le chat qui galope à droite et descend, le raton qui trotte à gauche et monte.
