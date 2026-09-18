def test_canards(banc):
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const g = L.Foire.jeux().find(function (q) { return q.slug === 'peche_canards'; });
        const j = L.B.joueur;
        j.x = g.x * L.TT + 8; j.y = (g.y + 2) * L.TT + 8;
        L.Entites.indexer();
        o.frame(1);
        const sous = L.Foire.jeuSousLaMain(j);
        o.tape('KeyE'); o.frame(1);
        o.tape('KeyE'); o.frame(1);
        const parti = L.B.defi && L.B.defi.slug;
        // On joue COMME UN JOUEUR : on regarde le bassin, et on tire quand le
        // fil descend. (Ici : on lit `canardAuCrochet`, ce que le dessin montre.)
        const lignes = [];
        let n = 0;
        for (let k = 0; k < 2400 && L.B.defi; k++) {
          if (L.Histoire.canardAuCrochet()) { o.tape('KeyE'); n++; }
          o.frame(1);
          if (k % 400 === 0) lignes.push(L.Histoire.ligneObjectif());
        }
        return { sous: sous, parti: parti, appuis: n, lignes: lignes,
                 faits: L.B.partie.defisFaits, argent: L.B.partie.argent, tenues: L.B.partie.tenues };
    }""")
    print(r)
