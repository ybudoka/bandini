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
        const noms = menu.items.map(function (i) { return i.meuble; });
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
