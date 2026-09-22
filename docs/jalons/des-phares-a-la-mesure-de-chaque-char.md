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
