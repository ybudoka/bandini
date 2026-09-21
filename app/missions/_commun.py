"""Les petites usines de repliques (`_l`, `_p`, `_r`, `_a`), partagees par l'ouverture et les missions.

Chaque mission vit dans son propre fichier (`m1.py`, `m2.py`, …), chacun
n'ayant besoin que de ces quatre-la pour ecrire ses dialogues. Elles sont ici,
pas recopiees dans chaque fichier, pour qu'une replique reste un dicton
identique partout : la boite de dialogue et la voix generee lisent le meme
`qui`/`texte` (voir `audio.voix_histoire`).
"""


def _ligne(qui: str, texte: str, jeu: str | None, **cles) -> dict:
    """Une réplique. ⚠️ `jeu` est ce qu'ElevenLabs DIT — les mêmes mots que `texte`, plus des balises
    d'émotion en anglais (`[worried]`), des « … » et de la ponctuation (`docs/jeu-d-acteur.md` § 3).
    Il vit ICI, collé à la réplique, dans le fichier de la mission : une mission se lit d'un bloc, et
    une réplique insérée au milieu n'emporte plus le jeu de sa voisine. `interpretation.JEU` le
    rassemble ; le navigateur, lui, ne le reçoit jamais (`missions.pour_le_navigateur`)."""
    ligne = {"qui": qui, "texte": texte, **cles}
    if jeu is not None:
        ligne["jeu"] = jeu
    return ligne


def _l(qui: str, texte: str, jeu: str | None = None) -> dict:
    return _ligne(qui, texte, jeu)


def _p(qui: str, texte: str, objectif: int, jeu: str | None = None) -> dict:
    """Une réplique PENDANT : dite quand l'objectif `objectif` (compté à partir de 0)
    commence — au combiné si celui qui la dit n'est pas là."""
    return _ligne(qui, texte, jeu, objectif=objectif)


def _r(qui: str, texte: str, objectif: int, jeu: str | None = None) -> dict:
    """Une réplique RENVOI : ce que dit `qui` quand on LUI parle alors que l'objectif
    `objectif` est en cours et que ce n'est pas encore son tour — « reviens à la nuit ».
    Elle se dit en personne, jamais au combiné : on est devant lui."""
    return _ligne(qui, texte, jeu, objectif=objectif)


def _a(qui: str, texte: str, objectif: int, jeu: str | None = None) -> dict:
    """Une réplique ACCUEIL : ce que dit `qui` quand on lui serre la main pour l'objectif `parler`
    `objectif` dont il est la cible (les quatre contacts de m6). Elle se dit en personne — on est
    devant lui — puis l'objectif avance ; sans réplique, la poignée de main reste muette."""
    return _ligne(qui, texte, jeu, objectif=objectif)
