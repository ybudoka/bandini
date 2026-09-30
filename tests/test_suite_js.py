"""La suite du paquet, au banc (docs/jalons/le-paquet-des-definitions-maigrit.md, la deuxième cure).

Le Clairon (manchettes, leçons, matins calmes, la photo de Louise) et la hantise des Galeries voyagent sur
`/api/suite` (`definitions.DANS_LA_SUITE`), demandé juste après les définitions et remis dans `B.defs` à son
arrivée (`Suite`). Ces juges partent du paquet NU (`poser_la_suite=False`) : c'est le jeu qui doit aller la
chercher. Ce qu'ils tiennent, chacun la preuve d'une clé :

- la suite est demandée au démarrage, UNE fois, et ses clés reviennent sous leur nom ;
- un jour qui se lève avant elle ne perd pas sa une : la manchette ATTEND, puis s'affiche et se dit ;
- une demande ratée se refait, sans marteler (une fois par `REESSAI_IMAGES`) ;
- sans elle, rien ne lève : le déclic de la photo, Louise, les Galeries la nuit, le bulletin de la radio.
"""

from app import definitions


def test_la_suite_arrive_au_demarrage_et_reprend_ses_cles(banc, suite_du_paquet):
    r = banc("""function (L, o) {
        const demandes = o.fetchs.filter(function (f) { return String(f.url).indexOf('/api/suite') === 0; });
        return { arrivee: L.Suite.arrivee(), demandes: demandes.length, url: demandes.length ? String(demandes[0].url) : null,
                 cles: Object.keys(L.B.defs).filter(function (k) { return k in %s; }).sort(),
                 matins: (L.B.defs.journal_matins || []).length };
    }""" % _cles_js())
    assert r["arrivee"] is True
    assert r["demandes"] == 1, "la suite se demande une fois, au démarrage"
    assert r["url"] == f"/api/suite?e={suite_du_paquet['empreinte']}", "par son empreinte : la clé du cache hors ligne"
    assert r["cles"] == sorted(definitions.DANS_LA_SUITE)
    assert r["matins"] == len(suite_du_paquet["journal_matins"])


def _cles_js() -> str:
    return "{" + ", ".join(f"{c}: 1" for c in definitions.DANS_LA_SUITE) + "}"


def test_le_paquet_nu_ne_porte_pas_la_suite(banc):
    """Le témoin des juges qui suivent : `poser_la_suite=False` retire bien ses clés AVANT le démarrage, et la
    première demande tombe (`suite_panne=1`) — le jeu est à l'écran titre sans elle, et sans une exception."""
    r = banc("""function (L, o) {
        return { etat: L.Suite.etat(), journal: 'journal' in L.B.defs, galeries: 'galeries' in L.B.defs,
                 titre: L.B.etat };
    }""", poser_la_suite=False, suite_panne=1)
    assert r == {"etat": "ratee", "journal": False, "galeries": False, "titre": "titre"}


def test_la_manchette_attend_la_suite_puis_s_affiche_et_se_dit(banc):
    """⚠️ UN TEXTE N'A PAS DE REPLI. Le jour se lève (une partie reprise à 23 h 59, un réseau lent) avant que
    la suite soit là : la manchette ne se perd pas, elle attend. Dix secondes plus tard la demande se refait,
    la suite arrive, et le Clairon paraît — la une et la voix du narrateur, comme avant la cure."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        L.B.dialogue = null;
        const p = L.B.partie;
        p.stats.tues = 2;
        L.Missions.nouveauJour();
        const avant = { dialogue: !!L.B.dialogue, attentes: L.Suite.attentes(), manchette: p.derniereManchette || null };
        function demandes() { return o.fetchs.filter(function (f) { return String(f.url).indexOf('/api/suite') === 0; }).length; }
        const d0 = demandes();
        // Une image : pas de martèlement.
        o.frame(1);
        const d1 = demandes();
        // Dix secondes : la demande se refait, et la suite arrive.
        for (let i = 0; i < L.Suite.REESSAI_IMAGES + 5 && !L.Suite.arrivee(); i++) { o.frame(1); }
        return o.attendre().then(function () {
          return { avant: avant, d0: d0, d1: d1, d2: demandes(), arrivee: L.Suite.arrivee(),
                   qui: L.B.dialogue && L.B.dialogue.qui, titre: L.B.dialogue && L.B.dialogue.lignes[0],
                   lue: L.Son.Voix.demandees[L.Son.Voix.demandees.length - 1] || null,
                   manchette: p.derniereManchette && p.derniereManchette.slug, attentes: L.Suite.attentes() };
        });
    }""", poser_la_suite=False, suite_panne=1)
    assert r["avant"] == {"dialogue": False, "attentes": 1, "manchette": None}, \
        "sans la suite, le Clairon a parlé quand même — ou il n'attend rien"
    assert r["d0"] == 1 and r["d1"] == 1, "une demande ratée ne se martèle pas à chaque image"
    assert r["d2"] == 2 and r["arrivee"] is True
    assert r["qui"] == "LE CLAIRON DE LA BAIE" and r["titre"] == "UN MORT DANS LA RUE", r
    assert r["lue"] == "narrateur-journal-un_mort", "la une s'affiche, mais le narrateur ne la dit plus"
    assert r["manchette"] == "un_mort" and r["attentes"] == 0


def test_la_une_d_un_matin_passe_ne_parait_pas_le_lendemain(banc):
    """Deux matins se lèvent avant la suite : seule la une du DERNIER paraît. Celle d'hier, attendue, ne
    s'affiche pas par-dessus celle d'aujourd'hui."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        L.B.dialogue = null;
        L.Missions.nouveauJour();
        L.B.partie.jour += 1;
        L.Missions.nouveauJour();
        const vues = [];
        const dialogue = L.Hud.dialogue;
        L.Hud.dialogue = function (qui) { vues.push(qui); return dialogue.apply(this, arguments); };
        for (let i = 0; i < L.Suite.REESSAI_IMAGES + 5 && !L.Suite.arrivee(); i++) { o.frame(1); }
        return o.attendre().then(function () {
          return { vues: vues.filter(function (q) { return q === 'LE CLAIRON DE LA BAIE'; }).length, arrivee: L.Suite.arrivee() };
        });
    }""", poser_la_suite=False, suite_panne=1)
    assert r == {"vues": 1, "arrivee": True}


def test_sans_la_suite_rien_ne_leve(banc):
    """Ce qui lit une clé de la suite se tait sans elle — jamais une exception (dans `maj()`, elle figerait
    l'écran sans un mot) : le déclic de la photo, Louise, les Galeries la nuit, le bulletin de la radio."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const erreurs = [];
        function essayer(nom, f) { try { f(); } catch (e) { erreurs.push(nom + ' : ' + e.message); } }
        essayer('declic', function () { L.Photos.declic({ x: L.B.cam.x, y: L.B.cam.y }); });
        essayer('louise', function () { L.Photos.accueillir(false); });
        essayer('ligne', function () { L.Photos.ligneDuClairon(); L.Photos.matin(); });
        L.B.partie.derniereManchette = { slug: 'un_mort', titre: 'UN MORT DANS LA RUE', texte: '' };
        let bulletin = 'pas appele';
        essayer('bulletin', function () { bulletin = L.Son.Ondes.bulletin(); });
        // Les Galeries, la nuit : on y est, et la hantise n'est pas là.
        L.B.partie.heure = 0.95;
        L.B.interieur = { slug: 'galeries' };
        essayer('galeries', function () { L.Galeries.maj(); L.Galeries.dessiner(o.ctx, { x: 0, y: 0 }); });
        L.B.interieur = null;
        return { erreurs: erreurs, bulletin: bulletin, suite: L.Suite.etat() };
    }""", poser_la_suite=False, suite_panne=1)
    assert r["suite"] == "ratee", "le témoin : la suite n'est pas là"
    assert r["erreurs"] == [], r["erreurs"]
    assert r["bulletin"] is None, "sans les leçons, la radio ne sait pas si la une en est une : elle se tait"
