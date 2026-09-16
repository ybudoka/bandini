"""Le bord de l'eau, 2e vague — les enfants jouent.

⚠️ **Jouer, c'est un `metier`, pas un costume.** La règle des sortes de gens est
écrite trois fois dans `pietons.py`, et le dépôt l'a déjà payée avec les filles
de la Brume : une sorte sans routine est un déguisement.
"""

#: Pose le joueur sur une grève et y fait naître les enfants.
POSER = """
    function greve(L) {
      const c = L.Monde.carte, TT = L.TT;
      function eau(tx, ty, d) {
        return L.Monde.estEau(tx + d, ty) || L.Monde.estEau(tx - d, ty)
            || L.Monde.estEau(tx, ty + d) || L.Monde.estEau(tx, ty - d);
      }
      // ⚠️ UNE VRAIE GREVE, pas le premier grain de sable venu. La carte porte
      // des bouts de rivage de quelques tuiles ; le premier trouve en balayant
      // du nord n'en comptait QUE CINQ dans toute la bulle, dont aucune hors
      // champ — il n'y naissait personne, et le juge accusait le moteur.
      let mieux = null, plus = 0;
      for (let ty = 6; ty < c.h - 6; ty += 2) {
        for (let tx = 6; tx < c.w - 6; tx += 2) {
          if (L.Monde.glyphe(tx, ty) !== 's' || !L.Monde.marchablePieton(tx, ty)) continue;
          if (!eau(tx, ty, 1) && !eau(tx, ty, 2)) continue;
          let n = 0;
          for (let dy = -12; dy <= 12; dy++) for (let dx = -12; dx <= 12; dx++) {
            if (L.Monde.glyphe(tx + dx, ty + dy) === 's') n++;
          }
          if (n > plus) { plus = n; mieux = { tx: tx, ty: ty, x: tx * TT + 8, y: ty * TT + 8, sable: n }; }
        }
      }
      return plus >= 40 ? mieux : null;
    }
    function enfants(L) {
      return L.B.entites.filter(function (e) { return e.metier === 'baigneur' && e.vivant; });
    }
"""


def test_des_enfants_naissent_sur_la_greve_et_jouent(banc, paquet):
    """Une grève vide est exactement ce qu'on avait avant la vague. ⚠️ Et ils
    naissent **hors champ** : personne ne voit apparaître un enfant."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        L.graine(31);
        %s
        const g = greve(L);
        if (!g) return { greve: false };
        L.B.joueur.x = g.x; L.B.joueur.y = g.y - 5 * L.TT;
        L.Monde.centrerCamera(L.B.joueur.x, L.B.joueur.y);
        L.Entites.indexer();
        let vus = 0;
        for (let i = 0; i < 900; i++) {
          o.frame(1);
          for (const e of enfants(L)) if (e.t < 2 && L.Entites.visibleAEcran(e.x, e.y, 0)) vus++;
        }
        const petits = enfants(L);
        const jeux = {};
        for (const e of petits) if (e.jeu) jeux[e.jeu] = (jeux[e.jeu] || 0) + 1;
        return { greve: true, n: petits.length, max: L.B.defs.pietons.plage.enfants,
                 jeux: Object.keys(jeux), vus: vus,
                 intouchables: petits.every(function (e) { return e.intouchable; }) };
    }""" % POSER)
    assert r["greve"], "aucune grève trouvée sur la carte"
    assert r["n"] > 0, "pas un enfant sur la grève"
    assert r["n"] <= r["max"], "plus d'enfants que la fiche n'en veut (%s)" % r["n"]
    assert r["jeux"], "des enfants sur la grève, et aucun ne joue"
    assert r["vus"] == 0, "un enfant est apparu à l'écran"
    # ⚠️ Il reste un enfant : intouchable sur la grève comme ailleurs.
    assert r["intouchables"], "un enfant de la plage a perdu son intouchabilité"


def test_un_enfant_ne_depasse_jamais_la_premiere_tuile_d_eau(banc, paquet):
    """⚠️ **LE JUGE QUI COMPTE.** `intouchable` veut dire aujourd'hui « aucune
    arme, aucun char » ; sur la grève il doit dire aussi « pas l'eau ».

    ⚠️ **Mesuré, pour ne pas s'attribuer un correctif** : aucun piéton ne se noie
    dans le jeu — le souffle et `noyade` n'existent que pour le joueur. Ce juge
    ne répare donc rien : il **épingle** la garantie.

    ⚠️ Et ce qui la tient n'est aucun des deux gardes écrits pour ça : c'est
    qu'on ne donne **jamais** à un enfant de destination au-delà de la première
    tuile, et qu'il s'immobilise dès qu'il y a le pied. Mesuré — neutraliser l'un
    ou l'autre garde ne fait tomber aucun juge ; ce sont des ceintures, et elles
    sont commentées comme telles."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        L.graine(32);
        %s
        const g = greve(L);
        if (!g) return { greve: false };
        L.B.joueur.x = g.x; L.B.joueur.y = g.y - 5 * L.TT;
        L.Monde.centrerCamera(L.B.joueur.x, L.B.joueur.y);
        L.Entites.indexer();
        let auLarge = 0, dansLEau = 0, morts = 0, baigneurs = 0;
        for (let i = 0; i < 1800; i++) {
          o.frame(1);
          for (const e of enfants(L)) {
            const tx = Math.floor(e.x / L.TT), ty = Math.floor(e.y / L.TT);
            if (!L.Monde.estEau(tx, ty)) continue;
            dansLEau++;
            // De l'eau sur les QUATRE cotes : il n'a plus de terre a portee.
            const cerne = L.Monde.estEau(tx + 1, ty) && L.Monde.estEau(tx - 1, ty)
                       && L.Monde.estEau(tx, ty + 1) && L.Monde.estEau(tx, ty - 1);
            if (cerne) auLarge++;
          }
          morts += L.B.entites.filter(function (e) {
            return e.metier === 'baigneur' && !e.vivant; }).length;
        }
        baigneurs = enfants(L).length;
        return { greve: true, auLarge: auLarge, dansLEau: dansLEau, morts: morts, n: baigneurs };
    }""" % POSER)
    assert r["greve"], "aucune grève trouvée"
    assert r["n"] > 0, "plus un enfant à la fin : le juge ne mesure rien"
    # ⚠️ Et il faut qu'ils y soient ENTRÉS : sans cette ligne, le juge passerait
    # tout aussi bien sur une plage où personne ne se mouille jamais les pieds.
    assert r["dansLEau"] > 0, "aucun enfant n'est entré dans l'eau : le juge ne mesure rien"
    assert r["auLarge"] == 0, "un enfant est parti au large (%s images)" % r["auLarge"]
    assert r["morts"] == 0, "un enfant est mort sur la grève"


def test_un_enfant_ne_joue_pas_au_chateau_sans_chateau(banc, paquet):
    """⚠️ Un enfant qui « joue au château » sans château à portée est un enfant
    planté devant rien. On choisit parmi ce qui est **là** — et si le château
    qu'il rebâtissait n'y est plus, il s'en cherche un autre."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        L.graine(33);
        %s
        const g = greve(L);
        if (!g) return { greve: false };
        L.B.joueur.x = g.x; L.B.joueur.y = g.y - 5 * L.TT;
        L.Monde.centrerCamera(L.B.joueur.x, L.B.joueur.y);
        L.Entites.indexer();
        o.frame(600);
        // On rase tous les châteaux de la bulle : plus personne ne peut y jouer.
        for (const d of L.B.entites.filter(function (e) { return e.decor === 'chateau_sable'; })) {
          L.Entites.briser(d);
        }
        L.Entites.indexer();
        o.frame(300);
        const restants = enfants(L).filter(function (e) { return e.jeu === 'chateau'; });
        const debout = L.B.entites.filter(function (e) {
          return e.decor === 'chateau_sable' && !e.brise; }).length;
        return { greve: true, joueursDeChateau: restants.length, debout: debout,
                 n: enfants(L).length };
    }""" % POSER)
    assert r["greve"], "aucune grève trouvée"
    assert r["n"] > 0, "plus un enfant : le juge ne mesure rien"
    assert r["debout"] == 0, "des châteaux ont survécu : le juge ne mesure rien"
    assert r["joueursDeChateau"] == 0, (
        "%s enfants jouent encore au château sans château" % r["joueursDeChateau"])


def test_le_ballon_va_d_un_enfant_a_l_autre_et_ne_reste_pas_seul(banc, paquet):
    """Deux enfants et un ballon qui va de l'un à l'autre. C'est tout, et ça
    suffit — un décor qui **bouge** se voit de trois écrans.

    ⚠️ Et un enfant oublié **emporte son ballon** : sans ça, la balle reste à
    voler toute seule au bord de l'eau, pour toujours."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        L.graine(34);
        %s
        const g = greve(L);
        if (!g) return { greve: false };
        const f = L.B.defs.pietons.plage;
        L.B.joueur.x = g.x; L.B.joueur.y = g.y - 5 * L.TT;
        L.Monde.centrerCamera(L.B.joueur.x, L.B.joueur.y);
        L.Entites.indexer();
        // On force le jeu de ballon sur deux enfants : le juge mesure le GESTE,
        // pas la chance d'un tirage à trois branches.
        let paire = null;
        for (let i = 0; i < 1200 && !paire; i++) {
          o.frame(1);
          const petits = enfants(L);
          for (let a = 0; a < petits.length && !paire; a++) {
            for (let b = a + 1; b < petits.length; b++) {
              const d = Math.hypot(petits[a].x - petits[b].x, petits[a].y - petits[b].y);
              if (d < f.ballon_px && d > f.ballon_min_px) {
                paire = [petits[a], petits[b]]; break;
              }
            }
          }
        }
        if (!paire) return { greve: true, paire: false };
        const [a, b] = paire;
        // ⚠️ On LANCE le ballon nous-mêmes. Le choix du jeu se tire à l'empreinte
        // de l'enfant (jamais au dé du jeu) : attendre qu'il tombe sur « ballon »
        // serait mesurer un tirage, pas le geste que ce juge annonce.
        a.jeu = 'ballon'; a.jeuT = 600;
        L.Entites.lancerLeBallon(a, b, L.B.defs.pietons.plage);
        const ballons = function () {
          return L.B.entites.filter(function (e) { return e.type === 'ballon' && e.actif; });
        };
        const avant = ballons().length;
        const cotes = {};
        let bouge = 0, x0 = ballons()[0] ? ballons()[0].x : 0;
        for (let i = 0; i < 400; i++) {
          o.frame(1);
          const bal = ballons()[0];
          if (!bal) break;
          if (Math.abs(bal.x - x0) > 0.01) bouge++;
          x0 = bal.x;
          cotes[bal.vers === a ? 'a' : 'b'] = true;
        }
        // On oublie les deux enfants : le ballon doit partir avec eux.
        L.B.joueur.x += 4000;
        o.frame(120);
        return { greve: true, paire: true, avant: avant, bouge: bouge,
                 cotes: Object.keys(cotes).length, orphelins: ballons().length };
    }""" % POSER)
    assert r["greve"], "aucune grève trouvée"
    assert r["paire"], "jamais deux enfants assez proches pour se lancer un ballon"
    assert r["avant"] == 1, "le ballon n'est pas apparu (%s)" % r["avant"]
    assert r["bouge"] > 50, "le ballon n'a pas bougé (%s images)" % r["bouge"]
    assert r["cotes"] == 2, "le ballon ne va que dans un sens"
    assert r["orphelins"] == 0, "un ballon vole tout seul après l'oubli des enfants"
