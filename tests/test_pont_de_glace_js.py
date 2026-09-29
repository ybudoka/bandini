"""Le pont de glace, au banc (docs/jalons/le-pont-de-glace.md) : il n'existe que les jours de grand froid
(l'hiver, pour tout le monde) ; un char le traverse sans couler ; une coque ne le passe pas et la baie
n'en prend pas une ; au dégel un char arrêté passe au travers ; après, la baie a toute son eau."""

#: Un jour de grand froid (ou un autre), a midi ou a l'heure dite ; quelques images pour que la baie prenne.
FROID = """
  // ⚠️ Le joueur au bout ouest du chemin (a terre, sur l'ile) : un char gare LOIN du joueur, la ville
  // l'oublie (`peupler`), et le juge ne verrait rien.
  function aLHeure(L, o, jour, heure) {
    const B = L.B, d = B.defs.pont.chemin;
    if (!B.joueur.dansVehicule) { B.joueur.x = d.ouest.x * 16 + 8; B.joueur.y = d.ouest.y * 16 + 8; L.Monde.centrerCamera(B.joueur.x, B.joueur.y); }
    B.partie.jour = jour; B.partie.heure = (heure === undefined ? 10 : heure) / 24;
    for (let k = 0; k < 62; k++) o.frame(1);
  }
  function premierFroid(L) { return L.B.defs.pont.froid.jours[0]; }
  function eauDuChemin(L) {
    const c = L.Monde.carte;
    return L.Pont.tuiles().map(function (t) { return c.solide[t[1] * c.w + t[0]]; });
  }
"""


def test_la_baie_ne_prend_que_les_jours_de_grand_froid(banc):
    r = banc("function (L, o) {" + FROID + """
        L.Jeu.commencer();
        const B = L.B, f = premierFroid(L);
        const avant = eauDuChemin(L).join(',');
        aLHeure(L, o, f + 20, 10); const autreJour = !!L.Pont.pose;
        aLHeure(L, o, f, 10); const froid = eauDuChemin(L);
        aLHeure(L, o, f + B.defs.pont.froid.jours.length, 10); const apres = eauDuChemin(L).join(',');
        aLHeure(L, o, f + B.defs.calendrier.annee, 10); const anDApres = !!L.Pont.pose;
        return { avant: avant, autreJour: autreJour, glace: froid.every(function (s) { return s === 0; }),
                 apres: apres, anDApres: anDApres };
    }""")
    assert r["avant"].split(",") == ["2"] * len(r["avant"].split(",")), "le chemin n'est pas de l'eau au départ"
    assert not r["autreJour"], r
    assert r["glace"], "le jour du grand froid, la baie n'a pas pris"
    assert r["apres"] == r["avant"], "après le grand froid, la baie n'a pas retrouvé toute son eau"
    assert r["anDApres"], "le grand froid ne revient pas l'hiver suivant"


def test_un_char_traverse_jusqu_a_l_ile_sans_couler(banc):
    r = banc("function (L, o) {" + FROID + """
        L.Jeu.commencer();
        const B = L.B, j = B.joueur, V = L.Vehicules, d = B.defs.pont.chemin;
        aLHeure(L, o, premierFroid(L), 10);
        B.entites = B.entites.filter(function (e) { return e === j || !(e.type === 'vehicule' || e.type === 'pieton' || e.type === 'police'); });
        const v = V.creer('auto', d.est.x * 16 + 8, d.est.y * 16 + 8, Math.PI, { etat: 'stationne', couleur: '#888' });
        V.monter(j, v); L.Entites.indexer();
        o.touche('KeyW');
        let coule = 0, k = 0;
        for (; k < 900 && Math.floor(v.x / 16) > d.ouest.x; k++) { o.frame(1); coule = Math.max(coule, v.coule || 0); }
        o.relacher('KeyW');
        return { arrive: Math.floor(v.x / 16) <= d.ouest.x, coule: coule, images: k, etat: v.etat };
    }""")
    assert r["arrive"], f"le char n'a pas atteint l'île : {r}"
    assert r["coule"] == 0 and r["etat"] != "epave", r


def test_une_coque_ne_passe_pas_et_la_baie_ne_la_prend_pas(banc):
    """Une chaloupe posée sur le chemin : la baie attend qu'elle parte pour prendre. Partie, la glace se
    pose ; la chaloupe qui fonce dessus s'y bute."""
    r = banc("function (L, o) {" + FROID + """
        L.Jeu.commencer();
        const B = L.B, j = B.joueur, V = L.Vehicules, d = B.defs.pont.chemin;
        const t = L.Pont.tuiles()[Math.floor(L.Pont.tuiles().length / 2)];
        const coque = V.creer('chaloupe', t[0] * 16 + 8, t[1] * 16 + 8, 0, { etat: 'stationne', couleur: '#fff' })
                   || V.creer('bateau', t[0] * 16 + 8, t[1] * 16 + 8, 0, { etat: 'stationne', couleur: '#fff' });
        L.Entites.indexer();
        aLHeure(L, o, premierFroid(L), 10);
        const prise = !!L.Pont.pose;
        // Elle s'en va, au nord du chemin ; la baie prend.
        coque.y = (d.ouest.y - 4) * 16 + 8; L.Entites.indexer();
        for (let k = 0; k < 62; k++) o.frame(1);
        const apres = !!L.Pont.pose;
        // Au volant, cap au sud, droit sur la glace.
        V.monter(j, coque); coque.angle = Math.PI / 2;
        o.touche('KeyW');
        for (let k = 0; k < 240; k++) o.frame(1);
        o.relacher('KeyW');
        return { slug: coque.slug, prise: prise, apres: apres, y: coque.y, bord: (d.ouest.y - 1) * 16 };
    }""")
    assert not r["prise"], f"la baie a pris une coque dans la glace : {r}"
    assert r["apres"], r
    assert r["y"] < r["bord"] + 8, f"la coque a traversé la glace : {r}"


def test_au_degel_un_char_arrete_passe_au_travers(banc):
    r = banc("function (L, o) {" + FROID + """
        L.Jeu.commencer();
        const B = L.B, j = B.joueur, V = L.Vehicules, d = B.defs.pont.chemin, f = B.defs.pont.froid;
        const dernier = f.jours[f.jours.length - 1];
        const t = L.Pont.tuiles()[Math.floor(L.Pont.tuiles().length / 2)];
        function garer(heure) {
            aLHeure(L, o, dernier, heure);
            const v = V.creer('auto', t[0] * 16 + 8, t[1] * 16 + 8, 0, { etat: 'stationne', couleur: '#888' });
            L.Entites.indexer();
            let coule = 0;
            for (let k = 0; k < (f.craque_s + 3) * 60; k++) { o.frame(1); coule = Math.max(coule, v.coule || 0); }
            B.entites.splice(B.entites.indexOf(v), 1);
            return coule;
        }
        const matin = garer(f.degel_h - 3);
        const soir = garer(f.degel_h + 2);
        return { matin: matin, soir: soir };
    }""")
    assert r["matin"] == 0, f"avant le dégel, un char garé sur la glace a coulé : {r}"
    assert r["soir"] > 0, f"au dégel, un char arrêté n'est pas passé au travers : {r}"


def test_le_clairon_annonce_le_grand_froid(banc):
    r = banc("function (L, o) {" + FROID + """
        L.Jeu.commencer();
        const B = L.B, f = premierFroid(L);
        const l = {};
        for (const k of [-2, -1, 0, 1]) { B.partie.jour = f + k; l[k] = L.Pont.ligneDuClairon(); }
        B.partie.jour = f - 1 + 20; l.sans = L.Pont.ligneDuClairon();   // la même veille, en juin
        return l;
    }""")
    from app import pont_de_glace
    assert r["-2"] is None and r["-1"] == pont_de_glace.CLAIRON["veille"] and r["0"] == pont_de_glace.CLAIRON["pendant"], r
    assert r["1"] is None and r["sans"] is None, r
