/* Des missions SUR PLACE, gardees par une FRONTIERE (29 sept. 2026).

   Demande de Martin : « pour certaines missions, des raccourcis vers le moment de la journee et
   l'endroit, avec une frontiere qui nous garde dans la mission ». Deux cles de mission, chacune
   facultative, lues ici et nulle part ailleurs :

   - `sur_place` : a la fin de l'intro, fondu au noir, l'horloge AVANCE jusqu'a l'heure voulue et
     l'on se releve au lieu (un lieu de bloc fait entrer dans le bloc) ;
   - `frontiere` : un district ou `bloc:<slug>`. Dehors, dix secondes pour revenir ; a zero, la
     mission rate (`hors_zone`). */
const SurPlace = (function () {
  const HORS_IMAGES = 600;              // 10 s
  const FONDU = [32, 56, 32];           // celui de la sieste (`FONDU_NUIT`)

  /** L'heure ou se relever pour `voulue` (« nuit » ou [h0, h1]), ou null si on y est deja.
      « nuit » : le reveil de la sieste (20 h 45). ⚠️ Jamais en arriere, c'est `avancerA` qui le
      garantit : une cible deja passee aujourd'hui est celle de demain. */
  function heureCible(voulue, heure) {
    if (voulue === 'nuit') return Monde.estNuit(heure) ? null : B.defs.economie.sieste.reveil;
    const h0 = voulue[0], h1 = voulue[1];
    const dans = h0 <= h1 ? heure >= h0 && heure <= h1 : heure >= h0 || heure <= h1;
    return dans ? null : h0;
  }

  /** Avance l'horloge jusqu'a `h` — minuit passe, c'est un vrai jour (le patron de la prison). */
  function avancerA(h) {
    const p = B.partie;
    let delta = h - p.heure;
    if (delta < 0) delta += 1;
    p.heure += delta;
    while (p.heure >= 1) { p.heure -= 1; p.jour += 1; Missions.nouveauJour(); }
    if (Math.abs(p.heure - h) < 1e-9) p.heure = h;
  }

  /** La frontiere s'arme. ⚠️ Dans `B.partie.mission` (sauvegardee), pas dans `B.mission` (refaite
      vide au rechargement) : une partie reprise en pleine mission reste gardee. */
  function garder() { if (B.partie.mission) B.partie.mission.gardee = true; }

  /** Pose le joueur a pied pres du lieu (la carte courante : la ville, ou le bloc). */
  function poser(slug) {
    const j = B.joueur, l = Histoire.lieu(slug);
    if (!l) return;
    const place = Histoire.tuileLibre(l.x, l.y, 4) || l;
    j.x = place.x; j.y = place.y; j.vx = 0; j.vy = 0;
    Entites.indexer();
    Monde.centrerCamera(j.x, j.y);
  }

  /** A la fin de l'intro : le saut s'il y en a un, puis `fin()` — toujours, une fois. */
  function sauter(m, fin) {
    const sp = m && m.sur_place;
    if (!sp) { garder(); fin(); return; }
    const bloc = Histoire.blocDuLieu(sp.lieu);
    const cible = heureCible(sp.heure, B.partie.heure);
    if (bloc) Blocs.charger(bloc);
    Jeu.transiter(FONDU, function () {
      const j = B.joueur;
      if (cible !== null) avancerA(cible);
      Police.remiseAZero();
      if (j.dansVehicule) Vehicules.descendre(j, true);
      if (!(bloc && B.bloc && B.bloc.slug === bloc)) Jeu.revenirEnVille();
      if (bloc) Blocs.entrerAuNoir(bloc, null);
      poser(sp.lieu);
      garder();
      fin();
    }, cible === null ? null : (sp.heure === 'nuit' ? 'LE SOIR VENU' : 'PLUS TARD'),
    bloc ? function () { return !Blocs.cartes[bloc]; } : null);
  }

  return { HORS_IMAGES, heureCible, avancerA, sauter };
})();
