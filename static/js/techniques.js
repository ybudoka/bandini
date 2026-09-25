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

  const api = { FENETRE, COLLE, SORTIE_ROULADE, def, sait, choisir, frapper, demarrer, maj, majCompteurs,
                cibleProche, surActif: null };
  return api;
})();
