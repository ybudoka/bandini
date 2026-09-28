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


def test_la_premiere_fois_elle_se_presente_puis_ouvre_ses_cours(banc):
    """« Qui parle se nomme » : la première fois, sa salutation (elle s'y nomme) ; ensuite, ACTION
    ouvre LES COURS."""
    r = banc("""function (L, o) { """ + ENTRER + """
        auDojo(L, o);
        L.Son.Voix.demandees.length = 0;
        o.tape('KeyE', 2);
        const premiere = { menu: L.B.menu ? L.B.menu.titre : null,
                           dit: L.B.dialogue ? L.B.dialogue.lignes.join(' ') : null,
                           voix: L.Son.Voix.demandees.slice() };
        L.B.dialogue = null;
        o.frame(2);
        o.tape('KeyE', 2);
        return { premiere: premiere, ensuite: L.B.menu ? L.B.menu.titre : null };
    }""")
    assert r["premiere"]["menu"] is None and "Mireille Dion" in (r["premiere"]["dit"] or ""), r
    assert "mireille-dojo-salut" in r["premiere"]["voix"], r
    assert r["ensuite"] == "LES COURS", r


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
        // Un coup qui l'a TOUCHE : dans les `touches` du coup de Bandini (le recul, lui, retombe).
        for (let k = 0; k < 4; k++) { o.tape('KeyX', 1); o.frame(18); if ((j.touches || []).indexOf(kevin.id) >= 0) touche++; }
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


# --- La relecture de la branche : une leçon au bouton par mise en place -------------------

import pytest  # noqa: E402

GESTES = {
    # La parade : Kevin arme sur le « et » ; on lui prend le poignet tout de suite.
    "retournement_poignet": "o.tape('KeyU', 1);",
    # De dos : on tient SAISIR le temps de l'étranglement.
    "etranglement": "o.touche('KeyU'); o.frame(95); o.relacher('KeyU'); o.frame(1);",
    # Tenue : on charge sur le « et », on relâche avant la fin de la fenêtre.
    "pied_de_cote": "o.touche('KeyX'); o.frame(21); o.relacher('KeyX'); o.frame(1);",
    # Plus loin : on sprinte vers Kevin et on frappe en course.
    "pied_saute": ("o.touche('ShiftLeft'); o.touche('ArrowRight'); o.frame(9); o.tape('KeyX', 1);"
                   " o.relacher('ArrowRight'); o.relacher('ShiftLeft'); o.frame(1);"),
    # Kevin attaque : on roule, et on balaie au sortir de la roulade.
    "balayage": "o.tape('ShiftLeft', 1); o.frame(15); o.tape('KeyX', 1);",
}


@pytest.mark.parametrize("slug", sorted(GESTES))
def test_chaque_mise_en_place_s_apprend_au_bouton(banc, slug):
    r = banc("""function (L, o) { """ + ENTRER + LECON + """
        auDojo(L, o);
        return lecon(L, o, '%s', function (L, o) { %s }, 1400);
    }""" % (slug, GESTES[slug]))
    assert r["appris"] is True, r


def test_kevin_revient_au_sac_et_se_redresse(banc):
    """Après une leçon, Kevin rejoint sa place au sac — et un coup ne le laisse pas penché."""
    r = banc("""function (L, o) { """ + ENTRER + """
        auDojo(L, o);
        const kevin = L.B.entites.find(function (e) { return e.partenaire; });
        const poste = { x: kevin.poste.x, y: kevin.poste.y };
        L.B.partie.argent = 1000;
        L.Dojo.acheter('uppercut');
        for (let k = 0; k < 200; k++) o.frame(1);
        L.Entites.blesser(kevin, 5, L.B.joueur, {});
        L.Dojo.annuler(null);
        for (let k = 0; k < 600; k++) o.frame(1);
        return { d: Math.round(Math.hypot(kevin.x - poste.x, kevin.y - poste.y)), recul: kevin.recul };
    }""")
    # ⚠️ « Au sac » a 8 px pres : Mireille se tient a cote, et deux corps restent a 10 px l'un
    # de l'autre (`Entites.demeler`) — il s'arrete ou elle le laisse.
    assert r["d"] <= 8 and r["recul"] == 0, r


def test_pas_de_cours_achete_pendant_une_lecon(banc):
    """Pendant la leçon d'uppercut, l'uppercut « se sait » : le circulaire ne doit pas pour
    autant devenir achetable, ni une leçon en remplacer une autre."""
    r = banc("""function (L, o) { """ + ENTRER + """
        auDojo(L, o);
        L.B.partie.argent = 5000;
        L.Dojo.acheter('uppercut');
        const achat = L.Dojo.acheter('pied_circulaire');
        // Un cours VRAIMENT achetable (le balayage n'attend rien) : pas pendant une leçon.
        const autre = L.Dojo.acheter('balayage');
        return { achat: achat, autre: autre, cours: L.B.cours && L.B.cours.slug,
                 etat: L.Dojo.etatDuCours('pied_circulaire'), argent: L.B.partie.argent };
    }""")
    assert r == {"achat": False, "autre": False, "cours": "uppercut", "etat": "verrouille", "argent": 4700}, r


# --- Des leçons qu'on comprend (docs/jalons/le-dojo-des-lecons-qu-on-comprend.md) ---------

def test_ne_rien_faire_n_est_pas_un_rate(banc):
    """Martin, 28 sept. : la leçon s'arrêtait pendant qu'on cherchait le bouton. Dix « et »
    sans un geste : pas un raté, la leçon attend."""
    r = banc("""function (L, o) { """ + ENTRER + """
        auDojo(L, o);
        L.B.partie.argent = 1000;
        L.Dojo.acheter('uppercut');
        let fenetres = 0;
        for (let n = 0; n < 1400 && L.B.cours; n++) { o.frame(1); if (L.B.cours) fenetres = L.B.cours.ouverte; }
        return { fenetres: fenetres, cours: L.B.cours ? { rates: L.B.cours.rates, reussis: L.B.cours.reussis } : null };
    }""")
    assert r["fenetres"] >= 10, r                  # sinon le juge ne juge rien
    assert r["cours"] == {"rates": 0, "reussis": 0}, r


def test_un_geste_rate_compte_encore(banc):
    """Le pendant : un geste TENTÉ au mauvais moment reste un raté (un par « et »)."""
    r = banc("""function (L, o) { """ + ENTRER + """
        auDojo(L, o);
        L.B.partie.argent = 1000;
        L.Dojo.acheter('uppercut');
        while (L.B.transition) o.frame(1);
        let rates = 0;
        for (let n = 0; n < 300 && L.B.cours; n++) {
            if (L.B.cours.t % 135 === 20) o.tape('KeyX', 1); else o.frame(1);
            if (L.B.cours) rates = L.B.cours.rates;
        }
        return rates;
    }""")
    assert r == 2, r


def test_la_fenetre_dure_six_dixiemes(banc):
    r = banc("""function (L, o) { """ + ENTRER + """
        auDojo(L, o);
        L.B.partie.argent = 1000;
        L.Dojo.acheter('uppercut');
        while (L.B.transition) o.frame(1);
        let ouverte = 0;
        for (let n = 0; n < 135; n++) { o.frame(1); if (L.B.cours.fenetre) ouverte++; }
        return ouverte;
    }""")
    assert r == 36, r


#: Ce que chaque carte doit montrer : le BOUTON de la technique (une action d'`Entree`).
BOUTONS = {"uppercut": ["attaque"], "pied_circulaire": ["attaque"], "pied_de_cote": ["attaque"],
           "pied_saute": ["esquive", "attaque"], "balayage": ["esquive", "attaque"],
           "projection_hanche": ["saisir"], "grand_fauchage": ["saisir"], "sacrifice": ["saisir"],
           "retournement_poignet": ["saisir"], "etranglement": ["saisir"]}


def test_chaque_cours_a_sa_carte_et_ses_boutons(banc):
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const out = {};
        for (const t of L.B.defs.techniques) {
            if (t.gratuite) continue;
            const carte = L.Dojo.carte(t.slug);
            out[t.slug] = { boutons: carte.filter(function (p) { return p.action; }).map(function (p) { return p.action; }),
                            mots: carte.filter(function (p) { return p.texte; }).map(function (p) { return p.texte; }).join(' '),
                            inconnus: carte.filter(function (p) { return p.texte; }).map(function (p) { return p.texte; }).join('')
                                .split('').filter(function (ch) { return ch !== ' ' && !L.Atlas.connait(ch); }) };
        }
        return out;
    }""")
    assert sorted(r) == sorted(BOUTONS), r
    for slug, c in r.items():
        assert c["boutons"] == BOUTONS[slug], (slug, c)
        assert c["mots"], (slug, c)
        assert c["inconnus"] == [], (slug, c)       # la police les dessinerait en « ? »


def test_la_carte_parle_l_appareil_qu_on_tient(banc):
    """Au clavier, la touche (X pour frapper) ; à la manette, son bouton ; au doigt, le nom du
    bouton tactile — jamais une touche de clavier à qui tient une manette."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        function glyphe() {
            const p = L.Dojo.carte('uppercut').find(function (q) { return q.action; });
            return p.glyphe ? p.glyphe.s : 'mot:' + p.texte;
        }
        o.tape('KeyZ', 1);
        const clavier = glyphe();
        o.pad([0, 0, 0, 0], [1]); o.frame(2); o.pad([0, 0, 0, 0], [0]); o.frame(2);
        const manette = glyphe();
        return { clavier: clavier, manette: manette, appareil: L.Entree.appareil };
    }""")
    assert r["appareil"] == "manette", r
    assert r["clavier"] == "touche" and r["manette"] not in ("touche", None) and not r["manette"].startswith("mot:"), r
