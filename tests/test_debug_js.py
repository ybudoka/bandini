"""Les TRICHES : une suite secrete de touches (qui ajoute ensuite un onglet
TRICHES au classeur de la PAUSE de la partie), jamais un bouton au titre — et ses
tricheries, faites pour tester a la main sans y perdre la soiree : de l'argent,
la sante, sauter l'objectif, teleporter au repere que le HUD montre deja
(`Histoire.cible`, la meme fleche que celle du joueur ordinaire).

⚠️ La suite (`SEQUENCE_DEBUG` dans `jeu.js`, « RIGOLO ») ne prend QUE des
lettres hors d'`Entree.MAP_TOUCHES` : le Konami classique (fleches, B, A) a
d'abord ete essaye, et KeyB (ANNULER) fermait le menu PAUSE puis relançait la
partie (`reprendre()`) juste avant que le dernier appui n'ouvre DEBUG
par-dessus — voir `test_pas_par_dessus_un_autre_menu`.
"""

import json

import pytest
from test_police_js import AGENT

TAPER_LA_SUITE = (
    "['KeyR','KeyI','KeyG','KeyO','KeyL','KeyO'].forEach(function (c) { o.tape(c); });"
)


def test_la_suite_secrete_ouvre_le_menu_debug_en_partie(banc):
    """Elle ouvre la PAUSE, sur l'onglet TRICHES du classeur."""
    r = banc(
        """function (L, o) {
        L.Jeu.commencer();
        """
        + TAPER_LA_SUITE
        + """
        return { titre: L.B.menu && L.B.menu.titre, etat: L.B.etat, onglet: L.B.menu && L.B.menu.classeur.onglet };
    }"""
    )
    assert r == {"titre": "TRICHES", "etat": "pause", "onglet": "triches"}


def test_une_suite_fausse_n_ouvre_rien(banc):
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        ['KeyR', 'KeyI', 'KeyG', 'KeyO', 'KeyL', 'KeyR'].forEach(function (c) { o.tape(c); });
        return { menu: L.B.menu };
    }""")
    assert r["menu"] is None


def test_pas_de_menu_debug_au_titre(banc):
    """Avant JOUER, `B.etat` vaut 'titre' : la suite ne fait rien."""
    r = banc(
        """function (L, o) {
        """
        + TAPER_LA_SUITE
        + """
        return { etat: L.B.etat, menu: L.B.menu };
    }"""
    )
    assert r["etat"] == "titre"
    assert r["menu"] is None


def test_pas_par_dessus_un_autre_menu(banc):
    """La suite ne vole pas un menu deja ouvert — ici, un comptoir."""
    r = banc(
        """function (L, o) {
        L.Jeu.commencer();
        L.Hud.ouvrirMenu({ titre: 'COMPTOIR', items: [{ libelle: 'UN HOT-DOG', faire: function () { return false; } }] });
        """
        + TAPER_LA_SUITE
        + """
        return { titre: L.B.menu && L.B.menu.titre, etat: L.B.etat, triches: L.B.partie.triches.menu };
    }"""
    )
    assert r == {"titre": "COMPTOIR", "etat": "jeu", "triches": False}


def test_dans_la_pause_la_suite_tourne_le_classeur_vers_les_triches(banc):
    """Le classeur de la PAUSE n'est pas « un autre menu » : la suite tapee
    dedans allume les triches et tourne vers leur onglet."""
    r = banc(
        """function (L, o) {
        L.Jeu.commencer();
        L.Jeu.pause();
        const avant = L.Hud.onglets();
        """
        + TAPER_LA_SUITE
        + """
        return { avant: avant, apres: L.Hud.onglets(), titre: L.B.menu && L.B.menu.titre, etat: L.B.etat };
    }"""
    )
    assert "triches" not in r["avant"] and r["apres"][-1] == "triches"
    assert r["titre"] == "TRICHES" and r["etat"] == "pause"


def test_argent_et_sante_dans_le_menu_debug(banc):
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const j = L.B.joueur;
        j.vie = 1;
        const avant = L.B.partie.argent;
        L.Hud.ouvrirMenu(L.Hud.menuDebug());
        const parNom = {};
        L.B.menu.items.forEach(function (i) { parNom[i.libelle] = i; });
        const resteArgent = parNom['ARGENT +1 000 $'].faire(parNom['ARGENT +1 000 $']);
        parNom['SANTÉ COMPLÈTE'].faire(parNom['SANTÉ COMPLÈTE']);
        return { avant: avant, apres: L.B.partie.argent, resteArgent: resteArgent,
                 vie: j.vie, vieMax: j.vieMax, viePartie: L.B.partie.vie, menuOuvert: !!L.B.menu };
    }""")
    assert r["apres"] == r["avant"] + 1000
    assert r["resteArgent"] is False, "l'item garde le menu ouvert pour en reprendre"
    assert r["vie"] == r["vieMax"]
    assert r["viePartie"] == r["vieMax"]
    assert r["menuOuvert"] is True


def test_invincible_bascule_et_bloque_les_degats(banc):
    """`B.debugInvincible` recharge les images d'invincibilite ORDINAIRES a
    chaque image (voir `Jeu.maj`) : `Entites.blesser` les respecte deja pour
    tout le monde, combat, tirs, explosions et collisions compris."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const j = L.B.joueur;
        L.Hud.ouvrirMenu(L.Hud.menuDebug());
        const item = L.B.menu.items.filter(function (i) { return i.libelle === 'INVINCIBLE'; })[0];
        const avant = item.detail;
        item.faire(item);
        const apres = item.detail;
        o.frame(5);
        const invincibleApres = j.invincible;
        const encaisse = L.Entites.blesser(j, 999, null, {});
        const vieApresCoupBloque = j.vie;
        item.faire(item);
        L.Hud.fermerMenu();               // un menu ouvert fige la simulation : rien ne decroit dessous
        o.frame(90);
        const invincibleEteint = j.invincible;
        const encaisse2 = L.Entites.blesser(j, 5, null, {});
        return { avant: avant, apres: apres, invincibleApres: invincibleApres, encaisse: encaisse,
                 vieApresCoupBloque: vieApresCoupBloque, vieMax: j.vieMax,
                 invincibleEteint: invincibleEteint, encaisse2: encaisse2, vieApresCoup2: j.vie };
    }""")
    assert (r["avant"], r["apres"]) == ("NON", "OUI")
    assert r["invincibleApres"] > 0
    assert r["encaisse"] is False, "un coup ne doit pas porter pendant INVINCIBLE"
    assert r["vieApresCoupBloque"] == r["vieMax"]
    assert r["invincibleEteint"] == 0, "et redescend a zero une fois eteint"
    assert r["encaisse2"] is True
    assert r["vieApresCoup2"] == r["vieMax"] - 5


def test_teleporter_sans_objectif_ne_bouge_personne(banc):
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const j = L.B.joueur;
        const x = j.x, y = j.y;
        L.Histoire.cible = function () { return null; };
        L.Hud.ouvrirMenu(L.Hud.menuDebug());
        const item = L.B.menu.items.filter(function (i) { return i.libelle.indexOf('TÉLÉPORTER') === 0; })[0];
        item.faire(item);
        return { actif: item.actif, x: j.x, y: j.y, ax: x, ay: y };
    }""")
    assert r["actif"] is False
    assert (r["x"], r["y"]) == (r["ax"], r["ay"])


def test_teleporter_vers_l_objectif(banc):
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const j = L.B.joueur;
        const cx = j.x + 3000, cy = j.y - 500;
        L.Histoire.cible = function () { return { x: cx, y: cy }; };
        L.Hud.ouvrirMenu(L.Hud.menuDebug());
        const item = L.B.menu.items.filter(function (i) { return i.libelle.indexOf('TÉLÉPORTER') === 0; })[0];
        const actif = item.actif;
        item.faire(item);
        return { actif: actif, x: j.x, y: j.y, cx: cx, cy: cy };
    }""")
    assert r["actif"] is True
    assert (r["x"], r["y"]) == (r["cx"], r["cy"])


def test_teleporter_refuse_dans_une_piece(banc):
    """`Jeu.sortir` orchestre sa propre transition : le debug n'ecrase pas la
    sienne, alors il ne fait rien tant qu'on n'est pas dehors."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const j = L.B.joueur;
        L.B.interieur = {};
        const x = j.x, y = j.y;
        L.Histoire.cible = function () { return { x: j.x + 3000, y: j.y - 500 }; };
        L.Hud.ouvrirMenu(L.Hud.menuDebug());
        const item = L.B.menu.items.filter(function (i) { return i.libelle.indexOf('TÉLÉPORTER') === 0; })[0];
        item.faire(item);
        return { x: j.x, y: j.y, ax: x, ay: y };
    }""")
    assert (r["x"], r["y"]) == (r["ax"], r["ay"])


def test_objectif_suivant_et_terminer_actifs_seulement_en_mission(banc):
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        L.Hud.ouvrirMenu(L.Hud.menuDebug());
        const avant = {};
        L.B.menu.items.forEach(function (i) { avant[i.libelle] = i.actif; });
        L.Hud.fermerMenu();
        L.Histoire.commencer('m1');
        L.B.cinema = null;
        L.Hud.ouvrirMenu(L.Hud.menuDebug());
        const pendant = {};
        L.B.menu.items.forEach(function (i) { pendant[i.libelle] = i.actif; });
        return { avant: avant, pendant: pendant };
    }""")
    assert r["avant"]["OBJECTIF SUIVANT"] is False
    assert r["avant"]["TERMINER LA MISSION"] is False
    assert r["pendant"]["OBJECTIF SUIVANT"] is True
    assert r["pendant"]["TERMINER LA MISSION"] is True


def test_terminer_la_mission_compte_la_reussite(banc):
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        L.Histoire.commencer('m1');
        L.B.cinema = null;
        L.Hud.ouvrirMenu(L.Hud.menuDebug());
        const item = L.B.menu.items.filter(function (i) { return i.libelle === 'TERMINER LA MISSION'; })[0];
        const fini = item.faire(item);
        return { fini: fini, missionsFaites: L.B.partie.missionsFaites, enCours: L.B.partie.mission };
    }""")
    assert r["fini"] is True
    assert "m1" in r["missionsFaites"]
    assert r["enCours"] is None


def test_retour_ferme_le_menu_debug_par_le_clavier(banc):
    """Il n'y a plus de RETOUR au bout des triches : c'est un onglet du classeur,
    et B (Effacer) reprend la partie, comme depuis tout onglet."""
    r = banc(
        """function (L, o) {
        L.Jeu.commencer();
        """
        + TAPER_LA_SUITE
        + """
        const lignes = L.B.menu.items.map(function (i) { return i.libelle; });
        o.tape('Backspace', 2);
        return { lignes: lignes, menu: L.B.menu, etat: L.B.etat };
    }"""
    )
    assert "RETOUR" not in r["lignes"] and "PLUS…" not in r["lignes"]
    assert r["menu"] is None and r["etat"] == "jeu"


# --- Les triches se sauvent avec la partie ----------------------------------------------

NOMS_DES_BASCULES = ["INVINCIBLE", "VÉHICULES INVINCIBLES", "ÉNERGIE INFINIE", "MUNITIONS INFINIES",
                     "LA POLICE NE T'ARRÊTE PAS"]
TOUT_ETEINT = {"menu": False, "invincible": False, "vehicules": False, "endurance": False,
               "munitions": False, "pasArrete": False}
TOUT_ALLUME = {**TOUT_ETEINT, "invincible": True, "vehicules": True, "endurance": True,
               "munitions": True, "pasArrete": True}


def test_les_triches_se_sauvent_avec_la_partie_et_reviennent(banc):
    """⚠️ Les bascules vivaient sur `B` et s'evaporaient au rechargement. Elles
    sont maintenant dans `B.partie.triches` : la bascule ECRIT tout de suite
    (sans attendre la sauvegarde auto), l'emplacement rouvert les retrouve, et
    le menu dit OUI — le menu, lui, reste secret."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const noms = %s;
        function items() {
            L.Hud.fermerMenu(); L.Hud.ouvrirMenu(L.Hud.menuDebug());
            const par = {};
            L.B.menu.items.forEach(function (i) { par[i.libelle] = i; });
            return par;
        }
        let par = items();
        const avant = noms.map(function (n) { return par[n].detail; });
        noms.forEach(function (n) { par[n].faire(par[n]); });
        // Aucune sauvegarde demandee ici : c'est la bascule qui ecrit.
        const ecrit = JSON.parse(o.store[L.Sauvegarde.CLE]).triches;
        // Rouvrir l'emplacement, comme `chargerPartie`.
        L.B.partie = L.Sauvegarde.completer(L.Sauvegarde.lire(1), L.B.defs);
        par = items();
        const rouvert = noms.map(function (n) { return par[n].detail; });
        par['INVINCIBLE'].faire(par['INVINCIBLE']);          // et l'eteindre se sauve aussi
        const eteint = JSON.parse(o.store[L.Sauvegarde.CLE]).triches;
        return { avant: avant, ecrit: ecrit, rouvert: rouvert, eteint: eteint, enMemoire: L.B.partie.triches };
    }""" % json.dumps(NOMS_DES_BASCULES))
    assert r["avant"] == ["NON"] * 5
    assert r["ecrit"] == TOUT_ALLUME
    assert r["rouvert"] == ["OUI"] * 5, "l'emplacement rouvert doit retrouver ses triches"
    assert r["eteint"] == {**TOUT_ALLUME, "invincible": False}
    assert r["enMemoire"] == r["eteint"]


def test_une_partie_neuve_ou_ancienne_n_a_aucune_triche(banc):
    """Une nouvelle partie repart sans rien, un vieux blob d'avant les triches se
    complete a « tout eteint », et un blob a moitie rempli garde ce qu'il a."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        return { neuve: L.etatInitial(L.B.defs).triches,
                 vieille: L.Sauvegarde.completer({ argent: 7 }, L.B.defs).triches,
                 partielle: L.Sauvegarde.completer({ triches: { invincible: true } }, L.B.defs).triches };
    }""")
    assert r["neuve"] == TOUT_ETEINT
    assert r["vieille"] == TOUT_ETEINT
    assert r["partielle"] == {**TOUT_ETEINT, "invincible": True}


def test_l_energie_infinie_est_lue_dans_la_partie(banc):
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const j = L.B.joueur;
        L.B.partie.triches.endurance = true;
        j.endurance = 0;
        o.frame(2);
        return { endurance: j.endurance, max: L.B.defs.recherche.vitesses.endurance };
    }""")
    assert r["endurance"] == r["max"]


def test_les_munitions_infinies_sont_lues_dans_la_partie(banc):
    """Chargeur VIDE et pourtant le coup part (la gachette ne clique pas), et le
    chargeur ne descend pas : les deux lecteurs de `Combat.tirer`."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const j = L.B.joueur;
        L.B.partie.armes.pistolet = { mun: 0, usure: 0 }; j.arme = 'pistolet';
        L.B.partie.triches.munitions = true;
        const un = L.Combat.frapper(j, false);
        j.etat = 'flane'; j.phase = null;
        const deux = L.Combat.frapper(j, false);
        return { un: un, deux: deux, mun: L.B.partie.armes.pistolet.mun };
    }""")
    assert r["un"] is True and r["deux"] is True
    assert r["mun"] == 0


@pytest.mark.parametrize("allumee", [False, True])
def test_la_police_ne_t_arrete_pas_est_lue_dans_la_partie(banc, allumee):
    """Le meme agent, la meme poursuite : seule la triche change s'il y a arrestation."""
    r = banc(AGENT + """
        L.Jeu.commencer();
        const j = L.B.joueur;
        L.B.partie.triches.pasArrete = %s;
        L.Police.ajouterChaleur(3);
        const a = poserAgent(L, 'poursuit', 30);
        a.but = { x: j.x, y: j.y };
        a.vuT = 0;
        const arrete = function () { return L.B.menu && L.B.menu.titre === 'ARRÊTÉ !'; };
        let arrive = -1;
        for (let i = 0; i < 300 && arrive < 0; i++) { o.frame(1); if (arrete()) arrive = i; }
        return { arrive: arrive, arrestations: L.B.partie.stats.arrestations };
    }""" % ("true" if allumee else "false"))
    if allumee:
        assert r["arrive"] == -1 and r["arrestations"] == 0, "la triche allumee : la police ne t'arrete pas"
    else:
        assert r["arrive"] >= 0, "temoin : sans la triche, la meme poursuite finit en arrestation"


# --- VÉHICULES INVINCIBLES : le char qu'on conduit ne casse pas et ne coule pas ------------

AU_VOLANT = """
        function auVolant(L, o) {
            const j = L.B.joueur;
            const v = o.char('auto', 0, 0, 0);
            L.Vehicules.monter(j, v);
            L.Entites.indexer();
            return v;
        }
"""


@pytest.mark.parametrize("allumee", [False, True])
def test_vehicules_invincibles_protege_le_char_qu_on_conduit(banc, allumee):
    """Le meme choc, la meme explosion : seule la triche change s'il en reste
    quelque chose. Le TRAFIC, lui, n'est jamais protege — un fuyard de mission
    doit pouvoir se faire casser."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        """ + AU_VOLANT + """
        L.B.partie.triches.vehicules = %s;
        const v = auVolant(L, o);
        const vieMax = v.vie;
        L.Vehicules.endommager(v, 30, null);
        const apresChoc = v.vie;
        L.Vehicules.endommager(v, 99999, null);
        const trafic = o.char('auto', 200, 0, 0);
        trafic.conducteur = 'trafic';
        L.Vehicules.endommager(trafic, 99999, null);
        return { vieMax: vieMax, apresChoc: apresChoc, vie: v.vie, etat: v.etat, traficEtat: trafic.etat };
    }""" % ("true" if allumee else "false"))
    assert r["traficEtat"] == "epave", "le trafic n'est jamais protege"
    if allumee:
        assert r["apresChoc"] == r["vieMax"] and r["vie"] == r["vieMax"]
        assert r["etat"] != "epave", "le char qu'on conduit ne casse pas"
    else:
        assert r["apresChoc"] == r["vieMax"] - 30
        assert r["etat"] == "epave", "temoin : sans la triche, le meme coup l'achevait"


def test_un_char_gare_n_est_pas_protege_par_la_triche(banc):
    """⚠️ `conducteur === null` et `B.joueur` : le garde ne doit pas confondre
    un char sans conducteur avec un char conduit par le joueur."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        L.B.partie.triches.vehicules = true;
        const v = o.char('auto', 200, 0, 0);
        L.Vehicules.endommager(v, 99999, null);
        // Et sans joueur du tout (`null === null`) : personne ne conduit, personne n'est protege.
        const w = o.char('auto', 300, 0, 0);
        const joueur = L.B.joueur;
        L.B.joueur = null;
        L.Vehicules.endommager(w, 99999, null);
        L.B.joueur = joueur;
        return { etat: v.etat, sansJoueur: w.etat };
    }""")
    assert r["etat"] == "epave"
    assert r["sansJoueur"] == "epave"


@pytest.mark.parametrize("allumee", [False, True])
def test_vehicules_invincibles_ne_coule_pas(banc, allumee):
    """Couler, c'est disparaitre du monde : la triche le refuse aussi."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        """ + AU_VOLANT + """
        L.B.partie.triches.vehicules = %s;
        const v = auVolant(L, o);
        L.Monde.estEau = function () { return true; };
        o.frame(L.B.defs.recherche.nage.coule_s * 60 + 60);
        return { present: L.B.entites.indexOf(v) >= 0 };
    }""" % ("true" if allumee else "false"))
    assert r["present"] is allumee, "avec la triche le char reste ; sans elle, la baie le mange"


# --- L'onglet TRICHES de la PAUSE ---------------------------------------------------------

def _lignes_de_la_pause():
    return """
        function lignes(L) {
            L.Jeu.pause();
            return L.Hud.onglets();
        }
    """


def test_la_pause_n_a_pas_de_ligne_triches_avant_la_suite_secrete(banc):
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        """ + _lignes_de_la_pause() + """
        return { lignes: lignes(L), menu: L.B.partie.triches.menu, ouvert: L.Hud.ouvrirOnglet('triches'),
                 titre: L.B.menu.titre };
    }""")
    assert "triches" not in r["lignes"]
    assert r["menu"] is False
    assert r["ouvert"] is False and r["titre"] == "PAUSE", "l'onglet ne s'ouvre pas meme en le demandant"


def test_la_suite_secrete_active_les_triches_et_la_pause_y_mene(banc):
    """La suite tapee UNE fois : l'onglet TRICHES est dans le classeur de la
    PAUSE, il se sauve avec la partie, et on y tourne a l'epaule droite depuis
    OPTIONS — puis encore une fois, et on fait le tour jusqu'a la PAUSE."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        """ + _lignes_de_la_pause() + TAPER_LA_SUITE + """
        const ecrit = JSON.parse(o.store[L.Sauvegarde.CLE]).triches.menu;
        L.Hud.fermerMenu(); L.Jeu.reprendre();
        // Rouvrir l'emplacement, comme `chargerPartie` : l'onglet doit y etre encore.
        L.B.partie = L.Sauvegarde.completer(L.Sauvegarde.lire(1), L.B.defs);
        const l = lignes(L);
        L.Hud.ouvrirOnglet('options');
        function rb() {
            o.pad([0, 0], [0, 0, 0, 0, 0, 1], { mapping: 'standard' }); o.frame(2);
            o.pad([0, 0], [0, 0, 0, 0, 0, 0], { mapping: 'standard' }); o.frame(2);
            return { titre: L.B.menu && L.B.menu.titre, etat: L.B.etat };
        }
        const un = rb(), deux = rb();
        return { ecrit: ecrit, lignes: l, un: un, deux: deux };
    }""")
    assert r["ecrit"] is True, "la suite secrete se sauve avec la partie"
    assert r["lignes"] == ["pause", "carnet", "bilan", "commandes", "options", "triches"]
    assert r["un"] == {"titre": "TRICHES", "etat": "pause"}
    assert r["deux"] == {"titre": "PAUSE", "etat": "pause"}, "RB fait le tour du classeur, il ne ferme rien"


def test_une_triche_qui_ferme_le_menu_depuis_la_pause_reprend_la_partie(banc):
    """SANTÉ COMPLÈTE laisse le menu ouvert ; TELEPORTER le ferme, et fermer le
    dernier menu d'une pause, c'est reprendre : la partie ne reste pas figee."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        L.B.partie.triches.menu = true;
        L.Histoire.cible = function () { return { x: L.B.joueur.x + 500, y: L.B.joueur.y }; };
        L.Jeu.pause();
        L.Hud.ouvrirOnglet('triches');
        const teleporter = L.B.menu.items.filter(function (i) { return i.libelle.indexOf('TÉLÉPORTER') === 0; })[0];
        L.B.menu.curseur = L.B.menu.items.indexOf(teleporter);
        o.tape('KeyE', 2);                                     // ACTION sur la ligne
        o.frame(2);
        return { etat: L.B.etat, menu: L.B.menu };
    }""")
    assert r["etat"] == "jeu" and r["menu"] is None


def test_le_menu_debug_ouvert_par_la_suite_secrete_se_ferme_toujours_vers_le_jeu(banc):
    """Ouvert par la suite, le classeur des triches se referme vers le jeu — a
    ECHAP comme a PAUSE : la partie ne reste pas figee."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        """ + TAPER_LA_SUITE + """
        o.tape('Escape', 2);
        const echap = { etat: L.B.etat, menu: L.B.menu };
        """ + TAPER_LA_SUITE + """
        o.pad([0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 1], { mapping: 'standard' }); o.frame(2);
        o.pad([0, 0], [], { mapping: 'standard' }); o.frame(2);
        return { echap: echap, start: { etat: L.B.etat, menu: L.B.menu } };
    }""")
    assert r["echap"] == {"etat": "jeu", "menu": None}
    assert r["start"] == {"etat": "jeu", "menu": None}



# --- SAUT VERS UNE MISSION : on va chez le donneur, et la mission demarre -------------------

CHOISIR_UNE_MISSION = """
        function choisir(L, slug, depuisLaPause) {
            if (!depuisLaPause) L.Hud.ouvrirMenu(L.Hud.menuDebug());
            else L.Hud.ouvrirOnglet('triches');
            function ligne(nom) { return L.B.menu.items.filter(function (i) { return i.libelle === nom; })[0]; }
            ligne('SAUT VERS UNE MISSION').faire();
            const titre = L.B.defs.missions.filter(function (m) { return m.slug === slug; })[0].titre.toUpperCase();
            const item = ligne(titre);
            const detail = item.detail, actif = item.actif;
            const rendu = item.faire(item);
            return { detail: detail, actif: actif, rendu: rendu };
        }
        function pres(L, slug) {
            const d = L.Histoire.donneur(slug), j = L.B.joueur;
            return d ? Math.hypot(d.x - j.x, d.y - j.y) : null;
        }
        function rendreLaMain(L) { L.B.scene = null; L.B.cinema = null; }
"""


def test_le_saut_de_mission_va_chez_le_donneur_et_la_lance(banc):
    """⚠️ Il ne faisait que TELEPORTER sur le pixel du donneur : il fallait encore
    lui parler. Maintenant la mission part tout de suite, intro comprise, et le
    joueur est a cote de lui — c'est ce qui la fait jouer en personne."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        """ + CHOISIR_UNE_MISSION + """
        rendreLaMain(L);
        const j = L.B.joueur;
        const c = choisir(L, 'm1');
        return { c: c, mission: L.B.partie.mission && L.B.partie.mission.slug, menu: L.B.menu,
                 etat: L.B.etat, distance: pres(L, 'ti_guy'), interieur: !!L.B.interieur,
                 intro: !!(L.B.scene || L.B.cinema), tx: L.TT };
    }""")
    assert r["c"]["detail"] == "LANCER" and r["c"]["actif"] is True
    assert r["mission"] == "m1", "la mission doit avoir demarre"
    assert r["menu"] is None and r["etat"] == "jeu"
    assert r["distance"] is not None and r["distance"] <= 2.5 * r["tx"], "a cote du donneur : %s" % r["distance"]
    assert r["distance"] >= 0.75 * r["tx"], "a cote de lui, pas dedans : %s" % r["distance"]
    assert r["intro"] is True, "son intro se joue"
    assert r["interieur"] is False


def test_refaire_une_mission_faite_dont_le_donneur_est_parti(banc):
    """Ti-Guy entre au garage a la fin de M1 (`parti_apres`) : il n'est plus en
    ville, et refaire M1 doit quand meme se jouer devant lui."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        """ + CHOISIR_UNE_MISSION + """
        rendreLaMain(L);
        L.B.partie.missionsFaites.m1 = 1;
        const parti = L.Histoire.donneur('ti_guy');
        if (parti) L.Entites.retirer(parti);
        L.Entites.indexer();
        const avant = L.Histoire.donneur('ti_guy');
        const c = choisir(L, 'm1');
        return { avantAbsent: !avant, c: c, faite: !!L.B.partie.missionsFaites.m1,
                 mission: L.B.partie.mission && L.B.partie.mission.slug,
                 distance: pres(L, 'ti_guy'), tx: L.TT };
    }""")
    assert r["avantAbsent"] is True, "le donneur est bien parti avant le saut"
    assert r["c"]["detail"] == "FAITE · REFAIRE"
    assert r["faite"] is False and r["mission"] == "m1"
    assert r["distance"] is not None and r["distance"] <= 2.5 * r["tx"]


def test_le_saut_entre_dans_la_piece_du_donneur_qui_se_tient_dedans(banc):
    """M4 : Bouchard parle DANS le casse-croute. Le bon endroit est dedans, a cote
    de lui — devant la porte, l'intro se dirait au combine."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        """ + CHOISIR_UNE_MISSION + """
        rendreLaMain(L);
        const c = choisir(L, 'm4');
        const j = L.B.joueur;
        return { mission: L.B.partie.mission && L.B.partie.mission.slug,
                 dedans: L.B.interieur && L.B.interieur.slug, exterieur: !!L.B.exterieur,
                 distance: pres(L, 'bouchard'), transition: !!L.B.transition,
                 sol: L.Monde.marchablePieton(Math.floor(j.x / L.TT), Math.floor(j.y / L.TT)),
                 present: L.Histoire.present('bouchard'), tx: L.TT };
    }""")
    assert r["mission"] == "m4"
    assert r["dedans"], "le joueur doit etre DANS la piece du donneur"
    assert r["exterieur"] is True, "on ressortira par la porte, comme d'habitude"
    assert r["transition"] is False, "sans fondu qui traine"
    assert r["distance"] is not None and r["distance"] <= 2.5 * r["tx"]
    assert r["sol"] is True and r["present"] is True


def test_le_saut_sort_de_la_piece_et_abandonne_la_mission_en_cours(banc):
    """Depuis une piece, en pleine autre mission : on ressort, la mission d'avant
    s'en va SANS compter d'echec, et la nouvelle demarre devant son donneur."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        """ + CHOISIR_UNE_MISSION + """
        rendreLaMain(L);
        choisir(L, 'm4');                       // on est dans le casse-croute, m4 en cours
        rendreLaMain(L);
        L.Hud.fermerMenu();
        const echecs = L.B.partie.stats.echecs || 0;
        const c = choisir(L, 'm1');
        return { mission: L.B.partie.mission && L.B.partie.mission.slug, interieur: !!L.B.interieur,
                 echecs: (L.B.partie.stats.echecs || 0) - echecs, cours: c.detail,
                 distance: pres(L, 'ti_guy'), tx: L.TT, tombes: L.B.partie.tombes || {} };
    }""")
    assert r["mission"] == "m1" and r["interieur"] is False
    assert r["echecs"] == 0, "abandonner n'est pas rater"
    assert r["distance"] is not None and r["distance"] <= 2.5 * r["tx"]


def test_le_saut_descend_du_char(banc):
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        """ + CHOISIR_UNE_MISSION + """
        rendreLaMain(L);
        const j = L.B.joueur;
        const v = o.char('auto', 0, 0, 0);
        L.Vehicules.monter(j, v);
        L.Entites.indexer();
        choisir(L, 'm1');
        return { auVolant: !!j.dansVehicule, conducteur: v.conducteur, mission: L.B.partie.mission && L.B.partie.mission.slug,
                 distance: pres(L, 'ti_guy'), tx: L.TT };
    }""")
    assert r["auVolant"] is False and r["conducteur"] is None
    assert r["mission"] == "m1" and r["distance"] <= 2.5 * r["tx"]


def test_le_saut_depuis_la_pause_reprend_la_partie_et_lance_la_mission(banc):
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        """ + CHOISIR_UNE_MISSION + """
        rendreLaMain(L);
        L.B.partie.triches.menu = true;
        L.Jeu.pause();
        choisir(L, 'm1', true);
        return { etat: L.B.etat, menu: L.B.menu, mission: L.B.partie.mission && L.B.partie.mission.slug };
    }""")
    assert r["etat"] == "jeu" and r["menu"] is None
    assert r["mission"] == "m1"


def test_le_saut_ne_se_lance_pas_pendant_une_scene(banc):
    """Une scene qui joue garde la main : rien ne bouge, le menu reste ouvert."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        """ + CHOISIR_UNE_MISSION + """
        L.B.scene = { bidon: true };
        const j = L.B.joueur, x = j.x, y = j.y;
        const c = choisir(L, 'm1');
        return { rendu: c.rendu, mission: L.B.partie.mission, menu: !!L.B.menu, bouge: j.x !== x || j.y !== y };
    }""")
    assert r["rendu"] is False and r["menu"] is True
    assert r["mission"] is None and r["bouge"] is False


def test_chaque_mission_du_catalogue_se_lance_par_le_saut(banc):
    """C'est le CATALOGUE qui fait la liste : une mission ajoutee au jeu doit
    pouvoir se lancer ici sans qu'on y touche — donneur dehors ou dedans."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        """ + CHOISIR_UNE_MISSION + """
        const sorties = [];
        L.B.defs.missions.forEach(function (m) {
            rendreLaMain(L);
            L.Hud.fermerMenu();
            const c = choisir(L, m.slug);
            sorties.push({ slug: m.slug, actif: c.actif, demarree: !!(L.B.partie.mission && L.B.partie.mission.slug === m.slug),
                           distance: pres(L, m.donneur), tx: L.TT, menu: !!L.B.menu });
        });
        return sorties;
    }""")
    assert len(r) >= 8
    for m in r:
        assert m["actif"] is True and m["demarree"] is True, m
        assert m["distance"] is not None and m["distance"] <= 2.5 * m["tx"], m
        assert m["menu"] is False, m


# --- SAUT VERS UN DÉFI : on se pose devant son panneau, et il se propose -----------------

ALLER_AU_DEFI = """
        function allerAu(L, slug, depuisLaPause) {
            if (depuisLaPause) { L.B.partie.triches.menu = true; L.Jeu.pause(); L.Hud.ouvrirOnglet('triches'); }
            else L.Hud.ouvrirMenu(L.Hud.menuDebug());
            L.B.menu.items.filter(function (i) { return i.libelle === 'SAUT VERS UN DÉFI'; })[0].faire();
            const item = L.B.menu.items.filter(function (i) { return i.defi === slug; })[0];
            return item.faire(item);
        }
        // Ce que le bouton ACTION lirait ici : un panneau, ou le comptoir d'un jeu de foire.
        function sousLaMain(L) {
            const j = L.B.joueur, p = L.Histoire.panneauSousLaMain(j);
            if (p) return p.defi;
            const jeu = L.Foire.jeuSousLaMain(j), d = jeu && L.Histoire.defiDuComptoir(jeu);
            return d ? d.slug : null;
        }
        function rendreLaMain(L) { L.B.scene = null; L.B.cinema = null; }
"""


def test_le_saut_vers_un_defi_range_le_catalogue_par_genre(banc):
    """C'est le CATALOGUE qui fait la liste, rangee au volant / les tours / debout / la
    foire — et un defi reussi le dit, un defi encore cache aussi."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        L.B.partie.defisFaits = { saut: { jour: 1, temps: 100 } };
        const m = L.Hud.menuSautDefis();
        return { lignes: m.items.map(function (i) { return i.entete ? '# ' + i.entete : i.libelle; }),
                 defis: m.items.filter(function (i) { return i.defi; }).map(function (i) { return i.defi; }),
                 saut: m.items.filter(function (i) { return i.defi === 'saut'; })[0].detail,
                 cache: m.items.filter(function (i) { return i.defi === 'roue'; })[0].detail,
                 catalogue: L.B.defs.defis.map(function (d) { return d.slug; }) };
    }""")
    assert sorted(r["defis"]) == sorted(r["catalogue"]), "chaque defi du catalogue, une fois"
    entetes = [x for x in r["lignes"] if x.startswith("# ")]
    # ⚠️ DEBOUT (les épreuves devant un panneau) et DANS LA RUE (la filature, l'esquive) :
    # les dix-huit défis, 23 sept. 2026.
    assert entetes == ["# AU VOLANT", "# LES TOURS", "# DEBOUT", "# DANS LA RUE", "# À LA FOIRE"]
    assert r["lignes"][-1] == "RETOUR"
    assert r["saut"] == "RÉUSSI"
    assert r["cache"] == "CACHÉ"


def test_chaque_defi_du_catalogue_se_rejoint_par_le_saut(banc):
    """Pour chaque defi : le joueur est pose a portee de son panneau (ou du
    comptoir de sa baraque), tourne vers lui — ACTION le lirait —, la pause est
    refermee et la proposition du defi est ouverte."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        """ + ALLER_AU_DEFI + """
        const sorties = [];
        L.B.defs.defis.forEach(function (d) {
            rendreLaMain(L);
            L.Hud.fermerMenu();
            if (L.B.etat === 'pause') L.Jeu.reprendre();
            const rendu = allerAu(L, d.slug, sorties.length % 2 === 1);
            sorties.push({ slug: d.slug, rendu: rendu, menu: L.B.menu && L.B.menu.titre, attendu: d.titre.toUpperCase(),
                           classeur: !!(L.B.menu && L.B.menu.classeur), sousLaMain: sousLaMain(L), etat: L.B.etat });
        });
        return sorties;
    }""")
    assert len(r) >= 10
    for d in r:
        assert d["rendu"] is True, d
        assert d["menu"] == d["attendu"] and d["classeur"] is False, d
        assert d["sousLaMain"] == d["slug"], d
        assert d["etat"] == "jeu", d


def test_apres_le_saut_action_lit_le_panneau_et_commencer_lance_le_defi(banc):
    """Par le BOUTON : PAS MAINTENANT referme la proposition, ACTION la rouvre —
    le panneau est bien sous la main —, et COMMENCER lance le defi."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        """ + ALLER_AU_DEFI + """
        const vu = {};
        for (const slug of ['tour', 'livraison', 'marteau']) {
            rendreLaMain(L);
            L.Hud.fermerMenu();
            if (L.B.defi) L.Histoire.abandonnerDefi();
            allerAu(L, slug);
            L.B.menu.curseur = L.B.menu.items.findIndex(function (i) { return i.libelle === 'PAS MAINTENANT'; });
            o.tape('KeyE', 2);
            const ferme = !L.B.menu;
            o.tape('KeyE', 2);
            const relu = L.B.menu && L.B.menu.titre;
            L.B.menu.curseur = L.B.menu.items.findIndex(function (i) { return i.libelle === 'COMMENCER'; });
            o.tape('KeyE', 2);
            vu[slug] = { ferme: ferme, relu: relu, defi: L.B.defi && L.B.defi.slug };
        }
        return { vu: vu, titres: L.B.defs.defis.reduce(function (a, d) { a[d.slug] = d.titre.toUpperCase(); return a; }, {}) };
    }""")
    for slug, v in r["vu"].items():
        assert v["ferme"] is True, (slug, v)
        assert v["relu"] == r["titres"][slug], (slug, v)
        assert v["defi"] == slug, (slug, v)


def test_le_saut_vers_un_defi_sort_du_char_et_de_la_piece(banc):
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        """ + ALLER_AU_DEFI + """
        rendreLaMain(L);
        const j = L.B.joueur;
        const v = o.char('auto', 0, 0, 0);
        L.Vehicules.monter(j, v);
        L.Entites.indexer();
        allerAu(L, 'saut');
        const char = { auVolant: !!j.dansVehicule, conducteur: v.conducteur, sousLaMain: sousLaMain(L) };
        L.Hud.fermerMenu();
        // Dans une piece : le casse-croute du sergent, par la porte de sa mission.
        const porte = L.Monde.carte.def.portes.filter(function (q) { return q.interieur; })[0];
        L.Jeu.entrer(porte); L.Jeu.finirTransition();
        const dedans = !!L.B.interieur;
        allerAu(L, 'canards');
        return { char: char, dedans: dedans, interieur: !!L.B.interieur, sousLaMain: sousLaMain(L),
                 menu: L.B.menu && L.B.menu.titre };
    }""")
    assert r["char"]["auVolant"] is False and r["char"]["conducteur"] is None
    assert r["char"]["sousLaMain"] == "saut"
    assert r["dedans"] is True, "temoin : on etait bien dans une piece"
    assert r["interieur"] is False and r["sousLaMain"] == "canards"
    assert r["menu"] == "LA PÊCHE AUX CANARDS"


def test_le_saut_abandonne_le_defi_en_cours_sans_rien_noter(banc):
    """Un defi en cours s'arrete sans « DÉFI RATÉ » au carnet — c'est une
    triche, pas un echec —, et le forain reprend sa carabine."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        """ + ALLER_AU_DEFI + """
        rendreLaMain(L);
        const tir = L.B.defs.defis.filter(function (d) { return d.slug === 'tir'; })[0];
        allerAu(L, 'tir');
        L.Hud.fermerMenu();
        L.Histoire.commencerDefi(tir);
        const pendant = { defi: L.B.defi && L.B.defi.slug, arme: L.B.joueur.arme };
        const carnet = (L.B.partie.carnet || []).length;
        allerAu(L, 'saut');
        return { pendant: pendant, defi: L.B.defi, arme: L.B.joueur.arme,
                 carabine: !!L.B.partie.armes.carabine_foire,
                 notes: (L.B.partie.carnet || []).slice(carnet).map(function (e) { return e.t; }) };
    }""")
    assert r["pendant"] == {"defi": "tir", "arme": "carabine_foire"}
    assert r["defi"] is None
    assert r["arme"] != "carabine_foire" and r["carabine"] is False
    assert not any("RATÉ" in n for n in r["notes"]), r["notes"]


def test_le_saut_vers_un_defi_ne_se_lance_pas_pendant_une_scene(banc):
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        """ + ALLER_AU_DEFI + """
        L.B.scene = { bidon: true };
        const j = L.B.joueur, x = j.x, y = j.y;
        const rendu = allerAu(L, 'saut');
        return { rendu: rendu, menu: L.B.menu && L.B.menu.titre, bouge: j.x !== x || j.y !== y };
    }""")
    assert r["rendu"] is False and r["menu"] == "SAUT VERS UN DÉFI" and r["bouge"] is False
