/* Des missions en CHAPITRES (30 sept. 2026, docs/jalons/des-missions-en-chapitres.md).

   Demande de Martin : « les missions doivent durer au moins 5 à 10 minutes chacune ». Un chapitre est une mission
   dont les objectifs sont coupés par des marqueurs `acte` : chacun a son donneur, pose un point de reprise, et se
   reprend après l'hôpital ou le poste. Ce module tient ce qui est PROPRE aux chapitres ; `histoire.js` l'appelle
   là où une mission commence, avance, échoue et réussit. */
const Chapitres = (function () {
  /** Les marqueurs `acte` : `[etape, donneur]`, dans l'ordre. ⚠️ Des OBJECTIFS quand ils sont là ; sinon du
      catalogue (`m.actes`, `missions._completer`) — les objectifs n'arrivent qu'avec `/api/mission/<slug>`, et le
      téléphone, les bulles et le carnet doivent savoir quel donneur attend avant. */
  function marqueurs(m) {
    if (!m) return [];
    if (!m.objectifs) return m.actes || [];
    const r = [];
    m.objectifs.forEach(function (o, i) { if (o && o.type === 'acte') r.push([i, o.donneur]); });
    return r;
  }

  /** Les étapes des marqueurs `acte`, dans l'ordre. */
  function actes(m) { return marqueurs(m).map(function (a) { return a[0]; }); }

  /** Le rang (0 = le premier) de l'acte qui contient `etape` ; -1 hors chapitre. */
  function acteA(m, etape) {
    const a = actes(m);
    let k = -1;
    for (let i = 0; i < a.length; i++) if (a[i] <= etape) k = i;
    return k;
  }

  function chapitres() { const p = B.partie; return p.chapitres || (p.chapitres = {}); }

  /** Le donneur de l'acte : celui de l'acte EN COURS si c'est la mission courante, celui de l'acte où l'on
      reprendra sinon ; celui de la mission hors chapitre. */
  function donneurDe(m) {
    if (!m) return null;
    const a = actes(m);
    if (!a.length) return m.donneur;
    const pm = B.partie.mission;
    // ⚠️ Une mission FAITE : le donneur du dernier acte — la scène de fin se joue chez lui (Josée, pas M. Bilodeau).
    const etape = pm && pm.slug === m.slug ? Math.max(0, pm.etape)
      : B.partie.missionsFaites[m.slug] || fait(m) ? Infinity : depart(m);
    return marqueurs(m)[Math.max(0, acteA(m, etape))][1] || m.donneur;
  }

  /** Le marqueur commence : l'acte d'avant est FAIT (sa mission remplacée aussi, pour tout ce qui lit encore
      `missionsFaites` — `arrive_apres`, le carnet), puis le carton et le point de reprise. */
  function ouvrirActe(m, o, etape) {
    const p = B.partie, pm = p.mission, j = B.joueur, k = acteA(m, etape);
    if (k > 0 && m.remplace && m.remplace[k - 1] && !p.missionsFaites[m.remplace[k - 1]]) p.missionsFaites[m.remplace[k - 1]] = p.jour;
    chapitres()[m.slug] = etape;
    const ici = Histoire.ouEstLeJoueurEnVille();
    const v = j.dansVehicule;
    pm.reprise = { etape: etape, x: ici.x, y: ici.y,
                   char: v && v.def ? { slug: v.def.slug, couleur: v.couleur || null } : null,
                   arme: j.arme || 'poings', mun: p.armes[j.arme] ? p.armes[j.arme].mun : null };
    Hud.message(o.texte, 200);
    Missions.sauvegarderPartie();
  }

  /** L'étape du marqueur où commencer : le premier acte dont la mission remplacée n'est pas faite, ou plus
      loin si la partie a déjà atteint un acte (`chapitres[slug]`, PLUS TARD). 0 hors chapitre. */
  function depart(m) {
    const a = actes(m);
    if (!a.length) return 0;
    const faites = B.partie.missionsFaites;
    let k = 0;
    while (k < a.length - 1 && m.remplace && m.remplace[k] && faites[m.remplace[k]]) k++;
    return Math.max(a[k], chapitres()[m.slug] || 0);
  }

  /** Un chapitre dont toutes les missions remplacées sont faites l'est aussi (une vieille partie). */
  function fait(m) {
    return !!(m && m.remplace && m.remplace.length && m.remplace.every(function (s) { return B.partie.missionsFaites[s]; }));
  }

  /** La mission réussie : le chapitre n'a plus d'acte en attente, et ses missions remplacées sont faites. */
  function reussi(m) {
    const p = B.partie;
    delete chapitres()[m.slug];
    (m.remplace || []).forEach(function (s) { if (!p.missionsFaites[s]) p.missionsFaites[s] = p.jour; });
  }

  return { actes, acteA, donneurDe, ouvrirActe, reussi, depart, fait };
})();
