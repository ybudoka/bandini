/* Bandini — le dojo du quartier : LES COURS de Mireille Dion, et la lecon sur le
   tatami (docs/jalons/le-dojo-du-quartier.md).

   Python decide (`app/dojo.py` : les heures, le temps, les reussites ; `app/techniques.py` :
   les cours et leurs prix), ce module joue. ⚠️ Aucun `B.rng()` ici : une lecon ne decale
   pas un seul de du reste de la ville. */

const Dojo = (function () {
  'use strict';

  //: Les styles, dans l'ordre du menu : chacun son en-tete.
  const STYLES = [['boxe', 'BOXE'], ['karate', 'KARATÉ'], ['judo', 'JUDO'], ['jiujitsu', 'JIU-JITSU']];

  function regles() { return B.defs.dojo; }

  /** Le maillon d'avant, pour une tape de la chaine : le circulaire (rang 5) attend l'uppercut. */
  function avant(t) {
    if (t.geste !== 'tape' || t.rang <= 1) return null;
    return (B.defs.techniques || []).find(function (q) { return q.geste === 'tape' && q.rang === t.rang - 1; }) || null;
  }

  /** Ou en est ce cours : 'appris', 'paye' (a reprendre), 'verrouille' (le maillon d'avant
      manque) ou 'a_vendre'. */
  function etatDuCours(slug) {
    const p = B.partie, t = Techniques.def(slug);
    if (p.techniques && p.techniques[slug]) return 'appris';
    if (p.coursPayes && p.coursPayes[slug]) return 'paye';
    const a = avant(t);
    if (a && !Techniques.sait(B.joueur, a.slug)) return 'verrouille';
    return 'a_vendre';
  }

  /** La nuit, le MENU ferme (comme tous les comptoirs du jeu), pas la porte. */
  function ferme() { return !Missions.ouvert({ heures: regles().heures }); }

  /** Payer (une fois) et commencer. Rend true si la lecon part. ⚠️ Un cours rate reste
      PAYE : on recommence sans repayer. */
  function acheter(slug) {
    const etat = etatDuCours(slug), t = Techniques.def(slug);
    if (ferme() || etat === 'appris' || etat === 'verrouille') return false;
    if (etat === 'a_vendre') {
      if (!Missions.payer(t.prix, t.nom.toUpperCase())) return false;
      B.partie.coursPayes = B.partie.coursPayes || {};
      B.partie.coursPayes[slug] = true;
    }
    return commencer(slug);
  }

  function menuCours() {
    const items = [];
    if (ferme()) {
      items.push({ libelle: 'FERMÉ — OUVRE À ' + Math.round(regles().heures[0] * 24) + ' H', actif: false });
      return { titre: 'LES COURS', sur: B.partie.argent + ' $', items: items };
    }
    for (const [style, titre] of STYLES) {
      items.push({ entete: titre, libelle: '', actif: false });
      for (const t of (B.defs.techniques || []).filter(function (q) { return q.style === style; })) {
        const etat = etatDuCours(t.slug), a = avant(t);
        const detail = { appris: 'APPRIS', paye: 'PAYÉ — À REPRENDRE',
                         verrouille: 'APRÈS ' + (a ? a.nom.toUpperCase() : ''), a_vendre: t.prix + ' $' }[etat];
        items.push({ libelle: t.nom.toUpperCase(), detail: detail,
                     actif: etat === 'a_vendre' || etat === 'paye',
                     // Une lecon qui part FERME le menu (`true`) : on est sur le tatami.
                     faire: function () { return acheter(t.slug); } });
      }
    }
    return { titre: 'LES COURS', sur: B.partie.argent + ' $', items: items };
  }

  // La lecon elle-meme : la 4e tache. Ici, la seance seulement.
  function commencer(slug) { B.cours = { slug: slug }; return true; }

  return { menuCours, etatDuCours, acheter, commencer };
})();
