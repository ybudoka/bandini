/* Bandini — HUD (canvas, hors nuit) et voiles DOM (titre, scores). */

const Hud = (function () {
  'use strict';

  let doc = null, racine = null, voiles = {}, urlScores = '';

  function init(d, r) {
    doc = d; racine = r;
    urlScores = r.dataset.urlScores;
    ['titre', 'scores', 'score-envoi'].forEach(function (n) { voiles[n] = d.getElementById('voile-' + n); });
    d.getElementById('bouton-jouer').addEventListener('click', function () { Son.reveiller(); Jeu.commencer(); });
    d.getElementById('bouton-scores').addEventListener('click', function () { Son.reveiller(); montrerScores(); });
    d.getElementById('bouton-fermer-scores').addEventListener('click', function () { voile('titre'); });
    d.getElementById('bouton-annuler-score').addEventListener('click', function () { voile(null); Jeu.reprendre(); });
    d.getElementById('score-form').addEventListener('submit', envoyerScore);
    avisSon = d.getElementById('avis-son');
    majAvisSon();
  }

  /** Le bandeau « touche l'ecran pour le son » de l'ecran titre. Il se montre
      des le chargement (le contexte naît suspendu) et disparaît au premier
      geste — c'est le seul moyen de savoir qu'on joue en silence. */
  let avisSon = null;
  function majAvisSon() {
    if (avisSon) avisSon.hidden = !Son.enAttente();
  }

  let voileCourant = null;
  function voile(nom) {
    voileCourant = nom;
    for (const n in voiles) voiles[n].hidden = (n !== nom);
  }

  function etat(nom) { if (racine) racine.dataset.etat = nom; }

  function message(texte, duree) { B.msg = texte; B.msgT = duree || 120; }

  // --- Menus canvas ---------------------------------------------------------------
  //: Un menu = { titre, items: [{ libelle, detail, actif, faire }], curseur, aide, sur, obligatoire }.
  //: `faire()` rend true pour fermer le menu, false pour le laisser ouvert
  //: (on achete trois hot-dogs sans rouvrir le comptoir).
  //: `refaire()` rend un menu NEUF : un menu qui reste ouvert se refait apres
  //: chaque achat (voir `rafraichirMenu`).

  let repetT = 0;

  /** Ouvrir un menu — SUR UNE LIGNE QU'ON PEUT CHOISIR.

      ⚠️ La moitie des comptoirs commencent par un en-tete qui se lit et ne se
      choisit pas (« LA DETTE », « TON DOSSIER », « PRIX DU JOUR ») : le curseur
      pose dessus, le menu n'a l'air d'avoir AUCUNE selection — la seule ligne
      surlignee est grise comme tout ce qui est hors de portee, et ACTION n'y
      repond qu'un bip. Martin l'a photographie chez les hommes de Sal. La regle
      existait pourtant : les OPTIONS la tenaient A LA MAIN (`curseur: 1`, leur
      premiere ligne etant un diagnostic) — mais chaque menu devait y penser
      tout seul, et cinq l'avaient oublie. Elle se tient donc ICI, une fois.
      ⚠️ Un menu qui SAIT ou il veut son curseur le dit (une fiche qui s'ouvre
      sur RETOUR, le JOURNAL qui s'ouvre en haut de sa liste et s'y promene) :
      un `curseur` donne ne se discute pas. Et un menu ou il n'y a rien a
      choisir (le BILAN) reste en haut, comme avant. */
  function ouvrirMenu(menu) {
    if (typeof menu.curseur !== 'number') {
      const i = (menu.items || []).findIndex(function (item) { return !!item.faire; });
      menu.curseur = i < 0 ? 0 : i;
    }
    B.menu = menu;
    Entree.contexte('menu');
    Son.SFX.menu();
  }

  function fermerMenu() {
    B.menu = null;
    Entree.contexte(B.joueur && B.joueur.dansVehicule ? 'vehicule' : 'pied');
  }

  /** Refaire le menu ouvert, apres un achat qui l'a laisse ouvert.

      ⚠️ Un menu est une PHOTO de l'etat au moment ou on l'ouvre : sans ca, le
      comptoir affiche encore le prix d'un fusil deja paye — et le revend une
      deuxieme fois. Le constructeur du menu (`refaire`) recalcule ce qui
      s'affiche ; le curseur, lui, ne bouge pas de sous le pouce du joueur. */
  function rafraichirMenu() {
    const m = B.menu;
    if (!m || !m.refaire) return;
    const neuf = m.refaire();
    if (!neuf || !neuf.items || !neuf.items.length) return;
    m.items = neuf.items;
    m.titre = neuf.titre;
    m.sur = neuf.sur;
    m.aide = neuf.aide;
    m.curseur = Math.max(0, Math.min(m.curseur, m.items.length - 1));
  }

  /** Navigation : haut/bas (clavier, stick, joystick), ACTION choisit, FRAPPE ou annuler ferme. */
  /** Combien de lignes tiennent dans la boite. ⚠️ Un menu qui tient au
      complet rend exactement son nombre d'items : le defilement ne se
      declenche que quand la hauteur bute sur l'ecran (`VH - 30`), donc aucun
      menu existant ne change d'allure. */
  /** Un petit triangle de defilement, trois rangees de pixels. */
  function fleche(ctx, x, y, sens) {
    ctx.fillStyle = '#8a8698';
    for (let i = 0; i < 3; i++) {
      const larg = sens < 0 ? 1 + i * 2 : 5 - i * 2;
      ctx.fillRect(x + (5 - larg) / 2, y + i, larg, 1);
    }
    B.stats.rects += 3;
  }

  function fenetreMenu(m) {
    const h = m.hauteur || Math.min(VH - 30, 40 + m.items.length * 14 + (m.aide ? 14 : 0));
    return Math.max(1, Math.floor((h - 28 - (m.aide ? 16 : 6)) / 14));
  }

  /** Garde le curseur dans la fenetre. Rend le premier item visible. */
  function hautDuMenu(m) {
    const f = fenetreMenu(m), n = m.items.length;
    let haut = m.haut || 0;
    if (haut > n - f) haut = n - f;
    if (haut < 0) haut = 0;
    if (m.curseur < haut) haut = m.curseur;
    if (m.curseur >= haut + f) haut = m.curseur - f + 1;
    m.haut = haut;
    return haut;
  }

  function majMenu() {
    const m = B.menu;
    if (!m) return;
    // Un menu qui montre quelque chose de VIVANT (l'ecran MANETTE, et les
    // boutons qu'on voit s'allumer) se refait a chaque image.
    if (m.maj) m.maj(m);
    // ⚠️ Pendant qu'on reapprend un bouton, le menu ne bouge plus : la manette
    // est muette (voir `Entree.apprendre`) et le clavier ne sert qu'a annuler.
    if (Entree.apprendEnCours()) {
      if (Entree.neuf('pause') || Entree.neuf('annuler')) { Entree.annulerApprentissage(); Son.SFX.erreur(); }
      return;
    }
    const axe = Entree.axe;
    let sens = 0;
    if (Entree.neuf('haut')) sens = -1;
    if (Entree.neuf('bas')) sens = 1;
    if (!sens && axe.source !== 'clavier' && Math.abs(axe.y) > 0.6) {
      if (repetT <= 0) { sens = axe.y < 0 ? -1 : 1; repetT = 12; } else repetT--;
    } else if (axe.mag < 0.3) repetT = 0;
    if (sens) {
      const n = m.items.length;
      m.curseur = (m.curseur + sens + n) % n;
      Son.SFX.menu();
    }
    if (Entree.neuf('action')) {
      const item = m.items[m.curseur];
      if (item && item.actif !== false) {
        const fini = item.faire ? item.faire(item) : true;
        if (fini !== false && B.menu === m) fermerMenu();
        else if (B.menu === m) rafraichirMenu();
      } else Son.SFX.erreur();
    }
    // Un menu `obligatoire` (l'arrestation) ne se ferme que par un choix.
    // ⚠️ `manetteInerte` (l'ecran MANETTE) : on y appuie sur les boutons pour
    // les VOIR s'allumer, pas pour commander. La manette peut encore bouger le
    // curseur et choisir — sinon un joueur qui n'a QUE sa manette resterait
    // enferme — mais elle ne FERME plus l'ecran sous ses doigts.
    const ferme = m.manetteInerte ? Entree.neufSansManette : Entree.neuf;
    if (!m.obligatoire && (ferme('annuler') || ferme('attaque') || ferme('pause'))) {
      // ⚠️ `retour` : une page d'un carnet recule d'un cran au lieu de rendre
      // la main au jeu. Sans ca, sortir du JOURNAL relancait la partie, et il
      // fallait remettre PAUSE pour lire la page d'a cote.
      if (m.retour) { const r = m.retour; Son.SFX.menu(); r(); } else fermerMenu();
    }
  }

  function dessinerMenu(ctx) {
    const m = B.menu;
    if (!m) return;
    // `largeur`, `hauteur` et `colonne` : un menu qui montre autre chose qu'une
    // liste (l'ecran MANETTE et son dessin) prend la place qu'il lui faut.
    const l = m.largeur || 300;
    const h = m.hauteur || Math.min(VH - 30, 40 + m.items.length * 14 + (m.aide ? 14 : 0));
    const x = (VW - l) / 2, y = (VH - h) / 2;
    ctx.fillStyle = 'rgba(11,10,18,0.92)'; ctx.fillRect(x, y, l, h);
    ctx.fillStyle = '#e8b33c'; ctx.fillRect(x, y, l, 1); ctx.fillRect(x, y + h - 1, l, 1);
    texte(ctx, m.titre, x + 8, y + 7, '#e8b33c', 2);
    if (m.sur) texte(ctx, m.sur, x + l - 8 - Atlas.largeurTexte(m.sur, 1), y + 10, '#cdc6e6', 1);
    const f = fenetreMenu(m), haut = hautDuMenu(m);
    m.items.slice(haut, haut + f).forEach(function (item, k) {
      const i = haut + k;
      const yy = y + 28 + k * 14;
      const choisi = i === m.curseur;
      const actif = item.actif !== false;
      if (choisi) { ctx.fillStyle = 'rgba(232,179,60,0.18)'; ctx.fillRect(x + 4, yy - 3, (m.colonne || l) - 8, 12); }
      texte(ctx, (choisi ? '> ' : '  ') + item.libelle, x + 8, yy, actif ? (choisi ? '#efe6d0' : '#cdc6e6') : '#6a6678', 1);
      const bord = x + (m.colonne || l);
      if (item.detail) texte(ctx, item.detail, bord - 8 - Atlas.largeurTexte(item.detail, 1), yy, actif ? '#e8b33c' : '#6a6678', 1);
    });
    // Les fleches de defilement : on doit voir qu'il y a autre chose au-dessus
    // et en dessous, sinon une page longue a l'air d'etre toute la page.
    // ⚠️ Dessinees, pas ecrites : la police pixel n'a que des lettres, des
    // chiffres et un peu de ponctuation — un « ▲ » y tomberait sur un « ? ».
    if (haut > 0) fleche(ctx, x + l - 12, y + 29, -1);
    if (haut + f < m.items.length) fleche(ctx, x + l - 12, y + 30 + (f - 1) * 14, 1);
    if (m.aide) texte(ctx, m.aide, x + 8, y + h - 12, '#8a8698', 1);
    if (m.dessiner) m.dessiner(ctx, x, y, l, h);
    B.stats.rects += 4;
  }

  // --- Pause : reprendre, bilan, options, quitter ------------------------------------

  function menuOptions() {
    const o = B.options;
    function bascule(cle, libelle) {
      return { libelle: libelle, detail: o[cle] ? 'OUI' : 'NON', faire: function (item) {
        o[cle] = !o[cle]; item.detail = o[cle] ? 'OUI' : 'NON';
        if (cle === 'muet') Son.majVolume();
        Sauvegarde.ecrireOptions(o);
        return false;
      } };
    }
    // ⚠️ Le son peut etre parfaitement branche et ne rien sortir : le
    // navigateur le retient tant qu'aucun geste n'a touche la page. Cette
    // ligne-la n'est pas un reglage, c'est un diagnostic — sans elle, un joueur
    // a la manette cherche la panne dans ses haut-parleurs.
    const ETATS = { actif: 'ACTIF', attente: 'TOUCHE L\'ECRAN', coupe: 'COUPE', absent: 'INDISPONIBLE' };
    const etatSon = { libelle: 'SON', detail: ETATS[Son.etatSon()] || '?', actif: false };
    return { titre: 'OPTIONS', curseur: 1,
      maj: function () { etatSon.detail = ETATS[Son.etatSon()] || '?'; }, items: [
      etatSon,
      bascule('sang', 'SANG'),
      bascule('vibration', 'VIBRATION'),
      bascule('muet', 'SON COUPE'),
      bascule('daltonien', 'PALETTE DALTONIENNE'),
      bascule('trace', 'TRACE DES VEHICULES'),
      { libelle: 'MANETTE', faire: function () { ouvrirMenu(menuManette()); return false; } },
      { libelle: 'RETOUR', faire: function () { ouvrirMenu(menuPause()); return false; } },
    ], aide: 'ACTION : CHANGER · FRAPPE : FERMER' };
  }

  // --- La manette : une disposition a choisir, un dessin qui la prouve ---------------

  //: Le dessin d'une manette, en pixels, a l'echelle 1 (78 x 46). Chaque piece
  //: dit de quel BOUTON elle est le portrait : `a` l'action, `rang` le rang
  //: dans sa liste (un bouton d'epaule et un bouton de droite peuvent servir la
  //: meme action). C'est ce qui fait du dessin une PREUVE — on appuie, la piece
  //: correspondante s'allume ; si ce n'est pas celle qu'on a sous le pouce, la
  //: disposition choisie n'est pas la bonne.
  const MANETTE_PIECES = [
    { pedale: 'frein', x: 10, y: 0, l: 14, h: 4 },
    { pedale: 'gaz', x: 54, y: 0, l: 14, h: 4 },
    { a: 'arme', rang: 1, x: 8, y: 5, l: 18, h: 5 },
    { a: 'attaque', rang: 1, x: 52, y: 5, l: 18, h: 5 },
    { a: 'haut', x: 15, y: 14, l: 4, h: 4 },
    { a: 'gauche', x: 11, y: 18, l: 4, h: 4 },
    { a: 'droite', x: 19, y: 18, l: 4, h: 4 },
    { a: 'bas', x: 15, y: 22, l: 4, h: 4 },
    { a: 'carte', x: 33, y: 18, l: 5, h: 3 },
    { a: 'pause', x: 41, y: 18, l: 5, h: 3 },
    { a: 'arme', rang: 0, x: 59, y: 14, l: 5, h: 5 },
    { a: 'attaque', rang: 0, x: 54, y: 19, l: 5, h: 5 },
    { a: 'esquive', rang: 0, x: 64, y: 19, l: 5, h: 5 },
    { a: 'action', rang: 0, x: 59, y: 24, l: 5, h: 5 },
  ];
  const MANETTE_L = 78, MANETTE_H = 46;

  /** Cette piece est-elle enfoncee en ce moment ?

      Par le NUMERO du bouton quand on en a un — c'est ce qui distingue le
      bouton d'epaule du bouton de droite qui font la meme chose. La croix sur
      un axe n'a pas de numero : on retombe alors sur l'action elle-meme. */
  function pieceEnfoncee(piece, profil, etat) {
    if (piece.pedale) return (piece.pedale === 'gaz' ? Entree.gaz : Entree.frein) > 0.15;
    const indice = (profil.boutons[piece.a] || [])[piece.rang || 0];
    if (indice === undefined) return Entree.bas(piece.a);
    return etat.boutons.indexOf(indice) >= 0;
  }

  function dessinerManette(ctx, ox, oy, ech, profil, etat) {
    function r(x, y, l, h, couleur) {
      ctx.fillStyle = couleur;
      ctx.fillRect(ox + x * ech, oy + y * ech, l * ech, h * ech);
      B.stats.rects++;
    }
    r(0, 24, 16, 22, '#22242a'); r(62, 24, 16, 22, '#22242a');      // les poignees
    r(4, 10, 70, 24, '#2c2c30');
    r(6, 12, 66, 20, '#3a3d44');                                    // la face
    r(24, 26, 9, 9, '#22242a'); r(47, 26, 9, 9, '#22242a');         // les cuvettes
    const axe = Entree.axe, decal = axe.source === 'manette' ? axe : { x: 0, y: 0 };
    r(26 + Math.round(decal.x * 2), 28 + Math.round(decal.y * 2), 5, 5, '#8a8698');
    r(49, 28, 5, 5, '#6f757c');
    r(15, 18, 4, 4, '#4a4e57');                                     // le coeur de la croix
    for (const piece of MANETTE_PIECES) {
      r(piece.x, piece.y, piece.l, piece.h, pieceEnfoncee(piece, profil, etat) ? '#e8b33c' : '#6f757c');
    }
  }

  //: Les actions qu'on peut reapprendre, dans l'ordre de « TOUT REAPPRENDRE ».
  //: La croix compte pour une ligne et s'apprend en quatre gestes.
  const LIGNES_MANETTE = [
    ['action', 'ACTION / ENTRER'],
    ['attaque', 'FRAPPER / KLAXON'],
    ['esquive', 'COURIR / FREIN A MAIN'],
    ['arme', 'ARME / RADIO'],
    ['annuler', 'RETOUR'],
    ['pause', 'PAUSE'],
    ['carte', 'CARTE'],
    ['croix', 'CROIX DIRECTIONNELLE'],
    ['gaz', 'GAZ'],
    ['frein', 'FREIN'],
    ['stick', 'STICK DE MARCHE'],
  ];
  const CROIX = ['haut', 'bas', 'gauche', 'droite'];
  const NOM_CROIX = { haut: 'HAUT', bas: 'BAS', gauche: 'GAUCHE', droite: 'DROITE' };

  function detailManette(quoi, profil) {
    if (quoi === 'stick') return 'AXES ' + profil.axes[0] + '/' + profil.axes[1];
    if (quoi === 'gaz' || quoi === 'frein') {
      const s = profil[quoi];
      return (s.type === 'axe' ? 'AXE ' : 'BOUTON ') + s.i;
    }
    if (quoi === 'croix') {
      // Une croix-chapeau (un seul axe pour huit directions) se dit autrement.
      if (profil.croix) return 'AXE ' + profil.croix.i + ' · ' + Object.keys(profil.croix.valeurs).length + '/4';
      const n = CROIX.map(function (a) { return profil.boutons[a][0]; }).filter(function (v) { return v !== undefined; });
      return n.length ? n.join(' ') : 'AUCUN';
    }
    const b = profil.boutons[quoi] || [];
    return b.length ? 'BOUTON ' + b.join(', ') : 'AUCUN';
  }

  /** Le deuxieme ecran : un bouton par action, qu'on REAPPREND en l'appuyant.

      C'est le recours quand aucune disposition toute faite ne tombe juste —
      et sur une manette que le navigateur ne reconnait pas, ca arrive. */
  function menuManetteBoutons() {
    let suite = null;                 // la file de « TOUT REAPPRENDRE »
    function garder() {
      B.options.manette = Entree.profilManette();
      B.options.manetteProfil = 'apprise';       // plus aucune disposition toute faite
      Sauvegarde.ecrireOptions(B.options);
    }
    function apprendreUn(quoi, apres) {
      if (quoi === 'croix') return apprendreCroix(0, apres);
      Entree.apprendre(quoi, function () { garder(); Son.SFX.menu(); if (apres) apres(); });
    }
    function apprendreCroix(k, apres) {
      if (k >= CROIX.length) { if (apres) apres(); return; }
      Entree.apprendre(CROIX[k], function () { garder(); Son.SFX.menu(); apprendreCroix(k + 1, apres); });
    }
    function toutReapprendre(k) {
      if (k >= LIGNES_MANETTE.length) { suite = null; return; }
      suite = LIGNES_MANETTE[k][0];
      apprendreUn(suite, function () { toutReapprendre(k + 1); });
    }
    const items = LIGNES_MANETTE.map(function (l) {
      return { libelle: l[1], quoi: l[0], faire: function () { apprendreUn(l[0]); return false; } };
    });
    items.push({ libelle: 'TOUT REAPPRENDRE', faire: function () { toutReapprendre(0); return false; } });
    items.push({ libelle: 'RETOUR', faire: function () { suite = null; ouvrirMenu(menuManette()); return false; } });
    const menu = { titre: 'REAPPRENDRE', items: items, curseur: 0, manetteInerte: true };
    let repos = null;                 // les axes au repos, pour voir lesquels bougent
    menu.maj = function (m) {
      const etat = Entree.manetteInfo(), profil = Entree.profilManette();
      if (!repos || repos.length !== etat.axes.length) repos = etat.axes.slice();
      // ⚠️ Les AXES QUI BOUGENT, c'est le diagnostic de la croix morte : sur
      // bien des manettes Bluetooth la croix n'est pas quatre boutons mais un
      // seul axe, et on appuie dessus sans qu'aucun numero ne s'allume.
      const bougent = etat.axes.map(function (v, i) { return Math.abs(v - repos[i]) > 0.3 ? i : -1; })
        .filter(function (i) { return i >= 0; });
      // ⚠️ La ligne du haut est le vrai diagnostic : une manette « NON
      // RECONNUE » explique a elle seule des boutons qui ne repondent pas la
      // ou on les attend.
      m.sur = etat.branchee ? (etat.mapping === 'standard' ? 'RECONNUE' : 'NON RECONNUE') : 'AUCUNE MANETTE';
      for (const item of m.items) {
        if (!item.quoi) continue;
        const encours = etat.apprend && (etat.apprend === item.quoi
          || (item.quoi === 'croix' && CROIX.indexOf(etat.apprend) >= 0));
        item.detail = encours
          ? 'APPUIE' + (item.quoi === 'croix' ? ' ' + NOM_CROIX[etat.apprend] : '') + '...'
          : detailManette(item.quoi, profil);
      }
      // Une 8BitDo en Bluetooth se presente en manette Switch ou DirectInput ;
      // par le dongle 2,4 GHz ou le cable, elle se presente en Xbox — et la, le
      // navigateur la reconnait. Ca vaut la peine de le dire sur place.
      const indice = /8bitdo/i.test(etat.id || '') && etat.mapping !== 'standard'
        ? '8BITDO : DONGLE 2,4 GHZ OU CABLE = MODE XBOX'
        : (etat.id || '?').slice(0, 24).toUpperCase();
      m.aide = etat.apprend
        ? (etat.attend ? 'RELACHE D’ABORD · ECHAP : ANNULER'
                       : 'APPUIE SUR LE BOUTON (OU LA CROIX) VOULU · ECHAP : ANNULER')
        : (etat.branchee
          ? 'ENFONCES : ' + (etat.boutons.length ? etat.boutons.join(' ') : '—')
            + ' · AXES : ' + (bougent.length ? bougent.join(' ') : '—')
            + ' · ' + indice
          : 'BRANCHE UNE MANETTE ET APPUIE SUR UN BOUTON');
      void suite;
    };
    menu.maj(menu);
    return menu;
  }

  /** L'ecran MANETTE : une disposition a choisir, et un dessin qui la prouve.

      ⚠️ Aucun test ne peut dire si une disposition correspond a la manette de
      quelqu'un : les numeros de boutons d'une manette que le navigateur ne
      reconnait pas ne veulent rien dire, et la meme manette n'a pas les memes
      numeros sur le telephone et sur le Mac. Le dessin, lui, le dit tout de
      suite — on appuie, la piece s'allume. Au bon endroit : c'est la bonne.
      Ailleurs : on essaie la suivante, ou on reapprend bouton par bouton. */
  function menuManette() {
    const bloc = B.defs.manettes || { profils: [], defaut: 'standard' };
    function choisir(profil) {
      Entree.reglerManette(profil);
      Entree.oublierRepos();
      B.options.manette = Entree.profilManette();
      B.options.manetteProfil = profil.slug;
      Sauvegarde.ecrireOptions(B.options);
      Son.SFX.menu();
      return false;
    }
    const items = bloc.profils.map(function (p) {
      return { libelle: p.nom, profil: p, faire: function () { return choisir(p); } };
    });
    items.push({ libelle: 'REAPPRENDRE BOUTON PAR BOUTON',
                 faire: function () { ouvrirMenu(menuManetteBoutons()); return false; } });
    items.push({ libelle: 'RETOUR', faire: function () { ouvrirMenu(menuOptions()); return false; } });
    // Le curseur commence sur la disposition en cours : appuyer sur ACTION pour
    // voir le bouton s'allumer ne change alors rien.
    const actuel = B.options.manetteProfil || bloc.defaut;
    const depart = Math.max(0, items.findIndex(function (i) { return i.profil && i.profil.slug === actuel; }));
    const menu = { titre: 'MANETTE', items: items, curseur: depart, manetteInerte: true,
                   largeur: 420, hauteur: 162, colonne: 212 };
    menu.maj = function (m) {
      const etat = Entree.manetteInfo();
      m.sur = etat.branchee ? (etat.mapping === 'standard' ? 'RECONNUE' : 'NON RECONNUE')
                            : 'AUCUNE MANETTE';
      const choisi = B.options.manetteProfil || bloc.defaut;
      for (const item of m.items) {
        if (!item.profil) continue;
        // ⚠️ Le detail du profil ne tient pas a cote de son nom : il se dit en
        // bas, pour celui que le curseur survole. La colonne, elle, ne porte
        // qu'un mot : laquelle est choisie.
        item.detail = item.profil.slug === choisi ? 'CHOISIE' : '';
      }
      const survole = m.items[m.curseur];
      const quoi = survole && survole.profil ? survole.profil.detail + ' · ' : '';
      m.aide = etat.branchee
        ? quoi + 'APPUIE SUR UN BOUTON : IL DOIT S’ALLUMER AU BON ENDROIT'
        : quoi + 'BRANCHE UNE MANETTE ET APPUIE SUR UN BOUTON';
    };
    menu.dessiner = function (ctx, x, y) {
      const etat = Entree.manetteInfo(), profil = Entree.profilManette();
      dessinerManette(ctx, x + 232, y + 24, 2, profil, etat);
      // ⚠️ Un bouton que la disposition ne connait pas n'allume RIEN, et on
      // croirait la manette morte. On le dit : c'est le signe qu'il faut une
      // autre disposition, ou reapprendre celle-la.
      const connus = {};
      for (const a in profil.boutons) for (const i of profil.boutons[a]) connus[i] = true;
      for (const cle of ['gaz', 'frein']) if (profil[cle].type === 'bouton') connus[profil[cle].i] = true;
      const inconnus = etat.boutons.filter(function (i) { return !connus[i]; });
      const bit = /8bitdo/i.test(etat.id || '') && etat.mapping !== 'standard';
      const lignes = ['ENFONCES : ' + (etat.boutons.length ? etat.boutons.join(' ') : '—'),
                      inconnus.length ? 'BOUTON ' + inconnus.join(' ') + ' : PAS DANS CELLE-CI'
                        : (bit ? '8BITDO : DONGLE 2,4 GHZ = XBOX' : (etat.id || '').slice(0, 24).toUpperCase())];
      lignes.forEach(function (l, i) {
        if (l) texte(ctx, l, x + 232, y + 122 + i * 10, '#8a8698', 1);
      });
    };
    menu.maj(menu);
    return menu;
  }

  /** Le bilan de la session : ce qu'on a fait depuis le debut. */
  function menuBilan() {
    const p = B.partie, s = p.stats;
    const minutes = Math.floor((s.secondes || 0) / 60);
    const fortune = p.argent + (p.planque.coffre || 0);
    const lignes = [
      ['JOUR ' + p.jour + ' · ' + minutes + ' MIN JOUEES', ''],
      ['FORTUNE', fortune + ' $'],
      ['PROPRIETES', Object.keys(p.proprietes).length + ' / ' + B.defs.economie.proprietes.filter(function (q) { return q.phase === 1; }).length],
      ['PAQUETS', Object.keys(p.paquets).length + ' / ' + (Monde.carte.ville ? Monde.carte.ville : Monde.carte).def.paquets.length],
      ['CRIMES', String(s.crimes || 0)],
      ['CHARS VOLES', String(s.volees || 0)],
      ['COURSES DE TAXI', String(s.courses || 0)],
      ['MORTS', String(s.tues || 0)],
      ['HOSPITALISATIONS', String(s.hospitalisations || 0)],
    ];
    return { titre: 'BILAN', items: lignes.map(function (l) { return { libelle: l[0], detail: l[1], actif: false }; })
      .concat([{ libelle: 'ENVOYER MON SCORE', faire: function () { fermerMenu(); demanderScore(); return true; } },
               { libelle: 'RETOUR', faire: function () { ouvrirMenu(menuPause()); return false; } }]) };
  }

  // --- Le carnet : la mission, le journal, le repertoire ---------------------------

  /*: ⚠️ Le carnet N'INVENTE AUCUNE DONNEE. Tout ce qu'il montre est deja dans
    la partie et n'etait montre nulle part : l'objectif que le HUD ecrit en
    trente caracteres, les evenements que `Histoire.noter` pose, les gens que
    `p.connus` retient. C'est une FENETRE, pas une comptabilite.

    ⚠️ Et « journal » est pris deux fois dans ce depot : `journal.py` est Le
    Clairon (la manchette du matin), M11 prevoit le carnet du POSTE (le dossier
    de la police sur toi). Ici, c'est la page du joueur, dans LE CARNET. */
  function menuCarnet() {
    const p = B.partie;
    const connus = Object.keys(p.connus || {}).length;
    return { titre: 'LE CARNET', sur: 'JOUR ' + p.jour, largeur: 320, items: [
      { libelle: 'EN COURS', detail: Histoire.courante() ? Histoire.courante().titre.toUpperCase() : 'RIEN',
        faire: function () { ouvrirMenu(menuCarnetEnCours()); return false; } },
      { libelle: 'JOURNAL', detail: (p.carnet || []).length + ' ENTRÉES',
        faire: function () { ouvrirMenu(menuCarnetJournal()); return false; } },
      { libelle: 'RÉPERTOIRE', detail: connus + ' PERSONNE' + (connus > 1 ? 'S' : ''),
        faire: function () { ouvrirMenu(menuCarnetRepertoire()); return false; } },
      // ⚠️ LA DETTE SE LIT ICI, sinon on l'oublie entre deux appels. C'est la
      // même règle que le carnet du poste : une pression qu'on subit sans
      // jamais pouvoir la regarder n'est pas une pression, c'est une
      // malchance. Elle disparaît de la page le jour où elle est réglée —
      // une ligne à zéro serait une dette qu'on traîne pour rien.
      p.dette > 0 ? { libelle: 'LA DETTE DE ROCCO', detail: p.dette + ' $', actif: false } : null,
      { libelle: 'RETOUR', faire: function () { ouvrirMenu(menuPause()); return false; } },
    ].filter(Boolean) };
  }

  //: Une ligne qu'on lit, qu'on ne choisit pas.
  function ligne(libelle, detail) { return { libelle: libelle, detail: detail || '', actif: false }; }

  /** EN COURS : le titre, le donneur, les objectifs — barres pour ce qui est
      fait —, la recompense et ou c'est.

      ⚠️ Ca RAPPELLE ce qu'il faut faire, ca ne raconte pas l'histoire :
      quelqu'un qui rouvre le jeu apres trois jours doit savoir ou aller en
      deux secondes. */
  function menuCarnetEnCours() {
    const p = B.partie, m = Histoire.courante();
    const items = [];
    if (B.defi) {
      const l = Histoire.ligneObjectif();
      items.push(ligne('DÉFI EN COURS'), ligne(l || ''));
    } else if (!m) {
      items.push(ligne('AUCUNE MISSION EN COURS'));
      const gps = Histoire.cible();
      if (gps) items.push(ligne('ON T’ATTEND :', (gps.nom || '').toUpperCase()));
      else items.push(ligne('PERSONNE NE T’ATTEND'));
    } else {
      const perso = Histoire.personnage(m.donneur);
      items.push(ligne('DONNÉE PAR', perso ? perso.nom.toUpperCase() : m.donneur.toUpperCase()));
      items.push(ligne('RÉCOMPENSE', m.recompense + ' $'));
      items.push(ligne(''));
      m.objectifs.forEach(function (o, i) {
        const fait = i < p.mission.etape;
        // ⚠️ « Barre » en police 5x7 : on ne peut pas rayer un texte, alors on
        // le marque et on l'eteint. Une coche, un point, et la couleur fait
        // le reste (`actif: false` grise deja tout).
        items.push({ libelle: (fait ? '\u00B7 ' : i === p.mission.etape ? '> ' : '  ') + o.texte,
                     actif: false });
      });
      const gps = Histoire.cible();
      if (gps) { items.push(ligne('')); items.push(ligne('OÙ', (gps.nom || '').toUpperCase())); }
    }
    items.push({ libelle: 'RETOUR', faire: function () { ouvrirMenu(menuCarnet()); return false; } });
    return { titre: m ? m.titre.toUpperCase() : 'EN COURS', largeur: 320, curseur: items.length - 1,
             items: items, retour: function () { ouvrirMenu(menuCarnet()); } };
  }

  /** JOURNAL : ce qui s'est passe, le plus recent en haut, date au jour. */
  function menuCarnetJournal() {
    const lignes = (B.partie.carnet || []).slice().reverse();
    const items = lignes.map(function (e) { return ligne(e.t, 'J' + e.j); });
    if (!items.length) items.push(ligne('RIEN ENCORE'));
    items.push({ libelle: 'RETOUR', faire: function () { ouvrirMenu(menuCarnet()); return false; } });
    return { titre: 'JOURNAL', largeur: 320, hauteur: VH - 30, curseur: 0, items: items,
             aide: 'HAUT/BAS : LIRE · FRAPPE : RETOUR',
             retour: function () { ouvrirMenu(menuCarnet()); } };
  }

  /** RÉPERTOIRE : les gens qu'on a RENCONTRES, et eux seuls. */
  function menuCarnetRepertoire() {
    const p = B.partie;
    const items = (B.defs.personnages || [])
      .filter(function (q) { return p.connus && p.connus[q.slug]; })
      .map(function (q) {
        return { libelle: q.nom.toUpperCase(), detail: 'J' + p.connus[q.slug],
                 faire: function () { ouvrirMenu(menuCarnetFiche(q.slug)); return false; } };
      });
    if (!items.length) items.push(ligne('TU N’AS ENCORE PARLÉ À PERSONNE'));
    items.push({ libelle: 'RETOUR', faire: function () { ouvrirMenu(menuCarnet()); return false; } });
    return { titre: 'RÉPERTOIRE', largeur: 320, hauteur: VH - 30, items: items,
             aide: 'ACTION : LA FICHE · FRAPPE : RETOUR',
             retour: function () { ouvrirMenu(menuCarnet()); } };
  }

  /** Le lieu d'un personnage, en francais : « porte:terminus » est une adresse
      de code, pas une indication. */
  function ouDuPersonnage(q) {
    if (!q || !q.ou) return null;
    const bout = String(q.ou).split(':');
    if (bout.length < 2) return null;
    if (bout[0] === 'porte') {
      const ville = Monde.carte.ville || Monde.carte;
      const pt = (ville.points || []).find(function (x) { return x.slug === bout[1]; });
      return pt ? pt.nom : bout[1];
    }
    // Un point de piece : c'est la PIECE qui le situe.
    const piece = Histoire.pieceDuPoint(bout[1]);
    return piece ? piece.nom : bout[1];
  }

  /** La fiche d'un personnage : son visage, ou il se tient, ce qu'il a dit. */
  function menuCarnetFiche(slug) {
    const p = B.partie, q = Histoire.personnage(slug);
    const items = [ligne('RENCONTRÉ', 'JOUR ' + (p.connus[slug] || '?'))];
    // ⚠️ `ou` vaut « porte:terminus » ou « point:sergent » — une adresse de
    // code. On la traduit par le NOM du lieu, sinon la fiche dit au joueur
    // d'aller a « PORTE:TERMINUS ».
    const ou = ouDuPersonnage(q);
    if (ou) items.push(ligne('ON LE TROUVE', ou.toUpperCase()));
    // Les missions qu'il a données, et ce qu'on en a fait.
    const siennes = (B.defs.missions || []).filter(function (m) { return m.donneur === slug; });
    siennes.forEach(function (m) {
      items.push(ligne('\u00B7 ' + m.titre.toUpperCase(), p.missionsFaites[m.slug] ? 'FAITE' : ''));
    });
    items.push({ libelle: 'RETOUR', faire: function () { ouvrirMenu(menuCarnetRepertoire()); return false; } });
    return { titre: q ? q.nom.toUpperCase() : slug.toUpperCase(), largeur: 320, colonne: 250,
             curseur: items.length - 1, items: items,
             retour: function () { ouvrirMenu(menuCarnetRepertoire()); },
             // ⚠️ Le visage se cuit avec SES couleurs de palette — celles que
             // `Entites.creerPieton` donne deja a son sosie dans la rue. Rien
             // de neuf a dessiner : on agrandit le meme sprite de 10 x 13.
             dessiner: function (ctx, x, y, l) {
               if (!q || !q.couleurs || typeof SPRITES === 'undefined' || !SPRITES.joueur) return;
               const cuit = Atlas.cuire('joueur', SPRITES.joueur, q.couleurs);
               const img = cuit.poses.bas && cuit.poses.bas[0];
               if (!img) return;
               ctx.imageSmoothingEnabled = false;
               ctx.drawImage(img, 0, 0, img.width, img.height,
                             x + l - 46, y + 26, img.width * 3, img.height * 3);
               B.stats.images++;
             } };
  }

  function menuPause() {
    return { titre: 'PAUSE', sur: 'JOUR ' + B.partie.jour + ' ' + Monde.heureTexte(), items: [
      { libelle: 'REPRENDRE', faire: function () { Jeu.reprendre(); return true; } },
      { libelle: 'CARTE DE LA VILLE', faire: function () { Jeu.ouvrirCarte(); return true; } },
      { libelle: 'LE CARNET', faire: function () { ouvrirMenu(menuCarnet()); return false; } },
      { libelle: 'BILAN DE LA SESSION', faire: function () { ouvrirMenu(menuBilan()); return false; } },
      { libelle: 'OPTIONS', faire: function () { ouvrirMenu(menuOptions()); return false; } },
      { libelle: 'SAUVEGARDER', faire: function () { Missions.sauvegarderPartie(); message('PARTIE SAUVEGARDEE'); return false; } },
      { libelle: 'QUITTER VERS LE TITRE', faire: function () { Jeu.retourTitre(); return true; } },
    ] };
  }

  /** L'invite du bas : ce que fera ACTION ici. */
  function invite(ctx) {
    const j = B.joueur;
    if (!j || j.dansVehicule || !B.invite || B.menu) return;   // un menu ouvert : l'invite se tait
    const t = 'ACTION : ' + B.invite;
    const l = Atlas.largeurTexte(t, 1);
    ctx.fillStyle = 'rgba(11,10,18,0.7)'; ctx.fillRect((VW - l) / 2 - 4, VH - 26, l + 8, 11);
    // ⚠️ La prise du bouclier humain se TIENT, et c'est L'INVITE qui se
    // remplit — pas une jauge de plus dans un coin. Le bouton qui resiste et
    // la phrase qui l'annonce sont la meme chose : sans ce remplissage, une
    // demi-seconde de maintien ressemblait a un bouton qui ne repond pas, et
    // c'est exactement ce qu'on venait de reparer a l'envers.
    const saisie = j.saisie || 0;
    if (saisie > 0) {
      const part = Math.min(1, saisie / Math.round(B.defs.recherche.bouclier.saisie_s * 60));
      ctx.fillStyle = 'rgba(196,54,47,0.55)';
      ctx.fillRect((VW - l) / 2 - 4, VH - 26, Math.round((l + 8) * part), 11);
      B.stats.rects++;
    }
    texte(ctx, t, (VW - l) / 2, VH - 24, '#efe6d0', 1);
    noter('invite', (VW - l) / 2 - 4, VH - 26, l + 8, 11);
  }

  /** Une boite de texte : une ou deux lignes, qui se ferme au bouton. */
  function dialogue(qui, lignes, duree) {
    B.dialogue = { qui: qui, lignes: Array.isArray(lignes) ? lignes : [lignes], t: 0, duree: duree || 0 };
  }

  function dessinerDialogue(ctx) {
    const d = B.dialogue;
    if (!d) return;
    d.t++;
    const h = 22 + d.lignes.length * 9;
    ctx.fillStyle = 'rgba(11,10,18,0.9)'; ctx.fillRect(12, VH - h - 8, VW - 24, h);
    ctx.fillStyle = '#e8b33c'; ctx.fillRect(12, VH - h - 8, VW - 24, 1);
    if (d.qui) texte(ctx, d.qui.toUpperCase(), 18, VH - h - 2, '#e8b33c', 1);
    d.lignes.forEach(function (ligne, i) { texte(ctx, ligne, 18, VH - h + 8 + i * 9, '#efe6d0', 1); });
    // ⚠️ L'HORLOGE DE L'OEIL (`B.image`), PAS CELLE DU MONDE (`B.t`) : depuis
    // qu'un dialogue fige la ville (`Jeu.maj`), `B.t` ne bouge plus pendant
    // qu'on lit — et « ACTION > » serait reste eteint (ou allume) tout l'appel,
    // c'est-a-dire au seul moment ou il a quelque chose a dire.
    if (B.cinema && (B.image >> 4) % 2 === 0) {
      const suite = B.cinema.i < B.cinema.lignes.length - 1 ? 'ACTION >' : 'ACTION > FIN';
      texte(ctx, suite, VW - 18 - Atlas.largeurTexte(suite, 1), VH - 16, '#8a8698', 1);
    }
    if (d.duree && d.t > d.duree) B.dialogue = null;
    B.stats.rects += 2;
  }

  /** Le noir d'un changement de scene (`Jeu.transiter`) : il monte a 1 sur la
      scene qu'on quitte, se TIENT le temps de l'ellipse, et redescend sur la
      nouvelle.

      ⚠️ `vu` dit au jeu que le noir a ete DESSINE. C'est le HUD qui le sait, et
      lui seul : sans ce drapeau, la boucle qui rattrape plusieurs images de
      simulation d'un coup eclaircirait deja quand la nouvelle scene se montre
      pour la premiere fois.

      ⚠️ Et le texte ne s'ecrit QUE sur du noir plein. L'ancien fondu des
      ellipses l'affichait entre 35 % et 75 % de sa course : « REVEIL A
      L'HOPITAL » se lisait par-dessus le trottoir ou l'on venait de tomber. */
  function dessinerTransition(ctx) {
    const tr = B.transition;
    if (!tr) return;
    const noir = tr.ferme + tr.tient;
    const part = tr.t <= tr.ferme ? tr.t / tr.ferme
               : tr.t <= noir ? 1
               : 1 - (tr.t - noir) / tr.ouvre;
    const alpha = Math.max(0, Math.min(1, part));
    ctx.fillStyle = 'rgba(11,10,18,' + alpha.toFixed(3) + ')';
    ctx.fillRect(0, 0, VW, VH);
    if (tr.texte && alpha >= 1) {
      const l = Atlas.largeurTexte(tr.texte, 1);
      Atlas.texte(ctx, tr.texte, (VW - l) / 2, VH / 2 - 4, '#cdc6e6', 1);
    }
    if (tr.fait) tr.vu = true;
    B.stats.rects++;
  }

  // --- Scores ---------------------------------------------------------------------

  function afficherScores(scores) {
    const liste = doc.getElementById('liste-scores');
    liste.innerHTML = '';
    if (!scores || !scores.length) {
      const li = doc.createElement('li');
      li.className = 'scores__vide';
      li.textContent = 'Personne encore. Baie-des-Brumes t’attend.';
      liste.appendChild(li);
      return;
    }
    scores.forEach(function (s) {
      const li = doc.createElement('li');
      const nom = doc.createElement('span'); nom.textContent = s.pseudo;
      const detail = doc.createElement('span');
      detail.textContent = s.fortune.toLocaleString('fr-CA') + ' $ · ' + s.missions + ' missions';
      li.appendChild(nom); li.appendChild(detail);
      liste.appendChild(li);
    });
  }

  function montrerScores() {
    voile('scores');
    fetch(urlScores, { cache: 'no-store' })
      .then(function (r) { return r.json(); })
      .then(function (d) { afficherScores(d.scores); })
      .catch(function () { afficherScores([]); });
  }

  function envoyerScore(ev) {
    ev.preventDefault();
    const champ = doc.getElementById('pseudo'), etatEl = doc.getElementById('score-etat');
    const pseudo = champ.value.trim();
    if (!pseudo) { etatEl.textContent = 'Écris un pseudo.'; return; }
    etatEl.textContent = 'Envoi…';
    const p = B.partie;
    const fortune = p.argent + Object.keys(p.proprietes).reduce(function (s, slug) {
      const prop = B.defs.economie.proprietes.find(function (q) { return q.slug === slug; });
      return s + (prop ? prop.prix : 0);
    }, 0);
    fetch(urlScores, {
      method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ pseudo: pseudo, fortune: fortune, missions: Object.keys(p.missionsFaites).length,
                             proprietes: Object.keys(p.proprietes).length, duree_s: Math.max(1, p.stats.secondes) }),
    })
      .then(function (r) { return r.json().then(function (d) { return { ok: r.ok, d: d }; }); })
      .then(function (res) {
        if (!res.ok) { etatEl.textContent = res.d.erreur || 'Refusé.'; return; }
        p.pseudo = pseudo;
        etatEl.textContent = res.d.rang && res.d.rang <= 10 ? 'Bravo, ' + res.d.rang + 'e au tableau!' : 'Score envoyé.';
        afficherScores(res.d.scores);
        setTimeout(function () { voile('scores'); }, 900);
      })
      .catch(function () { etatEl.textContent = 'Pas de réseau — réessaie plus tard.'; });
  }

  function demanderScore() {
    voile('score-envoi');
    doc.getElementById('pseudo').value = B.partie.pseudo || '';
    doc.getElementById('score-etat').textContent = '';
  }

  // --- Dessin --------------------------------------------------------------------------

  /** Du texte lisible SUR LE JEU : une ombre d'un pixel, toujours.
      ⚠️ Sans elle, l'heure en mauve pale disparait sur un passage pieton — on
      ne s'en apercoit qu'en jouant dehors, jamais sur un fond uni. */
  function texte(ctx, s, x, y, couleur, echelle) {
    Atlas.texte(ctx, s, x + 1, y + 1, 'rgba(11,10,18,0.8)', echelle);
    return Atlas.texte(ctx, s, x, y, couleur, echelle);
  }

  //: Les trois palettes de l'etoile de recherche. ⚠️ Le jaune est a ELLE : le
  //: dore #e8b33c est deja celui de l'argent et de « ce qui est a toi » sur la
  //: carte, et deux choses differentes de la meme couleur ne se lisent plus.
  //: L'eteinte est CREUSE (un contour, pas de corps) : on doit lire « trois
  //: sur cinq » d'un coup d'oeil, sans compter.
  const ETOILE_ALLUMEE = { p: '#fff3a8', c: '#ffd21e', k: '#6b4a00' };
  const ETOILE_ETEINTE = { p: '#3a3a48', c: null, k: '#4a4a5c' };
  const ETOILE_FLASH = { p: '#ffd9d2', c: '#ff5a4e', k: '#6b1008' };
  const ETOILE_L = ETOILE[0].length;
  const ETOILE_H = ETOILE.length;

  /** Une etoile cuite une fois par palette : un seul `drawImage` ensuite. */
  function etoileCuite(cle, pal) {
    return Atlas.cuirePeintre('etoile|' + cle, ETOILE_L, ETOILE_H, function (c) {
      for (let y = 0; y < ETOILE_H; y++) {
        const ligne = ETOILE[y];
        let x = 0;
        while (x < ligne.length) {
          const ch = ligne[x];
          let fin = x + 1;
          while (fin < ligne.length && ligne[fin] === ch) fin++;
          if (ch !== '.' && pal[ch]) { c.fillStyle = pal[ch]; c.fillRect(x, y, fin - x, 1); }
          x = fin;
        }
      }
    });
  }

  /** La rangee d'etoiles, en haut au centre. Rend sa boite, pour que la ligne
      d'objectif sache descendre dessous. */
  function dessinerEtoiles(ctx) {
    const max = B.defs.recherche.etoiles_max;
    const flash = B.recherche.flash > 0 && (B.recherche.flash >> 2) % 2 === 0;
    const pas = ETOILE_L + 2;
    const l = max * pas - 2;
    const x0 = Math.round((VW - l) / 2);
    for (let i = 0; i < max; i++) {
      const allumee = i < B.recherche.etoiles;
      const pal = !allumee ? ETOILE_ETEINTE : (flash ? ETOILE_FLASH : ETOILE_ALLUMEE);
      const cle = !allumee ? 'eteinte' : (flash ? 'flash' : 'allumee');
      ctx.drawImage(etoileCuite(cle, pal), x0 + i * pas, 4);
      B.stats.images++;
    }
    noter('etoiles', x0, 4, l, ETOILE_H);
    return { x: x0, y: 4, l: l, h: ETOILE_H };
  }

  function barre(ctx, x, y, l, h, frac, couleur) {
    ctx.fillStyle = '#101018'; ctx.fillRect(x - 1, y - 1, l + 2, h + 2);
    ctx.fillStyle = '#2a2a3a'; ctx.fillRect(x, y, l, h);
    ctx.fillStyle = couleur; ctx.fillRect(x, y, Math.round(l * borner(frac, 0, 1)), h);
    B.stats.rects += 3;
  }

  // --- Mini-carte ---------------------------------------------------------------------

  const MINI = { x: 6, y: 22, l: 64, h: 48 };

  //: Une couleur par famille de lieu — le joueur doit reconnaitre un blip sans
  //: le lire. Le doré est a lui (planque, propriétés), le bleu aux services.
  /*: Les rythmes des deux reperes qu'on cherche sur une carte. ⚠️ DIFFERENTS,
    et de formes differentes : deux choses qui battent au meme rythme se
    confondent, et on aurait corrige la lisibilite en la cassant. Le joueur est
    un ANNEAU blanc qui s'ouvre et se referme (40 images) et qui ne disparait
    JAMAIS — on ne cache pas la seule chose qu'on cherche ; l'objectif est un
    LOSANGE dore qui bat en 16 images. */
  const PULSE_JOUEUR = 40, BATTEMENT_CIBLE = 16;

  /*: Ce que la derniere image a dessine pour se reperer : le joueur, l'objectif,
    et leur FORME. ⚠️ C'est la seule facon de juger un clignotement sans
    regarder l'ecran — les juges lisent ca, pas des pixels. */
  let marqueurs = { joueur: null, cible: null };

  /** La couleur d'un lieu, prise dans les DONNEES (`carte.familles`).

      ⚠️ Il y avait ici une table de dix lieux ecrite a la main ; la ville en
      compte seize, et les six autres — depanneur, hotel, cantine, usine, phare,
      fourriere — tombaient tous sur le meme gris. Une couleur ecrite a cote des
      lieux ment des qu'on ajoute un lieu. */
  function famillesDeLieu() { return (B.defs && B.defs.carte && B.defs.carte.familles) || {}; }

  function couleurDeLieu(point) {
    const f = famillesDeLieu()[point.famille];
    return f ? f.couleur : '#cdc6e6';
  }

  /** La legende de la carte, BATIE depuis la table des couleurs : les familles
      des lieux que cette ville porte, dans l'ordre de la table. */
  function legendeDeLaCarte(carte) {
    const familles = famillesDeLieu();
    const portees = {};
    for (const point of (carte.points || [])) if (point.famille) portees[point.famille] = true;
    // ⚠️ L'ordre est celui de la TABLE, pas celui des lieux rencontres : sinon la
    // legende se reordonne d'une ville a l'autre, et on la relit a chaque partie.
    return Object.keys(familles).filter(function (nom) { return portees[nom]; }).map(function (nom) {
      return { famille: nom, couleur: familles[nom].couleur, libelle: familles[nom].libelle };
    });
  }

  /** Le rayon de l'anneau du joueur a cette image : il s'ouvre, il se referme. */
  function pulse(base, amplitude) {
    const part = (B.image % PULSE_JOUEUR) / PULSE_JOUEUR;
    return base + Math.round(Math.sin(part * Math.PI) * amplitude);
  }

  /** Un anneau carre de rayon `r` — quatre traits, en pixels entiers. */
  function anneau(ctx, x, y, r, couleur) {
    ctx.fillStyle = couleur;
    ctx.fillRect(x - r, y - r, r * 2 + 1, 1);
    ctx.fillRect(x - r, y + r, r * 2 + 1, 1);
    ctx.fillRect(x - r, y - r, 1, r * 2 + 1);
    ctx.fillRect(x + r, y - r, 1, r * 2 + 1);
    B.stats.rects += 4;
  }

  /** Un losange plein — la forme de l'objectif, celle que le joueur n'a pas. */
  function losange(ctx, x, y, r, couleur) {
    ctx.fillStyle = couleur;
    for (let i = -r; i <= r; i++) {
      const demi = r - Math.abs(i);
      ctx.fillRect(x - demi, y + i, demi * 2 + 1, 1);
    }
    B.stats.rects += r * 2 + 1;
  }

  /** Une fleche qui POINTE, pour une cible hors du cadre. */
  function flecheDeCarte(ctx, x, y, angle, couleur) {
    ctx.fillStyle = couleur;
    ctx.beginPath();
    ctx.moveTo(x + Math.cos(angle) * 4, y + Math.sin(angle) * 4);
    ctx.lineTo(x + Math.cos(angle + 2.4) * 4, y + Math.sin(angle + 2.4) * 4);
    ctx.lineTo(x + Math.cos(angle - 2.4) * 4, y + Math.sin(angle - 2.4) * 4);
    ctx.closePath();
    ctx.fill();
  }

  /** La ville autour du joueur, une tuile par pixel, avec les lieux en blips. */
  function miniCarte(ctx) {
    const carte = Monde.carte, j = B.joueur;
    if (!carte || !j) return;
    const mini = Monde.miniCarte();
    const sx = borner(Math.round(j.x / TT) - MINI.l / 2, 0, Math.max(0, carte.w - MINI.l));
    const sy = borner(Math.round(j.y / TT) - MINI.h / 2, 0, Math.max(0, carte.h - MINI.h));
    ctx.fillStyle = 'rgba(11,10,18,0.85)';
    ctx.fillRect(MINI.x - 1, MINI.y - 1, MINI.l + 2, MINI.h + 2);
    ctx.drawImage(mini, sx, sy, MINI.l, MINI.h, MINI.x, MINI.y, MINI.l, MINI.h);
    B.stats.images++;
    for (const point of carte.points) {
      const px = MINI.x + point.x - sx, py = MINI.y + point.y - sy;
      if (px < MINI.x || px >= MINI.x + MINI.l || py < MINI.y || py >= MINI.y + MINI.h) continue;
      ctx.fillStyle = '#101018'; ctx.fillRect(px - 1, py - 1, 3, 3);
      ctx.fillStyle = couleurDeLieu(point); ctx.fillRect(px, py, 2, 2);
      B.stats.rects += 2;
    }
    // Les agents et les autos de patrouille, en bleu, quand on est recherche.
    if (B.recherche.etoiles > 0) {
      ctx.fillStyle = '#4f8fe8';
      for (const e of B.entites) {
        if (!(e.agent && e.vivant) && !(e.type === 'vehicule' && e.conducteur === 'police')) continue;
        const bx = MINI.x + Math.round(e.x / TT) - sx, by = MINI.y + Math.round(e.y / TT) - sy;
        if (bx >= MINI.x && bx < MINI.x + MINI.l && by >= MINI.y && by < MINI.y + MINI.h) { ctx.fillRect(bx, by, 2, 2); B.stats.rects++; }
      }
    }
    // L'histoire : l'objectif, le donneur a aller voir, le defi.
    // ⚠️ Hors du cadre, ce n'est plus une position — c'est une FLECHE. Avant, la
    // cible etait BORNEE au bord : un objectif a deux cents tuiles s'affichait
    // collé au coin, exactement comme un objectif a trois tuiles. Un repere qui
    // invente une position est pire que pas de repere.
    const gps = Histoire.cible();
    marqueurs.cible = null;
    if (gps) {
      const couleur = gps.couleur || '#e8b33c';
      const gx = MINI.x + Math.round(gps.x / TT) - sx, gy = MINI.y + Math.round(gps.y / TT) - sy;
      const dedans = gx >= MINI.x && gx < MINI.x + MINI.l && gy >= MINI.y && gy < MINI.y + MINI.h;
      const bat = (B.image % BATTEMENT_CIBLE) < BATTEMENT_CIBLE / 2;
      if (dedans) {
        if (bat) losange(ctx, gx, gy, 2, couleur);
        marqueurs.cible = { x: gx, y: gy, forme: 'losange', visible: bat, dedans: true };
      } else {
        // La fleche, elle, ne clignote pas : une direction est une information,
        // pas une alerte — et elle ne se confond avec rien d'autre.
        const cx = MINI.x + MINI.l / 2, cy = MINI.y + MINI.h / 2;
        const angle = Math.atan2(gy - cy, gx - cx);
        const fx = borner(cx + Math.cos(angle) * MINI.l, MINI.x + 4, MINI.x + MINI.l - 5);
        const fy = borner(cy + Math.sin(angle) * MINI.h, MINI.y + 4, MINI.y + MINI.h - 5);
        flecheDeCarte(ctx, fx, fy, angle, couleur);
        marqueurs.cible = { x: Math.round(fx), y: Math.round(fy), forme: 'fleche', visible: true,
                            dedans: false, angle: angle };
      }
    }
    // Le boulot : ce qu'on va chercher (bleu) ou la destination (or) clignote.
    const cible = Missions.boulot.cible;
    if (cible && (B.image >> 4) % 2 === 0) {
      const bx = MINI.x + Math.round(cible.x / TT) - sx, by = MINI.y + Math.round(cible.y / TT) - sy;
      if (bx >= MINI.x && bx < MINI.x + MINI.l && by >= MINI.y && by < MINI.y + MINI.h) {
        ctx.fillStyle = Missions.boulot.etape === 'ramasse' ? '#6f9fd8' : '#e8b33c';
        ctx.fillRect(bx - 1, by - 1, 3, 3);
        B.stats.rects++;
      }
    }
    // Le joueur par-dessus tout le reste : c'est lui qu'on cherche des yeux.
    // ⚠️ Un carre blanc de 2 px etait lisible sur le Faubourg de 157 x 112 ; la
    // ville a quintuple sans qu'il grossisse, et il s'est perdu dans le gris.
    // Il PULSE donc, d'un anneau qui s'ouvre et se referme — et le point, lui,
    // reste dessine a chaque image : on ne cache pas ce qu'on cherche.
    const jx = MINI.x + Math.round(j.x / TT) - sx, jy = MINI.y + Math.round(j.y / TT) - sy;
    const r = pulse(2, 2);
    anneau(ctx, jx, jy, r, 'rgba(255,255,255,0.75)');
    ctx.fillStyle = '#101018'; ctx.fillRect(jx - 1, jy - 1, 4, 4);
    ctx.fillStyle = '#ffffff'; ctx.fillRect(jx, jy, 2, 2);
    marqueurs.joueur = { x: jx, y: jy, r: r, forme: 'anneau', visible: true };
    ctx.fillStyle = '#efe6d0';
    ctx.fillRect(MINI.x - 1, MINI.y - 1, MINI.l + 2, 1);
    ctx.fillRect(MINI.x - 1, MINI.y + MINI.h, MINI.l + 2, 1);
    ctx.fillRect(MINI.x - 1, MINI.y - 1, 1, MINI.h + 2);
    ctx.fillRect(MINI.x + MINI.l, MINI.y - 1, 1, MINI.h + 2);
    B.stats.rects += 6;
  }

  /** La ville entiere, deux pixels par tuile, avec ses lieux nommes, le
      joueur, l'objectif — et la police si elle te cherche. */
  function dessinerCarte(ctx) {
    const carte = Monde.carte.interieur ? (B.exterieur && B.exterieur.carte) : Monde.carte, j = B.joueur;
    if (!carte || !j) return;
    ctx.fillStyle = 'rgba(11,10,18,0.92)'; ctx.fillRect(0, 0, VW, VH);
    const mini = Monde.miniCarte(carte);
    // ⚠️ Au-dessus de 1, on reste sur un ENTIER : une carte de pixels etiree a
    // 1,7 bave. En dessous, on prend la fraction telle quelle — depuis les cinq
    // districts (421 x 213 tuiles), mieux vaut une ville un peu floue qu'une
    // ville qui deborde de l'ecran.
    // ⚠️ La ville se dessine ENTRE le titre et la legende, pas au milieu de
    // l'ecran : centree bêtement, ses dernieres rangees finissaient sous le
    // bandeau de la legende — et c'est La Pointe qu'on ne voyait plus.
    const yHaut = 14, yBas = VH - 38;
    const brut = Math.min((VW - 20) / carte.w, (yBas - yHaut) / carte.h);
    const echelle = brut >= 1 ? Math.floor(brut) : brut;
    const l = carte.w * echelle, h = carte.h * echelle;
    const ox = Math.round((VW - l) / 2), oy = yHaut + Math.round((yBas - yHaut - h) / 2);
    ctx.imageSmoothingEnabled = false;
    ctx.drawImage(mini, 0, 0, carte.w, carte.h, ox, oy, l, h);
    B.stats.images++;
    const pos = function (x, y) { return { x: ox + Math.round(x / TT * echelle), y: oy + Math.round(y / TT * echelle) }; };
    for (const point of carte.points) {
      const p = pos(point.x * TT, point.y * TT);
      ctx.fillStyle = '#101018'; ctx.fillRect(p.x - 2, p.y - 2, 5, 5);
      ctx.fillStyle = couleurDeLieu(point); ctx.fillRect(p.x - 1, p.y - 1, 3, 3);
      B.stats.rects += 2;
    }
    if (B.recherche.etoiles > 0) {
      ctx.fillStyle = '#4f8fe8';
      for (const e of (B.exterieur ? B.exterieur.entites : B.entites)) {
        if (!(e.agent && e.vivant) && !(e.type === 'vehicule' && e.conducteur === 'police')) continue;
        const p = pos(e.x, e.y); ctx.fillRect(p.x, p.y, 2, 2); B.stats.rects++;
      }
    }
    // L'objectif : un losange dore qui bat. La ville entiere tient a l'ecran,
    // alors il n'y a jamais de hors-cadre ici — pas de fleche a prevoir.
    const gps = Histoire.cible();
    marqueurs.cible = null;
    if (gps) {
      const p = pos(gps.x, gps.y);
      const bat = (B.image % BATTEMENT_CIBLE) < BATTEMENT_CIBLE / 2;
      if (bat) losange(ctx, p.x, p.y, 3, gps.couleur || '#e8b33c');
      marqueurs.cible = { x: p.x, y: p.y, forme: 'losange', visible: bat, dedans: true };
    }
    // Le joueur : le meme anneau que sur la mini-carte, en plus large — a un
    // demi-pixel par tuile, un carre blanc de 4 px se perd dans la ville.
    const pj = pos(B.exterieur ? B.exterieur.x : j.x, B.exterieur ? B.exterieur.y : j.y);
    const rj = pulse(4, 3);
    anneau(ctx, pj.x, pj.y, rj, 'rgba(255,255,255,0.8)');
    ctx.fillStyle = '#101018'; ctx.fillRect(pj.x - 2, pj.y - 2, 6, 6);
    ctx.fillStyle = '#ffffff'; ctx.fillRect(pj.x - 1, pj.y - 1, 4, 4);
    B.stats.rects += 2;
    marqueurs.joueur = { x: pj.x, y: pj.y, r: rj, forme: 'anneau', visible: true };
    const zone = Monde.zoneA ? (B.exterieur ? null : Monde.zoneA(j.x, j.y)) : null;
    const ville = (carte.def && carte.def.nom ? carte.def.nom : 'Baie-des-Brumes').toUpperCase();
    const titre = ville + (zone ? ' — ' + zone.nom.toUpperCase() : '');
    texte(ctx, titre, (VW - Atlas.largeurTexte(titre, 1)) / 2, 6, '#e8b33c', 1);
    dessinerLegende(ctx, carte);
    const aide = (gps ? gps.nom.toUpperCase() + ' · ' : '') + 'N : FERMER';
    texte(ctx, aide, (VW - Atlas.largeurTexte(aide, 1)) / 2, VH - 12, '#cdc6e6', 1);
  }

  /** La legende, en deux rangees en bas a gauche. ⚠️ Elle se lit dans les
      donnees : les couleurs des blips codaient deja des familles, et rien ne le
      disait au joueur. */
  function dessinerLegende(ctx, carte) {
    const lignes = legendeDeLaCarte(carte);
    if (!lignes.length) return;
    const parRangee = 4, cellule = 114;
    // ⚠️ Un bandeau sous la legende : sans lui elle se lit sur la ville — donc
    // sur du vert, du bleu et du gris a la fois, et une ligne sur deux disparait.
    const rangees = Math.ceil(lignes.length / parRangee);
    ctx.fillStyle = 'rgba(11,10,18,0.86)';
    ctx.fillRect(0, VH - 36, VW, rangees * 9 + 8);
    B.stats.rects++;
    lignes.forEach(function (entree, i) {
      const x = 12 + (i % parRangee) * cellule;
      const y = VH - 32 + Math.floor(i / parRangee) * 9;
      ctx.fillStyle = '#101018'; ctx.fillRect(x - 1, y - 1, 6, 6);
      ctx.fillStyle = entree.couleur; ctx.fillRect(x, y, 4, 4);
      texte(ctx, entree.libelle, x + 8, y - 1, '#cdc6e6', 1);
      B.stats.rects += 2;
    });
  }

  // --- La roue d'armes --------------------------------------------------------------
  //: ⚠️ CRENEAU 0 EN HAUT, puis dans le sens des aiguilles. `Combat.creneauVise`
  //: lit la direction avec exactement la meme regle, et les deux DOIVENT dire
  //: la meme chose : un dessin qui tourne dans l'autre sens rend la roue
  //: injouable sans qu'aucun test de logique ne rougisse (le pouce pointe la
  //: carabine, le jeu degaine la pelle). Un juge compare les deux.
  const ROUE_ECART = 27;                       // pixels d'arc entre deux creneaux, au moins
  const ROUE_R_MIN = 40, ROUE_R_MAX = 58;      // ⚠️ 58 : au-dela, treize armes debordent du cadre

  /** Le rayon de la roue — il s'ouvre avec le nombre d'armes, jamais au-dela
      de ce que l'ecran montre. */
  function rayonDeLaRoue(n) {
    return Math.round(borner(ROUE_ECART * n / (Math.PI * 2), ROUE_R_MIN, ROUE_R_MAX));
  }

  /** Ou tombe le creneau `i` sur une roue de `n` armes. */
  function posteDeLaRoue(i, n, cx, cy) {
    const a = -Math.PI / 2 + i * (Math.PI * 2 / n);
    const r = rayonDeLaRoue(n);
    return { x: Math.round(cx + Math.cos(a) * r), y: Math.round(cy + Math.sin(a) * r) };
  }

  function iconeDArme(def) {
    const sprite = def && OBJETS[def.sprite] ? def.sprite : 'defaut';
    return Atlas.cuirePeintre('objet|' + sprite, 16, 10, function (g, w, h) { OBJETS[sprite](g, w, h); });
  }

  function dessinerRoue(ctx) {
    const r = B.roue;
    if (!r || !r.armes.length) return;
    const cx = Math.round(VW / 2), cy = Math.round(VH / 2), n = r.armes.length;
    // ⚠️ Un voile LEGER, pas celui des menus (0,6) : la ville continue derriere
    // — au quart de vitesse, mais elle continue — et il faut VOIR ce qui arrive
    // sur soi pendant qu'on choisit. Une roue qui cache la rue ferait du
    // ralenti un abri, alors qu'il est le prix.
    ctx.fillStyle = 'rgba(11,10,18,0.45)';
    ctx.fillRect(0, 0, VW, VH);
    B.stats.rects++;
    for (let i = 0; i < n; i++) {
      const slug = r.armes[i];
      const def = Combat.armeDef(slug);
      if (!def) continue;
      const p = posteDeLaRoue(i, n, cx, cy);
      const choisi = i === r.choix;
      const vide = Combat.aSec(slug);
      ctx.fillStyle = choisi ? '#e8b33c' : '#3a3a48';
      ctx.fillRect(p.x - 11, p.y - 9, 22, 18);
      ctx.fillStyle = choisi ? '#2a2333' : '#14131d';
      ctx.fillRect(p.x - 10, p.y - 8, 20, 16);
      B.stats.rects += 2;
      // ⚠️ A sec, l'icone PALIT et le compte passe au rouge : c'est tout ce
      // que le vieux cycle ne disait pas — on degainait un pistolet a zero et
      // on perdait le tour sans avoir rien vu venir.
      if (vide) ctx.globalAlpha = 0.35;
      ctx.drawImage(iconeDArme(def), p.x - 8, p.y - 7);
      ctx.globalAlpha = 1;
      B.stats.images++;
      if (def.chargeur !== null) {
        const mun = String(Combat.munitions(slug) || 0);
        texte(ctx, mun, p.x + 9 - Atlas.largeurTexte(mun, 1), p.y + 3, vide ? '#ff5a4e' : '#cdc6e6', 1);
      }
    }
    // Au centre, ce qu'on tient sous le pouce : son nom, et ce qu'il reste
    // dedans. Sans ca, treize icones de seize pixels ne se nomment pas.
    const def = Combat.armeDef(r.armes[r.choix]);
    if (!def) return;
    const nom = def.nom.toUpperCase();
    texte(ctx, nom, Math.round(cx - Atlas.largeurTexte(nom, 1) / 2), cy - 6, '#efe6d0', 1);
    const mun = def.chargeur === null ? '' : Combat.munitions(r.armes[r.choix]) + ' / ' + def.munitions_max;
    const sous = mun || (def.usures ? 'SE CASSE' : '');
    if (sous) texte(ctx, sous, Math.round(cx - Atlas.largeurTexte(sous, 1) / 2), cy + 2, '#8a8698', 1);
  }

  //: Ce que la derniere image a dessine, en pixels logiques. Sert au test
  //: tactile : aucun element du HUD ne doit finir sous un bouton.
  let ancres = [];
  function noter(nom, x, y, l, h) { ancres.push({ nom: nom, x: x, y: y, l: l, h: h }); }

  function dessiner() {
    const ctx = Base.ecran();
    const j = B.joueur, p = B.partie;
    if (!p) return;
    ancres = [];
    if (B.etat === 'jeu' || B.etat === 'pause') {
      // Vie et endurance, en haut a gauche.
      barre(ctx, 6, 6, 60, 5, j ? j.vie / j.vieMax : 1, '#c4362f');
      const v = j && j.dansVehicule;
      // Au volant, la barre jaune est celle du char, pas l'endurance.
      // ⚠️ Sous cafe, la barre d'endurance passe au vert et clignote la
      // derniere seconde : sans ca, le souffle long s'arrete au milieu d'une
      // fuite sans que rien ne l'ait annonce.
      const cafeine = j && !v && j.cafeine > 0 && (j.cafeine > 60 || (j.cafeine >> 2) % 2 === 0);
      // ⚠️ La barre de souffle s'EFFACE quand elle n'a rien a dire. Depuis que
      // la course est gratuite, seul le sprint la vide : elle est pleine
      // presque tout le temps, et une barre qui ne bouge jamais ne se lit
      // plus — on cesse de la regarder le jour ou elle compte. Elle revient
      // des qu'on entame le souffle, qu'on a du surplus ou qu'on est sous
      // cafe, et elle s'attarde une seconde pour ne pas clignoter.
      if (j && !v) {
        const dit = j.endurance < 100 || (j.surplus || 0) > 0 || j.cafeine > 0;
        B.souffleT = dit ? 60 : Math.max(0, (B.souffleT || 0) - 1);
      }
      if (v || (j && (B.souffleT || 0) > 0)) {
        barre(ctx, 6, 13, 60, 3, v ? v.vie / v.vieMax : (j ? j.endurance / 100 : 1),
              v ? '#7fb3d8' : (cafeine ? '#8fd46a' : '#e8b33c'));
      }
      // Le souffle EN SURPLUS : une ligne plus mince POSEE SUR la barre, pas a
      // cote — on lit d'un coup « j'ai du souffle, et j'ai de l'avance en plus ».
      // ⚠️ Elle garde sa couleur que la base soit jaune ou verte (le cafe), et
      // elle DISPARAIT au volant : la barre y montre la carrosserie du char, et
      // du souffle par-dessus des points de vie ne voudrait rien dire.
      if (!v && j && j.surplus > 0 && (B.souffleT || 0) > 0) {
        const part = Math.min(1, j.surplus / B.defs.economie.souffle.surplus_max);
        ctx.fillStyle = '#7fd4ff';
        ctx.fillRect(6, 14, Math.max(1, Math.round(60 * part)), 1);
        B.stats.rects++;
      }
      noter('vie', 6, 6, 60, 10);
      // La ligne de boulot rend sa boite : la ligne d'objectif, centree, doit
      // savoir ou elle passe pour ne pas lui rentrer dedans.
      let boiteBoulot = null;
      if (v) {
        const kmh = Math.round(Math.abs(v.vitesse) / v.def.vitesse_max * 120);
        texte(ctx, kmh + ' KM/H', 70, 8, '#efe6d0', 1);
        // ⚠️ La ligne dit QUEL boulot : a quatre, « TAXI » en tete d'une
        // livraison de pizza ne veut plus rien dire.
        const nomBoulot = Missions.boulot.fiche() ? Missions.boulot.fiche().nom.toUpperCase() : '';
        let ligneBoulot = null;
        if (Missions.boulot.etape === 'route' && Missions.boulot.destination) {
          const d = Missions.boulot.destination;
          const dist = Math.round(Math.hypot(d.x - v.x, d.y - v.y) / TT);
          ligneBoulot = nomBoulot + ' : ' + d.nom.toUpperCase() + ' ' + dist + 'M';
        } else if (Missions.boulot.etape === 'ramasse') {
          ligneBoulot = nomBoulot + ' : QUELQU’UN ATTEND';
        }
        if (ligneBoulot) {
          texte(ctx, ligneBoulot, 70, 16, '#e8b33c', 1);
          boiteBoulot = { x: 70, y: 16, l: Atlas.largeurTexte(ligneBoulot, 1), h: 7 };
          noter('boulot', boiteBoulot.x, boiteBoulot.y, boiteBoulot.l, boiteBoulot.h);
        }
      }
      if (!B.interieur) miniCarte(ctx);
      // Argent, etoiles, heure a droite.
      // ⚠️ En tactile, les boutons PAUSE et PLEIN ECRAN sont poses par-dessus
      // le coin haut-droit du canevas : la colonne se decale pour ne pas
      // finir cachee sous le pouce.
      const marge = Entree.estTactile ? 40 : 6;
      const argent = p.argent.toLocaleString('fr-CA') + ' $';
      const largeurArgent = Atlas.largeurTexte(argent, 2);
      texte(ctx, argent, VW - marge - largeurArgent, 6, '#e8b33c', 2);
      const boiteArgent = { x: VW - marge - largeurArgent, y: 6, l: largeurArgent, h: 10 };
      noter('argent', boiteArgent.x, boiteArgent.y, boiteArgent.l, boiteArgent.h);
      // ⚠️ Les etoiles ont quitte cette colonne pour le HAUT AU CENTRE : en
      // poursuite, c'est L'information, et elle etait deux fois plus petite
      // que le montant d'argent juste au-dessus.
      const boiteEtoiles = dessinerEtoiles(ctx);
      const heure = 'JOUR ' + p.jour + ' ' + Monde.heureTexte();
      const largeurHeure = Atlas.largeurTexte(heure, 1);
      texte(ctx, heure, VW - marge - largeurHeure, 20, '#cdc6e6', 1);
      const boiteHeure = { x: VW - marge - largeurHeure, y: 20, l: largeurHeure, h: 7 };
      noter('heure', boiteHeure.x, boiteHeure.y, boiteHeure.l, boiteHeure.h);
      // Le quartier ou l'on se trouve, sous la mini-carte.
      const zone = j && !B.interieur ? Monde.zoneA(j.x, j.y) : null;
      if (!B.interieur) noter('minicarte', MINI.x - 1, MINI.y - 1, MINI.l + 2, MINI.h + 2);
      if (zone) {
        // Une ombre portee d'un pixel : sans elle, le nom disparait sur le
        // trottoir en plein jour — teste a l'oeil, pas en theorie.
        texte(ctx, zone.nom, MINI.x, MINI.y + MINI.h + 4, zone.gang ? '#e88a98' : '#e8e2f4', 1);
      }
      // Arme en bas a droite.
      const arme = Combat.armeCourante();
      if (arme) {
        const mun = p.armes[arme.slug] && p.armes[arme.slug].mun;
        const libelle = arme.nom.toUpperCase() + (mun === null || mun === undefined ? '' : ' ' + mun);
        const large = Atlas.largeurTexte(libelle, 1);
        // ⚠️ En tactile, le coin bas-droit est couvert par FRAPPE et ARME :
        // l'arme courante se range sous la mini-carte, la seule zone que le
        // pouce ne visite jamais.
        const ax = Entree.estTactile ? MINI.x : VW - 6 - large;
        const ay = Entree.estTactile ? MINI.y + MINI.h + 13 : VH - 12;
        texte(ctx, libelle, ax, ay, '#efe6d0', 1);
        noter('arme', ax, ay, large, 7);
      }
      // La charge du coup fort, sous la barre d'endurance.
      if (j && j.charge > 0) {
        const part = Math.min(1, j.charge / Combat.CHARGE_MIN);
        barre(ctx, 6, 19, 30, 3, part, part >= 1 ? '#efe6d0' : '#8a6a3f');
      }
      // L'objectif de l'histoire, en haut au centre, et la fleche vers lui au bord de l'ecran.
      const ligne = !B.interieur ? Histoire.ligneObjectif() : null;
      if (ligne) {
        const l = Atlas.largeurTexte(ligne, 1);
        const x = (VW - l) / 2;
        /* ⚠️ Elle passe SOUS tout ce qu'elle croise dans le bandeau du haut,
           jamais dessus — c'est elle qui cede, toujours. Sous les etoiles
           d'abord : les deux se disputaient le haut au centre, et c'est le
           niveau de recherche qui doit gagner. Sous la ligne de boulot ensuite,
           et c'est le vrai piege : centree, une phrase de soixante-dix
           caracteres (« FAIS TROIS COURSES — KLAXONNE POUR UN CLIENT 0/3 »)
           remonte jusque sous le compteur de vitesse et retombait PILE sur
           « COURSE : POSTE DE POLICE 120M » — deux textes dores imbriques a un
           pixel pres, et plus personne ne lisait ni l'un ni l'autre. Une seule
           regle pour les quatre boites : celle qu'on chevauche en largeur nous
           pousse d'une rangee vers le bas. */
        let y = 6;
        [boiteEtoiles, boiteBoulot, boiteArgent, boiteHeure].forEach(function (b) {
          if (b && x < b.x + b.l && x + l > b.x) y = Math.max(y, b.y + b.h + 2);
        });
        texte(ctx, ligne, x, y, B.defi ? '#7fc4ff' : '#e8b33c', 1);
        noter('objectif', x, y, l, 7);
      }
      const gps = !B.interieur && j ? Histoire.cible() : null;
      if (gps) {
        const dx = gps.x - j.x, dy = gps.y - j.y, d = Math.hypot(dx, dy);
        const sx = gps.x - B.cam.x, sy = gps.y - B.cam.y;
        if (d > 60 && (sx < 8 || sx > VW - 8 || sy < 24 || sy > VH - 30)) {
          const a = Math.atan2(dy, dx);
          const fx = borner(VW / 2 + Math.cos(a) * VW, 12, VW - 12), fy = borner(VH / 2 + Math.sin(a) * VH, 30, VH - 30);
          ctx.fillStyle = gps.couleur || '#e8b33c';
          ctx.beginPath(); ctx.moveTo(fx + Math.cos(a) * 6, fy + Math.sin(a) * 6);
          ctx.lineTo(fx + Math.cos(a + 2.5) * 5, fy + Math.sin(a + 2.5) * 5);
          ctx.lineTo(fx + Math.cos(a - 2.5) * 5, fy + Math.sin(a - 2.5) * 5); ctx.closePath(); ctx.fill();
          const m = Math.round(d / TT) + 'M';
          texte(ctx, m, borner(fx - Atlas.largeurTexte(m, 1) / 2, 2, VW - 20), borner(fy + 8, 30, VH - 20), gps.couleur || '#e8b33c', 1);
        }
      }
      // Message.
      if (B.msg && B.msgT > 0) {
        const l = Atlas.largeurTexte(B.msg, 2);
        ctx.fillStyle = 'rgba(11,10,18,0.75)'; ctx.fillRect((VW - l) / 2 - 6, 40, l + 12, 16);
        Atlas.texte(ctx, B.msg, (VW - l) / 2, 43, '#efe6d0', 2);
        B.msgT--;
      }
      if (B.etat === 'pause') {
        ctx.fillStyle = 'rgba(11,10,18,0.6)'; ctx.fillRect(0, 0, VW, VH);
        dessinerMenu(ctx);
      }
    }
    if (B.etat === 'jeu') {
      invite(ctx);
      dessinerDialogue(ctx);
      // ⚠️ PAR-DESSUS l'invite et la bulle : la roue est ce qu'on regarde,
      // et « ACTION POUR ENTRER » en travers d'une icone d'arme ne se lit plus.
      dessinerRoue(ctx);
      // ⚠️ La rue s'efface SOUS un menu ouvert, comme en pause. La boite d'un
      // menu ne couvre qu'a 92 % : ce qui est clair derriere elle TRANSPERCE —
      // et la bulle d'un passant qui parle sous le comptoir s'imprime en
      // travers d'une ligne, qui devient illisible (Martin a photographie
      // « TOUT REGLER » ecrase par un « HE! LE COUSIN! »). Le voile de la
      // pause existe deja pour ca ; un menu en jeu fige le monde autant
      // qu'elle, il merite le meme fond.
      if (B.menu) { ctx.fillStyle = 'rgba(11,10,18,0.6)'; ctx.fillRect(0, 0, VW, VH); B.stats.rects++; }
      dessinerMenu(ctx);
    }
    if (B.etat === 'carte') dessinerCarte(ctx);
    dessinerTransition(ctx);
    if (B.options.perf) {
      const s = B.stats;
      Atlas.texte(ctx, Math.round(s.ms * 10) / 10 + 'MS ' + s.images + 'I ' + s.entites + 'E', 6, VH - 8, '#8f8', 1);
    }
    if (B.options.trace && B.etat === 'jeu' && !B.interieur) {
      const b = Vehicules.bilanTrace();
      const ligne = 'TRACE ' + b.chars + ' CHARS · ' + b.immobiles + ' IMMOBILES · ' + b.total + ' ANOMALIES';
      Atlas.texte(ctx, ligne, VW - 6 - Atlas.largeurTexte(ligne, 1), VH - 8, b.fraiches ? '#ff5a4e' : '#8f8', 1);
    }
  }

  return { init, voile, etat, message, dialogue, ouvrirMenu, fermerMenu, rafraichirMenu, majMenu, menuPause, menuCarnet, menuCarnetEnCours, menuCarnetJournal, menuCarnetRepertoire, menuCarnetFiche, menuOptions, menuManette, menuManetteBoutons, menuBilan,
    legendeDeLaCarte, couleurDeLieu, PULSE_JOUEUR, BATTEMENT_CIBLE,
    marqueurs: function () { return marqueurs; },
    get voileCourant() { return voileCourant; },
           majAvisSon,
           dessiner, dessinerRoue, rayonDeLaRoue, posteDeLaRoue, miniCarte, MINI, montrerScores, demanderScore,
           afficherScores, ancres: function () { return ancres; } };
})();
