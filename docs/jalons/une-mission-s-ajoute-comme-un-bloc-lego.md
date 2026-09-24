# Une mission s'ajoute comme un bloc Lego

← [les jalons livrés](README.md) · [le plan](../plan.md)

## Notes

demande de Martin (20 sept. 2026) : « valide toutes les missions pour que les animations
fonctionnent. Je veux que ça soit facile d'ajouter des missions, comme des blocs Lego ».

✅ **Livré** (20 sept. 2026). Le mode d'emploi est dans
`docs/comment-monter-les-missions.md` — ici, ce qu'il a fallu défaire pour que ça tienne.

- ⚠️ **Le bloc, c'est la scène par défaut.** « Une mission = un fichier » avait réglé la
  moitié du problème ; restait qu'un fichier devait **écrire ses deux scènes à la main**,
  plan par plan. Maintenant `prerequis`, `phase`, `echec`, `donne` et **`scenes`** ont un
  défaut, posé au chargement par `_completer()` — le paquet, le navigateur et les juges ne
  voient que des missions **finies**. `scene_par_defaut` bâtit l'intro et la fin de ce que la
  fiche dit déjà : qui la donne, s'il se tient dehors ou dedans, ce qu'elle demande d'abord,
  où elle se termine.
- ⚠️ **On n'a rien inventé : on a relevé.** Les quatre formes du défaut sont celles que les
  missions écrites à la main ont fini par prendre, et la preuve tient en une mesure : **cinq
  des seize scènes du catalogue étaient, mot pour mot, ce que le défaut rebâtit** (m2 sa fin,
  m4 les deux, m5 son intro, m6 sa fin). Elles sont effacées ; le catalogue exporté est resté
  **identique, octet pour octet**.
- ⚠️ **Le défaut ne vise que ce que Python peut garantir** — un lieu nommé par un objectif,
  la porte du donneur (`chez:`), le joueur, le donneur. Jamais un acteur que seule une partie
  en cours poserait (`cible`, `fuyard`) : un plan dont le lieu ne se résout pas est **sauté
  en silence**, et une animation qui ne joue pas est pire qu'une animation absente. C'est
  pour ça que m2 garde son intro écrite : elle, elle vise la `cible`.
- ⚠️ **Quatre juges du banc nommaient les missions en dur**, et c'est ça qui rendait l'ajout
  coûteux : l'ordre des prérequis — **arrêté à `['m1'…'m5']` pendant que le catalogue en
  comptait huit** —, les quatre cas de « passer » choisis à la main, la seule m3 pour le dé,
  et `slug in ("m4", "m5", "m6")` pour les fins au combiné. Ils lisent tous le catalogue
  maintenant (`ordre_topologique()`, `fin_dite_en_personne()`), et **chaque mission est jugée
  deux fois** : avec la scène qu'elle écrit, et avec celle que le défaut lui bâtirait.
- ⚠️ **Un juge était rouge sur `dev` sans que rien ne le dise** : l'intro de m97 n'était
  jugée par personne, parce que sa condition d'état (`exige: {liberes: 3}`) n'était jamais
  remplie au banc — la mission n'était donc jamais offerte, et `parler` ne jouait rien. Le
  banc **tient** maintenant l'`exige` au lieu de faire comme s'il n'existait pas.
- ⚠️ **Et le juge du « passer » mesurait la foule.** Étendu à m2, il rougit tout de suite :
  2 488 entités contre 2 489. Ni l'une ni l'autre des deux scènes n'avait rien laissé —
  `B.entites.length` compte la ville entière, la foule se repeuple autour du joueur **au fil
  des images vivantes**, et une scène passée n'en consomme pas le même nombre qu'une scène
  regardée. Il compte maintenant ce qu'une scène TOUCHE : les hommes que la mission a posés,
  les personnages de l'histoire.
- ⚠️ **Qui s'en va est dans les données, pas dans la scène.** `parti_apres` disait déjà que
  Ti-Guy quitte le terminus après M1, mais rien ne le retirait de la partie EN COURS : c'était
  la scène écrite de m1 qui le faisait entrer au garage. Une mission qui n'écrit pas la sienne
  laissait donc son donneur planté devant sa porte jusqu'au rechargement. C'est la fin de la
  mission qui le retire, maintenant, et la scène ne fait plus que le montrer.
- ⚠️ **Où l'on est quand la fin part**, au banc, se lit dans le dernier objectif : un lieu
  nous y emmène, `retourner` nous ramène devant le donneur, et tout le reste (rattraper un
  fuyard, semer la police) se finit **là où l'on est**. Le juge plantait le joueur sur le
  donneur dans ce dernier cas : il faisait parler en personne quelqu'un que la vraie partie
  aurait mis au combiné.
- ⚠️ **Le couvercle de la boîte** : `scripts/verifier_missions.py` dit en clair ce qui manque
  à chaque mission, `--detail` dit ce que chacune porte (et d'où viennent ses scènes),
  `--squelette m7 --donneur josee` imprime un fichier prêt à coller. Il est dans « Reprendre
  le travail » et dans la recette d'ajout.
- ⚠️ Et les **six erreurs de lint déjà rouges sur `dev`** sont réparées : la CI ne juge que
  les dépendances et le lint, un lint rouge sur la base rend tout le signal muet.
- **5 juges neufs** (14 cas dans `test_mise_en_scene.py`, plus celui du banc qui pose une
  fiche neuve dans le catalogue du navigateur et joue ses deux scènes), **6 mutations toutes
  rouges** : plus de scène par défaut, le défaut qui ne sort pas de la pièce, la fin loin du
  donneur qui ne va plus le voir, les clés par défaut qui ne se posent plus, le donneur qui
  ne s'en va plus, et le banc qui cesse de tenir l'`exige`. Les juges existants, eux, ont
  **doublé** : chaque mission jugée deux fois, « passer » de 4 cas choisis à la main à 16,
  le dé de la seule m3 aux huit missions. **3 104 tests verts** — et jugés dans un worktree
  isolé, une autre session refactorisant les triches de débug dans le même arbre.
- ⚠️ **Trois juges restent rouges, et aucun n'est d'ici** : ils le sont déjà sur `dev` nu
  (`test_audio` pour les voix par mission, `test_carte_du_depot` pour `incendies.py`,
  `incendies.js` et `test_debug_js.py`, et `test_la_foule_ne_se_traverse_plus`). Ils
  appartiennent au chantier des incendies et du menu DEBUG, en cours ailleurs.
