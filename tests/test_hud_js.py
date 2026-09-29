"""Ce que l'écran montre et ce qu'on y touche, sous Node : mini-carte, carte et
légende, menus, pause, mode photo, police pixel, carnet, étoiles, ligne d'objectif,
moment de la journée, zone morte de la manette, joystick tactile.

Découpé de `test_moteur_js.py` (vague D, 29 sept. 2026) : même banc, mêmes juges.
"""

import pytest

from app import carte


def test_la_manette_a_une_zone_morte_radiale(banc):
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        o.pad([0.1, 0.05]); o.frame(2);
        const morte = Object.assign({}, L.Entree.axe);
        o.pad([0.6, 0]); o.frame(2);
        const demi = Object.assign({}, L.Entree.axe);
        o.pad([0, -1]); o.frame(2);
        const plein = Object.assign({}, L.Entree.axe);
        o.pad([0, 0], [0, 1]); o.frame(2);
        const bouton = L.entree('esquive');
        o.pad(null); o.frame(2);
        return { morte: morte, demi: demi, plein: plein, bouton: bouton.pad, apres: L.Entree.axe.source };
    }""")
    assert r["morte"]["mag"] == 0
    assert r["demi"]["source"] == "manette" and 0.45 < r["demi"]["mag"] < 0.6 and r["demi"]["y"] == 0
    assert r["plein"]["mag"] == 1 and r["plein"]["y"] == -1
    assert r["bouton"] is True
    assert r["apres"] == "clavier"


def test_le_joystick_tactile_deplace_le_joueur(banc):
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const j = L.B.joueur, x0 = j.x;
        // Le centre de #croix est en (90, 570) d'apres son faux rectangle.
        // On tire vers la GAUCHE : a l'est du terminus, Ti-Guy fait obstacle
        // depuis que la foule ne se traverse plus.
        o.pointeur('pointerdown', 90, 570, 1);
        o.pointeur('pointermove', 30, 570, 1);
        o.frame(60);
        const pendant = Object.assign({}, L.Entree.axe);
        o.pointeur('pointerup', 30, 570, 1);
        o.frame(2);
        o.bouton('esquive', 'pointerdown');
        o.frame(1);
        const tenu = L.entree('esquive').tactile;
        o.bouton('esquive', 'pointerup');
        return { dx: j.x - x0, pendant: pendant, tenu: tenu, apres: L.Entree.axe.mag,
                 tactile: o.doc.body.classList.contains('tactile') };
    }""")
    assert r["pendant"]["source"] == "tactile" and r["pendant"]["x"] < -0.9
    assert r["dx"] < -40
    assert r["tenu"] is True
    assert r["apres"] == 0
    assert r["tactile"] is True


def test_la_mini_carte_est_cuite_une_seule_fois(banc, paquet):
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const a = L.Monde.miniCarte(), b = L.Monde.miniCarte();
        L.Hud.dessiner();
        return { meme: a === b, w: a.width, h: a.height,
                 eau: L.Monde.couleurMini('~'), mur: L.Monde.couleurMini('B'),
                 route: L.Monde.couleurMini('#'), herbe: L.Monde.couleurMini(','),
                 taille: [L.Hud.MINI.l, L.Hud.MINI.h] };
    }""")
    assert r["meme"] is True, "la mini-carte est repeinte a chaque appel"
    assert [r["w"], r["h"]] == [paquet["carte"]["largeur"], paquet["carte"]["hauteur"]]
    assert len({r["eau"], r["mur"], r["route"], r["herbe"]}) == 4, "les familles doivent se distinguer"
    assert r["taille"] == [64, 48]


@pytest.fixture(scope="module")
def reperes(banc):
    """⚠️ **LA MINI-CARTE, PUIS LA CARTE OUVERTE, UN BANC** (vague C, 28 sept. 2026) : les
    deux juges posent le même objectif à deux pas et regardent battre les repères
    96 images. Le second ouvre la carte (N) là où le premier s'arrête : rien d'autre
    n'a bougé (personne n'a touché une touche), et les battements — 40 et 16 images —
    tiennent plus de deux fois dans chaque fenêtre, quel que soit l'instant de départ."""
    return banc("""function (L, o) {
        L.Jeu.commencer();
        const out = {};
        // test_on_se_trouve_sur_la_carte_et_l_objectif_ne_bat_pas_pareil
        out.fermee = (function () {
            const j = L.B.joueur, c = L.Monde.carte;
            // Un objectif a deux pas, dans le cadre de la mini-carte.
            L.Histoire.cible = function () { return { x: j.x + 40, y: j.y + 40, nom: 'ESSAI', couleur: '#e8b33c' }; };
            const joueur = [], cible = [], rayons = [];
            for (let i = 0; i < 96; i++) {
                o.frame(1);
                const m = L.Hud.marqueurs();
                joueur.push(m.joueur ? 1 : 0);
                rayons.push(m.joueur ? m.joueur.r : -1);
                cible.push(m.cible && m.cible.visible ? 1 : 0);
            }
            const m = L.Hud.marqueurs();
            return { joueur: joueur, cible: cible, rayons: rayons,
                     formes: [m.joueur.forme, m.cible.forme], dedans: m.cible.dedans,
                     pulse: L.Hud.PULSE_JOUEUR, battement: L.Hud.BATTEMENT_CIBLE };
        })();
        // test_la_carte_ouverte_les_reperes_battent_encore
        out.ouverte = (function () {
            const j = L.B.joueur;
            L.Histoire.cible = function () { return { x: j.x + 40, y: j.y + 40, nom: 'ESSAI', couleur: '#e8b33c' }; };
            o.tape('KeyN');
            const ouverte = L.B.etat === 'carte';
            const t = L.B.t, rayons = [], cible = [], joueur = [];
            // On n'appuie sur RIEN : la carte reste ouverte, on ne fait que regarder.
            for (let i = 0; i < 96; i++) {
                o.frame(1);
                const m = L.Hud.marqueurs();
                joueur.push(m.joueur ? 1 : 0);
                rayons.push(m.joueur ? m.joueur.r : -1);
                cible.push(m.cible && m.cible.visible ? 1 : 0);
            }
            return { ouverte: ouverte, fige: L.B.t === t, etat: L.B.etat,
                     joueur: joueur, rayons: rayons, cible: cible };
        })();
        return out;
    }""")


def test_on_se_trouve_sur_la_carte_et_l_objectif_ne_bat_pas_pareil(reperes):
    """⚠️ La demande de Martin : « un icone clignotant pour savoir ou on est ».
    Le joueur ETAIT dessine — un carre blanc de 2 px — mais depuis M8 la ville
    fait 421 x 213 tuiles et ce carre s'est perdu dans le gris. Ce n'etait pas un
    manque, c'etait une regression : il etait lisible sur le Faubourg.

    Deux pieges, et le test tient les deux : un repere qui clignote s'EFFACE une
    image sur deux (on ne cache pas la seule chose qu'on cherche — le joueur
    pulse, il ne disparait jamais), et deux choses qui battent au meme rythme se
    confondent (l'anneau du joueur contre le losange de l'objectif)."""
    r = reperes["fermee"]
    assert all(r["joueur"]), "le repere du joueur disparait : on cache ce qu'on cherche"
    assert len(set(r["rayons"])) > 2, "l'anneau du joueur ne pulse pas : rien ne le ramene a l'oeil"
    assert 0 in r["cible"] and 1 in r["cible"], "l'objectif ne clignote plus"
    assert r["formes"] == ["anneau", "losange"], "les deux reperes ont la meme forme"
    assert r["pulse"] != r["battement"], "le joueur et l'objectif battent au meme rythme"
    assert r["dedans"] is True


def test_la_carte_ouverte_les_reperes_battent_encore(reperes):
    """⚠️ Sur la carte plein ecran, Martin ne voyait plus rien clignoter. Le
    dessin etait bon : c'est l'HORLOGE qui etait mauvaise. L'anneau et le
    losange battaient sur `B.t`, le temps du MONDE — et le monde est fige tant
    que la carte est ouverte. Les deux reperes restaient donc geles sur l'image
    ou l'on a appuye sur N, et une fois sur deux geles sur du VIDE : le losange
    tombait dans sa demi-periode eteinte et n'en ressortait jamais.

    Le test ouvre la carte et REGARDE, sans toucher a rien : ce qui bat a
    l'ecran doit battre sur les images dessinees, pas sur celles simulees."""
    r = reperes["ouverte"]
    assert r["ouverte"] and r["etat"] == "carte", "la carte ne s'est pas ouverte sur N"
    assert r["fige"] is True, "le monde tourne sous la carte : le test ne prouve plus rien"
    assert all(r["joueur"]), "le repere du joueur disparait sur la carte"
    assert len(set(r["rayons"])) > 2, "l'anneau du joueur est fige : la carte ouverte, plus rien ne pulse"
    assert 0 in r["cible"] and 1 in r["cible"], "l'objectif ne clignote plus une fois la carte ouverte"


def test_une_cible_hors_du_cadre_devient_une_fleche_et_pas_une_position(banc):
    """⚠️ Sur la mini-carte, une cible hors cadre BORNEE au bord est un mensonge :
    le code la collait au coin, et un objectif a deux cents tuiles s'affichait
    exactement comme un objectif a trois tuiles. Une fleche dit la direction ;
    une position inventee dit le contraire de la verite."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const j = L.B.joueur, c = L.Monde.carte;
        function marqueurPour(dx, dy) {
            L.Histoire.cible = function () {
                return { x: Math.max(8, Math.min(c.pxW - 8, j.x + dx)),
                         y: Math.max(8, Math.min(c.pxH - 8, j.y + dy)), nom: 'LOIN', couleur: '#e8b33c' };
            };
            o.frame(1);
            const m = L.Hud.marqueurs().cible;
            return { forme: m.forme, x: m.x, y: m.y, dedans: m.dedans };
        }
        const est = marqueurPour(2400, 0);          // tout a l'est
        const sud = marqueurPour(0, 1200);          // tout au sud
        const pres = marqueurPour(32, 16);          // a deux pas
        return { est: est, sud: sud, pres: pres, mini: [L.Hud.MINI.x, L.Hud.MINI.y, L.Hud.MINI.l, L.Hud.MINI.h] };
    }""")
    assert r["est"]["forme"] == "fleche" and r["est"]["dedans"] is False
    assert r["sud"]["forme"] == "fleche" and r["sud"]["dedans"] is False
    assert (r["est"]["x"], r["est"]["y"]) != (r["sud"]["x"], r["sud"]["y"]), (
        "deux objectifs dans deux directions differentes pointent au meme endroit"
    )
    mx, my, large, haut = r["mini"]
    for cote in ("est", "sud"):
        assert mx <= r[cote]["x"] <= mx + large and my <= r[cote]["y"] <= my + haut, r[cote]
    assert r["pres"]["forme"] == "losange" and r["pres"]["dedans"] is True


def test_la_legende_de_la_carte_se_derive_de_la_table_des_couleurs(banc, paquet):
    """⚠️ Une legende recopiee a la main ment des qu'on ajoute un lieu — c'est
    exactement ce qui etait arrive a la table des couleurs : dix lieux declares,
    seize sur la carte, six gris. La legende se batit donc DEPUIS les donnees, et
    chaque lieu de la ville y a sa ligne."""
    familles = paquet["carte"]["familles"]
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const carte = L.Monde.carte;
        const legende = L.Hud.legendeDeLaCarte(carte);
        const couleurs = carte.points.map(function (p) { return { slug: p.slug, famille: p.famille, couleur: L.Hud.couleurDeLieu(p) }; });
        // Et la carte plein ecran la dessine pour de vrai.
        L.Jeu.ouvrirCarte();
        const avant = L.B.stats.rects;
        o.frame(1);
        return { legende: legende, couleurs: couleurs, etat: L.B.etat, rects: L.B.stats.rects - avant,
                 points: carte.points.length };
    }""")
    attendues = {f: familles[f]["couleur"] for f in familles}
    for lieu in r["couleurs"]:
        assert lieu["famille"] in attendues, lieu
        assert lieu["couleur"] == attendues[lieu["famille"]], lieu
    vues = [e["famille"] for e in r["legende"]]
    # ⚠️ L'ordre de la table ECRITE en Python, pas celui du paquet : le paquet trie
    # ses cles, et ce juge relisait l'alphabet en croyant relire la table.
    assert vues == [f for f in carte.FAMILLES_DE_LIEU if f in vues], "la legende doit suivre l'ordre de la table"
    assert set(vues) == {lieu["famille"] for lieu in r["couleurs"]}, (
        "la legende et les blips ne parlent pas des memes familles"
    )
    for entree in r["legende"]:
        assert entree["libelle"] == familles[entree["famille"]]["libelle"]
    assert r["etat"] == "carte" and r["rects"] > 0


def test_le_carnet_rappelle_la_mission_sans_rien_inventer(banc, paquet):
    """⚠️ Demande de Martin : « un rappel de la mission en cours dans le menu.
    Un journal et un bestiaire avec les personnages connus. »

    Le carnet **n'invente aucune donnée** : tout ce qu'il montre était déjà
    dans la partie et n'était montré nulle part. Le juge tient donc la seule
    chose qui compte — **trois endroits, une seule vérité** : la page EN COURS
    dit la même mission que la ligne du HUD (`ligneObjectif`) et que le GPS
    (`cible`), et elle barre exactement les objectifs déjà faits."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const p = L.B.partie;
        const vide = L.Hud.menuCarnetEnCours();
        L.Histoire.commencer('m1');
        const m = L.Histoire.courante();
        // ⚠️ La DERNIERE etape : elle a un lieu, donc un GPS — c'est la seule
        // facon de comparer les trois sources d'un coup.
        p.mission.etape = m.objectifs.length - 1;
        const menu = L.Hud.menuCarnetEnCours();
        const lignes = menu.items.map(function (i) { return { l: i.libelle, d: i.detail || '' }; });
        const gps = L.Histoire.cible();
        return { vide: vide.items.map(function (i) { return i.libelle; }),
                 titre: menu.titre, attendu: m.titre.toUpperCase(), etape: p.mission.etape,
                 lignes: lignes, objectifs: m.objectifs.map(function (o) { return o.texte; }),
                 hud: L.Histoire.ligneObjectif(), gps: gps && gps.nom,
                 donneur: L.Histoire.personnage(m.donneur).nom.toUpperCase(),
                 recompense: m.recompense };
    }""")
    assert any("AUCUNE MISSION" in ligne for ligne in r["vide"]), "sans mission, la page doit le dire : %s" % r["vide"]
    assert r["titre"] == r["attendu"], "la page ne porte pas le titre de la mission"
    details = {e["l"]: e["d"] for e in r["lignes"]}
    assert details.get("DONNÉE PAR") == r["donneur"], "le donneur n'est pas nommé : %s" % r["lignes"]
    assert details.get("RÉCOMPENSE") == "%s $" % r["recompense"], "la récompense n'est pas dite"
    # ⚠️ Les objectifs : tous listés, les faits marqués d'un point, celui du
    # moment d'un chevron — et c'est le MEME texte que la ligne du HUD.
    faits = [e["l"][2:] for e in r["lignes"] if e["l"].startswith("\u00b7 ")]
    encours = [e["l"][2:] for e in r["lignes"] if e["l"].startswith("> ")]
    assert faits == r["objectifs"][:r["etape"]], "les objectifs faits ne sont pas barrés : %s" % faits
    assert encours == [r["objectifs"][r["etape"]]] == [r["hud"]], (
        "la page et la ligne du HUD ne disent pas la même chose : %s / %s" % (encours, r["hud"])
    )
    # ⚠️ Trois endroits, une seule vérité : la page, le HUD et le GPS.
    assert r["gps"], "le GPS doit pointer quelque part pendant la mission"
    assert details.get("OÙ") == r["gps"].upper(), (
        "la page n'envoie pas où le GPS envoie : %s / %s" % (details.get("OÙ"), r["gps"])
    )


def test_le_journal_du_carnet_s_ecrit_tout_seul_et_reste_sous_son_plafond(banc):
    """⚠️ Le journal s'écrit **à partir de ce que le jeu émet déjà** : le jour où
    c'est une deuxième comptabilité tenue à la main, elle dérive de la première
    et plus personne ne sait laquelle a raison. Ici : une mission réussie, une
    arrestation, un séjour à l'hôpital — trois choses qu'aucune ligne de code
    du carnet ne déclenche.

    Et il est **plafonné**. Une partie de cent jours accumulerait des dizaines
    d'entrées, et la partie voyagera par le réseau en M14. ⚠️ On jette le
    quotidien **avant** les jalons : on veut pouvoir relire quand on a
    rencontré Marco, pas ce qu'on a mangé."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const p = L.B.partie, H = L.Histoire;
        p.carnet.length = 0;
        // 1. Rien n'est ecrit a la main : on joue les evenements du jeu.
        H.rencontrer('ti_guy');
        H.commencer('m1');
        H.reussir();
        H.evenement('mort');
        H.evenement('arrete');
        const apres = p.carnet.map(function (e) { return { t: e.t, jalon: e.jalon, j: e.j }; });
        // 2. Le plafond : cent jours de quotidien ne doivent pas chasser les
        //    jalons ni faire deborder le carnet.
        const jalonsAvant = p.carnet.filter(function (e) { return e.jalon; }).length;
        for (let i = 0; i < 300; i++) H.noter('BOUCHEE ' + i, false);
        const plein = { n: p.carnet.length, max: H.CARNET_MAX,
                        jalons: p.carnet.filter(function (e) { return e.jalon; }).length };
        // 3. Et quand il n'y a plus que des jalons, ils cedent aussi : rien ne
        //    grossit sans fin.
        p.carnet.length = 0;
        for (let i = 0; i < 300; i++) H.noter('JALON ' + i, true);
        const jalons = p.carnet.length;
        return { apres: apres, plein: plein, jalons: jalons, jalonsAvant: jalonsAvant };
    }""")
    textes = [e["t"] for e in r["apres"]]
    assert any("MISSION" in t for t in textes), "une mission reussie doit laisser une trace : %s" % textes
    assert any("HÔPITAL" in t for t in textes), "l'hopital doit laisser une trace : %s" % textes
    assert any("ARRÊTÉ" in t for t in textes), "une arrestation doit laisser une trace : %s" % textes
    assert all(e["j"] >= 1 for e in r["apres"]), "chaque entree est datee au jour de jeu"
    assert r["plein"]["n"] == r["plein"]["max"], (
        "le journal deborde : %s entrees pour un plafond de %s" % (r["plein"]["n"], r["plein"]["max"])
    )
    assert r["plein"]["jalons"] == r["jalonsAvant"], (
        "le quotidien a chassé des jalons : %s au lieu de %s" % (r["plein"]["jalons"], r["jalonsAvant"])
    )
    assert r["jalons"] == r["plein"]["max"], "meme les jalons cedent quand il n'y a qu'eux"


def test_le_repertoire_ne_montre_que_les_gens_rencontres(banc, paquet):
    """⚠️ Un répertoire qui montre la fin est pire que pas de répertoire. Rien
    ne disait, avant, qu'on avait rencontré quelqu'un : `p.appels` et
    `p.missionsFaites` le disent à moitié. `p.connus` s'écrit la **première
    fois qu'on parle**, et le répertoire ne montre que lui — sinon il
    divulgâche Josée, Marco qui te vend, et le Dr Lachance de M13."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const p = L.B.partie, H = L.Histoire;
        const neuve = L.Hud.menuCarnetRepertoire().items.map(function (i) { return i.libelle; });
        const tous = (L.B.defs.personnages || []).length;
        // On parle a Ti-Guy : lui seul entre au repertoire.
        H.parler('ti_guy');
        L.Hud.fermerMenu(); L.B.dialogue = null; L.B.cinema = null;
        const un = L.Hud.menuCarnetRepertoire().items.map(function (i) { return i.libelle; });
        const deux = H.rencontrer('ti_guy');          // deux fois : rien de plus
        const connus = Object.keys(p.connus);
        // La fiche : son visage se dessine, et elle liste SES missions.
        const fiche = L.Hud.menuCarnetFiche('ti_guy');
        let dessine = 0;
        const faux = { imageSmoothingEnabled: false, drawImage: function () { dessine++; },
                       fillRect: function () {}, fillStyle: '' };
        fiche.dessiner(faux, 0, 0, 320, 200);
        const ligneOu = fiche.items.find(function (i) { return i.libelle === 'ON LE TROUVE'; });
        return { neuve: neuve, un: un, deux: deux, connus: connus, tous: tous,
                 titre: fiche.titre, dessine: dessine, ou: ligneOu && ligneOu.detail,
                 lieux: (L.Monde.carte.points || []).map(function (x) { return x.nom.toUpperCase(); }),
                 fiches: fiche.items.map(function (i) { return i.libelle; }) };
    }""")
    assert [x for x in r["neuve"] if x != "RETOUR"] == ["TU N’AS ENCORE PARLÉ À PERSONNE"], (
        "une partie neuve ne connait personne : %s" % r["neuve"]
    )
    assert r["connus"] == ["ti_guy"], "seul celui a qui on a parle entre au repertoire : %s" % r["connus"]
    assert r["deux"] is False, "on n'entre au repertoire qu'une fois"
    assert r["tous"] > 1, "le catalogue a plus d'un personnage — c'est tout l'interet du juge"
    assert len([x for x in r["un"] if x != "RETOUR"]) == 1, "le repertoire montre quelqu'un d'autre : %s" % r["un"]
    assert r["titre"] == "TI-GUY" and r["dessine"] == 1, "la fiche doit dessiner son visage : %s" % r
    assert any("RENCONTRÉ" in x for x in r["fiches"])
    # ⚠️ « porte:terminus » est une adresse de CODE : la fiche doit dire le nom
    # du lieu, sinon elle envoie le joueur a « PORTE:TERMINUS ».
    assert ":" not in (r["ou"] or ""), "la fiche donne une adresse de code : %s" % r["ou"]
    assert r["ou"] and r["ou"] in r["lieux"], "le lieu de la fiche n'existe pas sur la carte : %s" % r["ou"]


def test_sortir_d_une_fiche_rend_le_curseur_a_la_meme_personne(banc):
    """⚠️ RETOUR depuis une fiche rouvrait le RÉPERTOIRE sur sa première ligne :
    avec dix personnes connues, on reperdait sa place à chaque fiche (Martin,
    22 sept. 2026). Au clavier, comme on joue : on ouvre la fiche de la
    DEUXIÈME personne, on en sort par RETOUR puis par B, le curseur est sur
    elle ; et le carnet rouvre sur RÉPERTOIRE, pas sur EN COURS."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const H = L.Histoire;
        (L.B.defs.personnages || []).slice(0, 3).forEach(function (q) { H.rencontrer(q.slug); });
        // La partie neuve ouvre sur l'aide COMMANDES : Echap la ferme, Echap met en pause.
        while (L.B.menu) o.tape('Escape', 2);
        o.tape('Escape', 2);
        L.Hud.ouvrirOnglet('carnet');
        const sous = function () { const m = L.B.menu; return m && m.items[m.curseur].libelle; };
        const ici = function () { return L.B.menu ? { titre: L.B.menu.titre, ligne: sous() } : null; };
        while (sous() !== 'RÉPERTOIRE') o.tape('ArrowDown', 2);
        o.tape('KeyE', 2);
        const premier = sous();
        o.tape('ArrowDown', 2);
        const visee = sous();
        o.tape('KeyE', 2);
        const fiche = ici(), surRetour = sous();
        o.tape('KeyE', 2);                         // RETOUR, la ligne du bas
        const parRetour = ici();
        o.tape('KeyE', 2);
        o.tape('KeyB', 2);                         // B recule d'un cran (Echap reprend la partie)
        const parB = ici();
        o.tape('KeyB', 2);
        const carnet = ici();
        return { premier: premier, visee: visee, fiche: fiche, surRetour: surRetour,
                 parRetour: parRetour, parB: parB, carnet: carnet };
    }""")
    assert r["visee"] != r["premier"], "il faut viser une autre personne que la premiere : %s" % r
    assert r["fiche"]["titre"] == r["visee"] and r["surRetour"] == "RETOUR", r
    assert r["parRetour"] == {"titre": "RÉPERTOIRE", "ligne": r["visee"]}, (
        "RETOUR doit rendre le curseur a la personne dont on sort : %s" % r
    )
    assert r["parB"] == {"titre": "RÉPERTOIRE", "ligne": r["visee"]}, "B doit faire pareil : %s" % r
    assert r["carnet"] == {"titre": "LE CARNET", "ligne": "RÉPERTOIRE"}, (
        "le carnet doit rouvrir sur la page d'ou l'on revient : %s" % r
    )


def test_le_menu_fige_le_jeu_et_se_navigue(banc):
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const t0 = L.B.t;
        let choisi = null;
        L.Hud.ouvrirMenu({ titre: 'ESSAI', items: [
            { libelle: 'UN', faire: function () { choisi = 'un'; return true; } },
            { libelle: 'DEUX', faire: function () { choisi = 'deux'; return true; } },
            { libelle: 'TROIS', actif: false, faire: function () { choisi = 'trois'; return true; } },
        ] });
        o.frame(30);
        const fige = L.B.t === t0;
        o.tape('KeyS', 2);
        const curseur = L.B.menu.curseur;
        o.tape('KeyE', 2);
        const ferme = L.B.menu === null;
        L.Hud.ouvrirMenu({ titre: 'ESSAI', items: [{ libelle: 'X', faire: function () { return true; } }] });
        o.tape('Space', 2);
        return { fige: fige, curseur: curseur, choisi: choisi, ferme: ferme, retour: L.B.menu === null };
    }""")
    assert r["fige"] is True, "le temps passe pendant un menu"
    assert r["curseur"] == 1 and r["choisi"] == "deux" and r["ferme"] is True
    assert r["retour"] is True, "FRAPPE doit fermer un menu"


def test_un_menu_s_ouvre_sur_une_ligne_qu_on_peut_choisir(banc):
    """⚠️ Un menu qui s'ouvre sur son EN-TÊTE n'a l'air d'avoir aucune sélection :
    la seule ligne surlignée est grise comme tout ce qui est hors de portée, et
    ACTION n'y répond qu'un bip. La moitié des comptoirs commencent par une ligne
    qui se lit et ne se choisit pas (« LA DETTE », « TON DOSSIER », « PRIX DU
    JOUR ») — c'est `ouvrirMenu` qui pose le curseur, pas chaque menu à la main.

    ⚠️ Mais une ligne HORS DE PORTÉE reste un choix : le curseur s'y pose, et
    c'est le bip qui dit pourquoi elle est grise. Et un menu qui NOMME son
    curseur (le JOURNAL s'ouvre en haut de sa liste et s'y promène) le garde."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        function entete() { return { libelle: 'CE QUE TU DOIS', detail: '100 $', actif: false }; }
        function ouvrir(deuxieme, curseur) {
            const m = { titre: 'ESSAI', items: [entete(), deuxieme] };
            if (curseur !== undefined) m.curseur = curseur;
            L.Hud.ouvrirMenu(m);
            const ou = L.B.menu.curseur;
            L.Hud.fermerMenu();
            return ou;
        }
        return {
            surLeChoix: ouvrir({ libelle: 'DONNER 500 $', faire: function () { return true; } }),
            surLaGrise: ouvrir({ libelle: 'TOUT REGLER', actif: false, faire: function () { return true; } }),
            rienAChoisir: ouvrir({ libelle: 'ARRESTATIONS', detail: '3', actif: false }),
            nomme: ouvrir({ libelle: 'RETOUR', faire: function () { return true; } }, 0),
        };
    }""")
    assert r["surLeChoix"] == 1, "le curseur s'ouvre sur un en-tête qu'on ne peut pas activer : %s" % r
    assert r["surLaGrise"] == 1, "une ligne hors de portée est un choix, pas un décor : %s" % r
    assert r["rienAChoisir"] == 0, "un menu sans rien à choisir (le BILAN) doit rester en haut : %s" % r
    assert r["nomme"] == 0, "un menu qui dit où il veut son curseur se le fait déplacer : %s" % r


def test_la_rue_s_efface_sous_un_menu_ouvert(banc):
    """⚠️ La boîte d'un menu ne couvre qu'à 92 % : ce qui est CLAIR derrière elle
    la transperce. Une bulle de passant qui parle sous le comptoir s'imprimait en
    travers d'une ligne — Martin a photographié « TOUT REGLER » écrasé par un
    « HE! LE COUSIN! ». La pause pose déjà son voile avant son menu ; un menu en
    jeu fige le monde autant qu'elle et mérite le même fond."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const ctx = L.Base.ecran();
        function rendre() {
            ctx.traces = [];
            L.Hud.dessiner();
            const t = ctx.traces;
            ctx.traces = null;
            return t;
        }
        function voiles(t) {
            return t.filter(function (r) { return r[0] === 0 && r[1] === 0 && r[2] === L.VW && r[3] === L.VH; });
        }
        function boite(t) {
            return t.findIndex(function (r) { return String(r[4]).indexOf('0.92') >= 0; });
        }
        const sansMenu = voiles(rendre()).length;
        L.Hud.ouvrirMenu({ titre: 'ESSAI', items: [{ libelle: 'UN', faire: function () { return true; } }] });
        const t = rendre();
        const vs = voiles(t);
        return { sansMenu: sansMenu, avecMenu: vs.length,
                 avant: vs.length ? t.indexOf(vs[vs.length - 1]) < boite(t) : false };
    }""")
    assert r["sansMenu"] == 0, "la rue s'assombrit sans menu ouvert : %s" % r
    assert r["avecMenu"] >= 1, "rien n'efface la rue sous le menu : une bulle la traverse (%s)" % r
    assert r["avant"] is True, "le voile est posé APRÈS la boîte du menu : il l'assombrit (%s)" % r


def test_la_police_pixel_sait_ecrire_tout_ce_que_le_jeu_affiche(banc):
    """Un glyphe absent tombe sur « ? » : HÔPITAL, CASSE-CROÛTE, BÂTON… Martin
    l'a vu a l'ecran. Chaque nom du jeu doit se normaliser en glyphes connus —
    une lettre accentuee l'est par sa lettre de base (`Atlas.connait`)."""
    r = banc("""function (L, o) {
        const d = L.B.defs;
        const textes = [];
        d.armes.forEach(function (a) { textes.push(a.nom); });
        d.vehicules.forEach(function (v) { textes.push(v.nom); });
        d.tenues.forEach(function (t) { textes.push(t.nom); });
        d.magasins.forEach(function (m) { textes.push(m.nom); });
        d.ambulants.forEach(function (m) { textes.push(m.nom); });
        d.carte.points_interet.forEach(function (p) { textes.push(p.nom); });
        d.carte.zones.forEach(function (z) { textes.push(z.nom); });
        Object.keys(d.carte.interieurs).forEach(function (k) { textes.push(d.carte.interieurs[k].nom); });
        d.journal.forEach(function (j) { textes.push(j.titre, j.texte); });
        d.audio.voix.forEach(function (v) { textes.push(v.texte); });
        d.audio.radios.forEach(function (r) { textes.push(r.nom); });
        d.economie.proprietes.forEach(function (p) { textes.push(p.nom); });
        d.pietons.catalogue.forEach(function (p) { textes.push(p.nom); });
        ['DORMIR JUSQU’AU MATIN', 'RÉVEIL À L’HÔPITAL — 30 $', 'Baie-des-Brumes… la brume'].forEach(function (t) { textes.push(t); });
        // La fortune du HUD : toLocaleString colle une espace fine insecable entre les milliers.
        textes.push((1078).toLocaleString('fr-CA') + ' $', (1250000).toLocaleString('fr-CA') + ' $');
        const inconnus = {};
        textes.forEach(function (t) {
            for (const ch of L.Atlas.normaliser(t)) if (ch !== ' ' && !L.Atlas.connait(ch)) inconnus[ch] = (inconnus[ch] || 0) + 1;
        });
        return { n: textes.length, inconnus: inconnus, hopital: L.Atlas.normaliser('Hôpital de Baie-des-Brumes'),
                 largeur: L.Atlas.largeurTexte('Œuvre', 1),
                 argent: L.Atlas.normaliser((1078).toLocaleString('fr-CA') + ' $') };
    }""")
    assert r["n"] > 40
    assert r["inconnus"] == {}, f"glyphes que la police ne sait pas ecrire : {r['inconnus']}"
    assert r["hopital"] == "HÔPITAL DE BAIE-DES-BRUMES", "la police garde les accents"
    assert r["argent"] == "1 078 $", "le separateur des milliers doit devenir une vraie espace"
    assert r["largeur"] == 6 * 4 - 1, "la largeur doit compter le OE en deux lettres"


def test_la_police_dessine_l_accent_au_dessus_de_la_lettre(banc):
    """Martin (17 sept. 2026) : « le jeu doit supporter les accents ». Longtemps
    la police ramenait « É » a « E » avant de dessiner.

    Le juge compte les pixels peints : « É » peint ceux de « E », PLUS l'aigu
    trois rangs au-dessus, un rang vide entre les deux ; « Ç » peint sa cedille
    SOUS la lettre ; « È », « Ê » et « Ë » ne se peignent pas pareil. La largeur
    d'une ligne ne bouge pas, et un accent decompose (« E » + U+0301) donne le
    meme dessin qu'un « É » compose."""
    r = banc("""function (L, o) {
        function peindre(s, e) {
            const px = [];
            const ctx = { set fillStyle(v) {}, fillRect: function (x, y, w, h) { px.push([x, y, w, h]); } };
            L.Atlas.texte(ctx, s, 0, 10, '#fff', e || 1);
            return px;
        }
        const e = peindre('E'), eAigu = peindre('É');
        const sans = function (a, b) { const k = b.map(String); return a.filter(function (p) { return k.indexOf(String(p)) < 0; }); };
        return {
            e: e.length, eAigu: eAigu.length,
            accent: sans(eAigu, e),
            garde: sans(e, eAigu).length,
            grave: sans(peindre('È'), e), circ: sans(peindre('Ê'), e), trema: sans(peindre('Ë'), e),
            cedille: sans(peindre('Ç'), peindre('C')),
            decompose: JSON.stringify(peindre('E\u0301')) === JSON.stringify(eAigu),
            minuscule: JSON.stringify(peindre('é')) === JSON.stringify(eAigu),
            double: sans(peindre('É', 2), peindre('E', 2)),
            largeur: [L.Atlas.largeurTexte('HÔPITAL', 1), L.Atlas.largeurTexte('HOPITAL', 1),
                      L.Atlas.largeurTexte('E\u0301TE\u0301', 1)],
            ntilde: JSON.stringify(peindre('Ñ')) === JSON.stringify(peindre('N')),
            inconnu: JSON.stringify(peindre('Ñ')) === JSON.stringify(peindre('?')),
            marques: Object.keys(L.MARQUES_PIXEL).map(function (k) { return L.MARQUES_PIXEL[k].bits.length; }),
        };
    }""")
    assert r["garde"] == 0, "l'accent s'ajoute a la lettre, il ne la remplace pas"
    assert r["eAigu"] > r["e"], "« É » doit peindre plus que « E »"
    assert r["accent"] == [[2, 7, 1, 1], [1, 8, 1, 1]], "l'aigu : deux rangs au-dessus, un rang vide avant la lettre (y = 10)"
    assert r["grave"] and r["circ"] and r["trema"]
    assert len({str(r["accent"]), str(r["grave"]), str(r["circ"]), str(r["trema"])}) == 4, "quatre accents, quatre dessins"
    assert r["cedille"] and all(y >= 15 for _, y, _, _ in r["cedille"]), "la cedille pend SOUS la lettre"
    assert all(y < 10 for _, y, _, _ in r["accent"] + r["grave"] + r["circ"] + r["trema"]), "les accents sont au-dessus"
    assert r["decompose"], "« E » + U+0301 se dessine comme « É »"
    assert r["minuscule"], "« é » s'ecrit « É »"
    assert r["double"] == [[4, 4, 2, 2], [2, 6, 2, 2]], "a l'echelle 2, l'accent grandit avec la lettre"
    assert r["largeur"][0] == r["largeur"][1] == 7 * 4 - 1, "un accent n'elargit pas sa lettre"
    assert r["largeur"][2] == 3 * 4 - 1, "un accent decompose ne prend pas une case a lui"
    assert r["ntilde"] and not r["inconnu"], "une lettre dont l'accent n'est pas dessine garde sa base, pas « ? »"
    assert set(r["marques"]) == {6}


def test_la_pause_a_un_menu_des_options_et_un_bilan(banc):
    """Les options et le bilan sont des ONGLETS du classeur de la PAUSE : on y
    tourne aux fleches, et ECHAP reprend la partie de n'importe lequel."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        o.tape('Escape', 2);
        const pause = { etat: L.B.etat, menu: L.B.menu && L.B.menu.titre };
        // OPTIONS : le cinquieme onglet ; on bascule le sang.
        L.Hud.ouvrirOnglet('options');
        const options = L.B.menu.titre;
        const sangAvant = L.B.options.sang;
        L.B.menu.items.find(function (i) { return i.libelle === 'SANG'; }).faire(L.B.menu.items[0]);
        const sangApres = L.B.options.sang;
        const sauvees = JSON.parse(o.store[L.Sauvegarde.CLE_OPTIONS]).sang;
        // Deux crans a gauche : COMMANDES, puis BILAN.
        o.tape('ArrowLeft', 2); o.tape('ArrowLeft', 2);
        const bilan = { titre: L.B.menu.titre, lignes: L.B.menu.items.length };
        o.tape('Escape', 2);
        return { pause: pause, options: options, sangAvant: sangAvant, sangApres: sangApres, sauvees: sauvees,
                 bilan: bilan, etat: L.B.etat, menu: L.B.menu };
    }""")
    assert r["pause"] == {"etat": "pause", "menu": "PAUSE"}
    assert r["options"] == "OPTIONS" and r["sangApres"] == (not r["sangAvant"]) and r["sauvees"] == r["sangApres"]
    assert r["bilan"]["titre"] == "BILAN" and r["bilan"]["lignes"] >= 9
    assert r["etat"] == "jeu" and r["menu"] is None, "Echap doit reprendre et fermer le menu"


def test_le_mode_photo_fige_le_monde_promene_la_camera_et_capture(banc):
    """M14, 6e vague. Ouvert depuis la PAUSE, comme la carte : le monde attend
    (`B.t` ne bouge pas) mais l'ecran continue de se dessiner (`B.image`
    avance) — sinon le mode photo serait un ecran noir, pas une vue qu'on
    cadre. Le stick deplace la vue SANS toucher `B.cam` (c'est `B.photo.dx/dy`
    qui bouge), ARME cycle les filtres, ACTION capture et telecharge, ANNULER
    referme."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const camAvant = { x: L.B.cam.x, y: L.B.cam.y }, tAvant = L.B.t;
        o.tape('Escape', 2);
        L.B.menu.items.find(function (i) { return i.libelle === 'MODE PHOTO'; }).faire();
        // ⚠️ Une COPIE : `L.B.photo` est le meme objet du debut a la fin, le
        // stick et les filtres le mutent en place plus bas — le lire ici sans
        // copier aurait rendu l'etat de LA FIN, pas celui de l'ouverture.
        const ouvert = { etat: L.B.etat, photo: Object.assign({}, L.B.photo), menu: L.B.menu };
        const imageAvant = L.B.image;
        o.pad([1, 0]); o.frame(10); o.pad(null);
        const apresPan = { dx: L.B.photo.dx, camInchangee: L.B.cam.x === camAvant.x && L.B.cam.y === camAvant.y,
                            imageAvance: L.B.image > imageAvant };
        o.tape('Tab', 2);
        const filtreApres1 = L.B.photo.filtre;
        o.tape('Tab', 2);
        const filtreApres2 = L.B.photo.filtre;
        o.tape('Enter', 2);
        const captures = o.photo.telechargements.length, premiere = o.photo.telechargements[0];
        // ⚠️ `tGele` AVANT de refermer : sortir du mode photo rend la main au
        // jeu, qui recommence aussitot a faire avancer `B.t` — le lire apres
        // les deux images de relache de `tape('Backspace', 2)` aurait mesure
        // la reprise, pas le gel.
        const tGele = L.B.t === tAvant;
        o.tape('Backspace', 2);
        return { ouvert: ouvert, apresPan: apresPan, filtreApres1: filtreApres1, filtreApres2: filtreApres2,
                 captures: captures, premiere: premiere, tGele: tGele,
                 etatApres: L.B.etat, photoApres: L.B.photo };
    }""")
    assert r["ouvert"] == {"etat": "photo", "photo": {"dx": 0, "dy": 0, "filtre": 0}, "menu": None}
    assert r["apresPan"]["dx"] > 0, "le stick doit deplacer la vue"
    assert r["apresPan"]["camInchangee"], "la camera DU JOUEUR ne bouge pas : seule la vue se detache"
    assert r["apresPan"]["imageAvance"], "le monde attend, l'ecran continue de se dessiner"
    assert r["filtreApres1"] == 1 and r["filtreApres2"] == 2, "ARME cycle les filtres un a la fois"
    assert r["captures"] == 1
    assert r["premiere"]["href"].startswith("data:image/png")
    assert r["premiere"]["nom"].startswith("bandini-") and r["premiere"]["nom"].endswith(".png")
    assert r["tGele"], "le monde attend en mode photo, comme la carte"
    assert r["etatApres"] == "jeu" and r["photoApres"] is None, "ANNULER referme et rend la main"


def test_la_vue_du_mode_photo_ne_deborde_pas_de_la_ville(banc):
    """Sans borne, le stick pousserait la vue hors de la carte — de l'eau et du
    vide sous la mer, jamais peints (voir `Monde.limitesCamera`). Pousse dans
    UN SEUL sens largement plus longtemps qu'il n'en faut pour traverser toute
    la ville, puis encore autant : si la vue s'arretait au bord une fois pour
    toutes, `camX/Y` ne bougerait plus du tout entre les deux mesures — un
    plafond qui laisserait encore deriver un peu (un bug d'arrondi, par
    exemple) se verrait ici, pas seulement « ca n'a pas encore deborde »."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        L.Jeu.pause();
        L.B.menu.items.find(function (i) { return i.libelle === 'MODE PHOTO'; }).faire();
        const lim = L.Monde.limitesCamera();
        o.pad([1, 1]); o.frame(2500);
        const premiere = { x: L.B.cam.x + L.B.photo.dx, y: L.B.cam.y + L.B.photo.dy };
        o.frame(1200); o.pad(null);
        const seconde = { x: L.B.cam.x + L.B.photo.dx, y: L.B.cam.y + L.B.photo.dy };
        return { premiere: premiere, seconde: seconde, lim: lim };
    }""")
    assert r["premiere"] == r["seconde"], "colle au bord : pousser plus longtemps ne devrait plus rien deplacer"
    assert r["premiere"]["x"] == pytest.approx(r["lim"]["xMax"], abs=0.01)
    assert r["premiere"]["y"] == pytest.approx(r["lim"]["yMax"], abs=0.01)


def test_les_etoiles_de_recherche_se_lisent(banc):
    """⚠️ Demande de Martin : « les étoiles de police plus grosses, jaunes et
    au centre de l'écran. » Elles etaient des caracteres « ★ » de la police
    5 x 7 tires a l'echelle 1, dans la colonne du coin haut-droit — SOUS un
    montant d'argent trace a l'echelle 2. La chose la plus importante d'une
    poursuite etait le plus petit element de l'ecran, dans un coin, en blanc.

    Trois regles tiennent maintenant : elles sont plus grandes que le texte du
    HUD, elles sont en haut au centre, et une allumee se distingue d'une
    eteinte sans compter (l'eteinte est CREUSE, pas un point).
    """
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        L.B.recherche.etoiles = 3;
        L.Jeu.rendre();
        const ancres = L.Hud.ancres();
        const etoiles = ancres.find(function (a) { return a.nom === 'etoiles'; });
        const objectif = ancres.find(function (a) { return a.nom === 'objectif'; });
        return {
            etoiles: etoiles, objectif: objectif || null, VW: L.VW,
            hauteurTexte: 7,
                sousEtoiles: objectif ? objectif.y >= etoiles.y + etoiles.h : null,
            largeurEtoile: L.ETOILE[0].length, hauteurEtoile: L.ETOILE.length,
            creuse: L.ETOILE.join('').indexOf('c') >= 0 && L.ETOILE.join('').indexOf('k') >= 0,
        };
    }""")
    e = r["etoiles"]
    assert e, "aucune ancre d'etoiles : le HUD ne les dessine plus"
    assert e["h"] > r["hauteurTexte"], \
        f"les etoiles font {e['h']} px de haut, le texte du HUD en fait {r['hauteurTexte']}"
    centre = e["x"] + e["l"] / 2
    assert abs(centre - r["VW"] / 2) <= 1, f"les etoiles ne sont pas centrees ({centre} pour {r['VW'] / 2})"
    assert e["y"] < 12, "les etoiles ne sont pas en haut"
    assert r["creuse"], "l'etoile n'a ni corps ni contour : allumee et eteinte se confondraient"
    if r.get("objectif"):
        assert r["sousEtoiles"], "la ligne d'objectif chevauche les etoiles"


def test_la_ligne_d_objectif_ne_passe_sur_rien(banc):
    """Bug de Martin, capture a l'appui : « bug de hoverlap en haut ». En taxi,
    « COURSE : POSTE DE POLICE 120M » et « FAIS TROIS COURSES — KLAXONNE POUR
    UN CLIENT 0/3 » etaient ecrits l'un DANS l'autre, tous les deux dores, a un
    pixel de hauteur pres.

    ⚠️ Rien n'etait casse : chaque ligne etait a sa place. La ligne de boulot
    est collee sous le compteur de vitesse (x 70, y 16) et la ligne d'objectif
    tombait sous les etoiles (y 17) — mais elle est CENTREE, et une phrase de
    soixante-dix caracteres centree commence bien avant le milieu de l'ecran.
    Deux mises en page qui ne se connaissaient pas.

    Le juge tient la regle entiere, pas le seul cas de la capture : la ligne
    d'objectif ne chevauche AUCUNE autre ancre du HUD. C'est elle qui cede —
    elle descend d'une rangee par boite qu'elle croise."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const j = L.B.joueur, d = o.ligneDroite();
        j.x = d.x; j.y = d.y;
        L.Histoire.commencer('m3');                 // Marco prete son taxi
        L.B.partie.mission.etape = 1;               // « FAIS TROIS COURSES ... »
        L.B.dialogue = null; L.B.cinema = null;
        if (L.B.mission) L.B.mission.attend = null;
        const taxi = (L.B.mission && L.B.mission.vehicule) || o.char('taxi', 0, 0, 0);
        taxi.x = j.x; taxi.y = j.y; taxi.vitesse = 0;
        L.Vehicules.monter(j, taxi);
        o.tape('Space', 2);                         // klaxon : un client hele
        const b = L.Missions.boulot;
        if (b.client) { taxi.x = b.client.x + 10; taxi.y = b.client.y; j.x = taxi.x; j.y = taxi.y; }
        o.frame(3);                                 // il monte : etape « route »
        // ⚠️ La destination la PLUS LONGUE du jeu, et loin : c'est la ligne de
        // boulot la plus large, la seule qui atteigne le texte centre. Un juge
        // qui prend la premiere course venue ne reproduit rien.
        const poste = L.Histoire.lieu('poste');
        if (poste && b.etape === 'route') b.destination = { x: poste.x, y: poste.y, nom: poste.nom };
        L.Jeu.rendre();
        const ancres = L.Hud.ancres();
        function trouver(n) { return ancres.find(function (a) { return a.nom === n; }) || null; }
        return { ligne: L.Histoire.ligneObjectif(), etape: b.etape, ancres: ancres,
                 objectif: trouver('objectif'), boulot: trouver('boulot') };
    }""")
    assert r["etape"] == "route", f"le taxi n'a pas de course : rien a chevaucher ({r['etape']})"
    assert r["boulot"], "la ligne de boulot ne s'affiche plus"
    assert r["objectif"], "la ligne d'objectif ne s'affiche plus"
    o, b = r["objectif"], r["boulot"]
    assert "COURSES" in r["ligne"], f"ce n'est pas l'objectif de la capture ({r['ligne']})"
    assert o["x"] < b["x"] + b["l"] and b["x"] < o["x"] + o["l"], (
        "les deux lignes ne se croisent meme plus en largeur : le juge ne prouve plus rien "
        f"(objectif {o}, boulot {b})")
    for autre in r["ancres"]:
        if autre["nom"] == "objectif":
            continue
        chevauche = (o["x"] < autre["x"] + autre["l"] and autre["x"] < o["x"] + o["l"]
                     and o["y"] < autre["y"] + autre["h"] and autre["y"] < o["y"] + o["h"])
        assert not chevauche, f"la ligne d'objectif passe sur « {autre['nom']} » : {o} / {autre}"


def test_le_moment_de_la_journee_suit_le_ciel(banc):
    """Martin (22 sept. 2026) : « un petit icone pour indiquer quel moment de la
    journee on est ». Quatre moments, dans l'ordre, une fois chacun par jour —
    et la lune se leve PILE quand `estNuit` le dit : une icone qui dirait « jour »
    quand les barrieres se ferment mentirait. Les heures sont ecrites ici, pas
    relues dans `TEINTES`."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const M = L.Monde, suite = [], desaccords = [];
        for (let k = 0; k < 24 * 60; k += 5) {
            const h = k / (24 * 60), p = M.periode(h);
            if ((p === 'nuit') !== M.estNuit(h)) desaccords.push(k);
            if (suite[suite.length - 1] !== p) suite.push(p);
        }
        return { suite: suite, desaccords: desaccords,
                 minuit: M.periode(0), midi: M.periode(0.5),
                 h645: M.periode(6.75 / 24), h1915: M.periode(19.25 / 24),
                 h900: M.periode(9 / 24), h1700: M.periode(17 / 24) };
    }""")
    assert r["suite"] == ["nuit", "aube", "jour", "crepuscule", "nuit"], r["suite"]
    assert r["desaccords"] == [], f"l'icone et estNuit ne disent pas la meme chose a {r['desaccords']} min"
    assert (r["minuit"], r["midi"]) == ("nuit", "jour")
    assert r["h645"] == "aube", "6 h 45 : le ciel est orange, c'est l'aube"
    assert r["h1915"] == "crepuscule", "19 h 15 : le ciel est orange, c'est le crepuscule"
    assert (r["h900"], r["h1700"]) == ("jour", "jour")


def test_l_icone_du_moment_se_dessine_devant_l_heure(banc):
    """L'icone est DEVANT « JOUR N HH:MM », a la hauteur du texte, et la boite de
    l'heure l'englobe — la ligne d'objectif, qui passe sous tout, passe aussi
    sous elle. ⚠️ Dans une piece, c'est l'heure DEHORS : on dort chez soi la
    nuit, et l'icone dit encore la lune meme si la piece est eclairee."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        function voir() {
            L.Jeu.rendre();
            const a = L.Hud.ancres();
            function trouver(n) { return a.find(function (x) { return x.nom === n; }) || null; }
            return { moment: trouver('moment'), heure: trouver('heure') };
        }
        L.B.partie.heure = 0.5;
        const midi = voir();
        L.B.partie.heure = 0.02;
        const minuit = voir();
        const porte = L.Monde.carte.def.portes.filter(function (q) { return q.interieur; })[0];
        L.Jeu.entrer(porte); L.Jeu.finirTransition();
        L.B.partie.heure = 0.02;
        const dedans = voir();
        return { midi: midi, minuit: minuit, dedans: dedans, interieur: !!L.B.interieur,
                 eclaire: L.Monde.ambiance().alpha, VW: L.VW };
    }""")
    m, h = r["midi"]["moment"], r["midi"]["heure"]
    assert m, "aucune ancre « moment » : le HUD ne dessine pas l'icone"
    assert m["periode"] == "jour" and r["minuit"]["moment"]["periode"] == "nuit"
    assert m["h"] == 7, "l'icone a la hauteur du texte du HUD (7 px)"
    assert m["y"] == h["y"], "l'icone est sur la ligne de l'heure"
    assert m["x"] == h["x"], "l'icone est DEVANT l'heure, et sa boite l'englobe"
    assert h["x"] + h["l"] <= r["VW"], "l'heure deborde de l'ecran"
    assert h["l"] > m["l"] + 20, "la boite de l'heure ne porte plus le texte"
    assert r["interieur"] is True, "temoin : on est bien dans une piece"
    assert r["eclaire"] == 0, "temoin : la piece est eclairee, le ciel ne s'y voit pas"
    assert r["dedans"]["moment"]["periode"] == "nuit", "dans une piece, l'icone dit l'heure DEHORS"


def test_le_niveau_de_recherche_ne_partage_pas_la_couleur_de_l_argent(racine):
    """⚠️ Le dore #e8b33c est deja celui de l'argent et de « ce qui est a toi »
    sur la carte. Deux choses differentes de la meme couleur dans le meme coin
    ne se lisent plus — c'est aussi pour ca que les etoiles ont demenage."""
    source = (racine / "static" / "js" / "hud.js").read_text(encoding="utf-8")
    bloc = source[source.index("const ETOILE_ALLUMEE"):source.index("const ETOILE_L")]
    assert "#e8b33c" not in bloc, "l'etoile reprend le dore de l'argent"
    assert "ETOILE_FLASH" in source, "le clignotement rouge du changement de palier a disparu"
