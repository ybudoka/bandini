# L'intérieur à la mesure du bâtiment

← [les jalons livrés](README.md) · [le plan](../plan.md)

## Fiche

_Titre d'origine dans le plan : L'intérieur à la mesure du bâtiment (**correctif**, taille 3) — **livré le 14 sept. 2026**_

_Demande de Martin :_ « je veux que l'intérieur de bâtiment soit proportionné à l'extérieur,
tu avais mal compris. »

⚠️ **La fiche du dessus n'a tenu que la moitié de la promesse.** « Une pièce plus grande que
sa maison » a posé une **inégalité** — le plancher ne dépasse jamais l'empreinte — et une
inégalité se satisfait très bien d'une pièce minuscule dans un immeuble immense. Mesuré sur
la ville livrée, aujourd'hui :

| Dehors | Dedans | |
|---|---|---|
| 59 × 8 (328 tuiles) | 9 × 8 (42 de plancher) | **13 %** |
| 58 × 7 (380) | 14 × 9 (84) | 22 % |
| 35 × 5 (153) | 17 × 10 (120) | la pièce est **deux fois plus profonde** que le bâtiment |
| 14 × 4 (56) | 11 × 8 (54) | la surface est juste, et il y a **six tuiles de profond dans un bâtiment qui en fait quatre** |

Médiane du rapport plancher / empreinte : **0,64 à 0,75** selon la graine. Et la **forme** ne
suit jamais : les pièces dessinées font toutes autour de 9 × 8, les bâtiments vont de 3 × 3 à
59 × 8.

**La règle, et elle remplace celle d'hier** : _la pièce a les **mesures** de son bâtiment._
Son plancher fait la boîte de ce qu'on voit de la rue — large et plat dehors, large et plat
dedans — et jamais plus de tuiles que l'empreinte.

Deux décisions de Martin, le 14 sept. :

1. **« les mesures du bâtiment »**, pas seulement la surface ;
2. **une longue façade se découpe en plusieurs vitrines** : soixante tuiles de large, ce
   n'est pas un commerce, c'est une **rangée** de commerces — chacun sa porte, son enseigne
   et sa pièce à sa mesure.

Ce qui suit de la règle :

- **La façade se découpe en vitrines.** Une bande de façade se coupe en segments de la
  largeur d'un commerce ; chaque segment tire son enseigne, sa famille et sa porte, et
  **possède les tuiles de bâtiment au-dessus de lui** — c'est sa part de l'empreinte, et
  c'est elle qui donne les mesures de sa pièce. Un bâtiment en L ou en U se partage tout
  seul, colonne par colonne.
- **La pièce se pose à la mesure.** Trois tailles dessinées ne peuvent pas couvrir des
  bâtiments qui vont de neuf tuiles à trois cent quatre-vingts, dans toutes les formes. Les
  commerces et logements **ordinaires** se posent donc à la mesure de leur part, meublés par
  **famille** (l'épicerie a ses frigos et ses allées, l'atelier ses machines, le logement son
  lit et son poêle) — la famille dit **quoi**, la mesure dit **combien**.
- ⚠️ **Les seize lieux garantis gardent leur plan dessiné à la main** : le billard du bar, les
  lits de l'hôpital et les ponts du garage ne se génèrent pas. C'est leur **bâtiment** qui se
  taille à eux — en largeur **et** en profondeur, alors qu'hier seule la surface était visée
  (la cantine se retrouvait dans 58 × 7).
- ⚠️ **On compare toujours les planchers**, et la convention d'hier tient : le plancher d'une
  pièce fait la **boîte** du bâtiment (une cabane de 3 × 3 ouvre sur 3 × 3 de plancher, donc
  une pièce de 5 × 5 murs compris). Les murs de la pièce sont ceux du bâtiment.
- ⚠️ **La ville va bouger** : tailler les parcelles des lieux garantis change le nombre de
  tuiles de façade, donc le nombre de tirages, donc la suite du hasard. C'est arrivé hier
  pour la même raison ; les juges de géométrie sont là pour ça et se rejouent tous.
- ⚠️ **Le mur ne bouge pas pour une porte.** Les vitrines, les portes et les pièces sont une
  **couche peinte** : elles tirent leurs décisions du dé des devantures, jamais du dé commun
  (celui qui pose les murs). Une porte de plus ne déplace pas un bâtiment à l'autre bout de
  la ville.
- **Juges** : pour chaque porte et sur cinq graines, le plancher de la pièce a **les mesures**
  de sa part de bâtiment (et plus seulement « pas plus ») ; chaque pièce **posée** passe les
  mêmes juges que les pièces dessinées (une porte, plancher d'un seul tenant, points
  atteignables qui ne volent pas la porte, un dixième de meubles au minimum, lits en blocs qui
  ne se touchent pas) ; et une longue façade porte **plusieurs** enseignes.

**Livré le 14 sept. 2026.** Sur cinq graines, **toutes les portes** : le plancher de la pièce
fait **exactement** la boîte du bâtiment qu'on voit au-dessus de sa vitrine — largeur ET
profondeur, à la tuile près. Mesuré avant : rapport médian **0,64 à 0,75**, le pire à
**0,07**.

- **Une vitrine, un commerce, une pièce.** `decouper_la_facade()` coupe la rangée de façade
  en morceaux de **huit tuiles** (la largeur d'un magasin de rue : une enseigne, une porte,
  deux vitrines), et chaque morceau **possède les tuiles de bâtiment au-dessus de lui** —
  c'est sa part, et c'est elle qui donne les mesures de sa pièce. Un bâtiment en L ou en U se
  partage tout seul, colonne par colonne. ⚠️ **Sauf un entrepôt** : un hangar est une seule
  affaire, sa façade porte un nom et une porte, et derrière il y a un entrepôt de toute sa
  largeur. Le découper en sept magasins aurait inventé une rue commerçante dans La Shop.
- **La pièce se POSE.** `piece_de_commerce()` et `piece_de_logement()` construisent un plan à
  la mesure et le font passer par `_piece()` — même validation que les plans dessinés, donc
  une pièce impossible lève **pendant la génération**. Un commerce, c'est trois rangées qui
  ne changent jamais (le **fond** contre le mur du fond, le **comptoir** à l'avant-dernière,
  la dernière **libre** — c'est celle où l'on entre) et une **allée une rangée sur deux** ;
  un logement, c'est des **coins meublés** de deux tuiles sur deux, tous les cinq tuiles.
- ⚠️ **Les dix boutiques dessinées d'hier sont supprimées**, avec les deux logements et les
  quatre petites pièces : elles répondaient à la règle d'hier par des **tailles**, et trois
  tailles ne couvrent pas des bâtiments qui vont de 9 à 380 tuiles dans toutes les formes. Ce
  qu'elles disaient de bon — une épicerie a des frigos et des allées, une taverne des tables,
  un atelier des machines — est passé dans **`MOBILIER`**, dix palettes de deux motifs. **La
  famille dit quoi, la mesure dit combien.** Les **seize lieux garantis** gardent leur plan
  dessiné à la main : le billard du Brouillard et les lits de l'hôpital sont des endroits,
  pas des gabarits.
- **Et leur bâtiment se taille à eux**, en largeur **et** en profondeur — hier seule la
  surface était visée, et la cantine se retrouvait dans un 58 × 7 pour une pièce de 14 × 9.
  ⚠️ **La bande aussi** : un îlot se partage en bandes égales (ruelle, bâtiments, devant), et
  la plus profonde de l'îlot qui porte l'hôtel en fait **neuf**, dont quatre pour la ruelle
  et le devant. Un lieu garanti **occupe son terrain** — c'est vrai d'un poste de police
  comme d'une usine — et sa façade donne alors sur le trottoir, ce qui est bien où l'on veut
  une porte.
- ⚠️ **Le dé commun ne décide plus des portes.** Une porte — vraie ou condamnée — est une
  **couche peinte** ; elle se tirait au dé commun (celui qui pose les murs) quand il y avait
  une porte par bâtiment, et depuis qu'il y en a une par vitrine, ce serait le nombre de
  commerces d'une rue qui déplacerait les bâtiments de l'autre bout de la ville.
- **Ce qui a bougé, et qu'aucune capture n'aurait montré :**
  - **Deux enseignes pareilles à trente tuiles.** La Shop a **vingt-six noms pour trente-six
    murs** (c'était déjà 31 pour 26 hier) : passé le vingt-septième, la question n'est plus
    « lequel est libre » mais « lequel a sa copie **la plus loin** ». `choisir_enseigne` rend
    maintenant le plus éloigné au lieu du tirage — deux pareilles restent à **40 tuiles au
    minimum** sur les cinq graines, la règle du quartier.
  - **Des débris sur un pas de porte.** `poser_decor` refuse une tuile réservée, mais le
    décor d'un terrain vague se sème **avant** les portes de l'îlot : une porte **dégage**
    désormais son devant. Deux par ville, et c'est le genre de chose qu'on ne voit qu'en
    restant coincé contre sa propre porte.
  - **Un point d'action ne creuse plus un meuble en bloc** (un lit à qui l'on enlève un coin
    n'est plus un lit) **ni l'escalier** — il restait un point « escalier » sur du plancher
    nu, et la pièce n'avait plus qu'une sorte de meuble.
- **Mesure.** Ville livrée : **56 portes** (45 hier), **106 enseignes** (94), **49 pièces
  posées** + 16 dessinées. Planchers de 9 à 120 tuiles, **médiane 32** — au lieu de 41 pièces
  toutes autour de 54. Paquet : +11 Ko d'intérieurs (23 Ko en tout), 445 Ko au total.
- **Juges.** `test_interieurs.py` ne lisait que le **catalogue du module** : les 49 pièces
  posées — la grande majorité — échappaient à tout. Elles passent maintenant **les mêmes
  juges** que les dessinées (une porte, plancher d'un seul tenant, un dixième de meubles et
  deux sortes, points atteignables qui ne volent pas la porte, blocs rectangulaires qui ne se
  touchent pas), et sur la ville livrée : **421 cas** au lieu de 265. Six juges neufs pour la
  règle elle-même — les mesures à chaque porte sur cinq graines, les portes qui s'ouvrent
  quand même (condamner les quarante serait une façon de ne jamais mentir), les vitrines qui
  ne se chevauchent pas, la coupe d'une façade de soixante tuiles, la part qui donne les
  mesures, et l'étage qui est une pièce de **plus**.
- ⚠️ **Deux juges d'à côté sont tombés avec la ville, et aucun ne mesurait ce qu'il croyait** :
  « la banlieue a des entrées » comptait les blocs d'asphalte de **huit tuiles au plus** —
  huit, c'était une entrée **sans case**, et trente-cinq entrées sur trente-six ont dépassé
  le seuil d'une ou deux tuiles ; il mesure maintenant ce qu'on dessine (une allée jusqu'à
  six tuiles **plus** une case de huit). Et « l'eau n'est plus un mur » cherchait une rive
  avec **trois** rangées d'eau : la première rive de la ville neuve est une langue de sable
  que l'agent contournait par une rangée sèche quatre tuiles plus haut — hors de la fenêtre
  que le juge regardait. Sept rangées, et la ville en offre trente-quatre.

## Notes

demande de Martin : « je veux que l'intérieur de bâtiment soit proportionné à l'extérieur,
tu avais mal compris ». La fiche d'hier n'a tenu que la moitié de la promesse — elle
interdisait à la pièce de **dépasser** son bâtiment, rien ne l'obligeait à le **remplir** :
13 % pour un bloc de 59 × 8, et une pièce de six tuiles de profond dans un bâtiment qui en
fait quatre. Maintenant : le plancher fait **exactement** la boîte du bâtiment au-dessus de
sa vitrine, à toutes les portes et sur cinq graines ; une longue façade se **coupe en
vitrines de huit tuiles**, chacune sa porte, son enseigne et sa pièce ; les commerces et
logements ordinaires sont **posés** à la mesure (`MOBILIER`, dix palettes) et les seize
lieux garantis gardent leur plan dessiné — c'est leur bâtiment qui se taille à eux
