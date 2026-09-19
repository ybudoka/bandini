/* Bandini — le compte, cote jeu (M14, 2e vague) : le local joue, le serveur se souvient.

   La 1re vague a donne au serveur tout ce qu'il fallait (`app/comptes.py`, six
   routes sous `/api/compte/`) et le jeu ne s'en servait pas : aucun ecran ne
   creait de compte, aucune partie ne montait. Ce module est le SEUL endroit du
   jeu qui parle a `/api/compte/`.

   ⚠️ UN COMPTE EST UN CONFORT, JAMAIS UNE CONDITION. Le `localStorage` reste la
   verite pendant qu'on joue ; le serveur recoit des INSTANTANES. Serveur eteint,
   wifi coupe, base tombee : `etat` passe a « hors-ligne » et le jeu ne s'en
   apercoit pas. Rien ici ne doit jamais empecher de presser JOUER.

   ⚠️ L'OUVERTURE PASSE EN PREMIER, ET SEULE. `POST /api/compte/ouvrir` tourne le
   jeton d'appareil une fois par chargement ; une requete partie avant sa reponse
   arriverait avec un jeton deja remplace et passerait pour un vol — tous les
   appareils coupes, pour rien (voir le prologue de `app/comptes.py`). D'ou la
   file : tout ce que le jeu demande attend derriere la promesse de l'ouverture,
   et les appels ne se croisent jamais.

   ⚠️ LE CONFLIT NE SE DEVINE PAS AU COMPTEUR SEUL. Le serveur refuse ce qui
   n'avance pas, et deux appareils n'ont pas la meme heure : le compteur est le
   seul ordre qui existe. Mais « mon local est a 41, le serveur a 40 » ne dit pas
   si j'ai joue depuis SA version ou si nous avons joue chacun de notre cote — la
   reponse est dans ce que CET appareil a vu du compte la derniere fois
   (`bandini-compte-sync-v1`). Sans ce temoin, il n'y a que deux issues, et les
   deux sont fausses : ecraser en silence, ou poser la question a chaque partie.
   Avec lui, `decision(n)` tranche seule dans les cas evidents et ne derange le
   joueur que quand les deux cotes ont vraiment bouge. */

const Compte = (function () {
  'use strict';

  //: Au plus une montee par minute et demie EN JOUANT : la partie se sauve toutes
  //: les dix secondes (`Missions.maj`), et le serveur n'a pas besoin de les voir
  //: toutes passer. Ce qui compte vraiment part ailleurs : au retour au titre et
  //: a la fermeture de l'onglet (`partir`).
  const REPOS_MS = 90 * 1000;

  //: Ce que cet appareil a vu du compte, par emplacement : `envoye` (le compteur
  //: local de la version qu'on a montee ou prise) et `serveur` (le sien, au meme
  //: instant). Range sous le pseudo : se connecter a un AUTRE compte remet le
  //: temoin a zero, et ses parties se comparent aux siennes, pas a celles d'avant.
  const CLE_SYNC = 'bandini-compte-sync-v1';

  const MSG_HORS_LIGNE = 'Pas de réseau : ta partie reste ici, elle montera plus tard.';

  let fenetre = null, stockage = null, base = '';
  let ouverture = null, chaine = Promise.resolve();
  let etat = 'inconnu';   //: inconnu | ferme | ouvert | hors-ligne | indisponible
  let pseudo = null, message = '';
  //: Par emplacement (1..3) : { compteur, sauvee_le, apercu } tel que le serveur le dit.
  let parties = {};
  //: Les cases ou le joueur doit trancher : { local, serveur, compteur, partie? }.
  let conflits = {};
  let sync = { compte: null, cases: {} };
  let derniereMontee = 0;
  const abonnes = [];

  function rien() { /* la file continue, quoi qu'il arrive */ }

  // --- Le temoin ------------------------------------------------------------------

  function lireSync() {
    try {
      const brut = stockage && stockage.getItem(CLE_SYNC);
      const s = brut ? JSON.parse(brut) : null;
      if (s && typeof s === 'object' && s.cases && typeof s.cases === 'object') return s;
    } catch (e) { /* un temoin illisible n'est pas un temoin */ }
    return { compte: null, cases: {} };
  }

  function ecrireSync() {
    try { stockage && stockage.setItem(CLE_SYNC, JSON.stringify(sync)); } catch (e) { /* rien */ }
  }

  /** Ce que cet appareil a vu de la case `n` POUR LE COMPTE OUVERT, ou null. */
  function vu(n) {
    if (!pseudo || sync.compte !== pseudo) return null;
    const v = sync.cases[String(n)];
    return v && typeof v.envoye === 'number' && typeof v.serveur === 'number' ? v : null;
  }

  /** On vient de mettre les deux cotes d'accord sur la case `n`. */
  function noterVu(n, envoye, serveur) {
    if (!pseudo) return;
    if (sync.compte !== pseudo) sync = { compte: pseudo, cases: {} };
    sync.cases[String(n)] = { envoye: envoye, serveur: serveur };
    ecrireSync();
  }

  // --- L'etat, et ceux qui le regardent ---------------------------------------------

  function etatPublic() {
    const cases = [];
    for (let n = 1; n <= Sauvegarde.EMPLACEMENTS; n++) {
      cases.push({ emplacement: n, serveur: parties[n] || null, conflit: conflits[n] || null,
                   decision: etat === 'ouvert' ? decision(n) : 'rien' });
    }
    return { etat: etat, pseudo: pseudo, message: message, cases: cases };
  }

  /** ⚠️ Sans try/catch : un abonne qui leve est un bogue a nous, et un bogue
      avale est un bogue qu'on cherche trois jours. */
  function prevenir(recue) {
    const vue = etatPublic();
    for (const f of abonnes) f(vue, recue || 0);
  }

  function surChangement(f) { abonnes.push(f); }

  function apercuServeur(n) {
    const p = parties[n];
    return p && p.apercu ? p.apercu : null;
  }

  function compteurServeur(n) {
    const p = parties[n];
    return p && typeof p.compteur === 'number' ? p.compteur : 0;
  }

  function noterServeur(n, etatCase) {
    parties[n] = { compteur: etatCase.compteur || 0, sauvee_le: etatCase.sauvee_le || null,
                   apercu: etatCase.apercu !== undefined ? etatCase.apercu : apercuDe(etatCase.partie) };
  }

  /** Les champs que `Sauvegarde.apercu` montre, tires d'une partie entiere. */
  function apercuDe(partie) {
    if (!partie || typeof partie !== 'object') return null;
    return { jour: partie.jour || 1, argent: partie.argent || 0,
             secondes: (partie.stats && partie.stats.secondes) || 0,
             missions: partie.missionsFaites ? Object.keys(partie.missionsFaites).length : 0 };
  }

  // --- CE QUI SE DECIDE TOUT SEUL, ET CE QUI SE DEMANDE ------------------------------

  /** Que faire de la case `n` : 'rien', 'monter', 'descendre' ou 'trancher'.

      ⚠️ La fonction la plus importante du module, et la seule qui merite d'etre
      lue deux fois. Une case VIDE d'un cote se remplit de l'autre sans rien
      demander — il n'y a rien a perdre. Deux cases pleines se comparent au
      TEMOIN : si le serveur n'a pas bouge depuis ce que j'ai vu, ma partie
      descend de la sienne et elle monte ; si c'est moi qui n'ai pas bouge, la
      sienne descend. Les deux ont bouge, ou je n'ai pas de temoin (autre compte,
      stockage vide) : le joueur tranche. */
  function decision(n) {
    if (etat !== 'ouvert') return 'rien';
    const ici = Sauvegarde.apercu(n), la = apercuServeur(n);
    const local = Sauvegarde.compteur(n), distant = compteurServeur(n);
    if (!ici && !la) return 'rien';
    //: ⚠️ « rien la-bas » n'est pas « la case du serveur est vide » : une case
    //: EFFACEE garde son compteur, et remonter par-dessus la vieille partie
    //: qu'on a effacee ailleurs, c'est annuler l'effacement.
    if (!ici) return distant > 0 ? 'descendre' : 'rien';
    if (!la && distant === 0) return 'monter';
    const temoin = vu(n);
    if (!temoin) return 'trancher';
    if (temoin.serveur !== distant && temoin.envoye !== local) return 'trancher';
    if (temoin.serveur !== distant) return 'descendre';
    if (temoin.envoye !== local) return 'monter';
    return 'rien';
  }

  // --- Le reseau : une file, derriere l'ouverture ------------------------------------

  function appel(chemin, corps, methode) {
    const options = { method: methode || 'POST', credentials: 'same-origin', cache: 'no-store' };
    if (corps !== undefined) {
      options.headers = { 'Content-Type': 'application/json' };
      options.body = JSON.stringify(corps);
    }
    return fenetre.fetch(base + chemin, options).then(function (r) {
      const statut = r.status || (r.ok ? 200 : 0);
      return Promise.resolve()
        .then(function () { return r.json ? r.json() : null; })
        .catch(function () { return null; })
        .then(function (d) { return { ok: !!r.ok, statut: statut, corps: d || {} }; });
    });
  }

  /** Le reseau s'est tu : on le dit, on ne perd rien, et le jeu continue. */
  function panne() {
    if (etat === 'ouvert' || etat === 'inconnu') { etat = 'hors-ligne'; message = MSG_HORS_LIGNE; }
    prevenir();
    return null;
  }

  /** Ce que rendent `ouvrir`, `inscription`, `connexion` et `deconnexion`. */
  function recevoirCompte(res) {
    if (res.statut === 401) {
      etat = 'ferme'; pseudo = null; parties = {}; conflits = {};
      message = res.corps.erreur || '';
      prevenir();
      return false;
    }
    if (res.statut === 503) { etat = 'indisponible'; message = res.corps.erreur || ''; prevenir(); return false; }
    if (!res.ok) { message = res.corps.erreur || 'Refusé.'; prevenir(); return false; }
    const c = res.corps.compte;
    parties = {}; conflits = {};
    if (!c) { etat = 'ferme'; pseudo = null; message = ''; prevenir(); return true; }
    etat = 'ouvert'; pseudo = c.pseudo; message = '';
    for (const p of (c.parties || [])) noterServeur(p.emplacement, p);
    sync = lireSync();
    prevenir();
    return true;
  }

  /** L'ouverture : la PREMIERE requete de compte du chargement, et tout attend
      derriere elle. Appelee une seule fois — sa promesse est l'ancre de la file. */
  function ouvrir() {
    if (ouverture) return ouverture;
    ouverture = appel('ouvrir').then(function (res) {
      recevoirCompte(res);
      if (etat === 'ouvert') ranger();
      return etatPublic();
    }, function () { panne(); return etatPublic(); });
    chaine = ouverture.then(rien, rien);
    return ouverture;
  }

  function file(faire) {
    if (!ouverture) ouvrir();
    const suite = chaine.then(faire, faire);
    chaine = suite.then(rien, rien);
    return suite;
  }

  // --- Les parties montent, descendent, ou attendent le joueur -----------------------

  /** Range les trois cases apres une ouverture ou une connexion : ce qui se
      decide tout seul se fait, le reste devient un conflit que l'ecran montre. */
  function ranger() {
    for (let n = 1; n <= Sauvegarde.EMPLACEMENTS; n++) {
      const quoi = decision(n);
      if (quoi === 'descendre') prendre(n);
      else if (quoi === 'monter') monter(n);
      else if (quoi === 'trancher') conflits[n] = { local: Sauvegarde.apercu(n), serveur: apercuServeur(n),
                                                    compteur: compteurServeur(n) };
    }
    prevenir();
  }

  /** Un instantane de la case `n` monte. `force` : apres « garder celle d'ici »,
      le compteur repart au-dessus de celui du serveur — c'est le seul endroit du
      jeu qui passe par-dessus un refus, et il vient d'un choix du joueur. */
  function monter(n, force) {
    return file(function () {
      if (etat !== 'ouvert') return null;
      const local = Sauvegarde.compteur(n);
      const envoi = force ? Math.max(local, compteurServeur(n)) + 1 : local;
      if (envoi <= 0) return null;
      const temoin = vu(n);
      if (!force && temoin && temoin.envoye === local && temoin.serveur === compteurServeur(n)) return null;
      const partie = Sauvegarde.lire(n);
      const corps = { compteur: envoi, partie: partie,
                      empreinte: (B.defs && B.defs.empreinte) || '' };
      return appel('parties/' + n, corps).then(function (res) {
        if (res.statut === 409) {
          const s = (res.corps && res.corps.serveur) || {};
          noterServeur(n, s);
          conflits[n] = { local: Sauvegarde.apercu(n), serveur: apercuDe(s.partie),
                          compteur: s.compteur || 0, partie: s.partie !== undefined ? s.partie : null };
          prevenir();
          return { conflit: true };
        }
        if (!res.ok) { recevoirCompte(res); return null; }
        if (force) Sauvegarde.poserCompteur(n, envoi);
        noterServeur(n, { compteur: envoi, sauvee_le: res.corps.sauvee_le, apercu: Sauvegarde.apercu(n) });
        noterVu(n, envoi, envoi);
        delete conflits[n];
        derniereMontee = Date.now();
        prevenir();
        return { monte: envoi };
      }, panne);
    });
  }

  /** La partie du serveur descend et remplace celle d'ici, TELLE QU'ELLE EST :
      elle garde sa date de sauvegarde, et le compteur local se pose sur le sien —
      la prochaine sauvegarde repart de la. */
  function prendre(n) {
    return file(function () {
      if (etat !== 'ouvert') return null;
      const c = conflits[n];
      if (c && c.partie !== undefined && c.partie !== null) { poser(n, c.partie, c.compteur); return { pris: true }; }
      return appel('parties/' + n, undefined, 'GET').then(function (res) {
        if (!res.ok) { recevoirCompte(res); return null; }
        // ⚠️ Une reponse 200 SANS le champ `partie` n'est pas une case vide : le
        // serveur en met toujours un, null compris (`comptes.lire_partie`). Vider
        // la case d'ici sur une reponse qu'on ne comprend pas — un proxy, une
        // page d'erreur en JSON — serait perdre la partie pour de bon.
        if (!res.corps || !('partie' in res.corps)) return null;
        poser(n, res.corps.partie, res.corps.compteur || 0);
        return { pris: true };
      }, panne);
    });
  }

  function poser(n, partie, compteur) {
    // ⚠️ RIEN NE SE POSE SOUS LES PIEDS DE QUELQU'UN QUI JOUE — et la garde est
    // ICI, pas avant la requete : entre la demande et la reponse, il se passe une
    // seconde, et une seconde suffit pour presser JOUER. La partie descendue
    // serait alors ecrasee dix secondes plus tard par la sauvegarde automatique
    // de celle qu'on joue, et l'autre appareil aurait perdu sa soiree sans que
    // personne ne comprenne. Elle devient une question, posee au retour au titre.
    if (n === Sauvegarde.emplacement() && B.etat !== 'titre') {
      conflits[n] = { local: Sauvegarde.apercu(n), serveur: apercuDe(partie), compteur: compteur, partie: partie };
      prevenir();
      return false;
    }
    if (partie) Sauvegarde.poser(n, partie); else Sauvegarde.effacer(n);
    Sauvegarde.poserCompteur(n, compteur);
    noterServeur(n, { compteur: compteur, apercu: apercuDe(partie) });
    noterVu(n, compteur, compteur);
    delete conflits[n];
    prevenir(n);
    return true;
  }

  /** « GARDER CELLE D'ICI » : la mienne monte par-dessus celle du serveur. */
  function garder(n) { return monter(n, true); }

  // --- Les moments ou un instantane monte ---------------------------------------------

  /** Chaque ecriture locale passe ici (`Sauvegarde.surEcriture`). ⚠️ Elle ne
      monte pas a chaque fois : dix secondes de jeu ne valent pas une requete. */
  function apresEcriture(n) {
    if (etat !== 'ouvert') return null;
    if (Date.now() - derniereMontee < REPOS_MS) return null;
    derniereMontee = Date.now();
    return monter(n);
  }

  /** L'onglet s'en va pour de bon : `sendBeacon` est le seul appel qui survit a
      la fermeture d'une page sur telephone. ⚠️ POST, jamais PUT — il ne sait
      faire que ca —, et un Blob `application/json`, sinon Flask ne lit pas le
      corps. Personne ne lira la reponse : rien ici ne met l'etat a jour. */
  function partir() {
    if (etat !== 'ouvert') return false;
    const n = Sauvegarde.emplacement();
    const compteur = Sauvegarde.compteur(n);
    if (compteur <= 0) return false;
    const temoin = vu(n);
    if (temoin && temoin.envoye === compteur && temoin.serveur === compteurServeur(n)) return false;
    if (decision(n) === 'trancher') return false;
    const nav = fenetre && fenetre.navigator;
    if (!nav || !nav.sendBeacon) return false;
    const texte = JSON.stringify({ compteur: compteur, partie: Sauvegarde.lire(n),
                                   empreinte: (B.defs && B.defs.empreinte) || '' });
    try {
      const paquet = typeof fenetre.Blob === 'function'
        ? new fenetre.Blob([texte], { type: 'application/json' }) : texte;
      const parti = !!nav.sendBeacon(base + 'parties/' + n, paquet);
      //: On note ce qu'on a envoye : le beacon ne rend pas de reponse, mais la
      //: case est a jour des deux cotes si elle est arrivee, et une montee de
      //: plus au prochain chargement ne couterait qu'une requete.
      if (parti) noterVu(n, compteur, compteur);
      return parti;
    } catch (e) { return false; }
  }

  // --- Le compte lui-meme --------------------------------------------------------------

  /** ⚠️ Ce que le serveur garde du nom de l'appareil, et rien de plus : de quoi
      reconnaitre « le téléphone » d'« ordinateur » dans sa liste. */
  function nomAppareil() {
    const ua = String((fenetre && fenetre.navigator && fenetre.navigator.userAgent) || '');
    if (/Quest|OculusBrowser/i.test(ua)) return 'casque';
    if (/iPad|Tablet/i.test(ua)) return 'tablette';
    if (/Mobi|Android|iPhone/i.test(ua)) return 'téléphone';
    return 'ordinateur';
  }

  function entrer(chemin, donnees) {
    return file(function () {
      const corps = Object.assign({ appareil: nomAppareil() }, donnees || {});
      return appel(chemin, corps).then(function (res) {
        const ok = recevoirCompte(res);
        if (ok && etat === 'ouvert') ranger();
        return etatPublic();
      }, function () { panne(); return etatPublic(); });
    });
  }

  function inscrire(donnees) { return entrer('inscription', donnees); }
  function connecter(donnees) { return entrer('connexion', donnees); }

  /** ⚠️ La partie en cours monte AVANT de partir : se deconnecter ne doit pas
      laisser sur le serveur une version plus vieille que celle qu'on a jouee. */
  function deconnecter() {
    monter(Sauvegarde.emplacement());
    return file(function () {
      return appel('deconnexion').then(function (res) {
        recevoirCompte(res);
        return etatPublic();
      }, function () { panne(); return etatPublic(); });
    });
  }

  function init(w, racine) {
    fenetre = w;
    try { stockage = w.localStorage || null; } catch (e) { stockage = null; }
    base = (racine && racine.dataset && racine.dataset.urlCompte) || '/api/compte/';
    sync = lireSync();
    Sauvegarde.surEcriture(apresEcriture);
    return ouvrir();
  }

  return { init, ouvrir, etat: etatPublic, surChangement, decision, conflit: function (n) { return conflits[n] || null; },
           inscrire, connecter, deconnecter, monter, prendre, garder, partir, apresEcriture, ranger,
           REPOS_MS };
})();
