# Des étages dedans aussi

← [le plan](../plan.md) · [les jalons livrés](README.md)

## Fiche

_Demandé par Martin le 30 sept. 2026_, après [les étages pour vrai](des-etages-pour-vrai-des-maisons-de-luxe-et-des-terrains-clotures.md#fiche)
(vague 1, les façades) : « il faut que les commerces et résidences qui ont plusieurs étages aient aussi plusieurs
étages à l'intérieur ».

**Aujourd'hui** : un logement de 2 ou 3 étages a au plus **une** pièce en haut (`poser_la_piece`, `_haut`) — un
triplex a deux niveaux dedans. Un commerce n'en a aucune, alors que 129 devantures sur 135 peignent 2 ou 3 étages de
logements au-dessus de l'enseigne. Et le nombre d'étages **peint** se décide dans le JS (`logementElargi`,
`etagesDuCommerce` : la profondeur du toit, une rangée de toit toujours visible) sans que Python, qui fait les
pièces, le connaisse.

**La règle** : une porte qui s'ouvre donne sur **autant de niveaux que la façade en peint** — le rez, plus `hauts`.
Ce qu'on voit de la rue fait foi.

**Tranché avec Martin (30 sept. 2026)** :

- **En haut d'un commerce, le logement du commerçant** : un escalier au fond de la boutique, et des logements meublés
  comme l'étage d'un plex (la façade y peint des fenêtres de logement).
- **Python compte, le JS peint** : une seule source pour le dehors et le dedans.

**Le design** :

1. **Le compte, en Python** — `app/etages.py`, à la toute fin de `generer` (après la bande nord : le Petit-Canton
   compris), sur la ville finie, **sans un dé et sans une tuile** : le portage du calcul du JS (les toits d'une même
   matière reliés, `teintesDesToits().qui` ; le mur étendu, `murDuBatiment` et `murDesLogements` ; la profondeur ;
   `2 + hash2(x, y) % 2` pour un commerce ; `ETAGES_MAX`). Il écrit `hauts` sur chaque `residences[]` et
   `devantures[]`. ⚠️ **Avant de brancher quoi que ce soit** : une sonde sous Node compare l'ancien calcul JS au
   compte Python sur toutes les façades — toutes égales, ou le portage est faux.
2. **Le JS peint la donnée** : `logementElargi` et `etagesDuCommerce` lisent `hauts` au lieu de le recalculer.
3. **Les pièces** : pour chaque porte qui s'ouvre, `1 + hauts` niveaux, chaînés par des escaliers (le point
   `escalier`, `vers`, `descend` : `Jeu.changerEtage` sait déjà faire).
   - Logement : `slug`, `slug_haut`, `slug_haut2`… ; un étage du milieu a **deux** escaliers, MONTER et DESCENDRE.
   - Commerce : un escalier au fond de la boutique monte au logement du commerçant (`piece_de_logement(haut=True)`),
     et au-dessus s'il y en a trois.
   - L'escalier prend une tuile libre hors de portée de la porte ; s'il n'y en a pas, la place du meuble le plus
     éloigné de la porte — jamais un coin de lit.
   - ⚠️ **Les escaliers dans les deux sens, ou aucun étage** : personne ne reste pris en haut.
   - ⚠️ **Un logement peu profond qui ne peint aucun étage perd sa pièce du haut** : il devient fidèle à sa façade.
   - La pièce du haut que `poser_la_piece` fait aujourd'hui se fait à la fin, avec les autres. ⚠️ Le tirage
     d'`etages` (`des_devanture`) reste où il est : l'enlever ferait glisser la ville.
4. **Les juges** (chacun rougit quand on retire sa règle) :
   - pour **toutes** les portes de la ville, la suite de pièces compte `1 + hauts` niveaux ;
   - sous Node, le JS peint exactement `hauts`, pour toutes les façades ;
   - chaque étage est rejoignable à pied depuis la porte, en montant et en redescendant ;
   - les juges « ce module ne déplace rien » : le même sol, le même hasard ;
   - le poids du paquet (`test_definitions`).
   - Et **se regarde** : une capture dedans et dehors d'un triplex et d'un commerce à trois étages.

## Notes

### Le plan d'implémentation (30 sept. 2026)

> Pour un agent : exécuter tâche par tâche (superpowers:subagent-driven-development ou executing-plans), cases à
> cocher. **Dans un worktree** ; les commandes supposent `UV_PROJECT_ENVIRONMENT=/Users/martingagne/dev/bandini/.venv`.

**But** : autant de niveaux derrière une porte que sa façade en peint ; le compte vit en Python, le JS le peint.

**Architecture** : un module neuf, `app/etages.py`, appelé en DERNIER dans `carte.generer` (juste avant
`return ville`) : `compter(ville)` écrit `au_dessus` (un entier, les étages peints au-dessus du rez) sur chaque
`residences[]` et `devantures[]` ; `monter(ville)` ajuste les pièces des portes générées (`<famille>_<n>`,
`nord_…_<n>`). Le JS (`monde.js`) lit `au_dessus`. ⚠️ Le champ s'appelle `au_dessus`, **pas** `hauts` : `hauts`
est déjà le cache du JS (`d.hauts`, `e.hauts`) et le raccourci du banc (`r.hauts !== undefined`,
`test_facades_js.py`) — le même nom sauterait l'élargissement du mur.

**Contraintes globales** :
- Sans un dé, sans une tuile : `sol`, `voie`, `portes`, `decor` identiques avant et après le module.
- Le tirage d'`etages` (`des_devanture.entier`, `carte.py` ~l. 4217) reste où il est.
- Les escaliers dans les deux sens, ou aucun étage.
- Une pièce ajoutée passe `carte._verifier_piece` (on entre, chaque point est atteignable, rien ne vole la porte).
- Les pièces dessinées à la main (terminus, hôtel, hôpital, casino, tripot, blocs) ne sont pas touchées.

**Ce que la relecture doit guetter** (aucune tâche ne l'exerce seule) :
1. Un étage du milieu : ses DEUX escaliers et le point `fouiller` à moins de 2 tuiles l'un de l'autre —
   `pointSousLaMain` en prendrait un pour l'autre (juge de la tâche 3 : distance de Tchebychev ≥ 2).
2. `Histoire.pieceDessous(slug_haut)` qui rend l'étage du DESSUS (son escalier descend vers `slug_haut`) —
   corrigé à la tâche 3, jugé au banc.
3. Un escalier de commerce derrière le comptoir (les coulisses) : injoignable — `_verifier_piece` le refuse.
4. La bande nord (`nord_logement_1001`) : ses pièces renommées doivent monter aussi (juge sur `nord_`).
5. Le poids du paquet : `interieurs`, `residences`, `devantures` dans `MESURE_DE_LA_CARTE` (tâche 4).

#### Tâche 1 — le compte, en Python

**Fichiers** : créer `app/etages.py` ; modifier `app/carte.py` (fin de `generer`) ; créer `tests/test_etages.py`.
**Produit** : `etages.hash2(x, y) -> int`, `etages.compter(ville) -> None`, `ETAGES_MAX = 3`, `MUR_ETENDU = 8`.

- [ ] Juges d'abord (`tests/test_etages.py`) :

```python
"""Des étages dedans aussi (docs/jalons/des-etages-dedans-aussi.md)."""
from app import etages
from tests import villes


def test_hash2_est_celui_du_navigateur(banc):
    paires = [(0, 0), (3, 4), (120, 57), (411, 389), (-1, 7), (65535, 2)]
    attendu = banc("function (L) { return %s.map(function (p) { return L.hash2(p[0], p[1]); }); }" % paires)
    assert [etages.hash2(x, y) for x, y in paires] == attendu


def test_chaque_facade_sait_combien_d_etages_elle_peint():
    v = villes.generer()
    for q in v["residences"] + v["devantures"]:
        assert type(q["au_dessus"]) is int and 0 <= q["au_dessus"] <= etages.ETAGES_MAX, q
    for r in v["residences"]:
        assert r["au_dessus"] <= r["etages"] - 1, r
    montes = sum(1 for d in v["devantures"] if d["au_dessus"])
    assert montes >= 120, f"{montes} devantures portent des étages (129 sur 135 le 30 sept.)"
```

- [ ] `uv run pytest tests/test_etages.py -q` : rouge (`No module named app.etages`).
- [ ] Écrire `app/etages.py` — le portage exact de `monde.js` (`teintesDesToits().qui`, `murDuBatiment`,
  `murDesLogements`, `logementElargi`, `etagesDuCommerce`) et de `base.js` (`hash2`) :

```python
"""Des étages dedans aussi (docs/jalons/des-etages-dedans-aussi.md) : combien d'étages une façade peint au-dessus
de son rez — compté ICI, une fois, sur la ville finie et sans un dé — et autant de pièces derrière sa porte.

⚠️ Python compte, le JS peint : `Monde.logementElargi` et `Monde.etagesDuCommerce` lisent `au_dessus`. La règle ne
vit qu'ici ; la changer, c'est changer le dehors ET le dedans.
"""
from __future__ import annotations

#: Au plus tant d'étages peints au-dessus du rez (la boîte d'un morceau de ville le sait, `monde.js`).
ETAGES_MAX = 3
#: Jusqu'où le mur d'une façade s'étend, de chaque côté, sur le mur nu de son bâtiment.
MUR_ETENDU = 8
#: Les matières de toit qui font un bâtiment — pas la tôle des cabanes (`MATIERES_TEINTES`, monde.js).
MATIERES = "BEOP"
VOISINES = ((1, 0), (-1, 0), (0, 1), (0, -1))


def _u32(v: float | int) -> int:
    return int(v) & 0xFFFFFFFF


def _i32(v: float | int) -> int:
    n = _u32(v)
    return n - (1 << 32) if n >= 1 << 31 else n


def hash2(x: int, y: int) -> int:
    """`hash2` de base.js, au bit près. ⚠️ Sa deuxième multiplication est un FLOTTANT en JS (pas `Math.imul`) :
    le produit dépasse 2**53 et s'arrondit — un float Python s'arrondit pareil."""
    h = _i32(x * 374761393 + y * 668265263)
    h = float(_i32(h ^ (_u32(h) >> 13))) * 1274126177.0
    return _u32(_i32(h) ^ (_u32(h) >> 16))


def _toits(sol: list[str]) -> list[list[int]]:
    """Le bâtiment de chaque tuile de toit (-1 ailleurs) : les tuiles d'une même matière reliées entre elles,
    numérotées dans l'ordre de lecture — `teintesDesToits().qui`."""
    h, w = len(sol), len(sol[0])
    qui = [[-1] * w for _ in range(h)]
    n = 0
    for y in range(h):
        for x in range(w):
            g = sol[y][x]
            if qui[y][x] >= 0 or g not in MATIERES:
                continue
            qui[y][x] = n
            pile = [(x, y)]
            while pile:
                cx, cy = pile.pop()
                for dx, dy in VOISINES:
                    xx, yy = cx + dx, cy + dy
                    if 0 <= xx < w and 0 <= yy < h and qui[yy][xx] < 0 and sol[yy][xx] == g:
                        qui[yy][xx] = n
                        pile.append((xx, yy))
            n += 1
    return qui


def _mur(q: dict, qui: list[list[int]], sol: list[str], prises: set, aussi: frozenset | set = frozenset()
         ) -> tuple[int, int]:
    """Le mur d'une façade va au bout de son bâtiment (`murDuBatiment`) : (x, largeur)."""
    w, y = len(sol[0]), q["y"]

    def batiment(x: int) -> int:
        return qui[y - 1][x] if 0 <= x < w and y > 0 else -1

    lui = batiment(q["x"])

    def libre(x: int) -> bool:
        return (0 <= x < w and lui >= 0 and batiment(x) == lui and sol[y][x] in "FW"
                and (x, y) not in prises and (x, y) not in aussi)

    x0, x1 = q["x"], q["x"] + q["l"] - 1
    if q.get("declin") is None:
        while x0 > q["x"] - MUR_ETENDU and libre(x0 - 1):
            x0 -= 1
        while x1 < q["x"] + q["l"] - 1 + MUR_ETENDU and libre(x1 + 1):
            x1 += 1
    return x0, x1 - x0 + 1


def _profondeur(qui: list[list[int]], y: int, x0: int, large: int) -> int:
    """Combien de rangées de SON toit il y a au-dessus de la façade, à sa colonne la moins profonde."""
    profondeur = 99
    for x in range(x0, x0 + large):
        lui = qui[y - 1][x] if x >= 0 and y > 0 else -1
        p = 0
        while lui >= 0 and y - 1 - p >= 0 and qui[y - 1 - p][x] == lui:
            p += 1
        profondeur = min(profondeur, p)
    return profondeur


def compter(ville: dict) -> None:
    """`au_dessus` sur chaque logement et chaque devanture : les étages que sa façade peint au-dessus du rez.
    ⚠️ Une rangée de toit reste toujours visible : un bâtiment peu profond en montre moins qu'il n'en a."""
    sol, residences, devantures = ville["sol"], ville["residences"], ville["devantures"]
    qui = _toits(sol)
    prises = {(q["x"] + i, q["y"]) for q in devantures + residences for i in range(q["l"])}
    murs_des_logements: set[tuple[int, int]] = set()
    for r in residences:
        x0, large = _mur(r, qui, sol, prises)
        murs_des_logements |= {(x0 + i, r["y"]) for i in range(large)}
        r["au_dessus"] = max(0, min(r["etages"] - 1, ETAGES_MAX, _profondeur(qui, r["y"], x0, large) - 1))
    for d in devantures:
        # Un commerce : deux ou trois étages en tout, à l'empreinte de sa devanture ; la rangée au-dessus de la
        # vitrine est celle de l'enseigne. Son mur s'arrête devant celui d'un logement.
        x0, large = _mur({"x": d["x"], "y": d["y"], "l": d["l"]}, qui, sol, prises, murs_des_logements)
        etages = 2 + hash2(d["x"], d["y"]) % 2
        d["au_dessus"] = max(0, min(etages - 1, ETAGES_MAX, _profondeur(qui, d["y"], x0, large) - 2))
```

- [ ] Brancher à la fin de `generer` (`app/carte.py`, juste avant `return ville`) :

```python
    # ⚠️ DES ÉTAGES DEDANS AUSSI (docs/jalons/des-etages-dedans-aussi.md), APRÈS ABSOLUMENT TOUT : combien
    # d'étages chaque façade peint, compté sur la ville finie, sans un dé et sans une tuile.
    from . import etages as etages_mod
    etages_mod.compter(ville)
```

- [ ] `uv run pytest tests/test_etages.py -q` : vert.
- [ ] **La sonde du portage** (jetable, jamais commitée : `tests/test_sonde_etages_tmp.py`, effacée après) — le JS
  d'AVANT la tâche 2 recalcule, et doit tomber juste partout :

```python
def test_sonde(banc):
    r = banc("""function (L) {
        const M = L.Monde, c = M.carte, f = [];
        for (const r of c.def.residences) if (M.logementElargi(r).hauts !== r.au_dessus) f.push(['r', r.x, r.y]);
        for (const d of c.def.devantures) if (M.etagesDuCommerce(d) !== d.au_dessus) f.push(['d', d.x, d.y]);
        return { n: c.def.residences.length + c.def.devantures.length, fautes: f };
    }""")
    assert r["fautes"] == [], r
```

  `uv run pytest tests/test_sonde_etages_tmp.py -q` : **zéro faute**, sinon le portage est faux (le sol du
  navigateur, `etages` absent d'une île…) — trouver pourquoi avant d'aller plus loin. Puis `rm` la sonde.
- [ ] Commit : `feat: des étages dedans aussi, le compte — Python compte les étages que chaque façade peint`.

#### Tâche 2 — le JS peint la donnée

**Fichiers** : modifier `static/js/monde.js` (`logementElargi` ~l. 1906-1920, `etagesDuCommerce` ~l. 1928-1944) ;
créer `tests/test_etages_js.py`. **Consomme** : `au_dessus` (tâche 1).

- [ ] Juge d'abord (`tests/test_etages_js.py`) :

```python
"""Des étages dedans aussi : le navigateur peint les étages que Python a comptés, sans les recompter."""


def test_le_navigateur_peint_ce_que_python_a_compte(banc):
    """⚠️ On FAUSSE la donnée : si le JS recompte, il ne la suit pas."""
    r = banc("""function (L) {
        const M = L.Monde, c = M.carte, f = [];
        for (const r of c.def.residences) { r.au_dessus = (r.x + r.y) % 3; delete r.elargi; delete r.murEtendu; }
        for (const d of c.def.devantures) { d.au_dessus = (d.x + d.y) % 3; delete d.hauts; }
        for (const r of c.def.residences) if (M.logementElargi(r).hauts !== r.au_dessus) f.push(['r', r.x, r.y]);
        for (const d of c.def.devantures) if (M.etagesDuCommerce(d) !== d.au_dessus) f.push(['d', d.x, d.y]);
        return f;
    }""")
    assert r == [], r[:5]
```

- [ ] `uv run pytest tests/test_etages_js.py -q` : rouge (le JS recompte).
- [ ] `logementElargi` : remplacer la boucle de profondeur et le calcul de `e.hauts` par

```js
    // LES ETAGES POUR VRAI : combien de rangees de toit se peignent en etages — COMPTE PAR PYTHON (`app/etages.py`,
    // `au_dessus`), qui en fait autant de pieces derriere la porte. Ne pas le recompter ici : le dehors et le dedans
    // divergeraient.
    e.hauts = r.au_dessus || 0;
```

- [ ] `etagesDuCommerce` : garder le calcul du mur (`d.murX`, `d.murL` : le peintre en a besoin), retirer la boucle
  de profondeur et `hash2`, et finir par `d.hauts = d.au_dessus || 0; return d.hauts;` (mettre à jour son
  commentaire : « compté par Python, `app/etages.py` »). Garder `ETAGES_MAX` (les boîtes des morceaux, l. 336 et 342).
- [ ] `uv run pytest tests/test_etages_js.py tests/test_facades_js.py -q` : vert (les étages montent toujours, une
  rangée de toit reste — mais sur les nombres de Python, maintenant).
- [ ] Commit : `feat: des étages dedans aussi — le navigateur peint les étages comptés par Python`.

#### Tâche 3 — les pièces

**Fichiers** : modifier `app/etages.py` (+ `monter`), `app/carte.py` (`piece_de_logement` : un paramètre `nom`,
et l'appel de `monter` à la fin de `generer`), `static/js/histoire.js` (`pieceDessous`) ; juges dans
`tests/test_etages.py` et `tests/test_etages_js.py`. **Produit** : `etages.niveau(slug, k) -> str`,
`etages.suite(pieces, slug) -> list[str]`, `etages.ajouter_un_escalier(piece, vers, *, descend=False) -> bool`,
`etages.retirer_l_escalier(piece, vers) -> None`, `etages.monter(ville) -> None`.

- [ ] Juges d'abord (`tests/test_etages.py`, à la suite) :

```python
import math
import re

from app import carte

GENEREE = re.compile(r"^(?:nord_)?[a-z_]+?_\d+$")


def _portes_generees(v):
    for p in v["portes"]:
        s = p.get("interieur")
        if s and GENEREE.match(s) and s in v["interieurs"]:
            q = etages.facade_de(v, p)
            if q is not None:
                yield p, q


def test_autant_de_niveaux_dedans_que_la_facade_en_peint():
    v = villes.generer()
    fautes, montes, commerces = [], 0, 0
    for p, q in _portes_generees(v):
        n = len(etages.suite(v["interieurs"], p["interieur"]))
        if n != 1 + q["au_dessus"]:
            fautes.append((p["interieur"], n, 1 + q["au_dessus"]))
        montes += n >= 3
        commerces += n >= 2 and q in v["devantures"]
    assert fautes == [], fautes[:10]
    assert montes >= 5 and commerces >= 10, (montes, commerces)


def test_chaque_etage_monte_et_redescend():
    v = villes.generer()
    for p, _ in _portes_generees(v):
        suite = etages.suite(v["interieurs"], p["interieur"])
        for k, slug in enumerate(suite):
            piece = v["interieurs"][slug]
            carte._verifier_piece(piece)
            esc = {(q["vers"], bool(q.get("descend"))) for q in piece["points"] if q["type"] == "escalier"}
            attendu = ({(suite[k - 1], True)} if k else set()) | ({(suite[k + 1], False)} if k + 1 < len(suite) else set())
            assert esc == attendu, (slug, esc, attendu)
            pts = piece["points"]
            for i, a in enumerate(pts):
                for b in pts[i + 1:]:
                    assert max(abs(a["x"] - b["x"]), abs(a["y"] - b["y"])) >= 2, (slug, a, b)


def test_la_bande_nord_monte_aussi():
    v = villes.generer()
    assert any(len(etages.suite(v["interieurs"], p["interieur"])) >= 2
               for p, _ in _portes_generees(v) if p["interieur"].startswith("nord_"))


def test_en_haut_d_un_commerce_le_logement_du_commercant():
    v = villes.generer()
    for p, q in _portes_generees(v):
        if q in v["devantures"]:
            for slug in etages.suite(v["interieurs"], p["interieur"])[1:]:
                assert v["interieurs"][slug]["nom"] == "Le logement du commerçant", slug


def test_les_etages_ne_deplacent_rien(monkeypatch):
    """⚠️ Pas `villes` : on compare une ville bâtie SANS le module (le monkeypatch ne se voit pas du cache)."""
    avec = carte.generer()
    monkeypatch.setattr(etages, "compter", lambda ville: None)
    monkeypatch.setattr(etages, "monter", lambda ville: None)
    sans = carte.generer()
    for cle in avec:
        if cle not in ("interieurs", "residences", "devantures"):
            assert avec[cle] == sans[cle], cle
    for cle in ("residences", "devantures"):
        assert [{k: x for k, x in q.items() if k != "au_dessus"} for q in avec[cle]] == sans[cle], cle
    for slug, piece in sans["interieurs"].items():
        if not GENEREE.match(slug):
            assert avec["interieurs"][slug] == piece, slug
```

- [ ] `uv run pytest tests/test_etages.py -q` : rouge (`facade_de`, `suite` n'existent pas).
- [ ] `piece_de_logement` (`app/carte.py` ~l. 8331) : ajouter `nom: str | None = None` aux mots-clés, et
  `nom = nom or ("Un logement, en haut" if haut else "Un logement")` à la place de la ligne actuelle.
- [ ] Écrire dans `app/etages.py` :

```python
import math
import re

#: Une pièce POSÉE par la ville (`poser_la_piece` : `<famille>_<n>`, renommée `nord_…` dans la bande) — jamais
#: une pièce dessinée à la main (le terminus, l'hôtel, le tripot).
GENEREE = re.compile(r"^(?:nord_)?[a-z_]+?_(\d+)$")
#: Un meuble d'une tuile qui cède sa place à l'escalier quand le plancher n'en a plus (jamais un lit, un comptoir).
MEUBLES_QUI_CEDENT = "nke"


def niveau(slug: str, k: int) -> str:
    """Le nom du k-ième niveau : le rez, `_haut`, `_haut2`… (`_haut` était celui des plex, on le garde)."""
    return slug if k == 0 else f"{slug}_haut" if k == 1 else f"{slug}_haut{k}"


def suite(pieces: dict, slug: str) -> list[str]:
    """Le rez et ses étages, du bas vers le haut."""
    niveaux = [slug]
    while niveau(slug, len(niveaux)) in pieces:
        niveaux.append(niveau(slug, len(niveaux)))
    return niveaux


def facade_de(ville: dict, porte: dict) -> dict | None:
    for q in ville["residences"] + ville["devantures"]:
        if q["y"] == porte["y"] and q["x"] <= porte["x"] < q["x"] + q["l"]:
            return q
    return None


def ajouter_un_escalier(piece: dict, vers: str, *, descend: bool = False) -> bool:
    """Un escalier de plus dans une pièce finie : sur le plancher qu'on rejoint depuis la porte, le plus loin
    d'elle, jamais sur la rangée d'entrée ni à moins de deux tuiles d'un autre point (`pointSousLaMain` les
    confondrait). Faute de plancher, un petit meuble (`MEUBLES_QUI_CEDENT`) cède sa place ; faute de tout, le
    point `fouiller` qui gêne s'en va. `False` : aucune place."""
    from . import carte
    sol = [list(ligne) for ligne in piece["sol"]]
    ax, ay = piece["apparition"]["x"], piece["apparition"]["y"]
    atteignable = next(g for g in carte.composantes_marchables(piece) if (ax, ay) in g)
    gens = {(g["x"], g["y"]) for g in piece["gens"]}
    sous_un_point = {(p["x"], p["y"]) for p in piece["points"]}

    def places(points: list[dict]) -> list[tuple[int, int]]:
        bonnes = []
        for y in range(1, piece["hauteur"] - 2):
            for x in range(1, piece["largeur"] - 1):
                g = sol[y][x]
                sur_le_plancher = g == piece["plancher"] and (x, y) in atteignable
                cede = g in MEUBLES_QUI_CEDENT and any((x + dx, y + dy) in atteignable for dx, dy in VOISINES)
                if not (sur_le_plancher or cede) or (x, y) in gens or (x, y) in sous_un_point:
                    continue
                if math.hypot(x - ax, y - ay) < carte.RAYON_POINT:
                    continue
                if all(max(abs(x - p["x"]), abs(y - p["y"])) >= 2 for p in points):
                    bonnes.append((x, y))
        # Le plancher d'abord, puis le plus loin de la porte ; l'ordre de lecture départage.
        return sorted(bonnes, key=lambda t: (sol[t[1]][t[0]] != piece["plancher"],
                                             -math.hypot(t[0] - ax, t[1] - ay), t[1], t[0]))

    points = piece["points"]
    choix = places(points)
    if not choix:
        points = [p for p in points if p["type"] != "fouiller"]
        choix = places(points)
    if not choix:
        return False
    x, y = choix[0]
    sol[y][x] = "/"
    piece["sol"] = ["".join(ligne) for ligne in sol]
    piece["points"] = [p for p in points] + [{"type": "escalier", "x": x, "y": y, "vers": vers,
                                              **({"descend": True} if descend else {})}]
    carte._verifier_piece(piece)
    return True


def retirer_l_escalier(piece: dict, vers: str) -> None:
    """L'escalier qui menait à un étage que la façade ne peint pas : sa marche redevient du plancher."""
    for p in [p for p in piece["points"] if p["type"] == "escalier" and p["vers"] == vers]:
        ligne = piece["sol"][p["y"]]
        piece["sol"][p["y"]] = ligne[:p["x"]] + piece["plancher"] + ligne[p["x"] + 1:]
        piece["points"].remove(p)


def monter(ville: dict) -> None:
    """Derrière chaque porte posée par la ville, `1 + au_dessus` niveaux : on retire ce que la façade ne peint pas,
    on empile ce qui manque. ⚠️ Les deux escaliers ou aucun : un étage qu'on n'a pas pu relier ne se pose pas."""
    from . import carte
    pieces = ville["interieurs"]
    faites: set[str] = set()
    for porte in ville["portes"]:
        slug = porte.get("interieur")
        m = GENEREE.match(slug or "")
        if not m or slug not in pieces or slug in faites:
            continue
        faites.add(slug)
        facade = facade_de(ville, porte)
        if facade is None:
            continue
        voulu = 1 + facade["au_dessus"]
        niveaux = suite(pieces, slug)
        while len(niveaux) > voulu:
            haut = niveaux.pop()
            del pieces[haut]
            retirer_l_escalier(pieces[niveaux[-1]], haut)
        rez = pieces[slug]
        commerce = facade in ville["devantures"]
        while len(niveaux) < voulu:
            k, dessous = len(niveaux), niveaux[-1]
            neuf = niveau(slug, k)
            haut = carte.piece_de_logement(
                neuf, rez["largeur"] - 2, rez["hauteur"] - 2, rez["sortie"]["x"], etage=dessous, haut=True,
                variante=int(m.group(1)) + k, nom="Le logement du commerçant" if commerce else None)
            if not any(p["type"] == "escalier" for p in haut["points"]):
                break
            if not ajouter_un_escalier(pieces[dessous], neuf):
                break
            pieces[neuf] = haut
            niveaux.append(neuf)
```

  (`VOISINES` est déjà défini en tête du module, tâche 1.)
- [ ] Appeler `etages_mod.monter(ville)` juste après `etages_mod.compter(ville)` dans `generer`.
- [ ] `uv run pytest tests/test_etages.py -q` : vert. Si `test_autant_de_niveaux…` garde des fautes, les lire
  (pièce trop petite ? escalier sans place ?) et corriger la RÈGLE, pas le juge.
- [ ] `static/js/histoire.js`, `pieceDessous` : un étage du milieu a deux pièces dont l'escalier y mène (celle
  d'en dessous qui MONTE, celle d'au-dessus qui DESCEND) — préférer celle qui monte :

```js
  function pieceDessous(slug) {
    const ville = Monde.carte.ville || Monde.carte;
    const pieces = (ville.def && ville.def.interieurs) || {};
    // ⚠️ Un etage du milieu (des etages dedans aussi) : l'escalier de l'etage du DESSUS y descend aussi. La piece
    // du dessous est celle dont l'escalier MONTE ; a defaut (le tripot : on y descend du casino), n'importe laquelle.
    let aDefaut = null;
    for (const s in pieces) {
      for (const q of (pieces[s].points || [])) {
        if (q.type !== 'escalier' || q.vers !== slug) continue;
        if (!q.descend) return s;
        aDefaut = aDefaut || s;
      }
    }
    return aDefaut;
  }
```

- [ ] Juge au banc (`tests/test_etages_js.py`, à la suite) — monter tout en haut et redescendre au bouton de
  l'escalier, pas en appelant `changerEtage` à l'aveugle :

```python
def test_on_monte_au_dernier_etage_et_on_redescend(banc):
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const I = L.Monde.carte.def.interieurs;
        const haut = function (s) { return s + '_haut2'; };
        const porte = L.Monde.carte.portes.find(function (p) { return p.interieur && I[haut(p.interieur)]; });
        if (!porte) return { rien: true };
        o.entrer(porte);
        const vus = [L.B.interieur.slug];
        for (const sens of ['monte', 'monte', 'descend', 'descend']) {
            const p = L.B.interieur.points.find(function (q) { return q.type === 'escalier' && !!q.descend === (sens === 'descend'); });
            L.Jeu.changerEtage(p.vers); L.Jeu.finirTransition();
            vus.push(L.B.interieur.slug);
        }
        return { vus: vus, dessous: L.Histoire.pieceDessous(porte.interieur + '_haut'), rez: porte.interieur };
    }""")
    assert not r.get("rien"), "aucune porte à trois niveaux"
    rez = r["rez"]
    assert r["vus"] == [rez, rez + "_haut", rez + "_haut2", rez + "_haut", rez], r
    assert r["dessous"] == rez, r
```

  Le faire rougir : remettre l'ancien `pieceDessous` → `dessous` vaut `…_haut2`.
- [ ] Mutations (chacune doit rougir, puis on la retire ; vider `__pycache__` après une mutation Python) :
  `voulu = 1` dans `monter` ; `ajouter_un_escalier` sans le filtre de distance aux points ; `nom=None` pour les
  commerces.
- [ ] Commit : `feat: des étages dedans aussi — autant de niveaux derrière la porte que la façade en peint`.

#### Tâche 4 — le poids, les juges voisins, le regard, la doc

- [ ] Les juges voisins, ciblés : `uv run pytest tests/test_etages.py tests/test_etages_js.py tests/test_facades_js.py
  tests/test_carte.py tests/test_interieurs.py tests/test_interieurs_js.py tests/test_devantures.py
  tests/test_definitions.py tests/test_infiltration_js.py tests/test_donneurs_visibles_js.py -q`. Un rouge :
  le rejouer sur la base (mémoire « un rouge est-il de moi ? ») avant de le prendre pour soi.
- [ ] Le poids : si `test_chaque_cle_de_la_carte_tient_son_budget` rougit, relever `interieurs`, `residences`,
  `devantures` dans `MESURE_DE_LA_CARTE` (`tests/test_definitions.py` l. 90) au poids mesuré, en le disant dans
  le commit.
- [ ] `uv run ruff check .`
- [ ] **Regarder** (mémoire « capturer une pièce du jeu ») : une capture dehors et dedans (chaque niveau) d'un
  triplex et d'un commerce à trois niveaux ; les ouvrir dans Aperçu pour Martin.
- [ ] La doc : les notes de cette fiche (ce qui est livré, les chiffres mesurés) ; `docs/architecture.md` (une ligne
  pour `app/etages.py`) ; la ligne du plan passe dans `docs/jalons/README.md`.
- [ ] Atterrir (cherry-pick + `merge --ff-only` sur `dev`), puis la suite complète.
