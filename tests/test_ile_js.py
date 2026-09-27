"""L'île, côté jeu : la police n'y va pas.

⚠️ C'est la seule idée mécanique de la fiche, et elle vaut toutes les autres :
sur l'île, aucun agent ne naît, l'hélico s'en va, les étoiles descendent et rien
ne les fait monter — ni un crime, ni un témoin qui appelle, ni un plancher
d'étoiles. `refuge` est une propriété de la ZONE (`ile.zone()`), lue par
`Police.auRefuge`.

⚠️ Chaque juge porte son TÉMOIN en ville : la même scène, à la même heure, sur
le continent, où la police vient. Sans lui, « aucun agent » pourrait vouloir
dire « le banc n'en fait naître nulle part ».
"""

#: Pose le joueur sur l'île, devant la chapelle — ou en ville, devant le terminus.
POSER = """
    function poser(L, ou) {
        const j = L.B.joueur, TT = L.TT, def = L.Monde.carte.def;
        const lieu = ou === 'ile' ? 'chapelle' : 'terminus';
        const porte = def.portes.find(function (p) { return p.lieu === lieu; });
        j.x = porte.x * TT + 8; j.y = (porte.y + 2) * TT + 8;
        L.Monde.centrerCamera(j.x, j.y);
        L.B.entites.filter(function (e) { return e.agent; }).forEach(function (e) { L.Entites.retirer(e); });
        L.Entites.indexer();
        return porte;
    }
"""


def test_sur_l_ile_la_police_ne_vient_pas_et_les_etoiles_tombent(banc, paquet):
    """À trois étoiles, en ville, les agents arrivent ; sur l'île, personne — et
    au bout du délai du palier, une étoile tombe."""
    palier3 = paquet["recherche"]["paliers"][3]["decroissance_s"]
    r = banc("""function (L, o) {""" + POSER + """
        L.Jeu.commencer();
        const r = L.B.recherche, j = L.B.joueur;
        j.intouchable = true;
        const out = {};
        for (const ou of ['ville', 'ile']) {
            poser(L, ou);
            r.etoiles = 3; r.chaleur = 0; r.vu = 0; r.dernierVu = { x: j.x, y: j.y, t: L.B.t };
            let agents = 0;
            for (let i = 0; i < %d; i++) {
                o.frame(1);
                agents = Math.max(agents, L.Police.agents().length);
            }
            out[ou] = { agents: agents, etoiles: r.etoiles, refuge: L.Police.auRefuge() };
        }
        return out;
    }""" % (palier3 * 60 + 90))
    assert r["ville"]["refuge"] is False and r["ile"]["refuge"] is True
    assert r["ville"]["agents"] > 0, "le temoin ne mord pas : meme en ville, aucun agent n'est venu"
    assert r["ile"]["agents"] == 0, f"{r['ile']['agents']} agents sont venus sur l'ile"
    assert r["ile"]["etoiles"] == 2, f"sur l'ile, les etoiles ne tombent pas : {r['ile']['etoiles']}"


def test_sur_l_ile_rien_ne_fait_monter_les_etoiles(banc):
    """Un crime vu, un témoin qui appelle, un plancher d'étoiles : en ville, ça
    monte ; sur l'île, non — ni dehors, ni dans la chapelle."""
    r = banc("""function (L, o) {""" + POSER + """
        L.Jeu.commencer();
        const r = L.B.recherche, out = {};
        function essayer() {
            r.etoiles = 0; r.chaleur = 0;
            L.Police.ajouterChaleur(3);
            const chaleur = r.etoiles;
            r.etoiles = 0; r.chaleur = 0;
            const plancher = L.Police.etoilesAuMoins(2);
            const etoiles = r.etoiles;
            r.etoiles = 0; r.chaleur = 0;
            return { chaleur: chaleur, plancher: plancher, etoiles: etoiles };
        }
        poser(L, 'ville');
        out.ville = essayer();
        const porte = poser(L, 'ile');
        out.ile = essayer();
        L.B.joueur.y = (porte.y + 1) * L.TT + 8;
        out.entre = o.entrer(porte);
        out.dedans = !!L.B.interieur;
        out.chapelle = essayer();
        return out;
    }""")
    assert r["ville"] == {"chaleur": 1, "plancher": True, "etoiles": 2}, r["ville"]
    assert r["ile"] == {"chaleur": 0, "plancher": False, "etoiles": 0}, r["ile"]
    assert r["entre"] is True and r["dedans"] is True
    assert r["chapelle"] == {"chaleur": 0, "plancher": False, "etoiles": 0}, r["chapelle"]


def test_l_agent_qui_t_a_suivi_rentre(banc):
    """⚠️ Un agent qui t'a suivi à la nage ne t'arrête pas sur l'île, et il ne
    te regarde plus — sinon il remettait `vu` à zéro à chaque regard et les
    étoiles ne tombaient jamais. En ville, le même agent te cueille."""
    r = banc("""function (L, o) {""" + POSER + """
        L.Jeu.commencer();
        const r = L.B.recherche, j = L.B.joueur, out = {};
        for (const ou of ['ville', 'ile']) {
            poser(L, ou);
            L.B.etat = 'jeu';
            r.etoiles = 2; r.chaleur = 0; r.vu = 0;
            let a = null;
            for (const [dx, dy] of [[0, 20], [20, 0], [-20, 0], [0, -20]]) {
                if (L.Monde.marchablePieton(Math.floor((j.x + dx) / L.TT), Math.floor((j.y + dy) / L.TT))) {
                    a = L.Police.creerAgent(j.x + dx, j.y + dy, 'poursuit');
                    break;
                }
            }
            L.Entites.regarder(a, j.x - a.x, j.y - a.y);
            L.Entites.indexer();
            let arrete = false;
            for (let i = 0; i < 180 && !arrete; i++) {
                o.frame(1);
                arrete = L.B.etat === 'prison' || !!L.B.menu;
            }
            out[ou] = { arrete: arrete, etat: a.etat, vu: r.vu };
            L.B.menu = null; L.B.etat = 'jeu';
            L.Entites.retirer(a);
        }
        return out;
    }""")
    assert r["ville"]["arrete"] is True, f"le temoin ne mord pas : en ville, l'agent n'arrete personne ({r['ville']})"
    assert r["ile"]["arrete"] is False, "l'agent t'a arrete sur l'ile"
    assert r["ile"]["etat"] == "flane", r["ile"]
    assert r["ile"]["vu"] > 100, f"l'agent te regarde encore : vu = {r['ile']['vu']}"


def test_les_maisons_de_l_ile_se_peignent_en_bois_et_sans_escalier(banc):
    """Le peintre lit `declin` : des planches de SA couleur d'un coin à l'autre,
    et pas une marche de fer. ⚠️ Le témoin : un logement de ville à deux étages
    et à escalier, peint par la même fonction, a ses marches — sans lui, « pas
    d'escalier » pourrait vouloir dire que le banc n'en peint jamais."""
    r = banc("""function (L, o) {
        const def = L.B.defs, fiche = def.carte.ile, murs = def.devantures.murs;
        const declins = def.devantures.declins, fer = def.devantures.fer;
        const dans = function (r) { return r.x >= fiche.x && r.x < fiche.x + fiche.l
                                         && r.y >= fiche.y && r.y < fiche.y + fiche.h; };
        const peindre = function (r) {
            const c = o.doc.createElement('canvas').getContext('2d');
            c.traces = [];
            L.FACADES.residence(c, r, murs[r.mur % murs.length], fer, 0, 0,
                              r.declin != null ? declins[r.declin] : null);
            return c.traces;
        };
        const maisons = def.carte.residences.filter(function (r) { return dans(r) && r.declin != null; });
        const out = { maisons: [], temoin: null };
        maisons.forEach(function (r) {
            const t = peindre(r), d = declins[r.declin];
            out.maisons.push({ l: r.l, planche: t.some(function (q) { return q[4] === d.planche && q[2] === r.l * 16; }),
                               marches: t.filter(function (q) { return q[4] === fer.marche; }).length });
        });
        const ville = def.carte.residences.find(function (r) { return !dans(r) && r.etages >= 2 && r.escalier !== null; });
        out.temoin = peindre(ville).filter(function (q) { return q[4] === fer.marche; }).length;
        return out;
    }""")
    assert r["temoin"] > 0, "le témoin ne mord pas : même en ville, aucune marche de fer"
    assert len(r["maisons"]) == 6
    for m in r["maisons"]:
        assert m["planche"], f"une maison de l'île sans ses planches : {m}"
        assert m["marches"] == 0, f"un escalier de fer sur une maison de pêcheur : {m}"
