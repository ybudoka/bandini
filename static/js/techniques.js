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
    // Pendant une lecon au dojo, la technique enseignee compte comme sue (`dojo.js`) :
    // on ne peut pas faire un geste qu'on n'a pas encore appris, et c'est le moment de l'apprendre.
    if (Entites.estJoueur(e) && B.cours && B.cours.slug === slug) return true;
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
      e.coups = (e.coups || 0) + 1;
      // LES MANTES (`app/mantes.py`) : les pieds et les projections du repertoire, a l'empreinte.
      if (e.techniques && e.techniques.length && frapperEnMante(e)) return true;
      // La rue seulement, a l'empreinte : gauche, droit, crochet — le genou colle.
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

  // --- Les Mantes : un gang qui sait se battre (docs/jalons/l-ecole-rivale.md) -------------

  function mantes() { return B.defs.mantes || null; }

  /** Celui qu'un passant combat en ce moment : son rival dans une rixe, sinon le joueur. */
  function adversaire(e) {
    const rixe = e.etat === 'bagarre' || (e.etat === 'attaque' && e.avantLeCoup === 'bagarre');
    return rixe ? e.rival : B.joueur;
  }

  /** `c` se laisse-t-il saisir et projeter ? Ni en char, ni en l'air, ni en roulade, ni intouchable. */
  function saisissable(c) {
    return !!c && c.vivant && !c.dansVehicule && !c.vol && !(c.roule > 0) && !(c.invincible > 0)
      && !c.intouchable && !c.partenaire && c.etat !== 'assomme' && !(c.auSol > 0) && !c.enjambe && !c.aBord;
  }

  /** Le coup d'un Mante, a l'EMPREINTE de son numero et de son compte de coups — jamais `B.rng()`.
      Colle a l'adversaire, une part de ses coups sont des PRISES (la projection suit) ; une autre part,
      des PIEDS (de plus loin, le pied de cote, qui porte le plus) ; le reste, les poings de rue.
      Rend false s'il n'a rien de mieux que la rue : l'appelant tape. */
  function frapperEnMante(e) {
    const m = mantes();
    if (!m) return false;
    const c = adversaire(e);
    const d = c ? Math.hypot(c.x - e.x, c.y - e.y) : Infinity;
    const k = hash2(e.id, e.coups) % 100;
    if (c && d <= m.saisie_px && k < m.part_projection && saisissable(c)) {
      const slug = k % 2 ? 'projection_hanche' : 'grand_fauchage';
      if (sait(e, slug)) return saisir(e, slug, c);
    }
    if (k >= 100 - m.part_pieds) {
      const slug = d > COLLE + 5 ? 'pied_de_cote' : 'pied_circulaire';
      if (sait(e, slug)) {
        if (c) Entites.regarder(e, c.x - e.x, c.y - e.y);
        return demarrer(e, slug, null);
      }
    }
    return false;
  }

  /** Un Mante saisit `c` pour le projeter : la prise TIENT le temps d'une roulade (`saisie_images`), et le
      joueur saisi ne marche plus (`saisiPar`, lu par `Entites.majJoueur` et `Combat.majGestes`).
      ⚠️ Son etape est l'anticipation : c'est la fenetre de la parade (SAISIR, le retournement du poignet). */
  function saisir(e, slug, c) {
    Entites.regarder(e, c.x - e.x, c.y - e.y);
    if (!demarrer(e, slug, c)) return false;
    e.techT = Math.max(e.techT, mantes().saisie_images);
    if (Entites.estJoueur(c)) {
      if (c.prise) lacher(c);
      c.saisiPar = e; c.vx = 0; c.vy = 0;
    }
    return true;
  }

  /** Le joueur est-il encore dans la prise d'un Mante ? Sinon, on l'oublie. */
  function tenuPar(j) {
    const e = j.saisiPar;
    if (e && e.vivant && e.etat === 'attaque' && e.techCible === j && e.phase === 'anticipation' && !j.dansVehicule) return true;
    j.saisiPar = null;
    return false;
  }

  /** Le joueur se degage (ESQUIVE) : le Mante lache, et chancelle — et il t'en veut toujours : qui te saisit
      se bat avec toi (c'est aussi ce qui laisse la roulade partir, `Combat.roulade` veut une menace). */
  function seDegager(j) {
    const e = j.saisiPar;
    j.saisiPar = null;
    if (!e || e.techCible !== j) return;
    e.technique = null; e.techPose = null; e.techCible = null; e.phase = null;
    e.etat = 'attaque_joueur'; e.avantLeCoup = null;
    e.recul = Math.max(e.recul || 0, 12);
  }

  /** Les boutons du joueur saisi : ESQUIVE le degage (la roulade suit), SAISIR fait la parade s'il connait le
      retournement du poignet (`majPrise` la trouve). Le reste ne fait rien : vrai si le geste s'arrete ici. */
  function majSaisi(j, ent) {
    if (!j.saisiPar || !tenuPar(j)) return false;
    if (ent.neuf('saisir') && sait(j, 'retournement_poignet')) return false;
    if (ent.neuf('esquive')) { seDegager(j); return false; }
    return true;
  }

  /** LA PARADE D'UN MANTE : son adversaire (`a` : le joueur, ou son rival dans une rixe) ARME son coup a
      portee — mains nues ou arme de melee, la batte d'une Cravate comprise —, et le Mante lui retourne le
      poignet — une fois sur trois environ (`parade_chance`), a l'empreinte du Mante et du coup, puis il se
      repose (`parade_repos_images`). Vrai si la parade part. */
  function parer(e, a) {
    const m = mantes(), j = a || B.joueur;
    if (!m || !j || !(e.paradeT <= 0 || e.paradeT === undefined) || !sait(e, 'retournement_poignet')) return false;
    if (j.etat !== 'attaque' || j.phase !== 'anticipation' || !j.arc || j.arc.type !== 'melee' || !saisissable(j)) return false;
    const t = def('retournement_poignet');
    if (dist2(e.x, e.y, j.x, j.y) > t.portee * t.portee) return false;
    // Une decision par coup : le meme elan ne se rejoue pas a chaque image.
    if (e.paradeVue === j.elans) return false;
    e.paradeVue = j.elans;
    if (hash2(e.id * 131 + (j.elans || 0), 0x9A2E) % 1000 >= m.parade_chance * 1000) return false;
    // On lui prend le poignet avant que ca parte : son coup s'arrete (un passant reprend ce qu'il faisait).
    j.etat = Entites.estJoueur(j) ? 'flane' : (j.avantLeCoup || 'flane'); j.avantLeCoup = null;
    j.technique = null; j.techPose = null; j.techCible = null; j.phase = null;
    j.reserve = false; j.fort = false; j.charge = 0;
    if (j.prise) lacher(j);
    Entites.regarder(e, j.x - e.x, j.y - e.y);
    e.paradeT = m.parade_repos_images;
    return demarrer(e, 'retournement_poignet', j);
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
    // Le compte des elans : la parade d'un Mante decide UNE fois par coup (`parer`).
    e.elans = (e.elans || 0) + 1;
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
    if (t.temps[e.techEtape].actif && frappeEnArc(t)) {
      // Le crochet `quandPorte` (la lecon du dojo l'ecoute) : chaque cible NOUVELLEMENT touchee.
      const avant = e.touches.length;
      Combat.arcDeMelee(e, e.arc);
      if (api.quandPorte) {
        for (const id of e.touches.slice(avant)) {
          const c = B.entites.find(function (q) { return q.id === id; });
          if (c) api.quandPorte(e, t.slug, c);
        }
      }
    }
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
    // Un pied fend l'air ; le reste sonne comme ce qu'on a au poing.
    Son.depuis(e, function () { if (t.style === 'karate') Son.SFX.pied(); else Son.SFX.arme(arme); });
    // Une technique APPRISE se nomme quand elle part : on sait ce qu'on vient de
    // faire, et ce qu'on a paye au dojo. Les coups de rue se taisent.
    if (Entites.estJoueur(e) && !t.gratuite) Hud.message(t.nom.toUpperCase() + ' !', 50);
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
    if (e.paradeT > 0) e.paradeT--;
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
      // ⚠️ RIEN N'ATTEINT UN ENFANT (`Entites.blesser`) : ni un enfant, ni un
      // cycliste, ni un personnage de l'histoire, ni un escorte — tout ce qui est
      // `intouchable` ne se saisit pas, et ne se projette donc pas.
      if (!c.vivant || c.dansVehicule || c.vol || c.tenu || c.etat === 'assomme' || c.intouchable || c.invincible > 0) continue;
      if (Math.abs(ecartAngle(j.angle, angleVers(j.x, j.y, c.x, c.y))) > 0.9) continue;
      if (!Monde.ligneLibre(j.x, j.y, c.x, c.y)) continue;
      return c;
    }
    return null;
  }

  function tenir(j, c, mode) {
    // ⚠️ La prise retient la SCENE ou elle commence : une porte franchie la lache.
    j.prise = { cible: c, t: 0, mode: mode, interieur: B.interieur };
    // ⚠️ Saisi en plein elan, son coup S'ARRETE : sinon il partait quand meme,
    // fige dans nos bras, et touchait le joueur qui le tenait.
    if (c.etat === 'attaque') { c.etat = c.avantLeCoup || 'flane'; c.avantLeCoup = null; }
    c.technique = null; c.techPose = null; c.phase = null;
    c.tenu = true; c.avantPrise = c.etat; c.vx = 0; c.vy = 0;
    j.vx = 0; j.vy = 0;
    // On se fait face : la prise se voit (`Entites.nomDePose`, `tech_saisie_*`).
    Entites.regarder(j, c.x - j.x, c.y - j.y);
    if (mode !== 'etrangler') Entites.regarder(c, j.x - c.x, j.y - c.y);
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
          if (!c.partenaire) {
            Police.signalerCrime(c.agent ? 'coup_policier' : 'coup_pieton', c.x, c.y,
                                 !!c.agent || Police.quelqu_un_voit(c.x, c.y, c));
          }
          if (api.quandPorte) api.quandPorte(j, 'etranglement', c);
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
      // Il ARME : un coup de rue comme un couteau ou un baton (`Combat.majAttaque`) —
      // c'est le cas d'ecole du retournement du poignet.
      const a = Entites.pietonsAutour(j.x, j.y, def('retournement_poignet').portee).find(function (c) {
        return c.vivant && c.etat === 'attaque' && c.phase === 'anticipation' && !c.vol && !c.intouchable
          && c.arc && c.arc.type === 'melee';
      });
      if (a) {
        // On lui prend le poignet avant que ca parte. `projeter` le relachera.
        a.etat = a.avantLeCoup || 'flane'; a.avantLeCoup = null;
        a.technique = null; a.techPose = null; a.phase = null; a.tenu = true;
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
    // LE JOUEUR PROJETE (par un Mante) : il lache ce qu'il tenait, et plus personne ne le tient.
    if (Entites.estJoueur(c)) { c.saisiPar = null; if (c.prise) lacher(c); c.charge = 0; }
    c.tenu = false; c.vx = 0; c.vy = 0;
    c.etat = 'flane'; c.technique = null; c.techPose = null; c.phase = null;
    c.vol = { x0: c.x, y0: c.y, x1: fin.x, y1: fin.y, t: 0, duree: 24 + Math.round(t.projete / 3),
              h: 10 + t.projete / 4, tours: t.tours, sens: Math.cos(a) >= 0 ? 1 : -1, auteur: auteur, tech: t.slug };
    // Une projection PORTE quand elle part (la lecon du dojo compte le geste, pas la chute).
    if (api.quandPorte) api.quandPorte(auteur, t.slug, c);
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
      if (Entites.estJoueur(v.auteur) && !c.partenaire) {
        B.cam.secousse = 0.8;
        Police.signalerCrime(c.agent ? 'coup_policier' : 'coup_pieton', c.x, c.y,
                             !!c.agent || Police.quelqu_un_voit(c.x, c.y, c));
      }
      const porte = Entites.blesser(c, t.degats, v.auteur, { renverse: true, assomme: t.assomme, sans_sang: t.sans_sang,
                                                             angle: angleVers(v.x0, v.y0, v.x1, v.y1) });
      // ⚠️ UNE PROJECTION COUCHE : `assomme` ne joue qu'a zero de vie (le coup
      // qui aurait tue assomme), et 12 points n'y menent pas — la victime se
      // relevait en courant. Retombee, elle reste au sol le temps d'un K.-O.
      // Et seulement si la chute a PORTE : `blesser` refuse un intouchable.
      // Kevin, au dojo, se releve de lui-meme (`Entites.blesser`, le partenaire) : jamais assomme.
      if (porte && c.vivant && c.etat !== 'assomme' && c.type === 'pieton' && !c.partenaire) Entites.assommer(c);
      // ⚠️ LE JOUEUR PROJETE SE COUCHE SANS ETRE ASSOMME (`mantes.COMBAT.au_sol_images`) : il reste au sol le
      // temps de reprendre son souffle, intouchable — on ne s'acharne pas sur un homme a terre —, et se releve.
      if (Entites.estJoueur(c) && c.vivant && c.vie > 0 && c.etat !== 'assomme') {
        const m = mantes(), sol = m ? m.au_sol_images : 45;
        c.auSol = sol; c.face = 'couche'; c.vx = 0; c.vy = 0;
        c.invincible = Math.max(c.invincible || 0, sol + 10);
        if (c === B.joueur) B.cam.secousse = 1;
      }
    }
  }

  /** A l'etape `actif` d'une prise : la projection, ou la poussee. */
  function surActif(e, t) {
    const c = e.techCible;
    if (!c || !c.vivant) return;
    if (t.projete > 0 && !frappeEnArc(t)) {
      // ⚠️ La prise d'un PASSANT (un Mante) a tenu vingt images : sa victime a pu rouler, monter en char ou
      // s'eloigner. Le joueur, lui, projette ce qu'il tient.
      if (!Entites.estJoueur(e) && (!saisissable(c) || dist2(e.x, e.y, c.x, c.y) > (t.portee + 8) * (t.portee + 8))) {
        if (c.saisiPar === e) c.saisiPar = null;
        return;
      }
      projeter(c, e, t);
      return;
    }
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
      if (Entites.estJoueur(e) && !c.partenaire) Police.signalerCrime('coup_pieton', c.x, c.y, Police.quelqu_un_voit(c.x, c.y, c));
      if (tenait && c.vivant && c.etat !== 'assomme') { c.vx = 0; c.vy = 0; }
    }
  }

  const api = { FENETRE, COLLE, SORTIE_ROULADE, PRISE_MAX, def, sait, choisir, frapper, demarrer, maj, majCompteurs,
                cibleProche, majPrise, projeter, majVols, lacher, chute, surActif: surActif,
                // Les Mantes : leurs coups, leur prise et leur parade.
                frapperEnMante, saisir, tenuPar, seDegager, majSaisi, parer,
                // Le crochet de la lecon du dojo : (auteur, slug, cible) quand une technique PORTE.
                quandPorte: null };
  return api;
})();
