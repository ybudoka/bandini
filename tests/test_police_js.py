"""M4 — la police sur le terrain : cone, temoins, poursuite, arrestation, prison, autos.

⚠️ La regle de tout le module : rien n'est compte tant que ce n'est pas vu.
Chaque test pose ses agents lui-meme (`Police.creerAgent`) : attendre qu'une
patrouille passe rendrait le banc lent et capricieux.
"""

# Un agent pose a cote du joueur, sur une tuile marchable, qui le regarde.
# (L'aide vit DANS la fonction du banc : le banc ne prend qu'une expression.)
# ⚠️ La voie doit etre libre de CORPS autant que de murs : depuis que la foule
# ne se traverse plus, un personnage plante entre les deux (Ti-Guy attend a
# l'est du terminus) arrete l'agent en chemin, exactement comme le ferait un
# arbre. On testerait alors la navigation en foule, pas l'arrestation.
AGENT = """function (L, o) {
    function poserAgent(L, etat, distance) {
        const j = L.B.joueur;
        const essais = [[1, 0], [-1, 0], [0, 1], [0, -1], [1, 1], [-1, -1]];
        for (const e of essais) {
            const x = j.x + e[0] * distance, y = j.y + e[1] * distance;
            if (!L.Monde.marchablePieton(Math.floor(x / L.TT), Math.floor(y / L.TT))) continue;
            if (!L.Monde.ligneLibre(j.x, j.y, x, y)) continue;
            const surLaVoie = L.B.entites.some(function (q) {
                if (!L.Entites.deboutDansLaFoule(q) || q === j) return false;
                const t = ((q.x - j.x) * (x - j.x) + (q.y - j.y) * (y - j.y)) / (distance * distance);
                if (t <= 0 || t >= 1) return false;
                return Math.hypot(j.x + (x - j.x) * t - q.x, j.y + (y - j.y) * t - q.y) < 16;
            });
            if (surLaVoie) continue;
            const a = L.Police.creerAgent(x, y, etat || 'flane');
            L.Entites.regarder(a, j.x - x, j.y - y);
            L.Entites.indexer();
            return a;
        }
        throw new Error('aucune tuile marchable et libre de monde autour du joueur');
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


def test_une_poursuite_ne_se_gagne_pas_en_enjambant_une_cloture(banc):
    """⚠️ LE piege du correctif des clotures : si franchir un grillage etait une
    capacite du joueur seul, la premiere cloture venue deviendrait l'exploit qui
    gagne toutes les poursuites — on enjambe, les agents restent plantes de
    l'autre cote.

    Franchir est donc une capacite de tout le monde, au meme prix : l'A* des
    agents traverse le grillage (a un cout plus eleve qu'une tuile), et l'agent
    l'enjambe pour de vrai, une seconde en haut comme nous."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const c = L.Monde.carte, j = L.B.joueur;
        // ⚠️ Une LONGUE cloture, et c'est tout le sel du juge : devant une
        // cloture d'une tuile, faire le tour coute moins cher que l'enjamber, et
        // un agent qui fait le tour a raison. C'est au milieu d'un grillage de
        // neuf tuiles que le choix se pose vraiment.
        const LONG = 9;
        let place = null;
        for (let ty = 4; ty < c.h - 4 && !place; ty++) {
            for (let tx = 4; tx < c.w - 4 - LONG && !place; tx++) {
                let course = 0;
                while (course < LONG + 6 && L.Monde.solidite(tx + course, ty) === 4
                       && L.Monde.solidite(tx + course, ty - 1) === 0
                       && L.Monde.solidite(tx + course, ty + 1) === 0) course++;
                if (course < LONG) continue;
                const mx = tx + (course >> 1);
                let libre = true;
                for (const d of [-3, -2, -1, 1, 2]) if (L.Monde.solidite(mx, ty + d) !== 0) libre = false;
                if (libre) place = { tx: mx, ty: ty, course: course };
            }
        }
        if (!place) throw new Error('aucune longue cloture enjambable avec de la place autour');
        L.B.entites = L.B.entites.filter(function (e) { return e.type === 'joueur'; });
        L.Entites.reindexerDecor(); L.Entites.indexer();
        // Le joueur d'un cote, l'agent lance de l'autre.
        j.x = place.tx * L.TT + 8; j.y = (place.ty + 2) * L.TT + 8;
        L.Monde.centrerCamera(j.x, j.y);
        const a = L.Police.creerAgent(place.tx * L.TT + 8, (place.ty - 2) * L.TT + 8, 'poursuit');
        L.Entites.indexer();
        L.B.recherche.etoiles = 2;
        const d0 = Math.hypot(a.x - j.x, a.y - j.y);
        let enjambe = false, images = 0;
        for (let i = 0; i < 600; i++) {
            o.frame(1);
            images++;
            L.B.recherche.etoiles = Math.max(2, L.B.recherche.etoiles);   // la chasse reste ouverte
            if (a.enjambe) enjambe = true;
            if (Math.floor(a.y / L.TT) > place.ty) break;
        }
        return { enjambe: enjambe, images: images, d0: d0, cote: Math.floor(a.y / L.TT) - place.ty,
                 cloture: place.ty, course: place.course, vivant: a.vivant, arrete: !!j.arrete };
    }""")
    assert r["enjambe"] is True, "l'agent n'a jamais enjambe : la cloture est un exploit"
    assert r["cote"] > 0, "l'agent est reste de l'autre cote de la cloture"
    assert r["images"] > 40, (
        "l'agent a franchi la cloture sans y perdre de temps : elle ne coute rien a la police"
    )


def test_l_agent_poursuit_et_arrete_le_joueur_immobile(banc, paquet):
    r = banc(AGENT + """
        L.Jeu.commencer();
        const j = L.B.joueur;
        L.B.partie.argent = 500;
        L.Police.ajouterChaleur(3);                 // une etoile
        // ⚠️ 30 px, pas 64 : a l'est du terminus Ti-Guy attend a 32 px, et
        // depuis que la foule ne se traverse plus, l'agent lance a 64 px vient
        // buter sur lui et n'arrive jamais — exactement comme sur un arbre.
        // ⚠️ ET IL EST LANCE, pas en ronde (14 sept. 2026) : il flanait, et ce
        // juge tenait alors a ce qu'un flaneur regarde dans la bonne direction
        // au bon moment — vrai a l'est du terminus jusqu'au jour ou les
        // batiments ont bouge, faux le lendemain, et l'agent s'en allait sans
        // jamais voir personne. QU'UN AGENT QUI VOIT SE LANCE est juge a cote
        // (`l'agent voit le crime et va voir`) ; ici, c'est l'ARRESTATION.
        const a = poserAgent(L, 'poursuit', 30);
        a.but = { x: j.x, y: j.y };
        a.vuT = 0;
        let arrive = -1;
        // ⚠️ On attend LE MENU D'ARRESTATION, pas « un menu » : n'importe quel
        // autre menu (une reponse de l'histoire, un comptoir) arretait la
        // boucle et le juge lisait le mauvais titre.
        const arrete = function () { return L.B.menu && L.B.menu.titre === 'ARRÊTÉ !'; };
        for (let i = 0; i < 300 && !arrete(); i++) { o.frame(1); if (arrete() && arrive < 0) arrive = i; }
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
    assert r["arrive"] >= 0, "l'agent lance sur un recherche ne l'arrete jamais"
    assert r["titre"] == "ARRÊTÉ !"
    assert r["resteOuvert"] is True, "on ne se sauve pas d'une arrestation en fermant le menu"
    assert r["etoiles"] == 0 and r["casier"] == 1 and r["arrestations"] == 1
    assert r["paye"] == paquet["economie"]["amendes"][0][0]
    assert r["arme"] == "poings", "la prison confisque les armes"
    assert r["arrete"] is False and r["auPoste"] is True


def test_en_courant_on_ne_seme_pas_un_agent_mais_en_sprintant_on_gagne_du_terrain(banc, paquet):
    """⚠️ LE juge du nouveau modèle d'endurance. Rendre la course **gratuite**
    (la ville fait 421 tuiles, on court tout le temps) casserait toutes les
    poursuites à pied si on s'arrêtait là : une course gratuite plus rapide
    que le policier, c'est s'échapper **toujours**, sans rien dépenser.

    La parade est celle que le dépôt s'est déjà donnée deux fois — le char
    rapide, les armes à feu : **la vitesse achète de la distance, jamais
    l'impunité.** Le policier court donc exactement à la vitesse de la course,
    et c'est le **sprint** — qui coûte du souffle — qui ouvre l'écart.

    On mesure les deux dans le même décor : mêmes 200 images, même ligne
    droite, le souffle plein dans les deux cas."""
    r = banc(AGENT + """
        L.Jeu.commencer();
        const j = L.B.joueur;
        // Une ligne droite degagee : on fuit vers l'est sans buter sur la ville.
        function fuir(sprint) {
            const d = o.ligneDroite();
            j.x = d.x; j.y = d.y;
            j.endurance = 100; j.surplus = 0; j.cafeine = 0;
            L.B.recherche.etoiles = 0; L.B.recherche.chaleur = 0;
            // ⚠️ Et la rue VIDE DE SES CHARS : la ligne droite est une voie, et ce juge
            // mesure la course a pied, pas le trafic. Un char passe entre le joueur et
            // l'agent — ou un velo tasse a la bordure — et l'ecart ne disait plus rien de
            // l'endurance : sur la base, quatre graines sur douze tombaient deja.
            L.B.entites = L.B.entites.filter(function (e) { return (e.type !== 'pieton' || !e.agent) && e.type !== 'vehicule'; });
            L.Entites.indexer();
            L.Police.ajouterChaleur(3);
            const a = poserAgent(L, 'poursuit', 40);
            a.but = null;
            const depart = Math.hypot(a.x - j.x, a.y - j.y);
            if (sprint) o.touche('ShiftLeft');
            o.touche('KeyD');
            for (let i = 0; i < 200; i++) o.frame(1);
            o.relacher('KeyD');
            if (sprint) o.relacher('ShiftLeft');
            const fin = Math.hypot(a.x - j.x, a.y - j.y);
            const r = { gagne: Math.round(fin - depart), souffle: Math.round(j.endurance) };
            L.Entites.retirer(a);
            return r;
        }
        const course = fuir(false);
        const sprint = fuir(true);
        return { course: course, sprint: sprint, tuile: L.TT };
    }""")
    # ⚠️ En courant : on ne gagne pas de terrain. On ne PERD pas non plus — on
    # ne se fait pas rattraper en marchant, la course reste la vitesse de
    # voyage. Une tuile de marge pour les virages du A* et les sous-pas.
    assert abs(r["course"]["gagne"]) <= r["tuile"], (
        "en courant, l'écart bouge de %s px : la course sème (ou se fait semer)" % r["course"]["gagne"]
    )
    assert r["course"]["souffle"] == 100, "courir a coûté du souffle : %s" % r["course"]["souffle"]
    # En sprintant : on gagne du terrain, et ça se paie.
    assert r["sprint"]["gagne"] > r["tuile"] * 3, (
        "un sprint ne gagne que %s px sur un agent : fuir à pied ne marche pas" % r["sprint"]["gagne"]
    )
    assert r["sprint"]["souffle"] < 100, "le sprint doit coûter du souffle"


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
        // ⚠️ **PAS DE ROULOTTE DANS LE DOS.** L'invite ACTION nomme le plus proche,
        // et la ville pose ses ambulants où elle veut : le 17 sept. 2026, la trame
        // a bougé, une roulotte à café s'est installée au terminus, et le juge
        // lisait « ROULOTTE À CAFÉ — 4 $ » au lieu du silence du témoin.
        L.B.defs.ambulants = [];
        for (const q of L.B.entites.slice()) if (q !== j && q.type !== 'joueur') L.Entites.retirer(q);
        const t = o.poser('passant', 16, 0);
        t.probaTemoin = 1; t.etat = 'flane';
        L.Entites.regarder(t, -1, 0);
        // ⚠️ On regarde le témoin : ACTION n'agit que sur ce qu'on regarde (test_regard_js.py).
        o.viser(t);
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
        // ⚠️ L'AGENT REGARDE A CHAQUE IMAGE. Au budget d'une sur trois, il ne regarde qu'aux
        // images ou `(B.t + a.id) %% 3 === 0` : une entite de plus creee avant lui (21 sept.
        // 2026, les entrees de garage des bungalows retiraient du decor) le faisait regarder
        // une ou deux images trop tard — il s'etait deja detourne pour flaner et ne voyait
        // plus rien. Le juge passait pour un numero sur trois ; le budget n'est pas sa regle.
        L.B.defs.recherche.police.regarde_toutes_les_images = 1;
        // ⚠️ L'agent reste a 'flane', que la police dirige (`gere`) : il te voit, remet
        // `vu` a zero, et se met en poursuite — sans t'arreter, tu es intouchable.
        // Il etait pose 'fige' (« il te regarde sans bouger ») : un agent fige n'est
        // JAMAIS consulte par `gere` (son `vuT` restait a 9999), donc il ne voyait
        // rien, et le juge ne passait que si un AUTRE agent, ne au hasard, arrivait
        // a temps — 3 graines sur 60 le faisaient tomber, sur la base comme apres
        // n'importe quel changement qui deplace un de (21 sept. 2026).
        const a = poserAgent(L, 'flane', 40);
        j.intouchable = true;                         // on observe : personne ne t'arrete
        o.frame(%d * 60 + 30);
        const vuParLAgent = L.B.recherche.etoiles;
        const vuCompteur = L.B.recherche.vu;
        const menu = L.B.menu;
        L.B.entites.filter(function (e) { return e.agent; }).forEach(function (e) { L.Entites.retirer(e); });
        L.B.recherche.vu = 0;
        const entre = o.entrer({ interieur: 'poste' });  // et tu te caches dedans
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
        // ⚠️ Ce juge regarde ce que les renforts FONT, pas quand ils partent : leur délai
        // (`renfort_s`, la tolérance du 22 sept. 2026) a son propre juge, et il dure plus
        // longtemps que cette boucle.
        L.B.defs.recherche.police.renfort_s = 0;
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


def test_a_cinq_etoiles_l_helico_te_survole_et_rien_ne_retombe(banc, paquet):
    palier5 = paquet["recherche"]["paliers"][5]
    assert palier5["helico"] and palier5["barrages"]
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const j = L.B.joueur;
        j.intouchable = true;
        // ⚠️ Ce juge regarde ce que les renforts FONT, pas quand ils partent : leur délai
        // (`renfort_s`, la tolérance du 22 sept. 2026) a son propre juge, et il dure plus
        // longtemps que cette boucle.
        L.B.defs.recherche.police.renfort_s = 0;
        L.Police.ajouterChaleur(15);                // cinq etoiles
        let apparu = -1, dMin = Infinity;
        for (let i = 0; i < 900; i++) {
            o.frame(1);
            const h = L.Police.helico();
            if (h && apparu < 0) apparu = i;
            if (h) dMin = Math.min(dMin, Math.hypot(h.x - j.x, h.y - j.y));
        }
        const vu = L.B.recherche.vu, etoiles = L.B.recherche.etoiles;
        L.Jeu.rendre();                              // il se dessine, avec son ombre
        L.Police.remiseAZero();
        let parti = -1;
        for (let i = 0; i < 900 && parti < 0; i++) { o.frame(1); if (!L.Police.helico()) parti = i; }
        return { apparu: apparu, dMin: dMin, vu: vu, etoiles: etoiles, parti: parti };
    }""")
    assert 0 <= r["apparu"] < 120, "a cinq etoiles, l'helico arrive"
    assert r["dMin"] < 90, "il vient te survoler"
    assert r["etoiles"] == 5 and r["vu"] < 5, "sous l'helico, rien ne retombe"
    assert 0 <= r["parti"] < 900, "la chasse finie, il s'en va"


# Cinq etoiles, le son branche et ses fichiers charges, et 400 images : l'helico
# est arrive et te survole. (Meme regle que `AGENT` : l'aide vit dans la fonction.)
# `poser(j)`, s'il est donne, place le joueur avant que la chasse commence.
SOUS_L_HELICO = """async function (L, o) {
    async function sousLHelico(L, o, poser) {
        L.Jeu.commencer();
        L.Son.reveiller();
        await o.attendre(); await o.attendre(); await o.attendre();
        L.B.joueur.intouchable = true;
        if (poser) { poser(L.B.joueur); L.Monde.centrerCamera(L.B.joueur.x, L.B.joueur.y); L.Entites.indexer(); }
        // ⚠️ Ce juge regarde ce que les renforts FONT, pas quand ils partent : leur délai
        // (`renfort_s`, la tolérance du 22 sept. 2026) a son propre juge, et il dure plus
        // longtemps que cette boucle.
        L.B.defs.recherche.police.renfort_s = 0;
        L.Police.ajouterChaleur(15);
        for (let i = 0; i < 400; i++) o.frame(1);
    }
"""


def test_dans_une_piece_l_helico_s_entend_sourd_et_se_tait_quand_il_repart(banc):
    """⚠️ Bug de Martin (21 sept. 2026) : « je suis resté avec un son
    d'hélicoptère de police ». La boucle `helico` ne se réglait que DEHORS, dans
    `majHelico` : on entrait dans une pièce sous l'hélico, et son bruit restait
    figé à son dernier volume, en plein air, pour toujours. Les étoiles
    tombaient, mais l'hélico ne repartait pas — il reste dans la ville mise de
    côté, où la police ne le cherchait plus — et rien n'éteignait la boucle.

    Dedans, on l'entend encore : plus bas, et SOURD (un passe-bas — le rotor à
    travers le toit). La chasse finie, il repart, et le bruit s'éteint avec
    lui, sans qu'on ait à ressortir."""
    r = banc(SOUS_L_HELICO + """
        o.brancherAudio(true);
        // ⚠️ Devant LA porte, pendant toute la chasse : dedans, l'helico tourne
        // au-dessus d'elle. Une porte a l'autre bout de la ville ferait baisser le
        // bruit par la DISTANCE, et le juge ne verrait plus le mur.
        const def = L.Monde.carte.def;
        let porte = null;
        await sousLHelico(L, o, function (j) {
            porte = def.portes.filter(function (q) { return q.interieur && def.interieurs[q.interieur]; })
                .sort(function (a, b) { return Math.hypot(a.x * L.TT - j.x, a.y * L.TT - j.y) - Math.hypot(b.x * L.TT - j.x, b.y * L.TT - j.y); })[0];
            j.x = porte.x * L.TT + 8; j.y = (porte.y + 1) * L.TT + 10;
        });
        const out = { charge: L.Son.estCharge('helico'), dehors: L.Son.volumeBoucle('helico'),
                      coupureDehors: L.Son.coupureBoucle('helico') };
        o.entrer(porte);
        out.piece = !!L.B.interieur;
        out.auNoir = L.Son.coupureBoucle('helico');   // la porte se ferme : c'est la qu'il devient sourd
        o.frame(60);
        out.dedans = L.Son.volumeBoucle('helico');
        out.coupureDedans = L.Son.coupureBoucle('helico');
        out.muettes = L.Son.contexte.sourcesMuettes();
        L.Police.remiseAZero();
        const la = function () { return L.B.exterieur.entites.some(function (e) { return e.type === 'helico'; }); };
        let tu = -1, parti = -1;
        for (let i = 0; i < 900 && (tu < 0 || parti < 0); i++) {
            o.frame(1);
            if (tu < 0 && !L.Son.boucleActive('helico')) tu = i;
            if (parti < 0 && !la()) parti = i;
        }
        out.tu = tu;
        out.encoreLa = parti < 0;
        out.entenduApres = L.Son.boucleActive('helico');
        out.toujoursDedans = !!L.B.interieur;
        return out;
    }""")
    assert r["charge"] and r["dehors"], f"l'helico ne s'entend pas dehors : le juge ne mesure rien ({r})"
    assert r["coupureDehors"] is None or r["coupureDehors"] >= 10000, "dehors, l'helico est deja sourd"
    assert r["piece"], "le joueur n'est pas entre"
    assert r["auNoir"] is not None and r["auNoir"] <= 400, (
        "l'helico ne devient sourd qu'apres le fondu, pas quand la porte se ferme : %s" % r["auNoir"]
    )
    assert 0 < r["dedans"] < r["dehors"] * 0.6, (
        "dedans, l'helico doit s'entendre encore, mais plus bas : %s dehors, %s dedans" % (r["dehors"], r["dedans"])
    )
    assert r["coupureDedans"] is not None and r["coupureDedans"] <= 400, (
        "dedans, l'helico doit s'entendre SOURD (passe-bas) : %s" % r["coupureDedans"]
    )
    assert r["muettes"] == 0, "le passe-bas a debranche la boucle de la sortie"
    assert 0 <= r["tu"] < 900, "la chasse finie, le bruit de l'helico tourne encore dans la piece"
    assert not r["encoreLa"], "la chasse finie, l'helico tourne encore au-dessus du toit"
    assert not r["entenduApres"], "l'helico reparti, son bruit est revenu"
    assert r["toujoursDedans"], "le juge devait rester dedans"


def test_le_bruit_de_l_helico_ne_survit_ni_a_une_partie_reprise_ni_au_titre(banc):
    """L'autre moitié de « être certain qu'il arrête » : l'hélico peut
    disparaître sans repartir. Une partie reprise (`commencer()` vide la ville)
    l'efface d'un coup, et le titre fige le monde où il tourne encore. Dans les
    deux cas, sa boucle n'avait plus personne pour l'éteindre."""
    r = banc(SOUS_L_HELICO + """
        o.brancherAudio(true);
        await sousLHelico(L, o);
        const out = { avant: L.Son.boucleActive('helico') };
        L.Jeu.commencer();
        o.frame(2);
        out.reprise = L.Son.boucleActive('helico');
        L.B.joueur.intouchable = true;
        L.Police.ajouterChaleur(15);
        for (let i = 0; i < 400; i++) o.frame(1);
        out.revenu = L.Son.boucleActive('helico');
        L.Jeu.retourTitre();
        o.frame(2);
        out.titre = L.Son.boucleActive('helico');
        return out;
    }""")
    assert r["avant"] and r["revenu"], f"l'helico ne s'entend pas : le juge ne mesure rien ({r})"
    assert r["reprise"] is False, "une partie reprise garde le bruit d'un helico qui n'existe plus"
    assert r["titre"] is False, "l'helico tourne encore sur l'ecran titre"


def test_a_cinq_etoiles_un_barrage_se_dresse_devant_le_char(banc):
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const j = L.B.joueur, d = o.ligneDroite();
        j.x = d.x; j.y = d.y; j.intouchable = true;
        L.B.defs.conduite.trafic.vehicules_max = 0;
        L.B.entites.filter(function (e) { return e.type === 'vehicule'; }).forEach(function (e) { L.Entites.retirer(e); });
        const v = o.char('auto', 0, 0, 0);
        L.Vehicules.monter(j, v);
        L.Police.ajouterChaleur(15);
        v.vitesse = 3;
        const b = L.Police.poserBarrage(v);
        const autos = L.Police.barrages();
        const surRoute = autos.every(function (a) { return L.Monde.estChaussee(Math.floor(a.x / L.TT), Math.floor(a.y / L.TT)); });
        const devant = b && b.x > v.x + 200;
        const agents = L.Police.agents().filter(function (a) { return Math.hypot(a.x - b.x, a.y - b.y) < 60; }).length;
        L.Police.remiseAZero();
        j.x = v.x = b.x - 900; j.y = v.y = b.y + 400;        // loin : le barrage se leve
        o.frame(120);
        return { pose: !!b, autos: autos.length, surRoute: surRoute, devant: devant, agents: agents,
                 travers: autos.length ? Math.abs(Math.abs(autos[0].angle) - Math.PI / 2) < 0.01 : null,
                 apres: L.Police.barrages().length };
    }""")
    assert r["pose"] and r["autos"] == 2, "deux autos en travers"
    assert r["surRoute"] and r["devant"], "sur la rue, devant toi"
    assert r["travers"] is True, "en travers de la voie"
    assert r["agents"] == 2, "deux agents derriere"
    assert r["apres"] == 0, "la chasse finie et hors de vue, le barrage se leve"


def test_un_casier_epais_te_fait_reconnaitre_de_plus_loin(banc, paquet):
    """⚠️ M11, première ligne : « le carnet du poste — plus il est épais, plus
    les agents te reconnaissent de loin ».

    Le casier pesait déjà sur l'amende et le pot-de-vin, c'est-à-dire **au
    comptoir, après coup**. Il fallait qu'il se sente **dans la rue** : c'est la
    différence entre un chiffre dans un menu et une règle de jeu.

    ⚠️ Et il ne vaut **que pour le joueur** : un casier épais n'aide pas la
    police à voir les passants. C'est un signalement, une photo au mur, pas une
    paire de jumelles."""
    v = paquet["recherche"]["vision"]
    plein = paquet["economie"]["casier_max"]
    r = banc(AGENT + """
        L.Jeu.commencer();
        const j = L.B.joueur;
        L.B.partie.heure = 0.5;                      // plein jour : la portée du jour
        const a = poserAgent(L, 'flane', 0);
        a.x = 400; a.y = 400; a.angle = 0;           // planté, le regard vers l'est
        L.Entites.indexer();
        const PLEIN = L.B.defs.economie.casier_max;
        // Jusqu'où il voit le JOUEUR (`reconnait`), et jusqu'où il voit
        // n'importe qui d'autre à la même place.
        const limite = function (casier, reconnait) {
            L.B.partie.casier = casier;
            let loin = 0;
            for (let d = 8; d < 40 * L.TT; d += 4) {
                j.x = a.x + d; j.y = a.y;
                if (!L.Police.voit(a, j.x, j.y, 'policier', reconnait)) break;
                loin = d;
            }
            return loin;
        };
        const out = { vierge: limite(0, true), une: limite(1, true), plein: limite(PLEIN, true),
                      absurde: limite(100000, true),
                      anonymeVierge: limite(0, false), anonymePlein: limite(PLEIN, false) };
        L.B.partie.casier = PLEIN;
        out.facteur = L.Police.porteeDuCasier();
        L.B.partie.casier = 0;
        out.facteurVierge = L.Police.porteeDuCasier();
        return out;
    }""")

    assert r["vierge"] > 0, "le décor du juge est faux : l'agent ne voit rien du tout"
    assert r["une"] > r["vierge"], "la première page du casier ne se voit pas"
    assert r["plein"] > r["vierge"], "un casier plein ne change rien : %s" % r
    # ⚠️ LE PLAFOND MORD : au-delà du casier maximum, plus rien ne bouge. Sans
    # lui, la police verrait à seize tuiles en pleine nuit et il n'y aurait plus
    # une ruelle où souffler.
    assert r["absurde"] == r["plein"], "un casier absurde allonge encore le cône : %s" % r
    attendu = min(v["casier_portee_max"], 1 + v["casier_portee_par_page"] * plein)
    assert abs(r["facteur"] - attendu) < 0.001, "le facteur ne suit pas la fiche : %s" % r
    assert r["facteurVierge"] == 1, "un casier vierge change déjà la portée : %s" % r
    # ⚠️ Et un passant reste vu à la même distance, casier plein ou vierge.
    assert r["anonymeVierge"] == r["anonymePlein"], (
        "un casier épais fait voir les PASSANTS de plus loin : c'est une paire de "
        "jumelles, pas un signalement (%s)" % r
    )
    assert r["anonymeVierge"] == r["vierge"], "le juge mesure deux choses différentes : %s" % r


# --- L'equipage d'une auto de patrouille --------------------------------------------------

# Une auto de patrouille lancee sur toi, a pied, sur une ligne droite de chaussee
# qu'on trouve dans la ville (seize tuiles, deux de large, sans mur entre les deux).
# Rien d'autre ne roule ni ne marche : on juge l'equipage, pas la circulation.
# (L'aide vit DANS la fonction du banc : le banc ne prend qu'une expression.)
PATROUILLE = """function (L, o) {
    function lancer(L, vitesse) {
        L.Jeu.commencer();
        const j = L.B.joueur, TT = L.TT, c = L.Monde.carte;
        let site = null;
        chercher: for (let ty = 3; ty < c.h - 3; ty++) for (let tx = 3; tx < c.w - 18; tx++) {
            let ok = true;
            for (let k = 0; k < 16 && ok; k++) if (!L.Monde.estChaussee(tx + k, ty) || !L.Monde.estChaussee(tx + k, ty + 1)) ok = false;
            if (ok && L.Monde.ligneLibre(tx * TT, ty * TT + 8, (tx + 15) * TT, ty * TT + 8)) { site = { tx: tx, ty: ty }; break chercher; }
        }
        if (!site) throw new Error('aucune ligne droite de seize tuiles de chaussee dans la ville');
        for (const e of L.B.entites.slice()) if (e !== j && (e.type === 'vehicule' || e.type === 'pieton')) L.Entites.retirer(e);
        j.x = (site.tx + 15) * TT + 8; j.y = site.ty * TT + 8; j.dansVehicule = null;
        j.intouchable = true;                       // on observe : personne ne t'arrete
        L.Police.ajouterChaleur(9);                 // trois etoiles : l'auto vient
        const v = L.Vehicules.creer('police', (site.tx + 2) * TT + 8, site.ty * TT + 8, 0,
                                    { conducteur: 'police', etat: 'roule', sirene: true, poursuite: true });
        v.vitesse = vitesse; v.vx = vitesse; v.vy = 0;
        L.Entites.indexer();
        return { j: j, v: v, site: site, avant: new Set(L.Police.agents().map(function (a) { return a.id; })) };
    }
"""


def test_l_equipage_ne_descend_que_d_une_auto_arretee(banc, paquet):
    """⚠️ Retour de Martin : « à plusieurs étoiles, la police arrive en voiture
    rapidement, les policiers en sortent trop vite et se font écraser par leur
    propre voiture. Quand les policiers en sortent, le véhicule ne devrait plus
    rouler, à moins qu'un seul policier en sorte. »

    Ils naissaient à ±14 px de l'auto pendant qu'elle roulait encore à 2,5–3,7
    px/image, et mouraient en une image. Puis elle reculait sur leurs corps (le
    frein, à l'arrêt, c'est la marche arrière : −1,45 px/image, au-dessus du
    seuil qui renverse). Le juge tient les quatre choses ensemble : jamais deux
    dehors tant qu'elle roule, l'auto GARÉE une fois l'équipage dehors, aucune
    marche arrière, et personne d'écrasé."""
    p = paquet["recherche"]["police"]
    r = banc(PATROUILLE + """
        const { j, v, avant } = lancer(L, 3.5);
        const equipage = new Set();
        const sorties = [];
        let dehorsEnRoulant = 0, vitesseMin = 0, ecart = 0, garee = null, blesses = 0, images = 0;
        for (let i = 0; i < 260; i++) {
            o.frame(1);
            const roule = Math.hypot(v.vx, v.vy);
            vitesseMin = Math.min(vitesseMin, v.vitesse);
            const dehors = L.Police.equipageDe(v).dehors;
            if (dehors > equipage.size) {
                const neufs = L.B.entites.filter(function (a) { return a.agent && !avant.has(a.id) && !equipage.has(a); })
                    .sort(function (a, b) { return Math.hypot(a.x - v.x, a.y - v.y) - Math.hypot(b.x - v.x, b.y - v.y); });
                for (const a of neufs.slice(0, dehors - equipage.size)) {
                    equipage.add(a);
                    const dx = a.x - v.x, dy = a.y - v.y, c = Math.cos(v.angle), s = Math.sin(v.angle);
                    sorties.push({ i: i, roule: roule, axial: dx * c + dy * s, lateral: -dx * s + dy * c });
                }
            }
            if (roule > L.B.defs.recherche.police.auto_arret_sous) dehorsEnRoulant = Math.max(dehorsEnRoulant, dehors);
            if (dehors >= 2) {
                garee = garee || { x: v.x, y: v.y };
                ecart = Math.max(ecart, Math.hypot(v.x - garee.x, v.y - garee.y));
                images++;
            }
            for (const a of equipage) if (!a.vivant || a.vie < a.vieMax || a.etat === 'assomme') blesses++;
        }
        return { dehors: L.Police.equipageDe(v).dehors, equipage: equipage.size, sorties: sorties, dehorsEnRoulant: dehorsEnRoulant,
                 vitesseMin: vitesseMin, ecart: ecart, blesses: blesses, images: images, demi: v.def.largeur / 2, longueur: v.def.longueur };
    }""")
    assert r["dehors"] == 2 and r["equipage"] == 2, "l'auto s'est arrêtée sur le joueur et personne n'en est sorti : %s" % r
    premier, second = r["sorties"]
    # ⚠️ « A moins qu'un seul policier en sorte » : le passager saute seul, au pas,
    # et le conducteur reste au volant. Deux dehors, elle ne roule plus.
    assert premier["roule"] < p["auto_passager_saute_sous"], "le passager saute d'une auto lancée : %s" % r
    assert second["roule"] < p["auto_arret_sous"], "le conducteur descend d'une auto qui roule encore : %s" % r
    assert second["i"] > premier["i"], "les deux sortent dans la même image : c'est l'ancien « tous d'un coup » : %s" % r
    assert r["dehorsEnRoulant"] <= 1, "deux agents dehors alors que l'auto roule : %s" % r
    # ⚠️ Par la portière, pas dans l'axe : c'est la que l'auto roule.
    for s in r["sorties"]:
        assert abs(s["lateral"]) >= r["demi"] + 4, "un agent descend contre la carrosserie, dans l'axe de l'auto : %s" % r
        assert abs(s["axial"]) < r["longueur"] / 2, "un agent descend loin devant ou derrière l'auto : %s" % r
    assert premier["lateral"] * second["lateral"] < 0, "les deux descendent du même côté : %s" % r
    assert r["images"] > 100, "le juge n'a pas regardé l'auto garée assez longtemps : %s" % r
    assert r["ecart"] < 0.5, "l'auto roule encore, équipage dehors : %s" % r
    assert r["vitesseMin"] > -0.05, "l'auto recule (le frein à l'arrêt, c'est la marche arrière) : %s" % r
    assert r["blesses"] == 0, "un agent a été blessé ou écrasé par son auto : %s" % r


def test_une_auto_de_patrouille_ne_renverse_pas_ses_agents(banc, paquet):
    """Le filet, sous la règle : même si un agent se trouve devant une auto de
    patrouille qui roule (elle repart avec l'équipage au flanc, une autre
    patrouille la frôle), elle le **pousse** hors de sa carrosserie — elle ne le
    renverse pas. Sans le filet, le même agent est mort en quelques images."""
    r = banc(PATROUILLE + """
        const { v } = lancer(L, 3.5);
        // L'agent se tient dans l'axe, entre l'auto et toi, a la portee d'un pas.
        const a = L.Police.creerAgent(v.x + 40, v.y, 'flane');
        L.Entites.indexer();
        let vitesseAuChoc = 0, touche = false;
        for (let i = 0; i < 20; i++) {
            a.vx = 0; a.vy = 0; a.etat = 'flane';                // il ne bouge pas : on le retient dans l'axe
            o.frame(1);
            if (Math.hypot(a.x - v.x, a.y - v.y) < v.def.longueur / 2 + a.r + 2) { touche = true; vitesseAuChoc = Math.max(vitesseAuChoc, Math.hypot(v.vx, v.vy)); }
        }
        return { touche: touche, vitesseAuChoc: vitesseAuChoc, vivant: a.vivant, vie: a.vie, vieMax: a.vieMax, etat: a.etat };
    }""")
    assert r["touche"], "le juge n'a jamais mis l'agent sous l'auto : %s" % r
    assert r["vitesseAuChoc"] >= paquet["conduite"]["physique"]["renverse_vitesse_min"], (
        "l'auto n'allait pas assez vite pour renverser : %s" % r)
    assert r["vivant"] and r["vie"] == r["vieMax"] and r["etat"] != "assomme", "l'auto de patrouille a renversé son propre agent : %s" % r


def test_la_chasse_finie_l_auto_freine_et_ne_recule_pas(banc):
    """Le même défaut, sans équipage : `frein` à l'arrêt, c'est la marche
    arrière. Quand la recherche tombe à zéro, l'auto de patrouille freinait —
    puis reculait à 1,45 px/image tant qu'on la voyait."""
    r = banc(PATROUILLE + """
        const { v } = lancer(L, 3.5);
        o.frame(20);
        L.Police.remiseAZero();
        let vitesseMin = 0;
        for (let i = 0; i < 200; i++) { o.frame(1); vitesseMin = Math.min(vitesseMin, v.vitesse); }
        return { vitesseMin: vitesseMin, vitesse: v.vitesse, x: v.x };
    }""")
    assert r["vitesseMin"] > -0.05, "la chasse finie, l'auto de patrouille recule : %s" % r
    assert abs(r["vitesse"]) < 0.05, "la chasse finie, l'auto ne s'est pas arrêtée : %s" % r


# Les deux agents sont descendus, l'auto est garee : le point de depart des juges qui suivent.
DEUX_DEHORS = PATROUILLE + """
    function descendreLesDeux(L, o, v) {
        for (let i = 0; i < 300 && L.Police.equipageDe(v).dehors < 2; i++) o.frame(1);
        return L.Police.equipageDe(v).dehors === 2;
    }
"""


def test_deux_dehors_l_auto_reste_immobile_jusqu_a_ce_qu_un_agent_reprenne_le_volant(banc):
    """⚠️ Retour de Martin : « si deux policiers sortent du véhicule, le véhicule
    reste immobile, à moins qu'un policier reprenne le volant — mais toujours
    logique : deux policiers par véhicule, un prend le volant, un seul peut en
    ressortir. »

    Avant, l'auto « repartait pleine » dès que tu étais à 150 px, ses deux
    agents restant à pied : une auto sans conducteur qui roule, et, la fois
    d'après, deux agents de plus. Maintenant : personne au volant, elle est
    garée ; les agents rentrent à pied ; le premier monté la reprend. Le juge
    tient l'arithmétique à chaque image — dehors + à bord = deux —, l'immobilité
    IMAGE PAR IMAGE tant que personne n'est à bord, et qu'elle repart ensuite.
    Le joueur s'éloigne à pied : les agents le suivent un moment, puis rentrent."""
    r = banc(DEUX_DEHORS + """
        const { j, v, site } = lancer(L, 3.5);
        if (!descendreLesDeux(L, o, v)) return { erreur: 'l equipage n est pas descendu' };
        const TT = L.TT, bout = site.tx * TT + 24, x0 = j.x;
        let sansVolant = 0, pas = 0, faux = 0, reprise = null, plusLoin = 0, maxAutour = 0, loinDeLAuto = 0, plusLoinApres = 0;
        let avant = { x: v.x, y: v.y, abord: 0 }, depart = null;
        for (let i = 0; i < 800; i++) {
            // Tu files vers l'autre bout de la ligne. ⚠️ Par un compteur a toi, pas par
            // `j.x - 2` : l'equipage se tient entre toi et le bout, et la foule ne se
            // traverse plus — le joueur restait colle derriere lui, et le juge ne
            // passait que si un agent ne ailleurs venait le decoincer (la tolerance,
            // 22 sept. 2026 : les renforts arrivent plus tard, et le de a bouge).
            j.x = Math.max(bout, x0 - 2 * (i + 1));
            o.frame(1);
            const eq = L.Police.equipageDe(v);
            if (eq.dehors + eq.abord !== 2 || eq.abord < 0 || eq.dehors < 0) faux++;
            maxAutour = Math.max(maxAutour, L.B.entites.filter(function (a) { return a.auto === v; }).length);
            plusLoin = Math.max(plusLoin, Math.hypot(j.x - v.x, j.y - v.y));
            for (const a of v.equipe) loinDeLAuto = Math.max(loinDeLAuto, Math.hypot(a.x - v.x, a.y - v.y));
            // Personne a bord, ni a l'image d'avant : elle n'a pas bouge d'un pixel.
            if (eq.abord === 0 && avant.abord === 0) {
                sansVolant++;
                pas = Math.max(pas, Math.hypot(v.x - avant.x, v.y - avant.y), Math.hypot(v.vx, v.vy));
            }
            if (eq.abord >= 1 && reprise === null) { reprise = i; depart = { x: v.x, y: v.y }; }
            if (depart) plusLoinApres = Math.max(plusLoinApres, Math.hypot(v.x - depart.x, v.y - depart.y));
            avant = { x: v.x, y: v.y, abord: eq.abord };
        }
        return { plusLoin: plusLoin, sansVolant: sansVolant, pas: pas, faux: faux, reprise: reprise, loinDeLAuto: loinDeLAuto,
                 apres: plusLoinApres, maxAutour: maxAutour, final: L.Police.equipageDe(v) };
    }""")
    assert "erreur" not in r, r
    assert r["plusLoin"] > 160, "le juge est faux : le joueur est resté sur l'auto : %s" % r
    assert r["faux"] == 0, "le compte de l'équipage est faux (dehors + à bord != 2) : %s" % r
    assert r["maxAutour"] <= 2, "plus de deux agents pour une auto : %s" % r
    assert r["loinDeLAuto"] > 30, "le juge est faux : les agents n'ont jamais quitté l'auto : %s" % r
    assert r["sansVolant"] > 30, "le juge n'a pas vu l'auto sans conducteur assez longtemps : %s" % r
    # ⚠️ LE COEUR : personne à bord, elle ne bouge pas — ni position, ni vitesse, image par image.
    assert r["pas"] < 0.05, "l'auto roule sans personne au volant : %s" % r
    assert r["reprise"] is not None, "personne n'a repris le volant : l'auto est garée pour toujours : %s" % r
    assert r["apres"] > 30, "un agent a repris le volant et l'auto ne repart pas : %s" % r


def test_un_seul_dehors_l_auto_peut_rouler_mais_pas_les_deux(banc):
    """« Un policier prend le volant, un seul policier peut en ressortir. » Le
    passager seul, dehors, ne retient pas l'auto (il saute pendant qu'elle finit
    de freiner) ; le conducteur qui descend à son tour, si. Et quand elle roule,
    jamais deux dehors — sur tout le trajet : l'arrivée, le départ, le retour."""
    r = banc(PATROUILLE + """
        const { j, v, site } = lancer(L, 3.5);
        let deuxDehorsEnRoulant = 0, unSeulEnRoulant = 0, deuxDehors = 0, plusDeDeux = 0;
        // Elle arrive, le passager saute, le conducteur descend ; tu files ; l'un remonte ; elle repart.
        for (let i = 0; i < 1000; i++) {
            if (i === 260) { j.x = site.tx * L.TT + 16; j.y = site.ty * L.TT + 8; }
            o.frame(1);
            const eq = L.Police.equipageDe(v), roule = Math.hypot(v.vx, v.vy);
            if (eq.dehors > 2) plusDeDeux++;
            if (eq.dehors === 2) deuxDehors++;
            if (roule > 0.15 && eq.dehors === 2) deuxDehorsEnRoulant++;
            if (roule > 0.15 && eq.dehors === 1) unSeulEnRoulant++;
        }
        return { deuxDehorsEnRoulant: deuxDehorsEnRoulant, unSeulEnRoulant: unSeulEnRoulant, deuxDehors: deuxDehors, plusDeDeux: plusDeDeux };
    }""")
    assert r["deuxDehors"] > 30, "le juge n'a jamais vu l'auto garée, équipage dehors : %s" % r
    assert r["plusDeDeux"] == 0, "plus de deux agents dehors pour une auto : %s" % r
    assert r["deuxDehorsEnRoulant"] == 0, "l'auto roule avec ses deux agents dehors : %s" % r
    # L'exception de Martin, vue : un agent dehors, l'auto roule encore (l'autre est au volant).
    assert r["unSeulEnRoulant"] > 0, "le passager ne saute jamais d'une auto qui finit de freiner : %s" % r


def test_une_auto_dont_l_equipage_est_mort_reste_garee_et_ne_retient_plus_les_renforts(banc):
    """Deux agents tués : personne ne reprendra le volant. L'auto reste garée —
    immobile —, mais elle ne compte plus dans les autos du palier : sans ça, la
    police n'enverrait plus jamais de renfort."""
    r = banc(DEUX_DEHORS + """
        // ⚠️ Ce juge regarde QUI tient la place d'un renfort, pas QUAND il vient : les
        // renforts d'une etoile neuve attendent `renfort_s` (la tolerance, 22 sept. 2026),
        // et son juge est `test_les_renforts_d_une_etoile_neuve_prennent_le_temps_de_venir`.
        L.B.defs.recherche.police.renfort_s = 0;
        const { j, v, site } = lancer(L, 3.5);
        if (!descendreLesDeux(L, o, v)) return { erreur: 'l equipage n est pas descendu' };
        const garee = { x: v.x, y: v.y };
        for (const a of v.equipe.slice()) { a.vivant = false; a.vie = 0; a.etat = 'mort'; }
        j.x = site.tx * L.TT + 16; j.y = site.ty * L.TT + 8;
        let ecart = 0, autos = 0;
        for (let i = 0; i < 500; i++) {
            o.frame(1);
            ecart = Math.max(ecart, Math.hypot(v.x - garee.x, v.y - garee.y));
            autos = Math.max(autos, L.Police.autos().length);
        }
        return { eq: L.Police.equipageDe(v), abandonnee: L.Police.abandonnee(v), ecart: ecart, autos: autos, equipage: v.equipage };
    }""")
    assert "erreur" not in r, r
    assert r["equipage"] == 0 and r["abandonnee"] is True, "l'équipage mort compte encore : %s" % r
    assert r["ecart"] < 0.5, "une auto sans équipage roule : %s" % r
    assert r["autos"] >= 2, "la police n'a pas envoyé de renfort : l'auto abandonnée retient la place d'une vivante : %s" % r


def test_le_vigile_prive_a_son_propre_cone_et_sa_propre_allure(banc):
    """⚠️ Infiltration : `Police.creerAgent(x, y, etat, 'garde')` fabrique un
    vigile prive, pas un policier — un cone a lui (`VISION.garde`, plus court),
    une palette a lui (on doit le reconnaitre avant qu'il se retourne), une
    matraque et pas un pistolet. `genreVision` est ce que `voit()` lit."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const j = L.B.joueur, TT = L.TT;
        const v = L.B.defs.recherche.vision;
        // A mi-chemin entre la portee d'un garde et celle d'un policier : hors
        // de porte du premier, dans celle du second.
        const d = (v.garde.jour + v.policier.jour) / 2 * TT;
        const dirs = [[1, 0], [-1, 0], [0, 1], [0, -1]];
        let place = null;
        for (const e of dirs) {
            const x = j.x + e[0] * d, y = j.y + e[1] * d;
            if (L.Monde.marchablePieton(Math.floor(x / TT), Math.floor(y / TT)) && L.Monde.ligneLibre(j.x, j.y, x, y)) { place = { x: x, y: y }; break; }
        }
        if (!place) return { erreur: 'aucune direction degagee autour du joueur' };
        // La MEME tuile pour les deux, l'un apres l'autre : la ligne de vue ne
        // depend alors que du cone de chacun, jamais d'un obstacle different.
        const garde = L.Police.creerAgent(place.x, place.y, 'flane', 'garde');
        L.Entites.regarder(garde, j.x - place.x, j.y - place.y);
        L.Entites.indexer();
        const out = {
            genreVision: garde.genreVision, metier: garde.metier, arme: garde.arme,
            swapsGarde: JSON.stringify(garde.swaps),
            gardeVoitLoin: L.Police.voit(garde, j.x, j.y, garde.genreVision),
        };
        L.Entites.retirer(garde);
        const policier = L.Police.creerAgent(place.x, place.y, 'flane');
        L.Entites.regarder(policier, j.x - place.x, j.y - place.y);
        L.Entites.indexer();
        out.memePalette = out.swapsGarde === JSON.stringify(policier.swaps);
        out.policierVoitLoin = L.Police.voit(policier, j.x, j.y, policier.genreVision);
        return out;
    }""")
    assert "erreur" not in r, r
    assert r["genreVision"] == "garde" and r["metier"] == "garde" and r["arme"] == "batte"
    assert r["memePalette"] is False, "un vigile ne porte pas le bleu de la police"
    assert r["gardeVoitLoin"] is False, "hors de sa portee, un garde ne voit pas comme un policier : %s" % r
    assert r["policierVoitLoin"] is True, "a la meme distance, un policier voit : %s" % r


def test_signalerCrime_compte_le_guet_d_un_garde_comme_celui_d_un_policier(banc):
    """⚠️ `signalerCrime` generalise aussi son `parAgent` : un garde qui a
    l'effraction dans son cone la compte tout de suite (`temoin: True`
    n'attend pas qu'un passant coure le raconter — le garde EST le temoin,
    exactement comme le policier qu'il remplace pour cette porte)."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const j = L.B.joueur;
        const garde = L.Police.creerAgent(j.x + 24, j.y, 'flane', 'garde');
        L.Entites.regarder(garde, j.x - garde.x, j.y - garde.y);
        L.Entites.indexer();
        L.B.recherche.chaleur = 0; L.B.recherche.etoiles = 0;
        // vu=false : sans le garde dans le cone, un delit a temoin ne compte pas tout de suite.
        const crime = L.Police.signalerCrime('effraction', j.x, j.y, false);
        return { rapporte: crime.rapporte, chaleur: L.B.recherche.chaleur };
    }""")
    assert r["rapporte"] is True, "un garde en cone doit compter comme un agent : %s" % r
    assert r["chaleur"] > 0


# --- La tolerance (demande de Martin en jouant, 22 sept. 2026) -----------------------
#
# « la police arrive trop rapidement et les etoiles aussi. il faut plus de tolerance ».
# Trois regles, un juge chacune : la jauge refroidit, un carambolage est UN delit, et
# les renforts d'une etoile neuve prennent le temps de venir (et jamais par une porte).


def test_la_chaleur_refroidit_apres_un_repit_mais_pas_les_etoiles(banc, paquet):
    """⚠️ La jauge ne redescendait JAMAIS : trois petits delits espaces de vingt
    minutes faisaient une etoile. Maintenant elle tient `chaleur_repit_s` apres le
    dernier delit compte, puis perd `chaleur_refroidit_par_s` a la seconde. Le
    delit oublie, le suivant repart de zero ; trois coup sur coup font toujours
    leur etoile ; et l'etoile, elle, ne refroidit pas — sous les yeux d'un agent,
    elle reste."""
    rech = paquet["recherche"]
    repit, par_s, g = rech["chaleur_repit_s"], rech["chaleur_refroidit_par_s"], rech["chaleur_par_gravite"]
    oubli = repit + -(-g // par_s) + 2          # le repit, puis le temps de fondre, en secondes
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const j = L.B.joueur, r = L.B.recherche;
        j.intouchable = true;                         // on observe la jauge : personne ne t'arrete
        L.Police.ajouterChaleur(1);
        const dabord = r.chaleur;
        o.frame(%(repit)d * 60 - 60);
        const avantLaFin = r.chaleur;
        o.frame((%(oubli)d - %(repit)d) * 60 + 60);
        const oublie = r.chaleur;
        L.Police.ajouterChaleur(1);
        const ensuite = r.chaleur + r.etoiles * 100;
        o.frame(60); L.Police.ajouterChaleur(1); o.frame(60); L.Police.ajouterChaleur(1);
        const serres = r.etoiles;
        for (let i = 0; i < (%(repit)d + 5) * 60; i++) { r.vu = 0; o.frame(1); }   // un agent te regarde
        return { dabord: dabord, avantLaFin: avantLaFin, oublie: oublie, ensuite: ensuite,
                 serres: serres, etoilesApres: r.etoiles, chaleurApres: r.chaleur };
    }""" % {"repit": repit, "oubli": oubli})
    assert r["dabord"] == g
    assert r["avantLaFin"] == g, "la jauge a refroidi avant la fin du repit : %s" % r
    assert r["oublie"] == 0, "la jauge ne refroidit pas : un petit delit pese toute la partie : %s" % r
    assert r["ensuite"] == g, "le delit d'apres ne repart pas de zero : %s" % r
    assert r["serres"] == 1, "trois delits coup sur coup ne font plus leur etoile : %s" % r
    assert r["etoilesApres"] == 1, "l'etoile a refroidi avec la jauge : elle ne tombe qu'hors de vue : %s" % r
    assert r["chaleurApres"] == 0, "le reste de la jauge ne refroidit pas une fois l'etoile tombee : %s" % r


def test_un_carambolage_ne_chauffe_qu_une_fois_et_pas_sans_temoin(banc, paquet):
    """⚠️ Chaque accrochage devant un passant etait une conduite dangereuse,
    BRUYANTE : trois chars touches, une etoile d'un coup. Deux regles, et sa
    fiche disait deja la seconde (« casser est un delit, avec son temoin qui
    rapporte ») : `repit_s` — le meme delit, compte de nouveau avant ce delai,
    ne chauffe pas une deuxieme fois — et `temoin` — il faut qu'un agent le
    VOIE, ou qu'un passant aille le raconter. Le repit ne glisse pas (sinon on
    conduirait comme un fou pour rien), et il n'est que pour CE delit : un coup
    a un agent, dans la foulee, compte."""
    rech = paquet["recherche"]
    g, delit = rech["chaleur_par_gravite"], rech["delits"]["conduite_dangereuse"]
    repit = delit["repit_s"]
    assert delit["temoin"] is True, "un accrochage n'est pas un coup de feu : il lui faut un temoin"
    assert repit < rech["chaleur_repit_s"], "le juge suppose que la jauge ne refroidit pas pendant le repit du delit"
    r = banc(AGENT + """
        L.Jeu.commencer();
        const j = L.B.joueur, r = L.B.recherche;
        j.intouchable = true;
        const pression = function () { return r.chaleur + r.etoiles * 100; };
        // 1. Personne en uniforme pour le voir : ca ne chauffe pas tout de suite,
        //    meme si un passant a tout vu — il faut qu'il aille le raconter.
        for (const q of L.B.entites.slice()) if (q.agent) L.Entites.retirer(q);
        const seul = L.Police.signalerCrime('conduite_dangereuse', j.x, j.y, true);
        const sansAgent = pression();
        // 2. Un agent le voit : ca compte — mais une seule fois par repit.
        const a = poserAgent(L, 'flane', 40);
        const ax = a.x, ay = a.y;
        const cogner = function () {
            a.x = ax; a.y = ay; a.etat = 'flane';
            L.Entites.regarder(a, j.x - ax, j.y - ay);
            return L.Police.signalerCrime('conduite_dangereuse', j.x, j.y, true);
        };
        const vu = cogner();
        const voit = L.Police.voit(a, j.x, j.y);
        cogner();
        o.frame(60);
        cogner();
        const rafale = pression();
        o.frame(%d * 60 + 30);
        cogner();
        const plusTard = pression();
        L.Police.signalerCrime('coup_policier', j.x, j.y, true);
        return { sansAgent: sansAgent, voit: voit, rafale: rafale, plusTard: plusTard,
                 autre: pression(), temoinSeul: seul.rapporte, vuParLAgent: vu.rapporte };
    }""" % repit)
    assert r["voit"] is True, "le juge est faux : l'agent ne voit pas le lieu du delit : %s" % r
    assert r["sansAgent"] == 0 and r["temoinSeul"] is False, "un accrochage chauffe encore sans que personne l'ait rapporte : %s" % r
    assert r["vuParLAgent"] is True, "un agent qui voit l'accrochage doit le compter : %s" % r
    assert r["rafale"] == g, "trois accrochages dans la foulee chauffent chacun : %s" % r
    assert r["plusTard"] == 2 * g, "passe le repit, le meme delit ne chauffe plus du tout : %s" % r
    assert r["autre"] == 2 * g + 2 * g, "le repit d'un delit en a fait taire un autre : %s" % r


def test_les_renforts_d_une_etoile_neuve_prennent_le_temps_de_venir(banc, paquet):
    """⚠️ Les renforts d'un palier naissaient a l'image ou l'etoile tombait, et
    couraient : trois secondes et demie plus tard, ils etaient la. Ceux de trois
    etoiles — deux agents a pied, une auto — partent maintenant `renfort_s` apres
    l'etoile, et arrivent quand meme. ⚠️ L'agent DEJA la n'est pas un renfort : il
    te voit et te poursuit dans la seconde."""
    s = paquet["recherche"]["police"]["renfort_s"]
    r = banc(AGENT + """
        L.Jeu.commencer();
        const j = L.B.joueur, r = L.B.recherche;
        j.intouchable = true;                         // on observe : personne ne t'arrete
        for (const q of L.B.entites.slice()) {
            if (q.agent || (q.type === 'vehicule' && q.conducteur === 'police')) L.Entites.retirer(q);
        }
        // Pas de patrouille : ce qui vient, ce sont les renforts, et rien d'autre.
        L.B.defs.recherche.police.patrouille_par_zone_max = 0;
        L.B.defs.recherche.police.regarde_toutes_les_images = 1;
        const la = poserAgent(L, 'flane', 40);
        L.Police.ajouterChaleur(9);                  // trois etoiles
        const t0 = L.B.t, deja = new Set([la.id]);
        let poursuit = -1, agent = -1, auto = -1;
        while (L.B.t - t0 < (%d + 20) * 60 && (agent < 0 || auto < 0 || poursuit < 0)) {
            o.frame(1);
            const t = L.B.t - t0;
            if (poursuit < 0 && la.etat === 'poursuit') poursuit = t;
            if (agent < 0 && L.Police.agents().some(function (a) { return !deja.has(a.id); })) agent = t;
            if (auto < 0 && L.Police.autos().length) auto = t;
        }
        return { poursuit: poursuit, agent: agent, auto: auto };
    }""" % s)
    assert 0 <= r["poursuit"] < 60, "l'agent deja la attend les renforts pour te poursuivre : %s" % r
    assert r["agent"] >= s * 60 - 2, "un agent de renfort est arrive avant le delai : %s" % r
    assert r["auto"] >= s * 60 - 2, "l'auto de renfort est arrivee avant le delai : %s" % r
    assert r["agent"] > 0 and r["auto"] > 0, "les renforts ne sont jamais venus : %s" % r


def test_un_renfort_ne_sort_jamais_d_une_porte(banc):
    """⚠️ `placeDeNaissance` fait sortir un passant sur trois d'une porte — parfois
    a l'ecran, a deux pas de toi. Un policier de renfort arrive de la rue, pas du
    salon d'a cote. (Le passant ordinaire, lui, garde ses portes.)"""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const j = L.B.joueur, r = L.B.recherche;
        for (const q of L.B.entites.slice()) if (q.agent) L.Entites.retirer(q);
        r.etoiles = 3; r.etoilesAvant = 3; r.renforts = 3; r.renfortN = 0; r.dernierVu = null;
        const essayer = function (porte) {
            L.Entites.placeDeNaissance = function () { return { x: j.x + 40, y: j.y, porte: porte }; };
            L.B.t = Math.ceil((L.B.t + 1) / 30) * 30;       // l'image ou la police peuple
            const avant = L.Police.agents().length;
            L.Police.peuplerAgents();
            return L.Police.agents().length - avant;
        };
        return { parLaPorte: essayer({ x: 0, y: 0 }), parLaRue: essayer(undefined) };
    }""")
    assert r["parLaRue"] == 1, "le juge est faux : le renfort ne nait meme pas de la rue : %s" % r
    assert r["parLaPorte"] == 0, "un renfort est sorti d'une porte : %s" % r
