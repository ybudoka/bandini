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
