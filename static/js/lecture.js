/* Bandini — la lecture des passants (docs/jalons/la-reputation-et-la-lecture-des-passants.md, vague 1).

   Tranché par Martin le 1er oct. 2026 : on TIENT LIRE (la gâchette de gauche à pied, Y au clavier, le
   bouton LIRE au doigt) en regardant un passant, et sa ligne s'affiche au-dessus de sa tête — le
   profilage de Watch Dogs. On lâche, elle s'en va. Les lignes sont dans `app/lectures.py`, un lot par
   quartier, et voyagent dans la suite du paquet (`B.defs.lectures`) : sans elle, on ne lit rien.

   ⚠️ UNE LECTURE NE COÛTE RIEN ET NE RAPPORTE RIEN. Ce module ne touche ni à la partie, ni à la
   mission, ni au passant (il ne s'arrête pas, ne se retourne pas) : il lit, il peint. Aucune mission
   ne lit `e.lecture`. Si elle se mettait à donner, elle deviendrait l'objectif que M16 interdit.

   ⚠️ UN ENFANT NE SE LIT PAS (`lisible`) : ni un intouchable, ni un corps d'enfant, ni un ado — les
   lignes sont écrites pour des grandes personnes. Ni un personnage, ni une bête, ni un figurant de
   mission : eux ont déjà un nom et une histoire.

   ⚠️ RIEN AU DÉ : la ligne d'un passant est celle que son identifiant désigne dans le lot de son
   quartier (`hash2`), et il la GARDE (`e.lecture`) : il ne change pas d'histoire en traversant une rue.
   Rien ne naît, rien ne se tire — ni au démarrage, ni en lisant. */

const Lecture = (function () {
  'use strict';

  //: Le sel de l'empreinte : la ligne d'un passant ne suit pas sa tenue (`0x7e4e`) ni rien d'autre.
  const SEL = 0x1ec7;
  //: La fiche : une encre de profileur sur fond de nuit, au-dessus de la tête.
  const FOND = '#14161f', ENCRE = '#9fe3ff', CADRE = '#3c8cc8';
  const RANGEE_H = 8, DESSUS = 30;

  function donnees() { return (B.defs && B.defs.lectures) || null; }

  /** Le quartier d'un passant : la zone de la VILLE sous ses pieds ; dans une pièce, celle de la porte
      qu'on a passée. ⚠️ `B.defs.carte`, jamais `Monde.carte` : dans un bloc, `Monde.carte` est le bloc
      (et un bloc n'a pas de quartier — on n'y lit rien). */
  function quartierDe(e) {
    const ville = B.defs && B.defs.carte;
    if (!ville || B.bloc) return null;
    let x = e.x, y = e.y;
    if (B.interieur) {
      const porte = Monde.carte && Monde.carte.porte;
      if (!porte) return null;
      x = porte.x * TT + 8; y = porte.y * TT + 8;
    }
    let trouvee = null;
    for (const z of ville.zones || []) {
      if (x >= z.x * TT && x < (z.x + z.l) * TT && y >= z.y * TT && y < (z.y + z.h) * TT) trouvee = z;
    }
    return trouvee ? trouvee.district || trouvee.slug : null;
  }

  /** Sa ligne, ou null : un quartier sans lot (la baie, un bloc) n'a rien à dire. Gardée une fois lue. */
  function ligneDe(e) {
    if (e.lecture) return e.lecture;
    const d = donnees(), q = quartierDe(e);
    const lot = d && q && d.lignes[q];
    if (!lot || !lot.length) return null;
    e.lecture = lot[hash2(e.id, SEL) % lot.length];
    return e.lecture;
  }

  /** Peut-on lire celui-là ? ⚠️ D'abord ce qui ne se lit JAMAIS. */
  function lisible(e) {
    if (!e || e.type !== 'pieton' || !e.vivant || e.dansVehicule) return false;
    if (e.intouchable || String(e.sprite || '').indexOf('enfant') === 0 || e.arch === 'enfant' || e.arch === 'ado') return false;
    if (e.personnage || e.partenaire || e.bete || e.nomDeMission || e.job) return false;
    return true;
  }

  /** Le regard du joueur : sa face, sinon son angle (`faceA` fait pareil). */
  function regardDe(j) {
    const r = typeof REGARDS !== 'undefined' ? REGARDS[j.face] : undefined;
    return r === undefined ? j.angle : r;
  }

  function aPortee(j, e, portee) {
    return dist2(j.x, j.y, e.x, e.y) <= portee * portee && Monde.ligneLibre(j.x, j.y, e.x, e.y);
  }

  /** Qui le joueur regarde : celui qu'il vise, sinon le plus proche dans son regard. */
  function regarde(j, regle) {
    if (lisible(j.cible) && aPortee(j, j.cible, regle.portee_px)) return j.cible;
    const cone = regle.cone_deg * Math.PI / 180, regard = regardDe(j);
    let meilleur = null, d2 = Infinity;
    for (const e of Entites.pietonsAutour(j.x, j.y, regle.portee_px)) {
      if (!lisible(e) || Math.abs(ecartAngle(regard, angleVers(j.x, j.y, e.x, e.y))) > cone) continue;
      const d = dist2(j.x, j.y, e.x, e.y);
      if (d < d2 && Monde.ligneLibre(j.x, j.y, e.x, e.y)) { meilleur = e; d2 = d; }
    }
    return meilleur;
  }

  function peutLire(j) {
    return !!(j && j.vivant && !j.dansVehicule && !B.menu && !B.scene && !B.transition && donnees());
  }

  /** Chaque image : tant que LIRE tient, la fiche suit celui qu'on regarde ; lâché, elle s'en va. */
  function maj() {
    const j = B.joueur;
    if (!Entree.bas('lire') || !peutLire(j)) { B.lecture = null; return; }
    const regle = donnees().regle;
    const avant = B.lecture && B.lecture.cible;
    // La cible tient tant qu'on tient le bouton et qu'on la voit : elle ne saute pas d'une tête à l'autre.
    let cible = lisible(avant) && aPortee(j, avant, regle.garde_px) ? avant : regarde(j, regle);
    if (cible && !ligneDe(cible)) cible = null;
    if (!cible) { B.lecture = null; return; }
    if (cible !== avant) B.lecture = { cible: cible, t: 0 };
    else B.lecture.t++;
  }

  /** La ligne en rangées d'au plus `largeur` caractères, coupée aux espaces. */
  function ranger(texte, largeur) {
    const rangees = [''];
    for (const mot of String(texte).split(' ')) {
      const r = rangees[rangees.length - 1];
      if (r && r.length + 1 + mot.length > largeur) rangees.push(mot);
      else rangees[rangees.length - 1] = r ? r + ' ' + mot : mot;
    }
    return rangees;
  }

  /** La fiche, au-dessus de la tête de celui qu'on lit — après tout le monde, comme une bulle. */
  function dessiner(ctx, cam) {
    const l = B.lecture;
    if (!l || !l.cible || !l.cible.vivant) return;
    const e = l.cible, d = donnees();
    const texte = ligneDe(e);
    if (!texte || !d) return;
    const rangees = ranger(texte, d.largeur_rangee);
    const large = Math.max.apply(null, rangees.map(function (r) { return Atlas.largeurTexte(r, 1); })) + 8;
    const haut = rangees.length * RANGEE_H + 4;
    const monte = l.t < 5 ? 5 - l.t : 0;
    const x = Math.round(e.x - large / 2 - cam.x);
    const y = Math.round(e.y - DESSUS - haut + monte - cam.y);
    ctx.fillStyle = CADRE;
    ctx.fillRect(x - 1, y - 1, large + 2, haut + 2);
    ctx.fillStyle = FOND;
    ctx.fillRect(x, y, large, haut);
    // Le fil qui descend vers la tête : on sait QUI on lit, même dans une foule.
    ctx.fillStyle = CADRE;
    ctx.fillRect(Math.round(e.x - cam.x), y + haut + 1, 1, Math.max(0, DESSUS - 12 - monte));
    rangees.forEach(function (r, i) { Atlas.texte(ctx, r, x + 4, y + 3 + i * RANGEE_H, ENCRE, 1); });
    B.stats.rects += 4;
  }

  /** Une partie neuve, un rechargement : on ne lit plus personne. */
  function oublier() { B.lecture = null; }

  return { maj, dessiner, oublier, lisible, ligneDe, quartierDe, ranger, regarde };
})();
