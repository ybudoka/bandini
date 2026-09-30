# Des missions en chapitres, de cinq à dix minutes

← [les jalons livrés](README.md) · [le plan](../plan.md)

## Fiche

_Demandé par Martin le 30 sept. 2026 : « les missions doivent durer au moins 5 à 10 minutes chacune, trouve une
solution pour agrandir »._

_Ce que ça donne :_ une mission devient un **chapitre** de 5 à 10 minutes, découpé en **actes**. Mourir ou se faire
pogner à l'acte 3 ne renvoie plus au début : après l'hôpital ou le poste, on **reprend l'acte**. Les objectifs
peuvent faire durer le jeu (des renforts, un gang qui te colle au pare-chocs, une étoile) et trois types neufs
prennent du temps par nature. Un chronomètre au carnet dit si on y est.

**Aujourd'hui** (30 sept. 2026) :
- 77 missions. La ville fait ≈ 7 300 × 6 600 px, une berline plafonne à 4 px/image (≈ 240 px/s) : on la traverse
  en 30 s en ligne droite, ≈ 1 min dans le trafic. Estimation, pas une mesure : une mission typique dure 2 à 4 min,
  les plus courtes (p02, p04, p05, p10, e04, s06…) moins de 2. [Des missions plus longues](des-missions-plus-longues.md)
  (22 sept.) a déjà ajouté 2 à 4 étapes à chacune des 37 d'alors.
- **Aucune durée n'est enregistrée** : `missionsFaites[slug]` ne garde que le jour (`histoire.js`, `reussir`).
- **Aucun point de reprise** : `echouer()` (`histoire.js`) nettoie et met `mission = null` ; la mission redevient
  disponible, et on recommence à l'étape 0. Les ennemis déjà couchés restent couchés (`retenirLesTombes`).
- **Une mission ne survit pas au rechargement** : `jeu.js` fait `if (p.mission) p.mission = null`.
- La filature existe (`suivre`), le fuyard aussi (`ramasser` avec `cible: fuyard`) ; aucune option ne fait arriver
  des renforts ni un gang en char pendant un trajet (les renforts existent dans `frenesies.js` et `police.js`).

**Tranché avec Martin (30 sept. 2026)** :
- **Les quatre approches ensemble** : des actes avec des reprises, la fusion des missions courtes en chapitres, des
  objectifs qui durent, et des types d'objectifs longs.
- **On ne compte plus** : l'objectif « cent missions » de M16 tombe ; chaque arc prend le nombre de chapitres que
  son histoire demande.
- **La reprise** : un menu après l'hôpital ou le poste, REPRENDRE L'ACTE N ou PLUS TARD.
- **Ce qui fait durer se déclare dans le fichier de la mission**, objectif par objectif ; rien d'automatique.
- **Le pilote est La Pointe** : p02, p05, p04, p10, p09 et p11 en un chapitre de six actes.

### La forme d'un chapitre

Un chapitre reste **un fichier de mission** (`app/missions/<slug>.py`) : une seule liste d'`objectifs`, coupée par
un marqueur :

```python
{"type": "acte", "texte": "ACTE 3 — LE DÉFI DE ZED", "donneur": "zed"},
```

- Le marqueur est **instantané**. Il affiche son `texte` en carton (« ACTE 3 — LE DÉFI DE ZED »), pose le point de reprise
  et, s'il le déclare, porte ce qui ouvre l'acte : l'appel ou la scène du donneur suivant, et un saut d'horloge
  (`sur_place: {"lieu": "phare", "heure": "nuit"}`, le même saut que `surplace.js`).
- Le premier objectif d'un chapitre est un `acte` ; le validateur (`__init__.py`) le refuse sinon, et refuse un
  `acte` en dernière place.
- `pendant` garde son index d'étape : le marqueur compte comme une étape, et le moteur ne voit presque pas la
  différence. `sur_place` se déclare sur le marqueur ; `frontiere` reste au niveau de la mission (le pilote n'en a
  pas : ses actes vont de la Pointe au Brouillard).
- `remplace: ["p02", "p05", …]` nomme les missions que le chapitre remplace, dans l'ordre des actes.

**Les parties déjà commencées.** Une mission remplacée faite (`missionsFaites`) compte comme son acte fait. Le
chapitre commence au premier acte pas fait ; tous faits, le chapitre est fait. Les `prerequis` du catalogue qui
visaient une mission remplacée sont réécrits vers le chapitre ; le validateur refuse un slug remplacé ailleurs. Les
mp3 déjà payés gardent leur voix, renommés par (qui, mission, texte) comme au 22 sept.

### La reprise

- **Au marqueur `acte`**, `B.partie.mission.reprise` retient : l'étape, la position en ville, le char (modèle,
  couleur), l'arme en main et ses munitions. Pas l'heure : l'horloge ne recule jamais, et un acte de nuit refait
  son propre saut (`sur_place` du marqueur).
- **À l'échec** (`mort`, `arrete`, `vehicule_detruit`, `chrono`…) d'un chapitre, le parcours d'aujourd'hui se fait
  tel quel (hôpital ou poste, frais, armes confisquées en prison), puis un menu : **REPRENDRE L'ACTE N** ou
  **PLUS TARD**.
  - **Reprendre** : fondu au noir, police à zéro, le joueur au point de l'acte avec un char neuf du même modèle et
    l'arme de l'acte **rendue**, même si la prison l'avait prise. Les tombés restent tombés, comme aujourd'hui.
  - **Plus tard** : l'acte atteint reste dans `B.partie.chapitres[slug]` ; le donneur de cet acte rappelle, et le
    chapitre reprend là.
- **Au rechargement**, la mission en cours est encore vidée (`jeu.js` ne change pas), mais `chapitres[slug]` est
  sauvegardé : fermer le jeu à la 8ᵉ minute ne perd que l'acte en cours.

### Le chronomètre

Le temps d'une mission se compte dans `Jeu.maj` (ni rAF ni `B.t`), sans la pause ni les menus. Il s'écrit dans
`B.partie.durees[slug]` : le dernier temps et le meilleur, pour le chapitre et pour chaque acte. Le carnet l'affiche
sur la fiche du donneur, à côté de « FAITE ». C'est lui qui dit si on tient 5 à 10 minutes dans les vraies parties
de Martin (`donnees/bandini.sqlite3`, table `parties`).

### Ce qui fait durer

Des **options**, déclarées dans le fichier, là où l'histoire les justifie :

- `renforts: {"vagues": 2, "n": 3}` sur `tuer`, `proteger`, `tenir` : quand le groupe tombe à un seul debout, la
  vague suivante arrive `loin`, hors champ (`poserLesCravates`, `faireArriver`). Une réplique `pendant` peut
  l'annoncer.
- `poursuite: {"groupe": "skateux", "chars": 1}` sur `aller`, `livrer`, `retourner` : un char du gang naît hors
  champ et te colle jusqu'à la fin de l'objectif ; crevé ou semé, il lâche. L'IA se branche sur celle des renforts
  de frénésie et de la poursuite de police, pour un gang.
- `etoiles: N` sur n'importe quel objectif : ce que `semer` et `survivre` font déjà, généralisé.
- `donne: {…}` sur n'importe quel objectif : ce que la fin de mission accorde (`libere`, `calme`, `manchette`,
  `message`…), accordé quand CET objectif est fait — chaque acte donne ce que sa mission d'origine donnait.

Deux **types neufs** — la filature existe déjà (`suivre`), et la tournée aussi : `course` passe des points dans
l'ordre, à pied ou au volant, `chrono_s` au choix ; une tournée de cinq arrêts est une `course` sans chrono.

- `tenir` : rester dans un rayon pendant X secondes pendant que les vagues arrivent ; en sortir remet le compte à
  zéro, ou fait échouer (`strict`). C'est « défendre le phare ».
- `relais` sur le fuyard (`ramasser` avec `cible: fuyard`) : il change de char ou de district une ou deux fois
  avant qu'on le coince.

Chaque option et chaque type s'ajoute à `OPTIONS_OBJECTIFS` ou aux types de `__init__.py`, et se lit dans
`poser()`/`majObjectif()` de `histoire.js`.

### Le pilote : La Pointe

| Acte | D'où | Donneur | Ce qu'on fait |
|---|---|---|---|
| 1 | p02 | M. Bilodeau | les Skateux bloquent le pont, leur grand au cône |
| 2 | p05 | le Trappeur | de nuit, les collets près du phare |
| 3 | p04 | Zed | la course à pied contre son temps |
| 4 | p10 | Zed | le saut de la rampe, sur sa machine |
| 5 | p09 | Ovila | le phare éteint : le tenir, puis rallumer la lampe |
| 6 | p11 | Josée | Zed au Brouillard sain et sauf, et la paix (`libere: pointe`) |

Aujourd'hui ≈ 15 étapes. Le chapitre ajoute des répliques de pont entre les actes (le donneur suivant appelle, ou
attend sur place), des `renforts` au pont et au phare, une `poursuite` de Skateux vers le Brouillard, un `tenir` au
phare et une `course` au besoin. Visée : 8 à 10 min au chronomètre. Les voix neuves se génèrent dans le même passage
(ElevenLabs v3 : Martin a donné carte blanche le 28 sept.), et la dépense se dit.

### Les juges

- `tests/test_arc_p_js.py` réécrit : le chapitre de la Pointe joué de bout en bout, au bouton, sous Node.
- La reprise : mort à l'acte 3, REPRENDRE, et l'étape, la position, le char et l'arme sont ceux de l'acte ; arrêté à
  l'acte 5, l'arme confisquée revient ; PLUS TARD, puis le chapitre repart à l'acte atteint, rechargement compris.
- La migration : une partie qui a fait p02 et p05 commence le chapitre à l'acte 3 ; toutes faites, le chapitre est
  fait ; un prérequis vers p11 est réécrit.
- Chaque option et chaque type neuf a son juge de banc, qui rougit sans sa règle.
- Le chronomètre ne compte ni la pause ni les menus.
- `test_missions_en_scene_js` et `test_definitions` avant d'atterrir (le poids du paquet).

### Ensuite

Après le pilote joué par Martin, les autres arcs passent en chapitres par vagues, un arc à la fois. Les arcs qui
restent à écrire (Q, E, S, P, H, D, C, R, T, I, X de M16) s'écrivent directement en chapitres.

⚠️ **Ce qui guette** :
- Une mission remplacée a pu être une clé de `donne` ou de `ferme` (le téléphone, la rue libérée) : `libere`,
  `calme`, `manchette` et `a_vendre` passent à la fin de l'acte qui les donnait, pas à la fin du chapitre.
- Les juges « ce module ne déplace rien » et la ville : un chapitre ne pose aucun lieu neuf.
- [Qui parle se nomme](../personnages/README.md) : une fois par mission, donc une fois par **donneur** dans un
  chapitre.
- Six donneurs pour un chapitre : deux voix partagées ne se croisent jamais dans un même dialogue.

### Le plan d'exécution — tranche 1 : le moteur et La Pointe

> **Pour qui l'exécute :** superpowers:subagent-driven-development ou superpowers:executing-plans, tâche par tâche.
> Les étapes sont des cases (`- [ ]`). Registre tenu à la main (les outils cherchent « Task N ») :
> `<wt>/.superpowers/sdd/chapitres/progress.md`, `.superpowers/` dans `.git/info/exclude`.

**Le but :** une mission peut être un chapitre de plusieurs actes qu'on reprend à l'acte, chronométré, avec de quoi
durer ; et La Pointe en est le premier, de 8 à 10 minutes.

**L'architecture :** Python décrit (le type `acte`, `remplace`, les options) et juge la forme ; `static/js/chapitres.js`,
un module neuf, tient ce qui est propre aux chapitres (les actes, le donneur de l'acte, la reprise, le chronomètre) ;
`histoire.js` ne fait que l'appeler aux endroits où une mission commence, avance, échoue et réussit. Les options et
les deux types neufs vivent là où vivent les autres, dans `poser()` et `majObjectif()` de `histoire.js`.

**La pile :** Python 3 (`app/missions/`), JavaScript sans module (`static/js/*.js`, un IIFE par fichier, inclus par
`templates/index.html`), pytest, le banc Node (`tests/banc.js`, fixture `banc`).

**La spec :** la « Fiche » ci-dessus.

#### Les contraintes de tout le jalon

- Tout dans un worktree du scratchpad, base = `dev` LOCAL ; pytest avec
  `UV_PROJECT_ENVIRONMENT=/Users/martingagne/dev/bandini/.venv`.
- Rien au dé qui ne soit déjà au dé : aucune tuile, aucun lieu, aucun décor posé ; la ville ne bouge pas
  (`test_devants.py`, les juges « ce module ne déplace rien »).
- Chaque réplique neuve porte son `jeu=` ; « qui parle se nomme » une fois par donneur dans un chapitre.
- Un texte d'objectif : majuscules, 60 caractères au plus (`test_missions.py`).
- Commits `feat:`/`fix:`/`docs:` en français, par chemins explicites, `git add` et `git commit` en deux commandes,
  terminés par `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`.
- `uv run ruff check .` avant tout atterrissage ; `test_missions_en_scene_js` et `test_definitions` avant d'atterrir
  une mission.

#### Ce que la relecture doit regarder

1. **Mourir pendant le carton ou pendant la réplique d'ouverture d'un acte** : la reprise doit viser CET acte, pas
   le précédent — le point de reprise se pose au marqueur, avant toute réplique (juge à la tâche 4).
2. **Se faire arrêter pendant le fondu de l'hôpital** (le cas que `prison()` traite déjà) : un seul menu, pas deux
   (juge à la tâche 4).
3. **Une vieille partie qui a fait p02, p05 et p04** et ouvre le jeu : Zed doit être là (il `arrive_apres` p02), le
   chapitre au téléphone doit partir à l'acte 4 et la bulle doit être sur Zed, pas sur M. Bilodeau (juge à la
   tâche 3).
4. **PLUS TARD, puis recharger la partie** : le chapitre repart à l'acte atteint, et le téléphone ne rejoue pas
   l'appel de M. Bilodeau (juge à la tâche 3).
5. **Un `retourner` au milieu d'un chapitre** doit avancer à l'acte suivant, jamais payer la prime entière (juge
   à la tâche 2).

---

#### Tâche 1 : le chapitre dans les données (Python)

**Fichiers :**
- Modifier : `app/missions/__init__.py` (`TYPES_OBJECTIFS`, `OPTIONS_OBJECTIFS`, `Mission`, `scene_par_defaut`,
  une fonction neuve `erreurs_de_chapitre`, une fonction neuve `donneur_final`)
- Créer : `tests/test_chapitres.py`

**Interfaces :**
- Produit : le type d'objectif `"acte"` (`texte`, `donneur`, facultatif `sur_place`) ; la clé de mission
  `remplace: list[str]` ; l'option `donne` sur tout objectif ; `erreurs_de_chapitre(mission: dict,
  catalogue: list[dict] | None = None) -> list[str]` ; `donneur_final(mission: dict) -> str`.

- [ ] **Étape 1 : écrire les juges qui échouent** — `tests/test_chapitres.py` :

```python
"""Des missions en chapitres (docs/jalons/des-missions-en-chapitres.md) — la forme, en Python."""

from app import missions


def _chapitre(**plus):
    base = {"slug": "zz", "titre": "Zz", "donneur": "bilodeau", "recompense": 100,
            "remplace": ["za", "zb"],
            "objectifs": [
                {"type": "acte", "texte": "ACTE 1 — LE PONT", "donneur": "bilodeau"},
                {"type": "aller", "texte": "VA AU PONT", "lieu": "phare", "rayon": 5},
                {"type": "acte", "texte": "ACTE 2 — LES COLLETS", "donneur": "trappeur"},
                {"type": "retourner", "texte": "RETOURNE VOIR LE TRAPPEUR"},
            ],
            "dialogue": {"intro": [], "fin": []}}
    base.update(plus)
    return base


def test_acte_est_un_type_d_objectif_et_donne_une_option():
    assert "acte" in missions.TYPES_OBJECTIFS
    assert "donne" in missions.OPTIONS_OBJECTIFS


def test_un_chapitre_bien_forme_n_a_aucune_erreur():
    assert missions.erreurs_de_chapitre(_chapitre(), catalogue=[]) == []


def test_un_chapitre_commence_par_un_acte():
    m = _chapitre()
    m["objectifs"] = m["objectifs"][1:]
    assert any("commence" in e for e in missions.erreurs_de_chapitre(m, catalogue=[]))


def test_un_chapitre_ne_finit_pas_sur_un_acte():
    m = _chapitre()
    m["objectifs"].append({"type": "acte", "texte": "ACTE 3 — RIEN", "donneur": "zed"})
    m["remplace"].append("zc")
    assert any("finit" in e for e in missions.erreurs_de_chapitre(m, catalogue=[]))


def test_autant_de_missions_remplacees_que_d_actes():
    assert any("remplace" in e for e in missions.erreurs_de_chapitre(_chapitre(remplace=["za"]), catalogue=[]))


def test_le_donneur_d_un_acte_existe():
    m = _chapitre()
    m["objectifs"][2]["donneur"] = "personne_de_connu"
    assert any("donneur" in e for e in missions.erreurs_de_chapitre(m, catalogue=[]))


def test_une_mission_remplacee_ne_reste_pas_au_catalogue_ni_en_prerequis():
    autre = {"slug": "za", "prerequis": []}
    assert any("za" in e for e in missions.erreurs_de_chapitre(_chapitre(), catalogue=[autre]))
    suite = {"slug": "zq", "prerequis": ["zb"]}
    assert any("zb" in e for e in missions.erreurs_de_chapitre(_chapitre(), catalogue=[suite]))


def test_le_catalogue_n_a_aucune_erreur_de_chapitre():
    for m in missions.CATALOGUE:
        assert missions.erreurs_de_chapitre(m) == [], m["slug"]


def test_la_fin_d_un_chapitre_se_joue_chez_le_donneur_du_dernier_acte():
    assert missions.donneur_final(_chapitre()) == "trappeur"
    assert missions.donneur_final({"donneur": "zed", "objectifs": []}) == "zed"
```

- [ ] **Étape 2 : les voir échouer** — `uv run pytest tests/test_chapitres.py -q` : `AttributeError` sur
  `erreurs_de_chapitre`, et `acte` absent.

- [ ] **Étape 3 : le code** — dans `app/missions/__init__.py` :

```python
# dans TYPES_OBJECTIFS, après "boulots" :
    "acte",        # CHAPITRES (30 sept. 2026) : un marqueur instantané — son `texte` en carton, le point de
                   # reprise, le `donneur` de l'acte ; `sur_place` facultatif (le saut de `surplace.js`)
```

```python
# OPTIONS_OBJECTIFS : ajouter "donne" (ce que CET objectif accorde, fait — la même forme que `donne` de mission)
OPTIONS_OBJECTIFS = ("chrono_s", "sans_etoile", "sans_arme", "contre", "remet", "tenue", "allies", "treve", "donne")
```

```python
# class Mission, sous `frontiere` :
    remplace: NotRequired[list[str]]  # CHAPITRES : les missions qu'il remplace, une par acte, dans l'ordre
```

```python
def donneur_final(mission: dict) -> str:
    """Chez qui se joue la fin : le donneur du DERNIER acte d'un chapitre, sinon celui de la mission."""
    actes = [o for o in mission.get("objectifs") or [] if o.get("type") == "acte"]
    return actes[-1]["donneur"] if actes else mission["donneur"]


def erreurs_de_chapitre(mission: dict, catalogue: list[dict] | None = None) -> list[str]:
    """La forme d'un chapitre (docs/jalons/des-missions-en-chapitres.md). Une mission sans `acte` ni `remplace`
    n'en a aucune."""
    slug, objs = mission["slug"], mission.get("objectifs") or []
    actes = [o for o in objs if o.get("type") == "acte"]
    remplace = mission.get("remplace") or []
    if not actes and not remplace:
        return []
    erreurs = []
    if not objs or objs[0].get("type") != "acte":
        erreurs.append(f"{slug} : un chapitre commence par un acte")
    if objs and objs[-1].get("type") == "acte":
        erreurs.append(f"{slug} : un chapitre ne finit pas sur un acte")
    if len(remplace) != len(actes):
        erreurs.append(f"{slug} : remplace nomme {len(remplace)} missions pour {len(actes)} actes")
    for o in actes:
        if not personnage(o.get("donneur", "")):
            erreurs.append(f"{slug} : l'acte « {o.get('texte')} » n'a pas de donneur connu")
    for autre in CATALOGUE if catalogue is None else catalogue:
        if autre["slug"] in remplace:
            erreurs.append(f"{slug} : {autre['slug']} est remplacée, elle ne reste pas au catalogue")
        for p in set(autre.get("prerequis") or []) & set(remplace):
            erreurs.append(f"{autre['slug']} : son prérequis {p} est remplacé par {slug}")
    return erreurs
```

Et dans `scene_par_defaut`, en toute première ligne du corps : la fin d'un chapitre se joue chez le dernier donneur.

```python
    if partie == "fin":
        mission = {**mission, "donneur": donneur_final(mission)}
```

- [ ] **Étape 4 : les voir passer** — `uv run pytest tests/test_chapitres.py tests/test_missions.py -q` : vert.

- [ ] **Étape 5 : commit** — `git add app/missions/__init__.py tests/test_chapitres.py`, puis
  `git commit -m "feat: un chapitre dans les données — le type acte, remplace, et la forme jugée …"`.

---

#### Tâche 2 : l'acte se joue (le module `chapitres.js`)

**Fichiers :**
- Créer : `static/js/chapitres.js`
- Modifier : `templates/index.html` (la ligne après `surplace.js`), `static/js/histoire.js` (`avancer`,
  `majObjectif`, `reussir` → `accorder`, `parler`, les lectures de `m.donneur`), `static/js/scenes.js:60`,
  `static/js/hud.js` (carnet EN COURS, `m.donneur`), `docs/architecture.md` (la ligne du module)
- Créer : `tests/test_chapitres_js.py`

**Interfaces :**
- Consomme : le type `acte` et `donne` sur objectif (tâche 1).
- Produit : `Chapitres.actes(m) -> number[]` (les étapes des marqueurs) ; `Chapitres.acteA(m, etape) -> number`
  (le rang 0-based de l'acte qui contient `etape`, -1 hors chapitre) ; `Chapitres.donneurDe(m) -> string` ;
  `Chapitres.ouvrirActe(m, o, etape)` ; `Histoire.accorder(d)` (le corps de `reussir` qui applique `donne`,
  sorti tel quel) ; `Histoire.mission(slug)` exporté s'il ne l'est pas.

- [ ] **Étape 1 : écrire les juges qui échouent** — `tests/test_chapitres_js.py`. Une mission de banc greffée dans
  `L.B.defs.missions` (la manière de `test_sur_place_js.py`), pour juger le moteur sans le pilote :

```python
"""Des missions en chapitres — le moteur, joué au banc sur une mission de banc (`zz`)."""

from tests.outils_missions import OUTILS, PLUS_LONGUES, outils

#: Deux actes : M. Bilodeau au pont, puis le Trappeur ; chacun finit par un `retourner`.
ZZ = """
  function greffer(L) {
    const m = { slug: 'zz', titre: 'Zz', donneur: 'bilodeau', recompense: 500, prerequis: [], phase: 1,
      echec: ['mort', 'arrete'], donne: {}, remplace: ['za', 'zb'],
      objectifs: [
        { type: 'acte', texte: 'ACTE 1 — LE PONT', donneur: 'bilodeau' },
        { type: 'aller', texte: 'VA AU PONT', lieu: 'pont', rayon: 5 },
        { type: 'retourner', texte: 'RETOURNE VOIR M. BILODEAU', donne: { calme: 'skateux' } },
        { type: 'acte', texte: 'ACTE 2 — LES COLLETS', donneur: 'trappeur' },
        { type: 'aller', texte: 'VA AU BOIS', lieu: 'bois', rayon: 5 },
        { type: 'retourner', texte: 'RETOURNE VOIR LE TRAPPEUR' } ],
      dialogue: { appel: [], intro: [], pendant: [], fin: [], echec: [] }, scenes: {} };
    L.B.defs.missions.push(m);
    return m;
  }
  function a(L, slug) { const d = L.Histoire.donneur(slug), j = L.B.joueur; j.x = d.x - 16; j.y = d.y; L.Entites.indexer(); }
"""


def test_un_acte_pose_son_carton_et_sa_reprise_puis_avance_seul(banc):
    r = banc("function (L, o) {" + OUTILS + PLUS_LONGUES + ZZ + """
        L.Jeu.commencer(); L.graine(6);
        greffer(L); commencer(L, o, 'zz'); jouer(L, o);
        const pm = L.B.partie.mission;
        return { etape: pm.etape, reprise: pm.reprise && pm.reprise.etape, acte: L.Chapitres.acteA(L.Histoire.courante(), pm.etape),
                 chapitre: L.B.partie.chapitres.zz, donneur: L.Chapitres.donneurDe(L.Histoire.courante()) };
    }""")
    assert r == {"etape": 1, "reprise": 0, "acte": 0, "chapitre": 0, "donneur": "bilodeau"}


def test_retourner_au_milieu_avance_a_l_acte_suivant_sans_payer(banc):
    r = banc("function (L, o) {" + OUTILS + PLUS_LONGUES + ZZ + """
        L.Jeu.commencer(); L.graine(6);
        const B = L.B, p = B.partie; greffer(L);
        const argent = paiements(L);
        commencer(L, o, 'zz'); jouer(L, o);
        const pont = L.Histoire.lieu('pont'); B.joueur.x = pont.x; B.joueur.y = pont.y; L.Entites.indexer(); jouer(L, o);
        a(L, 'bilodeau'); jouer(L, o);
        return { etape: p.mission && p.mission.etape, donneur: L.Chapitres.donneurDe(L.Histoire.courante()),
                 paye: argent.length, calmes: p.calmes.slice(), za: !!p.missionsFaites.za, reprise: p.mission.reprise.etape };
    }""")
    assert r["etape"] == 4 and r["donneur"] == "trappeur", r
    assert r["paye"] == 0, "un retourner au milieu ne paie pas la prime"
    assert "skateux" in r["calmes"], "le donne de l'objectif est accordé quand il est fait"
    assert r["za"] is True, "l'acte fini marque sa mission remplacée faite"
    assert r["reprise"] == 3


def test_le_dernier_retourner_paie_et_le_chapitre_est_fait(banc):
    r = banc("function (L, o) {" + OUTILS + PLUS_LONGUES + ZZ + """
        L.Jeu.commencer(); L.graine(6);
        const B = L.B, p = B.partie; greffer(L);
        const argent = paiements(L);
        commencer(L, o, 'zz'); jouer(L, o);
        p.mission.etape = 4; jouer(L, o);                         // au bois : on saute le premier acte
        const bois = L.Histoire.lieu('bois'); B.joueur.x = bois.x; B.joueur.y = bois.y; L.Entites.indexer(); jouer(L, o);
        a(L, 'trappeur'); finir(L, o);
        return { fait: !!p.missionsFaites.zz, zb: !!p.missionsFaites.zb, argent: argent.map(function (x) { return x.montant; }),
                 chapitre: p.chapitres.zz === undefined };
    }""")
    assert r == {"fait": True, "zb": True, "argent": [500], "chapitre": True}
```

- [ ] **Étape 2 : les voir échouer** — `uv run pytest tests/test_chapitres_js.py -q` : `L.Chapitres` indéfini.

- [ ] **Étape 3 : le module** — `static/js/chapitres.js` :

```js
/* Des missions en CHAPITRES (30 sept. 2026, docs/jalons/des-missions-en-chapitres.md).

   Demande de Martin : « les missions doivent durer au moins 5 à 10 minutes chacune ». Un chapitre est une mission
   dont les objectifs sont coupés par des marqueurs `acte` : chacun a son donneur, pose un point de reprise, et se
   reprend après l'hôpital ou le poste. Ce module tient ce qui est PROPRE aux chapitres ; `histoire.js` l'appelle
   là où une mission commence, avance, échoue et réussit. */
const Chapitres = (function () {
  /** Les étapes des marqueurs `acte`, dans l'ordre. */
  function actes(m) {
    const r = [];
    (m && m.objectifs || []).forEach(function (o, i) { if (o && o.type === 'acte') r.push(i); });
    return r;
  }

  /** Le rang (0 = le premier) de l'acte qui contient `etape` ; -1 hors chapitre. */
  function acteA(m, etape) {
    const a = actes(m);
    let k = -1;
    for (let i = 0; i < a.length; i++) if (a[i] <= etape) k = i;
    return k;
  }

  function chapitres() { const p = B.partie; return p.chapitres || (p.chapitres = {}); }

  /** Le donneur de l'acte : celui de l'acte EN COURS si c'est la mission courante, celui de l'acte où l'on
      reprendra sinon, celui de la mission hors chapitre. */
  function donneurDe(m) {
    if (!m) return null;
    const a = actes(m);
    if (!a.length) return m.donneur;
    const pm = B.partie.mission;
    const etape = pm && pm.slug === m.slug ? Math.max(0, pm.etape) : (chapitres()[m.slug] || 0);
    const o = m.objectifs[a[Math.max(0, acteA(m, etape))]];
    return (o && o.donneur) || m.donneur;
  }

  /** Le marqueur commence : l'acte d'avant est FAIT (sa mission remplacée aussi, pour tout ce qui lit encore
      `missionsFaites` — `arrive_apres`, le carnet), puis le carton et le point de reprise. */
  function ouvrirActe(m, o, etape) {
    const p = B.partie, pm = p.mission, j = B.joueur, k = acteA(m, etape);
    if (k > 0 && m.remplace && m.remplace[k - 1] && !p.missionsFaites[m.remplace[k - 1]]) p.missionsFaites[m.remplace[k - 1]] = p.jour;
    chapitres()[m.slug] = etape;
    const ici = Histoire.ouEstLeJoueurEnVille();
    const v = j.dansVehicule;
    pm.reprise = { etape: etape, x: ici.x, y: ici.y,
                   char: v && v.def ? { slug: v.def.slug, couleur: v.couleur || null } : null,
                   arme: j.arme || 'poings', mun: p.armes[j.arme] ? p.armes[j.arme].mun : null };
    Hud.message(o.texte, 200);
    Missions.sauvegarderPartie();
  }

  /** La mission réussie : le chapitre n'a plus d'acte en attente, et ses missions remplacées sont faites. */
  function reussi(m) {
    const p = B.partie;
    delete chapitres()[m.slug];
    (m.remplace || []).forEach(function (s) { if (!p.missionsFaites[s]) p.missionsFaites[s] = p.jour; });
  }

  return { actes, acteA, donneurDe, ouvrirActe, reussi };
})();
```

- [ ] **Étape 4 : le brancher** — dans `static/js/histoire.js` :
  - `avancer()` : après `p.debutT = B.t;`, `if (o.type === 'acte') Chapitres.ouvrirActe(m, o, p.etape);`.
  - `avancer()` : juste avant `p.etape++`, `if (fait && fait.donne) accorder(fait.donne);`.
  - `majObjectif()`, un `case` de plus :

```js
      case 'acte': {
        // Instantané — sauf un acte `sur_place` (la nuit du Trappeur) : le saut, puis l'objectif suivant.
        if (o.sur_place && !B.mission.sautEnCours) {
          B.mission.sautEnCours = true;
          SurPlace.sauter({ sur_place: o.sur_place }, function () { if (B.mission) B.mission.sautEnCours = false; avancer(); });
        } else if (!o.sur_place) avancer();
        return;
      }
```

  - `reussir()` : sortir tel quel le bloc qui lit `d` (de `if (d.arme …` à `if (d.boss …`) dans
    `function accorder(d)`, et l'appeler `accorder(m.donne || {});` ; puis `Chapitres.reussi(m);` juste après
    `p.missionsFaites[m.slug] = p.jour;`. Exporter `accorder`, `ouEstLeJoueurEnVille` et `courante`.
  - `parler()` : `enCours.donneur === slug` → `Chapitres.donneurDe(enCours) === slug`, et dans ce bloc
    `reussir(); return true;` → `avancer(); return true;` (le dernier `retourner` réussit par `avancer`, qui appelle
    `reussir` quand il n'y a plus d'objectif).
  - `case 'retourner'` : `donneur(m.donneur)` → `donneur(Chapitres.donneurDe(m))`, et `reussir()` → `avancer()`.
  - Les autres lectures du donneur de la mission EN COURS ou À PRENDRE passent par `Chapitres.donneurDe(m)` :
    `disponibleDe` (193), l'appel « VA VOIR » (1129), `lieuDuPersonnage(m.donneur)` du téléphone (1186),
    `cible()` du `retourner` (3451), `majBulles` (3586), `scenes.js:60`, et `hud.js:1899` (EN COURS). Restent sur
    `m.donneur` : `aBesoinDe`, `demarrer` et le répertoire du carnet (`hud.js:2057`, les missions qu'IL a données).
  - `templates/index.html` : `<script src="{{ url_for('static', filename='js/chapitres.js') }}?v={{ version }}"></script>`
    juste après la ligne de `surplace.js`.
  - `docs/architecture.md` : une ligne pour `chapitres.js` sous celle de `surplace.js`, même forme.

- [ ] **Étape 5 : les voir passer** — `uv run pytest tests/test_chapitres_js.py tests/test_arc_p_js.py
  tests/test_missions_en_scene_js.py -q` : vert (l'arc P n'a pas encore bougé : `retourner` → `avancer` ne change
  rien pour une mission d'un seul acte).

- [ ] **Étape 6 : que le juge morde** — remettre `reussir()` dans `case 'retourner'` : le 2e juge doit rougir
  (payé 500 au milieu). Remettre, vider `__pycache__` n'est pas utile (JS), rejouer vert.

- [ ] **Étape 7 : commit** — `feat: l'acte se joue — un marqueur, son donneur, le point de reprise, et retourner qui avance …`

---

#### Tâche 3 : le chapitre commence où on en est

**Fichiers :** modifier `static/js/chapitres.js`, `static/js/histoire.js` (`faite`, `commencer`,
`poserPuisDireLIntro`, `majTelephone`) ; juges dans `tests/test_chapitres_js.py`.

**Interfaces :**
- Consomme : `Chapitres.actes`, `acteA`, `donneurDe` (tâche 2).
- Produit : `Chapitres.depart(m) -> number` (l'étape du marqueur où commencer, 0 pour une mission ordinaire) ;
  `Chapitres.fait(m) -> boolean`.

- [ ] **Étape 1 : les juges qui échouent** — ajouter à `tests/test_chapitres_js.py` :

```python
def test_une_vieille_partie_commence_au_premier_acte_pas_fait(banc):
    r = banc("function (L, o) {" + OUTILS + PLUS_LONGUES + ZZ + """
        L.Jeu.commencer(); L.graine(6);
        const p = L.B.partie, m = greffer(L);
        p.missionsFaites.za = 1;
        const depart = L.Chapitres.depart(m), donneur = L.Chapitres.donneurDe(m), dispo = L.Histoire.disponibleDe('trappeur');
        commencer(L, o, 'zz'); jouer(L, o);
        return { depart: depart, donneur: donneur, dispo: dispo && dispo.slug, etape: p.mission.etape };
    }""")
    assert r == {"depart": 3, "donneur": "trappeur", "dispo": "zz", "etape": 4}


def test_toutes_ses_missions_faites_le_chapitre_est_fait(banc):
    r = banc("function (L, o) {" + OUTILS + ZZ + """
        L.Jeu.commencer(); L.graine(6);
        const p = L.B.partie, m = greffer(L);
        p.missionsFaites.za = 1; p.missionsFaites.zb = 1;
        return { fait: L.Chapitres.fait(m), dispo: L.Histoire.disponibles().some(function (x) { return x.slug === 'zz'; }) };
    }""")
    assert r == {"fait": True, "dispo": False}


def test_plus_tard_puis_recharger_repart_a_l_acte_atteint_sans_rejouer_l_appel(banc):
    r = banc("function (L, o) {" + OUTILS + PLUS_LONGUES + ZZ + """
        L.Jeu.commencer(); L.graine(6);
        const B = L.B, p = B.partie; greffer(L);
        p.chapitres = { zz: 3 }; p.appels.zz = true;
        L.Jeu.retourTitre(); L.Jeu.commencer(); greffer(L);
        const dispo = L.Histoire.disponibleDe('trappeur');
        L.Histoire.parler('trappeur'); jouer(L, o);
        return { dispo: dispo && dispo.slug, etape: B.partie.mission && B.partie.mission.etape, intro: !!B.cinema };
    }""")
    assert r["dispo"] == "zz" and r["etape"] == 4 and r["intro"] is False, r
```

- [ ] **Étape 2 : les voir échouer.**

- [ ] **Étape 3 : le code** — dans `chapitres.js` :

```js
  /** L'étape du marqueur où commencer : le premier acte dont la mission remplacée n'est pas faite, ou plus
      loin si la partie a déjà atteint un acte (`chapitres[slug]`, PLUS TARD). 0 hors chapitre. */
  function depart(m) {
    const a = actes(m);
    if (!a.length) return 0;
    const faites = B.partie.missionsFaites;
    let k = 0;
    while (k < a.length - 1 && m.remplace && m.remplace[k] && faites[m.remplace[k]]) k++;
    return Math.max(a[k], chapitres()[m.slug] || 0);
  }

  /** Un chapitre dont toutes les missions remplacées sont faites l'est aussi (une vieille partie). */
  function fait(m) { return !!(m && m.remplace && m.remplace.length && m.remplace.every(function (s) { return B.partie.missionsFaites[s]; })); }
```

  et `depart`, `fait` à l'export. Dans `histoire.js` :
  - `faite(slug)` : `return !!B.partie.missionsFaites[slug] || Chapitres.fait(mission(slug));`
  - `commencer()` : `etape: -1` → `etape: Chapitres.depart(m) - 1`.
  - `poserPuisDireLIntro(m)` : après `porteEnAttente = null;`, une reprise ne redit pas l'intro du chapitre —
    le marqueur a ses propres répliques (`pendant` à son étape) :

```js
    if (Chapitres.depart(m) > 0) { commencer(m.slug, true); annoncer(m); return; }
```

  - `majTelephone()` : au décrochage, pour un chapitre à reprendre, pas l'`appel` du premier donneur :

```js
      if (Chapitres.depart(m) > 0) { Hud.message('RAPPEL : ' + m.titre.toUpperCase() + ' — VA VOIR ' + personnage(Chapitres.donneurDe(m)).nom.toUpperCase(), 220); return; }
```

- [ ] **Étape 4 : les voir passer**, plus `tests/test_arc_p_js.py` et `tests/test_telephone*.py` s'il y en a
  (`ls tests | grep -i telephone`).

- [ ] **Étape 5 : commit** — `feat: le chapitre commence où on en est — la vieille partie, PLUS TARD, et le rappel …`

---

#### Tâche 4 : REPRENDRE L'ACTE

**Fichiers :** modifier `static/js/chapitres.js`, `static/js/histoire.js` (`echouer`, `maj`) ; juges dans
`tests/test_chapitres_js.py`.

**Interfaces :**
- Consomme : `pm.reprise` (tâche 2), `Chapitres.depart` (tâche 3).
- Produit : `Chapitres.retenir(m)` (appelé par `echouer`), `Chapitres.majReprise() -> boolean` (true : un menu
  s'ouvre, `Histoire.maj` s'arrête là), `Chapitres.reprendre(r)`.

- [ ] **Étape 1 : les juges qui échouent** :

```python
REPRENDRE = """
  function mourir(L, o) {
    L.Missions.hopital('banc');
    for (let k = 0; k < 900 && (L.B.transition || L.B.cinema || !L.B.menu); k++) { o.frame(1); ecouter(L); }
    return L.B.menu ? L.B.menu.items.map(function (i) { return i.libelle; }) : null;
  }
  function choisir(L, o, libelle) {
    const i = L.B.menu.items.findIndex(function (x) { return x.libelle.indexOf(libelle) === 0; });
    L.B.menu.items[i].faire(); L.Hud.fermerMenu(); o.fondu();
    for (let k = 0; k < 400 && L.B.transition; k++) o.frame(1);
    jouer(L, o);
  }
"""


def test_mort_a_l_acte_2_reprendre_rend_l_etape_le_char_et_l_arme(banc):
    r = banc("function (L, o) {" + OUTILS + PLUS_LONGUES + ZZ + REPRENDRE + """
        L.Jeu.commencer(); L.graine(6);
        const B = L.B, p = B.partie, j = B.joueur; greffer(L);
        p.armes.fronde = { mun: 12 }; L.Combat.degainer(j, 'fronde');
        const v = L.Vehicules.creer('moto', j.x + 20, j.y, 0, { etat: 'stationne' }); L.Entites.indexer(); L.Vehicules.monter(j, v);
        commencer(L, o, 'zz'); jouer(L, o);
        p.mission.etape = 2; L.Histoire.avancer(); jouer(L, o);   // le marqueur de l'acte 2
        const menu = mourir(L, o);
        choisir(L, o, 'REPRENDRE');
        const pres = Math.round(Math.hypot(j.x - p.mission.reprise.x, j.y - p.mission.reprise.y) / 16);
        const moto = B.entites.find(function (e) { return e.type === 'vehicule' && e.def.slug === 'moto' && e !== v; });
        return { menu: menu, etape: p.mission.etape, pres: pres, arme: j.arme, moto: !!moto };
    }""")
    assert r["menu"][:2] == ["REPRENDRE L'ACTE 2", "PLUS TARD"], r
    assert r["etape"] == 4 and r["pres"] <= 6 and r["arme"] == "fronde" and r["moto"], r


def test_arrete_la_prison_prend_l_arme_la_reprise_la_rend(banc):
    r = banc("function (L, o) {" + OUTILS + PLUS_LONGUES + ZZ + REPRENDRE + """
        L.Jeu.commencer(); L.graine(6);
        const B = L.B, p = B.partie, j = B.joueur; greffer(L);
        p.armes.pistolet = { mun: 30 }; L.Combat.degainer(j, 'pistolet');
        commencer(L, o, 'zz'); jouer(L, o);
        B.recherche.etoiles = 1; L.Missions.prison(null);
        for (let k = 0; k < 900 && (B.transition || B.cinema || !B.menu); k++) { o.frame(1); ecouter(L); }
        const sans = !p.armes.pistolet;
        choisir(L, o, 'REPRENDRE');
        return { sans: sans, arme: j.arme, mun: p.armes.pistolet && p.armes.pistolet.mun };
    }""")
    assert r == {"sans": True, "arme": "pistolet", "mun": 30}


def test_mourir_pendant_le_fondu_de_l_hopital_ne_fait_qu_un_menu(banc):
    r = banc("function (L, o) {" + OUTILS + PLUS_LONGUES + ZZ + REPRENDRE + """
        L.Jeu.commencer(); L.graine(6);
        const B = L.B; greffer(L); commencer(L, o, 'zz'); jouer(L, o);
        L.Missions.hopital('banc'); B.recherche.etoiles = 1; L.Missions.prison(null);
        let menus = 0, avant = null;
        for (let k = 0; k < 1200; k++) { o.frame(1); ecouter(L); if (B.menu && B.menu !== avant) { menus++; avant = B.menu; } }
        return { menus: menus };
    }""")
    assert r["menus"] == 1


def test_plus_tard_garde_l_acte_et_rend_la_main(banc):
    r = banc("function (L, o) {" + OUTILS + PLUS_LONGUES + ZZ + REPRENDRE + """
        L.Jeu.commencer(); L.graine(6);
        const B = L.B, p = B.partie; greffer(L); commencer(L, o, 'zz'); jouer(L, o);
        p.mission.etape = 2; L.Histoire.avancer(); jouer(L, o);
        mourir(L, o); choisir(L, o, 'PLUS TARD');
        return { mission: p.mission, chapitre: p.chapitres.zz, appel: !!p.appels.zz };
    }""")
    assert r == {"mission": None, "chapitre": 3, "appel": False}
```

  Ajuster `mourir`/`choisir` à l'API réelle de `Hud` si `B.menu.items[i].faire` n'est pas la forme (lire
  `Hud.ouvrirMenu`, `hud.js:288`, et le menu d'`arrestation`, `missions.js:418`, qui s'en sert).

- [ ] **Étape 2 : les voir échouer.**

- [ ] **Étape 3 : le code** — dans `chapitres.js` :

```js
  const FONDU = [32, 40, 32];
  const CAP = { '>': 0, '<': Math.PI, '^': -Math.PI / 2, 'v': Math.PI / 2 };

  /** Ratée : si c'est un chapitre qui a un point de reprise, le menu attendra que l'hôpital ou le poste ait fini. */
  function retenir(m) {
    const pm = B.partie.mission;
    if (!pm || !pm.reprise || !actes(m).length) return;
    B.repriseEnAttente = { slug: m.slug, reprise: pm.reprise, acte: acteA(m, pm.reprise.etape) + 1 };
  }

  /** Le menu, quand plus rien ne se passe : ni fondu, ni réplique, ni lit, ni menu déjà ouvert. */
  function majReprise() {
    const r = B.repriseEnAttente, j = B.joueur;
    if (!r || B.transition || B.cinema || B.menu || B.partie.mission || !j || j.hospitalise || j.arrete) return false;
    B.repriseEnAttente = null;
    const m = Histoire.mission(r.slug);
    Hud.ouvrirMenu({ titre: 'MISSION RATÉE', sur: m.titre.toUpperCase(), obligatoire: true, items: [
      { libelle: "REPRENDRE L'ACTE " + r.acte, faire: function () { reprendre(r); return true; } },
      { libelle: 'PLUS TARD', detail: 'ON TE RAPPELLERA', faire: function () { delete B.partie.appels[r.slug]; B.partie.appelT = null; return true; } },
    ] });
    return true;
  }

  /** Au point de l'acte : hors du lit et de la pièce, la police à zéro, l'arme de l'acte rendue, un char neuf du
      même modèle sur la rue d'à côté ; puis la mission repart au marqueur (qui refait son saut s'il en a un). */
  function reprendre(r) {
    const j = B.joueur, p = B.partie, x = r.reprise;
    Jeu.transiter(FONDU, function () {
      if (j.alite) Entites.seLever(j, 0, 0);
      if (j.dansVehicule) Vehicules.descendre(j, true);
      Jeu.revenirEnVille();
      Police.remiseAZero();
      const place = Histoire.tuileLibre(x.x, x.y, 6) || x;
      j.x = place.x; j.y = place.y; j.vx = 0; j.vy = 0;
      if (x.arme && x.arme !== 'poings') { p.armes[x.arme] = { mun: x.mun }; Combat.degainer(j, x.arme); }
      if (x.char) {
        const rue = Histoire.tuileDeRue(j.x, j.y, 8);
        if (rue) Vehicules.creer(x.char.slug, rue.x, rue.y, CAP[rue.sens], { etat: 'stationne', couleur: x.char.couleur });
      }
      Entites.indexer(); Monde.centrerCamera(j.x, j.y);
      chapitres()[r.slug] = x.etape;
      Histoire.commencer(r.slug, false);
    }, "ACTE " + r.acte);
  }
```

  Export : `retenir, majReprise, reprendre`. Dans `histoire.js` : `echouer()` appelle `Chapitres.retenir(m);` en
  première ligne après `if (!m) return;` ; `maj()` appelle `if (Chapitres.majReprise()) return;` juste après
  `jouerLeGenerique();`. ⚠️ `Entites.seLever`, `Jeu.revenirEnVille` : vérifier leur nom exact (`prison()` et
  `SurPlace.sauter` s'en servent) ; si `Vehicules.creer` ne prend pas `couleur` en option, lire sa signature
  (`vehicules.js:93`) et poser `v.couleur` après.

- [ ] **Étape 4 : les voir passer**, et que les juges mordent : sans `Chapitres.retenir` dans `echouer`, les
  quatre rougissent.

- [ ] **Étape 5 : commit** — `feat: reprendre l'acte — un menu après l'hôpital ou le poste, l'arme rendue …`

---

#### Tâche 5 : le chronomètre

**Fichiers :** `static/js/chapitres.js`, `static/js/histoire.js` (`maj`, `reussir`), `static/js/hud.js`
(`menuCarnetFiche`, la ligne 2058) ; juges dans `tests/test_chapitres_js.py`.

**Interfaces :** produit `Chapitres.compter()`, `Chapitres.noterDuree(m)`, `B.partie.durees[slug] =
{ dernier: s, meilleur: s, actes: [s, …] }` (secondes entières).

- [ ] **Étape 1 : les juges qui échouent** :

```python
def test_le_chronometre_compte_le_jeu_pas_la_pause_ni_les_menus(banc):
    r = banc("function (L, o) {" + OUTILS + PLUS_LONGUES + ZZ + """
        L.Jeu.commencer(); L.graine(6);
        const B = L.B, p = B.partie; greffer(L); commencer(L, o, 'zz'); jouer(L, o);
        const t0 = p.mission.images;
        for (let k = 0; k < 600; k++) o.frame(1);                   // 10 s de jeu
        L.Jeu.pause(); for (let k = 0; k < 600; k++) o.frame(1); L.Jeu.reprendre();
        L.Hud.ouvrirMenu({ titre: 'X', items: [{ libelle: 'OK', faire: function () { return true; } }] });
        for (let k = 0; k < 600; k++) o.frame(1); L.Hud.fermerMenu();
        return { s: Math.round((p.mission.images - t0) / 60) };
    }""")
    assert r["s"] == 10


def test_la_duree_s_ecrit_a_la_reussite_par_acte(banc):
    r = banc("function (L, o) {" + OUTILS + PLUS_LONGUES + ZZ + """
        L.Jeu.commencer(); L.graine(6);
        const B = L.B, p = B.partie; greffer(L); commencer(L, o, 'zz'); jouer(L, o);
        for (let k = 0; k < 1200; k++) o.frame(1);
        p.mission.etape = 2; L.Histoire.avancer(); jouer(L, o);
        for (let k = 0; k < 600; k++) o.frame(1);
        p.mission.etape = 5; L.Histoire.avancer(); finir(L, o);
        return p.durees.zz;
    }""")
    assert r["actes"][0] >= 20 and r["actes"][1] >= 10 and r["dernier"] == sum(r["actes"]) and r["meilleur"] == r["dernier"], r
```

- [ ] **Étape 2 : les voir échouer.**

- [ ] **Étape 3 : le code** — `chapitres.js` :

```js
  /** Une image de mission jouée (`Histoire.maj` ne tourne ni sous un menu, ni en pause, ni dans un fondu). */
  function compter() {
    const pm = B.partie.mission;
    if (!pm) return;
    pm.images = (pm.images || 0) + 1;
    pm.imagesActe = (pm.imagesActe || 0) + 1;
  }

  /** L'acte fini : sa durée rejoint celles d'avant (gardées dans la reprise, pour survivre à un échec). */
  function fermerActe(pm) {
    pm.actes = (pm.actes || []).concat([Math.round((pm.imagesActe || 0) / 60)]);
    pm.imagesActe = 0;
  }

  function noterDuree(m) {
    const p = B.partie, pm = p.mission, d = p.durees || (p.durees = {});
    const actesFaits = actes(m).length ? (fermerActe(pm), pm.actes) : [Math.round((pm.images || 0) / 60)];
    const total = actesFaits.reduce(function (a, b) { return a + b; }, 0);
    const avant = d[m.slug];
    d[m.slug] = { dernier: total, meilleur: avant ? Math.min(avant.meilleur, total) : total, actes: actesFaits };
  }
```

  Dans `ouvrirActe` : `if (acteA(m, etape) > 0) fermerActe(pm);` avant la reprise, et `actes: pm.actes || []`
  dans l'objet `reprise` ; dans `reprendre` et `commencer` (quand `chapitres[slug]` est posé), `pm.actes` repart de
  `reprise.actes`. `histoire.js` : `Chapitres.compter();` en tête du bloc `if (B.partie.mission) {` de `maj()` ;
  `Chapitres.noterDuree(m);` dans `reussir()` avant `p.mission = null`. `hud.js:2058` :

```js
      const d = p.durees && p.durees[m.slug];
      const temps = d ? ' · ' + Math.floor(d.dernier / 60) + ':' + String(d.dernier % 60).padStart(2, '0') : '';
      items.push(ligne('· ' + m.titre.toUpperCase(), p.missionsFaites[m.slug] ? 'FAITE' + temps : ''));
```

- [ ] **Étape 4 : les voir passer**, `tests/test_carnet*.py` compris (`ls tests | grep -i carnet`).

- [ ] **Étape 5 : commit** — `feat: le chronomètre des missions — au carnet, par acte …`

---

#### Tâche 6 : `etoiles` sur tout objectif, et `renforts`

**Fichiers :** `app/missions/__init__.py` (`OPTIONS_OBJECTIFS` += `"etoiles"`, `"renforts"`),
`static/js/histoire.js` (`poser`, `poserLesCravates`, `majObjectif` case `tuer`, `avancer`) ; juges dans
`tests/test_chapitres_js.py`.

**Interfaces :** produit `majRenforts(m, o, p, cibles, tombes) -> boolean` (dans `histoire.js`, non exporté ;
servira à `tenir`, tâche 8).

- [ ] **Étape 1 : les juges qui échouent** :

```python
def test_renforts_deux_vagues_avant_que_l_objectif_tombe(banc):
    r = banc("function (L, o) {" + OUTILS + PLUS_LONGUES + ZZ + outils("coucher", "images") + """
        L.Jeu.commencer(); L.graine(6);
        const B = L.B, p = B.partie, m = greffer(L);
        m.objectifs[1] = { type: 'tuer', texte: 'DÉGAGE LE PONT', groupe: 'skateux', n: 3, ou: 'pont',
                           renforts: { vagues: 2, n: 2 } };
        commencer(L, o, 'zz'); jouer(L, o);
        const vagues = [];
        for (let k = 0; k < 4 && p.mission.etape === 1; k++) { vagues.push(coucher(L, o)); images(L, o, 30); }
        return { vagues: vagues, etape: p.mission.etape };
    }""")
    assert r["vagues"] == [3, 2, 2] and r["etape"] == 2, r


def test_etoiles_sur_un_aller(banc):
    r = banc("function (L, o) {" + OUTILS + PLUS_LONGUES + ZZ + """
        L.Jeu.commencer(); L.graine(6);
        const m = greffer(L); m.objectifs[1].etoiles = 2;
        commencer(L, o, 'zz'); jouer(L, o);
        return L.B.recherche.etoiles;
    }""")
    assert r == 2
```

  (`coucher` couche ceux de l'étape encore debout ; la 1re vague en
  compte 3, chaque renfort 2 — le dernier debout d'une vague déclenche la suivante, `coucher` les couche tous.)

- [ ] **Étape 2 : les voir échouer.**

- [ ] **Étape 3 : le code** — `histoire.js` :
  - `poser()` après `if (o.treve) …` :
    `if (o.etoiles && o.type !== 'semer' && o.type !== 'survivre') Police.etoilesAuMoins(o.etoiles);`
    (lire `police.js:374` : si elle ne pose pas `dernierVu`, faire comme le `semer` de `poser`).
  - `poserLesCravates` : `const reste = o.vague ? o.n : o.n - dejaTombes(m.slug, etape);` et
    `const arrivee = o.loin ? (o.vague ? placeDArrivee(o.loin) : B.mission.arrivee || placeDArrivee(o.loin)) : null;`
  - `avancer()` : `B.mission.vagues = 0;` à côté de `p.debutT = B.t;`.
  - la fonction, avant `majObjectif` :

```js
  /** `renforts` : quand il ne reste qu'UN debout, la vague suivante arrive de loin. Rend true s'il en a posé une. */
  function majRenforts(m, o, p, cibles, tombes) {
    const r = o.renforts;
    if (!r || (B.mission.vagues || 0) >= r.vagues || !cibles.length || cibles.length - tombes > 1) return false;
    B.mission.vagues = (B.mission.vagues || 0) + 1;
    dansLaVille(function () { poserLesCravates(m, Object.assign({}, o, { n: r.n, chef: false, loin: o.loin || 14, vague: true }), false); });
    return true;
  }
```

  - `case 'tuer'` : après le calcul de `tombes` et `avant`, `if (majRenforts(m, o, p, cibles, tombes)) return;` ; puis
    `const total = o.n + (B.mission.vagues || 0) * (o.renforts ? o.renforts.n : 0);` et `o.n` → `total` dans
    `B.mission.kos` et dans la condition de fin.

- [ ] **Étape 4 : les voir passer**, plus `tests/test_arc_*_js.py` des missions qui ont un `tuer` (le calcul de
  `total` ne change rien sans `renforts`).

- [ ] **Étape 5 : commit** — `feat: renforts et étoiles sur tout objectif …`

---

#### Tâche 7 : `poursuite` — un char du gang qui te colle

**Fichiers :** `app/missions/__init__.py` (`OPTIONS_OBJECTIFS` += `"poursuite"`), `static/js/histoire.js`
(`poser`, `avancer`, une fonction `commandesDuPoursuivant` exportée), `static/js/vehicules.js` (la boucle des
pilotes, `vehicules.js:3280` et la condition des rails `:3287`) ; juges dans `tests/test_chapitres_js.py`.

**Interfaces :** produit le pilote `conducteur: 'poursuivant'` ; `Histoire.commandesDuPoursuivant(v) -> 'rails' |
{gaz, frein, direction, freinMain}`.

- [ ] **Étape 1 : les juges qui échouent** :

```python
def test_une_poursuite_nait_hors_champ_colle_et_lache_a_la_fin_de_l_objectif(banc):
    r = banc("function (L, o) {" + OUTILS + PLUS_LONGUES + ZZ + """
        L.Jeu.commencer(); L.graine(6);
        const B = L.B, p = B.partie, j = B.joueur, m = greffer(L);
        m.objectifs[1].poursuite = { groupe: 'skateux', chars: 1 };
        commencer(L, o, 'zz'); jouer(L, o);
        const v = B.entites.find(function (e) { return e.type === 'vehicule' && e.conducteur === 'poursuivant'; });
        const nait = v ? Math.round(Math.hypot(v.x - j.x, v.y - j.y)) : 0, horsChamp = v && !L.Entites.visibleAEcran(v.x, v.y, 0);
        for (let k = 0; k < 900; k++) o.frame(1);
        const pres = Math.round(Math.hypot(v.x - j.x, v.y - j.y));
        const pont = L.Histoire.lieu('pont'); j.x = pont.x; j.y = pont.y; L.Entites.indexer(); jouer(L, o);
        return { nait: nait, horsChamp: horsChamp, pres: pres, apres: v.conducteur };
    }""")
    assert r["horsChamp"] and r["nait"] >= 300, r
    assert r["pres"] < r["nait"], "il s'approche"
    assert r["apres"] == "trafic", "l'objectif fait, il retourne au trafic"
```

- [ ] **Étape 2 : les voir échouer.**

- [ ] **Étape 3 : le code** — `histoire.js` :

```js
  /** Une voie hors champ à 320-520 px du joueur, dans le sens de la voie (le patron de `Police.peuplerAutos`). */
  function rueHorsChamp() {
    const j = B.joueur, c = Monde.carte;
    for (let essai = 0; essai < 20; essai++) {
      const a = B.rng() * Math.PI * 2, d = 320 + B.rng() * 200;
      const tx = Math.floor((j.x + Math.cos(a) * d) / TT), ty = Math.floor((j.y + Math.sin(a) * d) / TT);
      if (tx < 1 || ty < 1 || tx >= c.w - 1 || ty >= c.h - 1) continue;
      const f = Monde.fleche(tx, ty);
      if (!f || Entites.visibleAEcran(tx * TT + 8, ty * TT + 8, 40)) continue;
      return { x: tx * TT + 8, y: ty * TT + 8, sens: f };
    }
    return null;
  }

  /** `poursuite` : des chars du gang, nés hors champ, qui te collent tant que l'objectif dure. */
  function poserLaPoursuite(m, o) {
    const pr = o.poursuite, CAP = { '>': 0, '<': Math.PI, '^': -Math.PI / 2, 'v': Math.PI / 2 };
    B.mission.poursuivants = [];
    for (let k = 0; k < (pr.chars || 1); k++) {
      const rue = rueHorsChamp();
      if (!rue) continue;
      const v = Vehicules.creer(pr.vehicule || 'auto', rue.x, rue.y, CAP[rue.sens],
                                { conducteur: 'poursuivant', etat: 'roule', surRails: true, poursuite: true, sens: rue.sens });
      if (!v) continue;
      v.gang = pr.groupe; v.mission = m.slug;
      B.mission.poursuivants.push(v);
    }
  }

  /** Le pilote d'un poursuivant : sur les rails de loin, droit sur toi de près (`Police.commandes`, sans équipage). */
  function commandesDuPoursuivant(v) {
    const j = B.joueur, cible = j.dansVehicule || j;
    const d = Math.hypot(cible.x - v.x, cible.y - v.y);
    const direct = d < 140 && Monde.ligneLibre(v.x, v.y, cible.x, cible.y);
    const coince = !v.surRails && (v.immobileT || 0) > 45;
    if (!direct || coince) {
      if (!v.surRails) { v.cible = null; v.sortie = null; v.immobileT = 0; }
      v.surRails = true;
      return 'rails';
    }
    v.surRails = false;
    const voulu = Math.atan2(cible.y - v.y, cible.x - v.x);
    let ecart = voulu - v.angle;
    while (ecart > Math.PI) ecart -= 2 * Math.PI;
    while (ecart < -Math.PI) ecart += 2 * Math.PI;
    return { gaz: Math.abs(ecart) > 1.6 ? 0 : 1, frein: Math.abs(ecart) > 1.6 && v.vitesse > 1 ? 1 : 0,
             direction: Math.max(-1, Math.min(1, ecart * 2)), freinMain: Math.abs(ecart) > 1.2 && v.vitesse > 2 };
  }

  function relacherLesPoursuivants() {
    ((B.mission && B.mission.poursuivants) || []).forEach(function (v) { if (v.etat !== 'epave') { v.conducteur = 'trafic'; v.poursuite = false; } });
    if (B.mission) B.mission.poursuivants = [];
  }
```

  `poser()` : dans `dansLaVille`, `if (o.poursuite) poserLaPoursuite(m, o);`. `avancer()` : en tête,
  `relacherLesPoursuivants();`. `nettoyer()` : les relâcher aussi. Export : `commandesDuPoursuivant`.
  `vehicules.js`, la boucle : 
  `else if (v.conducteur === 'poursuivant') { const c = Histoire.commandesDuPoursuivant(v); if (c === 'rails') majConducteur(v); else majPhysique(v, c); }`,
  et la condition des rails : `|| (v.conducteur === 'poursuivant' && v.surRails)`. ⚠️ Les chars nés ici tirent
  `B.rng` (comme la police) : un juge de mission qui compte les dés à l'empreinte peut bouger — le rejouer.

- [ ] **Étape 4 : les voir passer**, `tests/test_police*.py` et `tests/test_vehicules*.py` compris.

- [ ] **Étape 5 : commit** — `feat: la poursuite — un char du gang qui te colle pendant un trajet …`

---

#### Tâche 8 : le type `tenir`

**Fichiers :** `app/missions/__init__.py` (`TYPES_OBJECTIFS` += `"tenir"`), `static/js/histoire.js` (`poser`,
`majObjectif`, `cible`, `ligneObjectif`) ; juges dans `tests/test_chapitres_js.py`.

**Interfaces :** consomme `majRenforts` (tâche 6). Forme : `{"type": "tenir", "texte": …, "lieu": …, "rayon": 6,
"secondes": 90, "strict": false, "groupe": …, "n": …, "renforts": {…}}` (`groupe`/`n`/`renforts` facultatifs).

- [ ] **Étape 1 : les juges qui échouent** :

```python
def _tenir(banc, sortir, strict=False):
    return banc("function (L, o) {" + OUTILS + PLUS_LONGUES + ZZ + """
        L.Jeu.commencer(); L.graine(6);
        const B = L.B, p = B.partie, j = B.joueur, m = greffer(L);
        m.objectifs[1] = { type: 'tenir', texte: 'TIENS LE PONT', lieu: 'pont', rayon: 6, secondes: 10, strict: """ + ("true" if strict else "false") + """ };
        commencer(L, o, 'zz'); jouer(L, o);
        const pont = L.Histoire.lieu('pont'); j.x = pont.x; j.y = pont.y; L.Entites.indexer();
        for (let k = 0; k < 360; k++) o.frame(1);
        if (""" + ("true" if sortir else "false") + """) { j.x += 16 * 12; L.Entites.indexer(); o.frame(2); j.x = pont.x; L.Entites.indexer(); }
        for (let k = 0; k < 360; k++) o.frame(1);
        return { etape: p.mission ? p.mission.etape : null, ligne: p.mission ? L.Histoire.ligneObjectif() : null };
    }""")


def test_tenir_dix_secondes_sans_sortir_avance(banc):
    assert _tenir(banc, sortir=False)["etape"] == 2


def test_tenir_sortir_remet_le_compte_a_zero(banc):
    r = _tenir(banc, sortir=True)
    assert r["etape"] == 1 and "TIENS" in r["ligne"], r


def test_tenir_strict_sortir_fait_rater(banc):
    assert _tenir(banc, sortir=True, strict=True)["etape"] is None
```

- [ ] **Étape 2 : les voir échouer.**

- [ ] **Étape 3 : le code** — `poser()` : `else if (o.type === 'tenir') { B.mission.tenu = 0; if (o.groupe) poserLesCravates(m, Object.assign({}, o, { loin: o.loin || 14 }), enSilence); }`.
  `majObjectif()` :

```js
      case 'tenir': {
        const l = resoudre(o.lieu, m), dedans = l && dist2(j.x, j.y, l.x, l.y) < (o.rayon * TT) * (o.rayon * TT);
        if (!dedans) { if (o.strict && B.mission.tenu > 0) { echouer('hors_zone'); return; } B.mission.tenu = 0; B.mission.attend = 'REVIENS : ' + texteDObjectif(o); return; }
        B.mission.attend = null;
        if (o.groupe) {
          const cibles = B.mission.entites.filter(function (e) { return e.type === 'pieton' && e.cible && e.etape === p.etape; });
          majRenforts(m, o, p, cibles, cibles.filter(function (e) { return !e.vivant || e.etat === 'assomme'; }).length);
        }
        if (++B.mission.tenu >= (o.secondes || 60) * 60) avancer();
        return;
      }
```

  `cible()` : `else if (o.type === 'tenir') l = resoudre(o.lieu, m);`. `ligneObjectif()` : le compte à rebours à
  côté des autres (` ' + Math.ceil(((o.secondes || 60) * 60 - (B.mission.tenu || 0)) / 60) + ' S'`), là où
  `course` ajoute son `i/n`. `hors_zone` existe déjà dans `ECHECS` ; le pilote doit le mettre dans l'`echec` du
  chapitre s'il se sert de `strict`.

- [ ] **Étape 4 : les voir passer.**

- [ ] **Étape 5 : commit** — `feat: tenir — rester au lieu pendant que les vagues arrivent …`

---

#### Tâche 9 : `relais` — le fuyard qui change de char

**Fichiers :** `app/missions/__init__.py` (`OPTIONS_OBJECTIFS` += `"relais"`), `static/js/histoire.js`
(`poserLeFuyard`, `case 'ramasser'`) ; juge dans `tests/test_chapitres_js.py`.

- [ ] **Étape 1 : le juge qui échoue** :

```python
def test_le_fuyard_saute_dans_un_autre_char_avant_de_tomber(banc):
    r = banc("function (L, o) {" + OUTILS + PLUS_LONGUES + ZZ + """
        L.Jeu.commencer(); L.graine(6);
        const B = L.B, p = B.partie, m = greffer(L);
        m.objectifs[1] = { type: 'ramasser', texte: 'RATTRAPE LE VOLEUR', cible: 'fuyard', vehicule: 'moto', relais: 1 };
        commencer(L, o, 'zz'); jouer(L, o);
        const premier = B.mission.fuyard; premier.vie = 1; jouer(L, o);
        const second = B.mission.fuyard, tombe1 = !!B.mission.fuyardTombe;
        second.vie = 1; jouer(L, o);
        return { autre: second !== premier, tombe1: tombe1, tombe2: !!B.mission.fuyardTombe };
    }""")
    assert r == {"autre": True, "tombe1": False, "tombe2": True}
```

- [ ] **Étape 2 : le voir échouer.**

- [ ] **Étape 3 : le code** — `poserLeFuyard(m, o, depuis)` : `const ici = depuis || ouEstLeJoueurEnVille();`.
  `case 'ramasser'`, à la place de l'appel direct à `faireTomberLeFuyard()` :

```js
          if (j.dansVehicule === v || v.etat === 'epave' || (d < 40 && Math.abs(v.vitesse) < 0.6) || v.vie < v.vieMax * 0.5) {
            if ((B.mission.relais || 0) < (o.relais || 0)) {
              B.mission.relais = (B.mission.relais || 0) + 1;
              v.fuyard = false; v.conducteur = null; v.etat = v.etat === 'epave' ? 'epave' : 'stationne';
              Hud.message('IL SAUTE DANS UN AUTRE CHAR !', 150);
              dansLaVille(function () { poserLeFuyard(m, o, { x: v.x, y: v.y }); });
            } else faireTomberLeFuyard();
          }
```

  ⚠️ Lire `poserLeFuyard` jusqu'au bout : s'il remplit `B.mission.fuyard` et `B.mission.entites`, l'ancien char
  doit sortir de `B.mission.entites` (sinon `nettoyer` le retire en fin de mission, ce qui est voulu) ; `avancer()`
  remet `B.mission.relais = 0`.

- [ ] **Étape 4 : le voir passer**, plus les juges de m2 et m50 (leurs fuyards, `grep -l fuyard tests/*.py`).

- [ ] **Étape 5 : commit** — `feat: le fuyard change de char — relais …`

---

#### Tâche 10 : le pilote — La Pointe en six actes

**Fichiers :**
- Créer : `app/missions/pointe.py`
- Supprimer : `app/missions/p02.py`, `p04.py`, `p05.py`, `p09.py`, `p10.py`, `p11.py` (l'histoire les garde)
- Modifier : `app/missions/__init__.py` (imports, `CATALOGUE` : `pointe.MISSION` à la place des six), 
  `tests/test_arc_p_js.py` (réécrit), `tests/test_sur_place_js.py:343` (p05 n'a plus de `sur_place` de mission),
  `docs/personnages/` si une fiche nomme p02…p11, `docs/carte.md` si elle les liste
- Voix : `static/audio/histoire-*-p0[2459]-*.mp3`, `…-p1[01]-*.mp3` (54 fichiers) renommés, les neuves générées

**Interfaces :** consomme tout ce qui précède. Slug `pointe`, titre « La Pointe », donneur `bilodeau`,
`prerequis: ["p01"]`, `remplace: ["p02", "p05", "p04", "p10", "p09", "p11"]`, `echec: ["mort", "arrete"]`,
`recompense` = 150 + 120 + 200 + 250 + la prime de p09 + celle de p11, `donne` = celui de p11 (`libere: pointe`,
sa `manchette`, son `message`).

- [ ] **Étape 1 : garder la trace des voix** — AVANT de toucher un fichier, dans le scratchpad :

```bash
UV_PROJECT_ENVIRONMENT=/Users/martingagne/dev/bandini/.venv uv run python -c "
import json; from app import missions
v=[r for r in missions.repliques() if r['mission'] in ('p02','p04','p05','p09','p10','p11')]
json.dump(v, open('$SCRATCH/voix_pointe_avant.json','w'), ensure_ascii=False, indent=1)"
```

- [ ] **Étape 2 : écrire le chapitre** — `app/missions/pointe.py`. Les objectifs des six missions, dans l'ordre
  des actes, chacun précédé de son marqueur ; toutes les répliques existantes gardées **mot pour mot** avec leur
  `jeu=`, déplacées ainsi :
  - l'`appel` et l'`intro` de p02 restent l'`appel` et l'`intro` du chapitre ;
  - l'`appel` + l'`intro` des cinq autres deviennent des `pendant` sur l'étape de LEUR marqueur (dites à
    l'ouverture de l'acte) ; leur `fin` devient des `pendant` sur le marqueur de l'acte SUIVANT (dites en personne
    en arrivant au `retourner`) ; la `fin` de p11 reste la `fin` du chapitre ;
  - les `pendant` gardent leur objectif, décalé de la place qu'il a dans le chapitre ;
  - les `echec` : celui de p02 reste, les autres disparaissent (un seul `echec` par mission) — noter lesquels dans
    les Notes du jalon ;
  - chaque `retourner` d'acte porte le `donne` de sa mission d'origine (sauf p11, dont le `donne` est celui du
    chapitre) ; l'acte 2 (p05) porte `sur_place: {"lieu": "phare", "heure": "nuit"}` sur son marqueur (p05 en avait
    un de mission ; sa `frontiere` tombe) ; l'arme `fronde` de p05 passe dans le `donne` du `retourner` de l'acte 2.
  - **ce qui fait durer**, là où l'histoire le justifie : au pont (acte 1) `renforts: {"vagues": 1, "n": 2}` ; au
    phare (acte 5) le `tuer` de p09 devient un `tenir` de 90 s avec `groupe: "skateux"`, `n: 3`,
    `renforts: {"vagues": 2, "n": 2}`, suivi du `parler` d'Ovila ; vers le Brouillard (acte 6) le `proteger` de Zed
    porte `poursuite: {"groupe": "skateux", "chars": 1}`.
  - des **répliques de pont** neuves (3 à 6), chacune avec son `jeu=`, là où un acte s'ouvre sans que son donneur
    soit là (le Trappeur qui rappelle au téléphone, Zed qui hèle) — « qui parle se nomme » une fois par donneur.
  - le module suit la forme des autres (`"""La mission …"""`, `from ._commun import _l, _p`, `MISSION = {…}`) ;
    un commentaire en tête dit que c'est le premier chapitre et renvoie à ce jalon.

- [ ] **Étape 3 : le catalogue** — `__init__.py` : retirer les six de l'import et du `CATALOGUE`, ajouter
  `pointe` à la place de p02 ; `zed.arrive_apres` reste `"p02"` (l'acte 1 fini le marque fait, tâche 2).
  `uv run pytest tests/test_chapitres.py tests/test_missions.py tests/test_definitions.py -q` : vert.

- [ ] **Étape 4 : renommer les voix payées** — un script du scratchpad : pour chaque réplique de
  `voix_pointe_avant.json`, trouver dans `missions.repliques()` la réplique neuve de mission `pointe` au même
  (`qui`, `texte`), et `git mv static/audio/histoire-<ancien slug>.mp3 static/audio/histoire-<nouveau slug>.mp3`
  (et la variante `-hiver` si elle existe). Il s'arrête net si une ancienne n'a pas de neuve. Vérifier :
  `git ls-files static/audio | grep -c -- '-pointe-'` = 54.

- [ ] **Étape 5 : générer les voix neuves** — `mcp__elevenlabs__elevenlabs_status` avant ;
  `uv run python scripts/audio_elevenlabs.py --mission pointe` (lire `--help` : la forme exacte de la commande est
  dans `docs/reprendre-le-travail.md`, section audio) ; `elevenlabs_status` après, et dire à Martin ce qui est
  dépensé. Le poids du dépôt (plafond 80 Mo) : `du -sh static/audio`.

- [ ] **Étape 6 : réécrire `tests/test_arc_p_js.py`** — un seul chapitre joué au bouton, dans l'ordre des actes, en
  reprenant les gestes des juges d'aujourd'hui (le pont, les collets de nuit, la course à pied, le saut, le phare
  tenu, Zed au Brouillard) et en jugeant à chaque acte : le carton, `Chapitres.donneurDe`, la réplique d'ouverture
  dite (`dites`), le `donne` de l'acte (`calmes` contient `skateux` après l'acte 3, la `fronde` après l'acte 2), et
  à la fin `libere` contient `pointe`, une seule prime, `durees.pointe.actes.length === 6`. Garder `p04` trop lent
  (le chrono de Zed rate l'ACTE, et REPRENDRE L'ACTE 3 le rejoue). `test_sur_place_js.py:343` : l'ensemble perd
  `p05`.

- [ ] **Étape 7 : les juges d'une mission neuve** — `tests/test_missions_en_scene_js.py`, `tests/test_definitions.py`,
  `tests/test_interpretation.py`, `tests/test_audio.py`, `tests/test_chapitres*.py`, `tests/test_arc_p_js.py`,
  `tests/test_devants.py`, et `uv run ruff check .`.

- [ ] **Étape 8 : le chronomètre, pour vrai** — jouer le chapitre au banc à vitesse de joueur n'a pas de sens ;
  noter dans les Notes la durée que le banc mesure (`durees.pointe`) comme plancher, et demander à Martin de le
  jouer : sa partie (`donnees/bandini.sqlite3`, `parties`) dira la vraie durée.

- [ ] **Étape 9 : commit** — `feat: La Pointe en six actes — le premier chapitre …`

---

#### Tâche 11 : atterrir

- [ ] `docs/comment-monter-les-missions.md` : une section « Un chapitre » (le marqueur, `remplace`, les options
  `renforts`, `poursuite`, `etoiles`, `donne`, les types `tenir` et le `relais`) — changer la façon de faire, c'est
  ajuster toute la doc dans le même passage.
- [ ] Les Notes de ce jalon : ce qui est livré, les `echec` retirés, la durée mesurée, ce qui reste (les autres arcs).
- [ ] La ligne du plan reste ⬜ **en cours** (les autres arcs suivent) ; la ligne M16 perd « cent » dans son texte
  si Martin le confirme.
- [ ] Atterrir selon `base-du-worktree-dev-local` : `checkout --detach dev`, `cherry-pick` des commits, conflits de
  version seulement, `merge --ff-only` dans l'arbre principal ; la suite complète APRÈS l'atterrissage.

## Notes

**Tranche 1 livrée le 30 sept. 2026 : le moteur et La Pointe.** Ce qui reste : les autres arcs, un à la fois, après
que Martin a joué le pilote (son chronomètre au carnet dira si on tient 5 à 10 minutes).

**Le moteur** (`static/js/chapitres.js`, et `histoire.js` qui l'appelle) :
- le type `acte` et `remplace` (`erreurs_de_chapitre`, `donneur_final`, `remplacee_par`) ; le catalogue porte
  `actes: [[étape, donneur]]` — les objectifs ne sont pas au paquet, et le téléphone, les bulles et le carnet
  doivent savoir quel donneur attend ;
- l'acte se joue : son carton, son donneur (`donneurDe` : l'acte en cours, celui où l'on reprendra, ou le dernier
  une fois la mission faite), le point de reprise ; un `retourner` au milieu passe à l'acte suivant ;
- ⚠️ **qui arrive après une mission remplacée arrive entre deux actes** (`Histoire.arriverApres`, sorti de
  `jouerLaFin`) : Zed n'était posé qu'au chargement, et l'acte 3 n'aurait trouvé personne ;
- une vieille partie commence au premier acte pas fait ; toutes faites, le chapitre l'est ;
- REPRENDRE L'ACTE N / PLUS TARD après l'hôpital ou le poste ; la reprise rend la place en ville, un char du même
  modèle et l'arme de l'acte, même confisquée ; PLUS TARD garde l'acte, et le téléphone dit « RAPPEL » ;
- le chronomètre (`partie.durees`, par acte, sans pause ni menu), au carnet à côté de FAITE ;
- `donne`, `etoiles`, `renforts`, `poursuite`, `relais` sur un objectif, et le type `tenir`. La tournée n'est pas un
  type : une `course` sans chrono.

**La Pointe** (`app/missions/la_pointe.py` — pas `pointe`, le nom du district, que le code nomme) : p02, p05, p04,
p10, p09 et p11 en six actes, 21 étapes. Les répliques d'origine gardées mot pour mot : **47 voix payées renommées**.
Retirées : les six échecs (un seul échec par mission — le neuf dit « La Pointe va vous attendre ») et l'appel de p10,
où Zed se renommait à côté de toi (7 mp3). Neuves : l'échec, les renforts du pont, le phare à tenir, l'auto des
Skateux, le défi du saut sans « c'est Zed » — **5 voix, 93 caractères** (61 095 restants). Ce qui fait durer : deux de
renfort au pont, le phare à tenir 90 s contre trois vagues, une auto de Skateux jusqu'au Brouillard. La prime est
celle des six (1 520 $), à la fin. Tombés : la `frontiere` de p05 et les scènes d'intro écrites de p09 et p11 (leurs
intros se disent à l'ouverture de l'acte, en boîte ordinaire plutôt qu'au combiné).

**Les juges** : `test_chapitres.py` (la forme), `test_chapitres_js.py` (le moteur sur une mission greffée, chaque
règle vue rouge sans elle), `test_arc_p_js.py` réécrit acte par acte (trop lent à la course : REPRENDRE L'ACTE 3),
`test_sur_place_js.py`, et le plafond de répliques de `test_missions.py` : 18 **par acte**.
