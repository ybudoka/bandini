/* Bandini — le defi du jour, cote jeu (M14, 5e vague).

   Le jeu a six defis (`B.defs.defis`) : une prime, un chrono, et la prime ne se paie qu'UNE
   fois. Le SERVEUR dit lequel est celui d'aujourd'hui (`GET /api/defi` : `{ date, defi }`) —
   un jeu qui tourne dans le navigateur ne decide pas seul du jour qu'on est —, et le reussir
   paie sa prime UNE FOIS PAR JOUR, meme s'il a deja ete fait.

   ⚠️ IL N'Y A PAS DE CLASSEMENT : le tableau des scores est parti le 17 sept. 2026 (demande de
   Martin) et le « classement du jour » de la fiche partait avec lui. Voir `app/defi.py`.

   ⚠️ SANS RESEAU, IL N'Y A PAS DE DEFI DU JOUR — et le jeu ne s'en apercoit pas. Le defi du
   jour est un bonus, jamais une condition : `duJour()` rend null, le titre ne dit rien, les
   six defis se jouent comme avant. Pas de repli sur l'horloge du telephone : c'est justement
   ce qu'on evite en demandant la date au serveur.

   ⚠️ « DEJA PAYE AUJOURD'HUI » SE COMPARE A LA DATE DU SERVEUR (`B.partie.defiDuJour.date`),
   jamais a un slug ni a l'horloge locale : deployer un defi de plus change la rotation en
   pleine journee, et deux defis du jour le meme jour ne doivent pas payer deux fois.

   ⚠️ CE QUE LE SERVEUR DIT SE VERIFIE : une date qui n'en est pas une, ou un defi que ce
   catalogue ne connait pas (version d'avant, version d'apres), est ignore — comme s'il n'y en
   avait pas. */

const Defi = (function () {
  'use strict';

  //: Au plus une demande toutes les dix minutes : le titre revient souvent, le jour non.
  const REPOS_MS = 10 * 60 * 1000;

  let fenetre = null, url = '/api/defi', courant = null, dernier = 0;
  const abonnes = [];

  function valider(d) {
    if (!d || typeof d !== 'object' || typeof d.defi !== 'string') return null;
    if (typeof d.date !== 'string' || !/^\d{4}-\d{2}-\d{2}$/.test(d.date)) return null;
    // ⚠️ La fiche du catalogue se cherche UNE fois, ici, a la porte : `courant` ne porte jamais un
    // defi que ce catalogue ne connait pas, donc rien d'autre n'a besoin de le reverifier.
    const def = ((B.defs && B.defs.defis) || []).find(function (q) { return q.slug === d.defi; });
    return def ? { date: d.date, slug: d.defi, def: def } : null;
  }

  function prevenir() { for (const f of abonnes) f(courant); }
  function surChangement(f) { abonnes.push(f); }

  /** Demande le defi d'aujourd'hui. ⚠️ Rend TOUJOURS une promesse qui se resout (jamais ne
      rejette) : un reseau coupe, une page d'erreur ou un JSON illisible valent « pas de defi
      du jour », et rien de plus. */
  function actualiser() {
    dernier = Date.now();
    return Promise.resolve().then(function () {
      return fenetre.fetch(url, { cache: 'no-store', credentials: 'omit' });
    }).then(function (r) { return r && r.ok ? r.json() : null; })
      .catch(function () { return null; })
      .then(function (d) {
        courant = valider(d);
        prevenir();
        return duJour();
      });
  }

  function init(w, racine) {
    fenetre = w;
    url = (racine && racine.dataset && racine.dataset.urlDefi) || '/api/defi';
    return actualiser();
  }

  /** Le titre revient, ou la page se rouvre : au plus une demande par `REPOS_MS`. */
  function rafraichir() {
    if (!fenetre || Date.now() - dernier < REPOS_MS) return Promise.resolve(duJour());
    return actualiser();
  }

  /** { date, slug, def } — `def` est la fiche du catalogue —, ou null. */
  function duJour() { return courant; }

  function estDuJour(slug) { return !!courant && courant.slug === slug; }

  /** Cette partie a-t-elle DEJA touche la prime du jour, aujourd'hui (date du serveur) ? */
  function dejaPaye() {
    const f = B.partie && B.partie.defiDuJour;
    return !!courant && !!f && f.date === courant.date;
  }

  /** Vrai si reussir `slug` MAINTENANT paie la prime du jour : c'est le defi d'aujourd'hui,
      et cette partie ne l'a pas encore touchee aujourd'hui. */
  function aPayer(slug) { return estDuJour(slug) && !dejaPaye(); }

  /** La prime du jour est encaissee : la partie s'en souvient, avec la date du serveur. */
  function noterFait(slug, temps) {
    if (!courant) return;
    B.partie.defiDuJour = { date: courant.date, slug: slug, temps: temps };
  }

  return { init, actualiser, rafraichir, surChangement, duJour, estDuJour, dejaPaye, aPayer, noterFait, REPOS_MS };
})();
