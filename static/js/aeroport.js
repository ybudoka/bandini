/* Bandini — l'aéroport de Baie-des-Brumes, tel qu'on le voit du pont inachevé.

   ⚠️ Python décide (`app/aeroport.py`) : le plan de l'île, la piste, l'axe de la
   voie de circulation, la place des avions, le pont et sa travée manquante. Ce
   script ne fait que PEINDRE, une fois, dans le morceau de carte (`peindre`,
   appelé par `Monde` comme `Chantiers.peindre`) : rien n'y bouge d'une image à
   l'autre, et le budget d'image n'y touche jamais.

   ⚠️ Les avions sont PEINTS, pas des véhicules : personne ne peut encore s'en
   approcher (le pont s'arrête au-dessus de l'eau, la guérite ne lève pas sa
   barrière). Le jour où une mission en fait voler un, il entrera au catalogue des
   véhicules comme le chalutier y est entré.

   ⚠️ Et les arbres, la manche à air, les portes fermées aussi : une entité ou une
   porte `d` de plus au chargement décale le hasard de toute la ville
   (`aeroport.PEINTS`). On les peint avec le dessin du jeu, et rien ne naît. */

const Aeroport = (function () {
  'use strict';

  const BLANC = '#e6e4da', JAUNE = '#e0b43a';

  function fiche() {
    const def = typeof Monde !== 'undefined' && Monde.carte && Monde.carte.def;
    return (def && def.aeroport) || null;
  }

  /** Ce rectangle de tuiles touche-t-il le morceau (mx, my) ? `marge` en tuiles :
      ce qui déborde de sa tuile (une aile, un chiffre) doit se peindre aussi dans
      le morceau voisin, sinon la couture le coupe en deux. */
  function touche(x, y, l, h, ox, oy, marge) {
    const m = marge || 0;
    return x + l + m > ox && x - m < ox + 16 && y + h + m > oy && y - m < oy + 16;
  }

  // --- La piste -------------------------------------------------------------------

  /** Les marques d'une piste vue d'en haut : les deux lignes de bord, les seuils en
      touches de piano, les numéros (09 à l'ouest, 27 à l'est, lus par celui qui
      atterrit), les zones de toucher et l'axe en tirets. */
  function piste(ctx, p, ox, oy) {
    const x0 = (p.x - ox) * TT, y0 = (p.y - oy) * TT, L = p.l * TT, H = p.h * TT;
    const milieu = y0 + H / 2;
    ctx.fillStyle = BLANC;
    ctx.fillRect(x0 + 2, y0 + 3, L - 4, 2);
    ctx.fillRect(x0 + 2, y0 + H - 5, L - 4, 2);
    // Les seuils : huit touches de chaque côté de l'axe, un couloir libre au milieu.
    for (const bout of [x0 + 6, x0 + L - 6 - 34]) {
      for (let k = 0; k < 4; k++) {
        ctx.fillRect(bout, y0 + 11 + k * 8, 34, 4);
        ctx.fillRect(bout, milieu + 7 + k * 8, 34, 4);
      }
    }
    numero(ctx, '09', x0 + 58, milieu, 1);
    numero(ctx, '27', x0 + L - 58, milieu, -1);
    // Les zones de toucher : deux blocs de chaque côté de l'axe, à 150 px du seuil.
    for (const x of [x0 + 150, x0 + L - 150 - 44]) {
      ctx.fillRect(x, milieu - 26, 44, 8);
      ctx.fillRect(x, milieu + 18, 44, 8);
    }
    // L'axe : des tirets, entre les deux numéros.
    for (let x = x0 + 96; x < x0 + L - 96 - 28; x += 48) ctx.fillRect(x, milieu - 1, 28, 3);
  }

  /** Un numéro de piste : la police 5 × 7 à l'échelle 4, tourné pour être lu à
      l'approche — le haut des chiffres regarde le sens de l'atterrissage. */
  function numero(ctx, texte, cx, cy, sens) {
    const echelle = 4, largeur = Atlas.largeurTexte(texte, echelle);
    ctx.save();
    ctx.translate(cx, cy);
    ctx.rotate(sens * Math.PI / 2);
    Atlas.texte(ctx, texte, -largeur / 2, -14, BLANC, echelle);
    ctx.restore();
  }

  /** Les balises des bords : un plot et sa lentille (la lueur de nuit, elle, est une
      LAMPE du paquet — `sorte: balise`). */
  function balises(ctx, a, ox, oy) {
    for (const b of a.balises || []) {
      if (!touche(b[0], b[1], 1, 1, ox, oy, 1)) continue;
      const x = (b[0] - ox) * TT + 7, y = (b[1] - oy) * TT + (b[1] === a.piste.y ? 1 : 12);
      ctx.fillStyle = '#3a3d44'; ctx.fillRect(x - 1, y - 1, 4, 4);
      ctx.fillStyle = '#f3e7b0'; ctx.fillRect(x, y, 2, 2);
    }
  }

  /** L'axe jaune de la voie de circulation : une ligne par segment, au milieu des
      tuiles ; au bout de chaque bretelle, la ligne d'arrêt avant la piste (deux
      pleines, deux tiretées) — on ne roule pas sur une piste sans permission. */
  function axes(ctx, a, ox, oy) {
    ctx.fillStyle = JAUNE;
    for (const s of a.axes || []) {
      const x = Math.min(s[0], s[2]), y = Math.min(s[1], s[3]);
      const l = Math.abs(s[2] - s[0]) + 1, h = Math.abs(s[3] - s[1]) + 1;
      if (!touche(x, y, l, h, ox, oy, 1)) continue;
      const px = (x - ox) * TT, py = (y - oy) * TT;
      if (h === 1) ctx.fillRect(px + 7, py + 7, (l - 1) * TT + 2, 2);
      else ctx.fillRect(px + 7, py + 7, 2, (h - 1) * TT + 2);
      if (h > 1 && y + h === a.piste.y) {
        const bas = py + (h - 1) * TT + 2;
        ctx.fillRect(px - 9, bas, 34, 2); ctx.fillRect(px - 9, bas + 4, 34, 2);
        for (let k = 0; k < 34; k += 6) { ctx.fillRect(px - 9 + k, bas + 8, 3, 2); ctx.fillRect(px - 9 + k, bas + 12, 3, 2); }
      }
    }
  }

  // --- Les avions -----------------------------------------------------------------

  //: Les livrées : le fuselage, la bande et la dérive, l'aile.
  const LIVREES = {
    brumes: { fuselage: '#e9ecef', bande: '#23406e', derive: '#23406e', aile: '#c9ced4' },
    gaspesie: { fuselage: '#eceae4', bande: '#b3322b', derive: '#b3322b', aile: '#cdd0d3' },
    aeroclub: { fuselage: '#f1efe6', bande: '#d9a52b', derive: '#d9a52b', aile: '#e8c75a' },
  };
  //: Les gabarits, en pixels, le nez au nord : longueur, largeur du fuselage,
  //: envergure, corde de l'aile, empennage.
  const MODELES = {
    bimoteur: { long: 108, fus: 14, env: 124, corde: 14, aileY: -10, emp: 44, moteurs: [-28, 28] },
    monomoteur: { long: 46, fus: 8, env: 60, corde: 9, aileY: -8, emp: 20, moteurs: [0] },
  };

  /** Un avion vu d'en haut, centré sur sa tuile. ⚠️ Tout est dessiné dans le repère
      de l'avion (nez vers -y), puis tourné selon son cap : un avion garé le nez à
      l'est n'est qu'un angle de plus. */
  function avion(ctx, v, ox, oy) {
    const m = MODELES[v.modele] || MODELES.bimoteur, l = LIVREES[v.livree] || LIVREES.brumes;
    const cx = (v.x - ox) * TT + 8, cy = (v.y - oy) * TT + 8;
    const cap = { N: 0, E: 0.5, S: 1, O: -0.5 }[v.cap] || 0;
    ctx.save();
    ctx.translate(cx, cy);
    ctx.rotate(cap * Math.PI);
    const demi = m.long / 2, f = m.fus / 2, e = m.env / 2;
    // L'ombre, au sud-est : c'est elle qui décolle l'avion du béton.
    ctx.fillStyle = 'rgba(11,10,18,0.28)';
    ctx.fillRect(-f + 5, -demi + 8, m.fus, m.long);
    ctx.fillRect(-e + 5, m.aileY + 6, m.env, m.corde);
    ctx.fillRect(-m.emp / 2 + 5, demi - 12 + 6, m.emp, 8);
    // L'empennage d'abord (sous le fuselage), puis l'aile.
    ctx.fillStyle = l.aile;
    ctx.fillRect(-m.emp / 2, demi - 12, m.emp, 8);
    ctx.fillStyle = 'rgba(0,0,0,0.15)'; ctx.fillRect(-m.emp / 2, demi - 6, m.emp, 2);
    ctx.fillStyle = l.aile;
    ctx.fillRect(-e, m.aileY, m.env, m.corde);
    ctx.fillRect(-e + 4, m.aileY - 1, m.env - 8, 1);                         // le bord d'attaque arrondi
    ctx.fillStyle = 'rgba(0,0,0,0.18)'; ctx.fillRect(-e, m.aileY + m.corde - 3, m.env, 3);   // les volets
    ctx.fillStyle = l.bande; ctx.fillRect(-e, m.aileY, 3, m.corde); ctx.fillRect(e - 3, m.aileY, 3, m.corde);
    // Le fuselage : un long cigare, le nez et la queue effilés.
    ctx.fillStyle = l.fuselage;
    ctx.fillRect(-f, -demi + 8, m.fus, m.long - 16);
    ctx.fillRect(-f + 2, -demi + 3, m.fus - 4, 6);
    ctx.fillRect(-f + 4, -demi, m.fus - 8, 4);
    ctx.fillRect(-f + 2, demi - 8, m.fus - 4, 6);
    ctx.fillRect(-f + 4, demi - 3, m.fus - 8, 3);
    ctx.fillStyle = 'rgba(255,255,255,0.35)'; ctx.fillRect(-f + 2, -demi + 10, 2, m.long - 22);
    ctx.fillStyle = l.bande; ctx.fillRect(-f, -demi + 14, 1, m.long - 26); ctx.fillRect(f - 1, -demi + 14, 1, m.long - 26);
    // Le poste de pilotage : le pare-brise, en bandeau sombre.
    ctx.fillStyle = '#243240'; ctx.fillRect(-f + 2, -demi + 6, m.fus - 4, 3);
    ctx.fillStyle = '#5a7890'; ctx.fillRect(-f + 3, -demi + 6, 2, 1);
    // La dérive, vue d'en haut : une arête de la couleur de la livrée.
    ctx.fillStyle = l.derive; ctx.fillRect(-1, demi - 22, 3, 20);
    // Les moteurs et leurs hélices, figées en disque flou.
    for (const mx of m.moteurs) {
      if (m.moteurs.length > 1) {
        ctx.fillStyle = '#b8bdc3'; ctx.fillRect(mx - 5, m.aileY - 14, 10, m.corde + 20);
        ctx.fillStyle = '#8d9399'; ctx.fillRect(mx - 5, m.aileY + m.corde, 10, 6);
        ctx.fillStyle = '#3a3d44'; ctx.fillRect(mx - 2, m.aileY - 16, 4, 3);
        ctx.fillStyle = 'rgba(40,44,52,0.55)'; ctx.fillRect(mx - 15, m.aileY - 17, 30, 2);
      } else {
        ctx.fillStyle = '#3a3d44'; ctx.fillRect(-2, -demi - 2, 4, 3);
        ctx.fillStyle = 'rgba(40,44,52,0.55)'; ctx.fillRect(-11, -demi - 3, 22, 2);
      }
    }
    ctx.restore();
    // Les cales sous les roues : deux petits blocs jaunes, pour qu'on sache qu'il ne part pas.
    ctx.fillStyle = JAUNE;
    ctx.fillRect(cx - 7, cy + 6, 3, 2); ctx.fillRect(cx + 5, cy + 6, 3, 2);
  }

  // --- Le pont inachevé ------------------------------------------------------------

  /** Le bout d'un tablier qui s'arrête : un muret de béton rayé, et les fers qui
      dépassent au-dessus de l'eau. `vers` : +1 si l'eau est au sud, -1 au nord. */
  function boutDeTablier(ctx, x, y, l, vers) {
    const bord = vers > 0 ? y + TT - 6 : y + 1;
    ctx.fillStyle = '#8e8f8c'; ctx.fillRect(x, bord, l * TT, 5);
    for (let k = 0; k < l * TT; k += 8) {
      ctx.fillStyle = '#d98324'; ctx.fillRect(x + k, bord + 1, 4, 3);
      ctx.fillStyle = '#efe6d0'; ctx.fillRect(x + k + 4, bord + 1, 4, 3);
    }
    ctx.fillStyle = '#7a4a2a';
    const fers = vers > 0 ? y + TT : y - 6;
    for (let k = 3; k < l * TT; k += 5) ctx.fillRect(x + k, fers, 1, 6);
  }

  /** Une pile qui attend son tablier : le chevêtre de béton en travers, deux fûts
      dessous, l'eau qui clapote au pied. */
  function pile(ctx, x, y, l) {
    ctx.fillStyle = 'rgba(11,10,18,0.3)'; ctx.fillRect(x + 4, y + 6, l * TT, 9);
    ctx.fillStyle = '#9c9d99'; ctx.fillRect(x, y + 3, l * TT, 8);
    ctx.fillStyle = '#b8b9b4'; ctx.fillRect(x, y + 3, l * TT, 2);
    ctx.fillStyle = '#6f706c'; ctx.fillRect(x, y + 10, l * TT, 1);
    ctx.fillStyle = '#7a4a2a';
    for (let k = 4; k < l * TT; k += 6) ctx.fillRect(x + k, y + 1, 1, 3);
    ctx.fillStyle = 'rgba(220,235,245,0.5)';
    ctx.fillRect(x + 6, y + 12, 6, 1); ctx.fillRect(x + l * TT - 12, y + 12, 6, 1);
  }

  function pont(ctx, p, ox, oy) {
    if (!touche(p.x, p.y, p.l, p.nord + p.trou + p.sud, ox, oy, 1)) return;
    const x = (p.x - ox) * TT;
    boutDeTablier(ctx, x, (p.y + p.nord - 1 - oy) * TT, p.l, 1);
    boutDeTablier(ctx, x, (p.y + p.nord + p.trou - oy) * TT, p.l, -1);
    const rangees = new Set((p.piles || []).map(function (q) { return q[1]; }));
    rangees.forEach(function (ty) { pile(ctx, x, (ty - oy) * TT, p.l); });
  }

  /** Un décor du jeu (`DECORS`), peint à plat dans le morceau : son pied au bas de
      sa tuile, comme `Entites.creerDecor` le pose. */
  function peint(ctx, type, x, y, ox, oy) {
    const f = typeof DECORS !== 'undefined' && DECORS[type];
    if (!f || !f.peindre) return;
    ctx.save();
    ctx.translate((x - ox) * TT + 8 - f.ancre[0], (y - oy) * TT + 15 - f.ancre[1]);
    f.peindre(ctx, f.w, f.h);
    ctx.restore();
  }

  /** Une porte fermée dans une façade : un battant de tôle, ou le rideau d'un hangar
      (`large` tuiles, des lattes). Elle ne promet rien — pas de poignée dorée. */
  function porteFermee(ctx, x, y, large, ox, oy) {
    const px = (x - ox) * TT - Math.floor((large - 1) / 2) * TT, py = (y - oy) * TT;
    const l = large * TT;
    ctx.fillStyle = '#2b2d33'; ctx.fillRect(px + 2, py + 2, l - 4, 14);
    ctx.fillStyle = '#6c7178'; ctx.fillRect(px + 3, py + 3, l - 6, 13);
    ctx.fillStyle = '#50545a';
    for (let k = py + 5; k < py + 16; k += 3) ctx.fillRect(px + 3, k, l - 6, 1);
    ctx.fillStyle = '#e8b33c'; ctx.fillRect(px + l / 2 - 3, py + 8, 6, 3);        // l'écriteau PRIVÉ
  }

  /** Tout ce qui se peint dans le morceau (mx, my). */
  function peindre(ctx, mx, my) {
    const a = fiche();
    if (!a) return;
    const ox = mx * 16, oy = my * 16;
    if (a.pont) pont(ctx, a.pont, ox, oy);
    const plan = a.plan;
    if (!plan || !touche(plan[0], plan[1], plan[2], plan[3], ox, oy, 4)) return;
    if (a.piste && touche(a.piste.x, a.piste.y, a.piste.l, a.piste.h, ox, oy, 2)) piste(ctx, a.piste, ox, oy);
    balises(ctx, a, ox, oy);
    axes(ctx, a, ox, oy);
    for (const d of a.portes_peintes || []) {
      if (touche(d[0] - 1, d[1], d[2] + 2, 1, ox, oy, 1)) porteFermee(ctx, d[0], d[1], d[2], ox, oy);
    }
    for (const d of a.peints || []) {
      if (touche(d[1], d[2], 1, 1, ox, oy, 2)) peint(ctx, d[0], d[1], d[2], ox, oy);
    }
    for (const v of a.avions || []) {
      if (touche(v.x, v.y, 1, 1, ox, oy, 5)) avion(ctx, v, ox, oy);
    }
  }

  return { peindre, LIVREES, MODELES, fiche };
})();
