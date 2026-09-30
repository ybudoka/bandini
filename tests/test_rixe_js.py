"""Des bagarres de gangs vivantes — le gang contre toi, au banc (docs/jalons/des-bagarres-de-gangs-vivantes-et-armees.md)."""

#: Trois Cravates, nés à la même image du même côté du joueur, lancés contre lui. Le joueur est increvable (sa vie
#: remise à chaque image) : on juge LEUR façon de se battre, pas sa survie.
TROIS = """
    function trois(L, dx) {
      const j = L.B.joueur, gens = [];
      for (const dy of [-10, 0, 10]) {
        const e = L.Entites.creerPieton(j.x + dx, j.y + dy, L.Entites.archetype('cravate'));
        e.etat = 'attaque_joueur'; e.courage = 1; e.arme = 'batte';
        gens.push(e);
      }
      L.Entites.indexer();
      return gens;
    }
    function tenir(L) { const j = L.B.joueur; j.vie = j.vieMax || 100; j.vivant = true; }
"""



def test_trois_cravates_se_repartissent_autour_du_joueur(banc):
    """Nés du même côté, ils l'encerclent au lieu de faire la file : l'écart d'angle le plus petit entre deux
    d'entre eux, vu du joueur, dépasse 60° EN MOYENNE (le cercle parfait en donne 120 ; le joueur de départ est
    adossé à une façade, et trois hommes sur un demi-cercle en donnent 90).

    ⚠️ En moyenne, pas au pire : un pas de côté (`tourne_rad`) rapproche deux hommes un instant, et c'est voulu.
    L'ancien combat, en file, donnait 0,6°."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        L.graine(21);
        %s
        const gens = trois(L, 60);
        let somme = 0, images = 0;
        for (let i = 0; i < 300; i++) {
          tenir(L); o.frame(1);
          if (i < 180) continue;          // le temps d'arriver
          const j = L.B.joueur;
          const angles = gens.filter(function (e) { return e.vivant; })
            .map(function (e) { return Math.atan2(e.y - j.y, e.x - j.x); }).sort(function (a, b) { return a - b; });
          let pire = Math.PI * 2;
          for (let k = 0; k < angles.length; k++) {
            const suivant = k + 1 < angles.length ? angles[k + 1] : angles[0] + Math.PI * 2;
            pire = Math.min(pire, suivant - angles[k]);
          }
          somme += pire; images++;
        }
        return { ecart: somme / images * 180 / Math.PI, etats: gens.map(function (e) { return e.etat; }) };
    }""" % TROIS)
    assert r["ecart"] > 60, "ils font la file au lieu d'encercler (%s)" % r


def test_celui_qui_s_en_va_rend_sa_place(banc):
    """⚠️ Un homme passé à `flane` garde son vieux `e.rixe` : il ne doit plus compter dans le cercle."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        L.graine(22);
        %s
        const gens = trois(L, 40);
        for (let i = 0; i < 120; i++) { tenir(L); o.frame(1); }
        const f = L.B.defs.rixes.contact;
        const avant = L.Rixe.assaillants(L.B.joueur, f).length;
        gens[0].etat = 'flane';
        return { avant: avant, apres: L.Rixe.assaillants(L.B.joueur, f).length };
    }""" % TROIS)
    assert r["avant"] == 3 and r["apres"] == 2, r


def test_adosse_a_un_mur_il_frappe_quand_meme(banc):
    """La portée prime sur la place : une place dans le mur ne l'empêche pas de cogner."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        L.graine(23);
        %s
        const j = L.B.joueur, TT = L.TT;
        // Un trottoir dont la tuile du dessus est un mur : le joueur s'y adosse.
        let place = null;
        const c = L.Monde.carte;
        for (let ty = 5; ty < c.h - 5 && !place; ty++) for (let tx = 5; tx < c.w - 5 && !place; tx++) {
          if (L.Monde.marchablePieton(tx, ty) && !L.Monde.marchablePieton(tx, ty - 1)
              && L.Monde.marchablePieton(tx - 2, ty) && L.Monde.marchablePieton(tx + 2, ty)) place = { tx: tx, ty: ty };
        }
        j.x = place.tx * TT + 8; j.y = place.ty * TT + 4;
        L.Monde.centrerCamera(j.x, j.y);
        const gens = trois(L, 30);
        let coups = 0;
        const avant = {};
        for (let i = 0; i < 400; i++) {
          tenir(L); o.frame(1);
          for (const e of gens) { if (e.etat === 'attaque' && avant[e.id] !== 'attaque') coups++; avant[e.id] = e.etat; }
        }
        return { coups: coups };
    }""" % TROIS)
    assert r["coups"] >= 3, "adossé au mur, personne ne le frappe (%s)" % r


def test_il_esquive_parfois_ton_coup(banc):
    """Le joueur arme son bâton vingt fois à portée : le Cravate en esquive quelques-uns, jamais tous. ⚠️ Le
    Cravate est increvable lui aussi : cinq coups de bâton le couchent, et un mort n'esquive plus rien (le juge
    ne tenait que par une esquive tombée avant.)"""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        L.graine(24);
        %s
        const j = L.B.joueur;
        L.Combat.ramasserArme('batte', null);
        j.arme = 'batte';
        const e = trois(L, 16)[1];
        let armes = 0;
        for (let i = 0; i < 1400 && armes < 20; i++) {
          tenir(L); e.vie = e.vieMax;
          if (j.etat !== 'attaque' && i %% 60 === 0) {
            L.Entites.regarder(j, e.x - j.x, e.y - j.y);
            if (L.Combat.frapper(j, false)) armes++;
          }
          o.frame(1);
        }
        return { armes: armes, esquives: e.rixe ? e.rixe.esquives : -1 };
    }""" % TROIS)
    assert r["armes"] >= 15, "le joueur n'a pas pu armer (%s)" % r
    assert 1 <= r["esquives"] < r["armes"], r


def test_il_touche_une_cible_qui_bouge(banc):
    """Une cible qui bouge (un Cravate qui tourne autour de toi, qui recule après son coup) se frappe quand
    même À SA CADENCE : l'homme frappe à portée sans attendre sa place — une place sur le cercle d'une cible qui
    bouge bouge avec elle, et il ne l'atteignait presque jamais (11 élans en 20 s, pour une cadence de 40
    images). ⚠️ Au banc du siège de m98, les alliés portaient 47 coups sur des Cravates plantés ; sur des
    Cravates qui bougent, ils tombaient à 18."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        L.graine(25);
        const j = L.B.joueur;
        // Loin du joueur, dans la rue : un Cravate en rixe contre une Morue qui va et vient devant lui.
        const x0 = j.x, y0 = j.y + 40;
        const c = L.Entites.creerPieton(x0 - 20, y0, L.Entites.archetype('cravate'));
        const m = L.Entites.creerPieton(x0, y0, L.Entites.archetype('morue'));
        for (const e of [c, m]) { e.bagarre = true; e.metier = 'bagarre'; e.bagarreT = 99999; }
        c.etat = 'bagarre'; c.arme = 'batte'; c.rival = m;
        m.etat = 'fige'; m.vie = m.vieMax = 1e9;
        L.Entites.indexer();
        let elans = 0, touches = 0, avant = c.etat;
        const vrai = L.Entites.blesser;
        L.Entites.blesser = function (e, d, s) { if (s === c && e === m) touches++; return vrai.apply(null, arguments); };
        for (let i = 0; i < 1200; i++) {
          // Elle va et vient, à un petit pas de course, sur 40 px.
          m.x = x0 + Math.sin(i / 25) * 20; m.y = y0 + Math.cos(i / 40) * 10;
          m.vx = Math.cos(i / 25) * 0.8; m.vy = 0; m.etat = 'fige';
          o.frame(1);
          if (c.etat === 'attaque' && avant !== 'attaque') elans++;
          avant = c.etat;
        }
        L.Entites.blesser = vrai;
        return { elans: elans, touches: touches };
    }""")
    assert r["elans"] >= 16, "il ne s'élance pas sur une cible qui bouge (%s)" % r
    assert r["touches"] / r["elans"] >= 0.6, "il frappe dans le vide (%s)" % r


def test_coince_loin_de_sa_place_il_frappe_d_ou_il_est(banc):
    """À portée de sa cible, sa place de l'autre côté, et des corps qui l'empêchent d'en approcher (on le remet
    au même endroit à chaque image, comme le démêlage) : il frappe d'où il est. ⚠️ Au siège de m98, six alliés
    plantés sur le cercle autour de toi : les Cravates attendaient une place qui ne se libérait jamais et n'ont
    passé que 36 images en plein geste de tout le siège (450 avec cette règle)."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        L.graine(26);
        const j = L.B.joueur;
        const c = L.Entites.creerPieton(j.x + 18, j.y, L.Entites.archetype('cravate'));
        c.etat = 'attaque_joueur';
        let coups = 0;
        const vrai = L.Combat.frapper;
        L.Combat.frapper = function (e) { if (e === c) coups++; return false; };
        for (let i = 0; i < 90; i++) {
          c.x = j.x + 18; c.y = j.y; c.t++;          // son horloge avance, comme a chaque image
          L.Rixe.maj(c, j, 1.5);
          // Sa place, de l'autre côté de la cible, et qui y reste (ni pas de côté, ni rang qui change).
          c.rixe.derive = Math.PI; c.rixe.deriveT = 0; c.rixe.tourneT = 9999;
        }
        L.Combat.frapper = vrai;
        return { coups: coups };
    }""")
    assert r["coups"] >= 1, "coincé à portée, loin de sa place, il ne frappe jamais (%s)" % r


def test_il_frappe_a_sa_cadence(banc):
    """Un Cravate seul contre le joueur planté : entre deux élans, sa cadence (la fiche) plus son recul — pas la
    cadence PLUS le geste. ⚠️ Le délai ne s'écoulait que dans `Rixe.maj`, et le geste (26 images au bâton) rend
    la main sans l'appeler : 70 images entre deux élans au lieu de 40 (l'ancien `e.t % 40`) — le gang frappait
    40 % moins souvent sans que personne l'ait voulu (la relecture du 30 sept. 2026)."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        L.graine(28);
        const j = L.B.joueur, f = L.B.defs.rixes.contact;
        const c = L.Entites.creerPieton(j.x + 16, j.y, L.Entites.archetype('cravate'));
        c.etat = 'attaque_joueur'; c.courage = 1; c.arme = 'batte';
        L.Entites.indexer();
        const departs = [];
        let avant = c.etat;
        for (let i = 0; i < 1200; i++) {
          j.vie = j.vieMax || 100; j.x = j.x; o.frame(1);
          if (c.etat === 'attaque' && avant !== 'attaque') departs.push(i);
          avant = c.etat;
        }
        const ecarts = departs.slice(1).map(function (t, k) { return t - departs[k]; });
        return { n: departs.length, moyenne: ecarts.reduce(function (s, x) { return s + x; }, 0) / Math.max(1, ecarts.length),
                 plafond: f.cadence_images + f.recul_images };
    }""")
    assert r["n"] >= 10, r
    assert r["moyenne"] <= r["plafond"], "il frappe moins souvent que sa cadence (%s)" % r
