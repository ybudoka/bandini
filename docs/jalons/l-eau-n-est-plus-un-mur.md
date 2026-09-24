# L'eau n'est plus un mur

← [les jalons livrés](README.md) · [le plan](../plan.md)

## Fiche

_Titre d'origine dans le plan : L'eau n'est plus un mur (**correctif**, taille 3) — **livré le 14 sept. 2026**_

_Demande de Martin :_ « l'eau ne doit plus être un mur, mais qu'on puisse soit y nager ou
s'y noyer, à pied ou dans un véhicule. »

Aujourd'hui c'est littéralement un mur : `MASQUE_PIETON = MUR | EAU` et `MASQUE_VEHICULE =
MUR | EAU | BASSE`. On s'arrête au bord de la baie comme contre une façade, ce qui est le
plus étrange dans une ville qui s'appelle Baie-des-Brumes.

**À pied : on nage, et c'est le souffle qui décide.** L'endurance existe déjà — 100 points,
0,4 par image à la course, rendue par la bouffe et tenue plus longtemps par le café. Nager
la dépense plus vite. À bout de souffle, on coule : on se réveille à l'hôpital avec sa
facture, exactement comme quand on tombe (`Missions.hopital` fait déjà tout ça).

**En véhicule : il coule.** Aucun char ne flotte. Il s'enfonce en quelques secondes ; le
conducteur sort et nage, ou coule avec. Le char est perdu — ⚠️ et la fourrière ne va pas le
chercher au fond : un char noyé est un char perdu, sinon couler devient un moyen commode de
se faire rembourser une épave.

⚠️ **Le vrai enjeu n'est pas la noyade, c'est le pont.** M8 a bâti sa géographie sur une
règle : une rue dont tous les blocs voisins sont de l'eau est **noyée**, et `PONTS` fait
l'unique exception — « un pont, que le juge défait pour vérifier qu'il est bien le seul
lien ». Si l'on nage, La Pointe n'est plus une île et ce juge devient un mensonge.

La sortie est de reformuler le juge, pas de l'affaiblir : **le pont est le seul lien
CARROSSABLE**. Un homme traverse un chenal à la nage, une auto non — c'est plus vrai qu'avant,
pas moins. Et le souffle fait le reste : la largeur du chenal doit coûter assez de souffle
pour que la traversée soit un pari, et la baie, elle, ne se traverse pas. ⚠️ **Ça se mesure**
et c'est un test : largeur de l'eau × dépense par image contre les 100 points d'endurance.

- ⚠️ **La police nage aussi**, comme elle enjambe les clôtures. Sinon l'eau devient l'exploit
  anti-police le plus simple du jeu : deux pas dans la baie et on est intouchable.
- ⚠️ **Les piétons, eux, ne se noient jamais.** `marchablePieton` exclut déjà la chaussée ;
  il doit exclure l'eau pour tout ce qui flâne. Un passant qui part se baigner dans la baie
  parce que son errance l'y a mené, c'est le genre de chose qu'on ne voit qu'en jeu.
- ⚠️ **Les juges de connexité gardent leur sens.** `composantes_marchables` continue
  d'ignorer l'eau : il sert à prouver qu'aucun trottoir n'est enclavé, et si l'eau reliait
  les rives, il ne dirait plus rien du tout.
- **Il faut un bord.** On ne doit pas passer d'un pas de la terre ferme à la noyade : le
  sable (`s`) existe déjà comme rive, et il devient l'eau **basse** où l'on entre encore
  debout. C'est là que se joue la lisibilité — voir où ça devient sérieux.
- **Coût réel à ne pas cacher** : nager est un état de plus (une pose de sprite — on ne voit
  que la tête et les bras), plus les remous, plus le char qui s'enfonce.
- **Et ça débloque le bateau.** M9 le reporte faute de « tuiles d'eau carrossables » : c'est
  exactement ce que cette vague apporte. Le traversier de M12 y gagne aussi.
- **Juges** : on ne traverse pas la baie à la nage, quel que soit le café bu ; le pont reste
  le seul lien carrossable (le juge de M8, reformulé) ; un char dans l'eau coule toujours et
  ne revient jamais ; un policier lancé derrière le joueur entre dans l'eau comme lui ;
  aucun piéton ordinaire ne met un pied dans l'eau de toute une partie de banc.

**Livré le 14 sept. 2026.** L'eau n'arrête plus que ce qui doit être arrêté, et c'est le
**souffle** qui a repris le travail que faisait la collision.

- **Deux masques au lieu d'un.** `MASQUE_NAGEUR` (le joueur, les agents) ne voit pas l'eau ;
  `MASQUE_PIETON` la garde, et les passants avec. ⚠️ Et **le masque d'un corps dépend d'où il
  est, pas de qui il est** : celui qui a les pieds dans l'eau doit pouvoir en **sortir**. Un
  agent lancé à la nage, revenu à `flane`, serait resté figé au milieu de la baie pour
  toujours.
- **Le souffle décide, et ça se calcule.** `recherche.NAGE` : 1,0 px par image, 0,5 point par
  image — donc **8 points la tuile d'eau**. Le chenal du pont fait 11 tuiles : **88 points sur
  100**, un pari. Le large de la baie est à **73 tuiles** de toute terre, pour **40** au
  plafond absolu (café **et** estomac plein) : on ne l'atteint même pas, et il faudrait
  revenir. ⚠️ **Nager coûte même immobile** — sans ça, s'arrêter au milieu de l'eau serait un
  moyen de refaire son souffle à l'abri de la police.
- **On coule comme on tombe.** `Missions.hopital` fait déjà tout : la facture, la police
  remise à zéro, le boulot abandonné, le fondu et le réveil. Une deuxième façon de perdre
  connaissance aurait sa propre facture, ses propres oublis, et le jour où l'une des deux
  change, l'autre ment.
- **Un char coule, et il est perdu** — ni au fond, ni à la fourrière. ⚠️ Sinon couler devient
  le moyen commode de se faire rembourser une épave : on pousse sa carcasse à l'eau et on va
  la racheter au lot pour le prix d'un remorquage. Trois secondes pour en sortir, et le HUD
  le dit. **Le bateau flotte**, et c'est **sa fiche** qui le dit (`eau`, déjà là pour sa
  friction et son adhérence) — une classe écrite dans le JavaScript en aurait fait une
  deuxième vérité à tenir à jour.
- **La police nage**, à la vitesse de la nage comme tout le monde, et son chemin **paie
  l'eau** (8 tuiles de marche par tuile d'eau, comme le grillage se paie 5). Sans prix, le
  plus court chemin couperait par la baie à chaque fois.
- **Ça se voit.** Un nageur n'a pas d'ombre : il a un **remous**, et son corps est **coupé à
  la ligne d'eau** — cinq pixels, assez pour noyer les jambes, pas assez pour couper le
  visage, qui dit dans quel sens on nage. ⚠️ On coupe **à la source** du `drawImage`, pas avec
  un `clip` : un `clip` coûte un `save`/`restore` par nageur et par image.
- ⚠️ **Le juge du pont est reformulé, pas affaibli**, et il lisait déjà la bonne chose : il
  travaille sur `voie`, la grille des **rues**. « La Pointe est une île pour les chars » est
  une phrase **plus vraie** que « La Pointe est une île », et c'est celle que la géographie de
  M8 a toujours voulu dire.
- ⚠️ **Un défaut trouvé par le juge, et il aurait été invisible** : `v.coule++` sur un char
  qui n'a jamais touché l'eau rend **NaN**, et `NaN < 180` est faux — le char coulait **à la
  première image**, sans qu'on ait le temps d'en sortir. Le compteur s'écrit
  `(v.coule || 0) + 1`.
- **Ce qui reste ouvert** : la rive de sable est là (elle borde presque toute l'eau — 237
  tuiles de bord franc sur 18 569, et ce sont les **quais**, qui doivent être francs), mais
  elle ne ralentit pas encore. Et **le bateau** de M9 a maintenant ses tuiles d'eau : il lui
  manque son sprite et sa place au port.

## Notes

demande de Martin : l'eau était **littéralement un mur** (`MASQUE_PIETON` la comptait comme
une façade). Maintenant : un **masque de nageur** pour le joueur et les agents (les
passants, eux, n'y entrent jamais), le **souffle qui décide** — 8 points par tuile, le
chenal du pont en coûte 88 sur 100 : un **pari** —, la **noyade par `Missions.hopital`**
(une seule façon de perdre connaissance), le **char qui coule et qui est perdu** (jamais à
la fourrière : couler ne doit pas devenir un remboursement d'épave ; le **bateau** flotte,
et c'est sa fiche qui le dit), et la **police qui nage** au prix fort dans l'A\*.

- ⚠️ Le juge du pont est **reformulé, pas affaibli** : le pont est le seul lien
  **carrossable**. Le large de la baie est à **73 tuiles** de toute terre pour **40** au
  plafond absolu (café + estomac plein) : on n'y va pas. 6 juges neufs
