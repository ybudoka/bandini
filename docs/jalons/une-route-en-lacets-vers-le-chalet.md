# Une route en lacets vers le chalet

← [les jalons livrés](README.md) · [le plan](../plan.md)

## Fiche

Martin (30 sept. 2026) : « est-ce techniquement possible d'avoir des courbes dans les rues ? » La ville
est une grille de tuiles de 16 px, et le champ `voie` ne connaît que `> < ^ v` : tout le trafic, la
police, les autobus, le GPS et `voies_bloquees` lisent ces flèches. Une ville courbe partout serait un
autre jeu. Martin a tranché pour **quelques routes courbes posées à part**, et la première : **la montée
vers le chalet**, dans le bloc du rang (`app/blocs/rang.py`).

Le rang est le bon endroit pour commencer : c'est un plan dessiné à part (la ville ne change pas d'un
octet), et **un bloc n'a pas de trafic** (la vague 3 des blocs), donc aucune IA n'a besoin de suivre la
courbe. Il reste un tracé, un sol, un bois et un dessin.

**Le tracé** (tranché par Martin : « Lacets dans le bois », chalet au bout du chemin). Le vieux chemin de
gravier en L (tout droit de l'entrée est jusqu'à x=17, puis au nord le long du lac) devient une route
sinueuse de 3 tuiles de large. On entre à l'est (rangées 23 à 26, le `retour` ne bouge pas), on passe
devant l'allée de la cabane à sucre (qui reste tout près de l'entrée : c'est un lieu public), on plonge au
sud-ouest dans le bois en deux grands virages, on remonte le long du lac (l'embranchement du quai reste),
et on arrive **au chalet par l'ouest, au bout du chemin**. Le croquis d'accord (points de passage, en
tuiles du bloc, le coin nord-ouest de la tuile (x, y) étant le point (x, y)) :
`(80,25) (66,25.5) (52,27) (42,31) (40,37) (30,42) (18,41) (9,34) (12,26) (20,21.5) (30,22) (38,22) (43.5,22.5)`.

**Le bois et la surface** (tranchés par Martin : « Bois dense + route roulante »). Aujourd'hui, au rang,
l'herbe est de la `terre` comme le gravier : une auto ralentit autant partout, et entre l'entrée et le
chalet il n'y a qu'un champ. Sans rien de plus, on filerait tout droit et les lacets ne seraient qu'un
dessin. Donc :

- **Un bois dense** : le long de la route, dans la zone du bois (le sud-ouest du rang), une **haie
  d'arbres de deux tuiles d'épaisseur** de chaque côté, au-delà d'une tuile de lisière dégagée ; et une
  **haie tracée à la main** entre le côté de la cabane et le côté du chalet, du bord nord jusqu'au bois.
  On suit la route, en char comme à pied.
- **Une route roulante** : un glyphe neuf, `§` (« chemin de gravier roulé » ; pas `¤`, que le plan des districts donne déjà au casino), qui n'est **pas** de la
  `terre` — une auto y roule à pleine vitesse, l'herbe la ralentit toujours. Le `g` des allées de parc de
  la ville ne change pas.

**L'approche** (tranchée par Martin : « tracé lisse ») :

- **Python, sans un dé.** `BLOC["chemins"] = [{…}]` dans `rang.py` : les points, la largeur, le sol
  (`§`), et les zones du bois. `blocs/__init__.py` échantillonne la spline (Catmull-Rom, un point tous
  les 4 px, comme la voie de la montagne russe) et pose le chemin sur le plan (`plan_du_bloc`) : la
  chaussée sur chaque tuile dont le centre tombe dans la largeur, la lisière dégagée de ses arbres et
  buissons, la haie dans les zones du bois. `sol_du_bloc` et `decor_du_bloc` lisent ce plan-là (ils
  s'accordent). Le paquet du bloc exporte les points échantillonnés, en pixels. Réutilisable par un
  autre bloc, et plus tard en ville.
- **JS.** Les tuiles `§` se peignent **en herbe** (le cache du sol n'a pas d'escalier à montrer) ;
  `Blocs.dessinerChemins`, appelé juste après `Monde.dessinerSol` (donc **sous** la neige, le verglas et
  les traces de pneus), peint un ruban de gravier au bord lisse — le grain du `g`, en motif ancré au
  monde —, une lisière d'herbe foulée et deux ornières. La collision et la vitesse restent sur les
  tuiles ; l'écart visuel reste sous 8 px.

**Hors périmètre** : le trafic dans le rang (la vague 3 des blocs), une vraie pente, des courbes en ville.

**Ensuite : des routes en diagonale** (Martin, 30 sept. 2026 : « je veux aussi des routes en diagonales »,
puis « dans les blocs, après les lacets »). La même mécanique : un chemin de deux points est une route
droite à n'importe quel angle. Une vague à part, qui se tranche avec Martin une fois les lacets livrés et
essayés (quel bloc, quel raccourci). En ville, une avenue en biais demanderait un trafic qui suit un tracé :
un autre jalon, pas demandé.

- ⚠️ **La raquette en babiche** (`collectionner.py`, la bebelle du rang) se pose sur la tuile la plus loin
  à pied de l'arrivée, les arbres comptant comme des murs. Le bois va la déplacer : c'est une règle sans
  dé, donc permis ; elle doit rester atteignable et « au fond du rang ».
- ⚠️ **Le sentier de la calèche** (`CABANE["caleche"]["chemin"]`, x 48 à 75, rangées 29 à 44) et son
  raccord au chemin (x 62-63, rangées 27-28) ne bougent pas ; la route passe à l'ouest de sa boucle.
- ⚠️ **La planque** : la place du char (46,18) et le 4 roues (52,19) ne bougent pas, tous deux du côté du
  chalet de la haie ; l'allée courte devant la porte du chalet (x 43) se raccorde au bout de la route.
- ⚠️ **Le glyphe `§` voyage dans la légende** de `/api/carte` : quelques octets de plus au paquet de la
  carte (plafond 55 000 gzip) — `test_definitions` dans les juges ciblés.

## Plan

> **Pour l'agent qui exécute :** sous-compétence requise — `superpowers:subagent-driven-development`
> (recommandé) ou `superpowers:executing-plans`, tâche par tâche. Les étapes sont des cases (`- [ ]`).

**But :** une route de gravier courbe, bordée d'un bois, qui mène de l'entrée du rang au chalet en lacets.

**Architecture :** un chemin est une donnée du bloc (points de passage, largeur, sol, zones du bois).
Python l'échantillonne et le cuit dans le plan du bloc (sol, lisière, haie), sans un dé ; le paquet du
bloc porte les points échantillonnés ; `blocs.js` peint le ruban lisse par-dessus des tuiles peintes en
herbe. Aucun changement à la ville.

**Pile :** Python 3.14 (Flask, pytest, `uv`), JS sans bundler (`static/js/*.js`, globaux), banc Node
(`tests/banc.js`, fixture `banc`), Playwright pour la capture.

**Fiche :** ce fichier, section « Fiche » ci-dessus.

### Contraintes globales

- Travailler dans le worktree `…/scratchpad/wt-lacets`, branche `claude/route-en-lacets` ; jamais
  `git add -A`, jamais `git stash`.
- **Aucun dé** dans le chemin : tout se calcule depuis `BLOC["chemins"]`, le même résultat à chaque import.
- **La ville ne change pas d'un octet** : `/api/carte` ne gagne que l'entrée `§` de la légende.
- Le `g` de la ville garde sa légende (`terre: True`) et son peintre.
- Les coordonnées des points de passage sont en **tuiles**, continues : le centre de la tuile (x, y) est
  (x + 0,5, y + 0,5). Les points exportés sont en **pixels du monde**.
- Commentaires et noms en français, dans le ton du fichier touché ; les ⚠️ disent le piège.
- Avant chaque commit : `uv run ruff check .` ; le crochet des tables lit l'arbre principal — `git add`
  puis `git commit` en deux commandes.

### Ce que la revue doit surveiller

1. **L'hiver** (une partie commence en janvier) : le ruban doit être **sous** le voile de neige, sinon une
   route brune traverse un rang blanc. Juge : l'ordre des peintres (tâche 4).
2. **La planque rouverte au chalet** : le char se réveille sur (46,18) ; il doit pouvoir repartir vers la
   ville sans traverser un arbre. Juge : le char suit la route dans les deux sens (tâche 5).
3. **La police qui reprend au bord** : ses agents naissent au passage est ; les tuiles du retour doivent
   rester libres d'arbres. Juge : `blocs.erreurs` (le retour se marche) plus le juge du bois (tâche 3).
4. **Le 4 roues du chalet** (52,19) : il doit rester du côté du chalet de la haie, et rejoindre la route.
   Juge : tâche 3.
5. **Le char qui arrive de la ville** à (77,24), tourné vers l'ouest : il doit trouver la chaussée devant
   lui, pas un tronc. Juge : `test_au_volant_on_passe_avec_son_char_et_on_revient_avec_lui` (existant,
   rejoué) et le juge du bois (tâche 3).

---

### Tâche 0 : partir de `dev` à jour, et savoir ce qui est déjà rouge

**Fichiers :** aucun.

- [ ] **Étape 1 : rebaser la branche sur `dev`**

```bash
cd …/scratchpad/wt-lacets
git fetch -q --all
git rebase dev
```
Attendu : la branche contient le commit « une route en lacets vers le chalet — en cours » (déjà sur
`dev`, le rebase le saute) et rien d'autre.

- [ ] **Étape 2 : les juges de départ**

```bash
uv run pytest tests/test_rang.py tests/test_blocs.py tests/test_blocs_js.py tests/test_bebelles.py tests/test_collections.py tests/test_decoration.py tests/test_quatre_roues.py tests/test_definitions.py -q -p no:randomly 2>&1 | tail -5
```
Attendu : vert. Un rouge ici n'est pas de nous : le noter (nom du juge) et le rejouer sur `dev` avant de
continuer.

---

### Tâche 1 : le glyphe `§`, un gravier qui ne ralentit pas

**Fichiers :**
- Modifier : `app/carte.py` (la `LEGENDE`, à côté de `"g"`, ligne ~268)
- Modifier : `static/js/sprites.js` (les `TUILES`, à côté de `'g'`, ligne ~3797)
- Créer : `tests/test_chemins_des_blocs.py`
- Créer : `tests/test_chemins_des_blocs_js.py`

**Interfaces :**
- Produit : `carte.LEGENDE["§"] == {"nom": "chemin de gravier roulé", "chemin": True}` (ni `terre`, ni
  `route`, ni `solide`) ; `TUILES['§']` peint de l'herbe (le même peintre que `','`).

- [ ] **Étape 1 : le juge Python**

`tests/test_chemins_des_blocs.py` :

```python
"""Les chemins des blocs (docs/jalons/une-route-en-lacets-vers-le-chalet.md) : une courbe douce posée
sur la grille d'un bloc — son glyphe, son tracé, sa lisière, son bois."""

from app import carte


def test_le_chemin_roule_n_est_ni_terre_ni_rue_ni_mur():
    """⚠️ Pas de la `terre` : une auto y roule à pleine vitesse (l'herbe du rang la ralentit). Pas une
    `route` : aucun trafic ne s'y engage, et `sortie_sans_rue` ne le compte pas. Et on marche dessus."""
    g = carte.LEGENDE["§"]
    assert not g.get("terre") and not g.get("route") and not g.get("solide"), g
    assert carte.LEGENDE["g"].get("terre"), "le g des allées de la ville a changé"
```

- [ ] **Étape 2 : le voir rougir**

Run : `uv run pytest tests/test_chemins_des_blocs.py -q`
Attendu : FAIL, `KeyError: '§'`.

- [ ] **Étape 3 : la légende**

Dans `app/carte.py`, juste après l'entrée `"g"` :

```python
    # ⚠️ LE CHEMIN DE GRAVIER ROULÉ des blocs (la route en lacets du rang,
    # docs/jalons/une-route-en-lacets-vers-le-chalet.md) : posé par un chemin de bloc
    # (`blocs.plan_du_bloc`), jamais écrit dans un plan. Ni `terre` — une auto y roule à pleine
    # vitesse, l'herbe d'à côté la ralentit — ni `route` : aucun trafic ne s'y engage. Il se peint
    # en HERBE : le ruban lisse de `Blocs.dessinerChemins` est la route qu'on voit.
    "§": {"nom": "chemin de gravier roulé", "chemin": True},
```

- [ ] **Étape 4 : le voir passer**

Run : `uv run pytest tests/test_chemins_des_blocs.py -q` — Attendu : PASS.

- [ ] **Étape 5 : le juge JS de la vitesse**

`tests/test_chemins_des_blocs_js.py` :

```python
"""Les chemins des blocs, JOUÉS (docs/jalons/une-route-en-lacets-vers-le-chalet.md)."""


def test_une_auto_roule_plus_vite_sur_le_chemin_que_sur_l_herbe(banc):
    """Le même char, la même pédale, deux sols : l'herbe (`terre`) le ralentit, le chemin roulé non."""
    r = banc("""async function (L, o) {
        L.Jeu.commencer(); L.B.partie.jour = 21;
        const TT = 16, c = L.Monde.carte, j = L.B.joueur;
        // Une rangée d'herbe, puis la même rangée repeinte en chemin : on y lance l'auto.
        function essai(glyphe) {
          const y = 5, ligne = c.sol[y];
          c.sol[y] = ligne.slice(0, 2) + glyphe.repeat(40) + ligne.slice(42);
          const v = L.Vehicules.creer('auto', 4 * TT, y * TT + 8, 0, { etat: 'stationne' });
          j.x = v.x; j.y = v.y + 12; L.Entites.indexer(); L.Vehicules.monter(j, v); L.Entites.indexer();
          o.touche('KeyW'); for (let i = 0; i < 60; i++) o.frame(1); o.relacher('KeyW');
          const dx = v.x - 4 * TT;
          L.Vehicules.descendre(j); c.sol[y] = ligne;
          return dx;
        }
        return { herbe: essai(','), chemin: essai('§') };
    }""")
    assert r["chemin"] > r["herbe"] * 1.1, r
```

⚠️ Vérifier d'abord, au banc, que la rangée 5 de la ville au départ est libre de x = 2 à 42 (sinon choisir
une autre rangée libre : `L.Monde.carte.sol[y].slice(2, 42)` sans mur ni décor) ; que
`L.Vehicules.descendre` existe (sinon `grep -n "function descendre" static/js/vehicules.js`) ; et que
`Monde.estTerre` relit bien `c.sol` à chaque appel (pas de cache par tuile). Si le sol est mis en cache,
poser l'essai dans une pièce vide plutôt que de patcher la ville.

- [ ] **Étape 6 : le voir rougir** — `uv run pytest tests/test_chemins_des_blocs_js.py -q` — Attendu :
FAIL (le glyphe n'a pas de peintre, ou la vitesse est la même) ; lire le message.

- [ ] **Étape 7 : le peintre**

Dans `static/js/sprites.js`, juste après le peintre `'g'` :

```js
    // ⚠️ LE CHEMIN DE GRAVIER ROULÉ des blocs (la route en lacets du rang) : peint en HERBE,
    // exprès. Sa tuile porte la vitesse et la collision ; la route qu'on voit est le ruban
    // lisse de `Blocs.dessinerChemins`, par-dessus. Un gravier carré ici montrerait l'escalier
    // de la grille au bord de la courbe.
    '§': function (ctx, v, T) { TUILES[','](ctx, v, T); },
```

⚠️ `TUILES` est l'objet rendu par l'IIFE : si le peintre `','` n'est pas encore défini à cet endroit, ou
si `TUILES` n'est pas accessible de l'intérieur, appeler la fonction locale qu'utilise `','` (lire son
entrée : `grep -n "^    ',': " static/js/sprites.js`). Chercher aussi les tables indexées par glyphe
(`grep -n "'g':" static/js/*.js`) : la mini-carte ou un autre peintre qui a une entrée `'g'` en veut une
pour `'§'` (le vert de l'herbe).

- [ ] **Étape 8 : les voir passer, plus les juges de la légende**

```bash
uv run pytest tests/test_chemins_des_blocs.py tests/test_chemins_des_blocs_js.py tests/test_carte.py tests/test_definitions.py -q 2>&1 | tail -5
```
Attendu : PASS. `test_definitions` dit le poids de la carte : il doit rester sous son plafond.

- [ ] **Étape 9 : commit**

```bash
git add app/carte.py static/js/sprites.js tests/test_chemins_des_blocs.py tests/test_chemins_des_blocs_js.py
git commit -m "feat: un chemin de gravier roulé pour les blocs — un glyphe qui n'est pas de la terre, peint en herbe sous son ruban (la route en lacets, tâche 1)"
```

---

### Tâche 2 : un chemin de bloc — tracé, chaussée, lisière, bois

**Fichiers :**
- Modifier : `app/blocs/__init__.py` (`sol_du_bloc`, `decor_du_bloc`, `carte_du_bloc`, `erreurs`,
  `a_pied_depuis_l_arrivee` — toutes lisent `plan_du_bloc`)
- Test : `tests/test_chemins_des_blocs.py`

**Interfaces :**
- Consomme : `carte.LEGENDE["§"]` (tâche 1).
- Produit :
  - `blocs.echantillonner(points: list[tuple[float, float]], pas_px: float = PAS_DU_CHEMIN_PX) -> list[tuple[float, float]]`
    — points de passage en tuiles → points en pixels, un tous les ~4 px, par Catmull-Rom.
  - `blocs.distances_au_chemin(chemin: dict, largeur: int, hauteur: int) -> dict[tuple[int, int], float]`
    — pour chaque tuile à portée, sa distance (px) au tracé.
  - `blocs.plan_du_bloc(bloc: dict) -> list[str]` — le plan, chemins posés.
  - `carte_du_bloc(bloc)["bloc"]["chemins"] == [{"largeur_px": int, "points": [[x, y], …]}]`.
  - Clés d'un chemin dans `BLOC["chemins"]` : `points` (tuiles), `largeur` (tuiles), `sol` (glyphe),
    `bois` (liste de rectangles `[x, y, l, h]` en tuiles où la haie pousse), `haie` (épaisseur en
    tuiles, 2 par défaut), `arbre` (le glyphe de décor de la haie, `"A"`).
  - Constantes : `PAS_DU_CHEMIN_PX = 4`, `LISIERE_TUILES = 1`, `RAYON_MIN_PX = 48`.

- [ ] **Étape 1 : les juges, sur un petit bloc fabriqué**

Ajouter à `tests/test_chemins_des_blocs.py` :

```python
import math

from app import blocs

#: Un bloc de 30 x 20 tuiles, tout en herbe, des arbres (`A`) et un buisson (`b`) sur le passage d'un
#: chemin qui traverse d'ouest en est en faisant une bosse vers le sud.
PETIT = {
    "slug": "essai", "nom": "Essai",
    "plan": tuple(
        "".join("A" if (x, y) in {(10, 10), (11, 11), (20, 8)} else "b" if (x, y) == (15, 12) else ","
                for x in range(30))
        for y in range(20)),
    "decors": {"A": (",", "arbre"), "b": (",", "buisson")},
    "chemins": [{"points": [(0, 8), (10, 10), (20, 10), (30, 8)], "largeur": 3, "sol": "§",
                 "bois": [[0, 0, 30, 20]], "haie": 2, "arbre": "A"}],
    "passage": {"bord": "ouest", "de": 7, "l": 3}, "retour": {"bord": "ouest", "de": 7, "l": 3},
    "arrivee": {"x": 1, "y": 8},
}


def test_l_echantillon_suit_les_points_a_pas_regulier():
    pts = blocs.echantillonner([(0, 8), (10, 10), (20, 10), (30, 8)])
    assert pts[0] == (0.0, 128.0) and pts[-1] == (480.0, 128.0)
    pas = [math.dist(a, b) for a, b in zip(pts, pts[1:])]
    assert max(pas) <= 4.5 and min(pas) > 0, (min(pas), max(pas))
    # La courbe passe PAR chaque point de passage.
    for x, y in [(10, 10), (20, 10)]:
        assert min(math.dist(p, (x * 16, y * 16)) for p in pts) < 1


def test_la_chaussee_la_lisiere_et_la_haie():
    plan = blocs.plan_du_bloc(PETIT)
    d = blocs.distances_au_chemin(PETIT["chemins"][0], 30, 20)
    demi = 1.5 * 16
    for (x, y), dist in d.items():
        if dist <= demi:
            assert plan[y][x] == "§", ((x, y), dist, plan[y][x])
        elif dist <= demi + 16:
            assert plan[y][x] == ",", ("la lisière n'est pas dégagée", (x, y), plan[y][x])
        elif dist <= demi + 16 + 2 * 16:
            assert plan[y][x] == "A", ("un trou dans la haie", (x, y), plan[y][x])
    # Les arbres et le buisson SUR le chemin sont partis ; celui de loin (20, 8) reste un arbre.
    assert plan[10][10] == "§" and plan[12][15] in ",§"
    assert blocs.sol_du_bloc(PETIT)[10][10] == "§"
    assert (10, 10) not in {(e["x"], e["y"]) for e in blocs.decor_du_bloc(PETIT)}


def test_hors_du_bois_pas_de_haie():
    sans_bois = {**PETIT, "chemins": [{**PETIT["chemins"][0], "bois": [[0, 0, 5, 20]]}]}
    plan = blocs.plan_du_bloc(sans_bois)
    assert "A" not in "".join(ligne[6:] for ligne in plan[13:]), "une haie hors de la zone du bois"


def test_le_paquet_du_bloc_porte_le_trace_en_pixels():
    c = blocs.carte_du_bloc(PETIT)
    (ch,) = c["bloc"]["chemins"]
    assert ch["largeur_px"] == 48
    assert ch["points"][0] == [0.0, 128.0] and len(ch["points"]) > 100
    assert c["sol"][10][10] == "§"


def test_un_bloc_sans_chemin_n_a_pas_change():
    for b in blocs.BLOCS:
        if not b.get("chemins"):
            assert blocs.plan_du_bloc(b) == list(b["plan"]), b["slug"]


def test_erreurs_denonce_un_virage_trop_serre_et_un_decor_sur_la_route():
    serre = {**PETIT, "chemins": [{**PETIT["chemins"][0], "points": [(0, 8), (10, 8), (10.5, 12), (0, 12)]}]}
    assert any("virage" in f for f in blocs.erreurs(serre)), blocs.erreurs(serre)
    # Un décor qu'on ne dégage pas (une corde de bois) posé sur la chaussée.
    corde = {**PETIT, "decors": {**PETIT["decors"], "L": (",", "corde_bois")},
             "plan": tuple(ligne[:12] + ("L" if y == 10 else ligne[12]) + ligne[13:]
                           for y, ligne in enumerate(PETIT["plan"]))}
    assert any("sur le chemin" in f for f in blocs.erreurs(corde)), blocs.erreurs(corde)
    assert not [f for f in blocs.erreurs(PETIT) if "chemin" in f or "virage" in f], blocs.erreurs(PETIT)
```

- [ ] **Étape 2 : les voir rougir** — `uv run pytest tests/test_chemins_des_blocs.py -q` — Attendu :
FAIL, `AttributeError: module 'app.blocs' has no attribute 'echantillonner'`.

- [ ] **Étape 3 : le code**

Dans `app/blocs/__init__.py`, ajouter `import math` aux imports du haut, puis, juste avant
`sol_du_bloc` :

```python
#: ⚠️ LES CHEMINS D'UN BLOC (docs/jalons/une-route-en-lacets-vers-le-chalet.md) : une courbe douce
#: posée sur la grille. Ses points de passage sont en TUILES continues (le centre de la tuile (x, y)
#: est (x + 0,5, y + 0,5)) ; la courbe passe par chacun (Catmull-Rom), échantillonnée tous les
#: PAS_DU_CHEMIN_PX pixels — comme la voie de la montagne russe. Tout se calcule sans un dé : le même
#: plan à chaque import.
PAS_DU_CHEMIN_PX = 4
#: La lisière : tant de tuiles, au-delà de la chaussée, d'où l'on retire arbres et buissons.
LISIERE_TUILES = 1
#: Un virage plus serré ne se prend pas en auto (trois tuiles de rayon).
RAYON_MIN_PX = 48
#: Les décors qu'un chemin a le droit de dégager ; tout autre décor sur sa chaussée ou sa lisière est une faute.
DEGAGEABLES = ("arbre", "buisson")


def echantillonner(points, pas_px: float = PAS_DU_CHEMIN_PX) -> list[tuple[float, float]]:
    """Les points de passage (en tuiles) → la courbe, en PIXELS du monde, un point tous les ~`pas_px`."""
    t_px = carte.TUILE_PX
    p = [(x * t_px, y * t_px) for x, y in points]
    p = [p[0]] + p + [p[-1]]
    fins: list[tuple[float, float]] = []
    for i in range(1, len(p) - 2):
        p0, p1, p2, p3 = p[i - 1], p[i], p[i + 1], p[i + 2]
        n = max(1, math.ceil(math.dist(p1, p2) / pas_px))
        for k in range(n):
            t = k / n
            fins.append(tuple(
                0.5 * (2 * p1[j] + (p2[j] - p0[j]) * t + (2 * p0[j] - 5 * p1[j] + 4 * p2[j] - p3[j]) * t * t
                       + (3 * p1[j] - p0[j] - 3 * p2[j] + p3[j]) * t ** 3) for j in (0, 1)))
    fins.append(p[-2])
    return fins


def _portee_px(chemin: dict) -> float:
    """Jusqu'où un chemin touche le plan : la chaussée, la lisière, puis la haie."""
    t_px = carte.TUILE_PX
    return chemin["largeur"] * t_px / 2 + (LISIERE_TUILES + chemin.get("haie", 2)) * t_px


def distances_au_chemin(chemin: dict, largeur: int, hauteur: int) -> dict[tuple[int, int], float]:
    """Chaque tuile à portée du chemin, et la distance (px) de son centre au tracé."""
    t_px, portee = carte.TUILE_PX, _portee_px(chemin)
    d: dict[tuple[int, int], float] = {}
    for px, py in echantillonner(chemin["points"]):
        for ty in range(max(0, int((py - portee) // t_px)), min(hauteur, int((py + portee) // t_px) + 1)):
            for tx in range(max(0, int((px - portee) // t_px)), min(largeur, int((px + portee) // t_px) + 1)):
                e = math.hypot((tx + 0.5) * t_px - px, (ty + 0.5) * t_px - py)
                if e <= portee and e < d.get((tx, ty), math.inf):
                    d[(tx, ty)] = e
    return d


def _dans(rectangles, x: int, y: int) -> bool:
    return any(rx <= x < rx + rl and ry <= y < ry + rh for rx, ry, rl, rh in rectangles)


def plan_du_bloc(bloc: dict) -> list[str]:
    """Le plan, ses chemins posés : la chaussée sur chaque tuile dont le centre tombe dans la largeur,
    la lisière dégagée de ses arbres et buissons, la haie du bois (dans ses zones, sur l'herbe seulement).
    ⚠️ Ce que le chemin ne peut pas dégager (une corde de bois, de l'eau) reste : `erreurs` le dénonce."""
    plan = [list(ligne) for ligne in bloc["plan"]]
    if not bloc.get("chemins"):
        return ["".join(ligne) for ligne in plan]
    decors = bloc.get("decors", {})
    hauteur, largeur, t_px = len(plan), len(plan[0]), carte.TUILE_PX
    degageables = {g: sol for g, (sol, genre) in decors.items() if genre in DEGAGEABLES}
    for chemin in bloc["chemins"]:
        demi = chemin["largeur"] * t_px / 2
        lisiere = demi + LISIERE_TUILES * t_px
        for (x, y), e in distances_au_chemin(chemin, largeur, hauteur).items():
            g = plan[y][x]
            if e <= demi:
                if g in degageables or carte.LEGENDE.get(g, {}).get("terre"):
                    plan[y][x] = chemin["sol"]
            elif e <= lisiere:
                if g in degageables:
                    plan[y][x] = degageables[g]
            elif g == "," and _dans(chemin.get("bois", ()), x, y):
                plan[y][x] = chemin.get("arbre", "A")
    return ["".join(ligne) for ligne in plan]
```

⚠️ Deux chemins qui se croisent : la haie du second pousserait sur la chaussée du premier — le `g == ","`
l'en empêche (la chaussée est déjà `§`), mais pas l'inverse. Un seul chemin au rang : laisser ainsi, et le
dire dans le commentaire si un deuxième chemin arrive.

Puis faire lire `plan_du_bloc` partout où le module lisait `bloc["plan"]` :

```python
def sol_du_bloc(bloc: dict) -> list[str]:
    """Le plan (chemins posés), ses décors remplacés par le sol qu'ils couvrent."""
    decors = bloc.get("decors", {})
    return ["".join(decors[g][0] if g in decors else g for g in ligne) for ligne in plan_du_bloc(bloc)]


def decor_du_bloc(bloc: dict) -> list[dict]:
    decors = bloc.get("decors", {})
    return [{"type": decors[g][1], "x": x, "y": y}
            for y, ligne in enumerate(plan_du_bloc(bloc)) for x, g in enumerate(ligne) if g in decors]
```

Dans `erreurs`, remplacer `plan = bloc["plan"]` par `plan = plan_du_bloc(bloc)` **après** le contrôle des
largeurs de ligne (qui doit continuer de lire `bloc["plan"]`), et ajouter, juste avant
`# Le passage, dans la ville` :

```python
    # ⚠️ SES CHEMINS : la chaussée entière est du chemin (rien qu'on ne sache dégager dessus), aucun décor
    # sur la chaussée ni la lisière, et aucun virage qu'une auto ne prend pas.
    decors_poses = {(d["x"], d["y"]): d["type"] for d in decor_du_bloc(bloc)}
    for i, chemin in enumerate(bloc.get("chemins", ())):
        demi = chemin["largeur"] * carte.TUILE_PX / 2
        lisiere = demi + LISIERE_TUILES * carte.TUILE_PX
        for (x, y), e in sorted(distances_au_chemin(chemin, largeur, hauteur).items()):
            if e <= demi and sol[y][x] != chemin["sol"]:
                fautes.append(f"{slug} : le chemin {i} passe sur ({x}, {y}) {sol[y][x]!r}")
            if e <= lisiere and (x, y) in decors_poses:
                fautes.append(f"{slug} : un décor {decors_poses[(x, y)]} sur le chemin {i} en ({x}, {y})")
        pts = echantillonner(chemin["points"])
        k = 8                                                    # 32 px entre les trois points du cercle
        for a, b, c in zip(pts, pts[k:], pts[2 * k:]):
            ab, bc, ca = math.dist(a, b), math.dist(b, c), math.dist(c, a)
            aire2 = abs((b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0]))
            if aire2 > 1e-6 and ab * bc * ca / (2 * aire2) < RAYON_MIN_PX:
                fautes.append(f"{slug} : le chemin {i} a un virage trop serré vers ({b[0]:.0f}, {b[1]:.0f}) px")
                break
```

Dans `carte_du_bloc`, dans le dict `"bloc"`, après `"cheminees"` :

```python
                 # ⚠️ SES CHEMINS (la route en lacets du rang) : le tracé en pixels, que `Blocs.dessinerChemins`
                 # peint en ruban lisse ; les tuiles `§` dessous portent la vitesse et la collision.
                 "chemins": [{"largeur_px": c["largeur"] * carte.TUILE_PX,
                              "points": [[round(x, 1), round(y, 1)] for x, y in echantillonner(c["points"])]}
                             for c in bloc.get("chemins", ())],
```

- [ ] **Étape 4 : les voir passer, et rien d'autre de cassé**

```bash
uv run pytest tests/test_chemins_des_blocs.py tests/test_blocs.py tests/test_rang.py tests/test_bebelles.py tests/test_collections.py tests/test_decoration.py -q 2>&1 | tail -5
```
Attendu : PASS partout (aucun bloc n'a encore de chemin : `test_un_bloc_sans_chemin_n_a_pas_change`).
Si le juge du virage trop serré ne rougit pas sur `serre`, baisser `k` à 6 et relire le rayon calculé.

- [ ] **Étape 5 : la mutation** — remplacer temporairement `plan[y][x] = chemin.get("arbre", "A")` par
`pass`, vider `__pycache__` (`find . -name __pycache__ -path "*app*" -exec rm -rf {} +`), rejouer
`test_la_chaussee_la_lisiere_et_la_haie` : il doit rougir sur « un trou dans la haie ». Remettre.

- [ ] **Étape 6 : commit**

```bash
uv run ruff check app/blocs tests/test_chemins_des_blocs.py
git add app/blocs/__init__.py tests/test_chemins_des_blocs.py
git commit -m "feat: les chemins des blocs — une courbe douce posée sur la grille : sa chaussée, sa lisière dégagée, la haie de son bois, sans un dé (la route en lacets, tâche 2)"
```

---

### Tâche 3 : le rang — la route en lacets, la haie, le bois

**Fichiers :**
- Modifier : `app/blocs/rang.py` (`PLAN`, `BLOC["chemins"]`, docstring)
- Test : `tests/test_rang.py`

**Interfaces :**
- Consomme : `blocs.plan_du_bloc`, `blocs.sol_du_bloc`, `blocs.decor_du_bloc`, `blocs.distances_au_chemin`
  (tâche 2).
- Produit : `rang.CHEMIN` (le dict du chemin, aussi dans `BLOC["chemins"]`), `rang.HAIE_X` (la colonne de
  la haie tracée à la main).

- [ ] **Étape 1 : le juge des lacets obligatoires**

Ajouter à `tests/test_rang.py` :

```python
# --- La route en lacets (docs/jalons/une-route-en-lacets-vers-le-chalet.md) ---------------------------------

#: Les décors qui arrêtent un char (un buisson se traverse).
ARRETENT = ("arbre", "erable_seau", "erable_tube", "corde_bois", "table_tire")


def _en_char(depuis: tuple[int, int]) -> dict[tuple[int, int], int]:
    """Le nombre de tuiles, en char, de `depuis` à chaque tuile du rang. ⚠️ En HUIT directions, et une
    diagonale passe dès que la tuile d'arrivée est libre : entre deux troncs en biais (22 px entre les
    centres, 12 px de jour), un char ne passe pas, mais un juge trop gentil vaut mieux qu'un bois percé."""
    sol = blocs.sol_du_bloc(rang.BLOC)
    murs = {(d["x"], d["y"]) for d in blocs.decor_du_bloc(rang.BLOC) if d["type"] in ARRETENT}

    def libre(x, y):
        return (0 <= y < len(sol) and 0 <= x < len(sol[0]) and (x, y) not in murs and sol[y][x] != "~"
                and not carte.LEGENDE.get(sol[y][x], {}).get("solide"))

    dist, file = {depuis: 0}, [depuis]
    for x, y in file:
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                n = (x + dx, y + dy)
                if n not in dist and libre(*n):
                    dist[n] = dist[(x, y)] + 1
                    file.append(n)
    return dist


def test_en_char_on_ne_rejoint_le_chalet_que_par_les_lacets():
    """Martin (30 sept. 2026) : « Bois dense + route roulante ». Sans le bois, on file tout droit à travers
    le champ (32 tuiles) ; avec, on suit la route (plus de cent)."""
    a, c = rang.BLOC["arrivee"], rang.BLOC["planque"]["char"]
    dist = _en_char((a["x"], a["y"]))
    assert (c["x"], c["y"]) in dist, "la place du char ne se rejoint plus en char"
    assert dist[(c["x"], c["y"])] >= 100, f"un raccourci : {dist[(c['x'], c['y'])]} tuiles jusqu'au chalet"
    # Et la cabane, lieu public, reste tout près de l'entrée.
    porte = next(p for p in rang.BLOC["portes"] if p["interieur"] == "cabane")
    assert dist[(porte["x"], porte["y"] + 1)] <= 25


def test_le_quatre_roues_est_du_cote_du_chalet():
    c, q = rang.BLOC["planque"]["char"], rang.BLOC["quatre_roues"]
    dist = _en_char((c["x"], c["y"]))
    assert (q["x"], q["y"]) in dist and dist[(q["x"], q["y"])] <= 12, "la haie sépare le 4 roues du chalet"


def test_la_route_est_roulante_et_sans_decor():
    assert [f for f in blocs.erreurs(rang.BLOC) if "chemin" in f or "virage" in f] == []
    sol = blocs.sol_du_bloc(rang.BLOC)
    assert sum(ligne.count("§") for ligne in sol) > 300, "une route bien courte"
    # Le vieux L de gravier est parti : plus de `g` sur les rangées de l'entrée, sauf les allées.
    assert "g" not in sol[25][20:60], sol[25]
```

- [ ] **Étape 2 : les voir rougir** — `uv run pytest tests/test_rang.py -q -k "lacets or quatre_roues or roulante"`
— Attendu : FAIL (le rang n'a pas de chemin : ~32 tuiles jusqu'au chalet).

- [ ] **Étape 3 : récrire le PLAN par un script, pas à la main**

Le `PLAN` a 80 colonnes et une erreur de frappe décale tout. Le récrire par un script jetable
(scratchpad), qui imprime les lignes à recoller dans `rang.py` :

```python
# …/scratchpad/nouveau_plan.py — lancé depuis le worktree : uv run python …/scratchpad/nouveau_plan.py
import sys
sys.path.insert(0, ".")
from app.blocs.rang import PLAN

HAIE_X = 53                      # entre le 4 roues (52, 19) et les gens de la cabane (56, 18)
g = [list(l) for l in PLAN]
# 1. Le vieux L : les rangées 23 à 26, de x = 17 au bord est, redeviennent de l'herbe —
#    sauf (64, 23), le bout de l'allée de la cabane, qui rejoint la route un peu plus bas.
for y in range(23, 27):
    for x in range(17, 80):
        if g[y][x] == "g" and (x, y) != (64, 23):
            g[y][x] = ","
# 2. La haie tracée à la main : la colonne HAIE_X, du bord nord jusqu'au bois (rangée 22),
#    un arbre sur chaque tuile d'herbe ; les cordes de bois, les érables et les toits restent.
for y in range(1, 23):
    if g[y][HAIE_X] in ",b":
        g[y][HAIE_X] = "A"
for l in g:
    print(f'    "{"".join(l)}",')
```

Coller la sortie à la place du corps de `PLAN`. **Avant**, afficher les colonnes 50 à 57 des rangées 1 à
22 (`print([l[50:58] for l in PLAN[1:23]])`) : si `HAIE_X` tombe sur un `T` (érable à tubulure) ou un `L`,
la haie a un trou là — ces décors arrêtent un char, c'est permis ; si elle tombe sur un `g` ou un `p`,
choisir 54 ou 55 et relancer.

- [ ] **Étape 4 : le chemin**

Dans `rang.py`, avant `BLOC` :

```python
#: ⚠️ LA ROUTE EN LACETS (docs/jalons/une-route-en-lacets-vers-le-chalet.md) — Martin (30 sept. 2026) :
#: « Montée vers le chalet », « Lacets dans le bois », « Bois dense + route roulante ». De l'entrée est,
#: devant l'allée de la cabane, on plonge au sud-ouest dans le bois, deux grands virages, on remonte le long
#: du lac, et on arrive au chalet PAR L'OUEST, au bout du chemin. La haie pousse dans la zone du bois (le
#: sud-ouest, sous la rangée 22) ; la haie de `HAIE_X`, tracée dans le plan, sépare la cabane du chalet.
HAIE_X = 53
CHEMIN = {
    "points": [(80, 25), (66, 25.5), (52, 27), (42, 31), (40, 37), (30, 42), (18, 41), (9, 34), (12, 26),
               (20, 21.5), (30, 22), (38, 22), (43.5, 22.5)],
    "largeur": 3, "sol": "§", "arbre": "A", "haie": 2,
    "bois": [[1, 22, HAIE_X, 27]],
}
```

et dans `BLOC`, après `"cheminees"` : `"chemins": [CHEMIN],`.

- [ ] **Étape 5 : regarder le plan cuit avant de juger**

```bash
uv run python -c "
from app import blocs; from app.blocs import rang
for i, l in enumerate(blocs.plan_du_bloc(rang.BLOC)): print(f'{i:2} {l}')
print(blocs.erreurs(rang.BLOC))"
```
Lire : la route `§` continue de l'est au chalet, l'allée `g` du chalet (x 43) la touche, celle de la
cabane (x 64) aussi, le raccord de la calèche (x 62-63, rangées 27-28) aussi, l'embranchement du quai
(x 17-19) aussi ; la haie ferme le bois. `erreurs` doit être `[]`. S'il reste une faute « un décor … sur
le chemin » (un érable `E` de la calèche trop près, x ≥ 45), déplacer d'une demi-tuile vers l'ouest le point
de passage le plus proche (`(42, 31)` ou `(40, 37)`) et relancer.

- [ ] **Étape 6 : les juges du rang, les anciens compris**

```bash
uv run pytest tests/test_rang.py tests/test_blocs.py tests/test_bebelles.py tests/test_collections.py tests/test_decoration.py tests/test_quatre_roues.py tests/test_chemins_des_blocs.py -q 2>&1 | tail -8
```
Attendu : PASS. Pièges connus :
- `test_le_sentier_de_la_caleche_est_libre…` : si la haie pousse à moins de 18 px du sentier, rétrécir le
  rectangle du bois (`[1, 22, 45, 27]`) plutôt que de toucher au sentier.
- `test_les_gens_de_la_cabane_se_tiennent…` lit `sol[t["y"]][64] == "g"` : l'allée de la cabane ne doit pas
  être avalée par la route (elle ne l'est pas : la route passe sous la rangée 23).
- Le juge de la raquette en babiche (`test_bebelles.py`) : sa place bouge — c'est attendu. S'il
  compare à une place écrite en dur, écrire la nouvelle place dans le juge avec un commentaire qui dit
  pourquoi (le bois du 30 sept. 2026), et vérifier qu'elle est encore dans la moitié sud-ouest du rang.
- `test_blocs_js.py::test_les_arbres_du_bloc_sont_la…` pousse le joueur contre l'arbre de la tuile 0 de
  la rangée 30 depuis (4, 30) : les tuiles 1 à 4 de la rangée 30 doivent rester libres. Vérifier dans le
  plan cuit ; sinon, y choisir une autre rangée libre et dire pourquoi.

- [ ] **Étape 7 : la mutation** — retirer `"bois"` du `CHEMIN` (et vider `__pycache__`) :
`test_en_char_on_ne_rejoint_le_chalet_que_par_les_lacets` doit rougir (un raccourci). Remettre. Puis
retirer la haie de `HAIE_X` (relancer le script sans l'étape 2) : le même juge doit rougir. Remettre.

- [ ] **Étape 8 : commit**

```bash
uv run ruff check app/blocs tests/test_rang.py
git add app/blocs/rang.py tests/test_rang.py
git commit -m "feat: la route en lacets vers le chalet — le vieux chemin en L devient une route roulante qui plonge dans le bois, et le chalet est au bout ; une haie sépare la cabane du chalet (tâche 3)"
```

---

### Tâche 4 : le ruban, peint sous la neige

**Fichiers :**
- Modifier : `static/js/blocs.js` (nouvelle fonction `dessinerChemins`, exportée)
- Modifier : `static/js/jeu.js:1246` (l'appeler juste après `Monde.dessinerSol`)
- Test : `tests/test_chemins_des_blocs_js.py`

**Interfaces :**
- Consomme : `B.bloc.def.bloc.chemins` (`[{largeur_px, points: [[x, y], …]}]`, tâche 2) ; `TUILES['g']`
  (sprites.js) ; `hash2` (base.js:337).
- Produit : `Blocs.dessinerChemins(ctx, cam)`.

- [ ] **Étape 1 : le juge de l'ordre des peintres**

Ajouter à `tests/test_chemins_des_blocs_js.py` (reprendre `OUTILS` et `VOLANT` de `test_blocs_js.py` en
les important : `from test_blocs_js import OUTILS`) :

```python
from test_blocs_js import OUTILS


def test_au_rang_le_ruban_est_peint_sous_la_neige(banc):
    """⚠️ Une partie commence en janvier : un ruban peint APRÈS la neige ferait une route brune dans un rang
    blanc. `Jeu.rendre()` (pas `frame`, qui fait bouger le monde) ; on note l'ordre des peintres."""
    r = banc("async function (L, o) {" + OUTILS + """
        L.Jeu.commencer();
        auPassage(L, o); await laisserArriver(L, o); pousser(L, o, 'KeyA');
        const B = L.B, ch = B.bloc.def.bloc.chemins[0], p = ch.points[Math.floor(ch.points.length / 2)];
        B.joueur.x = p[0]; B.joueur.y = p[1]; L.Entites.indexer();
        for (let i = 0; i < 3; i++) o.frame(1);
        const ordre = [], neige = L.Neige.dessinerSol, ruban = L.Blocs.dessinerChemins;
        L.Neige.dessinerSol = function () { ordre.push('neige'); return neige.apply(this, arguments); };
        L.Blocs.dessinerChemins = function (ctx) {
          const trait = ctx.stroke; let n = 0;
          ctx.stroke = function () { n++; return trait.apply(this, arguments); };
          const r = ruban.apply(this, arguments); ctx.stroke = trait;
          ordre.push('ruban:' + n); return r;
        };
        L.Jeu.rendre();
        L.Neige.dessinerSol = neige; L.Blocs.dessinerChemins = ruban;
        return { bloc: B.bloc && B.bloc.slug, ordre: ordre, points: ch.points.length, largeur: ch.largeur_px };
    }""")
    assert r["bloc"] == "rang" and r["largeur"] == 48 and r["points"] > 300, r
    peints = [o for o in r["ordre"] if o.startswith("ruban:")]
    assert peints and int(peints[0].split(":")[1]) >= 2, f"le ruban n'a rien tracé : {r['ordre']}"
    assert r["ordre"].index(peints[0]) < r["ordre"].index("neige"), f"le ruban est peint sur la neige : {r['ordre']}"
```

⚠️ Si `jeu.js` appelle `Neige.dessinerSol` par une référence gardée (pas `Neige.dessinerSol(…)` à chaque
image), l'espion ne la voit pas : lire la ligne 1251 de `jeu.js` ; elle l'appelle bien par la propriété.
Même chose pour `Blocs.dessinerChemins`, qu'on appellera par la propriété.

- [ ] **Étape 2 : le voir rougir** — `uv run pytest tests/test_chemins_des_blocs_js.py -q -k neige` —
Attendu : FAIL (`L.Blocs.dessinerChemins` n'existe pas, ou « le ruban n'a rien tracé »).

- [ ] **Étape 3 : le peintre**

Dans `static/js/blocs.js`, avant `/** Une plaque de bois, le mot… */ function dessiner` :

```js
  /* ⚠️ LES CHEMINS DU BLOC (la route en lacets du rang, docs/jalons/une-route-en-lacets-vers-le-chalet.md) :
     un ruban de gravier au bord LISSE, par-dessus des tuiles `§` peintes en herbe. Appelé juste après
     `Monde.dessinerSol`, donc SOUS la neige, le verglas et les traces de pneus : l'hiver le blanchit comme
     le reste. Le grain est celui du `g` des allées, en motif ancré au monde (il ne glisse pas avec la
     caméra). */
  //: La lisière d'herbe foulée déborde du ruban de tant de pixels de chaque côté.
  const LISIERE_PX = 6;
  //: Les ornières : à cette part de la demi-largeur, de chaque côté du milieu.
  const ORNIERES = 0.45;
  let motif = null;
  function motifDuChemin(ctx) {
    if (motif) return motif;
    const c = document.createElement('canvas');
    c.width = c.height = 4 * TT;
    const g = c.getContext('2d');
    for (let j = 0; j < 4; j++) for (let i = 0; i < 4; i++) {
      g.save(); g.translate(i * TT, j * TT); TUILES['g'](g, hash2(i, j) & 15, TT); g.restore();
    }
    motif = ctx.createPattern(c, 'repeat');
    return motif;
  }
  /** La même courbe, décalée de `d` pixels sur sa normale (les ornières). */
  function decaler(pts, d) {
    return pts.map(function (p, i) {
      const a = pts[Math.max(0, i - 1)], b = pts[Math.min(pts.length - 1, i + 1)];
      const dx = b[0] - a[0], dy = b[1] - a[1], n = Math.hypot(dx, dy) || 1;
      return [p[0] - dy / n * d, p[1] + dx / n * d];
    });
  }
  function trait(ctx, pts, largeur, style) {
    ctx.strokeStyle = style; ctx.lineWidth = largeur; ctx.lineCap = 'round'; ctx.lineJoin = 'round';
    ctx.beginPath();
    ctx.moveTo(pts[0][0], pts[0][1]);
    for (let i = 1; i < pts.length; i++) ctx.lineTo(pts[i][0], pts[i][1]);
    ctx.stroke();
  }
  function dessinerChemins(ctx, cam) {
    const b = B.bloc && B.bloc.def && B.bloc.def.bloc;
    if (B.interieur || !b || !b.chemins || !b.chemins.length) return;
    ctx.save();
    ctx.translate(-Math.round(cam.x), -Math.round(cam.y));      // tout en pixels du monde : le motif s'y ancre
    for (const ch of b.chemins) {
      if (!ch.ornieres) {
        const d = ch.largeur_px / 2 * ORNIERES;
        ch.ornieres = [decaler(ch.points, -d), decaler(ch.points, d)];
      }
      trait(ctx, ch.points, ch.largeur_px + 2 * LISIERE_PX, 'rgba(58,82,40,0.30)');   // l'herbe foulée
      trait(ctx, ch.points, ch.largeur_px, motifDuChemin(ctx));                       // le gravier
      for (const o of ch.ornieres) trait(ctx, o, 3, 'rgba(126,110,78,0.55)');        // les ornières
      B.stats.rects += 4;
    }
    ctx.restore();
  }
```

Ajouter `dessinerChemins` à l'objet que rend le module (la ligne `return { … }` en bas de `blocs.js`).

⚠️ `document.createElement('canvas')` au banc : lire comment `tests/banc.js` fabrique ses canevas (il
fournit `createPattern`, ligne 36). Si `document.createElement('canvas')` n'y rend pas un canevas avec
`getContext`, regarder comment `monde.js` fabrique les morceaux de 256 px de son cache et faire pareil.

⚠️ Performance : 4 traits d'environ 800 points par image, seulement au rang. Si `B.stats` montre un coût,
couper les points hors de l'écran (garder ceux à moins de `largeur_px` du cadre de la caméra).

- [ ] **Étape 4 : l'appeler au bon moment**

Dans `static/js/jeu.js`, juste après `Monde.dessinerSol(ctx, vue);` (ligne ~1246) :

```js
    if (!B.interieur) Blocs.dessinerChemins(ctx, vue);  // la route en lacets du rang : SOUS la neige et les traces
```

- [ ] **Étape 5 : le voir passer, puis la mutation**

`uv run pytest tests/test_chemins_des_blocs_js.py -q` — Attendu : PASS. Puis déplacer temporairement
l'appel **après** `Neige.dessinerSol` : le juge doit rougir « peint sur la neige ». Remettre.

- [ ] **Étape 6 : regarder, été et janvier**

Recette de la mémoire « capturer une pièce du jeu », adaptée : un script jetable dans le scratchpad qui
lance le serveur du worktree (werkzeug, port 0, `DONNEES_DIR` temporaire), ouvre Chromium, passe
l'ouverture, entre au rang (`L.Jeu.commencer()` puis poser le joueur au passage du rang et pousser vers
l'ouest, comme `OUTILS`), pose le joueur sur un virage (`chemins[0].points[250]`), et fait deux captures :
`B.partie.jour = 21` (juillet) et `B.partie.jour = 1` (janvier). Les copier dans `captures/` et les ouvrir
(`open`). Regarder : bord lisse sans marches, grain du gravier, ornières qui suivent la courbe, haie
d'arbres des deux côtés, et en janvier une route blanchie comme le reste. Montrer les deux à Martin.

- [ ] **Étape 7 : commit**

```bash
uv run ruff check .
git add static/js/blocs.js static/js/jeu.js tests/test_chemins_des_blocs_js.py
git commit -m "feat: la route en lacets se peint en ruban lisse — le grain du gravier, la lisière foulée et deux ornières, sous la neige (tâche 4)"
```

---

### Tâche 5 : au banc, un char suit la route jusqu'au chalet, et en revient

**Fichiers :**
- Test : `tests/test_chemins_des_blocs_js.py`

**Interfaces :**
- Consomme : `B.bloc.def.bloc.chemins[0].points`, `B.bloc.def.bloc.planque.char`, `OUTILS` et `VOLANT` de
  `test_blocs_js.py`.

- [ ] **Étape 1 : le juge**

```python
from test_blocs_js import OUTILS, VOLANT  # remplace l'import de la tâche 4


def test_au_volant_on_suit_la_route_jusqu_au_chalet_et_on_en_revient(banc):
    """On arrive de la ville au volant, et un pilote simple suit le tracé (le cap vers un point 32 px plus
    loin, la pédale enfoncée) : il atteint la place du char du chalet sans rester collé à un tronc, puis
    refait le chemin à l'envers jusqu'au bord est. ⚠️ Le cap est POSÉ, pas braqué : on juge que la route se
    roule (pas d'arbre, pas de mur, la vitesse du chemin), pas l'adresse du pilote."""
    r = banc("async function (L, o) {" + OUTILS + VOLANT + """
        L.Jeu.commencer(); L.B.partie.jour = 21;
        const B = L.B, j = B.joueur;
        auPassage(L, o); await laisserArriver(L, o);
        const v = auVolant(L, o, 'auto'); foncer(L, o, 60);
        if (!B.bloc) return { bloc: null };
        const ch = B.bloc.def.bloc.chemins[0].points, c = B.bloc.def.bloc.planque.char;
        const place = [c.x * TT + 8, c.y * TT + 8];
        function conduire(cibles, n) {
          let i = 0, colle = 0, avant = [v.x, v.y], ecart = 0;
          o.touche('KeyW');
          for (let f = 0; f < n; f++) {
            while (i < cibles.length - 1 && Math.hypot(cibles[i][0] - v.x, cibles[i][1] - v.y) < 32) i++;
            v.angle = Math.atan2(cibles[i][1] - v.y, cibles[i][0] - v.x);
            if (v.vitesse > 2.2) o.relacher('KeyW'); else o.touche('KeyW');   // lent : la conduite simulée
            o.frame(1);
            ecart = Math.max(ecart, Math.min.apply(null, ch.map(function (p) { return Math.hypot(p[0] - v.x, p[1] - v.y); })));
            if (f % 60 === 59) { colle = Math.hypot(v.x - avant[0], v.y - avant[1]) < 4 ? colle + 1 : 0; avant = [v.x, v.y]; }
            if (colle >= 3 || (i === cibles.length - 1 && Math.hypot(cibles[i][0] - v.x, cibles[i][1] - v.y) < 12)) break;
          }
          o.relacher('KeyW');
          return { colle: colle >= 3, x: Math.round(v.x), y: Math.round(v.y), ecart: Math.round(ecart), bloc: B.bloc && B.bloc.slug };
        }
        const aller = conduire(ch.concat([place]), 9000);
        const auChalet = Math.hypot(v.x - place[0], v.y - place[1]);
        const retour = conduire([place].concat(ch.slice().reverse()), 9000);
        return { bloc: 'rang', aller: aller, auChalet: Math.round(auChalet), retour: retour,
                 largeur: B.bloc ? B.bloc.def.bloc.chemins[0].largeur_px : null };
    }""")
    assert r["bloc"] == "rang", r
    assert not r["aller"]["colle"] and r["auChalet"] < 16, f"le char n'atteint pas le chalet : {r}"
    assert r["aller"]["ecart"] <= 40, f"le pilote a quitté la route : {r}"
    # Au retour, le char repasse le bord est : on est revenu en ville (ou collé au bord, à moins d'une tuile).
    assert not r["retour"]["colle"] and (r["retour"]["bloc"] is None or r["retour"]["x"] > 78 * 16), r
```

⚠️ Réglages à vérifier au premier essai, en lisant ce que le juge rend (pas en devinant) : le nom de la
vitesse (`v.vitesse`, sinon `grep -n "vitesse" static/js/vehicules.js | head`) et son unité (px par image) ;
le seuil `2.2` doit laisser prendre les virages sans glisser dans la haie ; `9000` images suffisent-elles
(la route fait ~2 400 px). Si le char reste collé, lire `x, y` : un tronc à la lisière est une faute de la
tâche 3, pas du juge.

- [ ] **Étape 2 : le lancer** — `uv run pytest tests/test_chemins_des_blocs_js.py -q -k lacets` — Attendu :
PASS (tout est déjà posé). S'il passe du premier coup, c'est ici qu'il doit mordre :

- [ ] **Étape 3 : la mutation** — dans `rang.py`, raccourcir `LISIERE_TUILES` à 0 **et** passer `"haie"` à
3 (la haie mord sur le bord de la route), vider `__pycache__` : le juge doit rougir (collé, ou écart).
Remettre les deux.

- [ ] **Étape 4 : rejouer les juges de bloc au volant, qui entrent par la même route**

```bash
uv run pytest tests/test_blocs_js.py tests/test_quatre_roues_js.py tests/test_chalet_js.py -q 2>&1 | tail -5
```
Attendu : PASS. `test_au_volant_on_passe_avec_son_char…` pose le char en (70, 25) et fonce vers l'est :
la route y est droite et roulante — il doit rester vert.

- [ ] **Étape 5 : commit**

```bash
uv run ruff check tests/test_chemins_des_blocs_js.py
git add tests/test_chemins_des_blocs_js.py
git commit -m "test: au volant, on suit la route en lacets jusqu'au chalet et on en revient (tâche 5)"
```

---

### Tâche 6 : la doc, et atterrir

**Fichiers :**
- Modifier : `docs/architecture.md` (la ligne `blocs/` du tableau Python ; la liste des fichiers de tests)
- Modifier : `docs/jalons/une-route-en-lacets-vers-le-chalet.md` (« Notes »)
- Modifier : `docs/plan.md` (retirer la ligne) et `docs/jalons/README.md` (l'ajouter en ✅)

- [ ] **Étape 1 : la carte du dépôt** — dans `docs/architecture.md`, à la ligne `blocs/`, ajouter après la
description du rang : « **ses chemins** (30 sept. 2026, la route en lacets) : `chemins` — une courbe
posée sur la grille (`plan_du_bloc` : la chaussée `§`, la lisière, la haie du bois), le tracé exporté en
pixels, peint en ruban par `Blocs.dessinerChemins` » ; et ajouter `test_chemins_des_blocs.py
test_chemins_des_blocs_js.py` à la liste des tests (ligne ~259). Vérifier :
`uv run python scripts/verifier_carte_du_depot.py` — Attendu : code 0.

- [ ] **Étape 2 : les notes de livraison** — sous « ## Notes » de ce fichier : **Livré le …** puis une puce
par morceau (le glyphe, les chemins des blocs, le rang, le ruban, les juges et leurs mutations), et la
nouvelle place de la raquette.

- [ ] **Étape 3 : déplacer la ligne** — la retirer de `docs/plan.md`, l'ajouter en bas de
`docs/jalons/README.md` en `✅ **livré**` avec sa date (copier le format de la dernière ligne), puis
`uv run python scripts/verifier_table_des_jalons.py` — Attendu : code 0.

- [ ] **Étape 4 : les juges ciblés, puis atterrir tout de suite**

```bash
uv run ruff check .
uv run pytest tests/test_chemins_des_blocs.py tests/test_chemins_des_blocs_js.py tests/test_rang.py tests/test_blocs.py tests/test_blocs_js.py tests/test_bebelles.py tests/test_collections.py tests/test_decoration.py tests/test_quatre_roues.py tests/test_quatre_roues_js.py tests/test_chalet_js.py tests/test_carte.py tests/test_definitions.py -q 2>&1 | tail -5
git add docs/architecture.md docs/plan.md docs/jalons/README.md docs/jalons/une-route-en-lacets-vers-le-chalet.md
git commit -m "docs: une route en lacets vers le chalet — livrée"
```
Puis atterrir sur `dev` : `git fetch -q --all && git rebase dev`, rejouer les juges ciblés si `dev` a bougé,
puis, depuis l'arbre principal (propre) : `git merge --ff-only claude/route-en-lacets`. Pousser `dev`
(`git push origin dev`). La suite complète se lance **après** l'atterrissage, détachée ; un rouge se rejoue
sur le commit d'avant pour savoir s'il est de nous.

## Notes

### Livré le 1er oct. 2026

Les tâches 1 à 3 par la session qui a ouvert le jalon (30 sept.) ; la 4 à la 6, reprises de sa branche
`claude/route-en-lacets` et finies par une autre session (Martin : « la finir moi-même »).

- **Le glyphe `§`** (gravier roulé) : pas de la `terre`, une auto y roule à pleine vitesse, l'herbe la ralentit
  toujours ; la tuile se peint en herbe, sous le ruban. Le `g` de la ville ne bouge pas.
- **Les chemins des blocs** (`app/blocs/__init__.py`, `plan_du_bloc`) : une courbe Catmull-Rom échantillonnée tous
  les 4 px, la chaussée sur chaque tuile dont le centre tombe dans la largeur, une tuile de lisière dégagée, la
  haie dans les zones du bois — sur l'herbe, et sur les buissons (un char traverse un buisson : resté dans la haie,
  il coupait la boucle des lacets). Sans un dé ; réutilisable par un autre bloc.
- **Le rang** : le vieux chemin en L devient la route en lacets, du passage est jusqu'au chalet, par l'ouest ; la
  haie de `HAIE_X` sépare la cabane du chalet ; le sentier de la calèche, la planque et le 4 roues ne bougent pas.
- **Le ruban** (`Blocs.dessinerChemins`, appelé juste après `Monde.dessinerSol`) : le grain du `g` en motif ancré
  au monde, une lisière d'herbe foulée, deux ornières qui suivent la courbe ; SOUS la neige, le verglas et les
  traces. Regardé en juillet et en janvier : le bord reste lisse ; l'hiver, la route reste brune comme les allées
  droites du rang (la neige ne couvre pas leur gravier), le bois et les champs blanchissent autour.
- **La raquette en babiche** se cache maintenant au nord du rang, en (52, 3) (avant : (2, 47), au fond du bois) :
  la haie et le bois rallongent le chemin à pied ; la règle reste sans dé, `test_bebelles` vert.
- **Juges** : `test_chemins_des_blocs.py` (8), `test_rang.py` (+3), `test_chemins_des_blocs_js.py` (3 : la vitesse
  sur `§`, le ruban sous la neige, l'aller-retour au volant jusqu'à la place du char du chalet).
- **Mutations** : le ruban appelé APRÈS `Neige.dessinerSol` → rouge (« peint sur la neige »). Celle du plan pour le
  volant (`LISIERE_TUILES = 0` et une haie de 3) reste VERTE : sans lisière, les troncs sont encore à 24 px du
  centre, la route se roule — la mutation ne cassait rien. Une chaussée d'UNE tuile sans lisière (troncs à 8 px)
  → rouge, le char collé dans le bois à (662, 583). ⚠️ Le juge du volant ne mesure l'écart à la route que pendant
  qu'il vise un point DE la route, dans le bloc : la place du char est à ~80 px du bout du chemin.
