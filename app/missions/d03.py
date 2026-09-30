"""La mission d03 — voir app/missions/__init__.py pour le moteur.

Les Ciseaux (M16, arc D, 30 sept. 2026). Les hommes de Sal, on les appelle les Ciseaux : ils coupent ce qui
dépasse. Mais aux Quais, trois gars collectent EN SON NOM, et gardent tout. Sal ne peut pas envoyer les siens
régler ça — ça ferait une guerre ; toi, t'es « la famille ». On couche les faux Ciseaux devant l'Hôtel Bandini,
on sème la police qui s'en mêle, et on revient au terminus.
"""

from ._commun import _l, _p

MISSION = {
    "slug": "d03",
    "titre": "Les Ciseaux",
    "donneur": "sal",
    "prerequis": ["d02"],
    "recompense": 300,
    "donne": {"dette": -300, "message": "LES CISEAUX, LES VRAIS, TE SALUENT"},

    # ⚠️ `tuer` des Cravates (le corps des hommes de Sal : `missions.js` `envoyerLesCollecteurs`), posés devant
    # l'hôtel (`ou: hotel`, déjà un lieu de mission de f06/q13 : la ville ne bouge pas) — les poings et le poing
    # américain, comme les vrais (`economie.DETTE["armes"]`), et un chef à la batte. ⚠️ Jamais à l'étape 0 là où
    # la mission FINIT (le terminus) : ils se battraient sous la scène de fin.
    "objectifs": [
        {"type": "tuer", "texte": "DE FAUX CISEAUX COLLECTENT AUX QUAIS : COUCHE-LES",
         "groupe": "cravates", "n": 3, "ou": "hotel", "arme": "poing_americain", "chef": True},

        {"type": "semer", "texte": "LA POLICE DES QUAIS S'EN MÊLE : SÈME-LA", "etoiles": 2},

        {"type": "parler", "texte": "DIS À SAL QUE C'EST RÉGLÉ, AU TERMINUS", "cible": "sal"},
    ],

    # Intention (intro) : Sal parle en coupant les cheveux — un geste, puis chaque réplique tient la scène (la voix
    # retient le plan ; l'intro par défaut les disait en `ensemble`, et la suivante coupait la première).
    "scenes": {
        "intro": [
            {"type": "geste", "acteur": "donneur", "geste": "bras_croises", "duree": 90, "ensemble": True},
            {"type": "dire", "repliques": [1]},
            {"type": "attendre", "duree": 20},
            {"type": "dire", "repliques": [2]},
            {"type": "coupe", "vers": "porte:hotel", "ferme": 20, "ouvre": 20, "tient": 170, "ensemble": True},
            {"type": "dire", "repliques": [3]},
        ]
    },

    # Le jeu de chaque réplique (`jeu=`) — Sal : pour la première fois, il est vexé, et ça le rend plus doux encore.
    # On parle de son NOM : il y tient plus qu'à l'argent. À la fin, une fierté de patriarche, vite rangée.
    "dialogue": {
        "appel": [
            _l("sal", "Sal, le barbier. J'ai un problème de réputation, le neveu. Pis toi, t'as une dette.",
               jeu="[quietly] Sal, le barbier. [annoyed] J'ai un problème de réputation, le neveu. [calm] Pis toi, t'as une dette.")
        ],
        "intro": [
            _l("sal", "Mes hommes, on les appelle les Ciseaux. Ils coupent ce qui dépasse.",
               jeu="[calm] Mes hommes, on les appelle les Ciseaux. [menacingly] Ils coupent ce qui dépasse."),
            _l("sal", "Aux Quais, trois gars collectent en mon nom, devant l'hôtel. Pis ils gardent tout.",
               jeu="[annoyed] Aux Quais, trois gars collectent en mon nom, devant l'hôtel. [bitterly] Pis ils gardent tout."),
            _l("sal", "Si j'envoie les miens, ça fait une guerre. Toi, t'es la famille. Va leur couper les cheveux.",
               jeu="[matter-of-fact] Si j'envoie les miens, ça fait une guerre. [softly] Toi, t'es la famille… [menacingly] Va leur couper les cheveux.")
        ],
        "pendant": [
            _p("sal", "Le plus grand, c'est leur chef. Il se promène avec un bâton comme si c'était une canne.", 0,
               jeu="[wryly] Le plus grand, c'est leur chef. [amused] Il se promène avec un bâton comme si c'était une canne."),
            _p("sal", "La police des Quais dort d'habitude. Faut croire que t'as fait du bruit.", 1,
               jeu="[amused] La police des Quais dort d'habitude. [knowingly] Faut croire que t'as fait du bruit.")
        ],
        "fin": [
            _l("sal", "Trois gars de moins qui disent mon nom. Mon nom, le neveu, c'est tout ce que j'ai.",
               jeu="[satisfied] Trois gars de moins qui disent mon nom. [serious] Mon nom, le neveu… c'est tout ce que j'ai."),
            _l("sal", "Ton oncle aurait négocié. Toi, tu règles. Je sais pas encore si c'est mieux.",
               jeu="[impressed] Ton oncle aurait négocié. Toi, tu règles. [wryly] Je sais pas encore si c'est mieux.")
        ],
        "echec": [
            _l("sal", "Ils collectent encore, pis ils disent que le barbier a envoyé un enfant. Merci bien.",
               jeu="[coldly] Ils collectent encore, pis ils disent que le barbier a envoyé un enfant. [sarcastic] Merci bien.")
        ]
    }
}
