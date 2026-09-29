"""Les boulots, sous Node : taxi, pizza, ambulance, remorquage, fourrière, et la
sirène qui n'appelle pas un nouveau contrat.

Découpé de `test_moteur_js.py` (vague D, 29 sept. 2026) : même banc, mêmes juges.
"""


def test_le_taxi_paie_la_course_selon_la_douceur(banc, paquet):
    boulot = paquet["economie"]["boulots"]["taxi"]
    civil = next(p for p in paquet["personnages"] if p["slug"] == "civil")
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        L.graine(47);
        const j = L.B.joueur, d = o.ligneDroite();
        j.x = d.x; j.y = d.y;
        const v = o.char('taxi', 0, 0, 0);
        L.Vehicules.monter(j, v);
        const argent0 = L.B.partie.argent;
        o.tape('Space', 2);                              // klaxon : un client
        const t = L.Missions.boulot;
        const etape1 = t.etape, client = t.client;
        const hele = client && client.bulle ? client.bulle.texte : null;
        if (client) { v.x = client.x + 10; v.y = client.y; j.x = v.x; j.y = v.y; v.vitesse = 0; }
        o.frame(3);
        const etape2 = t.etape, dest = t.destination;
        if (dest) { v.x = dest.x + 6; v.y = dest.y; j.x = v.x; j.y = v.y; v.vitesse = 0; }
        o.frame(3);
        return { etape1: etape1, etape2: etape2, etape3: t.etape, hele: hele,
                 gain: L.B.partie.argent - argent0, courses: t.faits.taxi };
    }""")
    assert r["etape1"] == "ramasse" and r["etape2"] == "route" and r["etape3"] is None
    assert r["hele"] == civil["heler"], \
        "un client qui attend un taxi sans rien dire est un passant de plus (bulle du « civil »)"
    assert r["courses"] == 1
    assert r["gain"] >= boulot["base"] + boulot["prime"], \
        "une course sans un choc doit donner le pourboire plein"


def test_le_taxi_n_envoie_personne_ou_un_char_ne_va_pas(banc):
    """⚠️ Rouge avant (17 sept. 2026) : depuis l'ile, la chapelle Sainte-Anne est
    un point de la carte comme un autre, et le taxi (la pizza aussi) l'y tirait
    au sort — on ne l'atteint qu'a la nage. La regle est ce dont la course a
    besoin, une route depuis le char : la route est donc ecrite ICI, pas relue
    dans `missions.js`."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const B = L.B, M = L.Monde, TT = L.TT, W = M.carte.w, H = M.carte.h;
        const g = L.Histoire.lieu('garage');
        let depart = null;
        for (let r = 0; r <= 4 && !depart; r++) for (let dy = -r; dy <= r && !depart; dy++) for (let dx = -r; dx <= r; dx++) {
            const tx = Math.floor(g.x / TT) + dx, ty = Math.floor(g.y / TT) + dy;
            if (!M.bloque(tx, ty, M.MASQUE_VEHICULE) && !M.estEau(tx, ty)) { depart = { x: tx * TT + 8, y: ty * TT + 8 }; break; }
        }
        const vus = new Uint8Array(W * H), file = [];
        const s0 = Math.floor(depart.y / TT) * W + Math.floor(depart.x / TT);
        vus[s0] = 1; file.push(s0);
        for (let i = 0; i < file.length; i++) {
            const k = file[i], x = k % W, y = (k - x) / W;
            [[1, 0], [-1, 0], [0, 1], [0, -1]].forEach(function (d) {
                const nx = x + d[0], ny = y + d[1], nk = ny * W + nx;
                if (nx < 0 || ny < 0 || nx >= W || ny >= H || vus[nk]) return;
                if (M.bloque(nx, ny, M.MASQUE_VEHICULE) || M.estEau(nx, ny)) return;
                vus[nk] = 1; file.push(nk);
            });
        }
        function enChar(px, py) {
            for (let y = Math.floor(py / TT) - 3; y <= Math.floor(py / TT) + 3; y++) {
                for (let x = Math.floor(px / TT) - 3; x <= Math.floor(px / TT) + 3; x++) {
                    if (x >= 0 && y >= 0 && x < W && y < H && vus[y * W + x] && Math.hypot(x * TT + 8 - px, y * TT + 8 - py) < 44) return true;
                }
            }
            return false;
        }
        const coupes = M.carte.points.filter(function (p) { return !enChar(p.x * TT + 8, p.y * TT + 8); }).map(function (p) { return p.slug; });
        const v = L.Vehicules.creer('taxi', depart.x, depart.y, 0, { etat: 'stationne' });
        const tires = {};
        let horsRoute = 0;
        for (let i = 0; i < 300; i++) {
            L.Missions.boulot.slug = 'taxi';
            L.Missions.boulot.enRoute(v);
            const d = L.Missions.boulot.destination;
            tires[d.nom] = (tires[d.nom] || 0) + 1;
            if (!enChar(d.x, d.y)) horsRoute++;
        }
        L.Missions.boulot.fin();
        return { coupes: coupes, tires: tires, horsRoute: horsRoute };
    }""")
    assert r["coupes"], "aucun point de la carte n'est coupe de la route : ce juge ne mord plus sur rien"
    assert r["horsRoute"] == 0, f"{r['horsRoute']} courses sur 300 vers un lieu sans route ({r['coupes']}) : {r['tires']}"
    assert len(r["tires"]) >= 10, f"le taxi ne va plus que dans {len(r['tires'])} lieux : {r['tires']}"


def test_la_pizza_se_livre_trois_fois_et_refroidit(banc, paquet):
    """⚠️ `Missions.taxi` etait le SEUL boulot : les trois autres etaient dans
    `economie.BOULOTS`, dans le paquet, avec leurs juges Python — et le klaxon
    d'une moto ne faisait rien. Une fiche de plus que le navigateur ne lisait
    pas, comme `cercles` et `defonce` avant elle.

    La pizza a ce que le taxi n'a pas : TROIS etapes de suite, et une prime qui
    FOND toute seule. Le juge tient les deux — et la distance doit se payer a
    chaque etape, sinon trois livraisons rapporteraient trois fois le premier
    trajet."""
    f = paquet["economie"]["boulots"]["pizza"]
    r = banc("""function (L, o) {
        L.Jeu.commencer(); L.B.partie.jour = 21;  // ⚠️ EN JUILLET : l'hiver, motos et vélos sont remisés (test_motos_velos_remises_js.py)
        L.graine(51);
        const j = L.B.joueur, d = o.ligneDroite();
        j.x = d.x; j.y = d.y;
        const v = o.char('moto', 0, 0, 0);
        L.Vehicules.monter(j, v);
        const b = L.Missions.boulot;
        const argent0 = L.B.partie.argent;
        o.tape('Space', 2);                              // klaxon : on part charge
        // ⚠️ Pas de ramassage : la pizza part tout de suite en route.
        const depart = { slug: b.slug, etape: b.etape, client: !!b.client };
        const etapes = [], primesChaudes = [];
        for (let i = 0; i < 5 && b.etape; i++) {
            const dest = b.destination;
            v.x = dest.x + 6; v.y = dest.y; j.x = v.x; j.y = v.y; v.vitesse = 0;
            primesChaudes.push(b.prime(v));
            o.frame(3);
            etapes.push({ faites: b.etapesFaites, encore: !!b.etape });
        }
        const chaud = L.B.partie.argent - argent0;
        // Et LA MEME TOURNEE, mais froide : on laisse le chrono s'ecouler.
        // ⚠️ La graine ET le point de depart reviennent a l'identique : sans
        // ca, la deuxieme tournee tire d'AUTRES clients (ils se choisissent
        // autour de la moto, et elle a fini la premiere tournee a l'autre bout
        // de la ville). On comparait deux trajets differents — une livraison
        // froide au loin paie plus qu'une chaude a cote, et le juge disait le
        // contraire de ce qu'il voulait dire.
        L.graine(51);
        v.x = d.x; v.y = d.y; j.x = d.x; j.y = d.y; v.vitesse = 0;
        L.B.partie.argent = argent0;
        o.tape('Space', 2);
        let froid = 0;
        const primesFroides = [];
        for (let i = 0; i < 5 && b.etape; i++) {
            o.frame(%d);                                  // la pizza refroidit
            const dest = b.destination;
            v.x = dest.x + 6; v.y = dest.y; j.x = v.x; j.y = v.y; v.vitesse = 0;
            primesFroides.push(b.prime(v));
            o.frame(3);
        }
        froid = L.B.partie.argent - argent0;
        return { depart: depart, etapes: etapes, chaud: chaud, froid: froid,
                 primesChaudes: primesChaudes, primesFroides: primesFroides,
                 faits: b.faits.pizza, taxis: b.faits.taxi };
    }""" % (f["chrono_s"] * 60 + 10))
    assert r["depart"] == {"slug": "pizza", "etape": "route", "client": False}, (
        "on part avec les boites : pas d'etape de ramassage (%s)" % r["depart"]
    )
    assert [e["faites"] for e in r["etapes"]] == [1, 2, 3], (
        "la pizza se livre %s fois au lieu de 3 : %s" % (f["etapes"], r["etapes"])
    )
    assert r["etapes"][-1]["encore"] is False, "le boulot ne se termine pas"
    # ⚠️ Deux boulots joues (chaud puis froid) : le compteur les compte tous
    # les deux, et AUCUN ne tombe dans celui du taxi.
    assert r["faits"] == 2 and r["taxis"] == 0, (
        "une pizza livree n'est pas une course de taxi : %s" % r
    )
    # ⚠️ La distance se paie A CHAQUE etape, donc trois trajets valent plus que
    # trois fois la base seule.
    assert r["chaud"] >= (f["base"] + f["prime"]) * f["etapes"], (
        "trois livraisons chaudes rapportent %s, moins que %s" % (r["chaud"], (f["base"] + f["prime"]) * f["etapes"])
    )
    # ⚠️ ON COMPARE LES PRIMES, PAS LES DEUX TOTAUX. Les clients se tirent au
    # sort autour de la moto : la tournee froide n'est PAS la tournee chaude, et
    # trois livraisons froides a l'autre bout de la ville paient plus, en
    # distance, que trois chaudes a cote — le juge disait alors le contraire de
    # ce qu'il voulait dire. La prime, elle, ne depend que du chrono : elle est
    # entiere tant que la pizza est chaude, nulle quand elle est froide, et
    # comme les deux livraisons paient la meme distance, c'est bien elle qui
    # fait qu'a trajet egal une pizza froide rapporte moins.
    assert all(prime > 0 for prime in r["primesChaudes"]), (
        "la pizza chaude ne paie aucune prime : %s" % r["primesChaudes"]
    )
    assert r["primesChaudes"][0] <= f["prime"], "la prime depasse la fiche"
    assert r["primesFroides"] == [0] * f["etapes"], (
        "une pizza froide garde sa prime : %s" % r["primesFroides"]
    )
    assert r["froid"] >= f["base"] * f["etapes"], "froide, il reste quand meme la base"


def test_l_ambulance_ramasse_un_blesse_et_le_perd_si_on_traine(banc, paquet):
    """⚠️ « Un blesse quelque part, chrono, le sortir vivant. » La prime EST sa
    vie : passe le chrono, il ne se releve pas, et il ne reste que la base.

    Le juge fait les deux trajets — a temps et trop tard — et verifie au
    passage que la destination n'est pas tiree au hasard comme celle du taxi :
    un blesse va A L'HOPITAL, pas au Bar Le Brouillard."""
    f = paquet["economie"]["boulots"]["ambulance"]
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        L.graine(53);
        const j = L.B.joueur, d = o.ligneDroite();
        j.x = d.x; j.y = d.y;
        const v = o.char('ambulance', 0, 0, 0);
        L.Vehicules.monter(j, v);
        const b = L.Missions.boulot;
        function course(attente) {
            const argent0 = L.B.partie.argent;
            // ⚠️ On repart sirene ETEINTE : dans une ambulance, c'est
            // l'allumage qui prend l'appel, jamais l'extinction (voir
            // `test_eteindre_sa_sirene_n_appelle_pas_un_nouveau_contrat`).
            v.sirene = false;
            o.tape('Space', 2);
            const etape1 = b.etape;
            const blesse = b.client;
            const aTerre = blesse ? blesse.etat : null;
            const part = blesse ? blesse.vie / blesse.vieMax : null;
            if (blesse) { v.x = blesse.x + 10; v.y = blesse.y; j.x = v.x; j.y = v.y; v.vitesse = 0; }
            o.frame(3);
            const dest = b.destination;
            if (attente) o.frame(attente);
            if (dest) { v.x = dest.x + 6; v.y = dest.y; j.x = v.x; j.y = v.y; v.vitesse = 0; }
            o.frame(3);
            return { etape1: etape1, aTerre: aTerre, part: part, dest: dest && dest.nom,
                     gain: L.B.partie.argent - argent0, fini: b.etape };
        }
        const aTemps = course(0);
        const tropTard = course(%d);
        return { aTemps: aTemps, tropTard: tropTard, faits: b.faits.ambulance,
                 hopital: (L.Monde.carte.points.find(function (p) { return p.slug === 'hopital'; }) || {}).nom };
    }""" % (f["chrono_s"] * 60 + 10))
    a, t = r["aTemps"], r["tropTard"]
    assert a["etape1"] == "ramasse", "l'ambulance doit aller CHERCHER quelqu'un"
    assert a["aTerre"] == "assomme", "le blesse doit etre a terre, pas debout a heler"
    assert a["part"] is not None and a["part"] < 0.3, "un blesse a pleine vie n'est pas un blesse"
    assert a["dest"] == r["hopital"], "un blesse va a l'hopital, pas au hasard : %s" % a["dest"]
    assert a["gain"] >= f["base"] + f["prime"], "le transport a temps doit donner la prime pleine"
    assert t["gain"] < a["gain"], "arriver trop tard paie autant qu'arriver a temps"
    assert t["gain"] >= f["base"], "il reste la base, meme trop tard"
    assert r["faits"] == 2 and a["fini"] is None


def test_la_fourriere_saisit_le_char_et_le_revend_plus_cher_qu_il_ne_vaut(banc, paquet):
    """⚠️ La fourrière existait **en Python** depuis M9 — une cour clôturée avec
    sa guérite, 40 cases, `economie.FOURRIERE` et son juge d'équilibrage — et
    le navigateur n'en savait rien : le comptoir « LE LOT » avait un libellé et
    aucun menu, et rien n'y amenait jamais un char.

    Trois règles, et la troisième est celle qui compte :

    1. on te prend le char que tu **conduisais** — ⚠️ pas celui où tu es, car
       la police t'en **sort** avant de t'embarquer, donc `dansVehicule` est
       déjà nul à l'arrestation ;
    2. il attend **dans la cour**, sur une case du lot ;
    3. le racheter coûte **plus cher que de le revendre** au garage. Sinon on
       se fait saisir un char exprès pour le racheter moins cher qu'il ne se
       revend, et la fourrière devient une machine à argent.
    """
    f = paquet["economie"]["fourriere"]
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        L.graine(67);
        const j = L.B.joueur, p = L.B.partie;
        const d = o.ligneDroite();
        j.x = d.x; j.y = d.y;
        // On conduit une berline, PUIS on en descend : c'est l'etat exact dans
        // lequel la police nous laisse avant de nous embarquer.
        const v = o.char('auto', 0, 0, 0);
        L.Vehicules.monter(j, v);
        L.Vehicules.descendre(j, true);
        const avant = { dedans: !!j.dansVehicule, dernier: j.dernierVehicule === v,
                        saisissable: L.Missions.charSaisissable(j) === v };
        p.argent = 5000;
        L.B.recherche.etoiles = 2;
        L.Missions.prison(null);
        o.fondu();
        const apres = { lot: p.fourriere.length, slug: p.fourriere[0] && p.fourriere[0].slug,
                        disparu: L.B.entites.indexOf(v) < 0 };
        // ⚠️ Le lot deborde : il garde `places` chars, le plus vieux part.
        for (let i = 0; i < %d; i++) p.fourriere.push({ slug: 'taxi', couleur: '#f1c40f', vie: 90, vole: true });
        const v2 = o.char('moto', 0, 0, 0);
        L.Vehicules.monter(j, v2); L.Vehicules.descendre(j, true);
        L.Missions.saisir(v2);
        const plein = { n: p.fourriere.length, dernier: p.fourriere[p.fourriere.length - 1].slug,
                        premier: p.fourriere[0].slug };
        // Le comptoir : on rachete la moto.
        p.fourriere.length = 0;
        p.fourriere.push({ slug: 'moto', couleur: '#1a1a1a', vie: 30, vole: true });
        const menu = L.Missions.menuFourriere([]);
        const argent0 = p.argent;
        const achete = menu.items[0].faire();
        const rachat = { titre: menu.titre, achete: achete, reste: p.fourriere.length,
                         paye: argent0 - p.argent, prix: L.Missions.prixRachat('moto') };
        // Vide, le comptoir le dit au lieu de se taire.
        const vide = L.Missions.menuFourriere([]);
        // Et les chars saisis se posent dans la COUR au demarrage.
        p.fourriere.push({ slug: 'auto', couleur: '#c0392b', vie: 80, vole: true });
        const poses = L.Missions.garnirLaFourriere();
        const lot = L.Monde.carte.fourriere;
        const dansLaCour = L.B.entites.filter(function (e) {
            return e.type === 'vehicule' && e.saisi !== null && e.saisi !== undefined
                && e.x / L.TT >= lot.x && e.x / L.TT < lot.x + lot.largeur
                && e.y / L.TT >= lot.y && e.y / L.TT < lot.y + lot.hauteur;
        }).length;
        return { avant: avant, apres: apres, plein: plein, rachat: rachat,
                 vide: vide.items[0].libelle, poses: poses, dansLaCour: dansLaCour,
                 places: lot.places.length };
    }""" % (f["places"] + 3))
    assert r["avant"] == {"dedans": False, "dernier": True, "saisissable": True}, (
        "a l'arrestation on est DEHORS : c'est le dernier char conduit qu'on saisit (%s)" % r["avant"]
    )
    assert r["apres"]["lot"] == 1 and r["apres"]["slug"] == "auto", "l'arrestation n'a rien saisi"
    assert r["apres"]["disparu"] is True, "le char saisi est reste dans la rue"
    assert r["plein"]["n"] == f["places"], "le lot garde %s chars, pas %s" % (f["places"], r["plein"]["n"])
    assert r["plein"]["dernier"] == "moto", "le dernier saisi n'est pas au bout"
    assert r["plein"]["premier"] == "taxi", "c'est le plus VIEUX qui doit partir"
    # ⚠️ `faire` rend `false` : le comptoir RESTE ouvert (Martin, 22 sept. 2026).
    # Le rachat se juge a ce qu'il fait — le lot vide, l'argent parti.
    assert r["rachat"]["achete"] is False and r["rachat"]["reste"] == 0
    assert r["rachat"]["paye"] == r["rachat"]["prix"] > 0
    assert r["vide"] == "LE LOT EST VIDE", "un lot vide doit le dire, pas se taire"
    assert r["poses"] == 1 and r["dansLaCour"] == 1, (
        "un char saisi doit attendre DANS LA COUR : %s posé(s), %s dedans" % (r["poses"], r["dansLaCour"])
    )
    # ⚠️ LA regle — racheter coute plus cher que revendre — se juge en Python, sur
    # tout le catalogue : `test_economie::test_la_fourriere_ne_peut_pas_devenir_une_machine_a_argent`.


def test_mal_gare_veut_dire_quelque_chose_et_la_fourriere_passe(banc, paquet):
    """⚠️ La fourrière promet depuis M9 qu'un char mal garé part au lot, et
    **la règle n'existait nulle part**. Depuis que les stationnements ont de
    vraies **cases**, la définition tombe toute seule et se teste : est mal
    garé un char **laissé hors d'une case ET qui gêne** — la chaussée (où
    personne ne s'arrête), un passage piéton (où les gens traversent), le
    devant d'une porte (où les gens sortent).

    Le juge tient les deux moitiés, et la seconde compte autant : un char dans
    sa case, sur une ruelle ou sur du stationnement ne se fait **jamais**
    remorquer — même mal aligné, même depuis trois jours. ⚠️ Et jamais celui de
    la planque : c'est la sauvegarde de Martin."""
    delai = paquet["economie"]["fourriere"]["remorquage_s"]
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        L.graine(83);
        const j = L.B.joueur, p = L.B.partie, c = L.Monde.carte;
        p.fourriere.length = 0;
        const out = {};

        /* Pose un char au centre d'une tuile choisie par un test, et dit s'il
           est mal gare. On le retire ensuite : un juge ne salit pas la ville. */
        function surUneTuile(choisir, slug) {
            for (let ty = 4; ty < c.h - 4; ty++) {
                for (let tx = 4; tx < c.w - 4; tx++) {
                    if (!choisir(tx, ty)) continue;
                    const v = L.Vehicules.creer(slug || 'auto', tx * L.TT + 8, ty * L.TT + 8, 0, { etat: 'stationne' });
                    if (!v) continue;
                    const mal = L.Missions.malGare(v);
                    L.Entites.retirer(v);
                    return { tx: tx, ty: ty, mal: mal, glyphe: L.Monde.glyphe(tx, ty) };
                }
            }
            return null;
        }
        // ⚠️ Des tuiles ENTOUREES de leur sorte : une auto fait 28 px, elle
        // deborde sur ses voisines, et on veut juger la tuile qu'on vise.
        function entouree(test) {
            return function (tx, ty) {
                for (let dy = -1; dy <= 1; dy++) for (let dx = -1; dx <= 1; dx++) {
                    if (!test(tx + dx, ty + dy)) return false;
                }
                return true;
            };
        }
        const M = L.Monde;
        out.chaussee = surUneTuile(entouree(function (x, y) { return M.estChaussee(x, y); }));
        out.case = surUneTuile(entouree(function (x, y) { return '^v<>'.indexOf(M.glyphe(x, y)) >= 0; }));
        // ⚠️ Un VELO pour la ruelle : elle fait deux tuiles de large, et une
        // berline de 28 px y deborde toujours sur autre chose.
        out.ruelle = surUneTuile(function (tx, ty) { return M.glyphe(tx, ty) === 'x'; }, 'velo');
        out.passage = surUneTuile(function (tx, ty) { return M.estPassage(tx, ty); });

        // Le chrono : un char LAISSE sur la chaussee part au lot, pas avant.
        // ⚠️ Le joueur se poste a cote : hors de sa bulle, `peupler()` oublie
        // le char, et on mesurerait un oubli en croyant mesurer un remorquage.
        const ch = out.chaussee;
        j.x = ch.tx * L.TT + 8; j.y = ch.ty * L.TT + 8;
        L.Monde.centrerCamera(j.x, j.y);
        const v = L.Vehicules.creer('auto', ch.tx * L.TT + 8, ch.ty * L.TT + 8, 0, { etat: 'stationne' });
        L.Entites.indexer();
        // ⚠️ Court, et sur un char NEUF ensuite : le joueur est plante au milieu
        // de la chaussee, et le trafic finit par demolir ce qui traine la — on
        // mesurerait une epave en croyant mesurer un remorquage.
        out.sansLaisser = { avant: p.fourriere.length };
        for (let i = 0; i < 10 * 60; i++) o.frame(1);
        out.sansLaisser.apres = p.fourriere.length;      // jamais conduit : on n'y touche pas
        L.Entites.retirer(v);
        // ⚠️ On coupe le trafic pour la phase chronometree : le joueur est
        // plante au milieu de la chaussee, et une berline laissee la se fait
        // demolir en dix secondes. On mesurerait une epave en croyant mesurer
        // un remorquage.
        L.B.defs.conduite.trafic.vehicules_max = 0;
        L.B.entites = L.B.entites.filter(function (e) { return e.type !== 'vehicule' || e.conducteur !== 'trafic'; });
        const w = L.Vehicules.creer('auto', ch.tx * L.TT + 8, ch.ty * L.TT + 8, 0, { etat: 'stationne' });
        L.Entites.indexer();
        w.laisse = true;
        let images = 0;
        while (L.B.entites.indexOf(w) >= 0 && images < (%d + 20) * 60) { o.frame(1); images++; }
        out.remorque = { secondes: Math.round(images / 60), lot: p.fourriere.length,
                         slug: p.fourriere.length ? p.fourriere[p.fourriere.length - 1].slug : null };
        // Et celui de la planque, JAMAIS — meme pose en pleine chaussee.
        // ⚠️ On mesure la REGLE, pas cinquante secondes : l'exemption se juge
        // contre `p.planque.vehicule`, que `sauvegarderPartie()` recalcule
        // toutes les dix secondes depuis la porte de la planque. Laisser
        // tourner testerait la sauvegarde, pas la fourriere.
        const garde = { slug: 'auto', couleur: '#c0392b', vie: 90,
                        x: ch.tx * L.TT + 8, y: ch.ty * L.TT + 8, angle: 0, vole: false };
        p.planque.vehicule = garde;
        const sien = L.Vehicules.creer('auto', garde.x, garde.y, 0, { etat: 'stationne' });
        sien.laisse = true;
        L.Entites.indexer();
        // Le MEME endroit, le meme etat : seul le lien avec la planque change.
        p.planque.vehicule = null;
        const sansPlanque = L.Missions.malGare(sien);
        p.planque.vehicule = garde;
        out.planque = { malGare: L.Missions.malGare(sien), sansPlanque: sansPlanque };
        return out;
    }""" % delai)
    assert r["chaussee"] and r["chaussee"]["mal"] is True, (
        "un char en pleine chaussée n'est pas mal garé ? %s" % r["chaussee"]
    )
    assert r["case"] and r["case"]["mal"] is False, (
        "un char DANS SA CASE ne se fait jamais remorquer : %s" % r["case"]
    )
    assert r["ruelle"] and r["ruelle"]["mal"] is False, (
        "un char rangé sur une ruelle ne gêne personne : %s" % r["ruelle"]
    )
    assert r["passage"] and r["passage"]["mal"] is True, (
        "un char sur un passage piéton doit être mal garé : %s" % r["passage"]
    )
    # ⚠️ Le trafic ne se fait PAS remorquer : seulement ce que le joueur laisse.
    assert r["sansLaisser"]["apres"] == r["sansLaisser"]["avant"] == 0, (
        "un char que le joueur n'a jamais conduit a été remorqué : %s" % r["sansLaisser"]
    )
    assert r["remorque"]["lot"] == 1 and r["remorque"]["slug"] == "auto", (
        "le char mal garé n'est pas parti au lot : %s" % r["remorque"]
    )
    assert abs(r["remorque"]["secondes"] - delai) <= 3, (
        "la remorqueuse passe après %s s au lieu de %s" % (r["remorque"]["secondes"], delai)
    )
    # ⚠️ Le MEME char, au MEME endroit : mal garé s'il n'est à personne, jamais
    # s'il est celui de la planque. C'est la sauvegarde de Martin.
    assert r["planque"] == {"malGare": False, "sansPlanque": True}, (
        "le char de la planque n'est pas protégé (ou l'exemption protège tout) : %s" % r["planque"]
    )


def test_la_fourriere_paie_les_epaves_qu_on_lui_amene_au_crochet(banc, paquet):
    """⚠️ Le remorquage attendait la fourrière ; il l'a. C'est le seul boulot où
    ce qu'on ramasse n'est pas une personne mais ce qu'on a **au crochet** : le
    bouton du klaxon accroche d'abord (`Vehicules.basculerCrochet`), puis
    appelle le boulot — une seule pression, l'épave est accrochée et le
    contrat est pris.

    Trois règles : la fourrière ne paie **que les épaves** (traîner une berline
    saine au lot, c'est du vol) ; on livre **dans la cour**, pas à 44 px d'un
    point (la grille fait quatre tuiles et la remorqueuse 36 px) ; et une épave
    qui décroche en route, c'est le contrat qui tombe."""
    f = paquet["economie"]["boulots"]["remorquage"]
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        L.graine(71);
        const j = L.B.joueur, p = L.B.partie, d = o.ligneDroite();
        j.x = d.x; j.y = d.y;
        const rem = o.char('remorqueuse', 0, 0, 0);          // cap 0 : l'arriere est a l'ouest
        L.Vehicules.monter(j, rem);
        const b = L.Missions.boulot, lot = L.Monde.carte.fourriere;
        const out = {};
        // 1. Une berline SAINE au crochet : pas de contrat, et on le dit.
        const saine = o.char('auto', -36, 0, 0);
        L.Entites.indexer();
        o.tape('Space', 2);
        out.saine = { accrochee: rem.remorque === saine, boulot: b.slug, msg: L.B.msg };
        o.tape('Space', 2);                                   // on decroche
        L.Entites.retirer(saine);
        // 2. Une epave : accrochee ET contrat, en une pression.
        const epave = o.char('auto', -36, 0, 0);
        L.Entites.indexer();
        L.Vehicules.endommager(epave, 9999, null);
        o.frame(2);
        o.tape('Space', 2);
        out.epave = { accrochee: rem.remorque === epave, etatEpave: epave.etat, boulot: b.slug, etape: b.etape,
                      dest: b.destination && b.destination.nom };
        // 3. On decroche en route : le contrat tombe.
        o.tape('Space', 2);
        o.frame(2);
        out.lache = { boulot: b.slug, etape: b.etape, msg: L.B.msg };
        // 4. On raccroche, et on livre DANS LA COUR : paye, l'epave part a la ferraille.
        L.Entites.indexer();
        o.tape('Space', 2);
        const argent0 = p.argent, distance = b.distance;
        const cx = (lot.x + lot.largeur / 2) * L.TT, cy = (lot.y + lot.hauteur / 2) * L.TT;
        rem.x = cx; rem.y = cy; j.x = cx; j.y = cy; rem.vitesse = 0; rem.vx = 0; rem.vy = 0;
        epave.x = cx - 40; epave.y = cy;                       // toujours au bout du cable
        o.frame(4);
        out.livre = { gain: p.argent - argent0, etape: b.etape, epaveDisparue: L.B.entites.indexOf(epave) < 0,
                      decroche: !rem.remorque, faits: b.faits.remorquage,
                      attendu: Math.round(%d + %f * (distance / L.TT)) };
        return out;
    }""" % (f["base"], f["par_tuile"]))
    assert r["saine"]["accrochee"] is True and r["saine"]["boulot"] is None, (
        "une berline saine ne doit PAS lancer de remorquage : %s" % r["saine"]
    )
    assert "ÉPAVES" in (r["saine"]["msg"] or ""), "le refus doit se dire : %s" % r["saine"]["msg"]
    assert r["epave"]["etatEpave"] == "epave" and r["epave"]["accrochee"] is True
    assert r["epave"]["boulot"] == "remorquage" and r["epave"]["etape"] == "route", (
        "une epave au crochet doit prendre le contrat en une pression : %s" % r["epave"]
    )
    assert "Fourrière" in r["epave"]["dest"], "le remorquage va A LA FOURRIERE : %s" % r["epave"]["dest"]
    assert r["lache"]["boulot"] is None and r["lache"]["etape"] is None, (
        "decrocher en route doit faire tomber le contrat : %s" % r["lache"]
    )
    assert r["livre"]["etape"] is None and r["livre"]["faits"] == 1, "la livraison ne finit pas : %s" % r["livre"]
    assert r["livre"]["gain"] == r["livre"]["attendu"] > 0, (
        "le remorquage paie %s $ au lieu de base + distance = %s $" % (r["livre"]["gain"], r["livre"]["attendu"])
    )
    assert r["livre"]["epaveDisparue"] is True and r["livre"]["decroche"] is True, (
        "l'epave livree doit partir a la ferraille et le crochet se liberer : %s" % r["livre"]
    )


def test_sortir_son_char_du_lot_sans_payer_appelle_la_police(banc, paquet):
    """⚠️ L'autre moitié de la fourrière : on peut reprendre son char **par-dessus
    la clôture** — à pied on enjambe le grillage, on monte dans son char, on
    sort par la seule grille. Le lot appelle (délit `fourriere`, bruyant : pas
    de témoin à convaincre), les gars du lot **ripostent**, et le char redevient
    volé. Racheté au comptoir, le même trajet ne coûte rien."""
    f = paquet["economie"]["fourriere"]
    etoiles = paquet["recherche"]["delits"]["fourriere"]["etoiles"]
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        L.graine(73);
        const j = L.B.joueur, p = L.B.partie, lot = L.Monde.carte.fourriere;
        p.fourriere.length = 0;
        p.fourriere.push({ slug: 'auto', couleur: '#c0392b', vie: 80, vole: true });
        p.fourriere.push({ slug: 'moto', couleur: '#1a1a1a', vie: 30, vole: true });
        L.Missions.garnirLaFourriere();
        L.Entites.indexer();
        const gardiens = L.B.entites.filter(function (e) { return e.type === 'pieton' && e.gardien; });
        const saisis = L.B.entites.filter(function (e) { return e.type === 'vehicule' && e.saisi !== null && e.saisi !== undefined; });
        const auto = saisis.find(function (v) { return v.slug === 'auto'; });
        const moto = saisis.find(function (v) { return v.slug === 'moto'; });
        const out = { gardiens: gardiens.length, saisis: saisis.length,
                      postes: gardiens.map(function (g) { return { etat: g.etat, y: Math.round(g.y / L.TT) - lot.grille.y }; }) };
        // 1. On enjambe (on se teleporte : la cloture a son propre juge), on
        //    monte, on sort par la grille.
        j.x = auto.x; j.y = auto.y + 20;
        L.Vehicules.monter(j, auto);
        const crimes0 = L.B.crimes.length;
        auto.x = (lot.grille.x + 2) * L.TT; auto.y = (lot.grille.y + 3) * L.TT;   // dehors, devant la grille
        j.x = auto.x; j.y = auto.y;
        o.frame(2);
        out.sortie = { crime: L.B.crimes.slice(crimes0).map(function (c) { return c.type; }),
                       etoiles: L.B.recherche.etoiles, lot: p.fourriere.map(function (c) { return c.slug; }),
                       saisi: auto.saisi, vole: auto.vole,
                       ripostent: gardiens.filter(function (g) { return g.etat === 'attaque_joueur'; }).length,
                       motoRang: moto.saisi };
        L.Vehicules.descendre(j, true);
        // 2. La moto, RACHETEE au comptoir, sort sans un mot.
        const menu = L.Missions.menuFourriere([]);
        p.argent = 9999;
        menu.items[0].faire();
        const crimes1 = L.B.crimes.length;
        j.x = moto.x; j.y = moto.y + 20;
        L.Vehicules.monter(j, moto);
        moto.x = (lot.grille.x + 2) * L.TT; moto.y = (lot.grille.y + 3) * L.TT;
        j.x = moto.x; j.y = moto.y;
        o.frame(2);
        out.rachetee = { crimes: L.B.crimes.length - crimes1, saisi: moto.saisi, vole: moto.vole,
                         lot: p.fourriere.length };
        return out;
    }""")
    assert r["gardiens"] == f["gardiens"], "il manque des gars du lot : %s" % r["gardiens"]
    assert all(g["etat"] == "fige" and abs(g["y"]) <= 1 for g in r["postes"]), (
        "les gardiens tiennent la grille, a une tuile pres : %s" % r["postes"]
    )
    assert r["saisis"] == 2
    s = r["sortie"]
    assert s["crime"] == ["fourriere"], "sortir sans payer doit signaler le delit `fourriere` : %s" % s["crime"]
    assert s["etoiles"] >= etoiles, "le lot appelle : %s etoile(s)" % s["etoiles"]
    assert s["lot"] == ["moto"] and s["saisi"] is None and s["vole"] is True, (
        "le char sorti quitte le lot et redevient vole : %s" % s
    )
    assert s["ripostent"] == r["gardiens"], "les gars du lot ne ripostent pas : %s" % s
    assert s["motoRang"] == 0, "les rangs des autres chars doivent glisser, sinon le comptoir libere le mauvais"
    assert r["rachetee"] == {"crimes": 0, "saisi": None, "vole": False, "lot": 0}, (
        "un char rachete sort sans un mot : %s" % r["rachetee"]
    )


def test_eteindre_sa_sirene_n_appelle_pas_un_nouveau_contrat(banc):
    """⚠️ Retour de Martin : « on ne devrait pas avoir de nouveaux contrats
    quand on arrête la sirène ; et quand un contrat est en cours, on ne peut
    pas en ravoir un autre. »

    Le bouton du klaxon fait deux choses dans une ambulance : il bascule la
    sirène **et** il prend l'appel. Le premier geste est le bon — on répond et
    on part la sirène allumée. ⚠️ Mais l'inverse veut dire « j'ai fini », pas
    « donne-m'en un autre » : éteindre sa sirène en sortant de l'hôpital
    rappelait aussitôt une ambulance, et on repartait sans l'avoir demandé.

    Le juge tient les trois états du bouton : on allume (contrat), on éteint
    (rien), on rallume pendant un contrat (rien de plus)."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        L.graine(61);
        const j = L.B.joueur, d = o.ligneDroite();
        j.x = d.x; j.y = d.y;
        const v = o.char('ambulance', 0, 0, 0);
        L.Vehicules.monter(j, v);
        const b = L.Missions.boulot;
        // 1. On allume : la sirene part, et l'appel se prend.
        o.tape('Space', 2);
        const allume = { sirene: v.sirene, slug: b.slug, etape: b.etape };
        const premier = b.client;
        // 2. On rallume pendant le contrat : rien de plus, et le meme client.
        o.tape('Space', 2);                              // eteint
        o.tape('Space', 2);                              // rallume
        const pendant = { sirene: v.sirene, etape: b.etape, memeClient: b.client === premier };
        // 3. Le contrat se finit, puis on ETEINT : rien ne doit repartir.
        const c = b.client;
        if (c) { v.x = c.x + 10; v.y = c.y; j.x = v.x; j.y = v.y; v.vitesse = 0; }
        o.frame(3);
        const dest = b.destination;
        if (dest) { v.x = dest.x + 6; v.y = dest.y; j.x = v.x; j.y = v.y; v.vitesse = 0; }
        o.frame(3);
        const fini = { etape: b.etape, faits: b.faits.ambulance };
        o.tape('Space', 2);                              // on eteint la sirene
        const apres = { sirene: v.sirene, etape: b.etape, slug: b.slug };
        // 4. Et on peut en reprendre un quand on RALLUME.
        o.tape('Space', 2);
        const repris = { sirene: v.sirene, etape: b.etape };
        return { allume: allume, pendant: pendant, fini: fini, apres: apres, repris: repris };
    }""")
    assert r["allume"] == {"sirene": True, "slug": "ambulance", "etape": "ramasse"}, (
        "allumer la sirene doit prendre l'appel : %s" % r["allume"]
    )
    assert r["pendant"] == {"sirene": True, "etape": "ramasse", "memeClient": True}, (
        "rallumer pendant un contrat en a donne un autre : %s" % r["pendant"]
    )
    assert r["fini"] == {"etape": None, "faits": 1}, "le premier contrat ne s'est pas fini"
    assert r["apres"] == {"sirene": False, "etape": None, "slug": None}, (
        "ETEINDRE la sirene a rappele une ambulance : %s" % r["apres"]
    )
    assert r["repris"] == {"sirene": True, "etape": "ramasse"}, (
        "on ne peut plus reprendre un appel en rallumant : %s" % r["repris"]
    )
