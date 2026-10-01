/* Bandini — la glace noire (docs/jalons/les-quatre-saisons-realistes.md, lot 6, vague 6b).

   L'hiver, la ville a ses PLAQUES DE GLACE : sur la chaussee (souvent a la ligne d'arret, la ou les chars
   polissent la neige), sur les trottoirs, et sur le tablier du pont de La Pointe, qui gele avant tout le
   reste. En avril et en novembre, LE GEL ET LE DEGEL : la glace du matin fond vers midi, et regele le soir
   si le lendemain gele encore.

   ⚠️ RIEN NE SE POSE, RIEN NE SE TIRE : une plaque est une fonction de sa CELLULE de la carte (`cellule`
   tuiles de cote) — l'empreinte de la cellule dit s'il y en a une, ou, et sa forme. Aucun de, aucune entite,
   aucun identifiant, aucune tuile changee : la ville ne glisse pas, et deux joueurs ont les memes plaques.
   L'intensite (0 a 1) est une fonction du jour et de l'heure (`intensiteA`) : rien a sauvegarder.

   Ce qu'elle fait :
   - aux CHARS (`adherence`, `frein`, lus par `Vehicules.majPhysique`) : sur une plaque, le sol ne tient plus
     que `adherence` — le DERAPAGE de la vague 6a s'eveille (sous-virage, survirage, roues bloquees) ; les
     pneus d'hiver de Ti-Guy en rendent une part ;
   - au TRAFIC, sur ses rails (`rouler`) : il demarre en patinant et freine long, le derriere qui chasse un
     peu — mais il ne quitte jamais sa voie, et la police en pleine poursuite n'y glisse pas ;
   - a l'IA au volant (la police hors des rails, les poursuivants) : le meme derapage, qu'elle rattrape d'elle-
     meme (vague 6a) — elle arrive plus tard, mais elle arrive : elle ne tourne pas autour du joueur (juge) ;
   - a PIED : le joueur qui court sur une plaque glisse, puis tombe ; un passant qui s'y sauve en courant
     tombe aussi (`faitTomber`). On marche dessus sans tomber.

   ⚠️ AU SEC (l'ete, l'automne, un apres-midi d'avril), `intensite()` rend 0, et 0 ne change rien : la
   conduite, les pas et le dessin sont ceux d'avant, au pixel. */

const Glace = (function () {
  'use strict';

  //: ⚠️ LES REGLAGES VIVENT ICI, PAS DANS LE PAQUET (comme `Derapage`) : du ressenti que Python ne lit jamais,
  //: et le paquet des definitions a un plafond gzip.
  const REGLAGES = {
    //: L'empreinte de la glace : change-la, et toutes les plaques changent de place.
    "sel": 0x61ACE5,
    //: Une plaque au plus par cellule de `cellule` tuiles de cote, une cellule sur `une_sur`.
    "cellule": 6, "une_sur": 4,
    //: Une plaque sur `trottoir_une_sur` est sur le trottoir ; une plaque de chaussee sur `arret_une_sur`
    //: se pose sur la ligne d'arret quand sa cellule en a une (la neige polie par les chars qui freinent).
    "trottoir_une_sur": 3, "arret_une_sur": 2,
    //: Les demi-axes d'une plaque (px) : sa longueur dans le sens de la rue, sa largeur en travers.
    "long": [16, 34], "large": [8, 14],
    //: Le pont gele avant tout : une plaque a toutes les `pont_pas` tuiles de son tablier, `pont_long` de long.
    "pont_pas": 3, "pont_long": [18, 28],
    //: Ce que la glace laisse au char, et a son frein (le verglas : 0,4 et 0,55 ; la tempete de neige : 0,3).
    "adherence": 0.3, "frein": 0.45,
    //: Le gel et le degel (avril, novembre) : pleine jusqu'a `gel_h`, fondue a `fondu_h`, elle regele des
    //: `regel_h` (pleine a minuit) si le lendemain gele encore.
    "degel": {"mois": ["avril", "novembre"], "gel_h": 8, "fondu_h": 12, "regel_h": 20},
    //: A pied. Le joueur qui COURT sur la glace garde `elan` de son elan d'avant (il glisse), et tombe au bout de
    //: `course_images` images de course de suite (`bottes` avec des bottes d'hiver) ; au sol `au_sol` images.
    "joueur": {"elan": 0.85, "course_images": 14, "bottes": 24, "au_sol": 45},
    //: Un passant qui s'y sauve en courant (au-dessus de `vitesse` px/image) tombe au bout de `course_images`
    //: + (son numero modulo `ecart`) images — a l'empreinte, jamais un de ; au sol `au_sol` images.
    "passant": {"vitesse": 1.0, "course_images": 8, "ecart": 8, "au_sol": 70},
    //: Le trafic sur ses rails : il demarre a `accel_min` au moins de son elan, et sa caisse chasse de
    //: `roulis` radian au plus quand il freine sur la glace.
    "trafic": {"accel_min": 0.35, "roulis": 0.04},
    //: Le dessin : la glace noire sur l'asphalte, la glace bleutee sur le trottoir, les reflets.
    "couleurs": {"noire": "rgba(24,36,54,0.46)", "coeur": "rgba(14,22,36,0.30)", "bleue": "rgba(150,192,228,0.55)",
                 "coeur_bleu": "rgba(214,236,252,0.45)", "reflet": "rgba(228,240,255,0.80)", "eclat": "rgba(255,255,255,0.95)"},
    //: La nuit : une plaque a moins de `portee` px d'un lampadaire, ou dans le faisceau d'un phare, luit.
    "nuit": {"portee": 70, "rayon": 16, "lueur": [200, 222, 248], "force": 0.42, "phare": 0.6},
    //: Les plaques peintes gardees en memoire (les plus vieilles s'oublient).
    "cache": 96,
  };

  let coupe = false;
  /** Pour les juges : couper la glace (l'hiver d'avant la vague 6b), puis la remettre. */
  function couper(oui) { coupe = !!oui; }
  function reglages() { return REGLAGES; }

  // --- Quand ---------------------------------------------------------------------------------

  /** Le genre de gel de ce jour-la : 'hiver' (tout le jour), 'degel' (le matin, et le soir si demain gele),
      ou null. Pure. */
  function gelDe(jour) {
    if (typeof Calendrier === 'undefined' || !Calendrier.donnees()) return null;
    if (Calendrier.saison(jour) === 'hiver') return 'hiver';
    return REGLAGES.degel.mois.indexOf(Calendrier.mois(jour)) >= 0 ? 'degel' : null;
  }

  /** La glace ce jour-la, a cette heure (0 a 1 de la journee) : 0 rien, 1 pleine. Pure, et CONTINUE : pas
      de saut a minuit (le matin d'avril tient de la nuit d'avant, le soir regele vers le lendemain). */
  function intensiteA(jour, heure) {
    const g = gelDe(jour);
    if (g === 'hiver') return 1;
    if (g !== 'degel') return 0;
    const d = REGLAGES.degel, h = heure * 24;
    if (h < d.fondu_h) {
      const matin = gelDe(jour - 1) ? 1 : 0;
      return h < d.gel_h ? matin : matin * (d.fondu_h - h) / (d.fondu_h - d.gel_h);
    }
    if (h < d.regel_h || !gelDe(jour + 1)) return 0;
    return (h - d.regel_h) / (24 - d.regel_h);
  }

  /** Dehors, dans la ville (pas dans une piece, ni au chalet du rang), la glace de maintenant. */
  function intensite() {
    const c = Monde.carte;
    if (coupe || !B.partie || !c || !c.laVille || B.interieur || B.bloc || Monde.aLAbri()) return 0;
    return intensiteA(B.partie.jour, B.partie.heure);
  }

  // --- Ou : les plaques, a l'empreinte de leur cellule ----------------------------------------

  //: Les plaques deja calculees, par cellule (null : pas de plaque) — pour UNE carte : la ville ne bouge pas.
  let plaques = new Map(), pont = null, pourCarte = null;
  function verifierCarte() {
    if (pourCarte !== Monde.carte) { pourCarte = Monde.carte; plaques = new Map(); pont = null; sprites.clear(); }
  }

  //: Une part de 0 a 1 de quelques bits d'une empreinte (des tranches DIFFERENTES : la lecon des bits faibles).
  function part(h, decalage) { return ((h >>> decalage) & 1023) / 1023; }

  function sensDeLaRue(tx, ty, trottoir) {
    // La ligne d'arret (`S`) n'a pas de fleche : le sens de qui s'y arrete (`Monde.sensArret`).
    const f = Monde.fleche(tx, ty) === 'S' ? Monde.sensArret(tx, ty) : Monde.fleche(tx, ty);
    if (f === '<' || f === '>') return 'h';
    if (f === '^' || f === 'v') return 'v';
    const pareil = trottoir ? Monde.estTrottoir : Monde.estRoute;
    const h = (pareil(tx - 1, ty) ? 1 : 0) + (pareil(tx + 1, ty) ? 1 : 0);
    const v = (pareil(tx, ty - 1) ? 1 : 0) + (pareil(tx, ty + 1) ? 1 : 0);
    return h >= v ? 'h' : 'v';
  }

  /** La plaque de la cellule (cx, cy), ou null. ⚠️ Lit la carte (les tuiles de la cellule), une fois. */
  function plaqueDe(cx, cy) {
    const cle = cx * 8192 + cy;
    if (plaques.has(cle)) return plaques.get(cle);
    const R = REGLAGES, c = Monde.carte, n = R.cellule;
    let p = null;
    const h = hash2(cx * 31 + 7, cy + R.sel);
    if (h % R.une_sur === 0 && cx >= 0 && cy >= 0) {
      const trottoir = ((h >>> 5) % R.trottoir_une_sur) === 0;
      const candidats = [], arrets = [];
      for (let ty = cy * n; ty < cy * n + n && ty < c.h; ty++) {
        for (let tx = cx * n; tx < cx * n + n && tx < c.w; tx++) {
          if (trottoir ? !Monde.estTrottoir(tx, ty) : !Monde.estChaussee(tx, ty)) continue;
          candidats.push([tx, ty]);
          if (!trottoir && Monde.fleche(tx, ty) === 'S') arrets.push([tx, ty]);
        }
      }
      if (candidats.length >= 3) {
        const t = arrets.length && ((h >>> 9) % R.arret_une_sur) === 0 ? arrets[(h >>> 12) % arrets.length]
                                                                      : candidats[(h >>> 12) % candidats.length];
        const sens = sensDeLaRue(t[0], t[1], trottoir);
        const long = R.long[0] + part(hash2(cx, cy * 3 + R.sel), 4) * (R.long[1] - R.long[0]);
        const large = R.large[0] + part(hash2(cx * 5 + 1, cy + R.sel), 14) * (R.large[1] - R.large[0]);
        const h2 = hash2(t[0] + R.sel, t[1] * 7);
        p = { x: t[0] * TT + 4 + (h2 % 9), y: t[1] * TT + 4 + ((h2 >>> 4) % 9),
              rx: sens === 'h' ? long : large, ry: sens === 'h' ? large : long,
              trottoir: trottoir, k1: part(h2, 8) * 6.28, k2: part(h2, 18) * 6.28, cle: 'c' + cle };
      }
    }
    plaques.set(cle, p);
    return p;
  }

  /** Les plaques du tablier du pont (`B.defs.carte.ponts`), une fois. */
  function plaquesDuPont() {
    if (pont) return pont;
    pont = [];
    const R = REGLAGES, liste = (B.defs && B.defs.carte && B.defs.carte.ponts) || [];
    for (const q of liste) {
      const vertical = q.sens === 'v', n = vertical ? q.h : q.l;
      for (let k = 1; k < n - 1; k += R.pont_pas) {
        const h = hash2(q.x * 13 + k, q.y + R.sel);
        const long = R.pont_long[0] + part(h, 3) * (R.pont_long[1] - R.pont_long[0]);
        const large = (vertical ? q.l : q.h) * TT / 2 + 4;
        const x = vertical ? (q.x + q.l / 2) * TT : (q.x + k + 0.5) * TT;
        const y = vertical ? (q.y + k + 0.5) * TT : (q.y + q.h / 2) * TT;
        pont.push({ x: x, y: y, rx: vertical ? large : long, ry: vertical ? long : large, trottoir: false,
                    k1: part(h, 11) * 6.28, k2: part(h, 21) * 6.28, cle: 'p' + q.x + ',' + q.y + ',' + k, pont: true });
      }
    }
    return pont;
  }

  /** Ce point (px) est-il dans la plaque `p` ? Le bord est irregulier (deux ondes a l'empreinte), et la plaque
      ne deborde pas de sa surface : l'asphalte pour une plaque de chaussee, le trottoir pour l'autre. */
  function dans(p, x, y) {
    const dx = (x - p.x) / p.rx, dy = (y - p.y) / p.ry, r2 = dx * dx + dy * dy;
    if (r2 > 1.5) return false;
    const a = Math.atan2(dy, dx), bord = 1 + 0.16 * Math.sin(3 * a + p.k1) + 0.08 * Math.sin(5 * a + p.k2);
    if (r2 >= bord * bord) return false;
    const tx = Math.floor(x / TT), ty = Math.floor(y / TT);
    return p.trottoir ? Monde.estTrottoir(tx, ty) : Monde.estRoute(tx, ty);
  }

  /** Les plaques qui peuvent toucher ce point (sa cellule et ses voisines, le pont). */
  function plaquesPres(x, y, rendre) {
    const n = REGLAGES.cellule * TT, cx = Math.floor(x / n), cy = Math.floor(y / n);
    for (let j = cy - 1; j <= cy + 1; j++) for (let i = cx - 1; i <= cx + 1; i++) {
      const p = plaqueDe(i, j);
      if (p && rendre(p)) return true;
    }
    for (const p of plaquesDuPont()) if (Math.abs(x - p.x) < p.rx * 1.3 && Math.abs(y - p.y) < p.ry * 1.3 && rendre(p)) return true;
    return false;
  }

  /** La glace sous ce point (px), maintenant : 0 (rien) a 1 (pleine). */
  function sous(x, y) {
    const i = intensite();
    if (!i) return 0;
    verifierCarte();
    return plaquesPres(x, y, function (p) { return dans(p, x, y); }) ? i : 0;
  }

  function melange(base, i) { return 1 - (1 - base) * i; }

  //: Ce que la glace ne touche pas : une COQUE, un char en plein saut, et la MOTONEIGE (ce qui est fait pour la
  //: neige, `hors_neige` sous 1) — sur ses skis, elle glisse comme avant (sa course des bois est reglee la-dessus,
  //: et le derapage de la vague 6a l'exempte deja).
  function exempt(v) { return !v || v.z > 0 || !!(v.def && (v.def.eau || v.def.hors_neige < 1)); }

  /** Ce que le sol tient sous ce char (1 hors de la glace). ⚠️ Une ADHERENCE, pas un facteur : `Vehicules`
      en prend le MINIMUM avec la neige et le verglas (une plaque sous la tempete ne glisse pas deux fois). */
  function adherence(v) {
    if (exempt(v)) return 1;
    const g = sous(v.x, v.y);
    return g ? melange(REGLAGES.adherence, g) : 1;
  }
  function frein(v) {
    if (exempt(v)) return 1;
    const g = sous(v.x, v.y);
    return g ? melange(REGLAGES.frein, g) : 1;
  }

  // --- Le trafic, sur ses rails -----------------------------------------------------------------

  /** Ce que la glace laisse au trafic sur ses rails : { accel, frein } (1 et 1 hors de la glace). ⚠️ Jamais
      pour la police en poursuite (elle ne glisse pas en pleine chasse), ni pour une coque — ni pour les AUTOBUS et
      les RAMES (`conducteur: 'ligne'`) : ils tiennent leur horaire (`Autobus`), et une rame roule sur l'acier (au
      banc, un autobus lent a demarrer laissait ses passagers a bord, une rame restait prise au coin). */
  function surRails(v) {
    if (v.poursuite || v.conducteur === 'ligne' || v.rails || exempt(v)) return null;
    const g = sous(v.x, v.y);
    if (!g) return null;
    return { accel: Math.max(REGLAGES.trafic.accel_min, melange(REGLAGES.adherence, g)), frein: melange(REGLAGES.frein, g), g: g };
  }

  /** La caisse qui chasse un peu quand il freine sur la glace : un roulis a l'empreinte du char et du temps,
      que la conduite sur rails reprend d'elle-meme (le cap y suit la route). */
  function roulis(v, g) {
    return Math.sin(((B.t || 0) + (v.id || 0) * 7) * 0.35) * REGLAGES.trafic.roulis * g;
  }

  // --- A pied ------------------------------------------------------------------------------------

  /** Le joueur a pied sur la glace : en courant, il garde une part de son elan (il glisse), et au bout de
      `course_images` images de course de suite, il tombe. Rend vrai s'il vient de tomber. */
  function glisserAPied(j, court, vxAvant, vyAvant) {
    const g = court ? sous(j.x, j.y) : 0;
    if (!g) { j.courseSurPlaque = 0; return false; }
    const R = REGLAGES.joueur, e = R.elan * g;
    j.vx = vxAvant * e + j.vx * (1 - e);
    j.vy = vyAvant * e + j.vy * (1 - e);
    j.courseSurPlaque = (j.courseSurPlaque || 0) + 1;
    const S = B.defs.saisons && B.defs.saisons.joueur;
    const bottes = !!(S && j.tenue && S.chaleur[j.tenue.souliers] > 0);
    if (j.courseSurPlaque < (bottes ? R.bottes : R.course_images)) return false;
    j.courseSurPlaque = 0;
    j.auSol = R.au_sol; j.face = 'couche'; j.vx = 0; j.vy = 0;
    if (typeof Son !== 'undefined' && Son.SFX && Son.SFX.chute) Son.SFX.chute();
    return true;
  }

  /** Un passant qui court sur la glace (il se sauve, il a vu quelque chose) tombe au bout de quelques images
      — a l'empreinte de son numero. Rend vrai s'il vient de tomber. ⚠️ Jamais celui d'une mission, ni un agent,
      ni un figurant qui tient son poste : seulement le passant ordinaire qui se sauve. */
  function faitTomber(e) {
    if (e.etat !== 'fuit' && e.etat !== 'temoin') { e.courseSurPlaque = 0; return false; }
    if (e.agent || e.mission || e.important || e.donneur || e.suit || e.metier === 'cycliste') return false;
    const R = REGLAGES.passant;
    if (Math.hypot(e.vx || 0, e.vy || 0) < R.vitesse || !sous(e.x, e.y)) { e.courseSurPlaque = 0; return false; }
    e.courseSurPlaque = (e.courseSurPlaque || 0) + 1;
    if (e.courseSurPlaque < R.course_images + ((e.id || 0) % R.ecart)) return false;
    e.courseSurPlaque = 0;
    e.chuteGlace = R.au_sol; e.face = 'couche'; e.vx = 0; e.vy = 0;
    return true;
  }

  /** Une image d'un passant tombe : il reste couche, puis se releve (et reprend ce qu'il faisait). Rend vrai
      tant qu'il est a terre. */
  function aTerre(e) {
    if (!(e.chuteGlace > 0)) return false;
    // ⚠️ Assomme, projete ou mort pendant sa chute : c'est l'autre etat qui le tient (et qui le relevera) — la glace
    // lache, sans le remettre debout (la relecture : un K.-O. se redessinait debout).
    if (!e.vivant || e.etat === 'assomme' || e.auSol > 0 || e.vol) { e.chuteGlace = 0; return false; }
    e.vx = 0; e.vy = 0;
    if (--e.chuteGlace <= 0) e.face = 'bas';
    return true;
  }

  // --- Ce qu'on voit -----------------------------------------------------------------------------

  //: Les plaques peintes (un canevas par plaque), les plus vieilles oubliees au-dela de `cache`.
  const sprites = new Map();
  if (typeof Base !== 'undefined' && Base.apresPerte) Base.apresPerte(function () { sprites.clear(); });

  function peindre(p) {
    const C = REGLAGES.couleurs, mx = Math.ceil(p.rx * 1.3) + 1, my = Math.ceil(p.ry * 1.3) + 1;
    const w = mx * 2, h = my * 2, x0 = Math.floor(p.x) - mx, y0 = Math.floor(p.y) - my;
    const cv = Base.nouveauCanvas(w, h), ctx = cv.getContext('2d');
    // Par tranches d'une rangee de pixels : la plaque, puis son coeur (plus sombre sur l'asphalte, plus clair
    // sur le trottoir) — un bord qui se lit, un dedans qui a de l'epaisseur.
    const passe = function (couleur, echelle) {
      ctx.fillStyle = couleur;
      const q = { x: p.x, y: p.y, rx: p.rx * echelle, ry: p.ry * echelle, trottoir: p.trottoir, k1: p.k1, k2: p.k2 };
      for (let y = 0; y < h; y++) {
        let debut = -1;
        for (let x = 0; x <= w; x++) {
          const ok = x < w && dans(q, x0 + x + 0.5, y0 + y + 0.5);
          if (ok && debut < 0) debut = x;
          if (!ok && debut >= 0) { ctx.fillRect(debut, y, x - debut, 1); debut = -1; }
        }
      }
    };
    passe(p.trottoir ? C.bleue : C.noire, 1);
    passe(p.trottoir ? C.coeur_bleu : C.coeur, 0.62);
    // Les reflets : deux ou trois traits en biais, dans la plaque seulement — sur la plaque, et seuls sur un
    // second canevas (la nuit, `dessinerReflets` les repasse PAR-DESSUS le voile).
    const rf = Base.nouveauCanvas(w, h), rctx = rf.getContext('2d');
    ctx.fillStyle = C.reflet; rctx.fillStyle = C.reflet;
    const traits = 2 + (Math.floor(p.k1 * 10) % 2);
    for (let k = 0; k < traits; k++) {
      const ox = p.x + (k - 1) * p.rx * 0.38 + Math.cos(p.k2 + k) * p.rx * 0.12, oy = p.y + Math.sin(p.k1 + k) * p.ry * 0.25;
      const l = Math.max(3, Math.round(Math.min(p.rx, p.ry) * 0.7));
      for (let s = 0; s < l; s++) {
        const x = ox + s * 0.8 - l * 0.4, y = oy - s * 0.5 + l * 0.25;
        if (!dans(p, x, y)) continue;
        ctx.fillRect(Math.floor(x) - x0, Math.floor(y) - y0, 2, 1);
        rctx.fillRect(Math.floor(x) - x0, Math.floor(y) - y0, 2, 1);
      }
    }
    return { cv: cv, rf: rf, x0: x0, y0: y0 };
  }

  function sprite(p) {
    let s = sprites.get(p.cle);
    if (s) { sprites.delete(p.cle); sprites.set(p.cle, s); return s; }
    s = peindre(p);
    sprites.set(p.cle, s);
    if (sprites.size > REGLAGES.cache) sprites.delete(sprites.keys().next().value);
    return s;
  }

  /** Les plaques a l'ecran (celles dont la boite touche la vue). */
  function plaquesVisibles(vue) {
    const n = REGLAGES.cellule * TT, out = [];
    const cx0 = Math.floor((vue.x - 48) / n), cy0 = Math.floor((vue.y - 48) / n);
    const cx1 = Math.floor((vue.x + VW + 48) / n), cy1 = Math.floor((vue.y + VH + 48) / n);
    const voit = function (p) { return p.x + p.rx * 1.3 > vue.x && p.x - p.rx * 1.3 < vue.x + VW && p.y + p.ry * 1.3 > vue.y && p.y - p.ry * 1.3 < vue.y + VH; };
    for (let j = cy0; j <= cy1; j++) for (let i = cx0; i <= cx1; i++) { const p = plaqueDe(i, j); if (p && voit(p)) out.push(p); }
    for (const p of plaquesDuPont()) if (voit(p)) out.push(p);
    return out;
  }

  /** La glace au sol, SOUS la neige (une tempete la cache) et les traces. Un eclat de soleil qui saute d'une
      plaque a l'autre (a l'empreinte de l'image) — jamais un de. */
  function dessinerSol(ctx, vue) {
    const i = intensite();
    if (!i) return;
    verifierCarte();
    const visibles = plaquesVisibles(vue);
    if (!visibles.length) return;
    const a = ctx.globalAlpha, battement = Math.floor((B.image || B.t || 0) / 9);
    ctx.globalAlpha = a * i;
    for (const p of visibles) {
      const s = sprite(p);
      ctx.drawImage(s.cv, Math.round(s.x0 - vue.x), Math.round(s.y0 - vue.y));
    }
    ctx.globalAlpha = a;
    // Un eclat : une plaque sur trois a un battement donne, sur un point de son coeur.
    ctx.fillStyle = REGLAGES.couleurs.eclat;
    let n = 0;
    for (const p of visibles) {
      const h = hash2(Math.floor(p.x) + battement, Math.floor(p.y));
      if (h % 3) continue;
      const x = Math.round(p.x + ((h >>> 4) % 9 - 4) * p.rx / 8 - vue.x), y = Math.round(p.y + ((h >>> 9) % 5 - 2) * p.ry / 6 - vue.y);
      ctx.fillRect(x - 1, y, 3, 1); ctx.fillRect(x, y - 1, 1, 3);
      n += 2;
    }
    B.stats.images = (B.stats.images || 0) + visibles.length;
    B.stats.rects += n;
  }

  //: Les plaques qui luisent a cette image (sous un lampadaire, dans un phare) : `dessinerReflets` les reprend.
  let luisent = [], luisentImage = -1;

  /** La nuit, la glace RENVOIE la lumiere : une plaque pres d'un lampadaire (`Monde.lampesVisibles`), ou dans le
      faisceau d'un phare (les cones de `deja`, les lampes deja ramassees), ajoute une lueur froide a la liste des
      lampes de `Base.fin`. ⚠️ Pas les feux de circulation ni les feux arriere : une lueur blanche sous un feu rouge
      mentait (la relecture). */
  function lampes(vue, deja) {
    luisent = []; luisentImage = B.image;
    const i = intensite();
    if (!i || Monde.ambianceVue().alpha < 0.2) return [];
    verifierCarte();
    const N = REGLAGES.nuit, out = [], visibles = plaquesVisibles(vue);
    if (!visibles.length) return [];
    const phares = deja.filter(function (l) { return l.cone && l.ox !== undefined; }), rue = Monde.lampesVisibles(vue);
    for (const p of visibles) {
      const px = p.x - vue.x, py = p.y - vue.y;
      let force = 0;
      for (const l of phares) {
        // Le faisceau d'un phare : la plaque devant lui, dans sa portee et son cone.
        const dx = p.x - l.ox, dy = p.y - l.oy, avant = dx * l.ca + dy * l.sa, cote = Math.abs(-dx * l.sa + dy * l.ca);
        if (avant > 0 && avant < l.r && cote < (l.cone[0] + (l.cone[1] - l.cone[0]) * avant / l.r) + p.rx * 0.5) force = Math.max(force, N.phare);
      }
      for (const l of rue) {
        const d = Math.hypot(l.x - px, l.y - py);
        if (d < N.portee) force = Math.max(force, N.force * (1 - d / N.portee) + 0.12);
      }
      if (!force) continue;
      luisent.push({ p: p, f: force });
      out.push({ x: px, y: py, r: N.rayon + Math.min(p.rx, p.ry) * 0.5, c: 'rgba(' + N.lueur.join(',') + ',' + (force * i).toFixed(3) + ')' });
    }
    return out;
  }

  /** PAR-DESSUS la nuit : les reflets d'une plaque qui luit se voient (peints dessous, le voile les eteignait). */
  function dessinerReflets(ctx, vue) {
    if (luisentImage !== B.image || !luisent.length) return;
    const i = intensite(), battement = Math.floor((B.image || 0) / 7);
    if (!i) return;
    ctx.fillStyle = REGLAGES.couleurs.reflet;
    for (const q of luisent) {
      const p = q.p, a = ctx.globalAlpha, s = sprite(p);
      // Les traits du reflet, puis un eclat qui saute d'un point a l'autre (a l'empreinte de l'image).
      ctx.globalAlpha = a * Math.min(1, q.f * 1.3) * i;
      ctx.drawImage(s.rf, Math.round(s.x0 - vue.x), Math.round(s.y0 - vue.y));
      const h = hash2(Math.floor(p.x) + battement, Math.floor(p.y) * 3);
      const x = Math.round(p.x + ((h >>> 3) % 9 - 4) * p.rx / 8 - vue.x), y = Math.round(p.y + ((h >>> 8) % 5 - 2) * p.ry / 6 - vue.y);
      ctx.fillRect(x - 2, y, 5, 1); ctx.fillRect(x, y - 2, 1, 5);
      ctx.globalAlpha = a;
    }
  }

  function oublier() { plaques = new Map(); pont = null; pourCarte = null; sprites.clear(); luisent = []; }

  return { reglages, couper, gelDe, intensiteA, intensite, plaqueDe, plaquesDuPont, plaquesVisibles, dans, sous,
           adherence, frein, surRails, roulis, glisserAPied, faitTomber, aTerre, dessinerSol, lampes, dessinerReflets, oublier };
})();
