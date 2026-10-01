"""Les chemins des blocs, JOUÉS (docs/jalons/une-route-en-lacets-vers-le-chalet.md)."""

from test_blocs_js import OUTILS, VOLANT


def test_une_auto_roule_plus_vite_sur_le_chemin_que_sur_l_herbe(banc):
    """Le même char, la même pédale, deux sols : l'herbe (`terre`) le ralentit, le chemin roulé non."""
    r = banc("""async function (L, o) {
        L.Jeu.commencer(); L.B.partie.jour = 21;
        const TT = 16, c = L.Monde.carte, j = L.B.joueur;
        // Une rangée d'herbe, puis la même rangée repeinte en chemin : on y lance l'auto.
        function essai(glyphe) {
          const y = 5, ligne = c.sol[y];
          c.sol[y] = ligne.slice(0, 2) + glyphe.repeat(40) + ligne.slice(42);
          const v = L.Vehicules.creer('auto', 4 * TT, y * TT + 8, 0, { etat: 'stationne' });
          j.x = v.x; j.y = v.y + 12; L.Entites.indexer(); L.Vehicules.monter(j, v); L.Entites.indexer();
          o.touche('KeyW'); for (let i = 0; i < 60; i++) o.frame(1); o.relacher('KeyW');
          const dx = v.x - 4 * TT;
          // ⚠️ `force` : à cette vitesse, un `descendre` poli refuse (garde > 1,2) et laisse le
          // joueur dans le char — le prochain `monter` échouerait en silence (dx figé à 0).
          L.Vehicules.descendre(j, true); c.sol[y] = ligne;
          return dx;
        }
        return { herbe: essai(','), chemin: essai('§') };
    }""")
    assert r["chemin"] > r["herbe"] * 1.1, r


def test_au_rang_le_ruban_est_peint_sous_la_neige(banc):
    """⚠️ Une partie commence en janvier : un ruban peint APRÈS la neige ferait une route brune dans un rang
    blanc. `Jeu.rendre()` (pas `frame`, qui fait bouger le monde) ; on note l'ordre des peintres."""
    r = banc("async function (L, o) {" + OUTILS + """
        L.Jeu.commencer();
        auPassage(L, o); await laisserArriver(L, o); pousser(L, o, 'KeyA');
        const B = L.B, ch = B.bloc.def.bloc.chemins[0], p = ch.points[Math.floor(ch.points.length / 2)];
        B.joueur.x = p[0]; B.joueur.y = p[1]; L.Entites.indexer();
        for (let i = 0; i < 3; i++) o.frame(1);
        const ordre = [], neige = L.Neige.dessinerSol, ruban = L.Blocs.dessinerChemins;
        L.Neige.dessinerSol = function () { ordre.push('neige'); return neige.apply(this, arguments); };
        L.Blocs.dessinerChemins = function (ctx) {
          const trait = ctx.stroke; let n = 0;
          ctx.stroke = function () { n++; return trait.apply(this, arguments); };
          const r = ruban.apply(this, arguments); ctx.stroke = trait;
          ordre.push('ruban:' + n); return r;
        };
        L.Jeu.rendre();
        L.Neige.dessinerSol = neige; L.Blocs.dessinerChemins = ruban;
        return { bloc: B.bloc && B.bloc.slug, ordre: ordre, points: ch.points.length, largeur: ch.largeur_px };
    }""")
    assert r["bloc"] == "rang" and r["largeur"] == 48 and r["points"] > 300, r
    peints = [o for o in r["ordre"] if o.startswith("ruban:")]
    assert peints and int(peints[0].split(":")[1]) >= 2, f"le ruban n'a rien tracé : {r['ordre']}"
    assert r["ordre"].index(peints[0]) < r["ordre"].index("neige"), f"le ruban est peint sur la neige : {r['ordre']}"


def test_au_volant_on_suit_la_route_jusqu_au_chalet_et_on_en_revient(banc):
    """On arrive de la ville au volant, et un pilote simple suit le tracé (le cap vers un point 32 px plus
    loin, la pédale enfoncée) : il atteint la place du char du chalet sans rester collé à un tronc, puis
    refait le chemin à l'envers jusqu'au bord est. ⚠️ Le cap est POSÉ, pas braqué : on juge que la route se
    roule (pas d'arbre, pas de mur, la vitesse du chemin), pas l'adresse du pilote."""
    r = banc("async function (L, o) {" + OUTILS + VOLANT + """
        L.Jeu.commencer(); L.B.partie.jour = 21;
        const B = L.B;
        auPassage(L, o); await laisserArriver(L, o);
        const v = auVolant(L, o, 'auto'); foncer(L, o, 60);
        if (!B.bloc) return { bloc: null };
        const ch = B.bloc.def.bloc.chemins[0].points, c = B.bloc.def.bloc.planque.char;
        const place = [c.x * TT + 8, c.y * TT + 8];
        // ⚠️ L'écart à la route ne se mesure que pendant qu'on vise un point DE LA ROUTE (`route` : ses indices
        // dans `cibles`), et dans le bloc : la place du char est à ~80 px du bout du chemin, et la ville n'a pas de route.
        function conduire(cibles, n, route) {
          let i = 0, colle = 0, avant = [v.x, v.y], ecart = 0;
          o.touche('KeyW');
          for (let f = 0; f < n; f++) {
            while (i < cibles.length - 1 && Math.hypot(cibles[i][0] - v.x, cibles[i][1] - v.y) < 32) i++;
            v.angle = Math.atan2(cibles[i][1] - v.y, cibles[i][0] - v.x);
            if (v.vitesse > 2.2) o.relacher('KeyW'); else o.touche('KeyW');   // lent : la conduite simulée
            o.frame(1);
            if (B.bloc && i >= route[0] && i <= route[1]) ecart = Math.max(ecart, Math.min.apply(null, ch.map(function (p) { return Math.hypot(p[0] - v.x, p[1] - v.y); })));
            if (f % 60 === 59) { colle = Math.hypot(v.x - avant[0], v.y - avant[1]) < 4 ? colle + 1 : 0; avant = [v.x, v.y]; }
            if (colle >= 3 || !B.bloc || (i === cibles.length - 1 && Math.hypot(cibles[i][0] - v.x, cibles[i][1] - v.y) < 12)) break;
          }
          o.relacher('KeyW');
          return { colle: colle >= 3, x: Math.round(v.x), y: Math.round(v.y), ecart: Math.round(ecart), bloc: B.bloc && B.bloc.slug };
        }
        const aller = conduire(ch.concat([place]), 9000, [0, ch.length - 1]);
        const auChalet = Math.hypot(v.x - place[0], v.y - place[1]);
        const retour = conduire([place].concat(ch.slice().reverse()), 9000, [1, ch.length]);
        return { bloc: 'rang', aller: aller, auChalet: Math.round(auChalet), retour: retour,
                 largeur: B.bloc ? B.bloc.def.bloc.chemins[0].largeur_px : null };
    }""")
    assert r["bloc"] == "rang", r
    assert not r["aller"]["colle"] and r["auChalet"] < 16, f"le char n'atteint pas le chalet : {r}"
    assert r["aller"]["ecart"] <= 40, f"le pilote a quitté la route : {r}"
    # Au retour, le char repasse le bord est : on est revenu en ville (ou collé au bord, à moins d'une tuile).
    assert not r["retour"]["colle"] and (r["retour"]["bloc"] is None or r["retour"]["x"] > 78 * 16), r
