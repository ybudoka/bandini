"""L'année de Baie-des-Brumes (`app/calendrier.py`, `static/js/calendrier.js`) : quarante jours, douze mois
dans l'ordre, quatre saisons, la même année des deux côtés."""

from app import calendrier, definitions


def test_douze_mois_dans_l_ordre_et_chacun_a_ses_jours():
    debuts = [d for _, d in calendrier.MOIS]
    assert len(debuts) == 12 and debuts[0] == 1 and debuts == sorted(set(debuts))
    fins = debuts[1:] + [calendrier.ANNEE + 1]
    assert all(3 <= f - d <= 4 for d, f in zip(debuts, fins)), "un mois de moins de trois jours ne se vit pas"
    assert set(calendrier.SAISONS) == {m for m, _ in calendrier.MOIS}
    assert set(calendrier.SAISONS.values()) == {"hiver", "printemps", "ete", "automne"}


def test_les_dates_tombent_dans_leur_mois():
    assert calendrier.mois(calendrier.DATES["saint_jean"]) == "juin"
    assert calendrier.mois(calendrier.DATES["demenagement"]) == "juillet"
    assert calendrier.mois(calendrier.DATES["noel"]) == "decembre"
    assert calendrier.saison(1) == "hiver" and calendrier.saison(1 + calendrier.ANNEE) == "hiver"
    assert calendrier.saison(calendrier.DATES["saint_jean"]) == "ete"


def test_la_meme_annee_des_deux_cotes(banc):
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const C = L.Calendrier, out = [];
        for (let j = 1; j <= 85; j++) out.push([C.mois(j), C.saison(j)]);
        return out;
    }""")
    assert r == [[calendrier.mois(j), calendrier.saison(j)] for j in range(1, 86)]
    assert definitions.assembler()["calendrier"] == calendrier.pour_le_navigateur()
