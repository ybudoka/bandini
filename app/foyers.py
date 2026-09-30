"""Les foyers de l'hiver (docs/jalons/la-foire-fermee-l-hiver.md, vague 3).

Martin (30 sept. 2026) : l'hiver ferme la foire, les amuseurs, la fontaine — « à la place : jongleur de
feu, des foyers centraux et des vendeurs de chocolat chaud ». Tranché : sur chaque place publique, un
brasero de part et d'autre de la fontaine à sec, où des passants s'arrêtent se chauffer les mains et où le
joueur reprend son souffle plus vite ; une roulotte de chocolat chaud juste sous la fontaine.

⚠️ RIEN NE SE POSE : le navigateur lit les places sur la carte finie (la fontaine de `_place`) et PEINT
braseros et roulotte (`static/js/foyers.js`), sans un dé et sans une entité — un décor posé en janvier
décalerait les numéros de toute la ville, et la ville d'été n'en aurait pas trace.
"""

from __future__ import annotations

#: Les places candidates autour de la fontaine, en tuiles depuis son pied, dans l'ordre où on les essaie :
#: un brasero à l'ouest et un à l'est (`cote` −1 / +1, le `dx` se retourne), la roulotte au sud. La première
#: tuile libre gagne — une place n'a pas ses bancs aux mêmes endroits qu'une autre (`_place` les tire).
BRASERO_ESSAIS: tuple[tuple[int, int], ...] = ((3, 0), (3, 1), (3, -1), (4, 0), (4, 1), (2, 2), (4, -1))
ROULOTTE_ESSAIS: tuple[tuple[int, int], ...] = ((0, 3), (1, 3), (-1, 3), (0, 4), (2, 3), (-2, 3), (0, -3))

FOYERS: dict = {
    "brasero_essais": [list(e) for e in BRASERO_ESSAIS],
    "roulotte_essais": [list(e) for e in ROULOTTE_ESSAIS],
    # Rien à moins de ce rayon d'un décor posé (banc, arbre, lampadaire) : on ne brûle pas un banc.
    "degagement_px": 14,
    # La lueur, le soir : celle du baril du bidonville (`SORTES_DE_LAMPE.feu`), un peu plus large.
    "lueur_px": 64,
    # Le joueur debout près du feu : son souffle remonte en plus de ce qu'il remonte seul (par image).
    "chaleur_px": 30,
    "chaleur_souffle": 0.35,
    # Les passants qui s'arrêtent : dans ce rayon, un sur `part` (à l'empreinte du passant et du jour,
    # jamais au dé), au plus `par_feu` autour d'un même brasero, `patience_images` à se chauffer.
    "appel_px": 120,
    "part": 3,
    "par_feu": 3,
    "cercle_px": 15,
    "patience_images": [420, 900],
    # La tasse, ACTION devant la roulotte : un commerce comme ceux du trottoir (`Missions.acheterAmbulant`).
    "chocolat": {"slug": "chocolat", "nom": "Chocolat chaud", "service": "manger", "tarif": "chocolat_chaud",
                 "gain_pv": "chocolat_chaud_pv", "gain_souffle": "chocolat_chaud_souffle", "effet": None, "heures": None},
    "portee_roulotte_px": 24,
}
