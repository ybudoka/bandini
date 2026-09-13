/* Bandini — la boucle et la machine d'etats. Seul fichier qui demarre quelque
   chose ; sous le banc d'essai, il attend que `document` existe. */

const Jeu = (function () {
  'use strict';

  const PAS = 1000 / 60;
  let dernier = 0, accu = 0, fenetre = null, doc = null;
  let horsLigne = false;

  // --- Etats -------------------------------------------------------------------------

  function commencer() {
    const p = B.partie;
    Entites.vider();
    B.entites.length = 0;
    Entites.creerDecor(Monde.carte.def);
    Entites.creerAmbulants(Monde.carte.def);
    const app = Monde.carte.apparition.joueur;
    const x = p.x !== null && p.x !== undefined ? p.x : app.x * TT + 8;
    const y = p.y !== null && p.y !== undefined ? p.y : app.y * TT + 8;
    const j = Entites.creerJoueur(x, y);
    Monde.centrerCamera(j.x, j.y);
    B.etat = 'jeu';
    B.recherche.etoiles = 0; B.recherche.chaleur = 0; B.recherche.vu = 0;
    Hud.voile(null);
    Hud.etat('jeu');
    Entree.contexte('pied');
    Hud.message('BAIE-DES-BRUMES', 150);
  }

  function pause() {
    if (B.etat !== 'jeu') return;
    B.etat = 'pause';
    Hud.etat('pause');
    Missions.sauvegarderPartie();
  }

  function reprendre() {
    if (B.etat !== 'pause') return;
    B.etat = 'jeu';
    Hud.etat('jeu');
  }

  function basculerPause() { if (B.etat === 'jeu') pause(); else if (B.etat === 'pause') reprendre(); }

  function retourTitre() {
    Missions.sauvegarderPartie();
    B.etat = 'titre';
    Hud.etat('titre');
    Hud.voile('titre');
  }

  // --- Boucle -------------------------------------------------------------------------

  function maj() {
    Entree.debutImage();
    if (Entree.neuf('muet')) {
      B.options.muet = !B.options.muet;
      Son.majVolume();
      Hud.message(B.options.muet ? 'SON COUPE' : 'SON');
    }
    if (B.etat === 'jeu') {
      if (Entree.neuf('pause')) { pause(); Entree.videPresse(); return; }
      if (Entree.neuf('carte')) { Hud.demanderScore(); B.etat = 'pause'; Hud.etat('pause'); Entree.videPresse(); return; }
      Monde.majHeure();
      Entites.maj();
      Combat.maj();
      Vehicules.maj();
      Police.maj();
      Missions.maj();
      Monde.majCamera();
      Son.Mus.tick();
      B.t++;
    } else if (B.etat === 'pause') {
      if (Entree.neuf('pause') || Entree.neuf('action')) reprendre();
      if (Entree.neuf('annuler')) retourTitre();
    }
    Entree.videPresse();
  }

  function rendre() {
    if (!B.carte) return;
    const ctx = Base.debut();
    ctx.fillStyle = '#0b0a12';
    ctx.fillRect(0, 0, VW, VH);
    const cam = B.cam;
    const sec = B.cam.secousse > 0.05 ? B.cam.secousse : 0;
    const vue = { x: cam.x + (sec ? (Math.random() - 0.5) * sec * 8 : 0), y: cam.y + (sec ? (Math.random() - 0.5) * sec * 8 : 0) };
    Monde.dessinerSol(ctx, vue);
    Entites.dessinerDecals(ctx, vue);     // le sang est SOUS les pieds
    Entites.dessiner(ctx, vue);
    Entites.dessinerParticules(ctx, vue);
    Base.fin(Monde.ambiance(), Monde.lampesVisibles(vue));
    Hud.dessiner();
  }

  function boucle(t) {
    fenetre.requestAnimationFrame(boucle);
    const debut = (typeof performance !== 'undefined' && performance.now) ? performance.now() : t;
    const dt = Math.min(60, t - dernier);
    dernier = t;
    accu += dt;
    let n = 0;
    while (accu >= PAS && n < 4) { maj(); accu -= PAS; n++; }
    if (accu > 200) accu = 0;
    rendre();
    const fin = (typeof performance !== 'undefined' && performance.now) ? performance.now() : t;
    B.stats.ms = B.stats.ms * 0.9 + (fin - debut) * 0.1;
  }

  // --- Demarrage ------------------------------------------------------------------------

  function fabriqueCanvas(w, h) {
    const c = doc.createElement('canvas');
    c.width = w; c.height = h;
    return c;
  }

  function chargerDefinitions(url) {
    return fenetre.fetch(url).then(function (r) {
      if (!r.ok) throw new Error('definitions ' + r.status);
      return r.json();
    });
  }

  function demarrer(w, d) {
    fenetre = w; doc = d;
    const racine = d.getElementById('bandini');
    const toile = d.getElementById('toile');
    Base.initCanvas(toile, fabriqueCanvas);
    Son.init(w, racine.dataset.urlStatique);
    Sauvegarde.init(w.localStorage);
    Entree.init(d, w, w.navigator);
    Hud.init(d, racine);
    B.rng = mulberry(B.graine);

    function redim() { Base.redimensionner(w, Entree.estTactile); }
    w.addEventListener('resize', redim);
    w.addEventListener('orientationchange', function () { setTimeout(redim, 120); });
    if (w.visualViewport) w.visualViewport.addEventListener('resize', redim);
    d.addEventListener('visibilitychange', function () { if (d.hidden) { pause(); Son.suspendre(); } });
    d.addEventListener('pointerdown', function () { Son.reveiller(); }, { passive: true });
    d.addEventListener('keydown', function () { Son.reveiller(); }, { passive: true });
    redim();

    return chargerDefinitions(racine.dataset.urlDefinitions).then(function (defs) {
      B.defs = defs;
      Monde.charger(defs.carte);
      B.partie = Sauvegarde.completer(Sauvegarde.lire(), defs);
      if (B.partie.empreinte && B.partie.empreinte !== defs.empreinte) {
        // Le catalogue a change : on garde la partie, mais une position qui
        // n'existe plus sur la nouvelle carte doit etre oubliee.
        B.partie.x = null; B.partie.y = null;
      }
      const app = defs.carte.apparition.joueur;
      Monde.centrerCamera(app.x * TT, app.y * TT);
      B.etat = 'titre';
      Hud.etat('titre');
      Hud.voile('titre');
      const etat = d.getElementById('etat-chargement');
      if (etat) etat.textContent = 'v' + defs.version + ' · ' + (B.partie.x !== null ? 'partie en cours, jour ' + B.partie.jour : 'nouvelle partie');
      dernier = 0; accu = 0;
      fenetre.requestAnimationFrame(boucle);
      return defs;
    }).catch(function (err) {
      horsLigne = true;
      const etat = d.getElementById('etat-chargement');
      if (etat) etat.textContent = 'Impossible de charger la ville. Recharge la page.';
      throw err;
    });
  }

  return { demarrer, commencer, pause, reprendre, basculerPause, retourTitre, maj, rendre, get horsLigne() { return horsLigne; } };
})();

/* Surface de test et de debogage — la seule poignee du banc d'essai. */
if (typeof window !== 'undefined') {
  window.BANDINI = {
    B: B, VW: VW, VH: VH, TT: TT,
    Base: Base, Atlas: Atlas, Entree: Entree, Son: Son, Monde: Monde, Entites: Entites, Combat: Combat,
    Vehicules: Vehicules, Police: Police, Missions: Missions, Hud: Hud, Jeu: Jeu, Sauvegarde: Sauvegarde,
    SPRITES: SPRITES, TUILES: TUILES, DECORS: DECORS, DECALS: DECALS, OBJETS: OBJETS,
    BULLES: BULLES, POLICE_PIXEL: POLICE_PIXEL,
    etatInitial: etatInitial, mulberry: mulberry, hash2: hash2,
    graine: function (n) { B.graine = n; B.rng = mulberry(n); },
    entree: function (a) { const s = Entree._sacs(); return { bas: Entree.bas(a), pad: !!s.vPad[a], tactile: !!s.vTact[a], axe: Entree.axe }; },
  };
  if (typeof document !== 'undefined' && document.getElementById && document.getElementById('bandini')) {
    if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', function () { Jeu.demarrer(window, document); });
    else Jeu.demarrer(window, document);
  }
}
