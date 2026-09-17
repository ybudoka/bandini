"""Le client du taxi attend au bord de la route, et une flèche y mène (17 sept. 2026).

Demande de Martin : « pour la mission du taxi et tout ce qui est taxi, il faut que
les clients attendent sur le bord de la route. et je veux les flèches pour savoir
où trouver le client. »

⚠️ Juges : au klaxon (le bouton, pas la fonction), le client naît sur un trottoir
collé à une voie que CE char rejoint — la route est recalculée ici, pas relue dans
`missions.js` ; il naît hors de l'écran ; il attend là où il est né, même quand on
prend le mauvais coin de rue ; et une flèche le montre au bord de l'écran et au bord
de la mini-carte, puis montre la course une fois le client à bord.
"""

#: Seize départs répartis sur toute la ville, sur une voie où le char roule droit,
#: et la route du char recalculée ici : un parcours en largeur sur les tuiles où
#: un char roule (ni mur, ni eau).
DEPARTS = """
    function departs(L, n) {
        const M = L.Monde, c = M.carte, voies = [];
        for (let ty = 4; ty < c.h - 4; ty++) for (let tx = 4; tx < c.w - 4; tx++) {
            const f = M.fleche(tx, ty);
            if ((f === '>' || f === '<' || f === '^' || f === 'v') && M.estChaussee(tx, ty)) voies.push([tx, ty]);
        }
        const pas = Math.floor(voies.length / n), choisis = [];
        for (let k = 0; k < n; k++) choisis.push(voies[k * pas + Math.floor(pas / 2)]);
        return choisis;
    }
    function routeDuChar(L, tx0, ty0) {
        const M = L.Monde, W = M.carte.w, H = M.carte.h, vus = new Uint8Array(W * H), file = [ty0 * W + tx0];
        vus[ty0 * W + tx0] = 1;
        for (let i = 0; i < file.length; i++) {
            const k = file[i], x = k % W, y = (k - x) / W;
            [[1, 0], [-1, 0], [0, 1], [0, -1]].forEach(function (d) {
                const nx = x + d[0], ny = y + d[1], nk = ny * W + nx;
                if (nx < 0 || ny < 0 || nx >= W || ny >= H || vus[nk]) return;
                if (M.bloque(nx, ny, M.MASQUE_VEHICULE) || M.estEau(nx, ny)) return;
                vus[nk] = 1; file.push(nk);
            });
        }
        return function (tx, ty) { return tx >= 0 && ty >= 0 && tx < W && ty < H && vus[ty * W + tx] === 1; };
    }
    function auVolant(L, o, slug, tx, ty) {
        const j = L.B.joueur;
        j.intouchable = true;
        j.x = tx * L.TT + 8; j.y = ty * L.TT + 8;
        L.Monde.centrerCamera(j.x, j.y);
        const v = o.char(slug, 0, 0, 0);
        L.Vehicules.monter(j, v);
        v.vitesse = 0;
        o.frame(2);
        return v;
    }
"""


def test_le_client_attend_sur_le_trottoir_d_une_rue_que_le_char_rejoint(banc):
    """⚠️ Rouge avant : le client naissait par `placeDeNaissance`, n'importe où hors
    route dans la bulle — un parc, une arrière-cour. Le juge klaxonne depuis seize
    coins de la ville, en taxi et en ambulance (le blessé se ramasse de la même
    façon), et regarde où chacun attend."""
    r = banc("function (L, o) {" + DEPARTS + """
        L.Jeu.commencer();
        const M = L.Monde, TT = L.TT, b = L.Missions.boulot, releves = [];
        departs(L, 16).forEach(function (d, i) {
            const slug = i % 4 === 3 ? 'ambulance' : 'taxi';
            L.graine(100 + i);
            const v = auVolant(L, o, slug, d[0], d[1]);
            const route = routeDuChar(L, d[0], d[1]);
            v.sirene = false;
            o.tape('Space', 2);                              // le klaxon (la sirene) prend l'appel
            const c = b.client;
            if (!c) { releves.push({ slug: slug, depart: d, client: false, msg: L.B.msg }); L.Vehicules.descendre(L.B.joueur, true); return; }
            const tx = Math.floor(c.x / TT), ty = Math.floor(c.y / TT);
            const rues = [[1, 0], [-1, 0], [0, 1], [0, -1]].filter(function (q) {
                const nx = tx + q[0], ny = ty + q[1];
                return M.estChaussee(nx, ny) && route(nx, ny);
            });
            releves.push({
                slug: slug, depart: d, client: true, tuile: [tx, ty], glyphe: M.glyphe(tx, ty),
                trottoir: M.estTrottoir(tx, ty) && M.marchablePieton(tx, ty),
                rue: rues.length > 0,
                distance: Math.round(Math.hypot(c.x - v.x, c.y - v.y)),
            });
            b.abandonner();
            L.Entites.retirer(c);
            L.Vehicules.descendre(L.B.joueur, true);
            L.Entites.retirer(v);
        });
        return releves;
    }""")
    sans = [x for x in r if not x["client"]]
    assert not sans, f"le klaxon n'a trouvé personne : {sans}"
    hors_trottoir = [x for x in r if not x["trottoir"]]
    assert not hors_trottoir, f"des clients n'attendent pas sur un trottoir : {hors_trottoir}"
    sans_rue = [x for x in r if not x["rue"]]
    assert not sans_rue, f"des clients attendent loin d'une rue que le char rejoint : {sans_rue}"
    assert {x["slug"] for x in r} == {"taxi", "ambulance"}


def test_le_client_nait_hors_de_l_ecran_et_regarde_la_rue(banc):
    r = banc("function (L, o) {" + DEPARTS + """
        L.Jeu.commencer();
        const b = L.Missions.boulot, TT = L.TT, releves = [];
        departs(L, 8).forEach(function (d, i) {
            L.graine(200 + i);
            const v = auVolant(L, o, 'taxi', d[0], d[1]);
            // On le regarde des qu'il est pose, avant que la camera ne bouge. ⚠️ Deux
            // images : un appui tenu une seule image tombe parfois entre deux pas.
            o.touche('Space'); o.frame(2);
            const c = b.client;
            if (c) {
                const tx = Math.floor(c.x / TT), ty = Math.floor(c.y / TT);
                const vers = [[1, 0, 'droite'], [-1, 0, 'gauche'], [0, 1, 'bas'], [0, -1, 'haut']].filter(function (q) {
                    return L.Monde.estChaussee(tx + q[0], ty + q[1]);
                }).map(function (q) { return q[2]; });
                releves.push({ vu: L.Entites.visibleAEcran(c.x, c.y, 0), face: c.face, vers: vers, bulle: c.bulle ? c.bulle.texte : null });
            }
            o.relacher('Space'); o.frame(1);
            b.abandonner();
            if (c) L.Entites.retirer(c);
            L.Vehicules.descendre(L.B.joueur, true);
            L.Entites.retirer(v);
        });
        return releves;
    }""")
    assert len(r) == 8, r
    assert not [x for x in r if x["vu"]], f"un client est né sous les yeux : {r}"
    assert not [x for x in r if x["face"] not in x["vers"]], f"un client tourne le dos à la rue : {r}"
    assert all(x["bulle"] for x in r), "un client qui attend un taxi hèle"


def test_le_client_attend_meme_quand_on_prend_le_mauvais_coin_de_rue(banc):
    """⚠️ Rouge avant : un passant au-delà de la bulle s'oublie, et le client en était
    un comme les autres — on faisait le tour du bloc par le mauvais côté, et la course
    tombait « IL N'EST PLUS LA »."""
    r = banc("function (L, o) {" + DEPARTS + """
        L.Jeu.commencer();
        const b = L.Missions.boulot, d = departs(L, 16)[5];
        L.graine(311);
        const v = auVolant(L, o, 'taxi', d[0], d[1]);
        o.tape('Space', 2);
        const c = b.client;
        if (!c) return { client: false };
        const ne = { x: c.x, y: c.y };
        const j = L.B.joueur;
        // Le taxi part a l'oppose, a plus de deux bulles du client, et y reste.
        const loin = { x: v.x + Math.sign(v.x - c.x || 1) * 1100, y: v.y };
        for (let i = 0; i < 240; i++) {
            v.x = loin.x; v.y = loin.y; v.vitesse = 0; j.x = v.x; j.y = v.y;
            L.Monde.centrerCamera(j.x, j.y);
            o.frame(1);
        }
        const encore = L.B.entites.indexOf(c) >= 0;
        return { client: true, encore: encore, etape: b.etape, pareil: b.client === c,
                 bouge: Math.round(Math.hypot(c.x - ne.x, c.y - ne.y)), loin: Math.round(Math.hypot(c.x - j.x, c.y - j.y)) };
    }""")
    assert r["client"], "le klaxon n'a trouvé personne"
    assert r["loin"] > 1000, r
    assert r["encore"] and r["pareil"] and r["etape"] == "ramasse", f"le client s'est oublié pendant qu'on le cherchait : {r}"
    assert r["bouge"] <= 2, f"le client n'attend pas où il est né : {r}"


def test_une_fleche_mene_au_client_puis_a_la_course(banc):
    """⚠️ Rouge avant : le client n'avait qu'un point bleu sur la mini-carte, et
    seulement dans son cadre — pas de flèche au bord de l'écran, ni au bord de la
    mini-carte, alors qu'un objectif de mission avait les deux."""
    r = banc("function (L, o) {" + DEPARTS + """
        L.Jeu.commencer();
        const b = L.Missions.boulot, d = departs(L, 16)[9], j = L.B.joueur;
        L.graine(421);
        const v = auVolant(L, o, 'taxi', d[0], d[1]);
        // Un objectif d'histoire en meme temps, a l'oppose : la fleche de l'ecran
        // doit etre celle du boulot.
        L.Histoire.cible = function () { return { x: j.x - 2000, y: j.y, nom: 'AILLEURS', couleur: '#8ad26a' }; };
        o.tape('Space', 2);
        const c = b.client;
        if (!c) return { client: false };
        function lire(cible) {
            const m = L.Hud.marqueurs(), e = m.ecran;
            const vers = Math.atan2(cible.y - j.y, cible.x - j.x);
            return { ecran: e && { quoi: e.quoi, couleur: e.couleur, ecart: e ? Math.abs(Math.atan2(Math.sin(e.angle - vers), Math.cos(e.angle - vers))) : null },
                     boulot: m.boulot && { forme: m.boulot.forme, couleur: m.boulot.couleur } };
        }
        o.frame(2);
        const client = lire(c);
        // Le client tout au bout de la ville : hors du cadre de la mini-carte.
        const ne = { x: c.x, y: c.y };
        c.x = j.x + 60 * L.TT; c.y = j.y; c.plante = { x: c.x, y: c.y };
        o.frame(2);
        const clientLoin = lire(c);
        c.x = ne.x; c.y = ne.y; c.plante = { x: c.x, y: c.y };
        // La carte ouverte : le client y est marque aussi.
        o.tape('KeyN');
        const carte = L.B.etat === 'carte';
        const surLaCarte = [];
        for (let i = 0; i < 40; i++) { o.frame(1); const m = L.Hud.marqueurs().boulot; surLaCarte.push(m && m.visible ? m.forme + ':' + m.y : null); }
        o.tape('KeyN');
        // On le ramasse : la fleche passe a la course.
        v.x = c.x + 10; v.y = c.y; j.x = v.x; j.y = v.y; v.vitesse = 0;
        o.frame(3);
        const dest = b.destination;
        L.Monde.centrerCamera(j.x, j.y);
        o.frame(2);
        const course = dest ? lire(dest) : null;
        return { client: true, etape: b.etape, avant: client, loin: clientLoin, carte: carte, surLaCarte: surLaCarte, course: course };
    }""")
    assert r["client"], "le klaxon n'a trouvé personne"
    a = r["avant"]
    assert a["ecran"], "aucune flèche au bord de l'écran vers le client"
    assert a["ecran"]["quoi"] == "boulot", f"la flèche de l'écran montre l'histoire, pas le client : {a}"
    assert a["ecran"]["couleur"] == "#6f9fd8" and a["ecran"]["ecart"] < 0.15, f"la flèche ne pointe pas le client : {a}"
    assert r["loin"]["boulot"] == {"forme": "fleche", "couleur": "#6f9fd8"}, (
        f"hors du cadre de la mini-carte, le client doit devenir une flèche : {r['loin']}")
    assert r["carte"] and None not in r["surLaCarte"], (
        f"le client n'est pas marqué à chaque image sur la carte ouverte : {r['surLaCarte']}")
    assert {m.split(":")[0] for m in r["surLaCarte"]} == {"pointeur"}, r["surLaCarte"]
    assert len(set(r["surLaCarte"])) == 2, f"le pointeur de la carte n'oscille pas : {r['surLaCarte']}"
    assert r["etape"] == "route", "le client n'est pas monté"
    c = r["course"]
    assert c and c["ecran"] and c["ecran"]["quoi"] == "boulot" and c["ecran"]["couleur"] == "#e8b33c", (
        f"une fois le client à bord, la flèche doit montrer la course : {c}")
    assert c["ecran"]["ecart"] < 0.15, f"la flèche ne pointe pas la course : {c}"


def test_sur_l_ile_personne_n_attend_un_taxi_qui_ne_peut_pas_venir(banc):
    """⚠️ Toutes les voies de la ville se tiennent, sauf pour un char qui n'y est
    pas : un taxi débarqué sur l'île ne rejoint aucun trottoir du continent, à une
    cinquantaine de tuiles de l'autre côté de l'eau (sans la règle, le client y
    naissait à 766 px). Le klaxon le DIT, plutôt que de
    poser un client qu'on ne peut pas aller chercher. Le témoin : le même klaxon
    devant le terminus, en ville."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const j = L.B.joueur, TT = L.TT, def = L.Monde.carte.def, b = L.Missions.boulot, out = {};
        j.intouchable = true;
        for (const ou of ['ville', 'ile']) {
            const porte = def.portes.find(function (p) { return p.lieu === (ou === 'ile' ? 'chapelle' : 'terminus'); });
            j.x = porte.x * TT + 8; j.y = (porte.y + 2) * TT + 8;
            L.Monde.centrerCamera(j.x, j.y);
            L.graine(512);
            const v = o.char('taxi', 0, 0, 0);
            L.Vehicules.monter(j, v);
            v.vitesse = 0;
            o.frame(2);
            o.tape('Space', 2);
            const c = b.client;
            out[ou] = { client: !!c, etape: b.etape, msg: L.B.msg,
                        eau: c ? Math.round(Math.hypot(c.x - v.x, c.y - v.y)) : null };
            b.abandonner();
            if (c) L.Entites.retirer(c);
            L.Vehicules.descendre(j, true);
            L.Entites.retirer(v);
        }
        return out;
    }""")
    assert r["ville"]["client"] is True, f"le témoin en ville n'a trouvé personne : {r}"
    assert r["ile"]["client"] is False and r["ile"]["etape"] is None, (
        f"sur l'île, un client attend un taxi qui ne peut pas le rejoindre : {r}")
    assert r["ile"]["msg"] == "PERSONNE N’ATTEND DANS LE COIN", r
