"""Le jeu dans un vrai navigateur (Playwright) : chargement, clavier, tactile, cibles.

Se saute sans Chromium en local ; en CI, BANDINI_TESTS_OBLIGATOIRES=1 en fait
un echec — un garde-fou qui se desactive tout seul n'en est pas un.
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


@pytest.mark.parametrize("ecran", list(ECRANS))
def test_la_page_charge_sans_erreur(page, serveur, erreurs, ecran):
    page.set_viewport_size({"width": ECRANS[ecran][0], "height": ECRANS[ecran][1]})
    page.goto(serveur)
    attendre_titre(page)
    assert erreurs == []
    deborde = page.evaluate("document.documentElement.scrollWidth - window.innerWidth")
    assert deborde <= 0, f"la page deborde de {deborde} px"


def test_jouer_puis_marcher_au_clavier(page, serveur, erreurs):
    page.goto(serveur)
    attendre_titre(page)
    page.click("#bouton-jouer")
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
    page.click("#bouton-jouer")          # le clic reveille l'audio
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
    page.click("#bouton-jouer")
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
    page.click("#bouton-jouer")
    page.wait_for_selector('#bandini[data-etat="jeu"]')
    page.wait_for_function("window.BANDINI.Son.Ambiance.courante === 'ville'", timeout=20000)
    attendues = page.evaluate("window.BANDINI.B.defs.audio.voix.filter(v => v.fichier).length")
    page.wait_for_function(
        "n => window.BANDINI.B.defs.audio.voix.filter(v => v.fichier).every(v => window.BANDINI.Son.echantillon('voix-' + v.slug, {volume: 0.001}) !== null) && n > 0",
        arg=attendues, timeout=20000)
    assert page.evaluate("window.BANDINI.Son.boucleActive('ambiance-ville')") is True
    assert erreurs == []


def test_une_voix_de_l_histoire_se_decode_et_baisse_la_radio(page, serveur, erreurs):
    """Les repliques de l'histoire se chargent PAR MISSION, quand on parle au
    donneur : c'est ici, et seulement ici, qu'on sait que le MP3 de Ti-Guy se
    decode — et que la musique baisse pendant qu'il parle (ducking)."""
    page.goto(serveur)
    attendre_titre(page)
    page.click("#bouton-jouer")
    page.wait_for_selector('#bandini[data-etat="jeu"]')
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
    page.click("#bouton-jouer")
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
