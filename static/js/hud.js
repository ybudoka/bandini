/* Bandini — HUD (canvas, hors nuit) et voiles DOM (titre, scores). */

const Hud = (function () {
  'use strict';

  let doc = null, racine = null, voiles = {}, urlScores = '';

  function init(d, r) {
    doc = d; racine = r;
    urlScores = r.dataset.urlScores;
    ['titre', 'scores', 'score-envoi'].forEach(function (n) { voiles[n] = d.getElementById('voile-' + n); });
    d.getElementById('bouton-jouer').addEventListener('click', function () { Son.reveiller(); Jeu.commencer(); });
    d.getElementById('bouton-scores').addEventListener('click', function () { Son.reveiller(); montrerScores(); });
    d.getElementById('bouton-fermer-scores').addEventListener('click', function () { voile('titre'); });
    d.getElementById('bouton-annuler-score').addEventListener('click', function () { voile(null); Jeu.reprendre(); });
    d.getElementById('score-form').addEventListener('submit', envoyerScore);
  }

  function voile(nom) {
    for (const n in voiles) voiles[n].hidden = (n !== nom);
  }

  function etat(nom) { if (racine) racine.dataset.etat = nom; }

  function message(texte, duree) { B.msg = texte; B.msgT = duree || 120; }

  // --- Scores ---------------------------------------------------------------------

  function afficherScores(scores) {
    const liste = doc.getElementById('liste-scores');
    liste.innerHTML = '';
    if (!scores || !scores.length) {
      const li = doc.createElement('li');
      li.className = 'scores__vide';
      li.textContent = 'Personne encore. Baie-des-Brumes t’attend.';
      liste.appendChild(li);
      return;
    }
    scores.forEach(function (s) {
      const li = doc.createElement('li');
      const nom = doc.createElement('span'); nom.textContent = s.pseudo;
      const detail = doc.createElement('span');
      detail.textContent = s.fortune.toLocaleString('fr-CA') + ' $ · ' + s.missions + ' missions';
      li.appendChild(nom); li.appendChild(detail);
      liste.appendChild(li);
    });
  }

  function montrerScores() {
    voile('scores');
    fetch(urlScores, { cache: 'no-store' })
      .then(function (r) { return r.json(); })
      .then(function (d) { afficherScores(d.scores); })
      .catch(function () { afficherScores([]); });
  }

  function envoyerScore(ev) {
    ev.preventDefault();
    const champ = doc.getElementById('pseudo'), etatEl = doc.getElementById('score-etat');
    const pseudo = champ.value.trim();
    if (!pseudo) { etatEl.textContent = 'Écris un pseudo.'; return; }
    etatEl.textContent = 'Envoi…';
    const p = B.partie;
    const fortune = p.argent + Object.keys(p.proprietes).reduce(function (s, slug) {
      const prop = B.defs.economie.proprietes.find(function (q) { return q.slug === slug; });
      return s + (prop ? prop.prix : 0);
    }, 0);
    fetch(urlScores, {
      method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ pseudo: pseudo, fortune: fortune, missions: Object.keys(p.missionsFaites).length,
                             proprietes: Object.keys(p.proprietes).length, duree_s: Math.max(1, p.stats.secondes) }),
    })
      .then(function (r) { return r.json().then(function (d) { return { ok: r.ok, d: d }; }); })
      .then(function (res) {
        if (!res.ok) { etatEl.textContent = res.d.erreur || 'Refusé.'; return; }
        p.pseudo = pseudo;
        etatEl.textContent = res.d.rang && res.d.rang <= 10 ? 'Bravo, ' + res.d.rang + 'e au tableau!' : 'Score envoyé.';
        afficherScores(res.d.scores);
        setTimeout(function () { voile('scores'); }, 900);
      })
      .catch(function () { etatEl.textContent = 'Pas de réseau — réessaie plus tard.'; });
  }

  function demanderScore() {
    voile('score-envoi');
    doc.getElementById('pseudo').value = B.partie.pseudo || '';
    doc.getElementById('score-etat').textContent = '';
  }

  // --- Dessin --------------------------------------------------------------------------

  function barre(ctx, x, y, l, h, frac, couleur) {
    ctx.fillStyle = '#101018'; ctx.fillRect(x - 1, y - 1, l + 2, h + 2);
    ctx.fillStyle = '#2a2a3a'; ctx.fillRect(x, y, l, h);
    ctx.fillStyle = couleur; ctx.fillRect(x, y, Math.round(l * borner(frac, 0, 1)), h);
    B.stats.rects += 3;
  }

  function dessiner() {
    const ctx = Base.ecran();
    const j = B.joueur, p = B.partie;
    if (!p) return;
    if (B.etat === 'jeu' || B.etat === 'pause') {
      // Vie et endurance, en haut a gauche.
      barre(ctx, 6, 6, 60, 5, j ? j.vie / j.vieMax : 1, '#c4362f');
      barre(ctx, 6, 13, 60, 3, j ? j.endurance / 100 : 1, '#e8b33c');
      // Argent, etoiles, heure a droite.
      const argent = p.argent.toLocaleString('fr-CA') + ' $';
      Atlas.texte(ctx, argent, VW - 6 - Atlas.largeurTexte(argent, 2), 6, '#e8b33c', 2);
      let etoiles = '';
      for (let i = 0; i < B.defs.recherche.etoiles_max; i++) etoiles += i < B.recherche.etoiles ? '★' : '.';
      Atlas.texte(ctx, etoiles, VW - 6 - Atlas.largeurTexte(etoiles, 1), 20, B.recherche.etoiles ? '#ffffff' : '#555560', 1);
      const heure = 'JOUR ' + p.jour + ' ' + Monde.heureTexte();
      Atlas.texte(ctx, heure, VW - 6 - Atlas.largeurTexte(heure, 1), 28, '#cdc6e6', 1);
      // Arme en bas a droite.
      const arme = Combat.armeCourante();
      if (arme) {
        const mun = p.armes[arme.slug] && p.armes[arme.slug].mun;
        const libelle = arme.nom.toUpperCase() + (mun === null || mun === undefined ? '' : ' ' + mun);
        Atlas.texte(ctx, libelle, VW - 6 - Atlas.largeurTexte(libelle, 1), VH - 12, '#efe6d0', 1);
      }
      // Message.
      if (B.msg && B.msgT > 0) {
        const l = Atlas.largeurTexte(B.msg, 2);
        ctx.fillStyle = 'rgba(11,10,18,0.75)'; ctx.fillRect((VW - l) / 2 - 6, 40, l + 12, 16);
        Atlas.texte(ctx, B.msg, (VW - l) / 2, 43, '#efe6d0', 2);
        B.msgT--;
      }
      if (B.etat === 'pause') {
        ctx.fillStyle = 'rgba(11,10,18,0.6)'; ctx.fillRect(0, 0, VW, VH);
        Atlas.texte(ctx, 'PAUSE', (VW - Atlas.largeurTexte('PAUSE', 4)) / 2, VH / 2 - 14, '#e8b33c', 4);
        const aide = 'ECHAP OU PAUSE : REPRENDRE';
        Atlas.texte(ctx, aide, (VW - Atlas.largeurTexte(aide, 1)) / 2, VH / 2 + 12, '#cdc6e6', 1);
      }
    }
    if (B.options.perf) {
      const s = B.stats;
      Atlas.texte(ctx, Math.round(s.ms * 10) / 10 + 'MS ' + s.images + 'I ' + s.entites + 'E', 6, VH - 8, '#8f8', 1);
    }
  }

  return { init, voile, etat, message, dessiner, montrerScores, demanderScore, afficherScores };
})();
