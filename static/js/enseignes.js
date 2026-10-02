/* Bandini — les enseignes qui ouvrent pour vrai : bingo, quilles, lave-auto, Rialto
   (docs/jalons/les-enseignes-qui-ouvrent-pour-vrai.md).

   Python choisit les portes et dessine les pieces (`app/enseignes.py`) ; ici, ce qu'on y fait.

   - LE BINGO : une carte au comptoir (`itemDuComptoir`), puis la partie — une epreuve d'`Adresse`
     (`bingo`) que ce module mene lui-meme, hors du catalogue des defis. Gagner paie le gros lot.
   - LE RIALTO : le soir, un billet ; les lumieres baissent, le film joue sur la toile (le meme film
     muet que le cine-parc, `Cineparc.film`), et on se repose.
   - LA SALLE DE QUILLES : un defi du catalogue (`quilles`), propose par son comptoir — rien ici.
   - LE LAVE-AUTO QU'ON TRAVERSE (docs/jalons/le-lave-auto-qu-on-traverse.md) : un tunnel vitre dans son
     batiment, de la rue a la ruelle (`B.defs.enseignes.lave_auto` : ses colonnes, la rangee de sa facade et
     celle de sa sortie). On arrive AU PAS devant la porte vitree, elle monte ; au seuil on paie, le volant se
     fige et le CONVOYEUR tire le char (jets, brosses, rincage, sechoir) ; la porte du fond monte, on
     ressort dans la ruelle et le char lave perd un cran de chaleur (`Police.unCranDeMoins`).

   ⚠️ RIEN AU DE : la carte de bingo et l'ordre des boules sortent d'un generateur a la graine du jour
   et du numero de la carte (`B.partie.bingos`) ; le film est une fonction de l'image. */

const Enseignes = (function () {
  'use strict';

  function donnees() { return B.defs && B.defs.enseignes; }
  function regles(slug) { const d = donnees(); return d ? d.regles[slug] : null; }
  function ici(slug) { return !!(B.interieur && B.interieur.slug === slug); }
  function s(sec) { return Math.round(sec * 60); }

  // --- Ce que les comptoirs font jouer ------------------------------------------------------

  /** L'article de plus d'un comptoir d'enseigne (`magasins.COMPTOIRS[genre].joue`), ou null. */
  function itemDuComptoir(jeu) {
    if (!donnees()) return null;
    if (jeu === 'bingo') return itemBingo();
    if (jeu === 'film') return itemFilm();
    if (jeu === 'lave_auto') {
      const r = regles('lave_auto');
      return { libelle: 'LE LAVAGE — ' + r.prix + ' $', detail: 'ENTRE EN CHAR PAR LA PORTE VITRÉE, AU PAS', actif: false };
    }
    return null;
  }

  // --- Le bingo -------------------------------------------------------------------------

  //: La partie en cours : la fiche que joue `Adresse` (null hors partie).
  let bingo = null;

  function itemBingo() {
    const r = regles('bingo');
    if (bingo) return { libelle: 'TA CARTE EST EN JEU', actif: false };
    return { libelle: 'UNE CARTE DE BINGO', detail: r.carte + ' $ · GROS LOT ' + r.gros_lot + ' $',
             actif: B.partie.argent >= r.carte && !B.defi && !B.epreuve,
             faire: function () { return commencerBingo(); } };
  }

  /** Une carte achetee : la partie commence. ⚠️ Sa graine : le jour et le numero de la carte. */
  function commencerBingo() {
    const r = regles('bingo'), p = B.partie;
    if (!Missions.payer(r.carte, 'CARTE DE BINGO')) return false;
    p.bingos = (p.bingos || 0) + 1;
    bingo = { slug: 'bingo', epreuve: 'bingo', consigne: 'ACTION : MARQUE LA BOULE SI ELLE EST SUR TA CARTE',
              regles: Object.assign({}, r, { graine: graineDuBingo(p.jour, p.bingos) }) };
    Adresse.commencer(bingo);
    return true;
  }

  function graineDuBingo(jour, n) { return hash2(jour * 977 + n, 0xB1760); }

  function majBingo() {
    if (!bingo) return;
    // Sortir de la salle, c'est laisser sa carte sur la table.
    if (!ici('bingo') || !B.epreuve || B.epreuve.slug !== 'bingo') { if (B.epreuve && B.epreuve.slug === 'bingo') Adresse.fermer(); bingo = null; return; }
    const issue = Adresse.maj(bingo);
    if (!issue) return;
    Adresse.fermer();
    bingo = null;
    if (issue.gagne) {
      Missions.encaisser(regles('bingo').gros_lot, 'LE GROS LOT');
      Hud.message('BINGO! — LES MADAMES TE REGARDENT DE TRAVERS', 240);
    } else Hud.message(issue.raison, 200);
  }

  // --- Le Rialto ----------------------------------------------------------------------

  //: Le film qui joue : `{ t }` en images (null sinon).
  let film = null;

  function seance() {
    const r = regles('rialto'), h = B.partie ? B.partie.heure * 24 : 0;
    return h >= r.seances[0] && h < r.seances[1];
  }

  function itemFilm() {
    const r = regles('rialto');
    if (film) return { libelle: 'LE FILM JOUE', actif: false };
    if (!seance()) return { libelle: 'LA SÉANCE EST À ' + Math.round(r.seances[0]) + ' H', actif: false };
    // Le titre du film de ce soir : le meme qu'au cine-parc (`Cineparc.programme`).
    return { libelle: 'UN BILLET — ' + Cineparc.programme().titre, detail: r.billet + ' $', actif: B.partie.argent >= r.billet,
             faire: function () {
               if (!Missions.payer(r.billet, 'BILLET DE CINÉMA')) return false;
               commencerFilm();
               return true;
             } };
  }

  /** Le billet paye : on s'assoit au milieu de la salle, et les lumieres baissent. */
  function commencerFilm() {
    film = { t: 0 };
    const siege = B.interieur && B.interieur.siege, j = B.joueur;
    if (siege && j) { j.x = siege.x * TT + 8; j.y = siege.y * TT + 8; j.vx = 0; j.vy = 0; }
    Hud.message('LES LUMIÈRES BAISSENT…', 120);
  }

  function majFilm() {
    if (!film) return;
    if (!ici('rialto')) { film = null; return; }
    film.t++;
    const r = regles('rialto');
    if (film.t < s(r.film_s)) return;
    film = null;
    const j = B.joueur;
    if (j) j.vie = Math.min(j.vieMax, j.vie + r.repos_pv);
    Hud.message('FIN — LES LUMIÈRES SE RALLUMENT', 180);
  }

  /** La toile du Rialto, en pixels d'ecran : ses rangees (`h`, deux depuis le grand ecran), et la rangee de mur
      au-dessus — trois tuiles de haut, toute la largeur de la salle. */
  function toile(vue) {
    const t = B.interieur && B.interieur.toile;
    if (!t) return null;
    return { x: Math.round(t.x * TT - vue.x), y: Math.round((t.y - 1) * TT - vue.y), l: t.l * TT, h: ((t.h || 1) + 1) * TT };
  }

  // --- Le lave-auto qu'on traverse -------------------------------------------------------
  //
  // ⚠️ LE TOIT RESTE UN TOIT : pour tout autre char, pour les pietons et pour la patrouille, le tunnel est un mur
  // (ses tuiles sont celles du batiment). Il ne s'ouvre qu'au char du LAVAGE (`tunnelOuvert`, lu par
  // `Vehicules.tuileInterdite`, comme le seuil d'un rideau de garage) — et a l'entree, seulement porte levee.
  // ⚠️ LE RAIL POSE LE CHAR LUI-MEME, chaque image, APRES la physique (`Jeu.maj` passe ici apres `Vehicules`) : le
  // volant ne fait plus rien. Un menu, une scene ou un fondu figent `maj` : le rail attend avec eux.

  //: Les images que met une porte vitree a monter (comme un rideau de garage), et a rester levee sans personne.
  const PORTE_MONTE = 30;
  //: Le char du lavage en cours : { v, phase ('devant' | 'rail' | 'panne'), y0, vit } — null sinon.
  let lavage = null;
  //: Les deux portes vitrees : leur ouverture (0 baissee, 1 levee).
  const portes = { e: 0, s: 0 };
  //: Le refus (pas assez d'argent) deja dit : il ne se repete pas tant qu'on reste devant.
  let refuse = false;

  function tunnel() { const d = donnees(); return d && d.lave_auto; }
  function demi(v) { return (v.def && v.def.longueur ? v.def.longueur : 24) / 2; }

  /** Ce char est-il DEVANT la porte vitree : dans les colonnes du tunnel, sur le trottoir ou la chaussee devant la
      facade, le nez vers elle (au nord, a 60 degres pres) ? */
  function devant(t, v) {
    const haut = (t.entree + 1) * TT;
    return v.x >= t.x * TT && v.x < (t.x + t.l) * TT && v.y >= haut && v.y < haut + demi(v) + 2 * TT
      && Math.abs(ecartAngle(v.angle, -Math.PI / 2)) < Math.PI / 3;
  }

  /** Ce point est-il dans le tunnel (ses colonnes, de la rangee de sortie a celle de la facade) ? */
  function dansLeTunnel(t, x, y) {
    return x >= t.x * TT && x < (t.x + t.l) * TT && y >= t.sortie * TT && y < (t.entree + 1) * TT;
  }

  /** ⚠️ LA TUILE QUI S'OUVRE POUR LE SEUL CHAR DU LAVAGE : les colonnes du tunnel, de sa sortie a sa facade — a
      l'entree, seulement porte levee. Pour tout autre, un toit. */
  function tunnelOuvert(v, tx, ty) {
    const t = tunnel();
    if (!t || !lavage || lavage.v !== v || B.interieur) return false;
    if (tx < t.x || tx >= t.x + t.l || ty < t.sortie || ty > t.entree) return false;
    return lavage.phase !== 'devant' || portes.e >= 1;
  }

  /** Le char du joueur est-il sur le rail (on n'en descend pas, l'agent ne l'en sort pas) ? */
  function auLavage(v) { return !!(lavage && lavage.v === v && lavage.phase === 'rail'); }

  /** L'etape du lavage ou en est ce char, d'apres sa place sur le rail : 'jets', 'brosses', 'rincage', 'sechoir'. */
  function etape() {
    if (!lavage || lavage.phase !== 'rail') return null;
    const f = (lavage.y0 - lavage.v.y) / Math.max(1, lavage.y0 - lavage.yFin);
    return f < 0.25 ? 'jets' : f < 0.55 ? 'brosses' : f < 0.75 ? 'rincage' : 'sechoir';
  }

  function vers(cle, voulu) {
    portes[cle] = voulu ? Math.min(1, portes[cle] + 1 / PORTE_MONTE) : Math.max(0, portes[cle] - 1 / PORTE_MONTE);
  }

  /** Une image au lave-auto. */
  function majLaveAuto() {
    const t = tunnel();
    if (!t || B.interieur || B.bloc) return;
    const j = B.joueur, v = j && j.dansVehicule;
    // Ses sons (le jet, le sechoir) se chargent quand on s'en approche.
    if (j && Math.abs(j.x - (t.x + 1) * TT) < 400 && Math.abs(j.y - t.entree * TT) < 400) Son.Lieu.charger('lave_auto');
    if (lavage) { majLavage(t, j); return; }
    vers('e', false); vers('s', false);
    if (!v || (v.def && v.def.eau) || !devant(t, v)) { refuse = false; return; }
    const r = regles('lave_auto');
    if (Math.abs(v.vitesse) > r.vitesse_max) return;
    if (B.partie.argent < r.prix) {
      if (!refuse) { Hud.message('LE LAVAGE : ' + r.prix + ' $ — PAS ASSEZ', 150); Son.SFX.erreur(); refuse = true; }
      return;
    }
    lavage = { v: v, phase: 'devant' };
  }

  function majLavage(t, j) {
    const l = lavage, v = l.v, r = regles('lave_auto');
    // Le char brule, ou il n'est plus au joueur : le rail s'arrete, les deux portes montent, et le tunnel reste ouvert
    // a ce char-la jusqu'a ce qu'il en soit sorti (pousse, remorque, ou reconduit).
    if (l.phase !== 'panne' && (v.etat === 'epave' || j.dansVehicule !== v)) l.phase = 'panne';
    if (l.phase === 'panne') {
      vers('e', true); vers('s', true);
      if (!dansLeTunnel(t, v.x, v.y) && !devant(t, v)) lavage = null;
      return;
    }
    if (l.phase === 'devant') {
      vers('e', true); vers('s', false);
      if (v.y < t.entree * TT + TT / 2) {
        // Le seuil passe : on paie, et le convoyeur prend le char.
        if (!Missions.payer(r.prix, 'LAVE-AUTO')) { l.phase = 'panne'; return; }
        l.phase = 'rail'; l.y0 = v.y; l.yFin = t.sortie * TT - demi(v) - 2;
        l.vit = (l.y0 - l.yFin) / Math.max(1, s(r.duree_s));
        l.etape = null;
        Hud.message('LE LAVAGE — LÂCHE LE VOLANT', 120);
        return;
      }
      if (!devant(t, v) && !dansLeTunnel(t, v.x, v.y)) lavage = null;
      return;
    }
    // Sur le rail : le convoyeur pose le char, cap au nord, au milieu du tunnel.
    v.x = (t.x + t.l / 2) * TT; v.angle = -Math.PI / 2; v.vitesse = 0; v.vx = 0; v.vy = 0;
    v.y = Math.max(l.yFin, v.y - l.vit);
    for (const q of Entites.joueurs()) if (q.dansVehicule === v) { q.x = v.x; q.y = v.y; }
    vers('e', v.y + demi(v) >= t.entree * TT);                  // la porte d'entree redescend derriere lui
    vers('s', v.y - demi(v) < (t.sortie + 2) * TT);              // celle du fond monte quand il en approche
    const e = etape();
    if (e !== l.etape) {
      l.etape = e;
      if (e === 'jets' || e === 'rincage') Son.SFX.jet_lavage(); else if (e === 'brosses') Son.SFX.brosses(); else if (e === 'sechoir') Son.SFX.sechoir();
    }
    if (v.y > l.yFin) return;
    // Sorti : la main revient, une etoile tombe, et le char reste luisant un moment.
    lavage = null;
    portes.s = 1;
    const avant = B.recherche.etoiles;
    Police.unCranDeMoins();
    v.luisant = B.t + s(10);
    Hud.message(avant > 0 ? 'LAVÉ — UNE ÉTOILE DE MOINS' : 'LAVÉ — PROPRE COMME UN SOU NEUF', 180);
  }

  function maj() { majBingo(); majFilm(); majLaveAuto(); }

  // --- Les dessins ----------------------------------------------------------------------

  /** Sous les gens : le film sur la toile du Rialto, le plancher mouille du tunnel du lave-auto. */
  function dessinerSol(ctx, vue) {
    if (film && ici('rialto')) {
      const t = toile(vue);
      if (t) Cineparc.film(ctx, t.x, t.y, t.l, t.h);
      return;
    }
    const t = tunnel();
    if (B.interieur || !t) return;
    const z = zone(t, vue);
    if (!z) return;
    // Le beton mouille du tunnel, sous les gens : le toit s'efface, on voit dedans. Une rigole au milieu.
    ctx.fillStyle = '#3e454e'; ctx.fillRect(z.x, z.y, z.l, z.h);
    ctx.fillStyle = 'rgba(120,170,220,0.25)'; ctx.fillRect(z.x + 2, z.y + 2, z.l - 4, z.h - 4);
    ctx.fillStyle = '#2b3036'; ctx.fillRect(z.x + z.l / 2 - 1, z.y, 2, z.h);
    ctx.fillStyle = '#e0b43a'; ctx.fillRect(z.x, z.y + z.h - 2, z.l, 1);            // la bande jaune du seuil
    B.stats.rects += 4;
  }

  /** Le rectangle du tunnel a l'ecran, ou null s'il n'y est pas. */
  function zone(t, vue) {
    const x = Math.round(t.x * TT - vue.x), y = Math.round(t.sortie * TT - vue.y);
    const l = t.l * TT, h = (t.entree - t.sortie + 1) * TT;
    if (x > VW || y > VH || x + l < 0 || y + h < 0) return null;
    return { x: x, y: y, l: l, h: h };
  }

  /** Une porte vitree : son cadre, et le verre qui monte (`ouv`, 0 baissee, 1 levee). */
  function porteVitree(ctx, x, y, l, ouv) {
    ctx.fillStyle = '#4a4e57'; ctx.fillRect(x, y, l, 2); ctx.fillRect(x, y, 2, TT); ctx.fillRect(x + l - 2, y, 2, TT);
    const h = Math.round((TT - 3) * (1 - ouv));
    if (h > 0) {
      ctx.fillStyle = 'rgba(170,215,240,0.55)'; ctx.fillRect(x + 2, y + 2, l - 4, h);
      ctx.fillStyle = 'rgba(255,255,255,0.45)'; ctx.fillRect(x + 4, y + 3, 2, Math.max(1, h - 2)); ctx.fillRect(x + l / 2, y + 3, 1, Math.max(1, h - 4));
      ctx.fillStyle = '#4a4e57'; ctx.fillRect(x + 2, y + 1 + h, l - 4, 1);
    }
    B.stats.rects += 7;
  }

  /** PAR-DESSUS LES GENS (`Jeu.rendre`, juste apres `Entites.dessiner`) : le toit de verre teinte et ses reflets, ses
      montants, les jets, les brosses qui tournent, le sechoir, les deux portes vitrees — et le char qui sort luisant.
      ⚠️ Rien ne cache : on voit le char a travers la vitre (et la police aussi). */
  function dessinerTunnel(ctx, vue) {
    const t = tunnel();
    if (B.interieur || B.bloc || !t) return;
    const z = zone(t, vue);
    if (z) {
      const e = etape(), rangees = t.entree - t.sortie + 1;
      // Les postes, du seuil vers la ruelle : les jets au premier quart, les brosses au milieu, le sechoir au fond.
      const yJets = z.y + z.h - Math.round(z.h * 0.3), yBrosses = z.y + Math.round(z.h * 0.45), ySech = z.y + Math.round(z.h * 0.18);
      ctx.fillStyle = '#5d6570'; ctx.fillRect(z.x, yJets, z.l, 2);                       // la rampe des jets
      if (e === 'jets' || e === 'rincage') {
        ctx.fillStyle = 'rgba(190,225,255,0.7)';
        for (let k = 2; k < z.l - 2; k += 4) ctx.fillRect(z.x + k, yJets + 2 + ((B.t + k) % 5), 1, 4);
      }
      const tourne = e === 'brosses' ? (B.t >> 1) % 4 : 0;                               // les deux brosses
      for (const bx of [z.x + 1, z.x + z.l - 5]) {
        for (let k = 0; k < 12; k += 3) {
          ctx.fillStyle = (k / 3) % 4 === tourne ? '#9fd0ff' : '#2f6fb8';
          ctx.fillRect(bx, yBrosses - 6 + k, 4, 3);
        }
      }
      ctx.fillStyle = e === 'sechoir' ? '#e8a03c' : '#6a6f78'; ctx.fillRect(z.x + 2, ySech, z.l - 4, 3);   // le sechoir
      if (e === 'sechoir') { ctx.fillStyle = 'rgba(255,255,255,0.35)'; for (let k = 3; k < z.l - 3; k += 5) ctx.fillRect(z.x + k, ySech + 4 + (B.t % 4), 1, 3); }
      // Le toit de verre : une teinte, ses montants a chaque rangee, deux reflets en biais.
      ctx.fillStyle = 'rgba(150,200,230,0.20)'; ctx.fillRect(z.x, z.y, z.l, z.h);
      ctx.fillStyle = 'rgba(40,46,56,0.8)';
      ctx.fillRect(z.x - 1, z.y, 1, z.h); ctx.fillRect(z.x + z.l, z.y, 1, z.h);
      for (let k = 1; k < rangees; k++) ctx.fillRect(z.x, z.y + k * TT, z.l, 1);
      ctx.fillStyle = 'rgba(255,255,255,0.12)';
      for (let k = 0; k < z.h - 6; k += 12) ctx.fillRect(z.x + 4 + (k % 9), z.y + k, 3, 6);
      porteVitree(ctx, z.x, z.y + z.h - TT, z.l, portes.e);                              // l'entree, sur la facade
      porteVitree(ctx, z.x, z.y, z.l, portes.s);                                         // la sortie, cote ruelle
      B.stats.rects += 16;
    }
    // Le char qui sort luisant : quelques eclats qui clignent, un moment.
    const v = B.joueur && B.joueur.dansVehicule;
    if (v && v.luisant > B.t) {
      const x = Math.round(v.x - vue.x), y = Math.round(v.y - vue.y);
      if (x > -20 && x < VW + 20 && y > -20 && y < VH + 20) {
        ctx.fillStyle = '#ffffff';
        for (let k = 0; k < 3; k++) if (((B.t >> 3) + k) % 3 === 0) ctx.fillRect(x - 6 + k * 6, y - 8 + (k % 2) * 10, 1, 1);
        B.stats.rects += 3;
      }
    }
  }

  /** Par-dessus la scene (`Base.ecran()`, apres `Base.fin`) : la salle du Rialto dans le noir, et le
      film qui seul brille. ⚠️ Une piece n'a pas de nuit a elle : c'est ici qu'on l'eteint. */
  function dessinerPardessus(ctx, vue) {
    if (!film || !ici('rialto')) return;
    const r = regles('rialto'), fondu = Math.min(1, film.t / 90, (s(r.film_s) - film.t) / 90);
    ctx.fillStyle = 'rgba(4,4,10,' + (0.78 * fondu).toFixed(2) + ')';
    ctx.fillRect(0, 0, VW, VH);
    const t = toile(vue);
    if (!t) return;
    Cineparc.film(ctx, t.x, t.y, t.l, t.h);
    // Le faisceau du projecteur, du mur du fond (la porte : la cabine est au-dessus) jusqu'a la toile —
    // le meme qu'au cine-parc (`Cineparc.faisceau`).
    const fond = ((B.interieur.hauteur || 10) - 1) * TT - vue.y;
    Cineparc.faisceau(ctx, t.x + t.l / 2, fond, t.x, t.x + t.l, t.y + t.h, fondu, film.t);
  }

  return { itemDuComptoir, commencerBingo, graineDuBingo, seance, commencerFilm, maj, tunnelOuvert, auLavage, etape,
           dessinerSol, dessinerTunnel, dessinerPardessus, get lavage() { return lavage; }, get portesDuLavage() { return portes; },
           get bingo() { return bingo; }, get film() { return film; } };
})();
