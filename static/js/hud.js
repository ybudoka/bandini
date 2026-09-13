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
  }

  function voile(nom) {
    for (const n in voiles) voiles[n].hidden = (n !== nom);
  }

  function etat(nom) { if (racine) racine.dataset.etat = nom; }

  function message(texte, duree) { B.msg = texte; B.msgT = duree || 120; }

  // --- Menus canvas ---------------------------------------------------------------
  //: Un menu = { titre, items: [{ libelle, detail, actif, faire }], curseur, aide, sur, obligatoire }.
  //: `faire()` rend true pour fermer le menu, false pour le laisser ouvert
  //: (on achete trois hot-dogs sans rouvrir le comptoir).

  let repetT = 0;

  function ouvrirMenu(menu) {
    menu.curseur = menu.curseur || 0;
    B.menu = menu;
    Entree.contexte('menu');
    Son.SFX.menu();
  }

  function fermerMenu() {
    B.menu = null;
    Entree.contexte(B.joueur && B.joueur.dansVehicule ? 'vehicule' : 'pied');
  }

  /** Navigation : haut/bas (clavier, stick, joystick), ACTION choisit, FRAPPE ou annuler ferme. */
  function majMenu() {
    const m = B.menu;
    if (!m) return;
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
      } else Son.SFX.erreur();
    }
    // Un menu `obligatoire` (l'arrestation) ne se ferme que par un choix.
    if (!m.obligatoire && (Entree.neuf('annuler') || Entree.neuf('attaque') || Entree.neuf('pause'))) fermerMenu();
  }

  function dessinerMenu(ctx) {
    const m = B.menu;
    if (!m) return;
    const l = 300, h = Math.min(VH - 30, 40 + m.items.length * 14 + (m.aide ? 14 : 0));
    const x = (VW - l) / 2, y = (VH - h) / 2;
    ctx.fillStyle = 'rgba(11,10,18,0.92)'; ctx.fillRect(x, y, l, h);
    ctx.fillStyle = '#e8b33c'; ctx.fillRect(x, y, l, 1); ctx.fillRect(x, y + h - 1, l, 1);
    texte(ctx, m.titre, x + 8, y + 7, '#e8b33c', 2);
    if (m.sur) texte(ctx, m.sur, x + l - 8 - Atlas.largeurTexte(m.sur, 1), y + 10, '#cdc6e6', 1);
    m.items.forEach(function (item, i) {
      const yy = y + 28 + i * 14;
      const choisi = i === m.curseur;
      const actif = item.actif !== false;
      if (choisi) { ctx.fillStyle = 'rgba(232,179,60,0.18)'; ctx.fillRect(x + 4, yy - 3, l - 8, 12); }
      texte(ctx, (choisi ? '> ' : '  ') + item.libelle, x + 8, yy, actif ? (choisi ? '#efe6d0' : '#cdc6e6') : '#6a6678', 1);
      if (item.detail) texte(ctx, item.detail, x + l - 8 - Atlas.largeurTexte(item.detail, 1), yy, actif ? '#e8b33c' : '#6a6678', 1);
    });
    if (m.aide) texte(ctx, m.aide, x + 8, y + h - 12, '#8a8698', 1);
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
    return { titre: 'OPTIONS', items: [
      bascule('sang', 'SANG'),
      bascule('vibration', 'VIBRATION'),
      bascule('muet', 'SON COUPE'),
      bascule('daltonien', 'PALETTE DALTONIENNE'),
      bascule('trace', 'TRACE DES VEHICULES'),
      { libelle: 'RETOUR', faire: function () { ouvrirMenu(menuPause()); return false; } },
    ], aide: 'ACTION : CHANGER · FRAPPE : FERMER' };
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

  function menuPause() {
    return { titre: 'PAUSE', sur: 'JOUR ' + B.partie.jour + ' ' + Monde.heureTexte(), items: [
      { libelle: 'REPRENDRE', faire: function () { Jeu.reprendre(); return true; } },
      { libelle: 'CARTE DE LA VILLE', faire: function () { Jeu.ouvrirCarte(); return true; } },
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
    if (B.cinema && (B.t >> 4) % 2 === 0) {
      const suite = B.cinema.i < B.cinema.lignes.length - 1 ? 'ACTION >' : 'ACTION > FIN';
      texte(ctx, suite, VW - 18 - Atlas.largeurTexte(suite, 1), VH - 16, '#8a8698', 1);
    }
    if (d.duree && d.t > d.duree) B.dialogue = null;
    B.stats.rects += 2;
  }

  /** Un fondu au noir, avec une ligne au milieu : ce qui se passe ne se
      montre pas. Sert aussi aux portes et aux ellipses (M5). */
  function fondu(duree, texte) {
    B.fondu = { t: 0, duree: duree || 90, texte: texte || null };
  }

  function dessinerFondu(ctx) {
    const f = B.fondu;
    if (!f) return;
    f.t++;
    const part = f.t / f.duree;
    const alpha = part < 0.5 ? part * 2 : (1 - part) * 2;
    ctx.fillStyle = 'rgba(11,10,18,' + Math.min(1, alpha).toFixed(3) + ')';
    ctx.fillRect(0, 0, VW, VH);
    if (f.texte && part > 0.35 && part < 0.75) {
      const l = Atlas.largeurTexte(f.texte, 1);
      Atlas.texte(ctx, f.texte, (VW - l) / 2, VH / 2 - 4, '#cdc6e6', 1);
    }
    if (f.t >= f.duree) B.fondu = null;
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
  const COULEUR_BLIP = {
    planque: '#e8b33c', garage: '#e8b33c', bar: '#e8b33c', kiosque: '#e8b33c',
    poste: '#6f9fd8', hopital: '#d86f7f',
    armurerie: '#8ad26a', vetements: '#8ad26a', casse_croute: '#8ad26a',
    terminus: '#cdc6e6',
  };

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
      ctx.fillStyle = COULEUR_BLIP[point.slug] || '#cdc6e6'; ctx.fillRect(px, py, 2, 2);
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
    // L'histoire : l'objectif, le donneur a aller voir, le defi — un blip qui clignote.
    const gps = Histoire.cible();
    if (gps && (B.t >> 3) % 2 === 0) {
      const gx = MINI.x + Math.round(gps.x / TT) - sx, gy = MINI.y + Math.round(gps.y / TT) - sy;
      const bx = borner(gx, MINI.x, MINI.x + MINI.l - 3), by = borner(gy, MINI.y, MINI.y + MINI.h - 3);   // au bord s'il est hors carte
      ctx.fillStyle = gps.couleur || '#e8b33c'; ctx.fillRect(bx, by, 3, 3);
      B.stats.rects++;
    }
    // Le taxi : le client (bleu) ou la destination (or) clignote.
    const cible = Missions.taxi.etape === 'attente' ? Missions.taxi.client : Missions.taxi.destination;
    if (cible && (B.t >> 4) % 2 === 0) {
      const bx = MINI.x + Math.round(cible.x / TT) - sx, by = MINI.y + Math.round(cible.y / TT) - sy;
      if (bx >= MINI.x && bx < MINI.x + MINI.l && by >= MINI.y && by < MINI.y + MINI.h) {
        ctx.fillStyle = Missions.taxi.etape === 'attente' ? '#6f9fd8' : '#e8b33c';
        ctx.fillRect(bx - 1, by - 1, 3, 3);
        B.stats.rects++;
      }
    }
    // Le joueur par-dessus tout le reste : c'est lui qu'on cherche des yeux.
    const jx = MINI.x + Math.round(j.x / TT) - sx, jy = MINI.y + Math.round(j.y / TT) - sy;
    ctx.fillStyle = '#101018'; ctx.fillRect(jx - 1, jy - 1, 4, 4);
    ctx.fillStyle = '#ffffff'; ctx.fillRect(jx, jy, 2, 2);
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
    const brut = Math.min((VW - 20) / carte.w, (VH - 40) / carte.h);
    const echelle = brut >= 1 ? Math.floor(brut) : brut;
    const l = carte.w * echelle, h = carte.h * echelle;
    const ox = Math.round((VW - l) / 2), oy = Math.round((VH - h) / 2) + 6;
    ctx.imageSmoothingEnabled = false;
    ctx.drawImage(mini, 0, 0, carte.w, carte.h, ox, oy, l, h);
    B.stats.images++;
    const pos = function (x, y) { return { x: ox + Math.round(x / TT * echelle), y: oy + Math.round(y / TT * echelle) }; };
    for (const point of carte.points) {
      const p = pos(point.x * TT, point.y * TT);
      ctx.fillStyle = '#101018'; ctx.fillRect(p.x - 2, p.y - 2, 5, 5);
      ctx.fillStyle = COULEUR_BLIP[point.slug] || '#cdc6e6'; ctx.fillRect(p.x - 1, p.y - 1, 3, 3);
      B.stats.rects += 2;
    }
    if (B.recherche.etoiles > 0) {
      ctx.fillStyle = '#4f8fe8';
      for (const e of (B.exterieur ? B.exterieur.entites : B.entites)) {
        if (!(e.agent && e.vivant) && !(e.type === 'vehicule' && e.conducteur === 'police')) continue;
        const p = pos(e.x, e.y); ctx.fillRect(p.x, p.y, 2, 2); B.stats.rects++;
      }
    }
    const gps = Histoire.cible();
    if (gps && (B.t >> 3) % 2 === 0) { const p = pos(gps.x, gps.y); ctx.fillStyle = gps.couleur || '#e8b33c'; ctx.fillRect(p.x - 2, p.y - 2, 5, 5); B.stats.rects++; }
    const pj = pos(B.exterieur ? B.exterieur.x : j.x, B.exterieur ? B.exterieur.y : j.y);
    ctx.fillStyle = '#101018'; ctx.fillRect(pj.x - 2, pj.y - 2, 6, 6);
    ctx.fillStyle = '#ffffff'; ctx.fillRect(pj.x - 1, pj.y - 1, 4, 4);
    B.stats.rects += 2;
    const zone = Monde.zoneA ? (B.exterieur ? null : Monde.zoneA(j.x, j.y)) : null;
    const ville = (carte.def && carte.def.nom ? carte.def.nom : 'Baie-des-Brumes').toUpperCase();
    const titre = ville + (zone ? ' — ' + zone.nom.toUpperCase() : '');
    texte(ctx, titre, (VW - Atlas.largeurTexte(titre, 1)) / 2, 6, '#e8b33c', 1);
    const aide = (gps ? gps.nom.toUpperCase() + ' · ' : '') + 'N : FERMER';
    texte(ctx, aide, (VW - Atlas.largeurTexte(aide, 1)) / 2, VH - 12, '#cdc6e6', 1);
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
      barre(ctx, 6, 13, 60, 3, v ? v.vie / v.vieMax : (j ? j.endurance / 100 : 1), v ? '#7fb3d8' : '#e8b33c');
      noter('vie', 6, 6, 60, 10);
      if (v) {
        const kmh = Math.round(Math.abs(v.vitesse) / v.def.vitesse_max * 120);
        texte(ctx, kmh + ' KM/H', 70, 8, '#efe6d0', 1);
        if (Missions.taxi.etape === 'course' && Missions.taxi.destination) {
          const d = Missions.taxi.destination;
          const dist = Math.round(Math.hypot(d.x - v.x, d.y - v.y) / TT);
          texte(ctx, 'TAXI : ' + d.nom.toUpperCase() + ' ' + dist + 'M', 70, 16, '#e8b33c', 1);
        } else if (Missions.taxi.etape === 'attente') {
          texte(ctx, 'TAXI : UN CLIENT ATTEND', 70, 16, '#e8b33c', 1);
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
      noter('argent', VW - marge - largeurArgent, 6, largeurArgent, 10);
      let etoiles = '';
      for (let i = 0; i < B.defs.recherche.etoiles_max; i++) etoiles += i < B.recherche.etoiles ? '★' : '.';
      const flash = B.recherche.flash > 0 && (B.recherche.flash >> 2) % 2 === 0;
      texte(ctx, etoiles, VW - marge - Atlas.largeurTexte(etoiles, 1), 20, flash ? '#ff5a4e' : (B.recherche.etoiles ? '#ffffff' : '#8a8698'), 1);
      const heure = 'JOUR ' + p.jour + ' ' + Monde.heureTexte();
      const largeurHeure = Atlas.largeurTexte(heure, 1);
      texte(ctx, heure, VW - marge - largeurHeure, 28, '#cdc6e6', 1);
      noter('heure', VW - marge - largeurHeure, 20, largeurHeure, 13);
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
        texte(ctx, ligne, (VW - l) / 2, 6, B.defi ? '#7fc4ff' : '#e8b33c', 1);
        noter('objectif', (VW - l) / 2, 6, l, 7);
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
    if (B.etat === 'jeu') { invite(ctx); dessinerDialogue(ctx); dessinerMenu(ctx); }
    if (B.etat === 'carte') dessinerCarte(ctx);
    dessinerFondu(ctx);
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

  return { init, voile, etat, message, fondu, dialogue, ouvrirMenu, fermerMenu, majMenu, menuPause, menuOptions, menuBilan,
           dessiner, miniCarte, MINI, montrerScores, demanderScore,
           afficherScores, ancres: function () { return ancres; } };
})();
