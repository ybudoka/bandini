"""La run, cote navigateur : la cale vend dans le coffre du char d'a cote (et
refuse sans char), le prix monte dans la journee, le comptoir affiche le prix
du jour du district et achete la cargaison, et la police fouille."""

from app import economie


def test_la_cale_vend_dans_le_coffre_du_char_d_a_cote(banc, paquet):
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        L.graine(9);
        const j = L.B.joueur, p = L.B.partie, c = L.B.defs.economie.contrebande;
        const cale = L.B.entites.find(function (e) { return e.type === 'ambulant' && e.slug === 'contrebande'; });
        if (!cale) return { pasDeCale: true };
        p.argent = 5000;
        j.x = cale.x; j.y = cale.y + 18; L.Monde.centrerCamera(j.x, j.y); L.Entites.indexer();
        // ⚠️ On regarde la cale : ACTION n'agit que sur ce qu'on regarde (test_regard_js.py).
        o.viser(cale);
        // Aucun char a portee : l'invite le dit, et le comptoir ne vend rien.
        for (const e of L.B.entites.slice()) if (e.type === 'vehicule' && Math.hypot(e.x - cale.x, e.y - cale.y) < c.rayon_px + 40) L.Entites.retirer(e);
        L.Entites.indexer();
        L.Missions.majInvite(j);
        const inviteSans = L.B.invite;
        const menuSans = L.Missions.menuContrebande(j, cale);
        const actifsSans = menuSans.items.filter(function (i) { return i.actif; }).length;
        // Un char gare a cote : on achete, et le prix monte.
        const v = o.char('auto', 30, 0, 0);
        L.Missions.majInvite(j);
        const inviteAvec = L.B.invite;
        const menu = L.Missions.menuContrebande(j, cale);
        const item = menu.items.find(function (i) { return i.libelle === 'CAISSE DE CIGARETTES'; });
        const prix1 = item.detail, avant = p.argent;
        item.faire();
        const prix2 = L.Missions.menuContrebande(j, cale).items.find(function (i) { return i.libelle === 'CAISSE DE CIGARETTES'; }).detail;
        L.Missions.menuContrebande(j, cale).items.find(function (i) { return i.libelle === 'CAISSE DE BOISSON'; }).faire();
        const paye = avant - p.argent;
        // Jusqu'au coffre plein, et pas une de plus.
        let tours = 0;
        while (L.Missions.caissesDe(v) < c.caisses_max && tours++ < 20) {
            L.Missions.menuContrebande(j, cale).items.find(function (i) { return i.libelle === 'CAISSE DE CIGARETTES'; }).faire();
        }
        const plein = L.Missions.menuContrebande(j, cale);
        const encoreActif = plein.items.some(function (i) { return i.libelle.indexOf('CAISSE DE') === 0 && i.actif; });
        L.Missions.majInvite(j);
        return { inviteSans: inviteSans, actifsSans: actifsSans, inviteAvec: inviteAvec,
                 prix1: prix1, prix2: prix2, paye: paye, cargaison: v.cargaison, caisses: L.Missions.caissesDe(v),
                 encoreActif: encoreActif, achetees: p.contrebande.achetees, invitePlein: L.B.invite, titre: menu.titre };
    }""")
    assert not r.get("pasDeCale"), "la ville n'a pas de cale"
    c = economie.CONTREBANDE
    assert r["inviteSans"] == "LA CALE DU NORVÉGIEN — VIENS EN CHAR"
    assert r["actifsSans"] == 0, "sans char, on achete quand meme"
    assert r["inviteAvec"] == "LA CALE DU NORVÉGIEN — 0/%d CAISSES" % c["caisses_max"]
    assert r["titre"] == "LA CALE DU NORVÉGIEN"
    assert r["prix1"] == "%d $" % economie.prix_achat("cigarettes", 0)
    assert r["prix2"] == "%d $" % economie.prix_achat("cigarettes", 1), "le prix ne monte pas"
    assert r["paye"] == economie.prix_achat("cigarettes", 0) + economie.prix_achat("boisson", 1)
    assert r["cargaison"]["boisson"] == 1 and r["caisses"] == c["caisses_max"]
    assert r["encoreActif"] is False, "le coffre deborde"
    assert r["achetees"] == c["caisses_max"]
    assert r["invitePlein"] == "LA CALE DU NORVÉGIEN — %d/%d CAISSES" % (c["caisses_max"], c["caisses_max"])


def test_le_comptoir_affiche_le_prix_du_jour_et_achete_la_cargaison(banc, paquet):
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        L.graine(4);
        const j = L.B.joueur, p = L.B.partie, c = L.B.defs.economie.contrebande;
        const districts = L.Monde.carte.def.districts.map(function (d) { return d.slug; });
        // Le prix du jour : dans la fourchette partout, pas le meme partout, et il bouge la nuit.
        const facteurs = districts.map(function (d) { return L.Missions.facteurDuJour(d, 'cigarettes'); });
        const dedans = facteurs.every(function (f) { return f >= c.facteur[0] && f <= c.facteur[1]; });
        const distincts = new Set(facteurs.map(function (f) { return Math.round(f * 100); })).size;
        const jour = p.jour; p.jour = jour + 1;
        const demain = districts.map(function (d) { return L.Missions.facteurDuJour(d, 'cigarettes'); });
        p.jour = jour;
        const bouge = demain.some(function (f, i) { return Math.abs(f - facteurs[i]) > 1e-9; });
        // Le comptoir du depanneur, le char devant avec trois caisses.
        const v = o.char('auto', 40, 0, 0);
        v.cargaison = { cigarettes: 3, boisson: 0 };
        L.B.interieur = { slug: 'depanneur', nom: 'Chez Ti-Paul' };
        L.B.exterieur = { entites: L.B.entites, x: v.x, y: v.y };
        const district = L.Monde.zoneA(v.x, v.y).district;
        const items = L.Missions.itemsRevente(L.B.interieur);
        const vente = items.find(function (i) { return i.libelle.indexOf('VENDRE') === 0; });
        const avant = p.argent;
        if (vente) vente.faire();
        const apres = L.Missions.itemsRevente(L.B.interieur);
        // Un commerce qui n'en prend pas n'affiche rien.
        const ailleurs = L.Missions.itemsRevente({ slug: 'armurerie', nom: 'Chez Gus' });
        L.B.interieur = null; L.B.exterieur = null;
        return { dedans: dedans, distincts: distincts, bouge: bouge, district: district,
                 prixDuJour: L.Missions.prixDuJour(district, 'cigarettes'),
                 libelles: items.map(function (i) { return i.libelle; }), vente: vente ? vente.detail : null,
                 gagne: p.argent - avant, reste: v.cargaison.cigarettes, apres: apres.length, ailleurs: ailleurs.length };
    }""")
    assert r["dedans"] is True and r["distincts"] >= 2 and r["bouge"] is True
    assert r["district"]
    assert r["libelles"][0].startswith("PRIX DU JOUR — ") and "CIGARETTES %d $" % r["prixDuJour"] in r["libelles"][0], r["libelles"]
    assert r["vente"] == "%d $" % (3 * r["prixDuJour"]), r
    assert r["gagne"] == 3 * r["prixDuJour"] and r["reste"] == 0
    assert r["apres"] == 1, "vendu, il ne reste que le prix du jour"
    assert r["ailleurs"] == 0


def test_la_police_fouille_le_char_saisi(banc, paquet):
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const j = L.B.joueur, p = L.B.partie;
        const v = o.char('auto', 40, 0, 0);
        v.cargaison = { cigarettes: 2, boisson: 3 };
        const seul = L.Missions.confisquerLaCargaison(v);
        const w = o.char('auto', -60, 0, 0);
        w.cargaison = { cigarettes: 4 };
        j.dernierVehicule = w;
        p.argent = 500;
        L.B.recherche.etoiles = 1;
        L.Missions.prison(null);
        return { seul: seul, videV: L.Missions.caissesDe(v), videW: L.Missions.caissesDe(w), saisi: !!w.saisi || w.saisi === 0 || p.fourriere.length > 0 };
    }""")
    assert r["seul"] == 5 and r["videV"] == 0
    assert r["videW"] == 0, "le char saisi part au lot avec ses caisses"
    assert r["saisi"] is True
