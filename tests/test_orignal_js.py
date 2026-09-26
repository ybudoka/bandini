"""L'orignal de La Pointe, au banc (docs/jalons/l-orignal-de-la-pointe.md).

Une bête rare et énorme sur les sentiers du bois de La Pointe, la nuit : elle y naît et y marche ;
elle se fige dans les phares ; le klaxon la fait fuir ; la frapper coûte au char bien plus qu'un
mur, et le Clairon en fait sa une le lendemain. Et rien de tout ça ne tire `B.rng()`.
"""

from app import pietons

#: Une nuit qui a son orignal, le joueur à 300 px de sa tuile (dans la bulle, hors de l'écran), et
#: les images qu'il faut pour qu'il naisse.
NUIT = """
  function uneNuitAvecOrignal(L, o) {
    const B = L.B, E = L.Entites, p = B.partie;
    let soir = null;
    for (let n = 1; n < 80 && !soir; n++) { p.jour = n; p.heure = 0.9; soir = E.orignalDeLaNuit(); }
    const x = soir.tuile[0] * 16 + 8, y = soir.tuile[1] * 16 + 8;
    B.joueur.x = x - 300; B.joueur.y = y; L.Monde.centrerCamera(B.joueur.x, B.joueur.y); L.Entites.indexer();
    for (let k = 0; k < 61 && !B.orignal; k++) o.frame(1);
    return soir;
  }
  function surUnSentier(L, x, y) {
    const tx = Math.floor(x / 16), ty = Math.floor(y / 16);
    return L.Monde.carte.def.chemins_des_bois.some(function (t) { return Math.abs(t[0] - tx) <= 1 && Math.abs(t[1] - ty) <= 1; });
  }
"""


def test_il_nait_la_nuit_sur_un_sentier_du_bois_et_y_marche(banc):
    """Une nuit sur trois environ (à l'empreinte du jour), sur un sentier du bois de La Pointe ; il
    y va au pas, d'une tuile de sentier à l'autre. Pas le jour, et pas deux fois la même nuit."""
    r = banc("function (L, o) {" + NUIT + """
        L.Jeu.commencer();
        const B = L.B, E = L.Entites, p = B.partie;
        let nuits = 0;
        for (let n = 1; n <= 300; n++) { p.jour = n; p.heure = 0.9; if (E.orignalDeLaNuit()) nuits++; }
        const soir = uneNuitAvecOrignal(L, o);
        const o1 = B.orignal;
        const ne = o1 ? { x: o1.x, y: o1.y, sentier: surUnSentier(L, o1.x, o1.y) } : null;
        const hors = [];
        for (let k = 0; k < 900 && B.orignal; k++) { o.frame(1); if (k % 30 === 0 && !surUnSentier(L, B.orignal.x, B.orignal.y)) hors.push(k); }
        const a_marche = B.orignal ? Math.round(Math.hypot(B.orignal.x - ne.x, B.orignal.y - ne.y)) : null;
        // Le jour : personne.
        L.Entites.retirer(B.orignal); B.orignal = null; p.orignalVu = null; p.heure = 0.5;
        for (let k = 0; k < 61; k++) o.frame(1);
        return { nuits: nuits, ne: ne, hors: hors, marche: a_marche, jour: !!B.orignal, vu: p.orignalVu };
    }""")
    assert 60 < r["nuits"] < 150, f"{r['nuits']} nuits sur 300 : pas une nuit sur trois"
    assert r["ne"] and r["ne"]["sentier"], r
    assert r["hors"] == [], f"il a quitté les sentiers : {r['hors']}"
    assert r["marche"] and r["marche"] > 16, "il ne marche pas"
    assert not r["jour"], "un orignal en plein jour"


def test_ni_sa_venue_ni_ses_pas_ne_tirent_un_de_du_jeu(banc):
    """⚠️ La règle du plan : sa venue est une règle d'horaire, pas un tirage. Cent images de
    l'orignal (sa naissance comprise), appelées seules, ne changent pas le tirage suivant."""
    r = banc("function (L, o) {" + NUIT + """
        L.Jeu.commencer();
        const B = L.B, E = L.Entites, p = B.partie;
        let soir = null;
        for (let n = 1; n < 80 && !soir; n++) { p.jour = n; p.heure = 0.9; soir = E.orignalDeLaNuit(); }
        B.joueur.x = soir.tuile[0] * 16 + 8 - 300; B.joueur.y = soir.tuile[1] * 16 + 8; L.Monde.centrerCamera(B.joueur.x, B.joueur.y);
        L.graine(4);
        const temoin = [B.rng(), B.rng()];
        L.graine(4);
        for (let k = 0; k < 400; k++) { B.t++; E.majOrignal(); }
        return { ne: !!B.orignal, apres: [B.rng(), B.rng()], temoin: temoin };
    }""")
    assert r["ne"], "l'orignal n'est pas né"
    assert r["apres"] == r["temoin"], "l'orignal a tiré au dé du jeu"


def test_il_se_fige_dans_les_phares_et_fuit_au_klaxon(banc):
    """Un char qui roule vers lui, tout près, la nuit : il ne bouge plus. Un coup de klaxon : il
    détale, et s'efface une fois loin."""
    r = banc("function (L, o) {" + NUIT + """
        L.Jeu.commencer();
        const B = L.B, j = B.joueur;
        uneNuitAvecOrignal(L, o);
        const bete = B.orignal;
        const v = o.char('auto', 0, 0, 0);
        L.Vehicules.monter(j, v);
        v.x = bete.x - 70; v.y = bete.y; v.angle = 0; v.vx = 1; v.vy = 0; v.vitesse = 1;
        L.Entites.majOrignal();
        const etat = bete.orignal.etat;
        v.vx = 0; v.vy = 0; v.vitesse = 0;
        const x0 = bete.x, y0 = bete.y;
        for (let k = 0; k < 120; k++) L.Entites.majOrignal();
        const immobile = bete.x === x0 && bete.y === y0;
        v.klaxonT = 29; L.Entites.majOrignal();
        const fuit = bete.orignal.etat;
        for (let k = 0; k < 60; k++) L.Entites.majOrignal();
        const loin = Math.round(Math.hypot(bete.x - x0, bete.y - y0));
        return { etat: etat, immobile: immobile, fuit: fuit, loin: loin };
    }""")
    assert r["etat"] == "fige", r
    assert r["immobile"], "figé dans les phares, il bouge encore"
    assert r["fuit"] == "fuit", r
    assert r["loin"] > 60, r


def test_le_frapper_coute_au_char_plus_qu_un_mur_et_fait_la_une(banc):
    """Le choc : le char y laisse la plus grande part de sa vie (un mur, à la même vitesse, en
    prend une fraction), la bête repart, et le lendemain matin le Clairon titre dessus."""
    r = banc("function (L, o) {" + NUIT + """
        L.Jeu.commencer();
        const B = L.B, j = B.joueur, p = B.partie;
        uneNuitAvecOrignal(L, o);
        const bete = B.orignal;
        bete.orignal.etat = 'fige';
        const v = o.char('auto', 0, 0, 0);
        L.Vehicules.monter(j, v);
        v.x = bete.x - 40; v.y = bete.y; v.angle = 0;
        L.Entites.indexer();
        const vie = v.vie;
        let k = 0;
        o.touche('KeyW');
        for (; k < 120 && !bete.orignal.choc; k++) o.frame(1);
        o.relacher('KeyW');
        const perdu = vie - v.vie;
        p.jour += 1; L.Missions.nouveauJour();
        return { choc: !!bete.orignal.choc, perdu: perdu, vieMax: v.vieMax, fuit: bete.orignal.etat,
                 une: p.derniereManchette && p.derniereManchette.slug };
    }""")
    assert r["choc"], "le char ne l'a pas touché"
    assert r["perdu"] >= round(r["vieMax"] * pietons.ORIGNAL["degats"]) - 1, r
    assert r["perdu"] > 3 * 7, "un mur, à cette vitesse, en coûte autant"
    assert r["fuit"] == "fuit"
    assert r["une"] == "orignal", r
