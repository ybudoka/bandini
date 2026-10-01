"""Les triches qui manquaient (docs/jalons/les-triches-qui-manquaient.md) — Martin, 30 sept. 2026 :
« regarde s'il ne manquerait pas certaines triches ». La police et l'heure, les chars, les raccourcis
d'histoire, les frénésies et les territoires.

⚠️ AU BOUTON, PAS À LA FONCTION : chaque juge ouvre l'onglet TRICHES et presse SA ligne, par son
libellé (`presser`). Un juge qui appellerait la fonction ne verrait pas une ligne mal branchée.
"""

import pytest

#: Ouvre l'onglet TRICHES et presse la ligne `libelle` (ou celle d'une page déjà ouverte) : rend ce que
#: `faire` a rendu (vrai : la ligne ferme le menu).
PRESSER = """
    function presser(L, libelle, dansLaPage) {
        if (!dansLaPage) L.Hud.ouvrirMenu(L.Hud.menuDebug());
        const item = L.B.menu.items.find(function (i) { return i.libelle === libelle; });
        if (!item) throw new Error('pas de ligne ' + libelle + ' dans ' + L.B.menu.titre);
        return item.faire(item);
    }
"""


def jouer(banc, corps: str, **kw):
    return banc("function (L, o) {" + PRESSER + "L.Jeu.commencer();\n" + corps + "}", **kw)


# --- La police et l'heure ---------------------------------------------------------------------------


def test_la_police_oublie_efface_toutes_les_etoiles(banc):
    r = jouer(banc, """
        L.Police.etoilesAuMoins(4);
        const avant = L.B.recherche.etoiles;
        L.B.recherche.chaleur = 3;
        const rendu = presser(L, 'LA POLICE OUBLIE');
        return { avant: avant, apres: L.B.recherche.etoiles, chaleur: L.B.recherche.chaleur, rendu: rendu, msg: L.B.msg };
    """)
    assert r["avant"] == 4, "le juge n'a jamais eu d'étoiles à effacer"
    assert r["apres"] == 0 and r["chaleur"] == 0
    assert r["rendu"] is False and r["msg"] == "PLUS PERSONNE NE TE CHERCHE"


def test_etoiles_au_maximum_lance_la_poursuite(banc):
    r = jouer(banc, """
        const rendu = presser(L, 'ÉTOILES AU MAXIMUM');
        const une = { etoiles: L.B.recherche.etoiles, max: L.B.defs.recherche.etoiles_max, rendu: rendu };
        une.encore = presser(L, 'ÉTOILES AU MAXIMUM');
        une.msg = L.B.msg;
        return une;
    """)
    assert r["etoiles"] == r["max"] and r["rendu"] is True, "la ligne ferme le menu : la poursuite part"
    assert r["encore"] is False and r["msg"] == "DÉJÀ AU MAXIMUM"


@pytest.mark.parametrize("avant, jour_apres, heure_apres", [(0.4, 5, 0.525), (0.9, 6, 0.025)])
def test_heure_plus_trois_passe_minuit_en_un_seul_jour(banc, avant, jour_apres, heure_apres):
    r = jouer(banc, f"""
        const p = L.B.partie; p.jour = 5; p.heure = {avant};
        let jours = 0;
        const vrai = L.Missions.nouveauJour;
        L.Missions.nouveauJour = function () {{ jours++; return vrai.apply(this, arguments); }};
        presser(L, 'HEURE +3 H');
        const item = L.B.menu.items.find(function (i) {{ return i.libelle === 'HEURE +3 H'; }});
        return {{ jour: p.jour, heure: p.heure, jours: jours, detail: item.detail, texte: L.Monde.heureTexte() }};
    """)
    assert r["jour"] == jour_apres and r["heure"] == pytest.approx(heure_apres)
    assert r["jours"] == jour_apres - 5, "minuit passé, c'est UN vrai jour — pas zéro, pas deux"
    assert r["detail"] == r["texte"], "la ligne dit la nouvelle heure"


# --- Les chars ----------------------------------------------------------------------------------------


def test_chaque_char_de_la_rue_apparait_a_soi_sur_la_chaussee_sans_un_de(banc):
    """La page lit le catalogue : chaque char qui n'est pas un bateau y est, apparaît à côté, sur la
    route, À SOI, à la première couleur de sa fiche — et sans tirer un seul dé du jeu."""
    r = jouer(banc, """
        L.Hud.fermerMenu && L.Hud.fermerMenu();
        const j = L.B.joueur, x0 = j.x, y0 = j.y;
        const terre = L.B.defs.vehicules.filter(function (d) { return !d.eau; });
        L.Hud.ouvrirMenu(L.Hud.menuDebug()); presser(L, 'FAIRE APPARAÎTRE UN CHAR', true);
        const titre = L.B.menu.titre;
        const lignes = L.B.menu.items.filter(function (i) { return i.vehicule; }).map(function (i) { return i.vehicule; });
        const vrai = L.B.rng; let des = 0;
        L.B.rng = function () { des++; return vrai(); };
        const out = terre.map(function (d) {
            j.x = x0; j.y = y0;
            if (j.dansVehicule) L.Vehicules.descendre(j, true);
            const avant = L.B.entites.length;
            L.Hud.ouvrirMenu(L.Hud.menuDebug()); presser(L, 'FAIRE APPARAÎTRE UN CHAR', true);
            const rendu = presser(L, d.nom.toUpperCase(), true);
            const v = L.B.entites.slice(avant).find(function (e) { return e.type === 'vehicule' && e.slug === d.slug; });
            const c = { slug: d.slug, rendu: rendu, menu: !!L.B.menu, ok: !!v, msg: L.B.msg,
                        aToi: v && v.aToi, couleur: v && v.couleur === d.couleurs[0],
                        route: v && L.Monde.estRoute(Math.floor(v.x / 16), Math.floor(v.y / 16)),
                        loin: v && Math.hypot(v.x - j.x, v.y - j.y) };
            // Retire : seize chars laissés là prendraient toute la rue au dernier.
            if (v) L.Entites.retirer(v);
            return c;
        });
        L.B.rng = vrai;
        return { titre: titre, lignes: lignes, terre: terre.map(function (d) { return d.slug; }), out: out, des: des };
    """)
    assert r["titre"] == "FAIRE APPARAÎTRE UN CHAR"
    assert r["lignes"] == r["terre"] and "bateau" not in r["lignes"] and "auto" in r["lignes"]
    for c in r["out"]:
        assert c["ok"] and c["rendu"] is True and not c["menu"], c
        assert c["aToi"] and c["couleur"] and c["route"], c
        assert c["loin"] <= 8 * 16 * 1.5, c
    assert r["des"] == 0, "un char de triche a tiré un dé : tout le hasard qui suit glisse"


def test_pas_de_char_dans_une_piece(banc):
    r = jouer(banc, """
        const porte = L.Monde.carte.portes.find(function (q) { return q.interieur; });
        L.Jeu.entrer(porte); L.Jeu.finirTransition();
        const avant = L.B.entites.filter(function (e) { return e.type === 'vehicule'; }).length;
        L.Hud.ouvrirMenu(L.Hud.menuDebug()); presser(L, 'FAIRE APPARAÎTRE UN CHAR', true);
        const rendu = presser(L, 'BERLINE', true);
        return { dedans: !!L.B.interieur, rendu: rendu, msg: L.B.msg,
                 apres: L.B.entites.filter(function (e) { return e.type === 'vehicule'; }).length, avant: avant };
    """)
    assert r["dedans"], "le juge n'est jamais entré"
    assert r["rendu"] is False and r["msg"] == "SORS D'ABORD" and r["apres"] == r["avant"]


def test_reparer_le_char_qu_on_conduit_mais_pas_une_epave(banc):
    r = jouer(banc, """
        const j = L.B.joueur;
        const v = L.Vehicules.creer('auto', j.x + 20, j.y, 0, { etat: 'stationne', couleur: '#aa2222' });
        L.Vehicules.monter(j, v);
        v.vie = 12;
        presser(L, 'RÉPARER LE CHAR');
        const repare = { dans: j.dansVehicule === v, vie: v.vie, vieMax: v.vieMax, msg: L.B.msg };
        v.etat = 'epave'; v.vie = 0;
        presser(L, 'RÉPARER LE CHAR');
        repare.epave = v.vie; repare.msgEpave = L.B.msg;
        return repare;
    """)
    assert r["dans"], "le juge n'est jamais monté"
    assert r["vie"] == r["vieMax"] and r["msg"] == "BERLINE RÉPARÉ"
    assert r["epave"] == 0 and r["msgEpave"] == "C’EST UNE ÉPAVE"


# --- Les raccourcis d'histoire ----------------------------------------------------------------------


def test_toutes_les_proprietes_du_catalogue_et_les_planques_des_blocs(banc):
    r = jouer(banc, """
        const p = L.B.partie;
        const avant = Object.keys(p.proprietes).length;
        presser(L, 'TOUTES LES PROPRIÉTÉS');
        return { avant: avant, proprietes: Object.keys(p.proprietes).sort(),
                 catalogue: L.B.defs.economie.proprietes.map(function (q) { return q.slug; }).sort(),
                 planques: p.planques.slice().sort(),
                 blocs: L.B.defs.blocs.filter(function (b) { return b.planque; }).map(function (b) { return b.slug; }).sort(),
                 caisses: Object.keys(p.proprietes).map(function (k) { return p.proprietes[k].caisse; }) };
    """)
    assert r["avant"] == 0
    assert r["proprietes"] == r["catalogue"] and len(r["catalogue"]) >= 3
    assert r["blocs"], "aucun bloc ne dit avoir une planque : le paquet a perdu `planque`"
    assert r["planques"] == r["blocs"]
    assert set(r["caisses"]) == {0}


def test_tous_les_meubles_sont_deja_livres_sans_annonce(banc):
    r = jouer(banc, """
        const p = L.B.partie, d = L.Decoration.donnees();
        p.jour = 4;
        presser(L, 'TOUS LES MEUBLES');
        const attendus = [], livres = [];
        Object.keys(d.places).forEach(function (piece) {
            L.Decoration.meubles().forEach(function (m) {
                if (!d.places[piece][m.slug]) return;
                attendus.push(piece + ':' + m.slug);
                if (L.Decoration.livre(piece, m.slug)) livres.push(piece + ':' + m.slug);
            });
        });
        p.jour = 5;
        const annonce = L.Decoration.nouveauJour();
        return { attendus: attendus.length, livres: livres.length, annonce: annonce, msg: L.B.msg };
    """)
    assert r["attendus"] >= 3, "le catalogue de la planque n'est pas arrivé au banc"
    assert r["livres"] == r["attendus"]
    assert r["annonce"] == [], "une triche silencieuse ne se fait pas annoncer par le camion le lendemain"


def test_effacer_la_dette_la_regle_pour_de_vrai(banc):
    r = jouer(banc, """
        const p = L.B.partie;
        const avant = p.dette;
        const evenements = [];
        const vrai = L.Histoire.evenement;
        L.Histoire.evenement = function (nom) { evenements.push(nom); return vrai.apply(this, arguments); };
        presser(L, 'EFFACER LA DETTE');
        const une = { avant: avant, apres: p.dette, evenements: evenements };
        presser(L, 'EFFACER LA DETTE');
        une.msg = L.B.msg;
        return une;
    """)
    assert r["avant"] > 0, "la partie neuve n'a pas de dette : le juge ne mord pas"
    assert r["apres"] == 0 and "dette_reglee" in r["evenements"]
    assert r["msg"] == "LA DETTE EST DÉJÀ RÉGLÉE"


def test_vider_le_casier(banc):
    r = jouer(banc, """
        L.B.partie.casier = 4;
        presser(L, 'VIDER LE CASIER');
        return { casier: L.B.partie.casier, msg: L.B.msg };
    """)
    assert r == {"casier": 0, "msg": "CASIER VIDÉ"}


# --- Les frénésies et les territoires ----------------------------------------------------------------


def test_chaque_frenesie_se_lance_depuis_la_page(banc):
    r = jouer(banc, """
        const j = L.B.joueur;
        const out = L.Frenesies.toutes().map(function (f) {
            if (L.B.frenesie) L.Frenesies.finir(false, 'JUGE');
            L.Hud.ouvrirMenu(L.Hud.menuDebug()); presser(L, 'LANCER UNE FRÉNÉSIE', true);
            const rendu = presser(L, f.titre.toUpperCase(), true);
            const pos = L.Frenesies.position(f);
            return { slug: f.slug, rendu: rendu, menu: !!L.B.menu, lancee: L.B.frenesie && L.B.frenesie.slug,
                     loin: Math.hypot(j.x - pos.x, j.y - pos.y) };
        });
        return out;
    """)
    assert len(r) >= 4
    for f in r:
        assert f["rendu"] is True and not f["menu"] and f["lancee"] == f["slug"] and f["loin"] < 1, f


def test_une_frenesie_ne_se_lance_pas_pendant_une_mission_ni_reussie(banc):
    r = jouer(banc, """
        const f = L.Frenesies.toutes()[0];
        L.B.partie.mission = { slug: 'm1', etape: 0 };
        L.Hud.ouvrirMenu(L.Hud.menuDebug()); presser(L, 'LANCER UNE FRÉNÉSIE', true);
        const rendu = presser(L, f.titre.toUpperCase(), true);
        const une = { rendu: rendu, msg: L.B.msg, lancee: !!L.B.frenesie };
        L.B.partie.mission = null;
        L.B.partie.frenesies[f.slug] = { jour: 1, temps: 10 };
        L.Hud.ouvrirMenu(L.Hud.menuDebug()); presser(L, 'LANCER UNE FRÉNÉSIE', true);
        const item = L.B.menu.items.find(function (i) { return i.frenesie === f.slug; });
        une.actif = item.actif; une.detail = item.detail;
        return une;
    """)
    assert r["rendu"] is False and r["msg"] == "PAS PENDANT UNE MISSION" and not r["lancee"]
    assert r["actif"] is False and r["detail"] == "RÉUSSIE"


def test_une_nuit_des_gangs_prend_un_coin_et_rendre_les_coins_l_efface(banc):
    r = jouer(banc, """
        const p = L.B.partie, d = L.Territoires.donnees();
        // Un gang au plus fort, tous les autres a zero : la nuit doit lui donner au moins un coin.
        d.gangs.forEach(function (g, i) { p.forcesDesGangs[g] = i === 0 ? d.regles.force : 0; });
        presser(L, 'UNE NUIT DES GANGS');
        const pris = Object.keys(p.territoires).length, msgNuit = L.B.msg;
        presser(L, 'RENDRE LES COINS DES GANGS');
        return { pris: pris, msgNuit: msgNuit, apres: Object.keys(p.territoires).length,
                 forces: Object.keys(p.forcesDesGangs).length, msg: L.B.msg };
    """)
    assert r["pris"] >= 1, "la nuit n'a rien pris : le juge ne mord pas"
    assert "PRIS CETTE NUIT" in r["msgNuit"]
    assert r["apres"] == 0 and r["forces"] == 0
    assert r["msg"] == (f"{r['pris']} COINS RENDUS" if r["pris"] > 1 else "UN COIN RENDU")


# --- La foire fermée l'hiver (docs/jalons/les-sauts-de-triche-retrouvent-la-foire-l-hiver.md) ---------


def test_sauter_a_un_defi_de_la_foire_l_hiver_l_ouvre_et_la_bascule_la_recadenasse(banc):
    """Une partie commence en janvier, la foire est cadenassée : LANCER UN DÉFI vers le tir l'ouvre
    (la bascule FOIRE OUVERTE L'HIVER passe à OUI), et l'éteindre la recadenasse."""
    r = jouer(banc, """
        const avant = { hiver: L.Saisons.enHiver(), fermee: L.Foire.fermee() };
        L.Hud.ouvrirMenu(L.Hud.menuDebug()); presser(L, 'LANCER UN DÉFI', true);
        const tir = L.B.defs.defis.find(function (d) { return d.slug === 'tir'; });
        const rendu = presser(L, tir.titre.toUpperCase(), true);
        const ouverte = { rendu: rendu, triche: L.B.partie.triches.foire, fermee: L.Foire.fermee() };
        L.Hud.ouvrirMenu(L.Hud.menuDebug());
        const ligne = L.B.menu.items.find(function (i) { return i.libelle === 'FOIRE OUVERTE L\\'HIVER'; });
        const detail = ligne.detail;
        ligne.faire(ligne);
        return { avant: avant, ouverte: ouverte, detail: detail, apres: L.Foire.fermee(), eteinte: ligne.detail };
    """)
    assert r["avant"] == {"hiver": True, "fermee": True}, "le juge n'a jamais vu la foire cadenassée"
    assert r["ouverte"] == {"rendu": True, "triche": True, "fermee": False}
    assert r["detail"] == "OUI"
    assert r["apres"] is True and r["eteinte"] == "NON"


def test_le_bonimenteur_revient_quand_on_saute_chez_lui_l_hiver(banc):
    r = jouer(banc, """
        const avant = !!L.Histoire.donneur('bonimenteur');
        L.Hud.ouvrirMenu(L.Hud.menuDebug()); presser(L, 'CHEZ UN DONNEUR', true);
        const ligne = L.B.menu.items.find(function (i) { return i.personnage === 'bonimenteur'; });
        const rendu = ligne.faire(ligne);
        const e = L.Histoire.donneur('bonimenteur'), j = L.B.joueur;
        return { avant: avant, rendu: rendu, la: !!e, loin: e && Math.hypot(e.x - j.x, e.y - j.y),
                 triche: L.B.partie.triches.foire, absent: L.Histoire.absentLHiver(L.Histoire.personnage('bonimenteur')) };
    """)
    assert r["avant"] is False, "le Bonimenteur était déjà là : le juge ne voit pas l'hiver"
    assert r["rendu"] is True and r["la"] and r["loin"] <= 2.5 * 16
    assert r["triche"] is True and r["absent"] is False


def test_l_ete_un_saut_vers_la_foire_n_allume_rien(banc):
    r = jouer(banc, """
        L.B.partie.jour = 22;   // l'été (le 21 déménage le joueur)
        L.Hud.ouvrirMenu(L.Hud.menuDebug()); presser(L, 'LANCER UN DÉFI', true);
        const tir = L.B.defs.defis.find(function (d) { return d.slug === 'tir'; });
        presser(L, tir.titre.toUpperCase(), true);
        return { hiver: L.Saisons.enHiver(), triche: L.B.partie.triches.foire, fermee: L.Foire.fermee() };
    """)
    assert r == {"hiver": False, "triche": False, "fermee": False}


def test_le_saut_trouve_gilles_dans_la_cour_d_asphalte(banc):
    """Gilles se tient DANS le lot de la fourrière (de l'asphalte) : le saut se pose à côté de lui
    quand même, jamais sous un char saisi."""
    r = jouer(banc, """
        function sauter() {
            L.Hud.ouvrirMenu(L.Hud.menuDebug()); presser(L, 'CHEZ UN DONNEUR', true);
            const ligne = L.B.menu.items.find(function (i) { return i.personnage === 'gilles'; });
            return ligne.faire(ligne);
        }
        const j = L.B.joueur;
        sauter();
        // Un char saisi garé sur la place du premier saut : le second ne s'y pose pas.
        L.Vehicules.creer('auto', j.x, j.y, 0, { etat: 'stationne', couleur: '#333333' });
        j.x += 400;
        const rendu = sauter();
        const e = L.Histoire.donneur('gilles');
        const tx = Math.floor(j.x / 16), ty = Math.floor(j.y / 16);
        return { rendu: rendu, msg: L.B.msg, loin: Math.hypot(e.x - j.x, e.y - j.y), chaussee: L.Monde.estChaussee(tx, ty),
                 sousUnChar: L.B.entites.some(function (v) { return v.type === 'vehicule' && v.vivant && Math.hypot(v.x - j.x, v.y - j.y) < 16; }) };
    """)
    assert r["rendu"] is True, r
    assert 0.75 * 16 <= r["loin"] <= 2.5 * 16
    assert r["chaussee"] is True, "Gilles n'est plus dans sa cour d'asphalte : ce juge ne garde plus rien"
    assert r["sousUnChar"] is False
