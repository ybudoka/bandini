"""Les incendies (P4, « le pompier volontaire ») — la règle et ses candidats.

⚠️ Le feu se déclare sur une façade qui donne sur du marchable : le pompier
doit pouvoir s'en approcher à l'extincteur. Et il ne brûle jamais une cour de
gang ni un lieu garanti — on ne brûle pas ce qu'une mission protège.
"""

from app import carte, incendies


def test_la_regle_tient_ses_bornes():
    r = incendies.REGLE
    assert 0 < r["chance_par_heure"] < 1
    assert 0 < r["minutes"] < 60, "un feu ne déborde pas sur l'heure suivante"
    assert r["prime"] > 0
    assert r["ecart_min"] >= 1
    assert r["max_candidats"] >= 1


def test_la_prime_ne_fait_pas_de_la_ville_un_salaire():
    """Éteindre un feu paie, mais pas mieux que le taxi à l'heure : sinon le
    feu devient LE boulot, et la fiche « aucune activité ne paie mieux qu'une
    mission » est trahie."""
    from app import economie

    taxi = economie.gain_boulot(economie.BOULOTS["taxi"])
    # Une intervention par « minutes » (chrono d'arrivée) : ce qu'elle vaut à la
    # chaîne, rapporte moins que le taxi fait en ce temps.
    par_heure = incendies.REGLE["prime"] * (60 / incendies.REGLE["minutes"])
    assert par_heure < taxi * 4, "le feu paie mieux que le boulot le plus riche"


def test_des_candidats_sur_du_marchable_et_jamais_un_lieu_intouchable():
    ville = carte.generer()
    fronts = incendies.candidats(ville)
    sol = ville["sol"]
    assert fronts, "la ville n'offre aucune façade où un feu peut se déclarer"

    # Chaque façade donne sur du marchable (on s'y tient pour éteindre).
    for f in fronts:
        assert carte.marchable(sol[f["y"] + 1][f["x"]]), (
            f"la façade ({f['x']},{f['y']}) ne donne pas sur du marchable"
        )

    # Jamais dans une cour de gang.
    gang = {(tx, ty) for z in ville["zones"] if z.get("gang")
            for ty in range(z["y"], z["y"] + z["h"]) for tx in range(z["x"], z["x"] + z["l"])}
    for f in fronts:
        assert (f["x"], f["y"]) not in gang, "un feu dans une cour de gang"

    # Jamais sur (ni à un pas de) la façade d'un lieu garanti.
    gardes = {(p["x"], p["y"]) for p in ville["points_interet"]}
    for f in fronts:
        for dy in (-1, 0, 1):
            for dx in (-1, 0, 1):
                assert (f["x"] + dx, f["y"] + dy) not in gardes, "un feu sur la planque ou un lieu garanti"


def test_l_incendie_voyage_dans_le_paquet():
    ville = carte.generer()
    assert "incendies" in ville
    assert set(ville["incendies"]) == {"regle", "facades"}
    assert ville["incendies"]["regle"]["prime"] == incendies.REGLE["prime"]
    assert ville["incendies"]["facades"] == incendies.candidats(ville)