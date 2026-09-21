"""Les machines distributrices et l'hopital, cote navigateur : on achete, la
spirale garde la canette, on brasse, la machine cede et crache sa monnaie ; a
l'hopital, les malades restent couches et les patients restent assis ; et quand
on tombe, on se reveille dans un de ses lits."""

from app import economie, magasins

FICHE = economie.DISTRIBUTRICE


def test_on_achete_a_la_machine_la_canette_reste_prise_et_on_brasse(banc, paquet):
    tarifs = paquet["economie"]["tarifs"]
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const j = L.B.joueur, p = L.B.partie;
        // Une machine a liqueur sans kiosque ni homme-sandwich a portee :
        // ACTION ne doit parler qu'a elle.
        const d = L.B.entites.find(function (e) {
            return e.type === 'decor' && e.decor === 'distributrice_liqueur'
                && !L.Entites.autour(e.x, e.y, 60, function (q) { return q.type === 'ambulant' || q.metier; }).length;
        });
        if (!d) return { pasDeMachine: true };
        j.x = d.x; j.y = d.y + 14; L.Monde.centrerCamera(j.x, j.y); L.Entites.indexer();
        // ⚠️ On regarde la machine : ACTION n'agit que sur ce qu'on regarde (test_regard_js.py).
        o.viser(d);
        L.Missions.majInvite(j);
        const invite = L.B.invite;
        p.argent = 100; j.vie = 50; j.endurance = 10; j.surplus = 0;
        const rng = L.B.rng;
        L.B.rng = function () { return 0.99; };                 // la canette tombe
        L.Missions.interagir(j);
        const menu = L.B.menu;
        if (!menu) { L.B.rng = rng; return { pasDeMenu: true, invite: invite }; }
        const titre = menu.titre;
        const libelles = menu.items.map(function (i) { return i.libelle; });
        const fermeServi = menu.items[0].faire();
        const servi = { argent: p.argent, vie: j.vie, souffle: j.endurance };
        L.B.menu = null;
        // La deuxieme reste prise dans la spirale : on a paye, rien ne vient.
        L.B.rng = function () { return 0.0; };
        const m = L.Missions.distributriceSousLaMain(j);
        const fermePris = L.Missions.menuDistributrice(m).items[0].faire();
        const pris = { argent: p.argent, vie: j.vie };
        L.Missions.majInvite(j);
        const inviteBrasser = L.B.invite;
        // Une secousse qui ne suffit pas...
        L.B.rng = function () { return 0.99; };
        L.Missions.interagir(j);
        const menuApresSecousse = !!L.B.menu;
        L.Missions.majInvite(j);
        const encore = L.B.invite;
        // ... puis celle qui la fait tomber : on la boit.
        const vieAvant = j.vie;
        L.B.rng = function () { return 0.0; };
        L.Missions.interagir(j);
        L.Missions.majInvite(j);
        const tombe = { invite: L.B.invite, vie: j.vie - vieAvant, argent: p.argent };
        // Et la nuit, le livreur vide ce qui est reste pris.
        L.Missions.menuDistributrice(m).items[0].faire();
        const priseAvantLaNuit = !!(L.B.coincees && L.B.coincees[m.cle]);
        L.Missions.nouveauJour();
        L.B.rng = rng;
        L.Missions.majInvite(j);
        return { invite: invite, titre: titre, libelles: libelles, fermeServi: fermeServi, servi: servi,
                 fermePris: fermePris, pris: pris, inviteBrasser: inviteBrasser, menuApresSecousse: menuApresSecousse,
                 encore: encore, tombe: tombe, priseAvantLaNuit: priseAvantLaNuit, matin: L.B.invite };
    }""")
    assert not r.get("pasDeMachine"), "la ville n'a pas de machine a liqueur loin des kiosques"
    assert not r.get("pasDeMenu"), r
    nom = magasins.DISTRIBUTRICES["liqueur"]["nom"].upper()
    assert r["invite"] == nom
    assert r["titre"] == nom
    assert r["libelles"] == [a["nom"].upper() for a in magasins.DISTRIBUTRICES["liqueur"]["articles"]]
    assert r["fermeServi"] is False, "le menu se ferme apres une canette servie"
    assert r["servi"]["argent"] == 100 - tarifs["liqueur"]
    assert r["servi"]["vie"] == 50 + tarifs["liqueur_pv"]
    assert r["servi"]["souffle"] == 10 + tarifs["liqueur_souffle"]
    assert r["fermePris"] is True, "une canette prise doit fermer le menu : il y a une machine a brasser"
    assert r["pris"]["argent"] == 100 - 2 * tarifs["liqueur"], "la spirale ne prend pas l'argent"
    assert r["pris"]["vie"] == r["servi"]["vie"], "une canette restee prise a quand meme ete bue"
    assert r["inviteBrasser"] == "BRASSER LA MACHINE"
    assert r["menuApresSecousse"] is False, "brasser ouvre le menu au lieu de secouer"
    assert r["encore"] == "BRASSER LA MACHINE"
    assert r["tombe"]["invite"] == nom and r["tombe"]["vie"] == tarifs["liqueur_pv"]
    assert r["tombe"]["argent"] == r["pris"]["argent"], "brasser ne coute rien"
    assert r["priseAvantLaNuit"] is True
    assert r["matin"] == nom, "une canette prise a survecu a la nuit"


def test_une_machine_defoncee_crache_sa_monnaie_et_ses_canettes(banc, paquet):
    tarifs = paquet["economie"]["tarifs"]
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        L.graine(11);
        const j = L.B.joueur, p = L.B.partie;
        const d = L.B.entites.find(function (e) { return e.type === 'decor' && e.decor === 'distributrice_liqueur'; });
        if (!d) return { pasDeMachine: true };
        // La berline la couche : une machine n'est pas un guichet blinde.
        j.x = d.x + 200; j.y = d.y + 200; L.Monde.centrerCamera(j.x, j.y);
        const auto = L.Vehicules.creer('auto', d.x, d.y + 6, -Math.PI / 2, { etat: 'stationne' });
        auto.vitesse = 4; auto.vx = 0; auto.vy = -4;
        L.Entites.indexer();
        const devant = L.Vehicules.decorDevant(auto, auto.x, auto.y);
        const passe = L.Vehicules.heurterDecor(auto, auto.x, auto.y);
        L.Entites.retirer(auto);
        const tas = L.B.entites.filter(function (e) { return e.type === 'ramassage' && e.objet === 'monnaie'; });
        const canettes = L.B.entites.filter(function (e) { return e.type === 'ramassage' && e.objet === 'canette'; });
        const total = tas.reduce(function (s, e) { return s + e.montant; }, 0);
        const crimes = L.B.crimes.filter(function (c) { return c.type === 'distributrice'; });
        const sud = tas.concat(canettes).every(function (e) { return e.y > d.y; });
        // On passe sur une canette : on la boit.
        j.endurance = 10; j.surplus = 0;
        j.x = canettes[0] ? canettes[0].x : j.x; j.y = canettes[0] ? canettes[0].y : j.y;
        L.Entites.indexer();
        const argentAvant = p.argent;
        L.Missions.maj();
        const bu = j.endurance + (j.surplus || 0) - 10;
        const restent = L.B.entites.filter(function (e) { return e.type === 'ramassage' && (e.objet === 'monnaie' || e.objet === 'canette'); });
        const parTerre = restent.filter(function (e) { return e.objet === 'monnaie'; }).reduce(function (s, e) { return s + e.montant; }, 0);
        // ⚠️ Les canettes tombent serrees : d'un pas, on en boit une ou deux.
        const bues = canettes.filter(function (e) { return restent.indexOf(e) < 0; }).map(function (e) { return e.article; });
        // Defoncee, elle ne vend plus rien ; au matin, elle est debout.
        j.x = d.x; j.y = d.y + 14; L.Entites.indexer();
        o.viser(d);                                            // on la regarde (test_regard_js.py)
        const brisee = !!d.brise, machine = L.Missions.distributriceSousLaMain(j);
        L.Missions.nouveauJour();
        L.Entites.indexer();
        return { devant: devant && devant.quoi, passe: passe, brisee: brisee, machineBrisee: !!machine,
                 tas: tas.length, canettes: canettes.length, total: total, crimes: crimes.length,
                 temoin: crimes[0] ? crimes[0].temoin : null, sud: sud, bu: bu, bues: bues,
                 empoche: p.argent - argentAvant, parTerre: parTerre,
                 matin: !d.brise && !!L.Missions.distributriceSousLaMain(j) };
    }""")
    assert not r.get("pasDeMachine")
    assert r["devant"] == "casse" and r["passe"] is True, "une berline doit coucher une machine"
    assert r["brisee"] is True and r["machineBrisee"] is False, "une machine defoncee vend encore"
    assert r["tas"] == FICHE["tas"]
    assert FICHE["monnaie"][0] <= r["total"] <= FICHE["monnaie"][1]
    assert r["canettes"] == FICHE["canettes"]
    assert r["sud"] is True, "la machine crache dans le mur"
    assert r["crimes"] == 1 and r["temoin"] is True, "defoncer une machine est un petit delit a temoin"
    assert r["bues"], "la canette par terre ne se boit pas"
    assert r["bu"] == sum(tarifs[a + "_souffle"] for a in r["bues"]), r
    # Ce qu'on a ramasse d'un pas, plus ce qui reste par terre, fait la monnaie.
    assert r["empoche"] + r["parTerre"] == r["total"]
    assert r["matin"] is True, "la machine n'est pas revenue au matin"


def test_a_l_hopital_les_malades_restent_couches_et_les_patients_assis(banc):
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const j = L.B.joueur, c = L.Monde.carte;
        const porte = c.portes.find(function (p) { return p.interieur === 'hopital'; });
        j.x = porte.x * L.TT + 8; j.y = (porte.y + 1) * L.TT + 10;
        o.entrer(porte);
        function recensement() {
            const gens = L.B.entites.filter(function (e) { return e.type === 'pieton'; });
            const couches = gens.filter(function (e) { return e.face === 'alite'; });
            return {
                slug: L.B.interieur.slug,
                malades: couches.length,
                poses: couches.map(function (e) { return L.Entites.imageDe(e).pose; }),
                jaquettes: couches.filter(function (e) { return e.arch === 'malade'; }).length,
                tetes: Object.keys(couches.reduce(function (t, e) { t[e.swaps.h + e.swaps.s] = 1; return t; }, {})).length,
                assis: gens.filter(function (e) { return e.face === 'assis_bas'; }).length,
                soignantes: gens.filter(function (e) { return e.arch === 'soignante'; }).length,
                places: gens.filter(function (e) { return e.etat === 'fige'; })
                    .map(function (e) { return [Math.round(e.x), Math.round(e.y), e.face]; }),
                lits: couches.map(function (e) { return L.Monde.glyphe(Math.floor(e.x / L.TT), Math.floor(e.y / L.TT)); }),
            };
        }
        const urgence = recensement();
        o.frame(300);
        const apres = recensement();
        // La machine a cafe de la salle d'attente, de la tuile d'a cote.
        const point = L.B.interieur.points.find(function (p) { return p.type === 'distributrice' && p.sorte === 'cafe'; });
        j.x = (point.x - 1) * L.TT + 8; j.y = point.y * L.TT + 8;
        // ⚠️ On regarde la machine : ACTION n'agit que sur ce qu'on regarde (test_regard_js.py).
        o.viser({ x: (point.x + 0.5) * L.TT, y: (point.y + 0.5) * L.TT });
        L.Missions.majInvite(j);
        const invite = L.B.invite;
        L.Missions.utiliserPoint(j);
        const titre = L.B.menu ? L.B.menu.titre : null;
        L.B.menu = null;
        // L'etage des soins.
        const escalier = L.B.interieur.points.find(function (p) { return p.type === 'escalier'; });
        j.x = escalier.x * L.TT + 8; j.y = escalier.y * L.TT + 8;
        L.Missions.utiliserPoint(j);
        o.fondu();
        const soins = recensement();
        return { urgence: urgence, apres: apres, invite: invite, titre: titre, soins: soins };
    }""")
    cafe = magasins.DISTRIBUTRICES["cafe"]["nom"].upper()
    u, s = r["urgence"], r["soins"]
    assert u["slug"] == "hopital" and s["slug"] == "hopital_soins", (u["slug"], s["slug"])
    assert u["malades"] >= 1 and s["malades"] >= 6, (u["malades"], s["malades"])
    assert set(u["poses"] + s["poses"]) == {"alite"}, "un malade dessine debout"
    assert s["jaquettes"] == s["malades"], "un malade sans sa jaquette"
    assert s["tetes"] >= 3, "six malades avec la meme tete"
    assert set(u["lits"] + s["lits"]) == {"r"}, "un malade couche ailleurs que dans un lit d'hopital"
    assert u["assis"] >= 5, u
    assert u["soignantes"] >= 1 and s["soignantes"] >= 1, "personne en blouse"
    # ⚠️ Trois cents images plus tard, personne ne s'est leve ni retourne.
    assert r["apres"]["places"] == u["places"], "un malade ou un patient a bouge"
    assert r["invite"] == cafe and r["titre"] == cafe


# --- Le reveil a l'hopital : dans un lit ----------------------------------------------

#: La porte de l'hopital dans la ville, et le pas devant elle — la ou l'on ressort.
PORTE_HOPITAL = """
        const porte = L.Monde.carte.portes.find(function (p) { return p.lieu === 'hopital' && p.interieur; });
        const devant = [porte.x * L.TT + 8, (porte.y + 1) * L.TT + 10];
"""


def test_on_se_reveille_couche_dans_un_lit_de_l_hopital(banc):
    """Martin : « pour le reveil a l'hopital, je veux qu'on se reveille a
    l'interieur et dans un lit, couche, des le premier deplacement on se leve et
    on peut partir. »

    On se reveillait DEHORS, sur le trottoir devant la porte. Ce juge tient le
    lit : la piece est l'hopital, le joueur est dans la tuile de TETE d'un lit
    d'hopital, dessine couche (`alite`) et droit — le coup qui l'a mis a terre
    le laissait penche de 0,22 rad —, seul dans ce lit (le malade de l'urgence
    lui a cede sa place), sans clignoter, et la porte d'en bas mene devant
    l'hopital. ⚠️ Et RIEN d'autre que le stick ne le sort du lit : ni FRAPPE, ni
    SPRINT, ni ACTION, ni cinq secondes a attendre."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const j = L.B.joueur, T = L.TT;""" + PORTE_HOPITAL + """
        L.B.partie.argent = 400;
        L.Entites.blesser(j, 9999, null, {});
        o.fondu();
        const tx = Math.floor(j.x / T), ty = Math.floor(j.y / T);
        const reveil = {
            piece: L.B.interieur && L.B.interieur.slug,
            lit: L.Monde.glyphe(tx, ty), tete: L.Monde.glyphe(tx, ty - 1) !== 'r',
            pose: L.Entites.imageDe(j).pose, penche: L.Entites.pose(j).rot,
            ombre: L.Entites.imageDe(j).pose === 'alite' && !!j.alite,
            partage: L.B.entites.filter(function (e) {
                return e !== j && e.alite && Math.floor(e.x / T) === tx && Math.floor(e.y / T) === ty;
            }).length,
            clignote: j.invincible > 0,
            dehors: L.B.exterieur ? [L.B.exterieur.x, L.B.exterieur.y] : null, devant: devant,
            vie: j.vie, max: j.vieMax, argent: L.B.partie.argent,
        };
        // Chaque geste se guette IMAGE PAR IMAGE : le poing part au relacher et il
        // est fini en trente images — lu apres coup, il n'a jamais existe.
        const x0 = j.x, y0 = j.y, gestes = {};
        for (const [touche, nom] of [['Space', 'frappe'], ['ShiftLeft', 'sprint'], ['KeyE', 'action']]) {
            const vu = { attaque: false, charge: false, roule: false, menu: false, fondu: false };
            o.touche(touche);
            for (let i = 0; i < 40; i++) {
                if (i === 10) o.relacher(touche);
                o.frame(1);
                vu.attaque = vu.attaque || j.etat === 'attaque';
                vu.charge = vu.charge || j.charge > 0;
                vu.roule = vu.roule || j.roule > 0;
                vu.menu = vu.menu || !!L.B.menu;
                vu.fondu = vu.fondu || !!L.B.transition;
            }
            gestes[nom] = vu;
        }
        o.frame(120);
        const reste = { bouge: Math.hypot(j.x - x0, j.y - y0), alite: !!j.alite, gestes: gestes,
                        pose: L.Entites.imageDe(j).pose, piece: L.B.interieur && L.B.interieur.slug };
        // Un passant qui passe PAR le lit (un meuble ne l'arrete pas) se cogne
        // au dormeur : c'est lui qui s'ecarte.
        const intrus = o.poser('flaneur', 3, 0);
        intrus.etat = 'flane';
        o.frame(30);
        reste.bouscule = Math.hypot(j.x - x0, j.y - y0);
        return { reveil: reveil, reste: reste };
    }""")
    v = r["reveil"]
    assert v["piece"] == "hopital", "on ne se reveille pas DANS l'hopital : %s" % v
    assert v["lit"] == "r" and v["tete"], "on ne se reveille pas dans la tuile de tete d'un lit : %s" % v
    assert v["pose"] == "alite" and v["penche"] == 0, "on ne se reveille pas couche, droit : %s" % v
    assert v["partage"] == 0, "le malade est reste dans le lit avec nous : %s" % v
    assert not v["clignote"], "un corps qui clignote sous sa couverture : %s" % v
    assert v["dehors"] == v["devant"], "la porte de la piece ne mene pas devant l'hopital : %s" % v
    assert v["vie"] == v["max"] and v["argent"] < 400, "le reveil ne soigne pas ou ne facture pas : %s" % v
    s = r["reste"]
    assert s["alite"] and s["pose"] == "alite" and s["bouge"] == 0, (
        "frapper, sprinter, ACTION ou attendre a sorti le joueur du lit : %s" % s
    )
    assert s["bouscule"] == 0, "un passant a pousse le joueur hors de son lit : %s" % s
    for nom, g in s["gestes"].items():
        assert not any(g.values()), (
            "%s part depuis le lit : %s" % (nom, g)
        )
    assert s["piece"] == "hopital", s


def test_la_premiere_poussee_leve_a_cote_du_lit_et_on_ressort_devant_l_hopital(banc):
    """« Des le premier deplacement on se leve et on peut partir. »

    ⚠️ Un meuble n'arrete personne : se lever sur place, c'etait se tenir DEBOUT
    SUR L'OREILLER et quitter le lit en marchant sur la couverture. La poussee
    choisit son cote — vers le bas, le pied du lit ; a gauche, le flanc gauche ;
    a droite, le droit — et on marche dans la meme image. Puis ACTION a la porte
    d'en bas : on est dans la rue, devant l'hopital."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const j = L.B.joueur, T = L.TT;""" + PORTE_HOPITAL + """
        L.Entites.blesser(j, 9999, null, {});
        o.fondu();
        const lit = { x: Math.floor(j.x / T), y: Math.floor(j.y / T) };
        const cotes = {};
        for (const [touche, sens] of [['KeyS', 'bas'], ['KeyA', 'gauche'], ['KeyD', 'droite']]) {
            L.Entites.coucher(j, lit.x, lit.y);
            const y0 = j.y;
            o.touche(touche); o.frame(1);
            const tx = Math.floor(j.x / T), ty = Math.floor(j.y / T);
            cotes[sens] = { alite: !!j.alite, pose: L.Entites.imageDe(j).pose, dx: tx - lit.x, dy: ty - lit.y,
                            meuble: L.Monde.estMeuble(tx, ty), plancher: !L.Monde.bloque(tx, ty, L.Monde.MASQUE_PIETON) };
            const x1 = j.x, y1 = j.y;
            o.frame(15); o.relacher(touche); o.frame(1);
            cotes[sens].marche = Math.round(Math.hypot(j.x - x1, j.y - y1));
        }
        const sortie = L.B.interieur.sortie;
        j.x = sortie.x * T + 8; j.y = (sortie.y - 1) * T + 8; j.face = 'bas';
        L.Entites.indexer();
        o.tape('KeyE', 2);
        o.fondu();
        return { cotes: cotes, sorti: !L.B.interieur,
                 loin: Math.hypot(j.x - devant[0], j.y - devant[1]) };
    }""")
    c = r["cotes"]
    # Du cote ou l'on pousse, colle au lit : au flanc (une colonne a cote) ou au
    # pied (la meme colonne, plus bas que la tete).
    cote = {"bas": lambda dx, dy: dx == 0 and dy > 0,
            "gauche": lambda dx, dy: dx == -1, "droite": lambda dx, dy: dx == 1}
    for sens, bon in cote.items():
        v = c[sens]
        assert not v["alite"] and v["pose"] != "alite", "pousser vers %s ne leve pas : %s" % (sens, v)
        assert bon(v["dx"], v["dy"]), "pousser vers %s ne leve pas de ce cote : %s" % (sens, v)
        assert v["plancher"] and not v["meuble"], "on se leve sur un meuble ou dans un mur : %s" % v
        assert v["marche"] > 8, "debout, on ne marche pas vers %s : %s" % (sens, v)
    assert r["sorti"] is True and r["loin"] < 4, "on ne ressort pas devant l'hopital : %s" % r


def test_tomber_dans_une_piece_reveille_quand_meme_a_l_hopital(banc):
    """⚠️ `Monde.entrer` part de la VILLE. Tomber dans une piece (ici la planque)
    et charger l'hopital par-dessus perdait le chemin du retour : on doit se
    reveiller dans le lit de l'hopital, et ressortir devant L'HOPITAL, dans la
    vraie ville — pas devant la planque, pas dans une piece fantome."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const j = L.B.joueur, T = L.TT;""" + PORTE_HOPITAL + """
        const planque = L.Monde.carte.portes.find(function (p) { return p.lieu === 'planque' && p.interieur; });
        j.x = planque.x * T + 8; j.y = (planque.y + 1) * T + 10;
        o.entrer(planque);
        const avant = L.B.interieur && L.B.interieur.slug;
        L.Entites.blesser(j, 9999, null, {});
        o.fondu();
        const reveil = { piece: L.B.interieur && L.B.interieur.slug, alite: !!j.alite,
                         dehors: L.B.exterieur ? [L.B.exterieur.x, L.B.exterieur.y] : null };
        L.Entites.seLever(j, 0, 1);
        o.sortir();
        return { avant: avant, reveil: reveil, devant: devant, sorti: !L.B.interieur && !L.Monde.carte.interieur,
                 decor: L.B.entites.filter(function (e) { return e.type === 'decor'; }).length, large: L.Monde.carte.w,
                 loin: Math.hypot(j.x - devant[0], j.y - devant[1]) };
    }""")
    assert r["avant"] and r["avant"] != "hopital", "le juge ne tombe pas dans une autre piece : %s" % r
    assert r["reveil"]["piece"] == "hopital" and r["reveil"]["alite"], r["reveil"]
    assert r["reveil"]["dehors"] == r["devant"], "la piece ne mene pas devant l'hopital : %s" % r
    assert r["sorti"] and r["decor"] > 0 and r["large"] > 100, (
        "on ressort dans une piece fantome, pas dans la ville : %s" % r
    )
    assert r["loin"] < 4, "on ressort ailleurs que devant l'hopital : %s" % r
