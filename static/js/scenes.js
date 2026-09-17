/* Bandini — le metteur en scène.

   Décision du 16 sept. 2026 (« Les missions mises en scène », docs/plan.md) : une
   scène est une LISTE DE PLANS écrite dans `missions.py` (`TYPES_PLANS`), et ce
   script les joue sans connaître aucune scène par son nom. Si une scène ne
   s'écrit pas avec les types d'ici, on ajoute UN TYPE — jamais un
   `if (slug === 'q07')`.

   Les plans se jouent l'un après l'autre ; `ensemble` fait partir le suivant avec
   lui, `fond` le laisse jouer sans retenir la scène.

   ⚠️ Les règles que l'ouverture a payées, et qui valent pour toutes :
   - AUCUN DÉ. Une partie jouée en regardant les scènes est exactement celle qu'on
     joue en les passant : même tuile, même monde, même prochain dé. Les couleurs
     se donnent en clair, les bouffées de fumée ont des angles fixes.
   - LA VILLE EST FIGÉE pendant qu'elle joue (`Jeu.maj` ne fait tourner qu'elle).
   - ON LA PASSE (PAUSE ou FRAPPE) et l'on tombe exactement où elle nous aurait
     laissés : il n'y a qu'UNE façon de finir (`finir`), et elle achève ce que les
     plans pas encore joués auraient laissé derrière eux.
   - ELLE SE TERMINE TOUJOURS : un plan dont le lieu ou l'acteur ne se trouve pas
     est sauté, jamais attendu.
   - ELLE NE DÉPLACE PAS LE JOUEUR : la caméra voyage, le bonhomme peut marcher,
     mais il revient à la dernière image là où il était à la première.
   - COURTE : elle finit quand ses plans ET ses répliques sont finis, et ne tient
     pas plus de trois secondes après son dernier mot une fois tous ses plans
     partis. */

const Scenes = (function () {
  'use strict';

  //: Trois secondes, en images : ce qu'une scène peut encore durer après son
  //: dernier mot, quand tous ses plans sont partis.
  const APRES_LE_DERNIER_MOT = 180;
  //: Un geste sans durée se tient une seconde.
  const GESTE_IMAGES = 60;
  //: Entrer : les quelques pas jusqu'à la porte.
  const ENTRER_IMAGES = 40;

  const ANGLES = { '>': 0, '<': Math.PI, '^': -Math.PI / 2, 'v': Math.PI / 2 };

  function courbe(nom, u) {
    if (nom === 'freine') return 1 - Math.pow(1 - u, 3);
    if (nom === 'accelere') return u * u;
    return u;
  }

  // --- Qui, et où ----------------------------------------------------------------------------

  /** Un acteur : le joueur, ce que la scène a créé (`car`), le donneur de la
      mission, ou un personnage de l'histoire par son slug. */
  function acteur(s, nom) {
    if (!nom) return null;
    if (nom === 'joueur') return B.joueur || null;
    if (s.acteurs[nom]) return s.acteurs[nom];
    if (nom === 'donneur') return s.mission ? Histoire.donneur(s.mission.donneur) : null;
    return Histoire.donneur(nom);
  }

  /** Un lieu : un nom que la scène a reçu, un acteur (sa position), ou tout ce
      que `Histoire.resoudre` connaît. `null` si rien ne répond : le plan saute. */
  function lieu(s, nom, recul) {
    if (!nom) return null;
    let l = s.lieux[nom] || null;
    if (!l) { const a = acteur(s, nom); if (a) l = { x: a.x, y: a.y }; }
    if (!l && (nom !== 'donneur' || s.mission)) l = Histoire.resoudre(nom, s.mission);
    if (!l) return null;
    if (recul && l.sens !== undefined && ANGLES[l.sens] !== undefined) {
      const a = ANGLES[l.sens];
      return { x: l.x - Math.cos(a) * recul, y: l.y - Math.sin(a) * recul, sens: l.sens };
    }
    return l;
  }

  function viser(s, x, y) {
    s.vise = { x: x, y: y };
    Monde.centrerCamera(x, y);
  }

  // --- Jouer une scène ------------------------------------------------------------------------

  /** Lance `scene` (une liste de plans). `contexte` : `lieux` (nom -> {x, y, sens}),
      `lignes` (les répliques que `dire` peut dire), `anonyme` (pas de nom au-dessus
      de la boîte), `voix` (le paquet de voix à charger), `mission`, `fin` (appelée
      une fois, à la dernière image ou quand on passe). Rend l'état, ou `null`. */
  function jouer(scene, contexte) {
    const j = B.joueur, c = contexte || {};
    if (!j || B.scene || !scene || !scene.length) return null;
    const s = {
      plans: scene, i: 0, t: 0, actifs: [], bloquant: null, cree: [], touches: [],
      lieux: Object.assign({}, c.lieux || {}), acteurs: {}, mission: c.mission || null,
      lignes: c.lignes || [], anonyme: !!c.anonyme,
      retour: { x: j.x, y: j.y }, musique: null, boucles: [], moteur: false,
      noir: 0, titre: 0, carton: null, camera: null,
      vise: { x: B.cam.x + VW / 2, y: B.cam.y + VH / 2 },
      silence: -1, fin: c.fin || null,
    };
    B.scene = s;
    j.vx = 0; j.vy = 0;
    // ⚠️ Qui SORT n'était pas là avant : un acteur dont le premier plan est
    // `sortir` est caché dès la première image (le bonhomme est dans le car).
    const vus = {};
    for (const plan of scene) {
      if (!plan.acteur || vus[plan.acteur]) continue;
      vus[plan.acteur] = true;
      if (plan.type !== 'sortir') continue;
      const a = acteur(s, plan.acteur);
      if (a) { a.dessine = false; toucher(s, a); }
    }
    if (c.voix) Son.Voix.chargerHistoire(c.voix);
    Entree.contexte('dialogue');
    demarrerLesSuivants(s);
    return s;
  }

  function toucher(s, e) { if (s.touches.indexOf(e) < 0) s.touches.push(e); }

  /** Les plans suivants partent : tant qu'ils sont instantanés ou `ensemble`,
      le suivant part avec eux ; le premier qui dure et retient s'arrête là. */
  function demarrerLesSuivants(s) {
    while (B.scene === s && s.i < s.plans.length && !s.bloquant) {
      const plan = s.plans[s.i++];
      const a = { plan: plan, debut: s.t, fini: false };
      s.actifs.push(a);
      demarrer(s, a);
      if (!a.fini && !plan.ensemble) s.bloquant = a;
    }
  }

  function demarrer(s, a) {
    const p = a.plan, genre = PLANS[p.type];
    if (!genre) { a.fini = true; return; }
    if (genre.demarrer(s, a, p) === false) a.fini = true;
  }

  /** Une image de la scène. La ville est figée : ici bougent les acteurs, la
      caméra, le noir, le titre — et la réplique en cours. */
  function maj() {
    const s = B.scene;
    if (!s) return;
    s.t++;
    for (const a of s.actifs.slice()) {
      if (a.fini) continue;
      const genre = PLANS[a.plan.type];
      if (genre.maj && genre.maj(s, a, a.plan, s.t - a.debut) === false) a.fini = true;
      if (B.scene !== s) return;
    }
    if (s.bloquant && s.bloquant.fini) { s.bloquant = null; demarrerLesSuivants(s); }
    if (s.camera) {
      const l = lieu(s, s.camera.vers, s.camera.recul);
      if (l) viser(s, s.vise.x + (l.x - s.vise.x) * s.camera.lissage, s.vise.y + (l.y - s.vise.y) * s.camera.lissage);
    }
    // La réplique avance, et elle SEULE : `Histoire.maj` enchaînerait sur le
    // téléphone et les objectifs au milieu de la scène.
    Histoire.majCinema();
    if (B.scene !== s) return;
    const partis = s.i >= s.plans.length;
    const retenue = s.actifs.some(function (a) { return !a.fini && !a.plan.fond; });
    const parle = !!B.cinema;
    if (partis && !parle) {
      if (s.silence < 0) s.silence = s.t;
      if (!retenue || s.t - s.silence >= APRES_LE_DERNIER_MOT) finir(s);
    }
  }

  /** PASSER : on saute tout, et l'on tombe exactement où la scène nous aurait
      laissés. */
  function passer() {
    if (!B.scene) return false;
    finir(B.scene);
    return true;
  }

  /** LA SEULE FAÇON DE FINIR, jouée jusqu'au bout ou passée. */
  function finir(s) {
    // Ce que les plans pas encore finis auraient laissé derrière eux, dans
    // l'ordre : une scène passée au premier plan doit laisser la ville comme
    // une scène vue jusqu'au dernier.
    for (const plan of s.plans) {
      const a = s.actifs.find(function (x) { return x.plan === plan; });
      if (a && a.fini) continue;
      const genre = PLANS[plan.type];
      if (genre && genre.achever) genre.achever(s, plan);
    }
    B.scene = null;
    Son.Voix.couper();
    B.cinema = null; B.dialogue = null;
    // ⚠️ Ce que la scène a fait naître quitte la ville avec elle : un autobus
    // garé devant le terminus jusqu'à la fin des temps serait un char de plus à
    // voler, né au premier geste de la partie.
    for (const e of s.cree) if (B.entites.indexOf(e) >= 0) Entites.retirer(e);
    if (s.moteur) Son.boucle('moteur', false);
    s.boucles.forEach(function (slug) { Son.boucle(slug, false); });
    for (const e of s.touches) e.geste = null;
    const j = B.joueur;
    if (j) {
      j.geste = null;
      j.dessine = true; j.x = s.retour.x; j.y = s.retour.y; j.vx = 0; j.vy = 0;
      Entites.dansLaCarte(j);
      Monde.centrerCamera(j.x, j.y);
    }
    Entree.contexte(j && j.dansVehicule ? 'vehicule' : 'pied');
    if (s.musique) { Son.Mus.arreter(); Son.Chef.maj(); }          // la ville reprend la main
    if (s.fin) s.fin(s);
  }

  // --- Les plans ------------------------------------------------------------------------------
  //
  // Chaque type : `demarrer(s, a, plan)` (rend `false` s'il est déjà fini — un
  // plan instantané, ou un plan qui ne trouve pas son lieu), `maj(s, a, plan, t)`
  // (t = 1 à la première image ; rend `false` quand il a fini) et, s'il laisse
  // quelque chose derrière lui, `achever(s, plan)` pour qui le passe.

  /** Les quelques pas d'un acteur, en ligne droite. Le monde est figé : c'est ici
      qu'on avance ses jambes, sinon il glisserait sans marcher. */
  function pas(e, x, y) {
    const dx = x - e.x, dy = y - e.y;
    e.x = x; e.y = y;
    e.vx = dx; e.vy = dy;
    if (e.anim) e.anim.dist += Math.abs(dx) + Math.abs(dy);
    if (Math.abs(dx) + Math.abs(dy) > 0.05) {
      e.face = Math.abs(dx) >= Math.abs(dy) ? (dx > 0 ? 'droite' : 'gauche') : (dy > 0 ? 'bas' : 'haut');
    } else { e.vx = 0; e.vy = 0; }
    Entites.dansLaCarte(e);
  }

  /** Le pot d'échappement. ⚠️ Des angles FIXES : `Entites.poussiere` tire des dés. */
  function fumee(v, n) {
    const ax = -Math.cos(v.angle), ay = -Math.sin(v.angle);
    for (let i = 0; i < n; i++) {
      const e = (i / n - 0.5) * 0.9;
      Entites.particule(v.x + ax * (v.def.longueur / 2), v.y + ay * (v.def.longueur / 2),
                        ax * 0.5 + e * 0.3, ay * 0.5 + e * 0.3, 18, '#9a958c', 1, 0.02);
    }
  }

  function poserLeChar(v, x, y) {
    v.x = x; v.y = y;
    // ⚠️ À L'ARRÊT AU SENS DE LA PHYSIQUE, toujours : la scène POSE le char, elle
    // ne le conduit pas. Une vitesse ici et il continuerait tout seul l'image où
    // la ville se remet à tourner — au milieu de la rue, sans conducteur.
    v.vx = 0; v.vy = 0; v.vitesse = 0;
  }

  const PLANS = {
    camera: {
      demarrer: function (s, a, p) {
        const l = lieu(s, p.vers, p.recul);
        if (!l) return false;
        if (p.lissage) { s.camera = { vers: p.vers, recul: p.recul || 0, lissage: p.lissage }; return false; }
        s.camera = null;
        if (!p.duree) { viser(s, l.x, l.y); return false; }
        a.de = { x: s.vise.x, y: s.vise.y }; a.a = l;
        return true;
      },
      maj: function (s, a, p, t) {
        const k = courbe(p.courbe, Math.min(1, t / p.duree));
        viser(s, a.de.x + (a.a.x - a.de.x) * k, a.de.y + (a.a.y - a.de.y) * k);
        return t < p.duree;
      },
    },

    marcher: {
      demarrer: function (s, a, p) {
        const e = acteur(s, p.acteur), l = lieu(s, p.vers);
        if (!e || !l) return false;
        toucher(s, e);
        a.e = e; a.de = { x: e.x, y: e.y }; a.a = l;
        if (!p.duree) { pas(e, l.x, l.y); e.vx = 0; e.vy = 0; return false; }
        return true;
      },
      maj: function (s, a, p, t) {
        const u = Math.min(1, t / p.duree);
        pas(a.e, a.de.x + (a.a.x - a.de.x) * u, a.de.y + (a.a.y - a.de.y) * u);
        if (u >= 1) { a.e.vx = 0; a.e.vy = 0; return false; }
        return true;
      },
      // Passé : il est arrivé. (Le joueur, lui, revient de toute façon chez lui.)
      achever: function (s, p) {
        const e = acteur(s, p.acteur), l = lieu(s, p.vers);
        if (e && l && e !== B.joueur) { e.x = l.x; e.y = l.y; e.vx = 0; e.vy = 0; }
      },
    },

    conduire: {
      demarrer: function (s, a, p) {
        let v = acteur(s, p.acteur);
        if (p.vers) {
          const l = lieu(s, p.vers);
          if (!l) return false;
          const angle = ANGLES[l.sens] !== undefined ? ANGLES[l.sens] : (v ? v.angle : 0);
          const dx = Math.cos(angle), dy = Math.sin(angle), recul = p.depuis || 0;
          if (!v && p.vehicule) {
            const def = Vehicules.vehiculeDef(p.vehicule);
            if (!def) return false;
            // ⚠️ La couleur EN CLAIR : `Vehicules.creer` en tire une du
            // catalogue sinon, et un dé tiré ici décale tous ceux qui suivent.
            v = Vehicules.creer(p.vehicule, l.x - dx * recul, l.y - dy * recul, angle,
                                { couleur: p.couleur || def.couleurs[0], etat: 'stationne' });
            if (!v) return false;
            s.acteurs[p.acteur] = v; s.cree.push(v);
            if (v.def.classe !== 'velo') { Son.boucle('moteur', true); s.moteur = true; }
          }
          if (!v) return false;
          a.v = v; a.de = { x: v.x, y: v.y }; a.a = { x: l.x, y: l.y }; v.angle = angle;
        } else {
          if (!v || B.entites.indexOf(v) < 0) return false;
          const dx = Math.cos(v.angle), dy = Math.sin(v.angle);
          a.v = v; a.de = { x: v.x, y: v.y }; a.a = { x: v.x + dx * (p.part || 0), y: v.y + dy * (p.part || 0) };
        }
        if (!p.duree) { poserLeChar(a.v, a.a.x, a.a.y); return this.arrive(s, a, p, true); }
        poserLeChar(a.v, a.de.x, a.de.y);
        return true;
      },
      maj: function (s, a, p, t) {
        const v = a.v;
        if (t === 1 && p.part !== undefined) {            // il repart : la portière, puis le pot
          if (p.portiere) Son.SFX.porte_vehicule();
          if (p.fumee) fumee(v, p.fumee);
        }
        const k = courbe(p.courbe, Math.min(1, t / p.duree));
        poserLeChar(v, a.de.x + (a.a.x - a.de.x) * k, a.de.y + (a.a.y - a.de.y) * k);
        if (t < p.duree) return true;
        return this.arrive(s, a, p, false);
      },
      arrive: function (s, a, p, instant) {
        if (p.vers && !instant) {                          // il arrive : la portière, et le pot
          if (p.portiere) Son.SFX.porte_vehicule();
          if (p.fumee) fumee(a.v, p.fumee);
        }
        if (p.retirer) {
          Entites.retirer(a.v);
          if (s.moteur) { Son.boucle('moteur', false); s.moteur = false; }
        }
        return false;
      },
    },

    geste: {
      demarrer: function (s, a, p) {
        const e = acteur(s, p.acteur);
        if (!e) return false;
        toucher(s, e);
        const l = p.vers ? lieu(s, p.vers) : null;
        if (l) {
          const dx = l.x - e.x, dy = l.y - e.y;
          if (Math.abs(dx) + Math.abs(dy) > 1) e.face = Math.abs(dx) >= Math.abs(dy) ? (dx > 0 ? 'droite' : 'gauche') : (dy > 0 ? 'bas' : 'haut');
        }
        e.geste = p.geste; e.vx = 0; e.vy = 0;
        a.e = e;
        return true;
      },
      maj: function (s, a, p, t) {
        if (t < (p.duree || GESTE_IMAGES)) return true;
        a.e.geste = null;
        return false;
      },
    },

    entrer: {
      demarrer: function (s, a, p) {
        const e = acteur(s, p.acteur), l = lieu(s, p.dans);
        if (!e || !l) return false;
        toucher(s, e);
        a.e = e; a.de = { x: e.x, y: e.y }; a.a = l;
        return true;
      },
      maj: function (s, a, p, t) {
        const duree = p.duree || ENTRER_IMAGES, u = Math.min(1, t / duree);
        pas(a.e, a.de.x + (a.a.x - a.de.x) * u, a.de.y + (a.a.y - a.de.y) * u);
        if (u < 1) return true;
        this.achever(s, p, a.e);
        return false;
      },
      // ⚠️ Passé la porte, un personnage QUITTE la ville (Ti-Guy rentre au
      // terminus, il n'y attend plus personne) ; le joueur, lui, est seulement
      // caché — il revient de toute façon chez lui à la dernière image.
      achever: function (s, p, deja) {
        const e = deja || acteur(s, p.acteur);
        if (!e) return;
        if (e === B.joueur) { e.dessine = false; return; }
        e.vx = 0; e.vy = 0;
        if (B.entites.indexOf(e) >= 0) Entites.retirer(e);
      },
    },

    sortir: {
      demarrer: function (s, a, p) {
        const e = acteur(s, p.acteur), de = acteur(s, p.de) || lieu(s, p.de);
        if (!e || !de) return false;
        toucher(s, e);
        if (de.type === 'vehicule') {
          // ⚠️ DU BON CÔTÉ DU CHAR, et ce n'est pas toujours le même : la rue peut
          // courir dans les quatre sens. On sort du côté OÙ L'ON VA (le trottoir) :
          // un bonhomme qui descend dans la voie d'en face traverserait la rue à
          // pied pendant que son char repart.
          const dx = Math.cos(de.angle), dy = Math.sin(de.angle), px = dy, py = -dx;
          const ou = lieu(s, p.vers) || { x: e.x, y: e.y };
          const cote = ((ou.x - de.x) * px + (ou.y - de.y) * py) >= 0 ? 1 : -1;
          e.x = de.x - dx * 6 + px * 12 * cote;
          e.y = de.y - dy * 6 + py * 12 * cote;
        } else {
          e.x = de.x; e.y = de.y;
          const ou = lieu(s, p.vers);
          if (ou && Math.abs(ou.x - e.x) + Math.abs(ou.y - e.y) > 1) {
            e.face = Math.abs(ou.x - e.x) >= Math.abs(ou.y - e.y) ? (ou.x > e.x ? 'droite' : 'gauche') : (ou.y > e.y ? 'bas' : 'haut');
          }
        }
        e.dessine = true; e.vx = 0; e.vy = 0;
        Son.SFX.pas();
        return false;
      },
      achever: function (s, p) {
        const e = acteur(s, p.acteur);
        if (e) e.dessine = true;
      },
    },

    coupe: {
      demarrer: function (s, a, p) {
        a.retourne = p.vers !== undefined && p.tient !== undefined;
        a.ailleurs = p.vers ? lieu(s, p.vers) : null;
        if (p.vers && !a.ailleurs) return false;
        // Sans `ferme`, on part DU noir : c'est l'ouverture, qui sort de l'écran titre.
        if (!p.ferme) { s.noir = 1; this.sauter(s, a); }
        return true;
      },
      /** Le noir est plein : la caméra saute là-bas. */
      sauter: function (s, a) {
        if (a.saute) return;
        a.saute = true;
        if (a.ailleurs) { a.depuis = { x: s.vise.x, y: s.vise.y }; viser(s, a.ailleurs.x, a.ailleurs.y); }
      },
      maj: function (s, a, p, t) {
        const f = p.ferme || 0, o = p.ouvre || 0;
        const A = f, Bo = A + o, C = Bo + (p.tient || 0), D = C + f, E = D + o;
        if (t >= A) this.sauter(s, a);
        // Et revient, le noir plein une seconde fois.
        if (a.retourne && !a.revenu && t >= D && t > C) { a.revenu = true; viser(s, a.depuis.x, a.depuis.y); }
        s.noir = t < A ? t / A
               : t < Bo ? 1 - (t - A) / o
               : (!a.retourne || t <= C) ? 0
               : t < D ? (t - C) / f
               : t < E ? 1 - (t - D) / o
               : 0;
        return a.retourne ? t < E : t < Bo;
      },
    },

    dire: {
      demarrer: function (s, a, p) {
        const choix = p.repliques || null;
        const lignes = s.lignes.filter(function (l, i) { return !choix || choix.indexOf(i + 1) >= 0; });
        if (!lignes.length) return false;
        Histoire.direLignes(lignes, { anonyme: s.anonyme, fin: function () { a.fini = true; } });
        return !a.fini;
      },
    },

    titre: {
      demarrer: function (s, a, p) {
        s.carton = { logo: !!p.logo, texte: p.texte || '', sous: p.sous || '' };
        s.titre = 0;
        return true;
      },
      // ⚠️ LE TITRE MONTE, TIENT, PUIS S'EN VA : laissé allumé jusqu'au bout,
      // il tiendrait quinze secondes sur un écran fixe.
      maj: function (s, a, p, t) {
        const monte = p.monte || 1, tenu = p.tenu || 0, descend = p.descend || 1;
        s.titre = t <= monte ? t / monte : t <= monte + tenu ? 1 : Math.max(0, 1 - (t - monte - tenu) / descend);
        if (t < monte + tenu + descend) return true;
        s.titre = 0;
        return false;
      },
    },

    son: {
      demarrer: function (s, a, p) {
        if (p.sfx && Son.SFX[p.sfx]) Son.SFX[p.sfx]();
        if (p.musique) { Son.Mus.jouer(p.musique); s.musique = p.musique; }
        if (p.boucle) { Son.boucle(p.boucle, true); s.boucles.push(p.boucle); }
        return false;
      },
    },

    attendre: {
      demarrer: function (s, a, p) { return (p.duree || 0) > 0; },
      maj: function (s, a, p, t) { return t < p.duree; },
    },
  };

  return { jouer, maj, passer, APRES_LE_DERNIER_MOT, TYPES: Object.keys(PLANS) };
})();
