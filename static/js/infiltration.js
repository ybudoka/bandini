/* Bandini — l'infiltration : des gardes qui font leur ronde, des escaliers d'un etage a l'autre, et ce
   qu'on vient prendre (docs/jalons/infiltration-portes-verrouillees-et-gardes-prives.md).

   Martin (28 sept. 2026) : « fais des missions d'infiltration ». Le premier batiment est la villa du
   maire (`app/blocs/villa.py`), un BLOC : dedans, `B.interieur` reste nul, et tout tourne — les
   objectifs, la police, les etoiles. Ce module ne fait que ce qu'un bloc a etages demande de plus, et il
   le lit dans la fiche du bloc (`B.bloc.def.bloc`), jamais dans un nom :

   - LA RELEVE (`releve`) : en entrant dans un bloc qui a des `gardes`, on pose chacun au debut de sa
     ronde — les memes a chaque visite, remis a neuf. C'est `Police.garder` qui les mene ensuite.
   - LES ESCALIERS (`majEscaliers`) : poser le pied sur une marche fait passer, au noir, a l'arrivee de
     l'autre bout. Les etages sont des CADRES de la meme carte (`Monde.cibleCamera` ne sort pas du sien).
   - CE QU'ON VIENT PRENDRE (`obtenir`, un objectif) : un objet pose a un lieu, qu'on ramasse en marchant
     dessus — ou dans la poche d'un garde (`porte`), qu'on vole par-derriere (`voler`, depuis
     `Combat.pickpocket`) ; assomme, il le laisse tomber.
   - CE QUI SE VOIT : le cone de la lampe de poche de chaque garde, la nuit (sinon on joue a l'aveugle),
     et le « ? » de celui qui a cru voir quelque chose.

   ⚠️ RIEN AU DE. Les gardes naissent a part de la suite des numeros (`Entites.enDehorsDeLaSuite`) : entrer
   a la villa ne decale pas l'id de ce qui naitra ensuite en ville. */

const Infiltration = (function () {
  'use strict';

  const TT = 16;
  //: A cette distance (px) d'un objet a prendre, on le ramasse en passant.
  const RAMASSER_PX = 14;
  //: Le fondu d'un escalier : on ferme, on tient, on ouvre (en images).
  const FONDU_ESCALIER = [16, 6, 14];
  //: Le dessin d'un objet de mission, par terre (`OBJETS` de `sprites.js`) : la cle, le dossier, le
  //: registre. Un objet que la fiche ne nomme pas se peint en sac.
  const DESSINS = { cle: true, dossier: true, registre: true, sac: true };

  //: Le bloc ou l'on etait a l'image d'avant : la releve se fait en ENTRANT.
  let blocVu = null;

  function fiche() { return (B.bloc && B.bloc.def && B.bloc.def.bloc) || null; }
  function dans(c, tx, ty) { return tx >= c[0] && tx < c[0] + c[2] && ty >= c[1] && ty < c[1] + c[3]; }

  /** Ce pixel est-il sur le terrain PRIVE du bloc ou l'on est ? Hors d'un bloc, jamais. */
  function prive(x, y) {
    const f = fiche();
    if (!f || !f.prive) return false;
    const tx = Math.floor(x / TT), ty = Math.floor(y / TT);
    return f.prive.some(function (c) { return dans(c, tx, ty); });
  }

  /** Le cadre de camera (x, y, l, h en tuiles) qui contient ce pixel, ou null. */
  function cadre(x, y) {
    const f = fiche();
    if (!f || !f.cadres || !f.cadres.length) return null;
    const tx = Math.floor(x / TT), ty = Math.floor(y / TT);
    return f.cadres.find(function (c) { return dans(c, tx, ty); }) || null;
  }

  function regles() { const f = fiche(); return (f && f.regles_des_gardes) || null; }

  function gardes() {
    return B.entites.filter(function (e) { return e.type === 'pieton' && e.ronde; });
  }

  // --- La releve ----------------------------------------------------------------------------

  /** Les gardes du bloc, chacun au debut de sa ronde. ⚠️ Ceux d'avant s'en vont d'abord : le bloc se
      souvient de ce qu'on y laisse (`Blocs.garder`), et un garde assomme a la derniere visite se
      releverait a cote de son remplacant. */
  function releve() {
    const f = fiche();
    if (!f || !f.gardes || !f.gardes.length) return;
    for (const e of B.entites.slice()) if (e.type === 'pieton' && e.gardeSlug) Entites.retirer(e);
    Entites.enDehorsDeLaSuite(function () {
      for (const g of f.gardes) {
        const p = g.ronde[0];
        const a = Police.creerAgent(p[0] * TT + 8, p[1] * TT + 8, 'flane', 'garde');
        a.gardeSlug = g.slug; a.ronde = g.ronde; a.rondeI = 0; a.pauseT = 0; a.pauseS = g.pause_s || 2;
        a.soupcon = 0; a.soupconDe = null; a.poche = g.porte || null; a.porteObjet = null; a.argent = 0;
        if (p.length > 2) cap(a, p[2]);
      }
    });
    Entites.indexer();
  }

  /** Tourne un garde vers un cap (degres, 0 = l'est, 90 = le sud). */
  function cap(a, degres) {
    const r = degres * Math.PI / 180;
    Entites.regarder(a, Math.cos(r), Math.sin(r));
  }

  // --- Ce qu'on vient prendre ---------------------------------------------------------------

  function objectifCourant() {
    const m = Histoire.courante(), p = B.partie && B.partie.mission;
    if (!m || !p || !m.objectifs) return null;
    return m.objectifs[p.etape] || null;
  }

  function possede(objet) { return !!(B.partie && B.partie.objets && B.partie.objets[objet] > 0); }

  /** Met l'objet dans le sac, et le dit. */
  function prendre(objet, nom) {
    if (!B.partie.objets) B.partie.objets = {};
    B.partie.objets[objet] = 1;
    Son.SFX.argent();
    Hud.message((nom || objet).toUpperCase(), 150);
  }

  function nomDe(o) { return o && (o.nom || o.texte); }

  /** L'objet a prendre par terre, s'il est dans la carte ou l'on est. */
  function objetPose(objet) {
    return B.entites.find(function (e) { return e.type === 'ramassage' && e.objetDeMission === objet; }) || null;
  }

  function poserObjet(o, x, y) {
    let e = null;
    Entites.enDehorsDeLaSuite(function () {
      e = Entites.creer('ramassage', x, y, { r: 4, objet: DESSINS[o.dessin] ? o.dessin : 'sac', objetDeMission: o.objet,
                                              nomDeMission: nomDe(o), t: 0, solide: false });
    });
    return e;
  }

  /** L'objectif `obtenir` : l'objet attend a son lieu (on le pose quand le lieu est dans la carte ou
      l'on est) ou dans la poche du garde qui le porte ; on le ramasse en marchant dessus. */
  function majObjets() {
    const o = objectifCourant(), j = B.joueur;
    const garde = o && o.type === 'obtenir' && o.garde && !possede(o.objet) ? o.garde : null;
    for (const a of gardes()) {
      a.porteObjet = garde && a.poche === o.objet && a.gardeSlug === garde ? o.objet : null;
      a.nomDeMission = a.porteObjet ? nomDe(o) : null;
      // ⚠️ Des poches a prendre (`Combat.pochesAPrendre` veut de l'argent dedans) : c'est l'objet.
      a.argent = a.porteObjet ? 1 : 0;
      // Assomme, il le laisse tomber : on le ramasse par terre.
      if (a.porteObjet && (!a.vivant || a.etat === 'assomme') && !objetPose(o.objet)) {
        poserObjet(o, a.x + 6, a.y + 4);
        a.poche = null; a.porteObjet = null; a.argent = 0;
      }
    }
    // ⚠️ Un objet PORTE par un garde ne se pose pas a son lieu : `ou` ne dit alors que ou le chercher
    // (le GPS, en ville, vise le passage du bloc).
    if (o && o.type === 'obtenir' && o.ou && !o.garde && !possede(o.objet) && !objetPose(o.objet)) {
      const l = Histoire.lieu(o.ou);
      if (l && !B.interieur) poserObjet(o, l.x, l.y);
    }
    if (!j || j.dansVehicule) return;
    for (const e of B.entites) {
      if (e.type !== 'ramassage' || !e.objetDeMission) continue;
      if (Math.hypot(e.x - j.x, e.y - j.y) > RAMASSER_PX) continue;
      prendre(e.objetDeMission, e.nomDeMission);
      j.animT = 14; j.animType = 'ramasse';
      Entites.retirer(e);
      return;
    }
  }

  /** ACTION dans le dos d'un garde qui porte l'objet (`Combat.pickpocket`) : il ne sent rien. ⚠️ Pas de
      cri, pas de fuite, pas de delit : un vol dans le dos d'un garde qui ne t'a pas vu ne se voit pas —
      s'il t'avait vu, c'est son cone qui l'aurait dit (`Police.garder`). */
  function voler(j, a) {
    if (!a || !a.porteObjet) return false;
    j.animT = 10; j.animType = 'ramasse';
    prendre(a.porteObjet, a.nomDeMission);
    a.poche = null; a.porteObjet = null; a.argent = 0; a.nomDeMission = null;
    return true;
  }

  /** Ce qu'une mission ratee fait retomber : les objets que ses objectifs avaient mis dans le sac (le
      dossier, le code) — on les a laisses en fuyant. Ce qui venait d'AVANT elle (la cle d'une mission
      finie) reste. */
  function rendre(m) {
    if (!m || !m.objectifs || !B.partie || !B.partie.objets) return;
    for (const o of m.objectifs) if (o.objet) delete B.partie.objets[o.objet];
    for (const e of B.entites.slice()) if (e.type === 'ramassage' && e.objetDeMission) Entites.retirer(e);
  }

  // --- Les escaliers ------------------------------------------------------------------------

  /** Le bout d'escalier sous les pieds du joueur, et l'autre bout — ou null. */
  function escalierSous(j) {
    const f = fiche();
    if (!f || !f.escaliers) return null;
    const tx = Math.floor(j.x / TT), ty = Math.floor(j.y / TT);
    const sur = function (bout) { return bout.tuiles.some(function (t) { return t[0] === tx && t[1] === ty; }); };
    for (const e of f.escaliers) {
      if (sur(e.a)) return { de: e.a, vers: e.b };
      if (sur(e.b)) return { de: e.b, vers: e.a };
    }
    return null;
  }

  function majEscaliers() {
    const j = B.joueur;
    if (!j || j.dansVehicule || B.transition || B.piratage) return;
    const e = escalierSous(j);
    if (!e) return;
    Jeu.transiter(FONDU_ESCALIER, function () {
      j.x = e.vers.arrivee[0] * TT + 8; j.y = e.vers.arrivee[1] * TT + 8; j.vx = 0; j.vy = 0;
      Entites.dansLaCarte(j);
      Entites.indexer();
      Monde.centrerCamera(j.x, j.y);
      Son.SFX.porte('maison');
      Hud.message(e.vers.nom, 120);
    });
  }

  // --- Une image ----------------------------------------------------------------------------

  function maj() {
    const f = fiche(), slug = f ? B.bloc.slug : null;
    if (slug !== blocVu) { blocVu = slug; if (f) releve(); }
    if (B.interieur || !B.partie) return;
    majObjets();
    if (f) majEscaliers();
  }

  /** Une partie qui commence (ou qui revient d'un bloc de force) : la releve se refera en entrant. */
  function oublier() { blocVu = null; }

  // --- Ce qui se voit -----------------------------------------------------------------------

  /** Les lampes de poche des gardes, la nuit : un cone jaune pale, par-dessus le noir — c'est ce qui
      dit au joueur ou le garde regarde. Et le « ? » de celui qui a cru voir quelque chose. */
  function dessiner(ctx, vue) {
    if (B.interieur || !fiche()) return;
    const nuit = Monde.ambiance().alpha > 0.25;
    const v = B.defs.recherche.vision.garde;
    for (const a of gardes()) {
      if (!a.vivant || a.etat === 'assomme') continue;
      const x = a.x - vue.x, y = a.y - 6 - vue.y;
      if (x < -120 || x > VW + 120 || y < -120 || y > VH + 120) continue;
      if (nuit) {
        const portee = (Monde.estNuit() ? v.nuit : v.jour) * TT, demi = v.angle * Math.PI / 180;
        const g = ctx.createRadialGradient(x, y, 4, x, y, portee);
        g.addColorStop(0, 'rgba(255,236,160,0.34)');
        g.addColorStop(1, 'rgba(255,236,160,0)');
        ctx.fillStyle = g;
        ctx.beginPath();
        ctx.moveTo(x, y);
        ctx.arc(x, y, portee, a.angle - demi, a.angle + demi);
        ctx.closePath();
        ctx.fill();
        B.stats.rects += 1;
      }
      if (a.soupcon > 0 && a.etat !== 'poursuit') {
        ctx.fillStyle = '#101018'; ctx.fillRect(Math.round(x) - 3, Math.round(y) - 22, 7, 9);
        Atlas.texte(ctx, '?', Math.round(x) - 1, Math.round(y) - 20, '#ffd23a', 1);
      }
    }
  }

  return { maj, releve, oublier, prive, cadre, gardes, escalierSous, voler, rendre, possede, dessiner,
           RAMASSER_PX, FONDU_ESCALIER };
})();
