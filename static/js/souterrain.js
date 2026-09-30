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

  return { SLUG, est, ici };
})();
