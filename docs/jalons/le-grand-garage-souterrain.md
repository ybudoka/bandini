# Le grand garage souterrain

← [les jalons livrés](README.md) · [le plan](../plan.md)

## Fiche

Martin, 30 sept. 2026 : « le garage Bandini doit pouvoir stocker des véhicules que nous pourrons reprendre après
dans un grand garage souterrain ». Tranché avec lui, question par question : on **descend en char** dans un vrai
sous-sol (pas un simple menu) ; il s'ouvre **quand on possède le garage** ; **deux niveaux de dix cases**, le
deuxième à acheter **10 000 $** ; un char volé **reste volé** et on ne descend pas avec des étoiles ; on entre
**par le rideau** du Garage Rocco Bandini, et **à pied par un ascenseur** dans la pièce du garage.

### Ce qui existe

- **Le Garage Rocco Bandini** (`SPECIAUX["G"]`, `app/carte.py`) : une propriété à 4 500 $ (`app/economie.py`,
  `p.proprietes.garage`), un rideau où l'on entre au volant (`missions.js` `majGarage`/`majAtelier`, phases
  `baisse → menu → leve → sortie`, REPARTIR en tête du menu), et une pièce à pied de 10 × 7 avec le commis
  (`carte.py`, l'intérieur `garage`).
- **Aucun parc de chars.** Seulement des places à un char : `planque.vehicule`, `charsDesPlanques`, la fourrière
  (`p.fourriere`, six places). La ville **oublie** un char garé loin (`Vehicules.peupler` retire tout char hors de
  la bulle, `aToi` compris) : un stockage doit vivre **en données**, pas en entités.
- **La fiche d'un char sauvegardé** : `{ slug, sprite, couleur, vie, vole, aToi, mods }`, recréée par
  `recreerLeChar` (`jeu.js`) et `Garage.poser`. La fourrière fait déjà « données → chars sur des places »
  (`garnirLaFourriere`), sans dé.
- **Un char ne roule jamais dans une pièce**, seulement dans un **bloc** (`B.bloc`, `Jeu.passerDansLeBloc`). La
  villa (`app/blocs/villa.py`) est un bloc à plusieurs niveaux, un `CADRE` par niveau, reliés par des escaliers
  **à pied seulement**.

### Ce que ça donne

**Le lieu : le bloc `souterrain`**, dessiné à la main, **sans un dé** (`app/blocs/souterrain.py`). Deux cadres,
chacun plus grand que l'écran (30 × 17) :

- **Niveau −1** : la rampe vers la rue, une allée, **dix cases numérotées P1 à P10** peintes au sol, l'ascenseur,
  des piliers, des néons.
- **Niveau −2** : la rampe intérieure qui monte au −1, dix cases **P11 à P20**, l'ascenseur. **Une grille** ferme
  la rampe tant qu'il n'est pas acheté (une barrière du bloc, sa condition lue dans la partie).

**Entrer et sortir :**

- **En char** : sous le rideau du Garage Bandini, le menu gagne **DESCENDRE AU SOUS-SOL** (REPARTIR reste en tête).
  Au noir, on est au bas de la rampe du −1, au volant (`Blocs.sauter`). Refusé, avec sa raison à l'écran : garage
  pas acheté, une étoile ou plus, un char de mission, un bateau, une remorque, ou **plus aucune case libre**
  (« SOUS-SOL PLEIN — 10/10 »).
- **À pied** : un **ascenseur** dans la pièce du garage (un point, comme un escalier). Au noir, on arrive devant
  l'ascenseur du −1. En bas, l'ascenseur remonte à la pièce du garage, et dessert les deux niveaux.
- **Entre les niveaux, au volant** : la rampe intérieure se franchit **en char** — c'est neuf (les escaliers de la
  villa sont à pied) : le char et son conducteur passent au noir d'un cadre à l'autre, cap conservé.
- **Ressortir** : monter la rampe du −1 au volant. On réapparaît **devant le rideau du Garage Bandini**, le nez vers
  la rue — pas au passage d'un bord de carte comme les autres blocs (le retour se pose à la main).

**La mémoire : `p.souterrain`**, dans la partie :

```js
souterrain: { niveaux: 1, cases: [ /* 20 × (null | { slug, sprite, couleur, vie, vole, aToi, mods }) */ ] }
```

- **Ranger** : un char immobile sur une case y est écrit **quand on quitte le sous-sol** (rampe ou ascenseur) et à
  chaque sauvegarde. Un char laissé dans l'allée est **garé par Ti-Guy** sur la première case libre ouverte.
- **Le plein ne se dépasse jamais** : la descente en char est refusée quand toutes les cases ouvertes sont prises,
  donc il y a toujours au plus autant de chars en bas que de cases. À pied, on descend toujours.
- **Reprendre** : à chaque descente, les chars rangés sont **recréés sur leur case**, couleur donnée (aucun dé),
  comme la fourrière. Monter la rampe au volant de l'un d'eux le **retire** de la liste : il redevient un char de
  la ville.
- **Un char volé reste volé** : le sous-sol cache, il ne lave pas — REPEINDRE reste le seul blanchiment.
- **Ni passant, ni trafic, ni police** en bas.
- **Recharger** ne perd rien : les cases sont des données, pas des positions en ville. Environ 3 Ko pour vingt chars,
  loin des 48 Ko d'une partie.

**Agrandir** : le comptoir du commis gagne **AGRANDIR LE SOUS-SOL — 10 000 $** (seulement si le garage est à toi et
le −2 pas encore ouvert). La grille du −2 s'ouvre.

**Le son** (ElevenLabs) : le ding et le moteur de l'ascenseur, les pneus qui crissent en écho sur le béton de la
rampe, le bourdonnement des néons.

### Deux vagues

1. **Le −1** : le bloc et son cadre, DESCENDRE AU SOUS-SOL au rideau, la rampe de sortie devant le garage,
   l'ascenseur dans les deux sens, `p.souterrain` (ranger, reprendre, Ti-Guy qui gare, le plein, recharger).
2. **Le −2** : la rampe intérieure au volant, la grille, AGRANDIR LE SOUS-SOL, et les sons.

### Ce qui guette

- ⚠️ **La ville ne doit pas bouger** : aucune tuile neuve dans la rue. Seul un point `ascenseur` s'ajoute dans la
  pièce du garage — une pièce du catalogue, pas la ville ; les juges « ce module ne déplace rien » le confirment.
- ⚠️ **`Vehicules.creer` sans couleur tire un dé** : chaque char recréé reçoit la sienne.
- ⚠️ **`Sauvegarde.completer`** initialise `souterrain` (les vieilles parties n'en ont pas), et la migration de la
  bande nord ne touche pas les cases (pas de `x`/`y` dedans).
- ⚠️ **Le retour d'un bloc** se fait par défaut à son `passage`, sur un bord de la carte : ici il se pose devant le
  rideau, cap vers la rue, et le rideau ne doit pas se rouvrir aussitôt (il faut relâcher puis réappuyer).
- ⚠️ **Une sauvegarde prise en bas** : la partie se réveille dans le bloc (`partie.bloc`, comme au chalet), ou devant
  le garage si la carte du bloc n'arrive pas — jamais un char perdu.
- ⚠️ **La rampe intérieure au volant** : l'arrivée est un refuge, le cap est gardé, et un char trop long (l'autobus,
  une remorque) n'y passe pas — la remorque est déjà refusée à la descente.
- ⚠️ **Le poids du paquet** : le bloc voyage à part (`/api/blocs/<slug>`), mais un son neuf va dans `audio.LIEUX`
  (plafond du premier écran plein) ; `test_definitions` dans les juges ciblés.

### Les juges

- Python : deux cadres plus grands que l'écran, vingt cases, la grille sur la rampe du −2, les arrivées (rampe,
  ascenseur) en refuge, `erreurs(bloc)` vide, la ville identique avec et sans le jalon.
- JS au banc, **au bouton** : ranger un char, recharger la partie, le reprendre (couleur, modifs, vie) ; le refus au
  plein, avec des étoiles, pour un char de mission et pour un bateau ; l'ascenseur dans les deux sens ; un char
  laissé dans l'allée rangé par Ti-Guy ; un char volé toujours volé en ressortant ; l'achat du −2 ouvre la grille ;
  la rampe intérieure au volant.
- Chaque juge vu rougir, sa règle retirée ; une capture Chromium du −1 et du −2 avant de livrer.

## Plan de la vague 1

> Écrit avec superpowers:writing-plans (30 sept. 2026). **Pour l'exécutant :** suivre les tâches dans l'ordre,
> test d'abord ; les cases `- [ ]` se cochent au fil du travail.

**But :** on descend au volant par le rideau du Garage Rocco Bandini (ou à pied par un ascenseur) dans un sous-sol
de dix cases ; les chars qu'on y laisse sont écrits dans la partie et y reviennent, recharge comprise.

**Architecture :** un bloc de carte **sans passage en ville** (`app/blocs/souterrain.py`, rangé dans
`blocs.SOUS_SOLS`, pas dans `BLOCS`) : on y entre par `Blocs.sauter`, et le retour se pose devant le rideau
(`Blocs.retourEnVille`, qui lit le `seuil` du bloc). Les chars rangés vivent dans `partie.souterrain.cases` ;
`Souterrain.garnir` les recrée à chaque descente, `Souterrain.ranger` les réécrit en remontant et à chaque
sauvegarde — la mémoire des blocs (`Blocs.garder`) n'en garde jamais un seul.

**Technique :** JavaScript sans module (des IIFE chargées par `templates/index.html`), Python 3 / Flask pour la
carte du bloc, pytest et le banc Node (`tests/banc.js`, fixture `banc`).

**Fiche :** la section « Fiche » ci-dessus ; l'exécutant lit les deux.

### Contraintes de tout le jalon

- Tout se fait dans le worktree `claude/garage-souterrain` ; l'arbre partagé ne sert qu'à atterrir (`merge --ff-only`).
- `git add` et `git commit` en **deux commandes** (le crochet des tables juge l'index d'avant) ; jamais `git add -A`.
- Les juges se lancent depuis le worktree avec le `.venv` du dépôt principal :
  `/Users/martingagne/dev/bandini/.venv/bin/python -m pytest <fichiers> -q`.
  Plus bas, `…pytest` et `…python` abrègent `/Users/martingagne/dev/bandini/.venv/bin/python -m pytest` et
  `/Users/martingagne/dev/bandini/.venv/bin/python`.
- **Aucun dé** : chaque char recréé reçoit sa couleur à `Vehicules.creer` (`{ couleur: … }`), sinon le hasard glisse.
- **La ville ne bouge pas** : aucune tuile neuve en ville ; seul le point `ascenseur` s'ajoute dans la pièce du garage.
- Libellés en majuscules, accents compris (« DESCENDRE AU SOUS-SOL », « SOUS-SOL PLEIN — 10/10 »).
- Constantes : **10 cases par niveau** (`PAR_NIVEAU`), **20 cases au plus** (`CASES_MAX`), un seul niveau à la
  vague 1 (`niveaux: 1`).
- Chaque juge neuf est vu rougir, sa règle retirée (vider `__pycache__` après une mutation Python).
- `uv run ruff check .` avant d'atterrir.

### Ce que les juges doivent aussi couvrir

1. **Une partie sauvegardée au sous-sol se rouvre au sous-sol**, les chars sur leurs cases, le char qu'on conduisait
   compris (garé par Ti-Guy) — juge de la tâche 4.
2. **La sortie devant le rideau tombe sur la chaussée**, pas dans la façade ni dans le trottoir d'en face — juges des
   tâches 1 et 3.
3. **Un char rangé revient sans tirer un dé** : le hasard de la partie est le même, qu'on ait garni ou non — juge de
   la tâche 4.
4. **Pendant le fondu de la descente, le rideau ne remonte pas et le menu ne se rouvre pas** — juge de la tâche 5.
5. **Au sous-sol, ni pluie ni neige, et pas de nuit** — juge de la tâche 7.

---

### Tâche 1 : le bloc `souterrain`, en Python

**Fichiers :**
- Créer : `app/blocs/souterrain.py`
- Modifier : `app/blocs/__init__.py` (`SOUS_SOLS`, `par_slug`, `carte_du_bloc`, `pour_le_navigateur`, `erreurs`)
- Modifier : `app/definitions.py:324` (les cartes des sous-sols servies comme celles des blocs)
- Modifier : `tests/test_blocs.py` (`test_un_bloc_ne_change_pas_un_octet_de_la_ville`, `test_le_paquet_nomme_les_passages_et_pas_les_cartes`)
- Créer : `tests/test_souterrain.py`

**Interfaces :**
- Produit : `souterrain.BLOC` (slug `"souterrain"`, `passage: None`, `seuil: "garage"`, `retour` au nord, `abrite: True`) ;
  `souterrain.CASES` (dix `{"n", "x", "y", "l", "h", "cap"}`, en tuiles) ; `souterrain.ASCENSEUR` (`{"x", "y", "l"}`,
  la rangée devant ses portes) ; `souterrain.PAR_NIVEAU = 10`, `souterrain.CASES_MAX = 20`.
- Produit, dans la carte du bloc : `carte["bloc"]["abrite"]` (bool) et `carte["bloc"]["souterrain"]`
  (`{"cases": [...], "ascenseur": {...}}`).
- Produit, dans le paquet : une entrée `{"slug": "souterrain", "nom", "passage": None, "seuil": "garage", "panneau", "portes": []}`
  à la fin de `paquet["blocs"]`.

- [ ] **Étape 1 : écrire le juge qui échoue** — `tests/test_souterrain.py` :

```python
"""Le grand garage souterrain, en Python (docs/jalons/le-grand-garage-souterrain.md) : le bloc tient debout, ses dix
cases sont peintes et se rejoignent, sa rampe et son ascenseur sont où la fiche le dit, le paquet le nomme sans
passage, et la sortie devant le rideau de Ti-Guy tombe sur la chaussée."""

from app import blocs, carte
from app.blocs import souterrain
from tests import villes


def test_le_souterrain_tient_debout():
    assert blocs.erreurs(souterrain.BLOC) == []


def test_il_n_est_pas_un_bloc_de_bord_de_ville():
    """⚠️ Pas dans `BLOCS` : les juges des blocs y exigent un passage sur un bord de la ville."""
    assert souterrain.BLOC not in blocs.BLOCS and souterrain.BLOC in blocs.SOUS_SOLS
    assert blocs.par_slug("souterrain") is souterrain.BLOC
    assert souterrain.BLOC["passage"] is None and souterrain.BLOC["seuil"] == "garage"


def test_dix_cases_peintes_qui_ne_se_chevauchent_pas_et_se_rejoignent():
    plan, cases = souterrain.PLAN, souterrain.CASES
    assert len(cases) == souterrain.PAR_NIVEAU == 10
    assert [c["n"] for c in cases] == list(range(1, 11))
    vues: set[tuple[int, int]] = set()
    a_pied = blocs.a_pied_depuis_l_arrivee(souterrain.BLOC)
    for c in cases:
        tuiles = {(c["x"] + i, c["y"] + j) for i in range(c["l"]) for j in range(c["h"])}
        assert all(plan[y][x] == "^" for x, y in tuiles), f"la case P{c['n']} n'est pas peinte"
        assert not tuiles & vues, f"la case P{c['n']} en chevauche une autre"
        assert tuiles <= a_pied, f"on ne rejoint pas la case P{c['n']}"
        vues |= tuiles


def test_la_rampe_au_nord_et_l_arrivee_au_bas_de_la_rampe():
    r, a = souterrain.BLOC["retour"], souterrain.BLOC["arrivee"]
    assert r["bord"] == "nord"
    assert r["de"] <= a["x"] < r["de"] + r["l"], "on arrive dans l'axe de la rampe"
    assert 2 <= a["y"] <= 5, "au bas de la rampe, pas dessus ni au milieu de l'allée"


def test_l_ascenseur_est_devant_ses_portes():
    s = souterrain.ASCENSEUR
    a_pied = blocs.a_pied_depuis_l_arrivee(souterrain.BLOC)
    for i in range(s["l"]):
        assert souterrain.PLAN[s["y"] + 1][s["x"] + i] == "D", "les portes de l'ascenseur, sous la rangée où l'on attend"
        assert (s["x"] + i, s["y"]) in a_pied


def test_la_carte_du_bloc_porte_ses_cases_et_son_abri():
    c = blocs.carte_du_bloc(souterrain.BLOC)
    assert c["bloc"]["abrite"] is True
    assert len(c["bloc"]["souterrain"]["cases"]) == 10 and c["bloc"]["souterrain"]["ascenseur"] == souterrain.ASCENSEUR
    assert blocs.carte_du_bloc(blocs.par_slug("rang"))["bloc"]["abrite"] is False


def test_le_paquet_nomme_le_sous_sol_sans_passage(paquet):
    b = next(b for b in paquet["blocs"] if b["slug"] == "souterrain")
    assert b["passage"] is None and b["seuil"] == "garage" and b["portes"] == []


def test_la_sortie_devant_le_rideau_tombe_sur_la_chaussee():
    """La sortie (`Blocs.retourEnVille`) : quatre tuiles devant la façade du rideau de Ti-Guy, au milieu de sa
    largeur — la chaussée, et rien de solide sur la longueur d'un char (une tuile de chaque côté)."""
    ville = villes.exporter()
    pg = next(p for p in ville["portes_garage"] if p["lieu"] == "garage")
    x, y = pg["x"] + pg["l"] // 2, pg["y"] + 4
    assert carte.LEGENDE[ville["sol"][y][x]].get("route"), ville["sol"][y][x]
    for dy in (-1, 0, 1):
        assert carte.LEGENDE[ville["sol"][y + dy][x]].get("solide", 0) == 0
```

- [ ] **Étape 2 : le lancer, le voir rougir**

Run: `/Users/martingagne/dev/bandini/.venv/bin/python -m pytest tests/test_souterrain.py -q`
Expected: FAIL — `ImportError: cannot import name 'souterrain'`.

- [ ] **Étape 3 : écrire le bloc** — `app/blocs/souterrain.py` :

```python
"""Le grand garage souterrain, sous le Garage Rocco Bandini (docs/jalons/le-grand-garage-souterrain.md).

Martin, 30 sept. 2026 : « le garage Bandini doit pouvoir stocker des véhicules que nous pourrons reprendre après
dans un grand garage souterrain ». On y descend au volant par le rideau de Ti-Guy (DESCENDRE AU SOUS-SOL), ou à pied
par l'ascenseur de la pièce du garage ; on y gare son char sur une case, et il y est encore au retour.

⚠️ **UN BLOC SANS PASSAGE EN VILLE** : il n'est pas au bout d'une rue, il est SOUS le garage. Il vit dans
`blocs.SOUS_SOLS`, pas dans `blocs.BLOCS` (dont les juges exigent un passage sur un bord de la ville) ; son `seuil`
dit devant quel rideau on ressort (`Blocs.retourEnVille`).

⚠️ **LES CHARS NE SONT PAS DANS LE PLAN** : ils vivent dans la partie (`partie.souterrain.cases`), et le navigateur
les pose sur les cases à chaque descente (`static/js/souterrain.js`). Le plan ne porte que le béton.
"""

import math

#: Les cases d'un niveau, et de tout le sous-sol (le −2 est la vague 2).
PAR_NIVEAU = 10
CASES_MAX = 20

#: Le −1 : la rampe au nord (14 à 16), dix cases contre le mur nord (le nez au mur), l'allée, deux piliers, et
#: l'ascenseur au milieu du mur sud (ses portes, les deux `D`). `B` : du béton peint (`materiaux`, comme les murs
#: d'une pièce). 32 × 18 : plus grand que l'écran (30 × 17), la caméra n'y voit jamais le vide.
PLAN: tuple[str, ...] = (
    "BBBBBBBBBBBBBB###BBBBBBBBBBBBBBB",
    "BBBBBBBBBBBBBB###BBBBBBBBBBBBBBB",
    "B#^^^^^^^^^^######^^^^^^^^^^###B",
    "B#^^^^^^^^^^######^^^^^^^^^^###B",
    "B#^^^^^^^^^^######^^^^^^^^^^###B",
    "B##############################B",
    "B##############################B",
    "B##############################B",
    "B##############################B",
    "B##############################B",
    "B######B################B######B",
    "B##############################B",
    "B##############################B",
    "B##############################B",
    "B##############################B",
    "B##############################B",
    "B##############################B",
    "BBBBBBBBBBBBBBBDDBBBBBBBBBBBBBBB",
)

#: Les dix cases, de gauche à droite : deux tuiles de large, trois de creux, le nez au mur nord.
CASES: tuple[dict, ...] = tuple({"n": k + 1, "x": x, "y": 2, "l": 2, "h": 3, "cap": -math.pi / 2}
                                for k, x in enumerate((2, 4, 6, 8, 10, 18, 20, 22, 24, 26)))

#: La rangée où l'on attend l'ascenseur (ses portes juste au sud) : ACTION y remonte à la pièce du garage, et on y
#: arrive en descendant.
ASCENSEUR = {"x": 15, "y": 16, "l": 2}

BLOC = {
    "slug": "souterrain",
    "nom": "Le garage souterrain",
    "panneau": "SOUS-SOL", "panneau_retour": "RUE",
    "plan": PLAN,
    "decors": {},
    # Pas de passage en ville : on ressort devant le rideau de Ti-Guy (`porte_de_garage` au lieu `garage`).
    "passage": None,
    "seuil": "garage",
    # La rampe, au nord : on la monte au volant (ou à pied), et on est devant le rideau.
    "retour": {"bord": "nord", "de": 14, "l": 3},
    "arrivee": {"x": 15, "y": 4},
    "gens": False,
    # Sous terre : ni pluie, ni neige, ni nuit (`Monde.aLAbri`).
    "abrite": True,
    "materiaux": {"B": "piece", "D": "piece"},
    "souterrain": {"cases": CASES, "ascenseur": ASCENSEUR},
}
```

- [ ] **Étape 4 : le ranger à part** — `app/blocs/__init__.py`.

Sous `BLOCS: list[dict] = [...]`, ajouter l'import et la liste (ajouter `souterrain` à la ligne
`from . import cineparc, galeries, rang, villa`) :

```python
from . import cineparc, galeries, rang, souterrain, villa  # noqa: E402

#: ⚠️ LES SOUS-SOLS : des blocs SANS passage en ville — on y descend par un rideau (`seuil`), pas en poussant contre
#: un bord. À part de `BLOCS`, dont les juges exigent un passage (docs/jalons/le-grand-garage-souterrain.md).
SOUS_SOLS: list[dict] = [souterrain.BLOC]
```

`par_slug` cherche dans les deux :

```python
def par_slug(slug: str) -> dict | None:
    return next((b for b in BLOCS + SOUS_SOLS if b["slug"] == slug), None)
```

Dans `carte_du_bloc`, à la fin du dict `"bloc"` (après `"nuit_tient"`) :

```python
                 # La nuit y attend qu'on ressorte (la villa, `Monde.majHeure`).
                 "nuit_tient": bool(bloc.get("nuit_tient", False)),
                 # Sous terre (le garage souterrain) : ni pluie, ni neige, ni nuit (`Monde.aLAbri`).
                 "abrite": bool(bloc.get("abrite", False)),
                 # Ses cases et son ascenseur (`Souterrain`) ; null ailleurs.
                 "souterrain": copy.deepcopy(bloc["souterrain"]) if bloc.get("souterrain") else None},
```

`pour_le_navigateur` : les sous-sols à la suite, `passage` à `None` et leur `seuil` :

```python
def pour_le_navigateur() -> list[dict]:
    ...  # la docstring ne change pas
    return [{"slug": b["slug"], "nom": b["nom"],
             "passage": passage_en_ville(b) if b.get("passage") else None,
             "panneau": b.get("panneau", b["nom"][:5].upper()),
             "portes": [{"x": p["x"], "y": p["y"], "nom": b.get("pieces", {})[p["interieur"]]["nom"]}
                        for p in b.get("portes", [])],
             **({"lieux": sorted(b["lieux"])} if b.get("lieux") else {}),
             **({"planque": True} if b.get("planque") else {}),
             # ⚠️ Un sous-sol : le rideau devant lequel on ressort (`Blocs.retourEnVille`).
             **({"seuil": b["seuil"]} if b.get("seuil") else {})} for b in BLOCS + SOUS_SOLS]
```

`erreurs` : le passage ne se juge que s'il existe. Remplacer la boucle `for cote in ("passage", "retour")` par :

```python
    for cote in ("passage", "retour"):
        if cote == "passage" and bloc.get("passage") is None and bloc.get("seuil"):
            continue   # un sous-sol : pas de bord en ville, un rideau
        if bloc[cote]["bord"] not in BORDS:
            fautes.append(f"{slug} : le {cote} n'est sur aucun bord ({bloc[cote]['bord']!r})")
```

et la garde du passage en ville `if ville is not None:` par `if ville is not None and bloc.get("passage"):`.

- [ ] **Étape 5 : servir sa carte** — `app/definitions.py:324` :

```python
    des_cartes = {b["slug"]: _signer(blocs.carte_du_bloc(b)) for b in blocs.BLOCS + blocs.SOUS_SOLS}
```

- [ ] **Étape 6 : les deux juges des blocs qui listent tout** — `tests/test_blocs.py`.

Dans `test_un_bloc_ne_change_pas_un_octet_de_la_ville`, patcher aussi les sous-sols :

```python
    monkeypatch.setattr(blocs, "BLOCS", [])
    monkeypatch.setattr(blocs, "SOUS_SOLS", [])
```

Dans `test_le_paquet_nomme_les_passages_et_pas_les_cartes`, les sous-sols à la suite, et leur clé `seuil` :

```python
    tous = blocs.BLOCS + blocs.SOUS_SOLS
    assert [b["slug"] for b in paquet["blocs"]] == [b["slug"] for b in tous]
    for b, source in zip(paquet["blocs"], tous):
        assert set(b) - {"lieux", "planque", "seuil"} == {"slug", "nom", "passage", "panneau", "portes"}
        assert (b["passage"] is None) is bool(source.get("seuil"))
```

(le reste de la boucle ne change pas).

- [ ] **Étape 7 : les juges au vert**

Run: `/Users/martingagne/dev/bandini/.venv/bin/python -m pytest tests/test_souterrain.py tests/test_blocs.py tests/test_rang.py tests/test_nord.py tests/test_definitions.py -q`
Expected: PASS. Si `test_definitions.py` rougit sur un plafond, lire le message : la carte du bloc voyage à part
(`/api/carte/bloc/souterrain`) et ne doit peser sur aucun plafond du paquet — une clé du paquet qui grossit, c'est
l'entrée de `pour_le_navigateur`, pas la carte.

- [ ] **Étape 8 : muter** — retirer `"^"` d'une case du `PLAN` (la remplacer par `#`) : `test_dix_cases_peintes…`
  rougit ; remettre. Mettre `"abrite": False` : `test_la_carte_du_bloc_porte_ses_cases_et_son_abri` rougit ; remettre.

- [ ] **Étape 9 : commiter**

```bash
git add app/blocs/souterrain.py app/blocs/__init__.py app/definitions.py tests/test_souterrain.py tests/test_blocs.py
```
```bash
git commit -m "feat(souterrain): le bloc du garage souterrain, un sous-sol sans passage en ville"
```

---

### Tâche 2 : l'ascenseur dans la pièce du garage

**Fichiers :**
- Modifier : `app/carte.py` (la pièce `garage`, vers la ligne 7629)
- Modifier : `tests/test_souterrain.py`

**Interfaces :**
- Produit : un point `{"type": "ascenseur", "x": 8, "y": 1}` dans `interieurs["garage"]["points"]` — la tuile de
  plancher au pied du mur nord, à l'est ; les portes se peignent sur le mur au-dessus (tâche 7).

- [ ] **Étape 1 : le juge qui échoue** — à la fin de `tests/test_souterrain.py` :

```python
def test_la_piece_du_garage_a_son_ascenseur_sur_le_plancher():
    ville = villes.exporter()
    piece = ville["interieurs"]["garage"]
    pt = next(p for p in piece["points"] if p["type"] == "ascenseur")
    sol = piece["sol"]
    assert carte.LEGENDE[sol[pt["y"]][pt["x"]]].get("solide", 0) == 0, "l'ascenseur s'attend debout, sur le plancher"
    assert sol[pt["y"] - 1][pt["x"]] == "B", "ses portes se peignent sur le mur, juste au nord"
```

- [ ] **Étape 2 : le voir rougir** — `…pytest tests/test_souterrain.py -q -k ascenseur_sur` : FAIL (`StopIteration`).

- [ ] **Étape 3 : le point** — dans `_piece("garage", …)` de `app/carte.py`, ajouter le point à la fin :

```python
""", points=(_pt("vendre", 3, 4), _pt("reparer", 7, 1), _pt("repeindre", 3, 2),
             # L'ascenseur du garage souterrain (docs/jalons/le-grand-garage-souterrain.md) : on l'attend au
             # pied du mur nord, ses portes peintes sur le mur (`Souterrain.dessiner`).
             _pt("ascenseur", 8, 1)),
```

- [ ] **Étape 4 : au vert, et la ville n'a pas bougé**

Run: `…pytest tests/test_souterrain.py tests/test_interieurs.py tests/test_blocs.py tests/test_definitions.py tests/test_meubles_js.py -q`
(`test_meubles_js.py` : le juge « points touchés depuis la porte »).
Expected: PASS.

- [ ] **Étape 5 : commiter**

```bash
git add app/carte.py tests/test_souterrain.py
```
```bash
git commit -m "feat(souterrain): l'ascenseur dans la pièce du garage"
```

---

### Tâche 3 : un bloc sans passage — descendre, remonter la rampe, ressortir devant le rideau

**Fichiers :**
- Créer : `static/js/souterrain.js` (le squelette : `SLUG`, `est`, `ici`)
- Modifier : `templates/index.html` (le script, juste après `blocs.js`)
- Modifier : `static/js/blocs.js` (`retourEnVille`, `maj`, `ouvertures`, `entrerAuNoir`, l'export)
- Modifier : `static/js/jeu.js` (`passerDansLeBloc`, `sortirDuBloc`)
- Modifier : `static/js/histoire.js:500` (`passageDuBloc`)
- Créer : `tests/test_souterrain_js.py`

**Interfaces :**
- Produit : `Blocs.retourEnVille(b, e)` → `{ x, y }` (un bloc à passage, comme avant) ou `{ x, y, cap }` (un
  sous-sol : devant son rideau, le nez vers la rue), ou `null` (le rideau n'existe pas).
- Produit : `B.bloc.ville.sortie` → `{ x, y, cap }` pour un sous-sol, `null` sinon ; `B.bloc.ville.passage` → `null`
  pour un sous-sol.
- Produit : `Souterrain.SLUG === 'souterrain'`, `Souterrain.est(slug)`, `Souterrain.ici()`.

- [ ] **Étape 1 : le juge qui échoue** — `tests/test_souterrain_js.py` :

```python
"""Le grand garage souterrain, JOUÉ (docs/jalons/le-grand-garage-souterrain.md) : on descend, on se gare, on
remonte la rampe et on ressort devant le rideau de Ti-Guy ; les chars rangés y sont encore au retour et au
rechargement ; le rideau et l'ascenseur, au bouton. Voir `static/js/souterrain.js`."""

OUTILS = """
  const TT = 16;
  function proprio(L) { L.B.partie.proprietes.garage = { jour: L.B.partie.jour, caisse: 0 }; }
  // La rue devant le rideau vidée (le trafic et les passants du hasard ne sont pas ce qu'on juge).
  function viderLaBaie(L) {
    const j = L.B.joueur, pg = L.Monde.porteDeGarage('garage'), baie = L.Monde.baieDeLaPorteDeGarage(pg);
    L.B.entites.filter(function (e) { return (e.type === 'vehicule' || e.type === 'pieton') && e !== j
        && Math.hypot(e.x - baie.x, e.y - baie.y) < 300; }).forEach(function (e) { L.Entites.retirer(e); });
    L.B.defs.conduite.trafic.vehicules_max = 0;
    return { pg: pg, baie: baie };
  }
  async function attendreLeBloc(L, o, slug) {
    for (let i = 0; i < 400 && !(L.B.bloc && L.B.bloc.slug === slug && !L.B.transition); i++) {
      o.frame(1); if (i % 10 === 0) await o.attendre();
    }
  }
  async function attendreLaVille(L, o) {
    for (let i = 0; i < 400 && (L.B.bloc || L.B.transition); i++) { o.frame(1); if (i % 10 === 0) await o.attendre(); }
  }
  // Un char à soi, garé nez au rideau, le joueur au volant.
  function auVolantDevant(L, slug, options) {
    const j = L.B.joueur, a = viderLaBaie(L);
    const v = L.Vehicules.creer(slug || 'auto', a.baie.x, a.baie.y, -Math.PI / 2,
                                Object.assign({ etat: 'stationne', couleur: '#c0392b' }, options || {}));
    j.x = v.x; j.y = v.y; L.Entites.indexer(); L.Vehicules.monter(j, v); L.Monde.centrerCamera(j.x, j.y);
    v.aToi = true;
    return Object.assign({ v: v }, a);
  }
  // Remonter la rampe au gaz, depuis le bas, nez au nord.
  async function remonterLaRampe(L, o, v) {
    const r = L.B.bloc.def.bloc.retour;
    v.x = (r.de + r.l / 2) * TT; v.y = 5 * TT; v.angle = -Math.PI / 2; v.vitesse = 0;
    const j = L.B.joueur; j.x = v.x; j.y = v.y;
    o.touche('KeyW');
    for (let i = 0; i < 300 && !L.B.transition; i++) o.frame(1);
    o.relacher('KeyW');
    await attendreLaVille(L, o);
  }
"""


def test_on_descend_au_noir_et_on_ressort_devant_le_rideau_le_nez_vers_la_rue(banc):
    r = banc("async function (L, o) {" + OUTILS + """
        L.Jeu.commencer(); proprio(L);
        const B = L.B, j = B.joueur, a = auVolantDevant(L);
        L.Blocs.sauter('souterrain', null, null);
        await attendreLeBloc(L, o, 'souterrain');
        const def = B.bloc && B.bloc.def.bloc;
        const dedans = { bloc: B.bloc && B.bloc.slug, auVolant: j.dansVehicule === a.v,
                         tuile: [Math.floor(a.v.x / TT), Math.floor(a.v.y / TT)], cap: +a.v.angle.toFixed(2),
                         arrivee: def && [def.arrivee.x, def.arrivee.y], sortie: B.bloc.ville.sortie,
                         passage: B.bloc.ville.passage };
        await remonterLaRampe(L, o, a.v);
        return { dedans: dedans, apres: { bloc: !!B.bloc, auVolant: j.dansVehicule === a.v, enVille: B.entites.indexOf(a.v) >= 0,
                 x: a.v.x, y: a.v.y, cap: +a.v.angle.toFixed(2), attendu: { x: a.baie.x, y: a.baie.y + 2 * TT + 8 },
                 menu: !!B.menu } };
    }""")
    d, a = r["dedans"], r["apres"]
    assert d["bloc"] == "souterrain" and d["auVolant"], d
    assert d["tuile"] == d["arrivee"], f"on arrive au bas de la rampe : {d}"
    assert d["cap"] == 1.57, f"le nez vers l'allée (le sud) : {d}"
    assert d["passage"] is None and d["sortie"], d
    assert a["bloc"] is False and a["auVolant"] and a["enVille"], a
    assert abs(a["x"] - a["attendu"]["x"]) < 1 and abs(a["y"] - a["attendu"]["y"]) < 20, a
    assert a["cap"] == 1.57, f"on ressort le nez vers la rue : {a}"
    assert a["menu"] is False, "ressortir ne rouvre pas le menu du garage"


def test_aucune_plaque_ni_passage_en_ville_pour_le_sous_sol(banc):
    """Un sous-sol n'a pas de passage : aucune plaque en ville ne le montre, et longer tous les bords n'y mène pas."""
    r = banc("function (L, o) {" + OUTILS + """
        L.Jeu.commencer();
        const b = L.Blocs.liste().find(function (q) { return q.slug === 'souterrain'; });
        o.frame(5);
        return { liste: !!b, passage: b && b.passage, seuil: b && b.seuil, bloc: !!L.B.bloc,
                 gps: L.Histoire.passageDuBloc('souterrain') };
    }""")
    assert r["liste"] and r["passage"] is None and r["seuil"] == "garage", r
    assert r["bloc"] is False and r["gps"] is None, r
```

- [ ] **Étape 2 : le voir rougir** — `…pytest tests/test_souterrain_js.py -q` : FAIL (`Blocs.sauter` lit
  `b.passage.bord` de `null`, ou la sortie n'est pas devant le rideau).

- [ ] **Étape 3 : le squelette** — `static/js/souterrain.js` :

```js
/* Bandini — le grand garage souterrain, sous le Garage Rocco Bandini (docs/jalons/le-grand-garage-souterrain.md).

   Martin, 30 sept. 2026 : « le garage Bandini doit pouvoir stocker des vehicules que nous pourrons reprendre
   apres dans un grand garage souterrain ». Un BLOC DE CARTE sans passage en ville (`app/blocs/souterrain.py`) :
   on y descend au volant par le rideau de Ti-Guy (DESCENDRE AU SOUS-SOL), ou a pied par l'ascenseur de la piece
   du garage ; on remonte la rampe, et on est devant le rideau.

   ⚠️ LES CHARS RANGES VIVENT DANS LA PARTIE (`partie.souterrain.cases`), JAMAIS DANS LA MEMOIRE DU BLOC :
   `garnir` les pose a chaque descente, `ranger` les reecrit en remontant et a chaque sauvegarde. La ville oublie
   un char gare loin (`Vehicules.peupler`) ; celui-ci, jamais. */

const Souterrain = (function () {
  'use strict';

  const TT = 16;
  const SLUG = 'souterrain';

  /** Ce bloc-ci est-il le sous-sol ? */
  function est(slug) { return slug === SLUG; }

  /** Y est-on ? */
  function ici() { return !!(B.bloc && B.bloc.slug === SLUG); }

  return { SLUG, est, ici };
})();
```

Dans `templates/index.html`, juste après la ligne de `js/blocs.js` :

```html
<script src="{{ url_for('static', filename='js/souterrain.js') }}?v={{ version }}"></script>
```

Et dans `static/js/jeu.js`, ajouter `Souterrain: Souterrain` à `window.BANDINI` (à côté de `Blocs: Blocs`).

- [ ] **Étape 4 : `Blocs` sans passage** — `static/js/blocs.js`.

Après `capVersLInterieur`, ajouter :

```js
  /** Ou l'on reviendra en ville en sortant de ce bloc : juste en deca de son passage (`recul`) — ou, pour un
      SOUS-SOL (pas de passage, un `seuil`), devant son rideau, a quatre tuiles de la facade (la chaussee), le nez
      vers la rue (`cap`). Null si le rideau n'est pas dans la carte courante. */
  function retourEnVille(b, e) {
    if (b.passage) return recul(b.passage, Monde.carte, e);
    const pg = b.seuil && Monde.porteDeGarage(b.seuil);
    if (!pg) return null;
    const baie = Monde.baieDeLaPorteDeGarage(pg);
    return { x: baie.x, y: baie.y + 2 * TT + 8, cap: Math.PI / 2 };
  }
```

Dans `maj`, la boucle de la ville saute ce qui n'a pas de passage :

```js
    for (const b of liste()) {
      if (!b.passage || !pres(b.passage, Monde.carte, j)) continue;
```

Dans `ouvertures`, la ville ne plaque que les passages :

```js
    return liste().filter(function (b) { return b.passage; })
      .map(function (b) { return { o: b.passage, mot: b.panneau || 'CHEMIN', nom: b.nom }; });
```

Dans `entrerAuNoir` :

```js
  function entrerAuNoir(slug, ici) {
    const b = liste().find(function (q) { return q.slug === slug; }), def = cartes[slug];
    if (!b || !def || B.bloc) return false;
    const retour = retourEnVille(b, B.joueur);
    if (!retour) return false;
    Jeu.passerDansLeBloc(b, def, retour, ici || null);
    return true;
  }
```

Ajouter `retourEnVille` à l'objet rendu (à côté de `recul`).

- [ ] **Étape 5 : `Jeu` sans passage** — `static/js/jeu.js`.

Dans `passerDansLeBloc`, remplacer la construction de `B.bloc` :

```js
    const passage = bloc.passage || null;
    B.bloc = { slug: bloc.slug, def: def, ville: { carte: Monde.carte, entites: ville, x: retour.x, y: retour.y,
                                                   passage: passage,
                                                   leLong: !passage ? 0 : passage.bord === 'nord' || passage.bord === 'sud' ? j.x : j.y,
                                                   // ⚠️ UN SOUS-SOL (le garage souterrain) n'a pas de passage : on
                                                   // ressort devant son rideau, le nez vers la rue (`Blocs.retourEnVille`).
                                                   sortie: passage ? null : { x: retour.x, y: retour.y, cap: retour.cap } } };
```

Dans `sortirDuBloc`, au noir, remplacer les trois lignes qui posent et relancent la poursuite :

```js
      const point = ville.sortie ? { x: ville.sortie.x, y: ville.sortie.y }
        : Blocs.recul(ville.passage, Monde.carte, Blocs.porteur(j), ville.leLong);
      poserLesVoyageurs(gens, point, ville.sortie ? ville.sortie.cap : Blocs.capVersLInterieur(ville.passage));
      if (ville.passage) Blocs.poursuiteAuBord(ville.passage, Monde.carte);
```

- [ ] **Étape 6 : le GPS** — `static/js/histoire.js`, dans `passageDuBloc`, remplacer `if (!b) return null;` par :

```js
    if (!b || !b.passage) return null;   // un sous-sol n'a pas de passage : on y descend par un rideau
```

- [ ] **Étape 7 : au vert, et les blocs d'avant aussi**

Run: `…pytest tests/test_souterrain_js.py tests/test_blocs_js.py tests/test_cineparc_js.py -q`
Expected: PASS.

- [ ] **Étape 8 : muter** — dans `retourEnVille`, rendre `cap: -Math.PI / 2` : le premier juge rougit (« le nez vers
  la rue ») ; remettre.

- [ ] **Étape 9 : commiter**

```bash
git add static/js/souterrain.js templates/index.html static/js/blocs.js static/js/jeu.js static/js/histoire.js tests/test_souterrain_js.py
```
```bash
git commit -m "feat(souterrain): un bloc sans passage — on y descend, on remonte la rampe, on ressort devant le rideau"
```

---

### Tâche 4 : la mémoire des chars — ranger, garnir, recharger

**Fichiers :**
- Modifier : `static/js/base.js` (`etatInitial` : `souterrain` ; `completer`)
- Modifier : `static/js/souterrain.js` (`CASES_MAX`, `PAR_NIVEAU`, `ouvertes`, `occupees`, `plein`, `fiche`, `caseSous`, `ranger`, `garnir`)
- Modifier : `static/js/jeu.js` (`passerDansLeBloc` garnit, `quitterLeBloc` range)
- Modifier : `static/js/missions.js` (`sauvegarderPartie`)
- Modifier : `tests/test_souterrain_js.py`

**Interfaces :**
- Consomme : `B.bloc.def.bloc.souterrain.cases` (tâche 1), `Souterrain.est` (tâche 3).
- Produit : `partie.souterrain = { niveaux: 1, cases: [20 × (null | { slug, sprite, couleur, vie, vole, aToi, mods })] }`.
- Produit : `Souterrain.ranger(entites, def)` → rend les entités qui ne sont pas des chars (ce que le bloc peut
  garder), et réécrit `partie.souterrain.cases` ; `Souterrain.garnir(def)` → pose les chars rangés ;
  `Souterrain.ouvertes()`, `Souterrain.occupees()`, `Souterrain.plein()` → nombres et booléen.

- [ ] **Étape 1 : les juges qui échouent** — à la fin de `tests/test_souterrain_js.py` :

```python
GARER = """
  // Garer le char sur la case k (0 = P1), nez au mur, et en descendre.
  function garerSur(L, v, k) {
    const q = L.B.bloc.def.bloc.souterrain.cases[k], j = L.B.joueur;
    if (j.dansVehicule !== v) { j.x = v.x; j.y = v.y; L.Vehicules.monter(j, v); }
    v.x = (q.x + q.l / 2) * TT; v.y = (q.y + q.h / 2) * TT; v.angle = -Math.PI / 2; v.vitesse = 0; v.vx = 0; v.vy = 0;
    L.Vehicules.descendre(j, true);
    j.x = 15 * TT + 8; j.y = 8 * TT + 8;
    L.Entites.indexer();
  }
"""


def test_un_char_gare_sur_une_case_y_est_encore_au_retour_avec_sa_couleur_ses_pieces_et_ses_bosses(banc):
    r = banc("async function (L, o) {" + OUTILS + GARER + """
        L.Jeu.commencer(); proprio(L);
        const B = L.B, j = B.joueur, a = auVolantDevant(L, 'auto', { couleur: '#2e86de' });
        L.Garage.poser(a.v, { moteur: true }); a.v.vie = 40; a.v.vole = true;
        L.Blocs.sauter('souterrain', null, null); await attendreLeBloc(L, o, 'souterrain');
        garerSur(L, a.v, 2);
        // On remonte à pied par la rampe, on redescend.
        L.Jeu.sortirDuBloc(); await attendreLaVille(L, o);
        const ecrit = B.partie.souterrain.cases[2];
        const enVille = B.entites.indexOf(a.v) >= 0;
        L.Blocs.sauter('souterrain', null, null); await attendreLeBloc(L, o, 'souterrain');
        const q = B.bloc.def.bloc.souterrain.cases[2];
        const revenu = B.entites.filter(function (e) { return e.type === 'vehicule'; });
        const v = revenu[0];
        return { ecrit: ecrit, enVille: enVille, n: revenu.length,
                 v: v && { slug: v.slug, couleur: v.couleur, mods: v.mods, vie: v.vie, vole: v.vole, aToi: v.aToi,
                           x: v.x, y: v.y, cx: (q.x + q.l / 2) * TT, cy: (q.y + q.h / 2) * TT } };
    }""")
    assert r["ecrit"] and r["ecrit"]["couleur"] == "#2e86de" and r["ecrit"]["mods"] == {"moteur": True}, r
    assert r["enVille"] is False, "le char rangé ne remonte pas en ville"
    assert r["n"] == 1, f"un seul char, pas un double de mémoire : {r['n']}"
    v = r["v"]
    assert (v["slug"], v["couleur"], v["mods"], v["vie"], v["vole"], v["aToi"]) == ("auto", "#2e86de", {"moteur": True}, 40, True, True), v
    assert abs(v["x"] - v["cx"]) < 1 and abs(v["y"] - v["cy"]) < 1, "il revient sur SA case"


def test_un_char_laisse_dans_l_allee_ti_guy_le_gare_sur_la_premiere_case_libre(banc):
    r = banc("async function (L, o) {" + OUTILS + GARER + """
        L.Jeu.commencer(); proprio(L);
        const B = L.B, j = B.joueur, a = auVolantDevant(L);
        B.partie.souterrain.cases[0] = { slug: 'auto', sprite: undefined, couleur: '#f1c40f', vie: 100, vole: false, aToi: true };
        L.Blocs.sauter('souterrain', null, null); await attendreLeBloc(L, o, 'souterrain');
        // En plein milieu de l'allée, et on remonte à pied.
        a.v.x = 20 * TT; a.v.y = 9 * TT; L.Vehicules.descendre(j, true); j.x = 15 * TT + 8; j.y = 6 * TT;
        L.Jeu.sortirDuBloc(); await attendreLaVille(L, o);
        return B.partie.souterrain.cases.slice(0, 3).map(function (c) { return c && c.couleur; });
    }""")
    assert r == ["#f1c40f", "#c0392b", None], f"le jaune garde P1, le rouge de l'allée prend P2 : {r}"


def test_le_char_qu_on_remonte_quitte_le_sous_sol_et_un_vole_reste_vole(banc):
    r = banc("async function (L, o) {" + OUTILS + GARER + """
        L.Jeu.commencer(); proprio(L);
        const B = L.B, j = B.joueur;
        viderLaBaie(L);
        B.partie.souterrain.cases[4] = { slug: 'auto', couleur: '#8e44ad', vie: 90, vole: true, aToi: false };
        L.Blocs.sauter('souterrain', null, null); await attendreLeBloc(L, o, 'souterrain');
        const v = B.entites.find(function (e) { return e.type === 'vehicule'; });
        j.x = v.x; j.y = v.y; L.Vehicules.monter(j, v);
        await remonterLaRampe(L, o, v);
        return { case4: B.partie.souterrain.cases[4], enVille: B.entites.indexOf(v) >= 0, vole: v.vole, auVolant: j.dansVehicule === v };
    }""")
    assert r["case4"] is None, "la case se libère quand on remonte avec son char"
    assert r["enVille"] and r["auVolant"], r
    assert r["vole"] is True, "le sous-sol cache, il ne lave pas"


def test_sauvegardee_au_sous_sol_la_partie_s_y_rouvre_avec_ses_chars_et_celui_qu_on_conduisait(banc):
    r = banc("async function (L, o) {" + OUTILS + GARER + """
        L.Jeu.commencer(); proprio(L);
        const B = L.B, a = auVolantDevant(L, 'auto', { couleur: '#16a085' });
        B.partie.souterrain.cases[7] = { slug: 'camion', couleur: '#d35400', vie: 120, vole: false, aToi: true };
        L.Blocs.sauter('souterrain', null, null); await attendreLeBloc(L, o, 'souterrain');
        // Toujours au volant, au milieu de l'allée : on sauvegarde.
        a.v.x = 12 * TT; a.v.y = 9 * TT; B.joueur.x = a.v.x; B.joueur.y = a.v.y;
        L.Missions.sauvegarderPartie();
        B.partie = L.Sauvegarde.completer(JSON.parse(o.store['bandini-partie-v1']), B.defs);
        L.Jeu.commencer();
        await attendreLeBloc(L, o, 'souterrain');
        const chars = B.entites.filter(function (e) { return e.type === 'vehicule'; })
          .map(function (e) { return e.couleur; }).sort();
        return { bloc: B.bloc && B.bloc.slug, chars: chars, cases: B.partie.souterrain.cases.filter(Boolean).length };
    }""")
    assert r["bloc"] == "souterrain", "on se réveille au sous-sol"
    assert r["chars"] == ["#16a085", "#d35400"], f"le camion rangé ET le char qu'on conduisait : {r}"
    assert r["cases"] == 2, r


def test_garnir_ne_tire_aucun_de(banc):
    """⚠️ Un char né sans couleur tire un dé et fait glisser tout le hasard de la partie : même graine, même tirage
    suivant, qu'on ait garni le sous-sol ou pas."""
    r = banc("async function (L, o) {" + OUTILS + """
        L.Jeu.commencer(); proprio(L);
        const B = L.B;
        B.partie.souterrain.cases[0] = { slug: 'auto', couleur: '#c0392b', vie: 100, vole: false, aToi: true };
        B.partie.souterrain.cases[1] = { slug: 'moto', couleur: '#2c3e50', vie: 60, vole: false, aToi: true };
        L.Blocs.sauter('souterrain', null, null); await attendreLeBloc(L, o, 'souterrain');
        const def = B.bloc.def;
        B.entites = B.entites.filter(function (e) { return e.type !== 'vehicule'; });
        L.graine(7); L.Souterrain.garnir(def); const avec = B.rng();
        L.graine(7); const sans = B.rng();
        return { avec: avec, sans: sans };
    }""")
    assert r["avec"] == r["sans"], r


def test_une_vieille_partie_sans_sous_sol_se_complete(banc):
    r = banc("function (L, o) {" + OUTILS + """
        const p = L.Sauvegarde.completer({ argent: 5 }, L.B.defs);
        const q = L.Sauvegarde.completer({ souterrain: { niveaux: 9, cases: [{ slug: 'auto', couleur: '#fff' }, 'x'] } }, L.B.defs);
        return { p: p.souterrain, q: q.souterrain };
    }""")
    assert r["p"] == {"niveaux": 1, "cases": [None] * 20}, r
    assert r["q"]["niveaux"] == 1 and len(r["q"]["cases"]) == 20, r
    assert r["q"]["cases"][0]["slug"] == "auto" and r["q"]["cases"][1] is None, r
```

- [ ] **Étape 2 : les voir rougir** — `…pytest tests/test_souterrain_js.py -q` : les six neufs FAIL
  (`partie.souterrain` est `undefined`).

- [ ] **Étape 3 : la partie** — `static/js/base.js`, dans `etatInitial`, après `bloc: null,` :

```js
    //: LE GARAGE SOUTERRAIN (docs/jalons/le-grand-garage-souterrain.md) : ses niveaux ouverts (le −2 s'achète, vague
    //: 2) et ses vingt cases, chacune vide ou la fiche du char qui y dort — `{ slug, sprite, couleur, vie, vole, aToi,
    //: mods }`, comme le char de la planque, SANS position : la case EST la position.
    souterrain: { niveaux: 1, cases: [null, null, null, null, null, null, null, null, null, null,
                                      null, null, null, null, null, null, null, null, null, null] },
```

Dans `completer`, juste après `if (!Array.isArray(out.fourriere)) out.fourriere = [];` :

```js
    // Le sous-sol : ses niveaux (1 ou 2, rien d'autre) et vingt cases exactement — une fiche de char ou null.
    // ⚠️ Un objet imbrique ne passe pas par la fusion d'en haut : une partie d'avant lui arriverait sans cases.
    const sous = partie.souterrain && typeof partie.souterrain === 'object' ? partie.souterrain : {};
    out.souterrain = { niveaux: sous.niveaux === 2 ? 2 : 1, cases: [] };
    for (let k = 0; k < 20; k++) {
      const c = Array.isArray(sous.cases) ? sous.cases[k] : null;
      out.souterrain.cases.push(c && typeof c === 'object' && typeof c.slug === 'string' ? c : null);
    }
```

- [ ] **Étape 4 : ranger et garnir** — dans `static/js/souterrain.js`, avant le `return` :

```js
  //: Les cases d'un niveau, et de tout le sous-sol (`app/blocs/souterrain.py`, les memes nombres).
  const PAR_NIVEAU = 10, CASES_MAX = 20;

  /** Les cases ouvertes : dix par niveau achete. */
  function ouvertes() { return PAR_NIVEAU * ((B.partie.souterrain && B.partie.souterrain.niveaux) || 1); }
  /** Les cases ouvertes ou dort un char. */
  function occupees() { return B.partie.souterrain.cases.slice(0, ouvertes()).filter(Boolean).length; }
  function plein() { return occupees() >= ouvertes(); }

  /** Ce qu'on ecrit d'un char : comme le char de la planque, sans position. */
  function fiche(v) {
    return { slug: v.slug, sprite: v.sprite, couleur: v.couleur, vie: v.vie, vole: !!v.vole, aToi: !!v.aToi, mods: Garage.fiche(v) };
  }

  /** La case (son rang) sous le centre de ce char, ou -1. */
  function caseSous(cases, v) {
    for (let k = 0; k < cases.length; k++) {
      const q = cases[k];
      if (v.x >= q.x * TT && v.x < (q.x + q.l) * TT && v.y >= q.y * TT && v.y < (q.y + q.h) * TT) return k;
    }
    return -1;
  }

  /** Reecrit `partie.souterrain.cases` d'apres les chars de `entites` : chacun sur SA case s'il y est (et qu'elle
      est ouverte et libre), les autres — laisses dans l'allee — gares par Ti-Guy sur la premiere case libre. Une
      epave ne se range pas. Rend ce qui n'est pas un char : ce que le bloc peut garder (`Blocs.garder`).
      ⚠️ Ne retire rien : la sauvegarde l'appelle en plein sous-sol, les chars restent ou ils sont. */
  function ranger(entites, def) {
    const cases = def.bloc.souterrain.cases, n = ouvertes();
    const neuf = [];
    for (let k = 0; k < CASES_MAX; k++) neuf.push(null);
    const reste = [], sansPlace = [];
    for (const e of entites) {
      if (e.type !== 'vehicule') { reste.push(e); continue; }
      if (e.etat === 'epave') continue;
      const k = caseSous(cases, e);
      if (k >= 0 && k < n && !neuf[k]) neuf[k] = fiche(e); else sansPlace.push(e);
    }
    for (const e of sansPlace) {
      let k = 0;
      while (k < n && neuf[k]) k++;
      if (k < n) neuf[k] = fiche(e);
    }
    B.partie.souterrain.cases = neuf;
    return reste;
  }

  /** Pose les chars ranges sur leurs cases, a la descente. ⚠️ `couleur` DONNEE a `Vehicules.creer` : un char ne
      sans couleur tire un de, et tout le hasard de la partie glisse. */
  function garnir(def) {
    const cases = def.bloc.souterrain.cases, n = ouvertes();
    B.partie.souterrain.cases.forEach(function (c, k) {
      if (!c || k >= n || !cases[k] || !Vehicules.vehiculeDef(c.slug)) return;
      const q = cases[k];
      const v = Vehicules.creer(c.slug, (q.x + q.l / 2) * TT, (q.y + q.h / 2) * TT, q.cap,
                                { etat: 'stationne', sprite: c.sprite, couleur: c.couleur });
      if (!v) return;
      if (c.couleur) v.swaps = nuances(c.couleur);
      Garage.poser(v, c.mods);
      v.vie = Math.max(1, c.vie || v.vieMax); v.vole = !!c.vole; v.aToi = !!c.aToi;
      // Comme le char d'une planque : l'hiver, le balayage des deux-roues remisees ne l'emporte pas.
      v.aLaPlanque = true;
    });
  }
```

Et l'objet rendu devient :

```js
  return { SLUG, PAR_NIVEAU, CASES_MAX, est, ici, ouvertes, occupees, plein, fiche, ranger, garnir };
```

- [ ] **Étape 5 : les brancher** — `static/js/jeu.js`.

Dans `passerDansLeBloc`, juste après le `if (souvenir) { … } else { … }` :

```js
    // ⚠️ LE SOUS-SOL SE GARNIT A CHAQUE DESCENTE, souvenir ou pas : ses chars vivent dans la partie, et le bloc
    // n'en garde jamais un (`quitterLeBloc` → `Souterrain.ranger`).
    if (Souterrain.est(bloc.slug)) Souterrain.garnir(def);
```

Dans `quitterLeBloc`, remplacer la ligne `Blocs.garder(…)` :

```js
    let restent = B.entites.filter(function (e) { return partent.indexOf(e) < 0 && !Entites.estJoueur(e); });
    // Le sous-sol ecrit ses chars dans la partie, et le bloc ne garde que le reste.
    if (Souterrain.est(bloc.slug)) restent = Souterrain.ranger(restent, bloc.def);
    Blocs.garder(bloc.slug, restent);
```

- [ ] **Étape 6 : la sauvegarde** — `static/js/missions.js`, dans `sauvegarderPartie`, juste avant
  `garderLesCharsDesPlanques(p);` :

```js
      // Au sous-sol, ses chars tels qu'ils sont — celui qu'on conduit compris, que Ti-Guy garera au reveil.
      if (Souterrain.ici()) Souterrain.ranger(B.entites, B.bloc.def);
```

- [ ] **Étape 7 : au vert**

Run: `…pytest tests/test_souterrain_js.py tests/test_blocs_js.py tests/test_garage_js.py -q -k "not klaxon_joue_gens"`
puis `…pytest tests/test_garage_js.py -q -k sauvegarde`.
Expected: PASS.

- [ ] **Étape 8 : muter** — dans `garnir`, retirer `couleur: c.couleur` : `test_garnir_ne_tire_aucun_de` rougit ;
  remettre. Dans `quitterLeBloc`, retirer la ligne `Souterrain.ranger` : `…y_est_encore_au_retour…` rougit (deux chars,
  ou aucun écrit) ; remettre.

- [ ] **Étape 9 : commiter**

```bash
git add static/js/base.js static/js/souterrain.js static/js/jeu.js static/js/missions.js tests/test_souterrain_js.py
```
```bash
git commit -m "feat(souterrain): les chars rangés vivent dans la partie — Ti-Guy gare ce qu'on laisse dans l'allée"
```

---

### Tâche 5 : DESCENDRE AU SOUS-SOL, au rideau de Ti-Guy

**Fichiers :**
- Modifier : `static/js/souterrain.js` (`refus`, `descendre`)
- Modifier : `static/js/missions.js` (`menuDuRideau`, `majGarage`)
- Modifier : `tests/test_souterrain_js.py`

**Interfaces :**
- Consomme : `Missions.possede`, `Missions.proprieteDe` (existants), `Souterrain.plein/occupees/ouvertes` (tâche 4).
- Produit : `Souterrain.refus(v)` → chaîne (la raison, à l'écran) ou `null` ; `Souterrain.descendre(v, pg)` → bool ;
  `pg.garde` (le char qui descend : le rideau l'ignore tant que le fondu joue).

- [ ] **Étape 1 : les juges qui échouent** — à la fin de `tests/test_souterrain_js.py` :

```python
RIDEAU = """
  // Garé nez au rideau, on attend le menu de Ti-Guy, et on choisit la ligne au bouton.
  function menuDuRideau(L, o) { for (let k = 0; k < 240 && !L.B.menu; k++) o.frame(1); return L.B.menu; }
  function choisir(L, o, libelle) {
    const k = L.B.menu.items.findIndex(function (i) { return i.libelle === libelle; });
    if (k < 0) return false;
    L.B.menu.curseur = k; o.tape('KeyE', 2);
    return true;
  }
"""


def test_au_rideau_descendre_au_sous_sol_au_bouton_et_le_rideau_ne_remonte_pas_pendant_le_fondu(banc):
    r = banc("async function (L, o) {" + OUTILS + RIDEAU + """
        L.Jeu.commencer(); proprio(L);
        const B = L.B, a = auVolantDevant(L);
        const menu = menuDuRideau(L, o);
        const libelles = menu ? menu.items.map(function (i) { return i.libelle; }) : [];
        choisir(L, o, 'DESCENDRE AU SOUS-SOL');
        // Le fondu : le rideau ne remonte pas, le menu ne revient pas.
        let menuPendant = false;
        for (let i = 0; i < 400 && !(B.bloc && !B.transition); i++) {
          o.frame(1); if (i % 10 === 0) await o.attendre();
          if (!B.bloc) menuPendant = menuPendant || !!B.menu;
        }
        return { libelles: libelles, bloc: B.bloc && B.bloc.slug, auVolant: B.joueur.dansVehicule === a.v,
                 menuPendant: menuPendant };
    }""")
    assert r["libelles"][:2] == ["REPARTIR", "DESCENDRE AU SOUS-SOL"], f"REPARTIR reste en tête : {r['libelles']}"
    assert r["bloc"] == "souterrain" and r["auVolant"], r
    assert r["menuPendant"] is False, "le menu de Ti-Guy s'est rouvert pendant la descente"


@pytest.mark.parametrize("cas", ["pas_proprio", "etoiles", "mission", "plein"])
def test_le_sous_sol_refuse_et_le_dit(banc, cas):
    r = banc("async function (L, o) {" + OUTILS + RIDEAU + """
        L.Jeu.commencer();
        const B = L.B, cas = '""" + cas + """';
        if (cas !== 'pas_proprio') proprio(L);
        const a = auVolantDevant(L);
        if (cas === 'etoiles') { B.recherche.etoiles = 1; B.recherche.chaleur = 20; }
        if (cas === 'mission') a.v.mission = true;
        if (cas === 'plein') for (let k = 0; k < 10; k++) B.partie.souterrain.cases[k] = { slug: 'auto', couleur: '#fff', vie: 100 };
        const menu = menuDuRideau(L, o);
        const ligne = menu && menu.items.find(function (i) { return i.libelle === 'DESCENDRE AU SOUS-SOL'; });
        if (ligne) choisir(L, o, 'DESCENDRE AU SOUS-SOL');
        for (let i = 0; i < 60; i++) o.frame(1);
        return { ligne: ligne ? { actif: ligne.actif !== false, detail: ligne.detail } : null,
                 bloc: !!B.bloc, transition: !!B.transition };
    }""")
    if cas == "mission":
        # Le char d'une mission se livre DEVANT le rideau : le menu ne s'ouvre pas du tout.
        assert r["ligne"] is None and not r["bloc"], r
        return
    assert r["ligne"] and r["ligne"]["actif"] is False, r
    attendu = {"pas_proprio": "GARAGE", "etoiles": "POLICE", "plein": "10/10"}[cas]
    assert attendu in r["ligne"]["detail"], r
    assert not r["bloc"] and not r["transition"], r
```

Ajouter `import pytest` en tête du fichier.

- [ ] **Étape 2 : les voir rougir** — FAIL : la ligne n'existe pas.

- [ ] **Étape 3 : refuser et descendre** — `static/js/souterrain.js`, avant le `return` :

```js
  /** Pourquoi ce char ne descend pas — la raison, telle qu'elle s'ecrit a la ligne du menu — ou null. */
  function refus(v) {
    if (!Missions.possede(Missions.proprieteDe('garage'))) return 'ACHÈTE LE GARAGE D’ABORD';
    if (B.recherche.etoiles > 0) return 'SÈME LA POLICE D’ABORD';
    if (v.mission || v.aQui) return 'CE CHAR-LÀ N’EST PAS À TOI';
    if (v.def && v.def.eau) return 'UN BATEAU ? DANS UN GARAGE ?';
    if (v.remorque) return 'DÉCROCHE CE QUE TU TIRES D’ABORD';
    if (plein()) return 'SOUS-SOL PLEIN — ' + occupees() + '/' + ouvertes();
    return null;
  }

  /** DESCENDRE AU SOUS-SOL, du menu du rideau : l'atelier se defait (s'il tenait le char sous le toit), le rideau
      garde le char (`pg.garde` : ni leve, ni menu pendant le fondu), et le bloc se charge au noir. */
  function descendre(v, pg) {
    const r = refus(v);
    if (r) { Hud.message(r, 150); Son.SFX.erreur(); return false; }
    if (pg && pg.dedans === v) { pg.dedans = null; pg.phase = null; pg.admis = null; }
    v.atelier = null;
    if (pg) { pg.garde = v; pg.servi = v; }
    return Blocs.sauter(SLUG, null, null);
  }
```

et les ajouter à l'objet rendu (`refus, descendre`).

- [ ] **Étape 4 : la ligne du menu** — `static/js/missions.js`.

`menuDuRideau` prend le rideau, et la ligne vient en deuxième :

```js
  function menuDuRideau(v, pg) {
    const items = [{ libelle: 'REPARTIR', faire: function () { return true; } }];
    // LE GARAGE SOUTERRAIN (docs/jalons/le-grand-garage-souterrain.md) : en deuxieme, jamais en tete — le menu
    // s'ouvre au moment ou l'on freine, et deux pressions d'ACTION ne doivent que REPARTIR.
    const non = Souterrain.refus(v);
    items.push({ libelle: 'DESCENDRE AU SOUS-SOL', detail: non || (Souterrain.occupees() + '/' + Souterrain.ouvertes()),
                 actif: !non, faire: function () { return Souterrain.descendre(v, pg || Monde.porteDeGarage('garage')); } });
    const menu = menuGarage(items, v);
    menu.refaire = function () { return menuDuRideau(v, pg); };
    return menu;
  }
```

Les deux appels passent le rideau : dans `majAtelier`, `Hud.ouvrirMenu(menuDuRideau(v, pg));` ; dans `majGarage`,
`Hud.ouvrirMenu(menuDuRideau(v, pg));`.

Dans `majGarage`, en tête de la première boucle `for (const pg of portes) {` :

```js
      // ⚠️ Le char qui descend au sous-sol (`Souterrain.descendre`) : pendant le fondu, le rideau ne se releve pas
      // pour lui et le menu ne se rouvre pas. Au noir, il a quitte la ville.
      if (pg.garde) { if (B.transition) continue; pg.garde = null; }
```

et, dans la deuxième boucle (celle du menu devant le rideau), la même garde en tête :
`if (pg.garde) continue;`.

- [ ] **Étape 5 : au vert, et le rideau d'avant aussi**

Run: `…pytest tests/test_souterrain_js.py tests/test_poste_et_garage_js.py tests/test_garages_ou_l_on_entre_js.py tests/test_garage_js.py -q`
Expected: PASS. ⚠️ Un juge du rideau qui lisait les lignes par leur RANG (`items[1]`) rougit : le corriger pour
qu'il cherche la ligne par son libellé, pas pour qu'il saute la nouvelle.

- [ ] **Étape 6 : muter** — dans `majGarage`, retirer la garde `pg.garde` : `…ne_remonte_pas_pendant_le_fondu`
  rougit (le menu revient) — s'il reste vert, le juge ne mord pas : le rendre plus sévère avant de continuer ; remettre.

- [ ] **Étape 7 : commiter**

```bash
git add static/js/souterrain.js static/js/missions.js tests/test_souterrain_js.py
```
```bash
git commit -m "feat(souterrain): DESCENDRE AU SOUS-SOL au rideau de Ti-Guy, et ses refus"
```

---

### Tâche 6 : l'ascenseur, dans les deux sens

**Fichiers :**
- Modifier : `static/js/souterrain.js` (`descendreAPied`, `monterAPied`, `sousLaMain`, `invite`, `agir`)
- Modifier : `static/js/missions.js` (`LIBELLES`, `utiliserPoint`, `interagir`, `majInvite`)
- Modifier : `tests/test_souterrain_js.py`

**Interfaces :**
- Consomme : le point `ascenseur` de la pièce `garage` (tâche 2) ; `def.bloc.souterrain.ascenseur` (tâche 1) ;
  `Jeu.quitterLaPiece`, `Jeu.revenirEnVille`, `Jeu.chargerPiece`, `Jeu.transiter`, `Blocs.charger`,
  `Blocs.entrerAuNoir`, `Blocs.cartes` (existants).
- Produit : `Souterrain.descendreAPied()`, `Souterrain.monterAPied()` → bool ; `Souterrain.sousLaMain(j)` → bool ;
  `Souterrain.invite(j)` → chaîne ou null ; `Souterrain.agir(j)` → bool.

- [ ] **Étape 1 : les juges qui échouent** — à la fin de `tests/test_souterrain_js.py` :

```python
ASCENSEUR = """
  async function dansLaPieceDuGarage(L, o) {
    const porte = L.Monde.carte.def.portes.find(function (q) { return q.lieu === 'garage' && q.interieur; });
    const j = L.B.joueur;
    j.x = porte.x * TT + 8; j.y = (porte.y + 1) * TT + 10; L.Entites.indexer();
    L.Jeu.entrer(porte);
    for (let i = 0; i < 120 && (L.B.transition || !L.B.interieur); i++) o.frame(1);
  }
  function devantLAscenseurDeLaPiece(L) {
    const pt = L.B.interieur.points.find(function (p) { return p.type === 'ascenseur'; }), j = L.B.joueur;
    j.x = pt.x * TT + 8; j.y = (pt.y + 1) * TT + 8; L.Entites.regarder(j, 0, -1); L.Entites.indexer();
  }
"""


def test_l_ascenseur_descend_a_pied_et_remonte_a_la_piece_du_garage(banc):
    r = banc("async function (L, o) {" + OUTILS + ASCENSEUR + """
        L.Jeu.commencer(); proprio(L);
        const B = L.B, j = B.joueur;
        B.partie.souterrain.cases[3] = { slug: 'auto', couleur: '#27ae60', vie: 100, vole: false, aToi: true };
        await dansLaPieceDuGarage(L, o);
        devantLAscenseurDeLaPiece(L); o.frame(2);
        const inviteHaut = B.invite;
        o.tape('KeyE', 2);
        await attendreLeBloc(L, o, 'souterrain');
        const s = B.bloc.def.bloc.souterrain.ascenseur;
        const enBas = { bloc: B.bloc && B.bloc.slug, x: j.x, y: j.y, ax: (s.x + s.l / 2) * TT, ay: s.y * TT + 8,
                        chars: B.entites.filter(function (e) { return e.type === 'vehicule'; }).length };
        // Face aux portes, en bas : ACTION remonte.
        L.Entites.regarder(j, 0, 1); o.frame(2);
        const inviteBas = B.invite;
        o.tape('KeyE', 2);
        for (let i = 0; i < 200 && (B.transition || !B.interieur); i++) { o.frame(1); if (i % 10 === 0) await o.attendre(); }
        return { inviteHaut: inviteHaut, enBas: enBas, inviteBas: inviteBas,
                 enHaut: { piece: B.interieur && B.interieur.slug, bloc: !!B.bloc }, garde: B.partie.souterrain.cases[3] };
    }""")
    assert "ASCENSEUR" in (r["inviteHaut"] or ""), r
    b = r["enBas"]
    assert b["bloc"] == "souterrain" and abs(b["x"] - b["ax"]) < 2 and abs(b["y"] - b["ay"]) < 2, b
    assert b["chars"] == 1, "le char rangé attend sur sa case"
    assert "ASCENSEUR" in (r["inviteBas"] or ""), r
    assert r["enHaut"] == {"piece": "garage", "bloc": False}, r
    assert r["garde"] and r["garde"]["couleur"] == "#27ae60", "remonter par l'ascenseur ne perd pas le char"


def test_sans_le_garage_l_ascenseur_ne_descend_pas(banc):
    r = banc("async function (L, o) {" + OUTILS + ASCENSEUR + """
        L.Jeu.commencer();
        await dansLaPieceDuGarage(L, o);
        devantLAscenseurDeLaPiece(L); o.frame(2);
        o.tape('KeyE', 2);
        for (let i = 0; i < 60; i++) o.frame(1);
        return { piece: L.B.interieur && L.B.interieur.slug, bloc: !!L.B.bloc, msg: L.B.msg };
    }""")
    assert r["piece"] == "garage" and r["bloc"] is False, r
    assert "GARAGE" in r["msg"], r
```

- [ ] **Étape 2 : les voir rougir** — FAIL : l'invite est `ASCENSEUR` en majuscules de repli ou rien, et ACTION
  n'ouvre rien.

- [ ] **Étape 3 : les deux sens** — `static/js/souterrain.js`, avant le `return` :

```js
  //: Le fondu de l'ascenseur : celui d'un etage (`Jeu`, FONDU_ETAGE).
  const FONDU_ASCENSEUR = [20, 16];

  /** De la piece du garage, a pied : au noir, la piece se quitte et le sous-sol se charge, et l'on sort de
      l'ascenseur du −1. Le noir tient le temps que la carte arrive (`attente`). */
  function descendreAPied() {
    if (!Missions.possede(Missions.proprieteDe('garage'))) {
      Hud.message('LE SOUS-SOL EST AU PROPRIO — ACHÈTE LE GARAGE', 150); Son.SFX.erreur();
      return true;
    }
    Blocs.charger(SLUG);
    Jeu.transiter([1, 0, 24], function () {
      const def = Blocs.cartes[SLUG];
      if (!def) return;
      Jeu.quitterLaPiece();
      const s = def.bloc.souterrain.ascenseur;
      if (Blocs.entrerAuNoir(SLUG, { x: (s.x + s.l / 2) * TT, y: s.y * TT + 8 })) Entites.regarder(B.joueur, 0, -1);
    }, null, function () { return !Blocs.cartes[SLUG]; });
    return true;
  }

  /** Du sous-sol, a pied : au noir, on range ses chars (`Jeu.revenirEnVille` → `quitterLeBloc`), et l'on sort de
      l'ascenseur de la piece du garage. */
  function monterAPied() {
    Jeu.transiter(FONDU_ASCENSEUR, function () {
      Jeu.revenirEnVille();
      const porte = (Monde.carte.def.portes || []).find(function (q) { return q.lieu === 'garage' && q.interieur; });
      const piece = porte && Jeu.chargerPiece(porte);
      if (!piece) return;
      const j = B.joueur, pt = (piece.interieur.points || []).find(function (p) { return p.type === 'ascenseur'; });
      if (pt) { j.x = pt.x * TT + 8; j.y = (pt.y + 1) * TT + 8; }
      Entites.regarder(j, 0, 1);
      Monde.centrerCamera(j.x, j.y);
      Hud.message(piece.interieur.nom.toUpperCase(), 120);
    });
    return true;
  }

  /** Au sous-sol, a pied, dans la rangee devant les portes de l'ascenseur ? */
  function sousLaMain(j) {
    if (!ici() || !j || j.dansVehicule) return false;
    const s = B.bloc.def.bloc.souterrain.ascenseur, tx = Math.floor(j.x / TT), ty = Math.floor(j.y / TT);
    return ty === s.y && tx >= s.x && tx < s.x + s.l;
  }
  function invite(j) { return sousLaMain(j) ? 'L’ASCENSEUR' : null; }
  function agir(j) { return sousLaMain(j) ? monterAPied() : false; }
```

et l'objet rendu gagne `descendreAPied, monterAPied, sousLaMain, invite, agir`.

- [ ] **Étape 4 : les brancher** — `static/js/missions.js`.

Dans `LIBELLES`, après `catalogue: 'LE CATALOGUE', jukebox: 'LE JUKE-BOX',` :

```js
    // Le garage souterrain : l'ascenseur de la piece du garage (`Souterrain`).
    ascenseur: 'L’ASCENSEUR',
```

Dans `utiliserPoint`, après `if (point.type === 'jukebox') return Decoration.jukebox();` :

```js
    if (point.type === 'ascenseur') return Souterrain.descendreAPied();
```

Dans `interagir`, après `if (Cabane.sousLaMain(j)) return Cabane.agir(j);` :

```js
    // L'ascenseur du garage souterrain, en bas : il remonte a la piece du garage (`Souterrain`).
    if (Souterrain.sousLaMain(j)) return Souterrain.agir(j);
```

Dans `majInvite`, à l'endroit où l'invite de la cabane est lue (`const cabane = Cabane.invite(j);`), juste avant :

```js
    const ascenseur = Souterrain.invite(j);
    if (ascenseur) { B.invite = ascenseur; return; }
```

- [ ] **Étape 5 : au vert**

Run: `…pytest tests/test_souterrain_js.py tests/test_interieurs_js.py tests/test_braquage_js.py -q`
Expected: PASS.

- [ ] **Étape 6 : muter** — dans `interagir`, retirer la ligne de l'ascenseur : le premier juge rougit (on reste
  en bas) ; remettre.

- [ ] **Étape 7 : commiter**

```bash
git add static/js/souterrain.js static/js/missions.js tests/test_souterrain_js.py
```
```bash
git commit -m "feat(souterrain): l'ascenseur, de la pièce du garage au −1 et retour"
```

---

### Tâche 7 : à l'abri, et ce qui se peint

**Fichiers :**
- Modifier : `static/js/monde.js` (`charger` : `abrite` ; `aLAbri` ; `ambianceVue` ; l'export)
- Modifier : `static/js/pluie.js:61` (`intensite`), `static/js/neige.js:47` (`intensite`)
- Modifier : `static/js/jeu.js` (`rendre` : la pluie, la neige, et `Souterrain.dessiner`)
- Modifier : `static/js/souterrain.js` (`dessiner`)
- Modifier : `tests/test_souterrain_js.py`

**Interfaces :**
- Produit : `Monde.aLAbri()` → vrai dans une pièce ou dans un bloc `abrite` ; `Souterrain.dessiner(ctx, cam)`.

- [ ] **Étape 1 : le juge qui échoue** — à la fin de `tests/test_souterrain_js.py` :

```python
def test_au_sous_sol_ni_pluie_ni_neige_ni_nuit(banc):
    r = banc("async function (L, o) {" + OUTILS + """
        L.Jeu.commencer(); proprio(L);
        const B = L.B;
        viderLaBaie(L);
        L.Blocs.sauter('souterrain', null, null); await attendreLeBloc(L, o, 'souterrain');
        // En pleine nuit de janvier, un jour de tempête (la partie commence en janvier ; la tempête, le jour 2).
        B.partie.jour = 2; B.partie.heure = 0.02;
        o.frame(2);
        return { abri: L.Monde.aLAbri(), neige: L.Neige.intensite(), pluie: L.Pluie.intensite(),
                 nuit: L.Monde.ambianceVue().alpha };
    }""")
    assert r["abri"] is True, r
    assert r["neige"] == 0 and r["pluie"] == 0, r
    assert r["nuit"] < 0.1, f"pas de nuit au sous-sol : {r}"
```

- [ ] **Étape 2 : le voir rougir** — FAIL : `Monde.aLAbri is not a function`.

- [ ] **Étape 3 : l'abri** — `static/js/monde.js`.

Dans `charger`, à côté de `materiaux: def.materiaux || null,` :

```js
      // Sous terre (le garage souterrain, `app/blocs/souterrain.py`) : ni pluie, ni neige, ni nuit (`aLAbri`).
      abrite: !!(def.bloc && def.bloc.abrite),
```

Après `ambianceVue`, et `ambianceVue` elle-même :

```js
  function ambianceVue() {
    if ((carte && (carte.interieur || carte.abrite)) || !B.partie || typeof Saisons === 'undefined') return ambiance();
    return ambiance(Saisons.heureDeLumiere(B.partie.jour, B.partie.heure));
  }

  /** A l'abri du ciel : dans une piece, ou dans un bloc sous terre (`abrite`). */
  function aLAbri() { return !!B.interieur || !!(carte && carte.abrite); }
```

Ajouter `aLAbri` à l'objet rendu par `Monde`. ⚠️ Vérifier que `ambiance()` sans heure rend bien une lumière de jour
(`alpha` bas) : c'est ce que les pièces utilisent déjà.

`static/js/pluie.js:61` :

```js
  function intensite() { return !B.partie || Monde.aLAbri() ? 0 : intensiteA(B.partie.jour, B.partie.heure); }
```

`static/js/neige.js:47` (dans `intensite`) :

```js
    if (!B.partie || Monde.aLAbri()) return 0;
```

Dans `Jeu.rendre` (`static/js/jeu.js`), les quatre lignes de ciel passent à l'abri :

```js
    if (!Monde.aLAbri()) Neige.dessinerSol(ctx, vue);     // la neige au sol, SOUS les rails et les gens
    if (!Monde.aLAbri()) Pluie.dessinerSol(ctx, vue);     // la rue mouillee, les flaques, la gadoue d'avril (les saisons, lot 2)
    if (!Monde.aLAbri()) Neige.dessinerTempete(ctx);
    if (!Monde.aLAbri()) Pluie.dessiner(ctx);             // la pluie qui tombe, et l'eclair de l'orage
```

(garder les commentaires existants de chaque ligne).

- [ ] **Étape 4 : ce qui se peint** — `static/js/souterrain.js`, avant le `return` :

```js
  /** Les numeros des cases (P1…), et les portes de l'ascenseur : en bas, sur le mur sud (les `D` du plan sont
      deja des portes de platre, on y ajoute le bouton) ; en haut, sur le mur nord de la piece du garage, au-dessus
      du point `ascenseur`. Rien ailleurs. */
  function dessiner(ctx, cam) {
    if (ici()) {
      const s = B.bloc.def.bloc.souterrain;
      s.cases.forEach(function (q) {
        const x = Math.round((q.x + q.l / 2) * TT - cam.x) - 6, y = Math.round((q.y + q.h) * TT - cam.y) - 12;
        if (x < -20 || x > VW + 20 || y < -20 || y > VH + 20) return;
        Atlas.texte(ctx, 'P' + q.n, x, y, '#f4e4c1', 1);
      });
      const a = s.ascenseur;
      portes(ctx, Math.round(a.x * TT - cam.x), Math.round((a.y + 1) * TT - cam.y), a.l * TT);
      return;
    }
    if (B.interieur && B.interieur.slug === 'garage') {
      const pt = (B.interieur.points || []).find(function (p) { return p.type === 'ascenseur'; });
      if (pt) portes(ctx, Math.round(pt.x * TT - cam.x), Math.round((pt.y - 1) * TT - cam.y), TT);
    }
  }

  /** Deux battants d'acier brosse, leur joint, et le bouton allume. */
  function portes(ctx, x, y, l) {
    ctx.fillStyle = '#5d6168'; ctx.fillRect(x + 1, y + 1, l - 2, TT - 2);
    ctx.fillStyle = '#8a9099'; ctx.fillRect(x + 2, y + 2, l / 2 - 3, TT - 4); ctx.fillRect(x + l / 2 + 1, y + 2, l / 2 - 3, TT - 4);
    ctx.fillStyle = '#2b2e33'; ctx.fillRect(x + l / 2 - 1, y + 2, 2, TT - 4);
    ctx.fillStyle = '#f5c542'; ctx.fillRect(x + l - 3, y + TT / 2 - 1, 2, 2);
    B.stats.rects += 5;
  }
```

et l'objet rendu gagne `dessiner`. Dans `Jeu.rendre`, juste après `if (B.interieur) Monde.dessinerBarrieres(ctx, vue);` :

```js
    Souterrain.dessiner(ctx, vue);   // les numeros des cases, et les portes de l'ascenseur (en bas et dans la piece du garage)
```

- [ ] **Étape 5 : au vert, et le ciel d'avant aussi**

Run: `…pytest tests/test_souterrain_js.py tests/test_pluie.py tests/test_pluie_js.py tests/test_neige.py tests/test_neige_js.py tests/test_saisons.py tests/test_blocs_js.py -q`
Expected: PASS.

- [ ] **Étape 6 : muter** — `aLAbri` rendu à `!!B.interieur` : le juge rougit ; remettre.

- [ ] **Étape 7 : regarder** — capture Chromium du −1 et de la pièce du garage (la recette de la mémoire « Capturer
  une pièce du jeu ») : un script dans le scratchpad, lancé avec `/Users/martingagne/dev/bandini/.venv/bin/python`
  depuis le worktree :

```python
import logging, sys, tempfile, threading
sys.path.insert(0, ".")
from werkzeug.serving import make_server
from playwright.sync_api import sync_playwright
from config import Config
from app import create_app

C = type("C", (Config,), {"DONNEES_DIR": tempfile.mkdtemp()})
logging.getLogger("werkzeug").setLevel(logging.ERROR)
srv = make_server("127.0.0.1", 0, create_app(C), threaded=True)
threading.Thread(target=srv.serve_forever, daemon=True).start()
with sync_playwright() as p:
    page = p.chromium.launch().new_page(viewport={"width": 960, "height": 540})
    page.goto(f"http://127.0.0.1:{srv.server_port}/")
    page.wait_for_selector('#bandini[data-etat="titre"]')
    page.click("#bouton-jouer")
    page.evaluate("window.BANDINI.Histoire.passerOuverture()")
    page.wait_for_function("!window.BANDINI.B.ouverture")
    page.evaluate("""() => { const L = window.BANDINI, p = L.B.partie;
        p.proprietes.garage = { jour: p.jour, caisse: 0 }; p.jour = 22; p.heure = 0.5;
        p.souterrain.cases[0] = { slug: 'auto', couleur: '#c0392b', vie: 100, aToi: true };
        p.souterrain.cases[6] = { slug: 'camion', couleur: '#2e86de', vie: 120, aToi: true };
        L.Blocs.sauter('souterrain', { x: 15 * 16 + 8, y: 8 * 16 }, null); }""")
    page.wait_for_function("window.BANDINI.B.bloc && !window.BANDINI.B.transition", timeout=15000)
    page.wait_for_timeout(1500)
    page.screenshot(path="captures/souterrain-moins-1.png")
    srv.shutdown()
```

  Lire la capture (`Read` sur le PNG) : les cases peintes, les numéros lisibles, les murs en béton de pièce (pas de
  tôle de toit), les portes de l'ascenseur au mur sud. Refaire pour la pièce du garage (`L.Jeu.entrer` sur la porte
  `lieu === 'garage'`). Copier dans `captures/` du dépôt principal et `open` pour Martin.

- [ ] **Étape 8 : commiter**

```bash
git add static/js/monde.js static/js/pluie.js static/js/neige.js static/js/jeu.js static/js/souterrain.js tests/test_souterrain_js.py
```
```bash
git commit -m "feat(souterrain): à l'abri du ciel, les numéros des cases et les portes de l'ascenseur"
```

---

### Tâche 8 : la doc, les juges voisins, atterrir

**Fichiers :**
- Modifier : `docs/architecture.md` (deux lignes : `app/blocs/souterrain.py`, `static/js/souterrain.js`)
- Modifier : `docs/jalons/le-grand-garage-souterrain.md` (`## Notes` : la vague 1 livrée)
- Modifier : `docs/plan.md` (la cellule d'état : « ✅ vague 1 livrée : … ; reste la vague 2, le −2 »)

- [ ] **Étape 1 : la carte du dépôt** — dans `docs/architecture.md`, une ligne pour chaque fichier neuf, au format
  des voisines (`blocs/cineparc.py`, `cabane.js`) : ce que le module fait, et ses juges (`test_souterrain.py`,
  `test_souterrain_js.py`). `…python scripts/verifier_carte_du_depot.py` doit passer.

- [ ] **Étape 2 : les juges voisins, d'un coup**

Run: `…pytest tests/test_souterrain.py tests/test_souterrain_js.py tests/test_blocs.py tests/test_blocs_js.py tests/test_rang.py tests/test_nord.py tests/test_definitions.py tests/test_cineparc_js.py tests/test_garage_js.py tests/test_poste_et_garage_js.py tests/test_garages_ou_l_on_entre_js.py tests/test_interieurs.py tests/test_interieurs_js.py tests/test_braquage_js.py -q`
puis `cd <worktree> && UV_PROJECT_ENVIRONMENT=/Users/martingagne/dev/bandini/.venv uv run ruff check .`
Expected: PASS, et ruff muet. Un rouge qui n'est pas du jalon : le rejouer sur la base (worktree détaché sur le
commit d'avant) avant de conclure.

- [ ] **Étape 3 : la note** — sous `## Notes` du jalon : ce qui est livré, les écarts à la fiche, les pièges
  rencontrés ; la cellule du plan dit la vague 1 livrée, la ligne reste ⬜ (la vague 2 reste).
  `…python scripts/verifier_table_des_jalons.py` : code 0.

- [ ] **Étape 4 : commiter, puis atterrir** (arbre partagé propre, `dev` rejoué d'abord : `git rebase dev` dans le
  worktree si `dev` a bougé, juges ciblés relancés) :

```bash
git add docs/architecture.md docs/jalons/le-grand-garage-souterrain.md docs/plan.md
```
```bash
git commit -m "docs: le grand garage souterrain — vague 1 livrée (le −1, le rideau, l'ascenseur, la mémoire des chars)"
```
```bash
cd /Users/martingagne/dev/bandini && git merge --ff-only claude/garage-souterrain
```

  Puis la suite complète, détachée, après l'atterrissage (mémoire « Atterrir avant la suite complète »).

## Notes

**Vague 1 livrée (30 sept. 2026) : le −1.** Au rideau du Garage Rocco Bandini, DESCENDRE AU SOUS-SOL (en deuxième
ligne, REPARTIR reste en tête) ; l'ascenseur de la pièce du garage, dans les deux sens ; dix cases P1 à P10 ; les
chars rangés vivent dans `partie.souterrain.cases` et reviennent avec leur couleur, leurs pièces, leurs bosses et
leur marque de vol, recharge comprise ; Ti-Guy gare ce qu'on laisse dans l'allée ; ni pluie, ni neige, ni nuit, ni
froid en bas. Juges : `tests/test_souterrain.py` (9), `tests/test_souterrain_js.py` (19), chacun vu rougir.

Ce qui a changé en route (le registre d'exécution les appelle des « rulings ») :

- **Un sous-sol n'est pas un bloc de bord de ville** : `blocs.SOUS_SOLS`, `passage: None`, un `seuil` (le rideau
  devant lequel on ressort, `Blocs.retourEnVille`). Tout ce qui lisait `b.passage` d'un bloc du paquet est gardé
  (`Blocs.maj`, `ouvertures`, `entrerAuNoir`, `Histoire.passageDuBloc`, `Jeu.sortirDuBloc`).
- **Pas de garde du rideau pendant la descente** : le jeu est figé pendant un fondu (`Jeu.maj`), la garde prévue ne
  se voyait pas — retirée ; le juge reste, sentinelle du gel.
- **« À l'abri » est une règle, pas un dessin** : `Monde.aLAbri()` (une pièce, ou un bloc `abrite`) garde la pluie,
  la neige, le verglas, l'adhérence et le freinage, le pas dans la neige, le froid de Rosa (`majFroid`,
  `hiverAPied`) et la lumière (`ambiance()` sans heure y rend le jour, comme dans une pièce — `estNuit()` y est donc
  faux). La relecture finale a vu la route glisser au sous-sol alors que l'écran n'y montrait aucune neige.
- **La fourrière ne descend pas** : l'allée est de l'asphalte, et la remorqueuse saisissait en 45 s le char que Ti-Guy
  devait garer (relecture finale ; `majMalGares` se tait au sous-sol).
- **L'ascenseur refuse les étoiles**, comme le rideau : sinon la poursuite suivait au bord du bloc (relecture finale).
- Deux juges du rideau descendaient d'UNE ligne vers VENDRE ; ils descendent maintenant au bouton jusqu'à VENDRE.

Laissé pour plus tard (mineurs de la relecture) : un char de trop au sous-sol (seulement par la triche qui en fait
apparaître un) disparaît sans un mot ; la triche ENDROITS CLÉS y mène sans posséder le garage ; aucun juge ne joue la
descente depuis l'atelier rideau baissé (le chemin est lu correct).

**Deux rangées face à face (30 sept. 2026, retour de Martin sur la vague 1 : « le stationnement me semble beaucoup
trop grand. on pourrait mettre 2 rangées face à face »)** : le −1 passe de 32 × 18 à 17 × 14 — P1 à P5 au nord, le
nez au mur, P6 à P10 en face au sud, le nez au mur sud, une allée de cinq tuiles ; la rampe au nord-est, l'ascenseur
au sud-est. Plus petit que l'écran, il se centre avec du noir autour, comme une pièce (`Monde.limitesCamera`).
⚠️ Pour la vague 2 : le −2 ne peut plus être un deuxième CADRE de la même carte (le juge des blocs veut chaque cadre
plus grand que l'écran, sinon on voit l'étage d'à côté) — un deuxième sous-sol à part, ou des cadres séparés par du
noir, à trancher alors.

Reste la **vague 2** : le −2 (P11 à P20, 10 000 $, AGRANDIR LE SOUS-SOL, la grille), la rampe intérieure au volant, et
les sons (l'ascenseur, l'écho des pneus, les néons).

**Plan de la vague 2 (2 oct. 2026)** — tranché sur la question laissée ouverte : **un deuxième sous-sol à part**
(`souterrain_2`, 17 × 14 comme le −1), pas un deuxième cadre ; le juge « chaque cadre plus grand que l'écran » ne bouge
pas.

- **La rampe intérieure** : au mur est du −1 (une ouverture de trois tuiles dans l'allée), elle descend au −2 ; au mur
  est du −2, elle remonte au −1. Au volant ou à pied, au noir, cap gardé (`Jeu.changerDeBloc`, neuf : d'un bloc à
  l'autre sans repasser par la ville). Le −2 n'a pas d'autre sortie que cette rampe et l'ascenseur.
- **La grille** : tant que le −2 n'est pas acheté, la rampe du −1 est fermée — une grille peinte sur l'ouverture, et
  pousser contre ne mène nulle part.
- **AGRANDIR LE SOUS-SOL — 10 000 $** au comptoir de Ti-Guy, dans la pièce du garage (garage à toi, −2 pas encore
  ouvert) : `partie.souterrain.niveaux = 2`.
- **Les cases** : P11 à P20 sont les rangs 10 à 19 de `partie.souterrain.cases` ; chaque niveau range et garnit les
  siens (`q.n − 1`), et Ti-Guy gare ce qui reste dans l'allée sur une case libre de CE niveau, sinon de l'autre.
- **L'ascenseur dessert les trois arrêts** une fois le −2 ouvert : un petit menu (GARAGE · −1 · −2) au lieu d'un
  aller simple.
- **Les sons** (ElevenLabs, dans `audio.LIEUX`) : le ding et le moteur de l'ascenseur à chaque trajet ; les pneus qui
  crissent en écho à chaque rampe ; le bourdonnement des néons en fond, au sous-sol seulement.

**Vague 2 livrée (2 oct. 2026) : le −2.** AGRANDIR LE SOUS-SOL — 10 000 $ au comptoir de Ti-Guy (`economie.TARIFS
["sous_sol_2"]`, `Souterrain.itemAgrandir`) ouvre dix cases de plus, P11 à P20, dans un **deuxième sous-sol à part**
(`souterrain_2`, le même béton, sans rampe vers la rue). On y descend au volant par la **rampe intérieure** du mur est
du −1 — une grille et son étiquette « −2 » tant qu'il n'est pas acheté — ou par l'ascenseur, qui dessert alors trois
arrêts (GARAGE · −1 · −2, un petit menu ; avec un seul niveau, l'aller simple de la vague 1). La rampe du −2 remonte au
−1. Les sons, générés par ElevenLabs (lieu `souterrain`, chargé dans la pièce du garage ou en bas) : le ding et le
moteur de l'ascenseur à chaque trajet, les pneus qui crissent en écho à chaque rampe (et à la descente du rideau), et
les néons qui bourdonnent en fond, au sous-sol seulement. Juges : `tests/test_souterrain.py` (14, dont 4 du −2) et
`tests/test_souterrain_deux_js.py` (9) ; dix-huit mutations, toutes mordues (celle qui garde les vieilles cases d'un
niveau, par le juge de la vague 1 « le char qu'on remonte quitte le sous-sol »).

Ce qui a changé en route :

- **D'un bloc à l'autre** (`Jeu.changerDeBloc`) : au noir, le bloc d'où l'on part se range (`quitterLeBloc` : ses chars
  dans la partie), l'autre se charge et l'on y est, cap donné, au volant comme à pied. Un `retour` peut mener à un
  autre bloc (`vers`), et un bloc a ses `rampes` (`Blocs.maj` ; GPS : « Vers la rampe »).
- **Chaque niveau range SES cases** (`q.n − 1` : P11 est le rang 10) et laisse celles de l'autre telles quelles ; Ti-Guy
  gare ce qui reste dans l'allée sur une case libre de ce niveau, sinon de l'autre.
- **Le signe moins (−) se dessine** : la police pixel n'avait que le trait d'union ; `Atlas` le remplace, comme le tiret
  cadratin.
