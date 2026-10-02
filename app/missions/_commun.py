"""Les petites usines de repliques (`_l`, `_p`, `_r`, `_a`, `_e`), partagees par l'ouverture et les missions.

Chaque mission vit dans son propre fichier (`m1.py`, `m2.py`, …), chacun
n'ayant besoin que de ces quatre-la pour ecrire ses dialogues. Elles sont ici,
pas recopiees dans chaque fichier, pour qu'une replique reste un dicton
identique partout : la boite de dialogue et la voix generee lisent le meme
`qui`/`texte` (voir `audio.voix_histoire`).
"""


def _ligne(qui: str, texte: str, jeu: str | None, hiver: tuple[str, str] | None = None, **cles) -> dict:
    """Une réplique. ⚠️ `jeu` est ce qu'ElevenLabs DIT — les mêmes mots que `texte`, plus des balises
    d'émotion en anglais (`[worried]`), des « … » et de la ponctuation (`docs/jeu-d-acteur.md` § 3).
    Il vit ICI, collé à la réplique, dans le fichier de la mission : une mission se lit d'un bloc, et
    une réplique insérée au milieu n'emporte plus le jeu de sa voisine. `interpretation.JEU` le
    rassemble ; le navigateur, lui, ne le reçoit jamais (`missions.pour_le_navigateur`)."""
    ligne = {"qui": qui, "texte": texte, **cles}
    if jeu is not None:
        ligne["jeu"] = jeu
    # ⚠️ LA VARIANTE D'HIVER (Martin, 29 sept. 2026) : `hiver=(texte, jeu)`, ce que la réplique dit
    # tant que la neige tient — l'hiver, la moto est remisée et le fuyard file en motoneige. Elle a SA
    # voix, au slug de la réplique suivi de `-hiver` (`missions.repliques`) : aucune autre ne change
    # de nom. Le navigateur choisit (`Histoire.lignesDe`, `Saisons.enHiver`).
    if hiver is not None:
        ligne["hiver"] = {"texte": hiver[0], "jeu": hiver[1]}
    return ligne


def _bifurque(ligne: dict, branche: str | None, choix: list[tuple[str, str]] | None) -> dict:
    """⚠️ UN CHOIX DANS UN DIALOGUE (1er oct. 2026, Martin) : `choix=[(cle, texte), …]` — la réplique POSE la
    question, et le joueur répond (deux ou trois réponses, au clavier, à la manette ou au doigt) ; la mission
    bifurque (`missions.erreurs_de_choix`). `branche=cle` : la réplique ne se dit que sur cette branche-là."""
    if choix is not None:
        ligne["choix"] = [{"cle": cle, "texte": texte} for cle, texte in choix]
    if branche is not None:
        ligne["branche"] = branche
    return ligne


def _l(qui: str, texte: str, jeu: str | None = None, hiver: tuple[str, str] | None = None,
       branche: str | None = None, choix: list[tuple[str, str]] | None = None) -> dict:
    return _bifurque(_ligne(qui, texte, jeu, hiver), branche, choix)


def _p(qui: str, texte: str, objectif: int, jeu: str | None = None, hiver: tuple[str, str] | None = None,
       si: str | None = None, sauf: str | None = None,
       branche: str | None = None, choix: list[tuple[str, str]] | None = None) -> dict:
    """Une réplique PENDANT : dite quand l'objectif `objectif` (compté à partir de 0)
    commence — au combiné si celui qui la dit n'est pas là. `si` / `sauf` (le casse, x04) : dite
    seulement si cette mission est faite / ne l'est pas — ce qu'on a préparé, et ce qui manque
    (`Histoire.tenu`). `branche` / `choix` : un choix dans un dialogue (`_bifurque`)."""
    cles = {k: v for k, v in (("si", si), ("sauf", sauf)) if v}
    return _bifurque(_ligne(qui, texte, jeu, hiver, objectif=objectif, **cles), branche, choix)


def _r(qui: str, texte: str, objectif: int, jeu: str | None = None) -> dict:
    """Une réplique RENVOI : ce que dit `qui` quand on LUI parle alors que l'objectif
    `objectif` est en cours et que ce n'est pas encore son tour — « reviens à la nuit ».
    Elle se dit en personne, jamais au combiné : on est devant lui."""
    return _ligne(qui, texte, jeu, objectif=objectif)


def _e(qui: str, texte: str, objectif: int, jeu: str | None = None) -> dict:
    """Une réplique ÉCHEC d'un ACTE (un chapitre, 2 oct. 2026) : `objectif` est l'étape du marqueur de son acte —
    elle ne se dit que si c'est cet acte-là qui rate (`Histoire.echouer`). Au combiné, comme tout échec."""
    return _ligne(qui, texte, jeu, objectif=objectif)


def _a(qui: str, texte: str, objectif: int, jeu: str | None = None,
       branche: str | None = None, choix: list[tuple[str, str]] | None = None) -> dict:
    """Une réplique ACCUEIL : ce que dit `qui` quand on lui serre la main pour l'objectif `parler`
    `objectif` dont il est la cible (les quatre contacts de m6). Elle se dit en personne — on est
    devant lui — puis l'objectif avance ; sans réplique, la poignée de main reste muette."""
    return _bifurque(_ligne(qui, texte, jeu, objectif=objectif), branche, choix)
