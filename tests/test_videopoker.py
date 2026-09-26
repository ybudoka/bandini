"""Le vidéopoker du Brouillard : les règles (docs/jalons/le-videopoker-du-brouillard.md).

Le banc (`test_videopoker_js.py`) juge la machine qu'on joue ; ici, ce que Python en dit — que les
mains s'évaluent comme au poker, que la table va de la meilleure à la plus petite, et que la
machine rend MOINS qu'on y met, au chiffre qu'elle affiche.
"""

import random

import pytest

from app import videopoker as vp


def c(rang, couleur):
    """Une carte : `rang` dans RANGS (« 10 », « V », « A »), `couleur` dans COULEURS."""
    return vp.COULEURS.index(couleur) * 13 + vp.RANGS.index(rang)


@pytest.mark.parametrize("main, attendu", [
    ([c("10", "coeur"), c("V", "coeur"), c("D", "coeur"), c("R", "coeur"), c("A", "coeur")], "quinte_flush_royale"),
    ([c("5", "pique"), c("6", "pique"), c("7", "pique"), c("8", "pique"), c("9", "pique")], "quinte_flush"),
    ([c("A", "pique"), c("2", "pique"), c("3", "pique"), c("4", "pique"), c("5", "pique")], "quinte_flush"),
    ([c("7", "pique"), c("7", "coeur"), c("7", "carreau"), c("7", "trefle"), c("2", "pique")], "carre"),
    ([c("7", "pique"), c("7", "coeur"), c("7", "carreau"), c("2", "trefle"), c("2", "pique")], "main_pleine"),
    ([c("2", "carreau"), c("5", "carreau"), c("9", "carreau"), c("V", "carreau"), c("A", "carreau")], "couleur"),
    ([c("A", "pique"), c("2", "coeur"), c("3", "pique"), c("4", "pique"), c("5", "pique")], "quinte"),
    ([c("10", "pique"), c("V", "coeur"), c("D", "pique"), c("R", "pique"), c("A", "pique")], "quinte"),
    ([c("4", "pique"), c("4", "coeur"), c("4", "carreau"), c("9", "trefle"), c("2", "pique")], "brelan"),
    ([c("4", "pique"), c("4", "coeur"), c("9", "carreau"), c("9", "trefle"), c("2", "pique")], "deux_paires"),
    ([c("V", "pique"), c("V", "coeur"), c("9", "carreau"), c("3", "trefle"), c("2", "pique")], "valets"),
    ([c("10", "pique"), c("10", "coeur"), c("9", "carreau"), c("3", "trefle"), c("2", "pique")], None),
    ([c("R", "pique"), c("A", "coeur"), c("2", "carreau"), c("3", "trefle"), c("4", "pique")], None),
])
def test_une_main_s_evalue_comme_au_poker(main, attendu):
    """⚠️ La roue (A-2-3-4-5) est une quinte ; une paire de dix ne paie pas — valets ou mieux."""
    assert vp.evaluer(main) == attendu


def test_la_table_va_de_la_meilleure_main_a_la_plus_petite():
    paies = [g["paie"] for g in vp.GAINS]
    assert paies == sorted(paies, reverse=True) and len(set(paies)) == len(paies)
    assert {g["slug"] for g in vp.GAINS} == {
        "quinte_flush_royale", "quinte_flush", "carre", "main_pleine", "couleur", "quinte", "brelan",
        "deux_paires", "valets"}
    assert vp.GAINS[-1]["paie"] == 1, "la plus petite main rend la mise : elle ne gagne rien"
    assert all(len(g["nom"]) <= 26 for g in vp.GAINS), "un nom de main tient sur une ligne du menu"


def garder(main):
    """La stratégie d'un habitué : les indices des cartes qu'il garde."""
    if vp.paie(main) >= 4:
        return [0, 1, 2, 3, 4]
    rangs = [carte % 13 for carte in main]
    coul = [carte // 13 for carte in main]
    compte = {}
    for r in rangs:
        compte[r] = compte.get(r, 0) + 1
    # Quatre à la royale.
    for s in range(4):
        hauts = [i for i in range(5) if coul[i] == s and rangs[i] >= 8]
        if len(hauts) >= 4:
            return hauts[:4]
    # Une main qui paie déjà : ses paires, son brelan.
    if vp.paie(main) >= 1:
        return [i for i in range(5) if compte[rangs[i]] >= 2]
    # Quatre à la couleur.
    for s in range(4):
        idx = [i for i in range(5) if coul[i] == s]
        if len(idx) == 4:
            return idx
    # Une petite paire.
    if 2 in compte.values():
        return [i for i in range(5) if compte[rangs[i]] == 2]
    # Quatre à la quinte.
    for bas in range(0, 10):
        garde, vus = [], set()
        for i in range(5):
            if bas <= rangs[i] < bas + 5 and rangs[i] not in vus:
                vus.add(rangs[i])
                garde.append(i)
        if len(garde) == 4:
            return garde
    # Les deux plus petites figures (valet ou mieux).
    hauts = sorted([i for i in range(5) if rangs[i] >= vp.VALET], key=lambda i: rangs[i])
    return hauts[:2]


def mesurer(n, graine=1):
    """Le retour moyen, en pour cent, sur `n` mains jouées par l'habitué."""
    rng = random.Random(graine)
    rendu = 0
    for _ in range(n):
        paquet = list(range(52))
        rng.shuffle(paquet)
        main, garde, k, finale = paquet[:5], garder(paquet[:5]), 5, []
        for i in range(5):
            if i in garde:
                finale.append(main[i])
            else:
                finale.append(paquet[k])
                k += 1
        rendu += vp.paie(finale)
    return rendu / n * 100


def test_la_maison_gagne_au_chiffre_qu_elle_affiche():
    """⚠️ LE CHIFFRE AFFICHÉ EST MESURÉ, PAS PROMIS. Deux cent mille mains jouées par un habitué
    (qui garde ses paires, tire à la couleur, à la quinte ouverte et aux valets) : le retour reste
    sous 100 % — la machine ne paie pas mieux qu'un boulot — et à deux points de ce qu'elle
    affiche. (La table 6/5 à une pièce reste sous 96 % même jouée à la perfection.)"""
    retour = mesurer(200_000, graine=7)
    assert retour < 100, f"la machine rend {retour:.1f} % : elle paie mieux qu'un boulot"
    assert abs(retour - vp.RETOUR_AFFICHE) <= 2, f"elle affiche {vp.RETOUR_AFFICHE} %, et rend {retour:.1f} %"


def test_une_limite_par_jour():
    assert 0 < vp.MAINS_PAR_JOUR <= 60
    assert vp.MISE * vp.MAINS_PAR_JOUR * (vp.RETOUR_AFFICHE / 100) < vp.MISE * vp.MAINS_PAR_JOUR
