"""La coop locale, sous Node : le deuxième joueur à la manette.

Découpé de `test_moteur_js.py` (vague D, 29 sept. 2026) : même banc, mêmes juges.
"""

import pytest


def test_la_coop_locale_bascule_un_deuxieme_joueur_a_la_manette(banc):
    """M14 : `Jeu.basculerCoop` fait naitre un DEUXIEME VRAI JOUEUR
    (`type: 'joueur'`, pas un pieton deguise — remaniement du 22 sept.,
    « 2 vrais joueurs »), mene par LA manette (`Entree.SOURCE2`) — le
    joueur 1, lui, ne repond plus qu'au clavier pendant ce temps
    (`Entree.debutImage`, `!B.coop` sur la branche manette). Un clavier, une
    manette : la manette ne bouge jamais le joueur 1, le clavier ne bouge jamais
    le deuxieme. Rebasculer efface le deuxieme joueur."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const avant = L.B.entites.length;
        L.Jeu.basculerCoop();
        const ouvert = { coop: !!L.B.coop, entites: L.B.entites.length,
                          type: L.B.coop.entite.type, coopFlag: L.B.coop.entite.coopJoueur2,
                          vivant: L.B.coop.entite.vivant };
        // ⚠️ La VITESSE, pas la position accumulee : pousser longtemps dans une
        // direction fixe peut buter sur un mur pres du spawn (essaye, et vu :
        // un juge qui pousse "vers l'est" pendant 200 images peut avancer de
        // 5 px a peine, coince, sans que la coop y soit pour rien). La
        // reponse immediate au stick/au clavier, elle, ne depend pas du decor.
        o.pad([1, 0]); o.frame(3);
        const e2VitesseManette = { vx: L.B.coop.entite.vx, vy: L.B.coop.entite.vy };
        const joueurVitesseManette = { vx: L.B.joueur.vx, vy: L.B.joueur.vy };
        o.pad(null); o.frame(2);
        // Le CLAVIER pousse, SEUL : aucune manette branchee.
        o.touche('KeyD'); o.frame(3);
        const joueurVitesseClavier = { vx: L.B.joueur.vx, vy: L.B.joueur.vy };
        const e2VitesseClavier = { vx: L.B.coop.entite.vx, vy: L.B.coop.entite.vy };
        o.relacher('KeyD');
        const e2 = L.B.coop.entite;
        L.Jeu.basculerCoop();
        // ⚠️ PAS une comparaison de COMPTE : la foule nait et meurt toute
        // seule pendant ces images, `L.B.entites.length` bouge pour
        // d'autres raisons. La seule preuve qui compte, c'est que CETTE
        // entite-la (`e2`, la reference gardee plus haut) a quitte le tableau.
        const ferme = { coop: L.B.coop, encore: L.B.entites.indexOf(e2) >= 0 };
        return { avant: avant, ouvert: ouvert, e2VitesseManette: e2VitesseManette,
                 joueurVitesseManette: joueurVitesseManette,
                 joueurVitesseClavier: joueurVitesseClavier, e2VitesseClavier: e2VitesseClavier,
                 ferme: ferme };
    }""")
    assert r["ouvert"] == {"coop": True, "entites": r["avant"] + 1, "type": "joueur",
                            "coopFlag": True, "vivant": True}
    assert r["e2VitesseManette"]["vx"] > 0.2, "la manette doit faire marcher le deuxieme joueur"
    assert r["joueurVitesseManette"] == {"vx": 0, "vy": 0}, "la manette a bouge le joueur 1"
    assert r["joueurVitesseClavier"]["vx"] > 0.5, "le clavier doit faire marcher le joueur 1"
    # ⚠️ Retour de Martin (22 sept., en testant) : le deuxieme joueur ne
    # courait pas a la meme vitesse que le premier — l'essai le menait par
    # `v.pieton` (la foule), pas `v.joueur_course`. Les deux passent
    # desormais par la MEME fonction (`Entites.majJoueur`). Le stick a
    # fond (mag=1) et le clavier (toujours a fond) doivent donner LA MEME
    # vitesse, au pouce pres.
    assert r["e2VitesseManette"]["vx"] == pytest.approx(r["joueurVitesseClavier"]["vx"], abs=0.05), (
        f"le deuxieme joueur court a {r['e2VitesseManette']['vx']:.2f} px/image, "
        f"le premier a {r['joueurVitesseClavier']['vx']:.2f} : meme manette a fond, meme vitesse attendue"
    )
    assert r["e2VitesseClavier"] == {"vx": 0, "vy": 0}, "le clavier a bouge le deuxieme joueur"
    assert r["ferme"] == {"coop": None, "encore": False}, "rebasculer efface le deuxieme joueur"


def test_la_coop_locale_ignore_les_boutons_de_la_manette_pour_le_joueur_1(banc):
    """Retour de Martin (22 sept., en testant) : « les frappes ne sont pas bien
    assignées au bon joueur » — c'était plus large que le stick (déjà isolé) :
    un BOUTON de la manette (ACTION, ATTAQUE, ESQUIVE…) ne doit jamais
    déclencher une action du joueur 1 pendant la coop, exactement comme son
    stick ne doit jamais le faire marcher. `bas()`/`neuf()` ignorent la
    manette pendant `B.coop`, pas seulement `debutImage`."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        L.Jeu.basculerCoop();
        // ACTION (0), ESQUIVE/ANNULER (1), ATTAQUE (2, 5), ARME (3, 4) : tous
        // les boutons de la manette, enfonces en meme temps.
        o.pad([0, 0], [1, 1, 1, 1, 1, 1]);
        // ⚠️ `Entree.debutImage()` directement, PAS `o.frame(1)` : un frame
        // complet appelle `Jeu.maj()`, qui finit par `Entree.videPresse()` —
        // `neuf()` retomberait a faux avant qu'on le lise, qu'il ait ete
        // ignore par la coop ou non. Ici on lit la couche d'entree seule,
        // juste apres le calcul, avant que quoi que ce soit ne la vide.
        L.Entree.debutImage();
        const pendant = { bas: L.Entree.bas('attaque'), neuf: L.Entree.neuf('action'),
                           esquive: L.Entree.bas('esquive'), arme: L.Entree.bas('arme') };
        o.pad(null);
        L.Jeu.basculerCoop();
        return { pendant: pendant };
    }""")
    assert r["pendant"] == {"bas": False, "neuf": False, "esquive": False, "arme": False}, (
        "un bouton de la manette a declenche une action du joueur 1 pendant la coop"
    )


def test_la_coop_locale_le_deuxieme_joueur_interagit_au_bouton_action(banc):
    """Demande de Martin (22 sept.) : « ajouter ACTION (interagir) » pour le
    deuxième joueur — les mêmes gestes de décor que le premier
    (`Interactions.utiliserSurLesGens`/`Betes`/`LeDecor`), au bouton ACTION de
    LA MANETTE (`Entree.neufManette`), jamais celui du clavier. ⚠️ Jugé PAR LE
    BOUTON (comme `test_interactions_js.py` : « la chaîne d'ACTION affame ce
    qui suit, un juge qui appelle la fonction ne voit pas le bouton cassé »),
    pas en appelant `Interactions.utiliserSurLeDecor` a la main."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        L.Jeu.basculerCoop();
        const e2 = L.B.coop.entite;
        // Vide les passants autour : quelqu'un devant la poubelle fausserait le juge.
        for (const q of L.Entites.autour(e2.x, e2.y, 60, function (v) { return v.type === 'pieton' && v !== e2; })) L.Entites.retirer(q);
        L.Entites.creer('decor', e2.x, e2.y - 12, { decor: 'poubelle', r: 5, solide: true, dessine: true });
        L.Entites.reindexerDecor(); L.Entites.indexer();
        L.Entites.regarder(e2, 0, -1);   // face au bac
        const avant = Object.keys(L.B.partie.fouilles).length;
        // Le bouton ACTION (0) de LA MANETTE — ni le stick, ni le clavier.
        o.pad([0, 0], [1]);
        o.frame(1);
        o.pad(null);
        const apres = Object.keys(L.B.partie.fouilles).length;
        L.Jeu.basculerCoop();
        return { avant: avant, apres: apres };
    }""")
    assert r["apres"] == r["avant"] + 1, "le bouton ACTION de la manette doit fouiller le bac pour le deuxieme joueur"


def test_la_coop_locale_les_deux_joueurs_ne_peuvent_pas_se_frapper(banc):
    """« Il ne faut pas qu'ils puissent se frapper mutuellement » (Martin, 22
    sept.) : la regle est ecrite dans `Entites.blesser`, au seul passage de
    toute blessure du jeu — un joueur ne blesse pas un joueur. ⚠️ Et c'est
    BIEN CETTE REGLE-LA qu'on juge, pas l'invincibilite de naissance : on
    attend qu'elle soit retombee, puis le meme coup venant d'un PASSANT
    porte, lui."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        L.Jeu.basculerCoop();
        const e2 = L.B.coop.entite;
        // L'invincibilite de naissance (60 images) doit etre retombee : sans
        // ca, le juge resterait vert meme sans la regle.
        for (let i = 0; i < 70; i++) o.frame(1);
        const invincible = e2.invincible;
        const vieAvant = e2.vie;
        const parLeJoueur = L.Entites.blesser(e2, 20, L.B.joueur, {});
        const vieApres = e2.vie;
        // Le meme coup, venu d'un passant : il porte. C'est la preuve que le
        // refus vient de la regle joueur-contre-joueur et de rien d'autre.
        const passant = L.Entites.creerPieton(e2.x + 40, e2.y, L.Entites.archetypeDeRue());
        const parUnPassant = L.Entites.blesser(e2, 20, passant, {});
        // Et dans l'autre sens : le deuxieme ne blesse pas le premier.
        const jAvant = L.B.joueur.vie;
        L.B.joueur.invincible = 0;
        const versLePremier = L.Entites.blesser(L.B.joueur, 20, e2, {});
        L.Jeu.basculerCoop();
        return { invincible: invincible, vieAvant: vieAvant, vieApres: vieApres,
                 parLeJoueur: parLeJoueur, parUnPassant: parUnPassant,
                 versLePremier: versLePremier, jAvant: jAvant, jApres: L.B.joueur.vie };
    }""")
    assert not r["invincible"], "l'invincibilite de naissance tient encore : le juge ne prouverait rien"
    assert r["parLeJoueur"] is False, "le joueur 1 a pu frapper le deuxieme"
    assert r["vieApres"] == r["vieAvant"], "le deuxieme joueur a perdu de la vie sous le coup du premier"
    assert r["parUnPassant"] is True, "un passant doit pouvoir le blesser, lui : sinon le juge ne mord pas"
    assert r["versLePremier"] is False, "le deuxieme joueur a pu frapper le premier"
    assert r["jApres"] == r["jAvant"], "le joueur 1 a perdu de la vie sous le coup du deuxieme"


def test_la_coop_locale_le_deuxieme_joueur_frappe_a_poings_nus(banc):
    """Demande de Martin (22 sept.) : « toutes les mêmes actions » — ATTAQUE
    fait frapper le deuxième joueur, ET SON COUP PORTE.

    ⚠️ C'est LA raison du remaniement « 2 vrais joueurs » : tant qu'il etait
    un `pieton`, son poing ne touchait jamais personne — `Combat.arcDeMelee`
    refuse pieton contre pieton (les passants ne se battent pas entre eux,
    sauf deux gangs). Un juge qui ne regardait que `etat === 'attaque'` restait
    vert pendant que rien n'arrivait : on mesure donc la VIE de la cible."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        L.Jeu.basculerCoop();
        const e2 = L.B.coop.entite;
        // Le banc plante la cible sous son nez, face a elle, et vide le reste :
        // un passant qui s'interpose prendrait le coup a sa place.
        for (const q of L.Entites.autour(e2.x, e2.y, 60, function (v) { return v.type === 'pieton'; })) L.Entites.retirer(q);
        const cible = L.Entites.creerPieton(e2.x + 9, e2.y, L.Entites.archetypeDeRue());
        cible.etat = 'fige';
        L.Entites.regarder(e2, 1, 0);
        L.Entites.indexer();
        const vieAvant = cible.vie;
        // ATTAQUE : bouton 2 (MANETTE_DEFAUT.attaque = [2, 5]).
        // ⚠️ ON PRESSE ET ON RELACHE — a poings nus (melee), le bouton TENU
        // charge un coup fort, et le coup ne part qu'au relacher
        // (`Combat.majGestes`). C'est desormais le meme geste que pour le
        // joueur 1 : le tenir sans jamais le lacher ne frappe personne.
        o.pad([0, 0], [0, 0, 1]);
        o.frame(1);
        const charge = e2.charge;
        o.pad(null);
        o.frame(1);
        const etat = e2.etat, arme = e2.arme;
        // Les trois temps du coup : anticipation, actif, repos.
        for (let i = 0; i < 20; i++) o.frame(1);
        L.Jeu.basculerCoop();
        return { etat: etat, arme: arme, charge: charge, vieAvant: vieAvant, vieApres: cible.vie,
                 assomme: cible.etat === 'assomme' };
    }""")
    assert r["charge"] >= 1, "le bouton tenu doit CHARGER le coup du deuxieme joueur"
    assert r["etat"] == "attaque", "ATTAQUE doit faire frapper le deuxieme joueur"
    assert r["arme"] == "poings", "le deuxieme joueur part a poings nus"
    assert r["vieApres"] < r["vieAvant"] or r["assomme"], (
        f"le coup du deuxieme joueur n'a rien fait : la cible est passee de {r['vieAvant']} "
        f"a {r['vieApres']} point(s) de vie"
    )


def test_la_coop_le_deuxieme_joueur_ne_passe_pas_les_portes(banc):
    """« Les 2 personnages doivent pouvoir faire toutes les mêmes actions sauf
    ce qui change de scène et lancer des missions ou conduire. C'est toujours
    le joueur 1 » (Martin, 22 sept.). Le deuxième joueur, ACTION collé à une
    porte : rien. Pas de fondu, pas de pièce. ⚠️ Jugé PAR LE BOUTON, et le
    même juge vérifie que la porte, elle, s'ouvre bien pour le PREMIER — sans
    ça, un décor mal posé (mauvaise tuile, mauvais regard) rendrait le juge
    vert sans rien prouver."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        L.Jeu.basculerCoop();
        const j = L.B.joueur, e2 = L.B.coop.entite, c = L.Monde.carte;
        const porte = c.portes.find(function (p) { return p.lieu === 'planque'; });
        // Le DEUXIEME joueur sur le pas de la porte, face a elle ; le premier a cote.
        e2.x = porte.x * L.TT + 8; e2.y = (porte.y + 1) * L.TT + 10;
        j.x = e2.x + 20; j.y = e2.y;
        L.Entites.regarder(e2, 0, -1);
        L.Entites.regarder(j, 0, -1);
        // ACTION (bouton 0) a LA MANETTE : c'est le deuxieme joueur.
        o.pad([0, 0], [1]);
        o.frame(1);
        o.pad(null);
        o.frame(1);
        const lui = { fondu: !!L.B.transition, dedans: !!L.B.interieur };
        // La meme porte, au CLAVIER : le joueur 1 la passe.
        j.x = porte.x * L.TT + 8; j.y = (porte.y + 1) * L.TT + 10;
        L.Entites.regarder(j, 0, -1);
        o.tape('KeyE', 1);
        const premier = { fondu: !!L.B.transition };
        o.fondu();
        const apres = { dedans: L.B.interieur ? L.B.interieur.slug : null };
        return { lui: lui, premier: premier, apres: apres, attendu: porte.interieur };
    }""")
    assert r["lui"] == {"fondu": False, "dedans": False}, (
        "ACTION du deuxieme joueur a ouvert la porte : changer de scene est au joueur 1"
    )
    assert r["premier"]["fondu"] is True and r["apres"]["dedans"] == r["attendu"], (
        "la porte ne s'ouvre meme pas pour le joueur 1 : le decor du juge est faux"
    )


def test_la_coop_le_partenaire_suit_dans_la_piece(banc):
    """Il ne pousse pas les portes, il SUIT. L'essai le laissait dehors avec ses
    coordonnees de rue (`Jeu.chargerPiece` : `B.entites = [B.joueur]`), et la
    laisse de la camera le tirait a travers les murs de la piece. Il entre
    avec le premier (`Entites.joueurs`), et `Jeu.majCoop` le repose a cote."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        L.Jeu.basculerCoop();
        const j = L.B.joueur, e2 = L.B.coop.entite, c = L.Monde.carte;
        const porte = c.portes.find(function (p) { return p.lieu === 'planque'; });
        j.x = porte.x * L.TT + 8; j.y = (porte.y + 1) * L.TT + 10;
        e2.x = j.x + 24; e2.y = j.y;
        L.Entites.regarder(j, 0, -1);
        o.tape('KeyE', 1);
        o.fondu();
        o.frame(2);
        const dedans = { piece: L.B.interieur ? L.B.interieur.slug : null,
                          present: L.B.entites.indexOf(e2) >= 0,
                          dist: Math.round(Math.hypot(e2.x - j.x, e2.y - j.y)) };
        // Et on ressort : il revient dehors avec lui, une seule fois (pas de
        // sosie laisse dans la rue).
        L.Jeu.sortir();
        o.fondu();
        o.frame(2);
        let compte = 0;
        for (const q of L.B.entites) if (q === e2) compte++;
        const dehors = { present: L.B.entites.indexOf(e2) >= 0, compte: compte,
                          dist: Math.round(Math.hypot(e2.x - j.x, e2.y - j.y)) };
        return { dedans: dedans, dehors: dehors };
    }""")
    assert r["dedans"]["piece"], "le joueur 1 n'est pas entre : le decor du juge est faux"
    assert r["dedans"]["present"] is True, "le deuxieme joueur est reste dehors pendant que le premier entrait"
    assert r["dedans"]["dist"] <= 32, (
        f"le deuxieme joueur est a {r['dedans']['dist']} px du premier dans la piece : "
        "il a garde ses coordonnees de la rue"
    )
    assert r["dehors"] == {"present": True, "compte": 1, "dist": r["dehors"]["dist"]}
    assert r["dehors"]["dist"] <= 32, "en ressortant, le deuxieme joueur est reste dans la piece"


def test_la_coop_repeche_le_partenaire_oublie_par_une_scene(banc):
    """La ceinture ET les bretelles. `Jeu.majCoop` repose le partenaire des que
    la scene change (l'objet `B.interieur`), mais une sortie qui ne passerait
    pas par la — une scene qu'on ecrira plus tard — le laisserait hors du
    tableau des entites, vivant nulle part. Il y est repeche a l'image
    suivante, a cote du premier, plutot que perdu dans une carte morte."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        L.Jeu.basculerCoop();
        const j = L.B.joueur, e2 = L.B.coop.entite;
        // Ce que ferait une scene qui l'oublie : il quitte le tableau, et ses
        // coordonnees n'ont plus rien a voir avec celles du premier.
        L.B.entites.splice(L.B.entites.indexOf(e2), 1);
        e2.x = j.x + 200; e2.y = j.y + 200;
        o.frame(2);
        const r2 = { present: L.B.entites.indexOf(e2) >= 0,
                      dist: Math.round(Math.hypot(e2.x - j.x, e2.y - j.y)) };
        L.Jeu.basculerCoop();
        return r2;
    }""")
    assert r["present"] is True, "le partenaire oublie par une scene n'est jamais revenu"
    assert r["dist"] <= 32, f"il est revenu a {r['dist']} px du premier, pas a cote"


def test_la_coop_le_deuxieme_joueur_monte_en_passager(banc):
    """Conduire est au joueur 1 — mais le deuxieme MONTE AVEC LUI. Sans ca, la
    laisse de la camera le trainait derriere un char lance, a travers les murs
    (vu a la sonde, 22 sept.). Passager : invisible, porte par la tole, et il
    redescend a cote des que le premier se gare."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        L.Jeu.basculerCoop();
        const j = L.B.joueur, e2 = L.B.coop.entite;
        const v = o.char('auto', 24, 0, 0);
        L.Vehicules.monter(j, v);
        o.frame(1);
        const dedans = { passager: e2.dansVehicule === v, dessine: e2.dessine,
                          surLaTole: Math.round(Math.hypot(e2.x - v.x, e2.y - v.y)) };
        // Le char roule : le passager suit la tole, il ne se traine pas dedans.
        v.vitesse = 3;
        o.frame(20);
        const enRoute = { passager: e2.dansVehicule === v,
                           surLaTole: Math.round(Math.hypot(e2.x - v.x, e2.y - v.y)) };
        L.Vehicules.descendre(j, true);
        o.frame(2);
        const gare = { passager: !!e2.dansVehicule, dessine: e2.dessine,
                        dist: Math.round(Math.hypot(e2.x - j.x, e2.y - j.y)) };
        L.Jeu.basculerCoop();
        return { dedans: dedans, enRoute: enRoute, gare: gare };
    }""")
    assert r["dedans"]["passager"] is True, "le premier a pris le volant, le deuxieme est reste sur le trottoir"
    assert r["dedans"]["dessine"] is False, "un passager ne se dessine pas par-dessus le toit"
    assert r["enRoute"]["passager"] is True and r["enRoute"]["surLaTole"] <= 8, (
        "le passager a perdu le char en route"
    )
    assert r["gare"] == {"passager": False, "dessine": True, "dist": r["gare"]["dist"]}
    assert r["gare"]["dist"] <= 32, "le deuxieme joueur n'est pas redescendu a cote du premier"


def test_la_coop_le_deuxieme_joueur_tombe_ko_sans_envoyer_a_l_hopital(banc):
    """Un vrai joueur peut tomber — mais l'urgence CHANGE DE SCENE, et une
    scene est au joueur 1. A zero de vie, le deuxieme joueur est K.-O. sur
    place (`Entites.blesser` -> `assommer`), il attend son partenaire, puis il
    se releve a mi-vie (`Entites.majJoueur`). La partie, elle, continue."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        L.Jeu.basculerCoop();
        const e2 = L.B.coop.entite;
        for (let i = 0; i < 70; i++) o.frame(1);       // l'invincibilite de naissance retombe
        const passant = L.Entites.creerPieton(e2.x + 40, e2.y, L.Entites.archetypeDeRue());
        const vieMax = e2.vieMax;
        L.Entites.blesser(e2, 999, passant, {});
        const aTerre = { etat: e2.etat, vivant: e2.vivant, fondu: !!L.B.transition,
                          dedans: !!L.B.interieur, vie: e2.vie };
        e2.minuterie = 2;                              // le compte du K.-O., abrege
        o.frame(4);
        const debout = { etat: e2.etat, vie: e2.vie, vieMax: vieMax, invincible: e2.invincible > 0 };
        L.Jeu.basculerCoop();
        return { aTerre: aTerre, debout: debout };
    }""")
    assert r["aTerre"]["etat"] == "assomme", "le deuxieme joueur devait tomber K.-O."
    assert r["aTerre"]["vivant"] is True, "le deuxieme joueur est mort au lieu de tomber K.-O."
    assert r["aTerre"] == {"etat": "assomme", "vivant": True, "fondu": False, "dedans": False,
                            "vie": r["aTerre"]["vie"]}, (
        "la chute du deuxieme joueur a declenche le fondu de l'urgence"
    )
    assert r["debout"]["etat"] != "assomme", "le deuxieme joueur ne s'est jamais releve"
    assert r["debout"]["vie"] == round(r["debout"]["vieMax"] / 2), "il se releve a mi-vie"
    assert r["debout"]["invincible"] is True, "il se releve sans le repit qui evite de retomber aussitot"


def test_la_coop_locale_l_option_donne_la_manette_au_joueur_1(banc):
    """Demande de Martin (22 sept.) : « le joueur 1 doit pouvoir etre soit la
    manette ou soit le clavier dans les options » — `options.coopP1Manette`
    inverse qui a quoi : le premier a la manette, le deuxieme au clavier."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        L.B.options.coopP1Manette = true;
        L.Jeu.basculerCoop();
        // La manette pousse : le PREMIER doit marcher, le second rester immobile.
        o.pad([1, 0]); o.frame(3);
        const joueurVitesseManette = { vx: L.B.joueur.vx };
        const e2VitesseManette = { vx: L.B.coop.entite.vx };
        o.pad(null); o.frame(2);
        // Le clavier pousse : le DEUXIEME doit marcher, le premier rester immobile.
        o.touche('KeyD'); o.frame(3);
        const joueurVitesseClavier = { vx: L.B.joueur.vx };
        const e2VitesseClavier = { vx: L.B.coop.entite.vx };
        o.relacher('KeyD');
        L.Jeu.basculerCoop();
        L.B.options.coopP1Manette = false;
        return { joueurVitesseManette: joueurVitesseManette, e2VitesseManette: e2VitesseManette,
                 joueurVitesseClavier: joueurVitesseClavier, e2VitesseClavier: e2VitesseClavier };
    }""")
    assert r["joueurVitesseManette"]["vx"] > 0.5, "l'option doit donner la manette au joueur 1"
    assert r["e2VitesseManette"] == {"vx": 0}, "le deuxieme joueur ne doit pas repondre a la manette quand elle est au premier"
    assert r["e2VitesseClavier"]["vx"] > 0.2, "le clavier doit faire marcher le deuxieme joueur, manette au premier"
    assert r["joueurVitesseClavier"]["vx"] == 0, "le joueur 1 ne doit pas repondre au clavier quand il a la manette"


def test_la_camera_de_la_coop_retient_le_deuxieme_joueur_a_une_laisse(banc):
    """Le milieu des deux joueurs, et une LAISSE (`LAISSE_COOP`) qui l'empeche
    de trop s'eloigner — sans elle, l'un des deux sortirait de l'ecran.

    ⚠️ Pas un zoom arriere : essayé (22 sept. 2026), puis retiré — le sol et
    les entités ne se dessinent QUE dans la fenêtre normale (480×270,
    `Monde.dessinerSol`/`Entites.visibleAEcran` bornent tout sur `VW`/`VH` en
    dur), un vrai zoom exigeait de réécrire le cull dans plusieurs modules.
    La laisse est le choix simple qui tient dans l'écran tel qu'il est."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        L.Jeu.basculerCoop();
        // Le deuxieme joueur est teleporte loin — bien au-dela de la laisse —
        // et la camera doit le retenir, pas le suivre jusque-la.
        L.B.coop.entite.x += 300;
        o.frame(5);
        const dist = Math.hypot(L.B.joueur.x - L.B.coop.entite.x, L.B.joueur.y - L.B.coop.entite.y);
        L.Jeu.basculerCoop();
        return { dist: dist };
    }""")
    assert r["dist"] < 135, f"le deuxieme joueur est a {r['dist']:.0f}px du premier : la laisse ne tient pas"
