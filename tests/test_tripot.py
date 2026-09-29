"""Le tripot du sous-sol du Dragon d'or : la barbotte du Pouce, ses dés pipés, sa porte gardée
(docs/jalons/le-casino-du-petit-canton.md, vague 4 ; `app/tripot.py`).

Ce qui se CALCULE (les trente-six paires, les deux cent vingt-cinq des pipés) et ce qui se MESURE (des milliers de
jours de barbotte, quatre façons de jouer), et la salle : sous le casino sans le grossir, derrière sa porte."""

import random
from collections import deque

import pytest

from app import carte, casino, missions, tripot


def test_la_barbotte_est_juste_un_sur_deux_et_le_pouce_vit_de_sa_piastre():
    """Quatre coups de chaque côté, cinq chances sur trente-six chacun : honnête, la barbotte est pile ou face, et
    la piastre du Pouce (cinq pour cent du gain) fait tout le retour de la maison — 97,5 %, affiché 97."""
    compte = {"pour": 0, "contre": 0, None: 0}
    for a in range(1, 7):
        for b in range(1, 7):
            compte[tripot.coup(a, b)] += 1
    assert compte == {"pour": 5, "contre": 5, None: 26}
    assert tripot.coup(6, 5) == tripot.coup(5, 6) == "pour" and tripot.coup(2, 1) == "contre"
    for pari in tripot.COTES:
        assert tripot.chance_du_cote(pari, None) == pytest.approx(0.5)
        assert tripot.retour(pari, None) == pytest.approx(0.975)
    assert tripot.RETOUR == int(tripot.retour("pour", None) * 100), "l'affiché ne promet jamais plus que la table"
    # Des mises rondes : la piastre tombe sur un dollar rond, et un coup gagné rend 1,95 fois la mise.
    for mise in tripot.MISES:
        assert (mise * round(tripot.PIASTRE * 100)) % 100 == 0
        assert tripot.gain("pour", "pour", mise) == mise * 195 // 100
        assert tripot.gain("pour", "contre", mise) == 0 and tripot.gain("pour", None, mise) == mise
    assert min(tripot.MISES) >= 100 and max(tripot.MISES) == 1000, "en bas, on mise dix fois ce qu'on mise en haut"


def test_les_des_pipes_jouent_contre_ton_cote_et_pour_qui_change_de_cote():
    """CALCULÉ : contre ton côté, les pipés font sortir le leur sept fois sur dix (la table rend 60 %) ; qui change
    de côté une fois qu'ils sont posés les a pour lui (135 %). Les deux paires sont le miroir l'une de l'autre."""
    for pari in tripot.COTES:
        autre = "contre" if pari == "pour" else "pour"
        poids = tripot.poids_contre(pari)
        assert tripot.chance_du_cote(pari, poids) == pytest.approx(20 / 65)
        assert tripot.retour(pari, poids) == pytest.approx(0.6)
        assert tripot.retour(autre, poids) == pytest.approx(1.35)
    assert tuple(tripot.PIPES["pour"][i] for i in (1, 0, 3, 2, 5, 4)) != tripot.PIPES["contre"]
    assert {tripot.PIPES["pour"][i] + tripot.PIPES["contre"][i] for i in range(6)} == {5}
    assert sum(tripot.PIPES["pour"]) == sum(tripot.PIPES["contre"]) == 15
    # Sous le seuil, jamais ; au seuil et au-delà, une fois sur `chance`.
    assert not any(tripot.pipe(m, 0.0) for m in tripot.MISES if m < tripot.PIPES["seuil"])
    assert all(tripot.pipe(m, 0.0) and not tripot.pipe(m, 0.99) for m in tripot.MISES if m >= tripot.PIPES["seuil"])


def test_une_face_pipee_suit_ses_poids():
    """Un tirage uniforme tombe sur chaque face au prorata de son poids (dix mille tirages réguliers)."""
    for poids in (tripot.PIPES["pour"], tripot.PIPES["contre"]):
        n = 15000
        vus = [0] * 6
        for k in range(n):
            vus[tripot.face((k + 0.5) / n, poids) - 1] += 1
        assert vus == [n * p // 15 for p in poids]
    assert [tripot.face((k + 0.5) / 6, None) for k in range(6)] == [1, 2, 3, 4, 5, 6]


def _mesure(strategie, mise, graines=(1, 2, 3), jours=1500):
    mise_t = rendu = sorties = barres = coups = 0
    for g in graines:
        r = tripot.jouer_des_jours(random.Random(g), jours, mise, strategie)
        mise_t += r["mise"]
        rendu += r["rendu"]
        sorties += r["sorties"]
        barres += r["barres"]
        coups += r["coups"]
    return {"retour": rendu / mise_t, "sorties": sorties, "barres": barres, "coups": coups,
            "net_par_jour": (rendu - mise_t) / (jours * len(graines))}


def test_la_mesure_quatre_facons_de_jouer_au_sous_sol():
    """MESURÉ sur 4 500 jours de vingt coups (trois graines), comme le jeu les joue :
    - qui mise sous le seuil (200 $) joue une barbotte honnête : 97,5 % ;
    - le NAÏF qui mise 1 000 $ et lance quoi qu'il voie : environ 75 % — la maison triche, et ça coûte cher ;
    - qui DÉNONCE les pipés : sa mise rendue et la paix du jour — il revient au-dessus de la barbotte honnête, mais
      le Pouce s'en souvient, et il finit dehors de temps en temps ;
    - qui CHANGE DE CÔTÉ sur les pipés : il bat la maison (plus de 100 %) tant que le Pouce ne le sort pas — et il le
      sort, souvent : la semaine barrée est ce qui garde l'économie debout."""
    prudent = _mesure("naif", 200)
    naif = _mesure("naif", 1000)
    denonce = _mesure("denonce", 1000)
    retourne = _mesure("retourne", 1000)
    assert 0.965 < prudent["retour"] < 0.985 and prudent["sorties"] == 0
    assert 0.72 < naif["retour"] < 0.78 and naif["sorties"] == 0
    assert 0.98 < denonce["retour"] < 1.0, denonce
    assert retourne["retour"] > 1.0, retourne
    assert retourne["sorties"] > 50 and retourne["barres"] > 1000, "le Pouce voit le manège, et le sort"
    # ⚠️ L'ÉCONOMIE : même le retourneur ne gagne pas plus qu'un bon boulot — quelques centaines par jour, en moyenne,
    # quand on compte les jours où l'escalier lui est fermé.
    assert 0 < retourne["net_par_jour"] < 600, retourne


# --- La salle et sa porte ---------------------------------------------------------------------------------

def test_le_tripot_est_sous_le_casino_sans_le_grossir():
    """⚠️ Le bâtiment se taille à la plus grande pièce de sa suite : le tripot plus grand que la grande salle, et le
    Dragon d'or grandissait — la ville glissait. L'escalier monte et descend ; la salle a sa table, son Pouce et ses
    gros bras, et elle reste la pièce de la bande (`nord_`)."""
    salle, cave = casino.PIECE, tripot.PIECE
    assert cave["slug"].startswith("nord_")
    assert cave["largeur"] <= salle["largeur"] and cave["hauteur"] <= salle["hauteur"]
    pieces = {salle["slug"]: salle, cave["slug"]: cave}
    assert carte.suite_de(salle["slug"], pieces) == sorted([salle["slug"], cave["slug"]])
    assert carte.mesures_de_la_suite(salle["slug"], pieces) == carte.mesures_de(salle)
    descend = [p for p in salle["points"] if p["type"] == "escalier"]
    monte = [p for p in cave["points"] if p["type"] == "escalier"]
    assert [p["vers"] for p in descend] == [cave["slug"]] and [p["vers"] for p in monte] == [salle["slug"]]
    assert [p["type"] for p in cave["points"]].count("barbotte") == 1
    gens = [g["qui"] for g in cave["gens"]]
    assert gens.count("pouce") == 1 and gens.count("gros_bras") == 2
    assert [g["qui"] for g in salle["gens"]].count("gros_bras") == 1, "un gros bras garde la porte d'en haut"
    # Irène au bout du bar, sur un point à elle.
    assert any(p["type"] == "irene" for p in salle["points"])
    assert missions.personnage("irene")["ou"] == "point:irene"


def _atteint(piece, depart, murs=frozenset()):
    sol = piece["sol"]
    vus, file = {depart}, deque([depart])
    while file:
        x, y = file.popleft()
        for nx, ny in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
            if (nx, ny) in vus or (nx, ny) in murs or not carte.marchable(sol[ny][nx]):
                continue
            vus.add((nx, ny))
            file.append((nx, ny))
    return vus


def test_la_porte_du_sous_sol_est_une_barriere_de_la_piece_qui_garde_l_escalier():
    """La porte (`tripot.PORTE`) est au format de `carte.BARRIERES` : une condition `apres` qui nomme une mission du
    catalogue, une raison en majuscules, rien à forcer. Et elle garde VRAIMENT l'escalier : sans elle, on y arrive ;
    avec elle, pas une tuile d'où l'on touche la marche."""
    b = casino.PIECE["barrieres"][0]
    assert b == tripot.PORTE and b["decor"] == "porte_tripot" and b["forcer"] is None and b["plein"]
    assert set(b["arrete"]) == {"pieton", "vehicule"} and list(b["condition"]) == ["apres"]
    assert b["condition"]["apres"] in {m["slug"] for m in missions.CATALOGUE}
    assert b["raison"] == b["raison"].upper() and 0 < len(b["raison"]) <= 40
    salle = casino.PIECE
    assert carte.marchable(salle["sol"][b["y"]][b["x"]]), "la porte est sur le plancher : ouverte, on y passe"
    marche = next(p for p in salle["points"] if p["type"] == "escalier")
    entree = (salle["apparition"]["x"], salle["apparition"]["y"])
    pres = {(marche["x"] + dx, marche["y"] + dy) for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))}
    assert _atteint(salle, entree) & pres, "sans la porte, on atteint l'escalier"
    assert not _atteint(salle, entree, {(b["x"], b["y"])}) & pres, "la porte fermée ne garde rien"


def test_la_ville_a_le_tripot_et_le_casino_garde_sa_taille(ville_du_canton):
    """Dans la ville FINIE : la pièce du tripot est là, sous le nom de la bande, l'escalier de la grande salle y
    mène, et le Dragon d'or a toujours la boîte de sa grande salle (32 × 9 de plancher)."""
    pieces = ville_du_canton["interieurs"]
    assert tripot.PIECE["slug"] in pieces and "barrieres" in pieces[casino.PIECE["slug"]]
    assert carte.mesures_de_la_suite(casino.PIECE["slug"], pieces) == (32, 9)
    assert any(p["lieu"] == casino.CASINO["slug"] for p in ville_du_canton["portes"])


@pytest.fixture(scope="module")
def ville_du_canton():
    import villes
    return villes.generer()
