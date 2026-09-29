"""Pas de moto ni de vélo l'hiver, pas de moto sous la pluie, au banc
(docs/jalons/pas-de-moto-ni-de-velo-l-hiver-pas-de-moto-sous-la-pluie.md).

Demande de Martin (29 sept. 2026) : « pas de moto et velo lhiver », « pas de moto durant la
pluie non plus ». La fiche dit quand un char est remisé (`remise`) ; ces juges regardent le
jeu : ce qui naît dans la rue (avec les mêmes dés), ce qui rentre hors champ, la moto du
livreur sous sa bâche, le fuyard en motoneige, ce que disent les répliques et les objectifs,
la berline de livreur, Sven et Le Grand Saut.
"""

# ⚠️ Le jour 1 est le 1er janvier (la neige tient), le jour 21 est en juillet.
HIVER, ETE = 1, 21

DECOR = """
        L.Jeu.commencer();
        const B = L.B, V = L.Vehicules, j = B.joueur;
        // Un jour de PLUIE hors de l'hiver, a l'heure ou il pleut : cherche dans l'annee.
        const pluie = (function () {
            for (let jour = 12; jour <= 36; jour++) for (let k = 0; k < 96; k++) {
                if (L.Pluie.intensiteA(jour, k / 96) > 0.5 && L.Calendrier.saison(jour) !== 'hiver') return { jour: jour, heure: k / 96 };
            }
            return null;
        })();
        const saison = function (quoi) {
            if (quoi === 'pluie') { B.partie.jour = pluie.jour; B.partie.heure = pluie.heure; }
            else { B.partie.jour = quoi; B.partie.heure = 0.5; }
        };
"""


def test_la_regle_suit_la_fiche_la_neige_et_l_averse(banc):
    """`Vehicules.remise` : la moto l'hiver et sous la pluie, le vélo l'hiver seulement, et rien
    pour une berline ; l'été, rien du tout."""
    r = banc("""function (L, o) {""" + DECOR + """
        const out = { pluie: !!pluie };
        ['hiver', 'ete', 'pluie'].forEach(function (q) {
            saison(q === 'hiver' ? """ + str(HIVER) + """ : q === 'ete' ? """ + str(ETE) + """ : 'pluie');
            out[q] = { moto: V.remise('moto'), velo: V.remise('velo'), auto: V.remise('auto'), motoneige: V.remise('motoneige') };
        });
        return out;
    }""")
    assert r["pluie"], "aucune averse dans l'année : le juge ne peut rien dire de la pluie"
    assert r["hiver"] == {"moto": "hiver", "velo": "hiver", "auto": None, "motoneige": None}, r["hiver"]
    assert r["ete"] == {"moto": None, "velo": None, "auto": None, "motoneige": None}, r["ete"]
    assert r["pluie"] == {"moto": "pluie", "velo": None, "auto": None, "motoneige": None}, r["pluie"]


def test_la_rue_n_en_fait_pas_naitre_avec_les_memes_des(banc):
    """`typeDeRue`, balayé sur tout le dé : l'hiver, aucune moto ni aucun vélo (une berline à
    leur place) ; sous la pluie, aucune moto, mais des vélos ; l'été, les deux. Et UN SEUL dé
    par tirage, en toute saison : rien ne glisse derrière."""
    r = banc("""function (L, o) {""" + DECOR + """
        const zone = L.Monde.zoneA(j.x, j.y), rng = B.rng;
        const balayer = function () {
            const vus = {}; let des = 0;
            for (let k = 0; k < 400; k++) {
                const x = (k + 0.5) / 400;
                B.rng = function () { des++; return x; };
                const t = V.typeDeRue(zone, 1);
                vus[t.slug] = (vus[t.slug] || 0) + 1;
            }
            B.rng = rng;
            return { vus: vus, des: des };
        };
        const out = {};
        saison(""" + str(HIVER) + """); out.hiver = balayer();
        saison(""" + str(ETE) + """); out.ete = balayer();
        saison('pluie'); out.pluie = balayer();
        return out;
    }""")
    for q in ("hiver", "ete", "pluie"):
        assert r[q]["des"] == 400, f"{q} : {r[q]['des']} dés pour 400 tirages"
    assert r["ete"]["vus"].get("moto") and r["ete"]["vus"].get("velo"), f"l'été, ni moto ni vélo : {r['ete']['vus']}"
    assert not r["hiver"]["vus"].get("moto") and not r["hiver"]["vus"].get("velo"), f"l'hiver : {r['hiver']['vus']}"
    assert not r["pluie"]["vus"].get("moto") and r["pluie"]["vus"].get("velo"), f"sous la pluie : {r['pluie']['vus']}"
    # Ce qui était moto ou vélo est devenu berline — le reste n'a pas bougé.
    ete, hiver = r["ete"]["vus"], r["hiver"]["vus"]
    assert hiver["auto"] == ete["auto"] + ete["moto"] + ete["velo"], (ete, hiver)
    for slug, n in ete.items():
        if slug not in ("auto", "moto", "velo"):
            assert hiver.get(slug) == n, f"{slug} : {n} l'été, {hiver.get(slug)} l'hiver"


def test_ils_rentrent_hors_champ_jamais_sous_nos_yeux(banc):
    """L'hiver, les motos et les vélos du trafic ET garés rentrent — hors champ seulement, et
    jamais ce qui est à quelqu'un (payé, volé, à la planque, d'une mission). Sous la pluie,
    seules les motos qui ROULENT rentrent : garée, une moto attend la fin de l'averse."""
    r = banc("""function (L, o) {""" + DECOR + """
        const loin = function (k) { return { x: j.x + 900 + k * 40, y: j.y }; };
        const poser = function () {
            B.entites = B.entites.filter(function (e) { return e.type !== 'vehicule'; });
            const c = {};
            const naitre = function (nom, slug, p, opts) { c[nom] = V.creer(slug, p.x, p.y, 0, Object.assign({ couleur: '#123456' }, opts)); };
            naitre('motoRoule', 'moto', loin(0), { conducteur: 'trafic', etat: 'roule' });
            naitre('veloRoule', 'velo', loin(1), { conducteur: 'trafic', etat: 'roule' });
            naitre('motoGaree', 'moto', loin(2), { etat: 'stationne' });
            naitre('veloGare', 'velo', loin(3), { etat: 'stationne' });
            naitre('motoVue', 'moto', { x: j.x + 30, y: j.y }, { conducteur: 'trafic', etat: 'roule' });
            naitre('motoPayee', 'moto', loin(4), { etat: 'stationne' }); c.motoPayee.aToi = true;
            naitre('motoVolee', 'moto', loin(5), { etat: 'stationne' }); c.motoVolee.vole = true;
            naitre('motoPlanque', 'moto', loin(6), { etat: 'stationne' }); c.motoPlanque.aLaPlanque = true;
            naitre('motoMission', 'moto', loin(7), { etat: 'stationne', mission: 'q10' });
            naitre('berline', 'auto', loin(8), { conducteur: 'trafic', etat: 'roule' });
            L.Entites.indexer();
            return c;
        };
        const reste = function (c) {
            V.rentrerLesRemises();
            const o = {};
            for (const n in c) o[n] = B.entites.indexOf(c[n]) >= 0;
            return o;
        };
        L.Monde.centrerCamera(j.x, j.y);
        const out = {};
        saison(""" + str(HIVER) + """); out.hiver = reste(poser());
        saison('pluie'); out.pluie = reste(poser());
        saison(""" + str(ETE) + """); out.ete = reste(poser());
        return out;
    }""")
    a_toi = {"motoVue": True, "motoPayee": True, "motoVolee": True, "motoPlanque": True, "motoMission": True, "berline": True}
    assert r["hiver"] == {**a_toi, "motoRoule": False, "veloRoule": False, "motoGaree": False, "veloGare": False}, r["hiver"]
    assert r["pluie"] == {**a_toi, "motoRoule": False, "veloRoule": True, "motoGaree": True, "veloGare": True}, r["pluie"]
    assert all(r["ete"].values()), f"l'été, rien ne rentre : {r['ete']}"


def test_la_moto_du_livreur_dort_sous_sa_bache(banc):
    """L'hiver, la moto de la planque est peinte SOUS SA BÂCHE et on n'y monte pas (« REMISÉE
    POUR L'HIVER ») ; l'été, c'est une moto, et on y monte. Sous la pluie, on y monte aussi :
    c'est le trafic qui rentre, pas le joueur."""
    r = banc("""function (L, o) {""" + DECOR + """
        const out = {}, vrai = L.Atlas.cuireCap;
        [['hiver', """ + str(HIVER) + """], ['ete', """ + str(ETE) + """], ['pluie', 'pluie']].forEach(function (q) {
            saison(q[1]);
            if (j.dansVehicule) V.descendre(j, true);
            const v = V.creer('moto', j.x + 12, j.y, 0, { etat: 'stationne', couleur: '#1a1a1a' });
            v.aLaPlanque = true; L.Entites.indexer();
            const noms = [];
            L.Atlas.cuireCap = function (nom) { noms.push(nom); return vrai.apply(this, arguments); };
            V.dessinerUn(L.Base.ecran(), v, 0, 0);
            L.Atlas.cuireCap = vrai;
            B.msg = '';
            const monte = V.monter(j, v);
            out[q[0]] = { dessin: noms[0], monte: !!monte && j.dansVehicule === v, msg: B.msg };
            if (j.dansVehicule) V.descendre(j, true);
            L.Entites.retirer(v);
        });
        return out;
    }""")
    assert r["hiver"]["dessin"] == "moto~bache", f"l'hiver, la moto est peinte {r['hiver']['dessin']}"
    assert not r["hiver"]["monte"] and "REMISÉE" in r["hiver"]["msg"], f"l'hiver, on monte sur la moto : {r['hiver']}"
    assert r["ete"]["dessin"] == "moto" and r["ete"]["monte"], f"l'été : {r['ete']}"
    assert r["pluie"]["dessin"] == "moto" and r["pluie"]["monte"], f"sous la pluie : {r['pluie']}"


def test_les_enfants_a_velo_rentrent_l_hiver(banc):
    """L'hiver, aucun enfant à vélo ne naît, et celui qui roulait hors champ rentre ; l'été, on
    le laisse rouler."""
    r = banc("""function (L, o) {""" + DECOR + """
        const arch = L.Entites.archetype('enfant_velo');
        const out = {};
        [['hiver', """ + str(HIVER) + """], ['ete', """ + str(ETE) + """]].forEach(function (q) {
            saison(q[1]);
            B.entites = B.entites.filter(function (e) { return e.arch !== 'enfant_velo'; });
            const e = L.Entites.creerPieton(j.x + 900, j.y, arch);
            L.Entites.indexer();
            const nes = L.Entites.naitreLesEnfantsAVelo();
            out[q[0]] = { lui: B.entites.indexOf(e) >= 0, nes: nes };
        });
        return out;
    }""")
    assert r["hiver"] == {"lui": False, "nes": 0}, f"l'hiver, un enfant à vélo roule encore : {r['hiver']}"
    assert r["ete"]["lui"], "l'été, l'enfant à vélo a disparu"


def _m2(saison):
    return """function (L, o) {
        L.Jeu.commencer();
        L.graine(6);
        const B = L.B, j = B.joueur;
        B.partie.jour = """ + str(saison) + """; B.partie.heure = 0.5;
        B.partie.missionsFaites.m1 = 1;
        const t = L.Histoire.donneur('thibodeau');
        j.x = t.x - 16; j.y = t.y; L.Entites.indexer();
        // Comme au jeu : on lui PARLE, et l'intro se deroule (une scene) ; on garde chaque voix dite.
        const intro = [], vrai = L.Son.Voix.parler;
        L.Son.Voix.parler = function (slug) { intro.push(slug); return vrai.apply(this, arguments); };
        L.Histoire.parler('thibodeau');
        for (let k = 0; k < 4000 && (B.scene || B.cinema); k++) { if (B.cinema) L.Histoire.suivante(); else o.frame(1); }
        L.Son.Voix.parler = vrai;
        const cibles = L.B.mission.entites.filter(function (e) { return e.type === 'pieton' && e.cible; });
        cibles.forEach(function (e) { L.Entites.assommer(e); });
        B.msg = '';
        o.frame(2);
        const msg = B.msg;
        while (L.B.cinema) L.Histoire.suivante();
        const f = L.B.mission.fuyard;
        return { intro: intro, slug: f && f.slug, msg: msg, objectif: L.Histoire.ligneObjectif() };
    }"""


def test_l_hiver_le_fuyard_de_m2_file_en_motoneige_et_on_le_dit(banc):
    """m2 l'hiver : le fuyard file EN MOTONEIGE, le HUD le dit, l'objectif aussi, et Mme
    Thibodeau le dit avec sa voix d'hiver (`thibodeau-m2-4-hiver`) ; l'été, la moto, et les
    mots d'avant."""
    hiver, ete = banc(_m2(HIVER)), banc(_m2(ETE))
    assert hiver["slug"] == "motoneige" and "MOTONEIGE" in hiver["msg"], f"l'hiver : {hiver}"
    assert "MOTONEIGE" in hiver["objectif"], f"l'hiver, l'objectif dit : {hiver['objectif']}"
    assert "thibodeau-m2-4-hiver" in hiver["intro"], f"l'hiver, elle dit : {hiver['intro']}"
    assert ete["slug"] == "moto" and "EN MOTO" in ete["msg"], f"l'été : {ete}"
    assert "MOTONEIGE" not in ete["objectif"], ete["objectif"]
    assert "thibodeau-m2-4" in ete["intro"] and "thibodeau-m2-4-hiver" not in ete["intro"], ete["intro"]


def test_l_hiver_la_pizza_se_livre_en_berline_de_livreur(banc):
    """L'hiver, une berline au toit PIZZA attend près de la planque (elle naît hors champ, à
    l'approche) et son klaxon lance la livraison ; une berline ordinaire garde son klaxon.
    L'été, elle ne naît pas."""
    r = banc("""function (L, o) {""" + DECOR + """
        const planque = L.Histoire.lieu('planque');
        const out = {};
        [['hiver', """ + str(HIVER) + """], ['ete', """ + str(ETE) + """]].forEach(function (q) {
            saison(q[1]);
            if (j.dansVehicule) V.descendre(j, true);
            B.entites = B.entites.filter(function (e) { return e.sprite !== 'auto_pizza'; });
            // Elle nait a l'approche, hors champ : on arrive de chaque cote, une seconde chaque fois.
            let la = null;
            for (const d of [[440, 0], [-440, 0], [0, 440], [0, -440]]) {
                j.x = planque.x + d[0]; j.y = planque.y + d[1]; L.Monde.centrerCamera(j.x, j.y); L.Entites.indexer();
                for (let k = 0; k < 70; k++) { B.t++; L.Missions.majBerlineDeLivreur(); }
                la = B.entites.find(function (e) { return e.sprite === 'auto_pizza'; });
                if (la) break;
            }
            out[q[0]] = { nee: !!la, pres: la ? Math.hypot(la.x - planque.x, la.y - planque.y) : null };
            if (la && q[0] === 'hiver') {
                la.x = j.x + 12; la.y = j.y; L.Entites.indexer();
                V.monter(j, la);
                out.klaxon = L.Missions.boulot.klaxon(la) && L.Missions.boulot.slug;
                L.Missions.boulot.abandonner('');
                V.descendre(j, true);
                const b = V.creer('auto', j.x + 12, j.y + 30, 0, { etat: 'stationne', couleur: '#c0392b', sprite: 'auto' });
                L.Entites.indexer();
                V.monter(j, b);
                out.berline = L.Missions.boulot.klaxon(b);
                V.descendre(j, true);
            }
        });
        return out;
    }""")
    assert r["hiver"]["nee"], "l'hiver, aucune berline de livreur près de la planque"
    assert r["hiver"]["pres"] < 20 * 16, f"elle est à {r['hiver']['pres']:.0f} px de la planque"
    assert r["klaxon"] == "pizza", f"son klaxon ne lance pas la pizza : {r['klaxon']}"
    assert r["berline"] is False, "une berline ordinaire lance un boulot au klaxon"
    assert not r["ete"]["nee"], "l'été, la berline de livreur est née quand même"


def test_sven_veut_une_motoneige_et_le_grand_saut_attend_le_printemps(banc):
    """L'hiver, la moto de la liste de Sven devient une motoneige (le tirage ne bouge pas : les
    autres modèles restent les mêmes), et Le Grand Saut refuse de partir."""
    r = banc("""function (L, o) {""" + DECOR + """
        const out = {};
        // Un jour d'ete et un jour d'hiver qui tombent dans des periodes ou Sven veut une moto.
        const r = B.defs.economie.liste_du_quai;
        const cherche = function (hiver) {
            for (let jour = 1; jour <= 400; jour++) {
                if ((L.Calendrier.saison(jour) === 'hiver') !== hiver) continue;
                saison(jour);
                if (!!L.Saisons.enHiver() !== hiver) continue;
                B.partie.jour = jour;
                const brut = (function () {
                    const periode = Math.floor((jour - 1) / r.renouvelle_jours), pool = r.modeles.slice(), liste = [];
                    for (let k = 0; k < r.nombre && pool.length; k++) liste.push(pool.splice(L.hash2(periode, r.sel + k) % pool.length, 1)[0]);
                    return liste;
                })();
                if (brut.indexOf('moto') >= 0) return { brut: brut, liste: L.Missions.listeDuQuai(jour) };
            }
            return null;
        };
        out.hiver = cherche(true); out.ete = cherche(false);
        saison(""" + str(HIVER) + """);
        const saut = B.defs.defis.find(function (d) { return d.slug === 'saut'; });
        // ⚠️ Le refus se dit AU DEPART (`commencerDefi`) : le message est pose tout de suite.
        B.msg = '';
        L.Histoire.commencerDefi(saut);
        out.saut = { defi: !!B.defi, msg: B.msg };
        return out;
    }""")
    assert r["hiver"] and r["ete"], f"aucune période où Sven veut une moto : {r}"
    h = r["hiver"]
    assert "moto" not in h["liste"] and "motoneige" in h["liste"], f"l'hiver, Sven veut {h['liste']}"
    assert [s for s in h["liste"] if s != "motoneige"] == [s for s in h["brut"] if s != "moto"], h
    assert r["ete"]["liste"] == r["ete"]["brut"], f"l'été, la liste de Sven a changé : {r['ete']}"
    assert not r["saut"]["defi"] and "REMISÉE" in r["saut"]["msg"], f"l'hiver, Le Grand Saut part : {r['saut']}"


def test_l_hiver_une_motoneige_attend_sven_au_pont(banc):
    """q10 : l'hiver, c'est une MOTONEIGE qui attend au pont, à la mission, et l'objectif le dit ;
    l'été, la moto. (Sous la pluie, la moto garée attend : seul le trafic rentre.)"""
    r = banc("""function (L, o) {
        const out = {};
        [""" + f"{HIVER}, {ETE}" + """].forEach(function (jour) {
            L.Jeu.commencer(); L.graine(6);
            const B = L.B; B.partie.jour = jour; B.partie.heure = 0.5;
            L.Histoire.commencer('q10');
            for (let k = 0; k < 30; k++) o.frame(1);
            const v = B.mission && B.mission.vehicule;
            out[jour] = { slug: v && v.slug, mission: v && v.mission, ligne: L.Histoire.ligneObjectif() };
        });
        return out;
    }""")
    hiver, ete = r[str(HIVER)], r[str(ETE)]
    assert hiver["slug"] == "motoneige" and hiver["mission"] == "q10", f"l'hiver, au pont : {hiver}"
    assert "MOTONEIGE" in hiver["ligne"], f"l'hiver, l'objectif dit : {hiver['ligne']}"
    assert ete["slug"] == "moto" and "MOTONEIGE" not in ete["ligne"], f"l'été, au pont : {ete}"
