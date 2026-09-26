"""Braquer un commerce, au banc (docs/jalons/braquer-un-commerce.md).

Une arme en main devant le comptoir d'un commis : l'invite dit BRAQUER, ACTION vide la caisse et
fait monter la chaleur ; le commerce s'en souvient (il ne te sert plus, et sa caisse est presque vide
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


def test_arme_en_main_le_comptoir_se_braque_et_la_chaleur_monte(banc):
    """Au dépanneur, un pistolet en main : BRAQUER ; ACTION rend la caisse, l'alarme sonne, la
    chaleur monte de deux étoiles, et le commis le dit."""
    r = banc("function (L, o) {" + DEVANT + """
        L.Jeu.commencer();
        const B = L.B;
        B.partie.armes = B.partie.armes || {}; B.partie.armes.pistolet = { munitions: 12 };
        devant(L, o, 'depanneur', 'emplettes', 'pistolet');
        const invite = B.invite, argent = B.partie.argent, chaleur = B.recherche.chaleur;
        o.tape('KeyE', 2);
        const commis = B.entites.find(function (e) { return e.type === 'pieton' && e.poste; });
        const crime = B.crimes[B.crimes.length - 1];
        return { invite: invite, gagne: B.partie.argent - argent, chaleur: B.recherche.chaleur - chaleur,
                 crime: crime ? { type: crime.type, gravite: crime.gravite, rapporte: crime.rapporte } : null, bulle: commis && commis.bulle ? commis.bulle.texte : null,
                 menu: B.menu ? B.menu.titre : null, braque: B.partie.braquages && B.partie.braquages.depanneur };
    }""")
    assert r["invite"] == "BRAQUER", r
    assert r["gagne"] == economie.BRAQUAGE["caisses"]["depanneur"], r
    assert r["chaleur"] > 0, r
    assert r["crime"] == {"type": "braquage", "gravite": 2, "rapporte": True}, r
    assert r["bulle"] == economie.BRAQUAGE["dit"], r
    assert r["menu"] is None, "ACTION a ouvert le comptoir au lieu de braquer"
    assert r["braque"], r


def test_le_commerce_s_en_souvient(banc):
    """Le lendemain : il ne te sert plus (même sans arme), et le rebraquer ne rend presque rien.
    Passé la rancune, la caisse est pleine de nouveau."""
    r = banc("function (L, o) {" + DEVANT + """
        L.Jeu.commencer();
        const B = L.B, p = B.partie, M = L.Missions;
        devant(L, o, 'depanneur', 'emplettes', 'pistolet');
        o.tape('KeyE', 2);
        p.jour += 1;
        // Sans arme : le commis refuse.
        B.joueur.arme = 'poings'; p.arme = 'poings';
        o.frame(2);
        const inviteSansArme = B.invite;
        o.tape('KeyE', 2);
        const refus = { menu: B.menu ? B.menu.titre : null, msg: B.msg };
        // Arme en main : la caisse est presque vide.
        B.joueur.arme = 'pistolet';
        let argent = p.argent;
        M.braquer(B.interieur.points.find(function (q) { return q.type === 'emplettes'; }));
        const rebraque = p.argent - argent;
        // La rancune passee : pleine.
        p.jour += B.defs.economie.braquage.rancune_jours;
        argent = p.argent;
        M.braquer(B.interieur.points.find(function (q) { return q.type === 'emplettes'; }));
        return { inviteSansArme: inviteSansArme, refus: refus, rebraque: rebraque, plein: p.argent - argent };
    }""")
    caisse = economie.BRAQUAGE["caisses"]["depanneur"]
    assert r["refus"]["menu"] is None, "le commerce braqué t'a servi"
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
