"""Les sons des armes — un par arme, et ceux d'autour (a vide, casse, degainer).

⚠️ Jusqu'au 13 sept. 2026, `majAttaque` et `tirer` appelaient `SFX.coup` pour
tout le monde : la batte, le couteau, le pistolet et le fusil faisaient un coup
de poing. Ces juges regardent QUEL effet le combat demande, en remplacant les
effets par des compteurs — le banc n'a ni oreille ni AudioContext, et c'est
justement ce qui rend la question nette : on ne juge pas le son, on juge que
le combat demande le bon.
"""


def _espion(effets):
    """Le JS qui remplace chaque effet nomme par un compteur, dans `compte`."""
    return "const compte = {}; " + "".join(
        f"L.Son.SFX.{e} = function () {{ compte.{e} = (compte.{e} || 0) + 1; }}; " for e in effets)


def test_une_batte_ne_fait_pas_un_coup_de_poing(banc):
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        """ + _espion(["coup", "batte"]) + """
        const j = L.B.joueur;
        L.B.partie.armes.batte = { mun: null, usure: 0 }; j.arme = 'batte';
        L.Combat.frapper(j, false);
        for (let i = 0; i < 40; i++) { L.Entites.indexer(); L.Combat.maj(); }
        return compte;
    }""")
    assert r.get("batte") == 1, r
    assert not r.get("coup"), "la batte a fait un coup de poing"


def test_les_poings_font_toujours_le_coup_de_poing(banc):
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        """ + _espion(["coup"]) + """
        L.Combat.frapper(L.B.joueur, false);
        for (let i = 0; i < 40; i++) { L.Entites.indexer(); L.Combat.maj(); }
        return compte;
    }""")
    assert r.get("coup") == 1, r


def test_le_pistolet_tire_et_clique_a_vide(banc):
    """Le coup de feu, puis — chargeur vide — un clic sec, pas le buzzer des
    menus : celui-la faisait croire que le bouton etait casse."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        """ + _espion(["coup", "pistolet", "vide", "erreur"]) + """
        const j = L.B.joueur;
        L.B.partie.armes.pistolet = { mun: 1, usure: 0 }; j.arme = 'pistolet';
        const tire = L.Combat.frapper(j, false);
        j.etat = 'flane'; j.phase = null;            // la cadence ne nous retient pas
        const aVide = L.Combat.frapper(j, false);
        return { tire: tire, aVide: aVide, mun: L.B.partie.armes.pistolet.mun, compte: compte };
    }""")
    assert r["tire"] is True and r["aVide"] is False
    assert r["mun"] == 0
    assert r["compte"].get("pistolet") == 1
    assert r["compte"].get("vide") == 1, "la gachette a vide doit cliquer"
    assert not r["compte"].get("coup") and not r["compte"].get("erreur")


def test_un_policier_qui_tire_fait_un_coup_de_feu(banc):
    """Le meme chemin pour les PNJ : `Combat.tirer(agent, pistolet)`."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        """ + _espion(["coup", "pistolet"]) + """
        const agent = o.poser('policier', 40, 0);
        L.Combat.tirer(agent, L.Combat.armeDef('pistolet'));
        return compte;
    }""")
    assert r.get("pistolet") == 1 and not r.get("coup"), r


def test_une_arme_de_fortune_casse_en_le_disant(banc):
    """Chaque coup de cone fait un bruit de cone, et la casse fait une casse —
    pas le buzzer de refus."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        """ + _espion(["cone", "casse", "erreur", "coup"]) + """
        const j = L.B.joueur;
        L.Combat.ramasserArme('cone', null); j.arme = 'cone';
        const def = L.Combat.armeDef('cone');
        for (let coup = 0; coup < def.usures; coup++) {
            const cible = o.poser('ouvrier', 12, 0);
            cible.vie = 999; cible.vieMax = 999;
            o.viser(cible);
            L.Combat.frapper(j, false);
            for (let i = 0; i < 40; i++) { L.Entites.indexer(); L.Combat.maj(); }
            L.Entites.retirer(cible);
        }
        return { usures: def.usures, casse: !L.B.partie.armes.cone, arme: j.arme, compte: compte };
    }""")
    assert r["casse"] is True and r["arme"] == "poings"
    assert r["compte"].get("cone") == r["usures"]
    assert r["compte"].get("casse") == 1
    assert not r["compte"].get("erreur") and not r["compte"].get("coup")


def test_changer_d_arme_degaine(banc):
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        """ + _espion(["menu", "degainer"]) + """
        const j = L.B.joueur;
        L.B.partie.armes.batte = { mun: null, usure: 0 };
        L.Combat.cycler(j);
        return { arme: j.arme, compte: compte };
    }""")
    assert r["arme"] == "batte"
    assert r["compte"].get("degainer") == 1 and not r["compte"].get("menu")


def test_le_jet_de_l_extincteur_s_entend_tant_qu_il_sort(banc):
    """`SFX.jet(actif)` recoit la verite a chaque image : vrai tant que le
    bouton est tenu et qu'il reste de la poudre, faux des qu'on lache."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const jets = [];
        L.Son.SFX.jet = function (actif) { jets.push(!!actif); };
        const j = L.B.joueur;
        L.B.partie.armes.extincteur = { mun: 30, usure: 0 }; j.arme = 'extincteur'; L.B.partie.arme = 'extincteur';
        o.frame(2);
        const avant = jets.slice();
        o.touche('KeyJ'); o.frame(12);
        const tenu = jets.slice(avant.length);
        o.relacher('KeyJ'); o.frame(4);
        const lache = jets.slice(avant.length + tenu.length);
        return { avant: avant, tenu: tenu, lache: lache, mun: L.B.partie.armes.extincteur.mun };
    }""")
    assert r["avant"] and not any(r["avant"]), "sans bouton, pas de jet"
    assert r["tenu"][-1] is True and r["tenu"].count(True) >= 8, r["tenu"]
    assert r["lache"][-1] is False, "bouton lache, le jet doit se taire"
    assert r["mun"] < 30, "le jet n'a pas depense de poudre"


def test_le_jet_tourne_en_boucle_ou_souffle_par_a_coups(banc):
    """Avec l'echantillon : UNE boucle, allumee puis eteinte — pas un depart par
    image. Sans lui : le filet, un souffle court par a-coups."""
    r = banc("""async function (L, o) {
        o.brancherAudio(true);
        L.Son.reveiller();
        await o.attendre(); await o.attendre(); await o.attendre();
        L.Jeu.commencer();
        let souffles = 0;
        const vrai = L.Son.SFX.extincteur;
        L.Son.SFX.extincteur = function () { souffles++; return vrai(); };
        const j = L.B.joueur;
        L.B.partie.armes.extincteur = { mun: 60, usure: 0 }; j.arme = 'extincteur'; L.B.partie.arme = 'extincteur';
        const charge = L.Son.estCharge('extincteur');
        o.touche('KeyJ'); o.frame(30);
        const pendant = L.Son.boucleActive('extincteur');
        o.relacher('KeyJ'); o.frame(4);
        return { charge: charge, pendant: pendant, apres: L.Son.boucleActive('extincteur'), souffles: souffles };
    }""")
    if r["charge"]:
        assert r["pendant"] is True and r["apres"] is False
        assert r["souffles"] == 0, "avec la boucle, pas de souffle par a-coups"
    else:
        assert r["souffles"] >= 3, "sans echantillon, le filet doit souffler"
        assert r["pendant"] is False


# --- Les armes a feu du marche noir (14 sept. 2026) -----------------------------------


def test_la_mitraillette_tire_tant_qu_on_tient_et_s_arrete_a_vide(banc):
    """Automatique : on TIENT, et la cadence rythme la rafale — une balle par
    coup, jamais plus, et le chargeur vide arrete tout sans cliquer soixante
    fois par seconde. La dispersion s'ouvre tant qu'on tient et se referme
    des qu'on lache : c'est ce qui fait de la rafale courte un choix."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        """ + _espion(["mitraillette", "vide"]) + """
        const j = L.B.joueur, def = L.Combat.armeDef('mitraillette');
        j.intouchable = true;
        L.B.partie.armes.mitraillette = { mun: 8, usure: 0 }; j.arme = 'mitraillette'; L.B.partie.arme = 'mitraillette';
        const dispersions = [];
        o.touche('KeyJ');
        for (let i = 0; i < 90; i++) { dispersions.push(L.Combat.dispersionDe(j, def)); o.frame(1); }
        const tenu = { coups: compte.mitraillette || 0, vide: compte.vide || 0, mun: L.B.partie.armes.mitraillette.mun,
                       rafale: j.rafale, debut: dispersions[0], fin: dispersions[dispersions.length - 1] };
        o.relacher('KeyJ'); o.frame(3);
        return { def: { cadence: def.cadence, dispersion: def.dispersion, max: def.dispersion_max },
                 tenu: tenu, lache: { rafale: j.rafale, dispersion: L.Combat.dispersionDe(j, def) } };
    }""")
    assert r["tenu"]["coups"] == 8 and r["tenu"]["mun"] == 0, r
    assert r["tenu"]["vide"] <= 1, "a vide, la gachette tenue ne doit pas cliquer a chaque image"
    assert r["tenu"]["debut"] == r["def"]["dispersion"], "le premier coup part serre"
    assert r["tenu"]["fin"] == r["def"]["max"], "tenue trois quarts de seconde, la rafale est grande ouverte"
    assert r["lache"]["rafale"] == 0 and r["lache"]["dispersion"] == r["def"]["dispersion"], "lacher referme"


def test_un_coup_de_feu_s_entend_sans_etre_vu(banc):
    """La parade au tireur embusque : un agent qui te TOURNE LE DOS, hors de
    son cone, entend la carabine et part voir — sans etoile, il n'a rien vu.
    La fronde ne s'entend pas, et a trente tuiles on est hors du rayon. La
    distance achete du temps, pas l'impunite."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const j = L.B.joueur;
        // Personne d'autre dans la rue : on juge l'ouie, pas les temoins.
        L.B.entites.filter(function (e) { return e.type === 'pieton'; }).forEach(L.Entites.retirer);
        const car = L.Combat.armeDef('carabine'), fronde = L.Combat.armeDef('fronde');
        const a = L.Police.creerAgent(j.x + 12 * L.TT, j.y, 'flane');
        L.Entites.regarder(a, 1, 0);                       // il regarde AILLEURS
        L.Entites.indexer();
        L.B.partie.armes.carabine = { mun: 5, usure: 0 }; L.B.partie.armes.fronde = { mun: 30, usure: 0 };
        const voit = L.Police.voit(a, j.x, j.y, 'policier');
        L.Combat.tirer(j, car);
        const carabine = { etat: a.etat, but: a.but ? Math.hypot(a.but.x - j.x, a.but.y - j.y) : null, etoiles: L.B.recherche.etoiles };
        a.etat = 'flane'; a.but = null; j.etat = 'flane'; j.phase = null;
        L.Combat.tirer(j, fronde);
        const apresFronde = { etat: a.etat, etoiles: L.B.recherche.etoiles };
        const loin = L.Police.creerAgent(j.x + 30 * L.TT, j.y, 'flane');
        L.Entites.regarder(loin, 1, 0); L.Entites.indexer();
        j.etat = 'flane'; j.phase = null;
        L.Combat.tirer(j, car);
        return { voit: voit, bruit: car.bruit, carabine: carabine, fronde: apresFronde, loin: loin.etat };
    }""")
    assert r["voit"] is False, "l'agent tourne le dos : il ne doit rien voir"
    assert 12 < r["bruit"] < 30, r["bruit"]
    assert r["carabine"]["etat"] == "enquete" and r["carabine"]["but"] < 2, "il a entendu : il vient voir d'ou ca venait"
    assert r["carabine"]["etoiles"] == 0, "entendu, pas vu : aucune etoile"
    assert r["fronde"]["etat"] == "flane", "la fronde ne s'entend pas"
    assert r["loin"] == "flane", "a trente tuiles, hors du rayon"


def test_le_molotov_laisse_une_flaque_qui_brule_puis_s_eteint(banc):
    """La bouteille part en cloche et, la ou elle casse, le feu mord `feu_s`
    secondes puis S'ETEINT — un seul brasier, jamais deux. Un passant qui y
    reste meurt, et c'est une mort DU JOUEUR : `mort_pieton` est signale,
    sinon on tue sans etoiles. Et la bouteille s'entend quand elle CASSE,
    pas quand elle part."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        """ + _espion(["molotov"]) + """
        const j = L.B.joueur, def = L.Combat.armeDef('molotov');
        j.intouchable = true;
        const crimes = [];
        const vrai = L.Police.signalerCrime;
        L.Police.signalerCrime = function (type, x, y, vu) { crimes.push(type); return vrai(type, x, y, vu); };
        // Une rue droite : la bouteille ne doit pas casser sur un mur.
        const ligne = o.ligneDroite();
        j.x = ligne.x; j.y = ligne.y;
        const cible = o.poser('ouvrier', 90, 0);
        cible.vie = 40; cible.vieMax = 40; cible.etat = 'assomme'; cible.minuterie = 99999; cible.face = 'couche';
        o.viser(cible);
        L.B.partie.armes.molotov = { mun: 3, usure: 0 }; j.arme = 'molotov'; L.B.partie.arme = 'molotov';
        const brasiers = function () { return L.B.entites.filter(function (e) { return e.type === 'brasier'; }).length; };
        L.Combat.tirer(j, def);
        const depart = { son: compte.molotov || 0, brasiers: brasiers(), mun: L.B.partie.armes.molotov.mun };
        let max = 0, allumeA = -1, mortA = -1, distance = null;
        for (let i = 0; i < def.feu_s * 60 + 120; i++) {
            L.B.t++; L.Entites.indexer(); L.Combat.maj();
            const n = brasiers(); max = Math.max(max, n);
            if (n && allumeA < 0) {
                allumeA = i;
                const f = L.B.entites.find(function (e) { return e.type === 'brasier'; });
                distance = Math.hypot(f.x - cible.x, f.y - cible.y);
            }
            if (!cible.vivant && mortA < 0) mortA = i;
        }
        return { depart: depart, max: max, allumeA: allumeA, mortA: mortA, distance: distance, fin: brasiers(),
                 son: compte.molotov || 0, crimes: crimes, feu_s: def.feu_s };
    }""")
    assert r["depart"]["mun"] == 2 and r["depart"]["brasiers"] == 0 and r["depart"]["son"] == 0, "au lancer, rien ne brule et rien ne casse"
    assert 10 < r["allumeA"] < 60, f"la bouteille doit retomber en moins d'une seconde ({r['allumeA']})"
    assert r["distance"] < 30, "elle casse sur la cible, ou a ses pieds"
    assert r["son"] == 1, "le verre casse une fois, a l'arrivee"
    assert r["max"] == 1, "un brasier, jamais deux : le feu ne se propage pas"
    assert 0 < r["mortA"] < r["feu_s"] * 60, "rester dans le feu tue avant qu'il s'eteigne"
    assert "mort_pieton" in r["crimes"], "une mort dans le feu est une mort du joueur"
    assert r["fin"] == 0, "le feu s'eteint"
