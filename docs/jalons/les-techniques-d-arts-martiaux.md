# Les techniques d'arts martiaux : le répertoire

← [le plan](../plan.md) · [les jalons livrés](README.md)

## Fiche

Demande de Martin (25 sept. 2026) : « je veux des animations variées pour les coups et je veux des coups de
pieds et des projections et autres qu'on peut apprendre dans une école d'arts martiaux. »

Le premier de trois jalons : **le répertoire** (celui-ci), puis [le dojo](le-dojo-du-quartier.md#fiche) où on
l'apprend, puis [l'école rivale](l-ecole-rivale.md#fiche) qui le connaît aussi. Tranché avec Martin le 25 sept. :
un dojo DANS la ville ; un bouton SAISIR neuf ; un mélange de styles (boxe, karaté, judo, jiu-jitsu) aux noms
**en français** ; les poings de rue varient pour tout le monde, pieds et projections au joueur (et au gang de
l'école rivale) ; l'animation est **hybride** (voir plus bas).

- ⚠️ **Mesuré avant** : un coup, pour tout le monde, c'est UNE pose `frappe_<face>` et un élan de ±3 px
  (`Entites.nomDePose`, `Entites.pose`) — trois temps (`anticipation` → `actif` → `repos`) lus dans `armes.py`,
  plus le coup fort chargé. Aucun coup de pied, aucune projection dans l'historique (`git log --all`).

### La grammaire des boutons

- **FRAPPE en tapes** : un enchaînement ; chaque tape dans la fenêtre de rythme (≈ 0,4 s) passe au maillon
  suivant. **La chaîne s'allonge avec ce qu'on a appris** : chaque cours ajoute un maillon au bout. Une tape
  donnée pendant le coup en cours est **gardée en réserve** (une seule), sinon on rate une tape sur deux.
- **FRAPPE tenue** : le coup chargé. **FRAPPE en pleine course** : le coup sauté. **FRAPPE au sortir d'une
  roulade** : le balayage.
- **SAISIR** (neuf) : on attrape l'ennemi devant soi et on le tient ≈ 1,2 s ; **la direction du stick,
  relative à l'axe joueur → cible, choisit la projection** (vers l'avant, vers soi, de côté). FRAPPE dans la
  prise : des coups de genou. Relâcher sans rien : on le **repousse**. Rien pendant 1,2 s : il se dégage.
- **SAISIR tenu dans le dos** (écart de plus de 120° avec sa face) : l'étranglement. **SAISIR pendant que
  l'ennemi arme son coup** (sa phase `anticipation`, portée comprise) : la parade-contre.
- ⚠️ **Où va SAISIR** : clavier **U** — ni G, ni R, I, O, L, qui épèlent la suite secrète `RIGOLO`
  (`Jeu.SEQUENCE_DEBUG`) ; manette **RB (5)**, qui ne faisait que doubler FRAPPE ; l'écran MANETTE l'apprend
  comme les autres, et le tactile a son bouton. La prise d'otage reste sur ACTION.
- ⚠️ **Une arme de mêlée en main** (batte, couteau) : FRAPPE reste le coup de l'arme ; SAISIR marche toujours.
  Mains nues et poing américain passent par les techniques.

### Le répertoire

**Les poings de rue** — gratuits, pour tout le monde (passants et gangs compris) :

| Geste | Technique |
|---|---|
| FRAPPE 1, 2, 3 | direct du gauche → direct du droit → crochet |
| FRAPPE collé à la cible | coup de genou |
| SAISIR, relâcher | repousser (il titube) |
| SAISIR + FRAPPE | genoux dans la prise |

Un passant tire sa variante **à l'empreinte** — `(e.id + e.coups) % 3`, le genou s'il est collé — jamais par
`B.rng()`, qui décalerait tout le hasard de la ville.

**Les cours du dojo** — dix, au joueur seulement :

| Style | Technique | Geste | Ce qu'elle apporte |
|---|---|---|---|
| Boxe | uppercut | 4e tape | renverse |
| Karaté | coup de pied circulaire | 5e tape | large arc, deux ennemis |
| Karaté | coup de pied de côté | FRAPPE tenue | longue portée, l'envoie loin |
| Karaté | coup de pied sauté | FRAPPE en course | ferme la distance |
| Karaté | balayage | FRAPPE au sortir d'une roulade | couche tout ce qui est autour |
| Judo | projection de hanche | prise + stick vers l'avant | il passe par-dessus, retombe devant |
| Judo | grand fauchage | prise + stick vers soi | il tombe sur le dos, sur place |
| Judo | sacrifice en cercle | prise + stick de côté | on tombe, pied au ventre, il vole par-dessus |
| Jiu-jitsu | retournement du poignet | SAISIR pendant qu'il arme | parade-contre, il roule au sol |
| Jiu-jitsu | étranglement | SAISIR tenu, dans le dos | l'assomme **en silence** |

**Pourquoi les apprendre** : les pieds portent plus loin mais partent plus lentement ; les projections
**assomment sans faire saigner** (moins d'étoiles que cogner) ; l'étranglement, c'est la furtivité.

### L'animation : hybride

- **Une dizaine de poses clés**, dessinées une fois par face (bas, haut, côté ; la gauche est le miroir) dans
  le squelette `homme` de `garderobe.js` — les tenues les habillent toutes seules : poing avant (existe :
  `frappe`), poing arrière, crochet, genou, pied de face, pied de côté, saisie à deux mains, charge sur la
  hanche, au sol sur le dos, accroupi. **10 poses × 3 faces.** Le circulaire, l'uppercut et le coup sauté
  sont ces poses plus une rotation ou une hauteur.
- **Chaque technique est une ligne de temps** : `[(pose, images, dx, dy, rot, z), …]`, une seule étape
  marquée `actif`.
- **La victime projetée** (`e.vol`) : un arc en hauteur (`z = 4h·t(1−t)`), un demi-tour (un tour pour le
  sacrifice), la poussière et la secousse à l'atterrissage, puis couchée. ⚠️ **Le point de chute se raccourcit
  jusqu'à la dernière tuile marchable** : on ne projette personne dans un mur.
- `Entites.nomDePose` demande `tech_<pose>_<face>`, puis `frappe_<face>`, puis la face : un sprite dessiné à
  la main qui n'a pas les poses frappe comme aujourd'hui.

### La mécanique

- **`app/techniques.py`** (frère de `armes.py`) : `slug`, `nom`, `style`, `geste` (`tape`, `tenue`, `course`,
  `roulade`, `prise_avant`, `prise_vers_soi`, `prise_cote`, `contre`, `dos`), `rang` (sa place dans la
  chaîne), `gratuite`, `prix`, `degats`, `portee`, `arc`, `renverse`, `assomme`, `projete` (px),
  `silencieuse`, `sans_sang`, et `temps` (la ligne de temps). Servi par `definitions.py` →
  `B.defs.techniques`.
- **`static/js/techniques.js`** (neuf — `combat.js` fait déjà 1 080 lignes) : `choisir(e, geste)` **pure**
  (ce que `e` sait + son contexte → un slug) ; `demarrer(e, slug)` ; `maj(e)` avance la ligne de temps et
  applique l'arc à l'étape `actif` (`arcDeMelee`).
- ⚠️ **`j.prise`, pas `j.saisie`** : `saisie` est déjà la prise d'otage (`Combat.majSaisie`). La cible passe à
  l'état `tenu`, figée face à nous.
- ⚠️ **`Entites.blesser` fait TOUJOURS saigner un passant** (`sang(...)`) et **alerte toujours** : deux
  options neuves, `sans_sang` (les projections) et `silencieuse` (l'étranglement : ni cri ni `alerter` ;
  `Police.quelqu_un_voit` décide seul s'il y a un crime).
- **Ce qu'on sait** : `B.partie.techniques = {slug: true}`, sauvé avec la partie. L'onglet TRICHES gagne
  « TOUTES LES TECHNIQUES » — c'est par là qu'on joue avec avant que le dojo existe.
- **Le nom** de la technique apprise s'affiche brièvement quand elle porte (« GRAND FAUCHAGE ! »).
- **Trois bruitages** ElevenLabs au catalogue audio : le pied qui fend l'air, le corps qui tombe,
  l'étranglement.

### Les juges

- **Python** : chaque pose citée existe dans le squelette `homme` pour les trois faces ; une seule étape
  `actif` par technique ; pas deux techniques sur le même geste et le même rang ; portée ≤ 240 (la borne de
  `base.js`, comme `test_armes`).
- **Banc Node**, un par geste, **joués au bouton** (pas en appelant la fonction) : `choisir` rend le bon slug ;
  la tape en réserve enchaîne ; une projection vers un mur tombe sur une tuile libre ; un étranglement non vu
  n'alerte personne ; un passant rejoue la même suite de coups pour la même empreinte. Chacun **muté** une
  fois pour le voir rougir.
- **Capture Chromium** des 30 poses et d'une projection en vol, regardée avant de livrer.
- ⚠️ Les juges « ce module ne déplace rien » : aucun dé, aucun id global consommé au démarrage.

### Le plan d'exécution

Approuvé par Martin le 25 sept. 2026. Huit tâches, chacune jouable et jugée ; on coche au fil de l'eau.

**Contraintes de toutes les tâches**

- Tout se fait dans un **worktree** du `dev` local (`git worktree add --detach <scratchpad>/wt dev`) ;
  pytest avec `UV_PROJECT_ENVIRONMENT=/Users/martingagne/dev/bandini/.venv uv run --frozen pytest -q …` ;
  on atterrit par `git merge --ff-only` depuis `~/dev/bandini` (cherry-pick sur `dev` s'il a bougé).
- `git add` et `git commit` en **deux commandes** (le garde-fou juge l'index). Jamais `git add -A`,
  jamais `git stash`. Le WIP se range sous `refs/wip/arts-martiaux`.
- `uv run ruff check .` avant d'atterrir. Vider `__pycache__` après une mutation Python.
- **Aucun `B.rng()`** dans le module neuf : les choix des passants se tirent à l'empreinte.
- Un juge se joue **au bouton** (`o.touche('KeyU')`, `o.frame`, `o.relacher`), pas en appelant la fonction.
- Chaque juge neuf est **muté** une fois (retirer la règle, le voir rougir, la remettre).
- Les textes du jeu : français, accents compris, majuscules au HUD (`GRAND FAUCHAGE !`).
- Une image : 60 par seconde. Portée ≤ 240 px.

**À surveiller en relecture** — ce que la fiche implique sans qu'une tâche le dise d'elle-même :

1. **Une projection vers l'eau** : la victime retombe sur la dernière tuile sèche, jamais dans la baie
   (`Monde.estEau`), comme devant un mur — juge à la tâche 5.
2. **Une vieille partie** sans `techniques` : `Sauvegarde.completer` lui donne `{}` ; aucun plantage
   au premier coup — juge à la tâche 4.
3. **Une disposition de manette sauvée avant SAISIR** (`options.manette`) : SAISIR retombe sur le défaut
   du profil au lieu de n'avoir aucun bouton — juge à la tâche 3.
4. **La prise pendant une épreuve, la roue ouverte, au volant, sur une clôture** : SAISIR ne fait rien
   (les mêmes gardes que `majGestes`) — juge à la tâche 5.
5. **La cible qui meurt, part en char ou se fait renverser pendant qu'on la tient** : la prise se lâche,
   personne ne reste figé `tenu` — juge à la tâche 5.

---

#### Tâche 1 : le catalogue des techniques

**Fichiers** — créer `app/techniques.py`, `tests/test_techniques.py` ; modifier `app/definitions.py` (la
clé `"techniques"` à côté de `"armes"`).

**Produit** — `techniques.CATALOGUE: list[Technique]`, `techniques.POSES`, `techniques.GESTES`,
`techniques.par_slug(slug)`, `techniques.chaine()` (les techniques `tape` par rang) ; au client,
`B.defs.techniques` (la liste, telle quelle).

- [ ] **Le juge d'abord** — `tests/test_techniques.py` :

```python
"""Les techniques d'arts martiaux — le catalogue (voir docs/jalons/les-techniques-d-arts-martiaux.md)."""

import re
from pathlib import Path

from app import techniques

RACINE = Path(__file__).resolve().parent.parent


def test_slugs_uniques_et_gestes_connus():
    slugs = [t["slug"] for t in techniques.CATALOGUE]
    assert len(slugs) == len(set(slugs))
    for t in techniques.CATALOGUE:
        assert t["geste"] in techniques.GESTES, t["slug"]
        assert t["style"] in techniques.STYLES, t["slug"]


def test_une_seule_etape_active_par_technique():
    for t in techniques.CATALOGUE:
        actives = [e for e in t["temps"] if e["actif"]]
        assert len(actives) == 1, t["slug"]
        for e in t["temps"]:
            assert e["pose"] in techniques.POSES, (t["slug"], e["pose"])
            assert e["images"] >= 1


def test_pas_deux_techniques_sur_le_meme_geste_et_le_meme_rang():
    vus = set()
    for t in techniques.CATALOGUE:
        cle = (t["geste"], t["rang"])
        assert cle not in vus, cle
        vus.add(cle)


def test_la_chaine_des_tapes_est_continue_et_commence_gratuite():
    rangs = [t["rang"] for t in techniques.chaine()]
    assert rangs == list(range(1, len(rangs) + 1))
    assert all(t["gratuite"] for t in techniques.chaine()[:3])


def test_les_cours_ont_un_prix_la_rue_est_gratuite():
    for t in techniques.CATALOGUE:
        if t["style"] == "rue":
            assert t["gratuite"] and t["prix"] == 0, t["slug"]
        else:
            assert not t["gratuite"] and t["prix"] > 0, t["slug"]


def test_aucune_portee_au_dela_de_ce_que_l_ecran_montre():
    base = (RACINE / "static" / "js" / "base.js").read_text(encoding="utf-8")
    vue = int(re.search(r"VW\s*=\s*(\d+)", base).group(1))
    for t in techniques.CATALOGUE:
        assert 0 < t["portee"] <= vue // 2, t["slug"]


def test_le_paquet_porte_les_techniques():
    from app import definitions
    assert definitions.assembler()["techniques"] == techniques.CATALOGUE
```

⚠️ Vérifier le nom de la largeur de vue dans `base.js` (`test_armes` lit la même borne : copier sa
regex si elle diffère).

- [ ] **Le voir rougir** : `… pytest -q tests/test_techniques.py` → `ModuleNotFoundError: app.techniques`.

- [ ] **Le catalogue** — `app/techniques.py` :

```python
"""Les techniques d'arts martiaux — les coups de rue et les cours du dojo.

Unités du moteur, comme `armes.py` : dégâts en points de vie, portée en pixels,
durées en images (60 par seconde). Une technique est une LIGNE DE TEMPS : une
suite d'étapes (une pose clé, sa durée, un décalage le long du regard `dx`, un
décalage vertical `dy`, une rotation `rot`, une hauteur `z`), dont UNE est
`actif` — c'est là que le coup porte, ou que la prise projette.

Les gestes (`static/js/techniques.js` choisit) :
- `tape` : FRAPPE en tapes ; `rang` est la place dans la chaîne (1, 2, 3…).
- `genou` : FRAPPE collé à la cible. `tenue` : FRAPPE tenue. `course` : FRAPPE
  en sprint. `roulade` : FRAPPE au sortir d'une roulade.
- `prise` : SAISIR relâché sans rien faire (repousser). `prise_frappe` : FRAPPE
  dans la prise. `prise_avant`, `prise_vers_soi`, `prise_cote` : le stick dans
  la prise, relatif à l'axe joueur → cible.
- `contre` : SAISIR pendant que l'ennemi arme son coup. `dos` : SAISIR tenu
  dans le dos de l'ennemi (`tenir` images).

`projete` : la distance du vol, en pixels (0 = on ne vole pas). `sans_sang` :
la victime ne saigne pas. `silencieuse` : ni cri, ni alerte autour.
"""

from __future__ import annotations

from typing import TypedDict

STYLES = ("rue", "boxe", "karate", "judo", "jiujitsu")
GESTES = ("tape", "genou", "tenue", "course", "roulade", "prise", "prise_frappe",
          "prise_avant", "prise_vers_soi", "prise_cote", "contre", "dos")
#: `debout` : la pose de marche (rien à dessiner) ; `frappe` : la pose de coup
#: qui existe déjà (`SPRITES.joueur.poses.frappe_*`). Les autres se dessinent
#: dans `sprites.js` sous `tech_<pose>_<bas|haut|cote>`.
POSES = ("debout", "frappe", "poing_arriere", "crochet", "genou", "pied_face", "pied_cote",
         "saisie", "hanche", "au_sol", "accroupi")
DESSINEES = POSES[2:]


class Etape(TypedDict):
    pose: str
    images: int
    dx: int
    dy: int
    rot: float
    z: int
    actif: bool


class Technique(TypedDict):
    slug: str
    nom: str
    style: str
    geste: str
    rang: int
    gratuite: bool
    prix: int
    degats: int
    portee: int
    arc: float
    renverse: bool
    assomme: bool
    projete: int
    tours: float
    silencieuse: bool
    sans_sang: bool
    tenir: int
    temps: list[Etape]


def _e(pose, images, *, dx=0, dy=0, rot=0.0, z=0, actif=False) -> Etape:
    return Etape(pose=pose, images=images, dx=dx, dy=dy, rot=rot, z=z, actif=actif)


def _t(slug, nom, style, geste, degats, portee, temps, *, rang=0, prix=0, arc=0.9,
       renverse=False, assomme=True, projete=0, tours=0.5, silencieuse=False,
       sans_sang=False, tenir=0) -> Technique:
    return Technique(slug=slug, nom=nom, style=style, geste=geste, rang=rang,
                     gratuite=style == "rue", prix=prix, degats=degats, portee=portee,
                     arc=arc, renverse=renverse, assomme=assomme, projete=projete,
                     tours=tours, silencieuse=silencieuse, sans_sang=sans_sang,
                     tenir=tenir, temps=temps)


CATALOGUE: list[Technique] = [
    # --- La rue : gratuite, pour tout le monde. Les poings de `armes.py` (8 de
    # dégâts, 12 px) restent la mesure : un direct EST le coup de poing d'avant.
    _t("direct_gauche", "Direct du gauche", "rue", "tape", 8, 12, rang=1, temps=[
        _e("debout", 3, dx=-1), _e("frappe", 4, dx=3, actif=True), _e("frappe", 3, dx=1), _e("debout", 2)]),
    _t("direct_droit", "Direct du droit", "rue", "tape", 8, 12, rang=2, temps=[
        _e("debout", 3, dx=-1), _e("poing_arriere", 4, dx=3, actif=True), _e("poing_arriere", 3, dx=1),
        _e("debout", 2)]),
    _t("crochet", "Crochet", "rue", "tape", 10, 12, rang=3, arc=1.4, temps=[
        _e("debout", 4, dx=-2, rot=-0.15), _e("crochet", 4, dx=2, rot=0.2, actif=True), _e("crochet", 4),
        _e("debout", 3)]),
    _t("genou", "Coup de genou", "rue", "genou", 10, 9, temps=[
        _e("debout", 3, dy=-1), _e("genou", 5, dx=2, z=2, actif=True), _e("debout", 4)]),
    _t("repousser", "Repousser", "rue", "prise", 0, 14, assomme=False, sans_sang=True, temps=[
        _e("saisie", 6, dx=3, actif=True), _e("debout", 4)]),
    _t("genoux_prise", "Genoux", "rue", "prise_frappe", 8, 14, temps=[
        _e("saisie", 2), _e("genou", 5, dx=1, z=2, actif=True), _e("saisie", 3)]),
    # --- Boxe
    _t("uppercut", "Uppercut", "boxe", "tape", 14, 12, rang=4, prix=300, renverse=True, temps=[
        _e("accroupi", 5, dy=1), _e("crochet", 4, z=3, actif=True), _e("crochet", 4, z=1), _e("debout", 4)]),
    # --- Karaté : plus loin, plus lent.
    _t("pied_circulaire", "Coup de pied circulaire", "karate", "tape", 14, 18, rang=5, prix=500,
       arc=2.4, renverse=True, temps=[
        _e("debout", 5, rot=-0.3), _e("pied_cote", 5, rot=0.6, actif=True), _e("pied_cote", 4, rot=1.2),
        _e("debout", 5)]),
    _t("pied_de_cote", "Coup de pied de côté", "karate", "tenue", 16, 20, prix=400, arc=0.8,
       renverse=True, projete=40, tours=0.0, temps=[
        _e("genou", 8, dx=-1), _e("pied_cote", 6, dx=3, actif=True), _e("pied_cote", 6, dx=2), _e("debout", 6)]),
    _t("pied_saute", "Coup de pied sauté", "karate", "course", 14, 22, prix=600, renverse=True, temps=[
        _e("accroupi", 4), _e("pied_face", 6, dx=6, z=6, actif=True), _e("pied_face", 4, dx=3, z=3),
        _e("accroupi", 5)]),
    _t("balayage", "Balayage", "karate", "roulade", 6, 16, prix=450, arc=6.3, renverse=True, temps=[
        _e("accroupi", 3, dy=2), _e("accroupi", 8, dy=2, actif=True), _e("debout", 5)]),
    # --- Judo : les projections. Pas de sang, et on assomme.
    _t("projection_hanche", "Projection de hanche", "judo", "prise_avant", 12, 14, prix=500,
       renverse=True, projete=28, sans_sang=True, temps=[
        _e("saisie", 4), _e("hanche", 10, dx=2, actif=True), _e("hanche", 6), _e("debout", 6)]),
    _t("grand_fauchage", "Grand fauchage", "judo", "prise_vers_soi", 12, 14, prix=500,
       renverse=True, projete=6, sans_sang=True, temps=[
        _e("saisie", 4), _e("pied_face", 8, dx=2, actif=True), _e("saisie", 6), _e("debout", 5)]),
    _t("sacrifice", "Sacrifice en cercle", "judo", "prise_cote", 14, 14, prix=700,
       renverse=True, projete=40, tours=1.0, sans_sang=True, temps=[
        _e("saisie", 4), _e("au_sol", 14, actif=True), _e("accroupi", 8), _e("debout", 4)]),
    # --- Jiu-jitsu
    _t("retournement_poignet", "Retournement du poignet", "jiujitsu", "contre", 12, 20, prix=800,
       renverse=True, projete=16, sans_sang=True, temps=[
        _e("saisie", 10, actif=True), _e("accroupi", 6), _e("debout", 4)]),
    _t("etranglement", "Étranglement", "jiujitsu", "dos", 999, 14, prix=900, silencieuse=True,
       sans_sang=True, tenir=90, temps=[
        _e("saisie", 90, actif=True), _e("debout", 6)]),
]


def par_slug(slug: str) -> Technique:
    return next(t for t in CATALOGUE if t["slug"] == slug)


def chaine() -> list[Technique]:
    """Les techniques de la chaîne de tapes, dans l'ordre des rangs."""
    return sorted((t for t in CATALOGUE if t["geste"] == "tape"), key=lambda t: t["rang"])
```

Dans `app/definitions.py`, sous `"armes_regles": armes.REGLES,` : `"techniques": techniques.CATALOGUE,`
(et `techniques` dans l'import des modules du paquet, à côté d'`armes`).

- [ ] **Vert** : `… pytest -q tests/test_techniques.py tests/test_definitions.py` → tout passe. Les juges
  du poids du paquet (`test_definitions`, `test_hors_ligne`) : relire leur borne si l'un rougit.
- [ ] **Mutation** : donner `rang=3` à `uppercut` → `test_pas_deux_techniques…` rougit ; remettre.
- [ ] **Commit** : `feat: les techniques d'arts martiaux, 1re tâche — le catalogue`.

#### Tâche 2 : `blesser` sait ne pas faire saigner, et se taire

**Fichiers** — modifier `static/js/entites.js` (`blesser`, ≈ l. 4661) ; créer `tests/test_techniques_js.py`.

**Produit** — `Entites.blesser(e, degats, source, { sans_sang, silencieuse, … })`.

- [ ] **Les juges** — `tests/test_techniques_js.py` (le fichier des juges de banc du jalon ; les tâches
  suivantes y ajoutent les leurs) :

```python
"""Les techniques d'arts martiaux, au banc (docs/jalons/les-techniques-d-arts-martiaux.md)."""


def test_une_projection_ne_fait_pas_saigner(banc):
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const p = o.poser(null, 20, 0);
        const avant = L.B.entites.filter(function (e) { return e.type === 'particule'; }).length;
        L.Entites.blesser(p, 5, L.B.joueur, { sans_sang: true, renverse: true });
        const apres = L.B.entites.filter(function (e) { return e.type === 'particule'; }).length;
        return { avant: avant, apres: apres, saigne: p.saigne || 0 };
    }""")
    assert r["apres"] == r["avant"] and r["saigne"] == 0, r


def test_un_coup_silencieux_n_alerte_personne(banc):
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const p = o.poser(null, 20, 0), temoin = o.poser(null, 40, 0);
        const etat = temoin.etat;
        L.Entites.blesser(p, 999, L.B.joueur, { silencieuse: true, assomme: true, sans_sang: true });
        return { victime: p.etat, temoin: temoin.etat, avant: etat };
    }""")
    assert r["victime"] == "assomme", r
    assert r["temoin"] == r["avant"], r
```

⚠️ Avant d'écrire : lire `sang()` (l. ≈ 4788) — si le sang n'est pas une entité `type === 'particule'`,
compter ce qu'il crée vraiment (décalques `B.decals`, ou ce que `sang` remplit). Et lire `assommer` :
aujourd'hui il n'alerte pas ; si `tuer`/`assommer` crient ailleurs, la garde va là aussi.

- [ ] **Rouge** : le premier rougit (le sang tombe toujours), le second aussi si le témoin fuit.
- [ ] **Le code** — dans `blesser` :

```js
    if (opts.saigne && !opts.sans_sang) e.saigne = Math.min(B.defs.pietons.reactions.saignement_images, opts.saigne);
    // ⚠️ Une projection ASSOMME sans faire saigner : c'est ce qui la fait valoir
    // moins d'etoiles que cogner (docs/jalons/les-techniques-d-arts-martiaux.md).
    if (e !== B.joueur && !opts.sans_sang) sang(e.x, e.y, opts.saigne ? 6 : 3);
    if (!opts.silencieuse) Son.depuis(e, Son.SFX.touche);
```

et, dans la branche `else if (e.type === 'pieton')`, en tête : `if (opts.silencieuse) return true;` —
l'étranglement ne crie pas et n'alerte pas ; `Police.quelqu_un_voit` décide seul du crime (tâche 5).

- [ ] **Vert**, puis **mutation** (retirer `!opts.sans_sang`) → rouge ; remettre.
- [ ] **Commit** : `feat: les techniques d'arts martiaux, 2e tâche — un coup sans sang, un coup sans bruit`.

#### Tâche 3 : le bouton SAISIR

**Fichiers** — `static/js/entree.js` (`MAP_TOUCHES`, `MANETTE_DEFAUT`, les libellés tactiles ≈ l. 891-920,
et la ligne 119 qui lit `attaque[1]` comme l'épaule de droite) ; `app/manettes.py` (`_profil` : `boutons` et
`pieces`, `PAGES_COMMANDES`) ; `static/js/hud.js` (`MANETTE_PIECES` ≈ l. 775, `LIGNES_MANETTE` ≈ l. 822, le
dessin du téléphone ≈ l. 1457) ; `templates/index.html` (l. 177, les boutons tactiles) et la feuille qui les
place ; `tests/test_manettes*.py` (ce qui fige `attaque: [2, 5]`) ; `tests/test_techniques_js.py`.

**Produit** — l'action `saisir` : `Entree.neuf('saisir')`, `Entree.bas('saisir')`, `j.entree.neuf('saisir')`.

- [ ] **Les juges** :

```python
def test_u_saisit_au_clavier(banc):
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        o.touche('KeyU'); o.frame(1);
        const neuf = L.Entree.bas('saisir');
        o.relacher('KeyU'); o.frame(1);
        return { neuf: neuf, apres: L.Entree.bas('saisir') };
    }""")
    assert r == {"neuf": True, "apres": False}


def test_l_epaule_de_droite_saisit_et_ne_frappe_plus(banc):
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const b = [0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0];
        o.pad([0, 0], b); o.frame(1);
        return { saisir: L.Entree.bas('saisir'), attaque: L.Entree.bas('attaque') };
    }""")
    assert r == {"saisir": True, "attaque": False}


def test_une_disposition_sauvee_avant_saisir_garde_saisir(banc):
    """À surveiller no 3 : `options.manette` d'avant le bouton n'a pas la clé."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const b = [0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0];
        o.pad([0, 0], b); o.frame(1);
        return L.Entree.bas('saisir');
    }""", stockage={"bandini-options-v1": '{"manette": {"profil": "standard", "boutons": {"attaque": [2, 5]}}}'})
    assert r is True
```

⚠️ Lire d'abord comment `entree.js` fusionne `options.manette` avec le profil (la forme exacte de la clé
sauvée) et ajuster le `stockage` du troisième juge à cette forme ; lire aussi la signature de `o.pad`
(`tests/banc.js`, `function pad(axes, boutons, fiche)`).

- [ ] **Rouge**, puis le code :
  - `entree.js` : `saisir: ['KeyU'],` dans `MAP_TOUCHES` (commentaire : ni G ni R, I, O, L — `RIGOLO`) ;
    `MANETTE_DEFAUT` : `attaque: [2], saisir: [5]` ; la ligne 119 : `d: (boutons.saisir || [])[0]` si elle
    désigne l'épaule de droite (la lire avant) ; les libellés tactiles : `saisir: 'SAISIR'` à pied, `'·'`
    partout ailleurs ; une disposition sauvée sans `saisir` le prend au profil.
  - `manettes.py` : `"attaque": [faces["attaque"]]`, `"saisir": [epaules[1]]` ; `pieces` : `"attaque":
    [pos["attaque"]]`, `"saisir": ["epaule_d"]` ; `PAGES_COMMANDES`, page `pied`, après FRAPPER :
    `{"c": "saisir", "texte": "SAISIR · PROJETER"}`.
  - `hud.js` : `{ a: 'saisir', rang: 0, nom: 'epaule_d', … }` au lieu de `a: 'attaque', rang: 1` ;
    `['saisir', 'SAISIR / PROJETER']` dans `LIGNES_MANETTE`, après FRAPPER ; `'saisir'` dans la boucle
    du téléphone (et sa place dans `P`).
  - `index.html` : `<b data-a="saisir">SAISIR</b>` ; la feuille lui fait une place (au pouce droit, sous
    FRAPPE) — **capture Chromium** du téléphone avant de cocher.
- [ ] **Vert** : `… pytest -q tests/test_techniques_js.py tests/test_manettes*.py tests/test_commandes_js.py`.
  Les juges qui figeaient l'épaule de droite sur FRAPPE se corrigent **dans ce commit**, avec la raison.
- [ ] **Commit** : `feat: les techniques d'arts martiaux, 3e tâche — le bouton SAISIR`.

#### Tâche 4 : le moteur — la chaîne, la réserve, les passants

**Fichiers** — créer `static/js/techniques.js` ; `templates/index.html` (son `<script>` juste après
`combat.js`) ; `static/js/combat.js` (`frapper`, `maj`, `arcDeMelee`, `roulade`, l'export) ;
`static/js/entites.js` (`nomDePose`, `imageDe`, `pose`) ; `static/js/base.js` (`etatInitial` :
`techniques: {}` ; `completer` : `'techniques'` dans la liste des objets fusionnés) ;
`tests/test_techniques_js.py`.

**Consomme** — `B.defs.techniques` (tâche 1), `Entites.blesser(…, { sans_sang, silencieuse })` (tâche 2).

**Produit** — `Techniques.def(slug)`, `Techniques.sait(e, slug)`, `Techniques.choisir(e, geste) → slug|null`,
`Techniques.frapper(e, fort) → bool`, `Techniques.demarrer(e, slug, cible) → bool`, `Techniques.maj(e)` ;
sur l'entité : `e.technique` (slug), `e.techEtape`, `e.techT`, `e.techPose`, `e.reserve`, `e.chaine`,
`e.chaineT`, `e.coups` ; `Combat.arcDeMelee` exporté.

- [ ] **Les juges** (au bouton ; `X` est FRAPPE au clavier) :

```python
def _chaine(banc, sait, tapes, espace=4):
    """Les techniques qui partent, dans l'ordre, pour `tapes` tapes a `espace`
    images d'ecart. ⚠️ SANS CIBLE : un passant pose a cote se rapprocherait
    (`majPieton` tourne dans `o.frame`) et le genou volerait la place du poing.
    La tape part au RELACHER (`majGestes` : on charge tant que c'est tenu)."""
    return banc("""function (L, o) {
        L.Jeu.commencer();
        L.B.joueur.angle = 0; L.B.joueur.face = 'droite';
        %s
        const vus = []; let dernier = null;
        function regarder(n) {
            for (let k = 0; k < n; k++) {
                const t = L.B.joueur.technique || null;
                if (t && t !== dernier) vus.push(t);
                dernier = t; o.frame(1);
            }
        }
        for (let i = 0; i < %d; i++) { o.touche('KeyX'); regarder(1); o.relacher('KeyX'); regarder(%d); }
        regarder(60);
        return vus;
    }""" % (sait, tapes, espace))


def test_trois_tapes_font_gauche_droit_crochet(banc):
    r = _chaine(banc, "", 3, espace=14)
    assert r[:3] == ["direct_gauche", "direct_droit", "crochet"], r


def test_la_chaine_s_allonge_avec_ce_qu_on_sait(banc):
    r = _chaine(banc, "L.B.partie.techniques = { uppercut: true, pied_circulaire: true };", 5, espace=16)
    assert r == ["direct_gauche", "direct_droit", "crochet", "uppercut", "pied_circulaire"], r


def test_une_tape_pendant_le_coup_est_gardee_en_reserve(banc):
    """Deux tapes à deux images d'écart : la seconde tombe PENDANT le direct, et
    doit quand même donner le direct du droit."""
    r = _chaine(banc, "", 2, espace=2)
    assert r[:2] == ["direct_gauche", "direct_droit"], r


def test_une_vieille_partie_sans_techniques_frappe(banc):
    """À surveiller no 2."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        delete L.B.partie.techniques;
        L.B.partie = L.Sauvegarde.completer(L.B.partie, L.B.defs);
        o.poser(null, 10, 0);
        o.touche('KeyX'); o.frame(1); o.relacher('KeyX'); o.frame(3);
        return { t: L.B.joueur.technique || null, techniques: L.B.partie.techniques };
    }""")
    assert r["t"] == "direct_gauche" and r["techniques"] == {}, r


def test_tenue_sans_le_cours_reste_le_coup_fort(banc):
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        o.poser(null, 10, 0);
        o.touche('KeyX'); o.frame(L.Combat.CHARGE_MIN + 2); o.relacher('KeyX'); o.frame(2);
        return { t: L.B.joueur.technique, fort: !!L.B.joueur.fort };
    }""")
    assert r["fort"] is True, r


def test_tenue_avec_le_cours_donne_le_pied_de_cote(banc):
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        L.B.partie.techniques.pied_de_cote = true;
        o.poser(null, 10, 0);
        o.touche('KeyX'); o.frame(L.Combat.CHARGE_MIN + 2); o.relacher('KeyX'); o.frame(2);
        return L.B.joueur.technique;
    }""")
    assert r == "pied_de_cote"


def test_un_passant_rejoue_la_meme_suite_pour_la_meme_empreinte(banc):
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        function suite() {
            const p = o.poser(null, 12, 0); p.id = 4242; p.coups = 0;
            const vus = [];
            for (let i = 0; i < 6; i++) {
                p.etat = 'attaque_joueur';
                L.Combat.frapper(p, false); vus.push(p.technique);
                for (let k = 0; k < 40 && p.etat === 'attaque'; k++) L.Combat.maj();
            }
            L.Entites.retirer(p);
            return vus;
        }
        return [suite(), suite()];
    }""")
    assert r[0] == r[1] and len(set(r[0])) >= 2, r
```

⚠️ Le passant de `test_un_passant…` : `majPieton` ne tourne pas dans la boucle (on n'appelle que
`Combat.maj`) — c'est voulu, on juge le choix, pas la poursuite. Et `o.poser` : lire sa signature
(`tests/banc.js`, `poser(arch, dx, dy)`).

- [ ] **Rouge** : `Techniques is not defined` / `technique` indéfini.
- [ ] **Le module** — `static/js/techniques.js` :

```js
/* Bandini — les techniques d'arts martiaux : la chaine de tapes, les pieds,
   les projections (docs/jalons/les-techniques-d-arts-martiaux.md).

   Python decide (`app/techniques.py` : le catalogue, les lignes de temps), ce
   module JOUE : il choisit la technique d'apres le geste et le contexte, fait
   avancer sa ligne de temps, et applique le coup a l'etape `actif`.

   ⚠️ AUCUN `B.rng()` ICI. Un passant choisit sa variante a l'EMPREINTE (son id,
   son compteur de coups) : un de consomme ici decalerait tout le hasard de la
   ville (voir les juges « ce module ne deplace rien »). */

const Techniques = (function () {
  'use strict';

  //: La fenetre de rythme : une tape dans les 0,4 s apres la fin d'un coup
  //: passe au maillon suivant ; au-dela, on repart du direct du gauche.
  const FENETRE = 24;
  //: Colle a la cible (en px) : le genou plutot que le poing.
  const COLLE = 9;

  function def(slug) { return (B.defs.techniques || []).find(function (t) { return t.slug === slug; }) || null; }

  /** `e` connait-il `slug` ? La rue, tout le monde ; le reste, ce que la partie a appris. */
  function sait(e, slug) {
    const t = def(slug);
    if (!t) return false;
    if (t.gratuite) return true;
    if (Entites.estJoueur(e)) return !!(B.partie && B.partie.techniques && B.partie.techniques[slug]);
    return !!(e.techniques && e.techniques.indexOf(slug) >= 0);
  }

  function parGeste(geste, rang) {
    return (B.defs.techniques || []).find(function (t) { return t.geste === geste && (!rang || t.rang === rang); }) || null;
  }

  function cibleProche(e, rayon) {
    let mieux = null, d2 = rayon * rayon;
    for (const c of Entites.autour(e.x, e.y, rayon, function (q) { return q !== e && q.vivant && (q.type === 'pieton' || q.type === 'joueur'); })) {
      const d = (c.x - e.x) * (c.x - e.x) + (c.y - e.y) * (c.y - e.y);
      if (d <= d2) { d2 = d; mieux = c; }
    }
    return mieux;
  }

  /** Pure : le slug que `geste` donne a `e`, ou null. */
  function choisir(e, geste) {
    if (geste === 'tape') {
      const suivant = e.chaineT > 0 ? (e.chaine || 0) + 1 : 1;
      const t = parGeste('tape', suivant);
      return t && sait(e, t.slug) ? t.slug : parGeste('tape', 1).slug;
    }
    const t = parGeste(geste);
    return t && sait(e, t.slug) ? t.slug : null;
  }

  /** Le geste de FRAPPE, d'apres le contexte : collé, en sprint, au sortir d'une roulade, tenu. */
  function gesteDeFrappe(e, fort) {
    if (fort) return 'tenue';
    if (e.sortieRoulade > 0) return 'roulade';
    const ent = e.entree || Entree;
    const v = B.defs.recherche.vitesses;
    if (Entites.estJoueur(e) && ent.bas('esquive') && Math.hypot(e.vx, e.vy) > v.joueur_course + 0.1) return 'course';
    if (cibleProche(e, COLLE)) return 'genou';
    return 'tape';
  }

  /** Remplace `Combat.frapper` a mains nues. Rend true si un coup part. */
  function frapper(e, fort) {
    if (e.etat === 'attaque' && e.technique) { e.reserve = true; return false; }
    if (e.etat === 'attaque' || e.roule > 0) return false;
    let slug;
    if (!Entites.estJoueur(e)) {
      // La rue seulement, a l'empreinte : gauche, droit, crochet — le genou colle.
      e.coups = (e.coups || 0) + 1;
      slug = cibleProche(e, COLLE) ? 'genou' : parGeste('tape', ((e.id + e.coups) % 3) + 1).slug;
    } else {
      const geste = gesteDeFrappe(e, fort);
      slug = choisir(e, geste);
      if (!slug && geste === 'tenue') {
        // Sans le cours : le coup fort d'avant, sur le maillon de la chaine.
        slug = choisir(e, 'tape');
        if (!demarrer(e, slug, null)) return false;
        e.fort = true;
        return true;
      }
      if (!slug) slug = choisir(e, 'tape');
    }
    return demarrer(e, slug, null);
  }

  /** Lance `slug` sur `e` (et sur `cible`, pour une prise). */
  function demarrer(e, slug, cible) {
    const t = def(slug);
    if (!t) return false;
    e.avantLeCoup = e.etat === 'attaque' ? e.avantLeCoup : e.etat;
    e.etat = 'attaque';
    e.technique = slug;
    e.techCible = cible || null;
    e.techEtape = 0;
    e.techT = t.temps[0].images;
    e.techPose = t.temps[0].pose;
    e.touches = [];
    e.fort = false;
    e.reserve = false;
    e.phase = t.temps[0].actif ? 'actif' : 'anticipation';
    e.arc = armeDe(t, e);
    if (t.geste === 'tape') { e.chaine = t.rang; e.chaineT = 0; }
    // Le retournement, l'etranglement : l'etape 0 est deja l'actif.
    if (t.temps[0].actif) entrerDansLActif(e, t);
    return true;
  }

  /** Ce que `Combat.arcDeMelee` sait lire : une arme de la forme d'`armes.py`. */
  function armeDe(t, e) {
    // Le poing americain garde son ecart d'`armes.py` (12 contre 8) : +4.
    const lest = e && e.arme === 'poing_americain' ? 4 : 0;
    return { slug: 'poings', type: 'melee', degats: t.degats + lest, portee: t.portee, arc: t.arc,
             renverse: t.renverse, saigne: 0, assomme: t.assomme, usures: 0, son: 'coup',
             sans_sang: t.sans_sang, silencieuse: t.silencieuse, technique: t.slug };
  }

  /** Une image de la ligne de temps. */
  function maj(e) {
    const t = def(e.technique);
    if (!t) { finir(e); return; }
    const etape = t.temps[e.techEtape];
    if (etape.actif && !t.geste.startsWith('prise') && t.geste !== 'contre' && t.geste !== 'dos') {
      Combat.arcDeMelee(e, e.arc);
    }
    if (--e.techT > 0) return;
    e.techEtape++;
    if (e.techEtape >= t.temps.length) { finir(e); return; }
    const suivante = t.temps[e.techEtape];
    e.techT = suivante.images;
    e.techPose = suivante.pose;
    e.phase = suivante.actif ? 'actif' : (e.techEtape > t.temps.findIndex(function (q) { return q.actif; }) ? 'repos' : 'anticipation');
    if (suivante.actif) entrerDansLActif(e, t);
  }

  function entrerDansLActif(e, t) {
    Son.depuis(e, function () { Son.SFX.arme(e.arc); });
    // La prise (tache 5) branche ici la projection de `e.techCible`. ⚠️ `api`,
    // pas `Techniques` : appele a l'execution, apres la fin de l'IIFE.
    if (api.surActif) api.surActif(e, t);
  }

  function finir(e) {
    const t = def(e.technique);
    const reserve = e.reserve;
    e.technique = null; e.techPose = null; e.techCible = null; e.phase = null; e.reserve = false;
    if (t && t.geste === 'tape') e.chaineT = FENETRE;
    if (Entites.estJoueur(e)) {
      e.etat = 'flane';
      if (reserve && t && t.geste === 'tape') frapper(e, false);
      return;
    }
    e.etat = e.avantLeCoup || 'attaque_joueur';
    e.avantLeCoup = null;
  }

  /** Les compteurs qui courent hors du coup : la fenetre de la chaine, la sortie de roulade. */
  function majCompteurs(e) {
    if (e.chaineT > 0 && e.etat !== 'attaque') e.chaineT--;
    if (e.sortieRoulade > 0) e.sortieRoulade--;
  }

  const api = { FENETRE, COLLE, def, sait, choisir, frapper, demarrer, maj, majCompteurs, cibleProche, surActif: null };
  return api;
})();
```

- [ ] **Les branchements** :
  - `combat.js`, `frapper` : après `if (arme.type === 'tir') return tirer(e, arme);` —
    `if (arme.slug === 'poings' || arme.slug === 'poing_americain') return Techniques.frapper(e, fort);`
    (le poing américain garde son écart de dégâts : c'est `armeDe(t, e)`).
  - `combat.js`, `maj` : `if (e.etat === 'attaque') { if (e.technique) Techniques.maj(e); else { majAttaque(e); majJet(e); } }`
    et, pour chaque entité, `Techniques.majCompteurs(e)`.
  - `combat.js`, `arcDeMelee` : passer `sans_sang: !!arme.sans_sang, silencieuse: !!arme.silencieuse` à
    `Entites.blesser` ; exporter `arcDeMelee`.
  - `combat.js`, `roulade` : `j.sortieRoulade = ROULADE_IMAGES + 12;` quand elle part.
  - `entites.js`, `nomDePose` : en tête,
    `if (e.etat === 'attaque' && e.techPose) return e.techPose === 'debout' ? e.face : (e.techPose === 'frappe' ? 'frappe_' : 'tech_' + e.techPose + '_') + e.face;`
  - `entites.js`, `imageDe` : le repli devient `cuit.poses[voulu] ? voulu : (cuit.poses['frappe_' + e.face] && e.techPose && e.techPose !== 'debout' ? 'frappe_' + e.face : (cuit.poses[e.face] ? e.face : 'bas'))`
    — un sprite dessiné à la main frappe comme avant.
  - `entites.js`, `pose` : quand `e.technique`, l'élan vient de l'étape (et remplace l'ancien) :

```js
    const tech = e.technique && typeof Techniques !== 'undefined' ? Techniques.def(e.technique) : null;
    if (tech) {
      const et = tech.temps[e.techEtape] || tech.temps[0];
      const sens = cx >= 0 ? 1 : -1;
      p.dx += Math.round(cx * et.dx); p.dy += Math.round(cy * et.dx * 0.6) + et.dy - et.z;
      p.rot += et.rot * sens;
    } else if (e.etat === 'attaque' && e.phase && arme) {
      const elan = e.phase === 'anticipation' ? -2 : (e.phase === 'actif' ? 3 : 1);
      p.dx += Math.round(cx * elan); p.dy += Math.round(cy * elan * 0.6);
    }
```

  - `base.js` : `techniques: {}` dans `etatInitial` (près d'`armes`) ; `'techniques'` dans la liste de
    `completer`.
- [ ] **Vert** : `… pytest -q tests/test_techniques_js.py tests/test_armes_js.py tests/test_bagarre_js.py`,
  puis les juges « ce module ne déplace rien » (`-k deplace`) et ceux des poings (`-k poing`).
- [ ] **Mutations** : `FENETRE = 0` → la chaîne rougit ; retirer `e.reserve = true` → la réserve rougit ;
  `(e.id + e.coups)` → `B.rng()` → l'empreinte rougit.
- [ ] **Commit** : `feat: les techniques d'arts martiaux, 4e tâche — la chaîne, la réserve, les passants`.

#### Tâche 5 : la prise, les projections, l'étranglement, la parade

**Fichiers** — `static/js/techniques.js` (la prise, les vols) ; `static/js/combat.js` (`majGestes`, `maj`) ;
`static/js/entites.js` (`majPieton` : figé pendant `e.vol` et `e.tenu` ; `majJoueur` : figé pendant
`j.prise` ; `pose` : la rotation du vol) ; `tests/test_techniques_js.py`.

**Consomme** — `Techniques.demarrer/sait/def/cibleProche` (tâche 4), `saisir` (tâche 3), `blesser` (tâche 2).

**Produit** — `Techniques.majPrise(j, ent) → bool` (vrai = le geste est pris, `majGestes` s'arrête là),
`Techniques.projeter(c, auteur, t)`, `Techniques.majVols()`, `Techniques.lacher(j)` ; sur l'entité :
`j.prise = { cible, t, mode }` (`mode` : `'tenir'` ou `'etrangler'`), `c.tenu`, `c.vol = { x0, y0, x1, y1, t, duree, h, tours, sens, auteur, tech }`.

- [ ] **Les juges** — une fonction commune, puis un juge par geste :

```python
PRISE = """
    function prise(L, o, sait, dx, dy, geste) {
        L.Jeu.commencer();
        Object.assign(L.B.partie.techniques, sait);
        const j = L.B.joueur, p = o.poser(null, dx, dy);
        p.etat = 'flane'; p.angle = Math.atan2(dy, dx); j.angle = Math.atan2(dy, dx);
        j.face = dx > 0 ? 'droite' : 'bas';
        L.Entites.indexer();
        o.touche('KeyU'); o.frame(2);
        geste();
        for (let k = 0; k < 120 && (j.etat === 'attaque' || p.vol); k++) o.frame(1);
        o.relacher('KeyU'); o.frame(2);
        return { x: p.x, y: p.y, dx: p.x - j.x, etat: p.etat, jx: j.x, vol: !!p.vol, tenu: !!p.tenu, prise: !!j.prise,
                 solide: L.Monde.solidite(Math.floor(p.x / L.TT), Math.floor(p.y / L.TT)),
                 eau: L.Monde.estEau(Math.floor(p.x / L.TT), Math.floor(p.y / L.TT)) };
    }
"""


def test_la_hanche_le_fait_passer_devant(banc):
    r = banc("""function (L, o) { """ + PRISE + """
        return prise(L, o, { projection_hanche: true }, 12, 0, function () {
            o.touche('ArrowRight'); o.frame(3); o.relacher('ArrowRight'); });
    }""")
    assert r["etat"] == "assomme" and r["x"] > r["jx"] + 20 and not r["vol"], r


def test_le_sacrifice_le_fait_passer_par_dessus(banc):
    r = banc("""function (L, o) { """ + PRISE + """
        return prise(L, o, { sacrifice: true }, 12, 0, function () {
            o.touche('ArrowDown'); o.frame(3); o.relacher('ArrowDown'); });
    }""")
    assert r["etat"] == "assomme" and r["x"] < r["jx"], r


def test_sans_le_cours_le_stick_ne_projette_pas(banc):
    r = banc("""function (L, o) { """ + PRISE + """
        return prise(L, o, {}, 12, 0, function () {
            o.touche('ArrowRight'); o.frame(3); o.relacher('ArrowRight'); });
    }""")
    assert r["etat"] != "assomme", r


def test_relacher_sans_rien_repousse(banc):
    r = banc("""function (L, o) { """ + PRISE + """
        return prise(L, o, {}, 12, 0, function () {});
    }""")
    assert r["dx"] > 14 and not r["tenu"] and not r["prise"], r


def test_une_projection_vers_un_mur_tombe_sur_une_tuile_libre(banc):
    """Le joueur dos à la rue, la victime entre lui et un mur."""
    r = banc("""function (L, o) {
        const c = L.Monde.carte, TT = L.TT;
        L.Jeu.commencer();
        // Un mur plein a l'est d'une tuile libre : chercher la premiere paire.
        let pose = null;
        for (let y = 10; y < c.h - 10 && !pose; y++) for (let x = 10; x < c.w - 10 && !pose; x++) {
            if (L.Monde.solidite(x, y) === 0 && L.Monde.solidite(x + 1, y) === 0 && L.Monde.solidite(x + 2, y) === 1)
                pose = { x: x * TT + 8, y: y * TT + 8 };
        }
        L.B.joueur.x = pose.x - 4; L.B.joueur.y = pose.y;      // tuile x ; la victime, tuile x+1 L.Monde.centrerCamera(pose.x, pose.y);
        """ + PRISE.replace("L.Jeu.commencer();", "") + """
        return prise(L, o, { projection_hanche: true }, 12, 0, function () {
            o.touche('ArrowRight'); o.frame(3); o.relacher('ArrowRight'); });
    }""")
    assert r["solide"] != 1 and not r["eau"], r


def test_l_etranglement_non_vu_n_alerte_personne(banc):
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        L.B.partie.techniques.etranglement = true;
        const j = L.B.joueur, p = o.poser(null, 10, 0);
        p.etat = 'flane'; p.angle = 0; p.face = 'droite';    // il nous tourne le dos
        j.angle = 0; j.face = 'droite';
        L.Entites.indexer();
        const crimes = []; const f = L.Police.signalerCrime;
        L.Police.signalerCrime = function (q, x, y, vu) { crimes.push([q, vu]); return f.apply(null, arguments); };
        L.Police.quelqu_un_voit = function () { return false; };
        o.touche('KeyU'); o.frame(100); o.relacher('KeyU'); o.frame(2);
        return { etat: p.etat, crimes: crimes };
    }""")
    assert r["etat"] == "assomme", r
    assert all(vu is False for _, vu in r["crimes"]), r


def test_lacher_trop_tot_l_etranglement_le_libere(banc):
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        L.B.partie.techniques.etranglement = true;
        const j = L.B.joueur, p = o.poser(null, 10, 0);
        p.etat = 'flane'; p.angle = 0; j.angle = 0; j.face = 'droite';
        L.Entites.indexer();
        o.touche('KeyU'); o.frame(30); o.relacher('KeyU'); o.frame(2);
        return { etat: p.etat, tenu: !!p.tenu };
    }""")
    assert r["etat"] != "assomme" and not r["tenu"], r


def test_saisir_pendant_qu_il_arme_le_retourne(banc):
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        L.B.partie.techniques.retournement_poignet = true;
        const j = L.B.joueur, p = o.poser(null, 12, 0);
        p.etat = 'attaque_joueur'; p.angle = Math.PI; j.angle = 0; j.face = 'droite';
        L.Entites.indexer();
        L.Combat.frapper(p, false);                     // il arme
        o.touche('KeyU'); o.frame(1); o.relacher('KeyU');
        for (let k = 0; k < 90; k++) o.frame(1);
        return { etat: p.etat, vie: j.vie };
    }""")
    assert r["etat"] == "assomme" and r["vie"] == 100, r


def test_la_cible_qui_meurt_lache_la_prise(banc):
    """À surveiller no 5."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const j = L.B.joueur, p = o.poser(null, 12, 0);
        p.etat = 'flane'; j.angle = 0; j.face = 'droite'; L.Entites.indexer();
        o.touche('KeyU'); o.frame(3);
        const tenait = !!j.prise;
        L.Entites.tuer(p, null); o.frame(2);
        return { tenait: tenait, prise: !!j.prise, tenu: !!p.tenu };
    }""")
    assert r == {"tenait": True, "prise": False, "tenu": False}


def test_saisir_ne_fait_rien_la_roue_ouverte(banc):
    """À surveiller no 4."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const j = L.B.joueur, p = o.poser(null, 12, 0);
        p.etat = 'flane'; j.angle = 0; L.Entites.indexer();
        L.B.roue = { choix: 0 };
        o.touche('KeyU'); o.frame(3);
        return !!j.prise;
    }""")
    assert r is False
```

⚠️ Vérifier avant : `Entites.tuer(e, source)` (sa signature), la forme de `B.roue` qu'attend
`majRoue` (sinon ouvrir la roue par `Combat.ouvrirRoue(j)`), et que `ArrowDown` est bien « de côté »
quand le joueur regarde à droite (angle relatif ≈ 90°).

- [ ] **Rouge**, puis le code — dans `techniques.js`, avant `const api` :

```js
  //: La prise : combien de temps on tient sans rien faire, et le seuil du stick.
  const PRISE_MAX = 72, PRISE_PORTEE = 14, STICK = 0.5;
  //: Dans le dos : l'ecart entre le regard de la cible et la direction cible -> joueur.
  const DOS = 2.09;   // 120 degres

  function ecart(a, b) { let d = a - b; while (d > Math.PI) d -= 2 * Math.PI; while (d < -Math.PI) d += 2 * Math.PI; return d; }

  /** La cible prenable devant `j` (le cone de la frappe, a bout portant), ou null. */
  function prenable(j, portee) {
    for (const c of Entites.pietonsAutour(j.x, j.y, portee)) {
      if (!c.vivant || c.dansVehicule || c.vol || c.tenu || c.etat === 'assomme') continue;
      if (Math.abs(ecart(j.angle, Math.atan2(c.y - j.y, c.x - j.x))) > 0.9) continue;
      if (!Monde.ligneLibre(j.x, j.y, c.x, c.y)) continue;
      return c;
    }
    return null;
  }

  function tenir(j, c, mode) {
    j.prise = { cible: c, t: 0, mode: mode, interieur: B.interieur };
    c.tenu = true; c.avantPrise = c.etat; c.vx = 0; c.vy = 0;
    j.vx = 0; j.vy = 0;
  }

  /** Lache la prise, et rend a la cible ce qu'elle faisait (ou la colere). */
  function lacher(j) {
    const c = j.prise && j.prise.cible;
    j.prise = null;
    if (!c) return;
    c.tenu = false;
    if (c.vivant && c.etat !== 'assomme' && !c.vol) c.etat = c.courage > 0 ? 'attaque_joueur' : (c.avantPrise || 'fuit');
    c.avantPrise = null;
  }

  /** SAISIR et ce qu'on fait dans la prise. Vrai si le geste est pris (majGestes s'arrete). */
  function majPrise(j, ent) {
    if (j.prise) {
      const p = j.prise, c = p.cible;
      p.t++;
      if (!c.vivant || c.dansVehicule || c.etat === 'assomme' || !Entites.estJoueur(j)) { lacher(j); return false; }
      j.vx = 0; j.vy = 0; c.vx = 0; c.vy = 0;
      if (p.mode === 'etrangler') {
        if (!ent.bas('saisir')) { lacher(j); return true; }
        if (p.t >= def('etranglement').tenir) {
          c.tenu = false; j.prise = null;
          Entites.blesser(c, 999, j, { assomme: true, silencieuse: true, sans_sang: true });
          Police.signalerCrime('coup_pieton', c.x, c.y, Police.quelqu_un_voit(c.x, c.y, c));
        }
        return true;
      }
      if (ent.neuf('attaque')) { demarrer(j, 'genoux_prise', c); Combat.arcDeMelee(j, j.arc); return true; }
      const axe = ent.axe;
      if (axe.mag > STICK) {
        const rel = Math.abs(ecart(Math.atan2(axe.y, axe.x), Math.atan2(c.y - j.y, c.x - j.x)));
        const geste = rel < Math.PI / 4 ? 'prise_avant' : (rel > 3 * Math.PI / 4 ? 'prise_vers_soi' : 'prise_cote');
        const slug = choisir(j, geste);
        if (slug) { j.prise = null; demarrer(j, slug, c); return true; }
      }
      if (!ent.bas('saisir')) { j.prise = null; demarrer(j, 'repousser', c); return true; }
      if (p.t > PRISE_MAX) lacher(j);
      return true;
    }
    if (!ent.neuf('saisir') || j.etat === 'attaque') return false;
    // La parade : il arme son coup, a portee, et on sait le retournement.
    if (sait(j, 'retournement_poignet')) {
      const a = Entites.pietonsAutour(j.x, j.y, def('retournement_poignet').portee).find(function (c) {
        return c.vivant && c.etat === 'attaque' && c.phase === 'anticipation' && !c.vol;
      });
      if (a) {
        // Il armait : on lui prend le poignet avant que ca parte. `projeter` le relachera.
        a.etat = 'flane'; a.technique = null; a.techPose = null; a.phase = null; a.tenu = true;
        demarrer(j, 'retournement_poignet', a);
        return true;
      }
    }
    const c = prenable(j, PRISE_PORTEE);
    if (!c) return true;                          // SAISIR dans le vide : rien, mais le geste est pris
    const dos = Math.abs(ecart(c.angle, Math.atan2(j.y - c.y, j.x - c.x))) > DOS;
    tenir(j, c, dos && sait(j, 'etranglement') ? 'etrangler' : 'tenir');
    if (j.prise.mode === 'etrangler') Son.depuis(j, Son.SFX.etranglement);
    return true;
  }

  /** Le point de chute : de `x0,y0` vers `x1,y1`, raccourci a la derniere tuile seche et libre. */
  function chute(x0, y0, x1, y1) {
    const pas = Math.max(1, Math.ceil(Math.hypot(x1 - x0, y1 - y0) / 2));
    let bx = x0, by = y0;
    for (let i = 1; i <= pas; i++) {
      const x = x0 + (x1 - x0) * i / pas, y = y0 + (y1 - y0) * i / pas;
      const tx = Math.floor(x / TT), ty = Math.floor(y / TT);
      if (Monde.solidite(tx, ty) !== 0) break;      // un mur (1) ou l'eau (2) : on s'arrete avant
      bx = x; by = y;
    }
    return { x: bx, y: by };
  }

  /** Envoie `c` en l'air selon `t` : ou il retombe depend du geste. */
  function projeter(c, auteur, t) {
    const a = Math.atan2(c.y - auteur.y, c.x - auteur.x);
    const d = Math.hypot(c.x - auteur.x, c.y - auteur.y);
    let cx, cy;
    if (t.geste === 'prise_cote') { cx = auteur.x - Math.cos(a) * t.projete; cy = auteur.y - Math.sin(a) * t.projete; }
    else if (t.geste === 'prise_avant') { cx = auteur.x + Math.cos(a) * (d + t.projete); cy = auteur.y + Math.sin(a) * (d + t.projete); }
    else { cx = c.x + Math.cos(a) * t.projete; cy = c.y + Math.sin(a) * t.projete; }
    const fin = chute(c.x, c.y, cx, cy);
    c.tenu = false; c.vx = 0; c.vy = 0;
    c.vol = { x0: c.x, y0: c.y, x1: fin.x, y1: fin.y, t: 0, duree: 24 + Math.round(t.projete / 3),
              h: 10 + t.projete / 4, tours: t.tours, sens: Math.cos(a) >= 0 ? 1 : -1, auteur: auteur, tech: t.slug };
  }

  /** Une image de chaque vol ; a l'atterrissage, la chute fait mal. */
  function majVols() {
    for (const c of B.entites) {
      if (!c.vol) continue;
      const v = c.vol, k = ++v.t / v.duree;
      c.x = v.x0 + (v.x1 - v.x0) * k; c.y = v.y0 + (v.y1 - v.y0) * k;
      c.z = 4 * v.h * k * (1 - k);
      if (v.t < v.duree) continue;
      c.z = 0; c.vol = null;
      const t = def(v.tech);
      Entites.poussiere && Entites.poussiere(c.x, c.y);
      Son.depuis(c, Son.SFX.chute);
      if (Entites.estJoueur(v.auteur)) {
        B.cam.secousse = 0.8;
        Police.signalerCrime(c.agent ? 'coup_policier' : 'coup_pieton', c.x, c.y, c.agent || Police.quelqu_un_voit(c.x, c.y, c));
      }
      Entites.blesser(c, t.degats, v.auteur, { renverse: true, assomme: t.assomme, sans_sang: t.sans_sang, angle: 0 });
    }
  }

  api.surActif = function (e, t) {
    if (t.projete > 0 && e.techCible && (t.geste.startsWith('prise') || t.geste === 'contre')) projeter(e.techCible, e, t);
    else if (t.geste === 'prise' && e.techCible) {
      const c = e.techCible, a = Math.atan2(c.y - e.y, c.x - e.x);
      lacherCible(c); c.vx = Math.cos(a) * 3.2; c.vy = Math.sin(a) * 3.2; c.recul = 22;
    }
  };
  function lacherCible(c) { c.tenu = false; if (c.vivant && c.etat !== 'assomme') c.etat = c.courage > 0 ? 'attaque_joueur' : 'fuit'; }
```

⚠️ Dans `api`, ajouter `majPrise, projeter, majVols, lacher, chute`. `TT` : lire comment les autres
modules l'obtiennent (`B.defs.tuile_px` ou une constante de `base.js`) et faire pareil. Et
`Entites.poussiere(x, y, …)` : lire sa signature (l'export existe).

- [ ] **Les branchements** :
  - `combat.js`, `majGestes`, juste après `if (B.roue || B.piratage || B.epreuve) return;` :
    `if (Techniques.majPrise(j, ent)) return;` — les gardes du dessus (char, clôture, lit, manège, mort,
    roue, épreuve) valent donc pour SAISIR, et ESQUIVE dans la prise ne part pas (elle lâche : ajouter
    `if (j.prise && ent.neuf('esquive')) Techniques.lacher(j);` avant).
  - `combat.js`, `maj` : `Techniques.majVols();` après `majBrasiers()` ; et pour chaque joueur, avant
    les gardes, si `q.prise` et (`q.dansVehicule || !q.vivant || B.interieur !== q.prise.interieur`) →
    `Techniques.lacher(q)` (la prise ne survit pas à un changement de scène : poser `interieur:
    B.interieur` dans `j.prise` à `tenir`).
  - `entites.js`, `majPieton`, après la ligne `dansVehicule` : `if (e.vol || e.tenu) { e.vx = 0; e.vy = 0; return; }`.
  - `entites.js`, `majJoueur`, après `if (j.dansVehicule) return;` : `if (j.prise) { j.vx = 0; j.vy = 0; return; }`
    (⚠️ lire la suite de `majJoueur` : si l'endurance ou `recul` se décomptent plus bas, les garder).
  - `entites.js`, `pose` : `if (e.vol) { p.rot = e.vol.tours * Math.PI * 2 * (e.vol.t / e.vol.duree) * e.vol.sens; return p; }`
    en tête (après la roulade).
- [ ] **Vert** : tout `tests/test_techniques_js.py`, `tests/test_bouclier.py` (la prise d'otage ne doit pas
  bouger), `tests/test_bagarre_js.py`, `tests/test_armes_js.py`.
- [ ] **Mutations** : `chute` sans le `break` → le juge du mur rougit ; `DOS = 9` → l'étranglement rougit ;
  retirer le `lacher` sur `!c.vivant` → le no 5 rougit.
- [ ] **Commit** : `feat: les techniques d'arts martiaux, 5e tâche — la prise et les projections`.

#### Tâche 6 : les poses dessinées

**Fichiers** — `static/js/sprites.js` (`SPRITES.joueur.poses` : 27 grilles, et `mains` pour
`tech_poing_arriere_*` et `tech_crochet_*`) ; `tests/test_techniques_js.py`.

- [ ] **Le juge** :

```python
def test_chaque_pose_dessinee_existe_pour_les_trois_vues(banc):
    r = banc("""function (L, o) {
        const manque = [];
        const poses = L.SPRITES.joueur.poses;
        const dessinees = new Set();
        for (const t of L.B.defs.techniques) for (const e of t.temps)
            if (e.pose !== 'debout' && e.pose !== 'frappe') dessinees.add(e.pose);
        for (const p of dessinees) for (const v of ['bas', 'haut', 'cote']) {
            const g = poses['tech_' + p + '_' + v];
            if (!g || g[0].length !== 16 || g[0][0].length !== 12) manque.push(p + '_' + v);
        }
        return manque;
    }""")
    assert r == [], r
```

⚠️ Vérifier que `SPRITES` est exposé dans `L` (sinon `L.fenetre.SPRITES` ou ce que le banc expose).

- [ ] **Rouge** : les 27 manquent.
- [ ] **Dessiner** — 12×16, les lettres de région (`h s o c p b k`, `.` vide), les pieds sur la dernière
  rangée, comme `frappe_*`. Ce que chaque pose doit **montrer**, et c'est ça que la capture juge :
  - `poing_arriere` : le bras de l'AUTRE côté que `frappe` tendu, l'épaule avancée.
  - `crochet` : le bras replié en arc devant le visage, le torse tourné.
  - `genou` : une jambe levée, le genou à la hauteur des hanches (`p` monte de 3 rangées).
  - `pied_face` : une jambe tendue droit devant (de face : le soulier `b` au milieu, en avant ; de profil :
    horizontale, le soulier au bord).
  - `pied_cote` : le corps penché en arrière, la jambe horizontale sur le côté, le soulier au bout.
  - `saisie` : les deux bras tendus devant, les mains ensemble.
  - `hanche` : le dos tourné à moitié, le corps plié vers l'avant, les bras tirant vers le bas.
  - `au_sol` : couché sur le dos, une jambe levée (le pied au ventre de l'autre) — la tête en bas de la
    grille pour `bas`, en haut pour `haut`, de côté pour `cote`.
  - `accroupi` : le corps tassé de 4 rangées, une jambe tendue de côté (le balayage).
  - `mains` : `tech_poing_arriere_bas|haut|droite` et `tech_crochet_bas|haut|droite`, `[x, y, angle]` au
    bout du bras tendu — le poing américain doit rester au poing.
- [ ] **Capture Chromium** (voir la note « Capturer une pièce du jeu ») : chaque pose × 3 vues, pour le
  squelette `homme` ET les dérivés (`femme`, `costaud`, `vieux`, `grand` — leurs règles s'appliquent aux
  poses « debout » par le suffixe `_bas|_haut|_cote`, et `au_sol` peut s'y abîmer) ; plus une projection
  de hanche en vol. Copier dans `~/dev/bandini/captures/` et **regarder** chaque image avant de cocher.
- [ ] **Vert** + `tests/test_garderobe*.py` (le nombre de poses du squelette y est peut-être figé : « ses
  42 poses »).
- [ ] **Commit** : `feat: les techniques d'arts martiaux, 6e tâche — les poses`.

#### Tâche 7 : la triche, le nom affiché, les trois bruitages

**Fichiers** — `static/js/hud.js` (`menuDebug`, `tousLesItems` voisin) ; `static/js/techniques.js`
(`entrerDansLActif`) ; `app/audio.py` (trois `_e`) ; `static/js/son.js` (trois `SFX` avec repli
synthétique) ; `tests/test_techniques_js.py`.

- [ ] **Les juges** :

```python
def test_la_triche_donne_toutes_les_techniques(banc):
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        L.Hud.toutesLesTechniques();
        return L.B.defs.techniques.filter(function (t) { return !t.gratuite && !L.B.partie.techniques[t.slug]; }).length;
    }""")
    assert r == 0


def test_une_technique_apprise_se_nomme_quand_elle_part(banc):
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        L.B.partie.techniques.pied_de_cote = true;
        o.poser(null, 10, 0);
        o.touche('KeyX'); o.frame(L.Combat.CHARGE_MIN + 2); o.relacher('KeyX'); o.frame(20);
        return L.B.msg;
    }""")
    assert r == "COUP DE PIED DE CÔTÉ !"
```

- [ ] **Rouge**, puis :
  - `hud.js` : `function toutesLesTechniques()` (pose `true` pour chaque technique non gratuite, `message('TOUTES LES TECHNIQUES')`,
    `Son.SFX.argent()`), l'item `{ libelle: 'TOUTES LES TECHNIQUES', … }` sous TOUS LES ITEMS, et
    l'export.
  - `techniques.js`, `entrerDansLActif` : `if (Entites.estJoueur(e) && !t.gratuite) Hud.message(t.nom.toUpperCase() + ' !', 50);`
    et le son : `t.style === 'karate' ? Son.SFX.pied : Son.SFX.arme(e.arc)`.
  - `audio.py` : `_e("pied", "Coup de pied", …)` (un pied qui fend l'air, sec, court), `_e("chute", "Corps qui tombe", …)`
    (un corps qui tombe à plat sur l'asphalte), `_e("etranglement", "Étranglement", …)` (un souffle
    étouffé, sans mot) — prompts en anglais, secs, « no reverb, no music », comme `coup`.
  - `son.js` : `pied`, `chute`, `etranglement`, chacun `if (!joue('<slug>')) { … }` avec un repli par
    `ton`/`bruit`, comme `coup`.
- [ ] **Générer** : `uv run python scripts/audio_elevenlabs.py --essai` (le voir lister les trois, et
  eux seuls), `mcp elevenlabs_status` pour le solde, puis sans `--essai`. Écouter les trois.
- [ ] **Vert** : `tests/test_techniques_js.py`, `tests/test_audio.py`, `tests/test_hors_ligne.py`.
- [ ] **Commit** : `feat: les techniques d'arts martiaux, 7e tâche — la triche, le nom, les sons`.

#### Tâche 8 : la doc, la suite, la livraison

- [ ] `docs/architecture.md` : `app/techniques.py` dans la table des modules Python ; `techniques.js`
  dans la table des scripts (juste après `combat.js`) ; l'arborescence. `tests/test_carte_du_depot.py` vert.
- [ ] `docs/reprendre-le-travail.md` ou l'aide COMMANDES : SAISIR y est (tâche 3) — relire.
- [ ] La **suite complète** en parallèle (voir « Un rouge est-il de moi ? ») ; un rouge : le rejouer sur la
  base avant d'accuser le jalon.
- [ ] `uv run ruff check .`
- [ ] **Atterrir** (ff-only), puis **capture pour Martin** : une chaîne de 5 tapes, une projection de
  hanche, un sacrifice — dans `captures/`, ouvertes dans Aperçu.
- [ ] **Livrer** : la ligne quitte `docs/plan.md` pour `docs/jalons/README.md` (`✅ **livré**`, la date) ;
  la note sous `## Notes` (ce qui est livré, ce qui a surpris, les dettes).
- [ ] **Commit** : `docs: les techniques d'arts martiaux — livré`.

## Notes

_Rien de livré._
