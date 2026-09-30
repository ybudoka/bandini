/* Bandini — les saisons de la ville (docs/jalons/les-quatre-saisons-realistes.md, lot 1).

   La palette du moment : le gazon, la friche, les arbres, la neige qui tient sur les trottoirs et
   les toits. ⚠️ UNE PURE FONCTION DU JOUR ET DE L'HEURE (`app/saisons.py` donne les palettes et les
   images-cles) : aucun de, rien a sauvegarder, la meme ville pour tout le monde.

   ⚠️ HUIT PALIERS PAR TRANSITION : la couleur ne glisse pas a chaque image, elle saute d'un palier
   a l'autre. C'est le palier (`cle`) qui fait repeindre les tuiles cuites et les morceaux
   (`Monde.dessinerSol`) : une repeinte toutes les deux minutes pendant une transition, jamais le
   reste du temps — le rythme sur le telephone.

   ⚠️ LA LUMIERE EST POUR LES YEUX (`heureDeLumiere`) : les regles gardent l'horloge fixe de
   `Monde.ambiance`. */

const Saisons = (function () {
  'use strict';

  //: La neige qui tient, sur un trottoir ou un toit.
  const BLANC = [238, 242, 246];

  function donnees() { return B.defs && B.defs.saisons; }

  function rgb(c) { return [parseInt(c.substr(1, 2), 16), parseInt(c.substr(3, 2), 16), parseInt(c.substr(5, 2), 16)]; }
  function hex(v) { return '#' + v.map(function (x) { return ('0' + Math.round(x).toString(16)).slice(-2); }).join(''); }
  function meler(a, b, t) { const x = rgb(a), y = rgb(b); return hex(x.map(function (v, i) { return v + (y[i] - v) * t; })); }

  /** Mele deux valeurs de palette de meme forme : couleurs, nombres, tableaux, objets. */
  function melerTout(a, b, t) {
    if (typeof a === 'string') return t === 0 ? a : meler(a, b, t);
    if (typeof a === 'number') return a + (b - a) * t;
    if (Array.isArray(a)) return a.map(function (v, i) { return melerTout(v, b[i], t); });
    const o = {};
    for (const k in a) o[k] = melerTout(a[k], b[k], t);
    return o;
  }

  /** Ou en est l'annee : { de, vers, palier } — `palier` de 0 a paliers-1 dans une transition. */
  function position(jour, heure) {
    const d = donnees(), x = Calendrier.jourDeLAnnee(jour) + (heure || 0);
    const cles = d.cles;
    for (let i = 0; i < cles.length - 1; i++) {
      const a = cles[i], b = cles[i + 1];
      if (x >= a[0] && x < b[0]) {
        if (a[1] === b[1]) return { de: a[1], vers: a[1], palier: 0 };
        return { de: a[1], vers: b[1], palier: Math.floor((x - a[0]) / (b[0] - a[0]) * d.paliers) };
      }
    }
    return { de: cles[0][1], vers: cles[0][1], palier: 0 };
  }

  function cleA(jour, heure) {
    const p = position(jour, heure);
    return p.de === p.vers ? p.de : p.de + '>' + p.vers + ':' + p.palier;
  }

  const memo = new Map();
  function paletteA(jour, heure) {
    const d = donnees(), cle = cleA(jour, heure);
    if (memo.has(cle)) return memo.get(cle);
    const p = position(jour, heure);
    const pal = melerTout(d.palettes[p.de], d.palettes[p.vers], p.palier / d.paliers);
    memo.set(cle, pal);
    return pal;
  }

  function maintenant() { return B.partie ? [B.partie.jour, B.partie.heure] : [21, 0.5]; }
  function palette() { const m = maintenant(); return paletteA(m[0], m[1]); }
  function cle() { const m = maintenant(); return cleA(m[0], m[1]); }

  /** Le style d'un trottoir ou d'un toit sous la neige qui tient : chaque couleur melee au blanc
      de `palette().neige`. Le meme objet tant que la cle ne change pas (les peintres le lisent a
      chaque tuile cuite). */
  const neiges = new Map();
  function enneiger(style) {
    const n = palette().neige;
    if (!n) return style;
    const k = cle();
    let parStyle = neiges.get(k);
    if (!parStyle) { parStyle = new Map(); neiges.set(k, parStyle); }
    if (parStyle.has(style)) return parStyle.get(style);
    const o = {};
    for (const c in style) o[c] = typeof style[c] === 'string' && style[c][0] === '#' ? meler(style[c], hex(BLANC), n) : style[c];
    parStyle.set(style, o);
    return o;
  }

  /** L'hiver, pour ce qui s'habille : tant que la neige tient (`palette().neige`, de decembre au
      degel de la fin mars). ⚠️ Pas le mois du calendrier : ce qu'on voit au sol et sur les chars
      doit dire la meme chose — une capote relevee sur une rue sans neige ne se comprend pas. */
  function enHiver() {
    return !!(donnees() && palette().neige > 0);
  }

  /** LA NEIGE QUI COIFFE un decor laisse dehors pour l'hiver (la foire fermee, docs/jalons/la-foire-fermee-l-hiver.md) :
      rend un peintre qui peint `peintre`, puis pose `epaisseur` rangs de blanc sur ce qui regarde le ciel.
      ⚠️ SUR UNE SURFACE SEULEMENT : le dessus d'un plein d'au moins trois pixels de haut. La premiere version
      blanchissait tout pixel au ciel ouvert, et la jante, les rayons et la chaine (un ou deux pixels) de la
      grande roue et de l'arche disparaissaient sous la neige — la neige ne tient pas sur un fil.
      ⚠️ SANS LIRE UN PIXEL (`getImageData` coute cher et ne sert nulle part ailleurs) : des passes de
      composition. Le dessus = le decor, moins sa copie descendue d'un pixel (`destination-out`), garde la ou
      le decor est plein deux pixels plus bas (`destination-in`, sa copie remontee) ; on l'epaissit vers le bas
      sans sortir du dessin, on le blanchit (`source-atop`), on le pose par-dessus. Cuit une fois. */
  function coiffer(peintre, w, h, epaisseur) {
    return function (g) {
      const src = Base.nouveauCanvas(w, h);
      peintre(src.getContext('2d'), w, h);
      const dessus = Base.nouveauCanvas(w, h), k = dessus.getContext('2d');
      k.drawImage(src, 0, 0);
      k.globalCompositeOperation = 'destination-out';
      k.drawImage(src, 0, 1);
      k.globalCompositeOperation = 'destination-in';
      k.drawImage(src, 0, -2);
      const neige = Base.nouveauCanvas(w, h), n = neige.getContext('2d');
      for (let e = 0; e < (epaisseur || 2); e++) n.drawImage(dessus, 0, e);
      n.globalCompositeOperation = 'destination-in';
      n.drawImage(src, 0, 0);
      n.globalCompositeOperation = 'source-atop';
      n.fillStyle = hex(BLANC);
      n.fillRect(0, 0, w, h);
      g.drawImage(src, 0, 0);
      g.drawImage(neige, 0, 0);
    };
  }

  /** LA FICHE DU MOMENT (docs/jalons/les-decapotables-l-hiver.md) : une fiche peut porter sa
      version d'hiver (`fiche.hiver` : la capote relevee de la decapotable, la tuque de la
      conductrice). Rend [nom, fiche] — le NOM change avec elle, sinon le cache de l'atlas
      rendrait l'image d'ete sous la cle d'ete. */
  function ficheDuMoment(nom, fiche) {
    if (fiche && fiche.hiver && enHiver()) return [nom + '~hiver', fiche.hiver];
    // ⚠️ LES HABITS D'UN CORPS DESSINE A LA MAIN (l'enfant, vague 4c) : `fiche.saisons.froid` au grand
    // froid, `fiche.saisons.frais` a la mi-saison — d'apres le froid de la palette, dehors seulement.
    if (fiche && fiche.saisons && !B.interieur && habitsDonnees()) {
      const f = momentDesHabits().froid, H = habitsDonnees();
      if (f >= H.grand_froid && fiche.saisons.froid) return [nom + '~froid', fiche.saisons.froid];
      if (f >= H.frais && fiche.saisons.frais) return [nom + '~frais', fiche.saisons.frais];
    }
    return [nom, fiche];
  }

  // ------------------------------------------------------------------ l'habit du moment (lot 4a)

  //: LA GARDE-ROBE DES SAISONS (docs/jalons/les-quatre-saisons-realistes.md, vague 4a). La tenue TIREE
  //: d'un passant (`e.tenue`) ne change jamais : le tirage, ses couleurs, `e.swaps`, la sauvegarde restent
  //: ceux d'avant. C'est l'IMAGE qui s'habille, par une pure fonction de la tenue, du froid du moment
  //: (`palette().froid`, qui glisse en paliers) et de la pluie. ⚠️ AUCUN DE : ce qu'un passant a de
  //: frileux vient de l'EMPREINTE de sa tenue.

  function habitsDonnees() { const d = donnees(); return d && d.habits; }

  /** Une empreinte de la tenue (FNV sur ses champs) : la meme tenue, le meme passant, la meme frilosite. */
  const empreintes = new WeakMap();
  function empreinte(tn) {
    let h = empreintes.get(tn);
    if (h !== undefined) return h;
    const s = [tn.squelette, tn.peau, tn.cheveux, tn.coiffure, tn.haut, tn.couleur_haut, tn.bas,
               tn.couleur_bas, tn.chapeau, tn.accent].join('|');
    h = 0x811c9dc5;
    for (let i = 0; i < s.length; i++) { h ^= s.charCodeAt(i); h = Math.imul(h, 0x01000193) >>> 0; }
    h ^= h >>> 15; h = Math.imul(h, 0x2c1b3c6d) >>> 0; h ^= h >>> 12;
    empreintes.set(tn, h >>> 0);
    return h >>> 0;
  }
  function frilosite(tn) { return (empreinte(tn) % 1000) / 1000; }

  function pleut() {
    const H = habitsDonnees();
    return !!(H && typeof Pluie !== 'undefined' && !B.interieur && Pluie.intensite() > H.parapluie.seuil);
  }

  /** L'habit d'une tenue pour un froid SENTI `c` (et la pluie). Pure : rend `tn` lui-meme quand rien
      ne change (la cuisson de `Garderobe` reste la meme), sinon une copie. */
  function habiller(tn, arch, c, pluie, perso, joueur) {
    const H = habitsDonnees(), h = empreinte(tn), fr = frilosite(tn);
    const gr = arch && B.defs.garderobe && B.defs.garderobe.garde_robes && B.defs.garderobe.garde_robes[arch];
    const o = Object.assign({}, tn);
    const metier = H.hauts_de_metier.indexOf(tn.haut) >= 0;
    const uniforme = H.chapeau_d_uniforme.indexOf(arch) >= 0;
    let acc = tn.accessoires || [];
    if (c >= H.grand_froid) {
      // Le grand froid : manteau (de la couleur du haut — le gang et l'uniforme se reconnaissent),
      // pantalon, bottes, tuque, et le foulard des frileux.
      if (!metier) { o.haut = 'manteau'; o.motif = 'uni'; }
      // ⚠️ UN VRAI MANTEAU D'HIVER (vague 4c) : fonce, pour une part des passants, a l'empreinte — jamais un
      // gang ni un uniforme (`haut_fixe` : sa couleur le fait reconnaitre), ni un personnage ou le joueur.
      const M = H.manteaux;
      if (!metier && M && !perso && !(gr && gr.haut_fixe) && ((h >>> 20) % 1000) / 1000 < M.part) {
        o.couleur_haut = M.couleurs[(h >>> 7) % M.couleurs.length];
      }
      if (o.bas === 'short') o.bas = 'pantalon';
      // ⚠️ LE JOUEUR N'A QUE CE QU'IL A ACHETE aux pieds et sur la tete (`rosa-habille-l-hiver.md`) : ses
      // bottes et sa tuque le gardent du froid — l'image ne peut pas le montrer botte s'il ne l'est pas.
      if (!joueur) o.souliers = 'bottes';
      if (!joueur && !uniforme && H.chapeaux_chauds.indexOf(o.chapeau) < 0) {
        o.chapeau = 'tuque';
        // La tuque d'un personnage (ou du joueur) est dans SA palette : la couleur de son bas.
        if (perso) o.couleur_chapeau = tn.couleur_bas || tn.couleur_chapeau;
      }
      if (!uniforme && fr > 0.4 && acc.indexOf('foulard') < 0 && acc.indexOf('cravate') < 0) acc = acc.concat(['foulard']);
      acc = acc.filter(function (a) { return a !== 'lunettes_soleil'; });
    } else if (c >= H.frais) {
      // La mi-saison fraiche : on couvre les bras et les jambes.
      if (o.haut === 'tshirt' || o.haut === 'camisole') o.haut = (arch === 'ado' || arch === 'skateux' || (h & 1)) ? 'coton_ouate' : 'chandail';
      if (o.bas === 'short') o.bas = 'pantalon';
      if (o.chapeau === 'canotier') o.chapeau = 'aucun';
      if (!uniforme && fr > 0.85 && o.chapeau === 'aucun') o.chapeau = 'tuque';
    } else if (c < H.chaud && !perso) {
      // L'ete : le manteau et la tuque restent a la maison ; des shorts pour qui en porte.
      if (!metier && (o.haut === 'manteau' || o.haut === 'coton_ouate' || (o.haut === 'chandail' && (h & 2)))) {
        o.haut = (h & 4) ? 'chemise' : 'tshirt';
      }
      if (!uniforme && (o.chapeau === 'tuque' || o.chapeau === 'capuche')) o.chapeau = (h & 8) ? 'casquette' : 'aucun';
      if (o.bas === 'pantalon' && gr && gr.bas.indexOf('short') >= 0 && fr < 0.4) o.bas = 'short';
      if (o.souliers === 'bottes' && gr && gr.souliers.indexOf('souliers') >= 0) o.souliers = 'souliers';
      acc = acc.filter(function (a) { return a !== 'foulard'; });
    }
    // Sous la pluie, sans parapluie : la capuche des frileux.
    if (pluie && !joueur && !aUnParapluie(tn) && !uniforme && fr > 0.5 && H.chapeaux_chauds.indexOf(o.chapeau) < 0) o.chapeau = 'capuche';
    o.accessoires = acc;
    const pareil = ['haut', 'motif', 'bas', 'souliers', 'chapeau', 'couleur_haut', 'couleur_chapeau'].every(function (k) { return o[k] === tn[k]; }) &&
      acc.join('+') === (tn.accessoires || []).join('+');
    return pareil ? tn : o;
  }

  /** Ce passant ouvre-t-il un parapluie quand il pleut ? A l'empreinte de sa tenue, pas au de. */
  function aUnParapluie(tn) {
    const H = habitsDonnees();
    return !!H && ((empreinte(tn) >>> 10) % 1000) / 1000 < H.parapluie.part;
  }

  //: Le moment des habits : le palier des saisons et la pluie, recalcules une fois par heure de jeu vue.
  //: ⚠️ Une fois par IMAGE, pas par passant : l'heure avance a chaque image, et c'est tout ce qui change.
  let momentH = null, momentJ = null, momentDedans = null, moment = null;
  function momentDesHabits() {
    const p = B.partie;
    if (!moment || !p || p.heure !== momentH || p.jour !== momentJ || B.interieur !== momentDedans) {
      momentH = p ? p.heure : null; momentJ = p ? p.jour : null; momentDedans = B.interieur;
      const pl = pleut();
      moment = { cle: cle() + (pl ? '|pluie' : ''), froid: palette().froid || 0, pluie: pl };
    }
    return moment;
  }

  const habits = new WeakMap();
  /** L'HABIT DU MOMENT d'un passant : `tn` (sa tenue tiree) habillee pour la saison et la pluie. Dedans,
      on a enleve son manteau. ⚠️ Les personnages et le joueur (vague 4c, Martin : « il change juste a
      l'exterieur ») s'habillent DEHORS, du cote du froid seulement et dans leur palette : leur tenue de
      tous les jours est leur tenue d'ete. La meme tenue sert aux deux (un personnage et un passant ne
      partagent jamais une tenue), d'ou la cle qui porte `perso`. */
  function vetir(tn, e) {
    if (!tn || !habitsDonnees() || B.interieur) return tn;
    const perso = !!(e && (e.personnage || e.type === 'joueur'));
    const m = momentDesHabits(), cle = perso ? m.cle + '|perso' : m.cle;
    const deja = habits.get(tn);
    if (deja && deja.cle === cle) return deja.tn;
    const c = m.froid + (frilosite(tn) - 0.5) * habitsDonnees().ecart;
    const r = habiller(tn, perso ? null : (e ? e.arch : null), c, m.pluie, perso, !!(e && e.type === 'joueur'));
    habits.set(tn, { cle: cle, tn: r });
    return r;
  }

  //: Ceux qui marchent tranquillement tiennent leur parapluie ; qui court, se bat ou fuit le referme.
  const AU_PAS = { flane: 1, cap: 1, arret: 1 };

  /** La couleur du parapluie de `e`, ou null : sous la pluie, dehors, un passant habille au pas. Le
      JOUEUR a le sien s'il l'a a la main (`partie.main`, chez Rosa) : il l'ouvre tout seul, meme en
      courant — jamais en frappant ni a l'eau. */
  function parapluie(e) {
    if (e.type === 'joueur') return parapluieDuJoueur(e);
    if (!e.tenue || !e.vivant || e.personnage || e.type !== 'pieton' || e.nage || !AU_PAS[e.etat]) return null;
    if (!momentDesHabits().pluie || !aUnParapluie(e.tenue)) return null;
    return e.tenue.accent || '#2980b9';
  }

  function parapluieDuJoueur(e) {
    const p = B.partie;
    if (!p || p.main !== 'parapluie' || !e.tenue || !e.vivant || e.nage || e.etat === 'attaque' || e.dansVehicule) return null;
    if (!momentDesHabits().pluie) return null;
    const t = (B.defs.tenues || []).find(function (x) { return x.slug === 'parapluie'; });
    return t ? t.couleur : '#1a1a22';
  }

  // ------------------------------------------------------------------ le son des saisons (lot 5)

  //: LE SON DES SAISONS (docs/jalons/les-quatre-saisons-realistes.md, lot 5) : une boucle d'ambiance par
  //: saison, dehors, dont le volume suit la palette du moment — pendant une transition, l'une descend
  //: pendant que l'autre monte, palier par palier, et le volume GLISSE d'une image a l'autre (jamais une
  //: coupure : la regle du fondu enchaine). ⚠️ Aucun de : une pure fonction du jour, de l'heure, de la
  //: pluie et de la piece.

  /** Le volume VOULU de chaque ambiance a ce moment : { slug: 0..1 }. Pure. */
  function sonA(jour, heure, dedans, pluie, tempete) {
    const d = donnees(), S = d && d.son, out = {};
    if (!S) return out;
    Object.keys(S.ambiances).forEach(function (k) { out[S.ambiances[k]] = 0; });
    if (dedans) return out;
    const p = position(jour, heure), t = p.de === p.vers ? 0 : p.palier / d.paliers;
    const lumiere = heureDeLumiere(jour, heure);
    let v = S.volume * (lumiere > 0.3 && lumiere < 0.8 ? 1 : S.nuit);
    v *= 1 - (1 - S.sous_la_pluie) * Math.max(pluie || 0, tempete || 0);
    out[S.ambiances[p.de]] += v * (1 - t);
    out[S.ambiances[p.vers]] += v * t;
    return out;
  }

  //: Ce qu'on entend, glisse image par image vers le voulu ; et quand on a demande chaque lieu.
  const sonJoue = {}, sonDemande = {};

  /** Chaque pas de jeu (`jeu.js`) : charge la saison qu'on va entendre, allume, regle et eteint ses boucles. */
  function majSon() {
    if (typeof Son === 'undefined' || !B.partie || !donnees() || !donnees().son) return;
    const S = donnees().son;
    const pluie = typeof Pluie !== 'undefined' ? Pluie.intensite() : 0;
    const tempete = typeof Neige !== 'undefined' && Neige.intensite ? Neige.intensite() : 0;
    const voulu = sonA(B.partie.jour, B.partie.heure, !!B.interieur, pluie, tempete);
    const pas = 1 - Math.exp(-(1 / 60) / (S.glisse_s / 3));
    const t = B.t || 0;
    for (const slug in voulu) {
      const avant = sonJoue[slug] || 0, cible = voulu[slug];
      let v = avant + (cible - avant) * pas;
      if (Math.abs(cible - v) < 0.004) v = cible;
      sonJoue[slug] = v;
      if (cible > 0 && Son.Lieu && t - (sonDemande[slug] === undefined ? -Infinity : sonDemande[slug]) >= 300) {
        sonDemande[slug] = t; Son.Lieu.charger(slug);
      }
      if (v > 0.004) {
        if (!Son.boucleActive(slug)) Son.boucle(slug, true, v, 0.5);
        else Son.reglerBoucle(slug, v);
      } else if (Son.boucleActive(slug)) Son.boucle(slug, false, 0, 0.5);
    }
  }

  /** Une partie recommencee : les ambiances se taisent, et repartent de zero. */
  function oublierSon() {
    for (const slug in sonJoue) { if (typeof Son !== 'undefined' && Son.boucleActive(slug)) Son.boucle(slug, false, 0, 0.5); sonJoue[slug] = 0; }
  }

  /** L'heure DE LUMIERE : l'heure de l'horloge fixe (`Monde.TEINTES`) qui a la meme lumiere que
      `heure` ce jour-la. Le jour reel (lever -> coucher, qui suivent l'annee) est etire sur le jour
      de reference (7 h 12 -> 19 h 12), la nuit reelle sur la nuit de reference. Pure et continue :
      l'annee glisse avec `jour + heure`, sans saut a minuit. */
  function heureDeLumiere(jour, heure) {
    const d = donnees();
    if (!d) return heure;
    const l = d.lumiere, x = Calendrier.jourDeLAnnee(jour) + heure;
    const c = Math.cos(2 * Math.PI * (x - l.solstice_ete) / d.annee);
    const lever = l.lever[0] + l.lever[1] * c, coucher = l.coucher[0] + l.coucher[1] * c;
    const rl = l.reference[0], rc = l.reference[1], h = heure * 24;
    let r;
    if (h >= lever && h <= coucher) r = rl + (h - lever) / (coucher - lever) * (rc - rl);
    else {
      const depuis = h > coucher ? h - coucher : h + 24 - coucher, nuit = 24 - (coucher - lever);
      r = rc + depuis / nuit * (24 - (rc - rl));
    }
    return (r % 24) / 24;
  }

  return { paletteA, cleA, palette, cle, enneiger, enHiver, coiffer, ficheDuMoment, heureDeLumiere,
           vetir, parapluie, habiller, frilosite, aUnParapluie, sonA, majSon, oublierSon, get sonJoue() { return sonJoue; } };
})();
