"""Conduire un char au banc, au bouton, sur un chemin trouvé dans la carte — pour l'île (la navette, le chemin de
gravelle) : le chemin d'un joueur, pas un char téléporté. Une seule copie, partagée par les juges de l'île en char."""

PILOTE = """
  // Les tuiles où un char roule sans couler ni buter : ni mur, ni eau, ni décor (un arbre, un baril, un poteau).
  function roulable(L, tx, ty) {
    const M = L.Monde;
    if (M.bloque(tx, ty, M.MASQUE_VEHICULE) || M.estEau(tx, ty)) return false;
    return !L.Entites.decorAutour(tx * 16 + 8, ty * 16 + 8, 4).some(function (d) { return !d.brise && !d.flotte; });
  }
  // Un chemin de tuiles (largeur en largeur), qui préfère le large : une tuile collée à l'eau ou au décor coûte plus.
  function cheminDuChar(L, de, vers) {
    const w = L.Monde.carte.w, h = L.Monde.carte.h, cle = function (x, y) { return y * w + x; };
    const depart = { x: Math.floor(de.x / 16), y: Math.floor(de.y / 16) }, but = { x: Math.floor(vers.x / 16), y: Math.floor(vers.y / 16) };
    const cout = new Map(), avant = new Map(), file = [[0, depart.x, depart.y]];
    cout.set(cle(depart.x, depart.y), 0);
    // L'eau à côté coûte plus qu'un mur : on mord le bord d'un mur, on coule dans l'eau.
    const serre = function (x, y) { let n = 0; for (let dy = -1; dy <= 1; dy++) for (let dx = -1; dx <= 1; dx++) if (!roulable(L, x + dx, y + dy)) n += L.Monde.estEau(x + dx, y + dy) ? 3 : 1; return n; };
    let n = 0;
    while (file.length && n++ < 200000) {
      file.sort(function (a, b) { return a[0] - b[0]; });
      const [c, x, y] = file.shift();
      if (x === but.x && y === but.y) break;
      if (c > cout.get(cle(x, y))) continue;
      for (const [dx, dy] of [[1, 0], [-1, 0], [0, 1], [0, -1]]) {
        const nx = x + dx, ny = y + dy;
        if (nx < 0 || ny < 0 || nx >= w || ny >= h || !roulable(L, nx, ny)) continue;
        const nc = c + 1 + 4 * serre(nx, ny);
        if (!cout.has(cle(nx, ny)) || nc < cout.get(cle(nx, ny))) { cout.set(cle(nx, ny), nc); avant.set(cle(nx, ny), [x, y]); file.push([nc, nx, ny]); }
      }
    }
    if (!avant.has(cle(but.x, but.y))) return null;
    const out = [];
    for (let p = [but.x, but.y]; p && !(p[0] === depart.x && p[1] === depart.y); p = avant.get(cle(p[0], p[1]))) out.unshift({ x: p[0] * 16 + 8, y: p[1] * 16 + 8 });
    return out;
  }
  // Au bouton : W tenu, A/D selon l'écart d'angle avec un point trois tuiles plus loin sur le chemin, S pour freiner
  // dans un virage serré. Rend { images, arrive, eau (le plus long bain, en images), degats }.
  function piloter(L, o, v, chemin, maxImages) {
    const vie = v.vie;
    let i = 0, k = 0, eau = 0, cale = 0, recule = 0;
    const fin = chemin[chemin.length - 1];
    const lacher = function () { ['KeyW', 'KeyA', 'KeyD', 'KeyS'].forEach(function (t) { o.relacher(t); }); };
    for (; i < (maxImages || 3000); i++) {
      while (k < chemin.length - 1 && Math.hypot(chemin[k].x - v.x, chemin[k].y - v.y) < 20) k++;
      const cible = chemin[Math.min(chemin.length - 1, k + 1)];
      let ecart = Math.atan2(cible.y - v.y, cible.x - v.x) - v.angle;
      ecart = Math.atan2(Math.sin(ecart), Math.cos(ecart));
      const vite = Math.hypot(v.vx || 0, v.vy || 0);
      lacher();
      // Calé contre un coin : on recule en braquant de l'autre bord, puis on repart.
      if (recule > 0) { recule--; o.touche('KeyS'); o.touche(ecart > 0 ? 'KeyA' : 'KeyD'); }
      else {
        cale = vite < 0.15 ? cale + 1 : 0;
        if (cale > 40) { recule = 35; cale = 0; }
        if (Math.abs(ecart) > 0.05) o.touche(ecart > 0 ? 'KeyD' : 'KeyA');
        // Au pas dans les virages, et en arrivant (un quai, un pont de deux rangées : on y entre comme un joueur prudent).
        const proche = chemin.length - k < 6;
        const voulu = proche ? 0.5 : Math.abs(ecart) > 0.8 ? 0.5 : Math.abs(ecart) > 0.35 ? 0.8 : 1.6;
        if (vite > voulu + 0.3) o.touche('KeyS'); else if (vite < voulu) o.touche('KeyW');
      }
      o.frame(1);
      // Dans l'eau pour vrai : il COULE (`majNoyade` compte `coule`, trois secondes et il est au fond) — le pont posé
      // de la navette n'est pas de l'eau. On garde le plus long bain : un coin de roue qui mord le bord du quai en
      // tournant n'est pas un char perdu.
      eau = Math.max(eau, v.coule || 0);
      if (Math.hypot(fin.x - v.x, fin.y - v.y) < 18) break;
    }
    const arrive = Math.round(Math.hypot(fin.x - v.x, fin.y - v.y));
    lacher();
    // On freine jusqu'à l'arrêt — pas plus : sous 0,15, le frein est la marche arrière.
    for (let n = 0; n < 60 && Math.hypot(v.vx || 0, v.vy || 0) > 0.2; n++) { o.touche('KeyS'); o.frame(1); }
    o.relacher('KeyS'); o.frame(5);
    return { images: i, arrive: arrive, eau: eau, degats: Math.round(vie - v.vie) };
  }
"""
