"""Le jeu dans un vrai navigateur (Playwright) : chargement, clavier, tactile, cibles.

Se saute sans Chromium ; dans la suite de livraison (BANDINI_TESTS_OBLIGATOIRES=1,
en local avant de pousser sur `main` — les tests ne tournent plus en CI depuis le
17 sept. 2026), c'est un echec : un garde-fou qui se desactive tout seul n'en est pas un.
"""

import json
import os
import re

import pytest

OBLIGATOIRE = os.environ.get("BANDINI_TESTS_OBLIGATOIRES") == "1"
if OBLIGATOIRE:
    from playwright.sync_api import Error  # noqa: F401
else:
    pytest.importorskip("playwright.sync_api")

ECRANS = {
    "bureau": (1280, 720),
    "tablette": (1024, 768),
    "telephone": (390, 844),
    "paysage": (844, 390),
}

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


@pytest.fixture(scope="session")
def browser_context_args(browser_context_args):
    """⚠️ Sans le travailleur hors ligne : ses juges a lui sont dans
    `test_hors_ligne.py`. Ici, il remplirait son cache pendant chaque juge, et
    `page.route` ne voit pas ce qu'un travailleur sert (doc de Playwright)."""
    return {**browser_context_args, "service_workers": "block"}


@pytest.fixture(scope="session", autouse=True)
def navigateur_installe(browser_type):
    if not os.path.exists(browser_type.executable_path):
        message = "Chromium absent : uv run playwright install chromium"
        if OBLIGATOIRE:
            pytest.fail(message)
        pytest.skip(message)


@pytest.fixture
def erreurs(page):
    liste = []
    page.on("console", lambda m: liste.append(m.text) if m.type == "error" else None)
    page.on("pageerror", lambda e: liste.append(str(e)))
    return liste


COMMANDES_OUVERTES = "window.BANDINI.B.menu && window.BANDINI.B.menu.titre === 'COMMANDES'"


def attendre_titre(page):
    page.wait_for_selector('#bandini[data-etat="titre"]', timeout=15000)


def jouer(page):
    """JOUER, PASSER l'ouverture, puis fermer les COMMANDES : les juges d'ici
    veulent la ville, pas la scene ni l'aide.

    ⚠️ Depuis que le jeu s'ouvre sur une scene (le car de six heures, le
    narrateur), cliquer JOUER ne rend plus les commandes tout de suite : elle
    fige la ville tant qu'on ne l'a pas passee, et un test qui marche au clavier
    juste apres ne bouge pas d'un pixel. Tout ce qui veut jouer DANS la ville
    passe donc par ici — un seul endroit a changer le jour ou l'ouverture change.
    L'ouverture elle-meme a ses juges, plus bas et au banc.

    ⚠️ Et depuis le 21 sept. 2026, la fin de l'ouverture ouvre l'ecran
    COMMANDES, qui fige la ville tant qu'on ne l'a pas ferme (ses juges : plus
    bas, et `test_commandes_js.py`). On le ferme comme un joueur : ECHAP.
    """
    page.click("#bouton-jouer")
    page.wait_for_selector('#bandini[data-etat="jeu"]')
    page.evaluate("window.BANDINI.Histoire.passerOuverture()")
    page.wait_for_function("!window.BANDINI.B.ouverture")
    page.wait_for_function(COMMANDES_OUVERTES)
    page.keyboard.press("Escape")
    page.wait_for_function("!window.BANDINI.B.menu")


@pytest.mark.parametrize("ecran", list(ECRANS))
def test_la_page_charge_sans_erreur(page, serveur, erreurs, ecran):
    page.set_viewport_size({"width": ECRANS[ecran][0], "height": ECRANS[ecran][1]})
    page.goto(serveur)
    attendre_titre(page)
    assert erreurs == []
    deborde = page.evaluate("document.documentElement.scrollWidth - window.innerWidth")
    assert deborde <= 0, f"la page deborde de {deborde} px"


def test_le_titre_de_l_ouverture_est_le_logo(page, serveur, erreurs):
    """Quand le car repart, le titre qui monte est le logo de l'accueil, pas des lettres.

    Retour de Martin : le logo neuf etait sur l'accueil, et l'ouverture ecrivait
    encore « BANDINI » en police du HUD. On lit les PIXELS de l'ecran : l'eclat
    blanc du dernier I et l'or du haut du B, ou le titre en lettres ne met rien.
    """
    page.goto(serveur)
    attendre_titre(page)
    page.wait_for_function("document.querySelector('#voile-titre .logo').complete")
    jouer(page)
    couleurs = page.evaluate("""() => {
        const L = window.BANDINI, H = L.Hud, S = L.Base.SCALE;
        const img = document.querySelector('#voile-titre .logo');
        const x0 = Math.round((L.VW - img.naturalWidth * H.LOGO_ECHELLE) / 2), y0 = H.LOGO_Y;
        // ⚠️ Tout dans le meme tour de JS : une image de jeu entre la pose et la
        // lecture ferait avancer cette fausse ouverture, qui n'a pas de car.
        // ⚠️ C'est une SCENE qu'on fabrique (`Scenes`, depuis le 16 sept. 2026) :
        // le HUD dessine le carton de la scene qui joue, et celui de l'ouverture
        // est le logo (`missions.SCENE_OUVERTURE`, plan `titre`).
        L.B.scene = { noir: 0, titre: 1, carton: { logo: true, texte: '', sous: 'BAIE-DES-BRUMES' } };
        H.dessiner();
        L.B.scene = null;
        const ctx = document.getElementById('toile').getContext('2d');
        function lire(gx, gy) {
            const x = (x0 + gx * H.LOGO_ECHELLE + 1) * S + 1, y = (y0 + gy * H.LOGO_ECHELLE + 1) * S + 1;
            return Array.from(ctx.getImageData(x, y, 1, 1).data.slice(0, 3));
        }
        return { eclat: lire(img.naturalWidth - 5, 1), or: lire(4, 1) };
    }""")
    assert couleurs["eclat"] == [255, 255, 255], couleurs
    assert couleurs["or"] == [0xFF, 0xF3, 0xC8], couleurs
    assert erreurs == []


def test_la_barre_de_chargement_avance_puis_s_efface(page, serveur, erreurs):
    """Demande de Martin (17 sept. 2026) : « une barre de chargement au lancement
    du jeu ». Elle avance pendant les scripts (`chargement.js`), puis pendant les
    definitions et la carte, jamais a reculons, finit a 100 — et s'efface quand
    l'ecran titre est pret."""
    page.add_init_script("""
        window.__barre = [];
        new MutationObserver(function (ms) {
            ms.forEach(function (m) {
                if (m.target.id === 'chargement') window.__barre.push(Number(m.target.getAttribute('aria-valuenow')));
            });
        }).observe(document, { attributes: true, subtree: true, attributeFilter: ['aria-valuenow'] });
    """)
    page.goto(serveur)
    attendre_titre(page)
    valeurs = page.evaluate("window.__barre")
    part_scripts = int(page.get_attribute("#chargement", "data-part-scripts"))
    assert valeurs == sorted(valeurs), f"la barre a recule : {valeurs}"
    assert any(0 < v < part_scripts for v in valeurs), f"rien pendant les scripts : {valeurs}"
    # ⚠️ Sous 95 : le 95 se pose avant de batir la ville, sans avoir lu un octet —
    # c'est la lecture des deux reponses qui doit se voir entre les deux.
    assert any(part_scripts < v < 95 for v in valeurs), f"rien pendant les donnees : {valeurs}"
    assert valeurs[-1] == 100, valeurs
    assert page.locator("#chargement").is_hidden(), "la barre reste affichee sur l'ecran titre"
    assert erreurs == []


def test_une_carte_d_une_autre_construction_est_refusee(page, serveur):
    """⚠️ La carte voyage a part depuis le 16 sept. 2026 (`/api/carte`), et les
    deux reponses doivent etre de la MEME construction : un deploiement tombe
    entre les deux requetes donnerait une ville dont les portes et les missions
    ne se parlent plus. Le jeu refuse, reste au chargement, et dit de recharger.
    Le temoin : la meme page, sans la carte truquee, arrive au titre."""
    page.goto(serveur)
    attendre_titre(page)

    def une_autre_carte(route):
        reponse = route.fetch()
        carte = reponse.json()
        carte["empreinte"] = "0" * 16
        route.fulfill(response=reponse, json=carte)

    page.route("**/api/carte?*", une_autre_carte)   # `?e=` : l'empreinte, cle du cache hors ligne
    page.reload()
    page.wait_for_function(
        "() => document.getElementById('etat-chargement').textContent.indexOf('Impossible') >= 0",
        timeout=15000)
    assert page.locator("#bandini").get_attribute("data-etat") == "chargement"


def test_jouer_puis_marcher_au_clavier(page, serveur, erreurs):
    page.goto(serveur)
    attendre_titre(page)
    jouer(page)
    page.wait_for_selector('#bandini[data-etat="jeu"]')
    x0 = page.evaluate("window.BANDINI.B.joueur.x")
    page.keyboard.down("KeyD")
    page.wait_for_timeout(500)
    page.keyboard.up("KeyD")
    x1 = page.evaluate("window.BANDINI.B.joueur.x")
    assert x1 > x0 + 20
    page.keyboard.press("Escape")
    page.wait_for_selector('#bandini[data-etat="pause"]')
    assert erreurs == []


def test_l_ouverture_joue_au_premier_jouer_et_se_passe(page, serveur, erreurs):
    """L'ouverture dans un vrai navigateur : elle part sur JOUER, elle parle, elle se passe.

    ⚠️ C'est le SEUL endroit qui prouve qu'elle sonne. Sous Node il n'y a pas
    d'AudioContext : le banc verifie qu'on DEMANDE la voix, jamais qu'elle se
    decode. Et c'est aussi le seul endroit qui prouve l'autre moitie — que rien
    n'a ete demande au son AVANT le geste, ce qui est toute la raison pour
    laquelle l'ouverture part de JOUER et pas du chargement de la page.
    """
    page.goto(serveur)
    attendre_titre(page)
    # Avant le geste : les mp3 de l'ouverture sont deja tires dans le cache du
    # navigateur, mais le son, lui, est encore retenu.
    assert page.evaluate("window.BANDINI.Son.etatSon()") in ("absent", "attente")
    page.click("#bouton-jouer")
    page.wait_for_selector('#bandini[data-etat="jeu"]')
    assert page.evaluate("!!window.BANDINI.B.ouverture"), "JOUER lance la scene"
    assert page.evaluate("window.BANDINI.B.cinema.lignes.length") == 4
    # La voix se DECODE et se dit : une replique muette n'est pas une narration.
    page.wait_for_function("window.BANDINI.Son.Voix.enCours !== null", timeout=10000)
    assert page.evaluate("window.BANDINI.Son.Voix.demandees[0]") == "narrateur-ouverture-1"
    assert page.evaluate("window.BANDINI.Son.Mus.courante") == "ouverture"
    # Le car arrive, et le bonhomme n'est pas encore descendu.
    assert page.evaluate("window.BANDINI.B.entites.filter(e => e.slug === 'autobus' && e.conducteur !== 'ligne').length") == 1
    # PASSER, au clavier : on tombe dans la ville, et on marche.
    x0 = page.evaluate("window.BANDINI.B.joueur.x")
    y0 = page.evaluate("window.BANDINI.B.joueur.y")
    page.keyboard.press("Space")
    page.wait_for_function("!window.BANDINI.B.ouverture")
    assert page.evaluate("window.BANDINI.B.joueur.dessine") is True
    assert page.evaluate("window.BANDINI.B.entites.filter(e => e.slug === 'autobus' && e.conducteur !== 'ligne').length") == 0
    # Les COMMANDES s'ouvrent quand on rend le bonhomme, et E (« C'EST PARTI ») les ferme.
    page.wait_for_function(COMMANDES_OUVERTES)
    page.keyboard.press("KeyE")
    page.wait_for_function("!window.BANDINI.B.menu")
    page.keyboard.down("KeyW")
    page.wait_for_timeout(400)
    page.keyboard.up("KeyW")
    bouge = page.evaluate("window.BANDINI.B.joueur.y") != y0 or page.evaluate("window.BANDINI.B.joueur.x") != x0
    assert bouge, "les commandes sont rendues des que la scene est passee"
    assert erreurs == []


def test_changer_de_partie_recharge_la_page_et_rouvre_le_choix(page, serveur, erreurs):
    """Trois parties : prendre la 2 dans une ville posee pour la 1 RECHARGE la page.

    ⚠️ Le banc ne fait que COMPTER les rechargements, et son `sessionStorage`
    est un objet. Qu'une vraie page se recharge, que le drapeau survive a ce
    rechargement-la et a lui seul, et que le choix se rouvre sur la 2 : ca ne se
    voit qu'ici.
    """
    def appui(touche):
        # Tenue un instant : deux appuis dans la meme image n'en font qu'un.
        page.keyboard.down(touche)
        page.wait_for_timeout(60)
        page.keyboard.up(touche)
        page.wait_for_timeout(60)

    choix_ouvert = "window.BANDINI.B.menu && window.BANDINI.B.menu.titre === 'PARTIES'"
    ici = "() => { const m = BANDINI.B.menu; return m.items[m.curseur].libelle; }"
    page.goto(serveur)
    attendre_titre(page)
    jouer(page)                                   # aucune partie : JOUER joue, dans la 1
    page.evaluate("() => BANDINI.Jeu.retourTitre()")
    un = page.evaluate("() => localStorage.getItem('bandini-partie-v1')")
    assert un, "revenir au titre sauvegarde la 1"
    appui("KeyE")
    page.wait_for_function(choix_ouvert)
    appui("KeyS")
    assert page.evaluate(ici) == "2  NOUVELLE PARTIE"
    with page.expect_navigation():
        appui("KeyE")
    attendre_titre(page)
    page.wait_for_function(choix_ouvert)
    assert page.evaluate(ici) == "2  NOUVELLE PARTIE", "le choix se rouvre tout seul, sur la partie prise"
    appui("KeyE")
    page.wait_for_selector('#bandini[data-etat="jeu"]')
    assert page.evaluate("() => BANDINI.B.partie.jour") == 1
    assert page.evaluate("() => !!(BANDINI.B.scene || BANDINI.B.ouverture)"), "une partie neuve s'ouvre sur sa scene"
    assert page.evaluate("() => localStorage.getItem('bandini-emplacement-v1')") == "2"
    assert page.evaluate("() => localStorage.getItem('bandini-partie-v1')") == un, "la 1 n'a pas bouge"
    # Un rechargement ORDINAIRE ne rouvre rien : le drapeau n'a servi qu'une fois.
    page.reload()
    attendre_titre(page)
    page.wait_for_timeout(300)
    assert page.evaluate("() => BANDINI.B.menu") is None
    assert page.is_visible("#voile-titre")
    assert erreurs == []


def test_la_premiere_mission_se_joue_en_scenes_de_l_intro_a_la_fin(page, serveur, erreurs):
    """Les missions mises en scène, dans un vrai navigateur : M1 de l'intro à la fin,
    en temps réel, voix et musique comprises — et aucune erreur console.

    On ne conduit pas pour de vrai : on POSE le cousin là où l'objectif s'accomplit
    et on laisse le jeu le voir. Ce sont les scènes qu'on juge ici : qu'elles
    partent, qu'elles jouent jusqu'au bout sans qu'on touche à rien, et que Ti-Guy,
    sa clé tendue, rentre au garage."""
    page.goto(serveur)
    attendre_titre(page)
    jouer(page)
    page.wait_for_function("window.BANDINI.B.etat === 'jeu' && !window.BANDINI.B.scene")
    page.evaluate("""() => {
        const L = window.BANDINI, j = L.B.joueur, t = L.Histoire.donneur('ti_guy');
        j.x = t.x - 14; j.y = t.y; L.Entites.indexer();
        L.Histoire.parler('ti_guy');
    }""")
    assert page.evaluate("!!window.BANDINI.B.scene"), "parler a Ti-Guy ne joue pas sa scene d'intro"
    page.wait_for_function("!window.BANDINI.B.scene && !window.BANDINI.B.cinema", timeout=90000)
    assert page.evaluate("window.BANDINI.B.partie.mission.slug") == "m1"
    # Au garage, puis dans le char de la ruelle, puis le char ramene au garage.
    page.evaluate("""() => { const L = window.BANDINI, g = L.Histoire.lieu('garage'), j = L.B.joueur;
                            j.x = g.x; j.y = g.y; L.Entites.indexer(); }""")
    page.wait_for_function("window.BANDINI.B.partie.mission.etape === 1", timeout=20000)
    # Marco, devant le garage : sa poignée de main (« des missions plus longues », 22 sept. 2026).
    page.evaluate("() => window.BANDINI.Histoire.parler('marco')")
    page.wait_for_function("window.BANDINI.B.partie.mission.etape === 2", timeout=60000)
    page.evaluate("""() => { const L = window.BANDINI, v = L.B.mission.vehicule, j = L.B.joueur;
                            j.x = v.x + 12; j.y = v.y; L.Entites.indexer(); L.Vehicules.monter(j, v); }""")
    page.wait_for_function("window.BANDINI.B.partie.mission.etape === 3", timeout=20000)
    page.wait_for_function("!window.BANDINI.B.cinema", timeout=60000)      # Ti-Guy au combine
    # Le propriétaire a appelé la police : personne ne nous voit (les agents sont retirés à mesure
    # qu'ils naissent), l'étoile tombe toute seule en quinze secondes.
    page.evaluate("""() => { const L = window.BANDINI;
        window.__sansAgents = setInterval(function () {
            L.B.entites.filter(function (e) { return e.type === 'pieton' && e.arch === 'policier'; })
              .forEach(function (e) { L.Entites.retirer(e); });
        }, 100); }""")
    page.wait_for_function("window.BANDINI.B.partie.mission.etape === 4", timeout=60000)
    page.evaluate("() => clearInterval(window.__sansAgents)")
    page.wait_for_function("!window.BANDINI.B.cinema", timeout=60000)      # « Beau char! »
    page.evaluate("""() => { const L = window.BANDINI, g = L.Histoire.lieu('garage'), v = L.B.mission.vehicule, j = L.B.joueur;
                            v.x = g.x; v.y = g.y; v.vitesse = 0; v.vx = 0; v.vy = 0; j.x = v.x; j.y = v.y; }""")
    page.wait_for_function("!!window.BANDINI.B.partie.missionsFaites.m1", timeout=20000)
    page.wait_for_function("!!window.BANDINI.B.scene", timeout=20000)
    page.wait_for_function("!window.BANDINI.B.scene && !window.BANDINI.B.cinema", timeout=90000)
    assert page.evaluate("!window.BANDINI.Histoire.donneur('ti_guy')"), "Ti-Guy n'est pas rentre au garage"
    assert erreurs == []


#: Une manette que le navigateur croit branchee : `window.__manette(boutons)` la
#: tient, `navigator.getGamepads` la rend. Assez pour l'API Manette de Chromium,
#: que Playwright ne sait pas imiter.
FAUSSE_MANETTE = """
window.__pad = null;
navigator.getGamepads = function () { return window.__pad ? [window.__pad] : []; };
window.__manette = function (id, boutons) {
  const b = []; for (let i = 0; i < 17; i++) b.push({ pressed: boutons.indexOf(i) >= 0, value: boutons.indexOf(i) >= 0 ? 1 : 0 });
  window.__pad = { id: id, mapping: 'standard', connected: true, axes: [0, 0, 0, 0], buttons: b, index: 0 };
};
"""


def test_les_commandes_parlent_la_manette_du_titre_a_la_ville(page, serveur, erreurs):
    """Demande de Martin (21 sept. 2026) : une manette branchee, l'aide dit SUR
    QUEL BOUTON peser. Tout a la manette, comme il joue : le titre lit ses
    lettres, A commence, et l'ecran COMMANDES du bout de l'ouverture allume ce
    qu'on touche sans se fermer — seul A le ferme. ⚠️ Visibilite a l'ECRAN
    (`is_visible`), jamais l'attribut `hidden` (voir `.boutons`)."""
    page.add_init_script(FAUSSE_MANETTE)
    page.goto(serveur)
    attendre_titre(page)
    x = "Xbox Wireless Controller (STANDARD GAMEPAD Vendor: 045e Product: 0b13)"

    def appui(*boutons):
        page.evaluate("([i, b]) => window.__manette(i, b)", [x, list(boutons)])
        page.wait_for_timeout(120)
        page.evaluate("([i]) => window.__manette(i, [])", [x])
        page.wait_for_timeout(120)

    assert page.is_visible("#aide-clavier") and not page.is_visible("#aide-manette")
    appui(1)                                          # B : rien au titre, mais on tient la manette
    page.wait_for_function("!document.getElementById('aide-manette').hidden")
    assert page.is_visible("#aide-manette") and not page.is_visible("#aide-clavier")
    assert page.inner_text("#aide-manette-jouer") == "A"
    appui(0)                                          # A : JOUER
    page.wait_for_selector('#bandini[data-etat="jeu"]')
    page.evaluate("window.BANDINI.Histoire.passerOuverture()")
    page.wait_for_function(COMMANDES_OUVERTES)
    page.evaluate("([i]) => window.__manette(i, [1])", [x])            # B tenu
    page.wait_for_timeout(150)
    allumees = page.evaluate("""() => { const L = window.BANDINI;
        return L.Hud.lignesDAide(L.B.defs.manettes.pages[L.B.menu.page], L.Entree.appareil)
            .filter(li => li.allume).map(li => li.c); }""")
    assert allumees == ["esquive"], allumees
    page.evaluate("([i]) => window.__manette(i, [])", [x])
    page.wait_for_timeout(120)
    assert page.evaluate(COMMANDES_OUVERTES), "B ne ferme pas l'aide : on y essaie ses boutons"
    appui(0)
    page.wait_for_function("!window.BANDINI.B.menu")
    assert erreurs == []


def test_les_commandes_tactiles_sont_grandes_et_visibles(browser, serveur):
    contexte = browser.new_context(viewport={"width": 844, "height": 390}, has_touch=True, is_mobile=True,
                                   device_scale_factor=2)
    page = contexte.new_page()
    erreurs = []
    page.on("pageerror", lambda e: erreurs.append(str(e)))
    page.goto(serveur)
    attendre_titre(page)
    page.tap("#bouton-jouer")
    page.wait_for_selector('#bandini[data-etat="jeu"]')
    # ⚠️ Au doigt aussi, l'ouverture fige la ville : ce juge mesure des
    # pastilles et un joystick, pas une scene. Elle a les siens.
    page.evaluate("window.BANDINI.Histoire.passerOuverture()")
    page.wait_for_function("!window.BANDINI.B.ouverture")
    # ⚠️ L'ecran COMMANDES est ouvert ici, et c'est voulu : ses lignes sont des
    # ancres du HUD, et la mesure plus bas verifie qu'aucune ne finit sous un
    # pouce — au telephone en paysage, les boutons couvrent le coin en bas a
    # droite, et le plan centre y poussait FRAPPE et SPRINT (vu a la capture).
    page.wait_for_function(COMMANDES_OUVERTES)
    page.wait_for_timeout(100)
    assert page.evaluate("window.BANDINI.Hud.ancres().filter(a => a.nom === 'commandes').length") >= 6
    assert page.evaluate("document.body.classList.contains('tactile')")
    # SAISIR (les projections, 25 sept. 2026) : un peu plus petit, c'est un geste de moins souvent.
    for action, minimum in (("attaque", 64), ("action", 64), ("esquive", 64), ("arme", 64), ("saisir", 56),
                            ("pause", 44)):
        boite = page.locator(f'#tactile b[data-a="{action}"]').bounding_box()
        assert boite, action
        assert boite["width"] >= minimum and boite["height"] >= minimum, (action, boite)
        assert boite["x"] >= 0 and boite["y"] >= 0
        assert boite["x"] + boite["width"] <= 844 and boite["y"] + boite["height"] <= 390
    croix = page.locator("#croix").bounding_box()
    assert croix["width"] >= 120

    # ⚠️ Aucun chevauchement : deux pastilles qui se mordent, c'est un pouce
    # qui frappe quand il voulait courir. Le defaut s'etait glisse entre
    # ACTION et COURS sans que rien ne le dise.
    boites = {a: page.locator(f'#tactile b[data-a="{a}"]').bounding_box()
              for a in ("attaque", "action", "esquive", "arme", "saisir", "pause", "plein")}
    boites["croix"] = croix
    noms = sorted(boites)
    for i, un in enumerate(noms):
        for autre in noms[i + 1:]:
            a, b = boites[un], boites[autre]
            chevauche = (a["x"] < b["x"] + b["width"] and b["x"] < a["x"] + a["width"]
                         and a["y"] < b["y"] + b["height"] and b["y"] < a["y"] + a["height"])
            assert not chevauche, f"{un} et {autre} se chevauchent : {a} / {b}"

    # ⚠️ Et le HUD DESSINE ne doit pas finir sous un pouce non plus : l'argent
    # et l'arme courante se cachaient derriere les boutons, ce qu'aucune
    # mesure de boites DOM ne pouvait voir.
    toile = page.locator("#toile").bounding_box()
    echelle = toile["width"] / 480.0
    for ancre in page.evaluate("window.BANDINI.Hud.ancres()"):
        boite = {"x": toile["x"] + ancre["x"] * echelle, "y": toile["y"] + ancre["y"] * echelle,
                 "width": ancre["l"] * echelle, "height": ancre["h"] * echelle}
        for nom, bouton in boites.items():
            if nom == "croix":
                continue
            chevauche = (boite["x"] < bouton["x"] + bouton["width"]
                         and bouton["x"] < boite["x"] + boite["width"]
                         and boite["y"] < bouton["y"] + bouton["height"]
                         and bouton["y"] < boite["y"] + boite["height"])
            assert not chevauche, f"le HUD « {ancre['nom']} » passe sous le bouton {nom}"
    # L'aide se ferme au DOIGT : son pied dit « CHOISIR », le nom du bouton ACTION dans un menu.
    assert page.inner_text('#tactile b[data-a="action"]') == "CHOISIR"
    page.tap('#tactile b[data-a="action"]')
    page.wait_for_function("!window.BANDINI.B.menu")
    # Glisser sur le joystick deplace le joueur.
    x0 = page.evaluate("window.BANDINI.B.joueur.x")
    cx, cy = croix["x"] + croix["width"] / 2, croix["y"] + croix["height"] / 2
    page.mouse.move(cx, cy)
    page.mouse.down()
    page.mouse.move(cx + 55, cy, steps=4)
    page.wait_for_timeout(500)
    page.mouse.up()
    x1 = page.evaluate("window.BANDINI.B.joueur.x")
    assert x1 > x0 + 15
    assert erreurs == []
    contexte.close()


def test_le_pincement_est_bloque_par_les_trois_couches():
    with open(os.path.join(RACINE, "templates", "base.html"), encoding="utf-8") as f:
        base = f.read()
    with open(os.path.join(RACINE, "static", "css", "styles.css"), encoding="utf-8") as f:
        css = f.read()
    with open(os.path.join(RACINE, "static", "js", "entree.js"), encoding="utf-8") as f:
        js = f.read()
    meta = re.search(r'<meta name="viewport" content="([^"]+)"', base).group(1)
    assert "user-scalable=no" in meta and "viewport-fit=cover" in meta
    assert re.search(r"html,\s*body\s*\{[^}]*touch-action:\s*pan-x pan-y", css)
    assert "gesturestart" in js
    assert "env(safe-area-inset-bottom)" in css


def test_les_echantillons_se_chargent_dans_un_vrai_navigateur(page, serveur, erreurs):
    """⚠️ Le seul endroit qui prouve que les .mp3 generes se DECODENT vraiment.

    Sous Node il n'y a pas d'AudioContext, et pytest ne sait pas lire un MP3 :
    un fichier tronque passerait partout ailleurs et ne se verrait qu'a
    l'oreille, en jeu.
    """
    page.goto(serveur)
    attendre_titre(page)
    jouer(page)          # le clic reveille l'audio
    page.wait_for_selector('#bandini[data-etat="jeu"]')
    # ⚠️ Attendre l'EGALITE, pas « au moins un » : les fichiers se decodent en
    # parallele, et un test qui part au premier decode ne verrait jamais un MP3
    # tronque au fond de la liste.
    attendus = page.evaluate(
        "window.BANDINI.B.defs.audio.echantillons.filter(e => e.fichiers.length).length")
    page.wait_for_function(
        "n => window.BANDINI.Son.charges === n", arg=attendus, timeout=20000)
    assert page.evaluate("window.BANDINI.Son.charges") == attendus
    assert erreurs == []


def test_la_radio_joue_au_tour_de_cle(page, serveur, erreurs):
    """Les radios se telechargent au premier tour de cle : c'est ici, et
    seulement ici, qu'on sait que la piste de jazz se DECODE."""
    page.goto(serveur)
    attendre_titre(page)
    jouer(page)
    page.wait_for_selector('#bandini[data-etat="jeu"]')
    page.evaluate("""() => {
        const L = window.BANDINI, j = L.B.joueur;
        const v = L.Vehicules.creer('auto', j.x + 24, j.y, 0, { etat: 'stationne' });
        L.Entites.indexer();
        L.Vehicules.monter(j, v);
    }""")
    page.wait_for_function("window.BANDINI.Son.Radio.courante === 'la_brume'", timeout=20000)
    assert page.evaluate("window.BANDINI.Son.boucleActive('radio-la_brume')") is True
    page.keyboard.press("Tab")
    page.wait_for_function("window.BANDINI.Son.Radio.demandee !== 'la_brume'", timeout=5000)
    assert erreurs == []


def test_l_ambiance_et_les_voix_se_decodent(page, serveur, erreurs):
    """La musique de fond joue a pied des le premier geste, et les repliques
    des passants sont decodees : un MP3 de voix tronque ne se verrait qu'a
    l'oreille."""
    page.goto(serveur)
    attendre_titre(page)
    jouer(page)
    page.wait_for_selector('#bandini[data-etat="jeu"]')
    # ⚠️ L'ambiance de la ville ne demarre plus toute seule : chaque district
    # a maintenant la sienne, ecrite en notes (`Son.Chef`). Le fichier, lui,
    # existe toujours — et c'est ICI, et seulement ici, qu'on prouve qu'il se
    # DECODE. On le demande donc explicitement.
    page.evaluate("window.BANDINI.Son.Ambiance.jouer()")
    page.wait_for_function("window.BANDINI.Son.Ambiance.courante === 'ville'", timeout=20000)
    attendues = page.evaluate("window.BANDINI.B.defs.audio.voix.filter(v => v.fichier).length")
    page.wait_for_function(
        "n => n > 0 && window.BANDINI.B.defs.audio.voix.filter(v => v.fichier)"
        ".every(v => window.BANDINI.Son.estCharge('voix-' + v.slug))",
        arg=attendues, timeout=20000)
    assert page.evaluate("window.BANDINI.Son.boucleActive('ambiance-ville')") is True
    assert erreurs == []


def test_une_voix_de_l_histoire_se_decode_et_baisse_la_radio(page, serveur, erreurs):
    """Les repliques de l'histoire se chargent PAR MISSION, quand on parle au
    donneur : c'est ici, et seulement ici, qu'on sait que le MP3 de Ti-Guy se
    decode — et que la musique baisse pendant qu'il parle (ducking)."""
    page.goto(serveur)
    attendre_titre(page)
    jouer(page)
    page.wait_for_selector('#bandini[data-etat="jeu"]')
    # ⚠️ L'ambiance de la ville ne demarre plus toute seule : chaque district
    # a maintenant la sienne, ecrite en notes (`Son.Chef`). Le fichier, lui,
    # existe toujours — et c'est ICI, et seulement ici, qu'on prouve qu'il se
    # DECODE. On le demande donc explicitement.
    page.evaluate("window.BANDINI.Son.Ambiance.jouer()")
    page.wait_for_function("window.BANDINI.Son.Ambiance.courante === 'ville'", timeout=20000)
    # ⚠️ LES VOIX D'UNE MISSION NE SONT PLUS DANS LE PAQUET (24 sept. 2026) : elles se
    # declarent avec sa mission (`/api/mission/<slug>`). Dans le jeu, la bulle du
    # donneur la demande ; ici on la demande explicitement, avant de chercher sa voix.
    page.evaluate("window.BANDINI.Histoire.charger('m1')")
    page.wait_for_function(
        "window.BANDINI.B.defs.audio.histoire.some(v => v.mission === 'm1')", timeout=20000)
    premiere = page.evaluate("window.BANDINI.B.defs.audio.histoire.find(v => v.mission === 'm1' && v.fichier)")
    if not premiere:
        pytest.skip("aucune voix de l'histoire generee (scripts/audio_elevenlabs.py --voix)")
    page.evaluate("""() => {
        const L = window.BANDINI, j = L.B.joueur, t = L.Histoire.donneur('ti_guy');
        j.x = t.x - 16; j.y = t.y; L.Entites.indexer();
        // ⚠️ On le regarde : ACTION n'agit que sur ce qu'on regarde (test_regard_js.py).
        L.Entites.regarder(j, t.x - j.x, t.y - j.y);
        L.Missions.interagir(j);
    }""")
    assert page.evaluate("!!window.BANDINI.B.cinema"), "Ti-Guy ne parle pas"
    # La voix arrive (telechargee puis decodee) : la replique en cours la joue et la radio baisse.
    page.wait_for_function("window.BANDINI.Son.Voix.enCours !== null", timeout=20000)
    assert page.evaluate("window.BANDINI.Son.Voix.enCours.slug").startswith("ti_guy-m1-")
    assert page.evaluate("window.BANDINI.Son.Voix.ducking") is True
    assert erreurs == []


def test_la_ville_tient_le_rythme_de_nuit_a_trois_etoiles(page, serveur, erreurs):
    """Une sonde, pas un juge : Chromium sans GPU n'est pas un telephone. Elle
    mesure le temps moyen d'une image (`B.stats.ms`) de nuit, a 3 etoiles,
    au volant — le pire cas ordinaire — et ne crie que si c'est franchement
    hors de prix. Le chiffre s'imprime : c'est lui qu'on regarde."""
    page.goto(serveur)
    attendre_titre(page)
    jouer(page)
    page.wait_for_selector('#bandini[data-etat="jeu"]')
    page.evaluate("""() => {
        const L = window.BANDINI, j = L.B.joueur;
        j.intouchable = true;
        L.B.partie.heure = 0.9;
        L.Police.ajouterChaleur(9);
        const v = L.Vehicules.creer('auto', j.x + 24, j.y, 0, { etat: 'stationne' });
        L.Entites.indexer();
        L.Vehicules.monter(j, v);
    }""")
    page.wait_for_timeout(4000)
    ms = page.evaluate("window.BANDINI.B.stats.ms")
    images = page.evaluate("window.BANDINI.B.stats.images")
    entites = page.evaluate("window.BANDINI.B.entites.length")
    print(f"\n[perf] {ms:.1f} ms par image, {images} images dessinees, {entites} entites, 3 etoiles, nuit")
    assert ms < 40, f"{ms:.1f} ms par image : la ville ne tient plus le rythme"
    assert erreurs == []


def test_la_tempete_de_neige_tient_le_rythme(page, serveur, erreurs):
    """⚠️ La SONDE que le plan exigeait avant d'allumer la neige (M12) : le même pire
    cas que la nuit à trois étoiles — au volant, recherché — un soir de pleine tempête,
    l'option allumée, la charrue dehors. Le chiffre s'imprime à côté de celui de la nuit :
    c'est la différence qu'on regarde avant de mettre l'option à OUI par défaut."""
    page.goto(serveur)
    attendre_titre(page)
    jouer(page)
    page.wait_for_selector('#bandini[data-etat="jeu"]')
    page.evaluate("""() => {
        const L = window.BANDINI, j = L.B.joueur, t = L.Neige.donnees().tempete;
        j.intouchable = true;
        L.B.options.neige = true;
        L.B.partie.jour = t.premier;
        L.B.partie.heure = (t.debut_h + t.fin_h) / 2 / 24;
        L.Police.ajouterChaleur(9);
        const v = L.Vehicules.creer('auto', j.x + 24, j.y, 0, { etat: 'stationne' });
        L.Entites.indexer();
        L.Vehicules.monter(j, v);
    }""")
    page.wait_for_timeout(4000)
    etat = page.evaluate("({ ms: window.BANDINI.B.stats.ms, i: window.BANDINI.Neige.intensite(), images: window.BANDINI.B.stats.images })")
    print(f"\n[perf] {etat['ms']:.1f} ms par image, tempete {etat['i']:.2f}, {etat['images']} images, 3 etoiles")
    assert etat["i"] > 0.9, "la sonde ne mesure pas une tempête"
    assert etat["ms"] < 40, f"{etat['ms']:.1f} ms par image : la tempête ne tient pas le rythme"
    assert erreurs == []


def test_sans_geste_le_son_est_retenu_et_la_page_le_dit(page, serveur, erreurs):
    """La panne de Martin, dans un vrai navigateur.

    ⚠️ Tant que la page n'a recu aucun geste, l'AudioContext reste « suspended »
    et rien ne sort. L'API Manette ne donnant PAS de geste, on pouvait commencer
    la partie au pad et traverser toute la ville en silence. Le bandeau du titre
    est ce qui rend ce silence visible — il doit etre la AVANT qu'on joue."""
    page.goto(serveur)
    attendre_titre(page)
    etat = page.evaluate("() => ({ son: window.BANDINI.Son.etatSon(),"
                         " brut: window.BANDINI.Son.contexte.state,"
                         " cache: document.getElementById('avis-son').hidden })")
    assert etat["brut"] == "suspended", f"le navigateur accorde le son sans geste : {etat}"
    assert etat["son"] == "attente", etat
    assert etat["cache"] is False, "le silence doit se voir sur l'ecran titre"
    texte = page.locator("#avis-son").inner_text()
    assert "son" in texte.lower(), texte
    assert "touche" in texte.lower() or "clique" in texte.lower(), texte
    assert erreurs == []


def test_un_vrai_geste_rend_le_son_et_efface_le_bandeau(page, serveur, erreurs):
    page.goto(serveur)
    attendre_titre(page)
    assert page.evaluate("() => window.BANDINI.Son.enAttente()") is True
    jouer(page)
    page.wait_for_selector('#bandini[data-etat="jeu"]')
    page.wait_for_function("window.BANDINI.Son.etatSon() === 'actif'", timeout=10000)
    assert page.evaluate("() => document.getElementById('avis-son').hidden") is True
    assert erreurs == []


def test_les_options_disent_l_etat_du_son(page, serveur, erreurs):
    """OPTIONS est un onglet du classeur de la PAUSE : on le CLIQUE a la souris,
    sur la vraie toile etiree en CSS — le seul juge d'un clic reel sur un menu
    (`Hud.toucherMenu` ramene le point aux 480 x 270 pixels du jeu)."""
    page.goto(serveur)
    attendre_titre(page)
    jouer(page)
    page.wait_for_selector('#bandini[data-etat="jeu"]')
    page.evaluate("window.BANDINI.Jeu.pause()")
    page.wait_for_function("window.BANDINI.Hud.ciblesDuMenu().some(q => q.onglet === 'options')")
    z = page.evaluate("window.BANDINI.Hud.ciblesDuMenu().find(q => q.onglet === 'options')")
    boite = page.locator("canvas").first.bounding_box()
    page.mouse.click(boite["x"] + (z["x"] + z["l"] / 2) * boite["width"] / 480,
                     boite["y"] + (z["y"] + z["h"] / 2) * boite["height"] / 270)
    page.wait_for_function("window.BANDINI.B.menu && window.BANDINI.B.menu.titre === 'OPTIONS'")
    ligne = page.evaluate("""() => {
        const L = window.BANDINI;
        const son = L.B.menu.items.find(x => x.libelle === 'SON');
        return { titre: L.B.menu.titre, detail: son && son.detail, actif: son && son.actif };
    }""")
    assert ligne["titre"] == "OPTIONS"
    assert ligne["detail"] == "ACTIF", ligne
    assert ligne["actif"] is False
    assert erreurs == []


#: Une sonde posee sur la sortie audio : elle mesure ce qui SORT vraiment.
#: ⚠️ C'est le seul juge qui aurait attrape le silence du 13 sept. 2026 — tout
#: le reste (fichiers servis, tampons decodes, sources demarrees, volumes
#: justes) etait parfaitement vert pendant qu'il ne sortait rien.
SONDE_AUDIO = """
window.__analyseur = null;
(function () {
  const C = AudioNode.prototype.connect;
  AudioNode.prototype.connect = function (cible) {
    if (cible === this.context.destination) {
      if (!window.__analyseur) {
        window.__analyseur = this.context.createAnalyser();
        window.__analyseur.fftSize = 2048;
        C.call(window.__analyseur, this.context.destination);
      }
      C.call(this, window.__analyseur);
      return cible;
    }
    return C.apply(this, arguments);
  };
})();
window.__mesure = function (ms) {
  return new Promise(function (ok) {
    const an = window.__analyseur;
    if (!an) return ok(0);
    const buf = new Float32Array(an.fftSize);
    let pire = 0;
    const t = setInterval(function () {
      an.getFloatTimeDomainData(buf);
      let s = 0;
      for (let i = 0; i < buf.length; i++) s += buf[i] * buf[i];
      pire = Math.max(pire, Math.sqrt(s / buf.length));
    }, 30);
    setTimeout(function () { clearInterval(t); ok(pire); }, ms);
  });
};
"""

#: -60 dB : largement sous ce qu'on mesure (-26 dB), largement au-dessus de zero.
#: On juge « ca sort », pas « ca sort a tel niveau » — le niveau, c'est l'oreille.
PLANCHER = 0.001


def test_tout_ce_qui_doit_s_entendre_s_entend(page, serveur, erreurs):
    """⚠️ LE juge de bout en bout de l'audio. Un son peut se telecharger, se
    decoder, demarrer, avoir le bon volume et sembler relie a la sortie — et ne
    rien produire, si sa source n'entre dans aucune chaîne. C'est arrive DEUX
    fois le 13 sept. 2026 (`echantillon()` puis `Voix.parler()`), et aucun de nos
    juges ne l'a vu : ils verifiaient tous l'intention. Celui-ci ecoute la
    sortie, pour les cinq familles de sons a la fois — en une seule page, parce
    qu'un contexte audio par test finit par saturer le navigateur."""
    page.add_init_script(SONDE_AUDIO)
    page.goto(serveur)
    page.wait_for_selector('#bandini[data-etat="titre"]', timeout=45000)
    jouer(page)          # un vrai geste : le son est accorde
    page.wait_for_selector('#bandini[data-etat="jeu"]', timeout=45000)
    page.wait_for_function("window.BANDINI.Son.charges > 0", timeout=45000)
    page.wait_for_function(
        "() => (window.BANDINI.B.defs.audio.voix || []).some("
        "v => v.fichier && window.BANDINI.Son.estCharge('voix-' + v.slug))",
        timeout=45000)

    def mesurer(js):
        return page.evaluate("() => { const p = window.__mesure(1200); (%s)(); return p; }" % js)

    niveaux = {
        "la synthese": mesurer("() => BANDINI.Son.ton(440, 0.6, 'square', 0.9)"),
        "un bruitage": mesurer("() => BANDINI.Son.echantillon('coup', { volume: 1 })"),
        "une voix de passant": mesurer("""() => {
            const v = BANDINI.B.defs.audio.voix.find(x => x.fichier);
            BANDINI.Son.echantillon('voix-' + v.slug, { volume: 1 });
        }"""),
    }

    # L'ambiance tourne en boucle : on l'ecoute sans rien declencher. Elle se
    # telecharge apres les bruitages, alors on l'ATTEND plutot que de l'esperer.
    page.evaluate("window.BANDINI.Son.Ambiance.jouer()")
    page.wait_for_function("() => window.BANDINI.Son.boucleActive('ambiance-ville')", timeout=45000)
    niveaux["l'ambiance"] = page.evaluate(
        "() => { BANDINI.Son.reglerBoucle('ambiance-ville', 1); return window.__mesure(1500); }")

    # Une replique de l'histoire, la ville coupee pour n'entendre qu'elle.
    # ⚠️ Sa mission d'abord : les voix d'une mission ne sont plus dans le paquet.
    page.evaluate("window.BANDINI.Histoire.charger('m1')")
    page.wait_for_function(
        "window.BANDINI.B.defs.audio.histoire.some(v => v.mission === 'm1')", timeout=20000)
    premiere = page.evaluate(
        "window.BANDINI.B.defs.audio.histoire.find(v => v.mission === 'm1' && v.fichier)")
    if premiere:
        page.evaluate("(m) => window.BANDINI.Son.Voix.chargerHistoire(m)", premiere["mission"])
        page.wait_for_function(
            "s => window.BANDINI.Son.estCharge('histoire-' + s)", arg=premiere["slug"], timeout=45000)
        niveaux["une replique"] = page.evaluate("""(s) => {
            const S = window.BANDINI.Son;
            // ⚠️ NET, et dans cet ordre : `Ambiance.arreter()` fond maintenant sur deux
            // secondes, et la replique serait mesuree par-dessus l'ambiance qui s'eteint.
            S.Voix.couper(); S.boucle('ambiance-ville', false); S.Ambiance.arreter();
            const p = window.__mesure(1500);
            S.Voix.parler(s, {});
            return p;
        }""", premiere["slug"])

    # Le theme du menu, de retour au titre.
    page.evaluate("() => BANDINI.Jeu.retourTitre()")
    page.wait_for_timeout(1500)
    assert page.evaluate("() => BANDINI.Son.Mus.courante") == "titre"
    niveaux["le theme du menu"] = page.evaluate("() => window.__mesure(2500)")

    muets = [nom for nom, v in niveaux.items() if v <= PLANCHER]
    print("\n[audio] " + " · ".join(f"{nom} {v:.4f}" for nom, v in niveaux.items()))
    assert not muets, f"ca « joue » mais on n'entend rien : {muets} (niveaux {niveaux})"
    assert erreurs == []


#: Une sonde sur les fondus : elle garde chaque courbe posee et chaque arret de
#: source, avec le PARAMETRE lui-meme — c'est ce qui permet d'en lire la valeur
#: pendant qu'il descend, sans deviner quel noeud est lequel.
SONDE_FONDU = """
window.__courbes = []; window.__arrets = [];
(function () {
  const C = AudioParam.prototype.setValueCurveAtTime;
  AudioParam.prototype.setValueCurveAtTime = function (v, t, d) {
    window.__courbes.push({ param: this, sens: v[v.length - 1] > v[0] ? 'entree' : 'sortie', t: t, duree: d });
    return C.apply(this, arguments);
  };
  const S = AudioScheduledSourceNode.prototype.stop;
  AudioBufferSourceNode.prototype.stop = function (t) {
    window.__arrets.push({ apres: t === undefined ? 0 : t - this.context.currentTime });
    return S.apply(this, arguments);
  };
})();
"""


def test_le_fondu_enchaine_marche_pour_de_vrai_dans_le_navigateur(page, serveur, erreurs):
    """⚠️ Le faux contexte du banc dit ce que le jeu DEMANDE, pas ce que le
    navigateur en fait. Ici, un vrai `AudioContext` : les deux courbes sont
    acceptees (pas de `NotSupportedError`), l'ancienne piste descend pendant que
    la nouvelle monte — a puissance constante —, et la source de l'ancienne ne
    s'arrete qu'apres la fin de sa courbe. Demande de Martin (20 sept. 2026) :
    « les transitions de musique doivent toujours se faire en crossover »."""
    page.add_init_script(SONDE_FONDU)
    page.goto(serveur)
    attendre_titre(page)
    jouer(page)
    page.wait_for_function("window.BANDINI.Son.charges > 0", timeout=45000)
    # ⚠️ Le jukebox TIENT LA MAIN du chef d'orchestre : la ville ne remet pas son
    # ambiance pendant qu'on mesure. Deux morceaux dans le cache d'abord (le
    # premier telechargement, lui, n'est pas un fondu qu'on puisse dater).
    for slug in ("amb_quais", "amb_pointe"):
        page.evaluate("(s) => { BANDINI.B.jukebox = s; }", slug)
        page.wait_for_function("(s) => BANDINI.Son.boucleActive('musique-' + s)", arg=slug, timeout=45000)
    avant = page.evaluate("() => window.__courbes.length")
    fondu = page.evaluate("() => BANDINI.B.defs.audio.musique.fondu_s")
    page.evaluate("() => { window.__arrets.length = 0; BANDINI.B.jukebox = 'amb_quais'; }")
    page.wait_for_function("(n) => window.__courbes.length >= n + 2", arg=avant, timeout=15000)
    mesures = page.evaluate("""() => new Promise(function (ok) {
        const neuves = window.__courbes.slice(%d);
        const entree = neuves.find(function (c) { return c.sens === 'entree'; });
        const sortie = neuves.find(function (c) { return c.sens === 'sortie'; });
        const ctx = BANDINI.Son.contexte;
        const lu = [];
        const t = setInterval(function () {
          lu.push({ e: entree.param.value, s: sortie.param.value });
        }, 250);
        setTimeout(function () {
          clearInterval(t);
          ok({ lu: lu, neuves: neuves.map(function (c) { return { sens: c.sens, t: c.t, duree: c.duree }; }),
               arrets: window.__arrets, actives: [BANDINI.Son.boucleActive('musique-amb_quais'), BANDINI.Son.boucleActive('musique-amb_pointe')] });
        }, %d);
    })""" % (avant, int((fondu + 0.6) * 1000)))
    sens = sorted(c["sens"] for c in mesures["neuves"])
    assert sens == ["entree", "sortie"], f"un fondu, c'est une courbe qui monte et une qui descend : {mesures['neuves']}"
    for c in mesures["neuves"]:
        assert c["duree"] == fondu, f"la courbe ne suit pas fondu_s ({fondu}) : {c}"
    e, s = [next(c for c in mesures["neuves"] if c["sens"] == k) for k in ("entree", "sortie")]
    assert abs(e["t"] - s["t"]) < 0.5, f"les deux courbes ne partent pas ensemble : {e} {s}"
    lu = mesures["lu"]
    assert lu[-1]["e"] > 0.95 and lu[-1]["s"] < 0.05, f"le fondu n'arrive pas au bout : {lu[-1]}"
    assert all(b["e"] >= a["e"] - 1e-6 for a, b in zip(lu, lu[1:])), f"la nouvelle ne fait pas que monter : {lu}"
    assert all(b["s"] <= a["s"] + 1e-6 for a, b in zip(lu, lu[1:])), f"l'ancienne ne fait pas que baisser : {lu}"
    # Puissance constante : au milieu, ni creux ni bosse (deux fois 0,707 valent 1).
    puissances = [m["e"] ** 2 + m["s"] ** 2 for m in lu]
    assert all(0.8 < p < 1.2 for p in puissances), f"le fondu creuse ou gonfle le volume : {puissances}"
    assert mesures["actives"] == [True, False], f"seule la nouvelle doit etre une boucle active : {mesures['actives']}"
    # L'ancienne source ne s'arrete qu'APRES sa courbe.
    assert mesures["arrets"], "l'ancienne piste n'a jamais ete arretee : elle jouerait pour toujours"
    assert max(a["apres"] for a in mesures["arrets"]) >= fondu - 0.2, \
        f"l'ancienne piste est coupee net : {mesures['arrets']}"
    assert erreurs == []


#: Un faux casque pour un VRAI WebGL : la session ne fait que cadencer (sur
#: l'horloge de la fenetre, comme un Quest), une seule vue droit devant en
#: perspective, et le framebuffer par defaut du canevas en guise d'oeil.
FAUX_CASQUE = """
(function () {
  const etat = { images: 0, gl: null };
  window.__casque = etat;
  const getContext = HTMLCanvasElement.prototype.getContext;
  HTMLCanvasElement.prototype.getContext = function (type, opts) {
    if (type !== 'webgl') return getContext.call(this, type, opts);
    return (etat.gl = getContext.call(this, type, Object.assign({}, opts, { preserveDrawingBuffer: true })));
  };
  const f = 1 / Math.tan(Math.PI / 4), n = 0.1, l = 100;
  const vue = {
    projectionMatrix: new Float32Array([f, 0, 0, 0, 0, f, 0, 0, 0, 0, (l + n) / (n - l), -1, 0, 0, 2 * l * n / (n - l), 0]),
    transform: { inverse: { matrix: new Float32Array([1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1]) } },
  };
  const cadre = { getViewerPose: function () { return { views: [vue] }; } };
  const ecouteurs = {};
  const session = {
    inputSources: [], visibilityState: 'visible',
    addEventListener: function (t, g) { (ecouteurs[t] = ecouteurs[t] || []).push(g); },
    updateRenderState: function () {},
    requestReferenceSpace: function () { return Promise.resolve({}); },
    requestAnimationFrame: function (cb) {
      return window.requestAnimationFrame(function (t) { etat.images++; cb(t, cadre); });
    },
    end: function () { (ecouteurs.end || []).forEach(function (g) { g({}); }); return Promise.resolve(); },
  };
  Object.defineProperty(navigator, 'xr', { configurable: true, value: {
    isSessionSupported: function (mode) { return Promise.resolve(mode === 'immersive-vr'); },
    requestSession: function () { return Promise.resolve(session); },
  } });
  window.XRWebGLLayer = function (s, gl) {
    this.framebuffer = null;
    this.getViewport = function () { return { x: 0, y: 0, width: gl.drawingBufferWidth, height: gl.drawingBufferHeight }; };
  };
  etat.lire = function () {
    const gl = etat.gl, w = gl.drawingBufferWidth, h = gl.drawingBufferHeight;
    // Un point de la vue en coordonnees normalisees (-1..1, y vers le haut).
    function px(x, y) {
      const b = new Uint8Array(4);
      gl.readPixels(Math.round((x + 1) / 2 * w), Math.round((y + 1) / 2 * h), 1, 1, gl.RGBA, gl.UNSIGNED_BYTE, b);
      return [b[0], b[1], b[2]];
    }
    return { erreur: gl.getError(), coin: px(-0.98, -0.98),
             hautGauche: px(-0.3, 0.15), hautDroite: px(0.3, 0.15),
             basGauche: px(-0.3, -0.3), basDroite: px(0.3, -0.3) };
  };
})();
"""


def test_le_casque_montre_la_toile_dans_un_vrai_webgl(page, serveur, erreurs):
    """⚠️ Le banc Node n'a qu'un faux WebGL qui COMPTE ses appels : il ne compile
    aucun nuanceur et n'echantillonne aucune texture. Une texture incomplete, un
    attribut mal decale ou une matrice dans le mauvais ordre y restent verts — et
    dans le casque, Martin verrait du noir. Ici c'est Chromium qui dessine.

    La toile est repeinte en quatre quarts de couleur apres chaque image du jeu :
    chaque quart doit sortir a SA place dans la vue (une image a l'envers ou en
    miroir passerait partout ailleurs), et le coin de la vue — a cote de
    l'ecran — garder le noir du fond."""
    page.add_init_script(FAUX_CASQUE)
    page.goto(serveur)
    attendre_titre(page)
    assert page.is_visible("#bouton-casque"), "un navigateur qui ouvre une session immersive doit voir le bouton"
    if not page.evaluate("!!document.createElement('canvas').getContext('webgl')"):
        pytest.skip("ce Chromium n'a pas de WebGL")
    page.evaluate("""() => {
        const J = window.BANDINI.Jeu, avancer = J.avancer;
        J.avancer = function (t) {
            avancer(t);
            const toile = document.getElementById('toile'), c = toile.getContext('2d');
            const w = toile.width / 2, h = toile.height / 2;
            c.setTransform(1, 0, 0, 1, 0, 0);
            [['#ff00ff', 0, 0], ['#ffff00', w, 0], ['#00ffff', 0, h], ['#00ff00', w, h]].forEach(function (q) {
                c.fillStyle = q[0]; c.fillRect(q[1], q[2], w, h);
            });
        };
    }""")
    page.click("#bouton-casque")
    page.wait_for_selector('#bandini[data-etat="jeu"]')
    page.wait_for_function("window.__casque.images >= 10")
    r = page.evaluate("window.__casque.lire()")
    assert r["erreur"] == 0, f"WebGL a leve l'erreur {r['erreur']}"
    vu = {q: r[q] for q in ("hautGauche", "hautDroite", "basGauche", "basDroite")}
    assert vu == {"hautGauche": [255, 0, 255], "hautDroite": [255, 255, 0],
                  "basGauche": [0, 255, 255], "basDroite": [0, 255, 0]}, \
        f"l'ecran du casque ne montre pas la toile a l'endroit : {vu}"
    assert r["coin"] == [11, 10, 18], f"autour de l'ecran, le fond doit etre le noir du jeu : {r['coin']}"
    assert page.evaluate("window.BANDINI.Base.SCALE") == 3
    assert erreurs == []


# --- Le compte (M14, 2e vague) ---------------------------------------------------------


def test_creer_un_compte_de_bout_en_bout(page, serveur, erreurs):
    """Le vrai chemin : l'écran, le POST, SQLite, le cookie, l'écran qui suit.

    ⚠️ Et une chose que le banc ne peut pas voir : le formulaire doit DISPARAÎTRE
    une fois connecté. `hidden` ne suffit pas — `.compte-form` est en `display:
    flex`, qui bat l'attribut, et le banc lisait pourtant `hidden === true`. Un
    juge qui regarde la propriété plutôt que l'écran aurait laissé passer un
    formulaire de connexion affiché sous le nom de celui qui est connecté."""
    page.goto(serveur)
    attendre_titre(page)
    assert page.text_content("#bouton-compte") == "Compte"
    page.click("#bouton-compte")
    page.wait_for_selector("#voile-compte:not([hidden])")
    assert page.is_visible("#compte-form")

    page.fill("#compte-pseudo", "Martin")
    page.fill("#compte-passe", "un-mot-de-passe")
    page.fill("#compte-courriel", "martin@exemple.ca")
    page.click("#bouton-compte-inscription")
    page.wait_for_function("document.getElementById('compte-parties').children.length === 3", timeout=10000)

    assert not page.is_visible("#compte-form"), "connecté, on ne redemande pas un mot de passe"
    assert page.is_visible("#bouton-compte-deconnexion")
    assert page.text_content("#bouton-compte") == "Compte : Martin"
    assert page.input_value("#compte-passe") == "", "le mot de passe ne traîne pas dans un champ"
    # ⚠️ Le seul mot qui dit que ça a marché : il vivait DANS le formulaire, donc
    # il se cachait avec lui à la seconde où il servait.
    assert page.is_visible("#compte-etat") and "Martin" in page.text_content("#compte-etat")
    assert page.evaluate("window.BANDINI.Compte.etat().etat") == "ouvert"
    # ⚠️ Le jeton d'appareil est un cookie `HttpOnly` : le JS de la page ne doit
    # pas pouvoir le lire, sinon une seule faille d'injection ouvrirait le compte.
    assert "bandini-appareil" not in page.evaluate("document.cookie")
    jeton = [c for c in page.context.cookies() if c["name"] == "bandini-appareil"]
    assert jeton and jeton[0]["httpOnly"] and jeton[0]["path"] == "/api/compte"
    assert erreurs == []


def test_le_compte_ne_barre_jamais_le_chemin_de_jouer(page, serveur, erreurs):
    """⚠️ Serveur de comptes en panne (500 sur toutes ses routes) : la ville
    s'ouvre, JOUER joue, et l'écran du compte le dit sans drame."""
    page.route("**/api/compte/**", lambda route: route.fulfill(status=500, body="{}",
                                                              content_type="application/json"))
    page.goto(serveur)
    attendre_titre(page)
    jouer(page)
    assert page.get_attribute("#bandini", "data-etat") == "jeu"


# --- Le NIP (M14, 3e vague) --------------------------------------------------------------


def visibles(page, *ids):
    """Ce que le joueur VOIT : `is_visible`, jamais l'attribut `hidden` — le banc lisait
    `hidden === true` sur un formulaire encore affiche (2e vague), et sur `nip-retrait`
    encore affiche dans les quatre etats (3e vague)."""
    return {i: page.is_visible("#" + i) for i in ids}


NIP_ELEMENTS = ("nip-form", "compte-form", "nip-activer-form", "nip-retrait", "bouton-nip-retirer",
                "bouton-compte-deconnexion")


def test_activer_un_nip_puis_le_retrouver_au_rechargement(page, serveur, erreurs):
    """De bout en bout, avec un VRAI rechargement de page (localStorage survit, le
    cookie httpOnly aussi — c'est justement lui que le NIP protège) : créer un
    compte, activer un NIP, recharger, se faire demander le NIP, et déverrouiller.

    ⚠️ Son PROPRE pseudo : le fixture `serveur` est celui de toute la session, donc une
    seule base — « Martin » est déjà pris par le juge du compte, et le second
    `inscription` rendait 409 dans la suite complète alors que ce juge passait seul."""
    page.goto(serveur)
    attendre_titre(page)
    page.click("#bouton-compte")
    # ⚠️ FERME : ni reglage du NIP, ni bouton pour le retirer, ni deconnexion.
    assert visibles(page, *NIP_ELEMENTS) == {"nip-form": False, "compte-form": True, "nip-activer-form": False,
                                             "nip-retrait": False, "bouton-nip-retirer": False,
                                             "bouton-compte-deconnexion": False}
    page.fill("#compte-pseudo", "Nadia")
    page.fill("#compte-passe", "un-mot-de-passe")
    page.click("#bouton-compte-inscription")
    page.wait_for_function("document.getElementById('compte-parties').children.length === 3", timeout=10000)

    # OUVERT SANS NIP : on peut en ajouter un, pas en retirer un qui n'existe pas.
    assert visibles(page, *NIP_ELEMENTS) == {"nip-form": False, "compte-form": False, "nip-activer-form": True,
                                             "nip-retrait": False, "bouton-nip-retirer": False,
                                             "bouton-compte-deconnexion": True}
    page.fill("#nip-nouveau", "4821")
    page.click("#bouton-nip-activer")
    page.wait_for_function("window.BANDINI.Compte.etat().nipConfigure === true", timeout=5000)
    # OUVERT AVEC NIP : on peut le retirer, plus en ajouter.
    assert visibles(page, *NIP_ELEMENTS) == {"nip-form": False, "compte-form": False, "nip-activer-form": False,
                                             "nip-retrait": True, "bouton-nip-retirer": True,
                                             "bouton-compte-deconnexion": True}

    page.reload()
    attendre_titre(page)
    assert page.evaluate("window.BANDINI.Compte.etat().etat") == "verrouille"
    # ⚠️ Verrouille ou pas, JOUER doit rester JOUER : un compte est un confort.
    assert page.is_visible("#bouton-jouer")

    page.click("#bouton-compte")
    # ⚠️ VERROUILLE : le NIP SEUL. « Retirer le NIP » s'affichait ici, et retirait le
    # verrou sans le NIP — le bouton ne doit pas etre a l'ecran, ni cliquable.
    assert visibles(page, *NIP_ELEMENTS) == {"nip-form": True, "compte-form": False, "nip-activer-form": False,
                                             "nip-retrait": False, "bouton-nip-retirer": False,
                                             "bouton-compte-deconnexion": False}

    page.fill("#nip-code", "4821")
    page.click("#nip-form button[type=submit]")
    page.wait_for_function("window.BANDINI.Compte.etat().etat === 'ouvert'", timeout=5000)
    assert page.text_content("#bouton-compte") == "Compte : Nadia"
    assert erreurs == []


def test_le_nip_ne_bloque_jamais_jouer(page, serveur, erreurs):
    """Un appareil verrouillé (NIP configuré, pas encore tapé) : JOUER joue quand
    même, sans un seul appel au serveur des comptes."""
    appels = []

    def noter(route):
        appels.append(route.request.url)
        route.continue_()

    page.route("**/api/compte/**", noter)
    page.goto(serveur)
    attendre_titre(page)
    page.evaluate("""() => {
        localStorage.setItem('bandini-nip-v1', JSON.stringify({ sel: 'AA==', iv: 'AA==', corps: 'AA==', essais: 0 }));
    }""")
    page.reload()
    attendre_titre(page)
    assert page.evaluate("window.BANDINI.Compte.etat().etat") == "verrouille"
    appels_avant_jeu = list(appels)
    jouer(page)
    assert page.get_attribute("#bandini", "data-etat") == "jeu"
    assert appels == appels_avant_jeu, "verrouille ne doit jamais parler au serveur des comptes"
    assert erreurs == []


# --- Effacer son compte (M14, 4e vague) --------------------------------------------------

EFFACER_ELEMENTS = ("compte-effacer-ligne", "compte-effacer-form", "compte-garde")


def test_effacer_son_compte_de_bout_en_bout(page, serveur, erreurs):
    """Le vrai chemin, sur le vrai serveur : s'inscrire, refuser un mauvais mot de passe,
    effacer, puis — la seule preuve qu'un banc ne peut pas donner — **reprendre le même
    pseudo**, ce qui n'est possible que si le compte a vraiment disparu.

    ⚠️ Son PROPRE pseudo (le fixture `serveur` est partagé par toute la session)."""
    page.goto(serveur)
    attendre_titre(page)
    page.click("#bouton-compte")
    # FERME : la page « ce qu'on garde » se lit, mais rien à effacer.
    assert visibles(page, *EFFACER_ELEMENTS) == {"compte-effacer-ligne": False, "compte-effacer-form": False,
                                                 "compte-garde": True}
    page.fill("#compte-pseudo", "Leila")
    page.fill("#compte-passe", "un-mot-de-passe")
    page.click("#bouton-compte-inscription")
    page.wait_for_function("document.getElementById('compte-parties').children.length === 3", timeout=10000)

    # OUVERT : le bouton, pas encore la confirmation.
    assert visibles(page, *EFFACER_ELEMENTS) == {"compte-effacer-ligne": True, "compte-effacer-form": False,
                                                 "compte-garde": True}
    page.click("#bouton-compte-effacer")
    assert visibles(page, *EFFACER_ELEMENTS) == {"compte-effacer-ligne": False, "compte-effacer-form": True,
                                                 "compte-garde": True}

    # Un mauvais mot de passe : rien n'est effacé, on reste connecté (403, pas 401).
    page.fill("#compte-effacer-passe", "un-mauvais-mot-de-passe")
    page.click("#bouton-compte-effacer-confirmer")
    page.wait_for_function("document.getElementById('compte-effacer-etat').textContent.includes('incorrect')")
    assert page.text_content("#bouton-compte") == "Compte : Leila"
    assert page.input_value("#compte-effacer-passe") == "", "le mot de passe ne reste pas dans le champ"
    assert page.evaluate("window.BANDINI.Compte.etat().etat") == "ouvert"
    assert page.is_visible("#compte-effacer-form"), "la confirmation reste ouverte : on peut retaper"

    # Le bon : le compte disparaît, l'appareil est délié, le message se lit encore.
    page.fill("#compte-effacer-passe", "un-mot-de-passe")
    page.click("#bouton-compte-effacer-confirmer")
    page.wait_for_function("window.BANDINI.Compte.etat().etat === 'ferme'", timeout=10000)
    assert page.text_content("#bouton-compte") == "Compte"
    assert page.is_visible("#compte-form"), "retour au formulaire de connexion"
    assert visibles(page, *EFFACER_ELEMENTS) == {"compte-effacer-ligne": False, "compte-effacer-form": False,
                                                 "compte-garde": True}
    # ⚠️ Le seul mot qui dit ce qui s'est passé vit dehors du formulaire qui vient de se refermer.
    assert page.is_visible("#compte-etat") and "effacé" in page.text_content("#compte-etat")
    assert not [c for c in page.context.cookies() if c["name"] == "bandini-appareil"], "le cookie s'efface"

    # LA PREUVE : le pseudo est libre. Un compte encore là aurait rendu 409 « déjà pris ».
    page.fill("#compte-pseudo", "Leila")
    page.fill("#compte-passe", "un-autre-mot-de-passe")
    page.click("#bouton-compte-inscription")
    page.wait_for_function("window.BANDINI.Compte.etat().etat === 'ouvert'", timeout=10000)
    assert page.text_content("#bouton-compte") == "Compte : Leila"
    assert erreurs == ["Failed to load resource: the server responded with a status of 403 (FORBIDDEN)"], \
        "seul le 403 attendu du mauvais mot de passe s'est produit"


def test_la_page_ce_qu_on_garde_dit_la_verite_et_ne_promet_rien_qu_on_ne_tienne_pas(page, serveur, erreurs):
    """« Une page dit ce qui est gardé et comment tout effacer » : elle se déplie, et elle
    ne promet pas ce qu'aucun code ne tient — un mot de passe perdu ne se retrouve pas."""
    page.goto(serveur)
    attendre_titre(page)
    page.click("#bouton-compte")
    assert not page.is_visible("#compte-garde li"), "fermée par défaut : ce n'est pas ce qu'on est venu chercher"
    page.click("#compte-garde summary")
    assert page.is_visible("#compte-garde li")
    texte = page.text_content("#compte-garde")
    for verite in ("empreinte", "jamais le mot de passe", "sept jours", "Mot de passe perdu, compte perdu"):
        assert verite in texte, verite
    assert erreurs == []


# --- L'ecran du compte sur un petit ecran (M14) --------------------------------------------

DANS_L_ECRAN = """(id) => {
    const e = document.querySelector('.ecran').getBoundingClientRect(), b = document.getElementById(id);
    if (!b || b.offsetParent === null) return false;
    const r = b.getBoundingClientRect();
    return r.top >= e.top - 1 && r.bottom <= e.bottom + 1;
}"""


# ⚠️ Depuis le 22 sept. 2026, le compte SORT de la boîte du jeu (`position: fixed`) : son « écran »
# à lui, c'est le voile, qui couvre la fenêtre.
DANS_LE_COMPTE = DANS_L_ECRAN.replace("document.querySelector('.ecran')", "document.getElementById('voile-compte')")


def atteignable_au_doigt(page, ident, pas=60, maxi=60):
    """Vrai si `ident` finit DANS l'écran en faisant défiler le voile comme un doigt le fait.

    ⚠️ La MOLETTE, jamais `scrollIntoView` ni le `click` de Playwright (qui défilent
    programmatiquement, même un conteneur `overflow: hidden`) : un joueur ne peut pas
    faire ça, et un juge qui le fait laisserait passer un bouton inatteignable."""
    page.evaluate("document.getElementById('voile-compte').scrollTop = 0")
    boite = page.evaluate("""() => { const r = document.getElementById('voile-compte').getBoundingClientRect();
        return { x: r.left + r.width / 2, y: r.top + r.height / 2 }; }""")
    page.mouse.move(boite["x"], boite["y"])
    for _ in range(maxi):
        if page.evaluate(DANS_LE_COMPTE, ident):
            return True
        page.mouse.wheel(0, pas)
        page.wait_for_timeout(20)
    return page.evaluate(DANS_LE_COMPTE, ident)


@pytest.mark.parametrize("nom,taille", [("portrait", (390, 844)), ("paysage", (844, 390))])
def test_tout_l_ecran_du_compte_s_atteint_en_le_faisant_defiler_sur_un_telephone(page, serveur, erreurs, nom, taille):
    """⚠️ Mesuré le 20 sept. 2026 : `.voile` centre son contenu dans un `.ecran` en
    `overflow: hidden`, donc le compte était ROGNÉ — en portrait (écran de jeu de 390×219)
    « Retour » était hors écran et le pseudo coupé en haut ; en paysage, la confirmation
    d'effacement aurait débordé. Le pire état : compte ouvert, confirmation d'effacement ouverte."""
    page.set_viewport_size({"width": taille[0], "height": taille[1]})
    page.goto(serveur)
    attendre_titre(page)
    page.evaluate("""async (pseudo) => { await fetch('/api/compte/inscription', { method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ pseudo: pseudo, mot_de_passe: 'un-mot-de-passe' }) }); }""", "Ecran-" + nom)
    page.reload()
    attendre_titre(page)
    page.wait_for_function("window.BANDINI.Compte.etat().etat === 'ouvert'", timeout=15000)
    page.click("#bouton-compte")
    page.evaluate("document.getElementById('bouton-compte-effacer').click()")
    voile = page.evaluate("(() => { const r = document.getElementById('voile-compte').getBoundingClientRect(); return [r.width, r.height]; })()")
    assert voile[0] >= taille[0] - 1 and voile[1] >= taille[1] - 1, \
        f"le compte doit prendre toute la fenêtre, pas la boîte du jeu (390×219 en portrait) : {voile}"
    for ident in ("compte-mot", "compte-effacer-passe", "bouton-compte-effacer-annuler",
                  "bouton-compte-effacer-confirmer", "bouton-compte-deconnexion", "bouton-fermer-compte"):
        assert atteignable_au_doigt(page, ident), f"{ident} est inatteignable en {nom} ({taille[0]}×{taille[1]})"
    assert erreurs == []


# --- Le defi du jour (M14, 5e vague) -------------------------------------------------------


def test_le_titre_annonce_le_defi_que_le_vrai_serveur_designe(page, serveur, erreurs):
    """Le vrai serveur, la vraie route : la ligne du titre nomme le defi que `/api/defi` a rendu,
    avec la prime du catalogue — et aucun cookie ne part (route publique)."""
    demandes = []
    page.on("request", lambda r: demandes.append(r) if r.url.endswith("/api/defi") else None)
    page.goto(serveur)
    attendre_titre(page)
    page.wait_for_function("window.BANDINI.Defi.duJour() !== null", timeout=8000)
    reponse = page.evaluate("fetch('/api/defi').then(r => r.json())")
    fiche = page.evaluate("window.BANDINI.B.defs.defis.find(d => d.slug === '%s')" % reponse["defi"])
    assert page.is_visible("#defi-du-jour")
    assert page.text_content("#defi-du-jour") == f"Défi du jour : {fiche['titre']} — {fiche['prime']} $"
    assert len(demandes) >= 1 and all("cookie" not in r.headers for r in demandes)
    assert erreurs == []


def test_le_defi_du_jour_ne_barre_jamais_le_chemin_de_jouer(page, serveur, erreurs):
    """⚠️ Un bonus, jamais une condition : la route tombe (500), le titre ne dit rien, JOUER joue."""
    page.route("**/api/defi", lambda route: route.fulfill(status=500, body="{}", content_type="application/json"))
    page.goto(serveur)
    attendre_titre(page)
    page.wait_for_timeout(300)
    assert not page.is_visible("#defi-du-jour")
    assert page.evaluate("window.BANDINI.Defi.duJour()") is None
    jouer(page)
    assert page.get_attribute("#bandini", "data-etat") == "jeu"


def test_une_page_rouverte_le_lendemain_annonce_le_defi_du_nouveau_jour(page, serveur, erreurs):
    """Un telephone qui a dormi sur la table : la page revient (`visibilitychange`), dix minutes
    ont passe, et le titre ne doit pas annoncer le defi d'hier."""
    reponses = iter([{"date": "2026-09-20", "defi": "saut"}, {"date": "2026-09-21", "defi": "tour"}])

    def repondre(route):
        route.fulfill(status=200, body=json.dumps(next(reponses)), content_type="application/json")

    page.add_init_script("""(() => { const reel = Date.now.bind(Date); window.__decalage = 0;
        Date.now = () => reel() + window.__decalage; })()""")
    page.route("**/api/defi", repondre)
    page.goto(serveur)
    attendre_titre(page)
    page.wait_for_function("window.BANDINI.Defi.duJour() !== null", timeout=8000)
    assert "Grand Saut" in page.text_content("#defi-du-jour")
    page.evaluate("window.__decalage = window.BANDINI.Defi.REPOS_MS + 1000")
    page.evaluate("document.dispatchEvent(new Event('visibilitychange'))")
    page.wait_for_function("window.BANDINI.Defi.duJour() && window.BANDINI.Defi.duJour().slug === 'tour'", timeout=8000)
    assert "Tour du Faubourg" in page.text_content("#defi-du-jour")
    assert erreurs == []


@pytest.mark.parametrize("nom,taille", [("portrait", (390, 844)), ("paysage", (844, 390))])
def test_la_ligne_du_defi_ne_pousse_ni_jouer_ni_compte_hors_de_l_ecran(page, serveur, erreurs, nom, taille):
    """⚠️ L'écran titre est aussi un `.voile` en `overflow: hidden` (le piège de l'écran du compte) :
    une ligne de plus ne doit pas rogner JOUER — mesuré en portrait, où l'écran de jeu fait 390×219."""
    page.set_viewport_size({"width": taille[0], "height": taille[1]})
    page.goto(serveur)
    attendre_titre(page)
    page.wait_for_function("window.BANDINI.Defi.duJour() !== null", timeout=8000)
    for ident in ("bouton-jouer", "bouton-compte", "defi-du-jour"):
        assert page.evaluate(DANS_L_ECRAN, ident), f"{ident} sort de l'écran titre en {nom}"
    assert erreurs == []
