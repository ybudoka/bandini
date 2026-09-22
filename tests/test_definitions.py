import gzip
import json

from app import definitions


def test_le_paquet_est_deterministe():
    a, b = definitions.construire(), definitions.construire()
    for nom in ("definitions", "carte"):
        assert getattr(a, nom).corps == getattr(b, nom).corps, nom
        assert getattr(a, nom).etag == getattr(b, nom).etag, nom
        assert len(getattr(a, nom).etag) == 16, nom


def test_le_paquet_reste_leger():
    """⚠️ Budget releve a 600 Ko bruts le 13 sept. 2026 (demande de Martin).

    Mesure du 13 sept. 2026 : 370 Ko bruts / 43 Ko gzip, dont 306 Ko de carte
    pour 89 673 tuiles — et la carte ne pese que 26 Ko sur le fil, parce que
    `sol` et `voie` sont des suites de glyphes que gzip adore.

    Le brut n'est qu'un INDICATEUR : ce qui coute, c'est le gzip qui voyage
    et le temps de JSON.parse sur le telephone. Le plafond de 400 Ko etait a
    30 Ko d'etre touche par n'importe quel ajout ; il ne mesurait plus rien.
    Le gzip garde ses 70 Ko, et c'est lui le juge. Si le fil deborde, la
    carte sort du paquet (`/api/carte`, districts charges autour du joueur)
    — pas avant : personne n'a encore prouve le besoin de cette machinerie.
    Et ce qui n'est pas de la geographie (les dialogues de M16) n'entre pas
    ici du tout : une requete par mission, quand le telephone sonne.

    ⚠️ **Releve a 75 Ko gzip le 16 sept. 2026** (le petit train et la montagne
    russe de la foire). Mesure : 67 898 octets avant, 71 417 apres — dont
    2 667 pour la voie de la montagne russe, 407 points (x, y, z). Exportee en
    pixels ENTIERS (le dessin arrondit de toute facon), elle tombe a 1 975, et
    le paquet a 70 690 : sept cents octets au-dessus d'un plafond qui n'en
    laissait plus que deux mille a la ville entiere. Cinq Ko de plus, c'est
    une image de kiosque sur le fil, une fois, puis le cache de l'empreinte.
    Le remede du debordement reste celui d'au-dessus — la carte sort du paquet
    —, et c'est a ce plafond-ci qu'on le prendra.

    ⚠️ **LA CARTE EST SORTIE DU PAQUET le 16 sept. 2026** — decision de Martin,
    et c'est ce plafond-ci qui l'a demandee : avec L'Ile-aux-Corneilles, le paquet
    passait a 75 307 octets gzip (la ville seule 74 472, l'ile 835). Mesure au
    decoupage : les definitions 32 975 octets gzip (140 Ko bruts), la carte
    41 269 (374 Ko bruts). Chacune a desormais SON plafond.

    ⚠️ **Ce que le decoupage n'achete pas, et il faut le dire** : au premier
    chargement, le telephone recoit a peu pres autant d'octets qu'avant, en deux
    requetes paralleles au lieu d'une. Ce qu'il achete : un deploiement qui ne
    touche que les catalogues revalide la carte par un 304 (et l'inverse), deux
    `JSON.parse` plus petits, et un budget par sujet — la carte ne mange plus la
    marge des missions. Le vrai remede au poids du demarrage reste la dette des
    districts charges autour du joueur, avec son declencheur (« Dettes »).

    ⚠️ **La carte : 48 000 → 50 000 octets gzip le 21 sept. 2026.** Mesure : elle
    pesait 47 999 octets — UN de moins que le plafond, sans que personne y ait
    pense —, et le cabriolet rose (son nom dans les `rares` de deux districts et
    de leurs cours de gang) en a ajoute 13. Ce n'est pas le cabriolet qui a
    rempli la carte, c'est que le plafond n'avait plus de marge : le prochain
    ajout, quel qu'il soit, l'aurait fait tomber. Deux Ko de marge, et la meme
    regle qu'avant : le vrai juge du poids est le declencheur de la dette
    (« plus de 2 s entre Jouer et la ville »), pas ce nombre.

    ⚠️ **Les définitions : 40 000 → 44 000 octets gzip le 21 sept. 2026.** Mesure : huit missions
    pesaient 39 526 octets (474 sous le plafond), treize en pèsent 41 886 — **470 octets par mission**
    (objectifs, répliques, scènes : tout le catalogue voyage dans le paquet). Quatre mille de marge
    font place à quatre missions de plus ; ce n'est pas un droit d'en écrire cent. Le remède est
    écrit depuis le 16 sept. dans la fiche de M16 : les dialogues et les scènes sortent du paquet
    (`/api/dialogue/<slug>`, ETag), et le catalogue seul y reste. Il n'est pas livré ; ce plafond-ci
    est ce qui le rendra urgent. ⚠️ Le JEU des répliques (`jeu=`) n'y voyage PAS
    (`missions.pour_le_navigateur`) : il ne sert qu'à générer les voix.

    ⚠️ **La carte : 50 000 → 53 000 octets gzip, 450 000 → 520 000 bruts, le 21 sept. 2026**
    — l'aéroport (demande de Martin : « aggrandit la carte au sud »). Mesure : 48 282 → 50 331
    octets gzip, 409 780 → 483 244 bruts. Les 80 rangées que la carte gagne au sud font
    presque tout le brut (deux calques de 419 glyphes chacune) et presque rien sur le fil (de
    l'eau, que gzip avale) ; l'île dessinée et sa fiche font les deux Ko du fil (la fiche seule :
    454 octets). Une carte plus grande pèse plus : c'est le prix de la demande, pas une fuite.
    """
    paquets = definitions.construire()
    for nom, brut_max, fil_max in (("definitions", 200_000, 44_000), ("carte", 520_000, 53_000)):
        paquet = getattr(paquets, nom)
        assert paquet.taille < brut_max, f"{nom} : {paquet.taille} octets, le paquet enfle"
        sur_le_fil = len(gzip.compress(paquet.corps, 6))
        assert sur_le_fil < fil_max, f"{nom} : {sur_le_fil} octets gzip, le telephone va sentir passer"


def test_l_empreinte_change_avec_le_contenu(monkeypatch):
    avant = definitions.construire()
    monkeypatch.setattr(definitions.economie, "ARGENT_DEPART", 51)
    apres = definitions.construire()
    assert apres.definitions.etag != avant.definitions.etag
    assert apres.carte.etag == avant.carte.etag, "un catalogue qui change ne doit pas faire retelecharger la ville"


def test_l_empreinte_des_definitions_suit_la_carte(monkeypatch):
    """⚠️ La sauvegarde oublie une position quand `empreinte` change
    (`Jeu.demarrer`). Depuis que la carte voyage a part, ce n'est vrai que parce
    que les definitions portent l'empreinte de leur carte : une ville redessinee
    sans qu'un seul catalogue bouge doit quand meme faire oublier la position."""
    from app import carte

    avant = definitions.construire()
    monkeypatch.setattr(carte, "GRAINE", carte.GRAINE + 1)
    monkeypatch.setattr(carte.generer, "__defaults__", (carte.PLAN, carte.GRAINE))
    apres = definitions.construire()
    assert apres.carte.etag != avant.carte.etag, "la carte n'a pas change : le juge ne mesure rien"
    assert apres.definitions.etag != avant.definitions.etag, "la carte a change et la sauvegarde ne le saura pas"


def test_le_paquet_contient_tout(paquet):
    for cle in ("version", "empreinte", "tuile_px", "vehicules", "armes", "ordre_armes", "economie",
                "recherche", "carte", "missions", "defis", "types_objectifs", "magasins", "tenues"):
        assert cle in paquet, cle
    assert json.dumps(paquet)  # serialisable


def test_la_carte_voyage_a_part_et_se_reconnait():
    """Les definitions ne portent plus la carte, seulement son empreinte ; la
    carte porte la sienne, et c'est la meme. C'est ce que le navigateur verifie
    avant de les remettre ensemble."""
    paquets = definitions.construire()
    defs = json.loads(paquets.definitions.corps)
    carte = json.loads(paquets.carte.corps)
    assert "carte" not in defs, "la carte est encore dans le paquet"
    assert defs["carte_empreinte"] == carte["empreinte"] == paquets.carte.etag
    assert defs["empreinte"] == paquets.definitions.etag
    assert carte["largeur"] > 0 and carte["sol"]
