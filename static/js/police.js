/* Bandini — police : ce qu'elle voit, ce qu'elle retient, comment elle repond.

   Trois canaux de detection, et rien n'est compte tant que rien n'est detecte :
   le CONE d'un agent (il voit le crime, ou te voit quand tu es recherche), le
   TEMOIN (un passant court le raconter a un agent, ou telephone) et l'ALARME
   (un char qui hurle, dans un rayon). La machine de recherche (chaleur,
   etoiles, decroissance hors de vue) vit ici ; les agents sont des pietons
   (`agent: true`) que ce module dirige quand ils poursuivent ou enquetent,
   et laisse flaner sinon — ils respectent les trottoirs comme tout le monde.

   Les autos de patrouille sont des chars a conducteur `police`, pilotes ici
   avec la physique du joueur : elles peuvent VRAIMENT te rentrer dedans. */

const Police = (function () {
  'use strict';

  const PALETTE_AGENT = { c: '#1f3a6e', p: '#16264a', h: '#101018', s: '#e8b088' };

  function defs() { return B.defs.recherche; }
  function reglages() { return B.defs.recherche.police; }
  function palier() { return defs().paliers[Math.min(B.recherche.etoiles, defs().etoiles_max)]; }

  /** L'agent en (ax, ay) regardant vers `angle` voit-il (x, y) ? Cone + portee ; la ligne de vue est a part. */
  function dansLeCone(ax, ay, angle, demiAngleRad, portee, x, y) {
    const d2 = dist2(ax, ay, x, y);
    if (d2 > portee * portee) return false;
    if (d2 < 1) return true;
    return Math.abs(ecartAngle(angle, angleVers(ax, ay, x, y))) <= demiAngleRad;
  }

  function voit(agent, x, y, genre) {
    const vision = defs().vision[genre || 'policier'];
    const nuit = Monde.estNuit();
    const portee = (nuit ? vision.nuit : vision.jour) * TT;
    if (!dansLeCone(agent.x, agent.y, agent.angle, vision.angle * Math.PI / 180, portee, x, y)) return false;
    return Monde.ligneLibre(agent.x, agent.y, x, y);
  }

  function agents() {
    return B.entites.filter(function (e) { return e.agent && e.vivant && e.etat !== 'assomme'; });
  }

  /** Un temoin voit-il ce qui se passe ici ? (`sauf` = la victime elle-meme.)

      ⚠️ C'est LA regle du jeu : rien n'est compte tant que ce n'est pas vu.
      Un pieton assomme ou mort ne temoigne pas, et un mur suffit a tout
      cacher. Un agent qui voit, lui, compte pour deux : il se lance. */
  function quelqu_un_voit(x, y, sauf) {
    for (const a of agents()) {
      if (voit(a, x, y, 'policier')) { alerterAgent(a, x, y); return true; }
    }
    const rayon = defs().temoins.rayon_tuiles * TT;
    const vision = defs().vision.pieton;
    const portee = (Monde.estNuit() ? vision.nuit : vision.jour) * TT;
    const demi = vision.angle * Math.PI / 180;
    for (const e of Entites.pietonsAutour(x, y, Math.min(rayon, portee))) {
      if (e === sauf || !e.vivant || e.etat === 'assomme' || e.aveugle > 0 || e.agent) continue;
      if (!dansLeCone(e.x, e.y, e.angle, demi, portee, x, y)) continue;
      if (!Monde.ligneLibre(e.x, e.y, x, y)) continue;
      return true;
    }
    return false;
  }

  function ajouterChaleur(gravite) {
    const r = B.recherche, d = defs();
    r.chaleur += gravite * d.chaleur_par_gravite;
    while (r.chaleur >= d.chaleur_etoile && r.etoiles < d.etoiles_max) {
      r.chaleur -= d.chaleur_etoile;
      r.etoiles++;
      r.vu = 0;
      r.flash = 60;
      Son.SFX.etoile();
    }
    if (r.etoiles >= d.etoiles_max) r.chaleur = 0;
  }

  /** Un crime commis. `vu` : quelqu'un (agent ou passant) l'a vu.

      Il COMPTE tout de suite si un agent l'a vu, ou s'il est bruyant (`temoin:
      false` au catalogue : carjacking, coup de feu, explosion — tout le monde
      l'entend). Sinon, les passants qui l'ont vu deviennent des TEMOINS
      porteurs de ce crime : ils courent le raconter a un agent, ou
      telephonent — et d'ici la, on peut leur acheter le silence. */
  function signalerCrime(type, x, y, vu) {
    const delit = defs().delits[type];
    if (!delit) return null;
    const parAgent = agents().some(function (a) { return voit(a, x, y, 'policier'); });
    const compte = parAgent || (!!vu && !delit.temoin);
    const crime = { type: type, gravite: delit.etoiles, temoin: delit.temoin, x: x, y: y, t: B.t, vu: !!vu, rapporte: false };
    B.crimes.push(crime);
    if (B.crimes.length > 40) B.crimes.shift();
    B.partie.stats.crimes++;
    if (compte) { ajouterChaleur(delit.etoiles); crime.rapporte = true; B.recherche.dernierVu = { x: x, y: y, t: B.t }; }
    // Les temoins : ceux qui ont VU (dans leur cone, rien devant) et qui ont le
    // coeur de le dire. La victime d'un pickpocket, de dos, n'a rien vu.
    const t = defs().temoins, vision = defs().vision.pieton;
    const portee = (Monde.estNuit() ? vision.nuit : vision.jour) * TT, demi = vision.angle * Math.PI / 180;
    for (const e of Entites.pietonsAutour(x, y, Math.min(t.rayon_tuiles * TT, portee))) {
      if (!e.vivant || e.agent || e.intouchable || e.metier || e.etat === 'assomme') continue;
      if (!dansLeCone(e.x, e.y, e.angle, demi, portee, x, y) || !Monde.ligneLibre(e.x, e.y, x, y)) continue;
      if (B.rng() < e.probaTemoin) { e.etat = 'temoin'; e.crime = crime; e.menace = B.joueur; e.minuterie = t.oubli_s * 60; e.cri = 120; }
    }
    return crime;
  }

  /** Un temoin arrive a un agent (ou telephone) : le crime est connu. */
  function rapporter(crime, agent) {
    if (!crime || crime.rapporte) return false;
    crime.rapporte = true;
    ajouterChaleur(crime.gravite);
    B.recherche.dernierVu = { x: crime.x, y: crime.y, t: B.t };
    if (agent) { agent.etat = 'enquete'; agent.but = { x: crime.x, y: crime.y }; agent.chemin = null; agent.enqueteT = 180; }
    return true;
  }

  /** On achete le silence d'un temoin : il oublie ce qu'il a vu. */
  function acheterLeSilence(j, temoin) {
    const prix = B.defs.economie.tarifs.silence_temoin;
    if (!temoin || temoin.etat !== 'temoin' || !temoin.crime || temoin.crime.rapporte) return false;
    if (B.partie.argent < prix) { Hud.message(prix + ' $ — PAS ASSEZ'); Son.SFX.erreur(); return true; }
    Missions.payer(prix, 'SILENCE');
    temoin.crime = null; temoin.etat = 'flane'; temoin.cri = 0; temoin.menace = null;
    Hud.message('IL N’A RIEN VU');
    return true;
  }

  function remiseAZero() { const r = B.recherche; r.etoiles = 0; r.chaleur = 0; r.vu = 0; }

  // --- Les agents ------------------------------------------------------------------

  function creerAgent(x, y, etat) {
    const arch = Entites.archetype('policier');
    const a = Entites.creerPieton(x, y, arch);
    a.agent = true; a.metier = 'police'; a.swaps = Object.assign({}, PALETTE_AGENT);
    a.arme = 'pistolet'; a.etat = etat || 'flane'; a.chemin = null; a.cheminT = 0; a.tirT = 0; a.vuT = 9999;
    return a;
  }

  function alerterAgent(a, x, y) {
    if (a.etat === 'poursuit') return;
    a.etat = 'enquete'; a.but = { x: x, y: y }; a.chemin = null; a.enqueteT = 240;
  }

  /** Suit un chemin (liste de centres de tuiles) vers `but`. Rend true si arrive. */
  function suivre(a, but, vitesse) {
    const p = reglages();
    if (a.cheminT-- <= 0 || !a.chemin) {
      a.cheminT = p.chemin_toutes_les_images;
      Monde.demanderChemin(a.x, a.y, but.x, but.y, Monde.MASQUE_PIETON, function (chemin) { a.chemin = chemin; });
    }
    let cible = but;
    if (a.chemin && a.chemin.length) {
      while (a.chemin.length && dist2(a.x, a.y, a.chemin[0].x, a.chemin[0].y) < 36) a.chemin.shift();
      if (a.chemin.length) cible = a.chemin[0];
    }
    const dx = cible.x - a.x, dy = cible.y - a.y, d = Math.hypot(dx, dy);
    if (d < 2) { a.vx = 0; a.vy = 0; return true; }
    a.vx = dx / d * vitesse; a.vy = dy / d * vitesse;
    Entites.deplacerCercle(a, a.vx, a.vy, Monde.MASQUE_PIETON);
    Entites.dansLaCarte(a);
    a.anim.dist += vitesse;
    Entites.regarder(a, dx, dy);
    return false;
  }

  /** Rend true quand la police dirige cet agent (sinon il flane comme un pieton). */
  function gere(a) {
    const j = B.joueur, r = B.recherche, p = reglages(), v = defs().vitesses;
    if (!a.vivant || a.etat === 'assomme' || a.recul > 0) return false;
    if (a.etat === 'attaque') { a.vx = 0; a.vy = 0; return true; }        // il tire : Combat mene la phase
    if (a.etat === 'attaque_joueur') a.etat = 'poursuit';                 // Combat rend la main : on reprend la chasse
    if (a.etat === 'fuit' || a.etat === 'temoin') a.etat = 'poursuit';    // un agent ne fuit pas
    // Regarder : une image sur trois, c'est le budget.
    if ((B.t + a.id) % p.regarde_toutes_les_images === 0) {
      const cible = j.dansVehicule ? j.dansVehicule : j;
      if (voit(a, cible.x, cible.y, 'policier')) {
        a.vuT = 0;
        if (r.etoiles > 0) { r.vu = 0; r.dernierVu = { x: j.x, y: j.y, t: B.t }; if (a.etat !== 'poursuit') { a.etat = 'poursuit'; a.chemin = null; a.cheminT = 0; } }
        else if (j.flagrant > 0 && a.etat !== 'poursuit') { ajouterChaleur(1); a.etat = 'poursuit'; a.chemin = null; a.cheminT = 0; }
      } else a.vuT += p.regarde_toutes_les_images;
    }
    if (a.etat === 'poursuit') {
      if (r.etoiles <= 0) { a.etat = 'flane'; return false; }
      if (a.vuT > p.poursuite_abandon_s * 60) { a.etat = 'enquete'; a.but = r.dernierVu || { x: j.x, y: j.y }; a.enqueteT = 180; a.chemin = null; return true; }
      const but = a.vuT === 0 ? { x: j.x, y: j.y } : (r.dernierVu || { x: j.x, y: j.y });
      const d = Math.hypot(j.x - a.x, j.y - a.y);
      // A trois etoiles, on tire.
      if (palier().tirent && a.vuT === 0 && d < p.tir_portee_tuiles * TT) {
        if (a.tirT-- <= 0) { a.tirT = p.tir_cadence_s * 60; Entites.regarder(a, j.x - a.x, j.y - a.y); Combat.tirer(a, Combat.armeDef('pistolet')); }
      }
      if (!j.dansVehicule && d < p.arrestation_px + 4) {
        a.vx = 0; a.vy = 0;
        if (!j.hospitalise && !j.intouchable && !B.menu) Missions.arrestation(a);
        return true;
      }
      if (j.dansVehicule && d < 40) {
        a.vx = 0; a.vy = 0; Entites.regarder(a, j.x - a.x, j.y - a.y);
        // Un char arrete ne protege de rien : il t'en sort.
        if (d < 30 && Math.abs(j.dansVehicule.vitesse) < 0.5 && !j.intouchable && !B.menu) { Vehicules.descendre(j, true); Hud.message('SORS DU CHAR !'); }
        return true;
      }
      suivre(a, but, v.policier);
      return true;
    }
    if (a.etat === 'enquete') {
      if (!a.but || suivre(a, a.but, v.policier * 0.8)) {
        a.vx = 0; a.vy = 0;
        a.angle += 0.05; Entites.regarder(a, Math.cos(a.angle), Math.sin(a.angle));   // il regarde autour
        if (a.enqueteT-- <= 0) { a.etat = 'flane'; a.but = null; }
      }
      return true;
    }
    return false;   // il flane : un pieton comme un autre
  }

  /** Une place de naissance pour un agent : hors ecran, sur le trottoir. */
  function placeAgent(pres) {
    for (let essai = 0; essai < 20; essai++) {
      const place = Entites.placeDeNaissance();
      if (!place) return null;
      if (!pres || dist2(place.x, place.y, pres.x, pres.y) < 420 * 420) return place;
    }
    return null;
  }

  function peuplerAgents() {
    const j = B.joueur, r = B.recherche, p = reglages();
    if (B.t % 30 !== 0) return;
    const zone = Monde.zoneA(j.x, j.y);
    const voulu = Math.min(p.patrouille_par_zone_max, zone ? zone.police : 1) + palier().agents_pied;
    const presents = agents().length;
    if (presents >= voulu) return;
    const place = placeAgent(r.etoiles > 0 ? (r.dernierVu || j) : null);
    if (!place) return;
    const a = creerAgent(place.x, place.y, r.etoiles > 0 ? 'enquete' : 'flane');
    if (r.etoiles > 0) { a.but = r.dernierVu || { x: j.x, y: j.y }; a.enqueteT = 300; }
  }

  // --- Les autos de patrouille -------------------------------------------------------

  function autos() { return B.entites.filter(function (e) { return e.type === 'vehicule' && e.conducteur === 'police' && e.etat !== 'epave'; }); }

  function peuplerAutos() {
    const j = B.joueur, r = B.recherche;
    if (B.t % 45 !== 0) return;
    const voulu = palier().autos;
    const presentes = autos();
    if (presentes.length >= voulu) return;
    // Naissance sur une voie, hors ecran, dans le sens de la voie.
    const c = Monde.carte;
    for (let essai = 0; essai < 20; essai++) {
      const a = B.rng() * Math.PI * 2, d = 320 + B.rng() * 200;
      const tx = Math.floor((j.x + Math.cos(a) * d) / TT), ty = Math.floor((j.y + Math.sin(a) * d) / TT);
      if (tx < 1 || ty < 1 || tx >= c.w - 1 || ty >= c.h - 1) continue;
      const f = Monde.fleche(tx, ty);
      const pas = { '>': [1, 0], '<': [-1, 0], '^': [0, -1], 'v': [0, 1] }[f];
      if (!pas || Entites.visibleAEcran(tx * TT + 8, ty * TT + 8, 40)) continue;
      const v = Vehicules.creer('police', tx * TT + 8, ty * TT + 8, Math.atan2(pas[1], pas[0]),
                                { conducteur: 'police', etat: 'roule', sirene: true, surRails: true, poursuite: true, sens: f });
      if (v) { v.vitesse = 2; v.vx = pas[0] * 2; v.vy = pas[1] * 2; }
      return;
    }
  }

  /** Les commandes d'une auto de patrouille. Elle suit les RAILS de la ville
      vers toi (feux et stops brules, sortie choisie vers toi a chaque
      croisement) et ne quitte les rails pour te FONCER dessus que quand elle
      te voit de pres. Rend 'rails' (le trafic la conduit) ou des commandes
      (la physique la conduit). Foncer tout droit de loin finissait dans un mur. */
  function commandes(v) {
    const j = B.joueur, r = B.recherche, p = reglages();
    v.poursuite = r.etoiles > 0;
    if (r.etoiles <= 0) { v.surRails = false; return { gaz: 0, frein: 1, direction: 0, freinMain: false }; }
    const cible = j.dansVehicule ? j.dansVehicule : j;
    const d = Math.hypot(cible.x - v.x, cible.y - v.y);
    if (voit(v, cible.x, cible.y, 'auto_police') || d < 60) { r.vu = 0; r.dernierVu = { x: j.x, y: j.y, t: B.t }; }
    if (!j.dansVehicule && (d < p.auto_sortent_px || (v.descendus && d < p.auto_sortent_px * 2.5))) {
      // Tu es a pied : les agents descendent, et l'auto reste la (pas de va-et-vient).
      if (!v.descendus) { v.descendus = true; creerAgent(v.x + 14, v.y, 'poursuit'); creerAgent(v.x - 14, v.y, 'poursuit'); }
      v.surRails = false;
      return { gaz: 0, frein: 1, direction: 0, freinMain: false };
    }
    if (v.descendus && d > p.auto_sortent_px * 2.5) v.descendus = false;   // tu t'es sauve loin : elle repart, pleine
    // De pres et a vue : on quitte les rails et on fonce. Coince (un mur) : on y retourne.
    const direct = d < 140 && Monde.ligneLibre(v.x, v.y, cible.x, cible.y);
    const coince = !v.surRails && (v.immobileT || 0) > 45;
    if (!direct || coince) {
      if (!v.surRails) { v.cible = null; v.sortie = null; v.immobileT = 0; }
      v.surRails = true;
      return 'rails';
    }
    v.surRails = false;
    const voulu = angleVers(v.x, v.y, cible.x, cible.y);
    const ecart = ecartAngle(v.angle, voulu);
    const vitesseMax = v.def.vitesse_max * p.auto_vitesse;
    const gaz = (Math.abs(ecart) > 1.6) ? 0 : (v.vitesse < vitesseMax ? 1 : 0);
    const frein = (Math.abs(ecart) > 1.6 && v.vitesse > 1) ? 1 : 0;
    return { gaz: gaz, frein: frein, direction: borner(ecart * 2, -1, 1), freinMain: Math.abs(ecart) > 1.2 && v.vitesse > 2 };
  }

  // --- Les affiches ----------------------------------------------------------------

  let facades = { carte: null, liste: [] };

  /** Toutes les facades de la ville, une fois : c'est la qu'on colle les affiches. */
  function lesFacades() {
    const c = Monde.carte;
    if (facades.carte === c) return facades.liste;
    const liste = [];
    for (let ty = 1; ty < c.h - 1; ty++) for (let tx = 1; tx < c.w - 1; tx++) {
      if (Monde.glyphe(tx, ty) === 'F' && !Monde.bloque(tx, ty + 1, Monde.MASQUE_PIETON)) liste.push({ x: tx * TT + 8, y: ty * TT + 12 });
    }
    facades = { carte: c, liste: liste };
    return liste;
  }

  function majAffiches() {
    const r = B.recherche, j = B.joueur, p = reglages();
    const affiches = B.entites.filter(function (e) { return e.type === 'affiche'; });
    if (r.etoiles < 2) { affiches.forEach(function (e) { Entites.retirer(e); }); return; }
    if (affiches.length >= p.affiches_max || B.t % 40 !== 0) return;
    const proches = lesFacades().filter(function (f) {
      const d = dist2(f.x, f.y, j.x, j.y);
      return d > 120 * 120 && d < 420 * 420 && !affiches.some(function (e) { return dist2(e.x, e.y, f.x, f.y) < 64 * 64; });
    });
    if (!proches.length) return;
    const f = proches[Math.floor(B.rng() * proches.length)];
    Entites.creer('affiche', f.x, f.y, { decor: 'affiche', r: 0, solide: false, dessine: true, vivant: false });
  }

  // --- La machine de recherche -----------------------------------------------------

  /** Hors de vue, les etoiles tombent une a une. Rien ne les remet a zero d'un coup. */
  function decroitre() {
    const r = B.recherche;
    if (r.etoiles <= 0) return;
    r.vu++;
    const p = defs().paliers[r.etoiles];
    if (r.vu > p.decroissance_s * 60) { r.etoiles--; r.vu = 0; if (r.etoiles === 0) Hud.message('LA POLICE A LACHE'); }
  }

  function maj() {
    const r = B.recherche, j = B.joueur;
    if (!j) return;
    if (r.flash > 0) r.flash--;
    if (B.interieur) { decroitre(); return; }     // dedans, on se fait oublier ; personne ne patrouille les salons
    peuplerAgents();
    decroitre();
    if (r.etoiles > 0) {
      peuplerAutos();
    } else {
      autos().forEach(function (v) { if (!Entites.visibleAEcran(v.x, v.y, 60)) Entites.retirer(v); });
    }
    majAffiches();
    // Les temoins qui courent vers un agent : arrives, ils racontent. Loin de
    // tout agent, ils telephonent au bout du delai.
    const t = defs().temoins;
    for (const e of B.entites) {
      if (e.type !== 'pieton' || e.etat !== 'temoin' || !e.crime || e.crime.rapporte) continue;
      let proche = null, dMin = t.cherche_policier_tuiles * TT;
      for (const a of agents()) { const d = Math.hypot(a.x - e.x, a.y - e.y); if (d < dMin) { dMin = d; proche = a; } }
      if (proche) {
        e.menace = null; e.vers = proche;
        if (dMin < 20) { rapporter(e.crime, proche); e.etat = 'fuit'; e.minuterie = 300; }
      } else if (B.t - e.crime.t > t.delai_depeche_s * 60 && B.rng() < t.proba_telephone / 60) {
        rapporter(e.crime, null);
        e.etat = 'fuit'; e.minuterie = 300;
      }
    }
  }

  return { dansLeCone, voit, quelqu_un_voit, ajouterChaleur, signalerCrime, rapporter, acheterLeSilence, remiseAZero,
           creerAgent, agents, autos, gere, commandes, peuplerAgents, peuplerAutos, maj };
})();
