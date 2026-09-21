# Les toits

← [les jalons livrés](README.md) · [le plan](../plan.md)

## Fiche

_Titre d'origine dans le plan : Les toits (**correctif**, taille 2) — **livré le 13 sept. 2026**_

_Demande de Martin :_ « je veux que les toits des bâtiments soient plus réalistes. »

⚠️ **Le défaut était le même que celui des stationnements avant qu'on les dessine** : le toit
était peint **tuile par tuile**, chacune ignorant les autres. `TUILES.B/E/O` remplissait un
carré d'une couleur et semait des points tirés de `hash2(x, y)` — et comme la variante valait
0 pour tous les toits, **toutes les tuiles d'un toit étaient rigoureusement identiques**.
C'était une texture, pas un toit — et une texture uniforme ne peut pas être réaliste, parce
qu'un vrai toit vu d'en haut ne se lit ni par son grain ni par sa couleur.

Ce qui a été livré, dans l'ordre de ce qui se voit :

- **Un bord.** Parapet clair au ras du vide et sa ligne d'ombre à l'intérieur, sur chaque côté
  où le toit s'arrête. C'est le premier repère d'un toit : celui qui dit où finit le bâtiment.
- ⚠️ **Et c'est pour ça que deux voisins collés ne portent jamais la même couverture.** Le bord
  se lit dans le voisinage (« ma voisine n'est pas le même toit ») : entre deux toits
  identiques, il n'y a **aucun bord à trouver**. Le générateur corrige donc le tirage — sans
  en refaire un, parce qu'un dé de plus décalerait toute la ville (la leçon des devantures,
  des rampes et des clôtures).
- **Une identité par bâtiment.** `COUVERTURES` choisit la matière sur le **genre** :
  deux versants en banlieue, tôle et gravier à La Shop, ardoise dans la vieille ville. Avant,
  `des.choix(TOITS)` donnait l'ardoise à un entrepôt et le gravier goudronné à un bungalow.
- **Un grain qui varie.** Le bruit entre dans la variante (`GRAINS_DE_TOIT`), donc deux tuiles
  voisines ne sont plus le même dessin — un hangar de 26 tuiles ne se lit plus comme un damier.
- **Des pentes.** Le toit `P` a deux versants et une ligne de faîte, et le versant se
  **compte dans les voisines** (combien de tuiles du même toit au nord, combien au sud) : la
  faîte apparaît toute seule là où les deux pentes se rencontrent, sans qu'une tuile ait
  besoin de savoir qu'elle est au milieu, et **sans une donnée de plus dans le paquet**.
- **De quoi l'encombrer.** 172 équipements : ventilation, climatisation, cheminée, cage
  d'escalier, réservoir d'eau, antennes. ⚠️ **Ce n'est pas du décor** — `poser_decor` refuse
  les tuiles solides, et il a raison : le décor est une entité qu'on heurte. Ce qui est sur un
  toit n'est heurté par personne : c'est du dessin, il voyage dans le paquet et s'indexe par
  morceau comme les devantures et les graffitis.
- **Une ombre sur la rue.** Une bande sombre en dégradé au sud de chaque mur — elle donne
  d'un coup de la hauteur à toute la ville. ⚠️ Elle se peint **sous** les enseignes (une ombre
  par-dessus une pancarte donnerait une pancarte sale), et la boucle part **une rangée
  au-dessus du morceau** : l'ombre d'un mur assis sur la dernière rangée du morceau voisin
  appartient à celui-ci, et sans ça une bande de trottoir sur seize n'avait pas d'ombre.
- **Rien de tout ça ne coûte par image** : tout est peint **dans le morceau**, une fois. Le
  budget d'image (≤ 6 blits, ≤ 160 `drawImage`) n'y touche jamais.
- ⚠️ **Un beau toit donne envie d'y monter.** Rien n'est prévu pour : le joueur à pied n'a pas
  de `z`, le toit est solide 1, et une ville où l'on croit pouvoir grimper sans pouvoir le
  faire est plus frustrante qu'une ville aux toits plats. Les toits restent **muets pour le
  jeu** tant qu'on n'a pas d'escaliers — et c'est une décision, pas un oubli.
- **Juges (4 neufs)** : la couverture suit le genre (et la banlieue n'a que des versants, un
  entrepôt jamais d'ardoise) ; deux bâtiments collés posés l'un après l'autre ne portent pas la
  même couverture ; l'équipement ne se pose jamais au bord d'un toit, ni collé à un autre, ni
  ailleurs que sur du toit ; et au banc, une tuile de bord ne se peint pas comme un plein toit
  (les cuissons se comparent trait par trait) pendant que les versants se suivent du nord au
  sud avec **une seule** ligne de faîte. Le paquet pèse **368 Ko bruts / 41 Ko gzip**, sous ses
  bornes de 400 / 70.

## Notes

demande de Martin (« je veux que les toits soient plus réalistes ») : ils étaient peints
**tuile par tuile**, chacune ignorant les autres — une texture, pas un toit. Ils ont
maintenant un **bord** (parapet clair + ligne d'ombre, lu dans le voisinage comme les
passages piétons), un **grain** qui varie de tuile en tuile, une **couverture par genre**
(`COUVERTURES` : deux versants en banlieue, tôle et gravier à La Shop, ardoise en ville) que
**deux voisins collés ne partagent jamais** (sans quoi il n'y a pas de bord à trouver entre
eux), des **versants** avec leur ligne de faîte — comptés dans les voisines, zéro donnée de
plus —, **172 équipements** (ventilation, climatisation, cheminée, cage d'escalier,
réservoir, antennes) qui voyagent dans le paquet comme les enseignes, et une **ombre
portée** sur la rue qui donne d'un coup de la hauteur à la ville. 4 juges neufs ; paquet à
368 Ko bruts / 41 Ko gzip
