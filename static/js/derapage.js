/* Bandini — le vrai derapage (docs/jalons/les-quatre-saisons-realistes.md, lot 6).

   Un char ne flotte plus sur la glace, il DERAPE. `Vehicules.majPhysique` demande ici :
   - `volant` : ce qui reste du braquage — le SOUS-VIRAGE (lance sur un sol qui glisse, le volant mord
     moins) et les ROUES BLOQUEES (frein a fond sur la glace : il ne reste presque rien) ;
   - `majLacet` : le SURVIRAGE — le frein a main en courbe, ou le gaz a fond en tournant, font partir
     l'arriere (un lacet qui s'ajoute au cap ; laisse faire, le tete-a-queue) ; l'adherence le reprend peu
     a peu, et le CONTRE-BRAQUAGE beaucoup plus vite ;
   - `majSol` : les traces (noires au sec, un sillon dans la neige, rien sur la glace) et le crissement.

   ⚠️ AU SEC, RIEN NE CHANGE D'UN PIXEL : tout est proportionnel a la perte d'adherence (`perte`, 1 moins
   ce que le sol tient), et une perte nulle rend exactement l'ancien calcul. ⚠️ Aucun de. */

const Derapage = (function () {
  'use strict';

  //: ⚠️ LES REGLAGES VIVENT ICI, PAS DANS LE PAQUET : du ressenti de conduite que Python ne lit jamais, et le
  //: paquet des definitions a un plafond gzip (`test_definitions`) qu'ils faisaient deborder de 29 octets
  //: (30 sept. 2026). Au sec, rien de tout ca ne compte.
  const REGLAGES = {
    //: Le sous-virage : la part du volant perdue à pleine vitesse sur un sol sans aucune adhérence.
    "sous_virage": 0.9,
    //: Les roues bloquées : freiner à `frein` ou plus, TENU `tenu` images (au clavier, le frein est
    //: tout ou rien : des coups de frein gardent le volant — on pompe, comme en vrai l'hiver), lancé, sur un
    //: sol qui a perdu au moins `perte` de son adhérence (la neige, la glace ; pas la rue arrosée sous la
    //: pluie) — il ne reste que `volant` du braquage. Jamais pour un char de l'IA (la police fait demi-tour).
    "bloque": {"frein": 0.9, "perte": 0.45, "volant": 0.12, "tenu": 18},
    //: Le survirage : ce que le frein à main (en courbe) et le gaz à fond (en tournant) ajoutent au lacet à
    //: chaque image, par unité de perte et de vitesse relative ; au-dessus de `vitesse_min` (part de la
    //: pointe) et d'un volant tourné à `volant_min`. ⚠️ Le gaz, DOUX : plus fort, il compensait le sous-virage
    //: et le char tournait sur la glace autant qu'au sec (vu au banc).
    //: (`frein_main`, `gaz` : les coups ; `gaz_min`, `volant`, `vitesse` : les seuils.)
    "survirage": {"frein_main": 0.02, "gaz": 0.0006, "gaz_min": 0.8, "volant": 0.35, "vitesse": 0.3},
    //: Le lacet se reprend : `amorti` × l'adhérence par image, et `contre` × le volant tourné à l'opposé.
    "amorti": 0.1, "contre": 0.22, "lacet_max": 0.14,
    //: Les traces au sol (les roues arrière, une paire toutes les `pas` images) quand le char glisse de plus
    //: de `derive_min` radian au-dessus de `vitesse_min` px/image : `max` au plus, qui s'effacent en
    //: `duree_s` secondes. Au sec : une trace noire et le crissement ; dans la neige : un sillon ; sur la
    //: glace, rien — le silence.
    //: (`derive`, `vitesse` : les seuils ; `neige` : la couverture qui fait un sillon ; `crisse` : le
    //: crissement, au plus une fois toutes les tant d'images par char.)
    "traces": {"max": 160, "pas": 3, "derive": 0.3, "vitesse": 1.6, "duree_s": 45, "neige": 0.3, "crisse": 24},
  };

  let coupe = false;
  function donnees() { return coupe ? null : REGLAGES; }
  /** Pour les juges : couper le module (l'ancien calcul, au pixel), puis le remettre. */
  function couper(oui) { coupe = !!oui; }

  /** Ce qui reste du braquage (1 au sec). `t` : la vitesse en part de la pointe. */
  //: Ce qui ne derape pas : la MOTONEIGE (et ce qui est fait pour la neige, `hors_neige` sous 1) glisse sur
  //: ses skis comme avant (sa course des bois est reglee la-dessus) ; une COQUE n'a pas de roues.
  function exempt(v) { return !!(v.def && (v.def.hors_neige < 1 || v.def.eau)); }
  //: Un char conduit par l'IA (la police, les missions) : un bon conducteur — il ne bloque pas ses roues et
  //: rattrape son arriere de lui-meme (pas de tete-a-queue en pleine poursuite).
  function dePilote(v) { return v.conducteur !== B.joueur && !(v.conducteur && v.conducteur.coopJoueur2); }

  function volant(v, cmd, perte, t) {
    const d = donnees();
    if (!d || perte <= 0 || exempt(v)) return 1;
    let f = 1 - d.sous_virage * perte * Math.min(1, Math.abs(t));
    const b = d.bloque;
    if (cmd.frein >= b.frein && v.vitesse > 0.15 && perte >= b.perte && (v.freinT || 0) >= b.tenu && !dePilote(v)) f *= b.volant;
    return Math.max(0, f);
  }

  /** Le lacet de l'arriere qui part, ajoute au cap (rien au sec). `g` : l'adherence du sol. */
  function majLacet(v, cmd, perte, g, t) {
    const d = donnees();
    // Le frein TENU se compte (les roues bloquees l'attendent), au sec comme ailleurs.
    v.freinT = cmd.frein >= (d ? d.bloque.frein : 1) ? (v.freinT || 0) + 1 : 0;
    if (!d || perte <= 0 || exempt(v)) { v.lacet = 0; return; }
    let l = v.lacet || 0;
    const vt = Math.abs(t), vol = v.volant || 0, s = Math.sign(vol), sv = d.survirage;
    if (v.vitesse > 0 && vt >= sv.vitesse && Math.abs(vol) >= sv.volant) {
      if (cmd.freinMain) l += s * sv.frein_main * perte * vt;
      if (cmd.gaz >= sv.gaz_min) l += s * sv.gaz * perte * vt;
    }
    l *= 1 - d.amorti * g;                                                   // le sol le reprend
    if (vol && Math.sign(vol) === -Math.sign(l)) l *= 1 - d.contre * Math.abs(vol);   // le contre-braquage
    if (dePilote(v)) l *= 1 - d.contre;                                      // l'IA contre-braque d'elle-meme
    // ⚠️ LE LACET S'ETEINT AVEC LA VITESSE : il durait plus que l'elan, et un char arrete pivotait sur place
    // (trois quarts de tour sur la neige, vu par la relecture).
    l *= Math.min(1, Math.abs(t) / d.survirage.vitesse);
    if (Math.abs(v.vitesse) < 0.15) l = 0;
    l = Math.max(-d.lacet_max, Math.min(d.lacet_max, l));
    if (Math.abs(l) < 1e-4) l = 0;
    v.lacet = l;
    v.angle += l;
  }

  // --- Les traces au sol, et le crissement ------------------------------------------------------

  //: Les marques : { x, y, t (B.t), type ('trace' | 'sillon') } — bornees, elles s'effacent.
  const marques = [];
  let sonDemande = -Infinity;

  /** Chaque image : un char qui glisse de biais marque le sol (ses deux roues arriere) et, au sec,
      crisse. Sur la glace, rien : le silence qui inquiete. */
  function majSol(v, perte) {
    const d = donnees();
    if (!d || typeof Entites === 'undefined') return;
    if (v.crisseT > 0) v.crisseT--;
    // Le son du crissement — et les chocs selon ce qu'on frappe (`LIEUX["chocs"]`) — se chargent quand le JOUEUR conduit (redemande toutes les 300 images : un echec,
    // hors ligne, ne le perd pas pour la session).
    const t0 = B.t || 0;
    if (v.conducteur === B.joueur && t0 - sonDemande >= 300 && typeof Son !== 'undefined' && Son.Lieu) { sonDemande = t0; Son.Lieu.charger('derapage'); Son.Lieu.charger('chocs'); }
    if (exempt(v) || v.z > 0) return;                  // une coque ne marque pas l'eau ; en plein saut, rien au sol
    const tr = d.traces, vit = Math.hypot(v.vx || 0, v.vy || 0);
    if (vit < tr.vitesse) return;
    // ⚠️ Par rapport au SENS DE MARCHE : en marche arriere, le char va a l'envers de son cap sans glisser.
    const cap = v.vitesse < 0 ? v.angle + Math.PI : v.angle;
    const dir = Math.atan2(v.vy, v.vx), derive = Math.abs(Math.atan2(Math.sin(cap - dir), Math.cos(cap - dir)));
    if (derive < tr.derive) return;
    let type = null;
    if (perte <= 0) type = 'trace';
    else if (typeof Neige !== 'undefined' && Neige.couverture() >= tr.neige) type = 'sillon';
    if (!type) return;
    if (type === 'trace' && !(v.crisseT > 0) && typeof Son !== 'undefined' && Son.SFX && Son.SFX.crissement) {
      Son.SFX.crissement(v.x, v.y); v.crisseT = tr.crisse;
    }
    v.traceK = (v.traceK || 0) + 1;
    if (v.traceK % tr.pas !== 0) return;
    const ca = Math.cos(v.angle), sa = Math.sin(v.angle), l = ((v.def && v.def.longueur) || 30) / 2 - 3,
          w = ((v.def && v.def.largeur) || 14) / 2 - 2;
    const bx = v.x - ca * l, by = v.y - sa * l;
    for (const c of [-1, 1]) {
      if (marques.length >= tr.max) marques.shift();
      marques.push({ x: bx - sa * w * c, y: by + ca * w * c, t: B.t || 0, type: type });
    }
  }

  function traces() { return marques; }
  function oublier() { marques.length = 0; }

  /** Les marques au sol, sous les chars : elles palissent et s'effacent en `duree_s`. */
  function dessinerSol(ctx, cam) {
    const d = donnees();
    if (!d || !marques.length) return;
    const duree = d.traces.duree_s * 60, cx = Math.round(cam.x), cy = Math.round(cam.y), t = B.t || 0;
    while (marques.length && t - marques[0].t > duree) marques.shift();
    for (const m of marques) {
      const x = Math.round(m.x - cx), y = Math.round(m.y - cy);
      if (x < -4 || y < -4 || x > VW + 4 || y > VH + 4) continue;
      const a = Math.max(0, 1 - (t - m.t) / duree);
      ctx.fillStyle = m.type === 'trace' ? 'rgba(18,18,22,' + (0.4 * a).toFixed(3) + ')' : 'rgba(140,150,168,' + (0.55 * a).toFixed(3) + ')';
      ctx.fillRect(x - 1, y - 1, 2, 2);
    }
    B.stats.rects += marques.length;
  }

  return { donnees, couper, volant, majLacet, majSol, traces, oublier, dessinerSol };
})();
