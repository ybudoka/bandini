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
