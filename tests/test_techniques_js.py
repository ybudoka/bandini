"""Les techniques d'arts martiaux, au banc (docs/jalons/les-techniques-d-arts-martiaux.md)."""


def test_une_projection_ne_fait_pas_saigner(banc):
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        L.B.options.sang = true;
        const p = o.poser(null, 20, 0);
        const avant = L.B.particules.length;
        L.Entites.blesser(p, 5, L.B.joueur, { sans_sang: true, renverse: true, saigne: 30 });
        return { nouvelles: L.B.particules.length - avant, saigne: p.saigne || 0 };
    }""")
    assert r == {"nouvelles": 0, "saigne": 0}, r


def test_un_coup_silencieux_ne_crie_pas_et_n_alerte_personne(banc):
    """⚠️ Des degats qui ne couchent PAS : a 999 le coup assomme, et la branche
    qui alerte n'est jamais atteinte — le juge serait vert sans la regle."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        let cris = 0; L.Son.SFX.touche = function () { cris++; };
        const p = o.poser(null, 20, 0), temoin = o.poser(null, 40, 0);
        p.etat = 'flane'; temoin.etat = 'flane';
        L.Entites.blesser(p, 5, L.B.joueur, { silencieuse: true, sans_sang: true });
        return { victime: p.etat, temoin: temoin.etat, cris: cris };
    }""")
    assert r == {"victime": "flane", "temoin": "flane", "cris": 0}, r


# --- Le bouton SAISIR (tâche 3) --------------------------------------------------------

#: La manette : seize boutons, le 5 (RB, l'épaule de droite) enfoncé.
RB = "[0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]"


def test_u_saisit_au_clavier(banc):
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        o.touche('KeyU'); o.frame(1);
        const tenu = L.Entree.bas('saisir');
        o.relacher('KeyU'); o.frame(1);
        return { tenu: tenu, apres: L.Entree.bas('saisir') };
    }""")
    assert r == {"tenu": True, "apres": False}


def test_l_epaule_de_droite_saisit_et_ne_frappe_plus(banc):
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        o.pad([0, 0], %s); o.frame(1);
        return { saisir: L.Entree.bas('saisir'), attaque: L.Entree.bas('attaque') };
    }""" % RB)
    assert r == {"saisir": True, "attaque": False}


def test_une_disposition_sauvee_avant_saisir_donne_l_epaule_a_saisir(banc):
    """À surveiller no 3 : une disposition apprise avant le bouton a l'épaule de
    droite en DEUXIÈME bouton de FRAPPE, et pas de clé `saisir`. L'épaule passe
    à SAISIR — sinon elle frapperait ET saisirait à la fois."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        L.Entree.reglerManette({ boutons: { action: [0], esquive: [1], attaque: [2, 5], arme: [3, 4] } });
        o.pad([0, 0], %s); o.frame(1);
        return { saisir: L.Entree.bas('saisir'), attaque: L.Entree.bas('attaque'),
                 profil: L.Entree.profilManette().boutons };
    }""" % RB)
    assert r["saisir"] is True and r["attaque"] is False, r
    assert r["profil"]["attaque"] == [2] and r["profil"]["saisir"] == [5], r


def test_l_epaule_de_droite_tourne_encore_les_onglets(banc):
    """`lireEpaules` lisait le numéro de l'épaule dans FRAPPE ; il le lit dans SAISIR."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        o.pad([0, 0], %s);
        // ⚠️ L'appui NEUF se vide a la fin de l'image (`videPresse`) : on le lit
        // entre la lecture de la manette et la fin, comme le classeur le lit.
        L.Entree.debutImage();
        return L.Entree.neufEpaule('d');
    }""" % RB)
    assert r is True


# --- Le moteur : la chaîne, la réserve, les passants (tâche 4) ---------------------------

def _chaine(banc, sait, tapes, espace=4):
    """Les techniques qui partent, dans l'ordre, pour `tapes` tapes à `espace`
    images d'écart. ⚠️ SANS CIBLE : un passant posé à côté se rapprocherait
    (`majPieton` tourne dans `o.frame`) et le genou volerait la place du poing.
    La tape part au RELÂCHER (`majGestes` : on charge tant que c'est tenu)."""
    return banc("""function (L, o) {
        L.Jeu.commencer();
        L.B.joueur.angle = 0; L.B.joueur.face = 'droite';
        %s
        const vus = []; let dernier = null;
        function regarder(n) {
            for (let k = 0; k < n; k++) {
                const t = L.B.joueur.technique || null;
                if (t && t !== dernier) vus.push(t);
                dernier = t; o.frame(1);
            }
        }
        for (let i = 0; i < %d; i++) { o.touche('KeyX'); regarder(1); o.relacher('KeyX'); regarder(%d); }
        regarder(60);
        return vus;
    }""" % (sait, tapes, espace))


def test_trois_tapes_font_gauche_droit_crochet(banc):
    r = _chaine(banc, "", 3, espace=14)
    assert r[:3] == ["direct_gauche", "direct_droit", "crochet"], r


def test_la_chaine_s_allonge_avec_ce_qu_on_sait(banc):
    r = _chaine(banc, "L.B.partie.techniques = { uppercut: true, pied_circulaire: true };", 5, espace=18)
    assert r == ["direct_gauche", "direct_droit", "crochet", "uppercut", "pied_circulaire"], r


def test_sans_le_cours_la_chaine_repart_au_direct(banc):
    r = _chaine(banc, "", 4, espace=16)
    assert r == ["direct_gauche", "direct_droit", "crochet", "direct_gauche"], r


def test_une_tape_pendant_le_coup_est_gardee_en_reserve(banc):
    """Deux tapes à deux images d'écart : la seconde tombe PENDANT le direct, et
    doit quand même donner le direct du droit."""
    r = _chaine(banc, "", 2, espace=2)
    assert r == ["direct_gauche", "direct_droit"], r


def test_une_vieille_partie_sans_techniques_frappe(banc):
    """À surveiller no 2."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const p = JSON.parse(JSON.stringify(L.B.partie));
        delete p.techniques;
        L.B.partie = L.Sauvegarde.completer(p, L.B.defs);
        o.touche('KeyX'); o.frame(1); o.relacher('KeyX'); o.frame(3);
        return { t: L.B.joueur.technique || null, techniques: L.B.partie.techniques };
    }""")
    assert r == {"t": "direct_gauche", "techniques": {}}, r


def test_tenue_sans_le_cours_reste_le_coup_fort(banc):
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        o.touche('KeyX'); o.frame(L.Combat.CHARGE_MIN + 2); o.relacher('KeyX'); o.frame(2);
        return { t: L.B.joueur.technique, fort: !!L.B.joueur.fort };
    }""")
    assert r == {"t": "direct_gauche", "fort": True}, r


def test_tenue_avec_le_cours_donne_le_pied_de_cote(banc):
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        L.B.partie.techniques.pied_de_cote = true;
        o.touche('KeyX'); o.frame(L.Combat.CHARGE_MIN + 2); o.relacher('KeyX'); o.frame(2);
        return L.B.joueur.technique;
    }""")
    assert r == "pied_de_cote"


def test_colle_a_la_cible_le_crochet_devient_le_genou(banc):
    """Au contact (deux corps ne s'approchent pas sous 10 px), le 3e maillon est
    le genou — et la chaîne ne casse pas derrière lui."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        L.B.partie.techniques.uppercut = true;
        const j = L.B.joueur; j.angle = 0; j.face = 'droite';
        const p = o.poser(null, 10, 0); p.vie = 999;
        const vus = []; let dernier = null;
        function regarder(n) {
            for (let k = 0; k < n; k++) {
                const t = j.technique || null;
                if (t && t !== dernier) vus.push(t);
                dernier = t; o.frame(1);
            }
        }
        for (let i = 0; i < 4; i++) {
            // Les coups le repoussent : on le remet au contact avant chaque tape.
            p.x = j.x + 10; p.y = j.y; p.vx = 0; p.vy = 0; p.etat = 'fige'; p.recul = 0; L.Entites.indexer();
            o.touche('KeyX'); regarder(1); o.relacher('KeyX'); regarder(18);
        }
        return vus;
    }""")
    assert r == ["direct_gauche", "direct_droit", "genou", "uppercut"], r


def test_au_sortir_d_une_roulade_c_est_le_balayage(banc):
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        L.B.partie.techniques.balayage = true;
        const m = o.poser(null, 60, 0); m.etat = 'attaque_joueur';      // une menace : la roulade part
        o.touche('ShiftLeft'); o.frame(1); o.relacher('ShiftLeft');
        o.frame(L.Combat.ROULADE_IMAGES + 1);
        o.touche('KeyX'); o.frame(1); o.relacher('KeyX'); o.frame(2);
        return L.B.joueur.technique;
    }""")
    assert r == "balayage"


def test_un_passant_rejoue_la_meme_suite_pour_la_meme_empreinte(banc):
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        function suite() {
            const p = o.poser(null, 12, 0); p.id = 4242; p.coups = 0;
            const vus = [];
            for (let i = 0; i < 6; i++) {
                p.etat = 'attaque_joueur';
                L.Combat.frapper(p, false); vus.push(p.technique);
                for (let k = 0; k < 40 && p.etat === 'attaque'; k++) L.Combat.maj();
            }
            L.Entites.retirer(p);
            return vus;
        }
        return [suite(), suite()];
    }""")
    assert r[0] == r[1] and len(set(r[0])) >= 2, r
    assert set(r[0]) <= {"direct_gauche", "direct_droit", "crochet", "genou"}, r


def test_un_direct_touche_la_cible_devant(banc):
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const p = o.poser(null, 11, 0); L.B.joueur.angle = 0; L.B.joueur.face = 'droite';
        const vie = p.vie;
        o.touche('KeyX'); o.frame(1); o.relacher('KeyX'); o.frame(12);
        return vie - p.vie;
    }""")
    assert r == 8, r


