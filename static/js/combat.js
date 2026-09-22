/* Bandini — combat : melee, coup fort, roulade, projectiles, sang, ramassage.

   Un coup se joue en trois temps, pour tout le monde (joueur comme PNJ) :
   ANTICIPATION (on voit le geste venir), ACTIF (l'arc blesse), REPOS (on est
   decouvert). Les durees viennent du catalogue d'armes, en Python.

   ⚠️ Une attaque ne touche qu'UNE FOIS par cible : `touches` retient les
   identifiants deja frappes. Sans cela, un arc actif pendant cinq images
   frappe cinq fois et un coup de batte tue un passant net.

   Les armes a feu (14 sept. 2026) : une arme `auto` tire tant qu'on TIENT, la
   cadence rythme la rafale et la dispersion s'ouvre avec elle ; un coup de
   feu S'ENTEND (`Police.entendre`, rayon `bruit` de la fiche) ; et une
   bouteille a `feu_s` laisse un BRASIER la ou elle casse — une entite
   invisible qui crache des particules et mord ce qui reste dedans. ⚠️ Jamais
   une tuile repeinte : le sol est cuit dans les morceaux. */

const Combat = (function () {
  'use strict';

  const CHARGE_MIN = 20;          // images de maintien pour un coup fort
  const COUP_FORT_DEGATS = 1.8;
  const ASSIST_DEGRES = 26, ASSIST_PORTEE = 220;
  const ROULADE_IMAGES = 16, ROULADE_COUT = 25, ROULADE_VITESSE = 3.4;
  //: Le verrouillage de cible (17 sept. 2026, demande de Martin : « on rate
  //: trop souvent un ennemi tout proche »). Un ennemi colle au joueur peut
  //: quand meme tomber hors du cone d'attaque si `e.angle` n'a pas ete
  //: rafraichi depuis le dernier pas (`regarder`, `entites.js`) — s'arreter
  //: pour cogner suffit a le manquer. VERROUILLER force l'angle sur une cible
  //: choisie, image apres image, qu'on bouge ou non.
  //:
  //: Un seul bouton, comme la roue d'armes (voir plus bas) :
  //: - une TAPE verrouille l'ennemi le plus proche, ou — deja verrouille —
  //:   passe au suivant (le plus proche APRES celui-la, dans l'ordre des
  //:   distances, en boucle).
  //: - TENIR au-dela de `TENIR_IMAGES` deverrouille.
  //: - Le verrouillage se lache aussi tout seul : cible morte, hors de
  //:   `VERROU_PORTEE`, ou plus de ligne de vue.
  const VERROU_PORTEE = 260;
  let verrouTenu = 0;

  //: Le selecteur d'arme. ⚠️ Le catalogue compte TREIZE armes, et jusqu'au
  //: 16 sept. 2026 un seul bouton les parcourait d'un cran, dans un seul
  //: sens : revenir de la carabine aux poings coutait DOUZE pressions, en
  //: pleine fusillade, sans rien voir venir (le HUD ne montre que l'arme en
  //: main). Deux gestes sur le meme bouton remplacent ca :
  //:
  //: - une TAPE (relachee avant `TENIR_IMAGES`) bascule entre les deux
  //:   dernieres armes — les poings pour les poches, la carabine pour le
  //:   toit. C'est le geste qu'on fait le plus souvent : il ne coute rien.
  //: - TENIR ouvre la ROUE : les armes possedees en cercle, on choisit a la
  //:   DIRECTION (stick, fleches, pouce), on relache pour degainer.
  const TENIR_IMAGES = 12;        // au-dela, ARME ouvre la roue (un cinquieme de seconde)
  //: ⚠️ La roue ne FIGE pas le monde, elle le RALENTIT : une image de monde
  //: sur quatre. Les menus du jeu figent (« le temps ne passe pas au
  //: comptoir ») et c'est juste pour un comptoir ; une roue qui fige, elle,
  //: est une pause gratuite au milieu d'une fusillade. Changer d'arme sous le
  //: feu doit couter quelque chose — comme la cloture, ou l'on ne fait rien.
  const RALENTI = 4;
  const ROUE_ZONE_MORTE = 0.45;   // en deca, la direction ne choisit rien
  //: Depuis combien d'images ARME est tenu (0 = relache). Module, pas partie :
  //: un bouton tenu ne survit pas a un rechargement.
  let tenu = 0;

  function armeDef(slug) {
    return (B.defs.armes || []).find(function (a) { return a.slug === slug; }) || null;
  }

  function regles() {
    return B.defs.armes_regles || { rafale_images: 45, incendie: { rayon_px: 20, degats_par_seconde: 12 } };
  }

  function armeCourante() { return armeDef(B.joueur ? B.joueur.arme : 'poings') || armeDef('poings'); }

  function munitions(slug) {
    const sac = B.partie.armes[slug];
    return sac ? sac.mun : null;
  }

  function possede(slug) { return !!B.partie.armes[slug]; }

  /** Ajoute une arme au sac (et ses munitions). Rend false si rien de neuf. */
  function ramasserArme(slug, mun) {
    const def = armeDef(slug);
    if (!def) return false;
    const sac = B.partie.armes[slug];
    if (!sac) {
      B.partie.armes[slug] = { mun: def.chargeur === null ? null : (mun || def.chargeur), usure: 0 };
    } else if (def.chargeur !== null) {
      sac.mun = Math.min(def.munitions_max, sac.mun + (mun || def.chargeur));
    } else if (def.usures) {
      sac.usure = 0;
    } else {
      return false;
    }
    Son.SFX.ramasse();
    return true;
  }

  function perdreArme(e, slug) {
    delete B.partie.armes[slug];
    if (e.arme === slug) { e.arme = 'poings'; B.partie.arme = 'poings'; }
    Hud.message('ARME CASSÉE');
    Son.SFX.casse();
  }

  // --- Frapper --------------------------------------------------------------------

  /** Commence une attaque. `fort` = coup charge (projection). */
  function frapper(e, fort) {
    const arme = armeDef(e.arme || 'poings') || armeDef('poings');
    if (!arme || e.etat === 'attaque' || e.roule > 0) return false;
    if (arme.type === 'tir') return tirer(e, arme);
    // ⚠️ ON SE SOUVIENT DE CE QU'ON FAISAIT. `e.etat` est ecrase par 'attaque'
    // le temps des trois temps du coup ; sans memoire, la seule sortie ecrite
    // etait « attaquer le joueur », et un Cravate qui se battait avec une Morue
    // se retournait contre lui des le premier coup porte.
    e.avantLeCoup = e.etat;
    e.etat = 'attaque';
    e.arc = arme;
    e.fort = !!fort && arme.type === 'melee';
    e.phase = 'anticipation';
    e.phaseT = arme.anticipation;
    e.touches = [];
    if (e === B.joueur && arme.etoiles_usage > 0) {
      Police.signalerCrime('arme_sortie', e.x, e.y, Police.quelqu_un_voit(e.x, e.y, e));
    }
    return true;
  }

  /** Avance les trois temps du coup et applique l'arc pendant la phase active. */
  function majAttaque(e) {
    if (e.etat !== 'attaque') return;
    const arme = e.arc || armeDef('poings');
    if (--e.phaseT > 0) {
      if (e.phase === 'actif') arcDeMelee(e, arme);
      return;
    }
    if (e.phase === 'anticipation') {
      e.phase = 'actif';
      e.phaseT = arme.actif;
      // La batte, le couteau... chacune son son — entendu de LA OU frappe
      // celui qui frappe : une rixe hors champ ne s'entend pas.
      Son.depuis(e, function () { Son.SFX.arme(arme); });
      if (arme.type === 'jet') return;
      arcDeMelee(e, arme);
    } else if (e.phase === 'actif') {
      e.phase = 'repos';
      e.phaseT = Math.max(2, arme.cadence - arme.anticipation - arme.actif);
    } else {
      e.phase = null;
      if (e.type === 'joueur') { e.etat = 'flane'; return; }
      // On reprend ce qu'on faisait avant de frapper — se battre avec l'autre
      // gang, le plus souvent s'en prendre au joueur. Le repli reste `blesser`
      // ou `alerter`, qui ont deja change l'etat pendant le coup : dans ce
      // cas-la ils ont efface la memoire, et c'est eux qui tranchent.
      e.etat = e.avantLeCoup || 'attaque_joueur';
      e.avantLeCoup = null;
    }
  }

  /** Qui se trouve dans l'arc devant `e` ? Une seule fois par coup. */
  function arcDeMelee(e, arme) {
    const portee = arme.portee + 6;
    const demi = arme.arc / 2 * (e.fort ? 1.25 : 1);
    // ⚠️ A BOUT PORTANT, L'ANGLE VIENT DU DERNIER PAS, PAS DE LA CIBLE :
    // `e.angle` n'est ecrit que quand on bouge (`regarder`, appele depuis
    // `majJoueur`). S'arreter pour cogner un ennemi qui a devie de quelques
    // pixels suffisait a le manquer, meme colle contre lui. Le meme
    // rattrapage que `tirer` (`viseeAssistee`), mais borne a la portee de
    // l'arme pour ne pas accrocher un passant plus loin, mieux aligne, que
    // celui qu'on a sous le nez.
    const angle = e === B.joueur ? viseeAssistee(e, e.angle, portee) : e.angle;
    const cibles = Entites.autour(e.x, e.y, portee + 8, function (c) {
      return c !== e && c.vivant && (c.type === 'pieton' || c.type === 'joueur');
    });
    for (const c of cibles) {
      if (e.touches.indexOf(c.id) >= 0) continue;
      // ⚠️ LES PASSANTS NE SE BATTENT PAS ENTRE EUX — sauf deux gangs, et
      // seulement l'une contre l'autre. C'est la seule inimitie que la ville
      // connaisse, et elle est ecrite ici plutot que dans l'etat `bagarre` pour
      // une raison : un coup perdu dans une rixe ne doit pas faucher le passant
      // qui regardait, et c'est le meme test qui l'en protege.
      if (e.type === 'pieton' && c.type === 'pieton'
          && !(e.gang && c.gang && e.gang !== c.gang)) continue;
      const ecart = Math.abs(ecartAngle(angle, angleVers(e.x, e.y, c.x, c.y)));
      if (ecart > demi) continue;
      if (!Monde.ligneLibre(e.x, e.y, c.x, c.y)) continue;
      e.touches.push(c.id);
      const degats = Math.round(arme.degats * (e.fort ? COUP_FORT_DEGATS : 1));
      Entites.blesser(c, degats, e, {
        renverse: arme.renverse || e.fort,
        saigne: arme.saigne,
        // ⚠️ A mains nues on ASSOMME : c'est ce qui permet de faire taire un
        // temoin sans en faire un meurtre, et la difference vaut 2 etoiles.
        // Le poing americain aussi (`armes.py`, champ `assomme`) : c'est
        // un poing, plus lourd.
        assomme: !!arme.assomme,
        angle: angleVers(e.x, e.y, c.x, c.y),
      });
      if (e === B.joueur) {
        B.cam.secousse = e.fort ? 0.9 : 0.5;
        Entree.vibrer(e.fort ? 40 : 18);
        user(arme);
        if (c.vivant) {
          if (c.agent) Police.signalerCrime('coup_policier', c.x, c.y, true);
          else Police.signalerCrime('coup_pieton', c.x, c.y, Police.quelqu_un_voit(c.x, c.y, c));
        }
      }
    }
  }

  /** Une arme improvisee s'use a chaque coup porte, puis casse. */
  function user(arme) {
    if (!arme.usures) return;
    const sac = B.partie.armes[arme.slug];
    if (!sac) return;
    sac.usure = (sac.usure || 0) + 1;
    if (sac.usure >= arme.usures) perdreArme(B.joueur, arme.slug);
  }

  // --- Verrouillage -----------------------------------------------------------------

  /** Les ennemis a portee de verrouillage, du plus proche au plus loin, avec
      ligne de vue — le meme bassin que `viseeAssistee`, mais TOUS, pas
      seulement celui le mieux aligne. */
  function ciblesVerrouillables(e) {
    return Entites.pietonsAutour(e.x, e.y, VERROU_PORTEE)
      .filter(function (c) { return c !== e && Monde.ligneLibre(e.x, e.y, c.x, c.y); })
      .sort(function (a, b) { return dist2(e.x, e.y, a.x, a.y) - dist2(e.x, e.y, b.x, b.y); });
  }

  //: `verrouDeclenche` : ce TENIR a deja fait son geste (deverrouille) —
  //: sans lui, un bouton garde au-dela de `TENIR_IMAGES` reprenait a 0 et
  //: remontait, et le RELACHEMENT tombait en pleine remontee : il se relisait
  //: comme une TAPE et re-verrouillait aussitot ce qu'on venait de lacher.
  let verrouDeclenche = false;

  /** VERROUILLER : tape = verrouille/change de cible, tenir = deverrouille.
      Tant qu'une cible tient, `e.angle` pointe dessus a chaque image — c'est
      ce qui rend `arcDeMelee` et `viseeAssistee` fiables a bout portant, sans
      qu'ils aient eux-memes rien a savoir du verrouillage. */
  function majCible(e) {
    if (e.cible && (!e.cible.vivant || dist2(e.x, e.y, e.cible.x, e.cible.y) > VERROU_PORTEE * VERROU_PORTEE
        || !Monde.ligneLibre(e.x, e.y, e.cible.x, e.cible.y))) {
      e.cible = null;
    }
    if (Entree.neuf('verrouiller')) { verrouTenu = 1; verrouDeclenche = false; }
    else if (Entree.bas('verrouiller') && verrouTenu > 0) verrouTenu++;
    if (Entree.bas('verrouiller')) {
      if (!verrouDeclenche && verrouTenu > TENIR_IMAGES) { e.cible = null; verrouDeclenche = true; }
    } else {
      if (verrouTenu > 0 && !verrouDeclenche) {
        // Relache avant TENIR_IMAGES, et pas deja deverrouille : une TAPE.
        const cibles = ciblesVerrouillables(e);
        if (cibles.length) e.cible = cibles[(cibles.indexOf(e.cible) + 1) % cibles.length];
      }
      verrouTenu = 0;
      verrouDeclenche = false;
    }
    if (e.cible) Entites.regarder(e, e.cible.x - e.x, e.cible.y - e.y);
  }

  // --- Tirer ----------------------------------------------------------------------

  /** L'angle corrige vers l'ennemi le plus proche dans le cone de visee.
      `rayon` borne la recherche (la mêlée passe sa portée, courte : sans
      ça un passant loin mais mieux aligné volerait l'assistance à celui
      qu'on a sous le nez). */
  function viseeAssistee(e, angle, rayon) {
    let meilleur = angle, ecartMin = ASSIST_DEGRES * Math.PI / 180;
    for (const c of Entites.pietonsAutour(e.x, e.y, rayon || ASSIST_PORTEE)) {
      if (c === e) continue;
      const vers = angleVers(e.x, e.y, c.x, c.y);
      const ecart = Math.abs(ecartAngle(angle, vers));
      if (ecart < ecartMin && Monde.ligneLibre(e.x, e.y, c.x, c.y)) {
        ecartMin = ecart;
        meilleur = vers;
      }
    }
    return meilleur;
  }

  /** La dispersion du coup qui part. Une arme automatique s'ouvre avec la
      RAFALE : de `dispersion` a `dispersion_max` en `rafale_images` de bouton
      tenu, et `maj` remet `rafale` a zero des qu'on lache. */
  function dispersionDe(e, arme) {
    if (!arme.auto || e !== B.joueur) return arme.dispersion;
    const part = Math.min(1, (e.rafale || 0) / regles().rafale_images);
    return arme.dispersion + (arme.dispersion_max - arme.dispersion) * part;
  }

  function tirer(e, arme) {
    const joueur = e === B.joueur;
    if (joueur) {
      const reste = munitions(arme.slug);
      // ⚠️ La gachette a vide CLIQUE : le buzzer des menus faisait croire
      // que le bouton etait casse, pas le chargeur.
      if (!triche('munitions') && reste !== null && reste <= 0) { Son.SFX.vide(); return false; }
    }
    e.etat = 'attaque';
    e.arc = arme;
    e.phase = 'repos';
    e.phaseT = arme.cadence;
    e.touches = [];
    // ⚠️ APRES UN COUP DE FEU, LA RUE NE REPREND PAS SON MURMURE : elle revient
    // en CRIS, puis se calme. Une foule qui murmure pareil avant et apres un
    // coup de feu n'est pas une foule, c'est un bruit de fond. Le bouchon de
    // foire, lui, ne fait pas lever la tete : la fetes reste une fete.
    if (!arme.foire) Son.Rumeur.crier();
    // ⚠️ **PAS DE VISÉE ASSISTÉE POUR LE BOUCHON DE FOIRE** : dans une allée
    // pleine de monde, l'assistance détournerait chaque tir vers le passant le
    // mieux aligné — des gens immunisés, des cibles qui restent debout, et une
    // galerie injouable. On vise SA cible, là où on regarde.
    const angle = joueur ? (arme.foire ? e.angle : viseeAssistee(e, e.angle)) : angleVers(e.x, e.y, B.joueur.x, B.joueur.y);
    const dispersion = dispersionDe(e, arme);
    for (let i = 0; i < (arme.plombs || 1); i++) {
      const devie = angle + (B.rng() - 0.5) * dispersion * 2;
      Entites.creer('projectile', e.x + Math.cos(angle) * 8, e.y + Math.sin(angle) * 8 - 6, {
        r: 2, dessine: false, tireur: e, degats: arme.degats, arme: arme.slug,
        saigne: arme.saigne, cloche: !!arme.cloche, feu_s: arme.feu_s || 0,
        foire: !!arme.foire,
        vx: Math.cos(devie) * arme.vitesse_projectile,
        vy: Math.sin(devie) * arme.vitesse_projectile,
        z: 6, vz: arme.cloche ? 1.6 : 0, portee: arme.portee, parcouru: 0,
      });
    }
    // L'eclair de bouche : trois etincelles au bout du canon, une fraction de seconde.
    for (let i = 0; i < 3; i++) {
      Entites.particule(e.x + Math.cos(angle) * 12, e.y - 7 + Math.sin(angle) * 9,
                        Math.cos(angle) * (1 + i * 0.7) + (B.rng() - 0.5) * 0.4, Math.sin(angle) * (1 + i * 0.7) * 0.7,
                        4 + i, i === 0 ? '#ffffff' : '#ffd23a', 2, 0);
    }
    if (joueur) {
      const sac = B.partie.armes[arme.slug];
      if (!triche('munitions') && sac && sac.mun !== null) sac.mun = Math.max(0, sac.mun - 1);
      B.cam.secousse = 0.6;
      Entree.vibrer(25);
      // ⚠️ **LA CARABINE À BOUCHON DE LA FOIRE N'EST PAS UNE ARME** : pas de
      // crime signalé, personne ne fuit, aucun agent n'entend le petit « pop ».
      // C'est un jeu d'adresse devant un comptoir, pas un stand de tir en ville
      // — et sans cette porte, jouer à la galerie vidait l'allée et nous
      // mettait la police au cul pour une partie de foire.
      if (!arme.foire) {
        Police.signalerCrime('arme_sortie', e.x, e.y, Police.quelqu_un_voit(e.x, e.y, e));
        Entites.alerter(e.x, e.y, e, 3);
        // ⚠️ Un coup de feu s'entend : hors du cone, sans ligne de vue. Tirer
        // de loin t'evite d'etre vu, jamais d'etre cherche.
        if (arme.bruit > 0) Police.entendre(e.x, e.y, arme.bruit * TT);
      }
    }
    // Le coup de feu, la fronde qui claque — sauf la bouteille, qu'on entend
    // quand elle CASSE (`allumer`), pas quand elle part.
    if (!arme.feu_s) Son.SFX.arme(arme);
    return true;
  }

  // --- Le feu -----------------------------------------------------------------------

  /** La bouteille casse ici : un brasier de `feu_s` secondes. Sur l'eau, rien
      qu'un remous — l'essence ne brule pas la baie. */
  function allumer(x, y, p) {
    const tx = Math.floor(x / TT), ty = Math.floor(y / TT);
    if (Monde.estEau && Monde.estEau(tx, ty)) { Entites.remous(x, y, 8); return null; }
    const inc = regles().incendie;
    Son.SFX.arme(armeDef(p.arme));
    Entites.decal(x, y, 'impact');
    for (let i = 0; i < 10; i++) {
      const a = B.rng() * Math.PI * 2, v = 0.6 + B.rng() * 1.4;
      Entites.particule(x, y, Math.cos(a) * v, Math.sin(a) * v * 0.6, 14 + B.rng() * 8, i % 3 ? '#ff8c1a' : '#ffd23a', 2, 0.04);
    }
    return Entites.creer('brasier', x, y, {
      r: inc.rayon_px, dessine: false, solide: false, auteur: p.tireur, reste: p.feu_s * 60,
    });
  }

  /** Les brasiers : des flammes (particules), de la fumee, et une morsure
      toutes les vingt images a qui reste dedans — passant, joueur, char. La
      derniere seconde, il s'affaisse ; puis il s'eteint et laisse une tache.
      ⚠️ Un char qui brule tombe sous `feu_sous` et continue tout seul
      (`Vehicules`), avec le lanceur pour agresseur : s'il explose, c'est SON
      explosion. Et une mort dans le feu est une mort du lanceur —
      `Entites.tuer(e, auteur)` la signale comme telle. */
  function majBrasiers() {
    const inc = regles().incendie;
    for (let i = B.entites.length - 1; i >= 0; i--) {
      const f = B.entites[i];
      if (f.type !== 'brasier') continue;
      f.reste--;
      const vif = Math.min(1, f.reste / 60);
      if (B.t % 2 === 0) {
        const a = B.rng() * Math.PI * 2, d = B.rng() * f.r * (0.4 + vif * 0.6);
        Entites.particule(f.x + Math.cos(a) * d, f.y + Math.sin(a) * d * 0.6, (B.rng() - 0.5) * 0.3, -0.4 - B.rng() * 0.4,
                          12 + vif * 12, B.rng() < 0.5 ? '#ff8c1a' : '#ffd23a', 2, -0.02);
      }
      if (B.t % 9 === 0) Entites.particule(f.x + (B.rng() - 0.5) * f.r, f.y - 4, (B.rng() - 0.5) * 0.3, -0.3, 40, '#3a3a3a', 2, -0.01);
      if (B.t % 20 === 0) {
        const degats = Math.max(1, Math.round(inc.degats_par_seconde / 3));
        const dedans = Entites.autour(f.x, f.y, f.r + 12, function (q) {
          return q.vivant && (q.type === 'pieton' || q.type === 'joueur' || q.type === 'vehicule');
        });
        for (const c of dedans) {
          if (Math.hypot(c.x - f.x, (c.y - f.y) / 0.6) > f.r) continue;
          if (c.type === 'vehicule') { Vehicules.endommager(c, degats, f.auteur); continue; }
          if (c.z > 8 || c.dansVehicule) continue;
          // Pousse HORS du feu, pas loin du lanceur.
          Entites.blesser(c, degats, f.auteur, { angle: angleVers(f.x, f.y, c.x, c.y), assomme: false, renverse: false });
        }
        // ⚠️ Et le DECOR, que `q.vivant` ne prend pas : un banc au milieu d'une
        // flaque de feu qui brule cinq secondes et qui en ressort intact, c'est
        // la meme panne que la balle qui traversait le lampadaire.
        for (const d of Entites.decorAutour(f.x, f.y, f.r + 12)) {
          if (d.brise) continue;
          if (Math.hypot(d.x - f.x, (d.y - f.y) / 0.6) > f.r) continue;
          Entites.endommagerDecor(d, degats);
        }
      }
      if (f.reste <= 0) { Entites.decal(f.x, f.y, 'impact'); Entites.retirer(f); }
    }
  }

  //: Le canon crache a `y - 6` — hauteur de poitrine — alors qu'un decor est
  //: ancre a ses PIEDS. On compare donc la balle au decor A LA MEME HAUTEUR,
  //: plutot que d'elargir la cible jusqu'a rattraper l'ecart.
  //:
  //: ⚠️ C'est la difference entre un banc et un BOUCLIER. Elargir de sept
  //: pixels — le chiffre du test des gens — donnait au banc une prise de douze
  //: pixels de rayon, plus large que celle d'un passant : la balle s'arretait
  //: sur le banc avant d'atteindre quelqu'un qui se tenait A COTE. A la bonne
  //: hauteur, deux pixels de marge suffisent — et le banc reste un abri pour
  //: qui se tient VRAIMENT derriere, dans son axe. Les deux moities se jugent
  //: ensemble (`test_un_banc_est_un_abri_sans_etre_un_bouclier`) : l'une ou
  //: l'autre toute seule se regle en tordant le chiffre.
  const HAUTEUR_CANON = 6;
  const MARGE_DECOR = 2;

  /** La distance du decor au TRAJET de l'image, pas au point d'arrivee.

      ⚠️ Une balle de carabine avance de dix pixels par image et un lampadaire
      en fait huit de large : juger sur le point d'arrivee la fait TRAVERSER le
      poteau une fois sur deux, sans rien toucher, et le bogue ne se voit qu'a
      l'arme rapide. Le segment, lui, ne saute rien. */
  function distanceAuTrajet(p, px, py) {
    const ax = p.x - p.vx, ay = p.y - p.vy;
    const long2 = p.vx * p.vx + p.vy * p.vy;
    let t = long2 > 0 ? ((px - ax) * p.vx + (py - ay) * p.vy) / long2 : 0;
    t = Math.max(0, Math.min(1, t));
    return Math.hypot(px - (ax + p.vx * t), py - (ay + p.vy * t));
  }

  /** La balle mord le decor qu'elle traverse. Rend vrai si elle s'y ARRETE.

      Ce qui porte `pv` s'use et finit par tomber ; ce qui porte `arrete` (un
      arbre, une fontaine, un camion-restaurant) encaisse sans jamais tomber —
      et c'est ce qui fait un abri dans une fusillade. Ce qui n'est ni l'un ni
      l'autre (un feu de circulation, un panneau) se traverse comme avant : on
      ne demonte pas la signalisation a la balle.

      ⚠️ **Appele APRES le test des gens**, jamais avant : a egalite, c'est la
      personne qui prend la balle, pas le mobilier.

      ⚠️ Un buisson et une corde a linge s'effeuillent mais n'arretent RIEN :
      c'est `solide` qui tranche, pas la presence dans l'index — depuis qu'il
      porte aussi le non-solide qui casse (voir `Entites.estIndexable`). */
  function mordreLeDecor(p) {
    if (p.z > 8) return false;             // ce qui part en cloche passe au-dessus
    const pas = Math.hypot(p.vx, p.vy);
    let arrete = false;
    for (const d of Entites.decorAutour(p.x, p.y, pas + 24)) {
      if (d.brise) continue;
      // ⚠️ **LE BOUCHON DE FOIRE NE CASSE QUE LES CIBLES** de la galerie
      // (`cible_foire`) : il traverse le reste de l'allée sans rien démonter.
      // Crever un kiosque ou une table de pique-nique depuis le stand serait
      // un sabotage, pas un jeu d'adresse.
      if (p.foire && d.decor !== 'cible_foire') continue;
      const fiche = DECORS[d.decor] || {};
      if (!fiche.pv && !fiche.arrete) continue;
      if (distanceAuTrajet(p, d.x, d.y - HAUTEUR_CANON) > (d.r || 4) + MARGE_DECOR) continue;
      // ⚠️ UNE BALLE, UNE MORSURE. Ce qui n'arrete pas la balle (un buisson,
      // une corde a linge) la laisse filer — et elle repassait a portee du MEME
      // decor a l'image suivante, lui remettant ses degats une seconde fois. Un
      // buisson de 15 PV tombait d'une seule balle de mitraillette a 9. C'est
      // le meme `e.touches` que la melee, pour la meme raison.
      if (!p.mordus) p.mordus = [];
      if (p.mordus.indexOf(d.id) >= 0) continue;
      p.mordus.push(d.id);
      Entites.endommagerDecor(d, p.degats);
      if (d.solide) arrete = true;
    }
    return arrete;
  }

  function majProjectiles() {
    for (let i = B.entites.length - 1; i >= 0; i--) {
      const p = B.entites[i];
      if (p.type !== 'projectile') continue;
      const pas = Math.hypot(p.vx, p.vy);
      p.x += p.vx; p.y += p.vy;
      p.parcouru += pas;
      if (p.cloche) { p.z += p.vz; p.vz -= 0.12; }
      const tx = Math.floor(p.x / TT), ty = Math.floor(p.y / TT);
      if (Monde.solidite(tx, ty) === 1 && p.z <= 8) {
        Entites.poussiere(p.x, p.y, 3);
        Entites.decal(p.x, p.y, 'impact');
        Entites.retirer(p);
        if (p.feu_s) allumer(p.x - p.vx, p.y - p.vy, p);     // au pied du mur, pas dedans
        continue;
      }
      const touche = Entites.autour(p.x, p.y, 7, function (c) {
        // ⚠️ **LE BOUCHON DE FOIRE NE BLESSE PERSONNE** : il ne vise que les
        // cibles de la galerie, jamais un passant, un donneur, une mascotte. Un
        // joueur qui arrose l'allée ne doit pas transformer la fête en
        // carnage — il rate, c'est tout.
        if (p.foire) return false;
        return c !== p.tireur && c.vivant && (c.type === 'pieton' || c.type === 'joueur');
      })[0];
      if (touche && (!p.cloche || p.z < 14)) {
        // ⚠️ DANS UN CHAR, C'EST LA TOLE QUI PREND. `Entites.blesser` refuse
        // qui est assis dans un char — c'est la qu'est la regle — et sans cette
        // ligne, le seul effet de l'abri serait de faire DISPARAITRE la balle :
        // la police aurait pu vider ses chargeurs sur une carrosserie sans
        // jamais rien obtenir, et un char serait devenu le seul endroit du jeu
        // ou l'on ne risque rien. C'est le meme geste que le brasier, qui
        // endommage le char plutot que son conducteur.
        // ⚠️ Seule la balle qui aurait touche LE CONDUCTEUR mord la tole : tirer
        // sur le capot d'un char vide ne fait toujours rien.
        if (touche.dansVehicule) Vehicules.endommager(touche.dansVehicule, p.degats, p.tireur);
        else Entites.blesser(touche, p.degats, p.tireur, {
          saigne: p.saigne, angle: Math.atan2(p.vy, p.vx),
          assomme: false, renverse: false,
        });
        Entites.retirer(p);          // (la mort, s'il y en a une, est signalee par Entites.tuer)
        if (p.feu_s) allumer(p.x, p.y, p);
        continue;
      }
      if (mordreLeDecor(p)) {
        Entites.poussiere(p.x, p.y, 3);
        Entites.decal(p.x, p.y, 'impact');
        Entites.retirer(p);
        if (p.feu_s) allumer(p.x, p.y, p);
        continue;
      }
      if (p.parcouru > p.portee || (p.cloche && p.z <= 0)) {
        Entites.poussiere(p.x, p.y, 2);
        Entites.retirer(p);
        if (p.feu_s) allumer(p.x, p.y, p);
      }
    }
  }

  // --- Jet (extincteur) -----------------------------------------------------------

  function majJet(e) {
    const arme = e.arc;
    if (!arme || arme.type !== 'jet' || e.phase !== 'actif') return;
    const sac = B.partie.armes[arme.slug];
    if (e === B.joueur) {
      if (!triche('munitions') && (!sac || sac.mun <= 0)) { e.etat = 'flane'; e.phase = null; return; }
      if (!triche('munitions')) sac.mun--;
    }
    for (let i = 0; i < 3; i++) {
      const a = e.angle + (B.rng() - 0.5) * 0.7;
      const v = 2 + B.rng() * 1.5;
      Entites.particule(e.x + Math.cos(e.angle) * 8, e.y + Math.sin(e.angle) * 8 - 6,
                        Math.cos(a) * v, Math.sin(a) * v * 0.7, 22, '#e8e6de', 2, 0.02);
    }
    for (const c of Entites.autour(e.x, e.y, arme.portee, function (q) {
      return q !== e && q.vivant && q.type === 'pieton';
    })) {
      if (Math.abs(ecartAngle(e.angle, angleVers(e.x, e.y, c.x, c.y))) > 0.6) continue;
      c.aveugle = 90;
      c.etat = 'fuit';
      c.minuterie = 180;
      if (e.t % 20 === 0) Entites.blesser(c, arme.degats, e, { assomme: true });
    }
    // Le feu de bâtiment (P4) : le jet d'extincteur attire la flamme. ⚠️ C'est
    // `Incendies` qui décide de la règle — ici, on ne lui donne que la main qui
    // tient la gâchette.
    if (typeof Incendies !== 'undefined') Incendies.majJet(e);
  }

  // --- Ramasser, faire les poches -------------------------------------------------

  function objetSousLaMain(j) {
    return Entites.autour(j.x, j.y, 18, function (e) {
      return e.type === 'ramassage' && e.objet === 'arme' && faceA(j, e.x, e.y);
    })[0] || null;
  }

  /** Ses poches sont-elles a prendre, d'ici ? ⚠️ LA regle du pickpocket, dite une
      fois : `interactions.js` la lit aussi (un pourboire, une photo, un banc ne
      volent pas le geste de qui a quelqu'un dans le dos). */
  function pochesAPrendre(j, c) {
    const dos = B.defs.pietons.reactions.pickpocket_dos_degres * Math.PI / 180 / 2;
    if (c.gang || !c.vivant || c.argent <= 0 || !faceA(j, c.x, c.y)) return false;
    if (c.etat === 'assomme') return true;                 // assomme : les poches sont a nous
    // ⚠️ DERRIERE lui : on compare son regard a la direction d'ou l'on vient.
    return Math.abs(ecartAngle(c.angle, angleVers(c.x, c.y, j.x, j.y))) > Math.PI - dos;
  }

  function victimeDesPoches(j) {
    return Entites.pietonsAutour(j.x, j.y, 20).find(function (c) { return pochesAPrendre(j, c); }) || null;
  }

  function pickpocket(j) {
    const reactions = B.defs.pietons.reactions;
    const victime = victimeDesPoches(j);
    if (!victime) return false;
    Missions.encaisser(victime.argent, 'POCHES');
    victime.argent = 0;
    if (victime.etat !== 'assomme') {
      victime.etat = 'fuit';
      victime.minuterie = reactions.fuite_secondes * 60;
      victime.cri = 120;
      Entites.alerter(victime.x, victime.y, j, 1);
    }
    Police.signalerCrime('pickpocket', j.x, j.y, Police.quelqu_un_voit(j.x, j.y, victime));
    return true;
  }

  // --- Le selecteur : une tape, ou la roue -----------------------------------------

  /** Les armes possedees, dans l'ordre du catalogue. */
  function armesDuSac() {
    const ordre = B.defs.ordre_armes || ['poings'];
    return ordre.filter(function (s) { return B.partie.armes[s]; });
  }

  /** Une arme a feu a sec. La roue la montre GRISEE ; la tape et le cycle la
      sautent — un pistolet a zero pris au passage, c'est un tour perdu. */
  function aSec(slug) {
    const def = armeDef(slug);
    return !!def && def.chargeur !== null && !munitions(slug);
  }

  /** Degainer, en retenant ce qu'on tenait : c'est la memoire du retour rapide. */
  function degainer(e, slug) {
    if (!slug || !B.partie.armes[slug] || slug === e.arme) return false;
    if (e === B.joueur) { B.partie.armePrecedente = e.arme; B.partie.arme = slug; }
    e.arme = slug;
    Son.SFX.degainer();
    return true;
  }

  /** Le RETOUR RAPIDE : l'arme d'avant. A defaut — elle a casse, on l'a vendue,
      elle est a sec — on avance d'un cran : une tape ne reste jamais sans
      reponse, sinon le bouton a l'air brise. */
  function retourRapide(e) {
    const avant = B.partie.armePrecedente;
    if (avant && avant !== e.arme && B.partie.armes[avant] && !aSec(avant)) return degainer(e, avant);
    return cycler(e);
  }

  /** Un cran dans l'ordre du catalogue — le repli de la tape quand l'arme
      d'avant n'est plus prenable. ⚠️ PAS de sens inverse : la roue a rendu le
      cycle a rebours inutile, et le depot ne garde pas une branche que rien
      n'atteint (ni personne ne juge). */
  function cycler(e) {
    const possedees = armesDuSac();
    if (possedees.length < 2) return false;
    const i = possedees.indexOf(e.arme);
    const cran = function (n) { return possedees[(i + n) % possedees.length]; };
    for (let n = 1; n <= possedees.length; n++) {
      if (!aSec(cran(n))) return degainer(e, cran(n));
    }
    // Tout est a sec : mieux vaut une arme vide qu'un bouton qui ne repond pas.
    return degainer(e, cran(1));
  }

  /** Ouvrir la roue. ⚠️ Elle prend une PHOTO du sac : l'ordre ne doit pas
      bouger sous le pouce si une bouteille casse pendant qu'on choisit. */
  function ouvrirRoue(e) {
    const armes = armesDuSac();
    if (armes.length < 2) return false;
    const i = armes.indexOf(e.arme);
    B.roue = { armes: armes, choix: i < 0 ? 0 : i, t: 0 };
    Son.SFX.menu();
    return true;
  }

  /** Fermer la roue. `degaine` : on relache SUR un choix (sinon on annule —
      la pause, la carte, un char, la mort). */
  function fermerRoue(degaine) {
    const r = B.roue;
    if (!r) return false;
    B.roue = null;
    tenu = 0;
    if (degaine && B.joueur) return degainer(B.joueur, r.armes[r.choix]);
    return false;
  }

  /** Le creneau vise par la direction, ou -1 si elle ne pointe nulle part.
      ⚠️ Creneau 0 EN HAUT, puis dans le sens des aiguilles — c'est la lecture
      du dessin (`Hud.posteDeLaRoue`), et les deux doivent dire la meme chose. */
  function creneauVise(axe, n) {
    if (!axe || axe.mag <= ROUE_ZONE_MORTE || n < 1) return -1;
    const angle = Math.atan2(axe.y, axe.x) + Math.PI / 2;
    const i = Math.round(angle / (Math.PI * 2 / n));
    return ((i % n) + n) % n;
  }

  /** La roue et la tape, lues A CHAQUE IMAGE — meme quand le monde rampe.
      C'est `Jeu.maj` qui l'appelle, AVANT la simulation et hors du ralenti :
      une roue qui ne se lit qu'une image sur quatre repond au quart. */
  function majRoue() {
    const j = B.joueur;
    // Les memes gardes que le combat : au volant ARME est la RADIO, et en haut
    // d'une cloture on ne fait rien du tout.
    if (!j || j.dansVehicule || j.manege || !j.vivant || j.enjambe || j.alite || j.assis || B.cinema || B.piratage) {
      fermerRoue(false);
      tenu = 0;
      return;
    }
    if (B.roue) {
      const r = B.roue;
      r.t++;
      // ⚠️ Le choix RESTE quand la direction revient au centre : au pouce
      // comme au stick, on pointe, PUIS on relache le bouton — jamais les deux
      // dans la meme image. Sans ca, chaque choix retombe sur le creneau du
      // haut au moment ou on le valide.
      const vise = creneauVise(Entree.axe, r.armes.length);
      if (vise >= 0 && vise !== r.choix) { r.choix = vise; Son.SFX.menu(); }
      if (!Entree.bas('arme')) fermerRoue(true);
      return;
    }
    // ⚠️ LA PRESSION SE LATCHE, elle ne se lit pas qu'au niveau du bouton.
    // `Jeu.boucle` avance a PAS FIXE, par accumulateur : zero a quatre `maj`
    // par image dessinee. Une tape courte tombe donc parfois ENTIEREMENT
    // entre deux `maj`, et `bas` ne la voit jamais — mesure : une tape d'une
    // image se perdait une fois sur deux, et le bouton avait l'air brise.
    // `neuf`, lui, survit jusqu'au `videPresse` qui clot le tour : c'est le
    // seul signal qu'un pas variable ne peut pas manger.
    if (Entree.neuf('arme') && tenu < 1) tenu = 1;
    if (Entree.bas('arme')) {
      tenu++;
      if (tenu > TENIR_IMAGES) ouvrirRoue(j);
      return;
    }
    // Relache apres une pression courte : c'est une tape.
    if (tenu > 0) retourRapide(j);
    tenu = 0;
  }

  /** Le MONDE avance-t-il a cette image ? Roue ouverte, une sur `RALENTI`. */
  function tempsQuiPasse() {
    return !B.roue || B.roue.t % RALENTI === 0;
  }

  function roulade(j) {
    if (j.roule > 0 || j.endurance < ROULADE_COUT) return false;
    // Une roulade seulement quand ca compte : sinon `esquive` reste le sprint.
    const menace = Entites.pietonsAutour(j.x, j.y, 130).some(function (c) {
      return c.etat === 'attaque_joueur' || c.etat === 'attaque';
    });
    if (!menace && j.etat !== 'attaque') return false;
    const axe = Entree.axe;
    const angle = axe.mag > 0.2 ? Math.atan2(axe.y, axe.x) : j.angle;
    j.roule = ROULADE_IMAGES;
    j.invincible = ROULADE_IMAGES - 2;
    j.endurance -= ROULADE_COUT;
    j.vx = Math.cos(angle) * ROULADE_VITESSE;
    j.vy = Math.sin(angle) * ROULADE_VITESSE;
    j.etat = 'flane';
    Son.SFX.pas();
    return true;
  }

  // --- Boucle ---------------------------------------------------------------------

  // --- Le bouclier humain : une sortie de secours, jamais un abri -----------

  /** ⚠️ **Elle doit rester une SORTIE.** Un otage qu'on tient indefiniment,
      c'est l'invincibilite : on traverse la ville derriere un bonhomme et la
      police regarde. Trois choses l'en empechent, et elles vont ensemble : il
      SE DEBAT, il se degage tout seul au bout de `tenue_max_s`, et le compteur
      MONTE tant qu'on le tient. On gagne du temps, on ne gagne pas la partie —
      et on ressort plus recherche qu'on est entre. */
  function ficheBouclier() { return B.defs.recherche.bouclier; }

  /** Qui peut servir de bouclier. ⚠️ Pas un enfant, pas un agent, pas un
      personnage de l'histoire : les trois feraient du geste autre chose que ce
      qu'il est. Et A BOUT PORTANT — pas a travers la rue. */
  function otageSousLaMain(j) {
    if (!j || j.otage || j.dansVehicule || j.arme === 'poings' || B.interieur) return null;
    // ⚠️ Ce qu'ACTION sert APRES `interagir` passe avant nous : une arme par
    // terre, une porte, un char. Sans ca, s'arreter a cote de son char dans
    // une rue passante prenait un passant en otage au lieu de monter.
    if (objetSousLaMain(j) || Monde.porteDevant(j) || Vehicules.vehiculeSousLaMain(j)) return null;
    return Entites.pietonsAutour(j.x, j.y, ficheBouclier().portee_px).find(function (e) {
      return e.vivant && !e.agent && !e.intouchable && !e.petit && !e.commerce
        && !e.personnage && !e.mission && e.etat !== 'assomme' && faceA(j, e.x, e.y);
    }) || null;
  }

  /** ⚠️ IL FAUT UNE ARME. A mains nues, « prendre en otage » n'est qu'une
      prise : rien ne dit a la police pourquoi elle devrait s'arreter, et le
      geste n'aurait aucune lecture a l'ecran. */
  function prendreEnOtage(j, e) {
    if (!e) return false;
    j.otage = e;
    e.otage = true; e.otageT = 0;
    e.vx = 0; e.vy = 0;
    e.etat = 'flane'; e.cri = 0; e.vers = null; e.crime = null; e.porteBut = null;
    Police.signalerCrime('otage', j.x, j.y, true);
    Entites.bulle(e, ficheBouclier().dit.pris, { duree: 120 });
    Hud.message('BOUCLIER HUMAIN — LA POLICE N’OSE PLUS TIRER');
    return true;
  }

  /** ⚠️ **LA PRISE SE TIENT.** Remarque de Martin en jouant : une pression
      d'ACTION suffisait, et le bouclier est LE DERNIER de la chaine
      (`Missions.interagir`) — celui que le bouton fait quand il n'a rien
      trouve d'autre. On visait une porte d'un pas trop loin, une arme par
      terre, et on repartait avec un bonhomme dans les bras et deux etoiles
      qu'on n'avait pas demandees. La pression ARME la prise (`viserOtage`),
      c'est le maintien qui la prend.

      ⚠️ Et on rejuge `otageSousLaMain` a CHAQUE image, plutot que de garder la
      personne visee : c'est « qui est sous la main », pas « qui l'etait il y a
      une demi-seconde ». Un passant qui s'eloigne pendant qu'on insiste, une
      porte ou un char qui entre a portee — et l'invite du HUD annonce autre
      chose : la prise doit tomber avec elle, sinon le bouton ferait une chose
      quand l'ecran en promet une autre.

      ⚠️ **ET RELACHEE AVANT L'HEURE, C'ETAIT UNE TAPE : ELLE FAIT LES POCHES**
      (`majSaisie`). Retour de Martin : « je n'arrive plus a voler les gens ».
      La portee du bouclier couvre celle des poches, alors l'arme a la main
      chaque victime etait aussi un otage : la pression armait la prise, rendait
      `true`, et `pickpocket` n'etait plus jamais atteint. Taper fait les poches,
      tenir prend l'otage — un bouton, deux gestes. */
  function viserOtage(j) {
    j.saisie = 1;
    return true;
  }

  function majSaisie(j) {
    if (!j || !j.saisie) return;
    // ⚠️ `j.vivant` et `j.enjambe` ici, et pas dans `otageSousLaMain` : en haut
    // d'une cloture on ne fait RIEN, et un compteur laisse en l'air se
    // rallumerait tout seul a la prochaine pression sur ACTION — sans
    // nouvelle pression.
    // ⚠️ `B.roue` avec les autres : la roue ouverte, le monde rampe, et une
    // prise qui MURIT au quart de vitesse serait le meme ralenti a la demande
    // que la frappe (voir la porte de `maj`). Elle ne se met pas en pause, elle
    // RETOMBE — comme sous un char ou en haut d'une cloture : on lache pour
    // choisir son arme.
    // ⚠️ `dansVehicule` et `interieur` aussi, pour la tape : `otageSousLaMain`
    // les ecartait deja pour la prise, mais on ne fait pas les poches d'un
    // passant depuis un char ni a travers le mur d'une piece.
    const debout = j.vivant && !j.enjambe && !j.alite && !j.assis && !j.dansVehicule && !B.interieur
      && !B.cinema && !B.roue;
    // Relachee avant d'avoir muri : c'etait une tape (voir `viserOtage`).
    if (debout && !Entree.bas('action')) { j.saisie = 0; pickpocket(j); return; }
    const cible = debout && Entree.bas('action') ? otageSousLaMain(j) : null;
    if (!cible) { j.saisie = 0; return; }
    if (++j.saisie < Math.round(ficheBouclier().saisie_s * 60)) return;
    j.saisie = 0;
    prendreEnOtage(j, cible);
  }

  /** On le lache — de son plein gre, ou parce qu'il s'est degage. */
  function lacherOtage(deLuiMeme) {
    const j = B.joueur, e = j && j.otage;
    j.otage = null;
    if (!e) return false;
    e.otage = false; e.otageT = 0;
    if (e.vivant) {
      e.etat = 'fuit';
      e.menace = j;
      e.minuterie = B.defs.recherche.temoins.oubli_s * 60;
      e.cri = 120;
      Entites.bulle(e, ficheBouclier().dit.libre, { duree: 120 });
    }
    if (deLuiMeme) Hud.message('IL S’EST DÉGAGÉ');
    return true;
  }

  function majOtage() {
    const j = B.joueur;
    if (!j || !j.otage) return;
    const e = j.otage, f = ficheBouclier();
    // Mort, assomme, entre dans une piece, monte en char : on n'a plus d'otage.
    if (!e.vivant || e.etat === 'assomme' || B.interieur || j.dansVehicule || !j.vivant) {
      lacherOtage(false);
      return;
    }
    e.otageT++;
    // ⚠️ DEVANT, ENTRE TOI ET EUX — c'est ce qui fait de lui un bouclier et
    // pas un prisonnier qu'on traine. On le POUSSE (`deplacerCercle`) au lieu
    // de le poser : sinon on le glisse dans un mur et il y reste.
    const bx = j.x + Math.cos(j.angle) * f.devant_px;
    const by = j.y + Math.sin(j.angle) * f.devant_px;
    Entites.deplacerCercle(e, bx - e.x, by - e.y, Monde.MASQUE_PIETON);
    Entites.regarder(e, j.x - e.x, j.y - e.y);
    e.anim.dist += 0.6;
    // Le compteur monte tant qu'on le tient.
    Police.ajouterChaleur(f.chaleur_par_s / 60);
    // Il se debat : d'abord il gigote et il crie, puis il se degage.
    if (e.otageT === Math.round(f.debat_s * 60)) {
      Entites.bulle(e, f.dit.pris, { duree: 90 });
    }
    if (e.otageT > f.debat_s * 60) {
      const tremble = (e.otageT % 8 < 4) ? 1.5 : -1.5;
      Entites.deplacerCercle(e, 0, tremble, Monde.MASQUE_PIETON);
    }
    if (e.otageT >= f.tenue_max_s * 60) lacherOtage(true);
  }

  function maj() {
    const j = B.joueur;
    // ⚠️ AVANT LA BOUCLE D'ATTAQUE, plus bas : `arcDeMelee` lit `e.angle`
    // pendant la phase active, et c'est cette ligne qui le tient pointe sur
    // la cible verrouillee, image apres image, meme si le joueur ne bouge
    // pas. Un `j` qui n'existe pas encore (chargement) ne verrouille rien.
    if (j && j.vivant && !j.dansVehicule && !j.manege && !j.enjambe && !j.alite && !j.assis && !B.roue) majCible(j);
    else if (j) { j.cible = null; verrouTenu = 0; }
    majProjectiles();
    majBrasiers();
    majOtage();
    // ⚠️ AVANT les gardes du bas (char, mort, cloture) et avant la lecture
    // d'ACTION : la prise doit pouvoir RETOMBER dans les images ou le reste du
    // bouton ne se lit pas, sinon son compteur survit a un tour de char.
    majSaisie(j);
    for (const e of B.entites) {
      if (e.etat === 'attaque') { majAttaque(e); majJet(e); }
      if (e.aveugle > 0) e.aveugle--;
    }
    // Le jet de l'extincteur s'entend tant qu'il sort et se tait des qu'il
    // s'arrete — bouton relache, reservoir vide, char, mort : on redit la
    // verite a chaque image plutot que d'attraper chacune des sorties.
    Son.SFX.jet(!!j && j.vivant && !j.dansVehicule && j.etat === 'attaque'
                && !!j.arc && j.arc.type === 'jet' && j.phase === 'actif');
    // ⚠️ En haut d'une cloture, on ne fait RIEN : ni frapper, ni tirer, ni
    // rouler, ni ouvrir une porte. C'est ce prix-la qui fait d'une cloture un
    // choix plutot qu'un raccourci gratuit.
    // ⚠️ Couche dans un lit non plus : c'est le stick qui leve
    // (`Entites.majJoueur`), et un coup de poing donne depuis l'oreiller
    // partirait d'un corps qui n'est pas debout.
    // ⚠️ Assis dans un manège (`j.manege`), on ne frappe pas et on ne ramasse rien.
    if (!j || j.dansVehicule || j.manege || !j.vivant || j.enjambe || j.alite || j.assis) return;
    // ⚠️ ROUE OUVERTE, ON NE SE BAT PAS. Le monde rampe tant qu'elle est la :
    // pouvoir tirer dedans, ce serait un ralenti a la demande — tenir ARME,
    // viser tranquillement, tirer. On choisit son arme OU on se bat.
    // ⚠️ Et ACTION passe par ici : sans cette porte, relacher la roue devant
    // une porte ouvrirait la porte, et devant un passant lui ferait les poches.
    // ⚠️ Le piratage repurpose FRAPPE en ABANDONNER (`Histoire.majPiratage`) :
    // sans cette porte, la meme pression donnerait AUSSI un coup de poing.
    if (B.roue || B.piratage) return;

    if (Entree.neuf('esquive')) roulade(j);

    // Coup fort : on MAINTIENT la frappe, on relache quand c'est charge.
    const arme = armeCourante();
    if (arme.auto) {
      // ⚠️ Automatique : on TIENT. `frapper` refuse tant que la cadence court,
      // c'est elle qui rythme la rafale. Et a vide, la gachette tenue ne
      // clique qu'a la PRESSION — pas soixante fois par seconde.
      if (Entree.bas('attaque')) {
        if ((munitions(arme.slug) || 0) > 0 || Entree.neuf('attaque')) frapper(j, false);
        j.rafale = (j.rafale || 0) + 1;
      } else {
        j.rafale = 0;
      }
    } else if (Entree.bas('attaque') && arme.type === 'melee') {
      j.charge++;
    } else if (j.charge > 0) {
      frapper(j, j.charge >= CHARGE_MIN);
      j.charge = 0;
    } else if (Entree.neuf('attaque') && arme.type !== 'jet') {
      // ⚠️ Pas le jet : sans cette garde, la premiere pression partait par
      // ici — anticipation, quatre images de jet, deux de repos — AVANT que le
      // maintien ne prenne le relais juste dessous. Ca ne se voyait pas ; avec
      // une boucle qui s'allume et s'eteint, ca s'entend : un hoquet a chaque
      // depart.
      frapper(j, false);
    }
    if (Entree.bas('attaque') && arme.type === 'jet' && j.etat !== 'attaque') {
      frapper(j, false);
      j.phase = 'actif';
      j.phaseT = 9999;
    } else if (!Entree.bas('attaque') && arme.type === 'jet' && j.etat === 'attaque') {
      j.etat = 'flane';
      j.phase = null;
    }

    if (Entree.neuf('action')) {
      // Dedans : la sortie, ou un point (lit, coffre, comptoir...).
      // ⚠️ LA PORTE D'ABORD, et c'est un bloquant qui l'a decide (« chez
      // Ti-Paul, il est impossible de sortir »). `pointSousLaMain` attrape un
      // point dans 1,6 tuile AUTOUR de soi, quand `porteDevant` n'accepte que
      // la tuile collee a la porte : six pieces avaient un comptoir assez pres
      // de leur unique tuile de sortie pour voler ACTION a chaque fois, et
      // `utiliserPoint` rend `true` meme quand il n'a qu'un « PLUS TARD » a
      // dire — aucune deuxieme pression ne finissait par sortir.
      // Un comptoir se sert d'un pas de cote ; une porte, non.
      if (B.interieur) {
        if (Monde.porteDevant(j)) { Jeu.sortir(); return; }
        if (Missions.utiliserPoint(j)) return;
        return;
      }
      // ⚠️ L'ordre compte : on sert au kiosque avant de faire les poches du
      // vendeur, sinon on ne peut plus jamais acheter un hot-dog.
      if (Missions.interagir(j)) return;
      const objet = objetSousLaMain(j);
      if (objet) {
        j.animT = 14; j.animType = 'ramasse';         // on se penche
        if (ramasserArme(objet.arme, objet.munitions)) {
          Hud.message((armeDef(objet.arme) || {}).nom || 'ARME');
          j.arme = objet.arme;
          B.partie.arme = objet.arme;
        }
        Entites.retirer(objet);
      } else {
        const porte = Monde.porteDevant(j);
        // Une porte ne vend rien : un commerce s'achete au comptoir, dedans.
        if (porte) Jeu.entrer(porte);
        else pickpocket(j);
      }
    }
  }

  return {
    CHARGE_MIN, ROULADE_IMAGES, TENIR_IMAGES, RALENTI, armeDef, armeCourante, munitions, possede, regles,
    armesDuSac, aSec, degainer, retourRapide, ouvrirRoue, fermerRoue, creneauVise, majRoue, tempsQuiPasse,
    frapper, tirer, cycler, roulade, pickpocket, pochesAPrendre, victimeDesPoches, ramasserArme, objetSousLaMain,
    viseeAssistee, dispersionDe, allumer, majBrasiers, majAttaque, majProjectiles, maj,
    majCible, ciblesVerrouillables, VERROU_PORTEE,
    otageSousLaMain, viserOtage, prendreEnOtage, lacherOtage, majOtage, majSaisie,
  };
})();
