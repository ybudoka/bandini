"""Les saisons de Baie-des-Brumes : la ville change de couleur avec l'année (29 sept. 2026).

Le calendrier (`calendrier.py`) disait la saison ; la ville restait verte en janvier. Ici, les
DONNÉES seulement : six palettes (ce qui pousse, la neige qui tient), les images-clés de l'année (où
chaque palette tient et où elle glisse vers la suivante), et la longueur du jour. Le navigateur en
tire la palette du moment (`static/js/saisons.js`), en huit paliers par transition — c'est le palier
qui fait repeindre les tuiles cuites, pas l'heure.

⚠️ AUCUN DÉ, RIEN DE POSÉ : une pure fonction du jour et de l'heure ; la ville ne bouge pas d'un octet.
⚠️ LA LUMIÈRE EST POUR LES YEUX : les règles (commerces, barrières, police, missions « la nuit ») gardent
l'horloge fixe de `Monde.ambiance` ; seul le rendu lit `heureDeLumiere`.
"""

from __future__ import annotations

from app import calendrier

#: Combien de paliers dans une transition : un palier = une repeinte des tuiles cuites.
PALIERS = 8

#: Les images-clés : [jour de l'année (1 à 41, fractions permises), palette]. Deux clés de même palette
#: = la palette tient ; deux palettes différentes = elle glisse de l'une à l'autre.
CLES = [
    (1, "hiver"), (10.5, "hiver"),            # la neige tient jusqu'au 10 (fin mars)
    (12, "printemps"), (16, "printemps"),     # la fonte, puis le vert tendre
    (18, "ete"), (23, "ete"),
    (25, "fin_ete"), (27, "fin_ete"),         # août : le gazon jaunit
    (29, "automne"), (34, "automne"),         # octobre, l'Halloween (jour 33) en plein rouge
    (35.5, "novembre"), (37, "novembre"),     # les branches nues, le gazon brun
    (38, "hiver"), (41, "hiver"),
]

#: Chaque palette : le gazon (`,`), la friche (`;`), l'arbre de rue (trois teintes [cime, clair, sombre],
#: tirées à l'empreinte de sa tuile ; `feuillage` 0 = nu), et `neige` : la part de blanc sur les
#: trottoirs et les toits.
PALETTES = {
    "ete": {
        "gazon": {"fond": "#4f8d3e", "clair": "#5a9c47", "sombre": "#427a33", "brin": "#6aad55",
                  "terre": "#6d5c3e", "fleur": "#cfc95c", "feuille": "#4f8d3e", "feuille2": "#4f8d3e"},
        "friche": {"fond": "#6d6845", "clair": "#7b7551", "sombre": "#5b5638", "sec": "#a4975f"},
        "arbre": {"teintes": [["#2f6b2a", "#3f8d38", "#204d1e"], ["#2a6330", "#3a8440", "#1d4722"],
                              ["#356f27", "#468f35", "#25501b"]], "feuillage": 1, "neige": 0},
        "neige": 0,
    },
    "printemps": {
        "gazon": {"fond": "#5f9a45", "clair": "#74b057", "sombre": "#4d8438", "brin": "#8cc46a",
                  "terre": "#6a5536", "fleur": "#e8d85a", "feuille": "#5f9a45", "feuille2": "#5f9a45"},
        "friche": {"fond": "#6a6a44", "clair": "#787a50", "sombre": "#585a37", "sec": "#9a9a60"},
        "arbre": {"teintes": [["#4f8f3a", "#6fb050", "#3a7029"], ["#5a9a40", "#7cbc58", "#437a2e"],
                              ["#6aa048", "#8cc466", "#4e8034"]], "feuillage": 0.8, "neige": 0},
        "neige": 0,
    },
    "fin_ete": {
        "gazon": {"fond": "#7a8c42", "clair": "#8f9c4f", "sombre": "#667838", "brin": "#a3a85c",
                  "terre": "#7a6443", "fleur": "#d9b24a", "feuille": "#7a8c42", "feuille2": "#7a8c42"},
        "friche": {"fond": "#7d7546", "clair": "#8b8252", "sombre": "#6a6339", "sec": "#b5a462"},
        "arbre": {"teintes": [["#4a6b2a", "#5f8436", "#34501e"], ["#2f6b2a", "#3f8d38", "#204d1e"],
                              ["#6b7a2a", "#869536", "#4f5c1e"]], "feuillage": 1, "neige": 0},
        "neige": 0,
    },
    "automne": {
        "gazon": {"fond": "#6f7a3c", "clair": "#7f8646", "sombre": "#5c6632", "brin": "#8e8a4c",
                  "terre": "#6d5536", "fleur": "#c8622a", "feuille": "#c0392b", "feuille2": "#e67e22"},
        "friche": {"fond": "#76663f", "clair": "#86744a", "sombre": "#625434", "sec": "#b08850"},
        "arbre": {"teintes": [["#b8321f", "#d9502e", "#7f2416"], ["#d9731f", "#f09a3a", "#9a4f14"],
                              ["#d4a91c", "#efcb3e", "#9a7a12"]], "feuillage": 0.95, "neige": 0},
        "neige": 0,
    },
    "novembre": {
        "gazon": {"fond": "#6b6a45", "clair": "#77744f", "sombre": "#57553a", "brin": "#83805a",
                  "terre": "#5e4a32", "fleur": "#8a5a34", "feuille": "#8a5a34", "feuille2": "#7a4a2a"},
        "friche": {"fond": "#6a5f42", "clair": "#776b4c", "sombre": "#574e36", "sec": "#948058"},
        "arbre": {"teintes": [["#7a4a26", "#94603a", "#5a361c"], ["#8a5a2e", "#a67040", "#643f20"],
                              ["#6e5a34", "#8a7244", "#4f4024"]], "feuillage": 0.3, "neige": 0},
        "neige": 0,
    },
    "hiver": {
        "gazon": {"fond": "#e8edf2", "clair": "#f6f8fb", "sombre": "#cfd8e2", "brin": "#b9c4cf",
                  "terre": "#8a7f70", "fleur": "#dfe6ee", "feuille": "#e8edf2", "feuille2": "#e8edf2"},
        "friche": {"fond": "#e3e7ea", "clair": "#f2f4f6", "sombre": "#c9d0d6", "sec": "#a89f86"},
        "arbre": {"teintes": [["#7a4a26", "#94603a", "#5a361c"], ["#8a5a2e", "#a67040", "#643f20"],
                              ["#6e5a34", "#8a7244", "#4f4024"]], "feuillage": 0, "neige": 1},
        "neige": 0.7,
    },
}

#: La longueur du jour. `coucher`/`lever` = [moyenne, ampleur] en heures : l'heure du jour de l'année x
#: est moyenne ± ampleur × cos(2π (x − solstice_ete) / ANNEE) — 16 h 15 au 21 décembre, 20 h 45 au
#: 21 juin. `reference` = le lever et le coucher de l'horloge fixe (`Monde.TEINTES` : 0,30 et 0,80).
LUMIERE = {"solstice_ete": 19.7, "coucher": [18.5, 2.25], "lever": [6.25, -1.2], "reference": [7.2, 19.2]}


def palette_du_jour(jour_de_l_annee: float) -> str:
    """La palette qui TIENT ce jour-là (la clé précédente), sans le glissement — pour les juges."""
    nom = CLES[0][1]
    for j, s in CLES:
        if jour_de_l_annee >= j:
            nom = s
    return nom


def pour_le_navigateur() -> dict:
    return {"paliers": PALIERS, "cles": [[j, s] for j, s in CLES], "palettes": PALETTES,
            "lumiere": LUMIERE, "annee": calendrier.ANNEE}
