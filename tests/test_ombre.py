"""L'ombre au sol des véhicules — le filet de la refonte.

⚠️ **Elle existe dès maintenant, avant que les dessins changent**, et c'est
voulu. Le jour où le char sera dessiné de profil, il ne montrera plus ses 28 px
de longueur en s'éloignant : un objet de 14 px de large, et son encombrement
disparaît de l'écran. Or se garer dans une case, juger l'espace entre deux
chars, reculer dans une ruelle, tout ça se joue **à l'œil**. L'ombre rend à
l'œil la longueur que le dessin ne montrera plus.

La fiche le dit dans ces termes : « l'ombre d'abord — c'est elle le filet, et
elle se mesure ». Ces juges sont cette mesure.
"""

import pytest

from app import vehicules


def test_la_fiche_de_l_ombre_tient_ensemble():
    """⚠️ Les nombres étaient écrits en dur dans `dessinerUn` (0,30 / 0,14 /
    0,35 / 30). Une ombre qu'on ne peut pas régler depuis la fiche est un dessin
    qui décide de lui-même comment la ville est éclairée."""
    o = vehicules.OMBRE
    assert 0 < o["part"] < 1, "une ombre opaque est un trou, une ombre nulle n'existe pas"
    assert 0 < o["part_en_vol"] < o["part"], (
        "en montant, l'ombre disparaîtrait complètement ou ne pâlirait pas du tout"
    )
    assert 0 < o["retrait_max"] < 1, "elle s'annulerait en l'air, ou ne rétrécirait jamais"
    assert o["ecart_par_z"] > 0 and o["z_haut"] > 0
    # ⚠️ Au sol elle tombe À L'EST et pas au sud : rien ne dépasse devant les
    # roues d'un char posé — ce qui s'échappe vers le sud-est, c'est l'altitude.
    assert o["ecart_est"] > 0 and o["ecart_sud"] == 0
    assert 0 < o["profondeur"] < 1, (
        "le sol se voit de biais : l'axe nord-sud est écrasé, sinon un char qui "
        "roule vers le nord traîne toute sa longueur en ombre devant lui"
    )


def test_la_fiche_descend_au_navigateur():
    """⚠️ Le défaut qui revient : une fiche que le navigateur ne lisait pas."""
    assert vehicules.exporter_conduite()["ombre"] == vehicules.OMBRE


# --- L'ombre en jeu ----------------------------------------------------------

#: ⚠️ **UN SEUL BANC POUR TOUT CE QUI SUIT** (vague C, 28 sept. 2026). Les six
#: juges en jeu refaisaient chacun la même mise en place pour lire `ombreDe`,
#: `SPRITES` et la trace de `dessinerUn` — des lectures qui ne changent rien au
#: monde (chaque char posé est retiré). La fixture rend tout, chaque juge garde
#: son nom, sa règle et ses messages. Le dernier scénario (`peinte`) est venu de
#: `test_moteur_js::test_l_ombre_d_un_saut_raconte_la_hauteur` : c'est le seul
#: endroit où l'ombre est jugée TELLE QU'ELLE SE PEINT.
DECOR = """
    L.Jeu.commencer();
    L.graine(29);
    const j = L.B.joueur;
    const d = o.ligneDroite();
    j.x = d.x; j.y = d.y; L.Monde.centrerCamera(j.x, j.y);
"""


@pytest.fixture(scope="module")
def ombres(banc):
    return banc("""function (L, o) {
        %s
        const out = {};

        // test_l_ombre_est_tournee_comme_le_char
        (function () {
            const v = o.char('autobus', 0, 0, 0);
            const droit = L.Vehicules.ombreDe(v).angle;
            v.angle = Math.PI / 4;
            const biais = L.Vehicules.ombreDe(v).angle;
            v.angle = -1.2;
            out.tournee = { droit: droit, biais: biais, negatif: L.Vehicules.ombreDe(v).angle };
            L.Entites.retirer(v);
        })();

        // test_chaque_vehicule_a_l_empreinte_de_sa_fiche
        (function () {
            const r = {};
            L.B.defs.vehicules.forEach(function (def) {
                const v = o.char(def.slug, 0, 0, 0);
                if (!v) return;
                v.z = 0;
                const ombre = L.Vehicules.ombreDe(v);
                r[def.slug] = ombre ? [ombre.l, ombre.h, def.longueur, def.largeur, ombre.part] : null;
                L.Entites.retirer(v);
            });
            out.empreintes = { vehicules: r, part: L.B.defs.conduite.ombre.part };
        })();

        // test_en_montant_elle_retrecit_s_ecarte_et_palit
        (function () {
            const v = o.char('auto', 0, 0, 0);
            const mesure = function (z) {
                v.z = z;
                const q = L.Vehicules.ombreDe(v);
                return { l: q.l, h: q.h, dx: +(q.x - v.x).toFixed(2), part: +q.part.toFixed(3) };
            };
            out.montee = { sol: mesure(0), un: mesure(1), mi: mesure(15), haut: mesure(40) };
            L.Entites.retirer(v);
        })();

        // test_le_sol_se_voit_du_meme_biais_sous_un_char_et_dans_son_dessin
        (function () {
            const biais = {};
            Object.keys(L.SPRITES).forEach(function (s) { if (L.SPRITES[s].machine) biais[s] = L.SPRITES[s].machine.profondeur; });
            out.biais = { biais: biais, ombre: L.B.defs.conduite.ombre.profondeur };
        })();

        // test_l_ombre_ne_traine_pas_devant_un_char_qui_roule_vers_le_nord
        // (⚠️ il jouait sur la graine 31 : `ombreDe` et les dessins ne tirent aucun dé,
        // la graine ne changeait que la ville autour, qu'il ne regardait pas.)
        (function () {
            const r = {};
            L.B.defs.vehicules.forEach(function (def) {
                const v = o.char(def.slug, 0, 0, 0);
                if (!v) return;
                // ⚠️ Chaque véhicule a son dessin de profil (le bateau compris) : un
                // char sans flanc rend `hauteur: null`, et c'est un rouge, pas un saut.
                const sprite = L.SPRITES[v.sprite];
                const cuit = sprite ? L.Atlas.cuire(v.sprite, sprite, v.swaps) : null;
                // Ce que le FLANC monte au-dessus de la ligne de sol.
                let hauteur = null;
                if (cuit && sprite.poses && sprite.poses.cote) {
                    const g = sprite.poses.cote[0];
                    let premier = g.length;
                    for (let y = 0; y < g.length; y++) if (/[^.]/.test(g[y])) { premier = y; break; }
                    hauteur = cuit.ancre[1] - premier + 1;
                }
                const caps = {};
                [['est', 0], ['nord', -Math.PI / 2], ['sud', Math.PI / 2], ['biais', Math.PI / 4]].forEach(function (c) {
                    v.angle = c[1];
                    const q = L.Vehicules.ombreDe(v);
                    // Le point le plus au sud de l'empreinte tournee PUIS ecrasee.
                    const demi = (Math.abs(Math.sin(q.angle)) * q.l + Math.abs(Math.cos(q.angle)) * q.h) / 2;
                    caps[c[0]] = +((q.y - v.y) + demi * q.profondeur).toFixed(2);
                });
                r[def.slug] = { caps: caps, hauteur: hauteur, longueur: def.longueur };
                L.Entites.retirer(v);
            });
            out.nord = r;
        })();

        // test_l_ombre_se_peint_sous_le_char_des_le_premier_pixel_de_vol
        // ⚠️ La TRACE dit ce qui est vraiment peint a l'ecran : une regle qui ne se
        // dessinerait pas ne vaudrait rien.
        (function () {
            function ombre(slug, z) {
                const v = o.char(slug, 0, 0, 0);
                v.z = z;
                const ctx = L.Base.ecran();
                ctx.traces = [];
                L.Vehicules.dessinerUn(ctx, v, 0, 0);
                L.Entites.retirer(v);
                // L'ombre est le seul rectangle plein : le char, lui, est une image.
                const t = ctx.traces[0];
                return t ? { l: t[2], h: t[3], couleur: t[4] } : null;
            }
            out.peinte = {
                auSol: ombre('auto', 0),
                basse: ombre('auto', 1),
                haute: ombre('auto', 28),
                moto: ombre('moto', 10),
                autobus: ombre('autobus', 10),
            };
        })();
        return out;
    }""" % DECOR)


def test_l_ombre_est_tournee_comme_le_char(ombres):
    """⚠️ Une tache alignée sur les axes ne dit rien de la place qu'il prend :
    c'est justement l'encombrement qu'on rend à l'œil, et un autobus en travers
    de la rue n'a pas la même empreinte qu'un autobus dans sa voie."""
    r = ombres["tournee"]
    assert r["droit"] == 0
    assert abs(r["biais"] - 0.7853981633974483) < 1e-9, "l'ombre ne tourne pas : %s" % r
    assert abs(r["negatif"] + 1.2) < 1e-9, r


def test_chaque_vehicule_a_l_empreinte_de_sa_fiche(ombres):
    """⚠️ C'est la MÊME empreinte que la physique : ce qu'on voit est
    exactement ce qui bloque. Une ombre de taille unique referait le défaut
    qu'on vient de réparer en vol — la même tache pour une moto et pour un
    autobus de 48 px.

    ⚠️ **TOUT LE TEMPS, pas seulement en vol** (ce que tenait
    `test_un_char_pose_au_sol_a_son_ombre`, fondu ici le 28 sept. 2026 : il le
    vérifiait pour l'auto seule, on le vérifie pour chacun). C'était la règle
    d'avant, et c'est elle qu'on change : un char au sol n'avait aucune ombre,
    donc rien ne disait sa place sur l'asphalte."""
    r, part = ombres["empreintes"]["vehicules"], ombres["empreintes"]["part"]
    assert len(r) >= 8, "le décor du juge est faux : trop peu de véhicules (%s)" % list(r)
    sans = sorted(slug for slug, m in r.items() if m is None)
    assert sans == [], f"ces chars au sol n'ont pas d'ombre : {sans}"
    tailles = set()
    for slug, (large, haut, longueur, largeur, sa_part) in r.items():
        assert large == longueur and haut == largeur, (
            f"{slug} : ombre {large}x{haut}, fiche {longueur}x{largeur}"
        )
        assert abs(sa_part - part) < 1e-9, f"{slug} : son ombre au sol ne lit pas la fiche ({sa_part} contre {part})"
        tailles.add((large, haut))
    assert len(tailles) >= 5, (
        "toutes les ombres font la même taille : on a refait la tache unique (%s)" % tailles
    )


def test_en_montant_elle_retrecit_s_ecarte_et_palit(ombres):
    """C'est elle qui RACONTE la hauteur — et c'est pour ça qu'un saut se voit.
    ⚠️ Le juge mesure les trois ensemble : une ombre qui rétrécit sans s'écarter
    a l'air d'un char qui s'éloigne, pas d'un char qui décolle."""
    r = ombres["montee"]
    sol, un, mi, haut = r["sol"], r["un"], r["mi"], r["haut"]
    assert haut["l"] < mi["l"] < sol["l"], "elle ne rétrécit pas : %s" % r
    assert haut["dx"] > mi["dx"] > sol["dx"], "elle ne s'écarte pas : %s" % r
    assert haut["part"] < mi["part"] < sol["part"], "elle ne pâlit pas : %s" % r
    # ⚠️ Et jamais au-delà du plafond : à cinquante pixels d'altitude elle ne
    # doit pas devenir un point, ni disparaître.
    assert haut["l"] >= 4 and haut["part"] > 0, "elle s'annule en l'air : %s" % r
    # ⚠️ Venus de `test_moteur_js::test_l_ombre_d_un_saut_raconte_la_hauteur` : au
    # sol, l'ombre est SOUS le char, pas détachée de lui — c'est l'écart qui raconte
    # l'altitude, et à zéro il doit être nul ou presque ; et elle bouge dès le
    # premier pixel de vol, pas au-dessus d'un seuil.
    assert sol["dx"] <= 2, "l'ombre d'un char posé au sol est détachée de lui : %s" % r
    assert un["dx"] > sol["dx"], "l'ombre ne bouge pas dès le premier pixel de vol : %s" % r


def test_l_ombre_se_peint_sous_le_char_des_le_premier_pixel_de_vol(ombres):
    """⚠️ Bug de Martin : « s'il marche, qu'on voie une ombre pour bien imager
    le saut. » Elle existait — un rectangle de 20 x 10 FIXE, posé seulement
    au-dessus de `z > 2` : la même tache pour une moto et pour un autobus de
    48 px, qui ne rétrécissait pas. Les juges du dessus lisent `ombreDe` ; celui-ci
    lit ce que `dessinerUn` PEINT (venu de `test_moteur_js`, 28 sept. 2026)."""
    r = ombres["peinte"]
    assert r["auSol"], "un char posé au sol n'a plus d'ombre du tout"
    assert r["basse"], "une ombre qui n'arrive qu'au-dessus d'un seuil rate le début du vol"
    assert r["haute"]["l"] < r["basse"]["l"], "l'ombre ne rétrécit pas quand le char monte"
    assert r["autobus"]["l"] > r["moto"]["l"], \
        "l'autobus fait 48 px et la moto 20 : leur ombre ne peut pas être la même"


def test_le_sol_se_voit_du_meme_biais_sous_un_char_et_dans_son_dessin(ombres):
    """⚠️ **Un seul biais pour un char : celui de son dessin.** Ce juge comparait
    l'ombre d'un char à celle d'un passant (`DECORS.ombre`, 12 × 6 : le sol
    écrasé de moitié) — c'était la seule référence le jour où le char était une
    élévation plate. Depuis que le parc est EN VOLUME, la référence est le char
    lui-même : son dessin se projette avec un biais (`machine.profondeur`), et
    son ombre doit poser l'empreinte sur ce MÊME sol, sinon elle dépasse de son
    nez ou reste en deçà de son pare-chocs.

    ⚠️ Et le parc a quitté le biais du passant (16 sept. 2026, retour de Martin :
    « oui plus long ») : à 0,5, une berline vue de dos occupait 21 rangées pour
    28 px de long ; à 0,75, sa longueur. L'ombre d'un passant, elle, reste une
    tache sous ses pieds — un corps rond, pas une empreinte."""
    r = ombres["biais"]
    assert len(r["biais"]) >= 12, "le décor du juge est faux : %s" % r
    autres = {s: k for s, k in r["biais"].items() if abs(k - r["ombre"]) >= 0.01}
    assert autres == {}, f"ces chars ne posent pas leur ombre sur le sol de leur dessin ({r['ombre']}) : {autres}"


def test_l_ombre_ne_traine_pas_devant_un_char_qui_roule_vers_le_nord(ombres):
    """⚠️ **Le retour de Martin, mesuré.** Un char debout qui roule vers le nord
    montre 16 px de large et 11 px de haut ; son empreinte, elle, fait 28 px de
    long. À plat, l'ombre débordait de **quinze** pixels devant ses roues — plus
    que le char n'est haut — et on la lisait comme une remorque.

    La règle, et elle vaut pour tous les caps : **une ombre ne dépasse jamais
    la ligne de sol de plus que la hauteur du dessin qui la jette.**

    ⚠️ Cette hauteur se mesure sur le dessin DE PROFIL, pas sur l'ancre. Depuis
    la vue plongeante (15 sept. 2026), la toile monte jusqu'à la LONGUEUR du
    char pour porter sa pose de dos, et l'ancre avec elle : la prendre pour la
    hauteur du char relâcherait la borne de vingt pixels sans que personne ne
    le dise. C'est le flanc qui dit ce qu'un char a de haut."""
    r = ombres["nord"]
    assert len(r) >= 8, "le décor du juge est faux : trop peu de véhicules (%s)" % list(r)
    # ⚠️ Plus de saut : le juge passait par-dessus les sprites « en rotations »,
    # un champ qu'aucun dessin ne porte — il ne sautait rien, et un char sans
    # dessin de profil aurait glissé dehors sans un mot.
    sans_flanc = sorted(slug for slug, m in r.items() if m["hauteur"] is None)
    assert sans_flanc == [], f"ces véhicules n'ont pas de dessin de profil à mesurer : {sans_flanc}"
    for slug, m in r.items():
        for cap, sous in m["caps"].items():
            assert sous <= m["hauteur"], (
                f"{slug} vers le {cap} : l'ombre traîne {sous} px sous ses roues, "
                f"et le dessin n'est haut que de {m['hauteur']} px"
            )
