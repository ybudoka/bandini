"""La lecture des passants (`docs/jalons/la-reputation-et-la-lecture-des-passants.md`, vague 1).

Tranché par Martin le 1er oct. 2026 : on TIENT un bouton (LIRE : la gâchette de gauche à pied, Y au
clavier) en regardant un passant, et une ligne s'affiche au-dessus de lui — ce qu'il est, ce qu'il doit,
ce qu'il cache. Le profilage de Watch Dogs, à la mode de Baie-des-Brumes.

⚠️ **UNE LIGNE, C'EST DE LA COULEUR, PAS UN FIL À TIRER.** Aucune mission ne la lit, rien ne s'y enchaîne,
lire ne coûte rien et ne rapporte rien : si elle se mettait à donner, elle deviendrait le cent-et-unième
type d'objectif que M16 interdit. `Lecture` (le module) est autonome, branché dans `Jeu.maj`, jamais dans
`BOULOTS` (juge `test_lectures`).

⚠️ **UN ENFANT NE SE LIT PAS.** Pas de profil sur un gosse : `Lecture.lisible` refuse tout intouchable et
tout corps d'enfant, quoi que dise cette table.

⚠️ **RIEN AU DÉ.** Un passant lit la ligne que son identifiant désigne dans le lot de son quartier
(`hash2`, à l'empreinte), jamais `B.rng()` : un dé de plus par lecture décalerait tout le hasard de la
ville. Il la garde ensuite (`e.lecture`) : il ne change pas d'histoire en traversant une rue.

Les lignes suivent `docs/ecrire-drole.md` : un fait, puis la chute, le mot fort à la fin ; on frappe en
haut (Sal, Prévost, les gangs), jamais les pauvres. Elles tiennent en deux rangées de `LARGEUR_RANGEE`
caractères au-dessus d'une tête (juge `test_lectures`). Un quartier sans lot ne se lit pas (la baie, un
bloc) : on tient le bouton et rien ne vient, ce qui est juste — personne n'a rien à dire.
"""

from __future__ import annotations

#: Une rangée de la fiche, en caractères (quatre pixels chacun) : deux rangées au plus par ligne.
LARGEUR_RANGEE = 30

#: Le lot de chaque quartier. ⚠️ La clé est le `district` d'une zone de la carte (`carte.exporter`).
LIGNES: dict[str, tuple[str, ...]] = {
    "faubourg": (
        "Doit 200 $ à Sal. A les cheveux très courts.",
        "A gagné 10 $ au 6/49. L'a dit à tout le monde.",
        "Fait les mots croisés du Clairon. Triche.",
        "Habitué du Brouillard. Sa chaise porte son nom.",
        "A prêté 20 $ à Rocco en 1998. Y croit encore.",
        "Porte une cravate. N'est pas un Cravate. Le répète.",
        "Attend l'autobus depuis 1994. Optimiste.",
        "A laissé ses clés dans le char. Cherche le char.",
        "Se dit ami de Mme Thibodeau. Elle, non.",
    ),
    "erables": (
        "A déjà retrouvé Biscuit. Le raconte à chaque souper.",
        "Tond son gazon deux fois par jour. Le voisin aussi.",
        "Achète ses billets chez Ti-Paul. Jamais gagné. Fidèle.",
        "Président du comité des boîtes aux lettres.",
        "A mesuré la haie du voisin. Deux pouces de trop.",
        "Son fils est un Chevreuil. Pense qu'il joue au hockey.",
        "Pose ses lumières de Noël en août. Prévoyant.",
        "Lave son char le samedi. Le dimanche, le regarde.",
    ),
    "shop": (
        "Trente ans chez Prévost. A eu une montre. Elle retarde.",
        "Sort son char de la fourrière. Chaque lundi.",
        "A racheté son pare-chocs à Ti-Loup. Deux fois.",
        "Syndiqué. A une opinion. A plusieurs opinions.",
        "Sent l'huile à moteur. Trouve que ça sent bon.",
        "Boulonneux la nuit, comptable le jour. Déclare tout.",
        "Dîne sur le même tas de pneus depuis 1991.",
        "Fait signer une pétition contre le bruit. Crie.",
    ),
    "quais": (
        "Pêche sur le quai depuis 6 h. A pris un soulier.",
        "Jure que la poutine de Lulu guérit le rhume.",
        "Rate le traversier tous les matins. Exprès.",
        "Débardeur. A déjà levé un char. Pas le sien.",
        "Parle aux goélands. Ils répondent.",
        "Sent la morue. N'est pas un Morue. C'est le métier.",
        "Dit qu'il a déjà navigué. Le pédalo compte.",
        "Attend un colis du porte-conteneurs. Depuis mars.",
    ),
    "pointe": (
        "Fait du skate depuis vingt ans. Maîtrise l'arrêt.",
        "Salue le phare tous les soirs. Le phare, non.",
        "A vu un orignal sur la plage. A une photo floue.",
        "Écrit un roman sur la mer. Page 3 depuis 2011.",
        "Ramasse les consignes sur la grève. A un REER.",
        "Ancien Skateux. A gardé la casquette, pas les genoux.",
        "Annonce la météo d'après les goélands. A raison.",
        "A un chalet à La Pointe. C'est une tente.",
    ),
    "canton": (
        "Joue au Dragon d'or. Gagne le jeudi. Perd le reste.",
        "Élève de Sifu Tam. Ceinture blanche. Depuis 2009.",
        "Doit de l'argent au Pouce. Content qu'il soit à Sorel.",
        "Fait le meilleur bouillon du Canton. Le dit lui-même.",
        "Mante à la retraite. Fait du tai-chi, menaçant.",
        "A compté les lanternes de l'arche. Il en manque une.",
        "Joue au mah-jong avec sa tante. Perd. Elle triche.",
        "Regarde les machines à sous comme d'autres la télé.",
    ),
    "gare": (
        "Compte les wagons qui passent. En est à 40 112.",
        "A pris le train une fois. Pour Montréal. Est revenu.",
        "Aiguilleur. A déjà envoyé un train à Gaspé. Exprès.",
        "Vit à côté des rails. Ne s'entend plus penser. Préfère.",
        "Attend le train de 17 h 12. Il arrive à 17 h 40.",
        "Graffeur. Signe ses wagons. Les voit revenir de Winnipeg.",
        "Chef de triage. Trie aussi ses bas, par couleur.",
        "A posé une cenne sur les rails en 1979. La cherche.",
    ),
    "friches": (
        "Fait du 4 roues. Celui de son beau-frère. En cachette.",
        "Cherche des champignons. Trouve des pneus.",
        "Va se bâtir un chalet ici. Depuis 2003.",
    ),
    "ile": (
        "Chante à la chapelle le vendredi. Faux. Avec cœur.",
        "Compte les corneilles. Elles le comptent aussi.",
        "Sait pas ce qu'il y a dans le hangar de Léo. Préfère.",
    ),
    "aeroport": (
        "Attend son vol depuis hier. A lu son livre. Deux fois.",
        "A peur de l'avion. Vient voir les autres partir.",
        "Revient de Floride. Bronzé d'un seul bras.",
    ),
}

#: Le geste. `portee_px` : jusqu'où on lit ; `cone_deg` : de combien on peut regarder à côté (de chaque
#: côté du regard) ; `garde_px` : la cible déjà lue tient jusque-là tant qu'on tient le bouton, même hors
#: du cône — une fiche qui saute d'une tête à l'autre au moindre pas ne se lit pas.
REGLE: dict[str, float] = {"portee_px": 120, "cone_deg": 40, "garde_px": 160}


def exporter() -> dict:
    return {"lignes": {q: list(lot) for q, lot in LIGNES.items()}, "regle": dict(REGLE),
            "largeur_rangee": LARGEUR_RANGEE}
