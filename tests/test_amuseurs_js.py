"""Les amuseurs de rue : le numéro, le public, et la musique qui en sort.

⚠️ Retour de Martin, et il a raison sur les trois points : « présentement ils
ne font rien et sont ennuyants ». La fiche « des sortes de gens » promettait un
musicien qui « joue — et **ça s'entend** » ; ce qui a été livré, c'est un corps
avec une guitare dessinée dessus et **zéro note**. Et les deux qui existaient
tenaient l'**image zéro** de leur sprite du début à la fin de la partie :
`imageDe` choisit son image d'après la DISTANCE PARCOURUE, et un corps à
`vitesse: 0` n'en parcourt aucune.

L'attroupement, lui, était une **chance** et pas une règle : il fallait qu'un
passant entre de lui-même dans les 46 pixels. L'ancien juge posait quatre
badauds à la main avant de mesurer — il mesurait donc l'attroupement d'une
foule qu'il avait fabriquée.

⚠️ Ce que ces juges tiennent, c'est le contrat tel que Martin l'a posé : quand
on VOIT un amuseur, il y a entre 3 et 5 personnes autour, il BOUGE, et le
musicien fait SORTIR DES NOTES, plus fort de près que de loin.
"""

import pytest


#: Les quatre métiers qui font un numéro. ⚠️ La liste est ici et pas dans
#: chaque juge : trois d'entre eux la lisent.
AMUSEURS = ("musicien", "amuseur", "jongleur", "echassier")


@pytest.fixture(scope="module")
def spectacle(paquet):
    return paquet["pietons"]["spectacle"]


def test_les_quatre_amuseurs_naissent_au_centre_ville(banc, paquet):
    """⚠️ Demande de Martin : « ils doivent toujours être dans le centre-ville,
    où il y a plus de gens ».

    Ils naissaient PARTOUT : un mime dans une cour à ferraille de La Shop à 3 h
    du matin, devant personne. Le Faubourg est le centre-ville ouvrier
    (`devantures.py` le dit déjà en toutes lettres) et le quartier le plus
    peuplé de la ville."""
    for slug in AMUSEURS:
        arch = next(p for p in paquet["pietons"]["catalogue"] if p["slug"] == slug)
        assert arch["districts"] == ["faubourg"], f"{slug} : {arch['districts']}"
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        L.graine(31);
        const vus = {}, quartiers = {};
        // On promène le joueur dans toute la ville : personne ne doit en
        // trouver ailleurs qu'au centre.
        const c = L.Monde.carte;
        // ⚠️ **LE CENTRE DU FAUBOURG EN PREMIER, et par sa ZONE, pas par une
        // fraction de la carte.** Les cinq fractions promenaient le juge aux
        // quatre coins ; qu'une d'elles tombe dans le centre-ville tenait à la
        // trame, et le 17 sept. 2026 la carte a grandi vers le bas — plus
        // aucune n'y tombait, et le juge a dit « aucun amuseur dans toute la
        // ville » alors qu'ils étaient tous là où on les voulait. On va donc
        // AU centre-ville, puis on fait le tour pour vérifier qu'il n'y en a
        // nulle part ailleurs.
        const zf = (c.zones || []).find(function (q) { return q.slug === 'faubourg'; });
        const places = [[(zf.x + zf.l / 2) * L.TT, (zf.y + zf.h / 2) * L.TT]];
        for (const [fx, fy] of [[0.2, 0.2], [0.8, 0.2], [0.5, 0.5], [0.2, 0.8], [0.85, 0.85]]) {
            places.push([c.pxW * fx, c.pxH * fy]);
        }
        for (const [px, py] of places) {
            L.B.joueur.x = px; L.B.joueur.y = py;
            L.Monde.centrerCamera(L.B.joueur.x, L.B.joueur.y);
            o.frame(400);
            for (const a of L.B.entites) {
                if (a.type !== 'pieton' || !a.vivant) continue;
                if (L.Entites.SPECTACLES.indexOf(a.metier) < 0) continue;
                vus[a.metier] = (vus[a.metier] || 0) + 1;
                const z = L.Monde.zoneA(a.x, a.y);
                const d = z ? z.district : '?';
                quartiers[d] = (quartiers[d] || 0) + 1;
            }
        }
        return { vus: vus, quartiers: quartiers, max: L.B.defs.pietons.spectacle.artistes_max };
    }""")
    assert r["quartiers"], "aucun amuseur dans toute la ville"
    assert set(r["quartiers"]) == {"faubourg"}, (
        "un amuseur hors du centre-ville : %s" % r["quartiers"]
    )


def test_ils_partagent_un_plafond_et_ne_sont_jamais_tous_les_quatre(banc):
    """⚠️ Quatre sortes à deux exemplaires, ce sont huit artistes dans la bulle
    — donc de 24 à 40 spectateurs, pour un budget de foule de 28. Le cercle
    serait resté vide et la rue n'aurait plus eu un seul passant qui passe. Ils
    partagent donc UN plafond, et c'est aussi ce qui les garde rares."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        L.graine(12);
        // ⚠️ **AU CENTRE DU FAUBOURG, pas au terminus** (voir `test_quand_on_le_voit_...`) : un
        // amuseur naît sur une scène HORS CHAMP mais dans la bulle, et au départ de la partie les
        // scènes du terminus sont à l'écran. Ce juge tenait donc à la trame — sur vingt graines de
        // jeu, une seule voyait naître un amuseur, dans la ville d'avant comme dans la nouvelle —
        // et « aucun amuseur n'est jamais né » disait la chance, pas la règle du plafond.
        const zf = (L.Monde.carte.zones || []).find(function (q) { return q.slug === 'faubourg'; });
        L.B.joueur.x = (zf.x + zf.l / 2) * L.TT; L.B.joueur.y = (zf.y + zf.h / 2) * L.TT;
        L.Monde.centrerCamera(L.B.joueur.x, L.B.joueur.y);
        let pire = 0;
        const sortes = {};
        for (let i = 0; i < 2400; i++) {
            o.frame(1);
            let n = 0;
            for (const a of L.B.entites) {
                if (a.type !== 'pieton' || !a.vivant) continue;
                if (L.Entites.SPECTACLES.indexOf(a.metier) < 0) continue;
                n++; sortes[a.metier] = true;
            }
            pire = Math.max(pire, n);
        }
        return { pire: pire, max: L.B.defs.pietons.spectacle.artistes_max,
                 sortes: Object.keys(sortes).sort() };
    }""")
    assert r["pire"] <= r["max"], (
        "%s amuseurs a la fois, le plafond de la fiche est %s" % (r["pire"], r["max"])
    )
    assert r["pire"] >= 1, "aucun amuseur n'est jamais ne"


def test_quand_on_le_voit_il_a_entre_trois_et_cinq_personnes_autour(banc, spectacle):
    """⚠️ LA demande de Martin, mot pour mot : « qu'il y ait toujours entre 3 et
    5 personnes autour ».

    On MARCHE jusqu'à lui, comme un joueur, et on mesure à **chaque image où on
    le voit**. Le contrat porte sur ce qu'on voit : un artiste né hors champ à
    l'autre bout du quartier met quelques secondes à rassembler son monde — les
    badauds traversent la rue à pied, ils ne se matérialisent pas — et personne
    ne regarde ces secondes-là.

    ⚠️ Les deux bornes viennent de la FICHE (`pietons.SPECTACLE`), pas du juge :
    le jour où Martin dit « plutôt 6 », rien ici ne ment.

    ⚠️ **Le contrat vaut pour une rue calme.** Quand la rue prend peur autour
    du numéro — une auto du trafic renverse quelqu'un à côté, un pickpocket se
    fait prendre —, le public se sauve (`reactions.fuite_secondes`) et personne
    n'est recrutable tant qu'il court : c'est voulu. On cesse alors de juger ce
    numéro-là. Mesuré le 16 sept. 2026 (les rixes) : ce juge ne tenait que par
    l'ordre des dés. Sans aucune rixe, la graine 77 tombait déjà (une auto à
    48 px, 591 images seul) ; les rixes tiraient des dés et déplaçaient
    l'accident ailleurs. Resserré, il tient sur sept graines et trois chances
    de rixe."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        L.graine(77);
        // ⚠️ **AU CENTRE DU FAUBOURG, pas au terminus.** Un amuseur naît sur une
        // scène HORS CHAMP mais dans la bulle (`sceneLibre`) : au départ de la
        // partie, les scènes du terminus sont toutes à l'écran — elles ne
        // comptent pas — et les suivantes sont hors de la bulle. Ce juge tenait
        // donc à la trame, et le 17 sept. 2026 elle a bougé : plus un seul
        // amuseur en 2 000 images, alors que la règle n'avait pas changé.
        const zf = (L.Monde.carte.zones || []).find(function (q) { return q.slug === 'faubourg'; });
        L.B.joueur.x = (zf.x + zf.l / 2) * L.TT; L.B.joueur.y = (zf.y + zf.h / 2) * L.TT;
        L.Monde.centrerCamera(L.B.joueur.x, L.B.joueur.y);
        const j = L.B.joueur;
        const releves = [];
        let vues = 0, seuls = 0;
        const rayonPeur = L.B.defs.pietons.reactions.peur_rayon_tuiles * L.TT;
        for (let tour = 0; tour < 3; tour++) {
            let a = null;
            for (let i = 0; i < 600 && !a; i++) {
                o.frame(1);
                a = L.B.entites.find(function (q) {
                    return q.vivant && L.Entites.SPECTACLES.indexOf(q.metier) >= 0; }) || null;
            }
            if (!a) break;
            // ⚠️ LES SECONDES OU IL RASSEMBLE SON MONDE NE SE JUGENT PAS, et c'est
            // ce que dit la docstring depuis le debut : un artiste ne hors champ met
            // quelques secondes a reunir son public. Le juge les jugeait quand meme
            // des que le numero SUIVANT naissait assez pres pour entrer vite a
            // l'ecran — deux badauds assis, le troisieme encore en chemin. Mesure
            // le 17 sept. 2026 : 4 graines sur 40 tombaient ainsi sans rien changer
            // au jeu, et les quarante decors de l'Ile-aux-Corneilles (d'autres
            // numeros d'entite, donc d'autres cadences) en changeaient seulement
            // lesquelles. On juge donc un numero a partir du moment ou son cercle
            // s'est forme une fois ; un cercle qui ne se forme jamais ne donne
            // aucune image vue, et `vues` le dit.
            let rassemble = false;
            const mini = L.B.defs.pietons.spectacle.minimum;
            for (let i = 0; i < 900 && a.vivant; i++) {
                const dx = a.x - j.x, dy = a.y - j.y, n = Math.hypot(dx, dy) || 1;
                if (n > 44) { j.x += dx / n * 0.9; j.y += dy / n * 0.9; L.Monde.centrerCamera(j.x, j.y); }
                // ⚠️ On traverse les rues EN LIGNE DROITE : sans ca, un char du trafic
                // renverse le joueur, qui se reveille a l'hopital a l'autre bout de la
                // ville — et le juge mesure l'hopital, pas le spectacle.
                j.invincible = 60;
                o.frame(1);
                // ⚠️ LA RUE A EU PEUR : son public s'est sauvé, et c'est voulu.
                if (L.Entites.pietonsAutour(a.x, a.y, rayonPeur).some(function (q) {
                    return q.vivant && (q.etat === 'fuit' || q.etat === 'temoin'); })) break;
                if (!L.Entites.visibleAEcran(a.x, a.y, 0)) continue;
                const cercle = L.Entites.badauds(a).length;
                if (cercle >= mini) rassemble = true;
                if (!rassemble) continue;
                vues++;
                releves.push({ metier: a.metier, n: cercle });
                if (cercle === 0) seuls++;
            }
            L.Entites.retirer(a);
        }
        const ns = releves.map(function (x) { return x.n; });
        return { vues: vues, seuls: seuls,
                 plusPetit: ns.length ? Math.min.apply(null, ns) : null,
                 plusGrand: ns.length ? Math.max.apply(null, ns) : null,
                 metiers: Array.from(new Set(releves.map(function (x) { return x.metier; }))).sort() };
    }""")
    assert r["vues"] > 500, "le juge n'a presque jamais vu d'amuseur a l'ecran : %s" % r["vues"]
    assert r["seuls"] == 0, "un amuseur a joué devant personne pendant %s images" % r["seuls"]
    assert r["plusPetit"] >= spectacle["minimum"], (
        "vu avec %s personne(s) autour, la fiche en demande %s"
        % (r["plusPetit"], spectacle["minimum"])
    )
    assert r["plusGrand"] <= spectacle["maximum"], (
        "vu avec %s personnes autour : au-delà de %s on ne voit plus le numéro"
        % (r["plusGrand"], spectacle["maximum"])
    )


def test_chacun_des_quatre_fait_un_numero_qui_bouge(banc, spectacle):
    """⚠️ « Présentement ils ne font rien. » Un corps à `vitesse: 0` ne parcourt
    aucune distance, `imageDe` choisit son image d'après la distance parcourue,
    et les deux amuseurs livrés tenaient donc **l'image zéro** du début à la fin
    de la partie. Une seule image, ce n'est pas un numéro, c'est un mannequin.

    On les pose tous les quatre à la main ici — ce juge-là ne mesure pas la
    naissance, il mesure le GESTE."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        L.graine(5);
        const out = {};
        for (const slug of %s) {
            const a = L.Entites.archetype(slug);
            const e = L.Entites.creerPieton(L.B.joueur.x + 40, L.B.joueur.y, a);
            e.etat = 'fige'; e.plante = { x: e.x, y: e.y };
            L.Entites.indexer();
            const images = new Set(), poses = new Set();
            for (let i = 0; i < 600; i++) {
                o.frame(1);
                // ⚠️ **ON LE TIENT SUR SA SCENE.** Ce juge mesure le GESTE, et
                // il le disait deja — mais il le mesurait dans une ville
                // vivante : il a suffi qu'un camion tombe en panne au bout de
                // la rue pour que le jongleur devienne TEMOIN, s'en aille, et
                // ne montre plus que deux dessins. Un amuseur qui regarde un
                // accident ne joue pas ; ce n'est pas son numero qu'on
                // mesurait alors, c'est le hasard de la rue.
                e.etat = 'fige'; e.plante = { x: e.x, y: e.y };
                images.add(e.poseFixe);
                const img = L.Entites.imageDe ? L.Entites.imageDe(e) : null;
                if (img) poses.add(img.canvas);
            }
            out[slug] = { images: images.size, dessins: poses.size, corps: e.sprite,
                          zero: images.size === 1 && images.has(0) };
            L.Entites.retirer(e);
        }
        return out;
    }""" % list(AMUSEURS))
    for slug in AMUSEURS:
        n = r[slug]
        assert n["corps"] == slug, "%s porte le corps « %s »" % (slug, n["corps"])
        assert n["zero"] is False, "%s tient l'image zéro, comme avant" % slug
        assert n["images"] >= 3, "%s ne fait que %s image(s)" % (slug, n["images"])
        # ⚠️ Et les images choisies doivent être de VRAIS dessins différents :
        # `poseFixe` qui change sans que le canevas change, c'est un compteur
        # qui tourne dans le vide.
        assert n["dessins"] >= 3, "%s : %s dessin(s) pour %s poses" % (
            slug, n["dessins"], n["images"]
        )


def test_l_echassier_depasse_la_foule(banc):
    """⚠️ C'est la seule chose qu'un échassier fait qu'un homme ne fait pas : on
    le voit PAR-DESSUS son propre attroupement, de l'autre bout de la rue. Un
    échassier à hauteur d'homme serait un homme."""
    r = banc("""function (L, o) {
        const h = {};
        for (const nom of ['echassier', 'jongleur', 'amuseur', 'musicien', 'joueur']) {
            h[nom] = { h: L.SPRITES[nom].h, ancre: L.SPRITES[nom].ancre[1] };
        }
        return h;
    }""")
    ordinaire = max(r[nom]["h"] for nom in ("joueur", "amuseur", "musicien"))
    assert r["echassier"]["h"] >= ordinaire + 8, (
        "l'échassier fait %s px, le plus grand corps de la ville en fait %s — "
        "il ne dépasse pas la foule" % (r["echassier"]["h"], ordinaire)
    )
    # Il est ancré à ses PIEDS, comme tout le monde : sinon il flotte.
    assert r["echassier"]["ancre"] == r["echassier"]["h"] - 1
    # Le jongleur, lui, a besoin de ciel au-dessus de la tête pour ses balles.
    assert r["jongleur"]["h"] > ordinaire, "le jongleur n'a pas de place pour ses balles"


def test_le_musicien_joue_vraiment_et_plus_fort_de_pres(banc, paquet):
    """⚠️ « Je veux que le musicien fasse vraiment de la musique, 5 musiques
    différentes. » Il ne sortait PAS UNE NOTE : le jeu avait le séquenceur, dix
    morceaux écrits en notes et un chef d'orchestre, et l'homme à la guitare
    était muet depuis le premier jour.

    Ce juge tient les trois bouts : il pose des notes DANS le contexte audio,
    elles atteignent la sortie (une source que personne ne relie au maître joue
    sans qu'on l'entende — le dépôt a déjà payé ce défaut), et le volume suit
    la DISTANCE."""
    r = banc("""function (L, o) {
        o.brancherAudio(true);
        L.Son.reveiller();
        L.Jeu.commencer();
        L.graine(88);
        const j = L.B.joueur;
        // ⚠️ ON NE COMPTE QUE LES NOTES DU MUSICIEN. `joues` recueille TOUT ce
        // qui demarre — l'ambiance du district, les pas, les moteurs — et un
        // juge qui compte tout ne juge rien. On suit donc les branchements
        // jusqu'a SA sortie a lui : c'est la meme marche que
        // `ctx.atteintLaSortie`, et elle repond a la vraie question (est-ce que
        // ces notes-la sortent de ce gars-la ?).
        function siennes() {
            const sortie = L.Son.Rue.sortie;
            if (!sortie) return 0;
            let n = 0;
            for (const s of L.Son.contexte.sources) {
                if (!s.__demarree) continue;
                const vus = new Set(), pile = [s];
                while (pile.length) {
                    const c = pile.pop();
                    if (!c || vus.has(c)) continue;
                    vus.add(c);
                    if (c === sortie) { n++; break; }
                    (c.__vers || []).forEach(function (x) { pile.push(x); });
                }
            }
            return n;
        }
        // ⚠️ ON JUGE LE FILET, c'est-a-dire les NOTES. `son.js` joue le mp3
        // quand il existe et la synthese sinon — et un mp3 se telecharge, donc
        // il ne peut pas arriver au milieu d'une boucle d'images synchrone : le
        // banc n'a aucun tour de boucle a donner aux promesses. On coupe donc
        // le fichier ici et on mesure le chemin qui doit marcher DE TOUTE
        // FACON — reseau coupe, decodage refuse, fichier absent. C'est la
        // moitie du contrat que personne d'autre ne tient : le son des
        // fichiers, lui, se juge la ou les fichiers se chargent.
        for (const m of L.B.defs.audio.musiques) {
            if (m.slug.indexOf('rue_') === 0) m.fichier = null;
        }
        const a = L.Entites.archetype('musicien');
        const e = L.Entites.creerPieton(j.x + 30, j.y, a);
        e.etat = 'fige'; e.plante = { x: e.x, y: e.y };
        L.Entites.ouvrirLeSpectacle(e);
        L.Entites.indexer();
        // ⚠️ IL SONNE PAR UN DES DEUX CHEMINS, et le juge doit tenir les deux :
        // le mp3 quand il existe, les notes sinon. C'est la regle de tout
        // `son.js` depuis le premier jour (« l'echantillon quand il existe, la
        // synthese sinon ») ; un juge qui n'attendrait que les oscillateurs
        // tomberait le jour ou la piece recoit son enregistrement, alors que
        // le musicien, lui, jouerait mieux que jamais.
        function sonne() {
            const cle = L.Son.Rue.jouee ? 'rue-' + L.Son.Rue.jouee : null;
            return { boucle: !!(cle && L.Son.boucleActive(cle)), notes: siennes() };
        }
        const avant = siennes();
        o.frame(60);
        const s = sonne();
        const pres = { notes: s.notes - avant, boucle: s.boucle, slug: L.Son.Rue.jouee,
                       volume: L.Son.Rue.g, muettes: L.Son.contexte.sourcesMuettes() };
        // On s'en va : plus loin, plus faible.
        e.x = j.x + 200; e.plante = { x: e.x, y: e.y };
        L.Entites.indexer();
        o.frame(60);
        const loin = { volume: L.Son.Rue.g };
        // Hors de portee : il se TAIT.
        e.x = j.x + 4000; e.plante = { x: e.x, y: e.y };
        L.Entites.indexer();
        o.frame(120);
        const jalon = siennes();
        o.frame(120);
        const parti = { notes: siennes() - jalon, slug: L.Son.Rue.jouee,
                        boucle: sonne().boucle };
        return { toune: e.toune, pres: pres, loin: loin, parti: parti };
    }""")
    pieces = [m["slug"] for m in paquet["audio"]["musiques"] if m["slug"].startswith("rue_")]
    assert len(pieces) == 5, "cinq pièces de rue, pas %s" % len(pieces)
    assert r["toune"] in pieces, "le musicien ne joue rien : %s" % r["toune"]
    assert r["pres"]["slug"] == r["toune"], "sa toune n'est pas celle qui joue : %s" % r["pres"]
    assert r["pres"]["notes"] > 0 or r["pres"]["boucle"], (
        "il ne sort rien du musicien : ni notes, ni boucle (%s)" % r["pres"]
    )
    # ⚠️ Une source que personne ne relie au maître démarre sans erreur et ne
    # s'entend JAMAIS : c'est ainsi qu'aucun des 79 fichiers du dépôt n'a été
    # entendu jusqu'au 13 sept. 2026, sans qu'une seule erreur soit levée.
    assert r["pres"]["muettes"] == 0, "des notes jouent sans atteindre la sortie"
    assert r["pres"]["volume"] > r["loin"]["volume"] > 0, (
        "le volume ne suit pas la distance : %s puis %s"
        % (r["pres"]["volume"], r["loin"]["volume"])
    )
    assert r["parti"]["slug"] is None and r["parti"]["notes"] == 0 \
        and r["parti"]["boucle"] is False, (
        "il joue encore à l'autre bout de la ville : %s" % r["parti"]
    )


def test_le_public_applaudit_paie_et_se_renouvelle(banc, paquet):
    """⚠️ L'ARGENT CHANGE DE POCHE POUR DE VRAI, comme pour le pickpocket :
    sinon le chapeau n'est qu'une animation, et fouiller l'artiste rapporterait
    la même chose qu'il ait joué ou non. Et le public TOURNE : un cercle de
    trois statues qui ne bougent plus n'est pas une foule."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        L.graine(64);
        const a = L.Entites.archetype('jongleur');
        const e = L.Entites.creerPieton(L.B.joueur.x + 36, L.B.joueur.y, a);
        e.etat = 'fige'; e.plante = { x: e.x, y: e.y };
        L.Entites.indexer();
        L.Entites.ouvrirLeSpectacle(e);
        const bourse = e.argent;
        const passes = new Set();
        let bravos = 0;
        for (let i = 0; i < 3000; i++) {
            o.frame(1);
            for (const q of L.Entites.badauds(e)) passes.add(q.id);
            for (const q of L.B.entites) {
                if (q.bulle && q.bulle.texte && /BRAVO|HOP|OH!/.test(q.bulle.texte)) bravos++;
            }
        }
        return { gagne: e.argent - bourse, passes: passes.size, bravos: bravos,
                 cercle: L.Entites.badauds(e).length };
    }""")
    assert r["passes"] >= 5, (
        "le public ne se renouvelle pas : %s personnes en 3000 images" % r["passes"]
    )
    assert r["gagne"] > 0, "le chapeau est vide : personne ne l'a payé"
    assert r["bravos"] > 0, "personne n'applaudit"


def test_un_amuseur_se_pose_sur_une_scene_de_la_carte(banc, paquet):
    """⚠️ Un amuseur ne choisit pas un coin de rue au hasard : il se met LÀ OÙ
    LE MONDE PASSE ET S'ARRÊTE. `naitreLesSortes` le posait sur la première
    tuile marchable venue hors de l'écran — c'est-à-dire souvent dans une
    ruelle, devant un mur de hangar, entre deux poubelles. Le numéro était bon,
    l'endroit ne l'était pas, et personne ne venait le voir.

    `carte.scenes` donne les endroits qui valent quelque chose : la place
    publique, les parcs, le terminus d'autobus, le trottoir devant les
    commerces — et chacun est **dégagé** sur deux tuiles à la ronde, sans quoi
    le cercle de badauds n'a nulle part où se mettre."""
    scenes = paquet["carte"]["scenes"]
    assert scenes, "la carte ne propose aucune scène"
    centre = [s for s in scenes if s["district"] == "faubourg"]
    assert len(centre) >= 6, "le centre-ville n'a que %s scènes" % len(centre)
    ilots = {s["ilot"] for s in centre}
    assert "o" in ilots, "la place publique n'est pas une scène"
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        L.graine(44);
        // ⚠️ **AU CENTRE DU FAUBOURG, pas au terminus.** Un amuseur naît sur une
        // scène HORS CHAMP mais dans la bulle (`sceneLibre`) : au départ de la
        // partie, les scènes du terminus sont toutes à l'écran — elles ne
        // comptent pas — et les suivantes sont hors de la bulle. Ce juge tenait
        // donc à la trame, et le 17 sept. 2026 elle a bougé : plus un seul
        // amuseur en 2 000 images, alors que la règle n'avait pas changé.
        const zf = (L.Monde.carte.zones || []).find(function (q) { return q.slug === 'faubourg'; });
        L.B.joueur.x = (zf.x + zf.l / 2) * L.TT; L.B.joueur.y = (zf.y + zf.h / 2) * L.TT;
        L.Monde.centrerCamera(L.B.joueur.x, L.B.joueur.y);
        const sur = [], hors = [];
        for (let i = 0; i < 2000; i++) {
            o.frame(1);
            if (i % 50) continue;
            for (const a of L.B.entites) {
                if (a.type !== 'pieton' || !a.vivant) continue;
                if (L.Entites.SPECTACLES.indexOf(a.metier) < 0) continue;
                const s = (L.B.defs.carte.scenes || []).find(function (q) {
                    return Math.abs(q.x * L.TT + 8 - a.x) < 12 && Math.abs(q.y * L.TT + 8 - a.y) < 12;
                });
                if (s) sur.push(s.ilot); else hors.push(a.metier);
            }
        }
        return { sur: sur.length, hors: hors.length, ilots: Array.from(new Set(sur)).sort() };
    }""")
    assert r["sur"] > 0, "aucun amuseur ne s'est posé sur une scène"
    assert r["hors"] == 0, "%s amuseur(s) plantés hors de toute scène" % r["hors"]
