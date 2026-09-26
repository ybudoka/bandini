"""Le temps des Fêtes, au banc (docs/jalons/le-temps-des-fetes.md) : en décembre seulement, les fenêtres et
les vitrines prennent les couleurs des guirlandes la nuit, le sapin brille sur la place, le camion livre
des dindes, et le Clairon l'annonce ; rien au dé, et tout s'en va en janvier."""

DECEMBRE = """
  function aLHeure(L, jour, h) { L.B.partie.jour = jour; L.B.partie.heure = h / 24; }
  function decembre(L) { return L.B.defs.fetes.jours[0]; }
"""


def test_les_guirlandes_en_decembre_seulement(banc):
    r = banc("function (L, o) {" + DECEMBRE + """
        L.Jeu.commencer();
        const Mo = L.Monde, B = L.B, F = L.Fetes;
        const fenetre = Mo.carte.lampes.find(function (l) { return l.sorte === 'fenetre'; });
        const poteau = Mo.carte.lampes.find(function (l) { return l.sorte !== 'fenetre' && l.sorte !== 'vitrine'; });
        aLHeure(L, decembre(L), 22);
        const dec = { fenetre: F.couleur(fenetre), poteau: F.couleur(poteau) };
        aLHeure(L, decembre(L) - 5, 22);
        const nov = { fenetre: F.couleur(fenetre) };
        aLHeure(L, decembre(L) + 4, 22);
        const jan = { fenetre: F.couleur(fenetre) };
        return { dec: dec, nov: nov, jan: jan, mois: [L.Calendrier.mois(decembre(L)), L.Calendrier.mois(decembre(L) + 4)] };
    }""")
    assert r["mois"] == ["decembre", "janvier"], r
    assert r["dec"]["fenetre"] and r["dec"]["fenetre"].startswith("rgba("), r
    assert r["dec"]["poteau"] is None, "un lampadaire de rue ne porte pas de guirlande"
    assert r["nov"]["fenetre"] is None and r["jan"]["fenetre"] is None, r


def test_le_sapin_brille_sur_la_place_en_decembre(banc):
    r = banc("function (L, o) {" + DECEMBRE + """
        L.Jeu.commencer();
        const B = L.B, F = L.Fetes, s = B.defs.fetes.sapin;
        let traits = 0;
        const ctx = { fillRect: function () { traits++; }, set fillStyle(c) {} };
        const cam = { x: s.x * 16 - 240, y: s.y * 16 - 135 };
        aLHeure(L, decembre(L), 22); F.dessinerSapin(ctx, cam);
        const dec = traits, lueur = F.lampes(cam).length;
        traits = 0; aLHeure(L, decembre(L) + 4, 22); F.dessinerSapin(ctx, cam);
        return { dec: dec, lueur: lueur, jan: traits, lueurJan: F.lampes(cam).length };
    }""")
    assert r["dec"] > 20 and r["lueur"] == 1, r
    assert r["jan"] == 0 and r["lueurJan"] == 0, r


def test_le_camion_livre_des_dindes_en_decembre(banc):
    """Le camion n'a qu'un boulot à la fois : les dindes en décembre, les génératrices pendant le verglas,
    et rien le reste de l'année."""
    r = banc("function (L, o) {" + DECEMBRE + """
        L.Jeu.commencer();
        const B = L.B, M = L.Missions, j = B.joueur;
        if (B.menu) L.Hud.fermerMenu();      // l'aide d'une partie neuve prendrait le premier coup de klaxon
        o.frame(2);
        const v = o.char('camion', 30, 0, 0);
        L.Vehicules.monter(j, v);
        o.frame(30);                          // la portiere se referme
        function klaxon(jour, verglas) {
            if (M.boulot.etape) M.boulot.abandonner('');
            aLHeure(L, jour, 13); B.options.verglas = verglas; L.Verglas.oublier();
            // Le jour change : le Clairon peut parler — sa boite prendrait le coup de klaxon.
            o.frame(5); B.dialogue = null; if (B.menu) L.Hud.fermerMenu();
            o.tape('KeyJ', 2);
            return M.boulot.slug;
        }
        return { dec: klaxon(decembre(L), false), juillet: klaxon(decembre(L) - 16, false),
                 verglas: klaxon(B.defs.verglas.tempete.premier + 1, true) };
    }""")
    assert r == {"dec": "dindes", "juillet": None, "verglas": "generatrices"}, r


def test_le_clairon_l_annonce_le_premier_matin(banc):
    r = banc("function (L, o) {" + DECEMBRE + """
        L.Jeu.commencer();
        const out = {};
        for (const k of [-1, 0, 1]) { aLHeure(L, decembre(L) + k, 7); out[k] = L.Fetes.ligneDuClairon(); }
        return out;
    }""")
    from app import fetes
    assert r["-1"] is None and r["0"] == fetes.CLAIRON and r["1"] is None, r
