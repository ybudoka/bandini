"""Les deux petites usines de repliques, partagees par l'ouverture et les missions.

Chaque mission vit dans son propre fichier (`m1.py`, `m2.py`, …), chacun
n'ayant besoin que de ces deux-la pour ecrire ses dialogues. Elles sont ici,
pas recopiees dans chaque fichier, pour qu'une replique reste un dicton
identique partout : la boite de dialogue et la voix generee lisent le meme
`qui`/`texte` (voir `audio.voix_histoire`).
"""


def _l(qui: str, texte: str) -> dict:
    return {"qui": qui, "texte": texte}


def _p(qui: str, texte: str, objectif: int) -> dict:
    """Une réplique PENDANT : dite quand l'objectif `objectif` (compté à partir de 0)
    commence — au combiné si celui qui la dit n'est pas là."""
    return {"qui": qui, "texte": texte, "objectif": objectif}
