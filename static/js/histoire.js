/* Bandini — l'histoire : les donneurs, les missions, les defis, les voix.

   Tout le texte vient de `missions.py` (le paquet `B.defs.missions`) : ici on
   ne fait que le JOUER. Une mission = une suite d'objectifs types ; a chaque
   image, `maj()` regarde si l'objectif courant est atteint, et passe au
   suivant. Les repliques s'affichent dans la boite de dialogue ET se disent
   a voix haute (`Son.Voix.parler`), une par personnage ; pendant qu'un
   personnage parle, le joueur ecoute (il ne bouge pas), la radio baisse.

   Le telephone : quand une mission devient possible, son donneur appelle
   quelques secondes plus tard — la voix vient du combine.

   ⚠️ **CE QU'UNE MISSION DEMANDE POUR SE JOUER N'EST PLUS DANS LE PAQUET** (24 sept.
   2026) : il etait au-dessus de ses deux plafonds. `B.defs.missions` porte le CATALOGUE —
   son titre, son donneur, ses prerequis, sa recompense : c'est lui que le carnet, le GPS
   et le telephone lisent, et il faut l'avoir en entier pour savoir quelle mission est
   possible. Ses repliques, ses scenes, ses voix et ses OBJECTIFS arrivent par
   `/api/mission/<slug>` : voir `charger`. */

const Histoire = (function () {
  'use strict';

  // ⚠️ UN APPEL A LA FOIS. Martin (25 sept. 2026) : « j'ai trop de missions au telephone
  // une apres l'autre ». Le combine sonnait 10 s apres chaque appel tant qu'une mission
  // restait a annoncer — avec une dizaine de donneurs, quatre ou cinq d'affilee. Il attend
  // maintenant qu'on aille voir celui qui a appele ; s'il est ignore, il relance plus tard.
  const DELAI_APPEL = 2700;         // images (45 s) entre la fin d'une mission et l'appel de la suivante
  const DELAI_RELANCE = 10800;      // images (3 min) quand une mission annoncee attend encore d'etre prise
  const RAYON_PARLER = 22;          // a cette distance d'un personnage, ACTION = lui parler

  function defs() { return B.defs.missions || []; }

  // --- Ce qu'une mission dit : hors du paquet -----------------------------------
  /*: ⚠️ **UN TEXTE NE PEUT PAS ARRIVER EN RETARD**, contrairement a une voix : une
    replique sans son mp3 s'affiche quand meme (`Son.Voix.attendue` la dit des qu'il
    arrive), un dialogue absent n'a RIEN a afficher. On le demande donc bien AVANT sa
    porte — des que la bulle d'un donneur s'allume (il est visible a plusieurs secondes
    de marche) et des que le telephone choisit sa prochaine mission (il attend
    `DELAI_APPEL` avant de sonner) — et les portes verifient quand meme : un reseau lent
    ne doit pas ouvrir une boite vide. */
  let fenetre = null;
  let gabarit = '/api/mission/SLUG';
  //: slug -> ce qu'on rappellera quand son texte arrivera. La clef seule dit « en
  //: route » : on ne demande jamais deux fois la meme.
  const enRoute = {};
  //: La mission dont on attend le texte pour ouvrir sa porte. ⚠️ Deux coups d'ACTION
  //: pendant qu'il vole ne doivent pas poser la mission deux fois.
  let porteEnAttente = null;

  function init(w, racine) {
    fenetre = w;
    const dit = racine && racine.dataset && racine.dataset.urlMission;
    if (dit) gabarit = dit;
  }

  /** Demande tout ce qu'une mission demande pour se jouer — une seule fois. `suite`
      s'appelle quand c'est la ; tout de suite si ca y est deja. Rend `true` quand elle est
      deja sous la main. */
  function charger(slug, suite) {
    const m = mission(slug);
    if (!m) return false;
    if (m.dialogue) { if (suite) suite(); return true; }
    if (enRoute[slug]) { if (suite) enRoute[slug].push(suite); return false; }
    enRoute[slug] = suite ? [suite] : [];
    if (!fenetre || !fenetre.fetch) return false;
    fenetre.fetch(gabarit.replace('SLUG', slug))
      .then(function (r) { if (!r.ok) throw new Error('mission ' + slug + ' : ' + r.status); return r.json(); })
      .then(function (d) {
        m.dialogue = d.dialogue || {};
        m.scenes = d.scenes || {};
        // ⚠️ Les OBJECTIFS aussi (ils pesaient les deux tiers du catalogue) : ils ne
        // servent qu'a partir de `commencer()`, donc apres l'intro, donc apres tout ceci.
        m.objectifs = d.objectifs || [];
        // Le saut et la frontiere (`SurPlace`), sortis du paquet comme les objectifs (30 sept. 2026).
        m.sur_place = d.sur_place || null;
        m.frontiere = d.frontiere || null;
        // Ce qu'elle donne (`donne`), sorti du catalogue (30 sept. 2026) : lu par `recompenser` et `jouerLaFin`.
        if (d.donne) m.donne = d.donne;
        // Ce que paie chaque réponse d'un choix (`branches`, 1er oct. 2026) : lu en la réussissant, comme `donne`.
        if (d.branches) m.branches = d.branches;
        // Le passant d'une petite job, entier (le nom de sa boîte) : le catalogue n'en porte que « archétype@district ».
        if (d.passant) m.passant = d.passant;
        // ⚠️ SES VOIX SE DECLARENT ICI AUSSI. `Son.Voix.histoire()` lit la liste du
        // paquet, et celles d'une mission n'y sont plus : sans cette ligne, le texte
        // s'afficherait et personne ne parlerait. `chargerHistoire` va chercher les
        // mp3 ensuite, comme avant.
        const connues = Son.Voix.histoire();   // (les series du paquet, depliees)
        (d.voix || []).forEach(function (v) {
          if (!connues.some(function (x) { return x.slug === v.slug; })) connues.push(v);
        });
        const suites = enRoute[slug] || [];
        delete enRoute[slug];
        suites.forEach(function (f) { f(); });
      })
      .catch(function () {
        // ⚠️ ON OUBLIE LA DEMANDE : la porte redemandera. Un reseau qui tombe une fois
        // ne doit pas fermer une mission pour le reste de la partie.
        delete enRoute[slug];
        if (porteEnAttente === slug) porteEnAttente = null;
      });
    return false;
  }
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
  // ⚠️ Un CHAPITRE dont toutes les missions remplacées sont faites l'est aussi (une vieille partie).
  function faite(slug) { return !!B.partie.missionsFaites[slug] || Chapitres.fait(mission(slug)); }
  /** CE QU'ON A PRÉPARÉ CHANGE LA SUITE (le casse, x04 — 1er oct. 2026) : `si` (cette mission est faite) et `sauf` (elle ne
      l'est pas), sur un objectif — tenu, il se joue ; sinon il se SAUTE — ou sur une réplique `pendant` — tenue, elle
      se dit. Le coupé du x02 qui attend dans la ruelle, Josée qui dit ce qui manque. ⚠️ En données, jamais un slug ici. */
  /** L'heure de jeu, comptée depuis le premier jour : le jour et la fraction de jour de la partie. */
  function heuresDeJeu() { return ((B.partie.jour || 0) + (B.partie.heure || 0)) * 24; }
  function tenu(o) { return !o || ((!o.si || faite(o.si)) && (!o.sauf || !faite(o.sauf))); }
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
    // ⚠️ `une_de` (29 sept. 2026, q13) : un prerequis ne sait dire que « et ». Apres un CHOIX
    // (q10 ou q11, l'autre est fermee pour de bon), la suite s'ouvre par l'un OU l'autre cote.
    if (exige.une_de && !exige.une_de.some(faite)) return false;
    // ⚠️ `choix` (1er oct. 2026) : la réponse qu'on a donnée dans une AUTRE mission (`partie.choix`, gardé à sa
    // réussite) — ce qu'on a dit à quelqu'un change ce qu'on nous propose ensuite.
    if (exige.choix && Object.keys(exige.choix).some(function (s) { return (p.choix || {})[s] !== exige.choix[s]; })) return false;
    // ⚠️ `exige.heure` ne se juge PAS ici : `disponibles()` est un filtre
    // statique, sans le moment du jour. L'heure se vérifie au DECLENCHEMENT du
    // téléphone (tranche 3, la police : être au casse-croûte à midi).
    return true;
  }

  /** ⚠️ `ferme` de M16 : une mission FERMEE disparait du telephone ET du carnet.
      C'est ce qui fait les choix (q10/q11, r03/r04, d07/d08, e11, x04). */
  function estFermee(slug) { return (B.partie.fermees || []).indexOf(slug) >= 0; }

  /** La mission `m` a-t-elle besoin du personnage `slug` en ville : il la DONNE, ou l'on doit lui PARLER ? */
  function aBesoinDe(m, slug) {
    return m.donneur === slug || (m.objectifs || []).some(function (o) {
      return !!o && o.type === 'parler' && cibleDuParler(o) === slug;
    });
  }

  /** PARTI (`parti_apres`) : sa mission de depart est faite, et plus rien ne le RETIENT en ville.

      ⚠️ Ce qui le retient : une mission ni faite ni fermee qui a besoin de lui (`aBesoinDe`). Marco
      disparait apres m97 (« Moi, je disparais », Martin, 29 sept. 2026) — mais m97 ne demande que m5 et
      trois districts : on peut la jouer avant f08 et f09 (les siennes, apres f02, f03 et f06), et avant f12,
      ou Madame Thibodeau t'envoie chercher SON enveloppe au garage. Parti tout de suite, il laissait trois
      missions qu'on ne pouvait plus jamais jouer. Il s'en va donc apres la derniere des deux : m97, ou la
      derniere qui avait besoin de lui (`jouerLaFin`). Ti-Guy, Berube, Cindy, Jo et le maire ne sont
      attendus par aucune autre mission : pour eux, rien ne change. */
  function estParti(p) {
    if (!p || !p.parti_apres || !faite(p.parti_apres)) return false;
    return !defs().some(function (m) { return !faite(m.slug) && !estFermee(m.slug) && aBesoinDe(m, p.slug); });
  }

  /** Les missions qu'on peut commencer : prerequis faits, pas encore faites,
      aucune en cours, `exige` tenu, et pas fermees. */
  function disponibles() {
    if (B.partie.mission) return [];
    // ⚠️ UNE PETITE JOB (`passant`) ne s'offre que dans la rue, par le passant qui t'interpelle (`Jobs`) : jamais au
    // téléphone, au carnet, ni par la bulle d'un donneur.
    return defs().filter(function (m) {
      return !m.passant && !faite(m.slug) && !estFermee(m.slug) && m.prerequis.every(faite) && exigeTenu(m.exige) && !absentLHiver(personnage(Chapitres.donneurDe(m)));
    });
  }

  /** ABSENT L'HIVER (`absent_l_hiver` : le Bonimenteur, dont la foire est fermee tant que la neige tient,
      docs/jalons/la-foire-fermee-l-hiver.md) : il n'est pas en ville, et ses missions attendent qu'il revienne.
      ⚠️ Celui de la foire revient quand la TRICHE l'ouvre (`triche('foire')`) : sa foire est ouverte, il y est. */
  function absentLHiver(p) {
    if (p && p.ou === 'foire' && triche('foire')) return false;
    return !!(p && p.absent_l_hiver && typeof Saisons !== 'undefined' && Saisons.enHiver());
  }

  /** Qui part pour l'hiver s'en va HORS DE L'ECRAN, et revient au degel — sans recharger la partie
      (`creerDonneurs` ne pose qu'au chargement). ⚠️ Jamais pendant une mission : on ne retire pas la
      mission de sous les pieds de celui qui la joue ; il part apres. Une fois toutes les cinq secondes
      (`maintenant` : tout de suite — un juge qui vient de poser l'ete). */
  function majSaisonniers(maintenant) {
    if ((!maintenant && B.t % 300 !== 0) || B.interieur || B.bloc || B.cinema) return;
    const enJeu = courante();
    for (const p of personnages()) {
      if (!p.absent_l_hiver) continue;
      const e = donneur(p.slug);
      if (absentLHiver(p)) {
        if (e && !(enJeu && aBesoinDe(enJeu, p.slug)) && !Entites.visibleAEcran(e.x, e.y, 40)) Entites.retirer(e);
      } else if (!e && !estParti(p) && !(p.arrive_apres && !faite(p.arrive_apres))) {
        poserDehors(p);
      }
    }
  }

  function disponibleDe(donneur) {
    return disponibles().find(function (m) { return Chapitres.donneurDe(m) === donneur; }) || null;
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
    if (slug.indexOf('traversier:') === 0) return quaiDuTraversier(slug.slice(11));
    // La NAVETTE DE L'ÎLE (un char sur l'île, 1er oct. 2026) : le bout de SON quai, aux Quais ou à l'île.
    if (slug.indexOf('navette:') === 0) return quaiDuBateau(slug.slice(8), 'navette');
    // `ile:<lieu>` : un lieu DE L'ÎLE qu'on rejoint par l'eau (la navette, la chaloupe) — le devant de sa porte, comme
    // un autre. Le préfixe dit aux juges des barrières qu'on n'y marche pas depuis la ville.
    if (slug.indexOf('ile:') === 0) return lieu(slug.slice(4));
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
    // Une coque qu'on AMARRE ailleurs qu'à son mouillage (m53 : le relais de la rive nord).
    if (slug.indexOf('amarrage:') === 0) return resoudre(slug, courante());
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
  function tuileLibre(x, y, rayonMax, accepte) {
    const tx = Math.floor(x / TT), ty = Math.floor(y / TT);
    let repli = null;
    for (let r = 0; r <= (rayonMax || 4); r++) {
      for (let dy = -r; dy <= r; dy++) for (let dx = -r; dx <= r; dx++) {
        if (Math.max(Math.abs(dx), Math.abs(dy)) !== r) continue;
        if (!Monde.marchablePieton(tx + dx, ty + dy) || Monde.estChaussee(tx + dx, ty + dy)) continue;
        const place = { x: (tx + dx) * TT + 8, y: (ty + dy) * TT + 8 };
        if (accepte && !accepte(place)) continue;
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
    // ⚠️ Le mot peut être un GENRE de devanture (`boutique:artisan`, la quincaillerie ;
    // `boutique:industrie`, la Shop) : c'est la famille du comptoir, pas un mot de l'enseigne.
    // Chercher « ARTISAN » dans les textes ne trouvait rien — ni flèche, ni coupe d'intro
    // (f04, p01). Une devanture qu'on visite (`porte`) passe devant une porte peinte.
    const genres = (B.defs && B.defs.devantures && B.defs.devantures.genres) || [];
    const g = genres.findIndex(function (q) { return q.slug === String(mot).toLowerCase(); });
    for (const d of devs) {
      if (g >= 0 ? d.genre !== g : (!d.texte || sansAccent(d.texte).indexOf(n) < 0)) continue;
      // Une porte peinte ne vend rien : elle ne gagne que s'il n'y a aucune vraie porte du genre.
      const d2 = dist2(d.x * TT + 8, (d.y + 1) * TT + 8, j.x, j.y) + (g >= 0 && !d.porte ? 1e12 : 0);
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

  /** Le bout du quai du traversier dans le district `district` (`traversier.ESCALES`) : la
      tuile du milieu de ses accès, là où le pont touche la rive (M13, le capitaine Bérubé et
      m99). `null` si la ville n'a pas de traversier. */
  function quaiDuTraversier(district) { return quaiDuBateau(district, 'traversier'); }

  /** Le bateau d'un `embarquer` ou d'un lieu : le traversier (par défaut), ou la NAVETTE de l'île (`bateau: navette`)
      — la même fabrique (`traversier.js`), une autre route (les Quais et l'île). */
  function bateauNomme(bateau) {
    if (bateau === 'navette') return typeof Navette !== 'undefined' ? Navette : null;
    return typeof Traversier !== 'undefined' ? Traversier : null;
  }

  /** Le bout du quai du `bateau` dans le district `district` (son escale) : la tuile du milieu de ses accès. */
  function quaiDuBateau(district, bateau) {
    const b = bateauNomme(bateau), d = b ? b.donnees() : null;
    const q = d && d.escales.find(function (e) { return e.district === district; });
    if (!q || !q.acces.length) return null;
    const t = q.acces[Math.floor(q.acces.length / 2)];
    return { x: t[0] * TT + 8, y: t[1] * TT + 8, nom: bateau === 'navette' ? 'le quai de la navette' : 'le quai du traversier', escale: q };
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

  /** `amarrage:<lieu>` : l'amarrage de la ville (`carte.amarrages`) le plus près d'un lieu —
      un point d'EAU au pied d'un quai, où une coque accoste et d'où l'on débarque. m53 y met le
      relais de Josée, de l'autre côté de la baie (`amarrage:hopital`, la rive nord). `nom` : celui
      du lieu, pour la flèche. Null dans une pièce ou un bloc (pas d'amarrages). */
  function amarragePres(slug) {
    const places = (Monde.carte.def && Monde.carte.def.amarrages) || [], l = lieu(slug);
    if (!places.length || !l) return null;
    let meilleure = null, dMin = Infinity;
    for (const a of places) {
      const x = a.x * TT + 8, y = a.y * TT + 8, d2 = (x - l.x) * (x - l.x) + (y - l.y) * (y - l.y);
      if (d2 < dMin) { dMin = d2; meilleure = { x: x, y: y, amarrage: a, nom: l.nom }; }
    }
    return meilleure;
  }

  /** `ou` d'un objectif ou d'un personnage → un pixel. */
  function resoudre(ou, m) {
    if (!ou) return null;
    if (ou === 'donneur') return ouTrouver(Chapitres.donneurDe(m));
    if (ou === 'pont') return lieuPont();
    if (ou === 'quai') return tuileDeQuai();
    if (ou === 'bois') return tuileDeBois();
    if (ou === 'foire') return lieuFoire();
    if (ou === 'amarrage:sven') return amarrageDeSven();
    const deux = ou.split(':');
    if (deux[0] === 'porte') return lieu(deux[1]);
    if (deux[0] === 'amarrage') return amarragePres(deux[1]);
    if (deux[0] === 'ruelle') return ruellePres(deux[1], Number(deux[2]) || 0);   // `ruelle:garage:24`
    if (deux[0] === 'zone') { const z = Monde.carte.zones.find(function (q) { return q.slug === deux[1]; }); return z ? { x: (z.x + z.l / 2) * TT, y: (z.y + z.h / 2) * TT, zone: z } : null; }
    if (deux[0] === 'point') return null;                 // dedans : pas de pixel en ville
    if (deux[0] === 'district') return tuileDeDistrict(deux[1]);
    // `bloc:<slug>` : le passage d'un bloc de carte, en ville — ce qu'une scene montre de la villa.
    if (deux[0] === 'bloc') return passageDuBloc(deux[1]);
    if (deux[0] === 'boutique') return boutiquex(deux[1]);
    if (deux[0] === 'rampe') return tuileDeRampe(deux[1]);
    // `bouee:<n>` (le tour de l'île, i07) : la n-ième bouée du parcours de la baie (`regate.py`). Pas de pixel dedans.
    if (deux[0] === 'bouee') return B.interieur || B.bloc ? null : Regate.point(deux[1]);
    // ⚠️ Le CENTRE de la coque, pas son poste : une caméra le regarde, et
    // `poserLeChar` y fait naître le véhicule, à son cap (`m.angle`).
    if (deux[0] === 'mouillage') { const mo = trouverMouillage(deux.slice(1).join(':')); return mo ? { x: mo.x, y: mo.y, mouillage: mo } : null; }
    return lieu(ou);
  }

  /** Le passage d'un bloc de carte (`B.defs.blocs`), en pixels de la VILLE : le milieu de l'ouverture,
      un pas en deca du bord. Null dans un bloc — il n'y a pas de ville autour — et dans une piece :
      ⚠️ `Monde.carte` y est la carte de la PIECE, et ses mesures posaient le passage de la villa dans le
      bar de Josee. Null, la scene le cherche dans la ville (`Scenes.lieu` → `dansLaVille`), et l'y trouve
      marque `dehors` : une coupe y va, au noir. */
  function passageDuBloc(slug) {
    if (B.bloc || !Monde.carte || Monde.carte.interieur) return null;
    const b = ((B.defs && B.defs.blocs) || []).find(function (q) { return q.slug === slug; });
    if (!b || !b.passage) return null;   // un sous-sol n'a pas de passage : on y descend par un rideau
    const o = b.passage, w = Monde.carte.w, h = Monde.carte.h, milieu = (o.de + o.l / 2) * TT;
    const place = o.bord === 'nord' ? { x: milieu, y: TT } : o.bord === 'sud' ? { x: milieu, y: (h - 1) * TT }
      : o.bord === 'ouest' ? { x: TT, y: milieu } : { x: (w - 1) * TT, y: milieu };
    return { x: place.x, y: place.y, nom: b.nom };
  }

  /** Le bloc qui porte ce lieu (la villa pour `villa_bureau`), ou null : un lieu de la ville. */
  function blocDuLieu(slug) {
    const b = ((B.defs && B.defs.blocs) || []).find(function (q) { return (q.lieux || []).indexOf(slug) >= 0; });
    return b ? b.slug : null;
  }

  function lieuDuPersonnage(slug) {
    const p = personnage(slug);
    if (!p) return null;
    const ou = p.ou.split(':');
    if (ou[0] === 'porte') return lieu(ou[1]);
    if (ou[0] === 'point') {                                // il est dedans : la porte de son commerce
      const piece = pieceDuPoint(ou[1]);
      if (!piece) return null;
      // ⚠️ UN ÉTAGE n'a pas de porte en ville (la chambre de l'hôtel, où dort le maire de m98) : c'est la porte de
      // la pièce dont l'escalier y monte.
      const dessous = lieu(piece.slug) ? null : pieceDessous(piece.slug);
      return lieu(piece.slug) || (dessous ? lieu(dessous) : null);
    }
    // ⚠️ Le POSTE, pas le centre de la coque : Sven se tient sur la jetée, pas
    // dans l'eau (`navires.py` l'exporte pour chaque mouillage).
    if (ou[0] === 'mouillage') { const mo = trouverMouillage(ou.slice(1).join(':')); return mo && mo.poste ? mo.poste : null; }
    // ⚠️ Posé DEHORS, à l'arche — contrairement à un donneur `point:`, il existe
    // vraiment en ville : hélable, GPS, et un `retourner` le trouve.
    if (ou[0] === 'foire') return lieuFoire();
    if (ou[0] === 'traversier') return lieu(p.ou);
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

  /** La pièce dont l'ESCALIER mène à `slug` (le hall de l'hôtel, pour sa chambre), ou null. */
  function pieceDessous(slug) {
    const ville = Monde.carte.ville || Monde.carte;
    const pieces = (ville.def && ville.def.interieurs) || {};
    // ⚠️ Un etage du milieu (des etages dedans aussi) : l'escalier de l'etage du DESSUS y descend aussi. La piece
    // du dessous est celle dont l'escalier MONTE ; a defaut (le tripot : on y descend du casino), n'importe laquelle.
    let aDefaut = null;
    for (const s in pieces) {
      for (const q of (pieces[s].points || [])) {
        if (q.type !== 'escalier' || q.vers !== slug) continue;
        if (!q.descend) return s;
        aDefaut = aDefaut || s;
      }
    }
    return aDefaut;
  }

  // --- Les donneurs, en chair et en os ---------------------------------------------------

  function donneur(slug) {
    return B.entites.find(function (e) { return e.type === 'pieton' && e.personnage === slug && e.vivant; }) || null;
  }

  /** La cible d'un objectif `parler` : le slug du personnage a qui l'on doit
      parler. `cible: "<perso>"` ou `cible: "personnages:<perso>"` nomment un
      personnage de l'histoire ; `cible: "arch:<slug>"` viserait un figurant
      de cet archetype — ⚠️ rien ne le pose encore (f12 a pris cinq commerçants
      qui existent). Les quatre contacts de m6 sont des personnages. */
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
      // donnees, parce qu'ici aucun slug de mission ne s'ecrit (`estParti`).
      if (estParti(p)) continue;
      // Pas encore arrive (`arrive_apres` : le vieux maitre des Mantes, en Floride jusqu'a la chute du Pouce).
      if (p.arrive_apres && !faite(p.arrive_apres)) continue;
      if (absentLHiver(p)) continue;              // parti pour l'hiver (`majSaisonniers` le ramene)
      poserDehors(p);
    }
  }

  /** UN personnage du DEHORS, a sa place (null pour ceux du dedans : ils se posent a l'entree de leur
      piece, `creerDonneursDedans`). */
  function poserDehors(p) {
    if (p.ou.indexOf('porte:') === 0) return poserDonneur(p);
    // ⚠️ Sven se tient sur SON poste a quai (`mouillage:`), pas a une porte :
    // les autres formes (`point:`) restent dedans, posees a l'entree de leur piece.
    if (p.ou.indexOf('mouillage:') === 0) return poserDonneurMouillage(p);
    // Le Bonimenteur, a l'arche de la foire — dehors, comme une porte, mais sans batiment.
    if (p.ou === 'foire') return poserDonneurFoire(p);
    // Le capitaine Bérubé, au bout du quai du traversier (M13).
    if (p.ou.indexOf('traversier:') === 0) return poserDonneurAuQuai(p);
    return null;
  }

  /** UN personnage posé au bout du quai du traversier (`ou: "traversier:<escale>"`) — même
      idée que `poserDonneurFoire` : une place qu'on voit, à côté du lieu. */
  function poserDonneurAuQuai(p) {
    const l = lieu(p.ou);
    if (!l) return null;
    const place = placeVisible(l);
    return place ? creerPersonnage(p, place.x, place.y) : null;
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
      const ecart = Math.max(Math.abs(e.x - place.x), Math.abs(e.y - place.y));
      // ⚠️ ET LE STAND D'UN AMBULANT (la roulotte de cafe du terminus), meme ferme : son
      // vendeur n'existe pas encore quand la partie commence le matin, il arrive a
      // l'ouverture — a son poste, c'est-a-dire sur Ti-Guy, pose a sept pixels de lui. Deux
      // personnes qui tiennent chacune leur place, l'une dans l'autre, se repoussent hors de
      // leur place, cessent de ceder et y reviennent, l'une dans l'autre, six images sur six
      // (le juge de la foule : 333 chevauchements creuses). C'est le STAND qui est toujours la.
      if (e.type === 'ambulant') return ecart < 2 * TT;
      if (e.type !== 'pieton' || !e.vivant) return false;
      return e.personnage && ecart < ECART_DONNEURS * TT;
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
    let collee = null, repli = null;
    for (const [dx, dy] of essais) {
      const place = tuileDeTrottoir(tx0 + dx, ty0 + dy);
      if (!place || placeTenue(place)) continue;
      if (!repli) repli = place;
      const c = partCachee(place.x, place.y);
      if (!libre && colleeAUnMeuble(place)) {
        if (c < CACHE_MAX && !collee) collee = place;
        continue;
      }
      if (c < CACHE_MAX) return place;
      if (c < part) { part = c; meilleure = place; }
    }
    // ⚠️ Plutot une place a moitie cachee, collee a un banc, ou plus loin, que celle d'un autre : Fern,
    // troisieme donneur du terminus apres Ti-Guy, Mo et la roulotte de cafe, avait epuise ses essais
    // et retombait sur `premiere` — le poste du vendeur de cafe. Les deux s'y poussaient hors de leur
    // place six images sur six (le juge de la foule : 333 creusements). Le tour plus loin ne se fait
    // que si rien n'a ete trouve : les autres donneurs ne bougent pas d'un pixel.
    if (!collee && !meilleure && !repli && !libre) {
      for (const [dx, dy] of [[7, 0], [-7, 0], [5, 1], [-5, 1], [6, 1], [-6, 1], [8, 0], [-8, 0]]) {
        const place = tuileDeTrottoir(tx0 + dx, ty0 + dy);
        if (place && !placeTenue(place)) return place;
      }
      // ⚠️ Et JAMAIS `premiere` quand un autre la tient : Gros-Boulon, troisieme a la porte de la
      // fourriere (30 sept. 2026), n'avait que de l'asphalte et du grillage autour de la guerite —
      // aucun essai ne tombait sur un trottoir, et il se posait sur Gilles au pixel pres. La tuile
      // libre la plus proche de cette premiere place, que personne ne tient.
      const autour = tuileLibre(premiere.x, premiere.y, 6, function (q) { return !placeTenue(q); });
      if (autour) return autour;
    }
    return collee || meilleure || repli || premiere;
  }

  //: Dans une cour, deux personnages se tiennent a au moins tant de tuiles l'un de l'autre : ils ont
  //: la place, et « trop colles » (Martin, 30 sept. 2026) se voit de plus loin qu'au trottoir.
  const ECART_COUR = 3;

  /** La cour CLOTUREE sur laquelle donne une porte (la guerite de la fourriere donne sur son lot,
      derriere le grillage) — ou null. En dedans du grillage : la cloture est le tour du rectangle. */
  function courDe(l) {
    const lot = Monde.carte.fourriere;
    if (!lot) return null;
    const tx = Math.floor(l.x / TT), ty = Math.floor(l.y / TT);
    return tx > lot.x && tx < lot.x + lot.largeur - 1 && ty > lot.y && ty < lot.y + lot.hauteur - 1 ? lot : null;
  }

  /** Ou se tient, DANS LA COUR, qui y travaille (`dans_la_cour` : Gilles, le gardien du lot ; Ti-Loup,
      qui y achete les epaves). ⚠️ La cour est de l'asphalte : `placeVisible` n'y voit aucun trottoir et
      les posait DEHORS, de l'autre cote du grillage, colles aux autres (Martin, 30 sept. 2026).

      Pas sur une case du lot (un char saisi y est gare : trois tuiles depuis son fond), ni devant la
      porte, ni dans un mur, ni a moins de `ECART_COUR` d'un autre personnage. SANS DE : la plus proche
      de la porte, en comptant double l'ecart en hauteur — on se tient le long de la guerite, face aux
      chars, pas au fond contre le grillage. */
  function placeDansLaCour(l, lot) {
    const px = Math.floor(l.x / TT), py = Math.floor(l.y / TT);
    // Le fond d'une case porte le pare-chocs : le char s'etend de la sur trois tuiles, A RECULONS
    // (une case « N » descend vers le sud) — pas des deux cotes, sinon la bande le long de la guerite
    // tombe avec.
    const RECUL = { N: [0, 1], S: [0, -1], O: [1, 0], E: [-1, 0] };
    const surUneCase = function (tx, ty) {
      return lot.places.some(function (c) {
        const r = RECUL[c.sens] || [0, 0];
        for (let k = 0; k < 3; k++) if (c.x + r[0] * k === tx && c.y + r[1] * k === ty) return true;
        return false;
      });
    };
    const loin = function (place) {
      return !B.entites.some(function (e) {
        return e.type === 'pieton' && e.vivant && e.personnage
          && Math.max(Math.abs(e.x - place.x), Math.abs(e.y - place.y)) < ECART_COUR * TT;
      });
    };
    let meilleure = null, score = Infinity;
    for (let ty = lot.y + 1; ty < lot.y + lot.hauteur - 1; ty++) {
      for (let tx = lot.x + 1; tx < lot.x + lot.largeur - 1; tx++) {
        if (Monde.bloque(tx, ty, Monde.MASQUE_PIETON) || Monde.devantDUnePorte(tx, ty) || surUneCase(tx, ty)) continue;
        const place = { x: tx * TT + 8, y: ty * TT + 8 };
        if (!loin(place) || partCachee(place.x, place.y) >= CACHE_MAX) continue;
        const d = Math.abs(tx - px) + 2 * Math.abs(ty - py);
        if (d < score) { score = d; meilleure = place; }
      }
    }
    return meilleure;
  }

  /** UN personnage du dehors, pose devant sa porte — ou null quand la porte ou la
      place manque. ⚠️ Il ne regarde ni `parti_apres` ni s'il est deja la : c'est
      `creerDonneurs` qui juge s'il doit exister, et le debug (`Hud.menuSautMissions`)
      qui le REPOSE pour refaire la mission d'un donneur parti. */
  function poserDonneur(p) {
    const l = lieu(p.ou.slice(6));
    if (!l) return null;
    // Qui travaille dans la cour clôturée de sa porte s'y tient (la fourrière : Gilles et Ti-Loup).
    const cour = p.dans_la_cour ? courDe(l) : null;
    // A deux tuiles de la porte : assez pres pour le voir, assez loin pour
    // qu'ACTION au pas de la porte serve encore a autre chose — et JAMAIS derriere
    // un abribus : `placeVisible` ecarte la tuile ou du decor le cache.
    const place = (cour && placeDansLaCour(l, cour)) || placeVisible(l);
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
      // ⚠️ `arrive_apres` : pas encore la (le vieux maitre, en Floride jusqu'a la chute du Pouce). Sa salle n'a
      // que ses eleves, et personne ne s'y tient a sa place.
      if (p.arrive_apres && !faite(p.arrive_apres)) continue;
      // ⚠️ `parti_apres` DEDANS AUSSI (M13) : le maire Tanguay quitte la chambre de l'hotel apres m98. Jusque-la,
      // aucun personnage de piece ne partait — la regle n'etait ecrite que pour ceux de la rue.
      if (estParti(p)) continue;
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

  /** Celui qui parle est-il la, a portee de voix ?

      ⚠️ UN DONNEUR A LA BARRE (Martin, 1er oct. 2026, i07) : Leo court le tour de l'ile dans le bateau de son
      pere, a trente pixels de ta chaloupe, et son « A trois, on part » se disait AU COMBINE — `present` ne
      cherchait que le pieton, reste devant son hangar. Le rival d'une course (`contre.qui`, `v.regate.qui`)
      est aussi lui : a portee de voix, il parle en personne. */
  function present(qui) {
    const j = B.joueur, e = donneur(qui), r2 = RAYON_PRESENT * RAYON_PRESENT;
    if (!j) return false;
    if (e && e.dessine !== false && dist2(e.x, e.y, j.x, j.y) < r2) return true;
    const a = B.mission && B.mission.entites;
    return !!(a && a.some(function (v) {
      return v.regate && v.regate.qui === qui && B.entites.indexOf(v) >= 0 && dist2(v.x, v.y, j.x, j.y) < r2;
    }));
  }

  /** Les repliques d'une partie, pretes a dire, avec leur slug de voix.

      ⚠️ AU COMBINE : l'appel toujours, et l'echec toujours — on n'est jamais a
      cote du donneur quand on rate. L'intro, la fin et les repliques `pendant`
      le sont QUAND CELUI QUI PARLE N'EST PAS LA (`auto`, tranche a la ligne) :
      une fin de M4 jouee au garage, Bouchard au casse-croute, se dit au
      telephone ; la meme ligne dite a deux pas ne l'est pas. Le client du taxi,
      lui, est assis dans le char. */
  function lignesDe(m, partie, filtre) {
    // ⚠️ UN PASSANT (une petite job, `Jobs`) n'a pas ton numéro : tout ce qu'il dit, il le dit en personne.
    const passant = !!(m && m.passant);
    const toujours = !passant && (partie === 'appel' || partie === 'echec');
    const auto = !passant && (partie === 'intro' || partie === 'fin' || partie === 'pendant');
    // ⚠️ L'HIVER, la variante d'hiver (`hiver`, `_l(..., hiver=...)`) : l'hiver la moto est remisee
    // et le fuyard file en motoneige — la replique le dit, avec SA voix (le slug suivi de `-hiver`).
    const hiver = typeof Saisons !== 'undefined' && Saisons.enHiver();
    return ((m && m.dialogue && m.dialogue[partie]) || []).map(function (l, i) {
      const h = hiver && l.hiver;
      return { qui: l.qui, texte: h ? l.hiver : l.texte, telephone: toujours, auto: auto, objectif: l.objectif,
               slug: slugDeVoix(m, partie, i) + (h ? '-hiver' : ''), humeur: l.humeur, dite: tenu(l),
               // Un CHOIX (1er oct. 2026) : la question (`choix`) et la branche d'une réplique (`branche`).
               choix: l.choix || null, branche: l.branche || null };
    }).filter(function (l) { return l.dite && (!filtre || filtre(l)); });
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
    // ⚠️ Dans une scène, la Voix ne s'arme pas (`Scenes.jouer` l'a fait) ; ailleurs (une question redemandée,
    // `demanderLeChoix`), on parle comme un `dire`.
    if (!B.scene) Entree.contexte('dialogue');
    suivante();
    return true;
  }

  /** Le slug de voix d'une replique : `<qui>-<mission>-<n>`, n compte a travers
      appel, intro, client, fin, echec, pendant, renvoi, accueil — exactement comme `missions.repliques()`. */
  /** Le texte d'un objectif EN CE MOMENT : l'hiver, sa variante (`hiver`, « RATTRAPE LE FUYARD EN
      MOTONEIGE ») — la meme saison que les repliques (`lignesDe`) et que le char (`charDeSaison`). */
  function texteDObjectif(o) {
    return o && o.hiver && typeof Saisons !== 'undefined' && Saisons.enHiver() ? o.hiver : (o && o.texte);
  }

  function slugDeVoix(m, partie, i) {
    // ⚠️ `pendant` APRES `echec`, puis `renvoi`, comme `missions.PARTIES` : inseree plus tot,
    // elle renommerait des voix deja generees.
    const ordre = ['appel', 'intro', 'client', 'fin', 'echec', 'pendant', 'renvoi', 'accueil', 'generique', 'hele'];
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
    // ⚠️ UNE QUESTION ATTEND SA RÉPONSE : ni ACTION, ni le temps de lire, ni la voix finie ne la passent — seul un
    // choix dans la boîte des réponses (`choisir`) rend la parole.
    if (c.question) return;
    c.i++;
    // Les répliques de l'AUTRE branche d'un choix ne se disent pas (`branche=`, `missions.erreurs_de_choix`).
    const m = c.mission ? mission(c.mission) : null;
    while (c.i < c.lignes.length && c.lignes[c.i].branche && c.lignes[c.i].branche !== brancheDe(m)) c.i++;
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
    // Un passant (une petite job) porte le nom que sa mission lui donne : « Le débardeur », pas « Un passant ».
    const nom = m && m.passant && l.qui === m.donneur ? m.passant.nom : (p ? p.nom : l.qui);
    Hud.dialogue(c.anonyme ? '' : nom + (l.telephone ? ' (AU TÉLÉPHONE)' : ''), decouper(l.texte), 0,
                 c.anonyme || (m && m.passant) ? null : { slug: l.qui, humeur: l.humeur || 'neutre' });
    c.voix = Son.Voix.parler(l.slug, { telephone: l.telephone, fin: function () { if (B.cinema === c && c.i === c.lignes.indexOf(l)) c.duree = Math.min(c.duree, c.t + 20); } });
    if (B.dialogue && c.voix) B.dialogue.voix = true;
    // La QUESTION : la réplique reste dans sa boîte, sa voix continue, et les réponses s'ouvrent au-dessus.
    if (l.choix && m && B.partie.mission && B.partie.mission.slug === m.slug && !B.partie.mission.branche) ouvrirLeChoix(c, l, m);
  }

  // --- Un choix dans un dialogue (1er oct. 2026, Martin) -------------------------------------------------------
  //
  // ⚠️ Une réplique POSE une question (`choix`, `missions.py`) ; le joueur répond — deux ou trois réponses, au
  // clavier, à la manette ou au doigt, dans la boîte des réponses (un menu du HUD `obligatoire`, posé AU-DESSUS de
  // la boîte de dialogue, qui reste lisible) — et la mission bifurque : ses objectifs (`branche`), ses répliques
  // (`branche`), ce que la fin paie (`branches`). La réponse vit dans `partie.mission.branche` (la sauvegarde la
  // garde), puis dans `partie.choix[slug]` quand la mission réussit.

  //: Combien d'images la boîte des réponses fait la sourde oreille en s'ouvrant : l'ACTION qui passait la
  //: réplique d'avant ne doit pas choisir la première réponse dans la foulée.
  const CHOIX_SOURD = 12;

  /** La question de la mission `m` : `{ partie, i, ligne }`, ou null. */
  function questionDe(m) {
    const ordre = ['appel', 'intro', 'client', 'fin', 'echec', 'pendant', 'renvoi', 'accueil', 'generique'];
    for (const partie of ordre) {
      const lignes = (m && m.dialogue && m.dialogue[partie]) || [];
      for (let i = 0; i < lignes.length; i++) if (lignes[i].choix) return { partie: partie, i: i, ligne: lignes[i] };
    }
    return null;
  }

  /** La branche de la mission `m` : la réponse donnée (en cours, puis gardée à la réussite) — et, tant qu'on n'a
      pas répondu, la PREMIÈRE réponse (un banc qui saute à la fin, une vieille partie : la mission se finit quand
      même, sur une branche qui existe). Null pour une mission sans question. */
  function brancheDe(m) {
    if (!m) return null;
    const p = B.partie;
    if (p.mission && p.mission.slug === m.slug && p.mission.branche) return p.mission.branche;
    if (p.choix && p.choix[m.slug]) return p.choix[m.slug];
    const q = questionDe(m);
    return q ? q.ligne.choix[0].cle : null;
  }

  /** Ce que la fin de `m` accorde : son `donne`, et par-dessus celui de la branche choisie (`branches`). */
  function donneDe(m) {
    const b = ((m && m.branches) || {})[brancheDe(m)] || {};
    return Object.assign({}, (m && m.donne) || {}, b.donne || {});
  }

  /** La boîte des réponses. */
  function ouvrirLeChoix(c, l, m) {
    c.question = true;
    Hud.ouvrirMenu({
      titre: 'TA RÉPONSE', choix: true, obligatoire: true, classeur: null, sourd: CHOIX_SOURD,
      items: l.choix.map(function (r) {
        return { libelle: r.texte, cle: r.cle, faire: function () { choisir(r.cle); } };
      }),
    });
  }

  /** On a répondu : la mission prend sa branche, et la conversation reprend là où la question l'avait laissée. */
  function choisir(cle) {
    const c = B.cinema, p = B.partie;
    if (!p.mission) return false;
    p.mission.branche = cle;
    if (B.menu && B.menu.choix) Hud.fermerMenu();
    noter('TU AS RÉPONDU : ' + (((c && c.lignes[c.i] && c.lignes[c.i].choix) || []).find(function (r) { return r.cle === cle; }) || { texte: cle }).texte);
    Missions.sauvegarderPartie();
    if (!c) return true;
    c.question = false;
    Entree.contexte('dialogue');
    suivante();
    return true;
  }

  /** La question qu'on n'a pas encore répondue — passée avec la scène qui la posait, ou une partie reprise
      avant la réponse : elle se REPOSE (sa réplique, sa voix, ses réponses) avant que la mission bifurque. */
  function demanderLeChoix(m, suite) {
    const q = questionDe(m);
    if (!q) { suite(); return; }
    const ligne = lignesDe(m, q.partie)[q.i];
    ligne.telephone = false; ligne.auto = false;
    direLignes([ligne], { mission: m.slug, partie: q.partie, fin: suite });
  }

  /** Un choix reste-t-il à faire avant de jouer l'étape d'après ? */
  function choixEnAttente(m, p) {
    if (p.branche || !questionDe(m)) return false;
    const suivant = m.objectifs[p.etape + 1];
    // Un objectif qui bifurque, ou la fin (ce que paie chaque réponse) : on ne la passe pas sans avoir répondu.
    return !suivant || !!suivant.branche;
  }

  function finir() {
    const c = B.cinema;
    B.cinema = null;
    B.dialogue = null;
    Son.Voix.couper();
    // ⚠️ Pendant une scene, la derniere replique ne rend PAS les commandes :
    // la scene tourne encore (le car repart, le titre s'inscrit) et PAUSE doit
    // la passer jusqu'au bout.
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
    if (c.question) return;
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
    // ⚠️ ET PAS FRAPPE : les coups qu'on martele encore au moment ou la
    // mission se gagne sautaient les repliques de fin (Martin, 30 sept. 2026).
    const bouton = c.t > 1 && Entree.neuf('action');
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
    // ⚠️ Pendant une mission, l'echeance repart de zero : ratee ou abandonnee, elle ne doit
    // pas laisser derriere elle une sonnerie deja due, qui tomberait a la seconde de l'echec.
    if (p.mission) p.appelT = null;
    if (B.cinema || p.mission || B.interieur || B.finEnAttente) return;
    if (B.sonnerie) {
      if (B.t < B.sonnerie.t) return;                     // ca sonne encore : on ne decroche pas
      const m = mission(B.sonnerie.slug);
      B.sonnerie = null;
      // ⚠️ On a pu aller voir le donneur pendant que ca sonnait : un appel qui
      // annonce une mission deja prise (ou deja annoncee) ne se dit pas.
      if (!m || p.appels[m.slug] || !disponibles().some(function (x) { return x.slug === m.slug; })) return;
      p.appels[m.slug] = true;
      p.dernierAppel = demiJournee();
      // Un chapitre à reprendre : pas l'appel de son premier donneur, un rappel.
      if (Chapitres.depart(m) > 0) { Hud.message('RAPPEL : ' + m.titre.toUpperCase() + ' — VA VOIR ' + personnage(Chapitres.donneurDe(m)).nom.toUpperCase(), 220); return; }
      dire(m, 'appel', function () { Hud.message('VA VOIR ' + personnage(Chapitres.donneurDe(m)).nom.toUpperCase(), 180); });
      return;
    }
    // ⚠️ `m.prerequis.length` SEUL dit « celle-la s'annonce au telephone ». On y lisait
    // aussi `m.dialogue.appel.length`, et ce n'est plus dans le paquet — mais c'etait
    // deja une tautologie : la seule mission sans replique d'appel est la premiere, et
    // elle n'a pas de prerequis. Un juge de `missions.py` tient les deux ensemble.
    const dispo = disponibles();
    const prochaine = plusProche(dispo.filter(function (m) { return m.prerequis.length && !p.appels[m.slug]; }));
    if (!prochaine) return;
    // ⚠️ Son texte AVANT sa sonnerie : il vole pendant que le delai s'ecoule, et le
    // combine ne sonne jamais sur une mission qui n'aurait rien a dire.
    if (!charger(prochaine.slug)) return;
    // Une mission deja annoncee et toujours la (ni prise, ni faite) : on n'empile pas un
    // deuxieme appel par-dessus, on laisse le temps d'y aller.
    const attend = dispo.some(function (m) { return p.appels[m.slug]; });
    const delai = attend ? DELAI_RELANCE : DELAI_APPEL;
    // ⚠️ `appelT` est dans la SAUVEGARDE, `B.t` repart de zero a chaque chargement : une
    // echeance plus loin que le plus long des delais vient d'une autre session.
    if (p.appelT === undefined || p.appelT === null || p.appelT - B.t > DELAI_RELANCE) { p.appelT = B.t + delai; return; }
    if (B.t < p.appelT) return;
    // ⚠️ LE TÉLÉPHONE QUI TRIE (M16, 28 sept. 2026). Avec cent missions, il sonnerait sans
    // arrêt : jamais deux appels dans la même DEMI-JOURNÉE (l'échéance tient, et ça sonne dès
    // que la suivante commence), et jamais à trois étoiles et plus — on ne décroche pas en
    // pleine poursuite. Le donneur qu'on croise hèle quand même (`majBulles`) : le téléphone
    // n'est qu'une des deux portes.
    if (typeof p.dernierAppel === 'number' && demiJournee() <= p.dernierAppel) return;
    if (B.recherche && B.recherche.etoiles >= 3) return;
    p.appelT = null;
    // `Son.SFX.telephone()` rend ce que dure la sonnerie, en secondes (le mp3,
    // ou les trois bips de la synthese) ; 60 images font une seconde, et une
    // image au moins : le dialogue ne part jamais dans celle ou ca sonne.
    B.sonnerie = { slug: prochaine.slug, t: B.t + Math.max(1, Math.round((Son.SFX.telephone() || 0) * 60)) };
  }

  /** La tenue `slug` du catalogue (`B.defs.tenues`), ou null. */
  function tenueDef(slug) { return (B.defs.tenues || []).find(function (t) { return t.slug === slug; }) || null; }

  /** L'option `tenue` d'un objectif (M16, f10 — « en la portant ») : vrai tant qu'on ne
      porte PAS cette tenue-là (le linge, ou le chapeau pour une tenue de tête). */
  /** Porte-t-on la tenue `slug` (le linge, ou le chapeau d'une tenue de tête) ? Le casse le demande au garde. */
  function porteLaTenue(slug) { return !tenueManque({ tenue: slug }); }

  function tenueManque(o) {
    if (!o || !o.tenue) return false;
    const p = B.partie;
    return !Object.keys(PLACES_DE_TENUE).some(function (e) { return p[PLACES_DE_TENUE[e]] === o.tenue; });
  }

  /** La demi-journée de la partie : deux par jour, minuit-midi puis midi-minuit. */
  function demiJournee() { return B.partie.jour * 2 + (B.partie.heure >= 0.5 ? 1 : 0); }

  /** Des missions à annoncer, celle dont le donneur se tient le PLUS PRÈS : il appelle
      d'abord (M16). ⚠️ Sa porte en ville (`lieuDuPersonnage`), pas son sprite : un donneur
      qui marche ne change pas qui appelle, et le choix ne dépend que de la carte. À égalité
      — ou sans adresse —, l'ordre du catalogue, qui reste celui de l'histoire. */
  function plusProche(liste) {
    const j = B.joueur;
    let meilleure = null, dMin = Infinity;
    for (const m of liste) {
      const l = lieuDuPersonnage(Chapitres.donneurDe(m));
      const d = l && j ? dist2(l.x, l.y, j.x, j.y) : Infinity;
      if (!meilleure || d < dMin) { meilleure = m; dMin = d; }
    }
    return meilleure;
  }

  // --- Parler a quelqu'un -----------------------------------------------------------------

  /** ACTION pres d'un personnage (ou sur son point, dedans). Rend true si ca a fait quelque chose. */
  function parler(slug) {
    const p = personnage(slug);
    if (!p || B.cinema) return false;
    // ⚠️ LE PASSANT QUI T'A INTERPELLÉ (une petite job, `Jobs`) : lui parler, c'est prendre sa job — son intro, puis
    // la mission, sans téléphone. Il ne se « rencontre » pas : c'est un passant.
    const job = Jobs.offreDe(slug);
    if (job) { poserPuisDireLIntro(job); return true; }
    const premiere = rencontrer(slug);
    const enCours = courante();
    // ⚠️ L'objectif `parler` d'une mission : on l'accomplit en parlant a SA
    // cible, pas au donneur. m6 t'envoie serrer la main de quatre personnes :
    // c'est la poignee qui compte, et elle est ICI, dans le moteur.
    if (enCours) {
      const o = objectif();
      if (o && o.type === 'parler' && cibleDuParler(o) === slug && tenueManque(o)) {
        // « EN LA PORTANT » (f10) : il ne te reconnaît pas dans ce linge-là.
        Hud.message('IL NE TE RECONNAÎT PAS — ENFILE : ' + tenueDef(o.tenue).nom.toUpperCase(), 180);
        return true;
      }
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
    // ⚠️ Le donneur de l'ACTE (un chapitre en a plusieurs), et `avancer` plutôt que `reussir` : un `retourner`
    // au milieu d'un chapitre passe à l'acte suivant ; le dernier réussit (`avancer` n'a plus d'objectif).
    if (enCours && Chapitres.donneurDe(enCours) === slug) {
      const o = objectif();
      if (o && o.type === 'retourner') { avancer(); return true; }
      Hud.message(objectif() ? objectif().texte : '', 150);
      return true;
    }
    const m = disponibleDe(slug);
    if (m) { poserPuisDireLIntro(m); return true; }
    const mn = B.defs.marche_noir;
    if (mn && slug === 'josee' && faite(mn.apres)) { Hud.ouvrirMenu(Missions.menuMarcheNoir()); return true; }
    // Mireille (le DOJO DION, `dojo.js`) : la premiere fois, elle se PRESENTE (« Qui parle se
    // nomme ») ; ensuite, ACTION ouvre ses COURS. Elle n'a pas de repos.
    if (slug === 'mireille') { Dojo.accueillir(premiere); return true; }
    // Louise, du Clairon : elle regarde ta photo (docs/jalons/des-photos-pour-le-clairon.md).
    if (slug === 'louise') { Photos.accueillir(premiere); return true; }
    const repos = B.defs.repos || {};
    const apres = !!(repos.apres && faite(repos.apres));
    // ⚠️ Le repos se DIT aussi : `<qui>-repos-1` avant `repos.apres`, `-2` ensuite (`missions.
    // repliques_de_repos`). Sans le mp3 (pas encore genere), la boite reste muette — le filet.
    const voix = slug + '-repos-' + (apres ? 2 : 1);
    const dite = Son.Voix.histoire().some(function (v) { return v.slug === voix && v.fichier; });
    // ⚠️ `p.repos` : un repos a lui (l'ile — « le Faubourg est tranquille » y mentirait).
    const texte = p.repos ? p.repos[apres ? 1 : 0]
      : (apres ? repos.texte_apres : (repos.texte || 'REVIENS ME VOIR PLUS TARD.'));
    Hud.dialogue(p.nom, [texte], dite ? 220 : 120,
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
    // ⚠️ LE TEXTE D'ABORD. Sans lui, la mission se poserait et son intro ouvrirait une
    // boite vide. La bulle du donneur l'a demande bien avant (`majBulles`) : on n'arrive
    // ici sans texte qu'avec un reseau lent, ou du premier coup dans un banc qui ne pose
    // rien. `porteEnAttente` fait que deux coups d'ACTION ne posent pas la mission deux
    // fois pendant qu'il vole.
    if (!m.dialogue) {
      porteEnAttente = m.slug;
      charger(m.slug, function () {
        if (porteEnAttente !== m.slug) return;
        porteEnAttente = null;
        poserPuisDireLIntro(m);
      });
      return;
    }
    porteEnAttente = null;
    // ⚠️ UN CHAPITRE QU'ON REPREND ne redit pas l'intro de son premier donneur : le marqueur de l'acte a ses
    // propres répliques (`pendant` à son étape), et `annoncer` les arme.
    if (Chapitres.depart(m) > 0) { commencer(m.slug, true); annoncer(m); return; }
    commencer(m.slug, true);
    // La fin de l'intro passe par `SurPlace` : le saut a l'heure et au lieu (`sur_place`), et la
    // frontiere qui s'arme (`gardee`) — une mission sans ces cles annonce tout de suite.
    jouerOuDire(m, 'intro', function () { SurPlace.sauter(m, function () { annoncer(m); }); });
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
    // Une PETITE JOB : son passant se présente à deux pas (`Jobs.offrir`) — c'est lui qui la donne, et qui l'attend.
    if (m.passant) Jobs.offrir(slug, true); else rencontrer(m.donneur);
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
    const d = donneDe(m);
    jouerOuDire(m, 'fin', function () {
      if (d.message) Hud.message(d.message, 200);
      // ⚠️ **QUI S'EN VA EST DANS LES DONNEES** (`parti_apres`), pas dans la
      // scene. `creerDonneurs` ne le repose deja plus a la partie suivante, mais
      // rien ne le retirait de CELLE-CI : c'est la scene ecrite de M1 qui le
      // faisait entrer au garage, et une mission qui n'ecrit pas la sienne
      // laissait son donneur plante devant sa porte jusqu'au rechargement.
      // Ici, aucun slug ne s'ecrit : la fiche dit apres quelle mission il part.
      // ⚠️ Apres SA mission de depart, ou apres la derniere qui le retenait (`estParti` : Marco, m97
      // jouee avant f08, f09 ou f12 — il s'en va a la fin de la derniere).
      for (const p of personnages()) {
        if (p.parti_apres !== m.slug && !aBesoinDe(m, p.slug)) continue;
        if (!estParti(p)) continue;
        const e = donneur(p.slug);
        if (e) Entites.retirer(e);
      }
      // ⚠️ **ET QUI ARRIVE AUSSI** (`arrive_apres` : Cindy apres q04, Diane et Jo apres e01, Zed, le
      // Trappeur, Ti-Loup…) : `creerDonneurs` ne le pose qu'au CHARGEMENT d'une partie — le joueur qui
      // finissait q04 ne trouvait Cindy qu'apres avoir recharge. Ceux du dedans se posent deja a l'entree
      // de leur piece (`creerDonneursDedans`).
      // ⚠️ DANS LA VILLE, meme si la fin se joue dedans (`dansLaVille`) ; dans un bloc de carte (le
      // chalet), le chargement suivant les posera.
      // Un CHAPITRE : ceux qui arrivent après ses missions remplacées aussi (`arriverApres`).
      [m.slug].concat(m.remplace || []).forEach(arriverApres);
      // ⚠️ UNE FIN DE PARTIE (M13) : le générique attend que la scène de fin soit finie
      // (`jouerLeGenerique`) — on est encore dans son dernier appel.
      if (d.generique) B.generiqueEnAttente = m.slug;
      Missions.sauvegarderPartie();
    }, { vehicule: f.vehicule });
  }

  /** Ceux qui ARRIVENT après la mission `slug` (`arrive_apres`) se posent en ville, sans attendre le chargement
      suivant — à la fin d'une mission (`jouerLaFin`) et à la fin d'un acte de chapitre (`Chapitres.ouvrirActe` :
      Zed, qui arrive après p02, doit être devant le phare pour l'acte suivant). */
  function arriverApres(slug) {
    if (B.bloc) return;
    dansLaVille(function () {
      for (const p of personnages()) {
        if (p.arrive_apres !== slug || donneur(p.slug)) continue;
        if (estParti(p) || absentLHiver(p)) continue;
        poserDehors(p);
      }
    });
  }

  /** Les chiffres que le générique écrit (`VALEURS_DE_TITRE`, `missions.py`). */
  function valeursDuGenerique() {
    // La FORTUNE du BILAN (`Hud.menuBilan`) : la poche et le coffre de la planque.
    const p = B.partie, argent = Math.round((p.argent || 0) + ((p.planque && p.planque.coffre) || 0));
    const pieces = function (n) { return String(n).replace(/\B(?=(\d{3})+(?!\d))/g, ' '); };
    const dette = Math.round(p.dette || 0);
    return {
      fortune: pieces(argent),
      missions: String(Object.keys(p.missionsFaites || {}).length),
      proprietes: String(Object.keys(p.proprietes || {}).length),
      jours: String(p.jour || 1),
      dette: dette > 0 ? pieces(dette) + ' $ À SAL' : 'RÉGLÉE',
      liberes: String((p.libere || []).length),
    };
  }

  /** LE GÉNÉRIQUE (M13) : la scène `generique` de la mission, dite par le narrateur du
      Clairon comme l'ouverture (`anonyme`), avec les chiffres de la partie. Puis le BILAN —
      et la partie continue : le générique n'est pas un écran de fin, c'est une scène.
      ⚠️ Une fin vue le reste (`p.fins`, dans la sauvegarde). */
  function jouerLeGenerique() {
    const slug = B.generiqueEnAttente;
    if (!slug || B.cinema || B.scene) return;
    B.generiqueEnAttente = null;
    const m = mission(slug), p = B.partie;
    if (!m || !p) return;
    const fin = function () {
      p.fins = p.fins || {};
      if (!p.fins[slug]) p.fins[slug] = { jour: p.jour || 1 };
      Missions.sauvegarderPartie();
      if (Hud.ouvrirOnglet) Hud.ouvrirOnglet('bilan');
    };
    const scene = m.scenes && m.scenes.generique;
    const etat = scene && Scenes.jouer(scene, {
      mission: m, voix: m.slug, lignes: lignesDe(m, 'generique'), anonyme: true,
      valeurs: valeursDuGenerique(), fin: fin,
    });
    if (!etat) fin();
  }

  // --- Les missions ------------------------------------------------------------------------

  function objectif() {
    const m = courante();
    // ⚠️ `m.objectifs` peut ne pas etre arrive : ils ne sont plus dans le paquet, et une
    // partie reprise en pleine mission les redemande (`maj`). D'ici la, pas d'objectif —
    // plutot que de planter la boucle de dessin, qui lit ceci a chaque image.
    return m && m.objectifs ? m.objectifs[B.partie.mission.etape] || null : null;
  }

  /** `enSilence` : posee sans rien annoncer — son intro va se dire par-dessus,
      et c'est `annoncer` qui parlera quand elle sera finie. */
  function commencer(slug, enSilence) {
    const m = mission(slug);
    if (!m || B.partie.mission) return false;
    // ⚠️ `avant` : ce qu'on avait dans le sac en commençant — une mission ratée ne fait retomber que ce
    // qu'ELLE a fait prendre (`Infiltration.rendre`), jamais la clé d'une mission d'avant.
    const objets = B.partie.objets || {};
    // Un chapitre commence à l'acte où la partie en est (`Chapitres.depart`) ; toute autre mission, au début.
    B.partie.mission = { slug: slug, etape: Chapitres.depart(m) - 1, t: B.t, chocs: 0,
                         avant: Object.keys(objets).filter(function (k) { return objets[k] > 0; }) };
    B.mission = { entites: [], vehicule: null, chars: {}, fuyard: null, chef: null, escorte: null, courses: 0, kos: 0,
                  vol: 0, boulotsDepart: 0, suit: null, protege: null, suivi: null };
    if (!enSilence) { Hud.message(m.titre.toUpperCase(), 180); Son.SFX.mission(); }
    B.mission.auDepart = true;
    avancer(enSilence);
    return true;
  }

  /** Ce que `commencer` aurait dit : le titre, le coup de cuivre, l'objectif. */
  function annoncer(m) {
    const o = objectif();
    if (!B.partie.mission || B.partie.mission.slug !== m.slug) return;
    Hud.message(m.titre.toUpperCase(), 180);
    Son.SFX.mission();
    if (o) Hud.message(texteDObjectif(o), 200);
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
    // ⚠️ SANS SES OBJECTIFS (encore en route, `charger`), rien n'avance : l'etape
    // monterait sur un tableau absent. `maj` attend deja ; un appel direct (la
    // triche, un evenement) ne doit pas plus faire tomber la mission.
    if (!m.objectifs) return;
    // ⚠️ UN CHOIX PAS ENCORE FAIT ne se saute pas : la question se repose avant l'étape qui bifurque (ou la fin).
    if (choixEnAttente(m, p)) { demanderLeChoix(m, function () { if (courante() === m) avancer(enSilence); }); return; }
    // ⚠️ `objet` (l'infiltration) : ce que l'objectif FINI met dans le sac — le code que le terminal
    // pirate crache, et qui ouvre la chambre forte (une serrure `objet` du bloc). `obtenir` le met
    // lui-meme, au moment ou on le ramasse.
    // ⚠️ Au DÉPART (`commencer`), l'étape d'avant n'a pas été faite ICI : un chapitre repris à l'acte 3 ne
    // redonne pas le `donne` de l'acte 2 (la fronde qu'une prison a prise, la manchette).
    const fait = B.mission && B.mission.auDepart ? null : m.objectifs[p.etape];
    if (B.mission) B.mission.auDepart = false;
    if (fait && fait.objet && fait.type !== 'obtenir') { if (!B.partie.objets) B.partie.objets = {}; B.partie.objets[fait.objet] = 1; }
    // `donne` sur un objectif (les chapitres) : accordé quand il est fait. Sa `prime` (celle de la mission que
    // l'acte remplace) se paie et s'annonce au bandeau, qui porte son message — la bande des messages n'a qu'une
    // place, et le carton de l'acte suivant l'écrasait dans la même image.
    if (fait && fait.donne) {
      accorder(fait.donne);
      if (fait.donne.prime) {
        Missions.encaisser(fait.donne.prime, m.titre.toUpperCase(), true);
        Missions.annoncerPrime(fait.donne.prime, fait.donne.message || m.titre.toUpperCase(), 'ACTE RÉUSSI', 0);
      } else if (fait.donne.message) Hud.message(fait.donne.message, 200);
    }
    p.etape++;
    let o = m.objectifs[p.etape];
    // ⚠️ Un acte dont la mission remplacée est DÉJÀ faite (une vieille partie qui a fait p04 sans p05) se saute :
    // on ne le rejoue pas, on ne le repaie pas.
    while (o && o.type === 'acte' && Chapitres.dejaFait(m, p.etape)) { p.etape = Chapitres.marqueurSuivant(m, p.etape); o = m.objectifs[p.etape]; }
    // ⚠️ Un objectif `si`/`sauf` qui ne tient pas (`tenu`) se saute : rien ne se pose, rien ne se dit. Et L'AUTRE BRANCHE
    // d'un choix (`branche`) : ses objectifs ne se jouent pas.
    while (o && (!tenu(o) || (o.branche && o.branche !== brancheDe(m)))) { p.etape++; o = m.objectifs[p.etape]; }
    if (!o || !o.allies) relacherLesAllies();
    relacherLesPoursuivants();
    if (!o) { reussir(); return; }
    // ⚠️ Tout le monde est deja tombe a un essai rate : l'objectif est FAIT.
    // On ne repose pas des morts pour les recoucher.
    if (o.type === 'tuer' && dejaTombes(m.slug, p.etape) >= o.n) { avancer(enSilence); return; }
    p.debutT = B.t;
    if (B.mission) { B.mission.vagues = 0; B.mission.relais = 0; }
    if (o.type === 'acte') {
      Chapitres.ouvrirActe(m, o, p.etape);
      // ⚠️ Sous l'intro (`enSilence`), un marqueur sans saut ni réplique s'enchaîne tout de suite : l'objectif
      // suivant se POSE avant la scène (les Skateux du pont existent quand la caméra va les voir).
      const parle = (m.dialogue.pendant || []).some(function (l) { return l.objectif === p.etape; });
      if (enSilence && !o.sur_place && !parle) { avancer(true); return; }
    }
    // Un `acheter` dont l'article est DÉJÀ en poche au départ : l'étape le dira (`majObjectif`).
    if (o.type === 'acheter' && B.mission && (B.partie.objets[o.article] || B.partie.armes[o.article])) B.mission.acheterDeja = p.etape;
    poser(enSilence);
    if (!enSilence) Hud.message(texteDObjectif(o), 200);
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
    const o = m.objectifs && m.objectifs[p.etape];
    if (!o) return;
    // ⚠️ Toujours dans la VILLE, même quand on est dans une pièce : une scène
    // qui coupe vers la rue doit y trouver ce qu'on pose (`dansLaVille`).
    // `remet` (M16, 28 sept. 2026) : ce que le donneur te met dans les mains quand
    // l'objectif commence — une arme, chargée à plein, et en main. Le seau d'eau de
    // Mado avant les feux (f13) : sans lui, `eteindre` demandait un extincteur que
    // rien ne garantissait, ni plein. Déjà dans le sac, il se remplit.
    if (o.remet && Combat.armeDef(o.remet)) {
      Combat.ramasserArme(o.remet, Combat.armeDef(o.remet).munitions_max || null);
      if (j.arme !== o.remet) Combat.degainer(j, o.remet);
    } else if (o.remet && tenueDef(o.remet) && B.partie.tenues.indexOf(o.remet) < 0) {
      // Une TENUE (f10, la chemise de Rosa) : elle entre au sac comme achetée — on l'enfile
      // au comptoir de Rosa ou à la penderie, pas d'office : se changer se fait quelque part.
      B.partie.tenues.push(o.remet);
    }
    // ⚠️ `treve` (M13, m98 : Bouchard rappelle ses chiens) : la police rentre au poste quand l'objectif
    // commence — les etoiles tombent a zero, comme au garage (`Police.remiseAZero`).
    if (o.treve) Police.remiseAZero();
    // `etoiles` sur n'importe quel objectif (les chapitres) : la police à ce niveau-là au départ — ce que `semer` et
    // `survivre` font déjà plus bas, pour eux.
    if (o.etoiles && o.type !== 'semer' && o.type !== 'survivre' && Police.etoilesAuMoins(o.etoiles)) {
      B.recherche.dernierVu = { x: j.x, y: j.y, t: B.t };
    }
    dansLaVille(function () {
      // ⚠️ `allies` (M13, m98 : « les Morues, les Skateux et les Boulonneux a tes cotes ») : ils arrivent
      // quand l'objectif commence, et restent tant que les objectifs suivants les nomment (`avancer`).
      if (o.allies) poserLesAllies(m, o);
      if (o.poursuite) poserLaPoursuite(m, o);
      if (o.type === 'monter') {
        const v = poserLeChar(m, o, p.etape);
        if (v) B.mission.vehicule = v;
      } else if (o.type === 'tuer') {
        poserLesCravates(m, o, enSilence);
      } else if (o.type === 'ramasser' && o.cible === 'fuyard') {
        poserLeFuyard(m, o);
      } else if (o.type === 'semer' || (o.type === 'survivre' && o.etoiles)) {
        // ⚠️ `survivre` + `etoiles` (M13, m98 : la police du maire) : TENIR a ce niveau-la, pas le semer.
        B.recherche.etoiles = Math.max(B.recherche.etoiles, o.etoiles || 1); B.recherche.vu = 0; B.recherche.flash = 60;
        B.recherche.dernierVu = { x: j.x, y: j.y, t: B.t };
        if (o.escorte) poserLEscorte(m, o);
      } else if (o.type === 'attendre') {
        p.depuis = heuresDeJeu();
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
      } else if (o.type === 'eteindre') {
        // ⚠️ LE FEU DE LA MISSION, pas celui de l'heure (28 sept. 2026) : il prend sur
        // la façade la plus proche de `ou` (`Incendies.allumerPourMission`), une spirale
        // sans dé. Posé avant l'intro comme le reste : la caméra le filme qui brûle.
        const l = resoudre(o.ou, m);
        B.mission.feu = l ? Incendies.allumerPourMission(l.x, l.y) : null;
      } else if (o.type === 'course') {
        // ⚠️ `course` (29 sept. 2026, p04 : « la course de Zed ») : déclarée depuis la v1 et lue par personne — elle
        // avançait dans la même image. Ses `points` (des lieux que `resoudre` connaît) se passent DANS L'ORDRE, à
        // `rayon` tuiles (3), le chrono est l'option `chrono_s` ; `a_pied` : au volant, rien ne compte. Sans dé.
        const pts = (o.points || []).map(function (s) { return resoudre(s, m); }).filter(Boolean)
          .map(function (q) { return { x: q.x, y: q.y }; });
        B.mission.course = { i: 0, points: pts };
        // `contre` (le tour de l'île, i07) : un RIVAL court les mêmes points (`Regate.creerRival`) — s'il passe la
        // dernière avant toi, c'est raté (`battu`). Déclaré depuis la v1, lu par personne jusque-là.
        if (o.contre && typeof o.contre === 'object') {
          const r = Regate.creerRival(m, o, pts);
          if (r) { B.mission.course.rival = r; B.mission.entites.push(r); Hud.message('À VOS MARQUES…', Regate.DECOMPTE); }
        }
      } else if (o.type === 'tenir') {
        // `tenir` (les chapitres, « défendre le phare ») : le compte part de zéro ; les hommes arrivent de loin.
        B.mission.tenu = 0;
        if (o.groupe) poserLesCravates(m, Object.assign({}, o, { loin: o.loin || 14 }), enSilence);
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
        if (m.objectifs[i].type === 'monter' && tenu(m.objectifs[i])) poserLeChar(m, m.objectifs[i], i);
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
    // ⚠️ Et toute COQUE à un amarrage (`amarrage:<lieu>`, i07) : elle passait par `tuileDeRue`, et sur l'île — aucune
    // rue — elle naissait PAR-DESSUS la chaloupe de décor du même amarrage : deux coques soudées, aucune ne bougeait.
    const coque = Vehicules.vehiculeDef(o.vehicule) && Vehicules.vehiculeDef(o.vehicule).eau;
    const surEau = o.ou.indexOf('mouillage:') === 0 || o.ou === 'amarrage:sven' || (coque && o.ou.indexOf('amarrage:') === 0);
    const cleAmarrage = ou && (ou.mouillage || ou.amarrage);
    // ⚠️ « PRENDRE LA COQUE », PAS LA DÉDOUBLER (m52-m54, Sven) : le grand bateau
    // ou la chaloupe mouillés là sont du DÉCOR permanent (`Vehicules.majMouillages`,
    // `majAmarrages`), présents avant même que la mission commence. Sans ce test,
    // `Vehicules.creer` en ferait naître un second par-dessus.
    const dejaAmarre = surEau && cleAmarrage && B.entites.find(function (e) { return e.type === 'vehicule' && e.amarrage === cleAmarrage; });
    // ⚠️ SUR L'ÎLE (`ile:<lieu>`, i04), PAS UNE RUE : l'île n'en a aucune, et la plus proche est en ville, de l'autre
    // côté de l'eau. Une tuile de terre libre devant le lieu, où un char tient (aucun mur, aucun décor solide).
    const surIle = o.ou.indexOf('ile:') === 0;
    const terre = surIle && ou ? tuileLibre(ou.x, ou.y + 2 * TT, 5, function (q) {
      return sansChar(q) && !Monde.bloque(Math.floor(q.x / TT), Math.floor(q.y / TT), Monde.MASQUE_VEHICULE | Monde.EAU);
    }) : null;
    const rue = ou && !surEau ? (surIle ? terre : o.ou.indexOf('ruelle:') === 0 ? ou : (tuileDeRue(ou.x, ou.y, 8, sansChar) || tuileDeRue(ou.x, ou.y, 8))) : null;
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
      // ⚠️ L'HIVER, la moto qui attend (q10, au pont) est une motoneige (`charDeSaison`). Sous la
      // pluie, non : une moto GAREE attend la fin de l'averse, c'est le trafic qui rentre.
      const slug = typeof Vehicules !== 'undefined' && Vehicules.remise(o.vehicule) === 'hiver' ? charDeSaison(o.vehicule) : o.vehicule;
      v = Vehicules.creer(slug, place.x, place.y, angle, { etat: 'stationne', mission: m.slug, aQui: o.prete || null });
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
  // Depuis le 27 sept. 2026 (Martin : « je veux un jeu de labyrinthe electrifie »), un
  // LABYRINTHE (`Circuit`, `circuit.js`) : on guide une etincelle de la prise au port avec
  // le MEME axe unifie que la marche (`Entree.axe` : clavier, manette, joystick tactile),
  // et chaque fil touche est un zap. Il remplace la sequence de directions d'avant.
  // `B.piratage` cloue le joueur (`Entites.majJoueur`) et affame la roue, le combat,
  // l'entree en char et les interactions (memes portes que `B.roue`) : un seul bouton a
  // la fois.

  //: Le labyrinthe fait `longueur + 3` colonnes sur `RANGS_PIRATAGE` rangees (m53, 4 : 7 × 4).
  const RANGS_PIRATAGE = 4;

  /** L'objectif `pirater` EN COURS, ou null. Un seul a la fois : `p.etape` le dit. */
  function objectifDePiratage() {
    const m = courante(), p = B.partie.mission;
    if (!m || !p || !m.objectifs) return null;
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
    // ⚠️ SANS DE : le trace vient de l'empreinte du terminal (la mission, l'etape) — le meme a
    // chaque essai, et la ville ne glisse pas. Les zaps deja pris sur CE terminal reviennent :
    // abandonner ne remet pas le compteur a zero.
    const plan = Circuit.generer(courante().slug + ':' + p.etape, (o.longueur || 4) + 3, RANGS_PIRATAGE);
    const zaps = B.mission && B.mission.zaps ? B.mission.zaps[p.etape] || 0 : 0;
    B.piratage = { etape: p.etape, circuit: Circuit.ouvrir(plan, zaps),
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
      au relachement d'ARME) : on peut revenir, mais on repart de la prise et les
      zaps restent comptes (`B.mission.zaps`, par etape). Un zap secoue l'ecran ;
      au-dela de `essais`, l'alarme. */
  function majPiratage() {
    const r = B.piratage;
    if (Entree.neuf('attaque')) { fermerPiratage(); return; }
    const res = Circuit.maj(r.circuit, Entree.axe);
    if (res === 'zap') {
      if (B.mission) (B.mission.zaps = B.mission.zaps || {})[r.etape] = r.circuit.zaps;
      Son.SFX.erreur();
      B.cam.secousse = Math.max(B.cam.secousse || 0, 0.4);
      if (r.circuit.zaps > r.essais) { fermerPiratage(); echouer('alarme'); }
    } else if (res === 'fini') {
      Son.SFX.menu();
      fermerPiratage(); avancer();
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
  function placeDArrivee(loin, tour) {
    const j = B.joueur;
    if (B.interieur) return null;
    for (const horsChamp of [true, false]) {
      for (let r = loin; r >= loin - 3; r--) {
        for (let k = 0; k < 16; k++) {
          // `tour` (m98, les allies) : on commence le tour ailleurs — de l'autre cote de la rue que ceux
          // qui viennent te chercher. Sans lui, le premier angle libre, comme toujours.
          const a = ((k + (tour || 0)) % 16) * Math.PI / 8;
          const tx = Math.floor((j.x + Math.cos(a) * r * TT) / TT), ty = Math.floor((j.y + Math.sin(a) * r * TT) / TT);
          if (!Monde.marchablePieton(tx, ty)) continue;
          const place = { x: tx * TT + 8, y: ty * TT + 8 };
          // ⚠️ HORS DE L'ECRAN CENTRE SUR LE JOUEUR, pas de celui d'a present : le point se
          // choisit quand la mission se pose — la camera est alors sur la scene, ou en retard
          // sur un joueur qui vient d'arriver — et ils naissent quand elle est REVENUE sur
          // lui. Choisis a 240 px a l'est, ils naissaient au bord droit de l'ecran, sous les
          // yeux (le juge des Cravates de m2 l'a dit).
          if (horsChamp && Math.abs(place.x - j.x) < VW / 2 + 16 && Math.abs(place.y - j.y) < VH / 2 + 16) continue;
          if (Monde.ligneLibre(place.x, place.y, j.x, j.y)) return place;
        }
      }
    }
    return null;
  }

  /** LES ALLIES (`allies`, M13 — m98) : deux membres de chacun de ces gangs arrivent a tes cotes, a la
      course, de l'autre cote de la rue que ceux qui viennent te chercher (`placeDArrivee`, un demi-tour plus
      loin). Ils visent les hommes de la mission (`Entites`, l'etat `allie`) et ne te touchent jamais.
      ⚠️ Deja la (l'objectif d'avant les avait poses) : on ne double pas la troupe. Dedans (`placeDArrivee`
      rend null), personne ne nait — la rue n'a pas de pixel ou poser. */
  function poserLesAllies(m, o) {
    const deja = (B.mission.allies || []).filter(function (e) { return e.vivant && e.etat !== 'assomme'; });
    if (deja.length) return;
    const place = placeDArrivee(o.loin || 10, 8);
    if (!place) return;
    const j = B.joueur, dx = j.x - place.x, dy = j.y - place.y, norme = Math.hypot(dx, dy) || 1;
    B.mission.allies = [];
    let i = 0;
    for (const slug of o.allies) {
      const gang = B.defs.pietons.gangs.find(function (g) { return g.slug === slug; });
      const arch = gang && Entites.archetype(gang.pieton);
      if (!arch) continue;
      for (let k = 0; k < (o.allies_par || 2); k++, i++) {
        const ici = tuileLibre(place.x - dy / norme * (i - 2.5) * 18, place.y + dx / norme * (i - 2.5) * 18, 3);
        if (!ici) continue;
        const e = Entites.creerPieton(ici.x, ici.y, arch);
        // ⚠️ `metier` : ils ne sont pas la foule (le plafond de passants ne les compte pas), et `mission` :
        // ils ne s'oublient pas hors de la bulle.
        e.allie = true; e.metier = 'allie'; e.mission = m.slug; e.etat = 'allie'; e.courage = 1; e.cri = 90;
        e.rival = null;
        B.mission.allies.push(e);
      }
    }
    Entites.indexer();
  }

  /** Les allies rentrent chez eux : l'objectif ne les nomme plus, ou la mission est finie. Ils redeviennent
      des membres de leur gang comme les autres — et s'oublient hors de la bulle. */
  function relacherLesAllies() {
    if (!B.mission || !B.mission.allies) return;
    for (const e of B.mission.allies) {
      e.allie = false; e.metier = null; e.mission = null; e.rival = null;
      if (e.vivant && e.etat !== 'assomme' && e.etat !== 'attaque') { e.etat = 'flane'; e.vx = 0; e.vy = 0; }
    }
    B.mission.allies = null;
  }

  /** `enSilence` : l'intro va se dire. Ceux qui `arrivent` (`loin`) attendent la fin
      de la scène (`faireArriver`) : leur point de naissance est choisi tout de suite —
      la caméra de l'intro peut aller le voir (`cible`) —, eux naissent plus tard. */
  function poserLesCravates(m, o, enSilence) {
    const gang = B.defs.pietons.gangs.find(function (g) { return g.slug === o.groupe; });
    if (!gang) return;
    // ⚠️ `pieton` (29 sept. 2026, q13) : QUI on envoie, quand ce n'est pas un membre de rue du gang — les
    // matelots de Sven (`matelot`, un piéton de mission, fréquence 0). Le gang reste ce qu'il est.
    const arch = Entites.archetype(o.pieton || gang.pieton);
    const coins = o.coins || 1;
    const etape = B.partie.mission.etape, parCoin = tombesDe(m.slug, etape);
    // Une VAGUE de renforts (`majRenforts`) : ses hommes à elle, rien de ce qu'un essai raté aurait couché.
    const reste = o.vague ? o.n : o.n - dejaTombes(m.slug, etape);
    B.mission.kos = o.n - reste;
    if (reste <= 0) return;
    const arrivee = o.loin ? (o.vague ? placeDArrivee(o.loin) : B.mission.arrivee || placeDArrivee(o.loin)) : null;
    if (arrivee && enSilence) { B.mission.arrivee = arrivee; return; }
    // Le chef vient à toi (m5) — sauf si la fiche dit où il attend (`ou` : Kenny à la porte de chez Gus, c06).
    const centre = arrivee || (o.chef && !o.ou ? { x: B.joueur.x, y: B.joueur.y } : resoudre(o.ou, m) || { x: B.joueur.x, y: B.joueur.y });
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
        // ⚠️ POSÉS À UN ENDROIT (`ou`), ILS Y TIENNENT (Martin, 30 sept. 2026 : « les skateux s'en vont et ne
        // bloquent pas le pont »). Ils naissaient en flânant, sans poste : les trois de p02, posés au pont
        // pendant qu'on était au phare, à 254 tuiles, avaient fait 30 tuiles en 40 s. Un poste les ramène à
        // leur place (`POSTE_RAYON`, comme la Brume à son lampadaire), et la bagarre finie, ils y retournent.
        else if (o.ou) e.poste = { x: place.x, y: place.y };
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
          // Le chef de m5 : le baton et 160 de vie — sauf si la fiche dit autre chose (c06 : Kenny, le caid des
          // Mantes, se bat a mains nues ; `arme: ""`), comme pour ses hommes.
          e.chef = true; e.vie = e.vieMax = o.vie || 160; e.arme = o.arme !== undefined ? (o.arme || null) : 'batte';
          e.swaps = Object.assign({}, e.swaps, { c: '#101018' });
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

  /** LE CHAR D'UNE MISSION, A LA SAISON (Martin, 29 sept. 2026) : un deux-roues remise
      (`Vehicules.remise`) ne sort pas — l'hiver, la moto devient une MOTONEIGE (le fuyard file dans
      la neige, la moto de Sven attend au pont) ; sous la pluie, une berline. Le reste de l'annee, et
      tout ce qui n'est pas remise, reste ce que la mission demande. */
  function charDeSaison(slug) {
    const pourquoi = typeof Vehicules !== 'undefined' ? Vehicules.remise(slug) : null;
    if (pourquoi === 'hiver') return slug === 'moto' ? 'motoneige' : 'auto';
    return pourquoi === 'pluie' ? 'auto' : slug;
  }

  function poserLeFuyard(m, o, depuis) {
    // ⚠️ Le fuyard naît dans la ville, près de la porte quand on est dedans (m50 : Lulu le
    // voit filer depuis la cantine), et pas dans le char qu'on a garé devant elle.
    // `depuis` (un `relais`) : près du char qu'il vient de lâcher.
    const ici = depuis || ouEstLeJoueurEnVille();
    const rue = tuileDeRue(ici.x, ici.y, 10, sansChar) || tuileDeRue(ici.x, ici.y, 10);
    if (!rue) return;
    const angle = { '>': 0, '<': Math.PI, '^': -Math.PI / 2, 'v': Math.PI / 2 }[rue.sens];
    const slug = charDeSaison(o.vehicule || 'moto');
    const v = Vehicules.creer(slug, rue.x, rue.y, angle, { conducteur: 'trafic', etat: 'roule', poursuite: true, fuite: true, sens: rue.sens, mission: m.slug, fuyard: true });
    if (!v) return;
    v.vitesse = 1.5;
    B.mission.vehicule = v; B.mission.fuyard = v; B.mission.entites.push(v);
    // ⚠️ En moto OU en char : « EN MOTO » s'affichait aussi quand l'auto de m5 ou le taxi de m97 filaient.
    Hud.message(slug === 'moto' ? 'LE FUYARD FILE EN MOTO !' : slug === 'motoneige' ? 'LE FUYARD FILE EN MOTONEIGE !' : 'LE FUYARD FILE EN CHAR !', 150);
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
    // ⚠️ ON LUI A PRIS SON CHAR (Martin, 29 sept. 2026 : « j'ai volé le char du pyromane et après
    // quelques secondes j'ai perdu tout contrôle ») : c'est le JOUEUR qui conduit, on ne lui vide
    // pas le siège. Le fuyard, tiré dehors par le carjacking, file à pied avec la caisse.
    if (v.conducteur !== B.joueur) { v.conducteur = null; v.etat = v.etat === 'epave' ? 'epave' : 'stationne'; }
    v.fuite = false; v.poursuite = false;
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

  /** Une voie hors champ à 320-520 px du joueur, dans le sens de la voie (le patron de `Police.peuplerAutos`). */
  function rueHorsChamp() {
    const j = B.joueur, c = Monde.carte;
    for (let essai = 0; essai < 20; essai++) {
      const a = B.rng() * Math.PI * 2, d = 320 + B.rng() * 200;
      const tx = Math.floor((j.x + Math.cos(a) * d) / TT), ty = Math.floor((j.y + Math.sin(a) * d) / TT);
      if (tx < 1 || ty < 1 || tx >= c.w - 1 || ty >= c.h - 1) continue;
      const f = Monde.fleche(tx, ty);
      if (!CAP_DE_FLECHE[f] && CAP_DE_FLECHE[f] !== 0) continue;
      if (Entites.visibleAEcran(tx * TT + 8, ty * TT + 8, 40)) continue;
      return { x: tx * TT + 8, y: ty * TT + 8, sens: f };
    }
    return null;
  }

  /** `poursuite` (les chapitres) : des chars du gang, nés hors champ, qui te collent tant que l'objectif dure. */
  function poserLaPoursuite(m, o) {
    const pr = o.poursuite;
    B.mission.poursuivants = [];
    for (let k = 0; k < (pr.chars || 1); k++) {
      const rue = rueHorsChamp();
      if (!rue) continue;
      const v = Vehicules.creer(pr.vehicule || 'auto', rue.x, rue.y, CAP_DE_FLECHE[rue.sens],
                                { conducteur: 'poursuivant', etat: 'roule', surRails: true, poursuite: true, sens: rue.sens });
      if (!v) continue;
      v.gang = pr.groupe; v.mission = m.slug; v.vitesse = 2;
      B.mission.poursuivants.push(v);
    }
  }

  /** Le pilote d'un poursuivant : sur les rails de loin, droit sur toi de près (`Police.commandes`, sans équipage). */
  function commandesDuPoursuivant(v) {
    const j = B.joueur, cible = j.dansVehicule || j;
    const d = Math.hypot(cible.x - v.x, cible.y - v.y);
    const direct = d < 140 && Monde.ligneLibre(v.x, v.y, cible.x, cible.y);
    const coince = !v.surRails && (v.immobileT || 0) > 45;
    if (!direct || coince) {
      if (!v.surRails) { v.cible = null; v.sortie = null; v.immobileT = 0; }
      v.surRails = true;
      return 'rails';
    }
    v.surRails = false;
    let ecart = Math.atan2(cible.y - v.y, cible.x - v.x) - v.angle;
    while (ecart > Math.PI) ecart -= 2 * Math.PI;
    while (ecart < -Math.PI) ecart += 2 * Math.PI;
    return { gaz: Math.abs(ecart) > 1.6 ? 0 : 1, frein: Math.abs(ecart) > 1.6 && v.vitesse > 1 ? 1 : 0,
             direction: Math.max(-1, Math.min(1, ecart * 2)), freinMain: Math.abs(ecart) > 1.2 && v.vitesse > 2 };
  }

  /** L'objectif fait (ou la mission finie) : les poursuivants retournent au trafic. */
  function relacherLesPoursuivants() {
    ((B.mission && B.mission.poursuivants) || []).forEach(function (v) {
      if (v.etat !== 'epave' && v.conducteur === 'poursuivant') { v.conducteur = 'trafic'; v.poursuite = false; v.surRails = false; }
      // Plus à la mission : le trafic l'oublie quand il est loin, le garage le repeint comme un autre.
      if (v.conducteur !== B.joueur) { v.mission = null; v.gang = null; }
    });
    if (B.mission) B.mission.poursuivants = [];
  }

  /** `renforts` (les chapitres) : quand il ne reste qu'UN debout, la vague suivante arrive de loin. Rend true s'il en
      a posé une — l'objectif ne se juge pas dans la même image. */
  function majRenforts(m, o, p, cibles, tombes) {
    const r = o.renforts;
    if (!r || (B.mission.vagues || 0) >= r.vagues || !cibles.length || cibles.length - tombes > 1) return false;
    B.mission.vagues = (B.mission.vagues || 0) + 1;
    dansLaVille(function () { poserLesCravates(m, Object.assign({}, o, { n: r.n, chef: false, loin: o.loin || 14, vague: true }), false); });
    return true;
  }

  /** Le chef sort quand ses gars sont tombes : `tuer` avec `chef` se pose au moment venu. */
  function majObjectif() {
    const m = courante(), p = B.partie.mission, j = B.joueur;
    const o = m.objectifs && m.objectifs[p.etape];
    if (!o) return;
    // ⚠️ LE CHAR DE LA MISSION A SAUTE : c'est rate, QUEL QUE SOIT l'objectif.
    // Seuls `monter` et `livrer` le regardaient : le taxi de Marco explosait
    // pendant les courses, l'auto-patrouille de M4 pendant qu'on semait, et la
    // mission continuait sans char jusqu'a la livraison. Le fuyard de M2 n'en
    // est pas un (on le casse expres), ni un char deja livre (`mission: null`).
    const mv = B.mission.vehicule;
    if (mv && mv.etat === 'epave' && mv.mission === m.slug && !mv.fuyard && echecsDe(m).indexOf('vehicule_detruit') >= 0) {
      echouer('vehicule_detruit');
      return;
    }
    // ⚠️ M16 — les options qui TRAVERSENT tout objectif (`OPTIONS_OBJECTIFS`).
    // `chrono_s` : le chrono sur n'importe lequel (le défi l'avait, la mission
    // non). `debutT` est posé dans `avancer()` ; `* 60` convertit en images.
    if (o.chrono_s && B.t - p.debutT > o.chrono_s * 60) { echouer('chrono'); return; }
    // `sans_etoile` : échec `etoile` dès qu'on est vu (les missions discrètes).
    if (o.sans_etoile && B.recherche.etoiles > 0) { echouer('etoile'); return; }
    // `sans_arme` (29 sept. 2026, q06 : « coucher Denis à mains nues ») : une arme AU POING en territoire
    // de gang, c'est raté (échec `arme`). Hors de son territoire, on a le temps de la ranger — la ligne
    // d'objectif le dit (`ligneObjectif`).
    if (o.sans_arme && armeAuPoing(j) && Territoires.gangA(j.x, j.y)) { echouer('arme'); return; }
    switch (o.type) {
      case 'acte': {
        // Instantané — sauf un acte `sur_place` (la nuit du Trappeur) : le saut, puis l'objectif suivant.
        if (o.sur_place && !B.mission.sautEnCours) {
          B.mission.sautEnCours = true;
          SurPlace.sauter({ sur_place: o.sur_place }, function () { if (B.mission) B.mission.sautEnCours = false; avancer(); });
        } else if (!o.sur_place) avancer();
        return;
      }
      case 'tenir': {
        const l = resoudre(o.lieu, m), dedans = l && dist2(j.x, j.y, l.x, l.y) < (o.rayon * TT) * (o.rayon * TT);
        if (!dedans) {
          if (o.strict && B.mission.tenu > 0) { echouer('hors_zone'); return; }
          B.mission.tenu = 0; B.mission.attend = 'REVIENS — ' + texteDObjectif(o);
          return;
        }
        B.mission.attend = null;
        if (o.groupe) {
          const cibles = B.mission.entites.filter(function (e) { return e.type === 'pieton' && e.cible && e.etape === p.etape; });
          majRenforts(m, o, p, cibles, cibles.filter(function (e) { return !e.vivant || e.etat === 'assomme'; }).length);
        }
        if (++B.mission.tenu >= (o.secondes || 60) * 60) avancer();
        return;
      }
      case 'aller': {
        if (o.nuit && !Monde.estNuit()) { B.mission.attend = 'ATTENDS LA NUIT'; return; }
        B.mission.attend = null;
        const l = lieu(o.lieu);
        if (l && dist2(j.x, j.y, l.x, l.y) < (o.rayon * TT) * (o.rayon * TT)) {
          // `tenue` (f10) : arrivé, mais pas dans le bon linge — la ligne dit quoi enfiler.
          if (tenueManque(o)) { B.mission.attend = 'ENFILE : ' + tenueDef(o.tenue).nom.toUpperCase(); return; }
          avancer();
        }
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
        // `repeint` (x02, le casse) : le char ne se livre qu'une fois REPEINT (`Missions.repeindre` le marque) — la ligne
        // d'objectif le dit tant qu'il ne l'est pas.
        if (o.repeint && !v.repeint) { B.mission.attend = 'FAIS-LE REPEINDRE — ' + texteDObjectif(o); return; }
        if (o.repeint) B.mission.attend = null;
        const l = lieuDeLivraison(o.lieu);
        if (j.dansVehicule === v && l && dist2(v.x, v.y, l.x, l.y) < (o.rayon * TT) * (o.rayon * TT) && Math.abs(v.vitesse) < 0.4) {
          B.mission.sansBosse = o.sans_degats && v.chocs === p.chocs && v.vie === v.vieMax;
          Vehicules.descendre(j, true);
          v.mission = null; v.vole = false; v.conducteur = null; v.etat = 'stationne';
          B.mission.entites = B.mission.entites.filter(function (e) { return e !== v; });
          // `rentre` (i04) : on le rentre — Léo le roule dans son hangar. Il n'est plus dans la rue.
          if (o.rentre) Entites.retirer(v);
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
        if (majRenforts(m, o, p, cibles, tombes)) return;
        const total = o.n + (B.mission.vagues || 0) * (o.renforts ? o.renforts.n : 0);
        B.mission.kos = Math.min(total, avant + tombes);
        if (cibles.length && tombes >= Math.min(total - avant, cibles.length)) {
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
          // Au volant de SON char (on le lui a pris en marche), on l'a rattrapé : il est dehors.
          if (j.dansVehicule === v || v.etat === 'epave' || (d < 40 && Math.abs(v.vitesse) < 0.6) || v.vie < v.vieMax * 0.5) {
            // `relais` (les chapitres) : rattrapé, il saute dans un autre char tout près — N fois avant de tomber.
            if ((B.mission.relais || 0) < (o.relais || 0)) {
              B.mission.relais = (B.mission.relais || 0) + 1;
              if (v.conducteur !== j) { v.conducteur = null; v.etat = v.etat === 'epave' ? 'epave' : 'stationne'; }
              v.fuite = false; v.poursuite = false;
              Hud.message('IL SAUTE DANS UN AUTRE CHAR !', 150);
              dansLaVille(function () { poserLeFuyard(m, o, { x: v.x, y: v.y }); });
            } else faireTomberLeFuyard();
          }
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
        const d = donneur(Chapitres.donneurDe(m));
        if (d && dist2(j.x, j.y, d.x, d.y) < RAYON_PARLER * RAYON_PARLER) avancer();
        return;
      }
      case 'survivre':
        if (B.t - p.debutT > (o.secondes || 30) * 60) avancer();
        return;
      case 'attendre': {
        // `attendre` (i04, « laisse-le refroidir une journée ») : `heures` de JEU depuis le début de l'étape — dormir
        // les fait passer, comme vivre. Le départ est dans la partie (`p.depuis`) : il survit à une partie rouverte.
        if (p.depuis === undefined || p.depuis === null) p.depuis = heuresDeJeu();
        const reste = (o.heures || 24) - (heuresDeJeu() - p.depuis);
        if (reste <= 0) { B.mission.attend = null; p.depuis = null; avancer(); return; }
        B.mission.attend = texteDObjectif(o) + ' — ENCORE ' + Math.ceil(reste) + ' H';
        return;
      }
      case 'course': {
        const c = B.mission.course;
        if (!c || !c.points.length) { avancer(); return; }
        if (o.a_pied && j.dansVehicule) { B.mission.attend = texteDObjectif(o) + ' — À PIED, DESCENDS'; return; }
        // `vehicule` (i07) : la course se court DANS ce véhicule — une chaloupe, pas à la nage.
        if (o.vehicule && !(j.dansVehicule && j.dansVehicule.slug === o.vehicule)) {
          B.mission.attend = texteDObjectif(o) + ' — ' + (o.vehicule === 'bateau' ? 'EN CHALOUPE' : 'AU VOLANT');
          if (c.rival && Regate.arrive(c.rival)) { echouer('battu'); return; }
          return;
        }
        B.mission.attend = null;
        const pt = c.points[c.i], ici = j.dansVehicule || j, r = (o.rayon || 3) * TT;
        if (pt && dist2(ici.x, ici.y, pt.x, pt.y) < r * r) {
          c.i++;
          Son.SFX.ramasse();
          if (c.i < c.points.length) Hud.message('POINT ' + c.i + ' / ' + c.points.length, 90);
        }
        // Le rival est arrivé avant toi : c'est raté.
        if (c.i < c.points.length && c.rival && Regate.arrive(c.rival)) { echouer('battu'); return; }
        if (c.i >= c.points.length) {
          // Gagné : le rival se laisse dériver, puis rentre (ce n'est plus un char de mission qu'on surveille).
          if (c.rival) c.rival.regate.battu = true;
          avancer();
        }
        return;
      }
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
        // Le feu que la mission a allumé (`poser`) : l'objectif tombe quand le jet l'a
        // éteint. ⚠️ Avant le 28 sept. 2026, ce cas attendait qu'AUCUN feu de l'heure ne
        // brûle — vrai presque toujours : l'objectif passait dans la même image. Pas de
        // mur à brûler près de `ou` : il passe aussi, plutôt que de bloquer la mission.
        const fe = B.mission.feu;
        if (!fe || fe.eteint) avancer();
        return;
      }
      case 'payer': {
        if (Missions.payer(o.montant, o.raison || '')) avancer();
        return;
      }
      case 'embarquer': {
        // M13 : à bord — à pied ou au volant — quand il QUITTE l'escale. C'est
        // `Traversier.embarquer` qui met sur le pont ce qui s'y trouve à l'heure du départ ;
        // manquer le départ, c'est attendre le suivant. Une ville sans traversier ne
        // bloque pas la mission.
        // `bateau: navette` (un char sur l'île) : la navette de l'île, pas le traversier.
        const l = quaiDuBateau(o.escale, o.bateau), bt = bateauNomme(o.bateau);
        if (!l || !bt) { avancer(); return; }
        const s = bt.etatA(B.partie.heure);
        const aBord = bt.aBord(j) || (j.dansVehicule && bt.aBord(j.dansVehicule));
        if (aBord && s.phase === 'traverse' && s.de === l.escale.k) avancer();
        return;
      }
      case 'acheter': {
        // Un article a un comptoir : la mission avance quand on l'a en poche
        // (`B.partie.objets` ou `armes`). Le menu du comptoir l'achète déjà.
        const enPoche = B.partie.objets[o.article] || B.partie.armes[o.article];
        // ⚠️ Déjà en poche quand l'étape a COMMENCÉ (`avancer` le note ; p01 : le bâton que m2
        // donne) : le comptoir affiche « DÉJÀ À TOI » et ne le revend pas. L'étape passe, mais le
        // jeu le DIT — avant, elle filait sans un mot et l'objectif mentait.
        if (enPoche) {
          const deja = B.mission.acheterDeja === B.partie.mission.etape;
          avancer();
          if (deja) Hud.message('DÉJÀ DANS TES POCHES', 150);
        }
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
      case 'obtenir': {
        // ⚠️ L'INFILTRATION : un objet dans le sac, d'ou qu'il vienne — ramasse a son lieu, vole dans la
        // poche d'un garde, tombe d'un garde assomme (`Infiltration`). On ne regarde que le sac.
        if (B.partie.objets && B.partie.objets[o.objet] > 0) avancer();
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

  /** Une arme AU POING (pas les poings, pas le poing américain, pas au volant) : ce que `sans_arme` refuse. */
  function armeAuPoing(j) {
    return !!(j && !j.dansVehicule && j.arme && j.arme !== 'poings' && j.arme !== 'poing_americain');
  }

  /** Ce qu'une fin accorde, en plus de l'argent : le `donne` d'une mission — ou, depuis les CHAPITRES
      (30 sept. 2026), celui d'un objectif, accordé quand il est fait (chaque acte donne ce que sa mission
      d'origine donnait). */
  function accorder(d) {
    const p = B.partie;
    if (d.arme && !p.armes[d.arme]) { const a = Combat.armeDef(d.arme); p.armes[d.arme] = { mun: a && a.chargeur ? a.chargeur : null }; }
    if (d.rabais) Object.keys(d.rabais).forEach(function (k) { p.rabais[k] = d.rabais[k]; });
    if (d.sergent_ami) p.sergentAmi = true;
    if (d.propriete && !p.proprietes[d.propriete]) p.proprietes[d.propriete] = { jour: p.jour, caisse: 0 };
    if (d.faubourg_libere) p.faubourgLibere = true;
    // ⚠️ `libere` : un district de plus (m98 comptera la liste). `faubourg_libere`
    // alimente la MEME liste, pour qu'il n'y ait qu'une verite.
    if (d.libere && p.libere.indexOf(d.libere) < 0) p.libere.push(d.libere);
    // ⚠️ LE GANG PERD SON QUARTIER, ET CE QU'IL AVAIT PRIS AILLEURS (29 sept. 2026) : ses coins pris a la
    // frontiere reviennent a leurs gangs (`Territoires.liberer`) — il est hors jeu, il ne les defendrait plus.
    if (d.libere && typeof Territoires !== 'undefined') Territoires.liberer(d.libere);
    if (d.faubourg_libere && p.libere.indexOf('faubourg') < 0) p.libere.push('faubourg');
    // ⚠️ `calme` (M16) : un gang de plus qui oublie son hostilite (la seule
    // facon de marcher dans La Shop, s05 — et Les Erables, e04). Comme `libere`,
    // une liste ordonnee dans la partie.
    if (d.calme && p.calmes.indexOf(d.calme) < 0) p.calmes.push(d.calme);
    // ⚠️ `dette: -n` et `casier: -n` (M16) : des cles NEGATIVES, une facon de
    // dire « la fin t'enleve ce poids ». Bornees a zero, jamais sous.
    if (typeof d.dette === 'number') p.dette = Math.max(0, p.dette + d.dette);
    if (typeof d.casier === 'number') p.casier = Math.max(0, p.casier + d.casier);
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
    // ⚠️ `technique` : ce que le donneur t'APPREND en paiement (le vieux maitre des Mantes, c07) — comme une lecon
    // reussie au DOJO DION (`dojo.js`), sans la payer. Deja sue, il n'y a rien de plus a apprendre.
    if (d.technique && p.techniques && !p.techniques[d.technique] && Techniques.def(d.technique)) {
      p.techniques[d.technique] = true;
      if (p.coursPayes) delete p.coursPayes[d.technique];
      Hud.message('TU SAIS ' + Techniques.def(d.technique).nom.toUpperCase() + ' !', 180);
    }
    // ⚠️ `a_vendre` (M16) : une propriete qu'aucun comptoir ne vendait se met en vente
    // (l'hotel apres q07) — `Missions.aVendre` la lit, la sauvegarde la garde.
    if (d.a_vendre && p.enVente.indexOf(d.a_vendre) < 0) p.enVente.push(d.a_vendre);
    // ⚠️ `boss` (M13, m98 _Le Boss_) : la ville change de couleur — les gangs reviennent a tes couleurs et te
    // saluent, les passants aussi, plus de rixes aux frontieres, la carte a l'or des Bandini (`Entites`,
    // `Hud`, `B.defs.boss`). Une fois boss, on le reste : la sauvegarde le garde.
    if (d.boss && !p.boss) p.boss = { jour: p.jour };
  }

  function reussir() {
    const m = courante();
    if (!m) return;
    const p = B.partie;
    // ⚠️ LA BRANCHE CHOISIE (un choix dans un dialogue) : gardée pour de bon, et c'est elle qui paie — sa récompense,
    // son `donne` par-dessus celui de la mission, sa fermeture (`branches`).
    const branche = brancheDe(m);
    if (branche && questionDe(m)) p.choix[m.slug] = branche;
    const b = ((m.branches || {})[branche]) || {};
    const d = donneDe(m), recompense = b.recompense !== undefined ? b.recompense : m.recompense, ferme = b.ferme || m.ferme;
    const vehicule = B.mission ? B.mission.vehicule : null;
    nettoyer(false);
    if (p.tombes) delete p.tombes[m.slug];
    Chapitres.noterDuree(m);
    p.missionsFaites[m.slug] = p.jour;
    Chapitres.reussi(m);
    p.mission = null;
    p.appelT = null;
    const bonus = B.mission && B.mission.sansBosse ? Math.round(recompense * 0.5) : 0;
    const prime = recompense + bonus;
    Missions.encaisser(prime, m.titre.toUpperCase(), true);
    accorder(d);
    // ⚠️ `ferme` (M16) : une mission qui en FERME une autre. Un choix est un
    // choix parce qu'il coute : on ecrit la fermeture ICI, au moment de la
    // recompense, et la mission fermee disparait de partout des la prochaine
    // fois qu'on regarde le telephone ou le carnet.
    // Une liste aussi (x04 ferme la dernière coupe de Sal ET les préparatifs qu'on n'a plus à faire).
    [].concat(ferme || []).forEach(function (f) { if (p.fermees.indexOf(f) < 0) p.fermees.push(f); });
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
    // Un CHAPITRE : le menu REPRENDRE L'ACTE attendra la fin de l'hôpital ou du poste (`Chapitres.majReprise`).
    Chapitres.retenir(m);
    retenirLesTombes(m);
    nettoyer(true);
    // ⚠️ Ce que ses objectifs avaient mis dans le sac (le dossier, le code de la chambre forte) retombe :
    // on l'a laisse en fuyant, et la mission se refait du debut (`Infiltration.rendre`).
    if (typeof Infiltration !== 'undefined') Infiltration.rendre(m);
    B.partie.mission = null;
    B.mission = null;
    // ⚠️ UNE PETITE JOB (`Jobs`) : le passant n'a pas ton numéro. Il ne te dit l'échec que s'il est LÀ ; loin,
    // un simple « JOB RATÉE » au HUD (Martin, 1er oct. 2026).
    const job = !!m.passant;
    Hud.message((job ? 'JOB RATÉE — ' : 'MISSION RATÉE — ') + m.titre.toUpperCase(), 200);
    noter((job ? 'JOB RATÉE : ' : 'MISSION RATÉE : ') + m.titre, true);
    Son.SFX.erreur();
    B.partie.stats.echecs = (B.partie.stats.echecs || 0) + 1;
    if (!job || present(m.donneur)) dire(m, 'echec', null);
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
    relacherLesAllies();
    relacherLesPoursuivants();
    // Le feu d'une mission s'en va avec elle — éteint ou non, il n'est plus le sien.
    if (B.mission.feu) { Incendies.oublierLeFeuDeMission(); B.mission.feu = null; }
    for (const e of B.mission.entites) {
      if (e.type === 'vehicule') {
        // Celui qu'on filait repart comme un autre, qu'on l'ait mené au bout ou
        // qu'il nous ait vus : il n'est jamais escamoté sous nos yeux.
        if (e.suivi && B.joueur.dansVehicule !== e) { e.suivi = false; e.attendLeJoueur = false; e.destination = null; e.mission = null; }
        // Le char du fuyard qu'on lui a volé : un char volé comme un autre, qui reste sous le joueur.
        else if (e.fuyard && B.joueur.dansVehicule === e) { e.fuyard = false; e.fuite = false; e.poursuite = false; e.mission = null; }
        else if (tout || e.fuyard || e.escorte) { if (B.joueur.dansVehicule === e) Vehicules.descendre(B.joueur, true); Entites.retirer(e); }
        else { e.mission = null; }
      } else if (e.type === 'pieton') {
        e.cible = false; e.chef = false;
        // ⚠️ UN PERSONNAGE qu'une escorte a pose (le vieux maitre de c08, qui ne se tient pas en ville) ne se sauve
        // pas avec les figurants : la mission finie, il reste la ou elle l'a mene, et la fin se dit DEVANT lui.
        if (e.personnage) { e.mission = null; e.suit = null; e.piste = null; e.intouchable = true; e.etat = 'fige'; e.vx = 0; e.vy = 0; }
        else if (e.vivant && e.etat !== 'assomme') { e.etat = 'fuit'; e.minuterie = 300; }
      }
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

  /** Les échecs d'une mission. ⚠️ Le paquet ne porte pas celui qui vaut le défaut (`missions.DEFAUTS_DE_MISSION`,
      `PAR_DEFAUT_AU_NAVIGATEUR`) : mort ou arrêté, comme en m1. */
  function echecsDe(m) { return (m && m.echec) || ['mort', 'arrete']; }

  function evenement(nom) {
    if (AU_CARNET[nom]) noter(AU_CARNET[nom], false);
    const m = courante();
    if (!m) return;
    if (echecsDe(m).indexOf(nom) >= 0) echouer(nom);
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
    // UNE COURSE AUX FANIONS (`course:<cle>`, la course des Friches en 4 roues) : a son depart, lu par Python
    // sur la ville finie (`B.defs[cle].course.depart`).
    else if (d.ou.indexOf('course:') === 0) {
      const c = B.defs[d.ou.slice(7)] && B.defs[d.ou.slice(7)].course;
      if (c) l = { x: c.depart[0] * TT + 8, y: c.depart[1] * TT + 8 };
    }
    // LE DERBY : au bord sud de son arene (`derby.arene`, lue par Python sur la ville finie).
    else if (d.ou === 'derby') {
      const a = B.defs.derby && B.defs.derby.arene;
      if (a) l = { x: a.panneau.x * TT + 8, y: a.panneau.y * TT + 8 };
    }
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
      s'il vient de s'ouvrir. ⚠️ La triche LANCER UN DÉFI passe aussi par ici
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
      // Le derby : au bord de son arene ; une course aux fanions (`course:<cle>`) : a son depart.
      if (!d.debloque || !d.ou || (d.ou.indexOf('porte:') !== 0 && d.ou !== 'derby' && d.ou.indexOf('course:') !== 0)) continue;
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
    // ⚠️ UNE ÉPREUVE DANS LA RUE (`Rue`) se joue à pied, sans char à trouver : elle
    // pose celui qu'on file ou celui qui cogne, et part tout de suite.
    // ⚠️ LE SOIR SEULEMENT (`soir` : le derby, le hockey de ruelle) : ca se DIT, et rien ne part.
    if (d.soir && ['crepuscule', 'nuit'].indexOf(Monde.periode()) < 0) {
      B.defi = null;
      Hud.message('ÇA SE JOUE LE SOIR — REVIENS À LA BRUNANTE', 150); Son.SFX.erreur();
      return;
    }
    // ⚠️ L'HIVER SEULEMENT (`hiver`, la course de motoneige) : la saison, et la neige de M12.
    if (d.hiver && !Missions.hiverDeMotoneige()) {
      B.defi = null;
      Hud.message('ÇA SE JOUE L\'HIVER, DANS LA NEIGE', 150); Son.SFX.erreur();
      return;
    }
    // ⚠️ PAS L'HIVER (`hors_hiver`, le derby de demolition a cote de la foire cadenassee) : ca se dit, rien ne part.
    // La triche qui ouvre la foire (`triche('foire')`) ouvre aussi son derby.
    if (d.hors_hiver && typeof Saisons !== 'undefined' && Saisons.enHiver() && !triche('foire')) {
      B.defi = null;
      Hud.message('ÇA REPREND AU PRINTEMPS, QUAND LA FOIRE ROUVRE', 150); Son.SFX.erreur();
      return;
    }
    // ⚠️ ET L'INVERSE : un defi a moto (Le Grand Saut) ne se joue pas l'hiver — la moto est remisee
    // (`Vehicules.remise`, docs/jalons/pas-de-moto-ni-de-velo-l-hiver-pas-de-moto-sous-la-pluie.md).
    if (d.vehicule && Vehicules.remise(d.vehicule) === 'hiver') {
      B.defi = null;
      Hud.message('LA MOTO EST REMISÉE — REVIENS AU PRINTEMPS', 150); Son.SFX.erreur();
      return;
    }
    if (d.rue) {
      if (!Rue.commencer(d)) { B.defi = null; Hud.message('PAS DE PLACE ICI POUR CE DÉFI', 150); Son.SFX.erreur(); return; }
      partir(d, null);
      return;
    }
    if (d.conduite && !Conduite.commencer(d)) {
      B.defi = null;
      Hud.message('PAS DE PLACE ICI POUR CE DÉFI', 150); Son.SFX.erreur();
      return;
    }
    // Une epreuve qui PRETE son char (le bazou du derby) : on y monte tout de suite, a sa place.
    if (d.conduite && B.conduite && B.conduite.monter && !j.dansVehicule) {
      j.x = B.conduite.monter.x; j.y = B.conduite.monter.y;
      Vehicules.monter(j, B.conduite.monter);
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
    if (d.rue) {
      f.t++;
      if (d.chrono_s && f.t > d.chrono_s * 60) { finirDefi(false, 'TEMPS ÉCOULÉ'); return; }
      const issue = Rue.maj(d);
      if (issue) finirDefi(issue.gagne, issue.raison);
      return;
    }
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
      triche LANCER UN DÉFI (`Hud.menuSautDefis`) qui l'abandonne pour en
      proposer un autre — pas un echec du joueur. */
  function abandonnerDefi() {
    rendreLaCarabine(B.defi);
    Adresse.fermer();
    Conduite.fermer();
    Rue.fermer();
    B.defi = null;
  }

  function finirDefi(reussi, raison) {
    const f = B.defi, d = defis().find(function (q) { return q.slug === f.slug; });
    rendreLaCarabine(f);
    Adresse.fermer();
    Conduite.fermer();
    Rue.fermer();
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

  /** Ce que la fleche vise DANS un bloc : le lieu d'un `aller`, le terminal d'un `pirater`, l'objet d'un
      `obtenir` (par terre, ou le garde qui l'a dans la poche) — seulement ce qui est de CE bloc. Null
      sinon : la fleche vise la sortie. */
  function cibleDansLeBloc(m, p) {
    const o = m.objectifs && p.mission && m.objectifs[p.mission.etape];
    if (!o) return null;
    const nomme = o.lieu || o.ou;
    if (nomme && blocDuLieu(nomme) !== B.bloc.slug) return null;
    let l = null;
    if (o.type === 'aller' || o.type === 'pirater') l = lieu(nomme);
    else if (o.type === 'obtenir') {
      l = B.entites.find(function (e) { return e.type === 'ramassage' && e.objetDeMission === o.objet; })
        || B.entites.find(function (e) { return e.porteObjet === o.objet && e.vivant; })
        || (nomme ? lieu(nomme) : null);
    }
    return l ? { x: l.x, y: l.y, nom: l.nom || texteDObjectif(o), couleur: '#e8b33c' } : null;
  }

  /** La cible du moment : un objectif, un appel a honorer, un defi en cours. */
  function cible() {
    const m = courante(), p = B.partie, j = B.joueur;
    if (!j) return null;
    // ⚠️ DANS UN BLOC DE CARTE, les lieux de la ville n'ont pas de pixel ici : la fleche
    // vise la sortie, vers la ville (`Blocs`) — c'est par la que passe tout le reste. Sauf ce que la
    // mission vient faire DANS ce bloc (la villa : son lieu, son terminal, ce qu'on vient prendre).
    // ⚠️ Et dans un bloc a ETAGES (la villa), ce qui est a un autre etage se vise par son escalier.
    if (B.bloc) {
      const c = (m && cibleDansLeBloc(m, p)) || Blocs.cibleDeSortie();
      const esc = c && Infiltration.escalierVers(j, c.x, c.y);
      return esc ? { x: esc.x, y: esc.y, nom: esc.nom, couleur: c.couleur } : c;
    }
    if (B.defi) {
      const d = defis().find(function (q) { return q.slug === B.defi.slug; });
      const l = d.rue ? Rue.cible(d) : d.conduite ? Conduite.cible(d) : d.circuit ? repereDeCircuit(B.defi) : d.lieu ? lieu(d.lieu) : null;
      return l ? { x: l.x, y: l.y, nom: l.nom, couleur: '#7fc4ff' } : null;
    }
    if (m) {
      // ⚠️ Pas encore arrivee (voir `objectif`) : le GPS ne pointe rien plutot que de
      // tomber. Le HUD appelle ceci a chaque image.
      const o = m.objectifs && m.objectifs[p.mission.etape];
      if (!o) return null;
      let l = null;
      if (o.type === 'aller') l = lieu(o.lieu);
      else if (o.type === 'embarquer') l = quaiDuBateau(o.escale, o.bateau);
      else if (o.type === 'livrer') l = lieuDeLivraison(o.lieu);
      else if (o.type === 'monter') l = B.mission && B.mission.vehicule ? B.mission.vehicule : null;
      else if (o.type === 'retourner') l = ouTrouver(Chapitres.donneurDe(m));
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
      else if (o.type === 'tenir') l = resoudre(o.lieu, m);
      else if (o.type === 'course') l = B.mission && B.mission.course ? B.mission.course.points[B.mission.course.i] || null : null;
      else if (o.type === 'proteger') {
        // Lui d'abord, tant qu'on ne l'a pas rejoint ; puis où on l'emmène.
        const c = B.mission ? B.mission.protege : null;
        l = (c && !c.suit) ? c : ((o.lieu && lieu(o.lieu)) || c);
      }
      else if (o.type === 'pickpocket') l = B.mission ? B.mission.entites.find(function (e) { return e.pickpocket && e.vivant; }) : null;
      else if (o.type === 'detruire') l = B.mission && B.mission.chars ? B.mission.chars[p.mission.etape] : null;
      else if (o.type === 'sauter') l = resoudre(o.ou, m);
      else if (o.type === 'acheter') l = resoudre(o.ou, m);
      else if (o.type === 'eteindre') { const fe = B.mission && B.mission.feu; l = fe && !fe.eteint ? Incendies.position(fe) : null; }
      // ⚠️ `pirater` : le terminal, sur le POSTE quand il est sur un mouillage (le quai, là où
      // `piratageSousLaMain` l'ouvre). Sans ce cas, un terminal loin du donneur (l'île de m53,
      // m54) n'avait ni flèche ni repère.
      else if (o.type === 'pirater') { const t = resoudre(o.ou, m); l = t && t.mouillage ? t.mouillage.poste : t; }
      // ⚠️ Un lieu de BLOC (la villa) n'a pas de pixel en ville : on vise son passage.
      if (!l) { const bloc = blocDuLieu(o.lieu || o.ou || ''); if (bloc) l = passageDuBloc(bloc); }
      return l ? { x: l.x, y: l.y, nom: (l.nom || texteDObjectif(o)), couleur: '#e8b33c' } : null;
    }
    // Un appel recu : le donneur a aller voir.
    const attendue = disponibles().find(function (q) { return p.appels[q.slug]; }) || disponibles().find(function (q) { return !q.prerequis.length; });
    if (attendue) { const qui = Chapitres.donneurDe(attendue), l = ouTrouver(qui), perso = personnage(qui); return l ? { x: l.x, y: l.y, nom: perso.nom, couleur: '#8ad26a' } : null; }
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
    if (B.frenesie && typeof Frenesies !== 'undefined') return Frenesies.ligne();
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
      if (d.rue) return d.titre.toUpperCase() + chrono + ' ' + Rue.compte(d);
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
    const o = m.objectifs && m.objectifs[B.partie.mission.etape];
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
    if (o.type === 'course' && B.mission && B.mission.course) compte = ' ' + B.mission.course.i + '/' + B.mission.course.points.length;
    if (o.type === 'suivre' && B.mission && B.mission.suivi) compte = filature(B.mission);
    if (o.type === 'tenir' && B.mission) compte = ' ' + Math.max(0, Math.ceil(((o.secondes || 60) * 60 - (B.mission.tenu || 0)) / 60)) + ' S';
    if (o.type === 'parler' && tenueManque(o) && tenueDef(o.tenue)) compte = ' — ENFILE : ' + tenueDef(o.tenue).nom.toUpperCase();
    // `sans_arme` : tant qu'on tient une arme, la ligne le dit AVANT qu'on entre chez eux.
    if (o.sans_arme && armeAuPoing(B.joueur)) compte += ' — RANGE TON ARME';
    // ⚠️ `chrono_s` sur un objectif (M16) : le temps qui reste, comme au défi. Il
    // tombait en silence (q10 : « la moto au phare en une minute », sans montre).
    if (o.chrono_s && typeof B.partie.mission.debutT === 'number') {
      const reste = Math.max(0, o.chrono_s * 60 - (B.t - B.partie.mission.debutT));
      compte += ' ' + Math.floor(reste / 3600) + ':' + ('0' + Math.floor(reste % 3600 / 60)).slice(-2);
    }
    return texteDObjectif(o) + compte;
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
    // L'ECOLE LA MANTE ROUVERTE (`mantes.REPRISE`) : dans sa salle, le maitre donne son cours — il compte, deux
    // secondes sur quatre, quand il n'a rien pour toi.
    const r = B.defs.mantes && B.defs.mantes.reprise;
    const cours = !!(r && B.interieur && faite(r.apres)) && B.t % 240 < 120;
    for (const e of B.entites) {
      if (!e.personnage || !e.vivant) continue;
      if (e.job) { Jobs.bulle(e); continue; }      // le passant d'une petite job : sa bulle est à `Jobs`
      const dispo = disponibleDe(e.personnage);
      // ⚠️ SA BULLE S'ALLUME, SON TEXTE SE DEMANDE. Il est visible a plusieurs secondes
      // de marche : c'est la marge qu'il faut pour que la porte n'attende jamais.
      if (dispo && !dispo.dialogue) charger(dispo.slug);
      const attend = (m && Chapitres.donneurDe(m) === e.personnage && o && o.type === 'retourner') || !!dispo;
      const p = attend ? personnage(e.personnage) : null;
      const compte = !p && cours && personnage(e.personnage).ou === 'point:' + r.point;
      Entites.bulle(e, p ? p.heler : (compte ? r.bulle : ''));
    }
  }

  function maj() {
    if (!B.joueur || !B.partie) return;
    // ⚠️ UNE PARTIE REPRISE EN PLEINE MISSION n'a pas son texte : il n'est plus dans le
    // paquet, et elle a ete sauvegardee bien apres son intro. Tout ce qui suit le lit —
    // les repliques `pendant`, la fin, l'echec — alors on le demande et on laisse passer
    // l'image. La ville, elle, continue de tourner.
    const reprise = courante();
    if (reprise && !reprise.dialogue) { charger(reprise.slug); return; }
    // Le chronomètre compte AUSSI les répliques (et un appel reçu au volant) : ni la pause, ni un menu, ni un
    // fondu n'appellent `maj`.
    Chapitres.compter();
    majCinema();
    if (B.cinema) return;
    jouerLaFin();
    if (B.cinema) return;
    jouerLeGenerique();
    if (Chapitres.majReprise()) return;
    majBulles();
    majRetours();
    majSaisonniers();
    majTelephone();
    Jobs.maj();
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
      // La frontiere (`frontiere`) se compte meme dans une piece : c'est sa porte qui compte.
      SurPlace.maj(courante());
      if (!B.partie.mission) return;             // la frontiere vient de la faire rater
      if (!B.interieur) {
        majObjectif();
      }
    }
    majDefi();
    majDeblocages(false);
  }

  return { texteDObjectif, exigeTenu, tenu, porteLaTenue, faite, disponibles, disponibleDe, estParti, personnage, personnageSousLaMain, personnageDuPoint, pieceDuPoint,
           donneur, creerDonneurs, majSaisonniers, absentLHiver, poserDonneur, creerDonneursDedans, creerPanneaux, panneauSousLaMain,
           parler, dire, suivante, finir, commencer, demarrer, avancer, objectif, courante, reussir, echouer, evenement,
           mission, accorder, ouEstLeJoueurEnVille, commandesDuPoursuivant, arriverApres,
           ouverture, passerOuverture, fichiersDeLOuverture, direLignes, majCinema, resoudre,
           lieuDuPersonnage, pieceDessous, ouTrouver, present, calme, jouerOuDire,
           reinitialiser, noter, rencontrer, CARNET_MAX, init, charger,
           proposerDefi, commencerDefi, finirDefi, abandonnerDefi, actionDeDefi, defisDeFoire, comptoirDeDefi, defiDuComptoir, canardAuCrochet,
           appareilsDe, jouableAvec, defiOuvert, defisOuverts, defiNeuf, ouvrirDefi, majDeblocages, planterLesPanneauxOuverts, APPAREIL_DU_CATALOGUE,
           cible, ligneObjectif, lieu, lieuDeLivraison, passageDuBloc, blocDuLieu, ruellePres, tuileLibre, tuileDeRue, slugDeVoix, cibleDuParler, maj,
           piratageSousLaMain, commencerPiratage, estCourse, dessinerCheminCourse, lampesDeCourse,
           questionDe, brancheDe, donneDe, choisir, CHOIX_SOURD };
})();
