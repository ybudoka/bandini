"""Les montagnes et les falaises : la carte a une limite, et elle se voit.

Demande de Martin (21 sept. 2026) : « ajoute des falaises et montagnes
infranchissable pour délimiter les endroits strategique ». Deux questions
tranchées avec lui avant de coder : le relief délimite des zones PRÉCISES (pas
tout le pourtour), et sert à la fois de bordure de carte et de renfort autour
de l'aéroport — voir docs/jalons/les-montagnes-et-les-falaises-infranchissables.md.

⚠️ **On n'agrandit pas la trame.** Le chenal du 17 sept. 2026 l'a montré :
changer une rangée ou une colonne de `COLONNES`/`RANGEES`/`RUES_V`/`RUES_H`
re-tire toute la ville (26 juges sans rapport tombés d'un coup). Le relief se
pose comme l'aéroport et l'Île-aux-Corneilles : en AJOUTANT au bord de la
carte finie, jamais en la redessinant.

⚠️ **Est et sud seulement.** Ajouter des colonnes après la dernière rue (à
l'est) ne décale aucune coordonnée déjà posée — exactement le principe qui a
permis à l'aéroport d'ajouter des rangées après la dernière rue (au sud).
Ajouter au nord ou à l'ouest décalerait TOUT ce qui a un x, y dans la ville
entière : un chantier à part, pas celui-ci.

⚠️ **Posé après l'aéroport, en tout dernier dans `generer`, sans un dé** :
rien de la ville d'aujourd'hui, aéroport compris, ne bouge d'une tuile — sauf
l'eau du large, au sud de lui, que la ligne de falaises recouvre EXPRÈS.

Deux morceaux :

1. `_agrandir_a_l_est` : une chaîne de montagnes ajoutée après la dernière
   colonne de la trame — une paroi de FALAISE en bordure (ce qu'on voit
   depuis la ville), puis de la MONTAGNE pleine jusqu'au bord de la carte.
2. `_falaises_du_large` : au sud de l'aéroport, le « large » est de l'eau à
   perte de vue depuis le 21 sept. — une ligne de falaises EN PLACE (elle ne
   fait pas grandir la carte) lui donne une limite. Elle ne touche jamais que
   des tuiles d'eau (`~`) : elle s'arrête net à la première tuile qui n'en est
   pas, colonne par colonne — jamais un pied de fence, une plage ou un
   bâtiment de l'aéroport.
"""

from __future__ import annotations

#: La largeur de la chaîne de montagnes, à l'est. ⚠️ Assez large pour remplir
#: l'écran (480 px = 30 tuiles) une fois collé dessus : un mur d'un ou deux
#: tuiles se voit comme un mur peint, pas comme une chaîne de montagnes.
LARGEUR_MONTAGNES = 40
#: L'épaisseur de la paroi de falaise, côté ville — le reste est de la montagne.
EPAISSEUR_FALAISE_EST = 2

#: La profondeur maximale (en tuiles) de la bande de falaises au sud du
#: large — une par colonne, jamais plus loin que la première tuile qui n'est
#: pas de l'eau.
PROFONDEUR_FALAISES_SUD = 8


def poser(chantier, ville: dict) -> dict:
    """Pose le relief. Rend sa fiche pour le paquet (`ville["relief"]`)."""
    est = _agrandir_a_l_est(chantier, ville)
    # ⚠️ Sans aéroport, pas de large : les falaises du sud n'existent que dans
    # l'eau QU'IL a ajoutée (`masque.carte_h`, la hauteur de la carte d'avant
    # lui). Sans cette borne, la bande de huit tuiles se poserait sur la vraie
    # baie — un quartier qu'on joue, pas de l'eau à perte de vue.
    aeroport = ville.get("aeroport")
    if aeroport:
        _falaises_du_large(chantier, ville, aeroport["masque"]["carte_h"])
    return {"montagnes": est}


def _agrandir_a_l_est(chantier, ville: dict) -> dict:
    """La chaîne de montagnes : des colonnes ajoutées après la dernière rue,
    sur toute la hauteur de la carte (l'aéroport compris, posé avant nous)."""
    x0 = chantier.largeur
    paroi = "C" * EPAISSEUR_FALAISE_EST + "M" * (LARGEUR_MONTAGNES - EPAISSEUR_FALAISE_EST)
    for ligne in chantier.sol:
        ligne.extend(paroi)
    for ligne in chantier.voie:
        ligne.extend("." * LARGEUR_MONTAGNES)
    for ligne in chantier.bouchon:
        ligne.extend("B" * LARGEUR_MONTAGNES)
    chantier.largeur = x0 + LARGEUR_MONTAGNES
    ville["largeur"] = chantier.largeur
    ville["sol"] = ["".join(ligne) for ligne in chantier.sol]
    ville["voie"] = ["".join(ligne) for ligne in chantier.voie]
    return {"x": x0, "y": 0, "l": LARGEUR_MONTAGNES, "h": chantier.hauteur}


def _falaises_du_large(chantier, ville: dict, y_min: int) -> None:
    """Une ligne de falaises au bord sud de la carte, colonne par colonne :
    elle ne recouvre que de l'eau, et s'arrête à la première tuile qui n'en
    est pas — jamais l'aéroport, sa clôture, sa grève, ni une rangée plus
    haute que `y_min` (la vraie baie, celle qu'on joue)."""
    largeur, hauteur = chantier.largeur, chantier.hauteur
    for x in range(largeur):
        y, profondeur = hauteur - 1, 0
        while profondeur < PROFONDEUR_FALAISES_SUD and y >= y_min and chantier.sol[y][x] == "~":
            y -= 1
            profondeur += 1
        if profondeur == 0:
            continue
        haut = y + 1
        chantier.sol[haut][x] = "C"
        for yy in range(haut + 1, hauteur):
            chantier.sol[yy][x] = "M"
    ville["sol"] = ["".join(ligne) for ligne in chantier.sol]
