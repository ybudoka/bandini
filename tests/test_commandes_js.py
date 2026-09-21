"""L'ecran COMMANDES : l'aide du debut de partie, avec les boutons qu'on TIENT.

Demande de Martin (21 sept. 2026) : « au debut du jeu, un affichage d'aides pour
que les joueurs sachent comment ca fonctionne ; si une manette est branchee,
indiquer visuellement sur quel bouton peser ». Ces juges gardent ce que l'ecran
PROMET — qu'il s'ouvre quand on prend le bonhomme, qu'il parle l'appareil qu'on
tient, qu'on y essaie ses boutons sans le fermer. Ce qu'il MONTRE (les traits, les
lettres a la bonne place, rien sous un pouce) se juge a la capture et dans
`test_navigateur.py`.

⚠️ `o.frame(2)` apres chaque `o.pad(...)` (voir `test_manette_js.py`).
"""

#: La 8BitDo de Martin en Bluetooth : non reconnue, croix sur l'axe 9, et un nom
#: de manette Nintendo — alors qu'elle porte les lettres Xbox.
MARTIN = "Pro Controller (Vendor: 057e Product: 2009)"
XBOX = "Xbox Wireless Controller (STANDARD GAMEPAD Vendor: 045e Product: 0b13)"
DS4 = "Wireless Controller (STANDARD GAMEPAD Vendor: 054c Product: 09cc)"

NOUVELLE_PARTIE = """
    L.Jeu.retourTitre();
    L.B.partie.x = null; L.B.partie.y = null; L.B.partie.ouvertureVue = false;
"""


def test_la_fin_de_l_ouverture_ouvre_les_commandes_et_action_rend_la_ville(banc):
    """⚠️ Au moment ou on REND le bonhomme : la scene finie, pas avant. Et
    l'ecran fige la ville — personne ne se fait renverser en lisant ou est le
    frein. ACTION (ce que dit le pied de l'ecran) rend la main, et on marche :
    juge PAR LE BOUTON, pas par `fermerMenu`."""
    r = banc("""function (L, o) {""" + NOUVELLE_PARTIE + """
        L.Jeu.jouer();
        let n = 0;
        while (L.B.ouverture && n < 3000) { o.frame(1); n++; }
        const ouvert = { titre: L.B.menu && L.B.menu.titre, bouton: L.B.menu && L.B.menu.items[0].libelle };
        const t0 = L.B.t; o.frame(30);
        const fige = L.B.t === t0;
        o.tape('KeyE', 2);
        const ferme = !L.B.menu;
        let bouge = 0;
        ['KeyW', 'KeyS', 'KeyA', 'KeyD'].forEach(function (touche) {
            const x0 = L.B.joueur.x, y0 = L.B.joueur.y;
            o.tape(touche, 20);
            if (Math.hypot(L.B.joueur.x - x0, L.B.joueur.y - y0) >= 1) bouge++;
        });
        return { ouvert: ouvert, fige: fige, ferme: ferme, bouge: bouge };
    }""")
    assert r["ouvert"] == {"titre": "COMMANDES", "bouton": "C'EST PARTI"}, r["ouvert"]
    assert r["fige"] is True, "la ville attend qu'on ait lu"
    assert r["ferme"] is True, "ACTION ferme l'aide : c'est ce que dit le pied de l'ecran"
    assert r["bouge"] >= 1, "et les commandes sont rendues"


def test_l_aide_ne_revient_qu_a_une_partie_neuve(banc):
    """Celui qui joue depuis trois jours n'a pas besoin qu'on lui reexplique le
    frein a chaque chargement ; celui qui revoit l'ouverture du carnet non plus.
    Mais une partie neuve dont l'ouverture ne peut pas jouer a quand meme ses
    commandes."""
    r = banc("""function (L, o) {
        // Une partie en cours : une position dans la ville.
        L.Jeu.retourTitre();
        L.B.partie.ouvertureVue = false; L.B.partie.x = 900; L.B.partie.y = 900;
        L.Jeu.jouer();
        const enCours = L.B.menu && L.B.menu.titre;
        // La revue du carnet.
        L.Jeu.retourTitre(); L.Jeu.commencer();
        L.Histoire.ouverture(true);
        let n = 0;
        while (L.B.ouverture && n < 3000) { o.frame(1); n++; }
        const revue = L.B.menu && L.B.menu.titre;
        // Une partie neuve sans rue devant le terminus : pas d'ouverture possible.
        L.Jeu.retourTitre();
        L.B.partie.x = null; L.B.partie.y = null; L.B.partie.ouvertureVue = false;
        const vraie = L.Histoire.ouverture;
        L.Histoire.ouverture = function () { return false; };
        L.Jeu.jouer();
        L.Histoire.ouverture = vraie;
        return { enCours: enCours || null, revue: revue || null, sansOuverture: L.B.menu && L.B.menu.titre };
    }""")
    assert r["enCours"] is None
    assert r["revue"] is None
    assert r["sansOuverture"] == "COMMANDES"


def test_la_manette_de_martin_allume_ce_qu_on_touche_et_seul_action_ferme(banc):
    """Le cas qui compte : sa 8BitDo en Bluetooth, disposition DirectInput, croix
    sur un axe. On appuie : la LIGNE de ce bouton s'allume, et l'ecran reste —
    B (RETOUR partout ailleurs) et START compris, sinon on le ferme en essayant
    le premier bouton. La croix tourne la page ; A ferme."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const bloc = L.B.defs.manettes;
        L.Entree.reglerManette(bloc.profils.find(function (q) { return q.slug === 'bt_dinput'; }));
        L.B.options.manetteProfil = 'bt_dinput';
        const repos = [0, 0, 0, 0, 0, 0, 0, 0, 0, 1.2857];
        function pad(boutons, axes) {
            const b = []; for (let k = 0; k <= 11; k++) b.push(boutons.indexOf(k) >= 0 ? 1 : 0);
            o.pad(axes || repos, b, { id: '""" + MARTIN + """', mapping: '' }); o.frame(2);
        }
        pad([]);
        L.Hud.ouvrirCommandes();
        o.frame(2);
        function allumees() {
            return L.Hud.lignesDAide(bloc.pages[L.B.menu.page], 'manette')
                .filter(function (li) { return li.allume; }).map(function (li) { return li.c; });
        }
        const vu = {};
        [1, 3, 4, 6, 7, 10, 11].forEach(function (b) {
            pad([b]); vu[b] = { allumees: allumees(), ouvert: !!L.B.menu }; pad([]);
        });
        // Le stick allume MARCHER — et ne tourne pas la page sous le pouce.
        const stick = repos.slice(); stick[0] = 0.9;
        pad([], stick); vu.stick = { allumees: allumees(), page: L.B.menu.page }; pad([]);
        const page0 = L.B.menu.page;
        const droite = repos.slice(); droite[9] = -1 + 4 / 7;         // le chapeau, a droite
        pad([], droite); pad([]);
        const page1 = L.B.menu.page;
        pad([9]); const gaz = allumees(); pad([]);
        const viser = L.Hud.lignesDAide(bloc.pages[0], 'manette').find(function (li) { return li.c === 'verrouiller'; });
        pad([0]); const ferme = !L.B.menu; pad([]);
        return { vu: vu, page0: page0, page1: page1, gaz: gaz, ferme: ferme,
                 viser: viser.glyphes[0].texte, lettre: L.Hud.glypheDAction('action').texte,
                 appareil: L.Entree.appareil };
    }""")
    vu = r["vu"]
    attendu = {"1": "esquive", "3": "attaque", "4": "arme", "6": "arme", "7": "attaque",
               "10": "carte", "11": "pause"}
    for bouton, action in attendu.items():
        assert vu[bouton]["allumees"] == [action], (bouton, vu[bouton])
        assert vu[bouton]["ouvert"] is True, f"le bouton {bouton} a ferme l'aide"
    assert vu["stick"] == {"allumees": ["marcher"], "page": 0}, vu["stick"]
    assert (r["page0"], r["page1"]) == (0, 1), "la croix-chapeau tourne la page"
    assert r["gaz"] == ["gaz"], "au volant, sa gachette 9 est le gaz"
    assert r["ferme"] is True
    assert r["viser"] == "BOUTON 2", "un numero que rien ne situe se dit par son numero"
    assert r["lettre"] == "A", "« Pro Controller » ne fait pas une Nintendo : ses lettres sont Xbox"
    assert r["appareil"] == "manette"


def test_l_appareil_est_le_dernier_qui_a_servi(banc):
    """⚠️ Pas « une manette est branchee » : celui qui tape au clavier avec une
    manette qui dort sur le bureau lit ses touches, pas des A et des B. Et une
    manette qui DERIVE (stick a 0,3) ou qui rend un bouton enfonce en permanence
    ne reprend pas la main a chaque image : il faut un geste neuf."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const vu = [L.Entree.appareil];
        o.pad([0, 0], [0, 0]); o.frame(2); vu.push(L.Entree.appareil);     // branchee, rien d'autre
        o.tape('KeyW', 2); vu.push(L.Entree.appareil);
        o.frame(10); vu.push(L.Entree.appareil);                            // elle dort : le clavier garde
        o.pad([0.3, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1]); o.frame(2);  // derive + bouton coince
        o.tape('KeyW', 2); o.frame(10); vu.push(L.Entree.appareil);        // ... le clavier garde encore
        o.pad([0, 0], [0, 0]); o.frame(2);
        o.pad([0, 0], [0, 1]); o.frame(2); vu.push(L.Entree.appareil);
        o.pad([0, 0], [0, 0]); o.frame(2);
        o.bouton('esquive', 'pointerdown'); o.frame(2); vu.push(L.Entree.appareil);
        o.bouton('esquive', 'pointerup'); o.frame(2);
        o.tape('KeyW', 2); vu.push(L.Entree.appareil);
        o.pad(null); o.frame(2);
        return vu;
    }""")
    assert r == ["clavier", "manette", "clavier", "clavier", "clavier", "manette", "tactile", "clavier"], r


def test_les_lettres_suivent_la_famille_de_la_manette(banc):
    """Xbox par defaut, PlayStation a son fabricant (054c) — et une « Xbox
    Wireless Controller » n'est PAS une DualShock « Wireless Controller » : vu a
    la capture, une croix bleue sous le A. Nintendo ne se devine pas, elle se
    choisit (OPTIONS > MANETTE > LETTRES)."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        function lettre(id) {
            o.pad([0, 0], [0, 1], { id: id }); o.frame(2);
            o.pad([0, 0], [0, 0], { id: id }); o.frame(2);
            const g = L.Hud.glypheDAction('action');
            return g.texte || g.forme;
        }
        const vu = {
            xbox: lettre('""" + XBOX + """'),
            ds4: lettre('""" + DS4 + """'),
            dualsense: lettre('DualSense Wireless Controller (STANDARD GAMEPAD Vendor: 054c Product: 0ce6)'),
            martin: lettre('""" + MARTIN + """'),
        };
        L.B.options.lettresManette = 'nintendo'; vu.nintendo = lettre('""" + XBOX + """');
        L.B.options.lettresManette = 'playstation'; vu.forcee = lettre('""" + XBOX + """');
        L.B.options.lettresManette = null;
        o.pad(null); o.frame(2);
        return vu;
    }""")
    assert r == {"xbox": "A", "ds4": "croix", "dualsense": "croix", "martin": "A",
                 "nintendo": "B", "forcee": "croix"}, r


def test_l_invite_montre_le_bouton_de_l_appareil(banc):
    """« ACTION : ENTRER » ne dit a personne sur quoi peser : a la manette, le A ;
    au clavier, la touche E ; au doigt, le bouton s'appelle ACTION et le mot reste.
    Le texte de l'invite, lui, ne change pas (cent juges le lisent)."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const vu = {};
        o.tape('KeyW', 2);
        vu.clavier = L.Hud.glypheDAction('action');
        o.pad([0, 0], [0, 1]); o.frame(2); o.pad([0, 0], [0, 0]); o.frame(2);
        vu.manette = L.Hud.glypheDAction('action');
        o.pad(null); o.frame(2);
        o.bouton('esquive', 'pointerdown'); o.frame(2); o.bouton('esquive', 'pointerup'); o.frame(2);
        vu.tactile = L.Hud.glypheDAction('action');
        // Et l'invite se dessine, au doigt comme ailleurs.
        L.B.invite = 'ENTRER'; L.Hud.dessiner();
        return { clavier: vu.clavier && vu.clavier.code, manette: vu.manette && vu.manette.texte,
                 tactile: vu.tactile, invite: L.Hud.ancres().some(function (a) { return a.nom === 'invite'; }) };
    }""")
    assert r == {"clavier": "KeyE", "manette": "A", "tactile": None, "invite": True}, r


def test_chaque_ligne_a_son_bouton_sur_chaque_appareil(banc):
    """Une ligne qu'un appareil ne sait pas faire ne s'y montre pas — et c'est
    la SEULE raison d'en retirer une : le son ne se coupe qu'au clavier, le
    doigt n'a ni carte ni verrouillage."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const bloc = L.B.defs.manettes, vu = {};
        bloc.profils.forEach(function (p) {
            L.Entree.reglerManette(p); L.B.options.manetteProfil = p.slug;
            bloc.pages.forEach(function (page) {
                ['manette', 'clavier', 'tactile'].forEach(function (app) {
                    vu[p.slug + '/' + page.slug + '/' + app] = L.Hud.lignesDAide(page, app)
                        .filter(function (li) { return li.glyphes.length; }).map(function (li) { return li.c; });
                });
            });
        });
        L.Entree.reglerManette(null); L.B.options.manetteProfil = null;
        return { vu: vu, pages: bloc.pages.map(function (p) { return [p.slug, p.lignes.map(function (l) { return l.c; })]; }) };
    }""")
    manque = {"manette": {"muet"}, "clavier": set(), "tactile": {"verrouiller", "carte", "muet"}}
    pages = dict((slug, lignes) for slug, lignes in r["pages"])
    for cle, lignes in r["vu"].items():
        _, page, appareil = cle.split("/")
        attendu = [c for c in pages[page] if c not in manque[appareil]]
        assert lignes == attendu, (cle, lignes)


def test_pause_commandes_et_retour(banc):
    """PAUSE > COMMANDES : RETOUR (Effacer, B) revient a la PAUSE, et PAUSE
    reprend le jeu — la regle de tous les sous-menus de la pause. Ouverte au
    volant, l'aide s'ouvre sur la page du volant."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        L.Jeu.pause();
        const lignes = L.B.menu.items.map(function (i) { return i.libelle; });
        L.B.menu.items.find(function (i) { return i.libelle === 'COMMANDES'; }).faire();
        const ouvert = { titre: L.B.menu.titre, bouton: L.B.menu.items[0].libelle, page: L.B.menu.page };
        o.tape('Backspace', 2);
        const retour = L.B.menu && L.B.menu.titre;
        L.B.menu.items.find(function (i) { return i.libelle === 'COMMANDES'; }).faire();
        o.tape('Escape', 2);
        const repris = L.B.etat;
        L.B.joueur.dansVehicule = true;
        const auVolant = L.Hud.menuCommandes(true).page;
        L.B.joueur.dansVehicule = null;
        return { lignes: lignes, ouvert: ouvert, retour: retour, repris: repris,
                 auVolant: L.B.defs.manettes.pages[auVolant].slug };
    }""")
    assert "COMMANDES" in r["lignes"]
    assert r["ouvert"] == {"titre": "COMMANDES", "bouton": "RETOUR", "page": 0}
    assert r["retour"] == "PAUSE"
    assert r["repris"] == "jeu"
    assert r["auVolant"] == "volant"


def test_le_titre_parle_la_manette_qu_on_tient(banc):
    """La ligne d'aide du titre disait WASD a qui tient une manette. Elle suit
    maintenant l'appareil, avec les lettres de SA manette."""
    r = banc("""function (L, o) {
        L.Jeu.retourTitre(); o.frame(2);
        const e = o.elements;
        function etat() {
            return { clavier: !e['aide-clavier'].hidden, manette: !e['aide-manette'].hidden,
                     jouer: e['aide-manette-jouer'].textContent, pause: e['aide-manette-pause'].textContent };
        }
        const vu = { avant: etat() };
        function appui(id) {
            o.pad([0, 0], [0, 1], { id: id }); o.frame(2);
            o.pad([0, 0], [0, 0], { id: id }); o.frame(2);
        }
        appui('""" + XBOX + """'); vu.xbox = etat();
        appui('""" + DS4 + """'); vu.ds4 = etat();
        o.pad(null); o.frame(2);
        o.tape('KeyW', 2); vu.clavier = etat();
        return vu;
    }""")
    assert r["avant"]["clavier"] is True and r["avant"]["manette"] is False
    assert r["xbox"] == {"clavier": False, "manette": True, "jouer": "A", "pause": "START"}, r["xbox"]
    assert (r["ds4"]["jouer"], r["ds4"]["pause"]) == ("✕", "OPTIONS"), r["ds4"]
    assert r["clavier"]["clavier"] is True and r["clavier"]["manette"] is False
