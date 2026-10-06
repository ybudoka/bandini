"""L'année de Baie-des-Brumes (`app/calendrier.py`, `static/js/calendrier.js`) : quarante jours, douze mois
dans l'ordre, quatre saisons, la même année des deux côtés."""

from app import calendrier


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


def test_la_meme_annee_des_deux_cotes(banc, paquet):
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const C = L.Calendrier, out = [];
        for (let j = 1; j <= 85; j++) out.push([C.mois(j), C.saison(j)]);
        return out;
    }""")
    assert r == [[calendrier.mois(j), calendrier.saison(j)] for j in range(1, 86)]
    assert paquet["calendrier"] == calendrier.pour_le_navigateur()


def test_une_partie_neuve_commence_sans_neige(banc):
    """Martin, 4 oct. 2026 : « le jeu doit débuter à un moment sans neige ». Une partie neuve commence au
    jour `DEPART` (le 1er mai) ; toute sa première journée, pas un flocon, pas de neige qui tient, pas de
    banc, pas de gadoue, pas de verglas. Une vieille sauvegarde, elle, garde son jour. (Le banc commence le
    1er janvier pour les autres juges : `depart_du_jeu=True` joue le vrai départ.)"""
    assert calendrier.saison(calendrier.DEPART) != "hiver"
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const p = L.B.partie, j = p.jour, rien = [];
        for (let h = 0; h < 1; h += 1 / 48) {
            const n = { tempete: L.Neige.intensiteA(j, h), sol: L.Neige.couvertureA(j, h),
                        palette: L.Saisons.paletteA(j, h).neige || 0, banc: L.BancsDeNeige.grosseurA(j, h),
                        gadoue: L.Pluie.gadoueA(j, h), verglas: L.Verglas.intensiteA(j, h) };
            if (Object.keys(n).some(function (k) { return n[k] > 0; })) rien.push([h, n]);
        }
        return { jour: j, debut: p.chantiers.debut, mois: L.Calendrier.mois(j), neige: rien,
                 vieille: L.Sauvegarde.completer({ jour: 3 }, L.B.defs).jour };
    }""", depart_du_jeu=True)
    assert r["jour"] == r["debut"] == calendrier.DEPART and r["mois"] == "mai"
    assert r["neige"] == [], r["neige"][:3]
    assert r["vieille"] == 3
