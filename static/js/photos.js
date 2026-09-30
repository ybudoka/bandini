/* Bandini — des photos pour le Clairon (docs/jalons/des-photos-pour-le-clairon.md).

   Au declic du mode photo (`Jeu.majPhoto`), le jeu juge CE QUI EST DANS LE CADRE — les entites a l'ecran de la
   vue detachee —, jamais les pixels : un char en feu (ou un batiment qui brule), un char qui vole, une poursuite,
   une figure du quartier ; et TOI, si tu es dans le cadre d'une poursuite. La meilleure photo du jour attend dans
   la partie (`partie.photo`). Louise Tremblay-Dion, devant le kiosque, en achete UNE par jour (`accueillir`, son
   menu) ; la une du lendemain la nomme (`ligneDuClairon`). Le piege : ta face en une, et la police t'a vu
   (`matin` : une etoile, le jour ou le journal sort).

   ⚠️ RIEN AU DE : le cadre est une question d'entites et de rectangle ; le prix, une table (`app/photos.py`). */

const Photos = (function () {
  'use strict';

  function donnees() { return B.defs && B.defs.photos; }

  function dans(vue, x, y) { return x >= vue.x && x < vue.x + VW && y >= vue.y && y < vue.y + VH; }

  /** Les sujets du cadre de la vue `vue` (coin haut-gauche, en pixels de ville) : une liste de slugs. */
  function sujets(vue) {
    const d = donnees(), r = d.regles, ph = B.defs.conduite.physique, j = B.joueur, out = [];
    let police = false, moi = false;
    for (const e of B.entites) {
      if (!dans(vue, e.x, e.y)) continue;
      if (e.type === 'vehicule') {
        const brule = e.def && e.def.reservoir !== false && e.etat !== 'epave' && e.vieMax && e.vie / e.vieMax < ph.feu_sous;
        if (brule) out.push('feu');
        if ((e.z || 0) > r.vol_z) out.push('vol');
        if (e.conducteur === 'police') police = true;
        if (j && j.dansVehicule === e) moi = true;
      } else if (e.type === 'helico' || e.agent) {
        police = true;
      } else if (e.personnage && e.personnage !== 'louise') {
        out.push('personnage');
      }
      if (e === j && !j.dansVehicule) moi = true;
    }
    const feu = typeof Incendies !== 'undefined' ? Incendies.feuActif() : null;
    if (feu) { const q = Incendies.position(feu); if (dans(vue, q.x, q.y)) out.push('feu'); }
    const etoiles = (B.recherche && B.recherche.etoiles) || 0;
    if (police && etoiles > 0) out.push(moi ? 'toi' : 'poursuite');
    return out;
  }

  /** Ce que vaut un sujet (la poursuite : plus a chaque etoile). */
  function prix(sujet) {
    const d = donnees(), s = d.sujets[sujet];
    if (!s) return 0;
    return s.prix + (sujet === 'poursuite' ? d.regles.par_etoile * ((B.recherche && B.recherche.etoiles) || 0) : 0);
  }

  /** Le meilleur sujet du cadre, ou null. */
  function juger(vue) {
    let meilleur = null;
    for (const s of sujets(vue)) if (!meilleur || prix(s) > prix(meilleur)) meilleur = s;
    return meilleur;
  }

  /** Le declic : le cadre juge, la meilleure photo du jour gardee. Rend le sujet (ou null). */
  function declic(vue) {
    // ⚠️ Le Clairon voyage dans la suite du paquet (`Suite`) : sans lui, le cadre ne se juge pas.
    if (!donnees()) return null;
    const p = B.partie, s = juger(vue);
    if (!B.photo) return s;
    if (!s) { B.photo.dit = 'RIEN QUI VAILLE UNE UNE'; p.photoVide = p.jour; return null; }
    const vaut = prix(s), gardee = p.photo && p.photo.jour === p.jour ? p.photo : null;
    if (!gardee || vaut > gardee.prix) p.photo = { sujet: s, prix: vaut, jour: p.jour };
    B.photo.dit = 'PHOTO : ' + donnees().sujets[s].nom + ' — LOUISE EN DONNERAIT ' + vaut + ' $';
    return s;
  }

  // --- Louise --------------------------------------------------------------------------

  function dire(cle) {
    const d = donnees(), texte = d.repliques[cle], m = (B.defs.personnages || []).find(function (q) { return q.slug === 'louise'; });
    if (!texte) return;
    Hud.dialogue(m ? m.nom : 'LOUISE', [texte], 300, { slug: 'louise', humeur: cle === 'achat' || cle === 'toi' ? 'content' : 'neutre' });
    Son.Voix.chargerHistoire('clairon');
    if (Son.Voix.parler('louise-clairon-' + cle, {}) && B.dialogue) B.dialogue.voix = true;
  }

  /** On parle a Louise : la premiere fois elle se presente ; ensuite, elle regarde ta photo. */
  function accueillir(premiere) {
    const p = B.partie, d = donnees();
    if (!d) return;                       // la suite du paquet n'est pas encore là (`Suite`)
    if (premiere) { dire('salut'); return; }
    if (p.uneVendue === p.jour) { dire('deja'); return; }
    const ph = p.photo;
    if (!ph) { dire(p.photoVide === p.jour ? 'vide' : 'rien'); return; }
    if (p.jour - ph.jour > d.regles.fraiche_jours) { dire('vieille'); p.photo = null; return; }
    Hud.ouvrirMenu({
      titre: 'LE CLAIRON DE LA BAIE', sur: p.argent + ' $',
      items: [{ libelle: 'VENDRE : ' + d.sujets[ph.sujet].nom, detail: ph.prix + ' $', actif: true,
                faire: function () { vendre(); return true; } }],
    });
  }

  /** Louise achete : l'argent, la une de demain, et la photo n'est plus a toi. */
  function vendre() {
    const p = B.partie, ph = p.photo;
    if (!ph) return false;
    Missions.encaisser(ph.prix, 'PHOTO AU CLAIRON');
    p.une = { sujet: ph.sujet, jour: p.jour };
    p.uneVendue = p.jour;
    p.photo = null;
    dire(ph.sujet === 'toi' ? 'toi' : 'achat');
    return true;
  }

  // --- La une du lendemain ---------------------------------------------------------------

  /** La ligne du Clairon, le matin d'apres la vente (ou null). */
  function ligneDuClairon() {
    const p = B.partie, d = donnees();
    if (!p || !d || !p.une || p.une.jour !== p.jour - 1) return null;
    return d.sujets[p.une.sujet].titre + ' — PHOTO : L. TREMBLAY-DION';
  }

  /** Le matin (`Missions.nouveauJour`) : ta face en une, et la police t'a vu. Rend vrai s'il s'est passe quelque chose. */
  function matin() {
    const p = B.partie, d = donnees();
    if (!p || !d || !p.une || p.une.jour !== p.jour - 1 || p.une.sujet !== 'toi' || p.une.vue) return false;
    p.une.vue = true;
    Police.etoilesAuMoins(d.regles.etoiles_toi);
    return true;
  }

  return { sujets, prix, juger, declic, accueillir, vendre, ligneDuClairon, matin };
})();
