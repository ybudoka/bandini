"""Le dojo du quartier, au banc (docs/jalons/le-dojo-du-quartier.md)."""

ENTRER = """
    function auDojo(L, o) {
        L.Jeu.commencer();
        const porte = L.Monde.carte.portes.find(function (p) { return p.interieur === 'dojo'; });
        L.B.joueur.x = porte.x * L.TT + 8; L.B.joueur.y = (porte.y + 1) * L.TT + 10;
        L.B.partie.heure = 0.5;                                   // midi : ouvert
        o.entrer(porte);
        const m = L.Entites.joueurs()[0];
        const mireille = L.B.entites.find(function (e) { return e.personnage === 'mireille'; });
        L.Entites.regarder(m, mireille.x - m.x, mireille.y - m.y);
        m.x = mireille.x; m.y = mireille.y + 14;
        L.Entites.indexer();
        return mireille;
    }
"""


def test_action_pres_de_mireille_ouvre_les_cours(banc):
    r = banc("""function (L, o) { """ + ENTRER + """
        auDojo(L, o);
        o.tape('KeyE', 2);
        return L.B.menu ? L.B.menu.titre : null;
    }""")
    assert r == "LES COURS"


def test_un_cours_se_paie_une_fois(banc):
    r = banc("""function (L, o) { """ + ENTRER + """
        auDojo(L, o);
        L.B.partie.argent = 1000;
        L.Dojo.acheter('uppercut');
        const apres = L.B.partie.argent;
        L.B.cours = null;                                         // la leçon ratée
        L.Dojo.acheter('uppercut');
        return { apres: apres, encore: L.B.partie.argent, etat: L.Dojo.etatDuCours('uppercut') };
    }""")
    assert r == {"apres": 700, "encore": 700, "etat": "paye"}, r


def test_sans_argent_rien_ne_commence(banc):
    """À surveiller no 5."""
    r = banc("""function (L, o) { """ + ENTRER + """
        auDojo(L, o);
        L.B.partie.argent = 10;
        const ok = L.Dojo.acheter('uppercut');
        return { ok: ok, cours: L.B.cours || null, etat: L.Dojo.etatDuCours('uppercut') };
    }""")
    assert r == {"ok": False, "cours": None, "etat": "a_vendre"}, r


def test_le_circulaire_attend_l_uppercut(banc):
    r = banc("""function (L, o) { """ + ENTRER + """
        auDojo(L, o);
        L.B.partie.argent = 5000;
        return { avant: L.Dojo.etatDuCours('pied_circulaire'), achat: L.Dojo.acheter('pied_circulaire') };
    }""")
    assert r == {"avant": "verrouille", "achat": False}, r


def test_la_nuit_le_menu_est_ferme(banc):
    r = banc("""function (L, o) { """ + ENTRER + """
        auDojo(L, o);
        L.B.partie.heure = 23 / 24;
        const m = L.Dojo.menuCours();
        return m.items.filter(function (i) { return i.actif !== false && !i.entete; }).length;
    }""")
    assert r == 0


def test_une_vieille_partie_a_ses_cours_vides(banc):
    """À surveiller no 4."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const p = JSON.parse(JSON.stringify(L.B.partie)); delete p.coursPayes;
        return L.Sauvegarde.completer(p, L.B.defs).coursPayes;
    }""")
    assert r == {}
