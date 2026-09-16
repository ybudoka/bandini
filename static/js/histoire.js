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

  /** Les missions qu'on peut commencer : prerequis faits, pas encore faites, aucune en cours. */
  function disponibles() {
    if (B.partie.mission) return [];
    return defs().filter(function (m) { return !faite(m.slug) && m.prerequis.every(faite); });
  }

  function disponibleDe(donneur) {
    return disponibles().find(function (m) { return m.donneur === donneur; }) || null;
  }

  // --- Les lieux -------------------------------------------------------------------------

  function point(slug) { return Monde.carte.points.find(function (p) { return p.slug === slug; }) || null; }

  /** Le pixel d'un lieu nomme : la tuile devant sa porte. Les lieux speciaux
      sont des points d'interet ; le kiosque, lui, n'est qu'une porte. */
  function lieu(slug) {
    const p = point(slug);
    if (p) return { x: p.x * TT + 8, y: p.y * TT + 8, nom: p.nom };
    const porte = (Monde.carte.def.portes || []).find(function (q) { return q.lieu === slug; });
    if (porte) {
      const inte = Monde.carte.def.interieurs && Monde.carte.def.interieurs[porte.interieur];
      return { x: porte.x * TT + 8, y: (porte.y + 1) * TT + 8, nom: inte ? inte.nom : slug };
    }
    return null;
  }

  /** Une tuile marchable pres d'un pixel, hors chaussee, en spirale. */
  function tuileLibre(x, y, rayonMax) {
    const tx = Math.floor(x / TT), ty = Math.floor(y / TT);
    for (let r = 0; r <= (rayonMax || 4); r++) {
      for (let dy = -r; dy <= r; dy++) for (let dx = -r; dx <= r; dx++) {
        if (Math.max(Math.abs(dx), Math.abs(dy)) !== r) continue;
        if (Monde.marchablePieton(tx + dx, ty + dy) && !Monde.estChaussee(tx + dx, ty + dy)) return { x: (tx + dx) * TT + 8, y: (ty + dy) * TT + 8 };
      }
    }
    return null;
  }

  /** Une tuile de rue (avec une fleche) pres d'un pixel : la ou un char peut naitre. */
  function tuileDeRue(x, y, rayonMax) {
    const tx = Math.floor(x / TT), ty = Math.floor(y / TT);
    for (let r = 1; r <= (rayonMax || 8); r++) {
      for (let dy = -r; dy <= r; dy++) for (let dx = -r; dx <= r; dx++) {
        if (Math.max(Math.abs(dx), Math.abs(dy)) !== r) continue;
        const f = Monde.fleche(tx + dx, ty + dy);
        if (f === '>' || f === '<' || f === '^' || f === 'v') return { x: (tx + dx) * TT + 8, y: (ty + dy) * TT + 8, sens: f };
      }
    }
    return null;
  }

  /** La ruelle (glyphe `x`) la plus proche d'un lieu — la ou dort le char de M1. */
  function ruellePres(slug) {
    const p = point(slug), c = Monde.carte;
    if (!p) return null;
    let meilleur = null, dMin = Infinity;
    for (let ty = 1; ty < c.h - 1; ty++) for (let tx = 1; tx < c.w - 1; tx++) {
      if (Monde.glyphe(tx, ty) !== 'x') continue;
      const d = dist2(tx, ty, p.x, p.y);
      if (d < dMin) { dMin = d; meilleur = { x: tx * TT + 8, y: ty * TT + 8 }; }
    }
    return meilleur;
  }

  /** `ou` d'un objectif ou d'un personnage → un pixel. */
  function resoudre(ou, m) {
    if (!ou) return null;
    if (ou === 'donneur') return ouTrouver(m.donneur);
    const deux = ou.split(':');
    if (deux[0] === 'porte') return lieu(deux[1]);
    if (deux[0] === 'ruelle') return ruellePres(deux[1]);
    if (deux[0] === 'zone') { const z = Monde.carte.zones.find(function (q) { return q.slug === deux[1]; }); return z ? { x: (z.x + z.l / 2) * TT, y: (z.y + z.h / 2) * TT, zone: z } : null; }
    if (deux[0] === 'point') return null;                 // dedans : pas de pixel en ville
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

  /** Pose les personnages qui se tiennent DEHORS, a cote de leur porte. Ti-Guy
      attend au terminus tant que M1 n'est pas faite ; les autres sont chez eux. */
  function creerDonneurs() {
    for (const p of personnages()) {
      if (p.ou.indexOf('porte:') !== 0) continue;                 // les autres sont dedans
      if (p.slug === 'ti_guy' && faite('m1')) continue;
      const l = lieu(p.ou.slice(6));
      if (!l) continue;
      // A deux tuiles de la porte : assez pres pour le voir, assez loin pour
      // qu'ACTION au pas de la porte serve encore a autre chose.
      const place = tuileLibre(l.x + 2 * TT, l.y, 3) || tuileLibre(l.x - 2 * TT, l.y, 3);
      if (!place) continue;
      creerPersonnage(p, place.x, place.y);
    }
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
                   temoin: 0, vie: 100, argent: [0, 0], arme: null, intouchable: true, metier: 'histoire' };
    const e = Entites.creerPieton(x, y, arch);
    e.personnage = p.slug; e.etat = 'fige'; e.cri = 0;
    return e;
  }

  /** Le personnage a portee d'ACTION, s'il y en a un. */
  function personnageSousLaMain(j) {
    return Entites.pietonsAutour(j.x, j.y, RAYON_PARLER).find(function (e) { return e.personnage; }) || null;
  }

  // --- Les dialogues, dits a voix haute ----------------------------------------------------

  /** Une suite de repliques. Le joueur ecoute : ACTION passe a la suivante, et
      la voix finie (ou le texte lu) passe toute seule. `fin` s'appelle apres. */
  function dire(m, partie, fin) {
    const lignes = ((m && m.dialogue && m.dialogue[partie]) || []).map(function (l, i) {
      return { qui: l.qui, texte: l.texte, telephone: partie === 'appel', slug: slugDeVoix(m, partie, i) };
    });
    if (!lignes.length) { if (fin) fin(); return false; }
    Son.Voix.chargerHistoire(m.slug);
    B.cinema = { lignes: lignes, i: -1, t: 0, duree: 0, fin: fin || null, mission: m.slug, partie: partie };
    Entree.contexte('dialogue');
    suivante();
    return true;
  }

  /** Le slug de voix d'une replique : `<qui>-<mission>-<n>`, n compte a travers
      appel, intro, client, fin, echec — exactement comme `missions.repliques()`. */
  function slugDeVoix(m, partie, i) {
    const ordre = ['appel', 'intro', 'client', 'fin', 'echec'];
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
    c.t = 0;
    c.duree = 90 + l.texte.length * 3;                      // le temps de lire, si la voix manque
    // ⚠️ `anonyme` : l'ouverture n'a personne au-dessus de sa boite — c'est une
    // voix qu'on entend, pas quelqu'un a qui l'on parle. Le Clairon se
    // presentera demain matin, avec sa manchette.
    Hud.dialogue(c.anonyme ? '' : (p ? p.nom : l.qui) + (l.telephone ? ' (AU TÉLÉPHONE)' : ''), decouper(l.texte), 0);
    c.voix = Son.Voix.parler(l.slug, { telephone: l.telephone, fin: function () { if (B.cinema === c && c.i === c.lignes.indexOf(l)) c.duree = Math.min(c.duree, c.t + 20); } });
  }

  function finir() {
    const c = B.cinema;
    B.cinema = null;
    B.dialogue = null;
    Son.Voix.couper();
    // ⚠️ Pendant l'ouverture, la derniere replique ne rend PAS les commandes :
    // la scene tourne encore (le car repart, le titre s'inscrit) et PASSER doit
    // rester PASSER jusqu'au bout.
    Entree.contexte(B.ouverture ? 'dialogue' : B.joueur && B.joueur.dansVehicule ? 'vehicule' : 'pied');
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
    const parle = !!(l && Son.Voix.enCours && Son.Voix.enCours.slug === l.slug) && c.t < c.duree + 900;
    if (Entree.neuf('action') || Entree.neuf('attaque') || (c.t > c.duree && !parle)) suivante();
  }

  // --- L'OUVERTURE : le car de six heures ---------------------------------------------------

  /*: LA SCENE, en images (60 = une seconde). ⚠️ Elle est plus COURTE que la
    narration, et c'est voulu : le car arrive, on descend, il repart, et le
    narrateur finit sa phrase sur la ville — pas sur un autobus arrete au milieu
    de la rue. L'ouverture se termine quand les DEUX sont finis (la scene ET les
    quatre repliques), jamais au premier des deux. */
  const OUV = { noir: 45, arrivee: 170, porte: 70, depart: 130, titre: 30, tenu: 150 };

  /*: D'ou le car arrive, et ou il s'en va, en pixels : hors champ des deux
    cotes (l'ecran fait 480 de large). Un car qui apparait dans le cadre ne
    s'est jamais approche, il s'est allume. */
  const OUV_LOIN = 330;

  /** L'ouverture : le car de six heures entre au terminus, le bonhomme en
      descend, et le narrateur dit d'ou l'on vient.

      ⚠️ ELLE NE TIRE AUCUN DE. Le car recoit sa couleur en clair (`creer` en
      tirerait une), aucune particule n'est semee au hasard, et la ville est
      figee pendant qu'elle joue : une partie jouee avec l'ouverture doit etre
      exactement la meme qu'une partie jouee sans — c'est ce qu'un juge du banc
      verifie, et c'est la seule facon qu'une animation ne change pas le jeu.

      ⚠️ ET ELLE NE PART PAS AU CHARGEMENT DE LA PAGE : le navigateur retient le
      son tant que personne n'a touche, et une introduction audio muette n'est
      pas une introduction. C'est `Jeu.jouer()` qui l'appelle, apres le geste.

      Rend `false` si la scene est impossible (pas de rue devant le terminus) :
      la partie commence alors comme avant, sans rien dire. */
  function ouverture(rejoue) {
    const j = B.joueur;
    if (!j || B.ouverture || B.interieur) return false;
    const porte = lieu('terminus');
    const arret = porte && tuileDeRue(porte.x, porte.y, 10);
    if (!porte || !arret) return false;
    const def = Vehicules.vehiculeDef('autobus');
    if (!def) return false;
    const sens = arret.sens;
    const angle = sens === '<' ? Math.PI : sens === '^' ? -Math.PI / 2 : sens === 'v' ? Math.PI / 2 : 0;
    const dx = Math.cos(angle), dy = Math.sin(angle);
    // ⚠️ La couleur EN CLAIR : `Vehicules.creer` en tire une du catalogue
    // sinon, et un de tire ici decale tous ceux qui suivent — le trafic et la
    // foule de la partie ne seraient plus les memes selon qu'on a regarde
    // l'ouverture ou qu'on l'a passee.
    const car = Vehicules.creer('autobus', arret.x - dx * OUV_LOIN, arret.y - dy * OUV_LOIN, angle,
                                { couleur: def.couleurs[0], etat: 'stationne' });
    if (!car) return false;
    j.dessine = false;                       // il est dans le car : on ne le voit pas encore
    j.vx = 0; j.vy = 0;
    // ⚠️ DEUX ENDROITS, ET ILS NE SONT LE MEME QU'AU PREMIER MATIN. `quai` est
    // la ou l'on descend du car ; `retour` la ou l'on etait avant la scene.
    //   - Partie neuve : on descend LA OU L'ON SERAIT NE sans l'ouverture (sa
    //     tuile d'apparition, devant le terminus) — c'est ce qui fait qu'une
    //     partie avec l'ouverture est exactement celle qu'on aurait sans.
    //   - REVUE du carnet : on est peut-etre a l'autre bout de la ville. La
    //     scene se joue quand meme au terminus (c'est la qu'est le car), le
    //     bonhomme y est prete le temps de la revoir — il est invisible et la
    //     ville est figee, personne ne le voit voyager — et il revient chez lui
    //     a la derniere image. Sans `retour`, revoir l'ouverture te teleporterait
    //     au terminus : une animation qui deplace le joueur n'est plus une
    //     animation.
    const chezLui = { x: j.x, y: j.y };
    B.ouverture = {
      t: 0, car: car, angle: angle, dx: dx, dy: dy,
      arret: { x: arret.x, y: arret.y },
      quai: rejoue ? { x: porte.x, y: porte.y } : chezLui,
      retour: chezLui,
      rejoue: !!rejoue,
      noir: 1, titre: 0, descendu: false, parti: false, scene: false,
    };
    // La camera part sur la rue d'ou le car arrive, et remonte avec lui.
    B.ouverture.vise = { x: arret.x - dx * 80, y: arret.y - dy * 80 };
    Monde.centrerCamera(B.ouverture.vise.x, B.ouverture.vise.y);
    Son.Voix.chargerHistoire('ouverture');
    Son.Mus.jouer('ouverture');
    Son.boucle('moteur', true);
    Entree.contexte('dialogue');
    direOuverture();
    return true;
  }

  /** Les quatre phrases du narrateur. ⚠️ Elles viennent du PAQUET
      (`missions.repliques_ouverture()`), avec leur slug de voix deja calcule :
      le navigateur ne refait pas la regle du slug, il la lit. */
  function direOuverture() {
    const lignes = (B.defs.ouverture || []).map(function (l) {
      return { qui: l.qui, texte: l.texte, telephone: false, slug: l.slug };
    });
    if (!lignes.length) return false;
    B.cinema = { lignes: lignes, i: -1, t: 0, duree: 0, fin: null, mission: 'ouverture', partie: 'ouverture',
                 // ⚠️ Sans nom au-dessus de la boite : c'est une voix qu'on
                 // entend, pas quelqu'un a qui l'on parle. Le Clairon se
                 // presentera bien assez tot, demain matin.
                 anonyme: true };
    suivante();
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

  /** Une image de la scene. La ville est figee (voir `Jeu.maj`) : ici bougent le
      car, la camera, le noir, le titre — et la replique en cours. */
  function majOuverture() {
    const o = B.ouverture, j = B.joueur;
    if (!o || !j) return;
    o.t++;
    o.noir = Math.max(0, 1 - o.t / OUV.noir);
    const finArrivee = OUV.arrivee, finPorte = finArrivee + OUV.porte, finDepart = finPorte + OUV.depart;
    if (o.t <= finArrivee) {
      // Le car entre et ralentit : l'approche freine, elle ne glisse pas.
      const u = o.t / finArrivee, k = 1 - Math.pow(1 - u, 3);
      placerLeCar(o, -OUV_LOIN * (1 - k));
      o.vise.x = o.arret.x - o.dx * 80 * (1 - k);
      o.vise.y = o.arret.y - o.dy * 80 * (1 - k);
      Monde.centrerCamera(o.vise.x, o.vise.y);
      if (o.t === finArrivee) { Son.SFX.porte_vehicule(); fumee(o, 6); }
    } else if (o.t <= finPorte) {
      // Arret. Les portes s'ouvrent, et quelqu'un descend.
      placerLeCar(o, 0);
      // ⚠️ IL DESCEND, PUIS IL MARCHE — il n'apparait pas a la porte. Pose
      // d'un coup sur sa tuile d'apparition (a trois tuiles de la), la scene se
      // lisait « quelqu'un s'allume sur le trottoir » et non « quelqu'un sort du
      // car ». Il nait donc A COTE DU CAR et rejoint le quai a pied, le temps de
      // l'arret. C'est la scene qui bouge ses jambes (`anim.dist`, `face`) :
      // `Entites.majJoueur` ne tourne pas pendant l'ouverture.
      if (!o.descendu && o.t > finArrivee + 14) {
        o.descendu = true;
        o.marcheT = o.t;
        j.dessine = true;
        // ⚠️ DU BON COTE DU CAR, et ce n'est pas toujours le meme : la rue du
        // terminus peut courir dans les quatre sens selon la carte generee. On
        // sort donc du cote OU L'ON VA (le trottoir), jamais du cote fixe — un
        // bonhomme qui descend dans la voie d'en face traverserait la rue a
        // pied pendant que son car repart.
        const px = o.dy, py = -o.dx;
        const vers = ((o.quai.x - o.car.x) * px + (o.quai.y - o.car.y) * py) >= 0 ? 1 : -1;
        j.x = o.car.x - o.dx * 6 + px * 12 * vers;
        j.y = o.car.y - o.dy * 6 + py * 12 * vers;
        o.portiere = { x: j.x, y: j.y };
        Son.SFX.pas();
      }
      if (o.descendu) marcherVersLeQuai(o, j);
      viser(o, o.descendu ? o.quai : o.arret, 0.06);
    } else if (o.t <= finDepart) {
      // Il repart. ⚠️ Le car s'EN VA pour de vrai (on le retire) : un autobus
      // gare devant le terminus jusqu'a la fin des temps serait un char de plus
      // a voler, ne au premier geste de la partie.
      const u = (o.t - finPorte) / OUV.depart;
      placerLeCar(o, OUV_LOIN * u * u);
      if (o.t === finPorte + 1) { Son.SFX.porte_vehicule(); fumee(o, 10); }
      viser(o, o.quai, 0.06);
    } else {
      if (!o.parti) { o.parti = true; Entites.retirer(o.car); Son.boucle('moteur', false); }
      // ⚠️ LE TITRE MONTE, TIENT, PUIS S'EN VA. La narration dure quatre voix
      // (une vingtaine de secondes) et la scene sept : un titre laisse allume
      // jusqu'au bout tiendrait quinze secondes sur un ecran fixe. Il s'inscrit,
      // on le lit, et la ville reste — c'est elle qu'on est venu voir.
      o.titreT = (o.titreT || 0) + 1;
      o.titre = o.titreT <= OUV.titre ? o.titreT / OUV.titre
              : o.titreT <= OUV.titre + OUV.tenu ? 1
              : Math.max(0, 1 - (o.titreT - OUV.titre - OUV.tenu) / OUV.titre);
      o.scene = true;
      viser(o, o.quai, 0.08);
    }
    // ⚠️ `majCinema()` ET PAS `maj()`. La replique avance, et elle SEULE :
    // `maj()` enchaine sur les bulles, le telephone, l'objectif et les defis
    // des que la derniere phrase est dite — c'est-a-dire au milieu de la scene.
    // Un appel de mission qui sonne pendant l'ouverture remplacerait `B.cinema`
    // par le sien, et la scene attendrait la fin d'un dialogue qu'elle n'a
    // jamais demande.
    majCinema();
    if (o.scene && !B.cinema) finirOuverture();
  }

  /** Les quelques pas de la portiere au trottoir, en ligne droite. Le monde est
      fige : c'est ici qu'on avance ses jambes, sinon il glisserait sans marcher. */
  function marcherVersLeQuai(o, j) {
    const reste = Math.max(1, OUV.porte - 14);
    const u = Math.min(1, (o.t - o.marcheT) / reste);
    const ax = j.x, ay = j.y;
    j.x = o.portiere.x + (o.quai.x - o.portiere.x) * u;
    j.y = o.portiere.y + (o.quai.y - o.portiere.y) * u;
    const dx = j.x - ax, dy = j.y - ay;
    j.vx = dx; j.vy = dy;
    j.anim.dist += Math.abs(dx) + Math.abs(dy);
    if (Math.abs(dx) + Math.abs(dy) > 0.05) {
      j.face = Math.abs(dx) >= Math.abs(dy) ? (dx > 0 ? 'droite' : 'gauche') : (dy > 0 ? 'bas' : 'haut');
    } else { j.vx = 0; j.vy = 0; }
    Entites.dansLaCarte(j);
  }

  function placerLeCar(o, avance) {
    const v = o.car;
    v.x = o.arret.x + o.dx * avance; v.y = o.arret.y + o.dy * avance;
    // ⚠️ A L'ARRET AU SENS DE LA PHYSIQUE, toujours : la scene POSE le car, elle
    // ne le conduit pas. Une vitesse ici et il continuerait tout seul l'image
    // ou la ville se remet a tourner — au milieu de la rue, sans conducteur.
    v.vx = 0; v.vy = 0; v.vitesse = 0; v.angle = o.angle;
  }

  /** Le pot d'echappement. ⚠️ Des angles FIXES : `Entites.poussiere` tire des
      des, et l'ouverture n'en tire aucun. */
  function fumee(o, n) {
    const v = o.car, ax = -o.dx, ay = -o.dy;
    for (let i = 0; i < n; i++) {
      const e = (i / n - 0.5) * 0.9;
      Entites.particule(v.x + ax * (v.def.longueur / 2), v.y + ay * (v.def.longueur / 2),
                        ax * 0.5 + e * 0.3, ay * 0.5 + e * 0.3, 18, '#9a958c', 1, 0.02);
    }
  }

  function viser(o, cible, part) {
    o.vise.x += (cible.x - o.vise.x) * part;
    o.vise.y += (cible.y - o.vise.y) * part;
    Monde.centrerCamera(o.vise.x, o.vise.y);
  }

  /** PASSER : on saute tout, et on tombe exactement la ou l'ouverture nous
      aurait laisses. ⚠️ Une ouverture qu'on ne peut pas passer devient une
      punition a la deuxieme partie. */
  function passerOuverture() {
    if (!B.ouverture) return false;
    Son.Voix.couper();
    B.cinema = null; B.dialogue = null;
    finirOuverture();
    return true;
  }

  function finirOuverture() {
    const o = B.ouverture, j = B.joueur;
    if (!o) return;
    B.ouverture = null;
    if (!o.parti && o.car) Entites.retirer(o.car);
    Son.boucle('moteur', false);
    Son.Voix.couper();
    B.cinema = null; B.dialogue = null;
    if (j) {
      const ou = o.rejoue ? o.retour : o.quai;
      j.dessine = true; j.x = ou.x; j.y = ou.y; j.vx = 0; j.vy = 0;
      Entites.dansLaCarte(j);
      Monde.centrerCamera(j.x, j.y);
    }
    Entree.contexte('pied');
    Son.Mus.arreter();                       // la ville reprend la main
    Son.Chef.maj();
    // ⚠️ ELLE NE SE REJOUE PAS. Le drapeau part dans la sauvegarde tout de
    // suite : quelqu'un qui regarde l'ouverture puis ferme l'onglet ne doit pas
    // la revoir a son retour. Il la revoit quand IL le demande (le carnet).
    if (!o.rejoue && B.partie) {
      B.partie.ouvertureVue = true;
      if (typeof Missions !== 'undefined' && Missions.sauvegarderPartie) Missions.sauvegarderPartie();
      Hud.message('BAIE-DES-BRUMES', 150);
    }
  }

  // --- Le telephone ------------------------------------------------------------------------

  function majTelephone() {
    const p = B.partie;
    if (B.cinema || p.mission || B.interieur) return;
    const prochaine = disponibles().find(function (m) { return m.prerequis.length && m.dialogue.appel.length && !p.appels[m.slug]; });
    if (!prochaine) return;
    if (p.appelT === undefined || p.appelT === null) { p.appelT = B.t + DELAI_APPEL; return; }
    if (B.t < p.appelT) return;
    p.appels[prochaine.slug] = true; p.appelT = null;
    Son.SFX.telephone();
    dire(prochaine, 'appel', function () { Hud.message('VA VOIR ' + personnage(prochaine.donneur).nom.toUpperCase(), 180); });
  }

  // --- Parler a quelqu'un -----------------------------------------------------------------

  /** ACTION pres d'un personnage (ou sur son point, dedans). Rend true si ca a fait quelque chose. */
  function parler(slug) {
    const p = personnage(slug);
    if (!p || B.cinema) return false;
    rencontrer(slug);
    const enCours = courante();
    if (enCours && enCours.donneur === slug) {
      const o = objectif();
      if (o && o.type === 'retourner') { reussir(); return true; }
      Hud.message(objectif() ? objectif().texte : '', 150);
      return true;
    }
    const m = disponibleDe(slug);
    if (m) { dire(m, 'intro', function () { commencer(m.slug); }); return true; }
    const mn = B.defs.marche_noir;
    if (mn && slug === 'josee' && faite(mn.apres)) { Hud.ouvrirMenu(Missions.menuMarcheNoir()); return true; }
    Hud.dialogue(p.nom, [faite('m5') ? 'LE FAUBOURG EST TRANQUILLE. MERCI.' : 'REVIENS ME VOIR PLUS TARD.'], 120);
    return true;
  }

  // --- Les missions ------------------------------------------------------------------------

  function objectif() {
    const m = courante();
    return m ? m.objectifs[B.partie.mission.etape] || null : null;
  }

  function commencer(slug) {
    const m = mission(slug);
    if (!m || B.partie.mission) return false;
    B.partie.mission = { slug: slug, etape: -1, t: B.t, chocs: 0 };
    B.mission = { entites: [], vehicule: null, fuyard: null, chef: null, escorte: null, courses: 0, kos: 0 };
    Hud.message(m.titre.toUpperCase(), 180);
    Son.SFX.mission();
    avancer();
    return true;
  }

  /** L'objectif suivant. Ce qu'il faut poser en ville se pose DEHORS : si
      l'objectif arrive pendant qu'on est dedans (Josee au bar), a la sortie. */
  function avancer() {
    const m = courante(), p = B.partie.mission;
    p.etape++;
    const o = m.objectifs[p.etape];
    if (!o) { reussir(); return; }
    p.debutT = B.t;
    B.mission.aPoser = true;
    if (!B.interieur) poser();
    Hud.message(o.texte, 200);
  }

  function poser() {
    const m = courante(), p = B.partie.mission, j = B.joueur;
    const o = m.objectifs[p.etape];
    B.mission.aPoser = false;
    if (!o) return;
    if (o.type === 'monter') {
      const ou = resoudre(o.ou, m);
      const rue = ou ? (o.ou.indexOf('ruelle:') === 0 ? ou : tuileDeRue(ou.x, ou.y, 8)) : null;
      const place = rue || ou;
      if (place) {
        // ⚠️ `aQui` vient de la fiche (`prete` dans `missions.py`), et il ne
        // s'efface JAMAIS : le taxi de Marco est a Marco avant, pendant et
        // apres — c'est lui qui l'empeche d'etre vendu au garage de Ti-Guy,
        // qui est a deux pas de la ou il dort.
        const v = Vehicules.creer(o.vehicule, place.x, place.y, rue && rue.sens ? { '>': 0, '<': Math.PI, '^': -Math.PI / 2, 'v': Math.PI / 2 }[rue.sens] : 0, { etat: 'stationne', mission: m.slug, aQui: o.prete || null });
        if (v) { B.mission.vehicule = v; B.mission.entites.push(v); }
      }
    } else if (o.type === 'tuer') {
      poserLesCravates(m, o);
    } else if (o.type === 'ramasser' && o.cible === 'fuyard') {
      poserLeFuyard(m, o);
    } else if (o.type === 'semer') {
      B.recherche.etoiles = Math.max(B.recherche.etoiles, o.etoiles || 1); B.recherche.vu = 0; B.recherche.flash = 60;
      B.recherche.dernierVu = { x: j.x, y: j.y, t: B.t };
      if (o.escorte) poserLEscorte(m, o);
    } else if (o.type === 'courses') {
      B.mission.courses = 0; B.mission.coursesDepart = Missions.boulot.faits.taxi;
    }
  }

  function poserLesCravates(m, o) {
    const gang = B.defs.pietons.gangs.find(function (g) { return g.slug === o.groupe; });
    if (!gang) return;
    const arch = Entites.archetype(gang.pieton);
    const centre = o.chef ? { x: B.joueur.x, y: B.joueur.y } : resoudre(o.ou, m) || { x: B.joueur.x, y: B.joueur.y };
    const coins = o.coins || 1;
    B.mission.kos = 0;
    for (let c = 0; c < coins; c++) {
      const a = c / coins * Math.PI * 2;
      const cx = coins > 1 ? centre.x + Math.cos(a) * 120 : centre.x, cy = coins > 1 ? centre.y + Math.sin(a) * 120 : centre.y;
      for (let i = 0; i < Math.ceil(o.n / coins); i++) {
        const place = tuileLibre(cx + (i - 1) * 20 + 40, cy + 10, 6);
        if (!place) continue;
        const e = Entites.creerPieton(place.x, place.y, arch);
        e.cible = true; e.mission = m.slug; e.courage = 1; e.etat = 'flane';
        // ⚠️ CE QUE PORTE UN HOMME DE MISSION VIENT DE LA FICHE, pas de
        // l'archetype. `arme` et `vie` sont facultatives (`missions.py`) et ne
        // valent que pour CES hommes-la : la Cravate de rue reste ce qu'elle
        // est — elle tient le Faubourg en M5 et vient encaisser la dette de
        // Rocco. ⚠️ `''` veut dire les poings, et il faut donc tester
        // `!== undefined` : un `||` rendrait le baton a qui vient les mains
        // vides, ce qui est exactement le bogue qu'on repare.
        if (o.arme !== undefined) e.arme = o.arme || null;
        if (o.vie) { e.vie = e.vieMax = o.vie; }
        if (o.chef) { e.chef = true; e.vie = e.vieMax = 160; e.arme = 'batte'; e.swaps = Object.assign({}, e.swaps, { c: '#101018' }); }
        B.mission.entites.push(e);
        if (B.mission.entites.filter(function (q) { return q.cible && q.mission === m.slug && q.vivant && q.etat !== 'assomme'; }).length >= o.n) break;
      }
    }
    Entites.indexer();
    Entites.alerter(centre.x, centre.y, B.joueur, 1);     // ils t'ont vu venir
  }

  function poserLeFuyard(m, o) {
    const j = B.joueur;
    const rue = tuileDeRue(j.x, j.y, 10);
    if (!rue) return;
    const angle = { '>': 0, '<': Math.PI, '^': -Math.PI / 2, 'v': Math.PI / 2 }[rue.sens];
    const v = Vehicules.creer(o.vehicule || 'moto', rue.x, rue.y, angle, { conducteur: 'trafic', etat: 'roule', poursuite: true, fuite: true, sens: rue.sens, mission: m.slug, fuyard: true });
    if (!v) return;
    v.vitesse = 1.5;
    B.mission.vehicule = v; B.mission.fuyard = v; B.mission.entites.push(v);
    Hud.message('LE FUYARD FILE EN MOTO !', 150);
  }

  function poserLEscorte(m, o) {
    const j = B.joueur;
    const rue = tuileDeRue(j.x, j.y, 10);
    if (!rue) return;
    const angle = { '>': 0, '<': Math.PI, '^': -Math.PI / 2, 'v': Math.PI / 2 }[rue.sens];
    const v = Vehicules.creer('auto', rue.x, rue.y, angle, { conducteur: 'trafic', etat: 'roule', poursuite: true, escorte: true, sens: rue.sens, mission: m.slug, couleur: '#2e8b57', swaps: { c: '#2e8b57' } });
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
        const l = lieu(o.lieu);
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
        const cibles = B.mission.entites.filter(function (e) { return e.type === 'pieton' && e.cible && !e.porteLaCaisse; });
        const tombes = cibles.filter(function (e) { return !e.vivant || e.etat === 'assomme'; }).length;
        B.mission.kos = tombes;
        if (cibles.length && tombes >= Math.min(o.n, cibles.length)) {
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
      default:
        avancer();
    }
  }

  function reussir() {
    const m = courante();
    if (!m) return;
    const p = B.partie, d = m.donne || {};
    nettoyer(false);
    p.missionsFaites[m.slug] = p.jour;
    p.mission = null;
    p.appelT = null;
    let prime = m.recompense;
    if (B.mission && B.mission.sansBosse) prime += Math.round(m.recompense * 0.5);
    Missions.encaisser(prime, m.titre.toUpperCase());
    if (d.arme && !p.armes[d.arme]) { const a = Combat.armeDef(d.arme); p.armes[d.arme] = { mun: a && a.chargeur ? a.chargeur : null }; }
    if (d.rabais) Object.keys(d.rabais).forEach(function (k) { p.rabais[k] = d.rabais[k]; });
    if (d.sergent_ami) p.sergentAmi = true;
    if (d.propriete && !p.proprietes[d.propriete]) p.proprietes[d.propriete] = { jour: p.jour, caisse: 0 };
    if (d.faubourg_libere) p.faubourgLibere = true;
    if (d.manchette) p.manchetteForcee = d.manchette;
    p.stats.missions = (p.stats.missions || 0) + 1;
    noter('MISSION : ' + m.titre + ' — ' + prime + ' $', true);
    B.mission = null;
    Son.SFX.mission();
    dire(m, 'fin', function () {
      if (d.message) Hud.message(d.message, 200);
      if (m.slug === 'm1') { const t = donneur('ti_guy'); if (t) { t.etat = 'entre'; t.minuterie = 60; } }
      Missions.sauvegarderPartie();
    });
  }

  function echouer(raison) {
    const m = courante();
    if (!m) return;
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

  /** Ce que la mission avait pose : on l'enleve (ou on le laisse vivre sa vie). */
  function nettoyer(tout) {
    if (!B.mission) return;
    for (const e of B.mission.entites) {
      if (e.type === 'vehicule') {
        if (tout || e.fuyard || e.escorte) { if (B.joueur.dansVehicule === e) Vehicules.descendre(B.joueur, true); Entites.retirer(e); }
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
  function creerPanneaux() {
    for (const d of defis()) {
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
      if (!l) continue;
      const place = tuileLibre(l.x - TT * 3, l.y, 3) || tuileLibre(l.x + TT * 3, l.y, 3);
      if (!place) continue;
      Entites.creer('panneau', place.x, place.y, { decor: 'panneau', r: 3, solide: false, dessine: true, vivant: false, defi: d.slug });
    }
  }

  function panneauSousLaMain(j) {
    return Entites.autour(j.x, j.y, 24, function (e) { return e.type === 'panneau'; })[0] || null;
  }

  function proposerDefi(slug) {
    const d = defis().find(function (q) { return q.slug === slug; });
    if (!d || B.defi) return false;
    const fait = !!B.partie.defisFaits[slug];
    Hud.ouvrirMenu({ titre: d.titre.toUpperCase(), sur: fait ? 'DÉJÀ RÉUSSI' : d.prime + ' $', aide: d.texte, items: [
      { libelle: 'COMMENCER', faire: function () { commencerDefi(d); return true; } },
      { libelle: 'PAS MAINTENANT', faire: function () { return true; } },
    ] });
    return true;
  }

  function commencerDefi(d) {
    const j = B.joueur;
    B.defi = { slug: d.slug, t: 0, etape: 0, tours: 0, vol: 0, chocs: j.dansVehicule ? j.dansVehicule.chocs : 0, vie: j.dansVehicule ? j.dansVehicule.vie : 0 };
    if (d.etoiles) { B.recherche.etoiles = Math.max(B.recherche.etoiles, d.etoiles); B.recherche.vu = 0; }
    Hud.message(d.titre.toUpperCase() + ' — GO !', 120);
    Son.SFX.mission();
  }

  function majDefi() {
    const f = B.defi, j = B.joueur;
    if (!f) return;
    const d = defis().find(function (q) { return q.slug === f.slug; });
    f.t++;
    if (d.chrono_s && f.t > d.chrono_s * 60) { finirDefi(false, 'TEMPS ÉCOULÉ'); return; }
    const v = j.dansVehicule;
    if (d.vehicule === 'moto') {
      if (!v || v.slug !== 'moto') { if (f.t > 600) finirDefi(false, 'IL FAUT UNE MOTO'); return; }
      if (v.z > 0) { f.vol += Math.hypot(v.vx, v.vy); if (f.vol >= d.vol_px) finirDefi(true); }
      else f.vol = 0;
      return;
    }
    if (d.points) {
      if (!v) { finirDefi(false, 'SANS CHAR, PAS DE TOUR'); return; }
      const cible = lieu(d.points[f.etape]);
      if (cible && dist2(v.x, v.y, cible.x, cible.y) < (5 * TT) * (5 * TT)) {
        f.etape++;
        if (f.etape >= d.points.length) { f.etape = 0; f.tours++; Hud.message('TOUR ' + f.tours + ' / ' + d.tours, 90); }
        if (f.tours >= d.tours) finirDefi(true);
      }
      return;
    }
    if (d.lieu) {
      if (!v) { finirDefi(false, 'SANS CHAR, PAS DE LIVRAISON'); return; }
      if (v.chocs !== f.chocs || v.vie < f.vie) { finirDefi(false, 'UNE BOSSE !'); return; }
      const cible = lieu(d.lieu);
      if (cible && dist2(v.x, v.y, cible.x, cible.y) < (4 * TT) * (4 * TT) && Math.abs(v.vitesse) < 0.4) finirDefi(true);
    }
  }

  function finirDefi(reussi, raison) {
    const f = B.defi, d = defis().find(function (q) { return q.slug === f.slug; });
    B.defi = null;
    if (!reussi) { Hud.message('DÉFI RATÉ — ' + (raison || ''), 180); Son.SFX.erreur(); noter('DÉFI RATÉ : ' + d.titre, false); return; }
    const premiere = !B.partie.defisFaits[d.slug];
    B.partie.defisFaits[d.slug] = { jour: B.partie.jour, temps: f.t };
    if (premiere) Missions.encaisser(d.prime, d.titre.toUpperCase());
    else Hud.message(d.titre.toUpperCase() + ' — RÉUSSI', 180);
    noter('DÉFI RÉUSSI : ' + d.titre + (premiere ? ' — ' + d.prime + ' $' : ''), true);
    Son.SFX.mission();
  }

  // --- Le GPS : ou aller, pour le HUD ------------------------------------------------------------

  /** La cible du moment : un objectif, un appel a honorer, un defi en cours. */
  function cible() {
    const m = courante(), p = B.partie, j = B.joueur;
    if (!j) return null;
    if (B.defi) {
      const d = defis().find(function (q) { return q.slug === B.defi.slug; });
      const l = d.points ? lieu(d.points[B.defi.etape]) : d.lieu ? lieu(d.lieu) : null;
      return l ? { x: l.x, y: l.y, nom: l.nom, couleur: '#7fc4ff' } : null;
    }
    if (m) {
      const o = m.objectifs[p.mission.etape];
      if (!o) return null;
      let l = null;
      if (o.type === 'aller' || o.type === 'livrer') l = lieu(o.lieu);
      else if (o.type === 'monter') l = B.mission && B.mission.vehicule ? B.mission.vehicule : null;
      else if (o.type === 'retourner') l = ouTrouver(m.donneur);
      else if (o.type === 'ramasser') l = B.mission && (B.mission.entites.find(function (e) { return e.objet === 'caisse'; }) || B.mission.entites.find(function (e) { return e.porteLaCaisse && e.vivant && e.etat !== 'assomme'; }) || (!B.mission.fuyardTombe ? B.mission.fuyard : null));
      else if (o.type === 'tuer') { const restants = B.mission ? B.mission.entites.filter(function (e) { return e.cible && e.vivant && e.etat !== 'assomme'; }) : []; l = restants[0] || null; }
      return l ? { x: l.x, y: l.y, nom: (l.nom || o.texte), couleur: '#e8b33c' } : null;
    }
    // Un appel recu : le donneur a aller voir.
    const attendue = disponibles().find(function (q) { return p.appels[q.slug]; }) || disponibles().find(function (q) { return !q.prerequis.length; });
    if (attendue) { const l = ouTrouver(attendue.donneur); const perso = personnage(attendue.donneur); return l ? { x: l.x, y: l.y, nom: perso.nom, couleur: '#8ad26a' } : null; }
    return null;
  }

  /** La ligne d'objectif que le HUD ecrit en haut : mission, objectif, compte. */
  function ligneObjectif() {
    const m = courante();
    if (B.defi) {
      const d = defis().find(function (q) { return q.slug === B.defi.slug; });
      const reste = d.chrono_s ? Math.max(0, d.chrono_s * 60 - B.defi.t) : null;
      const chrono = reste === null ? '' : ' ' + Math.floor(reste / 3600) + ':' + ('0' + Math.floor(reste % 3600 / 60)).slice(-2);
      const compte = d.points ? ' TOUR ' + (B.defi.tours + 1) + '/' + d.tours : d.vol_px ? ' VOL ' + Math.round(B.defi.vol) + '/' + d.vol_px : '';
      return d.titre.toUpperCase() + chrono + compte;
    }
    if (!m) return null;
    const o = m.objectifs[B.partie.mission.etape];
    if (!o) return null;
    if (B.mission && B.mission.attend) return B.mission.attend;
    let compte = '';
    if (o.type === 'tuer') compte = ' ' + (B.mission ? B.mission.kos : 0) + '/' + o.n;
    if (o.type === 'courses') compte = ' ' + (B.mission ? B.mission.courses : 0) + '/' + o.n;
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
    majBulles();
    majTelephone();
    if (B.partie.mission) {
      if (!B.mission) B.mission = { entites: [], vehicule: null, fuyard: null, chef: null, escorte: null, courses: 0, kos: 0 };  // partie rechargee : on reprend au meme objectif, sans ses figurants
      if (!B.interieur) {
        if (B.mission.aPoser) poser();
        majObjectif();
      }
    }
    majDefi();
  }

  return { disponibles, disponibleDe, personnage, personnageSousLaMain, personnageDuPoint, pieceDuPoint,
           donneur, creerDonneurs, creerDonneursDedans, creerPanneaux, panneauSousLaMain,
           parler, dire, suivante, finir, commencer, avancer, objectif, courante, reussir, echouer, evenement,
           ouverture, majOuverture, passerOuverture, finirOuverture, fichiersDeLOuverture, OUV,
           noter, rencontrer, CARNET_MAX,
           proposerDefi, commencerDefi, finirDefi, cible, ligneObjectif, lieu, ruellePres, tuileLibre, tuileDeRue, slugDeVoix, maj };
})();
