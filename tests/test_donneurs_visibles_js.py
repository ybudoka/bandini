"""Les donneurs se voient : aucun n'est caché par du décor peint devant lui — au banc.

⚠️ Rouge avant (20 sept. 2026), retour de Martin avec une capture : « ici Ti-Paul est caché par
l'arrêt, mets un garde pour éviter ça ». La ville se peint du nord au sud (`Entites.dessiner`
trie par `y`) et `poserDonneur` mettait le personnage à deux tuiles de sa porte sans regarder
ce qui se peint devant lui : l'abribus, une tuile plus bas, le recouvrait, et il n'en restait que
la tête. Le juge compte, pour chaque personnage de l'histoire, la part de son sprite que du décor
peint APRÈS lui recouvre (rectangles des fiches, pixels transparents compris : c'est prudent).

⚠️ Il refait le calcul de son côté, avec les vraies dimensions du sprite (`Entites.imageDe`) : un
juge qui appellerait la fonction du jeu serait d'accord avec elle même quand elle se trompe.

⚠️ Rouge du 29 sept. 2026 (« maitre : il n'est pas là (dedans) », puis « cindy : … (dehors) ») : le
juge supposait que TOUS les personnages de l'histoire sont là dès la naissance de la partie. Depuis
9ee0ae6f, un personnage peut n'ARRIVER qu'après une mission (`arrive_apres` : le vieux maître en
Floride jusqu'à c04, Cindy devant la cantine après q04, puis Diane, Jo, Zed, Ti-Loup, Prévost…), et
c'est voulu — posé dès l'ouverture, il décalerait les identifiants de toute la ville. Les donneurs se
posent au chargement : le juge regarde donc ceux-là APRÈS leur mission d'arrivée, partie rechargée,
et vérifie en passant qu'ils ne sont pas déjà là à la naissance.
"""

#: Au-delà de cette part de son sprite sous du décor, un personnage est caché.
CACHE_MAX = 0.5

PART_CACHEE = """
  function partCachee(L, e) {
    const img = L.Entites.imageDe(e), w = img.canvas.width, h = img.canvas.height;
    const x0 = e.x - img.ancre[0], y0 = e.y - img.ancre[1];
    let cache = 0; const par = [];
    for (const d of L.B.entites) {
      if (!d.decor || d.dessine === false) continue;
      const f = L.DECORS[d.decor]; if (!f) continue;
      // Peint APRES lui : plus bas, ou à la même hauteur avec un numéro plus grand.
      if (!(d.y > e.y || (d.y === e.y && d.id > e.id))) continue;
      const dx0 = d.x - f.ancre[0], dy0 = d.y - f.ancre[1] - (d.altitude || 0);
      const ox = Math.min(x0 + w, dx0 + f.w) - Math.max(x0, dx0);
      const oy = Math.min(y0 + h, dy0 + f.h) - Math.max(y0, dy0);
      if (ox > 0 && oy > 0) { cache += ox * oy; par.push(d.decor); }
    }
    return { part: Math.min(1, cache / (w * h)), par: par };
  }
"""


def test_aucun_donneur_n_est_cache_par_du_decor(banc):
    """Dehors, à la naissance de la partie ; dedans, en entrant chez eux. Ceux qui n'arrivent
    qu'après une mission (`arrive_apres`) : absents à la naissance, jugés une fois arrivés."""
    r = banc("function (L, o) {" + PART_CACHEE + """
        function juger(tardifs) {
          const persos = L.B.defs.personnages.filter(function (q) { return !!q.arrive_apres === tardifs; }), vus = [];
          for (const p of persos.filter(function (q) { return q.ou.indexOf('porte:') === 0; })) {
            const e = L.Histoire.donneur(p.slug);
            vus.push({ slug: p.slug, dehors: true, present: !!e, cache: e ? partCachee(L, e) : null });
          }
          for (const p of persos.filter(function (q) { return q.ou.indexOf('point:') === 0; })) {
            if (L.B.interieur) L.Jeu.quitterLaPiece();
            const piece = L.Histoire.pieceDuPoint(p.ou.slice(6));
            // ⚠️ UN ÉTAGE n'a pas de porte en ville (le maire, dans la chambre de l'hôtel) : on entre par la
            // pièce dont l'escalier y monte, et on monte — comme le saut du debug (`allerChezLeDonneur`).
            const dessous = L.Histoire.pieceDessous(piece.slug);
            const porte = L.Monde.carte.portes.find(function (q) { return q.lieu === piece.slug; })
              || L.Monde.carte.portes.find(function (q) { return q.lieu === dessous; });
            o.entrer(porte);
            if (L.B.interieur && L.B.interieur.slug !== piece.slug) { L.Jeu.changerEtage(piece.slug); L.Jeu.finirTransition(); }
            const e = L.Histoire.donneur(p.slug);
            vus.push({ slug: p.slug, dehors: false, present: !!e, cache: e ? partCachee(L, e) : null });
          }
          if (L.B.interieur) L.Jeu.quitterLaPiece();
          return vus;
        }
        L.Jeu.commencer();
        const tardifs = L.B.defs.personnages.filter(function (q) { return q.arrive_apres; });
        const trop_tot = tardifs.filter(function (p) { return L.Histoire.donneur(p.slug); }).map(function (p) { return p.slug; });
        const vus = juger(false);
        // Leurs missions d'arrivée faites, la partie rechargée : c'est au chargement qu'ils se posent.
        tardifs.forEach(function (p) { L.B.partie.missionsFaites[p.arrive_apres] = 1; });
        L.Jeu.retourTitre(); L.Jeu.commencer();
        return { vus: vus, arrives: juger(true), trop_tot: trop_tot, tardifs: tardifs.length };
    }""")
    assert not r["trop_tot"], f"déjà là à la naissance, avant leur mission d'arrivée : {r['trop_tot']}"
    assert r["tardifs"] >= 2 and len(r["arrives"]) == r["tardifs"], r["arrives"]
    assert len(r["vus"]) >= 9, f"le juge ne voit que {len(r['vus'])} personnages : {r['vus']}"
    for v in r["vus"] + r["arrives"]:
        assert v["present"], f"{v['slug']} : il n'est pas là ({'dehors' if v['dehors'] else 'dedans'})"
        assert v["cache"]["part"] < CACHE_MAX, (
            f"{v['slug']} est caché à {v['cache']['part']:.0%} par {v['cache']['par']} "
            f"({'dehors' if v['dehors'] else 'dedans'})")


def test_un_donneur_repose_se_tient_au_meme_endroit_et_ne_tire_aucun_de(banc):
    """Le garde n'a ni dé ni mémoire : reposer un donneur (le debug le fait) le remet où il
    était, et la pose consomme les mêmes dés que sans le garde — deux tirages, ceux de
    `creerPieton`, comme pour tout le monde."""
    r = banc("function (L, o) {" + PART_CACHEE + """
        L.Jeu.commencer();
        const p = L.B.defs.personnages.find(function (q) { return q.slug === 'tipaul'; });
        const e = L.Histoire.donneur('tipaul');
        const avant = { x: e.x, y: e.y };
        L.Entites.retirer(e);
        L.graine(4242);
        const a = L.B.rng(); L.graine(4242);
        const neuf = L.Histoire.poserDonneur(p);
        const apres = L.B.rng();
        L.graine(4242); L.B.rng(); L.B.rng(); const attendu = L.B.rng();
        return { avant: avant, apres: { x: neuf.x, y: neuf.y }, de: apres, attendu: attendu, cache: partCachee(L, neuf).part };
    }""")
    assert r["apres"] == r["avant"], f"reposé ailleurs : {r['avant']} -> {r['apres']}"
    assert r["de"] == r["attendu"], "la pose ne consomme pas les deux dés de `creerPieton`, ni plus ni moins"
    assert r["cache"] < CACHE_MAX


#: Deux personnages de l'histoire se tiennent au moins à tant de tuiles l'un de l'autre (en carré).
#: ⚠️ Écrit ici, pas relu dans `histoire.js` : un juge qui relit la règle qu'il juge ne rougit jamais.
ECART_TUILES = 2


def test_deux_donneurs_ne_se_tiennent_jamais_sur_la_meme_tuile(banc):
    """Retour de Martin (22 sept. 2026, capture du dépanneur) : « trop de choses collé devant chez
    Ti-Paul ». Ti-Paul et Xavier attendent à la même porte, et `placeVisible` les posait sur le MÊME
    pixel : deux bulles l'une sur l'autre, un seul bonhomme. Ti-Guy, Mo et Fern étaient trois sur la
    même tuile du terminus. Ici, à la naissance de la partie, et encore après le départ de Ti-Guy
    (m1 faite : Mo et Fern se partagent le terminus sans lui).

    ⚠️ Et une fois TOUT LE MONDE ARRIVÉ (30 sept. 2026, capture de la fourrière) : le juge ne regardait
    que la naissance, et Ti-Loup et Gros-Boulon n'arrivent qu'après s01 et s02 (`arrive_apres`). Gros-
    Boulon, troisième à la porte de la fourrière, avait épuisé ses essais (la cour est de l'asphalte,
    pas du trottoir) et retombait sur la première place — celle de Gilles, au pixel près."""
    r = banc("""function (L, o) {
        function places() {
          return L.B.defs.personnages.filter(function (q) { return q.ou.indexOf('porte:') === 0; })
            .map(function (p) { const e = L.Histoire.donneur(p.slug); return e ? [p.slug, p.ou, e.x, e.y] : null; })
            .filter(Boolean);
        }
        L.Jeu.commencer();
        const depart = places();
        L.B.entites.filter(function (e) { return e.type === 'pieton' && e.personnage; }).forEach(L.Entites.retirer);
        L.B.partie.missionsFaites.m1 = true;
        L.Histoire.creerDonneurs();
        const apres_m1 = places();
        // Leurs missions d'arrivée faites, la partie rechargée : c'est au chargement qu'ils se posent.
        L.B.defs.personnages.forEach(function (p) { if (p.arrive_apres) L.B.partie.missionsFaites[p.arrive_apres] = 1; });
        L.Jeu.retourTitre(); L.Jeu.commencer();
        return { depart: depart, apres_m1: apres_m1, tous_arrives: places() };
    }""")
    for moment, places in r.items():
        assert len(places) >= 10, f"{moment} : le juge ne voit que {len(places)} donneurs"
        colles = [(a[0], b[0], (a[2] // 16, a[3] // 16), (b[2] // 16, b[3] // 16))
                  for i, a in enumerate(places) for b in places[i + 1:]
                  if max(abs(a[2] - b[2]), abs(a[3] - b[3])) < ECART_TUILES * 16]
        assert not colles, f"{moment} : donneurs collés {colles}"
    assert "ti_guy" not in {p[0] for p in r["apres_m1"]}, "Ti-Guy n'est pas parti après m1"
    partages = [p for p in r["depart"] if p[1] in ("porte:depanneur", "porte:terminus")]
    assert len(partages) >= 5, partages
    assert {"tiloup", "boulon"} <= {p[0] for p in r["tous_arrives"]}, r["tous_arrives"]


def test_le_gardien_et_le_ferrailleur_se_tiennent_dans_la_cour_de_la_fourriere(banc):
    """Retour de Martin (30 sept. 2026, capture) : « ils sont trop collés, et certains devraient être
    dans les clôtures de la fourrière ». La porte de la guérite donne SUR LA COUR, derrière le
    grillage : Gilles (le gardien du lot) et Ti-Loup (le ferrailleur, qui y achète les épaves) s'y
    tiennent, près de la guérite. Gros-Boulon, le chef de la gang qui a volé la remorqueuse, reste
    dehors, contre la clôture. Aucun ne se tient sur une case du lot : un char saisi y est garé."""
    r = banc("""function (L, o) {
        L.B.defs.personnages.forEach(function (p) { if (p.arrive_apres) L.B.partie.missionsFaites[p.arrive_apres] = 1; });
        L.Jeu.commencer();
        const lot = L.Monde.carte.fourriere, gens = {};
        ['gilles', 'tiloup', 'boulon'].forEach(function (slug) {
          const e = L.Histoire.donneur(slug);
          if (!e) return;
          const tx = Math.floor(e.x / 16), ty = Math.floor(e.y / 16);
          gens[slug] = { tx: tx, ty: ty, mur: L.Monde.bloque(tx, ty, L.Monde.MASQUE_PIETON) };
        });
        return { lot: { x: lot.x, y: lot.y, l: lot.largeur, h: lot.hauteur, porte: lot.porte,
                        places: lot.places.map(function (p) { return [p.x, p.y, p.sens]; }) }, gens: gens };
    }""")
    lot, gens = r["lot"], r["gens"]
    assert set(gens) == {"gilles", "tiloup", "boulon"}, gens

    def dans_la_cour(g):
        # En dedans du grillage : la clôture est le tour du rectangle.
        return lot["x"] < g["tx"] < lot["x"] + lot["l"] - 1 and lot["y"] < g["ty"] < lot["y"] + lot["h"] - 1

    # Une case : son fond (le pare-chocs) et les deux tuiles derrière, à reculons de son sens.
    recul = {"N": (0, 1), "S": (0, -1), "O": (1, 0), "E": (-1, 0)}
    cases = {(p[0] + recul[p[2]][0] * k, p[1] + recul[p[2]][1] * k) for p in lot["places"] for k in range(3)}
    for slug in ("gilles", "tiloup"):
        g = gens[slug]
        assert dans_la_cour(g), f"{slug} n'est pas dans la cour de la fourrière : {g}, lot {lot}"
        assert not g["mur"], f"{slug} se tient dans un mur : {g}"
        assert (g["tx"], g["ty"]) not in cases, f"{slug} se tient sur une case du lot : {g}"
        porte = lot["porte"]
        assert max(abs(g["tx"] - porte["x"]), abs(g["ty"] - porte["y"])) <= 8, f"{slug} est loin de la guérite : {g}"
        # Le long de la guérite, face aux chars : pas au fond, contre le grillage.
        assert g["ty"] == porte["y"], f"{slug} ne se tient pas le long de la guérite : {g}, porte {porte}"
    assert not dans_la_cour(gens["boulon"]), f"Gros-Boulon est entré dans la cour : {gens['boulon']}"
    # « Trop collés » : trois tuiles au moins entre deux d'entre eux (écrit ici, pas relu dans le jeu).
    trio = list(gens.items())
    colles = [(a, b) for i, (a, ga) in enumerate(trio) for b, gb in trio[i + 1:]
              if max(abs(ga["tx"] - gb["tx"]), abs(ga["ty"] - gb["ty"])) < 3]
    assert not colles, f"collés : {colles} — {gens}"


def test_le_second_donneur_d_une_porte_ne_se_glisse_pas_entre_deux_meubles(banc):
    """Le second donneur d'une porte prend une place ou il ne touche aucun meuble solide : c'est
    entre l'edicule du metro et le guichet que Ti-Paul se rabattait, colle aux deux. Au depanneur :
    Ti-Paul a deux tuiles de la porte, Xavier plus loin sur la meme facade, a l'air libre."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const porte = L.Monde.carte.def.portes.find(function (q) { return q.lieu === 'depanneur'; });
        const donne = {};
        ['tipaul', 'xavier'].forEach(function (slug) {
          const e = L.Histoire.donneur(slug);
          const tx = Math.floor(e.x / 16), ty = Math.floor(e.y / 16);
          const meubles = L.B.entites.filter(function (d) {
            return d.decor && d.solide && Math.max(Math.abs(Math.floor(d.x / 16) - tx), Math.abs(Math.floor(d.y / 16) - ty)) <= 1;
          }).map(function (d) { return d.decor; });
          donne[slug] = { tx: tx, ty: ty, meubles: meubles };
        });
        return { porte: [porte.x, porte.y], donne: donne };
    }""")
    px, py = r["porte"]
    tipaul, xavier = r["donne"]["tipaul"], r["donne"]["xavier"]
    assert (tipaul["tx"], tipaul["ty"]) == (px + 2, py + 1), f"Ti-Paul n'est plus à deux tuiles de sa porte : {tipaul}"
    assert xavier["ty"] == py + 1 and abs(xavier["tx"] - px) >= 3, f"Xavier : {xavier}"
    assert not xavier["meubles"], f"Xavier se glisse contre {xavier['meubles']}"
