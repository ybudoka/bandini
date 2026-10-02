"""Les enseignes qui ouvrent pour vrai, au banc (docs/jalons/les-enseignes-qui-ouvrent-pour-vrai.md) : on
entre au bingo, au Rialto, à la salle de quilles et au lave-auto, et chaque comptoir donne quelque chose ; le
bingo et les quilles se jouent sans un `B.rng()` ; le Rialto passe son film le soir ; un char lavé perd un
cran de chaleur, une fois par passage."""

import pytest

from app import enseignes

OUTILS = """
  const TT = 16;
  function entrer(L, o, slug) {
    const B = L.B, j = B.joueur, porte = L.Monde.carte.def.portes.find(function (q) { return q.interieur === slug; });
    if (!porte) return null;
    if (B.menu) L.Hud.fermerMenu();
    j.x = porte.x * TT + 8; j.y = (porte.y + 1) * TT + 4; L.Entites.indexer();
    L.Jeu.entrer(porte); o.fondu();
    for (let k = 0; k < 200 && !B.interieur; k++) o.frame(1);
    return B.interieur && B.interieur.slug === slug ? B.interieur.points.find(function (q) { return q.type === 'emplettes'; }) : null;
  }
  function libelles(m) { return m ? m.items.map(function (i) { return i.libelle; }) : null; }
  function item(m, debut) { return m.items.find(function (i) { return i.libelle.indexOf(debut) === 0; }); }
"""


def test_on_entre_dans_les_quatre_et_chaque_comptoir_donne_quelque_chose(banc):
    r = banc("function (L, o) {" + OUTILS + """
        L.Jeu.commencer();
        const B = L.B, M = L.Missions, out = {};
        B.partie.heure = 14 / 24;
        // La ligue du mardi s'ouvre apres trois defis, comme la tire.
        L.Histoire.ouvrirDefi(B.defs.defis.find(function (q) { return q.slug === 'quilles'; }), true);
        for (const slug of ['bingo', 'rialto', 'quilles', 'lave_auto']) {
            const pt = entrer(L, o, slug);
            out[slug] = pt ? libelles(M.menuDuPoint(pt)) : null;
            L.Jeu.sortir(); o.fondu(); for (let k = 0; k < 200 && B.interieur; k++) o.frame(1);
        }
        return out;
    }""")
    assert "UNE CARTE DE BINGO" in r["bingo"] and "CAFÉ" in r["bingo"], r["bingo"]
    assert "MAÏS ÉCLATÉ" in r["rialto"] and "MAÏS SOUFFLÉ" not in r["rialto"] and "LA SÉANCE EST À 18 H" in r["rialto"], r["rialto"]
    assert "LA LIGUE DU MARDI — DÉFI" in r["quilles"] and "GROSSE BIÈRE" in r["quilles"], r["quilles"]
    assert any(i.startswith("LE LAVAGE") for i in r["lave_auto"]), r["lave_auto"]


def test_le_bingo_se_gagne_au_crayon_et_se_perd_aux_madames_sans_un_de(banc):
    """Une carte achetée : le boulier tourne. En marquant chaque boule de sa carte, on gagne parfois le gros
    lot ; les mains dans les poches, une madame crie toujours avant. Et la partie ne tire pas un dé."""
    r = banc("function (L, o) {" + OUTILS + """
        L.Jeu.commencer();
        const B = L.B, M = L.Missions, E = L.Enseignes, A = L.Adresse;
        const pt = entrer(L, o, 'bingo');
        function partie(marquer) {
            // ⚠️ L'heure a chaque carte : une partie dure deux minutes, et le comptoir ferme a 23 h.
            B.partie.heure = 14 / 24; B.partie.argent = 100;
            const avant = B.partie.argent, msgs = [], hud = L.Hud.message;
            L.Hud.message = function (m) { msgs.push(m); return hud.apply(null, arguments); };
            item(M.menuDuPoint(pt), 'UNE CARTE').faire();
            const carte = B.epreuve.carte.slice();
            for (let k = 0; k < 75 * 4 * 60 && E.bingo; k++) {
                const e = B.epreuve;
                if (marquer && e && e.k >= 0 && e.fenetre === 30 && e.carte.indexOf(e.ordre[e.k]) >= 0) o.tape('KeyE', 1);
                else o.frame(1);
            }
            L.Hud.message = hud;
            return { gain: B.partie.argent - avant, fin: msgs.filter(function (m) { return /BINGO|BOULES/.test(m); }).pop() || '', carte: carte };
        }
        const parties = [];
        for (let n = 0; n < 20 && !parties.some(function (p) { return p.gain > 0; }); n++) parties.push(partie(true));
        const mains = partie(false);
        // Aucun de : la partie seule, du boulier a la derniere boule, entre deux tirages — en marquant.
        // ⚠️ Le temoin AVANT la carte : c'est en la tirant (et l'ordre des boules) qu'un de se glisserait.
        B.partie.heure = 14 / 24; B.partie.argent = 100;
        L.graine(9); const temoin = [B.rng(), B.rng()]; L.graine(9);
        item(M.menuDuPoint(pt), 'UNE CARTE').faire();
        const ep = B.epreuve, d = E.bingo, neuf = L.Entree.neuf;
        L.Entree.neuf = function (a) { return a === 'action' && ep.k >= 0 && ep.carte.indexOf(ep.ordre[ep.k]) >= 0; };
        for (let k = 0; k < 75 * 4 * 60 && !A.maj(d); k++);
        const apres = [B.rng(), B.rng()];
        L.Entree.neuf = neuf;
        const g1 = E.graineDuBingo(3, 2), g2 = E.graineDuBingo(3, 2), g3 = E.graineDuBingo(3, 3);
        return { parties: parties, mains: mains, de: apres[0] === temoin[0] && apres[1] === temoin[1], marquees: ep.marques.filter(Boolean).length,
                 pure: g1 === g2 && g1 !== g3 };
    }""")
    rg = enseignes.REGLES["bingo"]
    gagnees = [p for p in r["parties"] if p["gain"] == rg["gros_lot"] - rg["carte"]]
    assert gagnees, f"vingt cartes bien marquées, aucune gagnée : {r['parties']}"
    assert all("MADAMES TE REGARDENT DE TRAVERS" in p["fin"] for p in gagnees)
    assert r["mains"]["gain"] == -rg["carte"] and "UNE MADAME DU FOND" in r["mains"]["fin"], r["mains"]
    assert r["de"], "le bingo a tiré au dé du jeu"
    assert r["marquees"] >= 5, "le juge du dé n'a rien marqué"
    assert len({tuple(p["carte"]) for p in r["parties"] + [r["mains"]]}) == len(r["parties"]) + 1, "deux cartes pareilles"
    assert r["pure"]


def test_la_carte_de_bingo_se_lit_sans_ombre_sous_ses_chiffres(banc):
    """Le lettrage de la carte : l'en-tete B I N G O en double, le numero crie en triple, et AUCUNE ombre du
    HUD sous un chiffre — decalee d'un pixel sous un trait sombre sur une case creme, elle le bavait."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const B = L.B, A = L.Adresse;
        A.commencer({ slug: 'bingo', epreuve: 'bingo', consigne: '',
                      regles: { carte: 3, gros_lot: 20, appel_s: 3.2, fenetre_s: 2.6, madames: 3, graine: 12345 } });
        const e = B.epreuve;
        e.t = A.PRET + 1; e.k = 4; e.fenetre = 30; e.marques[0] = true;
        const ecrits = [], vrai = L.Atlas.texte;
        L.Atlas.texte = function (ctx, s, x, y, c, k) { ecrits.push({ s: String(s), c: c, k: k || 1 }); return vrai.apply(null, arguments); };
        try { A.dessiner(o.ctx); } finally { L.Atlas.texte = vrai; }
        return { ecrits: ecrits, carte: e.carte, boule: e.ordre[e.k] };
    }""")
    ecrits = r["ecrits"]
    ombres = [t["s"] for t in ecrits if t["c"].startswith("rgba(11,10,18")]
    chiffres = {str(n) for n in r["carte"] if n} | {str(r["boule"])}
    assert not chiffres & set(ombres), f"une ombre sous un chiffre : {sorted(chiffres & set(ombres))}"
    assert [t["s"] for t in ecrits if t["k"] == 2][:5] == list("BINGO"), ecrits
    assert {"s": str(r["boule"]), "c": "#1a1a22", "k": 3} in ecrits, ecrits
    assert all(t["s"] != "*" for t in ecrits), "la case gratuite est une etoile dessinee, pas un « * »"


def test_les_quilles_se_calculent_et_la_ligue_se_gagne_au_milieu_de_l_allee(banc):
    """Au milieu de l'allée et à pleine force : un abat. Dans le dalot : rien. La ligue du mardi se gagne en
    visant le milieu, se perd en lançant n'importe comment — sans un dé."""
    r = banc("function (L, o) {" + OUTILS + """
        L.Jeu.commencer();
        const B = L.B, A = L.Adresse, H = L.Histoire;
        const d = B.defs.defis.find(function (q) { return q.slug === 'quilles'; }), rq = d.regles;
        const calc = { milieu: A.quillesTombees(0.5, 1, rq), dalot: A.quillesTombees(0, 1, rq), molle: A.quillesTombees(0.5, 0.1, rq) };
        function appuie(e, bien) {
            const vise = e && e.phase === 'vise' && !e.pause && (bien ? Math.abs(e.vise - 0.5) < 0.03 : e.u === 20);
            const force = e && e.phase === 'force' && !e.pause && (bien ? e.force > 0.95 : e.u === 10);
            return vise || force;
        }
        function jouer(bien) {
            B.partie.defisFaits = {};
            H.commencerDefi(d);
            for (let k = 0; k < (d.chrono_s + 2) * 60 && B.defi; k++) {
                if (appuie(B.epreuve, bien)) o.tape('KeyE', 1); else o.frame(1);
            }
            return !!B.partie.defisFaits.quilles;
        }
        const bien = jouer(true), mal = jouer(false);
        // Aucun de : l'epreuve seule, cinq carreaux, entre deux tirages.
        H.commencerDefi(d);
        const ep = B.epreuve, neuf = L.Entree.neuf;
        L.Entree.neuf = function (a) { return a === 'action' && appuie(ep, true); };
        L.graine(5); const temoin = [B.rng(), B.rng()]; L.graine(5);
        for (let k = 0; k < 60 * 60 && !A.maj(d); k++);
        const apres = [B.rng(), B.rng()];
        L.Entree.neuf = neuf;
        return { calc: calc, bien: bien, mal: mal, de: apres[0] === temoin[0] && apres[1] === temoin[1], total: ep.total };
    }""")
    assert r["calc"] == {"milieu": 10, "dalot": 0, "molle": 2}, r["calc"]
    assert r["bien"] and not r["mal"], r
    assert r["de"] and r["total"] >= 32, r


@pytest.fixture(scope="module")
def une_soiree_au_rialto(banc):
    """UNE entrée au Rialto à 20 h (vague C, 28 sept. 2026 — trois bancs) : le billet de trois
    soirs lu au comptoir, puis on en prend un, et le film passe — le projecteur regardé à deux
    secondes du début, la fin et le repos à la fin.

    ⚠️ Le jour remis à celui d'avant les trois soirs, avant d'acheter : le film du juge du repos
    est celui de la partie, pas celui du 32. Le projecteur n'est pas une autre séance : c'est la
    même, deux secondes après le début — et on la laisse finir."""
    return banc("function (L, o) {" + OUTILS + """
        L.Jeu.commencer();
        const B = L.B, M = L.Missions, E = L.Enseignes, C = L.Cineparc;
        B.partie.heure = 20 / 24;
        const pt = entrer(L, o, 'rialto');
        // 1. Le billet dit le film du soir, trois soirs de suite.
        const jour = B.partie.jour, billets = [];
        for (let d = 0; d < 3; d++) {
            B.partie.jour = 30 + d;
            billets.push([item(M.menuDuPoint(pt), 'UN BILLET').libelle, L.Cineparc.programme().titre]);
        }
        B.partie.jour = jour;
        // 2. On prend un billet, la vie basse.
        const billet = item(M.menuDuPoint(pt), 'UN BILLET');
        const actif = billet && billet.actif;
        B.joueur.vie = 40;
        billet.faire();
        const pendant = !!E.film, assis = { x: Math.floor(B.joueur.x / TT), y: Math.floor(B.joueur.y / TT) };
        // 3. Deux secondes plus tard, le projecteur éclaire la toile.
        for (let k = 0; k < 120; k++) o.frame(1);
        const appels = [], vrai = C.faisceau;
        C.faisceau = function () { appels.push(Array.prototype.slice.call(arguments, 1)); return vrai.apply(null, arguments); };
        L.Jeu.rendre();
        C.faisceau = vrai;
        const projecteur = { appels: appels, hauteur: B.interieur.hauteur, toile: B.interieur.toile };
        // 4. Le film va au bout : on en sort reposé.
        for (let k = 120; k < B.defs.enseignes.regles.rialto.film_s * 60 + 5; k++) o.frame(1);
        return { billets: billets, projecteur: projecteur,
                 film: { actif: actif, pendant: pendant, assis: assis, siege: B.interieur.siege, apres: !!E.film, vie: B.joueur.vie } };
    }""")


def test_le_rialto_passe_son_film_le_soir_et_on_en_sort_repose(une_soiree_au_rialto):
    rr = enseignes.REGLES["rialto"]
    r = une_soiree_au_rialto["film"]
    assert r["actif"] and r["pendant"] and not r["apres"], r
    assert r["assis"] == r["siege"], r
    assert r["vie"] >= 40 + rr["repos_pv"], r


def test_au_rialto_le_projecteur_eclaire_la_toile_depuis_le_fond_de_la_salle(une_soiree_au_rialto):
    """Pendant le film, le faisceau (`Cineparc.faisceau`, le même qu'au ciné-parc) part du mur du fond de la
    salle et s'ouvre sur toute la toile (docs/jalons/le-casse-croute-du-cine-parc-au-centre-et-le-projecteur.md)."""
    r = une_soiree_au_rialto["projecteur"]
    assert len(r["appels"]) == 1, r
    sx, sy, x0, x1, ty, force, _t = r["appels"][0]
    t = r["toile"]
    assert force > 0 and x1 - x0 == t["l"] * 16 and abs(sx - (x0 + x1) / 2) < 1, r
    assert sy - ty == (r["hauteur"] - 1 - t["y"] - t["h"]) * 16, r


def test_la_toile_du_rialto_est_un_grand_ecran():
    """Martin : « agrandis l'écran du Rialto ». La toile prend toute la largeur de la salle, sur deux rangées (plus la
    rangée de mur au-dessus, où le navigateur la peint) ; les fauteuils et le siège du film restent devant."""
    for largeur, hauteur, porte in ((6, 5, 2), (8, 6, 3), (11, 7, 9)):
        piece = enseignes.piece_de_rialto(largeur, hauteur, porte)
        t, plan = piece["toile"], piece["sol"]
        assert t == {"x": 1, "y": 1, "l": largeur, "h": 2}, t
        for y in (1, 2):
            assert plan[y][1:-1] == "]" * largeur, plan
        assert plan[piece["siege"]["y"]][piece["siege"]["x"]] not in "]", plan


def test_le_billet_du_rialto_dit_le_film_du_soir(une_soiree_au_rialto):
    r = une_soiree_au_rialto["billets"]
    assert len({titre for _, titre in r}) == 3, r
    for libelle, titre in r:
        assert libelle == "UN BILLET — " + titre, r
