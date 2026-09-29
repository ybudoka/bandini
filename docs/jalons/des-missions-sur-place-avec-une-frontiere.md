# Des missions sur place, avec une frontière

← [le plan](../plan.md) · [les jalons livrés](README.md)

## Fiche

Demande de Martin (29 sept. 2026) : « pour certaines missions, je veux des raccourcis vers le moment
de la journée et l'endroit, avec une frontière qui nous garde dans la mission — le tout réutilisable ».
Tranché avec lui : c'est pour **le joueur** (pas une triche), le saut est **automatique** (pas offert),
la frontière est **un district ou un bloc** (pas un cercle), et la franchir **avertit puis fait rater**.

Deux clés **indépendantes** dans le fichier de la mission — une mission peut avoir l'une sans l'autre
(une poursuite gardée dans les Quais n'a pas besoin de saut) :

```python
sur_place = {"lieu": "villa_chemin", "heure": "nuit"}                 # heure : "nuit" ou (0.75, 0.95)
frontiere = "bloc:villa"                                              # ou un district : "quais", "pointe"…
```

**Le saut (`sur_place`).** Après l'accueil du donneur (en personne ou au combiné — l'accueil se joue,
c'est le trajet qu'on saute) : fondu au noir, l'horloge **avance** jusqu'à la fenêtre voulue (jamais en
arrière ; déjà dedans, elle ne bouge pas), et l'on se relève à `lieu`, à pied. Les étoiles s'effacent (des heures ont passé, comme à la sieste). Passer minuit
est un **vrai changement de jour** (`nouveauJour` : dette, revenus) — le temps a vraiment passé. Un lieu
de bloc passe par `Blocs.sauter`, qui existe déjà. Le premier `aller … nuit` sur ce lieu est alors fait
en arrivant.

**La frontière (`frontiere`).** Active dès l'arrivée (dès le début sans `sur_place`), jusqu'à la fin de
la mission. Dehors : « RETOURNE DANS LES QUAIS » et un compte de **10 s** au HUD ; revenir l'annule, zéro
fait rater la mission (raison `hors_zone`). Le compte se fige sous une scène ou un menu. Dans une pièce,
c'est la porte qui compte (`B.exterieur`) ; pour un bloc, être en ville, c'est être dehors. Le district
se lit par `Monde.zoneA(x, y).district` (les neuf, nord compris). La mini-carte et la grande carte
grisent le hors-zone.

**Pilotes** : `v01` « La clé du maire » (`bloc:villa`, de nuit — une infiltration ne se quitte pas) et
`q13` « La nuit des Morues » (le district de l'hôtel, de nuit — on tient l'hôtel).

- ⚠️ **`char` est reporté** (décidé en écrivant le plan) : aucun des deux pilotes n'en a besoin, et
  monter dans un char de mission garé sans conducteur compte comme un **vol** (`Vehicules.monter` pose
  `vol_vehicule` sur tout char stationné qui n'est ni `vole` ni `aToi`) — il faudra trancher qui possède
  ce char. On l'ajoutera avec la première mission qui le demande.
- ⚠️ **Refusé au chargement** (jugé) : un district ou un bloc inconnu, une `heure` mal formée, un `lieu`
  de `sur_place` inconnu, et **tout lieu d'objectif hors de la frontière** de sa mission.
- ⚠️ **Le dernier objectif de v01 se joue au bord** (« RESSORS PAR LE CHEMIN ») : la mission doit être
  finie AVANT que le passage ne ramène en ville, sinon le compte partirait sur une mission gagnée. À
  mesurer au banc.
- ⚠️ **Juges de banc**, chacun cassé par une mutation : le saut pose au lieu et à l'heure (et ne recule
  jamais l'horloge) ; sortir lance le compte, zéro fait rater, revenir l'annule ;
  une scène fige le compte ; la pièce (la porte compte) ; le bloc (en ville = dehors) ; une mission
  sans les clés ne change pas. Et `test_missions_en_scene_js` pour les deux pilotes.
- ⚠️ La doc suit dans le même passage : la table des clés de
  [comment-monter-les-missions.md](../comment-monter-les-missions.md).

## Notes

✅ **Livré** (29 sept. 2026).

- **`static/js/surplace.js`** (`SurPlace`) porte tout ; `histoire.js` ne fait que l'appeler à la fin de
  l'intro (`poserPuisDireLIntro`) et dans `maj` (même dans une pièce) ; `hud.js` y prend le suffixe de la
  ligne d'objectif (« — REVIENS ! 7 S ») et le gris des deux cartes. `Blocs.entrerAuNoir` sort du `faire`
  de `Blocs.sauter` : le saut vers un lieu de bloc tient son propre fondu (celui de la sieste, « LE SOIR
  VENU »), et le noir attend la carte du bloc.
- **Pilotes** : `v01` (`bloc:villa`, de nuit au chemin de la villa) et `q13` (`quais`, de nuit devant
  l'hôtel). Leur premier `aller … nuit` se fait en arrivant.
- ⚠️ **`gardee` vit dans `B.partie.mission`** (sauvegardée) : `B.mission` se refait vide au
  rechargement, et une partie reprise en pleine mission perdait sa frontière.
- ⚠️ **Une pièce et un bloc n'ont pas de zones** : `Monde.zoneA` y rend `null`. La position qui compte
  est lue sur la carte de la VILLE (`B.exterieur` : la porte ; `B.bloc.ville` : le passage).
- ⚠️ **`char` reporté** : monter dans un char de mission garé compte comme un vol.
- ⚠️ **Les juges** (`test_sur_place.py`, 6 ; `test_sur_place_js.py`, 18) ferment chaque réplique à
  chaque image (`vivre`) : l'intro et les `pendant` figent la ville, et deux juges « rien ne bouge »
  passaient à vide. La pause se juge par `Jeu.pause()` (c'est son menu qui fige), pas par `B.etat`. Le
  juge de la pièce est devenu deux juges (une pièce hors frontière compte, une pièce dedans non) : le
  premier ne mordait pas. Quinze mutations, toutes rouges ; un garde-fou reste vert par nature (v01 finit
  au bord sans rater).
- Captures Chromium regardées : la grande carte laisse les Quais en clair et grise le reste ; sur la
  mini-carte le gris est discret sur l'eau.
- ⚠️ **Revue finale (30 sept. 2026)**, deux correctifs : (1) **v01 se ratait la clé en poche** — la bande
  d'herbe à l'est de la palissade mène à la sortie sans passer à trois tuiles du chemin, et sous la
  frontière, ressortir en ville sans avoir « fini » faisait rater ; le dernier objectif passe au rayon 6
  (la sortie est à 5,4 tuiles au plus, la ronde du garde à plus de dix). Le garde-fou « v01 finit au
  bord » passait **à vide** : `avancer` passe à l'étape SUIVANTE, et poser l'étape 2 puis avancer
  finissait la mission sur-le-champ — il part maintenant de l'étape 2 et le vérifie. (2) **Dans une
  pièce, le compte tournait sans se dire** (la ligne d'objectif s'y tait) : `SurPlace.ligne` écrit
  « RETOURNE DANS LES QUAIS — REVIENS ! 7 S » même dedans. Reportés (mineurs) : un saut lancé depuis une
  pièce du bloc visé ; une carte de bloc qui n'arrive jamais arme quand même la frontière ; le gris
  ignore la zone `large` (district `baie`) et griserait l'île sous `baie` ; « PLUS TARD » pour une
  fenêtre du lendemain ; un lieu de bloc sous une frontière de district n'est pas jugé ; le message
  d'échec vit hors d'`echouer`.

## Plan d'implémentation

> **Pour l'exécutant :** superpowers:subagent-driven-development (recommandé) ou superpowers:executing-plans,
> tâche par tâche ; les étapes se cochent (`- [ ]`). Tout se fait dans un worktree détaché sur le `dev`
> local ; pytest avec `UV_PROJECT_ENVIRONMENT=~/dev/bandini/.venv` ; `uv run ruff check .` avant d'atterrir.

**But :** deux clés de mission réutilisables — `sur_place` (le saut à l'heure et au lieu) et `frontiere`
(un district ou un bloc qu'on ne quitte pas plus de 10 s) — et deux pilotes, `v01` et `q13`.

**Architecture :** un module neuf, `static/js/surplace.js` (`SurPlace`), porte tout le comportement ;
`histoire.js` ne fait que l'appeler à deux endroits (la fin de l'intro, et `maj`), sans jamais nommer une
mission. Côté Python, `app/missions/__init__.py` gagne `hors_zone` dans `ECHECS` et un juge de forme,
`erreurs_de_sur_place(mission)` ; la ville (le district d'un lieu) ne se juge que dans les tests.

**Technique :** JS du navigateur (modules `const X = (function () {…})()`, exportés dans `window.BANDINI`),
Python 3 / pytest, juges de banc sous Node (`banc`, `tests/banc.js`, qui lit l'ordre des scripts dans
`templates/index.html`).

**Spec :** la fiche ci-dessus.

### Contraintes globales

- Clés : `sur_place = {"lieu": <lieu>, "heure": "nuit" | (h0, h1)}` — `h0`, `h1` des flottants dans
  `[0, 1)` (0 = minuit, 0,5 = midi) ; `frontiere = "<district>" | "bloc:<slug>"`.
- Districts : les zones dont `z.district == z.slug` — `faubourg, erables, shop, quais, baie, pointe, ile,
  aeroport, friches, canton, gare`. Blocs : `app/blocs` (`villa`, `cineparc`, `galeries`, `rang`).
- Compte : **10 s = 600 images**. Raison d'échec : `hors_zone`.
- `"nuit"` se relève à `B.defs.economie.sieste.reveil` (0,865, 20 h 45 — la même que la sieste).
- L'horloge n'avance que vers l'avant ; passer minuit appelle `Missions.nouveauJour()` pour chaque jour
  (le patron de la prison, `missions.js:475`).
- `histoire.js` ne contient aucun slug de mission entre guillemets (`test_histoire_ne_nomme_aucune_mission`).
- Textes du HUD en MAJUSCULES accentuées ; commentaires sans accents dans le JS, comme le code voisin.

### Ce que la revue doit guetter

1. **Rechargée en pleine mission** : la frontière reste active (l'état « gardée » vit dans
   `B.partie.mission`, qui se sauvegarde, pas dans `B.mission`, qui se refait vide) — juge en tâche 3.
2. **Dans une pièce** : `Monde.zoneA` y rend `null` (les pièces n'ont pas de zones) — la position qui
   compte est celle de la porte, lue sur la carte de la VILLE (`B.exterieur.carte`) — juge en tâche 3.
3. **Dans un bloc avec une frontière de district** : on compte le passage du bloc
   (`B.bloc.ville.carte`, `.x`, `.y`) — juge en tâche 3.
4. **Pause, carte, scène** : le compte ne bouge pas (la boucle n'appelle pas `Histoire.maj`) — juge en tâche 3.
5. **Le dernier objectif de v01 au bord du bloc** : la mission est réussie avant que le passage ne ramène
   en ville ; aucun échec après une réussite — juge en tâche 5.

---

### Tâche 1 : la forme des clés, jugée en Python

**Fichiers :**
- Modifier : `app/missions/__init__.py` (`ECHECS` `:100`, `class Mission` `:396-418`, une fonction neuve
  près de `erreurs_de_mise_en_scene` `:1366`)
- Créer : `tests/test_sur_place.py`

**Interfaces :**
- Produit : `missions.erreurs_de_sur_place(mission: dict) -> list[str]` (vide si tout va) ;
  `missions.DISTRICTS_DE_FRONTIERE: frozenset[str]` ; `"hors_zone" in missions.ECHECS`.

- [ ] **Étape 1 : écrire les juges qui échouent**

```python
"""Des missions sur place, avec une frontière — la forme des clés, et la ville.

Demande de Martin (29 sept. 2026) : des raccourcis vers l'heure et l'endroit, et une frontière qui
garde dans la mission. `sur_place` saute le trajet et l'attente ; `frontiere` fait rater la mission
qu'on quitte plus de dix secondes.
"""

import copy

from app import blocs, missions
from tests import villes


def _mission(**cles):
    m = copy.deepcopy(next(m for m in missions.CATALOGUE if m["slug"] == "q13"))
    m.pop("sur_place", None)
    m.pop("frontiere", None)
    m.update(cles)
    return m


def test_hors_zone_est_une_raison_d_echec():
    assert "hors_zone" in missions.ECHECS


def test_une_mission_sans_les_cles_n_a_rien_a_redire():
    assert missions.erreurs_de_sur_place(_mission()) == []


def test_les_formes_refusees():
    cas = {
        "district inconnu": _mission(frontiere="atlantide"),
        "bloc inconnu": _mission(frontiere="bloc:atlantide"),
        "heure mal formée": _mission(sur_place={"lieu": "hotel", "heure": "midi"}),
        "heure hors de [0, 1)": _mission(sur_place={"lieu": "hotel", "heure": (0.5, 1.2)}),
        "lieu inconnu": _mission(sur_place={"lieu": "atlantide", "heure": "nuit"}),
        "clé inconnue": _mission(sur_place={"lieu": "hotel", "heure": "nuit", "char": True}),
    }
    for attendu, m in cas.items():
        assert any(attendu in e for e in missions.erreurs_de_sur_place(m)), (attendu, missions.erreurs_de_sur_place(m))


def test_les_formes_acceptees():
    assert missions.erreurs_de_sur_place(_mission(sur_place={"lieu": "hotel", "heure": "nuit"}, frontiere="quais")) == []
    assert missions.erreurs_de_sur_place(_mission(sur_place={"lieu": "hotel", "heure": (0.9, 0.1)})) == []
    assert missions.erreurs_de_sur_place(_mission(frontiere="bloc:villa")) == []


def test_tout_le_catalogue_a_des_cles_bien_formees():
    for m in missions.CATALOGUE:
        assert missions.erreurs_de_sur_place(m) == [], (m["slug"], missions.erreurs_de_sur_place(m))


def _district_du_lieu(ville, lieu):
    porte = next((p for p in ville["portes"] if p.get("lieu") == lieu), None)
    if porte is None:
        return None
    trouvee = None
    for z in ville["zones"]:
        if z["x"] <= porte["x"] < z["x"] + z["l"] and z["y"] <= porte["y"] + 1 < z["y"] + z["h"]:
            trouvee = z
    return trouvee and trouvee["district"]


def _lieux_nommes(m):
    """Les lieux que la mission nomme en clair (`lieu`, `ou` sans forme) — ceux qu'on sait situer."""
    noms = [m["sur_place"]["lieu"]] if m.get("sur_place") else []
    for o in m["objectifs"]:
        for cle in ("lieu", "ou"):
            v = o.get(cle)
            if isinstance(v, str) and ":" not in v and v != "donneur":
                noms.append(v)
    return noms


def test_chaque_lieu_nomme_est_dans_la_frontiere():
    """⚠️ Un lieu hors de sa propre frontière rend la mission impossible : on y va, et elle rate."""
    ville = villes.exporter()
    par_bloc = blocs.lieux_des_blocs()
    for m in missions.CATALOGUE:
        f = m.get("frontiere")
        if not f:
            continue
        for lieu in _lieux_nommes(m):
            if f.startswith("bloc:"):
                assert par_bloc.get(lieu) == f[5:], (m["slug"], lieu)
            elif lieu not in par_bloc:
                assert _district_du_lieu(ville, lieu) == f, (m["slug"], lieu, _district_du_lieu(ville, lieu))
```

- [ ] **Étape 2 : les voir échouer** — `uv run pytest tests/test_sur_place.py -q` : `AttributeError`
  (`erreurs_de_sur_place`) et `hors_zone` absent.

- [ ] **Étape 3 : le code**

Dans `ECHECS` (`:100`), ajouter `"hors_zone"` au bout du tuple. Dans `class Mission`, deux clés
facultatives (le `TypedDict` est déjà `total=False` pour ses facultatives — suivre la forme de `exige`) :

```python
    sur_place: dict       # le saut : {"lieu": …, "heure": "nuit" | (h0, h1)} — voir `erreurs_de_sur_place`
    frontiere: str        # un district, ou "bloc:<slug>" : on ne la quitte pas plus de 10 s
```

Près de `erreurs_de_mise_en_scene` :

```python
#: Les districts qu'une frontière peut nommer : ceux de la ville et du nord, plus l'île et l'aéroport
#: (des zones dont le district est elles-mêmes — `carte.exporter()["zones"]`).
DISTRICTS_DE_FRONTIERE = frozenset(
    [d["slug"] for d in carte.DISTRICTS] + [d["slug"] for d in nord.DISTRICTS_NORD] + ["ile", "aeroport"])


def erreurs_de_sur_place(mission: dict) -> list[str]:
    """Ce qui cloche dans `sur_place` et `frontiere` — la FORME seulement ; que chaque lieu soit dans sa
    frontière se juge sur la ville (`tests/test_sur_place.py`)."""
    erreurs = []
    f = mission.get("frontiere")
    if f is not None:
        if f.startswith("bloc:"):
            if f[5:] not in set(blocs.lieux_des_blocs().values()):
                erreurs.append(f"bloc inconnu : {f}")
        elif f not in DISTRICTS_DE_FRONTIERE:
            erreurs.append(f"district inconnu : {f}")
    sp = mission.get("sur_place")
    if sp is not None:
        if set(sp) - {"lieu", "heure"}:
            erreurs.append(f"clé inconnue dans sur_place : {sorted(set(sp) - {'lieu', 'heure'})}")
        lieux = ({p["slug"] for p in carte.SPECIAUX.values()} | {"kiosque", "planque"}
                 | set(blocs.lieux_des_blocs()))
        if sp.get("lieu") not in lieux:
            erreurs.append(f"lieu inconnu dans sur_place : {sp.get('lieu')}")
        h = sp.get("heure")
        if h != "nuit":
            if not (isinstance(h, (tuple, list)) and len(h) == 2):
                erreurs.append(f"heure mal formée : {h!r}")
            elif not all(isinstance(v, (int, float)) and 0 <= v < 1 for v in h):
                erreurs.append(f"heure hors de [0, 1) : {h!r}")
    return erreurs
```

Vérifier en tête du fichier que `carte`, `nord` et `blocs` sont importés (sinon les ajouter à côté des
autres `from app import …` — ⚠️ attention à un import circulaire avec `app.blocs` : s'il y en a un,
importer `blocs` dans la fonction).

- [ ] **Étape 4 : les voir passer** — `uv run pytest tests/test_sur_place.py tests/test_missions.py -q`.
- [ ] **Étape 5 : mutation** — retirer `"hors_zone"` d'`ECHECS`, puis la vérification `0 <= v < 1` : chaque
  fois un juge rougit ; remettre.
- [ ] **Étape 6 : commit** — `git add app/missions/__init__.py tests/test_sur_place.py` puis, dans une
  autre commande, `git commit -m "feat: sur_place et frontiere — la forme des clés, jugée"`.

---

### Tâche 2 : le saut à l'heure et au lieu

**Fichiers :**
- Créer : `static/js/surplace.js`
- Modifier : `templates/index.html` (le `<script>` de `surplace.js` juste AVANT celui de `histoire.js`,
  `:239`), `static/js/jeu.js` (`window.BANDINI` `:1562` : ajouter `SurPlace: SurPlace` après `Histoire`),
  `static/js/blocs.js` (`sauter` `:370` : extraire `entrerAuNoir`), `static/js/histoire.js` (`:1277`)
- Créer : `tests/test_sur_place_js.py`

**Interfaces :**
- Consomme : `Histoire.lieu`, `Histoire.blocDuLieu`, `Histoire.tuileLibre`, `Jeu.transiter`,
  `Jeu.revenirEnVille`, `Missions.nouveauJour`, `Police.remiseAZero`, `Vehicules.descendre`,
  `Blocs.charger`, `Blocs.cartes`.
- Produit : `SurPlace.heureCible(voulue, heure) -> number|null`, `SurPlace.avancerA(h)`,
  `SurPlace.sauter(m, fin)` (appelle toujours `fin()` une fois, et pose `B.partie.mission.gardee = true`
  juste avant) ; `Blocs.entrerAuNoir(slug, ici) -> bool`.

- [ ] **Étape 1 : écrire les juges qui échouent** (`tests/test_sur_place_js.py`)

```python
"""Des missions sur place — le saut, puis la frontière, joués au banc.

Le saut : fondu au noir, l'horloge avance (jamais en arrière), on se relève au lieu, sans étoile.
"""

from tests.outils_missions import OUTILS, PLUS_LONGUES

MISSION = """
  function mission(L, slug) { return L.B.defs.missions.find(function (m) { return m.slug === slug; }); }
  function sauter(L, o, m) {
    let fini = 0;
    L.SurPlace.sauter(m, function () { fini += 1; });
    o.fondu();
    for (let k = 0; k < 400 && L.B.transition; k++) o.frame(1);
    return fini;
  }
"""


def test_le_saut_avance_l_horloge_jusqu_a_la_nuit_et_pose_au_lieu(banc):
    r = banc("function (L, o) {" + OUTILS + MISSION + """
        L.Jeu.commencer(); L.graine(6);
        const B = L.B, p = B.partie, j = B.joueur;
        commencer(L, o, 'q13');
        p.heure = 0.40; const jour = p.jour;
        B.recherche.etoiles = 2;
        const m = Object.assign({}, mission(L, 'q13'), { sur_place: { lieu: 'hotel', heure: 'nuit' } });
        const fini = sauter(L, o, m);
        const h = L.Histoire.lieu('hotel');
        return { fini: fini, heure: p.heure, jour: p.jour - jour, nuit: L.Monde.estNuit(p.heure),
                 loin: Math.hypot(j.x - h.x, j.y - h.y), etoiles: B.recherche.etoiles,
                 gardee: !!p.mission.gardee };
    }""")
    assert r["fini"] == 1
    assert r["nuit"] and r["jour"] == 0 and abs(r["heure"] - 0.865) < 1e-6
    assert r["loin"] < 4 * 16
    assert r["etoiles"] == 0
    assert r["gardee"]


def test_le_saut_ne_recule_jamais_l_horloge(banc):
    r = banc("function (L, o) {" + OUTILS + MISSION + """
        L.Jeu.commencer(); L.graine(6);
        const p = L.B.partie; commencer(L, o, 'q13');
        p.heure = 0.93; const jour = p.jour;
        sauter(L, o, Object.assign({}, mission(L, 'q13'), { sur_place: { lieu: 'hotel', heure: 'nuit' } }));
        return { heure: p.heure, jour: p.jour - jour };
    }""")
    assert r["jour"] == 0 and r["heure"] >= 0.93


def test_une_fenetre_de_demain_passe_minuit_pour_vrai(banc):
    r = banc("function (L, o) {" + OUTILS + MISSION + """
        L.Jeu.commencer(); L.graine(6);
        const p = L.B.partie; commencer(L, o, 'q13');
        p.heure = 0.60; const jour = p.jour;
        let nouveaux = 0; const vrai = L.Missions.nouveauJour;
        L.Missions.nouveauJour = function () { nouveaux += 1; return vrai.apply(this, arguments); };
        sauter(L, o, Object.assign({}, mission(L, 'q13'), { sur_place: { lieu: 'hotel', heure: [0.25, 0.30] } }));
        L.Missions.nouveauJour = vrai;
        return { heure: p.heure, jour: p.jour - jour, nouveaux: nouveaux };
    }""")
    assert r["jour"] == 1 and r["nouveaux"] == 1
    assert abs(r["heure"] - 0.25) < 1e-6


def test_le_saut_sort_de_la_piece_et_du_char(banc):
    r = banc("function (L, o) {" + OUTILS + MISSION + """
        L.Jeu.commencer(); L.graine(6);
        const B = L.B, j = B.joueur; commencer(L, o, 'q13');
        const porte = L.Monde.carte.portes.find(function (p) { return p.lieu === 'planque'; });
        j.x = porte.x * L.TT + 8; j.y = (porte.y + 1) * L.TT + 10; o.entrer(porte);
        const dedans = !!B.interieur;
        sauter(L, o, Object.assign({}, mission(L, 'q13'), { sur_place: { lieu: 'hotel', heure: 'nuit' } }));
        return { dedans: dedans, apres: !!B.interieur, char: !!j.dansVehicule };
    }""")
    assert r["dedans"] and not r["apres"] and not r["char"]


def test_un_lieu_de_bloc_fait_entrer_dans_le_bloc(banc):
    r = banc("function (L, o) {" + OUTILS + MISSION + """
        L.Jeu.commencer(); L.graine(6);
        const B = L.B, j = B.joueur; commencer(L, o, 'q13');
        sauter(L, o, Object.assign({}, mission(L, 'q13'), { sur_place: { lieu: 'villa_chemin', heure: 'nuit' } }));
        const l = L.Histoire.lieu('villa_chemin');
        return { bloc: B.bloc && B.bloc.slug, loin: l ? Math.hypot(j.x - l.x, j.y - l.y) : -1 };
    }""")
    assert r["bloc"] == "villa"
    assert 0 <= r["loin"] < 4 * 16


def test_une_mission_sans_sur_place_ne_bouge_rien(banc):
    r = banc("function (L, o) {" + OUTILS + MISSION + """
        L.Jeu.commencer(); L.graine(6);
        const B = L.B, p = B.partie, j = B.joueur; commencer(L, o, 'q13');
        p.heure = 0.40; const x = j.x, y = j.y;
        const m = Object.assign({}, mission(L, 'q13')); delete m.sur_place;
        let fini = 0; L.SurPlace.sauter(m, function () { fini += 1; });
        return { fini: fini, heure: p.heure, bouge: j.x !== x || j.y !== y, transition: !!B.transition,
                 gardee: !!p.mission.gardee };
    }""")
    assert r == {"fini": 1, "heure": 0.40, "bouge": False, "transition": False, "gardee": True}
```

⚠️ Si `commencer` des outils change la mission courante, le banc des blocs doit servir la carte de la
villa (`/api/bloc/villa`) : regarder comment `tests/test_blocs_js.py` le fait, et copier sa fixture.

- [ ] **Étape 2 : les voir échouer** — `uv run pytest tests/test_sur_place_js.py -q` : `L.SurPlace` indéfini.

- [ ] **Étape 3 : `Blocs.entrerAuNoir`** — dans `blocs.js`, remplacer le corps du `faire` de `sauter`
  par un appel à une fonction neuve, et l'exporter :

```js
  /** Au noir : passe dans le bloc `slug` si sa carte est la, a `ici` (a son arrivee sans lui).
      Rend false sans rien faire si la carte manque ou qu'on est deja dans un bloc. */
  function entrerAuNoir(slug, ici) {
    const b = liste().find(function (q) { return q.slug === slug; }), def = cartes[slug];
    if (!b || !def || B.bloc) return false;
    Jeu.passerDansLeBloc(b, def, recul(b.passage, Monde.carte, B.joueur), ici || null);
    return true;
  }

  function sauter(slug, ici, apres) {
    const b = liste().find(function (q) { return q.slug === slug; });
    if (!b) return false;
    charger(b.slug);
    Jeu.transiter([1, 0, 24], function () {
      if (entrerAuNoir(b.slug, ici) && apres) apres();
    }, null, function () { return !cartes[b.slug]; });
    return true;
  }
```

  et `entrerAuNoir` dans l'objet rendu. `uv run pytest tests/test_blocs_js.py tests/test_chalet_js.py -q`
  doit rester vert.

- [ ] **Étape 4 : `static/js/surplace.js`**

```js
/* Des missions SUR PLACE, gardees par une FRONTIERE (29 sept. 2026).

   Demande de Martin : « pour certaines missions, des raccourcis vers le moment de la journee et
   l'endroit, avec une frontiere qui nous garde dans la mission ». Deux cles de mission, chacune
   facultative, lues ici et nulle part ailleurs :

   - `sur_place` : a la fin de l'intro, fondu au noir, l'horloge AVANCE jusqu'a l'heure voulue et
     l'on se releve au lieu (un lieu de bloc fait entrer dans le bloc) ;
   - `frontiere` : un district ou `bloc:<slug>`. Dehors, dix secondes pour revenir ; a zero, la
     mission rate (`hors_zone`). */
const SurPlace = (function () {
  const HORS_IMAGES = 600;              // 10 s
  const FONDU = [32, 56, 32];           // celui de la sieste (`FONDU_NUIT`)

  /** L'heure ou se relever pour `voulue` (« nuit » ou [h0, h1]), ou null si on y est deja. */
  function heureCible(voulue, heure) {
    if (voulue === 'nuit') return Monde.estNuit(heure) ? null : Math.max(heure, B.defs.economie.sieste.reveil);
    const h0 = voulue[0], h1 = voulue[1];
    const dans = h0 <= h1 ? heure >= h0 && heure <= h1 : heure >= h0 || heure <= h1;
    return dans ? null : h0;
  }

  /** Avance l'horloge jusqu'a `h` — minuit passe, c'est un vrai jour (le patron de la prison). */
  function avancerA(h) {
    const p = B.partie;
    let delta = h - p.heure;
    if (delta < 0) delta += 1;
    p.heure += delta;
    while (p.heure >= 1) { p.heure -= 1; p.jour += 1; Missions.nouveauJour(); }
    if (Math.abs(p.heure - h) < 1e-9) p.heure = h;
  }

  function garder() { if (B.partie.mission) B.partie.mission.gardee = true; }

  /** Pose le joueur a pied pres du lieu (la carte courante : la ville, ou le bloc). */
  function poser(slug) {
    const j = B.joueur, l = Histoire.lieu(slug);
    if (!l) return;
    const place = Histoire.tuileLibre(l.x, l.y, 4) || l;
    j.x = place.x; j.y = place.y; j.vx = 0; j.vy = 0;
    Entites.indexer();
    Monde.centrerCamera(j.x, j.y);
  }

  /** A la fin de l'intro : le saut s'il y en a un, puis `fin()` — toujours, une fois. */
  function sauter(m, fin) {
    const sp = m && m.sur_place;
    if (!sp) { garder(); fin(); return; }
    const bloc = Histoire.blocDuLieu(sp.lieu);
    const cible = heureCible(sp.heure, B.partie.heure);
    if (bloc) Blocs.charger(bloc);
    Jeu.transiter(FONDU, function () {
      const j = B.joueur;
      if (cible !== null) avancerA(cible);
      Police.remiseAZero();
      if (j.dansVehicule) Vehicules.descendre(j, true);
      if (!(bloc && B.bloc && B.bloc.slug === bloc)) Jeu.revenirEnVille();
      if (bloc) Blocs.entrerAuNoir(bloc, null);
      poser(sp.lieu);
      garder();
      fin();
    }, cible === null ? null : (sp.heure === 'nuit' ? 'LE SOIR VENU' : 'PLUS TARD'),
    bloc ? function () { return !Blocs.cartes[bloc]; } : null);
  }

  return { HORS_IMAGES, heureCible, avancerA, sauter };
})();
```

- [ ] **Étape 5 : le crochet** — `histoire.js:1277`, dans `poserPuisDireLIntro` :

```js
    // La fin de l'intro passe par `SurPlace` : le saut a l'heure et au lieu (`sur_place`), et la
    // frontiere qui s'arme (`gardee`) — une mission sans ces cles annonce tout de suite.
    jouerOuDire(m, 'intro', function () { SurPlace.sauter(m, function () { annoncer(m); }); });
```

- [ ] **Étape 6 : les voir passer** — `uv run pytest tests/test_sur_place_js.py tests/test_mise_en_scene.py -q`.
- [ ] **Étape 7 : mutations** — `avancerA` sans le `while` (le juge de minuit rougit) ; `heureCible` sans
  le `Math.max` (le recul rougit) ; `sauter` sans `Jeu.revenirEnVille()` (la pièce rougit) ; sans
  `Police.remiseAZero()` (les étoiles rougissent). Vider `__pycache__` n'est pas utile (JS), remettre.
- [ ] **Étape 8 : commit** — `feat: sur_place — le saut à l'heure et au lieu, après l'intro`.

---

### Tâche 3 : la frontière et son compte

**Fichiers :**
- Modifier : `static/js/surplace.js`, `static/js/histoire.js` (`maj` `:3570`), `static/js/hud.js` (`:3873`)
- Tester : `tests/test_sur_place_js.py`

**Interfaces :**
- Produit : `SurPlace.ici() -> {carte, x, y}` (la position en VILLE), `SurPlace.dedans(f) -> bool`,
  `SurPlace.nom(f) -> string` (en majuscules, « LES QUAIS »), `SurPlace.maj(m)`,
  `SurPlace.suffixe() -> string` (`' — REVIENS ! 7 S'` ou `''`). L'état du compte : `B.mission.hors`
  (en images).

- [ ] **Étape 1 : les juges qui échouent** (à la suite, même fichier)

```python
FRONTIERE = """
  function garder(L, o, slug, f) {
    commencer(L, o, slug);
    L.Histoire.courante().frontiere = f;
    L.B.partie.mission.gardee = true;
  }
  function a(L, lieu) { const l = L.Histoire.lieu(lieu), j = L.B.joueur; j.x = l.x; j.y = l.y + 24; L.Entites.indexer(); }
"""


def test_sortir_lance_le_compte_et_zero_fait_rater(banc):
    r = banc("function (L, o) {" + OUTILS + FRONTIERE + """
        L.Jeu.commencer(); L.graine(6); L.B.joueur.invincible = 1e6;
        garder(L, o, 'q13', 'quais');
        a(L, 'hotel'); o.frame(30);
        const dedans = L.B.mission.hors || 0;
        a(L, 'bar'); o.frame(60);
        const ligne = L.SurPlace.suffixe();
        o.frame(L.SurPlace.HORS_IMAGES);
        return { dedans: dedans, ligne: ligne, mission: L.B.partie.mission && L.B.partie.mission.slug,
                 echecs: L.B.partie.stats.echecs || 0 };
    }""")
    assert r["dedans"] == 0
    assert "REVIENS" in r["ligne"] and "9 S" in r["ligne"]
    assert r["mission"] is None and r["echecs"] == 1


def test_revenir_annule_le_compte(banc):
    r = banc("function (L, o) {" + OUTILS + FRONTIERE + """
        L.Jeu.commencer(); L.graine(6); L.B.joueur.invincible = 1e6;
        garder(L, o, 'q13', 'quais');
        a(L, 'bar'); o.frame(L.SurPlace.HORS_IMAGES - 60);
        a(L, 'hotel'); o.frame(2);
        const remis = L.B.mission.hors;
        a(L, 'bar'); o.frame(L.SurPlace.HORS_IMAGES - 60);
        return { remis: remis, mission: !!L.B.partie.mission };
    }""")
    assert r == {"remis": 0, "mission": True}


def test_la_pause_fige_le_compte(banc):
    r = banc("function (L, o) {" + OUTILS + FRONTIERE + """
        L.Jeu.commencer(); L.graine(6); L.B.joueur.invincible = 1e6;
        garder(L, o, 'q13', 'quais');
        a(L, 'bar'); o.frame(60);
        const avant = L.B.mission.hors;
        L.B.etat = 'pause'; o.frame(L.SurPlace.HORS_IMAGES); L.B.etat = 'jeu';
        return { avant: avant, apres: L.B.mission.hors, mission: !!L.B.partie.mission };
    }""")
    assert r["mission"] and r["apres"] == r["avant"]


def test_dans_une_piece_c_est_la_porte_qui_compte(banc):
    r = banc("function (L, o) {" + OUTILS + FRONTIERE + """
        L.Jeu.commencer(); L.graine(6); L.B.joueur.invincible = 1e6;
        garder(L, o, 'q13', 'quais');
        const B = L.B, j = B.joueur;
        const porte = L.Monde.carte.portes.find(function (p) { return p.lieu === 'planque'; });
        j.x = porte.x * L.TT + 8; j.y = (porte.y + 1) * L.TT + 10; o.entrer(porte);
        o.frame(60);
        return { dedans: !!B.interieur, compte: B.mission.hors || 0 };
    }""")
    assert r["dedans"] and r["compte"] > 0   # la planque est au Faubourg : dehors, même à l'abri


def test_un_bloc_hors_du_district_compte_dehors_et_bloc_dedans(banc):
    r = banc("function (L, o) {" + OUTILS + FRONTIERE + """
        L.Jeu.commencer(); L.graine(6);
        garder(L, o, 'q13', 'bloc:villa');
        a(L, 'hotel'); o.frame(10);
        const enVille = L.SurPlace.dedans('bloc:villa');
        L.Blocs.sauter('villa'); o.fondu(); for (let k = 0; k < 400 && L.B.transition; k++) o.frame(1);
        return { enVille: enVille, dansLeBloc: L.SurPlace.dedans('bloc:villa'),
                 quaisDepuisLeBloc: L.SurPlace.dedans('quais'), erablesDepuisLeBloc: L.SurPlace.dedans('erables') };
    }""")
    assert r == {"enVille": False, "dansLeBloc": True, "quaisDepuisLeBloc": False, "erablesDepuisLeBloc": True}


def test_une_partie_rechargee_garde_sa_frontiere(banc):
    r = banc("function (L, o) {" + OUTILS + FRONTIERE + """
        L.Jeu.commencer(); L.graine(6); L.B.joueur.invincible = 1e6;
        garder(L, o, 'q13', 'quais');
        L.B.mission = null;                        // ce que fait un rechargement : B.mission se refait vide
        a(L, 'bar'); o.frame(60);
        return { compte: L.B.mission ? L.B.mission.hors || 0 : -1 };
    }""")
    assert r["compte"] > 0


def test_pas_de_frontiere_pas_de_compte(banc):
    r = banc("function (L, o) {" + OUTILS + FRONTIERE + """
        L.Jeu.commencer(); L.graine(6); L.B.joueur.invincible = 1e6;
        commencer(L, o, 'q13'); delete L.Histoire.courante().frontiere; L.B.partie.mission.gardee = true;
        a(L, 'bar'); o.frame(L.SurPlace.HORS_IMAGES + 10);
        return { compte: L.B.mission.hors || 0, mission: !!L.B.partie.mission };
    }""")
    assert r == {"compte": 0, "mission": True}
```

⚠️ `villa_chemin` est aux Érables (la villa « au bout des Érables ») : le juge du bloc le suppose —
vérifier avec `_district_du_lieu` sur le passage du bloc avant d'en faire une vérité ; corriger le juge,
pas le code, si le passage est ailleurs.

- [ ] **Étape 2 : les voir échouer.**

- [ ] **Étape 3 : le code** — dans `surplace.js`, avant le `return` :

```js
  /** Ou l'on est EN VILLE : dans un bloc, son passage ; dans une piece, sa porte ; sinon, soi.
      ⚠️ `Monde.zoneA` lit la carte COURANTE, et les pieces et les blocs n'ont pas de zones. */
  function ici() {
    const j = B.joueur;
    if (B.bloc) return { carte: B.bloc.ville.carte, x: B.bloc.ville.x, y: B.bloc.ville.y };
    if (B.interieur && B.exterieur) return { carte: B.exterieur.carte, x: B.exterieur.x, y: B.exterieur.y };
    return { carte: Monde.carte, x: j.x, y: j.y };
  }

  function districtA(carte, x, y) {
    let trouvee = null;
    for (const z of (carte && carte.zones) || []) {
      if (x >= z.x * TT && x < (z.x + z.l) * TT && y >= z.y * TT && y < (z.y + z.h) * TT) trouvee = z;
    }
    return trouvee ? trouvee.district : null;
  }

  function dedans(f) {
    if (f.indexOf('bloc:') === 0) return !!B.bloc && B.bloc.slug === f.slice(5);
    const l = ici();
    return districtA(l.carte, l.x, l.y) === f;
  }

  function nom(f) {
    if (f.indexOf('bloc:') === 0) {
      const b = Blocs.liste().find(function (q) { return q.slug === f.slice(5); });
      return ((b && b.nom) || f.slice(5)).toUpperCase();
    }
    const carte = ici().carte, d = ((carte && carte.def && carte.def.districts) || []).find(function (q) { return q.slug === f; });
    return ((d && d.nom) || f).toUpperCase();
  }

  /** Chaque image de mission, meme dans une piece (`Histoire.maj`). Figee sous une scene, un menu, la
      pause : la boucle n'appelle pas `Histoire.maj`. ⚠️ `gardee` vit dans `B.partie.mission` (sauvegardee),
      pas dans `B.mission` (refaite vide au rechargement). */
  function maj(m) {
    const pm = B.partie.mission;
    if (!m || !m.frontiere || !pm || !pm.gardee || !B.mission) return;
    if (dedans(m.frontiere)) { B.mission.hors = 0; return; }
    if (!B.mission.hors) Hud.message('RETOURNE DANS ' + nom(m.frontiere), 120);
    B.mission.hors = (B.mission.hors || 0) + 1;
    if (B.mission.hors > HORS_IMAGES) {
      const n = nom(m.frontiere);
      Histoire.echouer('hors_zone');
      Hud.message('MISSION RATÉE — TU AS QUITTÉ ' + n, 200);
    }
  }

  function suffixe() {
    const bm = B.mission;
    return bm && bm.hors ? ' — REVIENS ! ' + Math.max(1, Math.ceil((HORS_IMAGES - bm.hors) / 60)) + ' S' : '';
  }
```

  et `return { HORS_IMAGES, heureCible, avancerA, sauter, ici, dedans, nom, maj, suffixe };`.

  Dans `histoire.js`, `maj()`, juste avant `if (!B.interieur) {` :

```js
      SurPlace.maj(courante());
      if (!B.partie.mission) return;             // la frontiere vient de la faire rater
```

  Dans `hud.js:3873` :

```js
      const ligne = !B.interieur ? (function (l) { return l ? l + SurPlace.suffixe() : l; })(Histoire.ligneObjectif()) : null;
```

- [ ] **Étape 4 : les voir passer**, avec `tests/test_histoire_js.py` et `tests/test_hud_js.py`.
- [ ] **Étape 5 : mutations** — `ici()` sans la branche `B.interieur` (la pièce rougit) ; sans la branche
  `B.bloc` (le bloc rougit) ; `gardee` lu dans `B.mission` (le rechargement rougit) ; `maj` appelé dans
  `if (!B.interieur)` (la pièce rougit) ; `B.mission.hors = 0` retiré (revenir rougit).
- [ ] **Étape 6 : commit** — `feat: la frontière d'une mission — dix secondes pour revenir, puis c'est raté`.

---

### Tâche 4 : le hors-zone grisé sur les cartes

**Fichiers :**
- Modifier : `static/js/surplace.js`, `static/js/hud.js` (`miniCarte` `:3256`, `dessinerCarte` `:3517`)
- Tester : `tests/test_sur_place_js.py`, et une capture Chromium (voir la mémoire « capturer une pièce »)

**Interfaces :**
- Produit : `SurPlace.zonesHors(carte) -> [{x, y, l, h}]` (en tuiles, les districts autres que la
  frontière ; vide sans mission gardée, sans frontière de district, ou dans un bloc) ;
  `SurPlace.dessinerSurLaCarte(ctx, pos)` ; `SurPlace.dessinerMini(ctx, MINI, sx, sy)`.

- [ ] **Étape 1 : le juge qui échoue**

```python
def test_les_districts_hors_de_la_frontiere_se_grisent(banc):
    r = banc("function (L, o) {" + OUTILS + FRONTIERE + """
        L.Jeu.commencer(); L.graine(6);
        const avant = L.SurPlace.zonesHors(L.Monde.carte).length;
        garder(L, o, 'q13', 'quais');
        const z = L.SurPlace.zonesHors(L.Monde.carte);
        return { avant: avant, n: z.length, quais: z.some(function (q) { return q.slug === 'quais'; }),
                 faubourg: z.some(function (q) { return q.slug === 'faubourg'; }) };
    }""")
    assert r["avant"] == 0
    assert r["n"] >= 8 and not r["quais"] and r["faubourg"]
```

- [ ] **Étape 2 : le voir échouer.**
- [ ] **Étape 3 : le code** (`surplace.js`)

```js
  const GRIS = 'rgba(11,10,18,0.55)';

  function zonesHors(carte) {
    const m = Histoire.courante(), pm = B.partie && B.partie.mission;
    if (!m || !m.frontiere || !pm || !pm.gardee || m.frontiere.indexOf('bloc:') === 0 || B.bloc) return [];
    return ((carte && carte.zones) || []).filter(function (z) { return z.district === z.slug && z.slug !== m.frontiere; });
  }

  function dessinerSurLaCarte(ctx, pos) {
    ctx.fillStyle = GRIS;
    for (const z of zonesHors(Monde.carte)) {
      const a = pos(z.x * TT, z.y * TT), c = pos((z.x + z.l) * TT, (z.y + z.h) * TT);
      ctx.fillRect(a.x, a.y, c.x - a.x, c.y - a.y);
    }
  }

  function dessinerMini(ctx, mini, sx, sy) {
    ctx.save();
    ctx.beginPath(); ctx.rect(mini.x, mini.y, mini.l, mini.h); ctx.clip();
    ctx.fillStyle = GRIS;
    for (const z of zonesHors(Monde.carte)) ctx.fillRect(mini.x + z.x - sx, mini.y + z.y - sy, z.l, z.h);
    ctx.restore();
  }
```

  (les exporter). `hud.js` : dans `miniCarte`, juste après le `drawImage(mini, …)` et `B.stats.images++` :
  `SurPlace.dessinerMini(ctx, MINI, sx, sy);` ; dans `dessinerCarte`, après `dessinerLaVilleDuBoss(…)` :
  `SurPlace.dessinerSurLaCarte(ctx, pos);   // une mission gardee : le hors-zone grise`.

- [ ] **Étape 4 : le voir passer**, avec `tests/test_hud_js.py`.
- [ ] **Étape 5 : regarder** — une capture Chromium de la mini-carte et de la grande carte, q13 gardée
  aux Quais, copiée dans `~/dev/bandini/captures/` et ouverte dans Aperçu pour Martin. Les juges verts ne
  voient pas un gris qui mange les étiquettes : c'est l'œil qui juge.
- [ ] **Étape 6 : commit** — `feat: la frontière se voit — le hors-zone grisé sur les deux cartes`.

---

### Tâche 5 : les pilotes, v01 et q13

**Fichiers :**
- Modifier : `app/missions/v01.py`, `app/missions/q13.py`
- Tester : `tests/test_sur_place_js.py`, `tests/test_missions_en_scene_js.py`, `tests/test_arc_q_js.py`,
  les juges de v01 (`grep -ln "'v01'" tests/`)

- [ ] **Étape 1 : les juges qui échouent**

```python
def test_q13_se_joue_sur_place_et_gardee(banc):
    r = banc("function (L, o) {" + OUTILS + PLUS_LONGUES + """
        L.Jeu.commencer(); L.graine(6);
        const B = L.B, p = B.partie, j = B.joueur; j.invincible = 1e6;
        faites(L, ['q06']); p.heure = 0.40;
        L.Histoire.demarrer('q13');
        for (let k = 0; k < 40 && !(p.mission && p.mission.gardee); k++) { ecouter(L); o.frame(10); if (B.transition) o.fondu(); }
        const h = L.Histoire.lieu('hotel');
        return { gardee: !!(p.mission && p.mission.gardee), nuit: L.Monde.estNuit(p.heure),
                 loin: Math.hypot(j.x - h.x, j.y - h.y), frontiere: L.Histoire.courante().frontiere };
    }""")
    assert r["gardee"] and r["nuit"] and r["loin"] < 6 * 16 and r["frontiere"] == "quais"


def test_v01_finit_au_bord_sans_rater(banc):
    """⚠️ Le dernier objectif (« RESSORS PAR LE CHEMIN ») se joue au bord du bloc : la mission est
    gagnée avant que le passage ne ramène en ville, et rien ne la fait rater après."""
    r = banc("function (L, o) {" + OUTILS + PLUS_LONGUES + """
        L.Jeu.commencer(); L.graine(6);
        const B = L.B, p = B.partie, j = B.joueur; j.invincible = 1e6;
        faites(L, ['q04']); p.heure = 0.90;
        commencer(L, o, 'v01'); p.mission.gardee = true;
        L.Blocs.sauter('villa'); o.fondu(); for (let k = 0; k < 400 && B.transition; k++) o.frame(1);
        p.mission.etape = 2; L.Histoire.avancer(true);
        const l = L.Histoire.lieu('villa_chemin'); j.x = l.x; j.y = l.y; L.Entites.indexer();
        const echecs = p.stats.echecs || 0;
        for (let k = 0; k < 900; k++) { o.frame(1); if (B.transition) o.fondu(); }
        return { faite: !!p.missionsFaites.v01, echecs: (p.stats.echecs || 0) - echecs };
    }""")
    assert r == {"faite": True, "echecs": 0}
```

  ⚠️ `L.Histoire.avancer` et `L.Histoire.demarrer` : vérifier qu'ils sont exportés (`histoire.js:3604`) ;
  sinon passer par l'outil que `tests/test_infiltration_js.py` utilise pour poser une étape.

- [ ] **Étape 2 : les voir échouer.**
- [ ] **Étape 3 : les clés** — dans `v01.py`, au niveau de `"prerequis"` :

```python
    # Sur place, de nuit, au chemin de la villa (29 sept. 2026) : on ne traverse pas la ville pour
    # attendre la noirceur devant une haie — et une infiltration ne se quitte pas.
    "sur_place": {"lieu": "villa_chemin", "heure": "nuit"},
    "frontiere": "bloc:villa",
```

  et dans `q13.py` :

```python
    # Sur place, de nuit, devant l'hôtel (29 sept. 2026) : on tient l'hôtel, on ne va pas se promener.
    "sur_place": {"lieu": "hotel", "heure": "nuit"},
    "frontiere": "quais",
```

  Relire le texte du premier objectif (« ATTENDS LA NUIT DEVANT L'HÔTEL BANDINI », « VA À LA VILLA DU
  MAIRE, DE NUIT ») : il se fait en arrivant, et ne se lit plus qu'une image. Le garder (une partie
  reprise avant le saut le lit encore).

- [ ] **Étape 4 : les voir passer**, avec `tests/test_sur_place.py`, `tests/test_missions_en_scene_js.py`
  (obligatoire pour une mission touchée), `tests/test_arc_q_js.py`, les juges de v01, `tests/test_definitions.py`
  (le poids du paquet : deux clés de plus au catalogue).
- [ ] **Étape 5 : mutation** — `frontiere: "faubourg"` dans q13 : `test_chaque_lieu_nomme_est_dans_la_frontiere`
  rougit ; remettre.
- [ ] **Étape 6 : commit** — `feat: la clé du maire et la nuit des Morues se jouent sur place, gardées`.

---

### Tâche 6 : la doc, l'architecture, et atterrir

**Fichiers :**
- Modifier : `docs/comment-monter-les-missions.md` (§ 2 `:48-73`, § 8 `:535-551`), `docs/architecture.md`
  (la table des scripts, près de `histoire.js` `:163`), cette fiche (`## Notes`), `docs/plan.md` → `docs/jalons/README.md`

- [ ] **Étape 1 : § 2** — dans le dict annoté, après `"donne"` :

```python
    "sur_place": {"lieu": "hotel", "heure": "nuit"},  # facultatif : après l'intro, fondu, l'horloge AVANCE
                                                      # jusqu'à l'heure ("nuit" ou (h0, h1) dans [0, 1)),
                                                      # on se relève au lieu (un lieu de bloc : dans le bloc)
    "frontiere": "quais",                             # facultatif : un district, ou "bloc:<slug>" ; dehors
                                                      # plus de 10 s, la mission rate (`hors_zone`)
```

  et un paragraphe dessous : les deux clés sont indépendantes ; le compte dort sous une scène, un menu, la
  pause ; dans une pièce la porte compte ; tout lieu nommé doit être dans la frontière (jugé) ; `char`
  n'existe pas encore (le vol, voir la fiche).
- [ ] **Étape 2 : § 8** — `hors_zone` dans la liste d'`ECHECS`, et « une clé `sur_place`/`frontiere` mal
  formée, ou un lieu hors de sa frontière » dans ce que les juges refusent.
- [ ] **Étape 3 : architecture** — une ligne `surplace.js` dans la table des scripts, juste avant
  `histoire.js` : « les missions **sur place** (`sur_place` : le saut à l'heure et au lieu, après l'intro)
  et leur **frontière** (`frontiere` : un district ou un bloc, dix secondes pour revenir, `hors_zone`) ;
  le hors-zone grisé sur les deux cartes ».
- [ ] **Étape 4 : les juges ciblés** — `test_sur_place.py test_sur_place_js.py test_missions.py
  test_mise_en_scene.py test_missions_en_scene_js.py test_arc_q_js.py test_blocs_js.py test_chalet_js.py
  test_histoire_js.py test_hud_js.py test_definitions.py`, puis `uv run ruff check .` ;
  `scripts/verifier_table_des_jalons.py` sur le worktree.
- [ ] **Étape 5 : livrer** — la ligne quitte `docs/plan.md` pour le bas de `docs/jalons/README.md`
  (`✅ **livré**`, date), la note de livraison sous `## Notes` ici ; commit ; atterrir sur `dev`
  (`merge --ff-only`, ou cherry-pick si `dev` a bougé) ; la suite complète APRÈS.
