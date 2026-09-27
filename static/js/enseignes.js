/* Bandini — les enseignes qui ouvrent pour vrai : bingo, quilles, lave-auto, Rialto
   (docs/jalons/les-enseignes-qui-ouvrent-pour-vrai.md).

   Python choisit les portes et dessine les pieces (`app/enseignes.py`) ; ici, ce qu'on y fait.

   - LE BINGO : une carte au comptoir (`itemDuComptoir`), puis la partie — une epreuve d'`Adresse`
     (`bingo`) que ce module mene lui-meme, hors du catalogue des defis. Gagner paie le gros lot.
   - LE RIALTO : le soir, un billet ; les lumieres baissent, le film joue sur la toile (le meme film
     muet que le cine-parc, `Cineparc.film`), et on se repose.
   - LA SALLE DE QUILLES : un defi du catalogue (`quilles`), propose par son comptoir — rien ici.
   - LE LAVE-AUTO : sa baie est peinte sur la chaussee (`B.defs.enseignes.lave_auto`). On y roule AU
     PAS, on paie, et le char lave perd un cran de chaleur (`Police.unCranDeMoins`) — une fois par
     passage : il faut sortir de la baie pour se refaire laver.

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
      return { libelle: 'LE LAVAGE — ' + r.prix + ' $', detail: 'PASSE EN CHAR DANS LA BAIE, AU PAS', actif: false };
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

  // --- Le lave-auto -------------------------------------------------------------------

  function baie() { const d = donnees(); return d && d.lave_auto; }

  /** Ce char est-il dans la baie (son centre) ? */
  function dansLaBaie(v) {
    const b = baie();
    if (!b) return false;
    const tx = v.x / TT, ty = v.y / TT;
    return tx >= b.x && tx < b.x + b.l && ty >= b.y && ty < b.y + b.h;
  }

  /** Une image au lave-auto : au pas dans la baie pendant `duree_s`, on paie et on est lave. Une fois
      par passage (`v.lave` retombe quand on sort de la baie). */
  function majLaveAuto() {
    const j = B.joueur, v = j && j.dansVehicule;
    if (!v || B.interieur || !baie()) return;
    if (!dansLaBaie(v)) { v.laveT = 0; v.lave = false; return; }
    if (v.lave) return;
    const r = regles('lave_auto');
    if (Math.abs(v.vitesse) > r.vitesse_max) { v.laveT = 0; return; }
    if (!v.laveT) Son.SFX.brosses();
    v.laveT = (v.laveT || 0) + 1;
    if (v.laveT < s(r.duree_s)) return;
    v.lave = true;
    if (!Missions.payer(r.prix, 'LAVE-AUTO')) { Hud.message('LE LAVAGE : ' + r.prix + ' $ — PAS ASSEZ', 150); Son.SFX.erreur(); return; }
    const avant = B.recherche.etoiles;
    Police.unCranDeMoins();
    Hud.message(avant > 0 ? 'LAVÉ — UNE ÉTOILE DE MOINS' : 'LAVÉ — PROPRE COMME UN SOU NEUF', 180);
  }

  function maj() { majBingo(); majFilm(); majLaveAuto(); }

  // --- Les dessins ----------------------------------------------------------------------

  /** Sous les gens : le film sur la toile du Rialto, la baie du lave-auto dans la rue. */
  function dessinerSol(ctx, vue) {
    if (film && ici('rialto')) {
      const t = toile(vue);
      if (t) Cineparc.film(ctx, t.x, t.y, t.l, t.h);
      return;
    }
    const b = baie();
    if (B.interieur || !b) return;
    const x = Math.round(b.x * TT - vue.x), y = Math.round(b.y * TT - vue.y), l = b.l * TT, h = b.h * TT;
    if (x > VW || y > VH || x + l < 0 || y + h < 0) return;
    // Le beton mouille, les brosses bleues qui tournent de chaque cote, le portique au milieu.
    ctx.fillStyle = 'rgba(120,170,220,0.22)'; ctx.fillRect(x, y, l, h);
    const tour = (B.t >> 2) % 4;
    for (let k = 0; k < l; k += 4) {
      ctx.fillStyle = (k >> 2) % 4 === tour ? '#9fd0ff' : '#2f6fb8';
      ctx.fillRect(x + k, y, 3, 3); ctx.fillRect(x + k, y + h - 3, 3, 3);
    }
    ctx.fillStyle = '#3a3d44';
    ctx.fillRect(x + l / 2 - 1, y - 2, 3, h + 4);                       // le portique
    ctx.fillStyle = '#e8b33c'; ctx.fillRect(x + l / 2 - 1, y - 2, 3, 2); ctx.fillRect(x + l / 2 - 1, y + h, 3, 2);
    B.stats.rects += 8 + l / 2;
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

  return { itemDuComptoir, commencerBingo, graineDuBingo, seance, commencerFilm, dansLaBaie, maj,
           dessinerSol, dessinerPardessus,
           get bingo() { return bingo; }, get film() { return film; } };
})();
