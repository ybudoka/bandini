"""Les icones, le favicon et le logo — dessines par `scripts/icones.py`, servis par le jeu.

Trois choses se jugent ici : que les fichiers de `static/img/` sont bien ceux
que le script dessine (un PNG retouche a la main serait ecrase au prochain
passage), que le Bandini de l'icone est encore celui du jeu, et que la page
les annonce tous — un manifeste qui nomme une icone absente, Chrome l'avale
sans rien dire et l'ecran d'accueil garde une capture floue.
"""

import importlib.util
import json
import re
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
SCRIPT = RACINE / "scripts" / "icones.py"


def _charger():
    spec = importlib.util.spec_from_file_location("icones", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


icones = _charger()


def test_static_img_est_ce_que_le_script_dessine(tmp_path):
    assert icones.main(["--verifier"]) == 0, "uv run python scripts/icones.py"
    # Et le juge mord : un pixel de travers dans une copie, et il le dit.
    for nom, octets in icones.fichiers().items():
        (tmp_path / nom).write_bytes(octets)
    g = icones.icone()
    g[0][0] = "#ffffff"
    (tmp_path / "icone-192.png").write_bytes(icones.en_png(g, 192))
    assert icones.main(["--verifier", "--dossier", str(tmp_path)]) == 1


def test_bandini_sur_l_icone_est_le_sprite_du_jeu():
    sprites = (RACINE / "static" / "js" / "sprites.js").read_text(encoding="utf-8")
    joueur = sprites[sprites.index("joueur: {") : sprites.index("SPRITES.enfant")]
    pal = ", ".join(f"{k}: '{v}'" for k, v in icones.JOUEUR_PAL.items())
    assert f"pal: {{ {pal} }}" in joueur, "la palette du joueur a change dans sprites.js"
    bas = joueur[joueur.index("bas: [") :]
    premiere_image = re.search(r"\[\s*(\[[^\]]*\])", bas).group(1)
    assert re.findall(r"'([^']*)'", premiere_image) == icones.JOUEUR, (
        "le joueur a ete redessine dans sprites.js : recopier JOUEUR, puis relancer le script"
    )


def test_bandini_tient_dans_le_masque_d_android():
    """Android decoupe l'icone « maskable » en cercle : 80 % du cote, au centre."""
    x0, y0 = icones.BANDINI_ICONE
    rayon = 0.4 * 24
    for y, rangee in enumerate(icones.JOUEUR):
        for x, ch in enumerate(rangee):
            if ch == ".":
                continue
            for cx, cy in [(x0 + x, y0 + y), (x0 + x + 1, y0 + y), (x0 + x, y0 + y + 1),
                           (x0 + x + 1, y0 + y + 1)]:
                assert (cx - 12) ** 2 + (cy - 12) ** 2 <= rayon**2, (x, y)


def test_la_page_annonce_ses_icones(client):
    html = client.get("/").get_data(as_text=True)
    liens = dict(re.findall(r'<link rel="(icon|apple-touch-icon|manifest)"[^>]*href="([^"?]+)', html))
    assert set(liens) == {"icon", "apple-touch-icon", "manifest"}
    tactile = client.get(liens["apple-touch-icon"])
    assert tactile.status_code == 200
    assert icones.lire_png(tactile.data)[:2] == (180, 180)
    assert client.get("/static/img/favicon.svg").status_code == 200
    assert client.get("/favicon.ico").data[:4] == b"\0\0\1\0"


def test_le_manifeste(client):
    reponse = client.get("/manifest.webmanifest")
    assert reponse.status_code == 200
    assert reponse.mimetype == "application/manifest+json"
    manifeste = json.loads(reponse.data)
    assert manifeste["name"] == "Bandini"
    assert manifeste["start_url"] == "/"
    assert manifeste["background_color"] == manifeste["theme_color"] == "#0b0a12"
    tailles = {}
    for icone in manifeste["icons"]:
        image = client.get(icone["src"])
        assert image.status_code == 200, icone["src"]
        w, h, _ = icones.lire_png(image.data)
        assert icone["sizes"] == f"{w}x{h}"
        tailles.setdefault(icone["purpose"], set()).add(w)
    assert tailles == {"any": {192, 512}, "maskable": {512}}


def test_le_titre_de_l_accueil_est_le_logo(client):
    html = client.get("/").get_data(as_text=True)
    titre = re.search(r'<h1 class="titre[^"]*">(.*?)</h1>', html, re.S).group(1)
    img = re.search(r'<img class="logo" src="([^"?]+)[^"]*" alt="Bandini"', titre)
    assert img, "le h1 de l'accueil doit porter le logo, avec son nom en alt"
    assert client.get(img.group(1)).status_code == 200
