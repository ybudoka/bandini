"""Le cuivre du départ après les voix (`docs/jalons/le-cuivre-du-depart-apres-les-voix.md`) : le son qui lance une
mission sonne quand plus personne ne parle — après l'intro, après la réplique `pendant` du premier objectif, après la
dernière voix ; une fois, et jamais retenu pour toujours."""

PRELUDE = """
    L.Jeu.commencer(); while (L.B.menu) L.Hud.fermerMenu();
    L.B.partie.jour = 22; L.B.partie.heure = 13 / 24;
    L.B.joueur.intouchable = true;
    L.B.partie.missionsFaites.e01 = 1;
    const cuivres = []; const sfx = L.Son.SFX.mission;
    L.Son.SFX.mission = function () { cuivres.push(image); return sfx.apply(this, arguments); };
    let image = 0;
"""


def test_le_cuivre_sonne_apres_la_replique_qui_suit_l_intro(banc):
    """e02 : Ti-Paul finit son intro, puis dit sa réplique du premier objectif (« Douce, douce! ») — le cuivre vient
    après elle, pas entre les deux."""
    r = banc("""function (L, o) {""" + PRELUDE + """
        L.Histoire.demarrer('e02');
        let derniereReplique = -1, pendantVu = false;
        for (image = 1; image < 4000; image++) {
            o.frame(1);
            const c = L.B.cinema;
            if (c && c.mission === 'e02') { derniereReplique = image; if (c.partie === 'pendant') pendantVu = true; }
            if (L.B.scene) derniereReplique = image;
            if (cuivres.length && image > cuivres[0] + 120) break;
        }
        return { cuivres: cuivres, derniereReplique: derniereReplique, pendantVu: pendantVu, mission: !!L.B.partie.mission };
    }""")
    assert r["mission"] and r["pendantVu"], f"la réplique du premier objectif ne s'est pas dite : {r}"
    assert len(r["cuivres"]) == 1, f"le cuivre doit sonner une fois : {r}"
    assert r["cuivres"][0] > r["derniereReplique"], f"le cuivre sonne pendant que le donneur parle : {r}"


def test_le_cuivre_attend_qu_une_voix_finisse_mais_pas_pour_toujours(banc):
    r = banc("""function (L, o) {""" + PRELUDE + """
        L.Histoire.commencer('e02', true);
        L.B.mission.pendant = null; L.B.cinema = null; L.B.scene = null;
        const V = L.Son.Voix;
        // Une voix joue encore : le cuivre attend.
        V.enCours = { source: {}, slug: 'une-voix' };
        L.B.mission.cuivre = L.B.t + 1;
        for (image = 1; image <= 60; image++) L.Histoire.majCuivre(), L.B.t++;
        const pendant = cuivres.length;
        V.enCours = null;
        L.Histoire.majCuivre();
        const apres = cuivres.length;
        // Une voix qui ne finit jamais ne le retient pas pour toujours.
        V.enCours = { source: {}, slug: 'une-voix' };
        L.B.mission.cuivre = L.B.t + 1;
        let t = 0;
        for (; t < 2000 && cuivres.length === apres; t++) { L.Histoire.majCuivre(); L.B.t++; }
        V.enCours = null;
        // Une réplique sans mp3, restée « attendue », ne le retient pas.
        V.attendue = { slug: 'pas-de-fichier-pour-moi', options: null };
        L.B.mission.cuivre = L.B.t + 1;
        const avantSansFichier = cuivres.length;
        L.Histoire.majCuivre();
        V.attendue = null;
        return { pendant: pendant, apres: apres, delai: t, sansFichier: cuivres.length - avantSansFichier };
    }""")
    assert r["pendant"] == 0 and r["apres"] == 1, r
    assert 600 <= r["delai"] <= 1000, f"une voix qui ne finit pas retient le cuivre trop ou pas assez : {r}"
    assert r["sansFichier"] == 1, r
