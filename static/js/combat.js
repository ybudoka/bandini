/* Bandini — combat : melee, coup fort, roulade, projectiles, sang, ramassage.

   Un coup se joue en trois temps, pour tout le monde (joueur comme PNJ) :
   ANTICIPATION (on voit le geste venir), ACTIF (l'arc blesse), REPOS (on est
   decouvert). Les durees viennent du catalogue d'armes, en Python.

   ⚠️ Une attaque ne touche qu'UNE FOIS par cible : `touches` retient les
   identifiants deja frappes. Sans cela, un arc actif pendant cinq images
   frappe cinq fois et un coup de batte tue un passant net. */

const Combat = (function () {
  'use strict';

  const CHARGE_MIN = 20;          // images de maintien pour un coup fort
  const COUP_FORT_DEGATS = 1.8;
  const ASSIST_DEGRES = 26, ASSIST_PORTEE = 220;
  const ROULADE_IMAGES = 16, ROULADE_COUT = 25, ROULADE_VITESSE = 3.4;

  function armeDef(slug) {
    return (B.defs.armes || []).find(function (a) { return a.slug === slug; }) || null;
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
    Hud.message('ARME CASSEE');
    Son.SFX.erreur();
  }

  // --- Frapper --------------------------------------------------------------------

  /** Commence une attaque. `fort` = coup charge (projection). */
  function frapper(e, fort) {
    const arme = armeDef(e.arme || 'poings') || armeDef('poings');
    if (!arme || e.etat === 'attaque' || e.roule > 0) return false;
    if (arme.type === 'tir') return tirer(e, arme);
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
      Son.SFX.coup();
      if (arme.type === 'jet') return;
      arcDeMelee(e, arme);
    } else if (e.phase === 'actif') {
      e.phase = 'repos';
      e.phaseT = Math.max(2, arme.cadence - arme.anticipation - arme.actif);
    } else {
      e.etat = e.type === 'joueur' ? 'flane' : e.etat;
      e.phase = null;
      if (e.type !== 'joueur' && e.etat === 'attaque') e.etat = 'attaque_joueur';
    }
  }

  /** Qui se trouve dans l'arc devant `e` ? Une seule fois par coup. */
  function arcDeMelee(e, arme) {
    const portee = arme.portee + 6;
    const demi = arme.arc / 2 * (e.fort ? 1.25 : 1);
    const cibles = Entites.autour(e.x, e.y, portee + 8, function (c) {
      return c !== e && c.vivant && (c.type === 'pieton' || c.type === 'joueur');
    });
    for (const c of cibles) {
      if (e.touches.indexOf(c.id) >= 0) continue;
      if (e.type === 'pieton' && c.type === 'pieton') continue;    // ils ne se battent pas entre eux
      const ecart = Math.abs(ecartAngle(e.angle, angleVers(e.x, e.y, c.x, c.y)));
      if (ecart > demi) continue;
      if (!Monde.ligneLibre(e.x, e.y, c.x, c.y)) continue;
      e.touches.push(c.id);
      const degats = Math.round(arme.degats * (e.fort ? COUP_FORT_DEGATS : 1));
      const poings = arme.slug === 'poings';
      Entites.blesser(c, degats, e, {
        renverse: arme.renverse || e.fort,
        saigne: arme.saigne,
        // ⚠️ A mains nues on ASSOMME : c'est ce qui permet de faire taire un
        // temoin sans en faire un meurtre, et la difference vaut 2 etoiles.
        assomme: poings,
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

  // --- Tirer ----------------------------------------------------------------------

  /** L'angle corrige vers l'ennemi le plus proche dans le cone de visee. */
  function viseeAssistee(e, angle) {
    let meilleur = angle, ecartMin = ASSIST_DEGRES * Math.PI / 180;
    for (const c of Entites.pietonsAutour(e.x, e.y, ASSIST_PORTEE)) {
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

  function tirer(e, arme) {
    const joueur = e === B.joueur;
    if (joueur) {
      const reste = munitions(arme.slug);
      if (reste !== null && reste <= 0) { Son.SFX.erreur(); return false; }
    }
    e.etat = 'attaque';
    e.arc = arme;
    e.phase = 'repos';
    e.phaseT = arme.cadence;
    e.touches = [];
    const angle = joueur ? viseeAssistee(e, e.angle) : angleVers(e.x, e.y, B.joueur.x, B.joueur.y);
    for (let i = 0; i < (arme.plombs || 1); i++) {
      const devie = angle + (B.rng() - 0.5) * arme.dispersion * 2;
      Entites.creer('projectile', e.x + Math.cos(angle) * 8, e.y + Math.sin(angle) * 8 - 6, {
        r: 2, dessine: false, tireur: e, degats: arme.degats, arme: arme.slug,
        saigne: arme.saigne, cloche: !!arme.cloche,
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
      if (sac && sac.mun !== null) sac.mun = Math.max(0, sac.mun - 1);
      B.cam.secousse = 0.6;
      Entree.vibrer(25);
      Police.signalerCrime('arme_sortie', e.x, e.y, Police.quelqu_un_voit(e.x, e.y, e));
      Entites.alerter(e.x, e.y, e, 3);
    }
    Son.SFX.coup();
    return true;
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
        continue;
      }
      const touche = Entites.autour(p.x, p.y, 7, function (c) {
        return c !== p.tireur && c.vivant && (c.type === 'pieton' || c.type === 'joueur');
      })[0];
      if (touche && (!p.cloche || p.z < 14)) {
        Entites.blesser(touche, p.degats, p.tireur, {
          saigne: p.saigne, angle: Math.atan2(p.vy, p.vx),
          assomme: false, renverse: false,
        });
        Entites.retirer(p);          // (la mort, s'il y en a une, est signalee par Entites.tuer)
        continue;
      }
      if (p.parcouru > p.portee || (p.cloche && p.z <= 0)) {
        Entites.poussiere(p.x, p.y, 2);
        Entites.retirer(p);
      }
    }
  }

  // --- Jet (extincteur) -----------------------------------------------------------

  function majJet(e) {
    const arme = e.arc;
    if (!arme || arme.type !== 'jet' || e.phase !== 'actif') return;
    const sac = B.partie.armes[arme.slug];
    if (e === B.joueur) {
      if (!sac || sac.mun <= 0) { e.etat = 'flane'; e.phase = null; return; }
      sac.mun--;
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
  }

  // --- Ramasser, faire les poches -------------------------------------------------

  function objetSousLaMain(j) {
    return Entites.autour(j.x, j.y, 18, function (e) { return e.type === 'ramassage'; })[0] || null;
  }

  function pickpocket(j) {
    const reactions = B.defs.pietons.reactions;
    const dos = reactions.pickpocket_dos_degres * Math.PI / 180 / 2;
    const victimes = Entites.pietonsAutour(j.x, j.y, 20).filter(function (c) {
      if (c.gang || !c.vivant || c.argent <= 0) return false;
      if (c.etat === 'assomme') return true;                 // assomme : les poches sont a nous
      // ⚠️ DERRIERE lui : on compare son regard a la direction d'ou l'on vient.
      return Math.abs(ecartAngle(c.angle, angleVers(c.x, c.y, j.x, j.y))) > Math.PI - dos;
    });
    const victime = victimes[0];
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

  function cycler(e) {
    const ordre = B.defs.ordre_armes || ['poings'];
    const possedees = ordre.filter(function (s) { return B.partie.armes[s]; });
    if (possedees.length < 2) return;
    const i = possedees.indexOf(e.arme);
    e.arme = possedees[(i + 1) % possedees.length];
    B.partie.arme = e.arme;
    Son.SFX.menu();
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

  function maj() {
    const j = B.joueur;
    majProjectiles();
    for (const e of B.entites) {
      if (e.etat === 'attaque') { majAttaque(e); majJet(e); }
      if (e.aveugle > 0) e.aveugle--;
    }
    if (!j || j.dansVehicule || !j.vivant) return;

    if (Entree.neuf('esquive')) roulade(j);
    if (Entree.neuf('arme')) cycler(j);

    // Coup fort : on MAINTIENT la frappe, on relache quand c'est charge.
    const arme = armeCourante();
    if (Entree.bas('attaque') && arme.type === 'melee') {
      j.charge++;
    } else if (j.charge > 0) {
      frapper(j, j.charge >= CHARGE_MIN);
      j.charge = 0;
    } else if (Entree.neuf('attaque')) {
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
      if (B.interieur) {
        if (Missions.utiliserPoint(j)) return;
        if (Monde.porteDevant(j)) { Jeu.sortir(); return; }
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
        if (porte) { if (!Missions.acheterPropriete(porte)) Jeu.entrer(porte); }
        else pickpocket(j);
      }
    }
  }

  return {
    CHARGE_MIN, ROULADE_IMAGES, armeDef, armeCourante, munitions, possede,
    frapper, tirer, cycler, roulade, pickpocket, ramasserArme, objetSousLaMain,
    viseeAssistee, majAttaque, majProjectiles, maj,
  };
})();
