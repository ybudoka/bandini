"""Le casino du Dragon d'or, JOUÉ au banc (docs/jalons/le-casino-du-petit-canton.md, vague 1).

La machine à sous qu'on touche : au bouton ACTION, dans la grande salle ; un tour qui prend la mise et paie
selon la table ; son hasard qui n'est pas celui du jeu ; l'évaluation qui est celle de Python ; sur vingt mille
tours, une machine qui rend moins qu'on y met. Et dehors : le portier, qui naît quand on approche sans
rien déplacer, et la marquise de néon.
"""

import json
from itertools import product

from app import machine_a_sous as m

DEDANS = """
  function dedans(L, o, lieu, point) {
    const B = L.B, j = B.joueur, M = L.Monde;
    const porte = (M.carte.def.portes || []).find(function (q) { return q.lieu === lieu && q.interieur; });
    j.x = porte.x * 16 + 8; j.y = (porte.y + 1) * 16 + 4; L.Entites.indexer();
    L.Jeu.entrer(porte); o.fondu();
    for (let k = 0; k < 200 && !B.interieur; k++) o.frame(1);
    const pt = B.interieur.points.find(function (q) { return q.type === point; });
    j.x = pt.x * 16 + 8; j.y = (pt.y + 1) * 16 + 8; j.angle = -Math.PI / 2; L.Entites.indexer();
    o.frame(2);
    return pt;
  }
"""


def test_la_machine_a_sous_s_ouvre_au_bouton_et_prend_la_mise(banc):
    r = banc("function (L, o) {" + DEDANS + """
        L.Jeu.commencer();
        L.B.partie.argent = 100;
        dedans(L, o, 'nord_casino', 'machine_a_sous');
        const invite = L.B.invite;
        o.tape('KeyE', 2);
        const menu = L.B.menu;
        const vu = { invite: invite, titre: menu && menu.titre, aide: menu && menu.aide,
                     premiere: menu && menu.items[0].libelle };
        menu.curseur = 0;
        o.tape('KeyE', 2);
        vu.reste = L.B.menu === menu;
        vu.tours = L.B.partie.machine_a_sous && L.B.partie.machine_a_sous.tours;
        vu.argent = L.B.partie.argent;
        vu.gain = L.B.machineASous ? L.B.machineASous.resultat.gain : null;
        return vu;
    }""")
    assert r["invite"] == "LA MACHINE À SOUS", r
    assert r["titre"] == "MACHINE À SOUS" and r["premiere"] == "TIRER LE BRAS", r
    assert f"RETOUR {m.RETOUR_AFFICHE} %" in r["aide"], r
    assert r["reste"], "le bras a refermé la machine"
    assert r["tours"] == 1 and r["argent"] == 100 - m.MISE + r["gain"], r


def test_le_navigateur_evalue_comme_python_sur_les_huit_mille_arrets(banc):
    arrets = [list(a) for a in product(*m.ROULEAUX)]
    r = banc("""function (L, o) {
        const C = L.Casino;
        return ARRETS.map(function (a) { return C.evaluerRouleaux(a); });
    }""".replace("ARRETS", json.dumps(arrets)))
    assert r == [m.evaluer(tuple(a)) for a in arrets]


def test_jouer_ne_touche_pas_au_hasard_du_jeu(banc):
    """Cent tours entre deux tirages ne changent pas le tirage suivant — et le même tour revient au même
    numéro (le sel n'est pas celui du vidéopoker)."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const B = L.B, C = L.Casino;
        L.graine(3);
        const temoin = [B.rng(), B.rng(), B.rng()];
        L.graine(3);
        B.partie.argent = 100000;
        for (let i = 0; i < 100; i++) { C.compteur().tours = 0; C.tirer(); }
        const apres = [B.rng(), B.rng(), B.rng()];
        return { temoin: temoin, apres: apres, meme: C.arretDuTour(7).join() === C.arretDuTour(7).join(),
                 differents: new Set([0, 1, 2, 3, 4, 5, 6, 7].map(function (n) { return C.arretDuTour(n).join(); })).size };
    }""")
    assert r["apres"] == r["temoin"], "jouer à la machine à sous a décalé le hasard du jeu"
    assert r["meme"] and r["differents"] >= 6


def test_vingt_mille_tours_rendent_moins_qu_on_y_met(banc):
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const C = L.Casino, r = C.regles();
        let mise = 0, rendu = 0;
        for (let n = 0; n < 20000; n++) { mise += r.mise; rendu += C.gainDe(C.arretDuTour(n)); }
        return rendu / mise;
    }""")
    assert r < 1.0, f"la machine rend {r:.3f}"
    assert abs(r - m.retour_exact()) < 0.04, (r, m.retour_exact())


def test_la_machine_a_assez_mange_pour_aujourd_hui(banc):
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const B = L.B, C = L.Casino;
        B.partie.argent = 100000;
        let ok = 0;
        for (let i = 0; i < C.regles().tours_par_jour + 5; i++) if (C.tirer()) ok++;
        return ok;
    }""")
    assert r == m.TOURS_PAR_JOUR


def test_le_portier_nait_quand_on_approche_sans_rien_deplacer(banc):
    """Au démarrage, personne à la porte (le hasard du départ est intact) ; on approche, il naît à deux tuiles
    de la porte, figé, hors de la suite des numéros — et le tirage suivant du jeu est le même qu'avant."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const B = L.B, C = L.Casino, j = B.joueur;
        const avant = !!C.portier();
        const porte = L.Monde.carte.def.portes.find(function (p) { return p.lieu === 'nord_casino'; });
        j.x = porte.x * 16 + 8; j.y = (porte.y + 6) * 16 + 8; L.Entites.indexer();
        L.graine(5);
        const temoin = B.rng(); L.graine(5);
        B.t = 30 * Math.ceil(B.t / 30); C.maj();
        const g = C.portier();
        return { avant: avant, ici: !!g, id: g ? g.id : 0, fige: g && g.etat,
                 tx: g ? Math.floor(g.x / 16) - porte.x : null, ty: g ? Math.floor(g.y / 16) - porte.y : null,
                 apres: B.rng(), temoin: temoin };
    }""")
    assert r["avant"] is False, "un portier au démarrage : le hasard du départ bouge"
    assert r["ici"] and r["fige"] == "fige" and (r["tx"], r["ty"]) == (2, 1), r
    assert r["id"] >= 1e9, "le portier a pris un numéro de la suite de la ville"
    assert r["apres"] == r["temoin"], "la naissance du portier a tiré un dé du jeu"


def test_la_marquise_se_peint_devant_le_casino_et_nulle_part_ailleurs(banc):
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const porte = L.Monde.carte.def.portes.find(function (p) { return p.lieu === 'nord_casino'; });
        const peindre = function (cx, cy) {
            const c = o.doc.createElement('canvas').getContext('2d');
            c.traces = [];
            L.Casino.dessinerMarquise(c, { x: cx - 240, y: cy - 160 });
            return c.traces.filter(function (q) { return q[4] === '#5a0c0a'; }).length;
        };
        return { ici: peindre(porte.x * 16, porte.y * 16), loin: peindre(20 * 16, 300 * 16) };
    }""")
    assert r["ici"] == 1 and r["loin"] == 0, r
