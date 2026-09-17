"""L'Île-aux-Corneilles : ce que la ville gagne, et ce qu'elle ne doit pas perdre.

Demande de Martin (15 sept. 2026) : « tu peux extensionner la carte au besoin ».

⚠️ Les juges de la fiche, dans l'ordre où elle les écrit : l'île ne touche
aucune rive ; aucune route, aucun pont ne la relie ; on y va à la nage, mais
c'est un pari ; la police n'y va pas (`test_ile_js.py`) ; chaque terre ferme
reste un seul îlot marchable. Et un de plus, qui tient tous les autres : elle ne
déplace rien de la ville.
"""

from collections import deque

import pytest

from app import carte, economie, ile, recherche

VILLE = carte.exporter()
SOL = VILLE["sol"]
LARGEUR, HAUTEUR = VILLE["largeur"], VILLE["hauteur"]
FICHE = VILLE["ile"]


def dans_l_ile(x: int, y: int) -> bool:
    return FICHE["x"] <= x < FICHE["x"] + FICHE["l"] and FICHE["y"] <= y < FICHE["y"] + FICHE["h"]


def terre_de_l_ile() -> set[tuple[int, int]]:
    return {(x, y) for y in range(FICHE["y"], FICHE["y"] + FICHE["h"])
            for x in range(FICHE["x"], FICHE["x"] + FICHE["l"]) if SOL[y][x] != "~"}


def eau_jusqu_a_la_rive() -> int:
    """Combien de tuiles d'EAU séparent l'île de la terre la plus proche.

    ⚠️ Mesuré en pas de tuile, par l'eau seulement — comme `test_eau` mesure le
    large : un nageur ne traverse pas une plage pour raccourcir.
    """
    ile_ = terre_de_l_ile()
    dist = {t: 0 for t in ile_}
    file = deque(ile_)
    while file:
        x, y = file.popleft()
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nx, ny = x + dx, y + dy
            if not (0 <= nx < LARGEUR and 0 <= ny < HAUTEUR) or (nx, ny) in dist:
                continue
            if SOL[ny][nx] != "~":
                return dist[(x, y)]            # la premiere terre qui n'est pas l'ile
            dist[(nx, ny)] = dist[(x, y)] + 1
            file.append((nx, ny))
    raise AssertionError("l'ile ne voit aucune rive : elle est seule au monde ?")


def test_l_ile_est_dans_la_ville_et_dans_la_baie():
    assert FICHE["slug"] == "ile" and FICHE["nom"] == "L'Île-aux-Corneilles"
    zone_baie = next(z for z in VILLE["zones"] if z["slug"] == "baie")
    assert zone_baie["x"] <= FICHE["x"] and FICHE["x"] + FICHE["l"] <= zone_baie["x"] + zone_baie["l"]
    assert zone_baie["y"] <= FICHE["y"] and FICHE["y"] + FICHE["h"] <= zone_baie["y"] + zone_baie["h"]
    assert len(terre_de_l_ile()) > 600, "une ile de quelques tuiles n'est pas un endroit ou aller"


def test_l_ile_ne_touche_aucune_rive():
    """Une ceinture d'eau d'au moins quatre tuiles autour du plan — et le plan
    lui-même ne pose pas de terre sur son pourtour (`ile._verifier_le_plan`)."""
    for y in range(FICHE["y"] - 4, FICHE["y"] + FICHE["h"] + 4):
        for x in range(FICHE["x"] - 4, FICHE["x"] + FICHE["l"] + 4):
            if not dans_l_ile(x, y):
                assert SOL[y][x] == "~", f"de la terre a {(x, y)}, dans la ceinture de l'ile"


def test_aucune_route_ni_pont_ne_relie_l_ile():
    for y in range(FICHE["y"], FICHE["y"] + FICHE["h"]):
        for x in range(FICHE["x"], FICHE["x"] + FICHE["l"]):
            assert not carte.routier(SOL[y][x]), f"de la chaussee sur l'ile en {(x, y)}"
            assert VILLE["voie"][y][x] == ".", f"une voie sur l'ile en {(x, y)}"
    for pont in VILLE["ponts"]:
        assert not (pont["x"] < FICHE["x"] + FICHE["l"] and FICHE["x"] < pont["x"] + pont["l"]
                    and pont["y"] < FICHE["y"] + FICHE["h"] and FICHE["y"] < pont["y"] + pont["h"]), pont


def test_aucune_barriere_ne_touche_l_ile():
    """Les zones conditionnelles ferment des endroits de la ville ; l'île n'en a
    pas — sa seule barrière est l'eau (`test_barrieres` la saute pour ça)."""
    for b in VILLE["barrieres"]:
        assert not (b["x"] < FICHE["x"] + FICHE["l"] and FICHE["x"] < b["x"] + b["l"]
                    and b["y"] < FICHE["y"] + FICHE["h"] and FICHE["y"] < b["y"] + b["h"]), b["slug"]


def test_un_ilot_par_terre_ferme():
    """⚠️ Le juge de toute la géographie, changé EXPRÈS : « un seul îlot
    marchable » devient « un îlot par terre ferme ». La ville reste d'un seul
    tenant, et l'île aussi."""
    terres = carte.composantes_par_terre(VILLE)
    assert set(terres) == {"ville", "ile"}
    assert len(terres["ville"]) == 1, f"{len(terres['ville'])} ilots en ville : un trottoir est enclave"
    assert len(terres["ile"]) == 1, f"{len(terres['ile'])} morceaux d'ile : un bout ne se rejoint pas"
    assert terres["ile"][0] <= terre_de_l_ile()


def test_le_decor_de_l_ile_ne_ferme_aucun_passage():
    """⚠️ `composantes_marchables` ne voit pas le décor, le joueur si : un arbre
    ou une corde à linge au mauvais endroit coupe un sentier. Sur l'île, le
    décor SOLIDE compte comme un mur, et on rejoint quand même chaque porte,
    le quai et la chaloupe."""
    solides = {(d["x"], d["y"]) for d in VILLE["decor"]
               if d["type"] in carte.DECOR_SOLIDE and dans_l_ile(d["x"], d["y"])}
    libres = {t for t in terre_de_l_ile() if carte.marchable(SOL[t[1]][t[0]]) and t not in solides}
    depart = min(libres)
    vus, pile = {depart}, [depart]
    while pile:
        x, y = pile.pop()
        for n in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
            if n in libres and n not in vus:
                vus.add(n)
                pile.append(n)
    assert vus == libres, f"{len(libres - vus)} tuiles de l'ile fermees par le decor : {sorted(libres - vus)[:5]}"
    for porte in VILLE["portes"]:
        if dans_l_ile(porte["x"], porte["y"]):
            assert (porte["x"], porte["y"] + 1) in vus, porte
    for amarre in FICHE["amarrages"]:
        assert any((amarre["x"] + dx, amarre["y"] + dy) in vus for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))), \
            f"la chaloupe de {amarre} n'a pas de quai ou mettre le pied"


def _cout_par_tuile(cafe: bool) -> float:
    depense = economie.CAFE["depense"] if cafe else 1.0
    return carte.TUILE_PX / recherche.NAGE["vitesse"] * recherche.NAGE["souffle_par_image"] * depense


def test_a_la_nage_c_est_un_pari():
    """⚠️ « Elle n'est pas fermée, elle est LOIN. » On y va à la nage, mais pas
    sur un coup de tête : ni le souffle seul, ni le café seul, ni l'estomac
    plein seul n'y suffisent — les deux ensemble, oui.

    La première et la dernière tuile sont de l'eau basse (`Monde.eauBasse`) :
    elles ne se paient pas, et ce juge compte comme le jeu compte.
    """
    eau = eau_jusqu_a_la_rive()
    a_payer = eau - 2
    barre = recherche.VITESSES["endurance"]
    surplus = economie.SOUFFLE["surplus_max"]
    assert a_payer * _cout_par_tuile(cafe=False) > barre + surplus, \
        f"{eau} tuiles d'eau : on y va l'estomac plein, sans cafe — l'ile est a cote"
    assert a_payer * _cout_par_tuile(cafe=True) > barre, \
        f"{eau} tuiles d'eau : un cafe suffit — l'ile est a cote"
    assert a_payer * _cout_par_tuile(cafe=True) <= barre + surplus, \
        f"{eau} tuiles d'eau : meme cafe et estomac plein, on se noie — l'ile est fermee, pas loin"


def test_une_chaloupe_attend_au_quai_de_l_ile():
    """⚠️ Hors du plafond de la ville : ses dix-huit places sont prises, et une
    île sans bateau est une île d'où l'on revient à la nage."""
    assert FICHE["amarrages"], "aucune chaloupe a l'ile"
    for amarre in FICHE["amarrages"]:
        assert amarre in VILLE["amarrages"], amarre
        x, y = amarre["x"], amarre["y"]
        assert dans_l_ile(x, y) and SOL[y][x] == "~", amarre
        assert any(SOL[y + dy][x + dx] == "Q" for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))), \
            f"{amarre} ne touche pas le quai de l'ile"


def test_la_zone_de_l_ile_est_un_refuge_et_elle_passe_en_dernier():
    """`Monde.zoneA` garde la DERNIÈRE zone qui contient le point : l'île doit
    passer après la baie, sinon elle n'existe pas pour la police ni la musique."""
    zone = VILLE["zones"][-1]
    assert zone["slug"] == "ile" and zone["district"] == "ile"
    assert (zone["x"], zone["y"], zone["l"], zone["h"]) == (FICHE["x"], FICHE["y"], FICHE["l"], FICHE["h"])
    assert zone["refuge"] is True and zone["police"] == 0 and zone["vehicules"] == 0
    assert zone["pietons"] > 0, "trente habitants l'hiver, pas zero"
    assert [z["slug"] for z in VILLE["zones"] if z.get("refuge")] == ["ile"], "un refuge de trop"


def test_la_chapelle_se_voit_et_s_ouvre():
    """Le repère de l'île : une porte qui mène à sa pièce, un point sur la carte,
    et un clocher sur son toit d'ardoise."""
    portes = {p["lieu"]: p for p in VILLE["portes"] if dans_l_ile(p["x"], p["y"])}
    assert set(portes) == {"chapelle", "hangar_ile"}, sorted(portes)
    assert portes["hangar_ile"]["nom"] == "Le hangar sans nom"
    for porte in portes.values():
        assert porte["interieur"] in VILLE["interieurs"], porte
    reperes = [p for p in VILLE["points_interet"] if dans_l_ile(p["x"], p["y"])]
    assert [(p["slug"], p["famille"]) for p in reperes] == [("chapelle", "repere")]
    clochers = [t for t in VILLE["toits"] if t["type"] == "clocher"]
    assert len(clochers) == 1 and dans_l_ile(clochers[0]["x"], clochers[0]["y"])
    assert SOL[clochers[0]["y"]][clochers[0]["x"]] == "E", "un clocher sur autre chose que l'ardoise"


def test_six_maisons_une_usine_fermee_et_un_couvent():
    """Ce que la fiche promet, compté sur la carte livrée : six maisons et le
    couvent peints comme des logements, l'usine à poisson condamnée."""
    residences = [r for r in VILLE["residences"] if dans_l_ile(r["x"], r["y"])]
    assert len(residences) == 7, len(residences)
    condamnees = [(x, y) for y in range(FICHE["y"], FICHE["y"] + FICHE["h"])
                  for x in range(FICHE["x"], FICHE["x"] + FICHE["l"]) if SOL[y][x] == "d"]
    assert len(condamnees) == 1, condamnees


def test_l_ile_ne_deplace_rien_de_la_ville(monkeypatch):
    """⚠️ Posée après la ville, sans un dé : la ville sans l'île est la même tuile
    pour tuile hors de son rectangle, et tout ce que l'île ajoute s'ajoute —
    rien d'autre ne bouge, pas même un abribus ou un arbre de rue."""
    avec = VILLE
    monkeypatch.setattr(ile, "poser", lambda chantier, ville: None)
    sans = carte.generer()
    for y in range(HAUTEUR):
        if FICHE["y"] <= y < FICHE["y"] + FICHE["h"]:
            x0, x1 = FICHE["x"], FICHE["x"] + FICHE["l"]
            assert avec["sol"][y][:x0] == sans["sol"][y][:x0] and avec["sol"][y][x1:] == sans["sol"][y][x1:], y
        else:
            assert avec["sol"][y] == sans["sol"][y], f"la rangee {y} a bouge"

    def hors_de_l_ile(objets):
        return [o for o in objets if not dans_l_ile(o["x"], o["y"])]

    for cle in ("decor", "portes", "points_interet", "lampes", "residences", "toits", "amarrages"):
        assert hors_de_l_ile(avec[cle]) == sans[cle], f"« {cle} » a bouge hors de l'ile"
    assert avec["zones"][:-1] == sans["zones"]
    assert {k: v for k, v in avec["interieurs"].items() if k not in ile.PIECES} == sans["interieurs"]
    for cle in sans:
        if cle in ("sol", "decor", "portes", "points_interet", "lampes", "residences", "toits",
                   "amarrages", "zones", "interieurs", "ile", "legende", "familles"):
            continue
        assert avec[cle] == sans[cle], f"« {cle} » a bouge"


@pytest.mark.parametrize("graine", [3, 777])
def test_une_autre_graine_a_la_meme_ile(graine):
    """L'île est dessinée : la chapelle est à la même place d'une graine à
    l'autre — c'est ce qui permet d'y écrire des missions."""
    autre = carte.generer(graine=graine)
    assert autre["ile"] == FICHE
    y0, x0 = FICHE["y"], FICHE["x"]
    for y in range(y0, y0 + FICHE["h"]):
        assert autre["sol"][y][x0:x0 + FICHE["l"]] == SOL[y][x0:x0 + FICHE["l"]], y
    terres = carte.composantes_par_terre(autre)
    assert len(terres["ville"]) == 1 and len(terres["ile"]) == 1
