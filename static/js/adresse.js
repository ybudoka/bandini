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
    // LA TIRE SUR LA NEIGE (la cabane a sucre, docs/jalons/la-cabane-a-sucre.md) : le sirop coule sur la
    // neige et refroidit ; on l'enroule sur le baton quand il est A POINT (ACTION dans le vert). Trop tot,
    // elle coule ; trop tard, elle casse. Chaque palette refroidit plus vite. ⚠️ Le point change a chaque
    // palette, a l'empreinte du compte — jamais `B.rng()`.
    tire: {
      init: function (r) { return { temp: 1, centre: 0.45, reussis: 0, rates: 0, pause: 0, dit: '' }; },
      maj: function (e, r) {
        if (e.pause > 0) { e.pause--; return null; }
        const rater = function (dit) {
          e.rates++; e.dit = dit; Son.SFX.erreur(); e.pause = PAUSE; e.temp = 1;
          return e.rates >= r.rates ? { gagne: false, raison: 'LA TIRE EST RATÉE' } : null;
        };
        e.temp -= (1 + e.reussis * r.acceleration) / s(r.refroidit_s);
        if (e.temp <= 0) return rater('ELLE A CASSÉ');
        if (!Entree.neuf('action')) return null;
        if (Math.abs(e.temp - e.centre) <= r.zone / 2) {
          e.reussis++; e.dit = 'SUR LE BÂTON!'; Son.SFX.ramasse(); e.pause = PAUSE / 2; e.temp = 1;
          e.centre = 0.3 + ((e.reussis * 37 + e.rates * 11) % 40) / 100;
          return e.reussis >= r.reussis ? { gagne: true } : null;
        }
        return rater(e.temp > e.centre ? 'TROP CHAUDE, ELLE COULE' : 'TROP FROIDE, ELLE CASSE');
      },
      compte: function (e, r) { return 'PALETTES ' + e.reussis + '/' + r.reussis + ' · RATÉES ' + e.rates + '/' + r.rates; },
      dessiner: function (ctx, e, r, x, y) {
        // La neige, et la tire dessus : doree quand elle est chaude, brune quand elle prend.
        const bx = x + 30, by = y + 12, l = 140;
        ctx.fillStyle = '#eef3f8'; ctx.fillRect(bx, by, l, 12);
        const t = Math.max(0, e.temp);
        ctx.fillStyle = 'rgb(' + Math.round(150 + 90 * t) + ',' + Math.round(80 + 90 * t) + ',' + Math.round(20 + 40 * t) + ')';
        ctx.fillRect(bx + 10, by + 5, Math.round((l - 20) * (0.4 + 0.6 * (1 - t))), 3);
        // Le thermometre : froid a gauche, chaud a droite, le vert la ou elle est a point.
        const ty = by + 18;
        ctx.fillStyle = VIDE; ctx.fillRect(bx, ty, l, 6);
        ctx.fillStyle = '#2f6b2a'; ctx.fillRect(bx + Math.round((e.centre - r.zone / 2) * l), ty, Math.round(r.zone * l), 6);
        ctx.fillStyle = '#ff8a3a'; ctx.fillRect(bx + Math.round(t * l) - 1, ty - 3, 2, 12);
        if (e.dit) ecrire(ctx, e.dit, x + 100, y + 44, e.dit === 'SUR LE BÂTON!' ? '#8fd46a' : '#ff8a7a');
      },
    },

    // LA LIGUE DU MARDI (la salle de quilles, docs/jalons/les-enseignes-qui-ouvrent-pour-vrai.md) : cinq
    // carreaux, une boule chacun. ACTION arrete la VISEE (la boule va et vient d'un dalot a l'autre), puis
    // la FORCE (la jauge monte et redescend). ⚠️ Les quilles qui tombent se CALCULENT (`quillesTombees`) :
    // l'ecart au milieu de l'allee en abat moins, une boule molle en abat moins. Jamais `B.rng()`.
    quilles: {
      init: function (r) { return { carreau: 0, total: 0, phase: 'vise', u: 0, vise: 0, force: 0, pause: 0, dit: '', derniere: -1 }; },
      maj: function (e, r) {
        if (e.pause > 0) {
          if (--e.pause > 0) return null;
          if (e.carreau >= r.carreaux) {
            return e.total >= r.objectif ? { gagne: true }
              : { gagne: false, raison: e.total + ' QUILLES — IL EN FALLAIT ' + r.objectif };
          }
          e.phase = 'vise'; e.u = 0; e.vise = 0; e.force = 0; e.derniere = -1; e.dit = '';
          return null;
        }
        e.u++;
        if (e.phase === 'vise') {
          // D'un dalot a l'autre et retour, en `vise_s` par traversee : elle PART du dalot.
          e.vise = 0.5 - 0.5 * Math.cos(e.u * Math.PI / s(r.vise_s));
          if (Entree.neuf('action')) { e.phase = 'force'; e.u = 0; }
          return null;
        }
        e.force = 0.5 - 0.5 * Math.cos(e.u * Math.PI / s(r.force_s));
        if (!Entree.neuf('action')) return null;
        const n = quillesTombees(e.vise, e.force, r);
        e.total += n; e.carreau++; e.derniere = n;
        e.dit = n === 10 ? 'ABAT!' : (n === 0 ? 'DANS LE DALOT' : n + (n > 1 ? ' QUILLES' : ' QUILLE'));
        Son.SFX.quilles(n);
        e.pause = PAUSE * 2;
        return null;
      },
      compte: function (e, r) { return 'CARREAU ' + Math.min(r.carreaux, e.carreau + 1) + '/' + r.carreaux + ' · ' + e.total + '/' + r.objectif + ' QUILLES'; },
      dessiner: function (ctx, e, r, x, y) {
        // L'allee, de cote : la boule a gauche, les dix quilles en triangle au bout, a droite.
        const bx = x + 20, by = y + 8, l = 160, h = 26;
        ctx.fillStyle = '#2a2230'; ctx.fillRect(bx, by - 3, l, h + 6);            // les dalots
        ctx.fillStyle = '#c99a5b'; ctx.fillRect(bx, by, l, h);                      // l'erable verni
        ctx.fillStyle = '#b5874b'; for (let k = 6; k < l; k += 12) ctx.fillRect(bx + k, by, 1, h);
        ctx.fillStyle = '#8a5a2a'; for (let k = 0; k < 5; k++) ctx.fillRect(bx + 44, by + 4 + k * 4, 2, 2);   // les fleches de visee
        const tombees = e.derniere < 0 ? 0 : e.derniere;
        let k = 0;
        for (let rang = 0; rang < 4; rang++) {
          for (let j = 0; j <= rang; j++, k++) {
            const qx = bx + l - 30 + rang * 6, qy = by + h / 2 + (j - rang / 2) * 6;
            ctx.fillStyle = k < tombees ? '#6a5a50' : '#f4f1e8';
            ctx.fillRect(Math.round(qx), Math.round(qy) - 1, k < tombees ? 3 : 2, k < tombees ? 2 : 3);
            if (k >= tombees) { ctx.fillStyle = '#c0392b'; ctx.fillRect(Math.round(qx), Math.round(qy) - 1, 2, 1); }
          }
        }
        // La boule : sur la ligne de faute pendant la visee, lancee apres.
        const boule = e.phase === 'vise' || e.pause === 0 ? 0 : 1 - e.pause / (PAUSE * 2);
        ctx.fillStyle = '#1f3a6b';
        ctx.fillRect(Math.round(bx + 6 + boule * (l - 44)), Math.round(by + 2 + e.vise * (h - 8)), 5, 5);
        // La jauge de force.
        ctx.fillStyle = VIDE; ctx.fillRect(bx, by + h + 8, l, 5);
        if (e.phase === 'force' || e.pause > 0) {
          ctx.fillStyle = e.force < r.force_min ? '#ff8a3a' : '#8fd46a';
          ctx.fillRect(bx, by + h + 8, Math.round(l * e.force), 5);
        }
        ctx.fillStyle = '#efe6d0'; ctx.fillRect(bx + Math.round(l * r.force_min), by + h + 7, 1, 7);
        ecrire(ctx, e.phase === 'vise' && !e.pause ? 'VISE' : 'FORCE', bx - 12, by + h + 7, '#cdc6e6');
        if (e.dit) ecrire(ctx, e.dit, x + 100, y + 52, e.dit === 'ABAT!' ? '#8fd46a' : '#e8b33c');
      },
    },

    // LE BINGO DU SOUS-SOL (docs/jalons/les-enseignes-qui-ouvrent-pour-vrai.md) : ta carte, et une boule
    // toutes les `appel_s` secondes. ACTION la marque, si elle est sur ta carte, pendant `fenetre_s` ;
    // les madames, elles, ne ratent rien — et c'est a la fin de la fenetre qu'elles crient. La premiere
    // ligne pleine (rangee, colonne ou diagonale) gagne. ⚠️ Les cartes et l'ordre des boules sortent d'un
    // generateur a la graine de la carte (`regles.graine`, `Enseignes`) : jamais `B.rng()`.
    bingo: {
      init: function (r) {
        const alea = mulberry(r.graine >>> 0);
        const carte = function () {
          const c = [];
          for (let col = 0; col < 5; col++) {
            const pris = [];
            while (pris.length < 5) {
              const n = col * 15 + 1 + Math.floor(alea() * 15);
              if (pris.indexOf(n) < 0) pris.push(n);
            }
            for (let rang = 0; rang < 5; rang++) c[rang * 5 + col] = pris[rang];
          }
          c[12] = 0;                                                  // la case gratuite
          return c;
        };
        const joueur = carte(), madames = [];
        for (let k = 0; k < r.madames; k++) madames.push(carte());
        const ordre = [];
        for (let n = 1; n <= 75; n++) ordre.push(n);
        for (let i = 74; i > 0; i--) { const j = Math.floor(alea() * (i + 1)), t = ordre[i]; ordre[i] = ordre[j]; ordre[j] = t; }
        return { carte: joueur, marques: joueur.map(function (n) { return n === 0; }), madames: madames, ordre: ordre,
                 k: -1, attente: 0, fenetre: 0, dit: '' };
      },
      maj: function (e, r) {
        if (e.fenetre > 0 && --e.fenetre === 0) {
          // La fenetre se ferme : une madame qui a sa ligne CRIE.
          const tirees = e.ordre.slice(0, e.k + 1);
          if (e.madames.some(function (m) { return ligneBingo(m, function (i) { return m[i] === 0 || tirees.indexOf(m[i]) >= 0; }); })) {
            return { gagne: false, raison: 'BINGO! — UNE MADAME DU FOND' };
          }
        }
        if (--e.attente <= 0) {
          if (e.k >= 74) return { gagne: false, raison: 'PLUS DE BOULES' };
          e.k++; e.attente = s(r.appel_s); e.fenetre = s(r.fenetre_s);
          const b = e.ordre[e.k];
          e.dit = lettreBingo(b) + '-' + b;
          Son.SFX.boule();
        }
        if (!Entree.neuf('action')) return null;
        const i = e.carte.indexOf(e.ordre[e.k]);
        if (e.fenetre > 0 && i >= 0 && !e.marques[i]) {
          e.marques[i] = true; Son.SFX.ramasse();
          if (ligneBingo(e.carte, function (q) { return e.marques[q]; })) return { gagne: true };
        } else Son.SFX.erreur();
        return null;
      },
      compte: function (e, r) { return e.k < 0 ? 'LE BOULIER TOURNE' : 'BOULE ' + (e.k + 1) + ' · ' + e.dit; },
      dessiner: function (ctx, e, r, x, y) {
        // La carte, a gauche : le bandeau rouge B I N G O en double, et les cases marquees au crayon rouge.
        // ⚠️ Sur une case creme, le chiffre s'ecrit SANS l'ombre du HUD (`net`) : decalee d'un pixel, elle
        // bavait sous le trait sombre et « 30 », « 38 » se lisaient comme des paves.
        const c = 15, gx = x + 8, gy = y + 14;
        ctx.fillStyle = '#c0392b'; ctx.fillRect(gx, gy - 13, 5 * c - 1, 12);
        'BINGO'.split('').forEach(function (l, col) { net(ctx, l, gx + col * c + (c - 1) / 2, gy - 12, '#efe6d0', 2); });
        for (let i = 0; i < 25; i++) {
          const cx = gx + (i % 5) * c, cy = gy + Math.floor(i / 5) * 11, n = e.carte[i];
          const appelee = n > 0 && n === e.ordre[e.k] && e.fenetre > 0;
          ctx.fillStyle = e.marques[i] ? '#6b1f1c' : (appelee ? '#e8b33c' : '#efe6d0');
          ctx.fillRect(cx, cy, c - 1, 10);
          if (n) net(ctx, String(n), cx + (c - 1) / 2, cy + 3, e.marques[i] ? '#ffd8c8' : '#1a1a22');
          else etoile(ctx, cx + (c - 1) / 2, cy + 5, '#ffd8c8');
        }
        // La boule qu'on crie, a droite, en gros : sa lettre dans le bandeau, son numero en triple.
        if (e.k >= 0) {
          const bx = x + 140, by = y + 26, n = e.ordre[e.k];
          ctx.fillStyle = '#efe6d0'; ctx.fillRect(bx - 16, by - 14, 32, 34);
          ctx.fillStyle = '#c0392b'; ctx.fillRect(bx - 16, by - 14, 32, 13);
          net(ctx, lettreBingo(n), bx, by - 12, '#efe6d0', 2);
          net(ctx, String(n), bx, by + 2, '#1a1a22', 3);
          ctx.fillStyle = '#e8b33c'; ctx.fillRect(bx - 16, by + 22, Math.round(32 * e.fenetre / s(r.fenetre_s)), 2);
        }
      },
    },

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

  /** Les quilles qu'abat une boule : `vise` (0 et 1, les dalots ; 0,5, la poche), `force` (0 a 1).
      Pure : la meme boule abat toujours autant de quilles. */
  function quillesTombees(vise, force, r) {
    let n = Math.round(10 - Math.abs(vise - 0.5) * r.abat);
    if (force < r.force_min) n = Math.round(n * force / r.force_min);
    return Math.max(0, Math.min(10, n));
  }

  //: Les lettres du bingo : B (1-15), I (16-30), N (31-45), G (46-60), O (61-75).
  function lettreBingo(n) { return 'BINGO'.charAt(Math.floor((n - 1) / 15)); }

  /** Une ligne pleine sur une carte (rangee, colonne ou diagonale) ? `pleine(i)` dit si la case i l'est. */
  function ligneBingo(carte, pleine) {
    for (let k = 0; k < 5; k++) {
      let rang = true, col = true;
      for (let j = 0; j < 5; j++) { rang = rang && pleine(k * 5 + j); col = col && pleine(j * 5 + k); }
      if (rang || col) return true;
    }
    let d1 = true, d2 = true;
    for (let j = 0; j < 5; j++) { d1 = d1 && pleine(j * 6); d2 = d2 && pleine(j * 4 + 4); }
    return d1 || d2;
  }

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

  /** Une ligne centrée SANS ombre : pour un trait sombre sur fond clair, ou l'ombre bave. */
  function net(ctx, t, cx, y, couleur, echelle) {
    Atlas.texte(ctx, t, Math.round(cx - Atlas.largeurTexte(t, echelle || 1) / 2), y, couleur, echelle);
  }

  //: La case gratuite du bingo : une etoile de 5 sur 5, centree sur (cx, cy).
  const ETOILE = ['00100', '00100', '11111', '01010', '10001'];
  function etoile(ctx, cx, cy, couleur) {
    ctx.fillStyle = couleur;
    ETOILE.forEach(function (rang, j) {
      for (let i = 0; i < 5; i++) if (rang[i] === '1') ctx.fillRect(Math.round(cx) - 2 + i, cy - 2 + j, 1, 1);
    });
  }

  // --- Le cycle -------------------------------------------------------------------------

  /** Ouvre l'épreuve du défi `d` (appelé par `Histoire.commencerDefi`). */
  function commencer(d) {
    const sorte = EPREUVES[d.epreuve];
    if (!sorte) return false;
    // ⚠️ `def` voyage avec l'epreuve : le bingo n'est pas un defi du catalogue (`Enseignes` le joue, avec
    // une fiche a lui), et le dessin la cherchait dans `B.defs.defis`.
    B.epreuve = Object.assign(sorte.init(d.regles), { slug: d.slug, sorte: d.epreuve, t: 0, def: d });
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
    const d = e.def || (B.defs.defis || []).find(function (q) { return q.slug === e.slug; });
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

  return { commencer, fermer, maj, compte, dessiner, EPREUVES, PRET, angleDuStick, quillesTombees, lettreBingo, ligneBingo };
})();
