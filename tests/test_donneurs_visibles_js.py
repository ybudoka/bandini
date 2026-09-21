"""Les donneurs se voient : aucun n'est caché par du décor peint devant lui — au banc.

⚠️ Rouge avant (20 sept. 2026), retour de Martin avec une capture : « ici Ti-Paul est caché par
l'arrêt, mets un garde pour éviter ça ». La ville se peint du nord au sud (`Entites.dessiner`
trie par `y`) et `poserDonneur` mettait le personnage à deux tuiles de sa porte sans regarder
ce qui se peint devant lui : l'abribus, une tuile plus bas, le recouvrait, et il n'en restait que
la tête. Le juge compte, pour chaque personnage de l'histoire, la part de son sprite que du décor
peint APRÈS lui recouvre (rectangles des fiches, pixels transparents compris : c'est prudent).

⚠️ Il refait le calcul de son côté, avec les vraies dimensions du sprite (`Entites.imageDe`) : un
juge qui appellerait la fonction du jeu serait d'accord avec elle même quand elle se trompe.
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
    """Dehors, à la naissance de la partie ; dedans, en entrant chez eux."""
    r = banc("function (L, o) {" + PART_CACHEE + """
        L.Jeu.commencer();
        const persos = L.B.defs.personnages, vus = [];
        for (const p of persos.filter(function (q) { return q.ou.indexOf('porte:') === 0; })) {
          const e = L.Histoire.donneur(p.slug);
          vus.push({ slug: p.slug, dehors: true, present: !!e, cache: e ? partCachee(L, e) : null });
        }
        for (const p of persos.filter(function (q) { return q.ou.indexOf('point:') === 0; })) {
          if (L.B.interieur) L.Jeu.quitterLaPiece();
          const piece = L.Histoire.pieceDuPoint(p.ou.slice(6));
          o.entrer(L.Monde.carte.portes.find(function (q) { return q.lieu === piece.slug; }));
          const e = L.Histoire.donneur(p.slug);
          vus.push({ slug: p.slug, dehors: false, present: !!e, cache: e ? partCachee(L, e) : null });
        }
        return vus;
    }""")
    assert len(r) >= 9, f"le juge ne voit que {len(r)} personnages : {r}"
    for v in r:
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
