"""Le moteur JS sous Node, contre le paquet que le serveur sert VRAIMENT.

Chaque test passe une fonction `(L, o) => resultat` au banc (tests/banc.js) :
L = window.BANDINI, o = outils (frame, touche, pad, pointeur, singe...).
"""

import pytest


def test_le_moteur_charge_et_expose_son_api(banc, paquet):
    r = banc("""function (L, o) {
        return { etat: L.B.etat, cles: Object.keys(L).sort(), version: L.B.defs.version,
                 carte: [L.Monde.carte.w, L.Monde.carte.h], fetchs: o.fetchs.length,
                 compte: o.compte.appels.map(function (a) { return a.chemin; }),
                 defi: o.defi.appels.length,
                 ouverture: L.Histoire.fichiersDeLOuverture().length };
    }""")
    assert r["etat"] == "titre"
    for cle in ("B", "Base", "Atlas", "Entree", "Son", "Monde", "Entites", "Combat", "Vehicules",
                "Police", "Missions", "Hud", "Jeu", "Sauvegarde", "SPRITES", "TUILES"):
        assert cle in r["cles"], cle
    assert r["carte"] == [paquet["carte"]["largeur"], paquet["carte"]["hauteur"]]
    # ⚠️ DEUX REQUETES, PLUS CELLES DE L'OUVERTURE — et pas une de plus.
    # Le paquet de definitions et la carte (a part depuis le 16 sept. 2026 :
    # elle faisait plus de la moitie du poids), puis les mp3 de l'ouverture (sa musique et ses
    # quatre voix) que `Son.prechauffer` tire dans le cache du navigateur
    # pendant qu'on lit l'ecran titre : elle part a la seconde ou l'on presse
    # JOUER, et un narrateur qui arrive en retard ne raconte plus rien. Tout le
    # reste de l'audio (12 Mo en 166 fichiers) se charge A L'USAGE, et le
    # chiffre ci-dessous est ce qui le garantit : il ne bouge que si quelqu'un
    # ajoute une phrase a l'ouverture, jamais parce qu'un son de plus s'est
    # invite au demarrage.
    # ⚠️ Plus UNE requete de compte (M14, 2e vague) : `POST /api/compte/ouvrir`,
    # qui tourne le jeton d'appareil une fois par chargement. Sans cookie, le
    # serveur repond « pas de compte » et plus rien ne part — un jeu qui bavarde
    # avec le serveur alors que personne n'a de compte serait un jeu qui a oublie
    # qu'il se joue hors ligne.
    assert r["compte"] == ["ouvrir"]
    # ⚠️ Plus UNE requete pour le defi du jour (M14, 5e vague) : `GET /api/defi`, sans
    # cookie et sans que rien n'attende sa reponse.
    assert r["defi"] == 1
    # ⚠️ Plus UNE pour les notes de la musique (29 sept. 2026) : `GET /api/musiques`, le filet
    # du sequenceur, sorti du paquet et demande juste apres lui (`Son.Notes`).
    # ⚠️ Plus UNE pour les collections (30 sept. 2026, `/api/collections`), et UNE pour la suite du paquet
    # (30 sept. 2026, `/api/suite` : le Clairon, les Galeries hantees) — sorties du paquet, demandees juste
    # apres lui, comme les notes.
    assert r["fetchs"] == 7 + r["ouverture"]
    assert r["ouverture"] <= 6, "l'ouverture se prechauffe ; la ville, non"


@pytest.fixture(scope="module")
def ce_qui_est_recu(banc):
    """⚠️ **DEUX LECTURES, UN BANC** (vague C, 28 sept. 2026) : l'intégrité des
    sprites et la ville reçue ne touchent à rien — ni partie commencée, ni image
    jouée. Elles se lisent dans le même chargement. « Une tuile de la légende sans
    peintre » était vérifiée DEUX fois ; elle ne l'est plus que dans la ville
    reçue, avec son message."""
    return banc("""function (L, o) {
        const problemes = [];
        for (const nom in L.SPRITES) problemes.push.apply(problemes, L.Atlas.valider(nom, L.SPRITES[nom]));
        for (const ch in L.POLICE_PIXEL) if (L.POLICE_PIXEL[ch].length !== 15) problemes.push('police ' + ch);

        const c = L.Monde.carte, d = L.B.defs.carte;
        const types = {};
        L.B.defs.carte.decor.forEach(function (m) { types[m.type] = true; });
        return { sprites: problemes,
                 ville: { w: c.w, h: c.h, portes: c.portes.length, points: c.points.length,
                          decor: L.B.defs.carte.decor.length,
                          // Les lampes DU PAQUET : les lucarnes allumees s'y ajoutent au bout (les toits, vague 4).
                          lampes: c.lampes.filter(function (l) { return !l.lucarne; }).length,
                          zones: c.zones.length, sansPeintre: Object.keys(d.legende).filter(function (g) { return !L.TUILES[g]; }),
                          decorSansPeintre: Object.keys(types).filter(function (t) { return !L.DECORS[t]; }),
                          typesDecor: Object.keys(types).sort() } };
    }""")


def test_les_sprites_sont_integres(ce_qui_est_recu):
    assert ce_qui_est_recu["sprites"] == []


def test_la_sauvegarde_fait_l_aller_retour_et_complete_un_vieux_blob(banc):
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        L.B.partie.argent = 1234; L.B.partie.casier = 2;
        L.Missions.sauvegarderPartie();
        const brut = JSON.parse(o.store[L.Sauvegarde.CLE]);
        const vieux = L.Sauvegarde.completer({ argent: 7 }, L.B.defs);
        return { argent: brut.argent, casier: brut.casier, x: brut.x, vieux: vieux,
                 cles: Object.keys(L.etatInitial(L.B.defs)).sort() };
    }""")
    assert r["argent"] == 1234 and r["casier"] == 2 and isinstance(r["x"], int)
    assert r["vieux"]["argent"] == 7
    assert sorted(r["vieux"].keys()) == r["cles"]
    assert r["vieux"]["armes"]["poings"] == {"mun": None}


def test_un_char_ne_pousse_personne_hors_de_la_carte(banc):
    """Un char gare qui chevauche le joueur au ras du bord nord le repousse — vers
    le dedans de la carte, jamais au-dela. Le singe l'a trouve (graine 1) : le
    joueur finissait a y = -3,5, dans le « mur » du dehors."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const j = L.B.joueur, T = L.TT, c = L.Monde.carte;
        const out = [];
        for (const dy of [4, 6, 8, 10]) {
            j.x = 1782.8; j.y = 5.0; j.vx = 0; j.vy = 0;
            L.B.entites = L.B.entites.filter(function (e) { return e.type !== 'vehicule'; });
            const v = L.Vehicules.creer('remorqueuse', j.x + 2, j.y + dy, 0, { etat: 'stationne' });
            L.Entites.indexer();
            o.frame(1);
            out.push({ dy: dy, y: j.y, dedans: j.y >= j.r && j.y <= c.pxH - j.r });
            L.Entites.retirer(v);
        }
        return out;
    }""")
    assert all(q["dedans"] for q in r), f"pousse hors de la carte : {r}"


@pytest.mark.parametrize("graine", [1, 2])
def test_le_singe_ne_casse_rien(banc, graine):
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        o.singe(3000, %d);
        const j = L.B.joueur, c = L.Monde.carte;
        const tx = Math.floor(j.x / L.TT), ty = Math.floor(j.y / L.TT);
        return { etat: L.B.etat, dedans: j.x >= 0 && j.y >= 0 && j.x <= c.pxW && j.y <= c.pxH,
                 sol: L.Monde.solidite(tx, ty), nage: !!j.nage, t: L.B.t, argent: L.B.partie.argent, nan: isNaN(j.x) || isNaN(j.y) };
    }""" % graine)
    assert r["etat"] in ("jeu", "pause")
    # ⚠️ L'eau (2) est permise EN NAGEANT : le joueur nage depuis le 15 sept. 2026,
    # et un singe qui marche assez longtemps finit parfois dans l'etang d'un parc.
    # Ce que le juge refuse, c'est un mur (1), une cloture ou un NaN.
    assert r["dedans"] and (r["sol"] in (0, 3) or (r["sol"] == 2 and r["nage"])) and not r["nan"]
    assert r["argent"] >= 0
    assert r["t"] > 1000


def test_la_ville_recue_est_celle_du_serveur(ce_qui_est_recu, paquet):
    r = ce_qui_est_recu["ville"]
    carte = paquet["carte"]
    assert [r["w"], r["h"]] == [carte["largeur"], carte["hauteur"]]
    assert r["portes"] == len(carte["portes"]) >= 8
    assert r["points"] == len(carte["points_interet"])
    assert r["decor"] == len(carte["decor"]) > 100
    assert r["lampes"] == len(carte["lampes"]) > 40
    assert r["zones"] >= 2
    assert r["sansPeintre"] == [], "une tuile de la legende n'a pas de peintre"
    assert r["decorSansPeintre"] == [], "un decor de la carte n'a pas de peintre"
    assert len(r["typesDecor"]) >= 6, r["typesDecor"]


def test_le_joueur_et_les_lieux_sont_sur_des_tuiles_marchables(banc):
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const j = L.B.joueur;
        const dur = L.Monde.solidite(Math.floor(j.x / L.TT), Math.floor(j.y / L.TT));
        const lieux = L.Monde.carte.points.map(function (p) {
            // ⚠️ Une carrosserie n'a pas de porte des pietons : sa porte est le rideau.
            const rideau = L.Monde.portesDeGarage().some(function (pg) {
                return pg.lieu === p.slug && pg.y === p.y - 1 && p.x >= pg.x && p.x < pg.x + pg.l;
            });
            // ⚠️ Un lot clôturé (le Salon Prestige) : son point est devant le PORTAIL, du côté de la rue — devant
            // la porte, on est déjà dans l'enclos (docs/jalons/les-concessionnaires-le-neuf-aux-erables-l-usage-
            // dans-les-friches.md, « Le lot devant, clôturé » ; `test_barrieres`). La porte du lot, elle, reste
            // dans l'axe : sur la même colonne, au nord du portail, et c'est une vraie porte.
            const portail = ((L.Monde.carte.def && L.Monde.carte.def.concessionnaires) || []).some(function (c) {
                const pt = c.portail;
                return pt && c.slug === p.slug && pt.y === p.y - 1 && p.x >= pt.x && p.x < pt.x + pt.l
                    && c.porte.x === p.x && c.porte.y < pt.y && !!L.Monde.porteA(c.porte.x, c.porte.y);
            });
            return [p.slug, L.Monde.solidite(p.x, p.y), !!L.Monde.porteA(p.x, p.y - 1) || rideau || portail];
        });
        return { dur: dur, lieux: lieux, zone: L.Monde.zoneA(j.x, j.y).slug,
                 horsCarte: L.Monde.porteA(-1, -1) };
    }""")
    assert r["dur"] in (0, 3), "le joueur apparait dans un mur"
    for slug, dur, porte in r["lieux"]:
        assert dur in (0, 3), f"{slug} : on ne peut pas s'en approcher"
        assert porte is True, f"{slug} : pas de porte au-dessus du point d'interet"
    assert r["zone"] == "faubourg"
    assert r["horsCarte"] is None


def test_le_cache_de_morceaux_ne_gonfle_pas_quand_on_traverse_la_ville(banc):
    """Un cache non borne, c'est 20 Mo de canevas et un telephone qui rame."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const j = L.B.joueur, c = L.Monde.carte;
        const vus = [];
        // On traverse la ville en diagonale, en rendant a chaque saut.
        for (let i = 0; i < 40; i++) {
            j.x = 40 + (c.pxW - 80) * i / 39;
            j.y = 40 + (c.pxH - 80) * i / 39;
            L.Monde.centrerCamera(j.x, j.y);
            L.Jeu.rendre();
            vus.push(L.B.stats.morceaux);
        }
        return { max: Math.max.apply(null, vus), plafond: L.Monde.MORCEAUX_MAX,
                 images: L.B.stats.images, fin: L.B.stats.morceaux };
    }""")
    assert r["max"] <= r["plafond"], f"{r['max']} morceaux en cache pour un plafond de {r['plafond']}"
    assert r["fin"] > 0 and r["images"] > 0


def test_le_son_survit_a_l_absence_d_audio(banc, paquet, collections_du_paquet):
    """Sous Node il n'y a pas d'AudioContext : le jeu doit jouer quand meme."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        L.Son.reveiller();
        const avant = L.B.t;
        for (const nom in L.Son.SFX) L.Son.SFX[nom]();
        L.Son.boucle('sirene', true); L.Son.boucle('sirene', false);
        o.tape('KeyD', 30);
        return { charges: L.Son.charges, pret: L.Son.pret(), contexte: L.Son.contexte,
                 avance: L.B.t > avant, sons: L.B.defs.audio.echantillons.length,
                 sansFichier: L.B.defs.audio.echantillons.filter(function (e) { return !e.fichiers.length; }).map(function (e) { return e.slug; }) };
    }""")
    assert r["contexte"] is None and r["pret"] is False
    assert r["charges"] == 0, "rien ne doit se charger sans AudioContext"
    assert r["avance"] is True, "la boucle s'est arretee sur un son"
    # ⚠️ Plus les sons des collections, qui voyagent avec leur catalogue (`audio.LIEUX_A_PART`) et rejoignent
    # le paquet a son arrivee (`Son.Lieu.declarer`).
    a_part = len(((collections_du_paquet or {}).get("sons") or {}).get("echantillons") or [])
    assert r["sons"] == len(paquet["audio"]["echantillons"]) + a_part
    assert r["sansFichier"] == [], f"sons declares sans fichier : {r['sansFichier']}"
