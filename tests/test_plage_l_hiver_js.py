"""La plage l'hiver (docs/jalons/la-plage-l-hiver.md) — Martin, 30 sept. 2026 : « la plage
devrait aussi être en hiver, et les exhibitionnistes prennent une pause ».

⚠️ Le 22 est l'été (juillet), le 2 l'hiver (janvier). Pas le 21 : c'est le déménagement, qui
déplace le joueur.
"""

from app import pietons, saisons

ETE, HIVER = 22, 2

#: La plus grosse grève de la carte (comme `test_plage_js.py`), le joueur cinq tuiles au nord.
GREVE = """
    function greve(L) {
      const c = L.Monde.carte, TT = L.TT;
      function eau(tx, ty, d) {
        return L.Monde.estEau(tx + d, ty) || L.Monde.estEau(tx - d, ty)
            || L.Monde.estEau(tx, ty + d) || L.Monde.estEau(tx, ty - d);
      }
      let mieux = null, plus = 0;
      for (let ty = 6; ty < c.h - 6; ty += 2) {
        for (let tx = 6; tx < c.w - 6; tx += 2) {
          if (L.Monde.glyphe(tx, ty) !== 's' || !L.Monde.marchablePieton(tx, ty)) continue;
          if (!eau(tx, ty, 1) && !eau(tx, ty, 2)) continue;
          let n = 0;
          for (let dy = -12; dy <= 12; dy++) for (let dx = -12; dx <= 12; dx++) {
            if (L.Monde.glyphe(tx + dx, ty + dy) === 's') n++;
          }
          if (n > plus) { plus = n; mieux = { tx: tx, ty: ty, x: tx * TT + 8, y: ty * TT + 8 }; }
        }
      }
      return plus >= 40 ? mieux : null;
    }
    function surLaGreve(L, jour) {
      L.Jeu.commencer();
      L.graine(31);
      L.B.partie.jour = jour;
      L.B.partie.heure = 0.55;
      const g = greve(L);
      if (!g) return null;
      L.B.joueur.x = g.x; L.B.joueur.y = g.y - 5 * L.TT;
      // ⚠️ Invincible : sur 1 800 images, les hommes de Sal l'envoient parfois à l'hôpital, selon
      // la graine — et la grève s'oublie derrière lui.
      L.B.joueur.invincible = 1e9;
      L.Monde.centrerCamera(L.B.joueur.x, L.B.joueur.y);
      L.Entites.indexer();
      return g;
    }
    function baigneurs(L) {
      return L.B.entites.filter(function (e) { return e.metier === 'baigneur' && e.vivant; });
    }
"""


def test_la_saison_des_plages_est_l_ete_et_le_manteau_prend_conge_au_grand_froid():
    """Les seuils se lisent contre les palettes : la plage est ouverte en juillet et en août,
    fermée au printemps, à l'automne et l'hiver ; l'homme au manteau travaille encore en
    novembre et prend congé en janvier."""
    P = saisons.PALETTES
    f = pietons.PLAGE["froid_max"]
    assert P["ete"]["froid"] <= f and P["fin_ete"]["froid"] <= f, "la plage fermée en été"
    for nom in ("printemps", "automne", "novembre", "hiver"):
        assert P[nom]["froid"] > f, "on se baigne en %s" % nom
    ex = next(p for p in pietons.CATALOGUE if p["slug"] == "exhibitionniste")
    assert P["novembre"]["froid"] <= ex["froid_max"] < P["hiver"]["froid"]
    # ⚠️ Une clé nulle sur chaque archétype pèserait dans le paquet.
    assert sum(1 for p in pietons.CATALOGUE if "froid_max" in p) >= 1
    assert all(p.get("froid_max", 0) is not None for p in pietons.CATALOGUE)


def test_le_sable_de_janvier_est_sous_la_neige(banc):
    """La tuile de sable peinte en juillet garde sa couleur ; en janvier elle blanchit, comme le
    trottoir (`Saisons.enneiger`)."""
    r = banc("""function (L) {
        L.Jeu.commencer();
        function fond(jour) {
          L.B.partie.jour = jour;
          const vus = [];
          const ctx = { fillRect: function () {}, save: function () {}, restore: function () {},
                        beginPath: function () {}, fill: function () {}, rect: function () {} };
          Object.defineProperty(ctx, 'fillStyle', { set: function (v) { vus.push(v); }, get: function () { return vus[vus.length - 1]; } });
          L.TUILES['s'](ctx, 3, 16);
          return vus[0];
        }
        return { ete: fond(%d), hiver: fond(%d) };
    }""" % (ETE, HIVER))
    assert r["ete"] == "#d8c48a", "le sable de juillet a changé de couleur : %s" % r["ete"]
    bleu = int(r["hiver"][5:7], 16)
    assert bleu > 0xc8, "le sable de janvier n'est pas sous la neige : %s" % r["hiver"]


def test_la_greve_est_rangee_l_hiver_et_ressortie_l_ete(banc, paquet):
    """Sur la même grève : en juillet on peint des parasols et des serviettes et un char peut
    défoncer un château ; en janvier rien de tout ça ne se peint ni ne se casse ; revenu l'été,
    tout ressort. ⚠️ La saison change EN JEU (sans nouvelle partie) : c'est `rangerLaGreve` qui
    reindexe."""
    r = banc("""function (L, o) {
        %s
        const g = surLaGreve(L, %d);
        if (!g) return { greve: false };
        const cam = L.B.cam;
        function releve(jour) {
          L.B.partie.jour = jour;
          // ⚠️ Les autres modules reindexent le decor pour leurs raisons (le bac de l'autobus, les
          // chantiers) : on les fait taire, sinon ce juge ne verrait pas `rangerLaGreve` manquer.
          const autre = L.Entites.reindexerDecor;
          L.Entites.reindexerDecor = function () {};
          o.frame(61);
          L.Entites.reindexerDecor = autre;
          const cles = new Set();
          const cuire = L.Atlas.cuirePeintre;
          L.Atlas.cuirePeintre = function (cle) {
            if (cle.indexOf('decor|') === 0) cles.add(cle.split('|')[1]);
            return cuire.apply(null, arguments);
          };
          L.Entites.dessiner(o.ctx, cam);
          L.Atlas.cuirePeintre = cuire;
          const ete = L.B.entites.filter(function (e) { return e.ete && !e.brise; });
          const indexes = ete.filter(function (e) {
            return L.Entites.decorAutour(e.x, e.y, 1).indexOf(e) >= 0;
          }).length;
          const peints = ['parasol', 'serviette', 'chaise_longue', 'chateau_sable', 'kayak']
            .filter(function (k) { return cles.has(k); });
          return { peints: peints, ete: ete.length, indexes: indexes,
                   chateaux: ete.filter(function (e) { return e.decor === 'chateau_sable'; }).length };
        }
        return { greve: true, juillet: releve(%d), janvier: releve(%d), retour: releve(%d) };
    }""" % (GREVE, ETE, ETE, HIVER, ETE))
    assert r["greve"], "aucune grève sur la carte"
    j, h, b = r["juillet"], r["janvier"], r["retour"]
    assert j["ete"] > 0, "aucun meuble d'été dans la ville : le juge ne mesure rien"
    assert j["peints"], "en juillet, rien de la grève ne se peint à l'écran : le témoin ne dit rien"
    assert h["peints"] == [], "en janvier, la grève est encore meublée : %s" % h["peints"]
    assert j["chateaux"] > 0 and j["indexes"] > 0, "en juillet, pas un château qu'un char puisse défoncer"
    assert h["indexes"] == 0, "en janvier, %s meubles d'été invisibles se cassent encore" % h["indexes"]
    assert b["peints"] and b["indexes"] == j["indexes"], "revenu l'été, la grève ne ressort pas : %s" % b


def test_personne_ne_se_baigne_en_janvier(banc, paquet):
    """Juillet peuple la grève (le témoin) ; l'hiver arrive : qui est hors champ est rentré,
    personne ne s'évapore sous nos yeux, et il ne naît plus personne."""
    r = banc("""function (L, o) {
        %s
        const g = surLaGreve(L, %d);
        if (!g) return { greve: false };
        for (let i = 0; i < 900; i++) o.frame(1);
        const avant = baigneurs(L).slice();
        L.B.partie.jour = %d;
        let evapores = 0, nes = 0;
        const vus = new Map();
        for (let i = 0; i < 900; i++) {
          for (const e of avant) vus.set(e, L.B.entites.indexOf(e) >= 0 && L.Entites.visibleAEcran(e.x, e.y, 0));
          o.frame(1);
          for (const e of avant) if (vus.get(e) && L.B.entites.indexOf(e) < 0 && e.vivant) evapores++;
          for (const e of baigneurs(L)) if (avant.indexOf(e) < 0) nes++;
        }
        const restent = baigneurs(L);
        return { greve: true, avant: avant.length, apres: restent.length, evapores: evapores, nes: nes,
                 horsChamp: restent.filter(function (e) { return !L.Entites.visibleAEcran(e.x, e.y, 40); }).length };
    }""" % (GREVE, ETE, HIVER))
    assert r["greve"], "aucune grève sur la carte"
    assert r["avant"] > 0, "personne sur la grève en juillet : le témoin ne dit rien"
    assert r["nes"] == 0, "un baigneur est né en janvier"
    assert r["horsChamp"] == 0, "%s baigneurs restent sur la plage de janvier hors de l'écran" % r["horsChamp"]
    assert r["apres"] < r["avant"], "l'hiver est arrivé et personne n'est rentré"
    assert r["evapores"] == 0, "%s baigneurs ont disparu sous nos yeux" % r["evapores"]


def test_l_homme_au_manteau_prend_conge_l_hiver(banc, paquet):
    """En juillet il ouvre son manteau à la première qui passe (le témoin) ; en janvier il ne
    l'ouvre plus, et hors champ il rentre. Et `naitreLesSortes` ne le fait plus naître."""
    r = banc("""function (L, o) {
        function essai(jour) {
          L.Jeu.commencer();
          L.graine(101);
          L.B.partie.jour = jour;
          const j = L.B.joueur;
          for (const q of L.B.entites.slice()) {
            if (q.type === 'pieton' && Math.hypot(q.x - j.x, q.y - j.y) < 140) L.Entites.retirer(q);
          }
          const a = L.Entites.archetype('exhibitionniste');
          const ex = L.Entites.creerPieton(j.x + 30, j.y, a);
          ex.etat = 'flane';
          const loin = L.Entites.creerPieton(j.x + L.VW, j.y, a);
          loin.etat = 'flane';
          const dame = o.poser('passante', 34, 10);
          dame.etat = 'flane';
          L.Entites.indexer();
          let ouvert = false;
          for (let i = 0; i < 60; i++) { o.frame(1); if (ex.manteauT > 0) ouvert = true; }
          const loinRentre = L.B.entites.indexOf(loin) < 0;
          // La naissance : on retire les deux (une sorte qui marche ne vit qu'a un exemplaire).
          for (const q of L.B.entites.slice()) if (q.arch === 'exhibitionniste') L.Entites.retirer(q);
          let nes = 0;
          for (let k = 0; k < 40 && !nes; k++) {
            L.Entites.naitreLesSortes();
            nes = L.B.entites.filter(function (e) { return e.arch === 'exhibitionniste' && e.vivant; }).length;
          }
          return { ouvert: ouvert, loinRentre: loinRentre,
                   enSaison: L.Entites.enSaison(a.froid_max), nes: nes };
        }
        return { ete: essai(%d), hiver: essai(%d) };
    }""" % (ETE, HIVER))
    assert r["ete"]["enSaison"] and r["ete"]["ouvert"], "en juillet il n'ouvre pas son manteau : %s" % r["ete"]
    assert not r["ete"]["loinRentre"], "en juillet il rentre hors champ : le témoin ne dit rien"
    assert r["ete"]["nes"] > 0, "en juillet il ne naît jamais : le témoin ne dit rien"
    assert not r["hiver"]["enSaison"], "en janvier il est encore en saison"
    assert not r["hiver"]["ouvert"], "en janvier il ouvre encore son manteau"
    assert r["hiver"]["loinRentre"], "en janvier, hors champ, il ne rentre pas"
    assert r["hiver"]["nes"] == 0, "en janvier il naît encore"
