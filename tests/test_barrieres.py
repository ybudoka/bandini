"""Les zones conditionnelles : une barriere est une FICHE (`carte.BARRIERES`),
pas un cas — ou, ce qu'elle arrete, a quelle condition, ce que coute de
forcer, la raison qui s'affiche.

⚠️ Le juge qui compte : aucune combinaison de barrieres fermees n'enferme la
planque ni ne rend un lieu de mission inatteignable a pied."""

from collections import deque

import pytest
import villes

from app import aeroport, blocs, carte, economie, missions

SORTES = {"pieton", "vehicule"}
CONDITIONS = {"apres", "heure", "jour_tire", "payer", "objet"}


def test_la_fiche_se_tient():
    slugs = [b["slug"] for b in carte.BARRIERES]
    assert len(slugs) == len(set(slugs)) and len(slugs) >= 4
    connues = {m["slug"] for m in missions.CATALOGUE}
    # ⚠️ L'aéroport attend des missions qui ne sont pas encore écrites — c'est ce
    # qui le garde fermé. Elles sont DÉCLARÉES (`aeroport.MISSIONS_A_VENIR`), et
    # un `apres` qui n'est ni au catalogue ni là reste une faute de frappe.
    a_venir = set(aeroport.MISSIONS_A_VENIR)
    assert not a_venir & connues, f"{sorted(a_venir & connues)} : écrite, elle sort des missions à venir"
    for b in carte.BARRIERES:
        assert b["arrete"] and set(b["arrete"]) <= SORTES, b["slug"]
        assert len(b["condition"]) == 1 and set(b["condition"]) <= CONDITIONS, b["slug"]
        if "apres" in b["condition"]:
            assert b["condition"]["apres"] in connues | a_venir, f"{b['slug']} attend une mission qui n'existe pas"
        if "heure" in b["condition"]:
            assert b["condition"]["heure"] in ("jour", "nuit")
        assert b["raison"] == b["raison"].upper() and 0 < len(b["raison"]) <= 40, b["slug"]
        if b["forcer"] is not None:
            assert set(b["forcer"]) <= {"etoiles", "degats"} and b["forcer"], b["slug"]
    # Le pont : ferme aux CHARS, jamais aux jambes — c'est la cle qui evite d'enfermer.
    pont = next(b for b in carte.BARRIERES if b["slug"] == "pont")
    assert pont["arrete"] == ("vehicule",) and pont["forcer"]["degats"] > 0


def test_la_guerite_est_declaree_et_d_accord_avec_la_fourriere():
    """La fiche DECLARE la guerite ; le code qui la joue (`majFourriere`) reste
    le meme, et les deux disent la meme etoile."""
    g = next(b for b in carte.BARRIERES if b["slug"] == "fourriere")
    assert g["existant"] is True and g["arrete"] == ("vehicule",)
    assert g["forcer"]["etoiles"] == economie.FOURRIERE["etoiles_vol"]


@pytest.fixture(scope="module")
def ville():
    return villes.generer()


def rect(b):
    return b["x"], b["y"], b["l"], b["h"]


def dedans(b, x, y):
    return b["x"] <= x < b["x"] + b["l"] and b["y"] <= y < b["y"] + b["h"]


def couronne(b, x, y):
    return dedans(b, x, y) and (x in (b["x"], b["x"] + b["l"] - 1) or y in (b["y"], b["y"] + b["h"] - 1))


def test_chaque_barriere_est_un_rectangle_de_la_ville(ville):
    barrieres = {b["slug"]: b for b in ville["barrieres"]}
    assert set(barrieres) == {b["slug"] for b in carte.BARRIERES}
    for b in barrieres.values():
        assert 0 <= b["x"] and b["x"] + b["l"] <= ville["largeur"] and 0 <= b["y"] and b["y"] + b["h"] <= ville["hauteur"]
        assert b["l"] >= 1 and b["h"] >= 1 and b["raison"] and isinstance(b["arrete"], list)
    pont = ville["ponts"][0]
    assert rect(barrieres["pont"]) == (pont["x"], pont["y"], pont["l"], pont["h"])
    g = ville["fourriere"]["grille"]
    assert rect(barrieres["fourriere"]) == (g["x"], g["y"], g["largeur"], 1)
    # L'usine : sa porte est DEDANS (pas sur la couronne), et la couronne est
    # hors route — une chaine en travers d'une rue arreterait le trafic.
    usine = barrieres["usine"]
    devant = next(p for p in ville["points_interet"] if p["slug"] == "usine")
    assert dedans(usine, devant["x"], devant["y"]) and not couronne(usine, devant["x"], devant["y"])
    for y in range(usine["y"], usine["y"] + usine["h"]):
        for x in range(usine["x"], usine["x"] + usine["l"]):
            if couronne(usine, x, y):
                assert not carte.LEGENDE[ville["sol"][y][x]].get("route"), (x, y)


def test_la_cale_du_norvegien_n_est_derriere_aucune_barriere(ville):
    """Martin (30 sept. 2026) : « on n'a pas vraiment besoin de l'enclos ». La chaîne du quai du cargo
    fermait la cale le jour, et Sven disait « VIENS EN CHAR » derrière une chaîne qu'aucun char ne passait.
    Elle est retirée : aucune barrière n'entoure la cale, et on y vient en char à toute heure."""
    assert "cargo" not in {b["slug"] for b in carte.BARRIERES}
    cale = next(a for a in ville["ambulants"] if a["slug"] == "contrebande")
    autour = [b["slug"] for b in ville["barrieres"]
              if b["x"] - 2 <= cale["x"] < b["x"] + b["l"] + 2 and b["y"] - 2 <= cale["y"] < b["y"] + b["h"] + 2]
    assert not autour, f"la cale de Sven est encore derrière {autour}"


def lieux_de_mission():
    lieux = set()
    for m in missions.CATALOGUE:
        for o in m["objectifs"]:
            # ⚠️ Un mouillage (mouillage:<slug>[:n], m52-m54) n'est pas un
            # point_interet : c'est de l'eau, sans porte ni barrière piétonne à
            # franchir — cette règle-ci ne le concerne pas. Le quai du traversier
            # (`traversier:<escale>`, m99) non plus : il est jugé dans test_traversier.
            # ⚠️ Un lieu de BLOC (la villa, l'infiltration) non plus : il est derrière un passage, dans
            # une autre carte — `blocs.erreurs` juge qu'on l'y rejoint à pied.
            # ⚠️ Ni le quai de la NAVETTE (`navette:<escale>`), ni un lieu de l'ÎLE (`ile:<lieu>`, i04) : on y arrive par
            # l'eau, jamais à pied depuis la planque — `test_ile_en_char_js.py` juge qu'un char y roule.
            if (o.get("lieu") and not o["lieu"].startswith(("mouillage:", "traversier:", "amarrage:", "navette:", "ile:"))
                    and o["lieu"] not in blocs.lieux_des_blocs()):
                lieux.add(o["lieu"])
    for d in missions.DEFIS:
        if d.get("lieu"):
            lieux.add(d["lieu"])
    return lieux


def atteignables(ville, fermees):
    """Les tuiles qu'un pieton atteint depuis la planque, les couronnes des
    barrieres `fermees` comptees comme des murs."""
    sol, L, H = ville["sol"], ville["largeur"], ville["hauteur"]
    murs = set()
    for b in fermees:
        for y in range(b["y"], b["y"] + b["h"]):
            for x in range(b["x"], b["x"] + b["l"]):
                if couronne(b, x, y):
                    murs.add((x, y))
    planque = next(p for p in ville["points_interet"] if p["slug"] == "planque")
    depart = (planque["x"], planque["y"])
    vus, file = {depart}, deque([depart])
    while file:
        x, y = file.popleft()
        for nx, ny in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
            if not (0 <= nx < L and 0 <= ny < H) or (nx, ny) in vus or (nx, ny) in murs:
                continue
            if not carte.marchable(sol[ny][nx]):
                continue
            vus.add((nx, ny))
            file.append((nx, ny))
    return vus


def test_aucune_barriere_n_enferme_la_planque_ni_un_lieu_de_mission(ville):
    """TOUTES fermees en meme temps — le pire cas, et il n'existe pas dans une
    partie (le jour et la nuit ne sont jamais ensemble) : la planque n'est
    dans aucune, et chaque lieu de mission reste a portee de jambes."""
    pietons = [b for b in ville["barrieres"] if "pieton" in b["arrete"] and not b["existant"]]
    points = {p["slug"]: p for p in ville["points_interet"]}
    planque = points["planque"]
    for b in ville["barrieres"]:
        assert not dedans(b, planque["x"], planque["y"]), f"{b['slug']} enferme la planque"
    vus = atteignables(ville, pietons)
    for slug in sorted(lieux_de_mission()):
        p = points[slug]
        # ⚠️ Sauf un lieu que SA barriere d'heure tient pour ses jobs (la regle de l'usine, plus bas) : elle est ouverte
        # quand la job s'offre, et le reste tant qu'elle tourne — on l'atteint toutes les AUTRES barrieres fermees.
        tenante = next((b for b in pietons if dedans(b, p["x"], p["y"]) and tenues_a_l_heure(slug, b["slug"])), None)
        if tenante:
            assert (p["x"], p["y"]) in atteignables(ville, [b for b in pietons if b is not tenante]), \
                f"{slug} : sa chaine ouverte, il reste enferme par une autre"
            continue
        assert (p["x"], p["y"]) in vus, f"{slug} n'est plus atteignable a pied, toutes barrieres fermees"
    # Et ce qui ne rouvre jamais tout seul (`apres`) n'enferme AUCUN lieu.
    fixes = [b for b in pietons if "apres" in b["condition"]]
    vus = atteignables(ville, fixes)
    for slug, p in points.items():
        # ⚠️ Sauf les îles : on n'y va pas à pied, par construction — l'île aux
        # Corneilles n'a pas de pont (`test_ile`), celui de l'aéroport s'arrête
        # au-dessus de l'eau (`test_aeroport`).
        if any(i["x"] <= p["x"] < i["x"] + i["l"] and i["y"] <= p["y"] < i["y"] + i["h"]
               for i in (ville["ile"], ville["aeroport"])):
            continue
        assert (p["x"], p["y"]) in vus, f"{slug} attend une mission pour etre atteignable a pied"
    # Un lieu enferme par une barriere d'heure rouvre le jour ou la nuit : on
    # le tolere — et pour un lieu de mission, seulement si chaque mission qui le
    # nomme est tenue a l'heure de CETTE barriere (la regle de l'usine, ci-dessous).
    for b in pietons:
        for slug, p in points.items():
            if dedans(b, p["x"], p["y"]):
                assert "heure" in b["condition"], f"{b['slug']} enferme {slug} pour de bon"
                if slug in lieux_de_mission():
                    assert tenues_a_l_heure(slug, b["slug"]), f"{b['slug']} enferme le lieu de mission {slug}"


def nommant(slug):
    """Les missions et les defis dont un objectif a `slug` pour `lieu`."""
    return ([m for m in missions.CATALOGUE if any(o.get("lieu") == slug for o in m["objectifs"])]
            + [d for d in missions.DEFIS if d.get("lieu") == slug])


def tenues_a_l_heure(slug, barriere):
    """⚠️ LA REGLE DE L'USINE (1er oct. 2026, t08 et t10) : un lieu derriere une barriere d'heure peut etre un lieu de
    mission si CHAQUE mission qui le nomme est une petite job que cette barriere tient a l'heure
    (`missions.barriere_d_heure`) — elle ne s'offre que barriere ouverte (`Jobs.aLHeure`), et prise, la barriere ne se
    ferme pas sur elle (`Monde.barriereFermee`) : elle ne peut pas finir porte fermee. Un defi, une mission du
    telephone ou du carnet ne regardent pas l'horloge : jamais."""
    qui = nommant(slug)
    return bool(qui) and all("objectifs" in m and m.get("passant") and missions.barriere_d_heure(m) == barriere
                             for m in qui)


def test_la_regle_de_l_usine_se_tient_et_refuse_ce_qu_elle_doit_refuser():
    """t08 et t10 vont a la porte de l'usine : la barriere qui les tient est la cour, la job voyage avec son nom (le
    septieme champ, et seulement pour elles), et une mission qui n'est pas une petite job s'y fait refuser."""
    import copy
    assert {m["slug"] for m in nommant("usine")} == {"t08", "t10"}
    assert tenues_a_l_heure("usine", "usine")
    pliees = {j[0]: j for j in missions.jobs_pour_le_navigateur()}
    assert pliees["t08"][6:] == ["usine"] and pliees["t10"][6:] == ["usine"]
    assert all(len(j) == len(missions.CHAMPS_D_UNE_JOB) for s, j in pliees.items() if s not in ("t08", "t10"))
    # Une mission du telephone qui irait a l'usine : refusee par la forme.
    m = copy.deepcopy(missions.par_slug("s03"))
    m["objectifs"][-1]["lieu"] = "usine"
    assert any("seule une petite job" in e for e in missions.erreurs_de_passant(m))
