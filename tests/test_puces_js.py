"""Le marché aux puces du dimanche au banc : ouvert le dimanche matin seulement, le même étal pour tout le monde,
marchander sans un dé, une carte achetée entre dans l'album, un meuble acheté va à la planque — et ACTION, par le
bouton, ouvre l'étal.
"""

DEVANT = """
    function devant(L, o, slug) {
        L.Jeu.commencer();
        if (L.B.menu) L.Hud.fermerMenu();
        L.B.defs.trafic && (L.B.defs.trafic.vehicules_max = 0);
        L.B.entites.filter(function (e) { return e.type === 'pieton' && !e.personnage; }).forEach(L.Entites.retirer);
        const e = L.Puces.etal(slug), j = L.B.joueur;
        L.B.partie.jour = 14; L.B.partie.heure = 8 / 24;
        j.x = (e.x + 1) * 16; j.y = (e.y + 1) * 16 + 10; j.vx = 0; j.vy = 0; j.angle = -Math.PI / 2; j.dir = 'haut';
        L.Entites.indexer(); L.Monde.centrerCamera(j.x, j.y);
        L.B.partie.argent = 5000;
        return { e: e, j: j };
    }
"""


def test_ouvert_le_dimanche_matin_seulement(banc):
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const P = L.Puces;
        return { dim8: P.ouvertA(14, 8 / 24), sam8: P.ouvertA(13, 8 / 24), dim5: P.ouvertA(14, 5 / 24),
                 dim13: P.ouvertA(21, 13 / 24), dim11: P.ouvertA(7, 11.5 / 24), etals: P.etals().length,
                 places: P.etals().every(function (e) { return typeof e.x === 'number'; }) };
    }""")
    assert r["dim8"] and r["dim11"], r
    assert not (r["sam8"] or r["dim5"] or r["dim13"]), r
    assert r["etals"] == 2 and r["places"], r


def test_le_meme_dimanche_le_meme_etal_et_il_change_la_semaine_d_apres(banc):
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const P = L.Puces, s = [];
        for (let k = 0; k < 6; k++) s.push(P.stock(k));
        return { s: s, encore: P.stock(1), humeurs: [P.humeur(1, 'cartes', 'carte12'), P.humeur(1, 'cartes', 'carte12')] };
    }""")
    s = r["s"]
    assert all(len(x) == 4 and len(set(x)) == 4 and all(1 <= n <= 40 for n in x) for x in s), s
    assert r["encore"] == s[1], "le même dimanche, deux étals différents"
    assert len({tuple(x) for x in s}) >= 5, "l'étal ne change pas d'une semaine à l'autre"
    assert r["humeurs"][0] == r["humeurs"][1]


def test_marchander_ne_tire_aucun_de_et_un_refus_tient_la_semaine(banc):
    r = banc("function (L, o) {" + DEVANT + """
        devant(L, o, 'cartes');
        const P = L.Puces;
        let des = 0; const vrai = L.B.rng; L.B.rng = function () { des++; return vrai(); };
        // Un article que Ti-Rhéal refuse cette semaine, un autre qu'il accepte : lus à son humeur.
        const sem = P.semaine(14), stock = P.stock(sem).filter(function (n) { return !L.Collections.trouvee(n); });
        const refuse = stock.find(function (n) { return !P.accepte(sem, 'cartes', 'carte' + n); });
        const accepte = stock.find(function (n) { return P.accepte(sem, 'cartes', 'carte' + n); });
        const out = {};
        if (refuse) {
            const a = L.B.partie.argent;
            out.refus = P.marchander('cartes', 'carte' + refuse, 120, function (x) { return P.acheterCarte(refuse, x); });
            out.encore = P.marchander('cartes', 'carte' + refuse, 120, function (x) { return P.acheterCarte(refuse, x); });
            out.paye = a - L.B.partie.argent;
            L.B.partie.jour += 7;
            out.semaineApres = P.refusDeLaSemaine()['cartes:carte' + refuse] || false;
            L.B.partie.jour -= 7;
        }
        if (accepte) {
            const a = L.B.partie.argent;
            out.ok = P.marchander('cartes', 'carte' + accepte, 120, function (x) { return P.acheterCarte(accepte, x); });
            out.payeOk = a - L.B.partie.argent;
            out.album = L.B.partie.collections.cartes[accepte] || null;
        }
        L.B.rng = vrai;
        out.des = des; out.aUnRefus = !!refuse; out.aUnAccord = !!accepte;
        return out;
    }""")
    assert r["des"] == 0, "marchander a tiré un dé"
    if r["aUnRefus"]:
        assert r["refus"] == "refuse" and r["encore"] is None and r["paye"] == 0, r
        assert r["semaineApres"] is False, "un refus tient au-delà de sa semaine"
    if r["aUnAccord"]:
        assert r["ok"] == "accepte" and r["payeOk"] == 84 and r["album"]["source"] == "puces", r
    assert r["aUnRefus"] or r["aUnAccord"]


def test_une_carte_achetee_entre_dans_l_album_sans_la_prime_de_la_rue(banc):
    r = banc("function (L, o) {" + DEVANT + """
        devant(L, o, 'cartes');
        const n = L.Puces.stock(L.Puces.semaine(14))[0];
        const a = L.B.partie.argent;
        const ok = L.Puces.acheterCarte(n, 120);
        const deux = L.Puces.acheterCarte(n, 120);
        return { ok: ok, deux: deux, paye: a - L.B.partie.argent, album: L.B.partie.collections.cartes[n] || null,
                 detail: L.Puces.menuEtal('cartes').items.filter(function (i) { return i.numero === n; })[0].detail };
    }""")
    assert r["ok"] is True and r["deux"] is False, r
    assert r["paye"] == 120, "une carte achetée rapporte aussi la prime de la rue (ou se paie deux fois)"
    assert r["album"]["source"] == "puces" and r["detail"] == "DANS L’ALBUM", r


def test_un_meuble_des_puces_va_a_la_planque_le_lendemain(banc):
    r = banc("function (L, o) {" + DEVANT + """
        devant(L, o, 'meubles');
        const menu = L.Puces.menuEtal('meubles');
        const noms = menu.items.filter(function (i) { return i.meuble; }).map(function (i) { return i.meuble; });
        const sofa = L.Decoration.meubles().find(function (m) { return m.slug === 'sofa'; });
        const a = L.B.partie.argent;
        const ok = L.Puces.acheterMeuble('sofa', L.Puces.prixMeuble(sofa));
        const aujourdhui = L.Decoration.presents('planque').indexOf('sofa') >= 0;
        L.B.partie.jour += 1;
        const demain = L.Decoration.presents('planque').indexOf('sofa') >= 0;
        return { noms: noms, ok: ok, paye: a - L.B.partie.argent, prixCatalogue: sofa.prix, aujourdhui: aujourdhui, demain: demain };
    }""")
    assert sorted(r["noms"]) == ["jukebox", "sofa", "tapis_tresse", "televiseur"], r["noms"]
    assert r["ok"] and 0 < r["paye"] < r["prixCatalogue"], "aux puces, plus cher qu'au catalogue"
    assert r["aujourdhui"] is False and r["demain"] is True, r


def test_action_devant_l_etal_ouvre_son_menu_par_le_bouton(banc):
    r = banc("function (L, o) {" + DEVANT + """
        const d = devant(L, o, 'cartes');
        o.frame(2);
        o.tape('KeyE', 2);
        o.frame(2);
        const ouvert = L.B.menu && L.B.menu.titre;
        if (L.B.menu) L.Hud.fermerMenu();
        L.B.partie.jour = 13;                        // un samedi : rien
        o.frame(2);
        o.tape('KeyE', 2);
        o.frame(2);
        return { ouvert: ouvert, samedi: L.B.menu && L.B.menu.titre };
    }""")
    assert r["ouvert"] == "LES CARTES DE TI-RHÉAL", r
    assert r["samedi"] != "LES CARTES DE TI-RHÉAL", r


def test_le_marche_se_peint_le_dimanche_et_pas_la_semaine(banc):
    r = banc("function (L, o) {" + DEVANT + """
        devant(L, o, 'cartes');
        let n = 0; const ctx = { fillRect: function () { n++; }, set fillStyle(v) {} };
        L.Puces.dessiner(ctx, L.B.cam);
        const dim = n; n = 0;
        L.B.partie.jour = 12;
        L.Puces.dessiner(ctx, L.B.cam);
        return { dim: dim, semaine: n };
    }""")
    assert r["dim"] > 30 and r["semaine"] == 0, r


def test_la_triche_mene_au_marche_un_dimanche_matin(banc):
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        if (L.B.menu) L.Hud.fermerMenu();
        L.B.partie.jour = 10;
        const page = L.Hud.menuDebugCollections();
        const ligne = page.items.filter(function (i) { return i.puces; })[0];
        ligne.faire(ligne);
        return { jour: L.B.partie.jour, ouvert: L.Puces.ouvert(), devant: !!L.Puces.sousLaMain(L.B.joueur) };
    }""")
    assert r["jour"] == 14 and r["ouvert"] and r["devant"], r


# --- La deuxième vague : les marchands parlent, la rumeur, et on vend à Gisèle -----------------------------------------

#: Choisir la ligne `trouver` du menu ouvert, PAR LE BOUTON : le curseur dessus, puis ACTION.
CHOISIR = """
    function choisir(L, o, trouver) {
        const m = L.B.menu;
        if (!m) return false;
        const i = m.items.findIndex(trouver);
        if (i < 0) return false;
        m.curseur = i;
        o.tape('KeyE', 2);
        return true;
    }
    function dits(L) { return L.Son.Voix.demandees.filter(function (s) { return s.indexOf('-puces-') > 0; }); }
"""


def test_le_marchand_se_nomme_la_premiere_fois_puis_dit_sa_ligne_de_la_semaine(banc):
    r = banc("function (L, o) {" + DEVANT + CHOISIR + """
        devant(L, o, 'cartes');
        o.frame(2);
        o.tape('KeyE', 2);
        const premier = { voix: dits(L).slice(), aide: L.B.menu && L.B.menu.aide };
        o.tape('Escape', 2);
        const sortie = { voix: dits(L).slice(-1)[0], menu: !!L.B.menu, message: L.B.msg && L.B.msg.texte };
        o.tape('KeyE', 2);
        const deuxieme = dits(L).slice(-1)[0];
        o.tape('Escape', 2);
        L.B.partie.jour = 21;
        o.tape('KeyE', 2);
        const semaineApres = dits(L).slice(-1)[0];
        return { premier: premier, sortie: sortie, deuxieme: deuxieme, semaineApres: semaineApres,
                 connus: L.B.partie.puces.connus, sem14: L.Puces.semaine(14), sem21: L.Puces.semaine(21) };
    }""")
    assert r["premier"]["voix"] == ["ti_rheal-puces-salut"], r
    assert "TI-RHÉAL BERGERON" in r["premier"]["aide"], "le nom dit à voix haute ne s'affiche pas"
    assert r["sortie"]["voix"] == "ti_rheal-puces-aurevoir" and r["sortie"]["menu"] is False, r["sortie"]
    assert r["deuxieme"] == f"ti_rheal-puces-accueil-{1 + r['sem14'] % 3}", "il se représente, ou tire sa ligne"
    assert r["semaineApres"] == f"ti_rheal-puces-accueil-{1 + r['sem21'] % 3}" != r["deuxieme"], r
    assert r["connus"] == {"ti_rheal": 14}, "on ne se présente qu'une fois : ça se garde"


def test_rien_a_vendre_quand_tout_l_etal_est_a_toi(banc):
    r = banc("function (L, o) {" + DEVANT + CHOISIR + """
        devant(L, o, 'cartes');
        L.B.partie.puces = { semaine: L.Puces.semaine(14), refus: {}, connus: { ti_rheal: 7, gisele: 7 } };
        L.Puces.stock(L.Puces.semaine(14)).forEach(function (n) { L.B.partie.collections.cartes[n] = { jour: 1, source: 'rue' }; });
        o.tape('KeyE', 2);
        const cartes = dits(L).slice(-1)[0];
        o.tape('Escape', 2);
        L.Puces.meublesAuxPuces().forEach(function (m) { L.B.partie.meubles.planque = L.B.partie.meubles.planque || {}; L.B.partie.meubles.planque[m.slug] = { jour: 1 }; });
        const e = L.Puces.etal('meubles'), j = L.B.joueur;
        j.x = (e.x + 1) * 16; j.y = (e.y + 1) * 16 + 10; L.Entites.indexer();
        o.tape('KeyE', 2);
        return { cartes: cartes, meubles: dits(L).slice(-1)[0] };
    }""")
    assert r == {"cartes": "ti_rheal-puces-rien", "meubles": "gisele-puces-rien"}, r


def test_la_vente_et_le_marchandage_se_disent(banc):
    r = banc("function (L, o) {" + DEVANT + CHOISIR + """
        devant(L, o, 'cartes');
        const P = L.Puces, sem = P.semaine(14), stock = P.stock(sem);
        o.tape('KeyE', 2);
        // ACHETER au prix affiché, par le bouton : « vendue ».
        choisir(L, o, function (i) { return i.numero === stock[0]; });
        choisir(L, o, function (i) { return i.libelle === 'ACHETER'; });
        const vente = dits(L).slice(-1)[0];
        const refuse = stock.find(function (n) { return !P.accepte(sem, 'cartes', 'carte' + n); });
        const accepte = stock.slice(1).find(function (n) { return P.accepte(sem, 'cartes', 'carte' + n); });
        const out = { vente: vente };
        if (refuse && refuse !== stock[0]) {
            P.marchander('cartes', 'carte' + refuse, 120, function (x) { return P.acheterCarte(refuse, x); });
            out.refuse = dits(L).slice(-1)[0]; out.message = L.B.msg && L.B.msg.texte;
        }
        if (accepte) {
            P.marchander('cartes', 'carte' + accepte, 120, function (x) { return P.acheterCarte(accepte, x); });
            out.accepte = dits(L).slice(-1)[0];
        }
        return out;
    }""")
    assert r["vente"] == "ti_rheal-puces-vente", r
    if "refuse" in r:
        assert r["refuse"] == "ti_rheal-puces-refuse" and "84 $ ? T'ES DRÔLE, TOI." in r["message"], r
    if "accepte" in r:
        assert r["accepte"] == "ti_rheal-puces-accepte", r


VENDRE = """
    function aGisele(L, o) {
        const d = devant(L, o, 'meubles');
        L.B.partie.puces = { semaine: L.Puces.semaine(14), refus: {}, connus: { gisele: 7 } };
        L.B.partie.meubles = { planque: { sofa: { jour: 10 }, lampe_lave: { jour: 10 } } };
        return d;
    }
"""


def test_vendre_un_meuble_a_gisele_par_le_bouton_le_retire_de_la_planque_et_de_la_sauvegarde(banc):
    r = banc("function (L, o) {" + DEVANT + CHOISIR + VENDRE + """
        aGisele(L, o);
        const a = L.B.partie.argent;
        o.tape('KeyE', 2);
        const ligne = L.B.menu.items.find(function (i) { return i.vendre; });
        const vendre = choisir(L, o, function (i) { return i.vendre; });
        const titre = L.B.menu && L.B.menu.titre, lignes = L.B.menu.items.map(function (i) { return i.vend || i.libelle; });
        choisir(L, o, function (i) { return i.vend === 'sofa'; });
        const titreRachat = L.B.menu && L.B.menu.titre;
        choisir(L, o, function (i) { return i.libelle === 'VENDRE'; });
        const p = L.B.partie;
        const relue = L.Sauvegarde.completer(JSON.parse(JSON.stringify(p)), L.B.defs);
        const etal = L.Puces.menuEtal('meubles').items.find(function (i) { return i.meuble === 'sofa'; });
        return { detail: ligne.detail, vendre: vendre, titre: titre, lignes: lignes, titreRachat: titreRachat, recu: p.argent - a,
                 planque: Object.keys(p.meubles.planque), sauvegarde: Object.keys(relue.meubles.planque || {}),
                 presents: L.Decoration.presents('planque'), etal: etal && etal.detail, voix: dits(L),
                 carnet: JSON.stringify(p.journalDuCarnet || p.carnet || '') };
    }""")
    assert r["vendre"] and r["detail"] == "2 À LA PLANQUE", r
    assert r["titre"] == "VENDRE À GISÈLE" and r["lignes"][:2] == ["sofa", "lampe_lave"] or r["lignes"][:2] == ["lampe_lave", "sofa"], r
    assert r["recu"] == 100, "Gisèle rachète le sofa (400 $ au catalogue) au quart"
    assert r["planque"] == ["lampe_lave"] and r["sauvegarde"] == ["lampe_lave"], r
    assert "sofa" not in r["presents"]
    assert r["etal"] == str(round(400 * 0.6)) + " $", "un meuble vendu ne revient pas à l'étal de Gisèle"
    assert r["voix"][-2:] == ["gisele-puces-rachat", "gisele-puces-rachat-conclu"], r["voix"]


def test_un_meuble_pas_encore_livre_ne_se_vend_pas(banc):
    r = banc("function (L, o) {" + DEVANT + VENDRE + """
        aGisele(L, o);
        L.B.partie.meubles.planque.jukebox = { jour: 14 };        // acheté ce matin : livré demain
        const avant = L.Puces.aRacheter().map(function (a) { return a.meuble.slug; });
        const vendu = L.Puces.vendreMeuble('planque', 'jukebox', 375);
        return { avant: avant, vendu: vendu, encore: !!L.B.partie.meubles.planque.jukebox };
    }""")
    assert "jukebox" not in r["avant"] and r["vendu"] is False and r["encore"], r


def test_demander_plus_sans_un_de_et_le_refus_tient_la_semaine(banc):
    r = banc("function (L, o) {" + DEVANT + VENDRE + """
        aGisele(L, o);
        const P = L.Puces;
        let des = 0; const vrai = L.B.rng; L.B.rng = function () { des++; return vrai(); };
        // Une semaine où Gisèle monte pour le sofa, une où elle refuse : lues à son humeur.
        let oui = null, non = null;
        for (let s = 1; s < 60 && (oui === null || non === null); s++) {
            if (P.accepteDeMonter(s, 'sofa')) { if (oui === null) oui = s; } else if (non === null) non = s;
        }
        const out = { oui: oui, non: non };
        L.B.partie.jour = 7 * (non + 1);
        L.B.partie.meubles.planque.sofa = { jour: 1 };
        let a = L.B.partie.argent;
        out.refus = P.demanderPlus('planque', 'sofa');
        out.encore = P.demanderPlus('planque', 'sofa');
        out.payeRefus = L.B.partie.argent - a;
        out.garde = !!L.B.partie.meubles.planque.sofa;
        out.voixRefus = L.Son.Voix.demandees.slice(-1)[0];
        out.ligne = P.menuRachat('meubles', 'planque', L.Decoration.meubles().find(function (m) { return m.slug === 'sofa'; }), 'SOFA').items[1];
        L.B.partie.jour = 7 * (oui + 1);
        a = L.B.partie.argent;
        out.ok = P.demanderPlus('planque', 'sofa');
        out.recuOk = L.B.partie.argent - a;
        out.voixOk = L.Son.Voix.demandees.slice(-1)[0];
        out.parti = !L.B.partie.meubles.planque.sofa;
        L.B.rng = vrai;
        out.des = des;
        return out;
    }""")
    assert r["oui"] and r["non"], "sur soixante semaines, Gisèle ne change jamais d'humeur"
    assert r["des"] == 0, "demander plus a tiré un dé"
    assert r["refus"] == "refuse" and r["encore"] is None and r["payeRefus"] == 0 and r["garde"], r
    assert r["voixRefus"] == "gisele-puces-plus-refuse" and r["ligne"]["actif"] is False, r
    assert r["ok"] == "accepte" and r["recuOk"] == 130 and r["parti"], "le sofa se revend 100 $ × 1,3"
    assert r["voixOk"] == "gisele-puces-plus-accepte", r


def test_acheter_pour_revendre_perd_toujours(banc):
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const P = L.Puces, off = P.regle().offre;
        return L.Decoration.meubles().map(function (m) {
            const achat = m.ou.indexOf('puces') >= 0 ? Math.round(P.prixMeuble(m) * off) : m.prix;
            return { slug: m.slug, achat: Math.min(achat, m.prix), revente: P.prixDemande(m) };
        });
    }""")
    for m in r:
        assert m["revente"] < m["achat"], m


def test_la_rumeur_suit_la_distance_et_les_heures_et_glisse(banc):
    r = banc("function (L, o) {" + DEVANT + """
        const d = devant(L, o, 'cartes'), P = L.Puces, j = d.j, t = P.donnees().terrain;
        const surPlace = P.cibleDuSon(j);
        // La partie tourne loin du marché (un dimanche matin, à trente tuiles) : rien du marché ne se charge.
        const x0 = j.x, y0 = j.y;
        j.y = (t.y + t.h) * 16 + 480; L.Entites.indexer(); o.frame(5);
        const avant = L.Son.Voix.missionsChargees.has('puces') || !!(L.B.defs.audio.lieux || {}).puces;
        j.y = y0;
        j.y = (t.y + t.h) * 16 + 160;                       // à dix tuiles sous le bord du terrain
        const aDix = P.cibleDuSon(j);
        j.y = (t.y + t.h) * 16 + 400;
        const loin = P.cibleDuSon(j);
        j.x = x0; j.y = (t.y + 1) * 16;
        L.B.partie.jour = 13; const samedi = P.cibleDuSon(j);
        L.B.partie.jour = 14; L.B.partie.heure = 12.5 / 24; const midi = P.cibleDuSon(j);
        L.B.partie.heure = 8 / 24;
        // Elle glisse : une image n'y est pas, deux secondes et demie oui ; midi sonne, elle ne tombe pas d'un coup.
        P.majSon(); const uneImage = P.volumeDuSon();
        for (let k = 0; k < 160; k++) P.majSon();
        const plein = P.volumeDuSon();
        L.B.partie.heure = 12 / 24;
        P.majSon(); const apresMidi = P.volumeDuSon();
        for (let k = 0; k < 160; k++) P.majSon();
        const eteinte = P.volumeDuSon();
        const noms = L.Son.Voix.histoire().filter(function (v) { return v.mission === 'puces'; }).map(function (v) { return v.slug; });
        return { surPlace: surPlace, aDix: aDix, loin: loin, samedi: samedi, midi: midi, uneImage: uneImage, plein: plein,
                 apresMidi: apresMidi, eteinte: eteinte, avant: avant, apres: L.Son.Voix.missionsChargees.has('puces'),
                 lieu: (L.B.defs.audio.lieux || {}).puces || null, noms: noms.length,
                 gisele: noms.indexOf('gisele-puces-salut') >= 0 };
    }""")
    assert r["surPlace"] == 1 and 0.4 < r["aDix"] < 0.6 and r["loin"] == 0, r
    assert r["samedi"] == 0 and r["midi"] == 0, r
    assert 0 < r["uneImage"] < 0.05 and r["plein"] == 1, "la rumeur saute d'un coup au lieu de glisser"
    assert 0.9 < r["apresMidi"] < 1 and r["eteinte"] == 0, r
    assert r["avant"] is False, "les voix du marché se chargent au démarrage"
    assert r["apres"] and r["lieu"] == ["rumeur_puces"] and r["noms"] == 22 and r["gisele"], r
