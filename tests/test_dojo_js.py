"""Le dojo du quartier, au banc (docs/jalons/le-dojo-du-quartier.md)."""

import pytest

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


@pytest.fixture(scope="module")
def achats(banc):
    """Les cinq juges du comptoir de Mireille dans UN banc : sans argent, le circulaire verrouillé,
    un cours payé une fois, pas d'achat pendant une leçon, puis le menu de nuit.

    ⚠️ Aucun ne joue une image : ce sont des achats et un menu, lus sur place. Avant chacun, on
    remet ce que le juge trouvait en entrant au dojo — pas de leçon (`B.cours`), aucun cours payé,
    les techniques de la partie neuve, midi."""
    return banc("""function (L, o) { """ + ENTRER + """
        auDojo(L, o);
        const neuves = JSON.stringify(L.B.partie.techniques), sorties = {};
        function remettre() {
            L.B.cours = null; L.B.partie.coursPayes = {}; L.B.partie.techniques = JSON.parse(neuves);
            L.B.partie.heure = 0.5;
        }
        remettre();
        L.B.partie.argent = 10;
        sorties.sansArgent = { ok: L.Dojo.acheter('uppercut'), cours: L.B.cours || null, etat: L.Dojo.etatDuCours('uppercut') };
        remettre();
        L.B.partie.argent = 5000;
        sorties.circulaire = { avant: L.Dojo.etatDuCours('pied_circulaire'), achat: L.Dojo.acheter('pied_circulaire') };
        remettre();
        L.B.partie.argent = 1000;
        L.Dojo.acheter('uppercut');
        const apres = L.B.partie.argent;
        L.B.cours = null;                                         // la leçon ratée
        L.Dojo.acheter('uppercut');
        sorties.uneFois = { apres: apres, encore: L.B.partie.argent, etat: L.Dojo.etatDuCours('uppercut') };
        remettre();
        L.B.partie.argent = 5000;
        L.Dojo.acheter('uppercut');
        const achat = L.Dojo.acheter('pied_circulaire');
        // Un cours VRAIMENT achetable (le balayage n'attend rien) : pas pendant une leçon.
        const autre = L.Dojo.acheter('balayage');
        sorties.pendant = { achat: achat, autre: autre, cours: L.B.cours && L.B.cours.slug,
                            etat: L.Dojo.etatDuCours('pied_circulaire'), argent: L.B.partie.argent };
        remettre();
        L.B.partie.heure = 23 / 24;
        sorties.nuit = L.Dojo.menuCours().items.filter(function (i) { return i.actif !== false && !i.entete; }).length;
        return sorties;
    }""")


def test_un_cours_se_paie_une_fois(achats):
    assert achats["uneFois"] == {"apres": 700, "encore": 700, "etat": "paye"}, achats["uneFois"]


def test_sans_argent_rien_ne_commence(achats):
    """À surveiller no 5."""
    r = achats["sansArgent"]
    assert r == {"ok": False, "cours": None, "etat": "a_vendre"}, r


def test_le_circulaire_attend_l_uppercut(achats):
    r = achats["circulaire"]
    assert r == {"avant": "verrouille", "achat": False}, r


def test_la_nuit_le_menu_est_ferme(achats):
    assert achats["nuit"] == 0


def test_pas_de_cours_achete_pendant_une_lecon(achats):
    """Pendant la leçon d'uppercut, l'uppercut « se sait » : le circulaire ne doit pas pour
    autant devenir achetable, ni une leçon en remplacer une autre."""
    r = achats["pendant"]
    assert r == {"achat": False, "autre": False, "cours": "uppercut", "etat": "verrouille", "argent": 4700}, r


def test_une_vieille_partie_a_ses_cours_vides(banc):
    """À surveiller no 4."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const p = JSON.parse(JSON.stringify(L.B.partie)); delete p.coursPayes;
        return L.Sauvegarde.completer(p, L.B.defs).coursPayes;
    }""")
    assert r == {}


# --- La leçon sur le tatami (tâche 4) -----------------------------------------------------

#: Joue une leçon À SON RYTHME : `geste(L, o)` part quand tout le monde est en place (pas en plein
#: essai, personne au sol ni en l'air ; pour la parade, quand Kevin ARME), puis après une attente
#: qui change d'un essai à l'autre — le moment exact ne compte plus.
LECON = """
    function pret(L) {
        const c = L.B.cours;
        if (!c || L.B.transition || c.essai || c.remise > 0) return false;
        const k = c.kevin;
        if (k.etat === 'couche_dojo' || k.vol) return false;
        if (c.slug === 'retournement_poignet') return k.etat === 'attaque' && k.phase === 'anticipation';
        return true;
    }
    function lecon(L, o, slug, geste, images) {
        L.B.partie.argent = 5000;
        const ok = L.Dojo.acheter(slug);
        let essais = 0, attente = 0, n = 0;
        for (; n < (images || 1400) && L.B.cours; n++) {
            if (pret(L) && --attente <= 0) {
                geste(L, o); essais++;
                attente = (essais * 37) % 50;
            } else o.frame(1);
        }
        return { ok: ok, essais: essais, appris: !!L.B.partie.techniques[slug],
                 paye: !!(L.B.partie.coursPayes || {})[slug],
                 cours: L.B.cours ? { reussis: L.B.cours.reussis } : null };
    }
"""


def test_trois_reussites_a_son_rythme_apprennent_l_uppercut(banc):
    """Martin, 29 sept. : « change comment on apprend ces techniques, c'est trop dur ». Trois
    uppercuts sur Kevin, espacés comme ça vient : la leçon garde la chaîne au maillon d'avant, la
    tape fait donc partir l'uppercut."""
    r = banc("""function (L, o) { """ + ENTRER + LECON + """
        auDojo(L, o);
        return lecon(L, o, 'uppercut', function (L, o) { o.tape('KeyX', 1); });
    }""")
    assert r["essais"] == 3, r                     # trois essais, trois réussites : aucun de perdu
    assert {k: r[k] for k in ("ok", "appris", "paye", "cours")} == \
        {"ok": True, "appris": True, "paye": False, "cours": None}, r


def test_des_coups_dans_le_vide_n_arretent_rien(banc):
    """Aucun échec : vingt uppercuts dos à Kevin, et la leçon est toujours là, le cours payé —
    Mireille le dit (PRESQUE), c'est tout."""
    r = banc("""function (L, o) { """ + ENTRER + LECON + """
        auDojo(L, o);
        L.B.partie.argent = 1000;
        L.Dojo.acheter('uppercut');
        let coups = 0, presque = 0;
        for (let n = 0; n < 2400 && L.B.cours && !(coups === 20 && pret(L)); n++) {
            if (pret(L) && coups < 20) { L.Entites.regarder(L.B.joueur, -1, 0); o.tape('KeyX', 1); coups++; }
            else o.frame(1);
            if (L.B.cours && L.B.cours.dit === 'PRESQUE' && L.B.cours.ditT === 40) presque++;
        }
        return { coups: coups, presque: presque, paye: !!L.B.partie.coursPayes.uppercut,
                 cours: L.B.cours ? { reussis: L.B.cours.reussis } : null };
    }""")
    assert r["coups"] == 20, r                     # sinon le juge ne juge rien
    assert r["cours"] == {"reussis": 0} and r["paye"] is True, r
    assert r["presque"] == 20, r


def test_la_projection_de_hanche_s_apprend_a_son_rythme(banc):
    """SAISIR puis le stick vers l'avant : la projection compte quand Kevin retombe."""
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

GESTES = {
    # La parade : Kevin arme (lentement) ; on lui prend le poignet pendant qu'il arme.
    "retournement_poignet": "o.tape('KeyU', 1);",
    # De dos : on tient SAISIR le temps de l'étranglement.
    "etranglement": "o.touche('KeyU'); o.frame(95); o.relacher('KeyU'); o.frame(1);",
    # Tenue : on charge, on relâche.
    "pied_de_cote": "o.touche('KeyX'); o.frame(21); o.relacher('KeyX'); o.frame(1);",
    # Plus loin : on sprinte vers Kevin et on frappe en course, une fois sur lui. ⚠️ 9 images (23 px
    # sur 70) frappaient de trop loin.
    "pied_saute": ("o.touche('ShiftLeft'); o.touche('ArrowRight'); o.frame(16); o.tape('KeyX', 1);"
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


# --- Des leçons qu'on comprend (docs/jalons/le-dojo-des-lecons-qu-on-comprend.md) ---------

def test_ne_rien_faire_ne_finit_rien(banc):
    """Martin, 28 sept. : la leçon s'arrêtait pendant qu'on cherchait le bouton. Vingt secondes
    sans un geste : elle attend."""
    r = banc("""function (L, o) { """ + ENTRER + """
        auDojo(L, o);
        L.B.partie.argent = 1000;
        L.Dojo.acheter('uppercut');
        o.frame(1200);
        return L.B.cours ? { reussis: L.B.cours.reussis } : null;
    }""")
    assert r == {"reussis": 0}, r


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


# --- Bandini revient sur sa marque (docs/jalons/le-dojo-bandini-revient-sur-sa-marque.md) ------

def test_le_coup_de_pied_saute_s_apprend_essai_apres_essai(banc):
    """Martin, 29 sept. : « trop difficile ». Un premier essai parti trop tôt laisse Bandini DERRIÈRE
    Kevin, dos à lui : on souffle, et chacun reprend sa marque — les essais suivants portent."""
    r = banc("""function (L, o) { """ + ENTRER + LECON + """
        auDojo(L, o);
        L.B.partie.argent = 5000;
        L.Dojo.acheter('pied_saute');
        while (L.B.transition) o.frame(1);
        const j = L.B.joueur, k = L.B.cours.kevin;
        // Le premier essai est parti trop tôt : Bandini a filé DERRIÈRE Kevin, dos à lui.
        j.x = k.x + 24; j.y = k.y; L.Entites.regarder(j, 1, 0); L.Entites.indexer();
        o.tape('KeyX', 1);
        const depasse = k.x - j.x;
        const fin = lecon(L, o, 'pied_saute', function (L, o) {
            o.touche('ShiftLeft'); o.touche('ArrowRight'); o.frame(16);
            o.tape('KeyX', 1); o.relacher('ArrowRight'); o.relacher('ShiftLeft'); o.frame(1);
        });
        return { appris: fin.appris, depasse: Math.round(depasse) };
    }""")
    assert r["depasse"] < 0, r                     # sinon le juge ne juge rien : il l'a bien dépassé
    assert r["appris"] is True, r


#: Un essai qui part dans le vide (dos à Kevin), puis on laisse retomber.
DANS_LE_VIDE = """
    function dansLeVide(L, o) {
        L.B.partie.argent = 5000;
        L.Dojo.acheter('uppercut');
        while (L.B.transition) o.frame(1);
        const j = L.B.joueur, x0 = j.x, y0 = j.y;
        j.x += 40; L.Entites.regarder(j, 1, 0); L.Entites.indexer();
        o.tape('KeyX', 1);
        while (L.B.cours.essai || !L.B.cours.remise) o.frame(1);
        return { x0: x0, y0: y0 };
    }
"""


def test_bandini_revient_sur_sa_marque_face_a_kevin(banc):
    """Derrière Kevin, dos à lui : un essai, on souffle, et il est sur sa marque."""
    r = banc("""function (L, o) { """ + ENTRER + DANS_LE_VIDE + """
        auDojo(L, o);
        const m = dansLeVide(L, o), j = L.B.joueur;
        o.frame(L.B.defs.dojo.remise_images + 2);
        return { dx: Math.round(j.x - m.x0), dy: Math.round(j.y - m.y0), regard: j.regard ? Math.sign(j.regard.x) : null,
                 kevin: Math.sign(L.B.cours.kevin.x - j.x) };
    }""")
    assert r["dx"] == 0 and r["dy"] == 0 and r["kevin"] == 1, r


def test_on_ne_ramene_personne_en_pleine_course(banc):
    """Le pendant : qui marche après son essai n'est pas téléporté sous ses pieds."""
    r = banc("""function (L, o) { """ + ENTRER + DANS_LE_VIDE + """
        auDojo(L, o);
        const m = dansLeVide(L, o), j = L.B.joueur;
        // Un bond de plus de 4 px d'une image à l'autre : téléporté.
        // ⚠️ Vers le BAS, sur le tatami : au-dessus, c'est la rangee de classeurs du mur du fond,
        // et on ne marche plus sur les meubles (30 sept. 2026) — le juge n'aurait plus rien mesure.
        let bond = 0, px = j.x, py = j.y;
        o.touche('ArrowDown');
        for (let n = 0; n < L.B.defs.dojo.remise_images * 3; n++) {
            o.frame(1); bond = Math.max(bond, Math.hypot(j.x - px, j.y - py)); px = j.x; py = j.y;
        }
        o.relacher('ArrowDown');
        return { bond: Math.round(bond), bouge: Math.round(Math.hypot(j.x - m.x0 - 40, j.y - m.y0)) };
    }""")
    assert r["bouge"] > 10, r                      # sinon le juge ne juge rien : il a marché
    assert r["bond"] <= 4, r


def test_kevin_arme_lentement_pour_la_parade(banc):
    """La parade : Kevin arme son coup à intervalle régulier, TIENT l'élan 0,75 s et crie — le coup
    de rue n'armait que 5 images, c'était le vrai mur de cette leçon."""
    r = banc("""function (L, o) { """ + ENTRER + """
        auDojo(L, o);
        L.B.partie.argent = 5000;
        L.Dojo.acheter('retournement_poignet');
        while (L.B.transition) o.frame(1);
        const k = L.B.cours.kevin;
        let arme = 0, plus = 0, cri = '', elans = k.elans || 0;
        for (let n = 0; n < 400; n++) {
            o.frame(1);
            if (k.etat === 'attaque' && k.phase === 'anticipation') { arme++; if (k.bulle) cri = k.bulle.texte; }
            else if (arme) { plus = Math.max(plus, arme); arme = 0; }
        }
        return { plus: plus, cri: cri, elans: (k.elans || 0) - elans };
    }""")
    assert r["elans"] >= 2, r                      # plus d'un coup en 400 images
    assert r["plus"] >= 44 and r["cri"] == "HA !", r
