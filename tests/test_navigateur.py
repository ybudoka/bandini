"""Le jeu dans un vrai navigateur (Playwright) : chargement, clavier, tactile, cibles.

Se saute sans Chromium ; dans la suite de livraison (BANDINI_TESTS_OBLIGATOIRES=1,
en local avant de pousser sur `main` — les tests ne tournent plus en CI depuis le
17 sept. 2026), c'est un echec : un garde-fou qui se desactive tout seul n'en est pas un.
"""

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


def attendre_titre(page):
    page.wait_for_selector('#bandini[data-etat="titre"]', timeout=15000)


def jouer(page):
    """JOUER, puis PASSER l'ouverture : les juges d'ici veulent la ville, pas la scene.

    ⚠️ Depuis que le jeu s'ouvre sur une scene (le car de six heures, le
    narrateur), cliquer JOUER ne rend plus les commandes tout de suite : elle
    fige la ville tant qu'on ne l'a pas passee, et un test qui marche au clavier
    juste apres ne bouge pas d'un pixel. Tout ce qui veut jouer DANS la ville
    passe donc par ici — un seul endroit a changer le jour ou l'ouverture change.
    L'ouverture elle-meme a ses juges, plus bas et au banc.
    """
    page.click("#bouton-jouer")
    page.wait_for_selector('#bandini[data-etat="jeu"]')
    page.evaluate("window.BANDINI.Histoire.passerOuverture()")
    page.wait_for_function("!window.BANDINI.B.ouverture")


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

    page.route("**/api/carte", une_autre_carte)
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
    page.evaluate("""() => { const L = window.BANDINI, v = L.B.mission.vehicule, j = L.B.joueur;
                            j.x = v.x + 12; j.y = v.y; L.Entites.indexer(); L.Vehicules.monter(j, v); }""")
    page.wait_for_function("window.BANDINI.B.partie.mission.etape === 2", timeout=20000)
    page.wait_for_function("!window.BANDINI.B.cinema", timeout=60000)      # Ti-Guy au combine
    page.evaluate("""() => { const L = window.BANDINI, g = L.Histoire.lieu('garage'), v = L.B.mission.vehicule, j = L.B.joueur;
                            v.x = g.x; v.y = g.y; v.vitesse = 0; v.vx = 0; v.vy = 0; j.x = v.x; j.y = v.y; }""")
    page.wait_for_function("!!window.BANDINI.B.partie.missionsFaites.m1", timeout=20000)
    page.wait_for_function("!!window.BANDINI.B.scene", timeout=20000)
    page.wait_for_function("!window.BANDINI.B.scene && !window.BANDINI.B.cinema", timeout=90000)
    assert page.evaluate("!window.BANDINI.Histoire.donneur('ti_guy')"), "Ti-Guy n'est pas rentre au garage"
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
    assert page.evaluate("document.body.classList.contains('tactile')")
    for action, minimum in (("attaque", 64), ("action", 64), ("esquive", 64), ("arme", 64), ("pause", 44)):
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
              for a in ("attaque", "action", "esquive", "arme", "pause", "plein")}
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
    premiere = page.evaluate("window.BANDINI.B.defs.audio.histoire.find(v => v.mission === 'm1' && v.fichier)")
    if not premiere:
        pytest.skip("aucune voix de l'histoire generee (scripts/audio_elevenlabs.py --voix)")
    page.evaluate("""() => {
        const L = window.BANDINI, j = L.B.joueur, t = L.Histoire.donneur('ti_guy');
        j.x = t.x - 16; j.y = t.y; L.Entites.indexer();
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
    page.goto(serveur)
    attendre_titre(page)
    jouer(page)
    page.wait_for_selector('#bandini[data-etat="jeu"]')
    ligne = page.evaluate("""() => {
        const L = window.BANDINI;
        L.Jeu.pause();
        const pause = L.B.menu;
        const i = pause.items.findIndex(x => x.libelle === 'OPTIONS');
        pause.items[i].faire(pause.items[i]);
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
    premiere = page.evaluate(
        "window.BANDINI.B.defs.audio.histoire.find(v => v.mission === 'm1' && v.fichier)")
    if premiere:
        page.evaluate("(m) => window.BANDINI.Son.Voix.chargerHistoire(m)", premiere["mission"])
        page.wait_for_function(
            "s => window.BANDINI.Son.estCharge('histoire-' + s)", arg=premiere["slug"], timeout=45000)
        niveaux["une replique"] = page.evaluate("""(s) => {
            const S = window.BANDINI.Son;
            S.Voix.couper(); S.Ambiance.arreter(); S.boucle('ambiance-ville', false);
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
