# Le train

← [le plan](../plan.md) · [les jalons livrés](README.md)

## Fiche

_Demande de Martin (28 sept. 2026) :_ « je veux un vrai train aérien, terrestre et tunnel. »

Ce qui roule déjà n'en est pas un : le [métro](le-metro.md) ne se voit qu'au quai et dans la voiture, le
tramway est un autobus sur rails dans la rue, et la Gare de triage a perdu ses voies (elles sont devenues la
cour à scrap des Boulonneux) — elle n'a plus de train.

**Tranché avec Martin le même jour** (quatre questions, quatre « oui ») :

- **Ce qu'il apporte : tout.** On le **voit** passer (viaduc, passages à niveau, portail du tunnel), on y
  **monte** à une gare, et il **écrase** ce qui traîne sur la voie.
- **Une ligne de passage**, pas une boucle : un vrai train interurbain qui entre à l'ouest hors carte et
  sort à l'est, **dans les deux sens**.
- **À bord, les deux** : s'asseoir dans le wagon (une pièce), ou rester sur la plateforme avec la caméra
  qui suit le train dehors.
- **Le viaduc est une couche du haut** (voir plus bas), pas des tuiles pleines : les rues passent dessous.

### Le tracé

D'ouest en est, la bande nord ([`app/nord.py`](../../app/nord.py)) va Friches (`bx 0`) → Petit-Canton
(`bx 5`) → Gare de triage (`bx 13`) → montagnes (`app/relief.py`) : exactement sol, aérien, gare, tunnel.

| Tronçon | Niveau | Ce qu'on y voit |
|---|---|---|
| Ouest, hors carte → les Friches | **au sol** | des passages à niveau : feux qui clignotent, cloche, barrières ; les chars attendent |
| Le Petit-Canton | **aérien** | le viaduc monte avant le quartier, enjambe la rue principale et redescend ; chars et gens passent **dessous**, entre les piliers |
| La Gare de triage | **au sol** | la **gare centrale** : un quai, un bâtiment de voyageurs |
| Est : les montagnes | **tunnel** | un portail de béton ; le train y entre et sort de la carte |

**Trois arrêts** : le quai des Friches, la station du viaduc (un escalier monte au quai), la gare centrale.

### Deux règles de fond

- ⚠️ **Le train est une heure**, comme la rame du métro et l'autobus : sa place sur la ligne ne dépend que
  du temps de la partie — rien à simuler, pas un dé (`B.rng` intact), la même place au rechargement. Un train
  vers l'est, puis un vers l'ouest, chacun à son heure.
- ⚠️ **La voie se pose en tout dernier dans `generer`, sans dé** (grossir un lieu garanti déplace la
  ville) : la ville avec et sans la voie est la même, clé par clé. Une clé neuve
  de la carte = une ligne dans `nord.DECALAGES`.

### Le viaduc : une couche du haut

Au niveau de la rue, le viaduc n'est que ses **piliers** (solides) ; la ville dessous garde toutes ses
tuiles, ses rues restent ouvertes. Le **tablier** et le train se dessinent **par-dessus** les chars et les
gens (après `Entites.dessiner`), avec leur ombre au sol. Écartés : le viaduc en tuiles pleines (un mur à
travers le Petit-Canton) et le viaduc seulement au-dessus du vide (on ne passe jamais dessous — c'est pourtant
ce qui fait vrai).

### Subir le train

- **Les passages à niveau.** Quelques secondes avant le train : feux, cloche, barrières qui descendent. Le
  trafic s'y arrête comme à un feu rouge (un « bloqué » que les chars lisent) ; les barrières remontent
  derrière le dernier wagon. Un char peut les **défoncer**, comme les barrières coulissantes.
- **Sur la voie** : un **char** est poussé de côté et cabossé — à grande vitesse, il prend feu ; un
  **piéton**, toi compris, meurt. **Le train ne freine jamais** : il klaxonne quand quelque chose est devant,
  et il passe. Rien ne l'arrête ni ne le dévie — pas même un autobus.
- **Sous le viaduc**, rien : seuls les piliers sont solides.
- **Le tunnel ne se visite qu'à bord** : son portail est clôturé.
- **Marcher sur la voie** est permis au sol (Friches, gare) — c'est là tout le danger ; sur le viaduc et dans
  le tunnel, on ne met les pieds qu'à bord.
- **La police** : **pas de billet quand on est recherché**, comme au métro (sinon, la meilleure cachette du
  jeu). Mais **sauter sur la plateforme d'un train arrêté en gare** reste possible en fuite, et l'hélico
  suit : une évasion, pas une téléportation.
- **Le son** : la cloche des passages, le klaxon grave, le roulement — fort de près, étouffé sur le viaduc
  au-dessus de soi. Bruitages ElevenLabs, la synthèse en filet ([audio](../../app/audio.py)).

### Monter à bord

- **En gare**, on se tient sur le quai : « TRAIN VERS L'EST — GARE CENTRALE — 5 $ · DANS 14 S ». Le train
  entre, ralentit pour de vrai, s'arrête une dizaine de secondes portes ouvertes, et repart à son heure —
  avec ou sans toi.
- **S'ASSEOIR** : le wagon, une pièce du CATALOGUE partagée comme la rame du métro (banquettes,
  porte-bagages) ; aux fenêtres, le paysage **du tronçon** — les Friches, les toits du Petit-Canton vus d'en
  haut, le noir du tunnel et ses lampes. « PROCHAINE GARE : GARE CENTRALE ».
- **RESTER SUR LA PLATEFORME** : le bonhomme à l'arrière du dernier wagon, la caméra suit le train dehors ;
  dans le tunnel, l'écran passe au noir et les lampes filent.
- **On change d'idée en route**, d'une pression : du wagon à la plateforme, et l'inverse.
- **Descendre** : en gare, sur **son** quai (à la station du viaduc, l'escalier ramène à la rue). **En
  marche, depuis la plateforme**, on peut **sauter** — au sol seulement : on roule par terre et l'on perd de
  la vie selon la vitesse ; sur le viaduc et dans le tunnel, refusé.
- **Les bouts de la ligne** : rester à bord jusqu'au tunnel ramène à la gare centrale ; le train sort de la
  carte, le joueur jamais.
- **Sauvegarde** : sauver à bord, c'est sauver à la gare d'où l'on est parti (comme le métro recale
  `B.exterieur` sur son édicule). **La grande carte** trace la ligne : pleine au sol, doublée sur le viaduc,
  en pointillé dans le tunnel.

### Les vagues

1. **Le train passe.** La voie posée en dernier sans dé : au sol, le viaduc (piliers, tablier dans la couche
   du haut, ombre), le portail du tunnel ; le train à son heure dans les deux sens ; les passages à niveau et
   le trafic qui s'arrête ; les collisions ; les sons ; la ligne sur la grande carte. _À la fin, on le voit
   passer et il peut t'écraser._
2. **On monte.** Les trois quais, le billet et son refus quand on est recherché, la plateforme et la caméra
   qui suit, sauter en marche, descendre à son quai, la sauvegarde recalée.
3. **On s'assoit.** Le wagon ; le paysage aux fenêtres selon le tronçon ; passer du wagon à la plateforme et
   revenir.

### Les juges (chacun rouge avant sa règle)

- **La ville ne bouge pas** : la même ville avec et sans la voie, clé par clé.
- **Les rues restent ouvertes** : chaque rue du Petit-Canton reste traversable sous le viaduc ; seuls les
  piliers sont solides.
- **Le train est une heure** : même heure, même place ; `B.rng` intact.
- **Un char attend au passage à niveau** ; un autre, laissé sur la voie, est poussé.
- **Au banc sous Node** : prendre le billet et descendre à la gare centrale — **au bouton**, pas en appelant
  la fonction.
- **Le poids du paquet** (`test_definitions`), et une **capture Chromium** de chaque niveau (sol, viaduc,
  portail) avant de livrer : un juge vert ne voit pas un dessin raté.

### Plan d'exécution — vague 1 : le train passe

> **Pour l'agent qui exécute :** sous-compétence REQUISE : `superpowers:subagent-driven-development` (recommandé) ou
> `superpowers:executing-plans`, tâche par tâche. Les étapes se cochent (`- [ ]`). Registre tenu à la main dans
> `<wt>/.superpowers/sdd/le-train/progress.md` (les titres disent « Tâche N », pas « Task N »).

**But :** un train visible traverse la bande nord d'ouest en est et retour — au sol dans les Friches, sur un viaduc
au-dessus du Petit-Canton, au sol à la Gare de triage, puis dans un tunnel sous les montagnes —, ferme ses passages
à niveau, et écrase ce qui reste sur sa voie.

**Architecture :** Python (`app/train.py`) ne pose **rien** dans la ville : il lit la ville finie et rend une clé
`train` (la voie, le viaduc, les piliers, les passages, le tunnel, les gares, l'horaire). Le navigateur
(`static/js/train.js`) calcule la place du train **à partir du seul temps de la partie** (`Autobus.tempsDeLaPartie()`),
dessine la voie, le viaduc et le train, rend les piliers solides, donne un signal d'arrêt au trafic et heurte ce qui
est sur la voie. **Une seule voie, un seul train à la fois** : vers l'est, puis vers l'ouest.

**Pile :** Python 3.11 (génération), JavaScript sans cadre (navigateur), pytest + le banc Node (`tests/banc.js`),
Playwright pour la capture.

**Spec :** cette fiche, plus haut.

#### Contraintes globales

- Le train est **une heure** : `Train.etat(t)` est une fonction pure de `t = Autobus.tempsDeLaPartie()` ; **pas un dé**
  (`B.rng` jamais appelé depuis `train.js`) ; aucun état qui survit à une image sauf les caches de géométrie.
- **La ville ne bouge pas** : `train.poser(ville)` n'écrit que `ville["train"]`, ne tire rien, et passe **avant**
  `frenesies_mod.poser` (qui doit rester le dernier, `test_les_frenesies_ne_deplacent_rien`), à la fin du bloc
  `if nord and plan == PLAN:` de `carte.generer` (`app/carte.py` ~7358). Sans la bande (`nord=False`), pas de clé
  `train`, et `train.js` ne fait rien.
- **La voie : rang 6 de la carte finie** (le rang libre sous le grand boulevard du haut, rangs 0-5), de l'ouest hors
  carte jusqu'au tunnel à `x = 419` (la falaise `C`, `ville["relief"]["montagnes"]["x"]`).
- **Le viaduc : tuiles 96 à 284**, rampes de 12 tuiles comprises (96-107 à l'ouest, 273-284 à l'est) ; le tablier haut
  de 108 à 272 enjambe les rues 113-116, les rues du Petit-Canton et 262-265.
- **Trois gares**, en tuiles : Les Friches `x = 50` (au sol), Petit-Canton `x = 236` (sur le viaduc), Gare centrale
  `x = 310` (au sol). En vague 1 le train **s'y arrête** (l'horaire est celui des vagues suivantes) ; les quais
  viennent en vague 2.
- **Hors d'un intérieur et hors d'un bloc** : tout ce que fait `train.js` se garde par `if (B.interieur || B.bloc)
  return` (dans le chalet, `Monde.carte` est le bloc).
- Tuile : `TT = 16` px ; le centre de la voie est à `y = 6 * 16 + 8 = 104` px.
- Tests : `UV_PROJECT_ENVIRONMENT=/Users/martingagne/dev/bandini/.venv uv run --frozen pytest -q <fichiers>` ; lint :
  `uv run ruff check .` ; tout fichier de test neuf a son entrée dans `docs/carte.md`
  (`scripts/verifier_carte_du_depot.py`).

#### Points à surveiller à la relecture

1. **Un char arrêté SUR le passage** (bouchon, feu) quand les barrières baissent : il doit être poussé, pas traversé
   — juge « char sur le passage » (tâche 5).
2. **Revenir d'un bloc ou d'un intérieur** : les piliers doivent redevenir solides (la carte de la ville est rebâtie
   ou remplacée) — juge « piliers après un bloc » (tâche 3).
3. **Une ville sans bande** (`nord=False`, ou une vieille carte sans clé `train`) : aucune erreur, aucune voie
   dessinée — juge « sans train » (tâche 2).
4. **Un saut dans le temps** (dormir à la planque, recharger) : barrières et train se relisent à l'heure, rien ne
   reste coincé fermé — juge « barrières à l'heure » (tâche 4).
5. **Une poursuite** : la police ne s'arrête pas au signal (comme au signaleur de chantier) — et le train la heurte
   comme les autres ; juge « la police passe » (tâche 4).

---

#### Tâche 1 : la clé `train` (Python)

**Fichiers :**
- Créer : `app/train.py`
- Modifier : `app/carte.py` (fin du bloc `if nord and plan == PLAN:`, ~7358, avant les frénésies)
- Modifier : `tests/test_definitions.py:175` (le plafond brut de la carte, avec sa note datée)
- Test : `tests/test_train.py` (et son entrée dans `docs/carte.md`)

**Interfaces :**
- Produit : `train.poser(ville) -> dict`, rangé dans `ville["train"]` :
  `{"rang": 6, "tunnel": 419, "viaduc": [96, 284], "rampe": 12, "piliers": [x, …], "passages": [[x0, x1], …],
  "gares": [["Les Friches", 50], ["Petit-Canton", 236], ["Gare centrale", 310]], "horaire": {…}}`, en tuiles.
  `horaire = {"vitesse": 4.5, "acceleration": 0.04, "arret": 600, "bout": 900, "longueur": 14, "annonce": 1100}`
  (px/image, px/image², images, images, tuiles, px).

- [ ] **Étape 1 : écrire les juges qui échouent** — `tests/test_train.py` :

```python
"""Le train : la clé `train` de la carte (docs/jalons/le-train.md)."""

import json

import pytest

from app import carte, train
from tests import villes


@pytest.fixture(scope="module")
def ville():
    return villes.generer()


def test_la_carte_a_son_train(ville):
    t = ville["train"]
    assert t["rang"] == 6 and t["tunnel"] == ville["relief"]["montagnes"]["x"] == 419
    assert t["viaduc"] == [96, 284] and [g[0] for g in t["gares"]] == ["Les Friches", "Petit-Canton", "Gare centrale"]


def test_les_passages_sont_les_rues_croisees_au_sol(ville):
    t, rang = ville["train"], ville["voie"][6]
    rues = []
    x = 0
    while x < t["tunnel"]:
        if rang[x] != ".":
            x0 = x
            while rang[x] != ".":
                x += 1
            if not (t["viaduc"][0] <= x0 <= t["viaduc"][1]):
                rues.append([x0, x - 1])
        else:
            x += 1
    assert t["passages"] == rues == [[1, 4], [353, 354], [414, 417]]


def test_sous_le_viaduc_les_rues_restent_ouvertes(ville):
    t = ville["train"]
    haut = range(t["viaduc"][0] + t["rampe"], t["viaduc"][1] - t["rampe"] + 1)
    assert len(t["piliers"]) >= 12
    for x in t["piliers"]:
        assert x in haut
        assert ville["voie"][6][x] == "." and ville["sol"][6][x] != ".", f"un pilier sur la rue ou le trottoir : {x}"
    # Chaque rue que le tablier enjambe garde toutes ses tuiles libres au rang 6.
    for x in haut:
        if ville["voie"][6][x] != ".":
            assert x not in t["piliers"]


def test_le_train_ne_deplace_rien(monkeypatch):
    avec = carte.generer()
    monkeypatch.setattr(train, "poser", lambda ville: None)
    sans = carte.generer()
    assert sans["train"] is None
    for cle in avec:
        if cle != "train":
            assert json.dumps(avec[cle], sort_keys=True) == json.dumps(sans[cle], sort_keys=True), cle


def test_poser_ne_tire_rien_et_redit_la_meme_chose(ville):
    import copy
    assert train.poser(copy.deepcopy(ville)) == train.poser(copy.deepcopy(ville)) == ville["train"]
    source = open(train.__file__, encoding="utf-8").read()
    assert "random" not in source and "Des" not in source and "graine" not in source


def test_sans_la_bande_pas_de_train():
    assert "train" not in villes.generer(nord=False)
```

- [ ] **Étape 2 : les voir échouer** — `… pytest -q tests/test_train.py` : attendu `ImportError` (`train`
  n'existe pas).

- [ ] **Étape 3 : `app/train.py`** :

```python
"""Le train : une ligne de passage au rang 6 de la bande nord — au sol, sur le viaduc, dans le tunnel.

Martin (28 sept. 2026) : « je veux un vrai train aérien, terrestre et tunnel » (docs/jalons/le-train.md).

⚠️ **Python ne pose rien, le navigateur roule** — comme le tramway : ce module lit la ville FINIE et rend la
géométrie de la ligne ; pas une tuile, pas un décor, pas un dé. La ville est la même avec et sans lui
(`test_le_train_ne_deplace_rien`). Il passe AVANT les frénésies, qui doivent rester les dernières.
"""

from __future__ import annotations

#: Le rang de la voie, dans la carte finie : libre d'un bout à l'autre de la bande, sous le grand boulevard.
RANG = 6
#: Le viaduc, en tuiles, rampes comprises : il monte dans les Friches, enjambe le Petit-Canton, redescend à la gare.
VIADUC = (96, 284)
RAMPE = 12
#: Un pilier toutes les tant de tuiles, sur le tablier haut ; jamais sur une rue ni sur un trottoir.
PAS_PILIERS = 8
GARES = (("Les Friches", 50), ("Petit-Canton", 236), ("Gare centrale", 310))
#: px/image, px/image², images d'arrêt en gare, images d'attente à chaque bout (hors carte), longueur en tuiles,
#: et à combien de px devant sa tête un passage à niveau se ferme.
HORAIRE = {"vitesse": 4.5, "acceleration": 0.04, "arret": 600, "bout": 900, "longueur": 14, "annonce": 1100}


def _libre(ville, x):
    """Une tuile où planter un pilier : ni rue, ni trottoir."""
    return ville["voie"][RANG][x] == "." and ville["sol"][RANG][x] != "."


def _piliers(ville):
    haut0, haut1 = VIADUC[0] + RAMPE, VIADUC[1] - RAMPE
    piliers, x = [], haut0
    while x <= haut1:
        pris = next((p for p in range(x, min(x + 4, haut1 + 1)) if _libre(ville, p)), None)
        if pris is not None:
            piliers.append(pris)
        x += PAS_PILIERS
    return piliers


def _passages(ville, tunnel):
    rang, passages, x = ville["voie"][RANG], [], 0
    while x < tunnel:
        if rang[x] == ".":
            x += 1
            continue
        x0 = x
        while rang[x] != ".":
            x += 1
        if not VIADUC[0] <= x0 <= VIADUC[1]:
            passages.append([x0, x - 1])
    return passages


def poser(ville):
    tunnel = ville["relief"]["montagnes"]["x"]
    return {
        "rang": RANG, "tunnel": tunnel, "viaduc": list(VIADUC), "rampe": RAMPE,
        "piliers": _piliers(ville), "passages": _passages(ville, tunnel),
        "gares": [list(g) for g in GARES], "horaire": dict(HORAIRE),
    }
```

Dans `app/carte.py`, à la fin du bloc `if nord and plan == PLAN:` (après la navette, avant les frénésies) :
`ville["train"] = train_mod.poser(ville)`, avec `from . import train as train_mod` parmi les imports du module.
Vérifier d'abord : `ville["relief"]["montagnes"]` est-il un dict `{"x": 419, …}` ? (`app/relief.py:63` rend
`{"montagnes": est}` — lire `est`.) Si la clé est ailleurs, corriger `poser` ET le juge.

- [ ] **Étape 4 : le paquet** — `test_definitions.py:175` : la carte était à 719 806 octets bruts (194 sous le
  plafond). Mesurer avec la clé, puis monter le plafond brut de 720 000 à la mesure arrondie au millier supérieur,
  **avec sa note datée** dans la docstring (avant/après, « la clé `train` : ~300 octets »). Le gzip ne doit pas
  passer 71 000.

- [ ] **Étape 5 : les juges verts, et ceux qui gardent la ville** — `… pytest -q tests/test_train.py
  tests/test_definitions.py tests/test_frenesies.py tests/test_nord.py tests/test_carte_du_depot.py` : tout vert.
  Rouge-avant du juge « ne déplace rien » : écrire un `T` dans `ville["sol"][6]` depuis `poser`, le voir rougir,
  retirer. `uv run ruff check .`

- [ ] **Étape 6 : commit** — `git add app/train.py app/carte.py tests/test_train.py tests/test_definitions.py
  docs/carte.md && git commit -m "feat: le train, vague 1 — la ligne (Python)"`.

---

#### Tâche 2 : l'horaire (`Train.etat`)

**Fichiers :**
- Créer : `static/js/train.js`
- Modifier : `templates/index.html` (le script, après `autobus.js` et `vehicules.js`, avant `hud.js` et `jeu.js`)
- Modifier : `static/js/jeu.js` (`pas('train', Train.maj)` dans la liste de `Jeu.maj`, juste après `Traversier`)
- Test : `tests/test_train_js.py` (et `docs/carte.md`)

**Interfaces :**
- Consomme : `B.defs.carte.train` (tâche 1), `Autobus.tempsDeLaPartie()`.
- Produit : `Train.donnees()` → `null` ou `{rang, tunnel, viaduc, rampe, piliers, passages, gares, horaire, yPx,
  trajets, periode}` ; `Train.etat(t)` → `{sens: 1|-1, tete: px, vitesse: px/image, gare: nom|null}` ou `null`
  (entre deux trajets, hors carte) ; `Train.etendue(e)` → `[gauche, droite]` en px ; `Train.maj()`.

- [ ] **Étape 1 : les juges qui échouent** — `tests/test_train_js.py` :

```python
"""Le train au banc (docs/jalons/le-train.md) : une heure, pas un dé."""

HEURE = """
function aLHeure(L, t) {                   // place la partie à t images depuis le premier matin
  const jour = L.B.defs.economie.jour_secondes * 60;
  L.B.partie.jour = 1 + Math.floor(t / jour);
  L.B.partie.heure = (t % jour) / jour;
}
"""


def test_le_train_est_une_heure(banc):
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        %s
        const d = L.Train.donnees(), vus = [];
        for (let t = 0; t < d.periode; t += 97) vus.push(JSON.stringify(L.Train.etat(t)));
        const encore = [];
        for (let t = 0; t < d.periode; t += 97) encore.push(JSON.stringify(L.Train.etat(t)));
        const plus = JSON.stringify(L.Train.etat(1234 + d.periode)) === JSON.stringify(L.Train.etat(1234));
        return { pareil: vus.join() === encore.join(), plus: plus, n: vus.filter(v => v !== 'null').length };
    }""" % HEURE)
    assert r["pareil"] and r["plus"] and r["n"] > 20


def test_il_s_arrete_a_ses_trois_gares_dans_les_deux_sens(banc):
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const d = L.Train.donnees(), arrets = [];
        for (let t = 0; t < d.periode; t += 30) {
          const e = L.Train.etat(t);
          if (e && e.gare && e.vitesse === 0) {
            const cle = e.sens + ' ' + e.gare;
            if (arrets.indexOf(cle) < 0) arrets.push(cle);
          }
        }
        return arrets;
    }""")
    assert r == ["1 Les Friches", "1 Petit-Canton", "1 Gare centrale",
                 "-1 Gare centrale", "-1 Petit-Canton", "-1 Les Friches"]


def test_le_train_ne_tire_pas_un_de(banc):
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        %s
        L.graine(5);
        const tirage = L.B.rng; let des = 0;
        L.B.rng = function () { if (String(new Error().stack).indexOf('train.js') >= 0) des++; return tirage(); };
        let vu = 0;
        for (let k = 0; k < 40; k++) {
          aLHeure(L, k * 311);
          o.frame(3);
          if (L.Train.etat(L.Autobus.tempsDeLaPartie())) vu++;
        }
        L.B.rng = tirage;
        return { des: des, vu: vu };
    }""" % HEURE)
    assert r["vu"] > 5 and r["des"] == 0


def test_sans_train_rien_ne_casse(banc):
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        delete L.B.defs.carte.train;
        o.frame(30);
        return { d: L.Train.donnees(), e: L.Train.etat(1000) };
    }""")
    assert r == {"d": None, "e": None}
```

- [ ] **Étape 2 : les voir échouer** — `L.Train` indéfini.

- [ ] **Étape 3 : le cœur de `static/js/train.js`** :

```js
/* Le train : une ligne de passage au rang 6 de la bande nord — au sol, sur le viaduc, dans le tunnel.
   Martin (28 sept. 2026) : « je veux un vrai train aérien, terrestre et tunnel » (docs/jalons/le-train.md).

   ⚠️ LE TRAIN EST UNE HEURE, comme la rame du métro : sa place ne dépend que de
   `Autobus.tempsDeLaPartie()` — rien à simuler, pas un dé, la même place au rechargement. Une seule voie,
   un seul train : il fait l'aller vers l'est (Friches → viaduc → gare centrale → tunnel), attend `bout`
   images sous la montagne, fait le retour, attend `bout` images hors carte à l'ouest. */
const Train = (function () {
  'use strict';
  const TT = 16;
  let cache = null, source = null;

  /** Distance couverte et vitesse, `t` images après le départ d'un arrêt, sur un tronçon de `d` px qui finit à
      l'arrêt : accélération `a` jusqu'à `v`, croisière, freinage — ou un triangle si le tronçon est court. */
  function profil(d, v, a, t) {
    const ta = v / a, da = v * ta / 2;
    if (2 * da >= d) {
      const tm = Math.sqrt(d / a);
      if (t <= tm) return { s: a * t * t / 2, v: a * t };
      const r = Math.max(0, 2 * tm - t);
      return { s: d - a * r * r / 2, v: a * r };
    }
    const tc = (d - 2 * da) / v, total = 2 * ta + tc;
    if (t <= ta) return { s: a * t * t / 2, v: a * t };
    if (t <= ta + tc) return { s: da + v * (t - ta), v: v };
    const r = Math.max(0, total - t);
    return { s: d - a * r * r / 2, v: a * r };
  }
  function dureeProfil(d, v, a) {
    const ta = v / a, da = v * ta / 2;
    return 2 * da >= d ? 2 * Math.sqrt(d / a) : 2 * ta + (d - 2 * da) / v;
  }

  /** Un trajet : les arrêts de la TÊTE, en px, dans l'ordre du sens. À l'est, la tête est le bout est du train :
      arrêté en gare, son milieu est sur la gare. Le départ et la fin sont hors carte (ou sous la montagne). */
  function trajet(t, sens) {
    const L = t.horaire.longueur, gares = t.gares.map(function (g) { return { nom: g[0], x: g[1] }; });
    const depart = { nom: null, px: -(L + 40) * TT }, fin = { nom: null, px: (t.tunnel + L + 45) * TT };
    let arrets = gares.map(function (g) { return { nom: g.nom, px: (g.x + 0.5 + L / 2) * TT }; });
    if (sens < 0) {
      arrets = gares.slice().reverse().map(function (g) { return { nom: g.nom, px: (g.x + 0.5 - L / 2) * TT }; });
      return [{ nom: null, px: fin.px - L * TT }].concat(arrets, [{ nom: null, px: depart.px }]);
    }
    return [depart].concat(arrets, [fin]);
  }

  function donnees() {
    const t = B.defs && B.defs.carte && B.defs.carte.train;
    if (!t) { cache = null; source = null; return null; }
    if (t === source) return cache;
    const h = t.horaire, trajets = [];
    let debut = 0;
    [1, -1].forEach(function (sens) {
      const pts = trajet(t, sens), troncons = [];
      for (let i = 0; i + 1 < pts.length; i++) {
        const d = Math.abs(pts[i + 1].px - pts[i].px), duree = dureeProfil(d, h.vitesse, h.acceleration);
        const arret = pts[i].nom ? h.arret : 0;     // on attend en gare AVANT de repartir
        troncons.push({ de: pts[i], vers: pts[i + 1], d: d, debut: debut, arret: arret, duree: duree });
        debut += arret + duree;
      }
      trajets.push({ sens: sens, troncons: troncons });
      debut += h.bout;
    });
    source = t;
    cache = Object.assign({}, t, { yPx: (t.rang + 0.5) * TT, trajets: trajets, periode: debut });
    return cache;
  }

  function etat(temps) {
    const d = donnees();
    if (!d) return null;
    const phase = ((temps % d.periode) + d.periode) % d.periode;
    for (const tr of d.trajets) {
      for (const c of tr.troncons) {
        if (phase < c.debut || phase >= c.debut + c.arret + c.duree) continue;
        if (phase < c.debut + c.arret) return { sens: tr.sens, tete: c.de.px, vitesse: 0, gare: c.de.nom };
        const p = profil(c.d, d.horaire.vitesse, d.horaire.acceleration, phase - c.debut - c.arret);
        return { sens: tr.sens, tete: c.de.px + tr.sens * p.s, vitesse: p.v, gare: null };
      }
    }
    return null;                                     // au bout, sous la montagne ou hors carte
  }

  /** Ce que le train couvre, en px, de gauche à droite. */
  function etendue(e) {
    const L = donnees().horaire.longueur * TT;
    return e.sens > 0 ? [e.tete - L, e.tete] : [e.tete, e.tete + L];
  }

  function enVille() { return !B.interieur && !B.bloc; }

  function maj() {
    if (!enVille() || !donnees()) return;
  }

  return { donnees: donnees, etat: etat, etendue: etendue, maj: maj, profil: profil };
})();
```

Enregistrer : la balise `<script>` dans `templates/index.html` (la liste est aussi celle du banc), et
`pas('train', Train.maj)` dans `Jeu.maj` après `Traversier`. Le juge des trois gares demande que l'arrêt en gare
remonte `vitesse: 0` et le nom : c'est la branche `phase < c.debut + c.arret`.

- [ ] **Étape 4 : les voir passer** — `… pytest -q tests/test_train_js.py`. Rouge-avant du juge « pas un dé » :
  mettre `B.rng()` dans `maj`, le voir rougir, retirer.

- [ ] **Étape 5 : commit** — `feat: le train, vague 1 — son horaire`.

---

#### Tâche 3 : la voie, le viaduc, le tunnel et le train, dessinés ; les piliers solides

**Fichiers :**
- Modifier : `static/js/train.js` (dessin, solidité), `static/js/jeu.js` (`rendre`), `static/js/entites.js`
  (`ajouterVisibles`, ~5478)
- Test : `tests/test_train_js.py`

**Interfaces :**
- Consomme : `Train.donnees/etat/etendue` (tâche 2).
- Produit : `Train.dessinerVoie(ctx, vue)` (au sol, avec `Autobus.dessinerRails`, `jeu.js` ~1233) ;
  `Train.ajouterVisibles(visibles, cx, cy)` (les voitures AU SOL, triées en y avec les gens) ;
  `Train.dessinerHaut(ctx, vue)` (le tablier, son ombre, les voitures sur le viaduc et les rampes, puis le portail
  du tunnel — après `Entites.dessinerParticules`, avant `Police.dessinerHelico`) ; `Train.surLeViaduc(xPx)` → bool
  (tablier haut ou rampe) ; `Train.auSol(xPx)` → bool (ni viaduc, ni tunnel).

- [ ] **Étape 1 : les juges qui échouent** — ajouter à `tests/test_train_js.py` :

```python
def test_les_piliers_sont_solides_et_la_rue_passe_dessous(banc):
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        o.frame(2);
        const d = L.Train.donnees(), M = L.Monde;
        const pilier = d.piliers.every(function (x) { return M.bloque(x, d.rang, M.MASQUE_PIETON); });
        const rue = [113, 114, 115, 116, 191, 192].every(function (x) { return !M.bloque(x, d.rang, M.MASQUE_VEHICULE); });
        const rampe = [97, 106, 274, 283].every(function (x) { return M.bloque(x, d.rang, M.MASQUE_PIETON); });
        return { pilier: pilier, rue: rue, rampe: rampe };
    }""")
    assert r == {"pilier": True, "rue": True, "rampe": True}


def test_les_piliers_reviennent_apres_une_piece(banc):
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        o.frame(2);
        const d = L.Train.donnees(), M = L.Monde, x = d.piliers[0];
        o.entrer(); o.fondu(); o.frame(2); o.sortir(); o.fondu(); o.frame(2);
        return M.bloque(x, d.rang, M.MASQUE_PIETON);
    }""")
    assert r is True
```

(Lire `tests/banc.js` : `o.entrer()`/`o.sortir()` et les noms exacts des masques exportés par `Monde` — `MASQUE_PIETON`
/ `MASQUE_VEHICULE`, `monde.js:18-32` ; s'ils ne sont pas exportés, les exporter.)

- [ ] **Étape 2 : les voir échouer.**

- [ ] **Étape 3 : la solidité** — dans `train.js`, comme `Fetes.maj` (`static/js/fetes.js:50-65`) : à chaque image
  en ville, si `Monde.carte` n'est plus celle qu'on a marquée, poser `solide = 1` sur chaque pilier et sur chaque
  tuile des deux rampes (le remblai), au rang `d.rang` ; retenir la carte marquée.

```js
  let marquee = null;
  function marquer() {
    const d = donnees(), c = Monde.carte;
    if (!d || !c || c === marquee) return;
    const poser = function (x) { c.solide[d.rang * c.w + x] = 1; };
    d.piliers.forEach(poser);
    for (let k = 0; k < d.rampe; k++) { poser(d.viaduc[0] + k); poser(d.viaduc[1] - k); }
    marquee = c;
  }
```

  `maj()` appelle `marquer()` après la garde `enVille()`. Vérifier que `Monde.carte`, `c.solide` et `c.w` sont bien
  les noms de `monde.js:222-235`.

- [ ] **Étape 4 : le dessin** —
  - `dessinerVoie` : sur chaque tuile visible du rang 6 **au sol** (hors `[viaduc0, viaduc1]`, `x < tunnel`) dont le
    glyphe n'est pas déjà `T`, les traverses et les deux rails comme `sprites.js:3387` (`'T'`) ; sur les tuiles des
    passages, des planches entre les rails (le bit 16 de `Monde.varianteDeRail`) ; les rampes : un remblai de pierre
    grise, plus clair en montant.
  - Les voitures : une locomotive (cabine, nez arrondi, phare) et `longueur / 3.5` voitures d'acier à fenêtres, 20 px
    de large, centrées sur `yPx` ; chaque voiture se dessine **au sol** par `ajouterVisibles` (objet `{id, vivant:
    true, x, y, peindreFoire(ctx)}`, comme `Foire.ajouterVisibles`) ou **en haut** par `dessinerHaut` si son milieu
    est sur le viaduc — levée de `z` (0 au pied de la rampe, 10 px sur le tablier), ombre au sol décalée vers le sud
    comme `Police.dessinerHelico` (`police.js:994-998`).
  - Le tablier : une dalle de béton de 24 px, garde-corps sombres des deux côtés, les rails dessus, l'ombre au sud ;
    les têtes de piliers visibles sous l'ombre.
  - Le portail : un arc de béton sur la falaise à `x = tunnel`, rang 5 à 7 ; **tout ce qui est à l'est de
    `tunnel * TT` n'est pas dessiné** (`ctx.save(); ctx.beginPath(); ctx.rect(…jusqu'à tunnel*TT…); ctx.clip()`),
    puis le portail par-dessus.
  - La nuit : un phare dans `lampes` (`jeu.js` ~1259-1273), comme `Cineparc.lampes`.

- [ ] **Étape 5 : les voir passer, puis LE REGARDER** — juges verts ; puis une capture Chromium de chaque niveau
  (le train au sol dans les Friches, sur le viaduc au-dessus de la rue principale 190-193, et à moitié dans le
  portail), par le script de capture (serveur werkzeug port 0, `Histoire.passerOuverture()`, `Hud.fermerMenu()`,
  `B.partie.jour/heure` pour placer le train, `Monde.centrerCamera`) ; les PNG dans `~/dev/bandini/captures/`, les
  lire, et les ouvrir pour Martin (`open`). Un juge vert ne voit pas un dessin raté.

- [ ] **Étape 6 : commit** — `feat: le train, vague 1 — on le voit passer`.

---

#### Tâche 4 : les passages à niveau

**Fichiers :**
- Modifier : `static/js/train.js`, `static/js/vehicules.js` (`obstacleDevant` ~2790, `attenteLegitime` ~2830)
- Test : `tests/test_train_js.py`

**Interfaces :**
- Produit : `Train.passageFerme(i, temps)` → bool (fonction de l'heure seule) ; `Train.signalDevant(v)` → distance
  en px jusqu'à la ligne d'arrêt, ou `Infinity`.

- [ ] **Étape 1 : les juges qui échouent** :

```python
ATTENTE = HEURE + """
function avantLePassage(L, i, avance) {    // t tel que le passage i se ferme dans `avance` images
  const d = L.Train.donnees();
  for (let t = 0; t < d.periode; t++) if (!L.Train.passageFerme(i, t) && L.Train.passageFerme(i, t + avance)) return t;
  return -1;
}
"""


def test_les_barrieres_se_relisent_a_l_heure(banc):
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        %s
        const t = avantLePassage(L, 1, 60), d = L.Train.donnees();
        return { t: t, avant: L.Train.passageFerme(1, t), apres: L.Train.passageFerme(1, t + 120),
                 loin: L.Train.passageFerme(1, t + Math.floor(d.periode / 2)) };
    }""" % ATTENTE)
    assert r["t"] >= 0 and r == {**r, "avant": False, "apres": True, "loin": False}


def test_un_char_attend_au_passage(banc):
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        %s
        const t0 = avantLePassage(L, 1, 90);
        aLHeure(L, t0);
        // un char du trafic qui monte (flèche '^') la rue 353-354, à six tuiles sous la voie
        const v = o.char('berline', (354 + 0.5) * L.TT, 12.5 * L.TT, -Math.PI / 2, { conducteur: 'trafic' });
        let plusHaut = 99;
        for (let k = 0; k < 300; k++) { o.frame(1); plusHaut = Math.min(plusHaut, v.y / L.TT); }
        return { plusHaut: plusHaut };
    }""" % ATTENTE)
    assert r["plusHaut"] > 7.0          # le nez n'a jamais franchi le rang 7


def test_la_police_en_poursuite_ne_s_arrete_pas(banc):
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        %s
        aLHeure(L, avantLePassage(L, 1, 60) + 90);          // le passage est fermé
        const v = o.char('berline', (354 + 0.5) * L.TT, 9.5 * L.TT, -Math.PI / 2, { conducteur: 'trafic' });
        v.sens = '^';
        const sage = L.Train.signalDevant(v);
        v.poursuite = true;
        const police = L.Train.signalDevant(v);
        return { sage: isFinite(sage), police: isFinite(police) };
    }""" % ATTENTE)
    assert r == {"sage": True, "police": False}    # le témoin : sans poursuite, le même char s'arrête
```

(Lire `o.char` dans `tests/banc.js` pour sa vraie signature, et `v.sens`/`Monde.fleche` : la flèche d'une tuile de
rue nord-sud est `'^'` ou `'v'`. `avantLePassage(L, 1, 60) + 90` = un instant où le passage est fermé.)

- [ ] **Étape 2 : les voir échouer.**

- [ ] **Étape 3 : `passageFerme` et `signalDevant`** :

```js
  /** Un passage est fermé quand le train le couvre, ou quand sa tête en est à moins de `annonce` px devant lui,
      ou que sa queue ne l'a pas dépassé d'une tuile. Fonction de l'heure seule : un saut dans le temps ne laisse
      jamais une barrière coincée. */
  function passageFerme(i, temps) {
    const d = donnees(), e = d && etat(temps);
    if (!e) return false;
    const p = d.passages[i], a = p[0] * TT, b = (p[1] + 1) * TT, ext = etendue(e);
    const g = e.sens > 0 ? ext[0] - TT : ext[0] - d.horaire.annonce;
    const dr = e.sens > 0 ? ext[1] + d.horaire.annonce : ext[1] + TT;
    return dr > a && g < b;
  }

  const PAS_RUE = { '^': -1, 'v': 1 };
  /** La distance d'un char jusqu'à sa ligne d'arrêt devant un passage FERMÉ, dans sa file. Jamais pour une rame
      ni pour une poursuite (comme le signaleur de chantier, `Chantiers.signalDevant`). */
  function signalDevant(v) {
    const d = donnees();
    if (!d || v.rails || v.poursuite || !enVille()) return Infinity;
    const pas = PAS_RUE[v.sens];
    if (!pas) return Infinity;
    const tx = Math.floor(v.x / TT), temps = Autobus.tempsDeLaPartie();
    for (let i = 0; i < d.passages.length; i++) {
      const p = d.passages[i];
      if (tx < p[0] || tx > p[1] || !passageFerme(i, temps)) continue;
      const ligne = pas < 0 ? (d.rang + 1) * TT + 4 : d.rang * TT - 4;
      const devant = (ligne - v.y) * pas - v.def.longueur / 2;
      if (devant >= -2 && devant < 6 * TT) return Math.max(0, devant);
    }
    return Infinity;
  }
```

  Dans `vehicules.js`, `obstacleDevant` : `const signal = Math.min(Chantiers.signalDevant(v), Train.signalDevant(v));`
  (le commentaire d'à côté le dit). Dans `attenteLegitime` : `if (Train.signalDevant(v) < Infinity) return true;` en
  tête — sinon le chien `debloquer` saute sur un char sage. **Rouge-avant** : retirer l'appel dans `obstacleDevant`,
  voir « un char attend » rougir.

- [ ] **Étape 4 : les barrières dessinées, et le char qui les défonce** — dans `dessinerVoie`, pour chaque passage :
  deux poteaux (un de chaque côté de la voie, sur le trottoir est et ouest de la rue), leurs feux rouges qui
  **alternent** toutes les 30 images quand c'est fermé, et le bras rayé rouge et blanc (comme `'levante'`,
  `monde.js:852-864`) qui s'abaisse en 45 images (l'angle se lit à l'heure : depuis combien d'images c'est fermé).
  Le joueur au volant qui passe une barrière baissée la **brise** : `brise[i] = numéro du passage du train`
  (`Math.floor(temps / periode)`), le bras dessiné cassé jusqu'au train suivant ; `Son.SFX.bris` s'il existe. Les
  gens passent dessous.

- [ ] **Étape 5 : verts** — `… pytest -q tests/test_train_js.py tests/test_vehicules_js.py tests/test_chantiers_js.py`
  (le trafic et le signaleur n'ont pas bougé).

- [ ] **Étape 6 : commit** — `feat: le train, vague 1 — les passages à niveau`.

---

#### Tâche 5 : il écrase, il klaxonne

**Fichiers :**
- Modifier : `static/js/train.js`
- Test : `tests/test_train_js.py`

**Interfaces :**
- Consomme : `Entites.autour(x, y, r, filtre)`, `Entites.blesser(e, degats, source, {renverse, angle, saigne})`,
  `Vehicules.endommager(v, degats, source)`, `B.defs.conduite.physique.feu_sous` (0,2), `Hud.message(txt, dur)`.
- Produit : `Train.heurter()` (appelé par `maj`), `Train.klaxonner()`.

- [ ] **Étape 1 : les juges qui échouent** :

```python
DEVANT = ATTENTE + """
function trainDevant(L, x, avance) {       // t où la tête arrive à x (px) dans `avance` images, vers l'est, au sol
  const d = L.Train.donnees();
  for (let t = 0; t < d.periode; t++) {
    const e = L.Train.etat(t + avance);
    if (e && e.sens > 0 && e.tete >= x && e.vitesse > 2) return t;
  }
  return -1;
}
"""


def test_un_char_sur_la_voie_est_pousse_et_prend_feu(banc):
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        %s
        const x = 330.5 * L.TT, y = L.Train.donnees().yPx;
        aLHeure(L, trainDevant(L, x, 60));
        const v = o.char('berline', x, y, 0, {});
        const vie = v.vie;
        for (let k = 0; k < 120; k++) o.frame(1);
        return { hors: Math.abs(v.y - y) > L.TT, vie: v.vie < vie * 0.2 || !v.vivant };
    }""" % DEVANT)
    assert r == {"hors": True, "vie": True}


def test_un_char_arrete_sur_le_passage_est_pousse(banc):
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        %s
        const x = 353.5 * L.TT, y = L.Train.donnees().yPx;
        aLHeure(L, trainDevant(L, x, 60));
        const v = o.char('berline', x, y, -Math.PI / 2, { conducteur: 'trafic' });
        for (let k = 0; k < 120; k++) o.frame(1);
        return Math.abs(v.y - y) > L.TT;
    }""" % DEVANT)
    assert r is True


def test_le_joueur_sur_la_voie_se_reveille_a_l_hopital(banc):
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        %s
        const x = 80.5 * L.TT, y = L.Train.donnees().yPx;   // loin de la gare des Friches : il roule vite
        aLHeure(L, trainDevant(L, x, 60));
        o.poser(x, y);
        let hopital = false;
        const avant = L.Missions.hopital;
        L.Missions.hopital = function () { hopital = true; return avant.apply(this, arguments); };
        for (let k = 0; k < 120; k++) o.frame(1);
        return hopital;
    }""" % DEVANT)
    assert r is True


def test_sous_le_viaduc_le_train_ne_touche_personne(banc):
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        %s
        const x = 191.5 * L.TT, y = L.Train.donnees().yPx;
        aLHeure(L, trainDevant(L, x, 60));
        o.poser(x, y);
        const vie = L.B.joueur.vie;
        for (let k = 0; k < 120; k++) o.frame(1);
        return L.B.joueur.vie === vie;
    }""" % DEVANT)
    assert r is True
```

(Le train s'arrête à la gare centrale, `x = 310` : le char à 330,5 est après la gare, là où le train repart — si
`vitesse > 2` n'est pas atteint à 330, prendre le premier `x` au sol où il l'est, entre 285 et 350, et le noter
dans le juge. Lire `o.poser`/`o.char` dans `tests/banc.js`.)

- [ ] **Étape 2 : les voir échouer.**

- [ ] **Étape 3 : `heurter` et `klaxonner`** :

```js
  const COOLDOWN_KLAXON = 180;
  let klaxonT = 0;
  function heurter() {
    const d = donnees(), temps = Autobus.tempsDeLaPartie(), e = etat(temps);
    if (!e || e.vitesse <= 0) return;
    const ext = etendue(e), feu = B.defs.conduite.physique.feu_sous;
    const cx = (ext[0] + ext[1]) / 2, demi = (ext[1] - ext[0]) / 2 + TT;
    for (const q of Entites.autour(cx, d.yPx, demi, function (q) {
      return q.vivant && (q.type === 'vehicule' || q.type === 'pieton' || (q.type === 'joueur' && !q.dansVehicule));
    })) {
      if (!auSol(q.x) || q.x < ext[0] || q.x > ext[1] || Math.abs(q.y - d.yPx) > TT) continue;
      const cote = q.y >= d.yPx ? 1 : -1;             // on le jette du côté où il est déjà
      if (q.type === 'vehicule') {
        q.conducteur = q.conducteur === B.joueur ? q.conducteur : null;   // un char du trafic ne se remet pas en voie
        q.y = d.yPx + cote * (TT + q.def.largeur / 2);
        q.vx = e.sens * e.vitesse * 0.6; q.vy = cote * e.vitesse * 0.8;
        const vite = e.vitesse > d.horaire.vitesse * 0.66;
        Vehicules.endommager(q, vite ? q.vie - q.vieMax * feu * 0.5 : q.vieMax * 0.3, TRAIN);
        B.cam.secousse = Math.max(B.cam.secousse || 0, 8);
      } else {
        if (q.type === 'joueur') Hud.message('FRAPPÉ PAR LE TRAIN', 180);
        Entites.blesser(q, 9999, TRAIN, { renverse: true, angle: e.sens > 0 ? 0 : Math.PI, saigne: 90 });
      }
    }
  }
  function klaxonner() {
    if (klaxonT > 0) { klaxonT--; return; }
    const d = donnees(), e = etat(Autobus.tempsDeLaPartie());
    if (!e || e.vitesse <= 0) return;
    const nez = e.tete, loin = nez + e.sens * 12 * TT;
    const devant = Entites.autour((nez + loin) / 2, d.yPx, 6 * TT + TT, function (q) {
      return q.vivant && (q.type === 'vehicule' || q.type === 'pieton' || q.type === 'joueur')
        && Math.abs(q.y - d.yPx) <= TT && (q.x - nez) * e.sens > 0 && auSol(q.x);
    });
    if (devant.length) { Son.SFX.klaxon_train(nez, d.yPx); klaxonT = COOLDOWN_KLAXON; }
  }
```

  `TRAIN` est un objet fixe `{ type: 'train', nom: 'le train' }` passé comme source : ni un meurtre ni un crime au
  compte du joueur (`Entites.tuer` ne crédite que `source === B.joueur`). `auSol(x)` : `x < viaduc0*TT || x >
  (viaduc1+1)*TT` et `x < tunnel*TT`. Vérifier `q.def.largeur`, `q.vieMax`, `B.cam.secousse` contre `vehicules.js`.
  `maj()` appelle `heurter()` puis `klaxonner()`.

- [ ] **Étape 4 : verts, rouge-avant** (retirer l'appel à `heurter`, voir les trois premiers juges rougir), ruff.

- [ ] **Étape 5 : commit** — `feat: le train, vague 1 — il écrase, il klaxonne`.

---

#### Tâche 6 : les sons

**Fichiers :**
- Modifier : `app/audio.py` (`CATALOGUE`, près de `cloche_tram` l.358), `static/js/son.js` (`SFX`), `static/js/train.js`
- Générer : `static/audio/…` par `scripts/audio_elevenlabs.py` (`elevenlabs_status` avant d'estimer)
- Test : `tests/test_train_js.py`

- [ ] **Étape 1 : le juge qui échoue** — les trois effets existent et se jouent **sans fichier** (la synthèse est le
  filet) :

```python
def test_les_sons_du_train_se_jouent_sans_fichier(banc):
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const S = L.Son.SFX;
        return ['klaxon_train', 'cloche_passage', 'roulement_train'].map(function (k) {
          try { S[k](100, 100, 1); return typeof S[k]; } catch (e) { return String(e); }
        });
    }""")
    assert r == ["function", "function", "function"]
```

- [ ] **Étape 2 : l'échec** (`S[k] is not a function`).

- [ ] **Étape 3 : les entrées du catalogue** :

```python
    _e("klaxon_train", "Klaxon du train", duree_s=2.5, volume=0.7, influence=0.6,
       prompt="Deep two-tone diesel locomotive air horn, long blast, North American freight train, outdoors"),
    _e("cloche_passage", "Cloche du passage à niveau", duree_s=3.0, volume=0.35, boucle=True,
       prompt="Railroad crossing warning bell ringing steadily, electronic ding ding, loopable, outdoors"),
    _e("roulement_train", "Roulement du train", duree_s=6.0, volume=0.55, boucle=True,
       prompt="Passenger train passing on steel rails, rhythmic wheel clatter over joints, diesel rumble, loopable"),
```

  Dans `son.js`, sur le modèle de `SFX.corne` (l.879) et de `tenir` (l.694) : `klaxon_train(x, y)` →
  `Son.jouerA('klaxon_train', x, y, 1400)` ou la synthèse (deux `ton` graves de 1,5 s, 311 et 370 Hz) ;
  `cloche_passage(x, y, actif)` et `roulement_train(x, y, volume)` → `tenir(slug, volume, repli)`, le volume par
  la distance au joueur. Dans `train.js`, chaque image : la cloche du passage fermé le plus proche du joueur
  (portée 500 px), le roulement par la distance au train le plus proche (portée 900 px), **divisé par deux** si le
  joueur est sous le viaduc et le train dessus, **coupé** quand le train est passé le tunnel.

- [ ] **Étape 4 : générer** — `elevenlabs_status`, puis `uv run python scripts/audio_elevenlabs.py --seulement
  klaxon_train,cloche_passage,roulement_train` (lire l'option exacte dans le script) ; écouter ; relancer le poids
  du paquet (`test_definitions`) et `test_audio*`.

- [ ] **Étape 5 : commit** — `feat: le train, vague 1 — son klaxon, sa cloche, son roulement`.

---

#### Tâche 7 : la grande carte, la doc, livrer

**Fichiers :**
- Modifier : `static/js/train.js` (`dessinerSurLaCarte`), `static/js/hud.js` (~3500, à côté de
  `Metro.dessinerSurLaCarte`), `docs/carte.md` (la ligne, la Gare de triage qui a retrouvé un train),
  `docs/architecture.md` (la carte du dépôt : `app/train.py`, `static/js/train.js`), cette fiche (« Notes »),
  `docs/plan.md` (la ligne : vague 1 livrée, le reste en cours)

- [ ] **Étape 1 : la carte** — `Train.dessinerSurLaCarte(ctx, pos)` : la voie en trait plein d'un pixel au sol,
  **doublée** (deux traits) sur le viaduc, **en pointillé** (`k += 3`, comme `metro.js:415`) de `tunnel` au bord
  est ; les trois gares en carrés 5×5 sombres à cœur bordeaux. Juge : `o.ctx.traces` après `Hud.dessinerCarte`
  contient des `fillRect` sur le rang de la voie (lire comment `test_metro_js.py` juge sa ligne sur la carte, s'il
  le fait, et faire pareil).

- [ ] **Étape 2 : les juges ciblés, le lint** — `… pytest -q tests/test_train.py tests/test_train_js.py
  tests/test_definitions.py tests/test_nord.py tests/test_frenesies.py tests/test_vehicules_js.py
  tests/test_chantiers_js.py tests/test_carte_du_depot.py tests/test_table_des_jalons.py` ; `uv run ruff check .`

- [ ] **Étape 3 : les captures** (sol, viaduc, portail, passage fermé avec un char qui attend, la grande carte) dans
  `~/dev/bandini/captures/`, lues, et ouvertes pour Martin.

- [ ] **Étape 4 : les notes et le plan** — sous « ## Notes » de cette fiche, ce qui a été livré et ses ⚠️ ; la
  ligne du plan dit « vague 1 livrée ; restent : on monte, on s'assoit ».

- [ ] **Étape 5 : commit et atterrir** — `feat: le train — il traverse la bande nord : au sol dans les Friches, sur
  son viaduc au-dessus du Petit-Canton, à la gare centrale, et dans son tunnel sous les montagnes ; les barrières
  baissent, et il n'arrête pour personne` ; atterrir par `git merge --ff-only` (ou cherry-pick sur le `dev` qui a
  bougé) — les juges ciblés verts suffisent pour atterrir, la suite complète après
  (atterrir avant la suite complète).

## Notes

✅ **Vague 1 livrée** (29 sept. 2026) — _le train passe_. Une rame bordeaux à bande jaune (une locomotive, trois
voitures d'acier) traverse la bande nord au **rang 6**, sous le grand boulevard : elle sort de l'ouest hors
carte, roule au sol dans les Friches, **monte sa rampe** et passe **sur le viaduc** au-dessus du Petit-Canton —
les chars et les gens circulent dessous, entre les piliers, dans l'ombre du tablier —, redescend à la Gare de
triage, et **entre dans le portail** de la falaise, à l'est. Une seule voie, un seul train : l'aller, puis le
retour. Il s'arrête dix secondes à ses trois gares (les Friches, Petit-Canton, Gare centrale — les quais sont
pour la vague 2). Trois **passages à niveau** (rues 1-4, 353-354, 414-417) : feux qui alternent, bras rayés qui
s'abaissent, cloche ; le trafic attend au bord de la voie, et le joueur au volant **défonce** la barrière. Ce qui
reste sur la voie est **poussé** (un char prend feu si le train roule vite) ou **tué** ; il klaxonne, il ne
freine jamais. La nuit, son phare. La grande carte trace la ligne : pleine au sol, doublée sur le viaduc,
pointillée sous la montagne.

- ⚠️ **Le train est une heure** (`Train.etat(t)`, `t = Autobus.tempsDeLaPartie()`) : pas un dé (juge par pile
  d'appels, rouge-avant prouvé), la même place au rechargement ; les barrières se relisent à l'heure — un saut
  dans le temps n'en laisse aucune coincée. Seul état d'image : une barrière défoncée (jusqu'au train suivant).
- ⚠️ **Python ne pose rien** (`app/train.py`) : la ville est la même avec et sans la clé `train`, clé par clé
  (rouge-avant : une tuile écrite par `poser`). Il passe avant les frénésies, qui restent les dernières. La carte :
  720 500 bruts / 70 449 gzip, sous 722 000 / 71 000 — pas de plafond à monter.
- ⚠️ **ON N'ATTEND JAMAIS SUR LA VOIE.** Deux passages sont à la bouche d'un carrefour du boulevard : la ligne
  d'arrêt de ce carrefour (la tuile `S`) tombe **sur les rails**, et un char qui attendait son tour attendait sur
  la voie — le train l'aurait pris à chaque passage. `Train.ligneHorsDeLaVoie` recule cette ligne d'une tuile
  (`cibleDeLaVoie`, `vehicules.js`) ; le signal du passage fermé s'arrête au même bord.
- ⚠️ **Les piliers et les rampes sont solides dans le navigateur** (`Train.maj` → `marquer`, comme le tronc du
  sapin), jamais dans la carte : une carte rebâtie est remarquée (juge : `Monde.charger`, rouge-avant prouvé).
- ⚠️ **Les sons du train sont un LIEU** (`audio.LIEUX["train"]`), chargés à 60 tuiles de la ligne : le budget du
  premier écran (2,5 Mo) n'avait plus que 6 Ko de marge, et le relever est une décision de Martin. Le klaxon, la
  cloche et le roulement ont leur synthèse en filet.
- ⚠️ Trois juges du plan **ne mordaient pas** : le char « qui attend » était hors de la bulle (la ville ne vit
  qu'autour du joueur — `presDe`), le joueur « sous le viaduc » se réveillait à l'hôpital la vie pleine (on guette
  maintenant les coups portés par le train), et la pièce où l'on entrait n'existait pas (on rebâtit la carte).
- ⚠️ **La relecture finale (un agent neuf) en a trouvé deux, et la correction deux autres.** (1) Le train lisait
  le CENTRE des chars : un autobus debout, le nez sur les rails, passait dessous intact — il lit maintenant leur
  étendue selon leur cap. (2) Un char qui avait passé la ligne reculée quand le STOP ou la boîte le retenait
  s'arrêtait sur place, sur les rails (« jamais derrière soi ») : un char **engagé** va au carrefour
  (`Train.engage`), et la ligne reculée se **guette une tuile plus tôt** (`ligneDevant`), comme une vraie ligne.
  (3) Ce qui frappe tient dans la **rangée des rails** (7 px de part et d'autre), pas dans les 20 px peints : à
  10 px, un char sage arrêté à sa ligne se faisait écraser (le juge des T du trafic l'a vu). (4) L'**impatience**
  du trafic forçait une barrière baissée après `patience_images` : devant elle, on klaxonne, on ne force pas.
  Huit mineurs restent notés dans le registre de la vague (conducteur vidé pour tout char frappé, l'enfant que le
  train traverse, la barrière cassée pour l'aller ET le retour…).
- ⚠️ **Peint comme les autres véhicules** (Martin, 29 sept. 2026 : « le visuel du train doit être comme les autres
  véhicules »). Les rectangles peints à la main sont partis : la locomotive et la voiture de passagers sont deux
  **machines en volume** (`SPRITES.locomotive`, `SPRITES.voiture_train`, bâties comme le tramway), et chaque voiture
  passe par le peintre des chars (`Vehicules.dessinerUn`) — même projection, même ombre, mêmes phares la nuit ; `z` la
  lève sur le viaduc. Les juges des machines (`test_poses_vehicules`) les jugent comme les autres : le pare-brise a
  son cadre, **une roue par bogie** (deux essieux faisaient quatre roues de profil — une machine vue d'en haut), les
  lampes débordent du coin comme celles de l'autobus. La voiture n'a ni phare ni feu, et le déclare (`sansLampes`) :
  le juge des lampes la laisse passer sur ce point seul. Sans le montant vertical de l'autobus, une rangée de
  fenêtres ne se peignait pas — l'aperçu agrandi l'a montré.
- ⚠️ **Les proportions d'un vrai train, et sa livrée** (Martin : « regarde sur le net pour que ça ressemble plus à
  un train », puis la livrée **B** sur une page à quatre choix). Une voiture de passagers fait 26 m sur 3,2 (la LRC de
  VIA : 25,91 × 3,19 — huit pour un) ; à 52 px sur 16, la nôtre avait la silhouette d'un autobus, et la rame en
  lisait trois à la queue leu leu. Les voitures font **80 px** : une bande de vitres d'un bout à l'autre, deux
  climatiseurs sur le toit arrondi, les portes près des bouts, les soufflets entre elles. La locomotive est une
  **F40PH** (17,12 × 3,23 m) : la cabine pleine largeur devant, et sur le toit, d'avant en arrière, le klaxon, le
  ventilateur du frein dynamique, la cheminée, puis les trois ventilateurs de radiateur. Le train passe de 14 à
  **19 tuiles** (`train.HORAIRE["longueur"]`). Livrée **bleu et jaune** — le train canadien qu'on reconnaît au premier
  coup d'œil, les couleurs seulement, ni nom ni logo ; écartées : bordeaux et jaune, argent à filets rouge et bleu,
  vert et crème. Sources : [LRC](https://en.wikipedia.org/wiki/LRC_(train)),
  [EMD F40PH](https://en.wikipedia.org/wiki/EMD_F40PH), [Rapido — F40PH Masterclass](https://rapidotrains.com/emd-f40ph-master-class/).
- 27 juges : `test_train.py` (7), `test_train_js.py` (20). Restent : **on monte** (vague 2), **on s'assoit**
  (vague 3).

