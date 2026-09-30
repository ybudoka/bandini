"""Les interieurs vus du jeu : on entre, il y a du monde, et les comptoirs servent.

⚠️ Le juge qui compte le plus est le premier : `carte.py` declare des POINTS
d'action dans chaque piece, et `missions.js` doit savoir quoi en faire. Les deux
listes vivent dans deux langages et deux fichiers ; sans ce test, on dessine un
comptoir a Montreal et on l'oublie a Quebec — c'est exactement comme ca que
« guichet », « casier » et « sortie_prison » etaient devenus des comptoirs morts
qu'on touchait pour lire « PLUS TARD ».
"""

import json

from app import missions

#: Les points qui ne passent PAS par un menu : ils agissent tout de suite. ⚠️ Le point d'un
#: PERSONNAGE posé dedans (`ou: "point:<type>"`) en est un, et se lit dans le catalogue :
#: la liste écrite à la main avait oublié le Dr Lachance.
#: Des gestes, pas des menus. L'ascenseur du garage souterrain descend au −1 (`Souterrain.descendreAPied`).
SANS_MENU = ("escalier", "fouiller", "rame", "ascenseur") + tuple(
    p["ou"][len("point:"):] for p in missions.PERSONNAGES if p["ou"].startswith("point:"))

#: ⚠️ Les comptoirs encore en chantier, et le jalon qui les doit. La liste est
#: volontairement penible a garder : chaque entree doit encore exister dans une
#: piece (sinon ce test rougit), et le jour ou M9 pose son menu, on l'enleve.
#: C'est la seule facon honnete d'avoir un comptoir dessine avant son menu —
#: sans elle, on exempterait par habitude et « guichet » renaîtrait.
#: Vide depuis le 13 sept. 2026 : le lot de la fourriere a recu son menu.
EN_CHANTIER: dict[str, str] = {}

def _types(paquet: dict) -> list[str]:
    """⚠️ LES POINTS DE LA VILLE LIVREE, pas ceux du catalogue du module. Depuis
    que les commerces et les logements se POSENT a la mesure de leur batiment,
    `emplettes`, `salon`, `journal` et `fouiller` ne vivent plus dans
    `carte.INTERIEURS` : ils naissent avec la ville. Lire le catalogue seul
    laissait la moitie du contrat hors du juge. (La carte telle que le navigateur
    la recoit : celle du paquet de la session, pas une ville regeneree.)"""
    return sorted({p["type"] for piece in paquet["carte"]["interieurs"].values()
                   for p in piece["points"]})


def test_chaque_comptoir_dessine_est_servi_par_le_jeu(banc, paquet):
    """⚠️ LE contrat entre `carte.INTERIEURS` et `missions.js`. Un type de point
    qui n'a ni libelle ni menu est une porte qu'on ouvre pour rien."""
    TYPES = _types(paquet)
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const types = %s, sansMenu = %s;
        const muets = [], sansLibelle = [];
        const c = L.Monde.carte;
        for (const type of types) {
            // La piece qui porte ce point-la, et le point lui-meme.
            let trouve = null, piece = null;
            for (const cle in c.def.interieurs) {
                const p = c.def.interieurs[cle];
                const q = (p.points || []).find(function (x) { return x.type === type; });
                if (q) { trouve = q; piece = p; break; }
            }
            if (!trouve) continue;
            if (!L.Missions.libelleDuPoint(type)) sansLibelle.push(type);
            if (sansMenu.indexOf(type) >= 0) continue;
            L.B.interieur = piece;
            const menu = L.Missions.menuDuPoint(trouve);
            if (!menu || !menu.items || !menu.items.length) muets.push(type);
        }
        L.B.interieur = null;
        return { muets: muets, sansLibelle: sansLibelle, vus: types.length };
    }""" % (json.dumps(TYPES), json.dumps(list(SANS_MENU))))
    assert r["vus"] == len(TYPES)
    assert r["sansLibelle"] == [], f"des points sans libelle d'invite : {r['sansLibelle']}"
    attendus = set(EN_CHANTIER) & set(TYPES)
    assert set(EN_CHANTIER) <= set(TYPES), \
        f"exemption perimee : {set(EN_CHANTIER) - set(TYPES)} n'est plus dessine nulle part"
    assert set(r["muets"]) == attendus, \
        f"des comptoirs qui ne donnent rien : {sorted(set(r['muets']) - attendus)}"


def test_on_entre_chez_un_commerce_ordinaire_et_il_porte_son_enseigne(banc):
    """⚠️ Dix-huit tabagies partagent la meme piece : c'est le nom pose sur la
    PORTE qui doit s'afficher, pas celui du catalogue. Sinon on lit
    « TABAGIE DUBOIS » sur le mur et « L'epicerie » en entrant."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const j = L.B.joueur, c = L.Monde.carte;
        // ⚠️ On cherche une porte par ce qu'il y a DERRIERE, pas par un slug :
        // chaque commerce a maintenant sa piece a lui, posee a la mesure de son
        // batiment (« bouffe_12 »), et plus une piece partagee par dix-huit
        // tabagies. C'est la porte de la piece qui dit ce qu'on pousse.
        const porte = c.portes.find(function (p) {
            const piece = c.def.interieurs[p.interieur];
            return p.nom && piece.porte === 'commerce';
        });
        j.x = porte.x * L.TT + 8; j.y = (porte.y + 1) * L.TT + 10;
        // ⚠️ On regarde la porte : dehors, ENTRER n'agit que sur ce qu'on regarde (test_regard_js.py).
        L.Entites.regarder(j, 0, -1);
        L.Missions.majInvite(j);
        const invite = L.B.invite;
        o.entrer(porte);
        const gens = L.B.entites.filter(function (e) { return e.type === 'pieton'; });
        const commis = gens.filter(function (e) { return e.arch === 'commis'; });
        const dedans = { nom: L.B.interieur.nom, genre: L.B.interieur.porte, gens: gens.length,
                         commis: commis.length, poste: commis.length ? !!commis[0].poste : false,
                         points: L.B.interieur.points.length };
        o.sortir();
        return { invite: invite, porte: porte, dedans: dedans,
                 dehors: L.B.entites.filter(function (e) { return e.arch === 'commis'; }).length };
    }""")
    assert r["invite"] == "ENTRER"
    assert r["dedans"]["nom"] == r["porte"]["nom"], "la piece n'a pas pris le nom de l'enseigne"
    assert r["dedans"]["genre"] == "commerce", "on a pousse une porte de maison"
    assert r["dedans"]["commis"] >= 1, "personne au comptoir"
    assert r["dedans"]["poste"] is True, "le commis doit tenir son poste"
    assert r["dedans"]["points"] >= 1
    assert r["dehors"] == 0, "le commis est sorti dans la rue avec nous"


def test_le_comptoir_d_un_commerce_ordinaire_vend(banc, paquet):
    """Acheter au comptoir d'une famille : ca coute, et ca donne."""
    tarifs = paquet["economie"]["tarifs"]
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const j = L.B.joueur, c = L.Monde.carte;
        const porte = c.portes.find(function (p) {
            return (c.def.interieurs[p.interieur].points || []).some(function (q) {
                return q.type === 'emplettes' && q.genre === 'bouffe';
            });
        });
        j.x = porte.x * L.TT + 8; j.y = (porte.y + 1) * L.TT + 10;
        o.entrer(porte);
        const point = L.B.interieur.points.find(function (p) { return p.type === 'emplettes'; });
        j.x = point.x * L.TT + 8; j.y = point.y * L.TT + 8;
        L.B.partie.argent = 200; j.vie = 40; j.endurance = 20;
        L.Missions.majInvite(j);
        const invite = L.B.invite;
        L.Missions.utiliserPoint(j);
        const menu = L.B.menu;
        const titre = menu.titre, n = menu.items.length;
        menu.items[0].faire();
        return { invite: invite, titre: titre, n: n, argent: L.B.partie.argent,
                 vie: j.vie, souffle: j.endurance, nom: L.B.interieur.nom };
    }""")
    assert r["invite"] == "ACHETER"
    assert r["titre"] == r["nom"].upper(), "le menu doit porter le nom de l'enseigne"
    assert r["n"] >= 2
    assert r["argent"] == 200 - tarifs["sandwich"]
    assert r["vie"] == 40 + tarifs["sandwich_pv"]
    assert r["souffle"] > 20


def test_l_escalier_monte_a_l_etage_et_redescend(banc):
    """⚠️ Monter ne doit PAS ressortir : `B.exterieur` reste celui d'en bas, et
    c'est par cette porte-la qu'on retrouvera la rue, trois etages plus haut."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const j = L.B.joueur, c = L.Monde.carte;
        // Un logement a etage : sa piece porte un escalier.
        const porte = c.portes.find(function (p) {
            return (c.def.interieurs[p.interieur].points || []).some(function (q) {
                return q.type === 'escalier';
            });
        });
        j.x = porte.x * L.TT + 8; j.y = (porte.y + 1) * L.TT + 10;
        o.entrer(porte);
        const bas = { slug: L.B.interieur.slug, dehors: !!L.B.exterieur };
        const point = L.B.interieur.points.find(function (p) { return p.type === 'escalier'; });
        j.x = point.x * L.TT + 8; j.y = point.y * L.TT + 8;
        L.Missions.majInvite(j);
        const invite = L.B.invite;
        L.Missions.utiliserPoint(j);
        o.fondu();                      // l'escalier passe par un fondu, comme une porte
        const haut = { slug: L.B.interieur.slug, nom: L.B.interieur.nom, dehors: !!L.B.exterieur,
                       w: L.Monde.carte.w, sol: L.Monde.solidite(Math.floor(j.x / L.TT), Math.floor(j.y / L.TT)) };
        // On redescend par l'escalier de l'etage.
        const retour = L.B.interieur.points.find(function (p) { return p.type === 'escalier'; });
        j.x = retour.x * L.TT + 8; j.y = retour.y * L.TT + 8;
        L.Missions.majInvite(j);
        const inviteHaut = L.B.invite;
        L.Missions.utiliserPoint(j);
        o.fondu();
        const revenu = L.B.interieur.slug;
        o.sortir();
        return { bas: bas, invite: invite, inviteHaut: inviteHaut, haut: haut, revenu: revenu,
                 sorti: L.B.interieur, pres: Math.hypot(j.x - porte.x * L.TT - 8, j.y - (porte.y + 1) * L.TT - 10) };
    }""")
    assert r["bas"]["dehors"] is True
    assert r["invite"] == "MONTER"
    assert r["inviteHaut"] == "DESCENDRE", "l'escalier de l'étage dit MONTER pour redescendre"
    assert r["haut"]["slug"] != r["bas"]["slug"], "l'escalier n'a pas change de plancher"
    assert r["haut"]["dehors"] is True, "monter a oublie par ou l'on est entre"
    assert r["haut"]["sol"] != 1, "on arrive dans un mur"
    assert r["revenu"] == r["bas"]["slug"], "on reste pris en haut"
    assert r["sorti"] is None and r["pres"] < 20, "on ressort par la porte d'en bas"


def test_les_tiroirs_d_un_logement_ne_se_fouillent_qu_une_fois(banc, paquet):
    tarifs = paquet["economie"]["tarifs"]
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const j = L.B.joueur, c = L.Monde.carte;
        const portes = c.portes.filter(function (p) {
            return (c.def.interieurs[p.interieur].points || []).some(function (q) {
                return q.type === 'fouiller';
            });
        });
        function fouiller(porte) {
            if (L.B.interieur) o.sortir();
            j.x = porte.x * L.TT + 8; j.y = (porte.y + 1) * L.TT + 10;
            o.entrer(porte);
            const point = L.B.interieur.points.find(function (p) { return p.type === 'fouiller'; });
            j.x = point.x * L.TT + 8; j.y = point.y * L.TT + 8;
            const avant = L.B.partie.argent;
            L.Missions.majInvite(j);
            const invite = L.B.invite;
            L.Missions.utiliserPoint(j);
            return { gain: L.B.partie.argent - avant, invite: invite };
        }
        // Le standing se lit DEHORS, avant d'entrer : une piece n'a pas de quartier.
        const standing = L.Monde.standingA(portes[0].x, portes[0].y);
        const un = fouiller(portes[0]);
        const encore = fouiller(portes[0]);
        const autre = fouiller(portes[1]);
        return { un: un, encore: encore.gain, autre: autre.gain, adresses: portes.length, standing: standing };
    }""")
    assert r["adresses"] >= 2, "il faut deux logements pour juger"
    assert r["un"]["invite"] == "FOUILLER"
    # ⚠️ Les tiroirs disent le quartier (4e vague des quartiers) : la fourchette
    # est celle des tarifs, multipliee par la part du standing de l'adresse.
    part = paquet["economie"]["fouille_standing"].get(r["standing"], 1)
    assert round(tarifs["fouille_min"] * part) <= r["un"]["gain"] <= round(tarifs["fouille_max"] * part), r
    assert r["encore"] == 0, "les memes tiroirs paient deux fois"
    assert r["autre"] > 0, "une autre adresse doit payer"


def test_le_barbier_change_la_tete_et_fait_oublier_la_tienne(banc, paquet):
    coupe = paquet["economie"]["tarifs"]["coupe"]
    couleur = paquet["coiffures"][1]["couleur"]
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const j = L.B.joueur, c = L.Monde.carte;
        const porte = c.portes.find(function (p) {
            return (c.def.interieurs[p.interieur].points || []).some(function (q) {
                return q.type === 'salon';
            });
        });
        j.x = porte.x * L.TT + 8; j.y = (porte.y + 1) * L.TT + 10;
        o.entrer(porte);
        const point = L.B.interieur.points.find(function (p) { return p.type === 'salon'; });
        j.x = point.x * L.TT + 8; j.y = point.y * L.TT + 8;
        L.B.partie.argent = 100;
        L.B.recherche.etoiles = 2; L.B.recherche.chaleur = 500;
        L.Missions.utiliserPoint(j);
        const menu = L.B.menu;
        menu.items[1].faire();
        const apres = { cheveux: L.B.partie.cheveux, swap: j.swaps.h, chandail: j.swaps.c,
                        argent: L.B.partie.argent, etoiles: L.B.recherche.etoiles };
        // Et le linge ne doit pas effacer la teinture.
        L.Missions.porterTenue('veste_cuir');
        return { apres: apres, apresLinge: j.swaps.h, n: menu.items.length };
    }""")
    assert r["n"] >= 3
    assert r["apres"]["cheveux"] == couleur and r["apres"]["swap"] == couleur
    assert r["apres"]["argent"] == 100 - coupe
    assert r["apres"]["etoiles"] == 0, "changer de tete doit faire oublier la tienne"
    assert r["apresLinge"] == couleur, "changer de linge a efface la coupe"


def test_les_meubles_ne_coincent_personne(banc):
    """⚠️ Un meuble arrete un char, pas un piéton (solidite 3). Si l'un d'eux
    bloquait, un joueur pourrait entrer, se coincer derriere un comptoir et
    perdre sa partie — il n'y a pas de « se degager » dans ce jeu."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const c = L.Monde.carte, def = c.def.interieurs;
        const bloquants = [];
        for (const cle in def) {
            const piece = def[cle];
            for (let y = 0; y < piece.hauteur; y++) {
                for (let x = 0; x < piece.largeur; x++) {
                    const g = piece.sol[y][x];
                    const p = c.legende[g] || {};
                    if (p.meuble && p.solide === 1) bloquants.push(cle + ':' + g);
                }
            }
        }
        return { bloquants: bloquants.slice(0, 5) };
    }""")
    assert r["bloquants"] == []


def test_on_ressort_de_toutes_les_pieces_par_la_porte(banc):
    """⚠️ Le bloquant du 13 sept. 2026 : « chez Ti-Paul, il est impossible de
    sortir ». On entrait, et ACTION servait le comptoir — toujours : le point
    d'action s'attrape dans 1,6 tuile AUTOUR de soi, la porte seulement sur la
    tuile collee a elle, et six pieces avaient un comptoir assez pres. Pire,
    `utiliserPoint` rend `true` meme quand il n'a qu'un « PLUS TARD » a dire :
    aucune deuxieme pression ne finissait par sortir. On quittait vers le titre,
    ou on restait.

    Le juge passe par le VRAI chemin — la touche ACTION, la ou l'on arrive en
    entrant — et il le fait dans CHAQUE piece de la ville : c'est la seule facon
    de voir venir la prochaine."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const j = L.B.joueur, c = L.Monde.carte;
        const prises = [], vues = [];
        for (const porte of c.portes) {
            if (L.B.interieur) o.sortir();
            j.x = porte.x * L.TT + 8; j.y = (porte.y + 1) * L.TT + 10;
            if (!o.entrer(porte)) continue;
            const slug = L.B.interieur.slug;
            if (vues.indexOf(slug) < 0) vues.push(slug);
            // On ne bouge pas : on arrive sur la tuile de sortie, et on appuie.
            o.tape('KeyE', 2);
            o.fondu();
            if (L.B.interieur) {
                prises.push(slug + ' (' + (L.B.menu ? 'menu ' + L.B.menu.titre : 'rien') + ')');
                if (L.B.menu) L.Hud.fermerMenu();
                o.sortir();
            }
        }
        if (L.B.interieur) o.sortir();
        return { prises: prises, pieces: vues.length, dehors: L.B.interieur === null };
    }""")
    assert r["pieces"] >= 25, r["pieces"]
    assert r["prises"] == [], f"on reste enferme dans : {r['prises']}"
    assert r["dehors"] is True


def test_un_comptoir_sur_la_tuile_de_sortie_ne_vole_pas_la_porte(banc):
    """⚠️ Les deux corrections du bloquant sont necessaires, et chacune a son
    juge : le plan des pieces garde la tuile de sortie libre (juge Python), et le
    jeu fait passer la porte avant le comptoir (celui-ci).

    Ici on REMET le piege a la main — un point d'action pose pile sur la tuile de
    sortie, comme le journal de chez Ti-Paul l'etait — et la porte doit gagner
    quand meme. Sans ca, la premiere piece dessinee de travers rendrait le jeu
    injouable une deuxieme fois."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const j = L.B.joueur, c = L.Monde.carte;
        const porte = c.portes.find(function (p) { return p.lieu === 'depanneur'; }) || c.portes[0];
        j.x = porte.x * L.TT + 8; j.y = (porte.y + 1) * L.TT + 10;
        o.entrer(porte);
        const piece = L.B.interieur;
        const sortie = piece.apparition;
        piece.points.push({ type: 'journal', x: sortie.x, y: sortie.y });
        const sousLaMain = !!L.Missions.pointSousLaMain(j);
        o.tape('KeyE', 2);
        o.fondu();
        return { sousLaMain: sousLaMain, dedans: L.B.interieur, menu: L.B.menu ? L.B.menu.titre : null };
    }""")
    assert r["sousLaMain"] is True, "le piege n'a pas ete remis : le point n'est pas a portee"
    assert r["dedans"] is None, f"le comptoir a vole la porte (menu : {r['menu']})"


def test_une_piece_se_peint_sans_planter(banc):
    """On entre dans chaque piece et on laisse tourner six images : c'est le
    chemin qui cuit les tuiles de meuble, une par glyphe."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const j = L.B.joueur, c = L.Monde.carte;
        const vues = [];
        for (const porte of c.portes) {
            if (L.B.interieur) o.sortir();
            j.x = porte.x * L.TT + 8; j.y = (porte.y + 1) * L.TT + 10;
            if (!o.entrer(porte)) continue;
            o.frame(3);
            vues.push(L.B.interieur.slug);
        }
        if (L.B.interieur) o.sortir();
        return { vues: vues.length, pieces: Object.keys(c.def.interieurs).length,
                 etat: L.B.etat, entites: L.B.entites.length };
    }""")
    assert r["vues"] >= 30, r["vues"]
    assert r["etat"] == "jeu"


def test_un_lit_de_quatre_tuiles_est_un_seul_lit(banc):
    """Retour de Martin (13 sept. 2026) : « les lits doivent vraiment avoir l'air
    de lits, juste un set d'oreillers et des couvertes ; actuellement c'est 2 ou
    4 cases avec chacune leur oreiller ». Le peintre du lit ne savait pas qu'il
    avait des voisines : un lit de 2 × 2 etait quatre lits d'une place colles.

    ⚠️ Le remede etait deja ecrit pour la cloture et le toit : la variante vient
    des voisines (`varianteDeBloc`). Le juge lit les quatre variantes du lit de la
    planque, cuit les quatre tuiles avec, et regarde les traces : l'oreiller n'est
    qu'en tete et il court d'une tuile a l'autre, la couverture aussi — et le
    cadre ne se ferme, avec son pixel de plancher, que la ou le lit s'arrete."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const j = L.B.joueur, c = L.Monde.carte;
        const porte = c.portes.find(function (p) { return p.interieur === 'planque'; });
        j.x = porte.x * L.TT + 8; j.y = (porte.y + 1) * L.TT + 10;
        o.entrer(porte);
        // Le lit de la planque : nord-ouest, nord-est, sud-ouest, sud-est.
        const variantes = [[1, 1], [2, 1], [1, 2], [2, 2]].map(function (t) { return L.Monde.varianteDeBloc('l', t[0], t[1]) & 15; });   // sans le grain
        o.sortir();
        function peindre(variante) {
            const ctx = L.Base.nouveauCanvas(L.TT, L.TT).getContext('2d');
            ctx.traces = [];
            L.TUILES['l'](ctx, variante, L.TT);
            return ctx.traces;
        }
        const OREILLER = '#efeae0', COUVERTURE = '#3f6b8a', BOIS = '#5b3f26';
        function rects(traces, couleur) { return traces.filter(function (t) { return t[4] === couleur; }); }
        // L'oreiller fait quatre pixels de haut ; le drap rabattu, de la meme couleur, deux.
        function oreiller(traces) { return rects(traces, OREILLER).filter(function (t) { return t[3] >= 3; }); }
        function boite(t) { return [t[0], t[1], t[0] + t[2], t[1] + t[3]]; }
        const tuiles = variantes.map(peindre);
        const NO = tuiles[0], NE = tuiles[1], SO = tuiles[2], SE = tuiles[3];
        return {
            variantes: variantes,
            oreillers: tuiles.map(function (t) { return oreiller(t).length; }),
            // Un seul oreiller, a cheval sur la couture : il touche l'est de la tuile
            // nord-ouest et part de l'ouest de la nord-est.
            oreillerContinu: oreiller(NO).some(function (t) { return t[0] + t[2] === L.TT; })
                && oreiller(NE).some(function (t) { return t[0] === 0; }),
            // Et il laisse voir le matelas au bord exterieur : il ne touche pas le cadre.
            oreillerDedans: oreiller(NO).every(function (t) { return t[0] >= 3; }),
            // La couverture va jusqu'au bas des tuiles de tete et part du haut de celles du pied.
            couvertureContinue: rects(NO, COUVERTURE).some(function (t) { return t[1] + t[3] === L.TT; })
                && rects(SO, COUVERTURE).some(function (t) { return t[1] === 0; }),
            cadreNO: rects(NO, BOIS).map(boite), cadreSE: rects(SE, BOIS).map(boite),
        };
    }""")
    assert r["variantes"] == [2 | 4, 8 | 4, 1 | 2, 1 | 8], f"les voisines ne sont pas lues : {r['variantes']}"
    assert r["oreillers"] == [1, 1, 0, 0], f"l'oreiller n'est qu'en tete du lit : {r['oreillers']}"
    assert r["oreillerContinu"], "l'oreiller est coupe a la couture des deux tuiles de tete"
    assert r["oreillerDedans"], "l'oreiller touche le cadre"
    assert r["couvertureContinue"], "la couverture est coupee entre la tete et le pied"
    # Un pixel de plancher au nord et a l'ouest, le cadre plein jusqu'a la couture a l'est et au sud.
    assert r["cadreNO"] == [[1, 1, 16, 16]], r["cadreNO"]
    assert r["cadreSE"] == [[0, 0, 15, 15]], r["cadreSE"]


#: Le prelude commun des juges de blocs : cuire une tuile avec un masque et lire
#: ses traces. ⚠️ Les masques sont ceux de `varianteDeBloc` (1 nord, 2 est,
#: 4 sud, 8 ouest = ou le bloc CONTINUE), poses a la main : on juge le PEINTRE,
#: la lecture des voisines a son juge chez le lit.
_PEINDRE = """
        function peindre(g, v) { const ctx = L.Base.nouveauCanvas(L.TT, L.TT).getContext('2d'); ctx.traces = []; L.TUILES[g](ctx, v, L.TT); return ctx.traces; }
        function rects(traces, couleur) { return traces.filter(function (t) { return t[4] === couleur; }); }
        function boite(t) { return [t[0], t[1], t[0] + t[2], t[1] + t[3]]; }
        // Un bloc de quatre sur deux : la rangee de tete (nord-ouest, milieu, nord-est), puis celle du pied.
        function quatreSurDeux(g) { return [2 | 4, 2 | 4 | 8, 4 | 8, 1 | 2, 1 | 2 | 8, 1 | 8].map(function (v) { return peindre(g, v); }); }
"""


def test_un_billard_de_huit_tuiles_est_une_seule_table(banc):
    """Suite des lits (Martin, 14 sept. 2026 : « regarde si d'autres composantes
    meriteraient un traitement similaire »). Le billard du bar et de la taverne
    fait quatre tuiles sur deux, et c'etait huit tabourets : chaque tuile avait
    son plateau aux bords rentres, son vernis, son chant et son ombre. Le juge
    cuit les six tuiles avec leurs masques : au milieu de la rangee de tete le
    plateau ne rentre que son bord nord (une tuile entouree le remplit), un
    coin ne rentre que ses deux bords libres, le
    vernis ne court qu'au nord et le chant qu'au sud — et une table d'une seule
    tuile est celle d'avant, au pixel."""
    r = banc("""function (L, o) {""" + _PEINDRE + """
        const PLATEAU = '#a0784a', VERNIS = '#bb9160', CHANT = 'rgba(0,0,0,0.22)';
        const t = quatreSurDeux('a');
        return {
            plateauMilieu: rects(t[1], PLATEAU).map(boite), plateauNO: rects(t[0], PLATEAU).map(boite),
            plateauSE: rects(t[5], PLATEAU).map(boite), plateauCentre: rects(peindre('a', 15), PLATEAU).map(boite),
            vernis: t.map(function (u) { return rects(u, VERNIS).length; }),
            chant: t.map(function (u) { return rects(u, CHANT).length; }),
            seule: rects(peindre('a', 0), PLATEAU).map(boite),
        };
    }""")
    assert r["plateauMilieu"] == [[0, 2, 16, 16]], "au milieu de la tete, le plateau ne rentre que son bord nord"
    assert r["plateauCentre"] == [[0, 0, 16, 16]], "une tuile entouree de table est tout plateau"
    assert r["plateauNO"] == [[2, 2, 16, 16]], "le coin nord-ouest ne rentre que ses deux bords libres"
    assert r["plateauSE"] == [[0, 0, 14, 12]], "le coin sud-est garde la place du chant et de l'ombre"
    assert r["vernis"] == [1, 1, 1, 0, 0, 0], f"le vernis ne court qu'au nord : {r['vernis']}"
    assert r["chant"] == [0, 0, 0, 1, 1, 1], f"le chant ne se voit qu'au sud : {r['chant']}"
    assert r["seule"] == [[2, 2, 14, 12]], "une table d'une tuile n'a pas change"


def test_un_tapis_de_neuf_tuiles_est_un_seul_tapis(banc):
    """Le galon dore n'allait qu'en haut et en bas de CHAQUE tuile : le tapis de
    trois sur trois de la planque etait trois chemins de couloir empiles, et il
    n'avait pas de bord a gauche ni a droite. Le juge cuit les neuf tuiles : deux
    galons aux coins, un sur les cotes, aucun au centre — et le galon du haut est
    couche, celui de l'ouest debout. Un tapis d'une tuile en a quatre."""
    r = banc("""function (L, o) {""" + _PEINDRE + """
        const GALON = '#c9a24a';
        const masques = [2 | 4, 2 | 4 | 8, 4 | 8, 1 | 2 | 4, 15, 1 | 4 | 8, 1 | 2, 1 | 2 | 8, 1 | 8];
        const t = masques.map(function (v) { return peindre('y', v); });
        return {
            galons: t.map(function (u) { return rects(u, GALON).length; }),
            haut: rects(t[1], GALON).map(boite), ouest: rects(t[3], GALON).map(boite),
            seul: rects(peindre('y', 0), GALON).length,
        };
    }""")
    assert r["galons"] == [2, 1, 2, 1, 0, 1, 2, 1, 2], f"le galon ne borde que le bord du tapis : {r['galons']}"
    assert r["haut"] == [[0, 0, 16, 1]], "le galon du haut est couche sur le bord nord"
    assert r["ouest"] == [[0, 0, 1, 16]], "le galon de l'ouest est debout sur le bord"
    assert r["seul"] == 4


def test_une_presse_de_huit_tuiles_est_une_seule_machine(banc):
    """Les presses de l'usine font quatre tuiles sur deux, et chacune etait huit
    petites machines avec leurs deux boulons. Le juge cuit les six tuiles : au
    milieu de la tete la tole ne rentre que son bord nord (entouree, elle remplit
    la tuile), les boulons ne vont qu'aux quatre coins du
    bloc, la face au pied seulement, et la courroie est couchee dans toutes —
    d'une tuile a l'autre, elle court jusqu'au bord. Une machine d'une tuile
    tire son sens au sort dans le grain : les deux sens existent."""
    r = banc("""function (L, o) {""" + _PEINDRE + """
        const TOLE = '#82868c', FACE = '#5a5e63', BOULON = '#d8b83a', COURROIE = '#3f4347';
        const t = quatreSurDeux('m');
        return {
            tole: rects(t[1], TOLE).map(boite), toleCentre: rects(peindre('m', 15), TOLE).map(boite),
            boulons: t.map(function (u) { return rects(u, BOULON).length; }),
            faces: t.map(function (u) { return rects(u, FACE).length; }),
            courroies: t.map(function (u) { return rects(u, COURROIE).map(boite)[0]; }),
            seules: [0, 16].map(function (v) { return rects(peindre('m', v), COURROIE).map(boite)[0]; }),
        };
    }""")
    assert r["tole"] == [[0, 1, 16, 16]], "au milieu de la tete, la tole ne rentre que son bord nord"
    assert r["toleCentre"] == [[0, 0, 16, 16]], "une tuile entouree de machine est toute tole"
    assert r["boulons"] == [1, 0, 1, 1, 0, 1], f"un boulon par coin du bloc, aucun ailleurs : {r['boulons']}"
    assert r["faces"] == [0, 0, 0, 1, 1, 1], f"la face ne se voit qu'au pied : {r['faces']}"
    assert r["courroies"] == [[3, 4, 16, 7], [0, 4, 16, 7], [0, 4, 13, 7], [3, 4, 16, 7], [0, 4, 16, 7], [0, 4, 13, 7]], r["courroies"]
    assert sorted(b[2] - b[0] for b in r["seules"]) == [3, 10], f"une machine seule connait les deux sens : {r['seules']}"


def test_la_porte_s_ouvre_pour_le_joueur_aussi(banc):
    """⚠️ Retour de Martin : « les portes doivent ouvrir quand j'entre aussi. »
    Elles s'ouvraient pour les piétons et **pas pour lui** — il traversait un
    battant fermé, et c'était d'autant plus voyant que les passants, eux,
    attendaient poliment l'ouverture.

    ⚠️ Et le piège est dans l'ordre : le jeu est **figé** pendant un fondu de
    porte (`maj()` ne fait avancer que la transition). Un battant ouvert au
    départ y resterait donc au premier pixel, et la porte serait toujours
    fermée à l'écran. Les battants doivent battre **pendant** la transition —
    c'est la seule chose qui bouge quand tout le reste est arrêté."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const j = L.B.joueur, c = L.Monde.carte;
        const porte = c.portes.find(function (p) { return p.lieu === 'planque'; });
        j.x = porte.x * L.TT + 8; j.y = (porte.y + 1) * L.TT + 10;
        L.Monde.centrerCamera(j.x, j.y);
        // 1. On entre : le battant doit s'ouvrir PENDANT que la rue est encore
        //    visible, c'est-a-dire dans la premiere moitie du fondu.
        L.Jeu.entrer(porte);
        const ouvertures = [];
        for (let i = 0; i < 60 && L.B.transition; i++) {
            const tr = L.B.transition;
            const alpha = tr.t <= tr.ferme ? tr.t / tr.ferme : 0;
            ouvertures.push({ a: Math.round(alpha * 100) / 100, p: L.Monde.battant(porte.x, porte.y) });
            o.frame(1);
        }
        // Sur la rue (avant le noir), a-t-on vu la porte bouger ?
        const surLaRue = ouvertures.filter(function (q) { return q.a < 1; });
        const out = { dedans: !!L.B.interieur,
                      vueSurLaRue: Math.max.apply(null, surLaRue.map(function (q) { return q.p; })) };
        // 2. On ressort : la porte de la RUE doit s'ouvrir, pas celle de la piece.
        L.Jeu.sortir();
        o.fondu();
        out.sortie = L.Monde.battant(porte.x, porte.y);
        out.dehors = L.B.interieur === null;
        // 3. Et elle se referme toute seule.
        o.frame(60);
        out.refermee = L.Monde.battant(porte.x, porte.y);
        return out;
    }""")
    assert r["dedans"] is True and r["dehors"] is True, "l'aller-retour par la porte n'a pas marché"
    # ⚠️ Sur la rue, pendant que le fondu noircit : c'est là qu'on peut la voir.
    assert r["vueSurLaRue"] > 0.5, (
        "la porte n'a pas bougé pendant qu'on voyait encore la rue (%s) : le joueur traverse un battant fermé"
        % r["vueSurLaRue"]
    )
    assert r["sortie"] > 0.5, "en ressortant, la porte de la rue doit être ouverte : %s" % r["sortie"]
    assert r["refermee"] == 0, "la porte reste ouverte derrière le joueur : %s" % r["refermee"]


def test_les_portes_s_ouvrent_et_les_gens_les_passent(banc):
    """⚠️ Demande de Martin : « les piétons devraient aussi sortir et entrer dans
    les commerces. Profites-en pour aussi faire ouvrir concrètement les
    portes. » Les deux demandes n'en font qu'une, et le code disait pourquoi.

    **Un piéton sur trois sortait déjà d'une porte — et on ne le voyait
    jamais** : `placeDeNaissance()` refusait la place si elle était visible à
    l'écran. Ce n'était pas une sortie, c'était une naissance déguisée en
    sortie, dont le seul intérêt aurait été d'être vue. **Personne n'entrait
    nulle part**, et **aucune porte ne s'ouvrait**.

    Le juge tient les règles qui coûtent : une porte ne s'ouvre jamais sur
    rien, la planque du joueur n'avale personne, un commerce fermé non plus, et
    ⚠️ **le cache de morceaux ne bouge pas** quand une porte s'ouvre — c'est lui
    qui tient le rythme sur téléphone."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        L.graine(97);
        const j = L.B.joueur, c = L.Monde.carte;
        const out = {};

        // 1. Un battant s'ouvre, tient, et se referme — tout seul.
        const porte = c.portesFermees.find(function (p) { return p.glyphe === 'd'; });
        L.Monde.ouvrirPorte(porte.x, porte.y);
        const courbe = [];
        for (let i = 0; i < 60; i++) { courbe.push(L.Monde.battant(porte.x, porte.y)); o.frame(1); }
        out.battant = { debut: courbe[0], max: Math.max.apply(null, courbe), fin: courbe[courbe.length - 1],
                        monte: courbe[6] > courbe[0] };

        // 2. ⚠️ Le cache de morceaux ne bouge pas : le sol est cuit, le battant
        //    se pose PAR-DESSUS.
        L.Jeu.rendre();
        const morceaux0 = L.B.stats.morceaux;
        L.Monde.ouvrirPorte(porte.x, porte.y);
        L.Jeu.rendre();
        out.morceaux = { avant: morceaux0, apres: L.B.stats.morceaux };

        // 3. Quelles portes servent : jamais la planque, jamais le poste.
        function sert(lieu) {
            const p = (c.portes || []).find(function (q) { return q.lieu === lieu; });
            return p ? L.Entites.porteQuiSert({ x: p.x, y: p.y, glyphe: 'D' }) : null;
        }
        out.regles = { planque: sert('planque'), poste: sert('poste'), hopital: sert('hopital'),
                       logement: L.Entites.porteQuiSert({ x: porte.x, y: porte.y, glyphe: 'd' }) };
        // Un commerce : ouvert le jour, ferme la nuit.
        // ⚠️ Les interieurs n'ont pas d'heures declarees (seuls les kiosques
        // de rue en ont) : la nuit tient lieu de fermeture, sauf pour le bar —
        // qui vit justement la nuit.
        const dep = (c.portes || []).find(function (q) { return q.lieu === 'depanneur'; });
        const bar = (c.portes || []).find(function (q) { return q.lieu === 'bar'; });
        L.B.partie.heure = 0.5;
        const jour = dep ? L.Entites.porteQuiSert({ x: dep.x, y: dep.y, glyphe: 'D' }) : null;
        L.B.partie.heure = 0.95;
        const nuit = dep ? L.Entites.porteQuiSert({ x: dep.x, y: dep.y, glyphe: 'D' }) : null;
        const barLaNuit = bar ? L.Entites.porteQuiSert({ x: bar.x, y: bar.y, glyphe: 'D' }) : null;
        out.commerce = { jour: jour, nuit: nuit, barLaNuit: barLaNuit };
        L.B.partie.heure = 0.5;

        // 4. Sortir : ne DANS la porte, invisible tant qu'elle s'ouvre, puis
        //    dehors — et VISIBLE, meme en plein ecran.
        // ⚠️ ON REMET LA GRAINE ICI. Les soixante images du battant plus haut
        // font vivre toute la ville, et elles puisent dans `B.rng` un nombre de
        // fois qui depend d'elle : deux tuiles de cloture de plus a l'autre bout
        // du Faubourg, et l'archetype tire ici n'est plus le meme, ni sa vitesse.
        // La marge etait d'UN pixel (« avance > 8 » pour douze mesures), alors le
        // juge tombait sur des changements qui n'ont rien a voir avec les portes —
        // c'est deja arrive le 14 sept. 2026. Ce qu'on mesure ici ne doit dependre
        // que de la porte et de celui qui en sort.
        L.graine(97);
        j.x = porte.x * L.TT + 8; j.y = (porte.y + 6) * L.TT + 8;
        L.Monde.centrerCamera(j.x, j.y);
        // ⚠️ On DEGAGE LE PAS DE PORTE : ce qu'on juge ici, c'est le battant et
        // la sortie, pas la foule. Un passant plante sur la tuile d'en dessous
        // et celui qui sort n'avance plus de quatre pixels — le juge parlerait
        // alors de la densite du quartier, pas des portes.
        for (const q of L.B.entites.slice()) {
            if (q.type === 'pieton' && Math.hypot(q.x - j.x, q.y - j.y) < 120) L.Entites.retirer(q);
        }
        L.Entites.indexer();
        const arch = L.Entites.archetypeDeRue();
        const e = L.Entites.creerPieton(porte.x * L.TT + 8, (porte.y + 1) * L.TT + 8, arch);
        e.sortie = { x: porte.x, y: porte.y, t: 0 };
        L.Monde.ouvrirPorte(porte.x, porte.y);
        const y0 = e.y;
        const vus = [];
        // ⚠️ LE PLUS LOIN qu'il soit alle, pas ou il est a la quarantieme image :
        // une fois dehors il reprend sa vie, et flaner veut dire revenir sur ses
        // pas. Sur une porte de ruelle (celle que ce juge tire depuis que la
        // ville a bouge, 14 sept. 2026), il sortait de onze pixels puis
        // rebroussait chemin — le juge lisait cinq et disait qu'il ne sortait
        // pas. Ce qu'on juge, c'est qu'il SORT.
        let loin = 0;
        for (let i = 0; i < 40; i++) { o.frame(1); vus.push(e.dessine); loin = Math.max(loin, e.y - y0); }
        out.sortie = { cacheAuDebut: vus[0] === false, vuEnsuite: vus.indexOf(true) > 0,
                       avance: Math.round(loin), libre: !e.sortie,
                       aLEcran: L.Entites.visibleAEcran(e.x, e.y, 0) };

        // 5. Entrer : il marche jusqu'a la porte, elle s'ouvre, ET IL DISPARAIT
        //    SEULEMENT APRES — jamais devant une porte fermee.
        e.etat = 'flane'; e.porteBut = porte; e.porteT = 0; e.porteBloque = 0;
        e.x = porte.x * L.TT + 8; e.y = (porte.y + 3) * L.TT + 8;
        let disparu = -1, ouvertAlors = -1;
        for (let i = 0; i < 300 && disparu < 0; i++) {
            o.frame(1);
            if (L.B.entites.indexOf(e) < 0) { disparu = i; ouvertAlors = L.Monde.battant(porte.x, porte.y); }
        }
        out.entree = { disparu: disparu, ouvertAlors: ouvertAlors };
        return out;
    }""")
    b = r["battant"]
    assert b["debut"] == 0 and b["monte"] is True and b["max"] >= 0.99 and b["fin"] == 0, (
        "un battant doit s'ouvrir, tenir, puis se refermer tout seul : %s" % b
    )
    # ⚠️ LE juge du rythme : repeindre un morceau de 256 px pour une porte
    # tuerait le cache qui tient le téléphone.
    assert r["morceaux"]["apres"] == r["morceaux"]["avant"], (
        "ouvrir une porte a fait repeindre des morceaux : %s" % r["morceaux"]
    )
    assert r["regles"] == {"planque": False, "poste": False, "hopital": False, "logement": True}, (
        "les portes qui servent ne sont pas les bonnes : %s" % r["regles"]
    )
    assert r["commerce"] == {"jour": True, "nuit": False, "barLaNuit": True}, (
        "un commerce fermé ne doit laisser entrer personne — sauf le bar : %s" % r["commerce"]
    )
    s = r["sortie"]
    assert s["cacheAuDebut"] is True, "on le voit AVANT que la porte s'ouvre : %s" % s
    assert s["vuEnsuite"] is True and s["aLEcran"] is True, (
        "la sortie doit se voir, et en plein écran : %s" % s
    )
    assert s["avance"] > 8 and s["libre"] is True, "il doit sortir de la porte et reprendre sa vie : %s" % s
    assert r["entree"]["disparu"] >= 0, "personne n'entre nulle part : %s" % r["entree"]
    # ⚠️ Une porte ne s'ouvre jamais sur rien : il disparaît APRÈS l'ouverture.
    assert r["entree"]["ouvertAlors"] >= 0.9, (
        "il est entré par une porte encore fermée (%s) : une porte ne s'ouvre jamais sur rien"
        % r["entree"]["ouvertAlors"]
    )


def test_le_fondu_de_porte_noircit_avant_de_changer_de_scene(banc):
    """⚠️ Le defaut que Martin a nomme « la transition n'est pas juste » : la
    piece se chargeait PUIS le fondu partait de transparent. Sa premiere moitie
    noircissait donc sur la scene deja changee — on voyait la piece une image,
    l'ecran noircissait, il s'eclaircissait sur la meme piece. Ce test mesure la
    scene a CHAQUE image : aucune ne doit montrer la nouvelle avant le noir
    complet, et la porte doit s'entendre la, au noir."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const j = L.B.joueur, c = L.Monde.carte;
        const porte = c.portes.find(function (p) { return p.lieu === 'planque'; });
        j.x = porte.x * L.TT + 8; j.y = (porte.y + 1) * L.TT + 10;
        const villeW = c.w;
        // La porte s'entend-elle, et QUAND ?
        const sons = [];
        const vraiSon = L.Son.SFX.porte;
        L.Son.SFX.porte = function () { sons.push({ noir: L.B.transition ? L.B.transition.t : -1, dedans: !!L.B.interieur }); return vraiSon.apply(null, arguments); };
        L.Jeu.entrer(porte);
        const images = [];
        for (let i = 0; i < 120 && L.B.transition; i++) {
            o.frame(1);
            const tr = L.B.transition;
            // L'alpha du noir, comme le HUD le calcule : 0 -> 1, puis 1 -> 0.
            const alpha = tr ? (tr.t <= tr.ferme ? tr.t / tr.ferme : 1 - (tr.t - tr.ferme) / tr.ouvre) : 0;
            images.push({ alpha: Math.round(alpha * 1000) / 1000, w: L.Monde.carte.w, dedans: !!L.B.interieur });
        }
        const entree = images.length;
        // Et au retour : plus vif qu'a l'aller.
        L.Jeu.sortir();
        const sortie = o.fondu();
        return { villeW: villeW, images: images, entree: entree, sortie: sortie, sons: sons,
                 dedans: L.B.interieur, w: L.Monde.carte.w };
    }""")
    change = [i for i, im in enumerate(r["images"]) if im["dedans"]]
    assert change, "on n'est jamais entre"
    premiere = change[0]
    assert r["images"][premiere]["alpha"] == 1.0, (
        "la nouvelle scene se montre a %s de noir : le fondu clignote"
        % r["images"][premiere]["alpha"]
    )
    for im in r["images"][:premiere]:
        assert im["w"] == r["villeW"] and not im["dedans"], "la piece est chargee avant le noir"
        assert im["alpha"] < 1.0
    assert r["images"][-1]["alpha"] < 0.2, "le fondu ne finit pas en clair"
    assert r["sons"][0] == {"noir": premiere + 1, "dedans": True}, (
        "la porte doit s'entendre AU NOIR, a l'image du changement : %s" % r["sons"]
    )
    assert len(r["sons"]) == 2 and r["sons"][1]["dedans"] is False, (
        "la porte de sortie s'entend aussi au noir, une fois la rue revenue : %s" % r["sons"]
    )
    assert r["sortie"] < r["entree"], "sortir doit etre plus vif qu'entrer"
    assert 30 <= r["entree"] <= 90 and r["sortie"] >= 20, (
        "un fondu de porte se sent : ni un clignotement, ni une attente (%s, %s)"
        % (r["entree"], r["sortie"])
    )


def test_le_jeu_est_fige_pendant_un_fondu_de_porte(banc):
    """⚠️ La simulation continuait pendant le fondu : on pouvait sortir d'une
    piece et se faire renverser par un char qu'on n'a pas vu venir, sur un ecran
    noir ou l'on ne controle rien. Un menu fige deja tout ; une porte pareil."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const j = L.B.joueur, c = L.Monde.carte;
        const porte = c.portes.find(function (p) { return p.lieu === 'planque'; });
        j.x = porte.x * L.TT + 8; j.y = (porte.y + 1) * L.TT + 10;
        o.frame(2);
        // Un passant qui marche, un char qui roule : rien de tout ca ne doit
        // avancer d'un pixel pendant le noir.
        const passant = o.poser('flaneur', 24, 0);
        passant.etat = 'flane';
        const char = o.char('auto', -30, 0, 0);
        char.etat = 'roule'; char.vitesse = 3;
        j.vie = 60;
        const avant = { t: L.B.t, vie: j.vie, px: passant.x, py: passant.y, cx: char.x, heure: L.B.partie.heure };
        L.Jeu.entrer(porte);
        const images = o.fondu();
        const apres = { t: L.B.t, vie: j.vie, px: passant.x, py: passant.y, cx: char.x, heure: L.B.partie.heure };
        // Et une fois dedans, le jeu repart : le temps passe de nouveau.
        o.frame(5);
        return { avant: avant, apres: apres, images: images, repart: L.B.t - apres.t, dedans: !!L.B.interieur };
    }""")
    assert r["dedans"] is True and r["images"] > 20
    assert r["apres"]["t"] == r["avant"]["t"], "le temps de jeu a passe pendant le fondu"
    assert r["apres"]["heure"] == r["avant"]["heure"], "l'heure a avance pendant le fondu"
    assert r["apres"]["vie"] == r["avant"]["vie"], "le joueur a pris des coups pendant le fondu"
    assert r["apres"]["px"] == r["avant"]["px"] and r["apres"]["py"] == r["avant"]["py"], "un passant a marche pendant le fondu"
    assert r["apres"]["cx"] == r["avant"]["cx"], "un char a roule pendant le fondu"
    assert r["repart"] == 5, "le jeu n'est pas reparti apres le fondu"


def test_sortir_pendant_le_fondu_d_entree_ramene_devant_la_porte(banc):
    """⚠️ Le cas qui casse tout : ressortir alors que le fondu d'entree joue
    encore. La scene ne change qu'au noir — celui qui sort avant ne trouverait
    aucun interieur, la sortie serait refusee, et le joueur se reveillerait
    dedans sans l'avoir demande."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const j = L.B.joueur, c = L.Monde.carte;
        const porte = c.portes.find(function (p) { return p.lieu === 'planque'; });
        const x0 = porte.x * L.TT + 8, y0 = (porte.y + 1) * L.TT + 10;
        j.x = x0; j.y = y0;
        // Aller-retour normal, d'abord : on revient au pixel.
        o.entrer(porte);
        o.sortir();
        const normal = { x: j.x, y: j.y, dedans: L.B.interieur };
        // Puis on ressort AVANT le noir : trois images de fondu, et on repart.
        j.x = x0; j.y = y0;
        L.Jeu.entrer(porte);
        o.frame(3);
        const avantLeNoir = { dedans: !!L.B.interieur, fondu: !!L.B.transition };
        const sorti = L.Jeu.sortir();
        o.fondu();
        // L'elan qui reste au pas de la porte, avant que le jeu reprenne la main.
        const elan = { garde: Math.abs(j.vy) > 0, vers: j.vy > 0, face: j.face };
        // La camera ne saute pas : elle est deja posee quand le jeu repart.
        const cam = { x: L.B.cam.x, y: L.B.cam.y };
        o.frame(1);
        const bouge = Math.hypot(L.B.cam.x - cam.x, L.B.cam.y - cam.y);
        return { normal: normal, avantLeNoir: avantLeNoir, sorti: sorti, dedans: L.B.interieur,
                 x: j.x, y: j.y, x0: x0, y0: y0, bouge: bouge, elan: elan };
    }""")
    assert r["normal"]["dedans"] is None and (r["normal"]["x"], r["normal"]["y"]) == (r["x0"], r["y0"]), (
        "un aller-retour par la porte doit ramener a la tuile EXACTE"
    )
    assert r["avantLeNoir"] == {"dedans": False, "fondu": True}
    assert r["sorti"] is True, "sortir pendant le fondu d'entree a ete refuse"
    assert r["dedans"] is None, "on est reste dedans"
    assert (r["x"], r["y"]) == (r["x0"], r["y0"]), "on ne revient pas devant la porte"
    assert r["bouge"] < 2, "la camera saute a la premiere image jouable : %s px" % r["bouge"]
    assert r["elan"] == {"garde": True, "vers": True, "face": "bas"}, (
        "on sort d'une porte avec un reste d'elan vers la rue, pas d'un arret complet : %s" % r["elan"]
    )


def test_l_hopital_et_la_prison_passent_par_la_machine_des_portes(banc):
    """⚠️ Retour de Martin : « il faut corriger le fade out et in quand on va a
    l'hopital ou qu'on se fait enfermer. »

    Les quatre ellipses (hopital, prison, compagnie, coucher) etaient restees
    sur `Hud.fondu` + `setTimeoutJeu` : DEUX HORLOGES independantes, l'une dans
    le dessin, l'autre dans la mise a jour. Rien ne liait le changement de scene
    au noir — il tombait a 80 % d'alpha, donc a travers un voile transparent
    d'un cinquieme, et le texte s'ecrivait par-dessus la rue qu'on voyait
    encore, pendant que la ville continuait de tourner.

    Ce juge mesure, image par image, les trois choses en meme temps : l'alpha a
    l'instant OU l'on est teleporte, l'alpha a chaque fois que le texte se
    dessine, et le temps du monde pendant le noir."""
    r = banc(r"""function (L, o) {
        L.Jeu.commencer();
        const j = L.B.joueur;
        L.B.partie.argent = 400;
        // Ce que le texte du fondu voit du monde : on note l'alpha a chaque
        // fois qu'Atlas l'ecrit (le banc ne garde aucun pixel). ⚠️ On guette
        // « REVEIL », pas « HOPITAL » : la facture passe aussi par un message
        // du HUD, et lui a le droit de s'ecrire sur la rue.
        const ecrits = [];
        const vraiTexte = L.Atlas.texte;
        function alpha() {
            const tr = L.B.transition;
            if (!tr) return null;
            const noir = tr.ferme + tr.tient;
            return tr.t <= tr.ferme ? tr.t / tr.ferme
                 : tr.t <= noir ? 1
                 : 1 - (tr.t - noir) / tr.ouvre;
        }
        L.Atlas.texte = function (ctx, s, x, y, c, e) {
            if (String(s).indexOf('RÉVEIL') >= 0) ecrits.push(alpha());
            return vraiTexte.apply(null, arguments);
        };
        // Un passant et un char : rien de tout ca ne doit avancer dans le noir.
        const passant = o.poser('flaneur', 40, 0);
        passant.etat = 'flane';
        const char = o.char('auto', -40, 0, 0);
        char.etat = 'roule'; char.vitesse = 3;
        const avant = { t: L.B.t, heure: L.B.partie.heure, px: passant.x, cx: char.x, x: j.x, y: j.y };
        L.Entites.blesser(j, 9999, null, {});
        const lance = { fondu: !!L.B.transition, tient: L.B.transition && L.B.transition.tient,
                        vivant: j.vivant, dejaLoin: Math.hypot(j.x - avant.x, j.y - avant.y) };
        // Image par image : ou est le joueur, et a quel alpha ?
        const images = [];
        for (let i = 0; i < 300 && L.B.transition; i++) {
            o.frame(1);
            images.push({ a: Math.round((alpha() === null ? 0 : alpha()) * 1000) / 1000,
                          loin: Math.round(Math.hypot(j.x - avant.x, j.y - avant.y)) });
        }
        L.Atlas.texte = vraiTexte;
        const apres = { t: L.B.t, heure: L.B.partie.heure, px: passant.x, cx: char.x };
        o.frame(5);
        // ⚠️ On arrive DANS la piece de l'hopital, couche : on juge ou sa porte mene.
        const hopital = L.B.exterieur.carte.points.find(function (p) { return p.slug === 'hopital'; });
        return { lance: lance, images: images, ecrits: ecrits, avant: avant, apres: apres,
                 repart: L.B.t - apres.t, vie: j.vie, max: j.vieMax,
                 argent: L.B.partie.argent, etat: L.B.etat,
                 piece: L.B.interieur && L.B.interieur.slug,
                 arrive: Math.hypot(L.B.exterieur.x - hopital.x * L.TT, L.B.exterieur.y - hopital.y * L.TT) };
    }""")
    assert r["lance"]["fondu"] is True, "tomber doit lancer un fondu de `Jeu.transiter`"
    assert r["lance"]["tient"] > 0, "une ellipse tient le noir : c'est la que le temps passe"
    assert r["lance"]["dejaLoin"] == 0, "le joueur est parti a l'hopital AVANT que le noir commence"
    change = [i for i, im in enumerate(r["images"]) if im["loin"] > 8]
    assert change, "on ne s'est jamais reveille a l'hopital"
    assert r["images"][change[0]]["a"] == 1.0, (
        "la teleportation se voit a %s de noir : c'est le defaut de l'ancien fondu"
        % r["images"][change[0]]["a"]
    )
    assert r["ecrits"], "le fondu doit dire ou l'on se reveille et ce que ca coute"
    assert all(a == 1.0 for a in r["ecrits"]), (
        "le texte s'ecrit sur une rue qu'on voit encore (alphas %s)" % sorted(set(r["ecrits"]))
    )
    assert r["images"][-1]["a"] < 0.2, "le fondu ne finit pas en clair"
    assert 120 <= len(r["images"]) <= 200, (
        "une ellipse d'hopital se sent : ni un clignotement, ni une attente (%s images)"
        % len(r["images"])
    )
    # ⚠️ La ville est FIGEE pendant : on gisait a 1 PV au milieu de la rue
    # pendant deux secondes et demie, et un char pouvait repasser dessus.
    assert r["apres"]["t"] == r["avant"]["t"], "le temps de jeu a passe pendant le fondu"
    assert r["apres"]["heure"] == r["avant"]["heure"], "l'heure a avance pendant le fondu"
    assert r["apres"]["px"] == r["avant"]["px"], "un passant a marche pendant le fondu"
    assert r["apres"]["cx"] == r["avant"]["cx"], "un char a roule pendant le fondu"
    assert r["repart"] == 5, "le jeu n'est pas reparti apres le fondu"
    assert r["vie"] == r["max"] and r["piece"] == "hopital" and r["arrive"] < 48
    # ⚠️ Venus de `test_l_hopital_ramasse_le_joueur_et_le_facture` (vague C, 28 sept. 2026),
    # qui refaisait la même chute sans regarder le fondu : on tombe VIVANT (le fondu
    # d'abord, le réveil ensuite), l'hôpital FACTURE, et on repart en jeu.
    assert r["lance"]["vivant"] is True, "le joueur est mort au lieu de tomber : %s" % r["lance"]
    assert r["argent"] < 400, "l'hopital n'a pas facture"
    assert r["etat"] == "jeu", "on ne repart pas en jeu apres l'hopital : %s" % r["etat"]


def test_se_faire_arreter_pendant_le_fondu_de_l_hopital_n_empile_pas_deux_noirs(banc):
    """⚠️ Le cas qui casse tout, version ellipse : deux fondus en meme temps.

    C'est celui que `finirTransition()` reglait deja pour les portes — passer
    une porte pendant le noircissement d'une autre. Depuis que l'hopital et la
    prison ont la meme machine, la regle doit valoir pour eux : le fondu qui
    joue finit tout de suite (sa scene change, une fois), et le nouveau repart
    du clair. Sinon on se reveille a l'hopital APRES etre sorti de prison."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const j = L.B.joueur;
        L.B.partie.argent = 900;
        L.Entites.blesser(j, 9999, null, {});
        o.frame(10);                                  // en plein noircissement
        const pendant = { t: L.B.transition.t, fait: L.B.transition.fait };
        L.B.recherche.etoiles = 3;
        L.Missions.prison(null);
        const repart = { t: L.B.transition.t, fait: L.B.transition.fait };
        // ⚠️ Le reveil fini, on est couche dans un lit de l'hopital — et c'est de
        // LA que la prison doit nous sortir, pas nous laisser dans la piece.
        const auHopital = !!L.B.interieur && L.B.interieur.slug === 'hopital' && !!j.alite;
        o.fondu();
        const poste = L.Monde.carte.points.find(function (p) { return p.slug === 'poste'; });
        return { pendant: pendant, repart: repart, auHopital: auHopital,
                 auPoste: Math.hypot(j.x - poste.x * L.TT, j.y - poste.y * L.TT),
                 fondus: !!L.B.transition, arrete: !!j.arrete, vie: j.vie, max: j.vieMax,
                 dehors: !L.B.interieur && !L.B.exterieur, alite: !!j.alite };
    }""")
    assert r["pendant"]["fait"] is False and r["pendant"]["t"] > 0, "le premier fondu doit etre en cours"
    assert r["auHopital"] is True, (
        "le fondu interrompu doit avoir fait ce qu'il promettait (le reveil a l'hopital), une fois"
    )
    assert r["repart"] == {"t": 0, "fait": False}, (
        "le fondu de la prison repart du clair : %s" % r["repart"]
    )
    assert r["fondus"] is False, "il reste un fondu ouvert"
    assert r["auPoste"] < 48 and r["arrete"] is False and r["vie"] == r["max"]
    assert r["dehors"] is True and r["alite"] is False, (
        "sorti de prison encore couche, ou encore dans la piece de l'hopital : %s" % r
    )


def test_on_entre_dans_la_planque_et_on_en_ressort(banc):
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const j = L.B.joueur, c = L.Monde.carte;
        const porte = c.portes.find(function (p) { return p.lieu === 'planque'; });
        j.x = porte.x * L.TT + 8; j.y = (porte.y + 1) * L.TT + 10;
        // ⚠️ On regarde la porte : dehors, ENTRER n'agit que sur ce qu'on regarde (test_regard_js.py).
        L.Entites.regarder(j, 0, -1);
        // Ce qui ne bouge pas : ni les pietons (oublies quand on s'eloigne), ni les
        // chars, ni les armes de fortune (semees au fil des images).
        // ⚠️ `bete` et `ballon` sont de la VIE DE RUE, pas du mobilier : un goéland
        // qui se pose pendant qu'on est dans la planque n'est pas « la ville qui
        // est entrée avec nous ». Ce juge dit que le mobilier fixe revient tel
        // quel — on nomme donc ce qui va et vient, comme les piétons et les chars.
        const fixes = function () { return L.B.entites.filter(function (e) { return ['pieton', 'vehicule', 'ramassage', 'projectile', 'bete', 'ballon'].indexOf(e.type) < 0; }).length; };
        const dehors = { entites: fixes(), w: c.w };
        o.tape('KeyE', 3);
        // La porte passe par un fondu : la piece se charge AU NOIR, pas au clic.
        const pendant = { interieur: L.B.interieur, t: L.B.t, fondu: !!L.B.transition };
        o.fondu();
        const dedans = { interieur: L.B.interieur ? L.B.interieur.slug : null, w: L.Monde.carte.w, entites: L.B.entites.length,
                         nuit: L.Monde.ambiance().alpha, cam: L.B.cam.x < 0,
                         sol: L.Monde.solidite(Math.floor(j.x / L.TT), Math.floor(j.y / L.TT)),
                         invite: (function () { j.x = L.B.interieur.sortie.x * L.TT + 8; j.y = (L.B.interieur.sortie.y - 1) * L.TT + 8; L.Missions.majInvite(j); return L.B.invite; })() };
        o.tape('KeyE', 3);
        o.fondu();
        return { dehors: dehors, pendant: pendant, dedans: dedans, apres: { interieur: L.B.interieur, w: L.Monde.carte.w, entites: fixes(),
                 pres: Math.hypot(j.x - porte.x * L.TT - 8, j.y - (porte.y + 1) * L.TT - 10) } };
    }""")
    assert r["pendant"]["fondu"] is True, "passer une porte doit lancer un fondu"
    assert r["pendant"]["interieur"] is None, "la piece est chargee AVANT le noir : le fondu clignote"
    assert r["dedans"]["interieur"] == "planque" and r["dedans"]["w"] < r["dehors"]["w"]
    assert r["dedans"]["entites"] == 1, "la ville est entree avec nous"
    assert r["dedans"]["nuit"] == 0 and r["dedans"]["cam"] is True, "une piece se centre et n'a pas de nuit"
    assert r["dedans"]["sol"] == 0 and r["dedans"]["invite"] == "SORTIR"
    assert r["apres"]["interieur"] is None and r["apres"]["w"] == r["dehors"]["w"]
    assert r["apres"]["entites"] == r["dehors"]["entites"], "la ville n'est pas revenue telle quelle"
    assert r["apres"]["pres"] < 20, "on doit ressortir devant la porte"


# --- Les murs d'une pièce, harmonisés (docs/jalons/des-interieurs-fideles-a-l-exterieur.md) -----

def test_tous_les_murs_d_une_piece_sont_du_meme_platre(banc):
    """Martin (29 sept. 2026) : « les portes et murs des portes intérieur doivent avoir des murs harmonisés ».
    Le mur `B` d'une pièce se peignait en toit de tôle (neigeux l'hiver), la fenêtre `W` et la porte `D` en
    façade de brique, comme vues de la rue. ⚠️ Dans CHAQUE pièce de la ville qui n'a pas ses propres
    matériaux : ses trois glyphes de mur vont au même peintre, et il existe — le plâtre `@piece`, ou l'habit du
    logement selon sa façade (`test_habit_du_logement_js.py` : le pauvre, le cossu, la villa)."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const c = L.Monde.carte, vues = {}, fautes = [];
        for (const porte of c.portes) {
            const piece = c.def.interieurs[porte.interieur];
            if (!piece || vues[porte.interieur] || piece.materiaux) continue;
            vues[porte.interieur] = true;
            o.entrer(porte);
            const k = L.Monde.carte, mats = k.materiaux || {};
            for (let y = 0; y < k.h; y++) for (let x = 0; x < k.w; x++) {
                const g = k.sol[y][x];
                if ('BWD'.indexOf(g) < 0) continue;
                if (!mats[g] || mats[g] !== mats.B || mats.B !== mats.W || mats.W !== mats.D || !L.TUILES[g + '@' + mats[g]]) {
                    fautes.push(porte.interieur + ' ' + g + ' ' + x + ',' + y);
                }
            }
            o.sortir();
        }
        return { pieces: Object.keys(vues).length, fautes: fautes.slice(0, 5),
                 dehors: L.Monde.carte.materiaux ? Object.keys(L.Monde.carte.materiaux) : [] };
    }""")
    assert r["pieces"] >= 60, r
    assert not r["fautes"], r["fautes"]
    assert r["dehors"] == [], "la ville a pris les murs d'une pièce en ressortant"


def test_la_fenetre_et_la_porte_se_peignent_sur_le_platre_du_mur(banc):
    """Le même mur : la fenêtre et la porte d'une pièce commencent par le plâtre plein du mur `B@piece`, pas
    par la brique de la façade (`W` et `D` de la ville, eux, gardent la leur)."""
    r = banc("""function (L, o) {
        function premier(nom, v) {
            let style = null, pris = null;
            const ctx = { fillRect: function (x, y, w, h) { if (!pris && w >= 16 && h >= 16) pris = style; } };
            Object.defineProperty(ctx, 'fillStyle', { get: function () { return style; }, set: function (s) { style = s; } });
            L.TUILES[nom](ctx, v, 16);
            return pris;
        }
        return { mur: premier('B@piece', 5), fenetre: premier('W@piece', 5), porte: premier('D@piece', 5),
                 facade: premier('W', 5) };
    }""")
    assert r["mur"] and r["fenetre"] == r["mur"] and r["porte"] == r["mur"], r
    assert r["facade"] != r["mur"], "la façade de la rue a pris le plâtre du dedans"
