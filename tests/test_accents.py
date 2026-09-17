"""Le jeu écrit avec ses accents — le juge des textes.

Martin (17 sept. 2026) : « le jeu doit supporter les accents ». La police pixel
les dessine depuis la 1re vague (`test_la_police_dessine_l_accent_au_dessus_de_la_lettre`) ;
restaient les textes, écrits sans accents dès le départ : « PARTIE SAUVEGARDEE »,
« HOPITAL A MOITIE PRIX », « LA POLICE A LACHE ». Deux cents chaînes corrigées
à la 2e vague, et ce juge pour qu'elles ne reviennent pas.

⚠️ Il ne juge que des mots qui N'EXISTENT PAS sans leur accent : « HOPITAL »,
« DEJA », « FOURRIERE ». Un « A » qui devrait être « À », un « PASSE » qui
devrait être « PASSÉ » sont justes tels quels dans une autre phrase : aucun juge
ne les tranche sans lire la phrase. Ils se relisent.

⚠️ L'orthographe est la TRADITIONNELLE, comme dans tout le dépôt (« connaît »,
« croûte », « août ») : « AOUT », « COUTE » ou « RECONNAIT », que les
rectifications de 1990 admettent, sont refusés ici aussi.
"""

import json
import re
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent

#: Les mots que le jeu a écrits sans leur accent, et qui ne sont pas du français
#: sans lui. Tirés de la 2e vague (les mots que le correcteur de macOS refuse tels
#: quels), plus les graphies rectifiées que le dépôt n'emploie pas.
SANS_ACCENT = frozenset("""
    ACHETES AGITEE AMENE AOUT APPATS ARRETE BELIVEAU BIBLIOTHEQUE BIERE CABLE CAFE
    CASSEE CHASSEES CHEQUES CINEMA CLOTURE COMMERCANTS CONFISQUEES COUTE CREMERIE CROUTE
    DEBOSSELAGE DEC DEJA DEMOLIR DEPANNEUR DEPANNEUSE DEPOSER DERRIERE ECHAP ECOEURE
    ECOLE ECRAN ECRASEE ECRASER EJECTE ELECTRIQUE ENCHAINE ENTREE ENTREPOT EPAIS EPAVE
    EPAVES EPICERIE ETEINTE ETOILE FEVR FOURRIERE GACHETTES GAREE HOPITAL HOTEL HUITRES
    INQUIETE JOUEES LACHE LACHER LEO LIBERES MEME MOITIE NUMEROS PATISSERIE PECHE
    PEPINIERE PIECES PORTEE PRET PRETS PREVOST PROPRIETAIRE PROPRIETES RACHETE
    REAPPRENDRE RECONNAIT REGLEE REGLER RELACHE REPARATION REPARE REPARER REVEIL ROMEO
    ROTISSERIE SAUVEE SAUVEGARDEE SIRENE SOUPCONS TEMOINS TEMPETES TETE USAGEES
    VEHICULES VELOS VETERINAIRE VIDEO
""".split())

#: Un mot en capitales, borné par autre chose qu'une lettre (accentuée ou non).
CAPITALES = re.compile(r"(?<![A-Za-zÀ-ÖØ-öø-ÿ])[A-Z]{2,}(?![A-Za-zÀ-ÖØ-öø-ÿ])")
#: « Hopital » : une capitale puis des minuscules, dans les noms du paquet.
NOM = re.compile(r"(?<![A-Za-zÀ-ÖØ-öø-ÿ])[A-Z][a-z]+(?![A-Za-zÀ-ÖØ-öø-ÿ])")

#: Ce qui, dans le paquet, n'est pas un texte montré au joueur.
CLES_MUETTES = frozenset({"slug", "voix", "prompt", "fichier", "fichiers", "id", "cle", "type", "glyphe"})


def chaines_js(source):
    """(ligne, contenu) de chaque chaîne d'un source JS, commentaires exclus.

    ⚠️ Les commentaires du dépôt sont écrits en capitales et sans accents
    (« la file de TOUT REAPPRENDRE ») : c'est du code, pas de l'écran. Une
    chaîne entre apostrophes ou guillemets s'arrête à la fin de sa ligne, donc
    une regex qui porterait une apostrophe ne dérègle qu'une ligne.
    """
    i, n, ligne = 0, len(source), 1
    while i < n:
        c = source[i]
        if c == "\n":
            ligne += 1
        elif source.startswith("//", i):
            j = source.find("\n", i)
            i = n if j < 0 else j
            continue
        elif source.startswith("/*", i):
            j = source.find("*/", i + 2)
            j = n if j < 0 else j + 2
            ligne += source.count("\n", i, j)
            i = j
            continue
        elif c in "'\"`":
            j = i + 1
            while j < n and source[j] != c and (c == "`" or source[j] != "\n"):
                j += 2 if source[j] == "\\" else 1
            yield ligne, source[i + 1:j]
            ligne += source.count("\n", i, j)
            i = j + 1
            continue
        i += 1


def fautes(texte, noms=False):
    mots = CAPITALES.findall(texte)
    if noms:
        mots += [m.upper() for m in NOM.findall(texte)]
    return sorted({m for m in mots if m in SANS_ACCENT})


def test_le_lecteur_de_chaines_ignore_les_commentaires():
    """Le juge ne vaut que si son lecteur mord au bon endroit : une chaîne
    fautive se voit, un commentaire fautif non, et un mot accentué passe."""
    source = (
        "// HOPITAL en commentaire\n"
        "/* DEJA, ET SUR DEUX\n LIGNES */\n"
        "Hud.message('PARTIE SAUVEGARDEE'); // TETE\n"
        "const x = \"L'HÔPITAL\", y = `DÉJÀ ${n} FOIS`;\n"
    )
    trouve = {(ligne, mot) for ligne, s in chaines_js(source) for mot in fautes(s)}
    assert trouve == {(4, "SAUVEGARDEE")}
    assert fautes("HÔPITAL À MOITIÉ PRIX") == []
    assert fautes("Fourriere municipale", noms=True) == ["FOURRIERE"]


def test_aucun_texte_du_moteur_n_a_perdu_son_accent():
    """Les messages, menus et invites écrits dans `static/js`."""
    trouves = []
    for fichier in sorted((RACINE / "static/js").glob("*.js")):
        for ligne, s in chaines_js(fichier.read_text(encoding="utf-8")):
            for mot in fautes(s):
                trouves.append(f"{fichier.name}:{ligne} {mot} dans {s[:60]!r}")
    assert trouves == [], "\n".join(trouves)


def test_aucun_texte_du_paquet_n_a_perdu_son_accent(paquet):
    """Tout ce que le serveur envoie au navigateur : enseignes, journal, paliers,
    répliques, noms de lieux — la carte comprise."""
    trouves = []

    def parcourir(valeur, chemin):
        if isinstance(valeur, dict):
            for cle, v in valeur.items():
                if cle not in CLES_MUETTES:
                    parcourir(v, f"{chemin}.{cle}")
        elif isinstance(valeur, list):
            for k, v in enumerate(valeur):
                parcourir(v, f"{chemin}[{k}]")
        elif isinstance(valeur, str):
            for mot in fautes(valeur, noms=True):
                trouves.append(f"{chemin} : {mot} dans {valeur[:60]!r}")

    parcourir(paquet, "paquet")
    assert trouves == [], "\n".join(trouves[:40])


def test_la_liste_ne_contient_que_des_mots_sans_accent():
    """Un mot accentué dans la liste ne pourrait jamais être trouvé : le juge
    aurait l'air de garder une porte qui n'existe pas."""
    assert all(re.fullmatch(r"[A-Z]+", m) for m in SANS_ACCENT)
    assert json.dumps(sorted(SANS_ACCENT)).isascii()
