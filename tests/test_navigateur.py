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
