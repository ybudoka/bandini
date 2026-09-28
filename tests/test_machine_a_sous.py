"""La machine à sous du Dragon d'or : ses règles (docs/jalons/le-casino-du-petit-canton.md, vague 1).

⚠️ Le retour est CALCULÉ sur les 8 000 arrêts, pas mesuré : le chiffre affiché est le vrai, arrondi, et il
reste sous cent pour cent — la règle du vidéopoker (un jeu d'argent ne bat jamais un boulot).
"""

from collections import Counter
from itertools import product

from app import machine_a_sous as m


def test_le_retour_affiche_est_le_vrai_et_la_maison_gagne():
    exact = m.retour_exact()
    assert round(exact * 100) == m.RETOUR_AFFICHE, exact
    assert 0.80 <= exact < 1.0, exact


def test_trois_rouleaux_de_vingt_de_la_meme_composition():
    assert len(m.ROULEAUX) == 3
    slugs = {s["slug"] for s in m.SYMBOLES}
    for rouleau in m.ROULEAUX:
        assert len(rouleau) == 20 and Counter(rouleau) == Counter(m.COMPTE), Counter(rouleau)
        assert set(rouleau) <= slugs
    assert len(set(m.ROULEAUX)) == 3, "trois fois la même bande"


def test_la_table_paie_du_plus_gros_au_plus_petit_et_chaque_gain_arrive():
    paies = [g["paie"] for g in m.GAINS]
    assert paies == sorted(paies, reverse=True)
    vus = Counter(m.evaluer(a) for a in product(*m.ROULEAUX))
    for g in m.GAINS:
        assert vus[g["slug"]] > 0, f"{g['slug']} n'arrive jamais"
    assert m.evaluer(("dragon", "dragon", "dragon")) == "trois_dragons"
    assert m.evaluer(("cerise", "citron", "cerise")) == "deux_cerises"
    assert m.evaluer(("cerise", "citron", "prune")) == "premiere_cerise"
    assert m.evaluer(("citron", "cerise", "prune")) is None, "une cerise ailleurs qu'au premier rouleau ne paie pas"


def test_le_navigateur_recoit_les_regles():
    r = m.pour_le_navigateur()
    assert r["mise"] == m.MISE and r["retour"] == m.RETOUR_AFFICHE and r["tours_par_jour"] == m.TOURS_PAR_JOUR
    decodes = [[r["symboles"][int(c)] for c in rouleau] for rouleau in r["rouleaux"]]
    assert decodes == [list(x) for x in m.ROULEAUX] and len(r["gains"]) == len(m.GAINS)
