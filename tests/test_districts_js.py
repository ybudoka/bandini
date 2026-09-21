"""M8 au banc : ce que le joueur voit changer quand il change de quartier.

Les juges de `test_districts.py` regardent la carte ; ceux-ci regardent le JEU —
qui naît dans la rue, combien, et si le pont se traverse vraiment en char.
"""

import pytest

# Se transporter au centre d'une zone, camera et index remis a jour.
ALLER = """function (L, o) {
    function aller(L, slug) {
        const z = L.Monde.carte.zones.find(function (q) { return q.slug === slug; });
        if (!z) throw new Error('zone inconnue : ' + slug);
        L.B.joueur.x = (z.x + z.l / 2) * L.TT;
        L.B.joueur.y = (z.y + z.h / 2) * L.TT;
        L.Monde.centrerCamera();
        L.Entites.indexer();
        return z;
    }
"""


def test_chaque_quartier_a_ses_passants(banc):
    """⚠️ Le debardeur ne monte pas en banlieue, et le banlieusard ne descend
    pas aux quais. Sans cela, cinq districts font un seul quartier repeint."""
    r = banc(ALLER + """
        L.Jeu.commencer();
        const compte = {};
        for (const slug of ['quais', 'erables', 'shop', 'pointe']) {
            const z = aller(L, slug);
            const vus = {};
            for (let i = 0; i < 60; i++) {
                const p = L.Entites.creerPieton(L.B.joueur.x, L.B.joueur.y, null);
                vus[p.arch] = (vus[p.arch] || 0) + 1;
                L.Entites.retirer(p);
            }
            compte[slug] = vus;
        }
        return compte;
    }""")
    attendus = {"quais": "docker", "erables": "banlieusard", "shop": "machiniste", "pointe": "promeneur"}
    for quartier, chez_eux in attendus.items():
        vus = r[quartier]
        assert vus.get(chez_eux, 0) > 0, f"aucun {chez_eux} dans {quartier} : {vus}"
        etrangers = [s for s in attendus.values() if s != chez_eux and vus.get(s)]
        assert not etrangers, f"{etrangers} dans {quartier} — ils ne sont pas de la"
        assert vus.get("passant", 0) > 0, f"{quartier} n'a plus de passants ordinaires"


def test_la_shop_se_vide_la_nuit_et_les_quais_grouillent_au_matin(banc):
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const z = function (s) { return L.Monde.carte.zones.find(function (q) { return q.slug === s; }); };
        const a = function (heure, slug) { L.B.partie.heure = heure; return L.Monde.rythme(z(slug)); };
        return { shopNuit: a(0.95, 'shop'), shopJour: a(0.55, 'shop'),
                 quaisMatin: a(0.33, 'quais'), quaisJour: a(0.55, 'quais'),
                 erablesNuit: a(0.95, 'erables'), faubourgJour: a(0.55, 'faubourg') };
    }""")
    assert r["shopNuit"] < 0.3 and r["shopJour"] == 1
    assert r["quaisMatin"] > 1.2 and r["quaisJour"] == 1
    assert r["erablesNuit"] < 0.8
    assert r["faubourgJour"] == 1


def test_le_nom_du_quartier_suit_le_joueur(banc):
    """⚠️ Sous la mini-carte s'affiche la zone la PLUS PRECISE : le nom de la
    gang quand on est dans sa cour, celui du quartier partout ailleurs. Dans les
    deux cas `district` dit ou l'on est — c'est lui qui choisit les passants."""
    r = banc(ALLER + """
        L.Jeu.commencer();
        const vus = {};
        for (const slug of ['faubourg', 'erables', 'shop', 'quais', 'pointe']) {
            aller(L, slug);
            const zone = L.Monde.zoneA(L.B.joueur.x, L.B.joueur.y);
            vus[slug] = zone ? { nom: zone.nom, district: zone.district, gang: zone.gang } : null;
        }
        // Et le coin nord-ouest, c'est la banlieue, loin de toute cour de gang.
        L.B.joueur.x = 30 * L.TT; L.B.joueur.y = 12 * L.TT;
        const coin = L.Monde.zoneA(L.B.joueur.x, L.B.joueur.y);
        return { vus: vus, coin: coin ? coin.nom : null };
    }""")
    for slug, zone in r["vus"].items():
        assert zone and zone["district"] == slug, f"{slug} : {zone}"
        assert zone["nom"], slug
    assert r["coin"] == "Les Érables"


def test_on_traverse_le_pont_en_char(banc):
    """La promesse de M8, conduite pour de vrai : du bord nord du chenal a
    La Pointe, sans chargement et sans tomber a l'eau."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        // ⚠️ Le pont est une BARRIERE tant que m2 n'est pas faite (les
        // Skateux le tiennent) : ici on juge la traversee, pas la barriere —
        // `test_barrieres_js` juge celle-la.
        L.B.partie.missionsFaites.m2 = true;
        const pont = L.Monde.carte.def.ponts[0];
        // Sur la voie de droite, EN AMONT du tablier : on part de La Shop, du
        // bon bord du chenal, et on descend.
        const x = (pont.x + pont.l / 2 + 0.5) * L.TT, y = (pont.y - 9) * L.TT;
        L.B.joueur.x = x; L.B.joueur.y = y;
        L.Monde.centrerCamera(); L.Entites.indexer();
        const v = L.Vehicules.creer('auto', x, y, Math.PI / 2, { etat: 'stationne' });
        L.Entites.indexer();
        L.Vehicules.monter(L.B.joueur, v);
        const depart = L.Monde.zoneA(v.x, v.y);
        o.touche('KeyW');
        o.frame(420);
        o.relacher('KeyW');
        const arrivee = L.Monde.zoneA(v.x, v.y);
        return { depart: depart ? depart.slug : null, arrivee: arrivee ? arrivee.slug : null,
                 y0: Math.round(y / L.TT), y1: Math.round(v.y / L.TT), vie: v.vie, noye: v.noye || false };
    }""")
    assert r["depart"] == "shop", f"on ne part pas de La Shop : {r}"
    assert r["arrivee"] == "pointe", f"le char n'a pas traverse : {r}"
    assert r["y1"] > r["y0"] + 8, "le char n'a pas avance sur le pont"


def test_une_vieille_partie_ne_ramene_pas_son_char_dans_un_mur(banc):
    """⚠️ M8 a quintuple la ville : une position sauvegardee sur l'ancienne
    carte ne veut plus rien dire. Le joueur repart du terminus, et son char
    revient devant la planque — pas au milieu d'un entrepot."""
    r = banc("""function (L, o) {
        // Une partie d'avant : bonne empreinte nulle part, position d'ailleurs.
        L.Sauvegarde.ecrire(Object.assign(L.Sauvegarde.completer({}, L.B.defs), {
            empreinte: 'vieille-carte', x: 130 * L.TT, y: 95 * L.TT, jour: 4,
            planque: { vehicule: { slug: 'auto', couleur: '#c0392b', vie: 90, x: 131 * L.TT, y: 96 * L.TT, angle: 0 } },
        }));
        L.B.partie = L.Sauvegarde.completer(L.Sauvegarde.lire(), L.B.defs);
        if (L.B.partie.empreinte !== L.B.defs.empreinte) {
            L.B.partie.x = null; L.B.partie.y = null;
            L.B.partie.planque.vehicule.x = null; L.B.partie.planque.vehicule.y = null;
        }
        L.Jeu.commencer();
        const j = L.B.joueur;
        const v = L.B.entites.find(function (e) { return e.type === 'vehicule' && e.etat === 'stationne' && e.couleur === '#c0392b'; });
        const porte = L.Monde.carte.def.portes.find(function (q) { return q.lieu === 'planque'; });
        return { joueurLibre: !L.Monde.bloque(Math.floor(j.x / L.TT), Math.floor(j.y / L.TT), L.Monde.MASQUE_PIETON),
                 char: !!v,
                 surRue: v ? L.Monde.estRoute(Math.floor(v.x / L.TT), Math.floor(v.y / L.TT)) : null,
                 pres: v ? Math.round(Math.hypot(v.x - porte.x * L.TT, v.y - porte.y * L.TT) / L.TT) : null };
    }""")
    assert r["joueurLibre"], "le joueur repart dans un mur"
    assert r["char"] and r["surRue"], "le char de la planque n'est pas sur la rue"
    assert r["pres"] <= 10, f"le char revient a {r['pres']} tuiles de la planque"


# Une partie de la BONNE carte, sauvegardee a (x, y), puis rouverte.
ROUVRIR = """function (L, o) {
    function rouvrir(x, y) {
        L.B.partie = L.Sauvegarde.completer({}, L.B.defs);
        L.B.partie.empreinte = L.B.defs.empreinte;
        L.B.partie.x = x; L.B.partie.y = y;
        L.Jeu.commencer();
        const j = L.B.joueur;
        return { x: j.x, y: j.y, tx: Math.floor(j.x / L.TT), ty: Math.floor(j.y / L.TT),
                 mur: L.Monde.bloque(Math.floor(j.x / L.TT), Math.floor(j.y / L.TT), L.Monde.MASQUE_PIETON) };
    }
    const porte = L.Monde.carte.def.portes.find(function (q) { return q.lieu === 'garage'; });
    const pg = L.Monde.porteDeGarage('garage');
"""


@pytest.mark.parametrize("ou", ["toit", "baie"])
def test_une_partie_sauvee_dans_le_garage_se_rouvre_devant(banc, ou):
    """⚠️ Martin, 21 sept. 2026 : sa partie sauvee a 2549, 763 — deux rangees de
    toit au-dessus de la porte du garage Bandini — se rouvrait SUR le toit, et
    rien ne sort un pieton d'un mur. La sauvegarde ecrit ou l'on est, et au
    volant c'est le centre du char : la baie sous le rideau en est un autre cas.
    On se rouvre sur le trottoir devant, pas dans la ruelle derriere."""
    r = banc(ROUVRIR + """
        const x = %s, y = %s;
        const dessous = L.Monde.bloque(Math.floor(x / L.TT), Math.floor(y / L.TT), L.Monde.MASQUE_PIETON);
        return Object.assign(rouvrir(x, y), { dessous: dessous, porteY: porte.y, porteX: porte.x });
    }""" % (("porte.x * L.TT + 5", "(porte.y - 2) * L.TT + 11") if ou == "toit"
            else ("(pg.x + pg.l / 2) * L.TT", "(pg.y - 1) * L.TT + 8")))
    assert r["dessous"], f"le décor du juge est faux : la position n'est pas dans un mur ({r})"
    assert not r["mur"], f"la partie se rouvre dans le garage : {r}"
    assert r["ty"] > r["porteY"], f"on se rouvre derrière le garage, pas devant : {r}"
    assert abs(r["tx"] - r["porteX"]) <= 3 and r["ty"] - r["porteY"] <= 2, f"on se rouvre loin du garage : {r}"


def test_une_partie_sauvee_sur_le_trottoir_se_rouvre_au_pixel(banc):
    """Ce qu'on corrige ne touche que les places ou l'on ne tient pas : sur le
    trottoir devant le garage, on revient exactement ou l'on etait."""
    r = banc(ROUVRIR + """
        const x = porte.x * L.TT + 3, y = (porte.y + 1) * L.TT + 13;
        return Object.assign(rouvrir(x, y), { x0: x, y0: y });
    }""")
    assert not r["mur"]
    assert (r["x"], r["y"]) == (r["x0"], r["y0"]), f"une place libre a bougé : {r}"


def test_la_nuit_le_trafic_et_la_foule_tombent(banc):
    """⚠️ Le juge cote moteur : on compte ce qui vit autour du joueur a midi,
    puis a 3 h du matin, au meme endroit. Le rythme s'appliquait APRES le
    plafond, donc le Faubourg gardait ses neuf chars toute la nuit."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        function compter(heure) {
            L.B.partie.heure = heure;
            L.B.entites.length = 0;
            L.Entites.creerJoueur(L.B.joueur.x, L.B.joueur.y);
            for (let i = 0; i < 12; i++) { L.Entites.peupler(); L.Vehicules.peupler(); }
            return {
                pietons: L.B.entites.filter(function (e) { return e.type === 'pieton'; }).length,
                chars: L.B.entites.filter(function (e) { return e.type === 'vehicule' && e.conducteur === 'trafic'; }).length,
                rythme: L.Monde.rythme(L.Monde.zoneA(L.B.joueur.x, L.B.joueur.y)),
            };
        }
        const midi = compter(0.5);
        const nuit = compter(0.05);
        return { midi: midi, nuit: nuit };
    }""")
    assert r["midi"]["rythme"] > r["nuit"]["rythme"], "l'horloge ne change pas le rythme"
    assert r["nuit"]["pietons"] < r["midi"]["pietons"], \
        f"autant de monde la nuit ({r['nuit']['pietons']}) qu'a midi ({r['midi']['pietons']})"
    assert r["nuit"]["chars"] < r["midi"]["chars"], \
        f"autant de chars la nuit ({r['nuit']['chars']}) qu'a midi ({r['midi']['chars']})"
