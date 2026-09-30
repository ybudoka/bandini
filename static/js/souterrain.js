/* Bandini — le grand garage souterrain, sous le Garage Rocco Bandini (docs/jalons/le-grand-garage-souterrain.md).

   Martin, 30 sept. 2026 : « le garage Bandini doit pouvoir stocker des vehicules que nous pourrons reprendre
   apres dans un grand garage souterrain ». Un BLOC DE CARTE sans passage en ville (`app/blocs/souterrain.py`) :
   on y descend au volant par le rideau de Ti-Guy (DESCENDRE AU SOUS-SOL), ou a pied par l'ascenseur de la piece
   du garage ; on remonte la rampe, et on est devant le rideau.

   ⚠️ LES CHARS RANGES VIVENT DANS LA PARTIE (`partie.souterrain.cases`), JAMAIS DANS LA MEMOIRE DU BLOC :
   `garnir` les pose a chaque descente, `ranger` les reecrit en remontant et a chaque sauvegarde. La ville oublie
   un char gare loin (`Vehicules.peupler`) ; celui-ci, jamais. */

const Souterrain = (function () {
  'use strict';

  const TT = 16;
  const SLUG = 'souterrain';

  /** Ce bloc-ci est-il le sous-sol ? */
  function est(slug) { return slug === SLUG; }

  /** Y est-on ? */
  function ici() { return !!(B.bloc && B.bloc.slug === SLUG); }

  //: Les cases d'un niveau, et de tout le sous-sol (`app/blocs/souterrain.py`, les memes nombres).
  const PAR_NIVEAU = 10, CASES_MAX = 20;

  /** Les cases ouvertes : dix par niveau achete. */
  function ouvertes() { return PAR_NIVEAU * ((B.partie.souterrain && B.partie.souterrain.niveaux) || 1); }
  /** Les cases ouvertes ou dort un char. */
  function occupees() { return B.partie.souterrain.cases.slice(0, ouvertes()).filter(Boolean).length; }
  function plein() { return occupees() >= ouvertes(); }

  /** Ce qu'on ecrit d'un char : comme le char de la planque, sans position. */
  function fiche(v) {
    return { slug: v.slug, sprite: v.sprite, couleur: v.couleur, vie: v.vie, vole: !!v.vole, aToi: !!v.aToi, mods: Garage.fiche(v) };
  }

  /** La case (son rang) sous le centre de ce char, ou -1. */
  function caseSous(cases, v) {
    for (let k = 0; k < cases.length; k++) {
      const q = cases[k];
      if (v.x >= q.x * TT && v.x < (q.x + q.l) * TT && v.y >= q.y * TT && v.y < (q.y + q.h) * TT) return k;
    }
    return -1;
  }

  /** Reecrit `partie.souterrain.cases` d'apres les chars de `entites` : chacun sur SA case s'il y est (et qu'elle
      est ouverte et libre), les autres — laisses dans l'allee — gares par Ti-Guy sur la premiere case libre. Une
      epave ne se range pas. Rend ce qui n'est pas un char : ce que le bloc peut garder (`Blocs.garder`).
      ⚠️ Ne retire rien : la sauvegarde l'appelle en plein sous-sol, les chars restent ou ils sont. */
  function ranger(entites, def) {
    const cases = def.bloc.souterrain.cases, n = ouvertes();
    const neuf = [];
    for (let k = 0; k < CASES_MAX; k++) neuf.push(null);
    const reste = [], sansPlace = [];
    for (const e of entites) {
      if (e.type !== 'vehicule') { reste.push(e); continue; }
      if (e.etat === 'epave') continue;
      const k = caseSous(cases, e);
      if (k >= 0 && k < n && !neuf[k]) neuf[k] = fiche(e); else sansPlace.push(e);
    }
    for (const e of sansPlace) {
      let k = 0;
      while (k < n && neuf[k]) k++;
      if (k < n) neuf[k] = fiche(e);
    }
    B.partie.souterrain.cases = neuf;
    return reste;
  }

  /** Pose les chars ranges sur leurs cases, a la descente. ⚠️ `couleur` DONNEE a `Vehicules.creer` : un char ne
      sans couleur tire un de, et tout le hasard de la partie glisse. */
  function garnir(def) {
    const cases = def.bloc.souterrain.cases, n = ouvertes();
    B.partie.souterrain.cases.forEach(function (c, k) {
      if (!c || k >= n || !cases[k] || !Vehicules.vehiculeDef(c.slug)) return;
      const q = cases[k];
      const v = Vehicules.creer(c.slug, (q.x + q.l / 2) * TT, (q.y + q.h / 2) * TT, q.cap,
                                { etat: 'stationne', sprite: c.sprite, couleur: c.couleur });
      if (!v) return;
      if (c.couleur) v.swaps = nuances(c.couleur);
      Garage.poser(v, c.mods);
      v.vie = Math.max(1, c.vie || v.vieMax); v.vole = !!c.vole; v.aToi = !!c.aToi;
      // Comme le char d'une planque : l'hiver, le balayage des deux-roues remisees ne l'emporte pas.
      v.aLaPlanque = true;
    });
  }

  return { SLUG, PAR_NIVEAU, CASES_MAX, est, ici, ouvertes, occupees, plein, fiche, ranger, garnir };
})();
