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

### Le plan d'exécution

> **Pour l'exécutant** : compétence requise, `superpowers:executing-plans` (ou `subagent-driven-development`).
> Les étapes se cochent (`- [ ]`). La spec, c'est la fiche ci-dessus : le plan argumente à partir d'elle.

**But** : la ville descend de 110 rangées, et une deuxième ville bâtie par le même générateur remplit la bande
nord (les Friches, la place du Petit-Canton, la Gare de triage). Avant ça, le rang (le chalet, la clairière et la
cabane fondus en un seul bloc) et le ciné-parc passent au bord ouest.

**Architecture** : `carte.generer()` ne change pas d'un tirage. Tout à la fin, `nord.poser(ville)` fait trois
choses : il **décale** la ville d'avant avec une table explicite, une entrée par clé de la carte ; il **bâtit**
la bande par `_Chantier`, qui reçoit sa trame en paramètre ; il **coud** les deux à la hauteur du boulevard du
nord. Le navigateur lit deux trames (`grille` et `grille_nord`).

**Outils** : Python 3.14, Flask, JS vanilla, pytest, le banc JS (`banc`, sous Node).

#### Contraintes pour toutes les tâches

- **Worktree** du `dev` local (le scratchpad `wt`), jamais l'arbre partagé.
- WIP commité sous `refs/wip/nord` à chaque tâche : un redémarrage vide le scratchpad.
- pytest par `UV_PROJECT_ENVIRONMENT=/Users/martingagne/dev/bandini/.venv uv run --frozen pytest -q …`.
- `git add` de fichiers nommés, jamais `-A`, jamais `git stash`.
- `ruff check .` avant d'atterrir. La suite complète par le lanceur parallèle (`par.py`), jamais une boucle zsh.
  Pas de Chromium pendant une suite.
- **Aucun dé de la ville ne bouge** : ce qu'on ajoute se pose en dernier, sans dé. La bande a sa graine,
  `GRAINE_NORD = 20260926`.
- `DECALAGE_NORD = 110`, dans `app/nord.py`, et nulle part ailleurs en dur.
- Les noms que la bande crée (pièces, lieux, points) commencent par `nord_`.
- Chaque juge neuf est **muté une fois** pour le voir rougir. On lit le message : une mutation qui casse la
  syntaxe rougit pour rien.
- On atterrit après les verts ciblés, par cherry-pick puis `merge --ff-only`, **sans pousser**. La suite complète
  vient après. La tâche 1 atterrit seule ; les tâches 2 à 6 atterrissent ensemble.

**Deux écarts avec la spec, lus dans le code** :
- **`standing_en`, `usage_en` et `district_en` restent à une trame.** Ils ne servent que pendant la génération,
  et chaque chantier (la ville, la bande) a la sienne. Seul le navigateur (`Monde.lettreDuBloc`) lit les deux
  trames, parce qu'il lit la carte finie.
- **L'ouverture de rue du rang est une retouche de la VILLE** (`carte.OUVERTURES_DE_RUE`), et non du bloc. Le juge
  `test_un_bloc_ne_change_pas_un_octet_de_la_ville` interdit à un bloc de toucher la carte.

#### À surveiller en relecture

1. **Une clé neuve dans la carte**, ajoutée par une autre session : `nord.decaler` lève une erreur qui la nomme,
   au lieu de la laisser au mauvais y. Juge à la tâche 4.
2. **Un y oublié dans une structure imbriquée** (une paire `[x, y]` ou un `y` dans un sous-objet) : un juge
   parcourt toute la ville d'avant et exige que chaque objet `{x, y}` ait descendu de 110. Les paires sont
   jugées par les tests de leurs modules (bus, tram, charrue, éboueurs, petit train, montagne russe, chemins,
   aéroport). Juge à la tâche 4.
3. **Une vieille partie** : sa position, son char, ses skimmers et son passage de bloc descendent de 110. Une
   partie qui dormait au chalet se réveille au chalet du rang. Juges aux tâches 1 et 6.
4. **La circulation et l'ouverture du rang** : aucun char ne s'engage vers le bord. Juge à la tâche 1.
5. **La couture** : un char passe de la ville à la bande et revient en suivant les flèches (`carte.suivre_voie`),
   et un piéton aussi. Juge à la tâche 5.

---

#### Tâche 1 : le rang et le ciné-parc au bord ouest

**Fichiers** :
- Créer : `app/blocs/rang.py`
- Supprimer : `app/blocs/chalet.py`, `app/blocs/clairiere.py`, `app/blocs/cabane.py` (leurs `PIECE` passent dans
  `rang.py`)
- Modifier : `app/blocs/__init__.py` (`BLOCS`, l'import), `app/blocs/cineparc.py`, `app/carte.py`
  (`OUVERTURES_DE_RUE`, `ouvrir_les_rues`, l'appel dans `generer`), `app/magasins.py` (`"bloc": "rang"`),
  `static/js/base.js` (`Sauvegarde.completer` : la migration des slugs)
- Tests : `tests/test_blocs.py`, `tests/test_blocs_js.py`, `tests/test_chalet_js.py`, `tests/test_cabane_js.py`,
  `tests/test_cineparc_js.py`, `tests/test_traversier_js.py`, et un neuf, `tests/test_rang.py`

**Interfaces** :
- Produit : le bloc `rang`, avec `passage: {"bord": "ouest", "de": 171, "l": 4}`,
  `retour: {"bord": "est", "de": 23, "l": 4}`, `arrivee: {"x": 77, "y": 24}` ; ses portes `chalet` (43, 16) et
  `cabane` (64, 16) ; `planque: {"piece": "chalet", "prix": 2500, "char": {"x": 46, "y": 18}}`.
- Produit : le ciné-parc, avec `passage: {"bord": "ouest", "de": 94, "l": 5}`,
  `retour: {"bord": "est", "de": 21, "l": 4}` et `arrivee: {"x": 41, "y": 22}`.
- Produit : `carte.OUVERTURES_DE_RUE = ({"x": 0, "y": 172, "g": "#"}, {"x": 0, "y": 173, "g": "+"})` et
  `carte.ouvrir_les_rues(ville)`. Les coordonnées sont celles de la ville d'avant ; la tâche 4 les décale avec le
  reste.

- [ ] **Étape 1 : les juges neufs, rouges** (`tests/test_rang.py`)

```python
"""Le rang : le chalet, le lac de la clairière et la cabane à sucre, un seul bloc au bout d'une rue
(docs/jalons/la-ville-s-agrandit-au-nord.md)."""

from app import blocs, carte
from app.blocs import rang

VILLE = carte.generer()


def test_trois_blocs_tous_au_bord_ouest():
    slugs = [b["slug"] for b in blocs.BLOCS]
    assert sorted(slugs) == ["cineparc", "galeries", "rang"], slugs
    assert all(b["passage"]["bord"] == "ouest" for b in blocs.BLOCS)
    pris = [range(b["passage"]["de"], b["passage"]["de"] + b["passage"]["l"]) for b in blocs.BLOCS]
    for i, a in enumerate(pris):
        for b in pris[i + 1:]:
            assert not set(a) & set(b), "deux passages se chevauchent"


def test_l_entree_du_rang_est_une_rue_qui_va_jusqu_au_bord():
    sol, voie = VILLE["sol"], VILLE["voie"]
    p = rang.BLOC["passage"]
    tuiles = [sol[p["de"] + i][0] for i in range(p["l"])]
    assert tuiles == [".", "#", "+", "."], tuiles          # trottoir, deux voies, trottoir
    # La même rue, une tuile plus loin : c'est bien elle qui continue.
    assert [sol[172][x] for x in range(1, 5)] == ["#"] * 4


def test_aucun_char_de_la_circulation_ne_s_engage_vers_le_bord():
    voie = VILLE["voie"]
    assert voie[172][0] == "." and voie[173][0] == ".", "l'ouverture n'est pas une voie de circulation"
    for inter in VILLE["intersections"]:
        if inter["x"] <= 1 and inter["y"] <= 173 < inter["y"] + inter["h"]:
            assert "O" not in inter["bras"], inter


def test_depuis_l_arrivee_on_rejoint_les_deux_portes_le_char_et_le_quai():
    assert blocs.erreurs(rang.BLOC, VILLE) == []
    plan = rang.BLOC["plan"]
    quai = [(x, y) for y, ligne in enumerate(plan) for x, g in enumerate(ligne) if g == "Q"]
    assert quai, "le lac de la clairière a perdu son quai"
    assert set(quai) & blocs.a_pied_depuis_l_arrivee(rang.BLOC), "on ne rejoint pas le quai à pied"
```

Run : `… pytest -q tests/test_rang.py`
Attendu : ÉCHEC à l'import (`cannot import name 'rang'`).

- [ ] **Étape 2 : `app/blocs/rang.py`**

Le plan est composé une fois, sans dé, à partir des trois plans d'avant, par ce script
(`scratchpad/composer_rang.py`, lancé avant de supprimer les trois fichiers). Sa sortie, collée telle quelle,
devient `PLAN` :

```python
"""Compose le plan du rang depuis les trois blocs d'avant (sans un dé)."""
import sys
sys.path.insert(0, '.')
from app.blocs import chalet, clairiere, cabane

L, H = 80, 50
g = [[","] * L for _ in range(H)]
for y in range(H):
    for x in range(L):
        if x in (0, L - 1) or y in (0, H - 1):
            g[y][x] = "A"
        elif x in (1, L - 2) or y in (1, H - 2):
            g[y][x] = "A" if (x + y) % 2 == 0 else ","
        elif (x * 7 + y * 13) % 29 == 0:
            g[y][x] = "A"
        elif (x * 11 + y * 5) % 37 == 0:
            g[y][x] = "b"

def coller(src, sx, sy, l, h, dx, dy):
    for j in range(h):
        for i in range(l):
            g[dy + j][dx + i] = src[sy + j][sx + i]

def rect(x, y, l, h, c):
    for j in range(h):
        for i in range(l):
            g[y + j][x + i] = c

rect(3, 2, 32, 16, ",")
coller(clairiere.PLAN, 6, 2, 28, 13, 4, 3)          # le lac, sa grève et son quai (QQQ, rangée 14)
rect(17, 15, 3, 8, "g")                              # le sentier du quai jusqu'au chemin
CX, CY = 38, 11
rect(CX - 2, CY - 1, 15, 13, ",")
coller(chalet.PLAN, 13, 11, 11, 6, CX, CY)           # le chalet ; sa porte à (43, 16)
rect(CX + 5, CY + 6, 1, 23 - (CY + 6), "g")
rect(CX + 7, CY + 7, 3, 2, "p")                      # la place du char, (45..47, 18..19)
KX, KY = 58, 11
rect(KX - 1, KY - 1, 16, 13, ",")
coller(cabane.PLAN, 13, 7, 14, 6, KX, KY)            # la cabane ; sa porte à (64, 16)
rect(KX + 6, KY + 6, 1, 23 - (KY + 6), "g")
rect(17, 23, L - 17, 4, "g")                         # le chemin : 4 rangées, du bord est au sentier
print("PLAN: tuple[str, ...] = (")
for ligne in g:
    print(f'    "{"".join(ligne)}",')
print(")")
```

Le reste de `rang.py` :

```python
"""Le rang : le chalet, le lac de la clairière et la cabane à sucre, un seul bloc
(docs/jalons/la-ville-s-agrandit-au-nord.md).

Martin (26 sept. 2026) : « Regroupe la clairière et la cabane à sucre avec le chalet. » Puis : « Je préfère
une vraie fusion », et « l'entrée de la ville au rang [doit être] une ouverture de rue ». On quitte la ville
par la rue des Quais qui traverse jusqu'au bord ouest (`carte.OUVERTURES_DE_RUE`) ; au noir, on est sur le
chemin de gravier qui la continue. Le chalet est au bord du lac, la cabane dans son érablière.

⚠️ LE CHALET S'ACHÈTE (2 500 $) et reste la deuxième planque ; la cabane garde son comptoir, sa saison et sa
tire. Leurs PIÈCES n'ont pas bougé d'une tuile : elles viennent des anciens `chalet.py` et `cabane.py`.
"""

from .. import carte

PLAN: tuple[str, ...] = (
    # ← la sortie de composer_rang.py, 50 lignes de 80
)

DECORS: dict[str, tuple[str, str]] = {"A": (",", "arbre"), "b": (",", "buisson")}

PIECE_CHALET = …   # le `PIECE` de l'ancien chalet.py, recopié tel quel
PIECE_CABANE = …   # le `PIECE` de l'ancien cabane.py, recopié tel quel

BLOC = {
    "slug": "rang",
    "nom": "Le rang",
    "plan": PLAN,
    "decors": DECORS,
    "panneau": "RANG", "panneau_retour": "VILLE",
    # Le passage : la rue des Quais qui traverse jusqu'au bord ouest — trottoir, deux voies, trottoir.
    "passage": {"bord": "ouest", "de": 171, "l": 4},
    # Le chemin de gravier la continue, par le bord est du bloc : les mêmes quatre rangées.
    "retour": {"bord": "est", "de": 23, "l": 4},
    "arrivee": {"x": 77, "y": 24},
    "gens": False,
    "materiaux": {"F": "bois_rond", "W": "bois_rond", "D": "bois_rond"},
    "portes": [{"x": 43, "y": 16, "interieur": "chalet", "lieu": "chalet"},
               {"x": 64, "y": 16, "interieur": "cabane", "lieu": "cabane"}],
    "pieces": {"chalet": PIECE_CHALET, "cabane": PIECE_CABANE},
    "planque": {"piece": "chalet", "prix": 2500, "char": {"x": 46, "y": 18}},
    "cheminees": [{"x": 43, "y": 12, "l": 2}],
    "lampes": [{"x": 59, "y": 17, "r": 26, "c": "fenetre"}, {"x": 70, "y": 17, "r": 26, "c": "fenetre"}],
}
```

Remplacer les `…` par les deux `PIECE` d'origine : le code complet, pas un renvoi. Supprimer `chalet.py`,
`clairiere.py` et `cabane.py`. Dans `app/blocs/__init__.py` :

```python
from . import cineparc, galeries, rang

BLOCS: list[dict] = [rang.BLOC, cineparc.BLOC, galeries.BLOC]
```

Ajouter dans `blocs/__init__.py` la fonction que le juge appelle ; `erreurs` la réutilise pour son parcours :

```python
def a_pied_depuis_l_arrivee(bloc: dict) -> set[tuple[int, int]]:
    """Les tuiles qu'on rejoint à pied depuis l'arrivée (les arbres arrêtent)."""
    sol = sol_du_bloc(bloc)
    hauteur, largeur = len(sol), len(sol[0])
    arbres = {(d["x"], d["y"]) for d in decor_du_bloc(bloc) if d["type"] == "arbre"}
    a = bloc["arrivee"]
    vues, pile = {(a["x"], a["y"])}, [(a["x"], a["y"])]
    while pile:
        x, y = pile.pop()
        for nx, ny in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
            if (0 <= nx < largeur and 0 <= ny < hauteur and (nx, ny) not in vues
                    and carte.LEGENDE.get(sol[ny][nx], {}).get("solide", 0) == 0 and (nx, ny) not in arbres):
                vues.add((nx, ny))
                pile.append((nx, ny))
    return vues
```

- [ ] **Étape 3 : le ciné-parc à l'ouest, son entrée à l'est** (`app/blocs/cineparc.py`)

Remplacer les lignes 20 à 29 de `PLAN` par ces lignes. Le grillage de l'est s'ouvre sur les rangées 21 à 24,
l'allée va jusqu'au bord, et le côté sud se ferme :

```python
    "AA,,f###^^^^^^^^^^^^^^^^^^^^^^^^^^^^###f,,AA",
    "A,,,f#OOOOOO################################",
    "AA,,f#OOOOOO################################",
    "A,,,f#FWdFWF################################",
    "AA,,f#######################################",
    "A,,,ffffffffffffffffffffffffffffffffffff,,,A",
    "AA,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,AA",
    "A,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,A",
    "AA,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,AA",
    "A,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,A",
```

Puis, dans `BLOC` :

```python
    # Le passage : le trottoir de ceinture du bord OUEST des Érables (un tronçon droit, 94 à 98).
    "passage": {"bord": "ouest", "de": 94, "l": 5},
    # L'allée arrive par le bord EST du terrain, ses quatre rangées d'asphalte, le long du casse-croûte.
    "retour": {"bord": "est", "de": 21, "l": 4},
    "arrivee": {"x": 41, "y": 22},
    "lampes": [{"x": 7, "y": 24, "r": 26, "c": "fenetre"}, {"x": 10, "y": 24, "r": 26, "c": "fenetre"},
               {"x": 41, "y": 20, "r": 40, "c": "lampadaire"}, {"x": 41, "y": 25, "r": 40, "c": "lampadaire"}],
```

Mettre la docstring à jour : il n'est plus au bord nord de La Shop, mais au bord ouest des Érables, et l'on
entre par le côté.

- [ ] **Étape 4 : l'ouverture de rue, dans la ville** (`app/carte.py`)

Près de `generer` :

```python
#: LES RUES QUI TRAVERSENT JUSQU'AU BORD (Martin, 26 sept. 2026 : « l'entrée de la ville au rang [doit être] une
#: ouverture de rue »). La rue à deux voies des Quais (y 172-173) s'arrêtait sur la rue de l'ouest, contre le
#: trottoir de ceinture : ses deux tuiles de trottoir à x 0 deviennent sa chaussée, et le passage du rang
#: (`blocs/rang.py`) les couvre, avec les deux trottoirs. ⚠️ En DERNIER et sans un dé, et JAMAIS dans `voie` :
#: la circulation ne s'engage pas dans un cul-de-sac au bord de la carte.
OUVERTURES_DE_RUE: tuple[dict, ...] = ({"x": 0, "y": 172, "g": "#"}, {"x": 0, "y": 173, "g": "+"})


def ouvrir_les_rues(ville: dict) -> None:
    for o in OUVERTURES_DE_RUE:
        ligne = ville["sol"][o["y"]]
        if ligne[o["x"]] != ".":
            raise ValueError(f"l'ouverture ({o['x']}, {o['y']}) ne tombe pas sur le trottoir : {ligne[o['x']]!r}")
        ville["sol"][o["y"]] = ligne[:o["x"]] + o["g"] + ligne[o["x"] + 1:]
```

À la fin de `generer`, après `chantiers_mod.completer(ville, graine)` : `ouvrir_les_rues(ville)`.

- [ ] **Étape 5 : le comptoir des sucres et la vieille partie**

Dans `app/magasins.py`, sur le comptoir `sucre`, remplacer `"bloc": "cabane"` par `"bloc": "rang"`, et mettre
son commentaire à jour.

Dans `static/js/base.js`, `Sauvegarde.completer`, après la ligne qui valide `out.bloc`, ajouter :

```js
    // ⚠️ LE RANG (26 sept. 2026) : le chalet, la clairière et la cabane sont UN bloc, `rang`. Une partie
    // d'avant garde sa planque (le chalet acheté), son char (à la place du rang : il y a changé de tuile)
    // et se réveille au rang — devant le chalet si elle y dormait, à l'arrivée sinon.
    const FONDUS = { chalet: 1, clairiere: 1, cabane: 1 };
    out.planques = out.planques.map(function (s) { return s === 'chalet' ? 'rang' : s; })
      .filter(function (s, i, t) { return t.indexOf(s) === i; });
    if (out.charsDesPlanques && out.charsDesPlanques.chalet) {
      out.charsDesPlanques.rang = Object.assign({}, out.charsDesPlanques.chalet, { x: null, y: null });
      delete out.charsDesPlanques.chalet;
    }
    if (out.bloc && FONDUS[out.bloc.slug]) {
      const auChalet = out.bloc.slug === 'chalet';
      out.bloc = { slug: 'rang', x: (auChalet ? 43 : 77) * 16 + 8, y: (auChalet ? 17 : 24) * 16 + 8 };
    }
```

- [ ] **Étape 6 : les juges d'avant suivent**
  - `tests/test_blocs_js.py` : `OUTILS` devient générique par bord. `passage(L, slug)` ; `auPassage` pose le
    joueur à `x = TT + 8`, `y = (p.de + Math.floor(p.l / 2)) * TT + 8` pour un bord `ouest` ; `entrer` pousse
    `KeyA` ; `versLeRetour`, pour un retour `est`, pose à `x = (L.Monde.carte.w - 2) * TT + 8`,
    `y = (r.de + 1) * TT + 8`, et pousse `KeyD`.
  - Chaque test qui nommait `clairiere` nomme `rang` : renommer le test, pas seulement la chaîne.
  - Le test du trottoir qu'on longe sans passer longe le trottoir OUEST.
  - `tests/test_chalet_js.py` et `tests/test_cabane_js.py` : le slug `rang`, et les coordonnées du bloc lues dans
    `L.B.bloc.def` ou dans la réponse de `/api/carte/bloc/rang`, jamais en dur.
  - `tests/test_blocs.py` : la liste des slugs, et `test_on_ressort_d_un_bloc_dans_le_sens_ou_l_on_est_venu`
    pour les bords ouest et est.
  - `tests/test_cineparc_js.py` et `tests/test_traversier_js.py` : lire leurs lignes qui nomment `clairiere`,
    `chalet` ou le bord nord, et les suivre.
  - Ajouter un juge de migration dans `tests/test_chalet_js.py` : une partie
    `{planques: ['chalet'], charsDesPlanques: {chalet: {slug: 'pickup', x: 10, y: 10}}, bloc: {slug: 'chalet', x: 1, y: 1}}`
    passée à `Sauvegarde.completer` donne `planques == ['rang']`, `charsDesPlanques.rang.x === null` et
    `bloc == {slug: 'rang', x: 696, y: 280}`.

- [ ] **Étape 7 : vert, muté, capturé**

Run :
`… pytest -q tests/test_rang.py tests/test_blocs.py tests/test_blocs_js.py tests/test_chalet_js.py tests/test_cabane_js.py tests/test_cineparc_js.py tests/test_traversier_js.py tests/test_magasins.py tests/test_definitions.py`
Attendu : tout PASSE.

Mutations, une à la fois, chacune rougit :
- `OUVERTURES_DE_RUE = ()` → `test_l_entree_du_rang_est_une_rue…` ;
- `"O"` ajouté au `bras` du croisement de la rue de l'ouest à y 172 → `test_aucun_char…` ;
- le sentier du quai remis en `,` → `test_depuis_l_arrivee…`.

Captures (`capture.py`) : le rang entier, son ouverture de rue en ville (le coin x 0 à 20, y 160 à 185) et
l'entrée du ciné-parc. Les copier dans `captures/` et les ouvrir dans Aperçu pour Martin.

- [ ] **Étape 8 : commit, et atterrir seul**

```bash
git add app/blocs/rang.py app/blocs/__init__.py app/blocs/cineparc.py app/carte.py app/magasins.py static/js/base.js tests/test_rang.py tests/test_blocs.py tests/test_blocs_js.py tests/test_chalet_js.py tests/test_cabane_js.py tests/test_cineparc_js.py tests/test_traversier_js.py
git rm -q app/blocs/chalet.py app/blocs/clairiere.py app/blocs/cabane.py
git commit -m "feat: le rang — le chalet, le lac et la cabane en un bloc au bout d'une rue ; le ciné-parc à l'ouest"
```

`ruff`, puis atterrir (cherry-pick sur `dev` à jour, `merge --ff-only`), sans pousser. La suite complète suit.

---

#### Tâche 2 : le générateur prend sa trame en paramètre

**Fichiers** : modifier `app/carte.py` (`_Chantier`) ; tests : `tests/test_nord.py` (neuf).

**Interfaces** :
- Produit :
  `_Chantier(plan, graine, trame=None)`, où
  `trame = {"colonnes", "rangees", "rues_v", "rues_h", "districts", "standing"}` (des tuples). Par défaut, c'est
  la trame de la ville (`COLONNES`, `RANGEES`, `RUES_V`, `RUES_H`, `DISTRICTS`, et `STANDING` si
  `plan == PLAN`). Ce sont des attributs d'instance : `self.colonnes`, `self.rangees`, `self.rues_v`,
  `self.rues_h`, `self.districts`.
- Produit : `_Chantier.BATISSEURS: dict[str, Callable]`, vide par défaut. `ilots()` y cherche une lettre de plan
  inconnue avant de lever.

- [ ] **Étape 1 : l'empreinte de la ville d'avant**, sur la base

```bash
./uvw python -c "import json,hashlib; from app import carte; print(hashlib.sha256(json.dumps(carte.generer(), sort_keys=True).encode()).hexdigest())" > ../empreinte_base.txt
```

- [ ] **Étape 2 : le juge rouge** (`tests/test_nord.py`)

```python
"""La ville s'agrandit au nord (docs/jalons/la-ville-s-agrandit-au-nord.md)."""

from app import carte


def test_le_chantier_lit_sa_trame_et_pas_les_globales(monkeypatch):
    """Une autre trame passée en paramètre bâtit une autre ville, même si les globales ne bougent pas."""
    trame = {"colonnes": (10, 10), "rangees": (10,), "rues_v": (4, 4, 4), "rues_h": (4, 4),
             "districts": ({"slug": "essai", "nom": "Essai", "bx": 0, "by": 0, "gang": None,
                            "gang_nom": None, "brume": False, "pietons": 0, "vehicules": 0, "police": 0,
                            "rythme": (0.1, 1.0, 1.0), "rares": (), "plan": ("hh",), "standing": ("==",)},),
             "standing": ("==",)}
    ch = carte._Chantier(("hh",), 1, trame=trame)
    assert (ch.largeur, ch.hauteur) == (32, 18)
    assert ch.district_en(5, 5) == "essai"
```

Run : `… pytest -q tests/test_nord.py` → ÉCHEC (`unexpected keyword argument 'trame'`).

- [ ] **Étape 3 : la refonte**

Dans `_Chantier.__init__` :

```python
    def __init__(self, plan: tuple[str, ...], graine: int, trame: dict | None = None) -> None:
        # ⚠️ LA TRAME EST UN PARAMÈTRE (26 sept. 2026) : la bande nord se bâtit par le même chantier, sur la
        # sienne (`nord.py`). Par défaut, celle de la ville ; aucun tirage ne change.
        trame = trame or {"colonnes": COLONNES, "rangees": RANGEES, "rues_v": RUES_V, "rues_h": RUES_H,
                          "districts": DISTRICTS, "standing": STANDING if plan == PLAN else None}
        self.colonnes, self.rangees = tuple(trame["colonnes"]), tuple(trame["rangees"])
        self.rues_v, self.rues_h = tuple(trame["rues_v"]), tuple(trame["rues_h"])
        self.districts = tuple(trame["districts"])
        self.plan = plan
        self.standing = trame["standing"] or tuple(
            "".join(SANS_STANDING if g == "~" else "=" for g in ligne) for ligne in plan)
```

Puis, **dans le corps de la classe seulement** (de `class _Chantier` à la fin de ses méthodes), remplacer hors
commentaires `COLONNES` → `self.colonnes`, `RANGEES` → `self.rangees`, `RUES_V` → `self.rues_v`, `RUES_H` →
`self.rues_h` et `DISTRICTS` → `self.districts`. Ça fait 44 usages. On le fait par un script Python qui ne touche
que les lignes de la classe, puis on relit le diff.

⚠️ `zones()` appelle `district_par_slug("faubourg")` pour le bassin. On le garde tel quel : la bande filtre ses
zones par district (tâche 5).

Dans `ilots()`, juste avant le `else` qui lève sur une lettre inconnue (ou à la fin de la chaîne de `elif`) :

```python
            elif glyphe in self.BATISSEURS:
                self.BATISSEURS[glyphe](self, x, y, largeur, hauteur)
```

Et sur la classe : `BATISSEURS: dict = {}`.

- [ ] **Étape 4 : identique, et vert**

```bash
./uvw python -c "import json,hashlib; from app import carte; print(hashlib.sha256(json.dumps(carte.generer(), sort_keys=True).encode()).hexdigest())" | diff - ../empreinte_base.txt && echo IDENTIQUE
```

Attendu : `IDENTIQUE`. Puis `… pytest -q tests/test_nord.py tests/test_carte.py tests/test_districts.py tests/test_banlieue.py tests/test_rampes.py` : tout PASSE.

- [ ] **Étape 5 : commit**, sous `refs/wip/nord` (pas d'atterrissage seul).

---

#### Tâche 3 : la bande nord, bâtie à part

**Fichiers** :
- Créer : `app/nord.py`
- Modifier : `app/carte.py` (`USAGE_DU_PLAN` : trois lettres ; `DECOR_SOLIDE` : `carcasse`),
  `static/js/sprites.js` (deux peintres de décor : `carcasse` et `pancarte_a_batir`)
- Tests : `tests/test_nord.py`

**Interfaces** :
- Consomme : `_Chantier(plan, graine, trame=…)` et `_Chantier.BATISSEURS` (tâche 2).
- Produit : `nord.DECALAGE_NORD = 110`, `nord.GRAINE_NORD = 20260926`, `nord.DISTRICTS_NORD`, `nord.TRAME_NORD`,
  `nord.PLAN_NORD`.
- Produit : `nord.batir_la_bande() -> _ChantierNord`, un chantier de 419 × 116. Ses rangées 110 à 115 sont le
  boulevard de la couture, que la pose ne colle pas.
- Produit : `nord.PIECE_AIGUILLAGE`, et le lieu `nord_aiguillage`.

- [ ] **Étape 1 : les juges rouges**

```python
from app import nord


def test_la_bande_fait_110_rangees_plus_la_couture_et_la_largeur_de_la_trame():
    ch = nord.batir_la_bande()
    assert ch.hauteur == nord.DECALAGE_NORD + 6 and ch.largeur == 419


def test_trois_districts_dans_la_bande_avec_leur_gang():
    assert [(d["slug"], d["gang"]) for d in nord.DISTRICTS_NORD] == [
        ("friches", "chevreuils"), ("canton", "cravates"), ("gare", "boulonneux")]


def test_la_gare_a_ses_voies_ses_wagons_et_son_poste():
    ch = nord.batir_la_bande()
    x0, y0, l, h = ch.rect_district(nord.district("gare"))
    zone = [ch.sol[y][x0:x0 + l] for y in range(y0, min(y0 + h, nord.DECALAGE_NORD))]
    assert sum(ligne.count("T") for ligne in map("".join, zone)) > 200, "des voies ferrées"
    assert sum(ligne.count("B") for ligne in map("".join, zone)) > 30, "des wagons"
    postes = [p for p in ch.portes if p["interieur"] == "nord_aiguillage"]
    assert len(postes) == 1 and ch.marchable_en(postes[0]["x"], postes[0]["y"] + 1)


def test_le_canton_n_a_que_des_terrains_a_batir():
    ch = nord.batir_la_bande()
    x0, y0, l, h = ch.rect_district(nord.district("canton"))
    assert not [p for p in ch.portes if x0 <= p["x"] < x0 + l], "personne n'y habite encore"
    pancartes = [d for d in ch.decor if d["type"] == "pancarte_a_batir"]
    assert len(pancartes) >= 20


def test_les_friches_ont_leurs_carcasses_et_pas_une_porte():
    ch = nord.batir_la_bande()
    x0, y0, l, h = ch.rect_district(nord.district("friches"))
    dedans = lambda d: x0 <= d["x"] < x0 + l and d["y"] < nord.DECALAGE_NORD
    assert [d for d in ch.decor if d["type"] == "carcasse" and dedans(d)]
    assert not [p for p in ch.portes if dedans(p)]


def test_tout_ce_que_la_bande_nomme_commence_par_nord():
    ch = nord.batir_la_bande()
    assert all(k.startswith("nord_") for k in ch.pieces)
    assert all(p["interieur"].startswith("nord_") for p in ch.portes)


def test_la_bande_ne_tire_rien_de_la_ville():
    """Même graine, même bande ; et bâtir la bande ne change pas la ville."""
    from app import carte
    avant = carte.generer()
    a, b = nord.batir_la_bande(), nord.batir_la_bande()
    assert a.sol == b.sol and a.decor == b.decor
    assert carte.generer()["sol"] == avant["sol"]
```

Run → ÉCHEC (`No module named 'app.nord'`).

- [ ] **Étape 2 : `app/nord.py`, la trame et les districts**

```python
"""La ville s'agrandit au nord : les Friches, la place du Petit-Canton, la Gare de triage
(docs/jalons/la-ville-s-agrandit-au-nord.md).

Martin (26 sept. 2026) : « au nord, on décale », « comme le Faubourg », « du terrain vague et des voies
ferrées », et l'approche A — la bande est une DEUXIÈME VILLE, bâtie par le même chantier sur sa trame et sa
graine, puis collée au-dessus de la ville d'avant, qui descend de `DECALAGE_NORD` rangées sans qu'un tirage
bouge. `poser` est appelé EN TOUT DERNIER par `carte.generer`.

⚠️ LES MÊMES COLONNES que la ville : chaque rue nord-sud de la bande tombe en face d'une rue de la ville. Et
PAS DE RUE AU SUD : la dernière rue de la trame (6 de large) est le boulevard qui bordait la ville au nord ; on
la bâtit pour que les croisements s'y ouvrent, et on ne la colle pas.
"""

from __future__ import annotations

from . import carte

DECALAGE_NORD = 110
GRAINE_NORD = 20260926
RANGEES_NORD = (11, 11, 11, 12, 11, 11, 11)
RUES_H_NORD = (6, 4, 4, 6, 4, 4, 4, 6)           # la dernière : la couture, jamais collée
assert sum(RANGEES_NORD) + sum(RUES_H_NORD[:-1]) == DECALAGE_NORD

#: `z` friche, `b` terrain à bâtir, `v` voies ferrées : trois lettres de plan que seule la bande emploie.
DISTRICTS_NORD: tuple[dict, ...] = (
    {"slug": "friches", "nom": "Les Friches", "bx": 0, "by": 0,
     "gang": "chevreuils", "gang_nom": "Les Chevreuils", "brume": False,
     "pietons": 4, "vehicules": 1, "police": 0, "rythme": (0.2, 1.0, 0.5), "rares": (),
     "plan": ("z<<<<", "^<<<<", "^<<<<", "z<<<<", "^<<<<", "^<<<<", "^<<<<"),
     "standing": ("-----",) * 7},
    {"slug": "canton", "nom": "Le Petit-Canton", "bx": 5, "by": 0,
     "gang": "cravates", "gang_nom": "Les Cravates", "brume": False,
     "pietons": 2, "vehicules": 2, "police": 0, "rythme": (0.2, 1.0, 0.5), "rares": (),
     "plan": ("bbbbbbbb",) * 7,
     "standing": ("========",) * 7},
    {"slug": "gare", "nom": "La Gare de triage", "bx": 13, "by": 0,
     "gang": "boulonneux", "gang_nom": "Les Boulonneux", "brume": False,
     "pietons": 3, "vehicules": 2, "police": 0, "rythme": (0.15, 1.2, 0.6), "rares": (),
     "plan": ("v<<<<<<", "^<<<<<<", "^<<<<<<", "^<<<<<<", "^<<<<<<", "w<w<w<i", "^<^<^<^"),
     "standing": ("-------",) * 7},
)
PLAN_NORD: tuple[str, ...] = carte._assembler(DISTRICTS_NORD)
TRAME_NORD = {"colonnes": carte.COLONNES, "rangees": RANGEES_NORD, "rues_v": carte.RUES_V,
              "rues_h": RUES_H_NORD, "districts": DISTRICTS_NORD,
              "standing": carte._assembler_le_standing(DISTRICTS_NORD, PLAN_NORD)}


def district(slug: str) -> dict:
    return next(d for d in DISTRICTS_NORD if d["slug"] == slug)
```

Dans `carte.py`, `USAGE_DU_PLAN` gagne `"z": "parc", "b": "commercial", "v": "industriel"`. La ville d'avant
n'en emploie aucune.

- [ ] **Étape 3 : les trois bâtisseurs, et la pièce du poste**

```python
#: Le poste d'aiguillage : des leviers (`m`), le classeur des horaires, la chaise et le poêle.
PIECE_AIGUILLAGE = carte._piece("nord_aiguillage", "Le poste d'aiguillage", porte="commerce", plan="""
BBBWWWWBB
Bmmm   kB
B       B
B h   z B
BBBBDBBBB
""")
POSTE = {"slug": "nord_aiguillage", "nom": "Le poste d'aiguillage", "interieur": "nord_aiguillage",
         "famille": "repere", "genre": "industriel"}


def _friche(ch, x, y, l, h):
    """Herbes hautes, sentiers de terre battue, clôtures percées, carcasses et cabanons — sans un dé du
    chantier : tout se tire à la tuile (`carte.tirage_stable`), la bande a de toute façon sa graine."""
    for j in range(h):
        for i in range(l):
            ch.sol[y + j][x + i] = ","
    for i in range(l):                                   # un sentier est-ouest au milieu
        ch.sol[y + h // 2][x + i] = "s"
    for j in range(h):                                   # et un nord-sud
        ch.sol[y + j][x + l // 3] = "s"
    for j in range(1, h - 1, 7):                         # des bouts de clôture percée
        for i in range(2, l - 2):
            if (i // 5) % 3 == 0 and ch.sol[y + j][x + i] == ",":
                ch.sol[y + j][x + i] = "f"
    libres = [(i, j) for i, j in _semis(x, y, l, h, 60) if ch.sol[j][i] == ","]
    for k, (i, j) in enumerate(libres):
        ch.decor.append({"type": GENRES_FRICHE[k % len(GENRES_FRICHE)], "x": i, "y": j})


GENRES_FRICHE = ("carcasse", "cabanon", "pneu", "debris", "baril", "arbre", "buisson", "caddie", "ordures")


def _terrain_a_batir(ch, x, y, l, h):
    """La palissade autour, du gravier dedans, une barrière au sud et la pancarte « À BÂTIR » devant."""
    for j in range(h):
        for i in range(l):
            bord = j in (0, h - 1) or i in (0, l - 1)
            ch.sol[y + j][x + i] = "w" if bord else "g"
    ch.sol[y + h - 1][x + l // 2] = "g"                  # l'entrée, au sud
    ch.decor.append({"type": "pancarte_a_batir", "x": x + l // 2 + 1, "y": y + h})


def _voies_ferrees(ch, x, y, l, h):
    """Des voies tous les trois rangs, des wagons (un toit de tôle long de six, sur la voie), et le poste
    d'aiguillage au coin sud-ouest."""
    for j in range(h):
        for i in range(l):
            ch.sol[y + j][x + i] = "," if j % 3 else "T"
    for j in range(0, h, 3):
        for i in range(2 + (j * 5) % 11, l - 8, 17):
            for k in range(6):
                ch.sol[y + j][x + i + k] = "B"
    px, py = x + 2, y + h - 5                            # le poste : toit, façade, et sa porte
    for j in range(3):
        for i in range(5):
            ch.sol[py + j][px + i] = "O"
    facades = [(px + i, py + 3) for i in range(5)]
    for fx, fy in facades:
        ch.sol[fy][fx] = "F"
    ch.sol[py + 4][px + 2] = "."
    ch.poser_porte(facades, special=POSTE)


def _semis(x, y, l, h, n):
    """Au plus `n` tuiles réparties dans le rectangle, à la tuile près, sans dé (et sans doublon)."""
    return list(dict.fromkeys((x + 2 + (k * 37) % max(1, l - 4), y + 2 + (k * 23) % max(1, h - 4))
                              for k in range(n)))


class _ChantierNord(carte._Chantier):
    BATISSEURS = {"z": _friche, "b": _terrain_a_batir, "v": _voies_ferrees}
    A_ABORD = carte._Chantier.A_ABORD | {"b"}
```

⚠️ `ch.pieces` doit recevoir `PIECE_AIGUILLAGE` : `poser_porte` pose la porte et le point, pas la pièce. On
l'ajoute dans `batir_la_bande`.

- [ ] **Étape 4 : `batir_la_bande`, et les préfixes**

```python
def batir_la_bande() -> _ChantierNord:
    ch = _ChantierNord(PLAN_NORD, GRAINE_NORD, trame=TRAME_NORD)
    for etape in ("eaux", "rues", "croisements", "ilots", "ponts", "lampadaires", "bornes"):
        getattr(ch, etape)()
    ch.pieces["nord_aiguillage"] = PIECE_AIGUILLAGE
    # ⚠️ LES NOMS DE LA BANDE : `logement_1` existe déjà en ville.
    renomme = {k: (k if k.startswith("nord_") else "nord_" + k) for k in ch.pieces}
    ch.pieces = {renomme[k]: v for k, v in ch.pieces.items()}
    for p in ch.portes:
        p["interieur"] = renomme.get(p["interieur"], p["interieur"])
        p["lieu"] = renomme.get(p["lieu"], p["lieu"])
    return ch
```

La sonde du 26 sept. 2026 a fait tourner ces sept étapes en 0,1 s, sans rien casser.

- [ ] **Étape 5 : les deux décors peints** (`static/js/sprites.js`)
  - `carcasse` : une auto sans roues, rouillée, vue de haut. Elle est solide, donc dans `DECOR_SOLIDE`.
  - `pancarte_a_batir` : un panneau de bois sur deux poteaux, écrit « À BÂTIR » en police pixel.
  - On suit le peintre de `benne` ou de `cabanon` (même signature, même grille de 16 px).

- [ ] **Étape 6 : vert, muté**

Run : `… pytest -q tests/test_nord.py` → PASSE.

Mutations :
- `_voies_ferrees` sans wagons → `test_la_gare…` ;
- le préfixe retiré → `test_tout_ce_que_la_bande_nomme…`.

Commit sous `refs/wip/nord`.

---

#### Tâche 4 : la translation, une clé à la fois

**Fichiers** : `app/nord.py` (`decaler`, `DECALAGES`) ; tests : `tests/test_nord.py`.

**Interfaces** :
- Produit : `nord.decaler(ville: dict, n: int) -> None`. Il décale en place et lève `KeyError` sur une clé
  inconnue. Les `n` rangées du haut du `sol` sont remplies de `M` (inertes) et celles de la `voie` de `.`, en
  attendant la bande. `hauteur += n`, `grille["y0"] = n` et `decalage_nord = n`.

- [ ] **Étape 1 : les juges rouges**

```python
import copy
import pytest
from app import carte, nord

VILLE = carte.generer(nord=False)          # la ville d'avant


def _decalee():
    v = copy.deepcopy(VILLE)
    nord.decaler(v, nord.DECALAGE_NORD)
    return v


def test_une_cle_inconnue_fait_echouer_la_translation():
    v = copy.deepcopy(VILLE)
    v["cle_neuve"] = [{"x": 1, "y": 1}]
    with pytest.raises(KeyError, match="cle_neuve"):
        nord.decaler(v, 1)


def _objets_xy(o, chemin=()):
    """Chaque objet {x, y} de la carte, par son chemin — sauf les pièces (leurs coordonnées sont à elles)."""
    if isinstance(o, dict):
        if isinstance(o.get("x"), int) and isinstance(o.get("y"), int):
            yield chemin, o["y"]
        for k, v in o.items():
            if chemin == () and k in ("interieurs",):
                continue
            yield from _objets_xy(v, chemin + (k,))
    elif isinstance(o, list):
        for i, v in enumerate(o):
            yield from _objets_xy(v, chemin + (i,))


def test_chaque_objet_xy_descend_de_110_tuiles_ou_de_110_x_16_pixels():
    apres = dict(_objets_xy(_decalee()))
    for chemin, y in _objets_xy(VILLE):
        attendu = y + nord.DECALAGE_NORD * (carte.TUILE_PX if chemin[0] == "mouillages" else 1)
        if chemin[:2] == ("relief", "montagnes"):
            attendu = y                                   # les montagnes grandissent vers le haut
        assert apres[chemin] == attendu, chemin


def test_le_sol_de_la_ville_d_avant_est_identique_110_rangees_plus_bas():
    v = _decalee()
    assert v["sol"][nord.DECALAGE_NORD:] == VILLE["sol"] and v["voie"][nord.DECALAGE_NORD:] == VILLE["voie"]
    assert v["hauteur"] == VILLE["hauteur"] + nord.DECALAGE_NORD


def test_les_paires_descendent_aussi():
    v, n = _decalee(), nord.DECALAGE_NORD
    assert v["autobus"]["lignes"][0]["trace"][0][1] == VILLE["autobus"]["lignes"][0]["trace"][0][1] + n
    assert v["tramway"]["arrets"][0][2] == VILLE["tramway"]["arrets"][0][2] + n
    assert v["eboueurs"]["points"][0][2] == VILLE["eboueurs"]["points"][0][2] + n
    assert v["foire_enclos"][0][0] == VILLE["foire_enclos"][0][0] + n
    assert v["montagne_russe"]["voie"][0][1] == VILLE["montagne_russe"]["voie"][0][1] + n * carte.TUILE_PX
    assert v["aeroport"]["axes"][0][1] == VILLE["aeroport"]["axes"][0][1] + n
    assert v["aeroport"]["masque"]["carte_h"] == VILLE["aeroport"]["masque"]["carte_h"] + n
    x, y = next(iter(VILLE["arrets"])).split(",")
    assert f"{x},{int(y) + n}" in v["arrets"]
```

Run → ÉCHEC (`unexpected keyword argument 'nord'`, puis `no attribute 'decaler'`).

Dans `carte.generer`, la signature devient tout de suite `generer(plan=PLAN, graine=GRAINE, nord: bool = True)`.
Le paramètre ne fait rien avant la tâche 5 ; les juges de la translation partent ainsi toujours de la ville
d'avant.

- [ ] **Étape 2 : la table** (`app/nord.py`)

```python
PX = carte.TUILE_PX


def _y(o, n):
    """Tout entier sous une clé `y`, à toute profondeur."""
    if isinstance(o, dict):
        for k, v in o.items():
            if k == "y" and isinstance(v, int):
                o[k] = v + n
            else:
                _y(v, n)
    elif isinstance(o, list):
        for v in o:
            _y(v, n)


def _paires(liste, n, i=1):
    for p in liste or ():
        p[i] += n


def _rien(v, n):
    pass


def _aeroport(a, n):
    _y(a, n)
    a["plan"][1] += n
    for s in a["axes"]:
        s[1] += n
        s[3] += n
    _paires(a["balises"], n)
    _paires(a["peints"], n, 2)
    _paires(a["portes_peintes"], n)
    _paires(a["pont"]["piles"], n)
    a["masque"]["carte_h"] += n


def _chantiers(liste, n):
    _y(liste, n)
    for c in liste:
        if isinstance(c.get("tranchee"), list):
            _paires(c["tranchee"], n)
        for cle in ("signaleur", "conteneur"):
            if c.get(cle):
                c[cle][1] += n
        for ph in c["phases"]:
            _paires(ph["equipe"], n)
            if ph.get("porte"):
                ph["porte"][1] += n
            for m in ph["machines"]:
                if m.get("frappe"):
                    m["frappe"][1] += n


def _autobus(a, n):
    _y(a, n)
    for ligne in a["lignes"]:
        _paires(ligne["trace"], n)                       # `arrets` y est [id, rang] : des indices


def _eboueurs(e, n):
    _paires(e["trace"], n)
    _paires(e["points"], n, 2)                           # [rang, x, y]


def _tramway(t, n):
    _paires(t["trace"], n)
    _paires(t["arrets"], n, 2)                           # [rang, x, y, nom]


def _neige(v, n):
    _paires(v["charrue"]["trace"], n)
    for paires in v["deneigement"]["panneaux"].values():
        _paires(paires, n)


def _traversier(t, n):
    _y(t, n)
    for e in t["escales"]:
        _paires(e["acces"], n)


def _train(t, n):
    _paires(t["voie"], n)
    t["quai"][2] += n                                    # [x0, x1, y]


def _montagne_russe(m, n):
    _paires(m["voie"], n * PX)                           # [x, y, z] en PIXELS
    _paires(m["supports"], n, 2)                         # [rang, x, y]
    _y(m["zone"], n)


def _relief(r, n):
    r["montagnes"]["h"] += n                              # elles montent jusqu'en haut de la bande


DECALAGES = {
    "aeroport": _aeroport, "amarrages": _y, "ambulants": _y, "apparition": _y, "aqueduc": _rien,
    "aqueducs": _y, "arrets": None, "autobus": _autobus, "barrieres": _y, "chantiers": _chantiers,
    "chemins_des_bois": _paires, "decor": _y, "decor_solide": _rien, "devant": _rien, "devantures": _y,
    "districts": _rien, "eboueurs": _eboueurs, "entrave": _rien, "entraves": _y, "fermeture": _rien,
    "fermetures": _y, "feux_pietons": _y, "flottants": _rien, "foire": _y,
    "foire_enclos": lambda v, n: _paires(v, n, 0), "fourriere": _y, "graffitis": _y, "graine": _rien,
    "grille": None, "hauteur": None, "ile": _y, "incendies": _y, "interieurs": _rien, "intersections": _y,
    "jeux_de_foire": _y, "kiosques_de_foire": _y, "lampes": _y, "largeur": _rien, "metro": _y,
    "montagne_russe": _montagne_russe, "mouillages": lambda v, n: _y(v, n * PX), "neige": _neige,
    "nids_de_poule": _y, "nom": _rien, "paquets": _y, "plages": _y, "points_interet": _y, "ponts": _y,
    "portes": _y, "portes_garage": _y, "rampes": _y, "reclames": _y, "relief": _relief, "residences": _y,
    "roue": _y, "scenes": _y, "slug": _rien, "sol": None, "stationnement_du_poste": _y, "toits": _y,
    "train_de_foire": _train, "tramway": _tramway, "traversier": _traversier, "tuile_px": _rien,
    "tuiles_bouchees": _rien, "voie": None, "zones": _y,
}


def decaler(ville: dict, n: int) -> None:
    """Toute la ville descend de `n` rangées. ⚠️ Une clé que la table ne connaît pas LÈVE : une autre session
    qui ajoute une clé à la carte doit dire ici comment elle descend, sinon elle resterait 110 rangées trop haut."""
    inconnues = sorted(set(ville) - set(DECALAGES))
    if inconnues:
        raise KeyError(f"nord.decaler ne sait pas décaler {inconnues} : ajoute-les à nord.DECALAGES")
    for cle, f in DECALAGES.items():
        if f is not None and cle in ville:
            f(ville[cle], n)
    ville["arrets"] = {f"{k.split(',')[0]},{int(k.split(',')[1]) + n}": v for k, v in ville["arrets"].items()}
    ville["sol"][:0] = ["M" * ville["largeur"]] * n
    ville["voie"][:0] = ["." * ville["largeur"]] * n
    ville["hauteur"] += n
    ville["grille"]["y0"] = n
    ville["decalage_nord"] = n
```

⚠️ Avant de fermer la tâche, **lire le module producteur** de chaque clé traitée par `_paires` (`autobus`,
`eboueurs`, `tramway`, `neige`, `traversier`, le petit train et la montagne russe dans `carte.py`, `aeroport`,
`chantiers`). Pour chacune, confirmer tuiles ou pixels, et l'index du y. Une erreur de la table se paie en
silence.

- [ ] **Étape 3 : vert, muté**

Run : `… pytest -q tests/test_nord.py` → PASSE.

Mutations :
- `"decor": _rien` → `test_chaque_objet_xy…` ;
- `_tramway` sans ses arrêts → `test_les_paires…` ;
- une clé retirée de la table → `generer` lève en la nommant.

Commit sous `refs/wip/nord`.

---

#### Tâche 5 : la pose — décaler, coller, coudre

**Fichiers** :
- Modifier : `app/nord.py` (`poser`), `app/carte.py` (l'appel en tout dernier dans `generer`),
  `app/blocs/__init__.py` (les passages ouest/est décalés), `app/definitions.py` (`decalage_nord`),
  `static/js/monde.js` (deux trames)
- Tests : `tests/test_nord.py`, `tests/test_nord_js.py` (neuf)

**Interfaces** :
- Consomme : `batir_la_bande()` (tâche 3) et `decaler()` (tâche 4).
- Produit : `nord.poser(ville) -> None`. Après lui, la carte fait 459 × 414, et `ville["grille_nord"]` a la
  forme de `grille`, avec `y0 = 0`. `ville["districts"]` et `ville["zones"]` gagnent les trois districts de la
  bande, au bout de leurs listes.
- Produit : `blocs.passage_en_ville(bloc) -> dict`, le passage tel qu'il est sur la carte finie.
- Produit : `definitions` → `defs.decalage_nord`.

- [ ] **Étape 1 : les juges rouges**

```python
def test_la_carte_finie_a_la_bande_au_dessus_de_la_ville_d_avant():
    avant = carte.generer(nord=False)
    apres = carte.generer()
    n = nord.DECALAGE_NORD
    assert (apres["largeur"], apres["hauteur"]) == (459, 304 + n)
    couture = {(x, n) for x in nord.colonnes_de_la_couture()}
    for y, ligne in enumerate(avant["sol"]):
        for x, g in enumerate(ligne):
            if (x, y + n) not in couture:
                assert apres["sol"][y + n][x] == g, (x, y + n)


def test_on_roule_de_la_ville_au_canton_et_on_en_revient():
    v = carte.generer()
    def tuiles(slug):
        z = next(z for z in v["zones"] if z["slug"] == slug and not z["gang"])
        return [(x, y) for y in range(z["y"], z["y"] + z["h"]) for x in range(z["x"], z["x"] + z["l"])
                if v["voie"][y][x] != "."]
    def atteint(depart):
        vues, pile = {depart}, [depart]
        while pile:
            for s in carte.suivre_voie(v, *pile.pop()):
                if s not in vues:
                    vues.add(s)
                    pile.append(s)
        return vues
    assert set(tuiles("canton")) & atteint(tuiles("faubourg")[0])
    assert set(tuiles("faubourg")) & atteint(tuiles("canton")[0])
    assert set(tuiles("gare")) & atteint(tuiles("friches")[0])


def test_la_bande_se_marche_depuis_le_terminus():
    v = carte.generer()
    t = next(p for p in v["points_interet"] if p["slug"] == "terminus")
    groupe = next(g for g in carte.composantes_par_terre(v)["ville"] if (t["x"], t["y"]) in g)
    assert (0, 50) in groupe, "le trottoir de ceinture des Friches ne se rejoint pas à pied"
    poste = next(p for p in v["portes"] if p["interieur"] == "nord_aiguillage")
    assert (poste["x"], poste["y"] + 1) in groupe, "le poste d'aiguillage ne se rejoint pas"


def test_les_trois_districts_de_la_bande_et_leurs_zones():
    v = carte.generer()
    assert [d["slug"] for d in v["districts"][-3:]] == ["friches", "canton", "gare"]
    for slug in ("friches", "canton", "gare"):
        z = next(z for z in v["zones"] if z["slug"] == slug)
        assert z["y"] + z["h"] <= nord.DECALAGE_NORD, slug


def test_aucun_nom_de_la_bande_n_entre_en_collision():
    v = carte.generer()
    lieux = [p["lieu"] for p in v["portes"]]
    assert len(lieux) == len(set(lieux))


def test_les_passages_de_blocs_suivent_la_ville():
    from app import blocs
    v = carte.generer()
    for b in blocs.BLOCS:
        assert blocs.erreurs(b, v) == [], b["slug"]
    rang = next(b for b in blocs.pour_le_navigateur() if b["slug"] == "rang")
    assert rang["passage"]["de"] == 171 + nord.DECALAGE_NORD
```

Et `tests/test_nord_js.py` :

```python
def test_le_quartier_se_lit_des_deux_cotes_de_la_couture(banc):
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const n = L.B.defs.decalage_nord;
        return { bande: L.Monde.standingA(10, 10), dessous: L.Monde.standingA(10, n + 10),
                 canton: L.Monde.usageA(140, 20), faubourg: L.Monde.usageA(140, n + 20) };
    }""")
    assert r["bande"] == "pauvre" and r["dessous"] == "cossu", r
    assert r["canton"] == "commercial", r
```

Run → ÉCHEC (`unexpected keyword argument 'nord'`).

- [ ] **Étape 2 : `poser`**

```python
def colonnes_de_la_couture() -> list[int]:
    """Les x où une rue nord-sud de la bande débouche sur le boulevard de la couture."""
    ch = _bande()
    return [x for x in range(ch.largeur) if ch.voie[DECALAGE_NORD - 1][x] != "."]


_CACHE: dict = {}


def _bande():
    if "bande" not in _CACHE:
        _CACHE["bande"] = batir_la_bande()
    return _CACHE["bande"]


def poser(ville: dict) -> None:
    n, ch = DECALAGE_NORD, _bande()
    decaler(ville, n)
    est = ville["sol"][n][ch.largeur:]                    # la falaise et les montagnes de l'est
    for y in range(n):
        ville["sol"][y] = "".join(ch.sol[y]) + est
        ville["voie"][y] = "".join(ch.voie[y]) + "." * len(est)
    # LA COUTURE : là où une rue de la bande débouche, le trottoir nord du boulevard s'ouvre comme un
    # croisement — la rangée 110 de la bande, qui l'a bâti ouvert.
    for x in colonnes_de_la_couture():
        for cle, grille in (("sol", ch.sol), ("voie", ch.voie)):
            ligne = ville[cle][n]
            ville[cle][n] = ligne[:x] + grille[n][x] + ligne[x + 1:]
    for inter in ville["intersections"]:
        if inter["y"] == n and any(inter["x"] <= x < inter["x"] + inter["l"] for x in colonnes_de_la_couture()):
            inter["bras"] = "".join(sorted(set(inter["bras"]) | {"N"}, key="NSOE".index))
    haut = lambda o: o["y"] < n
    for cle, source in (("portes", ch.portes), ("decor", ch.decor), ("lampes", ch.lampes),
                        ("residences", ch.residences), ("devantures", ch.devantures), ("toits", ch.toits),
                        ("points_interet", ch.points), ("intersections", ch.intersections),
                        ("feux_pietons", ch.feux_pietons())):
        ville[cle].extend(o for o in source if haut(o))
    ville["arrets"].update({k: v for k, v in ch.arrets.items() if int(k.split(",")[1]) < n})
    ville["interieurs"].update(ch.pieces)
    slugs = {d["slug"] for d in DISTRICTS_NORD}
    ville["zones"].extend({**z, "h": min(z["h"], n - z["y"])} for z in ch.zones() if z["district"] in slugs)
    ville["districts"].extend({"slug": d["slug"], "nom": d["nom"], "gang": d["gang"], "eau": False}
                              for d in DISTRICTS_NORD)
    ville["grille_nord"] = {"colonnes": list(carte.COLONNES), "rangees": list(RANGEES_NORD),
                            "rues_v": list(carte.RUES_V), "rues_h": list(RUES_H_NORD),
                            "trottoir": carte.TROTTOIR, "standing": list(ch.standing),
                            "usage": list(ch.usage), "y0": 0}
```

⚠️ Pour chaque attribut lu sur `ch` (`residences`, `devantures`, `toits`, `lampes`, `arrets`), vérifier
dans `generer` d'où la ville le tire. Si c'est une méthode ou un autre nom, le prendre pareil.

Ajouter `"grille_nord": _rien` et `"decalage_nord": _rien` à `DECALAGES`, puisque la carte finie les porte.

Dans `carte.generer` (qui a déjà le paramètre `nord` depuis la tâche 4), la toute dernière instruction,
après `ouvrir_les_rues(ville)` :

```python
    # ⚠️ LA VILLE S'AGRANDIT AU NORD (docs/jalons/la-ville-s-agrandit-au-nord.md), APRÈS ABSOLUMENT TOUT :
    # elle descend de 110 rangées, et la bande (les Friches, le Petit-Canton, la Gare) se colle au-dessus.
    # Sa graine est à elle ; la ville d'avant est la même à la tuile près. `nord=False` : la ville d'avant.
    if nord and plan == PLAN:
        from . import nord as nord_mod
        nord_mod.poser(ville)
```

- [ ] **Étape 3 : les passages de blocs et le paquet**

Dans `app/blocs/__init__.py` :

```python
def passage_en_ville(bloc: dict) -> dict:
    """Le passage sur la carte FINIE : un bord ouest ou est descend avec la ville (`nord.DECALAGE_NORD`)."""
    from .. import nord
    p = dict(bloc["passage"])
    if p["bord"] in ("ouest", "est"):
        p["de"] += nord.DECALAGE_NORD
    return p
```

`pour_le_navigateur` et `erreurs` (la partie `ville`) lisent `passage_en_ville(b)` au lieu de
`b["passage"]`. Dans `tests/test_rang.py` (tâche 1), les rangées de l'ouverture se lisent désormais par
`blocs.passage_en_ville(rang.BLOC)` et `carte.OUVERTURES_DE_RUE` plus `nord.DECALAGE_NORD`. Dans `definitions.py`, à côté de `"blocs"` : `"decalage_nord": nord.DECALAGE_NORD`.

- [ ] **Étape 4 : deux trames au navigateur** (`static/js/monde.js`)

```js
  function quartiersDe(g, zonage) {
    return g && g.standing ? {
      standing: g.standing, usage: g.usage || null, oy: g.y0 || 0,
      usages: Object.keys(zonage || {}).reduce(function (m, slug) { m[zonage[slug].lettre] = slug; return m; }, {}),
      x: coupes(g.colonnes, g.rues_v), y: coupes(g.rangees, g.rues_h),
      w: somme(g.colonnes) + somme(g.rues_v), h: somme(g.rangees) + somme(g.rues_h),
    } : null;
  }
```

`quartiers: quartiersDe(def.grille, def.zonage)` et `quartiersNord: quartiersDe(def.grille_nord, def.zonage)`.
Puis `lettreDuBloc` :

```js
  function lettreDuBloc(nom, tx, ty, laquelle) {
    const k = laquelle || carte;
    // ⚠️ DEUX TRAMES : la bande nord (0 .. y0) a la sienne, la ville d'avant commence à `y0`.
    const q = k && k.quartiers && ty < k.quartiers.oy ? k.quartiersNord : k && k.quartiers;
    if (!q || !q[nom]) return null;
    const ly = ty - q.oy;
    if (tx < 0 || ly < 0 || tx >= Math.min(k.w, q.w) || ly >= q.h || ty >= k.h) return null;
    return q[nom][rang(q.y, ly)][rang(q.x, tx)];
  }
```

`usageA` lit `k.quartiers.usages` : le remplacer par `(q && q.usages)` via la même règle, ou lire
`quartiersNord.usages`, qui est la même table.

- [ ] **Étape 5 : vert, muté**

Run : `… pytest -q tests/test_nord.py tests/test_nord_js.py tests/test_blocs.py tests/test_districts.py tests/test_definitions.py` → PASSE.

Mutations :
- la couture sans `"N"` → `test_on_roule…` ;
- `lettreDuBloc` sans `quartiersNord` → `test_le_quartier…` ;
- `passage_en_ville` sans décalage → `test_les_passages…`.

Commit sous `refs/wip/nord`.

---

#### Tâche 6 : la vieille partie, les juges en dur, la doc, et livrer

**Fichiers** : `static/js/base.js` (`Sauvegarde.completer`), les tests qui avaient des y en dur, `docs/carte.md`,
`docs/architecture.md`, la fiche (Notes), `docs/plan.md`, `docs/jalons/README.md`, `tests/test_nord_js.py`.

- [ ] **Étape 1 : le juge de la vieille partie, rouge** (`tests/test_nord_js.py`)

```python
def test_une_vieille_partie_descend_avec_la_ville(banc):
    r = banc("""function (L, o) {
        const n = L.B.defs.decalage_nord, TT = 16;
        const p = L.Sauvegarde.completer({ x: 100, y: 200, planque: { vehicule: { slug: 'pickup', x: 5, y: 6 } },
            skimmers: [{ cle: '12,34', x: 200, y: 552, jour: 1, monte: 0, pret: false }] }, L.B.defs);
        return { y: p.y, vy: p.planque.vehicule.y, cle: p.skimmers[0].cle, sy: p.skimmers[0].y,
                 d: p.decalage_nord, n: n, encore: L.Sauvegarde.completer(p, L.B.defs).y };
    }""")
    n = r["n"]
    assert r["y"] == 200 + n * 16 and r["vy"] == 6 + n * 16, r
    assert r["cle"] == f"12,{34 + n}" and r["sy"] == 552 + n * 16, r
    assert r["d"] == n and r["encore"] == r["y"], "une partie déjà décalée ne redescend pas"
```

- [ ] **Étape 2 : la migration** (`Sauvegarde.completer`, après la migration du rang)

```js
    // ⚠️ LA VILLE S'AGRANDIT AU NORD : une partie écrite avant descend avec elle. Ce qu'elle garde en
    // coordonnées de la VILLE : sa position, le char de la planque de Rocco, ses skimmers. Les chars des
    // planques de blocs et `bloc.x/y` sont en coordonnées du bloc : ils ne bougent pas.
    const dn = (defs.decalage_nord || 0) - (out.decalage_nord || 0);
    if (dn) {
      const px = dn * 16;
      if (typeof out.y === 'number') out.y += px;
      const v = out.planque && out.planque.vehicule;
      if (v && typeof v.y === 'number') v.y += px;
      (out.skimmers || []).forEach(function (s) {
        if (typeof s.y === 'number') s.y += px;
        const c = String(s.cle).split(',');
        if (c.length === 2) s.cle = c[0] + ',' + (Number(c[1]) + dn);
      });
    }
    out.decalage_nord = defs.decalage_nord || 0;
```

Ajouter `decalage_nord: 0` à la partie par défaut. Run → PASSE ; mutation : sans `dn` → rouge.

- [ ] **Étape 3 : les juges qui avaient des y en dur**

Lancer la suite par le lanceur parallèle. Pour chaque rouge, décider :
- **Une coordonnée en dur** (on le sait en la lisant : `test_chalet_js`, `test_districts_js`,
  `test_moteur_js:1305`, `test_blocs_js`, et la douzaine de lignes qu'on y trouvera) : la lire sur la carte, ou
  y ajouter `nord.DECALAGE_NORD` / `L.B.defs.decalage_nord`. Écrire pourquoi dans le test.
- **Un juge « hauteur = trame »** ou « un seul district au nord » (`test_carte`, `test_districts`,
  `test_trottoir`, `composantes_par_terre`) : il compare la ville d'avant. Il appelle `generer(nord=False)`,
  ou il apprend la bande, selon ce qu'il juge. Les deux sont écrits.
- **Autre chose** : un vrai défaut. `superpowers:systematic-debugging`, et le rejouer sans `-x` sur la base
  (« Un rouge est-il de moi ? »).

- [ ] **Étape 4 : mesurer**
  - Le temps de `generer`, avant et après (2,8 s aujourd'hui).
  - Le poids de `/api/carte` en gzip, avant et après.
  - `test_definitions` (le plafond de 54 000).
  - Tout va dans les Notes.

- [ ] **Étape 5 : captures pour Martin**
  - La bande entière (0 à 110, en réduction).
  - La couture au Faubourg, x 110 à 160, y 95 à 125.
  - Les Friches, la Gare avec son poste, un terrain à bâtir et sa pancarte.
  - Tout dans `captures/`, ouvert dans Aperçu.

- [ ] **Étape 6 : la doc**
  - `docs/carte.md` : la bande, `nord.py`, `DECALAGE_NORD`, et la règle « une clé neuve dans la carte =
    une ligne dans `nord.DECALAGES` ».
  - `docs/architecture.md` : `app/nord.py` et `app/blocs/rang.py`, et les trois blocs retirés.
  - La fiche : les Notes (livré, ce qui a surpris, les dettes).
  - `docs/plan.md` : la ligne quitte la table pour `docs/jalons/README.md`. La ligne du Petit-Canton dit
    « étape 2 sur 4 ».

- [ ] **Étape 7 : relecture de toute la branche, puis livrer**
  - Un relecteur neuf, sur le modèle le plus capable, avec la liste « À surveiller en relecture ».
  - Une passe de corrections, chacune rouge puis verte.
  - `ruff`, verts ciblés, atterrir (`merge --squash` depuis `refs/wip/nord`, puis `--ff-only`), sans pousser.
  - La suite complète après.

## Notes

**Livré le 27 sept. 2026** — en deux temps : le rang et le ciné-parc d'abord (tâche 1), puis la bande (tâches 2 à 6),
avec une relecture neuve de toute la branche et une passe de corrections.

- **Le rang** (`app/blocs/rang.py`) : le chalet au bord du lac de l'ancienne clairière, la cabane à sucre en face,
  un chemin de gravier ; on y entre par la rue des Quais, qui traverse jusqu'au bord ouest
  (`carte.OUVERTURES_DE_RUE`). Le **ciné-parc** est au bord ouest des Érables, entré par son côté est. Une vieille
  partie retrouve sa planque au rang.
- **La bande nord** (`app/nord.py`) : la carte fait 459 × 414. Toute la ville descend de 110 rangées ; une deuxième
  ville, bâtie par le même chantier sur sa trame et sa graine, se colle au-dessus — **les Friches** (herbes hautes,
  sentiers de gravier, terrains vagues, carcasses), **la place du Petit-Canton** (ses rues, et 56 terrains à bâtir
  derrière leur grillage, pancarte « À BÂTIR »), **la Gare de triage** (voies, wagons, hangars de tôle et le **poste
  d'aiguillage**, sa seule pièce). Les croisements de la couture s'ouvrent au nord ; on y roule et on y marche.
- **Mesures** : `generer` 1,58 s → 1,64 s ; la carte 53 → 64 Ko gzip (682 Ko bruts) — le plafond est relevé, comme
  pour l'aéroport (`test_definitions`) — **confirmé par Martin** le 27 sept. 2026.

⚠️ **Ce qui a surpris** :
- **Le scratchpad s'est vidé** en pleine exécution : un `cd` raté a fait un `checkout --detach dev` dans l'arbre
  partagé (même commit, arbre propre), remis aussitôt.
- Une **moto lancée** dans la rue du rang heurtait le bord et **éjectait son pilote** avant le passage :
  `Blocs.marge` anticipe maintenant d'une image de route.
- **La ville partage des objets** entre ses listes (les amarrages de l'île) : décalés deux fois sans un registre.
- **« Python n'a pas besoin de deux trames » était faux** : les juges qui lisent le quartier d'une tuile de la
  carte finie en ont besoin — `nord.LECTEUR`.
- Les juges de la ville (les clôtures qui tournent, la pièce à la mesure de son bâtiment, rien devant une porte,
  pas de terre sèche dans un parc) ont trouvé **six défauts de la bande** ; la relecture, **un faux pont** (la
  globale `PONTS`, indexée sur la trame de la ville, peignait onze rangées de quai dans la gare), **dix commerces
  dans la gare** (une clinique, une disco) et un plantage pour d'autres graines.
- **Les numéros d'entités** : chaque décor et chaque poteau créés au démarrage prennent un numéro pour toujours, et
  tout ce qui se tire au numéro suit. La bande prend les siens dans une plage à part, et la couture saute ceux de
  ses anciens panneaux d'arrêt : la ville d'avant garde sa suite à l'unité près.
- **Le hasard du démarrage change forcément** : on naît aussi au-dessus du terminus maintenant. Les juges du banc
  qui tenaient par ce tirage fixent ce qu'ils jugent (l'archétype, la graine, l'intouchable).

**Dettes** :
- ~~La **course de motoneige** ne se gagne, par le pilote du juge, qu'**une graine sur huit** — sur la base aussi.~~
  Réglée le 1er oct. 2026 : c'était le pilote (une cible recalculée toutes les 20 images, qu'il dépassait) ;
  il suit sa place sur la route, 24 graines sur 24, sans `L.graine`.
- Les **phares du camion-benne et du camion-citerne** se voient quand ils montent l'écran (un `xfail` le tient) :
  un défaut d'avant, mis au jour par le nouveau hasard.
- Les croisements de la couture n'ont pas de **feux piétons** (leurs feux de chars, oui).
- Mineures : `nord._VUS` est un registre de module ; `Sauvegarde.completer` modifie la partie qu'on lui donne ;
  les clés de `partie.fouilles` (« rue:tx,ty ») ne descendent pas (elles ne durent qu'une journée).

**À regarder** (captures dans `captures/`) : le rang, son ouverture de rue, l'entrée du ciné-parc, la bande.
