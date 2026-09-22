# Des phares à la mesure de chaque char

← [les jalons livrés](README.md) · [le plan](../plan.md)

## Fiche

Martin (21 sept. 2026) : « ajuste correctement les phares pour tous les types de véhicules
le soir ». Ce que la capture du soir montre : un seul halo rond, le même pour le vélo et
l'autobus, centré 16 px devant le nez (il déborde sur la caisse et derrière elle) ; un seul
feu arrière, au milieu, même sur un camion ; les bateaux ont des phares d'auto ; le sol vu
de biais (0,75) n'écrase pas le faisceau comme il écrase l'ombre ; et passé six chars à
l'écran, les suivants roulent éteints. Le plan : les lampes viennent de la MACHINE — les
pièces `l` et `t` de chaque silhouette, projetées au cap dessiné —, une lueur sur chaque
lampe peinte, et un faisceau en cône posé au sol à partir des phares bas, écrasé comme
l'ombre ; sa portée et son ouverture par classe (le vélo une lampe faible, la moto un
faisceau étroit, le camion et l'autobus plus loin, le bateau aucun : ses feux seulement) ;
le plafond compte des chars, pas des lampes. Regardé dans Chromium avant de livrer.

## Notes

**Livré le 21 sept. 2026.** Les lampes d'un char viennent de **sa machine** (`Vehicules.lampesDeLaMachine`) :
ses pièces `l` et `t` — `bloc`, `point` (le feu du vélo, au bout du porte-bagages) et `tube` —, lues une
fois par silhouette et projetées **au cap dessiné**, comme le toit (le biais du sol, 0,75, et la hauteur
de la lampe). Chacune a sa **lueur** (5 px, la couleur de sa palette) ; les phares **bas** (sous 10 px)
jettent un **cône au sol** (`Base.fin`, `cone`) qui part d'eux, écrasé comme l'ombre, et qui reste sur
la chaussée quand le char saute.

- **Par classe** (`FAISCEAUX`) : l'auto porte à 56 px, le camion et l'autobus à 68 et plus large au
  départ (leurs phares sont plus écartés), la moto à 54 en faisceau étroit (une lampe), le vélo à 26 et
  faible. **Le bateau, aucun** : ses feux seulement (l'avant, le feu de mât du chalutier et du
  porte-conteneurs, la poupe). Un juge exige une décision pour chaque classe du catalogue : la prochaine
  (un avion au sol) le fera rougir jusqu'à ce qu'on écrive la sienne, fût-ce `null`.
- ⚠️ **Le plafond compte des chars** : 14 chars à 7 lampes au plus (`LAMPES_PHARES_MAX` = 98 ;
  `Base.LAMPES_MAX` passe de 62 à 148). À 12 lampes, deux par char, le septième char de l'écran roulait
  éteint. Sept places gardées pour le char du joueur, et un juge : le plus éclairé du parc (l'autobus
  scolaire et le cabriolet, 7 lampes) y tient.
- ⚠️ **Le soir, le faisceau monte avec la nuit** : un tiers de sa force à la brune (18 h 40), toute à la
  nuit faite (21 h). Les lueurs sont pleines dès qu'on allume — une lampe allumée se voit.
- ⚠️ **Deux passes pour le bord du cône** (`CONE_FLOU`) : d'une seule, c'était une arête franche, un
  triangle de lumière posé sur la rue.
- ⚠️ **La charrue, de face, cache ses phares derrière sa lame** (et une auto qui s'éloigne, derrière sa
  caisse) : la lueur déborde. Le juge demande donc qu'une lueur tombe sur sa lampe à **un cap au moins**
  sur huit, et que chaque pixel de lampe peint soit sous une lueur, à tous.
- ⚠️ **Le vieux juge « char mené » tournait deux images de simulation** : le char du trafic braquait de
  0,9 rad pour suivre sa rue, et « devant » n'était plus l'est. Les juges des phares rendent sans avancer
  le monde (`Jeu.rendre`).
- **Ce que ça coûte** : 18 chars allumés, 82 lampes, 1,3 ms par image contre 1,0 avec l'ancien plafond
  (Chromium, bureau, 400 images).
- **Juges** : cinq neufs et un réécrit dans `test_la_nuit_js.py`, le plafond dans `test_moteur_js.py`.
  **17 mutations, une par règle, toutes rouges** (dont une refaite : elle cassait la syntaxe et rougissait
  pour rien).
- **Regardé dans Chromium** : chaque silhouette seule, la nuit, vers l'est (l'auto aussi vers le nord et
  en diagonale) ; puis 18 chars du parc à 18 h 57, 19 h 12, 20 h 38 et 22 h 47.
- ⚠️ **La suite complète** (sur `19720d2` + ce jalon) : 3 865 verts, 14 sautés, 4 xfail, **3 rouges qui ne
  sont pas de ce jalon** — ils tombent à l'identique sur `19720d2` sans lui :
  `test_definitions::test_le_paquet_reste_leger` (le paquet des définitions au-dessus de 44 000 octets
  gzip ; ce jalon n'y ajoute rien, tout est dans le JS),
  `test_histoire_js::test_les_cravates_de_m2_arrivent_quand_madame_thibodeau_a_fini_de_parler` et
  `test_moteur_js::test_la_foule_ne_se_traverse_plus`.

### Vague 2 — le faisceau ne passe pas au travers d'un mur (21 sept. 2026)

Martin : « les phares ne doivent pas passer au travers des toits ». Le faisceau était un cône qui
ignorait la ville : un char garé nez contre un mur, ou dans une ruelle qui tourne, jetait sa lumière
à travers — un toit, un pâté de maisons plus loin s'il le fallait.

- **`porteeLibre`** marche depuis le phare, dans le cap dessiné, par quarts de tuile, et s'arrête au
  premier mur (`Monde.solidite` = 1) — **la même valeur qu'un toit** (`app/carte.py` : une couverture
  a `"solide": 1`, comme une façade), et la même règle que `Jeu.ligneLibre`. La portée trouvée
  remplace celle de la classe ; l'ouverture du cône (`cone[1]`) rétrécit dans la même proportion, pour
  qu'un faisceau raccourci ne s'évase pas plus qu'un long.
- ⚠️ **La marche part du PHARE, pas du centre du char** : un phare près du trottoir voit le mur d'à
  côté une demi-tuile avant celui du centre. Et dans le MÊME cap dessiné que la lampe (`cap`, pas
  `v.angle`) — les deux étaient déjà légèrement désaccordés (l'origine du faisceau au cap arrondi, son
  axe au cap continu) ; unifiés, sinon le mur qu'on cherche n'est pas celui qu'on éclaire.
- **Juges** : une scène construite dans la vraie ville générée (jamais posée à la main) — un mur trouvé
  près du joueur dans les quatre directions cardinales, le CHEMIN JUSQU'À LUI confirmé dégagé (sinon un
  mur plus proche, jamais vu par la recherche, se glissait sous les roues de l'auto posée entre les
  deux — premier piège du juge lui-même) ; et le pendant, une route dégagée sur 6 tuiles où le faisceau
  du camion (le plus long, 68 px) porte sa pleine mesure.
- **4 mutations, 3 rouges par le juge dédié** (ignorer les murs, un pas de marche trop grossier, un
  mur qui bloquerait même loin) ; la 4e (marcher depuis le centre du char plutôt que le phare) est
  rattrapée par un juge voisin (`test_le_faisceau_est_a_la_mesure_de_chaque_classe`), pas par celui-ci
  — l'écart entre les deux origines (≈13 px) est trop petit pour la marge du juge dédié.
- **Regardé dans Chromium** : une auto posée à trois tuiles d'un mur (les toits de deux devantures) —
  comparé au même mur, la garde retirée : sans elle, le cône s'étale sur tout le trottoir et déborde
  sur le toit ; avec elle, il reste un halo court qui ne dépasse pas le trottoir.
- Les 17 mutations de la 1re vague mordent toujours (rejouées telles quelles).
