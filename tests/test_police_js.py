"""M4 — la police sur le terrain : cone, temoins, poursuite, arrestation, prison, autos.

⚠️ La regle de tout le module : rien n'est compte tant que ce n'est pas vu.
Chaque test pose ses agents lui-meme (`Police.creerAgent`) : attendre qu'une
patrouille passe rendrait le banc lent et capricieux.
"""

# Un agent pose a cote du joueur, sur une tuile marchable, qui le regarde.
# (L'aide vit DANS la fonction du banc : le banc ne prend qu'une expression.)
AGENT = """function (L, o) {
    function poserAgent(L, etat, distance) {
        const j = L.B.joueur;
        const essais = [[1, 0], [-1, 0], [0, 1], [0, -1], [1, 1], [-1, -1]];
        for (const e of essais) {
            const x = j.x + e[0] * distance, y = j.y + e[1] * distance;
            if (!L.Monde.marchablePieton(Math.floor(x / L.TT), Math.floor(y / L.TT))) continue;
            if (!L.Monde.ligneLibre(j.x, j.y, x, y)) continue;
            const a = L.Police.creerAgent(x, y, etat || 'flane');
            L.Entites.regarder(a, j.x - x, j.y - y);
            L.Entites.indexer();
            return a;
        }
        throw new Error('aucune tuile marchable autour du joueur');
    }
"""


def test_l_agent_voit_le_crime_et_va_voir(banc):
    r = banc(AGENT + """
        L.Jeu.commencer();
        const j = L.B.joueur;
        const a = poserAgent(L, 'flane', 48);
        const vu = L.Police.quelqu_un_voit(j.x, j.y, j);
        const dos = L.Police.creerAgent(a.x, a.y + 8, 'flane');
        L.Entites.regarder(dos, -(j.x - a.x), -(j.y - a.y));   // il tourne le dos
        L.Entites.indexer();
        const dosVoit = L.Police.voit(dos, j.x, j.y);
        return { vu: vu, etat: a.etat, but: a.but, dosVoit: dosVoit, agents: L.Police.agents().length };
    }""")
    assert r["vu"] is True
    assert r["etat"] == "enquete" and r["but"] is not None, "un agent qui voit un crime va voir"
    assert r["dosVoit"] is False, "un agent de dos ne voit rien"
    assert r["agents"] == 2


def test_l_agent_poursuit_et_arrete_le_joueur_immobile(banc, paquet):
    r = banc(AGENT + """
        L.Jeu.commencer();
        const j = L.B.joueur;
        L.B.partie.argent = 500;
        L.Police.ajouterChaleur(3);                 // une etoile
        const a = poserAgent(L, 'flane', 64);
        let arrive = -1;
        for (let i = 0; i < 300 && !L.B.menu; i++) { o.frame(1); if (a.etat === 'poursuit' && arrive < 0) arrive = i; }
        const menu = L.B.menu;
        const ferme = (function () { o.tape('Space'); return L.B.menu === menu; })();
        const avant = L.B.partie.argent;
        const item = menu.items.find(function (i) { return i.libelle.indexOf('SUIVRE') === 0; });
        item.faire(item); L.Hud.fermerMenu();
        o.frame(90);
        const poste = L.Monde.carte.points.find(function (q) { return q.slug === 'poste'; });
        return { arrive: arrive, titre: menu && menu.titre, resteOuvert: ferme, etoiles: L.B.recherche.etoiles,
                 paye: avant - L.B.partie.argent, casier: L.B.partie.casier, arme: L.B.partie.arme,
                 arrestations: L.B.partie.stats.arrestations, arrete: j.arrete,
                 auPoste: Math.hypot(j.x - (poste.x * L.TT + 8), j.y - (poste.y * L.TT + 20)) < 24 };
    }""")
    assert r["arrive"] >= 0, "l'agent qui voit un recherche se lance"
    assert r["titre"] == "ARRETE !"
    assert r["resteOuvert"] is True, "on ne se sauve pas d'une arrestation en fermant le menu"
    assert r["etoiles"] == 0 and r["casier"] == 1 and r["arrestations"] == 1
    assert r["paye"] == paquet["economie"]["amendes"][0][0]
    assert r["arme"] == "poings", "la prison confisque les armes"
    assert r["arrete"] is False and r["auPoste"] is True


def test_le_pot_de_vin_accepte_ou_refuse(banc, paquet):
    r = banc(AGENT + """
        L.Jeu.commencer();
        const j = L.B.joueur;
        L.B.partie.argent = 500;
        L.Police.ajouterChaleur(3);
        const a = poserAgent(L, 'poursuit', 12);
        o.frame(3);
        const menu = L.B.menu;
        const pot = menu.items.find(function (i) { return i.libelle === 'POT-DE-VIN'; });
        const avant = L.B.partie.argent;
        L.B.rng = function () { return 0; };        // l'agent accepte
        pot.faire(pot); L.Hud.fermerMenu();
        const accepte = { etoiles: L.B.recherche.etoiles, paye: avant - L.B.partie.argent, casier: L.B.partie.casier, agent: a.etat };
        // Deuxieme fois : il refuse, et c'est la prison avec une etoile de plus au dossier.
        L.Police.ajouterChaleur(3);
        j.arrete = false; a.etat = 'poursuit';
        o.frame(3);
        L.B.rng = function () { return 0.99; };
        const menu2 = L.B.menu;
        const pot2 = menu2.items.find(function (i) { return i.libelle === 'POT-DE-VIN'; });
        pot2.faire(pot2); L.Hud.fermerMenu();
        o.frame(90);
        return { accepte: accepte, refuse: { casier: L.B.partie.casier, etoiles: L.B.recherche.etoiles,
                 crimes: L.B.crimes.filter(function (c) { return c.type === 'pot_de_vin_refuse'; }).length } };
    }""")
    eco = paquet["economie"]
    assert r["accepte"]["etoiles"] == 0 and r["accepte"]["casier"] == 0 and r["accepte"]["agent"] == "flane"
    assert r["accepte"]["paye"] == eco["pots_de_vin"][0][0]
    assert r["refuse"]["casier"] == 1 and r["refuse"]["etoiles"] == 0
    assert r["refuse"]["crimes"] == 1, "un pot-de-vin refuse est un delit de plus"


def test_le_temoin_court_vers_l_agent_et_rapporte(banc, paquet):
    r = banc(AGENT + """
        L.Jeu.commencer();
        L.graine(3);
        const j = L.B.joueur;
        const a = poserAgent(L, 'flane', 96);
        L.Entites.regarder(a, -(j.x - a.x), -(j.y - a.y));   // il tourne le dos : il ne voit rien
        const t = o.poser('passant', 20, 0);
        t.probaTemoin = 1; t.etat = 'flane';
        L.Entites.regarder(t, -1, 0);                          // il regarde le joueur
        const crime = L.Police.signalerCrime('coup_pieton', j.x, j.y, L.Police.quelqu_un_voit(j.x, j.y, j));
        const vu = crime.vu, temoin = t.etat, avant = L.B.recherche.etoiles;
        let rapporte = -1;
        for (let i = 0; i < 600 && rapporte < 0; i++) { o.frame(1); if (crime.rapporte) rapporte = i; }
        return { vu: vu, temoin: temoin, avant: avant, rapporte: rapporte,
                 chaleur: L.B.recherche.chaleur + L.B.recherche.etoiles * 100,
                 agent: a.etat, vers: t.vers === a || t.etat !== 'temoin' };
    }""")
    assert r["vu"] is True, "le passant a vu"
    assert r["temoin"] == "temoin" and r["avant"] == 0, "vu par un passant, pas par un agent : rien n'est compte tant que ce n'est pas rapporte"
    assert 0 <= r["rapporte"] < 600, "le temoin a rejoint l'agent et lui a raconte"
    assert r["chaleur"] == paquet["recherche"]["chaleur_par_gravite"], "le crime rapporte chauffe, a sa gravite"
    assert r["agent"] in ("enquete", "poursuit")


def test_on_achete_le_silence_d_un_temoin(banc, paquet):
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const j = L.B.joueur;
        L.B.partie.argent = 100;
        const t = o.poser('passant', 16, 0);
        t.probaTemoin = 1; t.etat = 'flane';
        L.Entites.regarder(t, -1, 0);
        const crime = L.Police.signalerCrime('coup_pieton', j.x, j.y, false);
        L.Missions.majInvite(j);
        const invite = L.B.invite;
        const fait = L.Missions.interagir(j);
        o.frame(600);
        return { etat: t.etat, invite: invite, fait: fait, argent: L.B.partie.argent, rapporte: crime.rapporte,
                 etoiles: L.B.recherche.etoiles };
    }""")
    prix = paquet["economie"]["tarifs"]["silence_temoin"]
    assert "SILENCE" in r["invite"]
    assert r["fait"] is True and r["argent"] == 100 - prix
    assert r["rapporte"] is False and r["etoiles"] == 0, "un temoin paye n'a rien vu"


def test_les_etoiles_ne_tombent_que_hors_de_vue(banc, paquet):
    palier1 = paquet["recherche"]["paliers"][1]["decroissance_s"]
    r = banc(AGENT + """
        L.Jeu.commencer();
        const j = L.B.joueur;
        L.Police.ajouterChaleur(3);
        const a = poserAgent(L, 'flane', 40);
        a.etat = 'fige';                              // il te regarde sans bouger
        j.intouchable = true;                         // on observe : personne ne t'arrete
        o.frame(%d * 60 + 30);
        const vuParLAgent = L.B.recherche.etoiles;
        const vuCompteur = L.B.recherche.vu;
        const menu = L.B.menu;
        L.B.entites.filter(function (e) { return e.agent; }).forEach(function (e) { L.Entites.retirer(e); });
        L.B.recherche.vu = 0;
        const entre = L.Jeu.entrer({ interieur: 'poste' });  // et tu te caches dedans
        o.frame(%d * 60 + 30);
        return { vuParLAgent: vuParLAgent, vuCompteur: vuCompteur, menu: menu, entre: entre, cache: L.B.recherche.etoiles };
    }""" % (palier1, palier1))
    assert r["menu"] is None and r["entre"] is True
    assert r["vuParLAgent"] == 1 and r["vuCompteur"] < 10, "sous les yeux d'un agent, rien ne retombe"
    assert r["cache"] == 0, "cache dedans, on se fait oublier"


def test_a_trois_etoiles_les_autos_arrivent_et_l_agent_tire(banc):
    r = banc(AGENT + """
        L.Jeu.commencer();
        const j = L.B.joueur;
        L.Police.ajouterChaleur(9);                  // trois etoiles
        const a = poserAgent(L, 'poursuit', 80);
        j.intouchable = true;                         // on observe : personne ne t'arrete
        let autos = 0, balles = 0, sirene = false, dMin = Infinity, surRoute = 0, images = 0;
        for (let i = 0; i < 600; i++) {
            o.frame(1);
            autos = Math.max(autos, L.Police.autos().length);
            for (const v of L.Police.autos()) {
                dMin = Math.min(dMin, Math.hypot(v.x - j.x, v.y - j.y));
                if (!v.surRails) continue;                 // de pres, elle fonce ou elle s'arrete : hors rails
                images++;
                const tx = Math.floor(v.x / L.TT), ty = Math.floor(v.y / L.TT);
                if (L.Monde.estChaussee(tx, ty) || L.Monde.estPassage(tx, ty)) surRoute++;
            }
            balles += L.B.entites.filter(function (e) { return e.type === 'projectile' && e.tireur === a; }).length;
            sirene = sirene || L.Police.autos().some(function (v) { return v.sirene; });   // (pas d'AudioContext au banc)
        }
        const auto = L.Police.autos()[0];
        const cmd = auto ? L.Police.commandes(auto) : null;
        L.Police.remiseAZero();
        o.frame(120);
        return { etoiles: 3, autos: autos, balles: balles, sirene: sirene, cmd: cmd, dMin: dMin, surRoute: surRoute / Math.max(1, images),
                 apres: L.Police.autos().length, sireneApres: L.Police.autos().some(function (v) { return v.sirene; }) };
    }""")
    assert r["autos"] >= 1, "a trois etoiles, une auto de patrouille arrive"
    assert r["dMin"] < 160, "l'auto de patrouille n'a pas rejoint le joueur (elle fonce dans un mur ?)"
    assert r["surRoute"] > 0.9, "sur les rails, l'auto de patrouille suit les rues, pas les facades"
    assert r["balles"] > 0, "a trois etoiles, l'agent tire"
    assert r["sirene"] is True
    assert r["cmd"] is not None, "l'auto de patrouille est toujours la a la fin de la chasse"
    assert r["sireneApres"] is False, "la sirene se tait quand la chasse est finie"


def test_changer_de_char_hors_de_vue_fait_perdre_une_etoile(banc, paquet):
    deg = paquet["recherche"]["deguisement"]
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const j = L.B.joueur;
        L.Police.ajouterChaleur(6);                 // deux etoiles
        L.B.recherche.vu = %d * 60 + 1;             // hors de vue depuis assez longtemps
        const v = o.char('auto', 24, 0, 0);
        L.Vehicules.monter(j, v);
        return { etoiles: L.B.recherche.etoiles };
    }""" % deg["vehicule_s"])
    assert r["etoiles"] == 2 - deg["vehicule_etoiles"]


def test_les_affiches_recherche_a_deux_etoiles(banc, paquet):
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        L.B.joueur.intouchable = true;                // on observe : pas d'arrestation qui gele tout
        L.Police.ajouterChaleur(6);
        o.frame(400);
        const pendant = L.B.entites.filter(function (e) { return e.type === 'affiche'; }).length;
        L.Police.remiseAZero();
        o.frame(2);
        return { pendant: pendant, apres: L.B.entites.filter(function (e) { return e.type === 'affiche'; }).length };
    }""")
    assert 1 <= r["pendant"] <= paquet["recherche"]["police"]["affiches_max"]
    assert r["apres"] == 0
