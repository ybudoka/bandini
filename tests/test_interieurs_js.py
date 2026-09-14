"""Les interieurs vus du jeu : on entre, il y a du monde, et les comptoirs servent.

⚠️ Le juge qui compte le plus est le premier : `carte.py` declare des POINTS
d'action dans chaque piece, et `missions.js` doit savoir quoi en faire. Les deux
listes vivent dans deux langages et deux fichiers ; sans ce test, on dessine un
comptoir a Montreal et on l'oublie a Quebec — c'est exactement comme ca que
« guichet », « casier » et « sortie_prison » etaient devenus des comptoirs morts
qu'on touchait pour lire « PLUS TARD ».
"""

import json

from app import carte

#: Les points qui ne passent PAS par un menu : ils agissent tout de suite.
SANS_MENU = ("sergent", "contact", "escalier", "fouiller")

#: ⚠️ Les comptoirs encore en chantier, et le jalon qui les doit. La liste est
#: volontairement penible a garder : chaque entree doit encore exister dans une
#: piece (sinon ce test rougit), et le jour ou M9 pose son menu, on l'enleve.
#: C'est la seule facon honnete d'avoir un comptoir dessine avant son menu —
#: sans elle, on exempterait par habitude et « guichet » renaîtrait.
#: Vide depuis le 13 sept. 2026 : le lot de la fourriere a recu son menu.
EN_CHANTIER: dict[str, str] = {}

TYPES = sorted({p["type"] for piece in carte.INTERIEURS.values() for p in piece["points"]})


def test_chaque_comptoir_dessine_est_servi_par_le_jeu(banc):
    """⚠️ LE contrat entre `carte.INTERIEURS` et `missions.js`. Un type de point
    qui n'a ni libelle ni menu est une porte qu'on ouvre pour rien."""
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
        const porte = c.portes.find(function (p) { return p.nom && p.interieur !== 'logement'; });
        j.x = porte.x * L.TT + 8; j.y = (porte.y + 1) * L.TT + 10;
        L.Missions.majInvite(j);
        const invite = L.B.invite;
        o.entrer(porte);
        const gens = L.B.entites.filter(function (e) { return e.type === 'pieton'; });
        const commis = gens.filter(function (e) { return e.arch === 'commis'; });
        const dedans = { nom: L.B.interieur.nom, slug: L.B.interieur.slug, gens: gens.length,
                         commis: commis.length, poste: commis.length ? !!commis[0].poste : false,
                         points: L.B.interieur.points.length };
        o.sortir();
        return { invite: invite, porte: porte, dedans: dedans,
                 dehors: L.B.entites.filter(function (e) { return e.arch === 'commis'; }).length };
    }""")
    assert r["invite"] == "ENTRER"
    assert r["dedans"]["nom"] == r["porte"]["nom"], "la piece n'a pas pris le nom de l'enseigne"
    assert r["dedans"]["slug"].startswith("boutique_")
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
        const porte = c.portes.find(function (p) { return p.interieur === 'boutique_bouffe'; });
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
        const porte = c.portes.find(function (p) { return p.interieur === 'logement'; });
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
        L.Missions.utiliserPoint(j);
        o.fondu();
        const revenu = L.B.interieur.slug;
        o.sortir();
        return { bas: bas, invite: invite, haut: haut, revenu: revenu,
                 sorti: L.B.interieur, pres: Math.hypot(j.x - porte.x * L.TT - 8, j.y - (porte.y + 1) * L.TT - 10) };
    }""")
    assert r["bas"]["slug"] == "logement" and r["bas"]["dehors"] is True
    assert r["invite"] == "MONTER"
    assert r["haut"]["slug"] == "logement_haut", "l'escalier n'a pas change de plancher"
    assert r["haut"]["dehors"] is True, "monter a oublie par ou l'on est entre"
    assert r["haut"]["sol"] != 1, "on arrive dans un mur"
    assert r["revenu"] == "logement", "on reste pris en haut"
    assert r["sorti"] is None and r["pres"] < 20, "on ressort par la porte d'en bas"


def test_les_tiroirs_d_un_logement_ne_se_fouillent_qu_une_fois(banc, paquet):
    tarifs = paquet["economie"]["tarifs"]
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const j = L.B.joueur, c = L.Monde.carte;
        const portes = c.portes.filter(function (p) { return p.interieur === 'logement'; });
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
        const un = fouiller(portes[0]);
        const encore = fouiller(portes[0]);
        const autre = fouiller(portes[1]);
        return { un: un, encore: encore.gain, autre: autre.gain, adresses: portes.length };
    }""")
    assert r["adresses"] >= 2, "il faut deux logements pour juger"
    assert r["un"]["invite"] == "FOUILLER"
    assert tarifs["fouille_min"] <= r["un"]["gain"] <= tarifs["fouille_max"]
    assert r["encore"] == 0, "les memes tiroirs paient deux fois"
    assert r["autre"] > 0, "une autre adresse doit payer"


def test_le_barbier_change_la_tete_et_fait_oublier_la_tienne(banc, paquet):
    coupe = paquet["economie"]["tarifs"]["coupe"]
    couleur = paquet["coiffures"][1]["couleur"]
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const j = L.B.joueur, c = L.Monde.carte;
        const porte = c.portes.find(function (p) { return p.interieur === 'boutique_service'; });
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
