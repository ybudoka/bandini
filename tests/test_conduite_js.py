"""Le char qu'on mène, sous Node : physique, volant, lourds, remorqueuse, explosion,
épave, vélo plié, sirènes, radio, portières, sonnette, et le char pris dans un mur.

Découpé de `test_moteur_js.py` (vague D, 29 sept. 2026) : même banc, mêmes juges.
"""

import json

import pytest

from app import vehicules


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


@pytest.fixture(scope="module")
def physique(banc):
    """⚠️ **QUATRE MESURES DE `majPhysique`, UN BANC** (vague C, 28 sept. 2026) : le
    cercle, le pivot, le volant qui prend et se recentre, le frein à main. Aucune ne
    joue d'image — `majPhysique` à la main, sur un char posé. Chacune garde son corps
    tel quel ; ENTRE DEUX, on descend le joueur de son char et on retire tout char
    posé, pour que la suivante parte de la rue qu'avait son juge."""
    return banc("""function (L, o) {
        L.Jeu.commencer();
        const vehicules0 = new Set(L.B.entites.filter(function (e) { return e.type === 'vehicule'; }));
        function ranger() {
            const j = L.B.joueur;
            if (j.dansVehicule) L.Vehicules.descendre(j, true);
            L.B.entites.filter(function (e) { return e.type === 'vehicule' && !vehicules0.has(e); })
                .forEach(function (e) { L.Entites.retirer(e); });
            L.Entites.indexer();
        }
        const out = {};
        // test_le_cercle_d_un_char_ne_grandit_pas_avec_sa_vitesse
        out.cercle = (function () {
            L.graine(7);
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
        })();
        ranger();
        // test_un_char_pivote_sur_son_arriere_pas_sur_son_nombril
        out.pivot = (function () {
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
        })();
        ranger();
        // test_le_volant_se_tourne_et_se_recentre
        out.volant = (function () {
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
        })();
        ranger();
        // test_le_frein_a_main_fait_deriver
        out.freinMain = (function () {
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
        })();
        ranger();
        return out;
    }""")


def test_le_cercle_d_un_char_ne_grandit_pas_avec_sa_vitesse(physique, paquet):
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
    r = physique["cercle"]
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


def test_le_volant_se_tourne_et_se_recentre(physique):
    """⚠️ La direction passait de 0 à 1 en une image : au clavier, chaque appui
    était un coup de butée à butée. Le volant prend, et il se recentre quand on
    lâche — c'est ce qui fait qu'une courbe est une courbe."""
    r = physique["volant"]
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
        L.Hud.ouvrirOnglet('options');
        const ligne = function () { return L.B.menu.items.find(function (i) { return i.libelle === 'VOLANT EN MARCHE ARRIÈRE'; }); };
        const avant = { detail: ligne().detail, option: L.B.options.reculCommeEnAvant };
        ligne().faire(ligne());
        const apres = { detail: ligne().detail, option: L.B.options.reculCommeEnAvant,
                        sauvee: JSON.parse(o.store[L.Sauvegarde.CLE_OPTIONS]).reculCommeEnAvant };
        // Rouvrir les options : la ligne dit ce qui est choisi, pas le defaut.
        o.tape('ArrowRight', 2); o.tape('ArrowLeft', 2);
        const rouvert = ligne().detail;
        ligne().faire(ligne());
        return { avant: avant, apres: apres, rouvert: rouvert, retour: { detail: ligne().detail, option: L.B.options.reculCommeEnAvant } };
    }""")
    assert r["avant"] == {"detail": "COMME UNE AUTO", "option": False}, "par défaut, rien ne doit changer : %s" % r
    assert r["apres"] == {"detail": "COMME EN AVANT", "option": True, "sauvee": True}, r
    assert r["rouvert"] == "COMME EN AVANT", r
    assert r["retour"] == {"detail": "COMME UNE AUTO", "option": False}, r


def test_un_char_pivote_sur_son_arriere_pas_sur_son_nombril(physique):
    """⚠️ En tournant autour de son centre, le char balayait son coffre dans le
    mur derrière lui, et le nez ne « rentrait » jamais dans le virage. Le juge
    mesure les deux bouts : dans un quart de tour, le nez parcourt plus de
    chemin que le train arrière."""
    r = physique["pivot"]
    assert r["images"] < 600, "le char n'a pas bouclé son quart de tour : %s" % r
    assert r["nez"] > r["cul"], (
        "le nez et le coffre parcourent le même chemin : le char pivote sur son nombril (%s)" % r
    )


def test_le_frein_a_main_fait_deriver(physique):
    r = physique["freinMain"]
    assert r["avec"] > r["sans"] * 1.3, f"la derive au frein a main ({r['avec']:.2f}) ne depasse pas la conduite normale ({r['sans']:.2f})"


def test_un_mur_fait_mal_mais_ne_se_traverse_pas(banc):
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        // ⚠️ La rue la plus au nord de la CARTE (au-dessus de la bande nord), pas de la ville d'avant.
        const j = L.B.joueur, d = o.ligneDroite(true);
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
