/* Bandini — la boucle et la machine d'etats. Seul fichier qui demarre quelque
   chose ; sous le banc d'essai, il attend que `document` existe. */

const Jeu = (function () {
  'use strict';

  const PAS = 1000 / 60;
  //: La suite de touches qui reveille le menu DEBUG (voir `Entree.surSecret`,
  //: `ouvrirMenuDebug`) : « RIGOLO », en lettres qu'AUCUNE action
  //: d'`Entree.MAP_TOUCHES` n'utilise (a verifier avant d'y toucher : une
  //: lettre libre aujourd'hui peut se faire lier demain, comme KeyT l'a ete a
  //: `verrouiller`). ⚠️ Pas les fleches ni B/A (le Konami classique) : KeyB est
  //: ANNULER, et le taper pendant que PAUSE est ouvert fermait le menu pause
  //: (`reprendre()` suit, `jeu.js:690`) juste avant que le dernier appui
  //: n'ouvre DEBUG par-dessus — la suite paraissait ignorer le garde-fou de
  //: `ouvrirMenuDebug` alors qu'elle avait change l'etat sous ses pieds. Une
  //: suite hors de `MAP_TOUCHES` ne fait RIEN d'autre en la tapant, dans aucun
  //: ecran — c'est le seul moyen de garder le garde-fou fiable.
  const SEQUENCE_DEBUG = ['KeyR', 'KeyI', 'KeyG', 'KeyO', 'KeyL', 'KeyO'];
  //: La suite d'ACTIONS qui reveille AUSSI le menu DEBUG, la ou un clavier
  //: n'existe pas — le Konami directionnel, accessible a la manette, au stick
  //: du casque et au joystick tactile (`Entree.surSuiteActions`). Les fleches
  //: bougent le joueur au passage, comme toute suite : c'est de la triche de
  //: developpeur, jamais un geste qu'on fait par accident.
  const SEQUENCE_DEBUG_ACTIONS = ['haut', 'haut', 'bas', 'bas', 'gauche', 'droite', 'gauche', 'droite'];
  let dernier = 0, accu = 0, fenetre = null, doc = null;
  let horsLigne = false;
  //: Debug des gels (Martin, 21 sept.) : le temps par systeme durant l'image en
  //: cours de simulation — null hors d'`avancer()` (le banc appelle `maj()`
  //: tout seul). `pas()` mesure sans rien changer au comportement : un
  //: `fn` refuse simplement d'etre chronometre quand `tEtapes` est null.
  let tEtapes = null;
  //: Le seuil au-dela duquel une image se signale : 50ms, pire que 20 IPS —
  //: une image ordinaire tourne sous les 16ms. En dessous, ce sont des
  //: courants d'air normaux, pas un gel.
  const SEUIL_GEL = 50;
  //: La partie pour laquelle `commencer()` a pose la ville, ou null tant qu'on
  //: n'a pas joue depuis le chargement de la page (voir `jouerPartie`).
  let monde = null;

  // --- Etats -------------------------------------------------------------------------

  function commencer() {
    const p = B.partie;
    monde = p;
    Entites.vider();
    B.entites.length = 0;
    Entites.creerDecor(Monde.carte.def);
    Entites.creerAmbulants(Monde.carte.def);
    Vehicules.creerSignalisation();
    Entites.creerPaquets(Monde.carte.def);
    // Le char laisse devant la planque a la derniere sauvegarde.
    // ⚠️ Sans position (la carte a change sous la partie — M8 a quintuple la
    // ville), il revient sur la rue la plus proche de la porte : une position
    // d'une ancienne carte tombe au hasard, et c'est un char dans un mur.
    const garde = p.planque.vehicule;
    if (garde && Vehicules.vehiculeDef(garde.slug)) {
      const place = garde.x === null || garde.x === undefined
        ? placeDevantLaPlanque() : { x: garde.x, y: garde.y };
      const v = place && Vehicules.creer(garde.slug, place.x, place.y, garde.angle || 0, { etat: 'stationne', sprite: garde.sprite });
      // ⚠️ `nuances` : le rehaut et l'ombre suivent la couleur (voir le lot).
      if (v) {
        if (garde.couleur) { v.couleur = garde.couleur; v.swaps = nuances(garde.couleur); }
        v.vie = Math.max(1, garde.vie); v.vole = !!garde.vole;
      }
    }
    // Le char DONNE par une mission (`donne.vehicule`, le taxi de m97) gare
    // devant la planque, a part de celui qu'on y laisse soi-meme.
    const donne = p.vehiculePlanque;
    if (donne && Vehicules.vehiculeDef(donne.slug)) {
      const place = placeDevantLaPlanque();
      const v = place && Vehicules.creer(donne.slug, place.x, place.y, donne.angle || 0, { etat: 'stationne' });
      if (v && donne.couleur) { v.couleur = donne.couleur; v.swaps = nuances(donne.couleur); }
    }
    // Les chars saisis attendent dans la cour du lot, comme celui de la
    // planque attend devant sa porte.
    Missions.garnirLaFourriere();
    const app = Monde.carte.apparition.joueur;
    let x = p.x !== null && p.x !== undefined ? p.x : app.x * TT + 8;
    let y = p.y !== null && p.y !== undefined ? p.y : app.y * TT + 8;
    // ⚠️ Au tout premier matin, on debarque au terminus. Des qu'on a la cle de
    // la planque en poche (m1 faite, `donne.message` = « LA CLE DE LA
    // PLANQUE »), c'est DEVANT LA PLANQUE qu'on reapparait au lancement : une
    // position perdue (la carte a change sous la partie) ne renvoie plus a la
    // gare, elle nous remet chez nous. Une partie continue, elle, garde sa
    // position sauvegardee (`p.x`), exactement comme avant.
    if ((p.x === null || p.x === undefined) && p.missionsFaites && p.missionsFaites.m1) {
      const porte = (Monde.carte.def.portes || []).find(function (q) { return q.lieu === 'planque'; });
      if (porte) { x = porte.x * TT + 8; y = (porte.y + 1) * TT + 8; }
    }
    // ⚠️ UNE POSITION SAUVEGARDEE N'EST PAS UNE PLACE OU L'ON TIENT. La sauvegarde
    // ecrit ou l'on est, et au volant c'est le centre du char : sous le toit d'un
    // garage, sur l'eau, dans une facade. Rouverte telle quelle, la partie nous
    // posait sur le toit du garage Bandini (Martin, 21 sept. 2026), et rien ne
    // sort un pieton d'un mur. C'est ICI qu'on corrige, pas a la sauvegarde : les
    // parties deja ecrites se rouvrent aussi.
    const debout = ouTenirDebout(x, y);
    if (debout) { x = debout.x; y = debout.y; }
    const j = Entites.creerJoueur(x, y);
    Monde.centrerCamera(j.x, j.y);
    Entites.peuplerDabord();          // ⚠️ apres le joueur : la bulle est autour de lui
    if (p.mission) p.mission = null;  // une mission ne survit pas au rechargement : ses figurants non plus
    B.mission = null; B.defi = null; B.cinema = null; B.ouverture = null; B.scene = null; B.finEnAttente = null;
    B.sonnerie = null;                       // un telephone qui sonnait dans la partie d'avant ne sonne pas dans celle-ci
    B.abribusServis = {};                    // les abribus qu'un autobus vient de servir (Autobus)
    Traversier.oublier();                    // rien a bord, la carte neuve n'a pas de pont pose
    Neige.oublier();                         // la rue d'une partie rechargee est blanche
    Incendies.oublier();                     // une nouvelle partie n'hérite pas des feux éteints
    Interactions.oublier();                  // ni de la soif des fontaines
    Monde.oublierLesRuesMouillees();         // ni de l'arroseuse d'une autre nuit
    B.lastCall = null;                       // ni des bars qu'elle a vus se vider
    B.transition = null;        // une partie ne commence jamais dans le noir d'une porte
    Histoire.creerDonneurs();
    Histoire.creerPanneaux();
    B.etat = 'jeu';
    B.recherche.etoiles = 0; B.recherche.chaleur = 0; B.recherche.vu = 0;
    Hud.voile(null);
    Hud.etat('jeu');
    Entree.contexte('pied');
    Son.Mus.arreter();          // le theme du menu laisse la place a la ville
    // ⚠️ On ne lance plus l'ambiance UNIQUE de la ville : c'est precisement
    // ce que la fiche retire — une seule musique de fond de La Pointe aux
    // Quais. `Son.Chef` choisit maintenant celle du district, et se tait si
    // une ambiance ENREGISTREE joue (elle occupe la meme case de l'echelle).
    Son.Chef.maj();
    Hud.message('BAIE-DES-BRUMES', 150);
    // ⚠️ LES CHANTIERS EN DERNIER. Poses au milieu, leurs machines prenaient des
    // numeros d'entite que la foule et les donneurs auraient eus, et tout ce qui
    // se tire a l'empreinte d'un numero changeait de tirage — trois juges sans
    // rapport en sont tombes. Ici, rien n'est encore dessine, et personne ne peut
    // etre ne dans une empreinte : a la premiere phase, c'est encore un mur.
    Chantiers.demarrer();
    // Le petit train et la montagne russe : ils ne creent aucune entite, donc
    // aucun numero n'est pris a personne.
    Foire.demarrer();
  }

  /** JOUER : la partie se pose, et l'histoire commence.

      ⚠️ DEUX FONCTIONS ET PAS UNE, et c'est la moitie qui compte : `commencer()`
      POSE une partie (la ville, le joueur, les donneurs) et ne raconte rien —
      c'est ce qu'appellent les bancs d'essai, cent fois, pour juger autre chose.
      `jouer()` est le GESTE : il pose la partie puis, si elle est neuve, lance
      l'ouverture. Melanger les deux, c'est faire jouer une introduction a
      chacun des cent tests qui voulaient seulement une ville.

      ⚠️ L'ouverture ne part JAMAIS au chargement de la page : le navigateur
      retient l'`AudioContext` tant que personne n'a touche, et une introduction
      AUDIO muette n'est pas une introduction. JOUER est le geste qui accorde le
      son ; l'ouverture commence juste apres.

      ⚠️ Et seulement a une partie NEUVE : `p.x` nul veut dire qu'on n'a jamais
      pose un pied dans la ville. Celui qui joue depuis trois jours n'a pas
      besoin qu'on lui presente son oncle — il la revoit du carnet s'il veut. */
  function jouer() {
    const p = B.partie;
    const neuve = (p.x === null || p.x === undefined) && !p.ouvertureVue;
    commencer();
    // Sans ouverture possible (pas de rue devant le terminus), les commandes
    // s'ouvrent tout de suite : c'est la fin de l'ouverture qui les montre.
    if (neuve && !Histoire.ouverture(false)) Hud.ouvrirCommandes();
  }

  // --- Les parties : trois emplacements -------------------------------------------------

  /** La partie de l'emplacement `n`, completee — ou une partie neuve s'il est vide. */
  function chargerPartie(n) {
    const p = Sauvegarde.completer(Sauvegarde.lire(n), B.defs);
    if (p.empreinte && p.empreinte !== B.defs.empreinte) {
      // Le catalogue a change : on garde la partie, mais une position qui
      // n'existe plus sur la nouvelle carte doit etre oubliee — la sienne, et
      // celle du char gare devant la planque.
      p.x = null; p.y = null;
      if (p.planque && p.planque.vehicule) {
        p.planque.vehicule.x = null; p.planque.vehicule.y = null;
      }
    }
    return p;
  }

  /** JOUER, au titre : le choix des parties.

      ⚠️ Sans aucune partie sauvegardee, JOUER JOUE. Trois fois « NOUVELLE
      PARTIE » devant quelqu'un qui ouvre le jeu pour la premiere fois, c'est un
      menu qui ne choisit rien — il commence dans l'emplacement 1, comme avant.
      `sur` : au retour d'un rechargement, le choix se montre quand meme, le
      curseur sur cet emplacement-la. */
  function ouvrirParties(sur) {
    if (!sur && !Sauvegarde.occupes().length) { jouerPartie(Sauvegarde.emplacement()); return; }
    Hud.voile(null);
    Hud.ouvrirMenu(Hud.menuParties(sur ? sur - 1 : undefined));
  }

  /** Jouer l'emplacement `n` : sa partie, ou une neuve s'il est vide.

      ⚠️ UNE VILLE DEJA POSEE POUR UNE AUTRE PARTIE SE RECHARGE, elle ne se
      recycle pas. `commencer()` sait reposer la MEME partie apres un retour au
      titre ; il ne sait pas oublier tout ce qu'une autre a laisse : le sang sur
      le trottoir, les lampadaires casses, la phase posee des chantiers, et les
      compteurs que chaque systeme accroche a `B` en cours de route. Un seul
      oubli, et la partie 2 porte les cicatrices de la 1. Recharger la page est
      le seul oubli complet, et il ne coute qu'au geste rare — changer de partie
      apres avoir joue. Le choix des parties se rouvre alors tout seul, le
      curseur sur celle qu'on a prise : il reste un ACTION a faire, et c'est
      tant mieux, parce que c'est ce geste-la qui rend le son.

      « Une autre partie », c'est un autre emplacement, mais aussi le meme
      emplacement efface ou ecrase par une copie depuis (`B.partie` n'est plus
      l'objet pour lequel la ville a ete posee). */
  function jouerPartie(n) {
    if (monde && (n !== Sauvegarde.emplacement() || B.partie !== monde)) {
      Sauvegarde.choisir(n);
      Sauvegarde.marquerRouverture(n);
      if (B.menu) Hud.fermerMenu();
      const etat = doc && doc.getElementById('etat-chargement');
      if (etat) etat.textContent = 'Changement de partie…';
      if (fenetre && fenetre.location && fenetre.location.reload) fenetre.location.reload();
      return;
    }
    if (n !== Sauvegarde.emplacement()) B.partie = chargerPartie(n);
    Sauvegarde.choisir(n);
    if (B.menu) Hud.fermerMenu();
    jouer();
  }

  /** Effacer l'emplacement `n`. ⚠️ Si c'est celui qu'on a charge, `B.partie`
      redevient une partie NEUVE tout de suite : l'ancienne, restee en memoire,
      se reecrirait sinon a la premiere sauvegarde automatique — une partie
      effacee qui revient toute seule dix secondes plus tard. */
  function effacerPartie(n) {
    Sauvegarde.effacer(n);
    if (n === Sauvegarde.emplacement()) B.partie = chargerPartie(n);
  }

  /** Copier `de` sur `vers`. Meme garde qu'`effacerPartie` : ecraser la partie
      chargee, c'est la remplacer en memoire aussi. */
  function copierPartie(de, vers) {
    const ok = Sauvegarde.copier(de, vers);
    if (ok && vers === Sauvegarde.emplacement()) B.partie = chargerPartie(vers);
    return ok;
  }

  // --- Les portes : noircir sur l'ancienne, changer au noir, eclaircir sur la nouvelle ---

  /*: La duree d'un fondu de porte, en images (60 = une seconde) : [noircir,
    eclaircir]. ⚠️ ASYMETRIQUE, et c'est voulu : entrer prend son temps — on
    pousse une porte, on veut le sentir — alors que sortir doit etre vif, parce
    qu'on veut retourner au jeu. Les 40 images d'avant, partagees en deux,
    etaient juste assez pour clignoter et pas assez pour lire. */
  const FONDU_ENTREE = [26, 20];
  const FONDU_ETAGE = [20, 16];
  const FONDU_SORTIE = [15, 11];

  /*: Ce qu'on garde d'elan en passant une porte, en fraction de la marche : on
    ne repart pas d'un arret complet. Une course qui s'arrete net au pas de la
    porte se sent teleportee. */
  const ELAN_DE_PORTE = 0.5;

  /** Un changement de scene qui se voit : on noircit sur la scene qu'on QUITTE,
      elle change AU NOIR (`faire`), et on eclaircit sur la nouvelle.

      ⚠️ C'est l'ordre, et lui seul, qui fait un fondu. `entrer()` chargeait la
      piece PUIS demandait le fondu : sa premiere moitie noircissait donc sur la
      scene deja changee et sa seconde l'eclaircissait — on voyait la piece une
      image, l'ecran noircissait, il s'eclaircissait sur la meme piece. Ce n'est
      pas un fondu enchaine, c'est un clignotement, et l'oeil le sait meme quand
      on n'arrive pas a le nommer.

      `duree` vaut `[fermer, ouvrir]` — ou `[fermer, TENIR, ouvrir]` quand le
      fondu doit raconter quelque chose. ⚠️ Une porte, on la passe : rien a
      tenir. Mais l'hopital, la prison et la nuit font PASSER DU TEMPS, et ce
      temps se sent dans le noir. C'est pendant `tenir` — et seulement la,
      quand l'ecran est vraiment plein — que `texte` s'ecrit.

      Le jeu est FIGE pendant (voir `maj()`). */
  function transiter(duree, faire, texte) {
    // ⚠️ Un fondu par-dessus un autre n'en empile pas deux : celui qui joue
    // finit tout de suite (sa scene change AU NOIR, une fois), et le nouveau
    // repart du clair. Se faire arreter en tombant dans la rue passait sinon
    // par deux noirs superposes, chacun avec son horloge.
    finirTransition();
    const tenu = duree.length > 2;
    B.transition = { t: 0, ferme: duree[0], tient: tenu ? duree[1] : 0, ouvre: duree[tenu ? 2 : 1],
                     faire: faire, texte: texte || null, fait: false, vu: false };
  }

  /** Le changement de scene lui-meme, au noir — une fois, jamais deux. */
  function auNoir() {
    const tr = B.transition;
    if (!tr || tr.fait) return;
    tr.fait = true;
    tr.faire();
  }

  /** Avance le fondu d'une image.

      ⚠️ Le noir s'arrete PILE a `ferme` (alpha 1) avant de changer la scene, et
      il ne s'eclaircit pas avant d'avoir ete dessine une fois (`vu`, pose par le
      HUD) : la boucle rattrape jusqu'a quatre images de simulation entre deux
      images dessinees, et sans ces deux precautions la premiere image de la
      nouvelle scene pourrait se montrer a 94 % de noir — donc se montrer. */
  function majTransition() {
    const tr = B.transition;
    if (!tr) return;
    if (!tr.fait) {
      tr.t++;
      if (tr.t >= tr.ferme) { tr.t = tr.ferme; auNoir(); }
      return;
    }
    if (!tr.vu) return;
    tr.t++;
    if (tr.t >= tr.ferme + tr.tient + tr.ouvre) B.transition = null;
  }

  /** Finit tout de suite le fondu en cours.

      ⚠️ Passer une porte pendant qu'un autre fondu joue est LE cas qui casse
      tout : sans ca, `sortir()` appele pendant le noircissement d'une entree ne
      trouve aucun interieur, refuse — et le joueur se reveille dedans sans avoir
      rien demande. */
  function finirTransition() {
    if (!B.transition) return;
    auNoir();
    B.transition = null;
  }

  /** Poser le joueur au pas d'une porte : la face et un reste d'elan dans le
      sens ou l'on passe, et la camera deja a sa place.

      ⚠️ La camera se pose AU NOIR, sur la cible exacte que `majCamera` viserait
      a la premiere image (position + avance de l'elan) : personne ne voit le
      saut, et l'amorti n'a rien a rattraper quand le jeu repart. */
  function poserDansLaPorte(j, sens) {
    const pas = B.defs.recherche.vitesses.joueur_marche * ELAN_DE_PORTE;
    j.vx = 0; j.vy = sens === 'haut' ? -pas : pas;
    j.face = sens;
    Entites.dansLaCarte(j);
    Monde.centrerCamera(j.x + j.vx * 14, j.y + j.vy * 14);
  }

  /** Passer une porte : on noircit sur la rue, la piece se charge AU NOIR, on
      eclaircit dedans. */
  function entrer(porte) {
    const j = B.joueur;
    finirTransition();
    if (!porte || !porte.interieur || B.interieur || j.dansVehicule) return false;
    // ⚠️ La piece se cherche AVANT de noircir : un fondu qui ne mene nulle part
    // est plus laid qu'une porte qui ne s'ouvre pas.
    const interieurs = (Monde.carte.def && Monde.carte.def.interieurs) || {};
    if (!interieurs[porte.interieur]) return false;
    // ⚠️ Elle s'ouvre AVANT le fondu, pas au noir : la premiere moitie du
    // fondu se joue sur la rue, et c'est la — et seulement la — qu'on peut
    // voir le battant bouger. Au noir, il n'y aurait rien a voir.
    Monde.ouvrirPorte(porte.x, porte.y);
    transiter(FONDU_ENTREE, function () {
      const piece = chargerPiece(porte);
      if (!piece) return;
      j.x = piece.interieur.apparition.x * TT + 8;
      j.y = piece.interieur.apparition.y * TT + 8;
      poserDansLaPorte(j, 'haut');
      Son.SFX.porte(piece.interieur.porte);   // la porte s'entend AU NOIR : c'est la qu'on la passe
      Hud.message(piece.interieur.nom.toUpperCase(), 120);
    });
    return true;
  }

  /** La piece derriere une porte, chargee AU NOIR : la rue mise de cote (c'est
      par cette porte-la qu'on ressortira), les gens de dedans, la toune. Le
      joueur, lui, n'est pas encore pose — c'est a l'appelant de dire ou.

      ⚠️ UNE SEULE FACON D'ENTRER. Le reveil a l'hopital entre sans pousser la
      porte ; s'il chargeait la piece a sa facon, le jour ou l'entree change
      (un donneur de plus, une toune), l'hopital l'oublierait. */
  function chargerPiece(porte) {
    const piece = Monde.entrer(porte);
    if (!piece) return null;
    B.exterieur = { carte: piece.ville, entites: B.entites, x: porte.x * TT + 8, y: (porte.y + 1) * TT + 10 };
    B.entites = [B.joueur];
    B.particules.length = 0;
    B.interieur = piece.interieur;
    Entites.reindexerDecor();
    Entites.peuplerInterieur(piece.interieur);
    Histoire.creerDonneursDedans(piece.interieur);
    // ⚠️ La toune du commerce demarre AU NOIR elle aussi : la porte se ferme,
    // la rue se tait, et ce qu'on entend en ouvrant les yeux est deja celle
    // d'ici. Une piece qui n'est pas un commerce reste silencieuse.
    Son.Radio.dedans(piece.interieur.slug);
    // ⚠️ L'helico devient sourd AU NOIR aussi, avec la porte qui se ferme : le
    // monde est fige pendant le fondu, et sans cet appel on l'entendrait en plein
    // air dans la piece deja eclairee.
    Police.majBruitHelico();
    return piece;
  }

  /** Le reveil a l'hopital : DEDANS, couche dans le lit de l'urgence — demande
      de Martin. On se reveillait sur le trottoir devant la porte, comme si
      personne ne nous avait ramasses.

      AU NOIR : la piece de l'hopital se charge comme par sa porte, et le joueur
      prend le lit du MALADE de l'urgence — sa tuile de tete, la ou le plan le
      couche (`carte.ASSIS_OU_COUCHE`). Le malade n'y est pas cette fois : c'est
      nous qu'on a mis dans son lit. La premiere poussee du stick nous leve
      (`Entites.majJoueur`), et la porte d'en bas mene devant l'hopital.

      ⚠️ Tombe DANS une piece (un comptoir, l'hopital lui-meme), on en ressort
      d'abord : `Monde.entrer` part de la VILLE, et une piece chargee par-dessus
      une piece perdrait le chemin du retour.

      Rend faux quand la ville n'a pas d'hopital ou que sa piece n'a pas de lit :
      on se reveille alors devant la porte, comme avant. */
  function coucherALHopital() {
    const j = B.joueur;
    quitterLaPiece();
    const porte = (Monde.carte.def.portes || []).find(function (q) { return q.lieu === 'hopital' && q.interieur; });
    const commune = porte && ((Monde.carte.def.interieurs || {})[porte.interieur]);
    const lit = commune && (commune.gens || []).find(function (g) { return g.qui === 'malade'; });
    if (!lit) return false;
    const piece = chargerPiece(porte);
    if (!piece) return false;
    for (const e of B.entites.slice()) {
      if (e.alite && Math.floor(e.x / TT) === lit.x && Math.floor(e.y / TT) === lit.y) Entites.retirer(e);
    }
    Entites.coucher(j, lit.x, lit.y);
    Entites.indexer();
    // ⚠️ Pas de clignotement : il n'y a personne a craindre dans un lit
    // d'hopital, et un corps qui clignote sous sa couverture a l'air d'un bogue.
    j.invincible = 0;
    Monde.centrerCamera(j.x, j.y);
    return true;
  }

  /** Monter l'escalier : meme adresse, autre plancher.

      ⚠️ On ne repasse PAS par la rue : `B.exterieur` reste ce qu'il etait, et
      c'est toujours par la porte d'en bas qu'on ressortira. On arrive sur
      l'escalier qui redescend — pas au milieu de la piece : c'est ce qui dit
      au joueur par ou il est monte. */
  function changerEtage(slug, ou) {
    const j = B.joueur;
    finirTransition();
    if (!B.interieur || !B.exterieur || j.dansVehicule) return false;
    const depuis = B.interieur.slug;
    // Comme pour une porte : l'etage se cherche avant de noircir.
    const etages = (B.exterieur.carte.def && B.exterieur.carte.def.interieurs) || {};
    if (!etages[slug]) return false;
    transiter(FONDU_ETAGE, function () {
      const piece = Monde.changerPiece(slug);
      if (!piece) return;
      B.entites = [j];
      B.particules.length = 0;
      B.interieur = piece.interieur;
      Entites.reindexerDecor();
      Entites.peuplerInterieur(piece.interieur);
      Histoire.creerDonneursDedans(piece.interieur);
      // ⚠️ `ou` : la ou l'on arrive quand ce n'est ni un escalier ni la porte — le
      // quai du metro, ou l'on descend de la rame et pas de l'escalier.
      const retour = ou || (piece.interieur.points || []).find(function (p) {
        return p.type === 'escalier' && p.vers === depuis;
      }) || piece.interieur.apparition;
      j.x = retour.x * TT + 8; j.y = retour.y * TT + 8;
      poserDansLaPorte(j, 'bas');
      Son.SFX.porte(piece.interieur.porte);
      Hud.message(piece.interieur.nom.toUpperCase(), 120);
    });
    return true;
  }

  function sortir() {
    const j = B.joueur;
    finirTransition();
    // ⚠️ Le metro d'abord : la porte de la rame mene au quai, et l'escalier du
    // quai remonte a l'edicule de la station ou l'on est (`Metro.sortir`).
    if (Metro.sortir()) return true;
    const ext = B.exterieur;
    if (!B.interieur || !ext) return false;
    transiter(FONDU_SORTIE, function () {
      const genre = B.interieur ? B.interieur.porte : undefined;   // la porte qu'on a poussee en entrant
      quitterLaPiece();
      // ⚠️ La tuile devant la porte, au pixel : entrer puis sortir doit ramener
      // exactement la ou l'on etait, meme en sortant pendant le fondu d'entree.
      j.x = ext.x; j.y = ext.y;
      poserDansLaPorte(j, 'bas');
      Police.majBruitHelico();              // la porte s'ouvre : l'helico se reentend en plein air
      // ⚠️ La porte de la RUE s'ouvre ici, une fois `Monde.restaurer` fait :
      // avant, `Monde.carte` est encore la piece, et ses battants ne sont pas
      // ceux de la ville. On la trouve juste au-dessus du pas de porte.
      // ⚠️ `ext.porte` quand la sortie n'est pas une porte de facade : un
      // edicule dont le trottoir est au nord a la chaussee au-dessus du pas.
      const battant = ext.porte || { x: Math.floor(ext.x / TT), y: Math.floor(ext.y / TT) - 1 };
      Monde.ouvrirPorte(battant.x, battant.y);
      Son.SFX.porte(genre);
    });
    return true;
  }

  /** La ville reprend sa place, AU NOIR, sans bruit de porte : c'est l'appelant
      qui dit ou poser le joueur. Rend ce qu'on savait du dehors, ou null quand
      on n'etait dans aucune piece. */
  function quitterLaPiece() {
    const j = B.joueur, ext = B.exterieur;
    if (!B.interieur || !ext) return null;
    Monde.restaurer(ext.carte);
    B.entites = ext.entites;
    if (B.entites.indexOf(j) < 0) B.entites.push(j);
    B.particules.length = 0;
    B.interieur = null;
    Son.Radio.dedans(null);                 // on ressort : la toune du commerce s'arrete
    B.exterieur = null;
    Entites.reindexerDecor();
    return ext;
  }

  function pause() {
    if (B.etat !== 'jeu') return;
    // ⚠️ La roue d'armes se referme SANS degainer : on a appuye sur PAUSE, pas
    // choisi une arme. Sans ca elle reste ouverte sous le menu, le monde reste
    // au ralenti en sortant, et rien ne la ferme plus (`majRoue` ne tourne pas
    // en pause). Meme chose pour la carte, juste en dessous.
    Combat.fermerRoue(false);
    B.etat = 'pause';
    Hud.etat('pause');
    Missions.sauvegarderPartie();
    Hud.ouvrirMenu(Hud.menuPause());
  }

  function reprendre() {
    if (B.etat !== 'pause') return;
    B.etat = 'jeu';
    Hud.etat('jeu');
    if (B.menu) Hud.fermerMenu();
  }

  function basculerPause() { if (B.etat === 'jeu') pause(); else if (B.etat === 'pause') reprendre(); else if (B.etat === 'carte') fermerCarte(); else if (B.etat === 'photo') fermerPhoto(); }

  /** Reveille par la suite secrete (`SEQUENCE_DEBUG`) — jamais par un bouton.
      En partie seulement, et pas par-dessus un autre menu, une scene ou la
      roue d'armes : ce sont eux qui gelent deja la simulation, pas ce menu.

      ⚠️ La taper ACTIVE les triches de cette partie : la ligne TRICHES apparait
      dans la PAUSE (`Hud.menuPause`), et se sauve avec la partie — on n'a plus
      a retaper la suite, mais une partie qui ne l'a jamais tapee n'en montre rien. */
  function ouvrirMenuDebug() {
    if (B.etat !== 'jeu' || B.menu || B.cinema || B.roue) return;
    if (!triche('menu')) { B.partie.triches.menu = true; Missions.sauvegarderPartie(); }
    Hud.ouvrirMenu(Hud.menuDebug());
  }

  /** La carte de la ville, plein ecran : la simulation attend. */
  function ouvrirCarte() {
    if (B.etat !== 'jeu' && B.etat !== 'pause') return;
    Combat.fermerRoue(false);
    if (B.menu) Hud.fermerMenu();
    B.etat = 'carte';
    Hud.etat('carte');
  }

  function fermerCarte() {
    if (B.etat !== 'carte') return;
    B.etat = 'jeu';
    Hud.etat('jeu');
  }

  //: Le PAS d'un fondu de camera par image, en pixels — assez vif pour
  //: explorer un pate de maisons en une seconde, assez lent pour viser un
  //: cadrage precis (voir `majPhoto`).
  const VITESSE_PHOTO = 6;

  /** Le mode photo (M14, 6e vague) : comme la carte, la simulation attend —
      mais la camera se detache et repond au stick, et l'ecran reste celui du
      jeu (pas un fond noir) pour qu'on cadre ce qu'on voit. Depuis le jeu ou
      la pause, comme `ouvrirCarte`. */
  function ouvrirPhoto() {
    if (B.etat !== 'jeu' && B.etat !== 'pause') return;
    Combat.fermerRoue(false);
    if (B.menu) Hud.fermerMenu();
    B.etat = 'photo';
    Hud.etat('photo');
    Entree.contexte('photo');
    B.photo = { dx: 0, dy: 0, filtre: 0 };
  }

  function fermerPhoto() {
    if (B.etat !== 'photo') return;
    B.photo = null;
    B.etat = 'jeu';
    Hud.etat('jeu');
    Entree.contexte(B.joueur && B.joueur.dansVehicule ? 'vehicule' : 'pied');
  }

  //: Les pas essayes pour poser le deuxieme joueur PRES du premier sans le
  //: planter dans un mur — meme idee que `Hud.placeAupres` (l'objectif
  //: teleporte), une tuile a la fois autour de lui.
  const PAS_COOP = [[1, 0], [-1, 0], [0, 1], [0, -1], [1, 1], [-1, 1], [1, -1], [-1, -1], [2, 0], [-2, 0]];

  /** Une tuile marchable A COTE de (x, y) — jamais (x, y) lui-meme, deja pris
      par celui qu'on longe. */
  function placePresDe(x, y) {
    const tx0 = Math.floor(x / TT), ty0 = Math.floor(y / TT);
    for (const p of PAS_COOP) {
      const tx = tx0 + p[0], ty = ty0 + p[1];
      if (Monde.marchablePieton(tx, ty) && !Monde.estMeuble(tx, ty)) return { x: tx * TT + 8, y: ty * TT + 8 };
    }
    return { x: x, y: y };
  }

  /** La coop locale (M14, essai — RISQUÉ, pas promis) : bascule un deuxième
      joueur, mené par la deuxième manette, à côté du premier. Depuis le menu
      DEBUG seulement — aucune promesse tant que Martin n'a pas jugé, à deux
      manettes, si la caméra tient à 480×270 (voir `Monde.majCameraCoop`). */
  function basculerCoop() {
    if (B.coop) {
      Entites.retirer(B.coop.entite);
      B.coop = null;
      return;
    }
    if (!B.joueur) return;
    const place = placePresDe(B.joueur.x, B.joueur.y);
    B.coop = { entite: Entites.creerCoopJoueur2(place.x, place.y) };
  }

  /** Le stick promene la camera (bornee a la ville, voir `Monde.limitesCamera`),
      ARME cycle les filtres, ACTION capture et telecharge, ANNULER/PAUSE/CARTE
      referment — trois sorties parce que le pouce d'un telephone n'a que
      quatre boutons et que ANNULER n'en est pas un (voir `Entree.etiquettes`). */
  function majPhoto() {
    const p = B.photo, axe = Entree.axe;
    if (axe.mag > 0) { p.dx += axe.x * axe.mag * VITESSE_PHOTO; p.dy += axe.y * axe.mag * VITESSE_PHOTO; }
    const lim = Monde.limitesCamera();
    p.dx = borner(B.cam.x + p.dx, lim.xMin, lim.xMax) - B.cam.x;
    p.dy = borner(B.cam.y + p.dy, lim.yMin, lim.yMax) - B.cam.y;
    if (Entree.neuf('arme')) p.filtre = (p.filtre + 1) % FILTRES_PHOTO.length;
    if (Entree.neuf('action')) Base.telecharger('bandini-' + Date.now() + '.png');
    if (Entree.neuf('annuler') || Entree.neuf('pause') || Entree.neuf('carte')) fermerPhoto();
  }

  function retourTitre() {
    Missions.sauvegarderPartie();
    // ⚠️ UN DES TROIS MOMENTS QUI COMPTENT (M14) : on vient de finir de jouer, et
    // c'est la que la partie doit etre a jour sur le compte — pas dans une minute
    // et demie. Les deux autres : l'onglet qui se ferme, et le repos de
    // `Compte.apresEcriture` pendant qu'on joue. ⚠️ `ranger` et pas `monter` : le
    // titre est aussi le moment ou une partie qui attendait en coulisse (elle ne
    // pouvait pas se poser pendant qu'on jouait) peut enfin descendre.
    Compte.ranger();
    // Le titre revient : le defi du jour a peut-etre change depuis (au plus une demande / 10 min).
    Defi.rafraichir();
    B.etat = 'titre';
    Hud.etat('titre');
    Hud.voile('titre');
    Son.Ambiance.arreter();
    Son.Chef.arreter();
    // ⚠️ La ville reste derriere le titre, figee, l'helico avec : plus rien ne
    // reglerait son bruit, qui tournerait sous la musique du titre.
    Police.taireHelico();
    Son.Mus.jouer('titre');
  }

  // --- Boucle -------------------------------------------------------------------------

  /** La tuile de rue la plus proche de la porte de la planque. */
  function placeDevantLaPlanque() {
    const porte = (Monde.carte.def.portes || []).find(function (q) { return q.lieu === 'planque'; });
    if (!porte) return null;
    for (let r = 1; r <= 8; r++) {
      for (let dy = -r; dy <= r; dy++) {
        for (let dx = -r; dx <= r; dx++) {
          const tx = porte.x + dx, ty = porte.y + dy;
          if (Monde.estRoute(tx, ty) && !Monde.estPassage(tx, ty)) return { x: tx * TT + 8, y: ty * TT + 8 };
        }
      }
    }
    return null;
  }

  /** Ou un pieton tient debout, au plus pres du pixel (x, y) : ce pixel-la s'il y
      tient (ni mur, ni eau, ni grillage), sinon le centre de la tuile a pied la
      plus proche — hors chaussee, hors meuble —, ou null a plus de 12 tuiles.

      ⚠️ La plus proche AU PIXEL, pas la premiere d'une spirale : sorti du toit du
      garage, on retombe devant sa porte, pas dans la ruelle derriere parce que la
      spirale commence par le nord. */
  function ouTenirDebout(x, y) {
    const tx = Math.floor(x / TT), ty = Math.floor(y / TT);
    if (!Monde.bloque(tx, ty, Monde.MASQUE_PIETON)) return { x: x, y: y };
    let mieux = null, loin = Infinity;
    for (let dy = -12; dy <= 12; dy++) {
      for (let dx = -12; dx <= 12; dx++) {
        if (!Monde.marchablePieton(tx + dx, ty + dy) || Monde.estMeuble(tx + dx, ty + dy)) continue;
        const px = (tx + dx) * TT + 8, py = (ty + dy) * TT + 8;
        const d = (px - x) * (px - x) + (py - y) * (py - y);
        if (d < loin) { loin = d; mieux = { x: px, y: py }; }
      }
    }
    return mieux;
  }

  function maj() {
    Entree.debutImage();
    // ⚠️ Le debug INVINCIBLE (`Hud.menuDebug`) reutilise les images
    // d'invincibilite ORDINAIRES (`Entites.blesser` refuse tout coup tant
    // qu'elles durent) plutot qu'un second garde-fou : en la rechargeant
    // CHAQUE image, tant que le flag tient, elle ne retombe jamais a zero — et
    // combat, tirs, explosions, collisions restent le MEME chemin qu'en jeu
    // normal, juste sans jamais s'epuiser.
    if (triche('invincible') && B.joueur) B.joueur.invincible = 30;
    // ⚠️ MÊME PATRON que l'invincibilité : on recharge le souffle à fond à
    // CHAQUE image tant que le flag tient, au lieu d'un second garde-fou dans
    // la dépense. Le sprint et la nage restent le même chemin, juste sans
    // jamais s'épuiser — et on ne coule jamais.
    if (triche('endurance') && B.joueur) B.joueur.endurance = B.defs.recherche.vitesses.endurance;
    // ⚠️ A chaque image, quel que soit l'ecran : la musique du menu doit
    // tourner au titre, la ou la simulation, elle, ne tourne pas.
    Son.Mus.tick();
    // ⚠️ ICI AUSSI, et pas dans `Entites` : le musicien de rue DEMANDE sa toune
    // pendant la simulation, mais c'est l'horloge audio qui la joue — au menu,
    // en pause, dans un magasin, il faut quand meme venir couper le son du gars
    // qu'on a laisse sur le trottoir. Une musique qu'on n'arrete que la ou on
    // la demarre est une musique qui reste allumee.
    Son.Rue.tick();
    if (Entree.neuf('muet')) {
      B.options.muet = !B.options.muet;
      Son.majVolume();
      Hud.message(B.options.muet ? 'SON COUPÉ' : 'SON');
    }
    // ⚠️ « Jouer » n'etait qu'un bouton de la page : a la manette (ou au
    // clavier), on ne pouvait pas commencer la partie sans toucher l'ecran.
    // La ligne d'aide du titre suit l'appareil qu'on tient.
    if (B.etat === 'titre') Hud.majAideDuTitre();
    if (B.etat === 'titre' && Hud.voileCourant === 'titre'
        && (Entree.neuf('action') || Entree.neuf('pause'))) {
      Son.reveiller();
      const sansSon = Son.enAttente();
      ouvrirParties();
      // ⚠️ Apres `commencer()`, qui pose son propre message : sinon le nôtre
      // est efface par « BAIE-DES-BRUMES » et le silence reste muet.
      // Commencer a la manette ne donne AUCUN geste au navigateur : il refuse
      // alors le son sans rien dire. On le dit a sa place.
      if (sansSon && B.etat === 'jeu') Hud.message('SON EN ATTENTE — TOUCHE L\'ÉCRAN', 300);
      Entree.videPresse();
      return;
    }
    // Le choix des parties, au titre : un menu comme les autres.
    if (B.etat === 'titre' && B.menu) {
      const choisit = Entree.neuf('action');
      if (choisit) Son.reveiller();
      const sansSon = choisit && Son.enAttente();
      Hud.majMenu();
      // ⚠️ Meme avis qu'au titre : c'est ICI qu'on commence, desormais.
      if (sansSon && B.etat === 'jeu') Hud.message('SON EN ATTENTE — TOUCHE L\'ÉCRAN', 300);
      Entree.videPresse();
      return;
    }
    // ⚠️ UNE SCENE FIGE LA VILLE (l'ouverture, et toute scene de `Scenes`),
    // comme un dialogue et comme une porte : le
    // trafic, la foule et la police ne tournent pas pendant qu'on la regarde.
    // Deux raisons, et la seconde est la vraie : une scene ou un char peut
    // entrer dans le champ n'est plus une scene, et surtout une partie jouee
    // avec l'ouverture doit etre EXACTEMENT celle qu'on aurait jouee sans —
    // c'est ce qu'un juge du banc verifie, tuile par tuile.
    //
    // ⚠️ PASSER (le bouton FRAPPE, ou PAUSE) saute TOUT, a la manette et au
    // doigt comme au clavier. ACTION, lui, passe une replique : c'est
    // `majCinema` qui s'en occupe, et les etiquettes tactiles le disent deja
    // (« PASSER » et « SUIVANT », contexte `dialogue`).
    if (B.etat === 'jeu' && B.scene) {
      if (Entree.neuf('pause') || Entree.neuf('attaque')) { Scenes.passer(); Entree.videPresse(); return; }
      Scenes.maj();
      Entree.videPresse();
      return;
    }
    if (B.etat === 'jeu' && B.transition) {
      // ⚠️ Le jeu est FIGE pendant un fondu de porte. Avant, la simulation
      // continuait : on pouvait sortir d'une piece et se faire renverser par un
      // char qu'on n'a pas vu venir, sur un ecran noir ou l'on ne controle rien.
      // Un menu fige deja tout (`if (B.menu) return`) ; une porte fait pareil.
      // ⚠️ SAUF les battants : c'est justement pendant le fondu qu'on doit VOIR
      // la porte s'ouvrir. Figes avec le reste, ils resteraient au premier
      // pixel — et le joueur traverserait une porte fermee, ce que Martin a vu.
      // C'est la seule chose qui bouge quand tout le reste est arrete, et elle
      // ne touche a rien d'autre qu'a son propre compteur.
      Monde.majBattants();
      majTransition();
      Entree.videPresse();
      return;
    }
    if (B.etat === 'jeu' && B.menu) {
      // Un menu ouvert fige la simulation : le temps ne passe pas au comptoir.
      Hud.majMenu();
      Entree.videPresse();
      return;
    }
    if (B.etat === 'jeu') {
      if (Entree.neuf('pause')) { pause(); Entree.videPresse(); return; }
      if (Entree.neuf('carte')) { ouvrirCarte(); Entree.videPresse(); return; }
      // ⚠️ UN DIALOGUE OU L'ON NE PEUT PAS BOUGER FIGE LA VILLE — demande de
      // Martin : « il faut aussi figer tout lors qu'on est au telephone et
      // qu'on ne peut pas bouger ». Le telephone sonne n'importe ou, en pleine
      // rue : `Entites.majJoueur` clouait le joueur sur place (`vx = vy = 0`)
      // pendant que le trafic, la foule et la police continuaient — on encaisse
      // des coups qu'on ne peut pas rendre, et c'est la seule chose qu'un jeu
      // ne doit jamais faire. Un menu fige deja tout (« le temps ne passe pas
      // au comptoir »), un fondu de porte aussi : un appel est de la meme
      // famille.
      //
      // ⚠️ SAUF AU VOLANT, et c'est la moitie qui compte autant : au volant on
      // PEUT encore bouger (`Vehicules.majJoueur` lit toujours le gaz pendant
      // un dialogue). Figer un char lance parce que le telephone sonne, ce
      // serait poser un mur au milieu de la rue.
      //
      // ⚠️ `Histoire.maj` reste appele : c'est lui qui fait avancer la
      // replique (`majCinema` compte ses propres images) et qui raccroche. Le
      // figer, ce serait un appel dont on ne sort jamais.
      if (B.cinema && B.joueur && !B.joueur.dansVehicule) {
        Histoire.maj();
        Entree.videPresse();
        return;
      }
      // ⚠️ LE SELECTEUR D'ARME SE LIT A CHAQUE IMAGE, avant tout le reste et
      // HORS du ralenti ci-dessous : c'est lui qui decide du ralenti (roue
      // ouverte = une image de monde sur quatre), et une roue qui ne se
      // lirait qu'une image sur quatre repondrait au quart.
      Combat.majRoue();
      // Le MONDE, lui, rampe pendant qu'on choisit son arme. Tout ce qui est
      // ici mesure le temps en IMAGES (cadences, minuteries, usure) : en
      // sauter trois sur quatre ralentit tout d'un coup, sans un seul `dt`.
      if (Combat.tempsQuiPasse()) {
        pas('monde', function () {
          Monde.majHeure();
          Monde.majBattants();
          Monde.majChemins();
          Monde.majSonDuBord();          // les vagues : leur volume est une question de carte, pas de son
        });
        // La musique suit ce qui t'arrive (Chef), la radio parle entre les
        // tounes (Ondes, M15), on s'entend respirer et un quartier s'entend
        // avant de se voir (Souffle, Quartier, M15).
        pas('son', function () { Son.Chef.maj(); Son.Ondes.maj(); Son.Souffle.maj(B.joueur); Son.Quartier.maj(); });
        pas('entites', Entites.maj);
        pas('combat', Combat.maj);
        pas('vehicules', Vehicules.maj);
        pas('traversier', Traversier.maj); // apres les chars : ce qui est a bord suit la coque
        pas('neige', Neige.maj);
        pas('police', Police.maj);
        pas('incendies', Incendies.maj);
        pas('interactions', Interactions.maj);
        pas('missions', Missions.maj);
        pas('chantiers', Chantiers.maj);
        pas('foire', Foire.maj);
        pas('metro', Metro.maj);
        pas('histoire', Histoire.maj);
        Monde.majCamera();
        B.t++;
      }
    } else if (B.etat === 'carte') {
      // La carte de la ville : N, ECHAP, ACTION ou FRAPPE la referment.
      if (Entree.neuf('carte') || Entree.neuf('pause') || Entree.neuf('action') || Entree.neuf('attaque') || Entree.neuf('annuler')) { fermerCarte(); Entree.videPresse(); return; }
    } else if (B.etat === 'photo') {
      majPhoto();
    } else if (B.etat === 'pause') {
      // ⚠️ Pendant qu'on reapprend un bouton de manette, ECHAP annule
      // l'apprentissage ; il ne sort pas de la pause.
      if (Entree.apprendEnCours()) { Hud.majMenu(); Entree.videPresse(); return; }
      // Sur l'ecran MANETTE, START sert a se voir s'allumer, pas a reprendre.
      const sortir = B.menu && B.menu.manetteInerte ? Entree.neufSansManette : Entree.neuf;
      if (sortir('pause')) { reprendre(); Entree.videPresse(); return; }
      if (B.menu) Hud.majMenu();
      else if (Entree.neuf('action')) reprendre();
      // Fermer le dernier menu avec FRAPPE, c'est reprendre.
      if (!B.menu && B.etat === 'pause') reprendre();
    }
    Entree.videPresse();
  }

  /** Chronometre `fn` (aucun argument, aucune valeur de retour utilisee — tous
      les `.maj()` de systeme) sous le nom `nom`, dans `tEtapes` : ne fait rien
      de plus que l'appel nu quand `tEtapes` est null (hors d'`avancer()`). */
  function pas(nom, fn) {
    if (!tEtapes || typeof performance === 'undefined' || !performance.now) { fn(); return; }
    const d = performance.now();
    fn();
    tEtapes[nom] = (tEtapes[nom] || 0) + performance.now() - d;
  }

  /** Ce qui aide a relire un gel dans la console : ou on en etait, sans
      rejouer la partie pour le savoir. */
  function contexteGel() {
    const b = ['etat=' + B.etat];
    if (B.partie) b.push('jour ' + B.partie.jour, (Monde.heureTexte && Monde.heureTexte()) || '');
    if (B.cinema) b.push('cinema:' + (B.cinema.mission || '?'));
    if (B.scene) b.push('scene');
    if (B.menu) b.push('menu');
    if (B.transition) b.push('transition');
    if (B.joueur && B.joueur.dansVehicule) b.push('vehicule');
    return b.join(' ');
  }

  /** Une image a mis plus de `SEUIL_GEL` a se simuler ET se dessiner : on le
      dit, avec de quoi savoir OU ca a coute cher sans avoir a le reproduire
      sous un profileur. `etapes` : le temps par systeme, accumule sur les
      `n` pas de simulation de cette image (voir `avancer`) ; peut etre vide
      (aucun pas — le jeu etait fige, menu ou cinema). */
  function signalerGel(duree, etapes, dureeRendu, n) {
    if (typeof console === 'undefined' || !console.warn) return;
    const detail = Object.keys(etapes)
      .sort(function (a, c) { return etapes[c] - etapes[a]; })
      .map(function (k) { return k + ' ' + Math.round(etapes[k]) + 'ms'; })
      .join(', ');
    console.warn('[gel] ' + Math.round(duree) + 'ms (' + n + ' pas, rendu ' + Math.round(dureeRendu) + 'ms) — '
      + contexteGel() + (detail ? ' — ' + detail : ''));
  }

  function rendre() {
    if (!B.carte) return;
    B.image++;                          // l'horloge de l'OEIL : elle avance meme quand le monde est fige
    const ctx = Base.debut();
    ctx.fillStyle = '#0b0a12';
    ctx.fillRect(0, 0, VW, VH);
    const cam = B.cam;
    const sec = B.cam.secousse > 0.05 ? B.cam.secousse : 0;
    const vue = { x: cam.x + (sec ? (Math.random() - 0.5) * sec * 8 : 0) + (B.photo ? B.photo.dx : 0),
                  y: cam.y + (sec ? (Math.random() - 0.5) * sec * 8 : 0) + (B.photo ? B.photo.dy : 0) };
    Monde.dessinerSol(ctx, vue);
    if (!B.interieur) Neige.dessinerSol(ctx, vue);     // la neige au sol, SOUS les rails et les gens
    if (!B.interieur) Monde.dessinerMouille(ctx, vue); // derriere l'arroseuse (la nuit a ses habitudes)
    // Le tunnel, la rame et ses fenetres : peints par-dessus le sol de la piece,
    // sous les gens du quai.
    if (B.interieur) Metro.dessiner(ctx, vue);
    // ⚠️ Les battants PAR-DESSUS le sol, jamais dedans : repeindre un
    // morceau de 256 px a chaque image pour une porte tuerait le cache.
    if (!B.interieur) { Autobus.dessinerRails(ctx, vue); Neige.dessinerPanneaux(ctx, vue); Monde.dessinerBattants(ctx, vue); Monde.dessinerPortesDeGarage(ctx, vue); Monde.dessinerBarrieres(ctx, vue); }
    Entites.dessinerDecals(ctx, vue);     // le sang est SOUS les pieds
    if (!B.interieur) Histoire.dessinerCheminCourse(ctx, vue);   // le trace d'une course, sur la chaussee
    if (!B.interieur) Entites.dessinerBetes(ctx, vue);   // un goeland passe sous personne
    Entites.dessiner(ctx, vue);
    Entites.dessinerCible(ctx, vue);
    Entites.dessinerParticules(ctx, vue);
    if (B.options.trace && !B.interieur) Vehicules.dessinerTrace(ctx, vue);
    if (!B.interieur) Police.dessinerHelico(ctx, vue);
    if (!B.interieur) Neige.dessinerTempete(ctx);      // le voile et les flocons, SOUS la nuit
    const lampes = Monde.lampesVisibles(vue);
    // ⚠️ Les feux ont DEJA ete peints, deux lignes plus haut : leurs lampes
    // sont ramassees EN DESSINANT, donc il n'y a ici que celles de l'ecran, et
    // chacune porte la couleur de sa phase a CETTE image-ci. Les chercher
    // autrement voudrait dire balayer 482 poteaux par image.
    if (!B.interieur) for (const l of Vehicules.lampesDesFeux()) lampes.push(l);
    // Les phares (la nuit a ses habitudes) : ramasses en dessinant, comme les feux.
    if (!B.interieur) for (const l of Vehicules.lampesDesPhares()) lampes.push(l);
    // Les fleches d'une course : lumineuses, meme la nuit.
    if (!B.interieur) for (const l of Histoire.lampesDeCourse(vue)) lampes.push(l);
    const projecteur = !B.interieur ? Police.lampeHelico(vue) : null;
    if (projecteur && Monde.ambiance().alpha > 0.2) lampes.unshift(projecteur);
    // Les empreintes des chars, pour decouper les faisceaux qui les recouvrent.
    const corpsPhares = !B.interieur ? Vehicules.corpsDesPhares() : [];
    // ⚠️ Le filtre du mode photo se pose sur l'ECRAN (`Base.ecran()`), pas dans
    // `Base.fin` : il ne doit teindre QUE le dernier `drawImage` de cette
    // fonction-la (la ville deja peinte), jamais le HUD dessine juste apres.
    if (B.photo) Base.ecran().filter = FILTRES_PHOTO[B.photo.filtre].css;
    Base.fin(Monde.ambiance(), lampes, corpsPhares);
    if (B.photo) Base.ecran().filter = 'none';
    Hud.dessiner();
  }

  function boucle(t) {
    fenetre.requestAnimationFrame(boucle);
    // ⚠️ Dans le casque, c'est la SESSION WebXR qui cadence le jeu (voir
    // `Casque`) : la fenetre se tait, sinon le monde avancerait deux fois.
    if (typeof Casque !== 'undefined' && Casque.actif) return;
    avancer(t);
  }

  /** Une image : les pas fixes de la simulation, puis le rendu. */
  function avancer(t) {
    const debut = (typeof performance !== 'undefined' && performance.now) ? performance.now() : t;
    const dt = Math.min(60, t - dernier);
    dernier = t;
    accu += dt;
    let n = 0;
    tEtapes = {};
    while (accu >= PAS && n < 4) { maj(); accu -= PAS; n++; }
    if (accu > 200) accu = 0;
    const avantRendu = (typeof performance !== 'undefined' && performance.now) ? performance.now() : t;
    rendre();
    const fin = (typeof performance !== 'undefined' && performance.now) ? performance.now() : t;
    B.stats.ms = B.stats.ms * 0.9 + (fin - debut) * 0.1;
    if (fin - debut > SEUIL_GEL) signalerGel(fin - debut, tEtapes, fin - avantRendu, n);
    tEtapes = null;
  }

  // --- Demarrage ------------------------------------------------------------------------

  function fabriqueCanvas(w, h) {
    const c = doc.createElement('canvas');
    c.width = w; c.height = h;
    return c;
  }

  function chargerJson(url, quoi, suivi) {
    return fenetre.fetch(url).then(function (r) {
      if (!r.ok) throw new Error(quoi + ' ' + r.status);
      return lireEnSuivant(r, suivi);
    });
  }

  /** Le corps d'une reponse JSON, en disant ou on en est : `suivi(0..1)`.

      ⚠️ On compte les octets DECOMPRESSES que lit le navigateur contre ceux que
      le serveur annonce (`X-Octets`, voir `routes._revalide`) : derriere nginx,
      la longueur de la reponse est celle du gzip, et la barre avancerait au
      juge. Sans l'en-tete ou sans flux lisible (un vieux navigateur, le banc
      d'essai), on lit d'un coup : la barre saute, elle ne ment pas. */
  function lireEnSuivant(r, suivi) {
    const total = Number(r.headers && r.headers.get && r.headers.get('X-Octets')) || 0;
    const Decodeur = fenetre.TextDecoder;
    if (!suivi || !total || !r.body || !r.body.getReader || !Decodeur) return r.json();
    const lecteur = r.body.getReader(), morceaux = [];
    let recus = 0;
    function lire() {
      return lecteur.read().then(function (m) {
        if (m.done) {
          const tout = new Uint8Array(recus);
          let k = 0;
          morceaux.forEach(function (c) { tout.set(c, k); k += c.length; });
          return JSON.parse(new Decodeur('utf-8').decode(tout));
        }
        morceaux.push(m.value);
        recus += m.value.length;
        suivi(Math.min(1, recus / total));
        return lire();
      });
    }
    return lire();
  }

  /** Les definitions et la carte : DEUX requetes, lancees ensemble, et la carte
      remise dans `defs.carte` — tout ce qui lit la carte la lit la ou elle a
      toujours ete.

      ⚠️ La carte est sortie du paquet le 16 sept. 2026 (le paquet touchait son
      plafond de 75 Ko gzip, et elle en faisait plus de la moitie).
      ⚠️ Les deux reponses doivent etre de la MEME construction : les
      definitions nomment l'empreinte de leur carte. Un deploiement tombe entre
      les deux requetes donnerait une carte d'une autre ville — des portes et
      des missions qui ne se parlent plus. On refuse, et la page dit de
      recharger. */
  function chargerDefinitions(racine) {
    // ⚠️ La barre reprend ou `chargement.js` l'a laissee (les scripts), et garde
    // ses cinq derniers pour la ville qui se batit. Entre les deux, les deux
    // requetes a la mesure de leur poids sur le fil : la carte 42 Ko gzip, les
    // definitions 33 (mesure du 17 sept. 2026).
    const depart = Hud.partDesScripts(), arrivee = 95;
    const parts = { definitions: 0, carte: 0 };
    function suivre(quoi, poids) {
      return function (f) {
        parts[quoi] = f * poids;
        Hud.progression(depart + (arrivee - depart) * (parts.definitions + parts.carte));
      };
    }
    return Promise.all([
      chargerJson(racine.dataset.urlDefinitions, 'definitions', suivre('definitions', 0.45)),
      chargerJson(racine.dataset.urlCarte, 'carte', suivre('carte', 0.55)),
    ]).then(function (reponses) {
      const defs = reponses[0], carte = reponses[1];
      if (carte.empreinte !== defs.carte_empreinte) {
        throw new Error('carte ' + carte.empreinte + ' au lieu de ' + defs.carte_empreinte);
      }
      defs.carte = carte;
      return defs;
    });
  }

  /** Un gel qui ne vient pas de la boucle de jeu (decodage audio, GC, un
      `fetch` qui bloque) ne passe jamais par `avancer()` — la Long Tasks API
      le voit quand meme : elle signale TOUT ce qui bloque le fil principal
      plus de 50ms, quelle qu'en soit la cause. Absente de Safari et Firefox
      (avril 2026) : `pas()`/`signalerGel` restent le filet la ou elle manque. */
  function surveillerLesGels(w) {
    if (!w.PerformanceObserver) return;
    try {
      new w.PerformanceObserver(function (liste) {
        liste.getEntries().forEach(function (e) {
          if (typeof console !== 'undefined' && console.warn) {
            console.warn('[gel] tache longue ' + Math.round(e.duration) + 'ms — ' + contexteGel());
          }
        });
      }).observe({ entryTypes: ['longtask'] });
    } catch (e) { /* entryType inconnu : rien a faire */ }
  }

  function demarrer(w, d) {
    fenetre = w; doc = d;
    const racine = d.getElementById('bandini');
    const toile = d.getElementById('toile');
    Base.initCanvas(toile, fabriqueCanvas);
    surveillerLesGels(w);
    Son.init(w, racine.dataset.urlStatique);
    // ⚠️ Lire `sessionStorage` peut LEVER (stockage bloque, navigation privee
    // de certains navigateurs) : le choix des parties s'en passe tres bien.
    let session = null;
    try { session = w.sessionStorage || null; } catch (e) { session = null; }
    Sauvegarde.init(w.localStorage, session);
    Object.assign(B.options, Sauvegarde.lireOptions() || {});
    // Les boutons de manette reappris par le joueur (ecran OPTIONS > MANETTE).
    Entree.reglerManette(B.options.manette);
    // ?trace=1 (ou ?perf=1) dans l'adresse : le mode s'allume sans passer par le menu.
    const adresse = (w.location && w.location.search) || '';
    if (/[?&]trace=1/.test(adresse)) B.options.trace = true;
    if (/[?&]perf=1/.test(adresse)) B.options.perf = true;
    Entree.init(d, w, w.navigator);
    Entree.surSecret(SEQUENCE_DEBUG, ouvrirMenuDebug);
    Entree.surSuiteActions(SEQUENCE_DEBUG_ACTIONS, ouvrirMenuDebug);
    Hud.init(d, racine);
    B.rng = mulberry(B.graine);

    function redim() { Base.redimensionner(w, Entree.estTactile); }
    w.addEventListener('resize', redim);
    w.addEventListener('orientationchange', function () { setTimeout(redim, 120); });
    if (w.visualViewport) w.visualViewport.addEventListener('resize', redim);
    // ⚠️ Sauf dans le casque : la page 2D peut s'y dire cachee pendant qu'on joue
    // dedans. C'est alors la session qui dit si on la regarde (`Casque`).
    d.addEventListener('visibilitychange', function () {
      if (d.hidden && !(typeof Casque !== 'undefined' && Casque.actif)) { pause(); Son.suspendre(); }
      // Une page rouverte le lendemain matin ne doit pas annoncer le defi d'hier.
      else if (!d.hidden) Defi.rafraichir();
    });
    // ⚠️ La page s'en va : on rend la carte son — mais SEULEMENT si elle ne peut
    // pas revenir. `persisted` dit que le navigateur la met de cote (bfcache,
    // le geste le plus banal sur telephone : changer d'application). Fermer
    // dans ce cas-la viderait les sons decodes et la page reviendrait muette.
    w.addEventListener('pagehide', function (ev) {
      if (ev && ev.persisted) return;
      Son.fermer();
      // ⚠️ `sendBeacon`, pas `fetch` : une requete ordinaire lancee pendant que
      // la page s'en va se fait couper — sur telephone, changer d'application
      // EST la facon normale de quitter le jeu.
      Compte.partir();
    });
    d.addEventListener('pointerdown', function () { Son.reveiller(); Hud.majAvisSon(); }, { passive: true });
    d.addEventListener('keydown', function () { Son.reveiller(); Hud.majAvisSon(); }, { passive: true });
    // On sonde tout de suite : le contexte naît « suspended » si la page n'a
    // recu aucun geste, et c'est la seule facon de savoir — avant de jouer —
    // qu'on va jouer en silence.
    Son.surEtat(function () { Hud.majAvisSon(); });
    Son.sonder();
    Hud.majAvisSon();
    redim();

    return chargerDefinitions(racine).then(function (defs) {
      B.defs = defs;
      Hud.progression(95);
      Monde.charger(defs.carte);
      // La partie du dernier emplacement joue : celle que JOUER propose d'abord.
      B.partie = chargerPartie(Sauvegarde.emplacement());
      const app = defs.carte.apparition.joueur;
      Monde.centrerCamera(app.x * TT, app.y * TT);
      B.etat = 'titre';
      Hud.etat('titre');
      Hud.voile('titre');
      // ⚠️ Le theme se DEMANDE ici, mais il ne sortira qu'au premier geste :
      // tant que le navigateur retient le son, `Mus.tick()` se contente
      // d'avancer son compteur. C'est le bandeau du titre qui reclame ce geste.
      Son.Mus.jouer('titre');
      // ⚠️ L'ouverture est le SEUL son qu'il faut avoir avant de le jouer : elle
      // commence a la seconde ou l'on presse JOUER, et un narrateur qui arrive
      // trois phrases en retard ne raconte plus rien. Tout le reste de l'audio
      // se charge a l'usage (12 Mo en 166 fichiers), et doit le rester.
      Son.prechauffer(Histoire.fichiersDeLOuverture());
      // Le bouton JOUER DANS LE CASQUE : seulement une fois la ville chargee, et
      // seulement si le navigateur ouvre une session immersive.
      Casque.init(d, w, w.navigator);
      // LE COMPTE (M14) : l'ouverture part ICI, une fois la ville batie — elle ne
      // retarde pas le chargement d'une milliseconde, et sa reponse arrive
      // pendant qu'on lit l'ecran titre. ⚠️ Rien n'attend apres elle : serveur
      // eteint, wifi coupe, base tombee, on joue pareil.
      Compte.init(w, racine);
      Compte.surChangement(function (vue, recue) {
        // Une partie qui DESCEND du compte remplace celle qu'on a en memoire.
        // ⚠️ C'est `Compte.poser` qui refuse d'ecrire quoi que ce soit sous les
        // pieds de quelqu'un qui joue — une garde de plus ici ne serait jamais
        // exercee, donc jamais jugee, et elle mentirait le jour ou l'autre tombe.
        if (recue && recue === Sauvegarde.emplacement()) B.partie = chargerPartie(recue);
      });
      // LE DEFI DU JOUR (M14, 5e vague) : une demande, et rien n'attend sa reponse. ⚠️ Sans
      // reseau, pas de defi du jour — et le jeu ne s'en apercoit pas.
      Defi.init(w, racine);
      const etat = d.getElementById('etat-chargement');
      const parties = Sauvegarde.occupes().length;
      if (etat) etat.textContent = 'v' + defs.version + ' · ' + (B.partie.x !== null ? 'partie ' + Sauvegarde.emplacement() + ', jour ' + B.partie.jour : 'nouvelle partie')
        + (parties > 1 ? ' · ' + parties + ' parties sauvegardées' : '');
      // On revient d'un changement de partie : le choix se rouvre sur elle.
      // La ville est batie : la barre fait son dernier pas, et s'efface.
      Hud.progression(100);
      Hud.finirChargement();
      const rouvrir = Sauvegarde.rouverture();
      if (rouvrir) ouvrirParties(rouvrir);
      dernier = 0; accu = 0;
      fenetre.requestAnimationFrame(boucle);
      return defs;
    }).catch(function (err) {
      horsLigne = true;
      const etat = d.getElementById('etat-chargement');
      if (etat) etat.textContent = 'Impossible de charger la ville. Recharge la page.';
      throw err;
    });
  }

  return { demarrer, commencer, jouer, ouvrirParties, jouerPartie, effacerPartie, copierPartie, entrer, sortir, changerEtage, coucherALHopital, quitterLaPiece, transiter, finirTransition, pause, reprendre, basculerPause, ouvrirCarte, fermerCarte, ouvrirPhoto, fermerPhoto, basculerCoop, retourTitre, maj, rendre, avancer, get horsLigne() { return horsLigne; } };
})();

/* Surface de test et de debogage — la seule poignee du banc d'essai. */
if (typeof window !== 'undefined') {
  window.BANDINI = {
    B: B, VW: VW, VH: VH, TT: TT,
    Base: Base, Atlas: Atlas, Entree: Entree, Son: Son, Chargements: Chargements, Monde: Monde, Entites: Entites, Combat: Combat,
    Vehicules: Vehicules, Autobus: Autobus, Metro: Metro, Traversier: Traversier, Neige: Neige, Incendies: Incendies, Interactions: Interactions, Police: Police, Chantiers: Chantiers, Aeroport: Aeroport, Foire: Foire, Missions: Missions, Scenes: Scenes, Histoire: Histoire, Hud: Hud, Casque: Casque, Jeu: Jeu, Sauvegarde: Sauvegarde, Compte: Compte, Defi: Defi,
    SPRITES: SPRITES, TUILES: TUILES, DECORS: DECORS, DECALS: DECALS, OBJETS: OBJETS, FACADES: FACADES,
    ETOILE: ETOILE,
    BULLES: BULLES, POLICE_PIXEL: POLICE_PIXEL, MARQUES_PIXEL: MARQUES_PIXEL,
    etatInitial: etatInitial, mulberry: mulberry, hash2: hash2, nuances: nuances, faceA: faceA,
    graine: function (n) { B.graine = n; B.rng = mulberry(n); },
    entree: function (a) { const s = Entree._sacs(); return { bas: Entree.bas(a), pad: !!s.vPad[a], tactile: !!s.vTact[a], axe: Entree.axe }; },
  };
  if (typeof document !== 'undefined' && document.getElementById && document.getElementById('bandini')) {
    if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', function () { Jeu.demarrer(window, document); });
    else Jeu.demarrer(window, document);
  }
}
