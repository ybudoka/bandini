"""Des bagarres de gangs vivantes, et armées (docs/jalons/des-bagarres-de-gangs-vivantes-et-armees.md).

Martin (30 sept. 2026) : « revise les bagarres de gang pour que ce soit dynamique et réaliste ». Ce module décide ;
le navigateur joue (`static/js/rixe.js`) : UN SEUL CERVEAU pour la rixe à la frontière (sa cible : un rival) et
pour le gang qui te tombe dessus (sa cible : toi).

⚠️ Toutes les durées en images (60 par seconde), les distances en pixels ; RIEN au dé du jeu — la place, le
rythme et l'esquive se lisent à l'EMPREINTE de l'identifiant (la leçon du char en panne).
"""

from __future__ import annotations

#: VAGUE 1 — AU CONTACT. Avant : chacun marchait droit sur sa cible, se plantait et cognait au métronome
#: (`e.t % 38` dans la rixe, `% 40` contre toi) — six hommes nés à la même image frappaient à la même image, en
#: file indienne. Maintenant chacun prend SA place sur un cercle autour de la cible (son rang parmi ceux qui la
#: visent), fait un pas de côté de temps en temps, recule après son coup, et esquive parfois le tien.
CONTACT: dict = {
    "portee_px": 20,          # d'où il frappe (la rixe frappait à 22, le gang contre toi à 18)
    "cercle_px": 16,          # le rayon de sa place autour de la cible : en deçà de la portée
    "places": 8,              # combien de places sur le cercle (on n'en garde que les libres, hors des murs)
    "place_px": 8,            # « à sa place » : il ne frappe que de là (ou d'où il est, si sa place est un mur)
    "bouge_px": 0.3,          # une cible qui bouge de plus que ça par image : il frappe à portée, sans attendre sa place
    "coince_images": 20,      # à portée, sa place prise par des corps et plus moyen d'en approcher : il frappe d'où il est
    "contourne_rad": 0.8,     # pour gagner sa place, il tourne autour de la cible d'au plus ça à la fois
    "cadence_images": 40,     # un coup toutes les deux tiers de seconde au plus (geste compris), en moyenne…
    "cadence_ecart": 12,      # … plus ou moins ça, à l'empreinte : jamais au métronome commun
    # ⚠️ UN PAS EN ARRIÈRE, PAS UNE RETRAITE : le geste dure déjà 26 images au bâton, et 18 images de recul
    # plus le retour faisaient un coup par seconde — le gang frappait un tiers moins souvent qu'avant (la
    # relecture du 30 sept. 2026).
    "recul_images": 10,       # après son coup (ou une esquive), il recule ce temps-là
    "recul_allure": 0.8,      # à reculons, un peu moins vite qu'en avançant
    "tourne_min": 50,         # entre deux pas de côté, en images (à l'empreinte)
    "tourne_max": 110,
    "tourne_rad": 0.7,        # l'ampleur du pas de côté, en tournant autour de la cible
    "pas_images": 24,         # combien de temps il le tient
    "esquive_pct": 30,        # sur cent coups armés à portée, combien il en esquive
    "esquive_marge_px": 8,    # « à portée » : celle de l'arme de la cible, plus ça
}


def exporter() -> dict:
    """Ce que le navigateur reçoit sous `B.defs.rixes`."""
    return {"contact": dict(CONTACT)}
