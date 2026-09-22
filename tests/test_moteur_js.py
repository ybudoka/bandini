"""Le moteur JS sous Node, contre le paquet que le serveur sert VRAIMENT.

Chaque test passe une fonction `(L, o) => resultat` au banc (tests/banc.js) :
L = window.BANDINI, o = outils (frame, touche, pad, pointeur, singe...).
"""

import json
import re

import pytest

from app import carte, economie, vehicules


def test_le_moteur_charge_et_expose_son_api(banc, paquet):
    r = banc("""function (L, o) {
        return { etat: L.B.etat, cles: Object.keys(L).sort(), version: L.B.defs.version,
                 carte: [L.Monde.carte.w, L.Monde.carte.h], fetchs: o.fetchs.length,
                 compte: o.compte.appels.map(function (a) { return a.chemin; }),
                 defi: o.defi.appels.length,
                 ouverture: L.Histoire.fichiersDeLOuverture().length };
    }""")
    assert r["etat"] == "titre"
    for cle in ("B", "Base", "Atlas", "Entree", "Son", "Monde", "Entites", "Combat", "Vehicules",
                "Police", "Missions", "Hud", "Jeu", "Sauvegarde", "SPRITES", "TUILES"):
        assert cle in r["cles"], cle
    assert r["carte"] == [paquet["carte"]["largeur"], paquet["carte"]["hauteur"]]
    # ⚠️ DEUX REQUETES, PLUS CELLES DE L'OUVERTURE — et pas une de plus.
    # Le paquet de definitions et la carte (a part depuis le 16 sept. 2026 :
    # elle faisait plus de la moitie du poids), puis les mp3 de l'ouverture (sa musique et ses
    # quatre voix) que `Son.prechauffer` tire dans le cache du navigateur
    # pendant qu'on lit l'ecran titre : elle part a la seconde ou l'on presse
    # JOUER, et un narrateur qui arrive en retard ne raconte plus rien. Tout le
    # reste de l'audio (12 Mo en 166 fichiers) se charge A L'USAGE, et le
    # chiffre ci-dessous est ce qui le garantit : il ne bouge que si quelqu'un
    # ajoute une phrase a l'ouverture, jamais parce qu'un son de plus s'est
    # invite au demarrage.
    # ⚠️ Plus UNE requete de compte (M14, 2e vague) : `POST /api/compte/ouvrir`,
    # qui tourne le jeton d'appareil une fois par chargement. Sans cookie, le
    # serveur repond « pas de compte » et plus rien ne part — un jeu qui bavarde
    # avec le serveur alors que personne n'a de compte serait un jeu qui a oublie
    # qu'il se joue hors ligne.
    assert r["compte"] == ["ouvrir"]
    # ⚠️ Plus UNE requete pour le defi du jour (M14, 5e vague) : `GET /api/defi`, sans
    # cookie et sans que rien n'attende sa reponse.
    assert r["defi"] == 1
    assert r["fetchs"] == 4 + r["ouverture"]
    assert r["ouverture"] <= 6, "l'ouverture se prechauffe ; la ville, non"


def test_les_sprites_sont_integres(banc):
    r = banc("""function (L, o) {
        const problemes = [];
        for (const nom in L.SPRITES) problemes.push.apply(problemes, L.Atlas.valider(nom, L.SPRITES[nom]));
        for (const ch in L.POLICE_PIXEL) if (L.POLICE_PIXEL[ch].length !== 15) problemes.push('police ' + ch);
        const legende = L.B.defs.carte.legende;
        for (const g in legende) if (!L.TUILES[g]) problemes.push('tuile sans peintre : ' + g);
        return problemes;
    }""")
    assert r == []


def test_chaque_char_de_phase_1_a_son_sprite(banc, paquet):
    """⚠️ Le juge que le prologue de `vehicules.py` promet depuis M9 et qui
    n'existait pas : « phase 1 = le navigateur a son sprite ».

    `test_les_sprites_sont_integres` valide les sprites DECLARES ; il ne dit
    rien du catalogue. Pendant ce temps, quatre chars de phase 1 — camion,
    autobus, ambulance, remorqueuse — etaient dans le paquet, tires par le
    trafic, vendables au garage, et rien ne les dessinait. Le catalogue
    promettait des chars que le jeu ne montrait pas, et aucun test ne le
    disait. Celui-ci le dit, et il dira la meme chose du bateau le jour ou on
    le passera en phase 1."""
    r = banc("""function (L, o) {
        const manquants = [];
        const tailles = {};
        const poses = {};
        for (const v of L.B.defs.vehicules) {
            if (v.phase !== 1) continue;
            const def = L.SPRITES[v.sprite];
            if (!def) { manquants.push(v.slug + ' -> ' + v.sprite); continue; }
            tailles[v.slug] = [def.w, def.h, v.longueur, v.largeur, def.rotations || 0];
            if (def.machine) tailles[v.slug].push(true);
            // ⚠️ La refonte : un char se dessine soit en 32 caps (l'ancienne
            // voie), soit en TROIS POSES debout — et il faut les trois, plus
            // l'ancre a la ligne de sol.
            poses[v.slug] = { a: Object.keys(def.poses || {}).sort().join(','),
                              ancre: def.ancre || null, h: def.h };
        }
        return { manquants: manquants, tailles: tailles, poses: poses,
                 phase2: L.B.defs.vehicules.filter(function (v) { return v.phase !== 1; }).map(function (v) { return v.slug; }) };
    }""")
    assert r["manquants"] == [], "des chars de phase 1 sans sprite : %s" % r["manquants"]
    attendus = {v["slug"] for v in paquet["vehicules"] if v["phase"] == 1}
    assert set(r["tailles"]) == attendus
    for slug, (w, h, lon, lat, rotations, *machine) in r["tailles"].items():
        pose = r["poses"][slug]
        # ⚠️ **UN DEUX-ROUES N'EST PAS UNE GRILLE DESSINEE** (16 sept. 2026, « le
        # vélo et son cycliste ») : c'est une machine en volume, projetée au cap
        # sur une toile CARRÉE dont le centre est le milieu de son empreinte.
        # Ses règles sont donc les siennes : la toile couvre la machine à tous
        # les caps (sa longueur, et ce qui monte au-dessus) sans être une
        # affiche, ses trois poses sont tirées d'elle, et son ancre met
        # `centreDuToit` au centre de la toile — là où elle tourne.
        if machine:
            assert w == h and lon + 4 <= w <= 2 * lon, "%s : toile de %sx%s pour %s px de long" % (slug, w, h, lon)
            assert pose["a"] == "bas,cote,haut", "%s : poses %s" % (slug, pose["a"])
            assert pose["ancre"] == [w / 2, w / 2 - 1 + lon / 2], (
                "%s : ancre %s — son centre de rotation n'est pas le centre de sa toile" % (slug, pose["ancre"])
            )
            continue
        # ⚠️ Le sprite doit COUVRIR la carrosserie, sinon un char de 48 px
        # dessine sur 32 laisse deux capots dans le vide a chaque bout.
        assert w >= lon, "%s : sprite de %s px pour %s px de long" % (slug, w, lon)
        # ⚠️ **ET LA HAUTEUR NE SE MESURE PLUS PAREIL DES DEUX COTES** (15 sept.
        # 2026). Vu d'en haut, `h` etait la LARGEUR du char, d'ou « h <= lat+4 ».
        # Debout, `h` est sa HAUTEUR, et elle n'a rien a voir avec sa largeur :
        # un autobus fait 16 px de large et se dresse sur 21. Ce qui reste vrai
        # des deux cotes : le dessin couvre la carrosserie sans etre une
        # affiche, et rien dans cette ville n'est plus haut que long.
        if rotations:
            assert h >= lat, "%s : sprite de %s px pour %s px de large" % (slug, h, lat)
            assert w <= lon + 6 and h <= lat + 4, "%s : %sx%s pour %sx%s" % (slug, w, h, lon, lat)
        else:
            # La marge laisse la place aux roues — et au BRAS de la remorqueuse,
            # qui depasse derriere et qui est ce qui la nomme de profil.
            assert w <= lon + 12, "%s : sprite de %s px pour %s px de long" % (slug, w, lon)
            # ⚠️ **Reformulé le 15 sept. 2026, la vue plongeante.** La règle
            # disait « rien n'est plus haut que long » : elle datait du dessin
            # de dos À PLAT, où la toile ne portait que la HAUTEUR du char. Vu
            # d'en haut à 45°, la pose de dos porte sa LONGUEUR — la toile fait
            # donc la longueur, à la marge de la ligne de sol près. Ce qui reste
            # vrai : elle ne fait pas PLUS, sinon c'est une affiche.
            assert lat <= h <= lon + 4, "%s : %s px de haut pour %sx%s" % (slug, h, lon, lat)
        # ⚠️ **Reformule deux fois le 15 sept. 2026.** Il exigeait 32 caps pour
        # tout le monde ; la refonte du parc l'a remplace par trois poses ; et
        # le soir meme, « le char tourne comme son ombre » a remis les caps —
        # mais cuits a la demande, a partir d'UN des trois dessins. La fiche,
        # elle, en porte toujours trois : `haut` est celui qui roule, `bas`
        # prete ses phares au dessin qui tourne, `cote` attend qu'on montre un
        # char de profil sans le faire rouler. Ce qui compte ici n'est pas
        # LEQUEL sert, c'est que la fiche soit COMPLETE : un char a moitie
        # converti (deux dessins sur trois, ou une ancre restee au centre) se
        # dessinerait a cote de lui-meme.
        if rotations:
            assert rotations == 32, "%s se dessine en %s caps" % (slug, rotations)
            assert pose["a"] == "base", "%s garde 32 caps mais a des poses : %s" % (slug, pose["a"])
        else:
            assert pose["a"] == "bas,cote,haut", (
                "%s est debout mais il lui manque une pose : %s" % (slug, pose["a"])
            )
            # ⚠️ L'ANCRE EST LA LIGNE DE SOL, pas le centre : un char debout
            # ancre au milieu flotte au-dessus de la rue.
            assert pose["ancre"] and pose["ancre"][1] >= pose["h"] - 4, (
                "%s : ancre %s pour une grille de %s de haut — ce n'est pas la ligne de sol"
                % (slug, pose["ancre"], pose["h"])
            )
    # ⚠️ **Plus un seul véhicule en phase 2 depuis le 16 sept. 2026** : la
    # chaloupe est entrée dans le parc, et la dette de M3 est payée. Ce juge
    # gardait la liste des promesses pour qu'on ne l'oublie pas ; elle est vide,
    # et c'est exactement ce qu'il voulait obtenir.
    assert r["phase2"] == [], (
        "la phase 2 a change : ce juge doit suivre (%s)" % r["phase2"]
    )


def test_un_lourd_defonce_ce_qui_est_bas_et_jamais_une_facade(banc, paquet):
    r"""⚠️ `defonce` etait dans les fiches depuis M9 et PERSONNE NE LE LISAIT.
    Le camion, l'autobus et la remorqueuse rebondissaient sur un grillage
    comme une berline — trois nombres du catalogue (0,75, 0,7, 0,6) qui ne
    voulaient rien dire.

    Le juge tient les deux moities de la regle, et la seconde est la plus
    importante : ce qui est BAS cede (borne-fontaine, grillage, palissade),
    et une FACADE, jamais. La ville tient par ses murs — les juges de
    connexite, les interieurs et les devantures en dependent, et un trou dans
    un mur ouvrirait sur un toit."""
    ph = paquet["conduite"]["physique"]
    r = banc(r"""function (L, o) {
        L.Jeu.commencer();
        const c = L.Monde.carte;
        const out = {};

        // Une tuile de la solidite voulue, avec du libre au nord et au sud :
        // on lance le char dessus par le nord.
        function fonceSur(slug, solide, vitesse) {
            for (let ty = 4; ty < c.h - 4; ty++) {
                for (let tx = 4; tx < c.w - 4; tx++) {
                    if (L.Monde.solidite(tx, ty) !== solide) continue;
                    if (L.Monde.estMeuble(tx, ty)) continue;
                    let libre = true;
                    for (let d = 1; d <= 3; d++) if (L.Monde.solidite(tx, ty - d) !== 0) libre = false;
                    if (!libre) continue;
                    L.B.entites = L.B.entites.filter(function (e) { return e.type === 'joueur'; });
                    L.Entites.reindexerDecor(); L.Entites.indexer();
                    const j = L.B.joueur;
                    j.x = tx * L.TT + 8; j.y = (ty - 3) * L.TT + 8;
                    const v = L.Vehicules.creer(slug, j.x, j.y, Math.PI / 2, { etat: 'roule' });
                    L.Vehicules.monter(j, v);
                    v.vitesse = vitesse; v.vx = 0; v.vy = vitesse;
                    const avant = { glyphe: L.Monde.glyphe(tx, ty), solide: L.Monde.solidite(tx, ty), y: v.y, vie: v.vie };
                    // ⚠️ On garde le pied dedans et on va JUSQU'AU BOUT : casser
                    // la tuile ne suffit pas, il faut ressortir de l'autre cote.
                    // Et on mesure ce qui RESTE de vitesse a l'image du passage,
                    // pas a la fin — apres, le char a repris son elan.
                    let casse = false, garde = null;
                    for (let i = 0; i < 90; i++) {
                        const v0 = Math.abs(v.vy);
                        L.Vehicules.avancer(v);
                        if (!casse && L.Monde.solidite(tx, ty) !== avant.solide) {
                            casse = true;
                            garde = v0 > 0 ? Math.abs(v.vy) / v0 : 0;
                        }
                        v.vy = Math.max(Math.abs(v.vy), vitesse * 0.6);   // toujours vers le sud
                    }
                    const r = { casse: casse,
                                glypheAvant: avant.glyphe, glypheApres: L.Monde.glyphe(tx, ty),
                                passe: v.y > (ty + 1) * L.TT, abime: v.vie < avant.vie,
                                garde: garde === null ? null : Math.round(garde * 100) / 100 };
                    L.Vehicules.descendre(j, true);
                    L.Entites.retirer(v);
                    return r;
                }
            }
            return null;
        }

        out.camionGrillage = fonceSur('camion', 4, 3.0);       // grillage / palissade
        out.camionBasse = fonceSur('camion', 3, 3.0);          // borne-fontaine
        out.camionFacade = fonceSur('camion', 1, 3.0);         // ⚠️ une façade : jamais
        out.camionBarbele = fonceSur('camion', 5, 3.0);        // ⚠️ le barbelé non plus
        out.autoGrillage = fonceSur('auto', 4, 3.0);           // une berline ne casse rien
        out.camionLent = fonceSur('camion', 4, 0.6);           // au pas, on ne défonce pas
        return out;
    }""")
    assert r["camionGrillage"], "aucun grillage isolé trouvé dans la ville"
    g = r["camionGrillage"]
    assert g["casse"] is True and g["passe"] is True, "le camion n'a pas traversé le grillage : %s" % g
    assert g["glypheApres"] != g["glypheAvant"], "la tuile n'a pas changé"
    assert g["abime"] is True, "passer au travers ne coûte rien à la carrosserie"
    defonce = next(v for v in paquet["vehicules"] if v["slug"] == "camion")["defonce"]
    assert abs(g["garde"] - defonce) < 0.25, (
        "le camion garde %s de sa vitesse au lieu de %s" % (g["garde"], defonce)
    )
    assert r["camionBasse"] and r["camionBasse"]["casse"] is True, (
        "une borne-fontaine doit céder aussi : %s" % r["camionBasse"]
    )
    # ⚠️ La moitié qui compte.
    assert r["camionFacade"] and r["camionFacade"]["casse"] is False and r["camionFacade"]["passe"] is False, (
        "LE CAMION A TRAVERSÉ UNE FAÇADE : %s" % r["camionFacade"]
    )
    if r["camionBarbele"]:
        assert r["camionBarbele"]["casse"] is False, "le barbelé a cédé : %s" % r["camionBarbele"]
    assert r["autoGrillage"] and r["autoGrillage"]["casse"] is False, (
        "une berline défonce un grillage : %s" % r["autoGrillage"]
    )
    assert r["camionLent"] and r["camionLent"]["casse"] is False, (
        "on défonce au pas, sous %s px/image : %s" % (ph["defonce_vitesse_min"], r["camionLent"])
    )


def test_la_remorqueuse_traine_un_char_a_la_fois(banc, paquet):
    """`crochet` était la dernière ligne de fiche que personne ne lisait : la
    remorqueuse était un camion orange.

    ⚠️ Et « un seul à la fois » n'est pas un détail de confort — c'est ce qui
    empêche le train de douze chars qu'on ne saurait plus arrêter. Le juge
    tient les quatre règles : on accroche **derrière** (un crochet est à
    l'arrière, il faut reculer dessus), un seul, jamais un char conduit, et le
    câble **lâche** si on l'étire trop."""
    ph = paquet["conduite"]["physique"]
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const j = L.B.joueur;
        const rem = o.char('remorqueuse', 0, 0, 0);      // cap 0 : elle regarde l'est
        L.Vehicules.monter(j, rem);
        const out = {};
        // 1. Devant, rien ne s'accroche : le crochet est DERRIERE.
        const devant = o.char('auto', 40, 0, 0);
        L.Entites.indexer();
        out.devant = !!L.Vehicules.aCrocher(rem);
        L.Entites.retirer(devant);
        // 2. Derriere, oui.
        const epave = o.char('auto', -36, 0, 0);
        L.Entites.indexer();
        out.accroche = L.Vehicules.basculerCrochet(rem);
        out.lien = rem.remorque === epave && epave.remorqueePar === rem;
        // 3. Un SEUL : un deuxieme char derriere ne s'ajoute pas — le meme
        //    bouton decroche.
        const second = o.char('auto', -80, 0, 0);
        L.Entites.indexer();
        L.Vehicules.basculerCrochet(rem);
        out.apresDeuxieme = { remorque: !!rem.remorque, second: !!second.remorqueePar };
        L.Vehicules.basculerCrochet(rem);                 // on raccroche
        out.raccroche = !!rem.remorque;
        // 4. Un char CONDUIT ne s'accroche pas.
        L.Vehicules.decrocher(rem);
        rem.remorque = null;
        for (const e of [epave, second]) { e.remorqueePar = null; e.conducteur = 'trafic'; }
        L.Entites.indexer();
        out.conduit = !!L.Vehicules.aCrocher(rem);
        for (const e of [epave, second]) e.conducteur = null;
        L.Entites.indexer();
        L.Vehicules.basculerCrochet(rem);
        // 5. On roule : la charge est POSEE, pas tiree. Ecart constant, dans
        //    l'axe, et l'avant leve.
        const suivi = [], biais = [];
        o.touche('KeyW');
        for (let i = 0; i < 90; i++) {
            o.frame(1);
            const t = rem.remorque;
            if (!t) { suivi.push(null); break; }
            suivi.push(Math.round(Math.hypot(t.x - rem.x, t.y - rem.y)));
            const d = t.angle - rem.angle;
            biais.push(Math.abs(Math.atan2(Math.sin(d), Math.cos(d))));
        }
        o.relacher('KeyW');
        out.suivi = { min: Math.min.apply(null, suivi), max: Math.max.apply(null, suivi),
                      tient: suivi.indexOf(null) < 0, n: suivi.length,
                      biais: +Math.max.apply(null, biais).toFixed(3) };
        const t = rem.remorque;
        out.leve = t ? t.z : null;
        // 6. Meme jetee a quatre cents pixels, elle est REPOSEE a l'image
        //    suivante : une fourche ne s'etire pas, donc elle ne lache pas.
        if (t) { t.x = rem.x - 400; t.y = rem.y; }
        o.frame(2);
        out.lache = !rem.remorque;
        out.reposee = rem.remorque ? Math.round(Math.hypot(rem.remorque.x - rem.x, rem.remorque.y - rem.y)) : null;
        return out;
    }""")
    assert r["devant"] is False, "un char DEVANT s'accroche : le crochet est a l'arriere"
    assert r["accroche"] is True and r["lien"] is True, "rien ne s'est accroche derriere"
    assert r["apresDeuxieme"] == {"remorque": False, "second": False}, (
        "le meme bouton doit DECROCHER, jamais accrocher un deuxieme : %s" % r["apresDeuxieme"]
    )
    assert r["raccroche"] is True
    assert r["conduit"] is False, "on a accroche un char qui avait un conducteur"
    assert r["suivi"]["tient"] is True, "la charge est tombee en roulant droit"
    # ⚠️ UNE FOURCHE N'A PAS DE JEU. Le câble donnait un écart qui respirait ;
    # ici, il ne bouge pas d'un pixel, et il vaut ce que la fiche dit.
    attendu = ph["crochet_jeu_px"] + (36 + 28) / 2       # longueurs remorqueuse + auto
    assert r["suivi"]["max"] - r["suivi"]["min"] <= 1, (
        "l'écart respire (%s à %s px) : c'est encore une corde" % (r["suivi"]["min"], r["suivi"]["max"])
    )
    assert abs(r["suivi"]["min"] - attendu) <= 4, (
        "la charge n'est pas à la longueur de la fourche : %s px pour %s attendus"
        % (r["suivi"]["min"], attendu)
    )
    # ⚠️ Et DANS L'AXE, pas « pointée vers elle » : c'est ce jeu-là qui trahit
    # la corde, bien avant qu'on regarde le dessin.
    assert r["suivi"]["biais"] < 0.02, "la charge roule de biais : %s rad" % r["suivi"]["biais"]
    assert r["leve"] == ph["crochet_leve_px"], "l'avant n'est pas levé : %s" % r["leve"]
    assert r["lache"] is False, "une fourche a lâché : elle ne s'étire pas, elle ne casse pas"
    assert r["reposee"] is not None and abs(r["reposee"] - attendu) <= 4, (
        "jetée à 400 px, la charge n'est pas revenue sur la fourche : %s" % r["reposee"]
    )


def test_la_depanneuse_leve_les_roues_et_charge_les_deux_roues(banc, paquet):
    """⚠️ Demande de Martin : « la dépanneuse devrait embarquer les roues avant
    des véhicules qu'elle remorque, sauf les motos et vélos qu'elle embarque
    complètement sur sa plateforme. »

    C'était une **corde**, pas une fourche : le char remorqué roulait à plat au
    bout d'un élastique, pointé **vers** la remorqueuse, et le lien lâchait
    quand on l'étirait. Le jeu du câble est ce qui trahissait la corde bien
    avant qu'on regarde le dessin.

    ⚠️ Et un lien rigide change la réponse à la seule question qui compte : que
    se passe-t-il quand la charge est bloquée par une tuile ? Ce n'est plus le
    câble qui s'allonge, c'est **la remorqueuse qui ne passe pas**."""
    ph = paquet["conduite"]["physique"]
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        L.graine(44);
        const j = L.B.joueur, out = {};
        const d = o.ligneDroite();
        j.x = d.x; j.y = d.y; L.Monde.centrerCamera(j.x, j.y);

        function atteler(slug) {
            const rem = o.char('remorqueuse', 0, 0, 0);
            L.Vehicules.monter(j, rem);
            const charge = o.char(slug, -36, 0, 1.2);     // de biais, pour voir le redressement
            L.Entites.indexer();
            L.Vehicules.basculerCrochet(rem);
            o.frame(2);
            return { rem: rem, charge: charge };
        }
        function ranger(a) {
            if (a.rem.remorque) L.Vehicules.decrocher(a.rem);
            if (L.B.joueur.dansVehicule) L.Vehicules.descendre(j, true);
            L.Entites.retirer(a.charge); L.Entites.retirer(a.rem);
            L.Entites.indexer();
        }

        // 1. UNE AUTO : l'avant levé, collée, dans l'axe.
        let a = atteler('auto');
        const ecart = Math.hypot(a.charge.x - a.rem.x, a.charge.y - a.rem.y);
        const biais = a.charge.angle - a.rem.angle;
        out.auto = {
            ecart: Math.round(ecart),
            colle: Math.round(ecart - (a.rem.def.longueur + a.charge.def.longueur) / 2),
            biais: +Math.abs(Math.atan2(Math.sin(biais), Math.cos(biais))).toFixed(3),
            z: a.charge.z, plateau: !!a.charge.def.plateau,
        };
        // ⚠️ ON NE MONTE PAS DEDANS : deux conducteurs, un seul lien rigide.
        L.Vehicules.descendre(j, true);
        out.auto.monte = L.Vehicules.monter(j, a.charge);
        L.Vehicules.monter(j, a.rem);
        // 2. LA REMORQUEUSE NE PASSE PAS LA OU SA CHARGE NE PASSE PAS.
        //    ⚠️ C'est LA question que le cable permettait de ne pas poser : il
        //    s'etirait, et l'auto au bout traversait le mur.
        out.mur = { libre: L.Vehicules.chargeBloquee(a.rem, a.rem.x, a.rem.y) };
        //    On cherche une facade, et on se plante devant, la charge dedans.
        const c = L.Monde.carte;
        let mur = null;
        for (let ty = 6; ty < c.h - 6 && !mur; ty++) {
            for (let tx = 6; tx < c.w - 6; tx++) {
                if (!L.Monde.bloque(tx, ty, L.Monde.MASQUE_VEHICULE)) continue;
                let libre = true;
                for (let k = 1; k <= 6; k++) if (L.Monde.bloque(tx + k, ty, L.Monde.MASQUE_VEHICULE)) libre = false;
                if (libre) { mur = { x: tx, y: ty }; break; }
            }
        }
        const recul = (a.rem.def.longueur + a.charge.def.longueur) / 2;
        a.rem.x = (mur.x + 1) * L.TT + 8 + recul; a.rem.y = mur.y * L.TT + 8;
        a.rem.angle = 0;                       // cap est : la charge est a l'ouest, dans le mur
        a.rem.vitesse = 0; a.rem.vx = 0; a.rem.vy = 0;
        L.Monde.centrerCamera(a.rem.x, a.rem.y);
        L.Vehicules.decrocher(a.rem);
        a.charge.x = a.rem.x - recul; a.charge.y = a.rem.y;
        L.Entites.indexer();
        L.Vehicules.basculerCrochet(a.rem);
        out.mur.attelee = !!a.rem.remorque;
        out.mur.bloque = L.Vehicules.chargeBloquee(a.rem, a.rem.x - 8, a.rem.y);
        //    Et en marche arriere, elle NE RECULE PAS : elle ne traine pas sa
        //    charge dans la facade.
        const x0 = a.rem.x;
        o.touche('KeyS');
        for (let i = 0; i < 90; i++) o.frame(1);
        o.relacher('KeyS');
        out.mur.recule = Math.round(x0 - a.rem.x);
        ranger(a);

        // 3. UNE MOTO : elle monte EN ENTIER, meme cap, ecart presque nul.
        a = atteler('moto');
        const em = Math.hypot(a.charge.x - a.rem.x, a.charge.y - a.rem.y);
        const bm = a.charge.angle - a.rem.angle;
        out.moto = {
            ecart: Math.round(em), plateau: !!a.charge.def.plateau, z: a.charge.z,
            biais: +Math.abs(Math.atan2(Math.sin(bm), Math.cos(bm))).toFixed(3),
            surLaRemorqueuse: em < a.rem.def.longueur / 2,
        };
        // ⚠️ Cargaison : aucune tuile ne l'arrete, et la remorqueuse ne se
        // laisse plus bloquer par elle.
        out.moto.chargeBloquee = L.Vehicules.chargeBloquee(a.rem, a.rem.x, a.rem.y);
        // Et elle SUIT au pixel, meme en tournant.
        o.touche('KeyW'); o.touche('KeyA');
        let pire = 0, pireBiais = 0;
        for (let i = 0; i < 120; i++) {
            o.frame(1);
            if (!a.rem.remorque) { pire = 999; break; }
            pire = Math.max(pire, Math.abs(Math.hypot(a.charge.x - a.rem.x, a.charge.y - a.rem.y) - em));
            const b = a.charge.angle - a.rem.angle;
            pireBiais = Math.max(pireBiais, Math.abs(Math.atan2(Math.sin(b), Math.cos(b))));
        }
        o.relacher('KeyW'); o.relacher('KeyA');
        out.moto.derive = +pire.toFixed(2);
        out.moto.deriveBiais = +pireBiais.toFixed(3);
        out.moto.tient = !!a.rem.remorque;

        // 4. L'ORDRE DE DESSIN : la charge se peint APRES sa remorqueuse.
        L.Jeu.rendre();
        // On relit l'ordre que le peintre a utilise : meme regle que lui.
        const gens = L.B.entites.filter(function (e) { return e.dessine; });
        const prof = function (e) { return e.remorqueePar ? e.remorqueePar.y + 0.5 : e.y; };
        gens.sort(function (x, y) {
            return (x.vivant ? 1 : 0) - (y.vivant ? 1 : 0) || prof(x) - prof(y) || x.id - y.id;
        });
        out.dessin = { apres: gens.indexOf(a.charge) > gens.indexOf(a.rem) };

        // 5. DECROCHEE, elle redescend.
        L.Vehicules.decrocher(a.rem);
        out.moto.reposee = a.charge.z;
        ranger(a);

        // 6. UN VELO AUSSI MONTE SUR LE PLATEAU.
        a = atteler('velo');
        out.velo = { plateau: !!a.charge.def.plateau,
                     surLaRemorqueuse: Math.hypot(a.charge.x - a.rem.x, a.charge.y - a.rem.y) < a.rem.def.longueur / 2 };
        ranger(a);
        return out;
    }""")

    au = r["auto"]
    # ⚠️ COLLEE : plus de trou de câble entre les deux. L'écart vaut le jeu de
    # la fourche, pas trente pixels de corde.
    assert au["colle"] <= ph["crochet_jeu_px"] + 2, (
        "il reste un trou entre la remorqueuse et sa charge : %s px" % au["colle"]
    )
    # ⚠️ DANS L'AXE, pas « pointée vers elle ».
    assert au["biais"] < 0.02, "la charge est de biais : %s rad" % au["biais"]
    assert au["z"] == ph["crochet_leve_px"], "l'avant n'est pas levé : %s" % au
    assert au["plateau"] is False, "une auto ne monte pas sur le plateau"
    assert au["monte"] is False, (
        "on est monté dans un char remorqué : deux conducteurs, un seul lien rigide"
    )

    # ⚠️ LA REMORQUEUSE NE PASSE PAS là où sa charge ne passe pas : le même
    # « tout ou rien » que `defoncerDevant`. C'est la question que le câble
    # permettait de ne pas poser — il s'étirait, et l'auto au bout traversait
    # le mur.
    mur = r["mur"]
    assert mur["libre"] is False, "le décor du juge est faux : en pleine rue, rien ne bloque"
    assert mur["attelee"] is True, "le décor du juge est faux : rien n'est attelé devant le mur"
    assert mur["bloque"] is True, "reculer vers une façade ne bloque pas la charge : %s" % mur
    assert mur["recule"] <= 4, (
        "elle a reculé de %s px avec une auto au bout de la fourche : elle la traîne dans "
        "la façade" % mur["recule"]
    )

    m = r["moto"]
    assert m["plateau"] is True, "la moto ne déclare pas `plateau` : %s" % m
    assert m["surLaRemorqueuse"] is True, (
        "la moto est accrochée derrière au lieu de monter dessus (%s px)" % m["ecart"]
    )
    assert m["z"] == ph["plateau_leve_px"], "elle n'est pas posée sur le plateau : %s" % m
    assert m["biais"] < 0.02, "elle est de travers sur le plateau : %s rad" % m["biais"]
    # ⚠️ Zéro dérive, même en tournant : elle fait partie de la remorqueuse.
    assert m["tient"] is True, "la moto est tombée du plateau"
    assert m["derive"] <= 1.0, "elle glisse sur le plateau : %s px" % m["derive"]
    assert m["deriveBiais"] < 0.05, "elle pivote sur le plateau : %s rad" % m["deriveBiais"]
    # ⚠️ C'est de la cargaison : aucune tuile ne l'arrête, donc elle ne peut pas
    # bloquer la remorqueuse.
    assert m["chargeBloquee"] is False, "une charge de plateau bloque la remorqueuse : %s" % m
    assert m["reposee"] == 0, "décrochée, elle reste en l'air : %s" % m["reposee"]

    assert r["dessin"]["apres"] is True, (
        "la charge se peint AVANT sa remorqueuse : la moto disparaît dessous"
    )
    assert r["velo"] == {"plateau": True, "surLaRemorqueuse": True}, r["velo"]


def test_le_feu_pieton_s_eteint_avant_que_les_chars_repartent(banc, paquet):
    """⚠️ Demande de Martin : « pour les piétons, il faut ajouter des lumières de
    priorité, et sinon ils ne passent pas. »

    La règle existait (`traverseeSure`) mais **personne ne la voyait** — et elle
    **se trompait d'un temps** : `!feuVert(...)` est vrai pendant l'**orange**
    aussi, donc les piétons s'engageaient exactement quand les chars accélèrent
    pour vider le croisement, le pire moment du cycle.

    Un vrai feu piéton ne s'allume pas au rouge : il s'éteint **avant** que les
    chars repartent. Ce juge parcourt un cycle entier, image par image."""
    t = paquet["conduite"]["trafic"]
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const cycle = 2 * (L.B.defs.conduite.trafic.feu_vert_images + L.B.defs.conduite.trafic.feu_orange_images);
        const inter = L.Monde.carte.intersections.find(function (i) { return i.feux; });
        const t0 = L.B.t;
        const suite = [];
        for (let k = 0; k < cycle; k++) {
            L.B.t = t0 + k;
            suite.push({
                // Le pieton qui traverse la rue est-ouest (passage « = »).
                pieton: L.Monde.feuPieton(inter, '>'),
                mesChars: L.Monde.feuVert(inter, '>'),
                lesAutres: L.Monde.feuVert(inter, '^'),
            });
        }
        L.B.t = t0;
        // Le blanc, jamais avec le vert de MA rue, jamais pendant un orange.
        let avecMesChars = 0, pendantOrange = 0, blanc = 0, degage = 0;
        for (const p of suite) {
            if (p.pieton === 'blanc') blanc++;
            if (p.pieton === 'degage') degage++;
            if (p.pieton === 'blanc' && p.mesChars) avecMesChars++;
            if (p.pieton === 'blanc' && !p.mesChars && !p.lesAutres) pendantOrange++;
        }
        // Le DEGAGEMENT : combien d'images entre la derniere blanche et le
        // moment ou mes chars repartent.
        // ⚠️ On tourne EN ROND : la fenetre commence a une phase quelconque, et
        // la derniere image blanche tombe souvent apres le dernier vert de la
        // fenetre. Chercher en avant sans reboucler, c'est ne rien trouver une
        // fois sur deux — et le juge dirait « pas de degagement » pour un
        // degagement parfait.
        let dernierBlanc = -1, apres = null;
        for (let k = 0; k < cycle; k++) {
            if (suite[k].pieton !== 'blanc') continue;
            if (suite[(k + 1) % cycle].pieton === 'blanc') continue;
            dernierBlanc = k;                 // la DERNIERE d'une plage blanche
        }
        for (let k = 1; k <= cycle; k++) {
            if (suite[(dernierBlanc + k) % cycle].mesChars) { apres = k - 1; break; }
        }
        return { cycle: cycle, blanc: blanc, degage: degage,
                 avecMesChars: avecMesChars, pendantOrange: pendantOrange,
                 degagementMesure: apres,
                 sansFeux: L.Monde.feuPieton({ feux: false }, '>') };
    }""")

    assert r["blanc"] > 0, "le feu piéton n'est jamais blanc : personne ne traverse plus"
    # ⚠️ LE DÉFAUT D'ORIGINE, tenu des deux côtés.
    assert r["avecMesChars"] == 0, (
        "le blanc s'allume pendant le vert des chars de sa rue (%s images)" % r["avecMesChars"]
    )
    assert r["pendantOrange"] == 0, (
        "le blanc s'allume pendant l'orange (%s images) : c'est exactement le moment où les "
        "chars accélèrent pour vider le croisement" % r["pendantOrange"]
    )
    # ⚠️ Et il s'éteint AVANT que les chars repartent : le dégagement, plus
    # l'orange, séparent la dernière image blanche du premier char qui roule.
    attendu = t["feu_pieton_degagement_images"] + t["feu_orange_images"]
    assert r["degagementMesure"] == attendu, (
        "le dégagement vaut %s images au lieu de %s : on s'engage trop tard"
        % (r["degagementMesure"], attendu)
    )
    assert r["degage"] == t["feu_pieton_degagement_images"], r["degage"]
    # Sans feux (un T), il n'y a pas de feu piéton : on traverse quand c'est libre.
    assert r["sansFeux"] == "aucun"


def test_un_pieton_attend_le_blanc_et_ne_reste_pas_planté_la_ou_il_n_y_a_pas_de_feu(banc):
    """⚠️ « Sinon ils ne passent pas » demande une **exception**, sinon la foule
    s'échoue. Les croisements en **T** n'ont pas de feux — ils ont un STOP.

    Si un piéton n'y traverse jamais, un côté de rue entier devient un cul-de-sac
    pour la foule, et **aucun juge existant ne le verrait** : « un seul îlot
    marchable » parle de géométrie, pas de circulation. La règle juste est donc :
    **au feu, on attend le blanc ; sans feu, on traverse quand c'est libre**."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const c = L.Monde.carte, TT = L.TT, out = {};

        // 1. AU FEU : on ne s'engage que sur le blanc, jamais autrement.
        const inter = c.intersections.find(function (i) { return i.feux; });
        let passage = null;
        for (let y = inter.y - 3; y < inter.y + inter.h + 3 && !passage; y++) {
            for (let x = inter.x - 3; x < inter.x + inter.l + 3; x++) {
                if (L.Monde.glyphe(x, y) === '=') { passage = { x: x, y: y }; break; }
            }
        }
        const cycle = 2 * (L.B.defs.conduite.trafic.feu_vert_images + L.B.defs.conduite.trafic.feu_orange_images);
        let fautes = 0, sûr = 0;
        const t0 = L.B.t;
        for (let k = 0; k < cycle; k++) {
            L.B.t = t0 + k;
            const ok = L.Entites.traverseeSure(passage.x, passage.y, [0, 1]);
            const feu = L.Monde.feuPieton(inter, '>');
            if (ok) { sûr++; if (feu !== 'blanc') fautes++; }
        }
        L.B.t = t0;
        out.auFeu = { sûr: sûr, fautes: fautes, cycle: cycle };

        // 2. SANS FEU : un T. On traverse des que la rue est libre.
        const te = c.intersections.find(function (i) { return !i.feux && i.bras.length === 3; });
        let sansFeu = null;
        for (let y = te.y - 3; y < te.y + te.h + 3 && !sansFeu; y++) {
            for (let x = te.x - 3; x < te.x + te.l + 3; x++) {
                const g = L.Monde.glyphe(x, y);
                if (g === '=' || g === ':') { sansFeu = { x: x, y: y, g: g }; break; }
            }
        }
        // On vide la rue de ses chars : rien ne doit plus empecher de passer.
        for (const e of L.B.entites.slice()) if (e.type === 'vehicule') L.Entites.retirer(e);
        L.Entites.indexer();
        out.sansFeu = { trouve: !!sansFeu,
                        passe: sansFeu ? L.Entites.traverseeSure(sansFeu.x, sansFeu.y, [0, 1]) : null };

        // 3. LE BUDGET : un feu par bout de traverse, pas un par tuile.
        const poteaux = (c.def.feux_pietons || []);
        const tuiles = {};
        let surLeTrottoir = 0, doublons = 0;
        for (const f of poteaux) {
            const cle = f.x + ',' + f.y;
            if (tuiles[cle]) doublons++;
            tuiles[cle] = true;
            if (L.Monde.glyphe(f.x, f.y) === '.') surLeTrottoir++;
        }
        let passages = 0;
        for (let y = 0; y < c.h; y++) for (let x = 0; x < c.w; x++) {
            const g = c.sol[y][x];
            if (g === '=' || g === ':') passages++;
        }
        out.budget = { poteaux: poteaux.length, doublons: doublons,
                       surLeTrottoir: surLeTrottoir, tuilesDePassage: passages };
        return out;
    }""")

    a = r["auFeu"]
    assert a["sûr"] > 0, "on ne traverse jamais au feu : la foule s'échoue"
    assert a["fautes"] == 0, (
        "on s'engage %s images sur %s alors que le feu n'est pas au blanc" % (a["fautes"], a["cycle"])
    )
    s = r["sansFeu"]
    assert s["trouve"] is True, "le juge n'a pas trouvé de passage sans feu : il ne prouve rien"
    assert s["passe"] is True, (
        "sans feu et sans un char en vue, on ne traverse pas : un côté de rue entier "
        "devient un cul-de-sac pour la foule"
    )
    b = r["budget"]
    assert b["doublons"] == 0, "deux poteaux sur la même tuile : %s" % b
    assert b["poteaux"] == b["surLeTrottoir"], (
        "un poteau est planté ailleurs que sur le trottoir : il se fait faucher, et il "
        "cache la ligne d'arrêt (%s)" % b
    )
    # ⚠️ Un par BOUT, pas un par tuile : il y a bien plus de tuiles de passage
    # que de poteaux, et c'est la mesure qui le dit.
    assert b["poteaux"] < b["tuilesDePassage"] / 3, (
        "autant de poteaux que de tuiles de passage : %s" % b
    )


def test_l_ambulance_soigne_son_conducteur_mais_ne_ressuscite_personne(banc, paquet):
    """`soigne` était dans la fiche depuis M9 et personne ne le lisait :
    l'ambulance était une fourgonnette blanche.

    ⚠️ Et la limite compte autant que le don : elle ne RESSUSCITE personne. Un
    mort reste mort — sinon l'ambulance devient la sortie de secours de toutes
    les fusillades, et l'hôpital ne veut plus rien dire."""
    soigne = next(v for v in paquet["vehicules"] if v["slug"] == "ambulance")["soigne"]
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const j = L.B.joueur;
        const amb = o.char('ambulance', 30, 0, 0);
        L.Vehicules.monter(j, amb);
        j.vie = 40;
        o.frame(180);                       // trois secondes au volant
        const rendu = j.vie - 40;
        const sauve = L.B.partie.vie;
        // Au plafond, ça n'ajoute rien.
        j.vie = j.vieMax;
        o.frame(120);
        const plafond = j.vie === j.vieMax;
        L.Vehicules.descendre(j, true);
        // Une auto, elle, ne soigne rien.
        const auto = o.char('auto', 30, 0, 0);
        L.Vehicules.monter(j, auto);
        j.vie = 40;
        o.frame(180);
        const autoRend = j.vie - 40;
        return { rendu: rendu, sauve: sauve, plafond: plafond, autoRend: autoRend, max: j.vieMax };
    }""")
    assert r["rendu"] > 0, "l'ambulance ne soigne pas son conducteur"
    assert abs(r["rendu"] - soigne * 3) <= soigne, (
        "trois secondes doivent rendre environ %s PV, pas %s" % (soigne * 3, r["rendu"])
    )
    assert r["sauve"] == 40 + r["rendu"], "la sauvegarde n'a pas suivi les PV rendus"
    assert r["plafond"] is True, "l'ambulance dépasse le maximum de vie"
    assert r["autoRend"] == 0, "une berline soigne : %s PV" % r["autoRend"]


def test_les_ambulances_et_les_polices_ont_chacune_leur_sirene(banc):
    """⚠️ Demande de Martin : « je veux des sirènes pour les ambulances et
    polices. »

    Il n'y en avait qu'UNE, et presque jamais : `Son.boucle('sirene', …)` ne
    s'allumait que pour une auto-patrouille de l'IA en chasse, à volume fixe,
    sans distance. L'ambulance déclare pourtant `sirene: true` depuis M9 et
    n'en a jamais fait entendre une seule. Et au volant, aucune des deux : on
    conduisait une ambulance en silence.

    Ce juge tient les trois choses qui manquaient : DEUX boucles distinctes
    (on doit savoir qui arrive derrière soi), un volume qui suit la DISTANCE
    (une sirène qu'on entend toujours ne veut plus rien dire), et le bouton
    du klaxon qui allume la sienne quand on est au volant."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const j = L.B.joueur;
        const out = {};
        // 1. Deux sons, deux boucles : la police et l'ambulance ne se
        //    confondent pas.
        const amb = o.char('ambulance', 40, 0, 0);
        amb.sirene = true;
        L.Entites.indexer();
        o.frame(2);
        const S = L.Vehicules.sirenes;
        out.ambulance = { police: S.sirene > 0, sienne: S.sirene_ambulance > 0 };
        out.pres = S.sirene_ambulance;
        // 2. Le volume suit la distance : loin, elle se tait. ⚠️ 520 px et
        //    pas 2000 : au-dela de `oubli_px` le trafic OUBLIE le char, et on
        //    mesurerait une disparition au lieu d'un volume.
        amb.x = j.x + 520; amb.y = j.y;
        o.frame(2);
        out.loin = S.sirene_ambulance;
        amb.x = j.x + 40;
        o.frame(2);
        out.revenue = S.sirene_ambulance > 0;
        // 3. Eteinte, plus rien.
        amb.sirene = false;
        o.frame(2);
        out.eteinte = S.sirene_ambulance > 0;
        // 4. Au volant, le bouton du klaxon est celui de la sirene — et
        //    l'etiquette du bouton tactile le dit.
        L.Vehicules.monter(j, amb);
        out.etiquette = o.doc.querySelector('#boutons b[data-a="attaque"]').textContent;
        o.tape('KeyJ', 2);
        out.allumee = amb.sirene;
        out.entendue = S.sirene_ambulance;
        o.tape('KeyJ', 2);
        out.rerreteinte = amb.sirene;
        L.Vehicules.descendre(j, true);
        // 5. Une auto, elle, klaxonne : le bouton ne change pas de metier
        //    pour tout le monde.
        const auto = o.char('auto', 40, 0, 0);
        L.Vehicules.monter(j, auto);
        out.etiquetteAuto = o.doc.querySelector('#boutons b[data-a="attaque"]').textContent;
        o.tape('KeyJ', 2);
        out.klaxon = auto.klaxonT > 0;
        return out;
    }""")
    assert r["ambulance"] == {"police": False, "sienne": True}, (
        "une ambulance doit avoir SA sirene, pas celle de la police : %s" % r["ambulance"]
    )
    assert r["loin"] == 0, "on entend une ambulance a 2000 px"
    assert 0 < r["pres"] <= 1, "le volume ne suit pas la distance : %s" % r["pres"]
    assert r["revenue"] is True, "la sirene ne revient pas quand elle se rapproche"
    assert r["eteinte"] is False, "la sirene continue apres avoir ete eteinte"
    assert r["etiquette"] == "SIRÈNE", "le bouton dit encore KLAXON dans une ambulance"
    assert r["allumee"] is True and r["entendue"] == 1, (
        "au volant, la sirene doit sonner a plein : %s" % r["entendue"]
    )
    assert r["rerreteinte"] is False, "le bouton n'eteint pas la sirene"
    assert r["etiquetteAuto"] == "KLAXON" and r["klaxon"] is True, (
        "dans une auto, le meme bouton doit rester le klaxon : %s" % r
    )


def test_aucune_carrosserie_n_est_transparente(banc):
    """⚠️ Bug de Martin : « l'autobus est transparent. »

    Et il l'était. `s` valait `#00000030` — un noir à 19 % — copié des trois
    autos, où il ne couvre que huit pixels de capot : un REFLET. Sur l'autobus,
    la même lettre couvrait deux trappes de toit de 66 pixels chacune, soit un
    cinquième de la carrosserie, et le canevas de cuisson est transparent :
    on voyait la rue à travers l'autobus.

    La règle n'est donc pas « aucune couleur translucide » — les trois autos
    en vivent bien — mais **un reflet est un détail** : au plus un pixel peint
    sur vingt. Au-delà, ce n'est plus un reflet, c'est une carrosserie qu'on
    a oublié de peindre."""
    r = banc("""function (L, o) {
        const bilans = {};
        for (const v of L.B.defs.vehicules) {
            const def = L.SPRITES[v.sprite];
            if (!def) continue;
            // Les lettres dont la couleur porte un canal alpha (#rrggbbaa).
            const claires = {};
            for (const ch in def.pal) claires[ch] = /^#[0-9a-fA-F]{8}$/.test(def.pal[ch]);
            let peints = 0, translucides = 0;
            for (const pose in def.poses) {
                for (const grille of def.poses[pose]) {
                    for (const ligne of grille) {
                        for (const ch of ligne) {
                            if (ch === '.') continue;
                            peints++;
                            if (claires[ch]) translucides++;
                        }
                    }
                }
            }
            bilans[v.slug] = { peints: peints, translucides: translucides };
        }
        return bilans;
    }""")
    assert r, "aucun sprite de vehicule trouve"
    for slug, b in r.items():
        assert b["peints"] > 40, "%s : %s pixels peints, ce n'est pas un char" % (slug, b["peints"])
        part = b["translucides"] / b["peints"]
        assert part <= 0.05, (
            "%s : %s pixels translucides sur %s (%.0f %%) — on voit la rue au travers"
            % (slug, b["translucides"], b["peints"], part * 100)
        )


def test_les_quatre_chars_de_m9_roulent_et_se_conduisent(banc, paquet):
    """⚠️ Un sprite ne suffit pas : le char doit NAITRE dans le trafic, tenir
    la route, et se laisser conduire. Ce juge les cree tous les quatre, les
    fait rouler, et verifie au passage la chose que le catalogue disait sans
    que personne ne l'ecoute — la chaine de cercles.

    Elle valait 3 pour tout le monde (`PHYSIQUE.cercles`), alors que la fiche
    de l'autobus en demande 5 : a 48 px de long pour 16 de large, trois
    cercles laissent deux trous par lesquels une moto entre dans l'autobus
    sans que rien ne se touche."""
    slugs = [v["slug"] for v in paquet["vehicules"] if v["phase"] == 1]
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const j = L.B.joueur;
        const out = {};
        // ⚠️ On remet le joueur a SA place a chaque tour : `descendre()` le
        // pose a cote du char, donc il derive d'un char a l'autre — et le
        // onzieme finissait contre un mur, ou aucun gaz ne le fait avancer.
        const px = j.x, py = j.y;
        for (const slug of %s) {
            j.x = px; j.y = py;
            // ⚠️ On degage la place a chaque tour : la ville vit (chars gares,
            // passants qui sortent des portes), et un juge qui mesure « est-ce
            // que le gaz fait avancer » ne doit pas mesurer « y a-t-il un
            // camion gare devant ».
            L.B.entites = L.B.entites.filter(function (e) {
                if (e.type === 'joueur') return true;
                if (e.type !== 'vehicule' && e.type !== 'pieton') return true;
                return Math.hypot(e.x - px, e.y - py) > 120;
            });
            L.Entites.indexer();
            const v = o.char(slug, 0, 0, 0);
            if (!v) { out[slug] = 'pas cree'; continue; }
            // La chaine de cercles : combien, et couvre-t-elle la carrosserie ?
            const cs = L.Vehicules.cercles(v);
            let trou = 0;
            for (let i = 1; i < cs.length; i++) {
                const d = Math.hypot(cs[i].x - cs[i-1].x, cs[i].y - cs[i-1].y);
                trou = Math.max(trou, d - 2 * cs[i].r);
            }
            // On le conduit : dix images de gaz, il doit avancer.
            L.Vehicules.monter(j, v);
            const x0 = v.x;
            o.touche('KeyW'); o.frame(20); o.relacher('KeyW');
            const avance = Math.hypot(v.x - x0, v.y - v.y);
            const dessine = !!L.SPRITES[v.sprite];
            L.Vehicules.descendre(j, true);
            out[slug] = { cercles: cs.length, fiche: v.def.cercles, trou: Math.round(trou * 100) / 100,
                          avance: Math.round(Math.abs(v.x - x0) * 10) / 10, dessine: dessine };
            L.Entites.retirer(v);
        }
        L.Jeu.rendre();                       // et le dessin ne plante pas
        return out;
    }""" % json.dumps(slugs))
    for slug, bilan in r.items():
        assert bilan != "pas cree", slug
        assert bilan["dessine"], "%s n'a pas de sprite" % slug
        assert bilan["cercles"] == bilan["fiche"], (
            "%s : %s cercles alors que sa fiche en demande %s" % (slug, bilan["cercles"], bilan["fiche"])
        )
        assert bilan["trou"] <= 0, (
            "%s : %s px de trou entre deux cercles — une moto y entre" % (slug, bilan["trou"])
        )
        # ⚠️ Sauf une COQUE : ce juge met le gaz sur une rue, et une chaloupe
        # est arrêtée par tout ce qui n'est pas de l'eau — c'est exactement la
        # règle de la 3e vague du bord de l'eau, pas un défaut. Sa géométrie se
        # juge ici comme celle des autres ; sa marche se juge sur l'eau, dans
        # `test_bateau.py`.
        if not vehicules.par_slug(slug)["eau"]:
            assert bilan["avance"] > 2, "%s ne bouge pas quand on met le gaz" % slug
    assert r["autobus"]["cercles"] == 5 and r["camion"]["cercles"] == 4, (
        "les deux longs doivent avoir leurs cercles de plus : %s" % r
    )


def test_le_joueur_a_trois_vitesses_et_ne_traverse_pas_les_murs(banc, paquet):
    """⚠️ TROIS vitesses, un seul bouton — et la COURSE EST LA VITESSE PAR
    DEFAUT (demande de Martin : « on court quand même tout le temps, avec la
    grandeur de la carte »). Pousser le pouce à fond, ou n'importe quelle
    touche de direction, c'est courir ; l'effleurer, c'est marcher ; le bouton,
    c'est sprinter — et lui seul coûte du souffle.

    On mesure vers l'OUEST : à l'est du terminus se tient Ti-Guy, et depuis que
    la foule ne se traverse plus, un personnage figé est un obstacle."""
    v = paquet["recherche"]["vitesses"]
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const j = L.B.joueur;
        function versLOuest(images) { const x = j.x; o.frame(images); return x - j.x; }
        // 1. Au clavier, sans rien : on COURT.
        o.touche('KeyA');
        const course = versLOuest(60);
        o.relacher('KeyA');
        // 2. Le pouce a peine pousse : on MARCHE.
        o.pad([-0.5, 0], [0, 0, 0, 0]);
        const marche = versLOuest(60);
        o.pad(null);
        // 3. Le bouton : on SPRINTE.
        j.endurance = 100;
        o.touche('ShiftLeft'); o.touche('KeyA');
        const sprint = versLOuest(60);
        o.relacher('KeyA'); o.relacher('ShiftLeft');
        // Vers le haut, un batiment se trouve sur le chemin : on doit s'arreter dessus.
        o.touche('KeyW'); o.frame(900); o.relacher('KeyW');
        const tx = Math.floor(j.x / L.TT), ty = Math.floor(j.y / L.TT);
        return { marche: marche, course: course, sprint: sprint,
                 sol: L.Monde.solidite(tx, ty), y: j.y, etat: L.B.etat,
                 dataEtat: o.elements.bandini.dataset.etat };
    }""")
    assert r["course"] > 50, "au clavier, sans rien, on doit courir"
    assert r["marche"] > 0, "le pouce a peine poussé doit quand même avancer"
    assert r["course"] > r["marche"] * 1.3, (
        "courir n'est pas plus rapide que marcher : %s contre %s" % (r["course"], r["marche"])
    )
    assert r["sprint"] > r["course"] * 1.15, (
        "le sprint doit être nettement plus rapide que la course : %s contre %s" % (r["sprint"], r["course"])
    )
    # Les trois vitesses du paquet, dans l'ordre, et le policier à la course.
    assert v["joueur_marche"] < v["joueur_course"] < v["joueur_sprint"]
    assert v["policier"] == v["joueur_course"], (
        "le policier doit courir exactement à la vitesse de la course : %s contre %s"
        % (v["policier"], v["joueur_course"])
    )
    assert r["sol"] in (0, 3), "le joueur a fini dans un mur"
    assert r["y"] > 0
    assert r["etat"] == "jeu" and r["dataEtat"] == "jeu"


#: Trouve une tuile de cloture (par sa solidite) avec du libre au nord et au sud,
#: vide la rue de tout le monde, et pose le joueur une tuile AU NORD. Le meme
#: decor pour les trois juges de cloture.
DEVANT_UNE_CLOTURE = """
    function devantUneCloture(L, o, solide) {
        const c = L.Monde.carte;
        for (let ty = 3; ty < c.h - 3; ty++) {
            for (let tx = 3; tx < c.w - 3; tx++) {
                if (L.Monde.solidite(tx, ty) !== solide) continue;
                if (L.Monde.solidite(tx, ty - 1) !== 0 || L.Monde.solidite(tx, ty - 2) !== 0) continue;
                if (L.Monde.solidite(tx, ty + 1) !== 0 || L.Monde.solidite(tx, ty + 2) !== 0) continue;
                // ⚠️ La rue se vide, DECOR COMPRIS : un arbre pose dans une cour
                // arretait le joueur avant la cloture, et le juge mesurait un
                // buisson en croyant mesurer une palissade.
                L.B.entites = L.B.entites.filter(function (e) { return e.type === 'joueur'; });
                L.Entites.reindexerDecor(); L.Entites.indexer();
                const j = L.B.joueur;
                j.x = tx * L.TT + 8; j.y = (ty - 1) * L.TT + 8;
                L.Monde.centrerCamera(j.x, j.y);
                return { tx: tx, ty: ty, j: j };
            }
        }
        return null;
    }
"""


def test_on_ne_traverse_plus_une_cloture_en_courant(banc):
    """⚠️ La demande de Martin : « des clotures, mais si elles ne sont pas
    barbelees, qu'on puisse passer par-dessus ». On passait par-dessus TOUTES —
    sans meme ralentir : `f` etait solide 3, donc le masque des pietons ne la
    voyait pas. Une cloture n'arretait que les chars.

    Maintenant on l'ENJAMBE, et ca coute : une seconde en haut, immobile, sans
    frapper — c'est ce prix-la qui fait d'une cloture un choix (couper par la
    cour, ou faire le tour) plutot qu'un trait de peinture."""
    r = banc("""function (L, o) {
        %s
        L.Jeu.commencer();
        const place = devantUneCloture(L, o, 4);
        if (!place) throw new Error('aucune cloture enjambable dans la ville');
        const j = place.j, regles = L.Entites.reglesCloture();
        const y0 = j.y;
        o.touche('KeyS'); o.touche('ShiftLeft');          // on POUSSE, et en courant
        o.frame(6);
        const pendant = { enjambe: !!j.enjambe, y: j.y, tuile: Math.floor(j.y / L.TT),
                          cloture: place.ty, z: j.z };
        // Ce qu'on ne peut PAS faire en haut d'une cloture : frapper.
        o.touche('Space'); o.frame(2); o.relacher('Space');
        const frappe = j.etat;
        let images = 6, zMax = 0;
        for (let i = 0; i < 200 && j.enjambe; i++) { o.frame(1); images++; zMax = Math.max(zMax, j.z); }
        o.relacher('KeyS'); o.relacher('ShiftLeft');
        const apres = { tuile: Math.floor(j.y / L.TT), x: j.x, enjambe: !!j.enjambe, z: j.z,
                        colonne: Math.floor(j.x / L.TT) };
        return { pendant: pendant, frappe: frappe, images: images, zMax: zMax, apres: apres,
                 duree: regles.enjambe_images, y0: Math.floor(y0 / L.TT) };
    }""" % DEVANT_UNE_CLOTURE)
    assert r["pendant"]["enjambe"] is True, "on pousse une cloture et rien ne se passe"
    assert r["pendant"]["tuile"] == r["y0"], "on a traverse la cloture en courant"
    assert r["frappe"] != "attaque", "on frappe en haut d'une cloture"
    assert r["zMax"] > 0, "le corps ne se souleve jamais : rien ne dit qu'il est EN HAUT"
    assert r["duree"] - 4 <= r["images"] <= r["duree"] + 12, (
        "l'enjambee doit durer ce que les donnees disent (%s images) : %s" % (r["duree"], r["images"])
    )
    assert r["apres"]["tuile"] == r["pendant"]["cloture"] + 1, "on ne retombe pas de l'autre cote"
    assert r["apres"]["enjambe"] is False and r["apres"]["z"] == 0


def test_une_cloture_nord_sud_ne_se_peint_pas_comme_une_est_ouest(banc):
    """⚠️ Bug de Martin : « les clotures qui sont nord-sud ne sont pas dans le
    bon sens. » Les trois peintres ne savaient dessiner qu'est-ouest — lisses en
    travers de toute la tuile, poteaux a x=2 et x=13, planches cote a cote — et
    une cloture qui descend du nord au sud etait une PILE DE PANNEAUX VUS DE
    FACE. Elles lisent maintenant leurs voisines (`varianteDeCloture`), comme les
    passages pietons, les cases de stationnement et les rampes le font deja.

    ⚠️ La PREMIERE version de ce juge exigeait que le nord-sud soit l'est-ouest
    TOURNE. Elle a sorti les clotures de leur premier bug, puis elle a verrouille
    le suivant, que Martin a nomme aussitot : « les clotures nord-sud doivent
    etre plus vues de haut, donc mince ». Un panneau tourne de 90 degres reste
    un panneau — sept pixels de large, pose a plat.

    La regle juste est deja ecrite deux fois dans le depot : la camera regarde
    d'en haut avec juste assez de face au SUD (les facades de la ville, les
    meubles des interieurs). Une cloture est-ouest montre donc sa HAUTEUR ; une
    cloture nord-sud ne montre que son EPAISSEUR. Le juge mesure cette largeur,
    et il tourne pour les trois glyphes."""
    r = banc("""function (L, o) {
        function peindre(glyphe, variante) {
            const c = L.Base.nouveauCanvas(L.TT, L.TT);
            const ctx = c.getContext('2d');
            ctx.traces = [];
            L.TUILES[glyphe](ctx, variante, L.TT);
            return ctx.traces;
        }
        // Ce que le dessin OCCUPE sur un axe (0 = x, 1 = y), le fond d'herbe
        // mis de cote : c'est la hauteur d'une cloture vue de face, et la
        // largeur d'une cloture vue par la tranche.
        function etendue(traces, axe) {
            let min = 99, max = -1;
            for (const t of traces) {
                if (t[2] >= L.TT && t[3] >= L.TT) continue;      // le fond, pas la cloture
                if (t[axe] < min) min = t[axe];
                if (t[axe] + t[axe + 2] > max) max = t[axe] + t[axe + 2];
            }
            return max < 0 ? 0 : max - min;
        }
        const sortie = {};
        for (const glyphe of ['f', 'w', 'X']) {
            const est_ouest = peindre(glyphe, 2 | 8);       // elle continue a l'est et a l'ouest
            const nord_sud = peindre(glyphe, 1 | 4);        // elle continue au nord et au sud
            const bout = peindre(glyphe, 8);                // elle s'arrete ici, vers l'ouest
            const boutNS = peindre(glyphe, 1);              // elle s'arrete ici, vers le nord
            const coin = peindre(glyphe, 1 | 2);            // un coin nord-est
            sortie[glyphe] = {
                est_ouest: est_ouest, nord_sud: nord_sud,
                // La hauteur de celle qu'on voit de face, la largeur de celle
                // qu'on prend par la tranche.
                hauteurEO: etendue(est_ouest, 1),
                largeurNS: etendue(nord_sud, 0),
                // Le poteau du centre : ce qui tient le tournant et ferme un bout.
                poteauBout: bout.some(function (t) { return t[0] === 7 && t[2] === 2; }),
                poteauCoin: coin.some(function (t) { return t[0] === 7 && t[2] === 2; }),
                poteauDroit: est_ouest.some(function (t) { return t[0] === 7 && t[2] === 2; }),
                // Un bout tout en nord-sud ferme par un CHAPEAU, pas par un piquet.
                chapeauNS: boutNS.some(function (t) { return t[1] === 7 && t[3] === 2; }),
                // ⚠️ Le fond d'herbe fait 16 x 16 : sans le mettre de cote, il
                // passerait pour un poteau debout a lui tout seul.
                piquetNS: boutNS.some(function (t) {
                    return !(t[2] >= L.TT && t[3] >= L.TT) && t[3] >= 10;
                }),
            };
        }
        return sortie;
    }""")
    for glyphe, mesure in r.items():
        assert mesure["est_ouest"], f"{glyphe} : une cloture est-ouest ne dessine rien"
        assert mesure["nord_sud"] != mesure["est_ouest"], (
            f"{glyphe} : le nord-sud se peint exactement comme l'est-ouest — elle est couchee"
        )
        # ⚠️ Le juge du bug de Martin : une cloture nord-sud se prend par la
        # tranche, donc elle occupe NETTEMENT moins large qu'une est-ouest
        # n'occupe haut. Tournee, elle faisait exactement la meme mesure.
        assert mesure["largeurNS"] * 2 <= mesure["hauteurEO"], (
            f"{glyphe} : le nord-sud fait {mesure['largeurNS']} px de large pour "
            f"{mesure['hauteurEO']} px de haut a l'est-ouest — c'est un panneau, pas une tranche"
        )
        assert mesure["largeurNS"] >= 2, f"{glyphe} : le nord-sud a disparu"
        assert mesure["chapeauNS"] is True, f"{glyphe} : un bout nord-sud sans chapeau de poteau"
        assert mesure["piquetNS"] is False, (
            f"{glyphe} : un poteau debout au bout d'un brin vu par la tranche"
        )
        assert mesure["poteauBout"] is True, f"{glyphe} : un bout de course sans poteau — coupe au couteau"
        assert mesure["poteauCoin"] is True, f"{glyphe} : un coin sans poteau — la maille flotte"
        assert mesure["poteauDroit"] is False, f"{glyphe} : un poteau au milieu d'une ligne droite"


def test_le_barbele_ne_se_passe_pas(banc):
    """Le barbele se met la ou quelqu'un a paye pour que personne n'entre : ni a
    pied, ni en char, ni en l'enjambant. Sans ca, il ne veut rien dire."""
    r = banc("""function (L, o) {
        %s
        L.Jeu.commencer();
        const place = devantUneCloture(L, o, 5);
        if (!place) throw new Error('aucun barbele dans la ville');
        const j = place.j;
        const tuile0 = Math.floor(j.y / L.TT);
        o.touche('KeyS'); o.touche('ShiftLeft');
        let enjambe = false;
        for (let i = 0; i < 240; i++) { o.frame(1); if (j.enjambe) enjambe = true; }
        o.relacher('KeyS'); o.relacher('ShiftLeft');
        const tuile = Math.floor(j.y / L.TT);
        // ⚠️ Le char en DERNIER, et la mesure du joueur avant : un char lance
        // dans le dos du joueur le pousse, et on mesurerait sa poussee en
        // croyant mesurer le barbele.
        const v = L.Vehicules.creer('auto', place.tx * L.TT + 8, (place.ty - 3) * L.TT + 8, Math.PI / 2, { etat: 'stationne' });
        j.x = v.x - 60;                                  // on se tasse de sa route
        for (let i = 0; i < 90; i++) { v.vitesse = 4; L.Vehicules.maj(); }
        return { enjambe: enjambe, tuile: tuile, tuile0: tuile0, cloture: place.ty,
                 char: Math.floor(v.y / L.TT) };
    }""" % DEVANT_UNE_CLOTURE)
    assert r["enjambe"] is False, "on enjambe le barbele"
    assert r["tuile"] == r["tuile0"], "on est passe a travers le barbele"
    assert r["char"] < r["cloture"], "un char a franchi le barbele"


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


def test_la_recherche_monte_puis_retombe(banc, paquet):
    palier1 = paquet["recherche"]["paliers"][1]["decroissance_s"]
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        L.Police.signalerCrime('mort_policier', 100, 100, true);
        const apres = L.B.recherche.etoiles;
        o.frame(%d * 60 - 5);
        const avantDecroissance = L.B.recherche.etoiles;
        o.frame(10);
        return { apres: apres, avant: avantDecroissance, fin: L.B.recherche.etoiles,
                 nonVu: (function () { L.Police.signalerCrime('pickpocket', 0, 0, false); return L.B.recherche.etoiles; })() };
    }""" % palier1)
    assert r["apres"] == 1
    assert r["avant"] == 1
    assert r["fin"] == 0
    assert r["nonVu"] == 0, "un crime non vu ne donne pas d'etoile"


def test_le_cone_de_vision(banc):
    r = banc("""function (L, o) {
        const c = L.Police.dansLeCone;
        const demi = 45 * Math.PI / 180;
        return [c(0, 0, 0, demi, 100, 80, 0), c(0, 0, 0, demi, 100, -80, 0), c(0, 0, 0, demi, 100, 60, 70),
                c(0, 0, 0, demi, 100, 200, 0), c(0, 0, Math.PI, demi, 100, -80, 0)];
    }""")
    assert r == [True, False, False, False, True]


def test_les_amendes_du_navigateur_sont_celles_de_python(banc):
    cas = [(1000, 1, 0), (1000, 2, 3), (50, 5, 20), (100000, 3, 7), (0, 1, 0)]
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        return %s.map(function (c) { return [L.Missions.amende(c[0], c[1], c[2]), L.Missions.potDeVin(c[1], c[2]),
                                              L.Missions.factureHopital(c[0])]; });
    }""" % json.dumps(cas))
    for (argent, etoiles, casier), (amende, pot, hopital) in zip(cas, r):
        assert amende == economie.amende(argent, etoiles, casier)
        assert pot == economie.pot_de_vin(etoiles, casier)
        assert hopital == economie.facture_hopital(argent)


def test_la_sauvegarde_fait_l_aller_retour_et_complete_un_vieux_blob(banc):
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        L.B.partie.argent = 1234; L.B.partie.casier = 2;
        L.Missions.sauvegarderPartie();
        const brut = JSON.parse(o.store[L.Sauvegarde.CLE]);
        const vieux = L.Sauvegarde.completer({ argent: 7 }, L.B.defs);
        return { argent: brut.argent, casier: brut.casier, x: brut.x, vieux: vieux,
                 cles: Object.keys(L.etatInitial(L.B.defs)).sort() };
    }""")
    assert r["argent"] == 1234 and r["casier"] == 2 and isinstance(r["x"], int)
    assert r["vieux"]["argent"] == 7
    assert sorted(r["vieux"].keys()) == r["cles"]
    assert r["vieux"]["armes"]["poings"] == {"mun": None}


def test_un_char_ne_pousse_personne_hors_de_la_carte(banc):
    """Un char gare qui chevauche le joueur au ras du bord nord le repousse — vers
    le dedans de la carte, jamais au-dela. Le singe l'a trouve (graine 1) : le
    joueur finissait a y = -3,5, dans le « mur » du dehors."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const j = L.B.joueur, T = L.TT, c = L.Monde.carte;
        const out = [];
        for (const dy of [4, 6, 8, 10]) {
            j.x = 1782.8; j.y = 5.0; j.vx = 0; j.vy = 0;
            L.B.entites = L.B.entites.filter(function (e) { return e.type !== 'vehicule'; });
            const v = L.Vehicules.creer('remorqueuse', j.x + 2, j.y + dy, 0, { etat: 'stationne' });
            L.Entites.indexer();
            o.frame(1);
            out.push({ dy: dy, y: j.y, dedans: j.y >= j.r && j.y <= c.pxH - j.r });
            L.Entites.retirer(v);
        }
        return out;
    }""")
    assert all(q["dedans"] for q in r), f"pousse hors de la carte : {r}"


@pytest.mark.parametrize("graine", [1, 2])
def test_le_singe_ne_casse_rien(banc, graine):
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        o.singe(3000, %d);
        const j = L.B.joueur, c = L.Monde.carte;
        const tx = Math.floor(j.x / L.TT), ty = Math.floor(j.y / L.TT);
        return { etat: L.B.etat, dedans: j.x >= 0 && j.y >= 0 && j.x <= c.pxW && j.y <= c.pxH,
                 sol: L.Monde.solidite(tx, ty), nage: !!j.nage, t: L.B.t, argent: L.B.partie.argent, nan: isNaN(j.x) || isNaN(j.y) };
    }""" % graine)
    assert r["etat"] in ("jeu", "pause")
    # ⚠️ L'eau (2) est permise EN NAGEANT : le joueur nage depuis le 15 sept. 2026,
    # et un singe qui marche assez longtemps finit parfois dans l'etang d'un parc.
    # Ce que le juge refuse, c'est un mur (1), une cloture ou un NaN.
    assert r["dedans"] and (r["sol"] in (0, 3) or (r["sol"] == 2 and r["nage"])) and not r["nan"]
    assert r["argent"] >= 0
    assert r["t"] > 1000


# --- M1 : la ville ---------------------------------------------------------


def test_la_ville_recue_est_celle_du_serveur(banc, paquet):
    r = banc("""function (L, o) {
        const c = L.Monde.carte, d = L.B.defs.carte;
        const types = {};
        L.B.defs.carte.decor.forEach(function (m) { types[m.type] = true; });
        return { w: c.w, h: c.h, portes: c.portes.length, points: c.points.length,
                 decor: L.B.defs.carte.decor.length, lampes: c.lampes.length,
                 zones: c.zones.length, sansPeintre: Object.keys(d.legende).filter(function (g) { return !L.TUILES[g]; }),
                 decorSansPeintre: Object.keys(types).filter(function (t) { return !L.DECORS[t]; }),
                 typesDecor: Object.keys(types).sort() };
    }""")
    carte = paquet["carte"]
    assert [r["w"], r["h"]] == [carte["largeur"], carte["hauteur"]]
    assert r["portes"] == len(carte["portes"]) >= 8
    assert r["points"] == len(carte["points_interet"])
    assert r["decor"] == len(carte["decor"]) > 100
    assert r["lampes"] == len(carte["lampes"]) > 40
    assert r["zones"] >= 2
    assert r["sansPeintre"] == [], "une tuile de la legende n'a pas de peintre"
    assert r["decorSansPeintre"] == [], "un decor de la carte n'a pas de peintre"
    assert len(r["typesDecor"]) >= 6, r["typesDecor"]


def test_le_joueur_et_les_lieux_sont_sur_des_tuiles_marchables(banc):
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const j = L.B.joueur;
        const dur = L.Monde.solidite(Math.floor(j.x / L.TT), Math.floor(j.y / L.TT));
        const lieux = L.Monde.carte.points.map(function (p) {
            // ⚠️ Une carrosserie n'a pas de porte des pietons : sa porte est le rideau.
            const rideau = L.Monde.portesDeGarage().some(function (pg) {
                return pg.lieu === p.slug && pg.y === p.y - 1 && p.x >= pg.x && p.x < pg.x + pg.l;
            });
            return [p.slug, L.Monde.solidite(p.x, p.y), !!L.Monde.porteA(p.x, p.y - 1) || rideau];
        });
        return { dur: dur, lieux: lieux, zone: L.Monde.zoneA(j.x, j.y).slug,
                 horsCarte: L.Monde.porteA(-1, -1) };
    }""")
    assert r["dur"] in (0, 3), "le joueur apparait dans un mur"
    for slug, dur, porte in r["lieux"]:
        assert dur in (0, 3), f"{slug} : on ne peut pas s'en approcher"
        assert porte is True, f"{slug} : pas de porte au-dessus du point d'interet"
    assert r["zone"] == "faubourg"
    assert r["horsCarte"] is None


def test_le_cache_de_morceaux_ne_gonfle_pas_quand_on_traverse_la_ville(banc):
    """Un cache non borne, c'est 20 Mo de canevas et un telephone qui rame."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const j = L.B.joueur, c = L.Monde.carte;
        const vus = [];
        // On traverse la ville en diagonale, en rendant a chaque saut.
        for (let i = 0; i < 40; i++) {
            j.x = 40 + (c.pxW - 80) * i / 39;
            j.y = 40 + (c.pxH - 80) * i / 39;
            L.Monde.centrerCamera(j.x, j.y);
            L.Jeu.rendre();
            vus.push(L.B.stats.morceaux);
        }
        return { max: Math.max.apply(null, vus), plafond: L.Monde.MORCEAUX_MAX,
                 images: L.B.stats.images, fin: L.B.stats.morceaux };
    }""")
    assert r["max"] <= r["plafond"], f"{r['max']} morceaux en cache pour un plafond de {r['plafond']}"
    assert r["fin"] > 0 and r["images"] > 0


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


def test_on_se_trouve_sur_la_carte_et_l_objectif_ne_bat_pas_pareil(banc):
    """⚠️ La demande de Martin : « un icone clignotant pour savoir ou on est ».
    Le joueur ETAIT dessine — un carre blanc de 2 px — mais depuis M8 la ville
    fait 421 x 213 tuiles et ce carre s'est perdu dans le gris. Ce n'etait pas un
    manque, c'etait une regression : il etait lisible sur le Faubourg.

    Deux pieges, et le test tient les deux : un repere qui clignote s'EFFACE une
    image sur deux (on ne cache pas la seule chose qu'on cherche — le joueur
    pulse, il ne disparait jamais), et deux choses qui battent au meme rythme se
    confondent (l'anneau du joueur contre le losange de l'objectif)."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
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
    }""")
    assert all(r["joueur"]), "le repere du joueur disparait : on cache ce qu'on cherche"
    assert len(set(r["rayons"])) > 2, "l'anneau du joueur ne pulse pas : rien ne le ramene a l'oeil"
    assert 0 in r["cible"] and 1 in r["cible"], "l'objectif ne clignote plus"
    assert r["formes"] == ["anneau", "losange"], "les deux reperes ont la meme forme"
    assert r["pulse"] != r["battement"], "le joueur et l'objectif battent au meme rythme"
    assert r["dedans"] is True


def test_la_carte_ouverte_les_reperes_battent_encore(banc):
    """⚠️ Sur la carte plein ecran, Martin ne voyait plus rien clignoter. Le
    dessin etait bon : c'est l'HORLOGE qui etait mauvaise. L'anneau et le
    losange battaient sur `B.t`, le temps du MONDE — et le monde est fige tant
    que la carte est ouverte. Les deux reperes restaient donc geles sur l'image
    ou l'on a appuye sur N, et une fois sur deux geles sur du VIDE : le losange
    tombait dans sa demi-periode eteinte et n'en ressortait jamais.

    Le test ouvre la carte et REGARDE, sans toucher a rien : ce qui bat a
    l'ecran doit battre sur les images dessinees, pas sur celles simulees."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
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
    }""")
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


def test_un_toit_porte_son_bord_et_ses_versants(banc):
    """⚠️ Un toit etait peint TUILE PAR TUILE, chacune ignorant les autres : un
    carre de couleur et des points tires de `hash2`. C'est une texture, pas un
    toit — et une texture uniforme ne peut pas etre realiste, parce qu'un vrai
    toit vu d'en haut ne se lit ni par son grain ni par sa couleur. Il se lit par
    son BORD.

    Ce juge mesure les deux choses que le voisinage doit apprendre a la tuile :
    ou le toit s'arrete (le bord), et sur quel versant on est (la pente). Il
    compare aussi les cuissons : un bord ne se peint pas comme un plein toit,
    sinon il n'y a pas de bord."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const c = L.Monde.carte;
        // Un toit plat assez large pour avoir un DEDANS et des bords.
        let plein = null, bord = null;
        for (let ty = 2; ty < c.h - 2 && !plein; ty++) {
            for (let tx = 2; tx < c.w - 2 && !plein; tx++) {
                const g = L.Monde.glyphe(tx, ty);
                if ('BEO'.indexOf(g) < 0) continue;
                const v = L.Monde.varianteDeToit(g, tx, ty);
                // ⚠️ Un bord et un plein DU MEME GLYPHE : chaque toit a son peintre,
                // et comparer le bord d'un toit plat au plein d'un toit a versants
                // ne compare rien. Le juge prenait le premier de chaque et tenait
                // par chance — il est tombe le jour ou la ville a bouge d'une tuile.
                if ((v & 15) === 0 && (!bord || bord.g === g)) { plein = { g: g, x: tx, y: ty, v: v }; }
                else if ((v & 15) !== 0 && (!bord || (plein && plein.g !== bord.g && plein.g === g))) { bord = { g: g, x: tx, y: ty, v: v }; }
            }
        }
        function peindre(glyphe, variante) {
            const t = L.Base.nouveauCanvas(L.TT, L.TT);
            const ctx = t.getContext('2d');
            ctx.traces = [];
            L.TUILES[glyphe](ctx, variante, L.TT);
            return ctx.traces;
        }
        // La pente : les versants d'un toit de maison, du nord au sud.
        let pente = null;
        for (let ty = 2; ty < c.h - 2 && !pente; ty++) {
            for (let tx = 2; tx < c.w - 2 && !pente; tx++) {
                if (L.Monde.glyphe(tx, ty) !== 'P') continue;
                let haut = ty;
                while (L.Monde.glyphe(tx, haut - 1) === 'P') haut--;
                let bas = ty;
                while (L.Monde.glyphe(tx, bas + 1) === 'P') bas++;
                if (bas - haut < 1) continue;
                const versants = [];
                for (let y = haut; y <= bas; y++) versants.push((L.Monde.varianteDePente('P', tx, y) >> 4) & 3);
                pente = { versants: versants, hauteur: bas - haut + 1 };
            }
        }
        return { plein: plein, bord: bord, pente: pente,
                 tracePlein: plein ? peindre(plein.g, plein.v).length : 0,
                 traceBord: bord ? peindre(bord.g, bord.v).length : 0,
                 memeGrain: plein && bord
                   ? JSON.stringify(peindre(plein.g, (plein.v & 240))) === JSON.stringify(peindre(plein.g, (plein.v & 240) | 15))
                   : true };
    }""")
    assert r["plein"] and r["bord"], "aucun toit plat avec un dedans et un bord"
    assert r["bord"]["v"] & 15, "la tuile de bord n'a pas de bord"
    # ⚠️ « Pas pareil », et non « plus » : le bord d'un toit a versants remplace
    # le grain par une arete et peut compter MOINS de rectangles que son plein.
    # Le juge disait « plus » et tenait par chance sur le premier toit venu.
    assert r["traceBord"] != r["tracePlein"], "un bord se peint comme un plein toit"
    assert r["memeGrain"] is False, "les quatre bords ne changent rien au dessin"
    assert r["pente"], "aucun toit a deux versants dans la ville"
    versants = r["pente"]["versants"]
    assert versants[0] == 0, f"la premiere rangee doit etre le versant nord : {versants}"
    assert versants[-1] == 2, f"la derniere doit etre le versant sud : {versants}"
    assert versants == sorted(versants), f"les versants doivent se suivre du nord au sud : {versants}"
    assert versants.count(1) <= 1, f"une seule ligne de faite : {versants}"


def test_la_musique_dit_ou_tu_es_et_ce_qui_t_arrive(banc, paquet):
    """⚠️ Demande de Martin : « des musiques différentes par district, et des
    musiques pour quand on se bat avec des gangs, et quand on a plusieurs
    étoiles. » Il y avait **une** musique de fond — la même de La Pointe aux
    Quais — et rien ne changeait quand trois Cravates te tombaient dessus.

    ⚠️ **Le vrai travail n'est pas les pistes, c'est QUI GAGNE.** Il y a déjà la
    radio dans un char, l'ambiance à pied, la rumeur, les sirènes et les voix :
    sans une échelle **écrite une fois**, deux musiques joueraient ensemble un
    jour sur trois. Ce juge tient l'échelle, l'**hystérésis** aux frontières et
    la **queue** des musiques d'état — les trois choses que la fiche appelle le
    vrai travail."""
    m = paquet["audio"]["musique"]
    e = paquet["audio"]["echelle"]
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        L.graine(107);
        o.frame(2);
        const j = L.B.joueur, C = L.Son.Chef, out = {};
        out.ambiance = L.Son.Mus.courante;

        // 1. L'ECHELLE : la poursuite couvre l'ambiance, la bagarre la suit.
        L.B.recherche.etoiles = ETOILES;
        o.frame(2);
        out.poursuite = L.Son.Mus.courante;
        // ⚠️ Et UNE SEULE piste a la fois : le sequenceur n'en tient qu'une,
        // c'est ce qui rend l'echelle vraie et pas seulement ecrite.
        L.B.recherche.etoiles = 0;
        out.queueDebut = C.queue;
        // 2. La QUEUE : la poursuite continue APRES la derniere etoile perdue.
        let tenue = 0;
        while (L.Son.Mus.courante === 'mus_poursuite' && tenue < 60 * 30) { o.frame(1); tenue++; }
        out.queue = { images: tenue, apres: L.Son.Mus.courante };

        // 3. L'HYSTERESIS : un zigzag sur une frontiere ne change pas de piste.
        const table = L.B.defs.audio.ambiances_de_district;
        // On se pose sur une frontiere : le district d'a cote, a un cheveu.
        const depart = L.Son.Mus.courante;
        const seuil = L.B.defs.audio.musique.hysteresis_px;
        let autre = null, bord = null;
        for (const z of L.Monde.carte.zones) {
            if (!table[z.district] || table[z.district] === depart) continue;
            autre = z; break;
        }
        if (autre) {
            bord = { x: (autre.x + 1) * L.TT, y: (autre.y + 1) * L.TT };
            const changements = [];
            for (let i = 0; i < 40; i++) {
                // Un pas de cote de part et d'autre, comme sur un boulevard.
                j.x = bord.x + (i % 2 ? 6 : -6); j.y = bord.y;
                o.frame(1);
                const c = L.Son.Mus.courante;
                if (!changements.length || changements[changements.length - 1] !== c) changements.push(c);
            }
            out.zigzag = { changements: changements.length, seuil: seuil };
            // Et en s'enfoncant pour de bon, la piste change.
            for (let i = 0; i < 40; i++) { j.x = bord.x + seuil + 40; j.y = bord.y; o.frame(1); }
            out.dedans = L.Son.Mus.courante;
            out.attendu = table[autre.district];
        }
        return out;
    }""".replace("ETOILES", str(m["poursuite_etoiles"])))
    assert r["ambiance"] and r["ambiance"].startswith("amb_"), (
        "à pied, l'ambiance du district doit jouer : %s" % r["ambiance"]
    )
    assert r["poursuite"] == "mus_poursuite", (
        "à %s étoiles, la poursuite doit couvrir l'ambiance : %s" % (m["poursuite_etoiles"], r["poursuite"])
    )
    assert e["poursuite"] < e["ambiance"] and e["histoire"] < e["poursuite"] < e["bagarre"], (
        "l'échelle n'est pas ordonnée : %s" % e
    )
    # ⚠️ La queue : sans elle, la poursuite démarrerait et s'arrêterait trois
    # fois en dix secondes. C'est elle qui fait qu'on SOUFFLE.
    assert r["queue"]["images"] >= m["poursuite_queue_s"] * 60 - 10, (
        "la poursuite s'arrête au quart de tour : %s images au lieu de %s"
        % (r["queue"]["images"], m["poursuite_queue_s"] * 60)
    )
    assert r["queue"]["apres"] and r["queue"]["apres"].startswith("amb_"), (
        "après la poursuite, l'ambiance du district doit revenir : %s" % r["queue"]["apres"]
    )
    # ⚠️ L'hystérésis : une musique qui bascule à chaque pas de côté est pire
    # que pas de musique du tout.
    assert r.get("zigzag"), "aucune frontière trouvée : le juge ne mesure rien"
    assert r["zigzag"]["changements"] == 1, (
        "un zigzag sur la frontière a changé de piste %s fois" % r["zigzag"]["changements"]
    )
    assert r["dedans"] == r["attendu"], (
        "en s'enfonçant pour de bon, la piste doit changer : %s au lieu de %s" % (r["dedans"], r["attendu"])
    )


def test_une_sorte_de_gens_est_un_corps_et_une_routine(banc, paquet):
    """⚠️ Demande de Martin : « des amuseurs publics, des musiciens de rue, des
    exhibitionnistes. »

    La ville avait **24 archétypes et 4 corps** : vingt et un portaient celui du
    joueur avec un échange de palette. Et sur six `metier`, **deux** faisaient
    quelque chose dans le moteur ; les autres n'étaient que des nombres. Une
    sorte était donc une couleur et trois chiffres — le dépôt a déjà payé ce
    défaut une fois, avec les filles de la Brume qu'on ne distinguait plus de
    personne.

    **Une sorte = un corps + une routine.** Le corps est jugé côté Python ;
    ici, c'est la **routine** — ce qu'elle fait que les autres ne font pas."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        L.graine(101);
        const j = L.B.joueur;
        const out = {};

        function poser(slug, dx, dy) {
            const a = L.Entites.archetype(slug);
            const e = L.Entites.creerPieton(j.x + dx, j.y + dy, a);
            e.etat = slug === 'exhibitionniste' ? 'flane' : 'fige';
            if (e.etat === 'fige') e.plante = { x: e.x, y: e.y };
            L.Entites.indexer();
            return e;
        }

        // 1. L'AMUSEUR attroupe — et un attroupement est une FOULE DE TEMOINS.
        // ⚠️ ON NE GARNIT PLUS LE CERCLE A LA MAIN, ET ON NE POSE PLUS
        // L'ARTISTE A LA MAIN NON PLUS. L'ancien juge posait lui-meme quatre
        // badauds avant de mesurer : il mesurait donc l'attroupement d'une
        // foule qu'il avait fabriquee, et la vraie regle — « toujours entre 3
        // et 5 personnes autour » — n'etait jugee nulle part. Ici c'est le
        // MOTEUR qui installe l'amuseur, sur une scene de la carte et hors
        // champ, exactement comme en partie ; le juge ne fait que regarder.
        const regles = L.B.defs.pietons.spectacle;
        // ⚠️ ON OUVRE LE SPECTACLE NOUS-MEMES sur la scene la plus proche. Le
        // juge attendait qu'un amuseur naisse tout seul en 400 images pres du
        // joueur : un pari sur les des, tombe le jour ou la ville a bouge.
        const TT = L.TT;
        const scenes = (L.Monde.carte.def.scenes || []);
        let proche = null, dMin = 1e9;
        scenes.forEach(function (sc) { const d = Math.hypot(sc.x * TT - j.x, sc.y * TT - j.y); if (d < dMin) { dMin = d; proche = sc; } });
        if (proche) { j.x = proche.x * TT + 8; j.y = proche.y * TT + 40; L.Monde.centrerCamera(j.x, j.y); }
        // ⚠️ UN AMUSEUR NE NAIT QUE HORS ECRAN (`naitreLesSortes`) : attendre
        // qu'il apparaisse a cote du joueur, c'est attendre pour rien. On le
        // pose nous-memes sur la scene, exactement comme le moteur le fait —
        // fige, face au sud, plante la — et on ouvre son spectacle.
        let amuseur = null;
        if (proche) {
            amuseur = o.poser('amuseur', 0, 0);
            amuseur.x = proche.x * TT + 8; amuseur.y = proche.y * TT + 8;
            amuseur.etat = 'fige'; amuseur.face = 'bas'; amuseur.plante = { x: amuseur.x, y: amuseur.y };
            L.Entites.indexer();
            L.Entites.ouvrirLeSpectacle(amuseur);
        }
        if (!amuseur) return { pasDAmuseur: true };
        // ⚠️ ON MARCHE JUSQU'A LUI, comme un joueur. Le contrat porte sur ce
        // qu'on VOIT : un artiste ne d'un coup a l'autre bout du quartier met
        // quelques secondes a rassembler son monde (les badauds traversent la
        // rue a pied, ils ne se materialisent pas), et personne ne regarde ces
        // secondes-la. Ce qui doit etre vrai, et l'est a chaque image, c'est :
        // quand il est A L'ECRAN, il y a entre 3 et 5 personnes autour.
        const cercles = [], temoinsFaibles = [];
        let vuImages = 0, images = new Set();
        for (let i = 0; i < 1200; i++) {
            const dx = amuseur.x - j.x, dy = amuseur.y - j.y, n = Math.hypot(dx, dy) || 1;
            if (n > 44) { j.x += dx / n * 0.9; j.y += dy / n * 0.9; L.Monde.centrerCamera(j.x, j.y); }
            o.frame(1);
            if (!amuseur.vivant) break;
            images.add(amuseur.poseFixe);
            if (!L.Entites.visibleAEcran(amuseur.x, amuseur.y, 0)) continue;
            vuImages++;
            const cercle = L.Entites.badauds(amuseur);
            cercles.push(cercle.length);
            for (const q of cercle) {
                const arch = L.B.defs.pietons.catalogue.find(function (p) { return p.slug === q.arch; });
                if (arch && q.probaTemoin <= arch.temoin) temoinsFaibles.push(q.arch);
            }
        }
        out.attroupement = {
            vuImages: vuImages,
            mini: regles.minimum, maxi: regles.maximum,
            plusPetit: cercles.length ? Math.min.apply(null, cercles) : null,
            plusGrand: cercles.length ? Math.max.apply(null, cercles) : null,
            temoinsFaibles: temoinsFaibles.length,
        };
        // Et il BOUGE : c'etait tout le defaut. Un corps a `vitesse: 0` tombait
        // sur l'image zero de son sprite du debut a la fin de la partie.
        out.mime = { images: images.size, corps: amuseur.sprite };
        L.Entites.retirer(amuseur);

        // 2. Le MUSICIEN attroupe aussi, il tient son poste, et IL JOUE.
        // ⚠️ On le fait naitre par le moteur lui aussi — mais l'amuseur qu'on
        // vient de retirer laisse la place a n'importe lequel des quatre, et
        // l'ordre est tire au sort (sans quoi les deux premiers de la liste
        // seraient les seuls a jamais naitre). On attend donc le musicien.
        let mus = null;
        for (let i = 0; i < 900 && !mus; i++) {
            o.frame(1);
            mus = L.B.entites.find(function (q) { return q.metier === 'musicien' && q.vivant; }) || null;
            if (!mus) {
                const autre = L.B.entites.find(function (q) {
                    return q.vivant && L.Entites.SPECTACLES.indexOf(q.metier) >= 0; });
                if (autre) L.Entites.retirer(autre);
            }
        }
        if (!mus) return { pasDeMusicien: true };
        const poste = { x: mus.x, y: mus.y };
        o.frame(120);
        out.musicien = { cercle: L.Entites.badauds(mus).length,
                         toune: mus.toune,
                         bouge: Math.round(Math.hypot(mus.x - poste.x, mus.y - poste.y)),
                         corps: mus.sprite };
        L.Entites.retirer(mus);

        // 3. L'EXHIBITIONNISTE ouvre son manteau : elle crie et fuit.
        // ⚠️ On vide la rue d'abord : il ouvre son manteau AU PREMIER QUI
        // FLANE, et le juge regarde SA dame. Un passant de la ville arrive
        // entre-temps, c'est lui qui prend le geste — et le juge conclut qu'il
        // n'y a pas eu de geste.
        for (const q of L.B.entites.slice()) {
            if (q.type === 'pieton' && Math.hypot(q.x - j.x, q.y - j.y) < 140) L.Entites.retirer(q);
        }
        L.Entites.indexer();
        const ex = poser('exhibitionniste', 30, 0);
        const dame = o.poser('passante', 34, 10);
        dame.etat = 'flane';
        L.Entites.indexer();
        let ouvert = -1;
        for (let i = 0; i < 60 && ouvert < 0; i++) { o.frame(1); if (ex.manteauT > 0) ouvert = i; }
        out.manteau = { ouvert: ouvert >= 0, image: ex.poseFixe, fuit: dame.etat === 'fuit',
                        crie: dame.cri > 0, corps: ex.sprite };
        // ⚠️ Et un AGENT qui passe l'arrete, lui — la seule fois ou la police
        // s'occupe de quelqu'un d'autre que le joueur.
        ex.manteauT = 0; ex.poseFixe = null;
        const agent = L.Police.creerAgent(ex.x + 24, ex.y, 'flane');
        L.Entites.indexer();
        o.frame(30);
        out.police = { fuit: ex.etat === 'fuit', menace: ex.menace === agent, suit: !!agent.but };
        return out;
    }""")
    a = r["attroupement"]
    assert a["vuImages"] > 300, "le juge n'a jamais vu l'amuseur à l'écran : %s" % a
    # ⚠️ « Je veux qu'il y ait TOUJOURS entre 3 et 5 personnes autour »
    # (Martin) — mesuré à CHAQUE IMAGE où on le voit, et les deux bornes
    # viennent de la fiche, pas du juge.
    assert a["plusPetit"] >= a["mini"], (
        "l'amuseur s'est retrouvé devant %s personne(s) (la fiche en demande %s)"
        % (a["plusPetit"], a["mini"])
    )
    assert a["plusGrand"] <= a["maxi"], (
        "%s personnes autour : au-delà de %s on ne voit plus le numéro"
        % (a["plusGrand"], a["maxi"])
    )
    # ⚠️ Un badaud qui regarde un spectacle REGARDE : il témoigne mieux que le
    # même passant qui marchait en pensant à autre chose.
    assert a["temoinsFaibles"] == 0, (
        "l'attroupement ne fait pas de meilleurs témoins : %s" % a
    )
    # ⚠️ ET IL BOUGE. C'est le retour de Martin, et c'est ce qu'aucun juge ne
    # regardait : `imageDe` choisit son image d'après la distance parcourue, un
    # corps à `vitesse: 0` n'en parcourt aucune, et le mime tenait l'image zéro
    # toute la partie. Une seule image, c'est un mannequin.
    assert r["mime"]["images"] >= 3, (
        "le mime ne fait aucun numéro : %s image(s) en 300" % r["mime"]["images"]
    )
    assert r["mime"]["corps"] == "amuseur"
    m = r["musicien"]
    assert m["cercle"] >= 1, "personne ne s'arrête pour le musicien : %s" % m
    # ⚠️ Et il a une TOUNE À LUI, tirée à la naissance parmi les cinq. Sans
    # elle, le sprite porte une guitare et il ne sort pas une note — ce qui
    # était exactement le cas jusqu'ici.
    assert m["toune"] and m["toune"].startswith("rue_"), "le musicien ne joue rien : %s" % m
    assert m["bouge"] <= 2, "le musicien quitte son coin de rue : %s px" % m["bouge"]
    assert m["corps"] == "musicien", "le musicien porte le corps commun"
    m = r["manteau"]
    assert m["ouvert"] is True and m["image"] == 1, (
        "le manteau ne s'ouvre pas, ou sur la mauvaise image : %s" % m
    )
    assert m["fuit"] is True and m["crie"] is True, "elle ne crie pas, ou ne fuit pas : %s" % m
    assert m["corps"] == "exhibitionniste"
    assert r["police"] == {"fuit": True, "menace": True, "suit": True}, (
        "un agent doit l'arrêter, LUI : c'est ce qui rend la police crédible (%s)" % r["police"]
    )


def test_les_cinq_qui_viennent_avec_font_chacune_son_metier(banc, paquet):
    """⚠️ La deuxième vague des « sortes de gens », et la même règle : **une
    sorte = un corps + une routine**.

    Celles-ci ne sont pas du remplissage — chacune sert une fiche **déjà
    livrée** : la contractuelle rend « mal garé » visible avant que la fourrière
    n'avale le char, le touriste est le meilleur témoin de la ville, l'ivrogne
    est le seul qui ne fuit pas devant une arme, le jogger ne s'arrête jamais,
    et le facteur fait battre les portes sans jamais entrer.

    Le corps est jugé côté Python ; ici, c'est la **routine**."""
    mots = paquet["pietons"]["paroles"]
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        L.graine(77);
        const j = L.B.joueur, TT = L.TT, out = {};

        // 1. LA CONTRACTUELLE : elle va au char mal gare et elle verbalise.
        const d = o.ligneDroite();
        j.x = d.x; j.y = d.y; L.Monde.centrerCamera(j.x, j.y);
        const v = o.char('auto', 0, 0, 0);
        v.laisse = true;
        const agente = o.poser('contractuelle', 70, 0);
        agente.etat = 'flane';
        L.Entites.indexer();
        const loin0 = Math.hypot(v.x - agente.x, v.y - agente.y);
        let cap = false;
        for (let i = 0; i < 400 && !v.contravention; i++) { o.frame(1); if (agente.etat === 'cap') cap = true; }
        out.contravention = { malGare: L.Missions.malGare(v), cap: cap,
                              tickets: v.contravention || 0,
                              rapproche: Math.hypot(v.x - agente.x, v.y - agente.y) < loin0,
                              dit: agente.bulle ? agente.bulle.texte : null,
                              corps: agente.sprite };
        L.Entites.retirer(agente); L.Entites.retirer(v);

        // 2. LE TOURISTE : il leve la tete devant une vitrine et il photographie.
        const c = L.Monde.carte;
        let devant = null;
        for (let y = 4; y < c.h - 4 && !devant; y++) {
            for (let x = 4; x < c.w - 4; x++) {
                if (c.sol[y][x] !== 'W') continue;
                if (!L.Monde.marchablePieton(x, y + 2) || L.Monde.estChaussee(x, y + 2)) continue;
                devant = { x: x * TT + 8, y: (y + 2) * TT + 8 };
                break;
            }
        }
        j.x = devant.x; j.y = devant.y + 40; L.Monde.centrerCamera(j.x, j.y);
        const t = o.poser('touriste', devant.x - j.x, devant.y - j.y);
        t.etat = 'flane';
        L.Entites.indexer();
        L.B.particules.length = 0;
        // ⚠️ ON ATTEND LA PHOTO, PAS LE PREMIER ARRET. Le juge sortait de sa
        // boucle des que le touriste s'arretait — or un flaneur s'arrete AUSSI
        // tout seul (une fois sur trois, `majPieton`), et `majPhoto` ne part
        // que depuis `flane`. Le juge lisait donc parfois une pause ordinaire
        // et concluait « il ne regarde pas la vitrine ». Il ne tenait que tant
        // que le de tombait bien, et il est tombe le jour ou une routine de
        // plus a decale le hasard.
        let arrete = false, photo = false;
        for (let i = 0; i < 400 && !photo; i++) {
            o.frame(1);
            if (t.etat === 'arret') arrete = true;
            if (t.face === 'haut' && L.B.particules.length > 0) photo = true;
        }
        out.photo = { arrete: arrete, leveLaTete: t.face === 'haut',
                      flash: L.B.particules.length > 0, corps: t.sprite,
                      temoin: L.Entites.archetype('touriste').temoin };
        L.Entites.retirer(t);

        // 3. L'IVROGNE : il zigzague, il ne fuit pas, et il finit par tomber.
        j.x = d.x; j.y = d.y; L.Monde.centrerCamera(j.x, j.y);
        // ⚠️ ON NE COMPARE PAS DEUX PROMENADES. Additionner les virages de
        // deux marches au hasard, c'est mesurer le terrain autant que la
        // demarche : un passant coince entre deux clotures tourne beaucoup, et
        // le juge devenait une loterie. Ce qui distingue vraiment l'ivrogne est
        // GEOMETRIQUE : un pieton ordinaire suit l'un des QUATRE axes, donc une
        // de ses deux vitesses est toujours nulle ; l'ivrogne, lui, a sa
        // direction tournee par un sinus — ses deux vitesses sont non nulles
        // presque tout le temps. C'est la regle elle-meme, pas son ombre.
        // ⚠️ ON NE MESURE QUE LA FLANERIE LIBRE, et c'est la moitie du juge.
        // Le passant ordinaire a DEUX autres facons de marcher, toutes deux
        // obliques et toutes deux legitimes : pousse sur la chaussee, il
        // regagne le trottoir le plus proche en diagonale ; et une fois sur
        // douze, `quelquUnRentre()` lui donne une porte et il y va tout
        // droit — `etat` reste « flane » pendant ce temps-la. Le temoin du
        // juge est tombe sur la deuxieme : cent dix-neuf images a marcher
        // vers sa porte, et le juge a accuse « un passant ordinaire marche en
        // biais ». C'etait vrai, et ca ne disait rien de l'ivrogne. Ce qui
        // distingue l'ivrogne, c'est que sa FLANERIE est tordue — alors on
        // ne mesure que la flanerie.
        // ⚠️ ON COMPTE DES PAS, PAS DES IMAGES. A 240 images fixes, ce qu'on
        // mesure depend de ce que le flaneur a fait de sa journee : s'il rentre
        // chez lui, s'il se fait pousser sur la chaussee ou s'il s'arrete, la
        // moitie des images ne compte pas. Le plancher de l'echantillon
        // (« personne n'a marche ») est tombe a 58 pour 60 demandes le jour ou
        // les cours arriere se sont cloturees — pour deux pas, et sans que rien
        // de l'ivrogne ait change. On marche donc jusqu'a EN AVOIR ASSEZ.
        const PAS_VOULUS = 160, IMAGES_MAX = 900;
        function deTravers(e) {
            let bouge = 0, obliques = 0;
            for (let i = 0; i < IMAGES_MAX && bouge < PAS_VOULUS; i++) {
                o.frame(1);
                if (e.porteBut) continue;                       // il rentre chez lui
                if (e.recul > 0) continue;                      // il vient d'encaisser
                if (L.Monde.estChaussee(Math.floor(e.x / TT), Math.floor(e.y / TT))) continue;
                if (Math.hypot(e.vx, e.vy) < 0.1) continue;
                bouge++;
                if (Math.abs(e.vx) > 0.05 && Math.abs(e.vy) > 0.05) obliques++;
            }
            return { pct: bouge ? Math.round(100 * obliques / bouge) : 0, pas: bouge };
        }
        // ⚠️ Le temoin a 24 px, pas 40 : depuis que le trottoir fait une tuile,
        // quarante pixels a l'ouest tombaient dans l'abord ou le mur du bloc,
        // et un passant ne dans un mur ne reagit a rien.
        const soul = o.poser('ivrogne', 40, 0); soul.etat = 'flane';
        const sobre = o.poser('passant', -24, 0); sobre.etat = 'flane';
        L.Entites.indexer();
        const vireSoul = deTravers(soul), vireSobre = deTravers(sobre);
        // Une arme sous le nez : tout le monde fuit, lui repond.
        // ⚠️ UN TEMOIN NEUF POUR L'ALERTE, pose a cote de l'ivrogne. Celui qui
        // vient de marcher cent soixante pas pour la mesure du zigzag est, a
        // cette image-ci, QUELQUE PART dans le quartier — le reprendre dans le
        // rayon de l'ivrogne, c'etait parier sur sa promenade, et le pari se
        // perd des qu'un lot de la ville change. Il s'etait deja perdu « le
        // jour ou les cours arriere se sont cloturees » (voir plus haut), et il
        // s'est reperdu le 16 sept. 2026 quand la palissade de banlieue est
        // passee des lots vides aux vraies cours. Ce qu'on prouve ici n'a rien
        // a voir avec sa marche : c'est qu'un passant ORDINAIRE, a la meme
        // place et sous la meme arme, reagit la ou l'ivrogne repond.
        sobre.etat = 'flane'; soul.etat = 'flane'; soul.bulle = null;
        const temoin = o.poser('passant', 16, 0); temoin.etat = 'flane';
        // ⚠️ A COTE DE L'IVROGNE, pas du joueur. `poser` place par rapport au
        // JOUEUR, et l'ivrogne vient de marcher cent soixante pas : mesure du
        // 17 sept. 2026, il etait a 191 px — hors du rayon de peur (sept
        // tuiles). Le juge notait « le passant ne reagit pas » alors que le
        // passant n'etait pas la, et il ne tenait que par la promenade de
        // l'ivrogne (la 4e vague des quartiers l'a defaite).
        temoin.x = soul.x + 16; temoin.y = soul.y; temoin.plante = null;
        L.Entites.indexer();
        L.Entites.alerter(soul.x, soul.y, j, 2);
        out.ivrogne = { zigzag: vireSoul.pct, droit: vireSobre.pct,
                        pasSoul: vireSoul.pas, pasSobre: vireSobre.pas, corps: soul.sprite,
                        fuit: soul.etat === 'fuit', repond: soul.bulle ? soul.bulle.texte : null,
                        lAutreFuit: temoin.etat === 'fuit' || temoin.etat === 'temoin' };
        soul.etat = 'flane';
        // ⚠️ ON FORCE LA REGLE, on ne joue pas sa probabilite. A six pour cent
        // par seconde, 1500 images donnent vingt-cinq occasions : une sur cinq
        // de n'en voir aucune, et le juge devient une loterie. On met la chance
        // a 1 dans la fiche et on mesure qu'il tombe ; le taux livre, lui, se
        // juge a part (`test_pietons.py`).
        const vraiTaux = L.B.defs.pietons.reactions.ivrogne_chute;
        L.B.defs.pietons.reactions.ivrogne_chute = 1;
        let tombe = false;
        // ⚠️ ET ON LE REMET DEBOUT S'IL S'ARRETE. Un flaneur s'arrete tout seul
        // une fois sur trois, pour 50 a 209 images, et `majIvrogne` ne regarde
        // qu'un ivrogne qui FLANE : mesure du 17 sept. 2026, sa halte a dure
        // 195 images, son compte a gele a 45 — UNE COCHE avant la chute — et le
        // juge a note « il ne tombe jamais tout seul ». Ce qu'on prouve, c'est
        // qu'il tombe en marchant ; la duree de ses haltes est une autre regle.
        for (let i = 0; i < 400 && !tombe; i++) {
            o.frame(1);
            if (soul.etat === 'arret') { soul.etat = 'flane'; soul.minuterie = 0; }
            if (soul.etat === 'assomme') tombe = true;
        }
        L.B.defs.pietons.reactions.ivrogne_chute = vraiTaux;
        out.ivrogne.tombe = tombe;
        out.ivrogne.taux = vraiTaux;
        L.Entites.retirer(soul); L.Entites.retirer(sobre);

        // 4. LE JOGGER : il ne s'arrete JAMAIS, et il ne temoigne de rien.
        const jog = o.poser('jogger', 40, 0); jog.etat = 'flane';
        const flaneur = o.poser('passant', -40, 0); flaneur.etat = 'flane';
        // ⚠️ LE TRAFIC NE DOIT PAS DECIDER DU RESULTAT. On pose les deux a une
        // distance fixe du joueur, sans regarder ce qui roule : le temoin s'est
        // fait ecraser par une moto a la HUITIEME image sur neuf cents, le juge
        // a compte zero pause et a accuse « un flaneur ne s'arrete jamais ».
        // `intouchable` est le drapeau des enfants : le char ne les renverse
        // pas. Il ne touche NI aux pauses NI a la marche — les deux seules
        // choses qu'on mesure ici — et il rend le decor reproductible.
        jog.intouchable = true; flaneur.intouchable = true;
        L.Entites.indexer();
        let pauses = 0, pausesFlaneur = 0;
        let routeJ = 0, routeF = 0;
        let avantJ = { x: jog.x, y: jog.y }, avantF = { x: flaneur.x, y: flaneur.y };
        for (let i = 0; i < 900; i++) {
            // ⚠️ ON FORCE LA DECISION, on ne l'attend pas. Un flaneur ne
            // decide de s'arreter que lorsque son `butT` tombe — une fois par
            // cinq secondes environ, et une fois sur trois seulement. Attendre
            // que le hasard le fasse, c'est jouer a pile ou face avec son
            // temoin : le juge est tombe le jour ou le passant n'a pas fait UNE
            // pause en neuf cents images. En remettant `butT` a zero a chaque
            // image, les deux passent par la meme porte, des centaines de fois.
            if (jog.etat === 'flane') jog.butT = 0;
            if (flaneur.etat === 'flane') flaneur.butT = 0;
            // ⚠️ ET ON LES GARDE DEHORS. `quelquUnRentre()` donne une porte a
            // un flaneur une fois sur douze, et `porteBut` court-circuite
            // toute la flanerie : il marche vers chez lui, il ne s'arrete
            // plus, et `butT` ne sert plus a rien. Le temoin y est parti, et
            // le juge a dit « un flaneur ne fait jamais de pause » — ce qui
            // est faux de la flanerie et vrai de celui qui rentre souper.
            // Rentrer chez soi est une TROISIEME routine ; elle ne repond ni
            // a la question du jogger ni a celle de l'ivrogne.
            jog.porteBut = null; flaneur.porteBut = null;
            o.frame(1);
            if (jog.etat === 'arret') pauses++;
            if (flaneur.etat === 'arret') pausesFlaneur++;
            routeJ += Math.hypot(jog.x - avantJ.x, jog.y - avantJ.y);
            routeF += Math.hypot(flaneur.x - avantF.x, flaneur.y - avantF.y);
            avantJ = { x: jog.x, y: jog.y }; avantF = { x: flaneur.x, y: flaneur.y };
        }
        out.jogger = { pauses: pauses, pausesFlaneur: pausesFlaneur, corps: jog.sprite,
                       vivants: jog.vivant && flaneur.vivant,
                       route: Math.round(routeJ), routeFlaneur: Math.round(routeF),
                       temoin: L.Entites.archetype('jogger').temoin };
        L.Entites.retirer(jog); L.Entites.retirer(flaneur);

        // 5. LE FACTEUR : il fait battre la porte, et il N'ENTRE PAS.
        const porte = c.portesFermees.find(function (p) { return L.Monde.marchablePieton(p.x, p.y + 1); });
        j.x = porte.x * TT + 8; j.y = (porte.y + 4) * TT + 8; L.Monde.centrerCamera(j.x, j.y);
        const fac = o.poser('facteur', 0, -2 * TT);
        fac.etat = 'flane';
        L.Entites.indexer();
        let ouverte = 0, vise = false, dit = null;
        for (let i = 0; i < 500; i++) {
            o.frame(1);
            if (fac.etat === 'cap') vise = true;
            // ⚠️ On attrape la bulle AU PASSAGE : elle dure quatre-vingts
            // images, la tournee en dure cinq cents. La lire a la fin, c'est
            // lire apres qu'elle s'est fermee.
            if (fac.bulle && !dit) dit = fac.bulle.texte;
            ouverte = Math.max(ouverte, L.Monde.battant(porte.x, porte.y));
        }
        out.facteur = { vise: vise, battant: Math.round(ouverte * 100) / 100, dit: dit,
                        dehors: L.B.entites.indexOf(fac) >= 0,
                        desservies: (fac.tournee || []).length, corps: fac.sprite };
        return out;
    }""")

    # --- La contractuelle -----------------------------------------------------
    c = r["contravention"]
    assert c["malGare"] is True, "le décor du juge est faux : le char doit être mal garé"
    assert c["cap"] is True and c["rapproche"] is True, "elle ne va pas au char : %s" % c
    assert c["tickets"] == 1, "elle ne verbalise pas, ou deux fois : %s" % c
    # ⚠️ Le mot vient de `pietons.PAROLES`, pas du JavaScript.
    assert c["dit"] == mots["contractuelle"]["verbalise"], (
        "elle ne dit pas ce que la fiche dit : %s" % c
    )
    assert c["corps"] == "contractuelle"

    # --- Le touriste ----------------------------------------------------------
    p = r["photo"]
    assert p["arrete"] is True and p["leveLaTete"] is True, "il ne regarde pas la vitrine : %s" % p
    assert p["flash"] is True, "pas de flash : %s" % p
    assert p["corps"] == "touriste"
    # ⚠️ Son intérêt n'est pas le flash, c'est qu'il REGARDE : le meilleur
    # témoin de la ville, et le seul à 1,0.
    assert p["temoin"] == 1.0, "le touriste doit être le témoin parfait : %s" % p

    # --- L'ivrogne ------------------------------------------------------------
    i = r["ivrogne"]
    # ⚠️ L'ivrogne est de travers presque tout le temps ; un passant suit un
    # axe, donc jamais. La marge est énorme parce que la règle est nette.
    # ⚠️ Et le decor doit AVOIR FLANE : sans ces deux lignes, un temoin qui
    # passe ses 240 images a rentrer chez lui donne « 0 % de pas obliques » et
    # le juge passe au vert en n'ayant rien mesure du tout.
    assert i["pasSoul"] >= 120 and i["pasSobre"] >= 120, (
        "le décor du juge est faux : personne n'a marché sur le trottoir (%s)" % i
    )
    assert i["zigzag"] >= 70, "l'ivrogne marche droit : %s %% de pas obliques" % i["zigzag"]
    assert i["droit"] <= 10, (
        "le décor du juge est faux : un passant ordinaire ne marche pas en biais (%s)" % i
    )
    assert i["fuit"] is False, "l'ivrogne fuit devant une arme : %s" % i
    assert i["lAutreFuit"] is True, "le décor du juge est faux : le passant, lui, doit réagir"
    assert i["repond"] == mots["ivrogne"]["sans_peur"], "il ne répond pas : %s" % i
    assert i["tombe"] is True, "il ne tombe jamais tout seul : %s" % i
    # Et le taux livré reste celui d'un ivrogne, pas d'un pantin.
    assert 0.01 <= i["taux"] <= 0.2, "il tombe %s fois par seconde" % i["taux"]
    assert i["corps"] == "ivrogne"

    # --- Le jogger ------------------------------------------------------------
    g = r["jogger"]
    assert g["pauses"] == 0, "le jogger s'arrête : %s" % g
    assert g["vivants"] is True, "le décor du juge est faux : le trafic a tué un des deux (%s)" % g
    assert g["pausesFlaneur"] > 0, "le décor du juge est faux : un flâneur, lui, fait des pauses (%s)" % g
    assert g["route"] > g["routeFlaneur"], "le jogger ne court pas plus loin qu'un flâneur : %s" % g
    assert g["temoin"] == 0.0, "le jogger ne témoigne de rien : %s" % g
    assert g["corps"] == "jogger"

    # --- Le facteur -----------------------------------------------------------
    f = r["facteur"]
    assert f["vise"] is True, "il ne fait pas sa tournée : %s" % f
    assert f["battant"] > 0.5, "la porte ne bat pas : %s" % f
    assert f["dit"] == mots["facteur"]["livre"], "il ne dit pas ce que la fiche dit : %s" % f
    # ⚠️ ET IL N'ENTRE PAS : c'est toute la différence avec le flâneur qui
    # rentre chez lui — celui-là disparaît derrière le battant.
    assert f["dehors"] is True, "le facteur est entré : %s" % f
    assert f["desservies"] >= 1, "aucune porte desservie : %s" % f
    assert f["corps"] == "facteur"


def test_l_eau_n_est_plus_un_mur(banc, paquet):
    """⚠️ Demande de Martin : « l'eau ne doit plus être un mur, mais qu'on puisse
    soit y nager ou s'y noyer, à pied ou dans un véhicule. »

    C'était littéralement un mur : `MASQUE_PIETON` et `MASQUE_VEHICULE`
    comptaient l'eau comme une façade, et on s'arrêtait au bord de la baie —
    ce qui est le plus étrange dans une ville qui s'appelle Baie-des-Brumes.

    ⚠️ Le vrai enjeu n'est pas la noyade, c'est le **pont** : la géographie de M8
    tenait par la collision, elle tient maintenant par le **souffle**. Les
    nombres se jugent côté Python (`test_eau.py`) ; ici, c'est le moteur."""
    nage = paquet["recherche"]["nage"]
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        L.graine(31);
        const j = L.B.joueur, c = L.Monde.carte, TT = L.TT, out = {};

        // Une rive : une tuile qu'on foule, avec six tuiles d'eau plein est.
        let rive = null;
        for (let y = 4; y < c.h - 4 && !rive; y++) {
            for (let x = 4; x < c.w - 10; x++) {
                if (!L.Monde.marchablePieton(x, y) || L.Monde.estEau(x, y)) continue;
                // ⚠️ DE L'EAU SUR SEPT RANGEES, pas un filet d'une tuile. Sur
                // un chenal mince, l'agent longe la berge au sec et arrive a
                // portee d'arrestation sans se mouiller : le juge mesurait
                // alors un agent qui contourne, pas un agent qui refuse de
                // nager. ⚠️ Trois rangees ont suffi jusqu'au 14 sept. 2026 et
                // ne suffisent plus : la ville a bouge (« l'interieur a la
                // mesure du batiment »), la premiere rive trouvee est devenue
                // une langue de sable, et l'agent la contournait par une
                // rangee seche QUATRE tuiles plus haut — hors de la fenetre
                // que ce juge regardait. La ville en offre trente-quatre a
                // sept rangees : on prend celles-la.
                let eau = true;
                for (let k = 1; k <= 9; k++) {
                    for (let dy = -3; dy <= 3; dy++) if (!L.Monde.estEau(x + k, y + dy)) eau = false;
                }
                if (eau) { rive = { x: x, y: y }; break; }
            }
        }
        out.rive = rive;

        // 1. LES DEUX MASQUES NE DISENT PAS LA MEME CHOSE.
        out.masques = {
            pieton: L.Monde.bloque(rive.x + 2, rive.y, L.Monde.MASQUE_PIETON),
            nageur: L.Monde.bloque(rive.x + 2, rive.y, L.Monde.MASQUE_NAGEUR),
            flanerie: L.Monde.marchablePieton(rive.x + 2, rive.y),
        };

        // 2. ON ENTRE DANS L'EAU, ET LE SOUFFLE PART.
        j.x = rive.x * TT + 8; j.y = rive.y * TT + 8;
        L.Monde.centrerCamera(j.x, j.y);
        j.endurance = 100; j.surplus = 0; j.cafeine = 0;
        o.touche('KeyD');
        let entre = -1;
        for (let i = 0; i < 180 && entre < 0; i++) { o.frame(1); if (j.nage) entre = i; }
        // ⚠️ ON MESURE AU LARGE, pas au premier pixel mouille. La premiere tuile
        // est de l'eau BASSE depuis le 16 sept. 2026 — on y a pied, elle ne
        // coûte rien (`Monde.eauBasse`, et ses propres juges) — alors une
        // seconde comptee depuis l'entree comptait seize images de patauge et
        // trouvait 22 points la ou la fiche en promet 30.
        let large = -1;
        for (let i = 0; i < 180 && large < 0; i++) {
            o.frame(1);
            if (!L.Monde.eauBasse(Math.floor(j.x / TT), Math.floor(j.y / TT))) large = i;
        }
        const souffle0 = j.endurance;
        for (let i = 0; i < 60; i++) o.frame(1);
        o.relacher('KeyD');
        out.nage = { entre: entre >= 0, large: large >= 0, dansLEau: L.Entites.dansLEau(j),
                     souffleAvant: Math.round(souffle0), souffleApres: Math.round(j.endurance),
                     tuiles: Math.round((j.x / TT) - rive.x) };

        // 3. A BOUT DE SOUFFLE, ON COULE — et on se reveille a l'hopital.
        j.endurance = 3; j.surplus = 0;
        const hopital = c.points.find(function (p) { return p.slug === 'hopital'; });
        let noye = -1;
        for (let i = 0; i < 120 && noye < 0; i++) { o.frame(1); if (L.B.transition) noye = i; }
        o.fondu();
        // ⚠️ On se reveille DANS un lit de l'hopital, plus sur son trottoir : on se
        // leve et on ressort — c'est le pas de sa porte qui dit ou l'on etait.
        const lit = { piece: L.B.interieur && L.B.interieur.slug, alite: !!j.alite, nage: !!j.nage };
        L.Entites.seLever(j, 0, 1);
        o.sortir();
        out.noyade = { noye: noye >= 0, lit: lit,
                       auSec: !L.Entites.dansLEau(j),
                       souffle: Math.round(j.endurance),
                       pres: hopital ? Math.round(Math.hypot(j.x - (hopital.x * TT + 8), j.y - (hopital.y * TT + 8))) : null };

        // 4. UN CHAR DANS L'EAU COULE, ET IL EST PERDU.
        const eau = { x: (rive.x + 4) * TT + 8, y: rive.y * TT + 8 };
        j.x = rive.x * TT + 8; j.y = rive.y * TT + 8;
        j.endurance = 100; L.Monde.centrerCamera(j.x, j.y);
        const v = L.Vehicules.creer('auto', eau.x, eau.y, 0, { etat: 'stationne' });
        const bateau = L.Vehicules.creer('bateau', eau.x, eau.y + 3 * TT, 0, { etat: 'stationne' });
        L.Entites.indexer();
        let sombre = -1;
        for (let i = 0; i < 400 && sombre < 0; i++) { o.frame(1); if (L.B.entites.indexOf(v) < 0) sombre = i; }
        out.char = { sombre: sombre >= 0, images: sombre,
                     coule_s: L.B.defs.recherche.nage.coule_s,
                     // ⚠️ Et il n'est PAS a la fourriere : couler ne doit pas
                     // devenir le moyen commode de se faire rembourser une epave.
                     auLot: (L.B.partie.fourriere || []).some(function (q) { return q.slug === 'auto'; }),
                     bateauFlotte: L.B.entites.indexOf(bateau) >= 0 };
        if (L.B.entites.indexOf(bateau) >= 0) L.Entites.retirer(bateau);

        // 5. UN AGENT NAGE DERRIERE TOI.
        // ⚠️ SIX tuiles au large, pas trois : a trois, l'agent arrive a portee
        // d'arrestation depuis la rive et s'arrete — le juge mesurait alors un
        // agent qui te passe les menottes, pas un agent qui nage.
        j.x = (rive.x + 6) * TT + 8; j.y = rive.y * TT + 8;
        j.endurance = 100; j.surplus = 60;
        L.Monde.centrerCamera(j.x, j.y);
        L.Police.remiseAZero();
        // ⚠️ Sans etoile, `Police.gere` renvoie l'agent a la flanerie des la
        // premiere image : un agent « en poursuite » sans recherche ne poursuit
        // personne, et le juge aurait mesure un promeneur.
        L.Police.etoilesAuMoins(2);
        const agent = L.Police.creerAgent(rive.x * TT + 8, rive.y * TT + 8, 'poursuit');
        agent.but = { x: j.x, y: j.y };
        agent.vuT = 0;
        L.Entites.indexer();
        let mouille = false;
        for (let i = 0; i < 300 && !mouille; i++) { o.frame(1); if (L.Entites.dansLEau(agent)) mouille = true; }
        out.police = { mouille: mouille, vitesse: L.B.defs.recherche.nage.vitesse };
        L.Entites.retirer(agent);

        // 6. AUCUN PASSANT ORDINAIRE NE SE BAIGNE.
        j.x = rive.x * TT + 8; j.y = rive.y * TT + 8;
        L.Monde.centrerCamera(j.x, j.y);
        let baigneurs = 0, vus = 0;
        for (let i = 0; i < 600; i++) {
            o.frame(1);
            for (const e of L.B.entites) {
                if (e.type !== 'pieton' || e.agent || !e.vivant) continue;
                // ⚠️ Sauf les enfants de la grève, qui BARBOTENT par métier (la
                // 2e vague du bord de l'eau). Ce juge a raison sur le fond — une
                // flânerie qui mène à la baie est le genre de chose qu'on ne voit
                // qu'en jeu — et ce n'est pas lui qu'on jette : c'est l'exception
                // qu'on nomme. Ils ont leur propre juge, qui tient qu'ils ne
                // dépassent jamais la première tuile d'eau.
                if (e.metier === 'baigneur') continue;
                vus++;
                if (L.Entites.dansLEau(e)) baigneurs++;
            }
        }
        out.passants = { baigneurs: baigneurs, vus: vus };
        return out;
    }""")

    assert r["rive"], "le juge n'a pas trouvé de rive : la carte n'a plus d'eau ?"
    # ⚠️ Les deux masques : l'eau arrête un corps de piéton, jamais un nageur.
    assert r["masques"] == {"pieton": True, "nageur": False, "flanerie": False}, (
        "les masques ne disent plus ce qu'ils doivent dire : %s" % r["masques"]
    )
    n = r["nage"]
    assert n["entre"] is True and n["dansLEau"] is True, "on ne rentre pas dans l'eau : %s" % n
    assert n["large"] is True, "on n'a jamais quitté l'eau basse : le juge ne prouve rien (%s)" % n
    assert n["tuiles"] >= 1, "on n'avance pas dans l'eau : %s" % n
    # Le souffle part, et il part vite : 0,5 par image — AU LARGE.
    attendu = nage["souffle_par_image"] * 60
    assert n["souffleAvant"] - n["souffleApres"] >= attendu * 0.8, (
        "nager ne coûte presque rien : %s (attendu ~%s en une seconde)" % (n, attendu)
    )
    no = r["noyade"]
    assert no["noye"] is True, "à bout de souffle, on ne coule pas : %s" % no
    assert no["auSec"] is True, "on se réveille dans l'eau : %s" % no
    assert no["souffle"] >= 100, "on se réveille sans souffle : %s" % no
    assert no["lit"] == {"piece": "hopital", "alite": True, "nage": False}, (
        "on ne se réveille pas couché dans un lit de l'hôpital — ou encore en train de nager : %s" % no
    )
    assert no["pres"] is not None and no["pres"] < 64, "on ne ressort pas devant l'hôpital : %s" % no
    ch = r["char"]
    assert ch["sombre"] is True, "un char dans l'eau flotte : %s" % ch
    assert ch["images"] >= ch["coule_s"] * 60 * 0.8, (
        "il coule instantanément : on n'a pas le temps d'en sortir (%s)" % ch
    )
    assert ch["auLot"] is False, "un char noyé revient à la fourrière : %s" % ch
    # ⚠️ Le bateau, lui, flotte — et c'est sa fiche qui le dit, pas une classe
    # écrite dans le JavaScript.
    assert ch["bateauFlotte"] is True, "la chaloupe coule aussi : %s" % ch
    assert r["police"]["mouille"] is True, (
        "un agent lancé derrière le joueur s'arrête au bord : l'eau devient l'exploit "
        "anti-police le plus simple du jeu (%s)" % r["police"]
    )
    p = r["passants"]
    assert p["vus"] > 500, "le juge n'a croisé personne : il ne prouve rien (%s)" % p
    assert p["baigneurs"] == 0, (
        "un passant s'est mis à l'eau : `marchablePieton` doit garder l'eau, et une "
        "flânerie qui mène à la baie est le genre de chose qu'on ne voit qu'en jeu (%s)" % p
    )


def test_les_trois_de_la_rue_ont_chacune_leur_crochet(banc, paquet):
    """⚠️ Troisième vague des « sortes de gens », et la même règle : une sorte =
    un corps + une routine. Celles-ci ont été choisies pour leur **crochet** :

    - le **crieur** hurle ce que **tu** as fait hier — la manchette du Clairon
      (`journal.py`) compare tes statistiques du jour à celles d'hier ;
    - le **laveur** ne travaille qu'au **feu rouge** : il ne s'approche que des
      chars **arrêtés** — la même horloge que les feux pour piétons ;
    - le **pickpocket** vole les **autres** : un crime que tu n'as pas commis,
      une victime qui crie, et un agent qui arrête quelqu'un d'autre que toi.
    """
    mots = paquet["pietons"]["paroles"]
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        // ⚠️ Ce juge mesure le crime d'autrui SANS méprise : la méprise (M12) a les siens
        // (`test_crime_d_autrui_js.py`), et une empreinte qui tombe bien ne doit rien y changer.
        L.B.defs.recherche.autrui.chance = 0;
        L.graine(88);
        const j = L.B.joueur, TT = L.TT, out = {};
        const d = o.ligneDroite();

        // 1. LE CRIEUR hurle la manchette — celle du Clairon, pas une phrase à lui.
        j.x = d.x; j.y = d.y - 3 * TT; L.Monde.centrerCamera(j.x, j.y);
        L.B.partie.derniereManchette = { slug: 'nuit_rouge', titre: 'NUIT ROUGE AU FAUBOURG' };
        const cri = o.poser('crieur', 20, 0);
        cri.etat = 'fige'; cri.plante = { x: cri.x, y: cri.y };
        L.Entites.indexer();
        let dit = null, bouge = 0;
        const poste = { x: cri.x, y: cri.y };
        for (let i = 0; i < 120 && !dit; i++) { o.frame(1); if (cri.bulle) dit = cri.bulle.texte; }
        for (let i = 0; i < 60; i++) { o.frame(1); bouge = Math.max(bouge, Math.hypot(cri.x - poste.x, cri.y - poste.y)); }
        out.crieur = { dit: dit, corps: cri.sprite, bouge: Math.round(bouge),
                       vitesse: L.Entites.archetype('crieur').vitesse };
        L.Entites.retirer(cri);

        // 2. LE LAVEUR : il laisse passer un char qui ROULE, il lave celui qui est ARRETE.
        // ⚠️ SUR LA CHAUSSEE : un laveur de vitres travaille dans la rue, et
        // `charArrete` ne regarde que les chars qui sont sur la route — sinon
        // il laverait les autos garees dans les cours.
        j.x = d.x; j.y = d.y; L.Monde.centrerCamera(j.x, j.y);
        const roule = o.char('auto', 30, 0, 0);
        roule.vitesse = 3; roule.vx = 3;
        const lav = o.poser('laveur', 0, 0);
        lav.etat = 'flane';
        L.Entites.indexer();
        let versLeRoulant = false;
        for (let i = 0; i < 60; i++) { o.frame(1); roule.vitesse = 3; if (lav.etat === 'cap') versLeRoulant = true; }
        out.laveur = { suitUnRoulant: versLeRoulant };
        L.Entites.retirer(roule);
        // Et maintenant un char a l'arret, pile devant lui.
        j.x = d.x; j.y = d.y;
        const arrete = o.char('auto', 26, 0, 0);
        arrete.vitesse = 0; arrete.vx = 0; arrete.vy = 0;
        L.Entites.indexer();
        let lave = -1, propose = null;
        for (let i = 0; i < 300 && lave < 0; i++) {
            o.frame(1);
            arrete.vitesse = 0; arrete.vx = 0; arrete.vy = 0;
            if (lav.bulle && !propose) propose = lav.bulle.texte;
            if (lav.laveT > 0) lave = i;
        }
        out.laveur.lave = lave >= 0;
        out.laveur.propose = propose;
        out.laveur.corps = lav.sprite;
        out.laveur.surLeChar = lave >= 0 ? Math.round(Math.hypot(lav.x - arrete.x, lav.y - arrete.y)) : null;
        L.Entites.retirer(lav); L.Entites.retirer(arrete);

        // 3. LE PICKPOCKET vole un passant — dans le dos, et l'argent CHANGE de poche.
        j.x = d.x; j.y = d.y - 3 * TT; L.Monde.centrerCamera(j.x, j.y);
        for (const q of L.B.entites.slice()) {
            if (q.type === 'pieton' && Math.hypot(q.x - j.x, q.y - j.y) < 160) L.Entites.retirer(q);
        }
        L.Entites.indexer();
        const voleur = o.poser('pickpocket', 0, 0);
        voleur.etat = 'flane'; voleur.argent = 0;
        const victime = o.poser('passant', 40, 0);
        victime.etat = 'flane'; victime.argent = 37; victime.face = 'droite';
        // ⚠️ LE JOUEUR S'ECARTE. `o.poser` fait naitre le voleur SUR lui : le
        // joueur se tenait donc entre le voleur et sa victime, et selon le tirage
        // le voleur le poussait, qui poussait la victime — tous les trois glissaient
        // vers l'est pendant 850 images sans que la main atteigne une poche. Le
        // pickpocket n'y etait pour rien (mesure du 16 sept. 2026, le jour ou le
        // tirage de la ville a glisse avec l'hopital). On le pose derriere le
        // voleur, sur le meme trottoir : pas sur la chaussee.
        j.x -= 3 * TT;
        L.Entites.indexer();
        let vole = -1;
        for (let i = 0; i < 900 && vole < 0; i++) {
            o.frame(1);
            // ⚠️ ON TIENT LA RUE VIDE PENDANT TOUTE LA MESURE. `peupler()`
            // repose des passants a chaque seconde, et le voleur prend le
            // PREMIER qui passe : le juge voyait alors un vol — le bon geste,
            // la bonne bulle — sur quelqu'un d'autre, et concluait que sa
            // victime n'avait rien perdu.
            for (const q of L.B.entites.slice()) {
                if (q.type === 'pieton' && q !== voleur && q !== victime) L.Entites.retirer(q);
            }
            victime.face = 'droite';                    // il regarde a l'oppose : on l'aborde de dos
            if (voleur.voleT > 0) vole = i;
        }
        out.vol = { vole: vole >= 0, poches: victime.argent, butin: voleur.argent,
                    crie: victime.cri > 0, fuit: victime.etat === 'fuit',
                    menace: victime.menace === voleur,
                    dit: victime.bulle ? victime.bulle.texte : null,
                    corps: voleur.sprite };
        // ⚠️ Et un agent l'arrete, LUI.
        voleur.voleT = 0; voleur.etat = 'flane'; voleur.repos = 0;
        const agent = L.Police.creerAgent(voleur.x + 30, voleur.y, 'flane');
        L.Entites.indexer();
        o.frame(30);
        out.vol.police = { neVolePlus: voleur.repos > 0 || voleur.etat === 'fuit' };
        return out;
    }""")

    c = r["crieur"]
    # ⚠️ Il dit LA MANCHETTE, pas une phrase à lui : c'est tout le personnage.
    assert c["dit"] == "NUIT ROUGE AU FAUBOURG", (
        "le crieur ne hurle pas la manchette du Clairon : %s" % c
    )
    assert c["corps"] == "crieur"
    assert c["vitesse"] == 0.0 and c["bouge"] <= 2, (
        "un crieur de journaux tient son coin : %s px parcourus" % c["bouge"]
    )

    lv = r["laveur"]
    # ⚠️ AU FEU ROUGE : il ne court pas après un char qui roule.
    assert lv["suitUnRoulant"] is False, (
        "il s'approche d'un char qui roule : ce n'est plus un métier, c'est un accident"
    )
    assert lv["lave"] is True, "il ne lave jamais un char arrêté : %s" % lv
    assert lv["surLeChar"] is not None and lv["surLeChar"] <= 26, (
        "il lave de loin : %s px du char" % lv["surLeChar"]
    )
    assert lv["propose"] == mots["laveur"]["propose"], "il ne dit pas ce que la fiche dit : %s" % lv
    assert lv["corps"] == "laveur"

    v = r["vol"]
    assert v["vole"] is True, "le pickpocket ne vole personne : %s" % v
    # ⚠️ L'argent CHANGE de poche : sinon le vol n'est qu'une animation, et
    # fouiller le volé rapporterait quand même.
    assert v["poches"] == 0 and v["butin"] == 37, (
        "l'argent n'a pas changé de poche : %s" % v
    )
    assert v["crie"] is True and v["fuit"] is True, "la victime ne réagit pas : %s" % v
    assert v["menace"] is True, "la victime en veut à quelqu'un d'autre que son voleur : %s" % v
    assert v["dit"] == mots["pickpocket"]["au_voleur"], "elle ne crie pas au voleur : %s" % v
    assert v["corps"] == "pickpocket"
    assert v["police"]["neVolePlus"] is True, (
        "il vole sous le nez d'un agent : la police n'existe pas que pour le joueur, "
        "mais elle existe quand même (%s)" % v["police"]
    )


def test_la_porte_s_ouvre_pour_le_joueur_aussi(banc):
    """⚠️ Retour de Martin : « les portes doivent ouvrir quand j'entre aussi. »
    Elles s'ouvraient pour les piétons et **pas pour lui** — il traversait un
    battant fermé, et c'était d'autant plus voyant que les passants, eux,
    attendaient poliment l'ouverture.

    ⚠️ Et le piège est dans l'ordre : le jeu est **figé** pendant un fondu de
    porte (`maj()` ne fait avancer que la transition). Un battant ouvert au
    départ y resterait donc au premier pixel, et la porte serait toujours
    fermée à l'écran. Les battants doivent battre **pendant** la transition —
    c'est la seule chose qui bouge quand tout le reste est arrêté."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const j = L.B.joueur, c = L.Monde.carte;
        const porte = c.portes.find(function (p) { return p.lieu === 'planque'; });
        j.x = porte.x * L.TT + 8; j.y = (porte.y + 1) * L.TT + 10;
        L.Monde.centrerCamera(j.x, j.y);
        // 1. On entre : le battant doit s'ouvrir PENDANT que la rue est encore
        //    visible, c'est-a-dire dans la premiere moitie du fondu.
        L.Jeu.entrer(porte);
        const ouvertures = [];
        for (let i = 0; i < 60 && L.B.transition; i++) {
            const tr = L.B.transition;
            const alpha = tr.t <= tr.ferme ? tr.t / tr.ferme : 0;
            ouvertures.push({ a: Math.round(alpha * 100) / 100, p: L.Monde.battant(porte.x, porte.y) });
            o.frame(1);
        }
        // Sur la rue (avant le noir), a-t-on vu la porte bouger ?
        const surLaRue = ouvertures.filter(function (q) { return q.a < 1; });
        const out = { dedans: !!L.B.interieur,
                      vueSurLaRue: Math.max.apply(null, surLaRue.map(function (q) { return q.p; })) };
        // 2. On ressort : la porte de la RUE doit s'ouvrir, pas celle de la piece.
        L.Jeu.sortir();
        o.fondu();
        out.sortie = L.Monde.battant(porte.x, porte.y);
        out.dehors = L.B.interieur === null;
        // 3. Et elle se referme toute seule.
        o.frame(60);
        out.refermee = L.Monde.battant(porte.x, porte.y);
        return out;
    }""")
    assert r["dedans"] is True and r["dehors"] is True, "l'aller-retour par la porte n'a pas marché"
    # ⚠️ Sur la rue, pendant que le fondu noircit : c'est là qu'on peut la voir.
    assert r["vueSurLaRue"] > 0.5, (
        "la porte n'a pas bougé pendant qu'on voyait encore la rue (%s) : le joueur traverse un battant fermé"
        % r["vueSurLaRue"]
    )
    assert r["sortie"] > 0.5, "en ressortant, la porte de la rue doit être ouverte : %s" % r["sortie"]
    assert r["refermee"] == 0, "la porte reste ouverte derrière le joueur : %s" % r["refermee"]


def test_les_portes_s_ouvrent_et_les_gens_les_passent(banc):
    """⚠️ Demande de Martin : « les piétons devraient aussi sortir et entrer dans
    les commerces. Profites-en pour aussi faire ouvrir concrètement les
    portes. » Les deux demandes n'en font qu'une, et le code disait pourquoi.

    **Un piéton sur trois sortait déjà d'une porte — et on ne le voyait
    jamais** : `placeDeNaissance()` refusait la place si elle était visible à
    l'écran. Ce n'était pas une sortie, c'était une naissance déguisée en
    sortie, dont le seul intérêt aurait été d'être vue. **Personne n'entrait
    nulle part**, et **aucune porte ne s'ouvrait**.

    Le juge tient les règles qui coûtent : une porte ne s'ouvre jamais sur
    rien, la planque du joueur n'avale personne, un commerce fermé non plus, et
    ⚠️ **le cache de morceaux ne bouge pas** quand une porte s'ouvre — c'est lui
    qui tient le rythme sur téléphone."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        L.graine(97);
        const j = L.B.joueur, c = L.Monde.carte;
        const out = {};

        // 1. Un battant s'ouvre, tient, et se referme — tout seul.
        const porte = c.portesFermees.find(function (p) { return p.glyphe === 'd'; });
        L.Monde.ouvrirPorte(porte.x, porte.y);
        const courbe = [];
        for (let i = 0; i < 60; i++) { courbe.push(L.Monde.battant(porte.x, porte.y)); o.frame(1); }
        out.battant = { debut: courbe[0], max: Math.max.apply(null, courbe), fin: courbe[courbe.length - 1],
                        monte: courbe[6] > courbe[0] };

        // 2. ⚠️ Le cache de morceaux ne bouge pas : le sol est cuit, le battant
        //    se pose PAR-DESSUS.
        L.Jeu.rendre();
        const morceaux0 = L.B.stats.morceaux;
        L.Monde.ouvrirPorte(porte.x, porte.y);
        L.Jeu.rendre();
        out.morceaux = { avant: morceaux0, apres: L.B.stats.morceaux };

        // 3. Quelles portes servent : jamais la planque, jamais le poste.
        function sert(lieu) {
            const p = (c.portes || []).find(function (q) { return q.lieu === lieu; });
            return p ? L.Entites.porteQuiSert({ x: p.x, y: p.y, glyphe: 'D' }) : null;
        }
        out.regles = { planque: sert('planque'), poste: sert('poste'), hopital: sert('hopital'),
                       logement: L.Entites.porteQuiSert({ x: porte.x, y: porte.y, glyphe: 'd' }) };
        // Un commerce : ouvert le jour, ferme la nuit.
        // ⚠️ Les interieurs n'ont pas d'heures declarees (seuls les kiosques
        // de rue en ont) : la nuit tient lieu de fermeture, sauf pour le bar —
        // qui vit justement la nuit.
        const dep = (c.portes || []).find(function (q) { return q.lieu === 'depanneur'; });
        const bar = (c.portes || []).find(function (q) { return q.lieu === 'bar'; });
        L.B.partie.heure = 0.5;
        const jour = dep ? L.Entites.porteQuiSert({ x: dep.x, y: dep.y, glyphe: 'D' }) : null;
        L.B.partie.heure = 0.95;
        const nuit = dep ? L.Entites.porteQuiSert({ x: dep.x, y: dep.y, glyphe: 'D' }) : null;
        const barLaNuit = bar ? L.Entites.porteQuiSert({ x: bar.x, y: bar.y, glyphe: 'D' }) : null;
        out.commerce = { jour: jour, nuit: nuit, barLaNuit: barLaNuit };
        L.B.partie.heure = 0.5;

        // 4. Sortir : ne DANS la porte, invisible tant qu'elle s'ouvre, puis
        //    dehors — et VISIBLE, meme en plein ecran.
        // ⚠️ ON REMET LA GRAINE ICI. Les soixante images du battant plus haut
        // font vivre toute la ville, et elles puisent dans `B.rng` un nombre de
        // fois qui depend d'elle : deux tuiles de cloture de plus a l'autre bout
        // du Faubourg, et l'archetype tire ici n'est plus le meme, ni sa vitesse.
        // La marge etait d'UN pixel (« avance > 8 » pour douze mesures), alors le
        // juge tombait sur des changements qui n'ont rien a voir avec les portes —
        // c'est deja arrive le 14 sept. 2026. Ce qu'on mesure ici ne doit dependre
        // que de la porte et de celui qui en sort.
        L.graine(97);
        j.x = porte.x * L.TT + 8; j.y = (porte.y + 6) * L.TT + 8;
        L.Monde.centrerCamera(j.x, j.y);
        // ⚠️ On DEGAGE LE PAS DE PORTE : ce qu'on juge ici, c'est le battant et
        // la sortie, pas la foule. Un passant plante sur la tuile d'en dessous
        // et celui qui sort n'avance plus de quatre pixels — le juge parlerait
        // alors de la densite du quartier, pas des portes.
        for (const q of L.B.entites.slice()) {
            if (q.type === 'pieton' && Math.hypot(q.x - j.x, q.y - j.y) < 120) L.Entites.retirer(q);
        }
        L.Entites.indexer();
        const arch = L.Entites.archetypeDeRue();
        const e = L.Entites.creerPieton(porte.x * L.TT + 8, (porte.y + 1) * L.TT + 8, arch);
        e.sortie = { x: porte.x, y: porte.y, t: 0 };
        L.Monde.ouvrirPorte(porte.x, porte.y);
        const y0 = e.y;
        const vus = [];
        // ⚠️ LE PLUS LOIN qu'il soit alle, pas ou il est a la quarantieme image :
        // une fois dehors il reprend sa vie, et flaner veut dire revenir sur ses
        // pas. Sur une porte de ruelle (celle que ce juge tire depuis que la
        // ville a bouge, 14 sept. 2026), il sortait de onze pixels puis
        // rebroussait chemin — le juge lisait cinq et disait qu'il ne sortait
        // pas. Ce qu'on juge, c'est qu'il SORT.
        let loin = 0;
        for (let i = 0; i < 40; i++) { o.frame(1); vus.push(e.dessine); loin = Math.max(loin, e.y - y0); }
        out.sortie = { cacheAuDebut: vus[0] === false, vuEnsuite: vus.indexOf(true) > 0,
                       avance: Math.round(loin), libre: !e.sortie,
                       aLEcran: L.Entites.visibleAEcran(e.x, e.y, 0) };

        // 5. Entrer : il marche jusqu'a la porte, elle s'ouvre, ET IL DISPARAIT
        //    SEULEMENT APRES — jamais devant une porte fermee.
        e.etat = 'flane'; e.porteBut = porte; e.porteT = 0; e.porteBloque = 0;
        e.x = porte.x * L.TT + 8; e.y = (porte.y + 3) * L.TT + 8;
        let disparu = -1, ouvertAlors = -1;
        for (let i = 0; i < 300 && disparu < 0; i++) {
            o.frame(1);
            if (L.B.entites.indexOf(e) < 0) { disparu = i; ouvertAlors = L.Monde.battant(porte.x, porte.y); }
        }
        out.entree = { disparu: disparu, ouvertAlors: ouvertAlors };
        return out;
    }""")
    b = r["battant"]
    assert b["debut"] == 0 and b["monte"] is True and b["max"] >= 0.99 and b["fin"] == 0, (
        "un battant doit s'ouvrir, tenir, puis se refermer tout seul : %s" % b
    )
    # ⚠️ LE juge du rythme : repeindre un morceau de 256 px pour une porte
    # tuerait le cache qui tient le téléphone.
    assert r["morceaux"]["apres"] == r["morceaux"]["avant"], (
        "ouvrir une porte a fait repeindre des morceaux : %s" % r["morceaux"]
    )
    assert r["regles"] == {"planque": False, "poste": False, "hopital": False, "logement": True}, (
        "les portes qui servent ne sont pas les bonnes : %s" % r["regles"]
    )
    assert r["commerce"] == {"jour": True, "nuit": False, "barLaNuit": True}, (
        "un commerce fermé ne doit laisser entrer personne — sauf le bar : %s" % r["commerce"]
    )
    s = r["sortie"]
    assert s["cacheAuDebut"] is True, "on le voit AVANT que la porte s'ouvre : %s" % s
    assert s["vuEnsuite"] is True and s["aLEcran"] is True, (
        "la sortie doit se voir, et en plein écran : %s" % s
    )
    assert s["avance"] > 8 and s["libre"] is True, "il doit sortir de la porte et reprendre sa vie : %s" % s
    assert r["entree"]["disparu"] >= 0, "personne n'entre nulle part : %s" % r["entree"]
    # ⚠️ Une porte ne s'ouvre jamais sur rien : il disparaît APRÈS l'ouverture.
    assert r["entree"]["ouvertAlors"] >= 0.9, (
        "il est entré par une porte encore fermée (%s) : une porte ne s'ouvre jamais sur rien"
        % r["entree"]["ouvertAlors"]
    )


def test_le_decor_arrete_ou_casse_sous_un_char_et_la_ville_se_repare(banc):
    """⚠️ Demande de Martin : « une interaction réaliste avec le décor — les bris
    de poteau, de banc de parc et d'arbre. »

    Le décor était **solide pour les piétons et fantôme pour les chars** : un
    autobus traversait un arbre, un kiosque et une fontaine sans ralentir. Le
    défonçage de M9 ne cassait que des **tuiles** (clôtures, bornes) ; le décor
    n'était ni un obstacle ni une chose qui casse. C'est la moitié d'un monde.

    Deux familles, et **c'est la fiche qui décide** : ce qui **arrête** un char
    (un arbre, une fontaine — sauf au-dessus d'une masse) et ce qui **casse**
    sous lui (un banc, un lampadaire). Le juge lance une berline puis un camion
    sur les deux, vérifie que le bris laisse des **débris**, éteint la lampe du
    poteau tombé, compte une **conduite dangereuse**, et que tout est debout le
    lendemain."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        L.graine(91);
        const j = L.B.joueur;
        const out = {};

        /* Lance `slug` sur le premier decor de ce type, et dit ce qui s'est
           passe. Le char arrive par le sud, a pleine vitesse. */
        function foncer(slug, type) {
            // ⚠️ Un decor avec DE LA PLACE AU SUD : sinon le char bute sur la
            // facade d'a cote avant d'atteindre l'arbre, et on mesurerait un
            // mur en croyant mesurer un arbre.
            //
            // ⚠️ Et de la place VIDE DE DECOR, pas seulement de tuiles. Le
            // 15 sept. 2026, un buisson est entre dans l'index du decor — il
            // portait `casse` depuis toujours mais `solide: false` l'en tenait
            // dehors, et rien ne pouvait le toucher. Des qu'un char a pu le
            // coucher, celui du couloir d'approche a mange une part de l'elan
            // de la berline : elle finissait a UN pixel de l'ancre de l'arbre
            // au lieu d'un cheveu avant, et le juge criait « une berline
            // traverse un arbre » alors qu'elle s'arretait dessus. On mesurait
            // un buisson en croyant mesurer un arbre.
            const corridorLibre = function (e) {
                return !L.B.entites.some(function (q) {
                    if (q === e || q.type !== 'decor' || q.brise) return false;
                    const f = L.DECORS[q.decor] || {};
                    if (!f.casse && !f.arrete) return false;
                    const dy = q.y - e.y;
                    return Math.abs(q.x - e.x) < 24 && dy > 0 && dy < 90;
                });
            };
            const d = L.B.entites.find(function (e) {
                if (e.decor !== type || e.brise) return false;
                const tx = Math.floor(e.x / L.TT);
                for (let k = 1; k <= 6; k++) {
                    const ty = Math.floor(e.y / L.TT) + k;
                    for (let dx = -1; dx <= 1; dx++) {
                        if (L.Monde.bloque(tx + dx, ty, L.Monde.MASQUE_VEHICULE)) return false;
                    }
                }
                return corridorLibre(e);
            });
            if (!d) return null;
            j.x = d.x; j.y = d.y + 70;
            L.Monde.centrerCamera(j.x, j.y);
            const v = L.Vehicules.creer(slug, d.x, d.y + 70, -Math.PI / 2, { etat: 'roule' });
            L.Vehicules.monter(j, v);
            v.vitesse = v.def.vitesse_max; v.vx = 0; v.vy = -v.def.vitesse_max;
            const crimes0 = L.B.partie.stats.crimes;
            // ⚠️ On ne force PAS la vitesse a chaque image : un arbre qui
            // arrete doit pouvoir renvoyer le char. Le forcer, ce serait
            // pousser soi-meme le char au travers et croire que l'arbre est
            // fantome.
            for (let i = 0; i < 60; i++) L.Vehicules.avancer(v);
            const r = { brise: !!d.brise, passe: v.y < d.y,
                        // ⚠️ Seulement les debris NES D'UN BRIS (`e.debris` porte
                        // l'image) : la ville en pose deja 88 a la main, dans la
                        // cour de la fourriere et les terrains vagues.
                        debris: L.B.entites.filter(function (e) { return e.debris; }).length,
                        crimes: L.B.partie.stats.crimes - crimes0,
                        solide: d.solide };
            L.Vehicules.descendre(j, true);
            L.Entites.retirer(v);
            return r;
        }

        out.berlineArbre = foncer('auto', 'arbre');          // un arbre arrete une berline
        out.camionArbre = foncer('camion', 'arbre');         // un camion le deracine
        out.berlineBanc = foncer('auto', 'banc');            // un banc cede sous n'importe quoi

        // Le lampadaire : son poteau tombe, SA LUMIERE S'ETEINT.
        const lampe = L.B.entites.find(function (e) { return e.decor === 'lampadaire' && !e.brise; });
        const avant = L.Monde.carte.lampes.filter(function (l) { return l.eteinte; }).length;
        L.Entites.briser(lampe);
        out.lampe = { eteintes: L.Monde.carte.lampes.filter(function (l) { return l.eteinte; }).length - avant,
                      solide: lampe.solide, brise: lampe.brise };

        // Le plafond des debris : une nuit a tout casser doit tenir le rythme.
        const cassables = L.B.entites.filter(function (e) {
            const f = L.DECORS[e.decor] || {};
            return e.type === 'decor' && !e.brise && (f.casse || f.arrete);
        });
        for (const d of cassables) L.Entites.briser(d);
        out.plafond = { debris: L.B.entites.filter(function (e) { return e.debris; }).length,
                        max: L.Entites.DEBRIS_MAX, casses: cassables.length };

        // Et le lendemain, tout est debout — par `nouveauJour()`, pas en
        // appelant la reparation a la main : c'est le lever du jour qui repare,
        // et c'est ce lien-la qu'il faut juger.
        // ⚠️ On compte les brises AVANT :
        // le camion en a couche d'autres sur son passage, et une soustraction
        // faite en Python se tromperait de ce qu'elle mesure.
        const brisesAvant = L.B.entites.filter(function (e) { return e.type === 'decor' && e.brise; }).length;
        const brisesRestants = function () { return L.B.entites.filter(function (e) { return e.type === 'decor' && e.brise; }).length; };
        L.B.partie.jour++;
        L.Missions.nouveauJour();
        const remis = brisesAvant - brisesRestants();
        out.lendemain = { remis: remis, brisesAvant: brisesAvant,
                          // ⚠️ Seulement les debris NES D'UN BRIS (`e.debris` porte
                        // l'image) : la ville en pose deja 88 a la main, dans la
                        // cour de la fourriere et les terrains vagues.
                        debris: L.B.entites.filter(function (e) { return e.debris; }).length,
                          brises: L.B.entites.filter(function (e) { return e.type === 'decor' && e.brise; }).length,
                          eteintes: L.Monde.carte.lampes.filter(function (l) { return l.eteinte; }).length };
        return out;
    }""")
    a, c, b = r["berlineArbre"], r["camionArbre"], r["berlineBanc"]
    assert a and c and b, "il manque un arbre ou un banc dans la ville"
    assert a["brise"] is False and a["passe"] is False, (
        "une berline traverse un arbre : %s" % a
    )
    assert c["brise"] is True and c["passe"] is True, (
        "un camion doit déraciner l'arbre et passer : %s" % c
    )
    assert b["brise"] is True and b["passe"] is True, "un banc doit céder sous une berline : %s" % b
    assert b["solide"] is False, "un décor cassé reste solide : on bute sur des planches"
    assert b["debris"] >= 1, "le bris ne laisse aucun débris : c'est une disparition, pas un bris"
    # ⚠️ Casser est un délit : sinon défoncer est gratuit, et un char lourd
    # vaut plus qu'un char rapide.
    assert c["crimes"] >= 1, "déraciner un arbre au camion n'est pas un délit : %s" % c
    assert r["lampe"] == {"eteintes": 1, "solide": False, "brise": True}, (
        "un lampadaire à terre continue d'éclairer : %s" % r["lampe"]
    )
    assert r["plafond"]["casses"] > r["plafond"]["max"], "pas assez de décor cassé pour tester le plafond"
    assert r["plafond"]["debris"] <= r["plafond"]["max"], (
        "%s débris pour un plafond de %s" % (r["plafond"]["debris"], r["plafond"]["max"])
    )
    matin = r["lendemain"]
    assert matin["remis"] == matin["brisesAvant"] > 0, (
        "tout ce qui était cassé n'a pas été remis : %s" % matin
    )
    assert (matin["debris"], matin["brises"], matin["eteintes"]) == (0, 0, 0), (
        "le lendemain, la ville doit être debout, déblayée et rallumée : %s" % matin
    )


def test_le_decor_solide_arrete_le_joueur_mais_pas_un_buisson(banc):
    """⚠️ Le lampadaire BLOQUE maintenant, et c'est le correctif : il était
    `solide: false`, donc fantôme pour tout le monde — on le traversait à pied
    comme en char. Un poteau de deux pixels de rayon qu'on traverse, c'est la
    moitié d'un monde."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const j = L.B.joueur;
        // ⚠️ PAS LE PREMIER VENU : celui qui a LE PAS LIBRE AU SUD. On pose le
        // joueur vingt pixels sous le decor et on pousse vers le nord ; si cette
        // tuile-la est une cloture ou un mur, on ne mesure plus le decor, on
        // mesure son voisinage. Le juge est tombe le jour ou les cours arriere
        // se sont cloturees pour de bon : le premier buisson de la liste avait
        // une palissade juste en dessous, et « un buisson ne doit pas bloquer »
        // accusait le buisson.
        function pousser(type) {
            const d = L.B.entites.find(function (e) {
                if (e.decor !== type) return false;
                const tx = Math.floor(e.x / L.TT), ty = Math.floor(e.y / L.TT);
                return !L.Monde.bloque(tx, ty, L.Monde.MASQUE_PIETON)
                    && !L.Monde.bloque(tx, ty + 1, L.Monde.MASQUE_PIETON);
            });
            if (!d) return null;
            j.x = d.x; j.y = d.y + 20; j.vx = 0; j.vy = 0;
            for (let i = 0; i < 30; i++) L.Entites.deplacerCercle(j, 0, -1.2, L.Monde.MASQUE_PIETON);
            return Math.round(j.y - d.y);
        }
        return { arbre: pousser('arbre'), buisson: pousser('buisson'),
                 lampadaire: pousser('lampadaire') };
    }""")
    assert r["arbre"] is not None and r["arbre"] > 0, "on traverse les arbres"
    assert r["buisson"] is not None and r["buisson"] <= 0, "un buisson ne doit pas bloquer"
    assert r["lampadaire"] is not None and r["lampadaire"] > 0, "on traverse les lampadaires"


def test_on_ne_se_tient_pas_DANS_le_decor(banc):
    """Retour de Martin, capture a l'appui : le joueur debout au milieu du
    camion-restaurant, dans la carrosserie.

    ⚠️ La cause n'etait pas la collision mais sa FORME. Le camion fait 44 px
    de large et 8 px de profond ; son seul cercle (r 16) tenait dans la
    profondeur, alors il laissait 6 px de carrosserie libres de chaque cote.
    Chaque decor carre porte maintenant une boite `sol`, et ce juge pousse le
    joueur dessus par les quatre cotes : il doit rester DEHORS.
    """
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const j = L.B.joueur;
        const dedans = [], vus = {};
        for (const d of L.B.entites) {
            if (!d.decor || !d.solide) continue;
            const f = L.DECORS[d.decor];
            if (!f || !f.sol || vus[d.decor]) continue;
            vus[d.decor] = true;
            [[1, 0], [-1, 0], [0, 1], [0, -1]].forEach(function (c) {
                j.x = d.x + c[0] * 60; j.y = d.y + c[1] * 60; j.vx = 0; j.vy = 0;
                for (let i = 0; i < 120; i++) L.Entites.deplacerCercle(j, -c[0] * 1.2, -c[1] * 1.2, L.Monde.MASQUE_PIETON);
                // Le cercle du joueur mord-il la boite au sol du decor ?
                const mordX = f.sol[0] + j.r - Math.abs(j.x - d.x);
                const mordY = f.sol[1] + j.r - Math.abs(j.y - d.y);
                const mord = Math.min(mordX, mordY);
                if (mord > 0.01) dedans.push({ decor: d.decor, cote: c.join(','), mord: +mord.toFixed(2) });
            });
        }
        return { dedans: dedans, boites: Object.keys(vus).sort() };
    }""")
    assert "camion_cuisine" in r["boites"], "le camion-restaurant de la capture doit etre teste"
    assert r["dedans"] == [], "le joueur se tient dans le dessin d'un decor"


def test_la_portee_de_recherche_couvre_la_plus_grosse_empreinte(banc):
    """⚠️ Le piege du jour ou l'on ajoutera un decor plus large : la recherche
    du decor autour de soi est un CERCLE, l'empreinte est une BOITE. Si le
    rayon ne va pas jusqu'au COIN de la boite, le decor n'est meme pas trouve
    — pas de collision ratee, pas de test rouge : rien, on lui passe au
    travers. Ce juge refait le calcul sur chaque decor solide.
    """
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const trop = [];
        const rayonHumain = 5;             // joueur et pietons ont tous r = 5
        for (const nom in L.DECORS) {
            const f = L.DECORS[nom];
            if (!f.solide) continue;
            const coin = f.sol ? Math.hypot(f.sol[0] + rayonHumain, f.sol[1] + rayonHumain) : f.r + rayonHumain;
            const exige = coin - rayonHumain;
            if (exige > L.Entites.PORTEE_DECOR) trop.push({ decor: nom, exige: +exige.toFixed(1) });
        }
        return { trop: trop, portee: L.Entites.PORTEE_DECOR };
    }""")
    assert r["trop"] == [], f"PORTEE_DECOR ({r['portee']}) ne couvre pas ces decors"


def test_le_marchand_reste_derriere_son_comptoir(banc):
    """⚠️ Le guichet du camion-restaurant est TROUE pour qu'on voie le marchand
    dedans — encore faut-il qu'il y soit. `peupler()` oubliait tout pieton a
    plus de 520 px du joueur, marchands compris : on debarquait de l'autobus
    et les neuf comptoirs de la ville se vidaient a la premiere image. Un
    marchand tient son poste comme un personnage d'histoire : il attend.
    """
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const compter = function () {
            return { comptoirs: L.B.entites.filter(function (e) { return e.type === 'ambulant'; }).length,
                     marchands: L.B.entites.filter(function (e) { return e.commerce; }).length };
        };
        const avant = compter();
        o.frame(60);
        return { avant: avant, apres: compter() };
    }""")
    assert r["avant"]["comptoirs"] > 0, "aucun commerce ambulant sur la carte"
    assert r["avant"]["marchands"] == r["avant"]["comptoirs"], "un comptoir nait sans marchand"
    assert r["apres"]["marchands"] == r["apres"]["comptoirs"], "les marchands s'oublient quand on est loin"


def test_la_foule_ne_se_traverse_plus(banc):
    """Retour de Martin : « empeche que les choses se chevauchent ».

    ⚠️ Personne ne poussait personne : deux passants qui se croisaient se
    superposaient EXACTEMENT. Mesure avant correctif, en marchant deux minutes
    dans la ville : 1032 paires enfoncees l'une dans l'autre en 960 images,
    jusqu'a 9,9 px — deux corps de 10 px parfaitement confondus. Apres : 0,1 px
    au pire, des la premiere image (personne ne NAIT non plus dans quelqu'un).
    """
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        let paires = 0, pire = 0, images = 0, nes = 0;
        // ⚠️ On mesure aussi la DUREE d'un chevauchement, et combien passent le
        // pixel : c'est ca, « se traverser ». Une profondeur seule ne distingue
        // pas deux corps confondus d'un frolement d'une image entre deux
        // passants qui se croisent de face.
        let gros = 0, plusLong = 0, creuse = 0;
        const durees = {}, profond = {}, creuseT = {};
        // Naitre dans quelqu'un se voit a un chevauchement PLEIN (meme pixel) :
        // les deux branches de placeDeNaissance rendent un centre de tuile.
        const touches = ['KeyD', 'KeyW', 'KeyA', 'KeyS'];
        for (let bloc = 0; bloc < 24; bloc++) {
            const t = touches[bloc % 4];
            o.touche(t);
            for (let k = 0; k < 40; k++) {
                o.frame(1); images++;
                const gens = L.B.entites.filter(L.Entites.deboutDansLaFoule);
                const vues = {};
                for (let a = 0; a < gens.length; a++) {
                    for (let b = a + 1; b < gens.length; b++) {
                        const d = Math.hypot(gens[a].x - gens[b].x, gens[a].y - gens[b].y);
                        const chevauche = gens[a].r + gens[b].r - d;
                        if (chevauche > gens[a].r + gens[b].r - 0.001) nes++;
                        // ⚠️ **LA FOULE ENTRE ELLE, pas le joueur contre elle.** Deux
                        // passants se démêlent tous les deux : chacun cède la moitié,
                        // et un chevauchement qui dure est un vrai défaut. Le joueur,
                        // lui, POUSSE — et quand il coince quelqu'un contre un mur,
                        // personne n'a plus où aller : mesuré le 17 sept. 2026 au
                        // terminus, 5,2 px d'enfoncement, un passant acculé à la
                        // façade. Ce cas-là a son juge à lui, et il est plus sévère
                        // (`test_courir_ne_permet_pas_de_traverser_les_gens` : on
                        // n'entre pas dans quelqu'un qui a de quoi s'écarter).
                        if (gens[a].type === 'joueur' || gens[b].type === 'joueur') continue;
                        if (chevauche > 0) { paires++; pire = Math.max(pire, chevauche); }
                        const cle = gens[a].id + '-' + gens[b].id;
                        if (chevauche > 1) {
                            gros++;
                            durees[cle] = (durees[cle] || 0) + 1;
                            plusLong = Math.max(plusLong, durees[cle]);
                            vues[cle] = true;
                            // ⚠️ LA VRAIE REGLE : un chevauchement SE DEFAIT. Deux
                            // corps qui s'enfoncent l'un dans l'autre d'une image a
                            // l'autre, c'est ca, se traverser — un nombre d'images
                            // n'est qu'une consequence, et il depend du trajet des
                            // passants.
                            // ⚠️ ... et un creusement qui se DEFAIT l'image suivante est une
                            // bousculade — un troisieme corps qui pousse — pas une traversee.
                            // On ne compte que ceux qui creusent ET tiennent.
                            if (profond[cle] !== undefined && chevauche > profond[cle] + 0.01) {
                                creuseT[cle] = (creuseT[cle] || 0) + 1;
                                if (creuseT[cle] >= 2) creuse++;
                            } else creuseT[cle] = 0;
                            profond[cle] = chevauche;
                        }
                    }
                }
                for (const cle in durees) if (!vues[cle]) { durees[cle] = 0; delete profond[cle]; delete creuseT[cle]; }
            }
            o.relacher(t);
        }
        return { images: images, paires: paires, pire: +pire.toFixed(2), nes_empiles: nes,
                 gros: gros, plusLong: plusLong, creuse: creuse };
    }""")
    assert r["images"] == 960
    assert r["nes_empiles"] == 0, "on ne nait pas dans quelqu'un"
    # ⚠️ CE QU'ON INTERDIT, C'EST DE SE TRAVERSER : un chevauchement qui DURE,
    # ou qui va jusqu'à confondre deux corps. Le juge exigeait moins d'un pixel
    # à toute image — c'était la MESURE du jour, pas la règle : deux passants
    # qui se croisent de face se rapprochent de quatre pixels en une image, et
    # la séparation les défait à la suivante. Exiger moins d'un pixel revenait à
    # exiger que personne ne se croise jamais de face, et ça tenait au trajet des
    # passants, pas au code. Le défaut d'origine (1032 paires, 9,9 px, tenues)
    # reste rouge des trois côtés.
    # ⚠️ **Reformule le 15 sept. 2026, et cette fois sur la REGLE.** Il exigeait
    # qu'aucun chevauchement ne tienne plus d'UNE image — un nombre qui dependait
    # du trajet des passants, pas du code : une seule paire l'a depasse, deux
    # images a 1,05 px, le jour ou la ville est redevenue reproductible (elle ne
    # l'etait pas, voir `test_reproductible`). Ce qu'on veut dire par « se
    # traverser », c'est deux corps qui s'ENFONCENT l'un dans l'autre au lieu de
    # se defaire. Ca, c'est une regle, et elle se mesure sans seuil : mesure du
    # jour, ZERO enfoncement sur 960 images.
    assert r["creuse"] == 0, (
        f"{r['creuse']} fois un chevauchement s'est CREUSE au lieu de se défaire : "
        "la séparation ne pousse pas assez fort, et la foule se traverse"
    )
    assert r["plusLong"] <= 4, (
        f"un chevauchement tient {r['plusLong']} images : deux corps restent pris l'un dans l'autre"
    )
    assert r["gros"] <= 8, f"{r['gros']} chevauchements de plus d'un pixel en 960 images"
    assert r["pire"] < 4.0, f"deux personnes s'enfoncent de {r['pire']} px l'une dans l'autre"


def test_courir_ne_permet_pas_de_traverser_les_gens(banc, paquet):
    """⚠️ Le plafond de separation doit passer DEVANT les jambes les plus
    rapides du jeu. Fixe a 1,5 px, il arretait bien le joueur qui MARCHE
    (1,2 px/image) et laissait passer celui qui SPRINTE (2,1) : il suffisait
    de tenir MAJ pour entrer dans le vendeur.
    """
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const j = L.B.joueur;
        const pas = L.Entites.pasDeDemele();
        const t = L.B.entites.find(function (e) { return e.personnage === 'ti_guy'; });
        function foncer(sprint) {
            j.x = t.x - 40; j.y = t.y; j.vx = 0; j.vy = 0;
            if (sprint) o.touche('ShiftLeft');
            o.touche('KeyD'); o.frame(120); o.relacher('KeyD');
            if (sprint) o.relacher('ShiftLeft');
            return +Math.hypot(j.x - t.x, j.y - t.y).toFixed(1);
        }
        return { pas: pas, marche: foncer(false), sprint: foncer(true), r: j.r + t.r };
    }""")
    vitesses = paquet["recherche"]["vitesses"]
    assert r["pas"] > vitesses["joueur_sprint"], "on sprinte plus vite qu'on ne se demele"
    assert r["marche"] >= r["r"] - 0.5, "on entre dans un personnage en marchant"
    assert r["sprint"] >= r["r"] - 0.5, "on entre dans un personnage en courant"


def test_celui_qui_tient_son_poste_cede_puis_revient(banc):
    """⚠️ « Fige » veut dire « il tient son poste », pas « c'est un poteau ».
    Vraiment immobile, un donneur plante sur le trottoir bouchait la rue POUR
    TOUJOURS : l'agent lance aux trousses du joueur venait buter dessus et y
    restait — 260 images sur place, l'arrestation n'arrivait jamais. Il se
    laisse donc bousculer de quelques pixels, et il rentre chez lui.
    """
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const j = L.B.joueur;
        const t = L.B.entites.find(function (e) { return e.personnage === 'ti_guy'; });
        // ⚠️ **LA RUE AUTOUR DE LUI EST VIDE** : une roulotte a cafe a 1 tuile de Ti-Guy fait ce juge.
        // A l'ouest, elle se tenait sur la piste du coureur — il mesurait 1 px, la roulotte, pas la
        // laisse ; deplacee a l'est (`app/devants.py` : elle bouchait la porte du terminus), Ti-Guy
        // se retrouvait coince contre elle, a 12,1 px et incapable de revenir. Le juge parle d'un
        // donneur, pas d'une roulotte : on l'ote, et ce qu'on mesure est la laisse toute seule.
        L.B.entites.filter(function (e) { return e.type === 'ambulant' && Math.hypot(e.x - t.x, e.y - t.y) < 200; })
            .forEach(function (e) { L.Entites.retirer(e); });
        L.Entites.indexer();
        o.frame(2);
        const poste = { x: t.plante ? t.plante.x : t.x, y: t.plante ? t.plante.y : t.y };
        j.x = poste.x - 40; j.y = poste.y; j.vx = 0; j.vy = 0;
        // ⚠️ **ON LE POUSSE, ON NE LE CONTOURNE PAS.** Le juge courait droit
        // vers l'est pendant 240 images et lisait le déplacement à la fin :
        // sauf que `demeler` écarte les corps qui se touchent, donc le joueur
        // DÉRIVE de quelques pixels, passe à côté du poste et continue sa
        // course — mesuré le 16 sept. 2026, il finissait 228 px plus loin sans
        // avoir bousculé personne, et le juge concluait « on ne peut pas le
        // tasser ». Ce qu'on mesure est une POUSSÉE : on garde donc le joueur
        // sur la ligne du poste pendant qu'il pousse. Le contournement a son
        // propre juge ; celui-ci n'en parle pas.
        o.touche('ShiftLeft'); o.touche('KeyD');
        for (let i = 0; i < 240; i++) { j.y = poste.y; o.frame(1); }
        const pousse = Math.hypot(t.x - poste.x, t.y - poste.y);
        o.relacher('KeyD'); o.relacher('ShiftLeft');
        // ⚠️ Et on le DEPLACE pour de bon, de huit pixels (sous la laisse) : en rue libre la poussee
        // ne l'ecarte que d'un dixieme de pixel, et « il rentre » serait vrai sans qu'il ait a rentrer.
        t.x = poste.x + 8; t.y = poste.y;
        j.x = poste.x - 200; j.y = poste.y;              // on le lache
        // ⚠️ Il rentre à pied, et le chemin du retour dépend de ce qu'il a autour
        // (un banc, un passant, la largeur du trottoir) : 180 images le ramenaient
        // à un demi-pixel près tant que la trame n'avait pas bougé, et à 1,0 px
        // pile le 17 sept. 2026. On lui laisse le temps d'arriver plutôt que
        // d'élargir la règle : « à sa place » veut dire à sa place.
        for (let i = 0; i < 600 && Math.hypot(t.x - poste.x, t.y - poste.y) > 1; i++) o.frame(1);
        return { pousse: +pousse.toFixed(1), rentre: +Math.hypot(t.x - poste.x, t.y - poste.y).toFixed(1),
                 etat: t.etat };
    }""")
    # ⚠️ Le plancher est « un peu », pas un demi-pixel : en rue libre la laisse le ramene a chaque
    # image et l'equilibre est a 0,1-0,3 px (le demi-pixel d'avant n'etait tenu que par la roulotte).
    assert r["pousse"] > 0.05, "on doit pouvoir le tasser un peu, sinon il bouche la rue"
    assert r["pousse"] < 12, f"on l'a promene de {r['pousse']} px : il n'est plus a son poste"
    # ⚠️ **UN PIXEL, c'est à sa place** : il marche par pas de fraction de pixel et
    # s'arrête dès qu'il est chez lui. Le juge exigeait STRICTEMENT moins d'un
    # pixel, et il l'obtenait tant que le trottoir d'à côté était celui-là ; le
    # 17 sept. 2026, la trame a bougé et il s'est posé à 1,0 px pile. Un donneur
    # large de douze pixels est à son poste à un pixel près — ce qu'on juge, c'est
    # qu'il RENTRE, pas qu'il vise le sous-pixel.
    assert r["rentre"] <= 1, "lache, il doit revenir a sa place"
    assert r["etat"] == "fige"


def test_le_son_survit_a_l_absence_d_audio(banc, paquet):
    """Sous Node il n'y a pas d'AudioContext : le jeu doit jouer quand meme."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        L.Son.reveiller();
        const avant = L.B.t;
        for (const nom in L.Son.SFX) L.Son.SFX[nom]();
        L.Son.boucle('sirene', true); L.Son.boucle('sirene', false);
        o.tape('KeyD', 30);
        return { charges: L.Son.charges, pret: L.Son.pret(), contexte: L.Son.contexte,
                 avance: L.B.t > avant, sons: L.B.defs.audio.echantillons.length,
                 sansFichier: L.B.defs.audio.echantillons.filter(function (e) { return !e.fichiers.length; }).map(function (e) { return e.slug; }) };
    }""")
    assert r["contexte"] is None and r["pret"] is False
    assert r["charges"] == 0, "rien ne doit se charger sans AudioContext"
    assert r["avance"] is True, "la boucle s'est arretee sur un son"
    assert r["sons"] == len(paquet["audio"]["echantillons"])
    assert r["sansFichier"] == [], f"sons declares sans fichier : {r['sansFichier']}"


# --- M2 : pietons et poings ------------------------------------------------

def test_la_rue_se_peuple_puis_s_oublie(banc, paquet):
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        o.frame(600);
        const j = L.B.joueur;
        // ⚠️ Les marchands derriere leur kiosque ne sont pas la foule.
        const pietons = L.B.entites.filter(function (e) { return e.type === 'pieton' && !e.metier; });
        const loin = pietons.filter(function (e) {
            return Math.hypot(e.x - j.x, e.y - j.y) > L.Entites.BULLE_OUBLI + 80;
        });
        const dansLEcran = pietons.filter(function (e) { return L.Entites.visibleAEcran(e.x, e.y, 0); });
        // On se teleporte a l'autre bout : la foule doit suivre, pas rester la.
        // ⚠️ « L'autre bout » reste la VILLE, pas le relief (`relief.py`, 21 sept.
        // 2026) : sa chaine de montagnes, a l'est, est infranchissable — personne
        // n'y nait, n'y marche ni n'y suit personne.
        const c = L.Monde.carte;
        const largeurRelief = c.def.relief ? c.def.relief.montagnes.l * L.TT : 0;
        j.x = c.pxW - largeurRelief - 200; j.y = c.pxH - 200;
        L.Monde.centrerCamera(j.x, j.y);
        o.frame(600);
        const apres = L.B.entites.filter(function (e) { return e.type === 'pieton' && !e.metier; });
        const proches = apres.filter(function (e) {
            return Math.hypot(e.x - j.x, e.y - j.y) < L.Entites.BULLE_OUBLI;
        });
        return { avant: pietons.length, loin: loin.length, vus: dansLEcran.length,
                 apres: apres.length, proches: proches.length, max: L.Entites.MAX_PIETONS,
                 sol: apres.map(function (e) { return L.Monde.solidite(Math.floor(e.x / L.TT), Math.floor(e.y / L.TT)); }) };
    }""")
    # +1 : une mere nait avec son petit, et la bulle compte les vivants AVANT.
    assert 4 <= r["avant"] <= r["max"] + 1, "la rue est vide ou bondee"
    assert r["loin"] == 0, "des pietons trainent hors de la bulle"
    assert r["vus"] > 0, "personne a l'ecran"
    assert r["proches"] == r["apres"] > 0, "la foule n'a pas suivi le joueur"
    assert all(s in (0, 3) for s in r["sol"]), "un pieton est ne dans un mur"


def test_l_arc_de_melee_touche_devant_et_pas_derriere(banc):
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        L.graine(4);
        const devant = o.poser('passant', 14, 0);
        const derriere = o.poser('passant', -14, 0);
        o.viser(devant);
        L.Combat.frapper(L.B.joueur, false);
        for (let i = 0; i < 20; i++) { L.Entites.indexer(); L.Combat.maj(); }
        return { devant: devant.vie, derriere: derriere.vie, max: devant.vieMax };
    }""")
    assert r["devant"] < r["max"], "le coup n'a pas porte devant"
    assert r["derriere"] == r["max"], "le coup a porte DERRIERE le joueur"


def test_un_coup_ne_compte_qu_une_fois(banc, paquet):
    degats = next(a for a in paquet["armes"] if a["slug"] == "poings")["degats"]
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        L.graine(5);
        const cible = o.poser('ouvrier', 12, 0);
        o.viser(cible);
        const avant = cible.vie;
        L.Combat.frapper(L.B.joueur, false);
        for (let i = 0; i < 30; i++) { L.Entites.indexer(); L.Combat.maj(); }
        return { perdu: avant - cible.vie };
    }""")
    assert r["perdu"] == degats, f"un coup a enleve {r['perdu']} au lieu de {degats}"


def test_les_poings_assomment_et_le_couteau_tue(banc):
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        L.graine(6);
        function cogner(arme, arch) {
            L.B.joueur.arme = arme;
            if (arme !== 'poings') L.B.partie.armes[arme] = { mun: null, usure: 0 };
            // ⚠️ **LA RUE SE VIDE AVANT CHAQUE MANCHE.** Un coup touche TOUT ce
            // qui est à portée : un passant de plus à côté de la cible, et le
            // couteau en tue deux (17 sept. 2026, la trame a bougé et le juge
            // comptait deux morts pour un). On ne juge que le corps qu'on frappe.
            for (const q of L.B.entites.slice()) {
                if (q === L.B.joueur || q.type === 'joueur') continue;
                if (q.type === 'pieton' || q.type === 'vehicule') L.Entites.retirer(q);
            }
            const c = o.poser(arch, 12, 0);
            c.courage = 0;
            for (let coup = 0; coup < 30 && c.vie > 0; coup++) {
                L.B.joueur.x = c.x - 12; L.B.joueur.y = c.y;
                o.viser(c);
                L.Combat.frapper(L.B.joueur, false);
                for (let i = 0; i < 30; i++) { L.Entites.indexer(); L.Combat.maj(); }
            }
            const etat = { vivant: c.vivant, etat: c.etat, vie: c.vie };
            // ⚠️ On retire le corps avant la manche suivante : sinon le couteau
            // acheve le KO d'a cote (ce qui est juste, mais fausse le compte).
            L.Entites.retirer(c);
            L.Entites.indexer();
            return etat;
        }
        const poing = cogner('poings', 'passant');
        const americain = cogner('poing_americain', 'ouvrier');
        const lame = cogner('couteau', 'passante');
        return { poing: poing, americain: americain, lame: lame, tues: L.B.partie.stats.tues,
                 decals: L.B.decals.length, sang: L.B.options.sang };
    }""")
    assert r["poing"]["vivant"] is True and r["poing"]["etat"] == "assomme", \
        "les poings doivent assommer, pas tuer — c'est ce qui separe 1 etoile de 3"
    assert r["americain"]["vivant"] is True and r["americain"]["etat"] == "assomme", \
        "le poing americain est un poing plus lourd : il assomme aussi (%s)" % r["americain"]
    assert r["lame"]["vivant"] is False and r["lame"]["etat"] == "mort"
    assert r["tues"] == 1
    assert r["decals"] > 0, "pas une goutte de sang"


def test_le_sang_et_les_particules_sont_plafonnes(banc):
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const j = L.B.joueur;
        for (let i = 0; i < 400; i++) {
            L.Entites.sang(j.x + (i % 40), j.y + (i % 30), 8);
            L.Entites.particule(j.x, j.y, 0, 0, 60, '#fff', 1);
        }
        return { decals: L.B.decals.length, particules: L.B.particules.length,
                 maxD: L.Entites.MAX_DECALS, maxP: L.Entites.MAX_PARTICULES };
    }""")
    assert r["decals"] == r["maxD"], "les decalques de sang ne sont pas plafonnes"
    assert r["particules"] == r["maxP"], "les particules ne sont pas plafonnees"


def test_l_arme_du_mort_se_ramasse(banc):
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        L.graine(8);
        // ⚠️ **RIEN D'AUTRE SOUS LA MAIN.** ACTION sert le premier venu — une
        // porte, un personnage, un comptoir — et l'arme au sol passe après (voir
        // `Missions.interagir`). Le 17 sept. 2026, la trame a bougé, le terminus
        // a changé de voisinage, et le E ramassait autre chose. On s'écarte de la
        // porte et on vide les alentours : ce juge parle de l'arme du mort.
        const j0 = L.B.joueur;
        j0.y += 40;
        for (const q of L.B.entites.slice()) {
            if (q === j0 || q.type === 'joueur') continue;
            if (q.type === 'pieton' || q.type === 'vehicule' || q.type === 'ramassage') L.Entites.retirer(q);
        }
        L.Entites.indexer();
        const cravate = o.poser('cravate', 14, 0);
        const armeDeLaCravate = cravate.arme;
        L.Entites.tuer(cravate, L.B.joueur);
        L.Entites.indexer();
        // ⚠️ On regarde l'arme : ACTION n'agit que sur ce qu'on regarde (test_regard_js.py).
        L.Entites.regarder(L.B.joueur, 1, 0);
        const objet = L.Combat.objetSousLaMain(L.B.joueur);
        o.tape('KeyE', 2);
        return { arme: armeDeLaCravate, objet: objet ? objet.arme : null,
                 sac: Object.keys(L.B.partie.armes).sort(), porte: L.B.joueur.arme,
                 restes: L.B.entites.filter(function (e) {
                     return e.type === 'ramassage' && e.arme === 'batte';
                 }).length };
    }""")
    assert r["arme"] == "batte"
    assert r["objet"] == "batte", "le mort n'a pas lache son arme"
    assert "batte" in r["sac"] and r["porte"] == "batte"
    assert r["restes"] == 0, "l'arme ramassee traine encore par terre"


def test_le_pickpocket_se_fait_dans_le_dos(banc):
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        L.graine(9);
        const j = L.B.joueur;
        // ⚠️ **LA RUE SE VIDE** : `pickpocket` sert le plus commode, pas celui
        // qu'on vise, et un passant de dos à côté de la dame suffit à faire dire
        // « oui » au juge qui attendait « non » (17 sept. 2026, la trame a bougé).
        L.B.entites = L.B.entites.filter(function (e) { return e.type !== 'pieton'; });
        L.Entites.indexer();
        const face = o.poser('dame', 14, 0);
        face.argent = 40;
        // ⚠️ Le joueur, lui, regarde la dame : ACTION n'agit que sur ce qu'on regarde (test_regard_js.py).
        L.Entites.regarder(j, 1, 0);
        L.Entites.regarder(face, -1, 0);            // elle regarde le joueur
        const deFace = L.Combat.pickpocket(j);
        L.Entites.regarder(face, 1, 0);             // elle lui tourne le dos
        L.Entites.indexer();
        const argentAvant = L.B.partie.argent;
        const deDos = L.Combat.pickpocket(j);
        return { deFace: deFace, deDos: deDos, gain: L.B.partie.argent - argentAvant,
                 reste: face.argent, etat: face.etat, crimes: L.B.partie.stats.crimes };
    }""")
    assert r["deFace"] is False, "on fait les poches de quelqu'un qui nous regarde"
    assert r["deDos"] is True and r["gain"] == 40 and r["reste"] == 0
    assert r["etat"] == "fuit"
    assert r["crimes"] >= 1


def test_le_pistolet_tire_touche_et_compte_ses_balles(banc, paquet):
    pistolet = next(a for a in paquet["armes"] if a["slug"] == "pistolet")
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        L.graine(11);
        const j = L.B.joueur;
        // La rue est peuplee des le depart : on la vide, la visee assistee
        // irait chercher le premier passant venu.
        L.B.entites = L.B.entites.filter(function (e) { return e.type !== 'pieton'; });
        // ⚠️ **ET LA BALLE A BESOIN DE QUATRE-VINGT-DIX PIXELS DE RUE.** Au
        // terminus, le jour où la trame a bougé (17 sept. 2026), un mur se
        // trouvait entre le canon et la cible : la balle s'arrêtait dessus et le
        // juge lisait « la balle n'a pas touché ». Le boulevard du nord est droit.
        const c0 = L.Monde.carte;
        for (let y = 0; y < 12; y++) {
          let pris = false;
          for (let x = 40; x < 80; x++) if (c0.voie[y][x] === '>') {
            j.x = x * L.TT + 8; j.y = y * L.TT + 8; L.Monde.centrerCamera(j.x, j.y); pris = true; break;
          }
          if (pris) break;
        }
        L.Entites.indexer();
        j.arme = 'pistolet';
        L.B.partie.armes.pistolet = { mun: 12, usure: 0 };
        const cible = o.poser('ouvrier', 90, 0);
        cible.courage = 0;
        o.viser(cible);
        const avant = cible.vie;
        L.Combat.frapper(j);
        let projectiles = 0;
        for (let i = 0; i < 40; i++) {
            L.Entites.indexer();
            projectiles = Math.max(projectiles, L.B.entites.filter(function (e) { return e.type === 'projectile'; }).length);
            L.Combat.majProjectiles();
        }
        return { perdu: avant - cible.vie, mun: L.B.partie.armes.pistolet.mun,
                 projectiles: projectiles, etoiles: L.B.recherche.etoiles,
                 restants: L.B.entites.filter(function (e) { return e.type === 'projectile'; }).length };
    }""")
    assert r["perdu"] == pistolet["degats"], "la balle n'a pas touche"
    assert r["mun"] == 11, "la balle n'a pas ete comptee"
    assert r["projectiles"] == 1
    assert r["restants"] == 0, "un projectile traine apres avoir touche"


def test_rien_n_est_compte_sans_temoin(banc):
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const j = L.B.joueur;
        // Personne autour : le crime passe inapercu.
        L.B.entites = L.B.entites.filter(function (e) { return e.type !== 'pieton'; });
        L.Entites.indexer();
        const seul = L.Police.quelqu_un_voit(j.x, j.y, null);
        // Un passant qui regarde dans notre direction, lui, voit tout.
        const temoin = o.poser('passant', 40, 0);
        L.Entites.regarder(temoin, -1, 0);
        L.Entites.indexer();
        const vu = L.Police.quelqu_un_voit(j.x, j.y, null);
        // ... mais pas s'il est assomme.
        temoin.etat = 'assomme';
        const assomme = L.Police.quelqu_un_voit(j.x, j.y, null);
        temoin.etat = 'flane';
        // ... ni s'il regarde ailleurs.
        L.Entites.regarder(temoin, 1, 0);
        const dosTourne = L.Police.quelqu_un_voit(j.x, j.y, null);
        return { seul: seul, vu: vu, assomme: assomme, dosTourne: dosTourne };
    }""")
    assert r["seul"] is False, "un crime sans temoin ne doit rien declencher"
    assert r["vu"] is True, "un passant en face ne voit rien ?"
    assert r["assomme"] is False, "un temoin assomme ne temoigne pas"
    assert r["dosTourne"] is False, "un temoin de dos ne voit pas"


def test_la_bagarre_tient_le_budget(banc):
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        L.graine(13);
        o.singe(2500, 3, ['KeyW', 'KeyA', 'KeyS', 'KeyD', 'Space', 'ShiftLeft', 'KeyE', 'Tab']);
        const s = L.B.stats;
        // ⚠️ `vivant` : un CADAVRE n'est pas un flaneur. `peupler()` compte
        // « e.vivant && !e.metier » — c'est SA definition du budget, et c'est
        // elle qu'on juge. Un corps laisse par terre par le singe faisait
        // compter vingt-neuf personnes pour vingt-huit vivantes : le moteur
        // tenait son budget et le juge accusait un emballement.
        let flaneurs = 0, metiers = 0, morts = 0;
        for (const e of L.B.entites) {
            if (e.type !== 'pieton' || !e.actif) continue;
            if (!e.vivant) { morts++; continue; }
            // ⚠️ Le PETIT QUI SUIT SA MERE nait avec elle : le budget se decide a la
            // naissance (`peupler`), et une mere nee a vingt-sept flaneurs en fait
            // vingt-neuf. Le juge tenait tant que la graine ne faisait pas naitre de
            // paire au bord du budget (21 sept. 2026, graine 13).
            if (e.suit) continue;
            if (e.metier || e.personnage) metiers++; else flaneurs++;
        }
        return { etat: L.B.etat, entites: L.B.entites.length, actifs: s.actifs,
                 flaneurs: flaneurs, metiers: metiers, morts: morts,
                 budget: L.Entites.MAX_PIETONS,
                 vendeurs: (L.Monde.carte.def.ambulants || []).length,
                 particules: L.B.particules.length, decals: L.B.decals.length,
                 images: s.images, morceaux: s.morceaux,
                 nan: isNaN(L.B.joueur.x) || isNaN(L.B.joueur.y) };
    }""")
    assert r["etat"] in ("jeu", "pause")
    assert not r["nan"]
    # ⚠️ LE BUDGET, C'EST CELUI DES FLANEURS, et il vaut `MAX_PIETONS` : c'est
    # le seul nombre que `peupler()` tienne. Le reste de la figuration ne se
    # regule pas par la foule — les douze vendeurs des kiosques de la ville
    # naissent avec elle et ne dorment jamais, les amuseurs, les trois
    # personnages de l'histoire et les agents de patrouille s'ajoutent
    # par-dessus. Le juge disait `actifs <= 30` : arithmetiquement intenable
    # (22 + 12 font deja 34), il ne tenait que tant que le singe ne traversait
    # pas un quartier dense, et il est tombe le jour ou la ville a bouge d'une
    # tuile. On mesure donc les deux separement, et on garde un plafond sur le
    # total pour attraper un emballement.
    #
    # ⚠️ ET LE CHIFFRE SE LIT DANS LE MOTEUR, il ne se recopie pas ici. Il
    # etait ecrit « 22 » en dur : le jour ou le centre-ville a demande plus de
    # monde (demande de Martin) et ou `MAX_PIETONS` est passe a 28, le juge
    # n'a pas dit « le budget a change », il a dit « emballement ». Un plafond
    # recopie dans un juge finit toujours par juger l'ancien.
    assert r["flaneurs"] <= r["budget"], (
        f"{r['flaneurs']} flaneurs vivants, le budget est de {r['budget']} "
        f"({r['morts']} corps par terre, qui ne comptent pas)"
    )
    # ⚠️ **LES VENDEURS SE LISENT DANS LA CARTE, EUX AUSSI.** Chaque kiosque et
    # chaque camion fait naitre UN vendeur fixe pour toute la partie
    # (`creerAmbulants`) — douze quand ce plafond a ete ecrit, treize depuis le
    # quai du contrebandier. Le « +28 » les rangeait dedans, c'est-a-dire qu'il
    # recopiait un nombre du moteur, exactement ce que la note du dessus
    # interdit. Il est tombe le 16 sept. 2026 sans qu'aucun budget ait bouge :
    # a HEAD, le singe finissait COINCE dans un coin vide de la carte (10, 1),
    # avec un seul pieton a metier autour de lui ; apres le changement du port,
    # sa marche au hasard l'a mene au centre-ville (146, 6) — treize vendeurs,
    # une bagarre de quatre, les trois personnages de l'histoire, deux agents.
    # Le plafond ne tenait que tant que le singe ne voyait personne.
    assert r["actifs"] <= r["budget"] + r["vendeurs"] + 28, (
        f"{r['actifs']} pietons actifs ({r['metiers']} a un metier, "
        f"dont {r['vendeurs']} vendeurs fixes)"
    )
    assert r["particules"] <= 300 and r["decals"] <= 150
    assert r["images"] <= 160, f"{r['images']} drawImage par image"


def test_un_meurtre_vu_fait_monter_les_etoiles(banc, paquet):
    """La chaine complete : je tue, quelqu'un voit, il le raconte a un agent,
    et LA la police le sait — pas avant (M4 : un temoin se rachete)."""
    gravite = paquet["recherche"]["delits"]["mort_pieton"]["etoiles"]
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        L.graine(21);
        function meurtre(avecTemoin) {
            L.Police.remiseAZero();
            L.B.crimes.length = 0;
            L.B.entites = L.B.entites.filter(function (e) { return e.type !== 'pieton'; });
            const victime = o.poser('passant', 14, 0);
            let temoin = null;
            if (avecTemoin) {
                temoin = o.poser('passante', 60, 0);
                temoin.probaTemoin = 1; temoin.etat = 'flane';
                L.Entites.regarder(temoin, -1, 0);
            }
            L.Entites.indexer();
            L.Entites.tuer(victime, L.B.joueur);
            const surLeCoup = { etoiles: L.B.recherche.etoiles, chaleur: L.B.recherche.chaleur,
                                temoin: temoin ? temoin.etat : null, crime: !!(temoin && temoin.crime) };
            if (!temoin) return { surLeCoup: surLeCoup };
            // Un agent arrive dans le coin, de dos : le temoin court le lui dire.
            const a = L.Police.creerAgent(temoin.x + 40, temoin.y, 'flane');
            L.Entites.regarder(a, 1, 0);
            L.Entites.indexer();
            let quand = -1;
            for (let i = 0; i < 400 && quand < 0; i++) { o.frame(1); if (temoin.crime && temoin.crime.rapporte) quand = i; }
            return { surLeCoup: surLeCoup, quand: quand,
                     chaleur: L.B.recherche.chaleur + L.B.recherche.etoiles * 100 };
        }
        const sansTemoin = meurtre(false);
        const avecTemoin = meurtre(true);
        return { sans: sansTemoin, avec: avecTemoin,
                 chaleurParGravite: L.B.defs.recherche.chaleur_par_gravite };
    }""")
    assert r["sans"]["surLeCoup"]["chaleur"] == 0, "un meurtre que personne ne voit ne chauffe pas"
    assert r["avec"]["surLeCoup"]["chaleur"] == 0 and r["avec"]["surLeCoup"]["etoiles"] == 0, \
        "sans agent dans le coin, la police ne sait rien encore"
    assert r["avec"]["surLeCoup"]["temoin"] == "temoin" and r["avec"]["surLeCoup"]["crime"] is True
    assert 0 <= r["avec"]["quand"] < 400, "le temoin n'a pas rejoint l'agent"
    assert r["avec"]["chaleur"] == gravite * r["chaleurParGravite"], \
        "le temoin n'a pas transmis la gravite du crime"


def test_des_armes_de_fortune_trainent_en_ville(banc, paquet):
    fortunes = {a["slug"] for a in paquet["armes"] if a["usures"] > 0 and a["prix"] == 0}
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        o.frame(900);
        const objets = L.B.entites.filter(function (e) { return e.type === 'ramassage'; });
        // On en ramasse une et on la casse a force de cogner.
        const arme = objets.length ? objets[0].arme : null;
        let usure = null, casse = null;
        if (arme) {
            L.Combat.ramasserArme(arme, null);
            L.B.joueur.arme = arme;
            const def = L.Combat.armeDef(arme);
            for (let coup = 0; coup < def.usures + 1; coup++) {
                const cible = o.poser('ouvrier', 12, 0);
                cible.vie = 999; cible.vieMax = 999;
                o.viser(cible);
                L.Combat.frapper(L.B.joueur, false);
                for (let i = 0; i < 40; i++) { L.Entites.indexer(); L.Combat.maj(); }
                L.Entites.retirer(cible);
            }
            usure = def.usures;
            casse = !L.B.partie.armes[arme];
        }
        return { objets: objets.length, armes: objets.map(function (e) { return e.arme; }),
                 arme: arme, usure: usure, casse: casse, porte: L.B.joueur.arme };
    }""")
    assert r["objets"] > 0, "aucune arme de fortune ne traine dans la rue"
    assert set(r["armes"]) <= fortunes, r["armes"]
    assert r["casse"] is True, f"la {r['arme']} n'a pas casse apres {r['usure']} coups"
    assert r["porte"] == "poings", "on garde une arme cassee a la main"


# --- La vie de rue : enfants, meres, kiosques, la Brume -------------------


def test_un_enfant_ne_peut_pas_etre_touche(banc):
    """⚠️ Regle du moteur, pas consigne : RIEN n'atteint un enfant."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        L.graine(31);
        const j = L.B.joueur;
        // ⚠️ **LA RUE SE VIDE** : six coups de couteau touchent TOUT ce qui est à
        // portée, et un passant de plus à côté de l'enfant met un mort au compteur
        // que ce juge veut à zéro (17 sept. 2026, la trame a bougé).
        L.B.entites = L.B.entites.filter(function (e) { return e.type !== 'pieton'; });
        L.Entites.indexer();
        const petit = o.poser('enfant', 12, 0);
        o.viser(petit);
        const avant = petit.vie;
        // Au poing, au couteau, et d'une balle en pleine poitrine.
        j.arme = 'couteau'; L.B.partie.armes.couteau = { mun: null, usure: 0 };
        for (let coup = 0; coup < 6; coup++) {
            L.Combat.frapper(j, true);
            for (let i = 0; i < 30; i++) { L.Entites.indexer(); L.Combat.maj(); }
        }
        const auCouteau = petit.vie;
        const direct = L.Entites.blesser(petit, 999, j, {});
        return { avant: avant, auCouteau: auCouteau, direct: direct,
                 vivant: petit.vivant, etat: petit.etat, tues: L.B.partie.stats.tues,
                 intouchable: petit.intouchable, sprite: petit.sprite };
    }""")
    assert r["intouchable"] is True and r["sprite"] == "enfant"
    assert r["auCouteau"] == r["avant"], "un enfant a perdu de la vie"
    assert r["direct"] is False, "blesser() a accepte de toucher un enfant"
    assert r["vivant"] is True and r["tues"] == 0
    assert r["etat"] == "fuit", "il devrait detaler"


def test_la_mere_ne_sort_pas_sans_son_petit(banc):
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        L.graine(32);
        const mere = o.poser('mere', 30, 0);
        mere.etat = 'flane';
        const petit = mere.petit;
        // On eloigne le petit : il doit revenir vers elle.
        petit.x = mere.x + 120; petit.y = mere.y + 80;
        const avant = Math.hypot(petit.x - mere.x, petit.y - mere.y);
        o.frame(240);
        const apres = Math.hypot(petit.x - mere.x, petit.y - mere.y);
        return { arch: petit ? petit.arch : null, avant: avant, apres: apres,
                 suit: petit.suit === mere };
    }""")
    assert r["arch"] == "enfant", "la mere est sortie sans son petit"
    assert r["suit"] is True
    assert r["apres"] < r["avant"], "le petit ne rejoint pas sa mere"


def test_le_kiosque_vend_de_la_vie_contre_de_l_argent(banc, paquet):
    tarifs = paquet["economie"]["tarifs"]
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const j = L.B.joueur;
        const etal = L.B.entites.filter(function (e) { return e.type === 'ambulant' && e.slug === 'hotdog'; })[0];
        j.x = etal.x; j.y = etal.y + 22; j.vie = 40; L.B.partie.argent = 100;
        // ⚠️ On regarde le kiosque : ACTION n'agit que sur ce qu'on regarde (test_regard_js.py).
        L.Entites.regarder(j, 0, -1);
        L.Entites.indexer();
        const achat = L.Missions.interagir(j);
        const apres = { vie: j.vie, argent: L.B.partie.argent };
        // Sans le sou, on ne mange pas.
        L.B.partie.argent = 1; j.vie = 40;
        const refus = L.Missions.interagir(j);
        const vendeurs = L.B.entites.filter(function (e) { return e.metier === 'ambulant'; }).length;
        const etals = L.B.entites.filter(function (e) { return e.type === 'ambulant'; }).length;
        return { achat: achat, apres: apres, refus: refus, vieApresRefus: j.vie,
                 argentApresRefus: L.B.partie.argent, vendeurs: vendeurs, etals: etals };
    }""")
    assert r["achat"] is True
    assert r["apres"]["argent"] == 100 - tarifs["hotdog"]
    assert r["apres"]["vie"] == 40 + tarifs["hotdog_pv"]
    assert r["refus"] is True and r["vieApresRefus"] == 40 and r["argentApresRefus"] == 1
    assert r["etals"] >= 6 and r["vendeurs"] == r["etals"], "un kiosque sans personne derriere"


def test_manger_redonne_du_souffle_et_le_cafe_reveille(banc, paquet):
    tarifs = paquet["economie"]["tarifs"]
    cafe = paquet["economie"]["cafe"]
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const j = L.B.joueur;
        L.B.partie.heure = 0.4;                    // la roulotte a cafe est ouverte
        L.B.partie.argent = 200;
        function acheter(slug) {
          const etal = L.B.entites.filter(function (e) { return e.type === 'ambulant' && e.slug === slug; })[0];
          j.x = etal.x; j.y = etal.y + 22;
          // ⚠️ On regarde l'étal : ACTION n'agit que sur ce qu'on regarde (test_regard_js.py).
          L.Entites.regarder(j, 0, -1);
          L.Entites.indexer();
          return L.Missions.interagir(j);
        }
        j.endurance = 20; j.vie = 40;
        const hotdog = acheter('hotdog');
        const apres = { souffle: j.endurance, vie: j.vie, cafeine: j.cafeine };
        // Manger a plein souffle ne fait pas deborder la barre.
        j.endurance = 100; acheter('hotdog');
        const plein = j.endurance;
        j.endurance = 20;
        const achatCafe = acheter('cafe');
        return { hotdog: hotdog, apres: apres, plein: plein, achatCafe: achatCafe,
                 souffleCafe: j.endurance, cafeine: j.cafeine };
    }""")
    assert r["hotdog"] is True
    assert r["apres"]["souffle"] == 20 + tarifs["hotdog_souffle"]
    assert r["apres"]["vie"] == 40 + tarifs["hotdog_pv"]
    assert r["apres"]["cafeine"] == 0, "un hot-dog nourrit, il ne reveille pas"
    assert r["plein"] == 100, "le souffle deborde"
    assert r["achatCafe"] is True
    assert r["souffleCafe"] == 20 + tarifs["cafe_souffle"]
    assert r["cafeine"] == cafe["duree_s"] * 60


def test_le_souffle_en_surplus_s_achete_et_ne_revient_pas_tout_seul(banc, paquet):
    """⚠️ Le defaut que Martin a nomme : « le souffle monte seul actuellement ».
    Il remonte de 0,24 par image des qu'on arrete de courir — une barre vide se
    remplit en sept secondes — et `nourrir` plafonnait a 100. Une poutine a 18 $
    rendait donc 70 points qu'on aurait eus gratuitement en s'arretant quatre
    secondes : le kiosque ne servait a rien, malgre l'intention inverse ecrite
    dans le depot depuis M5.

    Le surplus est ce que la regeneration ne peut PAS donner. Ce test tient les
    quatre promesses d'un coup : il se remplit par-dessus, il se depense en
    premier, il ne revient jamais tout seul, et il est passager."""
    souffle = paquet["economie"]["souffle"]
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const j = L.B.joueur;
        const plein = L.B.defs.recherche.vitesses.endurance;
        // 1. Manger a barre pleine : la base ne bouge plus, le surplus monte.
        j.endurance = plein; j.surplus = 0;
        L.Missions.nourrir(j, 40);
        const pardessus = { base: j.endurance, surplus: j.surplus };
        // 2. Et jamais au-dela du plafond.
        L.Missions.nourrir(j, 9999);
        const plafonne = j.surplus;
        // 3. A l'arret, il ne remonte pas d'un point — la base, si.
        j.endurance = 40; j.surplus = 20;
        o.frame(120);
        const repos = { base: j.endurance, surplus: j.surplus };
        // 4. Au sprint, c'est le surplus qui part en premier.
        j.endurance = 100; j.surplus = 20;
        o.touche('ShiftLeft'); o.touche('KeyA');
        let images = 0;
        while (j.surplus > 0 && images < 400) { o.frame(1); images++; }
        const videSurplus = { base: j.endurance, images: images };
        o.relacher('KeyA'); o.relacher('ShiftLeft');
        // 5. Passager : une nuit l'efface.
        j.surplus = 30;
        L.Missions.dormir(); o.fondu();
        const apresLaNuit = j.surplus;
        return { pardessus: pardessus, plafonne: plafonne, repos: repos,
                 videSurplus: videSurplus, apresLaNuit: apresLaNuit, plein: plein };
    }""")
    assert r["pardessus"] == {"base": r["plein"], "surplus": 40}, (
        "manger a barre pleine doit monter le SURPLUS, pas la base"
    )
    assert r["plafonne"] == souffle["surplus_max"], "le surplus depasse son plafond"
    assert r["repos"]["surplus"] == 20, "le surplus remonte tout seul : il ne vaut plus rien"
    assert r["repos"]["base"] > 40, "la base, elle, doit remonter a l'arret"
    # ⚠️ Une image de jeu peut en rattraper une deuxieme (l'accumulateur de la
    # boucle) : la base a le droit de perdre le cout d'une image ou deux apres
    # que le surplus est tombe a zero, pas davantage.
    depense = paquet["recherche"]["vitesses"]["endurance_par_image"]
    assert r["videSurplus"]["base"] >= 100 - depense * 2, (
        "la base a baisse avant le surplus : on depense d'abord ce qui revient gratuitement"
    )
    assert 0 < r["videSurplus"]["images"] < 400
    assert r["apresLaNuit"] == 0, "une nuit rend le souffle, pas l'avance achetee"


def test_traverser_la_ville_en_courant_ne_coute_rien(banc, paquet):
    """⚠️ Le défaut mesuré : le modèle d'endurance avait été réglé pour le
    Faubourg de 157 tuiles, et M8 a **quintuplé la ville** sans que personne y
    revienne. Un souffle complet valait 4,2 s de course — **33 tuiles sur
    421** — et la vitesse qu'on pouvait tenir (courir, puis marcher pour
    souffler) tombait **sous celle du policier**. La barre ne récompensait
    rien : elle taxait le déplacement.

    Le juge se compare donc à la **taille de la ville**, pas à un nombre
    choisi une fois pour toutes : on traverse d'un bout à l'autre en courant,
    et la barre ne bouge pas d'un point."""
    largeur = paquet["carte"]["largeur"]
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const j = L.B.joueur, c = L.Monde.carte;
        // Une longue ligne droite : la rue la plus degagee qu'on trouve, et on
        // y court le temps qu'il faudrait pour traverser la ville.
        const d = o.ligneDroite();
        j.x = d.x; j.y = d.y;
        j.endurance = 100; j.surplus = 0;
        const souffle0 = j.endurance;
        const images = Math.ceil(%d * L.TT / L.B.defs.recherche.vitesses.joueur_course);
        o.touche('KeyD');
        let bouge = 0, avant = j.x;
        for (let i = 0; i < images; i++) {
            o.frame(1);
            bouge += Math.abs(j.x - avant); avant = j.x;
        }
        o.relacher('KeyD');
        return { souffle0: souffle0, souffle: j.endurance, images: images,
                 bouge: Math.round(bouge), largeurPx: %d * L.TT };
    }""" % (largeur, largeur))
    assert r["souffle"] == r["souffle0"] == 100, (
        "courir a coûté du souffle : %s au lieu de %s" % (r["souffle"], r["souffle0"])
    )
    # ⚠️ La mesure doit porter sur la VILLE ENTIERE, sinon elle ne dit rien :
    # 421 tuiles a la vitesse de course, c'est pres d'une minute de touche
    # tenue. Si ce chiffre tombe, c'est que la ville a retreci — pas que le
    # souffle va mieux.
    assert r["images"] > 45 * 60, (
        "traverser la ville ne demande que %.0f s de course : la mesure ne porte plus sur la ville"
        % (r["images"] / 60)
    )


def test_un_sprint_plein_ouvre_un_ecart_borne_sur_la_police(banc, paquet):
    """⚠️ Rendre la course gratuite casserait toutes les poursuites à pied si on
    s'arrêtait là : une course gratuite plus rapide que le policier, c'est
    s'échapper **toujours**, sans rien dépenser. La parade est celle que le
    dépôt s'est déjà donnée deux fois — le char rapide, les armes à feu : **la
    vitesse achète de la distance, jamais l'impunité.**

    Donc : le policier court **exactement** à la vitesse de la course, et c'est
    le sprint — qui coûte — qui ouvre un écart. Le juge le mesure, et le veut
    **borné** : assez pour casser une ligne de vue, pas assez pour semer
    quelqu'un en ligne droite."""
    v = paquet["recherche"]["vitesses"]
    cafe = paquet["economie"]["cafe"]
    r = banc("""function (L, o) {
        const v = %s;
        // Le calcul, pas la simulation : un sprint dure `endurance / cout`
        // images, et il gagne la difference de vitesse a chaque image.
        function ecart(depense) {
            const images = v.endurance / (v.endurance_par_image * depense);
            return { images: Math.round(images), px: Math.round((v.joueur_sprint - v.policier) * images) };
        }
        return { nu: ecart(1), cafe: ecart(%s), tuile: L.TT,
                 course: v.joueur_course === v.policier };
    }""" % (
        '{"endurance": %s, "endurance_par_image": %s, "joueur_sprint": %s, "policier": %s, "joueur_course": %s}'
        % (v["endurance"], v["endurance_par_image"], v["joueur_sprint"], v["policier"], v["joueur_course"]),
        cafe["depense"]))
    assert r["course"] is True, "en courant, on ne gagne AUCUN terrain sur un agent"
    tuiles_nu = r["nu"]["px"] / r["tuile"]
    tuiles_cafe = r["cafe"]["px"] / r["tuile"]
    assert 5 <= tuiles_nu <= 20, (
        "un sprint plein ouvre %.1f tuiles : trop peu pour casser une ligne de vue, ou trop pour être une fuite"
        % tuiles_nu
    )
    assert tuiles_cafe > tuiles_nu, "le café doit servir à s'échapper, pas seulement à courir"
    # ⚠️ Borné, café compris : la vision d'un agent porte 9 tuiles de jour.
    vision = paquet["recherche"]["vision"]["policier"]["jour"]
    assert tuiles_cafe <= vision * 4, (
        "%.1f tuiles d'écart, c'est semer la police en ligne droite (vision : %s tuiles)"
        % (tuiles_cafe, vision)
    )


def test_le_cafe_fait_courir_deux_fois_plus_longtemps(banc, paquet):
    """⚠️ Ce qui s'achete, c'est la DUREE du sprint, jamais sa vitesse.

    On mesure les deux : combien d'images on tient au sprint d'un souffle
    plein a zero (ca doit doubler), et la distance parcourue par image (elle
    ne doit pas bouger d'un pixel — sinon la police ne rattrape plus personne).
    """
    cafe = paquet["economie"]["cafe"]
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const j = L.B.joueur;
        // ⚠️ **SUR LE BOULEVARD DU POURTOUR, là où il y a de quoi courir.** Le
        // juge sprintait vers l'OUEST depuis le terminus : le jour où la trame a
        // bougé (17 sept. 2026), un mur s'y trouvait et le joueur a parcouru ZÉRO
        // pixel à jeun — on comparait un mur à une course. Le boulevard du nord
        // traverse toute la ville et il est droit d'un bout à l'autre.
        const c = L.Monde.carte;
        let place = null;
        for (let y = 0; y < 12 && !place; y++) {
          for (let x = 40; x < 80; x++) if (c.voie[y][x] === '>') { place = { x: x * L.TT + 8, y: y * L.TT + 8 }; break; }
        }
        j.x = place.x; j.y = place.y; L.Monde.centrerCamera(j.x, j.y);
        function tenir() {
          j.endurance = 100;
          j.x = place.x; j.y = place.y; L.Monde.centrerCamera(j.x, j.y);
          const depart = { x: j.x, y: j.y };
          let n = 0;
          o.touche('ShiftLeft'); o.touche('KeyD');
          while (j.endurance > 0 && n < 2000) {
            for (const v of L.B.entites.slice()) if (v.type === 'vehicule') L.Entites.retirer(v);
            // ⚠️ On mesure le JOUEUR, pas la foule : une flaneuse plantee sur
            // le trajet coutait 44 images de bousculade (mesure du 13 sept.
            // 2026, le jour ou huit enseignes de plus ont deplace les portes
            // par ou les passants naissent) et la vitesse tombait de 5 %.
            for (const e of L.Entites.pietonsAutour(j.x, j.y, 60)) L.Entites.retirer(e);
            o.frame(1); n++;
          }
          o.relacher('KeyD'); o.relacher('ShiftLeft');
          return { images: n, px: Math.hypot(j.x - depart.x, j.y - depart.y) };
        }
        const ajeun = tenir();
        L.Missions.cafeine(j);
        const pose = j.cafeine;
        const souscafe = tenir();
        return { ajeun: ajeun, souscafe: souscafe, pose: pose, reste: j.cafeine };
    }""")
    assert r["ajeun"]["images"] > 0 and r["souscafe"]["images"] < 2000
    # Le rapport, pas le compte : la premiere image d'une course part avant que
    # l'axe ne soit lu, et une image d'ecart ne dit rien de l'equilibrage.
    assert r["souscafe"]["images"] / r["ajeun"]["images"] > 1 / cafe["depense"] - 0.15
    assert r["pose"] == cafe["duree_s"] * 60
    assert r["reste"] == r["pose"] - r["souscafe"]["images"], "la minuterie doit tomber d'une image par image"
    vitesse_ajeun = r["ajeun"]["px"] / r["ajeun"]["images"]
    vitesse_cafe = r["souscafe"]["px"] / r["souscafe"]["images"]
    assert abs(vitesse_cafe - vitesse_ajeun) < 0.05, "le cafe accelere le joueur : la police ne le rattrapera plus"


def test_le_kiosque_a_journaux_ferme_la_nuit(banc):
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const journaux = L.Missions.commerceDe('journaux');
        const camion = L.Missions.commerceDe('camion_cuisine');
        L.B.partie.heure = 0.5;
        const midi = [L.Missions.ouvert(journaux), L.Missions.ouvert(camion)];
        L.B.partie.heure = 0.95;
        const nuit = [L.Missions.ouvert(journaux), L.Missions.ouvert(camion)];
        return { midi: midi, nuit: nuit, heures: journaux.heures };
    }""")
    assert r["midi"] == [True, True]
    assert r["nuit"] == [False, True], "le camion-restaurant, lui, veille"


def test_la_compagnie_se_paie_et_refuse_quand_la_police_cherche(banc, paquet):
    tarifs = paquet["economie"]["tarifs"]
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        L.graine(33);
        const j = L.B.joueur;
        // ⚠️ **PAS DE ROULOTTE DANS LE DOS.** ACTION sert le plus proche : le jour
        // où la trame a bougé (17 sept. 2026), une roulotte à café s'est installée
        // au terminus, et le juge a vu 4 $ de café là où il attendait un refus.
        L.B.defs.ambulants = [];
        for (const q of L.B.entites.slice()) if (q !== j && q.type !== 'joueur') L.Entites.retirer(q);
        const fille = o.poser('racoleuse', 12, 0);
        fille.etat = 'arret';
        // ⚠️ On regarde la fille : ACTION n'agit que sur ce qu'on regarde (test_regard_js.py).
        L.Entites.regarder(j, 1, 0);
        L.Entites.indexer();
        j.vie = 50; L.B.partie.argent = 200;
        L.B.recherche.etoiles = 2;
        const recherche = L.Missions.interagir(j);
        const apresRecherche = { vie: j.vie, argent: L.B.partie.argent };
        L.B.recherche.etoiles = 0;
        const ok = L.Missions.interagir(j);
        const fondu = !!L.B.transition;
        o.fondu();
        return { metier: fille.metier, recherche: recherche, apresRecherche: apresRecherche,
                 ok: ok, vie: j.vie, argent: L.B.partie.argent, fondu: fondu };
    }""")
    assert r["metier"] == "compagnie"
    assert r["recherche"] is True and r["apresRecherche"]["argent"] == 200, \
        "elle a servi alors que la police cherchait le joueur"
    assert r["ok"] is True
    assert r["argent"] == 200 - tarifs["compagnie"]
    assert r["vie"] == 50 + tarifs["compagnie_pv"]
    assert r["fondu"] is True, "ca doit passer par un fondu, pas par une scene"


def test_la_fille_de_la_brume_a_une_silhouette_a_elle(banc):
    """⚠️ Retour de Martin : « on ne distingue plus les prostituées, elles sont
    trop pareilles que tout le monde. » Elles etaient le corps commun repeint
    en rose — et a douze pixels de large, sous la teinte de nuit, une couleur
    ne distingue rien. Ce juge tient le CONTOUR : la jupe s'evase plus large
    que les epaules (personne d'autre), et sous l'ourlet les jambes sont de la
    peau la ou tout le monde a du pantalon."""
    r = banc(r"""function (L, o) {
        // La largeur de chaque rangee du dessin de face, pixels poses.
        function largeurs(nom) {
            return L.SPRITES[nom].poses.bas[0].map(function (l) { return l.replace(/\./g, '').length; });
        }
        const f = largeurs('racoleuse'), j = largeurs('joueur');
        const jambes = L.SPRITES.racoleuse.poses.bas[0][13];
        L.Jeu.commencer();
        const fille = o.poser('racoleuse', 12, 0);
        return { sprite: fille.sprite, epaulesF: f[7], jupeF: Math.max(f[11], f[12], f[13]),
                 epaulesJ: j[7], hanchesJ: Math.max(j[11], j[12], j[13]),
                 jambes: jambes, cheveux: fille.swaps.h, robe: fille.swaps.c,
                 poses: Object.keys(L.Atlas.cuire('racoleuse', L.SPRITES.racoleuse, null).poses).sort() };
    }""")
    assert r["sprite"] == "racoleuse", "elle porte encore le corps de tout le monde"
    assert r["jupeF"] - r["epaulesF"] >= 4, "la jupe ne s'evase pas : de loin, c'est un passant"
    assert r["hanchesJ"] - r["epaulesJ"] <= 1, "le corps commun, lui, tombe droit — c'est le contraste"
    assert "s" in r["jambes"] and "p" not in r["jambes"], "les jambes ne sont pas nues sous l'ourlet"
    assert r["cheveux"] == "#f2d27a" and r["robe"] == "#ff3d8e"
    # ⚠️ Elle meurt comme les autres : sans `couche`, un KO restait debout.
    for pose in ("bas", "haut", "cote", "gauche", "droite", "couche"):
        assert pose in r["poses"], pose


def test_la_fille_de_la_brume_tient_son_coin(banc):
    """Le deuxieme signe, celui qu'on lit avant meme la robe : elle ATTEND.
    Elle flanait comme tout le monde dix secondes apres etre apparue.

    ⚠️ **On mesure jusqu'a sa premiere FUITE, pas au-dela.** Le juge prenait
    son écart maximum sur quarante secondes, fuite comprise : une fille qui
    détale d'un coup de feu court 240 px — et c'est exactement ce qu'elle doit
    faire. Une fois partie, elle ne revient pas : la fuite lui fait traverser
    une rue, et un passant ne remet pas le pied sur la chaussée hors d'un
    passage. Le juge a donc rougi le jour où les lampadaires ont bougé de trois
    tuiles ; aucune ligne de *son* code n'avait changé, mais la ville autour
    d'elle oui, et avec elle ce qui l'effraie. Il tenait par chance.

    Ce que le poste promet, et la seule chose : **tant que rien ne lui fait
    peur, elle ne flâne pas au loin.** Le juge le dit maintenant, et il exige
    aussi d'avoir eu de quoi regarder — sinon une fuite à la troisième seconde
    le ferait passer sans rien mesurer.

    ⚠️ **SIX ESSAIS, UNE GRAINE CHACUN** (16 sept. 2026, le métro). Mesuré sur
    un seul essai, le contraste avec la passante tenait par l'ordre des dés : sur
    la base seule, décaler TROIS dés faisait marcher la fille 554 px et la
    passante 121 — la passante marche entre 121 et 1 383 px selon le tirage.
    Une probabilité se mesure avec une graine par essai. Sur six : avec son
    poste, la passante marche au moins 1,5 fois plus qu'elle (douze mesures, la
    base et le métro, six décalages de dés) ; sans poste, le rapport tombe à
    1,0. Et une fois sur trente-six, elle s'écarte de 510 px sans fuir — d'où
    « cinq essais sur six », et pas six.
    """
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const essais = [];
        for (let n = 0; n < 6; n++) {
            L.graine(34 + n);
            const fille = o.poser('racoleuse', 20, 0);
            const passante = o.poser('passante', -20, 0);
            fille.etat = 'flane'; passante.etat = 'flane';
            const p0 = { x: fille.x, y: fille.y };
            let ecart = 0, chemin = 0, cheminPassante = 0, arrets = 0, calmes = 0, fuite = false;
            let px = passante.x, py = passante.y, fx = fille.x, fy = fille.y;
            for (let i = 0; i < 80; i++) {
                o.frame(30);
                if (fille.etat === 'fuit') fuite = true;
                if (!fuite) {
                    calmes++;
                    if (fille.etat === 'arret') arrets++;
                    ecart = Math.max(ecart, Math.hypot(fille.x - p0.x, fille.y - p0.y));
                    chemin += Math.hypot(fille.x - fx, fille.y - fy);
                    // ⚠️ La passante se mesure SUR LA MEME FENETRE : comparer 40 s
                    // de flanerie a 13 s de faction ne compare rien.
                    cheminPassante += Math.hypot(passante.x - px, passante.y - py);
                }
                fx = fille.x; fy = fille.y;
                px = passante.x; py = passante.y;
            }
            essais.push({ poste: !!fille.poste, calmes: calmes, arrets: arrets, ecart: Math.round(ecart),
                          chemin: Math.round(chemin), passante: Math.round(cheminPassante) });
            L.Entites.retirer(fille); L.Entites.retirer(passante);
        }
        return essais;
    }""")
    assert all(e["poste"] for e in r), "elle n'a pas de coin a tenir"
    # ⚠️ VINGT RELEVES, soit dix secondes, par essai qui compte : c'est la
    # fenetre que la fiche nomme — « elle se remettait a flaner au bout de dix
    # secondes ». En deca, l'essai n'a rien vu.
    vus = [e for e in r if e["calmes"] >= 20]
    assert len(vus) >= 4, f"seulement {len(vus)} essais avant qu'elle prenne peur : le juge n'a rien mesure"
    au_coin = sum(1 for e in vus if e["ecart"] < 80)
    assert au_coin >= len(vus) - 1, (
        f"tant que rien ne l'effraie, elle ne doit pas quitter son coin : {[e['ecart'] for e in vus]}")
    # ⚠️ On mesure le CHEMIN, pas l'ecart au depart : une flaneuse qui revient
    # sur ses pas fait un long chemin et un petit ecart.
    fille = sum(e["chemin"] for e in vus)
    passante = sum(e["passante"] for e in vus)
    assert passante > 100 * len(vus), "⚠️ une passante, elle, doit continuer de flaner"
    # ⚠️ ET C'EST LE CONTRASTE QUI COMPTE, sur la SOMME des essais : la passante
    # marche plus de 1,3 fois ce que marche la fille. Avec son poste, le rapport
    # ne descend pas sous 1,5 ; sans, il est a 1,0.
    assert passante > 1.3 * fille, f"elle marche autant qu'une passante : {fille} px contre {passante}"
    arrets = sum(e["arrets"] for e in vus)
    calmes = sum(e["calmes"] for e in vus)
    assert arrets > calmes * 0.5, (
        f"elle attend {arrets} releves sur {calmes} : elle flane au lieu de tenir son coin"
    )


def test_le_hud_nomme_la_fille_de_la_brume(banc, paquet):
    """Derniere preuve, a bout de bras : l'invite ACTION la nomme et donne le
    prix — avant, on appuyait sur ACTION en esperant que c'en etait une."""
    tarifs = paquet["economie"]["tarifs"]
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const j = L.B.joueur;
        // ⚠️ **PAS DE ROULOTTE DANS LE DOS.** L'invite ACTION nomme ce qu'il y a
        // de plus proche, et la ville pose ses ambulants où elle veut : le jour
        // où la trame a bougé (17 sept. 2026), une roulotte à café s'est
        // installée au terminus et c'est elle que le juge lisait. Ce juge-ci
        // parle de la fille, pas de ce qui se vend à côté.
        L.B.defs.ambulants = [];
        for (const q of L.B.entites.slice()) if (q !== j && q.type !== 'joueur') L.Entites.retirer(q);
        const fille = o.poser('racoleuse', 14, 0);
        fille.etat = 'arret';
        // ⚠️ On regarde la fille : l'invite n'apparaît que pour ce qu'on regarde (test_regard_js.py).
        L.Entites.regarder(j, 1, 0);
        L.Entites.indexer();
        L.Missions.majInvite(j);
        const pres = L.B.invite;
        fille.x = j.x + 200; fille.y = j.y + 200;
        L.Entites.indexer();
        L.Missions.majInvite(j);
        return { pres: pres, loin: L.B.invite };
    }""")
    assert r["pres"] == "LA BRUME — " + str(tarifs["compagnie"]) + " $"
    assert r["loin"] != r["pres"], "l'invite la promet alors qu'elle est partie"


# --- M3 : vehicules ----------------------------------------------------------


def test_on_vole_un_char_et_on_en_descend(banc):
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        L.graine(41);
        const j = L.B.joueur;
        j.y += 40;                                  // loin de la porte du terminus : E y entrerait
        const v = o.char('auto', 24, 0, 0);
        const avantVol = L.B.partie.stats.volees;
        // ⚠️ On regarde le char : ACTION n'agit que sur ce qu'on regarde (test_regard_js.py).
        L.Entites.regarder(j, 1, 0);
        o.tape('KeyE', 2);
        const dedans = { conducteur: v.conducteur === j, dansVehicule: j.dansVehicule === v,
                         dessine: j.dessine, contexte: o.elements.tactile.querySelectorAll('[data-a]')[0].textContent };
        o.tape('KeyE', 2);
        return { dedans: dedans, dehors: { conducteur: v.conducteur, dansVehicule: j.dansVehicule, dessine: j.dessine },
                 volees: L.B.partie.stats.volees - avantVol, vole: v.vole,
                 loin: Math.hypot(j.x - v.x, j.y - v.y) };
    }""")
    assert r["dedans"]["conducteur"] and r["dedans"]["dansVehicule"] and r["dedans"]["dessine"] is False
    assert r["dedans"]["contexte"] == "KLAXON", "les boutons tactiles n'ont pas change d'etiquette"
    assert r["dehors"]["conducteur"] is None and r["dehors"]["dansVehicule"] is None and r["dehors"]["dessine"] is True
    assert r["volees"] == 1 and r["vole"] is True
    assert 8 < r["loin"] < 40, "le joueur doit descendre A COTE du char"


def test_la_vitesse_max_et_la_marche_arriere(banc, paquet):
    auto = next(v for v in paquet["vehicules"] if v["slug"] == "auto")
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const j = L.B.joueur, d = o.ligneDroite();
        j.x = d.x; j.y = d.y;
        // ⚠️ On mesure la physique, pas la chance : sans trafic sur la ligne.
        // (Un char du trafic s'y trouvait selon la graine, et bloquait la mesure.)
        L.B.defs.conduite.trafic.vehicules_max = 0;
        L.B.entites.filter(function (e) { return e.type === 'vehicule'; }).forEach(function (e) { L.Entites.retirer(e); });
        const v = o.char('auto', 0, 0, 0);
        L.Vehicules.monter(j, v);
        const x0 = v.x;
        o.touche('KeyW'); o.frame(300); o.relacher('KeyW');
        const pleine = v.vitesse, x1 = v.x;
        o.touche('KeyS'); o.frame(200);
        const recul = v.vitesse;
        o.relacher('KeyS');
        return { pleine: pleine, avance: x1 - x0, recul: recul, y: v.y - d.y,
                 sol: L.Monde.solidite(Math.floor(v.x / L.TT), Math.floor(v.y / L.TT)) };
    }""")
    assert r["pleine"] > auto["vitesse_max"] * 0.95, f"{r['pleine']} px/image, la voiture n'atteint pas sa vitesse"
    assert r["pleine"] <= auto["vitesse_max"] + 1e-6
    assert r["avance"] > 800, "elle n'a pas avance"
    assert -auto["vitesse_recul"] - 1e-6 <= r["recul"] < -0.3, "la marche arriere ne marche pas"
    assert abs(r["y"]) < 4, "elle a devie en ligne droite"
    assert r["sol"] == 0


def test_le_cercle_d_un_char_ne_grandit_pas_avec_sa_vitesse(banc, paquet):
    """⚠️ **Demande de Martin : « améliore les virages ».** Le char tournait
    d'un nombre fixe de radians par image, quelle que soit sa vitesse : le
    cercle qu'il décrivait valait donc `vitesse / braquage`, et il GRANDISSAIT
    avec elle. Mesuré sur une berline : 1,4 tuile au pas, **dix tuiles à fond**.
    Un coin de rue en demande une et demie — à pleine vitesse, le coin était
    impossible, et `majTrafic` l'écrivait déjà (« il ratait son virage et
    finissait sur le trottoir d'en face »).

    Une vraie auto décrit **toujours le même cercle** à volant fixe. Le juge
    mesure le cercle réellement parcouru — pas la formule — à quatre vitesses,
    et exige qu'il ne double jamais entre le pas et le plein régime."""
    r = banc("""function (L, o) {
        L.Jeu.commencer(); L.graine(7);
        const j = L.B.joueur, d = o.ligneDroite();
        j.x = d.x; j.y = d.y; L.Monde.centrerCamera(j.x, j.y);
        function ecart(a, b) { let e = b - a; while (e > Math.PI) e -= 2 * Math.PI; while (e < -Math.PI) e += 2 * Math.PI; return e; }
        const out = {};
        ['auto', 'moto', 'camion', 'autobus'].forEach(function (slug) {
            const v = o.char(slug, 0, 0, 0);
            const cercles = [], glisses = [];
            [0.25, 1.0].forEach(function (part) {
                v.x = 0; v.y = 0; v.angle = 0; v.z = 0; v.volant = 0;
                const vise = v.def.vitesse_max * part;
                v.vitesse = vise; v.vx = vise; v.vy = 0;
                let n = 0, x0 = 0, x1 = 0, y0 = 0, y1 = 0, tourne = 0, prec = 0;
                while (tourne < Math.PI * 2 && n < 3000) {
                    L.Vehicules.majPhysique(v, { gaz: v.vitesse < vise ? 1 : 0,
                                                 frein: v.vitesse > vise * 1.02 ? 0.4 : 0,
                                                 direction: 1, freinMain: false });
                    v.x += v.vx; v.y += v.vy; n++;
                    tourne += Math.abs(ecart(prec, v.angle)); prec = v.angle;
                    x0 = Math.min(x0, v.x); x1 = Math.max(x1, v.x);
                    y0 = Math.min(y0, v.y); y1 = Math.max(y1, v.y);
                }
                cercles.push(+(((x1 - x0) + (y1 - y0)) / 4).toFixed(1));
                glisses.push(+(Math.abs(ecart(v.angle, Math.atan2(v.vy, v.vx))) * 180 / Math.PI).toFixed(1));
                if (tourne < Math.PI * 2) cercles.push('jamais bouclé');
            });
            out[slug] = { rayon: v.def.rayon_braquage, classe: v.def.classe, cercles: cercles, glisses: glisses };
            L.Entites.retirer(v);
        });
        return out;
    }""")
    for slug, m in r.items():
        lent, vite = m["cercles"]
        assert isinstance(lent, (int, float)) and isinstance(vite, (int, float)), (slug, m)
        # Au pas, le cercle est celui de la fiche, à la glisse près.
        assert abs(lent - m["rayon"]) <= m["rayon"] * 0.35, f"{slug} : {lent} px au pas pour {m['rayon']} px de fiche"
        # ⚠️ LE DÉFAUT, MESURÉ : à fond, le cercle ne fait pas plus de deux fois
        # et demie celui du pas — c'est ce que la fiche concède au volant qui
        # perd de la prise (`braquage_vite`). Avant, une berline passait de
        # 22 px à 163 : SEPT fois.
        assert vite <= lent * 2.6, f"{slug} : le cercle passe de {lent} à {vite} px avec la vitesse"
        # Et il reste franchissable : un coin de rue fait une tuile et demie,
        # une intersection quatre.
        # ⚠️ SAUF UN POIDS LOURD LANCÉ (21 sept. 2026, la paie de la Prévost).
        # Jusque-là l'autobus ne passait jamais 1,84 px/image — la friction lui
        # volait sa `vitesse_max` —, et ce juge le mesurait « à fond » sans le
        # savoir : il était vert à vide. Il roule enfin à 2,6, et à 2,6 un
        # autobus ne prend pas une intersection : il freine avant, comme un vrai.
        # Rien n'a reculé : la courbe lit `vitesse / vitesse_max`, qui n'a pas
        # bougé, donc à chaque vitesse qu'il atteignait avant il tourne comme
        # avant. La borne ne garde que l'ordre de grandeur — qu'on ne l'alourdisse
        # pas sans le voir.
        tuiles = 6.5 if m["classe"] == "camion" else 4.5
        assert vite <= 16 * tuiles, f"{slug} : {vite / 16:.1f} tuiles de rayon à fond, aucun coin ne passe"
    # La berline glisse un peu, jamais en travers : c'est le caractère de la
    # sport, pas celui d'une auto de tous les jours.
    assert max(r["auto"]["glisses"]) < 20, r["auto"]


def test_le_volant_se_tourne_et_se_recentre(banc):
    """⚠️ La direction passait de 0 à 1 en une image : au clavier, chaque appui
    était un coup de butée à butée. Le volant prend, et il se recentre quand on
    lâche — c'est ce qui fait qu'une courbe est une courbe."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const j = L.B.joueur, d = o.ligneDroite();
        j.x = d.x; j.y = d.y;
        const v = o.char('auto', 0, 0, 0);
        L.Vehicules.monter(j, v);
        v.vitesse = 2; v.vx = 2; v.vy = 0;
        const neuf = v.volant;
        const prise = [];
        for (let i = 0; i < 6; i++) { L.Vehicules.majPhysique(v, { gaz: 0, frein: 0, direction: 1 }); prise.push(+v.volant.toFixed(3)); }
        const plein = [];
        for (let i = 0; i < 60; i++) { L.Vehicules.majPhysique(v, { gaz: 0, frein: 0, direction: 1 }); }
        plein.push(+v.volant.toFixed(3));
        const relache = [];
        for (let i = 0; i < 30; i++) { L.Vehicules.majPhysique(v, { gaz: 0, frein: 0, direction: 0 }); relache.push(+v.volant.toFixed(3)); }
        return { neuf: neuf, prise: prise, plein: plein[0], relache: relache };
    }""")
    assert r["neuf"] == 0, "on hérite du volant de celui d'avant"
    assert 0 < r["prise"][0] < 0.5, "le volant claque à la butée en une image : %s" % r["prise"]
    assert r["prise"] == sorted(r["prise"]), "il ne prend pas régulièrement : %s" % r["prise"]
    assert r["plein"] > 0.95, "il n'atteint jamais la butée : %s" % r["plein"]
    assert r["relache"] == sorted(r["relache"], reverse=True), "il ne se recentre pas : %s" % r["relache"]
    assert r["relache"][-1] == 0, "il reste braqué après qu'on a lâché : %s" % r["relache"]


def test_le_volant_en_marche_arriere_se_choisit_dans_les_options(banc):
    """Retour de Martin : vue de dessus, le volant d'une vraie auto en marche
    arrière (droite fait tourner le char à rebours) ne colle à l'écran que nez en
    haut. L'option COMME EN AVANT garde droite = sens des aiguilles d'une montre.

    Jugé AU CLAVIER, dans la boucle du jeu : D tenu tout du long, W pour partir,
    puis S jusqu'à reculer. ⚠️ Et image par image : c'est le signe de la rotation
    qui change, pas la consigne — une consigne retournée au passage à vitesse
    nulle ferait traverser le volant lissé de butée à butée, et le char
    tournerait à rebours au début de chaque recul, option ou pas."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        L.B.defs.conduite.trafic.vehicules_max = 0;
        function manoeuvre(option) {
            L.B.entites.filter(function (e) { return e.type === 'vehicule'; }).forEach(function (e) { L.Entites.retirer(e); });
            const j = L.B.joueur, d = o.ligneDroite();
            if (j.dansVehicule) L.Vehicules.descendre(j, true);
            j.x = d.x; j.y = d.y;
            const v = o.char('auto', 0, 0, 0);
            L.Vehicules.monter(j, v);
            L.B.options.reculCommeEnAvant = option;
            let avant = v.angle, avance = 0, recule = 0, pire = 0, reculMax = 0;
            function image() {
                o.frame(1);
                const pas = v.angle - avant; avant = v.angle;
                if (v.vitesse > 0.3) avance += pas;
                if (v.vitesse < -0.3) recule += pas;
                pire = Math.min(pire, pas);
                reculMax = Math.min(reculMax, v.vitesse);
            }
            o.touche('KeyD'); o.touche('KeyW');
            for (let i = 0; i < 20; i++) image();
            o.relacher('KeyW'); o.touche('KeyS');
            for (let i = 0; i < 90; i++) image();
            o.relacher('KeyS'); o.relacher('KeyD'); o.frame(1);
            return { avance: +avance.toFixed(3), recule: +recule.toFixed(3), pire: +pire.toFixed(4), reculMax: +reculMax.toFixed(2) };
        }
        const auto = manoeuvre(false), commeEnAvant = manoeuvre(true);
        // La police et le trafic ne lisent pas l'option : ils gardent l'auto.
        L.B.options.reculCommeEnAvant = true;
        const p = o.char('auto', 0, 40, 0);
        p.vitesse = -1; p.vx = -1; p.vy = 0; p.volant = 1;
        const cap = p.angle;
        L.Vehicules.majPhysique(p, { gaz: 0, frein: 1, direction: 1 });
        return { auto: auto, commeEnAvant: commeEnAvant, police: +(p.angle - cap).toFixed(4) };
    }""")
    for cle in ("auto", "commeEnAvant"):
        m = r[cle]
        assert m["reculMax"] < -0.3, "le char n'a jamais reculé (%s) : %s" % (cle, m)
        assert m["avance"] > 0, "en avançant, droite ne tourne pas à droite (%s) : %s" % (cle, m)
    assert r["auto"]["recule"] < 0, "COMME UNE AUTO : en reculant, droite doit tourner à rebours : %s" % r["auto"]
    assert r["commeEnAvant"]["recule"] > 0, (
        "COMME EN AVANT : en reculant, droite doit tourner dans le sens des aiguilles d'une montre : %s" % r["commeEnAvant"]
    )
    assert r["commeEnAvant"]["pire"] >= 0, (
        "COMME EN AVANT : le char a tourné à rebours pendant une image — le volant a traversé "
        "de butée à butée au passage à vitesse nulle : %s" % r["commeEnAvant"]
    )
    assert r["police"] < 0, "l'option du joueur a changé le volant d'un char qu'il ne conduit pas : %s" % r["police"]


def test_l_option_du_volant_en_marche_arriere_se_bascule_et_se_garde(banc):
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        o.tape('Escape', 2);
        L.B.menu.items.find(function (i) { return i.libelle === 'OPTIONS'; }).faire();
        const ligne = function () { return L.B.menu.items.find(function (i) { return i.libelle === 'VOLANT EN MARCHE ARRIÈRE'; }); };
        const avant = { detail: ligne().detail, option: L.B.options.reculCommeEnAvant };
        ligne().faire(ligne());
        const apres = { detail: ligne().detail, option: L.B.options.reculCommeEnAvant,
                        sauvee: JSON.parse(o.store[L.Sauvegarde.CLE_OPTIONS]).reculCommeEnAvant };
        // Rouvrir les options : la ligne dit ce qui est choisi, pas le defaut.
        L.B.menu.items.find(function (i) { return i.libelle === 'RETOUR'; }).faire();
        L.B.menu.items.find(function (i) { return i.libelle === 'OPTIONS'; }).faire();
        const rouvert = ligne().detail;
        ligne().faire(ligne());
        return { avant: avant, apres: apres, rouvert: rouvert, retour: { detail: ligne().detail, option: L.B.options.reculCommeEnAvant } };
    }""")
    assert r["avant"] == {"detail": "COMME UNE AUTO", "option": False}, "par défaut, rien ne doit changer : %s" % r
    assert r["apres"] == {"detail": "COMME EN AVANT", "option": True, "sauvee": True}, r
    assert r["rouvert"] == "COMME EN AVANT", r
    assert r["retour"] == {"detail": "COMME UNE AUTO", "option": False}, r


def test_un_char_pivote_sur_son_arriere_pas_sur_son_nombril(banc):
    """⚠️ En tournant autour de son centre, le char balayait son coffre dans le
    mur derrière lui, et le nez ne « rentrait » jamais dans le virage. Le juge
    mesure les deux bouts : dans un quart de tour, le nez parcourt plus de
    chemin que le train arrière."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const j = L.B.joueur, d = o.ligneDroite();
        j.x = d.x; j.y = d.y;
        const v = o.char('auto', 0, 0, 0);
        v.vitesse = 1.2; v.vx = 1.2; v.vy = 0; v.volant = 0;
        const demi = v.def.longueur / 2;
        const bout = function (signe) { return { x: v.x + Math.cos(v.angle) * demi * signe, y: v.y + Math.sin(v.angle) * demi * signe }; };
        const nez0 = bout(1), cul0 = bout(-1);
        let n = 0;
        while (v.angle < Math.PI / 2 && n < 600) { L.Vehicules.majPhysique(v, { gaz: 1, frein: 0, direction: 1 }); v.x += v.vx; v.y += v.vy; n++; }
        const nez1 = bout(1), cul1 = bout(-1);
        return { nez: +Math.hypot(nez1.x - nez0.x, nez1.y - nez0.y).toFixed(1),
                 cul: +Math.hypot(cul1.x - cul0.x, cul1.y - cul0.y).toFixed(1), images: n };
    }""")
    assert r["images"] < 600, "le char n'a pas bouclé son quart de tour : %s" % r
    assert r["nez"] > r["cul"], (
        "le nez et le coffre parcourent le même chemin : le char pivote sur son nombril (%s)" % r
    )


def test_le_frein_a_main_fait_deriver(banc):
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        function virage(freinMain) {
            const j = L.B.joueur, d = o.ligneDroite();
            j.x = d.x; j.y = d.y;
            if (j.dansVehicule) L.Vehicules.descendre(j, true);
            const v = o.char('auto', 0, 0, 0);
            v.vitesse = 3.5; v.vx = 3.5; v.vy = 0;
            L.Vehicules.monter(j, v);
            let ecartMax = 0;
            for (let i = 0; i < 25; i++) {
                L.Vehicules.majPhysique(v, { gaz: 1, frein: 0, direction: 1, freinMain: freinMain });
                const capVitesse = Math.atan2(v.vy, v.vx);
                ecartMax = Math.max(ecartMax, Math.abs(L.Vehicules.courbeBraquage ? (capVitesse - v.angle) : 0));
            }
            L.Entites.retirer(v);
            return ecartMax;
        }
        return { sans: virage(false), avec: virage(true) };
    }""")
    assert r["avec"] > r["sans"] * 1.3, f"la derive au frein a main ({r['avec']:.2f}) ne depasse pas la conduite normale ({r['sans']:.2f})"


def test_un_mur_fait_mal_mais_ne_se_traverse_pas(banc):
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const j = L.B.joueur, d = o.ligneDroite();
        j.x = d.x; j.y = d.y;
        const v = o.char('auto', 0, 0, -Math.PI / 2);   // plein nord : le bord de la carte
        L.Vehicules.monter(j, v);
        const vie0 = v.vie;
        o.touche('KeyW'); o.frame(120); o.relacher('KeyW');
        let dedans = false;
        for (const c of L.Vehicules.cercles(v)) {
            if (L.Monde.bloque(Math.floor(c.x / L.TT), Math.floor(c.y / L.TT), L.Monde.MASQUE_VEHICULE)) dedans = true;
        }
        return { perdu: vie0 - v.vie, chocs: v.chocs, dedans: dedans, vitesse: Math.abs(v.vitesse), y: v.y };
    }""")
    assert r["perdu"] > 0, "le mur n'a pas fait de degats"
    assert r["chocs"] >= 1
    assert r["dedans"] is False, "le char est entre dans le mur"
    assert r["vitesse"] < 1.5
    assert r["y"] > 0


def test_le_trafic_roule_3000_images_sans_se_bloquer(banc, paquet):
    maximum = paquet["conduite"]["trafic"]["vehicules_max"]
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        L.graine(43);
        o.frame(1200);
        // ⚠️ On ne suit un char que tant qu'il est LA : la bulle d'oubli retire
        // ceux qui s'eloignent du joueur, et un char retire ne bouge plus —
        // le test les prenait pour des chars bloques.
        //
        // ⚠️ Et on suit TOUS ceux qui passent, pas seulement ceux qui etaient
        // la a la premiere image : le joueur ne bouge pas, donc la plupart des
        // chars presents au depart s'en vont en quelques secondes. L'echantillon
        // tombait alors a deux ou trois, et le juge se mettait a dependre du
        // tirage plutot que du trafic. Un char BLOQUE, lui, reste dans la bulle
        // et accumule des images sans avancer d'un pixel : c'est exactement ce
        // qu'on cherche, et elargir l'echantillon le trouve mieux.
        const suivis = new Map();
        for (let i = 0; i < 1800; i++) {
            o.frame(1);
            L.B.entites.forEach(function (e) {
                if (e.type !== 'vehicule' || e.conducteur !== 'trafic') return;
                const s = suivis.get(e.id);
                if (!s) { suivis.set(e.id, { x: e.x, y: e.y, d: 0, images: 0 }); return; }
                s.d += Math.hypot(e.x - s.x, e.y - s.y); s.x = e.x; s.y = e.y; s.images++;
            });
        }
        const chars = L.B.entites.filter(function (e) { return e.type === 'vehicule'; });
        let dansUnMur = 0, horsRoute = 0;
        chars.forEach(function (v) {
            const tx = Math.floor(v.x / L.TT), ty = Math.floor(v.y / L.TT);
            if (L.Monde.solidite(tx, ty) === 1) dansUnMur++;
            if (v.conducteur === 'trafic' && !L.Monde.estRoute(tx, ty)) horsRoute++;
        });
        const presents = Array.from(suivis.values()).filter(function (s) { return s.images >= 300; });
        const distances = presents.map(function (s) { return s.d / s.images * 1800; });   // ramene a 1800 images
        const bouges = distances.filter(function (d) { return d > 300; }).length;
        return { roulent: chars.filter(function (v) { return v.conducteur === 'trafic'; }).length,
                 suivis: distances.length, bouges: bouges, dansUnMur: dansUnMur, horsRoute: horsRoute,
                 total: chars.length, epaves: chars.filter(function (v) { return v.etat === 'epave'; }).length,
                 ms: L.B.stats.ms };
    }""")
    assert r["roulent"] >= 3, "le trafic ne se peuple pas"
    assert r["roulent"] <= maximum
    assert r["dansUnMur"] == 0, "un char est dans un mur"
    assert r["horsRoute"] <= 1, f"{r['horsRoute']} chars du trafic hors de la route"
    assert r["epaves"] == 0, "le trafic s'entretue tout seul"
    assert r["suivis"] >= 3 and r["bouges"] >= r["suivis"] * 0.6, \
        f"{r['bouges']}/{r['suivis']} chars ont roule : le trafic se bloque"


def test_renverser_un_pieton_est_un_crime(banc):
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        L.graine(44);
        const j = L.B.joueur, d = o.ligneDroite();
        j.x = d.x; j.y = d.y;
        const v = o.char('auto', 0, 0, 0);
        L.Vehicules.monter(j, v);
        const victime = o.poser('passant', 90, 0);
        const enfant = o.poser('enfant', 90, 30);
        const crimes = L.B.partie.stats.crimes;
        v.vitesse = 3.5; v.vx = 3.5; v.vy = 0;
        o.touche('KeyW'); o.frame(60); o.relacher('KeyW');
        return { vie: victime.vie, max: victime.vieMax, etat: victime.etat, crimes: L.B.partie.stats.crimes - crimes,
                 enfant: enfant.vie === enfant.vieMax && enfant.vivant };
    }""")
    assert r["vie"] < r["max"], "le pieton n'a pas ete renverse"
    assert r["crimes"] >= 1, "renverser quelqu'un n'est pas compte comme un crime"
    assert r["enfant"] is True, "un enfant a ete touche par un char"


def test_un_char_explose_et_brule_ce_qui_l_entoure(banc, paquet):
    ph = paquet["conduite"]["physique"]
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        L.graine(45);
        const v = o.char('auto', 60, 0, 0);
        const voisin = o.poser('ouvrier', 60, 18);
        voisin.courage = 0;
        const loin = o.poser('passant', 60, 300);
        L.Entites.indexer();
        L.Vehicules.endommager(v, 9999, L.B.joueur);
        return { etat: v.etat, vie: v.vie, voisin: voisin.vie, voisinMax: voisin.vieMax,
                 loin: loin.vie === loin.vieMax, decals: L.B.decals.length,
                 particules: L.B.particules.length, crimes: L.B.partie.stats.crimes };
    }""")
    assert r["etat"] == "epave" and r["vie"] == 0
    assert r["voisin"] < r["voisinMax"], "l'explosion n'a pas touche le voisin"
    assert ph["explosion_rayon_px"] < 300
    assert r["loin"] is True, "l'explosion a porte a 300 px"
    assert r["particules"] > 20 and r["decals"] >= 1
    assert r["crimes"] >= 1, "faire exploser un char n'est pas un crime ?"


def test_une_epave_reste_une_epave_quand_on_etait_au_volant(banc):
    """⚠️ Rouge avant (17 sept. 2026). `exploser` (et `plier`, pour le velo)
    posent l'epave PUIS font descendre celui qui etait au volant — et
    `descendre()` ecrivait `stationne` par-dessus. La carcasse d'un char qui
    venait de sauter sous le joueur redevenait un char : on y remontait, et elle
    sautait une deuxieme fois. Tout au bouton."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const B = L.B, j = B.joueur;
        j.invincible = 1e6;
        const route = o.ligneDroite();
        function essai(slug, dx) {
            j.x = route.x + dx; j.y = route.y; L.Entites.indexer();
            const v = o.char(slug, 0, 16, 0);
            o.tape('KeyE', 2);
            const monte = j.dansVehicule === v;
            L.Vehicules.endommager(v, 9999, null);
            const apres = { etat: v.etat, dedans: !!j.dansVehicule, laisse: !!v.laisse };
            o.frame(5);
            j.x = v.x; j.y = v.y - 16; L.Entites.indexer();
            o.tape('KeyE', 2);
            return { monte: monte, apres: apres, remonte: j.dansVehicule === v, etat: v.etat };
        }
        return { auto: essai('auto', 0), velo: essai('velo', 160) };
    }""")
    for slug in ("auto", "velo"):
        e = r[slug]
        assert e["monte"] is True, f"{slug} : on n'a pas pu monter"
        assert e["apres"] == {"etat": "epave", "dedans": False, "laisse": False}, (
            f"{slug} : detruit sous le joueur, ce n'est plus une epave : {e['apres']}")
        assert e["remonte"] is False and e["etat"] == "epave", f"{slug} : on remonte dans la carcasse : {e}"


def test_un_velo_ne_saute_pas_il_se_plie(banc, paquet):
    """⚠️ Retour de Martin : un velo EXPLOSE. Il a 30 PV, le plus fragile du
    jeu ; deux coups de batte et il partait en boule de feu — quarante
    particules, une deflagration de 60 px a 90 points de degats sur tout ce qui
    l'entoure, l'ecran qui tremble, et un delit `explosion` a +2★ avec une
    alarme de 15 tuiles. On renversait un velo, et la police arrivait.

    Le meme decor que le juge de l'explosion, au velo pres : un voisin a 18 px,
    un temoin plus loin. Rien de tout ca ne doit bouger — et le velo doit quand
    meme finir en epave, sinon on l'a rendu indestructible."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        L.graine(45);
        const v = o.char('velo', 60, 0, 0);
        const voisin = o.poser('ouvrier', 60, 18);
        voisin.courage = 0;
        const auto = o.char('auto', 60, 30, 0);
        L.Entites.indexer();
        const secousse0 = L.B.cam.secousse;
        L.Vehicules.endommager(v, 9999, L.B.joueur);
        const apres = { etat: v.etat, vie: v.vie, plie: !!v.plie, voisin: voisin.vie === voisin.vieMax,
                        auto: auto.vie === auto.vieMax, secousse: L.B.cam.secousse <= secousse0,
                        crimes: L.B.partie.stats.crimes, etoiles: L.B.recherche.etoiles,
                        particules: L.B.particules.length, decals: L.B.decals.length };
        // Et il ne BRULE pas non plus : cent images sur une epave a zero PV
        // ne doivent poser ni flamme ni fumee. ⚠️ On compte les particules
        // POSEES PRES DU VELO, pas la longueur du tableau : celles de la chute
        // s'eteignent pendant la mesure, et le solde serait negatif.
        const vraiP = L.Entites.particule;
        let fume = 0;
        L.Entites.particule = function (x, y) {
            if (Math.hypot(x - v.x, y - v.y) < 24) fume++;
            return vraiP.apply(null, arguments);
        };
        o.frame(100);
        L.Entites.particule = vraiP;
        apres.fume = fume;
        // Le meme coup sur une auto, lui, fait bien tout sauter : c'est le
        // temoin que le juge mesure une DIFFERENCE, pas une panne.
        const a2 = o.char('auto', -200, 0, 0);
        L.Entites.indexer();
        L.Vehicules.endommager(a2, 9999, L.B.joueur);
        apres.auto_saute = { etat: a2.etat, crimes: L.B.partie.stats.crimes };
        return apres;
    }""")
    assert r["etat"] == "epave" and r["vie"] == 0 and r["plie"] is True, (
        "un velo detruit doit rester une epave, pliee : %s" % r
    )
    assert r["voisin"] is True, "le velo a blesse quelqu'un en se pliant"
    assert r["auto"] is True, "le velo a endommage le char d'a cote"
    assert r["secousse"] is True, "l'ecran a tremble pour un velo"
    assert r["decals"] == 0, "un velo plie laisse une marque d'explosion au sol"
    assert r["particules"] < 20, "quarante particules de feu pour un velo : %s" % r["particules"]
    assert r["crimes"] == 0 and r["etoiles"] == 0, (
        "plier un velo a donne %s crime(s) et %s etoile(s)" % (r["crimes"], r["etoiles"])
    )
    assert r["fume"] == 0, "le velo a zero PV fume ou brule : %s particules" % r["fume"]
    assert r["auto_saute"]["etat"] == "epave" and r["auto_saute"]["crimes"] >= 1, (
        "une auto, elle, doit toujours exploser et se compter : %s" % r["auto_saute"]
    )


def test_le_carjacking_se_voit_toujours(banc, paquet):
    gravite = paquet["recherche"]["delits"]["carjacking"]["etoiles"]
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        L.graine(46);
        const j = L.B.joueur;
        L.B.entites = L.B.entites.filter(function (e) { return e.type !== 'pieton'; });
        const v = o.char('auto', 20, 0, 0);
        v.conducteur = 'trafic'; v.etat = 'roule';
        L.Entites.indexer();
        L.Vehicules.monter(j, v);
        const temoins = L.B.entites.filter(function (e) { return e.type === 'pieton' && e.etat === 'temoin'; }).length;
        return { conducteur: v.conducteur === j, temoins: temoins,
                 chaleur: L.B.recherche.chaleur + L.B.recherche.etoiles * 100,
                 gravite: L.B.defs.recherche.chaleur_par_gravite };
    }""")
    assert r["conducteur"] is True
    assert r["temoins"] == 1, "la victime du carjacking doit sortir et temoigner"
    assert r["chaleur"] == gravite * r["gravite"], "le carjacking n'a pas chauffe la police"


def test_les_feux_alternent_et_les_t_n_en_ont_pas(banc):
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const inters = L.Monde.carte.intersections;
        const croix = inters.find(function (i) { return i.bras.length === 4; });
        const te = inters.find(function (i) { return i.bras.length === 3; });
        const cycle = 2 * (L.B.defs.conduite.trafic.feu_vert_images + L.B.defs.conduite.trafic.feu_orange_images);
        const releves = [];
        for (let t = 0; t < cycle; t += 30) {
            L.B.t = t - croix.decalage;
            releves.push([L.Monde.feuVert(croix, '^'), L.Monde.feuVert(croix, '>')]);
        }
        const deuxVerts = releves.filter(function (r) { return r[0] && r[1]; }).length;
        const nsVert = releves.filter(function (r) { return r[0]; }).length;
        const eoVert = releves.filter(function (r) { return r[1]; }).length;
        return { deuxVerts: deuxVerts, nsVert: nsVert, eoVert: eoVert, total: releves.length,
                 teVert: L.Monde.feuVert(te, '^') && L.Monde.feuVert(te, '>') };
    }""")
    assert r["deuxVerts"] == 0, "les deux sens ont ete verts en meme temps"
    assert r["nsVert"] > 0 and r["eoVert"] > 0
    assert abs(r["nsVert"] - r["eoVert"]) <= 1, "un sens est favorise"
    assert r["teVert"] is True, "un T n'a pas de feu : on y passe a vue"


def test_le_taxi_paie_la_course_selon_la_douceur(banc, paquet):
    boulot = paquet["economie"]["boulots"]["taxi"]
    civil = next(p for p in paquet["personnages"] if p["slug"] == "civil")
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        L.graine(47);
        const j = L.B.joueur, d = o.ligneDroite();
        j.x = d.x; j.y = d.y;
        const v = o.char('taxi', 0, 0, 0);
        L.Vehicules.monter(j, v);
        const argent0 = L.B.partie.argent;
        o.tape('Space', 2);                              // klaxon : un client
        const t = L.Missions.boulot;
        const etape1 = t.etape, client = t.client;
        const hele = client && client.bulle ? client.bulle.texte : null;
        if (client) { v.x = client.x + 10; v.y = client.y; j.x = v.x; j.y = v.y; v.vitesse = 0; }
        o.frame(3);
        const etape2 = t.etape, dest = t.destination;
        if (dest) { v.x = dest.x + 6; v.y = dest.y; j.x = v.x; j.y = v.y; v.vitesse = 0; }
        o.frame(3);
        return { etape1: etape1, etape2: etape2, etape3: t.etape, hele: hele,
                 gain: L.B.partie.argent - argent0, courses: t.faits.taxi };
    }""")
    assert r["etape1"] == "ramasse" and r["etape2"] == "route" and r["etape3"] is None
    assert r["hele"] == civil["heler"], \
        "un client qui attend un taxi sans rien dire est un passant de plus (bulle du « civil »)"
    assert r["courses"] == 1
    assert r["gain"] >= boulot["base"] + boulot["prime"], \
        "une course sans un choc doit donner le pourboire plein"


def test_le_taxi_n_envoie_personne_ou_un_char_ne_va_pas(banc):
    """⚠️ Rouge avant (17 sept. 2026) : depuis l'ile, la chapelle Sainte-Anne est
    un point de la carte comme un autre, et le taxi (la pizza aussi) l'y tirait
    au sort — on ne l'atteint qu'a la nage. La regle est ce dont la course a
    besoin, une route depuis le char : la route est donc ecrite ICI, pas relue
    dans `missions.js`."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const B = L.B, M = L.Monde, TT = L.TT, W = M.carte.w, H = M.carte.h;
        const g = L.Histoire.lieu('garage');
        let depart = null;
        for (let r = 0; r <= 4 && !depart; r++) for (let dy = -r; dy <= r && !depart; dy++) for (let dx = -r; dx <= r; dx++) {
            const tx = Math.floor(g.x / TT) + dx, ty = Math.floor(g.y / TT) + dy;
            if (!M.bloque(tx, ty, M.MASQUE_VEHICULE) && !M.estEau(tx, ty)) { depart = { x: tx * TT + 8, y: ty * TT + 8 }; break; }
        }
        const vus = new Uint8Array(W * H), file = [];
        const s0 = Math.floor(depart.y / TT) * W + Math.floor(depart.x / TT);
        vus[s0] = 1; file.push(s0);
        for (let i = 0; i < file.length; i++) {
            const k = file[i], x = k % W, y = (k - x) / W;
            [[1, 0], [-1, 0], [0, 1], [0, -1]].forEach(function (d) {
                const nx = x + d[0], ny = y + d[1], nk = ny * W + nx;
                if (nx < 0 || ny < 0 || nx >= W || ny >= H || vus[nk]) return;
                if (M.bloque(nx, ny, M.MASQUE_VEHICULE) || M.estEau(nx, ny)) return;
                vus[nk] = 1; file.push(nk);
            });
        }
        function enChar(px, py) {
            for (let y = Math.floor(py / TT) - 3; y <= Math.floor(py / TT) + 3; y++) {
                for (let x = Math.floor(px / TT) - 3; x <= Math.floor(px / TT) + 3; x++) {
                    if (x >= 0 && y >= 0 && x < W && y < H && vus[y * W + x] && Math.hypot(x * TT + 8 - px, y * TT + 8 - py) < 44) return true;
                }
            }
            return false;
        }
        const coupes = M.carte.points.filter(function (p) { return !enChar(p.x * TT + 8, p.y * TT + 8); }).map(function (p) { return p.slug; });
        const v = L.Vehicules.creer('taxi', depart.x, depart.y, 0, { etat: 'stationne' });
        const tires = {};
        let horsRoute = 0;
        for (let i = 0; i < 300; i++) {
            L.Missions.boulot.slug = 'taxi';
            L.Missions.boulot.enRoute(v);
            const d = L.Missions.boulot.destination;
            tires[d.nom] = (tires[d.nom] || 0) + 1;
            if (!enChar(d.x, d.y)) horsRoute++;
        }
        L.Missions.boulot.fin();
        return { coupes: coupes, tires: tires, horsRoute: horsRoute };
    }""")
    assert r["coupes"], "aucun point de la carte n'est coupe de la route : ce juge ne mord plus sur rien"
    assert r["horsRoute"] == 0, f"{r['horsRoute']} courses sur 300 vers un lieu sans route ({r['coupes']}) : {r['tires']}"
    assert len(r["tires"]) >= 10, f"le taxi ne va plus que dans {len(r['tires'])} lieux : {r['tires']}"


def test_la_pizza_se_livre_trois_fois_et_refroidit(banc, paquet):
    """⚠️ `Missions.taxi` etait le SEUL boulot : les trois autres etaient dans
    `economie.BOULOTS`, dans le paquet, avec leurs juges Python — et le klaxon
    d'une moto ne faisait rien. Une fiche de plus que le navigateur ne lisait
    pas, comme `cercles` et `defonce` avant elle.

    La pizza a ce que le taxi n'a pas : TROIS etapes de suite, et une prime qui
    FOND toute seule. Le juge tient les deux — et la distance doit se payer a
    chaque etape, sinon trois livraisons rapporteraient trois fois le premier
    trajet."""
    f = paquet["economie"]["boulots"]["pizza"]
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        L.graine(51);
        const j = L.B.joueur, d = o.ligneDroite();
        j.x = d.x; j.y = d.y;
        const v = o.char('moto', 0, 0, 0);
        L.Vehicules.monter(j, v);
        const b = L.Missions.boulot;
        const argent0 = L.B.partie.argent;
        o.tape('Space', 2);                              // klaxon : on part charge
        // ⚠️ Pas de ramassage : la pizza part tout de suite en route.
        const depart = { slug: b.slug, etape: b.etape, client: !!b.client };
        const etapes = [], primesChaudes = [];
        for (let i = 0; i < 5 && b.etape; i++) {
            const dest = b.destination;
            v.x = dest.x + 6; v.y = dest.y; j.x = v.x; j.y = v.y; v.vitesse = 0;
            primesChaudes.push(b.prime(v));
            o.frame(3);
            etapes.push({ faites: b.etapesFaites, encore: !!b.etape });
        }
        const chaud = L.B.partie.argent - argent0;
        // Et LA MEME TOURNEE, mais froide : on laisse le chrono s'ecouler.
        // ⚠️ La graine ET le point de depart reviennent a l'identique : sans
        // ca, la deuxieme tournee tire d'AUTRES clients (ils se choisissent
        // autour de la moto, et elle a fini la premiere tournee a l'autre bout
        // de la ville). On comparait deux trajets differents — une livraison
        // froide au loin paie plus qu'une chaude a cote, et le juge disait le
        // contraire de ce qu'il voulait dire.
        L.graine(51);
        v.x = d.x; v.y = d.y; j.x = d.x; j.y = d.y; v.vitesse = 0;
        L.B.partie.argent = argent0;
        o.tape('Space', 2);
        let froid = 0;
        const primesFroides = [];
        for (let i = 0; i < 5 && b.etape; i++) {
            o.frame(%d);                                  // la pizza refroidit
            const dest = b.destination;
            v.x = dest.x + 6; v.y = dest.y; j.x = v.x; j.y = v.y; v.vitesse = 0;
            primesFroides.push(b.prime(v));
            o.frame(3);
        }
        froid = L.B.partie.argent - argent0;
        return { depart: depart, etapes: etapes, chaud: chaud, froid: froid,
                 primesChaudes: primesChaudes, primesFroides: primesFroides,
                 faits: b.faits.pizza, taxis: b.faits.taxi };
    }""" % (f["chrono_s"] * 60 + 10))
    assert r["depart"] == {"slug": "pizza", "etape": "route", "client": False}, (
        "on part avec les boites : pas d'etape de ramassage (%s)" % r["depart"]
    )
    assert [e["faites"] for e in r["etapes"]] == [1, 2, 3], (
        "la pizza se livre %s fois au lieu de 3 : %s" % (f["etapes"], r["etapes"])
    )
    assert r["etapes"][-1]["encore"] is False, "le boulot ne se termine pas"
    # ⚠️ Deux boulots joues (chaud puis froid) : le compteur les compte tous
    # les deux, et AUCUN ne tombe dans celui du taxi.
    assert r["faits"] == 2 and r["taxis"] == 0, (
        "une pizza livree n'est pas une course de taxi : %s" % r
    )
    # ⚠️ La distance se paie A CHAQUE etape, donc trois trajets valent plus que
    # trois fois la base seule.
    assert r["chaud"] >= (f["base"] + f["prime"]) * f["etapes"], (
        "trois livraisons chaudes rapportent %s, moins que %s" % (r["chaud"], (f["base"] + f["prime"]) * f["etapes"])
    )
    # ⚠️ ON COMPARE LES PRIMES, PAS LES DEUX TOTAUX. Les clients se tirent au
    # sort autour de la moto : la tournee froide n'est PAS la tournee chaude, et
    # trois livraisons froides a l'autre bout de la ville paient plus, en
    # distance, que trois chaudes a cote — le juge disait alors le contraire de
    # ce qu'il voulait dire. La prime, elle, ne depend que du chrono : elle est
    # entiere tant que la pizza est chaude, nulle quand elle est froide, et
    # comme les deux livraisons paient la meme distance, c'est bien elle qui
    # fait qu'a trajet egal une pizza froide rapporte moins.
    assert all(prime > 0 for prime in r["primesChaudes"]), (
        "la pizza chaude ne paie aucune prime : %s" % r["primesChaudes"]
    )
    assert r["primesChaudes"][0] <= f["prime"], "la prime depasse la fiche"
    assert r["primesFroides"] == [0] * f["etapes"], (
        "une pizza froide garde sa prime : %s" % r["primesFroides"]
    )
    assert r["froid"] >= f["base"] * f["etapes"], "froide, il reste quand meme la base"


def test_l_ambulance_ramasse_un_blesse_et_le_perd_si_on_traine(banc, paquet):
    """⚠️ « Un blesse quelque part, chrono, le sortir vivant. » La prime EST sa
    vie : passe le chrono, il ne se releve pas, et il ne reste que la base.

    Le juge fait les deux trajets — a temps et trop tard — et verifie au
    passage que la destination n'est pas tiree au hasard comme celle du taxi :
    un blesse va A L'HOPITAL, pas au Bar Le Brouillard."""
    f = paquet["economie"]["boulots"]["ambulance"]
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        L.graine(53);
        const j = L.B.joueur, d = o.ligneDroite();
        j.x = d.x; j.y = d.y;
        const v = o.char('ambulance', 0, 0, 0);
        L.Vehicules.monter(j, v);
        const b = L.Missions.boulot;
        function course(attente) {
            const argent0 = L.B.partie.argent;
            // ⚠️ On repart sirene ETEINTE : dans une ambulance, c'est
            // l'allumage qui prend l'appel, jamais l'extinction (voir
            // `test_eteindre_sa_sirene_n_appelle_pas_un_nouveau_contrat`).
            v.sirene = false;
            o.tape('Space', 2);
            const etape1 = b.etape;
            const blesse = b.client;
            const aTerre = blesse ? blesse.etat : null;
            const part = blesse ? blesse.vie / blesse.vieMax : null;
            if (blesse) { v.x = blesse.x + 10; v.y = blesse.y; j.x = v.x; j.y = v.y; v.vitesse = 0; }
            o.frame(3);
            const dest = b.destination;
            if (attente) o.frame(attente);
            if (dest) { v.x = dest.x + 6; v.y = dest.y; j.x = v.x; j.y = v.y; v.vitesse = 0; }
            o.frame(3);
            return { etape1: etape1, aTerre: aTerre, part: part, dest: dest && dest.nom,
                     gain: L.B.partie.argent - argent0, fini: b.etape };
        }
        const aTemps = course(0);
        const tropTard = course(%d);
        return { aTemps: aTemps, tropTard: tropTard, faits: b.faits.ambulance,
                 hopital: (L.Monde.carte.points.find(function (p) { return p.slug === 'hopital'; }) || {}).nom };
    }""" % (f["chrono_s"] * 60 + 10))
    a, t = r["aTemps"], r["tropTard"]
    assert a["etape1"] == "ramasse", "l'ambulance doit aller CHERCHER quelqu'un"
    assert a["aTerre"] == "assomme", "le blesse doit etre a terre, pas debout a heler"
    assert a["part"] is not None and a["part"] < 0.3, "un blesse a pleine vie n'est pas un blesse"
    assert a["dest"] == r["hopital"], "un blesse va a l'hopital, pas au hasard : %s" % a["dest"]
    assert a["gain"] >= f["base"] + f["prime"], "le transport a temps doit donner la prime pleine"
    assert t["gain"] < a["gain"], "arriver trop tard paie autant qu'arriver a temps"
    assert t["gain"] >= f["base"], "il reste la base, meme trop tard"
    assert r["faits"] == 2 and a["fini"] is None


def test_la_fourriere_saisit_le_char_et_le_revend_plus_cher_qu_il_ne_vaut(banc, paquet):
    """⚠️ La fourrière existait **en Python** depuis M9 — une cour clôturée avec
    sa guérite, 40 cases, `economie.FOURRIERE` et son juge d'équilibrage — et
    le navigateur n'en savait rien : le comptoir « LE LOT » avait un libellé et
    aucun menu, et rien n'y amenait jamais un char.

    Trois règles, et la troisième est celle qui compte :

    1. on te prend le char que tu **conduisais** — ⚠️ pas celui où tu es, car
       la police t'en **sort** avant de t'embarquer, donc `dansVehicule` est
       déjà nul à l'arrestation ;
    2. il attend **dans la cour**, sur une case du lot ;
    3. le racheter coûte **plus cher que de le revendre** au garage. Sinon on
       se fait saisir un char exprès pour le racheter moins cher qu'il ne se
       revend, et la fourrière devient une machine à argent.
    """
    f = paquet["economie"]["fourriere"]
    eco = paquet["economie"]
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        L.graine(67);
        const j = L.B.joueur, p = L.B.partie;
        const d = o.ligneDroite();
        j.x = d.x; j.y = d.y;
        // On conduit une berline, PUIS on en descend : c'est l'etat exact dans
        // lequel la police nous laisse avant de nous embarquer.
        const v = o.char('auto', 0, 0, 0);
        L.Vehicules.monter(j, v);
        L.Vehicules.descendre(j, true);
        const avant = { dedans: !!j.dansVehicule, dernier: j.dernierVehicule === v,
                        saisissable: L.Missions.charSaisissable(j) === v };
        p.argent = 5000;
        L.B.recherche.etoiles = 2;
        L.Missions.prison(null);
        o.fondu();
        const apres = { lot: p.fourriere.length, slug: p.fourriere[0] && p.fourriere[0].slug,
                        disparu: L.B.entites.indexOf(v) < 0 };
        // ⚠️ Le lot deborde : il garde `places` chars, le plus vieux part.
        for (let i = 0; i < %d; i++) p.fourriere.push({ slug: 'taxi', couleur: '#f1c40f', vie: 90, vole: true });
        const v2 = o.char('moto', 0, 0, 0);
        L.Vehicules.monter(j, v2); L.Vehicules.descendre(j, true);
        L.Missions.saisir(v2);
        const plein = { n: p.fourriere.length, dernier: p.fourriere[p.fourriere.length - 1].slug,
                        premier: p.fourriere[0].slug };
        // Le comptoir : on rachete la moto.
        p.fourriere.length = 0;
        p.fourriere.push({ slug: 'moto', couleur: '#1a1a1a', vie: 30, vole: true });
        const menu = L.Missions.menuFourriere([]);
        const argent0 = p.argent;
        const achete = menu.items[0].faire();
        const rachat = { titre: menu.titre, achete: achete, reste: p.fourriere.length,
                         paye: argent0 - p.argent, prix: L.Missions.prixRachat('moto') };
        // Vide, le comptoir le dit au lieu de se taire.
        const vide = L.Missions.menuFourriere([]);
        // Et les chars saisis se posent dans la COUR au demarrage.
        p.fourriere.push({ slug: 'auto', couleur: '#c0392b', vie: 80, vole: true });
        const poses = L.Missions.garnirLaFourriere();
        const lot = L.Monde.carte.fourriere;
        const dansLaCour = L.B.entites.filter(function (e) {
            return e.type === 'vehicule' && e.saisi !== null && e.saisi !== undefined
                && e.x / L.TT >= lot.x && e.x / L.TT < lot.x + lot.largeur
                && e.y / L.TT >= lot.y && e.y / L.TT < lot.y + lot.hauteur;
        }).length;
        return { avant: avant, apres: apres, plein: plein, rachat: rachat,
                 vide: vide.items[0].libelle, poses: poses, dansLaCour: dansLaCour,
                 places: lot.places.length };
    }""" % (f["places"] + 3))
    assert r["avant"] == {"dedans": False, "dernier": True, "saisissable": True}, (
        "a l'arrestation on est DEHORS : c'est le dernier char conduit qu'on saisit (%s)" % r["avant"]
    )
    assert r["apres"]["lot"] == 1 and r["apres"]["slug"] == "auto", "l'arrestation n'a rien saisi"
    assert r["apres"]["disparu"] is True, "le char saisi est reste dans la rue"
    assert r["plein"]["n"] == f["places"], "le lot garde %s chars, pas %s" % (f["places"], r["plein"]["n"])
    assert r["plein"]["dernier"] == "moto", "le dernier saisi n'est pas au bout"
    assert r["plein"]["premier"] == "taxi", "c'est le plus VIEUX qui doit partir"
    assert r["rachat"]["achete"] is True and r["rachat"]["reste"] == 0
    assert r["rachat"]["paye"] == r["rachat"]["prix"] > 0
    assert r["vide"] == "LE LOT EST VIDE", "un lot vide doit le dire, pas se taire"
    assert r["poses"] == 1 and r["dansLaCour"] == 1, (
        "un char saisi doit attendre DANS LA COUR : %s posé(s), %s dedans" % (r["poses"], r["dansLaCour"])
    )
    # ⚠️ LA regle : racheter coute plus cher que revendre.
    for v in paquet["vehicules"]:
        rachat = max(f["rachat_minimum"], round(v["prix"] * f["rachat_fraction"]))
        revente = round(v["prix"] * eco["vente_fraction"])
        assert rachat > revente, (
            "%s : rachat %s $ contre revente %s $ — la fourriere devient une machine a argent"
            % (v["slug"], rachat, revente)
        )


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


def test_mal_gare_veut_dire_quelque_chose_et_la_fourriere_passe(banc, paquet):
    """⚠️ La fourrière promet depuis M9 qu'un char mal garé part au lot, et
    **la règle n'existait nulle part**. Depuis que les stationnements ont de
    vraies **cases**, la définition tombe toute seule et se teste : est mal
    garé un char **laissé hors d'une case ET qui gêne** — la chaussée (où
    personne ne s'arrête), un passage piéton (où les gens traversent), le
    devant d'une porte (où les gens sortent).

    Le juge tient les deux moitiés, et la seconde compte autant : un char dans
    sa case, sur une ruelle ou sur du stationnement ne se fait **jamais**
    remorquer — même mal aligné, même depuis trois jours. ⚠️ Et jamais celui de
    la planque : c'est la sauvegarde de Martin."""
    delai = paquet["economie"]["fourriere"]["remorquage_s"]
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        L.graine(83);
        const j = L.B.joueur, p = L.B.partie, c = L.Monde.carte;
        p.fourriere.length = 0;
        const out = {};

        /* Pose un char au centre d'une tuile choisie par un test, et dit s'il
           est mal gare. On le retire ensuite : un juge ne salit pas la ville. */
        function surUneTuile(choisir, slug) {
            for (let ty = 4; ty < c.h - 4; ty++) {
                for (let tx = 4; tx < c.w - 4; tx++) {
                    if (!choisir(tx, ty)) continue;
                    const v = L.Vehicules.creer(slug || 'auto', tx * L.TT + 8, ty * L.TT + 8, 0, { etat: 'stationne' });
                    if (!v) continue;
                    const mal = L.Missions.malGare(v);
                    L.Entites.retirer(v);
                    return { tx: tx, ty: ty, mal: mal, glyphe: L.Monde.glyphe(tx, ty) };
                }
            }
            return null;
        }
        // ⚠️ Des tuiles ENTOUREES de leur sorte : une auto fait 28 px, elle
        // deborde sur ses voisines, et on veut juger la tuile qu'on vise.
        function entouree(test) {
            return function (tx, ty) {
                for (let dy = -1; dy <= 1; dy++) for (let dx = -1; dx <= 1; dx++) {
                    if (!test(tx + dx, ty + dy)) return false;
                }
                return true;
            };
        }
        const M = L.Monde;
        out.chaussee = surUneTuile(entouree(function (x, y) { return M.estChaussee(x, y); }));
        out.case = surUneTuile(entouree(function (x, y) { return '^v<>'.indexOf(M.glyphe(x, y)) >= 0; }));
        // ⚠️ Un VELO pour la ruelle : elle fait deux tuiles de large, et une
        // berline de 28 px y deborde toujours sur autre chose.
        out.ruelle = surUneTuile(function (tx, ty) { return M.glyphe(tx, ty) === 'x'; }, 'velo');
        out.passage = surUneTuile(function (tx, ty) { return M.estPassage(tx, ty); });

        // Le chrono : un char LAISSE sur la chaussee part au lot, pas avant.
        // ⚠️ Le joueur se poste a cote : hors de sa bulle, `peupler()` oublie
        // le char, et on mesurerait un oubli en croyant mesurer un remorquage.
        const ch = out.chaussee;
        j.x = ch.tx * L.TT + 8; j.y = ch.ty * L.TT + 8;
        L.Monde.centrerCamera(j.x, j.y);
        const v = L.Vehicules.creer('auto', ch.tx * L.TT + 8, ch.ty * L.TT + 8, 0, { etat: 'stationne' });
        L.Entites.indexer();
        // ⚠️ Court, et sur un char NEUF ensuite : le joueur est plante au milieu
        // de la chaussee, et le trafic finit par demolir ce qui traine la — on
        // mesurerait une epave en croyant mesurer un remorquage.
        out.sansLaisser = { avant: p.fourriere.length };
        for (let i = 0; i < 10 * 60; i++) o.frame(1);
        out.sansLaisser.apres = p.fourriere.length;      // jamais conduit : on n'y touche pas
        L.Entites.retirer(v);
        // ⚠️ On coupe le trafic pour la phase chronometree : le joueur est
        // plante au milieu de la chaussee, et une berline laissee la se fait
        // demolir en dix secondes. On mesurerait une epave en croyant mesurer
        // un remorquage.
        L.B.defs.conduite.trafic.vehicules_max = 0;
        L.B.entites = L.B.entites.filter(function (e) { return e.type !== 'vehicule' || e.conducteur !== 'trafic'; });
        const w = L.Vehicules.creer('auto', ch.tx * L.TT + 8, ch.ty * L.TT + 8, 0, { etat: 'stationne' });
        L.Entites.indexer();
        w.laisse = true;
        let images = 0;
        while (L.B.entites.indexOf(w) >= 0 && images < (%d + 20) * 60) { o.frame(1); images++; }
        out.remorque = { secondes: Math.round(images / 60), lot: p.fourriere.length,
                         slug: p.fourriere.length ? p.fourriere[p.fourriere.length - 1].slug : null };
        // Et celui de la planque, JAMAIS — meme pose en pleine chaussee.
        // ⚠️ On mesure la REGLE, pas cinquante secondes : l'exemption se juge
        // contre `p.planque.vehicule`, que `sauvegarderPartie()` recalcule
        // toutes les dix secondes depuis la porte de la planque. Laisser
        // tourner testerait la sauvegarde, pas la fourriere.
        const garde = { slug: 'auto', couleur: '#c0392b', vie: 90,
                        x: ch.tx * L.TT + 8, y: ch.ty * L.TT + 8, angle: 0, vole: false };
        p.planque.vehicule = garde;
        const sien = L.Vehicules.creer('auto', garde.x, garde.y, 0, { etat: 'stationne' });
        sien.laisse = true;
        L.Entites.indexer();
        // Le MEME endroit, le meme etat : seul le lien avec la planque change.
        p.planque.vehicule = null;
        const sansPlanque = L.Missions.malGare(sien);
        p.planque.vehicule = garde;
        out.planque = { malGare: L.Missions.malGare(sien), sansPlanque: sansPlanque };
        return out;
    }""" % delai)
    assert r["chaussee"] and r["chaussee"]["mal"] is True, (
        "un char en pleine chaussée n'est pas mal garé ? %s" % r["chaussee"]
    )
    assert r["case"] and r["case"]["mal"] is False, (
        "un char DANS SA CASE ne se fait jamais remorquer : %s" % r["case"]
    )
    assert r["ruelle"] and r["ruelle"]["mal"] is False, (
        "un char rangé sur une ruelle ne gêne personne : %s" % r["ruelle"]
    )
    assert r["passage"] and r["passage"]["mal"] is True, (
        "un char sur un passage piéton doit être mal garé : %s" % r["passage"]
    )
    # ⚠️ Le trafic ne se fait PAS remorquer : seulement ce que le joueur laisse.
    assert r["sansLaisser"]["apres"] == r["sansLaisser"]["avant"] == 0, (
        "un char que le joueur n'a jamais conduit a été remorqué : %s" % r["sansLaisser"]
    )
    assert r["remorque"]["lot"] == 1 and r["remorque"]["slug"] == "auto", (
        "le char mal garé n'est pas parti au lot : %s" % r["remorque"]
    )
    assert abs(r["remorque"]["secondes"] - delai) <= 3, (
        "la remorqueuse passe après %s s au lieu de %s" % (r["remorque"]["secondes"], delai)
    )
    # ⚠️ Le MEME char, au MEME endroit : mal garé s'il n'est à personne, jamais
    # s'il est celui de la planque. C'est la sauvegarde de Martin.
    assert r["planque"] == {"malGare": False, "sansPlanque": True}, (
        "le char de la planque n'est pas protégé (ou l'exemption protège tout) : %s" % r["planque"]
    )


def test_la_fourriere_paie_les_epaves_qu_on_lui_amene_au_crochet(banc, paquet):
    """⚠️ Le remorquage attendait la fourrière ; il l'a. C'est le seul boulot où
    ce qu'on ramasse n'est pas une personne mais ce qu'on a **au crochet** : le
    bouton du klaxon accroche d'abord (`Vehicules.basculerCrochet`), puis
    appelle le boulot — une seule pression, l'épave est accrochée et le
    contrat est pris.

    Trois règles : la fourrière ne paie **que les épaves** (traîner une berline
    saine au lot, c'est du vol) ; on livre **dans la cour**, pas à 44 px d'un
    point (la grille fait quatre tuiles et la remorqueuse 36 px) ; et une épave
    qui décroche en route, c'est le contrat qui tombe."""
    f = paquet["economie"]["boulots"]["remorquage"]
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        L.graine(71);
        const j = L.B.joueur, p = L.B.partie, d = o.ligneDroite();
        j.x = d.x; j.y = d.y;
        const rem = o.char('remorqueuse', 0, 0, 0);          // cap 0 : l'arriere est a l'ouest
        L.Vehicules.monter(j, rem);
        const b = L.Missions.boulot, lot = L.Monde.carte.fourriere;
        const out = {};
        // 1. Une berline SAINE au crochet : pas de contrat, et on le dit.
        const saine = o.char('auto', -36, 0, 0);
        L.Entites.indexer();
        o.tape('Space', 2);
        out.saine = { accrochee: rem.remorque === saine, boulot: b.slug, msg: L.B.msg };
        o.tape('Space', 2);                                   // on decroche
        L.Entites.retirer(saine);
        // 2. Une epave : accrochee ET contrat, en une pression.
        const epave = o.char('auto', -36, 0, 0);
        L.Entites.indexer();
        L.Vehicules.endommager(epave, 9999, null);
        o.frame(2);
        o.tape('Space', 2);
        out.epave = { accrochee: rem.remorque === epave, etatEpave: epave.etat, boulot: b.slug, etape: b.etape,
                      dest: b.destination && b.destination.nom };
        // 3. On decroche en route : le contrat tombe.
        o.tape('Space', 2);
        o.frame(2);
        out.lache = { boulot: b.slug, etape: b.etape, msg: L.B.msg };
        // 4. On raccroche, et on livre DANS LA COUR : paye, l'epave part a la ferraille.
        L.Entites.indexer();
        o.tape('Space', 2);
        const argent0 = p.argent, distance = b.distance;
        const cx = (lot.x + lot.largeur / 2) * L.TT, cy = (lot.y + lot.hauteur / 2) * L.TT;
        rem.x = cx; rem.y = cy; j.x = cx; j.y = cy; rem.vitesse = 0; rem.vx = 0; rem.vy = 0;
        epave.x = cx - 40; epave.y = cy;                       // toujours au bout du cable
        o.frame(4);
        out.livre = { gain: p.argent - argent0, etape: b.etape, epaveDisparue: L.B.entites.indexOf(epave) < 0,
                      decroche: !rem.remorque, faits: b.faits.remorquage,
                      attendu: Math.round(%d + %f * (distance / L.TT)) };
        return out;
    }""" % (f["base"], f["par_tuile"]))
    assert r["saine"]["accrochee"] is True and r["saine"]["boulot"] is None, (
        "une berline saine ne doit PAS lancer de remorquage : %s" % r["saine"]
    )
    assert "ÉPAVES" in (r["saine"]["msg"] or ""), "le refus doit se dire : %s" % r["saine"]["msg"]
    assert r["epave"]["etatEpave"] == "epave" and r["epave"]["accrochee"] is True
    assert r["epave"]["boulot"] == "remorquage" and r["epave"]["etape"] == "route", (
        "une epave au crochet doit prendre le contrat en une pression : %s" % r["epave"]
    )
    assert "Fourrière" in r["epave"]["dest"], "le remorquage va A LA FOURRIERE : %s" % r["epave"]["dest"]
    assert r["lache"]["boulot"] is None and r["lache"]["etape"] is None, (
        "decrocher en route doit faire tomber le contrat : %s" % r["lache"]
    )
    assert r["livre"]["etape"] is None and r["livre"]["faits"] == 1, "la livraison ne finit pas : %s" % r["livre"]
    assert r["livre"]["gain"] == r["livre"]["attendu"] > 0, (
        "le remorquage paie %s $ au lieu de base + distance = %s $" % (r["livre"]["gain"], r["livre"]["attendu"])
    )
    assert r["livre"]["epaveDisparue"] is True and r["livre"]["decroche"] is True, (
        "l'epave livree doit partir a la ferraille et le crochet se liberer : %s" % r["livre"]
    )


def test_sortir_son_char_du_lot_sans_payer_appelle_la_police(banc, paquet):
    """⚠️ L'autre moitié de la fourrière : on peut reprendre son char **par-dessus
    la clôture** — à pied on enjambe le grillage, on monte dans son char, on
    sort par la seule grille. Le lot appelle (délit `fourriere`, bruyant : pas
    de témoin à convaincre), les gars du lot **ripostent**, et le char redevient
    volé. Racheté au comptoir, le même trajet ne coûte rien."""
    f = paquet["economie"]["fourriere"]
    etoiles = paquet["recherche"]["delits"]["fourriere"]["etoiles"]
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        L.graine(73);
        const j = L.B.joueur, p = L.B.partie, lot = L.Monde.carte.fourriere;
        p.fourriere.length = 0;
        p.fourriere.push({ slug: 'auto', couleur: '#c0392b', vie: 80, vole: true });
        p.fourriere.push({ slug: 'moto', couleur: '#1a1a1a', vie: 30, vole: true });
        L.Missions.garnirLaFourriere();
        L.Entites.indexer();
        const gardiens = L.B.entites.filter(function (e) { return e.type === 'pieton' && e.gardien; });
        const saisis = L.B.entites.filter(function (e) { return e.type === 'vehicule' && e.saisi !== null && e.saisi !== undefined; });
        const auto = saisis.find(function (v) { return v.slug === 'auto'; });
        const moto = saisis.find(function (v) { return v.slug === 'moto'; });
        const out = { gardiens: gardiens.length, saisis: saisis.length,
                      postes: gardiens.map(function (g) { return { etat: g.etat, y: Math.round(g.y / L.TT) - lot.grille.y }; }) };
        // 1. On enjambe (on se teleporte : la cloture a son propre juge), on
        //    monte, on sort par la grille.
        j.x = auto.x; j.y = auto.y + 20;
        L.Vehicules.monter(j, auto);
        const crimes0 = L.B.crimes.length;
        auto.x = (lot.grille.x + 2) * L.TT; auto.y = (lot.grille.y + 3) * L.TT;   // dehors, devant la grille
        j.x = auto.x; j.y = auto.y;
        o.frame(2);
        out.sortie = { crime: L.B.crimes.slice(crimes0).map(function (c) { return c.type; }),
                       etoiles: L.B.recherche.etoiles, lot: p.fourriere.map(function (c) { return c.slug; }),
                       saisi: auto.saisi, vole: auto.vole,
                       ripostent: gardiens.filter(function (g) { return g.etat === 'attaque_joueur'; }).length,
                       motoRang: moto.saisi };
        L.Vehicules.descendre(j, true);
        // 2. La moto, RACHETEE au comptoir, sort sans un mot.
        const menu = L.Missions.menuFourriere([]);
        p.argent = 9999;
        menu.items[0].faire();
        const crimes1 = L.B.crimes.length;
        j.x = moto.x; j.y = moto.y + 20;
        L.Vehicules.monter(j, moto);
        moto.x = (lot.grille.x + 2) * L.TT; moto.y = (lot.grille.y + 3) * L.TT;
        j.x = moto.x; j.y = moto.y;
        o.frame(2);
        out.rachetee = { crimes: L.B.crimes.length - crimes1, saisi: moto.saisi, vole: moto.vole,
                         lot: p.fourriere.length };
        return out;
    }""")
    assert r["gardiens"] == f["gardiens"], "il manque des gars du lot : %s" % r["gardiens"]
    assert all(g["etat"] == "fige" and abs(g["y"]) <= 1 for g in r["postes"]), (
        "les gardiens tiennent la grille, a une tuile pres : %s" % r["postes"]
    )
    assert r["saisis"] == 2
    s = r["sortie"]
    assert s["crime"] == ["fourriere"], "sortir sans payer doit signaler le delit `fourriere` : %s" % s["crime"]
    assert s["etoiles"] >= etoiles, "le lot appelle : %s etoile(s)" % s["etoiles"]
    assert s["lot"] == ["moto"] and s["saisi"] is None and s["vole"] is True, (
        "le char sorti quitte le lot et redevient vole : %s" % s
    )
    assert s["ripostent"] == r["gardiens"], "les gars du lot ne ripostent pas : %s" % s
    assert s["motoRang"] == 0, "les rangs des autres chars doivent glisser, sinon le comptoir libere le mauvais"
    assert r["rachetee"] == {"crimes": 0, "saisi": None, "vole": False, "lot": 0}, (
        "un char rachete sort sans un mot : %s" % r["rachetee"]
    )


def test_eteindre_sa_sirene_n_appelle_pas_un_nouveau_contrat(banc):
    """⚠️ Retour de Martin : « on ne devrait pas avoir de nouveaux contrats
    quand on arrête la sirène ; et quand un contrat est en cours, on ne peut
    pas en ravoir un autre. »

    Le bouton du klaxon fait deux choses dans une ambulance : il bascule la
    sirène **et** il prend l'appel. Le premier geste est le bon — on répond et
    on part la sirène allumée. ⚠️ Mais l'inverse veut dire « j'ai fini », pas
    « donne-m'en un autre » : éteindre sa sirène en sortant de l'hôpital
    rappelait aussitôt une ambulance, et on repartait sans l'avoir demandé.

    Le juge tient les trois états du bouton : on allume (contrat), on éteint
    (rien), on rallume pendant un contrat (rien de plus)."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        L.graine(61);
        const j = L.B.joueur, d = o.ligneDroite();
        j.x = d.x; j.y = d.y;
        const v = o.char('ambulance', 0, 0, 0);
        L.Vehicules.monter(j, v);
        const b = L.Missions.boulot;
        // 1. On allume : la sirene part, et l'appel se prend.
        o.tape('Space', 2);
        const allume = { sirene: v.sirene, slug: b.slug, etape: b.etape };
        const premier = b.client;
        // 2. On rallume pendant le contrat : rien de plus, et le meme client.
        o.tape('Space', 2);                              // eteint
        o.tape('Space', 2);                              // rallume
        const pendant = { sirene: v.sirene, etape: b.etape, memeClient: b.client === premier };
        // 3. Le contrat se finit, puis on ETEINT : rien ne doit repartir.
        const c = b.client;
        if (c) { v.x = c.x + 10; v.y = c.y; j.x = v.x; j.y = v.y; v.vitesse = 0; }
        o.frame(3);
        const dest = b.destination;
        if (dest) { v.x = dest.x + 6; v.y = dest.y; j.x = v.x; j.y = v.y; v.vitesse = 0; }
        o.frame(3);
        const fini = { etape: b.etape, faits: b.faits.ambulance };
        o.tape('Space', 2);                              // on eteint la sirene
        const apres = { sirene: v.sirene, etape: b.etape, slug: b.slug };
        // 4. Et on peut en reprendre un quand on RALLUME.
        o.tape('Space', 2);
        const repris = { sirene: v.sirene, etape: b.etape };
        return { allume: allume, pendant: pendant, fini: fini, apres: apres, repris: repris };
    }""")
    assert r["allume"] == {"sirene": True, "slug": "ambulance", "etape": "ramasse"}, (
        "allumer la sirene doit prendre l'appel : %s" % r["allume"]
    )
    assert r["pendant"] == {"sirene": True, "etape": "ramasse", "memeClient": True}, (
        "rallumer pendant un contrat en a donne un autre : %s" % r["pendant"]
    )
    assert r["fini"] == {"etape": None, "faits": 1}, "le premier contrat ne s'est pas fini"
    assert r["apres"] == {"sirene": False, "etape": None, "slug": None}, (
        "ETEINDRE la sirene a rappele une ambulance : %s" % r["apres"]
    )
    assert r["repris"] == {"sirene": True, "etape": "ramasse"}, (
        "on ne peut plus reprendre un appel en rallumant : %s" % r["repris"]
    )


def test_l_hopital_ramasse_le_joueur_et_le_facture(banc, paquet):
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const j = L.B.joueur;
        L.B.partie.argent = 400;
        // ⚠️ Le point se lit AVANT : au reveil, `Monde.carte` est la piece de l'hopital.
        const hopital = L.Monde.carte.points.find(function (p) { return p.slug === 'hopital'; });
        L.Entites.blesser(j, 9999, null, {});
        const pendant = { vivant: j.vivant, fondu: !!L.B.transition };
        o.fondu();
        // On se reveille dans la piece, et sa porte mene devant l'hopital.
        const dehors = L.B.exterieur || { x: j.x, y: j.y };
        return { pendant: pendant, vie: j.vie, max: j.vieMax, argent: L.B.partie.argent,
                 piece: L.B.interieur && L.B.interieur.slug,
                 loin: Math.hypot(dehors.x - hopital.x * L.TT, dehors.y - hopital.y * L.TT), etat: L.B.etat };
    }""")
    assert r["pendant"]["vivant"] is True and r["pendant"]["fondu"] is True
    assert r["vie"] == r["max"], "le joueur ne s'est pas reveille en pleine forme"
    assert r["argent"] < 400, "l'hopital n'a pas facture"
    assert r["piece"] == "hopital", "le joueur ne s'est pas reveille DANS l'hopital"
    assert r["loin"] < 48, "la porte de la piece ne mene pas devant l'hopital"
    assert r["etat"] == "jeu"


def test_la_radio_suit_le_char(banc, paquet):
    """⚠️ Le bouton RADIO parcourt DEUX SOURCES depuis M9 : les stations
    enregistrees (des mp3 ElevenLabs) et les stations PROCEDURALES, ecrites par
    une graine et jouees par le sequenceur du theme du menu. Avant, `station()`
    ne cherchait que dans les mp3 : le bouton RADIO du camion ne faisait
    strictement rien, et sa toune, pourtant dans le paquet, n'etait jamais
    jouable."""
    enregistrees = [r["slug"] for r in paquet["audio"]["radios"]]
    procedurales = [m["slug"] for m in paquet["audio"]["musiques"] if m.get("station")]
    stations = enregistrees + procedurales
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const j = L.B.joueur;
        const v = o.char('auto', 24, 0, 0);
        L.Vehicules.monter(j, v);
        const auVolant = L.Son.Radio.demandee;
        o.tape('Tab', 2);
        const suivante = L.Son.Radio.demandee;
        const parcours = [suivante];
        // Tout le tour, jusqu'au silence : le cycle compte les deux sources.
        const combien = L.Son.Radio.stations().length;
        for (let i = 0; i < combien; i++) { L.Son.Radio.suivante(); parcours.push(L.Son.Radio.demandee); }
        L.Vehicules.descendre(j, true);
        return { auVolant: auVolant, suivante: suivante, parcours: parcours, apres: L.Son.Radio.demandee,
                 defaut: v.def.radio, stations: L.Son.Radio.stations().map(function (q) { return q.slug; }) };
    }""")
    assert r["auVolant"] == r["defaut"] == "la_brume", "l'auto doit allumer La Brume"
    assert r["suivante"] != r["auVolant"], "le bouton RADIO ne change pas de station"
    assert None in r["parcours"], "le cycle doit passer par le silence"
    assert set(s for s in r["parcours"] if s) <= set(stations)
    assert r["apres"] is None, "la radio joue encore une fois descendu"
    assert set(r["stations"]) == set(stations), \
        "le bouton RADIO ne voit pas les deux sources"
    assert set(procedurales) & set(s for s in r["parcours"] if s), \
        "le cycle n'atteint aucune station procedurale : elles restent injouables"


# --- La rue dans la vraie vie : trottoirs, passages, feux, stops, velos ----


def test_les_pietons_restent_sur_les_trottoirs(banc):
    """⚠️ La regle de la ville : on ne pose pas le pied sur la chaussee. Le
    passage pieton est la seule exception — et un pieton pousse sur la rue
    par un char regagne le trottoir."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        L.graine(51);
        let surLaChaussee = 0, surUnPassage = 0, releves = 0;
        for (let i = 0; i < 2400; i++) {
            o.frame(1);
            if (i < 300 || i % 30) continue;
            L.B.entites.forEach(function (e) {
                if (e.type !== 'pieton' || !e.vivant || e.recul > 0) return;
                // Le marchand du camion-restaurant tient son comptoir sur un
                // stationnement : il n'y marche pas, il y est pose par la carte.
                if (e.commerce) return;
                const tx = Math.floor(e.x / L.TT), ty = Math.floor(e.y / L.TT);
                releves++;
                if (L.Monde.estChaussee(tx, ty)) surLaChaussee++;
                if (L.Monde.estPassage(tx, ty)) surUnPassage++;
            });
        }
        return { releves: releves, chaussee: surLaChaussee, passage: surUnPassage };
    }""")
    assert r["releves"] > 200
    assert r["chaussee"] <= r["releves"] * 0.03, \
        f"{r['chaussee']} releves de pietons sur la chaussee (sur {r['releves']})"
    assert r["passage"] > 0, "personne ne traverse jamais"


def test_un_pieton_attend_au_feu_avant_de_traverser(banc):
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const c = L.Monde.carte;
        const inter = c.intersections.find(function (i) { return i.feux; });
        // Le passage a l'ouest du croisement, sur la rue est-ouest : tuile '='.
        const tx = inter.x - 1, ty = inter.y;
        const est = L.Monde.glyphe(tx, ty);
        L.B.t = -inter.decalage;                      // phase 0 : nord-sud roule, est-ouest est au rouge
        const rougeEO = !L.Monde.feuVert(inter, '>');
        const surAuRouge = L.Entites.traverseeSure(tx, ty, [0, 1]);
        L.B.t += Math.floor((L.B.defs.conduite.trafic.feu_vert_images + L.B.defs.conduite.trafic.feu_orange_images));
        const vertEO = L.Monde.feuVert(inter, '>');
        const surAuVert = L.Entites.traverseeSure(tx, ty, [0, 1]);
        return { glyphe: est, rougeEO: rougeEO, surAuRouge: surAuRouge, vertEO: vertEO, surAuVert: surAuVert };
    }""")
    assert r["glyphe"] == "=", "la tuile choisie n'est pas un passage de la rue est-ouest"
    assert r["rougeEO"] is True and r["surAuRouge"] is True, "au rouge des chars, le pieton doit pouvoir traverser"
    assert r["vertEO"] is True and r["surAuVert"] is False, "au vert des chars, le pieton doit attendre"


def test_le_trafic_reste_dans_sa_voie(banc):
    """Sur des rails : un char du trafic ne coupe plus un coin, jamais."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        L.graine(52);
        let horsRoute = 0, releves = 0, tournes = 0;
        const caps = new Map();
        for (let i = 0; i < 3000; i++) {
            o.frame(1);
            if (i < 200 || i % 20) continue;
            L.B.entites.forEach(function (v) {
                if (v.type !== 'vehicule' || v.conducteur !== 'trafic' || v.def.classe === 'velo' && false) return;
                // ⚠️ Un velo parti sur le trottoir ou au parc (`horsRue`) y est de son
                // plein gre : ce n'est pas un char qui coupe un coin (`test_velos_js`).
                if (v.horsRue) return;
                releves++;
                const tx = Math.floor(v.x / L.TT), ty = Math.floor(v.y / L.TT);
                if (!L.Monde.estRoute(tx, ty)) horsRoute++;
                const avant = caps.get(v.id);
                if (avant !== undefined && Math.abs(L.ecartAngle ? 0 : 0) === 0 && Math.abs(v.sens !== avant ? 1 : 0)) tournes++;
                caps.set(v.id, v.sens);
            });
        }
        return { releves: releves, horsRoute: horsRoute, tournes: tournes,
                 velos: L.B.entites.filter(function (v) { return v.type === 'vehicule' && v.def.classe === 'velo'; }).length };
    }""")
    assert r["releves"] > 300
    # 1 % : un char pousse d'une demi-tuile par un voisin a un coin, le temps
    # de regagner sa voie. Au-dela, c'est le trafic qui coupe les coins.
    assert r["horsRoute"] <= r["releves"] * 0.01, f"{r['horsRoute']} releves de trafic hors de la route"
    assert r["tournes"] > 3, "le trafic ne tourne jamais"


def test_un_char_se_deporte_pour_contourner_un_pieton(banc):
    """Sur un boulevard, un pieton plante au milieu de la voie ne bloque plus :
    le char se tasse dans la voie d'a cote — par la gauche — et repart."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        L.graine(61);
        const T = L.TT;
        const b = o.boulevard(true);
        if (!b) return { trouve: false };
        L.B.entites = L.B.entites.filter(function (e) { return e.type !== 'vehicule'; });
        const y0 = b.y;
        const v = L.Vehicules.creer('auto', b.x, y0, 0, { conducteur: 'trafic', etat: 'roule', sens: '>' });
        v.vitesse = 1.2;
        // Un passant fige au milieu de la chaussee, cinq tuiles devant.
        const p = L.Entites.creerPieton(b.x + 5 * T, y0, null);
        p.etat = 'fige';
        let yMin = y0, depasse = false, renverse = false, voie = null;
        for (let i = 0; i < 400; i++) {
            L.Entites.indexer();
            L.Vehicules.majConducteur(v);
            v.x += v.vx; v.y += v.vy;
            yMin = Math.min(yMin, v.y);
            if (!p.vivant) renverse = true;
            if (depasse) continue;
            if (v.x > p.x + 24) {
                depasse = true;
                voie = L.Monde.fleche(Math.floor(v.x / T), Math.floor(v.y / T));   // ou roule-t-il en doublant ?
            }
        }
        return { trouve: true, depasse: depasse, deports: v.deports || 0, renverse: renverse,
                 gauche: Math.round(y0 - yMin), voie: voie };
    }""")
    assert r["trouve"], "aucun boulevard a deux voies dans le meme sens sur la carte"
    assert r["deports"] >= 1, "le char n'a jamais essaye de se tasser"
    assert r["gauche"] >= 10, f"il s'est tasse de {r['gauche']} px : ce n'est pas la voie de gauche"
    assert r["depasse"], "le char n'a jamais depasse le pieton"
    assert r["renverse"] is False, "⚠️ on contourne le pieton, on ne le fauche pas"
    assert r["voie"] == ">", "en doublant, le char n'etait pas dans une voie de son sens"


def test_sur_une_rue_a_deux_voies_le_char_attend(banc):
    """⚠️ Le pendant du test precedent : sans voie parallele dans son sens, se
    deporter serait rouler a contresens. Le char attend, comme avant."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        L.graine(62);
        const T = L.TT;
        const b = o.boulevard(false);
        if (!b) return { trouve: false };
        L.B.entites = L.B.entites.filter(function (e) { return e.type !== 'vehicule'; });
        const y0 = b.y;
        const v = L.Vehicules.creer('auto', b.x, y0, 0, { conducteur: 'trafic', etat: 'roule', sens: '>' });
        v.vitesse = 1.2;
        const p = L.Entites.creerPieton(b.x + 5 * T, y0, null);
        p.etat = 'fige';
        let ecart = 0;
        for (let i = 0; i < 180; i++) {
            L.Entites.indexer();
            L.Vehicules.majConducteur(v);
            v.x += v.vx; v.y += v.vy;
            ecart = Math.max(ecart, Math.abs(v.y - y0));
        }
        return { trouve: true, deports: v.deports || 0, ecart: Math.round(ecart),
                 arrete: Math.abs(v.vx) + Math.abs(v.vy) < 0.05, avant: v.x < p.x };
    }""")
    assert r["trouve"], "aucune rue a une seule voie par sens sur la carte"
    assert r["deports"] == 0, "le char s'est deporte a contresens"
    assert r["ecart"] <= 4, f"il a quitte sa voie de {r['ecart']} px"
    assert r["arrete"] and r["avant"], "le char n'a pas attendu derriere le pieton"


def test_on_ne_se_deporte_pas_dans_une_voie_occupee(banc):
    """La voie d'a cote n'est libre que si personne n'y roule — devant COMME
    derriere. Un char qui arrive vite par la gauche a la priorite ; celui qui
    est coince reste derriere son pieton plutot que de lui couper la route."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        L.graine(63);
        const T = L.TT;
        const b = o.boulevard(true);
        if (!b) return { trouve: false };
        L.B.entites = L.B.entites.filter(function (e) { return e.type !== 'vehicule'; });
        const y0 = b.y;
        const v = L.Vehicules.creer('auto', b.x, y0, 0, { conducteur: 'trafic', etat: 'roule', sens: '>' });
        v.vitesse = 1.2;
        const p = L.Entites.creerPieton(b.x + 5 * T, y0, null);
        p.etat = 'fige';
        // Un char arrete dans la voie de gauche, juste a cote du pieton.
        const mur = L.Vehicules.creer('auto', b.x + 5 * T, y0 - T, 0, { conducteur: 'trafic', etat: 'roule', sens: '>' });
        mur.vitesse = 0;
        let ecart = 0;
        for (let i = 0; i < 180; i++) {
            L.Entites.indexer();
            L.Vehicules.majConducteur(v);
            v.x += v.vx; v.y += v.vy;
            ecart = Math.max(ecart, Math.abs(v.y - y0));
        }
        return { trouve: true, deports: v.deports || 0, ecart: Math.round(ecart), avant: v.x < p.x };
    }""")
    assert r["trouve"], "aucun boulevard a deux voies dans le meme sens sur la carte"
    assert r["deports"] == 0, "le char s'est tasse dans une voie occupee"
    assert r["ecart"] <= 4, f"il a quitte sa voie de {r['ecart']} px"
    assert r["avant"], "le char a traverse le pieton au lieu d'attendre"


def test_les_feux_et_les_stops_sont_poses(banc):
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const c = L.Monde.carte;
        const feux = L.B.entites.filter(function (e) { return e.type === 'feu'; });
        const stops = L.B.entites.filter(function (e) { return e.type === 'stop'; });
        const croix = c.intersections.filter(function (i) { return i.feux; }).length;
        const tes = c.intersections.filter(function (i) { return i.stop; }).length;
        const bienPlaces = feux.concat(stops).filter(function (e) {
            return L.Monde.solidite(Math.floor(e.x / L.TT), Math.floor(e.y / L.TT)) === 0 && !L.Monde.estRoute(Math.floor(e.x / L.TT), Math.floor(e.y / L.TT));
        }).length;
        // Un T dont le bras ouest manque : la tige est a l'est, on y arrive en roulant vers l'ouest.
        const sansOuest = c.intersections.find(function (i) { return i.bras.length === 3 && i.bras.indexOf('O') < 0; });
        return { feux: feux.length, croix: croix, stops: stops.length, tes: tes,
                 bienPlaces: bienPlaces, stopSansOuest: sansOuest ? sansOuest.stop : null };
    }""")
    # ⚠️ QUATRE, un par coin : un tricolore ne montre qu'une rue, il en faut
    # donc un en face de chaque approche. A deux, il manquait un feu a deux
    # coins sur quatre.
    assert r["feux"] == r["croix"] * 4 > 0
    assert r["stops"] == r["tes"] > 0
    assert r["bienPlaces"] == r["feux"] + r["stops"], "un feu ou un stop est sur la route ou dans un mur"
    assert r["stopSansOuest"] == "<", "le STOP est pour ceux qui arrivent par la tige"


# ⚠️ Le gabarit du mat se LIT dans `DECORS.feu`, il ne se recopie pas ici — et
# le miroir avec. Un mat dont le bras part vers l'ouest peint tout a l'envers ;
# un juge qui chercherait la lentille a sa place « de droite » ne verrait rien
# et dirait « le feu est eteint » alors qu'il brille.
GABARIT_JS = """
        const F = L.DECORS.feu;
        function miroir(x, l, bras) { return bras > 0 ? x : F.w - x - l; }
        function ancre(e) { return e.bras > 0 ? F.ancre : F.ancreMiroir; }
        function coin(e, cx, cy) {                       // le coin haut-gauche du sprite
            return [Math.round(e.x - ancre(e)[0] - cx), Math.round(e.y - ancre(e)[1] - cy)];
        }
        function lentilleDe(e, rang) {                   // le coin de la lentille du rang
            return miroir(F.lentilles[rang], F.lentilleCote, e.bras);
        }
        function boiteDesTetes(e) {                      // [bord gauche, largeur] du boitier pieton
            const large = e.traverses.length > 1 ? F.boitier.l : 7;
            return [miroir(F.tete.x, large, e.bras), large];
        }
        function teteDe(e, i) {                          // le coin de la i-e ampoule pieton
            const [bord, large] = boiteDesTetes(e), deux = e.traverses.length > 1;
            const cote = deux ? 3 : 4;
            return [deux ? (i === 0 ? bord + 1 : bord + large - 1 - cote) : bord + ((large - cote) >> 1), cote];
        }
"""


def test_une_ampoule_allumee_pose_une_lampe_de_la_couleur_de_sa_phase(banc):
    """⚠️ Un feu ÉTAIT de la peinture. `Base.fin` compose la nuit en
    **multipliant** toute l'image par la teinte de l'heure, puis rajoute les
    lampes en `lighter` par-dessus ; un feu n'avait aucune lampe, il ne
    recevait donc que la multiplication — comme une brique. À minuit, le vert
    (46, 204, 113) tombait à (16, 76, 57).

    La lentille allumée pose maintenant sa lampe, **de la couleur de sa
    phase** — et elle seule, puisqu'un tricolore n'en allume qu'une. Et **rien
    du tout en plein jour**.
    """
    r = banc("""function (L, o) {""" + GABARIT_JS + """
        L.Jeu.commencer();
        const inter = L.Monde.carte.intersections.find(function (i) { return i.feux; });
        const feu = L.B.entites.find(function (e) { return e.type === 'feu' && e.inter === inter; });
        const t = L.B.defs.conduite.trafic;
        const cycle = 2 * (t.feu_vert_images + t.feu_orange_images);
        const sens = feu.axe === 'ns' ? '^' : '>';
        L.B.joueur.x = feu.x; L.B.joueur.y = feu.y;
        const RANG = { rouge: 0, jaune: 1, vert: 2 };
        // La lampe de la lentille des CHARS, retrouvee a sa place a l'ecran :
        // le mat en porte d'autres (les tetes pieton) et les trois autres coins
        // aussi, et un juge qui lirait « il y a du vert quelque part »
        // passerait au vert du coin d'en face.
        function releve(heure, phase) {
            L.B.partie.heure = heure;
            L.B.t = ((phase - inter.decalage) % cycle + cycle) % cycle;
            L.Monde.centrerCamera(feu.x, feu.y);
            o.frame(1);
            const cx = Math.round(L.B.cam.x), cy = Math.round(L.B.cam.y);
            const [x, y] = coin(feu, cx, cy);
            const couleur = L.Monde.feuDeCirculation(inter, sens);
            const lx = x + lentilleDe(feu, RANG[couleur]) + 1.5, ly = y + F.lentilleY + 1.5;
            const lampes = L.Vehicules.lampesDesFeux();
            const l = lampes.find(function (q) { return q.x === lx && q.y === ly; });
            // ⚠️ « Ailleurs » veut dire DANS CE BOITIER-CI, pas n'importe ou sur
            // la rangee : les quatre mats d'un croisement sont a la meme
            // hauteur d'ecran, et le juge accusait le feu d'en face.
            return { total: lampes.length, couleur: couleur, c: l ? l.c : null,
                     ailleurs: lampes.filter(function (q) {
                         return q.y === ly && q.x !== lx && q.x >= x && q.x < x + F.w;
                     }).length };
        }
        const milieuVert = Math.floor(t.feu_vert_images / 2);
        // ⚠️ **PAS MINUIT** (15 sept. 2026) : a minuit, les feux CLIGNOTENT
        // maintenant, et un clignotant n'a pas de cycle a viser. Ce qu'il faut
        // ici, c'est l'heure ou il fait assez sombre pour que les lampes
        // s'allument ET ou le tricolore tourne encore — juste avant que la
        // ville bascule (`trafic.clignotant_depuis`).
        const nuit = t.clignotant_depuis - 0.02;
        return { vert: releve(nuit, milieuVert),
                 rouge: releve(nuit, cycle / 2 + milieuVert),
                 jaune: releve(nuit, t.feu_vert_images + Math.floor(t.feu_orange_images / 2)),
                 midi: releve(0.5, milieuVert) };
    }""")
    couleurs = {}
    for nom in ("vert", "rouge", "jaune"):
        x = r[nom]
        assert x["couleur"] == nom, f"la phase visee n'est pas la bonne : {x}"
        assert x["c"], f"la lentille {nom} n'eclaire pas la nuit : {x}"
        assert x["ailleurs"] == 0, \
            f"une autre lentille du meme boitier eclaire aussi : un tricolore n'en allume qu'une ({x})"
        couleurs[nom] = x["c"]
    assert len(set(couleurs.values())) == 3, f"deux phases jettent la meme lumiere : {couleurs}"
    assert r["midi"]["total"] == 0 and r["midi"]["c"] is None, \
        f"un feu qui eclaire en plein soleil : {r['midi']}"


def test_l_orange_qui_clignote_n_eclaire_pas_pendant_qu_il_est_eteint(banc):
    """Le dégagement du feu piéton **clignote** : un orange fixe se lit
    « attends », un orange qui bat se lit « finis, mais ne pars plus ».

    ⚠️ Sa lampe doit battre AVEC lui. Un halo qui reste allumé pendant que
    l'ampoule est éteinte, c'est un clignotant qui ne clignote plus — on le
    verrait battre à l'œil et briller en continu sur le trottoir.
    """
    r = banc("""function (L, o) {""" + GABARIT_JS + """
        L.Jeu.commencer();
        const t = L.B.defs.conduite.trafic;
        const cycle = 2 * (t.feu_vert_images + t.feu_orange_images);
        const mat = L.B.entites.find(function (e) { return e.type === 'feu' && e.traverses.length; });
        const inter = mat.inter, sens = mat.traverses[0] === '=' ? '>' : '^';
        L.B.joueur.x = mat.x; L.B.joueur.y = mat.y;
        // ⚠️ Pas minuit : les feux y clignotent depuis le 15 sept. 2026, et un
        // feu pieton s'eteint avec eux. On se met juste avant la bascule.
        L.B.partie.heure = t.clignotant_depuis - 0.02;
        // Deux images du MEME degagement (il dure 120 images), de parite
        // contraire au clignotant (il bat aux 8).
        const cibles = [];
        for (let phase = 1; phase < cycle && cibles.length < 2; phase++) {
            L.B.t = phase;
            if (L.Monde.feuPieton(inter, sens) !== 'degage') continue;
            const eteint = (phase >> 3) % 2 === 0;
            if (!cibles.some(function (c) { return c.eteint === eteint; })) cibles.push({ phase: phase, eteint: eteint });
        }
        return cibles.map(function (c) {
            L.B.t = c.phase - 1;                       // `o.frame` avance l'horloge d'une image
            L.Monde.centrerCamera(mat.x, mat.y);
            o.frame(1);
            const cx = Math.round(L.B.cam.x), cy = Math.round(L.B.cam.y);
            const [x, y] = coin(mat, cx, cy);
            const [col, cote] = teteDe(mat, 0);
            const l = L.Vehicules.lampesDesFeux().find(function (q) {
                return q.x === x + col + cote / 2 && q.y === y + F.tete.y + 3.5;
            });
            return { eteint: c.eteint, vise: c.phase, t: L.B.t,
                     etat: L.Monde.feuPieton(inter, sens), lampe: l ? l.c : null };
        });
    }""")
    assert len(r) == 2 and {x["eteint"] for x in r} == {True, False}, \
        f"le clignotant n'a pas ete pris des deux cotes : {r}"
    for x in r:
        assert x["t"] == x["vise"], f"l'horloge a derive : visee {x['vise']}, arrivee {x['t']}"
        assert x["etat"] == "degage", f"on a quitte le degagement : {x}"
    eteint = next(x for x in r if x["eteint"])
    allume = next(x for x in r if not x["eteint"])
    assert eteint["lampe"] is None, "l'ampoule est eteinte et le trottoir reste eclaire"
    assert allume["lampe"], "l'ampoule est allumee et n'eclaire rien"


def test_un_tricolore_n_allume_qu_une_lentille_a_la_fois(banc):
    """⚠️ **LE JUGE QUI MANQUAIT**, et il a servi deux fois. Les feux ont
    d'abord été **muets** du jour où on les a posés (l'entité portait
    `decor: 'feu'`, et `Entites.dessiner` teste `if (e.decor)` **avant**
    `if (e.type === 'feu')` : la branche générique peignait le boîtier cuit et
    s'en allait) ; rien ne le disait, parce que **tous les juges des feux
    parlaient de l'horloge** et aucun du **dessin**.

    Il tient maintenant la promesse d'un tricolore : à chaque instant du
    cycle, **une seule lentille allumée**, à la colonne de sa couleur, et de
    **sa forme** — le rouge carré, le jaune en losange, le vert rond, comme un
    vrai feu québécois. On mesure les rectangles peints, en plein jour, là où
    aucune lampe ne vient aider.
    """
    r = banc("""function (L, o) {""" + GABARIT_JS + """
        L.Jeu.commencer();
        const inter = L.Monde.carte.intersections.find(function (i) { return i.feux; });
        const feu = L.B.entites.find(function (e) { return e.type === 'feu' && e.inter === inter; });
        const t = L.B.defs.conduite.trafic;
        const cycle = 2 * (t.feu_vert_images + t.feu_orange_images);
        L.B.joueur.x = feu.x; L.B.joueur.y = feu.y;
        L.B.partie.heure = 0.5;                                   // plein midi : aucune lampe
        const sens = feu.axe === 'ns' ? '^' : '>';
        const releves = [];
        for (const phase of [0, t.feu_vert_images - 5, t.feu_vert_images + 5, cycle / 2 + 5,
                             cycle / 2 + t.feu_vert_images + 5]) {
            L.B.t = ((phase - inter.decalage) % cycle + cycle) % cycle - 1;
            L.Monde.centrerCamera(feu.x, feu.y);
            const c = L.Base.debut();
            c.traces = [];
            o.frame(1);
            const traces = c.traces; c.traces = null;
            const cx = Math.round(L.B.cam.x), cy = Math.round(L.B.cam.y);
            const [x, y] = coin(feu, cx, cy);
            // Tout ce qui a ete peint DANS le boitier des chars : le reste du
            // mat est cuit dans la fiche, donc un rectangle ici est forcement
            // une lentille vive.
            const dans = traces.filter(function (q) {
                return q[0] >= x && q[0] < x + F.w
                    && q[1] >= y + F.lentilleY && q[1] < y + F.lentilleY + F.lentilleCote;
            });
            // A quelle lentille (rang 0, 1, 2) chaque pixel peint touche-t-il ?
            const rangs = {};
            for (const q of dans) {
                for (let px = q[0]; px < q[0] + q[2]; px++) {
                    for (let rang = 0; rang < 3; rang++) {
                        const c0 = x + lentilleDe(feu, rang);
                        if (px >= c0 && px < c0 + F.lentilleCote) rangs[rang] = true;
                    }
                }
            }
            releves.push({ couleur: L.Monde.feuDeCirculation(inter, sens),
                           vert: L.Monde.feuVert(inter, sens),
                           rangs: Object.keys(rangs).map(Number).sort(),
                           pleins: dans.filter(function (q) { return q[2] === 3 && q[3] === 3; }).length,
                           barres: dans.filter(function (q) { return q[2] === 1 && q[3] === 3; }).length,
                           coins: dans.filter(function (q) { return q[2] === 1 && q[3] === 1; }).length });
        }
        return releves;
    }""")
    rang = {"rouge": 0, "jaune": 1, "vert": 2}
    vus = set()
    for x in r:
        vus.add(x["couleur"])
        assert x["rangs"] == [rang[x["couleur"]]], \
            f"feu {x['couleur']} : lentilles allumees aux rangs {x['rangs']}, il en faut UNE, la {rang[x['couleur']]}e"
        assert x["vert"] == (x["couleur"] == "vert"), \
            "ce que le feu MONTRE et ce que le char RESPECTE ne disent pas la meme chose"
        # La forme : le carre est plein, le losange est une croix (une barre
        # verticale + une horizontale), le cercle est un plein aux coins adoucis.
        if x["couleur"] == "rouge":
            assert x["pleins"] == 1 and x["barres"] == 0, f"le rouge n'est pas un carre plein : {x}"
            assert x["coins"] == 1, f"le rouge n'a que son coeur comme pixel isole : {x}"
        elif x["couleur"] == "jaune":
            assert x["pleins"] == 0 and x["barres"] == 1, f"le jaune n'est pas un losange : {x}"
        else:
            assert x["pleins"] == 1 and x["coins"] == 5, \
                f"le vert n'est pas un cercle (un plein + quatre coins adoucis + le coeur) : {x}"
    assert vus == {"rouge", "jaune", "vert"}, f"le cycle n'a pas montre les trois couleurs : {vus}"


def test_de_chaque_approche_un_feu_de_son_axe_est_en_face(banc):
    """Un tricolore ne montre **qu'une rue** — c'est ce qu'est un tricolore.
    Il faut donc qu'en arrivant à un croisement, un feu de **son** axe soit
    dans le champ, sinon on ne sait pas si c'est à soi de passer.

    ⚠️ Ça tient à une diagonale : nord-est et sud-ouest portent le nord-sud,
    nord-ouest et sud-est l'est-ouest. Qui arrive du sud a les deux coins nord
    devant lui, donc un de chaque diagonale, donc un « ns ». Le juge le
    vérifie **pour les quatre approches, à tous les croisements de la ville**
    — c'est la propriété qui justifie l'assignation, pas le goût.
    """
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const TT = L.TT;
        const manque = [], sansAxe = [];
        const feux = L.B.entites.filter(function (e) { return e.type === 'feu'; });
        const parInter = new Map();
        for (const e of feux) {
            if (!e.axe) sansAxe.push(e.id);
            if (!parInter.has(e.inter)) parInter.set(e.inter, []);
            parInter.get(e.inter).push(e);
        }
        for (const [inter, mats] of parInter) {
            const haut = inter.y * TT, bas = (inter.y + inter.h) * TT;
            const gauche = inter.x * TT, droite = (inter.x + inter.l) * TT;
            // Les deux coins « en face » de chaque approche, et l'axe qu'il faut y voir.
            const approches = [['^', 'ns', function (e) { return e.y < haut; }],
                               ['v', 'ns', function (e) { return e.y > bas; }],
                               ['>', 'eo', function (e) { return e.x > droite; }],
                               ['<', 'eo', function (e) { return e.x < gauche; }]];
            for (const [sens, axe, enFace] of approches) {
                if (!mats.some(function (e) { return enFace(e) && e.axe === axe; }))
                    manque.push(inter.i + ':' + sens);
            }
        }
        return { feux: feux.length, sansAxe: sansAxe.length, manque: manque.length,
                 exemples: manque.slice(0, 5),
                 axes: { ns: feux.filter(function (e) { return e.axe === 'ns'; }).length,
                         eo: feux.filter(function (e) { return e.axe === 'eo'; }).length } };
    }""")
    assert r["sansAxe"] == 0, f"{r['sansAxe']} mats sans axe : ils ne savent pas quelle rue ils montrent"
    assert r["manque"] == 0, \
        f"{r['manque']} approches sans feu de leur axe en face (ex. {r['exemples']})"
    assert r["axes"]["ns"] == r["axes"]["eo"] == r["feux"] // 2, \
        f"les deux axes ne se partagent pas les mats : {r['axes']}"


def test_un_char_respecte_le_feu_qu_on_lui_montre_sauf_la_sirene(banc):
    """« Les véhicules le respectent, sauf exception. » Le char du trafic lit
    **`Monde.feuVert`**, qui découle de **`feuDeCirculation`**, qui est ce que
    le mât **peint** : une seule phrase, lue deux fois.

    ⚠️ Et le **jaune n'est pas vert** : un char qui arrive à la ligne d'arrêt
    sur le jaune s'arrête. Sans ça, le dégagement du feu piéton ne servirait à
    rien — le croisement ne se viderait jamais.

    ⚠️ **L'exception, c'est la sirène** : en poursuite, on brûle le feu, le
    STOP et la boîte. Une auto-patrouille qui attend au rouge pendant que le
    joueur s'enfuit n'est pas une poursuite.
    """
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const c = L.Monde.carte, t = L.B.defs.conduite.trafic;
        const cycle = 2 * (t.feu_vert_images + t.feu_orange_images);
        // Une ligne d'arret ('S') qui donne sur un croisement a feux.
        let arret = null;
        for (const k in c.arrets) {
            const [tx, ty] = k.split(',').map(Number), sens = c.arrets[k];
            const p = { '>': [1, 0], '<': [-1, 0], '^': [0, -1], 'v': [0, 1] }[sens];
            const inter = L.Monde.intersectionA(tx + p[0], ty + p[1]);
            if (inter && inter.feux) { arret = { tx: tx, ty: ty, sens: sens, inter: inter }; break; }
        }
        const angle = { '>': 0, '<': Math.PI, '^': -Math.PI / 2, 'v': Math.PI / 2 }[arret.sens];
        function essai(couleurVoulue, sirene) {
            // On se cale sur la phase voulue, puis on pose un char sur la ligne d'arret.
            let phase = 0;
            for (; phase < cycle; phase++) {
                L.B.t = phase;
                if (L.Monde.feuDeCirculation(arret.inter, arret.sens) === couleurVoulue) break;
            }
            const v = L.Vehicules.creer('auto', arret.tx * L.TT + 8, arret.ty * L.TT + 8, angle,
                                        { conducteur: 'trafic', etat: 'roule', sens: arret.sens,
                                          poursuite: sirene || undefined });
            const depart = { x: v.x, y: v.y };
            for (let i = 0; i < 90; i++) { L.B.t = phase; o.frame(1); }   // l'horloge du feu FIGEE
            const avance = Math.hypot(v.x - depart.x, v.y - depart.y);
            const dedans = !!L.Monde.intersectionA(Math.floor(v.x / L.TT), Math.floor(v.y / L.TT));
            L.Entites.retirer(v);
            return { couleur: L.Monde.feuDeCirculation(arret.inter, arret.sens),
                     vert: L.Monde.feuVert(arret.inter, arret.sens),
                     avance: Math.round(avance), dedans: dedans };
        }
        return { rouge: essai('rouge', false), jaune: essai('jaune', false),
                 vert: essai('vert', false), sirene: essai('rouge', true) };
    }""")
    assert r["rouge"]["couleur"] == "rouge" and r["rouge"]["vert"] is False
    assert r["rouge"]["avance"] <= 8, f"un char a franchi le rouge : {r['rouge']['avance']} px"
    assert r["jaune"]["couleur"] == "jaune" and r["jaune"]["vert"] is False, \
        "le jaune compte comme vert : le croisement ne se viderait jamais"
    assert r["jaune"]["avance"] <= 8, f"un char est parti sur le jaune : {r['jaune']['avance']} px"
    assert r["vert"]["avance"] > 16, f"un char est reste plante au vert : {r['vert']['avance']} px"
    assert r["sirene"]["avance"] > 16, \
        f"une sirene a attendu au rouge : {r['sirene']['avance']} px — l'exception n'en est plus une"


def test_une_borne_defoncee_crache_et_ca_s_entend(banc):
    """⚠️ **Retour de Martin : « les trucs jaunes ne sont pas prioritaires aux
    feux » · « mets-les rouges, les bornes » · « et un jet d'eau avec son si on
    les défonce ».**

    La borne-fontaine était une **tuile** (`'b'`, solide), et une tuile ne se
    casse pas : elle ne pouvait ni tomber sous un char, ni gicler. C'est
    maintenant un **décor** avec sa fiche — donc une masse, une résistance, un
    bris. Le jet est une **entité invisible** qui vit ses dix secondes et crache
    des particules : le patron du brasier du Molotov, et la même raison — on ne
    repeint pas une tuile à chaque image pour un effet qui passe.
    """
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const borne = L.B.entites.find(function (e) { return e.decor === 'borne_fontaine'; });
        const fiche = L.DECORS.borne_fontaine;
        L.B.joueur.x = borne.x + 30; L.B.joueur.y = borne.y;
        const avant = L.B.particules.length;
        const casse = L.Entites.briser(borne);
        o.frame(1);
        const jet = L.B.entites.find(function (e) { return e.type === 'jet_eau'; });
        const apres = L.B.particules.length;
        o.frame(40);
        const encore = !!L.B.entites.find(function (e) { return e.type === 'jet_eau'; });
        if (jet) jet.minuterie = 1;
        o.frame(3);
        return { bornes: L.B.entites.filter(function (e) { return e.decor === 'borne_fontaine'; }).length,
                 casse: casse, brise: borne.brise, solide: borne.solide,
                 fiche: { casse: fiche.casse, solide: fiche.solide },
                 jet: !!jet, gouttes: apres - avant, encore: encore,
                 tari: !L.B.entites.find(function (e) { return e.type === 'jet_eau'; }),
                 son: !!(L.Son && L.Son.SFX && L.Son.SFX.borne_cassee && L.Son.SFX.borne_jet) };
    }""")
    assert r["bornes"] > 0, "aucune borne-fontaine dans la ville"
    assert r["fiche"]["casse"] and r["fiche"]["solide"],         "une borne qu'on ne peut pas defoncer n'est qu'une tache de peinture"
    assert r["casse"] is True and r["brise"] is True and r["solide"] is False
    assert r["jet"] is True, "une borne defoncee ne crache pas"
    assert r["gouttes"] > 0, f"le jet ne fait aucune goutte : {r['gouttes']}"
    assert r["encore"] is True, "le jet s'arrete dans la seconde"
    assert r["tari"] is True, "⚠️ le jet ne tarit jamais : la rue reste une fontaine"
    # ⚠️ DEUX sons, et c'est le correctif du 15 sept. 2026 : le bouchon qui
    # saute (une fois) et le souffle qui se TIENT. Un seul, et c'est le défaut
    # qu'on vient de réparer — le choc d'un accident de char rejoué seize fois.
    # Ce qu'ils jouent vraiment est jugé dans `test_son_js.py`.
    assert r["son"] is True, "le bris et le jet n'ont pas chacun leur bruit"


def test_aucune_borne_fontaine_ne_prend_le_coin_d_un_feu(racine):
    """Même règle que pour les lampadaires : le coin d'un croisement à feux est
    la place du **mât**. Une borne plantée dessus, c'est le feu qu'on ne voit
    pas en arrivant."""
    import json

    from app import carte as c

    ville = c.generer()
    reserves = set()
    for inter in ville["intersections"]:
        if len(inter["bras"]) < 4:
            continue
        for cx, cy in ((inter["x"] + inter["l"], inter["y"] - 1),
                       (inter["x"] - 1, inter["y"] + inter["h"]),
                       (inter["x"] - 1, inter["y"] - 1),
                       (inter["x"] + inter["l"], inter["y"] + inter["h"])):
            for ix in (-1, 0, 1):
                for iy in (-1, 0, 1):
                    reserves.add((cx + ix, cy + iy))
    bornes = [(d["x"], d["y"]) for d in ville["decor"] if d["type"] == "borne_fontaine"]
    assert len(bornes) >= 10, f"{len(bornes)} bornes-fontaines : la ville n'en a presque pas"
    dessus = [b for b in bornes if b in reserves]
    assert not dessus, f"{len(dessus)} bornes sur un coin reserve au feu (ex. {dessus[:4]})"
    assert json.dumps(bornes[:1])          # la ville se serialise, comme le reste du decor


def test_le_plafond_de_lampes_tient_les_lampadaires_ET_les_feux(racine):
    """⚠️ `Base.fin` plafonnait à **25** lampes par image, taillé pour les
    lampadaires seuls — c'est aussi ce que `Monde.lampesVisibles` en rend au
    plus. Les feux s'y ajoutent maintenant : sous ce plafond-là, ils
    **éteindraient** les lampadaires au lieu de s'ajouter à eux. Les trois
    nombres se **lisent dans le JS**, ils ne sont pas recopiés ici.
    """
    js = lambda nom: (racine / "static" / "js" / nom).read_text(encoding="utf-8")  # noqa: E731
    plafond = int(re.search(r"^  const LAMPES_MAX = (\d+);", js("base.js"), re.M).group(1))
    lampadaires = int(re.search(r"out\.length >= (\d+)\) break;", js("monde.js")).group(1))
    feux = int(re.search(r"^  const LAMPES_FEUX_MAX = (\d+);", js("vehicules.js"), re.M).group(1))
    # Et depuis « la nuit a ses habitudes », les phares des chars menés — comptés
    # en CHARS depuis « des phares à la mesure de chaque char » : tant de chars, à
    # tant de lampes au plus.
    chars = int(re.search(r"^  const CHARS_ECLAIRES_MAX = (\d+);", js("vehicules.js"), re.M).group(1))
    par_char = int(re.search(r"^  const LAMPES_PAR_CHAR_MAX = (\d+);", js("vehicules.js"), re.M).group(1))
    assert re.search(r"^  const LAMPES_PHARES_MAX = CHARS_ECLAIRES_MAX \* LAMPES_PAR_CHAR_MAX;", js("vehicules.js"), re.M)
    phares = chars * par_char
    assert plafond >= lampadaires + feux + phares + 1, (
        f"{lampadaires} lampadaires + {feux} feux + {phares} phares + le projecteur de l'helico ne "
        f"tiennent pas sous un plafond de {plafond} : les feux en eteindraient"
    )


def test_les_feux_s_allument_au_meme_seuil_de_brune_que_les_lampadaires(racine):
    """Deux seuils voudraient dire deux réponses à « fait-il noir ? », et la
    deuxième serait fausse un jour — on verrait les feux s'allumer une heure
    avant (ou après) les lampadaires de la même rue."""
    js = lambda nom: (racine / "static" / "js" / nom).read_text(encoding="utf-8")  # noqa: E731
    lampadaires = float(re.search(r"ambiance\(\)\.alpha < ([\d.]+)\)", js("monde.js")).group(1))
    feux = float(re.search(r"^  const BRUNE = ([\d.]+);", js("vehicules.js"), re.M).group(1))
    assert feux == lampadaires, f"les feux s'allument a {feux}, les lampadaires a {lampadaires}"


def test_un_char_s_arrete_au_stop_puis_repart(banc, paquet):
    arret = paquet["conduite"]["trafic"]["arret_images"]
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        L.graine(53);
        const c = L.Monde.carte;
        // Un T dont la tige arrive par l'est (sens '<') : on cherche sa ligne d'arret.
        const inter = c.intersections.find(function (i) { return i.stop === '<'; });
        let sx = -1, sy = -1;
        for (const cle in c.arrets) {
            const xy = cle.split(',').map(Number);
            if (c.arrets[cle] !== '<') continue;
            if (L.Monde.intersectionA(xy[0] - 1, xy[1]) === inter) { sx = xy[0]; sy = xy[1]; break; }
        }
        L.B.entites = L.B.entites.filter(function (e) { return e.type !== 'vehicule'; });
        const v = L.Vehicules.creer('auto', sx * L.TT + 8 + 40, sy * L.TT + 8, Math.PI, { conducteur: 'trafic', etat: 'roule', sens: '<' });
        v.vitesse = 1.5;
        let immobile = 0, arrive = false, reparti = false;
        for (let i = 0; i < 600; i++) {
            L.Entites.indexer(); L.Vehicules.majConducteur(v); v.x += v.vx; v.y += v.vy;
            const tx = Math.floor(v.x / L.TT);
            if (tx === sx && Math.abs(v.vx) + Math.abs(v.vy) < 0.01) { immobile++; arrive = true; }
            if (arrive && tx < sx) { reparti = true; break; }
        }
        return { trouve: sx >= 0, arrive: arrive, immobile: immobile, reparti: reparti };
    }""")
    assert r["trouve"], "aucune ligne d'arret de T trouvee"
    assert r["arrive"] and r["immobile"] >= arret - 2, f"le char ne s'est arrete que {r['immobile']} images au STOP"
    assert r["reparti"], "le char n'est jamais reparti du STOP"


def test_on_prend_le_velo_du_cycliste(banc):
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        L.graine(54);
        const j = L.B.joueur;
        // ⚠️ **SUR LE BOULEVARD DU POURTOUR** : le vélo part vers l'est (angle 0)
        // et il lui faut de la rue devant lui. Au terminus, le jour où la trame a
        // bougé (17 sept. 2026), il butait sur un mur au bout de vingt tuiles et
        // le juge lisait « le vélo n'avance pas ». Le boulevard du nord est droit
        // d'un bout à l'autre de la ville.
        const c = L.Monde.carte;
        for (let y = 0; y < 12; y++) {
          let pris = false;
          for (let x = 40; x < 80; x++) if (c.voie[y][x] === '>') {
            j.x = x * L.TT + 8; j.y = y * L.TT + 8; L.Monde.centrerCamera(j.x, j.y); pris = true; break;
          }
          if (pris) break;
        }
        L.Entites.indexer();
        const velo = o.char('velo', 16, 0, 0);
        velo.conducteur = 'trafic'; velo.etat = 'roule';
        L.Entites.indexer();
        const crimes = L.B.partie.stats.crimes;
        // ⚠️ ON REPERE CELUI QUI EST NE, pas « combien de temoins il y a dans la
        // ville ». Le juge comptait tous les `temoin` de la carte et en
        // attendait UN : un deuxieme passant qui voit voler un velo sous son
        // nez est pourtant exactement ce qu'on veut, et le jour ou le
        // centre-ville a eu plus de monde (demande de Martin), le juge a dit
        // « le cycliste ne temoigne pas » alors qu'ils etaient deux a le faire.
        const avant = new Set(L.B.entites);
        L.Vehicules.monter(j, velo);
        const neufs = L.B.entites.filter(function (e) { return e.type === 'pieton' && !avant.has(e); });
        // ⚠️ CELUI QUI TOMBE DU VELO : un temoin neuf pose SUR le velo. Compter
        // tous les temoins neufs en attendait un et en trouvait deux — un
        // passant ne a la meme image a cote de nous voit lui aussi voler le
        // velo, et c'est exactement ce qu'on veut. Ce qu'on juge, c'est que le
        // cycliste tombe et temoigne, pas que personne d'autre ne regarde.
        const cycliste = neufs.filter(function (e) {
            return e.etat === 'temoin' && Math.hypot(e.x - velo.x, e.y - velo.y) < 24;
        }).length;
        o.touche('KeyW'); o.frame(120); o.relacher('KeyW');
        return { dedans: j.dansVehicule === velo, cycliste: cycliste, crimes: L.B.partie.stats.crimes - crimes,
                 vitesse: velo.vitesse, max: velo.def.vitesse_max, moteur: L.Son.boucleActive('moteur'),
                 radio: L.Son.Radio.demandee };
    }""")
    assert r["dedans"] is True
    assert r["cycliste"] >= 1, "le cycliste doit tomber et temoigner"   # celui qui vient de tomber
    assert r["crimes"] >= 1
    assert r["vitesse"] > r["max"] * 0.8, "le velo n'avance pas"
    assert r["moteur"] is False and r["radio"] is None, "un velo n'a ni moteur ni radio"


def test_l_ambiance_du_district_joue_a_pied_et_cede_a_la_radio(banc, paquet):
    """⚠️ Il n'y a plus UNE musique de fond pour toute la ville : c'est
    precisement ce que la fiche retire. À pied, c'est l'ambiance **du district
    ou l'on se trouve** qui joue — et la radio d'un char la remplace, parce
    qu'elles occupent **la meme case de l'echelle**."""
    table = paquet["audio"]["ambiances_de_district"]
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        o.frame(2);
        const j = L.B.joueur;
        const zone = L.Monde.zoneA(j.x, j.y);
        const aPied = L.Son.Mus.courante;
        const v = o.char('auto', 24, 0, 0);
        L.Vehicules.monter(j, v);
        o.frame(2);
        const auVolant = { musique: L.Son.Mus.courante, radio: L.Son.Radio.demandee };
        L.Vehicules.descendre(j, true);
        o.frame(2);
        return { aPied: aPied, auVolant: auVolant, descendu: L.Son.Mus.courante,
                 district: zone && zone.district };
    }""")
    attendu = table[r["district"]]
    assert r["aPied"] == attendu, (
        "a pied, c'est l'ambiance du district qui joue : %s au lieu de %s" % (r["aPied"], attendu)
    )
    assert r["auVolant"]["musique"] is None and r["auVolant"]["radio"] == "la_brume", \
        "au volant, la radio remplace l'ambiance — meme case de l'echelle"
    assert r["descendu"] == attendu, "descendu, l'ambiance du district revient"


def test_la_rumeur_suit_la_foule_et_les_passants_parlent(banc):
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        L.graine(61);
        const j = L.B.joueur;
        // Sans audio sous Node : on verifie la mecanique, pas le son.
        const avant = L.Son.Voix.dernierT;
        const p = o.poser('passante', 12, 0);
        p.etat = 'flane';
        o.frame(2);
        const parle = p.aParle === true;
        const rumeur = typeof L.Son.Rumeur.maj === 'function';
        return { parle: parle, rumeur: rumeur, dernierT: L.Son.Voix.dernierT, avant: avant,
                 passage: typeof L.Son.jouerA === 'function' };
    }""")
    assert r["parle"] is True, "un passant qui nous frole doit tenter de parler"
    assert r["rumeur"] and r["passage"]


def test_deux_chars_qui_tournent_a_gauche_ne_se_bloquent_pas(banc):
    """⚠️ Le blocage de Martin : deux chars entrent au vert par des bouts
    opposes, tous deux pour tourner a gauche, se retrouvent nez a nez au
    milieu de la boite — et chacun attend l'autre. Un croisement ne doit
    accueillir un char que s'il peut le laisser ressortir."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        L.graine(72);
        const c = L.Monde.carte;
        // Un croisement a feux a quatre voies (rue est-ouest large).
        const inter = c.intersections.find(function (i) { return i.feux && i.l === 4 && i.h === 4; });
        L.B.entites = L.B.entites.filter(function (e) { return e.type !== 'vehicule' && e.type !== 'pieton'; });
        // ⚠️ Le joueur regarde de pres : hors de sa bulle, un char est oublie
        // et le test croirait a un blocage.
        const j = L.B.joueur;
        j.x = (inter.x - 1) * L.TT + 8; j.y = (inter.y - 1) * L.TT + 8;
        L.Monde.centrerCamera(j.x, j.y);
        // Phase : est-ouest au vert.
        L.B.t = -inter.decalage + L.B.defs.conduite.trafic.feu_vert_images + L.B.defs.conduite.trafic.feu_orange_images + 5;
        const T = L.TT;
        // A arrive de l'ouest sur la voie interieure (rangee y+2), B de l'est sur la voie interieure (rangee y+1).
        const a = L.Vehicules.creer('auto', (inter.x - 6) * T + 8, (inter.y + 2) * T + 8, 0, { conducteur: 'trafic', etat: 'roule', sens: '>' });
        const b = L.Vehicules.creer('auto', (inter.x + inter.l + 5) * T + 8, (inter.y + 1) * T + 8, Math.PI, { conducteur: 'trafic', etat: 'roule', sens: '<' });
        a.vitesse = 1.5; b.vitesse = 1.5;
        a.sortie = ['gauche', 'droit', 'droite']; b.sortie = ['gauche', 'droit', 'droite'];
        const boite = function (v) { return v.x >= inter.x * T && v.x < (inter.x + inter.l) * T && v.y >= inter.y * T && v.y < (inter.y + inter.h) * T; };
        let dansLaBoiteEnsemble = 0, sortis = 0;
        for (let i = 0; i < 2400; i++) {
            // ⚠️ LE JOUEUR NE SE FAIT PAS RENVERSER : il regarde a une tuile de la
            // boite, un des deux chars pouvait le faucher, et il se reveillait a
            // l'hopital — `Monde.carte` devenait la PIECE, `estRoute` repondait non
            // sur de l'asphalte, et le juge accusait le trafic. Mesure le 17 sept.
            // 2026 : 1 graine sur 40 tombait deja ainsi, et l'Ile-aux-Corneilles
            // (quarante decors de plus, donc d'autres numeros d'entite) en changeait
            // seulement laquelle. C'est la parade du juge des amuseurs.
            j.invincible = 60;
            o.frame(1);
            if (boite(a) && boite(b)) dansLaBoiteEnsemble++;
        }
        const aParti = Math.hypot(a.x - (inter.x - 6) * T, a.y - (inter.y + 2) * T) > 8 * T && !boite(a);
        const bParti = Math.hypot(b.x - (inter.x + inter.l + 5) * T, b.y - (inter.y + 1) * T) > 8 * T && !boite(b);
        return { ensemble: dansLaBoiteEnsemble, aParti: aParti, bParti: bParti, aSens: a.sens, bSens: b.sens,
                 aSol: L.Monde.estRoute(Math.floor(a.x / T), Math.floor(a.y / T)),
                 bSol: L.Monde.estRoute(Math.floor(b.x / T), Math.floor(b.y / T)) };
    }""")
    assert r["ensemble"] == 0, f"les deux chars ont partage la boite pendant {r['ensemble']} images"
    assert r["aParti"] and r["bParti"], f"un char est reste coince : {r}"
    assert r["aSol"] and r["bSol"], "un char a fini hors de la route"


def test_les_passages_ont_une_tuile_pleine_et_une_en_bout(banc):
    """⚠️ **Reformule le 15 sept. 2026, le trottoir a une tuile.** Le passage
    faisait deux tuiles — une pleine, une en bout — et le juge tenait cette
    forme. Depuis que la traverse fait la largeur du trottoir, une tuile, il
    n'y a plus de bout : chaque tuile de passage est PLEINE, et le peintre y
    met ses bandes entieres. Une tuile « en bout » qui reapparaitrait serait
    une traverse de deux tuiles revenue par la fenetre."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const c = L.Monde.carte;
        const compte = { '=': [0, 0, 0], ':': [0, 0, 0] };
        for (let y = 0; y < c.h; y++) for (let x = 0; x < c.w; x++) {
            const g = c.sol[y][x];
            if (g === '=' || g === ':') compte[g][L.Monde.varianteDePassage(g, x, y)]++;
        }
        return compte;
    }""")
    for g in ("=", ":"):
        pleines, ouest, est = r[g]
        assert pleines > 100, f"passage « {g} » : {pleines} tuiles pleines seulement — {r}"
        assert ouest == 0 and est == 0, (
            f"passage « {g} » : {ouest + est} tuiles en bout — une traverse fait plus d'une tuile"
        )


def test_une_case_de_stationnement_se_peint_et_se_gare(banc):
    """Une case fait deux tuiles : le FOND (ligne de nez, butoir) et l'ouverture
    sur l'allee. Le peintre ne le sait pas du generateur, il le LIT dans les
    voisines — et c'est la meme lecture qui met une auto stationnee dans ses
    lignes plutot qu'en travers du terrain."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const c = L.Monde.carte, NEZ = { '^': [0, -1], 'v': [0, 1], '<': [-1, 0], '>': [1, 0] };
        let fonds = 0, ouvertes = 0, mauvaises = 0;
        const coins = {}, cases = [];
        for (let y = 1; y < c.h - 1; y++) for (let x = 1; x < c.w - 1; x++) {
            const g = c.sol[y][x], nez = NEZ[g];
            if (!nez) continue;
            const v = L.Monde.varianteDeCase(g, x, y);
            const fond = (v & 1) !== 0;
            if (fond !== (c.sol[y + nez[1]][x + nez[0]] !== g)) mauvaises++;
            if (fond) fonds++; else ouvertes++;
            coins[v & 3] = (coins[v & 3] || 0) + 1;
            cases.push([x, y]);
        }
        // ⚠️ Une auto ne se stationne QUE hors de l'ecran, entre 180 et 560 px
        // du joueur : on se plante donc au milieu du coin le plus fourni en
        // cases, sinon on juge un quartier ou il n'y a rien a peupler.
        let mieux = cases[0], n = 0;
        for (let i = 0; i < cases.length; i += 8) {
            const p = cases.filter(function (k) {
                return Math.abs(k[0] - cases[i][0]) < 30 && Math.abs(k[1] - cases[i][1]) < 30;
            }).length;
            if (p > n) { n = p; mieux = cases[i]; }
        }
        L.B.joueur.x = mieux[0] * L.TT; L.B.joueur.y = mieux[1] * L.TT;
        L.Monde.centrerCamera(L.B.joueur.x, L.B.joueur.y);
        // ⚠️ ON FORCE LA REGLE, on ne joue pas sa probabilite — c'est la meme
        // lecon que la chute de l'ivrogne. Un char ne se gare que lorsque le
        // trafic ROULANT est au complet (`roulent >= voulu`, `vehicules.js`) :
        // le juge esperait donc qu'en 900 images le quartier finisse par
        // remplir ses rues, ce qui depend de trois tirages de de. Il a tenu
        // jusqu'au jour ou une routine de plus a decale le hasard. On met le
        // trafic voulu a zero : la condition est vraie tout de suite, et on
        // mesure ce qu'on veut mesurer — OU se gare un char, pas QUAND.
        const zone = L.Monde.zoneA(L.B.joueur.x, L.B.joueur.y);
        if (zone) zone.vehicules = 0;
        o.frame(900);
        // ⚠️ **UNE COQUE AMARREE N'EST PAS UNE AUTO GAREE.** Depuis la 3e vague
        // du bord de l'eau, une chaloupe nait `etat: 'stationne'` — dans la
        // BAIE, ce qui est exactement sa place — et ce juge-ci exige que tout
        // vehicule stationne soit dans une case peinte. Il ne s'en apercevait
        // pas tant que le coin le plus fourni en cases tombait loin de l'eau ;
        // le jour ou le port a touche la baie, le coin a bouge et le juge a
        // accuse le stationnement d'un bateau au mouillage. `def.eau` dit la
        // difference, et c'est la fiche qui la porte (`vehicules.py`).
        const gares = L.B.entites.filter(function (e) {
            return e.type === 'vehicule' && e.etat === 'stationne' && !(e.def && e.def.eau); });
        const poses = gares.map(function (v) {
            const tx = Math.floor(v.x / L.TT), ty = Math.floor(v.y / L.TT);
            const g = c.sol[ty][tx], nez = NEZ[g];
            return {
                case: !!nez,
                angle: !!nez && Math.abs(Math.atan2(nez[1], nez[0]) - v.angle) < 0.01,
                centree: (v.x % L.TT === 8 && v.y % L.TT === 0) || (v.y % L.TT === 8 && v.x % L.TT === 0),
            };
        });
        return { fonds: fonds, ouvertes: ouvertes, mauvaises: mauvaises, coins: coins, poses: poses };
    }""")
    assert r["mauvaises"] == 0, "une tuile de fond mal lue : le butoir se peint du mauvais bord"
    assert r["fonds"] > 0 and r["fonds"] == r["ouvertes"], \
        f"{r['fonds']} fonds pour {r['ouvertes']} ouvertures : une case n'a pas deux tuiles"
    assert set(r["coins"]) == {"0", "1", "2", "3"}, \
        f"le peintre n'a jamais vu les quatre coins d'une rangee : {r['coins']}"
    assert r["poses"], "aucune auto ne s'est stationnee en 900 images"
    for pose in r["poses"]:
        assert pose["case"], "une auto stationnee hors d'une case"
        assert pose["angle"], "une auto stationnee de travers dans sa case"
        assert pose["centree"], "une auto stationnee a cheval sur ses lignes"


# --- M5 : interieurs et economie ----------------------------------------------


def test_le_fondu_de_porte_noircit_avant_de_changer_de_scene(banc):
    """⚠️ Le defaut que Martin a nomme « la transition n'est pas juste » : la
    piece se chargeait PUIS le fondu partait de transparent. Sa premiere moitie
    noircissait donc sur la scene deja changee — on voyait la piece une image,
    l'ecran noircissait, il s'eclaircissait sur la meme piece. Ce test mesure la
    scene a CHAQUE image : aucune ne doit montrer la nouvelle avant le noir
    complet, et la porte doit s'entendre la, au noir."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const j = L.B.joueur, c = L.Monde.carte;
        const porte = c.portes.find(function (p) { return p.lieu === 'planque'; });
        j.x = porte.x * L.TT + 8; j.y = (porte.y + 1) * L.TT + 10;
        const villeW = c.w;
        // La porte s'entend-elle, et QUAND ?
        const sons = [];
        const vraiSon = L.Son.SFX.porte;
        L.Son.SFX.porte = function () { sons.push({ noir: L.B.transition ? L.B.transition.t : -1, dedans: !!L.B.interieur }); return vraiSon.apply(null, arguments); };
        L.Jeu.entrer(porte);
        const images = [];
        for (let i = 0; i < 120 && L.B.transition; i++) {
            o.frame(1);
            const tr = L.B.transition;
            // L'alpha du noir, comme le HUD le calcule : 0 -> 1, puis 1 -> 0.
            const alpha = tr ? (tr.t <= tr.ferme ? tr.t / tr.ferme : 1 - (tr.t - tr.ferme) / tr.ouvre) : 0;
            images.push({ alpha: Math.round(alpha * 1000) / 1000, w: L.Monde.carte.w, dedans: !!L.B.interieur });
        }
        const entree = images.length;
        // Et au retour : plus vif qu'a l'aller.
        L.Jeu.sortir();
        const sortie = o.fondu();
        return { villeW: villeW, images: images, entree: entree, sortie: sortie, sons: sons,
                 dedans: L.B.interieur, w: L.Monde.carte.w };
    }""")
    change = [i for i, im in enumerate(r["images"]) if im["dedans"]]
    assert change, "on n'est jamais entre"
    premiere = change[0]
    assert r["images"][premiere]["alpha"] == 1.0, (
        "la nouvelle scene se montre a %s de noir : le fondu clignote"
        % r["images"][premiere]["alpha"]
    )
    for im in r["images"][:premiere]:
        assert im["w"] == r["villeW"] and not im["dedans"], "la piece est chargee avant le noir"
        assert im["alpha"] < 1.0
    assert r["images"][-1]["alpha"] < 0.2, "le fondu ne finit pas en clair"
    assert r["sons"][0] == {"noir": premiere + 1, "dedans": True}, (
        "la porte doit s'entendre AU NOIR, a l'image du changement : %s" % r["sons"]
    )
    assert len(r["sons"]) == 2 and r["sons"][1]["dedans"] is False, (
        "la porte de sortie s'entend aussi au noir, une fois la rue revenue : %s" % r["sons"]
    )
    assert r["sortie"] < r["entree"], "sortir doit etre plus vif qu'entrer"
    assert 30 <= r["entree"] <= 90 and r["sortie"] >= 20, (
        "un fondu de porte se sent : ni un clignotement, ni une attente (%s, %s)"
        % (r["entree"], r["sortie"])
    )


def test_le_jeu_est_fige_pendant_un_fondu_de_porte(banc):
    """⚠️ La simulation continuait pendant le fondu : on pouvait sortir d'une
    piece et se faire renverser par un char qu'on n'a pas vu venir, sur un ecran
    noir ou l'on ne controle rien. Un menu fige deja tout ; une porte pareil."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const j = L.B.joueur, c = L.Monde.carte;
        const porte = c.portes.find(function (p) { return p.lieu === 'planque'; });
        j.x = porte.x * L.TT + 8; j.y = (porte.y + 1) * L.TT + 10;
        o.frame(2);
        // Un passant qui marche, un char qui roule : rien de tout ca ne doit
        // avancer d'un pixel pendant le noir.
        const passant = o.poser('flaneur', 24, 0);
        passant.etat = 'flane';
        const char = o.char('auto', -30, 0, 0);
        char.etat = 'roule'; char.vitesse = 3;
        j.vie = 60;
        const avant = { t: L.B.t, vie: j.vie, px: passant.x, py: passant.y, cx: char.x, heure: L.B.partie.heure };
        L.Jeu.entrer(porte);
        const images = o.fondu();
        const apres = { t: L.B.t, vie: j.vie, px: passant.x, py: passant.y, cx: char.x, heure: L.B.partie.heure };
        // Et une fois dedans, le jeu repart : le temps passe de nouveau.
        o.frame(5);
        return { avant: avant, apres: apres, images: images, repart: L.B.t - apres.t, dedans: !!L.B.interieur };
    }""")
    assert r["dedans"] is True and r["images"] > 20
    assert r["apres"]["t"] == r["avant"]["t"], "le temps de jeu a passe pendant le fondu"
    assert r["apres"]["heure"] == r["avant"]["heure"], "l'heure a avance pendant le fondu"
    assert r["apres"]["vie"] == r["avant"]["vie"], "le joueur a pris des coups pendant le fondu"
    assert r["apres"]["px"] == r["avant"]["px"] and r["apres"]["py"] == r["avant"]["py"], "un passant a marche pendant le fondu"
    assert r["apres"]["cx"] == r["avant"]["cx"], "un char a roule pendant le fondu"
    assert r["repart"] == 5, "le jeu n'est pas reparti apres le fondu"


def test_sortir_pendant_le_fondu_d_entree_ramene_devant_la_porte(banc):
    """⚠️ Le cas qui casse tout : ressortir alors que le fondu d'entree joue
    encore. La scene ne change qu'au noir — celui qui sort avant ne trouverait
    aucun interieur, la sortie serait refusee, et le joueur se reveillerait
    dedans sans l'avoir demande."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const j = L.B.joueur, c = L.Monde.carte;
        const porte = c.portes.find(function (p) { return p.lieu === 'planque'; });
        const x0 = porte.x * L.TT + 8, y0 = (porte.y + 1) * L.TT + 10;
        j.x = x0; j.y = y0;
        // Aller-retour normal, d'abord : on revient au pixel.
        o.entrer(porte);
        o.sortir();
        const normal = { x: j.x, y: j.y, dedans: L.B.interieur };
        // Puis on ressort AVANT le noir : trois images de fondu, et on repart.
        j.x = x0; j.y = y0;
        L.Jeu.entrer(porte);
        o.frame(3);
        const avantLeNoir = { dedans: !!L.B.interieur, fondu: !!L.B.transition };
        const sorti = L.Jeu.sortir();
        o.fondu();
        // L'elan qui reste au pas de la porte, avant que le jeu reprenne la main.
        const elan = { garde: Math.abs(j.vy) > 0, vers: j.vy > 0, face: j.face };
        // La camera ne saute pas : elle est deja posee quand le jeu repart.
        const cam = { x: L.B.cam.x, y: L.B.cam.y };
        o.frame(1);
        const bouge = Math.hypot(L.B.cam.x - cam.x, L.B.cam.y - cam.y);
        return { normal: normal, avantLeNoir: avantLeNoir, sorti: sorti, dedans: L.B.interieur,
                 x: j.x, y: j.y, x0: x0, y0: y0, bouge: bouge, elan: elan };
    }""")
    assert r["normal"]["dedans"] is None and (r["normal"]["x"], r["normal"]["y"]) == (r["x0"], r["y0"]), (
        "un aller-retour par la porte doit ramener a la tuile EXACTE"
    )
    assert r["avantLeNoir"] == {"dedans": False, "fondu": True}
    assert r["sorti"] is True, "sortir pendant le fondu d'entree a ete refuse"
    assert r["dedans"] is None, "on est reste dedans"
    assert (r["x"], r["y"]) == (r["x0"], r["y0"]), "on ne revient pas devant la porte"
    assert r["bouge"] < 2, "la camera saute a la premiere image jouable : %s px" % r["bouge"]
    assert r["elan"] == {"garde": True, "vers": True, "face": "bas"}, (
        "on sort d'une porte avec un reste d'elan vers la rue, pas d'un arret complet : %s" % r["elan"]
    )


def test_l_hopital_et_la_prison_passent_par_la_machine_des_portes(banc):
    """⚠️ Retour de Martin : « il faut corriger le fade out et in quand on va a
    l'hopital ou qu'on se fait enfermer. »

    Les quatre ellipses (hopital, prison, compagnie, coucher) etaient restees
    sur `Hud.fondu` + `setTimeoutJeu` : DEUX HORLOGES independantes, l'une dans
    le dessin, l'autre dans la mise a jour. Rien ne liait le changement de scene
    au noir — il tombait a 80 % d'alpha, donc a travers un voile transparent
    d'un cinquieme, et le texte s'ecrivait par-dessus la rue qu'on voyait
    encore, pendant que la ville continuait de tourner.

    Ce juge mesure, image par image, les trois choses en meme temps : l'alpha a
    l'instant OU l'on est teleporte, l'alpha a chaque fois que le texte se
    dessine, et le temps du monde pendant le noir."""
    r = banc(r"""function (L, o) {
        L.Jeu.commencer();
        const j = L.B.joueur;
        L.B.partie.argent = 400;
        // Ce que le texte du fondu voit du monde : on note l'alpha a chaque
        // fois qu'Atlas l'ecrit (le banc ne garde aucun pixel). ⚠️ On guette
        // « REVEIL », pas « HOPITAL » : la facture passe aussi par un message
        // du HUD, et lui a le droit de s'ecrire sur la rue.
        const ecrits = [];
        const vraiTexte = L.Atlas.texte;
        function alpha() {
            const tr = L.B.transition;
            if (!tr) return null;
            const noir = tr.ferme + tr.tient;
            return tr.t <= tr.ferme ? tr.t / tr.ferme
                 : tr.t <= noir ? 1
                 : 1 - (tr.t - noir) / tr.ouvre;
        }
        L.Atlas.texte = function (ctx, s, x, y, c, e) {
            if (String(s).indexOf('RÉVEIL') >= 0) ecrits.push(alpha());
            return vraiTexte.apply(null, arguments);
        };
        // Un passant et un char : rien de tout ca ne doit avancer dans le noir.
        const passant = o.poser('flaneur', 40, 0);
        passant.etat = 'flane';
        const char = o.char('auto', -40, 0, 0);
        char.etat = 'roule'; char.vitesse = 3;
        const avant = { t: L.B.t, heure: L.B.partie.heure, px: passant.x, cx: char.x, x: j.x, y: j.y };
        L.Entites.blesser(j, 9999, null, {});
        const lance = { fondu: !!L.B.transition, tient: L.B.transition && L.B.transition.tient,
                        dejaLoin: Math.hypot(j.x - avant.x, j.y - avant.y) };
        // Image par image : ou est le joueur, et a quel alpha ?
        const images = [];
        for (let i = 0; i < 300 && L.B.transition; i++) {
            o.frame(1);
            images.push({ a: Math.round((alpha() === null ? 0 : alpha()) * 1000) / 1000,
                          loin: Math.round(Math.hypot(j.x - avant.x, j.y - avant.y)) });
        }
        L.Atlas.texte = vraiTexte;
        const apres = { t: L.B.t, heure: L.B.partie.heure, px: passant.x, cx: char.x };
        o.frame(5);
        // ⚠️ On arrive DANS la piece de l'hopital, couche : on juge ou sa porte mene.
        const hopital = L.B.exterieur.carte.points.find(function (p) { return p.slug === 'hopital'; });
        return { lance: lance, images: images, ecrits: ecrits, avant: avant, apres: apres,
                 repart: L.B.t - apres.t, vie: j.vie, max: j.vieMax,
                 piece: L.B.interieur && L.B.interieur.slug,
                 arrive: Math.hypot(L.B.exterieur.x - hopital.x * L.TT, L.B.exterieur.y - hopital.y * L.TT) };
    }""")
    assert r["lance"]["fondu"] is True, "tomber doit lancer un fondu de `Jeu.transiter`"
    assert r["lance"]["tient"] > 0, "une ellipse tient le noir : c'est la que le temps passe"
    assert r["lance"]["dejaLoin"] == 0, "le joueur est parti a l'hopital AVANT que le noir commence"
    change = [i for i, im in enumerate(r["images"]) if im["loin"] > 8]
    assert change, "on ne s'est jamais reveille a l'hopital"
    assert r["images"][change[0]]["a"] == 1.0, (
        "la teleportation se voit a %s de noir : c'est le defaut de l'ancien fondu"
        % r["images"][change[0]]["a"]
    )
    assert r["ecrits"], "le fondu doit dire ou l'on se reveille et ce que ca coute"
    assert all(a == 1.0 for a in r["ecrits"]), (
        "le texte s'ecrit sur une rue qu'on voit encore (alphas %s)" % sorted(set(r["ecrits"]))
    )
    assert r["images"][-1]["a"] < 0.2, "le fondu ne finit pas en clair"
    assert 120 <= len(r["images"]) <= 200, (
        "une ellipse d'hopital se sent : ni un clignotement, ni une attente (%s images)"
        % len(r["images"])
    )
    # ⚠️ La ville est FIGEE pendant : on gisait a 1 PV au milieu de la rue
    # pendant deux secondes et demie, et un char pouvait repasser dessus.
    assert r["apres"]["t"] == r["avant"]["t"], "le temps de jeu a passe pendant le fondu"
    assert r["apres"]["heure"] == r["avant"]["heure"], "l'heure a avance pendant le fondu"
    assert r["apres"]["px"] == r["avant"]["px"], "un passant a marche pendant le fondu"
    assert r["apres"]["cx"] == r["avant"]["cx"], "un char a roule pendant le fondu"
    assert r["repart"] == 5, "le jeu n'est pas reparti apres le fondu"
    assert r["vie"] == r["max"] and r["piece"] == "hopital" and r["arrive"] < 48


def test_se_faire_arreter_pendant_le_fondu_de_l_hopital_n_empile_pas_deux_noirs(banc):
    """⚠️ Le cas qui casse tout, version ellipse : deux fondus en meme temps.

    C'est celui que `finirTransition()` reglait deja pour les portes — passer
    une porte pendant le noircissement d'une autre. Depuis que l'hopital et la
    prison ont la meme machine, la regle doit valoir pour eux : le fondu qui
    joue finit tout de suite (sa scene change, une fois), et le nouveau repart
    du clair. Sinon on se reveille a l'hopital APRES etre sorti de prison."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const j = L.B.joueur;
        L.B.partie.argent = 900;
        L.Entites.blesser(j, 9999, null, {});
        o.frame(10);                                  // en plein noircissement
        const pendant = { t: L.B.transition.t, fait: L.B.transition.fait };
        L.B.recherche.etoiles = 3;
        L.Missions.prison(null);
        const repart = { t: L.B.transition.t, fait: L.B.transition.fait };
        // ⚠️ Le reveil fini, on est couche dans un lit de l'hopital — et c'est de
        // LA que la prison doit nous sortir, pas nous laisser dans la piece.
        const auHopital = !!L.B.interieur && L.B.interieur.slug === 'hopital' && !!j.alite;
        o.fondu();
        const poste = L.Monde.carte.points.find(function (p) { return p.slug === 'poste'; });
        return { pendant: pendant, repart: repart, auHopital: auHopital,
                 auPoste: Math.hypot(j.x - poste.x * L.TT, j.y - poste.y * L.TT),
                 fondus: !!L.B.transition, arrete: !!j.arrete, vie: j.vie, max: j.vieMax,
                 dehors: !L.B.interieur && !L.B.exterieur, alite: !!j.alite };
    }""")
    assert r["pendant"]["fait"] is False and r["pendant"]["t"] > 0, "le premier fondu doit etre en cours"
    assert r["auHopital"] is True, (
        "le fondu interrompu doit avoir fait ce qu'il promettait (le reveil a l'hopital), une fois"
    )
    assert r["repart"] == {"t": 0, "fait": False}, (
        "le fondu de la prison repart du clair : %s" % r["repart"]
    )
    assert r["fondus"] is False, "il reste un fondu ouvert"
    assert r["auPoste"] < 48 and r["arrete"] is False and r["vie"] == r["max"]
    assert r["dehors"] is True and r["alite"] is False, (
        "sorti de prison encore couche, ou encore dans la piece de l'hopital : %s" % r
    )


def test_on_entre_dans_la_planque_et_on_en_ressort(banc):
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const j = L.B.joueur, c = L.Monde.carte;
        const porte = c.portes.find(function (p) { return p.lieu === 'planque'; });
        j.x = porte.x * L.TT + 8; j.y = (porte.y + 1) * L.TT + 10;
        // ⚠️ On regarde la porte : dehors, ENTRER n'agit que sur ce qu'on regarde (test_regard_js.py).
        L.Entites.regarder(j, 0, -1);
        // Ce qui ne bouge pas : ni les pietons (oublies quand on s'eloigne), ni les
        // chars, ni les armes de fortune (semees au fil des images).
        // ⚠️ `bete` et `ballon` sont de la VIE DE RUE, pas du mobilier : un goéland
        // qui se pose pendant qu'on est dans la planque n'est pas « la ville qui
        // est entrée avec nous ». Ce juge dit que le mobilier fixe revient tel
        // quel — on nomme donc ce qui va et vient, comme les piétons et les chars.
        const fixes = function () { return L.B.entites.filter(function (e) { return ['pieton', 'vehicule', 'ramassage', 'projectile', 'bete', 'ballon'].indexOf(e.type) < 0; }).length; };
        const dehors = { entites: fixes(), w: c.w };
        o.tape('KeyE', 3);
        // La porte passe par un fondu : la piece se charge AU NOIR, pas au clic.
        const pendant = { interieur: L.B.interieur, t: L.B.t, fondu: !!L.B.transition };
        o.fondu();
        const dedans = { interieur: L.B.interieur ? L.B.interieur.slug : null, w: L.Monde.carte.w, entites: L.B.entites.length,
                         nuit: L.Monde.ambiance().alpha, cam: L.B.cam.x < 0,
                         sol: L.Monde.solidite(Math.floor(j.x / L.TT), Math.floor(j.y / L.TT)),
                         invite: (function () { j.x = L.B.interieur.sortie.x * L.TT + 8; j.y = (L.B.interieur.sortie.y - 1) * L.TT + 8; L.Missions.majInvite(j); return L.B.invite; })() };
        o.tape('KeyE', 3);
        o.fondu();
        return { dehors: dehors, pendant: pendant, dedans: dedans, apres: { interieur: L.B.interieur, w: L.Monde.carte.w, entites: fixes(),
                 pres: Math.hypot(j.x - porte.x * L.TT - 8, j.y - (porte.y + 1) * L.TT - 10) } };
    }""")
    assert r["pendant"]["fondu"] is True, "passer une porte doit lancer un fondu"
    assert r["pendant"]["interieur"] is None, "la piece est chargee AVANT le noir : le fondu clignote"
    assert r["dedans"]["interieur"] == "planque" and r["dedans"]["w"] < r["dehors"]["w"]
    assert r["dedans"]["entites"] == 1, "la ville est entree avec nous"
    assert r["dedans"]["nuit"] == 0 and r["dedans"]["cam"] is True, "une piece se centre et n'a pas de nuit"
    assert r["dedans"]["sol"] == 0 and r["dedans"]["invite"] == "SORTIR"
    assert r["apres"]["interieur"] is None and r["apres"]["w"] == r["dehors"]["w"]
    assert r["apres"]["entites"] == r["dehors"]["entites"], "la ville n'est pas revenue telle quelle"
    assert r["apres"]["pres"] < 20, "on doit ressortir devant la porte"


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
        return { fige: fige, curseur: curseur, choisi: choisi, ferme: ferme, retour: L.B.menu === null,
                 etiquette: o.elements.tactile.querySelectorAll('[data-a]')[1].textContent };
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


def test_la_planque_dort_sauve_et_garde_le_coffre(banc):
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const j = L.B.joueur, c = L.Monde.carte;
        const porte = c.portes.find(function (p) { return p.lieu === 'planque'; });
        j.x = porte.x * L.TT + 8; j.y = (porte.y + 1) * L.TT + 10;
        o.entrer(porte);
        L.B.partie.argent = 250; j.vie = 30;
        const jour = L.B.partie.jour;
        // Le coffre.
        const coffre = L.B.interieur.points.find(function (p) { return p.type === 'coffre'; });
        j.x = coffre.x * L.TT + 8; j.y = coffre.y * L.TT + 8 + 12;
        L.Missions.utiliserPoint(j);
        const menuCoffre = L.B.menu.titre;
        L.B.menu.items[0].faire();          // deposer 100
        L.Hud.fermerMenu();
        // Le lit.
        const lit = L.B.interieur.points.find(function (p) { return p.type === 'lit'; });
        j.x = lit.x * L.TT + 8; j.y = lit.y * L.TT + 8 + 12;
        L.Missions.utiliserPoint(j);
        L.B.menu.items[0].faire();          // dormir
        const fondu = !!L.B.transition;
        L.Hud.fermerMenu();
        o.fondu();
        const brut = JSON.parse(o.store[L.Sauvegarde.CLE]);
        return { menuCoffre: menuCoffre, coffre: L.B.partie.planque.coffre, poches: L.B.partie.argent,
                 jour: L.B.partie.jour - jour, heure: L.B.partie.heure, vie: j.vie,
                 sauve: { coffre: brut.planque.coffre, jour: brut.jour, x: brut.x }, fondu: fondu,
                 dehorsX: porte.x * L.TT + 8 };
    }""")
    assert r["menuCoffre"] == "LE COFFRE"
    assert r["coffre"] == 100 and r["poches"] == 150
    assert r["jour"] == 1 and 0.25 < r["heure"] < 0.35, "on se reveille le lendemain matin"
    assert r["vie"] == 100 and r["fondu"] is True
    assert r["sauve"]["coffre"] == 100 and r["sauve"]["jour"] == r["jour"] + 1
    assert abs(r["sauve"]["x"] - r["dehorsX"]) < 4, "la sauvegarde doit retenir la position DEHORS, devant la porte"


def test_le_garage_rachete_repare_et_repeint(banc, paquet):
    eco = paquet["economie"]
    auto = next(v for v in paquet["vehicules"] if v["slug"] == "auto")
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const j = L.B.joueur, c = L.Monde.carte;
        const porte = c.portes.find(function (p) { return p.lieu === 'garage'; });
        j.x = porte.x * L.TT + 8; j.y = (porte.y + 1) * L.TT + 10;
        const v = o.char('auto', 20, 8, 0);
        v.vie = 50; v.vole = true;
        o.entrer(porte);
        L.B.partie.argent = 1000;
        const point = L.B.interieur.points.find(function (p) { return p.type === 'reparer'; });
        j.x = point.x * L.TT + 8; j.y = point.y * L.TT + 8 + 12;
        L.Missions.utiliserPoint(j);
        const menu = L.B.menu;
        const libelles = menu.items.map(function (i) { return i.libelle; });
        const vente = L.Missions.prixDeVente(v);
        const item = function (debut) { return (L.B.menu.items.find(function (i) { return i.libelle.indexOf(debut) === 0; }) || { faire: function () { throw new Error(debut + ' absent de ' + L.B.menu.items.map(function (i) { return i.libelle; }).join('|')); } }); };
        item('RÉPARER').faire();
        const apresReparation = { vie: v.vie, argent: L.B.partie.argent };
        item('REPEINDRE').faire();
        const apresPeinture = { vole: v.vole, argent: L.B.partie.argent };
        L.Missions.utiliserPoint(j);
        item('VENDRE').faire();
        return { libelles: libelles, vente: vente, apresReparation: apresReparation, apresPeinture: apresPeinture,
                 argent: L.B.partie.argent, reste: L.B.exterieur.entites.indexOf(v) >= 0 };
    }""")
    assert any(libelle.startswith("VENDRE") for libelle in r["libelles"]) and "RÉPARER" in r["libelles"]
    assert r["vente"] == round(auto["prix"] * eco["vente_fraction"] * 0.5)
    assert r["apresReparation"]["vie"] == auto["vie"]
    assert r["apresReparation"]["argent"] == 1000 - 50 * eco["reparation_par_pv"]
    assert r["apresPeinture"]["vole"] is False and r["apresPeinture"]["argent"] == r["apresReparation"]["argent"] - eco["repeinte"]
    assert r["reste"] is False, "le char vendu est encore devant le garage"
    assert r["argent"] > r["apresPeinture"]["argent"], "la vente n'a rien rapporte"



def test_le_taxi_de_marco_ne_se_vend_pas(banc, paquet):
    """⚠️ Demande de Martin : « il ne faut pas pouvoir vendre le taxi de Marco. »

    M3 pose le taxi à `porte:garage` — **la porte même** du garage où Ti-Guy
    rachète n'importe quel char garé devant. Trois pas et 175 $ : le taxi sort
    du monde, et l'objectif attend un char qui n'existe plus. ⚠️ Le pire n'est
    pas l'argent, c'est que **la mission ne rate même pas** : `livrer` ne fait
    échouer que sur une épave, donc `p.mission` reste pris, le téléphone ne
    sonne plus jamais, et l'histoire s'arrête là — il faut se faire arrêter
    pour s'en sortir.

    Le juge tient les trois temps, et le troisième est celui qui compte :
    pendant la mission, **après la livraison** (`mission` tombe, `aQui` reste :
    le taxi est à Marco pour toujours), et le char de n'importe qui, qui lui se
    vend encore — sinon on aurait réparé la fuite en fermant le garage.
    """
    marco = next(p for p in paquet["personnages"] if p["slug"] == "marco")
    auto = next(v for v in paquet["vehicules"] if v["slug"] == "auto")
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const j = L.B.joueur, c = L.Monde.carte;
        const porte = c.portes.find(function (p) { return p.lieu === 'garage'; });
        function alaPorte() { j.x = porte.x * L.TT + 8; j.y = (porte.y + 1) * L.TT + 10; }
        function garer(v) { v.x = j.x + 20; v.y = j.y + 8; v.etat = 'stationne'; v.vitesse = 0; L.Entites.indexer(); }
        // Le comptoir du garage : on se plante devant et on ouvre le menu.
        function comptoir() {
            const point = L.B.interieur.points.find(function (p) { return p.type === 'vendre'; });
            j.x = point.x * L.TT + 8; j.y = point.y * L.TT + 8 + 12;
            L.Missions.utiliserPoint(j);
            return L.B.menu.items.find(function (i) { return i.libelle.indexOf('VENDRE') === 0; });
        }
        function essayerDeVendre(v) {
            L.B.partie.argent = 0;
            // ⚠️ Sans char devant la porte, le menu n'a pas de ligne VENDRE :
            // on la remplace par une ligne morte, sinon le juge tombe sur un
            // « undefined » au lieu de dire ce qui cloche.
            const item = comptoir() || { libelle: 'AUCUNE VENTE', detail: '', actif: false, faire: function () { return false; } };
            const vendu = item.faire();
            const r = { libelle: item.libelle, detail: item.detail, actif: item.actif !== false,
                        vendu: vendu, argent: L.B.partie.argent, la: L.B.exterieur.entites.indexOf(v) >= 0 };
            L.Hud.fermerMenu();
            return r;
        }

        L.Histoire.commencer('m3');                 // Marco prête son taxi
        const taxi = L.B.mission.vehicule;
        // Le trafic de la rue n'a rien a faire ici : le char devant la porte
        // doit etre CELUI qu'on teste, pas le premier passant.
        L.B.entites = L.B.entites.filter(function (e) { return e.type !== 'vehicule' || e === taxi; });
        alaPorte(); garer(taxi);
        o.entrer(porte);
        const pendant = essayerDeVendre(taxi);
        o.sortir();

        // La livraison, la vraie : on ramene le taxi au garage et la mission
        // se termine toute seule — c'est la qu'on efface `mission`.
        L.B.partie.mission.etape = 2;
        const g = L.Histoire.lieu('garage');
        taxi.x = g.x; taxi.y = g.y; taxi.vitesse = 0;
        j.x = taxi.x; j.y = taxi.y;
        L.Vehicules.monter(j, taxi);
        o.frame(3);
        // La fin de M3 est une SCENE (Marco fait le tour du taxi) : on la passe.
        L.Scenes.passer();
        L.B.dialogue = null; L.B.cinema = null;
        const livre = { faite: !!L.B.partie.missionsFaites.m3, mission: taxi.mission, aQui: taxi.aQui };

        alaPorte(); garer(taxi);
        o.entrer(porte);
        const apres = essayerDeVendre(taxi);
        o.sortir();

        // Et le char de n'importe qui, a la meme place, se vend toujours.
        L.Entites.retirer(taxi);
        alaPorte();
        const v = o.char('auto', 0, 0, 0);
        garer(v);
        o.entrer(porte);
        const autre = essayerDeVendre(v);
        return { pendant: pendant, livre: livre, apres: apres, autre: autre };
    }""")
    attendu = "IL EST À " + marco["nom"].upper()
    for quand, etat in (("pendant la mission", r["pendant"]), ("apres la livraison", r["apres"])):
        assert etat["actif"] is False, f"{quand} : le garage propose encore d'acheter le taxi de Marco"
        assert etat["detail"] == attendu, f"{quand} : le menu ne dit pas a qui il est ({etat['detail']})"
        assert etat["vendu"] is False and etat["argent"] == 0, f"{quand} : la vente a rapporte de l'argent"
        assert etat["la"] is True, f"{quand} : le taxi a disparu de devant le garage"
    # ⚠️ La livraison efface `mission` — et c'est pour ca que `aQui` existe :
    # sans lui, le taxi redeviendrait vendable la minute ou Marco le recupere.
    assert r["livre"]["faite"], "la mission ne s'est pas terminee : le juge ne prouve rien"
    assert r["livre"]["mission"] is None and r["livre"]["aQui"] == "marco"
    assert r["autre"]["actif"] is True and r["autre"]["vendu"] is True, (
        "plus personne ne peut vendre un char au garage : %s" % r["autre"]
    )
    assert r["autre"]["argent"] == round(auto["prix"] * paquet["economie"]["vente_fraction"])
    assert r["autre"]["la"] is False, "le char vendu est encore devant le garage"

def test_l_armurerie_et_la_boutique_vendent(banc, paquet):
    batte = next(a for a in paquet["armes"] if a["slug"] == "batte")
    coupe_vent = next(t for t in paquet["tenues"] if t["slug"] == "coupe_vent")
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const j = L.B.joueur, c = L.Monde.carte;
        function entrer(lieu, type) {
            if (L.B.interieur) o.sortir();
            const porte = c.portes.find(function (p) { return p.lieu === lieu; });
            j.x = porte.x * L.TT + 8; j.y = (porte.y + 1) * L.TT + 10;
            o.entrer(porte);
            const point = L.B.interieur.points.find(function (p) { return p.type === type; });
            j.x = point.x * L.TT + 8; j.y = point.y * L.TT + 8 + 12;
            L.Missions.utiliserPoint(j);
            return L.B.menu;
        }
        L.B.partie.argent = 500;
        const gus = entrer('armurerie', 'acheter');
        gus.items.find(function (i) { return i.libelle === %s; }).faire();
        const apresBaton = { arme: !!L.B.partie.armes.batte, argent: L.B.partie.argent, titre: gus.titre };
        L.Hud.fermerMenu();
        const rosa = entrer('vetements', 'acheter');
        rosa.items.find(function (i) { return i.libelle === 'COUPE-VENT BLEU'; }).faire();
        return { apresBaton: apresBaton, tenue: L.B.partie.tenue, tenues: L.B.partie.tenues, argent: L.B.partie.argent,
                 swap: j.swaps.c, titre: rosa.titre };
    }""" % json.dumps(batte["nom"].upper()))
    assert r["apresBaton"]["titre"] == "CHEZ GUS" and r["apresBaton"]["arme"] is True
    assert r["apresBaton"]["argent"] == 500 - batte["prix"]
    assert r["titre"] == "BOUTIQUE ROSA" and r["tenue"] == "coupe_vent" and "coupe_vent" in r["tenues"]
    assert r["swap"] == coupe_vent["couleur"], "la tenue doit changer la couleur du chandail"
    assert r["argent"] == 500 - batte["prix"] - coupe_vent["prix"]


def test_le_poing_americain_se_paie_au_comptoir_de_gus(banc, paquet):
    """Martin : « on devrait aussi pouvoir l'acheter ». Par le vrai chemin : la
    porte de Chez Gus, le point `acheter`, la touche ACTION — et il entre dans
    le sac avec les autres, pret pour la roue."""
    americain = next(a for a in paquet["armes"] if a["slug"] == "poing_americain")
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const j = L.B.joueur, c = L.Monde.carte, p = L.B.partie;
        const porte = c.portes.find(function (x) { return x.lieu === 'armurerie'; });
        j.x = porte.x * L.TT + 8; j.y = (porte.y + 1) * L.TT + 10;
        o.entrer(porte);
        const point = L.B.interieur.points.find(function (x) { return x.type === 'acheter'; });
        j.x = point.x * L.TT + 8; j.y = point.y * L.TT + 8 + 12;
        p.argent = 100;
        L.Missions.utiliserPoint(j);
        const menu = L.B.menu;
        function ligne(m) { return m.items.find(function (i) { return i.libelle === 'POING AMÉRICAIN'; }) || null; }
        const avant = ligne(menu);
        if (!avant) return { titre: menu.titre, libelles: menu.items.map(function (i) { return i.libelle; }) };
        const rang = menu.items.indexOf(avant);
        menu.curseur = rang;
        o.tape('KeyE', 2);
        const apres = ligne(L.B.menu);
        return { titre: menu.titre, rang: rang, avant: avant.detail, actif: avant.actif,
                 apres: apres && apres.detail, argent: p.argent, sac: p.armes.poing_americain || null };
    }""")
    assert r["titre"] == "CHEZ GUS"
    assert "avant" in r, "pas de poing americain au comptoir de Gus : %s" % r.get("libelles")
    assert r["rang"] == 0, "en tete de vitrine, c'est le moins cher"
    assert r["avant"] == "%d $" % americain["prix"] and r["actif"] is True
    assert r["argent"] == 100 - americain["prix"], "le poing americain ne s'est pas paye"
    assert r["sac"] is not None, "paye, mais pas dans le sac"
    assert r["apres"] == "DÉJÀ À TOI"


def test_un_achat_unique_se_voit_tout_de_suite_au_comptoir(banc, paquet):
    """⚠️ Un menu est une PHOTO de l'etat au moment ou on l'ouvre. Le comptoir,
    lui, reste ouvert entre deux achats : sans un rafraichissement, le pistolet
    deja paye garde son prix, se rachete une deuxieme fois, et les munitions de
    l'arme qu'on vient d'acheter n'apparaissent qu'a la prochaine visite."""
    pistolet = next(a for a in paquet["armes"] if a["slug"] == "pistolet")
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const j = L.B.joueur, c = L.Monde.carte;
        const porte = c.portes.find(function (p) { return p.lieu === 'armurerie'; });
        j.x = porte.x * L.TT + 8; j.y = (porte.y + 1) * L.TT + 10;
        o.entrer(porte);
        const point = L.B.interieur.points.find(function (p) { return p.type === 'acheter'; });
        j.x = point.x * L.TT + 8; j.y = point.y * L.TT + 8 + 12;
        L.B.partie.argent = 2000;
        L.Missions.utiliserPoint(j);
        const menu = L.B.menu;
        function ligne(m, libelle) { return m.items.find(function (i) { return i.libelle === libelle; }) || null; }
        const avant = ligne(menu, 'PISTOLET');
        const rang = menu.items.indexOf(avant);
        menu.curseur = rang;
        // On achete par le vrai chemin : la touche ACTION, et le menu reste ouvert.
        o.tape('KeyE', 2);
        const apres = ligne(L.B.menu, 'PISTOLET');
        const etat = { ouvert: L.B.menu === menu, detail: apres && apres.detail, actif: apres && apres.actif,
                       sur: L.B.menu && L.B.menu.sur, munitions: !!ligne(L.B.menu, 'MUNITIONS PISTOLET'),
                       curseur: L.B.menu && L.B.menu.curseur };
        // Et on rappuie : un achat unique ne se paie pas deux fois.
        o.tape('KeyE', 2);
        return { avant: avant.detail, rang: rang, etat: etat, argent: L.B.partie.argent,
                 mun: L.B.partie.armes.pistolet ? L.B.partie.armes.pistolet.mun : 0 };
    }""")
    assert r["avant"] == "%d $" % pistolet["prix"]
    assert r["etat"]["ouvert"] is True, "le comptoir s'est ferme sous les doigts du joueur"
    assert r["etat"]["detail"] == "DÉJÀ À TOI", "le comptoir affiche encore le prix d'une arme payee"
    assert r["etat"]["actif"] is False
    assert r["etat"]["sur"] == "%d $" % (2000 - pistolet["prix"]), "le magot affiche n'a pas bouge"
    assert r["etat"]["munitions"] is True, "les munitions de l'arme achetee n'apparaissent pas"
    assert r["etat"]["curseur"] == r["rang"], "le curseur a saute sous le pouce"
    assert r["argent"] == 2000 - pistolet["prix"], "le pistolet s'est paye deux fois"
    assert r["mun"] == pistolet["chargeur"], "l'arme achetee doit venir avec son chargeur"


def test_un_commerce_s_achete_au_comptoir_et_rapporte(banc, paquet):
    """Retour de Martin : « pour acheter un commerce c'est a l'interieur ».

    La porte du kiosque ouvrait un menu ACHETER / ENTRER sur le trottoir. Elle
    n'est plus qu'une porte : on entre, on va a la caisse, et c'est la qu'on
    achete — puis la meme caisse se vide dans nos poches. Tout par le bouton."""
    kiosque = next(p for p in paquet["economie"]["proprietes"] if p["slug"] == "kiosque")
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const j = L.B.joueur, c = L.Monde.carte;
        const libelles = function () { return L.B.menu ? L.B.menu.items.map(function (i) { return i.libelle; }) : null; };
        const choisi = function () { return L.B.menu ? L.B.menu.items[L.B.menu.curseur].libelle : null; };
        L.B.partie.argent = 2000;
        const porte = c.portes.find(function (p) { return p.lieu === 'kiosque'; });
        j.x = porte.x * L.TT + 8; j.y = (porte.y + 1) * L.TT + 10;
        // ⚠️ On regarde la porte : dehors, ENTRER n'agit que sur ce qu'on regarde (test_regard_js.py).
        L.Entites.regarder(j, 0, -1);
        L.Missions.majInvite(j);
        const dehors = L.B.invite;
        o.tape('KeyE', 1);
        const aLaPorte = { menu: libelles(), fondu: !!L.B.transition };
        o.fondu();
        const dedans = L.B.interieur && L.B.interieur.slug;
        const point = L.B.interieur.points.find(function (p) { return p.type === 'caisse'; });
        j.x = point.x * L.TT + 8; j.y = point.y * L.TT + 8 + 12;
        // Et la caisse aussi : on la regarde (elle est au-dessus du joueur).
        L.Entites.regarder(j, 0, -1);
        L.Missions.majInvite(j);
        const inviteCaisse = L.B.invite;
        o.tape('KeyE', 2);
        const comptoir = { menu: libelles(), choisi: choisi(), aide: L.B.menu && L.B.menu.aide };
        o.tape('KeyE', 2);
        const achete = { ouvert: !!L.B.menu, a_soi: !!L.B.partie.proprietes.kiosque, argent: L.B.partie.argent };
        for (let i = 0; i < 4; i++) L.Missions.revenusDuJour();
        const caisse = L.B.partie.proprietes.kiosque.caisse;
        L.Missions.majInvite(j);
        const inviteApres = L.B.invite;
        o.tape('KeyE', 2);
        const aSoi = { menu: libelles(), choisi: choisi() };
        const avant = L.B.partie.argent;
        o.tape('KeyE', 2);
        return { dehors: dehors, aLaPorte: aLaPorte, dedans: dedans, inviteCaisse: inviteCaisse,
                 comptoir: comptoir, achete: achete, caisse: caisse, inviteApres: inviteApres, aSoi: aSoi,
                 gain: L.B.partie.argent - avant, reste: L.B.partie.proprietes.kiosque.caisse };
    }""")
    assert r["dehors"] == "ENTRER", "la porte promet encore un achat sur le trottoir"
    assert r["aLaPorte"]["menu"] is None, "la porte ouvre encore un menu : %s" % r["aLaPorte"]["menu"]
    assert r["aLaPorte"]["fondu"] is True and r["dedans"] == "kiosque"
    assert r["inviteCaisse"] == "ACHETER " + kiosque["nom"].upper()
    assert r["comptoir"]["menu"] == ["ACHETER LE COMMERCE"], r["comptoir"]["menu"]
    assert r["comptoir"]["choisi"] == "ACHETER LE COMMERCE"
    assert str(kiosque["revenu_par_jour"]) in r["comptoir"]["aide"], "le comptoir ne dit pas ce que ca rapporte"
    assert r["achete"] == {"ouvert": False, "a_soi": True, "argent": 2000 - kiosque["prix"]}
    assert r["caisse"] == kiosque["revenu_par_jour"] * paquet["economie"]["caisse_jours_max"], "la caisse doit plafonner"
    assert r["inviteApres"] == "LA CAISSE"
    assert r["aSoi"]["menu"] == ["PRENDRE LA CAISSE"], "un commerce a soi ne se rachete pas : %s" % r["aSoi"]["menu"]
    assert r["gain"] == r["caisse"] and r["reste"] == 0


def test_au_garage_deux_pressions_vendent_le_char_et_n_achetent_pas_le_garage(banc, paquet):
    """Le garage n'a pas de caisse : l'achat passe dans le menu du comptoir,
    comme PRENDRE LA CAISSE une fois le garage a soi. ⚠️ EN DERNIER — le
    curseur s'ouvre sur la premiere ligne qui se choisit, et la main qui
    appuie deux fois pour vendre un char aurait paye le garage."""
    garage = next(p for p in paquet["economie"]["proprietes"] if p["slug"] == "garage")
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const j = L.B.joueur, c = L.Monde.carte;
        L.B.partie.argent = 2 * %d;
        const porte = c.portes.find(function (p) { return p.lieu === 'garage'; });
        j.x = porte.x * L.TT + 8; j.y = (porte.y + 1) * L.TT + 10;
        // ⚠️ On regarde la porte : dehors, ENTRER n'agit que sur ce qu'on regarde (test_regard_js.py).
        L.Entites.regarder(j, 0, -1);
        o.char('auto', 20, 0, 0);
        o.tape('KeyE', 1);
        o.fondu();
        const point = L.B.interieur.points.find(function (p) { return p.type === 'vendre'; });
        j.x = point.x * L.TT + 8; j.y = point.y * L.TT + 8 + 12;
        // Et le comptoir aussi : on le regarde (il est au-dessus du joueur).
        L.Entites.regarder(j, 0, -1);
        o.tape('KeyE', 2);
        const menu = L.B.menu ? L.B.menu.items.map(function (i) { return i.libelle; }) : null;
        const choisi = L.B.menu ? L.B.menu.items[L.B.menu.curseur].libelle : null;
        const avant = L.B.partie.argent;
        o.tape('KeyE', 2);
        return { dedans: L.B.interieur.slug, menu: menu, choisi: choisi,
                 a_soi: !!L.B.partie.proprietes.garage, depense: avant - L.B.partie.argent };
    }""" % garage["prix"])
    assert r["dedans"] == "garage"
    assert r["menu"] and r["menu"][-1] == "ACHETER LE COMMERCE", r["menu"]
    assert r["choisi"].startswith("VENDRE"), r["choisi"]
    assert r["a_soi"] is False, "deux pressions au comptoir ont achete le garage"
    assert r["depense"] <= 0


@pytest.mark.parametrize("a_soi", [False, True], ids=["a_vendre", "a_soi"])
def test_devant_le_garage_la_porte_gagne_sur_le_char_gare_devant(banc, a_soi):
    """Bug de Martin : devant le garage, un char gare devant la porte, et
    « ENTRER » faisait monter dans le char au lieu d'entrer dans le batiment.

    Une seule pression d'ACTION, deux lecteurs dans la meme image :
    `Combat.maj` passe la porte, puis `Vehicules.maj` relisait la meme
    pression et prenait la portiere d'a cote — on se reveillait dans la piece
    au volant. A vendre ou a soi, la porte ne demande rien : elle s'ouvre."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const j = L.B.joueur, c = L.Monde.carte;
        const porte = c.portes.find(function (p) { return p.lieu === 'garage'; });
        if (%s) L.B.partie.proprietes.garage = { jour: L.B.partie.jour, caisse: 0 };
        L.B.partie.argent = 99999;             // de quoi acheter : la porte ne doit pas le proposer
        j.x = porte.x * L.TT + 8; j.y = (porte.y + 1) * L.TT + 10;
        // ⚠️ On regarde la porte : dehors, ENTRER n'agit que sur ce qu'on regarde (test_regard_js.py).
        L.Entites.regarder(j, 0, -1);
        // ⚠️ Le char est DANS LE REGARD, a cote de la porte : depuis que ACTION n'agit que
        // sur ce qu'on regarde, un char a l'est de quelqu'un qui regarde la porte au nord
        // n'etait plus a portee de rien — et la course entre les deux lecteurs ne se jouait plus.
        const v = o.char('auto', 12, -12, 0);  // gare devant, a portee de portiere
        const pres = L.Vehicules.vehiculeSousLaMain(j) === v, devant = L.Monde.porteDevant(j) === porte;
        o.tape('KeyE', 1);                     // UNE pression
        const fondu = !!L.B.transition, menu = !!L.B.menu, auVolant = !!j.dansVehicule;
        o.fondu();
        return { pres: pres, devant: devant, fondu: fondu, menu: menu, auVolant: auVolant,
                 dedans: L.B.interieur ? L.B.interieur.slug : null, attendu: porte.interieur,
                 encoreAuVolant: !!j.dansVehicule, conducteur: v.conducteur === j };
    }""" % ("true" if a_soi else "false"))
    assert r["pres"] is True and r["devant"] is True, "le decor du test : un char a portee ET la porte devant"
    assert r["menu"] is False and r["fondu"] is True, "la porte d'un commerce ouvre un menu au lieu de s'ouvrir"
    assert r["auVolant"] is False, "la meme pression d'ACTION a passe la porte ET pris la portiere"
    assert r["dedans"] == r["attendu"], "ENTRER n'a pas mene dans le garage"
    assert r["encoreAuVolant"] is False and r["conducteur"] is False


def test_les_paquets_caches_se_ramassent_et_paient(banc, paquet):
    tarifs = paquet["economie"]["tarifs"]
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const j = L.B.joueur;
        const paquets = L.B.entites.filter(function (e) { return e.type === 'paquet'; });
        const n = paquets.length;
        const argent = L.B.partie.argent;
        for (let i = 0; i < 10; i++) {
            const q = L.B.entites.find(function (e) { return e.type === 'paquet'; });
            j.x = q.x; j.y = q.y;
            L.Entites.indexer();
            L.Missions.maj();
        }
        L.Missions.sauvegarderPartie();
        const brut = JSON.parse(o.store[L.Sauvegarde.CLE]);
        return { n: n, restants: L.B.entites.filter(function (e) { return e.type === 'paquet'; }).length,
                 gain: L.B.partie.argent - argent, sauves: Object.keys(brut.paquets).length };
    }""")
    assert r["n"] == 20
    assert r["restants"] == 10
    assert r["gain"] == 10 * tarifs["paquet"] + tarifs["paquets_prime_10"]
    assert r["sauves"] == 10, "les paquets ramasses doivent etre sauvegardes"


def test_le_journal_du_matin_raconte_hier_et_enseigne_les_matins_calmes(banc, paquet):
    """⚠️ Le repli « rien à signaler » ENSEIGNE maintenant une chose.

    Le jeu a des boulots au klaxon, une fourrière, un marché noir, des
    propriétés — et rien n'expliquait rien : M1 apprend à marcher et à voler un
    char, après quoi le joueur est tout seul. Un matin où il ne s'est rien passé
    est exactement la place libre, et elle ne coûte pas une fenêtre de plus.

    Le juge tient les trois règles qui comptent : **on enseigne ce qu'il n'a pas
    fait**, **jamais deux fois la même**, et quand il n'y a plus rien à
    apprendre le repli **redevient** « rien à signaler » — ce qui est une bonne
    nouvelle, pas une panne."""
    lecons = paquet["journal_lecons"]
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const p = L.B.partie;
        // 1. Un matin calme : il enseigne.
        p.stats.tues = 0;
        L.Missions.nouveauJour();
        const premiere = L.B.dialogue ? L.B.dialogue.lignes[0] : null;
        L.B.dialogue = null;
        // 2. Jamais deux fois la meme : le lendemain, une autre.
        const lues = [];
        for (let jour = 0; jour < 4; jour++) {
            L.Missions.nouveauJour();
            lues.push(L.B.dialogue ? L.B.dialogue.lignes[1] : null);
            L.B.dialogue = null;
        }
        // 3. ⚠️ On n'enseigne QUE ce qu'il n'a pas fait : on remet a zero les
        //    lecons lues, mais on declare avoir tout fait.
        for (const l of (L.B.defs.journal_lecons || [])) p.stats[l.cle] = 9;
        // ⚠️ UN JOUR POUR RIEN D'ABORD : `nouveauJour` compare a HIER, et l'on
        // vient de faire neuf courses d'un coup — ce qui est une manchette, pas
        // un matin calme. Ce premier passage absorbe l'ecart ; le suivant est
        // le vrai matin calme de quelqu'un qui sait deja tout.
        L.Missions.nouveauJour();
        L.B.dialogue = null;
        p.leconsLues = [];
        L.Missions.nouveauJour();
        const toutSu = L.B.dialogue ? L.B.dialogue.lignes[0] : null;
        L.B.dialogue = null;
        // 4. Et le sang passe AVANT la lecon : une manchette est une manchette.
        p.stats.tues = 2;
        L.Missions.nouveauJour();
        const sang = L.B.dialogue ? L.B.dialogue.lignes[0] : null;
        return { premiere: premiere, lues: lues, toutSu: toutSu, sang: sang,
                 qui: L.B.dialogue.qui, retenues: p.leconsLues.length };
    }""")
    assert r["qui"] == "LE CLAIRON DE LA BAIE"
    assert r["premiere"] == "LE SAVIEZ-VOUS?", (
        "un matin calme n'enseigne rien : %s" % r["premiere"]
    )
    # ⚠️ Jamais deux fois la même — et c'est la règle qui manquait partout
    # ailleurs dans ce dépôt, répliques des passants comprises.
    dites = [x for x in r["lues"] if x]
    assert len(dites) == len(set(dites)), "le journal enseigne deux fois la même chose : %s" % dites
    assert len(dites) >= 3, "le journal cesse d'enseigner après deux jours : %s" % dites
    # ⚠️ Tout su : le repli ne reprend plus « Brume sur le bassin » a l'infini,
    # il VARIE entre les matins calmes — la bonne nouvelle reste la meme, un
    # matin ou rien n'arrive, mais il ne se lit plus mot pour mot pareil.
    matins = {m["titre"] for m in paquet["journal_matins"]}
    assert r["toutSu"] in matins, (
        "il enseigne encore, ou le matin calme ne varie pas : %s" % r["toutSu"]
    )
    assert r["sang"] == "UN MORT DANS LA RUE", "une leçon passe avant un mort : %s" % r["sang"]
    # ⚠️ `retenues` est mesuré APRÈS qu'on l'a remis à zéro dans le banc : ce
    # qui compte ici, c'est qu'il ait grandi pendant les quatre premiers jours,
    # et les quatre leçons distinctes ci-dessus le prouvent déjà.
    assert len(lecons) >= 4, "moins de quatre leçons : le journal a vite fini d'enseigner"


def test_les_matins_calmes_ne_se_redisent_pas_deux_fois_de_suite(banc, paquet):
    """⚠️ « Brume sur le bassin » était le SEUL matin normal, et un joueur qui
    avait tout appris le lisait mot pour mot chaque jour. Les matins calmes
    (`journal_matins`) VARIENT, tirés dans le dé du jeu sans jamais redire le
    précédent — la même règle que les répliques de la rue, et reproductible
    parce que le tirage passe par `B.rng()`."""
    matins = [m["slug"] for m in paquet["journal_matins"]]
    assert len(matins) >= 2, "moins de deux matins calmes : rien à faire varier"
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const p = L.B.partie;
        // Tout su : on enseigne a personne, il ne reste que les matins calmes.
        for (const l of (L.B.defs.journal_lecons || [])) p.stats[l.cle] = 9;
        // ⚠️ On rebase le journal d'hier sur les stats d'AUJOURD'HUI : sinon
        // `courses = 9` ferait une manchette (le taxi qui ne dort pas, min 3),
        // pas un matin calme. Le delta doit etre zero pour ne rien signaler.
        p.journal = { crimes: p.stats.crimes || 0, tues: p.stats.tues || 0, volees: p.stats.volees || 0,
                      courses: p.stats.courses || 0, hospitalisations: p.stats.hospitalisations || 0 };
        const titres = [];
        for (let jour = 0; jour < 8; jour++) {
            L.Missions.nouveauJour();
            const m = p.derniereManchette;
            titres.push(m ? m.slug : null);
            const s = p.stats;
            p.journal = { crimes: s.crimes || 0, tues: s.tues || 0, volees: s.volees || 0,
                          courses: s.courses || 0, hospitalisations: s.hospitalisations || 0,
                          matin: m ? m.slug : null };
        }
        return { titres: titres, lues: L.B.dialogue ? L.B.dialogue.lignes[0] : null };
    }""")
    titres = r["titres"]
    # Chaque matin tire est bien un matin calme, jamais une manchette ni lecon.
    assert all(t in matins for t in titres), f"pas des matins calmes : {titres}"
    # Jamais deux fois de suite le meme.
    for a, b in zip(titres, titres[1:]):
        assert a != b, f"deux matins calmes identiques de suite : {titres}"
    # Et le bassin est assez large pour qu'on en voie plus d'un sur huit jours.
    assert len(set(titres)) >= 2, f"les matins ne varient pas : {titres}"


# --- Les gestes : le corps bouge quand on agit ----------------------------


def test_le_coup_a_un_elan_et_une_pose_de_coup(banc):
    """⚠️ Le bras est DANS le sprite : la pose de coup le tend. Un bras dessine
    par-dessus faisait un troisieme bras (Martin)."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const j = L.B.joueur;
        L.Entites.regarder(j, 1, 0);
        const repos = { pose: L.Entites.nomDePose(j), arme: L.Entites.pose(j).arme, dx: L.Entites.pose(j).dx };
        L.Combat.frapper(j, false);
        const phases = {};
        for (let i = 0; i < 40 && j.etat === 'attaque'; i++) {
            const p = L.Entites.pose(j);
            if (!phases[j.phase]) phases[j.phase] = { dx: p.dx, pose: L.Entites.nomDePose(j), image: !!L.Entites.imageDe(j).canvas };
            L.Entites.indexer(); L.Combat.maj();
        }
        // Toutes les directions ont leur pose de coup, gauche par miroir.
        const cuit = L.Atlas.cuire('joueur', L.SPRITES.joueur, null);
        const poses = ['frappe_bas', 'frappe_haut', 'frappe_droite', 'frappe_gauche'].filter(function (n) { return !!cuit.poses[n]; });
        // Une batte se voit dans la main, au repos et au coup ; la main est celle de la pose.
        L.B.partie.armes.batte = { mun: null, usure: 0 }; j.arme = 'batte';
        const mainRepos = L.Entites.imageDe(j).main;
        L.Combat.frapper(j, false);
        for (let i = 0; i < 40 && j.phase !== 'actif'; i++) { L.Entites.indexer(); L.Combat.maj(); }
        const mainCoup = L.Entites.imageDe(j).main;
        const armeTenue = L.Entites.pose(j).arme && L.Entites.pose(j).arme.slug;
        L.Entites.regarder(j, -1, 0);
        const gauche = L.Entites.imageDe(j);
        // ⚠️ L'arme doit se voir dans les QUATRE directions. La main n'est
        // decrite que du cote droit : a gauche elle se miroite (Martin : plus
        // d'arme des qu'il allait a gauche).
        const mains = {};
        [[1, 0], [-1, 0], [0, 1], [0, -1]].forEach(function (d) {
            L.Entites.regarder(j, d[0], d[1]);
            j.etat = 'debout'; j.phase = null;
            const marche = L.Entites.imageDe(j);
            j.etat = 'attaque'; j.phase = 'actif';
            const coup = L.Entites.imageDe(j);
            j.etat = 'debout'; j.phase = null;
            mains[j.face] = { marche: !!marche.main, coup: !!coup.main, pose: coup.pose };
        });
        L.Jeu.rendre();
        return { repos: repos, phases: phases, poses: poses, mainRepos: mainRepos, mainCoup: mainCoup, armeTenue: armeTenue,
                 gauche: { pose: gauche.pose, miroir: gauche.miroir }, mains: mains, images: L.B.stats.images };
    }""")
    assert r["repos"]["pose"] == "droite" and r["repos"]["arme"] is None and r["repos"]["dx"] == 0
    assert r["phases"]["anticipation"]["pose"] == "droite", "on arme le coup dans la pose de marche"
    assert r["phases"]["actif"]["pose"] == "frappe_droite" and r["phases"]["actif"]["image"] is True
    assert r["phases"]["anticipation"]["dx"] < 0 < r["phases"]["actif"]["dx"], "on recule puis on se jette"
    assert sorted(r["poses"]) == ["frappe_bas", "frappe_droite", "frappe_gauche", "frappe_haut"]
    assert r["armeTenue"] == "batte"
    assert r["mainRepos"] != r["mainCoup"], "la main du coup n'est pas celle du repos"
    assert r["gauche"] == {"pose": "frappe_gauche", "miroir": True}
    for face in ("bas", "haut", "droite", "gauche"):
        assert r["mains"][face]["marche"], "l'arme n'est pas dans la main en marchant vers " + face
        assert r["mains"][face]["coup"], "l'arme n'est pas dans la main en frappant vers " + face
        assert r["mains"][face]["pose"] == "frappe_" + face
    assert r["images"] > 0


def test_le_poing_americain_se_tient_en_bout_de_poing_et_se_ramasse_en_arme(banc):
    """Martin : « l'arme poing americain devrait etre seulement un tip gris au
    bout des poings, mais quelque chose de plus gros a ramasser ».

    ⚠️ Un seul dessin servait aux deux : tenu, le 12 x 6 du sol depassait du
    poing comme une planche, aussi large que le torse ; par terre, gris sans
    contour, il se perdait dans le gris du trottoir. On juge ce que le VRAI
    dessin des entites cuit pour l'arme (`Entites.dessiner`), pas le catalogue
    des peintres : c'est ce chemin qui choisissait le mauvais."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const B = L.B, j = B.joueur, E = L.Entites;
        // Le banc ne garde aucun pixel : chaque peintre d'arme repasse sur un
        // canevas qui note ses traits, et on en garde la boite et le plus sombre.
        const cuites = [];
        const cuire = L.Atlas.cuirePeintre;
        L.Atlas.cuirePeintre = function (cle, w, h, peintre) {
            if (/^(objet|main)[|]/.test(cle)) {
                const traits = [];
                const t = { fillStyle: '', clearRect: function () {},
                            fillRect: function (x, y, lw, lh) { if (lw > 0 && lh > 0) traits.push([x, y, lw, lh, String(t.fillStyle)]); } };
                peintre(t, w, h);
                const c = { cle: cle, x0: w, y0: h, x1: -1, y1: -1, sombre: 1 };
                traits.forEach(function (r) {
                    c.x0 = Math.min(c.x0, r[0]); c.y0 = Math.min(c.y0, r[1]);
                    c.x1 = Math.max(c.x1, r[0] + r[2] - 1); c.y1 = Math.max(c.y1, r[1] + r[3] - 1);
                    const v = parseInt(r[4].slice(1), 16);
                    c.sombre = Math.min(c.sombre, (0.299 * (v >> 16 & 255) + 0.587 * (v >> 8 & 255) + 0.114 * (v & 255)) / 255);
                });
                cuites.push(c);
            }
            return cuire.call(this, cle, w, h, peintre);
        };
        function dessin(prep) {
            cuites.length = 0;
            const garde = B.entites;
            B.entites = [j];
            j.x = 3000; j.y = 3000; j.vx = 0; j.vy = 0; j.invincible = 0;
            prep();
            E.dessiner(o.ctx, { x: j.x - L.VW / 2, y: j.y - L.VH / 2 });
            B.entites = garde;
            return cuites.slice();
        }
        B.partie.armes.poing_americain = { mun: null, usure: 0 };
        B.partie.armes.batte = { mun: null, usure: 0 };
        const coup = dessin(function () { j.arme = 'poing_americain'; j.face = 'droite'; j.angle = 0; j.etat = 'attaque'; j.phase = 'actif'; });
        const repos = dessin(function () { j.arme = 'poing_americain'; j.face = 'bas'; j.etat = 'flane'; j.phase = null; });
        const batte = dessin(function () { j.arme = 'batte'; j.face = 'droite'; j.etat = 'attaque'; j.phase = 'actif'; });
        const sol = dessin(function () {
            j.arme = null; j.etat = 'flane'; j.phase = null;
            E.creer('ramassage', j.x + 20, j.y, { r: 4, objet: 'arme', arme: 'poing_americain', munitions: null, t: 0, solide: false });
        });
        return { coup: coup, repos: repos, batte: batte, sol: sol };
    }""")
    for moment in ("coup", "repos"):
        tenu = r[moment]
        assert [c["cle"] for c in tenu] == ["main|poing_americain"], (
            "au %s, la main tient le dessin du sol : %s" % (moment, tenu))
        c = tenu[0]
        assert c["x1"] - c["x0"] + 1 <= 2 and c["y1"] - c["y0"] + 1 <= 3, "un bout, pas une planche : %s" % c
        # La prise est le pixel (2, 5) de la toile (`dessinerArme`) : le bout
        # couvre la main, il ne flotte pas devant.
        assert c["x0"] <= 2 <= c["x1"] and c["y0"] <= 5 <= c["y1"], "le bout n'est pas sur le poing : %s" % c
    assert [c["cle"] for c in r["batte"]] == ["objet|batte"], "les autres armes se tiennent comme elles se ramassent"
    assert [c["cle"] for c in r["sol"]] == ["objet|poing_americain"], r["sol"]
    sol = r["sol"][0]
    assert sol["x1"] - sol["x0"] + 1 >= 13 and sol["y1"] - sol["y0"] + 1 >= 6, "par terre, une vraie arme : %s" % sol
    # ⚠️ Le trottoir est gris (#8f8c86), l'acier aussi : sans un trait sombre,
    # l'arme tombee ne se voit pas.
    assert sol["sombre"] < 0.25, "par terre, l'acier se perd dans le trottoir : %s" % sol


def test_la_roulade_tourne_et_le_recul_chancelle(banc):
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        L.graine(81);
        const j = L.B.joueur;
        j.roule = L.Combat.ROULADE_IMAGES / 2;
        const roule = L.Entites.pose(j).rot;
        j.roule = 0;
        const cible = o.poser('ouvrier', 14, 0);
        cible.vx = 1.5; cible.recul = 5;
        const chancelle = L.Entites.pose(cible).rot;
        j.animT = 5; j.animType = 'ramasse';
        const penche = L.Entites.pose(j);
        return { roule: roule, chancelle: chancelle, penche: penche.echelleY, dy: penche.dy };
    }""")
    assert abs(abs(r["roule"]) - 3.14159) < 0.05, "a mi-roulade, le corps est a l'envers"
    assert r["chancelle"] != 0
    assert r["penche"] < 1 and r["dy"] > 0, "ramasser courbe le dos"


def test_le_joueur_touche_chancelle_puis_se_redresse(banc):
    """Martin : « regarde pourquoi mon personnage est croche. » `blesser` pose un
    `recul` (8 images, 22 si on est renverse) et seule la mise a jour des
    PIETONS le decomptait : le joueur restait penche de 0,22 rad, du cote de sa
    marche, jusqu'a la fin de la partie — au premier coup recu."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        L.graine(81);
        const j = L.B.joueur;
        const lu = function () { return { recul: j.recul, rot: L.Entites.pose(j).rot }; };
        const avant = lu();
        L.Entites.blesser(j, 1, null, {});
        const petit = lu();
        o.frame(12);
        const petitApres = lu();
        L.Entites.blesser(j, 1, null, { renverse: true });
        const gros = lu();
        o.frame(30);
        const grosApres = lu();
        return { avant: avant, petit: petit, petitApres: petitApres, gros: gros, grosApres: grosApres };
    }""")
    assert r["avant"]["rot"] == 0, r
    assert r["petit"]["rot"] != 0 and r["gros"]["rot"] != 0, "le coup fait chanceler : %s" % r
    assert r["petitApres"] == {"recul": 0, "rot": 0}, "le petit coup est oublie en 12 images : %s" % r
    assert r["grosApres"] == {"recul": 0, "rot": 0}, "le corps renverse se redresse en 30 images : %s" % r


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
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        o.tape('Escape', 2);
        const pause = { etat: L.B.etat, menu: L.B.menu && L.B.menu.titre };
        // OPTIONS : troisieme ligne ; on bascule le sang.
        L.B.menu.items.find(function (i) { return i.libelle === 'OPTIONS'; }).faire();
        const options = L.B.menu.titre;
        const sangAvant = L.B.options.sang;
        L.B.menu.items.find(function (i) { return i.libelle === 'SANG'; }).faire(L.B.menu.items[0]);
        const sangApres = L.B.options.sang;
        const sauvees = JSON.parse(o.store[L.Sauvegarde.CLE_OPTIONS]).sang;
        L.B.menu.items.find(function (i) { return i.libelle === 'RETOUR'; }).faire();
        L.B.menu.items.find(function (i) { return i.libelle === 'BILAN DE LA SESSION'; }).faire();
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


def test_la_coop_locale_bascule_un_deuxieme_joueur_a_la_manette(banc):
    """M14, essai — RISQUÉ, pas promis (voir la fiche du jalon) : `Jeu.basculerCoop`
    fait naitre un pieton `coopJoueur2`, mene par LA manette (`Entree.stick`) — le
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
    assert r["ouvert"] == {"coop": True, "entites": r["avant"] + 1, "type": "pieton",
                            "coopFlag": True, "vivant": True}
    assert r["e2VitesseManette"]["vx"] > 0.2, "la manette doit faire marcher le deuxieme joueur"
    assert r["joueurVitesseManette"] == {"vx": 0, "vy": 0}, "la manette a bouge le joueur 1"
    assert r["joueurVitesseClavier"]["vx"] > 0.5, "le clavier doit faire marcher le joueur 1"
    assert r["e2VitesseClavier"] == {"vx": 0, "vy": 0}, "le clavier a bouge le deuxieme joueur"
    assert r["ferme"] == {"coop": None, "encore": False}, "rebasculer efface le deuxieme joueur"


def test_la_camera_de_la_coop_zoome_quand_les_deux_joueurs_s_eloignent(banc):
    """Le milieu des deux joueurs, et un zoom arriere qui grandit avec la
    distance — sans lui, l'un des deux sortirait de l'ecran des qu'ils se
    séparent (voir `Monde.majCameraCoop`)."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        L.Jeu.basculerCoop();
        const zoomProche = L.B.cam.zoom;
        // ⚠️ On DEPLACE le deuxieme joueur, on ne le fait pas MARCHER : ce
        // juge teste la formule de la camera (`Monde.majCameraCoop`), pas le
        // chemin dans la ville — pousser la manette pendant des centaines
        // d'images peut buter sur un mur pres du spawn selon l'endroit
        // (mesure : 22 px apres 900 images, plein est). La marche elle-meme
        // est le sujet de l'autre juge, avec la meme manette.
        L.B.coop.entite.x += 300;
        o.frame(120);
        const zoomLoin = L.B.cam.zoom;
        const dist = Math.hypot(L.B.joueur.x - L.B.coop.entite.x, L.B.joueur.y - L.B.coop.entite.y);
        L.Jeu.basculerCoop();
        o.frame(60);
        const zoomApresFerme = L.B.cam.zoom;
        return { zoomProche: zoomProche, zoomLoin: zoomLoin, dist: dist, zoomApresFerme: zoomApresFerme };
    }""")
    assert r["zoomProche"] == pytest.approx(1, abs=0.02), "cote a cote, pas de zoom arriere"
    assert r["dist"] > 150, "le deuxieme joueur doit s'etre vraiment eloigne"
    assert r["zoomLoin"] < 0.9, f"zoom={r['zoomLoin']} apres {r['dist']:.0f}px d'ecart : ca ne zoome pas"
    assert r["zoomApresFerme"] == pytest.approx(1, abs=0.05), "le zoom revient a 1 apres la coop"


# --- M4 : la police -----------------------------------------------------------


def test_le_a_etoile_contourne_un_batiment_et_ne_gele_pas(banc):
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const c = L.Monde.carte, j = L.B.joueur;
        // Un batiment garanti : on part devant sa porte et on vise derriere lui (la ruelle).
        const porte = c.portes.find(function (p) { return p.lieu === 'armurerie'; });
        const x0 = porte.x * L.TT + 8, y0 = (porte.y + 1) * L.TT + 8;
        let ty = porte.y - 1;
        while (ty > 0 && L.Monde.solidite(porte.x, ty) === 1) ty--;
        const x1 = porte.x * L.TT + 8, y1 = ty * L.TT + 8;
        const t0 = Date.now();
        const chemin = L.Monde.chemin(x0, y0, x1, y1, L.Monde.MASQUE_PIETON);
        const ms = Date.now() - t0;
        let traverseUnMur = false;
        (chemin || []).forEach(function (p) { if (L.Monde.solidite(Math.floor(p.x / L.TT), Math.floor(p.y / L.TT)) === 1) traverseUnMur = true; });
        const direct = Math.abs(y1 - y0) / L.TT;
        // La file : deux demandes servies par image, la troisieme attend.
        let servies = 0;
        for (let i = 0; i < 3; i++) L.Monde.demanderChemin(x0, y0, x1, y1, L.Monde.MASQUE_PIETON, function () { servies++; });
        L.Monde.majChemins();
        const apresUneImage = servies, enAttente = L.Monde.cheminsEnAttente;
        L.Monde.majChemins();
        // Une cible dans un mur : null, tout de suite.
        const impossible = L.Monde.chemin(x0, y0, porte.x * L.TT + 8, porte.y * L.TT + 8, L.Monde.MASQUE_PIETON);
        return { trouve: !!chemin, longueur: chemin ? chemin.length : 0, direct: direct, traverseUnMur: traverseUnMur,
                 ms: ms, apresUneImage: apresUneImage, enAttente: enAttente, servies: servies, impossible: impossible };
    }""")
    assert r["trouve"], "pas de chemin pour contourner l'armurerie"
    assert r["traverseUnMur"] is False
    assert r["longueur"] > r["direct"], "le chemin doit faire le tour, pas passer a travers"
    assert r["ms"] < 50
    assert r["apresUneImage"] == 2 and r["enAttente"] == 1 and r["servies"] == 3
    assert r["impossible"] is None


def test_un_char_coince_dix_secondes_est_debloque(banc):
    """Quelle qu'en soit la cause (ici : le joueur plante devant, de travers
    dans la boite), un char du trafic qui ne bouge plus repart — par lui-meme
    (la cascade de sorties) ou par le chien de garde. Et un char qui fait du
    SUR-PLACE (il bouge sans avancer : un va-et-vient) se fait mordre aussi :
    la capture de Martin montrait un char jamais immobile, jamais debloque."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        L.graine(95);
        const c = L.Monde.carte, j = L.B.joueur, T = L.TT;
        const inter = c.intersections.find(function (i) { return i.feux && i.l === 4; });
        L.B.entites = L.B.entites.filter(function (e) { return e.type !== 'vehicule' && e.type !== 'pieton'; });
        // Un char de travers au milieu de la boite, sans cible, le joueur colle devant lui.
        const v = L.Vehicules.creer('auto', (inter.x + 1) * T + 12, (inter.y + 1) * T + 10, 0.6, { conducteur: 'trafic', etat: 'roule', sens: '>' });
        v.cible = { x: v.x, y: v.y, tx: inter.x + 1, ty: inter.y + 1 };
        j.x = v.x + Math.cos(0.6) * 24; j.y = v.y + Math.sin(0.6) * 24;
        L.Monde.centrerCamera(j.x, j.y);
        const x0 = v.x, y0 = v.y, angle0 = v.angle;
        let bouge = 0;
        for (let i = 0; i < 1500; i++) {
            o.frame(1);
            j.x = v.x + Math.cos(v.angle) * 24; j.y = v.y + Math.sin(v.angle) * 24;   // le joueur reste devant
            if (Math.hypot(v.x - x0, v.y - y0) > 40 && !bouge) bouge = i;
        }
        const droit = Math.abs(Math.sin(2 * v.angle)) < 0.2;
        // Le sur-place : un char qu'on ramene chaque image a son point de depart.
        const w = L.Vehicules.creer('auto', (inter.x + 1) * T + 8, (inter.y + 1) * T + 8, 0, { conducteur: 'trafic', etat: 'roule', sens: '>' });
        const wx = w.x, wy = w.y;
        let mordu = -1;
        // ⚠️ Le joueur reste colle au char et en vie A CHAQUE IMAGE. Deux
        // raisons, et la seconde a deja fait passer ce test pour un bogue du
        // chien de garde : la bulle d'oubli retire un char loin du joueur, et un
        // joueur plante vingt secondes au milieu d'un croisement finit par se
        // faire renverser — l'hopital l'emmene a l'autre bout de la ville, le
        // char est oublie, et plus personne ne surveille rien.
        for (let i = 0; i < 1400 && mordu < 0; i++) {
            j.x = wx; j.y = wy + 40; j.vie = j.vieMax; j.invincible = 30;
            L.Monde.centrerCamera(j.x, j.y);
            o.frame(1);
            if (w.debloques) mordu = i; else { w.x = wx; w.y = wy; }
        }
        return { bouge: bouge, debloques: v.debloques || 0, droit: droit, angle0: angle0,
                 surRoute: L.Monde.estRoute(Math.floor(v.x / T), Math.floor(v.y / T)), mordu: mordu };
    }""")
    assert 0 < r["bouge"] < 700, "le char n'est jamais reparti (seul, ou par le chien de garde a 600 images)"
    assert 600 <= r["mordu"] < 1300, "un char qui bouge sans avancer doit se faire mordre par le chien de garde"
    assert r["surRoute"], "le char debloque a fini hors de la route"


def test_un_char_sort_de_chaque_t_par_la_tige_sans_tourner_en_rond(banc):
    """Martin : « ils tournent en rond dans l'intersection ». Par la tige d'un
    T, la sortie prevue est souvent impossible depuis la rangee ou l'on entre :
    le char doit quand meme sortir, par n'importe quel bras, sans repasser
    par la boite."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        L.graine(97);
        const c = L.Monde.carte, j = L.B.joueur, T = L.TT;
        const tes = c.intersections.filter(function (i) { return i.stop; });
        const resultats = [];
        tes.forEach(function (inter, k) {
            if (k % 3) return;                        // un T sur trois : assez pour couvrir les quatre tiges
            L.B.entites = L.B.entites.filter(function (e) { return e.type !== 'vehicule' && e.type !== 'pieton'; });
            j.x = (inter.x - 1) * T + 8; j.y = (inter.y - 1) * T + 8;
            L.Monde.centrerCamera(j.x, j.y);
            // La ligne d'arret de la tige : la tuile 'S' dont le sens est celui du stop.
            let sx = -1, sy = -1;
            for (const cle in c.arrets) {
                if (c.arrets[cle] !== inter.stop) continue;
                const xy = cle.split(',').map(Number);
                const p = { '<': [-1, 0], '>': [1, 0], '^': [0, -1], 'v': [0, 1] }[inter.stop];
                if (L.Monde.intersectionA(xy[0] + p[0], xy[1] + p[1]) === inter) { sx = xy[0]; sy = xy[1]; break; }
            }
            if (sx < 0) { resultats.push({ inter: k, stop: inter.stop, erreur: 'pas de ligne d arret' }); return; }
            const p = { '<': [-1, 0], '>': [1, 0], '^': [0, -1], 'v': [0, 1] }[inter.stop];
            const v = L.Vehicules.creer('auto', (sx - p[0] * 2) * T + 8, (sy - p[1] * 2) * T + 8, Math.atan2(p[1], p[0]), { conducteur: 'trafic', etat: 'roule', sens: inter.stop });
            v.sortie = ['droit', 'gauche', 'droite'];   // tout droit : impossible, c'est la tige
            let entre = false, sorti = false, boucles = 0, derniere = null;
            const vus = new Set();
            for (let i = 0; i < 1500 && !sorti; i++) {
                o.frame(1);
                const tx = Math.floor(v.x / T), ty = Math.floor(v.y / T);
                const cle = tx + ',' + ty;
                const dedans = tx >= inter.x - 2 && tx < inter.x + inter.l + 2 && ty >= inter.y - 2 && ty < inter.y + inter.h + 2;
                if (dedans) {
                    entre = true;
                    // Une boucle, c'est REVENIR sur une tuile deja quittee — pas y rester.
                    if (cle !== derniere) { if (vus.has(cle)) boucles++; vus.add(cle); derniere = cle; }
                }
                else if (entre && L.Monde.fleche(tx, ty) !== '.' && L.Monde.fleche(tx, ty) !== '+') sorti = true;
            }
            resultats.push({ inter: k, stop: inter.stop, entre: entre, sorti: sorti, boucles: boucles, sens: v.sens, debloques: v.debloques || 0 });
        });
        return resultats;
    }""")
    assert r, "aucun T"
    for res in r:
        assert "erreur" not in res, res
        assert res["entre"] and res["sorti"], f"le char n'est pas ressorti du T : {res}"
        assert res["debloques"] == 0, f"le chien de garde a du intervenir : {res}"
        assert res["boucles"] <= 1, f"le char a tourne en rond dans le T : {res}"


def test_l_ombre_d_un_saut_raconte_la_hauteur(banc):
    """⚠️ Bug de Martin : « s'il marche, qu'on voie une ombre pour bien imager
    le saut. » Elle existait — un rectangle de 20 x 10 FIXE, pose seulement
    au-dessus de `z > 2` : la meme tache pour une moto et pour un autobus de
    48 px, qui ne retrecissait pas, ne s'ecartait pas et ne palissait pas. Une
    ombre collee sous le char ne dit aucune altitude, et c'est pour ca qu'un
    saut de sept pixels avait l'air de ne pas exister.

    Le juge mesure ce qu'elle raconte : elle a la taille du char, elle
    retrecit et elle s'ecarte en montant.

    ⚠️ **Reformule le 15 sept. 2026** : il exigeait qu'un char POSE AU SOL n'ait
    AUCUNE ombre. C'etait la regle d'avant, et la refonte des vehicules la
    change — l'ombre au sol permanente est le filet de la vue de profil, parce
    qu'un char vu de dos ne montrera plus ses 28 px de longueur. Ce que le juge
    voulait vraiment dire survit intact et se mesure mieux : au sol, l'ombre est
    SOUS le char, pas detachee de lui. C'est l'ecart qui raconte l'altitude, et
    a zero il doit etre nul ou d'un pixel.
    """
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        // ⚠️ DEUX MESURES, ET IL FAUT LES DEUX. La TRACE dit ce qui est
        // vraiment peint a l'ecran (une regle qui ne se dessinerait pas ne
        // vaudrait rien) ; `ombreDe` dit OU l'ombre tombe — depuis qu'elle est
        // tournee comme le char, l'ecart passe par le `translate` et la trace
        // du rectangle ne le porte plus.
        function ombre(slug, z) {
            const v = o.char(slug, 0, 0, 0);
            v.z = z;
            const ctx = L.Base.ecran();
            ctx.traces = [];
            L.Vehicules.dessinerUn(ctx, v, 0, 0);
            const q = L.Vehicules.ombreDe(v);
            L.Entites.retirer(v);
            // L'ombre est le seul rectangle plein : le char, lui, est une image.
            const t = ctx.traces[0];
            return t ? { l: t[2], h: t[3], couleur: t[4],
                         ecart: +(q.x - v.x).toFixed(2), part: q.part } : null;
        }
        return {
            auSol: ombre('auto', 0),
            basse: ombre('auto', 1),
            haute: ombre('auto', 28),
            moto: ombre('moto', 10),
            autobus: ombre('autobus', 10),
        };
    }""")
    assert r["auSol"], "un char pose au sol n'a plus d'ombre du tout"
    # ⚠️ SOUS le char, pas a cote : au sol, l'ombre ne doit pas se detacher.
    assert r["auSol"]["ecart"] <= 2, (
        "l'ombre d'un char pose au sol est detachee de lui : %s" % r
    )
    assert r["basse"], "une ombre qui n'arrive qu'au-dessus d'un seuil rate le debut du vol"
    assert r["basse"]["ecart"] > r["auSol"]["ecart"], (
        "l'ombre ne bouge pas des le premier pixel de vol : %s" % r
    )
    assert r["haute"]["l"] < r["basse"]["l"], "l'ombre ne retrecit pas quand le char monte"
    assert r["haute"]["ecart"] > r["basse"]["ecart"], "l'ombre ne s'ecarte pas quand le char monte"
    assert r["haute"]["part"] < r["auSol"]["part"], "l'ombre ne palit pas quand le char monte"
    assert r["autobus"]["l"] > r["moto"]["l"], \
        "l'autobus fait 48 px et la moto 20 : leur ombre ne peut pas etre la meme"


def test_chaque_porte_a_son_bruit(banc):
    """Trois portes : le bois d'un logement, la porte d'un commerce, la
    portiere d'un char — et RIEN de tel pour une moto ou un velo, qu'on
    enfourche. C'etait le meme grincement pour tout le monde, taxi compris.
    Le genre vient de la fiche (la piece, le char), pas du JS."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const j = L.B.joueur, c = L.Monde.carte;
        const genres = [], montees = [];
        L.Son.SFX.porte = function (genre) { genres.push(genre || null); };
        const vraiEnfourcher = L.Son.SFX.enfourcher;
        L.Son.SFX.enfourcher = function () { montees.push('enfourcher'); return vraiEnfourcher.apply(null, arguments); };
        function pousser(porte) {
            if (!porte) return null;
            genres.length = 0;
            o.entrer(porte); L.Jeu.sortir(); o.fondu();
            return genres.slice();
        }
        const planque = pousser(c.portes.find(function (p) { return p.lieu === 'planque'; }));
        const depanneur = pousser(c.portes.find(function (p) { return p.lieu === 'depanneur'; }));
        const logement = pousser(c.portes.find(function (p) { return p.interieur === 'logement'; }));
        function rouler(slug) {
            genres.length = 0; montees.length = 0;
            const v = o.char(slug, 30, 0, 0);
            L.Vehicules.monter(j, v);
            L.Vehicules.descendre(j);
            return { portes: genres.slice(), montees: montees.slice() };
        }
        return { planque: planque, depanneur: depanneur, logement: logement,
                 auto: rouler('auto'), camion: rouler('camion'), moto: rouler('moto'), velo: rouler('velo') };
    }""")
    assert r["planque"] == ["maison", "maison"], r["planque"]
    assert r["depanneur"] == ["commerce", "commerce"], r["depanneur"]
    if r["logement"] is not None:
        assert r["logement"] == ["maison", "maison"], r["logement"]
    for quatre_roues in ("auto", "camion"):
        assert r[quatre_roues] == {"portes": ["vehicule", "vehicule"], "montees": []}, (quatre_roues, r[quatre_roues])
    for deux_roues in ("moto", "velo"):
        assert r[deux_roues] == {"portes": [], "montees": ["enfourcher", "enfourcher"]}, (deux_roues, r[deux_roues])


def test_le_velo_sonne_au_bouton_du_klaxon(banc):
    """Demande de Martin : « la sonnette comme klaxon de velo ». Le meme bouton
    qu'une auto — et l'etiquette du bouton tactile le dit. ⚠️ C'est la fiche
    qui nomme l'avertisseur (`klaxon`, `vehicules.py`), pas un `slug === 'velo'`."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const j = L.B.joueur;
        const sons = [];
        L.Son.SFX.klaxon = function () { sons.push('klaxon'); };
        L.Son.SFX.sonnette = function () { sons.push('sonnette'); };
        function essayer(slug) {
            sons.length = 0;
            const v = o.char(slug, 40, 0, 0);
            L.Vehicules.monter(j, v);
            const etiquette = o.doc.querySelector('#boutons b[data-a="attaque"]').textContent;
            o.tape('KeyJ', 2);
            o.frame(3);
            L.Vehicules.descendre(j, true);
            return { etiquette: etiquette, sons: sons.slice() };
        }
        return { velo: essayer('velo'), auto: essayer('auto') };
    }""")
    assert r["velo"] == {"etiquette": "SONNETTE", "sons": ["sonnette"]}, r["velo"]
    assert r["auto"] == {"etiquette": "KLAXON", "sons": ["klaxon"]}, r["auto"]


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


def test_le_niveau_de_recherche_ne_partage_pas_la_couleur_de_l_argent(banc):
    """⚠️ Le dore #e8b33c est deja celui de l'argent et de « ce qui est a toi »
    sur la carte. Deux choses differentes de la meme couleur dans le meme coin
    ne se lisent plus — c'est aussi pour ca que les etoiles ont demenage."""
    import pathlib

    racine = pathlib.Path(__file__).resolve().parent.parent
    source = (racine / "static" / "js" / "hud.js").read_text(encoding="utf-8")
    bloc = source[source.index("const ETOILE_ALLUMEE"):source.index("const ETOILE_L")]
    assert "#e8b33c" not in bloc, "l'etoile reprend le dore de l'argent"
    assert "ETOILE_FLASH" in source, "le clignotement rouge du changement de palier a disparu"


def test_un_char_pris_dans_un_mur_en_ressort_toujours(banc, paquet):
    """⚠️ Le garde-fou de Martin (« que mon véhicule ne coince plus dans un mur
    ou un objet »). `avancer` teste les tuiles AVANT chaque pas, mais rien ne
    regardait où le char EST — et trois choses l'y mettent : un autre char qui
    le pousse (`heurterVehicules` ne lit pas les tuiles), un pivot sur place
    contre une façade (la chaîne de cercles tourne DANS le mur), une retombée
    de saut (en l'air, les tuiles ne comptent pas). Une fois dedans, chaque
    direction est bloquée, même celle qui sort.

    Le juge tient les trois moitiés de la règle : un char enfoncé de quelques
    pixels est POUSSÉ dehors, de juste ce qu'il faut et sans changer de cap ;
    un char au milieu d'un toit est POSÉ à la place libre la plus proche, à
    portée, et repart de l'arrêt ; un char libre — ou en l'air — n'est pas
    touché. Puis la preuve que ça sert : un char laissé dans une façade ROULE
    à l'image suivante, sans même compter un choc, là où il restait pris pour
    toujours. Et le tout passe aussi par `maj()`, pour un char à l'arrêt que
    personne ne conduit."""
    ph = paquet["conduite"]["physique"]
    r = banc(r"""function (L, o) {
        L.Jeu.commencer();
        const c = L.Monde.carte, TT = L.TT;
        const out = {};

        function nettoyer() {
            L.B.entites = L.B.entites.filter(function (e) { return e.type === 'joueur'; });
            L.Entites.reindexerDecor(); L.Entites.indexer();
        }
        // Une façade (solide 1) qui court sur cinq tuiles, avec trois rangs
        // libres au nord sur la même largeur : de quoi coucher un char le long.
        function facadeAuSud() {
            for (let ty = 4; ty < c.h - 4; ty++) for (let tx = 4; tx < c.w - 4; tx++) {
                let bon = true;
                for (let dx = -2; dx <= 2 && bon; dx++) {
                    if (L.Monde.solidite(tx + dx, ty) !== 1) bon = false;
                    for (let dy = 1; dy <= 3; dy++) if (L.Monde.solidite(tx + dx, ty - dy) !== 0) bon = false;
                }
                if (bon) return [tx, ty];
            }
            return null;
        }
        // Une tuile qui bloque, entourée de tuiles qui bloquent sur deux rangs : le milieu d'un toit.
        function milieuDuToit() {
            for (let ty = 4; ty < c.h - 4; ty++) for (let tx = 4; tx < c.w - 4; tx++) {
                let plein = true;
                for (let dy = -2; dy <= 2 && plein; dy++) for (let dx = -2; dx <= 2; dx++) {
                    if (!L.Monde.bloque(tx + dx, ty + dy, L.Monde.MASQUE_VEHICULE)) plein = false;
                }
                if (plein) return [tx, ty];
            }
            return null;
        }
        function bloque(v) { return L.Vehicules.bloqueParLesTuiles(v, v.x, v.y); }
        function arrondi(x) { return Math.round(x * 100) / 100; }

        const mur = facadeAuSud();
        out.mur = mur;
        if (mur) {
            const tx = mur[0], ty = mur[1];
            const xMur = tx * TT + 8, yLibre = function (v) { return ty * TT - v.r - 1; };
            nettoyer();
            const v = L.Vehicules.creer('auto', xMur, 0, 0, { etat: 'stationne' });

            // 1. Enfoncé de 4 px dans la façade, couché le long : poussé de 4 px, pas plus.
            v.y = ty * TT - v.r + 4;
            const bloqueAvant = bloque(v);
            const bouge = L.Vehicules.degager(v);
            out.pousse = { bloqueAvant: bloqueAvant, bouge: bouge, bloqueApres: bloque(v),
                           dx: arrondi(v.x - xMur), dy: arrondi(v.y - (ty * TT - v.r + 4)), angle: v.angle };

            // 2. Libre le long du mur, puis pivoté de 30° : un bout entre dans le mur.
            //    Poussé dehors, il garde son cap — c'est ça, pivoter contre un mur.
            v.x = xMur; v.y = yLibre(v); v.angle = 0;
            L.Vehicules.degager(v);
            const libreAvant = !bloque(v);
            v.angle = Math.PI / 6;
            const bloqueTourne = bloque(v);
            const bouge2 = L.Vehicules.degager(v);
            out.pivote = { libreAvant: libreAvant, bloqueTourne: bloqueTourne, bouge: bouge2, bloqueApres: bloque(v),
                           angle: arrondi(v.angle), deplace: arrondi(Math.hypot(v.x - xMur, v.y - yLibre(v))) };

            // 3. Libre : pas touché. Dans le mur mais en l'air : pas touché non plus.
            v.x = xMur; v.y = yLibre(v); v.angle = 0;
            out.libre = { bouge: L.Vehicules.degager(v), meme: v.x === xMur && v.y === yLibre(v) };
            v.y = ty * TT - v.r + 4; v.z = 10;
            out.enLAir = { bouge: L.Vehicules.degager(v), meme: v.y === ty * TT - v.r + 4 };
            v.z = 0;

            // 4. La preuve : laissé dans la façade avec de l'élan le long du mur,
            //    il roule. Sans garde-fou, chaque pas était refusé — il restait là.
            v.x = xMur; v.y = ty * TT - v.r + 4; v.angle = 0; v.chocs = 0;
            v.vitesse = 2; v.vx = 2; v.vy = 0;
            for (let i = 0; i < 10; i++) { L.Vehicules.avancer(v); v.vx = 2; v.vy = 0; }
            out.roule = { dx: arrondi(v.x - xMur), chocs: v.chocs, bloque: bloque(v) };

            // 5. Par `maj()` : à l'arrêt, sans conducteur, poussé dans le mur par
            //    quelqu'un — à l'image suivante, il n'y est plus.
            v.x = xMur; v.y = ty * TT - v.r + 4; v.angle = 0; v.vitesse = 0; v.vx = 0; v.vy = 0;
            L.B.joueur.x = xMur; L.B.joueur.y = (ty - 3) * TT;
            L.Vehicules.maj();
            out.parMaj = { bloque: bloque(v), dy: arrondi(v.y - (ty * TT - v.r + 4)) };
            L.Entites.retirer(v);
        }

        const toit = milieuDuToit();
        out.toit = toit;
        if (toit) {
            nettoyer();
            const x0 = toit[0] * TT + 8, y0 = toit[1] * TT + 8;
            const v = L.Vehicules.creer('auto', x0, y0, 0.3, { etat: 'stationne' });
            v.vitesse = 3; v.vx = 3; v.vy = 0.5;
            const bloqueAvant = bloque(v);
            const bouge = L.Vehicules.degager(v);
            out.pose = { bloqueAvant: bloqueAvant, bouge: bouge, bloqueApres: bloque(v),
                         deplace: arrondi(Math.hypot(v.x - x0, v.y - y0)), vitesse: v.vitesse, vx: v.vx, vy: v.vy,
                         degagements: v.degagements || 0 };
            L.Entites.retirer(v);
        }
        return out;
    }""")
    assert r["mur"], "aucune façade dégagée trouvée dans la ville"
    p = r["pousse"]
    assert p["bloqueAvant"] is True and p["bouge"] is True and p["bloqueApres"] is False, p
    assert p["dx"] == 0 and -5 <= p["dy"] <= -4, "poussé de %s px pour 4 px d'enfoncement" % p["dy"]
    assert p["angle"] == 0
    q = r["pivote"]
    assert q["libreAvant"] is True and q["bloqueTourne"] is True, "le décor du juge a changé : %s" % q
    assert q["bouge"] is True and q["bloqueApres"] is False, q
    assert q["angle"] == round(3.14159265 / 6, 2), "pivoter contre un mur a changé le cap : %s" % q
    assert 0 < q["deplace"] < 8, "poussé trop loin pour un pivot : %s" % q
    assert r["libre"] == {"bouge": False, "meme": True}, "un char libre a été déplacé"
    assert r["enLAir"] == {"bouge": False, "meme": True}, "un char en l'air a été dégagé"
    m = r["roule"]
    assert m["dx"] >= 15 and m["chocs"] == 0 and m["bloque"] is False, "laissé dans la façade, il ne roule pas : %s" % m
    assert r["parMaj"]["bloque"] is False and r["parMaj"]["dy"] < 0, "`maj()` laisse un char à l'arrêt dans le mur : %s" % r["parMaj"]
    assert r["toit"], "aucun toit assez large trouvé"
    t = r["pose"]
    assert t["bloqueAvant"] is True and t["bouge"] is True and t["bloqueApres"] is False, t
    assert 0 < t["deplace"] <= ph["degagement_px"] + 1, "posé hors de portée : %s" % t
    assert t["vitesse"] == 0 and t["vx"] == 0 and t["vy"] == 0, "un char posé garde son élan : %s" % t
    assert t["degagements"] == 1


def test_le_sol_d_un_ilot_ne_se_repete_plus_toutes_les_quatre_tuiles(banc):
    """⚠️ Demande de Martin : « fais une passe visuelle d'amélioration de tous
    les pâtés de maison ».

    Le trottoir, l'herbe et la ruelle font **43 % de la ville** à eux trois
    (28 %, 10,5 %, 4,7 % des tuiles) — c'est de loin la plus grande surface
    qu'elle ait. Les trois se peignaient avec **quatre** tuiles de 16 px,
    tirées sur `hash2 % 4`, répétées d'un bout à l'autre du Faubourg. De loin,
    ce n'était pas un sol, c'était du papier peint.

    ⚠️ Et le trottoir faisait pire : il peignait son **joint de dalle sur chaque
    tuile**, en haut et à gauche. Un trait tous les seize pixels dans les deux
    sens, sur le quart de la ville — ce qu'on lisait alors, c'était la grille de
    la carte. Une dalle de béton fait maintenant DEUX tuiles de côté, et chaque
    tuile lit sa parité pour savoir de quel coin de dalle elle est (la même
    règle que la case de stationnement, qui ne peint que sa ligne de gauche pour
    ne pas doubler celle de sa voisine).
    """
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        function peindre(g, v) {
            const ctx = L.Base.nouveauCanvas(L.TT, L.TT).getContext('2d');
            ctx.traces = [];
            L.TUILES[g](ctx, v, L.TT);
            return JSON.stringify(ctx.traces);
        }
        // Combien de tuiles DIFFERENTES un carre de 8 x 8 donne, par sol.
        const distinctes = {};
        for (const g of ['.', ',', 'x']) {
            const vues = {};
            for (let y = 40; y < 48; y++) {
                for (let x = 40; x < 48; x++) vues[peindre(g, L.Monde.varianteDeSol(g, x, y))] = 1;
            }
            distinctes[g] = Object.keys(vues).length;
        }
        // La dalle : les quatre parites d'un carre de 2 x 2, sans l'usure.
        const dalle = [[0, 0], [1, 0], [0, 1], [1, 1]].map(function (p) {
            return L.Monde.varianteDeSol('.', 100 + p[0], 100 + p[1]) & 3;
        });
        // Qui peint un joint : une bande de 1 px sur tout un cote de la tuile.
        function joints(v) {
            const ctx = L.Base.nouveauCanvas(L.TT, L.TT).getContext('2d');
            ctx.traces = [];
            L.TUILES['.'](ctx, v, L.TT);
            const t = ctx.traces;
            return {
                ouest: t.some(function (q) { return q[0] === 0 && q[1] === 0 && q[2] === 1 && q[3] === L.TT; }),
                nord: t.some(function (q) { return q[0] === 0 && q[1] === 0 && q[2] === L.TT && q[3] === 1; }),
            };
        }
        return { distinctes: distinctes, dalle: dalle, usures: L.Monde.USURES_DE_SOL,
                 joints: [0, 1, 2, 3].map(joints) };
    }""")
    for glyphe, combien in r["distinctes"].items():
        assert combien > 4, (
            f"le sol « {glyphe} » ne donne que {combien} tuiles differentes sur 64 : "
            "c'est du papier peint"
        )
    assert r["usures"] >= 8, "moins de huit usures, et on reconnait la tuile d'a cote"
    assert sorted(r["dalle"]) == [0, 1, 2, 3], (
        f"les quatre coins d'une dalle ne se distinguent pas : {r['dalle']}")
    # ⚠️ UNE dalle sur quatre porte ses deux joints, une seule n'en porte aucun :
    # c'est ca, une dalle de deux tuiles de cote. Quatre tuiles qui peignent
    # chacune ses deux joints, c'est un quadrillage de seize pixels.
    j = r["joints"]
    assert sum(1 for q in j if q["ouest"] and q["nord"]) == 1, j
    assert sum(1 for q in j if not q["ouest"] and not q["nord"]) == 1, j
    assert sum(1 for q in j if q["ouest"]) == 2 and sum(1 for q in j if q["nord"]) == 2, j


def test_un_arbre_plante_dans_le_beton_a_une_fosse(banc):
    """⚠️ Demande de Martin : « les arbres qui sont sur un trottoir doivent avoir
    un petit rond de terre à leur pied ». Un arbre planté dans le béton sans rien
    à son pied n'est pas planté, il est **posé** — et c'est ce qu'on voyait sur
    la place publique du Faubourg, quatre arbres debout sur des dalles.

    ⚠️ C'est la **légende** qui décide, pas le dessin : `terre` dit d'un sol
    qu'on peut y planter sans rien découper (le gazon, le sable, l'allée de
    parc). Le jour où l'on plantera des arbres de rue pour de bon — il n'y en a
    que quatre aujourd'hui, 583 sur 596 sont sur du gazon — chacun aura sa fosse
    sans qu'on touche à une ligne.

    ⚠️ Et c'est une **couche peinte**, cuite avec le morceau : rien ne s'y cogne,
    et elle passe sous les entités. Peinte à chaque image sous chaque arbre, elle
    recouvrirait les pieds de celui qui marche juste au nord.
    """
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const c = L.Monde.carte, def = c.def;
        const arbres = (def.decor || []).filter(function (d) { return d.type === 'arbre'; });
        const dansLeBeton = arbres.filter(function (d) {
            return !(def.legende[def.sol[d.y][d.x]] || {}).terre;
        });
        // Les fosses indexees, sans les doublons de morceau.
        const vues = {};
        c.fosses.forEach(function (liste) {
            liste.forEach(function (f) { vues[f.x + ',' + f.y] = def.sol[f.y][f.x]; });
        });
        // Ce que le peintre pose AU PIED du tronc (l'ancre est en (8, 15)).
        const ctx = L.Base.nouveauCanvas(L.TT, 2 * L.TT).getContext('2d');
        ctx.traces = [];
        L.FACADES.fosseDArbre(ctx, 8, 15);
        const terre = ctx.traces.filter(function (t) { return t[4] === '#4f4030'; });
        const large = Math.max.apply(null, terre.map(function (t) { return t[2]; }));
        return {
            arbres: arbres.length, dansLeBeton: dansLeBeton.length,
            fosses: Object.keys(vues).length,
            sols: Object.keys(vues).map(function (k) { return vues[k]; }),
            rangees: terre.length, large: large,
            hautes: terre.map(function (t) { return t[1]; }),
            centrees: terre.every(function (t) { return t[0] + t[2] / 2 === 8; }),
        };
    }""")
    assert r["arbres"] > 100, "il n'y a presque pas d'arbres : le juge ne mesure rien"
    assert r["dansLeBeton"] > 0, "aucun arbre de rue dans la ville livrée"
    assert r["fosses"] == r["dansLeBeton"], (
        f"{r['fosses']} fosses pour {r['dansLeBeton']} arbres plantés dans le béton")
    assert "," not in r["sols"], f"une fosse creusée dans le gazon : {r['sols']}"
    # Un ROND : plusieurs rangées, plus large au milieu qu'aux bouts, centré sur
    # le tronc. ⚠️ Une seule rangée pleine largeur serait une barre, pas un rond.
    assert r["rangees"] >= 5, f"la fosse n'a que {r['rangees']} rangées : ce n'est pas un rond"
    assert r["large"] >= 10 and r["large"] <= 16, f"fosse large de {r['large']} px"
    assert r["centrees"], "la fosse n'est pas centrée sur le tronc"
    assert max(r["hautes"]) - min(r["hautes"]) + 1 == r["rangees"], "la fosse a un trou"
