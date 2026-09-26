# Les nids-de-poule qui mordent

← [les jalons livrés](README.md) · [le plan](../plan.md)

## Fiche

_Proposé le 25 sept. 2026, ajouté au plan par Martin (« oui génial »)._

_Ce que ça donne :_ les nids-de-poule dessinés dans les rues (les quartiers qu'on reconnaît les
distribuent déjà) cessent d'être du décor — on les sent.

- **Ce qu'ils font** : rouler dedans secoue le char (la caméra tremble), abîme un peu la carrosserie et, à
  grande vitesse, fait perdre le contrôle une fraction de seconde. Plus nombreux dans les quartiers pauvres,
  et **au printemps** du jeu (après la neige de M12).
- **Le boulot** : la voirie — boucher N nids-de-poule en un chrono, avec le camion d'asphalte (`boulots`).
  Un nid bouché disparaît pour de bon.
- **La blague** : le Clairon publie le décompte des nids-de-poule de la ville chaque lundi.

⚠️ **Ce qui guette** : un effet physique neuf sur tous les chars, trafic et police compris — le trafic ne
doit pas perdre ses virages (le juge des coins en L) ; et le nombre de nids est un budget déjà réparti par
quartier : ne pas en ajouter au dé.

**Juges** : un char qui passe dans un nid prend un choc ; un nid bouché ne revient pas ; le trafic ne sort
pas de sa voie à cause d'eux.

⚠️ **Relevé le 26 sept. 2026, avant de s'y mettre — plus gros que « taille 1 ».** Une bonne part mord
DÉJÀ (« le rythme de la ville ») : `Vehicules.majNidDePoule` secoue la caméra, coûte deux points de
carrosserie, fait vibrer la manette et s'entend, avec un répit par nid. Ce qui reste :
- la **perte de contrôle** une fraction de seconde à grande vitesse (le char du joueur seulement : le trafic
  roule sur des rails) ;
- le **boulot de voirie** — les boulots naissent d'un véhicule (on klaxonne au volant), et le parc n'a pas
  de **camion d'asphalte** : un véhicule neuf (fiche, dessin, bruit), c'est ce qui fait la taille ;
- les nids **bouchés pour de bon** (dans la partie, et `carte.nids` qui les oublie) ;
- le **décompte du Clairon le lundi** (le journal est dit par le narrateur : une phrase générique, le
  nombre en texte) ;
- **plus nombreux au printemps** : le jeu a-t-il un printemps ? (la neige de M12 est une météo, pas une
  saison) — à trancher.

### Le plan (26 sept. 2026)

⚠️ **Vu en ouvrant le chantier : les nids ne se DESSINENT pas.** La carte en pose (`nids_de_poule`, plus
nombreux dans les quartiers pauvres), le char les sent — et la chaussée est lisse à l'écran : on les
subit sans jamais les voir venir. D'abord ça.

1. **Les dessiner** : un trou sombre aux bords cassés sur la tuile, à l'écran (`Monde.dessinerNids`).
2. **La perte de contrôle** : à grande vitesse, le char du joueur ne répond plus une fraction de seconde
   (le trafic roule sur des rails, il n'est pas touché).
3. **Le camion d'asphalte** (`asphalte`, `freq` 0) : garé devant la fourrière municipale, il naît à
   l'approche du joueur, comme le camion de crème glacée.
4. **Le boulot de voirie** : au klaxon, trois nids à boucher, à l'arrêt dessus ; un nid bouché disparaît
   **pour de bon** (`partie.nidsBouches`, rendu au chargement).
5. **Le Clairon du lundi** : le décompte des nids de la ville, sous la manchette (tous les sept jours).
6. **Le printemps** : le jeu n'a pas de saisons — à trancher par Martin, pas dans cette vague.

## Notes

_Livré le 26 sept. 2026._

- **Ils se voient** : `Monde.dessinerNids` peint chaque nid de `carte.nids` sur la chaussée, avant la
  neige au sol — trois trous cuits une fois (`Atlas.cuirePeintre('nid|v')`), le bon tiré à l'EMPREINTE de
  la tuile (`hash2`) : bord cassé plus clair, fond sombre, une fissure. Hors champ, rien.
- **Ils mordent à grande vitesse** : au-delà de `nid_derape_vitesse` (3 px/image, `vehicules.PHYSIQUE`),
  le char du JOUEUR perd le volant `nid_derape_images` (18 images) et son nez part de
  `nid_derape_angle` d'un côté (l'empreinte de la tuile, jamais un dé). `sansLeVolant` annule la
  direction et garde le gaz et le frein. ⚠️ La direction a de l'inertie : les roues reviennent au centre
  en quelques images, elles ne se figent pas — le juge regarde la fin de l'aveuglement. Le trafic et la
  police ne dérapent pas (ils roulent sur des rails ; le juge le vérifie).
- **Le camion d'asphalte** (`asphalte`, `frequence` 0, `boulot="voirie"`) : cabine orange, benne basse
  pleine d'asphalte noir, ridelles, gyrophare ambre (`MACHINE_ASPHALTE`). Garé dans la rue devant la
  grille de la fourrière (`placeDeLAsphalte`), il naît paresseusement quand on passe à moins de 500 px
  sans le voir à l'écran (`majAsphalte`), comme le camion de crème glacée — aucun identifiant de plus
  au démarrage.
- ⚠️ **Un camion né pour le décor ne tire pas de dé** (`couleurDuDecor`) : né sans couleur, il en
  tirait une à `B.rng()`, et tout le hasard qui suit glissait — le saut du phare de e12 a fini dans un
  décor. Le camion de crème glacée avait le même défaut : corrigé du même geste.
- **Le boulot de voirie** (`BOULOTS.voirie`, « Nid bouché », trois nids, sans chrono) : au klaxon, un
  nid atteignable à plus de 160 px ; il faut s'arrêter DESSUS (18 px, pas 44). Bouché, il quitte
  `carte.nids` (on ne le sent plus, on ne le voit plus) et la partie le retient (`nidsBouches`) ;
  `rendreLesNidsBouches` le retire de la carte dès la première image d'une partie chargée (une fois par
  carte et par partie, `carte.nidsDe`). Paliers : 10 nids, prime ×1,3 ; 25, la fourrière à moitié
  prix ; 50, le camion est à toi.
- **Le Clairon du lundi** (`decompteDesNids`, les jours 1, 8, 15…) : « LE DÉCOMPTE DU LUNDI : N
  NIDS-DE-POULE EN VILLE, X BOUCHÉS PAR TOI », sous la manchette du matin, en texte (le narrateur ne
  dit pas le nombre).
- **Juges** : `test_nids_de_poule_js.py` — ils se peignent, le volant lâche à pleine vitesse et pas au
  pas ni pour le trafic, le camion naît à l'approche et jamais sous les yeux, un nid bouché le reste
  après un chargement, le décompte tombe le lundi, l'économie de la voirie. Chaque juge a été vu
  rougir sous sa mutation.
- **À trancher par Martin** : « plus nombreux au printemps » — le jeu n'a pas de saisons (la neige est
  une météo). Rien n'a été fait là.
