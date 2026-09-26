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
  const prechauffes = new Set();  // les fichiers deja tires dans le cache du navigateur

  function init(w, urlStatique) { fenetre = w; base = urlStatique || '/static/'; }

  /** Telecharge et decode un fichier : la promesse d'un tampon.

      ⚠️ Le SEUL chemin des six chargements d'audio (echantillons, voix des
      passants, voix de l'histoire, ambiance, radio, musique) : chacun se compte
      (`Chargements`), et c'est ce que montre l'icone du coin. Six copies de la
      meme chaine, c'etait six endroits ou oublier de compter. */
  function decoder(url) {
    return Chargements.suivre(fenetre.fetch(url)
      .then(function (r) { return r.ok ? r.arrayBuffer() : Promise.reject(r.status); })
      .then(function (octets) { return new Promise(function (ok, ko) { ctx.decodeAudioData(octets, ok, ko); }); }));
  }

  /** Tirer des mp3 dans le CACHE DU NAVIGATEUR avant d'en avoir besoin.

      ⚠️ Ce n'est pas un chargement : rien n'est decode, rien n'est garde ici.
      Decoder exige un `AudioContext`, et il n'y en a pas avant le premier geste
      de la main — c'est justement la fenetre qu'on veut utiliser, pendant que
      quelqu'un lit l'ecran titre. Au geste, `chargerMorceau` et `chargerHistoire`
      trouvent les octets dans le cache et decodent sans un aller-retour.

      ⚠️ A RESERVER A CE QUI DOIT SONNER TOUT DE SUITE. `static/audio/` pese
      12 Mo en 166 fichiers, et tout le reste se charge a l'usage : prechauffer
      largement, ce serait avaler la ville sur un forfait cellulaire pour une
      partie de deux minutes. Rend le nombre de fichiers demandes. */
  function prechauffer(fichiers) {
    if (!fenetre || !fenetre.fetch || !B.defs || !B.defs.audio) return 0;
    let n = 0;
    (fichiers || []).forEach(function (f) {
      if (!f || prechauffes.has(f)) return;
      prechauffes.add(f);
      n++;
      // ⚠️ On LIT le corps : `fetch` se resout aux en-tetes, et l'icone du coin
      // s'eteindrait avant que le fichier soit vraiment dans le cache.
      Chargements.suivre(fenetre.fetch(base + B.defs.audio.dossier + '/' + f)
        .then(function (r) { return r.arrayBuffer ? r.arrayBuffer() : r; }))
        .catch(function () { /* on jouera sans */ });
    });
    return n;
  }

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
    // ⚠️ Net : la page s'en va, le contexte se ferme juste apres — un fondu n'aurait personne a qui parler.
    Mus.arreter(0); Mus.sortantes.length = 0;
    try { parti.close(); } catch (e) { /* deja fermee */ }
  }

  //: Le volume et le panoramique du son en cours, le temps d'un appel a
  //: `depuis` — null le reste du temps. ⚠️ `joue`, `ton` et `bruit` le lisent :
  //: c'est ce qui pose dans le monde TOUS les effets du combat (une douzaine
  //: d'armes, chacune avec son filet) sans les reecrire un par un.
  let ici = null;

  //: L'image du dernier bris de decor entendu (`SFX.bris`) : un seul par image.
  let dernierBris = -1;

  /** Une note : frequence en Hz, duree en s, forme, volume, glisse (facteur de frequence finale). */
  function ton(freq, duree, forme, volume, glisse, depart) {
    if (!pret()) return;
    tonA(ctx.currentTime + (depart || 0), freq, duree, forme, ici ? (volume || 0.4) * ici.volume : volume, glisse);
  }

  /** La meme note, mais POSEE a un instant de l'horloge audio. C'est ce qu'il
      faut a un sequenceur : on programme la mesure suivante pendant que la
      mesure courante joue, et le rythme ne depend plus du rythme des images. */
  function tonA(t0, freq, duree, forme, volume, glisse, sortie) {
    if (!pret()) return;
    const osc = ctx.createOscillator();
    const gain = ctx.createGain();
    osc.type = forme || 'square';
    osc.frequency.setValueAtTime(freq, t0);
    if (glisse) osc.frequency.exponentialRampToValueAtTime(Math.max(20, freq * glisse), t0 + duree);
    gain.gain.setValueAtTime(0.0001, t0);
    gain.gain.exponentialRampToValueAtTime(volume || 0.4, t0 + 0.01);
    gain.gain.exponentialRampToValueAtTime(0.0001, t0 + duree);
    // ⚠️ `sortie` : ou la note aboutit. Par defaut le maitre, comme tout le
    // reste — mais le musicien de rue a besoin d'un gain a LUI, parce que son
    // volume suit la distance et change a chaque image. Sans ce parametre, il
    // aurait fallu recalculer le volume de chaque note au moment de la poser,
    // c'est-a-dire un quart de seconde EN AVANCE (voir HORIZON_S) : on
    // l'aurait entendu jouer fort une fraction de seconde apres etre parti.
    osc.connect(gain).connect(sortie || maitre);
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
    gain.gain.setValueAtTime((volume || 0.5) * (ici ? ici.volume : 1), t0);
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
  function bruitA(t0, duree, volume, coupure, sortie) {
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
    src.connect(filtre).connect(gain).connect(sortie || maitre);
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
  /** Les slugs qui n'appartiennent qu'aux bruits de quartier (M15, 2e vague) :
      ils ne se chargent PAS au demarrage — voir `chargerEchantillons`. */
  function slugsDeQuartier() {
    const q = (B.defs && B.defs.audio && B.defs.audio.quartiers) || {};
    const vus = new Set();
    Object.keys(q.sons || {}).forEach(function (d) {
      q.sons[d].forEach(function (e) { vus.add(e.slug); });
    });
    return vus;
  }

  function chargerEchantillons() {
    const audio = B.defs && B.defs.audio;
    if (demandes || !ctx || !audio || !fenetre || !fenetre.fetch) return;
    demandes = true;
    const dossier = base + audio.dossier + '/';
    // ⚠️ LES BRUITS DE QUARTIER NE SE CHARGENT PAS ICI (M15, 2e vague) : ils
    // sont RARES et PROPRES A UN DISTRICT — `Quartier.charger` les demande
    // en y entrant. Les charger tous au demarrage doublait presque le budget
    // de bruitages (2,83 Mo pour 2,5 Mo) pour des sons qu'une partie n'entend
    // peut-etre jamais si on ne visite pas le quartier.
    const deQuartier = slugsDeQuartier();
    audio.echantillons.forEach(function (e) {
      if (deQuartier.has(e.slug)) return;
      (e.fichiers || []).forEach(function (nom) {
        decoder(dossier + nom)
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
    // ⚠️ `fondu` (en secondes) : la musique entre PAR la chaine de fondu, pas
    // directement sur le maitre — voir « Le fondu enchaine ». Le volume, lui,
    // reste sur `gain` : la distance et le ducking le reposent sans toucher au fondu.
    const chaine = options && options.fondu !== undefined ? chaineDeFondu(options.fondu) : null;
    sortie.connect(chaine ? chaine.entree : maitre);
    source.start(ctx.currentTime);
    return { source: source, gain: gain, base: def ? def.volume : 1, fondu: chaine };
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

  function joue(slug) { return echantillon(slug, ici) !== null; }

  /** `joue`, mais COUPE au bout de `duree` secondes, en fondu : un geste bref
      qui emprunte un echantillon plus long que lui (la passe du pistolet a
      peinture dans le souffle de l'extincteur). `part` dose le volume (1 =
      celui du catalogue). Rend vrai si l'echantillon est parti. */
  function bref(slug, duree, part) {
    const options = ici ? { volume: ici.volume * (part || 1), pan: ici.pan } : { volume: part || 1 };
    const j = echantillon(slug, options);
    if (!j) return false;
    const fondu = 0.06, t = ctx.currentTime + Math.max(0, duree - fondu);
    const g = j.gain.gain.value;
    // Une courbe, pas une rampe : c'est ce que le banc lit (et un seul appel
    // par gain, comme le fondu de la musique).
    j.gain.gain.setValueCurveAtTime(Array.from(courbeDeFondu(false), function (c) { return c * g; }), t, fondu);
    try { j.source.stop(t + fondu + 0.02); } catch (e) { /* deja finie */ }
    return true;
  }

  //: LE BRIS D'UN DECOR, par matiere, dans les echantillons DEJA PAYES : le bois
  //: et le plastique qui cassent (`casse`, un manche qui claque et ses morceaux
  //: sur l'asphalte), le metal qui sonne (`pelle`, un clang), le verre qui
  //: eclate (`bouteille`). ⚠️ Le reste — buisson, chateau de sable, matelas,
  //: manche a air — n'a que sa poussiere : un craquement de bois sur un
  //: buisson sonnerait faux. Et la borne, le guichet et les distributrices ont
  //: leur propre son (`borne_cassee`, `argent`, `monnaie`), joue par `briser`.
  const MATIERE_DU_BRIS = {
    lampadaire: 'pelle', parcometre: 'pelle', boite_aux_lettres: 'pelle', poteau_amarrage: 'pelle',
    baril: 'pelle', caddie: 'pelle', kiosque_journaux: 'pelle', bbq: 'pelle',
    poubelle: 'pelle', poubelle_pleine: 'pelle',
    abribus: 'bouteille', abribus_nord: 'bouteille', abribus_est: 'bouteille', abribus_ouest: 'bouteille',
    bac: 'casse', cible_foire: 'casse', table_pique_nique: 'casse', chaise_sauveteur: 'casse',
    banc: 'casse', banc_nord: 'casse', banc_est: 'casse', banc_ouest: 'casse', bac_fleurs: 'casse',
    bac_recyclage: 'casse', palettes: 'casse', caisse: 'casse', cabanon: 'casse',
    corde_a_linge: 'casse', ordures: 'casse', pneu: 'casse',
  };

  /** Combien s'entend ce qui se passe en (x, y) : 0 hors de l'ecran, et de plus
      en plus fort a mesure que le joueur s'approche (`audio.coups_des_autres`).

      ⚠️ L'ECRAN, pas une distance : la vue est plus large que haute, et la rixe
      de gangs nait juste au-dela de son bord. Un rayon qui s'entend a 300 px
      entend aussi, en haut et en bas, ce que l'ecran ne montre pas. */
  function presence(x, y) {
    const j = B.joueur, cam = B.cam;
    if (!j || !cam) return 0;
    const r = (B.defs && B.defs.audio && B.defs.audio.coups_des_autres) || {};
    const m = r.marge_px || 0;
    if (x < cam.x - m || x > cam.x + VW + m || y < cam.y - m || y > cam.y + VH + m) return 0;
    return Math.max(0, 1 - Math.hypot(x - j.x, y - j.y) / (r.portee_px || 300));
  }

  /** Joue `effet` (un `SFX`) comme s'il venait de `qui` : muet si on ne le voit
      pas, plus fort de pres, a gauche s'il est a gauche. Le joueur s'entend
      toujours plein volume. Rend le volume (0 = rien n'est parti).

      ⚠️ Retour de Martin : « je veux pas entendre quand on les voit pas ». Le
      coup et le grognement d'une rixe hors champ partaient au plein volume. */
  function depuis(qui, effet) {
    if (!qui || qui === B.joueur) { effet(); return 1; }
    const v = presence(qui.x, qui.y);
    if (v <= 0) return 0;
    const r = (B.defs && B.defs.audio && B.defs.audio.coups_des_autres) || {};
    ici = { volume: v, pan: (qui.x - B.joueur.x) / (r.portee_px || 300) };
    // ⚠️ `finally` : un effet qui leve laisserait `ici` pose, et TOUS les sons
    // suivants du jeu — le joueur compris — sortiraient a ce volume-la.
    try { effet(); } finally { ici = null; }
    return v;
  }

  /** Ce son est-il pret a jouer ? ⚠️ Repondre en le JOUANT (comme le faisaient
      les tests) demarre une source a chaque appel : dans une boucle d'attente,
      ca finit par des centaines de sources en vol et le contexte cale. */
  function estCharge(slug) {
    const liste = tampons.get(slug);
    return !!liste && liste.length > 0;
  }

  // --- Le fondu enchaine : la regle de TOUTE la musique ---------------------------------
  /*: ⚠️ Demande de Martin (20 sept. 2026) : « les transitions de musique doivent
    toujours se faire en crossover, a moins que ce soit necessaire pour l'effet
    et l'ambiance ». Avant, `boucle(..., false)` faisait `source.stop()` : la
    piste s'arretait NET et la suivante partait apres — un blanc, ou un coup sec.
    Maintenant celle qui s'en va BAISSE pendant que celle qui arrive MONTE.

    ⚠️ Trois choses a ne pas defaire :
    - **Deux gains, pas un** (`entree`, puis `sortie`). Poser une courbe sur un
      parametre qui en suit deja une leve `NotSupportedError` : quelqu'un qui
      change encore de piste pendant le fondu d'entree aurait fait taire toute la
      musique. Chaque gain ne recoit qu'UNE courbe.
    - **Puissance constante** (sinus, cosinus), pas une rampe lineaire : deux
      morceaux qui n'ont rien en commun sonnent deux fois moins fort au milieu
      d'une rampe lineaire, et on entend le creux.
    - **La piste qui sort quitte `boucles` TOUT DE SUITE** : sa cle est libre pour
      la suivante (redemander la meme toune ne tombe pas sur elle), et
      `boucleActive` ne dit « vrai » que de ce qu'on est cense entendre.

    ⚠️ **UNE COUPURE FRANCHE SE DEMANDE.** Le fondu est ce qui arrive par defaut
    a toute la musique ; couper net, c'est passer `0` a l'appel
    (`Mus.jouer(slug, 0)`, `Mus.arreter(0)`) — et ecrire la raison a cet endroit,
    parce que ce n'est jamais un oubli qu'on veut y trouver. */
  const POINTS_DE_COURBE = 64;

  /** La courbe d'un fondu, de 0 a 1 (`entrant`) ou de 1 a 0, a PUISSANCE CONSTANTE. */
  function courbeDeFondu(entrant) {
    const c = new Float32Array(POINTS_DE_COURBE);
    for (let i = 0; i < POINTS_DE_COURBE; i++) {
      const x = i / (POINTS_DE_COURBE - 1) * Math.PI / 2;
      c[i] = entrant ? Math.sin(x) : Math.cos(x);
    }
    return c;
  }

  /** Combien de secondes dure un fondu. `vif` : celui de la musique d'ETAT qui
      arrive et du musicien de rue. ⚠️ Les chiffres viennent de Python
      (`musique.MUSIQUE`), comme l'echelle : le navigateur les LIT. */
  function dureeFondu(vif) {
    const r = reglagesMusique();
    return vif ? (r.fondu_vif_s || 0.7) : (r.fondu_s || 2);
  }

  /** Les chiffres de la musique, tels que Python les ecrit (`musique.MUSIQUE`). */
  function reglagesMusique() { return (B.defs && B.defs.audio && B.defs.audio.musique) || {}; }

  /** La poursuite et la bagarre : les deux pistes qui prennent toute la place. */
  function pisteDEtat(slug) { return slug === 'mus_poursuite' || slug === 'mus_bagarre'; }

  /** Les deux gains d'un fondu, branches sur le maitre. Tout ce qu'on branche
      sur `entree` monte pendant `duree` secondes (0 : plein tout de suite), et
      `sortir(d)` le fait redescendre jusqu'au silence en `d` secondes. */
  function chaineDeFondu(duree) {
    const entree = ctx.createGain(), sortie = ctx.createGain();
    entree.connect(sortie);
    sortie.connect(maitre);
    if (duree > 0) {
      entree.gain.value = 0;
      entree.gain.setValueCurveAtTime(courbeDeFondu(true), ctx.currentTime, duree);
    }
    let sortant = false;
    return {
      entree: entree,
      sortir: function (d) {
        if (sortant) return;
        sortant = true;
        sortie.gain.setValueCurveAtTime(courbeDeFondu(false), ctx.currentTime, d);
      },
    };
  }

  /** Eteint une boucle : en fondu si elle en a un et qu'on en demande un, net sinon. */
  function eteindre(courante, fondu) {
    if (fondu > 0 && courante.fondu && ctx) {
      courante.fondu.sortir(fondu);
      // ⚠️ Un peu APRES la fin de la courbe, jamais avant : arreter la source a
      // l'instant ou le gain touche zero laisserait un claquement.
      try { courante.source.stop(ctx.currentTime + fondu + 0.05); } catch (e) { /* deja finie */ }
      return;
    }
    try { courante.source.stop(); } catch (e) { /* deja finie */ }
  }

  /** Une boucle qu'on allume et qu'on eteint (sirene, moteur — et la musique, qui
      passe `fondu`, en secondes : voir plus haut). Sans `fondu`, elle part et
      s'arrete net, comme un moteur. */
  function boucle(slug, actif, volume, fondu) {
    const courante = boucles.get(slug);
    if (actif && !courante) {
      const jouee = echantillon(slug, { boucle: true, volume: volume, fondu: fondu });
      if (jouee) boucles.set(slug, jouee);
    } else if (!actif && courante) {
      boucles.delete(slug);
      eteindre(courante, fondu);
    }
  }

  // --- Le ducking : la musique se retire quand quelqu'un parle, GRADUELLEMENT ---------
  /*: ⚠️ Demande de Martin (20 sept. 2026), dans le prolongement du fondu enchaine :
    « il faut aussi baisser les volumes et les monter graduellement ». Avant, la
    musique tombait au quart D'UN COUP a la premiere syllabe d'une replique et
    revenait d'un coup a la derniere : deux repliques qui s'enchainaient la
    faisaient sauter deux fois.

    ⚠️ Le niveau GLISSE vers sa cible a chaque image de `maj()`, qui tourne a pas
    fixe (60 par seconde, `jeu.js`) : `baisse_s` et `remonte_s` sont de vraies
    secondes, quelle que soit la frequence de l'ecran — et le banc, qui rejoue les
    memes pas, voit la meme courbe.

    ⚠️ Elle REMONTE PLUS LENTEMENT qu'elle ne baisse, et c'est voulu : entre deux
    repliques d'une meme conversation, la musique n'a pas le temps de revenir.

    ⚠️ Ce qui glisse, c'est le NIVEAU ; qui l'applique reste a chacun : les boucles
    (`musique-`, `radio-`, `ambiance-`), les notes du sequenceur (`Mus.attenuation`,
    lue a la pose : jusqu'a HORIZON_S de retard, ce qui est deja programme garde son
    volume) et le musicien de rue (`Rue.attenuation`). */
  const IMAGE_S = 1 / 60;

  /** Un niveau qui rejoint sa `cible` GRADUELLEMENT, un pas de `maj()` a la fois :
      exponentiel, donc sans a-coup au depart, et arrete net quand il y est. */
  function glisser(niveau, cible) {
    if (niveau === cible) return niveau;
    const r = reglagesMusique();
    const duree = cible < niveau ? (r.baisse_s || 0.3) : (r.remonte_s || 1.2);
    const suivant = niveau + (cible - niveau) * (1 - Math.exp(-IMAGE_S / (duree / 3)));
    return Math.abs(cible - suivant) < 0.005 ? cible : suivant;
  }

  /** Une boucle qui est de la MUSIQUE (celle qui baisse pendant une replique). ⚠️
      `rue-` est absent expres : le musicien de rue repose son gain a chaque image,
      attenuation comprise (`Rue.tick`). */
  function boucleDeMusique(slug) {
    return slug.indexOf('radio-') === 0 || slug.indexOf('ambiance-') === 0 || slug.indexOf('musique-') === 0;
  }

  const Duck = {
    niveau: 1,          // 1 = plein ; `ducking` = tout en bas
    cible: 1,

    /** Ou l'on veut aller : `actif` = quelqu'un parle. */
    viser: function (actif) {
      Duck.cible = actif ? (reglagesMusique().ducking || 0.25) : 1;
    },

    /** Une image (`Mus.tick`). Ne fait rien quand tout est au plein volume.
        ⚠️ Elle tourne AUSSI quand le niveau est installe en bas : une boucle
        demarree pendant une replique n'a pas encore son `avant`. */
    maj: function () {
      if (Duck.niveau === 1 && Duck.cible === 1) return;
      Duck.niveau = glisser(Duck.niveau, Duck.cible);
      Mus.attenuation = Duck.niveau;
      Rue.attenuation = Duck.niveau;
      boucles.forEach(function (courante, slug) {
        if (!boucleDeMusique(slug)) return;
        // ⚠️ `avant` = le volume SANS ducking, pris la premiere fois qu'on baisse ce
        // qui joue : une boucle demarree PENDANT une replique le prend a son tour, et
        // baisse elle aussi au lieu de couvrir la voix.
        if (Duck.niveau < 1) {
          if (courante.avant === undefined) courante.avant = courante.gain.gain.value;
          courante.gain.gain.value = courante.avant * Duck.niveau;
        } else if (courante.avant !== undefined) {
          courante.gain.gain.value = courante.avant;
          delete courante.avant;
        }
      });
    },
  };

  /** Regle une boucle en marche : volume (0..1) et hauteur (1 = normale).
      C'est ce qui fait monter le moteur dans les tours. */
  function reglerBoucle(slug, volume, hauteur) {
    const courante = boucles.get(slug);
    if (!courante) return;
    if (volume !== undefined) courante.gain.gain.value = courante.base * volume;
    if (hauteur !== undefined && courante.source.playbackRate) courante.source.playbackRate.value = hauteur;
  }

  function boucleActive(slug) { return boucles.has(slug); }

  /** Le volume d'une boucle en marche, ou null. Le pendant en LECTURE de
      `reglerBoucle` : c'est ce qui permet de juger qu'un son pose dans le monde
      suit vraiment la distance, sans aller fouiller le graphe audio a la main
      (et sans confondre sa source avec le dernier bruitage qui a joue). */
  function volumeBoucle(slug) {
    const courante = boucles.get(slug);
    return courante ? courante.gain.gain.value : null;
  }

  //: Le passe-bas d'une boucle entendue a travers un mur : ouvert, il laisse
  //: tout passer ; ferme, il ne garde que le grave — le rotor sans son sifflement.
  const COUPURE_CLAIRE = 20000, COUPURE_SOURDE = 250;

  /** Etouffe une boucle en marche : `part` 0 = en plein air, 1 = a travers un
      toit. Le passe-bas se glisse entre la source et le gain a la premiere
      demande : les boucles qu'on n'etouffe jamais n'en portent pas. */
  function etouffer(slug, part) {
    const courante = boucles.get(slug);
    if (!courante || !ctx || !ctx.createBiquadFilter) return;
    if (!courante.sourdine) {
      const filtre = ctx.createBiquadFilter();
      filtre.type = 'lowpass';
      filtre.Q.value = 0.7;
      // ⚠️ La source ne va QUE dans son gain (`echantillon`) : la debrancher puis
      // la rebrancher par le filtre ne perd rien d'autre en chemin.
      courante.source.disconnect();
      courante.source.connect(filtre).connect(courante.gain);
      courante.sourdine = filtre;
    }
    // Exponentielle : l'oreille entend des octaves, pas des hertz.
    const p = Math.max(0, Math.min(1, part));
    courante.sourdine.frequency.value = COUPURE_CLAIRE * Math.pow(COUPURE_SOURDE / COUPURE_CLAIRE, p);
  }

  /** La coupure du passe-bas d'une boucle (en Hz), ou null : jamais etouffee, ou
      eteinte. Le pendant en LECTURE d'`etouffer`, comme `volumeBoucle`. */
  function coupureBoucle(slug) {
    const courante = boucles.get(slug);
    return courante && courante.sourdine ? courante.sourdine.frequency.value : null;
  }

  // --- Ça travaille : le filet des sons de chantier ---------------------------------
  //: Chaque son de chantier sans son fichier, a un volume `v` (0..1) qui dit deja
  //: la distance. ⚠️ Le bip de recul N'EST QUE CA : ElevenLabs n'a rendu que des
  //: sifflements continus en trois essais (voir `audio.py`), et un bip de recul
  //: est un ton electronique — trois bips de 0,45 s, autant de silence entre eux.
  const REPLI_CHANTIER = {
    boule: function (v) { bruit(0.7, 0.5 * v, 900, 50); ton(46, 0.5, 'sine', 0.45 * v, 0.6); },
    marteau_piqueur: function (v) {
      const t0 = ctx.currentTime;
      for (let k = 0; k < 30; k++) bruitA(t0 + k * 0.06, 0.04, 0.16 * v, 900);
    },
    godet: function (v) { bruit(0.9, 0.22 * v, 1600, 300); ton(110, 0.5, 'sawtooth', 0.05 * v, 1.3, 0.2); },
    bip_recul: function (v) { for (let k = 0; k < 3; k++) ton(1050, 0.45, 'square', 0.06 * v, 1, k * 0.9); },
    marteau: function (v) {
      const t0 = ctx.currentTime;
      for (let k = 0; k < 3; k++) { tonA(t0 + k * 0.22, 420, 0.06, 'triangle', 0.22 * v, 0.7); bruitA(t0 + k * 0.22, 0.05, 0.2 * v, 2500); }
    },
    scie: function (v) { ton(1800, 1.4, 'sawtooth', 0.04 * v, 1.15); bruit(1.2, 0.08 * v, 5000, 2500); },
    // La benne qu'on pousse : la tôle qui racle le trottoir, et un coup sourd de caisse vide.
    conteneur: function (v) {
      const t0 = ctx.currentTime;
      bruitA(t0, 0.35, 0.2 * v, 1400);
      tonA(t0 + 0.05, 95, 0.18, 'square', 0.12 * v, 0.7);
      tonA(t0 + 0.05, 240, 0.25, 'triangle', 0.05 * v, 0.9);
    },
    // Le tas de terre : la roue attaque la pente (un coup sourd), la terre roule sous
    // la caisse (du gravier), et on retombe mollement. Synthétisé : du sable, pas du fer.
    tas: function (v) {
      const t0 = ctx.currentTime;
      tonA(t0, 62, 0.16, 'sine', 0.3 * v, 0.6);
      bruitA(t0, 0.28, 0.16 * v, 900);
      bruitA(t0 + 0.22, 0.14, 0.1 * v, 500);
    },
    // La plaque d'acier de la tranchée : la roue avant claque, la plaque résonne, et
    // la roue arrière claque à son tour. Synthétisée, comme le nid-de-poule : un
    // cahot n'a pas besoin d'un fichier.
    plaque: function (v) {
      const t0 = ctx.currentTime;
      for (const [dt, force] of [[0, 1], [0.13, 0.7]]) {
        tonA(t0 + dt, 210, 0.09, 'square', 0.2 * v * force, 0.55);
        bruitA(t0 + dt, 0.1, 0.18 * v * force, 3200);
        tonA(t0 + dt + 0.02, 560, 0.3, 'triangle', 0.08 * v * force, 0.96);
      }
    },
    // Le bras du camion a ordures : le moteur hydraulique, puis ce qui degringole.
    benne: function (v) { ton(160, 1.1, 'sawtooth', 0.05 * v, 1.5); bruit(0.8, 0.25 * v, 1400, 200); },
  };

  //: Ce que dure la sonnerie SYNTHETISEE, en secondes : son dernier coup part a
  //: 0,29 s et dure 0,08. ⚠️ Elle sert de fin de sonnerie quand le mp3 n'est pas
  //: (encore) la — le dialogue de l'appel l'attend, et attendre les deux secondes
  //: du fichier pendant que trois bips ont deja fini serait un silence pour rien.
  const SONNERIE_SYNTHESE = 0.37;

  // --- Les briques des sons de prime (le filet synthetise) ---------------------------
  /** La caisse enregistreuse : le tiroir qui claque, puis la clochette. */
  function caisse(depart) {
    ton(180, 0.06, 'square', 0.12, 0.6, depart);
    ton(2093, 0.35, 'sine', 0.22, 1, depart + 0.05);
    ton(2637, 0.5, 'sine', 0.18, 1, depart + 0.1);
  }
  /** `n` pieces qui tombent pendant `duree` secondes, a partir de `depart`.
      ⚠️ Sans `Math.random` : la hauteur et l'ecart se tirent de l'indice, pour
      que le son ne puise pas dans le hasard du jeu, et qu'il soit le meme
      d'une fois sur l'autre. */
  function pieces(n, duree, depart) {
    for (let i = 0; i < n; i++) {
      const f = 2900 + ((i * 7919) % 11) * 240, dt = ((i * 37) % 5) * 0.012;
      ton(f, 0.07, 'sine', 0.1, 0.97, depart + (i * duree) / n + dt);
    }
  }
  /** Do-mi-sol-do, vif : la fanfare des grosses primes. */
  function arpege(depart, pas, volume) {
    [523, 659, 784, 1047].forEach(function (f, i) { ton(f, i === 3 ? pas * 2.5 : pas, 'square', volume, 1, depart + i * pas); });
  }

  const SFX = {
    pas: function () { if (!joue('pas')) bruit(0.05, 0.12, 900, 300); },
    coup: function () { if (!joue('coup')) { ton(140, 0.08, 'square', 0.3, 0.5); bruit(0.08, 0.3, 800, 200); } },
    touche: function () { if (!joue('touche')) ton(220, 0.12, 'sawtooth', 0.25, 0.4); },
    // Les techniques d'arts martiaux (`techniques.js`) : le pied qui fend l'air, le
    // corps projete qui tombe, l'etranglement.
    pied: function () { if (!joue('pied')) { bruit(0.12, 0.25, 1800, 400); ton(120, 0.06, 'square', 0.2, 0.5, 0.08); } },
    chute: function () { if (!joue('chute')) { ton(90, 0.18, 'sine', 0.35, 0.4); bruit(0.14, 0.3, 500, 120); } },
    etranglement: function () { if (!joue('etranglement')) bruit(0.4, 0.08, 400, 200); },
    // La cloche du tramway : deux coups clairs. Un DE SES effets (voir `Son.depuis`).
    cloche_tram: function () { if (!joue('cloche_tram')) { ton(1320, 0.3, 'triangle', 0.16, 1); ton(1320, 0.3, 'triangle', 0.16, 1, 0.32); } },
    ramasse: function () { if (!joue('ramasse')) { ton(880, 0.08, 'sine', 0.25); ton(1320, 0.12, 'sine', 0.2, 1, 0.07); } },
    //: LE MAILLET du marteau de force : un coup MAT sur un plateau de bois, pas
    //: un coup de poing. ⚠️ Synthetise, et ce n'est pas une economie de bouts de
    //: chandelle : le seau des bruitages porte deja 190 fichiers, et un coup sec
    //: est exactement ce qu'un oscillateur fait le mieux.
    //: ⚠️ 22 sept. 2026 : il emprunte le coup de BATON (`batte`, un « thwack »
    //: de bois creux), deja paye — la meme matiere qu'un maillet sur un plateau
    //: de bois, sans un octet de plus au seau. La synthese reste le filet.
    maillet: function () { if (!joue('batte')) { ton(190, 0.07, 'square', 0.26, 0.4); bruit(0.07, 0.22, 700, 180); } },
    //: LA CLOCHE, en haut de la colonne : UN coup, clair et qui traine. C'est le
    //: seul son du jeu qui dise « tu as gagne » avant que le HUD l'ecrive — deux
    //: coups en feraient un tramway (`cloche_tram`), qui, lui, passe.
    cloche: function () {
      ton(1760, 0.9, 'sine', 0.22, 1.6);
      ton(2640, 0.6, 'triangle', 0.09, 1.9, 0.01);
      ton(880, 1.1, 'sine', 0.10, 1.3, 0.02);
    },
    argent: function () { if (!joue('argent')) { ton(1500, 0.06, 'sine', 0.2); ton(2000, 0.1, 'sine', 0.18, 1, 0.06); } },
    menu: function () { if (!joue('menu')) ton(660, 0.05, 'square', 0.15); },
    // ⚠️ Le filet du refus suit la meme regle que l'echantillon (voir
    // `audio.py`) : deux petites notes qui descendent, pas un buzzer. La
    // dent de scie a 160 Hz d'avant grognait — pour dire qu'il ne se passe
    // rien, c'est beaucoup trop.
    erreur: function () { if (!joue('erreur')) { ton(330, 0.07, 'triangle', 0.12); ton(247, 0.11, 'triangle', 0.1, 1, 0.06); } },
    etoile: function () { if (!joue('etoile')) { ton(523, 0.15, 'square', 0.2); ton(784, 0.2, 'square', 0.2, 1, 0.12); } },
    sirene: function () { if (!joue('sirene')) ton(700, 0.4, 'square', 0.15, 1.4); },
    //: L'alarme d'un commerce braque : deux tons qui alternent, trois fois. Synthetisee, comme le
    //: bip de recul : un ton electronique a trous ne se genere pas (le modele ne fait pas de silence).
    alarme_commerce: function () { for (let k = 0; k < 6; k++) ton(k % 2 ? 660 : 880, 0.17, 'square', 0.09, 1, k * 0.2); },
    klaxon: function () { if (!joue('klaxon')) { ton(330, 0.25, 'sawtooth', 0.3); ton(415, 0.25, 'sawtooth', 0.3); } },
    choc: function () { if (!joue('choc')) bruit(0.4, 0.5, 1200, 100); },
    explosion: function () { if (!joue('explosion')) { bruit(0.9, 0.8, 600, 40); ton(60, 0.6, 'sine', 0.5, 0.5); } },
    // --- L'eau ---------------------------------------------------------------
    // ⚠️ Jusqu'ici, entrer dans l'eau jouait `choc` — la TOLE FROISSEE d'un
    // accident de char — et nager ne jouait rien du tout : les pas sont coupes
    // dans l'eau, et rien ne les remplacait. Trois sons pour les trois moments
    // que l'eau produit deja : on entre, on avance, on coule.
    plongeon: function () { if (!joue('plongeon')) { bruit(0.45, 0.5, 2500, 250); ton(300, 0.22, 'sine', 0.14, 0.25); bruit(0.16, 0.14, 9000, 4000); } },
    // La brassee : elle part a la DISTANCE parcourue, comme un pas.
    nage: function () { if (!joue('nage')) bruit(0.2, 0.14, 1300, 350); },
    //: La borne qui saute : le BOUCHON qui part, la tole qui cede, et l'eau
    //: qui s'ouvre d'un coup. Une seule fois, a l'instant du bris.
    //:
    //: ⚠️ **PAS LE `choc` D'UN ACCIDENT DE CHAR** (retour de Martin, 15 sept.
    //: 2026 : « le son des bornes-fontaines brisées n'est pas correct »). Elle
    //: jouait `SFX.choc()` — la tole froissee d'une collision — au bris ET
    //: toutes les 24 images pendant les dix secondes du jet : **dix-sept
    //: accidents de char pour une borne defoncee**. Et le premier etait un
    //: doublon, parce que le char qui la renverse joue deja `choc` a la meme
    //: image (`Vehicules.heurterDecor`). Le bruit de l'impact appartient a ce
    //: qui a defonce ; la borne, elle, n'a que son bouchon et son eau.
    //:
    //: ⚠️ Elle n'a pas son propre echantillon, et c'est un choix de budget :
    //: le seau des bruitages est a 14 Ko de son plafond (voir le plan). Ces
    //: deux-la sont donc ENTIEREMENT synthetises — et ils ne reclament rien au
    //: catalogue : le navigateur ne demande un echantillon que pour un slug
    //: que Python declare, et un juge le tient. Le jour d'une seance
    //: ElevenLabs, la fiche gagnera ses deux entrees et ces fonctions leur
    //: repli, ensemble.
    borne_cassee: function () {
      ton(760, 0.05, 'square', 0.14, 2.6);        // le bouchon qui saute
      bruit(0.12, 0.28, 5200, 1400);              // la tole qui cede
      bruit(0.55, 0.40, 2400, 800);               // l'eau qui s'ouvre d'un coup
    },
    /** Le jet, TENU tant que la gerbe vit : un souffle large et continu dont
        le volume suit la distance (`force`, 0 = on se tait).

        ⚠️ **Un jet est un son CONTINU, pas un son rejoue.** C'est le meme
        patron que `jet()` pour l'extincteur : appele A CHAQUE IMAGE avec la
        verite du moment — plus de gerbe, trop loin, dans une piece : toutes
        les raisons de se taire passent par la. Faute d'echantillon, la
        continuite se fait par recouvrement : un souffle de 0,2 s toutes les
        0,1 s, donc jamais de trou. */
    borne_jet: function (force) {
      const f = Math.max(0, Math.min(1, force || 0));
      if (f > 0 && B.t % 6 === 0) bruit(0.2, 0.1 * f, 2000, 700);
    },
    /** Un son de CHANTIER pose en (x, y) : l'echantillon s'il est charge, son
        filet sinon — au meme volume, qui dit la distance. Rend ce volume (0 =
        trop loin, rien n'est parti). C'est `chantiers.js` qui decide QUAND :
        au geste qu'on voit, sur son horloge, et jamais la nuit. */
    chantier: function (slug, x, y, portee) {
      const j = B.joueur;
      if (!j || !pret()) return 0;
      const p = portee || 320;
      const v = 1 - Math.hypot(x - j.x, y - j.y) / p;
      if (v <= 0) return 0;
      if (estCharge(slug)) return jouerA(slug, x, y, p);
      (REPLI_CHANTIER[slug] || REPLI_CHANTIER.marteau)(v);
      return v;
    },
    /** La rumeur du chantier le plus proche, TENUE a chaque image comme le jet
        d'une borne : `volume` 0 = on se tait. Faute de fichier, un grondement
        sourd toutes les quinze images, qui se recouvre. */
    /** La corne du traversier, posee en (x, y) : l'echantillon s'il est charge, sinon
        deux longs coups graves. Rend le volume (0 = trop loin).
        ⚠️ SANS position, elle sonne ou l'on est : c'est l'avertisseur des grands
        bateaux (`klaxon: 'corne'` de leur fiche), et `Vehicules.avertir` appelle
        un avertisseur sans rien lui donner, comme le klaxon et la sonnette. */
    corne: function (x, y, portee) {
      const j = B.joueur;
      if (!j || !pret()) return 0;
      if (x === undefined || y === undefined) { x = j.x; y = j.y; }
      const p = portee || 900;
      const v = 1 - Math.hypot(x - j.x, y - j.y) / p;
      if (v <= 0) return 0;
      if (estCharge('corne')) return jouerA('corne', x, y, p);
      for (let k = 0; k < 2; k++) { ton(98, 1.1, 'sawtooth', 0.09 * v, 1, k * 1.5); ton(147, 1.1, 'square', 0.03 * v, 1, k * 1.5); }
      return v;
    },
    rumeur_chantier: function (volume) {
      const v = Math.max(0, Math.min(1, volume || 0));
      if (!estCharge('chantier')) {
        if (v > 0.02 && B.t % 15 === 0) bruit(0.35, 0.05 * v, 260, 90);
        return;
      }
      if (v <= 0.02) { boucle('chantier', false); return; }
      if (!boucleActive('chantier')) boucle('chantier', true, v);
      reglerBoucle('chantier', v);
    },
    /** LES CRIS DE LA FOIRE, tenus comme la rumeur d'un chantier : `volume` 0
        = on se tait. ⚠️ Faute de fichier, ce n'est PAS du bruit blanc — une
        foire, ce sont des voix : deux cris courts et aigus de temps en temps,
        a des hauteurs qui ne se repetent pas. Un souffle continu sonnerait
        comme le vent, et la foire aurait l'air vide. */
    rumeur_foire: function (volume) {
      const v = Math.max(0, Math.min(1, volume || 0));
      if (!estCharge('foire_cris')) {
        if (v > 0.02 && B.t % 47 === 0) {
          const h = 620 + (B.t % 7) * 90;
          ton(h, 0.22, 'triangle', 0.035 * v, 1.25, 0);
          ton(h * 1.5, 0.16, 'sine', 0.02 * v, 1.4, 0.12);
        }
        return;
      }
      if (v <= 0.02) { boucle('foire_cris', false); return; }
      if (!boucleActive('foire_cris')) boucle('foire_cris', true, v);
      reglerBoucle('foire_cris', v);
    },
    /** LES VAGUES, dosees a la distance de l'eau (`Monde.majSonDuBord`).
        ⚠️ Le repli est un SOUFFLE QUI RESPIRE, pas un bruit plat : une vague
        monte et redescend, et c'est ce va-et-vient qu'on reconnait les yeux
        fermes. Un bruit blanc constant, c'est une radio mal accordee. */
    vagues: function (volume) {
      const v = Math.max(0, Math.min(1, volume || 0));
      if (!estCharge('vagues')) {
        if (v > 0.02 && B.t % 90 === 0) bruit(1.6, 0.05 * v, 700, 240);
        return;
      }
      if (v <= 0.02) { boucle('vagues', false); return; }
      if (!boucleActive('vagues')) boucle('vagues', true, v);
      reglerBoucle('vagues', v);
    },
    //: Le nid-de-poule : le COUP SEC de la suspension qui talonne, puis la
    //: tole qui resonne une demi-seconde. Synthetise, comme la borne : le seau
    //: des bruitages est plein, et un cahot n'a pas besoin d'un fichier.
    nid_de_poule: function () {
      ton(90, 0.07, 'square', 0.22, 0.45);          // le talonnage
      bruit(0.1, 0.16, 1100, 300);                  // le gravier
      ton(320, 0.14, 'triangle', 0.07, 0.7, 0.04);  // la tole qui resonne
    },
    //: La machine distributrice. ⚠️ Synthetisee, comme la borne et le nid-de-
    //: poule, pour la meme raison : le seau des bruitages est plein, et trois
    //: coups de tole n'ont pas besoin de trois fichiers.
    //: Ce qu'on achete TOMBE : le moteur de la spirale, puis la canette qui
    //: dégringole dans la trappe.
    distributrice: function () {
      ton(180, 0.16, 'sawtooth', 0.05, 0.9);          // la spirale qui tourne
      ton(140, 0.06, 'square', 0.18, 0.5, 0.18);      // le coup sourd dans la trappe
      bruit(0.08, 0.14, 1800, 500);
    },
    // On la BRASSE : l'epaule dans la tole, et tout ce qu'il y a dedans qui cogne.
    machine_brassee: function () {
      ton(70, 0.12, 'square', 0.24, 0.6);
      bruit(0.18, 0.22, 900, 200);
      ton(240, 0.1, 'triangle', 0.06, 0.8, 0.08);
    },
    // Defoncee : la monnaie qui s'eparpille, trois tintements qui descendent.
    monnaie: function () {
      for (let i = 0; i < 3; i++) ton(2200 - i * 260, 0.08, 'sine', 0.12, 0.9, i * 0.07);
      bruit(0.2, 0.18, 3200, 900);
    },
    // La tete qui passe dessous : le glouglou, puis les bulles qui remontent.
    couler: function () { if (!joue('couler')) { bruit(0.7, 0.35, 800, 60); for (let i = 0; i < 4; i++) ton(520 - i * 90, 0.1, 'sine', 0.12, 0.45, i * 0.12); } },
    // ⚠️ Le char n'a PAS son propre fichier, et c'est voulu : c'est la meme
    // eau, avec plus de masse. Le plongeon plus un coup de grave — ce qui
    // manque a un corps de 80 kg, c'est le poids, pas la matiere.
    char_a_l_eau: function () { if (!joue('plongeon')) bruit(0.6, 0.6, 2200, 200); ton(55, 0.5, 'sine', 0.3, 0.5); },
    // ⚠️ Trois portes : le bois et la serrure d'un logement, la vitre et la
    // porte d'un commerce, la portiere d'un char. Le jeu appelle
    // `porte(genre)` ; le genre vient de la fiche — de la piece (`carte._piece`,
    // champ `porte`) ou du char (`vehicules.py`, `portieres`).
    porte_maison: function () { if (!joue('porte_maison')) { ton(160, 0.14, 'triangle', 0.22, 0.6); bruit(0.06, 0.12, 400, 150); } },
    porte_commerce: function () { if (!joue('porte_commerce')) { bruit(0.03, 0.08, 3000, 2000); ton(2300, 0.18, 'sine', 0.12, 1, 0.03); ton(3100, 0.25, 'sine', 0.09, 1, 0.1); } },
    porte_vehicule: function () { if (!joue('porte_vehicule')) { bruit(0.05, 0.3, 1500, 200); ton(95, 0.09, 'square', 0.14, 0.5, 0.01); } },
    porte: function (genre) { (SFX['porte_' + genre] || SFX.porte_maison)(); },
    // Le petit train de la foire, arrete devant quelqu'un : deux coups de
    // sifflet aigus, un court et un long. ⚠️ Synthetise seulement, comme la
    // distributrice : le son de la foire (orgue, cris, sifflet) est une piste
    // ElevenLabs a part dans le plan, et un `joue` sans fichier au catalogue
    // reclamerait un mp3 qui n'existe pas.
    sifflet_train: function () { ton(1320, 0.12, 'triangle', 0.16); ton(1175, 0.32, 'triangle', 0.16, 1, 0.16); },
    // Le rideau du garage qui monte ou descend : un roulement grave et les lames
    // qui claquent une a une. ⚠️ Synthetise seulement, pour la meme raison que le
    // sifflet : un `joue` sans fichier au catalogue reclamerait un mp3 absent.
    rideau_garage: function () {
      bruit(0.5, 0.12, 700, 180);
      for (let i = 0; i < 6; i++) ton(150 + (i % 2) * 35, 0.04, 'square', 0.05, 0.8, i * 0.08);
    },
    // La barriere coulissante du poste : le moteur qui ronronne et les roulettes
    // sur le rail, puis le claquement du panneau en butee. ⚠️ Synthetise seulement,
    // comme le rideau : pas de fichier au catalogue.
    barriere_coulissante: function () {
      bruit(0.8, 0.07, 420, 120);
      ton(88, 0.8, 'sawtooth', 0.035, 0.9);
      ton(1900, 0.05, 'square', 0.05, 0.5, 0.82);
      ton(140, 0.08, 'square', 0.07, 0.6, 0.82);
    },
    // Le pistolet de la carrosserie, derriere le rideau baisse : UNE passe, un souffle
    // aigu qui siffle et le compresseur qui cogne dessous — l'atelier en fait trois
    // (`Missions.majGarage`). ⚠️ Synthetise seulement, comme le rideau : pas de
    // fichier au catalogue.
    //: ⚠️ 22 sept. 2026 : la passe emprunte le souffle de l'EXTINCTEUR, deja
    //: paye (un jet de poudre sous pression), coupe a 0,4 s et a moitie
    //: volume — c'est derriere un rideau baisse. La synthese reste le filet.
    pistolet_peinture: function () {
      if (bref('extincteur', 0.4, 0.5)) return;
      bruit(0.4, 0.09, 5200, 3400);
      ton(62, 0.12, 'square', 0.04, 0.6);
    },
    /** Un decor qui CEDE (`Entites.briser`), par sa matiere : voir
        `MATIERE_DU_BRIS`. Une seule fois par image : l'explosion d'un char
        couche six decors d'un coup, et six fois le meme fichier au meme
        instant ne sonnent pas plus fort, ils saturent. Rend le slug joue. */
    bris: function (decor) {
      const slug = MATIERE_DU_BRIS[decor];
      if (!slug || dernierBris === B.t) return null;
      dernierBris = B.t;
      // ⚠️ Chaque `joue` nomme son fichier en toutes lettres : c'est ce que
      // `test_audio.py` lit pour tenir le catalogue et le filet.
      if (slug === 'pelle') { if (!joue('pelle')) bruit(0.2, 0.3, 2600, 400); }
      else if (slug === 'bouteille') { if (!joue('bouteille')) bruit(0.2, 0.3, 3000, 400); }
      else if (!joue('casse')) bruit(0.2, 0.3, 3000, 400);
      return slug;
    },
    // ⚠️ La sonnette est l'AVERTISSEUR du velo (`vehicules.py`, `klaxon`) : au
    // meme bouton que le klaxon d'une auto. Les velos du trafic la font deja
    // entendre en passant (`jouerA`) ; ici c'est la sienne.
    sonnette: function () { if (!joue('sonnette')) { ton(2600, 0.1, 'sine', 0.16); ton(2600, 0.14, 'sine', 0.12, 1, 0.13); } },
    // Un deux-roues s'enfourche : la bequille et le cadre, pas une portiere.
    enfourcher: function () { if (!joue('enfourcher')) { bruit(0.05, 0.15, 1800, 300); ton(700, 0.05, 'square', 0.08, 0.6, 0.03); } },
    // ⚠️ **ELLE REND SA DUREE**, en secondes — le seul SFX qui rende quelque
    // chose. Le dialogue de l'appel attend la fin de la sonnerie
    // (`Histoire.majTelephone`) : sans ce nombre, il faudrait l'ecrire une
    // deuxieme fois dans `histoire.js`, et les deux divergeraient le jour ou
    // la sonnerie change. Le fichier dure ce que le catalogue declare
    // (`audio.py`, `duree_s` : la finition le coupe la) ; sans fichier, la
    // synthese fait ses trois coups en 0,37 s (le dernier part a 0,29 et dure
    // 0,08).
    telephone: function () {
      if (!joue('telephone')) { for (let i = 0; i < 3; i++) { ton(1200, 0.08, 'square', 0.15, 1, i * 0.12); ton(1600, 0.08, 'square', 0.15, 1, i * 0.12 + 0.05); } return SONNERIE_SYNTHESE; }
      const def = defEchantillon('telephone');
      return (def && def.duree_s) || SONNERIE_SYNTHESE;
    },
    helico: function () { if (!joue('helico')) bruit(0.3, 0.2, 200, 80); },
    // --- Les armes : un son par arme (`armes.py`, champ `son`) ----------------
    // ⚠️ `arme(def)` est le seul point d'entree du combat : il lit `def.son` et
    // retombe sur le coup de poing quand l'arme n'en declare pas. Le geste et
    // l'impact sont dans le meme son, comme pour `coup` : il part au debut de
    // la phase active, avant de savoir si le coup touche.
    // Le poing americain : le coup de poing, et le metal qui cogne l'os dessous.
    poing_americain: function () { if (!joue('poing_americain')) { ton(140, 0.08, 'square', 0.3, 0.5); bruit(0.08, 0.3, 800, 200); ton(1700, 0.06, 'triangle', 0.12, 0.8, 0.01); } },
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
    //: LA CARABINE À BOUCHON de la galerie de tir : un « pop » mat de liège.
    //: Synthétisé, comme le sifflet du petit train : le son de la foire est une
    //: piste à part, et un `joue` sans mp3 réclamerait un fichier absent.
    carabine_foire: function () { if (!joue('carabine_foire')) { ton(240, 0.05, 'sine', 0.3, 2.2); bruit(0.06, 0.18, 1400, 500); } },
    molotov: function () { if (!joue('molotov')) { bruit(0.1, 0.4, 7000, 2500); bruit(0.5, 0.5, 900, 150); ton(55, 0.4, 'sine', 0.3, 0.6, 0.08); } },
    // Un souffle de poudre, seul ; le jet en continu, c'est `jet()` qui le tient.
    extincteur: function () { if (!joue('extincteur')) bruit(0.25, 0.18, 5000, 2500); },
    // L'eau sur la braise : un sifflement court, quand le feu s'éteint. ⚠️
    // Synthétisé, comme la borne : le seau des bruitages est plein, et ce
    // « tss » ne réclame pas un fichier.
    eau: function () { bruit(0.4, 0.22, 3200, 900); },
    // Le feu de bâtiment, tenu tant qu'on en est près : un crépitement sourd,
    // dosé à la distance (`force`, 0 = on se tait). ⚠️ Sans fichier au
    // catalogue — comme la rumeur d'un chantier quand son mp3 manque.
    rumeur_incendie: function (force) {
      const v = Math.max(0, Math.min(1, force || 0));
      if (v > 0.02 && B.t % 13 === 0) {
        bruit(0.16, 0.06 * v, 900, 220);
        if (v > 0.4 && B.t % 37 === 0) ton(380, 0.05, 'square', 0.03 * v, 1.6);
      }
    },
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
    // --- La prime d'une mission : le son dit sa taille (`economie.PRIME_PALIERS`) ---
    // ⚠️ `prime(palier)` est le seul point d'entree : `Missions.annoncerPrime`
    // l'appelle avec le palier deja tranche. SYNTHESE SEULE pour l'instant :
    // les mp3 attendent le quota (`audio.EN_ATTENTE`, qui dit comment les
    // brancher — un `joue` devant chaque ligne, comme les autres). La gradation
    // est la meme des deux cotes : la caisse, puis des pieces de plus en plus
    // nombreuses, puis la fanfare. La pluie de pieces dure ce que dure le
    // compteur du bandeau (`Hud.prime`) : on entend l'argent tomber pendant
    // qu'on le voit monter.
    prime_petite: function () { caisse(0); pieces(3, 0.25, 0.12); },
    prime_moyenne: function () { caisse(0); pieces(8, 0.6, 0.1); ton(784, 0.1, 'square', 0.12, 1, 0.5); ton(1047, 0.22, 'square', 0.14, 1, 0.6); },
    prime_grosse: function () { arpege(0, 0.09, 0.16); caisse(0.36); pieces(14, 1.1, 0.4); ton(1047, 0.45, 'triangle', 0.18, 1, 1.2); ton(1319, 0.45, 'triangle', 0.14, 1, 1.2); },
    prime_gros_lot: function () { arpege(0, 0.1, 0.2); arpege(0.4, 0.1, 0.2); caisse(0.8); caisse(1.3); pieces(28, 1.8, 0.8); [1047, 1319, 1568, 2093].forEach(function (f) { ton(f, 0.9, 'triangle', 0.14, 1, 2.2); }); },
    prime: function (palier) { (SFX['prime_' + palier] || SFX.prime_petite)(); },
  };

  // --- Les voix des passants : un mot quand on se frole ------------------------------

  /** Une BANDE de frequences : un passe-haut puis un passe-bas, plat entre les
      deux. Le combine du telephone (300 Hz - 3,4 kHz, voir `Voix.parler`), le
      scanner de la police, le haut-parleur d'un autoradio. `renfort` compense
      ce que la coupe retire : une voix sans ses graves s'entend moins fort a
      puissance egale. Rend le dernier noeud, a brancher sur la sortie. */
  function bande(gain, basHz, hautHz, renfort) {
    const haut = ctx.createBiquadFilter();
    haut.type = 'highpass'; haut.frequency.value = basHz;
    const bas = ctx.createBiquadFilter();
    bas.type = 'lowpass'; bas.frequency.value = hautHz;
    gain.gain.value *= renfort || 1;
    gain.connect(haut); haut.connect(bas);
    return bas;
  }

  const Voix = {
    dernierT: -9999, chargees: false,
    //: Les contextes dont les repliques sont deja demandees. ⚠️ Un `Set`, pas un
    //: drapeau : elles arrivent UN CONTEXTE A LA FOIS, et un contexte ne se
    //: redemande pas a chaque rencontre.
    contextesCharges: new Set(),
    liste: function () { return (B.defs && B.defs.audio && B.defs.audio.voix) || []; },
    reglages: function () { return (B.defs && B.defs.audio && B.defs.audio.parole) || {}; },
    depart: function () { return Voix.reglages().contexte_de_depart || 'normal'; },

    /** Demande ces repliques-la au reseau. Une qui n'a pas de fichier n'est pas un
        manque : `audio.exporter()` ne declare que ce qui existe, et le texte se
        montre quand meme. */
    _charger: function (liste) {
      liste.forEach(function (v) {
        if (!v.fichier) return;
        decoder(base + B.defs.audio.dossier + '/' + v.fichier)
          .then(function (tampon) { tampons.set('voix-' + v.slug, [tampon]); })
          .catch(function () { /* muet, tant pis */ });
      });
    },

    /** Les repliques se chargent avec les bruitages : petites, et il en faut
        une sous la main des la premiere rencontre.

        ⚠️ **SAUF CELLES D'UN CONTEXTE** (M15, 2e vague) : vingt-quatre repliques de
        plus, c'est 960 Ko au premier ecran, sur un budget de demarrage qui avait
        160 Ko de marge (mesure du 24 sept. 2026). Elles arrivent quand leur monde
        arrive — voir `chargerContexte`. Ce qui n'a pas de `quand` (le crieur, la
        fille de la Brume, les ondes) part avec le reste : ces banques-la ne
        dependent d'aucun contexte. */
    charger: function () {
      if (Voix.chargees || !ctx || !fenetre || !fenetre.fetch) return;
      Voix.chargees = true;
      const depart = Voix.depart();
      Voix.contextesCharges.add(depart);
      Voix._charger(Voix.liste().filter(function (v) { return !v.quand || v.quand === depart; }));
    },

    /** Les repliques d'UN contexte, la premiere fois qu'on y entre — exactement
        comme `Quartier.charger` prend un district en y entrant, ou comme une piece
        de musique arrive a la porte du commerce. */
    chargerContexte: function (quand) {
      if (!quand || Voix.contextesCharges.has(quand) || !ctx || !fenetre || !fenetre.fetch) return;
      Voix.contextesCharges.add(quand);
      Voix._charger(Voix.liste().filter(function (v) { return v.quand === quand; }));
    },

    /** DANS QUEL MONDE la ville te parle — le `quand` d'une replique
        (`audio.VOIX`) : la premiere regle de `parole.contextes`
        qui passe, de la plus pressante a la plus banale. Meme forme que la
        manchette du Clairon (`journal.REGLES`), parce que c'est la meme question —
        et l'ordre est en Python, pas ici.

        ⚠️ **NI LA PEUR NI LA NUIT NE SE REDEFINISSENT ICI.** La peur est celle qui
        fait deja taire la rumeur (`Rumeur.peurT`, `Rumeur.criT`) ; la nuit est
        celle du ciel (`Monde.estNuit`). Deux definitions de la nuit, et le jour ou
        l'une des deux bouge, huit repliques ne sortent plus jamais — une panne qui
        ne se voit pas.

        ⚠️ Un contexte que le Python nomme et que ce tableau-ci ne connait pas ne
        se joue JAMAIS : ce sont huit clips morts, et un juge tient les deux
        ensemble (`test_parole.py`).

        ⚠️ Elle s'appelle `quand` et pas `contexte` : dans ce fichier-ci, `contexte`
        est deja l'AudioContext (`Son.contexte`). Deux sens pour un mot dans le meme
        module, et on finit par lire le mauvais. */
    quand: function () {
      const p = B.partie;
      const passe = {
        peur: function () { return B.t < Rumeur.peurT || B.t < Rumeur.criT; },
        celebre: function (c) { return !!p && ((p.stats && p.stats.missions) || 0) >= c.missions_min; },
        nuit: function () { return Monde.estNuit(); },
      };
      const contextes = Voix.reglages().contextes || [];
      for (const c of contextes) {
        const regle = passe[c.quand];
        if (regle && regle(c)) return c.quand;
      }
      return Voix.depart();
    },

    /** LA BANQUE OU L'ON TIRE : un genre ET un contexte, plus seulement un genre.

        ⚠️ Une banque vide **se rabat sur le contexte de depart** plutot que de
        laisser le passant muet : un mp3 pas encore genere ne doit pas faire taire
        la rue. C'est la meme regle qu'`audio.exporter()`, du cote du joueur.

        ⚠️ Et un genre SANS contexte (le crieur, la fille de la Brume) tire dans
        tout ce qu'il a : un homme-sandwich crie son special pareil a trois heures
        du matin, c'est son metier. ⚠️ Il n'a PAS besoin de sa ligne a lui : le
        dernier filet (`: liste`) le couvre deja, puisque ni sa banque ni celle du
        depart ne rendent rien. Un `if (!liste.some(v => v.quand)) return liste;`
        ecrit en tete ne rougissait AUCUNE mutation — on l'a retire. */
    banque: function (liste, quand) {
      const ici = liste.filter(function (v) { return v.quand === quand; });
      if (ici.length) return ici;
      const filet = liste.filter(function (v) { return v.quand === Voix.depart(); });
      return filet.length ? filet : liste;
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
        decoder(base + B.defs.audio.dossier + '/' + v.fichier)
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
      // ⚠️ La mission passe AVANT les ondes : l'animateur ou le scanner se taisent.
      Ondes.couper();
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
        sortie = bande(gain, 300, 3400, 2);
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

    /** Le ducking : la musique se retire pendant qu'on parle — GRADUELLEMENT, voir
        « Le ducking ». ⚠️ Cet appel ne baisse rien : il donne la CIBLE, et `Duck`
        glisse. Tout ce qui joue est concerne — les boucles (radio, ambiance,
        `musique-`), le sequenceur (`Mus.attenuation`) et le musicien de rue, qui a
        sa propre sortie : sans lui, sa guitare couvrait la voix au telephone,
        exactement comme la radio du camion le faisait avant elle. */
    baisserLeReste: function (actif) {
      Voix.ducking = !!actif;
      // ⚠️ Quelqu'un parle aussi quand c'est la radio ou la police (`Ondes`) : la
      // fin d'une replique de mission ne remonte pas la musique sous le scanner.
      Duck.viser(Voix.ducking || !!Ondes.enCours);
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
      const mort = Voix.reglages().temps_mort_images || 420;
      if (B.t - Voix.dernierT < mort) return null;
      const quand = Voix.quand();
      // La premiere fois qu'on entre dans ce monde-la, ses repliques se demandent.
      Voix.chargerContexte(quand);
      const tous = Voix.liste().filter(function (v) {
        return v.genre === genre && (!slug || v.slug === slug) && tampons.has('voix-' + v.slug);
      });
      const v = Voix.tirer(Voix.banque(tous, quand));
      if (!v) return null;
      Voix.dernierT = B.t;
      const j = B.joueur;
      echantillon('voix-' + v.slug, { volume: v.volume, pan: j ? (x - j.x) / 200 : 0 });
      return v.slug;
    },
  };

  // --- Sur les ondes : la radio qui parle, et la police ------------------------------
  /*: ⚠️ M15, 2e vague. « L'ame d'une radio, c'est ce qui se dit ENTRE les tounes » :
    douze clips d'animateurs et de pubs etaient generes, declares et telecharges au
    demarrage depuis le 16 sept. 2026 — et AUCUNE ligne du jeu ne les jouait. Et la
    police, qu'on voyait partout, ne s'entendait nulle part.

    ⚠️ UNE bande pour les deux : l'animateur et le scanner ne se marchent pas
    dessus, la police passe devant l'animateur, et une replique de MISSION passe
    devant tout le monde (`Voix.parler` coupe les ondes ; les ondes attendent
    qu'elle finisse). Ce qui passe baisse la musique comme une replique.

    ⚠️ A TOUR DE ROLE, JAMAIS `B.rng()` : ce sont des bruits de fond qui tournent
    toute la partie, et un de de plus decalerait tout le hasard du jeu
    (`docs/ecrire-drole.md`, regle 8). Chaque liste se lit dans l'ordre.

    `dites` garde ce qui est passe, fichier ou pas : le banc n'a pas d'oreille. */
  const Ondes = {
    enCours: null,           // { source, slug, radio } : ce qui passe en ce moment
    dites: [],               // { slug, t, bande } — ce qui est passe, dans l'ordre
    tours: {},               // cle -> combien de fois on a pioche dans cette liste
    station: null,           // la station dont on compte les tounes
    prochaineT: 0,           // quand l'animateur reprend la parole
    n: 0,                    // combien de fois il l'a prise sur cette station
    policeT: -99999,         // le dernier message de la police
    derniers: {},            // evenement -> quand il a ete dit
    bulletins: {},           // slug de manchette -> quand la radio l'a lue

    reglages: function () { return (B.defs && B.defs.audio && B.defs.audio.ondes) || {}; },

    /** Le suivant d'une liste, a tour de role : on n'entend deux fois la meme
        replique qu'apres les avoir toutes entendues. */
    aTourDeRole: function (cle, liste) {
      if (!liste.length) return null;
      const n = Ondes.tours[cle] || 0;
      Ondes.tours[cle] = n + 1;
      return liste[n % liste.length];
    },

    /** La pub suivante. ⚠️ Celle d'un commerce qu'on POSSEDE est sa jumelle « a
        toi » : entendre son propre bar annonce a la radio, dans un char qu'on
        vient de voler, c'est exactement ce que M15 promet. */
    pub: function () {
      const pubs = Voix.liste().filter(function (v) { return v.genre === 'pub'; });
      const v = Ondes.aTourDeRole('pub', pubs.filter(function (p) { return !p.a_toi; }));
      const a = B.partie && B.partie.proprietes;
      if (!v || !v.propriete || !(a && a[v.propriete])) return v;
      return pubs.find(function (p) { return p.a_toi && p.propriete === v.propriete; }) || v;
    },

    /** LE BULLETIN DE NOUVELLES : la manchette du jour — celle que le Clairon a lue
        au lever — passee par le haut-parleur de l'autoradio. La radio parle donc de
        CE QUE TU AS FAIT HIER, dans un char que tu viens de voler, et c'est le seul
        moment de la station qui ne soit pas le meme pour tout le monde.

        ⚠️ **IL NE COUTE PAS UN CLIP** : il rejoue la voix que le narrateur a deja
        pour cette manchette-la (`histoire-narrateur-journal-<slug>`), celle du
        matin. Dans une ville de cette taille, le vieux qui lit le journal lit aussi
        les nouvelles de huit heures.

        ⚠️ **UNE LECON N'EST PAS UNE NOUVELLE.** Le repli du Clairon enseigne
        (« Le saviez-vous? Un coup de klaxon dans un taxi vous trouve un client »).
        A la radio, ce ne serait pas un bulletin, ce serait un mode d'emploi : la
        station joue sa musique a la place.

        ⚠️ **ET JAMAIS DEUX FOIS EN DIX MINUTES.** La manchette ne change qu'au lever
        du jour : sans repos, la station redirait la meme nouvelle toutes les quatre
        minutes — la faute du scanner de police, au meme endroit. Le repos se pose
        ICI, a la question : demander le bulletin, c'est le prendre, comme
        `aTourDeRole` avance son compteur quand on l'interroge. */
    bulletin: function () {
      const r = Ondes.reglages();
      const m = B.partie && B.partie.derniereManchette;
      if (!m || !m.slug) return null;
      const lecons = (B.defs && B.defs.journal_lecons) || [];
      if (lecons.some(function (l) { return l.slug === m.slug; })) return null;
      const lue = Ondes.bulletins[m.slug];
      if (lue !== undefined && B.t - lue < (r.bulletin_repos_s || 600) * 60) return null;
      // ⚠️ La voix du narrateur se charge PAR MISSION, et « journal » est la sienne :
      // une partie reprise a bien sa manchette, mais pas encore la voix qui la lit.
      // L'appel est idempotent.
      Voix.chargerHistoire('journal');
      Ondes.bulletins[m.slug] = B.t;
      return { slug: 'narrateur-journal-' + m.slug, banque: 'histoire',
               volume: r.bulletin_volume || 0.72 };
    },

    /** Une image. L'animateur de la station qui joue reprend la parole entre deux
        et trois tounes ; une station sans animateur (le Choc, le camion) se tait. */
    maj: function () {
      const r = Ondes.reglages();
      const station = Radio.demandee;
      if (station !== Ondes.station) {
        // ⚠️ On change de station, ou on l'eteint : l'animateur se tait avec elle.
        if (Ondes.enCours && Ondes.enCours.radio) Ondes.couper();
        Ondes.station = station;
        Ondes.n = 0;
        Ondes.prochaineT = B.t + (r.premiere_s || 20) * 60;
      }
      const genres = station && r.stations ? r.stations[station] : null;
      if (!genres || !genres.length || B.t < Ondes.prochaineT) return;
      if (Voix.enCours || Ondes.enCours) { Ondes.prochaineT = B.t + (r.attente_s || 2) * 60; return; }
      // ⚠️ ON PREND LE PREMIER GENRE QUI A QUELQUE CHOSE A DIRE, a partir de celui
      // dont c'est le tour. Le bulletin n'a rien tant que le jour n'a pas livre sa
      // manchette, ni pendant son repos — et une station ne doit pas se taire deux
      // minutes pour autant. Le compteur avance jusqu'au genre retenu : le tour de
      // role reste un tour de role, et le bulletin muet est simplement sauté.
      let v = null, k = 0;
      for (; k < genres.length; k++) {
        const genre = genres[(Ondes.n + k) % genres.length];
        v = genre === 'pub' ? Ondes.pub()
          : genre === 'bulletin' ? Ondes.bulletin()
          : Ondes.aTourDeRole(genre, Voix.liste().filter(function (x) { return x.genre === genre; }));
        if (v) break;
      }
      Ondes.n += (v ? k : 0) + 1;
      // Entre deux et trois tounes, et pas toujours le meme ecart — sans de.
      const iv = r.intervalle_s || [80, 125];
      Ondes.prochaineT = B.t + (iv[0] + (Ondes.n * 23) % Math.max(1, iv[1] - iv[0])) * 60;
      if (v) Ondes.dire(v, 'radio');
    },

    /** La police parle : `evenement` est l'un de `audio.EVENEMENTS_DE_POLICE`.
        Rend le slug dit, ou null. ⚠️ Jamais par-dessus une replique de mission,
        jamais deux messages colles, et le meme evenement ne se redit pas a
        chaque etoile — sinon le scanner devient une alarme. */
    police: function (evenement) {
      const r = Ondes.reglages();
      if (Voix.enCours) return null;
      if (B.t - Ondes.policeT < (r.police_temps_mort_s || 6) * 60) return null;
      const dernier = Ondes.derniers[evenement];
      if (dernier !== undefined && B.t - dernier < (r.police_repos_s || 30) * 60) return null;
      const v = Ondes.aTourDeRole('police-' + evenement,
        Voix.liste().filter(function (x) { return x.genre === 'police' && x.evenement === evenement; }));
      if (!v) return null;
      Ondes.policeT = B.t;
      Ondes.derniers[evenement] = B.t;
      Ondes.couper();                     // la police passe devant l'animateur
      Ondes.dire(v, 'police');
      return v.slug;
    },

    /** Fait passer `v` sur les ondes. Le scanner est la bande du telephone ;
        l'autoradio, celle d'un petit haut-parleur. ⚠️ `v.banque` dit OU prendre le
        clip : les ondes ont les leurs (`voix-`), le bulletin emprunte celui du
        narrateur (`histoire-`) — c'est ce qui le rend gratuit. */
    dire: function (v, quelle) {
      const banque = v.banque || 'voix';
      Ondes.dites.push({ slug: v.slug, t: B.t, bande: quelle, banque: banque });
      if (Ondes.dites.length > 50) Ondes.dites.shift();
      const liste = tampons.get(banque + '-' + v.slug);
      if (!pret() || !liste || !liste.length) return null;
      const source = ctx.createBufferSource();
      source.buffer = liste[0];
      const gain = ctx.createGain();
      gain.gain.value = v.volume || 0.7;
      source.connect(gain);
      const sortie = ctx.createBiquadFilter
        ? (quelle === 'police' ? bande(gain, 300, 3400, 2) : bande(gain, 150, 6000, 1.2))
        : gain;
      sortie.connect(maitre);
      const enCours = { source: source, gain: gain, slug: v.slug, radio: quelle === 'radio' };
      source.onended = function () {
        if (Ondes.enCours === enCours) { Ondes.enCours = null; Duck.viser(Voix.ducking); }
      };
      Ondes.enCours = enCours;
      Duck.viser(true);
      source.start(ctx.currentTime);
      return enCours;
    },

    couper: function () {
      if (!Ondes.enCours) return;
      try { Ondes.enCours.source.onended = null; Ondes.enCours.source.stop(); } catch (e) { /* deja finie */ }
      Ondes.enCours = null;
      Duck.viser(Voix.ducking);
    },
  };

  // --- Le souffle du joueur ------------------------------------------------------------
  /*: ⚠️ M15, 2e vague. Il sprinte, il s'essouffle, et on n'entendait rien : la barre
    d'endurance ne se lisait qu'en la regardant, alors que le sprint est une
    ressource qu'on depense par bouffees. Une boucle qui suit la DETTE de souffle
    (ce qu'on a depense), et une inspiration quand il repart. Tout vient de
    `audio.souffle` ; `reprises` compte les inspirations (le banc n'a pas d'oreille). */
  const Souffle = {
    volume: 0,          // ce que la boucle joue en ce moment (0..1)
    bas: false,         // descendu sous `bas` : la prochaine remontee s'entend
    reprises: 0,

    maj: function (j) {
      const r = (B.defs && B.defs.audio && B.defs.audio.souffle) || {};
      const max = (B.defs && B.defs.recherche && B.defs.recherche.vitesses.endurance) || 100;
      // Au volant, on ne s'entend pas respirer — et on ne court pas.
      const actif = !!(j && j.vivant !== false && !j.dansVehicule && B.etat === 'jeu');
      const dette = actif ? 1 - Math.max(0, j.endurance) / max : 0;
      const seuil = r.seuil === undefined ? 0.35 : r.seuil;
      const voulu = dette <= seuil ? 0 : Math.min(1, (dette - seuil) / (1 - seuil));
      // ⚠️ Il MONTE vite et REDESCEND doucement : on halete encore un moment apres
      // s'etre arrete. Un souffle qui se coupe net a la seconde ou l'on lache le
      // bouton, c'est une barre de vie qui fait du bruit, pas quelqu'un qui respire.
      Souffle.volume = voulu > Souffle.volume
        ? Math.min(voulu, Souffle.volume + (r.monte_par_image || 0.03))
        : Math.max(voulu, Souffle.volume - (r.descend_par_image || 0.006));
      if (Souffle.volume <= 0.02) {
        if (boucleActive('souffle')) boucle('souffle', false);
      } else {
        if (!boucleActive('souffle')) boucle('souffle', true, Souffle.volume);
        reglerBoucle('souffle', Souffle.volume);
      }
      if (!actif) { Souffle.bas = false; return; }
      if (j.endurance <= (r.bas || 0.2) * max) Souffle.bas = true;
      else if (Souffle.bas && j.endurance >= (r.reprise || 0.6) * max) {
        // ⚠️ LE SOUFFLE REPART : c'est le moment ou l'on peut de nouveau courir,
        // et c'est la seule chose que la barre disait qu'on ne pouvait pas entendre.
        Souffle.bas = false;
        Souffle.reprises++;
        if (!joue('reprise')) bruit(0.5, 0.05, 1600, 500);
      }
    },
  };

  // --- Les bruits de quartier ----------------------------------------------------------
  /*: ⚠️ M15, 2e vague. Pas des nappes — chaque district a deja sa musique — mais des
    EVENEMENTS, rares et au loin : une corne de brume aux Quais, un marteau a La
    Shop, une tondeuse aux Erables. Un quartier s'entend avant de se voir.

    ⚠️ A TOUR DE ROLE, jamais `B.rng()` (comme `Ondes`), et chaque son a ses heures.
    Il vient d'une direction qui TOURNE (l'angle d'or) : jamais deux fois du meme
    cote, et `jouerA` le place a gauche ou a droite. `entendus` garde ce qui a
    joue, fichier ou pas. */
  const Quartier = {
    prochaineT: null,
    n: 0,
    tours: {},
    entendus: [],
    chargees: new Set(),

    /** Charge les bruits d'UN district, une seule fois — comme `Voix.chargerHistoire`
        charge les repliques d'une mission. Rare et propre au quartier : les charger
        tous au demarrage doublerait le budget de bruitages pour rien. */
    charger: function (district) {
      if (Quartier.chargees.has(district) || !ctx || !fenetre || !fenetre.fetch) return;
      Quartier.chargees.add(district);
      const r = (B.defs && B.defs.audio && B.defs.audio.quartiers) || {};
      const dossier = base + B.defs.audio.dossier + '/';
      ((r.sons && r.sons[district]) || []).forEach(function (e) {
        const def = defEchantillon(e.slug);
        (def && def.fichiers || []).forEach(function (nom) {
          decoder(dossier + nom)
            .then(function (tampon) {
              const liste = tampons.get(e.slug) || [];
              liste.push(tampon);
              tampons.set(e.slug, liste);
            })
            .catch(function () { /* ce district restera silencieux, tant pis */ });
        });
      });
    },

    /** `heures` : [debut, fin] sur 24 h ramenees a 0..1 ; peut passer minuit. */
    aSonHeure: function (e, heure) {
      if (!e.heures) return true;
      const d = e.heures[0], f = e.heures[1];
      return d < f ? (heure >= d && heure < f) : (heure >= d || heure < f);
    },

    maj: function () {
      const r = (B.defs && B.defs.audio && B.defs.audio.quartiers) || {};
      const j = B.joueur;
      if (!r.sons || !j) return;
      const iv = r.intervalle_s || [25, 50];
      if (Quartier.prochaineT === null) { Quartier.prochaineT = B.t + iv[0] * 60; return; }
      if (B.t < Quartier.prochaineT) return;
      Quartier.n++;
      // Entre `iv[0]` et `iv[1]` secondes, et pas toujours le meme ecart — sans de.
      Quartier.prochaineT = B.t + (iv[0] + (Quartier.n * 17) % Math.max(1, iv[1] - iv[0])) * 60;
      // Dedans, on n'entend pas la rue : la piece a sa propre musique, ou son silence.
      if (B.interieur) return;
      const zone = Monde.zoneA(j.x, j.y);
      const sons = zone && r.sons[zone.district];
      if (!sons) return;
      Quartier.charger(zone.district);
      const heure = B.partie && B.partie.heure !== undefined ? B.partie.heure : 0.5;
      const possibles = sons.filter(function (e) { return Quartier.aSonHeure(e, heure); });
      if (!possibles.length) return;
      const k = Quartier.tours[zone.district] || 0;
      Quartier.tours[zone.district] = k + 1;
      const e = possibles[k % possibles.length];
      const angle = Quartier.n * 2.39996;
      const d = r.distance_px || 240;
      const x = j.x + Math.cos(angle) * d, y = j.y + Math.sin(angle) * d;
      Quartier.entendus.push({ slug: e.slug, t: B.t, district: zone.district, x: x, y: y });
      if (Quartier.entendus.length > 50) Quartier.entendus.shift();
      jouerA(e.slug, x, y, r.portee_px || 420);
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
      decoder(base + B.defs.audio.dossier + '/' + a.fichier)
        .then(function (tampon) {
          tampons.set('ambiance-' + a.slug, [tampon]);
          Ambiance.chargee = 'prete';
          if (Ambiance.demandee === a.slug) Ambiance._demarrer(a);
        })
        .catch(function () { Ambiance.chargee = null; });
      return true;
    },
    _demarrer: function (a) { boucle('ambiance-' + a.slug, true, a.volume, dureeFondu()); Ambiance.courante = a.slug; },
    arreter: function () {
      if (Ambiance.courante) boucle('ambiance-' + Ambiance.courante, false, undefined, dureeFondu());
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
      // ⚠️ DANS LA FOIRE, PAS DE MUSIQUE DE DISTRICT. L'orgue est la musique du
      // lieu : elle sort de la même bouche que le musicien de rue (`Son.Rue`,
      // une source fixe au milieu de l'allée), PAR-DESSUS l'ambiance. Laisser
      // jouer l'ambiance de La Pointe dessous, ce serait deux musiques à la
      // fois — le bois et la foire — alors que la foire a SON monde à elle.
      // Comme c'est une décision de lieu, pas d'état, la poursuite et la
      // bagarre (qui se décident plus haut) continuent de couvrir : se cacher
      // sous un comptoir ne rend pas la ville muette à la police.
      if (Monde.dansLaFoire(Math.floor(j.x / TT), Math.floor(j.y / TT))) return null;
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
      // ⚠️ LE JUKEBOX (débug) TIENT LA MAIN. Tant qu'on a choisi un morceau
      // dans le jukebox, le chef d'orchestre ne replace ni l'ambiance du
      // district, ni la poursuite, ni la bagarre par-dessus : on écoute ce
      // qu'on a demandé. L'arrêt remet `B.jukebox` à null et le chef reprend.
      if (B.jukebox) {
        if (Chef.piste !== B.jukebox) { Chef.piste = B.jukebox; Chef.rang = 99; Mus.jouer(B.jukebox); }
        return;
      }
      if (Chef.queue > 0) Chef.queue--;
      const v = Chef.voulu();
      if (!v) {
        if (Chef.piste) { Mus.arreter(); Chef.piste = null; Chef.rang = 99; }
        return;
      }
      if (v.slug === Chef.piste) return;
      Chef.piste = v.slug; Chef.rang = v.rang;
      Chef.queue = Chef.queue || 0;
      // ⚠️ La musique d'ETAT entre VITE (`fondu_vif_s`) : deux secondes de montee
      // feraient entendre que ca tourne mal apres l'avoir vu. Elle entre quand
      // meme en fondu — c'est la duree qui change, pas la regle.
      Mus.jouer(v.slug, pisteDEtat(v.slug) ? dureeFondu(true) : undefined);
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
    /** Une station de `audio.musiques` plutot qu'un mp3 de `audio.radios`.
        ⚠️ Elle a MAINTENANT un fichier elle aussi (toute la musique est
        generee) : ce qui la distingue n'est donc plus `!fichier` mais d'ou
        elle vient — un morceau porte ses `voix`, une station enregistree
        n'en a pas. C'est `Mus` qui choisit ensuite entre le mp3 et les notes,
        et la radio n'a pas a le savoir. */
    estProcedurale: function (slug) {
      const s = Radio.station(slug);
      return !!(s && s.voix);
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
      // Une station de `musiques` passe par `Mus`, qui sait s'il faut jouer son
      // mp3 ou la reprendre note par note. C'est le meme filet que partout dans
      // `audio.py` : sans fichier, elle demarre tout de suite, meme hors ligne.
      if (Radio.estProcedurale(slug)) { Radio.courante = slug; Mus.jouer(slug); return true; }
      if (!ctx) return true;                               // pas d'audio : on garde l'etat
      if (tampons.has('radio-' + slug)) { Radio._demarrer(slug); return true; }
      if (Radio.chargees.get(slug) === 'en cours') return true;
      Radio.chargees.set(slug, 'en cours');
      decoder(base + B.defs.audio.dossier + '/' + station.fichier)
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
      boucle('radio-' + slug, true, station ? station.volume : 0.4, dureeFondu());
      Radio.courante = slug;
    },

    arreter: function () {
      // ⚠️ On n'arrete le sequenceur QUE s'il jouait une station : au titre il
      // joue le theme du menu, et descendre d'un char ne doit pas l'eteindre.
      if (Radio.courante && Radio.estProcedurale(Radio.courante)) Mus.arreter();
      else if (Radio.courante) boucle('radio-' + Radio.courante, false, undefined, dureeFondu());
      Radio.courante = null;
      Radio.demandee = null;
    },

    /** LA MUSIQUE D'UN COMMERCE. Demande de Martin : « une nouvelle musique
        quand on entre dans les commerces, des chansons differentes,
        contextuelles ».

        ⚠️ **C'EST LE LIEU QUI CHOISIT, PAS LE HASARD** : la carte vit en Python
        (`musique.MUSIQUES_DE_COMMERCE`), le navigateur la LIT. Une piece absente
        de la carte reste silencieuse, et c'est voulu — le poste de police,
        l'hopital et la planque ne sont pas des commerces, et le silence y dit ce
        qu'aucune toune ne dirait.

        ⚠️ Elle passe par `Mus`, donc par la meme porte que tout le reste : **le
        fichier d'abord, les notes en filet**. Un mp3 manquant ne fait pas un
        silence, il fait jouer le sequenceur. */
    dedans: function (slug) {
      const carte = (B.defs && B.defs.audio && B.defs.audio.musiques_de_commerce) || {};
      const morceau = slug ? carte[slug] : null;
      if (!morceau) { Mus.arreter(); return null; }
      Mus.jouer(morceau);
      return morceau;
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

  // --- La musique : le fichier d'abord, les notes en filet --------------------
  //
  /*: ⚠️ Demande de Martin (14 sept. 2026) : « je veux que toutes les musiques
    soient des musiques generees par IA ». Les quinze morceaux de `musique.py`
    — le theme du menu, les deux stations de char, les cinq ambiances de
    district, la poursuite, la bagarre et les cinq pieces du musicien de rue —
    ont chacun leur mp3. Ce qui suit decide, morceau par morceau, si c'est le
    FICHIER ou le SEQUENCEUR qui joue ; `musique.py` annoncait cette porte
    depuis le premier jour, mot pour mot : « elle se posera PAR-DESSUS comme
    les radios ».

    ⚠️ Rien d'autre n'apprend quoi que ce soit. Le chef d'orchestre demande
    `amb_quais` comme avant, le bouton RADIO du camion demande
    `station_camion`, l'hysteresis et l'echelle de priorite ne bougent pas :
    le slug est le meme des deux cotes, et c'est tout l'interet.

    ⚠️ TROIS etats, pas deux. « en cours » n'est pas « ratee » : pendant le
    telechargement on se TAIT quelques centaines de millisecondes, comme une
    vraie radio qu'on allume, plutot que de lancer un bout de sequenceur qu'il
    faudrait couper net a l'arrivee du fichier. « ratee » (404, decodage
    refuse, reseau coupe) rend la main aux notes pour de bon — c'est la regle 1
    d'`audio.py` : le jeu marche sans les fichiers. */
  const morceauxCharges = new Map();   // cle de tampon -> 'en cours' | 'prete' | 'ratee'

  /** Telecharge et decode un morceau une seule fois. Rend son etat. */
  function chargerMorceau(cle, fichier, ensuite) {
    if (tampons.has(cle)) { ensuite(); return 'prete'; }
    const etat = morceauxCharges.get(cle);
    if (etat === 'ratee' || etat === 'en cours') return etat;
    // ⚠️ Pas encore d'audio (avant le premier geste du joueur) : on ne marque
    // RIEN et on repartira au prochain tour. Poser « en cours » ici laisserait
    // le morceau en attente d'un telechargement qui n'a jamais commence — et
    // le menu, qui demande sa musique bien avant le premier clic, resterait
    // muet pour toujours.
    if (!ctx || !fenetre || !fenetre.fetch) return 'en cours';
    morceauxCharges.set(cle, 'en cours');
    decoder(base + B.defs.audio.dossier + '/' + fichier)
      .then(function (tampon) {
        tampons.set(cle, [tampon]);
        morceauxCharges.set(cle, 'prete');
        ensuite();
      })
      .catch(function () { morceauxCharges.set(cle, 'ratee'); });
    return 'en cours';
  }

  /** Le volume du morceau quand c'est le FICHIER qui joue. ⚠️ Ce n'est pas
      celui des notes et ca ne peut pas l'etre : dans le sequenceur, le volume
      du morceau multiplie celui de chaque voix (0,11 a 0,45), donc `titre` a
      0,85 sort a un dixieme de l'echelle. Un mp3 arrive normalise. Python
      declare les deux (`musique.py` pour les notes, `audio.MUSIQUES` pour le
      fichier) et on prend celui de la source qui joue. */
  function volumeFichier(def) {
    const v = def.volume_fichier;
    return (v === undefined || v === null) ? (def.volume || 1) : v;
  }

  /** Ce morceau-la joue-t-il en NOTES ? Oui s'il n'a pas de mp3, ou si son mp3
      n'arrivera jamais. */
  function enNotes(def, cle) {
    return !def.fichier || morceauxCharges.get(cle) === 'ratee';
  }

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
    // Le fondu (voir « Le fondu enchaine »). Le mp3 a le sien dans `boucles` ; le
    // SEQUENCEUR, dont les notes ne traversent aucune boucle, a `chaine`.
    entreeS: 0,         // la duree du fondu d'entree de la piste courante
    chaine: null,       // ou aboutissent les notes de la piste courante
    // ⚠️ Une piste en notes qui s'en va ne se tait pas : elle continue de poser ses
    // notes, dans sa chaine qui baisse, jusqu'a la fin de la courbe. Le sequenceur
    // ne programme qu'un quart de seconde d'avance : sans elle, l'ancienne se
    // tairait en un quart de seconde et le « fondu » n'aurait rien a baisser.
    sortantes: [],      // { def, debutT, prochain, chaine, finT }

    morceaux: function () { return (B.defs && B.defs.audio && B.defs.audio.musiques) || []; },
    def: function (slug) {
      if (!slug) return null;
      const l = Mus.morceaux();
      for (let i = 0; i < l.length; i++) if (l[i].slug === slug) return l[i];
      return null;
    },

    /** Demande un morceau. Le redemander pendant qu'il joue ne le fait PAS
        repartir du debut : le menu le reclame a chaque image.

        ⚠️ Le morceau qui jouait ne s'arrete pas, il BAISSE pendant que celui-ci
        monte, `fondu` secondes (`fondu_s` par defaut). `0` coupe net — se justifie
        a l'appel. */
    jouer: function (slug, fondu) {
      if (Mus.courante === slug) return true;
      if (!Mus.def(slug)) { Mus.arreter(); return false; }
      const d = fondu === undefined ? dureeFondu() : fondu;
      Mus.arreter(d);
      Mus.courante = slug; Mus.pas = 0; Mus.debutT = 0; Mus.prochain = 0; Mus.entreeS = d;
      return true;
    },

    /** La cle du tampon de ce morceau. ⚠️ Le musicien de rue a la sienne
        (`rue-`) : il joue PAR-DESSUS cette piste-ci, les deux boucles doivent
        pouvoir tourner en meme temps. */
    cle: function (slug) { return 'musique-' + slug; },

    /** Le mp3 est la : on le met en boucle. */
    _demarrer: function () {
      const def = Mus.def(Mus.courante);
      if (!def || !def.fichier) return;
      boucle(Mus.cle(Mus.courante), true, volumeFichier(def), Mus.entreeS);
    },

    /** Eteint la musique — en fondu (`fondu_s`), sauf si on passe `0`. */
    arreter: function (fondu) {
      const d = fondu === undefined ? dureeFondu() : fondu;
      if (Mus.courante) boucle(Mus.cle(Mus.courante), false, undefined, d);
      // Le sequenceur : la piste passe en `sortantes` et finit sa courbe. A `0`, les
      // notes deja posees s'eteignent seules — un quart de seconde au plus.
      if (Mus.chaine && ctx && d > 0 && Mus.debutT) {
        Mus.chaine.sortir(d);
        Mus.sortantes.push({ def: Mus.def(Mus.courante), debutT: Mus.debutT, prochain: Mus.prochain,
                             chaine: Mus.chaine, finT: ctx.currentTime + d });
      }
      Mus.courante = null; Mus.pas = 0; Mus.debutT = 0; Mus.prochain = 0; Mus.chaine = null;
    },
    stop: function () { Mus.arreter(); },       // l'ancien nom, garde par prudence

    /** Pose toutes les notes d'un pas, a l'instant `t`, dans `sortie`. */
    poser: function (def, p, t, pasS, sortie) {
      for (let v = 0; v < def.voix.length; v++) {
        const voix = def.voix[v];
        const motif = voix.motif || def.pas;
        const dans = ((p % motif) + motif) % motif;
        for (let n = 0; n < voix.notes.length; n++) {
          const note = voix.notes[n];
          if (note[0] !== dans) continue;
          const volume = (voix.volume || 0.2) * (note[3] === undefined ? 1 : note[3])
                       * (def.volume || 1) * Mus.attenuation;
          if (voix.forme === 'bruit') bruitA(t, Math.min(0.12, note[2] * pasS), volume, note[1], sortie);
          // ⚠️ 0.92 : la note s'arrete juste avant la suivante. Sans ce blanc,
          // deux notes voisines de meme hauteur n'en font plus qu'une longue.
          else tonA(t, frequence(note[1]), note[2] * pasS * 0.92, voix.forme, volume, 0, sortie);
        }
      }
    },

    /** Programme les pas d'une piste jusqu'a l'horizon. `piste` porte `debutT` et
        `prochain` : c'est `Mus` lui-meme pour la piste courante, un objet de
        `sortantes` pour une qui s'en va. Rend la duree d'un pas, en secondes. */
    programmer: function (piste, def, sortie) {
      const pasS = 60 / def.bpm / (def.pas_par_temps || 1);
      if (!piste.debutT) { piste.debutT = ctx.currentTime + 0.08; piste.prochain = 0; }
      const limite = ctx.currentTime + HORIZON_S;
      // Un garde-fou : si l'onglet dort une minute, on ne rattrape pas mille
      // pas d'un coup — on se recale sur l'horloge.
      const retard = (ctx.currentTime - piste.debutT) / pasS - piste.prochain;
      if (retard > 32) { piste.prochain = Math.floor((ctx.currentTime - piste.debutT) / pasS); }
      while (piste.debutT + piste.prochain * pasS < limite) {
        Mus.poser(def, piste.prochain, piste.debutT + piste.prochain * pasS, pasS, sortie);
        piste.prochain++;
      }
      return pasS;
    },

    /** Une image de musique. A appeler a CHAQUE image, y compris au menu. */
    tick: function () {
      // Le ducking glisse d'abord : la duree d'un pas ne depend pas de ce qui joue.
      Duck.maj();
      // Les pistes en notes qui finissent leur fondu de sortie — avant tout le
      // reste : quand plus rien ne joue, elles sont justement les seules.
      if (Mus.sortantes.length) {
        if (etatSon() !== 'actif') Mus.sortantes.length = 0;
        else {
          Mus.sortantes = Mus.sortantes.filter(function (q) { return ctx.currentTime < q.finT; });
          Mus.sortantes.forEach(function (q) { Mus.programmer(q, q.def, q.chaine.entree); });
        }
      }
      const def = Mus.def(Mus.courante);
      if (!def) return;
      // ⚠️ Un morceau qui sort d'un mp3 n'a RIEN a programmer : la boucle tourne
      // toute seule dans le graphe audio. Sans ce retour, le sequenceur poserait
      // ses notes PAR-DESSUS le fichier — les deux versions du meme morceau
      // ensemble, decalees d'un temps.
      // ⚠️ Et on redemande le chargement a CHAQUE image tant qu'il n'est pas
      // parti : le menu reclame sa musique avant le premier geste du joueur,
      // donc avant qu'il y ait un AudioContext. Un seul essai au moment du
      // `jouer()` et le theme n'arriverait jamais.
      const cle = Mus.cle(Mus.courante);
      if (!enNotes(def, cle)) {
        if (!boucles.has(cle)) chargerMorceau(cle, def.fichier, Mus._demarrer);
        return;
      }
      // ⚠️ Tant que le son n'est pas accorde (banc sans audio, ou navigateur qui
      // attend un geste), on avance un simple compteur : l'horloge audio est
      // figee, et programmer dedans ferait sortir toute la boucle d'un coup au
      // reveil. Le morceau demarrera pour de bon a la premiere image sonore.
      if (etatSon() !== 'actif') { Mus.pas++; Mus.debutT = 0; Mus.prochain = 0; return; }
      // ⚠️ La chaine naît ICI, au vrai depart des notes : son fondu d'entree part
      // de cet instant, pas de celui ou le morceau a ete demande.
      if (!Mus.chaine) Mus.chaine = chaineDeFondu(Mus.entreeS);
      const pasS = Mus.programmer(Mus, def, Mus.chaine.entree);
      Mus.pas = Math.max(0, Math.floor((ctx.currentTime - Mus.debutT) / pasS));
    },
  };

  // --- Le musicien de rue : une musique qui sort de QUELQU'UN ------------------
  //
  /*: ⚠️ La fiche « des sortes de gens » promettait un musicien qui « joue — et
    CA S'ENTEND ». Ce qui a ete livre, c'est un corps avec une guitare dessinee
    dessus et ZERO note : le jeu avait deja un sequenceur, dix morceaux ecrits
    en notes et un chef d'orchestre, et l'homme a la guitare etait muet.

    ⚠️ CE N'EST PAS UNE PISTE, C'EST UN SON DU MONDE. Il ne passe donc pas par
    `Chef` et ne prend la place de rien : il joue PAR-DESSUS l'ambiance du
    district, comme un moteur de char, et son volume vient de la DISTANCE. On
    l'entend d'un coin de rue, on l'a dans les oreilles devant lui, il s'eteint
    quand on s'en va. C'est pour ca qu'il lui faut son propre sequenceur : le
    volume change a chaque image, et `Mus` pose ses notes un quart de seconde en
    avance (HORIZON_S) — a volume fixe, on l'aurait entendu jouer fort une
    fraction de seconde apres qu'on soit parti.

    ⚠️ UN SEUL A LA FOIS, le plus proche : dix musiciens feraient dix
    sequenceurs, et deux tounes differentes a trente pixels l'une de l'autre ne
    font pas de la musique, elles font du bruit. */
  const Rue = {
    courante: null,     // le slug du morceau demande cette image
    jouee: null,        // celui qui tourne pour de vrai
    volume: 0,          // 0..1, la distance
    attenuation: 1,     // le ducking (une voix) : `Duck` le fait glisser
    sousEtat: 1,        // le retrait sous la musique d'ETAT : il glisse aussi
    demandeT: -1,       // la derniere image ou quelqu'un a demande a jouer
    pas: 0, debutT: 0, prochain: 0,
    sortie: null,       // le gain qui porte la distance
    g: 0,               // ce gain-la, calcule cette image : distance × ducking × etat

    def: function (slug) { return Mus.def(slug); },

    /** ⚠️ SA cle a lui, pas celle de `Mus` : le musicien joue PAR-DESSUS
        l'ambiance du district, donc deux boucles tournent en meme temps et
        deux boucles ne peuvent pas partager une entree. */
    cle: function (slug) { return 'rue-' + slug; },

    /** Sa toune sort-elle d'un mp3 ? */
    surFichier: function () {
      const def = Rue.def(Rue.jouee);
      return !!(def && !enNotes(def, Rue.cle(Rue.jouee)));
    },

    /** Le mp3 est arrive : on le met en boucle, au volume de la distance. */
    _demarrer: function () {
      const def = Rue.def(Rue.jouee);
      if (!def || !def.fichier) return;
      boucle(Rue.cle(Rue.jouee), true, volumeFichier(def) * Rue.g, dureeFondu(true));
      // ⚠️ L'instant ou la boucle part : c'est LUI qui fait gratter la main en
      // mesure quand c'est un fichier qui joue (voir `surLeTemps`).
      Rue.debutT = ctx ? ctx.currentTime : 0;
    },

    /** Le musicien le plus proche reclame sa toune, a ce volume-la. A appeler
        a chaque image tant qu'il joue ; des qu'on cesse, la musique s'arrete.

        ⚠️ **LE PLUS FORT GAGNE, PAS LE DERNIER ARRIVE.** Tant qu'il n'y avait
        que des musiciens, `entites.js` choisissait LE PLUS PROCHE avant
        d'appeler et l'ordre ne voulait rien dire. Depuis que l'orgue de la
        foire demande lui aussi (`Foire.laFoireSEntend`, une source fixe), deux
        sources reclament dans la meme image : sans cette ligne, celle qui joue
        est celle dont la boucle du jeu tombe en dernier — donc un gars a la
        guitare a l'entree de la foire couvrirait un limonaire de six metres. */
    demander: function (slug, volume) {
      if (!Rue.def(slug)) return false;
      const v = Math.max(0, Math.min(1, volume));
      if (Rue.demandeT === B.t && Rue.courante && v <= Rue.volume) return false;
      Rue.courante = slug;
      Rue.volume = v;
      Rue.demandeT = B.t;
      return true;
    },

    arreter: function () {
      // ⚠️ En fondu, vif : un musicien qu'on perd de vue s'eclipse, il ne claque pas.
      if (Rue.jouee) boucle(Rue.cle(Rue.jouee), false, undefined, dureeFondu(true));
      Rue.courante = null; Rue.jouee = null; Rue.volume = 0; Rue.g = 0;
      Rue.pas = 0; Rue.debutT = 0; Rue.prochain = 0;
    },

    /** Le gain a LUI : cree une fois, garde, et regle a chaque image. */
    _sortie: function () {
      if (!Rue.sortie && ctx) { Rue.sortie = ctx.createGain(); Rue.sortie.connect(maitre); }
      return Rue.sortie;
    },

    /** Une image de musique de rue. Appelee a chaque image, comme `Mus.tick`. */
    tick: function () {
      // ⚠️ La musique d'ETAT prend toute la place : quand la police te court
      // apres, la toune du guitariste n'a plus d'importance. Le chiffre vient de
      // Python (`musique.MUSIQUE.rue_sous_etat`), comme le reste de l'echelle.
      // ⚠️ Il GLISSE, et il glisse TOUJOURS — meme sans musicien en vue : un gars
      // qui apparait en pleine poursuite doit entrer deja tasse, pas plein puis
      // redescendre.
      Rue.sousEtat = glisser(Rue.sousEtat, pisteDEtat(Chef.piste) ? (reglagesMusique().rue_sous_etat || 0.25) : 1);
      // ⚠️ Plus personne ne demande : le musicien est mort, assomme, hors de
      // portee ou hors de la bulle. On se tait — et c'est ce qui evite qu'une
      // toune continue toute seule a l'autre bout de la ville.
      //
      // ⚠️ UNE image de retard est NORMALE, et exiger la meme couperait le son
      // a CHAQUE tour. Dans `jeu.js`, `Son.Rue.tick()` passe en tete de `maj()`
      // et `Entites.maj()` — celui qui DEMANDE — tout a la fin, juste avant
      // `B.t++` : la demande qu'on lit ici porte donc toujours le numero de
      // l'image precedente. Avec `!==`, le musicien etait reduit au silence a
      // l'image suivant chacune de ses demandes, sans arret, et sa toune ne
      // demarrait jamais. Au-dela d'une image, la, plus personne ne joue.
      if (B.t - Rue.demandeT > 1) Rue.courante = null;
      const def = Rue.def(Rue.courante);
      if (!def) { if (Rue.jouee) Rue.arreter(); return; }
      if (Rue.jouee !== Rue.courante) {
        // ⚠️ On eteint l'ancienne AVANT de changer de toune : `Rue.cle` suit
        // `Rue.jouee`, et une boucle qu'on oublie de nommer joue pour toujours.
        // Sa toune s'efface pendant que l'autre monte — meme regle que la piste de la ville.
        if (Rue.jouee) boucle(Rue.cle(Rue.jouee), false, undefined, dureeFondu(true));
        Rue.jouee = Rue.courante; Rue.pas = 0; Rue.debutT = 0; Rue.prochain = 0;
      }
      if (etatSon() !== 'actif') { Rue.pas++; Rue.debutT = 0; Rue.prochain = 0; return; }
      Rue.g = Rue.volume * Rue.attenuation * Rue.sousEtat;
      // LE FICHIER, quand il y en a un. ⚠️ Le volume se REPOSE a chaque image :
      // c'est la distance, et elle change a chaque pas du joueur. Une boucle
      // reglee une fois au depart resterait forte a l'autre bout de la rue.
      const cle = Rue.cle(Rue.jouee);
      if (!enNotes(def, cle)) {
        if (boucles.has(cle)) reglerBoucle(cle, volumeFichier(def) * Rue.g);
        else chargerMorceau(cle, def.fichier, Rue._demarrer);
        return;
      }
      const sortie = Rue._sortie();
      if (!sortie) return;
      sortie.gain.value = Rue.g;
      const pasS = 60 / def.bpm / (def.pas_par_temps || 1);
      if (!Rue.debutT) { Rue.debutT = ctx.currentTime + 0.08; Rue.prochain = 0; }
      const limite = ctx.currentTime + HORIZON_S;
      const retard = (ctx.currentTime - Rue.debutT) / pasS - Rue.prochain;
      if (retard > 32) { Rue.prochain = Math.floor((ctx.currentTime - Rue.debutT) / pasS); }
      while (Rue.debutT + Rue.prochain * pasS < limite) {
        Rue.poser(def, Rue.prochain, Rue.debutT + Rue.prochain * pasS, pasS, sortie);
        Rue.prochain++;
      }
      Rue.pas = Math.max(0, Math.floor((ctx.currentTime - Rue.debutT) / pasS));
    },

    /** Les notes d'un pas, dans SA sortie. Meme calcul que `Mus.poser` — le
        volume de la distance est sur le gain, pas sur chaque note. */
    poser: function (def, p, t, pasS, sortie) {
      for (let v = 0; v < def.voix.length; v++) {
        const voix = def.voix[v];
        const motif = voix.motif || def.pas;
        const dans = ((p % motif) + motif) % motif;
        for (let n = 0; n < voix.notes.length; n++) {
          const note = voix.notes[n];
          if (note[0] !== dans) continue;
          const volume = (voix.volume || 0.2) * (note[3] === undefined ? 1 : note[3]) * (def.volume || 1);
          if (voix.forme === 'bruit') bruitA(t, Math.min(0.12, note[2] * pasS), volume, note[1], sortie);
          else tonA(t, frequence(note[1]), note[2] * pasS * 0.92, voix.forme, volume, 0, sortie);
        }
      }
    },

    /** Ou en est la mesure, de 0 a 1 : c'est ce qui fait gratter la main du
        musicien EN MESURE plutot qu'a un rythme invente par le dessin. */
    surLeTemps: function () {
      const def = Rue.def(Rue.jouee);
      if (!def) return 0;
      // ⚠️ Un mp3 n'a pas de « pas » : la mesure se compte sur l'horloge audio
      // depuis le depart de la boucle, au tempo que Python declare. Sans ca, la
      // main du musicien gratterait a un rythme invente par le dessin pendant
      // que le haut-parleur joue autre chose — et c'est exactement ce que cette
      // fonction existe pour empecher.
      if (Rue.surFichier()) {
        // ⚠️ « La boucle tourne-t-elle ? », pas « `debutT` est-il pose ? » :
        // une horloge audio peut valoir zero (elle vaut zero au banc), et un
        // instant de depart legitime serait alors pris pour une absence.
        if (!ctx || !boucles.has(Rue.cle(Rue.jouee))) return 0;
        const t = (ctx.currentTime - Rue.debutT) * (def.bpm || 90) / 60;
        return t - Math.floor(t);
      }
      const parTemps = def.pas_par_temps || 1;
      return ((Rue.pas % parTemps) + parTemps) % parTemps / parTemps;
    },
  };

  return {
    init, reveiller, sonder, etatSon, enAttente, surEtat, pret, suspendre, fermer, majVolume, prechauffer, ton, bruit, SFX, Mus, Chef, Rue,
    chargerEchantillons, echantillon, joue, estCharge, jouerA, presence, depuis, boucle, boucleActive, reglerBoucle, volumeBoucle, etouffer, coupureBoucle,
    Radio, Ambiance, Rumeur, Voix, Ondes, Souffle, Quartier,
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
