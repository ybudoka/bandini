/* Bandini — le travailleur hors ligne (service worker).

   Demande de Martin : « est-ce compliqué de faire du jeu une webapp
   installable ? », puis « jouable hors ligne ».

   ⚠️ PAS DANS LA PAGE : servi a la racine par `routes.travailleur`, qui pose
   `HORS_LIGNE` devant ce fichier (la coquille, les sons, l'empreinte — voir
   app/hors_ligne.py). Un travailleur ne controle que son dossier, et
   /static/js/ n'est pas la page.

   UNE SEULE REGLE : LE RESEAU A TOUJOURS RAISON. Ce que le travailleur nomme
   part d'abord au reseau — le cache HTTP du navigateur fait deja le rapide —,
   et chaque reponse du reseau remet le cache a jour. Le cache ne parle que
   quand le reseau se tait, ou quand le serveur est en panne (un 502 derriere
   Caddy est une ville qu'on ne peut pas ouvrir, pas une ville qui n'existe pas).

   ⚠️ Pourquoi pas « le cache d'abord », qui est plus vite hors ligne : le serveur
   de dev ne change pas le `?v=` quand on edite un script. Un travailleur qui
   repond du cache servirait l'ancien fichier, et il faudrait recharger deux fois
   pour voir sa propre modification — le piege qui fait desinstaller un
   travailleur. En ligne, le cache HTTP rend le reseau d'abord gratuit.

   ⚠️ Les mp3 ne portent pas de `?v=` : un bruitage regenere garde son nom. C'est
   la meme regle qui le purge — le reseau d'abord le remplace des qu'on le joue
   en ligne — et un son qui n'est plus dans le dossier sort du cache a
   l'activation.

   ⚠️ Tout ce qu'il ne nomme pas passe sans lui : le compte et les parties sur
   le serveur (M14). Rien de ce qui ECRIT ne se garde, et rien d'autre qu'un
   GET. */

'use strict';

const COQUILLE = 'bandini-coquille-' + HORS_LIGNE.empreinte;
const SONS = 'bandini-sons';
const ORIGINE = self.location.origin;
//: ⚠️ `Vary` ne compte pas : nginx ajoute `Vary: Accept-Encoding`, et une page qui
//: se met a porter un cookie (M14) ne doit pas perdre sa ville hors ligne.
const SANS_VARY = { ignoreVary: true };

//: Les chemins de la coquille SANS leur requete : `jeu.js?v=1.2` et `jeu.js?v=1.3`
//: sont le meme fichier. Une page d'une version plus neuve que le travailleur se
//: garde donc quand meme a mesure qu'elle se charge — hors ligne, elle retrouvera
//: ses scripts, pas ceux d'avant.
const CHEMINS = new Set(HORS_LIGNE.coquille.map(function (u) { return new URL(u, ORIGINE).pathname; }));
const FICHIERS_SONS = new Map(HORS_LIGNE.audio.fichiers.map(function (f) {
  return [HORS_LIGNE.audio.dossier + f.nom, f];
}));

let telechargement = null;

self.addEventListener('install', function (ev) {
  // ⚠️ `no-cache` : on revalide (un 304 ne coute rien), mais on ne prend pas
  // pour argent comptant ce que le cache HTTP garde sept jours.
  ev.waitUntil(caches.open(COQUILLE).then(function (cache) {
    return cache.addAll(HORS_LIGNE.coquille.map(function (u) { return new Request(u, { cache: 'no-cache' }); }));
  }).then(function () { return self.skipWaiting(); }));
});

self.addEventListener('activate', function (ev) {
  ev.waitUntil(caches.keys().then(function (noms) {
    return Promise.all(noms.filter(function (n) {
      return n.indexOf('bandini-coquille-') === 0 && n !== COQUILLE;
    }).map(function (n) { return caches.delete(n); }));
  }).then(function () {
    return caches.open(SONS).then(function (cache) {
      return cache.keys().then(function (cles) {
        return Promise.all(cles.filter(function (r) { return !FICHIERS_SONS.has(new URL(r.url).pathname); })
          .map(function (r) { return cache.delete(r); }));
      });
    });
  }).then(function () { return self.clients.claim(); }));
});

self.addEventListener('fetch', function (ev) {
  const requete = ev.request;
  if (requete.method !== 'GET') return;
  const url = new URL(requete.url);
  if (url.origin !== ORIGINE) return;
  if (requete.mode === 'navigate') {
    // `/?trace=1` est la meme page : hors ligne, elle s'ouvre aussi.
    if (url.pathname === HORS_LIGNE.accueil) ev.respondWith(reseauDabord(ev, COQUILLE, HORS_LIGNE.accueil));
    return;
  }
  if (FICHIERS_SONS.has(url.pathname)) ev.respondWith(reseauDabord(ev, SONS, url.pathname));
  else if (CHEMINS.has(url.pathname)) ev.respondWith(reseauDabord(ev, COQUILLE, url.pathname + url.search));
});

/** Le reseau, et le cache s'il se tait ou s'il est en panne. */
function reseauDabord(ev, nomCache, cle) {
  function garde(panne) {
    return caches.open(nomCache).then(function (cache) { return cache.match(cle, SANS_VARY); }).then(function (gardee) {
      if (gardee) return gardee;
      if (panne instanceof Response) return panne;
      throw panne;
    });
  }
  return fetch(ev.request).then(function (reponse) {
    if (!reponse.ok) return garde(reponse);
    if (reponse.status === 200 && reponse.type === 'basic' && !reponse.redirected) {
      const copie = reponse.clone();
      ev.waitUntil(caches.open(nomCache).then(function (cache) { return ranger(cache, cle, copie); }));
    }
    return reponse;
  }, garde);
}

/** Remettre une reponse au cache — sauf si c'est la meme, deja la.

    ⚠️ Chaque son joue en ligne passe par ici : reecrire deux cents Ko pour un
    fichier qui n'a pas bouge, a chaque partie, userait le stockage pour rien. */
function ranger(cache, cle, reponse) {
  return cache.match(cle, SANS_VARY).then(function (avant) {
    if (avant && pareilles(avant, reponse)) return null;
    return cache.put(cle, reponse);
  });
}

function pareilles(a, b) {
  const ea = a.headers.get('ETag'), eb = b.headers.get('ETag');
  if (ea || eb) return ea === eb;
  const la = a.headers.get('Last-Modified');
  return !!la && la === b.headers.get('Last-Modified')
    && a.headers.get('Content-Length') === b.headers.get('Content-Length');
}

// --- Les sons, tous d'un coup (OPTIONS > LES SONS HORS LIGNE) ------------------------

self.addEventListener('message', function (ev) {
  const quoi = ev.data && ev.data.type;
  if (quoi === 'tout-telecharger') {
    if (!telechargement) {
      telechargement = toutTelecharger().catch(function () { /* on redemandera */ })
        .then(function () { telechargement = null; return annoncer(); });
    }
    ev.waitUntil(Promise.all([annoncer(), telechargement]));
  } else if (quoi === 'etat') {
    ev.waitUntil(annoncer());
  }
});

function dejaGardes(cache) {
  return cache.keys().then(function (cles) {
    return new Set(cles.map(function (r) { return new URL(r.url).pathname; }));
  });
}

/** Ce qui est garde : tout le monde le recoit, chaque onglet ouvert. */
function annoncer() {
  return caches.open(SONS).then(dejaGardes).then(function (gardes) {
    let sons = 0, octets = 0, total = 0;
    FICHIERS_SONS.forEach(function (f, chemin) {
      total += f.octets;
      if (gardes.has(chemin)) { sons++; octets += f.octets; }
    });
    const etat = { type: 'hors-ligne', sons: sons, total: FICHIERS_SONS.size, octets: octets,
                   octets_total: total, en_cours: !!telechargement };
    return self.clients.matchAll({ includeUncontrolled: true }).then(function (fenetres) {
      fenetres.forEach(function (f) { f.postMessage(etat); });
    });
  });
}

/** Trois a la fois, en disant ou on en est tous les dix fichiers.

    ⚠️ Un fichier qui echoue ne fait pas echouer les autres : on repassera par
    le bouton, et seuls les manquants repartiront. */
function toutTelecharger() {
  return caches.open(SONS).then(function (cache) {
    return dejaGardes(cache).then(function (gardes) {
      const reste = Array.from(FICHIERS_SONS.keys()).filter(function (c) { return !gardes.has(c); });
      let i = 0, faits = 0;
      function suivant() {
        if (i >= reste.length) return Promise.resolve();
        const chemin = reste[i++];
        return fetch(chemin, { cache: 'no-cache' })
          .then(function (r) { return r.ok ? cache.put(chemin, r) : null; })
          .catch(function () { return null; })
          .then(function () { faits++; return faits % 10 === 0 ? annoncer() : null; })
          .then(suivant);
      }
      return Promise.all([suivant(), suivant(), suivant()]);
    });
  });
}
