/* Bandini — police : ce qu'elle voit, ce qu'elle retient, comment elle repond.

   Trois canaux de detection, et rien n'est compte tant que rien n'est detecte :
   le CONE d'un agent (il voit le crime, ou te voit quand tu es recherche), le
   TEMOIN (un passant court le raconter a un agent, ou telephone) et l'ALARME
   (un char qui hurle, dans un rayon). La machine de recherche (chaleur,
   etoiles, decroissance hors de vue) vit ici ; les agents sont des pietons
   (`agent: true`) que ce module dirige quand ils poursuivent ou enquetent,
   et laisse flaner sinon — ils respectent les trottoirs comme tout le monde.

   Les autos de patrouille sont des chars a conducteur `police`, pilotes ici
   avec la physique du joueur : elles peuvent VRAIMENT te rentrer dedans. */

const Police = (function () {
  'use strict';

  const PALETTE_AGENT = { c: '#1f3a6e', p: '#16264a', h: '#101018', s: '#e8b088' };
  //: Le vigile prive (infiltration) : un uniforme d'entreprise, pas le bleu marine
  //: de la police — pour qu'on le reconnaisse avant meme qu'il se retourne.
  const PALETTE_GARDE = { c: '#5a5f47', p: '#3a3d33', h: '#2a2a2a', s: '#c98d66' };

  function defs() { return B.defs.recherche; }
  function reglages() { return B.defs.recherche.police; }
  function palier() { return defs().paliers[Math.min(B.recherche.etoiles, defs().etoiles_max)]; }
  /** Le palier dont le poste a DEJA envoye les renforts (`majRenforts`) : c'est lui, et
      pas les etoiles, qui dit combien d'agents, d'autos, d'helicos et de barrages viennent.
      ⚠️ Pas encore de compte, pas encore de renforts : un `undefined` lu comme les
      etoiles les faisait arriver a l'image meme. */
  function palierDesRenforts() {
    const r = B.recherche;
    return defs().paliers[Math.min(r.renforts || 0, r.etoiles, defs().etoiles_max)];
  }

  /** L'agent en (ax, ay) regardant vers `angle` voit-il (x, y) ? Cone + portee ; la ligne de vue est a part. */
  function dansLeCone(ax, ay, angle, demiAngleRad, portee, x, y) {
    const d2 = dist2(ax, ay, x, y);
    if (d2 > portee * portee) return false;
    if (d2 < 1) return true;
    return Math.abs(ecartAngle(angle, angleVers(ax, ay, x, y))) <= demiAngleRad;
  }

  /** De combien la portee s'allonge quand on cherche LE JOUEUR.

      ⚠️ Un casier epais se voit de loin — c'est la premiere ligne de M11, et la
      seule facon de faire peser un casier autrement qu'au comptoir des
      amendes. Vingt pages ne changent rien a ce qu'on lit dans le HUD ; elles
      changent la distance a laquelle on se fait reconnaitre.

      ⚠️ ET SEULEMENT POUR LUI : un casier epais n'aide pas la police a voir les
      passants. C'est un signalement, une photo au mur, pas une paire de
      jumelles.

      ⚠️ Le plafond vient de la fiche et il est la REGLE, pas le detail : sans
      lui, vingt pages feraient voir la police a seize tuiles en pleine nuit, et
      il n'y aurait plus une ruelle ou souffler. */
  function porteeDuCasier() {
    const v = defs().vision;
    const casier = (B.partie && B.partie.casier) || 0;
    const plafond = v.casier_portee_max === undefined ? 1.5 : v.casier_portee_max;
    const parPage = v.casier_portee_par_page || 0;
    return Math.min(plafond, 1 + parPage * Math.max(0, casier));
  }

  function voit(agent, x, y, genre, reconnait) {
    const vision = defs().vision[genre || 'policier'];
    const nuit = Monde.estNuit();
    const portee = (nuit ? vision.nuit : vision.jour) * TT * (reconnait ? porteeDuCasier() : 1);
    if (!dansLeCone(agent.x, agent.y, agent.angle, vision.angle * Math.PI / 180, portee, x, y)) return false;
    return Monde.ligneLibre(agent.x, agent.y, x, y);
  }

  function agents() {
    return B.entites.filter(function (e) { return e.agent && e.vivant && e.etat !== 'assomme'; });
  }

  /** Un temoin voit-il ce qui se passe ici ? (`sauf` = la victime elle-meme.)

      ⚠️ C'est LA regle du jeu : rien n'est compte tant que ce n'est pas vu.
      Un pieton assomme ou mort ne temoigne pas, et un mur suffit a tout
      cacher. Un agent qui voit, lui, compte pour deux : il se lance. */
  function quelqu_un_voit(x, y, sauf) {
    for (const a of agents()) {
      if (voit(a, x, y, 'policier')) { alerterAgent(a, x, y); return true; }
    }
    const rayon = defs().temoins.rayon_tuiles * TT;
    const vision = defs().vision.pieton;
    const portee = (Monde.estNuit() ? vision.nuit : vision.jour) * TT;
    const demi = vision.angle * Math.PI / 180;
    for (const e of Entites.pietonsAutour(x, y, Math.min(rayon, portee))) {
      if (e === sauf || !e.vivant || e.etat === 'assomme' || e.aveugle > 0 || e.agent) continue;
      if (!dansLeCone(e.x, e.y, e.angle, demi, portee, x, y)) continue;
      if (!Monde.ligneLibre(e.x, e.y, x, y)) continue;
      return true;
    }
    return false;
  }

  /** Le joueur est-il sur l'ile — dehors, ou dans une de ses pieces ?

      ⚠️ `refuge` est une propriete de la ZONE (`ile.zone()`), pas un slug : le
      jour ou un autre endroit echappe a la police, c'est sa fiche qui le dit.
      ⚠️ Dedans, la carte active est la piece, et une piece n'a pas de zones :
      on lit la rue qu'on a laissee derriere la porte. */
  function auRefuge() {
    const j = B.joueur, ext = B.exterieur;
    if (!j) return false;
    const carte = ext ? ext.carte : Monde.carte;
    const x = ext ? ext.x : j.x, y = ext ? ext.y : j.y;
    let trouvee = null;
    for (const z of (carte && carte.zones) || []) {
      if (x >= z.x * TT && x < (z.x + z.l) * TT && y >= z.y * TT && y < (z.y + z.h) * TT) trouvee = z;
    }
    return !!(trouvee && trouvee.refuge);
  }

  /** CE QUE LA POLICE DIT A LA RADIO quand les etoiles changent (M15, `Son.Ondes`) :
      repere a la premiere, la poursuite quand les autos s'en melent, perdu quand
      la derniere tombe. ⚠️ Un saut de zero a trois dit « poursuite » : c'est le
      plus grave des deux, et le scanner n'en dit qu'un a la fois. */
  function annoncer(avant) {
    const r = B.recherche, d = defs();
    const autos = function (n) { return (d.paliers[Math.min(n, d.etoiles_max)] || {}).autos || 0; };
    if (r.etoiles > avant && !autos(avant) && autos(r.etoiles)) Son.Ondes.police('poursuite');
    else if (avant === 0 && r.etoiles > 0) Son.Ondes.police('repere');
    else if (avant > 0 && r.etoiles === 0) Son.Ondes.police('perdu');
  }

  function ajouterChaleur(gravite) {
    // ⚠️ SUR L'ILE, RIEN NE FAIT MONTER LES ETOILES : ni un crime vu, ni un
    // temoin qui appelle. C'est la seule regle de l'ile, et elle vaut tout le
    // reste de sa fiche — on peut y laisser refroidir un char et un casier.
    if (auRefuge()) return;
    const r = B.recherche, d = defs(), avant = r.etoiles;
    r.chaleur += gravite * d.chaleur_par_gravite;
    r.repitChaleur = d.chaleur_repit_s * 60;          // la jauge ne refroidit qu'apres ce repit (`refroidir`)
    while (r.chaleur >= d.chaleur_etoile && r.etoiles < d.etoiles_max) {
      r.chaleur -= d.chaleur_etoile;
      r.etoiles++;
      r.vu = 0;
      r.flash = 60;
      Son.SFX.etoile();
    }
    if (r.etoiles >= d.etoiles_max) r.chaleur = 0;
    annoncer(avant);
  }

  /** Un crime commis. `vu` : quelqu'un (agent ou passant) l'a vu.

      Il COMPTE tout de suite si un agent l'a vu, ou s'il est bruyant (`temoin:
      false` au catalogue : carjacking, coup de feu, explosion — tout le monde
      l'entend). Sinon, les passants qui l'ont vu deviennent des TEMOINS
      porteurs de ce crime : ils courent le raconter a un agent, ou
      telephonent — et d'ici la, on peut leur acheter le silence. */
  function signalerCrime(type, x, y, vu) {
    const delit = defs().delits[type];
    if (!delit) return null;
    // ⚠️ `a.genreVision` : un vigile prive (infiltration) n'a pas le cone d'un
    // policier — voir `VISION.garde`. Sans defaut, tout agent qui n'est pas
    // un vrai policier deviendrait aveugle.
    const parAgent = agents().some(function (a) { return voit(a, x, y, a.genreVision || 'policier'); });
    const compte = parAgent || (!!vu && !delit.temoin);
    const crime = { type: type, gravite: delit.etoiles, temoin: delit.temoin, x: x, y: y, t: B.t, vu: !!vu, rapporte: false };
    B.crimes.push(crime);
    if (B.crimes.length > 40) B.crimes.shift();
    B.partie.stats.crimes++;
    if (compte) {
      // ⚠️ UN CARAMBOLAGE EST UN DELIT, PAS TROIS (`repit_s` au catalogue) : le meme
      // delit, compte de nouveau avant le repit, ne chauffe pas une deuxieme fois. Le
      // repit part du dernier qui a CHAUFFE — il ne glisse pas, sinon on conduirait
      // comme un fou sans jamais rien payer. (Un `B.t` plus petit que le souvenir :
      // une partie neuve, et rien n'est une redite.)
      const r = B.recherche, dernier = (r.redites || {})[type];
      const redite = !!delit.repit_s && dernier !== undefined && B.t - dernier >= 0 && B.t - dernier < delit.repit_s * 60;
      if (!redite) { ajouterChaleur(delit.etoiles); if (delit.repit_s) (r.redites = r.redites || {})[type] = B.t; }
      crime.rapporte = true; r.dernierVu = { x: x, y: y, t: B.t };
    }
    // Les temoins : ceux qui ont VU (dans leur cone, rien devant) et qui ont le
    // coeur de le dire. La victime d'un pickpocket, de dos, n'a rien vu.
    const t = defs().temoins, vision = defs().vision.pieton;
    const portee = (Monde.estNuit() ? vision.nuit : vision.jour) * TT, demi = vision.angle * Math.PI / 180;
    for (const e of Entites.pietonsAutour(x, y, Math.min(t.rayon_tuiles * TT, portee))) {
      if (!e.vivant || e.agent || e.intouchable || e.metier || e.etat === 'assomme') continue;
      if (!dansLeCone(e.x, e.y, e.angle, demi, portee, x, y) || !Monde.ligneLibre(e.x, e.y, x, y)) continue;
      if (B.rng() < e.probaTemoin) { e.etat = 'temoin'; e.crime = crime; e.menace = B.joueur; e.minuterie = t.oubli_s * 60; e.cri = 120; }
    }
    return crime;
  }

  /** LE CRIME D'AUTRUI (M12) : un passant confond le joueur avec le vrai coupable.

      ⚠️ Rare (`autrui.chance`, tiree a l'EMPREINTE de l'image et du coupable : aucun
      de), lisible (la scene est a l'ecran, et le vrai coupable avec — le pickpocket qui
      file, la victime qui crie « au voleur »), et JAMAIS au-dela de `autrui.rayon_px` :
      un joueur qui n'y est pour rien et qui se tient loin ne recoit rien. Le passant
      qui te designe doit te VOIR, pas le coupable ; il crie, et la suite est la
      machine des temoins — il court le dire a un agent, et on lui achete le silence.
      Au volant, on passe : personne ne confond un char avec un voleur a pied. */
  function crimeDAutrui(type, x, y, coupable) {
    const r = defs().autrui, delit = defs().delits[type], j = B.joueur;
    if (!r || !delit || !j || !j.vivant || B.interieur || j.dansVehicule) return null;
    if (Math.hypot(j.x - x, j.y - y) > r.rayon_px) return null;
    if (!Entites.visibleAEcran(x, y, 0)) return null;
    if (B.recherche.autruiT !== undefined && B.t - B.recherche.autruiT < r.repos_s * 60) return null;
    if (hash2(B.t, coupable && coupable.id || 0) % 1000 >= r.chance * 1000) return null;
    let temoin = null, dMin = Infinity;
    for (const e of Entites.pietonsAutour(x, y, r.temoin_px)) {
      if (e === coupable || !e.vivant || e.agent || e.intouchable || e.metier || e.gang) continue;
      if (e.etat === 'assomme' || e.etat === 'temoin' || e.bagarre) continue;
      // ⚠️ La VICTIME ne se trompe pas de coupable : elle fuit celui qui l'a volee, et
      // c'est lui qu'elle designe (« AU VOLEUR! »). Sans cette ligne, c'est elle — la plus
      // proche de la scene — qui te montrait du doigt.
      if (coupable && e.menace === coupable) continue;
      if (!Monde.ligneLibre(e.x, e.y, j.x, j.y)) continue;
      const d = Math.hypot(e.x - x, e.y - y);
      if (d < dMin) { dMin = d; temoin = e; }
    }
    if (!temoin) return null;
    const crime = { type: type, gravite: delit.etoiles, temoin: true, x: j.x, y: j.y, t: B.t, vu: true, rapporte: false, autrui: true };
    B.crimes.push(crime);
    if (B.crimes.length > 40) B.crimes.shift();
    const t = defs().temoins;
    temoin.etat = 'temoin'; temoin.crime = crime; temoin.menace = j; temoin.minuterie = t.oubli_s * 60; temoin.cri = 120;
    Entites.regarder(temoin, j.x - temoin.x, j.y - temoin.y);
    Entites.bulle(temoin, r.cri, { duree: 150 });
    B.recherche.autruiT = B.t;
    return crime;
  }

  /** Un temoin arrive a un agent (ou telephone) : le crime est connu. */
  function rapporter(crime, agent) {
    if (!crime || crime.rapporte) return false;
    crime.rapporte = true;
    ajouterChaleur(crime.gravite);
    B.recherche.dernierVu = { x: crime.x, y: crime.y, t: B.t };
    if (agent) { agent.etat = 'enquete'; agent.but = { x: crime.x, y: crime.y }; agent.chemin = null; agent.enqueteT = 180; }
    return true;
  }

  /** On achete le silence d'un temoin : il oublie ce qu'il a vu. */
  function acheterLeSilence(j, temoin) {
    const prix = B.defs.economie.tarifs.silence_temoin;
    if (!temoin || temoin.etat !== 'temoin' || !temoin.crime || temoin.crime.rapporte) return false;
    if (B.partie.argent < prix) { Hud.message(prix + ' $ — PAS ASSEZ'); Son.SFX.erreur(); return true; }
    Missions.payer(prix, 'SILENCE');
    temoin.crime = null; temoin.etat = 'flane'; temoin.cri = 0; temoin.menace = null;
    Hud.message('IL N’A RIEN VU');
    return true;
  }

  // --- Le stool : celui qui n'a rien vu, et qui te reconnait quand meme ------

  /** ⚠️ **Ce n'est pas un temoin, et la difference est tout le personnage.** Le
      temoin porte un CRIME : il a vu quelque chose, il court le raconter, son
      silence vaut vingt piastres. Le stool n'a rien vu — il a reconnu ta FACE,
      parce que ta face est dans le journal et sur les affiches. Il n'a besoin
      d'aucun delit, il va telephoner, et ce qu'il donne au poste n'est pas de
      la chaleur : c'est un SIGNALEMENT, donc un PLANCHER d'etoiles.

      C'est ce qui referme M11 : la premiere vague a fait que le dossier allonge
      le cone des agents, celle-ci fait qu'il transforme les passants en
      delateurs. */
  function ficheStool() { return defs().stool; }

  /** Un stool en route, c'est un stool qui a une porte. Assomme, il perd sa
      porte (`majPorte`) — et il cesse donc d'en etre un. */
  function estStool(e) { return !!(e && e.stool && e.vivant && e.porteBut); }

  function leStool() { return B.entites.find(estStool) || null; }

  /** Ce que coute son silence. ⚠️ Il sait ce que tu vaux : le prix monte avec
      le dossier, comme l'amende, comme l'avocat, comme tout ce qui touche au
      casier. */
  function prixDuStool() {
    const f = ficheStool(), eco = B.defs.economie;
    const casier = Math.max(0, Math.min(eco.casier_max, B.partie.casier));
    return Math.round(f.prix + f.prix_par_page * casier);
  }

  /** ⚠️ IL NE NAIT JAMAIS DANS TON DOS. Il faut pouvoir le voir se retourner et
      partir : une denonciation qu'on ne peut pas voir venir n'est pas une
      regle, c'est une taxe. Et un seul a la fois — sans ca, la rue entiere se
      relaie au telephone et le casier devient une condamnation. */
  function majStools() {
    const f = ficheStool(), j = B.joueur, r = B.recherche;
    if (!j || !j.vivant || B.interieur || j.dansVehicule) return;
    if (B.partie.casier < f.casier_minimum) return;
    if (B.t < (r.stoolT || 0) || B.t % f.occasion_images !== 0) return;
    if (leStool()) return;
    if (B.rng() >= Math.min(f.chance_max, f.chance_par_page * B.partie.casier)) return;
    const portee = f.rayon_tuiles * TT, demi = f.devant_degres * Math.PI / 360;
    const gens = Entites.pietonsAutour(j.x, j.y, portee).filter(function (e) {
      return e.vivant && !e.agent && !e.metier && !e.personnage && !e.mission
        && !e.intouchable && !e.petit && !e.suit && !e.gang && !e.porteBut
        && (e.etat === 'flane' || e.etat === 'arret')
        && dansLeCone(j.x, j.y, j.angle, demi, portee, e.x, e.y)
        && Monde.ligneLibre(j.x, j.y, e.x, e.y);
    });
    if (!gens.length) return;
    const e = gens[Math.floor(B.rng() * gens.length)];
    // Pas de porte a portee : pas de telephone, donc pas de stool.
    if (!Entites.envoyerAUnePorte(e)) return;
    e.stool = true;
    e.etat = 'flane';
    Entites.bulle(e, ficheStool().dit.reconnait, { duree: 150 });
    Hud.message('QUELQU’UN T’A RECONNU');
  }

  /** Il a passe la porte : le poste a ton signalement. ⚠️ `dernierVu` tombe SUR
      LE SEUIL, pas sur toi — c'est ce qu'il a donne, et c'est la que les autos
      vont chercher. On a donc encore quelques secondes pour ne plus y etre. */
  function appelDuStool(e) {
    const f = ficheStool();
    e.stool = false;
    B.recherche.stoolT = B.t + f.repit_s * 60;
    B.recherche.dernierVu = { x: e.x, y: e.y, t: B.t };
    etoilesAuMoins(f.etoiles);
    Hud.message('ON T’A DÉNONCÉ');
  }

  /** Du linge neuf, une coupe : on ne te reconnait plus pendant un moment.

      ⚠️ C'est le SEUL levier que le joueur ait vraiment contre le stool — le
      casier, lui, ne redescend qu'en payant l'avocat ou le comptoir du fond.
      Sans ca, un gros dossier n'etait plus une regle : c'etait une taxe qu'on
      paie jusqu'a la fin de la partie. Et celui qui etait deja en route
      raccroche : il cherchait une tete qui n'existe plus. */
  function onNeTeReconnaitPlus() {
    const f = ficheStool();
    B.recherche.stoolT = B.t + f.repit_deguisement_s * 60;
    const e = leStool();
    if (e) { e.stool = false; e.porteBut = null; e.porteT = 0; }
  }

  /** On l'achete. ⚠️ Plus cher que le silence d'un temoin, et c'est voulu : le
      temoin marchande ce qu'il a vu, le stool marchande QUI TU ES. */
  function acheterLeStool(j, stool) {
    if (!estStool(stool)) return false;
    const prix = prixDuStool();
    if (B.partie.argent < prix) { Hud.message(prix + ' $ — PAS ASSEZ'); Son.SFX.erreur(); return true; }
    Missions.payer(prix, 'SILENCE');
    stool.stool = false; stool.porteBut = null; stool.porteT = 0;
    B.recherche.stoolT = B.t + ficheStool().repit_s * 60;
    Entites.bulle(stool, ficheStool().dit.achete, { duree: 120 });
    return true;
  }

  function remiseAZero() { const r = B.recherche; r.etoiles = 0; r.chaleur = 0; r.vu = 0; }

  /** Un PLANCHER d'etoiles, tout de suite.

      ⚠️ La chaleur est une moyenne : un delit de gravite 1 pose 35 points, et
      il en faut 100 pour une etoile — trois delits, donc. C'est ce qu'on veut
      pour ce qu'on voit dans la rue, et c'est exactement ce qu'on ne veut pas
      pour un TELEPHONE : quand la fourriere appelle, elle ne « chauffe » pas
      l'ambiance, elle donne un signalement. Le plancher est la difference
      entre « quelqu'un a vu » et « quelqu'un a appele ». */
  function etoilesAuMoins(n) {
    if (auRefuge()) return false;                 // personne n'appelle la police de l'ile
    const r = B.recherche, d = defs();
    const voulu = Math.min(n, d.etoiles_max);
    if (r.etoiles >= voulu) return false;
    const avant = r.etoiles;
    r.etoiles = voulu;
    r.chaleur = 0; r.vu = 0; r.flash = 60;
    Son.SFX.etoile();
    annoncer(avant);
    return true;
  }

  // --- Les agents ------------------------------------------------------------------

  /** Un agent que `gere()` dirige : un vrai policier par defaut, ou — `genre:
      'garde'` — un vigile prive (infiltration). ⚠️ Meme moteur, un cone et une
      palette differents : `a.genreVision` est ce que `voit()`/`signalerCrime`
      lisent pour savoir a quelle fiche de `VISION` se fier ; sans lui, un
      garde verrait comme un policier (le defaut de `voit`), pas comme un
      vigile. Un garde ne nait jamais du budget de patrouille de la ville
      (`peuplerAgents`) : c'est une mission qui le pose, a la main. */
  function creerAgent(x, y, etat, genre) {
    const estGarde = genre === 'garde';
    const arch = Entites.archetype(estGarde ? 'garde' : 'policier');
    const a = Entites.creerPieton(x, y, arch);
    a.agent = true; a.metier = estGarde ? 'garde' : 'police';
    a.genreVision = estGarde ? 'garde' : 'policier';
    a.swaps = Object.assign({}, estGarde ? PALETTE_GARDE : PALETTE_AGENT);
    // ⚠️ `vuT` = depuis combien de temps il ne te voit plus. Un agent qui nait
    // EN POURSUITE te voit, par definition : a 9999 il abandonnait des la
    // premiere image, avant meme d'avoir regarde.
    a.arme = estGarde ? 'batte' : 'pistolet'; a.etat = etat || 'flane'; a.chemin = null; a.cheminT = 0; a.tirT = 0;
    a.vuT = a.etat === 'poursuit' ? 0 : 9999;
    return a;
  }

  function alerterAgent(a, x, y) {
    if (a.etat === 'poursuit') return;
    a.etat = 'enquete'; a.but = { x: x, y: y }; a.chemin = null; a.enqueteT = 240;
  }

  /** Un coup de feu S'ENTEND : chaque agent a moins de `rayon` px — sans cone,
      sans ligne de vue — part voir d'ou ca venait. Sans etoile : il n'a rien
      VU. C'est la parade au tireur embusque, la meme que pour le char rapide
      (le cone n'est pas le seul sens) : la distance achete du temps, pas
      l'impunite. Et si tu es deja recherche, le coup dit ou tu es. Rend le
      nombre d'agents qui l'ont entendu. */
  function entendre(x, y, rayon) {
    let n = 0;
    for (const a of agents()) {
      if (dist2(a.x, a.y, x, y) > rayon * rayon) continue;
      n++;
      alerterAgent(a, x, y);
    }
    if (n && B.recherche.etoiles > 0) B.recherche.dernierVu = { x: x, y: y, t: B.t };
    return n;
  }

  /** Suit un chemin (liste de centres de tuiles) vers `but`. Rend true si arrive. */
  function suivre(a, but, vitesse) {
    const p = reglages();
    if (a.cheminT-- <= 0 || !a.chemin) {
      a.cheminT = p.chemin_toutes_les_images;
      // ⚠️ MASQUE_A_PIED, pas MASQUE_PIETON : un agent sait enjamber un
      // grillage, exactement comme le joueur et au meme prix. Sinon la premiere
      // cloture venue gagne toutes les poursuites.
      Monde.demanderChemin(a.x, a.y, but.x, but.y, Monde.MASQUE_A_PIED, function (chemin) { a.chemin = chemin; });
    }
    let cible = but;
    if (a.chemin && a.chemin.length) {
      while (a.chemin.length && dist2(a.x, a.y, a.chemin[0].x, a.chemin[0].y) < 36) a.chemin.shift();
      if (a.chemin.length) cible = a.chemin[0];
    }
    const dx = cible.x - a.x, dy = cible.y - a.y, d = Math.hypot(dx, dy);
    if (d < 2) { a.vx = 0; a.vy = 0; return true; }
    a.vx = dx / d * vitesse; a.vy = dy / d * vitesse;
    // Une cloture sur le chemin : il l'enjambe, et il y perd le meme temps que
    // nous. Une poursuite ne se gagne donc pas en escaladant.
    if (Entites.enjamber(a, a.vx, a.vy)) return false;
    // ⚠️ L'agent porte le masque du NAGEUR : sinon l'eau serait l'exploit
    // anti-police le plus simple du jeu — deux pas dans la baie, et on est
    // intouchable. Il nage a la vitesse de la nage comme tout le monde
    // (`majPieton`), et son chemin paie l'eau au prix fort (`coutEau`).
    Entites.mouiller(a);
    Entites.deplacerCercle(a, a.vx, a.vy, Monde.MASQUE_NAGEUR);
    Entites.dansLaCarte(a);
    a.anim.dist += vitesse;
    Entites.regarder(a, dx, dy);
    return false;
  }

  /** Rend true quand la police dirige cet agent (sinon il flane comme un pieton). */
  function gere(a) {
    const j = B.joueur, r = B.recherche, p = reglages(), v = defs().vitesses;
    if (!a.vivant || a.etat === 'assomme' || a.recul > 0) return false;
    if (a.enjambe) { a.vx = 0; a.vy = 0; return true; }        // il est en haut d'une cloture
    if (a.etat === 'attaque') { a.vx = 0; a.vy = 0; return true; }        // il tire : Combat mene la phase
    if (a.etat === 'attaque_joueur') a.etat = 'poursuit';                 // Combat rend la main : on reprend la chasse
    if (a.etat === 'fuit' || a.etat === 'temoin') a.etat = 'poursuit';    // un agent ne fuit pas
    // ⚠️ L'AGENT QUI T'A SUIVI JUSQU'A L'ILE NE TE CHERCHE PLUS. Il ne te voit
    // pas, n'arrete personne, et redevient un passant qu'on retire hors de
    // l'ecran (`maj`). Sans ca, il suffisait d'etre nage de pres pour qu'un
    // agent remette `vu` a zero a chaque regard, et les etoiles ne tombaient
    // jamais sur l'ile.
    if (auRefuge()) {
      if (a.etat !== 'flane') { a.etat = 'flane'; a.but = null; a.chemin = null; }
      return false;
    }
    // Il rentre a son auto : rien d'autre ne le regarde tant qu'il n'y est pas (`regagner`).
    if (a.etat === 'regagne' && regagner(a)) return true;
    // Regarder : une image sur trois, c'est le budget.
    if ((B.t + a.id) % p.regarde_toutes_les_images === 0) {
      const cible = j.dansVehicule ? j.dansVehicule : j;
      if (voit(a, cible.x, cible.y, a.genreVision || 'policier', true)) {
        a.vuT = 0;
        if (r.etoiles > 0) { r.vu = 0; r.dernierVu = { x: j.x, y: j.y, t: B.t }; if (a.etat !== 'poursuit') { a.etat = 'poursuit'; a.chemin = null; a.cheminT = 0; } }
        else if (j.flagrant > 0 && a.etat !== 'poursuit') { ajouterChaleur(1); a.etat = 'poursuit'; a.chemin = null; a.cheminT = 0; }
      } else a.vuT += p.regarde_toutes_les_images;
    }
    if (a.etat === 'poursuit') {
      if (r.etoiles <= 0) { a.etat = 'flane'; return false; }
      if (a.vuT > p.poursuite_abandon_s * 60) { a.etat = 'enquete'; a.but = r.dernierVu || { x: j.x, y: j.y }; a.enqueteT = 180; a.chemin = null; return true; }
      const but = a.vuT === 0 ? { x: j.x, y: j.y } : (r.dernierVu || { x: j.x, y: j.y });
      const d = Math.hypot(j.x - a.x, j.y - a.y);
      // ⚠️ UN OTAGE DEVANT TOI, ET ILS S'ARRETENT NET. Ils ne tirent plus, ils
      // n'arretent plus, et ils RECULENT a `bouclier_recul_px`. Sans le recul,
      // le bouclier ne servait a rien : ils cessaient de tirer et venaient te
      // cueillir a la main, ce qui est pire que de tirer.
      if (j.otage && !j.dansVehicule) {
        if (d < p.bouclier_recul_px) {
          const n = Math.hypot(a.x - j.x, a.y - j.y) || 1;
          a.vx = (a.x - j.x) / n * p.auto_vitesse;
          a.vy = (a.y - j.y) / n * p.auto_vitesse;
          Entites.deplacerCercle(a, a.vx, a.vy, Monde.MASQUE_NAGEUR);
        } else { a.vx = 0; a.vy = 0; }
        Entites.regarder(a, j.x - a.x, j.y - a.y);
        return true;
      }
      // A trois etoiles, on tire.
      if (palier().tirent && a.vuT === 0 && d < p.tir_portee_tuiles * TT) {
        if (a.tirT-- <= 0) { a.tirT = p.tir_cadence_s * 60; Entites.regarder(a, j.x - a.x, j.y - a.y); Combat.tirer(a, Combat.armeDef('pistolet')); }
      }
      if (!j.dansVehicule && d < p.arrestation_px + 4) {
        a.vx = 0; a.vy = 0;
        if (!triche('pasArrete') && !j.hospitalise && !j.intouchable && !B.menu) Missions.arrestation(a);
        return true;
      }
      if (j.dansVehicule && d < 40) {
        a.vx = 0; a.vy = 0; Entites.regarder(a, j.x - a.x, j.y - a.y);
        // Un char arrete ne protege de rien : il t'en sort. ⚠️ Sauf SOUS LE TOIT d'un
        // garage : le rideau est entre vous deux, et il ne passe pas la main au travers.
        if (!triche('pasArrete') && d < 30 && Math.abs(j.dansVehicule.vitesse) < 0.5 && !j.intouchable && !B.menu
            && !Monde.rideauDe(j.dansVehicule)) { Vehicules.descendre(j, true); Hud.message('SORS DU CHAR !'); }
        return true;
      }
      suivre(a, but, v.policier);
      return true;
    }
    if (a.etat === 'enquete') {
      if (!a.but || suivre(a, a.but, v.policier * 0.8)) {
        a.vx = 0; a.vy = 0;
        a.angle += 0.05; Entites.regarder(a, Math.cos(a.angle), Math.sin(a.angle));   // il regarde autour
        if (a.enqueteT-- <= 0) { a.etat = 'flane'; a.but = null; }
      }
      return true;
    }
    return false;   // il flane : un pieton comme un autre
  }

  /** Une place de naissance pour un agent : hors ecran, sur le trottoir. */
  function placeAgent(pres) {
    for (let essai = 0; essai < 20; essai++) {
      const place = Entites.placeDeNaissance();
      if (!place) return null;
      // ⚠️ Un RENFORT arrive de la rue, pas d'une maison : `placeDeNaissance` fait
      // sortir un passant sur deux d'une porte, parfois a l'ecran, a deux pas de toi.
      if (pres && place.porte) continue;
      if (!pres || dist2(place.x, place.y, pres.x, pres.y) < 420 * 420) return place;
    }
    return null;
  }

  /** ⚠️ LA POLICE ET LE STANDING (4e vague des quartiers) : `patrouille` multiplie
      ce que la zone veut d'agents, `depeche` le delai du temoin qui telephone. Une
      ville ou l'on vole aussi tranquillement chez les riches que derriere le port
      n'a pas de quartiers — elle a des couleurs. */
  function standingIci(x, y) {
    const table = (defs().standing) || {};
    return table[Monde.standingA(Math.floor(x / TT), Math.floor(y / TT))]
      || { patrouille: 1, depeche: 1 };
  }

  /** Combien d'agents a pied cette zone veut, a cette heure et a ce standing. */
  function agentsVoulus(zone, standing) {
    const p = reglages(), table = (defs().standing) || {};
    const f = (table[standing] || { patrouille: 1 }).patrouille;
    return Math.round(Math.min(p.patrouille_par_zone_max, zone ? zone.police : 1)
                      * Monde.rythme(zone) * f) + palierDesRenforts().agents_pied;
  }

  function peuplerAgents() {
    const j = B.joueur, r = B.recherche;
    if (B.t % 30 !== 0) return;
    // ⚠️ Un bloc de carte sans passants (`bloc.gens`, la clairiere d'essai) n'a pas de
    // ronde non plus : un agent seul dans les bois ne patrouille rien. Recherche, on te
    // cherche quand meme — la poursuite qui reprend au bord est la vague 2.
    if (B.bloc && !B.bloc.def.bloc.gens && r.etoiles === 0) return;
    const zone = Monde.zoneA(j.x, j.y);
    // ⚠️ La police suit le rythme comme le reste : autant d'agents a 4 h du
    // matin qu'a midi, dans une ville desertee, ca se remarque tout de suite.
    // Les renforts d'un palier de recherche, eux, ne dorment pas : on te
    // cherche autant la nuit.
    const voulu = agentsVoulus(zone, Monde.standingA(Math.floor(j.x / TT), Math.floor(j.y / TT)));
    const presents = agents().length;
    if (presents >= voulu) return;
    const place = placeAgent(r.etoiles > 0 ? (r.dernierVu || j) : null);
    if (!place) return;
    const a = creerAgent(place.x, place.y, r.etoiles > 0 ? 'enquete' : 'flane');
    if (r.etoiles > 0) { a.but = r.dernierVu || { x: j.x, y: j.y }; a.enqueteT = 300; }
  }

  // --- Les autos de patrouille -------------------------------------------------------

  function autos() { return B.entites.filter(function (e) { return e.type === 'vehicule' && e.conducteur === 'police' && e.etat !== 'epave'; }); }

  function peuplerAutos() {
    const j = B.joueur, r = B.recherche;
    if (B.t % 45 !== 0) return;
    const voulu = palierDesRenforts().autos;
    // ⚠️ Une auto dont l'equipage est mort reste garee, mais ne compte plus : sans ca, deux agents tues
    // et la police n'enverrait plus jamais de renfort.
    const presentes = autos().filter(function (a) { return !abandonnee(a); });
    if (presentes.length >= voulu) return;
    // Naissance sur une voie, hors ecran, dans le sens de la voie.
    const c = Monde.carte;
    for (let essai = 0; essai < 20; essai++) {
      const a = B.rng() * Math.PI * 2, d = 320 + B.rng() * 200;
      const tx = Math.floor((j.x + Math.cos(a) * d) / TT), ty = Math.floor((j.y + Math.sin(a) * d) / TT);
      if (tx < 1 || ty < 1 || tx >= c.w - 1 || ty >= c.h - 1) continue;
      const f = Monde.fleche(tx, ty);
      const pas = { '>': [1, 0], '<': [-1, 0], '^': [0, -1], 'v': [0, 1] }[f];
      if (!pas || Entites.visibleAEcran(tx * TT + 8, ty * TT + 8, 40)) continue;
      const v = Vehicules.creer('police', tx * TT + 8, ty * TT + 8, Math.atan2(pas[1], pas[0]),
                                { conducteur: 'police', etat: 'roule', sirene: true, surRails: true, poursuite: true, sens: f });
      if (v) { v.vitesse = 2; v.vx = pas[0] * 2; v.vy = pas[1] * 2; }
      return;
    }
  }

  /** Freiner SANS reculer. ⚠️ `frein` a l'arret, c'est la MARCHE ARRIERE
      (`majPhysique` : sous 0,15 px/image, le frein pousse a reculer) : une auto
      de patrouille a qui on disait « freine » s'arretait, puis reculait a
      1,45 px/image — le seuil qui renverse un pieton est a 1,2 — et repartait.
      On ne freine donc que tant qu'elle avance ; sous ce seuil, plus de frein,
      et la friction finit le travail. */
  function freiner(v, force) {
    return { gaz: 0, frein: v.vitesse > 0.15 ? (force || 1) : 0, direction: 0, freinMain: false };
  }

  /** La portiere d'une auto arretee : `cote` = +1 le passager, -1 le conducteur.
      Comme `Vehicules.descendre` : de son cote si c'est libre, sinon de l'autre,
      sinon derriere, sinon dans l'auto (la collision le pousse dehors). Toujours
      a cote de la carrosserie, jamais dans l'axe : c'est la que l'auto roule. */
  function portiere(v, cote) {
    const cotes = [v.angle + cote * Math.PI / 2, v.angle - cote * Math.PI / 2, v.angle + Math.PI];
    for (const a of cotes) {
      const ecart = a === cotes[2] ? v.def.longueur / 2 + 8 : v.def.largeur / 2 + 8;
      const x = v.x + Math.cos(a) * ecart, y = v.y + Math.sin(a) * ecart;
      if (!Monde.bloque(Math.floor(x / TT), Math.floor(y / TT), Monde.MASQUE_PIETON)) return { x: x, y: y };
    }
    return { x: v.x, y: v.y };
  }

  // --- L'equipage : deux agents par auto, un au volant, jamais un de plus ----------------------
  //
  // ⚠️ (retour de Martin) UNE AUTO A DEUX AGENTS, ET UN SEUL CONDUIT. `v.equipage` = combien
  // en restent en vie (deux a la naissance) ; `v.equipe` = ceux qui sont DEHORS, des agents de
  // la ville ; ce qui n'est pas dehors est a bord. Deux regles en decoulent :
  // - l'auto ne roule que si quelqu'un est au volant : les deux dehors, elle reste GAREE
  //   (vitesse tenue a zero) jusqu'a ce que l'un d'eux REPRENNE LE VOLANT — ils reviennent a
  //   pied (`regagner`) des que tu n'es plus sur eux ;
  // - au volant, un seul peut etre dehors : le passager.
  // Personne n'est FABRIQUE : on descend de l'auto, on y remonte, et le compte ne change pas.
  // Il ne baisse que quand un agent meurt, ou s'est perdu trop loin de son auto.

  /** Met le compte a jour et le rend : { dehors, abord }. Un agent mort ne remonte pas (l'equipage
      perd un homme) ; un agent que la ville a retire est considere remonte. */
  function equipage(v) {
    if (v.equipage === undefined) { v.equipage = reglages().auto_equipage; v.equipe = []; }
    v.equipe = v.equipe.filter(function (a) {
      if (!a.vivant) { v.equipage--; return false; }
      return B.entites.indexOf(a) >= 0;
    });
    return { dehors: v.equipe.length, abord: v.equipage - v.equipe.length };
  }

  /** Une auto dont l'equipage est mort : personne ne la reprendra, elle ne compte plus. */
  function abandonnee(v) { return v.equipage !== undefined && v.equipage <= 0; }

  /** Un agent quitte l'equipage : mort, ou perdu trop loin. L'auto ne le compte plus. */
  function perdreUnEquipier(v, a) {
    v.equipe = v.equipe.filter(function (x) { return x !== a; });
    v.equipage--;
    a.auto = null;
    if (a.etat === 'regagne') { a.etat = 'flane'; a.but = null; a.chemin = null; }
  }

  /** Garee : personne au volant. Ni vitesse, ni marche arriere, ni glissade. */
  function garee(v) {
    v.vitesse = 0; v.vx = 0; v.vy = 0;
    return { gaz: 0, frein: 0, direction: 0, freinMain: false };
  }

  /** Un agent descend de l'auto, par sa portiere, et se tourne vers toi. */
  function faireDescendre(v, cote) {
    const j = B.joueur, porte = portiere(v, cote);
    const a = creerAgent(porte.x, porte.y, 'poursuit');
    Entites.regarder(a, j.x - porte.x, j.y - porte.y);
    a.auto = v;
    v.equipe.push(a);
    Son.depuis(v, function () { Son.SFX.porte('vehicule'); });
  }

  /** Tu es a pied et l'auto est sur toi : elle S'ARRETE, puis l'equipage descend.

      ⚠️ PAS AVANT (retour de Martin). Les deux agents naissaient a ±14 px de
      l'auto, dans l'axe du monde et non de sa carrosserie, pendant qu'elle roulait
      encore a 2,5–3,7 px/image : ecrases en une image, par leur propre voiture.
      Maintenant :
      - le PASSAGER saute seul quand l'auto est descendue au pas
        (`auto_passager_saute_sous`, sous le seuil qui renverse) — le conducteur
        tient le volant et continue de freiner ;
      - le CONDUCTEUR descend quand elle est arretee (`auto_arret_sous`) ;
      - equipage dehors, l'auto est GAREE : aucune marche arriere, immobile, jusqu'a ce
        qu'un agent ait repris le volant (`commandes`). */
  function stationner(v, p) {
    const roule = Math.hypot(v.vx, v.vy);
    if (equipage(v).abord >= 2 && roule < p.auto_passager_saute_sous) faireDescendre(v, 1);
    if (equipage(v).abord === 1 && roule < p.auto_arret_sous) faireDescendre(v, -1);
    return equipage(v).abord <= 0 ? garee(v) : freiner(v, p.auto_frein);
  }

  /** Personne au volant, et tu n'es plus sur eux : les agents dehors REGAGNENT l'auto. */
  function rappeler(v, p) {
    for (const a of v.equipe.slice()) {
      if (Math.hypot(a.x - v.x, a.y - v.y) > p.auto_rappel_px) { perdreUnEquipier(v, a); continue; }
      if (a.etat === 'regagne' || a.etat === 'assomme' || a.etat === 'attaque' || a.recul > 0) continue;
      a.etat = 'regagne'; a.regagneDepuis = B.t; a.chemin = null; a.cheminT = 0;
    }
  }

  /** Tu es de nouveau sur eux : ceux qui rentraient a l'auto reprennent la chasse. */
  function lacher(v) {
    for (const a of v.equipe) if (a.etat === 'regagne') { a.etat = 'poursuit'; a.chemin = null; a.vuT = 0; }
  }

  /** Un equipier arrive en courant : l'auto l'attend, une seconde, pas plus. */
  function attendUnEquipier(v, p) {
    return v.equipe.some(function (a) { return a.etat === 'regagne' && Math.hypot(a.x - v.x, a.y - v.y) < p.auto_attend_px; });
  }

  /** L'agent monte : il quitte la ville et l'auto le compte a bord. */
  function remonter(a, v) {
    v.equipe = v.equipe.filter(function (x) { return x !== a; });
    a.auto = null;
    Son.depuis(v, function () { Son.SFX.porte('vehicule'); });
    Entites.retirer(a);
  }

  /** L'agent retourne a son auto pour reprendre le volant (ou la place du passager). Rend true
      tant que la police le dirige ; sinon il a change d'etat, et la suite de `gere` le traite. */
  function regagner(a) {
    const v = a.auto, p = reglages();
    if (!v || v.etat === 'epave' || B.entites.indexOf(v) < 0) { a.auto = null; a.etat = 'flane'; a.chemin = null; return false; }
    if (B.recherche.etoiles <= 0) { a.etat = 'flane'; a.but = null; a.chemin = null; return false; }
    if (B.t - a.regagneDepuis > p.auto_regagne_s * 60) { perdreUnEquipier(v, a); return false; }
    // L'auto est deja repartie sans lui (l'autre a repris le volant) : il reprend la chasse a pied.
    if (Math.hypot(v.vx, v.vy) > p.auto_arret_sous) { a.etat = 'poursuit'; a.chemin = null; a.vuT = 0; return false; }
    if (Math.hypot(v.x - a.x, v.y - a.y) < v.def.largeur / 2 + 12) { remonter(a, v); return true; }
    suivre(a, { x: v.x, y: v.y }, defs().vitesses.policier * 1.25);
    return true;
  }

  /** Les commandes d'une auto de patrouille. Elle suit les RAILS de la ville
      vers toi (feux et stops brules, sortie choisie vers toi a chaque
      croisement) et ne quitte les rails pour te FONCER dessus que quand elle
      te voit de pres. Rend 'rails' (le trafic la conduit) ou des commandes
      (la physique la conduit). Foncer tout droit de loin finissait dans un mur.

      ⚠️ SANS PERSONNE AU VOLANT, ELLE NE ROULE PAS : les deux agents dehors, elle reste garee
      — immobile — jusqu'a ce que l'un d'eux la reprenne (`regagner`). */
  function commandes(v) {
    const j = B.joueur, r = B.recherche, p = reglages();
    const eq = equipage(v);
    v.poursuite = r.etoiles > 0;
    if (r.etoiles <= 0) { v.surRails = false; return eq.abord > 0 ? freiner(v) : garee(v); }
    const cible = j.dansVehicule ? j.dansVehicule : j;
    const d = Math.hypot(cible.x - v.x, cible.y - v.y);
    // Une auto sans conducteur ne voit rien : ses agents, dehors, voient pour eux.
    // ⚠️ Garee devant le rideau baisse, elle ne « sent » plus rien : le joueur est a l'abri.
    if (eq.abord > 0 && !Monde.abrite(j.dansVehicule) && (voit(v, cible.x, cible.y, 'auto_police', true) || d < 60)) { r.vu = 0; r.dernierVu = { x: j.x, y: j.y, t: B.t }; }
    if (!j.dansVehicule && (d < p.auto_sortent_px || (eq.dehors && d < p.auto_sortent_px * 2.5))) {
      // Tu es a pied : elle s'arrete, l'equipage descend, et elle reste la (pas de va-et-vient).
      v.surRails = false;
      lacher(v);
      return stationner(v, p);
    }
    // Tu t'es sauve loin (ou tu roules) : personne au volant, elle reste garee, et les agents rentrent.
    if (eq.abord <= 0) { v.surRails = false; rappeler(v, p); return garee(v); }
    if (eq.dehors && attendUnEquipier(v, p)) { v.surRails = false; return garee(v); }
    // De pres et a vue : on quitte les rails et on fonce. Coince (un mur) : on y retourne.
    const direct = d < 140 && Monde.ligneLibre(v.x, v.y, cible.x, cible.y);
    const coince = !v.surRails && (v.immobileT || 0) > 45;
    if (!direct || coince) {
      if (!v.surRails) { v.cible = null; v.sortie = null; v.immobileT = 0; }
      v.surRails = true;
      return 'rails';
    }
    v.surRails = false;
    const voulu = angleVers(v.x, v.y, cible.x, cible.y);
    const ecart = ecartAngle(v.angle, voulu);
    const vitesseMax = v.def.vitesse_max * p.auto_vitesse;
    const gaz = (Math.abs(ecart) > 1.6) ? 0 : (v.vitesse < vitesseMax ? 1 : 0);
    const frein = (Math.abs(ecart) > 1.6 && v.vitesse > 1) ? 1 : 0;
    return { gaz: gaz, frein: frein, direction: borner(ecart * 2, -1, 1), freinMain: Math.abs(ecart) > 1.2 && v.vitesse > 2 };
  }

  // --- L'helico : l'oeil dans le ciel, a cinq etoiles -----------------------------------
  //
  // Il ne tire pas, il VOIT : tant qu'il te survole, rien ne retombe. On s'en
  // debarrasse en rentrant quelque part, ou en tenant 90 s... il ne lache
  // rien. Son ombre court au sol, son projecteur te suit la nuit.

  const HELICO_VITESSE = 3.4, HELICO_ALTITUDE = 40, HELICO_RAYON_VOL = 56;
  //: On l'entend jusqu'a 700 px ; reparti, il disparait la. Dedans, il s'entend
  //: moins fort ET sourd (`Son.etouffer`) ; il entre et sort de l'oreille en fondu.
  const HELICO_PORTEE_SON = 700, HELICO_VOLUME_DEDANS = 0.45, HELICO_FONDU_S = 0.6;

  function helico() { return B.entites.find(function (e) { return e.type === 'helico'; }) || null; }

  /** L'helico, meme quand on est dedans : il est alors resté dans la ville mise
      de côté (`B.exterieur.entites`), où `helico()` ne regarde pas. */
  function helicoDuCiel() {
    if (!B.interieur) return helico();
    const dehors = B.exterieur && B.exterieur.entites;
    return (dehors && dehors.find(function (e) { return e.type === 'helico'; })) || null;
  }

  /** Ce que l'helico survole : ton char, ou toi ; DEDANS, la porte par où tu es
      entré — il tourne au-dessus du toit, pour rien. */
  function ceQuIlSurvole() {
    const j = B.joueur;
    if (B.interieur) return B.exterieur ? { x: B.exterieur.x, y: B.exterieur.y } : null;
    return j ? (j.dansVehicule || j) : null;
  }

  function peuplerHelico() {
    const j = B.joueur;
    if (helico() || B.t % 60 !== 0) return;
    const a = B.rng() * Math.PI * 2;
    Entites.creer('helico', j.x + Math.cos(a) * 520, j.y + Math.sin(a) * 520, {
      r: 0, z: HELICO_ALTITUDE, solide: false, vivant: true, dessine: false, orbite: a, rotor: 0, part: false,
    });
    Hud.message('UN HÉLICO !', 150);
    Son.Ondes.police('helico');
  }

  function majHelico(h) {
    const j = B.joueur, r = B.recherche, cible = ceQuIlSurvole();
    if (!cible) return;
    h.rotor += 0.9;
    if (r.etoiles <= 0 || !palier().helico) h.part = true;
    let bx, by;
    if (h.part) { bx = h.x + (h.x - cible.x) * 2 + 400; by = h.y - 400; }
    else { h.orbite += 0.008; bx = cible.x + Math.cos(h.orbite) * HELICO_RAYON_VOL; by = cible.y + Math.sin(h.orbite) * HELICO_RAYON_VOL; }
    const dx = bx - h.x, dy = by - h.y, d = Math.hypot(dx, dy) || 1;
    const pas = Math.min(HELICO_VITESSE, d * 0.06 + 0.4);
    h.vx = h.vx * 0.9 + dx / d * pas * 0.1; h.vy = h.vy * 0.9 + dy / d * pas * 0.1;
    h.x += h.vx; h.y += h.vy;
    if (Math.hypot(h.vx, h.vy) > 0.3) h.angle = Math.atan2(h.vy, h.vx);
    if (h.part && dist2(h.x, h.y, cible.x, cible.y) > HELICO_PORTEE_SON * HELICO_PORTEE_SON) { oublierHelico(h); return; }
    // Il voit tout ce qui est sous lui, sauf a travers un toit.
    const vision = defs().vision.helico, portee = (Monde.estNuit() ? vision.nuit : vision.jour) * TT;
    // ⚠️ Il voit a travers tout, sauf un toit : dans un garage, rideau baisse, il tourne pour rien.
    if (!h.part && !B.interieur && !Monde.abrite(j.dansVehicule) && dist2(h.x, h.y, cible.x, cible.y) < portee * portee) { r.vu = 0; r.dernierVu = { x: j.x, y: j.y, t: B.t }; }
  }

  /** Il est reparti assez loin : on le retire de la ville ou il vole — celle
      mise de cote quand on est dedans, ou `Entites.retirer` ne le trouverait pas. */
  function oublierHelico(h) {
    if (!B.interieur) { Entites.retirer(h); return; }
    const dehors = B.exterieur ? B.exterieur.entites : [];
    const i = dehors.indexOf(h);
    if (i >= 0) dehors.splice(i, 1);
  }

  //: Ce que le melangeur a demande a `Son` pour l'helico : `volume` 0 = eteint,
  //: `sourd` 1 = entendu a travers un toit. Les juges le lisent (voir `sirenes`).
  const bruitHelico = { volume: 0, sourd: 0 };

  /** Le bruit de l'helico : a CHAQUE image, dedans comme dehors, d'apres l'helico
      qui existe vraiment.

      ⚠️ Bug de Martin (21 sept. 2026) : « je suis resté avec un son
      d'hélicoptère ». Le bruit ne se reglait que dans `majHelico`, qui ne
      tournait que dehors, et ne s'eteignait qu'au depart de l'helico : entrer
      dans une piece le figeait a son dernier volume, et une partie reprise
      (`commencer()` vide la ville) effacait l'helico sans eteindre son bruit.
      Pas d'helico, pas de bruit — quelle que soit la facon dont il a disparu.

      ⚠️ Contrairement aux sirenes, il LIT `Son.boucleActive` : c'est la seule
      facon d'etre certain que la boucle s'eteint, et une boucle que `Son` ne
      peut pas jouer (pas de fichier, pas de geste) se redemande a chaque image
      pour presque rien — `echantillon` rend null avant de fabriquer quoi que ce soit. */
  function majBruitHelico() {
    const h = helicoDuCiel(), ou = h && ceQuIlSurvole();
    let voulu = 0;
    if (h && ou) {
      const loin = Math.hypot(h.x - ou.x, h.y - ou.y) / HELICO_PORTEE_SON;
      // En chasse, on l'entend toujours un peu ; reparti, il s'eteint en
      // s'eloignant, et se tait a la distance ou il disparait.
      voulu = h.part ? Math.max(0, 1 - loin) : Math.max(0.05, 1 - loin);
      if (B.interieur) voulu *= HELICO_VOLUME_DEDANS;
      if (voulu < 0.01) voulu = 0;
    }
    bruitHelico.volume = voulu;
    bruitHelico.sourd = B.interieur ? 1 : 0;
    if (!voulu) { taireHelico(); return; }
    if (!Son.boucleActive('helico')) Son.boucle('helico', true, voulu, HELICO_FONDU_S);
    Son.reglerBoucle('helico', voulu);
    Son.etouffer('helico', bruitHelico.sourd);
  }

  /** Eteint le bruit de l'helico, en fondu : l'ecran titre, ou plus d'helico. */
  function taireHelico() {
    bruitHelico.volume = 0;
    if (Son.boucleActive('helico')) Son.boucle('helico', false, undefined, HELICO_FONDU_S);
  }

  /** L'helico se dessine par-dessus tout, avec son ombre au sol et son rotor qui tourne. */
  function dessinerHelico(ctx, vue) {
    const h = helico();
    if (!h) return;
    const x = Math.round(h.x - vue.x), y = Math.round(h.y - vue.y);
    if (x < -40 || x > VW + 40 || y < -60 || y > VH + 40) return;
    ctx.fillStyle = 'rgba(0,0,0,0.3)'; ctx.fillRect(x - 10, y - 4, 20, 8); B.stats.rects++;   // l'ombre, au sol
    const yz = y - h.z;
    ctx.save(); ctx.translate(x, yz); ctx.rotate(h.angle || 0);
    ctx.fillStyle = '#1f3a6e'; ctx.fillRect(-8, -5, 16, 10);              // la cabine
    ctx.fillStyle = '#16264a'; ctx.fillRect(-20, -2, 12, 4);              // la queue
    ctx.fillStyle = '#7fb3d8'; ctx.fillRect(2, -3, 5, 6);                 // la vitre
    ctx.fillStyle = '#efe6d0'; ctx.fillRect(-4, -1, 3, 2);
    ctx.restore();
    ctx.save(); ctx.translate(x, yz); ctx.rotate(h.rotor);
    ctx.fillStyle = 'rgba(230,230,240,0.8)'; ctx.fillRect(-18, -1, 36, 2); ctx.fillRect(-1, -18, 2, 36);   // le rotor
    ctx.restore();
    B.stats.rects += 6;
  }

  /** Le projecteur de l'helico, la nuit : une lampe de plus pour `Base.fin`. */
  function lampeHelico(vue) {
    const h = helico();
    if (!h || h.part) return null;
    return { x: h.x - vue.x, y: h.y - vue.y, r: 70, c: 'rgba(255,255,230,0.75)' };
  }

  // --- Les barrages : deux autos en travers, devant toi, a cinq etoiles --------------------

  const BARRAGE_TOUTES_LES = 900, BARRAGE_DISTANCE = [260, 440];

  function barrages() { return B.entites.filter(function (e) { return e.type === 'vehicule' && e.barrage; }); }

  function majBarrages() {
    const j = B.joueur, r = B.recherche, v = j.dansVehicule;
    const existants = barrages();
    if (r.etoiles <= 0 || !palierDesRenforts().barrages) {
      existants.forEach(function (b) { if (!Entites.visibleAEcran(b.x, b.y, 60)) Entites.retirer(b); });
      return;
    }
    if (B.t % BARRAGE_TOUTES_LES !== 0 || !v || Math.abs(v.vitesse) < 1) return;
    if (existants.some(function (b) { return dist2(b.x, b.y, j.x, j.y) < 500 * 500; })) return;
    poserBarrage(v);
  }

  /** Cherche, devant le char, une tuile de voie droite ; y pose deux autos en
      travers et deux agents derriere. Rend le barrage pose, ou null. */
  function poserBarrage(v) {
    const cx = Math.cos(v.angle), cy = Math.sin(v.angle);
    for (let d = BARRAGE_DISTANCE[0]; d <= BARRAGE_DISTANCE[1]; d += 16) {
      const px = v.x + cx * d, py = v.y + cy * d;
      const tx = Math.floor(px / TT), ty = Math.floor(py / TT);
      const f = Monde.fleche(tx, ty);
      const pas = { '>': [1, 0], '<': [-1, 0], '^': [0, -1], 'v': [0, 1] }[f];
      if (!pas || !Monde.estChaussee(tx, ty)) continue;
      const route = Math.atan2(pas[1], pas[0]), travers = route + Math.PI / 2;
      const nx = Math.cos(travers), ny = Math.sin(travers);
      const centre = { x: tx * TT + 8, y: ty * TT + 8 };
      const autos = [];
      for (const s of [-1, 1]) {
        const a = Vehicules.creer('police', centre.x + nx * 14 * s, centre.y + ny * 14 * s, travers, { etat: 'stationne', barrage: true, conducteur: null });
        if (a) autos.push(a);
      }
      if (!autos.length) continue;
      for (const s of [-1, 1]) creerAgent(centre.x + cx * 26 + nx * 10 * s, centre.y + cy * 26 + ny * 10 * s, 'poursuit');
      Entites.indexer();
      Hud.message('BARRAGE !', 120);
      Son.Ondes.police('barrage');
      return { x: centre.x, y: centre.y, autos: autos };
    }
    return null;
  }

  // --- Les affiches ----------------------------------------------------------------

  let facades = { carte: null, liste: [] };

  /** Toutes les facades de la ville, une fois : c'est la qu'on colle les affiches. */
  function lesFacades() {
    const c = Monde.carte;
    if (facades.carte === c) return facades.liste;
    const liste = [];
    for (let ty = 1; ty < c.h - 1; ty++) for (let tx = 1; tx < c.w - 1; tx++) {
      if (Monde.glyphe(tx, ty) === 'F' && !Monde.bloque(tx, ty + 1, Monde.MASQUE_PIETON)) liste.push({ x: tx * TT + 8, y: ty * TT + 12 });
    }
    facades = { carte: c, liste: liste };
    return liste;
  }

  function majAffiches() {
    const r = B.recherche, j = B.joueur, p = reglages();
    const affiches = B.entites.filter(function (e) { return e.type === 'affiche'; });
    if (r.etoiles < 2) { affiches.forEach(function (e) { Entites.retirer(e); }); return; }
    if (affiches.length >= p.affiches_max || B.t % 40 !== 0) return;
    const proches = lesFacades().filter(function (f) {
      const d = dist2(f.x, f.y, j.x, j.y);
      return d > 120 * 120 && d < 420 * 420 && !affiches.some(function (e) { return dist2(e.x, e.y, f.x, f.y) < 64 * 64; });
    });
    if (!proches.length) return;
    const f = proches[Math.floor(B.rng() * proches.length)];
    Entites.creer('affiche', f.x, f.y, { decor: 'affiche', r: 0, solide: false, dessine: true, vivant: false });
  }

  // --- La machine de recherche -----------------------------------------------------

  /** ⚠️ LA CHALEUR REFROIDIT (la tolerance, 22 sept. 2026) : `chaleur_repit_s` apres le
      dernier delit compte, la jauge perd `chaleur_refroidit_par_s` a la seconde. Elle ne
      redescendait jamais : trois petits delits a vingt minutes d'ecart faisaient une
      etoile. ⚠️ La jauge seulement : les etoiles, elles, ne tombent qu'hors de vue. */
  function refroidir() {
    const r = B.recherche;
    if (r.repitChaleur > 0) { r.repitChaleur--; return; }
    if (r.chaleur > 0) r.chaleur = Math.max(0, r.chaleur - defs().chaleur_refroidit_par_s / 60);
  }

  /** ⚠️ LES RENFORTS PRENNENT LE TEMPS DE VENIR (la tolerance, 22 sept. 2026). Ceux d'une
      etoile neuve partent du poste `renfort_s` apres elle : `r.renforts` rattrape les
      etoiles au bout du compte a rebours, et redescend avec elles sans attendre. Une
      etoile de plus pendant l'attente la relance. ⚠️ Les agents DEJA la ne sont pas des
      renforts : ils te voient, te poursuivent et tirent tout de suite (`gere`). Un compte
      a rebours plutot qu'une heure (`B.t`), qui repart de zero a chaque partie. */
  function majRenforts() {
    const r = B.recherche;
    if (r.etoiles > (r.etoilesAvant || 0)) r.renfortN = reglages().renfort_s * 60;
    r.etoilesAvant = r.etoiles;
    if (r.renfortN > 0) r.renfortN--;
    if (r.renforts === undefined) r.renforts = 0;
    if (!(r.renfortN > 0) || r.renforts > r.etoiles) r.renforts = r.etoiles;
  }

  /** Hors de vue, les etoiles tombent une a une. Rien ne les remet a zero d'un coup. */
  function decroitre() {
    const r = B.recherche;
    if (r.etoiles <= 0) return;
    r.vu++;
    const p = defs().paliers[r.etoiles];
    if (r.vu > p.decroissance_s * 60) {
      r.etoiles--; r.vu = 0;
      if (r.etoiles === 0) { Hud.message('LA POLICE A LÂCHÉ'); annoncer(1); }
    }
  }

  function maj() {
    const r = B.recherche, j = B.joueur;
    if (!j) return;
    if (r.flash > 0) r.flash--;
    refroidir();
    majRenforts();
    if (B.interieur) {
      // Dedans, on se fait oublier ; personne ne patrouille les salons. Mais
      // l'helico tourne au-dessus du toit, et repart quand les etoiles tombent.
      decroitre();
      const h = helicoDuCiel();
      if (h) majHelico(h);
      majBruitHelico();
      return;
    }
    // ⚠️ L'ILE : on s'y fait oublier comme dans une piece, et la police s'en
    // va — aucun agent n'y nait, l'helico repart, et ce qui patrouillait hors
    // de l'ecran ne revient pas. Les temoins attendront qu'on rentre en ville.
    if (auRefuge()) {
      decroitre();
      const h = helico();
      if (h) { h.part = true; majHelico(h); }
      majBruitHelico();
      agents().concat(autos()).forEach(function (e) { if (!Entites.visibleAEcran(e.x, e.y, 60)) Entites.retirer(e); });
      return;
    }
    peuplerAgents();
    decroitre();
    if (r.etoiles > 0) {
      peuplerAutos();
      if (palierDesRenforts().helico) peuplerHelico();
    } else {
      autos().forEach(function (v) { if (!Entites.visibleAEcran(v.x, v.y, 60)) Entites.retirer(v); });
    }
    majAffiches();
    const h = helico();
    if (h) majHelico(h);
    majBruitHelico();
    majBarrages();
    majStools();
    // Les temoins qui courent vers un agent : arrives, ils racontent. Loin de
    // tout agent, ils telephonent au bout du delai.
    const t = defs().temoins;
    for (const e of B.entites) {
      if (e.type !== 'pieton' || e.etat !== 'temoin' || !e.crime || e.crime.rapporte) continue;
      let proche = null, dMin = t.cherche_policier_tuiles * TT;
      for (const a of agents()) { const d = Math.hypot(a.x - e.x, a.y - e.y); if (d < dMin) { dMin = d; proche = a; } }
      if (proche) {
        e.menace = null; e.vers = proche;
        if (dMin < 20) { rapporter(e.crime, proche); e.etat = 'fuit'; e.minuterie = 300; }
      } else if (B.t - e.crime.t > t.delai_depeche_s * 60 * standingIci(e.x, e.y).depeche
                 && B.rng() < t.proba_telephone / 60) {
        rapporter(e.crime, null);
        e.etat = 'fuit'; e.minuterie = 300;
      }
    }
  }

  return { dansLeCone, voit, porteeDuCasier, quelqu_un_voit, auRefuge, ajouterChaleur, etoilesAuMoins, signalerCrime, crimeDAutrui, rapporter, acheterLeSilence, remiseAZero, entendre, palierDesRenforts,
           estStool, leStool, prixDuStool, majStools, appelDuStool, acheterLeStool, onNeTeReconnaitPlus,
           creerAgent, agents, autos, gere, commandes, peuplerAgents, peuplerAutos, equipageDe: equipage, abandonnee,
           agentsVoulus, standingIci,
           helico, majHelico, majBruitHelico, taireHelico, bruitHelico, dessinerHelico, lampeHelico, barrages, poserBarrage, maj };
})();
