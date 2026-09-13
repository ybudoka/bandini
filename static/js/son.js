/* Bandini — son : Web Audio, tout synthetise, aucun fichier. */

const Son = (function () {
  'use strict';

  let ctx = null, maitre = null, fenetre = null;

  function init(w) { fenetre = w; }

  function reveiller() {
    if (!fenetre) return;
    if (!ctx) {
      const AC = fenetre.AudioContext || fenetre.webkitAudioContext;
      if (!AC) return;
      try { ctx = new AC(); } catch (e) { return; }
      maitre = ctx.createGain();
      maitre.gain.value = 0.18;
      maitre.connect(ctx.destination);
    }
    if (ctx.state === 'suspended') ctx.resume().catch(function () {});
  }

  function pret() { return !!ctx && !B.options.muet; }

  function suspendre() { if (ctx && ctx.state === 'running') ctx.suspend().catch(function () {}); }

  /** Une note : frequence en Hz, duree en s, forme, volume, glisse (facteur de frequence finale). */
  function ton(freq, duree, forme, volume, glisse, depart) {
    if (!pret()) return;
    const t0 = ctx.currentTime + (depart || 0);
    const osc = ctx.createOscillator();
    const gain = ctx.createGain();
    osc.type = forme || 'square';
    osc.frequency.setValueAtTime(freq, t0);
    if (glisse) osc.frequency.exponentialRampToValueAtTime(Math.max(20, freq * glisse), t0 + duree);
    gain.gain.setValueAtTime(0.0001, t0);
    gain.gain.exponentialRampToValueAtTime(volume || 0.4, t0 + 0.01);
    gain.gain.exponentialRampToValueAtTime(0.0001, t0 + duree);
    osc.connect(gain).connect(maitre);
    osc.start(t0);
    osc.stop(t0 + duree + 0.02);
  }

  /** Un souffle de bruit blanc filtre. */
  function bruit(duree, volume, freqDebut, freqFin) {
    if (!pret()) return;
    const t0 = ctx.currentTime;
    const n = Math.floor(ctx.sampleRate * duree);
    const tampon = ctx.createBuffer(1, n, ctx.sampleRate);
    const d = tampon.getChannelData(0);
    for (let i = 0; i < n; i++) d[i] = (Math.random() * 2 - 1) * (1 - i / n);
    const src = ctx.createBufferSource();
    src.buffer = tampon;
    const filtre = ctx.createBiquadFilter();
    filtre.type = 'lowpass';
    filtre.frequency.setValueAtTime(freqDebut || 1200, t0);
    filtre.frequency.exponentialRampToValueAtTime(freqFin || 200, t0 + duree);
    const gain = ctx.createGain();
    gain.gain.setValueAtTime(volume || 0.5, t0);
    src.connect(filtre).connect(gain).connect(maitre);
    src.start(t0);
  }

  const SFX = {
    pas: function () { bruit(0.05, 0.12, 900, 300); },
    coup: function () { ton(140, 0.08, 'square', 0.3, 0.5); bruit(0.08, 0.3, 800, 200); },
    touche: function () { ton(220, 0.12, 'sawtooth', 0.25, 0.4); },
    ramasse: function () { ton(880, 0.08, 'sine', 0.25); ton(1320, 0.12, 'sine', 0.2, 1, 0.07); },
    argent: function () { ton(1500, 0.06, 'sine', 0.2); ton(2000, 0.1, 'sine', 0.18, 1, 0.06); },
    menu: function () { ton(660, 0.05, 'square', 0.15); },
    erreur: function () { ton(160, 0.2, 'sawtooth', 0.2, 0.7); },
    etoile: function () { ton(523, 0.15, 'square', 0.2); ton(784, 0.2, 'square', 0.2, 1, 0.12); },
    sirene: function () { ton(700, 0.4, 'square', 0.15, 1.4); },
    klaxon: function () { ton(330, 0.25, 'sawtooth', 0.3); ton(415, 0.25, 'sawtooth', 0.3); },
    choc: function () { bruit(0.4, 0.5, 1200, 100); },
    explosion: function () { bruit(0.9, 0.8, 600, 40); ton(60, 0.6, 'sine', 0.5, 0.5); },
    porte: function () { ton(300, 0.1, 'triangle', 0.2, 0.7); },
  };

  /* Musique : sequenceur 3 voix a venir (M7). `tick()` avance meme sans audio,
     pour rester deterministe sous le banc. */
  const Mus = { courante: null, pas: 0, jouer: function (nom) { this.courante = nom; this.pas = 0; },
                stop: function () { this.courante = null; }, tick: function () { if (this.courante) this.pas++; } };

  return { init, reveiller, pret, suspendre, ton, bruit, SFX, Mus, get contexte() { return ctx; } };
})();
