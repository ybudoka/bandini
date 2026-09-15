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

DECOR = """
    L.Jeu.commencer();
    L.graine(29);
    const j = L.B.joueur;
    const d = o.ligneDroite();
    j.x = d.x; j.y = d.y; L.Monde.centrerCamera(j.x, j.y);
"""


def test_un_char_pose_au_sol_a_son_ombre(banc):
    """⚠️ TOUT LE TEMPS, pas seulement en vol. C'était la règle d'avant, et
    c'est elle qu'on change : un char au sol n'avait aucune ombre, donc rien ne
    disait sa place sur l'asphalte."""
    r = banc("""function (L, o) {
        %s
        const v = o.char('auto', 0, 0, 0);
        v.z = 0;
        const ombre = L.Vehicules.ombreDe(v);
        return { ombre: ombre, longueur: v.def.longueur, largeur: v.def.largeur,
                 part: L.B.defs.conduite.ombre.part };
    }""" % DECOR)
    assert r["ombre"] is not None, "un char au sol n'a pas d'ombre : %s" % r
    assert r["ombre"]["l"] == r["longueur"], (
        "l'ombre ne fait pas la longueur du catalogue : %s" % r
    )
    assert r["ombre"]["h"] == r["largeur"], (
        "l'ombre ne fait pas la largeur du catalogue : %s" % r
    )
    assert abs(r["ombre"]["part"] - r["part"]) < 1e-9, "elle ne lit pas la fiche : %s" % r


def test_l_ombre_est_tournee_comme_le_char(banc):
    """⚠️ Une tache alignée sur les axes ne dit rien de la place qu'il prend :
    c'est justement l'encombrement qu'on rend à l'œil, et un autobus en travers
    de la rue n'a pas la même empreinte qu'un autobus dans sa voie."""
    r = banc("""function (L, o) {
        %s
        const v = o.char('autobus', 0, 0, 0);
        const droit = L.Vehicules.ombreDe(v).angle;
        v.angle = Math.PI / 4;
        const biais = L.Vehicules.ombreDe(v).angle;
        v.angle = -1.2;
        return { droit: droit, biais: biais, negatif: L.Vehicules.ombreDe(v).angle };
    }""" % DECOR)
    assert r["droit"] == 0
    assert abs(r["biais"] - 0.7853981633974483) < 1e-9, "l'ombre ne tourne pas : %s" % r
    assert abs(r["negatif"] + 1.2) < 1e-9, r


def test_chaque_vehicule_a_l_empreinte_de_sa_fiche(banc):
    """⚠️ C'est la MÊME empreinte que la physique : ce qu'on voit est
    exactement ce qui bloque. Une ombre de taille unique referait le défaut
    qu'on vient de réparer en vol — la même tache pour une moto et pour un
    autobus de 48 px."""
    r = banc("""function (L, o) {
        %s
        const out = {};
        L.B.defs.vehicules.forEach(function (def) {
            const v = o.char(def.slug, 0, 0, 0);
            if (!v) return;
            const ombre = L.Vehicules.ombreDe(v);
            out[def.slug] = [ombre.l, ombre.h, def.longueur, def.largeur];
            L.Entites.retirer(v);
        });
        return out;
    }""" % DECOR)
    assert len(r) >= 8, "le décor du juge est faux : trop peu de véhicules (%s)" % list(r)
    tailles = set()
    for slug, (large, haut, longueur, largeur) in r.items():
        assert large == longueur and haut == largeur, (
            f"{slug} : ombre {large}x{haut}, fiche {longueur}x{largeur}"
        )
        tailles.add((large, haut))
    assert len(tailles) >= 5, (
        "toutes les ombres font la même taille : on a refait la tache unique (%s)" % tailles
    )


def test_en_montant_elle_retrecit_s_ecarte_et_palit(banc):
    """C'est elle qui RACONTE la hauteur — et c'est pour ça qu'un saut se voit.
    ⚠️ Le juge mesure les trois ensemble : une ombre qui rétrécit sans s'écarter
    a l'air d'un char qui s'éloigne, pas d'un char qui décolle."""
    r = banc("""function (L, o) {
        %s
        const v = o.char('auto', 0, 0, 0);
        const mesure = function (z) {
            v.z = z;
            const q = L.Vehicules.ombreDe(v);
            return { l: q.l, h: q.h, dx: +(q.x - v.x).toFixed(2), part: +q.part.toFixed(3) };
        };
        return { sol: mesure(0), mi: mesure(15), haut: mesure(40) };
    }""" % DECOR)
    sol, mi, haut = r["sol"], r["mi"], r["haut"]
    assert haut["l"] < mi["l"] < sol["l"], "elle ne rétrécit pas : %s" % r
    assert haut["dx"] > mi["dx"] > sol["dx"], "elle ne s'écarte pas : %s" % r
    assert haut["part"] < mi["part"] < sol["part"], "elle ne pâlit pas : %s" % r
    # ⚠️ Et jamais au-delà du plafond : à cinquante pixels d'altitude elle ne
    # doit pas devenir un point, ni disparaître.
    assert haut["l"] >= 4 and haut["part"] > 0, "elle s'annule en l'air : %s" % r


def test_le_sol_se_voit_du_meme_biais_pour_un_passant_et_pour_un_char(banc):
    """⚠️ **Un seul biais pour toute la ville.** L'ombre d'un passant le disait
    depuis toujours — `DECORS.ombre` fait 12 × 6 pour un corps rond, donc le
    sol est écrasé de moitié — et le char, lui, posait son empreinte à plat :
    deux conventions dans le même écran, et c'est la deuxième qui a fait la
    langue noire des chars nord-sud. Les deux sont d'accord, et ce juge est ce
    qui les empêche de re-diverger."""
    r = banc("""function (L, o) {
        const p = L.DECORS.ombre;
        return { passant: p.h / p.w, char: L.B.defs.conduite.ombre.profondeur };
    }""")
    assert abs(r["passant"] - r["char"]) < 0.01, (
        "le passant et le char ne posent pas leur ombre sur le même sol : %s" % r
    )


def test_l_ombre_ne_traine_pas_devant_un_char_qui_roule_vers_le_nord(banc):
    """⚠️ **Le retour de Martin, mesuré.** Un char debout qui roule vers le nord
    montre 16 px de large et 11 px de haut ; son empreinte, elle, fait 28 px de
    long. À plat, l'ombre débordait de **quinze** pixels devant ses roues — plus
    que le char n'est haut — et on la lisait comme une remorque.

    La règle, et elle vaut pour tous les caps : **une ombre ne dépasse jamais
    la ligne de sol de plus que la hauteur du dessin qui la jette.** L'ancre du
    sprite (`ancre[1]`) est cette hauteur : c'est de là que le dessin monte."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        L.graine(31);
        const j = L.B.joueur, d = o.ligneDroite();
        j.x = d.x; j.y = d.y; L.Monde.centrerCamera(j.x, j.y);
        const out = {};
        L.B.defs.vehicules.forEach(function (def) {
            const v = o.char(def.slug, 0, 0, 0);
            if (!v) return;
            // ⚠️ Le bateau n'a pas encore de sprite (dette connue) : on ne peut
            // pas mesurer la hauteur d'un dessin qui n'existe pas.
            const sprite = L.SPRITES[v.sprite];
            const cuit = sprite ? L.Atlas.cuire(v.sprite, sprite, v.swaps) : null;
            const hauteur = cuit && !sprite.rotations ? cuit.ancre[1] : null;
            const caps = {};
            [['est', 0], ['nord', -Math.PI / 2], ['sud', Math.PI / 2], ['biais', Math.PI / 4]].forEach(function (c) {
                v.angle = c[1];
                const q = L.Vehicules.ombreDe(v);
                // Le point le plus au sud de l'empreinte tournee PUIS ecrasee.
                const demi = (Math.abs(Math.sin(q.angle)) * q.l + Math.abs(Math.cos(q.angle)) * q.h) / 2;
                caps[c[0]] = +((q.y - v.y) + demi * q.profondeur).toFixed(2);
            });
            out[def.slug] = { caps: caps, hauteur: hauteur, longueur: def.longueur };
            L.Entites.retirer(v);
        });
        return out;
    }""")
    assert len(r) >= 8, "le décor du juge est faux : trop peu de véhicules (%s)" % list(r)
    debout = 0
    for slug, m in r.items():
        if m["hauteur"] is None:
            continue           # un sprite encore en rotations : il montre sa longueur
        debout += 1
        for cap, sous in m["caps"].items():
            assert sous <= m["hauteur"], (
                f"{slug} vers le {cap} : l'ombre traîne {sous} px sous ses roues, "
                f"et le dessin n'est haut que de {m['hauteur']} px"
            )
    assert debout >= 8, "presque aucun véhicule n'est debout : le juge ne mesure rien"
