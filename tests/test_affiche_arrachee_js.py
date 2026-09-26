"""Arracher une affiche « Recherché » (le décor répond, 2e vague — docs/jalons/le-decor-les-betes-et-
les-gens-repondent.md).

La police colle ta face sur les murs à partir de deux étoiles. ACTION devant une affiche l'arrache :
elle en recolle une de moins jusqu'à la fin de la poursuite (le plafond, sans lequel le geste ne
valait rien), et le stool — celui qui te reconnaît à cause d'elles — attend un peu plus.
"""

from app import interactions, recherche

#: Deux étoiles, et les images qu'il faut pour que la police colle ses affiches.
RECHERCHE = """
  function recherche(L, o) {
    const B = L.B;
    L.Police.ajouterChaleur(2);
    B.recherche.etoiles = 2;
    for (let k = 0; k < 400 && B.entites.filter(function (e) { return e.type === 'affiche'; }).length < 2; k++) {
      B.recherche.etoiles = 2; o.frame(1);
    }
    return B.entites.filter(function (e) { return e.type === 'affiche'; });
  }
  function devant(L, a) {
    const j = L.B.joueur;
    j.x = a.x; j.y = a.y + 12; j.angle = -Math.PI / 2; j.face = 'haut'; j.vx = 0; j.vy = 0; L.Entites.indexer();
  }
"""


def test_action_devant_une_affiche_l_arrache_et_le_stool_attend(banc):
    r = banc("function (L, o) {" + RECHERCHE + """
        L.Jeu.commencer();
        const B = L.B;
        const affiches = recherche(L, o);
        const a = affiches[0];
        devant(L, a);
        const invite = L.Interactions.afficheSousLaMain(B.joueur) === a;
        o.frame(1);
        const dit = B.invite;
        const stool = B.recherche.stoolT || 0, t = B.t;
        o.tape('KeyE', 2);
        return { n: affiches.length, invite: invite, partie: B.entites.indexOf(a) < 0,
                 arrachees: B.recherche.affichesArrachees, repit: (B.recherche.stoolT - Math.max(stool, t)) / 60,
                 msg: B.msg, dit: dit };
    }""")
    assert r["n"] >= 1, "la police n'a collé aucune affiche"
    assert r["invite"], "l'affiche n'est pas sous la main, devant elle"
    assert r["dit"] == interactions.AFFICHE["invite"], r
    assert r["partie"] and r["arrachees"] == 1, r
    assert abs(r["repit"] - interactions.AFFICHE["repit_stool_s"]) < 0.1, r


def test_une_affiche_arrachee_n_est_pas_recollee_avant_la_fin_de_la_poursuite(banc):
    """Toutes arrachées, pendant longtemps, à deux étoiles : la police n'en recolle pas. La
    poursuite finie, le compte repart à zéro."""
    r = banc("function (L, o) {" + RECHERCHE + """
        L.Jeu.commencer();
        const B = L.B;
        recherche(L, o);
        B.recherche.affichesArrachees = """ + str(recherche.POLICE["affiches_max"]) + """;
        B.entites.filter(function (e) { return e.type === 'affiche'; }).forEach(function (e) { L.Entites.retirer(e); });
        for (let k = 0; k < 800; k++) { B.recherche.etoiles = 2; o.frame(1); }
        const recollees = B.entites.filter(function (e) { return e.type === 'affiche'; }).length;
        B.recherche.etoiles = 0; B.recherche.chaleur = 0;
        o.frame(41);
        return { recollees: recollees, remis: B.recherche.affichesArrachees };
    }""")
    assert r["recollees"] == 0, f"la police a recollé {r['recollees']} affiches arrachées"
    assert r["remis"] == 0, r
