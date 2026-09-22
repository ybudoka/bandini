/* Bandini — HUD (canvas, hors nuit) et la voile DOM du titre. */

const Hud = (function () {
  'use strict';

  let doc = null, racine = null, voiles = {};

  function init(d, r) {
    doc = d; racine = r;
    ['titre', 'compte'].forEach(function (n) { voiles[n] = d.getElementById('voile-' + n); });
    // Un onglet, une ligne de menu : au doigt et a la souris (`toucherMenu`). La
    // toile est etiree en CSS (`Base.redimensionner`) : on ramene le point aux
    // 480 x 270 pixels du jeu.
    const toile = d.getElementById('toile');
    if (toile && toile.addEventListener) {
      toile.addEventListener('pointerdown', function (ev) {
        if (!B.menu) return;
        const b = toile.getBoundingClientRect();
        if (!b.width || !b.height) return;
        toucherMenu((ev.clientX - b.left) * VW / b.width, (ev.clientY - b.top) * VH / b.height);
      });
    }
    // ⚠️ `videPresse` : ENTREE sur le bouton qui a le focus fait un clic ET un
    // appui d'ACTION. Le clic ouvre le choix des parties, et l'appui, lu a
    // l'image suivante, y choisirait aussitot la ligne sous le curseur.
    d.getElementById('bouton-jouer').addEventListener('click', function () { Son.reveiller(); Entree.videPresse(); Jeu.ouvrirParties(); });
    // LE COMPTE (M14) : l'ecran, et le seul endroit du HUD qui parle a `Compte`.
    d.getElementById('bouton-compte').addEventListener('click', function () { Son.reveiller(); montrerCompte(); });
    d.getElementById('bouton-fermer-compte').addEventListener('click', function () { voile('titre'); });
    d.getElementById('compte-form').addEventListener('submit', function (ev) { ev.preventDefault(); envoyerCompte('connexion'); });
    d.getElementById('bouton-compte-inscription').addEventListener('click', function () { envoyerCompte('inscription'); });
    d.getElementById('bouton-compte-deconnexion').addEventListener('click', function () {
      const etatEl = d.getElementById('compte-etat');
      if (etatEl) etatEl.textContent = 'Déconnexion…';
      Compte.deconnecter().then(function (v) { majCompte(v); if (etatEl) etatEl.textContent = 'Déconnecté de cet appareil.'; });
    });
    // LE NIP (M14, 3e vague) : verrou d'ecran sur un appareil deja lie.
    d.getElementById('nip-form').addEventListener('submit', deverrouillerNip);
    d.getElementById('bouton-nip-mot-de-passe').addEventListener('click', function () {
      nipBypasse = true;
      majCompte();
      const el = d.getElementById('compte-pseudo');
      if (el && el.focus) el.focus();
    });
    d.getElementById('nip-activer-form').addEventListener('submit', function (ev) {
      ev.preventDefault();
      const nipEl = d.getElementById('nip-nouveau'), etatEl = d.getElementById('compte-etat');
      const nip = nipEl ? String(nipEl.value || '').trim() : '';
      if (etatEl) etatEl.textContent = 'Activation…';
      Compte.activerNip(nip).then(function (r) {
        if (nipEl) nipEl.value = '';
        if (etatEl) etatEl.textContent = r.ok ? 'NIP activé sur cet appareil.' : (r.motif || 'Refusé.');
        majCompte();
      });
    });
    d.getElementById('bouton-nip-retirer').addEventListener('click', function () {
      const fait = Compte.desactiverNip();
      const etatEl = d.getElementById('compte-etat');
      if (etatEl) etatEl.textContent = fait ? 'NIP retiré de cet appareil.' : 'Déverrouille le compte d’abord.';
      majCompte();
    });
    // EFFACER SON COMPTE (M14, 4e vague) : un bouton, puis une confirmation par mot de passe.
    d.getElementById('bouton-compte-effacer').addEventListener('click', function () {
      effacerDemande = true;
      majCompte();
      const el = d.getElementById('compte-effacer-passe');
      if (el && el.focus) el.focus();
    });
    d.getElementById('bouton-compte-effacer-annuler').addEventListener('click', function () {
      effacerDemande = false;
      const el = d.getElementById('compte-effacer-passe');
      if (el) el.value = '';
      direEffacer('');
      majCompte();
    });
    d.getElementById('compte-effacer-form').addEventListener('submit', envoyerEffacer);
    // ⚠️ L'ecran suit le compte, il ne l'interroge pas : l'ouverture, une partie
    // qui descend ou une session coupee arrivent quand le reseau veut bien.
    Compte.surChangement(function (vue) { majCompte(vue); });
    // LE DEFI DU JOUR (M14, 5e vague) : la ligne du titre suit ce que le serveur a dit.
    Defi.surChangement(majDefiDuJour);
    avisSon = d.getElementById('avis-son');
    logoTitre = d.querySelector('#voile-titre .logo');
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
    // ⚠️ Une voile est du DOM, et le casque n'affiche que la toile : on en
    // sort pour la montrer (depuis le 17 sept. 2026 il n'en reste qu'une, le titre).
    if (nom && typeof Casque !== 'undefined' && Casque.actif) Casque.sortir();
  }

  function etat(nom) { if (racine) racine.dataset.etat = nom; }

  /** La barre de chargement du lancement (`#chargement`), sur 100.

      ⚠️ Elle n'avance jamais a reculons : `chargement.js` l'a deja poussee
      pendant les scripts, et une barre qui recule ment. */
  function progression(valeur) {
    const barre = doc && doc.getElementById('chargement');
    const plein = doc && doc.getElementById('chargement-plein');
    if (!barre || !plein) return;
    const avant = Number(barre.getAttribute('aria-valuenow')) || 0;
    const v = Math.round(Math.max(avant, Math.min(100, valeur)));
    if (v === avant) return;
    barre.setAttribute('aria-valuenow', String(v));
    plein.style.width = v + '%';
  }

  /** La part de la barre qui revient aux scripts (`data-part-scripts`) : celle
      que `chargement.js` remplit, et au-dessus de laquelle le jeu continue. */
  function partDesScripts() {
    const barre = doc && doc.getElementById('chargement');
    return Number(barre && barre.dataset && barre.dataset.partScripts) || 60;
  }

  function finirChargement() {
    const barre = doc && doc.getElementById('chargement');
    if (barre) barre.hidden = true;
  }

  /*: L'ICONE QUI TOURNE quand quelque chose se charge en jouant (`Chargements`).
    ⚠️ Pas au premier fichier : un bruitage deja dans le cache se decode en
    quelques images, et une icone qui clignote a chaque coup de poing se lit
    comme un defaut. Elle attend `apres` images de chargement, puis s'attarde
    `reste` images apres le dernier.
    ⚠️ Au coin BAS-GAUCHE, a une colonne du bord : la boite de dialogue commence
    a x = 12 et s'arrete huit pixels au-dessus du bas, l'icone ne la touche pas.
    En tactile, la croix tient ce coin : l'icone se range contre la mini-carte,
    la ou le pouce ne va jamais (comme l'arme courante). */
  const ICONE = { apres: 12, reste: 20, cote: 10 };
  let chargeDepuis = 0, chargeReste = 0;
  function iconeDeChargement(ctx) {
    const n = typeof Chargements !== 'undefined' ? Chargements.nombre() : 0;
    chargeDepuis = n > 0 ? chargeDepuis + 1 : 0;
    if (chargeDepuis >= ICONE.apres) chargeReste = ICONE.reste;
    else if (n === 0 && chargeReste > 0) chargeReste--;
    if (chargeReste <= 0) return;
    const c = ICONE.cote;
    const x = Entree.estTactile ? MINI.x + MINI.l + 4 : 1;
    const y = Entree.estTactile ? MINI.y + MINI.h - c : VH - c - 1;
    // Huit briques en rond : la plus claire tourne, les autres s'eteignent
    // derriere elle — lisible a l'echelle 1, sans un seul arc a lisser.
    const tete = (B.image >> 2) % 8;
    for (let k = 0; k < 8; k++) {
      const a = k / 8 * Math.PI * 2;
      const age = (tete - k + 8) % 8;
      ctx.fillStyle = age === 0 ? '#ffe39a' : age < 3 ? '#e8b33c' : 'rgba(232,179,60,0.35)';
      ctx.fillRect(Math.round(x + c / 2 - 1 + Math.cos(a) * 3.5), Math.round(y + c / 2 - 1 + Math.sin(a) * 3.5), 2, 2);
      B.stats.rects++;
    }
    noter('chargement', x, y, c, c);
  }

  function message(texte, duree) { B.msg = texte; B.msgT = duree || 120; }

  // --- Menus canvas ---------------------------------------------------------------
  //: Un menu = { titre, items: [{ libelle, detail, actif, faire }], curseur, aide, sur, obligatoire }.
  //: `faire()` rend true pour fermer le menu, false pour le laisser ouvert
  //: (on achete trois hot-dogs sans rouvrir le comptoir).
  //: `refaire()` rend un menu NEUF : un menu qui reste ouvert se refait apres
  //: chaque achat (voir `rafraichirMenu`).
  //: Un item `entete('LE JOUEUR')` est un TITRE DE SECTION : il se lit, le
  //: curseur passe par-dessus (une liste de vingt triches se lit par blocs).
  //: Et chaque ligne qu'on peut choisir se TOUCHE et se CLIQUE (`toucherMenu`).

  //: La repetition d'un menu tenu, en images (60 par seconde) : un cran tout de
  //: suite, le suivant apres `REPETE_PREMIER`, puis un tous les `REPETE_ENSUITE`.
  //: ⚠️ Elle partait apres 12 images (200 ms) — moins qu'un appui ordinaire du
  //: pouce sur la croix tactile : au telephone, le menu sautait de deux lignes.
  const REPETE_PREMIER = 27, REPETE_ENSUITE = 9;
  let repetT = 0, sensTenu = 0;

  /** Le sens qu'on TIENT dans un menu : -1 vers le haut, 1 vers le bas, 0 rien.
      La croix, les fleches, le pouce, le stick — et au doigt, HAUT et BAS. */
  function sensDuMenu() {
    let s = 0;
    if (Entree.bas('haut') || Entree.basTactile('arme')) s -= 1;
    if (Entree.bas('bas') || Entree.basTactile('esquive')) s += 1;
    if (s) return s;
    // Le stick : pris a 0.6, lache sous 0.35, sinon un stick qui tremble autour
    // du seuil compte deux fois.
    const axe = Entree.axe, y = axe.y;
    if (axe.source !== 'manette') return 0;
    if (Math.abs(y) > 0.6 || (sensTenu && Math.sign(y) === sensTenu && Math.abs(y) > 0.35)) return y < 0 ? -1 : 1;
    return 0;
  }

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
    // ⚠️ Une page ouverte DEPUIS le classeur (le journal, l'ecran MANETTE, un
    // saut) en est une SOUS-PAGE : elle garde la barre d'onglets, sous l'onglet
    // d'ou elle vient. Un menu qui ne veut pas du classeur le dit
    // (`classeur: null`) ; la proposition d'un defi, elle, s'ouvre apres que le
    // saut a referme la pause.
    if (menu.classeur === undefined && B.menu && B.menu.classeur) {
      menu.classeur = { onglet: B.menu.classeur.onglet, racine: false };
    }
    B.menu = menu;
    // ⚠️ Un menu qui s'ouvre sous un pouce DEJA pousse (on marchait vers le
    // comptoir) ne bouge pas tant qu'on ne l'a pas lache : sans ca, le curseur
    // filait dans la liste avant qu'on l'ait seulement lue.
    sensTenu = sensDuMenu();
    repetT = Infinity;
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
    if (m.classeur) {
      return Math.max(1, Math.floor((hauteurClasseur(m) - LISTE_CLASSEUR - PIED_CLASSEUR - (m.aide ? 14 : 0)) / 14));
    }
    const h = m.hauteur || Math.min(VH - 30, 40 + m.items.length * 14 + (m.aide ? 14 : 0));
    return Math.max(1, Math.floor((h - 28 - (m.aide ? 16 : 6)) / 14));
  }

  /** Garde le curseur dans la fenetre. Rend le premier item visible.
      ⚠️ Le titre de section juste au-dessus du curseur reste a l'ecran : une
      ligne qui a perdu sa section se lit hors de son contexte. */
  function hautDuMenu(m) {
    const f = fenetreMenu(m), n = m.items.length;
    let haut = m.haut || 0;
    if (haut > n - f) haut = n - f;
    if (haut < 0) haut = 0;
    const avant = m.items[m.curseur - 1];
    const dessus = avant && avant.entete ? m.curseur - 1 : m.curseur;
    if (dessus < haut) haut = dessus;
    if (m.curseur >= haut + f) haut = m.curseur - f + 1;
    m.haut = haut;
    return haut;
  }

  /** Le curseur, un cran dans le `sens`, par-dessus les titres de section.
      `bute` : il s'arrete au bout de la liste au lieu d'en faire le tour. */
  function pasDuCurseur(m, sens, bute) {
    const n = m.items.length;
    let c = m.curseur;
    for (let k = 0; k < n; k++) {
      let s = c + sens;
      if (s < 0 || s >= n) { if (bute) return m.curseur; s = (s + n) % n; }
      c = s;
      if (!m.items[c].entete) return c;
    }
    return m.curseur;
  }

  /** Aucune ligne a choisir : une page qui se lit, et rien d'autre. */
  function rienQueDeLaLecture(m) {
    return !m.items.some(function (i) { return !i.entete && i.actif !== false; });
  }

  /** ACTION sur la ligne du curseur — au bouton comme au doigt. */
  function choisirLigne(m) {
    const item = m.items[m.curseur];
    if (item && !item.entete && item.actif !== false) {
      const fini = item.faire ? item.faire(item) : true;
      if (fini !== false && B.menu === m) fermerMenu();
      else if (B.menu === m) rafraichirMenu();
    } else Son.SFX.erreur();
  }

  /** Un titre de section : il se lit, il ne se choisit pas (`libelle` vide et
      `actif: false`, pour tout ce qui parcourt les lignes d'un menu). */
  function entete(texte) { return { entete: texte, libelle: '', actif: false }; }

  //: Ce que le doigt ou la souris a touche sur la toile, en pixels du jeu. Il se
  //: lit a l'image suivante (`majMenu`), comme un bouton : un menu n'agit que
  //: dans la boucle, jamais au milieu d'un evenement du navigateur.
  //: ⚠️ `index.html` le dit : les COMMANDES tactiles sont de vrais elements,
  //: jamais un test sur la toile — un pouce qui TIENT un bouton doit le sentir
  //: sous lui. Un onglet ou une ligne de menu ne se tient pas : on les touche
  //: une fois, la ou on les voit, et ils ne bougent pas sous le doigt.
  let clic = null;
  //: Les zones a toucher, telles que le DERNIER menu dessine les a posees.
  let cibles = [], ciblesDe = null;
  function poserCible(zone) { cibles.push(zone); }

  /** Un doigt ou un clic en (x, y), en pixels du jeu (480 x 270). */
  function toucherMenu(x, y) { if (B.menu) clic = { x: x, y: y }; }

  function majMenu() {
    const m = B.menu;
    if (!m) return;
    // Un menu qui montre quelque chose de VIVANT (l'ecran MANETTE, et les
    // boutons qu'on voit s'allumer) se refait a chaque image.
    if (m.maj) m.maj(m);
    // ⚠️ Pendant qu'on reapprend un bouton, le menu ne bouge plus : la manette
    // est muette (voir `Entree.apprendre`) et le clavier ne sert qu'a annuler.
    if (Entree.apprendEnCours()) {
      clic = null;
      if (Entree.neuf('pause') || Entree.neuf('annuler')) { Entree.annulerApprentissage(); Son.SFX.erreur(); }
      return;
    }
    // Le doigt, la souris : un onglet s'ouvre, une ligne se choisit tout de suite.
    if (clic) {
      const c = clic;
      clic = null;
      const z = ciblesDe === m ? cibles.find(function (q) {
        return c.x >= q.x && c.x < q.x + q.l && c.y >= q.y && c.y < q.y + q.h;
      }) : null;
      if (z && z.onglet) { ouvrirOnglet(z.onglet); return; }
      // Une page d'un ecran qui en a plusieurs (COMMANDES : a pied, au volant).
      if (z && z.page !== undefined) { if (m.page !== z.page) { m.page = z.page; Son.SFX.menu(); } return; }
      if (z && z.item !== undefined) { m.curseur = z.item; choisirLigne(m); return; }
    }
    // ⚠️ L'ONGLET AVANT TOUT : l'epaule droite est aussi FRAPPE, qui ferme un
    // menu — tournee, la page ne doit pas se refermer dans la meme image.
    if (m.classeur) {
      const s = sensDOnglet(m);
      if (s) { tournerOnglet(m, s); return; }
    }
    // ⚠️ UN appui, UNE ligne. Le pouce sur la croix donnait les deux a la fois :
    // son « haut » neuf bougeait le curseur, puis, a l'image suivante, l'axe
    // analogique du meme pouce le rebougeait, la repetition n'etant pas armee.
    // L'appui neuf (meme tape entre deux images) et le sens tenu (le stick, qui
    // n'a pas d'appui neuf) arment maintenant la MEME repetition.
    let sens = 0, repete = false;
    if (Entree.neuf('haut') || Entree.neufTactile('arme')) sens = -1;
    if (Entree.neuf('bas') || Entree.neufTactile('esquive')) sens = 1;
    const tenu = sensDuMenu();
    if (sens) repetT = REPETE_PREMIER;
    else if (tenu && tenu !== sensTenu) { sens = tenu; repetT = REPETE_PREMIER; }
    else if (tenu && --repetT <= 0) { sens = tenu; repetT = REPETE_ENSUITE; repete = true; }
    sensTenu = tenu;
    // Tenu, le curseur s'arrete au bout de la liste ; un appui neuf, lui, en
    // fait le tour — sinon un pouce qui s'attarde tourne en rond.
    if (sens && !m.sansListe) {
      const c = pasDuCurseur(m, sens, repete);
      if (c !== m.curseur) { m.curseur = c; Son.SFX.menu(); }
    }
    if (Entree.neuf('action')) choisirLigne(m);
    // Un menu `obligatoire` (l'arrestation) ne se ferme que par un choix.
    // ⚠️ `manetteInerte` (l'ecran MANETTE) : on y appuie sur les boutons pour
    // les VOIR s'allumer, pas pour commander. La manette peut encore bouger le
    // curseur et choisir — sinon un joueur qui n'a QUE sa manette resterait
    // enferme — mais elle ne FERME plus l'ecran sous ses doigts.
    const ferme = m.manetteInerte ? Entree.neufSansManette : Entree.neuf;
    if (B.menu === m && !m.obligatoire && (ferme('annuler') || ferme('attaque') || ferme('pause'))) {
      // ⚠️ `retour` : une page d'un carnet recule d'un cran au lieu de rendre
      // la main au jeu. Sans ca, sortir du JOURNAL relancait la partie, et il
      // fallait remettre PAUSE pour lire la page d'a cote.
      if (m.retour) { const r = m.retour; Son.SFX.menu(); r(); } else fermerMenu();
    }
  }

  /** Les lignes d'un menu, la premiere a `y0` : titres de section, curseur,
      detail a droite de la colonne — et une zone a toucher par ligne qu'on
      peut choisir. */
  function dessinerLignesDuMenu(ctx, m, x, y0, l, f, haut) {
    const col = m.colonne || l;
    // Une page qu'on ne fait que lire (le BILAN) n'a pas de curseur a montrer.
    const lire = !!m.classeur && rienQueDeLaLecture(m);
    m.items.slice(haut, haut + f).forEach(function (item, k) {
      const i = haut + k;
      const yy = y0 + k * 14;
      if (item.entete) {
        const w = Atlas.largeurTexte(item.entete, 1);
        texte(ctx, item.entete, x + 8, yy + 1, '#b89a4a', 1);
        ctx.fillStyle = '#3a3450'; ctx.fillRect(x + 13 + w, yy + 4, Math.max(0, col - 21 - w), 1);
        B.stats.rects++;
        return;
      }
      const choisi = i === m.curseur && !lire;
      const actif = item.actif !== false;
      if (choisi) { ctx.fillStyle = 'rgba(232,179,60,0.18)'; ctx.fillRect(x + 4, yy - 3, col - 8, 12); }
      texte(ctx, (choisi ? '> ' : '  ') + item.libelle, x + 8, yy, actif ? (choisi ? '#efe6d0' : '#cdc6e6') : '#6a6678', 1);
      const bord = x + col;
      if (item.detail) texte(ctx, item.detail, bord - 8 - Atlas.largeurTexte(item.detail, 1), yy, actif ? '#e8b33c' : '#6a6678', 1);
      if (actif) poserCible({ x: x + 4, y: yy - 4, l: col - 8, h: 14, item: i });
    });
  }

  function dessinerMenu(ctx) {
    const m = B.menu;
    if (!m) return;
    cibles = []; ciblesDe = m;
    if (m.classeur) { dessinerClasseur(ctx, m); return; }
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
    // `sansListe` : un ecran qui dessine tout lui-meme (COMMANDES) garde la
    // mecanique d'un menu — figer la ville, ACTION choisit, ECHAP ferme — sans
    // la liste.
    if (!m.sansListe) dessinerLignesDuMenu(ctx, m, x, y + 28, l, f, haut);
    // Les fleches de defilement : on doit voir qu'il y a autre chose au-dessus
    // et en dessous, sinon une page longue a l'air d'etre toute la page.
    // ⚠️ Dessinees, pas ecrites : la police pixel n'a que des lettres, des
    // chiffres et un peu de ponctuation — un « ▲ » y tomberait sur un « ? ».
    if (haut > 0 && !m.sansListe) fleche(ctx, x + l - 12, y + 29, -1);
    if (haut + f < m.items.length && !m.sansListe) fleche(ctx, x + l - 12, y + 30 + (f - 1) * 14, 1);
    if (m.aide) texte(ctx, m.aide, x + 8, y + h - 12, '#8a8698', 1);
    if (m.dessiner) m.dessiner(ctx, x, y, l, h);
    B.stats.rects += 4;
  }

  // --- Le classeur : la PAUSE en onglets ----------------------------------------------
  //: Demande de Martin (22 sept. 2026) : « remanier tous les menus pour que ce
  //: soit plus convivial et plus facile de s'y retrouver — des onglets
  //: cliquables, ou deplacables avec R et L ». La PAUSE etait un arbre : dix
  //: lignes, dont six ouvraient un sous-menu, qui en ouvraient d'autres (les
  //: triches, puis PLUS…, puis le saut) — et chaque sous-menu avait sa taille, sa
  //: place, et un RETOUR a trouver. Le classeur les range cote a cote :
  //:
  //: - un ONGLET par page (`ONGLETS`), qu'on tourne aux EPAULES (`Entree.neufEpaule`),
  //:   a la croix, aux fleches ← →, ou en le touchant ;
  //: - la boite a le HAUT FIXE, et la rangee d'onglets est centree sur l'ECRAN :
  //:   COMMANDES est plus large que les autres pages, rien ne glisse quand on y passe ;
  //: - une page ouverte depuis un onglet (le journal, la manette, un saut) est une
  //:   SOUS-PAGE : l'onglet reste allume, son titre s'ecrit dessous, B recule ;
  //: - depuis un onglet, B (FRAPPE, ECHAP) reprend la partie : il n'y a plus de
  //:   RETOUR a chercher au bout de la liste ;
  //: - le pied montre les VRAIS boutons de l'appareil qu'on tient.
  //:
  //: ⚠️ Au telephone en paysage, le pouce et les quatre boutons couvrent les
  //: coins du bas (`styles.css`) et PAUSE le coin du haut a droite : la boite des
  //: listes garde les 320 px du milieu, comme le carnet avant elle.
  const HAUT_CLASSEUR = 12, LARGEUR_CLASSEUR = 320, ONGLET_H = 14;
  //: Du haut de la boite a sa premiere ligne ; et le pied, ou vivent les boutons.
  const LISTE_CLASSEUR = 34, PIED_CLASSEUR = 16;
  //: Un dessin fait pour un menu ordinaire (sa premiere ligne a `y + 28`, l'ecran
  //: MANETTE, la fiche d'un personnage) se decale d'autant dans le classeur.
  const DECALAGE_CLASSEUR = LISTE_CLASSEUR - 28;

  /** La hauteur de la boite : ce qu'il faut a la page, jamais plus que l'ecran. */
  function hauteurClasseur(m) {
    const max = VH - HAUT_CLASSEUR - 4;
    // Un ecran qui dessine tout lui-meme (COMMANDES) compte deja son pied.
    if (m.hauteur) return Math.min(max, m.hauteur + DECALAGE_CLASSEUR + (m.sansListe ? 0 : PIED_CLASSEUR));
    return Math.min(max, LISTE_CLASSEUR + m.items.length * 14 + (m.aide ? 14 : 0) + PIED_CLASSEUR);
  }

  /** Une touche du clavier, dessinee comme sur l'ecran COMMANDES. */
  function glypheDeTouche(code) {
    return { s: 'touche', code: code, allume: function () { return Entree.toucheEnfoncee(code); } };
  }

  /** Les deux boutons qui tournent l'onglet, de part et d'autre de la rangee :
      les epaules de SA manette (LB/RB, L1/R1, L/R), les fleches du clavier ;
      rien au doigt — l'onglet se touche. */
  function glyphesDOnglets(m) {
    const appareil = Entree.appareil;
    if (appareil === 'clavier') return [glypheDeTouche('ArrowLeft'), glypheDeTouche('ArrowRight')];
    if (appareil !== 'manette' || m.epaulesInertes) return null;
    const prof = Entree.profilManette(), fam = familleCourante(), etat = Entree.manetteInfo();
    const g = (prof.boutons.arme || [])[1], d = (prof.boutons.attaque || [])[1];
    if (g === undefined || d === undefined || !fam) return null;
    return [glypheDePiece('epaule_g', fam, g, etat), glypheDePiece('epaule_d', fam, d, etat)];
  }

  /** Le pied : ce que font les boutons ICI, dessines pour l'appareil qu'on tient.
      Une page peut y ajouter les siens (`pied`, l'autre page de COMMANDES). */
  function piedDuClasseur(m) {
    const appareil = Entree.appareil, lignes = m.pied ? m.pied() : [];
    if (appareil === 'tactile') {
      lignes.push({ glyphes: [], texte: m.sansListe ? 'TOUCHE UN ONGLET' : 'TOUCHE UN ONGLET, OU UNE LIGNE' });
      return lignes;
    }
    // Un ecran sans liste (COMMANDES) dit lui-meme ce que font ses boutons.
    if (m.sansListe) return lignes;
    const choisir = glypheDAction('action');
    if (choisir && !rienQueDeLaLecture(m)) lignes.push({ glyphes: [choisir], texte: 'CHOISIR' });
    // ⚠️ Sur une page ou l'on essaie sa manette, B s'allume sans rien fermer :
    // on ne promet pas un bouton qui ne fait rien.
    const reculer = appareil === 'clavier' ? glypheDeTouche('Escape')
      : (m.manetteInerte ? null : glypheDAction('annuler'));
    if (reculer) lignes.push({ glyphes: [reculer], texte: m.classeur.racine ? 'REPRENDRE' : 'RETOUR' });
    return lignes;
  }

  function dessinerClasseur(ctx, m) {
    const l = m.largeur || LARGEUR_CLASSEUR, h = hauteurClasseur(m);
    const x = Math.round((VW - l) / 2), y = HAUT_CLASSEUR, corps = y + ONGLET_H;
    ctx.fillStyle = 'rgba(11,10,18,0.92)'; ctx.fillRect(x, corps, l, h - ONGLET_H);
    ctx.fillStyle = '#e8b33c'; ctx.fillRect(x, y + h - 1, l, 1);
    // Les onglets, centres sur l'ECRAN.
    const liste = ongletsVisibles();
    const largeurs = liste.map(function (o) { return Atlas.largeurTexte(o.titre, 1) + 10; });
    const total = largeurs.reduce(function (a, b) { return a + b; }, 0) + 2 * (liste.length - 1);
    const debut = Math.round((VW - total) / 2);
    let tx = debut, lu = null;
    liste.forEach(function (o, k) {
      const w = largeurs[k], la = o.slug === m.classeur.onglet;
      if (la) {
        lu = { x: tx, l: w };
        ctx.fillStyle = 'rgba(11,10,18,0.92)'; ctx.fillRect(tx, y, w, ONGLET_H + 1);
        ctx.fillStyle = '#e8b33c';
        ctx.fillRect(tx, y, w, 1); ctx.fillRect(tx, y, 1, ONGLET_H + 1); ctx.fillRect(tx + w - 1, y, 1, ONGLET_H + 1);
      } else {
        ctx.fillStyle = 'rgba(11,10,18,0.78)'; ctx.fillRect(tx, y + 3, w, ONGLET_H - 3);
      }
      texte(ctx, o.titre, tx + 5, y + (la ? 5 : 7), la ? '#e8b33c' : '#8a8698', 1);
      poserCible({ x: tx, y: y, l: w, h: ONGLET_H + 1, onglet: o.slug });
      tx += w + 2;
    });
    B.stats.rects += 6 + liste.length;
    // La ligne d'or du haut de la boite s'ouvre sous l'onglet qu'on lit.
    ctx.fillStyle = '#e8b33c';
    if (lu) {
      ctx.fillRect(x, corps, Math.max(0, lu.x - x), 1);
      ctx.fillRect(lu.x + lu.l, corps, Math.max(0, x + l - lu.x - lu.l), 1);
    } else ctx.fillRect(x, corps, l, 1);
    const bouts = glyphesDOnglets(m);
    if (bouts) {
      dessinerGlyphe(ctx, bouts[0], debut - 5 - largeurGlyphe(bouts[0]), y + 3);
      dessinerGlyphe(ctx, bouts[1], debut + total + 5, y + 3);
    }
    // Sous la rangee : le titre d'une SOUS-PAGE (l'onglet dit deja celui de la
    // page), et a droite ce que la page dit d'elle-meme (le jour, l'heure).
    const yT = corps + 6;
    if (!m.classeur.racine && m.titre) texte(ctx, m.titre, x + 8, yT, '#e8b33c', 1);
    if (m.sur) texte(ctx, m.sur, x + l - 8 - Atlas.largeurTexte(m.sur, 1), yT, '#8a8698', 1);
    const f = fenetreMenu(m), haut = hautDuMenu(m), y0 = y + LISTE_CLASSEUR;
    if (!m.sansListe) {
      dessinerLignesDuMenu(ctx, m, x, y0, l, f, haut);
      if (haut > 0) fleche(ctx, x + l - 12, y0 + 1, -1);
      if (haut + f < m.items.length) fleche(ctx, x + l - 12, y0 + 2 + (f - 1) * 14, 1);
    }
    if (m.aide) texte(ctx, m.aide, x + 8, y + h - PIED_CLASSEUR - 12, '#8a8698', 1);
    if (m.dessiner) m.dessiner(ctx, x, y + DECALAGE_CLASSEUR, l, h - DECALAGE_CLASSEUR);
    // Le pied, centre.
    const pied = piedDuClasseur(m);
    const largeur = pied.reduce(function (s, li) { return s + largeurLigne(li); }, 0) + 14 * Math.max(0, pied.length - 1);
    let px = x + Math.round((l - largeur) / 2);
    const py = y + h - 13;
    ctx.fillStyle = '#2a2440'; ctx.fillRect(x + 6, py - 4, l - 12, 1);
    B.stats.rects++;
    for (const li of pied) {
      li.allume = li.glyphes.some(function (g) { return g.allume && g.allume(); });
      dessinerLigne(ctx, li, px, py, 'pied');
      px += largeurLigne(li) + 14;
    }
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
    const ETATS = { actif: 'ACTIF', attente: 'TOUCHE L\'ÉCRAN', coupe: 'COUPÉ', absent: 'INDISPONIBLE' };
    const etatSon = { libelle: 'SON', detail: ETATS[Son.etatSon()] || '?', actif: false };
    // Installable, et jouable hors ligne : la ville se garde toute seule, les
    // sons a l'usage — les 14 Mo d'un coup, seulement si on le demande.
    HorsLigne.demanderEtat();
    const sonsHorsLigne = { libelle: 'LES SONS HORS LIGNE', detail: HorsLigne.detail(), actif: HorsLigne.disponible,
      faire: function (item) { HorsLigne.toutTelecharger(); item.detail = HorsLigne.detail(); return false; } };
    return enOnglet('options', { titre: 'OPTIONS', curseur: 1,
      maj: function () {
        etatSon.detail = ETATS[Son.etatSon()] || '?';
        sonsHorsLigne.detail = HorsLigne.detail();
        sonsHorsLigne.actif = HorsLigne.disponible;
      }, items: [
      etatSon,
      bascule('sang', 'SANG'),
      bascule('vibration', 'VIBRATION'),
      bascule('muet', 'SON COUPÉ'),
      bascule('daltonien', 'PALETTE DALTONIENNE'),
      bascule('trace', 'TRACE DES VÉHICULES'),
      // ⚠️ M12 : derriere une option tant que la sonde de performance ne l'a pas jugee.
      bascule('neige', 'TEMPÊTES DE NEIGE (ESSAI)'),
      // ⚠️ Retour de Martin : vue de dessus, on n'est pas assis dans l'auto. Le
      // volant d'une vraie auto (l'arriere part du cote ou l'on tourne) ne colle
      // a l'ecran que nez en haut ; COMME EN AVANT, droite tourne toujours dans
      // le sens des aiguilles d'une montre. Au choix, et l'auto par defaut.
      { libelle: 'VOLANT EN MARCHE ARRIÈRE', detail: o.reculCommeEnAvant ? 'COMME EN AVANT' : 'COMME UNE AUTO', faire: function (item) {
        o.reculCommeEnAvant = !o.reculCommeEnAvant;
        item.detail = o.reculCommeEnAvant ? 'COMME EN AVANT' : 'COMME UNE AUTO';
        Sauvegarde.ecrireOptions(o);
        return false;
      } },
      sonsHorsLigne,
      // ⚠️ La coop locale (essai, un clavier + une manette) : par defaut la
      // manette va au deuxieme joueur — Martin veut pouvoir se la garder
      // (jouer le personnage principal au stick) et laisser le clavier au
      // deuxieme. `Entree.debutImage`/`axeJoueur2` lisent cette meme case.
      bascule('coopP1Manette', 'JOUEUR 1 À LA MANETTE (COOP)'),
      { libelle: 'MANETTE', faire: function () { ouvrirMenu(menuManette()); return false; } },
    ] });
  }

  // --- La manette : une disposition a choisir, un dessin qui la prouve ---------------

  //: Le dessin d'une manette, en pixels, a l'echelle 1 (78 x 46). Chaque piece
  //: dit de quel BOUTON elle est le portrait : `a` l'action, `rang` le rang
  //: dans sa liste (un bouton d'epaule et un bouton de droite peuvent servir la
  //: meme action). C'est ce qui fait du dessin une PREUVE — on appuie, la piece
  //: correspondante s'allume ; si ce n'est pas celle qu'on a sous le pouce, la
  //: disposition choisie n'est pas la bonne.
  //: `nom` : la POSITION de la piece, celle que `manettes.py` nomme (`pieces`)
  //: et qui porte la lettre imprimee (l'ecran COMMANDES).
  const MANETTE_PIECES = [
    { pedale: 'frein', nom: 'gachette_g', x: 10, y: 0, l: 14, h: 4 },
    { pedale: 'gaz', nom: 'gachette_d', x: 54, y: 0, l: 14, h: 4 },
    { a: 'arme', rang: 1, nom: 'epaule_g', x: 8, y: 5, l: 18, h: 5 },
    { a: 'attaque', rang: 1, nom: 'epaule_d', x: 52, y: 5, l: 18, h: 5 },
    { a: 'haut', nom: 'croix', x: 15, y: 14, l: 4, h: 4 },
    { a: 'gauche', nom: 'croix', x: 11, y: 18, l: 4, h: 4 },
    { a: 'droite', nom: 'croix', x: 19, y: 18, l: 4, h: 4 },
    { a: 'bas', nom: 'croix', x: 15, y: 22, l: 4, h: 4 },
    { a: 'carte', nom: 'select', x: 33, y: 18, l: 5, h: 3 },
    { a: 'pause', nom: 'start', x: 41, y: 18, l: 5, h: 3 },
    { a: 'verrouiller', nom: 'centre', x: 36, y: 22, l: 6, h: 3 },
    { a: 'arme', rang: 0, nom: 'haut', x: 59, y: 14, l: 5, h: 5 },
    { a: 'attaque', rang: 0, nom: 'gauche', x: 54, y: 19, l: 5, h: 5 },
    { a: 'esquive', rang: 0, nom: 'droite', x: 64, y: 19, l: 5, h: 5 },
    { a: 'action', rang: 0, nom: 'bas', x: 59, y: 24, l: 5, h: 5 },
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
    ['esquive', 'COURIR / FREIN À MAIN'],
    ['arme', 'ARME / RADIO'],
    ['annuler', 'RETOUR'],
    ['pause', 'PAUSE'],
    ['carte', 'CARTE'],
    ['verrouiller', 'VERROUILLER / CHANGER DE CIBLE'],
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
    items.push({ libelle: 'TOUT RÉAPPRENDRE', faire: function () { toutReapprendre(0); return false; } });
    items.push({ libelle: 'RETOUR', faire: function () { suite = null; ouvrirMenu(menuManette()); return false; } });
    // ⚠️ `epaulesInertes` : on y apprend AUSSI les epaules — elles ne tournent
    // pas l'onglet sous le pouce de celui qui les essaie.
    const menu = { titre: 'RÉAPPRENDRE', items: items, curseur: 0, manetteInerte: true, epaulesInertes: true,
                   retour: function () { suite = null; Entree.annulerApprentissage(); ouvrirMenu(menuManette()); } };
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
        ? '8BITDO : DONGLE 2,4 GHZ OU CÂBLE = MODE XBOX'
        : (etat.id || '?').slice(0, 24).toUpperCase();
      m.aide = etat.apprend
        ? (etat.attend ? 'RELÂCHE D’ABORD · ÉCHAP : ANNULER'
                       : 'APPUIE SUR LE BOUTON (OU LA CROIX) VOULU · ÉCHAP : ANNULER')
        : (etat.branchee
          ? 'ENFONCÉS : ' + (etat.boutons.length ? etat.boutons.join(' ') : '—')
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
    items.push({ libelle: 'RÉAPPRENDRE BOUTON PAR BOUTON',
                 faire: function () { ouvrirMenu(menuManetteBoutons()); return false; } });
    // Les LETTRES que l'ecran COMMANDES imprime sur les boutons. AUTO : celles
    // que le nom de la manette trahit (une PlayStation), sinon Xbox. ⚠️ Nintendo
    // ne se devine pas (`manettes.DETECTION`) : c'est ici qu'on la choisit.
    const familles = Object.keys(bloc.familles || {});
    const lettres = { libelle: 'LETTRES DES BOUTONS', faire: function () {
      const cycle = [null].concat(familles);
      const k = cycle.indexOf(B.options.lettresManette || null);
      B.options.lettresManette = cycle[(k + 1) % cycle.length];
      Sauvegarde.ecrireOptions(B.options);
      Son.SFX.menu();
      return false;
    } };
    items.push(lettres);
    items.push({ libelle: 'RETOUR', faire: function () { ouvrirMenu(menuOptions()); return false; } });
    // Le curseur commence sur la disposition en cours : appuyer sur ACTION pour
    // voir le bouton s'allumer ne change alors rien.
    const actuel = B.options.manetteProfil || bloc.defaut;
    const depart = Math.max(0, items.findIndex(function (i) { return i.profil && i.profil.slug === actuel; }));
    const menu = { titre: 'MANETTE', items: items, curseur: depart, manetteInerte: true, epaulesInertes: true,
                   largeur: 420, hauteur: 162, colonne: 212, retour: function () { ouvrirMenu(menuOptions()); } };
    menu.maj = function (m) {
      const etat = Entree.manetteInfo();
      m.sur = etat.branchee ? (etat.mapping === 'standard' ? 'RECONNUE' : 'NON RECONNUE')
                            : 'AUCUNE MANETTE';
      const choisi = B.options.manetteProfil || bloc.defaut;
      const fam = (bloc.familles || {})[Entree.familleManette()];
      lettres.detail = (B.options.lettresManette ? '' : 'AUTO · ') + (fam ? fam.nom : '?');
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
      const lignes = ['ENFONCÉS : ' + (etat.boutons.length ? etat.boutons.join(' ') : '—'),
                      inconnus.length ? 'BOUTON ' + inconnus.join(' ') + ' : PAS DANS CELLE-CI'
                        : (bit ? '8BITDO : DONGLE 2,4 GHZ = XBOX' : (etat.id || '').slice(0, 24).toUpperCase())];
      lignes.forEach(function (l, i) {
        if (l) texte(ctx, l, x + 232, y + 122 + i * 10, '#8a8698', 1);
      });
    };
    menu.maj(menu);
    return menu;
  }

  // --- COMMANDES : chaque bouton et ce qu'il fait, avec les boutons qu'on TIENT --------

  //: Demande de Martin (21 sept. 2026) : « au debut du jeu, un affichage d'aides
  //: pour que les joueurs sachent comment ca fonctionne ; si une manette est
  //: branchee, indiquer visuellement sur quel bouton peser ». L'ecran s'ouvre a
  //: la fin de l'ouverture d'une partie neuve (`Histoire`), et de PAUSE.
  //:
  //: ⚠️ IL PARLE L'APPAREIL QU'ON TIENT (`Entree.appareil`), pas « une manette
  //: est branchee » : celui qui joue au clavier avec une manette qui dort sur le
  //: bureau ne veut pas lire des A et des B. Et il change sous les yeux quand
  //: on passe de l'un a l'autre.
  //:
  //: ⚠️ LES LETTRES SUIVENT LA POSITION, JAMAIS LE NUMERO. Le A d'une manette
  //: Xbox est EN BAS ; le numero que le navigateur lui donne depend de la
  //: manette, du Bluetooth et du systeme (`manettes.py`). La disposition dit
  //: quelle PIECE du dessin porte chaque action (`pieces`), la famille dit quelle
  //: lettre est imprimee sur cette piece.

  //: Les pieces du dessin par NOM (`manettes.py`). Le stick et son clic ne sont
  //: pas dans `MANETTE_PIECES` (le stick y est dessine a part), et la croix y
  //: est en quatre morceaux : l'aide la vise en entier. Le CLIC du stick vise le
  //: bas de la cuvette : deux traits vers le meme stick (marcher, viser) se
  //: confondraient.
  const PIECES_AIDE = { stick: { x: 24, y: 26, l: 9, h: 9 }, clic: { x: 24, y: 32, l: 9, h: 4 },
                        croix: { x: 11, y: 14, l: 12, h: 12 } };
  MANETTE_PIECES.forEach(function (p) { if (p.nom && !PIECES_AIDE[p.nom]) PIECES_AIDE[p.nom] = p; });
  //: La main qui tient chaque piece : la ligne de l'aide se range de son cote,
  //: ou dessous (`m`) pour les petits boutons du milieu.
  const COTE_DES_PIECES = { gachette_g: 'g', epaule_g: 'g', croix: 'g', stick: 'g', clic: 'g',
                            select: 'm', start: 'm', centre: 'm',
                            gachette_d: 'd', epaule_d: 'd', haut: 'd', gauche: 'd', droite: 'd', bas: 'd' };
  //: Les boutons de droite portent leur lettre SUR le dessin : pas de trait.
  const FACES = { haut: true, gauche: true, droite: true, bas: true };
  //: Les gestes qui ne sont pas un bouton : le stick, la croix, les fleches.
  const DIRECTIONS_DU_GESTE = { marcher: ['haut', 'gauche', 'bas', 'droite'], tourner: ['gauche', 'droite'],
                                gaz: ['haut'], frein: ['bas'] };
  //: Ce qu'on lit sur la touche. ⚠️ Les fleches ne s'ecrivent pas (la police
  //: pixel n'a pas de « ← ») : elles se dessinent.
  const NOMS_DE_TOUCHES = { Space: 'ESPACE', ShiftLeft: 'MAJ', ShiftRight: 'MAJ', Tab: 'TAB',
                            Escape: 'ÉCHAP', Enter: 'ENTRÉE', Backspace: 'EFFACER' };
  //: Les symboles PlayStation dans le DOM du titre (la toile, elle, les dessine).
  const SYMBOLES = { croix: '✕', rond: '○', carre: '□', triangle: '△' };

  /** La disposition choisie telle que le paquet la decrit. Une disposition
      REAPPRISE bouton par bouton n'a plus de description : on garde les pieces
      de la disposition par defaut — celles du dessin de l'ecran MANETTE, qui
      fait deja cette hypothese — sauf VISER, que rien ne situe. */
  function dispositionDecrite() {
    const bloc = B.defs.manettes || { profils: [] };
    const slug = B.options.manetteProfil || bloc.defaut;
    const p = bloc.profils.find(function (q) { return q.slug === slug; });
    if (p) return p;
    const defaut = bloc.profils.find(function (q) { return q.slug === bloc.defaut; });
    return defaut ? { slug: 'apprise', pieces: Object.assign({}, defaut.pieces, { verrouiller: [null] }) } : null;
  }

  function familleCourante() {
    const bloc = B.defs.manettes || {};
    return (bloc.familles || {})[Entree.familleManette()] || null;
  }

  function toucheLibelle(code) {
    if (/^Arrow/.test(code)) return null;
    return NOMS_DE_TOUCHES[code] || code.replace(/^Key|^Digit/, '');
  }

  /** La premiere touche de `a` d'un genre (`Key`, `Arrow`) dans `MAP_TOUCHES`. */
  function toucheDe(a, genre) {
    return (Entree.MAP_TOUCHES[a] || []).find(function (k) { return k.indexOf(genre) === 0; }) || null;
  }

  // Les glyphes : ce qui se dessine a la place du nom d'un bouton. Chacun sait
  // s'il est enfonce (`allume`) : on appuie, il s'allume, et sa ligne avec lui.

  function glypheDePiece(nom, fam, indice, etat) {
    const b = nom && fam && fam.boutons[nom];
    const allume = nom === 'gachette_d' ? function () { return Entree.gaz > 0.15; }
      : nom === 'gachette_g' ? function () { return Entree.frein > 0.15; }
      : function () { return indice !== undefined && etat.boutons.indexOf(indice) >= 0; };
    if (b) return { s: 'bouton', texte: b.texte, forme: b.forme, couleur: b.couleur, piece: nom, allume: allume };
    return { s: 'numero', texte: 'BOUTON ' + indice, piece: null, allume: allume };
  }

  function icone(nom, allume, vers) { return { s: 'icone', icone: nom, vers: vers || null, allume: allume }; }

  function stickPousse() { return Entree.axe.source === 'manette' && Entree.axe.mag > 0; }
  function croixTenue() { return ['haut', 'bas', 'gauche', 'droite'].some(function (a) { return Entree.bas(a); }); }
  function poucePose() { return Entree.axe.source === 'tactile' && Entree.axe.mag > 0; }

  /** Une ligne de l'aide, pour un appareil : ses glyphes et, a la manette, les
      pieces du dessin qu'elle designe. `null` : cet appareil ne le fait pas. */
  function ligneDAide(c, appareil, page, fam, etat) {
    if (appareil === 'manette') {
      if (c === 'marcher') return { glyphes: [icone('stick', stickPousse), icone('croix', croixTenue)], pieces: ['stick', 'croix'] };
      if (c === 'tourner') return { glyphes: [icone('stick', stickPousse)], pieces: ['stick'] };
      if (c === 'gaz' || c === 'frein') {
        const nom = c === 'gaz' ? 'gachette_d' : 'gachette_g';
        return { glyphes: [glypheDePiece(nom, fam, undefined, etat)], pieces: [nom] };
      }
      const indices = Entree.profilManette().boutons[c] || [];
      if (!indices.length) return null;
      const decrite = dispositionDecrite();
      const pieces = indices.map(function (_, k) { return (decrite && decrite.pieces[c] && decrite.pieces[c][k]) || null; });
      return { glyphes: indices.map(function (i, k) { return glypheDePiece(pieces[k], fam, i, etat); }), pieces: pieces };
    }
    if (appareil === 'clavier') {
      const dirs = DIRECTIONS_DU_GESTE[c];
      const codes = dirs
        ? dirs.map(function (d) { return toucheDe(d, 'Key'); }).concat([null], dirs.map(function (d) { return toucheDe(d, 'Arrow'); }))
        : [(Entree.MAP_TOUCHES[c] || [])[0]].filter(Boolean);
      if (!codes.length) return null;
      return { glyphes: codes.map(function (code) {
        return code ? { s: 'touche', code: code, allume: function () { return Entree.toucheEnfoncee(code); } } : { s: 'espace' };
      }) };
    }
    // Le doigt : le pouce, et les quatre boutons sous leur nom du moment.
    const vers = { marcher: null, tourner: 'cote', gaz: 'haut', frein: 'bas' };
    if (c in vers) return { glyphes: [icone('pouce', poucePose, vers[c])], cible: 'croix' };
    if (c === 'pause') return { glyphes: [icone('pause', function () { return Entree.basTactile('pause'); })], cible: 'pause' };
    const noms = Entree.etiquettesTactiles(page === 'volant' ? 'vehicule' : 'pied');
    if (!noms[c]) return null;
    return { glyphes: [{ s: 'doigt', texte: noms[c], allume: function () { return Entree.basTactile(c); } }], cible: c };
  }

  /** Les lignes d'une page pour l'appareil qu'on tient. */
  function lignesDAide(page, appareil) {
    const fam = familleCourante(), etat = Entree.manetteInfo();
    const out = [];
    for (const l of page.lignes) {
      const li = ligneDAide(l.c, appareil, page.slug, fam, etat);
      if (!li) continue;
      li.c = l.c; li.texte = l.texte;
      li.allume = li.glyphes.some(function (g) { return g.allume && g.allume(); });
      out.push(li);
    }
    return out;
  }

  /** Le glyphe de l'action `a` pour l'appareil qu'on tient — `null` au doigt,
      ou le nom ecrit sur le bouton EST deja « ACTION ». */
  function glypheDAction(a) {
    const appareil = Entree.appareil;
    if (appareil === 'tactile') return null;
    const li = ligneDAide(a, appareil, 'pied', familleCourante(), Entree.manetteInfo());
    return li && li.glyphes[0] ? li.glyphes[0] : null;
  }

  // --- Le dessin des glyphes (9 pixels de haut) ---

  function largeurGlyphe(g) {
    if (g.s === 'espace') return 4;
    if (g.s === 'icone') return 9;
    if (g.s === 'bouton' && (g.forme || String(g.texte).length === 1)) return 9;
    if (g.s === 'touche') {
      const lib = toucheLibelle(g.code);
      return lib ? Math.max(9, Atlas.largeurTexte(lib, 1) + 6) : 9;
    }
    return Atlas.largeurTexte(g.texte, 1) + 6;
  }

  /** Un rond de `d` pixels (9 ou 15), coins coupes. */
  function rond(ctx, x, y, d, couleur) {
    const c = d >= 15 ? 3 : 2;
    ctx.fillStyle = couleur;
    ctx.fillRect(x + c, y, d - 2 * c, d);
    ctx.fillRect(x, y + c, d, d - 2 * c);
    ctx.fillRect(x + 1, y + 1, d - 2, d - 2);
    B.stats.rects += 3;
  }

  //: Les quatre symboles PlayStation, 5 x 5 (`manettes.FORMES`).
  const FORMES_DE_BOUTON = {
    croix: ['10001', '01010', '00100', '01010', '10001'],
    rond: ['01110', '10001', '10001', '10001', '01110'],
    carre: ['11111', '10001', '10001', '10001', '11111'],
    triangle: ['00100', '01010', '01010', '10001', '11111'],
  };

  function forme(ctx, nom, x, y, couleur, e) {
    const g = FORMES_DE_BOUTON[nom];
    if (!g) return;
    ctx.fillStyle = couleur;
    for (let j = 0; j < 5; j++) for (let i = 0; i < 5; i++) {
      if (g[j][i] === '1') { ctx.fillRect(x + i * e, y + j * e, e, e); B.stats.rects++; }
    }
  }

  /** Un triangle plein de trois rangs, pointe vers `sens` : une fleche de touche. */
  function pointe(ctx, cx, cy, sens, couleur) {
    ctx.fillStyle = couleur;
    for (let i = 0; i < 3; i++) {
      const larg = 1 + i * 2;
      if (sens === 'haut') ctx.fillRect(cx - i, cy - 1 + i, larg, 1);
      else if (sens === 'bas') ctx.fillRect(cx - i, cy + 1 - i, larg, 1);
      else if (sens === 'gauche') ctx.fillRect(cx - 1 + i, cy - i, 1, larg);
      else ctx.fillRect(cx + 1 - i, cy - i, 1, larg);
    }
    B.stats.rects += 3;
  }

  const SENS_DES_FLECHES = { ArrowUp: 'haut', ArrowDown: 'bas', ArrowLeft: 'gauche', ArrowRight: 'droite' };

  function dessinerGlyphe(ctx, g, x, y) {
    const l = largeurGlyphe(g), allume = !!(g.allume && g.allume());
    function r(a, b, w, h, c) { ctx.fillStyle = c; ctx.fillRect(x + a, y + b, w, h); B.stats.rects++; }
    if (g.s === 'espace') return l;
    if (g.s === 'touche') {
      // Une touche : son dessus, et l'ombre de son flanc dessous.
      r(0, 1, l, 8, '#15141c');
      r(0, 0, l, 8, allume ? '#e8b33c' : '#8a8698');
      r(1, 1, l - 2, 6, allume ? '#f2cf72' : '#efe6d0');
      const lib = toucheLibelle(g.code);
      if (lib) Atlas.texte(ctx, lib, x + 3, y + 1, '#22242a', 1);
      else pointe(ctx, x + 4, y + 4, SENS_DES_FLECHES[g.code], '#22242a');
      return l;
    }
    if (g.s === 'icone') {
      if (g.icone === 'croix') {
        r(3, 0, 3, 9, allume ? '#e8b33c' : '#6f757c'); r(0, 3, 9, 3, allume ? '#e8b33c' : '#6f757c');
        r(4, 4, 1, 1, '#22242a');
        return l;
      }
      if (g.icone === 'pause') {
        rond(ctx, x, y, 9, allume ? '#e8b33c' : '#2a2440');
        r(2, 2, 2, 5, '#efe6d0'); r(5, 2, 2, 5, '#efe6d0');
        return l;
      }
      // Le stick de la manette, ou le pouce sur la vitre : un rond, et sa tete
      // poussee du cote ou le geste la pousse.
      rond(ctx, x, y, 9, g.icone === 'pouce' ? '#2a2440' : '#22242a');
      const dy = g.vers === 'haut' ? -2 : g.vers === 'bas' ? 2 : 0;
      r(3, 3 + dy, 3, 3, allume ? '#e8b33c' : (g.icone === 'pouce' ? '#b89a4a' : '#8a8698'));
      if (g.vers === 'cote') { r(0, 4, 1, 1, '#efe6d0'); r(8, 4, 1, 1, '#efe6d0'); }
      return l;
    }
    if (g.s === 'bouton' && l === 9) {
      rond(ctx, x, y, 9, allume ? '#e8b33c' : '#22242a');
      const c = allume ? '#22242a' : g.couleur;
      if (g.forme) forme(ctx, g.forme, x + 2, y + 2, c, 1);
      else Atlas.texte(ctx, g.texte, x + 3, y + 2, c, 1);
      return l;
    }
    // Une pastille : un bouton au nom long (LB, SELECT), un numero, un bouton tactile.
    const fond = allume ? '#e8b33c' : g.s === 'doigt' ? '#2a2440' : '#3a3d44';
    r(1, 0, l - 2, 9, fond); r(0, 1, l, 7, fond);
    if (g.s === 'doigt' && !allume) { r(1, 0, l - 2, 1, '#6b5a2e'); r(1, 8, l - 2, 1, '#6b5a2e'); }
    Atlas.texte(ctx, g.texte, x + 3, y + 2, allume ? '#22242a' : '#efe6d0', 1);
    return l;
  }

  function largeurLigne(li) {
    let l = 0;
    for (const g of li.glyphes) l += largeurGlyphe(g) + 2;
    return l + 1 + Atlas.largeurTexte(li.texte, 1);
  }

  function dessinerLigne(ctx, li, x, y, nom) {
    let cx = x;
    for (const g of li.glyphes) cx += dessinerGlyphe(ctx, g, cx, y) + 2;
    texte(ctx, li.texte, cx + 1, y + 2, li.allume ? '#e8b33c' : '#efe6d0', 1);
    // Chaque ligne est une ancre : le juge tactile verifie qu'aucune ne finit
    // sous un pouce (le telephone en paysage, ou les boutons sont grands).
    // Le pied du classeur a les siennes (`pied`).
    noter(nom || 'commandes', x, y, largeurLigne(li), 9);
  }

  /** Des lignes rangees d'un cote, chacune a la hauteur de ce qu'elle designe
      (`cible`), ou juste dessous si la place est prise — ou juste AU-DESSUS
      (`versLeHaut`), pour que rien ne descende plus bas que sa cible. Rend ses
      TRAITS : un par bout vise (`bouts`), avec sa gouttiere.

      ⚠️ Deux traits dans la meme gouttiere se confondraient : chacun a la
      sienne, le plus haut le plus loin du dessin — ainsi aucun coude ne coupe
      le trait d'un autre. */
  function rangerDUnCote(lignes, cote, bord, yMin, versLeHaut) {
    lignes.sort(function (a, b) { return a.cible.y - b.cible.y; });
    if (versLeHaut) {
      let dessus = Infinity;
      for (let k = lignes.length - 1; k >= 0; k--) {
        lignes[k].y = Math.min(Math.round(lignes[k].cible.y) - 4, dessus - 13); dessus = lignes[k].y;
      }
    } else {
      let dessous = yMin - 13;
      for (const li of lignes) { li.y = Math.max(Math.round(li.cible.y) - 4, dessous + 13); dessous = li.y; }
    }
    for (const li of lignes) li.x = cote === 'g' ? bord - 20 - largeurLigne(li) : bord + 20;
    const traits = [];
    for (const li of lignes) for (const b of li.bouts || []) traits.push({ li: li, b: b });
    traits.sort(function (a, b) { return a.b.y - b.b.y; });
    const sens = cote === 'g' ? -1 : 1;
    traits.forEach(function (t, k) {
      t.gx = bord + sens * (5 + 3 * (traits.length - 1 - k));
      t.depart = cote === 'g' ? t.li.x + largeurLigne(t.li) + 2 : t.li.x - 2;
    });
    return traits;
  }

  /** Les traits, PAR-DESSUS le dessin : ils arrivent au bord du bouton vise,
      et un point s'y pose. Coude a coude : la ligne, la gouttiere, le bouton.
      ⚠️ Traces sous le dessin, ils s'arretaient au bord de la manette, a la
      hauteur du bouton — on ne savait pas lequel (vu a la capture). */
  function tracer(ctx, traits) {
    for (const t of traits) {
      const ym = t.li.y + 4, xc = t.b.x, yc = t.b.y;
      ctx.fillStyle = t.li.allume ? '#e8b33c' : '#8a8698';
      if (t.gx === undefined) {                                // tout droit, a la verticale
        ctx.fillRect(xc, Math.min(ym, yc), 1, Math.abs(yc - ym) + 1);
        ctx.fillRect(Math.min(xc, t.depart), ym, Math.abs(t.depart - xc) + 1, 1);
      } else {
        ctx.fillRect(Math.min(t.depart, t.gx), ym, Math.abs(t.gx - t.depart) + 1, 1);
        ctx.fillRect(t.gx, Math.min(ym, yc), 1, Math.abs(yc - ym) + 1);
        ctx.fillRect(Math.min(t.gx, xc), yc, Math.abs(xc - t.gx) + 1, 1);
      }
      ctx.fillRect(xc - 1, yc - 1, 3, 3);
      B.stats.rects += 4;
    }
  }

  /** Les lignes du milieu (SELECT, START) : sous le dessin, de part et d'autre
      de leur bouton, avec un trait qui monte au bouton. */
  function rangerDessous(lignes, y) {
    const traits = [];
    const avecCible = lignes.filter(function (li) { return li.cible; })
      .sort(function (a, b) { return a.cible.x - b.cible.x; });
    avecCible.forEach(function (li, k) {
      const gauche = k === 0 && avecCible.length > 1;
      li.y = y;
      li.x = gauche ? li.cible.x - 8 - largeurLigne(li) : li.cible.x + 8;
      traits.push({ li: li, b: li.bouts[0] || li.cible,
                    depart: gauche ? li.x + largeurLigne(li) + 2 : li.x - 2 });
    });
    // Un bouton que rien ne situe (VISER sur une 8BitDo en DirectInput) : son
    // numero, sous les autres, sans trait — il n'a nulle part ou pointer.
    lignes.filter(function (li) { return !li.cible; }).forEach(function (li, k) {
      li.y = y + 14 + k * 12;
      li.x = Math.round((VW - largeurLigne(li)) / 2);
    });
    return traits;
  }

  function dessinerCommandesManette(ctx, lignes, x, y, l) {
    const ech = 3;
    const ox = x + Math.round((l - MANETTE_L * ech) / 2), oy = y + 32;
    function centre(nom) {
      const p = PIECES_AIDE[nom];
      return p ? { x: ox + Math.round((p.x + p.l / 2) * ech), y: oy + Math.round((p.y + p.h / 2) * ech) } : null;
    }
    /** Le bord du bouton qui fait face a sa ligne : a gauche, a droite, ou dessous. */
    function bord(nom, cote) {
      const p = PIECES_AIDE[nom], c = centre(nom);
      if (cote === 'g') return { x: ox + p.x * ech - 1, y: c.y };
      if (cote === 'd') return { x: ox + (p.x + p.l) * ech, y: c.y };
      return { x: c.x, y: oy + (p.y + p.h) * ech };
    }
    const cotes = { g: [], d: [], m: [] };
    for (const li of lignes) {
      const p = li.pieces[0], cote = (p && COTE_DES_PIECES[p]) || 'm';
      li.cible = p ? centre(p) : null;
      // Un trait vers chaque bouton de SON cote — pas vers les boutons de
      // droite, qui portent leur lettre sur le dessin.
      li.bouts = li.pieces.filter(function (q) { return q && COTE_DES_PIECES[q] === cote && !FACES[q]; })
        .map(function (q) { return bord(q, cote); });
      cotes[cote].push(li);
    }
    const traits = rangerDUnCote(cotes.g, 'g', ox, oy - 2)
      .concat(rangerDUnCote(cotes.d, 'd', ox + MANETTE_L * ech, oy - 2))
      .concat(rangerDessous(cotes.m, oy + MANETTE_H * ech + 4));
    const etat = Entree.manetteInfo(), profil = Entree.profilManette(), fam = familleCourante();
    dessinerManette(ctx, ox, oy, ech, profil, etat);
    // Les lettres, imprimees sur le dessin comme sur la manette.
    if (fam) {
      for (const p of MANETTE_PIECES) {
        const b = fam.boutons[p.nom];
        if (!b || p.nom === 'select' || p.nom === 'start') continue;
        const px = ox + p.x * ech, py = oy + p.y * ech, pl = p.l * ech, ph = p.h * ech;
        const tenue = pieceEnfoncee(p, profil, etat);
        if (FACES[p.nom]) {
          ctx.fillStyle = '#3a3d44'; ctx.fillRect(px, py, pl, ph);
          rond(ctx, px, py, 15, tenue ? '#e8b33c' : '#22242a');
          const c = tenue ? '#22242a' : b.couleur;
          if (b.forme) forme(ctx, b.forme, px + 3, py + 3, c, 2);
          else Atlas.texte(ctx, b.texte, px + 5, py + 3, c, 2);
        } else {
          Atlas.texte(ctx, b.texte, px + Math.round((pl - Atlas.largeurTexte(b.texte, 1)) / 2),
                      py + Math.round((ph - 5) / 2), tenue ? '#22242a' : '#15141c', 1);
        }
      }
    }
    tracer(ctx, traits);
    for (const li of lignes) dessinerLigne(ctx, li, li.x, li.y);
  }

  function dessinerCommandesClavier(ctx, lignes, x, y, l) {
    // Deux colonnes : le geste d'abord (marcher, conduire), puis les boutons.
    const moitie = Math.ceil(lignes.length / 2);
    lignes.forEach(function (li, k) {
      const col = k < moitie ? 0 : 1, rang = col ? k - moitie : k;
      dessinerLigne(ctx, li, x + 22 + col * Math.round(l / 2), y + 44 + rang * 20);
    });
  }

  //: Le plan de l'ecran tactile, en petit : ou sont le pouce et les boutons.
  //: L'ordre suit `styles.css` (`#croix`, `#boutons`, `#haut`) ; les hauteurs,
  //: elles, sont choisies pour qu'AUCUN trait ne passe sur un autre bouton — a
  //: la capture, celui de SPRINT traversait FRAPPE. Le plein ecran n'y est pas :
  //: l'aide dit comment jouer, pas comment regler la fenetre.
  const PLAN_TACTILE = { l: 184, h: 104,
    croix: { x: 24, y: 80, r: 15 },
    arme: { x: 164, y: 52, r: 7 }, action: { x: 136, y: 64, r: 8 },
    attaque: { x: 164, y: 80, r: 9 }, esquive: { x: 134, y: 94, r: 7 },
    pause: { x: 170, y: 10, r: 5 } };

  function disque(ctx, cx, cy, r, couleur) {
    ctx.fillStyle = couleur;
    for (let dy = -r; dy <= r; dy++) {
      const w = Math.floor(Math.sqrt(r * r - dy * dy));
      ctx.fillRect(cx - w, cy + dy, 2 * w + 1, 1);
    }
    B.stats.rects += 2 * r + 1;
  }

  function dessinerCommandesTactile(ctx, lignes, x, y) {
    const P = PLAN_TACTILE;
    // ⚠️ DECALE A GAUCHE, pas centre : sur un telephone en paysage, les quatre
    // boutons couvrent le coin en bas a droite de l'ecran — centre, le plan
    // poussait FRAPPE et SPRINT dessous (vu a la capture, 844 x 390).
    const ox = x + 92, oy = y + 36;
    const gauche = [], droite = [];
    for (const li of lignes) {
      const c = P[li.cible], aGauche = c.x < P.l / 2;
      li.cible = { x: ox + c.x, y: oy + c.y };
      li.bouts = [{ x: li.cible.x + (aGauche ? -c.r - 1 : c.r + 1), y: li.cible.y }];
      (aGauche ? gauche : droite).push(li);
    }
    // ⚠️ Les lignes du pouce s'empilent VERS LE HAUT : au volant il y en a
    // trois, et vers le bas elles tombaient dans le cercle du vrai joystick.
    const traits = rangerDUnCote(gauche, 'g', ox - 3, oy, true).concat(rangerDUnCote(droite, 'd', ox + P.l + 3, oy));
    // L'ecran du telephone, couche.
    ctx.fillStyle = '#8a8698'; ctx.fillRect(ox - 2, oy - 2, P.l + 4, P.h + 4);
    ctx.fillStyle = '#15141c'; ctx.fillRect(ox, oy, P.l, P.h);
    B.stats.rects += 2;
    for (const nom of ['croix', 'attaque', 'action', 'esquive', 'arme']) {
      const c = P[nom];
      const tenu = nom === 'croix' ? poucePose() : Entree.basTactile(nom);
      disque(ctx, ox + c.x, oy + c.y, c.r, tenu ? '#e8b33c' : '#3a3450');
    }
    disque(ctx, ox + P.croix.x, oy + P.croix.y, 6, '#6b5a2e');
    const c = P.pause;
    ctx.fillStyle = Entree.basTactile('pause') ? '#e8b33c' : '#3a3450';
    ctx.fillRect(ox + c.x - c.r, oy + c.y - c.r, 2 * c.r + 1, 2 * c.r + 1);
    ctx.fillStyle = '#efe6d0';
    ctx.fillRect(ox + c.x - 2, oy + c.y - 2, 1, 5); ctx.fillRect(ox + c.x + 2, oy + c.y - 2, 1, 5);
    B.stats.rects += 3;
    tracer(ctx, traits);
    for (const li of lignes) dessinerLigne(ctx, li, li.x, li.y);
  }

  /** Les onglets, en haut a droite : la page qu'on lit en or. `aGauche` : dans
      le classeur, a gauche — en haut a droite, au telephone, c'est le bouton
      PAUSE qui les couvrait. Chacun se touche (`page`). */
  function dessinerOnglets(ctx, pages, courante, x, y, l, aGauche) {
    const noms = pages.map(function (p) { return p.titre; });
    const total = noms.reduce(function (s, n) { return s + Atlas.largeurTexte(n, 1) + 12; }, 0);
    let cx = aGauche ? x + 2 : x + l - 8 - total;
    noms.forEach(function (n, k) {
      const w = Atlas.largeurTexte(n, 1);
      const la = k === courante;
      texte(ctx, n, cx + 6, y + 10, la ? '#e8b33c' : '#6a6678', 1);
      if (la) { ctx.fillStyle = '#e8b33c'; ctx.fillRect(cx + 6, y + 17, w, 1); B.stats.rects++; }
      poserCible({ x: cx, y: y + 5, l: w + 12, h: 14, page: k });
      cx += w + 12;
    });
  }

  /** Le pied de l'ecran : le bouton qui ferme, et celui qui tourne la page —
      dessines tous les deux pour l'appareil qu'on tient. */
  function dessinerPiedDesCommandes(ctx, m, appareil, x, y, l, h) {
    const lignes = [];
    const fermer = glypheDAction('action')
      || { s: 'doigt', texte: Entree.etiquettesTactiles('menu').action, allume: function () { return Entree.basTactile('action'); } };
    lignes.push({ glyphes: [fermer], texte: m.items[0].libelle });
    const tourner = appareil === 'manette' ? [icone('croix', croixTenue)]
      : appareil === 'clavier' ? [{ s: 'touche', code: 'ArrowLeft', allume: function () { return Entree.toucheEnfoncee('ArrowLeft'); } },
                                  { s: 'touche', code: 'ArrowRight', allume: function () { return Entree.toucheEnfoncee('ArrowRight'); } }]
      : [icone('pouce', poucePose, 'cote')];
    lignes.push({ glyphes: tourner, texte: 'L\'AUTRE PAGE' });
    const total = largeurLigne(lignes[0]) + 16 + largeurLigne(lignes[1]);
    let cx = x + Math.round((l - total) / 2);
    const yy = y + h - 15;
    lignes.forEach(function (li) { dessinerLigne(ctx, li, cx, yy); cx += largeurLigne(li) + 16; });
  }

  function dessinerCommandes(ctx, m, x, y, l, h) {
    const pages = (B.defs.manettes && B.defs.manettes.pages) || [];
    const page = pages[m.page];
    if (!page) return;
    const appareil = Entree.appareil;
    // Dans le classeur, la rangee d'onglets tient le haut : les deux pages se
    // lisent dessous, a droite, sur la ligne du titre — et le pied est celui du
    // classeur (`menu.pied`).
    dessinerOnglets(ctx, pages, m.page, x, m.classeur ? y + 4 : y, l, !!m.classeur);
    const lignes = lignesDAide(page, appareil);
    if (appareil === 'manette') dessinerCommandesManette(ctx, lignes, x, y, l);
    else if (appareil === 'clavier') dessinerCommandesClavier(ctx, lignes, x, y, l);
    else dessinerCommandesTactile(ctx, lignes, x, y);
    if (!m.classeur) dessinerPiedDesCommandes(ctx, m, appareil, x, y, l, h);
  }

  /** L'ecran COMMANDES. `depuisPause` : c'est l'onglet COMMANDES du classeur ;
      sinon (le debut d'une partie) un ecran seul, qui rend la ville.

      ⚠️ C'est un MENU : la ville est figee pendant qu'on lit — personne ne se
      fait renverser en apprenant ou est le frein. Et comme l'ecran MANETTE, la
      manette y ALLUME ce qu'on appuie sans rien fermer (`manetteInerte`) :
      seul ACTION ferme, c'est ce que dit le pied de l'ecran. Sinon on le
      fermerait en essayant le premier bouton. */
  function menuCommandes(depuisPause) {
    const pages = (B.defs.manettes && B.defs.manettes.pages) || [];
    const j = B.joueur;
    const menu = {
      titre: 'COMMANDES', sansListe: true, manetteInerte: true, largeur: 476, hauteur: 210, curseur: 0,
      page: j && j.dansVehicule && !j.passager ? Math.max(0, pages.findIndex(function (p) { return p.slug === 'volant'; })) : 0,
      // Fermer le dernier menu d'une pause, c'est reprendre (`Jeu.maj`).
      items: [{ libelle: depuisPause ? 'REPRENDRE' : 'C\'EST PARTI', faire: function () { return true; } }],
    };
    if (depuisPause) {
      enOnglet('commandes', menu);
      // Le pied du classeur, a la mode de celui de l'ecran seul : le bouton qui
      // tourne la page, celui qui rend la ville.
      menu.pied = function () {
        const appareil = Entree.appareil;
        const tourner = appareil === 'manette' ? [icone('croix', croixTenue)]
          : appareil === 'clavier' ? [glypheDeTouche('ArrowUp'), glypheDeTouche('ArrowDown')]
          : [icone('pouce', poucePose, 'haut')];
        const fermer = glypheDAction('action')
          || { s: 'doigt', texte: Entree.etiquettesTactiles('menu').action, allume: function () { return Entree.basTactile('action'); } };
        return [{ glyphes: tourner, texte: 'L\'AUTRE PAGE' }, { glyphes: [fermer], texte: 'REPRENDRE' }];
      };
    }
    menu.maj = function (m) {
      // Tourner la page : la croix, les fleches, le pouce.
      // ⚠️ PAS LE STICK : on le pousse pour voir MARCHER s'allumer, et la page
      // tournait sous le pouce (vu au banc). Le pied de l'ecran dit la croix.
      // ⚠️ Dans le classeur, gauche et droite tournent l'ONGLET : la page, elle,
      // se tourne en haut et en bas (il n'y a pas de liste ou promener un curseur).
      const sens = depuisPause ? (Entree.neuf('haut') ? -1 : Entree.neuf('bas') ? 1 : 0)
        : (Entree.neuf('gauche') ? -1 : Entree.neuf('droite') ? 1 : 0);
      if (sens && pages.length > 1) { m.page = (m.page + sens + pages.length) % pages.length; Son.SFX.menu(); }
      // La boite a la hauteur de ce qu'elle montre : le dessin de la manette
      // (et une ligne de plus pour un bouton que rien ne situe), deux colonnes
      // de touches, ou le plan de l'ecran tactile.
      const appareil = Entree.appareil;
      const numero = appareil === 'manette' && pages[m.page]
        && lignesDAide(pages[m.page], 'manette').some(function (li) { return !li.pieces[0]; });
      m.hauteur = appareil === 'manette' ? 210 + (numero ? 14 : 0) : appareil === 'clavier' ? 160 : 170;
    };
    menu.dessiner = function (ctx, x, y, l, h) { dessinerCommandes(ctx, menu, x, y, l, h); };
    return menu;
  }

  function ouvrirCommandes() { ouvrirMenu(menuCommandes(false)); }

  //: La ligne du titre suit l'appareil : une manette y lit SES boutons, pas WASD.
  let aideDuTitre = null;
  function majAideDuTitre() {
    if (!doc) return;
    const appareil = Entree.appareil, famille = appareil === 'manette' ? Entree.familleManette() : '';
    const cle = appareil + '/' + famille;
    if (cle === aideDuTitre) return;
    aideDuTitre = cle;
    const clavier = doc.getElementById('aide-clavier'), manette = doc.getElementById('aide-manette');
    if (!clavier || !manette) return;
    clavier.hidden = appareil === 'manette';
    manette.hidden = appareil !== 'manette';
    const fam = ((B.defs && B.defs.manettes && B.defs.manettes.familles) || {})[famille];
    if (!fam) return;
    const nom = function (piece) { const b = fam.boutons[piece]; return b ? (b.texte || SYMBOLES[b.forme] || '') : ''; };
    const decrite = dispositionDecrite();
    const pieceDe = function (a) { return (decrite && decrite.pieces[a] && decrite.pieces[a][0]) || null; };
    const jouer = doc.getElementById('aide-manette-jouer'), pause = doc.getElementById('aide-manette-pause');
    if (jouer) jouer.textContent = nom(pieceDe('action'));
    if (pause) pause.textContent = nom(pieceDe('pause'));
  }

  /** Le bilan de la session : ce qu'on a fait depuis le debut. */
  function menuBilan() {
    const p = B.partie, s = p.stats;
    const minutes = Math.floor((s.secondes || 0) / 60);
    const fortune = p.argent + (p.planque.coffre || 0);
    const lignes = [
      ['JOUR ' + p.jour + ' · ' + minutes + ' MIN JOUÉES', ''],
      ['FORTUNE', fortune + ' $'],
      ['PROPRIÉTÉS', Object.keys(p.proprietes).length + ' / ' + B.defs.economie.proprietes.filter(function (q) { return q.phase === 1; }).length],
      ['PAQUETS', Object.keys(p.paquets).length + ' / ' + (Monde.carte.ville ? Monde.carte.ville : Monde.carte).def.paquets.length],
      ['CRIMES', String(s.crimes || 0)],
      ['CHARS VOLÉS', String(s.volees || 0)],
      ['COURSES DE TAXI', String(s.courses || 0)],
      ['MORTS', String(s.tues || 0)],
      ['HOSPITALISATIONS', String(s.hospitalisations || 0)],
    ];
    return enOnglet('bilan', { titre: 'BILAN', items: lignes.map(function (l) { return { libelle: l[0], detail: l[1], actif: false }; }) });
  }

  // --- Les parties : trois emplacements, au titre ------------------------------------

  const MOIS = ['JANV.', 'FÉVR.', 'MARS', 'AVR.', 'MAI', 'JUIN', 'JUIL.', 'AOÛT', 'SEPT.', 'OCT.', 'NOV.', 'DÉC.'];

  /** « 3 H 20 », « 25 MIN » : le temps passe DANS la partie. */
  function tempsDeJeu(secondes) {
    const min = Math.floor((secondes || 0) / 60);
    return min >= 60 ? Math.floor(min / 60) + ' H ' + String(min % 60).padStart(2, '0') : min + ' MIN';
  }

  /** « AUJOURD'HUI A 21 H 40 », « HIER A 8 H 05 », « LE 14 SEPT. A 21 H 40 ». */
  function quand(ms, maintenant) {
    const d = new Date(ms), m = new Date(maintenant);
    const heure = d.getHours() + ' H ' + String(d.getMinutes()).padStart(2, '0');
    const meme = function (a, b) { return a.getFullYear() === b.getFullYear() && a.getMonth() === b.getMonth() && a.getDate() === b.getDate(); };
    if (meme(d, m)) return 'AUJOURD\'HUI À ' + heure;
    if (meme(d, new Date(m.getFullYear(), m.getMonth(), m.getDate() - 1))) return 'HIER À ' + heure;
    return 'LE ' + d.getDate() + ' ' + MOIS[d.getMonth()] + ' À ' + heure;
  }

  /** Une ligne d'emplacement : « 1  JOUR 12 · 4300 $ », ou `vide` s'il n'y a rien. */
  function ligneEmplacement(n, a, vide) {
    return n + '  ' + (a ? 'JOUR ' + a.jour + ' · ' + a.argent + ' $' : vide);
  }

  function apercus() {
    const out = [];
    for (let n = 1; n <= Sauvegarde.EMPLACEMENTS; n++) out.push(Sauvegarde.apercu(n));
    return out;
  }

  /** Revenir au titre depuis le choix des parties. */
  function fermerParties() { fermerMenu(); voile('titre'); }

  /** LE CHOIX DES PARTIES. ACTION sur un emplacement le JOUE — sa partie, ou une
      neuve s'il est vide : continuer, c'est deux ACTION depuis le titre, le
      curseur attend deja sur la derniere partie jouee.

      ⚠️ Effacer et copier sont des LIGNES du menu, pas un bouton de plus sur
      l'emplacement : un geste que l'ecran ne nomme pas n'existe pas pour celui
      qui tient la manette. */
  function menuParties(curseur) {
    const liste = apercus();
    const pleins = liste.filter(Boolean).length;
    const actif = Sauvegarde.emplacement();
    const items = liste.map(function (a, i) {
      const n = i + 1;
      // ⚠️ DEUX VERSIONS NE SE JOUENT PAS D'UN COUP (M14) : jouer celle d'ici
      // ferait monter la sienne par-dessus celle de l'autre appareil dix
      // secondes plus tard — la partie du telephone perdue sans un mot.
      const deux = Compte.decision(n) === 'trancher';
      return { libelle: ligneEmplacement(n, a, 'NOUVELLE PARTIE'),
               detail: deux ? 'DEUX VERSIONS' : (a ? tempsDeJeu(a.secondes) : ''), emplacement: n,
               faire: function () {
                 if (deux) { ouvrirMenu(menuVersions(n)); return false; }
                 Jeu.jouerPartie(n);
                 return false;
               } };
    });
    items.push({ libelle: 'COPIER UNE PARTIE', actif: pleins > 0, faire: function () { ouvrirMenu(menuCopier()); return false; } });
    items.push({ libelle: 'EFFACER UNE PARTIE', actif: pleins > 0, faire: function () { ouvrirMenu(menuEffacer()); return false; } });
    items.push({ libelle: 'RETOUR', faire: function () { fermerParties(); return false; } });
    if (typeof curseur !== 'number') {
      // La derniere partie jouee ; si elle n'est plus la, la premiere qui reste.
      curseur = liste[actif - 1] ? actif - 1 : Math.max(0, liste.findIndex(Boolean));
    }
    const menu = { titre: 'PARTIES', items: items, curseur: curseur, retour: fermerParties,
      // Ce que la ligne ne dit pas faute de place : quand, et ou l'on en est.
      maj: function (m) {
        const item = m.items[m.curseur];
        const a = item && item.emplacement ? liste[item.emplacement - 1] : null;
        m.aide = !item || !item.emplacement ? 'FRAPPE : RETOUR AU TITRE'
          : Compte.decision(item.emplacement) === 'trancher' ? 'UNE AUTRE VERSION DORT SUR TON COMPTE — ACTION POUR CHOISIR'
          : !a ? 'UNE PARTIE NEUVE COMMENCE ICI'
          : (a.sauveeLe ? 'SAUVÉE ' + quand(a.sauveeLe, Date.now()) + ' · ' : '')
            + a.missions + (a.missions > 1 ? ' MISSIONS' : ' MISSION');
      } };
    menu.maj(menu);
    return menu;
  }

  /** DEUX VERSIONS DE LA MEME CASE (M14). On a joue ici, et ailleurs, sans que
      les deux se soient parle : le serveur ne fusionne rien et le jeu non plus —
      c'est le joueur qui tranche, une fois, en voyant les deux.

      ⚠️ Le curseur s'ouvre sur CELLE DU COMPTE quand elle est plus avancee : on
      arrive ici surtout en s'asseyant a l'ordi apres avoir joue au telephone. */
  function menuVersions(n) {
    const c = Compte.conflit(n) || {};
    const ici = Sauvegarde.apercu(n), la = c.serveur || null;
    const dire = function (a) { return a ? 'JOUR ' + a.jour + ' · ' + a.argent + ' $ · ' + tempsDeJeu(a.secondes) : 'RIEN'; };
    return { titre: 'PARTIE ' + n + ' : DEUX VERSIONS', largeur: 320,
      sur: 'ELLES NE SE FUSIONNENT PAS',
      aide: 'CELLE QU\'ON NE GARDE PAS NE REVIENDRA PAS',
      curseur: la && ici && la.secondes > ici.secondes ? 1 : 0,
      items: [
        { libelle: 'GARDER CELLE D\'ICI', detail: dire(ici),
          faire: function () { Compte.garder(n); ouvrirMenu(menuParties(n - 1)); return false; } },
        { libelle: 'PRENDRE CELLE DU COMPTE', detail: dire(la),
          faire: function () { ouvrirMenu(menuEchange(n)); Compte.prendre(n).then(function () { ouvrirMenu(menuParties(n - 1)); }); return false; } },
        { libelle: 'RETOUR', faire: function () { ouvrirMenu(menuParties(n - 1)); return false; } },
      ],
      retour: function () { ouvrirMenu(menuParties(n - 1)); } };
  }

  /** L'attente pendant que la partie descend : une ligne inerte, et aucun bouton
      qui ferait deux fois le meme echange. */
  function menuEchange(n) {
    return { titre: 'PARTIE ' + n, sur: 'ON DESCEND CELLE DU COMPTE…', items: [{ libelle: 'UN INSTANT', actif: false }], curseur: 0 };
  }

  function menuEffacer(curseur) {
    const liste = apercus();
    const items = liste.map(function (a, i) {
      const n = i + 1;
      return { libelle: ligneEmplacement(n, a, 'VIDE'), detail: a ? tempsDeJeu(a.secondes) : '', actif: !!a,
               faire: function () { ouvrirMenu(menuEffacerConfirmer(n)); return false; } };
    });
    items.push({ libelle: 'RETOUR', faire: function () { ouvrirMenu(menuParties()); return false; } });
    // ⚠️ Sur une partie qui EXISTE : une case vide est grisee, et un curseur
    // pose dessus n'a l'air de rien choisir.
    return { titre: 'EFFACER QUELLE PARTIE?', items: items, retour: function () { ouvrirMenu(menuParties()); },
             curseur: typeof curseur === 'number' ? curseur : Math.max(0, liste.findIndex(Boolean)) };
  }

  /** ⚠️ Le curseur s'ouvre sur NON. Une partie effacee ne revient pas, et ACTION
      est le bouton qu'on vient de presser deux fois de suite pour arriver ici. */
  function menuEffacerConfirmer(n) {
    const a = Sauvegarde.apercu(n);
    return { titre: 'EFFACER LA PARTIE ' + n + '?', curseur: 0,
      sur: a ? 'JOUR ' + a.jour + ' · ' + tempsDeJeu(a.secondes) : '',
      aide: 'ELLE NE REVIENDRA PAS',
      items: [
        { libelle: 'NON, LA GARDER', faire: function () { ouvrirMenu(menuParties(n - 1)); return false; } },
        { libelle: 'OUI, L\'EFFACER POUR DE BON', faire: function () { Jeu.effacerPartie(n); ouvrirMenu(menuParties(n - 1)); return false; } },
      ],
      retour: function () { ouvrirMenu(menuEffacer(n - 1)); } };
  }

  function menuCopier(curseur) {
    const liste = apercus();
    const items = liste.map(function (a, i) {
      const n = i + 1;
      return { libelle: ligneEmplacement(n, a, 'VIDE'), detail: a ? tempsDeJeu(a.secondes) : '', actif: !!a,
               faire: function () { ouvrirMenu(menuCopierVers(n)); return false; } };
    });
    items.push({ libelle: 'RETOUR', faire: function () { ouvrirMenu(menuParties()); return false; } });
    return { titre: 'COPIER QUELLE PARTIE?', items: items, retour: function () { ouvrirMenu(menuParties()); },
             curseur: typeof curseur === 'number' ? curseur : Math.max(0, liste.findIndex(Boolean)) };
  }

  function menuCopierVers(de) {
    const liste = apercus();
    const items = [];
    liste.forEach(function (a, i) {
      const n = i + 1;
      if (n === de) return;
      items.push({ libelle: ligneEmplacement(n, a, 'VIDE'), detail: a ? 'ÉCRASÉE' : '',
                   faire: function () {
                     if (a) { ouvrirMenu(menuCopierConfirmer(de, n)); return false; }
                     Jeu.copierPartie(de, n);
                     ouvrirMenu(menuParties(n - 1));
                     return false;
                   } });
    });
    items.push({ libelle: 'RETOUR', faire: function () { ouvrirMenu(menuCopier(de - 1)); return false; } });
    return { titre: 'COPIER LA ' + de + ' VERS', items: items, retour: function () { ouvrirMenu(menuCopier(de - 1)); } };
  }

  /** Copier PAR-DESSUS une partie, c'est l'effacer : meme question, meme NON d'abord. */
  function menuCopierConfirmer(de, vers) {
    const a = Sauvegarde.apercu(vers);
    return { titre: 'ÉCRASER LA PARTIE ' + vers + '?', curseur: 0,
      sur: a ? 'JOUR ' + a.jour + ' · ' + tempsDeJeu(a.secondes) : '',
      aide: 'LA PARTIE ' + vers + ' NE REVIENDRA PAS',
      items: [
        { libelle: 'NON, LA GARDER', faire: function () { ouvrirMenu(menuParties(vers - 1)); return false; } },
        { libelle: 'OUI, LA REMPLACER PAR LA ' + de, faire: function () { Jeu.copierPartie(de, vers); ouvrirMenu(menuParties(vers - 1)); return false; } },
      ],
      retour: function () { ouvrirMenu(menuCopierVers(de)); } };
  }

  // --- Le carnet : la mission, le journal, le repertoire ---------------------------

  /*: ⚠️ Le carnet N'INVENTE AUCUNE DONNEE. Tout ce qu'il montre est deja dans
    la partie et n'etait montre nulle part : l'objectif que le HUD ecrit en
    trente caracteres, les evenements que `Histoire.noter` pose, les gens que
    `p.connus` retient. C'est une FENETRE, pas une comptabilite.

    ⚠️ Et « journal » est pris deux fois dans ce depot : `journal.py` est Le
    Clairon (la manchette du matin), M11 prevoit le carnet du POSTE (le dossier
    de la police sur toi). Ici, c'est la page du joueur, dans LE CARNET. */
  function menuCarnet(depuis) {
    const p = B.partie;
    const connus = Object.keys(p.connus || {}).length;
    return surLaLigne(depuis, enOnglet('carnet', { titre: 'LE CARNET', sur: 'JOUR ' + p.jour, largeur: 320, items: [
      { libelle: 'EN COURS', cle: 'en_cours', detail: Histoire.courante() ? Histoire.courante().titre.toUpperCase() : 'RIEN',
        faire: function () { ouvrirMenu(menuCarnetEnCours()); return false; } },
      { libelle: 'JOURNAL', cle: 'journal', detail: (p.carnet || []).length + ' ENTRÉES',
        faire: function () { ouvrirMenu(menuCarnetJournal()); return false; } },
      { libelle: 'RÉPERTOIRE', cle: 'repertoire', detail: connus + ' PERSONNE' + (connus > 1 ? 'S' : ''),
        faire: function () { ouvrirMenu(menuCarnetRepertoire()); return false; } },
      // ⚠️ LA DETTE SE LIT ICI, sinon on l'oublie entre deux appels. C'est la
      // même règle que le carnet du poste : une pression qu'on subit sans
      // jamais pouvoir la regarder n'est pas une pression, c'est une
      // malchance. Elle disparaît de la page le jour où elle est réglée —
      // une ligne à zéro serait une dette qu'on traîne pour rien.
      p.dette > 0 ? { libelle: 'LA DETTE DE ROCCO', detail: p.dette + ' $', actif: false } : null,
      // ⚠️ ON LA REVOIT QUAND ON LE DEMANDE. Elle ne joue qu'une fois par
      // sauvegarde (sinon elle devient un peage), et une histoire qu'on ne peut
      // plus jamais entendre est une histoire qu'on a ratee parce qu'on a appuye
      // trop vite. C'est le carnet qui la garde : c'est deja lui qui garde le
      // journal, le repertoire et la dette.
      // ⚠️ Pas depuis un intérieur : la scène se joue dans la rue, et
      // `Histoire.ouverture` refuse poliment — une ligne de menu qui ne fait
      // rien se lit comme un bogue.
      !B.interieur ? { libelle: "REVOIR L'OUVERTURE", faire: function () {
          fermerMenu(); Jeu.reprendre(); Histoire.ouverture(true); return true; } } : null,
    ].filter(Boolean) }));
  }

  /** Pose le curseur de `menu` sur la ligne `cle` — la page dont on revient.

      ⚠️ RETOUR depuis une fiche rouvrait le repertoire sur sa PREMIERE ligne :
      avec dix personnes connues, on reperdait sa place a chaque fiche (Martin,
      22 sept.). Une page qu'on quitte pour y revenir rend le curseur la ou il
      etait ; une cle qu'on ne trouve plus (la ligne a disparu) laisse
      `ouvrirMenu` choisir, comme avant. */
  function surLaLigne(cle, menu) {
    if (cle === undefined) return menu;
    const i = menu.items.findIndex(function (item) { return item.cle === cle; });
    if (i >= 0) menu.curseur = i;
    return menu;
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
    items.push({ libelle: 'RETOUR', faire: function () { ouvrirMenu(menuCarnet('en_cours')); return false; } });
    return { titre: m ? m.titre.toUpperCase() : 'EN COURS', largeur: 320, curseur: items.length - 1,
             items: items, retour: function () { ouvrirMenu(menuCarnet('en_cours')); } };
  }

  /** JOURNAL : ce qui s'est passe, le plus recent en haut, date au jour. */
  function menuCarnetJournal() {
    const lignes = (B.partie.carnet || []).slice().reverse();
    const items = lignes.map(function (e) { return ligne(e.t, 'J' + e.j); });
    if (!items.length) items.push(ligne('RIEN ENCORE'));
    items.push({ libelle: 'RETOUR', faire: function () { ouvrirMenu(menuCarnet('journal')); return false; } });
    return { titre: 'JOURNAL', largeur: 320, hauteur: VH - 30, curseur: 0, items: items,
             retour: function () { ouvrirMenu(menuCarnet('journal')); } };
  }

  /** RÉPERTOIRE : les gens qu'on a RENCONTRES, et eux seuls. */
  function menuCarnetRepertoire(depuis) {
    const p = B.partie;
    const items = (B.defs.personnages || [])
      .filter(function (q) { return p.connus && p.connus[q.slug]; })
      .map(function (q) {
        return { libelle: q.nom.toUpperCase(), cle: q.slug, detail: 'J' + p.connus[q.slug],
                 faire: function () { ouvrirMenu(menuCarnetFiche(q.slug)); return false; } };
      });
    if (!items.length) items.push(ligne('TU N’AS ENCORE PARLÉ À PERSONNE'));
    items.push({ libelle: 'RETOUR', faire: function () { ouvrirMenu(menuCarnet('repertoire')); return false; } });
    return surLaLigne(depuis, { titre: 'RÉPERTOIRE', largeur: 320, hauteur: VH - 30, items: items,
             retour: function () { ouvrirMenu(menuCarnet('repertoire')); } });
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
    items.push({ libelle: 'RETOUR', faire: function () { ouvrirMenu(menuCarnetRepertoire(slug)); return false; } });
    return { titre: q ? q.nom.toUpperCase() : slug.toUpperCase(), largeur: 320, colonne: 250,
             curseur: items.length - 1, items: items,
             retour: function () { ouvrirMenu(menuCarnetRepertoire(slug)); },
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

  /** Le premier onglet du classeur : ce qu'on fait de la partie. Le carnet, le
      bilan, les commandes, les options et les triches sont les onglets d'a cote
      (`ONGLETS`) — ils etaient des lignes de cette liste. */
  function menuPause() {
    return enOnglet('pause', { titre: 'PAUSE', sur: 'JOUR ' + B.partie.jour + ' ' + Monde.heureTexte(), items: [
      { libelle: 'REPRENDRE', faire: function () { Jeu.reprendre(); return true; } },
      { libelle: 'CARTE DE LA VILLE', faire: function () { Jeu.ouvrirCarte(); return true; } },
      { libelle: 'MODE PHOTO', faire: function () { Jeu.ouvrirPhoto(); return true; } },
      { libelle: 'SAUVEGARDER', faire: function () { Missions.sauvegarderPartie(); message('PARTIE SAUVEGARDÉE'); return false; } },
      { libelle: 'QUITTER VERS LE TITRE', faire: function () { Jeu.retourTitre(); return true; } },
    ] });
  }

  //: Les onglets du classeur, dans l'ordre ou on les tourne. ⚠️ TRICHES n'existe
  //: que dans une partie ou la suite secrete a ete tapee (`Jeu.ouvrirMenuDebug`) :
  //: une partie qui ne l'a jamais tapee n'en montre rien, pas meme un onglet gris.
  const ONGLETS = [
    { slug: 'pause', titre: 'PAUSE', menu: function () { return menuPause(); } },
    { slug: 'carnet', titre: 'CARNET', menu: function () { return menuCarnet(); } },
    { slug: 'bilan', titre: 'BILAN', menu: function () { return menuBilan(); } },
    { slug: 'commandes', titre: 'COMMANDES', menu: function () { return menuCommandes(true); } },
    { slug: 'options', titre: 'OPTIONS', menu: function () { return menuOptions(); } },
    { slug: 'triches', titre: 'TRICHES', menu: function () { return menuDebug(); }, si: function () { return triche('menu'); } },
  ];

  function ongletsVisibles() { return ONGLETS.filter(function (o) { return !o.si || o.si(); }); }

  /** Pose `menu` sous l'onglet `slug`, comme sa page de tete. */
  function enOnglet(slug, menu) { menu.classeur = { onglet: slug, racine: true }; return menu; }

  /** Ouvre la page de tete d'un onglet ; rend false s'il n'y en a pas (TRICHES
      dans une partie qui ne les a pas). */
  function ouvrirOnglet(slug) {
    const o = ongletsVisibles().find(function (q) { return q.slug === slug; });
    if (!o) return false;
    ouvrirMenu(o.menu());
    return true;
  }

  /** Le sens dans lequel on tourne l'onglet a cette image : -1, 1, ou 0.
      ⚠️ Sur une page ou l'on ESSAIE sa manette (COMMANDES, l'ecran MANETTE), la
      croix s'allume sans rien tourner ; les epaules, elles, tournent — sauf la
      ou on les essaie aussi (`epaulesInertes`). Le stick ne tourne jamais rien :
      on le pousse pour voir MARCHER s'allumer. */
  function sensDOnglet(m) {
    if (!m.epaulesInertes) {
      if (Entree.neufEpaule('g')) return -1;
      if (Entree.neufEpaule('d')) return 1;
    }
    const lire = m.manetteInerte ? Entree.neufSansManette : Entree.neuf;
    const sens = lire('gauche') ? -1 : lire('droite') ? 1 : 0;
    // ⚠️ LE POUCE SUR LA VITRE monte et descend dans la liste (HAUT et BAS) : une
    // diagonale passe par GAUCHE ou DROITE sans qu'on veuille changer de page.
    // Au doigt, seul un geste franchement de cote tourne l'onglet.
    const a = Entree.axe;
    if (sens && a.source === 'tactile' && Math.abs(a.x) <= Math.abs(a.y)) return 0;
    return sens;
  }

  /** L'onglet d'a cote — on fait le tour, comme un classeur qu'on feuillette. */
  function tournerOnglet(m, sens) {
    const liste = ongletsVisibles();
    const k = Math.max(0, liste.findIndex(function (o) { return o.slug === m.classeur.onglet; }));
    ouvrirOnglet(liste[(k + sens + liste.length) % liste.length].slug);
  }

  // --- Debug : la triche du developpeur, jamais un bouton visible -------------------
  //: L'onglet TRICHES du classeur. La suite secrete de touches ecoutee dans
  //: `Jeu.demarrer` (voir `Entree.surSecret`) l'ouvre — et l'allume pour de bon
  //: dans cette partie : l'onglet reste dans sa PAUSE. Aucun autre bouton n'y mene.
  //: ⚠️ Ses BASCULES (invincible, vehicules, energie, munitions, police) se sauvent
  //: avec la partie (`B.partie.triches`) : on rouvre son emplacement, elles y sont
  //: encore. C'est la ligne OUI/NON qui dit ce qui est allume.
  //: ⚠️ Une ligne qui rend `true` ferme le classeur et la pause reprend toute
  //: seule (`Jeu.maj` : « fermer le dernier menu, c'est reprendre »).

  /** Bascule une triche de `B.partie.triches`, la dit dans son item et SE SAUVE
      tout de suite : un rechargement avant la sauvegarde auto (dix secondes) ne
      la perdrait pas. */
  function basculerTriche(nom, item) {
    const t = B.partie.triches;
    t[nom] = !t[nom];
    item.detail = t[nom] ? 'OUI' : 'NON';
    Missions.sauvegarderPartie();
  }

  /** Saute le joueur au point que le HUD pointe deja (la fleche/losange de
      `Histoire.cible`) — rien de plus qu'un raccourci sur une position deja
      calculee. Refuse dans une piece ou au volant : `Jeu.sortir` orchestre sa
      propre transition et redonnerait au joueur la position de la porte un
      instant plus tard, par-dessus le teleport. */
  function teleporterVersObjectif() {
    const j = B.joueur;
    if (!j) return;
    if (B.interieur || j.dansVehicule) { message('SORS D\'ABORD'); return; }
    const c = Histoire.cible();
    if (!c) { message('AUCUN OBJECTIF'); return; }
    j.x = c.x; j.y = c.y; j.vx = 0; j.vy = 0;
    Monde.centrerCamera(j.x, j.y);
    message('TÉLÉPORTÉ');
  }

  /** Une tuile a pied a un pas de `e` — hors chaussee, hors meuble, sans
      personne dessus —, ou null. */
  function placeAupres(e) {
    const tx = Math.floor(e.x / TT), ty = Math.floor(e.y / TT);
    const pas = [[1, 0], [-1, 0], [0, 1], [0, -1], [1, 1], [-1, 1], [1, -1], [-1, -1], [2, 0], [-2, 0], [0, 2], [0, -2]];
    for (const p of pas) {
      const x = tx + p[0], y = ty + p[1];
      if (!Monde.marchablePieton(x, y) || Monde.estMeuble(x, y)) continue;
      if (Entites.pietonsAutour(x * TT + 8, y * TT + 8, 10).length) continue;
      return { x: x * TT + 8, y: y * TT + 8 };
    }
    return null;
  }

  /** Se poser DEVANT le donneur d'une mission, la ou l'on lui parle : a cote de
      lui dehors, DANS sa piece quand il se tient dedans (M4, M5, M6).

      ⚠️ Le bon endroit decide de la facon dont l'intro se joue : a moins de
      douze tuiles de lui (`Histoire.present`) elle se joue EN PERSONNE, plus
      loin elle se dit au combine. Et dehors, un donneur dedans n'existe pas.
      ⚠️ On sort de la piece ou l'on est et du char SANS fondu (`Jeu.entrer` puis
      `Jeu.finirTransition`, comme le reveil a l'hopital) : l'ancien saut refusait
      « SORS D'ABORD » et ne posait le joueur que sur le pixel du donneur. Un
      donneur qui n'est plus la — Ti-Guy entre au garage a la fin de M1 — est
      REPOSE devant sa porte : sa mission se refait quand meme.
      Rend faux quand il n'y a nulle part ou se poser. */
  function allerChezLeDonneur(slug) {
    const j = B.joueur, perso = Histoire.personnage(slug);
    if (!j || !perso) return false;
    Jeu.finirTransition();
    if (j.dansVehicule) Vehicules.descendre(j, true);
    // ⚠️ Dehors D'ABORD, toujours : `quitterLaPiece` ne pose pas le joueur, et un
    // joueur qui garderait ses coordonnees de piece se retrouverait au milieu de
    // la ville. Il retombe la ou il etait entre ; s'il ne trouve rien mieux, il y reste.
    const ext = Jeu.quitterLaPiece();
    if (ext) { j.x = ext.x; j.y = ext.y; }
    let e = null;
    if (perso.ou.indexOf('point:') === 0) {
      const piece = Histoire.pieceDuPoint(perso.ou.slice(6));
      const porte = piece && (Monde.carte.def.portes || []).find(function (q) { return q.lieu === piece.slug && q.interieur; });
      if (porte && Jeu.entrer(porte)) { Jeu.finirTransition(); e = Histoire.donneur(slug); }
    } else {
      e = Histoire.donneur(slug) || Histoire.poserDonneur(perso);
    }
    if (!e) return false;
    Entites.indexer();
    const place = placeAupres(e);
    if (!place) return false;
    j.x = place.x; j.y = place.y; j.vx = 0; j.vy = 0;
    Entites.regarder(j, e.x - j.x, e.y - j.y);
    Entites.regarder(e, j.x - e.x, j.y - e.y);
    Entites.indexer();
    Monde.centrerCamera(j.x, j.y);
    return true;
  }

  /** Va chez le donneur de `m` et LANCE la mission, comme s'il venait de nous
      parler (`Histoire.demarrer`). Ferme le menu — et la pause : la partie
      reprend AVANT que l'intro ne se joue. Rend `false` (le menu reste ouvert)
      quand on ne peut pas : une scene joue, ou il n'y a nulle part ou se poser. */
  function lancerLaMission(m) {
    if (!B.joueur || B.cinema || B.scene) { message('UNE SCÈNE JOUE'); return false; }
    if (!allerChezLeDonneur(m.donneur)) { message('INTROUVABLE'); return false; }
    if (B.etat === 'pause') Jeu.reprendre();
    fermerMenu();
    Histoire.demarrer(m.slug);
    return true;
  }

  /** SAUT VERS UNE MISSION : la liste complete de `B.defs.missions`. C'est le
      CATALOGUE qui fait la liste — une mission ajoutee au jeu tombe ici sans
      qu'on y touche. Choisir une ligne TELEPORTE devant le donneur (dans sa piece
      s'il est dedans) et LANCE la mission tout de suite, intro comprise
      (`lancerLaMission`) — deja faite, elle est d'abord reinitialisee ; en cours,
      celle-ci ou une autre, elle est abandonnee sans compter d'echec.
      ⚠️ Aucun pre-requis n'est regarde : la mission part dans l'etat ou est la partie. */
  function menuSautMissions() {
    const p = B.partie;
    const cours = p.mission ? p.mission.slug : null;
    const items = (B.defs.missions || []).map(function (m) {
      const faite = !!p.missionsFaites[m.slug];
      const etat = faite ? 'FAITE · REFAIRE' : (m.slug === cours ? 'EN COURS · RELANCER' : 'LANCER');
      return { libelle: m.titre.toUpperCase(), detail: etat,
               actif: !!Histoire.personnage(m.donneur),
               faire: function () { return lancerLaMission(m); } };
    });
    items.push({ libelle: 'RETOUR', faire: function () { ouvrirMenu(menuDebug()); return false; } });
    return { titre: 'SAUT VERS UNE MISSION', largeur: 320, hauteur: VH - 30,
             items: items, retour: function () { ouvrirMenu(menuDebug()); } };
  }

  /** Le point d'ou un defi se lance, dans la ville : son PANNEAU (`Histoire.creerPanneaux`),
      ou le comptoir de son jeu de foire (`foire:<jeu>` : aucun panneau ne s'y
      plante, c'est la baraque qui sert de panneau). `portee` : d'ou ACTION le lit
      (`Histoire.panneauSousLaMain`, `Foire.jeuSousLaMain`). Null s'il n'y en a pas. */
  function pointDuDefi(d) {
    if (!d.ou) return null;
    if (d.ou.indexOf('foire:') === 0) {
      const q = (typeof Foire !== 'undefined' ? Foire.jeux() : []).find(function (k) { return k.slug === d.ou.slice(6); });
      return q ? { x: q.x * TT + 8, y: q.y * TT + 15, portee: Foire.PORTEE_JEU - 4 } : null;
    }
    const e = B.entites.find(function (k) { return k.type === 'panneau' && k.defi === d.slug; });
    return e ? { x: e.x, y: e.y, portee: 20 } : null;
  }

  /** Dans un decor solide (une baraque, une borne) : le joueur y serait pousse
      dehors a l'image suivante (`Entites.bloquerParDecor`), hors de portee. */
  function dansUnDecor(x, y) {
    const r = 5;
    return Entites.decorAutour(x, y, 24).some(function (d) {
      if (!d.solide) return false;
      const sol = typeof DECORS !== 'undefined' && DECORS[d.decor] && DECORS[d.decor].sol;
      if (sol) return Math.abs(x - d.x) < sol[0] + r && Math.abs(y - d.y) < sol[1] + r;
      return Math.hypot(x - d.x, y - d.y) < r + (d.r || 0);
    });
  }

  /** La tuile a pied la plus proche de `c` d'ou on le LIT : a sa portee, pas
      dessus, hors meuble, hors decor solide, sans personne dessus. Ou null. */
  function placeDevant(c) {
    const tx0 = Math.floor(c.x / TT), ty0 = Math.floor(c.y / TT);
    let meilleure = null, dMin = Infinity;
    for (let dy = -3; dy <= 3; dy++) for (let dx = -3; dx <= 3; dx++) {
      const tx = tx0 + dx, ty = ty0 + dy, x = tx * TT + 8, y = ty * TT + 8;
      const d = Math.hypot(x - c.x, y - c.y);
      if (d < 8 || d > c.portee || d >= dMin) continue;
      if (!Monde.marchablePieton(tx, ty) || Monde.estMeuble(tx, ty) || dansUnDecor(x, y)) continue;
      if (Entites.pietonsAutour(x, y, 10).length) continue;
      meilleure = { x: x, y: y }; dMin = d;
    }
    return meilleure;
  }

  /** Va au depart d'un defi et OUVRE sa proposition (COMMENCER / PAS MAINTENANT),
      comme si on venait de lire son panneau. Ferme le classeur — et la pause :
      la proposition est un menu ordinaire, par-dessus la ville.
      ⚠️ On sort du char et de la piece SANS fondu, comme le saut vers une
      mission (`allerChezLeDonneur`) : le panneau se lit a pied, dehors. Un defi
      deja en cours est abandonne sans rien noter : c'est une triche, pas un echec.
      Rend `false` (le menu reste ouvert) quand on ne peut pas. */
  function allerAuDefi(d) {
    const j = B.joueur;
    if (!j || B.cinema || B.scene) { message('UNE SCÈNE JOUE'); return false; }
    Jeu.finirTransition();
    if (j.dansVehicule) Vehicules.descendre(j, true);
    const ext = Jeu.quitterLaPiece();
    if (ext) { j.x = ext.x; j.y = ext.y; }
    const c = pointDuDefi(d);
    const place = c && placeDevant(c);
    if (!place) { message('INTROUVABLE'); return false; }
    if (B.defi) Histoire.abandonnerDefi();
    j.x = place.x; j.y = place.y; j.vx = 0; j.vy = 0;
    Entites.regarder(j, c.x - j.x, c.y - j.y);
    Entites.indexer();
    Monde.centrerCamera(j.x, j.y);
    if (B.etat === 'pause') Jeu.reprendre();
    fermerMenu();
    Histoire.proposerDefi(d.slug);
    return true;
  }

  /** SAUT VERS UN DÉFI : tous les defis de `B.defs.defis`, rangés par genre — au
      volant, les tours (une course sur un circuit), la foire. C'est le CATALOGUE
      qui fait la liste : un defi ajoute au jeu tombe ici sans qu'on y touche. */
  function menuSautDefis() {
    const p = B.partie;
    const genres = [
      ['AU VOLANT', function (d) { return !d.circuit && !d.a_pied; }],
      ['LES TOURS', function (d) { return !!d.circuit; }],
      ['À LA FOIRE', function (d) { return !!d.a_pied; }],
    ];
    const items = [];
    for (const g of genres) {
      const siens = (B.defs.defis || []).filter(g[1]);
      if (!siens.length) continue;
      items.push(entete(g[0]));
      for (const d of siens) {
        const etat = B.defi && B.defi.slug === d.slug ? 'EN COURS' : (p.defisFaits && p.defisFaits[d.slug] ? 'RÉUSSI' : '');
        items.push({ libelle: d.titre.toUpperCase(), detail: etat, defi: d.slug, actif: !!d.ou,
                     faire: function () { return allerAuDefi(d); } });
      }
    }
    items.push({ libelle: 'RETOUR', faire: function () { ouvrirMenu(menuDebug()); return false; } });
    return { titre: 'SAUT VERS UN DÉFI', largeur: 320, items: items, retour: function () { ouvrirMenu(menuDebug()); } };
  }

  /** JUKEBOX : toutes les musiques de `B.defs.audio.musiques`, jouables a la
      demande. Le morceau choisit joue TANT QU'ON n'arrete pas (`Son.Chef` le
      respecte des qu'il lit `B.jukebox`) ; la note en bas le rappelle. */
  function menuJukebox() {
    const musiques = (B.defs.audio && B.defs.audio.musiques) || [];
    const items = musiques.map(function (m) {
      const joue = B.jukebox === m.slug;
      return { libelle: (m.nom || m.slug).toUpperCase(), detail: joue ? '▶ JOUE' : '',
               faire: function () {
                 B.jukebox = (B.jukebox === m.slug) ? null : m.slug;
                 if (B.jukebox) Son.Mus.jouer(B.jukebox);
                 else Son.Chef.arreter();
                 return false;                                        // on reste dans le jukebox
               } };
    });
    items.push({ libelle: 'ARRÊTER LA MUSIQUE', detail: B.jukebox ? '▶ JOUE' : '',
                 faire: function () { B.jukebox = null; Son.Chef.arreter(); return false; } });
    items.push({ libelle: 'RETOUR', faire: function () { B.jukebox = null; Son.Chef.arreter(); ouvrirMenu(menuDebug()); return false; } });
    return { titre: 'JUKEBOX', largeur: 340, hauteur: VH - 30, items: items,
             retour: function () { B.jukebox = null; Son.Chef.arreter(); ouvrirMenu(menuDebug()); } };
  }

  /** Donne TOUTES les armes (chargees a fond) et TOUS les vetements, en lisant
      la source de verite elle-meme (`B.defs`). C'est le CATALOGUE qui decide :
      une arme ou une tenue ajoutee au jeu tombe dans cette triche sans qu'on y
      touche — aucun slug ecrit ici, donc rien a oublier le jour ou s'ajoute le
      suivant. Les poings et le chandail, deja a soi, sont ignores. */
  function tousLesItems() {
    const p = B.partie;
    if (!p) { message('PAS DE PARTIE'); return false; }
    let armes = 0, tenues = 0;
    for (const a of (B.defs.armes || [])) {
      if (a.slug === 'poings') continue;                 // deja au sac a la naissance
      if (Combat.ramasserArme(a.slug, a.munitions_max || a.chargeur)) armes++;
    }
    for (const t of (B.defs.tenues || [])) {
      if (t.slug === 'chandail' || p.tenues.indexOf(t.slug) >= 0) continue;
      p.tenues.push(t.slug);
      tenues++;
    }
    Son.SFX.argent();
    message('TOUTES LES ARMES ET TENUES');
    return false;
  }

  /** L'onglet TRICHES, en sections : ce qu'on se donne, ou l'on va, la mission
      en cours, le reste. ⚠️ Il n'y a plus de PLUS… ni de RETOUR : les sauts sont
      des sous-pages de l'onglet, et B reprend la partie comme partout dans le
      classeur. */
  function menuDebug() {
    const m = Histoire.courante();
    function bascule(nom, libelle) {
      return { libelle: libelle, detail: triche(nom) ? 'OUI' : 'NON', faire: function (item) { basculerTriche(nom, item); return false; } };
    }
    return enOnglet('triches', { titre: 'TRICHES', sur: 'DEBUG', items: [
      entete('LE JOUEUR'),
      { libelle: 'ARGENT +1 000 $', faire: function () { Missions.encaisser(1000, 'DEBUG'); return false; } },
      { libelle: 'ARGENT +50 000 $', faire: function () { Missions.encaisser(50000, 'DEBUG'); return false; } },
      { libelle: 'TOUS LES ITEMS', faire: function () { tousLesItems(); return false; } },
      { libelle: 'SANTÉ COMPLÈTE', faire: function () { Missions.soigner(B.joueur, B.joueur.vieMax); return false; } },
      bascule('invincible', 'INVINCIBLE'),
      bascule('vehicules', 'VÉHICULES INVINCIBLES'),
      bascule('endurance', 'ÉNERGIE INFINIE'),
      bascule('munitions', 'MUNITIONS INFINIES'),
      bascule('pasArrete', 'LA POLICE NE T\'ARRÊTE PAS'),
      entete('ALLER'),
      { libelle: 'TÉLÉPORTER À L\'OBJECTIF', actif: !!Histoire.cible(), faire: function () { teleporterVersObjectif(); return true; } },
      { libelle: 'SAUT VERS UNE MISSION', faire: function () { ouvrirMenu(menuSautMissions()); return false; } },
      { libelle: 'SAUT VERS UN DÉFI', faire: function () { ouvrirMenu(menuSautDefis()); return false; } },
      entete('LA MISSION'),
      { libelle: 'OBJECTIF SUIVANT', actif: !!m, faire: function () { Histoire.avancer(); return true; } },
      { libelle: 'TERMINER LA MISSION', actif: !!m, faire: function () { Histoire.reussir(); return true; } },
      entete('DIVERS'),
      // ⚠️ Coop locale (M14, essai) : PAS une triche de `B.partie.triches` — elle
      // n'est jamais sauvegardee (on la rallume a chaque essai) et bascule une
      // VRAIE entite dans le monde, pas juste un drapeau.
      { libelle: 'COOP LOCALE (ESSAI)', detail: B.coop ? 'OUI' : 'NON', faire: function (item) { Jeu.basculerCoop(); item.detail = B.coop ? 'OUI' : 'NON'; return false; } },
      { libelle: 'JUKEBOX', faire: function () { ouvrirMenu(menuJukebox()); return false; } },
    ] });
  }

  /** L'invite du bas : ce que fera ACTION ici. */
  function invite(ctx) {
    const j = B.joueur;
    // ⚠️ A bord d'un autobus, on est « dans un vehicule » et l'invite parle quand
    // meme : c'est elle qui dit ou l'on descend.
    if (!j || (j.dansVehicule && !j.passager) || !B.invite || B.menu) return;   // un menu ouvert : l'invite se tait
    if (B.scene) return;                     // une scene joue : ACTION passe une replique, il n'ouvre pas de porte
    // ⚠️ LE BOUTON, PAS SON NOM : « ACTION » ne dit a personne sur quoi
    // peser. A la manette le A (ou la croix) dessine, au clavier la touche E ;
    // au doigt, le bouton s'appelle ACTION, et le mot reste.
    const glyphe = glypheDAction('action');
    const t = glyphe ? B.invite : 'ACTION : ' + B.invite;
    const lg = glyphe ? largeurGlyphe(glyphe) + 3 : 0;
    const l = lg + Atlas.largeurTexte(t, 1);
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
    if (glyphe) dessinerGlyphe(ctx, glyphe, (VW - l) / 2, VH - 25);
    texte(ctx, t, (VW - l) / 2 + lg, VH - 24, '#efe6d0', 1);
    noter('invite', (VW - l) / 2 - 4, VH - 26, l + 8, 11);
  }

  /** A l'abribus, sans rien a faire du bouton : quand passe le prochain. ⚠️ Pas
      d'« ACTION : » devant — le bouton n'y fait rien, et une invite qui promet
      un geste qui n'existe pas se lit comme un bogue. */
  function attenteALAbribus(ctx) {
    const j = B.joueur;
    if (!j || B.invite || B.menu || B.dialogue) return;
    // Sous terre, le metro dit ou l'on est et quand passe la rame.
    // Au quai du traversier (ou a bord), son horaire.
    const t = B.interieur ? Metro.texteDInfo(j) : (Autobus.texteDAttente(j) || Traversier.texteDInfo(j) || Neige.texteDInfo(j));
    if (!t) return;
    const l = Atlas.largeurTexte(t, 1);
    ctx.fillStyle = 'rgba(11,10,18,0.7)'; ctx.fillRect((VW - l) / 2 - 4, VH - 26, l + 8, 11);
    texte(ctx, t, (VW - l) / 2, VH - 24, '#cfe3ee', 1);
    noter('attente', (VW - l) / 2 - 4, VH - 26, l + 8, 11);
  }

  /** Les lignes d'autobus sur la grande carte : le trace de chacune dans sa
      couleur, et un point blanc par abribus. */
  function dessinerLignes(ctx, pos) {
    const d = Autobus.donnees();
    if (!d) return;
    for (const L of d.lignes) {
      ctx.fillStyle = L.couleur;
      for (const t of L.tuiles) { const p = pos(t[0] * TT, t[1] * TT); ctx.fillRect(p.x, p.y, 1, 1); }
      B.stats.rects += L.n;
    }
    for (const a of d.arrets) {
      const p = pos(a.x * TT, a.y * TT);
      ctx.fillStyle = '#101018'; ctx.fillRect(p.x - 1, p.y - 1, 3, 3);
      ctx.fillStyle = '#ffffff'; ctx.fillRect(p.x, p.y, 1, 1);
      B.stats.rects += 2;
    }
  }

  /** Une boite de texte : une ou deux lignes, qui se ferme au bouton.
      `visage` (`{ slug, humeur }`) pose le portrait de qui parle a gauche (`Visages`) ;
      sans lui, ou pour un slug qui n'a pas de visage, la boite reste celle d'avant. */
  function dialogue(qui, lignes, duree, visage) {
    B.dialogue = { qui: qui, lignes: Array.isArray(lignes) ? lignes : [lignes], t: 0, duree: duree || 0,
                   visage: visage && typeof Visages !== 'undefined' && Visages.connait(visage.slug) ? visage : null,
                   voix: false };
  }

  //: Le portrait dans la boite : 42 x 42 cadre compris, a quatre pixels du haut ; le texte
  //: se pousse de `PORTRAIT_DECALE` a droite. La boite grandit a `PORTRAIT_BOITE` pour le tenir.
  const PORTRAIT_DECALE = 48, PORTRAIT_BOITE = 50;

  /** La bouche bouge-t-elle ? Tant que SA voix joue ; sans voix (muette, pas encore
      generee, son coupe), le temps de dire le texte — deux images par lettre. */
  function parleEncore(d) {
    if (typeof Son !== 'undefined' && Son.Voix && Son.Voix.enCours) return true;
    if (d.voix) return false;
    const lettres = d.lignes.reduce(function (n, l) { return n + l.length; }, 0);
    return d.t < 10 + lettres * 2;
  }

  function dessinerDialogue(ctx) {
    const d = B.dialogue;
    if (!d) return;
    d.t++;
    const v = d.visage;
    const h = Math.max(22 + d.lignes.length * 9, v ? PORTRAIT_BOITE : 0);
    const xt = 18 + (v ? PORTRAIT_DECALE : 0);
    ctx.fillStyle = 'rgba(11,10,18,0.9)'; ctx.fillRect(12, VH - h - 8, VW - 24, h);
    ctx.fillStyle = '#e8b33c'; ctx.fillRect(12, VH - h - 8, VW - 24, 1);
    // ⚠️ L'HORLOGE DE L'OEIL (`B.image`) pour le clin, comme pour « ACTION > » plus bas :
    // la ville est figee pendant qu'on lit, et un visage qui ne cligne plus est un masque.
    if (v) Visages.dessiner(ctx, v.slug, 16, VH - h - 4, v.humeur, B.image || d.t, parleEncore(d));
    if (d.qui) texte(ctx, d.qui.toUpperCase(), xt, VH - h - 2, '#e8b33c', 1);
    d.lignes.forEach(function (ligne, i) { texte(ctx, ligne, xt, VH - h + 8 + i * 9, '#efe6d0', 1); });
    // ⚠️ L'HORLOGE DE L'OEIL (`B.image`), PAS CELLE DU MONDE (`B.t`) : depuis
    // qu'un dialogue fige la ville (`Jeu.maj`), `B.t` ne bouge plus pendant
    // qu'on lit — et « ACTION > » serait reste eteint (ou allume) tout l'appel,
    // c'est-a-dire au seul moment ou il a quelque chose a dire.
    if (B.cinema && (B.image >> 4) % 2 === 0) {
      // ⚠️ Dans une scene, la derniere ligne d'un plan `dire` n'est pas la fin : d'autres
      // repliques suivent sous d'autres plans. On ne promet pas « FIN » a tort.
      const fin = (B.scene || B.cinema.i < B.cinema.lignes.length - 1) ? '>' : '> FIN';
      const glyphe = glypheDAction('action');
      const suite = glyphe ? fin : 'ACTION ' + fin;
      const xs = VW - 18 - Atlas.largeurTexte(suite, 1);
      if (glyphe) dessinerGlyphe(ctx, glyphe, xs - largeurGlyphe(glyphe) - 3, VH - 18);
      texte(ctx, suite, xs, VH - 16, '#8a8698', 1);
    }
    if (d.duree && d.t > d.duree) B.dialogue = null;
    B.stats.rects += 2;
  }

  //: Le titre de l'ouverture. ⚠️ Le logo (71 x 15) a un multiple ENTIER : a x3,
  //: chaque pixel du dessin couvre trois pixels du jeu et garde le meme grain
  //: que la ville derriere ; a x2,5 il baverait une rangee sur deux.
  const LOGO_ECHELLE = 3, LOGO_Y = 54;
  //: La bande sombre sous le titre : le logo (54 a 99) et « BAIE-DES-BRUMES » (105).
  const BANDE_TITRE = { y: 50, h: 68 };
  let logoTitre = null;

  /** Le logo du `<h1>` de l'accueil, s'il a fini de charger — sinon `null`. */
  function logoCharge() {
    return logoTitre && logoTitre.complete && logoTitre.naturalWidth > 0 ? logoTitre : null;
  }

  /** Une scene (`Scenes`) : son noir, et le carton qui s'inscrit — le logo de
      l'accueil pour l'ouverture, un texte pour une mission.

      ⚠️ Son propre noir, et pas celui de `Jeu.transiter` : un fondu de porte
      FIGE le jeu (`B.transition` coupe la boucle), or ici c'est justement
      pendant le noir que le car doit arriver. Deux compteurs qui ne veulent pas
      dire la meme chose ne partagent pas une variable.

      ⚠️ LE TITRE EST LE LOGO DE L'ACCUEIL, la meme image : celle que le `<h1>`
      a deja chargee (`static/img/logo.svg`, dessinee par `scripts/icones.py`).
      Retour de Martin : le logo neuf etait sur l'accueil, et l'ouverture
      ecrivait encore « BANDINI » en police du HUD. Une seconde copie du dessin
      ici aurait diverge a la premiere retouche.

      ⚠️ Tant que l'image n'est pas la (ou au banc, qui n'a pas de page), le
      nom s'ecrit en lettres, en DEUX passes (l'ombre, puis les lettres) : sans
      ombre, « BANDINI » disparait sur un mur clair, et c'est le nom du jeu. */
  function dessinerScene(ctx) {
    const o = B.scene;
    if (!o) return;
    if (o.noir > 0.004) {
      ctx.fillStyle = 'rgba(11,10,18,' + o.noir.toFixed(3) + ')';
      ctx.fillRect(0, 0, VW, VH);
      B.stats.rects++;
    }
    if (o.titre > 0.004 && o.carton) {
      const a = Math.min(1, o.titre);
      const nom = o.carton.logo ? 'BANDINI' : o.carton.texte, sous = o.carton.sous || '';
      // ⚠️ UNE BANDE SOUS LE TITRE, pas seulement une ombre d'un pixel. Mesure
      // faite : « BAIE-DES-BRUMES » tombait pile sur l'enseigne TERMINUS et ne
      // se lisait plus. Le nom du jeu ne peut pas dependre de ce qu'il y a
      // derriere — et la scene se joue devant un batiment, toujours le meme.
      ctx.fillStyle = 'rgba(11,10,18,' + (0.62 * a).toFixed(3) + ')';
      ctx.fillRect(0, BANDE_TITRE.y, VW, BANDE_TITRE.h);
      B.stats.rects++;
      const logo = o.carton.logo ? logoCharge() : null;
      if (logo) {
        const w = logo.naturalWidth * LOGO_ECHELLE, h = logo.naturalHeight * LOGO_ECHELLE;
        ctx.save();
        ctx.globalAlpha = a;
        ctx.imageSmoothingEnabled = false;
        ctx.drawImage(logo, Math.round((VW - w) / 2), LOGO_Y, w, h);
        ctx.restore();
        B.stats.images++;
      } else {
        const xn = Math.round((VW - Atlas.largeurTexte(nom, 4)) / 2);
        Atlas.texte(ctx, nom, xn + 2, 70, 'rgba(11,10,18,' + (0.8 * a).toFixed(3) + ')', 4);
        Atlas.texte(ctx, nom, xn, 68, 'rgba(232,179,60,' + a.toFixed(3) + ')', 4);
      }
      const xs = Math.round((VW - Atlas.largeurTexte(sous, 1)) / 2);
      Atlas.texte(ctx, sous, xs + 1, 106, 'rgba(11,10,18,' + (0.8 * a).toFixed(3) + ')', 1);
      Atlas.texte(ctx, sous, xs, 105, 'rgba(239,230,208,' + a.toFixed(3) + ')', 1);
    }
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

  // --- LE COMPTE (M14, 2e vague) -------------------------------------------------------

  const MOT_DU_COMPTE = 'Un compte garde tes parties sur le serveur : commence au téléphone, finis à l’ordi. Le jeu se joue très bien sans.';

  function champ(id) {
    const el = doc && doc.getElementById(id);
    return el ? String(el.value || '').trim() : '';
  }

  /** « aujourd'hui à 21 h 40 » pour le DOM — le canvas, lui, a `quand()`. */
  function dateCourte(iso) {
    if (!iso) return '';
    const d = new Date(iso);
    if (isNaN(d.getTime())) return '';
    return quand(d.getTime(), Date.now()).toLowerCase();
  }

  //: LE NIP (M14, 3e vague) : « Mot de passe plutôt » montre le formulaire habituel
  //: SANS toucher au NIP local — un contournement d'un chargement, pas un « oublie
  //: mon NIP ». Remis a zero a chaque ouverture de l'ecran.
  let nipBypasse = false;
  //: EFFACER SON COMPTE (M14, 4e vague) : la confirmation est-elle ouverte ? Purement
  //: d'affichage, et remise a zero a chaque ouverture de l'ecran, comme `nipBypasse`.
  let effacerDemande = false;

  function montrerCompte() {
    nipBypasse = false;
    effacerDemande = false;
    voile('compte');
    majCompte();
    const v = Compte.etat();
    const el = doc.getElementById(v.etat === 'verrouille' ? 'nip-code' : 'compte-pseudo');
    if (el && el.focus) el.focus();
  }

  /** LE DEFI DU JOUR au titre : « Defi du jour : Tour du Faubourg — 250 $ », ou rien du tout
      (pas de reseau, defi inconnu de ce catalogue). ⚠️ `textContent`, jamais `innerHTML` : le
      titre vient d'un catalogue, mais le slug vient du reseau. */
  function majDefiDuJour() {
    const el = doc && doc.getElementById('defi-du-jour');
    if (!el) return;
    const j = Defi.duJour();
    el.hidden = !j;
    el.textContent = j ? 'Défi du jour : ' + j.def.titre + ' — ' + j.def.prime + ' $' : '';
  }

  /** Le message de l'effacement : dans le formulaire ET dans `compte-etat`, qui est
      DEHORS — un effacement reussi (ou une session coupee) referme le formulaire, et le
      seul mot qui dit ce qui s'est passe se cacherait avec lui (le piege de « Bonjour »). */
  function direEffacer(texte) {
    const dedans = doc.getElementById('compte-effacer-etat'), dehors = doc.getElementById('compte-etat');
    if (dedans) dedans.textContent = texte;
    if (dehors) dehors.textContent = texte;
  }

  /** ⚠️ Le mot de passe ne reste dans le champ NI apres un succes NI apres un echec. */
  function envoyerEffacer(ev) {
    if (ev) ev.preventDefault();
    const champEl = doc.getElementById('compte-effacer-passe');
    const motDePasse = champEl ? String(champEl.value || '').trim() : '';
    if (!motDePasse) { direEffacer('Il faut ton mot de passe pour confirmer.'); return null; }
    direEffacer('Effacement…');
    return Compte.effacer(motDePasse).then(function (r) {
      if (champEl) champEl.value = '';
      if (r.ok) {
        effacerDemande = false;
        direEffacer('Compte effacé. Les parties de ce navigateur sont toujours là.');
      } else {
        direEffacer(r.motif || 'Refusé.');
      }
      majCompte();
      return r;
    });
  }

  /** Le NIP tape au verrou. ⚠️ `Compte.deverrouiller` rend `{ok:false, motif, essaisRestants}`
      sur un echec, et l'etat public complet (avec `ok:true`) sur un succes — jamais de
      troisieme forme, pour que ce geste se lise d'un coup d'oeil. */
  function deverrouillerNip(ev) {
    if (ev) ev.preventDefault();
    const nipEl = doc.getElementById('nip-code'), etatEl = doc.getElementById('nip-etat');
    const nip = nipEl ? String(nipEl.value || '').trim() : '';
    if (etatEl) etatEl.textContent = 'Vérification…';
    return Compte.deverrouiller(nip).then(function (r) {
      if (nipEl) nipEl.value = '';
      if (!r.ok && etatEl) {
        etatEl.textContent = r.motif === 'efface' ? 'Cinq essais ratés : NIP effacé — le mot de passe est nécessaire.'
          : r.motif === 'faux' ? 'NIP incorrect — ' + r.essaisRestants + (r.essaisRestants > 1 ? ' essais restants' : ' essai restant')
          : (r.motif || 'Refusé.');
      }
      majCompte();
      return r;
    });
  }

  /** Ce que l'ecran du compte montre. Ferme, il demande un pseudo ; ouvert, il
      montre les trois cases TELLES QUE LE SERVEUR LES CONNAIT — c'est la seule
      fenetre sur ce qui est monte, et « ça a marché? » est la premiere question
      qu'on se pose en changeant d'appareil. */
  function majCompte(vue) {
    if (!doc) return;
    const v = vue || Compte.etat();
    // LE NIP (M14, 3e vague) : SEUL a l'ecran tant qu'on n'a pas tape les quatre
    // chiffres — jamais en meme temps que le formulaire de mot de passe. Le
    // contournement local (`nipBypasse`) montre le mot de passe sans y toucher.
    const verrouille = v.etat === 'verrouille' && !nipBypasse;
    const ouvert = v.etat === 'ouvert';
    const nipForm = doc.getElementById('nip-form');
    const form = doc.getElementById('compte-form');
    const liste = doc.getElementById('compte-parties');
    const mot = doc.getElementById('compte-mot');
    const partir = doc.getElementById('bouton-compte-deconnexion');
    const bouton = doc.getElementById('bouton-compte');
    const etatEl = doc.getElementById('compte-etat');
    const activerForm = doc.getElementById('nip-activer-form');
    const retrait = doc.getElementById('nip-retrait');
    const effacerLigne = doc.getElementById('compte-effacer-ligne');
    const effacerForm = doc.getElementById('compte-effacer-form');
    const garde = doc.getElementById('compte-garde');
    // ⚠️ Effacer n'existe QUE sur un compte ouvert (le serveur le refuserait de toute facon),
    // et la confirmation prend la place du bouton — jamais les deux a l'ecran.
    if (effacerLigne) effacerLigne.hidden = !ouvert || effacerDemande;
    if (effacerForm) effacerForm.hidden = !ouvert || !effacerDemande;
    // « Ce qu'on garde » se lit partout SAUF sous le verrou, qui montre le NIP seul.
    if (garde) garde.hidden = verrouille;
    if (nipForm) nipForm.hidden = !verrouille;
    if (form) form.hidden = verrouille || ouvert;
    if (mot) mot.hidden = verrouille;
    if (liste) liste.hidden = verrouille;
    if (partir) partir.hidden = verrouille || !ouvert;
    if (activerForm) activerForm.hidden = !ouvert || v.nipConfigure;
    if (retrait) retrait.hidden = !ouvert || !v.nipConfigure;
    if (bouton) bouton.textContent = verrouille ? 'Compte verrouillé' : ouvert ? 'Compte : ' + v.pseudo : 'Compte';
    if (mot && !verrouille) {
      mot.textContent = ouvert ? 'Connecté comme ' + v.pseudo + '. Tes parties montent toutes seules.'
        : v.etat === 'hors-ligne' ? 'Pas de réseau : le compte attendra. Le jeu, lui, se joue hors ligne.'
        : v.etat === 'indisponible' ? 'Les comptes sont indisponibles pour l’instant. Le jeu, lui, tourne.'
        : MOT_DU_COMPTE;
    }
    // ⚠️ Un message de session coupee doit rester lisible : il n'est efface que
    // par le geste suivant, jamais par une mise a jour qui passe.
    if (etatEl && !ouvert && !verrouille && v.message) etatEl.textContent = v.message;
    if (!liste) return;
    liste.innerHTML = '';
    if (!ouvert) return;
    for (const c of v.cases) {
      const li = doc.createElement('li');
      const nom = doc.createElement('span');
      const a = c.serveur && c.serveur.apercu;
      nom.textContent = 'Partie ' + c.emplacement + (a ? ' · jour ' + a.jour + ' · ' + a.argent + ' $' : ' · vide');
      const detail = doc.createElement('span');
      detail.textContent = c.decision === 'trancher' ? 'deux versions — choisis en jouant'
        : c.serveur && c.serveur.sauvee_le ? dateCourte(c.serveur.sauvee_le) : '—';
      li.appendChild(nom); li.appendChild(detail);
      liste.appendChild(li);
    }
  }

  /** ⚠️ Le mot de passe LIE L'APPAREIL, une fois : il ne reste pas dans le champ
      apres coup, et rien ne le garde nulle part. */
  function envoyerCompte(quoi) {
    const etatEl = doc.getElementById('compte-etat');
    const donnees = { pseudo: champ('compte-pseudo'), mot_de_passe: champ('compte-passe') };
    if (quoi === 'inscription') donnees.courriel = champ('compte-courriel');
    if (!donnees.pseudo || !donnees.mot_de_passe) {
      if (etatEl) etatEl.textContent = 'Il faut un pseudo et un mot de passe.';
      return null;
    }
    if (etatEl) etatEl.textContent = quoi === 'inscription' ? 'Création du compte…' : 'Connexion…';
    const promesse = quoi === 'inscription' ? Compte.inscrire(donnees) : Compte.connecter(donnees);
    return promesse.then(function (v) {
      const passe = doc.getElementById('compte-passe');
      if (passe) passe.value = '';
      majCompte(v);
      if (etatEl) etatEl.textContent = v.etat === 'ouvert' ? 'Bonjour, ' + v.pseudo + ' — tes parties sont là.' : (v.message || 'Refusé.');
      return v;
    });
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

  //: Les palettes du moment de la journee (`MOMENTS`). ⚠️ Le soleil est
  //: ORANGE, pas jaune : le jaune est a l'etoile de recherche et le dore a
  //: l'argent, juste au-dessus. L'aube est rose et claire, le crepuscule
  //: rouge et sombre : le meme soleil couche, deux moments qu'on ne confond pas.
  const MOMENT_PALETTES = {
    jour: { dessin: 'jour', pal: { s: '#ff9f43', r: '#ffc98a' } },
    aube: { dessin: 'levant', pal: { s: '#ffc06a', r: '#ffe0a0', h: '#9fb4e0' } },
    crepuscule: { dessin: 'levant', pal: { s: '#ff5e3a', r: '#ff9a5c', h: '#7a5a9e' } },
    nuit: { dessin: 'nuit', pal: { l: '#dfe6ff' } },
  };
  const MOMENT_L = MOMENTS.jour[0].length;
  const MOMENT_H = MOMENTS.jour.length;

  /** Un moment cuit une fois (et son ombre, comme le texte du HUD : sans elle,
      le soleil disparait sur un trottoir en plein jour). */
  function momentCuit(periode, ombre) {
    const m = MOMENT_PALETTES[periode];
    const grille = MOMENTS[m.dessin];
    return Atlas.cuirePeintre('moment|' + periode + (ombre ? '|ombre' : ''), MOMENT_L, MOMENT_H, function (c) {
      for (let y = 0; y < MOMENT_H; y++) {
        for (let x = 0; x < MOMENT_L; x++) {
          const ch = grille[y][x];
          if (ch === '.' || !m.pal[ch]) continue;
          c.fillStyle = ombre ? 'rgba(11,10,18,0.8)' : m.pal[ch];
          c.fillRect(x, y, 1, 1);
        }
      }
    });
  }

  /** L'icone du moment, le coin haut-gauche en (x, y). */
  function dessinerMoment(ctx, x, y) {
    const p = Monde.periode();
    ctx.drawImage(momentCuit(p, true), x + 1, y + 1);
    ctx.drawImage(momentCuit(p, false), x, y);
    B.stats.images += 2;
    return p;
  }

  function barre(ctx, x, y, l, h, frac, couleur) {
    ctx.fillStyle = '#101018'; ctx.fillRect(x - 1, y - 1, l + 2, h + 2);
    ctx.fillStyle = '#2a2a3a'; ctx.fillRect(x, y, l, h);
    ctx.fillStyle = couleur; ctx.fillRect(x, y, Math.round(l * borner(frac, 0, 1)), h);
    B.stats.rects += 3;
  }

  //: L'initiale de chaque direction du piratage (`Histoire.DIRS_PIRATAGE`) —
  //: le meme H/B/G/D que le clavier (`MAP_TOUCHES.haut` commence par une
  //: fleche, mais la police du HUD n'en dessine pas).
  const LETTRE_PIRATAGE = { haut: 'H', bas: 'B', gauche: 'G', droite: 'D' };

  /** La sequence du piratage en cours (`B.piratage`), et sa progression : un
      cran par direction, faite (vert), en cours (or, celle qu'on vise), a
      venir (gris). Le meme geste que la barre de charge du coup fort — on lit
      la couleur, pas les lettres, une fois qu'on a appris le motif. */
  function dessinerPiratage(ctx) {
    const r = B.piratage;
    if (!r) return;
    const n = r.sequence.length, pas = 14, largeur = n * pas + 6;
    const x0 = Math.round((VW - largeur) / 2), y0 = 90;
    ctx.fillStyle = 'rgba(11,10,18,0.82)'; ctx.fillRect(x0 - 5, y0 - 11, largeur + 10, 25);
    B.stats.rects++;
    for (let i = 0; i < n; i++) {
      const fait = i < r.pos, enCours = i === r.pos;
      ctx.fillStyle = fait ? '#1e3a1e' : (enCours ? '#4a3a10' : '#26262e');
      ctx.fillRect(x0 + i * pas, y0, pas - 3, 11);
      B.stats.rects++;
      texte(ctx, LETTRE_PIRATAGE[r.sequence[i]], x0 + i * pas + 3, y0 + 2,
            fait ? '#8fd46a' : (enCours ? '#e8b33c' : '#5a5a6a'), 1);
    }
    const consigne = 'FRAPPE POUR ABANDONNER';
    texte(ctx, consigne, Math.round((VW - Atlas.largeurTexte(consigne, 1)) / 2), y0 + 15, '#8a8698', 1);
    noter('piratage', x0 - 5, y0 - 11, largeur + 10, 25);
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
  let marqueurs = { joueur: null, cible: null, boulot: null, ecran: null };

  //: Ce qu'on va chercher (le client, le blesse) : bleu. La destination : or.
  const COULEUR_RAMASSE = '#6f9fd8', COULEUR_DESTINATION = '#e8b33c';

  /** Le boulot en cours, comme un GPS : ou est le client, ou va la course.

      ⚠️ Demande de Martin (17 sept. 2026) : « je veux les fleches pour savoir
      ou trouver le client ». Le client n'avait qu'un point bleu qui clignotait
      sur la mini-carte, et seulement s'il tombait dans son cadre : ni fleche au
      bord de l'ecran, ni fleche au bord de la mini-carte — alors qu'un
      objectif de mission avait les deux. */
  function cibleDuBoulot() {
    const b = Missions.boulot, c = b.cible;
    if (!c) return null;
    const ramasse = b.etape === 'ramasse';
    return { x: c.x, y: c.y, nom: ramasse ? 'CLIENT' : (c.nom || ''), couleur: ramasse ? COULEUR_RAMASSE : COULEUR_DESTINATION };
  }

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

  /** Les cles d'une table du paquet, dans l'ordre ou Python l'a ECRITE (`rang`) :
      le paquet trie ses cles, et `Object.keys` rendait l'alphabet. */
  function parRang(table) {
    return Object.keys(table).sort(function (a, b) { return (table[a].rang || 0) - (table[b].rang || 0); });
  }

  /** La legende de la carte, BATIE depuis la table des couleurs : les familles
      des lieux que cette ville porte, dans l'ordre de la table. */
  function legendeDeLaCarte(carte) {
    const familles = famillesDeLieu();
    const portees = {};
    for (const point of lieuxSurLaCarte(carte)) if (point.famille) portees[point.famille] = true;
    // ⚠️ L'ordre est celui de la TABLE, pas celui des lieux rencontres : sinon la
    // legende se reordonne d'une ville a l'autre, et on la relit a chaque partie.
    return parRang(familles).filter(function (nom) { return portees[nom]; }).map(function (nom) {
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

  /** Un pointeur qui descend sur (x, y) : sa pointe y touche, un lisere sombre
      autour pour qu'il se lise sur le bleu de l'eau comme sur le gris des blocs. */
  function pointeur(ctx, x, y, couleur) {
    ctx.fillStyle = '#101018';
    for (let i = 0; i <= 4; i++) ctx.fillRect(x - 4 + i, y - 5 + i, 9 - 2 * i, 1);
    ctx.fillStyle = couleur;
    for (let i = 0; i <= 3; i++) ctx.fillRect(x - 3 + i, y - 4 + i, 7 - 2 * i, 1);
    B.stats.rects += 9;
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
  /** Les lieux qu'on montre sur la carte : pas ceux qu'elle cache encore (l'aerogare,
      tant que le pont de l'aeroport n'est pas fini — `Monde.masquee`). */
  function lieuxSurLaCarte(carte) {
    return (carte.points || []).filter(function (p) { return !Monde.masquee(p.x, p.y, carte); });
  }

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
    for (const point of lieuxSurLaCarte(carte)) {
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
    // ⚠️ Hors du cadre, une FLECHE, comme l'objectif : un client ou une course
    // hors de la mini-carte n'y laissait rien, pas meme de quel cote chercher.
    const boulot = cibleDuBoulot();
    marqueurs.boulot = null;
    if (boulot) {
      const bx = MINI.x + Math.round(boulot.x / TT) - sx, by = MINI.y + Math.round(boulot.y / TT) - sy;
      if (bx >= MINI.x && bx < MINI.x + MINI.l && by >= MINI.y && by < MINI.y + MINI.h) {
        const bat = (B.image >> 4) % 2 === 0;
        if (bat) {
          ctx.fillStyle = boulot.couleur;
          ctx.fillRect(bx - 1, by - 1, 3, 3);
          B.stats.rects++;
        }
        marqueurs.boulot = { x: bx, y: by, forme: 'carre', visible: bat, dedans: true, couleur: boulot.couleur };
      } else {
        const cx = MINI.x + MINI.l / 2, cy = MINI.y + MINI.h / 2;
        const angle = Math.atan2(by - cy, bx - cx);
        const fx = borner(cx + Math.cos(angle) * MINI.l, MINI.x + 4, MINI.x + MINI.l - 5);
        const fy = borner(cy + Math.sin(angle) * MINI.h, MINI.y + 4, MINI.y + MINI.h - 5);
        flecheDeCarte(ctx, fx, fy, angle, boulot.couleur);
        marqueurs.boulot = { x: Math.round(fx), y: Math.round(fy), forme: 'fleche', visible: true,
                             dedans: false, angle: angle, couleur: boulot.couleur };
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
    // ⚠️ Le zonage prend une rangee sous le titre : sa legende n'a pas sa place
    // dans le bandeau du bas, qui tient deja les familles de lieux sur trois rangees.
    const zonage = legendeDuZonage(carte);
    const yHaut = zonage.length ? 24 : 14, yBas = VH - 38;
    // ⚠️ LA CARTE QU'ON CONNAIT : tant que l'ile de l'aeroport est cachee, il n'y a que
    // de l'eau sous la ville, et la ville garde l'echelle qu'elle avait avant lui.
    const hauteur = Monde.hauteurConnue(carte, B.exterieur ? B.exterieur.y : j.y);
    const brut = Math.min((VW - 20) / carte.w, (yBas - yHaut) / hauteur);
    const echelle = brut >= 1 ? Math.floor(brut) : brut;
    const l = carte.w * echelle, h = hauteur * echelle;
    const ox = Math.round((VW - l) / 2), oy = yHaut + Math.round((yBas - yHaut - h) / 2);
    ctx.imageSmoothingEnabled = false;
    ctx.drawImage(mini, 0, 0, carte.w, hauteur, ox, oy, l, h);
    B.stats.images++;
    // Le calque du ZONAGE, par-dessus les tuiles et sous tout le reste : les
    // blocs se teignent de leur usage, les rues restent grises et se lisent.
    const calque = Monde.calqueDeZonage(carte);
    if (calque) {
      ctx.globalAlpha = CALQUE_ALPHA;
      ctx.drawImage(calque, 0, 0, carte.w, hauteur, ox, oy, l, h);
      ctx.globalAlpha = 1;
      B.stats.images++;
    }
    const pos = function (x, y) { return { x: ox + Math.round(x / TT * echelle), y: oy + Math.round(y / TT * echelle) }; };
    dessinerLignes(ctx, pos);
    Metro.dessinerSurLaCarte(ctx, pos);
    Traversier.dessinerSurLaCarte(ctx, pos);
    for (const point of lieuxSurLaCarte(carte)) {
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
    // Le boulot : un POINTEUR pose au-dessus du client ou de la course.
    // ⚠️ Pas un carre, comme sur la mini-carte : ici les lieux SONT des carres,
    // et ceux de « TES PLACES » sont dores comme la course — le repere se
    // perdait dans la legende. Il oscille d'un pixel au lieu de clignoter : on
    // ne cache pas ce qu'on cherche.
    const boulot = cibleDuBoulot();
    marqueurs.boulot = null;
    if (boulot) {
      const p = pos(boulot.x, boulot.y);
      const y = p.y - 4 - ((B.image >> 4) % 2);
      pointeur(ctx, p.x, y, boulot.couleur);
      marqueurs.boulot = { x: p.x, y: y, forme: 'pointeur', visible: true, dedans: true, couleur: boulot.couleur };
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
    dessinerLegendeDuZonage(ctx, zonage);
    const aide = (gps ? gps.nom.toUpperCase() + ' · ' : '') + 'N : FERMER';
    texte(ctx, aide, (VW - Atlas.largeurTexte(aide, 1)) / 2, VH - 12, '#cdc6e6', 1);
  }

  /** Le bandeau du mode photo (M14) : un bord discret plutot que le fond noir
      de la carte — c'est la ville qu'on cadre, pas une fiche par-dessus elle. */
  function dessinerPhoto(ctx) {
    const nom = FILTRES_PHOTO[B.photo.filtre].nom;
    ctx.fillStyle = 'rgba(11,10,18,0.55)'; ctx.fillRect(0, VH - 13, VW, 13); B.stats.rects++;
    texte(ctx, 'MODE PHOTO · ' + nom, 6, VH - 10, '#efe6d0', 1);
    const aide = Entree.estTactile ? 'ACTION : CAPTURER · ARME : FILTRE'
      : 'ACTION : CAPTURER · ARME : FILTRE · ANNULER : RETOUR';
    texte(ctx, aide, VW - 6 - Atlas.largeurTexte(aide, 1), VH - 10, '#cdc6e6', 1);
  }

  //: La transparence du calque de zonage. ⚠️ Assez pour qu'un bloc d'usine et
  //: un bloc de maisons ne se confondent plus, pas assez pour effacer les toits
  //: et les cours qu'on reconnaissait deja.
  const CALQUE_ALPHA = 0.42;

  /** La legende du zonage, BATIE depuis la table (`carte.zonage`), dans son
      ordre, et seulement les usages que cette ville porte. */
  function legendeDuZonage(carte) {
    const table = (carte && carte.def && carte.def.zonage) || {};
    const lettres = ((carte && carte.def && carte.def.grille && carte.def.grille.usage) || []).join('');
    return parRang(table).filter(function (usage) { return lettres.indexOf(table[usage].lettre) >= 0; })
      .map(function (usage) { return { usage: usage, couleur: table[usage].couleur, libelle: table[usage].libelle }; });
  }

  /** Une rangee sous le titre, centree : une pastille et un mot par usage. */
  function dessinerLegendeDuZonage(ctx, lignes) {
    if (!lignes.length) return;
    const largeurs = lignes.map(function (e) { return 8 + Atlas.largeurTexte(e.libelle, 1); });
    const total = largeurs.reduce(function (a, b) { return a + b; }, 0) + 10 * (lignes.length - 1);
    let x = Math.round((VW - total) / 2);
    lignes.forEach(function (entree, i) {
      ctx.fillStyle = '#101018'; ctx.fillRect(x - 1, 15, 6, 6);
      ctx.fillStyle = entree.couleur; ctx.fillRect(x, 16, 4, 4);
      texte(ctx, entree.libelle, x + 8, 15, '#cdc6e6', 1);
      B.stats.rects += 2;
      x += largeurs[i] + 10;
    });
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
    // ⚠️ LE HUD SE TAIT PENDANT UNE SCENE (l'ouverture la premiere). Vie, souffle, etoiles, argent,
    // arme, mini-carte, heure : une barre de vie par-dessus une scene ou l'on
    // ne joue pas encore, c'est une scene que personne ne regarde. Seule la
    // boite de dialogue reste, plus bas — c'est elle qui porte les mots.
    if ((B.etat === 'jeu' || B.etat === 'pause') && !B.scene) {
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
        } else if (j.passager) {
          ligneBoulot = Autobus.ligneDuHud(j);
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
      // Le moment de la journee, devant l'heure : on lit « la nuit » d'un coup
      // d'oeil, sans faire le calcul de 20:47. La boite de l'heure l'englobe —
      // la ligne d'objectif doit passer dessous a elle aussi.
      const xMoment = VW - marge - largeurHeure - MOMENT_L - 3;
      const moment = dessinerMoment(ctx, xMoment, 20);
      ancres.push({ nom: 'moment', x: xMoment, y: 20, l: MOMENT_L, h: MOMENT_H, periode: moment });
      const boiteHeure = { x: xMoment, y: 20, l: VW - marge - xMoment, h: 7 };
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
      // ⚠️ UNE fleche au bord de l'ecran, et c'est le BOULOT qui la prend quand
      // il y en a un : on a klaxonne pour ce client, c'est lui qu'on cherche.
      // Deux fleches de deux couleurs, chacune avec ses metres, se marcheraient
      // dessus au meme bord. L'objectif reste sur la mini-carte.
      // ⚠️ EN COURSE, PAS DE FLECHE NI DE METRES ICI (Martin, 21 sept. 2026) :
      // les fleches au sol (`Histoire.dessinerCheminCourse`) montrent la piste
      // elle-meme — une fleche hors cadre en plus ferait double emploi.
      const boulotEcran = !B.interieur && j && !Histoire.estCourse() ? cibleDuBoulot() : null;
      const gps = boulotEcran || (!B.interieur && j && !Histoire.estCourse() ? Histoire.cible() : null);
      marqueurs.ecran = null;
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
          marqueurs.ecran = { x: Math.round(fx), y: Math.round(fy), angle: a, metres: Math.round(d / TT),
                              couleur: gps.couleur || '#e8b33c', quoi: boulotEcran ? 'boulot' : 'histoire' };
        }
      }
      dessinerPiratage(ctx);
      // Message.
      if (B.msg && B.msgT > 0) {
        const l = Atlas.largeurTexte(B.msg, 2);
        ctx.fillStyle = 'rgba(11,10,18,0.75)'; ctx.fillRect((VW - l) / 2 - 6, 40, l + 12, 16);
        Atlas.texte(ctx, B.msg, (VW - l) / 2, 43, '#efe6d0', 2);
        B.msgT--;
      }
      if (B.etat === 'jeu') iconeDeChargement(ctx);
      if (B.etat === 'pause') {
        ctx.fillStyle = 'rgba(11,10,18,0.6)'; ctx.fillRect(0, 0, VW, VH);
        dessinerMenu(ctx);
      }
    }
    if (B.etat === 'jeu') {
      // L'ouverture passe SOUS la boite de dialogue : le noir et le titre sont
      // la scene, les mots sont par-dessus, toujours lisibles.
      dessinerScene(ctx);
      invite(ctx);
      attenteALAbribus(ctx);
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
    // Le choix des parties : la ville vide du titre, assombrie, derriere.
    if (B.etat === 'titre' && B.menu) {
      ctx.fillStyle = 'rgba(11,10,18,0.6)'; ctx.fillRect(0, 0, VW, VH); B.stats.rects++;
      dessinerMenu(ctx);
    }
    if (B.etat === 'carte') dessinerCarte(ctx);
    if (B.etat === 'photo') dessinerPhoto(ctx);
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

  return { init, voile, etat, progression, partDesScripts, finirChargement, message, dialogue, ouvrirMenu, fermerMenu, rafraichirMenu, majMenu, menuPause, menuDebug, menuSautMissions, menuSautDefis, menuJukebox, pointDuDefi, menuCarnet,
    ouvrirOnglet, toucherMenu, onglets: function () { return ongletsVisibles().map(function (o) { return o.slug; }); },
    ciblesDuMenu: function () { return cibles.slice(); }, menuCarnetEnCours, menuCarnetJournal, menuCarnetRepertoire, menuCarnetFiche, menuOptions, menuManette, menuManetteBoutons, menuBilan,
    menuCommandes, ouvrirCommandes, majAideDuTitre, lignesDAide, glypheDAction,
    menuParties, menuEffacer, menuCopier, tempsDeJeu, quand,
    legendeDeLaCarte, legendeDuZonage, lieuxSurLaCarte, couleurDeLieu, cibleDuBoulot, PULSE_JOUEUR, BATTEMENT_CIBLE, CALQUE_ALPHA,
    marqueurs: function () { return marqueurs; },
    get voileCourant() { return voileCourant; },
           majAvisSon,
           dessiner, dessinerRoue, rayonDeLaRoue, LOGO_ECHELLE, LOGO_Y, posteDeLaRoue, miniCarte, MINI,
           montrerCompte, majCompte, envoyerCompte, menuVersions, deverrouillerNip, envoyerEffacer, majDefiDuJour,
           ancres: function () { return ancres; } };
})();
