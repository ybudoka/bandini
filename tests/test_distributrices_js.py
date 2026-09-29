"""Les machines distributrices, cote navigateur : on achete, la spirale garde la
canette, on brasse, la machine cede et crache sa monnaie. (L'hopital, lui, se
juge dans `test_hopital_js.py`.)"""

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
