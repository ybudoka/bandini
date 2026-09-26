# La ville s'agrandit au nord : les Friches, la Gare de triage, et la place du Petit-Canton

← [le plan](../plan.md) · [les jalons livrés](README.md) · [le Petit-Canton](le-quartier-chinois.md#fiche)

## Fiche

Première des quatre étapes du [Petit-Canton](le-quartier-chinois.md#fiche), tranchée avec Martin le 26 sept. 2026 :
**1. la ville s'agrandit au nord** (ce fichier) · 2. le Petit-Canton, le quartier lui-même · 3. le donneur et ses
missions · 4. [les Mantes](l-ecole-rivale.md#fiche).

_Ce que ça donne :_ la carte gagne **110 rangées par le haut**, sur toute sa largeur. Au-dessus des Érables, **les
Friches** : un terrain vague qu'on traverse. Au-dessus de La Shop, **la Gare de triage** : des voies, des wagons et
un poste d'aiguillage. Entre les deux, au-dessus du Faubourg, **la place du Petit-Canton** : ses rues sont déjà
tracées, mais ses îlots sont encore des terrains clôturés. Rien de la ville d'avant ne change, sauf son adresse.
Elle est 110 rangées plus bas.

**Tranché avec Martin (26 sept. 2026)** :
- **Au nord, par une translation.** Toute la ville descend. Le haut de la carte ne s'insère pas dans la trame.
- **La taille du Faubourg.** Le Petit-Canton aura la hauteur de la bande nord de la trame (110 rangées) et la
  largeur des colonnes du Faubourg.
- **Du terrain vague et des voies ferrées** de chaque côté. Les deux sont jouables : on y marche, on y roule, on s'y
  cache.
- **L'approche A** : la bande est une **deuxième ville**, bâtie par le même générateur sur une trame à elle et avec
  sa propre graine, puis collée dans les rangées libérées.

### L'ordre des opérations

`carte.generer()` bâtit la ville **exactement comme aujourd'hui**, aéroport, île et relief compris : mêmes tirages,
même ordre. Puis une toute dernière étape, dans un module neuf `app/nord.py`, fait trois choses :

1. **Décaler.** Tout descend de `DECALAGE_NORD = 110` rangées (+1 760 px) : le sol, les portes, le décor, les lampes,
   les chars, les arrêts, les lignes de bus, le métro, le tram, les points d'intérêt, les zones, les pièces, les
   annexes, et l'aéroport, l'île, la foire et le traversier. On décale **après** eux : les constantes en dur
   (`AEROPORT`, `ILE`) ne changent pas, et elles gardent leur sens de coordonnées de la ville d'avant.
   ⚠️ Pour ne rien oublier, la translation parcourt **toutes** les clés de la carte. Une clé qu'elle ne sait pas
   décaler fait échouer `generer`, pas un juge lointain : une clé neuve ajoutée plus tard par une autre session
   rougit tout de suite.
2. **Bâtir la bande.** Elle a sa propre trame, `TRAME_NORD`, avec les **mêmes colonnes** que la ville (`COLONNES`
   et `RUES_V`), pour que chaque rue nord-sud tombe en face d'une rue de la ville. Elle a aussi ses propres
   rangées, ses trois districts et sa graine (`GRAINE_NORD`). Les noms qu'elle crée portent le préfixe `nord_`
   (pièces, lieux, points), pour ne jamais entrer en collision avec `commerce_24` et les autres.
3. **Coudre.** Le boulevard qui bordait la ville au nord (y 0 à 5 aujourd'hui) devient la couture. La trame de la
   bande n'a **pas de rue au sud** : sa dernière rangée d'îlots s'appuie sur ce boulevard, et ses rues nord-sud y
   débouchent aux croisements qui existent déjà. Ses rangées et ses rues remplissent exactement les 110 rangées.
   Rien de la ville d'avant n'est repeint, sauf la bordure nord du boulevard, qui s'ouvre sur les rues de la bande.

⚠️ **Le risque, et où il se mesure en premier** : `_Chantier` lit `COLONNES`, `RANGEES`, `RUES_V` et `RUES_H` comme
des globales du module (21 usages). La première tâche du plan est une sonde, qui fait bâtir une trame passée en
paramètre, avec la ville d'avant identique à la tuile près. Si le générateur ne se laisse pas paramétrer à un coût
raisonnable, on s'arrête et on revient voir Martin, avec le repli déjà connu : un plan dessiné, la recette de
l'aéroport.

### La bande, morceau par morceau

La nouvelle carte fait 459 × 414. Dans la bande (y de 0 à 109) :

| x | Morceau | Ce qu'on y trouve |
|---|---|---|
| 0 → ≈ 117 | **Les Friches** (`friches`), au-dessus des Érables | herbes hautes, sentiers de terre battue, clôtures percées, deux ou trois carcasses d'autos (décor solide), des cabanons barricadés ; peu de monde : quelques flâneurs, des chiens errants ; aucune pièce visitable |
| ≈ 118 → ≈ 266 | **Le Petit-Canton** (`canton`), au-dessus du Faubourg | les **rues tracées** de sa trame (une grille serrée : les colonnes du Faubourg, des rangées plus courtes) ; les îlots sont des **terrains à bâtir** : une palissade de chantier, du gravier et un panneau « TERRAIN À BÂTIR » ; personne n'y habite encore |
| ≈ 267 → 418 | **La Gare de triage** (`gare`), au-dessus de La Shop | six à huit voies parallèles, des wagons de marchandises immobiles (décor solide, on s'y cache), des hangars de tôle, une clôture grillagée avec un portail, et **une pièce visitable** : le poste d'aiguillage (`nord_aiguillage`), pour qu'une mission future puisse y entrer |
| 419 → 458 | le relief | les montagnes de l'est, prolongées vers le haut, comme elles bordent déjà la ville |

- **Les trois districts** entrent dans `DISTRICTS` (pour la bande), avec leur rectangle, leur nom affiché, leur
  population (peu de passants, peu de chars, pas de brume) et leur gang :
  - `friches` → les Chevreuils, ceux des Érables ;
  - `gare` → les Boulonneux, ceux de La Shop ;
  - `canton` → les Cravates, ceux du Faubourg, jusqu'à ce que les Mantes le prennent à l'étape 4.

  Un district sans gang existe déjà (la baie, `gang: None`), mais personne n'y marche. On n'ouvre pas ce chemin ici.
- **Les terrains à bâtir** sont un usage de bloc à eux (une lettre de plan neuve, choisie peu courante : voir
  « Glyphes libres disputés entre sessions »). À l'étape 2, le Petit-Canton remplacera ces îlots par ses bâtiments
  sans toucher ses rues, donc sans rien décaler une deuxième fois.
- **Pas de train qui roule, ni bus ni tram dans la bande.** Un train qui bouge est un système entier ; le
  Petit-Canton aura son bus à l'étape 2.

### Ce qui doit connaître le décalage

- **`standing_en`, `usage_en`, `district_en`** (Python) et **`Monde.lettreDuBloc`** (JS) calculent le bloc depuis la
  trame, qui commençait à y = 0. Ils lisent maintenant deux trames : celle de la ville, à partir de
  `y = DECALAGE_NORD`, et celle de la bande, à partir de 0. `rect_district` fait de même.
- **Les blocs de carte** : leurs `passage` restent écrits en coordonnées de la ville d'avant, et c'est
  `app/blocs/__init__.py` qui les décale de `DECALAGE_NORD` en les posant sur la carte finie (les Galeries, de 60 à
  170 ; le rang, de 171 à 281 ; le ciné-parc, de 94 à 204). Le bord nord n'a plus aucun passage (voir plus
  bas).
- **La carte du jeu** (touche N), la caméra, les blips et la police lisent la taille de la carte. Ils n'ont rien de
  codé en dur à 304 ; un juge le vérifie.
- **Les missions** n'ont aucune coordonnée absolue : elles lisent des lieux et des points, qui descendent avec la
  ville.

### Les blocs du bord nord : le ciné-parc à l'ouest, et le rang

Martin, 26 sept. 2026 : « Déplace le ciné-parc à l'ouest et ajuste son entrée. Regroupe la clairière et la cabane à
sucre avec le chalet. » Puis : « Je préfère une vraie fusion », et « assure-toi que l'entrée de la ville au rang soit
bien une ouverture de rue ». La bande couvre le bord nord. Plutôt que d'y tirer des chemins, **le bord nord n'a plus
aucun passage** : le ciné-parc passe à l'ouest, et la clairière, la cabane et le chalet deviennent **un seul bloc :
le rang**.

Le bord ouest de la ville est un trottoir de ceinture qui longe une rue nord-sud (x 1 à 4), de y 0 à 190. Dans les
coordonnées de la ville d'avant :

| Bloc | Avant | Après |
|---|---|---|
| les Galeries | ouest, 60 | inchangé |
| **le ciné-parc** | nord, x 350 | **ouest, 94** : un tronçon droit du trottoir, aux Érables |
| la clairière | nord, x 55 | fondue dans le rang |
| le chalet | ouest, 164 (le trottoir le long d'un îlot) | fondu dans le rang |
| la cabane à sucre | nord, x 200 | fondue dans le rang |
| **le rang** | — | **ouest, 171 à 174** : l'ouverture de la rue des y 172-173 |

**L'entrée du rang est une ouverture de rue.** La rue à deux voies des y 172-173, aux Quais, s'arrête aujourd'hui
sur la rue de l'ouest, contre le trottoir de ceinture. Elle **traverse** maintenant jusqu'au bord de la carte : les
deux tuiles de trottoir à x 0 (y 172 et 173) deviennent de l'asphalte, avec les lignes de la rue. Les deux trottoirs
de la rue (y 171 et 174) vont eux aussi jusqu'au bord. On quitte la ville en roulant tout droit sur une vraie rue,
pas en poussant contre un trottoir. Le passage couvre les quatre tuiles, `{"bord": "ouest", "de": 171, "l": 4}` : à
pied sur le trottoir, au volant sur la chaussée.
- Ces tuiles sont **repeintes en dernier, sans un dé**. C'est la seule retouche de la ville d'avant, et le juge
  « la ville d'avant identique » la nomme.
- ⚠️ **Les chars de la ville ne s'y engagent pas.** Une voie qui mène au bord de la carte est un cul-de-sac pour la
  circulation. Le graphe des voies ignore l'ouverture, et un juge fait rouler le trafic devant pour le vérifier.

**Le rang, un seul bloc** (≈ 80 × 50 tuiles ; le chalet en fait 44 × 30). C'est un seul endroit, pas trois cartes
collées :
- **Le chemin** entre par le bord est. C'est la même rue qui continue en gravier : deux voies et leurs accotements,
  quatre tuiles, en face des quatre tuiles du passage (`retour` : bord est, `l: 4`). L'`arrivee` se pose juste en
  dedans du bord, et le chemin file vers l'ouest.
- **Le chalet** est posé sur la rive du **lac de la clairière**. Son étang disparaît : il n'y a plus qu'un lac, avec
  sa grève et son quai de bois. La place du char de la planque est devant le chalet. Sa pièce, son prix, son coffre
  partagé et sa cheminée qui fume ne changent pas.
- **La cabane à sucre** est de l'autre côté du chemin, dans son érablière. Sa pièce, son comptoir, la tire, le défi
  et sa fermeture hors saison ne changent pas.
- Des arbres partout autour, et personne n'y naît (`gens: False`), comme les trois blocs d'avant.
- Le panneau en ville dit **RANG**, et celui du retour **VILLE**.

**Ce qui suit la fusion**
- Le bloc a le slug `rang` ; `clairiere`, `cabane` et `chalet` disparaissent de `BLOCS`. Leurs **lieux** gardent leur
  nom : `chalet` pour la planque, `cabane` pour la mission de la tire et le comptoir. Seul `magasins.py`
  (`"bloc": "cabane"`) change.
- Une partie sauvegardée dans l'un des trois vieux blocs se réveille dans le rang : au chalet si c'est la planque,
  sinon à l'arrivée.
- Le juge des blocs (`erreurs`) vérifie qu'on rejoint à pied depuis l'arrivée les deux portes, la place du char et le
  quai.

**Le ciné-parc** : son passage passe au bord ouest (y 94, un tronçon droit du trottoir). Dans le bloc, on arrivait
par le sud. On arrive maintenant par l'**est** : le guichet, la barrière et l'allée d'accès passent sur son côté est,
les rangées de cases restent face à l'écran, et on entre par le côté pour les longer. Le film et le reste ne
changent pas.

Ce chantier ne dépend pas de la translation. **Il se livre en premier**, seul : le rang et le ciné-parc au bord
ouest, puis la bande sur un bord nord libre.

### La sauvegarde

Aujourd'hui, **tout** changement de catalogue (l'empreinte) oublie déjà la position du joueur et celle du char de sa
planque (`jeu.js`, `chargerPartie`) : il se réveille à la planque, qui est lue sur la carte. Ce comportement reste.

La carte porte `decalage_nord`, et la partie retient celui sous lequel elle a été écrite (absent = 0). Au
chargement, **ce que la partie garde encore en tuiles ou en pixels absolus** se décale de la différence. Le plan en
dresse la liste exacte ; un juge l'établit en cherchant toute coordonnée dans une partie complétée. Aucune vieille
partie ne se retrouve avec un skimmer ou une cachette au milieu des Friches.

### Ce qui n'y est pas

Ces éléments viennent aux étapes suivantes :
- les bâtiments, les devantures, les lanternes et l'arche du Petit-Canton ;
- le bus du Petit-Canton ;
- le donneur et ses missions ;
- les Mantes et leur territoire.

Ces éléments n'ont pas d'étape prévue :
- le train qui roule ;
- une musique de quartier.

**Juges** :
- **La ville d'avant, décalée, est identique** à la tuile près. Les deux villes sont comparées en JSON, clé par clé,
  avec +110 sur chaque y (« Grossir un lieu garanti déplace la ville »). La seule exception permise est la bordure
  nord du boulevard de la couture, et le juge la nomme.
- **Aucun tirage de la ville ne bouge** : la bande a sa graine et se bâtit après.
- **La translation refuse une clé inconnue** : mutée (une clé ajoutée), `generer` échoue.
- **Les trois districts existent**, avec leur rectangle, leur gang et leur standing. `district_en` et
  `Monde.lettreDuBloc` répondent juste de part et d'autre de la couture.
- **La bande est atteignable** à pied et au volant depuis le terminus (les composantes par terre), et le poste
  d'aiguillage s'ouvre.
- **Les trois blocs de carte se branchent toujours** (les Galeries, le ciné-parc, le rang), tous au bord ouest :
  on passe au bon endroit, on arrive par le bord est du bloc, on revient au même endroit, à pied et au volant. Aucun
  passage n'en chevauche un autre, et aucun n'est au bord nord (`test_blocs`).
- **L'entrée du rang est une rue** : les tuiles du passage sont de la chaussée et du trottoir qui continuent la rue
  des y 172-173 jusqu'au bord, et aucun char de la circulation ne s'y engage.
- **Une vieille partie** (sans `decalage_nord`) retrouve ses coordonnées gardées décalées de 110.
- **Aucune clé de nom `nord_` n'entre en collision** avec une clé de la ville.
- **Les tests qui avaient des y en dur** (une douzaine de lignes : `test_chalet_js`, `test_districts_js`,
  `test_moteur_js`, `test_blocs_js`…) les lisent désormais sur la carte.
- Le temps de `generer` (2,8 s aujourd'hui) et le poids du paquet des définitions (`test_definitions`) sont mesurés
  avant d'atterrir.
- **Une capture** de la bande entière, une de chaque couture, une du rang entier, une de son ouverture de rue en ville et
  une de l'entrée du ciné-parc, ouvertes dans Aperçu pour Martin avant de livrer.

## Notes

_Rien de livré._
