"""La prime d'une mission se voit et s'entend.

Martin, 22 sept. 2026 : « quand je reçois une prime pour une mission, je veux le voir
clairement et avec un son qui correspond à la prime ». Avant, la prime n'était qu'un
« +150 $ » dans la bande des messages — que le HUD tait pendant une scène, et la scène de
fin part dans la foulée : le chiffre ne s'affichait jamais. Et son son était le ding d'une
liasse ramassée, recouvert par le jingle de mission.
"""
import re

import pytest

from app import audio, economie
from app.missions import CATALOGUE

SON_JS = (audio.RACINE_STATIQUE / "js" / "son.js").read_text(encoding="utf-8")
PALIERS = [p["slug"] for p in economie.PRIME_PALIERS]


@pytest.mark.parametrize("montant,palier", [
    (0, "petite"), (100, "petite"), (249, "petite"), (250, "moyenne"), (449, "moyenne"),
    (450, "grosse"), (799, "grosse"), (800, "gros_lot"), (5000, "gros_lot"),
])
def test_le_palier_d_une_prime(montant, palier):
    assert economie.palier_de_prime(montant) == palier


def test_les_paliers_montent_et_partent_de_zero():
    seuils = [p["des"] for p in economie.PRIME_PALIERS]
    assert seuils[0] == 0 and seuils == sorted(set(seuils))


def test_chaque_palier_se_gagne_et_le_gros_lot_est_rare():
    """Un palier qu'aucune mission n'atteint est un son que personne n'entendra ; un gros lot
    que la moitié des missions paient ne sonne plus comme un gros lot."""
    vus = [economie.palier_de_prime(m["recompense"]) for m in CATALOGUE]
    assert set(vus) == set(PALIERS), {p: vus.count(p) for p in PALIERS}
    assert vus.count("gros_lot") <= len(vus) // 10, vus.count("gros_lot")


@pytest.mark.parametrize("palier", PALIERS)
def test_chaque_palier_a_sa_synthese_et_sa_recette_en_attente(palier):
    """Le mp3 viendra d'ElevenLabs (quota à sec le 22 sept. 2026) : sa recette attend HORS du
    catalogue (qui ne déclare jamais un son sans fichier) ; d'ici là, la synthèse joue seule."""
    recette = next(e for e in audio.EN_ATTENTE if e["slug"] == f"prime_{palier}")
    assert f"prime_{palier}" not in audio.SLUGS, "au catalogue, elle réclamerait un fichier absent"
    assert 0.5 <= recette["duree_s"] <= 30.0 and "no music" in recette["prompt"]
    assert re.search(rf"^    prime_{palier}: function \(\) {{ \S", SON_JS, re.M), palier


def test_la_prime_de_mission_se_voit_par_dessus_la_scene_et_sonne_a_sa_taille(banc, paquet):
    m1 = next(m for m in paquet["missions"] if m["slug"] == "m1")
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const B = L.B;
        B.menu && L.Hud.fermerMenu();
        L.Histoire.commencer('m1'); B.cinema = null; B.scene = null;
        // ⚠️ APRES `commencer` : lui aussi joue le jingle de mission, et c'est voulu.
        const sons = [];
        ['prime', 'argent', 'mission'].forEach(function (k) {
            const vrai = L.Son.SFX[k];
            L.Son.SFX[k] = function (x) { sons.push(k === 'prime' ? 'prime:' + x : k); return vrai.apply(null, arguments); };
        });
        B.mission.sansBosse = true;
        const avant = B.partie.argent;
        L.Histoire.reussir();
        const juste = Object.assign({}, B.prime);
        const scene = !!B.scene, msg = B.msg || '';
        o.frame(10);
        const monte = L.Hud.montantDeLaPrime(B.prime);
        o.frame(40);
        const arrive = L.Hud.montantDeLaPrime(B.prime);
        // La scene de fin fige la ville (un dialogue) : le bandeau, lui, continue.
        const P = L.Hud.PRIME, total = P.compte[juste.palier] + P.tenue + P.sortie;
        let n = 50;
        const t0 = B.t;
        while (B.prime && n < total + 20) { o.frame(1); n++; }
        return { gain: B.partie.argent - avant, juste: juste, scene: scene, msg: msg, sons: sons,
                 monte: monte, arrive: arrive, fini: B.prime, n: n, total: total, pasDeVille: B.t - t0 };
    }""")
    prime = m1["recompense"] + m1["recompense"] // 2
    assert r["gain"] == prime
    assert r["juste"]["montant"] == prime and r["juste"]["bonus"] == m1["recompense"] // 2
    assert r["juste"]["quoi"] == "MISSION RÉUSSIE" and r["juste"]["titre"] == m1["titre"]
    assert r["juste"]["palier"] == economie.palier_de_prime(prime)
    assert r["scene"], "la scène de fin est partie : c'est par-dessus elle que le bandeau doit se lire"
    assert r["sons"] == ["prime:" + economie.palier_de_prime(prime)], \
        "UN son, celui du palier : ni le ding de la liasse ni le jingle par-dessus"
    assert "$" not in r["msg"], "le « +150 $ » de la bande des messages fait double emploi"
    assert 0 < r["monte"] < prime, "le montant MONTE jusqu'à sa valeur"
    assert r["arrive"] == prime
    assert r["fini"] is None and r["n"] <= r["total"] + 1, "le bandeau s'en va, même pendant la scène"
    assert r["pasDeVille"] < r["n"] - 50, \
        "la ville s'est figée sous le dialogue de fin (sinon ce juge ne prouve pas que le bandeau ignore `B.t`)"


def test_un_gros_lot_prend_son_temps(banc):
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        L.B.menu && L.Hud.fermerMenu();
        const P = L.Hud.PRIME, dure = {};
        [[100, 'petite'], [300, 'moyenne'], [500, 'grosse'], [900, 'gros_lot']].forEach(function (x) {
            const palier = L.Missions.annoncerPrime(x[0], 'ESSAI', 'MISSION RÉUSSIE', 0);
            let n = 0;
            while (L.Hud.montantDeLaPrime(L.B.prime) < x[0] && n < 600) { o.frame(1); n++; }
            dure[palier] = n;
            L.B.prime = null;
        });
        return { dure: dure, rien: L.Missions.annoncerPrime(0, 'ESSAI', 'X', 0), prime: L.B.prime };
    }""")
    d = r["dure"]
    assert list(d) == PALIERS, "chaque montant tombe dans son palier, du JS comme du Python"
    assert d["petite"] < d["moyenne"] < d["grosse"] < d["gros_lot"], d
    assert r["rien"] is None and r["prime"] is None, "une prime nulle ne s'annonce pas"


def test_le_defi_reussi_passe_par_le_meme_bandeau(banc, paquet):
    tour = next(d for d in paquet["defis"] if d["slug"] == "tour")
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        L.B.menu && L.Hud.fermerMenu();
        const sons = [];
        const vrai = L.Son.SFX.prime;
        L.Son.SFX.prime = function (p) { sons.push(p); return vrai.apply(null, arguments); };
        L.Histoire.proposerDefi('tour');
        L.B.menu.items[0].faire();
        L.B.defi.t = 600;
        L.Histoire.finirDefi(true);
        return { prime: L.B.prime, sons: sons };
    }""")
    assert r["prime"]["montant"] >= tour["prime"]
    assert r["prime"]["quoi"] in ("DÉFI RÉUSSI", "DÉFI DU JOUR")
    assert r["sons"] == [economie.palier_de_prime(r["prime"]["montant"])]
