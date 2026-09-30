"""Braquer un commerce, au banc (docs/jalons/braquer-un-commerce.md).

Une arme en main devant le comptoir d'un commis : le menu du comptoir s'ouvre comme d'habitude,
BRAQUER en dernière ligne, qui vide la caisse et fait monter la chaleur ; le commerce s'en souvient (il ne te sert plus, et sa caisse est presque vide
le lendemain) ; on ne braque pas sa propre propriété, ni à mains nues.
"""

from app import economie

#: Entrer dans une pièce et se planter devant son comptoir, une arme en main (ou pas).
DEVANT = """
  function devant(L, o, lieu, point, arme) {
    const B = L.B, j = B.joueur, M = L.Monde;
    const porte = (M.carte.def.portes || []).find(function (q) { return q.lieu === lieu && q.interieur; });
    j.x = porte.x * 16 + 8; j.y = (porte.y + 1) * 16 + 4; L.Entites.indexer();
    L.Jeu.entrer(porte); o.fondu();
    for (let k = 0; k < 200 && !B.interieur; k++) o.frame(1);
    const pt = B.interieur.points.find(function (q) { return q.type === point; });
    j.x = pt.x * 16 + 8; j.y = (pt.y + 1) * 16 + 8; j.angle = -Math.PI / 2; L.Entites.indexer();
    j.arme = arme; B.partie.arme = arme;
    o.frame(2);
    return pt;
  }
  function sortir(L, o) { L.Hud.fermerMenu && L.Hud.fermerMenu(); L.Jeu.sortir(); o.fondu(); for (let k = 0; k < 200 && L.B.interieur; k++) o.frame(1); }
"""


def test_arme_en_main_braquer_est_un_choix_du_comptoir(banc):
    """Au dépanneur, un pistolet en main : l'invite reste celle du comptoir, ACTION ouvre le menu
    habituel et ne prend rien ; BRAQUER est la DERNIÈRE ligne. Deux pressions d'ACTION ne braquent
    pas (retour de Martin, 30 sept. : « je veux avoir le choix de braquer ou non »)."""
    r = banc("function (L, o) {" + DEVANT + """
        L.Jeu.commencer();
        const B = L.B;
        B.partie.armes = B.partie.armes || {}; B.partie.armes.pistolet = { munitions: 12 };
        devant(L, o, 'depanneur', 'emplettes', 'pistolet');
        const invite = B.invite, argent = B.partie.argent;
        o.tape('KeyE', 2);
        const libelles = B.menu ? B.menu.items.map(function (i) { return i.libelle; }) : null;
        const curseur = B.menu ? B.menu.items[B.menu.curseur].libelle : null;
        o.tape('KeyE', 2);
        const deuxFois = { braque: !!(B.partie.braquages && B.partie.braquages.depanneur), crimes: B.crimes.length };
        return { invite: invite, libelles: libelles, curseur: curseur, gagneALOuverture: B.partie.argent - argent,
                 deuxFois: deuxFois };
    }""")
    assert r["invite"] != "BRAQUER", r
    assert r["libelles"] and r["libelles"][-1] == "BRAQUER", r
    assert r["curseur"] != "BRAQUER", "le curseur s'ouvre sur le crime"
    assert r["gagneALOuverture"] <= 0, r
    assert not r["deuxFois"]["braque"], "deux pressions d'ACTION ont braqué"


def test_la_ligne_braquer_vide_la_caisse_et_la_chaleur_monte(banc):
    """La ligne BRAQUER choisie : la caisse, l'alarme, deux étoiles, le commis le dit, et le menu
    se ferme."""
    r = banc("function (L, o) {" + DEVANT + """
        L.Jeu.commencer();
        const B = L.B;
        B.partie.armes = B.partie.armes || {}; B.partie.armes.pistolet = { munitions: 12 };
        devant(L, o, 'depanneur', 'emplettes', 'pistolet');
        o.tape('KeyE', 2);
        const argent = B.partie.argent, chaleur = B.recherche.chaleur;
        B.menu.curseur = B.menu.items.length - 1;
        o.tape('KeyE', 2);
        const commis = B.entites.find(function (e) { return e.type === 'pieton' && e.poste; });
        const crime = B.crimes[B.crimes.length - 1];
        return { gagne: B.partie.argent - argent, chaleur: B.recherche.chaleur - chaleur,
                 crime: crime ? { type: crime.type, gravite: crime.gravite, rapporte: crime.rapporte } : null, bulle: commis && commis.bulle ? commis.bulle.texte : null,
                 menu: B.menu ? B.menu.titre : null, braque: B.partie.braquages && B.partie.braquages.depanneur };
    }""")
    assert r["gagne"] == economie.BRAQUAGE["caisses"]["depanneur"], r
    assert r["chaleur"] > 0, r
    assert r["crime"] == {"type": "braquage", "gravite": 2, "rapporte": True}, r
    assert r["bulle"] == economie.BRAQUAGE["dit"], r
    assert r["menu"] is None, "le menu est resté ouvert après le braquage"
    assert r["braque"], r


def test_a_l_armurerie_on_achete_des_balles_arme_en_main(banc):
    """L'armurerie de Gus, un pistolet en main : son menu s'ouvre (ses armes), BRAQUER au bout,
    et y rester ne braque pas."""
    r = banc("function (L, o) {" + DEVANT + """
        L.Jeu.commencer();
        const B = L.B;
        B.partie.armes = B.partie.armes || {}; B.partie.armes.pistolet = { munitions: 12 };
        devant(L, o, 'armurerie', 'acheter', 'pistolet');
        o.tape('KeyE', 2);
        const n = B.menu ? B.menu.items.length : 0;
        // Un achat (le menu se refait) : BRAQUER reste au bout, une seule fois.
        L.Hud.rafraichirMenu && L.Hud.rafraichirMenu();
        const apres = B.menu ? B.menu.items.map(function (i) { return i.libelle; }) : null;
        return { n: n, apres: apres, braque: !!(B.partie.braquages && B.partie.braquages.armurerie) };
    }""")
    assert r["n"] > 2, r
    assert r["apres"][-1] == "BRAQUER" and r["apres"].count("BRAQUER") == 1, r
    assert not r["braque"], r


def test_le_commerce_s_en_souvient(banc):
    """Le lendemain : il ne te sert plus (même sans arme), et le rebraquer ne rend presque rien.
    Passé la rancune, la caisse est pleine de nouveau."""
    r = banc("function (L, o) {" + DEVANT + """
        L.Jeu.commencer();
        const B = L.B, p = B.partie, M = L.Missions;
        devant(L, o, 'depanneur', 'emplettes', 'pistolet');
        o.tape('KeyE', 2);
        B.menu.curseur = B.menu.items.length - 1;
        o.tape('KeyE', 2);
        const braque = !!(p.braquages && p.braquages.depanneur);
        p.jour += 1;
        // Sans arme : le commis refuse.
        B.joueur.arme = 'poings'; p.arme = 'poings';
        o.frame(2);
        const inviteSansArme = B.invite;
        o.tape('KeyE', 2);
        const refus = { menu: B.menu ? B.menu.titre : null, msg: B.msg };
        // Arme en main : PARTIR d'abord, BRAQUER ensuite — jamais d'office.
        B.joueur.arme = 'pistolet'; p.arme = 'pistolet';
        o.frame(2);
        o.tape('KeyE', 2);
        const arme = { libelles: B.menu ? B.menu.items.map(function (i) { return i.libelle; }) : null,
                       curseur: B.menu ? B.menu.items[B.menu.curseur].libelle : null };
        L.Hud.fermerMenu();
        // Rebraque : la caisse est presque vide.
        let argent = p.argent;
        M.braquer(B.interieur.points.find(function (q) { return q.type === 'emplettes'; }));
        const rebraque = p.argent - argent;
        // La rancune passee : pleine.
        p.jour += B.defs.economie.braquage.rancune_jours;
        argent = p.argent;
        M.braquer(B.interieur.points.find(function (q) { return q.type === 'emplettes'; }));
        return { braque: braque, inviteSansArme: inviteSansArme, refus: refus, arme: arme, rebraque: rebraque, plein: p.argent - argent };
    }""")
    caisse = economie.BRAQUAGE["caisses"]["depanneur"]
    assert r["braque"], r
    assert r["refus"]["menu"] is None, "le commerce braqué t'a servi"
    assert r["arme"] == {"libelles": ["PARTIR", "BRAQUER"], "curseur": "PARTIR"}, r
    assert r["rebraque"] == round(caisse * economie.BRAQUAGE["apres"]), r
    assert r["plein"] == caisse, r


def test_ni_a_mains_nues_ni_chez_soi(banc):
    """À mains nues, le comptoir reste un comptoir. Et un commerce qui est à toi ne se braque pas."""
    r = banc("function (L, o) {" + DEVANT + """
        L.Jeu.commencer();
        const B = L.B, M = L.Missions;
        const pt = devant(L, o, 'depanneur', 'emplettes', 'poings');
        const mainsNues = { invite: B.invite, braquable: M.braquable(B.joueur, pt) };
        B.joueur.arme = 'pistolet';
        B.partie.proprietes.depanneur = { jour: 1, caisse: 0 };
        const chezSoi = M.braquable(B.joueur, pt);
        delete B.partie.proprietes.depanneur;
        const ailleurs = M.braquable(B.joueur, pt);
        return { mainsNues: mainsNues, chezSoi: chezSoi, ailleurs: ailleurs };
    }""")
    assert r["mainsNues"]["braquable"] is False and r["mainsNues"]["invite"] != "BRAQUER", r
    assert r["chezSoi"] is False and r["ailleurs"] is True, r


def test_un_braquage_ne_rapporte_pas_plus_qu_une_heure_de_boulot():
    """⚠️ L'économie : la plus grosse caisse reste sous ce qu'une heure de taxi rapporte, et le
    lendemain le même comptoir ne vaut presque rien."""
    heure_de_taxi = economie.gain_boulot(economie.BOULOTS["taxi"]) * 6
    plus_grosse = max(list(economie.BRAQUAGE["caisses"].values()) + [economie.BRAQUAGE["defaut"]])
    assert plus_grosse < heure_de_taxi, (plus_grosse, heure_de_taxi)
    assert economie.BRAQUAGE["apres"] <= 0.2
    assert "kiosque" in economie.BRAQUAGE["jamais"], "Madame Thibodeau s'en souviendrait"
