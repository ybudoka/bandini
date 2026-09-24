"""Le poste a son stationnement, le garage sa vraie porte (17 sept. 2026).

Demande de Martin : « ajoute toujours un stationnement au poste de police avec
une ou des vehicules de police stationnes et aussi pour le garage, il faut une
vraie porte de garage ou on stationne pour vendre ou faire des missions. la
porte ouvre seule des qu'on est devant en voiture. »

Ici, la VILLE : le lot et ses cases, la porte et sa baie. Ce qui bouge (les
autos-patrouilles garees, le rideau qui se leve, le menu) se juge au banc,
dans `test_poste_et_garage_js.py`.
"""

import pytest

from app import carte

GRAINES = (carte.GRAINE, 1, 2)
#: Le glyphe d'une case nez au nord, et celui de l'allee — ecrits ici, pas lus
#: dans le module : le juge ne relit pas la regle qu'il garde.
CASE_NORD, ALLEE = "^", "p"
#: Le barbele, et la barriere coulissante qui ferme le lot du poste sur la rue.
BARBELE, BARRIERE = "X", "Z"


@pytest.fixture(scope="module", params=GRAINES)
def ville(request):
    return carte.generer(graine=request.param)


def _roulable(sol, x, y):
    return carte.LEGENDE[sol[y][x]].get("solide", 0) == 0


def _batiment_du_poste(ville):
    """Les tuiles du batiment qui porte la porte du poste (sa carcasse)."""
    porte = next(p for p in ville["portes"] if p["lieu"] == "poste")
    sol = ville["sol"]
    vues, pile = {(porte["x"], porte["y"])}, [(porte["x"], porte["y"])]
    while pile:
        cx, cy = pile.pop()
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nx, ny = cx + dx, cy + dy
            if (nx, ny) not in vues and carte.LEGENDE[sol[ny][nx]].get("solide") == 1:
                vues.add((nx, ny))
                pile.append((nx, ny))
    return vues


def test_le_poste_a_toujours_son_stationnement_colle_au_batiment(ville):
    lot = ville["stationnement_du_poste"]
    assert lot, "le poste n'a pas de stationnement"
    assert lot["lieu"] == "poste" and lot["vehicule"] == "police"
    batiment = _batiment_du_poste(ville)
    # Colle au mur est du poste, sur toute la hauteur du lot qui le longe.
    assert any((lot["x"] - 1, lot["y"] + j) in batiment for j in range(lot["hauteur"])), \
        f"le lot {lot} ne touche pas le poste"
    assert len(lot["places"]) >= 2, lot
    assert 1 <= lot["garees"] <= len(lot["places"]), lot
    if len(lot["places"]) >= 3:
        assert lot["garees"] < len(lot["places"]), "un vrai lot garde une place libre"


def test_les_places_sont_des_cases_qui_donnent_sur_une_allee_jusqu_a_la_rue(ville):
    """Chaque place est le FOND d'une case nez au nord (la regle de
    `placeStationnee`), la case a son allee derriere elle, et l'allee descend
    sans mur jusqu'a une tuile de route — sinon on gare des chars qu'on ne
    ressort jamais."""
    lot, sol = ville["stationnement_du_poste"], ville["sol"]
    for place in lot["places"]:
        x, y = place["x"], place["y"]
        assert place["sens"] == "N"
        assert sol[y][x] == CASE_NORD and sol[y + 1][x] == CASE_NORD, f"pas une case en {x, y}"
        assert sol[y - 1][x] != CASE_NORD, f"{x, y} n'est pas le fond de sa case"
        assert sol[y + 2][x] == ALLEE, f"la case {x, y} n'a pas d'allee derriere elle"
        # On descend : roulable jusqu'a la route, en moins de huit tuiles apres le lot.
        # ⚠️ La barriere coulissante est la sortie : elle s'ouvre pour l'auto-patrouille.
        ty = y + 2
        while not carte.LEGENDE[sol[ty][x]].get("route") or sol[ty][x] in (ALLEE, CASE_NORD):
            assert _roulable(sol, x, ty) or sol[ty][x] == BARRIERE, \
                f"un mur en {x, ty} entre la case {x, y} et la rue"
            ty += 1
            assert ty <= lot["y"] + lot["hauteur"] + 8, f"la case {x, y} ne mene a aucune rue"


def test_le_lot_du_poste_est_clos_de_barbele_et_ne_sort_que_par_sa_barriere(ville):
    """Demande de Martin (23 sept. 2026) : « le poste de police doit etre
    completement cloture barbele pour ne pas qu'on vole les autos ». Depuis les
    cases, tout ce qu'un pieton traverse — en enjambant s'il le faut — reste dans
    le lot : les murs du poste, le barbele, et la barriere. Elle prend toute la
    largeur de l'allee, et de l'autre cote, c'est la rue."""
    lot, sol = ville["stationnement_du_poste"], ville["sol"]
    b = lot["barriere"]
    assert (b["x"], b["l"]) == (lot["x"], lot["largeur"]), f"la barriere {b} ne ferme pas toute l'allee"
    assert [sol[b["y"]][b["x"] + i] for i in range(b["l"])] == [BARRIERE] * b["l"]
    dedans = {(lot["x"] + i, lot["y"] + j) for i in range(lot["largeur"]) for j in range(lot["hauteur"])}
    depart = [(p["x"], p["y"]) for p in lot["places"]]
    vues, pile, bords = set(depart), list(depart), set()
    while pile:
        cx, cy = pile.pop()
        assert (cx, cy) in dedans, f"on sort du lot du poste a pied par {cx, cy} ({sol[cy][cx]!r})"
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nx, ny = cx + dx, cy + dy
            g = sol[ny][nx]
            if (nx, ny) in vues:
                continue
            if carte.LEGENDE[g].get("solide", 0) in (0, 3, 4):
                vues.add((nx, ny))
                pile.append((nx, ny))
            else:
                bords.add(g)
    assert BARRIERE in bords and BARBELE in bords, f"le lot n'est pas clos de barbele : {sorted(bords)}"
    assert bords <= {BARRIERE, BARBELE} | {g for g in bords if carte.LEGENDE[g].get("solide") == 1}, sorted(bords)
    for i in range(b["l"]):
        dehors = sol[b["y"] + 1][b["x"] + i]
        assert _roulable(sol, b["x"] + i, b["y"] + 1), f"la barriere donne sur {dehors!r}, pas sur la rue"


def test_la_barriere_coulissante_est_du_barbele_qui_s_ouvre():
    """Fermee, elle ne se passe pas plus que le barbele (ni a pied, ni en char, et
    un lourd ne la defonce pas : c'est la solidite 5) ; mais c'est une SORTIE —
    la connexite la traverse, sinon le lot serait une poche fermee."""
    assert carte.solidite(BARRIERE) == carte.solidite(BARBELE) == 5
    assert carte.LEGENDE[BARRIERE]["cloture"] == "barbele"
    assert carte.franchissable(BARRIERE) and not carte.franchissable(BARBELE)
    assert not carte.marchable(BARRIERE), "on ne se tient pas sur une barriere"


def _poses_sur(ville, tuiles):
    """Ce que la ville a pose sur ces tuiles : decor, paquets, kiosques, scenes."""
    return [(cle, q) for cle in ("decor", "paquets", "ambulants", "scenes")
            for q in ville[cle] if (q["x"], q["y"]) in tuiles]


def test_rien_ne_se_pose_dans_le_lot_ni_dans_sa_sortie(ville):
    """Dans le lot, dans sa sortie — et sur sa BORDURE : un meuble au bout d'une
    sortie de char ferme la sortie (`mobilier.SORTIES_DE_CHAR`), et un arbre, un
    parcometre et un lampadaire bordaient l'allee du poste."""
    lot = ville["stationnement_du_poste"]
    dedans = {(lot["x"] + i, lot["y"] + j) for i in range(-1, lot["largeur"] + 1)
              for j in range(-1, lot["hauteur"] + 2)}
    poses = _poses_sur(ville, dedans)
    assert not poses, f"pose dans le lot du poste, sa sortie ou sa bordure : {poses}"


def test_le_garage_a_une_vraie_porte_de_deux_tuiles_a_cote_de_la_sienne(ville):
    portes = [p for p in ville["portes_garage"] if p["lieu"] == "garage"]
    assert len(portes) == 1, ville["portes_garage"]
    pg, sol = portes[0], ville["sol"]
    assert pg["l"] >= 2, "une porte de garage d'une tuile, c'est un dessin, pas une porte"
    assert [sol[pg["y"]][pg["x"] + i] for i in range(pg["l"])] == ["G"] * pg["l"]
    # Sur la facade du garage, a cote de la porte des pietons — sans la toucher.
    porte = next(p for p in ville["portes"] if p["lieu"] == "garage")
    assert pg["y"] == porte["y"]
    assert porte["x"] < pg["x"] - 1 or porte["x"] > pg["x"] + pg["l"], \
        f"le rideau {pg} colle a la porte des pietons {porte['x']}"
    assert abs(porte["x"] - pg["x"]) <= 5, "le rideau est au bout du monde de la porte de Ti-Guy"


def test_devant_le_rideau_une_baie_paveee_libre_jusqu_a_la_rue(ville):
    """Les deux tuiles devant chaque lame : roulables, sans decor, et pavees —
    pas un `_` d'abord entre la baie et le trottoir."""
    pg, sol = ville["portes_garage"][0], ville["sol"]
    baie = {(pg["x"] + i, pg["y"] + j) for i in range(pg["l"]) for j in (1, 2)}
    for x, y in sorted(baie):
        assert _roulable(sol, x, y), f"la baie est bouchee en {x, y}"
        assert sol[y][x] != "_", f"l'abord n'est pas pave devant le rideau en {x, y}"
    poses = _poses_sur(ville, baie)
    assert not poses, f"pose dans la baie du garage : {poses}"
    # La pancarte d'une enseigne pend sous un bout du bandeau : jamais devant le rideau.
    for d in ville["devantures"]:
        if d["y"] == pg["y"] and d["pancarte"]:
            bout = d["x"] if d["pancarte"] == -1 else d["x"] + d["l"] - 1
            assert (bout, pg["y"] + 1) not in baie, f"la pancarte de « {d['texte']} » pend devant le rideau"


def test_le_lot_et_la_porte_ne_deplacent_rien_d_autre_dans_la_ville(ville, monkeypatch):
    """⚠️ Poses pendant la construction, les vingt-sept tuiles du lot faisaient
    glisser TOUTE la ville (166 decors, les vingt paquets, la cale du cargo hors
    de sa barriere) : chaque etape suivante tire sa place dans une liste de
    tuiles. La meme ville sans eux doit etre identique a la tuile pres, hors du
    lot et de la baie."""
    # ⚠️ Les deux POSEURS neutralises, pas l'etape de la fin : un lot pose trop tot
    # serait aussi dans la ville temoin, et le juge comparerait deux villes glissees.
    # ⚠️ Et le devant des portes (`devants.deplacer`) des DEUX villes : il vient apres le lot, et
    # la porte du garage est une porte comme une autre — il ecarte ce qui tombe devant elle
    # (un nid-de-poule a quatre tuiles de son rideau). C'est son travail, pas un glissement.
    from app import devants
    monkeypatch.setattr(devants, "deplacer", lambda chantier, ville_: {})
    avec = carte.generer(graine=ville["graine"])
    monkeypatch.setattr(carte._Chantier, "_stationnement_de_service", lambda self, *a: None)
    monkeypatch.setattr(carte._Chantier, "poser_porte_de_garage", lambda self, *a: None)
    sans = carte.generer(graine=ville["graine"])
    for cle in ("paquets", "ambulants", "reclames", "scenes", "nids_de_poule",
                "barrieres", "metro", "autobus", "chantiers"):
        assert avec[cle] == sans[cle], f"le lot du poste ou la porte du garage deplace « {cle} »"
    ville = avec
    lot, pg = ville["stationnement_du_poste"], ville["portes_garage"][0]
    # Les devantures : identiques, sauf l'enseigne au-dessus du rideau (son masque
    # et sa pancarte suivent la porte).
    def au_dessus(d):
        return d["y"] == pg["y"] and d["x"] < pg["x"] + pg["l"] and pg["x"] < d["x"] + d["l"]
    assert [d for d in ville["devantures"] if not au_dessus(d)] == [d for d in sans["devantures"] if not au_dessus(d)]
    a_nous = {(lot["x"] + i, lot["y"] + j) for i in range(-1, lot["largeur"] + 1)
              for j in range(-1, lot["hauteur"] + 2)}
    a_nous |= {(pg["x"] + i, pg["y"] + j) for i in range(pg["l"]) for j in range(0, 12)}
    for cle in ("decor", "lampes"):
        garde = [q for q in sans[cle] if (q["x"], q["y"]) not in a_nous]
        assert [q for q in ville[cle] if (q["x"], q["y"]) not in a_nous] == garde, f"« {cle} » a bouge hors du lot et de la baie"
    for y, (avec, sans_rangee) in enumerate(zip(ville["sol"], sans["sol"])):
        for x, (a, b) in enumerate(zip(avec, sans_rangee)):
            if a != b:
                assert (x, y) in a_nous, f"la tuile {(x, y)} a change hors du lot et de la baie : {b!r} -> {a!r}"
