/* Bandini — l'histoire : les donneurs, les missions, les defis, les voix.

   Tout le texte vient de `missions.py` (le paquet `B.defs.missions`) : ici on
   ne fait que le JOUER. Une mission = une suite d'objectifs types ; a chaque
   image, `maj()` regarde si l'objectif courant est atteint, et passe au
   suivant. Les repliques s'affichent dans la boite de dialogue ET se disent
   a voix haute (`Son.Voix.parler`), une par personnage ; pendant qu'un
   personnage parle, le joueur ecoute (il ne bouge pas), la radio baisse.

   Le telephone : quand une mission devient possible, son donneur appelle
   quelques secondes plus tard — la voix vient du combine. */

const Histoire = (function () {
  'use strict';

  const DELAI_APPEL = 600;          // images entre la fin d'une mission et l'appel de la suivante
  const RAYON_PARLER = 22;          // a cette distance d'un personnage, ACTION = lui parler

  function defs() { return B.defs.missions || []; }
  // --- Le carnet : ce qui s'ecrit tout seul -------------------------------------

  /*: Le plafond du journal. ⚠️ Une partie de cent jours accumule des dizaines
    d'entrees, et la partie voyagera par le reseau en M14. On jette donc les
    plus vieilles — mais les JALONS en dernier : on veut pouvoir relire quand
    on a rencontre Marco trois heures plus tot, pas ce qu'on a mange. */
  const CARNET_MAX = 60;

  /** Une ligne au journal du carnet. `jalon` : ce qu'on garde le plus
      longtemps (une mission, une rencontre), par opposition au quotidien.

      ⚠️ Il s'ecrit A PARTIR DE CE QUE LE JEU EMET DEJA. Le jour ou c'est une
      deuxieme comptabilite tenue a la main, elle derive de la premiere et plus
      personne ne sait laquelle a raison. */
  function noter(texte, jalon) {
    const p = B.partie;
    if (!p || !texte) return null;
    if (!Array.isArray(p.carnet)) p.carnet = [];
    const ligne = { j: p.jour, t: String(texte).toUpperCase(), jalon: !!jalon };
    p.carnet.push(ligne);
    // On coupe par le bas, et le quotidien part avant les jalons.
    while (p.carnet.length > CARNET_MAX) {
      const i = p.carnet.findIndex(function (q) { return !q.jalon; });
      p.carnet.splice(i >= 0 ? i : 0, 1);
    }
    return ligne;
  }

  /** On a parle a quelqu'un : le repertoire s'en souvient, une seule fois. */
  function rencontrer(slug) {
    const p = B.partie, perso = personnage(slug);
    if (!perso || !p || p.connus[slug]) return false;
    p.connus[slug] = p.jour;
    noter('RENCONTRÉ ' + perso.nom, true);
    return true;
  }

  function personnages() { return B.defs.personnages || []; }
  function personnage(slug) { return personnages().find(function (p) { return p.slug === slug; }) || null; }
  function mission(slug) { return defs().find(function (m) { return m.slug === slug; }) || null; }
  function faite(slug) { return !!B.partie.missionsFaites[slug]; }
  function courante() { return B.partie.mission ? mission(B.partie.mission.slug) : null; }

  /** `exige` de M16 tenu ? — ce qu'il faut AVOIR en plus des pre-requis
      (`argent_min`, `proprietes`, `liberes`, `dette`, `tenue`, `heure`).
      Un pre-requis dit « apres quoi », `exige` dit « dans quel etat ». */
  function exigeTenu(exige) {
    if (!exige) return true;
    const p = B.partie;
    if (exige.argent_min !== undefined && p.argent < exige.argent_min) return false;
    if (exige.liberes !== undefined && (p.libere || []).length < exige.liberes) return false;
    if (exige.proprietes !== undefined && (p.proprietes && Object.keys(p.proprietes).length < exige.proprietes)) return false;
    if (exige.dette !== undefined && (p.dette || 0) > exige.dette) return false;
    if (exige.tenue && (p.tenues || []).indexOf(exige.tenue) < 0) return false;
    // ⚠️ `exige.heure` ne se juge PAS ici : `disponibles()` est un filtre
    // statique, sans le moment du jour. L'heure se vérifie au DECLENCHEMENT du
    // téléphone (tranche 3, la police : être au casse-croûte à midi).
    return true;
  }

  /** ⚠️ `ferme` de M16 : une mission FERMEE disparait du telephone ET du carnet.
      C'est ce qui fait les choix (q10/q11, r03/r04, d07/d08, e11, x04). */
  function estFermee(slug) { return (B.partie.fermees || []).indexOf(slug) >= 0; }

  /** Les missions qu'on peut commencer : prerequis faits, pas encore faites,
      aucune en cours, `exige` tenu, et pas fermees. */
  function disponibles() {
    if (B.partie.mission) return [];
    return defs().filter(function (m) { return !faite(m.slug) && !estFermee(m.slug) && m.prerequis.every(faite) && exigeTenu(m.exige); });
  }

  function disponibleDe(donneur) {
    return disponibles().find(function (m) { return m.donneur === donneur; }) || null;
  }

  // --- Les lieux -------------------------------------------------------------------------

  function point(slug) { return Monde.carte.points.find(function (p) { return p.slug === slug; }) || null; }

  /** Le pixel d'un lieu nomme : la tuile devant sa porte. Les lieux speciaux
      sont des points d'interet ; le kiosque, lui, n'est qu'une porte. */
  function lieu(slug) {
    // ⚠️ Une `aller` vers un mouillage vise le POSTE (le quai, marchable) — pas
    // le centre de la coque, qui est dans l'eau (`lieuDeLivraison` fait déjà
    // cette différence pour un `livrer`).
    if (slug.indexOf('mouillage:') === 0) { const mo = trouverMouillage(slug.slice(10)); return mo && mo.poste ? { x: mo.poste.x, y: mo.poste.y, nom: 'le quai' } : null; }
    const p = point(slug);
    if (p) return { x: p.x * TT + 8, y: p.y * TT + 8, nom: p.nom };
    const porte = (Monde.carte.def.portes || []).find(function (q) { return q.lieu === slug; });
    if (porte) {
      const inte = Monde.carte.def.interieurs && Monde.carte.def.interieurs[porte.interieur];
      return { x: porte.x * TT + 8, y: (porte.y + 1) * TT + 8, nom: inte ? inte.nom : slug };
    }
    return null;
  }

  /** Ou l'on LIVRE un char : devant la porte de garage du lieu s'il en a une —
      c'est la qu'on stationne (demande de Martin, 17 sept. 2026) —, sinon a sa
      porte. ⚠️ Le rayon de l'objectif ne change pas : la baie est a trois tuiles
      de la porte des pietons, et un char livre « au garage » l'est toujours. */
  function lieuDeLivraison(slug) {
    // ⚠️ Livrer UNE COQUE, c'est la ramener à son mouillage — il n'y a pas de
    // baie de garage sur l'eau. Le centre du mouillage, comme `poserLeChar`.
    if (slug.indexOf('mouillage:') === 0) { const mo = trouverMouillage(slug.slice(10)); return mo ? { x: mo.x, y: mo.y, nom: 'son mouillage' } : null; }
    const pg = Monde.porteDeGarage(slug);
    if (!pg) return lieu(slug);
    const baie = Monde.baieDeLaPorteDeGarage(pg), l = lieu(slug);
    return { x: baie.x, y: baie.y, nom: l ? l.nom : slug };
  }

  /** Une tuile marchable pres d'un pixel, hors chaussee, en spirale.

      ⚠️ **Jamais devant une porte** : c'est ici que les missions posent leur monde (le
      donneur, les hommes de main, le fuyard, l'escorte), et un personnage plante sur le
      pas d'un commerce est un obstacle qu'on contourne pour entrer. On prend la premiere
      tuile qui n'y est pas, dans le rayon ; a defaut, la premiere venue — mieux vaut un
      donneur devant une porte que pas de donneur. */
  function tuileLibre(x, y, rayonMax) {
    const tx = Math.floor(x / TT), ty = Math.floor(y / TT);
    let repli = null;
    for (let r = 0; r <= (rayonMax || 4); r++) {
      for (let dy = -r; dy <= r; dy++) for (let dx = -r; dx <= r; dx++) {
        if (Math.max(Math.abs(dx), Math.abs(dy)) !== r) continue;
        if (!Monde.marchablePieton(tx + dx, ty + dy) || Monde.estChaussee(tx + dx, ty + dy)) continue;
        const place = { x: (tx + dx) * TT + 8, y: (ty + dy) * TT + 8 };
        if (!Monde.devantDUnePorte(tx + dx, ty + dy)) return place;
        if (!repli) repli = place;
      }
    }
    return repli;
  }

  /** Une tuile de rue (avec une fleche) pres d'un pixel : la ou un char peut naitre.
      `accepte(place)`, facultatif, ecarte celles qui ne font pas l'affaire. */
  function tuileDeRue(x, y, rayonMax, accepte) {
    const tx = Math.floor(x / TT), ty = Math.floor(y / TT);
    for (let r = 1; r <= (rayonMax || 8); r++) {
      for (let dy = -r; dy <= r; dy++) for (let dx = -r; dx <= r; dx++) {
        if (Math.max(Math.abs(dx), Math.abs(dy)) !== r) continue;
        const f = Monde.fleche(tx + dx, ty + dy);
        if (f !== '>' && f !== '<' && f !== '^' && f !== 'v') continue;
        const place = { x: (tx + dx) * TT + 8, y: (ty + dy) * TT + 8, sens: f };
        if (!accepte || accepte(place)) return place;
      }
    }
    return null;
  }

  /** Où le joueur se tient DANS LA VILLE. ⚠️ Dedans, ses x et y sont ceux de la PIÈCE
      (la cantine : 104, 120) : une rue cherchée à ces coordonnées-là est celle du coin
      haut-gauche de la carte, à 3 000 px de la porte. La rue qu'il verra en sortant est
      celle de sa porte (`B.exterieur`). */
  function ouEstLeJoueurEnVille() {
    const ext = B.interieur ? B.exterieur : null;
    return ext ? { x: ext.x, y: ext.y } : { x: B.joueur.x, y: B.joueur.y };
  }

  const CAP_DE_FLECHE = { '>': 0, '<': Math.PI, '^': -Math.PI / 2, 'v': Math.PI / 2 };

  /** Une place ou poser un char SANS le poser dans un autre.

      ⚠️ Arrive au poste EN CHAR, on s'arrete devant la porte — sur la tuile de
      rue la plus proche, celle-la meme ou naissait l'auto-patrouille de M4 : elle
      naissait DANS notre char, aux memes x et y, cachee dessous, et ACTION nous
      remettait au volant du notre. « L'auto-patrouille n'apparait pas. » Un char
      fait 28 px de long : rien a moins de 32 px, ni personne sur la tuile. */
  function sansChar(place) {
    return !B.entites.some(function (e) {
      if (e.type === 'vehicule') return dist2(e.x, e.y, place.x, place.y) < 32 * 32;
      return e.type === 'joueur' && dist2(e.x, e.y, place.x, place.y) < 20 * 20;
    });
  }

  /** La ruelle (glyphe `x`) la plus proche d'un lieu, a `loin` tuiles au moins —
      la ou dort le char de M1.

      ⚠️ `loin` vient du lieu (`ruelle:garage:24`, dans `missions.py`) : sans
      lui, c'est la plus proche.
      ⚠️ Seulement une tuile dont les DEUX voisines, dans le sens de la ruelle,
      sont de la ruelle : un char fait deux tuiles, et pose au bout d'une impasse
      il nait le nez dans un mur. `sens` dit dans quel sens le tourner (`poser`). */
  function ruellePres(slug, loin) {
    const p = point(slug), c = Monde.carte;
    if (!p) return null;
    const min2 = (loin || 0) * (loin || 0);
    let meilleur = null, dMin = Infinity;
    for (let ty = 1; ty < c.h - 1; ty++) for (let tx = 1; tx < c.w - 1; tx++) {
      if (Monde.glyphe(tx, ty) !== 'x') continue;
      const d = dist2(tx, ty, p.x, p.y);
      if (d < min2 || d >= dMin) continue;
      const long = Monde.glyphe(tx - 1, ty) === 'x' && Monde.glyphe(tx + 1, ty) === 'x';
      const large = Monde.glyphe(tx, ty - 1) === 'x' && Monde.glyphe(tx, ty + 1) === 'x';
      if (!long && !large) continue;
      dMin = d; meilleur = { x: tx * TT + 8, y: ty * TT + 8, sens: long ? '>' : 'v' };
    }
    return meilleur;
  }

  // --- Les lieux de M16 (docs/plan.md, « Des lieux qu'on peut nommer ») -----
  //
  // ⚠️ **JAMAIS DE DÉ** : un lieu se résout par itération déterministe (la
  // spirale de `tuileLibre`, la plus proche du joueur), pas par `B.rng()`. La
  // règle de la ville tient ici encore : un tirage au dé décalerait tout le
  // hasard qui suit.

  /** Sans accents, en majuscules — pour matcher une enseigne (`boutique:pharmacie`). */
  function sansAccent(t) {
    return (t || '').toUpperCase()
      .replace(/[ÀÂÄ]/g, 'A').replace(/[ÉÈÊË]/g, 'E')
      .replace(/[ÎÏ]/g, 'I').replace(/[ÔÖ]/g, 'O')
      .replace(/[ÙÛÜ]/g, 'U').replace(/Ç/g, 'C');
  }

  /** La devanture la plus proche dont l'ENSEIGNE porte le mot (`boutique:<mot>`).
      Le pixel rendu est devant la porte, sur le trottoir. La « plus proche du
      joueur » est un choix délibéré : une mission dit « la pharmacie d'ici »,
      pas « une pharmacie n'importe où ». */
  function boutiquex(mot) {
    const devs = (Monde.carte.def && Monde.carte.def.devantures) || [];
    const n = sansAccent(mot), j = B.joueur;
    let meilleure = null, meilleureD = Infinity;
    for (const d of devs) {
      if (!d.texte || sansAccent(d.texte).indexOf(n) < 0) continue;
      const d2 = dist2(d.x * TT + 8, (d.y + 1) * TT + 8, j.x, j.y);
      if (d2 < meilleureD) { meilleureD = d2; meilleure = d; }
    }
    return meilleure
      ? { x: (meilleure.x + meilleure.l / 2) * TT + 8, y: (meilleure.y + 1) * TT + 8, nom: meilleure.texte }
      : null;
  }

  /** Une tuile marchable dans un district, en spirale autour de son centre. */
  function tuileDeDistrict(slug) {
    const z = (Monde.carte.zones || []).find(function (q) { return q.slug === slug; });
    if (!z) return null;
    const cx = (z.x + z.l / 2) * TT + 8, cy = (z.y + z.h / 2) * TT + 8;
    return tuileLibre(cx, cy, Math.max(z.l, z.h)) || { x: cx, y: cy };
  }

  /** Le pont de La Pointe : la barrière du paquet (elle porte le bon rectangle). */
  function lieuPont() {
    const b = ((Monde.carte.def && Monde.carte.def.barrieres) || []).find(function (q) { return q.slug === 'pont'; });
    return b ? { x: (b.x + b.l / 2) * TT + 8, y: (b.y + b.h / 2) * TT + 8, nom: b.nom } : null;
  }

  /** L'arche de la foire : même patron que `lieuPont` — la barrière du paquet
      porte déjà le bon rectangle (`carte.py::foire_entree`), rien à recalculer. */
  function lieuFoire() {
    const b = ((Monde.carte.def && Monde.carte.def.barrieres) || []).find(function (q) { return q.slug === 'foire'; });
    return b ? { x: (b.x + b.l / 2) * TT + 8, y: (b.y + b.h / 2) * TT + 8, nom: b.nom } : null;
  }

  /** Un quai marchable (glyphe `q` ou `j`), le premier rencontré — déterministe
      par l'ordre de lecture (nord-ouest d'abord). */
  function tuileDeQuai() {
    const c = Monde.carte;
    for (let ty = 0; ty < c.h; ty++) for (let tx = 0; tx < c.w; tx++) {
      const g = Monde.glyphe(tx, ty);
      if ((g === 'q' || g === 'j') && Monde.marchablePieton(tx, ty)) return { x: tx * TT + 8, y: ty * TT + 8 };
    }
    return null;
  }

  /** Les bois de La Pointe : un glyphe `n` marchable dans le district `pointe`. */
  function tuileDeBois() {
    const z = (Monde.carte.zones || []).find(function (q) { return q.slug === 'pointe'; });
    if (!z) return null;
    for (let ty = z.y; ty < z.y + z.h; ty++) for (let tx = z.x; tx < z.x + z.l; tx++) {
      if (Monde.glyphe(tx, ty) === 'n' && Monde.marchablePieton(tx, ty)) return { x: tx * TT + 8, y: ty * TT + 8 };
    }
    return null;
  }

  /** Une rampe du district demandé (`rampe:<district>`), la plus proche du joueur. */
  function tuileDeRampe(district) {
    const rampes = Monde.carte.rampes || [];
    const z = (Monde.carte.zones || []).find(function (q) { return q.slug === district; });
    const j = B.joueur;
    let meilleure = null, meilleureD = Infinity;
    for (const r of rampes) {
      if (z && (r.x < z.x || r.x >= z.x + z.l || r.y < z.y || r.y >= z.y + z.h)) continue;
      const d2 = dist2(r.x * TT + 8, r.y * TT + 8, j.x, j.y);
      if (d2 < meilleureD) { meilleureD = d2; meilleure = r; }
    }
    return meilleure ? { x: meilleure.x * TT + 8, y: meilleure.y * TT + 8 } : null;
  }

  /** Le mouillage `slug` (le n-ième, 0 par défaut — deux chalutiers partagent le
      slug) : `carte.mouillages` (`navires.py`). `null` si la ville n'en a pas. */
  function trouverMouillage(spec) {
    const deux = spec.split(':'), slug = deux[0], n = Number(deux[1]) || 0;
    const tous = ((Monde.carte && Monde.carte.def && Monde.carte.def.mouillages) || []).filter(function (q) { return q.slug === slug; });
    return tous[n] || null;
  }

  /** LA CHALOUPE DE SVEN : pas la sienne en propre (les amarrages, `carte.amarrages`,
      n'appartiennent à personne — seuls les grands bateaux ont un mouillage nommé),
      mais celle amarrée le plus près de SON porte-conteneurs. ⚠️ `{ x, y, amarrage }`
      comme `resoudre('mouillage:…')` rend `{ x, y, mouillage }` : `poserLeChar` s'en
      sert pour ne pas router par `tuileDeRue` et pour réserver la place
      (`Vehicules.majAmarrages` ne la refait pas naître par-dessus). */
  function amarrageDeSven() {
    const places = (Monde.carte.def.amarrages || []), cargo = trouverMouillage('porte_conteneurs');
    if (!places.length || !cargo) return null;
    let meilleure = null, dMin = Infinity;
    for (const a of places) {
      const x = a.x * TT + 8, y = a.y * TT + 8, d2 = (x - cargo.x) * (x - cargo.x) + (y - cargo.y) * (y - cargo.y);
      if (d2 < dMin) { dMin = d2; meilleure = { x: x, y: y, amarrage: a }; }
    }
    return meilleure;
  }

  /** `ou` d'un objectif ou d'un personnage → un pixel. */
  function resoudre(ou, m) {
    if (!ou) return null;
    if (ou === 'donneur') return ouTrouver(m.donneur);
    if (ou === 'pont') return lieuPont();
    if (ou === 'quai') return tuileDeQuai();
    if (ou === 'bois') return tuileDeBois();
    if (ou === 'foire') return lieuFoire();
    if (ou === 'amarrage:sven') return amarrageDeSven();
    const deux = ou.split(':');
    if (deux[0] === 'porte') return lieu(deux[1]);
    if (deux[0] === 'ruelle') return ruellePres(deux[1], Number(deux[2]) || 0);   // `ruelle:garage:24`
    if (deux[0] === 'zone') { const z = Monde.carte.zones.find(function (q) { return q.slug === deux[1]; }); return z ? { x: (z.x + z.l / 2) * TT, y: (z.y + z.h / 2) * TT, zone: z } : null; }
    if (deux[0] === 'point') return null;                 // dedans : pas de pixel en ville
    if (deux[0] === 'district') return tuileDeDistrict(deux[1]);
    if (deux[0] === 'boutique') return boutiquex(deux[1]);
    if (deux[0] === 'rampe') return tuileDeRampe(deux[1]);
    // ⚠️ Le CENTRE de la coque, pas son poste : une caméra le regarde, et
    // `poserLeChar` y fait naître le véhicule, à son cap (`m.angle`).
    if (deux[0] === 'mouillage') { const mo = trouverMouillage(deux.slice(1).join(':')); return mo ? { x: mo.x, y: mo.y, mouillage: mo } : null; }
    return lieu(ou);
  }

  function lieuDuPersonnage(slug) {
    const p = personnage(slug);
    if (!p) return null;
    const ou = p.ou.split(':');
    if (ou[0] === 'porte') return lieu(ou[1]);
    if (ou[0] === 'point') {                                // il est dedans : la porte de son commerce
      const piece = pieceDuPoint(ou[1]);
      return piece ? lieu(piece.slug) : null;
    }
    // ⚠️ Le POSTE, pas le centre de la coque : Sven se tient sur la jetée, pas
    // dans l'eau (`navires.py` l'exporte pour chaque mouillage).
    if (ou[0] === 'mouillage') { const mo = trouverMouillage(ou.slice(1).join(':')); return mo && mo.poste ? mo.poste : null; }
    // ⚠️ Posé DEHORS, à l'arche — contrairement à un donneur `point:`, il existe
    // vraiment en ville : hélable, GPS, et un `retourner` le trouve.
    if (ou[0] === 'foire') return lieuFoire();
    return null;
  }

  /** Ou POINTER pour trouver quelqu'un : sa personne quand elle est dans le
      meme monde que nous, sinon sa porte.

      ⚠️ Dedans, le donneur qu'on a sous les yeux vit en coordonnees de PIECE
      (12, 6 dans le casse-croute) : le poser tel quel sur la minicarte
      enverrait la fleche a six tuiles du coin nord-ouest de la ville. */
  function ouTrouver(slug) {
    return (!B.interieur && donneur(slug)) || lieuDuPersonnage(slug);
  }

  //: Les personnages qui se tiennent DEDANS : leur `ou` nomme un point de
  //: piece (`point:sergent`), et c'est le point qui dit ou ils sont. La table
  //: ne se recopie donc nulle part — `missions.py` la porte deja.
  function personnageDuPoint(type) {
    return personnages().find(function (p) { return p.ou === 'point:' + type; }) || null;
  }

  /** La piece qui porte ce type de point — celle ou le personnage se tient.
      ⚠️ Dedans, `Monde.carte.def.interieurs` est vide : c'est la VILLE qui
      garde le catalogue des pieces. */
  function pieceDuPoint(type) {
    const ville = Monde.carte.ville || Monde.carte;
    const pieces = (ville.def && ville.def.interieurs) || {};
    for (const slug in pieces) {
      if ((pieces[slug].points || []).some(function (q) { return q.type === type; })) return pieces[slug];
    }
    return null;
  }

  // --- Les donneurs, en chair et en os ---------------------------------------------------

  function donneur(slug) {
    return B.entites.find(function (e) { return e.type === 'pieton' && e.personnage === slug && e.vivant; }) || null;
  }

  /** La cible d'un objectif `parler` : le slug du personnage a qui l'on doit
      parler. `cible: "<perso>"` ou `cible: "personnages:<perso>"` nomment un
      personnage de l'histoire ; `cible: "arch:<slug>"` vise le premier
      figurant de cet archetype pose en ville (les cinq commis de f12). Les
      quatre contacts de m6 sont des personnages. */
  function cibleDuParler(o) {
    const c = o && o.cible;
    if (!c) return null;
    if (c.indexOf('arch:') === 0) return 'arch:' + c.slice(5);
    if (c.indexOf('personnages:') === 0) return c.slice(12);
    return c;
  }

  /** Pose les personnages qui se tiennent DEHORS, a cote de leur porte — sauf
      ceux qui sont partis apres leur mission (`parti_apres`). */
  function creerDonneurs() {
    for (const p of personnages()) {
      // Parti apres sa mission (Ti-Guy entre au garage a la fin de M1) : dans les
      // donnees, parce qu'ici aucun slug de mission ne s'ecrit.
      if (p.parti_apres && faite(p.parti_apres)) continue;
      if (p.ou.indexOf('porte:') === 0) poserDonneur(p);
      // ⚠️ Sven se tient sur SON poste a quai (`mouillage:`), pas a une porte :
      // les autres formes (`point:`) restent dedans, posees a l'entree de leur piece.
      else if (p.ou.indexOf('mouillage:') === 0) poserDonneurMouillage(p);
      // Le Bonimenteur, a l'arche de la foire — dehors, comme une porte, mais sans batiment.
      else if (p.ou === 'foire') poserDonneurFoire(p);
    }
  }

  /** UN personnage posé à l'arche de la foire (`ou: "foire"`) — même idée que
      `poserDonneur`, mais la position vient de `lieuFoire()` (une barrière), pas
      d'un bâtiment `SPECIAUX`. */
  function poserDonneurFoire(p) {
    const l = lieuFoire();
    if (!l) return null;
    const place = placeVisible(l);
    return place ? creerPersonnage(p, place.x, place.y) : null;
  }

  /** UN personnage posé à quai, à côté du grand bateau que `navires.py` lui
      donne (`mouillage:<slug>[:n]`) — la même idée que `poserDonneur`, mais sur
      le POSTE, pas devant une porte. `null` si la ville n'a pas ce mouillage.

      ⚠️ **PAS PILE SUR LE POSTE.** C'est là que la coque s'aborde
      (`Vehicules.vehiculeSousLaMain`) : un personnage planté dessus vole le
      bouton ACTION au bateau, comme un donneur planté sur le pas d'une porte —
      la même raison qui écarte celui-là de 2 tuiles (`placeVisible`). Deux
      tuiles plus loin, le long du MÊME quai (l'axe où le poste ne bouge pas
      d'avec le centre de la coque est celui qui longe le flanc). */
  function poserDonneurMouillage(p) {
    const mo = trouverMouillage(p.ou.slice(10));
    if (!mo || !mo.poste) return null;
    const long_x = mo.poste.y === mo.y;
    const pas = { x: long_x ? 2 * TT : 0, y: long_x ? 0 : 2 * TT };
    for (const signe of [1, -1, 0]) {
      const x = mo.poste.x + pas.x * signe, y = mo.poste.y + pas.y * signe;
      if (Monde.marchablePieton(Math.floor(x / TT), Math.floor(y / TT))) return creerPersonnage(p, x, y);
    }
    return null;
  }

  //: Au-dela de cette part de son sprite sous du decor peint apres lui, un personnage est CACHE.
  const CACHE_MAX = 0.5;

  /** La part (0 a 1) du sprite d'un personnage pose en (x, y) que du decor PEINT APRES
      LUI recouvre.

      ⚠️ La ville se peint du nord au sud (`Entites.dessiner` trie par `y`) : un abribus
      une tuile plus bas passe DEVANT quelqu'un qui se tient derriere lui, et il n'en reste
      que la tete — c'etait Ti-Paul, devant son depanneur (20 sept. 2026). Un decor a la
      meme hauteur est peint AVANT lui (son numero est plus petit), donc ne le cache pas.
      On compte les RECTANGLES des fiches, pixels transparents compris : c'est prudent, et
      juste pour les decors pleins qui posent probleme (abribus, roulotte, kiosque). Tous
      les personnages de l'histoire portent le corps du joueur (`creerPersonnage`). */
  function partCachee(x, y) {
    if (typeof DECORS === 'undefined' || typeof SPRITES === 'undefined') return 0;
    const corps = SPRITES.joueur, x0 = x - corps.ancre[0], y0 = y - corps.ancre[1];
    let cache = 0;
    for (const d of B.entites) {
      const f = d.decor && d.dessine !== false ? DECORS[d.decor] : null;
      if (!f || d.y <= y) continue;
      const dx0 = d.x - f.ancre[0], dy0 = d.y - f.ancre[1] - (d.altitude || 0);
      const ox = Math.min(x0 + corps.w, dx0 + f.w) - Math.max(x0, dx0);
      const oy = Math.min(y0 + corps.h, dy0 + f.h) - Math.max(y0, dy0);
      if (ox > 0 && oy > 0) cache += ox * oy;
    }
    return Math.min(1, cache / (corps.w * corps.h));
  }

  /** Une tuile ou l'on peut se tenir : du trottoir, hors du pas d'une porte, et sans decor
      solide dessus (`tuileLibre` ne regarde que la carte, pas les abribus ni les bancs). */
  function tuileDeTrottoir(tx, ty) {
    if (!Monde.marchablePieton(tx, ty) || Monde.estChaussee(tx, ty) || Monde.devantDUnePorte(tx, ty)) return null;
    const x = tx * TT + 8, y = ty * TT + 8;
    const pris = Entites.decorAutour(x, y, 24).some(function (d) { return d.solide && Math.hypot(d.x - x, d.y - y) < d.r + 7; });
    return pris ? null : { x: x, y: y };
  }

  //: Deux personnages de l'histoire ne se tiennent pas a moins de tant de tuiles l'un de l'autre
  //: (en carre). ⚠️ Retour de Martin (22 sept. 2026, capture du depanneur) : Ti-Paul et Xavier
  //: attendent a la meme porte, et `placeVisible` les posait sur le MEME pixel — deux bulles l'une
  //: sur l'autre, un seul bonhomme. Ti-Guy, Mo et Fern etaient trois sur la meme tuile du terminus.
  const ECART_DONNEURS = 2;

  /** Un autre personnage de l'histoire se tient-il deja sur cette place, ou colle a elle ? */
  function placeTenue(place) {
    return B.entites.some(function (e) {
      return e.type === 'pieton' && e.personnage && e.vivant
        && Math.max(Math.abs(e.x - place.x), Math.abs(e.y - place.y)) < ECART_DONNEURS * TT;
    });
  }

  /** La place touche-t-elle un meuble solide (une des huit tuiles autour) ? ⚠️ En TUILES : le
      decor est ancre au pied de la sienne (`creerDecor`), pas en son centre. */
  function colleeAUnMeuble(place) {
    const tx = Math.floor(place.x / TT), ty = Math.floor(place.y / TT);
    return Entites.decorAutour(place.x, place.y, 2 * TT).some(function (d) {
      return d.solide && Math.max(Math.abs(Math.floor(d.x / TT) - tx), Math.abs(Math.floor(d.y / TT) - ty)) <= 1;
    });
  }

  /** Ou un personnage se tient devant sa porte : a deux tuiles d'un cote, sinon de l'autre —
      et, si du decor le cache (`partCachee`), la tuile voisine la plus proche ou on le voit.
      ⚠️ SANS DE : les essais vont dans un ordre fixe, du plus pres au plus loin de la porte.
      Quand rien n'est mieux, la tuile la moins cachee.

      ⚠️ Une place qu'un autre personnage tient (`placeTenue`) ne se prend pas : le second donneur
      d'une porte passe aux essais suivants. Et parmi ceux-la, pas une tuile collee a un meuble
      (`colleeAUnMeuble`) : c'est entre l'edicule du metro et le guichet que Ti-Paul se rabattait.
      Le premier donneur, lui, se tient ou il s'est toujours tenu. */
  function placeVisible(l) {
    const premiere = tuileLibre(l.x + 2 * TT, l.y, 3) || tuileLibre(l.x - 2 * TT, l.y, 3);
    if (!premiere) return null;
    const libre = !placeTenue(premiere);
    let part = libre ? partCachee(premiere.x, premiere.y) : 1, meilleure = libre ? premiere : null;
    if (libre && part < CACHE_MAX) return premiere;
    const tx0 = Math.floor(l.x / TT), ty0 = Math.floor(l.y / TT);
    const essais = [[-2, 0], [3, 0], [-3, 0], [2, 1], [-2, 1], [4, 0], [-4, 0], [3, 1], [-3, 1]];
    // Un second donneur cherche un peu plus loin : a deux tuiles de l'autre, il lui faut la place.
    if (!libre) essais.push([5, 0], [-5, 0], [4, 1], [-4, 1], [6, 0], [-6, 0]);
    let collee = null;
    for (const [dx, dy] of essais) {
      const place = tuileDeTrottoir(tx0 + dx, ty0 + dy);
      if (!place || placeTenue(place)) continue;
      const c = partCachee(place.x, place.y);
      if (!libre && colleeAUnMeuble(place)) {
        if (c < CACHE_MAX && !collee) collee = place;
        continue;
      }
      if (c < CACHE_MAX) return place;
      if (c < part) { part = c; meilleure = place; }
    }
    return collee || meilleure || premiere;
  }

  /** UN personnage du dehors, pose devant sa porte — ou null quand la porte ou la
      place manque. ⚠️ Il ne regarde ni `parti_apres` ni s'il est deja la : c'est
      `creerDonneurs` qui juge s'il doit exister, et le debug (`Hud.menuSautMissions`)
      qui le REPOSE pour refaire la mission d'un donneur parti. */
  function poserDonneur(p) {
    const l = lieu(p.ou.slice(6));
    if (!l) return null;
    // A deux tuiles de la porte : assez pres pour le voir, assez loin pour
    // qu'ACTION au pas de la porte serve encore a autre chose — et JAMAIS derriere
    // un abribus : `placeVisible` ecarte la tuile ou du decor le cache.
    const place = placeVisible(l);
    return place ? creerPersonnage(p, place.x, place.y) : null;
  }

  /** Pose les personnages qui se tiennent DEDANS, quand on entre chez eux.

      ⚠️ Ils naissent avec la piece et meurent avec elle (`B.entites` est
      remplace des deux cotes de la porte, comme pour le commis) : rien a
      nettoyer en sortant. Avant ca, Bouchard et Josee n'existaient NULLE PART
      — ni dans la rue, ni dans leur piece : on poussait la porte du
      casse-croute, la salle etait vide, et il fallait deviner qu'un point
      invisible attendait au fond a droite. */
  function creerDonneursDedans(piece) {
    if (!piece) return;
    for (const p of personnages()) {
      if (p.ou.indexOf('point:') !== 0) continue;
      const point = (piece.points || []).find(function (q) { return q.type === p.ou.slice(6); });
      if (!point) continue;
      const place = placeDebout(point);
      const e = creerPersonnage(p, place.x, place.y);
      e.face = 'bas';                                   // il regarde la salle, donc la porte
    }
    Entites.indexer();
  }

  /** Ou se TIENT quelqu'un dont le point tombe sur un meuble : Josee pointe la
      derniere table du Brouillard, et personne ne se tient debout sur une
      table. On prend alors la tuile libre voisine la plus proche du milieu de
      la piece — le fond d'un coin, ce n'est pas une scene. */
  function placeDebout(point) {
    const centre = { x: Monde.carte.w / 2, y: Monde.carte.h / 2 };
    let meilleure = null, dMin = Infinity;
    for (let dy = -1; dy <= 1; dy++) {
      for (let dx = -1; dx <= 1; dx++) {
        const tx = point.x + dx, ty = point.y + dy;
        if (!Monde.marchablePieton(tx, ty) || Monde.estMeuble(tx, ty)) continue;
        const d = Math.hypot(tx - centre.x, ty - centre.y) + (dx || dy ? 0.5 : 0);   // son point d'abord
        if (d < dMin) { dMin = d; meilleure = { x: tx * TT + 8, y: ty * TT + 8 }; }
      }
    }
    return meilleure || { x: point.x * TT + 8, y: point.y * TT + 8 };
  }

  function creerPersonnage(p, x, y) {
    const arch = { slug: 'perso_' + p.slug, nom: p.nom, sprite: 'joueur', couleurs: p.couleurs, vitesse: 0, courage: 0,
                   temoin: 0, vie: 100, argent: [0, 0], arme: null, intouchable: true, metier: 'histoire',
                   // Sa tenue de rue : la meme tete que son portrait, chapeau compris (`garderobe.py`).
                   tenue: typeof Garderobe !== 'undefined' ? Garderobe.duPersonnage(p.slug) : null };
    const e = Entites.creerPieton(x, y, arch);
    e.personnage = p.slug; e.etat = 'fige'; e.cri = 0;
    return e;
  }

  /** Le personnage a portee d'ACTION, s'il y en a un. */
  function personnageSousLaMain(j) {
    return Entites.pietonsAutour(j.x, j.y, RAYON_PARLER).find(function (e) { return e.personnage && faceA(j, e.x, e.y); }) || null;
  }

  // --- Les dialogues, dits a voix haute ----------------------------------------------------

  /** Une suite de repliques. Le joueur ecoute : ACTION passe a la suivante, et
      la voix finie (ou le texte lu) passe toute seule. `fin` s'appelle apres. */
  //: A cette distance, celui qui parle est LA ; plus loin, on l'entend au combine.
  const RAYON_PRESENT = 12 * TT;

  /** Celui qui parle est-il la, a portee de voix ? */
  function present(qui) {
    const j = B.joueur, e = donneur(qui);
    return !!(j && e && e.dessine !== false && dist2(e.x, e.y, j.x, j.y) < RAYON_PRESENT * RAYON_PRESENT);
  }

  /** Les repliques d'une partie, pretes a dire, avec leur slug de voix.

      ⚠️ AU COMBINE : l'appel toujours, et l'echec toujours — on n'est jamais a
      cote du donneur quand on rate. L'intro, la fin et les repliques `pendant`
      le sont QUAND CELUI QUI PARLE N'EST PAS LA (`auto`, tranche a la ligne) :
      une fin de M4 jouee au garage, Bouchard au casse-croute, se dit au
      telephone ; la meme ligne dite a deux pas ne l'est pas. Le client du taxi,
      lui, est assis dans le char. */
  function lignesDe(m, partie, filtre) {
    const toujours = partie === 'appel' || partie === 'echec';
    const auto = partie === 'intro' || partie === 'fin' || partie === 'pendant';
    return ((m && m.dialogue && m.dialogue[partie]) || []).map(function (l, i) {
      return { qui: l.qui, texte: l.texte, telephone: toujours, auto: auto, objectif: l.objectif,
               slug: slugDeVoix(m, partie, i), humeur: l.humeur };
    }).filter(function (l) { return !filtre || filtre(l); });
  }

  function dire(m, partie, fin, filtre) {
    const lignes = lignesDe(m, partie, filtre);
    if (!lignes.length) { if (fin) fin(); return false; }
    Son.Voix.chargerHistoire(m.slug);
    B.cinema = { lignes: lignes, i: -1, t: 0, duree: 0, fin: fin || null, mission: m.slug, partie: partie };
    Entree.contexte('dialogue');
    suivante();
    return true;
  }

  /** Des repliques deja pretes (`{ qui, texte, slug, telephone }`) : c'est ce que
      dit une scene (`Scenes`, plan `dire`). `anonyme` : pas de nom au-dessus de
      la boite — une voix qu'on entend, pas quelqu'un a qui l'on parle. */
  function direLignes(lignes, options) {
    const o = options || {};
    if (!lignes || !lignes.length) { if (o.fin) o.fin(); return false; }
    B.cinema = { lignes: lignes, i: -1, t: 0, duree: 0, fin: o.fin || null, mission: o.mission || null,
                 partie: o.partie || null, anonyme: !!o.anonyme };
    suivante();
    return true;
  }

  /** Le slug de voix d'une replique : `<qui>-<mission>-<n>`, n compte a travers
      appel, intro, client, fin, echec, pendant, renvoi, accueil — exactement comme `missions.repliques()`. */
  function slugDeVoix(m, partie, i) {
    // ⚠️ `pendant` APRES `echec`, puis `renvoi`, comme `missions.PARTIES` : inseree plus tot,
    // elle renommerait des voix deja generees.
    const ordre = ['appel', 'intro', 'client', 'fin', 'echec', 'pendant', 'renvoi', 'accueil'];
    let n = 0;
    for (const p of ordre) {
      const lignes = m.dialogue[p] || [];
      if (p === partie) return lignes[i].qui + '-' + m.slug + '-' + (n + i + 1);
      n += lignes.length;
    }
    return null;
  }

  function suivante() {
    const c = B.cinema;
    if (!c) return;
    c.i++;
    if (c.i >= c.lignes.length) { finir(); return; }
    const l = c.lignes[c.i];
    const p = personnage(l.qui);
    if (l.auto) l.telephone = !present(l.qui);        // la, ou au bout du fil : a la ligne
    c.t = 0;
    c.duree = 90 + l.texte.length * 3;                      // le temps de lire, si la voix manque
    // ⚠️ `anonyme` : l'ouverture n'a personne au-dessus de sa boite — c'est une
    // voix qu'on entend, pas quelqu'un a qui l'on parle. Le Clairon se
    // presentera demain matin, avec sa manchette.
    // Le visage de qui parle, avec la mine que lui donne son jeu (`l.humeur`, tiree des
    // balises par `visages.humeur`). ⚠️ Pas pour l'ouverture `anonyme` : une voix sans visage.
    Hud.dialogue(c.anonyme ? '' : (p ? p.nom : l.qui) + (l.telephone ? ' (AU TÉLÉPHONE)' : ''), decouper(l.texte), 0,
                 c.anonyme ? null : { slug: l.qui, humeur: l.humeur || 'neutre' });
    c.voix = Son.Voix.parler(l.slug, { telephone: l.telephone, fin: function () { if (B.cinema === c && c.i === c.lignes.indexOf(l)) c.duree = Math.min(c.duree, c.t + 20); } });
    if (B.dialogue && c.voix) B.dialogue.voix = true;
  }

  function finir() {
    const c = B.cinema;
    B.cinema = null;
    B.dialogue = null;
    Son.Voix.couper();
    // ⚠️ Pendant une scene, la derniere replique ne rend PAS les commandes :
    // la scene tourne encore (le car repart, le titre s'inscrit) et PASSER doit
    // rester PASSER jusqu'au bout.
    Entree.contexte(B.scene ? 'dialogue' : B.joueur && B.joueur.dansVehicule ? 'vehicule' : 'pied');
    if (c && c.fin) c.fin();
  }

  /** Deux lignes de 46 caracteres au plus : la boite fait la largeur de l'ecran. */
  function decouper(texte) {
    const mots = texte.split(' '), lignes = [];
    let courante = '';
    for (const mot of mots) {
      if ((courante + ' ' + mot).trim().length > 46) { lignes.push(courante.trim()); courante = mot; } else courante += ' ' + mot;
    }
    if (courante.trim()) lignes.push(courante.trim());
    return lignes;
  }

  function majCinema() {
    const c = B.cinema;
    if (!c) return;
    c.t++;
    // ⚠️ LA LIGNE ATTEND SA VOIX. `duree` est le temps de LIRE (90 + 3 par
    // caractere) : il passait a la suivante voix ou pas, et la suivante coupe
    // la voix. Mesure le 16 sept. 2026 : neuf repliques de mission y perdaient
    // leur fin (`bouchard-m4-6` : 7,06 s de voix, 5,65 s de ligne) — c'etait
    // une bonne part des « fins coupees ». `fin` rabat ensuite `duree` a la
    // derniere syllabe. Le plafond de 15 s au-dela garde une scene de rester
    // figee si le navigateur ne dit jamais que la voix s'est tue (onglet
    // cache, contexte suspendu) ; ACTION passe toujours.
    const l = c.lignes[c.i];
    // ⚠️ UNE VOIX QUI PARLE, OU QUI SE CHARGE ENCORE, RETIENT LA LIGNE. `parle`
    // regardait seulement `enCours` : la premiere replique d'une mission dont le
    // mp3 n'etait pas encore cache passait au temps de LIRE (court), la voix
    // chargee en differe arrivait sur la ligne suivante, et `parler` la coupait
    // a l'instant meme de la poser. Les voix regenerees du 18 sept. (plus
    // longues, avec leurs pauses) rendaient la coupure plus visible. Une voix
    // EN ATTENTE (`Voix.attendue`) pour la ligne courante retient donc autant
    // qu'une voix qui joue : son `fin` rabattra `duree` une fois dite.
    const enCours = !!(l && Son.Voix.enCours && Son.Voix.enCours.slug === l.slug);
    const enAttente = !!(l && Son.Voix.attendue && Son.Voix.attendue.slug === l.slug);
    const parle = (enCours || enAttente) && c.t < c.duree + 900;
    // ⚠️ PAS DE BOUTON A LA PREMIERE IMAGE D'UNE LIGNE. L'appui d'ACTION qui
    // OUVRE la conversation (`Combat.maj` → `parler`) est encore « neuf » quand
    // `Histoire.maj` passe ici, dans la MEME image : il sautait la premiere
    // replique de chaque intro — les cinq donneurs, clavier et manette, et la
    // voix demandee puis coupee aussitot. `c.t` compte les images de la ligne ;
    // `B.t` ne servirait pas, il s'arrete pendant une scene.
    const bouton = c.t > 1 && (Entree.neuf('action') || Entree.neuf('attaque'));
    if (bouton || (c.t > c.duree && !parle)) suivante();
  }

  // --- L'OUVERTURE : le car de six heures ---------------------------------------------------

  /** L'ouverture : le car de six heures entre au terminus, le bonhomme en
      descend, et le narrateur dit d'ou l'on vient.

      ⚠️ ELLE EST UNE SCENE COMME LES AUTRES. Ses plans sont dans `missions.py`
      (`SCENE_OUVERTURE`) et c'est `Scenes` qui les joue : ici, on ne fait que lui
      donner ses deux lieux et ses quatre phrases. Elle a ete ecrite en dur (265
      lignes) jusqu'au 16 sept. 2026 ; la reecrire dans le vocabulaire sans
      toucher un seul de ses treize juges est la preuve que les plans suffisent.

      ⚠️ ET ELLE NE PART PAS AU CHARGEMENT DE LA PAGE : le navigateur retient le
      son tant que personne n'a touche, et une introduction audio muette n'est
      pas une introduction. C'est `Jeu.jouer()` qui l'appelle, apres le geste.

      Rend `false` si la scene est impossible (pas de rue devant le terminus) :
      la partie commence alors comme avant, sans rien dire. */
  function ouverture(rejoue) {
    const j = B.joueur;
    if (!j || B.scene || B.interieur) return false;
    const scene = B.defs.scenes && B.defs.scenes.ouverture;
    const porte = lieu('terminus');
    const arret = porte && tuileDeRue(porte.x, porte.y, 10);
    if (!scene || !porte || !arret || !Vehicules.vehiculeDef('autobus')) return false;
    // ⚠️ DEUX ENDROITS, ET ILS NE SONT LE MEME QU'AU PREMIER MATIN. `quai` est la
    // ou l'on descend du car ; la scene, elle, ramene toujours le joueur la ou il
    // etait (`Scenes`, « elle ne deplace pas le joueur »).
    //   - Partie neuve : on descend LA OU L'ON SERAIT NE sans l'ouverture — c'est
    //     ce qui fait qu'une partie avec l'ouverture est exactement celle qu'on
    //     aurait sans.
    //   - REVUE du carnet : on est peut-etre a l'autre bout de la ville. La scene
    //     se joue quand meme au terminus (c'est la qu'est le car), le bonhomme y
    //     est prete le temps de la revoir, et il revient chez lui a la derniere
    //     image.
    const chezLui = { x: j.x, y: j.y };
    const quai = rejoue ? { x: porte.x, y: porte.y } : chezLui;
    // ⚠️ Les phrases viennent du PAQUET (`missions.repliques_ouverture()`), avec
    // leur slug de voix deja calcule : le navigateur ne refait pas la regle.
    const lignes = (B.defs.ouverture || []).map(function (l) {
      return { qui: l.qui, texte: l.texte, telephone: false, slug: l.slug };
    });
    const etat = Scenes.jouer(scene, {
      lieux: { arret: { x: arret.x, y: arret.y, sens: arret.sens }, quai: quai },
      lignes: lignes, anonyme: true, voix: 'ouverture',
      fin: function () { finirOuverture(!!rejoue); },
    });
    if (!etat) return false;
    B.ouverture = etat;
    etat.arret = { x: arret.x, y: arret.y };
    etat.quai = quai;
    etat.rejoue = !!rejoue;
    if (B.scene !== etat) B.ouverture = null;              // tout a saute d'un coup
    return true;
  }

  /** Les mp3 sans lesquels l'ouverture se joue muette : sa musique et ses
      quatre voix. ⚠️ Lus dans le PAQUET : un fichier absent n'y est pas declare
      (`audio.exporter`), donc on ne prechauffe jamais un 404. */
  function fichiersDeLOuverture() {
    const a = (B.defs && B.defs.audio) || {};
    const sortie = [];
    const mus = (a.musiques || []).find(function (m) { return m.slug === 'ouverture'; });
    if (mus && mus.fichier) sortie.push(mus.fichier);
    (a.histoire || []).forEach(function (v) { if (v.mission === 'ouverture' && v.fichier) sortie.push(v.fichier); });
    return sortie;
  }

  /** PASSER : c'est la scene qui sait ou l'on tombe. ⚠️ Une ouverture qu'on ne
      peut pas passer devient une punition a la deuxieme partie. */
  function passerOuverture() {
    if (!B.ouverture) return false;
    return Scenes.passer();
  }

  function finirOuverture(rejoue) {
    B.ouverture = null;
    // ⚠️ ELLE NE SE REJOUE PAS. Le drapeau part dans la sauvegarde tout de
    // suite : quelqu'un qui regarde l'ouverture puis ferme l'onglet ne doit pas
    // la revoir a son retour. Il la revoit quand IL le demande (le carnet).
    if (!rejoue && B.partie) {
      B.partie.ouvertureVue = true;
      if (typeof Missions !== 'undefined' && Missions.sauvegarderPartie) Missions.sauvegarderPartie();
      Hud.message('BAIE-DES-BRUMES', 150);
      // ⚠️ LES COMMANDES, AU MOMENT OU ON LES REND : la scene finie, on tient
      // enfin le bonhomme — c'est la qu'on a besoin de savoir sur quoi peser.
      // Pas avant (la scene dit elle-meme ACTION et FRAPPE), pas a la revue du
      // carnet (on sait deja jouer).
      Hud.ouvrirCommandes();
    }
  }

  // --- Le telephone ------------------------------------------------------------------------

  /** Le combine sonne, puis on decroche. `B.sonnerie` tient qui appelle et a
      quelle image la sonnerie se tait.

      ⚠️ **LE DIALOGUE ATTEND LA FIN DE LA SONNERIE.** Demande de Martin
      (17 sept. 2026) : « quand on reçoit des appels, le dialogue commence après
      la fin de la sonnerie ». La premiere replique partait dans la MEME image
      que `Son.SFX.telephone()` : le combine sonnait deux secondes par-dessus la
      voix du donneur — on l'entendait parler avant d'avoir decroche.

      ⚠️ La sonnerie n'est PAS dans la partie (`B`, pas `p`) : deux secondes de
      telephone n'ont rien a faire dans une sauvegarde. Et `p.appels` ne se
      marque qu'au DECROCHAGE — fermer l'onglet pendant que ca sonne refait
      sonner l'appel plus tard au lieu de le perdre pour de bon. */
  function majTelephone() {
    const p = B.partie;
    if (B.cinema || p.mission || B.interieur || B.finEnAttente) return;
    if (B.sonnerie) {
      if (B.t < B.sonnerie.t) return;                     // ca sonne encore : on ne decroche pas
      const m = mission(B.sonnerie.slug);
      B.sonnerie = null;
      // ⚠️ On a pu aller voir le donneur pendant que ca sonnait : un appel qui
      // annonce une mission deja prise (ou deja annoncee) ne se dit pas.
      if (!m || p.appels[m.slug] || !disponibles().some(function (x) { return x.slug === m.slug; })) return;
      p.appels[m.slug] = true;
      dire(m, 'appel', function () { Hud.message('VA VOIR ' + personnage(m.donneur).nom.toUpperCase(), 180); });
      return;
    }
    const prochaine = disponibles().find(function (m) { return m.prerequis.length && m.dialogue.appel.length && !p.appels[m.slug]; });
    if (!prochaine) return;
    if (p.appelT === undefined || p.appelT === null) { p.appelT = B.t + DELAI_APPEL; return; }
    if (B.t < p.appelT) return;
    p.appelT = null;
    // `Son.SFX.telephone()` rend ce que dure la sonnerie, en secondes (le mp3,
    // ou les trois bips de la synthese) ; 60 images font une seconde, et une
    // image au moins : le dialogue ne part jamais dans celle ou ca sonne.
    B.sonnerie = { slug: prochaine.slug, t: B.t + Math.max(1, Math.round((Son.SFX.telephone() || 0) * 60)) };
  }

  // --- Parler a quelqu'un -----------------------------------------------------------------

  /** ACTION pres d'un personnage (ou sur son point, dedans). Rend true si ca a fait quelque chose. */
  function parler(slug) {
    const p = personnage(slug);
    if (!p || B.cinema) return false;
    rencontrer(slug);
    const enCours = courante();
    // ⚠️ L'objectif `parler` d'une mission : on l'accomplit en parlant a SA
    // cible, pas au donneur. m6 t'envoie serrer la main de quatre personnes :
    // c'est la poignee qui compte, et elle est ICI, dans le moteur.
    if (enCours) {
      const o = objectif();
      if (o && o.type === 'parler' && cibleDuParler(o) === slug) {
        // ⚠️ LA POIGNEE DE MAIN SE DIT quand la fiche ecrit une replique `accueil` pour cette cible :
        // elle parle, puis l'objectif avance (`dire` appelle `fin` une fois la boite fermee, et tout
        // de suite quand il n'y a rien a dire — la poignee muette d'avant).
        const etape = B.partie.mission.etape;
        dire(enCours, 'accueil', function () { avancer(); }, function (l) { return l.qui === slug && l.objectif === etape; });
        return true;
      }
      // ⚠️ RENVOYE : on parle a quelqu'un dont ce n'est pas encore le tour. Sa replique `renvoi`
      // (`missions.py`) est accrochee a l'objectif en cours — Lulu, de jour, dit d'attendre la
      // noirceur — au lieu du texte de repos que tout le monde dit sans voix. Une mission qui n'en
      // ecrit pas garde le comportement d'avant.
      const etape = B.partie.mission.etape;
      if (dire(enCours, 'renvoi', null, function (l) { return l.qui === slug && l.objectif === etape; })) return true;
    }
    if (enCours && enCours.donneur === slug) {
      const o = objectif();
      if (o && o.type === 'retourner') { reussir(); return true; }
      Hud.message(objectif() ? objectif().texte : '', 150);
      return true;
    }
    const m = disponibleDe(slug);
    if (m) { poserPuisDireLIntro(m); return true; }
    const mn = B.defs.marche_noir;
    if (mn && slug === 'josee' && faite(mn.apres)) { Hud.ouvrirMenu(Missions.menuMarcheNoir()); return true; }
    const repos = B.defs.repos || {};
    const apres = !!(repos.apres && faite(repos.apres));
    // ⚠️ Le repos se DIT aussi : `<qui>-repos-1` avant `repos.apres`, `-2` ensuite (`missions.
    // repliques_de_repos`). Sans le mp3 (pas encore genere), la boite reste muette — le filet.
    const voix = slug + '-repos-' + (apres ? 2 : 1);
    const dite = Son.Voix.histoire().some(function (v) { return v.slug === voix && v.fichier; });
    Hud.dialogue(p.nom, [apres ? repos.texte_apres : (repos.texte || 'REVIENS ME VOIR PLUS TARD.')], dite ? 220 : 120,
                 { slug: slug, humeur: 'neutre' });
    if (dite) { Son.Voix.chargerHistoire('repos'); if (Son.Voix.parler(voix, {}) && B.dialogue) B.dialogue.voix = true; }
    return true;
  }

  /** Ce que fait un donneur qui nous confie sa mission : elle se pose, puis son
      intro se dit, puis elle s'annonce.

      ⚠️ LA MISSION SE POSE AVANT SA SCENE D'INTRO. Quand Madame Thibodeau
      parle de ses deux Cravates, ils doivent exister : une scene qui va les
      voir filmerait sinon un coin vide. Ce n'est pas un de de deplace — la
      ville est figee pendant qu'on parle et le dialogue n'en tire aucun, donc
      les tirages de `poser()` tombent dans le meme ordre. Ce qui s'ANNONCE
      (le titre, l'objectif, le coup de cuivre) attend, lui, la fin de l'intro. */
  function poserPuisDireLIntro(m) {
    commencer(m.slug, true);
    jouerOuDire(m, 'intro', function () { annoncer(m); });
  }

  /** LANCE une mission comme si son donneur venait de nous parler, sans regarder
      ce qu'il faut avoir fait avant (triche de debug : `Hud.menuSautMissions`).

      Celle qui est en cours, quelle qu'elle soit, est abandonnee proprement —
      sans compter d'echec ; celle qu'on lance, deja faite, redevient a faire.
      ⚠️ Rien n'est pris pour un pre-requis : lancer M6 sans M5 donne la mission
      dans l'etat ou la partie est, pas dans celui ou elle aurait du etre. */
  function demarrer(slug) {
    const m = mission(slug);
    if (!m || !B.partie) return false;
    abandonner();
    reinitialiser(slug);
    rencontrer(m.donneur);
    poserPuisDireLIntro(m);
    return true;
  }

  // --- Les scenes des missions ----------------------------------------------------------

  /** Le moment se prete-t-il a une scene ? ⚠️ JAMAIS EN PLEINE ACTION : ni a 3★
      et plus, ni au volant d'un char qui roule, ni pendant un fondu de porte. */
  function calme() {
    const j = B.joueur, v = j && j.dansVehicule;
    return !!j && (B.recherche.etoiles || 0) < 3 && !(v && Math.abs(v.vitesse || 0) > 0.2) && !B.transition && !B.scene;
  }

  /** Une partie d'une mission : sa SCENE (`missions.py`, `scenes`) si elle en a
      une et que le moment s'y prete, sinon ses repliques seules. `acteurs` : ce que
      la scene peut nommer en plus de ce que la mission a pose. */
  function jouerOuDire(m, partie, fin, acteurs) {
    const scene = m.scenes && m.scenes[partie];
    if (scene && calme()) {
      const bm = B.mission || {};
      const etat = Scenes.jouer(scene, {
        mission: m, voix: m.slug, lignes: lignesDe(m, partie), fin: fin,
        // ⚠️ Ceux qui ARRIVENT (`loin`) n'existent pas encore : `cible` nomme alors le
        // point d'où ils viendront, et la caméra peut aller le voir.
        lieux: bm.arrivee ? { cible: bm.arrivee } : {},
        acteurs: Object.assign({
          vehicule: bm.vehicule || null, fuyard: bm.fuyard || null,
          cible: (bm.entites || []).find(function (e) { return e.cible && e.vivant; }) || null,
        }, acteurs || {}),
      });
      if (etat) return true;
    }
    return dire(m, partie, fin);
  }

  /** La scene de fin, quand le moment s'y prete. ⚠️ Ce qu'on gagne est deja
      accorde (`reussir`) : rien ne depend de l'avoir regardee. La scene attend
      seulement qu'on soit a l'arret et hors poursuite. */
  function jouerLaFin() {
    const f = B.finEnAttente;
    if (!f || B.cinema || B.scene) return;
    const m = mission(f.slug);
    if (!m) { B.finEnAttente = null; return; }
    if (m.scenes && m.scenes.fin && !calme()) return;
    B.finEnAttente = null;
    const d = m.donne || {};
    jouerOuDire(m, 'fin', function () {
      if (d.message) Hud.message(d.message, 200);
      // ⚠️ **QUI S'EN VA EST DANS LES DONNEES** (`parti_apres`), pas dans la
      // scene. `creerDonneurs` ne le repose deja plus a la partie suivante, mais
      // rien ne le retirait de CELLE-CI : c'est la scene ecrite de M1 qui le
      // faisait entrer au garage, et une mission qui n'ecrit pas la sienne
      // laissait son donneur plante devant sa porte jusqu'au rechargement.
      // Ici, aucun slug ne s'ecrit : la fiche dit apres quelle mission il part.
      for (const p of personnages()) {
        if (p.parti_apres !== m.slug) continue;
        const e = donneur(p.slug);
        if (e) Entites.retirer(e);
      }
      Missions.sauvegarderPartie();
    }, { vehicule: f.vehicule });
  }

  // --- Les missions ------------------------------------------------------------------------

  function objectif() {
    const m = courante();
    return m ? m.objectifs[B.partie.mission.etape] || null : null;
  }

  /** `enSilence` : posee sans rien annoncer — son intro va se dire par-dessus,
      et c'est `annoncer` qui parlera quand elle sera finie. */
  function commencer(slug, enSilence) {
    const m = mission(slug);
    if (!m || B.partie.mission) return false;
    B.partie.mission = { slug: slug, etape: -1, t: B.t, chocs: 0 };
    B.mission = { entites: [], vehicule: null, chars: {}, fuyard: null, chef: null, escorte: null, courses: 0, kos: 0,
                  vol: 0, boulotsDepart: 0, suit: null, protege: null, suivi: null };
    if (!enSilence) { Hud.message(m.titre.toUpperCase(), 180); Son.SFX.mission(); }
    avancer(enSilence);
    return true;
  }

  /** Ce que `commencer` aurait dit : le titre, le coup de cuivre, l'objectif. */
  function annoncer(m) {
    const o = objectif();
    if (!B.partie.mission || B.partie.mission.slug !== m.slug) return;
    Hud.message(m.titre.toUpperCase(), 180);
    Son.SFX.mission();
    if (o) Hud.message(o.texte, 200);
    // ⚠️ La réplique PENDANT du premier objectif : `avancer(true)` ne l'arme pas (il
    // se tait sous l'intro) — elle attendait ici, et ne se disait jamais (m6, m54, e02…).
    if (o && B.mission && (m.dialogue.pendant || []).some(function (l) { return l.objectif === B.partie.mission.etape; })) {
      B.mission.pendant = B.partie.mission.etape;
    }
    faireArriver(m, o);
  }

  /** Ce que l'intro a fait attendre : les hommes d'un `tuer` qui `arrivent`
      naissent MAINTENANT, quand le donneur a fini de parler — pas pendant qu'il
      parle, collés à lui. */
  function faireArriver(m, o) {
    if (!B.mission || !B.mission.arrivee || !o || o.type !== 'tuer') return;
    dansLaVille(function () { poserLesCravates(m, o, false); });
  }

  /** L'objectif suivant. Ce qui se pose en ville se pose TOUT DE SUITE — dans
      la VILLE, même quand on est dans une pièce : la scène d'intro qui coupe
      vers la rue doit y trouver le char ou les Cravates qu'elle montre. */
  function avancer(enSilence) {
    const m = courante(), p = B.partie.mission;
    p.etape++;
    const o = m.objectifs[p.etape];
    if (!o) { reussir(); return; }
    // ⚠️ Tout le monde est deja tombe a un essai rate : l'objectif est FAIT.
    // On ne repose pas des morts pour les recoucher.
    if (o.type === 'tuer' && dejaTombes(m.slug, p.etape) >= o.n) { avancer(enSilence); return; }
    p.debutT = B.t;
    poser(enSilence);
    if (!enSilence) Hud.message(o.texte, 200);
    // La replique PENDANT de cet objectif, des qu'aucune autre ne parle (`maj`).
    if (!enSilence && (m.dialogue.pendant || []).some(function (l) { return l.objectif === p.etape; })) B.mission.pendant = p.etape;
  }

  /** Pose dans la VILLE, même quand on est dans une pièce. ⚠️ La règle des
      scènes : une coupe vers la rue doit y trouver ce que la mission y pose —
      le char d'un `monter`, les Cravates d'un `tuer` — pas une rue vide. Quand
      on est dedans, `Monde.carte` est la pièce et `B.entites` ses gens : le
      temps du placement, on remet la carte et la liste de la ville, on naît au
      bon monde, puis on reprend les deux. */
  function dansLaVille(fn) {
    const ext = B.interieur ? B.exterieur : null;
    if (!ext) { fn(); return; }
    const carte = Monde.carte, entites = B.entites;
    Monde.restaurer(ext.carte);
    B.entites = ext.entites;
    try { fn(); } finally { Monde.restaurer(carte); B.entites = entites; }
  }

  function poser(enSilence) {
    const m = courante(), p = B.partie.mission, j = B.joueur;
    const o = m.objectifs[p.etape];
    if (!o) return;
    // ⚠️ Toujours dans la VILLE, même quand on est dans une pièce : une scène
    // qui coupe vers la rue doit y trouver ce qu'on pose (`dansLaVille`).
    dansLaVille(function () {
      if (o.type === 'monter') {
        const v = poserLeChar(m, o, p.etape);
        if (v) B.mission.vehicule = v;
      } else if (o.type === 'tuer') {
        poserLesCravates(m, o, enSilence);
      } else if (o.type === 'ramasser' && o.cible === 'fuyard') {
        poserLeFuyard(m, o);
      } else if (o.type === 'semer') {
        B.recherche.etoiles = Math.max(B.recherche.etoiles, o.etoiles || 1); B.recherche.vu = 0; B.recherche.flash = 60;
        B.recherche.dernierVu = { x: j.x, y: j.y, t: B.t };
        if (o.escorte) poserLEscorte(m, o);
      } else if (o.type === 'courses') {
        B.mission.courses = 0; B.mission.coursesDepart = Missions.boulot.faits.taxi;
      } else if (o.type === 'boulots') {
        // ⚠️ Le compte part d'ICI : on ne compte QUE les boulots faits pendant
        // la mission, pas ceux d'avant. `sorte` nomme le compteur (`taxi`,
        // `pizza`, `ambulance`, `remorquage`).
        B.mission.boulotsDepart = Missions.boulot.faits[o.sorte] || 0;
      } else if (o.type === 'detruire') {
        // Un char posé exprès à détruire : réutilise `poserLeChar` (le même
        // char, la même `ou`), mais c'est dans `chars` qu'`majObjectif` le
        // surveille, pas `vehicule` (on ne roule pas dedans, on le casse).
        poserLeChar(m, o, p.etape);
      } else if (o.type === 'proteger') {
        // Le personnage à protéger. Il ATTEND qu'on vienne le chercher, puis il
        // nous suit (`majProtege`) — à pied, et dans le char quand on s'arrête
        // près de lui ; sa mort est l'échec `protege_mort`.
        //
        // ⚠️ LE DONNEUR QUI EST LÀ, PAS UN SECOND (22 sept. 2026, p14). On posait
        // un personnage neuf à côté de celui qui attendait déjà : deux
        // Bonimenteurs à l'arche, et `donneur()` rendait le PREMIER, resté
        // planté — les Skateux de `tuer` (`ou: "donneur"`) venaient à la foire
        // pendant qu'on était au poste, et la fin se disait au téléphone à deux
        // pas de lui. Un personnage neuf seulement si personne ne se tient en
        // ville (un donneur `point:`, dedans).
        const p = personnage(o.cible);
        let e = p ? donneur(p.slug) : null;
        if (e) e.chezLui = e.plante ? { x: e.plante.x, y: e.plante.y } : { x: e.x, y: e.y };
        else if (p) {
          const place = ouTrouver(p.slug) || tuileLibre(j.x + 40, j.y, 6);
          if (place) { e = creerPersonnage(p, place.x, place.y); B.mission.entites.push(e); }
        }
        if (e) {
          // ⚠️ `plante` retiré : un fige loin de son poste est un MUR pour la
          // foule (`Entites.cede`), et il le serait deux rues plus loin.
          e.plante = null; e.courage = 0; e.intouchable = false; e.mission = m.slug;
          e.vitesseSuite = B.defs.recherche.vitesses.joueur_sprint;
          B.mission.protege = e;
        }
        Entites.indexer();
      } else if (o.type === 'suivre') {
        poserLeSuivi(m, o);
      } else if (o.type === 'pickpocket') {
        // Un archétype précis, marqué pour le jet des poches : le joueur le
        // vide par-derrière (`Combat.pickpocket`), et `majObjectif` valide
        // quand SES poches sont à nous.
        const arch = Entites.archetype(o.cible);
        const place = tuileLibre(j.x + 60, j.y, 6);
        if (place) {
          const e = Entites.creerPieton(place.x, place.y, arch);
          e.pickpocket = true; e.cible = true; e.mission = m.slug; e.etape = p.etape;
          e.argent = (arch.argent || [10, 30]).reduce(function (a, b) { return a + b; }, 0);  // une bourse lisible
          B.mission.entites.push(e);
          Entites.indexer();
        }
      }
      // ⚠️ **UN CHAR DE MISSION DORT LA AVANT QU'ON EN PARLE.** Il ne naissait
      // qu'au tour de SON objectif : Ti-Guy disait « y a un char qui traine dans
      // une ruelle », la coupe de l'intro allait voir cette ruelle-la — et la
      // filmait VIDE (mesure au banc : 155 images a l'ecran, aucun char a 200 px).
      // Les chars des objectifs qui suivent se posent donc des le debut de la
      // mission ; `poser()`, venu leur tour, retrouve ceux-la (`B.mission.chars`)
      // au lieu d'en creer un second. ⚠️ `B.mission.vehicule`, lui, attend son
      // tour : c'est LUI que `majObjectif` surveille (un char de mission qui
      // saute fait rater), et un char qu'on n'a pas encore eu a chercher n'est
      // pas encore le char de la mission.
      for (let i = p.etape + 1; i < m.objectifs.length; i++) {
        if (m.objectifs[i].type === 'monter') poserLeChar(m, m.objectifs[i], i);
      }
    });
  }

  /** Le char d'un objectif `monter`, la ou il dort. Rend celui qui y est deja
      — pose d'avance — sauf s'il a saute ou quitte la ville entre-temps. */
  function poserLeChar(m, o, etape) {
    const chars = B.mission.chars || (B.mission.chars = {});
    const deja = chars[etape];
    if (deja && deja.etat !== 'epave' && B.entites.indexOf(deja) >= 0) return deja;
    const ou = resoudre(o.ou, m);
    // ⚠️ SUR L'EAU, RIEN NE PASSE PAR `tuileDeRue` : c'est la route qui trouve la
    // rue la plus proche d'un pixel, et la rue la plus proche d'une coque est
    // toujours de l'eau. Le point ET LE CAP viennent tels quels du mouillage
    // (`navires.py`, angle donné) ou de l'amarrage de Sven (`amarrageDeSven`,
    // angle 0 — comme `Vehicules.majAmarrages`, une chaloupe n'en garde pas).
    const surEau = o.ou.indexOf('mouillage:') === 0 || o.ou === 'amarrage:sven';
    const cleAmarrage = ou && (ou.mouillage || ou.amarrage);
    // ⚠️ « PRENDRE LA COQUE », PAS LA DÉDOUBLER (m52-m54, Sven) : le grand bateau
    // ou la chaloupe mouillés là sont du DÉCOR permanent (`Vehicules.majMouillages`,
    // `majAmarrages`), présents avant même que la mission commence. Sans ce test,
    // `Vehicules.creer` en ferait naître un second par-dessus.
    const dejaAmarre = surEau && cleAmarrage && B.entites.find(function (e) { return e.type === 'vehicule' && e.amarrage === cleAmarrage; });
    const rue = ou && !surEau ? (o.ou.indexOf('ruelle:') === 0 ? ou : (tuileDeRue(ou.x, ou.y, 8, sansChar) || tuileDeRue(ou.x, ou.y, 8))) : null;
    const place = rue || ou;
    if (!place) return null;
    const angle = surEau ? (ou.mouillage ? ou.mouillage.angle : 0) : (rue && rue.sens ? CAP_DE_FLECHE[rue.sens] : 0);
    // ⚠️ `aQui` vient de la fiche (`prete` dans `missions.py`), et il ne
    // s'efface JAMAIS : le taxi de Marco est a Marco avant, pendant et
    // apres — c'est lui qui l'empeche d'etre vendu au garage de Ti-Guy,
    // qui est a deux pas de la ou il dort.
    let v;
    if (dejaAmarre) {
      v = dejaAmarre;
      v.mission = m.slug; v.aQui = o.prete || null;
    } else {
      v = Vehicules.creer(o.vehicule, place.x, place.y, angle, { etat: 'stationne', mission: m.slug, aQui: o.prete || null });
      if (!v) return null;
      // ⚠️ LE MOUILLAGE OU L'AMARRAGE EST PRIS : sans `amarrage`, le decor
      // (`Vehicules.majMouillages`/`majAmarrages`) ferait naitre un second
      // bateau par-dessus des qu'on s'eloigne.
      if (surEau) v.amarrage = cleAmarrage;
    }
    chars[etape] = v;
    B.mission.entites.push(v);
    return v;
  }

  // --- Le piratage (M16, demande de Martin, 21 sept. 2026 : « de l'infiltration
  // et du hacking ») -----------------------------------------------------------
  //
  // Une sequence de 4 directions a reproduire, avec le MEME axe unifie que la
  // marche (`Entree.axe` : clavier, manette, joystick tactile) — rien de neuf a
  // apprendre au pouce, et `Combat.creneauVise` (la roue d'armes) sait deja lire
  // un flick de stick comme un cran parmi n. `B.piratage` cloue le joueur
  // (`Entites.majJoueur`) et affame la roue, le combat, l'entree en char et les
  // interactions (memes portes que `B.roue`) : un seul bouton a la fois.

  //: Cran 0 EN HAUT, puis dans le sens des aiguilles — la lecture de `Combat.creneauVise`.
  const DIRS_PIRATAGE = ['haut', 'droite', 'bas', 'gauche'];
  //: Au-dela, un flick COMPTE ; en deca, on est revenu au neutre et le prochain
  //: comptera. Le seuil haut est celui de la roue d'armes (`Combat.ROUE_ZONE_MORTE`,
  //: non exportee — le meme chiffre, 0.45, c'est le meme geste au pouce). Le bas est
  //: plus permissif : sans hysteresis, un stick qui tremble pile sur 0.45 compterait
  //: deux fois le meme flick.
  const PIRATAGE_SEUIL_HAUT = 0.45, PIRATAGE_SEUIL_BAS = 0.22;

  /** L'objectif `pirater` EN COURS, ou null. Un seul a la fois : `p.etape` le dit. */
  function objectifDePiratage() {
    const m = courante(), p = B.partie.mission;
    if (!m || !p) return null;
    const o = m.objectifs[p.etape];
    return o && o.type === 'pirater' ? o : null;
  }

  /** Le terminal d'un piratage en cours, a portee de main — pour le bouton ACTION,
      comme `personnageSousLaMain` et `vehiculeSousLaMain`. `null` si un piratage est
      deja ouvert (rien de neuf a demarrer) ou si on n'est pas assez pres. */
  function piratageSousLaMain(j) {
    if (B.piratage || !j || j.dansVehicule) return null;
    const o = objectifDePiratage();
    if (!o) return null;
    const brut = resoudre(o.ou, courante());
    // ⚠️ Un terminal sur un mouillage se pirate depuis le POSTE (le quai) : le
    // centre que `resoudre` rend pour `mouillage:` est celui de la coque, dans
    // l'eau, où l'on ne marche jamais.
    const l = brut && brut.mouillage ? brut.mouillage.poste : brut;
    if (!l) return null;
    const r = (o.rayon || 3) * TT;
    return dist2(j.x, j.y, l.x, l.y) < r * r ? o : null;
  }

  /** Ouvre le piratage de l'objectif en cours (bouton ACTION, via `Missions.interagir`).
      Rend faux si rien n'est a pirater — `Missions.interagir` passe alors au suivant
      de la chaine, comme pour un personnage ou un vehicule absents. */
  function commencerPiratage() {
    const p = B.partie.mission, o = objectifDePiratage();
    if (!o) return false;
    const longueur = o.longueur || 4, sequence = [];
    for (let i = 0; i < longueur; i++) sequence.push(DIRS_PIRATAGE[Math.floor(B.rng() * DIRS_PIRATAGE.length)]);
    B.piratage = { etape: p.etape, sequence: sequence, pos: 0, ratees: 0, relache: true,
                   essais: o.essais != null ? o.essais : 3 };
    Entree.contexte('piratage');
    Son.SFX.menu();
    return true;
  }

  /** Referme le piratage et REND LE BOUTON A CE QU'IL FAISAIT AVANT — comme
      `Hud.fermerMenu` (`vehicule` au volant, `pied` sinon). Un seul endroit,
      pour ne pas oublier l'etiquette dans un des trois chemins de sortie
      (abandon, reussite, alarme) — ou dans la mission qui se termine ailleurs
      (`nettoyer`). */
  function fermerPiratage() {
    if (!B.piratage) return;
    B.piratage = null;
    Entree.contexte(B.joueur && B.joueur.dansVehicule ? 'vehicule' : 'pied');
  }

  /** Lue a chaque image tant que `B.piratage` est ouvert (depuis `majObjectif`,
      cas `pirater`). ⚠️ FRAPPE ABANDONNE (comme `Combat.majRoue` referme la roue
      au relachement d'ARME) : on garde ce qu'on a fait, on peut revenir. */
  function majPiratage() {
    const r = B.piratage;
    if (Entree.neuf('attaque')) { fermerPiratage(); return; }
    const mag = Entree.axe.mag;
    if (r.relache && mag > PIRATAGE_SEUIL_HAUT) {
      r.relache = false;
      const cran = Combat.creneauVise(Entree.axe, DIRS_PIRATAGE.length);
      const dir = cran >= 0 ? DIRS_PIRATAGE[cran] : null;
      if (dir === r.sequence[r.pos]) {
        r.pos++;
        Son.SFX.menu();
        if (r.pos >= r.sequence.length) { fermerPiratage(); avancer(); }
      } else if (dir) {
        r.pos = 0; r.ratees++;
        Son.SFX.erreur();
        if (r.ratees > r.essais) { fermerPiratage(); echouer('alarme'); }
      }
    } else if (mag < PIRATAGE_SEUIL_BAS) {
      r.relache = true;
    }
  }

  /** Où naissent des hommes qui ARRIVENT (`loin`, en tuiles) : à cette distance
      du joueur, sur un sol où l'on marche, et avec une ligne droite libre
      jusqu'à lui — `attaque_joueur` marche droit et ne contourne aucun mur.

      ⚠️ AUCUN DÉ : les seize directions se prennent dans un ordre fixe, de la
      plus lointaine à la plus proche, pour que jouer la scène ou la passer donne
      la même ville. Hors de l'écran d'abord ; à l'écran seulement s'il n'y a
      que ça. ⚠️ Pas plus loin que 16 tuiles : au-delà de 260 px, `attaque_joueur`
      renonce à la première image.

      `null` : dedans (le joueur n'a pas de coordonnées de ville) ou nulle part. */
  function placeDArrivee(loin) {
    const j = B.joueur;
    if (B.interieur) return null;
    for (const horsChamp of [true, false]) {
      for (let r = loin; r >= loin - 3; r--) {
        for (let k = 0; k < 16; k++) {
          const a = k * Math.PI / 8;
          const tx = Math.floor((j.x + Math.cos(a) * r * TT) / TT), ty = Math.floor((j.y + Math.sin(a) * r * TT) / TT);
          if (!Monde.marchablePieton(tx, ty)) continue;
          const place = { x: tx * TT + 8, y: ty * TT + 8 };
          if (horsChamp && Entites.visibleAEcran(place.x, place.y, 8)) continue;
          if (Monde.ligneLibre(place.x, place.y, j.x, j.y)) return place;
        }
      }
    }
    return null;
  }

  /** `enSilence` : l'intro va se dire. Ceux qui `arrivent` (`loin`) attendent la fin
      de la scène (`faireArriver`) : leur point de naissance est choisi tout de suite —
      la caméra de l'intro peut aller le voir (`cible`) —, eux naissent plus tard. */
  function poserLesCravates(m, o, enSilence) {
    const gang = B.defs.pietons.gangs.find(function (g) { return g.slug === o.groupe; });
    if (!gang) return;
    const arch = Entites.archetype(gang.pieton);
    const coins = o.coins || 1;
    const etape = B.partie.mission.etape, parCoin = tombesDe(m.slug, etape);
    const reste = o.n - dejaTombes(m.slug, etape);
    B.mission.kos = o.n - reste;
    if (reste <= 0) return;
    const arrivee = o.loin ? B.mission.arrivee || placeDArrivee(o.loin) : null;
    if (arrivee && enSilence) { B.mission.arrivee = arrivee; return; }
    const centre = arrivee || (o.chef ? { x: B.joueur.x, y: B.joueur.y } : resoudre(o.ou, m) || { x: B.joueur.x, y: B.joueur.y });
    // Côte à côte, en travers de leur route : le second n'est pas derrière le premier.
    const dx = B.joueur.x - centre.x, dy = B.joueur.y - centre.y, norme = Math.hypot(dx, dy) || 1;
    for (let c = 0; c < coins; c++) {
      const a = c / coins * Math.PI * 2;
      const cx = coins > 1 ? centre.x + Math.cos(a) * 120 : centre.x, cy = coins > 1 ? centre.y + Math.sin(a) * 120 : centre.y;
      // ⚠️ Un coin qu'on a vide reste vide : on n'y repose que ce qui
      // manquait encore a son compte.
      for (let i = parCoin[c] || 0; i < Math.ceil(o.n / coins); i++) {
        const place = arrivee ? tuileLibre(cx - dy / norme * i * 18, cy + dx / norme * i * 18, 2)
                              : tuileLibre(cx + (i - 1) * 20 + 40, cy + 10, 6);
        if (!place) continue;
        const e = Entites.creerPieton(place.x, place.y, arch);
        e.cible = true; e.mission = m.slug; e.courage = 1; e.etat = 'flane';
        e.etape = etape; e.coin = c;
        // ⚠️ Ils ARRIVENT sur le joueur : à la course, tout de suite, un cri au-dessus de
        // la tête. `alerter` ne le ferait qu'autour de `centre`, et ne réveille que ceux
        // qui ont une ligne libre jusqu'à lui — ici, on le sait déjà.
        if (arrivee) { e.etat = 'attaque_joueur'; e.cri = 90; }
        // ⚠️ CE QUE PORTE UN HOMME DE MISSION VIENT DE LA FICHE, pas de
        // l'archetype. `arme` et `vie` sont facultatives (`missions.py`) et ne
        // valent que pour CES hommes-la : la Cravate de rue reste ce qu'elle
        // est — elle tient le Faubourg en M5 et vient encaisser la dette de
        // Rocco. ⚠️ `''` veut dire les poings, et il faut donc tester
        // `!== undefined` : un `||` rendrait le baton a qui vient les mains
        // vides, ce qui est exactement le bogue qu'on repare.
        if (o.arme !== undefined) e.arme = o.arme || null;
        if (o.vie) { e.vie = e.vieMax = o.vie; }
        if (o.chef) {
          e.chef = true; e.vie = e.vieMax = 160; e.arme = 'batte'; e.swaps = Object.assign({}, e.swaps, { c: '#101018' });
          // Habille (`Garderobe`), c'est sa TENUE qui se dessine : le chef la porte en noir aussi.
          if (e.tenue) e.tenue = Object.assign({}, e.tenue, { couleur_haut: '#101018' });
        }
        B.mission.entites.push(e);
        if (B.mission.entites.filter(function (q) { return q.cible && q.etape === etape && q.vivant && q.etat !== 'assomme'; }).length >= reste) break;
      }
    }
    Entites.indexer();
    if (arrivee) B.mission.arrivee = null;
    else Entites.alerter(centre.x, centre.y, B.joueur, 1);     // ils t'ont vu venir
  }

  function poserLeFuyard(m, o) {
    // ⚠️ Le fuyard naît dans la ville, près de la porte quand on est dedans (m50 : Lulu le
    // voit filer depuis la cantine), et pas dans le char qu'on a garé devant elle.
    const ici = ouEstLeJoueurEnVille();
    const rue = tuileDeRue(ici.x, ici.y, 10, sansChar) || tuileDeRue(ici.x, ici.y, 10);
    if (!rue) return;
    const angle = { '>': 0, '<': Math.PI, '^': -Math.PI / 2, 'v': Math.PI / 2 }[rue.sens];
    const v = Vehicules.creer(o.vehicule || 'moto', rue.x, rue.y, angle, { conducteur: 'trafic', etat: 'roule', poursuite: true, fuite: true, sens: rue.sens, mission: m.slug, fuyard: true });
    if (!v) return;
    v.vitesse = 1.5;
    B.mission.vehicule = v; B.mission.fuyard = v; B.mission.entites.push(v);
    Hud.message('LE FUYARD FILE EN MOTO !', 150);
  }

  /** Aucun char dans la voie, sur `n` tuiles devant cette place (ou jusqu'au
      croisement, là où la voie change de sens). */
  function voieLibreDevant(place, n) {
    const pas = { '>': [1, 0], '<': [-1, 0], '^': [0, -1], 'v': [0, 1] }[place.sens];
    const tx = Math.floor(place.x / TT), ty = Math.floor(place.y / TT);
    for (let k = 1; k <= n; k++) {
      const x = tx + pas[0] * k, y = ty + pas[1] * k;
      if (Monde.fleche(x, y) !== place.sens) return true;
      const cx = x * TT + 8, cy = y * TT + 8;
      if (B.entites.some(function (e) { return e.type === 'vehicule' && dist2(e.x, e.y, cx, cy) < 20 * 20; })) return false;
    }
    return true;
  }

  //: Celui qu'on file (`suivre`) : combien de temps il t'attend au volant, combien la
  //: méfiance monte avant qu'il te repère, et le temps de le retrouver quand on l'a
  //: perdu — les cinq secondes du tracé des courses.
  const SUIVI_ATTENTE = 45 * 60, SUIVI_MEFIANCE = 90, SUIVI_PERDU = 300;

  /** Celui qu'on FILE (`suivre`) : un char qui VA quelque part, pas un fuyard.

      ⚠️ Martin, 22 sept. 2026 : « impossible à faire, on se fait voir tout de suite en
      sortant de la cantine ». `suivre` posait le fuyard de m50 (`poserLeFuyard`) : sur la
      tuile de rue la plus proche de la porte du casse-croûte, à 44 px — sous `proche`
      (3 tuiles, 48 px) —, et l'échec tombait à la première image dehors. Et il FUYAIT
      (`fuite` et `poursuite` : les feux brûlés, la sortie qui s'éloigne de toi) : à
      pied, le temps de trouver un char, il était à plus de `loin`.

      Il naît donc à bonne distance, entre `proche` et `loin`, sur une voie libre devant
      lui, moteur en marche, et attend que tu sois au volant (`attendLeJoueur`). Puis il
      roule comme le trafic — feux, stops, vitesse de ville — vers le `lieu` de
      l'objectif : la voie la plus proche de sa porte (`destination`, que `Vehicules`
      suit aux croisements). */
  function poserLeSuivi(m, o) {
    const ici = ouEstLeJoueurEnVille();
    const min = ((o.proche || 3) + 2) * TT;
    const assezLoin = function (place) { return dist2(place.x, place.y, ici.x, ici.y) >= min * min; };
    const rayon = Math.max((o.loin || 10) - 2, (o.proche || 3) + 4);
    // ⚠️ Et la voie LIBRE devant lui : on se gare devant la porte, sur la rue — il
    // naissait en amont de notre char, dans la même voie, et restait coincé derrière
    // lui quinze secondes avant de le pousser.
    const rue = tuileDeRue(ici.x, ici.y, rayon, function (place) { return assezLoin(place) && sansChar(place) && voieLibreDevant(place, 8); })
      || tuileDeRue(ici.x, ici.y, rayon, function (place) { return assezLoin(place) && sansChar(place); })
      || tuileDeRue(ici.x, ici.y, rayon, assezLoin);
    if (!rue) return;
    const v = Vehicules.creer(o.vehicule || 'auto', rue.x, rue.y, CAP_DE_FLECHE[rue.sens], { conducteur: 'trafic', etat: 'roule', sens: rue.sens, mission: m.slug, suivi: true });
    if (!v) return;
    v.vitesse = 0; v.attendLeJoueur = true;
    // Ses étapes : le détour (`par`, Martin : « je veux que ce soit plus long »), puis
    // le `lieu`. Chacune est la voie la plus proche de sa porte ; `destination` est la
    // prochaine, et passe à la suivante quand il y arrive.
    const etapes = (o.par || []).concat(o.lieu ? [o.lieu] : []).map(function (slug) {
      const l = lieu(slug);
      return l ? Monde.routeLaPlusProche(l.x, l.y, 10) : null;
    }).filter(Boolean);
    v.destination = etapes.shift() || null;
    B.mission.etapesDuSuivi = etapes;
    B.mission.suivi = v; B.mission.entites.push(v);
    B.mission.suiviAttente = 0; B.mission.mefiance = 0; B.mission.perdu = 0;
  }

  /** Ti-Guy (M4) « te suit en char » : il nait DERRIERE le char du joueur, dans
      une voie qui roule dans le meme sens que lui.

      ⚠️ La tuile de rue la plus proche du joueur etait le plus souvent celle de
      DEVANT : il naissait 28 px devant l'auto-patrouille, dans sa voie, le nez
      dans le meme sens — et comme l'escorte s'arrete a 70 px du joueur
      (`Vehicules.majConducteur`), il restait plante la, a boucher la rue qu'il
      devait couvrir. Derriere, dans une voie qui va ou l'on va, il n'a qu'a
      rouler : le trafic en poursuite choisit ses sorties vers le joueur. */
  function placeDerriere(j) {
    const c = j.dansVehicule;
    if (!c) return null;
    const hx = Math.cos(c.angle), hy = Math.sin(c.angle);
    let meilleure = null, note = Infinity;
    const tx = Math.floor(c.x / TT), ty = Math.floor(c.y / TT);
    for (let dy = -10; dy <= 10; dy++) for (let dx = -10; dx <= 10; dx++) {
      const f = Monde.fleche(tx + dx, ty + dy);
      if (CAP_DE_FLECHE[f] === undefined) continue;
      const place = { x: (tx + dx) * TT + 8, y: (ty + dy) * TT + 8, sens: f };
      const ox = place.x - c.x, oy = place.y - c.y;
      const recul = -(ox * hx + oy * hy), cote = Math.abs(-ox * hy + oy * hx);
      if (recul < 40 || !sansChar(place)) continue;
      const memeSens = Math.cos(CAP_DE_FLECHE[f] - c.angle) > 0.7;
      const n = (memeSens ? 0 : 1000) + Math.abs(recul - 72) + cote * 2;
      if (n < note) { note = n; meilleure = place; }
    }
    return meilleure;
  }

  function poserLEscorte(m, o) {
    const j = B.joueur;
    const rue = placeDerriere(j) || tuileDeRue(j.x, j.y, 10, sansChar) || tuileDeRue(j.x, j.y, 10);
    if (!rue) return;
    const angle = CAP_DE_FLECHE[rue.sens];
    const v = Vehicules.creer('auto', rue.x, rue.y, angle, { conducteur: 'trafic', etat: 'roule', poursuite: true, escorte: true, sens: rue.sens, mission: m.slug, couleur: '#2e8b57' });
    if (!v) return;
    B.mission.escorte = v; B.mission.entites.push(v);
  }

  /** Le fuyard « tombe » : la moto s'arrete ou casse, un Cravate en descend avec la caisse. */
  function faireTomberLeFuyard() {
    const v = B.mission.fuyard;
    if (!v || B.mission.fuyardTombe) return;
    B.mission.fuyardTombe = true;
    v.conducteur = null; v.etat = v.etat === 'epave' ? 'epave' : 'stationne'; v.fuite = false; v.poursuite = false;
    const gang = B.defs.pietons.gangs[0];
    const place = tuileLibre(v.x, v.y, 4) || { x: v.x + 12, y: v.y };
    const e = Entites.creerPieton(place.x, place.y, Entites.archetype(gang.pieton));
    e.cible = true; e.mission = B.partie.mission.slug; e.porteLaCaisse = true; e.etat = 'fuit'; e.menace = B.joueur; e.minuterie = 9999; e.courage = 0;
    B.mission.entites.push(e);
    Entites.indexer();
    Hud.message('IL A LA CAISSE — ATTRAPE-LE !', 150);
  }

  function lacherLaCaisse(e) {
    if (!e.porteLaCaisse) return;
    e.porteLaCaisse = false;
    const c = Entites.creer('ramassage', e.x + 6, e.y + 4, { r: 4, objet: 'caisse', t: 0, solide: false, mission: B.partie.mission.slug });
    B.mission.entites.push(c);
  }

  /** Le chef sort quand ses gars sont tombes : `tuer` avec `chef` se pose au moment venu. */
  function majObjectif() {
    const m = courante(), p = B.partie.mission, j = B.joueur;
    const o = m.objectifs[p.etape];
    if (!o) return;
    // ⚠️ LE CHAR DE LA MISSION A SAUTE : c'est rate, QUEL QUE SOIT l'objectif.
    // Seuls `monter` et `livrer` le regardaient : le taxi de Marco explosait
    // pendant les courses, l'auto-patrouille de M4 pendant qu'on semait, et la
    // mission continuait sans char jusqu'a la livraison. Le fuyard de M2 n'en
    // est pas un (on le casse expres), ni un char deja livre (`mission: null`).
    const mv = B.mission.vehicule;
    if (mv && mv.etat === 'epave' && mv.mission === m.slug && !mv.fuyard && m.echec.indexOf('vehicule_detruit') >= 0) {
      echouer('vehicule_detruit');
      return;
    }
    // ⚠️ M16 — les options qui TRAVERSENT tout objectif (`OPTIONS_OBJECTIFS`).
    // `chrono_s` : le chrono sur n'importe lequel (le défi l'avait, la mission
    // non). `debutT` est posé dans `avancer()` ; `* 60` convertit en images.
    if (o.chrono_s && B.t - p.debutT > o.chrono_s * 60) { echouer('chrono'); return; }
    // `sans_etoile` : échec `etoile` dès qu'on est vu (les missions discrètes).
    if (o.sans_etoile && B.recherche.etoiles > 0) { echouer('etoile'); return; }
    switch (o.type) {
      case 'aller': {
        if (o.nuit && !Monde.estNuit()) { B.mission.attend = 'ATTENDS LA NUIT'; return; }
        B.mission.attend = null;
        const l = lieu(o.lieu);
        if (l && dist2(j.x, j.y, l.x, l.y) < (o.rayon * TT) * (o.rayon * TT)) avancer();
        return;
      }
      case 'monter': {
        const v = B.mission.vehicule;
        if (!v) { avancer(); return; }
        if (v.etat === 'epave') { echouer('vehicule_detruit'); return; }
        if (j.dansVehicule === v) { p.chocs = v.chocs; avancer(); }
        return;
      }
      case 'livrer': {
        const v = B.mission.vehicule || j.dansVehicule;
        if (!v || v.etat === 'epave') { echouer('vehicule_detruit'); return; }
        const l = lieuDeLivraison(o.lieu);
        if (j.dansVehicule === v && l && dist2(v.x, v.y, l.x, l.y) < (o.rayon * TT) * (o.rayon * TT) && Math.abs(v.vitesse) < 0.4) {
          B.mission.sansBosse = o.sans_degats && v.chocs === p.chocs && v.vie === v.vieMax;
          Vehicules.descendre(j, true);
          v.mission = null; v.vole = false; v.conducteur = null; v.etat = 'stationne';
          B.mission.entites = B.mission.entites.filter(function (e) { return e !== v; });
          avancer();
        }
        return;
      }
      case 'tuer': {
        // ⚠️ Les cibles de CET objectif, pas de toute la mission : les six du
        // premier objectif de m5 sont encore au sol quand le chef sort, et
        // comptees avec lui elles le couchaient avant qu'il ait fait un pas.
        const cibles = B.mission.entites.filter(function (e) { return e.type === 'pieton' && e.cible && !e.porteLaCaisse && e.etape === p.etape; });
        const tombes = cibles.filter(function (e) { return !e.vivant || e.etat === 'assomme'; }).length;
        const avant = dejaTombes(m.slug, p.etape);
        B.mission.kos = Math.min(o.n, avant + tombes);
        if (cibles.length && tombes >= Math.min(o.n - avant, cibles.length)) {
          if (o.chef && B.recherche.etoiles < 3 && m.objectifs[p.etape + 1] && m.objectifs[p.etape + 1].type === 'semer') Hud.message('UN TÉMOIN A APPELÉ LA POLICE !', 150);
          avancer();
        }
        return;
      }
      case 'ramasser': {
        const v = B.mission.fuyard;
        if (v && !B.mission.fuyardTombe) {
          const pres = j.dansVehicule ? j.dansVehicule : j;
          const d = Math.hypot(v.x - pres.x, v.y - pres.y);
          if (v.etat === 'epave' || (d < 40 && Math.abs(v.vitesse) < 0.6) || v.vie < v.vieMax * 0.5) faireTomberLeFuyard();
          return;
        }
        const porteur = B.mission.entites.find(function (e) { return e.porteLaCaisse; });
        if (porteur && (!porteur.vivant || porteur.etat === 'assomme')) lacherLaCaisse(porteur);
        const caisse = B.mission.entites.find(function (e) { return e.objet === 'caisse'; });
        if (caisse && dist2(j.x, j.y, caisse.x, caisse.y) < 14 * 14 && !j.dansVehicule) {
          Entites.retirer(caisse); Son.SFX.argent(); avancer();
        }
        return;
      }
      case 'courses': {
        B.mission.courses = Missions.boulot.faits.taxi - B.mission.coursesDepart;
        if (B.mission.courses === o.n - 1 && Missions.boulot.etape === 'route' && !B.mission.clientDit && m.dialogue.client) {
          B.mission.clientDit = true;
          dire(m, 'client', null);
        }
        if (B.mission.courses >= o.n) avancer();
        return;
      }
      case 'semer': {
        const v = B.mission.escorte;
        if (v && v.etat === 'epave') { echouer('vehicule_detruit'); return; }
        if (B.recherche.etoiles === 0) avancer();
        return;
      }
      case 'retourner': {
        const d = donneur(m.donneur);
        if (d && dist2(j.x, j.y, d.x, d.y) < RAYON_PARLER * RAYON_PARLER) reussir();
        return;
      }
      case 'survivre':
        if (B.t - p.debutT > (o.secondes || 30) * 60) avancer();
        return;
      case 'parler':
        return;
      // --- M16 : les neuf types de plus ------------------------------------
      // ⚠️ Chacun réutilise un mécanisme qui existe déjà ailleurs : le vol du
      // Grand Saut (`majDefi`), le compteur des boulots (`Missions.boulot`), le
      // jet des poches (`Combat.pickpocket`), l'extincteur (`Incendies`). Un
      // type ne s'invente ici un moteur que s'il n'existe nulle part.
      case 'sauter': {
        // Le vol compte en distance parcourue en l'air, comme le Grand Saut.
        const v = j.dansVehicule;
        if (v && v.z > 0) { B.mission.vol += Math.hypot(v.vx, v.vy); if (B.mission.vol >= o.vol_px) avancer(); }
        return;
      }
      case 'boulots': {
        const depart = B.mission.boulotsDepart, faits = Missions.boulot.faits[o.sorte] || 0;
        if (faits - depart >= o.n) avancer();
        return;
      }
      case 'detruire': {
        const c = B.mission.chars && B.mission.chars[p.etape];
        if (!c) { avancer(); return; }
        if (c.etat === 'epave') avancer();
        return;
      }
      case 'eteindre': {
        // L'extincteur éteint déjà le feu de bâtiment (`Incendies`). Ce type
        // attend qu'aucun feu ne brûle plus au lieu nommé — ou, faute de feu
        // de mission, le feu actif du moment.
        if (typeof Incendies !== 'undefined' && !Incendies.feuActif()) avancer();
        return;
      }
      case 'payer': {
        if (Missions.payer(o.montant, o.raison || '')) avancer();
        return;
      }
      case 'acheter': {
        // Un article a un comptoir : la mission avance quand on l'a en poche
        // (`B.partie.objets` ou `armes`). Le menu du comptoir l'achète déjà.
        const enPoche = B.partie.objets[o.article] || B.partie.armes[o.article];
        if (enPoche) avancer();
        return;
      }
      case 'suivre': {
        // Filer un char sans être vu (`poserLeSuivi`). ⚠️ Avec une MARGE, comme le
        // tracé des courses : trop près (`proche`), la méfiance monte, et redescend
        // quand on recule ; trop loin (`loin`), on a cinq secondes pour le retrouver.
        // L'objectif avance quand IL arrive à son `lieu` — sans lui, rien ne le
        // faisait jamais avancer.
        const c = B.mission.suivi, bm = B.mission;
        if (!c) { avancer(); return; }
        if (c.etat === 'epave' || c.conducteur === j) { echouer('etoile'); return; }
        if (c.attendLeJoueur) {
          if (j.dansVehicule || ++bm.suiviAttente > SUIVI_ATTENTE) { c.attendLeJoueur = false; Hud.message('IL DÉMARRE — SUIS-LE !', 150); }
          return;
        }
        if (c.destination && dist2(c.x, c.y, c.destination.x, c.destination.y) < (4 * TT) * (4 * TT)) {
          // Une étape du détour : il repart vers la suivante, et on le file toujours.
          if (bm.etapesDuSuivi && bm.etapesDuSuivi.length) c.destination = bm.etapesDuSuivi.shift();
          else {
            c.attendLeJoueur = true; c.destination = null;   // rendu : il se range
            avancer();
            return;
          }
        }
        // ⚠️ Trop près, c'est DANS SON RÉTROVISEUR : derrière lui ou à côté. Il
        // démarrait devant ton char garé et te frôlait en passant — la méfiance
        // montait, et la mission ratait sans que tu aies bougé.
        const d = Math.hypot(c.x - j.x, c.y - j.y);
        const devant = (j.x - c.x) * Math.cos(c.angle) + (j.y - c.y) * Math.sin(c.angle);
        bm.tropPres = d < (o.proche || 3) * TT && devant < d * 0.5;
        if (bm.tropPres) {
          if (++bm.mefiance > SUIVI_MEFIANCE) { echouer('etoile'); return; }
        } else bm.mefiance = Math.max(0, bm.mefiance - 0.5);
        if (o.loin && d > o.loin * TT) {
          if (++bm.perdu > SUIVI_PERDU) { echouer('chrono'); return; }
        } else bm.perdu = 0;
        return;
      }
      case 'proteger': {
        // Un personnage te suit ; s'il meurt, échec `protege_mort`. La cible
        // est posée en `poser()` (`B.mission.protege`). ⚠️ Comme `aller` : on
        // avance en ARRIVANT à `lieu` (l'escorte a un but), la cible toujours
        // vivante — sans `lieu`, l'objectif ne ferait jamais que garder.
        const c = B.mission.protege;
        if (!c) { avancer(); return; }
        if (!c.vivant || c.etat === 'assomme') { echouer('protege_mort'); return; }
        if (o.lieu) {
          // ⚠️ LUI AUSSI, et rejoint : on arrivait au poste seul, lui planté à
          // l'arche, et l'escorte était faite. Il marche une tuile ou deux
          // derrière nous (`suite_distance_px`) : deux tuiles de mou pour lui.
          const l = lieu(o.lieu), r = (o.rayon || 4) * TT, rLui = r + 2 * TT;
          if (l && c.suit && dist2(j.x, j.y, l.x, l.y) < r * r && dist2(c.x, c.y, l.x, l.y) < rLui * rLui) {
            // Arrivé, il descend : c'est ici qu'il avait affaire.
            if (c.dansVehicule) descendreLeProtege(c);
            avancer();
          }
        }
        return;
      }
      case 'pickpocket': {
        // Les poches d'un piéton PRÉCIS, par-derrière (le jet de `Combat`).
        // `cible` nomme l'archétype. ⚠️ `Combat.pickpocket` ne l'assomme PAS —
        // un vol par-derrière réussi le laisse `fuit`, poches vides
        // (`victime.argent = 0`) : c'est CE signal-là qu'on guette, pas
        // `assomme` (un vol par-derrière ne le produit jamais). Assommé ou
        // mort compte aussi, si on a réglé ça autrement.
        const victime = B.mission.entites.find(function (e) {
          return e.pickpocket === true && (e.argent <= 0 || !e.vivant || e.etat === 'assomme');
        });
        if (victime) avancer();
        return;
      }
      case 'pirater': {
        // ⚠️ DEMARRER passe par `Missions.interagir` (le bouton ACTION, la meme
        // chaine que parler/monter) : ici on ne fait QUE lire la sequence en
        // cours, image par image, tant qu'elle est ouverte.
        if (B.piratage && B.piratage.etape === p.etape) majPiratage();
        return;
      }
      default:
        avancer();
    }
  }

  function reussir() {
    const m = courante();
    if (!m) return;
    const p = B.partie, d = m.donne || {};
    const vehicule = B.mission ? B.mission.vehicule : null;
    nettoyer(false);
    if (p.tombes) delete p.tombes[m.slug];
    p.missionsFaites[m.slug] = p.jour;
    p.mission = null;
    p.appelT = null;
    const bonus = B.mission && B.mission.sansBosse ? Math.round(m.recompense * 0.5) : 0;
    const prime = m.recompense + bonus;
    Missions.encaisser(prime, m.titre.toUpperCase(), true);
    if (d.arme && !p.armes[d.arme]) { const a = Combat.armeDef(d.arme); p.armes[d.arme] = { mun: a && a.chargeur ? a.chargeur : null }; }
    if (d.rabais) Object.keys(d.rabais).forEach(function (k) { p.rabais[k] = d.rabais[k]; });
    if (d.sergent_ami) p.sergentAmi = true;
    if (d.propriete && !p.proprietes[d.propriete]) p.proprietes[d.propriete] = { jour: p.jour, caisse: 0 };
    if (d.faubourg_libere) p.faubourgLibere = true;
    // ⚠️ `libere` : un district de plus (m98 comptera la liste). `faubourg_libere`
    // alimente la MEME liste, pour qu'il n'y ait qu'une verite.
    if (d.libere && p.libere.indexOf(d.libere) < 0) p.libere.push(d.libere);
    if (d.faubourg_libere && p.libere.indexOf('faubourg') < 0) p.libere.push('faubourg');
    // ⚠️ `calme` (M16) : un gang de plus qui oublie son hostilite (la seule
    // facon de marcher dans La Shop, s05 — et Les Erables, e04). Comme `libere`,
    // une liste ordonnee dans la partie.
    if (d.calme && p.calmes.indexOf(d.calme) < 0) p.calmes.push(d.calme);
    // ⚠️ `dette: -n` et `casier: -n` (M16) : des cles NEGATIVES, une facon de
    // dire « la fin t'enleve ce poids ». Bornees a zero, jamais sous.
    if (typeof d.dette === 'number') p.dette = Math.max(0, p.dette + d.dette);
    if (typeof d.casier === 'number') p.casier = Math.max(0, p.casier + d.casier);
    // ⚠️ `ferme` (M16) : une mission qui en FERME une autre. Un choix est un
    // choix parce qu'il coute : on ecrit la fermeture ICI, au moment de la
    // recompense, et la mission fermee disparait de partout des la prochaine
    // fois qu'on regarde le telephone ou le carnet.
    if (m.ferme && p.fermees.indexOf(m.ferme) < 0) p.fermees.push(m.ferme);
    // ⚠️ `contacts` : des numeros au telephone (m6, Josée qui présente la ville).
    (d.contacts || []).forEach(function (slug) { p.contacts[slug] = true; });
    // ⚠️ `vehicule` : un char garé devant la planque, posé au prochain chargement
    // (m97, le taxi de Marco). Il vit à part de `planque.vehicule` pour ne pas
    // écraser la sauvegarde de Martin.
    if (d.vehicule && Vehicules.vehiculeDef(d.vehicule)) {
      const def = Vehicules.vehiculeDef(d.vehicule);
      p.vehiculePlanque = { slug: d.vehicule, couleur: def.couleurs && def.couleurs[0] ? def.couleurs[0] : null,
                            vie: 100, angle: 0, vole: false };
    }
    if (d.manchette) p.manchetteForcee = d.manchette;
    p.stats.missions = (p.stats.missions || 0) + 1;
    noter('MISSION : ' + m.titre + ' — ' + prime + ' $', true);
    B.mission = null;
    // ⚠️ Le son de la prime REMPLACE le jingle de mission (et le ding de
    // l'argent) : trois sons l'un sur l'autre ne disaient plus la taille.
    Missions.annoncerPrime(prime, m.titre, 'MISSION RÉUSSIE', bonus);
    Missions.sauvegarderPartie();
    // ⚠️ LA FIN SE JOUE QUAND LE MOMENT S'Y PRETE (`jouerLaFin`) : tout de suite
    // si l'on est a l'arret et hors poursuite, sinon des qu'on l'est.
    B.finEnAttente = { slug: m.slug, vehicule: vehicule };
    jouerLaFin();
  }

  function echouer(raison) {
    const m = courante();
    if (!m) return;
    retenirLesTombes(m);
    nettoyer(true);
    B.partie.mission = null;
    B.mission = null;
    Hud.message('MISSION RATÉE — ' + m.titre.toUpperCase(), 200);
    noter('MISSION RATÉE : ' + m.titre, true);
    Son.SFX.erreur();
    B.partie.stats.echecs = (B.partie.stats.echecs || 0) + 1;
    dire(m, 'echec', null);
    void raison;
  }

  /** Abandonne la mission EN COURS, sans compter d'echec ni redire la moindre
      replique : ses figurants s'en vont, la partie n'a plus de mission. Rien
      n'est rendu de ce qu'elle avait pris. */
  function abandonner() {
    const p = B.partie;
    if (!p || !p.mission) return;
    nettoyer(true);
    p.mission = null;
    B.mission = null;
    B.finEnAttente = null;
  }

  /** Reinitialise une mission pour pouvoir la refaire (triche de debug, appelee
      par le saut de mission) : retire son drapeau FAIT, ses appels et ses
      tombes. Si c'est la mission EN COURS, on l'abandonne proprement d'abord
      (nettoyage des entites, sans compter d'echec). ⚠️ Les recompenses deja
      recues ne sont pas reprises : rejouer la mission les redonnera. */
  function reinitialiser(slug) {
    const p = B.partie;
    if (!p || !slug) return false;
    if (p.mission && p.mission.slug === slug) abandonner();
    delete p.missionsFaites[slug];
    delete p.appels[slug];
    if (p.tombes) delete p.tombes[slug];
    p.appelT = null;
    return true;
  }

  /** Ceux qu'on a couches ne se relevent pas parce qu'on a rate : on les
      compte par objectif et par coin, et la reprise ne repose que les autres.
      ⚠️ K.-O. compte comme mort, comme au compteur de l'objectif : le « 4/6 »
      qu'on a lu a l'ecran est celui qu'on retrouve en revenant. */
  function retenirLesTombes(m) {
    if (!B.mission) return;
    const toutes = B.partie.tombes = B.partie.tombes || {};
    const t = toutes[m.slug] = toutes[m.slug] || {};
    for (const e of B.mission.entites) {
      if (e.type !== 'pieton' || e.etape === undefined || (e.vivant && e.etat !== 'assomme')) continue;
      const parCoin = t[e.etape] = t[e.etape] || [];
      parCoin[e.coin] = (parCoin[e.coin] || 0) + 1;
    }
  }

  function tombesDe(slug, etape) {
    const t = B.partie.tombes && B.partie.tombes[slug];
    return (t && t[etape]) || [];
  }

  function dejaTombes(slug, etape) {
    return tombesDe(slug, etape).reduce(function (a, n) { return a + (n || 0); }, 0);
  }

  /** Ce que la mission avait pose : on l'enleve (ou on le laisse vivre sa vie). */
  // --- Celui qu'on escorte (`proteger`) ---------------------------------------------------

  //: A cette distance de lui, on l'a rejoint : il se met a nous suivre.
  const RAYON_REJOINDRE = 3 * TT;
  //: Le char arrete a cette distance de lui, il monte — celle du client du taxi.
  const RAYON_MONTER = 40;
  //: Un pas de piste tous les tant de pixels : la ou le joueur est passe, il passe.
  const PAS_DE_PISTE = 12;
  //: Au-dela, les plus vieux pas s'effacent (5 000 px de trajet).
  const PISTE_MAX = 400;
  //: Plus pres du joueur que ca, il va droit sur lui.
  const RAYON_DROIT = 3 * TT;

  /** Il attend qu'on le rejoigne, puis il suit ; il monte dans le char quand on
      s'arrete pres de lui, et il en descend quand on en descend. ⚠️ Toute la
      mission, pas seulement l'objectif `proteger` : les Skateux de p14 arrivent
      APRES, et il reste « colle sur toi » pendant qu'on se bat. */
  function majProtege() {
    const c = B.mission && B.mission.protege, j = B.joueur;
    if (!c || !c.vivant || c.etat === 'assomme' || B.interieur || c.rentre) return;
    const v = j.dansVehicule;
    if (!c.suit) {
      if (dist2(j.x, j.y, c.x, c.y) > RAYON_REJOINDRE * RAYON_REJOINDRE) return;
      c.suit = j;
      Hud.message('IL TE SUIT — À PIED OU EN CHAR', 180);
    }
    if (c.dansVehicule && c.dansVehicule !== v) descendreLeProtege(c);
    else if (!c.dansVehicule && v && v.etat !== 'epave' && c.etat !== 'fuit' && Math.abs(v.vitesse) < 0.4
             && dist2(v.x, v.y, c.x, c.y) < RAYON_MONTER * RAYON_MONTER) {
      c.dansVehicule = v; c.dessine = false; c.vx = 0; c.vy = 0; c.x = v.x; c.y = v.y;
      Son.SFX.porte('vehicule');
    }
    if (c.dansVehicule) c.piste = null;
    else suivreLaPiste(c, j);
  }

  /** Il marche SUR NOS PAS, pas en ligne droite. ⚠️ En ligne droite (`suit`, le
      petit et sa mere, qui ne s'eloignent jamais), il suffisait d'un sprint pour
      le distancer, et d'un coin de mur pour le perdre : au banc, le joueur qui
      court de l'arche au poste le laissait a 2 800 px, colle contre une facade.
      La ou le joueur a mis les pieds, il y a de la place pour lui. */
  function suivreLaPiste(c, j) {
    const piste = c.piste || (c.piste = []);
    const bout = piste.length ? piste[piste.length - 1] : null;
    if (!bout || dist2(j.x, j.y, bout.x, bout.y) > PAS_DE_PISTE * PAS_DE_PISTE) piste.push({ x: j.x, y: j.y, vivant: true });
    if (piste.length > PISTE_MAX) piste.shift();
    if (dist2(c.x, c.y, j.x, j.y) < RAYON_DROIT * RAYON_DROIT) { piste.length = 0; c.suit = j; return; }
    // Le plus vieux pas qu'il n'a pas encore atteint. ⚠️ `suit` s'arrete a
    // `suite_distance_px` de ce qu'il suit : un pas se compte atteint un peu
    // au-dela, sinon il s'arreterait devant chacun.
    const atteint = B.defs.pietons.reactions.suite_distance_px + 4;
    while (piste.length > 1 && dist2(c.x, c.y, piste[0].x, piste[0].y) < atteint * atteint) piste.shift();
    c.suit = piste[0] || j;
  }

  /** Il sort du char, du cote du passager — pas sur le joueur qui sort du sien. */
  function descendreLeProtege(c) {
    const v = c.dansVehicule, j = B.joueur;
    c.dansVehicule = null; c.dessine = true;
    if (!v) return;
    for (const a of [v.angle - Math.PI / 2, v.angle + Math.PI / 2, v.angle + Math.PI]) {
      const x = v.x + Math.cos(a) * (v.def.largeur / 2 + 8), y = v.y + Math.sin(a) * (v.def.largeur / 2 + 8);
      if (dist2(x, y, j.x, j.y) < 12 * 12) continue;
      if (!Monde.bloque(Math.floor(x / TT), Math.floor(y / TT), Monde.MASQUE_PIETON)) { c.x = x; c.y = y; return; }
    }
    c.x = j.x; c.y = j.y;          // tout est bouche : a cote du joueur, `demeler` les ecarte
  }

  /** La mission finie — reussie, ratee, abandonnee —, il nous lache. Un donneur
      rentre a son poste (`majRetours`) ; un personnage neuf s'en va avec les
      figurants de la mission. */
  function lacherLeProtege() {
    const c = B.mission.protege;
    if (!c || !c.chezLui) return;
    if (c.dansVehicule) descendreLeProtege(c);
    c.suit = null; c.piste = null; c.mission = null; c.intouchable = true; c.rentre = true;
  }

  /** Ceux qu'une escorte a eloignes de leur poste y RENTRENT — remis a neuf,
      morts ou couches compris, comme au chargement —, mais jamais sous nos
      yeux : ni la ou il est, ni la ou il va, ne sont a l'ecran. Une fois par
      demi-seconde : il n'y a pas de presse.

      ⚠️ LE MEME, PAS UN NEUF : `creerPersonnage` passe par `creerPieton`, qui
      tire deux des. Le retour tombe quand la camera s'en va — un moment qu'une
      scene regardee ou sautee deplace — et le hasard de toute la ville basculait
      avec lui (`test_une_scene_de_mission_ne_tire_aucun_de`, p14 et f09). */
  function majRetours() {
    if (B.interieur || B.t % 30 !== 0) return;
    const e = B.entites.find(function (q) { return q.rentre && q.type === 'pieton'; });
    if (!e || Entites.visibleAEcran(e.x, e.y, TT) || Entites.visibleAEcran(e.chezLui.x, e.chezLui.y, TT)) return;
    e.x = e.chezLui.x; e.y = e.chezLui.y; e.vx = 0; e.vy = 0;
    e.vivant = true; e.vie = e.vieMax; e.etat = 'fige'; e.face = 'bas'; e.plante = null;
    e.recul = 0; e.saigne = 0; e.fuite = 0; e.sursaut = 0; e.menace = null; e.minuterie = 0;
    e.intouchable = true; e.dessine = true; e.vitesseSuite = null; e.rentre = false; e.chezLui = null;
    Entites.indexer();
  }

  function nettoyer(tout) {
    // ⚠️ TOUJOURS, meme mission deja nulle : un piratage ouvert ne doit pas
    // survivre a la mission qui l'a pose (`reussir`, `echouer`, `abandonner`).
    fermerPiratage();
    if (!B.mission) return;
    lacherLeProtege();
    for (const e of B.mission.entites) {
      if (e.type === 'vehicule') {
        // Celui qu'on filait repart comme un autre, qu'on l'ait mené au bout ou
        // qu'il nous ait vus : il n'est jamais escamoté sous nos yeux.
        if (e.suivi && B.joueur.dansVehicule !== e) { e.suivi = false; e.attendLeJoueur = false; e.destination = null; e.mission = null; }
        else if (tout || e.fuyard || e.escorte) { if (B.joueur.dansVehicule === e) Vehicules.descendre(B.joueur, true); Entites.retirer(e); }
        else { e.mission = null; }
      } else if (e.type === 'pieton') { e.cible = false; e.chef = false; if (e.vivant && e.etat !== 'assomme') { e.etat = 'fuit'; e.minuterie = 300; } }
      else Entites.retirer(e);
    }
  }

  /** Les echecs qui viennent d'ailleurs : la prison, l'hopital. */
  //: Ce qu'un evenement laisse au journal. ⚠️ La table est ici et nulle part
  //: ailleurs : `missions.js` emet deja `mort` et `arrete` pour faire echouer
  //: une mission, et le carnet se sert de la MEME emission — il n'y a pas deux
  //: endroits qui decident qu'on est alle a l'hopital.
  const AU_CARNET = {
    mort: 'Réveil à l’hôpital',
    arrete: 'Arrêté par la police',
  };

  function evenement(nom) {
    if (AU_CARNET[nom]) noter(AU_CARNET[nom], false);
    const m = courante();
    if (!m) return;
    if (m.echec.indexOf(nom) >= 0) echouer(nom);
  }

  // --- Les defis -------------------------------------------------------------------------------

  function defis() { return B.defs.defis || []; }

  /** Un panneau par defi, pose a son point de depart. */
  //: Un panneau se tient a cette distance au moins d'un donneur : au-dela de la
  //: portee de parole (`RAYON_PARLER`) de celui qui le lit, planté devant.
  const PANNEAU_LOIN_DU_DONNEUR = 3 * TT;

  /** Ce pixel, s'il n'est ni devant un rideau de garage (sa baie, une tuile de
      marge), ni devant une porte, ni a portee d'un donneur ; sinon null.
      ⚠️ `aere` : ni SUR un meuble solide, ni coince entre deux. `tuileLibre` ne
      regarde que la carte : devant le depanneur, le panneau de la course se
      plantait sur le banc de l'abribus, puis — l'arret parti — entre l'edicule du
      metro et le guichet (retour de Martin, 22 sept. 2026 : « trop de choses
      colle devant chez Ti-Paul »). */
  function placeDePanneau(p, aere) {
    if (!p) return null;
    if (Monde.devantDUnePorte(Math.floor(p.x / TT), Math.floor(p.y / TT))) return null;
    if (Monde.portesDeGarage().some(function (pg) { return Monde.devantLaPorteDeGarage(pg, p.x, p.y, 2, 1); })) return null;
    if (aere) {
      const tx = Math.floor(p.x / TT), ty = Math.floor(p.y / TT);
      const meubles = Entites.decorAutour(p.x, p.y, 2 * TT).filter(function (d) {
        return d.solide && Math.max(Math.abs(Math.floor(d.x / TT) - tx), Math.abs(Math.floor(d.y / TT) - ty)) <= 1;
      });
      const dessus = meubles.some(function (d) { return Math.floor(d.x / TT) === tx && Math.floor(d.y / TT) === ty; });
      if (dessus || meubles.length >= 2) return null;
    }
    if (panneauVoisin(p)) return null;
    return Entites.pietonsAutour(p.x, p.y, PANNEAU_LOIN_DU_DONNEUR).some(function (e) { return e.personnage; }) ? null : p;
  }

  /** Les panneaux des defis qu'on a DES LE DEPART (sans `debloque`). ⚠️ Ceux
      qui se debloquent naissent plus tard, un par un, a l'image ou ils s'ouvrent
      (`majDeblocages`) : une partie neuve ne cree pas une entite de plus au
      demarrage, et rien de ce qui se tire a l'empreinte d'un numero ne bouge. */
  function creerPanneaux() {
    for (const d of defis()) {
      if (!d.debloque) poserPanneau(d);
    }
  }

  //: Deux panneaux ne se plantent pas a moins de ca l'un de l'autre : deux defis
  //: devant la meme porte se liraient l'un pour l'autre (`panneauSousLaMain`
  //: prend le premier qui est a portee).
  const PANNEAUX_ECARTES = 3 * TT;

  /** Le panneau d'UN defi, a son point de depart — ou rien si le defi se joue a
      un comptoir de la foire, ou si la ville n'a pas de place. */
  function poserPanneau(d) {
    let l = null;
    if (d.ou === 'rampe') {
      // ⚠️ La PLUS PROCHE du depart, et pas la premiere venue en balayant la
      // carte : les rampes vivent maintenant dans les cours de La Shop et au
      // port, et le panneau du Grand Saut se posait a l'autre bout de la
      // ville. On se pose au PIED, du cote de l'elan — un panneau derriere
      // le tremplin, on le lit apres avoir saute.
      const depart = Monde.carte.apparition && Monde.carte.apparition.joueur;
      // ⚠️ Seulement celles que `carte.py` a marquees `defi` : elles ont de
      // quoi recevoir une MOTO LANCEE, pas seulement l'auto de reference. Le
      // Grand Saut exige la moto ; un panneau pose sur une rampe ordinaire,
      // c'est un defi qui se termine dans un mur. Repli sur toutes les
      // rampes : mieux vaut un defi dur qu'un defi absent.
      const toutes = Monde.carte.rampes || [];
      const bonnes = toutes.filter(function (r) { return r.defi; });
      const rampes = (bonnes.length ? bonnes : toutes).slice().sort(function (a, b) {
        if (!depart) return 0;
        return (Math.abs(a.x - depart.x) + Math.abs(a.y - depart.y))
             - (Math.abs(b.x - depart.x) + Math.abs(b.y - depart.y));
      });
      for (const r of rampes) {
        const c = { x: (r.x - r.dx) * TT + 8, y: (r.y - r.dy) * TT + 8 };
        if (tuileLibre(c.x - TT * 3, c.y, 3) || tuileLibre(c.x + TT * 3, c.y, 3)) { l = c; break; }
      }
    } else if (d.ou.indexOf('porte:') === 0) l = lieu(d.ou.slice(6));
    if (!l) return null;
    // ⚠️ JAMAIS DEVANT UN RIDEAU DE GARAGE : trois tuiles a l'ouest de la
    // porte de Ti-Guy, c'est exactement la baie ou l'on gare pour vendre, et
    // le panneau de la livraison s'y plantait devant la porte qui se leve.
    // ⚠️ NI SOUS LE NEZ D'UN DONNEUR : a l'est, c'est Marco qui attend, et
    // ACTION lui parlait au lieu de lire le panneau (`interagir` sert les
    // personnages d'abord). On s'eloigne par pas ; ailleurs, rien ne change.
    // ⚠️ Une place AEREE d'abord (ni sur un meuble, ni entre deux), un pas plus
    // loin s'il le faut : au terminus, Ti-Guy, Mo et Fern ne s'empilent plus sur
    // une tuile, et a eux trois ils tiennent toute la facade. Faute de mieux, la
    // premiere place d'avant : un panneau serre vaut mieux qu'un defi absent.
    let place = null;
    for (const aere of [true, false]) {
      for (const loin of [3, 5, 7, 9, 11]) {
        place = placeDePanneau(tuileLibre(l.x - TT * loin, l.y, 3), aere)
          || placeDePanneau(tuileLibre(l.x + TT * loin, l.y, 3), aere);
        if (place) break;
      }
      if (place) break;
    }
    if (!place) return null;
    return Entites.creer('panneau', place.x, place.y, { decor: 'panneau', r: 3, solide: false, dessine: true, vivant: false, defi: d.slug });
  }

  /** Un autre panneau de defi plante trop pres de ce pixel ? ⚠️ Dans `B.entites`,
      pas dans l'index spatial : un panneau pose dans la meme image n'y est pas encore. */
  function panneauVoisin(p) {
    return B.entites.some(function (e) {
      return e.type === 'panneau' && dist2(e.x, e.y, p.x, p.y) < PANNEAUX_ECARTES * PANNEAUX_ECARTES;
    });
  }

  function panneauSousLaMain(j) {
    return Entites.autour(j.x, j.y, 24, function (e) { return e.type === 'panneau' && faceA(j, e.x, e.y); })[0] || null;
  }

  function proposerDefi(slug) {
    const d = defis().find(function (q) { return q.slug === slug; });
    if (!d || B.defi) return false;
    const fait = !!B.partie.defisFaits[slug];
    // LE DEFI DU JOUR (M14, 5e vague) : sa prime se gagne chaque jour, en plus de celle de la
    // premiere fois — et on dit ce qu'on va toucher, pas seulement « une prime ».
    const duJour = Defi.estDuJour(slug), aPayer = Defi.aPayer(slug);
    const gain = (fait ? 0 : d.prime) + (aPayer ? d.prime : 0);
    const sur = duJour ? (aPayer ? 'DÉFI DU JOUR · ' + gain + ' $' : 'DÉFI DU JOUR — RÉUSSI AUJOURD\'HUI')
      : (fait ? 'DÉJÀ RÉUSSI' : d.prime + ' $');
    // Le panneau est LU : le drapeau du defi ne bat plus sur la carte.
    const ouvert = B.partie.defisOuverts && B.partie.defisOuverts[slug];
    if (ouvert) ouvert.lu = true;
    // ⚠️ AVEC QUOI IL SE JOUE, et pas seulement sur la carte : c'est ici qu'on
    // decide de commencer. Une ligne de plus sous la liste (`Hud.dessinerAppareils`),
    // et un avertissement quand l'appareil qu'on tient n'y est pas — on peut
    // commencer quand meme : on a peut-etre une manette dans le tiroir.
    Hud.ouvrirMenu({ titre: d.titre.toUpperCase(), sur: sur, aide: d.texte, hauteur: 100, largeur: 380, items: [
      { libelle: 'COMMENCER', faire: function () { commencerDefi(d); return true; } },
      { libelle: 'PAS MAINTENANT', faire: function () { return true; } },
    ], dessiner: function (ctx, x, y, l, h) { Hud.dessinerAppareils(ctx, appareilsDe(d), x + 8, y + h - 28); } });
    return true;
  }

  // --- Avec quoi on joue, et quand ca s'ouvre (les dix-huit defis, 23 sept. 2026) ----------------
  //: Martin : « on doit les voir selon s'il est possible de les faire avec les
  //: doigts ou avec la manette ou le clavier. Je veux qu'ils n'apparaissent pas
  //: tous en meme temps, mais graduellement quand on passe des defis ou qu'on
  //: avance dans l'histoire. »

  //: L'appareil qu'on tient (`Entree.appareil`) dans les mots du catalogue.
  const APPAREIL_DU_CATALOGUE = { tactile: 'doigts', manette: 'manette', clavier: 'clavier' };

  /** Les appareils avec lesquels ce defi se joue (`appareils` du catalogue ;
      les trois par defaut). */
  function appareilsDe(d) { return (d && d.appareils) || ['doigts', 'manette', 'clavier']; }

  /** Ce defi se joue-t-il avec `appareil` (un mot du catalogue : `doigts`,
      `manette`, `clavier`) — par defaut, celui qu'on tient ? */
  function jouableAvec(d, appareil) {
    const a = appareil || APPAREIL_DU_CATALOGUE[Entree.appareil] || 'clavier';
    return appareilsDe(d).indexOf(a) >= 0;
  }

  /** Les conditions de `debloque` tiennent-elles, dans cette partie ? */
  function conditionsTenues(d) {
    const r = d.debloque, p = B.partie;
    if (!r) return true;
    if (r.defis && Object.keys(p.defisFaits || {}).length < r.defis) return false;
    if (r.missions && r.missions.some(function (m) { return !(p.missionsFaites || {})[m]; })) return false;
    if (r.apres && r.apres.some(function (s) { return !(p.defisFaits || {})[s]; })) return false;
    return true;
  }

  /** Ce defi est-il OUVERT ? Sans `debloque`, toujours ; sinon, une fois
      qu'il a ete debloque — et il le reste (`partie.defisOuverts`). */
  function defiOuvert(d) {
    if (!d) return false;
    if (!d.debloque) return true;
    return !!(B.partie && B.partie.defisOuverts && B.partie.defisOuverts[d.slug]);
  }

  /** Les defis ouverts, dans l'ordre du catalogue — ceux de la carte. */
  function defisOuverts() { return defis().filter(defiOuvert); }

  /** Un defi neuf (pas encore lu) : son drapeau bat sur la carte. */
  function defiNeuf(d) {
    const o = d && d.debloque && B.partie && B.partie.defisOuverts && B.partie.defisOuverts[d.slug];
    return !!(o && !o.lu);
  }

  /** Ouvre ce defi : il entre dans la partie et son panneau se plante. Rend vrai
      s'il vient de s'ouvrir. ⚠️ La triche SAUT VERS UN DÉFI passe aussi par ici
      (`force`) : un saut vers un defi encore cache l'ouvre. */
  function ouvrirDefi(d, force) {
    if (!d || !d.debloque || defiOuvert(d)) return false;
    if (!force && !conditionsTenues(d)) return false;
    B.partie.defisOuverts[d.slug] = { jour: B.partie.jour, lu: false };
    return true;
  }

  /** Un panneau pour chaque defi ouvert qui n'en a pas encore (sauf ceux de la
      foire : la baraque sert de panneau). */
  function planterLesPanneauxOuverts() {
    for (const d of defisOuverts()) {
      if (!d.debloque || !d.ou || d.ou.indexOf('porte:') !== 0) continue;
      if (B.entites.some(function (e) { return e.type === 'panneau' && e.defi === d.slug; })) continue;
      poserPanneau(d);
    }
  }

  //: On regarde les conditions une fois par seconde : un defi s'ouvre a la fin
  //: d'une mission ou d'un autre defi, pas au milieu d'une image.
  const DEBLOCAGE_PERIODE = 60;

  /** Les defis qui s'ouvrent : on les ouvre, on plante leur panneau, on le dit
      — une fois pour tous ceux qui s'ouvrent ensemble (une vieille partie en
      ouvre plusieurs d'un coup, et six messages se recouvriraient). ⚠️ Jamais
      pendant une scene ni une mission : le message se perdrait sous elles. */
  function majDeblocages(maintenant) {
    if (!B.partie || B.interieur || B.cinema || B.scene) return;
    if (!maintenant && B.t % DEBLOCAGE_PERIODE !== 0) return;
    if (!B.partie.defisOuverts) B.partie.defisOuverts = {};
    const neufs = defis().filter(function (d) { return ouvrirDefi(d, false); });
    planterLesPanneauxOuverts();
    if (!neufs.length) return;
    for (const d of neufs) noter('NOUVEAU DÉFI : ' + d.titre, true);
    if (!B.mission && !B.defi) {
      Hud.message(neufs.length === 1 ? 'NOUVEAU DÉFI : ' + neufs[0].titre.toUpperCase() + ' — VOIS LA CARTE'
        : neufs.length + ' NOUVEAUX DÉFIS — VOIS LA CARTE', 240);
      Son.SFX.mission();
    }
  }

  // --- Les trois jeux d'adresse de la foire -----------------------------------------------------
  //
  // ⚠️ **UN JEU D'ADRESSE EST UN DÉFI, PAS UN MOTEUR**, et c'est la fiche du
  // plan qui l'écrit en majuscules : ce qui suit tient sur les rails des trois
  // défis de char de la v1 — un lieu, un compte, un chrono, une prime, un texte
  // en majuscules. La seule chose qu'ils ajoutent, c'est `a_pied` : on les joue
  // DEBOUT devant un comptoir. Pas de statistique neuve, pas d'état de plus.

  /** Les jeux de la foire, et ce qu'il en reste à gagner. */
  function defisDeFoire() { return defis().filter(function (d) { return d.foire; }); }

  /** Le comptoir d'un défi de foire, tel qu'il vit dans le monde. ⚠️ Peut être
      CASSÉ : un comptoir défoncé ne sert plus de lot (voir `majDefi`). */
  function comptoirDeDefi(d) {
    if (!d || !d.ou || d.ou.indexOf('foire:') !== 0 || typeof Foire === 'undefined') return null;
    return Foire.kiosqueDuJeu(d.ou.slice(6));
  }

  /** Le canard est-il sous le crochet, À CETTE IMAGE ?

      ⚠️ **C'est le DESSIN qui le dit**, et c'est tout ce qui rend la pêche
      jouable : la pose du bassin (`Entites.poseDuDecor`, la même que celle qui
      se peint) vaut `d.pose` pendant `anime` images par tour, et c'est à ce
      moment-là — et à ce moment-là seulement — qu'un canard passe sous la
      canne. Un chrono inventé ici et une animation qui tourne de son côté, ce
      serait un jeu d'adresse où l'adresse ne sert à rien. */
  function canardAuCrochet() {
    const f = typeof DECORS !== 'undefined' ? DECORS.peche_canards : null;
    const d = defis().find(function (q) { return q.slug === 'canards'; });
    if (!f || !d) return false;
    // ⚠️ `B.t + 1` : `maj` tourne AVANT que l'image avance, et c'est l'image
    // SUIVANTE qui se peint — la même correction que le marteau du chantier.
    return Entites.poseDuDecor(f, B.t + 1, false) === d.pose;
  }

  /** ACTION pendant un défi de foire : le marteau et la canne. Rend vrai si le
      bouton a servi — et alors il ne sert à rien d'autre.

      ⚠️ **LA CHAÎNE D'ACTION AFFAME CE QUI SUIT** : ce test passe AVANT tout le
      reste (`Missions.interagir`), sinon marteler devant le comptoir ouvrirait
      le menu du comptoir à chaque coup. */
  function actionDeDefi() {
    const f = B.defi;
    if (!f) return false;
    const d = defis().find(function (q) { return q.slug === f.slug; });
    if (!d || !d.a_pied) return false;
    // ⚠️ UNE ÉPREUVE LIT SES BOUTONS ELLE-MÊME (`Adresse.maj`, à chaque image) :
    // ACTION y freine une roue, lance un anneau, attrape une toux. Ici, on ne
    // fait que le garder pour elle — sinon il ouvrirait le kiosque d'à côté.
    if (d.epreuve) return true;
    if (d.coups) {
      f.coups++;
      Son.SFX.maillet();
      if (f.coups >= d.coups) { Son.SFX.cloche(); finirDefi(true); }
      return true;
    }
    if (d.canards) {
      if (!canardAuCrochet()) { Hud.message('RATÉ — IL EST REPARTI', 60); Son.SFX.erreur(); return true; }
      // ⚠️ UN CANARD PAR PASSAGE : sans ça, trois appuis dans la même fenêtre
      // pêchent trois fois le même canard, et le jeu se gagne en martelant.
      const tour = Math.floor((B.t + 1) / (DECORS.peche_canards.anime * DECORS.peche_canards.variantes));
      if (f.tour === tour) { Hud.message('CELUI-LÀ EST DÉJÀ DANS LE SEAU', 60); Son.SFX.erreur(); return true; }
      f.tour = tour;
      f.pris++;
      Son.SFX.ramasse();
      if (f.pris >= d.canards) finirDefi(true);
      else Hud.message('UN CANARD ! ' + f.pris + ' / ' + d.canards, 60);
      return true;
    }
    return false;
  }

  //: Le temps qu'on a, le panneau lu, pour monter dans le char du defi.
  //: ⚠️ LE PANNEAU SE LIT A PIED (au volant, ACTION fait descendre) : le tour et
  //: la livraison, qui ratent sans char, ratent donc a l'image suivante — ni
  //: l'un ni l'autre ne s'etait jamais gagne. Le Grand Saut avait deja ses dix
  //: secondes pour trouver sa moto ; les deux autres les ont aussi, et leur
  //: chrono ne part qu'au volant.
  const ATTENTE_CHAR = 600;

  function commencerDefi(d) {
    const j = B.joueur;
    B.defi = { slug: d.slug, t: 0, attente: 0, parti: false, etape: 0, tours: 0, vol: 0, chocs: 0, vie: 0,
               coups: 0, pris: 0, tour: -1, x: j.x, y: j.y, avantArme: null, vieDepart: j.vie };
    // Une course tire son circuit AU PANNEAU : la ligne de depart se montre
    // (fleches et GPS) avant meme qu'on ait trouve un char.
    if (d.circuit) Object.assign(B.defi, { piste: circuit(d), i: 0, avance: 0, hors: 0, enPiste: false });
    Son.SFX.mission();
    // ⚠️ UN JEU DE FOIRE SE JOUE DEBOUT : pas de char a trouver, ca part tout de
    // suite — et le forain RELEVE SES CIBLES avant de nous laisser tirer. Sans
    // ca, une galerie jouee deux fois dans la journee serait un defi qu'on ne
    // peut plus gagner : ses cibles sont par terre, et le matin est loin.
    if (d.a_pied) {
      if (d.cibles && typeof Foire !== 'undefined') Foire.cibles().forEach(Entites.releverDecor);
      // ⚠️ **LE FORAIN PRÊTE SA CARABINE À BOUCHON**, puis la reprend à la fin.
      // Avant, on crevait les cibles avec sa PROPRE arme à feu : la foule
      // fuyait, la police rappliquait, et sans arme à feu on ne pouvait pas
      // jouer du tout (les poings n'atteignent pas les décors). La carabine de
      // foire est inoffensive — `foire`, dans `combat.js` — et ne sort du sac
      // que le temps de la partie.
      if (d.cibles && typeof Combat !== 'undefined') {
        B.defi.avantArme = j.arme;
        B.partie.armes.carabine_foire = { mun: null, usure: 0 };
        B.partie.arme = 'carabine_foire';
        j.arme = 'carabine_foire';
      }
      if (d.consigne) Hud.message(d.consigne, 180);
      if (d.epreuve) Adresse.commencer(d);
      partir(d, null);
      return;
    }
    // ⚠️ UNE ÉPREUVE AU VOLANT (`Conduite`) trouve sa piste AU PANNEAU, et y pose
    // ce qui attend (la remorqueuse, l'épave) : ses marques se voient avant qu'on
    // ait trouvé un char. Pas de place ici : le défi ne ment pas, il ne part pas.
    if (d.conduite && !Conduite.commencer(d)) {
      B.defi = null;
      Hud.message('PAS DE PLACE ICI POUR CE DÉFI', 150); Son.SFX.erreur();
      return;
    }
    // Le Grand Saut compte ses dix secondes lui-meme (`majDefi`) : il part tout de suite.
    if (d.vehicule || j.dansVehicule) { partir(d, j.dansVehicule); return; }
    Hud.message(d.titre.toUpperCase() + ' — MONTE DANS UN CHAR', 150);
  }

  /** Le chrono part. ⚠️ La police aux fesses et la reference « sans bosse » se
      prennent ICI, au volant, et pas au panneau : sinon on se ferait arreter en
      marchant jusqu'a son char, et on comparerait ses bosses a celles d'aucun. */
  function partir(d, v) {
    const f = B.defi;
    f.parti = true; f.t = 0; f.attente = 0;
    f.chocs = v ? v.chocs : 0; f.vie = v ? v.vie : 0;
    if (d.etoiles) { B.recherche.etoiles = Math.max(B.recherche.etoiles, d.etoiles); B.recherche.vu = 0; }
    if (d.conduite) Conduite.partir(d, v);
    // ⚠️ **AU GO, ON RAPPELLE QUOI FAIRE** : le menu l'a dit en `aide`, mais on
    // le relit à l'instant où la partie part — et la consigne d'un jeu de
    // foire tient en une ligne (`FRAPPE POUR TIRER`, `MARTÈLE ACTION`…).
    Hud.message(d.titre.toUpperCase() + (d.circuit ? ' — À LA LIGNE DE DÉPART' : ' — GO ! ' + (d.consigne || '')), 160);
  }

  function majDefi() {
    const f = B.defi, j = B.joueur;
    if (!f) return;
    const d = defis().find(function (q) { return q.slug === f.slug; });
    if (d.a_pied) { majDefiDeFoire(d, f, j); return; }
    if (!f.parti) {
      if (!j.dansVehicule) { if (++f.attente > ATTENTE_CHAR) finirDefi(false, 'IL FAUT UN CHAR'); return; }
      partir(d, j.dansVehicule);
    }
    if (d.circuit) { majCircuit(d, f, j.dansVehicule); return; }
    f.t++;
    if (d.conduite) {
      if (d.chrono_s && f.t > d.chrono_s * 60) { finirDefi(false, 'TEMPS ÉCOULÉ'); return; }
      const issue = Conduite.maj(d, j.dansVehicule);
      if (issue) finirDefi(issue.gagne, issue.raison);
      return;
    }
    if (d.chrono_s && f.t > d.chrono_s * 60) { finirDefi(false, 'TEMPS ÉCOULÉ'); return; }
    const v = j.dansVehicule;
    if (d.vehicule === 'moto') {
      if (!v || v.slug !== 'moto') { if (f.t > 600) finirDefi(false, 'IL FAUT UNE MOTO'); return; }
      if (v.z > 0) { f.vol += Math.hypot(v.vx, v.vy); if (f.vol >= d.vol_px) finirDefi(true); }
      else f.vol = 0;
      return;
    }
    if (d.lieu) {
      if (!v) { finirDefi(false, 'SANS CHAR, PAS DE LIVRAISON'); return; }
      if (v.chocs !== f.chocs || v.vie < f.vie) { finirDefi(false, 'UNE BOSSE !'); return; }
      const cible = lieu(d.lieu);
      if (cible && dist2(v.x, v.y, cible.x, cible.y) < (4 * TT) * (4 * TT) && Math.abs(v.vitesse) < 0.4) finirDefi(true);
    }
  }

  /** Une image d'un jeu d'adresse. Trois règles pour les trois, et elles sont
      les mêmes que pour les défis de char : un chrono, un lieu, un compte.

      ⚠️ **ON RESTE DEVANT LE COMPTOIR.** C'est le « lieu » de la fiche : un
      marteau de force qu'on martèle en marchant vers le pont ne serait plus un
      jeu d'adresse, ce serait un bouton. Le rayon est large pour la galerie
      (on recule pour tirer) et serré pour les deux autres (on y a les mains).

      ⚠️ **ON LE GAGNE, ON NE LE VOLE PAS** : un comptoir défoncé ne rend pas de
      lot. Ça vaut pour les trois — défoncer la baraque met fin à la partie —
      et c'est `vole_pas` qui le DIT pour la pêche, là où la tentation est la
      plus grande (un bassin plein de canards derrière une planche). */
  function majDefiDeFoire(d, f, j) {
    f.t++;
    if (d.chrono_s && f.t > d.chrono_s * 60) { finirDefi(false, 'TEMPS ÉCOULÉ'); return; }
    if (j.dansVehicule) { finirDefi(false, 'PAS AU VOLANT'); return; }
    // ⚠️ UN COUP, ET L'ÉPREUVE S'ARRÊTE : on la joue cloué sur place
    // (`Entites.majJoueur`), et personne ne se fait tabasser sans pouvoir bouger.
    if (d.epreuve && j.vie < f.vieDepart) { finirDefi(false, 'ON T\'A DÉRANGÉ'); return; }
    // Une épreuve devant un PANNEAU n'a pas de comptoir : on la joue là où on
    // l'a commencée, et on n'en bouge pas.
    if (d.epreuve && d.ou.indexOf('foire:') !== 0) {
      const issue = Adresse.maj(d);
      if (issue) finirDefi(issue.gagne, issue.raison);
      return;
    }
    const comptoir = comptoirDeDefi(d);
    if (!comptoir || comptoir.brise) { finirDefi(false, 'LE COMPTOIR EST EN MIETTES'); return; }
    if (Math.hypot(j.x - comptoir.x, j.y - comptoir.y) > (d.rayon_px || 40)) {
      finirDefi(false, 'TU T\'EN VAS'); return;
    }
    // LA GALERIE DE TIR : les cibles sont des décors avec des PV, et n'importe
    // quoi qui les crève compte — une balle, une bille de fronde. ⚠️ Rien ne
    // compte les tirs : ce qu'on mesure, c'est ce qui est TOMBÉ.
    if (d.cibles) {
      const crevees = Foire.cibles().filter(function (c) { return c.brise; }).length;
      if (crevees >= d.cibles) finirDefi(true);
    }
    if (d.epreuve) {
      const issue = Adresse.maj(d);
      if (issue) finirDefi(issue.gagne, issue.raison);
    }
  }

  /** ⚠️ **LE FORAIN REPREND SA CARABINE** — gagnée, ratée ou abandonnée, la
      partie est finie, et on reprend l'arme qu'on tenait avant de jouer. Sans
      ça, on garderait le bouchon pour la rue, et il ne blesse personne. */
  function rendreLaCarabine(f) {
    if (f && f.avantArme && B.joueur) {
      delete B.partie.armes.carabine_foire;
      if (B.joueur.arme === 'carabine_foire') {
        B.joueur.arme = f.avantArme;
        B.partie.arme = f.avantArme;
      }
    }
  }

  /** Le defi en cours s'arrete la, SANS rien noter ni rien dire : c'est la
      triche SAUT VERS UN DÉFI (`Hud.menuSautDefis`) qui l'abandonne pour en
      proposer un autre — pas un echec du joueur. */
  function abandonnerDefi() {
    rendreLaCarabine(B.defi);
    Adresse.fermer();
    Conduite.fermer();
    B.defi = null;
  }

  function finirDefi(reussi, raison) {
    const f = B.defi, d = defis().find(function (q) { return q.slug === f.slug; });
    rendreLaCarabine(f);
    Adresse.fermer();
    Conduite.fermer();
    B.defi = null;
    if (!reussi) { Hud.message('DÉFI RATÉ — ' + (raison || ''), 180); Son.SFX.erreur(); noter('DÉFI RATÉ : ' + d.titre, false); return; }
    const premiere = !B.partie.defisFaits[d.slug];
    B.partie.defisFaits[d.slug] = { jour: B.partie.jour, temps: f.t };
    // ⚠️ LE DEFI DU JOUR PAIE SA PRIME UNE FOIS PAR JOUR (date du serveur), en plus de celle de
    // la premiere fois : UN seul `encaisser`, donc un seul message — deux se recouvriraient.
    const duJour = Defi.aPayer(d.slug);
    if (duJour) Defi.noterFait(d.slug, f.t);
    const gain = (premiere ? d.prime : 0) + (duJour ? d.prime : 0);
    if (gain) {
      Missions.encaisser(gain, (duJour ? 'DÉFI DU JOUR — ' : '') + d.titre.toUpperCase(), true);
      Missions.annoncerPrime(gain, d.titre, duJour ? 'DÉFI DU JOUR' : 'DÉFI RÉUSSI', 0);
    } else {
      Hud.message(d.titre.toUpperCase() + ' — RÉUSSI', 180);
      Son.SFX.mission();
    }
    noter('DÉFI RÉUSSI : ' + d.titre + (gain ? ' — ' + gain + ' $' : ''), true);
    if (d.foire) lotDeLaFoire();
  }

  /** LE LOT DU TROISIÈME PALIER : la casquette de la foire.

      ⚠️ **La prime de ces trois-là est petite, et c'est la règle des paliers de
      boulot** — un jeu d'adresse ne paie pas mieux à l'heure qu'une course. Ce
      qu'on vient chercher au troisième, ce n'est pas l'argent : c'est la seule
      tenue du jeu qui ne s'achète pas (`magasins.TENUES`, champ `prime`). Le
      vestiaire existait déjà et n'apprend rien. */
  function lotDeLaFoire() {
    const p = B.partie;
    // ⚠️ C'est le CATALOGUE qui dit quelle tenue est le lot (`prime: 'foire'`),
    // pas un slug écrit ici : une deuxième vérité serait une tenue qu'on ne
    // peut plus gagner le jour où quelqu'un la renomme.
    const tenue = (B.defs.tenues || []).find(function (t) { return t.prime === 'foire'; });
    if (!tenue || p.tenues.indexOf(tenue.slug) >= 0) return;
    if (defisDeFoire().some(function (q) { return !p.defisFaits[q.slug]; })) return;
    p.tenues.push(tenue.slug);
    Hud.message('LES TROIS JEUX — ' + tenue.nom.toUpperCase(), 240);
    noter('LA FOIRE : ' + tenue.nom, true);
  }

  /** Le défi que vend ce comptoir-là (`ou: 'foire:<kiosque>'`), ou null. */
  function defiDuComptoir(slug) {
    // ⚠️ Un kiosque dont le defi est encore CACHE reste un kiosque : ACTION
    // passe au suivant de la chaine (`Missions.interagir`).
    return defis().find(function (d) { return d.ou === 'foire:' + slug && defiOuvert(d); }) || null;
  }

  // --- Les courses : un circuit, et on suit les fleches -------------------------------------------
  //: Martin, 21 sept. 2026 : « pour les courses, il faut un nouveau concept de
  //: fleches lumineuses sur la route qui trace le chemin de la course, pas des
  //: fleches avec les metres ». Puis le 22 : « pas besoin de point de passage,
  //: on doit suivre les fleches lumineuses au sol. Si on quitte, on a 5 sec pour
  //: revenir ou on doit recommencer. »
  //:
  //: Une course (`circuit` dans `missions.DEFIS`) est donc un CIRCUIT FERME, tire
  //: une fois au panneau sur la chaussee (`Monde.cheminRoute`), et on le suit.
  //: ⚠️ Il est FIXE : un trace recalcule depuis le char suivrait le joueur
  //: partout, et on ne pourrait jamais en sortir.

  //: Au-dela de cette distance du trace, on n'est plus sur la piste : une rue
  //: fait quatre ou six tuiles, on y choisit sa voie ; la rue d'a cote est a
  //: un pate de maisons.
  const HORS_PISTE_PX = 4 * TT;
  //: Cinq secondes pour revenir, puis la course est ratee.
  const HORS_PISTE_IMAGES = 300;
  //: Le temps de rejoindre la ligne de depart, une fois au volant — le chrono,
  //: lui, ne part que sur la ligne.
  const ATTENTE_DEPART = 1200;
  //: Ou l'on cherche ou l'on en est, en points du trace (seize pixels) : un peu
  //: derriere, assez devant pour un char lance. ⚠️ Pas plus : un bout du circuit
  //: qui repasse a cote, c'est un raccourci, pas la piste.
  const FENETRE_ARRIERE = 8, FENETRE_AVANT = 48;
  //: Le rectangle du quartier ou se posent les coins du circuit, rentre de sa
  //: bordure : on tourne DANS le quartier, pas sur le boulevard qui le borde.
  const COINS_DU_QUARTIER = [[0.2, 0.2], [0.8, 0.2], [0.8, 0.8], [0.2, 0.8]];

  /** Les ancres d'un circuit, dans l'ordre du tour. Les `points` nommes d'une
      course s'il y en a (le Tour du Faubourg et ses quatre batiments) ; sinon
      le batiment du panneau, puis trois coins du quartier (`carte.zones`) dans
      le sens du tour — le coin le plus pres du panneau saute, le panneau en
      tient lieu. Pas de hasard : le circuit ne depend que de la carte. */
  function ancresDuCircuit(d) {
    if (d.points) return d.points.map(lieu);
    const z = (Monde.carte.zones || []).find(function (q) { return q.slug === d.district; });
    const depart = lieu(d.ou.slice(6));
    if (!z || !depart) return [];
    const cx = (z.x + z.l / 2) * TT, cy = (z.y + z.h / 2) * TT;
    const a0 = Math.atan2(depart.y - cy, depart.x - cx);
    const ecart = function (p) {
      let e = Math.atan2(p.y - cy, p.x - cx) - a0;
      while (e <= 0) e += 2 * Math.PI;
      return e;
    };
    const coins = COINS_DU_QUARTIER.map(function (c) { return { x: (z.x + z.l * c[0]) * TT, y: (z.y + z.h * c[1]) * TT }; });
    coins.sort(function (a, b) { return dist2(a.x, a.y, depart.x, depart.y) - dist2(b.x, b.y, depart.x, depart.y); });
    return [depart].concat(coins.slice(1).sort(function (a, b) { return ecart(a) - ecart(b); }));
  }

  /** Le circuit ferme : ses ancres posees sur la chaussee, reliees bout a bout.
      Une liste de centres de tuiles (seize pixels d'un point au suivant), le
      depart en tete ; le dernier point touche le premier. null s'il manque un
      troncon — le defi se rate alors au depart, il ne ment pas en route. */
  function circuit(d) {
    const ancres = [];
    for (const a of ancresDuCircuit(d)) {
      const r = a && Monde.routeLaPlusProche(a.x, a.y, 16);
      if (r && !ancres.some(function (q) { return dist2(q.x, q.y, r.x, r.y) < (6 * TT) * (6 * TT); })) ancres.push(r);
    }
    if (ancres.length < 3) return null;
    const piste = [ancres[0]];
    for (let i = 0; i < ancres.length; i++) {
      const a = ancres[i], b = ancres[(i + 1) % ancres.length];
      const bout = Monde.cheminRoute(a.x, a.y, b.x, b.y);
      if (!bout || !bout.length) return null;
      for (const p of bout) piste.push(p);
    }
    piste.pop();
    return piste;
  }

  function distanceASegment(x, y, a, b) {
    const dx = b.x - a.x, dy = b.y - a.y, l2 = dx * dx + dy * dy;
    const t = l2 ? Math.max(0, Math.min(1, ((x - a.x) * dx + (y - a.y) * dy) / l2)) : 0;
    return Math.hypot(x - (a.x + dx * t), y - (a.y + dy * t));
  }

  /** Une image d'une course, au volant. Avant la ligne de depart : on la
      rejoint, sans chrono. Apres : on avance sur le trace, un tour vaut un
      circuit entier parcouru dans l'ordre, et hors piste le compte de cinq
      secondes part. */
  function majCircuit(d, f, v) {
    if (!v) { finirDefi(false, 'SANS CHAR, PAS DE COURSE'); return; }
    const p = f.piste;
    if (!p) { finirDefi(false, 'PAS DE CIRCUIT ICI'); return; }
    if (!f.enPiste) {
      if (dist2(v.x, v.y, p[0].x, p[0].y) < HORS_PISTE_PX * HORS_PISTE_PX) {
        f.enPiste = true; f.t = 0;
        Hud.message(d.titre.toUpperCase() + ' — GO ! SUIS LES FLÈCHES', 120);
      } else if (++f.attente > ATTENTE_DEPART) finirDefi(false, 'LA LIGNE DE DÉPART EST AU PANNEAU');
      return;
    }
    f.t++;
    if (d.chrono_s && f.t > d.chrono_s * 60) { finirDefi(false, 'TEMPS ÉCOULÉ'); return; }
    const n = p.length;
    let pas = 0, dMin = Infinity;
    for (let k = -FENETRE_ARRIERE; k <= FENETRE_AVANT; k++) {
      const e = distanceASegment(v.x, v.y, p[((f.i + k) % n + n) % n], p[((f.i + k + 1) % n + n) % n]);
      if (e < dMin) { dMin = e; pas = k; }
    }
    if (dMin > HORS_PISTE_PX) {
      if (f.hors === 0) { Hud.message('HORS PISTE — 5 S POUR REVENIR', 90); Son.SFX.erreur(); }
      if (++f.hors > HORS_PISTE_IMAGES) finirDefi(false, 'HORS PISTE');
      return;
    }
    f.hors = 0;
    f.i = ((f.i + pas) % n + n) % n;
    f.avance += pas;
    if (f.avance >= n * (f.tours + 1)) {
      f.tours++;
      if (f.tours >= d.tours) { finirDefi(true); return; }
      Hud.message('TOUR ' + f.tours + ' / ' + d.tours, 90);
    }
  }

  /** On roule sur le trace d'une course : le GPS se tait, les fleches parlent. */
  function estCourse() { return !!(B.defi && B.defi.enPiste); }

  /** Ce que le GPS vise pour une course : la ligne de depart tant qu'on ne l'a
      pas rejointe, puis un point de la piste devant soi (la mini-carte). */
  function repereDeCircuit(f) {
    if (!f.piste) return null;
    const p = f.enPiste ? f.piste[(f.i + 40) % f.piste.length] : f.piste[0];
    return { x: p.x, y: p.y, nom: f.enPiste ? 'LA PISTE' : 'LA LIGNE DE DÉPART' };
  }

  /** « — REVIENS ! 3 S » tant qu'on est hors piste, sinon rien. */
  function horsPiste(f) {
    return f.hors > 0 ? ' — REVIENS ! ' + Math.max(1, Math.ceil((HORS_PISTE_IMAGES - f.hors) / 60)) + ' S' : '';
  }

  //: Une fleche tous les deux points du trace (32 px), et combien on en montre.
  //: ⚠️ **UN POINT SUR DEUX DU CIRCUIT, PAS DU CHAR** (retour de Martin, 22 sept.
  //: 2026 : « les fleches clignotent quand on avance, il faudrait qu'elles restent
  //: fixes »). Comptees depuis le char, elles changeaient de parite a chaque tuile
  //: et sautaient de 16 px. Chacune a sa place sur la piste et n'en bouge plus :
  //: on les depasse, et les nouvelles naissent loin devant, hors de l'ecran.
  const COURSE_PAS_POINTS = 2, COURSE_FLECHES_MAX = 24;

  function chevron(ctx, e) {
    ctx.beginPath();
    ctx.moveTo(7 * e, 0); ctx.lineTo(-4 * e, -6 * e); ctx.lineTo(-1 * e, 0); ctx.lineTo(-4 * e, 6 * e);
    ctx.closePath();
    ctx.fill();
  }

  /** Une fleche lumineuse : un halo, puis le trait clair par-dessus. */
  function dessinerFlecheDeCourse(ctx, x, y, angle) {
    ctx.save();
    ctx.translate(x, y);
    ctx.rotate(angle);
    ctx.globalAlpha = 0.35;
    ctx.fillStyle = '#3fb8ff';
    chevron(ctx, 1.6);
    ctx.globalAlpha = 1;
    ctx.fillStyle = '#b8f1ff';
    chevron(ctx, 1);
    ctx.restore();
  }

  /** Les fleches de la piste a l'ecran : devant le char (sur la ligne de depart
      tant qu'on ne l'a pas rejointe), en pixels d'ecran. Leur lumiere est fixe. */
  function flechesALEcran(vue) {
    const f = B.defi, out = [];
    if (!f || !f.piste) return out;
    const p = f.piste, n = p.length;
    for (let j = 1, m = 0; j <= n && m < COURSE_FLECHES_MAX; j++) {
      // Un circuit ferme, pas a pas sur la grille, a toujours un nombre PAIR de
      // points : la ligne de depart se franchit sans que le pas de 32 px casse.
      const k = (f.i + j) % n;
      if (k % COURSE_PAS_POINTS) continue;
      m++;
      const a = p[k], b = p[(k + COURSE_PAS_POINTS) % n];
      if (!Entites.visibleAEcran(a.x, a.y, 16)) continue;
      out.push({ x: a.x - vue.x, y: a.y - vue.y, angle: Math.atan2(b.y - a.y, b.x - a.x) });
    }
    return out;
  }

  /** Le trace au sol, sous les chars et les gens. */
  function dessinerCheminCourse(ctx, vue) {
    for (const q of flechesALEcran(vue)) dessinerFlecheDeCourse(ctx, q.x, q.y, q.angle);
  }

  /** ⚠️ **LUMINEUSES, MEME LA NUIT.** Peintes au sol, les fleches s'eteignent
      avec la ville quand la nuit tombe (`Base.fin` assombrit tout ce qui est
      peint avant elle) : on ne les voyait plus que dans ses phares. Chacune
      pose donc sa petite lampe, fixe comme elle. Poussees APRES les phares :
      si l'ecran deborde du plafond de lampes (`LAMPES_MAX`), ce sont elles
      qui sautent, pas un lampadaire. */
  function lampesDeCourse(vue) {
    return flechesALEcran(vue).map(function (q) {
      return { x: q.x, y: q.y, r: 18, c: 'rgba(120,210,255,0.6)' };
    });
  }

  // --- Le GPS : ou aller, pour le HUD ------------------------------------------------------------

  /** La cible du moment : un objectif, un appel a honorer, un defi en cours. */
  function cible() {
    const m = courante(), p = B.partie, j = B.joueur;
    if (!j) return null;
    if (B.defi) {
      const d = defis().find(function (q) { return q.slug === B.defi.slug; });
      const l = d.conduite ? Conduite.cible(d) : d.circuit ? repereDeCircuit(B.defi) : d.lieu ? lieu(d.lieu) : null;
      return l ? { x: l.x, y: l.y, nom: l.nom, couleur: '#7fc4ff' } : null;
    }
    if (m) {
      const o = m.objectifs[p.mission.etape];
      if (!o) return null;
      let l = null;
      if (o.type === 'aller') l = lieu(o.lieu);
      else if (o.type === 'livrer') l = lieuDeLivraison(o.lieu);
      else if (o.type === 'monter') l = B.mission && B.mission.vehicule ? B.mission.vehicule : null;
      else if (o.type === 'retourner') l = ouTrouver(m.donneur);
      else if (o.type === 'ramasser') l = B.mission && (B.mission.entites.find(function (e) { return e.objet === 'caisse'; }) || B.mission.entites.find(function (e) { return e.porteLaCaisse && e.vivant && e.etat !== 'assomme'; }) || (!B.mission.fuyardTombe ? B.mission.fuyard : null));
      else if (o.type === 'tuer') { const restants = B.mission ? B.mission.entites.filter(function (e) { return e.cible && e.vivant && e.etat !== 'assomme'; }) : []; l = restants[0] || null; }
      // ⚠️ `parler` : la cible est un PERSONNAGE, pas un lieu. On pointe sa
      // personne quand elle est dehors (Ti-Paul, Raymonde), sinon sa porte (Lulu
      // à la cantine, Ovila au phare). Sans ce cas, m6 n'avait ni flèche ni
      // repère — on cherchait quatre personnes à l'aveugle.
      else if (o.type === 'parler') {
        const slug = cibleDuParler(o);
        if (slug) {
          const ou = ouTrouver(slug);
          const qui = personnage(slug);
          if (ou && qui) l = { x: ou.x, y: ou.y, nom: qui.nom };
        }
      }
      // --- M16 : les neuf types de plus — le même repère que leurs cousins
      // (`ramasser` pour `suivre`, `tuer` pour `pickpocket`, `monter` pour
      // `detruire`). `payer` et `boulots` n'ont pas de pixel à pointer : on
      // parle à qui est là, ou on roule au klaxon.
      else if (o.type === 'suivre') l = B.mission ? B.mission.suivi : null;
      else if (o.type === 'proteger') {
        // Lui d'abord, tant qu'on ne l'a pas rejoint ; puis où on l'emmène.
        const c = B.mission ? B.mission.protege : null;
        l = (c && !c.suit) ? c : ((o.lieu && lieu(o.lieu)) || c);
      }
      else if (o.type === 'pickpocket') l = B.mission ? B.mission.entites.find(function (e) { return e.pickpocket && e.vivant; }) : null;
      else if (o.type === 'detruire') l = B.mission && B.mission.chars ? B.mission.chars[p.mission.etape] : null;
      else if (o.type === 'sauter') l = resoudre(o.ou, m);
      else if (o.type === 'acheter') l = resoudre(o.ou, m);
      // ⚠️ `pirater` : le terminal, sur le POSTE quand il est sur un mouillage (le quai, là où
      // `piratageSousLaMain` l'ouvre). Sans ce cas, un terminal loin du donneur (l'île de m53,
      // m54) n'avait ni flèche ni repère.
      else if (o.type === 'pirater') { const t = resoudre(o.ou, m); l = t && t.mouillage ? t.mouillage.poste : t; }
      return l ? { x: l.x, y: l.y, nom: (l.nom || o.texte), couleur: '#e8b33c' } : null;
    }
    // Un appel recu : le donneur a aller voir.
    const attendue = disponibles().find(function (q) { return p.appels[q.slug]; }) || disponibles().find(function (q) { return !q.prerequis.length; });
    if (attendue) { const l = ouTrouver(attendue.donneur); const perso = personnage(attendue.donneur); return l ? { x: l.x, y: l.y, nom: perso.nom, couleur: '#8ad26a' } : null; }
    // Un feu de bâtiment (P4) : pas de mission, pas d'appel — le feu est la
    // seule chose à chercher, et il se pointe comme un objectif.
    if (typeof Incendies !== 'undefined') { const fe = Incendies.cible(); if (fe) return fe; }
    return null;
  }

  /** La ligne d'objectif que le HUD ecrit en haut : mission, objectif, compte. */
  /** Où en est la filature, au bout de la ligne d'objectif : le joueur doit VOIR
      qu'il est trop près ou qu'il le perd avant que ça rate. */
  function filature(bm) {
    if (bm.suivi.attendLeJoueur) return ' — PRENDS UN CHAR';
    if (bm.perdu > 0) return ' — TU LE PERDS ! ' + Math.max(1, Math.ceil((SUIVI_PERDU - bm.perdu) / 60)) + ' S';
    if (bm.tropPres) return ' — TROP PRÈS !';
    return '';
  }

  function ligneObjectif() {
    const m = courante();
    if (B.defi) {
      const d = defis().find(function (q) { return q.slug === B.defi.slug; });
      const reste = d.chrono_s ? Math.max(0, d.chrono_s * 60 - B.defi.t) : null;
      const chrono = reste === null ? '' : ' ' + Math.floor(reste / 3600) + ':' + ('0' + Math.floor(reste % 3600 / 60)).slice(-2);
      if (!B.defi.parti) return d.titre.toUpperCase() + chrono + ' — MONTE DANS UN CHAR';
      // ⚠️ Les jeux de foire comptent aussi, et le CANARD dit « MAINTENANT » :
      // la fenêtre dure moins d'une demi-seconde, et un joueur qui ne voit pas
      // le fil descendre sur le bassin n'a rien pour savoir quand appuyer.
      if (d.cibles) {
        const crevees = typeof Foire === 'undefined' ? 0 : Foire.cibles().filter(function (c) { return c.brise; }).length;
        return d.titre.toUpperCase() + chrono + ' CIBLES ' + Math.min(crevees, d.cibles) + '/' + d.cibles;
      }
      if (d.epreuve) return d.titre.toUpperCase() + chrono + ' ' + Adresse.compte(d);
      if (d.conduite) return d.titre.toUpperCase() + chrono + ' ' + Conduite.compte(d);
      if (d.coups) return d.titre.toUpperCase() + chrono + ' COUPS ' + B.defi.coups + '/' + d.coups;
      if (d.canards) return d.titre.toUpperCase() + chrono + ' CANARDS ' + B.defi.pris + '/' + d.canards
             + (canardAuCrochet() ? ' — MAINTENANT !' : '');
      if (d.circuit) {
        return d.titre.toUpperCase() + chrono + (B.defi.enPiste
          ? ' TOUR ' + Math.min(B.defi.tours + 1, d.tours) + '/' + d.tours + horsPiste(B.defi)
          : ' — REJOINS LA LIGNE DE DÉPART');
      }
      const compte = d.vol_px ? ' VOL ' + Math.round(B.defi.vol) + '/' + d.vol_px : '';
      return d.titre.toUpperCase() + chrono + compte;
    }
    if (!m) return null;
    const o = m.objectifs[B.partie.mission.etape];
    if (!o) return null;
    if (B.mission && B.mission.attend) return B.mission.attend;
    let compte = '';
    if (o.type === 'tuer') compte = ' ' + (B.mission ? B.mission.kos : 0) + '/' + o.n;
    if (o.type === 'courses') compte = ' ' + (B.mission ? B.mission.courses : 0) + '/' + o.n;
    // --- M16 : `boulots` compte comme `courses`, `sauter` comme le Grand Saut.
    if (o.type === 'boulots' && B.mission) {
      const faits = (typeof Missions !== 'undefined' ? Missions.boulot.faits[o.sorte] : 0) || 0;
      compte = ' ' + Math.max(0, faits - B.mission.boulotsDepart) + '/' + o.n;
    }
    if (o.type === 'sauter') compte = ' VOL ' + Math.round(B.mission ? B.mission.vol : 0) + '/' + o.vol_px;
    if (o.type === 'suivre' && B.mission && B.mission.suivi) compte = filature(B.mission);
    return o.texte + compte;
  }

  // --- La boucle -------------------------------------------------------------------------------

  /** Les bulles des donneurs : celui qui a quelque chose pour toi t'interpelle,
      les autres se taisent.

      ⚠️ C'est la SEULE chose qui distingue un donneur d'un figurant. Dans une
      piece, Bouchard est un pieton de plus, assis devant un mur de tuiles ; la
      bulle dit qu'il attend apres toi, et elle s'eteint des qu'il n'attend
      plus rien — sinon elle ne voudrait plus rien dire. */
  function majBulles() {
    const m = courante(), o = objectif();
    for (const e of B.entites) {
      if (!e.personnage || !e.vivant) continue;
      const attend = (m && m.donneur === e.personnage && o && o.type === 'retourner') || !!disponibleDe(e.personnage);
      const p = attend ? personnage(e.personnage) : null;
      Entites.bulle(e, p ? p.heler : '');
    }
  }

  function maj() {
    if (!B.joueur || !B.partie) return;
    majCinema();
    if (B.cinema) return;
    jouerLaFin();
    if (B.cinema) return;
    majBulles();
    majRetours();
    majTelephone();
    majProtege();
    if (B.partie.mission) {
      if (!B.mission) B.mission = { entites: [], vehicule: null, chars: {}, fuyard: null, chef: null, escorte: null, courses: 0, kos: 0,
                                    vol: 0, boulotsDepart: 0, suit: null, protege: null, suivi: null };  // partie rechargee : on reprend au meme objectif, sans ses figurants
      if (B.mission.pendant !== undefined && B.mission.pendant !== null) {
        const etape = B.mission.pendant;
        B.mission.pendant = null;
        dire(courante(), 'pendant', null, function (l) { return l.objectif === etape; });
        return;
      }
      if (!B.interieur) {
        majObjectif();
      }
    }
    majDefi();
    majDeblocages(false);
  }

  return { disponibles, disponibleDe, personnage, personnageSousLaMain, personnageDuPoint, pieceDuPoint,
           donneur, creerDonneurs, poserDonneur, creerDonneursDedans, creerPanneaux, panneauSousLaMain,
           parler, dire, suivante, finir, commencer, demarrer, avancer, objectif, courante, reussir, echouer, evenement,
           ouverture, passerOuverture, fichiersDeLOuverture, direLignes, majCinema, resoudre,
           lieuDuPersonnage, ouTrouver, present, calme, jouerOuDire,
           reinitialiser, noter, rencontrer, CARNET_MAX,
           proposerDefi, commencerDefi, finirDefi, abandonnerDefi, actionDeDefi, defisDeFoire, comptoirDeDefi, defiDuComptoir, canardAuCrochet,
           appareilsDe, jouableAvec, defiOuvert, defisOuverts, defiNeuf, ouvrirDefi, majDeblocages, planterLesPanneauxOuverts, APPAREIL_DU_CATALOGUE,
           cible, ligneObjectif, lieu, lieuDeLivraison, ruellePres, tuileLibre, tuileDeRue, slugDeVoix, cibleDuParler, maj,
           piratageSousLaMain, commencerPiratage, estCourse, dessinerCheminCourse, lampesDeCourse };
})();
