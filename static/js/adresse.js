/* Bandini — les épreuves d'adresse : les défis qu'on joue DEBOUT, dessinés
   par-dessus la ville (les dix-huit défis, 1re vague, 23 sept. 2026).

   Martin : « je veux tout ça sur la carte, on doit les voir selon s'il est
   possible de les faire avec les doigts ou avec la manette ou le clavier ».
   Une épreuve est un défi comme les autres (`missions.DEFIS`, `epreuve` et
   `regles`) : un panneau ou un comptoir, un chrono, une prime — `Histoire`
   la commence, la finit et la paie. Ce module ne fait que la JOUER : lire les
   boutons, compter, dessiner.

   ⚠️ **LE MÊME AXE QUE LE PIRATAGE** (`Entree.axe` : clavier, manette, stick
   tactile) et la même lecture en crans (`Combat.creneauVise`) : rien de neuf à
   apprendre au pouce. `B.epreuve` cloue le joueur (`Entites.majJoueur`) et
   affame le combat, la roue d'armes, l'entrée en char et le décor — les mêmes
   portes que `B.piratage`.

   ⚠️ **ESQUIVE (ou RETOUR) ABANDONNE**, et aucune épreuve ne s'en sert : c'est
   le seul bouton qui reste libre sur les trois appareils (COURS au doigt, B à
   la manette, MAJ au clavier).

   ⚠️ **LES DOUZE PREMIÈRES IMAGES NE LISENT RIEN** : l'appui qui a choisi
   COMMENCER est encore « neuf » à l'image où l'épreuve s'ouvre — sans ça, la
   roue freinait avant qu'on l'ait vue tourner. */

const Adresse = (function () {
  'use strict';

  const PRET = 12;
  //: Les crans du stick, comme le piratage : 0 en HAUT, puis dans le sens des aiguilles.
  const DIRS = ['haut', 'droite', 'bas', 'gauche'];
  const SEUIL_HAUT = 0.45, SEUIL_BAS = 0.22;
  //: Le temps qu'on laisse lire « RATÉ » ou « UN ! » avant le coup suivant.
  const PAUSE = 30;
  //: Une case vide, un trou, une barre éteinte : lisible sur le fond de la boîte.
  const VIDE = '#3a3a48';

  function s(sec) { return Math.round(sec * 60); }
  function entre(a, b, k) { return a + (b - a) * Math.max(0, Math.min(1, k)); }
  function hasard() { return B.rng(); }

  /** Un flick NEUF du stick : sa direction, une fois par poussée, ou null. */
  function flick(e) {
    const mag = Entree.axe.mag;
    if (e.relache && mag > SEUIL_HAUT) {
      e.relache = false;
      const cran = Combat.creneauVise(Entree.axe, DIRS.length);
      return cran >= 0 ? DIRS[cran] : null;
    }
    if (mag < SEUIL_BAS) e.relache = true;
    return null;
  }

  /** L'angle du stick en degrés, 0 en haut, dans le sens des aiguilles. */
  function angleDuStick() {
    const a = Entree.axe;
    return ((Math.atan2(a.x, -a.y) * 180 / Math.PI) + 360) % 360;
  }

  function ecartAngle(a, b) {
    const d = Math.abs(a - b) % 360;
    return d > 180 ? 360 - d : d;
  }

  // --- Les épreuves ---------------------------------------------------------------------
  //
  // Chacune : `init(r)` rend son état, `maj(e, r)` avance d'une image et rend
  // `{ gagne, raison }` quand c'est fini, `compte(e, r)` la ligne du HUD,
  // `dessiner(ctx, e, r, x, y)` son dessin dans la boîte.

  /** Une goupille neuve : un angle ENTRE deux des huit directions (`decalage_deg`
      d'une diagonale), à `jeu_deg` près. ⚠️ C'est ce qui exclut le clavier, et
      le catalogue l'écrit : ses huit directions tombent toujours à plus de
      `decalage_deg - jeu_deg` de la goupille, bien au-delà de `tolerance_deg`. */
  function goupille(r) {
    return (Math.floor(hasard() * 8) * 45 + r.decalage_deg + (hasard() * 2 - 1) * r.jeu_deg + 360) % 360;
  }

  /** Une image de crochetage : rend vrai quand la goupille tombe. */
  function majGoupille(e, r) {
    const a = Entree.axe;
    e.proche = 0;
    if (a.mag < r.force) { e.tenu = 0; return false; }
    const ecart = ecartAngle(angleDuStick(), e.cible);
    e.proche = Math.max(0, 1 - ecart / r.proche_deg);
    // ⚠️ La manette VIBRE plus fort à mesure qu'on approche : c'est l'oreille
    // du crocheteur. Au doigt, le cadenas tremble à l'écran (même mesure).
    if (e.proche > 0.3 && e.t % 10 === 0) Entree.vibrer(Math.round(10 + 50 * e.proche));
    if (ecart <= r.tolerance_deg) e.tenu++;
    else e.tenu = 0;
    if (e.tenu >= s(r.tenir_s)) {
      e.tenu = 0;
      e.cible = goupille(r);
      Son.SFX.ramasse();
      return true;
    }
    return false;
  }

  const EPREUVES = {

    // LA ROUE : elle tourne à vitesse fixe ; ACTION la freine, et elle s'arrête
    // TOUJOURS `freinage_s` plus loin. On apprend quand appuyer, pas où.
    roue: {
      init: function (r) { return { angle: hasard() * r.secteurs, freine: -1, v0: 0, lot: Math.floor(hasard() * r.secteurs), essais: r.essais, pause: 0, dit: '' }; },
      maj: function (e, r) {
        const v = r.secteurs * r.tours_par_s / 60, F = s(r.freinage_s);
        if (e.pause > 0) {
          if (--e.pause === 0) { e.freine = -1; e.lot = Math.floor(hasard() * r.secteurs); e.dit = ''; }
          return null;
        }
        if (e.freine < 0) {
          e.angle = (e.angle + v) % r.secteurs;
          if (Entree.neuf('action')) { e.freine = 0; Son.SFX.menu(); }
          return null;
        }
        e.freine++;
        e.angle = (e.angle + v * Math.max(0, 1 - e.freine / F)) % r.secteurs;
        if (e.freine < F) return null;
        if (Math.floor(e.angle) === e.lot) { e.dit = 'GROS LOT !'; return { gagne: true }; }
        e.essais--;
        Son.SFX.erreur();
        if (e.essais <= 0) return { gagne: false, raison: 'LA ROUE A GAGNÉ' };
        e.dit = 'PERDU — ENCORE ' + e.essais; e.pause = PAUSE * 2;
        return null;
      },
      compte: function (e) { return 'ESSAIS ' + e.essais; },
      dessiner: function (ctx, e, r, x, y) {
        const cx = x + 100, cy = y + 38, R = 26, n = r.secteurs;
        for (let k = 0; k < n; k++) {
          // ⚠️ Le secteur `k` passe sous l'aiguille (en haut) quand `angle` vaut k.
          const a0 = (k - e.angle) / n * Math.PI * 2 - Math.PI / 2;
          ctx.fillStyle = k === e.lot ? '#e8b33c' : (k % 2 ? '#c4362f' : '#efe6d0');
          ctx.beginPath(); ctx.moveTo(cx, cy); ctx.arc(cx, cy, R, a0, a0 + Math.PI * 2 / n); ctx.closePath(); ctx.fill();
        }
        ctx.fillStyle = '#101018'; ctx.fillRect(cx - 2, cy - 2, 4, 4);
        ctx.fillStyle = '#6fe3ff'; ctx.fillRect(cx - 1, cy - R - 6, 3, 8);
        if (e.dit) ecrire(ctx, e.dit, cx, y + 70, e.dit === 'GROS LOT !' ? '#8fd46a' : '#ff8a7a');
      },
    },

    // LES ANNEAUX : tenir ACTION charge (la force monte et redescend), lâcher
    // dans la bande verte. La bande bouge à chaque anneau.
    anneaux: {
      init: function (r) { return { lances: 0, reussis: 0, charge: 0, sens: 1, tient: false, attendLacher: true, centre: 0.6, pause: 0, dit: '' }; },
      maj: function (e, r) {
        if (e.pause > 0) { e.pause--; return null; }
        const bas = Entree.bas('action');
        if (e.attendLacher) { if (!bas) e.attendLacher = false; return null; }
        if (bas) {
          if (!e.tient) { e.tient = true; e.charge = 0; e.sens = 1; }
          e.charge += e.sens / s(r.charge_s);
          if (e.charge >= 1) { e.charge = 1; e.sens = -1; }
          if (e.charge <= 0) { e.charge = 0; e.sens = 1; }
          return null;
        }
        if (!e.tient) return null;
        e.tient = false; e.lances++;
        const bon = Math.abs(e.charge - e.centre) <= r.bande / 2;
        if (bon) { e.reussis++; e.dit = 'SUR LA BOUTEILLE !'; Son.SFX.ramasse(); }
        else { e.dit = e.charge < e.centre ? 'TROP COURT' : 'TROP LOIN'; Son.SFX.erreur(); }
        e.centre = 0.3 + hasard() * 0.55; e.pause = PAUSE;
        if (e.reussis >= r.reussis) return { gagne: true };
        if (r.anneaux - e.lances < r.reussis - e.reussis) return { gagne: false, raison: 'PLUS D\'ANNEAUX' };
        return null;
      },
      compte: function (e, r) { return 'ANNEAUX ' + e.reussis + '/' + r.reussis + ' · LANCÉS ' + e.lances + '/' + r.anneaux; },
      dessiner: function (ctx, e, r, x, y) {
        const bx = x + 60, by = y + 12, l = 80, h = 10;
        ctx.fillStyle = VIDE; ctx.fillRect(bx, by, l, h);
        ctx.fillStyle = '#2f6b2a'; ctx.fillRect(bx + Math.round((e.centre - r.bande / 2) * l), by, Math.round(r.bande * l), h);
        ctx.fillStyle = '#efe6d0'; ctx.fillRect(bx + Math.round(e.charge * l) - 1, by - 2, 2, h + 4);
        ecrire(ctx, e.tient ? 'LÂCHE DANS LE VERT' : 'TIENS ACTION', x + 100, y + 30, '#cdc6e6');
        if (e.dit) ecrire(ctx, e.dit, x + 100, y + 48, e.dit === 'SUR LA BOUTEILLE !' ? '#8fd46a' : '#ff8a7a');
      },
    },

    // LES RATONS : un raton sort d'un des trois trous ; on pousse vers le sien
    // avant qu'il rentre. De plus en plus vite.
    ratons: {
      init: function (r) { return { trou: -1, reste: 0, pause: s(0.5), coups: 0, rates: 0, relache: true, dit: '' }; },
      maj: function (e, r) {
        const dir = flick(e);
        if (e.trou < 0) {
          if (--e.pause <= 0) {
            e.trou = Math.floor(hasard() * r.trous.length);
            e.reste = s(entre(r.fenetre_s[0], r.fenetre_s[1], e.coups / r.coups));
            e.dit = '';
          }
          return null;
        }
        let rate = false;
        if (dir === r.trous[e.trou]) {
          e.coups++; e.dit = 'POC !'; Son.SFX.maillet();
          e.trou = -1; e.pause = s(r.pause_s);
          if (e.coups >= r.coups) return { gagne: true };
          return null;
        }
        if (dir) { rate = true; e.dit = 'PAS CE TROU-LÀ'; }
        else if (--e.reste <= 0) { rate = true; e.dit = 'IL EST RENTRÉ'; }
        if (rate) {
          e.rates++; Son.SFX.erreur();
          e.trou = -1; e.pause = s(r.pause_s);
          if (e.rates >= r.rates) return { gagne: false, raison: 'TROP DE RATONS' };
        }
        return null;
      },
      compte: function (e, r) { return 'COUPS ' + e.coups + '/' + r.coups + ' · RATÉS ' + e.rates + '/' + r.rates; },
      dessiner: function (ctx, e, r, x, y) {
        const places = { gauche: [x + 60, y + 34], haut: [x + 100, y + 14], droite: [x + 140, y + 34] };
        r.trous.forEach(function (t, i) {
          const p = places[t];
          ctx.fillStyle = '#101018'; ctx.fillRect(p[0] - 9, p[1] + 2, 18, 6);
          if (e.trou === i) {
            ctx.fillStyle = '#8a8698'; ctx.fillRect(p[0] - 6, p[1] - 8, 12, 11);
            ctx.fillStyle = VIDE; ctx.fillRect(p[0] - 6, p[1] - 5, 12, 3);
            ctx.fillStyle = '#efe6d0'; ctx.fillRect(p[0] - 4, p[1] - 5, 2, 2); ctx.fillRect(p[0] + 2, p[1] - 5, 2, 2);
          }
          ecrire(ctx, t.toUpperCase(), p[0], p[1] + 11, '#5a5a6a');
        });
        if (e.dit) ecrire(ctx, e.dit, x + 100, y + 60, e.dit === 'POC !' ? '#8fd46a' : '#ff8a7a');
      },
    },

    // LA DANSE : Marcel crie, on danse. Une direction ou FRAPPE, de plus en plus vite.
    danse: {
      init: function (r) { return { appel: null, reste: 0, pause: s(0.6), pas: 0, erreurs: 0, relache: true, dit: '' }; },
      maj: function (e, r) {
        const dir = flick(e), frappe = Entree.neuf('attaque');
        if (!e.appel) {
          if (--e.pause <= 0) {
            let a = e.dernier;
            while (a === e.dernier) a = r.appels[Math.floor(hasard() * r.appels.length)];
            e.appel = a; e.dernier = a; e.dit = '';
            e.reste = s(entre(r.fenetre_s[0], r.fenetre_s[1], e.pas / r.pas));
          }
          return null;
        }
        const geste = frappe ? 'attaque' : dir;
        let faux = false;
        if (geste === e.appel) {
          e.pas++; e.dit = 'OLÉ !'; Son.SFX.menu();
          e.appel = null; e.pause = PAUSE / 2;
          return e.pas >= r.pas ? { gagne: true } : null;
        }
        if (geste) { faux = true; e.dit = 'FAUX PAS'; }
        else if (--e.reste <= 0) { faux = true; e.dit = 'TROP TARD'; }
        if (faux) {
          e.erreurs++; Son.SFX.erreur();
          e.appel = null; e.pause = PAUSE;
          if (e.erreurs > r.erreurs) return { gagne: false, raison: 'MARCEL S\'EST TANNÉ' };
        }
        return null;
      },
      compte: function (e, r) { return 'PAS ' + e.pas + '/' + r.pas + ' · FAUX PAS ' + e.erreurs + '/' + r.erreurs; },
      dessiner: function (ctx, e, r, x, y) {
        const mots = { haut: 'HAUT !', bas: 'BAS !', gauche: 'GAUCHE !', droite: 'DROITE !', attaque: 'FRAPPE !' };
        if (e.appel) {
          ecrire(ctx, mots[e.appel], x + 100, y + 16, '#e8b33c', 2);
          const tot = s(entre(r.fenetre_s[0], r.fenetre_s[1], e.pas / r.pas));
          ctx.fillStyle = VIDE; ctx.fillRect(x + 50, y + 40, 100, 4);
          ctx.fillStyle = '#e8b33c'; ctx.fillRect(x + 50, y + 40, Math.round(100 * e.reste / tot), 4);
        }
        if (e.dit) ecrire(ctx, e.dit, x + 100, y + 56, e.dit === 'OLÉ !' ? '#8fd46a' : '#ff8a7a');
      },
    },

    // LE MANNEQUIN : une aiguille va et vient ; ACTION quand elle est dans le
    // vert. Hors du vert, la clochette sonne.
    mannequin: {
      init: function (r) { return { phase: 0, centre: 0.5, reussis: 0, clochettes: 0, pause: 0, dit: '' }; },
      maj: function (e, r) {
        const periode = s(entre(r.periode_s[0], r.periode_s[1], e.reussis / r.reussis));
        e.phase += Math.PI * 2 / periode;
        if (e.pause > 0) { e.pause--; return null; }
        if (!Entree.neuf('action')) return null;
        if (Math.abs(aiguille(e) - e.centre) <= r.zone / 2) {
          e.reussis++; e.dit = 'LE PORTEFEUILLE !'; Son.SFX.ramasse();
          e.centre = 0.15 + hasard() * 0.7; e.pause = PAUSE / 2;
          return e.reussis >= r.reussis ? { gagne: true } : null;
        }
        e.clochettes++; e.dit = 'DRELIN !'; Son.SFX.cloche(); e.pause = PAUSE;
        return e.clochettes >= r.clochettes ? { gagne: false, raison: 'LA CLOCHETTE A SONNÉ' } : null;
      },
      compte: function (e, r) { return 'POCHES ' + e.reussis + '/' + r.reussis + ' · CLOCHETTES ' + e.clochettes + '/' + r.clochettes; },
      dessiner: function (ctx, e, r, x, y) {
        const bx = x + 30, by = y + 18, l = 140;
        ctx.fillStyle = VIDE; ctx.fillRect(bx, by, l, 8);
        ctx.fillStyle = '#2f6b2a'; ctx.fillRect(bx + Math.round((e.centre - r.zone / 2) * l), by, Math.round(r.zone * l), 8);
        ctx.fillStyle = '#efe6d0'; ctx.fillRect(bx + Math.round(aiguille(e) * l) - 1, by - 3, 2, 14);
        if (e.dit) ecrire(ctx, e.dit, x + 100, y + 40, e.dit === 'DRELIN !' ? '#ff8a7a' : '#8fd46a');
      },
    },

    // LA RADIO : gauche/droite promène l'aiguille ; on la tient sur la fréquence
    // jusqu'à ce que la voix sorte du grésillement. Trois stations.
    radio: {
      init: function (r) {
        const cibles = [];
        while (cibles.length < r.stations) {
          const f = 0.08 + hasard() * 0.84;
          if (Math.abs(f - 0.5) > 0.1 && cibles.every(function (c) { return Math.abs(c - f) > 0.15; })) cibles.push(f);
        }
        return { aiguille: 0.5, cibles: cibles, k: 0, tenu: 0, dit: '', pause: 0 };
      },
      maj: function (e, r) {
        if (e.pause > 0) { e.pause--; return null; }
        const x = Entree.axe.x;
        if (Math.abs(x) > 0.15) e.aiguille = Math.max(0, Math.min(1, e.aiguille + x * r.vitesse / 60));
        if (Math.abs(e.aiguille - e.cibles[e.k]) <= r.tolerance) e.tenu++;
        else e.tenu = 0;
        if (e.tenu < s(r.tenir_s)) return null;
        e.dit = BARRAGES[(e.k + Math.floor(hasard() * BARRAGES.length)) % BARRAGES.length];
        Son.SFX.menu();
        e.k++; e.tenu = 0; e.pause = PAUSE * 2;
        return e.k >= r.stations ? { gagne: true } : null;
      },
      compte: function (e, r) { return 'STATIONS ' + e.k + '/' + r.stations; },
      dessiner: function (ctx, e, r, x, y) {
        const bx = x + 20, by = y + 20, l = 160;
        ctx.fillStyle = '#2a2014'; ctx.fillRect(bx, by, l, 14);
        for (let k = 0; k <= 10; k++) { ctx.fillStyle = '#8a7a50'; ctx.fillRect(bx + Math.round(k * l / 10), by + 10, 1, 4); }
        ctx.fillStyle = '#ff5a4e'; ctx.fillRect(bx + Math.round(e.aiguille * l), by - 2, 2, 18);
        const cible = e.cibles[Math.min(e.k, e.cibles.length - 1)];
        const signal = Math.max(0, 1 - Math.abs(e.aiguille - cible) / 0.2);
        for (let k = 0; k < 10; k++) {
          ctx.fillStyle = k / 10 < signal ? '#8fd46a' : VIDE;
          ctx.fillRect(bx + 50 + k * 6, by + 20, 4, 6);
        }
        ecrire(ctx, (88 + e.aiguille * 20).toFixed(1) + ' MHZ', x + 100, by + 30, '#efe6d0');
        if (e.dit) ecrire(ctx, e.dit, x + 100, by + 42, '#6fe3ff');
      },
    },

    // LE MOTEUR : il tousse en cadence ; ACTION sur chaque toux, cinq de suite.
    moteur: {
      init: function () { return { suite: 0, pris: -1, dit: '' }; },
      maj: function (e, r) {
        const periode = s(r.cadence_s), marge = s(r.marge_s);
        const ph = e.t % periode, n = Math.floor(e.t / periode);
        // La toux de l'image : la plus proche, derrière ou devant.
        const toux = ph <= periode / 2 ? n : n + 1, ecart = Math.min(ph, periode - ph);
        if (ph === 0) Son.SFX.choc();
        // Une toux passée sans appui casse la cadence.
        if (ph === marge + 1 && e.pris !== n && e.suite > 0) { e.suite = 0; e.dit = 'IL CALE'; }
        if (!Entree.neuf('action')) return null;
        if (ecart <= marge && e.pris !== toux) {
          e.pris = toux; e.suite++; e.dit = e.suite >= r.toux ? 'IL PART !' : 'VROUM';
          return e.suite >= r.toux ? { gagne: true } : null;
        }
        e.suite = 0; e.dit = 'À CONTRETEMPS'; Son.SFX.erreur();
        return null;
      },
      compte: function (e, r) { return 'TOUX ' + e.suite + '/' + r.toux; },
      dessiner: function (ctx, e, r, x, y) {
        const periode = s(r.cadence_s), ph = e.t % periode;
        const bat = Math.max(0, 1 - Math.min(ph, periode - ph) / (periode / 3));
        ctx.fillStyle = '#3a3a48'; ctx.fillRect(x + 80, y + 8, 40, 26);
        ctx.fillStyle = bat > 0.6 ? '#e8b33c' : '#5a4a2a'; ctx.fillRect(x + 84, y + 12, 32, 18);
        for (let k = 0; k < r.toux; k++) {
          ctx.fillStyle = k < e.suite ? '#8fd46a' : VIDE;
          ctx.fillRect(x + 100 - r.toux * 5 + k * 10, y + 40, 7, 5);
        }
        if (e.dit) ecrire(ctx, e.dit, x + 100, y + 52, e.dit === 'VROUM' || e.dit === 'IL PART !' ? '#8fd46a' : '#ff8a7a');
      },
    },

    // LE CADENAS : trois goupilles au stick. Tout près, il tremble.
    crochet: {
      init: function (r) { return { k: 0, cible: goupille(r), tenu: 0, proche: 0 }; },
      maj: function (e, r) {
        if (majGoupille(e, r)) { e.k++; if (e.k >= r.goupilles) return { gagne: true }; }
        return null;
      },
      compte: function (e, r) { return 'GOUPILLES ' + e.k + '/' + r.goupilles; },
      dessiner: function (ctx, e, r, x, y) { dessinerCadenas(ctx, e, r, x, y); },
    },

    // LE COFFRE : le code (quatre directions), puis deux goupilles au stick.
    coffre: {
      init: function (r) {
        const code = [];
        for (let i = 0; i < r.sequence; i++) code.push(DIRS[Math.floor(hasard() * DIRS.length)]);
        return { code: code, pos: 0, erreurs: 0, relache: true, k: 0, cible: goupille(r), tenu: 0, proche: 0 };
      },
      maj: function (e, r) {
        if (e.pos < e.code.length) {
          const dir = flick(e);
          if (!dir) return null;
          if (dir === e.code[e.pos]) { e.pos++; Son.SFX.menu(); return null; }
          e.pos = 0; e.erreurs++; Son.SFX.erreur();
          return e.erreurs > r.erreurs ? { gagne: false, raison: 'L\'ALARME' } : null;
        }
        if (majGoupille(e, r)) { e.k++; if (e.k >= r.goupilles) return { gagne: true }; }
        return null;
      },
      compte: function (e, r) {
        return e.pos < e.code.length ? 'CODE ' + e.pos + '/' + e.code.length + ' · ERREURS ' + e.erreurs + '/' + r.erreurs
          : 'GOUPILLES ' + e.k + '/' + r.goupilles;
      },
      dessiner: function (ctx, e, r, x, y) {
        if (e.pos >= e.code.length) { dessinerCadenas(ctx, e, r, x, y); return; }
        const lettre = { haut: 'H', bas: 'B', gauche: 'G', droite: 'D' }, pas = 16;
        const x0 = x + 100 - e.code.length * pas / 2;
        e.code.forEach(function (d, i) {
          const fait = i < e.pos, enCours = i === e.pos;
          ctx.fillStyle = fait ? '#1e3a1e' : (enCours ? '#4a3a10' : VIDE);
          ctx.fillRect(x0 + i * pas, y + 20, pas - 3, 12);
          ecrire(ctx, lettre[d], x0 + i * pas + (pas - 3) / 2, y + 22, fait ? '#8fd46a' : (enCours ? '#e8b33c' : '#5a5a6a'));
        });
      },
    },
  };

  //: Ce que la radio de la police laisse entendre, une station à la fois.
  const BARRAGES = ['BARRAGE SUR LE PONT', 'UNE AUTO AU TERMINUS', 'ON SURVEILLE LES QUAIS',
                    'PATROUILLE AUX ÉRABLES', 'RIEN À LA POINTE', 'LE SERGENT EST AU CASSE-CROÛTE'];

  function aiguille(e) { return 0.5 + 0.5 * Math.sin(e.phase); }

  function dessinerCadenas(ctx, e, r, x, y) {
    // ⚠️ Il TREMBLE tout près — la même mesure que la vibration de la manette.
    const dx = e.proche > 0.3 && (e.t >> 1) % 2 ? Math.round(e.proche * 2) : 0;
    const cx = x + 100 + dx, cy = y + 30;
    ctx.fillStyle = '#8a8698'; ctx.fillRect(cx - 8, cy - 16, 16, 4); ctx.fillRect(cx - 8, cy - 14, 3, 8); ctx.fillRect(cx + 5, cy - 14, 3, 8);
    ctx.fillStyle = '#c9a23c'; ctx.fillRect(cx - 12, cy - 6, 24, 20);
    ctx.fillStyle = '#101018'; ctx.fillRect(cx - 1, cy + 1, 3, 7);
    for (let k = 0; k < r.goupilles; k++) {
      ctx.fillStyle = k < e.k ? '#8fd46a' : (k === e.k && e.tenu > 0 ? '#e8b33c' : VIDE);
      ctx.fillRect(cx - r.goupilles * 5 + k * 10, cy + 18, 7, 5);
    }
    if (e.tenu > 0) {
      ctx.fillStyle = '#e8b33c';
      ctx.fillRect(cx - 12, cy + 25, Math.round(24 * e.tenu / s(r.tenir_s)), 2);
    }
  }

  /** Une ligne centrée, avec l'ombre du HUD. */
  function ecrire(ctx, t, cx, y, couleur, echelle) {
    const k = echelle || 1, x = Math.round(cx - Atlas.largeurTexte(t, k) / 2);
    Atlas.texte(ctx, t, x + 1, y + 1, 'rgba(11,10,18,0.8)', k);
    Atlas.texte(ctx, t, x, y, couleur, k);
  }

  // --- Le cycle -------------------------------------------------------------------------

  /** Ouvre l'épreuve du défi `d` (appelé par `Histoire.commencerDefi`). */
  function commencer(d) {
    const sorte = EPREUVES[d.epreuve];
    if (!sorte) return false;
    B.epreuve = Object.assign(sorte.init(d.regles), { slug: d.slug, sorte: d.epreuve, t: 0 });
    Entree.contexte('epreuve');
    return true;
  }

  /** Referme l'épreuve et rend les boutons à ce qu'ils faisaient (comme le piratage). */
  function fermer() {
    if (!B.epreuve) return;
    B.epreuve = null;
    Entree.contexte(B.joueur && B.joueur.dansVehicule ? 'vehicule' : 'pied');
  }

  /** Une image de l'épreuve du défi `d` : `{ gagne, raison }` quand c'est fini. */
  function maj(d) {
    const e = B.epreuve;
    if (!e || e.slug !== d.slug) return null;
    e.t++;
    if (e.t <= PRET) return null;
    if (Entree.neuf('esquive') || Entree.neuf('annuler')) return { gagne: false, raison: 'ABANDONNÉ' };
    return EPREUVES[e.sorte].maj(e, d.regles);
  }

  function compte(d) {
    const e = B.epreuve;
    return e && e.slug === d.slug ? EPREUVES[e.sorte].compte(e, d.regles) : '';
  }

  //: La boîte : SOUS le joueur (la caméra le tient au milieu de l'écran) — au
  //: milieu, elle le cachait, et on ne voyait plus devant quel comptoir on jouait.
  //: Les dessins des épreuves tiennent sur 200 px ; la boîte est plus large pour
  //: la consigne.
  const BOITE = { l: 250, h: 98, y: 148 };

  /** Le dessin de l'épreuve en cours, par-dessus la ville (depuis `Hud`). */
  function dessiner(ctx) {
    const e = B.epreuve;
    if (!e) return;
    const d = (B.defs.defis || []).find(function (q) { return q.slug === e.slug; });
    if (!d) return;
    const x = Math.round((VW - BOITE.l) / 2), y = BOITE.y, cx = x + BOITE.l / 2;
    ctx.fillStyle = 'rgba(11,10,18,0.84)'; ctx.fillRect(x, y, BOITE.l, BOITE.h);
    ctx.fillStyle = '#e8b33c'; ctx.fillRect(x, y, BOITE.l, 1);
    B.stats.rects += 2;
    if (e.t <= PRET) ecrire(ctx, 'PRÊT ?', cx, y + 30, '#e8b33c', 2);
    else EPREUVES[e.sorte].dessiner(ctx, e, d.regles, cx - 100, y + 4);
    ecrire(ctx, d.consigne || '', cx, y + BOITE.h - 20, '#cdc6e6');
    ecrire(ctx, 'ESQUIVE : ABANDONNER', cx, y + BOITE.h - 10, '#5a5a6a');
  }

  return { commencer, fermer, maj, compte, dessiner, EPREUVES, PRET, angleDuStick };
})();
