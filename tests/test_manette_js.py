"""La manette : la disposition par defaut, et celle qu'on lui reapprend.

⚠️ `o.frame(2)` apres chaque `o.pad(...)`, jamais `frame(1)` : la boucle a un pas
fixe et un accumulateur, si bien qu'une image du banc fait parfois zero `maj()`
et la suivante deux. Avec `frame(1)`, on lit l'etat de la manette d'AVANT.

⚠️ Le probleme que ces tests gardent : une manette Bluetooth que le navigateur
ne reconnait pas (`mapping: ''`) numerote ses boutons comme elle veut. La meme
manette n'a pas les memes numeros sur le telephone et sur le Mac — ca ne se
devine pas, ca se reapprend. Retour de Martin, 13 sept. 2026.
"""


def test_la_disposition_par_defaut_est_celle_d_une_manette_reconnue(banc):
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const vu = {};
        const actions = ['action', 'esquive', 'attaque', 'arme', 'carte', 'pause', 'haut', 'bas', 'gauche', 'droite', 'annuler'];
        for (let b = 0; b <= 15; b++) {
            const boutons = []; for (let k = 0; k <= 15; k++) boutons.push(k === b ? 1 : 0);
            o.pad([0, 0], boutons); o.frame(2);
            vu[b] = actions.filter(function (a) { return L.Entree.bas(a); });
        }
        o.pad(null); o.frame(2);
        return vu;
    }""")
    assert r["0"] == ["action"]
    assert set(r["1"]) == {"esquive", "annuler"}, "le bouton de droite doit aussi servir de RETOUR"
    assert r["2"] == ["attaque"] and r["5"] == ["attaque"]
    assert r["3"] == ["arme"] and r["4"] == ["arme"]
    assert r["8"] == ["carte"] and r["9"] == ["pause"]
    assert (r["12"], r["13"], r["14"], r["15"]) == (["haut"], ["bas"], ["gauche"], ["droite"])


def test_on_reapprend_un_bouton_et_il_reste_appris(banc):
    """Le geste de Martin : OPTIONS > MANETTE > ACTION, puis il appuie."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        function boutons(i) { const b = []; for (let k = 0; k <= 9; k++) b.push(k === i ? 1 : 0); return b; }
        o.pad([0, 0], boutons(-1)); o.frame(2);
        L.Entree.apprendre('action');
        o.frame(2);                                  // la manette au repos : la reference
        const pendant = { action: L.Entree.bas('action'), apprend: L.Entree.apprendEnCours() };
        o.pad([0, 0], boutons(7)); o.frame(2);       // il appuie sur 7
        const profil = L.Entree.profilManette();
        o.pad([0, 0], boutons(-1)); o.frame(2);      // il relache
        o.pad([0, 0], boutons(7)); o.frame(2);
        const surSept = L.Entree.bas('action');
        o.pad([0, 0], boutons(0)); o.frame(2);
        const surZero = L.Entree.bas('action');
        o.pad(null); o.frame(2);
        return { pendant: pendant, boutonsAction: profil.boutons.action, surSept: surSept, surZero: surZero,
                 apprend: L.Entree.apprendEnCours(), options: L.B.options.manette ? L.B.options.manette.boutons.action : null };
    }""")
    assert r["pendant"]["apprend"] == "action"
    assert r["pendant"]["action"] is False, "la manette ne commande rien pendant qu'on l'apprend"
    assert r["boutonsAction"] == [7]
    assert r["surSept"] is True, "le bouton appris ne fait pas ACTION"
    assert r["surZero"] is False, "l'ancien bouton fait encore ACTION"
    assert r["apprend"] is None


def test_le_bouton_qu_on_vient_d_apprendre_ne_valide_pas_le_menu(banc):
    """⚠️ Sinon on apprend un bouton et il choisit aussitot la ligne du menu ou
    on l'apprenait — on n'en sortirait jamais."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        function boutons(i) { const b = []; for (let k = 0; k <= 9; k++) b.push(k === i ? 1 : 0); return b; }
        o.pad([0, 0], boutons(-1)); o.frame(2);
        L.Entree.apprendre('action');
        o.frame(2);
        o.pad([0, 0], boutons(3)); o.frame(2);       // appris
        const justeApres = L.Entree.neuf('action');
        o.frame(2);                                   // toujours enfonce
        const encoreTenu = L.Entree.bas('action');
        o.pad([0, 0], boutons(-1)); o.frame(2);       // relache
        o.pad([0, 0], boutons(3)); o.frame(2);        // nouvel appui, pour de vrai
        const vraiAppui = L.Entree.bas('action');
        o.pad(null); o.frame(2);
        return { justeApres: justeApres, encoreTenu: encoreTenu, vraiAppui: vraiAppui };
    }""")
    assert r["justeApres"] is False and r["encoreTenu"] is False
    assert r["vraiAppui"] is True


def test_une_gachette_sur_un_axe_s_apprend_aussi(banc):
    """Beaucoup de manettes non reconnues rendent le gaz comme un AXE qui
    repose a -1 : on mesure son repos au moment de l'apprendre."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        o.pad([0, 0, -1, -1], [0, 0, 0, 0], { mapping: '', id: 'Bidule BT Gamepad' });
        o.frame(2);
        const info = L.Entree.manetteInfo();
        L.Entree.apprendre('gaz');
        o.frame(2);                                   // repos : axe 2 a -1
        o.pad([0, 0, 1, -1], [0, 0, 0, 0], { mapping: '' }); o.frame(2);
        const source = L.Entree.profilManette().gaz;
        const plein = L.Entree.gaz;
        o.pad([0, 0, 0, -1], [0, 0, 0, 0], { mapping: '' }); o.frame(2);
        const moitie = L.Entree.gaz;
        o.pad([0, 0, -1, -1], [0, 0, 0, 0], { mapping: '' }); o.frame(2);
        const rien = L.Entree.gaz;
        o.pad(null); o.frame(2);
        return { mapping: info.mapping, id: info.id, source: source, plein: plein, moitie: moitie, rien: rien };
    }""")
    assert r["mapping"] == "", "l'ecran MANETTE doit pouvoir dire « NON RECONNUE »"
    assert r["id"].startswith("Bidule")
    assert r["source"]["type"] == "axe" and r["source"]["i"] == 2 and r["source"]["repos"] == -1
    assert r["plein"] == 1 and r["rien"] == 0
    assert 0.4 < r["moitie"] < 0.6


def test_l_ecran_manette_dit_ce_que_la_manette_dit_d_elle_meme(banc):
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        o.pad([0, 0], [0, 0, 1, 0], { mapping: '', id: 'Bidule BT Gamepad' }); o.frame(2);
        const m = L.Hud.menuManette();
        m.maj(m);
        const inconnue = { sur: m.sur, aide: m.aide };
        o.pad([0, 0], [1, 0, 0, 0], { mapping: 'standard', id: 'Xbox Wireless' }); o.frame(2);
        m.maj(m);
        o.pad(null); o.frame(2);
        return { inconnue: inconnue, reconnue: m.sur,
                 profils: m.items.filter(function (i) { return i.profil; }).map(function (i) { return i.profil.slug; }) };
    }""")
    assert r["inconnue"]["sur"] == "NON RECONNUE"
    assert "ALLUMER" in r["inconnue"]["aide"], "l'ecran doit dire comment se verifier"
    assert r["reconnue"] == "RECONNUE"
    assert r["profils"][0] == "standard" and len(r["profils"]) >= 3


def test_choisir_une_disposition_la_pose_et_la_garde(banc):
    """Le geste que Martin demandait : on choisit sa manette dans une liste.

    ⚠️ Et le test du retour qu'il a fait : en DirectInput, les GACHETTES sont
    les boutons 8 et 9 — ceux qui, sur une manette reconnue, ouvrent la carte
    et la pause. C'est exactement ce qui lui arrivait."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        function boutons(i) { const b = []; for (let k = 0; k <= 11; k++) b.push(k === i ? 1 : 0); return b; }
        function lit(i) {
            o.pad([0, 0], boutons(i)); o.frame(2);
            return { actions: ['action', 'attaque', 'esquive', 'arme', 'carte', 'pause']
                       .filter(function (a) { return L.Entree.bas(a); }),
                     gaz: L.Entree.gaz, frein: L.Entree.frein };
        }
        const m = L.Hud.menuManette();
        const avant = { huit: lit(8).actions, neuf: lit(9).actions };
        m.items.find(function (i) { return i.profil && i.profil.slug === 'bt_dinput'; }).faire();
        const apres = { huit: lit(8), neuf: lit(9), dix: lit(10).actions, onze: lit(11).actions,
                        zero: lit(0).actions, trois: lit(3).actions };
        m.maj(m);
        const marque = m.items.filter(function (i) { return i.detail === 'CHOISIE'; }).map(function (i) { return i.profil.slug; });
        // Rouvrir l'ecran pose le curseur sur la disposition en cours : appuyer
        // sur ACTION pour voir le bouton s'allumer ne change alors rien.
        const curseur = L.Hud.menuManette();
        const surLaSienne = curseur.items[curseur.curseur].profil.slug;
        m.items.find(function (i) { return i.profil && i.profil.slug === 'standard'; }).faire();
        const retour = lit(8).actions;
        o.pad(null); o.frame(2);
        return { avant: avant, apres: apres, marque: marque, retour: retour,
                 surLaSienne: surLaSienne, garde: L.B.options.manetteProfil };
    }""")
    assert r["avant"]["huit"] == ["carte"] and r["avant"]["neuf"] == ["pause"], \
        "le symptome de Martin : les gachettes ouvrent la carte et la pause"
    assert r["apres"]["huit"]["actions"] == [] and r["apres"]["huit"]["frein"] == 1
    assert r["apres"]["neuf"]["actions"] == [] and r["apres"]["neuf"]["gaz"] == 1
    assert r["apres"]["dix"] == ["carte"] and r["apres"]["onze"] == ["pause"]
    assert r["apres"]["zero"] == ["action"] and r["apres"]["trois"] == ["attaque"]
    assert r["marque"] == ["bt_dinput"], "la disposition choisie doit se voir dans la liste"
    assert r["surLaSienne"] == "bt_dinput", "le curseur doit s'ouvrir sur la sienne"
    assert r["retour"] == ["carte"], "revenir a STANDARD remet tout comme avant"
    assert r["garde"] == "standard"


def test_la_disposition_a_croix_sur_un_axe_marche_sans_rien_apprendre(banc):
    """⚠️ Le cas de la 8BitDo en Bluetooth : on choisit la disposition, et la
    croix repond tout de suite — diagonales comprises, sans un seul geste."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        function hat(v) { o.pad([0, 0, 0, 0, 0, 0, 0, 0, 0, v], [0, 0, 0, 0], { mapping: '' }); }
        function dirs() { return ['haut', 'bas', 'gauche', 'droite'].filter(function (a) { return L.Entree.bas(a); }); }
        const m = L.Hud.menuManette();
        hat(1.2857142857142858); o.frame(2);
        const avant = (function () { hat(-1); o.frame(2); return dirs(); })();
        m.items.find(function (i) { return i.profil && i.profil.slug === 'bt_croix_axe'; }).faire();
        const lu = {};
        const pos = { haut: -1, bas: 0.14285714285714285, gauche: 0.7142857142857143,
                      droite: -0.42857142857142855, diagonale: -0.7142857142857143,
                      repos: 1.2857142857142858 };
        for (const nom in pos) { hat(pos[nom]); o.frame(2); lu[nom] = dirs(); }
        o.pad(null); o.frame(2);
        return { avant: avant, lu: lu };
    }""")
    assert r["avant"] == [], "avant de choisir, la croix-axe ne fait rien"
    assert r["lu"]["haut"] == ["haut"] and r["lu"]["bas"] == ["bas"]
    assert r["lu"]["gauche"] == ["gauche"] and r["lu"]["droite"] == ["droite"]
    assert sorted(r["lu"]["diagonale"]) == ["droite", "haut"]
    assert r["lu"]["repos"] == []


def test_tout_reapprendre_enchaine_les_onze_gestes(banc):
    """⚠️ Le vrai geste quand rien ne repond : TOUT REAPPRENDRE, et le jeu
    demande un bouton apres l'autre. La croix compte pour quatre."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        function boutons(i) { const b = []; for (let k = 0; k <= 15; k++) b.push(k === i ? 1 : 0); return b; }
        o.pad([0, 0], boutons(-1)); o.frame(2);
        const m = L.Hud.menuManetteBoutons();
        m.items.find(function (i) { return i.libelle === 'TOUT RÉAPPRENDRE'; }).faire();
        const demandes = [];
        // On appuie sur 15, 14, 13... : chaque geste doit etre pris par l'action suivante.
        for (let n = 0; n < 15; n++) {
            demandes.push(L.Entree.apprendEnCours());
            if (!L.Entree.apprendEnCours()) break;
            o.pad([0, 0], boutons(-1)); o.frame(2);          // repos
            o.pad([0, 0], boutons(15 - n)); o.frame(2);      // il appuie
        }
        const profil = L.Entree.profilManette();
        o.pad(null); o.frame(2);
        return { demandes: demandes, action: profil.boutons.action, attaque: profil.boutons.attaque,
                 haut: profil.boutons.haut, droite: profil.boutons.droite,
                 fini: L.Entree.apprendEnCours(), garde: !!L.B.options.manette };
    }""")
    assert r["demandes"][:5] == ["action", "attaque", "esquive", "arme", "annuler"]
    assert "verrouiller" not in r["demandes"], "VISER est la gachette du gaz : rien a reapprendre"
    assert "haut" in r["demandes"] and "bas" in r["demandes"], "la croix s'apprend en quatre gestes"
    assert r["action"] == [15] and r["attaque"] == [14]
    assert r["fini"] is None, "la file doit finir"
    assert r["garde"] is True, "le profil appris doit etre garde dans les options"


def test_on_commence_la_partie_a_la_manette(banc):
    """⚠️ « Jouer » n'etait qu'un bouton de la page : sans toucher l'ecran, on
    ne pouvait pas commencer — ni a la manette, ni au clavier."""
    r = banc("""function (L, o) {
        const avant = L.B.etat;                       // le banc demarre au titre
        o.pad([0, 0], [1, 0]); o.frame(2);            // bouton ACTION
        const apad = L.B.etat;
        o.pad(null); o.frame(2);
        return { avant: avant, apad: apad, voile: L.Hud.voileCourant };
    }""")
    assert r["avant"] == "titre"
    assert r["apad"] == "jeu", "le bouton ACTION de la manette doit lancer la partie"
    assert r["voile"] is None


def test_on_commence_la_partie_au_clavier(banc):
    r = banc("""function (L, o) {
        const avant = L.B.etat;
        o.tape('Enter', 2);
        return { avant: avant, apres: L.B.etat };
    }""")
    assert r["avant"] == "titre" and r["apres"] == "jeu"


def test_la_croix_chapeau_s_apprend_et_le_tour_se_deduit(banc):
    """⚠️ Le cas 8BitDo en Bluetooth : la croix n'est pas quatre boutons mais UN
    AXE. On appuie dessus et aucun numero ne s'allume — la croix a l'air morte.

    On apprend HAUT puis DROITE, et le tour complet se deduit : les huit
    positions sont regulierement espacees, diagonales comprises. BAS et GAUCHE
    marchent sans qu'on les ait appris.
    """
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const REPOS = 1.2857142857142858;            // le chapeau au repos, hors de l'anneau
        function hat(v) { o.pad([0, 0, 0, 0, 0, 0, 0, 0, 0, v], [0, 0, 0, 0]); }
        function dirs() {
            return ['haut', 'bas', 'gauche', 'droite'].filter(function (a) { return L.Entree.bas(a); });
        }
        hat(REPOS); o.frame(2);
        // Aucun bouton ne s'allume quand on appuie sur la croix : le symptome.
        hat(-1); o.frame(2);
        const avant = { dirs: dirs(), boutons: L.Entree.manetteInfo().boutons.slice() };
        // On l'apprend : HAUT, puis DROITE.
        hat(REPOS); o.frame(2);
        L.Entree.apprendre('haut'); o.frame(2);
        hat(-1); o.frame(2);
        hat(REPOS); o.frame(2);
        L.Entree.apprendre('droite'); o.frame(2);
        hat(-0.42857142857142855); o.frame(2);
        const profil = L.Entree.profilManette();
        const lu = {};
        const positions = { haut: -1, diagonale: -0.7142857142857143, droite: -0.42857142857142855,
                            bas: 0.14285714285714285, gauche: 0.7142857142857143, repos: REPOS };
        for (const nom in positions) { hat(positions[nom]); o.frame(2); lu[nom] = dirs(); }
        o.pad(null); o.frame(2);
        return { avant: avant, croix: profil.croix, lu: lu };
    }""")
    assert r["avant"]["dirs"] == [], "la croix-chapeau ne doit rien faire avant d'etre apprise"
    assert r["avant"]["boutons"] == [], "aucun bouton ne s'allume : c'est bien un axe"
    assert r["croix"]["i"] == 9
    assert sorted(r["croix"]["valeurs"]) == ["droite", "haut"]
    assert r["lu"]["haut"] == ["haut"] and r["lu"]["droite"] == ["droite"]
    assert sorted(r["lu"]["diagonale"]) == ["droite", "haut"], "la diagonale doit sortir du tour"
    assert r["lu"]["bas"] == ["bas"], "BAS se deduit sans l'avoir appris"
    assert r["lu"]["gauche"] == ["gauche"], "GAUCHE se deduit sans l'avoir appris"
    assert r["lu"]["repos"] == [], "au repos, la croix ne doit rien tenir"


def test_une_croix_chapeau_a_moitie_apprise_ne_ment_pas(banc):
    """Une seule direction apprise : elle marche, et rien d'autre ne s'invente."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        function hat(v) { o.pad([0, 0, 0, 0, 0, 0, 0, 0, 0, v], [0, 0, 0, 0]); }
        function dirs() { return ['haut', 'bas', 'gauche', 'droite'].filter(function (a) { return L.Entree.bas(a); }); }
        hat(1.2857142857142858); o.frame(2);
        L.Entree.apprendre('haut'); o.frame(2);
        hat(-1); o.frame(2);
        const surHaut = dirs();
        hat(0.14285714285714285); o.frame(2);
        const surBas = dirs();
        o.pad(null); o.frame(2);
        return { surHaut: surHaut, surBas: surBas };
    }""")
    assert r["surHaut"] == ["haut"]
    assert r["surBas"] == [], "sans DROITE, le tour est inconnu : on n'invente pas BAS"


def test_relacher_la_croix_n_est_pas_un_geste(banc):
    """⚠️ Sur une croix-chapeau, LACHER le haut fait bouger l'axe autant
    qu'appuyer sur le bas. Sans garde, « tout reapprendre » apprenait la
    direction suivante sur la valeur du REPOS — et la croix tenait alors les
    quatre directions enfoncees en permanence."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const REPOS = 1.2857142857142858;
        function hat(v) { o.pad([0, 0, 0, 0, 0, 0, 0, 0, 0, v], [0, 0, 0, 0]); }
        function dirs() { return ['haut', 'bas', 'gauche', 'droite'].filter(function (a) { return L.Entree.bas(a); }); }
        const m = L.Hud.menuManetteBoutons();
        // ⚠️ Une demi-seconde au repos : c'est la que le jeu mesure le repos de
        // la croix. Dans la vraie vie, ouvrir le menu prend bien plus que ca.
        hat(REPOS); o.frame(40);
        m.items.find(function (i) { return i.quoi === 'croix'; }).faire();
        const suite = [];
        const gestes = [-1, 0.14285714285714285, 0.7142857142857143, -0.42857142857142855];
        for (const v of gestes) {
            suite.push(L.Entree.apprendEnCours());
            hat(REPOS); o.frame(2);                  // le temps de bouger le pouce
            hat(v); o.frame(2);                      // il appuie
            hat(REPOS); o.frame(2);                  // il relache : ca ne doit RIEN apprendre
        }
        const croix = L.Entree.profilManette().croix;
        const lu = {};
        hat(REPOS); o.frame(2); lu.repos = dirs();
        hat(-1); o.frame(2); lu.haut = dirs();
        hat(0.14285714285714285); o.frame(2); lu.bas = dirs();
        o.pad(null); o.frame(2);
        return { suite: suite, croix: croix, lu: lu, fini: L.Entree.apprendEnCours() };
    }""")
    assert r["suite"] == ["haut", "bas", "gauche", "droite"], "la file doit avancer d'un cran par geste"
    assert r["croix"]["i"] == 9
    assert sorted(r["croix"]["valeurs"]) == ["bas", "droite", "gauche", "haut"]
    assert abs(r["croix"]["valeurs"]["haut"] + 1) < 0.01, r["croix"]["valeurs"]
    assert abs(r["croix"]["valeurs"]["bas"] - 0.142857) < 0.01, "BAS appris sur le repos"
    assert r["lu"]["repos"] == [], "au repos la croix ne tient rien"
    assert r["lu"]["haut"] == ["haut"] and r["lu"]["bas"] == ["bas"]
    assert r["fini"] is None


def test_la_direction_suivante_attend_qu_on_relache(banc):
    """Le detail qui fait toute la difference dans l'enchainement : tant que la
    croix est tenue, l'apprentissage suivant ATTEND — il ne prend pas le
    relachement pour le geste."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const REPOS = 1.2857142857142858;
        function hat(v) { o.pad([0, 0, 0, 0, 0, 0, 0, 0, 0, v], [0, 0, 0, 0]); }
        hat(REPOS); o.frame(40);                      // le repos se mesure
        L.Entree.apprendre('haut', function () { L.Entree.apprendre('bas'); });
        o.frame(2);
        hat(-1); o.frame(2);                          // HAUT appris, BAS enchaine
        const tenu = { quoi: L.Entree.apprendEnCours(), attend: L.Entree.manetteInfo().attend,
                       valeurs: Object.keys(L.Entree.profilManette().croix.valeurs) };
        hat(REPOS); o.frame(2);                       // il relache
        const apresRelache = Object.keys(L.Entree.profilManette().croix.valeurs);
        hat(0.14285714285714285); o.frame(2);         // il appuie vraiment sur BAS
        const valeurs = L.Entree.profilManette().croix.valeurs;
        o.pad(null); o.frame(2);
        return { tenu: tenu, apresRelache: apresRelache, valeurs: valeurs };
    }""")
    assert r["tenu"]["quoi"] == "bas" and r["tenu"]["attend"] is True
    assert r["tenu"]["valeurs"] == ["haut"]
    assert r["apresRelache"] == ["haut"], "le relachement a ete pris pour un geste"
    assert abs(r["valeurs"]["bas"] - 0.142857) < 0.01


def test_le_dessin_allume_le_bouton_qu_on_appuie(banc):
    """⚠️ C'est toute la promesse de l'ecran : le dessin est une PREUVE. Le
    bouton d'epaule et le bouton de droite servent la meme action — s'ils
    s'allumaient ensemble, on ne pourrait rien verifier du tout."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const m = L.Hud.menuManette();
        m.items.find(function (i) { return i.profil && i.profil.slug === 'standard'; }).faire();
        function ors(boutons) {
            o.pad([0, 0], boutons, { mapping: 'standard' }); o.frame(2);
            const vus = [];
            const ctx = { fillStyle: '', fillRect: function (x, y, l, h) {
                if (this.fillStyle === '#e8b33c') vus.push([x, y, l, h].join(','));
            }, drawImage: function () {} };
            m.dessiner(ctx, 0, 0, 420, 162);
            return vus;
        }
        function b(i) { const t = []; for (let k = 0; k <= 9; k++) t.push(k === i ? 1 : 0); return t; }
        return { rien: ors(b(-1)), zero: ors(b(0)), cinq: ors(b(5)), deux: ors(b(2)), sept: ors(b(7)) };
    }""")
    # Origine du dessin : x + 232, y + 24, a l'echelle 2.
    def piece(x, y, largeur, hauteur):
        return f"{232 + x * 2},{24 + y * 2},{largeur * 2},{hauteur * 2}"

    assert r["rien"] == [], "rien d'allume quand rien n'est enfonce"
    assert r["zero"] == [piece(59, 24, 5, 5)], "le bouton du bas"
    assert r["cinq"] == [piece(52, 5, 18, 5)], "l'epaule droite, PAS le bouton de gauche"
    assert r["deux"] == [piece(54, 19, 5, 5)], "le bouton de gauche, PAS l'epaule droite"
    assert r["sept"] == [piece(54, 0, 14, 4)], "la gachette droite (le gaz)"


def test_la_manette_ne_ferme_pas_l_ecran_sous_ses_doigts(banc):
    """On y appuie sur ses boutons pour les VOIR : si FRAPPE ou START fermaient
    l'ecran, on ne pourrait pas les essayer. Le clavier, lui, recule — vers
    OPTIONS, l'onglet d'ou l'ecran s'ouvre (c'est une sous-page du classeur)."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        L.Hud.ouvrirMenu(L.Hud.menuManette());
        function b(i) { const t = []; for (let k = 0; k <= 9; k++) t.push(k === i ? 1 : 0); return t; }
        const etapes = [];
        for (const i of [2, 1, 9]) {                 // FRAPPE, RETOUR, PAUSE
            o.pad([0, 0], b(i), { mapping: 'standard' }); o.frame(2);
            etapes.push(!!L.B.menu);
            o.pad([0, 0], b(-1)); o.frame(2);
        }
        o.pad(null); o.frame(2);
        o.tape('Space', 2);                          // FRAPPE au clavier : ca, ca recule
        return { etapes: etapes, apresClavier: L.B.menu && L.B.menu.titre };
    }""")
    assert r["etapes"] == [True, True, True], "un bouton de manette a ferme l'ecran"
    assert r["apresClavier"] == "OPTIONS", "le clavier doit pouvoir reculer"


def test_un_bouton_hors_disposition_se_dit_au_lieu_de_ne_rien_faire(banc):
    """⚠️ Un bouton que la disposition ne connait pas n'allume rien sur le
    dessin — on croirait la manette morte. L'ecran doit le nommer : c'est le
    signe qu'il faut une autre disposition."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const m = L.Hud.menuManette();
        m.items.find(function (i) { return i.profil && i.profil.slug === 'standard'; }).faire();
        function lignes(i) {
            const b = []; for (let k = 0; k <= 11; k++) b.push(k === i ? 1 : 0);
            o.pad([0, 0], b, { mapping: '' }); o.frame(2);
            const vues = [];
            const ctx = { fillStyle: '', fillRect: function () {}, drawImage: function () {} };
            const vraiTexte = L.Atlas.texte;
            L.Atlas.texte = function (c, s) { vues.push(s); };
            m.dessiner(ctx, 0, 0, 420, 162);
            L.Atlas.texte = vraiTexte;
            return vues;
        }
        const connu = lignes(0), inconnu = lignes(11);
        o.pad(null); o.frame(2);
        return { connu: connu, inconnu: inconnu };
    }""")
    assert any("ENFONCÉS : 0" in s for s in r["connu"])
    assert not any("PAS DANS CELLE-CI" in s for s in r["connu"]), "le bouton 0 est connu"
    assert any("BOUTON 11 : PAS DANS CELLE-CI" in s for s in r["inconnu"])
