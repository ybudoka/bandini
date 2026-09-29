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

  /** Ou l'on est EN VILLE : dans un bloc, son passage ; dans une piece, sa porte ; sinon, soi.
      ⚠️ `Monde.zoneA` lit la carte COURANTE, et les pieces et les blocs n'ont pas de zones. */
  function ici() {
    const j = B.joueur;
    if (B.bloc) return { carte: B.bloc.ville.carte, x: B.bloc.ville.x, y: B.bloc.ville.y };
    if (B.interieur && B.exterieur) return { carte: B.exterieur.carte, x: B.exterieur.x, y: B.exterieur.y };
    return { carte: Monde.carte, x: j.x, y: j.y };
  }

  /** Le district d'un pixel sur une carte donnee (la derniere zone gagne, comme `Monde.zoneA`). */
  function districtA(carte, x, y) {
    let trouvee = null;
    for (const z of (carte && carte.zones) || []) {
      if (x >= z.x * TT && x < (z.x + z.l) * TT && y >= z.y * TT && y < (z.y + z.h) * TT) trouvee = z;
    }
    return trouvee ? trouvee.district : null;
  }

  function dedans(f) {
    if (f.indexOf('bloc:') === 0) return !!B.bloc && B.bloc.slug === f.slice(5);
    const l = ici();
    return districtA(l.carte, l.x, l.y) === f;
  }

  /** Le nom de la frontiere, en majuscules : « LES QUAIS », le nom du bloc. */
  function nom(f) {
    if (f.indexOf('bloc:') === 0) {
      const b = Blocs.liste().find(function (q) { return q.slug === f.slice(5); });
      return ((b && b.nom) || f.slice(5)).toUpperCase();
    }
    const carte = ici().carte, d = ((carte && carte.def && carte.def.districts) || []).find(function (q) { return q.slug === f; });
    return ((d && d.nom) || f).toUpperCase();
  }

  /** Chaque image de mission, meme dans une piece (`Histoire.maj`). Figee sous une scene, un menu, la
      pause : la boucle n'appelle pas `Histoire.maj`. Le compte vit dans `B.mission.hors`, en images. */
  function maj(m) {
    const pm = B.partie.mission;
    if (!m || !m.frontiere || !pm || !pm.gardee || !B.mission) return;
    if (dedans(m.frontiere)) { B.mission.hors = 0; return; }
    if (!B.mission.hors) Hud.message('RETOURNE DANS ' + nom(m.frontiere), 120);
    B.mission.hors = (B.mission.hors || 0) + 1;
    if (B.mission.hors > HORS_IMAGES) {
      const n = nom(m.frontiere);
      Histoire.echouer('hors_zone');
      Hud.message('MISSION RATÉE — TU AS QUITTÉ ' + n, 200);
    }
  }

  /** Ce que la ligne d'objectif porte dehors : « — REVIENS ! 7 S ». */
  function suffixe() {
    const bm = B.mission;
    return bm && bm.hors ? ' — REVIENS ! ' + Math.max(1, Math.ceil((HORS_IMAGES - bm.hors) / 60)) + ' S' : '';
  }

  // --- Le hors-zone GRISE, sur la mini-carte et la grande carte -------------------------------
  const GRIS = 'rgba(11,10,18,0.55)';

  /** Les districts (en tuiles) autres que la frontiere d'une mission gardee. Vide sans elle, pour
      une frontiere de bloc (le bloc est toute sa carte), et dans un bloc (sa carte n'a pas la ville). */
  function zonesHors(carte) {
    const m = Histoire.courante(), pm = B.partie && B.partie.mission;
    if (!m || !m.frontiere || !pm || !pm.gardee || m.frontiere.indexOf('bloc:') === 0 || B.bloc) return [];
    return ((carte && carte.zones) || []).filter(function (z) { return z.district === z.slug && z.slug !== m.frontiere; });
  }

  function dessinerSurLaCarte(ctx, pos) {
    ctx.fillStyle = GRIS;
    for (const z of zonesHors(Monde.carte)) {
      const a = pos(z.x * TT, z.y * TT), c = pos((z.x + z.l) * TT, (z.y + z.h) * TT);
      ctx.fillRect(a.x, a.y, c.x - a.x, c.y - a.y);
    }
  }

  /** La mini-carte est a une tuile par pixel, decalee de (sx, sy) ; on ne deborde pas de son cadre. */
  function dessinerMini(ctx, mini, sx, sy) {
    const zones = zonesHors(Monde.carte);
    if (!zones.length) return;
    ctx.save();
    ctx.beginPath(); ctx.rect(mini.x, mini.y, mini.l, mini.h); ctx.clip();
    ctx.fillStyle = GRIS;
    for (const z of zones) ctx.fillRect(mini.x + z.x - sx, mini.y + z.y - sy, z.l, z.h);
    ctx.restore();
  }

  return { HORS_IMAGES, heureCible, avancerA, sauter, ici, dedans, nom, maj, suffixe,
           zonesHors, dessinerSurLaCarte, dessinerMini };
})();
