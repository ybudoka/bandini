/* Bandini — l'annee de Baie-des-Brumes : quarante jours, douze mois, quatre saisons (`app/calendrier.py`,
   `B.defs.calendrier`).

   ⚠️ UNE PURE FONCTION DU JOUR : le jour 1 est le premier janvier (une partie neuve commence au jour
   `depart`, le 1er mai, sans neige — `etatInitial`), et la meme annee
   revient tous les quarante jours, pour tout le monde. Rien a sauvegarder, aucun de. Ce sont les
   jalons qui la LISENT (le pont de glace, la motoneige, la Saint-Jean, le cine-parc…) qui en
   dependent — la neige tombe l'hiver, et le verglas les trois derniers jours de mars. */

const Calendrier = (function () {
  'use strict';

  function donnees() { return B.defs && B.defs.calendrier; }

  /** Le jour d'une partie dans son annee (1 a 40). */
  function jourDeLAnnee(jour) {
    const d = donnees();
    return d ? ((jour - 1) % d.annee + d.annee) % d.annee + 1 : jour;
  }

  function mois(jour) {
    const d = donnees();
    if (!d) return null;
    const j = jourDeLAnnee(jour);
    let nom = d.mois[0][0];
    for (const m of d.mois) if (j >= m[1]) nom = m[0];
    return nom;
  }

  function saison(jour) {
    const d = donnees(), m = mois(jour);
    return d && m ? d.saisons[m] : null;
  }

  /** Ce jour-la est-il cette date de l'annee (`saint_jean`, `demenagement`, `noel`) ? */
  function estLe(date, jour) {
    const d = donnees();
    return !!d && jourDeLAnnee(jour) === d.dates[date];
  }

  /** Maintenant, pour la partie. */
  function saisonDuJour() { return B.partie ? saison(B.partie.jour) : null; }

  //: Le mois tel qu'on l'ecrit a l'ecran (le paquet a des slugs sans accents).
  const ECRITS = { janvier: 'JANVIER', fevrier: 'FÉVRIER', mars: 'MARS', avril: 'AVRIL', mai: 'MAI', juin: 'JUIN',
                   juillet: 'JUILLET', aout: 'AOÛT', septembre: 'SEPTEMBRE', octobre: 'OCTOBRE', novembre: 'NOVEMBRE',
                   decembre: 'DÉCEMBRE' };

  /** « JOUR 10 · MARS » : le jour de la partie, et le mois ou il tombe (le HUD, la pause). */
  function jourEcrit(jour) {
    const m = mois(jour);
    return 'JOUR ' + jour + (m ? ' · ' + ECRITS[m] : '');
  }

  /** Le jour de partie ou commence le mois qui suit `jour` (janvier de l'annee suivante apres
      decembre). La triche MOIS SUIVANT. */
  function premierDuMoisSuivant(jour) {
    const d = donnees(), j = jourDeLAnnee(jour);
    for (const m of d.mois) if (m[1] > j) return jour + (m[1] - j);
    return jour + (d.annee - j) + 1;
  }

  function moisEcrit(jour) { const m = mois(jour); return m ? ECRITS[m] : ''; }

  return { donnees, jourDeLAnnee, mois, saison, estLe, saisonDuJour, jourEcrit, premierDuMoisSuivant, moisEcrit };
})();
