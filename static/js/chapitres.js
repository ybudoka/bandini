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

  /** L'étape du marqueur de l'acte EN COURS de `m` (la mission courante) ; null hors chapitre. */
  function marqueurDe(m) {
    const a = actes(m), pm = B.partie.mission;
    if (!a.length || !pm || pm.slug !== m.slug) return null;
    return a[Math.max(0, acteA(m, pm.etape))];
  }

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
    // Tous les actes d'avant sont passés (joués ici, ou faits par une vieille partie et sautés).
    for (let i = 0; i < k; i++) {
      const s = m.remplace && m.remplace[i];
      if (!s || p.missionsFaites[s]) continue;
      p.missionsFaites[s] = p.jour;
      Histoire.arriverApres(s);                          // Zed arrive après p02 : il est là pour l'acte suivant
    }
    chapitres()[m.slug] = etape;
    // Le chronomètre : l'acte d'avant se ferme (seulement s'il s'est joué ici — une reprise rouvre l'acte sans
    // fermer celui d'avant, dont la durée revient de la reprise).
    if (pm.acteOuvert === k - 1) {
      fermerActe(pm);
      // ⚠️ LA RÉPUTATION (2 oct. 2026, les autres arcs) : chaque acte compte pour le quartier de SON donneur, comme
      // sa mission comptait — le chapitre, à sa réussite, compte pour le dernier (`Histoire.reussir`).
      if (typeof Reputation !== 'undefined' && k > 0) Reputation.reussite({ slug: m.slug, donneur: marqueurs(m)[k - 1][1] });
    }
    pm.acteOuvert = k;
    const ici = Histoire.ouEstLeJoueurEnVille();
    const v = j.dansVehicule;
    pm.reprise = { etape: etape, x: ici.x, y: ici.y,
                   char: v && v.def ? { slug: v.def.slug, couleur: v.couleur || null } : null,
                   arme: j.arme || 'poings', mun: p.armes[j.arme] ? p.armes[j.arme].mun : null,
                   actes: (pm.actes || []).slice() };
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

  /** L'acte qui commence à `etape` a-t-il déjà été fait, comme la mission qu'il remplace (une vieille partie) ? */
  function dejaFait(m, etape) {
    const k = actes(m).indexOf(etape);
    return k >= 0 && !!(m.remplace && m.remplace[k] && B.partie.missionsFaites[m.remplace[k]]);
  }

  /** L'étape du marqueur qui suit `etape` ; au-delà du dernier, la fin des objectifs. */
  function marqueurSuivant(m, etape) {
    const a = actes(m).filter(function (e) { return e > etape; });
    return a.length ? a[0] : (m.objectifs || []).length;
  }

  /** Un chapitre dont toutes les missions remplacées sont faites l'est aussi (une vieille partie). */
  function fait(m) {
    return !!(m && m.remplace && m.remplace.length && m.remplace.every(function (s) { return B.partie.missionsFaites[s]; }));
  }

  // --- Le chronomètre (docs/jalons/des-missions-en-chapitres.md : c'est lui qui dit si on tient 5 à 10 minutes) ---

  /** Une image de mission jouée : `Histoire.maj` ne tourne ni sous un menu, ni en pause, ni dans un fondu. */
  function compter() {
    const pm = B.partie.mission;
    if (!pm) return;
    pm.images = (pm.images || 0) + 1;
    pm.imagesActe = (pm.imagesActe || 0) + 1;
  }

  /** L'acte fini : sa durée, en secondes, rejoint celles d'avant. */
  function fermerActe(pm) {
    pm.actes = (pm.actes || []).concat([Math.round((pm.imagesActe || 0) / 60)]);
    pm.imagesActe = 0;
  }

  /** La mission réussie : sa durée (et celle de chaque acte) dans `partie.durees`, le dernier temps et le meilleur. */
  function noterDuree(m) {
    const p = B.partie, pm = p.mission, d = p.durees || (p.durees = {});
    if (!pm) return;
    let actesFaits;
    if (actes(m).length) { fermerActe(pm); actesFaits = pm.actes; } else actesFaits = [Math.round((pm.images || 0) / 60)];
    const total = actesFaits.reduce(function (a, b) { return a + b; }, 0);
    const avant = d[m.slug];
    d[m.slug] = { dernier: total, meilleur: avant ? Math.min(avant.meilleur, total) : total, actes: actesFaits };
  }

  // --- La reprise ------------------------------------------------------------------------------------

  const FONDU = [32, 40, 32];
  const CAP = { '>': 0, '<': Math.PI, '^': -Math.PI / 2, 'v': Math.PI / 2 };

  /** Ratée : un chapitre qui a un point de reprise attend que l'hôpital ou le poste aient fini, puis demande. */
  function retenir(m) {
    const pm = B.partie.mission;
    if (!pm || !pm.reprise || !actes(m).length) return;
    B.repriseEnAttente = { slug: m.slug, reprise: pm.reprise, acte: acteA(m, pm.reprise.etape) + 1 };
  }

  /** Le menu, quand plus rien ne se passe : ni fondu, ni réplique, ni menu, ni lit d'urgence en train de se
      faire, ni menottes. Rend true s'il vient de s'ouvrir (`Histoire.maj` s'arrête là). */
  function majReprise() {
    const r = B.repriseEnAttente, j = B.joueur;
    if (!r || B.transition || B.cinema || B.menu || B.partie.mission || !j || j.hospitalise || j.arrete) return false;
    B.repriseEnAttente = null;
    const m = Histoire.mission(r.slug);
    if (!m) return false;
    Hud.ouvrirMenu({ titre: 'MISSION RATÉE', sur: m.titre.toUpperCase(), obligatoire: true, items: [
      { libelle: "REPRENDRE L'ACTE " + r.acte, faire: function () { reprendre(r); return true; } },
      // PLUS TARD : l'acte reste atteint (`chapitres[slug]`), et le téléphone rappellera — c'est le donneur de
      // CET acte qui attend (`donneurDe`), et l'appel se dit en rappel (`majTelephone`).
      { libelle: 'PLUS TARD', detail: 'ON TE RAPPELLERA',
        faire: function () { delete B.partie.appels[r.slug]; B.partie.appelT = null; return true; } },
    ] });
    return true;
  }

  /** Au point de l'acte : hors du lit et de la pièce, la police à zéro, l'arme de l'acte RENDUE (même si la
      prison l'avait prise), un char neuf du même modèle sur la rue d'à côté ; puis la mission repart au
      marqueur, qui refait son saut s'il en a un. */
  function reprendre(r) {
    const j = B.joueur, p = B.partie, x = r.reprise;
    Jeu.transiter(FONDU, function () {
      if (j.alite) Entites.seLever(j, 0, 0);
      if (j.dansVehicule) Vehicules.descendre(j, true);
      Jeu.revenirEnVille();
      Police.remiseAZero();
      const place = Histoire.tuileLibre(x.x, x.y, 6) || x;
      j.x = place.x; j.y = place.y; j.vx = 0; j.vy = 0;
      if (x.arme && x.arme !== 'poings') { p.armes[x.arme] = { mun: x.mun }; Combat.degainer(j, x.arme); }
      if (x.char) {
        const rue = Histoire.tuileDeRue(j.x, j.y, 8);
        if (rue) Vehicules.creer(x.char.slug, rue.x, rue.y, CAP[rue.sens], { etat: 'stationne', couleur: x.char.couleur || undefined });
      }
      Entites.indexer(); Monde.centrerCamera(j.x, j.y);
      chapitres()[r.slug] = x.etape;
      Histoire.commencer(r.slug, false);
      // La durée des actes d'avant, jouée avant l'échec, revient avec la reprise.
      const pm = B.partie.mission;
      if (pm) { pm.actes = (x.actes || []).slice(); if (pm.reprise) pm.reprise.actes = pm.actes.slice(); }
      // ⚠️ Et le point de reprise d'AVANT : `ouvrirActe` vient de le refaire à pied, à l'hôpital — mourir deux fois
      // dans le même acte ne fait pas perdre le char, ni la place.
      if (pm && pm.reprise) { pm.reprise.char = x.char; pm.reprise.x = x.x; pm.reprise.y = x.y; }
    }, 'ACTE ' + r.acte);
  }

  /** La mission réussie : le chapitre n'a plus d'acte en attente, et ses missions remplacées sont faites. */
  function reussi(m) {
    const p = B.partie;
    delete chapitres()[m.slug];
    (m.remplace || []).forEach(function (s) { if (!p.missionsFaites[s]) p.missionsFaites[s] = p.jour; });
  }

  return { actes, acteA, marqueurDe, donneurDe, ouvrirActe, reussi, depart, fait, dejaFait, marqueurSuivant, retenir, majReprise, reprendre, compter, noterDuree };
})();
