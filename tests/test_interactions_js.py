"""Le décor, les bêtes et les gens répondent, côté navigateur : on s'assoit sur un
banc, on fouille une poubelle, on boit à la fontaine, on ouvre une borne, on
laisse un dollar à l'artiste et on prend le touriste en photo.

⚠️ **Chaque geste se juge PAR LE BOUTON** (`o.tape('KeyE')`), pas en appelant la
fonction : la chaîne d'ACTION affame ce qui la suit, et un juge qui appelle
`Interactions.utiliserSurLeDecor` ne voit jamais le bouton cassé. Les tirages
(`B.rng`) se figent, eux, autour de l'appel — le banc est un juge, il ne tire pas
à pile ou face.

⚠️ Et **l'invite et le geste disent la même chose** : la même fonction les sert.
"""

from app import interactions

#: Les outils que chaque scénario reprend. ⚠️ On se plante DEVANT le décor (ni porte,
#: ni arme par terre, ni char sous la main) et on efface les passants d'alentour : un
#: juge d'ACTION ne mesure pas la foule qui passait par là.
OUTILS = """
    L.Jeu.commencer();
    const j = L.B.joueur, p = L.B.partie;
    function nettoyer() {
        for (const e of L.Entites.autour(j.x, j.y, 100, function (q) { return q.type === 'pieton' || q.type === 'vehicule'; })) L.Entites.retirer(e);
        L.Entites.indexer();
    }
    function devant(type, dy) {
        const liste = L.B.entites.filter(function (e) { return e.type === 'decor' && e.decor === type && !e.brise; });
        for (const d of liste) {
            j.x = d.x; j.y = d.y + (dy === undefined ? 14 : dy); j.vx = 0; j.vy = 0; j.roule = 0;
            L.Monde.centrerCamera(j.x, j.y); nettoyer(); o.viser(d);
            if (L.Monde.porteDevant(j) || L.Combat.objetSousLaMain(j) || L.Vehicules.vehiculeSousLaMain(j)) continue;
            if (!L.Monde.marchablePieton(Math.floor(j.x / L.TT), Math.floor(j.y / L.TT))) continue;
            return d;
        }
        return null;
    }
    function invite() { L.Missions.majInvite(j); return L.B.invite; }
    // Une AUTRE pression, une image plus tard — et personne n'est venu s'y planter entre-temps.
    // ⚠️ `o.frame(1)` ne fait pas toujours avancer la simulation d'un pas (l'accumulateur d'images) :
    // on attend que `B.t` ait bougé, sinon deux gestes tombent dans la meme image de jeu.
    function suivant() { const t = L.B.t; for (let k = 0; k < 6 && L.B.t === t; k++) o.frame(1); nettoyer(); }
    function figer(v, f) { const r = L.B.rng; L.B.rng = function () { return v; }; try { return f(); } finally { L.B.rng = r; } }
"""


def jouer(banc, corps):
    return banc("function (L, o) {" + OUTILS + corps + "}")


# --- Le catalogue ---------------------------------------------------------------


#: Un chat, posé et laissé confiant — pour les scénarios qui n'ont besoin que de LUI,
#: pas de tout l'appareil de `test_betes_js.py`. ⚠️ Elle cherche son coin comme
#: `Entites.chezElle` le veut (le chat vit dans les ruelles) : un `devant('chat')`
#: sur `L.B.entites` ne trouverait jamais rien, les bêtes vivent dans `L.B.betes`.
CHAT = """
    function unChat() {
        for (const e of L.Entites.betes()) L.Entites.retirer(e);
        const c = L.Monde.carte, TT = L.TT;
        for (let ty = 4; ty < c.h - 4; ty++) for (let tx = 4; tx < c.w - 4; tx++) {
            if (!L.Entites.chezElle('chat', tx, ty)) continue;
            j.x = tx * TT + 8 + 300; j.y = ty * TT + 8;
            L.Monde.centrerCamera(j.x, j.y); L.Entites.indexer();
            for (let i = 0; i < 400 && !L.Entites.betes().filter(function (e) { return e.espece === 'chat'; }).length; i++) o.frame(1);
            const vus = L.Entites.betes().filter(function (e) { return e.espece === 'chat'; });
            if (vus.length) return vus[0];
        }
        return null;
    }
"""


def test_le_catalogue_ne_promet_rien_qui_n_existe_pas(banc, racine):
    """Chaque décor nommé existe dans `DECORS`, chaque pose de siège est dessinée."""
    noms = set()
    for gabarit in (interactions.ASSEOIR["sieges"], interactions.FOUILLER["decors"]):
        noms |= set(gabarit)
    noms |= set(interactions.BOIRE["decors"]) | set(interactions.BARBECUE["decors"]) | set(interactions.BORNE["decors"])
    r = banc("""function (L, o) {
        const decors = %s, poses = %s;
        return { manquants: decors.filter(function (d) { return !L.DECORS[d]; }),
                 poses: poses.filter(function (q) {
                     return !L.SPRITES.joueur.poses[q] && !L.SPRITES.joueur.poses[q.replace(/_(gauche|droite)$/, '_cote')];
                 }) };
    }""" % (sorted(noms), sorted({s["pose"] for s in interactions.ASSEOIR["sieges"].values()})))
    assert r["manquants"] == [], "un decor nomme dans le catalogue n'existe pas : %s" % r["manquants"]
    assert r["poses"] == [], "une pose de siege que le corps du joueur ne dessine pas : %s" % r["poses"]


# --- S'asseoir ------------------------------------------------------------------


def test_on_s_assoit_sur_un_banc_par_le_bouton_et_le_stick_nous_leve(banc):
    c = interactions.ASSEOIR
    r = jouer(banc, """
        const d = devant('banc');
        if (!d) return { pasDeBanc: true };
        const avant = { x: j.x, y: j.y };
        const inviteAvant = invite();
        j.endurance = 10; j.vie = 30; p.jour = 1;
        o.tape('KeyE');
        const assis = !!j.assis, face = j.face, sur = { x: j.x - d.x, y: j.y - d.y };
        const inviteAssis = invite();
        // Le souffle remonte plus vite assis que debout : on mesure les deux, a l'identique.
        const s0 = j.endurance; o.frame(30); const gainAssis = j.endurance - s0;
        const encore = !!j.assis;
        o.touche('KeyD'); o.frame(2); o.relacher('KeyD');
        const leve = !j.assis, bouge = j.x - avant.x;
        j.endurance = 10; const t0 = j.endurance; o.frame(30); const gainDebout = j.endurance - t0;
        return { inviteAvant: inviteAvant, assis: assis, face: face, sur: sur, inviteAssis: inviteAssis,
                 gainAssis: gainAssis, gainDebout: gainDebout, encore: encore, leve: leve, bouge: bouge };
    """)
    assert not r.get("pasDeBanc"), "la ville n'a pas un banc devant lequel se planter"
    assert r["inviteAvant"] == c["invite"], "le banc annonce ce qu'ACTION va faire"
    assert r["assis"], "ACTION devant un banc doit nous asseoir"
    assert r["face"] == c["sieges"]["banc"]["pose"]
    assert (r["sur"]["x"], r["sur"]["y"]) == (c["sieges"]["banc"]["dx"], c["sieges"]["banc"]["dy"]), \
        "le corps se pose sur l'assise, pas a cote"
    assert r["inviteAssis"] == "SE LEVER"
    assert r["encore"], "assis, on reste assis tant qu'on ne pousse pas"
    assert r["gainAssis"] > r["gainDebout"] * (c["souffle_x"] - 0.3), \
        "le souffle doit remonter %s fois plus vite assis que debout" % c["souffle_x"]
    assert r["leve"], "la premiere poussee du stick nous leve"
    assert r["bouge"] > 0, "et le pas qui suit est le notre, dans la meme image"


def test_assis_les_forces_reviennent_lentement_et_pas_au_dela_du_plafond(banc):
    c = interactions.ASSEOIR
    r = jouer(banc, """
        const d = devant('banc');
        if (!d) return { pasDeBanc: true };
        j.vie = 30; o.tape('KeyE');
        const v0 = j.vie; o.frame(%d + 5); const gagne = j.vie - v0;
        // Au plafond, un banc repose : il ne soigne plus.
        j.vie = Math.floor(j.vieMax * %s); const v1 = j.vie; o.frame(%d * 2); const auPlafond = j.vie - v1;
        return { gagne: gagne, auPlafond: auPlafond };
    """ % (c["pv_images"], c["pv_plafond"], c["pv_images"]))
    assert not r.get("pasDeBanc")
    assert r["gagne"] == 1, "une PV toutes les %s images, pas plus" % c["pv_images"]
    assert r["auPlafond"] == 0, "passe %s %% de la barre, le banc ne soigne plus" % (c["pv_plafond"] * 100)


def test_on_ne_s_assoit_pas_avec_la_police_aux_fesses_ni_en_saignant(banc):
    c = interactions.ASSEOIR["refus"]
    r = jouer(banc, """
        const d = devant('banc');
        if (!d) return { pasDeBanc: true };
        L.B.recherche.etoiles = 2;
        const invitePolice = invite();
        o.tape('KeyE'); const policier = !!j.assis;
        L.B.recherche.etoiles = 0; j.saigne = 30;
        const inviteSang = invite();
        o.tape('KeyE'); const saigneur = !!j.assis;
        j.saigne = 0;
        return { invitePolice: invitePolice, policier: policier, inviteSang: inviteSang, saigneur: saigneur };
    """)
    assert not r.get("pasDeBanc")
    assert r["invitePolice"] == c["police"] and not r["policier"], "le refus se montre, et ACTION ne s'assoit pas"
    assert r["inviteSang"] == c["saigne"] and not r["saigneur"], "assis, on ne saignerait plus : refuse"


def test_un_coup_recu_ou_donne_nous_leve_et_ACTION_aussi_sans_faire_les_poches(banc):
    r = jouer(banc, """
        const d = devant('banc');
        if (!d) return { pasDeBanc: true };
        o.tape('KeyE'); const a1 = !!j.assis;
        L.Entites.blesser(j, 5, null); o.frame(2); const coup = !j.assis;
        // ACTION : on se leve, et la pression est depensee — pas de pickpocket a la place. Un
        // passant a la poche pleine nous tourne le dos, juste devant l'endroit ou l'on se releve.
        j.x = d.x; j.y = d.y + 14; j.invincible = 0; o.viser(d); L.Entites.indexer();
        o.tape('KeyE'); const b1 = !!j.assis;
        const passant = L.Entites.creerPieton(j.assis.avant.x, j.assis.avant.y - 14, L.Entites.archetype('touriste'));
        passant.etat = 'fige'; passant.argent = 50; passant.angle = -Math.PI / 2; L.Entites.indexer();
        const argent = p.argent;
        o.tape('KeyE'); const b2 = !j.assis;
        return { a1: a1, coup: coup, b1: b1, b2: b2, argent: p.argent - argent, poches: passant.argent };
    """)
    assert not r.get("pasDeBanc")
    assert r["a1"] and r["coup"], "un coup recu nous met debout"
    assert r["b1"] and r["b2"], "ACTION s'assoit, puis se leve"
    assert r["argent"] == 0 and r["poches"] == 50, "la pression qui nous leve ne fait pas les poches"


def test_assis_on_se_sauvegarde_la_ou_l_on_se_tenait_et_on_ne_s_assoit_pas_devant_une_porte(banc):
    r = jouer(banc, """
        const d = devant('banc');
        if (!d) return { pasDeBanc: true };
        const avant = { x: j.x, y: j.y };
        o.tape('KeyE');
        L.Missions.sauvegarderPartie();
        const sauve = { x: p.x, y: p.y };
        // Une porte devant nous : ACTION entre, elle ne s'assoit pas.
        j.assis = null;
        const porte = L.Monde.carte.portes.find(function (q) { return q.lieu; });
        j.x = porte.x * L.TT + 8; j.y = (porte.y + 1) * L.TT + 8; j.vx = 0; j.vy = 0; nettoyer(); o.viser({ x: porte.x * L.TT + 8, y: porte.y * L.TT + 8 });
        const laPorte = L.Monde.porteDevant(j);
        const decorAvecPorte = L.Interactions.decorSousLaMain(j);
        return { avant: avant, sauve: sauve, laPorte: !!laPorte, decorAvecPorte: !!decorAvecPorte };
    """)
    assert not r.get("pasDeBanc")
    assert (r["sauve"]["x"], r["sauve"]["y"]) == (round(r["avant"]["x"]), round(r["avant"]["y"])), \
        "assis, on se sauvegarde la ou l'on se tenait : le banc est un mur"
    assert r["laPorte"] and not r["decorAvecPorte"], "la porte passe avant le decor"


# --- Fouiller -------------------------------------------------------------------


def test_on_fouille_une_poubelle_une_fois_par_jour_et_le_quartier_compte(banc):
    c = interactions.FOUILLER
    r = jouer(banc, """
        const d = devant('poubelle');
        if (!d) return { pasDePoubelle: true };
        p.jour = 4; p.fouilles = {}; p.argent = 0; j.vie = 50;
        const standing = function (s) { L.Monde.standingA = function () { return s; }; };
        const inviteAvant = invite();
        // Un quartier ordinaire : 0,6 tombe sur la monnaie (50 de « rien », puis 26 de monnaie).
        standing('ordinaire');
        figer(0.6, function () { L.Missions.interagir(j); });
        const monnaie = p.argent;
        const inviteApres = invite();
        // Le meme tirage, une deuxieme fois (une AUTRE pression : une image plus tard) : rien, et on le dit.
        suivant();
        figer(0.6, function () { L.Missions.interagir(j); });
        const deuxieme = { argent: p.argent, msg: L.B.msg };
        // Le lendemain, le bac est de nouveau plein.
        p.jour = 5; const inviteLendemain = invite();
        // Un quartier cossu : le MEME tirage ne tombe plus sur la monnaie.
        p.fouilles = {}; p.argent = 0; standing('cossu'); suivant();
        figer(0.6, function () { L.Missions.interagir(j); });
        const cossu = { argent: p.argent, marque: Object.keys(p.fouilles).length };
        // Et un rat mord, sans jamais tuer.
        p.fouilles = {}; standing('ordinaire'); j.vie = 2; suivant();
        figer(0.999, function () { L.Missions.interagir(j); });
        return { inviteAvant: inviteAvant, monnaie: monnaie, inviteApres: inviteApres, deuxieme: deuxieme,
                 inviteLendemain: inviteLendemain, cossu: cossu, vieRat: j.vie, msgRat: L.B.msg };
    """)
    assert not r.get("pasDePoubelle"), "la ville n'a pas de poubelle devant laquelle se planter"
    lo, hi = c["trouvailles"]["monnaie"]["argent"]
    assert r["inviteAvant"] == c["invite"]
    assert lo <= r["monnaie"] <= hi, "la monnaie trouvee reste dans la fourchette du catalogue"
    assert r["inviteApres"] == c["deja"], "un bac fouille le dit — l'invite ne promet pas une trouvaille"
    assert r["deuxieme"]["argent"] == r["monnaie"] and r["deuxieme"]["msg"] == c["deja"], "une fois par jour et par bac"
    assert r["inviteLendemain"] == c["invite"], "le lendemain, on peut refouiller"
    assert r["cossu"]["marque"] == 1, "en quartier cossu aussi, le geste a eu lieu"
    assert r["cossu"]["argent"] == 0, "la poubelle d'un quartier cossu est presque vide : meme tirage, rien"
    assert r["vieRat"] == 1, "un rat mord, mais il reste toujours un point de vie"
    assert r["msgRat"].startswith(c["trouvailles"]["rat"]["texte"])


def test_fouiller_par_le_bouton_marque_le_bac_et_se_sauvegarde_avec_la_partie(banc):
    r = jouer(banc, """
        const d = devant('poubelle_pleine') || devant('poubelle');
        if (!d) return { pasDePoubelle: true };
        p.jour = 9; p.fouilles = {};
        o.tape('KeyE');
        const marque = Object.keys(p.fouilles).filter(function (k) { return k.indexOf('rue:') === 0; });
        return { marque: marque, jour: p.fouilles[marque[0]] };
    """)
    assert not r.get("pasDePoubelle")
    assert len(r["marque"]) == 1 and r["jour"] == 9, "le bac fouille est note (la partie garde `fouilles`)"


# --- Boire et la borne -------------------------------------------------------------


def test_on_boit_a_la_fontaine_puis_on_n_a_plus_soif(banc):
    c = interactions.BOIRE
    r = jouer(banc, """
        const d = devant('fontaine', 20);
        if (!d) return { pasDeFontaine: true };
        j.endurance = 10;
        const inviteAvant = invite();
        o.tape('KeyE');
        const bu = j.endurance;
        const inviteApres = invite();
        o.tape('KeyE'); const deuxieme = { souffle: j.endurance, msg: L.B.msg };
        o.frame(%d + 5);
        const inviteSoif = invite();
        return { inviteAvant: inviteAvant, bu: bu, inviteApres: inviteApres, deuxieme: deuxieme, inviteSoif: inviteSoif };
    """ % c["repit_images"])
    assert not r.get("pasDeFontaine"), "la ville n'a pas de fontaine devant laquelle se planter"
    assert r["inviteAvant"] == c["invite"]
    assert r["bu"] >= 10 + c["souffle"] - 1, "boire rend du souffle"
    assert r["inviteApres"] == c["encore"], "on n'a plus soif, et l'invite le dit"
    assert r["deuxieme"]["msg"] == c["encore"]
    assert r["inviteSoif"] == c["invite"], "dix secondes plus tard, on a de nouveau soif"


def test_on_mange_au_barbecue_une_fois_par_jour_et_ca_reste_sous_le_hot_dog(banc):
    c = interactions.BARBECUE
    r = jouer(banc, """
        const d = devant('bbq');
        if (!d) return { pasDeBbq: true };
        p.jour = 4; p.fouilles = {};
        j.vie = 10; j.endurance = 5;
        const inviteAvant = invite();
        o.tape('KeyE');
        const mange = { vie: j.vie, endurance: j.endurance, msg: L.B.msg };
        const inviteApres = invite();
        // Une autre pression, le meme jour : deja mange, et on le dit.
        suivant();
        o.tape('KeyE');
        const deuxieme = { vie: j.vie, msg: L.B.msg };
        // Le lendemain, le barbecue est de nouveau bon.
        p.jour = 5; const inviteLendemain = invite();
        return { inviteAvant: inviteAvant, mange: mange, inviteApres: inviteApres, deuxieme: deuxieme,
                 inviteLendemain: inviteLendemain };
    """)
    assert not r.get("pasDeBbq"), "la ville n'a pas de barbecue devant lequel se planter"
    assert r["inviteAvant"] == c["invite"]
    assert r["mange"]["vie"] == 10 + c["pv"], "manger rend des PV"
    # ⚠️ >= et pas == : `o.tape` avance au moins une image, et la reprise passive du
    # souffle (`Entites.majJoueur`) en ajoute un peu par-dessus, comme pour `boire`.
    assert r["mange"]["endurance"] >= 5 + c["souffle"] - 1, "manger rend aussi du souffle"
    assert r["mange"]["msg"] == c["message"]
    assert r["inviteApres"] == c["deja"], "un barbecue vide le dit — l'invite ne promet pas un second repas"
    assert r["deuxieme"]["vie"] == r["mange"]["vie"] and r["deuxieme"]["msg"] == c["deja"], \
        "une fois par jour et par barbecue"
    assert r["inviteLendemain"] == c["invite"], "le lendemain, on peut remanger"


def test_un_barbecue_ne_soigne_pas_au_dela_de_la_barre(banc):
    """`Missions.soigner` plafonne déjà à `vieMax` : le barbecue n'a pas sa propre borne,
    et c'est exactement pour ça qu'il ne doit jamais en avoir besoin."""
    r = jouer(banc, """
        const d = devant('bbq');
        if (!d) return { pasDeBbq: true };
        p.jour = 4; p.fouilles = {};
        j.vie = j.vieMax;
        o.tape('KeyE');
        return { vie: j.vie, vieMax: j.vieMax };
    """)
    assert not r.get("pasDeBbq"), "la ville n'a pas de barbecue devant lequel se planter"
    assert r["vie"] == r["vieMax"], "manger a pleine vie ne fait pas déborder la barre"


def test_la_borne_s_ouvre_a_la_main_on_s_y_rafraichit_et_on_la_ferme(banc):
    c = interactions.BORNE
    r = jouer(banc, """
        const d = devant('borne_fontaine');
        if (!d) return { pasDeBorne: true };
        const inviteFermee = invite();
        o.tape('KeyE');
        const jet = L.Interactions.jetDe(d);
        const inviteOuverte = invite();
        // Dans la gerbe, le souffle revient plus vite ; hors d'elle, non.
        j.endurance = 10; const a0 = j.endurance; o.frame(40); const dedans = j.endurance - a0;
        L.Interactions.jetDe(d).x += 0;                                // (la gerbe ne bouge pas)
        j.x += 80; j.y += 0; L.Entites.indexer(); j.endurance = 10; const b0 = j.endurance; o.frame(40); const dehors = j.endurance - b0;
        j.x -= 80; L.Entites.indexer(); o.viser(d);
        o.tape('KeyE');
        const fermee = !L.Interactions.jetDe(d);
        return { inviteFermee: inviteFermee, ouverte: !!jet, inviteOuverte: inviteOuverte, dedans: dedans, dehors: dehors, fermee: fermee };
    """)
    assert not r.get("pasDeBorne"), "la ville n'a pas de borne-fontaine devant laquelle se planter"
    assert r["inviteFermee"] == c["invite_ouvrir"] and r["ouverte"], "ACTION ouvre la borne : la meme gerbe que celle d'une borne defoncee"
    assert r["inviteOuverte"] == c["invite_fermer"]
    assert r["dedans"] > r["dehors"], "on se rafraichit dans la gerbe"
    assert r["fermee"], "ACTION referme la borne"


# --- Le chat -------------------------------------------------------------------------


def test_on_caresse_le_chat_confiant_et_ca_ne_rapporte_rien(banc):
    """⚠️ La confiance (`Entites.majBete`, `pietons.BETES["chat"]["confiance_px"]`) est
    jugée à part, au banc des bêtes (`test_betes_js.py`) — ici, seulement le bouton :
    ACTION près d'un chat confiant caresse, ne fait rien perdre ni gagner, et le chat
    ne fuit pas pour autant (`utiliserSurLesBetes`, avant le décor, après le bouclier)."""
    r = jouer(banc, CHAT + """
        const chat = unChat();
        if (!chat) return { pasDeChat: true };
        // Dans la fenêtre jouable : au-delà de `confiance_px` (il ne fuit pas), en
        // deçà de `portee_px` du geste (assez près pour la main).
        const c = L.B.defs.pietons.betes.chat, ca = L.B.defs.interactions.caresser;
        j.x = chat.x + (c.confiance_px + ca.portee_px) / 2; j.y = chat.y;
        j.arme = 'poings'; L.Monde.centrerCamera(j.x, j.y); nettoyer(); o.frame(2);
        const inviteAvant = invite();
        const avant = { vie: j.vie, argent: p.argent, endurance: j.endurance };
        o.tape('KeyE');
        const apres = { vie: j.vie, argent: p.argent, endurance: j.endurance, msg: L.B.msg, fuite: chat.fuite > 0 };
        return { pasDeChat: false, inviteAvant: inviteAvant, avant: avant, apres: apres };
    """)
    assert not r["pasDeChat"], "la ville n'a pas de chat auquel s'approcher"
    assert r["inviteAvant"] == interactions.CARESSER["invite"]
    assert r["apres"]["msg"] in interactions.CARESSER["mots"], "caresser dit un des mots du catalogue"
    assert r["apres"]["vie"] == r["avant"]["vie"], "caresser ne rend ni ne coûte de PV"
    assert r["apres"]["argent"] == r["avant"]["argent"], "caresser ne rapporte pas un sou"
    assert r["apres"]["endurance"] == r["avant"]["endurance"], "caresser ne rend pas de souffle"
    assert not r["apres"]["fuite"], "le chat qu'on vient de caresser ne détale pas"


def test_loin_du_chat_ACTION_ne_caresse_rien(banc):
    r = jouer(banc, CHAT + """
        const chat = unChat();
        if (!chat) return { pasDeChat: true };
        j.x = chat.x + 200; j.y = chat.y; j.arme = 'poings';
        L.Monde.centrerCamera(j.x, j.y); nettoyer(); o.frame(2);
        return { pasDeChat: false, invite: invite() };
    """)
    assert not r["pasDeChat"], "la ville n'a pas de chat auquel s'approcher"
    assert r["invite"] != interactions.CARESSER["invite"], "un chat à 200 px n'est pas sous la main"


# --- Les gens ------------------------------------------------------------------------


def test_un_dollar_dans_le_chapeau_de_l_artiste_change_vraiment_de_poche(banc):
    c = interactions.POURBOIRE
    r = jouer(banc, """
        p.argent = 20;
        const a = o.poser('musicien', 0, 16);
        a.argent = 5; a.angle = -Math.PI / 2;                          // il nous regarde : ACTION est un pourboire
        o.viser(a);
        const inviteAvant = invite();
        o.tape('KeyE');
        return { inviteAvant: inviteAvant, argent: p.argent, sien: a.argent, bulle: a.bulle && a.bulle.texte, chapeau: a.chapeauT };
    """)
    assert r["inviteAvant"] == "%s — %d $" % (c["invite"], c["montant"])
    assert r["argent"] == 20 - c["montant"] and r["sien"] == 5 + c["montant"], "la piece change de poche"
    assert r["bulle"] in c["merci"]["musicien"], "l'artiste remercie"
    assert r["chapeau"] > 0, "et le chapeau s'anime, comme pour un badaud"


def test_derriere_l_artiste_ACTION_reste_le_pickpocket_et_sans_un_dollar_aussi(banc):
    r = jouer(banc, """
        p.argent = 20;
        const a = o.poser('musicien', 0, 16);
        a.argent = 30; a.angle = Math.PI / 2;                          // dos a nous, ses poches sont a prendre
        o.viser(a);
        const inviteDos = invite();
        L.Missions.interagir(j);
        const dos = { argent: p.argent, sien: a.argent };
        // Face a lui mais sans un dollar : rien a laisser, ACTION retombe sur ce qui suit.
        a.angle = -Math.PI / 2; p.argent = 0; o.viser(a);
        const inviteFauche = invite();
        return { inviteDos: inviteDos, dos: dos, inviteFauche: inviteFauche };
    """)
    assert not (r["inviteDos"] or "").startswith(interactions.POURBOIRE["invite"]), "dans son dos, l'invite n'est pas un pourboire"
    assert r["dos"]["argent"] == 20, "dans son dos, on ne lui donne rien"
    assert not (r["inviteFauche"] or "").startswith(interactions.POURBOIRE["invite"]), "sans un dollar, pas de pourboire"


def test_le_touriste_se_fait_photographier_une_fois_et_paie_de_sa_poche(banc):
    c = interactions.PHOTO
    r = jouer(banc, """
        p.argent = 0;
        const t = o.poser('touriste', 0, 16);
        t.argent = 40; t.angle = -Math.PI / 2; o.viser(t);
        const inviteAvant = invite();
        figer(0.5, function () { L.Missions.interagir(j); });
        const un = { argent: p.argent, sien: t.argent, bulle: t.bulle && t.bulle.texte, etat: t.etat, photo: t.photoPrise };
        const inviteApres = invite();
        // Un touriste fauche dit merci quand meme (on laisse la place au premier, puis une autre pression).
        suivant();
        const f = L.Entites.creerPieton(j.x, j.y + 16, L.Entites.archetype('touriste'));
        f.etat = 'fige'; f.argent = 0; f.angle = -Math.PI / 2; L.Entites.indexer(); o.viser(f);
        p.argent = 0; figer(0.5, function () { L.Missions.interagir(j); });
        return { inviteAvant: inviteAvant, un: un, inviteApres: inviteApres, fauche: { argent: p.argent, photo: f.photoPrise } };
    """)
    assert r["inviteAvant"] == c["invite"]
    assert c["pourboire"][0] <= r["un"]["argent"] <= c["pourboire"][1], "un pourboire dans la fourchette du catalogue"
    assert r["un"]["sien"] == 40 - r["un"]["argent"], "il paie de SA poche"
    assert r["un"]["bulle"] in c["merci"] and r["un"]["photo"] and r["un"]["etat"] == "arret"
    assert r["inviteApres"] != c["invite"], "une fois par touriste"
    assert r["fauche"]["argent"] == 0 and r["fauche"]["photo"], "fauche, il dit merci quand meme"


def test_une_personne_devant_un_banc_garde_ACTION_et_le_dos_tourne_ne_fait_rien(banc):
    r = jouer(banc, """
        const d = devant('banc');
        if (!d) return { pasDeBanc: true };
        // A mains nues : un passant a la poche pleine, dos tourne, entre nous et le banc. ACTION
        // fait ses poches (`Combat.maj`) — le banc ne lui vole pas le geste.
        const q = L.Entites.creerPieton(d.x, d.y + 2, L.Entites.archetype('touriste'));
        q.etat = 'fige'; q.argent = 20; q.angle = -Math.PI / 2; L.Entites.indexer(); o.viser(q);
        const pocheAPrendre = !!L.Combat.victimeDesPoches(j);
        const cede = !!L.Interactions.decorSousLaMain(j);
        const argent = p.argent;
        o.tape('KeyE');
        const poches = p.argent - argent, assis = !!j.assis;
        // Il s'en va : le banc est de nouveau a nous.
        L.Entites.retirer(q); L.Entites.indexer(); o.viser(d);
        const libre = !!L.Interactions.decorSousLaMain(j);
        // Le dos tourne au banc : rien du tout.
        j.face = 'bas';
        const dos = L.Interactions.decorSousLaMain(j);
        return { pocheAPrendre: pocheAPrendre, cede: cede, poches: poches, assis: assis, libre: libre, dos: !!dos };
    """)
    assert not r.get("pasDeBanc")
    assert r["pocheAPrendre"] and not r["cede"], "quelqu'un dont les poches sont a prendre passe avant le banc"
    assert r["poches"] == 20 and not r["assis"], "ACTION fait les poches, elle ne s'assoit pas"
    assert r["libre"], "une fois le passant parti, le banc est de nouveau sous la main"
    assert not r["dos"], "le dos tourne, ACTION ne fait rien : on agit sur ce qu'on regarde"


def test_un_char_sous_la_main_ne_double_pas_le_pourboire_et_ne_prend_pas_la_pression(banc):
    """⚠️ `Vehicules.maj` rappelle `interagir` dans la MEME image quand un char est sous la main : un
    pourboire donné deux fois, ou une pression qui monte dans le char après avoir payé l'artiste, est
    un bogue qu'aucun appel direct à la fonction ne voit — il faut le bouton."""
    r = jouer(banc, """
        p.argent = 20;
        const a = o.poser('musicien', 0, 16);
        a.argent = 5; a.angle = -Math.PI / 2;
        const v = o.char('auto', 16, 14, 0);
        o.viser(a);
        const charSousLaMain = !!L.Vehicules.vehiculeSousLaMain(j);
        o.tape('KeyE');
        return { charSousLaMain: charSousLaMain, argent: p.argent, sien: a.argent, dansLeChar: !!j.dansVehicule };
    """)
    assert r["charSousLaMain"], "le scenario doit avoir un char sous la main, sinon il ne juge rien"
    assert r["argent"] == 20 - interactions.POURBOIRE["montant"], "un seul pourboire, pas deux"
    assert not r["dansLeChar"], "la pression est depensee par le pourboire : on ne monte pas dans le char"


def test_un_coup_donne_ou_un_sprint_nous_leve_aussi(banc):
    r = jouer(banc, """
        const d = devant('banc');
        if (!d) return { pasDeBanc: true };
        const res = {};
        for (const [nom, touche] of [['attaque', 'KeyJ'], ['sprint', 'ShiftLeft'], ['arme', 'Tab']]) {
            // (Un sprint tape est une ROULADE : `roule` bloque ACTION, on la laisse finir.)
            j.x = d.x; j.y = d.y + 14; j.assis = null; j.roule = 0; o.viser(d); suivant();
            o.tape('KeyE'); const assis = !!j.assis;
            // La touche se TIENT jusqu'a ce qu'on soit debout (l'accumulateur d'images peut sauter un pas).
            o.touche(touche); for (let k = 0; k < 6 && j.assis; k++) o.frame(1); o.relacher(touche); o.frame(2);
            res[nom] = { assis: assis, leve: !j.assis };
        }
        return res;
    """)
    assert not r.get("pasDeBanc")
    for nom, etat in r.items():
        assert etat["assis"] and etat["leve"], "%s : assis, puis debout" % nom


def test_un_char_sous_la_main_passe_avant_le_banc(banc):
    r = jouer(banc, """
        const d = devant('banc');
        if (!d) return { pasDeBanc: true };
        const libre = !!L.Interactions.decorSousLaMain(j);
        o.char('auto', 0, -10, 0);                       // entre nous et le banc : dans le meme cone
        o.viser(d);
        const sous = !!L.Vehicules.vehiculeSousLaMain(j), decor = !!L.Interactions.decorSousLaMain(j);
        L.Missions.majInvite(j); const inv = L.B.invite;
        o.tape('KeyE');
        return { libre: libre, sous: sous, decor: decor, invite: inv, assis: !!j.assis, dansLeChar: !!j.dansVehicule };
    """)
    assert not r.get("pasDeBanc")
    assert r["libre"], "sans char, le banc est sous la main"
    assert r["sous"] and not r["decor"], "un char sous la main : le banc s'efface (la porte gagne sur la portiere, le banc aussi)"
    assert r["invite"] != interactions.ASSEOIR["invite"]
    assert r["dansLeChar"] and not r["assis"], "ACTION monte dans le char"


def test_une_arme_par_terre_passe_avant_le_banc(banc):
    r = jouer(banc, """
        const d = devant('banc');
        if (!d) return { pasDeBanc: true };
        const arme = L.Entites.creer('ramassage', j.x, j.y - 12, { r: 4, objet: 'arme', arme: 'pistolet', munitions: 6, t: 0, solide: false });
        L.Entites.indexer(); o.viser(arme);
        const sous = !!L.Combat.objetSousLaMain(j), decor = !!L.Interactions.decorSousLaMain(j);
        o.tape('KeyE');
        return { sous: sous, decor: decor, assis: !!j.assis, ramassee: L.B.entites.indexOf(arme) < 0 };
    """)
    assert not r.get("pasDeBanc")
    assert r["sous"] and not r["decor"], "une arme sous la main : le banc s'efface"
    assert r["ramassee"] and not r["assis"], "ACTION ramasse l'arme"


def test_une_porte_passe_avant_le_banc_qui_la_jouxte(banc):
    """Le test d'avant ne posait la porte NULLE PART près d'un banc : il jugeait le vide. Ici on
    plante un banc à deux pas de la porte, dans le même cône."""
    r = jouer(banc, """
        const porte = L.Monde.carte.portes.find(function (q) { return q.lieu; });
        j.x = porte.x * L.TT + 8; j.y = (porte.y + 1) * L.TT + 8; j.vx = 0; j.vy = 0; nettoyer();
        o.viser({ x: porte.x * L.TT + 8, y: porte.y * L.TT + 8 });
        const laPorte = !!L.Monde.porteDevant(j);
        L.Entites.creer('decor', j.x - 6, j.y - 12, { decor: 'banc', r: 5, solide: true, dessine: true });
        L.Entites.reindexerDecor(); nettoyer();
        const decor = !!L.Interactions.decorSousLaMain(j);
        o.tape('KeyE'); o.fondu();
        return { laPorte: laPorte, decor: decor, assis: !!j.assis, dedans: !!L.B.interieur };
    """)
    assert r["laPorte"], "le scenario doit avoir une porte devant nous"
    assert not r["decor"], "une porte devant nous : le banc s'efface"
    assert r["dedans"] and not r["assis"], "ACTION passe la porte, elle ne s'assoit pas"


def test_la_pression_qui_nous_leve_n_ouvre_pas_le_distributeur_d_a_cote(banc):
    """`majAssis` depense la pression (`Entree.videPresse`) : sans elle, `Combat.maj` la rejouait dans la
    meme image — et tout ce que la chaine d'ACTION sert AVANT le decor (une machine, un donneur, un etal)
    s'ouvrait sous le nez de qui voulait seulement se lever."""
    r = jouer(banc, """
        const d = devant('banc');
        if (!d) return { pasDeBanc: true };
        o.tape('KeyE'); const assis = !!j.assis;
        const av = j.assis.avant;
        L.Entites.creer('decor', av.x, av.y - 14, { decor: 'distributrice_cafe', r: 5, solide: true, dessine: true });
        L.Entites.reindexerDecor(); L.Entites.indexer();
        const machine = (function () { const s = j.x; j.x = av.x; const m = L.Missions.distributriceSousLaMain(Object.assign({}, j, { x: av.x, y: av.y, face: 'haut' })); j.x = s; return !!m; })();
        o.tape('KeyE');
        return { assis: assis, machine: machine, leve: !j.assis, menu: !!L.B.menu };
    """)
    assert not r.get("pasDeBanc")
    assert r["assis"] and r["machine"], "le scenario doit avoir une machine devant l'endroit ou l'on se releve"
    assert r["leve"] and not r["menu"], "la pression qui nous leve est depensee : aucun menu ne s'ouvre"
