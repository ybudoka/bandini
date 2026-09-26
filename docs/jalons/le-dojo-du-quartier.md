# Le dojo du quartier : apprendre les techniques

← [le plan](../plan.md) · [les jalons livrés](README.md)

## Fiche

Demande de Martin (25 sept. 2026), deuxième des trois jalons des arts martiaux : le répertoire est
[livré](les-techniques-d-arts-martiaux.md#notes), [les Mantes](l-ecole-rivale.md#fiche) viendront après le
[Petit-Canton](le-quartier-chinois.md#fiche). Conçu avec Martin le 26 sept. 2026 (brainstorming : le Faubourg,
Mireille Dion, l'épreuve « au vrai, en rythme », un module à part).

_Ce que ça donne :_ au nord du Faubourg, le **DOJO DION**. Mireille Dion, ancienne danseuse contemporaine venue
à l'aïkido puis au jiu-jitsu, vend ses cours au comptoir ; on les passe sur le tatami, en rythme, contre Kevin,
l'élève partenaire. Réussi, le geste est à nous pour de bon. Au départ, Bandini n'a que les coups de rue.

- ⚠️ **Mesuré avant** : un bâtiment garanti (`SPECIAUX`, une majuscule du plan) déplace la ville ; une devanture
  ordinaire, non (`devantures.py` : elle se peint par-dessus des tuiles qui existent). Il n'existe pas de façon
  générique d'imposer une enseigne et une pièce à un commerce ordinaire ; le précédent est
  `poser_les_carrosseries` (`carte.py`), qui choisit une façade par mesure, sans dé, sur la ville finie. Et le
  cadre des épreuves d'adresse (`B.epreuve`, `adresse.js`) COUPE le combat (`Combat.majGestes`) et fait
  d'ESQUIVE « abandonner » — or la leçon a besoin du combat, et le balayage part d'une roulade (ESQUIVE) :
  la leçon a donc son propre module.

### Le dojo dans la ville

- **Où** : posé après coup, sans un dé, dans la même passe que `poser_les_carrosseries` (fin de `generer`,
  avant `devants.deplacer`) : parmi les façades de commerce du **Faubourg** assez larges pour la pièce, **la
  plus au nord** (du côté du futur Petit-Canton), à égalité la plus proche du milieu du district. On y réécrit
  l'enseigne, la porte (`interieur: "dojo"`) et le point de la carte. La ville d'avant reste identique à la
  tuile près, sauf cette façade.
- **L'enseigne** : `DOJO DION`, famille de devanture `savoir` ; famille de lieu `service` sur la carte (blip et
  légende viennent de là, comme tous les lieux).
- **La pièce** (`_PIECES`, dessinée à la main) : un **tatami** au centre (un sol à lui, `tatami`), le comptoir
  d'accueil (le point de Mireille), un vestiaire, un sac de frappe, un mannequin de bois, des photos de
  spectacles au mur ; la marque de Bandini et celle de Kevin sur le tatami.
- **« SALON MIREILLE »** (`devantures.COMMERCES["faubourg"]`) devient **« SALON LOUISE »** : deux Mireille dans
  le même quartier, on croirait que c'est son dojo.

### Mireille Dion

- **Le personnage** `mireille` (`missions.PERSONNAGES`) : dedans, au point `cours` ; sa fiche
  `docs/personnages/mireille.md` (histoire, personnalité, comment elle parle, comment elle se présente). Calme,
  précise, elle compte les temps et voit tout ce que ton corps fait de travers ; drôle par la situation —
  c'est Bandini qui détonne dans son dojo, pas elle. Elle se nomme **une fois**, dans sa salutation.
- **Sa voix** : une voix ElevenLabs à choisir (voir « Voix multilingues ElevenLabs » : non québécoise permise).
- **ACTION près d'elle** ouvre le menu **LES COURS** (comme Josée ouvre le marché noir, `Histoire.parler`).
- **Horaires** : le dojo ouvre de 8 h à 22 h ; la nuit, la porte est fermée, comme les autres comptoirs à
  heures (`magasins.HEURES_DES_COMPTOIRS`).

### Les cours

- **LES COURS** : les dix techniques non gratuites de `app/techniques.py`, rangées par style (entêtes BOXE,
  KARATÉ, JUDO, JIU-JITSU), au prix du catalogue. À droite de chaque ligne : le prix, **APPRIS**,
  **PAYÉ — À REPRENDRE**, ou **APRÈS L'UPPERCUT** (un maillon de la chaîne attend celui d'avant : le circulaire,
  rang 5, attend l'uppercut, rang 4).
- **Acheter** : `Missions.payer`, le cours noté payé (`B.partie.coursPayes[slug] = true`), et la leçon part
  tout de suite. **Rater** laisse le cours payé : on recommence **sans repayer**. Apprise, la technique s'écrit
  dans `B.partie.techniques` et le cours payé s'efface.

### La leçon sur le tatami : `static/js/dojo.js`

- **La séance** : `B.cours = { slug, temps, fenetre, reussis, rates, kevin }`. Un court fondu, et Bandini est
  sur sa marque, face à **Kevin** (l'élève partenaire, kimono blanc — une tenue de la garde-robe).
- **La mise en place, par technique** (une donnée de `app/techniques.py`, `lecon`) : au contact pour les coups
  et les prises ; Kevin **de dos** pour l'étranglement ; Kevin qui **arme un coup sur le temps** pour la parade ;
  Kevin **plus loin** pour le coup sauté (l'élan) ; Kevin qui **attaque** pour le balayage (on roule, puis on
  balaie).
- **Le rythme** : Mireille compte « un… deux… et… », un temps toutes les **0,75 s** (45 images) ; le « et »
  ouvre une **fenêtre d'environ 0,4 s** (24 images). Une technique tenue se charge sur le « deux » et se
  relâche sur le « et ».
- **La réussite** : `dojo.js` écoute le moteur des techniques (un crochet de `Techniques` : la technique qui
  **porte** — l'arc qui touche, la prise qui projette, l'étranglement qui couche) ; si c'est la technique
  enseignée, **sur Kevin**, dans la fenêtre : « OUI ! ». **Trois réussites** : apprise. **Cinq ratés** :
  « On reprendra » — le cours reste payé. Une technique posée hors de la fenêtre ne compte pas.
- **Pendant la leçon**, la technique enseignée compte comme sue (`Techniques.sait`) ; les autres restent
  utilisables, seule celle-là compte.
- **Kevin** (`partenaire: true`) : on le frappe et on le projette **sans sang, sans crime**, il ne fuit pas ;
  couché, il se relève en une seconde et reprend sa marque. Hors leçon, c'est un élève qui s'entraîne au sac.
- **Sortir par la porte**, ou **ABANDONNER** dans la pause : la leçon est annulée, le cours reste payé.
- **À l'écran** : en haut, « UPPERCUT · 2/3 » et trois points qui s'allument au rythme du compte ; la voix de
  Mireille dit le compte. **Apprise** : « TU SAIS L'UPPERCUT », et un mot de Mireille.

### Les voix

≈ 25 répliques en v3, avec leur `jeu=` (voir « Le jeu d'acteur des missions ») : sa salutation, l'annonce des
cours, « un », « deux », « et », une annonce par technique (dix), trois « oui », trois « raté », la réussite,
l'abandon, le dojo fermé. ≈ 2 000 caractères du forfait ; `elevenlabs_status` avant.

### Les juges

- **Python** : le dojo existe **dans le Faubourg**, une seule fois ; la ville d'avant identique à la tuile près
  sauf sa façade (les deux villes en JSON, clé par clé) ; la pièce donne quelque chose à faire (et ses points
  ne se marchent pas dessus) ; chaque technique non gratuite a sa `lecon` et son annonce ; plus de
  « SALON MIREILLE ».
- **Banc, au bouton** : un cours se paie une fois — raté, il se reprend gratuitement ; trois réussites en
  rythme apprennent la technique ; une technique hors fenêtre ne compte pas ; le circulaire se refuse sans
  l'uppercut ; Kevin se relève et ne fuit pas, et le frapper n'est pas un crime ; sortir annule la leçon ;
  la nuit, la porte est fermée ; aucun `B.rng()` consommé par la leçon.
- **Mutations** sur chaque règle ; **capture** de la pièce, de Mireille au comptoir, et d'une leçon en cours.

### Le plan d'exécution

Six tâches, chacune jouable et jugée. Mêmes contraintes que le répertoire : **worktree** du `dev` local,
pytest par `UV_PROJECT_ENVIRONMENT=/Users/martingagne/dev/bandini/.venv uv run --frozen pytest -q …`,
`git add` et `git commit` en deux commandes, WIP sous `refs/wip/dojo`, `ruff` avant d'atterrir, la suite par
le lanceur parallèle (Python, jamais une boucle zsh), **aucun `B.rng()`**, les juges **au bouton**, chaque juge
muté une fois.

⚠️ **Deux corrections de la fiche, lues dans le code** :
- **La nuit, c'est le menu qui ferme, pas la porte** : aucun comptoir du jeu ne ferme sa porte, tous disent
  « FERMÉ — OUVRE À 8 H » dans leur menu (`Missions.comptoirFerme`). Le dojo fait pareil.
- **Le dojo reprend la PIÈCE d'un commerce visitable**, pas une façade sans porte : une pièce a les mesures de
  sa part de bâtiment (`poser_la_piece`). On garde ces mesures et on redessine l'intérieur en dojo
  (`piece_de_dojo`), sans un dé — la façade, les murs et la ville ne bougent pas.

**À surveiller en relecture** :
1. **Aucune façade du Faubourg assez grande** (une autre graine, une ville qui change) : la génération ne
   plante pas, il n'y a simplement pas de dojo, et le menu des techniques reste à la triche — juge à la tâche 1.
2. **Une leçon interrompue** (la mort, l'arrestation, un appel, une mission qui démarre) : `B.cours` s'efface,
   Kevin reprend sa place au sac — juge à la tâche 4.
3. **Kevin frappé hors leçon** : c'est un élève, pas un passant — il ne fuit pas, n'appelle pas la police, se
   relève ; ni sang ni crime — juge à la tâche 4.
4. **Une sauvegarde d'avant le dojo** (`coursPayes` absent) : `Sauvegarde.completer` donne `{}` — juge à la
   tâche 3.
5. **Payer sans argent** : le cours ne se paie pas, rien ne démarre — juge à la tâche 3.

---

#### Tâche 1 : le dojo dans la ville

**Fichiers** — `app/carte.py` (trois glyphes, `piece_de_dojo`, `_Chantier.poser_le_dojo`, l'appel dans
`generer`, `QUI_DEDANS`), `app/devantures.py` (SALON LOUISE), `app/pietons.py` (l'archétype `eleve`),
`static/js/sprites.js` (trois peintres), `static/js/entites.js` (`archetypeDedans`), `tests/test_dojo.py`
(neuf), `tests/test_interieurs.py` (`TYPES_SERVIS` : `cours`).

**Produit** — `ville["interieurs"]["dojo"]` : une pièce avec un point `cours`, un élève `eleve`, et
`piece["tatami"] = {"x", "y"}` (le centre du tatami, en tuiles de la pièce) ; une porte `interieur: "dojo"`,
`lieu: "dojo"`, `nom: "DOJO DION"` ; un point de carte `{"type": "dojo", "famille": "service"}`.

- [x] **Les juges** — `tests/test_dojo.py` :

```python
"""Le dojo du quartier (docs/jalons/le-dojo-du-quartier.md)."""

import json

from app import carte, devantures


def test_un_seul_dojo_et_il_est_au_faubourg():
    ville = carte.generer()
    portes = [p for p in ville["portes"] if p.get("interieur") == "dojo"]
    assert len(portes) == 1, portes
    p = portes[0]
    assert p["nom"] == "DOJO DION"
    assert carte._Chantier(carte.PLAN, carte.GRAINE).district_en(p["x"], p["y"]) == "faubourg"
    piece = ville["interieurs"]["dojo"]
    assert [pt["type"] for pt in piece["points"]] == ["cours"]
    assert [g["qui"] for g in piece["gens"]] == ["eleve"]
    sol = "".join(piece["sol"])
    assert "Y" in sol and "K" in sol and "U" in sol


def test_le_dojo_ne_deplace_rien(monkeypatch):
    """La ville d'avant, identique : seules la porte, la devanture, la pièce et le point
    du dojo changent — et la pièce de commerce qu'il a reprise disparaît."""
    avec = carte.generer()
    monkeypatch.setattr(carte._Chantier, "poser_le_dojo", lambda self, ville: None)
    sans = carte.generer()
    for cle in avec:
        if cle in ("portes", "devantures", "interieurs", "points_interet"):
            continue
        assert json.dumps(avec[cle], sort_keys=True) == json.dumps(sans[cle], sort_keys=True), cle
    portes = [(a, b) for a, b in zip(avec["portes"], sans["portes"]) if a != b]
    assert len(portes) == 1 and portes[0][0]["interieur"] == "dojo", portes
    enseignes = [(a, b) for a, b in zip(avec["devantures"], sans["devantures"]) if a != b]
    assert len(enseignes) == 1 and enseignes[0][0]["texte"] == "DOJO DION", enseignes
    assert set(avec["interieurs"]) - set(sans["interieurs"]) == {"dojo"}
    reprise = set(sans["interieurs"]) - set(avec["interieurs"])
    assert reprise == {portes[0][1]["interieur"]}, reprise
    assert len(avec["points_interet"]) == len(sans["points_interet"]) + 1


def test_sans_facade_qui_convient_pas_de_dojo_et_rien_ne_plante(monkeypatch):
    """À surveiller no 1 : une ville où aucune pièce du Faubourg n'est assez grande."""
    monkeypatch.setattr(carte._Chantier, "DOJO_MESURES_MIN", (99, 99))
    ville = carte.generer()
    assert "dojo" not in ville["interieurs"]
    assert not [p for p in ville["portes"] if p.get("interieur") == "dojo"]


def test_plus_de_salon_mireille():
    assert all(nom != "SALON MIREILLE" for noms in devantures.COMMERCES.values() for nom, _ in noms)
```

⚠️ Avant d'écrire : `carte._Chantier(PLAN, GRAINE)` — vérifier que le constructeur ne bâtit pas la ville
(sinon lire le district par `DISTRICTS` et `rect_district` comme `test_districts.py`) ; `devantures.COMMERCES` :
vérifier la forme (`{district: [(nom, genre), …]}`) ; et que `generer()` n'est pas mis en cache (sinon le
`monkeypatch` ne change rien : le juge « ne déplace rien » passerait à vide — le muter pour le voir rougir).

- [x] **Rouge** : `KeyError: 'dojo'` / aucune porte.
- [x] **Le code** :
  - `LEGENDE` : `"Y": {"nom": "tatami", "dedans": True, "bloc": True}`, `"K": {"nom": "sac de frappe",
    "solide": 3, "meuble": True}`, `"U": {"nom": "mannequin de bois", "solide": 3, "meuble": True}` (les
    trois libres, vérifié le 26 sept.).
  - `piece_de_dojo` (après `piece_de_commerce`) :

```python
def piece_de_dojo(slug: str, largeur: int, hauteur: int, porte: int) -> dict:
    """Le DOJO DION aux mesures d'une part de batiment (docs/jalons/le-dojo-du-quartier.md).

    Le fond : les casiers du vestiaire, le sac de frappe a un bout, le mannequin de bois a
    l'autre. Le TATAMI au milieu. Le comptoir d'accueil (Mireille) a l'avant, du cote oppose
    a la porte, et la derniere rangee libre — on entre. ⚠️ Sans un de : les memes mesures
    donnent le meme dojo.
    """
    grille = [[" "] * largeur for _ in range(hauteur)]
    for x in range(largeur):
        grille[0][x] = "e"
    grille[0][0], grille[0][largeur - 1] = "K", "U"
    haut, bas = 2, hauteur - 4
    for y in range(haut, bas + 1):
        for x in range(1, largeur - 1):
            grille[y][x] = "Y"
    rangee, long_ = hauteur - 2, 3
    debut = 0 if porte > largeur / 2 else largeur - long_
    comptoir = [(x, rangee) for x in range(debut, debut + long_)]
    for x, y in comptoir:
        grille[y][x] = "c"
    points = [_poser_le_point(grille, "cours", None, porte, list(reversed(comptoir)))]
    pris: set[tuple[int, int]] = set()
    kevin = _quelqu_un(grille, "eleve", (1, 1), porte, pris)       # au sac, hors lecon
    piece = _piece(slug, "DOJO DION", _plan_de(grille, porte), sol="t",
                   points=tuple(points), gens=_gens(kevin))
    # Le centre du tatami, en tuiles de la piece (murs compris : +1).
    piece["tatami"] = {"x": largeur // 2 + 1, "y": (haut + bas) // 2 + 1}
    return piece
```

  - `_Chantier.poser_le_dojo(self, ville)` (à côté de `poser_les_carrosseries`), appelé dans `generer`
    **juste après** `chantier.poser_les_lots_et_les_rideaux(ville)` :

```python
    #: Le plus petit dojo : un tatami de trois rangees sur sept tuiles, et l'accueil.
    DOJO_MESURES_MIN = (9, 8)

    def poser_le_dojo(self, ville: dict) -> None:
        """LE DOJO DION : la piece d'un commerce visitable du Faubourg, redessinee en dojo.

        ⚠️ SUR LA VILLE FINIE ET SANS UN DE, comme les carrosseries : la facade, les murs
        et les mesures de la piece ne bougent pas ; on reprend l'interieur, l'enseigne et la
        porte. Le choix est une MESURE : la plus au nord du district (du cote du futur
        Petit-Canton), a egalite la plus proche de son milieu. Aucune qui convient : pas de
        dojo, et rien ne plante.
        """
        from . import chantiers as chantiers_mod
        enseigne = "DOJO DION"
        x0, y0, dl, _ = self.rect_district(next(d for d in DISTRICTS if d["slug"] == "faubourg"))
        cx = x0 + dl / 2
        interdites: set[tuple[int, int]] = set()
        for ch in ville.get("chantiers") or []:
            interdites |= set(chantiers_mod.tuiles(ch))
        feux = {(f["x"], f["y"]) for f in (ville.get("incendies") or {}).get("facades") or []}
        meilleure = None
        for porte in ville["portes"]:
            dedans = self.pieces.get(porte.get("interieur") or "")
            if not dedans or porte["interieur"].startswith("logement"):
                continue
            if self.district_en(porte["x"], porte["y"]) != "faubourg":
                continue
            largeur, hauteur = dedans["largeur"] - 2, dedans["hauteur"] - 2
            if largeur < self.DOJO_MESURES_MIN[0] or hauteur < self.DOJO_MESURES_MIN[1]:
                continue
            if any(max(abs(fx - porte["x"]), abs(fy - porte["y"])) <= 2 for fx, fy in feux):
                continue
            if any((porte["x"], porte["y"] - k) in interdites for k in range(0, hauteur + 1)):
                continue
            devanture = next((d for d in self.devantures if d["y"] == porte["y"]
                              and d["x"] <= porte["x"] < d["x"] + d["l"]), None)
            if not devanture or not devantures_mod.tient_en(enseigne, devanture["l"], TUILE_PX):
                continue
            cle = (porte["y"], abs(porte["x"] - cx), porte["x"])
            if meilleure is None or cle < meilleure[0]:
                meilleure = (cle, porte, devanture, dedans)
        if not meilleure:
            return
        _, porte, devanture, dedans = meilleure
        ancienne = porte["interieur"]
        self.pieces.pop(ancienne, None)
        ville["interieurs"].pop(ancienne, None)
        self.pieces["dojo"] = ville["interieurs"]["dojo"] = piece_de_dojo(
            "dojo", dedans["largeur"] - 2, dedans["hauteur"] - 2, dedans["sortie"]["x"])
        porte.update({"interieur": "dojo", "lieu": "dojo", "nom": enseigne})
        devanture["texte"] = enseigne
        devanture["genre"] = devantures_mod.genre_index("savoir")
        self.points.append({"type": "dojo", "slug": "dojo", "nom": enseigne,
                            "x": porte["x"], "y": porte["y"] + 1, "famille": "service"})
```

  ⚠️ Vérifier avant de coller : les noms `devantures_mod`, `TUILE_PX`, `chantiers_mod.tuiles`, les clés
  d'une porte (`lieu`, `nom`, `interieur`) et d'une pièce (`largeur`, `hauteur`, `sortie`) — lus dans
  `poser_les_carrosseries`, `poser_porte` et `_piece` ; et que `dedans["sortie"]["x"]` est bien la colonne
  de porte que `piece_de_commerce` a reçue (`porte`, comptée murs compris).
  - `QUI_DEDANS` : `"eleve"`. `pietons.py`, à côté du commis : `_p("eleve", "Élève", "#f4f1e8", "#2a1d12",
    "#e8b088", "#f4f1e8", vitesse=0.8, courage=0.0, vie=80, argent=(0, 5), temoin=0.0, metier="dojo",
    frequence=0.0)` — le kimono blanc, haut et bas.
  - `entites.js`, `archetypeDedans` : `if (g.qui === 'eleve') return archetype('eleve');`.
  - `devantures.py` : `("SALON MIREILLE", "service")` → `("SALON LOUISE", "service")`.
  - `sprites.js`, à côté de `'S'` : trois peintres. `'Y'` : le tatami (vert pâle `#a9b98a`, les joints plus
    sombres toutes les huit pixels, le liseré noir aux bords comme le galon du tapis `'y'`, lu par
    `v & 1..8`) ; `'K'` : le sac de frappe (la chaîne au plafond, le sac rouge sombre, son ombre) ; `'U'` :
    le mannequin de bois (le tronc brun, trois bras courts, le pied).
- [x] **Vert** : `tests/test_dojo.py`, puis `tests/test_interieurs.py`, `tests/test_devantures.py`,
  `tests/test_carte.py`, `tests/test_districts.py`, `tests/test_reproductible.py`, `tests/test_interieurs_js.py`.
- [x] **Capture** de la pièce (recette « Capturer une pièce du jeu ») — la regarder.
- [x] **Mutations** : retirer la garde des mesures → le juge « sans façade » rougit (une pièce trop petite devient un dojo, `_piece` lève) ; retirer `ville["interieurs"]
  .pop(ancienne…)` → le juge « ne déplace rien » rougit.
- [x] **Commit** : `feat: le dojo du quartier, 1re tâche — le DOJO DION dans la ville`.

#### Tâche 2 : Mireille Dion, et les règles de la leçon

**Fichiers** — `app/missions/__init__.py` (`PERSONNAGES`, `repliques_de_repos`), `app/visages.py`,
`app/garderobe.py` (sa tenue et son corps), `app/techniques.py` (le champ `lecon`), `app/dojo.py` (neuf),
`app/definitions.py`, `app/audio.py` (`voix_dojo`), `app/interpretation.py` (`JEU`), `docs/personnages/
mireille.md` (neuf) et `docs/personnages/README.md`, `tests/test_dojo.py`.

**Produit** — le personnage `mireille` (`ou: "point:cours"`) ; `B.defs.dojo = {heures, temps_images,
fenetre_images, reussites, rates_max, distances, repliques}` ; `t.lecon` sur chaque technique ; les voix
`mireille-dojo-<cle>` (mission `dojo`).

- [x] **Les juges** (dans `tests/test_dojo.py`) :

```python
from app import audio, dojo, missions, techniques


def test_mireille_tient_le_comptoir_du_dojo():
    m = missions.personnage("mireille")
    assert m and m["ou"] == "point:cours" and m["nom"] == "Mireille Dion"


def test_chaque_cours_a_sa_lecon_et_son_annonce():
    cles = {r["cle"] for r in dojo.REPLIQUES}
    for t in techniques.CATALOGUE:
        if t["gratuite"]:
            continue
        assert t["lecon"] in dojo.DISTANCES, t["slug"]
        assert f"annonce_{t['slug']}" in cles, t["slug"]


def test_mireille_ne_dit_pas_son_repos():
    """ACTION ouvre ses cours, toujours : un repos qu'on n'entend jamais ne se paie pas."""
    assert not [r for r in missions.repliques_de_repos() if r["qui"] == "mireille"]


def test_les_voix_du_dojo_sont_declarees():
    slugs = {v["slug"] for v in audio.toutes_les_voix()}
    assert {f"mireille-dojo-{r['cle']}" for r in dojo.REPLIQUES} <= slugs
```

- [x] **Rouge**, puis :
  - `techniques.py` : `_t(..., lecon="contact")`, le champ `lecon: str` ; `pied_saute` → `lecon="loin"`,
    `balayage` → `"attaque"`, `retournement_poignet` → `"arme"`, `etranglement` → `"dos"`.
  - `app/dojo.py` :

```python
"""Le dojo du quartier : les regles de la lecon et ce que Mireille dit
(docs/jalons/le-dojo-du-quartier.md). Python decide, `dojo.js` joue."""

from __future__ import annotations

from . import techniques

#: Le dojo ouvre de 8 h a 22 h (fractions du jour, comme `magasins.HEURES_DES_COMPTOIRS`).
HEURES = (8 / 24, 22 / 24)
#: « un… deux… et… » : un temps toutes les 45 images (0,75 s) ; le « et » ouvre 24 images.
TEMPS_IMAGES = 45
FENETRE_IMAGES = 24
REUSSITES = 3
RATES_MAX = 5
#: Ou Kevin se tient, en pixels devant Bandini, selon la mise en place de la technique.
DISTANCES = {"contact": 12, "dos": 11, "arme": 12, "loin": 70, "attaque": 40}

#: Ce que Mireille dit, par cle. Le slug de la voix est `mireille-dojo-<cle>`, le jeu
#: d'acteur est dans `interpretation.JEU` (`test_interpretation`).
REPLIQUES: list[dict] = [
    {"cle": "salut", "texte": "Bonjour. Mireille Dion. Enlève tes souliers, on compte jusqu'à trois ici."},
    {"cle": "cours", "texte": "Choisis. Je t'apprends le geste, le rythme, tu fournis la sueur."},
    {"cle": "un", "texte": "Un…"},
    {"cle": "deux", "texte": "Deux…"},
    {"cle": "et", "texte": "Et…"},
    {"cle": "oui_1", "texte": "Oui."},
    {"cle": "oui_2", "texte": "C'est ça."},
    {"cle": "oui_3", "texte": "Voilà. Encore."},
    {"cle": "rate_1", "texte": "Trop tôt."},
    {"cle": "rate_2", "texte": "Tu danses tout seul."},
    {"cle": "rate_3", "texte": "Écoute le compte."},
    {"cle": "appris", "texte": "Tu l'as. Garde-le propre."},
    {"cle": "reprendre", "texte": "On reprendra. C'est payé, reviens quand ton corps m'écoute."},
    {"cle": "abandon", "texte": "On arrête là. Salue le tatami en sortant."},
    {"cle": "ferme", "texte": "Le dojo dort. Reviens à huit heures."},
] + [{"cle": f"annonce_{t['slug']}", "texte": f"{t['nom']}. Regarde, puis fais-le avec moi."}
     for t in techniques.CATALOGUE if not t["gratuite"]]


def repliques() -> list[dict]:
    return [{"slug": f"mireille-dojo-{r['cle']}", "qui": "mireille", "texte": r["texte"],
             "mission": "dojo", "partie": "dojo", "telephone": False} for r in REPLIQUES]


def exporter() -> dict:
    return {"heures": list(HEURES), "temps_images": TEMPS_IMAGES, "fenetre_images": FENETRE_IMAGES,
            "reussites": REUSSITES, "rates_max": RATES_MAX, "distances": DISTANCES,
            "repliques": {r["cle"]: r["texte"] for r in REPLIQUES}}
```

  ⚠️ Les textes ci-dessus sont une PREMIÈRE PASSE : les relire contre `docs/ecrire-drole.md` et la fiche de
  Mireille avant de générer (tâche 5) — elle est drôle par la situation, calme, elle compte. La salutation la
  NOMME une fois (« Qui parle se nomme ») ; aucune autre réplique ne la nomme.
  - `definitions.py` : `"dojo": dojo.exporter()`. `audio.py` : `voix_dojo()` sur le modèle de `voix_repos()`
    (même clés, `volume: 0.9`, `histoire: True`), ajoutée à `toutes_les_voix()`.
  - `PERSONNAGES` : `{"slug": "mireille", "nom": "Mireille Dion", "genre": "femme", "voix": <la voix>,
    "couleurs": {"c": "#f4f1e8", "h": "#2a1d12", "s": "#e8c0a0", "p": "#1f1f2a"}, "ou": "point:cours",
    "heler": "Au tatami."}` — la voix : `uv run python scripts/audio_elevenlabs.py --libres`, une voix
    féminine française calme et libre (voir « Voix multilingues ElevenLabs » — non québécoise permise) ;
    la décision au registre.
  - `repliques_de_repos` : exclure `mireille` comme Josée (`p["slug"] != "mireille"`), commentaire à
    l'appui. `visages.py` : son visage (listes fermées ; une femme de cinquante ans, chignon, sourcils
    fins). `garderobe.py` : son corps (`femme`) et sa tenue (le gi noir d'enseignante : haut et bas sombres).
    `interpretation.JEU` : une ligne par `mireille-dojo-<cle>` (balises v3 : `[calmly]`, `[counting
    softly]`, `[dryly]`…).
  - `docs/personnages/mireille.md` (histoire : danseuse contemporaine, l'aïkido puis le jiu-jitsu, le dojo au
    Faubourg ; personnalité ; comment elle parle ; comment elle se présente ; sa voix ; ses liens — aucun
    encore) et sa ligne dans le `README.md` des personnages.
- [x] **Vert** : `tests/test_dojo.py`, `tests/test_visages.py`, `tests/test_garderobe.py`,
  `tests/test_missions.py`, `tests/test_interpretation.py`, `tests/test_audio.py`, `tests/test_techniques.py`,
  `tests/test_interieurs.py` (`TYPES_SERVIS` lit déjà les `point:` des personnages).
- [x] **Commit** : `feat: le dojo du quartier, 2e tâche — Mireille Dion, et les règles de la leçon`.

#### Tâche 3 : LES COURS au comptoir

**Fichiers** — `static/js/dojo.js` (neuf : `Dojo.menuCours`, `Dojo.etatDuCours`), `templates/index.html`
(le script, après `adresse.js`), `static/js/histoire.js` (`parler` : la branche de Mireille),
`static/js/base.js` (`coursPayes: {}`, et dans `completer`), `static/js/jeu.js` (`window.BANDINI.Dojo`),
`tests/test_dojo_js.py` (neuf).

**Produit** — `Dojo.etatDuCours(slug) → 'appris' | 'paye' | 'verrouille' | 'a_vendre'`, `Dojo.menuCours() →
menu`, `Dojo.acheter(slug) → bool` (appelle `Dojo.commencer(slug)`, tâche 4 ; en tâche 3, `commencer` est un
bouchon qui pose `B.cours = { slug }` seulement).

- [x] **Les juges** (`tests/test_dojo_js.py`) — une fonction commune qui entre au dojo :

```python
"""Le dojo du quartier, au banc (docs/jalons/le-dojo-du-quartier.md)."""

ENTRER = """
    function auDojo(L, o) {
        L.Jeu.commencer();
        const porte = L.Monde.carte.portes.find(function (p) { return p.interieur === 'dojo'; });
        L.B.joueur.x = porte.x * L.TT + 8; L.B.joueur.y = (porte.y + 1) * L.TT + 10;
        L.B.partie.heure = 0.5;                                   // midi : ouvert
        o.entrer(porte);
        const m = L.Entites.joueurs()[0];
        const mireille = L.B.entites.find(function (e) { return e.personnage === 'mireille'; });
        L.Entites.regarder(m, mireille.x - m.x, mireille.y - m.y);
        m.x = mireille.x; m.y = mireille.y + 14;
        L.Entites.indexer();
        return mireille;
    }
"""


def test_action_pres_de_mireille_ouvre_les_cours(banc):
    r = banc("""function (L, o) { """ + ENTRER + """
        auDojo(L, o);
        o.tape('KeyE', 2);
        return L.B.menu ? L.B.menu.titre : null;
    }""")
    assert r == "LES COURS"


def test_un_cours_se_paie_une_fois(banc):
    r = banc("""function (L, o) { """ + ENTRER + """
        auDojo(L, o);
        L.B.partie.argent = 1000;
        L.Dojo.acheter('uppercut');
        const apres = L.B.partie.argent;
        L.B.cours = null;                                         // la leçon ratée
        L.Dojo.acheter('uppercut');
        return { apres: apres, encore: L.B.partie.argent, etat: L.Dojo.etatDuCours('uppercut') };
    }""")
    assert r == {"apres": 700, "encore": 700, "etat": "paye"}, r


def test_sans_argent_rien_ne_commence(banc):
    """À surveiller no 5."""
    r = banc("""function (L, o) { """ + ENTRER + """
        auDojo(L, o);
        L.B.partie.argent = 10;
        const ok = L.Dojo.acheter('uppercut');
        return { ok: ok, cours: L.B.cours || null, etat: L.Dojo.etatDuCours('uppercut') };
    }""")
    assert r == {"ok": False, "cours": None, "etat": "a_vendre"}, r


def test_le_circulaire_attend_l_uppercut(banc):
    r = banc("""function (L, o) { """ + ENTRER + """
        auDojo(L, o);
        L.B.partie.argent = 5000;
        return { avant: L.Dojo.etatDuCours('pied_circulaire'), achat: L.Dojo.acheter('pied_circulaire') };
    }""")
    assert r == {"avant": "verrouille", "achat": False}, r


def test_la_nuit_le_menu_est_ferme(banc):
    r = banc("""function (L, o) { """ + ENTRER + """
        auDojo(L, o);
        L.B.partie.heure = 23 / 24;
        const m = L.Dojo.menuCours();
        return m.items.filter(function (i) { return i.actif !== false && !i.entete; }).length;
    }""")
    assert r == 0


def test_une_vieille_partie_a_ses_cours_vides(banc):
    """À surveiller no 4."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const p = JSON.parse(JSON.stringify(L.B.partie)); delete p.coursPayes;
        return L.Sauvegarde.completer(p, L.B.defs).coursPayes;
    }""")
    assert r == {}
```

⚠️ Vérifier : le prix de l'uppercut (300 $, `techniques.py`) ; que `o.entrer(porte)` existe dans le banc
(`tests/banc.js`, `entrer`) ; le champ qui nomme le personnage d'une entité (`e.personnage` ? lire
`Histoire.creerPersonnage`) ; la touche d'ACTION (`KeyE`).

- [x] **Rouge**, puis `dojo.js` (le menu) — le patron de `Missions.menuMarcheNoir` :

```js
/* Bandini — le dojo du quartier : LES COURS de Mireille Dion, et la lecon sur le
   tatami (docs/jalons/le-dojo-du-quartier.md). Python decide (`app/dojo.py`,
   `app/techniques.py`), ce module joue. ⚠️ Aucun `B.rng()` ici. */

const Dojo = (function () {
  'use strict';

  const STYLES = [['boxe', 'BOXE'], ['karate', 'KARATÉ'], ['judo', 'JUDO'], ['jiujitsu', 'JIU-JITSU']];

  function regles() { return B.defs.dojo; }

  /** Le maillon d'avant, pour une tape de la chaine (le circulaire attend l'uppercut). */
  function avant(t) {
    if (t.geste !== 'tape' || t.rang <= 1) return null;
    return (B.defs.techniques || []).find(function (q) { return q.geste === 'tape' && q.rang === t.rang - 1; }) || null;
  }

  function etatDuCours(slug) {
    const p = B.partie, t = Techniques.def(slug);
    if (p.techniques && p.techniques[slug]) return 'appris';
    if (p.coursPayes && p.coursPayes[slug]) return 'paye';
    const a = avant(t);
    if (a && !Techniques.sait(B.joueur, a.slug)) return 'verrouille';
    return 'a_vendre';
  }

  function ferme() { return !Missions.ouvert({ heures: regles().heures }); }

  /** Payer (une fois) et commencer. Rend true si la lecon part. */
  function acheter(slug) {
    const etat = etatDuCours(slug), t = Techniques.def(slug);
    if (ferme() || etat === 'appris' || etat === 'verrouille') return false;
    if (etat === 'a_vendre') {
      if (!Missions.payer(t.prix, t.nom.toUpperCase())) return false;
      B.partie.coursPayes[slug] = true;
    }
    return commencer(slug);
  }

  function menuCours() {
    const items = [];
    if (ferme()) {
      items.push({ libelle: 'FERMÉ — OUVRE À ' + Math.round(regles().heures[0] * 24) + ' H', actif: false });
      return { titre: 'LES COURS', sur: B.partie.argent + ' $', items: items };
    }
    for (const [style, titre] of STYLES) {
      items.push({ entete: titre });
      for (const t of B.defs.techniques.filter(function (q) { return q.style === style; })) {
        const etat = etatDuCours(t.slug), a = avant(t);
        const detail = { appris: 'APPRIS', paye: 'PAYÉ — À REPRENDRE',
                         verrouille: 'APRÈS ' + (a ? a.nom.toUpperCase() : ''), a_vendre: t.prix + ' $' }[etat];
        items.push({ libelle: t.nom.toUpperCase(), detail: detail,
                     actif: etat === 'a_vendre' || etat === 'paye',
                     faire: function () { return acheter(t.slug); } });
      }
    }
    return { titre: 'LES COURS', sur: B.partie.argent + ' $', items: items };
  }

  // La lecon elle-meme : tache 4. Ici, un bouchon.
  function commencer(slug) { B.cours = { slug: slug }; return true; }

  return { menuCours, etatDuCours, acheter, commencer };
})();
```

  ⚠️ Vérifier la signature de `Missions.payer` (elle rend-elle un booléen ? son `raison`) et la forme d'un
  `entete` (`{ entete: 'BOXE' }` ou `{ libelle: 'BOXE', entete: true }` — lire `Hud.entete`, utilisé dans
  `menuDebug`). Et `faire` qui rend `true` ferme le menu : une leçon qui part DOIT le fermer.
  - `histoire.js`, dans `parler`, juste avant la branche de Josée : `if (slug === 'mireille') {
    Hud.ouvrirMenu(Dojo.menuCours()); return true; }` (la salutation la première fois — tâche 5).
  - `base.js` : `coursPayes: {}` dans l'état initial, `'coursPayes'` dans la liste de `completer`.
- [x] **Vert**, **mutations** (retirer le `if (etat === 'a_vendre')` → le juge « se paie une fois »
  rougit ; `avant()` qui rend toujours null → le circulaire rougit).
- [x] **Commit** : `feat: le dojo du quartier, 3e tâche — LES COURS au comptoir`.

#### Tâche 4 : la leçon sur le tatami

**Fichiers** — `static/js/dojo.js` (la leçon), `static/js/techniques.js` (le crochet `quandPorte`, et `sait`
qui lit `B.cours`), `static/js/entites.js` (`blesser` : le partenaire ; `majPieton` : Kevin), `static/js/jeu.js`
(`pas('dojo', Dojo.maj)` après `combat` ; la sortie annule), `static/js/hud.js` (le compteur en haut ;
ABANDONNER LA LEÇON dans la pause), `tests/test_dojo_js.py`.

**Consomme** — `B.defs.dojo` (tâche 2), `Dojo.acheter`/`etatDuCours` (tâche 3), `Techniques.demarrer/def`.

**Produit** — `B.cours = { slug, t, reussis, rates, kevin, compte, fenetre, vu }` ; `Dojo.commencer(slug)`,
`Dojo.maj()`, `Dojo.annuler(raison)`, `Dojo.dessiner(ctx)` ; `Techniques.quandPorte = function (e, slug, cible)`
(appelé par le moteur, voir plus bas).

- [x] **Les juges** :

```python
def test_trois_reussites_en_rythme_apprennent_l_uppercut(banc):
    """On tape sur le « et » : trois fois. Le moteur fait la chaîne (direct, droit, crochet
    avant l'uppercut) — la leçon, elle, pose l'uppercut comme prochain maillon."""
    r = banc("""function (L, o) { """ + ENTRER + """
        auDojo(L, o);
        L.B.partie.argent = 1000;
        L.Dojo.acheter('uppercut');
        for (let n = 0; n < 600 && L.B.cours; n++) {
            if (L.B.cours.fenetre && !L.B.cours.tape) { L.B.cours.tape = true; o.tape('KeyX', 1); }
            o.frame(1);
        }
        return { appris: !!L.B.partie.techniques.uppercut, paye: !!L.B.partie.coursPayes.uppercut };
    }""")
    assert r == {"appris": True, "paye": False}, r


def test_hors_de_la_fenetre_ca_ne_compte_pas(banc):
    r = banc("""function (L, o) { """ + ENTRER + """
        auDojo(L, o);
        L.B.partie.argent = 1000;
        L.Dojo.acheter('uppercut');
        let reussis = 0;
        for (let n = 0; n < 400 && L.B.cours; n++) {
            if (L.B.cours && !L.B.cours.fenetre && L.B.cours.t % 45 === 5) o.tape('KeyX', 1);
            o.frame(1);
            if (L.B.cours) reussis = L.B.cours.reussis;
        }
        return { appris: !!L.B.partie.techniques.uppercut, reussis: reussis };
    }""")
    assert r["appris"] is False and r["reussis"] == 0, r


def test_kevin_se_releve_ne_fuit_pas_et_n_est_pas_un_crime(banc):
    """À surveiller no 3 : hors leçon aussi."""
    r = banc("""function (L, o) { """ + ENTRER + """
        auDojo(L, o);
        const kevin = L.B.entites.find(function (e) { return e.partenaire; });
        const crimes = L.B.crimes.length;
        L.Entites.blesser(kevin, 999, L.B.joueur, { renverse: true });
        const ko = kevin.etat;
        o.frame(90);
        return { ko: ko, etat: kevin.etat, vivant: kevin.vivant, crimes: L.B.crimes.length - crimes,
                 fuit: kevin.etat === 'fuit' };
    }""")
    assert r["vivant"] and r["etat"] != "assomme" and not r["fuit"] and r["crimes"] == 0, r


def test_sortir_annule_la_lecon_et_garde_le_cours(banc):
    r = banc("""function (L, o) { """ + ENTRER + """
        auDojo(L, o);
        L.B.partie.argent = 1000;
        L.Dojo.acheter('uppercut');
        o.frame(30);
        o.sortir();
        return { cours: L.B.cours || null, paye: !!L.B.partie.coursPayes.uppercut };
    }""")
    assert r == {"cours": None, "paye": True}, r


def test_une_lecon_interrompue_se_defait(banc):
    """À surveiller no 2 : la mort (l'hôpital) coupe la leçon."""
    r = banc("""function (L, o) { """ + ENTRER + """
        auDojo(L, o);
        L.B.partie.argent = 1000;
        L.Dojo.acheter('uppercut');
        o.frame(20);
        L.Missions.hopital(null); o.frame(240);
        return L.B.cours || null;
    }""")
    assert r is None


def test_la_lecon_ne_tire_aucun_de(banc):
    r = banc("""function (L, o) { """ + ENTRER + """
        auDojo(L, o);
        L.B.partie.argent = 1000;
        let tires = 0; const rng = L.B.rng; L.B.rng = function () { tires++; return rng(); };
        L.Dojo.acheter('uppercut');
        const avant = tires;
        for (let n = 0; n < 120; n++) L.Dojo.maj();
        return tires - avant;
    }""")
    assert r == 0
```

⚠️ `Dojo.maj()` appelé seul (sans `o.frame`) : le dernier juge mesure la leçon, pas la ville. Et la chaîne :
une leçon d'**uppercut** doit faire partir l'uppercut à la tape, pas le direct — la leçon règle
`B.joueur.chaine = rang - 1` et `chaineT = FENETRE` avant chaque « et » (la mise en place des tapes).

- [x] **Rouge**, puis le code :
  - `techniques.js` :
    - `sait(e, slug)` : `if (Entites.estJoueur(e) && B.cours && B.cours.slug === slug) return true;` en tête.
    - le **crochet** `api.quandPorte = null` et un appel `if (api.quandPorte) api.quandPorte(e, slug, cible)`
      aux trois endroits où une technique PORTE : (1) dans `maj`, après `Combat.arcDeMelee`, pour chaque
      cible nouvellement ajoutée à `e.touches` (comparer la longueur avant/après ; retrouver l'entité par
      son `id`) ; (2) dans `majVols`, à l'atterrissage (`v.auteur`, `v.tech`, `c`) ; (3) dans `majPrise`,
      quand l'étranglement couche (`j`, `'etranglement'`, `c`) — et dans `surActif` pour `genoux_prise`.
  - `entites.js`, `blesser`, en tête après les gardes : `if (e.partenaire) { e.recul = 22; e.vx = …; e.vy
    = …; if (opts.renverse || degats >= e.vie) { e.etat = 'couche_dojo'; e.minuterie = 60; } return true; }`
    — aucun dégât, aucun sang, aucun cri, aucune alerte ; `majPieton` : `if (e.partenaire) { majKevin(e);
    return; }` (se relève au bout de `minuterie`, revient à sa marque `e.marque`, reste face au joueur
    pendant la leçon, au sac sinon).
    ⚠️ `couche_dojo` doit se DESSINER couché : lire comment `assomme` se peint (`face = 'couche'`) et faire
    pareil, puis rendre la face au relever.
  - `dojo.js`, la leçon :

```js
  //: La lecon : `B.cours`. ⚠️ Elle ne SURVIT a rien : une porte, la mort, un appel, une
  //: mission qui part — `Dojo.maj` la defait des que le joueur n'est plus au dojo.
  function commencer(slug) {
    const piece = B.interieur;
    if (!piece || piece.slug !== 'dojo') return false;
    const kevin = B.entites.find(function (e) { return e.partenaire && e.vivant; });
    if (!kevin) return false;
    Jeu.transiter([10, 10], function () {
      const t = Techniques.def(slug), d = regles().distances[t.lecon];
      const cx = piece.tatami.x * TT + 8, cy = piece.tatami.y * TT + 8;
      const j = B.joueur;
      j.x = cx - d / 2; j.y = cy; j.vx = 0; j.vy = 0; Entites.regarder(j, 1, 0);
      kevin.x = cx + d / 2; kevin.y = cy; kevin.marque = { x: kevin.x, y: kevin.y };
      Entites.regarder(kevin, t.lecon === 'dos' ? 1 : -1, 0);
      Entites.indexer();
    }, Techniques.def(slug).nom.toUpperCase());
    B.cours = { slug: slug, t: 0, reussis: 0, rates: 0, kevin: kevin, fenetre: false, tape: false, vu: false };
    Techniques.quandPorte = quandPorte;
    dire('annonce_' + slug);
    return true;
  }

  function quandPorte(e, slug, cible) {
    const c = B.cours;
    if (!c || e !== B.joueur || cible !== c.kevin || slug !== c.slug) return;
    if (!c.fenetre || c.vu) return;
    c.vu = true;
  }

  function maj() {
    const c = B.cours;
    if (!c) return;
    if (!B.interieur || B.interieur.slug !== 'dojo' || !B.joueur.vivant || B.cinema) { annuler(null); return; }
    if (B.transition) return;
    const r = regles(), phase = c.t % r.temps_images, temps = Math.floor(c.t / r.temps_images) % 3;
    if (phase === 0) dire(['un', 'deux', 'et'][temps]);
    const ouverte = temps === 2 && phase < r.fenetre_images;
    if (ouverte && !c.fenetre) {
      c.fenetre = true; c.vu = false; c.tape = false;
      miseEnPlace(c);
    } else if (!ouverte && c.fenetre) {
      c.fenetre = false;
      if (c.vu) { c.reussis++; dire('oui_' + ((c.reussis - 1) % 3 + 1)); }
      else { c.rates++; dire('rate_' + ((c.rates - 1) % 3 + 1)); }
      if (c.reussis >= r.reussites) { apprendre(c.slug); return; }
      if (c.rates >= r.rates_max) { annuler('reprendre'); return; }
    }
    c.t++;
  }
```

    et `miseEnPlace(c)` (avant chaque « et ») : Kevin revient à sa marque ; pour une tape, la chaîne du
    joueur au maillon d'avant (`chaine = rang - 1`, `chaineT = Techniques.FENETRE`) ; pour `arme`, Kevin
    arme un coup (`Combat.frapper(kevin, false)` — ⚠️ un coup de Kevin ne blesse pas : `blesser` refuse une
    `source.partenaire` sur le joueur) ; pour `attaque`, Kevin passe `etat = 'attaque_joueur'` le temps du
    temps (la roulade a sa menace) ; pour `dos`, Kevin tourne le dos. `apprendre(slug)` : `B.partie.
    techniques[slug] = true`, `delete coursPayes[slug]`, `Hud.message('TU SAIS ' + nom + ' !')`, `dire
    ('appris')`, puis `finir()`. `annuler(cle)` : `dire(cle)` si cle, `finir()`. `finir()` : `B.cours = null`,
    `Techniques.quandPorte = null`, Kevin retourne au sac. `dire(cle)` : `Son.Voix.chargerHistoire('dojo')`,
    `Son.Voix.parler('mireille-dojo-' + cle)` ; sans mp3, `Entites.bulle(mireille, texte)` — le filet.
  - `jeu.js` : `pas('dojo', Dojo.maj)` juste après `pas('combat', …)` ; `Dojo` dans `window.BANDINI`.
  - `hud.js` : `Dojo.dessiner(ctx)` à côté d'`Adresse.dessiner(ctx)` — en haut, « UPPERCUT · 2/3 » et
    trois points (un par temps, le troisième doré pendant la fenêtre) ; dans `menuPause`, avant QUITTER :
    `B.cours ? { libelle: 'ABANDONNER LA LEÇON', faire: function () { Dojo.annuler('abandon'); Jeu.reprendre();
    return true; } } : null` (filtrer les `null`).
- [x] **Vert** : `tests/test_dojo_js.py`, puis `tests/test_techniques_js.py`, `tests/test_armes_js.py`,
  `tests/test_bagarre_js.py`, `tests/test_interieurs_js.py`, `tests/test_classeur_js.py`.
- [x] **Mutations** : `c.vu = true` sans vérifier `c.fenetre` → « hors fenêtre » rougit ; `sait` sans
  `B.cours` → « trois réussites » rougit ; retirer la garde `e.partenaire` de `blesser` → Kevin rougit.
- [x] **Capture** d'une leçon en cours (le compteur, Kevin, le tatami) — la regarder.
- [x] **Commit** : `feat: le dojo du quartier, 4e tâche — la leçon sur le tatami`.

#### Tâche 5 : la voix de Mireille

- [x] Relire les répliques (`app/dojo.py`) contre `docs/ecrire-drole.md` et la fiche de Mireille ; le jeu
  (`interpretation.JEU`) contre `docs/jeu-d-acteur.md`.
- [x] `elevenlabs_status`, puis `uv run python scripts/audio_elevenlabs.py --voix --essai` : il doit lister
  les `mireille-dojo-*` (≈ 25) et **rien d'autre** — sinon, filtrer (lire les options du script ; ne pas
  générer les voix des autres sessions).
- [x] Générer ; `tests/test_audio.py` vert ; les voix au dépôt (le plafond du dépôt : « Voix des missions
  longues »). ⚠️ Personne ne les écoute ici : **les faire écouter à Martin**.
- [x] La salutation : la première fois qu'on parle à Mireille (`B.partie.connus` ou l'équivalent qui dit
  « déjà rencontré »), elle dit `salut` avant d'ouvrir le menu ; ensuite, `cours`.
- [x] **Commit** : `feat: le dojo du quartier, 5e tâche — la voix de Mireille`.

#### Tâche 6 : la doc, la suite, la livraison

- [x] `docs/architecture.md` (`app/dojo.py`, `dojo.js`, l'arborescence), `docs/carte.md` (le DOJO DION, les
  glyphes `Y`/`K`/`U`), `tests/test_carte_du_depot.py` vert.
- [x] La **suite complète** en parallèle ; un rouge : le rejouer sur la base avant d'accuser le jalon.
- [x] **Relecture de toute la branche** par un agent neuf ; corriger critiques et importants (un juge rouge
  d'abord), reporter les mineurs dans les Notes.
- [x] Atterrir (ff-only) ; captures pour Martin dans `captures/`, ouvertes dans Aperçu ; livrer (la ligne
  quitte le plan pour `jalons/README.md`, la note sous `## Notes`).

## Notes

**Livré le 26 sept. 2026** — six tâches, plus une passe de corrections après la relecture de toute la branche.

- **Le DOJO DION** : la pièce d'un commerce visitable du Faubourg (RADIO-TV DUMAS, `commerce_24`, la plus au nord qui convienne), reprise sur la ville finie et sans un dé (`_Chantier.poser_le_dojo`, `piece_de_dojo`) : casiers, sac de frappe (`@`), mannequin de bois (`%`), tatami (`A`), le comptoir de Mireille et Kevin au sac. Le SALON MIREILLE s'appelle SALON LOUISE.
- **Mireille Dion** (`mireille`, voix Marie Line) : sa fiche, son visage, sa tenue ; la première fois elle se présente, ensuite ACTION ouvre **LES COURS** (payé une fois, repris sans repayer, le maillon d'avant, fermé la nuit).
- **La leçon** (`static/js/dojo.js`) : le métronome (deux claquements, un fort sur le « et »), la fenêtre de 24 images, trois réussites ou cinq ratés ; la technique enseignée compte comme sue ; Kevin encaisse sans dégât, sans sang, sans crime, se relève et retourne au sac ; la porte, la mort ou ABANDONNER LA LEÇON (pause) l'arrêtent, le cours reste payé.
- **Vingt voix** (v3, avec leur jeu).

⚠️ **Ce qui a surpris** :
- Le Faubourg est serré de lieux garantis : ses pièces de commerce font cinq rangées de profond — un dojo de huit ne se trouvait nulle part (minimum 9 × 5).
- Le **paquet des définitions** était à son plafond : le compte est devenu un métronome synthétisé (plus juste pour le rythme, de toute façon), Kevin le corps du commis recoloré, et seules trois répliques partent au paquet (les autres se disent). ⚠️ Le juge `test_le_paquet_reste_leger` est rouge sur `dev` depuis le 6/49 (54 175 gzip) ; le dojo y ajoute ≈ 400 octets.
- La session du **chalet** a pris les glyphes `Y`, `K`, `U` le même jour : le dojo a `A`, `@`, `%`.
- La relecture a trouvé le **retournement du poignet impossible à apprendre** (sa projection portait dans la même image que SAISIR, avant que la leçon note le geste — le balayage et le coup sauté aussi), **Kevin qui ne marchait jamais** et restait penché, et un cours achetable pendant une leçon. Une leçon au bouton par mise en place tient maintenant chacun.
- Un appel téléphonique **met la leçon en pause** (la boucle est figée) au lieu de l'annuler : c'est mieux.

**Dettes** (mineures) : sans argent, l'item du cours ne dit rien ; `B.cours` n'est pas remis à zéro au retour au titre (une image) ; « TU L'AS » est écrasé par « TU SAIS … ! » ; « Trop tôt » aussi quand on n'a rien tenté ; Kevin ne peut pas mourir (même par balle) ; un étranglement pendant que Kevin est couché.

**À écouter** : les vingt voix de Mireille (`static/audio/histoire-mireille-dojo-*`) — personne ne les a entendues.
