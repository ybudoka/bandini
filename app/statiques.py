"""Les fichiers statiques à l'empreinte de LEUR contenu : `?v=<empreinte>`, plus la version du site.

La vague 3 de « Charger les districts autour du joueur » (docs/jalons/charger-les-districts-autour-du-joueur.md,
1er oct. 2026). Mesuré sous Chromium, réseau « 3G rapide » et processeur ×4 : **les scripts du jeu font 93 % de
ce qui voyage avant l'écran titre** (1,56 Mo sur le fil, 10 s sur 12,6) — la carte et les définitions, 108 Ko.
Et ils portaient tous `?v=<version>` : la version monte à chaque commit `feat:`/`fix:`, donc chaque mise en ligne
changeait l'adresse des 87 scripts, et le téléphone les retéléchargeait TOUS, même ceux qui n'avaient pas changé
d'un octet (nginx les garde pourtant sept jours, `expires 7d`).

Ici, chaque adresse porte l'empreinte de son PROPRE fichier : une mise en ligne qui touche trois scripts n'en
fait repartir que trois, et le cache du navigateur rend les 84 autres sans même demander.

⚠️ L'empreinte se relit quand le fichier change sous le serveur (date et taille) : le serveur de dev ne
redémarre pas pour un script (`run.py`), et une adresse figée servirait l'ancien fichier du cache.
⚠️ Le gabarit garde le texte `filename='js/…'` : le banc d'essai (`tests/banc.js`), le compte de la barre
(`routes._scripts_du_jeu`) et la coquille hors ligne (`hors_ligne.coquille`) lisent la liste là.

**La vague 4 : les scripts maigrissent** (même fiche). Les 87 scripts pèsent 4 Mo bruts, et plus de la moitié,
ce sont leurs commentaires et leur indentation — précieux dans le dépôt, inutiles au téléphone. `maigrir` les
retire, **ligne pour ligne** : 1 535 → 750 Ko sur le fil au niveau 1 de nginx, 628 Ko au niveau 9. Un seul
maigrisseur, servi partout :

- **en ligne**, nginx sert `/static/` lui-même : `deploy.sh` maigrit la release avant la bascule
  (`python app/statiques.py <release>`), et écrit à côté de chaque script son `.gz` au niveau 9 (pour `gzip_static on`) ;
- **le serveur de dev et les juges Chromium** reçoivent les mêmes octets (`Maigres`, branché sur la vue
  `static` par `create_app`) ;
- **le banc d'essai** joue les scripts maigres (`conftest.scripts_servis`) : tous les juges JS jugent ce que le
  téléphone exécute.
"""

from __future__ import annotations

import gzip
import hashlib
import re
import sys
from pathlib import Path
from threading import Lock

from flask import Response, request

#: Assez pour qu'une collision n'arrive jamais entre deux versions d'un même fichier.
LONGUEUR = 12


class Empreintes:
    """`empreintes("js/jeu.js")` → l'empreinte du fichier, relue seulement s'il a changé sur le disque."""

    def __init__(self, dossier: Path):
        self.dossier = Path(dossier)
        self._connues: dict[str, tuple[tuple[int, int], str]] = {}
        self._verrou = Lock()

    def __call__(self, nom: str) -> str:
        chemin = self.dossier / nom
        etat = chemin.stat()
        cle = (etat.st_mtime_ns, etat.st_size)
        connue = self._connues.get(nom)
        if connue and connue[0] == cle:
            return connue[1]
        empreinte = hashlib.sha256(chemin.read_bytes()).hexdigest()[:LONGUEUR]
        with self._verrou:
            self._connues[nom] = (cle, empreinte)
        return empreinte


# --- La vague 4 : les scripts maigrissent ------------------------------------------------------------------------

#: Après ces mots, une barre oblique OUVRE une expression régulière (`return /x/.test(s)`) ; après tout autre
#: nom, elle divise (`largeur / 2`).
MOTS_AVANT_UNE_EXPRESSION = frozenset({"return", "typeof", "case", "do", "else", "in", "of", "new", "delete",
                                       "void", "throw", "instanceof", "yield", "await"})

_JETON = re.compile(r"""
    (?P<espace>[ \t\r\f\v ﻿]+)
  | (?P<nl>\n)
  | (?P<ligne>//[^\n]*)
  | (?P<bloc>/\*.*?\*/)
  | (?P<chaine>'(?:[^'\\\n]|\\(?:\r\n|[\s\S]))*'|"(?:[^"\\\n]|\\(?:\r\n|[\s\S]))*")
  | (?P<gabarit>`)
  | (?P<nom>[A-Za-z_$\u0080-￿][\w$\u0080-￿]*)
  | (?P<nombre>\.?\d[\w.]*)
  | (?P<oblique>/)
  | (?P<ouvre>\{)
  | (?P<ferme>\})
  | (?P<autre>[\s\S])
""", re.VERBOSE | re.DOTALL)
#: Les mots dont la parenthèse fermante est suivie d'une INSTRUCTION, pas d'une valeur.
_EN_TETES = frozenset({"if", "while", "for", "with"})
#: Une expression régulière entière : ses classes `[...]` peuvent porter une barre oblique (`/[/]/`).
_REGEX = re.compile(r"/(?:[^/\\\[\n]|\\.|\[(?:[^\]\\\n]|\\.)*\])+/[a-z]*")
#: Le texte d'un gabarit jusqu'à sa fin (`` ` ``) ou sa prochaine substitution (`${`).
_TEXTE_DE_GABARIT = re.compile(r"(?:[^`\\$]|\\[\s\S]|\$(?!\{))*")


class ScriptIllisible(ValueError):
    """Le maigrisseur ne sait pas lire ce script : il refuse plutôt que de servir un code changé."""


def maigrir(source: str) -> str:
    """Le script sans ses commentaires ni son indentation, **ligne pour ligne**.

    ⚠️ Le même nombre de lignes, chaque instruction sur SA ligne : une erreur dans la console nomme toujours la
    bonne ligne du fichier source, et l'insertion automatique des points-virgules voit les mêmes fins de ligne.
    ⚠️ Rien d'autre ne change : ni les noms, ni les chaînes, ni le texte d'un gabarit (`` ` ``, gardé tel quel,
    indentation comprise — elle y est du texte). Les espaces au milieu d'une ligne se réduisent à un.
    ⚠️ La seule ambiguïté du JavaScript qu'il faut trancher : une barre oblique divise-t-elle ou ouvre-t-elle une
    expression régulière ? Comme tous les outils de ce genre, par le jeton d'avant (`MOTS_AVANT_UNE_EXPRESSION`).
    Le juge : chaque script maigre se compile, garde ses lignes, et le banc d'essai joue sur eux.
    """
    sortie: list[str] = []
    i, n = 0, len(source)
    exterieurs: list[int] = []   # la profondeur d'accolades autour de chaque `${` ouvert
    conditions: list[bool] = []  # chaque `(` ouverte : est-ce l'en-tête d'un `if`, `while`, `for`, `with` ?
    profondeur = 0
    dernier: tuple[str, str] | None = None
    debut_de_ligne = True

    def regex_ici() -> bool:
        if dernier is None:
            return True
        genre, texte = dernier
        if genre == "nom":
            return texte in MOTS_AVANT_UNE_EXPRESSION
        if genre in ("nombre", "chaine", "gabarit", "regex"):
            return False
        return not (genre == "autre" and texte in (")", "]"))

    def texte_de_gabarit(j: int) -> tuple[int, bool]:
        """Après un `` ` `` ou la `}` d'une substitution : la fin du texte, et si le gabarit s'y ferme."""
        k = _TEXTE_DE_GABARIT.match(source, j).end()
        if k >= n:
            raise ScriptIllisible("un gabarit ne se ferme jamais")
        return (k + 1, True) if source[k] == "`" else (k + 2, False)

    def espace():
        if not debut_de_ligne and sortie and sortie[-1] != " ":
            sortie.append(" ")

    while i < n:
        m = _JETON.match(source, i)
        genre, texte = m.lastgroup, m.group()
        if genre == "espace":
            espace()
            i = m.end()
            continue
        if genre == "nl":
            while sortie and sortie[-1] == " ":
                sortie.pop()
            sortie.append("\n")
            debut_de_ligne = True
            i = m.end()
            continue
        if genre == "ligne":
            i = m.end()
            continue
        if genre == "bloc":
            lignes = texte.count("\n")
            if lignes:
                while sortie and sortie[-1] == " ":
                    sortie.pop()
                sortie.append("\n" * lignes)
                debut_de_ligne = True
            else:
                espace()
            i = m.end()
            continue
        if genre == "oblique" and regex_ici():
            r = _REGEX.match(source, i)
            if not r:
                raise ScriptIllisible(f"une expression régulière illisible, ligne {source.count(chr(10), 0, i) + 1}")
            genre, texte = "regex", r.group()
            i = r.end()
        elif genre == "gabarit" or (genre == "ferme" and profondeur == 0 and exterieurs):
            fin, ferme = texte_de_gabarit(i + 1)
            texte = source[i:fin]
            i = fin
            if genre == "gabarit" and not ferme:
                exterieurs.append(profondeur)
            elif genre == "ferme" and ferme:
                profondeur = exterieurs.pop()
            if not ferme:
                # Dans une substitution : du code, à la profondeur zéro, comme après une accolade ouvrante.
                profondeur = 0
                sortie.append(texte)
                dernier, debut_de_ligne = ("autre", "{"), False
                continue
            genre = "gabarit"
        else:
            if genre == "ouvre":
                profondeur += 1
            elif genre == "ferme":
                profondeur -= 1
            elif texte == "(":
                conditions.append(dernier is not None and dernier[0] == "nom" and dernier[1] in _EN_TETES)
            elif texte == ")" and conditions and conditions.pop():
                # `if (x) /re/.test(s)` : après l'en-tête d'un `if`, une barre oblique ouvre une expression.
                genre = "condition"
            i = m.end()
        sortie.append(texte)
        dernier, debut_de_ligne = (genre, texte), False
    if exterieurs:
        raise ScriptIllisible("un gabarit ne se ferme jamais")
    maigre = "".join(sortie)
    if maigre.count("\n") != source.count("\n"):
        raise ScriptIllisible("le script maigre n'a plus le même nombre de lignes")
    return maigre


#: Les scripts de la page, dans l'ordre : `filename='js/…'` dans le gabarit, la seule liste.
_SCRIPT_DE_LA_PAGE = re.compile(r"filename='(js/[^']+)'")


def scripts_de_la_page(gabarit: str) -> list[str]:
    """`["js/chargement.js", …, "js/jeu.js"]`, lus dans le texte de `templates/index.html`."""
    return _SCRIPT_DE_LA_PAGE.findall(gabarit)


class Maigres:
    """Les scripts de la page, servis maigres par le serveur de dev (et aux juges Chromium).

    ⚠️ Relus quand le fichier change sous le serveur, comme les empreintes : le serveur de dev ne redémarre pas
    pour un script. Un script que le maigrisseur refuse est servi TEL QUEL — le jeu ne tombe pas pour un
    commentaire ; c'est `test_statiques.py` qui rougit."""

    def __init__(self, dossier: Path, gabarit: Path):
        self.dossier = Path(dossier)
        self.noms = frozenset(scripts_de_la_page(Path(gabarit).read_text(encoding="utf-8")))
        self._connus: dict[str, tuple[tuple[int, int], bytes, str]] = {}
        self._verrou = Lock()

    def lire(self, nom: str) -> tuple[bytes, str]:
        chemin = self.dossier / nom
        etat = chemin.stat()
        cle = (etat.st_mtime_ns, etat.st_size)
        connu = self._connus.get(nom)
        if connu and connu[0] == cle:
            return connu[1], connu[2]
        source = chemin.read_text(encoding="utf-8")
        try:
            corps = maigrir(source).encode("utf-8")
        except ScriptIllisible:
            corps = source.encode("utf-8")
        empreinte = hashlib.sha256(corps).hexdigest()[:LONGUEUR]
        with self._verrou:
            self._connus[nom] = (cle, corps, empreinte)
        return corps, empreinte

    def reponse(self, nom: str) -> Response:
        corps, empreinte = self.lire(nom)
        if request.if_none_match.contains_weak(empreinte):
            reponse = Response(status=304)
        else:
            reponse = Response(corps, mimetype="text/javascript")
        reponse.headers["ETag"] = f'"{empreinte}"'
        reponse.headers["Cache-Control"] = "no-cache"
        return reponse


def ecrire_la_release(racine: Path) -> dict:
    """Maigrit EN PLACE les scripts de la page d'une release (`deploy.sh`, avant la bascule) et écrit le `.gz` de
    chacun au niveau 9 (`mtime=0` : les mêmes octets à chaque déploiement).

    ⚠️ Refaire ne change rien (un script maigre est déjà maigre) ; ce qui n'est pas un script de la page —
    le travailleur, servi à la racine — n'est pas touché. Un script refusé fait échouer le déploiement AVANT la
    bascule : le site en ligne reste celui d'avant."""
    racine = Path(racine)
    bilan = {"scripts": 0, "avant": 0, "apres": 0, "avant_gz": 0, "gz": 0}
    for nom in scripts_de_la_page((racine / "templates" / "index.html").read_text(encoding="utf-8")):
        chemin = racine / "static" / nom
        source = chemin.read_text(encoding="utf-8")
        maigre = maigrir(source)
        octets = maigre.encode("utf-8")
        if maigre != source:
            chemin.write_bytes(octets)
        compresse = gzip.compress(octets, compresslevel=9, mtime=0)
        chemin.with_name(chemin.name + ".gz").write_bytes(compresse)
        bilan["scripts"] += 1
        bilan["avant"] += len(source.encode("utf-8"))
        bilan["apres"] += len(octets)
        bilan["avant_gz"] += len(gzip.compress(source.encode("utf-8"), compresslevel=9, mtime=0))
        bilan["gz"] += len(compresse)
    return bilan


if __name__ == "__main__":
    b = ecrire_la_release(Path(sys.argv[1]) if len(sys.argv) > 1 else Path.cwd())
    print(f"{b['scripts']} scripts maigres : {b['avant']} → {b['apres']} octets bruts, "
          f"{b['avant_gz']} → {b['gz']} au niveau 9")
