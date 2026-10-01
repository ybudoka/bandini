"""Des bagarres de gangs vivantes — le gang contre toi, au banc (docs/jalons/des-bagarres-de-gangs-vivantes-et-armees.md)."""

#: Trois Cravates, nés à la même image du même côté du joueur, lancés contre lui. Le joueur est increvable (sa vie
#: remise à chaque image) : on juge LEUR façon de se battre, pas sa survie.
TROIS = """
    function trois(L, dx) {
      const j = L.B.joueur, gens = [];
      for (const dy of [-10, 0, 10]) {
        const e = L.Entites.creerPieton(j.x + dx, j.y + dy, L.Entites.archetype('cravate'));
        // ⚠️ Au BATON, sans l'arme de son gang (`armeDeGang` null) : ces juges-ci jugent le contact, et un sur trois
        // aurait degaine son pistolet (vague 2) selon son identifiant.
        e.etat = 'attaque_joueur'; e.courage = 1; e.arme = 'batte'; e.armeDeGang = null;
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
        c.etat = 'bagarre'; c.arme = 'batte'; c.armeDeGang = null; c.rival = m;
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
        c.etat = 'attaque_joueur'; c.armeDeGang = null;
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
        c.etat = 'attaque_joueur'; c.courage = 1; c.arme = 'batte'; c.armeDeGang = null;
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


# --- Vague 2 : le tir -----------------------------------------------------------------------------------------

#: Un Cravate au pistolet, et une Morue à l'EST de lui ; le joueur à l'OUEST. La balle doit partir vers la Morue.
DUEL = """
    function duel(L) {
      const j = L.B.joueur;
      const c = L.Entites.creerPieton(j.x + 60, j.y, L.Entites.archetype('cravate'));
      const m = L.Entites.creerPieton(j.x + 140, j.y, L.Entites.archetype('morue'));
      for (const e of [c, m]) { e.bagarre = true; e.metier = 'bagarre'; e.bagarreT = 99999; }
      c.etat = 'bagarre'; c.rival = m; c.arme = 'pistolet';
      m.etat = 'fige'; m.vie = m.vieMax = 1e9;
      L.Entites.indexer();
      return { c: c, m: m };
    }
    function balleDe(L, e) {
      return L.B.entites.filter(function (p) { return p.type === 'projectile' && p.tireur === e; }).pop();
    }
"""


def test_la_balle_part_vers_sa_cible_et_il_reprend_la_rixe(banc):
    """⚠️ `Combat.tirer` d'un PNJ visait TOUJOURS le joueur, et ne notait pas ce qu'il faisait : au bout de sa
    balle, `majAttaque` le rendait à `attaque_joueur` — un tireur de rixe se retournait contre toi."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        L.graine(30);
        %s
        const d = duel(L);
        L.Combat.tirer(d.c, L.Combat.armeDef('pistolet'), d.m);
        const p = balleDe(L, d.c);
        const vx = p ? p.vx : null;
        for (let i = 0; i < 40; i++) o.frame(1);
        return { vx: vx, etat: d.c.etat };
    }""" % DUEL)
    assert r["vx"] is not None and r["vx"] > 0, "la balle part vers le joueur, pas vers la Morue (%s)" % r
    assert r["etat"] == "bagarre", "après sa balle, il se retourne contre le joueur (%s)" % r


def test_tirer_sur_une_cible_ne_tire_aucun_de(banc):
    """Sa dispersion et son éclair se lisent à l'empreinte : une fusillade de rixe ne déplace pas le hasard de la
    ville. ⚠️ La rue qui réagit (`alerter` : fuir ou témoigner) tire ses dés comme pour une rixe au poing — ce n'est
    pas le tir, on la tient à l'écart de la mesure."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        L.graine(31);
        %s
        const d = duel(L);
        let n = 0;
        const vrai = L.B.rng;
        const alerter = L.Entites.alerter;
        L.Entites.alerter = function () {};
        L.B.rng = function () { n++; return vrai(); };
        L.Combat.tirer(d.c, L.Combat.armeDef('fusil'), d.m);
        L.B.rng = vrai;
        L.Entites.alerter = alerter;
        return { n: n };
    }""" % DUEL)
    assert r["n"] == 0, "tirer sur une cible a tiré %s dés du jeu" % r["n"]


def test_touche_par_un_autre_on_fuit_on_ne_se_jette_pas_sur_toi(banc):
    """Un Cravate qui traîne (hors rixe) prend une balle perdue d'une Morue : il détale. ⚠️ Le courage le lançait
    sur le joueur, qui n'avait rien fait."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        L.graine(32);
        const j = L.B.joueur;
        const c = L.Entites.creerPieton(j.x + 40, j.y, L.Entites.archetype('cravate'));
        const m = L.Entites.creerPieton(j.x + 120, j.y, L.Entites.archetype('morue'));
        c.courage = 1; c.etat = 'flane';
        L.Entites.blesser(c, 5, m, {});
        return { etat: c.etat };
    }""")
    assert r["etat"] == "fuit", r


def test_un_coup_de_feu_d_autrui_ne_deplace_pas_ce_que_la_police_te_prete(banc):
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const j = L.B.joueur, R = L.B.recherche;
        L.Police.creerAgent(j.x + 200, j.y + 20, 'flane');     // un agent a portee d'oreille
        R.etoiles = 1; R.dernierVu = { x: 1, y: 2, t: 0 };
        L.Police.entendre(j.x + 200, j.y, 4000, true);
        const autrui = R.dernierVu;
        L.Police.entendre(j.x + 200, j.y, 4000);
        return { autrui: autrui, toi: R.dernierVu };
    }""")
    assert r["autrui"]["x"] == 1 and r["autrui"]["y"] == 2, r
    assert r["toi"]["x"] != 1, "le coup de feu du joueur doit toujours déplacer la recherche (%s)" % r


def test_la_balle_d_un_gang_te_prend_moins(banc):
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        L.graine(33);
        const j = L.B.joueur;
        for (let i = 0; i < 90; i++) o.frame(1);        // l'invincibilité de naissance s'en va
        const b = L.Entites.creerPieton(j.x + 40, j.y, L.Entites.archetype('boulonneux'));
        b.etat = 'fige'; b.arme = 'mitraillette';
        L.Entites.indexer();
        j.vie = j.vieMax = 100; j.invincible = 0;
        const arme = L.Combat.armeDef('mitraillette');
        L.Combat.tirer(b, arme, j);
        for (let i = 0; i < 30 && j.vie === 100; i++) o.frame(1);
        return { perdu: 100 - j.vie, degats: arme.degats, facteur: L.B.defs.rixes.tir.degats_contre_joueur };
    }""")
    assert r["perdu"] > 0, "la balle ne l'a pas touché (%s)" % r
    assert r["perdu"] <= r["degats"] * r["facteur"] + 0.5, r


# --- Vague 2 : le tireur et le lanceur -----------------------------------------------------------------------

#: Un tireur de `arch` armé de `arme` (marqué armé : `armer` ne le change plus), contre une Morue plantée et
#: increvable à `dist` px à l'est, dans la rue devant le joueur de départ.
FUSILLADE = """
    function fusillade(L, arch, arme, dist) {
      const j = L.B.joueur;
      const x0 = j.x - 60, y0 = j.y + 40;
      const t = L.Entites.creerPieton(x0, y0, L.Entites.archetype(arch));
      const m = L.Entites.creerPieton(x0 + dist, y0, L.Entites.archetype(arch === 'morue' ? 'cravate' : 'morue'));
      for (const e of [t, m]) { e.bagarre = true; e.metier = 'bagarre'; e.bagarreT = 99999; }
      t.etat = 'bagarre'; t.rival = m; t.arme = arme; t.armeDeGang = arme;
      m.etat = 'fige'; m.vie = m.vieMax = 1e9;
      L.Entites.indexer();
      return { t: t, m: m, x0: x0 + dist, y0: y0 };
    }
    function tenirLaCible(d) { d.m.x = d.x0; d.m.y = d.y0; d.m.etat = 'fige'; d.m.vie = 1e9; d.m.vivant = true; }
    function balles(L, e) {
      return L.B.entites.filter(function (p) { return p.type === 'projectile' && p.tireur === e; }).length;
    }
"""


def test_un_sur_trois_degaine_l_arme_de_son_gang(banc):
    """À l'empreinte de son identifiant : toujours le même homme, toujours la même arme. Jamais un Mante, jamais un
    homme de mission (il garde l'arme que sa mission lui donne)."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const j = L.B.joueur, R = L.B.defs.rixes;
        let armes = 0, fideles = 0, mantes = 0, mission = 0;
        for (let k = 0; k < 30; k++) {
          const c = L.Entites.creerPieton(j.x + 30, j.y, L.Entites.archetype('cravate'));
          const avant = c.arme;
          if (L.Rixe.armer(c)) { armes++; if (c.arme === R.arsenal.cravates) fideles++; }
          const deux = c.arme; L.Rixe.armer(c);
          if (c.arme !== deux) fideles = -99;
          const m = L.Entites.creerPieton(j.x + 30, j.y, L.Entites.archetype('mante'));
          if (L.Rixe.armer(m)) mantes++;
          const q = L.Entites.creerPieton(j.x + 30, j.y, L.Entites.archetype('cravate'));
          q.cible = true;
          if (L.Rixe.armer(q)) mission++;
          for (const e of [c, m, q]) L.Entites.retirer(e);
        }
        return { armes: armes, fideles: fideles, mantes: mantes, mission: mission };
    }""")
    assert 5 <= r["armes"] <= 15, "pas un sur trois (%s)" % r
    assert r["fideles"] == r["armes"], "l'arme change, ou ce n'est pas celle du gang (%s)" % r
    assert r["mantes"] == 0 and r["mission"] == 0, r


def test_le_tireur_tient_sa_distance(banc):
    """Né à 30 px de sa cible, le Cravate au pistolet s'en écarte jusqu'à sa fourchette et s'y tient."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        L.graine(34);
        %s
        const d = fusillade(L, 'cravate', 'pistolet', 30);
        const T = L.B.defs.rixes.tir, f = T.distances.pistolet;
        let dans = 0, n = 0, premiere = -1;
        for (let i = 0; i < 900; i++) {
          tenirLaCible(d); o.frame(1);
          if (premiere < 0 && balles(L, d.t) > 0) premiere = i;
          if (i < 180) continue;
          const dist = Math.hypot(d.t.x - d.m.x, d.t.y - d.m.y);
          n++; if (dist >= f[0] - 12 && dist <= f[1] + 12) dans++;
        }
        return { part: dans / n, premiere: premiere, lever: T.lever_images };
    }""" % FUSILLADE)
    assert r["part"] >= 0.7, "il ne tient pas sa distance (%s)" % r


def test_il_leve_l_arme_avant_sa_premiere_balle(banc):
    """Déjà à bonne distance, la cible en vue : il lève l'arme (`lever_images`) avant de tirer — le temps de
    rouler. ⚠️ Né à 30 px, il mettait déjà 29 images à reculer dans sa fourchette : la règle ne se voyait pas."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        L.graine(37);
        %s
        const d = fusillade(L, 'cravate', 'pistolet', 100);
        let premiere = -1;
        for (let i = 0; i < 120 && premiere < 0; i++) { tenirLaCible(d); o.frame(1); if (balles(L, d.t) > 0) premiere = i; }
        return { premiere: premiere, lever: L.B.defs.rixes.tir.lever_images };
    }""" % FUSILLADE)
    assert r["premiere"] >= r["lever"] - 1, "il tire avant d'avoir levé l'arme (%s)" % r


def test_le_tireur_tire_par_salves_et_recharge(banc):
    """Des salves, pas un robinet : et quand son chargeur (celui de l'arme) est vide, un trou d'au moins le temps
    de recharger."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        L.graine(35);
        %s
        const d = fusillade(L, 'cravate', 'pistolet', 100);
        const T = L.B.defs.rixes.tir, chargeur = L.Combat.armeDef('pistolet').chargeur;
        const coups = [];
        const vrai = L.Combat.tirer;
        L.Combat.tirer = function (e) { if (e === d.t) coups.push(i); return vrai.apply(null, arguments); };
        var i = 0;
        for (i = 0; i < 2400; i++) { tenirLaCible(d); o.frame(1); }
        L.Combat.tirer = vrai;
        const trous = coups.slice(1).map(function (t, k) { return t - coups[k]; });
        return { n: coups.length, chargeur: chargeur, trouApres: trous[chargeur - 1] || 0,
                 recharge: T.recharge_images, grands: trous.filter(function (x) { return x >= T.entre_salves_images - 5; }).length };
    }""" % FUSILLADE)
    assert r["n"] > r["chargeur"], "il n'a pas vidé son chargeur (%s)" % r
    assert r["trouApres"] >= r["recharge"], "il ne recharge pas (%s)" % r
    assert r["grands"] >= 2, "il tire en continu, sans salves (%s)" % r


def test_l_abri_trouve_est_cache_de_la_cible(banc):
    """Une tuile marchable d'où la cible ne le voit pas (`Monde.ligneLibre`), dans sa fourchette, près de lui."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const j = L.B.joueur, TT = L.TT, c = L.Monde.carte;
        const t = L.Entites.creerPieton(j.x, j.y, L.Entites.archetype('cravate'));
        t.arme = 'pistolet'; t.armeDeGang = 'pistolet';
        const m = L.Entites.creerPieton(j.x, j.y, L.Entites.archetype('morue'));
        let trouve = null, essais = 0;
        for (let ty = 5; ty < c.h - 5 && !trouve; ty += 3) for (let tx = 5; tx < c.w - 5 && !trouve; tx += 3) {
          if (!L.Monde.marchablePieton(tx, ty) || !L.Monde.marchablePieton(tx + 6, ty)) continue;
          t.x = tx * TT + 8; t.y = ty * TT + 8; m.x = t.x + 6 * TT; m.y = t.y;
          essais++;
          const a = L.Rixe.abriPour(t, m);
          if (a) trouve = { a: a, cache: !L.Monde.ligneLibre(a.x, a.y, m.x, m.y),
                            d: Math.hypot(a.x - m.x, a.y - m.y), loin: Math.hypot(a.x - t.x, a.y - t.y) };
        }
        return { trouve: trouve, essais: essais, f: L.B.defs.rixes.tir.distances.pistolet, tuiles: L.B.defs.rixes.tir.abri_tuiles };
    }""")
    t = r["trouve"]
    assert t, "aucun abri nulle part (%s essais)" % r["essais"]
    assert t["cache"], "l'abri est à découvert (%s)" % r
    assert r["f"][0] <= t["d"] <= r["f"][1] + 16, r
    assert t["loin"] <= (r["tuiles"] + 1) * 16, r


def test_le_molotov_part_de_sa_distance_et_brule_pres_de_la_cible(banc):
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        L.graine(36);
        %s
        const d = fusillade(L, 'skateux', 'molotov', 40);
        const f = L.B.defs.rixes.tir.distances.molotov;
        let depuis = null, brasier = null, apres = null, i;
        for (i = 0; i < 900 && (brasier === null || apres === null); i++) {
          tenirLaCible(d);
          const avant = balles(L, d.t);
          o.frame(1);
          if (depuis === null && balles(L, d.t) > avant) { depuis = Math.hypot(d.t.x - d.m.x, d.t.y - d.m.y); var lance = i; }
          if (brasier === null) {
            const b = L.B.entites.find(function (q) { return q.type === 'brasier'; });
            if (b) brasier = Math.hypot(b.x - d.m.x, b.y - d.m.y);
          }
          if (depuis !== null && apres === null && i === lance + 40) apres = Math.hypot(d.t.x - d.m.x, d.t.y - d.m.y);
        }
        return { depuis: depuis, brasier: brasier, apres: apres, f: f };
    }""" % FUSILLADE)
    assert r["depuis"] is not None, "il n'a rien lancé (%s)" % r
    assert r["f"][0] - 10 <= r["depuis"] <= r["f"][1] + 10, "il lance de trop près ou trop loin (%s)" % r
    assert r["brasier"] is not None and r["brasier"] <= 40, "la bouteille ne brûle pas près de la cible (%s)" % r
    assert r["apres"] > r["depuis"] + 10, "sa bouteille partie, il ne se sauve pas (%s)" % r


# --- Vague 2 : ce que la relecture a trouvé ------------------------------------------------------------------

def test_la_balle_du_tireur_ne_fait_pas_fuir_ses_coequipiers(banc):
    """⚠️ Le coup de feu fait fuir la rue (`alerter`, la menace c'est lui) — et `alerter` n'épargnait que la rixe :
    les deux Cravates qui t'attaquaient avec le tireur détalaient à sa première balle (la relecture, au banc :
    `['attaque/attaque_joueur', 'fuit', 'fuit']`)."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        L.graine(40);
        %s
        const gens = trois(L, 100);
        const t = gens[1], autres = [gens[0], gens[2]];
        t.arme = 'pistolet'; t.armeDeGang = 'pistolet';
        let tir = -1, fuites = 0;
        for (let i = 0; i < 400; i++) {
          tenir(L); o.frame(1);
          if (tir < 0 && L.B.entites.some(function (p) { return p.type === 'projectile' && p.tireur === t; })) tir = i;
          if (tir >= 0) for (const e of autres) if (e.etat === 'fuit' || e.etat === 'temoin') fuites++;
        }
        return { tir: tir, fuites: fuites };
    }""" % TROIS)
    assert r["tir"] >= 0, "le tireur n'a pas tiré : le juge ne mesure rien (%s)" % r
    assert r["fuites"] == 0, "ses coéquipiers ont détalé à sa balle (%s)" % r


def test_colle_a_lui_le_tireur_tire_quand_meme(banc):
    """Tenu à 30 px (sous sa fourchette), il reculait sans jamais tirer : collé contre un mur, il restait planté
    là. À bout portant, il tire."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        L.graine(41);
        %s
        const gens = trois(L, 30), t = gens[1], j = L.B.joueur;
        for (const e of [gens[0], gens[2]]) L.Entites.retirer(e);
        t.arme = 'pistolet'; t.armeDeGang = 'pistolet';
        let balles = 0;
        const vrai = L.Combat.tirer;
        L.Combat.tirer = function (e) { if (e === t) balles++; return vrai.apply(null, arguments); };
        for (let i = 0; i < 600; i++) { tenir(L); t.x = j.x + 30; t.y = j.y; o.frame(1); }
        L.Combat.tirer = vrai;
        return { balles: balles };
    }""" % TROIS)
    assert r["balles"] >= 3, "collé à lui, il ne tire plus (%s)" % r


def test_un_gang_qui_te_tire_dessus_ne_te_vaut_pas_de_meprise(banc):
    """La méprise (M12) : un passant te prend pour le coupable d'une rixe. Mais quand c'est TOI qu'on vise, il n'y
    a pas de méprise possible — tu es la victime. ⚠️ Au banc, une Morue au fusil te valait un crime."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        L.graine(42);
        const j = L.B.joueur, A = L.B.defs.recherche.autrui;
        A.chance = 1; A.repos_s = 0;
        for (let i = 0; i < 90; i++) o.frame(1);
        const m = L.Entites.creerPieton(j.x + 40, j.y, L.Entites.archetype('morue'));
        m.etat = 'fige'; m.arme = 'fusil';
        L.Entites.indexer();
        L.B.crimes.length = 0; L.B.recherche.etoiles = 0;
        for (let k = 0; k < 5; k++) { L.Combat.tirer(m, L.Combat.armeDef('fusil'), j); m.etat = 'fige'; o.frame(2); }
        return { crimes: L.B.crimes.length, etoiles: L.B.recherche.etoiles };
    }""")
    assert r["crimes"] == 0 and r["etoiles"] == 0, r


def test_il_crie_quand_il_leve_l_arme(banc):
    """La levée se VOIT : le tireur crie une réplique (une bulle) au moment où il lève l'arme — le signal pour
    rouler. Et revenu au combat après avoir lâché prise, il la relève."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        L.graine(43);
        %s
        const gens = trois(L, 100), t = gens[1];
        for (const e of [gens[0], gens[2]]) L.Entites.retirer(e);
        t.arme = 'pistolet'; t.armeDeGang = 'pistolet';
        o.frame(2);
        const cri = t.bulle && t.bulle.texte;
        for (let i = 0; i < 200; i++) { tenir(L); o.frame(1); }
        // Il lâche prise (trop loin : `flane`) plus longtemps que `retour_images`, puis revient.
        t.etat = 'flane'; t.x += 400;
        for (let i = 0; i < L.B.defs.rixes.tir.retour_images + 20; i++) { t.etat = 'flane'; o.frame(1); }
        t.x -= 400; t.etat = 'attaque_joueur'; t.bulle = null;
        o.frame(2);
        return { cri: cri, releve: !!(t.bulle && t.bulle.texte), mots: L.B.defs.rixes.tir.lever_mots };
    }""" % TROIS)
    assert r["cri"] and r["cri"] in r["mots"], "il lève l'arme sans un mot (%s)" % r
    assert r["releve"], "revenu au combat, il ne relève pas l'arme (%s)" % r


# --- Vague 3 : le moral et les blessés -----------------------------------------------------------------------

def test_le_blesse_au_contact_fuit_en_boitant(banc):
    """Sous le tiers de sa vie, l'homme au bâton détale en criant — et il BOITE : plus lent qu'un fuyard sain."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        L.graine(50);
        %s
        const gens = trois(L, 40), c = gens[1], sain = gens[2], j = L.B.joueur;
        L.Entites.retirer(gens[0]);
        c.vie = Math.floor(c.vieMax * 0.3);
        let fuite = -1;
        for (let i = 0; i < 90 && fuite < 0; i++) { tenir(L); o.frame(1); if (c.etat === 'fuit') fuite = i; }
        const cri = c.bulle && c.bulle.texte;
        // Un fuyard sain, au meme endroit, pour comparer les pas.
        sain.x = c.x; sain.y = c.y + 12; sain.etat = 'fuit'; sain.menace = j; sain.minuterie = 600; sain.boite = false;
        c.minuterie = 600;
        const a0 = { x: c.x, y: c.y }, b0 = { x: sain.x, y: sain.y };
        for (let i = 0; i < 60; i++) { tenir(L); o.frame(1); }
        const blesse = Math.hypot(c.x - a0.x, c.y - a0.y), valide = Math.hypot(sain.x - b0.x, sain.y - b0.y);
        return { fuite: fuite, boite: !!c.boite, ratio: blesse / Math.max(1, valide), cri: cri,
                 mots: L.B.defs.rixes.moral.blesse_mots, etat: c.etat };
    }""" % TROIS)
    assert r["fuite"] >= 0, "blessé, il se bat encore au contact (%s)" % r
    assert r["boite"] and r["ratio"] < 0.8, "il fuit sans boiter (%s)" % r
    assert r["cri"] in r["mots"], "il fuit sans un mot (%s)" % r


def test_le_tireur_blesse_tire_encore_de_plus_loin(banc):
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        L.graine(51);
        %s
        const d = fusillade(L, 'cravate', 'pistolet', 75);     // au bas de sa fourchette
        d.t.vie = Math.floor(d.t.vieMax * 0.3);
        const f = L.B.defs.rixes.tir.distances.pistolet;
        let tirs = 0, fuit = 0, auPlusPres = 1e9;
        const vrai = L.Combat.tirer;
        L.Combat.tirer = function (e) {
          if (e === d.t) { tirs++; auPlusPres = Math.min(auPlusPres, Math.hypot(d.t.x - d.m.x, d.t.y - d.m.y)); }
          return vrai.apply(null, arguments);
        };
        for (let i = 0; i < 900; i++) {
          tenirLaCible(d); d.t.vie = Math.min(d.t.vie, Math.floor(d.t.vieMax * 0.3)); o.frame(1);
          if (d.t.etat === 'fuit') fuit++;
        }
        L.Combat.tirer = vrai;
        return { tirs: tirs, fuit: fuit, auPlusPres: auPlusPres, milieu: (f[0] + f[1]) / 2 };
    }""" % FUSILLADE)
    assert r["fuit"] == 0 and r["tirs"] >= 3, "blessé, le tireur ne tire plus (%s)" % r
    assert r["auPlusPres"] >= r["milieu"] - 5, "blessé, il tire encore de près (%s)" % r


def test_la_moitie_couchee_les_autres_decrissent(banc):
    """Trois Cravates sur toi : un couché, les deux autres tiennent ; deux couchés, le dernier se sauve en criant."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        L.graine(52);
        %s
        const gens = trois(L, 40), j = L.B.joueur;
        for (let i = 0; i < 90; i++) { tenir(L); o.frame(1); }
        L.Entites.blesser(gens[0], 9999, j, { assomme: true });
        let tiennent = 0;
        for (let i = 0; i < 60; i++) { tenir(L); o.frame(1); if (gens[1].etat !== 'fuit' && gens[2].etat !== 'fuit') tiennent++; }
        L.Entites.blesser(gens[2], 9999, j, { assomme: true });
        let fuite = -1;
        for (let i = 0; i < 60 && fuite < 0; i++) { tenir(L); o.frame(1); if (gens[1].etat === 'fuit') fuite = i; }
        return { tiennent: tiennent, fuite: fuite, cri: gens[1].bulle && gens[1].bulle.texte,
                 mots: L.B.defs.rixes.moral.deroute_mots };
    }""" % TROIS)
    assert r["tiennent"] == 60, "un seul couché, et ils détalent déjà (%s)" % r
    assert r["fuite"] >= 0, "la moitié couchée, le dernier se bat encore (%s)" % r
    assert r["cri"] in r["mots"], r


def test_un_homme_de_mission_ne_lache_jamais(banc):
    """Il est là pour toi (`cible`) : blessé, ou seul debout de son camp, il se bat encore."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        L.graine(53);
        %s
        const gens = trois(L, 40), j = L.B.joueur, c = gens[1];
        for (const e of gens) e.cible = true;
        for (let i = 0; i < 60; i++) { tenir(L); o.frame(1); }
        L.Entites.blesser(gens[0], 9999, j, { assomme: true });
        L.Entites.blesser(gens[2], 9999, j, { assomme: true });
        c.vie = Math.floor(c.vieMax * 0.2);
        let fuit = 0;
        for (let i = 0; i < 120; i++) { tenir(L); o.frame(1); if (c.etat === 'fuit') fuit++; }
        return { fuit: fuit, etat: c.etat };
    }""" % TROIS)
    assert r["fuit"] == 0, r


def test_l_arme_lachee_garde_ce_qui_reste_dans_le_chargeur(banc):
    """⚠️ Couché, il lâchait son arme chargeur PLEIN : la mitraillette du marché noir devenait gratuite (la
    relecture de la vague 2)."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        L.graine(54);
        %s
        const d = fusillade(L, 'boulonneux', 'mitraillette', 90);
        for (let i = 0; i < 80; i++) { tenirLaCible(d); o.frame(1); }
        d.t.rixe.balles = 5; d.t.ballesDeGang = 5;
        L.Entites.blesser(d.t, 9999, d.m, {});
        const r = L.B.entites.find(function (q) { return q.type === 'ramassage' && q.arme === 'mitraillette'; });
        return { munitions: r ? r.munitions : null };
    }""" % FUSILLADE)
    assert r["munitions"] == 5, r


def test_un_vieux_cadavre_ne_met_pas_en_deroute(banc):
    """⚠️ Un mort garde son `e.rixe` et reste dans la grille : compté dans le camp, il mettait en déroute le premier
    Cravate frais venu t'attaquer à côté (la relecture de la vague 3 : il fuyait à l'image 0). Seuls comptent ceux
    du combat EN COURS."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        L.graine(55);
        %s
        const gens = trois(L, 40), j = L.B.joueur;
        for (let i = 0; i < 30; i++) { tenir(L); o.frame(1); }
        L.Entites.blesser(gens[0], 9999, j, {});            // il tombe, dans le combat
        for (let i = 0; i < 60; i++) { tenir(L); o.frame(1); }
        // Le combat d'il y a longtemps : celui-la n'est plus « vu » depuis bien plus que `camp_images`.
        gens[0].rixe.vu = L.B.t - L.B.defs.rixes.moral.camp_images - 60;
        L.Entites.retirer(gens[2]);
        const c = gens[1];
        c.rixe = null; c.etat = 'attaque_joueur';
        let fuit = 0;
        for (let i = 0; i < 60; i++) { tenir(L); o.frame(1); if (c.etat === 'fuit') fuit++; }
        return { fuit: fuit };
    }""" % TROIS)
    assert r["fuit"] == 0, "un vieux cadavre l'a mis en déroute (%s)" % r
