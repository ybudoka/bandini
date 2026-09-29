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
#: tirées à l'empreinte de sa tuile ; `feuillage` 0 = nu), `neige` : la part de blanc sur les
#: trottoirs et les toits, `mini` : l'herbe sur la mini-carte (l'été, le vert d'avant), et `froid` : ce que
#: les passants sentent (0 juillet, 1 janvier ; lot 4a, `HABITS`) — il glisse en paliers comme le reste.
PALETTES = {
    "ete": {
        "froid": 0,
        "mini": "#3f6b33",
        "gazon": {"fond": "#4f8d3e", "clair": "#5a9c47", "sombre": "#427a33", "brin": "#6aad55",
                  "terre": "#6d5c3e", "fleur": "#cfc95c", "feuille": "#4f8d3e", "feuille2": "#4f8d3e"},
        "friche": {"fond": "#6d6845", "clair": "#7b7551", "sombre": "#5b5638", "sec": "#a4975f"},
        "arbre": {"teintes": [["#2f6b2a", "#3f8d38", "#204d1e"], ["#2a6330", "#3a8440", "#1d4722"],
                              ["#356f27", "#468f35", "#25501b"]], "feuillage": 1, "neige": 0},
        "neige": 0,
    },
    "printemps": {
        "froid": 0.45,
        "mini": "#4d7f3a",
        "gazon": {"fond": "#5f9a45", "clair": "#74b057", "sombre": "#4d8438", "brin": "#8cc46a",
                  "terre": "#6a5536", "fleur": "#e8d85a", "feuille": "#5f9a45", "feuille2": "#5f9a45"},
        "friche": {"fond": "#6a6a44", "clair": "#787a50", "sombre": "#585a37", "sec": "#9a9a60"},
        "arbre": {"teintes": [["#4f8f3a", "#6fb050", "#3a7029"], ["#5a9a40", "#7cbc58", "#437a2e"],
                              ["#6aa048", "#8cc466", "#4e8034"]], "feuillage": 0.8, "neige": 0},
        "neige": 0,
    },
    "fin_ete": {
        "froid": 0.1,
        "mini": "#61703a",
        "gazon": {"fond": "#7a8c42", "clair": "#8f9c4f", "sombre": "#667838", "brin": "#a3a85c",
                  "terre": "#7a6443", "fleur": "#d9b24a", "feuille": "#7a8c42", "feuille2": "#7a8c42"},
        "friche": {"fond": "#7d7546", "clair": "#8b8252", "sombre": "#6a6339", "sec": "#b5a462"},
        "arbre": {"teintes": [["#4a6b2a", "#5f8436", "#34501e"], ["#2f6b2a", "#3f8d38", "#204d1e"],
                              ["#6b7a2a", "#869536", "#4f5c1e"]], "feuillage": 1, "neige": 0},
        "neige": 0,
    },
    "automne": {
        "froid": 0.4,
        "mini": "#8a5a2a",
        "gazon": {"fond": "#6f7a3c", "clair": "#7f8646", "sombre": "#5c6632", "brin": "#8e8a4c",
                  "terre": "#6d5536", "fleur": "#c8622a", "feuille": "#c0392b", "feuille2": "#e67e22"},
        "friche": {"fond": "#76663f", "clair": "#86744a", "sombre": "#625434", "sec": "#b08850"},
        "arbre": {"teintes": [["#b8321f", "#d9502e", "#7f2416"], ["#d9731f", "#f09a3a", "#9a4f14"],
                              ["#d4a91c", "#efcb3e", "#9a7a12"]], "feuillage": 0.95, "neige": 0},
        "neige": 0,
    },
    "novembre": {
        "froid": 0.65,
        "mini": "#56533a",
        "gazon": {"fond": "#6b6a45", "clair": "#77744f", "sombre": "#57553a", "brin": "#83805a",
                  "terre": "#5e4a32", "fleur": "#8a5a34", "feuille": "#8a5a34", "feuille2": "#7a4a2a"},
        "friche": {"fond": "#6a5f42", "clair": "#776b4c", "sombre": "#574e36", "sec": "#948058"},
        "arbre": {"teintes": [["#7a4a26", "#94603a", "#5a361c"], ["#8a5a2e", "#a67040", "#643f20"],
                              ["#6e5a34", "#8a7244", "#4f4024"]], "feuillage": 0.3, "neige": 0},
        "neige": 0,
    },
    "hiver": {
        "froid": 1,
        "mini": "#d6dde4",
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


#: L'HABIT DU MOMENT (lot 4a, `Saisons.vetir`) : la tenue TIRÉE ne change pas, c'est l'image qui
#: s'habille. Le froid qu'un passant sent = `froid` de la palette + (frileux − ½) × `ecart` (frileux : à
#: l'empreinte de sa tenue, jamais au dé). Au-dessus de `grand_froid` : manteau, bottes, tuque (et le
#: foulard des plus frileux) ; au-dessus de `frais` : plus de t-shirt ni de short ; sous `chaud` : l'été.
#: Les personnages et le joueur (vague 4c, Martin : « il change juste à l'extérieur ») s'habillent aussi,
#: DEHORS seulement et du côté du froid seulement : manteau et tuque dans LEUR palette (leur haut, leur
#: bas) — leur tenue de tous les jours est leur tenue d'été. Dedans, rien ne change pour personne.
HABITS = {
    "ecart": 0.3, "grand_froid": 0.75, "frais": 0.4, "chaud": 0.2,
    #: Ce qu'on garde au grand froid : un chapeau qui tient déjà chaud ou qui dit un métier.
    "chapeaux_chauds": ["tuque", "kepi", "casque_chantier", "feutre", "marin", "capuche"],
    #: Les archétypes dont le chapeau est un UNIFORME : on ne le change jamais.
    "chapeau_d_uniforme": ["policier", "garde", "gardien", "livreur", "mante"],
    #: Les hauts qui restent en toute saison : un métier (le tablier, le sarrau…) ou un gang.
    "hauts_de_metier": ["tablier", "sarrau", "veste_travail", "veste_kungfu", "salopette"],
    #: Sous la pluie (`Pluie.intensite()` au-dessus de `seuil`) : `part` des passants ouvrent un
    #: parapluie ; les autres remontent leur capuche s'ils sont frileux.
    "parapluie": {"seuil": 0.15, "part": 0.5},
    #: LES MANTEAUX D'HIVER (vague 4c, Martin : « des manteaux d'hiver de vraies couleurs ») : au grand
    #: froid, `part` des passants enfilent un manteau foncé (à l'empreinte de leur tenue) ; les autres
    #: reprennent la couleur de leur haut. Jamais un gang ni un uniforme (leur couleur les fait
    #: reconnaître), jamais un personnage ni le joueur (leur palette).
    "manteaux": {"part": 0.65,
                 "couleurs": ["#1f2a44", "#16161c", "#5a1f2b", "#264232", "#4a3322", "#3b3f46",
                              "#2c3e5c", "#6a2a22", "#3d2f45", "#50452e"]},
    #: Les ENFANTS (vague 4c) : dessinés à la main, sans garde-robe — leur sprite a deux habits de plus
    #: (`SPRITES.enfant.saisons`) : les manches longues au frais, l'habit de neige, la tuque et les
    #: mitaines au grand froid. Les parents habillent tous les enfants le même jour : pas de frileux.
}


#: LA RUE DES SAISONS (lot 4b, `static/js/rue_des_saisons.js`) : ce qui se PEINT dans la ville selon la
#: palette, jamais posé (rien ne bouge, aucun dé). Tout se lit de la palette du moment (`neige`, `froid`) :
#: les morceaux cuits ne se repeignent qu'au palier, comme le gazon.
RUE = {
    #: Les bancs de neige, dans la rue au bord du trottoir, tant que la neige tient : `largeur` en pixels
    #: à pleine neige (0,7), `sale` la teinte de la fonte (la palette « hiver>… » : le dégel).
    "bancs": {"largeur": [3, 6], "neige": "#f2f5f8", "ombre": "#c3ccd6", "sale": "#8b8479"},
    #: Les abris Tempo, dans les entrées (`p`, le stationnement) à côté d'une maison, ou devant son
    #: rideau de garage : montés dès que le froid passe `froid_min` (novembre), démontés au dégel quand la
    #: neige qui tient passe sous `demonte_neige`.
    "tempo": {"froid_min": 0.5, "demonte_neige": 0.35, "part": 0.8, "toile": "#dfe4ea", "arceau": "#aeb8c3",
              "bord": "#6f7984", "ouverture": "#363b42"},
    #: La fumée des cheminées (`toits`, `cheminee`) : au-dessus de `froid_min`, une part `froid` des
    #: cheminées fume ; `bouffees`, `vie` (images), `monte`, `derive` (px) — la recette du chalet.
    "fumee": {"froid_min": 0.5, "bouffees": 7, "vie": 180, "monte": 60, "derive": 40, "rayon": 9},
    #: Les terrasses, sur le trottoir devant les restos et les bars (`genres`), sous `froid_max`.
    "terrasses": {"froid_max": 0.15, "genres": ["bouffe", "nuit"],
                  "parasols": [["#c0392b", "#f4efe6"], ["#2e7d4f", "#f4efe6"], ["#1f5f99", "#f4d35e"]]},
    #: LES BORNES-FONTAINES OUVERTES (vague 4c, Martin : « lâche-toi lousse ») : les jours de CHALEUR de
    #: l'été (froid sous `froid_max`, `part_jours` des jours, à l'empreinte du jour, jamais sous la pluie),
    #: de `heures[0]` à `heures[1]`, `part` des bornes crachent vers la rue (à l'empreinte de la borne et du
    #: jour) et `enfants` enfants courent dans l'eau autour. Tout est PEINT d'après `B.t` : ni entité, ni
    #: dé. `portee_px` : jusqu'où s'entend la boucle `borne_ete` (un lieu chargé à la demande).
    #: LE PANACHE (Martin, 30 sept. : « plus gros ») : il traverse la rue — il retombe à `traverse` de la
    #: chaussée passé le bord du trottoir, entre `jet_min_px` et `jet_px` de la borne ; il monte à `haut_px`
    #: au-dessus du sol et s'ouvre jusqu'à `large_px` de large où il retombe.
    "bornes": {"froid_max": 0.05, "part_jours": 0.6, "heures": [11, 19.5], "part": 0.15, "enfants": 3,
               "jet_px": 60, "jet_min_px": 24, "traverse": 0.85, "haut_px": 18, "large_px": 14,
               "portee_px": 260, "volume": 0.6,
               "chandails": ["#e74c3c", "#f1c40f", "#3498db", "#2ecc71", "#e67e22", "#9b59b6", "#ff6fa8",
                             "#1abc9c"],
               "maillots": ["#1f5f99", "#c0392b", "#2e7d4f", "#f39c12", "#16161c"]},
}


#: LE SON DES SAISONS (lot 5, `Saisons.majSon`) : l'ambiance de chaque palette (août sonne comme l'été,
#: novembre comme l'automne), son volume de base, ce qui la baisse (la nuit, la pluie, la tempête) et le
#: temps qu'elle met à glisser vers son volume (en secondes). Dedans : muette.
SON = {
    "ambiances": {"hiver": "saison_hiver", "printemps": "saison_printemps", "ete": "saison_ete",
                  "fin_ete": "saison_ete", "automne": "saison_automne", "novembre": "saison_automne"},
    "volume": 0.55, "nuit": 0.45, "sous_la_pluie": 0.3, "glisse_s": 2.0,
}


def palette_du_jour(jour_de_l_annee: float) -> str:
    """La palette qui TIENT ce jour-là (la clé précédente), sans le glissement — pour les juges."""
    nom = CLES[0][1]
    for j, s in CLES:
        if jour_de_l_annee >= j:
            nom = s
    return nom


def pour_le_navigateur() -> dict:
    return {"paliers": PALIERS, "cles": [[j, s] for j, s in CLES], "palettes": PALETTES,
            "lumiere": LUMIERE, "annee": calendrier.ANNEE, "habits": HABITS, "rue": RUE, "son": SON}
