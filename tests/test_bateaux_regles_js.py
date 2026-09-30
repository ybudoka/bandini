"""Les bateaux ne sont pas des chars, vague 2 — ce qui n'est pas une règle de bateau.

Une coque n'est jamais « mal garée » ni saisie (elle renaissait sur la terre ferme du lot), la remorqueuse ne
l'accroche pas, Ti-Guy ne la prend pas, elle ne prend la place d'aucune auto garée, le carnet la compte à part
(BATEAUX VOLÉS), la frénésie « chars » ne la compte pas, et le traversier n'accoste pas sur elle."""

#: Le plein large : de l'eau sur quatre tuiles autour. Une coque et une auto posées là, sans conducteur.
AIDES = """
    function pleinLarge(L) {
        const c = L.Monde.carte;
        for (let ty = 8; ty < c.h - 8; ty++) for (let tx = 8; tx < c.w - 8; tx++) {
            let plein = true;
            for (let dy = -4; dy <= 4 && plein; dy++) for (let dx = -4; dx <= 4 && plein; dx++) if (!L.Monde.estEau(tx + dx, ty + dy)) plein = false;
            if (plein) return { x: tx * L.TT + 8, y: ty * L.TT + 8 };
        }
        return null;
    }
    function pose(L, slug, x, y) { return L.Vehicules.creer(slug, x, y, 0, { etat: 'stationne', couleur: '#3a6fb0' }); }
    function auLarge(L) {
        const p = pleinLarge(L), j = L.B.joueur;
        j.x = p.x; j.y = p.y - 40; L.Monde.centrerCamera(j.x, j.y);
        return p;
    }
"""


def test_une_coque_n_est_jamais_mal_garee_ni_saisie(banc):
    """Toute la ville en chaussée (bouchée) : l'auto laissée là est mal garée, la coque jamais ; au poste, la
    fourrière saisit la dernière auto conduite, jamais la dernière coque."""
    r = banc("function (L, o) {" + AIDES + """
        L.Jeu.commencer();
        const p = auLarge(L), j = L.B.joueur, M = L.Monde;
        const coque = pose(L, 'bateau', p.x, p.y), auto = pose(L, 'auto', p.x + 60, p.y);
        coque.laisse = auto.laisse = true;
        const vraie = M.estChaussee; M.estChaussee = function () { return true; };
        const mal = { coque: L.Missions.malGare(coque), auto: L.Missions.malGare(auto) };
        M.estChaussee = vraie;
        j.dernierVehicule = coque; const saisieCoque = L.Missions.charSaisissable(j) === coque;
        j.dernierVehicule = auto; const saisieAuto = L.Missions.charSaisissable(j) === auto;
        return { mal: mal, saisieCoque: saisieCoque, saisieAuto: saisieAuto };
    }""")
    assert r["mal"]["auto"], "la chaussée bouchée ne rend même pas l'auto mal garée"
    assert not r["mal"]["coque"], "une coque est « mal garée »"
    assert r["saisieAuto"], "la fourrière ne saisit plus l'auto"
    assert not r["saisieCoque"], "la fourrière saisit une coque (elle renaît sur la terre ferme du lot)"


def test_le_lot_de_la_fourriere_ne_rend_pas_une_coque_sur_la_terre(banc):
    """Une vieille partie qui a une coque au lot (saisie avant la règle) : la cour ne la pose pas sur la terre
    ferme, et le lot l'oublie ; l'auto d'à côté est posée comme avant."""
    r = banc("function (L, o) {" + AIDES + """
        L.Jeu.commencer();
        const fiche = function (slug) { const d = L.Vehicules.vehiculeDef(slug); return { slug: slug, sprite: d.sprite, couleur: '#3a6fb0', vie: 100, vole: false, mods: {} }; };
        L.B.partie.fourriere = [fiche('bateau'), fiche('auto')];
        const coques = function () { return L.B.entites.filter(function (e) { return e.type === 'vehicule' && e.def.eau && e.saisi !== undefined && e.saisi !== null; }).length; };
        const autos = function () { return L.B.entites.filter(function (e) { return e.type === 'vehicule' && e.slug === 'auto' && e.saisi !== undefined && e.saisi !== null; }).length; };
        L.Missions.garnirLaFourriere();
        return { coques: coques(), autos: autos(), lot: L.B.partie.fourriere.map(function (c) { return c.slug; }) };
    }""")
    assert r["autos"] == 1, f"l'auto du lot n'est pas posée : {r}"
    assert r["coques"] == 0, "une coque est posée dans la cour du lot, sur la terre ferme"
    assert r["lot"] == ["auto"], f"le lot garde une coque : {r['lot']}"


def test_la_remorqueuse_n_accroche_pas_une_coque(banc):
    r = banc("function (L, o) {" + AIDES + """
        L.Jeu.commencer();
        const p = auLarge(L), def = L.B.defs.vehicules.find(function (q) { return q.crochet; });
        const rem = pose(L, def.slug, p.x, p.y);
        const derriere = p.x - def.longueur / 2 - 12;
        const coque = pose(L, 'bateau', derriere, p.y); L.Entites.indexer();
        const surCoque = L.Vehicules.aCrocher(rem) === coque;
        L.Entites.retirer(coque);
        const auto = pose(L, 'auto', derriere, p.y); L.Entites.indexer();
        return { surCoque: surCoque, surAuto: L.Vehicules.aCrocher(rem) === auto };
    }""")
    assert r["surAuto"], "la remorqueuse n'accroche même pas l'auto"
    assert not r["surCoque"], "la remorqueuse accroche une coque (et la tire sur la terre)"


def test_ti_guy_ne_prend_pas_une_coque(banc):
    """Le garage (vendre, repeindre, les pièces) prend le char garé devant sa porte : jamais une coque."""
    r = banc("function (L, o) {" + AIDES + """
        L.Jeu.commencer();
        const p = auLarge(L), coque = pose(L, 'bateau', p.x, p.y), auto = pose(L, 'auto', p.x, p.y + 40);
        L.B.exterieur = { x: p.x, y: p.y, entites: [coque] };
        const devantCoque = L.Missions.charDevant();
        L.B.exterieur = { x: p.x, y: p.y, entites: [auto] };
        const devantAuto = L.Missions.charDevant();
        L.B.exterieur = null;
        return { coque: devantCoque === coque, auto: devantAuto === auto, pieces: L.Garage.accepte(coque), piecesAuto: L.Garage.accepte(auto) };
    }""")
    assert r["auto"] and r["piecesAuto"], f"Ti-Guy ne prend même plus l'auto : {r}"
    assert not r["coque"], "Ti-Guy prend une coque devant sa porte"
    assert not r["pieces"], "une coque prend des pièces de char (nitro, pneus d'hiver)"


def test_une_coque_ne_prend_la_place_d_aucune_auto_garee(banc):
    """`peupler` compte les chars garés pour savoir combien en faire naître : une coque amarrée n'en est pas un."""
    r = banc("function (L, o) {" + AIDES + """
        L.Jeu.commencer();
        const p = auLarge(L), coque = pose(L, 'bateau', p.x, p.y), auto = pose(L, 'auto', p.x, p.y + 40);
        coque.amarrage = { x: 0, y: 0 };
        return { coque: L.Vehicules.compteCommeGare(coque), auto: L.Vehicules.compteCommeGare(auto) };
    }""")
    assert r["auto"], "une auto garée ne compte plus"
    assert not r["coque"], "une coque amarrée compte comme une auto garée"


def test_une_coque_volee_compte_aux_bateaux_voles(banc):
    """Voler une coque amarrée : BATEAUX VOLÉS, au carnet du poste et au BILAN — pas CHARS VOLÉS."""
    r = banc("function (L, o) {" + AIDES + """
        L.Jeu.commencer();
        const p = auLarge(L), j = L.B.joueur, s = L.B.partie.stats;
        const coque = pose(L, 'bateau', p.x, p.y + 20);
        L.Vehicules.monter(j, coque);
        const apresCoque = { chars: s.volees, bateaux: s.bateauxVoles };
        L.Vehicules.descendre(j, true);
        const auto = pose(L, 'auto', p.x, p.y - 120);
        L.Vehicules.monter(j, auto);
        const ligne = function (menu, nom) { const i = (menu.items || []).find(function (q) { return q.libelle === nom; }); return i ? i.detail : null; };
        const carnet = L.Missions.menuCasier(), bilan = L.Hud.menuBilan();
        return { apresCoque: apresCoque, chars: s.volees, bateaux: s.bateauxVoles,
                 carnet: ligne(carnet, 'BATEAUX VOLÉS'), bilan: ligne(bilan, 'BATEAUX VOLÉS') };
    }""")
    assert r["apresCoque"] == {"chars": 0, "bateaux": 1}, f"la coque volée compte aux chars : {r['apresCoque']}"
    assert r["chars"] == 1 and r["bateaux"] == 1, r
    assert r["carnet"] == "1", f"le carnet du poste n'a pas sa ligne BATEAUX VOLÉS : {r['carnet']}"
    assert r["bilan"] == "1", f"le BILAN n'a pas sa ligne BATEAUX VOLÉS : {r['bilan']}"


def test_la_frenesie_des_chars_ne_compte_pas_les_bateaux(banc):
    r = banc("function (L, o) {" + AIDES + """
        L.Jeu.commencer();
        const p = auLarge(L), j = L.B.joueur;
        const f = L.Frenesies.toutes().find(function (q) { return q.cible === 'chars'; });
        L.B.frenesie = { slug: f.slug, t: 0, compte: 0, avant: null, renfortT: 0 };
        const coque = pose(L, 'bateau', p.x, p.y); coque.agresseur = j;
        L.Frenesies.detruit(coque);
        const apresCoque = L.B.frenesie.compte;
        const auto = pose(L, 'auto', p.x, p.y + 40); auto.agresseur = j;
        L.Frenesies.detruit(auto);
        return { apresCoque: apresCoque, apresAuto: L.B.frenesie.compte };
    }""")
    assert r["apresAuto"] == r["apresCoque"] + 1, f"l'auto détruite ne compte plus : {r}"
    assert r["apresCoque"] == 0, "la frénésie « chars » compte une coque"


def test_le_traversier_n_accoste_pas_sur_une_coque(banc):
    """À l'heure de l'escale, une chaloupe mouille sous le pont : le traversier attend (le pont reste de l'eau,
    la chaloupe n'est pas prise dans le sol) ; elle s'en va, il accoste."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const a = L.Traversier.donnees().escales[0], j = L.B.joueur, TT = L.TT;
        j.x = a.px - 200; j.y = a.py - 200; L.Monde.centrerCamera(j.x, j.y);
        L.B.partie.heure = 1.2 / 24; o.frame(2);
        L.Traversier.oublier(); L.Navette.oublier();
        const coque = L.Vehicules.creer('bateau', (a.x + 3) * TT + 8, a.y * TT + 8, 0, { etat: 'stationne' });
        L.B.partie.heure = 1.9 / 24; o.frame(2);
        const attend = { pont: L.Monde.estEau(a.x + 3, a.y), pose: !!L.Traversier.pose };
        L.Entites.retirer(coque); o.frame(2);
        return { attend: attend, accoste: !L.Monde.estEau(a.x + 3, a.y) };
    }""")
    assert r["accoste"], "sans coque, le traversier n'accoste plus"
    assert r["attend"]["pont"] and not r["attend"]["pose"], "le traversier pose son pont sur une coque"
