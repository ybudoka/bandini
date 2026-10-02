"""L'arc D, la dette de Rocco — deux CHAPITRES (2 oct. 2026, docs/jalons/des-missions-en-chapitres.md, vague D),
JOUÉS au bouton acte par acte, sur le modèle de `test_arc_p_js.py` ; puis le choix (d07/d08), resté en missions.

Chaque juge commence le chapitre là où une vieille partie le reprendrait : les missions des actes d'avant sont faites
(`faites`), et `Chapitres.depart` pose l'étape au marqueur de l'acte. Ce sont les gestes des juges de d01 à d06
d'avant (vague 6 et 8, 30 sept. 2026), plus le passage à l'acte suivant, les renforts du garage, une reprise.

_La dette de Rocco_ (`dette_de_rocco`, d01 à d04, Sal) :
- Sal Ferraro se tient DEDANS, à sa chaise au milieu du terminus (`point:sal`), après m6 seulement ;
- acte 1 (d01) : on lui serre la main (l'intro), puis on le mène au garage (`proteger`) ; couché en chemin, c'est raté
  — et c'est SON échec qu'on entend ;
- acte 2 (d02) : Momo le taxi (posé devant le terminus), la police à semer, l'enveloppe : la dette baisse de 500 ;
- acte 3 (d03) : les faux Ciseaux devant l'hôtel, la police, Sal : −300 ; mort, REPRENDRE L'ACTE 3 ;
- acte 4 (d04) : la collecte chez Ti-Paul, Lulu et Ovila, et Sal : −800, et le chapitre est fait.
_Le garage de Rocco_ (`garage_de_rocco`, d05 Josée, d06 Gus) : les papiers de l'oncle et deux Ciseaux de plus en
renfort ; la nuit au garage, deux vagues de renfort, le contremaître, Gus."""

from outils_missions import OUTILS, PLUS_LONGUES
from test_arc_f_js import DEDANS
from test_arc_p_js import RECHARGER
from test_arc_q_js import ESCORTE
from test_quatre_missions_js import RATTRAPER

AVANT_D = "['m1', 'm2', 'm3', 'm4', 'm5', 'm6']"
#: Les missions remplacées par _La dette de Rocco_, dans l'ordre des actes.
DETTE = ['d01', 'd02', 'd03', 'd04']


def _avant(n):
    """La partie telle qu'une vieille partie l'aurait au début de l'acte `n` (1 à 4) de la dette."""
    return AVANT_D[:-1] + "".join(", '%s'" % s for s in DETTE[:n - 1]) + "]"


#: Prendre le chapitre de Sal comme un joueur : entrer au terminus, lui serrer la main, écouter, ressortir.
CHEZ_SAL = """
  function chezSal(L, o) {
    const piece = dedans(L, o, 'terminus');
    const la = !!L.B.entites.find(function (e) { return e.personnage === 'sal'; });
    if (la) serrer(L, o, 'sal');
    const mission = L.B.partie.mission ? L.B.partie.mission.slug : null;
    const intro = !!(L.B.scene || L.B.cinema);
    passer(L, o); ecouter(L);
    return { piece: piece, la: la, intro: intro, mission: mission, etape: etape(L) };
  }
"""

def test_sal_n_est_au_terminus_qu_apres_m6(banc):
    r = banc("function (L, o) {" + OUTILS + PLUS_LONGUES + RECHARGER + DEDANS + """
        L.Jeu.commencer(); L.graine(6);
        faites(L, ['m1', 'm2', 'm3', 'm4', 'm5']);
        recharger(L);
        dedans(L, o, 'terminus');
        const avant = !!L.B.entites.find(function (e) { return e.personnage === 'sal'; });
        sortir(L, o);
        faites(L, ['m6']);
        recharger(L);
        const piece = dedans(L, o, 'terminus');
        const s = L.B.entites.find(function (e) { return e.personnage === 'sal'; });
        return { avant: avant, piece: piece, apres: !!s, dispo: (L.Histoire.disponibleDe('sal') || {}).slug || null };
    }""")
    assert r["avant"] is False, "pas de Sal au terminus avant m6 (`arrive_apres`)"
    assert r["piece"] == "terminus" and r["apres"] is True and r["dispo"] == "dette_de_rocco", r


def _acte_1(banc, coucher_sal=False):
    return banc("function (L, o) {" + OUTILS + PLUS_LONGUES + RECHARGER + DEDANS + ESCORTE + CHEZ_SAL + """
        L.Jeu.commencer(); L.graine(6);
        const B = L.B, p = B.partie;
        faites(L, """ + _avant(1) + """);
        const j = recharger(L);
        const argent = paiements(L);
        const chez = chezSal(L, o);
        sortir(L, o);
        const c = B.mission && B.mission.protege;
        const t = L.Histoire.lieu('terminus');
        const pose = c ? Math.round(Math.hypot(c.x - t.x, c.y - t.y) / 16) : null;
        const suit = rejoindre(L, o, c);
        if (""" + ("true" if coucher_sal else "false") + """) {
            L.Entites.assommer(c);
            for (let k = 0; k < 900 && (B.transition || B.cinema || !B.menu); k++) { o.frame(1); ecouter(L); }
            return { chez: chez, rate: !p.mission, echecs: p.stats.echecs || 0, fait: !!p.missionsFaites.d01, dites: dites,
                     menu: B.menu ? B.menu.items.map(function (i) { return i.libelle; }) : null };
        }
        arriverAvec(L, o, c, 'garage');
        jouer(L, o, 20);
        return { chez: chez, personnage: c && c.personnage, pose: pose, suit: suit, dites: dites, apres: etape(L),
                 fait: !!p.missionsFaites.d01, argent: argent.map(function (a) { return a.montant; }),
                 donneur: L.Chapitres.donneurDe(L.Histoire.courante()) };
    }""")


def test_acte_1_sal_te_fait_asseoir_puis_veut_voir_le_garage(banc):
    r = _acte_1(banc)
    assert r["chez"] == {"piece": "terminus", "la": True, "intro": True, "mission": "dette_de_rocco", "etape": 1}, r["chez"]
    assert r["personnage"] == "sal" and r["suit"] is True and r["pose"] <= 6, r
    assert "pendant:sal:1" in r["dites"], r["dites"]
    assert r["fait"] is True and r["argent"] == [100], "l'acte fini marque d01 faite, et paie sa prime"
    assert r["apres"] == 3 and r["donneur"] == "sal", "l'acte 2 commence : Momo"
    # La fin de d01 (en personne, au garage), puis l'appel et l'intro de d02, au marqueur de l'acte 2.
    assert "pendant:sal:2" in r["dites"] and "pendant:sal:3" in r["dites"], r["dites"]


def test_acte_1_sal_couche_en_chemin_c_est_rate_et_c_est_son_echec(banc):
    r = _acte_1(banc, coucher_sal=True)
    assert r["chez"]["mission"] == "dette_de_rocco"
    assert r["rate"] is True and r["echecs"] == 1 and r["fait"] is False, r
    assert [d for d in r["dites"] if d.startswith("echec:")] == ["echec:sal:0"], r["dites"]
    assert r["menu"][:2] == ["REPRENDRE L'ACTE 1", "PLUS TARD"], r


def test_acte_2_l_enveloppe_de_momo_paie_le_premier_versement(banc):
    r = banc("function (L, o) {" + OUTILS + PLUS_LONGUES + RECHARGER + DEDANS + RATTRAPER + CHEZ_SAL + """
        L.Jeu.commencer(); L.graine(6);
        const B = L.B, p = B.partie;
        faites(L, """ + _avant(2) + """);
        const j = recharger(L);
        p.dette = 15000;
        const argent = paiements(L);
        const chez = chezSal(L, o);
        sortir(L, o);
        const f = B.mission.fuyard, t = L.Histoire.lieu('terminus');
        const taxi = { slug: f && f.slug, terminus: f ? Math.round(Math.hypot(f.x - t.x, f.y - t.y) / 16) : null };
        j.x = f.x + 40; j.y = f.y; L.Entites.indexer(); jouer(L, o, 300);
        rattraper(L, o);
        const semer = { etape: etape(L), etoiles: B.recherche.etoiles };
        const cache = seCacher(L, o);
        const retour = { etape: etape(L), ligne: L.Histoire.ligneObjectif() };
        dedans(L, o, 'terminus'); serrer(L, o, 'sal'); jouer(L, o, 20); sortir(L, o); jouer(L, o, 10);
        return { chez: chez, taxi: taxi, semer: semer, cache: cache, retour: retour, dites: dites, dette: p.dette,
                 fait: !!p.missionsFaites.d02, apres: etape(L), argent: argent.map(function (a) { return a.montant; }) };
    }""")
    assert r["chez"]["mission"] == "dette_de_rocco" and r["chez"]["intro"] is False, "une vieille partie reprend à l'acte 2, sans l'intro de d01"
    assert r["taxi"]["slug"] == "taxi" and r["taxi"]["terminus"] <= 40, f"Momo part de devant le terminus : {r['taxi']}"
    assert r["semer"]["etape"] == 4 and r["semer"]["etoiles"] >= 1 and r["cache"]["apres"] == 0, r
    assert r["retour"]["etape"] == 5 and r["retour"]["ligne"].startswith("RAPPORTE L'ENVELOPPE"), r["retour"]
    for dite in ("pendant:sal:2", "pendant:sal:3", "pendant:sal:4", "pendant:sal:5", "pendant:sal:6"):
        assert dite in r["dites"], f"{dite} manque : {r['dites']}"
    assert r["fait"] is True and r["argent"] == [100] and r["dette"] == 14500, r
    assert r["apres"] == 7, "l'acte 3 commence au terminus : les faux Ciseaux"


def _acte_3(banc, mourir=False):
    return banc("function (L, o) {" + OUTILS + PLUS_LONGUES + RECHARGER + DEDANS + CHEZ_SAL + """
        L.Jeu.commencer(); L.graine(6);
        const B = L.B, p = B.partie;
        faites(L, """ + _avant(3) + """);
        const j = recharger(L);
        p.dette = 15000;
        const argent = paiements(L);
        const chez = chezSal(L, o);
        sortir(L, o);
        const h = L.Histoire.lieu('hotel');
        if (""" + ("true" if mourir else "false") + """) {
            L.Missions.hopital('banc');
            for (let k = 0; k < 900 && (B.transition || B.cinema || !B.menu); k++) { o.frame(1); ecouter(L); }
            const menu = B.menu ? B.menu.items.map(function (i) { return i.libelle; }) : null;
            const item = B.menu.items.find(function (x) { return x.libelle.indexOf('REPRENDRE') === 0; });
            if (item.faire(item) !== false && B.menu) L.Hud.fermerMenu();
            o.fondu(); for (let k = 0; k < 400 && B.transition; k++) o.frame(1);
            jouer(L, o, 10);
            const eux = B.mission ? B.mission.entites.filter(function (e) { return e.cible && e.etape === 7 && e.vivant; }) : [];
            return { menu: menu, echec: dites.filter(function (d) { return d.indexOf('echec:') === 0; }), etape: etape(L),
                     ciseaux: eux.length, dedans: !!B.interieur };
        }
        const eux = B.mission.entites.filter(function (e) { return e.cible && e.etape === 7; });
        const faux = { n: eux.length, chef: eux.some(function (e) { return e.chef; }),
                       hotel: Math.max.apply(null, eux.map(function (e) { return Math.round(Math.hypot(e.x - h.x, e.y - h.y) / 16); })) };
        j.x = h.x; j.y = h.y; L.Entites.indexer();
        eux.forEach(function (e) { L.Entites.assommer(e); }); jouer(L, o, 10);
        const semer = { etape: etape(L), etoiles: B.recherche.etoiles };
        const cache = seCacher(L, o);
        dedans(L, o, 'terminus'); serrer(L, o, 'sal'); jouer(L, o, 20); sortir(L, o); jouer(L, o, 10);
        return { chez: chez, faux: faux, semer: semer, cache: cache, dites: dites, dette: p.dette, apres: etape(L),
                 fait: !!p.missionsFaites.d03, argent: argent.map(function (a) { return a.montant; }) };
    }""")


def test_acte_3_les_faux_ciseaux_devant_l_hotel(banc):
    r = _acte_3(banc)
    # Dedans, le marqueur attend qu'on sorte (rien n'avance dans une pièce) : on est au marqueur de l'acte 3.
    assert r["chez"]["mission"] == "dette_de_rocco" and r["chez"]["etape"] == 6, r["chez"]
    assert r["faux"]["n"] >= 3 and r["faux"]["chef"] and r["faux"]["hotel"] <= 12, r["faux"]
    assert r["semer"]["etape"] == 8 and r["semer"]["etoiles"] >= 2 and r["cache"]["apres"] == 0, r
    for dite in ("pendant:sal:6", "pendant:sal:7", "pendant:sal:10"):
        assert dite in r["dites"], f"{dite} manque : {r['dites']}"
    assert r["fait"] is True and r["argent"] == [300] and r["dette"] == 14700, r
    assert r["apres"] == 11, "l'acte 4 commence : la collecte"


def test_acte_3_mort_reprendre_l_acte_3_remet_les_faux_ciseaux(banc):
    r = _acte_3(banc, mourir=True)
    assert r["menu"][:2] == ["REPRENDRE L'ACTE 3", "PLUS TARD"], r
    assert r["echec"] == ["echec:sal:6"], "on entend l'échec de d03, pas celui d'un autre job"
    assert r["etape"] == 7 and r["ciseaux"] >= 3 and not r["dedans"], r


def test_acte_4_la_collecte_puis_le_chapitre_est_fait(banc):
    r = banc("function (L, o) {" + OUTILS + PLUS_LONGUES + RECHARGER + DEDANS + CHEZ_SAL + """
        L.Jeu.commencer(); L.graine(6);
        const B = L.B, p = B.partie;
        faites(L, """ + _avant(4) + """);
        const j = recharger(L);
        p.dette = 15000;
        const argent = paiements(L);
        const chez = chezSal(L, o);
        sortir(L, o);
        const etapes = [];
        serrer(L, o, 'tipaul'); etapes.push(etape(L));
        dedans(L, o, 'cantine'); serrer(L, o, 'lulu'); sortir(L, o); etapes.push(etape(L));
        dedans(L, o, 'phare'); serrer(L, o, 'ovila'); sortir(L, o); etapes.push(etape(L));
        const ligne = L.Histoire.ligneObjectif();
        dedans(L, o, 'terminus'); serrer(L, o, 'sal'); finir(L, o);
        return { chez: chez, etapes: etapes, ligne: ligne, dites: dites, dette: p.dette,
                 fait: !!p.missionsFaites.dette_de_rocco, d04: !!p.missionsFaites.d04,
                 suite: (L.Histoire.disponibleDe('josee') || {}).slug || null, duree: p.durees && p.durees.dette_de_rocco,
                 argent: argent.map(function (a) { return a.montant; }) };
    }""")
    assert r["chez"]["mission"] == "dette_de_rocco" and r["chez"]["etape"] == 10, r["chez"]
    assert r["etapes"] == [12, 13, 14] and r["ligne"].startswith("RAPPORTE LA COLLECTE"), r
    for dite in ("accueil:tipaul:11", "accueil:lulu:12", "accueil:ovila:13", "pendant:sal:14"):
        assert dite in r["dites"], f"{dite} manque : {r['dites']}"
    assert r["fait"] is True and r["d04"] is True and r["argent"] == [400] and r["dette"] == 14200, r
    assert r["duree"] and len(r["duree"]["actes"]) == 1, "la durée du chapitre, par acte joué ici"


def test_une_vieille_partie_comme_celle_de_martin_a_fait_la_dette_et_reprend_le_garage_a_l_acte_2(banc):
    """La partie de Martin (2 oct. 2026) : d01 à d05 faites. La dette est faite ; le garage commence chez Gus."""
    r = banc("function (L, o) {" + OUTILS + RECHARGER + """
        L.Jeu.commencer(); L.graine(6);
        faites(L, """ + AVANT_D[:-1] + """, 'd01', 'd02', 'd03', 'd04', 'd05']);
        recharger(L);
        const dette = L.Histoire.mission('dette_de_rocco'), garage = L.Histoire.mission('garage_de_rocco');
        return { dette: L.Histoire.faite('dette_de_rocco'), garage: L.Histoire.faite('garage_de_rocco'),
                 gus: (L.Histoire.disponibleDe('gus') || {}).slug || null, depart: L.Chapitres.depart(garage),
                 donneur: L.Chapitres.donneurDe(garage), h03: L.Histoire.faite('d01') && !!dette };
    }""")
    assert r == {"dette": True, "garage": False, "gus": "garage_de_rocco", "depart": 4, "donneur": "gus", "h03": True}, r


# --- _Le garage de Rocco_ (d05, d06), puis le CHOIX — le coffre de Sal (d07, avec Josée) ou la dernière coupe (d08, la
# dette payée). Chacune ferme l'autre.

AVANT_D5 = AVANT_D[:-1] + ", 'd01', 'd02', 'd03', 'd04']"

CHEZ_JOSEE = """
  function chezJosee(L, o) {
    const piece = dedans(L, o, 'bar');
    const la = !!L.B.entites.find(function (e) { return e.personnage === 'josee'; });
    if (la) serrer(L, o, 'josee');
    const mission = L.B.partie.mission ? L.B.partie.mission.slug : null;
    passer(L, o); ecouter(L);
    sortir(L, o);
    return { piece: piece, la: la, mission: mission };
  }
"""


def test_garage_acte_1_l_acte_du_garage_pour_l_avocat_et_deux_ciseaux_de_renfort(banc):
    r = banc("function (L, o) {" + OUTILS + PLUS_LONGUES + RECHARGER + DEDANS + CHEZ_JOSEE + """
        L.Jeu.commencer(); L.graine(6);
        const B = L.B, p = B.partie;
        faites(L, """ + AVANT_D5 + """);
        const j = recharger(L);
        p.casier = 5;
        const argent = paiements(L);
        const chez = chezJosee(L, o);
        const g = L.Histoire.lieu('garage');
        const acte = B.entites.find(function (e) { return e.objetDeMission === 'papiers_de_rocco'; });
        const pose = acte ? Math.round(Math.hypot(acte.x - g.x, acte.y - g.y) / 16) : null;
        aPied(L); j.x = acte.x; j.y = acte.y; L.Entites.indexer(); jouer(L, o, 4);
        const eux = B.mission.entites.filter(function (e) { return e.cible && e.etape === 2; });
        const ciseaux = { etape: etape(L), n: eux.length, bagues: eux.every(function (e) { return e.arme === 'poing_americain'; }) };
        eux.forEach(function (e) { L.Entites.assommer(e); }); jouer(L, o, 10);
        const renfort = B.mission.entites.filter(function (e) { return e.cible && e.etape === 2 && e.etat !== 'assomme'; });
        const vague = { etape: etape(L), n: renfort.length };
        renfort.forEach(function (e) { L.Entites.assommer(e); }); jouer(L, o, 10);
        const bar = { etape: etape(L), ligne: L.Histoire.ligneObjectif() };
        dedans(L, o, 'bar'); serrer(L, o, 'josee'); jouer(L, o, 20); sortir(L, o); jouer(L, o, 10);
        return { chez: chez, pose: pose, ciseaux: ciseaux, vague: vague, bar: bar, dites: dites, casier: p.casier, apres: etape(L),
                 fait: !!p.missionsFaites.d05, argent: argent.map(function (a) { return a.montant; }) };
    }""")
    assert r["chez"] == {"piece": "bar", "la": True, "mission": "garage_de_rocco"}, r["chez"]
    assert r["pose"] is not None and r["pose"] <= 3, r
    assert r["ciseaux"] == {"etape": 2, "n": 2, "bagues": True}, r["ciseaux"]
    assert r["vague"] == {"etape": 2, "n": 2}, f"deux de renfort : {r['vague']}"
    assert r["bar"]["etape"] == 3 and r["bar"]["ligne"].startswith("LES PAPIERS AU BROUILLARD"), r["bar"]
    for dite in ("pendant:josee:1", "pendant:josee:2", "pendant:josee:3", "pendant:josee:4", "pendant:gus:4"):
        assert dite in r["dites"], f"{dite} manque : {r['dites']}"
    assert r["fait"] is True and r["argent"] == [150] and r["casier"] == 3, r
    assert r["apres"] == 5, "l'acte 2 commence : la nuit au garage"


def test_garage_acte_2_les_ciseaux_de_sal_deux_vagues_puis_gus(banc):
    r = banc("function (L, o) {" + OUTILS + PLUS_LONGUES + RECHARGER + """
        L.Jeu.commencer(); L.graine(6);
        const B = L.B, p = B.partie;
        faites(L, """ + AVANT_D5[:-1] + """, 'd05']);
        const j = recharger(L);
        const argent = paiements(L);
        const dispo = (L.Histoire.disponibleDe('gus') || {}).slug || null;
        serrer(L, o, 'gus'); passer(L, o); ecouter(L);
        const mission = p.mission ? p.mission.slug : null;
        const g = L.Histoire.lieu('garage');
        j.x = g.x; j.y = g.y; L.Entites.indexer();
        laNuit(L, o); jouer(L, o);
        const eux = B.mission.entites.filter(function (e) { return e.cible && e.etape === 6; });
        const vague = { etape: etape(L), n: eux.length,
                        garage: Math.max.apply(null, eux.map(function (e) { return Math.round(Math.hypot(e.x - g.x, e.y - g.y) / 16); })) };
        const vagues = [];
        for (let k = 0; k < 4 && etape(L) === 6; k++) {
            const debout = B.mission.entites.filter(function (e) { return e.cible && e.etape === 6 && e.etat !== 'assomme'; });
            vagues.push(debout.length);
            debout.forEach(function (e) { L.Entites.assommer(e); }); jouer(L, o, 10);
        }
        const c = B.mission.entites.find(function (e) { return e.cible && e.etape === 7; });
        const chef = { etape: etape(L), chef: !!(c && c.chef), arme: c && c.arme };
        j.x += 300; L.Entites.indexer();
        L.Entites.assommer(c); jouer(L, o, 10);
        const retour = { etape: etape(L), ligne: L.Histoire.ligneObjectif() };
        versLui(L, 'gus'); finir(L, o);
        return { dispo: dispo, mission: mission, vague: vague, vagues: vagues, chef: chef, retour: retour, dites: dites,
                 fait: !!p.missionsFaites.garage_de_rocco, d06: !!p.missionsFaites.d06, argent: argent.map(function (a) { return a.montant; }) };
    }""")
    assert r["dispo"] == "garage_de_rocco" and r["mission"] == "garage_de_rocco", r
    assert r["vague"]["etape"] == 6 and r["vague"]["n"] == 3, r["vague"]
    assert r["vagues"] == [3, 2, 2], f"trois Ciseaux, puis deux vagues de deux : {r['vagues']}"
    assert r["chef"] == {"etape": 7, "chef": True, "arme": "couteau"}, r["chef"]
    assert r["retour"]["etape"] == 8 and r["retour"]["ligne"].startswith("DIS À GUS"), r["retour"]
    for dite in ("pendant:gus:4", "pendant:gus:5", "pendant:gus:6", "pendant:gus:7", "pendant:gus:8"):
        assert dite in r["dites"], f"{dite} manque : {r['dites']}"
    assert r["fait"] is True and r["d06"] is True and r["argent"] == [250], r


def test_d07_le_coffre_de_sal_ferme_la_derniere_coupe(banc):
    r = banc("function (L, o) {" + OUTILS + PLUS_LONGUES + RECHARGER + DEDANS + CHEZ_JOSEE + """
        L.Jeu.commencer(); L.graine(6);
        const B = L.B, p = B.partie;
        faites(L, """ + AVANT_D5[:-1] + """, 'd05', 'd06']);
        const j = recharger(L);
        p.dette = 0;
        const argent = paiements(L);
        const les_deux = ['d07', 'd08'].map(function (s) { return L.Histoire.disponibles().some(function (m) { return m.slug === s; }); });
        const chez = chezJosee(L, o);
        const t = L.Histoire.lieu('terminus');
        j.x = t.x; j.y = t.y; L.Entites.indexer();
        laNuit(L, o); jouer(L, o);
        const v = B.mission.vehicule;
        const berline = { etape: etape(L), slug: v && v.slug, terminus: v ? Math.round(Math.hypot(v.x - t.x, v.y - t.y) / 16) : null };
        j.x = v.x + 12; j.y = v.y; L.Entites.indexer(); L.Vehicules.monter(j, v); L.Entites.indexer(); jouer(L, o);
        const semer = { etape: etape(L), etoiles: B.recherche.etoiles };
        const cache = seCacher(L, o);
        j.x = v.x + 12; j.y = v.y; L.Entites.indexer(); L.Vehicules.monter(j, v); L.Entites.indexer(); jouer(L, o);
        const baie = L.Histoire.lieuDeLivraison('bar');
        v.x = baie.x; v.y = baie.y; v.vitesse = 0; j.x = v.x; j.y = v.y; L.Entites.indexer(); jouer(L, o, 10);
        const livre = etape(L);
        dedans(L, o, 'bar'); serrer(L, o, 'josee'); finir(L, o);
        return { les_deux: les_deux, chez: chez, berline: berline, semer: semer, cache: cache, livre: livre, dites: dites,
                 fermees: p.fermees, d08: (L.Histoire.disponibleDe('sal') || {}).slug || null,
                 fait: !!p.missionsFaites.d07, argent: argent.map(function (a) { return a.montant; }) };
    }""")
    assert r["les_deux"] == [True, True], "la dette payée, les deux côtés du choix sont offerts"
    assert r["chez"]["mission"] == "d07", r["chez"]
    assert r["berline"]["etape"] == 1 and r["berline"]["slug"] == "luxe" and r["berline"]["terminus"] <= 16, r["berline"]
    assert r["semer"]["etape"] == 2 and r["semer"]["etoiles"] >= 2 and r["cache"]["apres"] == 0, r
    assert r["livre"] == 4, r
    for dite in ("pendant:josee:1", "pendant:josee:2", "pendant:josee:3", "pendant:josee:4"):
        assert dite in r["dites"], f"{dite} manque : {r['dites']}"
    assert r["fait"] is True and r["argent"] == [2000], r
    assert "d08" in r["fermees"] and r["d08"] is None, "le coffre volé, plus jamais de dernière coupe"


def test_d08_la_derniere_coupe_attend_la_dette_payee(banc):
    r = banc("function (L, o) {" + OUTILS + PLUS_LONGUES + RECHARGER + DEDANS + ESCORTE + CHEZ_SAL + """
        L.Jeu.commencer(); L.graine(6);
        const B = L.B, p = B.partie;
        faites(L, """ + AVANT_D5[:-1] + """, 'd05', 'd06']);
        const j = recharger(L);
        p.dette = 12800;
        const endettee = (L.Histoire.disponibleDe('sal') || {}).slug || null;
        p.dette = 0;
        const argent = paiements(L);
        const chez = chezSal(L, o);
        sortir(L, o);
        const c = B.mission.protege;
        const suit = rejoindre(L, o, c);
        arriverAvec(L, o, c, 'planque');
        const planque = etape(L);
        arriverAvec(L, o, c, 'bar');
        finir(L, o);
        return { endettee: endettee, chez: chez, personnage: c && c.personnage, suit: suit, planque: planque, dites: dites,
                 fermees: p.fermees, fait: !!p.missionsFaites.d08, argent: argent.map(function (a) { return a.montant; }) };
    }""")
    assert r["endettee"] is None, "tant que la dette court, pas de dernière coupe"
    assert r["chez"]["mission"] == "d08", r["chez"]
    assert r["personnage"] == "sal" and r["suit"] is True and r["planque"] == 1, r
    for dite in ("pendant:sal:0", "pendant:sal:1"):
        assert dite in r["dites"], f"{dite} manque : {r['dites']}"
    assert r["fait"] is True and "d07" in r["fermees"], r


def test_garage_mourir_a_l_acte_1_le_fait_rater_meme_sans_echec_au_paquet(banc):
    """Le paquet ne porte plus l'échec par défaut (`missions.PAR_DEFAUT_AU_NAVIGATEUR`) : mort, le chapitre rate quand
    même (`Histoire.echecsDe`), et c'est l'échec de d05 qu'on entend."""
    r = banc("function (L, o) {" + OUTILS + PLUS_LONGUES + RECHARGER + DEDANS + CHEZ_JOSEE + """
        L.Jeu.commencer(); L.graine(6);
        const B = L.B, p = B.partie;
        faites(L, """ + AVANT_D5 + """);
        recharger(L);
        const defs = L.Histoire.mission('garage_de_rocco');
        const chez = chezJosee(L, o);
        L.Histoire.evenement('mort'); jouer(L, o, 4);
        return { paquet: defs && defs.echec === undefined, chez: chez.mission, rate: !p.mission, echecs: p.stats.echecs || 0,
                 echec: dites.filter(function (d) { return d.indexOf('echec:') === 0; }) };
    }""")
    assert r["paquet"] is True and r["chez"] == "garage_de_rocco", r
    assert r["rate"] is True and r["echecs"] == 1, r
    assert r["echec"] == ["echec:josee:0"], r
