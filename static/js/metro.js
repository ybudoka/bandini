/* Bandini — metro : la ligne jaune, sous la ville.

   Demande de Martin (16 sept. 2026) : « je veux aussi un metro », puis, au
   choix : souterrain, comme a Montreal.

   ⚠️ PYTHON CREUSE, ICI ON ROULE. Les stations, leurs edicules et la duree de
   chaque trajet viennent du paquet (`carte.metro`, `app/metro.py`) ; le quai et
   la rame sont deux pieces du catalogue (`metro_quai`, `metro_rame`), partagees
   par toutes les stations. Ce module fait le reste : on descend par l'edicule
   (3 $), la rame entre en station a son heure, on monte, le tunnel defile dans
   les fenetres, et les portes ne s'ouvrent qu'en station — ou l'on descend sur
   le quai de CETTE station, puis on remonte a SON edicule.

   ⚠️ UNE RAME EST UNE HEURE. La ligne est une boucle : la place de chaque rame
   ne depend que du temps de la partie (`etatDeLaRame`), comme les autobus. Il
   n'y a rien a simuler, rien a oublier, et deux quais voient la meme rame
   passer a la meme heure.

   ⚠️ ON REMONTE AILLEURS QU'ON EST DESCENDU. `Jeu.entrer` retient la rue par ou
   l'on est entre (`B.exterieur`) ; ce module la recale, a chaque image, sur
   l'edicule de la station ou l'on est. La sauvegarde, la mini-carte et la
   sortie lisent `B.exterieur` : tous voient donc la bonne station. */

const Metro = (function () {
  'use strict';

  const QUAI = 'metro_quai', RAME = 'metro_rame';

  //: Les rangees du quai que le module peint par-dessus : le tunnel et sa voie
  //: (0 et 1), puis la barriere vitree et ses portes palieres (2).
  const RANGEES_TUNNEL = 2;

  //: Les portes palieres, aux colonnes du quai ou la rame ouvre les siennes.
  const PORTES_PALIERES = [2, 6, 10];

  let prepare = null, source = null;
  let dernier = { slug: null, station: null, quai: null };

  function donnees() {
    const def = B.defs && B.defs.carte;
    const brut = def && def.metro;
    if (!brut) return null;
    if (source === brut) return prepare;
    source = brut;
    // ⚠️ Le paquet ne porte que le nom et la tuile d'un edicule : le trottoir
    // devant se DEDUIT, exactement comme `metro.sortie` en Python.
    const stations = brut.stations.map(function (s, rang) {
      const cote = def.sol[s.y + 1] && def.sol[s.y + 1][s.x] === '.' ? 1 : -1;
      return { rang: rang, nom: s.nom, x: s.x, y: s.y, cote: cote, sortie: { x: s.x, y: s.y + cote } };
    });
    const h = brut.horaire, debuts = [];
    let t = 0;
    for (let i = 0; i < stations.length; i++) { debuts.push(t); t += h.arret_images + brut.trajets[i]; }
    prepare = { nom: brut.nom, couleur: brut.couleur, stations: stations, trajets: brut.trajets,
                horaire: h, debuts: debuts, periode: t };
    return prepare;
  }

  function temps() { return Autobus.tempsDeLaPartie(); }

  // --- L'horaire --------------------------------------------------------------------

  /** Ou en est la rame `k` : a quai (`station`, `reste` d'images portes
      ouvertes) ou entre deux stations (`de`, `vers`, `ecoule`, `reste`). */
  function etatDeLaRame(k, t) {
    const d = donnees(), h = d.horaire, n = d.stations.length;
    const phase = (((t === undefined ? temps() : t) + k * d.periode / h.rames) % d.periode + d.periode) % d.periode;
    for (let i = 0; i < n; i++) {
      const debut = d.debuts[i], finArret = debut + h.arret_images, fin = finArret + d.trajets[i];
      if (phase < debut || phase >= fin) continue;
      if (phase < finArret) return { k: k, quai: true, station: i, ecoule: phase - debut, reste: finArret - phase };
      return { k: k, quai: false, de: i, vers: (i + 1) % n, ecoule: phase - finArret, reste: fin - phase, duree: d.trajets[i] };
    }
    return { k: k, quai: true, station: 0, ecoule: 0, reste: h.arret_images };
  }

  /** La rame a quai a cette station, ou null. */
  function rameAQuai(station, t) {
    const d = donnees();
    for (let k = 0; k < d.horaire.rames; k++) {
      const e = etatDeLaRame(k, t);
      if (e.quai && e.station === station) return e;
    }
    return null;
  }

  /** La rame qu'on VOIT au quai de cette station : a quai, qui arrive (fin de son
      trajet) ou qui repart (debut du suivant), avec son decalage en pixels. */
  function rameEnVue(station, t) {
    const d = donnees(), approche = d.horaire.approche_images;
    const largeur = RAME_PX;
    for (let k = 0; k < d.horaire.rames; k++) {
      const e = etatDeLaRame(k, t);
      if (e.quai && e.station === station) return { e: e, dx: 0, ouverte: e.reste > 12 && e.ecoule > 12 };
      if (!e.quai && e.vers === station && e.reste < approche) {
        const q = 1 - e.reste / approche;
        return { e: e, dx: -largeur * (1 - q) * (1 - q), ouverte: false };
      }
      if (!e.quai && e.de === station && e.ecoule < approche) {
        const q = e.ecoule / approche;
        return { e: e, dx: largeur * q * q, ouverte: false };
      }
    }
    return null;
  }

  /** Dans combien d'images une rame ENTRE a cette station — la prochaine, strictement
      a venir, meme quand une autre y est deja a quai. */
  function prochaineArrivee(station, t) {
    const d = donnees();
    let mini = Infinity;
    for (let k = 0; k < d.horaire.rames; k++) {
      const phase = (((t === undefined ? temps() : t) + k * d.periode / d.horaire.rames) % d.periode + d.periode) % d.periode;
      const ecart = ((d.debuts[station] - phase) % d.periode + d.periode) % d.periode;
      mini = Math.min(mini, ecart > 0 ? ecart : d.periode);
    }
    return mini;
  }

  /** Dans combien d'images une rame a les portes ouvertes a cette station : 0 si
      elle y est deja. */
  function attenteALaStation(station, t) {
    return rameAQuai(station, t) ? 0 : prochaineArrivee(station, t);
  }

  // --- La surface : l'edicule ---------------------------------------------------------

  /** L'edicule dont on se tient sur le trottoir, devant l'escalier. */
  function ediculeSousLaMain(j) {
    const d = donnees();
    if (!d || !j || j.dansVehicule || B.interieur) return null;
    const tx = Math.floor(j.x / TT), ty = Math.floor(j.y / TT);
    return d.stations.find(function (s) {
      return s.sortie.y === ty && Math.abs(s.sortie.x - tx) <= 1 && faceA(j, (s.x + 0.5) * TT, (s.y + 0.5) * TT);
    }) || null;
  }

  function inviteDescendre(j) {
    const s = ediculeSousLaMain(j);
    return s ? 'DESCENDRE AU MÉTRO — ' + s.nom.toUpperCase() + ' — ' + donnees().horaire.tarif + ' $' : null;
  }

  /** Descendre : le tourniquet, puis l'escalier. Rend vrai (la pression est depensee). */
  function descendre(j, s) {
    const tarif = donnees().horaire.tarif;
    // ⚠️ RECHERCHE, ON NE PASSE PAS : une rame ou la police ne suit pas serait
    // la meilleure cachette du jeu, et elle depose a l'autre bout de la ville.
    if (B.recherche.etoiles > 0) { Hud.message('UN AGENT SURVEILLE LES TOURNIQUETS'); Son.SFX.erreur(); return true; }
    if (B.partie.argent < tarif) { Hud.message(tarif + ' $ — PAS ASSEZ'); Son.SFX.erreur(); return true; }
    const porte = { x: s.x, y: s.y, interieur: QUAI, lieu: 'metro', nom: 'Station ' + s.nom };
    if (!Jeu.entrer(porte)) return true;
    Missions.payer(tarif, 'MÉTRO');
    B.metro = { station: s.rang, rame: null };
    return true;
  }

  // --- Sous terre ------------------------------------------------------------------------

  function dansLeMetro() {
    return !!(B.interieur && B.metro && (B.interieur.slug === QUAI || B.interieur.slug === RAME));
  }

  /** La rue, recalee sur l'edicule de la station ou l'on est : c'est la qu'on
      remontera, la que la partie se sauve. */
  function recalerLaRue() {
    const d = donnees(), s = d && d.stations[B.metro.station];
    if (!s || !B.exterieur) return;
    B.exterieur.x = s.sortie.x * TT + 8;
    B.exterieur.y = s.sortie.y * TT + (s.cote > 0 ? 10 : 6);
    // ⚠️ Le battant s'ouvre sur l'EDICULE, pas « la tuile au-dessus du pas de
    // porte » : quand le trottoir est au nord, cette tuile-la est la chaussee.
    B.exterieur.porte = { x: s.x, y: s.y };
  }

  function prochaine(station) {
    const d = donnees();
    return d.stations[(station + 1) % d.stations.length];
  }

  /** ACTION sur le point `rame` : monter depuis le quai, descendre depuis la rame. */
  function utiliser(j, point) {
    if (!dansLeMetro()) return false;
    if (B.interieur.slug === QUAI) {
      const e = rameAQuai(B.metro.station);
      if (!e || e.reste < 20) { Hud.message('LA RAME N’EST PAS À QUAI'); return true; }
      B.metro.rame = e.k;
      return Jeu.changerEtage(RAME);
    }
    return descendreDeLaRame();
  }

  function descendreDeLaRame() {
    const e = etatDeLaRame(B.metro.rame);
    if (!e.quai || e.reste < 20) { Hud.message('LES PORTES SONT FERMÉES'); Son.SFX.erreur(); return true; }
    B.metro.station = e.station;
    const quai = (B.exterieur.carte.def.interieurs[QUAI].points || []).find(function (p) { return p.type === 'rame'; });
    return Jeu.changerEtage(QUAI, quai);
  }

  /** `Jeu.sortir` passe par ici d'abord. Rend vrai quand le metro a repondu : la
      porte de la rame mene au quai, pas a la rue. Au quai, on recale la rue et
      on laisse sortir. */
  function sortir() {
    if (!dansLeMetro()) return false;
    if (B.interieur.slug === RAME) return descendreDeLaRame();
    recalerLaRue();
    return false;
  }

  /** L'invite, sous terre : `null` quand le metro n'a rien a dire, '' pour taire
      l'invite (ACTION n'y ferait rien), sinon le geste. */
  function invite(j) {
    if (!dansLeMetro()) return null;
    const d = donnees();
    const pres = Missions.pointSousLaMain(j);
    const porte = Monde.porteDevant(j);
    if (B.interieur.slug === QUAI) {
      if (pres && pres.type === 'rame') {
        const e = rameAQuai(B.metro.station);
        return e && e.reste >= 20 ? 'MONTER — PROCHAINE : ' + prochaine(B.metro.station).nom.toUpperCase() : '';
      }
      if (porte) return 'REMONTER — ' + d.stations[B.metro.station].nom.toUpperCase();
      return null;
    }
    if ((pres && pres.type === 'rame') || porte) {
      const e = etatDeLaRame(B.metro.rame);
      return e.quai && e.reste >= 20 ? 'DESCENDRE — ' + d.stations[e.station].nom.toUpperCase() : '';
    }
    return null;
  }

  /** La ligne d'information du bas de l'ecran, sous terre. */
  function texteDInfo() {
    if (!dansLeMetro()) return null;
    const d = donnees();
    if (B.interieur.slug === QUAI) {
      const s = d.stations[B.metro.station];
      const images = attenteALaStation(B.metro.station);
      const quand = images === 0 ? 'RAME À QUAI' : 'RAME DANS ' + Math.max(1, Math.round(images / 60)) + ' S';
      return 'STATION ' + s.nom.toUpperCase() + ' · ' + quand + ' · PROCHAINE : ' + prochaine(s.rang).nom.toUpperCase();
    }
    const e = etatDeLaRame(B.metro.rame);
    if (e.quai) return 'STATION ' + d.stations[e.station].nom.toUpperCase() + ' · PORTES OUVERTES';
    return 'PROCHAINE STATION : ' + d.stations[e.vers].nom.toUpperCase();
  }

  /** A chaque image : la rue recalee, et les annonces de la rame. */
  function maj() {
    // ⚠️ PAS PENDANT UN FONDU : on appelle `Jeu.entrer` au milieu de l'image, et
    // la suite de CETTE image-la tourne encore dehors — sans cette garde, le
    // billet s'effacait avant meme qu'on arrive au quai.
    if (!B.interieur) { if (B.metro && !B.transition) B.metro = null; dernier = { slug: null, station: null, quai: null }; return; }
    if (!dansLeMetro()) return;
    const d = donnees();
    recalerLaRue();
    const slug = B.interieur.slug;
    if (slug === RAME) {
      const e = etatDeLaRame(B.metro.rame);
      const station = e.quai ? e.station : e.vers;
      if (dernier.slug !== RAME) Hud.message('PROCHAINE STATION : ' + d.stations[e.quai ? (e.station + 1) % d.stations.length : e.vers].nom.toUpperCase(), 150);
      else if (dernier.quai !== e.quai) {
        if (e.quai) { Hud.message(d.stations[e.station].nom.toUpperCase(), 150); Son.SFX.porte_vehicule(); }
        else Hud.message('PROCHAINE STATION : ' + d.stations[e.vers].nom.toUpperCase(), 150);
      }
      dernier = { slug: slug, station: station, quai: e.quai };
      return;
    }
    // Au quai : la station se nomme en arrivant, et les portes s'entendent.
    if (dernier.slug !== QUAI || dernier.station !== B.metro.station) Hud.message('STATION ' + d.stations[B.metro.station].nom.toUpperCase(), 120);
    const e = rameAQuai(B.metro.station);
    if (dernier.slug === QUAI && !!e !== !!dernier.quai && e) Son.SFX.porte_vehicule();
    dernier = { slug: slug, station: B.metro.station, quai: !!e };
  }

  // --- Le dessin ---------------------------------------------------------------------------

  //: La longueur d'une rame, en pixels : plus longue que le quai, on n'en voit
  //: jamais les deux bouts.
  const RAME_PX = 13 * 16 + 96;

  //: Les pixels par image dont defile le tunnel quand la rame file.
  const VITESSE_TUNNEL = 6;

  function peindreRame(ctx, x0, y0, largeur, couleur, ouverte) {
    ctx.fillStyle = '#c9ced6'; ctx.fillRect(x0, y0 + 4, largeur, 22);          // la caisse, en acier
    ctx.fillStyle = '#e3e7ec'; ctx.fillRect(x0, y0 + 4, largeur, 2);           // son arete eclairee
    ctx.fillStyle = couleur; ctx.fillRect(x0, y0 + 20, largeur, 3);            // la bande de la ligne
    ctx.fillStyle = '#7d848f'; ctx.fillRect(x0, y0 + 25, largeur, 1);
    for (let x = x0 + 6; x < x0 + largeur - 10; x += 16) {                     // les fenetres
      ctx.fillStyle = '#26303b'; ctx.fillRect(x, y0 + 9, 10, 8);
      ctx.fillStyle = '#fff2c2'; ctx.fillRect(x + 1, y0 + 10, 8, 1);           // la lumiere de dedans
    }
    for (let x = x0 + 40; x < x0 + largeur - 20; x += 64) {                    // les portes
      ctx.fillStyle = ouverte ? '#0e1014' : '#aab1bb';
      ctx.fillRect(x, y0 + 7, 12, 17);
      if (!ouverte) { ctx.fillStyle = '#6f7680'; ctx.fillRect(x + 6, y0 + 7, 1, 17); }
    }
    B.stats.rects += 6;
  }

  function dessinerQuai(ctx, vue) {
    const d = donnees(), piece = B.interieur;
    const x0 = -Math.round(vue.x), y0 = -Math.round(vue.y), largeur = piece.largeur * TT;
    // Le tunnel : du beton noirci, la voie et ses deux rails.
    ctx.fillStyle = '#16171b'; ctx.fillRect(x0, y0, largeur, RANGEES_TUNNEL * TT);
    ctx.fillStyle = '#23252b';
    for (let x = 0; x < largeur; x += 24) ctx.fillRect(x0 + x, y0 + 2, 12, 3);  // les lampes eteintes du tunnel
    ctx.fillStyle = '#3a3c42'; ctx.fillRect(x0, y0 + 26, largeur, 2);
    ctx.fillStyle = '#6d7078'; ctx.fillRect(x0, y0 + 24, largeur, 1); ctx.fillRect(x0, y0 + 29, largeur, 1);
    const vue2 = rameEnVue(B.metro.station);
    if (vue2) {
      ctx.save();
      ctx.beginPath(); ctx.rect(x0 + TT, y0, largeur - 2 * TT, RANGEES_TUNNEL * TT); ctx.clip();
      peindreRame(ctx, x0 + Math.round(vue2.dx) - 48, y0, RAME_PX, d.couleur, vue2.ouverte);
      ctx.restore();
    }
    // La barriere du quai : des panneaux de verre dans un cadre d'acier, et les
    // portes palieres, qui s'ouvrent avec celles de la rame.
    const y = y0 + RANGEES_TUNNEL * TT;
    ctx.fillStyle = '#2b2e35'; ctx.fillRect(x0 + TT, y, largeur - 2 * TT, TT);
    for (let c = 1; c < piece.largeur - 1; c++) {
      const porte = PORTES_PALIERES.indexOf(c) >= 0;
      ctx.fillStyle = porte ? '#aab1bb' : '#6f9bb3';
      ctx.fillRect(x0 + c * TT + 1, y + 1, TT - 2, 11);
      if (!porte) { ctx.fillStyle = '#b8d6e4'; ctx.fillRect(x0 + c * TT + 2, y + 2, 4, 1); }
      else if (vue2 && vue2.ouverte) { ctx.fillStyle = '#0e1014'; ctx.fillRect(x0 + c * TT + 3, y + 1, 10, 11); }
      else { ctx.fillStyle = '#6f7680'; ctx.fillRect(x0 + c * TT + 8, y + 1, 1, 11); }
    }
    ctx.fillStyle = '#2b2e35'; ctx.fillRect(x0 + TT, y + 12, largeur - 2 * TT, 4);
    ctx.fillStyle = d.couleur; ctx.fillRect(x0 + TT, y + 14, largeur - 2 * TT, 2);   // la bande jaune du bord du quai
    // La plaque de la station, au mur du fond.
    const nom = d.stations[B.metro.station].nom.toUpperCase();
    const l = Atlas.largeurTexte(nom, 1);
    // ⚠️ Treize de haut, le nom un rang plus bas : l'accent se dessine trois
    // rangs au-dessus de la lettre, et sur une plaque de onze il en depassait.
    ctx.fillStyle = '#1b1d22'; ctx.fillRect(x0 + (largeur - l) / 2 - 4, y0 + 5, l + 8, 13);
    if (!vue2) {
      ctx.fillStyle = d.couleur; ctx.fillRect(x0 + (largeur - l) / 2 - 4, y0 + 17, l + 8, 1);
      Atlas.texte(ctx, nom, Math.round(x0 + (largeur - l) / 2), y0 + 9, '#f4f1e6', 1);
    }
    B.stats.rects += 8;
  }

  function dessinerRame(ctx, vue) {
    const d = donnees(), piece = B.interieur;
    const x0 = -Math.round(vue.x), y0 = -Math.round(vue.y);
    const e = etatDeLaRame(B.metro.rame);
    // La vitesse a laquelle defile le tunnel : nulle a quai, qui monte et descend
    // aux deux bouts du trajet.
    let vitesse = 0, defile = 0;
    if (!e.quai) {
      const a = d.horaire.approche_images, V = VITESSE_TUNNEL;
      vitesse = Math.min(1, e.ecoule / a, e.reste / a);
      // Ce qui a defile depuis le quai : l'integrale d'une vitesse qui monte
      // pendant `a` images, file, puis redescend — les lampes ralentissent pour
      // de vrai en arrivant, elles ne font pas que raccourcir.
      const montee = Math.min(e.ecoule, a);
      defile = V * montee * montee / (2 * a) + V * Math.max(0, e.ecoule - a);
      if (e.reste < a) defile -= V * (a - e.reste) * (a - e.reste) / (2 * a);
      defile = Math.round(defile);
    }
    // ⚠️ UNE RAME N'EST PAS EN BRIQUE : les murs de la piece sont repeints en
    // acier, et la porte du bas est une porte coulissante — ouverte en station.
    for (let r = 0; r < piece.hauteur; r++) {
      for (let c = 0; c < piece.largeur; c++) {
        const g = piece.sol[r][c];
        if (g !== 'B' && g !== 'D') continue;
        const x = x0 + c * TT, y = y0 + r * TT;
        ctx.fillStyle = '#b9bec6'; ctx.fillRect(x, y, TT, TT);
        ctx.fillStyle = '#d4d8de'; ctx.fillRect(x, y, TT, 1);
        ctx.fillStyle = '#8e949d'; ctx.fillRect(x, y + TT - 1, TT, 1);
        if (r === piece.hauteur - 1) { ctx.fillStyle = d.couleur; ctx.fillRect(x, y + 4, TT, 2); }
      }
    }
    const bas = piece.hauteur - 1;
    for (const c of [3, piece.sortie.x, piece.largeur - 4]) {
      const x = x0 + c * TT, y = y0 + bas * TT;
      const ouverte = e.quai && e.reste > 12 && e.ecoule > 12;
      ctx.fillStyle = ouverte ? '#0e1014' : '#9aa1ab'; ctx.fillRect(x + 1, y, TT - 2, TT);
      if (!ouverte) { ctx.fillStyle = '#5f6670'; ctx.fillRect(x + 7, y, 2, TT); ctx.fillStyle = '#26303b'; ctx.fillRect(x + 3, y + 3, 3, 6); ctx.fillRect(x + 10, y + 3, 3, 6); }
    }
    B.stats.rects += piece.largeur * 2;
    const ligne = piece.sol[0];
    for (let c = 0; c < ligne.length; c++) {
      if (ligne[c] !== 'W') continue;
      const x = x0 + c * TT, y = y0;
      ctx.save();
      ctx.beginPath(); ctx.rect(x + 1, y + 3, TT - 2, TT - 5); ctx.clip();
      if (e.quai) {
        // En station : le carrelage du quai, et sa bande jaune.
        ctx.fillStyle = '#b9b4a8'; ctx.fillRect(x, y, TT, TT);
        ctx.fillStyle = d.couleur; ctx.fillRect(x, y + 12, TT, 2);
      } else {
        ctx.fillStyle = '#0d0e11'; ctx.fillRect(x, y, TT, TT);
        // Les lampes du tunnel qui filent, plus ou moins vite.
        const pas = 40;
        for (let k = -1; k < 2; k++) {
          const lx = x + ((((c * TT - defile) % pas) + pas) % pas) + k * pas;
          ctx.fillStyle = vitesse > 0.6 ? '#8a7a45' : '#d8c27a';
          ctx.fillRect(lx, y + 6, Math.max(2, Math.round(10 * vitesse)), 2);
        }
      }
      ctx.restore();
      B.stats.rects += 3;
    }
  }

  function dessiner(ctx, vue) {
    if (!dansLeMetro()) return;
    if (B.interieur.slug === QUAI) dessinerQuai(ctx, vue); else dessinerRame(ctx, vue);
  }

  /** Les stations sur la grande carte : un carre jaune par edicule, et la ligne
      en pointille entre elles — elle court sous la ville. */
  function dessinerSurLaCarte(ctx, pos) {
    const d = donnees();
    if (!d) return;
    ctx.fillStyle = d.couleur;
    for (let i = 0; i < d.stations.length; i++) {
      const a = d.stations[i], b = d.stations[(i + 1) % d.stations.length];
      const pa = pos(a.x * TT, a.y * TT), pb = pos(b.x * TT, b.y * TT);
      const n = Math.max(Math.abs(pb.x - pa.x), Math.abs(pb.y - pa.y));
      for (let k = 0; k <= n; k += 3) ctx.fillRect(Math.round(pa.x + (pb.x - pa.x) * k / n), Math.round(pa.y + (pb.y - pa.y) * k / n), 1, 1);
      B.stats.rects += Math.ceil(n / 3);
    }
    for (const s of d.stations) {
      const p = pos(s.x * TT, s.y * TT);
      ctx.fillStyle = '#101018'; ctx.fillRect(p.x - 2, p.y - 2, 5, 5);
      ctx.fillStyle = d.couleur; ctx.fillRect(p.x - 1, p.y - 1, 3, 3);
      B.stats.rects += 2;
    }
  }

  return {
    QUAI, RAME, donnees, etatDeLaRame, rameAQuai, rameEnVue, prochaineArrivee, attenteALaStation,
    ediculeSousLaMain, inviteDescendre, descendre, dansLeMetro, utiliser, sortir, invite, texteDInfo,
    maj, dessiner, dessinerSurLaCarte,
  };
})();
