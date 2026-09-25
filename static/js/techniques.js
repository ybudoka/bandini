/* Bandini — les techniques d'arts martiaux : la chaine de tapes, les pieds,
   les projections (docs/jalons/les-techniques-d-arts-martiaux.md).

   Python decide (`app/techniques.py` : le catalogue, les lignes de temps), ce
   module JOUE : il choisit la technique d'apres le geste et le contexte, fait
   avancer sa ligne de temps, et applique le coup a l'etape `actif`.

   ⚠️ AUCUN `B.rng()` ICI. Un passant choisit sa variante a l'EMPREINTE (son id,
   son compteur de coups) : un de consomme ici decalerait tout le hasard de la
   ville (voir les juges « ce module ne deplace rien »). */

const Techniques = (function () {
  'use strict';

  //: La fenetre de rythme : une tape dans les 0,4 s apres la fin d'un coup
  //: passe au maillon suivant ; au-dela, on repart du direct du gauche.
  const FENETRE = 24;
  //: Colle a la cible (en px) : le genou prend la place du crochet. ⚠️ Au
  //: CONTACT, pas plus pres : deux corps ne s'approchent jamais sous 10 px
  //: (`Entites.demeler`) — a 9, le genou ne partait jamais.
  const COLLE = 11;
  //: Le maillon que le genou remplace quand on est colle.
  const RANG_DU_GENOU = 3;
  //: Au sortir d'une roulade, combien d'images FRAPPE donne encore le balayage.
  const SORTIE_ROULADE = 12;

  function def(slug) { return (B.defs.techniques || []).find(function (t) { return t.slug === slug; }) || null; }

  /** `e` connait-il `slug` ? La rue, tout le monde ; le reste, ce que la partie a appris. */
  function sait(e, slug) {
    const t = def(slug);
    if (!t) return false;
    if (t.gratuite) return true;
    if (Entites.estJoueur(e)) return !!(B.partie && B.partie.techniques && B.partie.techniques[slug]);
    return !!(e.techniques && e.techniques.indexOf(slug) >= 0);
  }

  function parGeste(geste, rang) {
    return (B.defs.techniques || []).find(function (t) { return t.geste === geste && (!rang || t.rang === rang); }) || null;
  }

  /** La personne la plus proche de `e` dans `rayon`, ou null. */
  function cibleProche(e, rayon) {
    let mieux = null, d2 = rayon * rayon;
    for (const c of Entites.autour(e.x, e.y, rayon, function (q) {
      return q !== e && q.vivant && (q.type === 'pieton' || q.type === 'joueur');
    })) {
      const d = dist2(e.x, e.y, c.x, c.y);
      if (d <= d2) { d2 = d; mieux = c; }
    }
    return mieux;
  }

  /** Pure : le slug que `geste` donne a `e`, ou null s'il ne sait pas le faire.
      Pour une tape : le maillon suivant de la chaine s'il est su et que la
      fenetre de rythme court, sinon le direct du gauche. */
  function choisir(e, geste) {
    if (geste === 'tape') {
      const suivant = e.chaineT > 0 ? (e.chaine || 0) + 1 : 1;
      const t = parGeste('tape', suivant);
      return t && sait(e, t.slug) ? t.slug : parGeste('tape', 1).slug;
    }
    const t = parGeste(geste);
    return t && sait(e, t.slug) ? t.slug : null;
  }

  /** Le geste de FRAPPE, d'apres le contexte : tenu, au sortir d'une roulade,
      en sprint, colle a la cible — sinon une tape. */
  function gesteDeFrappe(e, fort) {
    if (fort) return 'tenue';
    if (e.sortieRoulade > 0) return 'roulade';
    const ent = e.entree || Entree;
    const v = B.defs.recherche.vitesses;
    if (ent.bas('esquive') && Math.hypot(e.vx, e.vy) > v.joueur_course + 0.1) return 'course';
    return 'tape';
  }

  /** Lance une tape de la chaine ; collé a la cible, le crochet devient le genou
      (et la chaine continue derriere lui). */
  function lancerTape(e, slug) {
    const t = def(slug);
    if (t.rang === RANG_DU_GENOU && cibleProche(e, COLLE)) {
      if (!demarrer(e, 'genou', null)) return false;
      e.chaine = RANG_DU_GENOU; e.chaineT = 0;
      return true;
    }
    return demarrer(e, slug, null);
  }

  /** Remplace `Combat.frapper` a mains nues. Rend true si un coup part. */
  function frapper(e, fort) {
    // ⚠️ UNE TAPE PENDANT LE COUP N'EST PAS PERDUE : on la garde (une seule), et
    // elle part a la fin du coup en cours. Sans elle, on ratait une tape sur deux.
    if (e.etat === 'attaque' && e.technique) { e.reserve = true; return false; }
    if (e.etat === 'attaque' || e.roule > 0) return false;
    if (!Entites.estJoueur(e)) {
      // La rue seulement, a l'empreinte : gauche, droit, crochet — le genou colle.
      e.coups = (e.coups || 0) + 1;
      return lancerTape(e, parGeste('tape', ((e.id + e.coups) % 3) + 1).slug);
    }
    const geste = gesteDeFrappe(e, fort);
    const slug = choisir(e, geste);
    if (slug) return geste === 'tape' ? lancerTape(e, slug) : demarrer(e, slug, null);
    // Sans le cours : une tape. TENUE, c'est le coup fort d'avant, sur le maillon.
    if (!lancerTape(e, choisir(e, 'tape'))) return false;
    if (geste === 'tenue') e.fort = true;
    return true;
  }

  /** Ce que `Combat.arcDeMelee` sait lire : une arme de la forme d'`armes.py`. */
  function armeDe(t, e) {
    // Le poing americain garde son ecart d'`armes.py` (12 contre 8) : +4.
    const lest = e && e.arme === 'poing_americain' ? 4 : 0;
    return { slug: e && e.arme === 'poing_americain' ? 'poing_americain' : 'poings', type: 'melee',
             degats: t.degats + lest, portee: t.portee, arc: t.arc, renverse: t.renverse, saigne: 0,
             assomme: t.assomme, usures: 0, son: 'coup', sans_sang: t.sans_sang,
             silencieuse: t.silencieuse, technique: t.slug };
  }

  /** Lance `slug` sur `e` (et sur `cible`, pour une prise). */
  function demarrer(e, slug, cible) {
    const t = def(slug);
    if (!t) return false;
    // ⚠️ ON SE SOUVIENT DE CE QU'ON FAISAIT (voir `Combat.frapper`) : un passant
    // qui se battait avec l'autre gang y retourne apres son coup.
    if (e.etat !== 'attaque') e.avantLeCoup = e.etat;
    e.etat = 'attaque';
    e.technique = slug;
    e.techCible = cible || null;
    e.techEtape = 0;
    e.techT = t.temps[0].images;
    e.techPose = t.temps[0].pose;
    e.touches = [];
    e.fort = false;
    e.reserve = false;
    e.phase = t.temps[0].actif ? 'actif' : 'anticipation';
    e.arc = armeDe(t, e);
    if (t.geste === 'tape') { e.chaine = t.rang; e.chaineT = 0; }
    // Le retournement, l'etranglement : l'etape 0 est deja l'actif.
    if (t.temps[0].actif) entrerDansLActif(e, t);
    return true;
  }

  /** Les gestes qui ne frappent pas en arc : la prise porte sur SA cible. */
  function frappeEnArc(t) {
    return t.geste !== 'contre' && t.geste !== 'dos' && t.geste.indexOf('prise') !== 0;
  }

  /** Une image de la ligne de temps de `e`. */
  function maj(e) {
    const t = def(e.technique);
    if (!t) { finir(e); return; }
    if (t.temps[e.techEtape].actif && frappeEnArc(t)) Combat.arcDeMelee(e, e.arc);
    if (--e.techT > 0) return;
    e.techEtape++;
    if (e.techEtape >= t.temps.length) { finir(e); return; }
    const suivante = t.temps[e.techEtape];
    e.techT = suivante.images;
    e.techPose = suivante.pose;
    const iActif = t.temps.findIndex(function (q) { return q.actif; });
    e.phase = suivante.actif ? 'actif' : (e.techEtape > iActif ? 'repos' : 'anticipation');
    if (suivante.actif) entrerDansLActif(e, t);
  }

  function entrerDansLActif(e, t) {
    const arme = e.arc;
    Son.depuis(e, function () { Son.SFX.arme(arme); });
    // La prise branche ici la projection de `e.techCible`. ⚠️ `api`, pas
    // `Techniques` : appele a l'execution, apres la fin de l'IIFE.
    if (api.surActif) api.surActif(e, t);
  }

  function finir(e) {
    const t = def(e.technique);
    const reserve = e.reserve;
    e.technique = null; e.techPose = null; e.techCible = null; e.phase = null; e.reserve = false;
    const enChaine = t && (t.geste === 'tape' || t.geste === 'genou');
    if (enChaine) e.chaineT = FENETRE;
    if (Entites.estJoueur(e)) {
      e.etat = 'flane';
      if (reserve && enChaine) frapper(e, false);
      return;
    }
    e.etat = e.avantLeCoup || 'attaque_joueur';
    e.avantLeCoup = null;
  }

  /** Les compteurs qui courent hors du coup : la fenetre de la chaine, la sortie de roulade. */
  function majCompteurs(e) {
    if (e.chaineT > 0 && e.etat !== 'attaque') e.chaineT--;
    if (e.sortieRoulade > 0 && !(e.roule > 0)) e.sortieRoulade--;
  }

  // --- La prise : SAISIR, et ce qu'on fait de celui qu'on tient -----------------------

  //: Combien d'images on tient sans rien faire, la portee de la prise, et le
  //: seuil du stick qui choisit la projection.
  const PRISE_MAX = 72, PRISE_PORTEE = 14, STICK = 0.5;
  //: Dans le dos : l'ecart entre le regard de la cible et la direction cible -> joueur.
  const DOS = 2.09;   // 120 degres

  /** La cible prenable devant `j` (le cone de la frappe, a bout portant), ou null. */
  function prenable(j, portee) {
    for (const c of Entites.pietonsAutour(j.x, j.y, portee)) {
      if (!c.vivant || c.dansVehicule || c.vol || c.tenu || c.etat === 'assomme') continue;
      if (Math.abs(ecartAngle(j.angle, angleVers(j.x, j.y, c.x, c.y))) > 0.9) continue;
      if (!Monde.ligneLibre(j.x, j.y, c.x, c.y)) continue;
      return c;
    }
    return null;
  }

  function tenir(j, c, mode) {
    // ⚠️ La prise retient la SCENE ou elle commence : une porte franchie la lache.
    j.prise = { cible: c, t: 0, mode: mode, interieur: B.interieur };
    c.tenu = true; c.avantPrise = c.etat; c.vx = 0; c.vy = 0;
    j.vx = 0; j.vy = 0;
  }

  /** La cible relachee reprend ce qu'elle faisait — ou la colere, ou la fuite. */
  function relacherCible(c) {
    c.tenu = false;
    if (c.vivant && c.etat !== 'assomme' && !c.vol) c.etat = c.courage > 0 ? 'attaque_joueur' : 'fuit';
    c.avantPrise = null;
  }

  /** Lache la prise de `j`, s'il en a une. */
  function lacher(j) {
    const c = j.prise && j.prise.cible;
    j.prise = null;
    if (c) relacherCible(c);
  }

  /** SAISIR et ce qu'on fait dans la prise. Vrai si le geste est pris : `majGestes`
      s'arrete la (ni FRAPPE, ni ACTION pendant qu'on tient quelqu'un). */
  function majPrise(j, ent) {
    if (j.prise) {
      const p = j.prise, c = p.cible;
      p.t++;
      if (!c.vivant || c.dansVehicule || c.etat === 'assomme' || c.vol) { lacher(j); return false; }
      j.vx = 0; j.vy = 0; c.vx = 0; c.vy = 0;
      if (ent.neuf('esquive')) { lacher(j); return true; }
      if (p.mode === 'etrangler') {
        // ⚠️ On TIENT tout le long : relacher avant la fin, il se degage.
        if (!ent.bas('saisir')) { lacher(j); return true; }
        if (p.t >= def('etranglement').tenir) {
          j.prise = null; c.tenu = false;
          Entites.blesser(c, def('etranglement').degats, j, { assomme: true, silencieuse: true, sans_sang: true });
          Police.signalerCrime(c.agent ? 'coup_policier' : 'coup_pieton', c.x, c.y,
                               !!c.agent || Police.quelqu_un_voit(c.x, c.y, c));
        }
        return true;
      }
      if (ent.neuf('attaque') && j.etat !== 'attaque') { demarrer(j, 'genoux_prise', c); return true; }
      const axe = ent.axe;
      if (axe.mag > STICK && j.etat !== 'attaque') {
        const rel = Math.abs(ecartAngle(Math.atan2(axe.y, axe.x), angleVers(j.x, j.y, c.x, c.y)));
        const geste = rel < Math.PI / 4 ? 'prise_avant' : (rel > 3 * Math.PI / 4 ? 'prise_vers_soi' : 'prise_cote');
        const slug = choisir(j, geste);
        if (slug) { j.prise = null; demarrer(j, slug, c); return true; }
      }
      if (!ent.bas('saisir') && j.etat !== 'attaque') { j.prise = null; demarrer(j, 'repousser', c); return true; }
      if (p.t > PRISE_MAX) lacher(j);
      return true;
    }
    if (!ent.neuf('saisir') || j.etat === 'attaque') return false;
    // La parade : il ARME son coup, a portee, et on sait le retournement.
    if (sait(j, 'retournement_poignet')) {
      const a = Entites.pietonsAutour(j.x, j.y, def('retournement_poignet').portee).find(function (c) {
        return c.vivant && c.etat === 'attaque' && c.phase === 'anticipation' && !c.vol && c.technique;
      });
      if (a) {
        // On lui prend le poignet avant que ca parte. `projeter` le relachera.
        a.etat = 'flane'; a.technique = null; a.techPose = null; a.phase = null; a.tenu = true;
        demarrer(j, 'retournement_poignet', a);
        return true;
      }
    }
    const c = prenable(j, PRISE_PORTEE);
    if (!c) return true;                          // SAISIR dans le vide : rien, mais le geste est pris
    const dos = Math.abs(ecartAngle(c.angle, angleVers(c.x, c.y, j.x, j.y))) > DOS;
    tenir(j, c, dos && sait(j, 'etranglement') ? 'etrangler' : 'tenir');
    if (j.prise.mode === 'etrangler') Son.depuis(j, Son.SFX.etranglement);
    return true;
  }

  /** Le point de chute : de `x0,y0` vers `x1,y1`, raccourci a la derniere tuile
      libre et seche. ⚠️ On ne projette personne dans un mur, ni dans la baie. */
  function chute(x0, y0, x1, y1) {
    const pas = Math.max(1, Math.ceil(Math.hypot(x1 - x0, y1 - y0) / 2));
    let bx = x0, by = y0;
    for (let i = 1; i <= pas; i++) {
      const x = x0 + (x1 - x0) * i / pas, y = y0 + (y1 - y0) * i / pas;
      if (Monde.solidite(Math.floor(x / TT), Math.floor(y / TT)) !== 0) break;
      bx = x; by = y;
    }
    return { x: bx, y: by };
  }

  /** Envoie `c` en l'air selon `t` : ou il retombe depend du geste. */
  function projeter(c, auteur, t) {
    const a = angleVers(auteur.x, auteur.y, c.x, c.y);
    const d = Math.hypot(c.x - auteur.x, c.y - auteur.y);
    let cx, cy;
    if (t.geste === 'prise_cote') {
      // Le sacrifice : il vole par-dessus nous et retombe DERRIERE.
      cx = auteur.x - Math.cos(a) * t.projete; cy = auteur.y - Math.sin(a) * t.projete;
    } else if (t.geste === 'prise_avant') {
      // La hanche : il passe par-dessus et retombe devant, plus loin qu'il n'etait.
      cx = auteur.x + Math.cos(a) * (d + t.projete); cy = auteur.y + Math.sin(a) * (d + t.projete);
    } else {
      cx = c.x + Math.cos(a) * t.projete; cy = c.y + Math.sin(a) * t.projete;
    }
    // ⚠️ Le sacrifice passe PAR-DESSUS le lanceur : sa chute se cherche depuis le
    // lanceur (un mur derriere lui l'arrete), pas depuis la victime.
    const depart = t.geste === 'prise_cote' ? auteur : c;
    const fin = chute(depart.x, depart.y, cx, cy);
    c.tenu = false; c.vx = 0; c.vy = 0;
    c.etat = 'flane'; c.technique = null; c.techPose = null; c.phase = null;
    c.vol = { x0: c.x, y0: c.y, x1: fin.x, y1: fin.y, t: 0, duree: 24 + Math.round(t.projete / 3),
              h: 10 + t.projete / 4, tours: t.tours, sens: Math.cos(a) >= 0 ? 1 : -1, auteur: auteur, tech: t.slug };
  }

  /** Une image de chaque vol ; a l'atterrissage, la chute fait mal. */
  function majVols() {
    for (const c of B.entites) {
      if (!c.vol) continue;
      const v = c.vol, k = ++v.t / v.duree;
      c.x = v.x0 + (v.x1 - v.x0) * k; c.y = v.y0 + (v.y1 - v.y0) * k;
      c.z = 4 * v.h * k * (1 - k);
      if (v.t < v.duree) continue;
      c.z = 0; c.vol = null;
      const t = def(v.tech);
      Entites.poussiere(c.x, c.y, 6);
      Son.depuis(c, Son.SFX.chute);
      if (Entites.estJoueur(v.auteur)) {
        B.cam.secousse = 0.8;
        Police.signalerCrime(c.agent ? 'coup_policier' : 'coup_pieton', c.x, c.y,
                             !!c.agent || Police.quelqu_un_voit(c.x, c.y, c));
      }
      Entites.blesser(c, t.degats, v.auteur, { renverse: true, assomme: t.assomme, sans_sang: t.sans_sang,
                                               angle: angleVers(v.x0, v.y0, v.x1, v.y1) });
      // ⚠️ UNE PROJECTION COUCHE : `assomme` ne joue qu'a zero de vie (le coup
      // qui aurait tue assomme), et 12 points n'y menent pas — la victime se
      // relevait en courant. Retombee, elle reste au sol le temps d'un K.-O.
      if (c.vivant && c.etat !== 'assomme' && c.type === 'pieton') Entites.assommer(c);
    }
  }

  /** A l'etape `actif` d'une prise : la projection, ou la poussee. */
  function surActif(e, t) {
    const c = e.techCible;
    if (!c || !c.vivant) return;
    if (t.projete > 0 && !frappeEnArc(t)) { projeter(c, e, t); return; }
    if (t.geste === 'prise') {
      const a = angleVers(e.x, e.y, c.x, c.y);
      relacherCible(c);
      c.vx = Math.cos(a) * 3.2; c.vy = Math.sin(a) * 3.2; c.recul = 22;
      return;
    }
    if (t.geste === 'prise_frappe') {
      // Les genoux dans la prise : la cible reste tenue, le coup porte sur ELLE.
      const tenait = e.prise;
      Entites.blesser(c, e.arc.degats, e, { assomme: true, angle: angleVers(e.x, e.y, c.x, c.y) });
      if (Entites.estJoueur(e)) Police.signalerCrime('coup_pieton', c.x, c.y, Police.quelqu_un_voit(c.x, c.y, c));
      if (tenait && c.vivant && c.etat !== 'assomme') { c.vx = 0; c.vy = 0; }
    }
  }

  const api = { FENETRE, COLLE, SORTIE_ROULADE, PRISE_MAX, def, sait, choisir, frapper, demarrer, maj, majCompteurs,
                cibleProche, majPrise, projeter, majVols, lacher, chute, surActif: surActif };
  return api;
})();
