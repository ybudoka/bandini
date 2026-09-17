/* Bandini — le casque : jouer dans un Meta Quest, aux manettes Touch.

   ⚠️ Pourquoi un module entier pour des MANETTES. Le navigateur du Quest ne
   montre pas ses manettes Touch a une page ordinaire : elles y pointent et
   cliquent, mais `navigator.getGamepads()` ne les voit pas. Elles ne se lisent
   que dans une SESSION WebXR, par `XRInputSource.gamepad` (disposition
   `xr-standard` — doc Meta, « Meta Quest Touch Pro Controller Support for
   Browser »). Or une session immersive n'affiche plus rien de la page : il faut
   y dessiner le jeu soi-meme.

   D'ou les deux moities de ce fichier :
   - un ECRAN devant soi, fixe dans la piece : la toile du jeu copiee en texture
     a chaque image, sur un rectangle WebGL ;
   - les deux manettes rendues a `Entree` comme UNE manette Xbox (`VERS_XBOX`) :
     les boutons tombent la ou ils tombent sur la manette de tous les jours, et
     rien d'autre dans le jeu n'a a savoir qu'on est dans un casque.

   ⚠️ Dans le casque, c'est la SESSION qui cadence le jeu
   (`session.requestAnimationFrame`) : la boucle de la fenetre se tait
   (`Jeu.boucle`), sinon le monde avancerait deux fois.

   ⚠️ Et on n'en sort jamais pour rester sur une partie : hors du casque, un
   joueur de Quest n'a plus aucune manette (la page 2D ne voit pas les Touch).
   Quitter le casque ramene donc au titre — partie sauvegardee — la ou JOUER
   DANS LE CASQUE l'attend. */

const Casque = (function () {
  'use strict';

  //: L'ecran, en metres, dans l'espace `local` (l'origine est la tete au moment
  //: d'entrer) : 2,4 m de large a 2 m devant, un peu sous les yeux — une grande
  //: tele vue du divan, 62° de champ.
  const DISTANCE = 2, LARGEUR = 2.4, SOUS_LES_YEUX = 0.15;
  const HAUTEUR = LARGEUR * VH / VW;
  //: L'echelle de la toile dans le casque. ⚠️ Pas celle de la fenetre : la
  //: fenetre du navigateur n'a plus rien a dire, et une toile a 1x baverait sur
  //: 2,4 m. A 3x, les pixels du jeu restent francs sous le filtrage lineaire,
  //: sans le fourmillement d'un filtrage au plus proche quand la tete bouge.
  const ECHELLE = 3;
  const FOND = [0.043, 0.039, 0.071];   // #0b0a12, le noir du jeu

  //: Chaque bouton d'une manette Xbox (`mapping: "standard"`, dans l'ordre) et
  //: d'ou il vient sur les Touch : [main, indice xr-standard]. En xr-standard, 0
  //: est la gachette, 1 la poignee, 3 le clic du stick ; les Touch y ajoutent 4
  //: (A ou X, le bouton du bas) et 5 (B ou Y, celui du haut).
  //: ⚠️ PAUSE est le clic du stick GAUCHE, pas le bouton ☰ : xr-standard ne
  //: promet pas ce bouton-la, alors que toutes les Touch rendent le clic du stick.
  const VERS_XBOX = [
    ['right', 4],   // 0  A      — action
    ['right', 5],   // 1  B      — courir, retour
    ['left', 4],    // 2  X      — frapper
    ['left', 5],    // 3  Y      — arme
    ['left', 1],    // 4  LB     — la poignee gauche : arme
    ['right', 1],   // 5  RB     — la poignee droite : frapper
    ['left', 0],    // 6  LT     — la gachette gauche : frein
    ['right', 0],   // 7  RT     — la gachette droite : gaz
    ['right', 3],   // 8  SELECT — clic du stick droit : carte
    ['left', 3],    // 9  START  — clic du stick gauche : pause
  ];
  //: Le stick droit fait la CROIX (12 a 15) : c'est elle qui promene un curseur
  //: de menu d'un cran a la fois. Au-dela de ce seuil, la direction est tenue.
  const SEUIL_CROIX = 0.5;
  const VIDE = { pressed: false, value: 0 };

  const VS = 'attribute vec3 p; attribute vec2 uv; uniform mat4 proj; uniform mat4 vue; varying vec2 v;\n'
    + 'void main() { v = uv; gl_Position = proj * vue * vec4(p, 1.0); }';
  const FS = 'precision mediump float; uniform sampler2D tex; varying vec2 v;\n'
    + 'void main() { gl_FragColor = texture2D(tex, v); }';

  let nav = null, doc = null, fenetre = null;
  let session = null, demande = false, espace = null, couche = null;
  let gl = null, prog = null, tampon = null, texture = null, loc = null;
  let manette = null;            // la manette Xbox fabriquee a cette image
  let supporte = false;

  function init(d, w, n) {
    doc = d; fenetre = w; nav = n;
    const b = d.getElementById('bouton-casque');
    // ⚠️ Le son vient du MEME clic : la gachette qui clique la page est un vrai
    // geste pour le navigateur — le seul qu'un joueur de casque fera jamais.
    if (b) b.addEventListener('click', function () { Son.reveiller(); Hud.majAvisSon(); Entree.videPresse(); entrer(); });
    Entree.brancherCasque(function () { return manette; }, vibrer);
    return sonder();
  }

  /** Le bouton ne se montre que si le navigateur ouvre VRAIMENT une session
      immersive — un Quest oui, un telephone ou un Mac non. */
  function sonder() {
    const xr = nav && nav.xr;
    if (!xr || !xr.isSessionSupported) return Promise.resolve(montrer(false));
    return Promise.resolve()
      .then(function () { return xr.isSessionSupported('immersive-vr'); })
      .then(montrer, function () { return montrer(false); });
  }

  function montrer(ok) {
    supporte = !!ok;
    const b = doc && doc.getElementById('bouton-casque');
    if (b) b.hidden = !supporte;
    // ⚠️ Changer de partie RECHARGE la page, qui rouvre alors le choix des parties
    // toute seule — sur la toile, sans voile. Si c'etait dans le casque, la
    // session est morte avec la page : les Touch ne commandent plus ce menu, et
    // le bouton du casque est sous la voile absente. On ne sait pas d'ici ou le
    // changement s'est fait : sur un navigateur qui ouvre un casque, on rend le
    // titre (une manette Bluetooth n'y perd qu'un JOUER de plus).
    if (supporte && !session && !demande && B.etat === 'titre' && !Hud.voileCourant) {
      if (B.menu) Hud.fermerMenu();
      Hud.voile('titre');
    }
    return supporte;
  }

  /** JOUER DANS LE CASQUE.

      ⚠️ `requestSession` exige un geste : on l'appelle DANS le clic, sans rien
      attendre avant. */
  function entrer() {
    if (session || demande || !nav || !nav.xr || B.etat === 'chargement') return Promise.resolve(false);
    demande = true;
    return nav.xr.requestSession('immersive-vr').then(demarrer).catch(function (err) {
      const s = session;
      fin();
      if (s) { try { s.end(); } catch (e) { /* deja fermee */ } }
      const etat = doc.getElementById('etat-chargement');
      if (etat) etat.textContent = 'Le casque n’a pas pu s’ouvrir : ' + ((err && err.message) || err);
      return false;
    });
  }

  function demarrer(s) {
    session = s;
    s.addEventListener('end', fin);
    s.addEventListener('visibilitychange', surVisibilite);
    const toile = doc.createElement('canvas');
    gl = toile.getContext('webgl', { xrCompatible: true, alpha: false, antialias: false });
    if (!gl || !gl.createShader) throw new Error('pas de WebGL');
    preparerGL();
    couche = new fenetre.XRWebGLLayer(s, gl);
    s.updateRenderState({ baseLayer: couche });
    return s.requestReferenceSpace('local').then(function (e) {
      if (session !== s) return false;       // refermee pendant qu'on attendait
      espace = e;
      demande = false;
      Base.imposerEchelle(ECHELLE);
      Base.redimensionner(fenetre, Entree.estTactile);
      s.requestAnimationFrame(image);
      // Ce que fait JOUER : le choix des parties (un menu de la toile, donc visible
      // dans le casque), ou la partie tout de suite s'il n'y en a aucune.
      if (B.etat === 'titre') Jeu.ouvrirParties();
      // ⚠️ Apres, parce que jouer pose son propre message. PAUSE est le seul bouton
      // qu'on ne trouverait pas seul : sur une Xbox c'est START, ici un clic de stick.
      Hud.message('CASQUE : CLIC DU STICK GAUCHE = PAUSE', 360);
      return true;
    });
  }

  /** Sortir du casque (une voile a montrer, QUITTER VERS LE TITRE). La session
      previent par son evenement `end`, qui fait le menage (`fin`). */
  function sortir() {
    const s = session;
    if (!s) return;
    try {
      const p = s.end();
      if (p && p.catch) p.catch(fin);
    } catch (e) { fin(); }
  }

  function fin() {
    if (!session && !demande) return;
    session = null; demande = false; espace = null; couche = null; manette = null;
    gl = null; prog = null; tampon = null; texture = null; loc = null;
    Base.imposerEchelle(null);
    Base.redimensionner(fenetre, Entree.estTactile);
    // ⚠️ Pas de partie hors du casque (voir l'en-tete) : retour au titre, qui
    // sauvegarde. Sauf si c'est une VOILE qui nous a fait sortir : c'est elle
    // qu'on vient montrer, elle reste.
    if (Hud.voileCourant) return;
    if (B.etat === 'jeu' || B.etat === 'pause' || B.etat === 'carte') Jeu.retourTitre();
    // Le choix des parties est un menu de la toile, sans voile : hors du casque
    // les Touch ne le commandent plus. Le titre revient, et son bouton avec.
    else if (B.etat === 'titre') { if (B.menu) Hud.fermerMenu(); Hud.voile('titre'); }
  }

  //: ⚠️ Le bouton Meta ouvre le menu du systeme PAR-DESSUS la session
  //: (`visible-blurred`) : le jeu ne recoit plus les manettes mais il tournerait
  //: encore, et on reviendrait mort. Pause. Retirer le casque le cache
  //: (`hidden`) : le son se tait aussi, et revient avec l'image.
  function surVisibilite() {
    const etat = session && session.visibilityState;
    if (!etat) return;
    if (etat !== 'visible' && B.etat === 'jeu') Jeu.pause();
    if (etat === 'hidden') Son.suspendre();
    else if (etat === 'visible') Son.reveiller();
  }

  /** Une image du casque : les manettes, la simulation, puis l'ecran. */
  function image(t, frame) {
    const s = session;
    if (!s) return;
    s.requestAnimationFrame(image);
    manette = manetteXbox(s.inputSources);
    Jeu.avancer(t);
    if (session === s) dessiner(frame);
  }

  /** Les deux manettes Touch, rendues comme UNE manette Xbox « standard ».
      Rend null s'il n'y a aucune manette (les mains nues n'ont pas de boutons). */
  function manetteXbox(sources) {
    const mains = {};
    for (const src of (sources || [])) {
      // ⚠️ Une main nue (`src.hand`) peut porter un gamepad — le pincement y
      // ferait la gachette, donc le gaz. On ne lit que les manettes.
      if (src && src.gamepad && !src.hand && (src.handedness === 'left' || src.handedness === 'right')) {
        mains[src.handedness] = src.gamepad;
      }
    }
    if (!mains.left && !mains.right) return null;
    const boutons = VERS_XBOX.map(function (d) {
      const g = mains[d[0]];
      const bt = g && g.buttons && g.buttons[d[1]];
      if (!bt) return VIDE;
      const v = typeof bt.value === 'number' && bt.value > 0 ? bt.value : (bt.pressed ? 1 : 0);
      return { pressed: !!bt.pressed || v > 0.5, value: v };
    });
    boutons.push(VIDE, VIDE);             // 10 et 11 : deja pris par PAUSE et CARTE
    const g = stick(mains.left), d = stick(mains.right);
    boutons.push(tenu(d[1] < -SEUIL_CROIX), tenu(d[1] > SEUIL_CROIX),
                 tenu(d[0] < -SEUIL_CROIX), tenu(d[0] > SEUIL_CROIX));
    return { id: 'Meta Quest Touch', mapping: 'standard', connected: true,
             buttons: boutons, axes: [g[0], g[1], d[0], d[1]] };
  }

  function tenu(oui) { return oui ? { pressed: true, value: 1 } : VIDE; }

  //: En xr-standard, le stick est aux axes 2 et 3 : 0 et 1 appartiennent au pave
  //: tactile, que les Touch n'ont pas (ils y restent a zero).
  function stick(g) {
    if (!g || !g.axes) return [0, 0];
    const a = g.axes.length >= 4 ? 2 : 0;
    return [g.axes[a] || 0, g.axes[a + 1] || 0];
  }

  /** Ce sont les mains qui tremblent (`Entree.vibrer`). */
  function vibrer(ms) {
    if (!session) return;
    for (const src of (session.inputSources || [])) {
      const h = src && src.gamepad && src.gamepad.hapticActuators && src.gamepad.hapticActuators[0];
      if (!h || !h.pulse) continue;
      try {
        const p = h.pulse(0.6, ms);
        if (p && p.catch) p.catch(function () {});     // un refus ne doit pas finir en erreur de console
      } catch (e) { /* rien */ }
    }
  }

  // --- L'ecran --------------------------------------------------------------------------

  function nuanceur(type, source) {
    const s = gl.createShader(type);
    gl.shaderSource(s, source);
    gl.compileShader(s);
    if (!gl.getShaderParameter(s, gl.COMPILE_STATUS)) throw new Error('nuanceur : ' + gl.getShaderInfoLog(s));
    return s;
  }

  function preparerGL() {
    prog = gl.createProgram();
    gl.attachShader(prog, nuanceur(gl.VERTEX_SHADER, VS));
    gl.attachShader(prog, nuanceur(gl.FRAGMENT_SHADER, FS));
    gl.linkProgram(prog);
    if (!gl.getProgramParameter(prog, gl.LINK_STATUS)) throw new Error('programme : ' + gl.getProgramInfoLog(prog));
    loc = { p: gl.getAttribLocation(prog, 'p'), uv: gl.getAttribLocation(prog, 'uv'),
            proj: gl.getUniformLocation(prog, 'proj'), vue: gl.getUniformLocation(prog, 'vue') };
    // Quatre coins en bande de triangles, (x, y, z, u, v). Le haut de la toile
    // est v = 0 : `texImage2D` pose la premiere rangee du canevas en premier.
    const g = -LARGEUR / 2, d = LARGEUR / 2, z = -DISTANCE;
    const h = HAUTEUR / 2 - SOUS_LES_YEUX, b = -HAUTEUR / 2 - SOUS_LES_YEUX;
    tampon = gl.createBuffer();
    gl.bindBuffer(gl.ARRAY_BUFFER, tampon);
    gl.bufferData(gl.ARRAY_BUFFER, new Float32Array([g, h, z, 0, 0, g, b, z, 0, 1, d, h, z, 1, 0, d, b, z, 1, 1]),
                  gl.STATIC_DRAW);
    texture = gl.createTexture();
    gl.bindTexture(gl.TEXTURE_2D, texture);
    gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MIN_FILTER, gl.LINEAR);
    gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MAG_FILTER, gl.LINEAR);
    gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_S, gl.CLAMP_TO_EDGE);
    gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_T, gl.CLAMP_TO_EDGE);
  }

  function dessiner(frame) {
    const pose = espace && frame && frame.getViewerPose(espace);
    if (!pose || !couche) return;
    gl.bindFramebuffer(gl.FRAMEBUFFER, couche.framebuffer);
    gl.clearColor(FOND[0], FOND[1], FOND[2], 1);
    gl.clear(gl.COLOR_BUFFER_BIT | gl.DEPTH_BUFFER_BIT);
    gl.useProgram(prog);
    gl.activeTexture(gl.TEXTURE0);
    gl.bindTexture(gl.TEXTURE_2D, texture);
    gl.texImage2D(gl.TEXTURE_2D, 0, gl.RGBA, gl.RGBA, gl.UNSIGNED_BYTE, doc.getElementById('toile'));
    gl.bindBuffer(gl.ARRAY_BUFFER, tampon);
    gl.enableVertexAttribArray(loc.p);
    gl.vertexAttribPointer(loc.p, 3, gl.FLOAT, false, 20, 0);
    gl.enableVertexAttribArray(loc.uv);
    gl.vertexAttribPointer(loc.uv, 2, gl.FLOAT, false, 20, 12);
    for (const vue of pose.views) {
      const v = couche.getViewport(vue);
      gl.viewport(v.x, v.y, v.width, v.height);
      gl.uniformMatrix4fv(loc.proj, false, vue.projectionMatrix);
      gl.uniformMatrix4fv(loc.vue, false, vue.transform.inverse.matrix);
      gl.drawArrays(gl.TRIANGLE_STRIP, 0, 4);
    }
  }

  return {
    VERS_XBOX, ECHELLE,
    init, sonder, entrer, sortir, manetteXbox, vibrer,
    get actif() { return !!session || demande; },
    get supporte() { return supporte; },
  };
})();
