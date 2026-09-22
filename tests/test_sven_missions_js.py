"""Les trois missions de Sven (m52-m54) : ce que le nouveau moteur leur doit — un donneur
posé sur son mouillage, un véhicule qui naît à la bonne place sur l'eau, avec le bon cap et
prêté par lui, et une récompense qui tombe à la fin. Le piratage lui-même a ses juges
(`test_piratage_js.py`) ; ceux-ci portent sur ce qui est PROPRE aux missions."""


def test_sven_nait_sur_son_poste_pres_du_porte_conteneurs(banc):
    """⚠️ Sur le POSTE (`carte.mouillages[…].poste`), pas sur le centre de la coque — et pas
    PILE dessus non plus : un personnage planté là volerait le bouton ACTION au bateau
    (`Histoire.poserDonneurMouillage`)."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const sven = L.B.entites.find(function (e) { return e.personnage === 'sven'; });
        const mo = L.B.defs.carte.mouillages.find(function (m) { return m.slug === 'porte_conteneurs'; });
        return { sven: sven && { x: sven.x, y: sven.y }, poste: mo.poste,
                 surLePoste: sven && sven.x === mo.poste.x && sven.y === mo.poste.y,
                 marchable: sven && L.Monde.marchablePieton(Math.floor(sven.x / 16), Math.floor(sven.y / 16)) };
    }""")
    assert r["sven"], "le décor du juge est faux : Sven n'est pas né"
    assert r["marchable"], "Sven flotte : il n'est pas sur une tuile marchable"
    assert not r["surLePoste"], "Sven se tient pile sur le poste : il bouche l'accès au bateau"


def test_m52_prend_la_chaloupe_amarree_pres_de_sven(banc):
    """`amarrage:sven` : la chaloupe amarrée le plus près de son mouillage — prêtée, hors
    de la naissance décorative habituelle (`Vehicules.majMouillages`/`majAmarrages`)."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        L.Histoire.commencer('m52');
        o.frame(2); L.B.cinema = null; L.B.scene = null;
        const v = L.B.mission.vehicule;
        const am = L.Histoire.resoudre('amarrage:sven', L.Histoire.courante());
        return { slug: v && v.slug, aQui: v && v.aQui, etat: v && v.etat,
                 surLeau: v && !L.Vehicules.tuileInterdite(v, Math.floor(v.x / 16), Math.floor(v.y / 16)),
                 place: v && { x: v.x, y: v.y }, amarrage: am };
    }""")
    assert r["slug"] == "bateau", r
    assert r["aQui"] == "sven"
    assert r["etat"] == "stationne"
    assert r["surLeau"], "la chaloupe de m52 ne naît pas sur l'eau"
    assert r["place"] == r["amarrage"] or (abs(r["place"]["x"] - r["amarrage"]["x"]) < 20
                                            and abs(r["place"]["y"] - r["amarrage"]["y"]) < 20)


def test_m52_va_jusqu_au_bout_et_paie(banc):
    """La chaîne complète (les étapes qui ne dépendent pas du piratage) : sauter au dernier
    objectif, réussir, encaisser — comme les juges existants le font pour m4/m5."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const avant = L.B.partie.argent;
        L.Histoire.commencer('m52');
        o.frame(2); L.B.cinema = null; L.B.scene = null;
        L.B.partie.mission.etape = 4;                  // `retourner`, déjà fait ailleurs
        L.Histoire.reussir();
        return { argent: L.B.partie.argent - avant, mission: L.B.partie.mission,
                 faite: L.B.partie.missionsFaites && L.B.partie.missionsFaites.m52 };
    }""")
    assert r["argent"] == 350, r
    assert r["mission"] is None, "la mission reste ouverte après reussir()"
    assert r["faite"]


def test_m53_les_deux_quais_de_chalutier_sont_distincts(banc):
    """`mouillage:chalutier:0` et `:1` : deux places différentes — sinon `monter` et
    `livrer` de m53 visent la même coque et le trajet n'existe pas."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const a = L.Histoire.resoudre('mouillage:chalutier:0', { donneur: 'sven' });
        const b = L.Histoire.resoudre('mouillage:chalutier:1', { donneur: 'sven' });
        return { a: a, b: b, distincts: a.x !== b.x || a.y !== b.y };
    }""")
    assert r["a"] and r["b"], "le décor du juge est faux : moins de deux chalutiers"
    assert r["distincts"], "les deux quais de chalutier se confondent"


def test_m53_prend_le_chalutier_au_bon_quai(banc):
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        L.Histoire.commencer('m53');
        o.frame(2); L.B.cinema = null; L.B.scene = null;
        const v = L.B.mission.vehicule;
        const cible = L.Histoire.resoudre('mouillage:chalutier:0', L.Histoire.courante());
        return { slug: v && v.slug, aQui: v && v.aQui, angle: v && v.angle, cibleAngle: cible.mouillage.angle,
                 place: v && { x: v.x, y: v.y }, cible: { x: cible.x, y: cible.y } };
    }""")
    assert r["slug"] == "chalutier"
    assert r["aQui"] == "sven"
    assert r["place"] == r["cible"], "le chalutier ne naît pas au centre exact de son mouillage"
    assert r["angle"] == r["cibleAngle"], "il ne part pas dans le sens de son chenal"


def test_m53_va_jusqu_au_bout_et_paie(banc):
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const avant = L.B.partie.argent;
        L.Histoire.commencer('m53');
        o.frame(2); L.B.cinema = null; L.B.scene = null;
        L.B.partie.mission.etape = 4;
        L.Histoire.reussir();
        return { argent: L.B.partie.argent - avant };
    }""")
    assert r["argent"] == 500, r


def test_m54_prend_la_coque_decorative_sans_la_dedoubler(banc):
    """⚠️ « PRENDRE LA COQUE, PAS LA DÉDOUBLER » (`Histoire.poserLeChar`) : objectif 0 est
    `pirater`, pas `monter` — quand la mission ATTEINT `monter`, si le porte-conteneurs
    décoratif (`Vehicules.majMouillages`) est déjà né à son mouillage, c'est LUI qu'on
    prend, pas un second par-dessus. Il ne naît qu'à portée du joueur (comme tout
    décor, `test_navires_js.py`) : on s'en approche d'abord, hors mission."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const mo = L.B.defs.carte.mouillages.find(function (m) { return m.slug === 'porte_conteneurs'; });
        const j = L.B.joueur;
        // ⚠️ Assez près pour naître (`portee_px` 560, moins `GAREES_MARGE` 60), assez loin
        // de l'écran (270 px de haut, marge 104) pour ne pas être le pop-in
        // qu'`Entites.visibleAEcran` refuse (`Vehicules.majMouillages`) : 450 px droit au
        // nord passe les deux bornes.
        j.x = mo.x; j.y = mo.y - 450; L.Monde.centrerCamera(j.x, j.y); L.Entites.indexer();
        o.frame(21);
        const decoratif = L.B.entites.find(function (e) { return e.slug === 'porte_conteneurs'; });
        L.Histoire.commencer('m54');
        o.frame(2); L.B.cinema = null; L.B.scene = null;
        L.Histoire.avancer();                          // de `pirater` (0) à `monter` (1) — `poser()` s'exécute
        o.frame(2);
        const v = L.B.mission.vehicule;
        const tous = L.B.entites.filter(function (e) { return e.slug === 'porte_conteneurs'; });
        return { decoratif: !!decoratif, meme: v === decoratif, aQui: v && v.aQui, combien: tous.length };
    }""")
    assert r["decoratif"], "le décor du juge est faux : le porte-conteneurs n'est jamais né"
    assert r["meme"], "la mission a fait naître un second porte-conteneurs au lieu de prendre celui qui dormait"
    assert r["aQui"] == "sven"
    assert r["combien"] == 1, "deux porte-conteneurs collés au même quai"


def test_m54_semer_puis_livrer_et_ca_paie(banc):
    """Le `semer` (2 étoiles) avance vers `livrer`, puis la chaîne jusqu'au bout paie.
    ⚠️ En sautant `monter`, aucun véhicule de mission n'existe : `livrer` le refuserait
    (`vehicule_detruit`, à raison — sans char, rien à livrer) — on en pose un factice,
    comme `poser()` l'aurait fait pour de vrai."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const avant = L.B.partie.argent;
        L.Histoire.commencer('m54');
        o.frame(2); L.B.cinema = null; L.B.scene = null;
        L.B.partie.mission.etape = 2;                  // `semer`
        L.B.mission.vehicule = { etat: 'stationne', mission: 'm54' };
        L.B.recherche.etoiles = 2;
        const enCoursDePoursuite = L.Histoire.objectif().type === 'semer';
        L.B.recherche.etoiles = 0;                      // semée
        o.frame(4);                                      // le pas fixe : jamais fier d'une seule image
        const apresSemer = L.B.partie.mission.etape;
        L.B.partie.mission.etape = 4;                  // `retourner`
        L.Histoire.reussir();
        return { argent: L.B.partie.argent - avant, enCoursDePoursuite: enCoursDePoursuite,
                 apresSemer: apresSemer };
    }""")
    assert r["enCoursDePoursuite"]
    assert r["apresSemer"] == 3, "semer à 0 étoile ne fait pas avancer vers `livrer`"
    assert r["argent"] == 900, r
