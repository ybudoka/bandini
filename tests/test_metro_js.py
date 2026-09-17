"""Le métro au banc : on descend, la rame passe à son heure, on roule, on remonte ailleurs.

Demande de Martin (16 sept. 2026) : « je veux aussi un métro » — souterrain.

⚠️ **On ne fait pas attendre le banc une minute par rame.** L'horaire est une
fonction de l'heure (`Metro.etatDeLaRame`) : `REGLER` met l'heure de la partie à
`avance` images de l'arrivée d'une rame à une station.
"""

OUTILS = """
    function regler(L, station, avance) {
      const jour = L.B.defs.economie.jour_secondes * 60;
      const t = L.Autobus.tempsDeLaPartie() + L.Metro.prochaineArrivee(station) - avance;
      L.B.partie.heure = t / jour - (L.B.partie.jour - 1);
    }
    function surLeTrottoir(L, rang) {
      const s = L.Metro.donnees().stations[rang], j = L.B.joueur;
      j.x = s.sortie.x * L.TT + 8; j.y = s.sortie.y * L.TT + 8;
      L.Monde.centrerCamera(j.x, j.y);
      return s;
    }
    function allerAuPoint(L, type) {
      const q = L.B.interieur.points.find(function (p) { return p.type === type; }), j = L.B.joueur;
      j.x = q.x * L.TT + 8; j.y = q.y * L.TT + 8;
    }
    function allerALaPorte(L) {
      const s = L.B.interieur.sortie, j = L.B.joueur;
      j.x = s.x * L.TT + 8; j.y = (s.y - 1) * L.TT + 8;
    }
"""


def test_on_descend_au_metro_par_l_edicule(banc):
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        %s
        const s = surLeTrottoir(L, 1);
        o.frame(2);
        const invite = L.B.invite, argent = L.B.partie.argent;
        o.tape('KeyE', 1); o.fondu(); o.frame(2);
        return { invite: invite, piece: L.B.interieur && L.B.interieur.slug, station: L.B.metro && L.B.metro.station,
                 paye: argent - L.B.partie.argent, msg: L.B.msg, nom: s.nom };
    }""" % OUTILS)
    assert r["invite"] == "DESCENDRE AU MÉTRO — HÔPITAL — 3 $", r["invite"]
    assert r["piece"] == "metro_quai" and r["station"] == 1
    assert r["paye"] == 3
    assert r["msg"] == "STATION HÔPITAL"


def test_recherche_ou_fauche_on_ne_passe_pas_le_tourniquet(banc):
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        %s
        surLeTrottoir(L, 2);
        o.frame(2);
        L.B.recherche.etoiles = 1;
        o.tape('KeyE', 1); o.frame(40);
        const recherche = { piece: !!L.B.interieur, transition: !!L.B.transition, msg: L.B.msg };
        L.B.recherche.etoiles = 0;
        L.B.partie.argent = 2;
        o.tape('KeyE', 1); o.frame(40);
        return { recherche: recherche, fauche: { piece: !!L.B.interieur, msg: L.B.msg, argent: L.B.partie.argent } };
    }""" % OUTILS)
    assert not r["recherche"]["piece"] and not r["recherche"]["transition"]
    assert "TOURNIQUETS" in r["recherche"]["msg"]
    assert not r["fauche"]["piece"] and "PAS ASSEZ" in r["fauche"]["msg"] and r["fauche"]["argent"] == 2


def test_la_rame_passe_a_son_heure_et_on_monte(banc):
    """Pas de rame, pas d'invite — ACTION le dit, et on reste sur le quai. La rame
    entre, ouvre ses portes, et « MONTER » mène dans la voiture."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        %s
        surLeTrottoir(L, 0);
        o.frame(2);
        o.tape('KeyE', 1); o.fondu(); o.frame(2);
        regler(L, 0, 240);
        allerAuPoint(L, 'rame');
        o.frame(2);
        const avant = { aQuai: !!L.Metro.rameAQuai(0), invite: L.B.invite, enVue: !!L.Metro.rameEnVue(0) };
        o.tape('KeyE', 1); o.frame(2);
        avant.msg = L.B.msg; avant.piece = L.B.interieur.slug;
        let images = 0;
        while (!L.Metro.rameAQuai(0) && images < 600) { o.frame(1); images++; }
        const approche = images;
        o.frame(30);
        allerAuPoint(L, 'rame');
        o.frame(1);
        const pendant = { invite: L.B.invite, info: L.Metro.texteDInfo(L.B.joueur) };
        o.tape('KeyE', 1); o.fondu(); o.frame(2);
        return { avant: avant, approche: approche, pendant: pendant, piece: L.B.interieur.slug,
                 rame: L.B.metro.rame, info: L.Metro.texteDInfo(L.B.joueur) };
    }""" % OUTILS)
    assert not r["avant"]["aQuai"] and r["avant"]["invite"] is None
    assert r["avant"]["piece"] == "metro_quai" and "PAS À QUAI" in r["avant"]["msg"]
    assert 200 <= r["approche"] <= 260, f"la rame arrive en {r['approche']} images, réglée à 240"
    assert r["pendant"]["invite"] == "MONTER — PROCHAINE : HÔPITAL", r["pendant"]
    assert "RAME À QUAI" in r["pendant"]["info"]
    assert r["piece"] == "metro_rame" and r["rame"] is not None


def test_les_portes_ne_s_ouvrent_qu_en_station_et_on_remonte_ailleurs(banc):
    """On roule POUR DE VRAI : la porte de la voiture reste fermée dans le tunnel,
    s'ouvre à la station suivante sur SON quai, et l'escalier remonte à SON
    édicule. Un seul passage payé."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        %s
        surLeTrottoir(L, 3);
        o.frame(2);
        o.tape('KeyE', 1); o.fondu(); o.frame(2);
        const argent = L.B.partie.argent;
        regler(L, 3, 30);
        allerAuPoint(L, 'rame');
        let n = 0;
        while (!(L.Metro.rameAQuai(3) && L.Metro.rameAQuai(3).ecoule > 20) && n < 400) { o.frame(1); n++; }
        o.tape('KeyE', 1); o.fondu(); o.frame(2);
        const rame = L.B.metro.rame;
        n = 0;
        while (L.Metro.etatDeLaRame(rame).quai && n < 400) { o.frame(1); n++; }
        o.frame(120);
        allerALaPorte(L);
        o.frame(1);
        const tunnel = { invite: L.B.invite, info: L.Metro.texteDInfo(L.B.joueur) };
        o.tape('KeyE', 1); o.frame(3);
        tunnel.piece = L.B.interieur.slug; tunnel.transition = !!L.B.transition; tunnel.msg = L.B.msg;
        n = 0;
        while (!(L.Metro.etatDeLaRame(rame).quai && L.Metro.etatDeLaRame(rame).ecoule > 20) && n < 3000) { o.frame(1); n++; }
        allerALaPorte(L);
        o.frame(1);
        const station = { invite: L.B.invite, rang: L.Metro.etatDeLaRame(rame).station };
        o.tape('KeyE', 1); o.fondu(); o.frame(2);
        const quai = { piece: L.B.interieur.slug, station: L.B.metro.station };
        allerALaPorte(L);
        o.frame(1);
        quai.invite = L.B.invite;
        o.tape('KeyE', 1); o.fondu(); o.frame(2);
        const s = L.Metro.donnees().stations[station.rang], j = L.B.joueur;
        return { tunnel: tunnel, station: station, quai: quai, dehors: !L.B.interieur, metro: L.B.metro,
                 tuile: [Math.floor(j.x / L.TT), Math.floor(j.y / L.TT)], sortie: [s.sortie.x, s.sortie.y],
                 paye: argent - L.B.partie.argent };
    }""" % OUTILS)
    assert r["tunnel"]["invite"] is None, "une invite promet de descendre dans le tunnel"
    assert r["tunnel"]["piece"] == "metro_rame" and not r["tunnel"]["transition"]
    assert "FERMÉES" in r["tunnel"]["msg"]
    assert r["station"]["rang"] == 4, "la station d'après La Pointe, par le tunnel sous la baie"
    assert r["station"]["invite"] == "DESCENDRE — LES QUAIS", r["station"]
    assert r["quai"]["piece"] == "metro_quai" and r["quai"]["station"] == 4
    assert r["quai"]["invite"] == "REMONTER — LES QUAIS"
    assert r["dehors"] and r["metro"] is None
    assert r["tuile"] == r["sortie"], f"remonté en {r['tuile']}, l'édicule des Quais est en {r['sortie']}"
    assert r["paye"] == 0


def test_la_partie_se_sauve_a_la_station_ou_l_on_est(banc):
    """⚠️ La sauvegarde lit `B.exterieur` : descendu à Faubourg et arrivé à
    l'Hôpital, on doit se réveiller devant l'édicule de l'Hôpital."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        %s
        surLeTrottoir(L, 0);
        o.frame(2);
        o.tape('KeyE', 1); o.fondu(); o.frame(2);
        L.B.metro.station = 1;
        o.frame(2);
        L.Missions.sauvegarderPartie();
        const s = L.Metro.donnees().stations[1];
        return { tuile: [Math.floor(L.B.partie.x / L.TT), Math.floor(L.B.partie.y / L.TT)], sortie: [s.sortie.x, s.sortie.y] };
    }""" % OUTILS)
    assert r["tuile"] == r["sortie"]


def test_le_metro_ne_tire_pas_un_de_du_jeu(banc):
    """Une rame est une heure : rien ne se tire au sort sous la ville."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        %s
        surLeTrottoir(L, 0);
        o.frame(2);
        o.tape('KeyE', 1); o.fondu(); o.frame(2);
        regler(L, 0, 60);
        L.graine(5);
        const tirage = L.B.rng;
        let dansLeMetro = 0;
        L.B.rng = function () { if (String(new Error().stack).indexOf('metro.js') >= 0) dansLeMetro++; return tirage(); };
        for (let i = 0; i < 200; i++) o.frame(1);
        // ⚠️ Au bord du quai JUSTE AVANT : en 200 images, les voyageurs du quai
        // poussent le joueur de deux tuiles.
        allerAuPoint(L, 'rame');
        o.frame(1);
        o.tape('KeyE', 1); o.fondu();
        for (let i = 0; i < 1500; i++) o.frame(1);
        return { dans: dansLeMetro, piece: L.B.interieur.slug };
    }""" % OUTILS)
    assert r["piece"] == "metro_rame", "le juge n'a pas roulé"
    assert r["dans"] == 0


def test_le_quai_montre_la_rame_et_la_carte_la_ligne(banc):
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        %s
        surLeTrottoir(L, 0);
        o.frame(2);
        o.tape('KeyE', 1); o.fondu(); o.frame(2);
        regler(L, 0, -60);
        const vue = { x: L.B.cam.x, y: L.B.cam.y };
        let avant = L.B.stats.rects;
        L.Metro.dessiner(o.ctx, vue);
        const quai = L.B.stats.rects - avant;
        const d = L.Metro.donnees();
        avant = L.B.stats.rects;
        L.Metro.dessinerSurLaCarte(o.ctx, function (x, y) { return { x: Math.round(x / L.TT), y: Math.round(y / L.TT) }; });
        return { quai: quai, rameEnVue: !!L.Metro.rameEnVue(0), carte: L.B.stats.rects - avant, stations: d.stations.length };
    }""" % OUTILS)
    assert r["rameEnVue"] and r["quai"] > 10
    assert r["carte"] > 2 * r["stations"]
