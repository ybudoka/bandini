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
    Vehicules.creerSignalisation();
    Entites.creerPaquets(Monde.carte.def);
    // Le char laisse devant la planque a la derniere sauvegarde.
    // ⚠️ Sans position (la carte a change sous la partie — M8 a quintuple la
    // ville), il revient sur la rue la plus proche de la porte : une position
    // d'une ancienne carte tombe au hasard, et c'est un char dans un mur.
    const garde = p.planque.vehicule;
    if (garde && Vehicules.vehiculeDef(garde.slug)) {
      const place = garde.x === null || garde.x === undefined
        ? placeDevantLaPlanque() : { x: garde.x, y: garde.y };
      const v = place && Vehicules.creer(garde.slug, place.x, place.y, garde.angle || 0, { etat: 'stationne' });
      if (v) { v.couleur = garde.couleur; v.swaps = { c: garde.couleur }; v.vie = Math.max(1, garde.vie); v.vole = !!garde.vole; }
    }
    // Les chars saisis attendent dans la cour du lot, comme celui de la
    // planque attend devant sa porte.
    Missions.garnirLaFourriere();
    const app = Monde.carte.apparition.joueur;
    const x = p.x !== null && p.x !== undefined ? p.x : app.x * TT + 8;
    const y = p.y !== null && p.y !== undefined ? p.y : app.y * TT + 8;
    const j = Entites.creerJoueur(x, y);
    Monde.centrerCamera(j.x, j.y);
    Entites.peuplerDabord();          // ⚠️ apres le joueur : la bulle est autour de lui
    if (p.mission) p.mission = null;  // une mission ne survit pas au rechargement : ses figurants non plus
    B.mission = null; B.defi = null; B.cinema = null;
    B.transition = null;        // une partie ne commence jamais dans le noir d'une porte
    Histoire.creerDonneurs();
    Histoire.creerPanneaux();
    B.etat = 'jeu';
    B.recherche.etoiles = 0; B.recherche.chaleur = 0; B.recherche.vu = 0;
    Hud.voile(null);
    Hud.etat('jeu');
    Entree.contexte('pied');
    Son.Mus.arreter();          // le theme du menu laisse la place a la ville
    Son.Ambiance.jouer();
    Hud.message('BAIE-DES-BRUMES', 150);
  }

  // --- Les portes : noircir sur l'ancienne, changer au noir, eclaircir sur la nouvelle ---

  /*: La duree d'un fondu de porte, en images (60 = une seconde) : [noircir,
    eclaircir]. ⚠️ ASYMETRIQUE, et c'est voulu : entrer prend son temps — on
    pousse une porte, on veut le sentir — alors que sortir doit etre vif, parce
    qu'on veut retourner au jeu. Les 40 images d'avant, partagees en deux,
    etaient juste assez pour clignoter et pas assez pour lire. */
  const FONDU_ENTREE = [26, 20];
  const FONDU_ETAGE = [20, 16];
  const FONDU_SORTIE = [15, 11];

  /*: Ce qu'on garde d'elan en passant une porte, en fraction de la marche : on
    ne repart pas d'un arret complet. Une course qui s'arrete net au pas de la
    porte se sent teleportee. */
  const ELAN_DE_PORTE = 0.5;

  /** Un changement de scene qui se voit : on noircit sur la scene qu'on QUITTE,
      elle change AU NOIR (`faire`), et on eclaircit sur la nouvelle.

      ⚠️ C'est l'ordre, et lui seul, qui fait un fondu. `entrer()` chargeait la
      piece PUIS demandait le fondu : sa premiere moitie noircissait donc sur la
      scene deja changee et sa seconde l'eclaircissait — on voyait la piece une
      image, l'ecran noircissait, il s'eclaircissait sur la meme piece. Ce n'est
      pas un fondu enchaine, c'est un clignotement, et l'oeil le sait meme quand
      on n'arrive pas a le nommer.

      `duree` vaut `[fermer, ouvrir]` — ou `[fermer, TENIR, ouvrir]` quand le
      fondu doit raconter quelque chose. ⚠️ Une porte, on la passe : rien a
      tenir. Mais l'hopital, la prison et la nuit font PASSER DU TEMPS, et ce
      temps se sent dans le noir. C'est pendant `tenir` — et seulement la,
      quand l'ecran est vraiment plein — que `texte` s'ecrit.

      Le jeu est FIGE pendant (voir `maj()`). */
  function transiter(duree, faire, texte) {
    // ⚠️ Un fondu par-dessus un autre n'en empile pas deux : celui qui joue
    // finit tout de suite (sa scene change AU NOIR, une fois), et le nouveau
    // repart du clair. Se faire arreter en tombant dans la rue passait sinon
    // par deux noirs superposes, chacun avec son horloge.
    finirTransition();
    const tenu = duree.length > 2;
    B.transition = { t: 0, ferme: duree[0], tient: tenu ? duree[1] : 0, ouvre: duree[tenu ? 2 : 1],
                     faire: faire, texte: texte || null, fait: false, vu: false };
  }

  /** Le changement de scene lui-meme, au noir — une fois, jamais deux. */
  function auNoir() {
    const tr = B.transition;
    if (!tr || tr.fait) return;
    tr.fait = true;
    tr.faire();
  }

  /** Avance le fondu d'une image.

      ⚠️ Le noir s'arrete PILE a `ferme` (alpha 1) avant de changer la scene, et
      il ne s'eclaircit pas avant d'avoir ete dessine une fois (`vu`, pose par le
      HUD) : la boucle rattrape jusqu'a quatre images de simulation entre deux
      images dessinees, et sans ces deux precautions la premiere image de la
      nouvelle scene pourrait se montrer a 94 % de noir — donc se montrer. */
  function majTransition() {
    const tr = B.transition;
    if (!tr) return;
    if (!tr.fait) {
      tr.t++;
      if (tr.t >= tr.ferme) { tr.t = tr.ferme; auNoir(); }
      return;
    }
    if (!tr.vu) return;
    tr.t++;
    if (tr.t >= tr.ferme + tr.tient + tr.ouvre) B.transition = null;
  }

  /** Finit tout de suite le fondu en cours.

      ⚠️ Passer une porte pendant qu'un autre fondu joue est LE cas qui casse
      tout : sans ca, `sortir()` appele pendant le noircissement d'une entree ne
      trouve aucun interieur, refuse — et le joueur se reveille dedans sans avoir
      rien demande. */
  function finirTransition() {
    if (!B.transition) return;
    auNoir();
    B.transition = null;
  }

  /** Poser le joueur au pas d'une porte : la face et un reste d'elan dans le
      sens ou l'on passe, et la camera deja a sa place.

      ⚠️ La camera se pose AU NOIR, sur la cible exacte que `majCamera` viserait
      a la premiere image (position + avance de l'elan) : personne ne voit le
      saut, et l'amorti n'a rien a rattraper quand le jeu repart. */
  function poserDansLaPorte(j, sens) {
    const pas = B.defs.recherche.vitesses.joueur_marche * ELAN_DE_PORTE;
    j.vx = 0; j.vy = sens === 'haut' ? -pas : pas;
    j.face = sens;
    Entites.dansLaCarte(j);
    Monde.centrerCamera(j.x + j.vx * 14, j.y + j.vy * 14);
  }

  /** Passer une porte : on noircit sur la rue, la piece se charge AU NOIR, on
      eclaircit dedans. */
  function entrer(porte) {
    const j = B.joueur;
    finirTransition();
    if (!porte || !porte.interieur || B.interieur || j.dansVehicule) return false;
    // ⚠️ La piece se cherche AVANT de noircir : un fondu qui ne mene nulle part
    // est plus laid qu'une porte qui ne s'ouvre pas.
    const interieurs = (Monde.carte.def && Monde.carte.def.interieurs) || {};
    if (!interieurs[porte.interieur]) return false;
    transiter(FONDU_ENTREE, function () {
      const piece = Monde.entrer(porte);
      if (!piece) return;
      B.exterieur = { carte: piece.ville, entites: B.entites, x: porte.x * TT + 8, y: (porte.y + 1) * TT + 10 };
      B.entites = [j];
      B.particules.length = 0;
      B.interieur = piece.interieur;
      Entites.reindexerDecor();
      Entites.peuplerInterieur(piece.interieur);
      Histoire.creerDonneursDedans(piece.interieur);
      j.x = piece.interieur.apparition.x * TT + 8;
      j.y = piece.interieur.apparition.y * TT + 8;
      poserDansLaPorte(j, 'haut');
      Son.SFX.porte(piece.interieur.porte);   // la porte s'entend AU NOIR : c'est la qu'on la passe
      Hud.message(piece.interieur.nom.toUpperCase(), 120);
    });
    return true;
  }

  /** Monter l'escalier : meme adresse, autre plancher.

      ⚠️ On ne repasse PAS par la rue : `B.exterieur` reste ce qu'il etait, et
      c'est toujours par la porte d'en bas qu'on ressortira. On arrive sur
      l'escalier qui redescend — pas au milieu de la piece : c'est ce qui dit
      au joueur par ou il est monte. */
  function changerEtage(slug) {
    const j = B.joueur;
    finirTransition();
    if (!B.interieur || !B.exterieur || j.dansVehicule) return false;
    const depuis = B.interieur.slug;
    // Comme pour une porte : l'etage se cherche avant de noircir.
    const etages = (B.exterieur.carte.def && B.exterieur.carte.def.interieurs) || {};
    if (!etages[slug]) return false;
    transiter(FONDU_ETAGE, function () {
      const piece = Monde.changerPiece(slug);
      if (!piece) return;
      B.entites = [j];
      B.particules.length = 0;
      B.interieur = piece.interieur;
      Entites.reindexerDecor();
      Entites.peuplerInterieur(piece.interieur);
      Histoire.creerDonneursDedans(piece.interieur);
      const retour = (piece.interieur.points || []).find(function (p) {
        return p.type === 'escalier' && p.vers === depuis;
      }) || piece.interieur.apparition;
      j.x = retour.x * TT + 8; j.y = retour.y * TT + 8;
      poserDansLaPorte(j, 'bas');
      Son.SFX.porte(piece.interieur.porte);
      Hud.message(piece.interieur.nom.toUpperCase(), 120);
    });
    return true;
  }

  function sortir() {
    const j = B.joueur;
    finirTransition();
    const ext = B.exterieur;
    if (!B.interieur || !ext) return false;
    transiter(FONDU_SORTIE, function () {
      const genre = B.interieur ? B.interieur.porte : undefined;   // la porte qu'on a poussee en entrant
      Monde.restaurer(ext.carte);
      B.entites = ext.entites;
      if (B.entites.indexOf(j) < 0) B.entites.push(j);
      B.particules.length = 0;
      B.interieur = null;
      B.exterieur = null;
      Entites.reindexerDecor();
      // ⚠️ La tuile devant la porte, au pixel : entrer puis sortir doit ramener
      // exactement la ou l'on etait, meme en sortant pendant le fondu d'entree.
      j.x = ext.x; j.y = ext.y;
      poserDansLaPorte(j, 'bas');
      Son.SFX.porte(genre);
    });
    return true;
  }

  function pause() {
    if (B.etat !== 'jeu') return;
    B.etat = 'pause';
    Hud.etat('pause');
    Missions.sauvegarderPartie();
    Hud.ouvrirMenu(Hud.menuPause());
  }

  function reprendre() {
    if (B.etat !== 'pause') return;
    B.etat = 'jeu';
    Hud.etat('jeu');
    if (B.menu) Hud.fermerMenu();
  }

  function basculerPause() { if (B.etat === 'jeu') pause(); else if (B.etat === 'pause') reprendre(); else if (B.etat === 'carte') fermerCarte(); }

  /** La carte de la ville, plein ecran : la simulation attend. */
  function ouvrirCarte() {
    if (B.etat !== 'jeu' && B.etat !== 'pause') return;
    if (B.menu) Hud.fermerMenu();
    B.etat = 'carte';
    Hud.etat('carte');
  }

  function fermerCarte() {
    if (B.etat !== 'carte') return;
    B.etat = 'jeu';
    Hud.etat('jeu');
  }

  function retourTitre() {
    Missions.sauvegarderPartie();
    B.etat = 'titre';
    Hud.etat('titre');
    Hud.voile('titre');
    Son.Ambiance.arreter();
    Son.Mus.jouer('titre');
  }

  // --- Boucle -------------------------------------------------------------------------

  /** La tuile de rue la plus proche de la porte de la planque. */
  function placeDevantLaPlanque() {
    const porte = (Monde.carte.def.portes || []).find(function (q) { return q.lieu === 'planque'; });
    if (!porte) return null;
    for (let r = 1; r <= 8; r++) {
      for (let dy = -r; dy <= r; dy++) {
        for (let dx = -r; dx <= r; dx++) {
          const tx = porte.x + dx, ty = porte.y + dy;
          if (Monde.estRoute(tx, ty) && !Monde.estPassage(tx, ty)) return { x: tx * TT + 8, y: ty * TT + 8 };
        }
      }
    }
    return null;
  }

  function maj() {
    Entree.debutImage();
    // ⚠️ A chaque image, quel que soit l'ecran : la musique du menu doit
    // tourner au titre, la ou la simulation, elle, ne tourne pas.
    Son.Mus.tick();
    if (Entree.neuf('muet')) {
      B.options.muet = !B.options.muet;
      Son.majVolume();
      Hud.message(B.options.muet ? 'SON COUPE' : 'SON');
    }
    // ⚠️ « Jouer » n'etait qu'un bouton de la page : a la manette (ou au
    // clavier), on ne pouvait pas commencer la partie sans toucher l'ecran.
    if (B.etat === 'titre' && Hud.voileCourant === 'titre'
        && (Entree.neuf('action') || Entree.neuf('pause'))) {
      Son.reveiller();
      const sansSon = Son.enAttente();
      commencer();
      // ⚠️ Apres `commencer()`, qui pose son propre message : sinon le nôtre
      // est efface par « BAIE-DES-BRUMES » et le silence reste muet.
      // Commencer a la manette ne donne AUCUN geste au navigateur : il refuse
      // alors le son sans rien dire. On le dit a sa place.
      if (sansSon) Hud.message('SON EN ATTENTE — TOUCHE L\'ECRAN', 300);
      Entree.videPresse();
      return;
    }
    if (B.etat === 'jeu' && B.transition) {
      // ⚠️ Le jeu est FIGE pendant un fondu de porte. Avant, la simulation
      // continuait : on pouvait sortir d'une piece et se faire renverser par un
      // char qu'on n'a pas vu venir, sur un ecran noir ou l'on ne controle rien.
      // Un menu fige deja tout (`if (B.menu) return`) ; une porte fait pareil.
      majTransition();
      Entree.videPresse();
      return;
    }
    if (B.etat === 'jeu' && B.menu) {
      // Un menu ouvert fige la simulation : le temps ne passe pas au comptoir.
      Hud.majMenu();
      Entree.videPresse();
      return;
    }
    if (B.etat === 'jeu') {
      if (Entree.neuf('pause')) { pause(); Entree.videPresse(); return; }
      if (Entree.neuf('carte')) { ouvrirCarte(); Entree.videPresse(); return; }
      Monde.majHeure();
      Monde.majBattants();
      Monde.majChemins();
      Entites.maj();
      Combat.maj();
      Vehicules.maj();
      Police.maj();
      Missions.maj();
      Histoire.maj();
      Monde.majCamera();
      B.t++;
    } else if (B.etat === 'carte') {
      // La carte de la ville : N, ECHAP, ACTION ou FRAPPE la referment.
      if (Entree.neuf('carte') || Entree.neuf('pause') || Entree.neuf('action') || Entree.neuf('attaque') || Entree.neuf('annuler')) { fermerCarte(); Entree.videPresse(); return; }
    } else if (B.etat === 'pause') {
      // ⚠️ Pendant qu'on reapprend un bouton de manette, ECHAP annule
      // l'apprentissage ; il ne sort pas de la pause.
      if (Entree.apprendEnCours()) { Hud.majMenu(); Entree.videPresse(); return; }
      // Sur l'ecran MANETTE, START sert a se voir s'allumer, pas a reprendre.
      const sortir = B.menu && B.menu.manetteInerte ? Entree.neufSansManette : Entree.neuf;
      if (sortir('pause')) { reprendre(); Entree.videPresse(); return; }
      if (B.menu) Hud.majMenu();
      else if (Entree.neuf('action')) reprendre();
      // Fermer le dernier menu avec FRAPPE, c'est reprendre.
      if (!B.menu && B.etat === 'pause') reprendre();
    }
    Entree.videPresse();
  }

  function rendre() {
    if (!B.carte) return;
    B.image++;                          // l'horloge de l'OEIL : elle avance meme quand le monde est fige
    const ctx = Base.debut();
    ctx.fillStyle = '#0b0a12';
    ctx.fillRect(0, 0, VW, VH);
    const cam = B.cam;
    const sec = B.cam.secousse > 0.05 ? B.cam.secousse : 0;
    const vue = { x: cam.x + (sec ? (Math.random() - 0.5) * sec * 8 : 0), y: cam.y + (sec ? (Math.random() - 0.5) * sec * 8 : 0) };
    Monde.dessinerSol(ctx, vue);
    // ⚠️ Les battants PAR-DESSUS le sol, jamais dedans : repeindre un
    // morceau de 256 px a chaque image pour une porte tuerait le cache.
    if (!B.interieur) Monde.dessinerBattants(ctx, vue);
    Entites.dessinerDecals(ctx, vue);     // le sang est SOUS les pieds
    Entites.dessiner(ctx, vue);
    Entites.dessinerParticules(ctx, vue);
    if (B.options.trace && !B.interieur) Vehicules.dessinerTrace(ctx, vue);
    if (!B.interieur) Police.dessinerHelico(ctx, vue);
    const lampes = Monde.lampesVisibles(vue);
    const projecteur = !B.interieur ? Police.lampeHelico(vue) : null;
    if (projecteur && Monde.ambiance().alpha > 0.2) lampes.unshift(projecteur);
    Base.fin(Monde.ambiance(), lampes);
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
    Object.assign(B.options, Sauvegarde.lireOptions() || {});
    // Les boutons de manette reappris par le joueur (ecran OPTIONS > MANETTE).
    Entree.reglerManette(B.options.manette);
    // ?trace=1 (ou ?perf=1) dans l'adresse : le mode s'allume sans passer par le menu.
    const adresse = (w.location && w.location.search) || '';
    if (/[?&]trace=1/.test(adresse)) B.options.trace = true;
    if (/[?&]perf=1/.test(adresse)) B.options.perf = true;
    Entree.init(d, w, w.navigator);
    Hud.init(d, racine);
    B.rng = mulberry(B.graine);

    function redim() { Base.redimensionner(w, Entree.estTactile); }
    w.addEventListener('resize', redim);
    w.addEventListener('orientationchange', function () { setTimeout(redim, 120); });
    if (w.visualViewport) w.visualViewport.addEventListener('resize', redim);
    d.addEventListener('visibilitychange', function () { if (d.hidden) { pause(); Son.suspendre(); } });
    // ⚠️ La page s'en va : on rend la carte son — mais SEULEMENT si elle ne peut
    // pas revenir. `persisted` dit que le navigateur la met de cote (bfcache,
    // le geste le plus banal sur telephone : changer d'application). Fermer
    // dans ce cas-la viderait les sons decodes et la page reviendrait muette.
    w.addEventListener('pagehide', function (ev) { if (!ev || !ev.persisted) Son.fermer(); });
    d.addEventListener('pointerdown', function () { Son.reveiller(); Hud.majAvisSon(); }, { passive: true });
    d.addEventListener('keydown', function () { Son.reveiller(); Hud.majAvisSon(); }, { passive: true });
    // On sonde tout de suite : le contexte naît « suspended » si la page n'a
    // recu aucun geste, et c'est la seule facon de savoir — avant de jouer —
    // qu'on va jouer en silence.
    Son.surEtat(function () { Hud.majAvisSon(); });
    Son.sonder();
    Hud.majAvisSon();
    redim();

    return chargerDefinitions(racine.dataset.urlDefinitions).then(function (defs) {
      B.defs = defs;
      Monde.charger(defs.carte);
      B.partie = Sauvegarde.completer(Sauvegarde.lire(), defs);
      if (B.partie.empreinte && B.partie.empreinte !== defs.empreinte) {
        // Le catalogue a change : on garde la partie, mais une position qui
        // n'existe plus sur la nouvelle carte doit etre oubliee — la sienne, et
        // celle du char gare devant la planque.
        B.partie.x = null; B.partie.y = null;
        if (B.partie.planque && B.partie.planque.vehicule) {
          B.partie.planque.vehicule.x = null; B.partie.planque.vehicule.y = null;
        }
      }
      const app = defs.carte.apparition.joueur;
      Monde.centrerCamera(app.x * TT, app.y * TT);
      B.etat = 'titre';
      Hud.etat('titre');
      Hud.voile('titre');
      // ⚠️ Le theme se DEMANDE ici, mais il ne sortira qu'au premier geste :
      // tant que le navigateur retient le son, `Mus.tick()` se contente
      // d'avancer son compteur. C'est le bandeau du titre qui reclame ce geste.
      Son.Mus.jouer('titre');
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

  return { demarrer, commencer, entrer, sortir, changerEtage, transiter, finirTransition, pause, reprendre, basculerPause, ouvrirCarte, fermerCarte, retourTitre, maj, rendre, get horsLigne() { return horsLigne; } };
})();

/* Surface de test et de debogage — la seule poignee du banc d'essai. */
if (typeof window !== 'undefined') {
  window.BANDINI = {
    B: B, VW: VW, VH: VH, TT: TT,
    Base: Base, Atlas: Atlas, Entree: Entree, Son: Son, Monde: Monde, Entites: Entites, Combat: Combat,
    Vehicules: Vehicules, Police: Police, Missions: Missions, Histoire: Histoire, Hud: Hud, Jeu: Jeu, Sauvegarde: Sauvegarde,
    SPRITES: SPRITES, TUILES: TUILES, DECORS: DECORS, DECALS: DECALS, OBJETS: OBJETS, FACADES: FACADES,
    ETOILE: ETOILE,
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
