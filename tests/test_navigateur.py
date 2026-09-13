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
    page.click("#bouton-jouer")
    page.wait_for_selector('#bandini[data-etat="jeu"]')
    page.wait_for_function("window.BANDINI.Son.etatSon() === 'actif'", timeout=10000)
    assert page.evaluate("() => document.getElementById('avis-son').hidden") is True
    assert erreurs == []


def test_les_options_disent_l_etat_du_son(page, serveur, erreurs):
    page.goto(serveur)
    attendre_titre(page)
    page.click("#bouton-jouer")
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


def test_le_jeu_sort_vraiment_du_son(page, serveur, erreurs):
    """⚠️ Un echantillon peut se telecharger, se decoder, demarrer, avoir le bon
    volume et etre relie a la sortie — et ne rien produire si la source n'entre
    dans rien. C'est arrive : aucun des 79 fichiers n'a sonne jusqu'au
    13 sept. 2026. Ce juge ecoute la sortie plutot que l'intention."""
    page.add_init_script(SONDE_AUDIO)
    page.goto(serveur)
    attendre_titre(page)
    page.click("#bouton-jouer")          # un vrai geste : le son est accorde
    page.wait_for_selector('#bandini[data-etat="jeu"]')
    page.wait_for_function("window.BANDINI.Son.charges > 0", timeout=20000)
    page.wait_for_timeout(1500)

    synthese = page.evaluate("""() => {
        const p = window.__mesure(900);
        BANDINI.Son.ton(440, 0.6, 'square', 0.9);
        return p;
    }""")
    assert synthese > PLANCHER, f"la synthese ne sort pas : {synthese:.5f}"

    echantillon = page.evaluate("""() => {
        const p = window.__mesure(900);
        BANDINI.Son.echantillon('coup', { volume: 1 });
        return p;
    }""")
    assert echantillon > PLANCHER, (
        f"un echantillon charge ne produit AUCUN son ({echantillon:.5f}) : "
        "la chaîne source > gain > maitre est coupee quelque part")
    assert erreurs == []


def test_l_ambiance_de_la_ville_s_entend(page, serveur, erreurs):
    """L'ambiance tourne en boucle : si elle est muette, la ville est morte."""
    page.add_init_script(SONDE_AUDIO)
    page.goto(serveur)
    attendre_titre(page)
    page.click("#bouton-jouer")
    page.wait_for_selector('#bandini[data-etat="jeu"]')
    page.wait_for_function("window.BANDINI.Son.Ambiance.courante !== null", timeout=20000)
    page.wait_for_timeout(2000)
    assert page.evaluate("() => BANDINI.Son.boucleActive('ambiance-ville')") is True
    niveau = page.evaluate("() => window.__mesure(2500)")
    assert niveau > PLANCHER, f"l'ambiance tourne mais ne s'entend pas : {niveau:.5f}"
    assert erreurs == []


def test_le_theme_du_menu_s_entend(page, serveur, erreurs):
    page.add_init_script(SONDE_AUDIO)
    page.goto(serveur)
    attendre_titre(page)
    page.click("#bouton-jouer")
    page.wait_for_selector('#bandini[data-etat="jeu"]')
    page.evaluate("() => BANDINI.Jeu.retourTitre()")
    page.wait_for_timeout(2000)
    assert page.evaluate("() => BANDINI.Son.Mus.courante") == "titre"
    niveau = page.evaluate("() => window.__mesure(3000)")
    assert niveau > PLANCHER, f"le theme du menu ne sort pas : {niveau:.5f}"
    assert erreurs == []
