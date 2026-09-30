"""La patinoire du parc (P4, docs/jalons/la-patinoire-du-parc.md).

Demande de Martin (30 sept. 2026) : « l'hiver, mets une patinoire dans un parc avec des gens qui
patinent ». Une patinoire extérieure à bandes, à la québécoise, dans le parc du Faubourg : l'hiver,
tant que la neige tient, la glace, ses bandes et ses deux filets ; l'été, une clairière de gazon.

Ici ne se choisit que sa PLACE : un rectangle de gazon et d'allée dans le parc, et les portes de ses
bandes. Tout le reste (la glace, les bandes, les patineurs, la glisse) vit dans le navigateur
(`static/js/patinoire.js`), peint et sans rien poser.

⚠️ **LE PARC N'A PAS LA PLACE** : 29 arbres semés partout, et le plus grand coin libre fait six tuiles
sur six. On taille donc une CLAIRIÈRE, à la toute fin (après les statues, avant la bande nord) et
**sans un dé** : le choix se fait au moindre coût, dans l'ordre de lecture ; le décor qui s'y trouve
(des arbres, des buissons, des bancs) se DÉPLACE sur la pelouse voisine, **à sa place dans la liste** —
jamais retiré : un décor de moins renumérote tout ce qui le suit (`Entites.creerDecor`), et avec lui
tout ce qui se tire à l'empreinte d'un numéro.

⚠️ **AUCUNE TUILE NE CHANGE** : la glace est une couche peinte. Le sol reste du gazon (`,`) et de la
poussière de pierre (`g`) ; les juges de circulation et de connexité ne voient pas de patinoire.
"""

from __future__ import annotations

#: Le parc qui la reçoit : le plus grand parc de ville, celui du Faubourg.
DISTRICT = "faubourg"

#: Les mesures essayées, de la plus grande à la plus petite (largeur, hauteur, en tuiles) : la
#: première qui trouve sa place l'emporte.
MESURES: tuple[tuple[int, int], ...] = ((14, 6), (14, 5), (13, 5), (12, 5), (12, 4))

#: Le sol sur lequel la glace peut se poser : le gazon et l'allée de poussière de pierre.
SOLS = frozenset({",", "g"})

#: Ce qui peut se déplacer pour lui faire de la place. Le reste (une statue, un belvédère, un banc
#: qui regarde la rue) arrête la fenêtre.
DEPLACABLES = frozenset({"arbre", "buisson", "banc"})

#: Ce que coûte chaque tuile d'allée couverte : une allée coupée se contourne, mais on la préfère
#: libre. Un décor déplacé coûte 1.
COUT_D_ALLEE = 0.25

#: Jusqu'où un décor déplacé cherche sa nouvelle place (en tuiles).
PORTEE = 10

#: Les couches qui prennent une tuile pour elles (la même liste que les statues).
COUCHES_PRISES = ("paquets", "scenes", "ambulants", "reclames", "points_interet")

#: Les quatre côtés : (nom, dx, dy) vers l'extérieur.
COTES = (("nord", 0, -1), ("sud", 0, 1), ("ouest", -1, 0), ("est", 1, 0))

#: Au plus deux portes dans les bandes.
PORTES_MAX = 2

#: Le guichet des patins : la fenêtre du kiosque de Madame Thibodeau qui donne sur la glace, s'il est à moins
#: de `PORTEE_DU_KIOSQUE` tuiles ; sinon, la première porte des bandes.
PORTEE_DU_KIOSQUE = 8


def _parc(chantier) -> tuple[int, int, int, int] | None:
    for x, y, largeur, hauteur, district in chantier.parcs_de_ville:
        if district == DISTRICT:
            return x, y, largeur, hauteur
    return None


def _fenetres(chantier, ville: dict, parc, largeur: int, hauteur: int, decor: dict, pris: set):
    """Les fenêtres possibles de cette mesure dans le parc, (coût, x, y), de la moins chère à la plus chère
    puis dans l'ordre de lecture. Pure."""
    px, py, pl, ph = parc
    toutes = []
    for y in range(py, py + ph - hauteur + 1):
        for x in range(px, px + pl - largeur + 1):
            cout, ok = 0.0, True
            for j in range(y - 1, y + hauteur + 1):
                for i in range(x - 1, x + largeur + 1):
                    dedans = x <= i < x + largeur and y <= j < y + hauteur
                    d = decor.get((i, j))
                    if not dedans:
                        if not (px <= i < px + pl and py <= j < py + ph):
                            continue            # le trottoir d'a cote : son mobilier ne gene pas
                        # ⚠️ Le tour des bandes reste praticable : ni une statue ni un belvédère collé
                        # contre (on ne passerait plus entre les deux), ni le devant d'une porte.
                        if d and d not in DEPLACABLES:
                            ok = False
                        continue
                    if ville["sol"][j][i] not in SOLS or (i, j) in pris or (i, j) in chantier.reserve:
                        ok = False
                    elif d:
                        if d not in DEPLACABLES:
                            ok = False
                        cout += 1
                    elif ville["sol"][j][i] == "g":
                        cout += COUT_D_ALLEE
                    if not ok:
                        break
                if not ok:
                    break
            if ok:
                toutes.append((cout, y, x))
    return [(cout, x, y) for cout, y, x in sorted(toutes)]


def _portes(ville: dict, x: int, y: int, largeur: int, hauteur: int) -> list[dict]:
    """Les portes des bandes : là où une allée ou un trottoir arrive contre elles, au milieu de chaque
    arrivée ; l'allée d'abord, puis le trottoir, puis l'ordre de lecture. Sans arrivée, une porte au
    milieu du côté sud."""
    arrivees = []
    for cote, dx, dy in COTES:
        if dx == 0:
            bord = [(i, y if dy < 0 else y + hauteur - 1) for i in range(x + 1, x + largeur - 1)]
        else:
            bord = [(x if dx < 0 else x + largeur - 1, j) for j in range(y + 1, y + hauteur - 1)]
        suite: list[tuple[int, int]] = []
        for i, j in bord + [(None, None)]:
            dehors = None if i is None else ville["sol"][j + dy][i + dx]
            if dehors in ("g", "."):
                suite.append((i, j))
                continue
            if suite:
                mi, mj = suite[len(suite) // 2]
                sorte = ville["sol"][mj + dy][mi + dx]
                arrivees.append((0 if sorte == "g" else 1, mj, mi, cote))
                suite = []
    arrivees.sort()
    portes = [{"x": i, "y": j, "cote": cote} for _, j, i, cote in arrivees[:PORTES_MAX]]
    return portes or [{"x": x + largeur // 2, "y": y + hauteur - 1, "cote": "sud"}]


def _service(ville: dict, x: int, y: int, largeur: int, hauteur: int) -> list[dict]:
    """LA PORTE DE SERVICE (la deuxième vague, 30 sept. 2026) : celle de la surfaceuse, deux tuiles au milieu du côté
    qui donne sur le TROTTOIR — un char y entre, et glisse. Aucune si la glace ne touche pas de trottoir."""
    for cote, dx, dy in COTES:
        if dx == 0:
            bord = [(i, y if dy < 0 else y + hauteur - 1) for i in range(x + 1, x + largeur - 1)]
        else:
            bord = [(x if dx < 0 else x + largeur - 1, j) for j in range(y + 1, y + hauteur - 1)]
        dehors = [(i, j) for i, j in bord if ville["sol"][j + dy][i + dx] == "."]
        if len(dehors) >= 4 and len(dehors) == len(bord):
            m = len(bord) // 2
            return [{"x": i, "y": j, "cote": cote, "service": True} for i, j in bord[m - 1:m + 1]]
    return []


def _deplacer(chantier, ville: dict, parc, zone: set, pris: set) -> int | None:
    """Le décor de la zone, sur la pelouse la plus proche du parc, à sa place dans la liste. Rend le
    nombre de décors déplacés — ou None si l'un d'eux ne trouve pas sa place : alors RIEN n'a bougé
    (on ne retire jamais un décor, et la fenêtre suivante essaiera)."""
    from . import carte, devants, mobilier

    px, py, pl, ph = parc
    solides = {(d["x"], d["y"]) for d in ville["decor"] if d["type"] in carte.DECOR_SOLIDE}
    # ⚠️ Ni devant une porte au sens LARGE de `devants.py` (le devant d'un lieu de mission : le kiosque de
    # Madame Thibodeau en est un) — `_place_libre` ne connaît que le pas de porte, et sur d'autres graines un
    # arbre retombait devant le kiosque.
    larges, pas = devants.devants(ville)
    interdites = larges | pas
    occupe, pris_avant, faits = set(chantier.occupe), set(pris), []
    deplaces = 0
    for d in sorted((d for d in ville["decor"] if (d["x"], d["y"]) in zone), key=lambda d: (d["y"], d["x"])):
        x0, y0 = d["x"], d["y"]
        chantier.occupe.discard((x0, y0))
        solides.discard((x0, y0))
        cible = next(((x, y) for x, y in devants._anneaux(x0, y0, PORTEE)
                      if px <= x < px + pl and py <= y < py + ph
                      and ville["sol"][y][x] == ","
                      and (x, y) not in zone and (x, y) not in pris and (x, y) not in interdites
                      and mobilier._place_libre(chantier, x, y, solides)), None)
        if cible is None:
            for fait in faits:
                fait[0]["x"], fait[0]["y"] = fait[1]
            chantier.occupe.clear()
            chantier.occupe.update(occupe)
            pris.clear()
            pris.update(pris_avant)
            return None
        faits.append((d, (x0, y0)))
        d["x"], d["y"] = cible
        chantier.occupe.add(cible)
        pris.add(cible)
        if d["type"] in carte.DECOR_SOLIDE:
            solides.add(cible)
        deplaces += 1
    return deplaces


def _guichet(ville: dict, x: int, y: int, largeur: int, hauteur: int, portes: list[dict]) -> dict:
    """La tuile de bord de la glace la plus proche de la porte du kiosque (celui du parc), et le côté de la bande
    qu'elle touche ; sans kiosque à portée, la première porte des bandes. Sans un dé."""
    kiosques = [p for p in ville["portes"] if p.get("lieu") == "kiosque"]
    bord = [(i, j) for j in range(y, y + hauteur) for i in range(x, x + largeur)
            if i in (x, x + largeur - 1) or j in (y, y + hauteur - 1)]
    mieux = None
    for k in kiosques:
        for i, j in bord:
            # ⚠️ La distance VRAIE, pas le max des écarts : à égalité de max, le coin de la glace l'emportait (la
            # rangée la plus haute), et la bande nord y repoussait le joueur hors de la glace.
            d = (i - k["x"]) ** 2 + (j - k["y"]) ** 2
            if d <= PORTEE_DU_KIOSQUE ** 2 and (mieux is None or (d, j, i) < mieux[0]):
                mieux = ((d, j, i), i, j)
    if mieux is None:
        return {"x": portes[0]["x"], "y": portes[0]["y"], "cote": portes[0]["cote"]}
    _, i, j = mieux
    cote = "est" if i == x + largeur - 1 else "ouest" if i == x else "sud" if j == y + hauteur - 1 else "nord"
    return {"x": i, "y": j, "cote": cote}


def poser(chantier, ville: dict) -> dict | None:
    """La clairière de la patinoire au parc du Faubourg, et ses portes ; rend sa fiche, ou None (une
    ville sans ce parc). Sur la ville finie, sans un dé : seul le décor de la clairière bouge."""
    parc = _parc(chantier)
    if parc is None:
        return None
    decor = {(d["x"], d["y"]): d["type"] for d in ville["decor"]}
    pris = {(o["x"], o["y"]) for cle in COUCHES_PRISES for o in ville.get(cle) or []}
    px, py, pl, ph = parc
    for largeur, hauteur in MESURES:
        for _, x, y in _fenetres(chantier, ville, parc, largeur, hauteur, decor, pris):
            # ⚠️ La clairière ET le tour des bandes : un arbre planté contre une bande bouche le passage.
            zone = {(i, j) for j in range(max(py, y - 1), min(py + ph, y + hauteur + 1))
                    for i in range(max(px, x - 1), min(px + pl, x + largeur + 1))}
            deplaces = _deplacer(chantier, ville, parc, zone, pris)
            if deplaces is not None:
                portes = _portes(ville, x, y, largeur, hauteur)
                return {"x": x, "y": y, "l": largeur, "h": hauteur,
                        "portes": portes + _service(ville, x, y, largeur, hauteur), "deplaces": deplaces,
                        "guichet": _guichet(ville, x, y, largeur, hauteur, portes)}
    return None


#: CE QUE DIT MADAME THIBODEAU AU GUICHET DES PATINS, à voix haute (Martin, 30 sept. 2026 : la deuxième vague). Le slug
#: de la voix : `thibodeau-patins-<cle>` ; le texte en casse naturelle (le HUD l'écrit en capitales) ; `jeu`, collé à
#: la réplique (docs/jeu-d-acteur.md) — ⚠️ il ne part jamais au navigateur. Elle ne se nomme pas : elle est chez
#: elle, derrière son comptoir (docs/personnages/madame-thibodeau.md). ⚠️ Une réplique neuve s'ajoute AU BOUT de sa
#: clé (`mot-4`) : les mp3 payés portent le slug.
REPLIQUES: tuple[dict, ...] = (
    {"qui": "thibodeau", "cle": "mot-1", "texte": "Tiens, mon p'tit. Tu me les ramènes en un morceau, veux-tu?",
     "jeu": "[warmly] Tiens, mon p'tit. Tu me les ramènes en un morceau, veux-tu?"},
    {"qui": "thibodeau", "cle": "mot-2", "texte": "Deux piastres. Pis tu laces serré, hein?",
     "jeu": "[warmly] Deux piastres. [laughs] Pis tu laces serré, hein?"},
    {"qui": "thibodeau", "cle": "mot-3", "texte": "Bonne patine! Tu fais attention aux petits, veux-tu?",
     "jeu": "[cheerful] Bonne patine! [softly] Tu fais attention aux petits, veux-tu?"},
    {"qui": "thibodeau", "cle": "fauche", "texte": "Deux piastres, mon p'tit… T'as pas ça sur toi?",
     "jeu": "[concerned] Deux piastres, mon p'tit… T'as pas ça sur toi?"},
)


def repliques() -> list[dict]:
    """Les répliques du guichet, comme `audio` les lit : une banque (`mission: "patinoire"`), une série."""
    return [{"slug": f"{r['qui']}-patins-{r['cle']}", "qui": r["qui"], "cle": r["cle"], "texte": r["texte"],
             "mission": "patinoire", "partie": "patinoire", "telephone": False} for r in REPLIQUES]


def _dit(cle: str) -> str:
    return next(r["texte"] for r in REPLIQUES if r["cle"] == cle).upper()


#: Ce que le navigateur en fait (`static/js/patinoire.js`) : les couleurs, la glisse, la chute.
FICHE: dict = {
    "couleurs": {
        "glace": "#dfeef6", "rayure": "#c6dcea", "reflet": "#f4fbff",
        "bande": "#f2f1ea", "ombre": "#9aa6ad", "liseret": "#c8302a",
        "filet": "#d23b2e", "poteau": "#e8e8e8", "lampe": "#3b3f44",
    },
    # ⚠️ LA GLISSE : la vitesse voulue (celle que donnent les commandes) se rejoint PEU À PEU. `elan` est
    # la part de l'écart comblée à chaque image quand on pousse, `freinage` quand on lâche tout : petite,
    # c'est un arrêt qui prend du temps et un virage large. Les passants ont la leur, un peu plus sûre.
    "glisse": {
        "joueur": {"elan": 0.05, "freinage": 0.015},
        "pieton": {"elan": 0.07, "freinage": 0.03},
    },
    # ⚠️ LA CHUTE, sans un dé : courir sur la glace sans patins (ESQUIVE tenue) `images_de_course` de suite,
    # ou virer de plus de `virage_deg` lancé à plus de `vitesse_de_virage` px par image — on tombe
    # `images_au_sol` images, comme projeté (`auSol`).
    "chute": {"images_de_course": 50, "virage_deg": 110, "vitesse_de_virage": 1.1, "images_au_sol": 50},
    # Les lampadaires des quatre coins, le soir : leur lueur (rgb), sa force et son rayon en px.
    "lampes": {"lueur": [255, 236, 190], "force": 0.55, "rayon": 58},
    # LES PATINEURS (vague 2) : de vrais passants, qui naissent sur la glace pendant qu'elle est HORS DE L'ÉCRAN
    # et que le joueur est à moins de `portee_px` — on arrive, elle est pleine ; personne n'apparaît sous nos
    # yeux. `nombre` : [de h, à h, combien] ; personne avant la première heure ni après la dernière.
    # `un_enfant_sur` : le rang d'arrivée le dit (le 2e, le 5e…), jamais un dé. Ils tournent à contre-sens des aiguilles d'une
    # montre, chacun sur son couloir (`couloirs_px` : l'écart entre deux couloirs), le cap `avance_rad` devant
    # eux. Un enfant tombe parfois : une chance sur `chute_une_sur` à chaque seconde, à l'empreinte.
    "patineurs": {
        "nombre": [[9, 12, 3], [12, 17, 7], [17, 22, 9]],
        "un_enfant_sur": 3, "portee_px": 480, "marge_px": 12, "couloirs_px": 6, "couloirs": 3,
        "avance_rad": 0.6, "chute_une_sur": 25, "images_de_chute": 50, "lame": "#d9dde2",
    },
    # LES PATINS À LOUER (vague 3) : au guichet du kiosque, qui ouvre sur la glace. On les chausse pour `prix` $,
    # on les rend en quittant la glace. En patins on va plus vite (`vitesse`, sur la vitesse de marche) MAIS on
    # glisse toujours (Martin : « patin, mais on doit glisser aussi ») — un élan plus franc, un arrêt encore
    # plus long ; et on ne tombe plus en courant, seulement en virant sec lancé.
    "patins": {
        "prix": 2, "portee_px": 20, "vitesse": 1.6,
        "glisse": {"elan": 0.08, "freinage": 0.01},
        "invite": "LOUER DES PATINS", "enseigne": "PATINS 2 $",
        # Madame Thibodeau (docs/personnages/madame-thibodeau.md) : « mon p'tit », une demande qui finit en
        # question, jamais un sacre — et pas son nom : elle est chez elle, derrière son comptoir.
        # Le texte vient des répliques (`REPLIQUES`) : ce qu'on lit est ce qu'on entend.
        "mots": tuple(_dit(f"mot-{n}") for n in (1, 2, 3)),
        "deja": "T'AS DÉJÀ TES PATINS AUX PIEDS, MON P'TIT.",
        "fauche": _dit("fauche"),
        "rendus": "TU RENDS TES PATINS.",
        "couleurs": {"guichet": "#6b4a2b", "enseigne": "#f2e6c4", "texte": "#8a2a1e"},
    },
    # LES CHARS SUR LA GLACE (la deuxième vague) : ils n'entrent que par la porte de service, et y glissent — ce
    # que la glace laisse de l'adhérence et du frein (le modèle du dérapage des saisons, lot 6a, fait le reste).
    "chars": {"adherence": 0.15, "frein": 0.2},
    # LE SON (vague 3) : la rumeur de la glace (`audio`, le lieu `patinoire`) tant qu'on y patine, et la valse du
    # haut-parleur le soir (`musique.VALSE`), dosées à la distance du centre de la glace : pleines à `plein_px`,
    # muettes à `portee_px`.
    "son": {"plein_px": 120, "portee_px": 420, "rumeur": 0.35, "valse": 0.55, "valse_des_h": 17, "valse_jusqu_h": 22},
}


def pour_le_navigateur() -> dict:
    """La fiche, et la série des voix du guichet (⚠️ hors des définitions : la fiche voyage dans la suite)."""
    from . import audio
    return {**FICHE, "voix": audio.serie_de_voix("thibodeau-patins-", audio.voix_patinoire())}
