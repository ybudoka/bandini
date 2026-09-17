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

  /** Ou l'on LIVRE un char : devant la porte de garage du lieu s'il en a une —
      c'est la qu'on stationne (demande de Martin, 17 sept. 2026) —, sinon a sa
      porte. ⚠️ Le rayon de l'objectif ne change pas : la baie est a trois tuiles
      de la porte des pietons, et un char livre « au garage » l'est toujours. */
  function lieuDeLivraison(slug) {
    const pg = Monde.porteDeGarage(slug);
    if (!pg) return lieu(slug);
    const baie = Monde.baieDeLaPorteDeGarage(pg), l = lieu(slug);
    return { x: baie.x, y: baie.y, nom: l ? l.nom : slug };
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

  /** `ou` d'un objectif ou d'un personnage → un pixel. */
  function resoudre(ou, m) {
    if (!ou) return null;
    if (ou === 'donneur') return ouTrouver(m.donneur);
    const deux = ou.split(':');
    if (deux[0] === 'porte') return lieu(deux[1]);
    if (deux[0] === 'ruelle') return ruellePres(deux[1], Number(deux[2]) || 0);   // `ruelle:garage:24`
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

  /** Pose les personnages qui se tiennent DEHORS, a cote de leur porte — sauf
      ceux qui sont partis apres leur mission (`parti_apres`). */
  function creerDonneurs() {
    for (const p of personnages()) {
      if (p.ou.indexOf('porte:') !== 0) continue;                 // les autres sont dedans
      // Parti apres sa mission (Ti-Guy entre au garage a la fin de M1) : dans les
      // donnees, parce qu'ici aucun slug de mission ne s'ecrit.
      if (p.parti_apres && faite(p.parti_apres)) continue;
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
               slug: slugDeVoix(m, partie, i) };
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
      appel, intro, client, fin, echec, pendant — exactement comme `missions.repliques()`. */
  function slugDeVoix(m, partie, i) {
    // ⚠️ `pendant` APRES `echec`, comme `missions.PARTIES` : inseree plus tot,
    // elle renommerait des voix deja generees.
    const ordre = ['appel', 'intro', 'client', 'fin', 'echec', 'pendant'];
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
    Hud.dialogue(c.anonyme ? '' : (p ? p.nom : l.qui) + (l.telephone ? ' (AU TÉLÉPHONE)' : ''), decouper(l.texte), 0);
    c.voix = Son.Voix.parler(l.slug, { telephone: l.telephone, fin: function () { if (B.cinema === c && c.i === c.lignes.indexOf(l)) c.duree = Math.min(c.duree, c.t + 20); } });
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
    const parle = !!(l && Son.Voix.enCours && Son.Voix.enCours.slug === l.slug) && c.t < c.duree + 900;
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
    if (enCours && enCours.donneur === slug) {
      const o = objectif();
      if (o && o.type === 'retourner') { reussir(); return true; }
      Hud.message(objectif() ? objectif().texte : '', 150);
      return true;
    }
    const m = disponibleDe(slug);
    if (m) {
      // ⚠️ LA MISSION SE POSE AVANT SA SCENE D'INTRO. Quand Madame Thibodeau
      // parle de ses deux Cravates, ils doivent exister : une scene qui va les
      // voir filmerait sinon un coin vide. Ce n'est pas un de de deplace — la
      // ville est figee pendant qu'on parle et le dialogue n'en tire aucun, donc
      // les tirages de `poser()` tombent dans le meme ordre. Ce qui s'ANNONCE
      // (le titre, l'objectif, le coup de cuivre) attend, lui, la fin de l'intro.
      commencer(m.slug, true);
      jouerOuDire(m, 'intro', function () { annoncer(m); });
      return true;
    }
    const mn = B.defs.marche_noir;
    if (mn && slug === 'josee' && faite(mn.apres)) { Hud.ouvrirMenu(Missions.menuMarcheNoir()); return true; }
    const repos = B.defs.repos || {};
    Hud.dialogue(p.nom, [repos.apres && faite(repos.apres) ? repos.texte_apres : (repos.texte || 'REVIENS ME VOIR PLUS TARD.')], 120);
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
    B.mission = { entites: [], vehicule: null, chars: {}, fuyard: null, chef: null, escorte: null, courses: 0, kos: 0 };
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
  }

  /** L'objectif suivant. Ce qu'il faut poser en ville se pose DEHORS : si
      l'objectif arrive pendant qu'on est dedans (Josee au bar), a la sortie. */
  function avancer(enSilence) {
    const m = courante(), p = B.partie.mission;
    p.etape++;
    const o = m.objectifs[p.etape];
    if (!o) { reussir(); return; }
    // ⚠️ Tout le monde est deja tombe a un essai rate : l'objectif est FAIT.
    // On ne repose pas des morts pour les recoucher.
    if (o.type === 'tuer' && dejaTombes(m.slug, p.etape) >= o.n) { avancer(enSilence); return; }
    p.debutT = B.t;
    B.mission.aPoser = true;
    if (!B.interieur) poser();
    if (!enSilence) Hud.message(o.texte, 200);
    // La replique PENDANT de cet objectif, des qu'aucune autre ne parle (`maj`).
    if (!enSilence && (m.dialogue.pendant || []).some(function (l) { return l.objectif === p.etape; })) B.mission.pendant = p.etape;
  }

  function poser() {
    const m = courante(), p = B.partie.mission, j = B.joueur;
    const o = m.objectifs[p.etape];
    B.mission.aPoser = false;
    if (!o) return;
    if (o.type === 'monter') {
      const v = poserLeChar(m, o, p.etape);
      if (v) B.mission.vehicule = v;
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
  }

  /** Le char d'un objectif `monter`, la ou il dort. Rend celui qui y est deja
      — pose d'avance — sauf s'il a saute ou quitte la ville entre-temps. */
  function poserLeChar(m, o, etape) {
    const chars = B.mission.chars || (B.mission.chars = {});
    const deja = chars[etape];
    if (deja && deja.etat !== 'epave' && B.entites.indexOf(deja) >= 0) return deja;
    const ou = resoudre(o.ou, m);
    const rue = ou ? (o.ou.indexOf('ruelle:') === 0 ? ou : (tuileDeRue(ou.x, ou.y, 8, sansChar) || tuileDeRue(ou.x, ou.y, 8))) : null;
    const place = rue || ou;
    if (!place) return null;
    // ⚠️ `aQui` vient de la fiche (`prete` dans `missions.py`), et il ne
    // s'efface JAMAIS : le taxi de Marco est a Marco avant, pendant et
    // apres — c'est lui qui l'empeche d'etre vendu au garage de Ti-Guy,
    // qui est a deux pas de la ou il dort.
    const v = Vehicules.creer(o.vehicule, place.x, place.y, rue && rue.sens ? CAP_DE_FLECHE[rue.sens] : 0, { etat: 'stationne', mission: m.slug, aQui: o.prete || null });
    if (!v) return null;
    chars[etape] = v;
    B.mission.entites.push(v);
    return v;
  }

  function poserLesCravates(m, o) {
    const gang = B.defs.pietons.gangs.find(function (g) { return g.slug === o.groupe; });
    if (!gang) return;
    const arch = Entites.archetype(gang.pieton);
    const centre = o.chef ? { x: B.joueur.x, y: B.joueur.y } : resoudre(o.ou, m) || { x: B.joueur.x, y: B.joueur.y };
    const coins = o.coins || 1;
    const etape = B.partie.mission.etape, parCoin = tombesDe(m.slug, etape);
    const reste = o.n - dejaTombes(m.slug, etape);
    B.mission.kos = o.n - reste;
    if (reste <= 0) return;
    for (let c = 0; c < coins; c++) {
      const a = c / coins * Math.PI * 2;
      const cx = coins > 1 ? centre.x + Math.cos(a) * 120 : centre.x, cy = coins > 1 ? centre.y + Math.sin(a) * 120 : centre.y;
      // ⚠️ Un coin qu'on a vide reste vide : on n'y repose que ce qui
      // manquait encore a son compte.
      for (let i = parCoin[c] || 0; i < Math.ceil(o.n / coins); i++) {
        const place = tuileLibre(cx + (i - 1) * 20 + 40, cy + 10, 6);
        if (!place) continue;
        const e = Entites.creerPieton(place.x, place.y, arch);
        e.cible = true; e.mission = m.slug; e.courage = 1; e.etat = 'flane';
        e.etape = etape; e.coin = c;
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
        if (B.mission.entites.filter(function (q) { return q.cible && q.etape === etape && q.vivant && q.etat !== 'assomme'; }).length >= reste) break;
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
  //: Un panneau se tient a cette distance au moins d'un donneur : au-dela de la
  //: portee de parole (`RAYON_PARLER`) de celui qui le lit, planté devant.
  const PANNEAU_LOIN_DU_DONNEUR = 3 * TT;

  /** Ce pixel, s'il n'est ni devant un rideau de garage (sa baie, une tuile de
      marge) ni a portee d'un donneur ; sinon null. */
  function placeDePanneau(p) {
    if (!p) return null;
    if (Monde.portesDeGarage().some(function (pg) { return Monde.devantLaPorteDeGarage(pg, p.x, p.y, 2, 1); })) return null;
    return Entites.pietonsAutour(p.x, p.y, PANNEAU_LOIN_DU_DONNEUR).some(function (e) { return e.personnage; }) ? null : p;
  }

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
      // ⚠️ JAMAIS DEVANT UN RIDEAU DE GARAGE : trois tuiles a l'ouest de la
      // porte de Ti-Guy, c'est exactement la baie ou l'on gare pour vendre, et
      // le panneau de la livraison s'y plantait devant la porte qui se leve.
      // ⚠️ NI SOUS LE NEZ D'UN DONNEUR : a l'est, c'est Marco qui attend, et
      // ACTION lui parlait au lieu de lire le panneau (`interagir` sert les
      // personnages d'abord). On s'eloigne par pas ; ailleurs, rien ne change.
      let place = null;
      for (const loin of [3, 5, 7]) {
        place = placeDePanneau(tuileLibre(l.x - TT * loin, l.y, 3)) || placeDePanneau(tuileLibre(l.x + TT * loin, l.y, 3));
        if (place) break;
      }
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

  //: Le temps qu'on a, le panneau lu, pour monter dans le char du defi.
  //: ⚠️ LE PANNEAU SE LIT A PIED (au volant, ACTION fait descendre) : le tour et
  //: la livraison, qui ratent sans char, ratent donc a l'image suivante — ni
  //: l'un ni l'autre ne s'etait jamais gagne. Le Grand Saut avait deja ses dix
  //: secondes pour trouver sa moto ; les deux autres les ont aussi, et leur
  //: chrono ne part qu'au volant.
  const ATTENTE_CHAR = 600;

  function commencerDefi(d) {
    const j = B.joueur;
    B.defi = { slug: d.slug, t: 0, attente: 0, parti: false, etape: 0, tours: 0, vol: 0, chocs: 0, vie: 0 };
    Son.SFX.mission();
    // Le Grand Saut compte ses dix secondes lui-meme (`majDefi`) : il part tout de suite.
    if (d.vehicule || j.dansVehicule) { partir(d, j.dansVehicule); return; }
    Hud.message(d.titre.toUpperCase() + ' — MONTE DANS UN CHAR', 150);
  }

  /** Le chrono part. ⚠️ La police aux fesses et la reference « sans bosse » se
      prennent ICI, au volant, et pas au panneau : sinon on se ferait arreter en
      marchant jusqu'a son char, et on comparerait ses bosses a celles d'aucun. */
  function partir(d, v) {
    const f = B.defi;
    f.parti = true; f.t = 0;
    f.chocs = v ? v.chocs : 0; f.vie = v ? v.vie : 0;
    if (d.etoiles) { B.recherche.etoiles = Math.max(B.recherche.etoiles, d.etoiles); B.recherche.vu = 0; }
    Hud.message(d.titre.toUpperCase() + ' — GO !', 120);
  }

  function majDefi() {
    const f = B.defi, j = B.joueur;
    if (!f) return;
    const d = defis().find(function (q) { return q.slug === f.slug; });
    if (!f.parti) {
      if (!j.dansVehicule) { if (++f.attente > ATTENTE_CHAR) finirDefi(false, 'IL FAUT UN CHAR'); return; }
      partir(d, j.dansVehicule);
    }
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
      if (o.type === 'aller') l = lieu(o.lieu);
      else if (o.type === 'livrer') l = lieuDeLivraison(o.lieu);
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
      if (!B.defi.parti) return d.titre.toUpperCase() + chrono + ' — MONTE DANS UN CHAR';
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
    jouerLaFin();
    if (B.cinema) return;
    majBulles();
    majTelephone();
    if (B.partie.mission) {
      if (!B.mission) B.mission = { entites: [], vehicule: null, chars: {}, fuyard: null, chef: null, escorte: null, courses: 0, kos: 0 };  // partie rechargee : on reprend au meme objectif, sans ses figurants
      if (B.mission.pendant !== undefined && B.mission.pendant !== null) {
        const etape = B.mission.pendant;
        B.mission.pendant = null;
        dire(courante(), 'pendant', null, function (l) { return l.objectif === etape; });
        return;
      }
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
           ouverture, passerOuverture, fichiersDeLOuverture, direLignes, majCinema, resoudre,
           lieuDuPersonnage, present, calme, jouerOuDire,
           noter, rencontrer, CARNET_MAX,
           proposerDefi, commencerDefi, finirDefi, cible, ligneObjectif, lieu, lieuDeLivraison, ruellePres, tuileLibre, tuileDeRue, slugDeVoix, maj };
})();
