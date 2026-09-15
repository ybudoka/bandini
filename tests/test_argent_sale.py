"""M10, 2e vague — les guichets, le skimmer, l'assurance et la fraude.

⚠️ La regle de tout M10 : **rien de sale ne bat le taxi a l'heure**. Un
guichet defonce vaut moins qu'une journee de travail honnete, trois skimmers
ne rapportent pas ce que le taxi fait dans la meme journee, et une fraude a
l'assurance — meme avec le char le plus cher du catalogue — rapporte moins
par seconde que la course de taxi type. Sinon le jeu se joue tout seul.
"""

from itertools import combinations

import pytest

from app import carte, economie, magasins, recherche, vehicules


def taxi_par_seconde() -> float:
    """L'etalon de tout gain : le taxi, sur la meme horloge que `test_economie`."""
    taxi = economie.BOULOTS["taxi"]
    return economie.gain_boulot(taxi) / (20 * taxi["etapes"])


def taxi_par_jour() -> float:
    return taxi_par_seconde() * economie.JOUR_SECONDES


# --- Les guichets -----------------------------------------------------------


def test_le_guichet_ne_cede_qu_au_camion():
    """`lourd` tranche entre ce qui defonce et ce qui s'arrete — et c'est la
    fiche des chars qui dit lequel est lequel."""
    lourd = economie.GUICHET["lourd"]
    masses = {v["slug"]: v["masse"] for v in vehicules.CATALOGUE}
    assert masses["camion"] >= lourd and masses["autobus"] >= lourd, "le camion doit l'ouvrir"
    for leger in ("auto", "taxi", "sport", "luxe", "remorqueuse", "police"):
        assert masses[leger] < lourd, f"{leger} ouvrirait un guichet"
    # Le delit existe deja dans la taxonomie, a deux etoiles et sans temoin a
    # convaincre : la caisse est par terre, tout le monde l'a vu.
    assert recherche.DELITS["guichet"]["etoiles"] == 2
    assert recherche.DELITS["guichet"]["temoin"] is False


def test_un_guichet_rapporte_moins_qu_une_journee_honnete():
    lo, hi = economie.GUICHET["caisse"]
    assert 0 < lo < hi
    assert economie.GUICHET["liasses"] >= 2
    assert hi < economie.revenu_honnete_par_jour(), "un guichet vaut une journee de proprietes"
    assert hi < taxi_par_jour(), "un guichet vaut une journee de taxi"


def test_le_skimmer_vaut_la_peine_mais_pas_plus_que_le_taxi():
    s = economie.GUICHET["skimmer"]
    assert 0 < s["trouve"] < 1, "un skimmer qu'on ne trouve jamais n'est pas un pari"
    assert s["rendement"][0] < s["rendement"][1]
    esperance = economie.esperance_skimmer()
    assert esperance > 0, "personne ne posera un skimmer qui perd de l'argent en moyenne"
    assert s["max_poses"] * esperance < taxi_par_jour(), "trois skimmers battent le taxi"
    assert s["max_poses"] * esperance < economie.revenu_honnete_par_jour()


def test_le_marche_noir_vend_le_skimmer():
    assert "skimmer" in magasins.MARCHE_NOIR["objets"]
    assert "skimmer" not in magasins.MARCHE_NOIR["articles"], "ce n'est pas une arme"


# --- L'assurance ------------------------------------------------------------


def test_la_fraude_rapporte_moins_a_l_heure_que_le_taxi():
    """Pour CHAQUE char du catalogue : la prime se rembourse (sinon personne
    n'assure), on y perd avec un char paye (sinon c'est un salaire), et le
    net d'une fraude, sur le temps qu'elle prend au moins, reste sous le taxi."""
    a = economie.ASSURANCE
    assert a["cycle_s"] > 0 and a["reclamations_max"] >= 2
    meilleur = 0
    for v in vehicules.CATALOGUE:
        valeur, prime = economie.valeur_assuree(v["prix"]), economie.prime_assurance(v["prix"])
        assert 0 < prime < valeur, v["slug"]
        assert valeur < v["prix"], f"{v['slug']} : frauder avec un char paye rapporterait"
        net = valeur - prime
        assert net / a["cycle_s"] < taxi_par_seconde(), f"{v['slug']} : la fraude bat le taxi a l'heure"
        meilleur = max(meilleur, net)
    # Et sur un cycle d'enquete entier : trois fraudes, puis des jours sans police.
    par_jour = a["reclamations_max"] * meilleur / (a["enquete_jours"] + 1)
    assert par_jour < economie.revenu_honnete_par_jour()
    assert a["enquete_pages"] >= 1, "une enquete qui ne s'ecrit pas au casier n'est pas une enquete"


def test_export_de_l_argent_sale():
    e = economie.exporter()
    assert e["guichet"]["lourd"] == economie.GUICHET["lourd"]
    assert e["guichet"]["skimmer"]["prix"] == economie.GUICHET["skimmer"]["prix"]
    assert list(e["guichet"]["caisse"]) == list(economie.GUICHET["caisse"])
    assert e["assurance"] == economie.ASSURANCE
    assert magasins.MARCHE_NOIR["objets"] == ["skimmer"]


# --- La ville ---------------------------------------------------------------


@pytest.fixture(scope="module")
def ville():
    return carte.generer()


def test_les_guichets_sont_sous_une_vitrine_sur_l_abord(ville):
    """Un guichet est encastre dans une devanture : la vitrine au nord, l'abord
    sous lui, la dalle au sud pour s'y tenir. Et ils s'espacent."""
    fiche = economie.GUICHET
    guichets = [d for d in ville["decor"] if d["type"] == "guichet"]
    lo, hi = fiche["par_ville"]
    assert lo <= len(guichets) <= hi, f"{len(guichets)} guichets"
    vitrines = {(d["x"] + i, d["y"]) for d in ville["devantures"]
                for i, m in enumerate(d["motifs"]) if m == "W"}
    sol = ville["sol"]
    for g in guichets:
        assert sol[g["y"]][g["x"]] == "_", f"un guichet sur « {sol[g['y']][g['x']]} »"
        assert sol[g["y"] + 1][g["x"]] == ".", "on ne peut pas se tenir devant"
        assert (g["x"], g["y"] - 1) in vitrines, f"{g} n'est pas sous une vitrine"
    for a, b in combinations(guichets, 2):
        assert abs(a["x"] - b["x"]) + abs(a["y"] - b["y"]) >= fiche["ecart"], (a, b)
    # Pas tous au meme coin : une moitie de ville sans guichet, c'est un district
    # ou le skimmer ne sert a rien.
    moitie = ville["largeur"] // 2
    assert any(g["x"] < moitie for g in guichets) and any(g["x"] >= moitie for g in guichets)
    # Un guichet est UNE place : rien d'autre n'y est pose.
    places = [(d["x"], d["y"]) for d in ville["decor"]] + [(a["x"], a["y"]) for a in ville["ambulants"]]
    for g in guichets:
        assert places.count((g["x"], g["y"])) == 1
