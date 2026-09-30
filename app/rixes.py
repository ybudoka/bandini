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


#: VAGUE 2 — L'ARSENAL (Martin, 30 sept. 2026 : « un arsenal par gang, un membre sur trois »). Chaque gang se
#: reconnaît à son arme ; les Mantes n'en ont pas, elles ont l'école (`mantes.COMBAT`).
ARSENAL: dict = {
    "cravates": "pistolet",       # propres, précis, à mi-distance
    "morues": "fusil",            # elles foncent et tirent de près
    "chevreuils": "carabine",     # ils restent loin, lents et justes
    "boulonneux": "mitraillette",  # des rafales qui s'ouvrent : les plus dangereux
    "skateux": "molotov",         # ils lancent et se sauvent
}
#: Un sur combien la porte : `hash2(e.id, …) % PART_ARMEE == 0`, à l'empreinte — toujours le même homme.
PART_ARMEE = 3

#: VAGUE 2 — LA FUSILLADE. Le tireur tient SA distance, cherche un abri d'où la cible ne le voit pas, en sort pour
#: une salve, y rentre, et recharge ; il lève l'arme avant sa première balle (le geste qu'on voit venir, comme
#: l'anticipation d'un coup), et il manque plus que toi. ⚠️ Images (60 par seconde) et pixels.
TIR: dict = {
    # La fourchette où il se tient, par arme. ⚠️ Le Molotov part EN CLOCHE et retombe vers 100 px quoi qu'on
    # vise : sa fourchette est sa distance de chute (un juge la calcule).
    "distances": {"pistolet": (70, 140), "fusil": (30, 70), "carabine": (140, 210),
                  "mitraillette": (60, 120), "molotov": (85, 110)},
    "lever_images": 30,           # il lève l'arme avant sa PREMIÈRE balle : le temps de rouler
    # … et ça se voit : il crie une de ces répliques en la levant (la relecture : une levée muette ne prévient pas).
    "lever_mots": ["BOUGE PAS!", "T'ES CUIT!", "À TERRE, LÀ!", "T'AS PAS D'AFFAIRE ICITTE!"],
    "retour_images": 120,         # absent du combat plus longtemps que ça, il relève l'arme en revenant
    "salve": (2, 4),              # balles par salve, à l'empreinte
    "rafale_images": 24,          # la mitraillette, elle, tient la gâchette ce temps-là
    "entre_salves_images": 70,    # à l'abri entre deux salves
    "recharge_images": 90,        # le chargeur vide (celui de l'arme), il recharge
    "dispersion_facteur": 2.0,    # sa dispersion, par rapport à la tienne
    "abri_tuiles": 5,             # jusqu'où il cherche un abri
    "degats_contre_joueur": 0.5,  # sa balle te prend moitié moins : trois tireurs ne te couchent pas en une seconde
    "fuite_images": 60,           # le lanceur, sa bouteille partie, se sauve ce temps-là
}


def exporter() -> dict:
    """Ce que le navigateur reçoit sous `B.defs.rixes`."""
    tir = dict(TIR, distances={k: list(v) for k, v in TIR["distances"].items()}, salve=list(TIR["salve"]),
               lever_mots=list(TIR["lever_mots"]))
    return {"contact": dict(CONTACT), "arsenal": dict(ARSENAL), "part_armee": PART_ARMEE, "tir": tir}
