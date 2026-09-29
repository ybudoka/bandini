"""Des photos pour le Clairon (docs/jalons/des-photos-pour-le-clairon.md).

Le mode photo (M14) devient un boulot : Louise Tremblay-Dion, journaliste au Clairon de la Baie, achète UNE
photo par jour — un char en feu, un char qui vole, une poursuite, une figure du quartier —, et la une du
lendemain l'affiche. Le piège : une photo de TOI en pleine poursuite se vend très cher… et le lendemain, toute
la ville a vu ta face (une étoile).

⚠️ **LE JEU NE VOIT PAS L'IMAGE** : au déclic, il juge ce qui est DANS LE CADRE — les entités à l'écran à ce
moment-là (`static/js/photos.js`, `juger`) —, jamais les pixels. La meilleure photo de la journée attend dans
la partie (`partie.photo`) ; elle se vend le jour même ou le lendemain, pas après (« du réchauffé »).
"""

from __future__ import annotations

#: Ce que Louise paie, par sujet, et la une qu'elle en tire. `titre` : la ligne du Clairon du lendemain.
#: Le meilleur sujet du cadre l'emporte (le plus cher). `toi` n'est pas un sujet qu'on cherche : c'est une
#: poursuite où l'on se voit soi-même.
SUJETS: dict[str, dict] = {
    "toi": {"nom": "TOI, EN PLEINE POURSUITE", "prix": 300,
            "titre": "EN UNE : L'INSAISISSABLE, EN PLEINE POURSUITE — LA POLICE A SA FACE"},
    "feu": {"nom": "UN CHAR EN FEU", "prix": 150, "titre": "EN UNE : UN CHAR FLAMBE EN PLEINE RUE"},
    "vol": {"nom": "UN CHAR QUI VOLE", "prix": 120, "titre": "EN UNE : UN CHAR PREND SON ENVOL"},
    "poursuite": {"nom": "UNE POURSUITE", "prix": 90, "titre": "EN UNE : LA POLICE AUX TROUSSES D'UN FUYARD"},
    "personnage": {"nom": "UNE FIGURE DU QUARTIER", "prix": 40, "titre": "EN UNE : UNE FIGURE DU QUARTIER"},
}

REGLES = {
    # Une poursuite vaut plus à chaque étoile.
    "par_etoile": 20,
    # Une photo se vend le jour du déclic ou le lendemain.
    "fraiche_jours": 1,
    # Une photo de toi en une : le lendemain, la police t'a vu (au moins cette étoile-là).
    "etoiles_toi": 1,
    # Un char « en l'air » sur la photo : au-dessus de tant de pixels (le code du jeu dit « en l'air » à 6).
    "vol_z": 6,
}

#: Ce que Louise dit, par clé. Le slug de la voix : `louise-clairon-<cle>` ; le jeu d'acteur est dans
#: `interpretation.JEU`. ⚠️ Elle se nomme UNE fois, dans sa salutation (« Qui parle se nomme »).
REPLIQUES: list[dict] = [
    {"cle": "salut", "texte": "Louise Tremblay-Dion, du Clairon. Tu traînes où ça brasse : rapporte-moi une photo, je paie."},
    {"cle": "rien", "texte": "Pas de photo? Reviens quand ça brûle, quand ça vole ou quand ça sirène."},
    {"cle": "vide", "texte": "Un trottoir vide, magnifique. Le Clairon paie pas pour du trottoir."},
    {"cle": "achat", "texte": "Ça, c'est une une : tiens, ton argent. Tu la verras demain matin."},
    {"cle": "toi", "texte": "C'est toi, ça, en pleine poursuite? Je la prends — la police va l'aimer aussi."},
    {"cle": "vieille", "texte": "Ta photo date d'avant-hier. Le Clairon sort tous les matins, mon beau."},
    {"cle": "deja", "texte": "J'ai ma une pour demain. Reviens demain avec mieux."},
]


def repliques() -> list[dict]:
    """Les voix de Louise, rangées ensemble (`mission: "clairon"`) : une série du paquet."""
    return [{"slug": f"louise-clairon-{r['cle']}", "qui": "louise", "texte": r["texte"],
             "mission": "clairon", "partie": "clairon", "telephone": False} for r in REPLIQUES]


def meilleur(sujets: list[str]) -> str | None:
    """Le sujet qui paie le plus parmi ceux du cadre (miroir de `Photos.juger`), ou None."""
    connus = [s for s in sujets if s in SUJETS]
    return max(connus, key=lambda s: SUJETS[s]["prix"]) if connus else None


def pour_le_navigateur() -> dict:
    return {"sujets": {k: dict(v) for k, v in SUJETS.items()}, "regles": dict(REGLES),
            "repliques": {r["cle"]: r["texte"] for r in REPLIQUES}}
