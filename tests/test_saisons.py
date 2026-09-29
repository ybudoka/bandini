"""Les saisons de Baie-des-Brumes (`app/saisons.py`) : six palettes, les images-clés de l'année,
la lumière — des données seulement ; le navigateur en tire la palette du moment."""

from app import calendrier, saisons


def test_les_cles_couvrent_l_annee_dans_l_ordre():
    jours = [j for j, _ in saisons.CLES]
    assert jours[0] == 1 and jours[-1] == calendrier.ANNEE + 1
    assert jours == sorted(jours) and len(set(jours)) == len(jours)
    assert saisons.CLES[0][1] == saisons.CLES[-1][1] == "hiver", "l'année finit comme elle commence"
    assert {s for _, s in saisons.CLES} == set(saisons.PALETTES)


def test_une_transition_dure_au_plus_deux_jours():
    for (a, pa), (b, pb) in zip(saisons.CLES, saisons.CLES[1:]):
        if pa != pb:
            assert 1 <= b - a <= 2, f"{pa} → {pb} en {b - a} jours"


def test_chaque_palette_a_les_memes_couleurs():
    formes = {s: {k: sorted(v) if isinstance(v, dict) else None for k, v in p.items()}
              for s, p in saisons.PALETTES.items()}
    assert len({repr(f) for f in formes.values()}) == 1
    for p in saisons.PALETTES.values():
        assert len(p["arbre"]["teintes"]) == 3 and all(len(t) == 3 for t in p["arbre"]["teintes"])
        assert 0 <= p["arbre"]["feuillage"] <= 1 and 0 <= p["neige"] <= 1


def test_l_octobre_est_rouge_et_janvier_blanc():
    a = saisons.PALETTES["automne"]["arbre"]["teintes"]
    assert any(int(t[0][1:3], 16) > 2 * int(t[0][3:5], 16) for t in a), "pas un érable rouge"
    assert saisons.palette_du_jour(33) == "automne", "l'Halloween est en plein automne"
    assert saisons.palette_du_jour(1) == "hiver" and saisons.PALETTES["hiver"]["neige"] > 0.5
    assert saisons.PALETTES["hiver"]["arbre"]["feuillage"] == 0


def test_dans_le_paquet(paquet):
    assert paquet["saisons"] == saisons.pour_le_navigateur()
