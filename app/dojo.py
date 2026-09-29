"""Le dojo du quartier : les regles de la lecon et ce que Mireille dit
(docs/jalons/le-dojo-du-quartier.md). Python decide, `dojo.js` joue.

Mireille Dion tient le DOJO DION, au Faubourg : ancienne danseuse contemporaine,
venue a l'aikido puis au jiu-jitsu. Une technique s'apprend quand on la place trois fois
sur Kevin, l'eleve partenaire — A SON RYTHME : ni metronome, ni fenetre, ni echec
(docs/jalons/le-dojo-apprendre-a-son-rythme.md). Sa fiche : `docs/personnages/mireille.md`.
"""

from __future__ import annotations

from . import techniques

#: Le dojo ouvre de 8 h a 22 h (fractions du jour, comme `magasins.HEURES_DES_COMPTOIRS`).
#: ⚠️ La nuit, c'est le MENU qui ferme, pas la porte — comme tous les comptoirs du jeu.
HEURES = (8 / 24, 22 / 24)
#: ⚠️ PLUS DE METRONOME (Martin, 29 sept. : « change comment on apprend ces techniques, c'est
#: trop dur ») : le « et » de 0,4 s (26 sept.), puis de 0,6 s (28 sept.), et Bandini ramene sur sa
#: marque (29 sept.) n'y ont rien fait — c'etait le principe. Une reussite, c'est la technique
#: enseignee qui PORTE sur Kevin, quand on veut ; trois, et elle est apprise. Aucun echec : un
#: geste qui ne porte pas, Mireille le dit (« tu danses tout seul »), et on recommence.
REUSSITES = 3
#: Apres un essai, le temps de souffler (0,75 s) avant que Kevin et Bandini reprennent leur marque
#: — si Bandini ne bouge plus : on ne tire personne en pleine course.
REMISE_IMAGES = 45
#: La parade (le retournement du poignet) : Kevin arme un coup toutes les 2 s, et le TIENT arme
#: 0,75 s, avec un cri. ⚠️ Le coup de rue n'arme que 5 images (0,08 s) : c'etait le vrai mur de
#: cette lecon-la, rythme ou pas.
CADENCE_ARME = 120
ANTICIPATION_KEVIN = 45
#: Ou Kevin se tient, en pixels devant Bandini, selon la mise en place (`techniques.lecon`).
#: ⚠️ Au contact, c'est 12 : deux corps ne s'approchent jamais sous 10 px (`Entites.demeler`).
DISTANCES = {"contact": 12, "dos": 11, "arme": 12, "loin": 70, "attaque": 40}
#: La mise en place de chaque cours, quand ce n'est pas « au contact » : Kevin de dos pour
#: l'etranglement, qui arme un coup pour la parade, plus loin pour le coup saute (l'elan),
#: qui attaque pour le balayage (la roulade). ⚠️ Ici, et pas un champ sur chaque technique :
#: seize fois « contact » dans le paquet coutaient plus que ces quatre lignes.
LECONS = {"etranglement": "dos", "retournement_poignet": "arme", "pied_saute": "loin",
          "balayage": "attaque"}


def lecon(slug: str) -> str:
    return LECONS.get(slug, "contact")

#: Ce que dit chaque cours, en l'annonçant. Sur mesure : une annonce generique (« X. Regarde,
#: puis fais-le avec moi. ») disait dix fois la meme chose avec un autre nom devant.
ANNONCES = {
    "uppercut": "L'uppercut. Tu plies les genoux, tu remontes avec tout le corps. Pas juste le bras.",
    "pied_circulaire": "Le coup de pied circulaire. La hanche tourne d'abord. La jambe suit.",
    "pied_de_cote": "Le coup de pied de côté. Tu charges, tu gardes… et tu pousses le mur.",
    "pied_saute": "Le coup de pied sauté. Tu cours, tu montes, et tu ne penses pas à la descente.",
    "balayage": "Le balayage. Tu roules, tu restes bas, et tu fauches ce qui tient debout.",
    "projection_hanche": "La projection de hanche. Tu le colles, tu tournes. Ta hanche fait le reste.",
    "grand_fauchage": "Le grand fauchage. Tu le tires vers toi, et ta jambe balaie la sienne.",
    "sacrifice": "Le sacrifice en cercle. Tu te laisses tomber. Oui, exprès. Ton pied fait voler le reste.",
    "retournement_poignet": "Le retournement du poignet. Il frappe, tu accueilles, tu tournes.",
    "etranglement": "L'étranglement. Par derrière, sans bruit. Et tu tiens jusqu'au bout.",
}

#: Ce que Mireille dit, par cle. Le slug de la voix est `mireille-dojo-<cle>` ; le jeu d'acteur
#: est dans `interpretation.JEU` (`test_interpretation`). ⚠️ Elle se nomme UNE fois, dans sa
#: salutation (« Qui parle se nomme ») — un juge le tient.
REPLIQUES: list[dict] = [
    {"cle": "salut", "texte": "Bonjour. Mireille Dion. Tu enlèves tes souliers, tu salues le tatami, et après on parle."},
    {"cle": "cours", "texte": "Choisis. Moi, je fournis le geste et le rythme. Toi, la sueur."},
    {"cle": "oui_1", "texte": "Oui."},
    {"cle": "oui_2", "texte": "C'est ça."},
    {"cle": "dans_le_vide", "texte": "Tu danses tout seul."},
    {"cle": "appris", "texte": "Tu l'as. Garde-le propre."},
    {"cle": "abandon", "texte": "On arrête. Salue le tatami en sortant."},
    {"cle": "ferme", "texte": "Le dojo dort. Reviens à huit heures."},
] + [{"cle": f"annonce_{t['slug']}", "texte": ANNONCES[t["slug"]]}
     for t in techniques.CATALOGUE if not t["gratuite"]]


def repliques() -> list[dict]:
    """Les voix du dojo, rangees ensemble (`mission: "dojo"`) : le navigateur les charge d'un
    coup (`Son.Voix.chargerHistoire('dojo')`)."""
    return [{"slug": f"mireille-dojo-{r['cle']}", "qui": "mireille", "texte": r["texte"],
             "mission": "dojo", "partie": "dojo", "telephone": False} for r in REPLIQUES]


#: Les repliques qui s'AFFICHENT (une boite de dialogue, avec son visage) : les autres — les
#: « oui », le geste dans le vide, les annonces — ne font que se DIRE ; l'ecran les montre
#: par le compteur de la lecon et le nom de la technique.
#: ⚠️ Le paquet des definitions est a son plafond (54 000 octets gzip, `test_definitions`) :
#: les vingt-cinq textes le depassaient de 638 octets. Ce qui se dit sans s'afficher reste ici.
AFFICHEES = ("salut", "appris")


def exporter() -> dict:
    return {"heures": list(HEURES), "reussites": REUSSITES, "remise_images": REMISE_IMAGES,
            "cadence_arme": CADENCE_ARME, "anticipation_kevin": ANTICIPATION_KEVIN,
            "distances": DISTANCES, "lecons": LECONS,
            "repliques": {r["cle"]: r["texte"] for r in REPLIQUES if r["cle"] in AFFICHEES}}
