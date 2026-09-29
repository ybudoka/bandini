"""L'Halloween (`app/halloween.py`) : le 31 octobre dans l'année du jeu, et ce qui se passe ce soir-là —
des données seulement, le navigateur en tire le décor, les déguisés et la maison hantée."""

from app import calendrier, halloween


def test_le_31_octobre_est_dans_octobre():
    assert calendrier.mois(calendrier.DATES["halloween"]) == "octobre"
    assert calendrier.mois(calendrier.DATES["halloween"] + 1) == "novembre", "l'Halloween est le dernier jour d'octobre"
    assert halloween.JOUR == calendrier.DATES["halloween"]


def test_les_heures_et_les_parts_se_tiennent():
    assert 0 < halloween.CITROUILLES["part"] < 0.6
    assert 0 < halloween.DEGUISES["part"] < 0.6 and len(halloween.DEGUISES["costumes"]) >= 4
    assert 12 <= halloween.LUMIERES["des_h"] <= halloween.MAISON["des_h"] < halloween.MAISON["jusqu_h"] <= 24
    assert 1 <= halloween.ENFANTS["bandes_max"] <= 6, "des bandes d'enfants sans borne : le rythme"
    assert halloween.MAISON["prime"] > 0


def test_dans_le_paquet(paquet):
    assert paquet["halloween"] == halloween.pour_le_navigateur()


def test_les_murmures_ont_leur_jeu_et_leur_voix_a_eux():
    from app import audio, interpretation
    assert halloween.VOIX in audio.VOIX_RESERVEES, "la voix de la maison hantée n'est pas réservée"
    assert audio.voix_partagees_a_tort() == []
    slugs = {v["slug"] for v in audio.voix_halloween()}
    assert slugs == {f"halloween-{m['cle']}" for m in halloween.MURMURES}
    for m in halloween.MURMURES:
        assert interpretation.JEU[f"halloween-{m['cle']}"] == m["jeu"]


def test_la_musique_d_halloween_a_son_jumeau_en_notes():
    from app import audio, musique
    assert "halloween" in {p["slug"] for p in audio.MUSIQUES}
    assert "halloween" in {m["slug"] for m in musique.exporter()}
