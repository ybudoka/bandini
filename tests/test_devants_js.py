"""Rien devant une porte, cote jeu — ce que les missions posent ne se plante pas sur un pas de porte.

`app/devants.py` degage la ville ; ici on juge le jeu, qui pose SON monde par-dessus : le donneur
qui attend, les hommes de main d'une mission, le panneau d'un defi. Un personnage plante devant
un commerce est un obstacle qu'on contourne pour entrer.
"""


def test_le_devant_d_une_porte_se_lit_dans_la_ville(banc, paquet):
    """Trois tuiles dans l'axe, une de chaque cote — la fenetre vient de la ville (`def.devant`),
    et les portes peintes en ont une comme les vraies."""
    assert paquet["carte"]["devant"] == {"cote": 1, "profondeur": 3}
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const def = L.Monde.carte.def;
        const p = def.portes.find(function (q) { return def.sol[q.y][q.x] === 'D'; });
        const dev = def.devantures.find(function (f) { return f.motifs.indexOf('P') >= 0; });
        const px = dev.x + dev.motifs.indexOf('P'), py = dev.y;
        const d = L.Monde.devantDUnePorte;
        return {
          axe: [1, 2, 3].map(function (j) { return d(p.x, p.y + j); }),
          flancs: [d(p.x - 1, p.y + 1), d(p.x + 1, p.y + 2), d(p.x - 1, p.y + 3)],
          dehors: [d(p.x, p.y + 4), d(p.x + 2, p.y + 1), d(p.x, p.y), d(p.x, p.y - 1)],
          peinte: [d(px, py + 1), d(px, py + 3)], peinteDehors: d(px, py + 4),
        };
    }""")
    assert r["axe"] == [True, True, True]
    assert r["flancs"] == [True, True, True]
    assert r["dehors"] == [False, False, False, False], "au-dela de la fenetre, la tuile est libre"
    assert r["peinte"] == [True, True] and r["peinteDehors"] is False, "une porte peinte est une porte"


def test_le_chantier_du_jour_ecarte_passe_au_suivant(banc):
    """⚠️ Le jeu tire la voie fermee du jour dans la liste ENTIERE (`hash % longueur`) : une entree
    de moins rebattrait tous les jours. Celle que Python a ecartee (`ecartee`) est donc sautee, et
    on passe a la suivante — un jour dont le tirage ne tombait pas dessus ne change pas."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const def = L.Monde.carte.def, p = L.B.partie;
        const tous = def.entraves.concat(def.fermetures);
        const nonEcarteesAvant = tous.filter(function (c) { return !c.ecartee; }).length;
        // Un jour, le tirage tombe sur une entree ; on l'ecarte, et le meme jour donne la suivante.
        p.jour = 5;
        const b0 = L.Monde.entraveDuJour();
        const c0 = tous.find(function (c) { return c.x === b0.x && c.y === b0.y; });
        c0.ecartee = 1;
        p.jour = 6; L.Monde.entraveDuJour(); p.jour = 5;             // vide le cache de la journee
        const b1 = L.Monde.entraveDuJour();
        const suivante = tous[(tous.indexOf(c0) + 1) % tous.length];
        c0.ecartee = 0;
        // Sur deux cents jours, la voie du jour n'est jamais une ecartee.
        const ecartee = tous.find(function (c) { return c.ecartee; });
        let ecarteeVue = 0;
        for (let jour = 1; jour <= 200; jour++) {
          p.jour = jour;
          const b = L.Monde.entraveDuJour();
          if (b && ecartee && b.x === ecartee.x && b.y === ecartee.y) ecarteeVue++;
        }
        return { nonEcarteesAvant: nonEcarteesAvant, total: tous.length,
                 saute: b1 && (b1.x !== b0.x || b1.y !== b0.y), bonne: b1 && b1.x === suivante.x && b1.y === suivante.y,
                 ecarteeVue: ecarteeVue, uneEcartee: !!ecartee };
    }""")
    assert r["nonEcarteesAvant"] < r["total"], "la ville a bien des voies ecartees devant une porte"
    assert r["saute"] is True and r["bonne"] is True, "l'ecartee passe a la suivante"
    assert r["uneEcartee"] and r["ecarteeVue"] == 0, "une voie ecartee ne sort jamais comme voie du jour"


def test_le_bris_d_aqueduc_ecarte_passe_au_suivant(banc):
    """Meme regle pour le bris : tire dans la liste entiere, jamais sur un bris qui tombe devant
    une porte. Trente jours d'heures — assez de bris pour que le juge ne soit pas vide."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const def = L.Monde.carte.def, p = L.B.partie;
        const ecartes = def.aqueducs.filter(function (c) { return c.ecartee; });
        let bris = 0, surUnEcarte = 0;
        for (let jour = 1; jour <= 30; jour++) for (let h = 0; h < 24; h++) {
          p.jour = jour; p.heure = (h * 60 + 5) / 1440;
          const b = L.Monde.brisDAqueduc();
          if (!b) continue;
          bris++;
          if (ecartes.some(function (c) { return c.x === b.x && c.y === b.y; })) surUnEcarte++;
        }
        return { ecartes: ecartes.length, total: def.aqueducs.length, bris: bris, surUnEcarte: surUnEcarte };
    }""")
    assert r["ecartes"] >= 1 and r["ecartes"] < r["total"]
    assert r["bris"] >= 30, "le juge ne voit pas assez de bris pour valoir quelque chose"
    assert r["surUnEcarte"] == 0, "un bris tombe devant une porte"


def test_une_piece_n_a_pas_de_devant_de_porte(banc):
    """Dedans, la sortie a son propre juge (`test_aucun_comptoir_ne_vole_la_porte`) : le jeu ne
    lit de devant que dans la ville."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const porte = L.Monde.carte.def.portes.find(function (q) { return q.interieur === 'garage'; });
        L.Jeu.entrer(porte);
        o.frame(90);
        return { piece: !!L.B.interieur, devant: L.Monde.devantDUnePorte(6, 5) };
    }""")
    assert r["piece"] is True and r["devant"] is False


def test_une_tuile_libre_de_mission_n_est_jamais_devant_une_porte(banc):
    """⚠️ `Histoire.tuileLibre` est ou les missions posent leur monde (le donneur, les hommes de
    main, le fuyard, l'escorte). Elle rendait la premiere tuile marchable en spirale — et pour un
    lieu, le centre de la spirale EST le pas de la porte. Le juge tire un point sur chacune des
    portes de la ville : aucune reponse devant une porte, sauf faute de mieux dans le rayon."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const def = L.Monde.carte.def;
        const mauvaises = [];
        let essais = 0, perdues = 0;
        // ⚠️ L'ancienne regle, telle quelle : la premiere tuile marchable hors chaussee. Une porte
        // qu'elle ne servait pas (la fourriere, au fond de sa cour grillagee) n'est pas ma faute.
        const ancienne = function (tx, ty) {
          for (let r = 0; r <= 3; r++) for (let dy = -r; dy <= r; dy++) for (let dx = -r; dx <= r; dx++) {
            if (Math.max(Math.abs(dx), Math.abs(dy)) !== r) continue;
            if (L.Monde.marchablePieton(tx + dx, ty + dy) && !L.Monde.estChaussee(tx + dx, ty + dy)) return true;
          }
          return false;
        };
        for (const p of def.portes) {
          essais++;
          const t = L.Histoire.tuileLibre(p.x * 16 + 8, (p.y + 1) * 16 + 8, 3);
          if (!t) { if (ancienne(p.x, p.y + 1)) perdues++; continue; }
          if (L.Monde.devantDUnePorte(Math.floor(t.x / 16), Math.floor(t.y / 16))) mauvaises.push([p.x, p.y, t.x, t.y]);
        }
        return { essais: essais, mauvaises: mauvaises, perdues: perdues };
    }""")
    assert r["essais"] >= 40
    assert not r["mauvaises"], f"{len(r['mauvaises'])} tuiles libres devant une porte : {r['mauvaises'][:4]}"
    assert r["perdues"] == 0, "une porte que l'ancienne regle servait n'a plus de tuile libre"


def test_faute_de_mieux_une_tuile_devant_une_porte_vaut_mieux_que_rien(banc):
    """Le repli : si tout le rayon est devant des portes, on rend la premiere venue plutot que
    de perdre le donneur. Vu ici avec un rayon de zero — la tuile meme, devant sa porte."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const p = L.Monde.carte.def.portes.find(function (q) { return q.lieu === 'garage'; });
        const t = L.Histoire.tuileLibre(p.x * 16 + 8, (p.y + 1) * 16 + 8, 0);
        return { t: t, devant: L.Monde.devantDUnePorte(p.x, p.y + 1) };
    }""")
    assert r["devant"] is True and r["t"] is not None, "sans alternative, le repli sert"


def test_les_donneurs_de_la_rue_n_attendent_pas_devant_une_porte(banc):
    """Ti-Guy a cote du terminus, Thibodeau au kiosque, Marco au garage : ils attendent A COTE de
    leur porte (`creerDonneurs`), pas sur son pas."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const donneurs = L.B.entites.filter(function (e) { return e.type === 'pieton' && e.personnage; });
        return donneurs.map(function (e) {
          return { qui: e.personnage, devant: L.Monde.devantDUnePorte(Math.floor(e.x / 16), Math.floor(e.y / 16)) };
        });
    }""")
    assert len(r) >= 3, "les donneurs de la rue existent"
    assert [d["qui"] for d in r if d["devant"]] == [], "un donneur plante devant une porte"


def test_un_panneau_de_defi_n_est_pas_devant_une_porte(banc):
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const panneaux = L.B.entites.filter(function (e) { return e.type === 'panneau'; });
        return panneaux.map(function (e) {
          return { defi: e.defi, devant: L.Monde.devantDUnePorte(Math.floor(e.x / 16), Math.floor(e.y / 16)) };
        });
    }""")
    assert r, "au moins un panneau de defi"
    assert [p["defi"] for p in r if p["devant"]] == []


def test_un_panneau_de_defi_ne_se_plante_ni_sur_un_meuble_ni_entre_deux(banc):
    """Retour de Martin (22 sept. 2026, capture du dépanneur) : « trop de choses collé devant chez
    Ti-Paul ». Le panneau de la course des Érables se plantait SUR le banc de l'abribus (`tuileLibre`
    ne regarde que la carte) ; l'arrêt parti, il se glissait entre l'édicule du métro et le guichet.
    Et au terminus, trois donneurs qui ne s'empilent plus lui prenaient toutes ses places : il
    disparaissait. Chaque panneau existe, et touche au plus un meuble, jamais dessous."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        return L.B.entites.filter(function (e) { return e.type === 'panneau'; }).map(function (e) {
          const tx = Math.floor(e.x / 16), ty = Math.floor(e.y / 16);
          const autour = L.B.entites.filter(function (d) {
            return d.decor && d.solide && d !== e
              && Math.max(Math.abs(Math.floor(d.x / 16) - tx), Math.abs(Math.floor(d.y / 16) - ty)) <= 1;
          });
          return { defi: e.defi, tuile: [tx, ty], autour: autour.map(function (d) { return d.decor; }),
                   dessous: autour.filter(function (d) { return Math.floor(d.x / 16) === tx && Math.floor(d.y / 16) === ty; })
                                  .map(function (d) { return d.decor; }) };
        });
    }""")
    defis = sorted(p["defi"] for p in r)
    assert defis == ["livraison", "saut", "tour", "tour_erables", "tour_pointe", "tour_quais", "tour_shop"], defis
    for p in r:
        assert not p["dessous"], f"le panneau {p['defi']} est planté sur {p['dessous']} en {p['tuile']}"
        assert len(p["autour"]) <= 1, f"le panneau {p['defi']} est coincé entre {p['autour']} en {p['tuile']}"
