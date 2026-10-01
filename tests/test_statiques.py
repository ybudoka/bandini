"""Les scripts maigres (vague 4 de « Charger les districts autour du joueur », 1er oct. 2026) : sans commentaires
ni indentation, ligne pour ligne — `app/statiques.py`.

Ce que ces juges tiennent : le maigrisseur ne change pas le sens (chaque cas piège rend la même chose sous Node,
maigre ou pas), chaque script de la page maigrit sans erreur, se compile et garde ses lignes, le serveur sert les
scripts maigres, le déploiement les écrit (et leur `.gz` au niveau 9), et le poids sur le fil a vraiment fondu.
Le banc d'essai joue les scripts maigres : `test_statiques_js.py`.
"""

from __future__ import annotations

import gzip
import json
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

from app import statiques
from harnais_js import lancer_node

RACINE = Path(__file__).resolve().parent.parent
GABARIT = RACINE / "templates" / "index.html"

#: Chaque piège d'un maigrisseur de JavaScript, et ce que le code doit rendre — maigre ou pas.
CAS = {
    "chaines": "const a = 'x // pas un commentaire', b = \"/* non plus */\", c = 'l\\'apostrophe // ici';\n"
               "rapporter([a, b, c]);",
    "regex_et_obliques": "const r = /[/]+\\/\\//g;\nrapporter('a//b/c///d'.replace(r, '-'));",
    "regex_apres_return": "function f(s) {\n  return /\\/\\*x/.test(s);   // une regex, pas un commentaire\n}\n"
                          "rapporter([f('/*x'), f('x')]);",
    "regex_apres_l_en_tete_d_un_if": "const s = 'a/b';\nif (s) /\\//.test(s) && rapporter('vu'); // fin\n"
                                     "while (false) /a/.test(s);\nrapporter((4) / 2);",
    "division": "const l = 10, d = 2, e = 5;\nconst g = { v: 8 };\nrapporter([l / d / e, g.v / 4, (l) / d, [6][0] / 3]);",
    "gabarit_sur_plusieurs_lignes": "const n = 3;\nconst t = `ligne\n    indentée // gardée\n   /* gardé */\n"
                                    "  ${n /* trois */ + 1}\n`;\nrapporter(t);",
    "gabarits_imbriques": "const x = 1;\nrapporter(`a${`b${x}c${'}'}`}d${ { k: 2 }.k }e${`}`}`);",
    "points_virgules_automatiques": "let a = 1\n/* un bloc\n   sur deux lignes */\nlet b = a\n// rien\n"
                                    ";[a, b].forEach(function (v) { a += v })\nrapporter(a)",
    "return_seul_sur_sa_ligne": "function f() {\n  return /* rien */\n    42;\n}\nrapporter(f() === undefined);",
    "commentaires_partout": "/** La doc.\n * ⚠️ Des accents : é, à. */\nconst o = { /* a */ a: 1, // b\n  b: 2 };\n"
                            "rapporter(o);",
    "continuation_de_chaine": "const s = 'un \\\n   deux';\nrapporter(s);",
    "commentaire_colle": "const a = 4, b = 2;\nrapporter(a/**/-/**/b);",
    "accolades_d_objets_et_de_blocs": "function f(o) { if (o) { return { a: [1, 2].map(function (v) { return v / 2; }) }; } }\n"
                                      "rapporter(f(true));",
}


def _jouer(code: str) -> str:
    return lancer_node("function rapporter(v) { console.log(JSON.stringify(v)); }\n" + code).strip()


@pytest.mark.parametrize("nom", sorted(CAS))
def test_un_piege_maigrit_sans_changer_ce_que_le_code_fait(nom):
    source = CAS[nom]
    maigre = statiques.maigrir(source)
    assert maigre.count("\n") == source.count("\n")
    assert _jouer(maigre) == _jouer(source), maigre
    assert len(maigre) <= len(source)
    assert statiques.maigrir(maigre) == maigre


def test_les_commentaires_et_l_indentation_partent_le_reste_reste():
    source = "/* Un bloc. */\nconst A = (function () {\n  'use strict';\n    // ⚠️ une note\n  return 1;   // fin\n})();\n"
    assert statiques.maigrir(source) == "\nconst A = (function () {\n'use strict';\n\nreturn 1;\n})();\n"


def test_un_script_illisible_est_refuse_plutot_que_change():
    with pytest.raises(statiques.ScriptIllisible):
        statiques.maigrir("const t = `jamais fermé;\n")
    with pytest.raises(statiques.ScriptIllisible):
        statiques.maigrir("return /jamais fermée\n")


def test_chaque_script_de_la_page_maigrit_se_compile_et_garde_ses_lignes(tmp_path):
    """Les 87 scripts du jeu : aucun n'est refusé, chacun garde ses lignes (une erreur nomme la bonne ligne du
    source), maigrir deux fois ne change plus rien, et Node les compile tous."""
    noms = statiques.scripts_de_la_page(GABARIT.read_text(encoding="utf-8"))
    assert len(noms) > 80 and noms[0] == "js/chargement.js"
    chemins = []
    for nom in noms:
        source = (RACINE / "static" / nom).read_text(encoding="utf-8")
        maigre = statiques.maigrir(source)
        assert maigre.count("\n") == source.count("\n"), nom
        assert statiques.maigrir(maigre) == maigre, nom
        chemin = tmp_path / Path(nom).name
        chemin.write_text(maigre, encoding="utf-8")
        chemins.append(str(chemin))
    sortie = lancer_node("""
      const fs = require('fs'), vm = require('vm');
      const ko = [];
      for (const f of ENTREE) {
        try { new vm.Script(fs.readFileSync(f, 'utf8'), { filename: f }); } catch (e) { ko.push(f + ' : ' + e.message); }
      }
      console.log(JSON.stringify(ko));
    """, entree=chemins)
    assert json.loads(sortie) == []


def test_les_scripts_maigres_pesent_moins_de_la_moitie_sur_le_fil():
    """La raison d'être de la vague 4 : 1,30 Mo de scripts au niveau 9 (1,54 au niveau 1 de nginx) avant
    l'écran titre. Maigres, moins de la moitié — sinon c'est que les commentaires restent."""
    avant = apres = 0
    for nom in statiques.scripts_de_la_page(GABARIT.read_text(encoding="utf-8")):
        octets = (RACINE / "static" / nom).read_bytes()
        avant += len(gzip.compress(octets, 9))
        apres += len(gzip.compress(statiques.maigrir(octets.decode("utf-8")).encode("utf-8"), 9))
    assert apres < 0.55 * avant, (avant, apres)


def test_le_serveur_sert_les_scripts_maigres(client):
    """Le serveur de dev et les juges Chromium reçoivent les octets que le téléphone recevra."""
    for nom in ("jeu.js", "chargement.js", "monde.js"):
        reponse = client.get(f"/static/js/{nom}?v=x")
        assert reponse.status_code == 200
        source = (RACINE / "static" / "js" / nom).read_text(encoding="utf-8")
        assert reponse.get_data(as_text=True) == statiques.maigrir(source), nom
        assert reponse.mimetype in ("text/javascript", "application/javascript")
        etag = reponse.headers["ETag"]
        assert client.get(f"/static/js/{nom}", headers={"If-None-Match": etag}).status_code == 304
    # Le reste de `static/` passe tel quel : la feuille, les images, et le travailleur (servi à la racine).
    feuille = client.get("/static/css/styles.css")
    assert feuille.get_data() == (RACINE / "static" / "css" / "styles.css").read_bytes()
    assert client.get("/static/js/nulle-part.js").status_code == 404


def test_le_deploiement_ecrit_les_scripts_maigres_et_leur_gz(tmp_path):
    """`deploy.sh` maigrit la release (`python app/statiques.py`) : nginx sert `/static/` lui-même. Chaque script
    de la page y devient maigre, avec son `.gz` au niveau 9 à côté (pour `gzip_static on`) ; refaire ne change
    plus rien ; ce qui n'est pas un script de la page ne bouge pas."""
    (tmp_path / "templates").mkdir()
    shutil.copy(GABARIT, tmp_path / "templates" / "index.html")
    shutil.copytree(RACINE / "static" / "js", tmp_path / "static" / "js")
    travailleur = (tmp_path / "static" / "js" / "travailleur.js").read_bytes()
    bilan = statiques.ecrire_la_release(tmp_path)
    assert bilan["scripts"] > 80 and bilan["gz"] < 0.55 * bilan["avant_gz"], bilan
    for nom in statiques.scripts_de_la_page(GABARIT.read_text(encoding="utf-8")):
        source = (RACINE / "static" / nom).read_text(encoding="utf-8")
        ecrit = (tmp_path / "static" / nom).read_text(encoding="utf-8")
        assert ecrit == statiques.maigrir(source), nom
        assert gzip.decompress((tmp_path / "static" / (nom + ".gz")).read_bytes()).decode("utf-8") == ecrit
    assert (tmp_path / "static" / "js" / "travailleur.js").read_bytes() == travailleur
    instantane = {f: f.read_bytes() for f in (tmp_path / "static" / "js").iterdir()}
    # Une seconde fois, comme `deploy.sh` le lance : le fichier en script, sans importer le paquet `app`.
    refait = subprocess.run([sys.executable, str(RACINE / "app" / "statiques.py"), str(tmp_path)],
                            capture_output=True, text=True, check=True)
    assert "scripts maigres" in refait.stdout and not refait.stderr, refait.stderr
    assert {f: f.read_bytes() for f in (tmp_path / "static" / "js").iterdir()} == instantane
    deploiement = (RACINE / "deploy" / "deploy.sh").read_text(encoding="utf-8")
    etape = '"$CIBLE/.venv/bin/python" "$CIBLE/app/statiques.py" "$CIBLE"'
    assert etape in deploiement
    assert deploiement.index(etape) < deploiement.index("==> Bascule"), "maigrir AVANT la bascule"
