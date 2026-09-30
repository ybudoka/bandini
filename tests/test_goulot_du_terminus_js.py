"""Le goulot du terminus (docs/jalons/le-goulot-du-terminus.md).

Au départ d'une partie, près du terminus, le joueur qui marchait dans la foule écrasait un passant contre un
autre corps — un passant, Momo planté à son poste : coincé, le passant recevait deux poussées qui
s'annulaient, et le joueur qui avançait encore l'enfonçait dans l'autre (`test_la_foule_ne_se_traverse_plus`,
3 graines sur 10). Ici, le geste seul, à la main : un homme figé, une passante collée à lui, et le joueur qui
marche droit sur elle au clavier. Elle ne s'enfonce pas dans l'homme, et c'est le joueur qui se bute.
"""


def test_le_joueur_n_ecrase_pas_une_passante_contre_un_homme_fige(banc):
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        if (L.B.menu) L.Hud.fermerMenu();
        L.B.partie.heure = 0.5;
        const c = L.Monde.carte, M = L.Monde, TT = L.TT;
        // Sept tuiles de trottoir libres d'est en ouest, loin de la chaussee (deux rangees au-dessus et
        // au-dessous aussi) : ni bordure, ni mur, rien d'autre qui retienne qui que ce soit.
        function scene() {
            for (let y = 20; y < c.h - 4; y++) for (let x = 12; x < c.w - 12; x++) {
                let ok = true;
                for (let k = -4; k <= 4 && ok; k++) for (let dy = -1; dy <= 1 && ok; dy++) {
                    ok = M.estTrottoir(x + k, y + dy) && !M.bloque(x + k, y + dy, M.MASQUE_PIETON) && !M.estChaussee(x + k, y + dy)
                      && !M.devantDUnePorte(x + k, y + dy);
                }
                if (ok && !L.Entites.decorAutour(x * TT + 8, y * TT + 8, 70).some(function (d) { return d.solide; })) return { tx: x, ty: y };
            }
            return null;
        }
        const s = scene();
        if (!s) return { trouve: false };
        const x0 = s.tx * TT + 8, y0 = s.ty * TT + 8, j = L.B.joueur;
        // Personne d'autre a l'entour : on ne mesure que ces trois-la.
        L.B.entites.filter(function (e) { return e.type === 'pieton' && Math.hypot(e.x - x0, e.y - y0) < 200; }).forEach(function (e) { L.Entites.retirer(e); });
        const homme = L.Entites.creerPieton(x0 - 20, y0, L.Entites.archetype('ouvrier'));
        homme.etat = 'fige'; homme.intouchable = true; homme.plante = { x: homme.x, y: homme.y };
        const elle = L.Entites.creerPieton(x0 - 10, y0, L.Entites.archetype('passante'));
        elle.etat = 'arret'; elle.minuterie = 100000; elle.intouchable = true;
        j.x = x0 + 12; j.y = y0; j.vx = 0; j.vy = 0; j.intouchable = true; j.invincible = 1e9;
        L.Monde.centrerCamera(j.x, j.y); L.Entites.indexer();
        let pire = 0, colle = 0;
        o.touche('KeyA');
        for (let i = 0; i < 120; i++) {
            o.frame(1);
            elle.etat = 'arret';   // elle attend, elle ne s'en va pas d'elle-meme
            const d = Math.hypot(elle.x - homme.x, elle.y - homme.y);
            pire = Math.max(pire, elle.r + homme.r - d);
            if (Math.hypot(j.x - elle.x, j.y - elle.y) < j.r + elle.r - 1.5) colle++;
        }
        o.relacher('KeyA');
        return { trouve: true, pire: +pire.toFixed(2), colle: colle, joueur: Math.round(j.x - x0) };
    }""")
    assert r["trouve"], "aucun trottoir libre de sept tuiles dans la ville"
    assert r["pire"] <= 1.0, f"la passante s'enfonce de {r['pire']} px dans l'homme figé"
    assert r["colle"] <= 3, f"le joueur entre dans la passante {r['colle']} images sur 120"
