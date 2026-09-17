"""Le casque : jouer dans un Meta Quest, aux manettes Touch.

⚠️ Le probleme que ces tests gardent : le navigateur du Quest ne montre PAS ses
manettes Touch a une page ordinaire (`navigator.getGamepads()` ne les voit pas).
Elles ne se lisent que dans une session WebXR — et une session immersive
n'affiche rien de la page. Demande de Martin, 17 sept. 2026 : « ajoute le
support des manettes sur casque vr meta quest ».

⚠️ Tout se juge PAR LE BOUTON : la gachette clique le bouton de la page, un
bouton de la Touch s'enfonce, une image du casque passe — jamais en appelant
`Entree` ou `Jeu` a la place du joueur. C'est la chaine entiere qui casse
d'habitude, pas la fonction du bout.

Le faux Quest ci-dessous n'a pas de pixels : son WebGL ne fait que COMPTER les
appels, et c'est la session qui cadence (`q.image(n)`), pas `o.frame(n)`.
"""

import json

FAUX_QUEST = """
    function fauxQuest(o, supporte) {
        const appels = {};
        const gl = new Proxy({}, { get: function (_, nom) {
            if (typeof nom !== 'string') return undefined;
            if (/^[A-Z0-9_]+$/.test(nom)) return nom;
            return function () {
                appels[nom] = (appels[nom] || 0) + 1;
                return /^get(Shader|Program)Parameter$/.test(nom) ? true : {};
            };
        } });
        const creer = o.doc.createElement;
        o.doc.createElement = function (tag) {
            const el = creer(tag);
            // ⚠️ Seulement le contexte WebGL : le jeu cuit ses tuiles dans des
            // canevas 2D fabriques par la meme fonction.
            const deux = el.getContext;
            if (tag === 'canvas') el.getContext = function (type) { return type === 'webgl' ? gl : deux.call(el, type); };
            return el;
        };
        function main(cote) {
            const boutons = [];
            for (let k = 0; k < 7; k++) boutons.push({ pressed: false, value: 0 });
            const pulses = [];
            return { handedness: cote, profiles: ['meta-quest-touch-plus', 'oculus-touch-v3'], pulses: pulses,
                     gamepad: { mapping: 'xr-standard', buttons: boutons, axes: [0, 0, 0, 0],
                                hapticActuators: [{ pulse: function (f, ms) { pulses.push(ms); return Promise.resolve(true); } }] } };
        }
        const mains = { left: main('left'), right: main('right') };
        const ecouteurs = {};
        const session = {
            inputSources: [mains.left, mains.right], visibilityState: 'visible', fini: false, rafs: [], etat: null,
            addEventListener: function (t, f) { (ecouteurs[t] = ecouteurs[t] || []).push(f); },
            updateRenderState: function (e) { session.etat = e; },
            requestReferenceSpace: function (type) { session.espace = type; return Promise.resolve({ type: type }); },
            requestAnimationFrame: function (cb) { session.rafs.push(cb); return session.rafs.length; },
            end: function () { session.fini = true; (ecouteurs.end || []).forEach(function (f) { f({}); }); return Promise.resolve(); },
            emettre: function (t) { (ecouteurs[t] || []).forEach(function (f) { f({}); }); },
        };
        const demandes = [];
        o.fenetre.navigator.xr = {
            isSessionSupported: function (mode) { return Promise.resolve(supporte !== false && mode === 'immersive-vr'); },
            requestSession: function (mode) { demandes.push(mode); return Promise.resolve(session); },
        };
        o.fenetre.XRWebGLLayer = function () {
            this.framebuffer = null;
            this.getViewport = function () { return { x: 0, y: 0, width: 100, height: 100 }; };
        };
        const vue = { projectionMatrix: new Float32Array(16), transform: { inverse: { matrix: new Float32Array(16) } } };
        const cadre = { getViewerPose: function () { return { views: [vue, vue] }; } };
        // ⚠️ La MEME horloge que la fenetre, comme dans un vrai navigateur : une
        // horloge a part laisserait `dernier` loin devant, et la boucle de la
        // fenetre attendrait des secondes avant de refaire un pas.
        let horloge = o.fenetre.performance.now();
        return {
            gl: appels, session: session, mains: mains, demandes: demandes,
            /** `n` images du casque, a 72 Hz : c'est la session qui cadence. */
            image: function (n) {
                for (let i = 0; i < (n || 1); i++) {
                    horloge += 1000 / 72;
                    session.rafs.splice(0).forEach(function (cb) { cb(horloge, cadre); });
                }
            },
            /** Le bouton xr-standard `i` d'une main : 1 enfonce, 0 relache. */
            bouton: function (cote, i, v) { mains[cote].gamepad.buttons[i] = { pressed: v > 0.5, value: v }; },
            /** Une pression complete, le temps que le jeu la voie. */
            tape: function (cote, i) {
                this.bouton(cote, i, 1); this.image(4); this.bouton(cote, i, 0); this.image(4);
            },
            stick: function (cote, x, y) { const a = mains[cote].gamepad.axes; a[2] = x; a[3] = y; },
            /** Entrer comme le joueur : la gachette clique le bouton de la page. */
            entrer: function () {
                return L.Casque.sonder().then(function () {
                    o.elements['bouton-casque'].dispatch('click', {});
                    return o.attendre();
                }).then(o.attendre);
            },
        };
    }
"""


def quest(corps: str) -> str:
    """Une fonction de banc qui a `fauxQuest` sous la main."""
    return "function (L, o) {\n" + FAUX_QUEST + "\n" + corps + "\n}"


def test_le_bouton_du_casque_ne_se_montre_que_sur_un_casque(banc):
    r = banc(quest("""
        const sansWebXR = o.elements['bouton-casque'].hidden;
        fauxQuest(o, false);
        return L.Casque.sonder().then(function () {
            const sansImmersif = o.elements['bouton-casque'].hidden;
            fauxQuest(o, true);
            return L.Casque.sonder().then(function () {
                return { sansWebXR: sansWebXR, sansImmersif: sansImmersif, quest: o.elements['bouton-casque'].hidden };
            });
        });
    """))
    assert r["sansWebXR"] is True, "un navigateur sans WebXR (un telephone) ne doit pas voir le bouton"
    assert r["sansImmersif"] is True, "WebXR sans session immersive (un Mac) : pas de bouton non plus"
    assert r["quest"] is False, "sur un Quest, le bouton JOUER DANS LE CASQUE doit se montrer"


def test_la_gachette_sur_le_bouton_ouvre_le_casque_et_lance_la_partie(banc):
    r = banc(quest("""
        const q = fauxQuest(o);
        L.B.partie.ouvertureVue = true;          // pas d'ouverture : on juge la boucle
        return q.entrer().then(function () {
            const t0 = L.B.t;
            o.frame(30);
            const tFenetre = L.B.t;
            q.image(30);
            return { demandes: q.demandes, espace: q.session.espace, etat: L.B.etat, voile: L.Hud.voileCourant,
                     message: L.B.msg,
                     actif: L.Casque.actif, echelle: L.Base.SCALE,
                     couche: !!(q.session.etat && q.session.etat.baseLayer),
                     fenetre: tFenetre - t0, casque: L.B.t - tFenetre,
                     textures: q.gl.texImage2D || 0, dessins: q.gl.drawArrays || 0 };
        });
    """))
    assert r["demandes"] == ["immersive-vr"]
    assert r["actif"] is True and r["couche"] is True and r["espace"] == "local"
    assert r["etat"] == "jeu" and r["voile"] is None, \
        "entrer dans le casque doit lancer la partie : l'ecran titre est du DOM, il ne s'y voit pas"
    assert "STICK GAUCHE = PAUSE" in r["message"], \
        "PAUSE est un clic de stick dans le casque : on ne le devine pas, il faut le dire en entrant"
    assert r["echelle"] == 3, "la toile du casque ne suit pas la taille de la fenetre"
    assert r["fenetre"] == 0, "dans le casque, la boucle de la fenetre ne doit plus faire avancer le monde"
    assert r["casque"] >= 20, "c'est la session du casque qui doit cadencer la simulation"
    assert r["textures"] == 30, "la toile doit etre recopiee a chaque image du casque"
    assert r["dessins"] == 60, "un dessin de l'ecran par oeil, a chaque image"


def test_les_touch_tombent_comme_une_manette_xbox(banc):
    r = banc(quest("""
        const q = fauxQuest(o);
        L.B.partie.ouvertureVue = true;
        const actions = ['action', 'esquive', 'attaque', 'arme', 'carte', 'pause', 'haut', 'bas', 'gauche', 'droite', 'annuler'];
        return q.entrer().then(function () {
            const vu = {};
            function lire(nom) {
                vu[nom] = { actions: actions.filter(function (a) { return L.Entree.bas(a); }),
                            gaz: Math.round(L.Entree.gaz * 100) / 100, frein: Math.round(L.Entree.frein * 100) / 100 };
            }
            [['left', 0], ['left', 1], ['left', 3], ['left', 4], ['left', 5],
             ['right', 0], ['right', 1], ['right', 3], ['right', 4], ['right', 5]].forEach(function (b) {
                q.bouton(b[0], b[1], 1); q.image(3);
                lire(b[0] + b[1]);
                q.bouton(b[0], b[1], 0); q.image(3);
            });
            [['haut', 0, -1], ['bas', 0, 1], ['gauche', -1, 0], ['droite', 1, 0]].forEach(function (d) {
                q.stick('right', d[1], d[2]); q.image(3);
                lire('droit-' + d[0]);
                q.stick('right', 0, 0); q.image(3);
            });
            return vu;
        });
    """))
    assert r["right4"]["actions"] == ["action"], "A : ACTION"
    assert set(r["right5"]["actions"]) == {"esquive", "annuler"}, "B : COURIR et RETOUR, comme le B d'une Xbox"
    assert r["left4"]["actions"] == ["attaque"], "X : FRAPPER"
    assert r["left5"]["actions"] == ["arme"], "Y : ARME"
    assert r["left1"]["actions"] == ["arme"], "la poignee gauche est l'epaule gauche : ARME"
    assert r["right1"]["actions"] == ["attaque"], "la poignee droite est l'epaule droite : FRAPPER"
    assert r["left3"]["actions"] == ["pause"], "le clic du stick gauche : PAUSE"
    assert r["right3"]["actions"] == ["carte"], "le clic du stick droit : CARTE"
    assert r["right0"] == {"actions": [], "gaz": 1, "frein": 0}, "la gachette droite est le GAZ"
    assert r["left0"] == {"actions": [], "gaz": 0, "frein": 1}, "la gachette gauche est le FREIN"
    for sens in ("haut", "bas", "gauche", "droite"):
        assert r["droit-" + sens]["actions"] == [sens], f"le stick droit fait la croix : {sens}"


def test_au_stick_gauche_bandini_marche(banc):
    r = banc(quest("""
        const q = fauxQuest(o);
        L.B.partie.ouvertureVue = true;
        return q.entrer().then(function () {
            const j = L.B.joueur, d = o.ligneDroite();
            j.x = d.x; j.y = d.y;
            L.B.defs.conduite.trafic.vehicules_max = 0;
            L.B.entites.filter(function (e) { return e.type === 'vehicule'; }).forEach(function (e) { L.Entites.retirer(e); });
            const x0 = j.x;
            q.stick('left', 1, 0); q.image(60);
            const source = L.Entree.axe.source, x1 = L.B.joueur.x;
            q.stick('left', 0, 0); q.image(10);
            return { avance: x1 - x0, source: source, arrete: L.Entree.axe.mag };
        });
    """))
    assert r["avance"] > 40, "pousser le stick gauche doit faire marcher Bandini"
    assert r["source"] == "manette", "le stick du casque est un stick de manette (marche a mi-course, menus)"
    assert r["arrete"] == 0


def test_la_gachette_droite_fait_rouler_le_char(banc):
    r = banc(quest("""
        const q = fauxQuest(o);
        L.B.partie.ouvertureVue = true;
        return q.entrer().then(function () {
            const j = L.B.joueur, d = o.ligneDroite();
            j.x = d.x; j.y = d.y;
            L.B.defs.conduite.trafic.vehicules_max = 0;
            L.B.entites.filter(function (e) { return e.type === 'vehicule'; }).forEach(function (e) { L.Entites.retirer(e); });
            const v = o.char('auto', 0, 0, 0);
            L.Vehicules.monter(j, v);
            const x0 = v.x;
            q.bouton('right', 0, 1); q.image(120);
            return { vitesse: v.vitesse, avance: v.x - x0 };
        });
    """))
    assert r["vitesse"] > 0 and r["avance"] > 30, "la gachette droite est le gaz : le char doit avancer"


def test_le_clic_du_stick_gauche_met_en_pause_et_quitter_sort_du_casque(banc):
    """Le chemin entier : PAUSE, le curseur au stick droit, QUITTER VERS LE TITRE a A."""
    r = banc(quest("""
        const q = fauxQuest(o);
        L.B.partie.ouvertureVue = true;
        return q.entrer().then(function () {
            q.image(10);
            q.tape('left', 3);
            const pause = L.B.etat;
            // Le curseur part de REPRENDRE ; un cran vers le haut fait le tour
            // jusqu'a la derniere ligne.
            q.stick('right', 0, -1); q.image(3); q.stick('right', 0, 0); q.image(3);
            const ligne = L.B.menu && L.B.menu.items[L.B.menu.curseur].libelle;
            q.tape('right', 4);
            return o.attendre().then(function () {
                return { pause: pause, ligne: ligne, etat: L.B.etat, voile: L.Hud.voileCourant,
                         fini: q.session.fini, actif: L.Casque.actif, echelle: L.Base.SCALE };
            });
        });
    """))
    assert r["pause"] == "pause", "le clic du stick gauche doit mettre en pause"
    assert r["ligne"] == "QUITTER VERS LE TITRE"
    assert r["etat"] == "titre" and r["voile"] == "titre"
    assert r["fini"] is True and r["actif"] is False, \
        "l'ecran titre est du DOM : le montrer doit refermer la session du casque"
    assert r["echelle"] == 2, "hors du casque, l'echelle revient a celle de la fenetre"


def test_quitter_le_casque_par_le_systeme_ramene_au_titre_partie_sauvegardee(banc):
    """Le bouton Meta, puis QUITTER : la session finit sans que le jeu l'ait demande."""
    r = banc(quest("""
        const q = fauxQuest(o);
        L.B.partie.ouvertureVue = true;
        return q.entrer().then(function () {
            q.image(10);
            const cle = L.Sauvegarde.cle(L.Sauvegarde.emplacement());
            delete o.store[cle];
            q.session.end();
            const apres = { etat: L.B.etat, voile: L.Hud.voileCourant, actif: L.Casque.actif,
                            sauvee: cle in o.store };
            // La fenetre reprend la main : une partie relancee au clavier avance.
            L.Jeu.jouer();
            const t0 = L.B.t;
            o.frame(30);
            apres.fenetre = L.B.t - t0;
            return apres;
        });
    """))
    assert r["etat"] == "titre" and r["voile"] == "titre", \
        "hors du casque, un joueur de Quest n'a plus de manette : il doit retrouver le titre"
    assert r["sauvee"] is True, "sortir du casque ne doit rien perdre de la partie"
    assert r["actif"] is False
    assert r["fenetre"] > 0, "la boucle de la fenetre doit reprendre la simulation hors du casque"


def une_partie(paquet, jour):
    """Une partie sauvegardee comme le jeu l'ecrit : posee a l'apparition, ouverture vue."""
    app = paquet["carte"]["apparition"]["joueur"]
    return json.dumps({"version": 1, "jour": jour, "argent": 120, "x": app["x"] * 16 + 8, "y": app["y"] * 16 + 8,
                       "ouvertureVue": True, "stats": {"secondes": 600}, "missionsFaites": {}})


def test_avec_des_parties_le_casque_ouvre_leur_choix_et_s_y_joue(banc, paquet):
    """Le bouton du casque fait ce que fait JOUER : le choix des parties. C'est un
    menu de la TOILE, donc il se voit et se choisit dans le casque — a la Touch."""
    r = banc(quest("""
        const q = fauxQuest(o);
        return q.entrer().then(function () {
            q.image(4);
            const choix = { etat: L.B.etat, voile: L.Hud.voileCourant, menu: L.B.menu && L.B.menu.titre,
                            actif: L.Casque.actif };
            q.tape('right', 4);                          // A sur la partie 1
            return { choix: choix, etat: L.B.etat, jour: L.B.partie.jour, actif: L.Casque.actif };
        });
    """), stockage={"bandini-partie-v1": une_partie(paquet, 4)})
    assert r["choix"] == {"etat": "titre", "voile": None, "menu": "PARTIES", "actif": True}, \
        "avec une partie sauvegardee, entrer dans le casque doit montrer le choix des parties"
    assert r["etat"] == "jeu" and r["jour"] == 4, "A sur la partie doit la jouer"
    assert r["actif"] is True


def test_sortir_du_casque_pendant_le_choix_des_parties_rend_le_titre(banc, paquet):
    r = banc(quest("""
        const q = fauxQuest(o);
        return q.entrer().then(function () {
            q.image(4);
            const avant = L.B.menu && L.B.menu.titre;
            q.session.end();
            return { avant: avant, voile: L.Hud.voileCourant, menu: !!L.B.menu, bouton: o.elements['bouton-casque'].hidden };
        });
    """), stockage={"bandini-partie-v1": une_partie(paquet, 4)})
    assert r["avant"] == "PARTIES"
    assert r["voile"] == "titre" and r["menu"] is False, \
        "hors du casque, un menu de la toile ne se commande plus aux Touch : le titre et son bouton doivent revenir"
    assert r["bouton"] is False


def test_le_choix_rouvert_apres_un_rechargement_rend_le_titre_sur_un_quest(banc, paquet):
    """Changer de partie recharge la page, qui rouvre le choix des parties sur la
    toile. Dans le casque, la session est morte avec la page : sur un Quest, il
    faut le titre et son bouton — pas un menu qu'aucune main ne commande."""
    r = banc(quest("""
        const avant = { voile: L.Hud.voileCourant, menu: L.B.menu && L.B.menu.titre };
        fauxQuest(o);
        return L.Casque.sonder().then(function () {
            return { avant: avant, voile: L.Hud.voileCourant, menu: !!L.B.menu, bouton: o.elements['bouton-casque'].hidden };
        });
    """), stockage={"bandini-partie-v1": une_partie(paquet, 4), "bandini-partie-v1-2": une_partie(paquet, 9)},
        session={"bandini-rouvrir-parties": "2"})
    assert r["avant"] == {"voile": None, "menu": "PARTIES"}, "temoin : le rechargement rouvre bien le choix"
    assert r["voile"] == "titre" and r["menu"] is False
    assert r["bouton"] is False


def test_le_menu_du_systeme_met_le_jeu_en_pause(banc):
    r = banc(quest("""
        const q = fauxQuest(o);
        L.B.partie.ouvertureVue = true;
        return q.entrer().then(function () {
            q.image(10);
            const avant = L.B.etat;
            q.session.visibilityState = 'visible-blurred';
            q.session.emettre('visibilitychange');
            return { avant: avant, apres: L.B.etat, actif: L.Casque.actif };
        });
    """))
    assert r["avant"] == "jeu"
    assert r["apres"] == "pause", "le menu du Quest par-dessus la partie : le jeu ne doit pas tourner derriere"
    assert r["actif"] is True, "un menu du systeme ne ferme pas la session"


def test_une_main_nue_ne_touche_a_rien(banc):
    """Les manettes posees, le Quest suit les mains : un pincement ne doit pas
    faire le gaz ni aucun bouton."""
    r = banc(quest("""
        const q = fauxQuest(o);
        L.B.partie.ouvertureVue = true;
        return q.entrer().then(function () {
            q.mains.right.hand = {};
            q.mains.left.hand = {};
            q.bouton('right', 0, 1); q.bouton('left', 4, 1); q.image(4);
            return { gaz: L.Entree.gaz, attaque: L.Entree.bas('attaque'), info: L.Entree.manetteInfo().branchee };
        });
    """))
    assert r == {"gaz": 0, "attaque": False, "info": False}


def test_les_mains_tremblent_et_l_ecran_manette_les_voit(banc):
    r = banc(quest("""
        const q = fauxQuest(o);
        L.B.partie.ouvertureVue = true;
        return q.entrer().then(function () {
            q.image(4);
            L.Entree.vibrer(25);
            q.bouton('right', 4, 1); q.image(3);
            const info = L.Entree.manetteInfo();
            q.bouton('right', 4, 0); q.image(3);
            return { gauche: q.mains.left.pulses, droite: q.mains.right.pulses, info: info };
        });
    """))
    assert r["gauche"] == [25] and r["droite"] == [25], "dans le casque, la vibration passe par les Touch"
    assert r["info"]["branchee"] is True, "l'ecran MANETTE ne doit pas dire AUCUNE MANETTE a qui en tient deux"
    assert r["info"]["mapping"] == "standard" and r["info"]["id"] == "Meta Quest Touch"
    assert r["info"]["boutons"] == [0], "A enfonce doit s'allumer comme le bouton 0 d'une Xbox"


def test_dans_le_casque_b_annule_un_apprentissage(banc):
    """⚠️ Pendant qu'on reapprend un bouton, la manette Bluetooth est muette — et
    dans le casque il n'y a ni clavier ni doigt. Les Touch doivent rester vivantes,
    sinon l'ecran REAPPRENDRE enferme le joueur."""
    r = banc(quest("""
        const q = fauxQuest(o);
        L.B.partie.ouvertureVue = true;
        return q.entrer().then(function () {
            q.image(4);
            q.tape('left', 3);
            const etat = L.B.etat;
            L.Entree.apprendre('action');
            q.image(4);
            const pendant = L.Entree.apprendEnCours();
            q.tape('right', 5);
            return { etat: etat, pendant: pendant, apres: L.Entree.apprendEnCours() };
        });
    """))
    assert r["etat"] == "pause"
    assert r["pendant"] == "action"
    assert r["apres"] is None, "B sur la Touch doit annuler l'apprentissage"
