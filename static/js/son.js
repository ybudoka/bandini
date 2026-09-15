/* Bandini — son : des echantillons reels quand ils existent, la synthese sinon.

   ⚠️ La synthese n'est pas un vestige : c'est le FILET. Un fichier absent, un
   decodage refuse, un reseau coupe — le jeu doit sonner quand meme. Chaque
   effet essaie donc son echantillon, et retombe sur ses oscillateurs. */

const Son = (function () {
  'use strict';

  const VOLUME_MAITRE = 0.18;
  let ctx = null, maitre = null, fenetre = null, base = '', surChangement = null;
  const tampons = new Map();      // slug -> [AudioBuffer]
  const boucles = new Map();      // slug -> source qui tourne
  let demandes = false;

  function init(w, urlStatique) { fenetre = w; base = urlStatique || '/static/'; }

  /** Qui prevenir quand le son passe de « retenu » a « actif » (ou l'inverse). */
  function surEtat(f) { surChangement = f; }

  /** Cree le contexte s'il manque et tente de le demarrer. Rend son etat.

      ⚠️ Un AudioContext naît « suspended » tant que la page n'a pas reçu un
      VRAI geste (clic, touche, toucher), et `resume()` est alors refuse. Or
      l'API Manette ne compte PAS comme un geste : on peut commencer la partie
      au pad sans que le navigateur accorde jamais le son. Le jeu doit donc
      pouvoir DIRE qu'il attend un geste, au lieu de se taire sans rien dire. */
  function sonder() {
    if (!fenetre) return 'absent';
    if (!ctx) {
      const AC = fenetre.AudioContext || fenetre.webkitAudioContext;
      if (!AC) return 'absent';
      try { ctx = new AC(); } catch (e) { return 'absent'; }
      maitre = ctx.createGain();
      maitre.gain.value = B.options.muet ? 0 : VOLUME_MAITRE;
      maitre.connect(ctx.destination);
      // ⚠️ `resume()` est asynchrone : au retour du geste l'etat est encore
      // « suspended ». Sans cet ecouteur, le bandeau « touche l'ecran » resterait
      // affiche alors que le son est revenu.
      ctx.onstatechange = function () { if (surChangement) surChangement(etatSon()); };
    }
    if (ctx.state === 'suspended') ctx.resume().catch(function () {});
    return etatSon();
  }

  /** 'actif' | 'attente' (il manque un geste) | 'coupe' (OPTIONS) | 'absent'. */
  function etatSon() {
    if (!ctx) return 'absent';
    if (ctx.state !== 'running') return 'attente';
    return B.options.muet ? 'coupe' : 'actif';
  }

  /** Le son est branche, mais le navigateur attend un geste de la main. */
  function enAttente() { return etatSon() === 'attente'; }

  function reveiller() {
    if (sonder() === 'absent') return;
    chargerEchantillons();
    Voix.charger();
  }

  /** Le son coupe doit couper AUSSI ce qui tourne deja (sirene, moteur). */
  function majVolume() {
    if (maitre) maitre.gain.value = B.options.muet ? 0 : VOLUME_MAITRE;
  }

  function pret() { return !!ctx && !B.options.muet; }

  function suspendre() { if (ctx && ctx.state === 'running') ctx.suspend().catch(function () {}); }

  /** Rend la carte son quand la page s'en va. ⚠️ Un AudioContext n'est pas
      gratuit : le navigateur en limite le nombre, et depuis qu'on en ouvre un
      des le chargement (pour savoir si le son est accorde), une page qui part
      sans fermer le sien en laisse un derriere elle. */
  function fermer() {
    if (!ctx) return;
    const parti = ctx;
    ctx = null; maitre = null; bruitTampon = null;
    demandes = false;
    tampons.clear(); boucles.clear();
    Voix.chargees = false; Voix.enCours = null; Voix.missionsChargees.clear();
    Ambiance.courante = null; Ambiance.chargee = null;
    Radio.courante = null; Radio.chargees.clear();
    Mus.arreter();
    try { parti.close(); } catch (e) { /* deja fermee */ }
  }

  /** Une note : frequence en Hz, duree en s, forme, volume, glisse (facteur de frequence finale). */
  function ton(freq, duree, forme, volume, glisse, depart) {
    if (!pret()) return;
    tonA(ctx.currentTime + (depart || 0), freq, duree, forme, volume, glisse);
  }

  /** La meme note, mais POSEE a un instant de l'horloge audio. C'est ce qu'il
      faut a un sequenceur : on programme la mesure suivante pendant que la
      mesure courante joue, et le rythme ne depend plus du rythme des images. */
  function tonA(t0, freq, duree, forme, volume, glisse) {
    if (!pret()) return;
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

  //: Un seul tampon de bruit blanc, refait a l'identique : le balai de la
  //: musique frappe cinq fois par seconde, et fabriquer un tampon neuf a chaque
  //: coup reviendrait a remplir un tableau de 5 000 nombres pour un « tss ».
  let bruitTampon = null;
  function tamponDeBruit() {
    if (!bruitTampon) {
      const n = Math.floor(ctx.sampleRate * 0.5);
      bruitTampon = ctx.createBuffer(1, n, ctx.sampleRate);
      const d = bruitTampon.getChannelData(0);
      for (let i = 0; i < n; i++) d[i] = Math.random() * 2 - 1;
    }
    return bruitTampon;
  }

  /** Un « tss » pose a un instant : bruit filtre, enveloppe courte. */
  function bruitA(t0, duree, volume, coupure) {
    if (!pret()) return;
    const src = ctx.createBufferSource();
    src.buffer = tamponDeBruit();
    const filtre = ctx.createBiquadFilter();
    filtre.type = 'highpass';
    filtre.frequency.setValueAtTime(coupure || 6000, t0);
    const gain = ctx.createGain();
    gain.gain.setValueAtTime(0.0001, t0);
    gain.gain.exponentialRampToValueAtTime(Math.max(0.0002, volume), t0 + 0.004);
    gain.gain.exponentialRampToValueAtTime(0.0001, t0 + duree);
    src.connect(filtre).connect(gain).connect(maitre);
    src.start(t0);
    src.stop(t0 + duree + 0.02);
  }

  // --- Echantillons (fichiers generes par ElevenLabs, catalogue en Python) ----

  function defEchantillon(slug) {
    const audio = B.defs && B.defs.audio;
    if (!audio) return null;
    for (const e of audio.echantillons) if (e.slug === slug) return e;
    return null;
  }

  /** Telecharge et decode une fois, apres le premier geste (il faut un ctx).
      ⚠️ Un echec ne remonte nulle part : l'effet retombera sur la synthese. */
  function chargerEchantillons() {
    const audio = B.defs && B.defs.audio;
    if (demandes || !ctx || !audio || !fenetre || !fenetre.fetch) return;
    demandes = true;
    const dossier = base + audio.dossier + '/';
    audio.echantillons.forEach(function (e) {
      (e.fichiers || []).forEach(function (nom) {
        fenetre.fetch(dossier + nom)
          .then(function (r) { return r.ok ? r.arrayBuffer() : Promise.reject(r.status); })
          .then(function (octets) {
            return new Promise(function (ok, ko) { ctx.decodeAudioData(octets, ok, ko); });
          })
          .then(function (tampon) {
            const liste = tampons.get(e.slug) || [];
            liste.push(tampon);
            tampons.set(e.slug, liste);
          })
          .catch(function () { /* la synthese prend le relais */ });
      });
    });
  }

  /** Joue l'echantillon `slug` s'il est charge. Rend { source, gain }, ou null.
      `options.pan` (-1..1) place le son a gauche ou a droite. */
  function echantillon(slug, options) {
    if (!pret()) return null;
    const liste = tampons.get(slug);
    if (!liste || !liste.length) return null;
    const def = defEchantillon(slug);
    const source = ctx.createBufferSource();
    // Plusieurs variantes : on en tire une au hasard, sinon dix coups de poing
    // d'affilee sonnent comme un bug.
    source.buffer = liste.length === 1 ? liste[0] : liste[Math.floor(Math.random() * liste.length)];
    source.loop = !!(options && options.boucle);
    const gain = ctx.createGain();
    gain.gain.value = (def ? def.volume : 1) * ((options && options.volume) || 1);
    let sortie = gain;
    if (options && options.pan && ctx.createStereoPanner) {
      const pan = ctx.createStereoPanner();
      pan.pan.value = Math.max(-1, Math.min(1, options.pan));
      gain.connect(pan); sortie = pan;
    }
    // ⚠️ La source DANS le gain : sans cette ligne, tout le reste est correct —
    // le fichier se telecharge, se decode, la source demarre, le gain est au bon
    // volume et il est branche sur la sortie — mais rien n'entre dans la chaîne
    // et il ne sort RIEN. C'est ainsi qu'aucun des 79 fichiers n'a jamais ete
    // entendu jusqu'au 13 sept. 2026, sans qu'une seule erreur soit levee.
    source.connect(gain);
    sortie.connect(maitre);
    source.start(ctx.currentTime);
    return { source: source, gain: gain, base: def ? def.volume : 1 };
  }

  /** Un son POSE dans le monde : plus loin, plus faible ; a droite, a droite.
      Rend le volume calcule (0 = trop loin, rien n'a joue). */
  function jouerA(slug, x, y, portee) {
    const j = B.joueur;
    if (!j) return 0;
    const d = Math.hypot(x - j.x, y - j.y);
    const p = portee || 320;
    if (d >= p) return 0;
    const volume = 1 - d / p;
    echantillon(slug, { volume: volume, pan: (x - j.x) / p });
    return volume;
  }

  function joue(slug) { return echantillon(slug) !== null; }

  /** Ce son est-il pret a jouer ? ⚠️ Repondre en le JOUANT (comme le faisaient
      les tests) demarre une source a chaque appel : dans une boucle d'attente,
      ca finit par des centaines de sources en vol et le contexte cale. */
  function estCharge(slug) {
    const liste = tampons.get(slug);
    return !!liste && liste.length > 0;
  }

  /** Une boucle qu'on allume et qu'on eteint (sirene, moteur). */
  function boucle(slug, actif, volume) {
    const courante = boucles.get(slug);
    if (actif && !courante) {
      const jouee = echantillon(slug, { boucle: true, volume: volume });
      if (jouee) boucles.set(slug, jouee);
    } else if (!actif && courante) {
      try { courante.source.stop(); } catch (e) { /* deja finie */ }
      boucles.delete(slug);
    }
  }

  /** Regle une boucle en marche : volume (0..1) et hauteur (1 = normale).
      C'est ce qui fait monter le moteur dans les tours. */
  function reglerBoucle(slug, volume, hauteur) {
    const courante = boucles.get(slug);
    if (!courante) return;
    if (volume !== undefined) courante.gain.gain.value = courante.base * volume;
    if (hauteur !== undefined && courante.source.playbackRate) courante.source.playbackRate.value = hauteur;
  }

  function boucleActive(slug) { return boucles.has(slug); }

  const SFX = {
    pas: function () { if (!joue('pas')) bruit(0.05, 0.12, 900, 300); },
    coup: function () { if (!joue('coup')) { ton(140, 0.08, 'square', 0.3, 0.5); bruit(0.08, 0.3, 800, 200); } },
    touche: function () { if (!joue('touche')) ton(220, 0.12, 'sawtooth', 0.25, 0.4); },
    ramasse: function () { if (!joue('ramasse')) { ton(880, 0.08, 'sine', 0.25); ton(1320, 0.12, 'sine', 0.2, 1, 0.07); } },
    argent: function () { if (!joue('argent')) { ton(1500, 0.06, 'sine', 0.2); ton(2000, 0.1, 'sine', 0.18, 1, 0.06); } },
    menu: function () { if (!joue('menu')) ton(660, 0.05, 'square', 0.15); },
    erreur: function () { if (!joue('erreur')) ton(160, 0.2, 'sawtooth', 0.2, 0.7); },
    etoile: function () { if (!joue('etoile')) { ton(523, 0.15, 'square', 0.2); ton(784, 0.2, 'square', 0.2, 1, 0.12); } },
    sirene: function () { if (!joue('sirene')) ton(700, 0.4, 'square', 0.15, 1.4); },
    klaxon: function () { if (!joue('klaxon')) { ton(330, 0.25, 'sawtooth', 0.3); ton(415, 0.25, 'sawtooth', 0.3); } },
    choc: function () { if (!joue('choc')) bruit(0.4, 0.5, 1200, 100); },
    explosion: function () { if (!joue('explosion')) { bruit(0.9, 0.8, 600, 40); ton(60, 0.6, 'sine', 0.5, 0.5); } },
    // ⚠️ Trois portes : le bois et la serrure d'un logement, la vitre et la
    // porte d'un commerce, la portiere d'un char. Le jeu appelle
    // `porte(genre)` ; le genre vient de la fiche — de la piece (`carte._piece`,
    // champ `porte`) ou du char (`vehicules.py`, `portieres`).
    porte_maison: function () { if (!joue('porte_maison')) { ton(160, 0.14, 'triangle', 0.22, 0.6); bruit(0.06, 0.12, 400, 150); } },
    porte_commerce: function () { if (!joue('porte_commerce')) { bruit(0.03, 0.08, 3000, 2000); ton(2300, 0.18, 'sine', 0.12, 1, 0.03); ton(3100, 0.25, 'sine', 0.09, 1, 0.1); } },
    porte_vehicule: function () { if (!joue('porte_vehicule')) { bruit(0.05, 0.3, 1500, 200); ton(95, 0.09, 'square', 0.14, 0.5, 0.01); } },
    porte: function (genre) { (SFX['porte_' + genre] || SFX.porte_maison)(); },
    // ⚠️ La sonnette est l'AVERTISSEUR du velo (`vehicules.py`, `klaxon`) : au
    // meme bouton que le klaxon d'une auto. Les velos du trafic la font deja
    // entendre en passant (`jouerA`) ; ici c'est la sienne.
    sonnette: function () { if (!joue('sonnette')) { ton(2600, 0.1, 'sine', 0.16); ton(2600, 0.14, 'sine', 0.12, 1, 0.13); } },
    // Un deux-roues s'enfourche : la bequille et le cadre, pas une portiere.
    enfourcher: function () { if (!joue('enfourcher')) { bruit(0.05, 0.15, 1800, 300); ton(700, 0.05, 'square', 0.08, 0.6, 0.03); } },
    telephone: function () { if (!joue('telephone')) for (let i = 0; i < 3; i++) { ton(1200, 0.08, 'square', 0.15, 1, i * 0.12); ton(1600, 0.08, 'square', 0.15, 1, i * 0.12 + 0.05); } },
    helico: function () { if (!joue('helico')) bruit(0.3, 0.2, 200, 80); },
    // --- Les armes : un son par arme (`armes.py`, champ `son`) ----------------
    // ⚠️ `arme(def)` est le seul point d'entree du combat : il lit `def.son` et
    // retombe sur le coup de poing quand l'arme n'en declare pas. Le geste et
    // l'impact sont dans le meme son, comme pour `coup` : il part au debut de
    // la phase active, avant de savoir si le coup touche.
    batte: function () { if (!joue('batte')) { bruit(0.07, 0.25, 700, 150); ton(120, 0.1, 'square', 0.3, 0.5, 0.03); } },
    couteau: function () { if (!joue('couteau')) { bruit(0.09, 0.2, 6000, 1500); ton(2400, 0.05, 'sine', 0.08, 1.3, 0.02); } },
    pelle: function () { if (!joue('pelle')) { bruit(0.08, 0.2, 800, 200); ton(1900, 0.3, 'triangle', 0.22, 0.9, 0.04); ton(2600, 0.2, 'sine', 0.12, 1, 0.04); } },
    cone: function () { if (!joue('cone')) { bruit(0.05, 0.2, 900, 300); ton(320, 0.08, 'triangle', 0.25, 0.6, 0.03); } },
    bouteille: function () { if (!joue('bouteille')) { bruit(0.12, 0.3, 7000, 2500); ton(2700, 0.09, 'sine', 0.18, 1, 0.02); } },
    fronde: function () { if (!joue('fronde')) { ton(380, 0.06, 'sine', 0.2, 2.5); bruit(0.08, 0.15, 3500, 800); } },
    pistolet: function () { if (!joue('pistolet')) { bruit(0.15, 0.7, 3000, 200); ton(90, 0.12, 'square', 0.4, 0.4); } },
    fusil: function () { if (!joue('fusil')) { bruit(0.3, 0.9, 2000, 100); ton(60, 0.25, 'sine', 0.5, 0.5); ton(1500, 0.04, 'square', 0.1, 1, 0.35); } },
    // Les trois du marche noir. La mitraillette part une fois PAR BALLE, douze
    // fois par seconde : court et sec. Le Molotov, c'est le verre qui casse
    // puis le « whoomp » — joue a l'ARRIVEE de la bouteille, par `Combat`.
    mitraillette: function () { if (!joue('mitraillette')) { bruit(0.06, 0.6, 3500, 300); ton(110, 0.05, 'square', 0.3, 0.5); } },
    carabine: function () { if (!joue('carabine')) { bruit(0.25, 0.9, 2500, 120); ton(70, 0.3, 'sine', 0.5, 0.4); ton(1200, 0.05, 'square', 0.1, 1, 0.5); } },
    molotov: function () { if (!joue('molotov')) { bruit(0.1, 0.4, 7000, 2500); bruit(0.5, 0.5, 900, 150); ton(55, 0.4, 'sine', 0.3, 0.6, 0.08); } },
    // Un souffle de poudre, seul ; le jet en continu, c'est `jet()` qui le tient.
    extincteur: function () { if (!joue('extincteur')) bruit(0.25, 0.18, 5000, 2500); },
    vide: function () { if (!joue('vide')) { ton(1400, 0.03, 'square', 0.15); ton(900, 0.03, 'square', 0.1, 1, 0.04); } },
    casse: function () { if (!joue('casse')) { bruit(0.2, 0.4, 3000, 400); ton(220, 0.08, 'square', 0.2, 0.5); } },
    degainer: function () { if (!joue('degainer')) { bruit(0.08, 0.1, 2500, 900); ton(520, 0.04, 'triangle', 0.1, 1, 0.05); } },
    arme: function (def) { (def && SFX[def.son] || SFX.coup)(); },
    /** Le jet de l'extincteur : la boucle tant que `actif`, eteinte sinon.
        A appeler A CHAQUE IMAGE avec la verite du moment — bouton relache,
        reservoir vide, char, mort : toutes les raisons de se taire passent par
        la. ⚠️ Sans echantillon, `boucle()` ne ferait rien : le filet relance
        un souffle court toutes les huit images. */
    jet: function (actif) {
      if (estCharge('extincteur')) { boucle('extincteur', !!actif); return; }
      if (actif && B.t % 8 === 0) SFX.extincteur();
    },
    mission: function () { ton(523, 0.1, 'square', 0.2); ton(659, 0.1, 'square', 0.2, 1, 0.1); ton(784, 0.25, 'square', 0.22, 1, 0.2); },
  };

  // --- Les voix des passants : un mot quand on se frole ------------------------------

  const Voix = {
    dernierT: -9999, chargees: false,
    liste: function () { return (B.defs && B.defs.audio && B.defs.audio.voix) || []; },

    /** Les repliques se chargent avec les bruitages : petites, et il en faut
        une sous la main des la premiere rencontre. */
    charger: function () {
      if (Voix.chargees || !ctx || !fenetre || !fenetre.fetch) return;
      Voix.chargees = true;
      Voix.liste().forEach(function (v) {
        if (!v.fichier) return;
        fenetre.fetch(base + B.defs.audio.dossier + '/' + v.fichier)
          .then(function (r) { return r.ok ? r.arrayBuffer() : Promise.reject(r.status); })
          .then(function (octets) { return new Promise(function (ok, ko) { ctx.decodeAudioData(octets, ok, ko); }); })
          .then(function (tampon) { tampons.set('voix-' + v.slug, [tampon]); })
          .catch(function () { /* muet, tant pis */ });
      });
    },

    // --- Les voix de l'histoire : une par personnage, chargees par mission ---

    enCours: null,           // la replique qui joue { source, gain }
    demandees: [],           // les slugs demandes (le banc n'a pas d'AudioContext : il verifie ceci)
    missionsChargees: new Set(),
    histoire: function () { return (B.defs && B.defs.audio && B.defs.audio.histoire) || []; },

    /** Les repliques d'une mission se telechargent quand on commence a lui parler. */
    chargerHistoire: function (mission) {
      if (Voix.missionsChargees.has(mission)) return;
      Voix.missionsChargees.add(mission);
      if (!ctx || !fenetre || !fenetre.fetch) return;
      Voix.histoire().filter(function (v) { return v.mission === mission && v.fichier; }).forEach(function (v) {
        fenetre.fetch(base + B.defs.audio.dossier + '/' + v.fichier)
          .then(function (r) { return r.ok ? r.arrayBuffer() : Promise.reject(r.status); })
          .then(function (octets) { return new Promise(function (ok, ko) { ctx.decodeAudioData(octets, ok, ko); }); })
          .then(function (tampon) {
            tampons.set('histoire-' + v.slug, [tampon]);
            // La replique qu'on affiche attendait justement cette voix : on la dit maintenant.
            if (Voix.attendue && Voix.attendue.slug === v.slug && !Voix.enCours) { const a = Voix.attendue; Voix.attendue = null; Voix.parler(a.slug, a.options); }
          })
          .catch(function () { /* la replique restera muette : le texte est la */ });
      });
    },

    /** Une replique de l'histoire. Une seule a la fois ; la radio et l'ambiance
        baissent pendant qu'on parle. `telephone` : la voix vient du combine.
        `fin` s'appelle quand la voix se tait (jamais si elle n'a pas joue). */
    parler: function (slug, options) {
      Voix.couper();
      Voix.demandees.push(slug);
      if (Voix.demandees.length > 50) Voix.demandees.shift();
      const cle = 'histoire-' + slug;
      const liste = tampons.get(cle);
      Voix.attendue = null;
      if (!pret() || !liste || !liste.length) { if (pret()) Voix.attendue = { slug: slug, options: options }; return null; }
      const def = Voix.histoire().find(function (v) { return v.slug === slug; });
      const source = ctx.createBufferSource();
      source.buffer = liste[0];
      const gain = ctx.createGain();
      gain.gain.value = def ? def.volume : 0.9;
      let sortie = gain;
      if (options && options.telephone && ctx.createBiquadFilter) {
        /* Le combine, c'est la BANDE telephonique : 300 Hz - 3,4 kHz. Un passe-haut
           puis un passe-bas la dessinent en laissant plat tout ce qu'il y a entre —
           c'est-a-dire l'essentiel de la parole.

           ⚠️ On avait mis un seul `bandpass` a 1,5 kHz (Q 1,2) : il pince bien plus
           serre qu'un vrai telephone et retire 6 dB par octave de part et d'autre.
           La voix y perdait le gros de son energie, et les 1,6x de compensation
           etaient loin du compte : sous 900 Hz — la ou la parole a le gros de sa
           puissance — la voix sortait PLUS BAS qu'en direct. Au telephone, on ne
           s'entendait plus parler.

           Le 2x qui reste n'est pas un caprice : une voix coupee de ses graves
           s'entend moins fort a puissance egale, et un appel se prend au milieu
           des moteurs et de la rue. Un combine, ca doit percer. */
        const haut = ctx.createBiquadFilter();
        haut.type = 'highpass'; haut.frequency.value = 300;
        const bas = ctx.createBiquadFilter();
        bas.type = 'lowpass'; bas.frequency.value = 3400;
        gain.gain.value *= 2;
        gain.connect(haut); haut.connect(bas); sortie = bas;
      }
      // ⚠️ Comme dans `echantillon()` : sans cette ligne la replique se charge,
      // se decode, « joue » (`enCours` est pose, la radio baisse, le texte
      // defile) et on n'entend RIEN. C'est la meme soudure oubliee deux fois.
      source.connect(gain);
      sortie.connect(maitre);
      Voix.baisserLeReste(true);
      source.onended = function () { if (Voix.enCours && Voix.enCours.source === source) { Voix.enCours = null; Voix.baisserLeReste(false); } if (options && options.fin) options.fin(); };
      source.start(ctx.currentTime);
      Voix.enCours = { source: source, gain: gain, slug: slug };
      return Voix.enCours;
    },

    couper: function () {
      Voix.attendue = null;
      if (!Voix.enCours) return;
      try { Voix.enCours.source.onended = null; Voix.enCours.source.stop(); } catch (e) { /* deja finie */ }
      Voix.enCours = null;
      Voix.baisserLeReste(false);
    },

    /** Le ducking : les boucles de musique (radio, ambiance) au quart pendant qu'on parle. */
    baisserLeReste: function (actif) {
      Mus.attenuation = actif ? 0.25 : 1;
      boucles.forEach(function (courante, slug) {
        if (slug.indexOf('radio-') !== 0 && slug.indexOf('ambiance-') !== 0) return;
        if (actif && courante.avant === undefined) { courante.avant = courante.gain.gain.value; courante.gain.gain.value = courante.avant * 0.25; }
        else if (!actif && courante.avant !== undefined) { courante.gain.gain.value = courante.avant; delete courante.avant; }
      });
      Voix.ducking = !!actif;
    },

    /** Une replique du catalogue, au hasard, pour ce genre — SANS regarder si
        sa voix est chargee : le texte se montre toujours (une bulle), la voix
        s'ajoute. `sauf` : la derniere dite, pour ne pas la redire tout de
        suite. Tire dans le de du jeu : la bulle est un etat visible. */
    choisir: function (genre, sauf) {
      const toutes = Voix.liste().filter(function (v) { return v.genre === genre; });
      const choix = toutes.length > 1 ? toutes.filter(function (v) { return v.slug !== sauf; }) : toutes;
      if (!choix.length) return null;
      return choix[Math.floor(B.rng() * choix.length)];
    },

    /** Un passant parle, si personne n'a parle depuis un moment. Rend le slug.
        `slug` : cette replique-la (choisie par `choisir`), sinon une au hasard. */
    //: Les dernieres repliques dites, toutes voix confondues : on ne les
    //: retire pas du tirage par politesse, on les retire parce que « jamais
    //: deux fois de suite la meme » etait ECRIT dans la fiche et FAUX dans le
    //: code. Un tirage au hasard peut sortir deux fois le meme : c'est sa
    //: definition.
    dernieres: [],

    /** LE CHOIX, separe du son — et c'est lui, la regle.

        ⚠️ `dire` a besoin de tampons charges, donc de fichiers ; la REGLE
        (« jamais une des dernieres, et par le hasard DU JEU ») n'a besoin de
        rien. Les deux melanges, elle n'etait jugeable que par un navigateur
        avec ses mp3 — c'est-a-dire nulle part.

        ⚠️ On ecarte les dernieres, MAIS on retombe sur la liste entiere s'il ne
        reste rien : une banque de trois dont on exclut trois n'en laisserait
        aucune, et la regle se retournerait contre elle-meme — plus personne ne
        parlerait. */
    tirer: function (liste) {
      if (!liste || !liste.length) return null;
      const reglages = (B.defs && B.defs.audio && B.defs.audio.parole) || {};
      const frais = liste.filter(function (v) { return Voix.dernieres.indexOf(v.slug) < 0; });
      const choix = frais.length ? frais : liste;
      // ⚠️ `B.rng()`, jamais `Math.random()` : tout le hasard du jeu y passe, et
      // c'est ce qui rend le banc reproductible — donc juge. Cette ligne-la lui
      // echappait, et c'etait precisement celle qu'on voulait pouvoir tester.
      const v = choix[Math.floor(B.rng() * choix.length)];
      Voix.dernieres.push(v.slug);
      while (Voix.dernieres.length > (reglages.memoire || 2)) Voix.dernieres.shift();
      return v;
    },

    dire: function (genre, x, y, slug) {
      const reglages = (B.defs && B.defs.audio && B.defs.audio.parole) || {};
      const mort = reglages.temps_mort_images || 420;
      if (B.t - Voix.dernierT < mort) return null;
      const tous = Voix.liste().filter(function (v) {
        return v.genre === genre && (!slug || v.slug === slug) && tampons.has('voix-' + v.slug);
      });
      const v = Voix.tirer(tous);
      if (!v) return null;
      Voix.dernierT = B.t;
      const j = B.joueur;
      echantillon('voix-' + v.slug, { volume: v.volume, pan: j ? (x - j.x) / 200 : 0 });
      return v.slug;
    },
  };

  // --- L'ambiance : la musique de fond, a pied ---------------------------------------

  const Ambiance = {
    courante: null, demandee: null, chargee: null,
    def: function () { const l = (B.defs && B.defs.audio && B.defs.audio.ambiances) || []; return l[0] || null; },

    /** A pied, la ville a sa musique. Elle se charge une fois, au premier geste. */
    jouer: function () {
      const a = Ambiance.def();
      if (!a) return false;
      Ambiance.demandee = a.slug;
      if (!ctx || !a.fichier) return true;
      if (tampons.has('ambiance-' + a.slug)) { Ambiance._demarrer(a); return true; }
      if (Ambiance.chargee === 'en cours') return true;
      Ambiance.chargee = 'en cours';
      fenetre.fetch(base + B.defs.audio.dossier + '/' + a.fichier)
        .then(function (r) { return r.ok ? r.arrayBuffer() : Promise.reject(r.status); })
        .then(function (octets) { return new Promise(function (ok, ko) { ctx.decodeAudioData(octets, ok, ko); }); })
        .then(function (tampon) {
          tampons.set('ambiance-' + a.slug, [tampon]);
          Ambiance.chargee = 'prete';
          if (Ambiance.demandee === a.slug) Ambiance._demarrer(a);
        })
        .catch(function () { Ambiance.chargee = null; });
      return true;
    },
    _demarrer: function (a) { boucle('ambiance-' + a.slug, true, a.volume); Ambiance.courante = a.slug; },
    arreter: function () {
      if (Ambiance.courante) boucle('ambiance-' + Ambiance.courante, false);
      Ambiance.courante = null; Ambiance.demandee = null;
    },
  };

  // --- Le chef d'orchestre : qui gagne, et quand ---------------------------------

  /*: ⚠️ C'est LA question qu'aucune des demandes ne posait et dont tout depend.
    Il y a deja la radio dans un char, l'ambiance a pied, la rumeur de la foule,
    les sirenes et les voix. Sans une echelle ECRITE UNE FOIS, chaque endroit du
    code aurait la sienne, et deux musiques joueraient ensemble un jour sur
    trois.

    L'echelle vient de Python (`musique.ECHELLE`) : le navigateur la LIT, il ne
    l'invente pas. Le plus petit gagne, et la rumeur passe dessous, toujours. */
  const Chef = {
    piste: null,          // le slug qui joue (procedural) ou null
    rang: 99,             // son rang dans l'echelle
    queue: 0,             // images restantes a la musique d'etat qui s'eteint
    district: null,       // le district dont on joue l'ambiance
    frontiere: null,      // ou l'on a bascule la derniere fois (hysteresis)

    reglages: function () { return (B.defs && B.defs.audio && B.defs.audio.musique) || {}; },
    echelle: function () { return (B.defs && B.defs.audio && B.defs.audio.echelle) || {}; },

    /** L'ambiance du district ou l'on se trouve, avec HYSTERESIS.

        ⚠️ On traverse une frontiere en zigzag sur un boulevard, et une musique
        qui bascule a chaque pas de cote est pire que pas de musique du tout.
        On ne change donc qu'apres avoir franchi `hysteresis_px` depuis le
        dernier basculement. */
    ambianceDuLieu: function () {
      const table = (B.defs && B.defs.audio && B.defs.audio.ambiances_de_district) || {};
      const j = B.joueur;
      if (!j) return null;
      const zone = Monde.zoneA(j.x, j.y);
      const slug = zone && (table[zone.district] || table[zone.slug]);
      if (!slug) return Chef.district;
      if (slug === Chef.district) { Chef.frontiere = null; return slug; }
      // ⚠️ L'hysteresis sert a ne pas BASCULER trop vite ; au tout premier
      // district, il n'y a rien a quitter. Sans ce cas, la musique attendait
      // qu'on marche six tuiles avant de commencer — c'est-a-dire qu'elle ne
      // commencait jamais si on restait sur place.
      if (!Chef.district) { Chef.district = slug; Chef.frontiere = null; return slug; }
      if (!Chef.frontiere) { Chef.frontiere = { x: j.x, y: j.y, slug: slug }; return Chef.district; }
      if (Chef.frontiere.slug !== slug) { Chef.frontiere = { x: j.x, y: j.y, slug: slug }; return Chef.district; }
      const seuil = Chef.reglages().hysteresis_px || 96;
      const d = Math.hypot(j.x - Chef.frontiere.x, j.y - Chef.frontiere.y);
      if (d < seuil) return Chef.district;
      Chef.frontiere = null;
      Chef.district = slug;
      return slug;
    },

    /** Ce qui devrait jouer, maintenant : { slug, rang } ou null. */
    voulu: function () {
      const r = Chef.reglages(), e = Chef.echelle();
      const j = B.joueur;
      if (!j || B.interieur || B.etat !== 'jeu') return null;
      // ⚠️ La QUEUE : une musique d'etat continue quelques secondes apres la
      // derniere etoile perdue. Sans elle, la poursuite demarrerait et
      // s'arreterait trois fois en dix secondes — et c'est cette queue qui
      // fait qu'on SOUFFLE.
      const chasse = B.recherche && B.recherche.etoiles >= (r.poursuite_etoiles || 2);
      const bagarre = Chef.bagarre();
      if (chasse || (Chef.piste === 'mus_poursuite' && Chef.queue > 0)) {
        if (chasse) Chef.queue = (r.poursuite_queue_s || 7) * 60;
        return { slug: 'mus_poursuite', rang: e.poursuite || 2 };
      }
      if (bagarre || (Chef.piste === 'mus_bagarre' && Chef.queue > 0)) {
        if (bagarre) Chef.queue = (r.bagarre_queue_s || 5) * 60;
        return { slug: 'mus_bagarre', rang: e.bagarre || 3 };
      }
      // ⚠️ La radio d'un char et l'ambiance ENREGISTREE occupent le rang de
      // l'ambiance : elles et le district ne jouent JAMAIS ensemble, c'est la
      // meme case de l'echelle. Le jour ou un vrai mp3 de district arrive, il
      // se pose ici et la piece ecrite en notes redevient le filet.
      // ⚠️ `demandee`, pas seulement `courante` : une station se DEMANDE tout
      // de suite et n'arrive qu'une seconde plus tard (le mp3 se telecharge).
      // Attendre son arrivee laisserait l'ambiance du district jouer par-dessus
      // pendant tout le chargement — deux musiques a la fois, ce que l'echelle
      // interdit.
      if (Radio.demandee || Radio.courante || Ambiance.demandee || Ambiance.courante) return null;
      const amb = Chef.ambianceDuLieu();
      return amb ? { slug: amb, rang: e.ambiance || 4 } : null;
    },

    /** Se bat-on avec une gang ? Deux membres d'une gang qui t'attaquent. */
    bagarre: function () {
      const j = B.joueur;
      if (!j || typeof Entites === 'undefined') return false;
      let n = 0;
      for (const q of Entites.pietonsAutour(j.x, j.y, 120)) {
        if (q.gang && q.vivant && q.etat === 'attaque_joueur') n++;
        if (n >= 2) return true;
      }
      return false;
    },

    maj: function () {
      if (Chef.queue > 0) Chef.queue--;
      const v = Chef.voulu();
      if (!v) {
        if (Chef.piste) { Mus.arreter(); Chef.piste = null; Chef.rang = 99; }
        return;
      }
      if (v.slug === Chef.piste) return;
      Chef.piste = v.slug; Chef.rang = v.rang;
      Chef.queue = Chef.queue || 0;
      Mus.jouer(v.slug);
    },

    arreter: function () { Mus.arreter(); Chef.piste = null; Chef.rang = 99; Chef.queue = 0; Chef.district = null; Chef.frontiere = null; },
  };

  // --- La rumeur : la foule qu'on entend sans la voir ----------------------------------

  const Rumeur = {
    //: JUSQU'A QUAND la rue se tait, et jusqu'a quand elle crie — en `B.t`, pas
    //: en images restantes. ⚠️ `maj` ne tourne qu'une image sur quinze : un
    //: compteur qu'on decremente de un a chaque appel met quinze fois trop
    //: longtemps a s'epuiser, et la rue ne revenait jamais. Une echeance ne se
    //: trompe pas de cadence.
    peurT: 0,
    criT: 0,
    //: Le volume rendu a la derniere image : la rumeur remonte DOUCEMENT, elle
    //: ne revient jamais d'un coup. Une foule qui reprend son murmure a la
    //: seconde ou l'arme rentre dans la poche n'a pas eu peur.
    volume: 0,

    /** ⚠️ LA RUE SE TAIT QUAND TU SORS UNE ARME. Une rue qui se tait d'un coup
        dit « ils t'ont vu » mieux qu'une etoile de plus, et elle le dit AVANT
        que tu regardes le HUD. */
    taire: function () {
      const r = (B.defs && B.defs.audio && B.defs.audio.rumeur) || {};
      Rumeur.peurT = B.t + (r.peur_images || 240);
    },

    /** ⚠️ Et apres un coup de feu, elle ne reprend PAS au meme endroit : elle
        revient en CRIS, puis se calme. Une foule qui murmure pareil avant et
        apres un mort n'est pas une foule, c'est un bruit de fond. */
    crier: function () {
      const r = (B.defs && B.defs.audio && B.defs.audio.rumeur) || {};
      Rumeur.criT = B.t + (r.cri_images || 150);
      Rumeur.peurT = 0;
    },

    /** Le volume suit le nombre de gens autour : rien dans une ruelle vide,
        un brouhaha sur la place — et la peur par-dessus. */
    maj: function (gens) {
      const r = (B.defs && B.defs.audio && B.defs.audio.rumeur) || {};
      const pas = r.retour_par_image || 0.004;
      let voulu = Math.min(1, gens / 10);
      if (B.t < Rumeur.criT) voulu = Math.min(1, voulu * (r.cri_part || 1.7));
      else if (B.t < Rumeur.peurT) voulu *= (r.peur_part || 0.18);
      // ⚠️ Elle TOMBE d'un coup et REMONTE doucement : c'est la chute qui se
      // remarque, et c'est la remontee lente qui fait qu'on se sent surveille
      // encore un moment apres avoir rangé l'arme.
      // ⚠️ `pas * 15` : `maj` ne tourne qu'une image sur quinze, et le pas de
      // la fiche est par IMAGE. Sans ce facteur, la remontee est quinze fois
      // trop lente — ce qui ne se voit pas, ca ressemble juste a une rue qui
      // ne revient pas.
      Rumeur.volume = voulu < Rumeur.volume
        ? voulu
        : Math.min(voulu, Rumeur.volume + pas * 15);
      if (Rumeur.volume <= 0.02) { boucle('foule', false); return; }
      if (!boucleActive('foule')) boucle('foule', true, Rumeur.volume);
      reglerBoucle('foule', Rumeur.volume);
    },
  };

  // --- La radio : une station par char, chargee au premier tour de cle ---------

  const Radio = {
    courante: null,          // slug de la station qui joue
    demandee: null,          // slug demande pendant que le fichier arrive
    chargees: new Map(),     // slug -> AudioBuffer

    /** ⚠️ DEUX SOURCES, une seule liste. Une station est soit un mp3 genere par
        ElevenLabs (`audio.radios`), soit une station PROCEDURALE : un morceau
        de `audio.musiques` marque `station` par Python, joue par le sequenceur
        qui fait deja le theme du menu. Le camion et la remorqueuse ont la
        leur, ecrite par une graine — sans ca, leur bouton RADIO ne faisait
        rien du tout, parce que `station()` ne cherchait que dans les mp3. */
    stations: function () {
      const mp3 = (B.defs && B.defs.audio && B.defs.audio.radios) || [];
      return mp3.concat(Mus.morceaux().filter(function (m) { return m.station; }));
    },
    station: function (slug) { return Radio.stations().find(function (r) { return r.slug === slug; }) || null; },
    /** Une station sans fichier : c'est le sequenceur qui la joue. */
    estProcedurale: function (slug) {
      const s = Radio.station(slug);
      return !!(s && !s.fichier);
    },

    /** Allume une station. Le fichier se telecharge la premiere fois : la
        musique arrive une seconde apres le demarrage, comme une vraie radio. */
    jouer: function (slug) {
      const station = Radio.station(slug);
      Radio.arreter();
      if (!station) return false;
      // ⚠️ La radio REMPLACE la musique de la ville, et c'est ICI que ca se
      // decide — pas seulement en montant dans un char. Un char sans station
      // par defaut (ambulance, autobus, velo) garde l'ambiance a pied ; quand
      // on y allume la radio au bouton, la station jouait PAR-DESSUS la ville.
      // On coupe des la demande, pas a l'arrivee du mp3 : sinon les deux se
      // chevauchent le temps du telechargement.
      Ambiance.arreter();
      Radio.demandee = slug;
      // Une station procedurale n'a rien a telecharger : le sequenceur la joue
      // note par note, comme le theme du menu. Elle demarre donc tout de suite,
      // meme hors ligne — c'est le meme filet que partout dans `audio.py`.
      if (!station.fichier) { Radio.courante = slug; Mus.jouer(slug); return true; }
      if (!ctx) return true;                               // pas d'audio : on garde l'etat
      if (tampons.has('radio-' + slug)) { Radio._demarrer(slug); return true; }
      if (Radio.chargees.get(slug) === 'en cours') return true;
      Radio.chargees.set(slug, 'en cours');
      fenetre.fetch(base + B.defs.audio.dossier + '/' + station.fichier)
        .then(function (r) { return r.ok ? r.arrayBuffer() : Promise.reject(r.status); })
        .then(function (octets) { return new Promise(function (ok, ko) { ctx.decodeAudioData(octets, ok, ko); }); })
        .then(function (tampon) {
          tampons.set('radio-' + slug, [tampon]);
          Radio.chargees.set(slug, 'prete');
          if (Radio.demandee === slug) Radio._demarrer(slug);
        })
        .catch(function () { Radio.chargees.delete(slug); });
      return true;
    },

    _demarrer: function (slug) {
      const station = Radio.station(slug);
      boucle('radio-' + slug, true, station ? station.volume : 0.4);
      Radio.courante = slug;
    },

    arreter: function () {
      // ⚠️ On n'arrete le sequenceur QUE s'il jouait une station : au titre il
      // joue le theme du menu, et descendre d'un char ne doit pas l'eteindre.
      if (Radio.courante && Radio.estProcedurale(Radio.courante)) Mus.arreter();
      else if (Radio.courante) boucle('radio-' + Radio.courante, false);
      Radio.courante = null;
      Radio.demandee = null;
    },

    /** Le bouton RADIO : la station suivante, puis le silence, puis la premiere. */
    suivante: function () {
      const liste = Radio.stations();
      if (!liste.length) return null;
      const i = liste.findIndex(function (r) { return r.slug === Radio.demandee; });
      if (i === liste.length - 1) { Radio.arreter(); return null; }
      const prochaine = liste[i + 1].slug;
      Radio.jouer(prochaine);
      return prochaine;
    },
  };

  // --- La musique : un sequenceur, un catalogue de notes (app/musique.py) ------

  //: On programme toujours un quart de seconde d'avance. En dessous, un a-coup
  //: d'images (une carte qui se dessine, un onglet qui revient) laisserait un
  //: trou dans la mesure ; au-dessus, arreter la musique laisserait sonner ce
  //: qui est deja pose.
  const HORIZON_S = 0.25;

  /** Le la du diapason : MIDI 69 = 440 Hz, douze demi-tons par octave. */
  function frequence(midi) { return 440 * Math.pow(2, (midi - 69) / 12); }

  const Mus = {
    courante: null,     // slug du morceau demande
    // ⚠️ Le ducking passe par ici pour une station PROCEDURALE : elle ne
    // traverse aucune boucle (`boucles`), donc `baisserLeReste` ne pouvait pas
    // l'atteindre — la radio du camion aurait couvert la voix au telephone.
    // Le changement met jusqu'a HORIZON_S a s'entendre : les notes deja
    // programmees gardent leur volume, et c'est bien ainsi (couper net une
    // mesure s'entend plus qu'un quart de seconde de trop).
    attenuation: 1,
    pas: 0,             // ou l'on en est, en pas (avance meme sans audio)
    debutT: 0,          // l'instant audio du pas 0 ; 0 = pas encore demarre
    prochain: 0,        // le prochain pas a programmer

    morceaux: function () { return (B.defs && B.defs.audio && B.defs.audio.musiques) || []; },
    def: function (slug) {
      if (!slug) return null;
      const l = Mus.morceaux();
      for (let i = 0; i < l.length; i++) if (l[i].slug === slug) return l[i];
      return null;
    },

    /** Demande un morceau. Le redemander pendant qu'il joue ne le fait PAS
        repartir du debut : le menu le reclame a chaque image. */
    jouer: function (slug) {
      if (Mus.courante === slug) return true;
      if (!Mus.def(slug)) { Mus.arreter(); return false; }
      Mus.courante = slug; Mus.pas = 0; Mus.debutT = 0; Mus.prochain = 0;
      return true;
    },

    arreter: function () { Mus.courante = null; Mus.pas = 0; Mus.debutT = 0; Mus.prochain = 0; },
    stop: function () { Mus.arreter(); },       // l'ancien nom, garde par prudence

    /** Pose toutes les notes d'un pas, a l'instant `t`. */
    poser: function (def, p, t, pasS) {
      for (let v = 0; v < def.voix.length; v++) {
        const voix = def.voix[v];
        const motif = voix.motif || def.pas;
        const dans = ((p % motif) + motif) % motif;
        for (let n = 0; n < voix.notes.length; n++) {
          const note = voix.notes[n];
          if (note[0] !== dans) continue;
          const volume = (voix.volume || 0.2) * (note[3] === undefined ? 1 : note[3])
                       * (def.volume || 1) * Mus.attenuation;
          if (voix.forme === 'bruit') bruitA(t, Math.min(0.12, note[2] * pasS), volume, note[1]);
          // ⚠️ 0.92 : la note s'arrete juste avant la suivante. Sans ce blanc,
          // deux notes voisines de meme hauteur n'en font plus qu'une longue.
          else tonA(t, frequence(note[1]), note[2] * pasS * 0.92, voix.forme, volume);
        }
      }
    },

    /** Une image de musique. A appeler a CHAQUE image, y compris au menu. */
    tick: function () {
      const def = Mus.def(Mus.courante);
      if (!def) return;
      // ⚠️ Tant que le son n'est pas accorde (banc sans audio, ou navigateur qui
      // attend un geste), on avance un simple compteur : l'horloge audio est
      // figee, et programmer dedans ferait sortir toute la boucle d'un coup au
      // reveil. Le morceau demarrera pour de bon a la premiere image sonore.
      if (etatSon() !== 'actif') { Mus.pas++; Mus.debutT = 0; Mus.prochain = 0; return; }
      const pasS = 60 / def.bpm / (def.pas_par_temps || 1);
      if (!Mus.debutT) { Mus.debutT = ctx.currentTime + 0.08; Mus.prochain = 0; }
      const limite = ctx.currentTime + HORIZON_S;
      // Un garde-fou : si l'onglet dort une minute, on ne rattrape pas mille
      // pas d'un coup — on se recale sur l'horloge.
      const retard = (ctx.currentTime - Mus.debutT) / pasS - Mus.prochain;
      if (retard > 32) { Mus.prochain = Math.floor((ctx.currentTime - Mus.debutT) / pasS); }
      while (Mus.debutT + Mus.prochain * pasS < limite) {
        Mus.poser(def, Mus.prochain, Mus.debutT + Mus.prochain * pasS, pasS);
        Mus.prochain++;
      }
      Mus.pas = Math.max(0, Math.floor((ctx.currentTime - Mus.debutT) / pasS));
    },
  };

  return {
    init, reveiller, sonder, etatSon, enAttente, surEtat, pret, suspendre, fermer, majVolume, ton, bruit, SFX, Mus, Chef,
    chargerEchantillons, echantillon, joue, estCharge, jouerA, boucle, boucleActive, reglerBoucle,
    Radio, Ambiance, Rumeur, Voix,
    get contexte() { return ctx; },
    // ⚠️ Les bruitages seuls : les voix, l'ambiance et les radios ont leurs
    // propres clefs dans `tampons`, et le test des bruitages compte l'egalite.
    get charges() {
      const audio = B.defs && B.defs.audio;
      if (!audio) return 0;
      return audio.echantillons.filter(function (e) { return tampons.has(e.slug); }).length;
    },
  };
})();
