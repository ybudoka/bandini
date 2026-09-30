"""On ne marche pas sur les meubles (Martin, 30 sept. 2026).

Un meuble d'intérieur reste un obstacle BAS (`solide 3`, il arrête un char), mais il porte
aussi le bit `MEUBLE`, que voient le passant, le joueur, l'agent et le A* : on fait le tour
du comptoir, on ne marche plus dessus. L'escalier est le seul qu'on foule — on y monte.

⚠️ Avant, un piéton traversait le comptoir, le lit et la table comme un tapis : au terminus,
en montant tout droit depuis la porte, on finissait contre le mur du fond, derrière le guichet.
"""

from app import carte

MEUBLES = sorted(g for g, p in carte.LEGENDE.items() if p.get("meuble"))


def test_au_terminus_le_comptoir_arrete_le_joueur(banc):
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const j = L.B.joueur, T = L.TT, c = L.Monde.carte;
        const porte = c.portes.find(function (p) { return p.interieur === 'terminus'; });
        j.x = porte.x * T + 8; j.y = (porte.y + 1) * T + 10;
        o.entrer(porte);
        const piece = L.B.interieur;
        // Tout droit vers le haut, depuis l'entree : le comptoir est deux rangees sous le mur.
        const a = piece.apparition;
        j.x = a.x * T + 8; j.y = a.y * T + 8;
        const vues = [];
        o.touche('KeyW');
        for (let i = 0; i < 180; i++) {
            o.frame(1);
            vues.push(L.Monde.glyphe(Math.floor(j.x / T), Math.floor(j.y / T)));
        }
        o.relacher('KeyW');
        const haut = Math.floor((j.y - j.r) / T);
        const devant = L.Monde.glyphe(Math.floor(j.x / T), haut - 1);
        // Et de cote, contre la rangee de chaises : on s'arrete avant la premiere.
        const chaise = piece.sol.findIndex(function (l) { return l.indexOf('h') >= 0; });
        const x0 = piece.sol[chaise].indexOf('h');
        j.x = (x0 - 1) * T + 8; j.y = chaise * T + 8;
        o.touche('KeyD');
        for (let i = 0; i < 90; i++) o.frame(1);
        o.relacher('KeyD');
        return { slug: piece.slug, sur: vues.filter(function (g) { return (L.B.carte.legende[g] || {}).meuble; }),
                 devant: devant, haut: haut,
                 chaise: { tx: Math.floor((j.x + j.r) / T), x0: x0 } };
    }""")
    assert r["slug"] == "terminus", r
    assert r["sur"] == [], "le joueur a marche sur un meuble : %s" % r
    assert r["devant"] == "c", "le joueur ne s'arrete pas contre le comptoir : %s" % r
    assert r["chaise"]["tx"] < r["chaise"]["x0"], "le joueur entre dans la chaise : %s" % r


def test_tout_meuble_barre_a_pied_sauf_l_escalier(banc):
    """Chaque meuble de la légende, posé dans une pièce : il arrête le passant, le joueur (et
    l'agent, qui nage), le chemin à pied et le char ; l'escalier n'arrête que le char."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const c = L.Monde.carte, M = L.Monde;
        const porte = c.portes.find(function (p) { return p.interieur === 'terminus'; });
        o.entrer(porte);
        const k = L.B.carte;
        const a = L.B.interieur.apparition;
        const ligne = k.sol[a.y - 1];
        const verdict = {};
        for (const g of MEUBLES) {
            k.sol[a.y - 1] = ligne.slice(0, a.x) + g + ligne.slice(a.x + 1);
            k.solide[(a.y - 1) * k.w + a.x] = (k.legende[g] || {}).solide || 0;
            verdict[g] = [M.MASQUE_PIETON, M.MASQUE_NAGEUR, M.MASQUE_A_PIED, M.MASQUE_VEHICULE]
                .map(function (m) { return M.bloque(a.x, a.y - 1, m); });
        }
        k.sol[a.y - 1] = ligne;
        return verdict;
    }""".replace("MEUBLES", repr(MEUBLES)))
    for g, (pieton, nageur, a_pied, char) in r.items():
        assert char, f"« {g} » ne bloque plus les chars"
        if g == carte.MARCHE_DESSUS:
            assert not (pieton or nageur or a_pied), f"on ne monte plus l'escalier : {r[g]}"
        else:
            assert pieton and nageur and a_pied, (
                f"« {g} » ({carte.LEGENDE[g]['nom']}) se marche encore : piéton, nageur, chemin = {r[g]}")


def test_le_chemin_a_pied_ne_passe_pas_derriere_le_comptoir(banc):
    """L'arrière du comptoir du terminus est un morceau de plancher à part : le commis s'y
    tient, et un agent ne le rejoint pas en enjambant le guichet."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const c = L.Monde.carte, T = L.TT;
        const porte = c.portes.find(function (p) { return p.interieur === 'terminus'; });
        o.entrer(porte);
        const piece = L.B.interieur, a = piece.apparition;
        const commis = piece.gens.find(function (g) { return g.qui === 'commis'; });
        const ailleurs = { x: 1, y: a.y - 2 };
        const vers = function (t) {
            return L.Monde.chemin(a.x * T + 8, a.y * T + 8, t.x * T + 8, t.y * T + 8, L.Monde.MASQUE_A_PIED);
        };
        return { derriere: vers(commis), devant: vers(ailleurs) };
    }""")
    assert r["devant"], "le A* ne trouve plus rien dans la piece : le juge ne mesure rien"
    assert r["derriere"] is None, "le chemin a pied enjambe le comptoir : %s" % r["derriere"]
