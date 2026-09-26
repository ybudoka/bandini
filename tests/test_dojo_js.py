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


# --- La leçon sur le tatami (tâche 4) -----------------------------------------------------

#: Joue une leçon : `geste(L, o)` est appelé à la première image de chaque fenêtre (le « et »).
LECON = """
    function lecon(L, o, slug, geste, images) {
        L.B.partie.argent = 5000;
        const ok = L.Dojo.acheter(slug);
        let vues = 0, n = 0;
        for (; n < (images || 900) && L.B.cours; n++) {
            // Un geste par fenêtre, à sa première image.
            if (L.B.cours.fenetre && L.B.cours.ouverte !== vues) { vues = L.B.cours.ouverte; geste(L, o); }
            else o.frame(1);
        }
        return { ok: ok, appris: !!L.B.partie.techniques[slug], paye: !!(L.B.partie.coursPayes || {})[slug],
                 cours: L.B.cours ? { reussis: L.B.cours.reussis, rates: L.B.cours.rates } : null };
    }
"""


def test_trois_reussites_en_rythme_apprennent_l_uppercut(banc):
    """On tape sur le « et », trois fois : la leçon met la chaîne au maillon d'avant, la
    tape fait donc partir l'uppercut, sur Kevin."""
    r = banc("""function (L, o) { """ + ENTRER + LECON + """
        auDojo(L, o);
        return lecon(L, o, 'uppercut', function (L, o) { o.tape('KeyX', 1); });
    }""")
    assert r == {"ok": True, "appris": True, "paye": False, "cours": None}, r


def test_hors_de_la_fenetre_ca_ne_compte_pas(banc):
    r = banc("""function (L, o) { """ + ENTRER + """
        auDojo(L, o);
        L.B.partie.argent = 1000;
        L.Dojo.acheter('uppercut');
        let reussis = 0;
        for (let n = 0; n < 700 && L.B.cours; n++) {
            // Un UPPERCUT (la chaîne au maillon d'avant) au milieu de chaque temps « un » :
            // la bonne technique, au mauvais moment — jamais dans la fenêtre.
            if (L.B.cours && L.B.cours.t % 135 === 20) {
                L.B.joueur.chaine = 3; L.B.joueur.chaineT = 24;
                o.tape('KeyX', 1);
            } else o.frame(1);
            if (L.B.cours) reussis = Math.max(reussis, L.B.cours.reussis);
        }
        return { appris: !!L.B.partie.techniques.uppercut, reussis: reussis,
                 paye: !!L.B.partie.coursPayes.uppercut, cours: L.B.cours || null };
    }""")
    assert r == {"appris": False, "reussis": 0, "paye": True, "cours": None}, r


def test_la_projection_de_hanche_s_apprend_en_rythme(banc):
    """SAISIR puis le stick vers l'avant, sur le « et » : la projection part dans la
    fenêtre, et compte même si Kevin retombe après."""
    r = banc("""function (L, o) { """ + ENTRER + LECON + """
        auDojo(L, o);
        return lecon(L, o, 'projection_hanche', function (L, o) {
            o.touche('KeyU'); o.frame(2); o.touche('ArrowRight'); o.frame(3);
            o.relacher('ArrowRight'); o.relacher('KeyU'); o.frame(1);
        });
    }""")
    assert r["appris"] is True, r


def test_kevin_se_releve_ne_fuit_pas_et_n_est_pas_un_crime(banc):
    """À surveiller no 3 : un vrai coup, hors leçon."""
    r = banc("""function (L, o) { """ + ENTRER + """
        auDojo(L, o);
        const kevin = L.B.entites.find(function (e) { return e.partenaire; });
        const j = L.B.joueur;
        // ⚠️ Kevin est au sac, contre le mur de gauche : on le frappe par sa DROITE.
        j.x = kevin.x + 11; j.y = kevin.y; L.Entites.regarder(j, -1, 0); L.Entites.indexer();
        const crimes = L.B.crimes.length, vie = kevin.vie;
        L.B.partie.techniques.uppercut = true;
        let touche = 0;
        for (let k = 0; k < 4; k++) { o.tape('KeyX', 1); o.frame(18); if (kevin.recul > 0) touche++; }
        const couche = kevin.etat;
        o.frame(120);
        return { vivant: kevin.vivant, etat: kevin.etat, vie: kevin.vie === vie, touche: touche,
                 crimes: L.B.crimes.length - crimes, couche: couche };
    }""")
    assert r["touche"] >= 2, r                     # sinon le juge ne juge rien
    assert r["vivant"] and r["etat"] not in ("assomme", "fuit", "couche_dojo") and r["vie"], r
    assert r["crimes"] == 0, r


def test_sortir_annule_la_lecon_et_garde_le_cours(banc):
    r = banc("""function (L, o) { """ + ENTRER + """
        auDojo(L, o);
        L.B.partie.argent = 1000;
        L.Dojo.acheter('uppercut');
        o.frame(60);
        o.sortir(); o.frame(2);
        return { cours: L.B.cours || null, paye: !!L.B.partie.coursPayes.uppercut };
    }""")
    assert r == {"cours": None, "paye": True}, r


def test_une_lecon_interrompue_se_defait(banc):
    """À surveiller no 2 : la mort (l'hôpital) coupe la leçon."""
    r = banc("""function (L, o) { """ + ENTRER + """
        auDojo(L, o);
        L.B.partie.argent = 1000;
        L.Dojo.acheter('uppercut');
        o.frame(40);
        L.Missions.hopital(null);
        for (let k = 0; k < 400 && L.B.cours; k++) o.frame(1);
        return L.B.cours || null;
    }""")
    assert r is None


def test_abandonner_dans_la_pause(banc):
    r = banc("""function (L, o) { """ + ENTRER + """
        auDojo(L, o);
        L.B.partie.argent = 1000;
        L.Dojo.acheter('uppercut');
        o.frame(40);
        L.Jeu.pause();
        const item = L.B.menu.items.find(function (i) { return i.libelle === 'ABANDONNER LA LEÇON'; });
        if (!item) return 'pas d\\'item';
        item.faire(); o.frame(2);
        return { cours: L.B.cours || null, paye: !!L.B.partie.coursPayes.uppercut };
    }""")
    assert r == {"cours": None, "paye": True}, r


def test_la_lecon_ne_tire_aucun_de(banc):
    r = banc("""function (L, o) { """ + ENTRER + """
        auDojo(L, o);
        L.B.partie.argent = 1000;
        L.Dojo.acheter('uppercut');
        while (L.B.transition) o.frame(1);
        let tires = 0; const rng = L.B.rng; L.B.rng = function () { tires++; return rng(); };
        for (let n = 0; n < 200 && L.B.cours; n++) L.Dojo.maj();
        return tires;
    }""")
    assert r == 0
