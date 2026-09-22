"""La mission h02 — voir app/missions/__init__.py pour le moteur."""

from ._commun import _a, _l, _p

MISSION = {
    "slug": "h02",
    "titre": "Les pilules",
    "donneur": "ginette",
    "prerequis": ["h01"],
    "recompense": 250,
    "donne": {"message": "LA PHARMACIE EST AU COMPLET"},

    # ⚠️ `suivre` (même patron que f06 : `vehicule`, `loin`/`proche`, et le `lieu` où
    # il va — c'est son arrivée au dépanneur qui fait avancer l'objectif) puis
    # `pickpocket` (même patron que f07 : l'archétype dédié, jamais un archétype
    # de gang). Ginette se tient DEHORS (`porte:hopital`) : `retourner` fonctionne.
    # ⚠️ Plus longue (Martin, 22 sept. 2026, « des missions plus longues ») : au
    # dépanneur, on fait jaser Ti-Paul (`parler`, sa poignée de main dite) ; le commis
    # volé crie au voleur (`semer`) ; et on rapporte les pilules jusqu'à l'hôpital
    # (≈ 245 tuiles). ⚠️ Pas de détour (`par`) pour le commis : la filature traverse
    # déjà la ville (≈ 105 s au banc, la plus longue du jeu) — par la cantine, elle
    # passait à 173 s, et l'intro annonce le dépanneur, pas les Quais.
    "objectifs": [
        {"type": "suivre", "texte": "SUIS-LE SANS TE FAIRE REPÉRER",
         "vehicule": "auto", "loin": 10, "proche": 3, "lieu": "depanneur"},

        {"type": "parler", "texte": "FAIS JASER TI-PAUL SUR LE COMMIS", "cible": "tipaul"},

        {"type": "pickpocket", "texte": "REPRENDS LES PILULES, PAR-DERRIÈRE", "cible": "pickpocket"},

        {"type": "semer", "texte": "IL CRIE AU VOLEUR — SÈME LA POLICE", "etoiles": 1},

        {"type": "retourner", "texte": "RAPPORTE-LES À GINETTE"},
    ],

    # Le jeu de chaque réplique (`jeu=`) — Ginette : sèche, elle sait tout ce qui se
    # passe dans son hôpital et n'a pas de patience pour ceux qui en profitent.
    "dialogue": {
        "appel": [
            _l("ginette", "C'est Ginette, de l'hôpital. Un commis vide notre pharmacie depuis des semaines. J'ai besoin de toi.",
               jeu="[annoyed] C'est Ginette, de l'hôpital. Un commis vide notre pharmacie depuis des semaines. [firmly] J'ai besoin de toi.")
        ],
        "intro": [
            _l("ginette", "Il sort dans dix minutes. Suis-le sans qu'il te voie, il va vendre ça au dépanneur.",
               jeu="[matter-of-fact] Il sort dans dix minutes. [firmly] Suis-le sans qu'il te voie… il va vendre ça au dépanneur."),
            _l("ginette", "Une fois la vente faite, reprends nos pilules par-derrière. Discret, comme toujours.",
               jeu="[knowingly] Une fois la vente faite, reprends nos pilules par-derrière. [quietly] Discret, comme toujours."),
            _l("ginette", "S'il crie au voleur, cours pas. Cache-toi, pis attends que ça passe.",
               jeu="[firmly] S'il crie au voleur, cours pas. [quietly] Cache-toi… pis attends que ça passe.")
        ],
        "pendant": [
            _p("ginette", "Il regarde dans son rétroviseur souvent. Garde tes distances.", 0,
               jeu="[gravely] Il regarde dans son rétroviseur souvent. [firmly] Garde tes distances."),
            _p("ginette", "Il est rentré chez Ti-Paul. Va voir ce qu'il lui vend, l'air de rien.", 1,
               jeu="[knowingly] Il est rentré chez Ti-Paul. [quietly] Va voir ce qu'il lui vend… l'air de rien."),
            _p("ginette", "Il crie au voleur, lui? Ça prend du front. Perds la police, pis reviens.", 3,
               jeu="[annoyed] Il crie au voleur, lui? [sarcastic] Ça prend du front. [firmly] Perds la police, pis reviens.")
        ],
        "accueil": [
            _a("tipaul", "Ton commis? Y m'offre des pilules pour dormir, l'ami. Avec mes vitrines, je dors pas pareil!", 1,
               jeu="[knowingly] Ton commis? Y m'offre des pilules pour dormir, l'ami. [cheerful] Avec mes vitrines… je dors pas pareil!")
        ],
        "fin": [
            _l("ginette", "Toutes là. Ce commis-là ne remettra plus les pieds dans ma pharmacie.",
               jeu="[satisfied] Toutes là. [firmly] Ce commis-là ne remettra plus les pieds dans ma pharmacie."),
            _l("ginette", "Bon travail. L'hôpital s'en souviendra, la prochaine fois que t'en auras besoin.",
               jeu="[matter-of-fact] Bon travail. [warmly] L'hôpital s'en souviendra, la prochaine fois que t'en auras besoin."),
            _l("ginette", "Pis si Ti-Paul dort mal, dis-y que ses vitrines, c'est pas mon département.",
               jeu="[wryly] Pis si Ti-Paul dort mal, dis-y que ses vitrines… [matter-of-fact] c'est pas mon département.")
        ],
        "echec": [
            _l("ginette", "Perdues... Il va continuer à vider mes tablettes. Reviens quand t'es prêt.",
               jeu="[disappointed] Perdues… [annoyed] Il va continuer à vider mes tablettes. Reviens quand t'es prêt.")
        ]
    }
}
