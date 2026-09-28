/* Bandini — le feu de bâtiment (P4, « le pompier volontaire »).

   ⚠️ PYTHON DÉCIDE, ICI ON BRÛLE. La règle (`carte.incendies.regle`) et les
   façades où un feu PEUT se déclarer (`facades`) viennent du paquet. QUAND il
   se déclare est une fonction de l'heure — tirée à l'empreinte (`hash2`),
   jamais au dé du jeu : deux joueurs voient le même feu au même moment, et un
   juge peut rejouer l'heure sans que la ville bouge.

   On l'éteint à l'EXTINCTEUR : le jet attire la flamme (`majJet`, appelé par
   `Combat` quand on tient la gâchette), on touche la façade de loin, et la
   prime tombe — une fois. C'est le pompier volontaire : pas de camion, pas de
   palier, une réponse à un feu qui n'attend pas.

   ⚠️ RIEN NE SE SAUVEGARDE. Un feu qui brûle est une EMPREINTE de l'heure,
   comme le bris d'aqueduc : une partie rechargée retrouve le feu en cours
   (son heure n'est pas passée), et un feu éteint se re-déclare au rechargement.
   C'est le prix de garder la ville déterministe.

   ⚠️ Le feu ne se déclare JAMAIS sous les yeux : il naît à l'heure, mais le
   navigateur ne l'ALLUME (fumée, flammes) que quand la façade est hors de
   l'écran — sinon un mur prend feu d'un coup au milieu d'une rue. La leçon des
   chantiers.
*/

const Incendies = (function () {
  'use strict';

  //: On n'échantillonne l'heure qu'une image sur trente : un feu ne se déclare
  //: pas à la demi-seconde près, et la ville n'a rien à gagner à sonder le jour
  //: soixante fois par seconde.
  const CADENCE = 30;
  //: La marge de fumée au-dessus de la façade : les flammes montent.
  const MARGE = 48;
  //: À cette distance, on VOIT la fumée et le feu s'entend.
  const PORTEE_FUMEE_PX = 420;

  //: Le feu d'une MISSION (M16, `eteindre`) résiste : il faut tenir le jet
  //: dessus ce nombre d'images (un tiers de seconde), pas une seule. Trois feux
  //: en coûtent 60 sur les 100 d'un extincteur plein — de quoi en rater un peu.
  const FORCE_DE_MISSION = 20;

  const eteints = {};      // jour:heure -> true : déjà éteint, jamais re-payé
  const allumes = {};      // jour:heure -> { f } : le feu en train de brûler à l'écran
  const signales = {};     // jour:heure -> true : le message « INCENDIE » est parti
  // ⚠️ LE FEU D'UNE MISSION n'est PAS un feu de l'heure (M16, 28 sept. 2026) :
  // `feuActif()` est un tirage de la ville entière, et aucune mission ne pouvait
  // allumer le sien. Celui-ci est posé par `Histoire` (objectif `eteindre`) sur
  // la façade la plus proche du lieu qu'il nomme — un seul à la fois, éteint au
  // même jet, jamais payé à la prime (c'est la mission qui paie), et retiré avec
  // la mission. Rien ne se sauvegarde : une mission ne survit pas au chargement.
  let feuMission = null;

  function donnees() { return B.defs && B.defs.carte && B.defs.carte.incendies; }

  function cle(jour, heure) { return jour + ':' + heure; }

  /** La façade qui brûle à cette heure-ci — ou null. Pure, à l'exception du
      registre des feux éteints (la mémoire du joueur, pas de la ville). */
  function feuActifA(jour, heure) {
    const d = donnees();
    if (!d || !d.regle || !(d.facades || []).length) return null;
    const r = d.regle;
    const minute = heure * 24 * 60;
    const hh = Math.floor(minute / 60);
    const ecoule = minute - hh * 60;
    // ⚠️ Le feu brûle du haut de l'heure, et s'éteint tout seul passé `minutes`.
    if (ecoule >= r.minutes) return null;
    if (eteints[cle(jour, hh)]) return null;
    const graine = jour * 1607 + hh;
    if (hash2(graine, 0xA9DE) / 4294967296 >= r.chance_par_heure) return null;
    const f = d.facades[hash2(graine, 0x5EA0) % d.facades.length];
    return { f: f, r: r, jour: jour, heuredelajour: hh, minute: ecoule };
  }

  /** La façade la plus proche d'un pixel : une tuile qui n'est PAS marchable (le
      mur) avec du trottoir juste au sud, pour qu'on puisse s'en approcher. Une
      spirale déterministe — jamais un dé — qui préfère un mur à une porte : un
      feu sur le pas de la porte boucherait l'entrée. */
  function facadePres(x, y, rayonMax) {
    const tx = Math.floor(x / TT), ty = Math.floor(y / TT);
    const portes = (Monde.carte && Monde.carte.def && Monde.carte.def.portes) || [];
    const estPorte = function (a, b) { return portes.some(function (q) { return q.x === a && q.y === b; }); };
    let repli = null;
    for (let r = 0; r <= (rayonMax || 6); r++) {
      for (let dy = -r; dy <= r; dy++) for (let dx = -r; dx <= r; dx++) {
        if (Math.max(Math.abs(dx), Math.abs(dy)) !== r) continue;
        const a = tx + dx, b = ty + dy;
        if (Monde.marchablePieton(a, b) || !Monde.marchablePieton(a, b + 1)) continue;
        if (!estPorte(a, b)) return { x: a, y: b };
        if (!repli) repli = { x: a, y: b };
      }
    }
    return repli;
  }

  /** Allume LE feu d'une mission sur la façade la plus proche de `(x, y)`, et le
      rend — ou null s'il n'y a pas de mur à brûler par là. */
  function allumerPourMission(x, y) {
    const f = facadePres(x, y, 6);
    if (!f) { feuMission = null; return null; }
    const d = donnees();
    const r = (d && d.regle) || { rayon_px: 44, prime: 0 };
    feuMission = { f: { x: f.x, y: f.y, genre: 'commerce' }, r: r, mission: true,
                   force: FORCE_DE_MISSION, forceMax: FORCE_DE_MISSION, eteint: false, signale: false };
    return feuMission;
  }

  /** Le feu de la mission qui brûle encore, ou null. */
  function feuDeMission() { return feuMission && !feuMission.eteint ? feuMission : null; }

  /** La mission s'en va (réussie, ratée, abandonnée) : son feu avec elle. */
  function oublierLeFeuDeMission() { feuMission = null; }

  function feuActif() {
    if (!B.partie || B.interieur) return null;
    return feuActifA(B.partie.jour, B.partie.heure);
  }

  /** Le feu à l'écran, position du mur en PIXELS pour le marqueur et le jet. */
  function position(fe) {
    return { x: fe.f.x * TT + 8, y: fe.f.y * TT + 14, nom: nomDe(fe.f) };
  }

  /** Le nom à afficher : celui de la devanture (lu sur la ville servie), sinon
      le genre. ⚠️ Il se résout ICI, au moment où l'on sert : la table de Python
      ne porte que la géométrie, pour rester insensible au changement des noms
      (`vitrines`), comme l'exige `test_les_commerces_montent_sans_rien_deplacer`. */
  function nomDe(f) {
    const carte = Monde.carte && Monde.carte.def;
    if (carte) {
      for (const d of (carte.devantures || [])) {
        if (f.x >= d.x && f.x < d.x + d.l && f.y === d.y) return d.texte || 'LE COMMERCE';
      }
    }
    return f.genre === 'logement' ? 'LE LOGEMENT' : 'LE COMMERCE';
  }

  /** Ce que le HUD doit pointer : un feu en cours, s'il y en a un. */
  function cible() {
    const fe = feuActif();
    if (!fe) return null;
    const p = position(fe);
    return { x: p.x, y: p.y, nom: p.nom, couleur: '#ff6a3c' };
  }

  /** Le jet d'extincteur attire la flamme : si l'on tient la gâchette d'un
      `jet` et que le feu est dans le cône, à portée, on l'éteint. Appelé par
      `Combat.majJet`, donc à chaque image de la phase active.

      ⚠️ `arme.portee` dit LA portée du jet ; `rayon_px` de la règle dit à quelle
      distance de la FAÇADE on attrape la flamme. Les deux se cumulent : on se
      tient près du mur ET on vise le mur. */
  function majJet(e) {
    const arme = e.arc;
    if (!arme || arme.type !== 'jet' || e.phase !== 'actif') return;
    // Le feu de la mission d'abord : il RÉSISTE (`force`), une image de jet à la fois.
    const fm = feuDeMission();
    if (fm && dansLeJet(e, arme, fm)) {
      fm.force--;
      if (fm.force <= 0) eteindreLeFeuDeMission(fm);
      return;
    }
    const fe = feuActif();
    if (!fe || !dansLeJet(e, arme, fe)) return;
    eteindre(fe);
  }

  function dansLeJet(e, arme, fe) {
    const p = position(fe);
    if (dist2(e.x, e.y, p.x, p.y) > (arme.portee + fe.r.rayon_px) * (arme.portee + fe.r.rayon_px)) return false;
    return Math.abs(ecartAngle(e.angle, angleVers(e.x, e.y, p.x, p.y))) <= 0.9;
  }

  /** La bouffée blanche de l'eau sur la braise — le même adieu pour les deux feux. */
  function bouffee(p) {
    for (let i = 0; i < 14; i++) {
      Entites.particule(p.x + (B.rng() - 0.5) * 26, p.y - 4 - B.rng() * 10,
                        (B.rng() - 0.5) * 0.5, -0.4 - B.rng() * 0.4, 26 + B.rng() * 14, '#e8e6de', 2, -0.01);
    }
  }

  /** ⚠️ Pas de prime : c'est la mission qui paie. Le feu dit seulement qu'il est mort. */
  function eteindreLeFeuDeMission(fm) {
    fm.eteint = true;
    bouffee(position(fm));
    if (typeof Hud !== 'undefined') Hud.message('FEU ÉTEINT', 150);
    if (typeof Son !== 'undefined') Son.SFX.eau();
  }

  function eteindre(fe) {
    eteints[cle(fe.jour, fe.heuredelajour)] = true;
    // ⚠️ Le feu qui s'éteint ne laisse pas une façade charbonneuse : il laisse
    // une bouffée de fumée blanche — l'eau sur la braise. Puis plus rien.
    const p = position(fe);
    bouffee(p);
    if (typeof Missions !== 'undefined') Missions.encaisser(fe.r.prime, 'INCENDIE MAÎTRISÉ');
    if (typeof Hud !== 'undefined') Hud.message('INCENDIE MAÎTRISÉ — ' + p.nom.toUpperCase(), 240);
    if (typeof Son !== 'undefined') { Son.SFX.argent(); Son.SFX.eau(); }
  }

  /** Allume un feu hors de l'écran, pour qu'il ne naisse pas sous les yeux. */
  function allumer(fe) {
    const k = cle(fe.jour, fe.heuredelajour);
    if (allumes[k]) return;
    allumes[k] = fe;
  }

  function maj() {
    if (!B.partie || B.interieur) return;
    // ⚠️ La RÈGLE (qui brûle) s'échantillonne à `CADENCE` ; les FLAMMES, elles,
    // montent à chaque image pour de vrai, sinon le feu fume par à-coups.
    // ⚠️ Le feu est CONTINU, pas un changement de phase discret : pas de fondu
    // d'apparition à masquer. Sa fumée se voit de loin, et c'est par elle qu'on
    // le trouve — il brûle donc tant que l'heure le dit, visible ou pas.
    if (B.t % CADENCE === 0) {
      const fe = feuActif();
      // Un feu passé (ou éteint) cesse de brûler à l'écran.
      for (const k in allumes) {
        if (eteints[k]) { delete allumes[k]; delete signales[k]; continue; }
        if (!fe || cle(fe.jour, fe.heuredelajour) !== k) delete allumes[k];
      }
      if (fe && !allumes[cle(fe.jour, fe.heuredelajour)]) allumer(fe);
    }
    // Le feu d'une mission brûle PLUS FORT que celui de l'heure (il « gagne la
    // façade »), et il recule quand on tient le jet dessus : ses flammes suivent
    // sa `force`. Il n'a pas de message « INCENDIE » : la mission l'a déjà dit.
    let bruit = null;
    const fm = feuDeMission();
    if (fm) bruit = flammes(fm, 0.5 + fm.force / fm.forceMax);
    const k = Object.keys(allumes)[0];
    if (k) {
      const fe = allumes[k];
      const p = position(fe);
      const b = flammes(fe, 1);
      bruit = bruit === null ? b : Math.max(bruit, b);
      // Et le feu se signale : une fois, quand on est assez près pour le voir.
      if (!signales[k] && Entites.visibleAEcran(p.x, p.y, PORTEE_FUMEE_PX) && typeof Hud !== 'undefined') {
        signales[k] = true;
        Hud.message('INCENDIE — ' + p.nom.toUpperCase(), 240);
      }
    }
    // Le feu s'entend quand on s'en approche.
    if (bruit !== null && typeof Son !== 'undefined') Son.SFX.rumeur_incendie(bruit);
  }

  /** La fumée et les flammes d'un feu, `vif` fois celles du feu de l'heure ; rend
      à quel point il s'entend d'où l'on est (1 dessus, 0 et moins au loin).

      ⚠️ DÉTERMINISTES, comme le bris d'aqueduc : elles se tirent de l'empreinte
      de la façade et de l'image (`hash2`), pas de `B.rng()` — un feu qui brûle au
      fond de la ville ne doit pas décaler le dé de tout le monde, ni une scène de
      mission qui le filme. C'est la leçon du champ de hasard, qui a fait tomber
      des juges sans rapport plus d'une fois. */
  function flammes(fe, vif) {
    const p = position(fe);
    const h = function (sel) { return hash2(fe.f.x * 397 + sel, fe.f.y * 71 + B.t) / 4294967296; };
    const fumee = vif > 1.2 ? 2 : 3, feu = vif > 1.2 ? 3 : 6;
    if (B.t % fumee === 0) {
      Entites.particule(p.x + (h(1) - 0.5) * 12 * vif, p.y - 6,
                        (h(2) - 0.5) * 0.15, -0.35 - h(3) * 0.3, 42 + h(4) * 20, '#3a3a3a', 3, -0.01);
    }
    if (B.t % feu === 0) {
      const a = h(5) * Math.PI * 2, d = h(6) * 5 * vif;
      Entites.particule(p.x + Math.cos(a) * d, p.y - Math.abs(Math.sin(a)) * d * 0.4,
                        (h(7) - 0.5) * 0.2, -0.5 - h(8) * 0.5, 14 + h(9) * 10,
                        h(10) < 0.5 ? '#ff8c1a' : '#ffd23a', 2, -0.02);
    }
    return 1 - Math.hypot(p.x - B.joueur.x, p.y - B.joueur.y) / PORTEE_FUMEE_PX;
  }

  /** Remet la mémoire à zéro : une nouvelle partie repart sans feux éteints. */
  function oublier() {
    for (const k in eteints) delete eteints[k];
    for (const k in allumes) delete allumes[k];
    for (const k in signales) delete signales[k];
    feuMission = null;
  }

  return { donnees, feuActifA, feuActif, cible, position, majJet, maj, oublier,
           allumerPourMission, feuDeMission, oublierLeFeuDeMission, facadePres };
})();