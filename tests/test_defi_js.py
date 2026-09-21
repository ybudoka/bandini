"""Le defi du jour cote jeu (M14, 5e vague) : le serveur designe, le jeu paie — une fois par jour.

`app/defi.py` et `tests/test_defi.py` disent quel defi est celui d'aujourd'hui ; ici, ce que le
JEU en fait : l'annonce au titre, le menu du defi, la prime — et surtout tout ce qui ne doit
PAS arriver : un defi du jour sans reseau, un slug inconnu, deux primes le meme jour.

⚠️ Il n'y a pas de classement (voir le prologue de `static/js/defi.js`) : ces juges n'en cherchent pas.
"""

import json

import pytest

D1, D2 = "2026-09-20", "2026-09-21"


def du_jour(slug="tour", date=D1):
    """La reponse du serveur : `defi=` de la fixture `banc`."""
    return {"statut": 200, "corps": {"date": date, "defi": slug}}


@pytest.fixture(scope="module")
def defis(paquet):
    return {d["slug"]: d for d in paquet["defis"]}


#: Joue un defi comme le jeu le joue : le menu du panneau, COMMENCER, puis la victoire au chrono.
JOUER = """
      function gagner(L, o, slug) {
        L.Hud.fermerMenu && L.B.menu && L.Hud.fermerMenu();
        L.Histoire.proposerDefi(slug);
        L.B.menu.items[0].faire();          // COMMENCER
        L.B.defi.t = 600;
        const avant = L.B.partie.argent;
        L.Histoire.finirDefi(true);
        return L.B.partie.argent - avant;
      }
"""


def _demarre(corps, **kw):
    return "function (L, o) {" + JOUER + "L.Jeu.commencer();" + corps + "}"


# --- Ce que le titre dit -----------------------------------------------------------------


def test_le_titre_annonce_le_defi_du_jour_avec_sa_prime(banc, defis):
    r = banc("""function (L, o) {
        return o.attendre().then(function () { return o.attendre(); }).then(function () {
          const el = o.elements['defi-du-jour'];
          return { cache: el.hidden, texte: el.textContent, appels: o.defi.appels.length,
                   cookie: o.defi.appels[0].opts.credentials };
        });
    }""", defi=du_jour("tour"))
    assert r["cache"] is False
    assert r["texte"] == f"Défi du jour : {defis['tour']['titre']} — {defis['tour']['prime']} $"
    assert r["appels"] == 1
    assert r["cookie"] == "omit", "route publique : aucun cookie ne part"


def test_sans_reseau_le_titre_ne_dit_rien_et_le_jeu_joue(banc):
    """⚠️ Un bonus, jamais une condition : pas de reseau, pas de defi du jour — et JOUER joue."""
    r = banc("""function (L, o) {
        return o.attendre().then(function () { return o.attendre(); }).then(function () {
          L.Jeu.jouerPartie(1);
          o.frame(5);
          return { cache: o.elements['defi-du-jour'].hidden, texte: o.elements['defi-du-jour'].textContent,
                   duJour: L.Defi.duJour(), etat: L.B.etat };
        });
    }""")  # defaut du banc : le reseau est coupe
    assert r == {"cache": True, "texte": "", "duJour": None, "etat": "jeu"}


@pytest.mark.parametrize("reponse", [
    {"statut": 500, "corps": {"erreur": "bug"}},
    {"statut": 200, "corps": None},
    {"statut": 200, "corps": {}},
    {"statut": 200, "corps": {"date": D1}},
    {"statut": 200, "corps": {"defi": "tour"}},
    {"statut": 200, "corps": {"date": "20 septembre", "defi": "tour"}},
    {"statut": 200, "corps": {"date": D1, "defi": "un-defi-de-la-version-d-apres"}},
    {"statut": 200, "corps": {"date": D1, "defi": 7}},
    {"statut": 200, "corps": {"date": D1, "defi": "<img src=x onerror=alert(1)>"}},
])
def test_une_reponse_qu_on_ne_comprend_pas_vaut_pas_de_defi_du_jour(banc, reponse):
    """⚠️ Ce que dit le serveur se verifie : une date qui n'en est pas une, un defi que CE
    catalogue ne connait pas (version d'avant, d'apres), du HTML — ignore, comme s'il n'y en avait pas."""
    r = banc("""function (L, o) {
        return o.attendre().then(function () { return o.attendre(); }).then(function () {
          return { duJour: L.Defi.duJour(), cache: o.elements['defi-du-jour'].hidden,
                   texte: o.elements['defi-du-jour'].textContent };
        });
    }""", defi=reponse)
    assert r == {"duJour": None, "cache": True, "texte": ""}


# --- La prime : une fois par jour -----------------------------------------------------------


def test_le_defi_du_jour_paie_sa_prime_meme_s_il_est_deja_fait(banc, defis):
    """Les six defis ne paient qu'UNE fois — celui d'aujourd'hui repaie sa prime, une fois par jour."""
    prime = defis["tour"]["prime"]
    r = banc(_demarre("""
        L.B.partie.defisFaits.tour = { jour: 3, temps: 4000 };        // deja fait, un autre jour
        return o.attendre().then(function () { return o.attendre(); }).then(function () {
          const premier = gagner(L, o, 'tour');
          const memeJour = gagner(L, o, 'tour');
          return { premier: premier, memeJour: memeJour, noté: L.B.partie.defiDuJour };
        });
    """), defi=du_jour("tour", D1))
    assert r["premier"] == prime
    assert r["memeJour"] == 0, "le meme jour, pas deux fois"
    assert r["noté"] == {"date": D1, "slug": "tour", "temps": 600}


def test_premiere_fois_et_defi_du_jour_paient_la_somme_en_un_seul_versement(banc, defis):
    prime = defis["tour"]["prime"]
    r = banc(_demarre("""
        return o.attendre().then(function () { return o.attendre(); }).then(function () {
          const paye = gagner(L, o, 'tour');
          return { paye: paye, msg: L.B.msg };
        });
    """), defi=du_jour("tour"))
    assert r["paye"] == 2 * prime, "la prime de la premiere fois ET celle du jour"
    # ⚠️ UN seul `encaisser` : deux messages « +250 $ » se recouvriraient a l'ecran.
    assert f"+{2 * prime} $" in r["msg"] and "DÉFI DU JOUR" in r["msg"]


def test_un_autre_defi_ne_paie_pas_la_prime_du_jour(banc, defis):
    r = banc(_demarre("""
        return o.attendre().then(function () { return o.attendre(); }).then(function () {
          const premiere = gagner(L, o, 'saut');       // ce n'est PAS le defi d'aujourd'hui
          const encore = gagner(L, o, 'saut');
          return { premiere: premiere, encore: encore, noté: L.B.partie.defiDuJour };
        });
    """), defi=du_jour("tour"))
    assert r["premiere"] == defis["saut"]["prime"], "sa prime de premiere fois, comme avant"
    assert r["encore"] == 0
    assert r["noté"] is None, "la prime du jour n'est pas touchee"


def test_le_lendemain_le_defi_du_jour_repaie(banc, defis):
    """La date est celle du SERVEUR : le jour suivant, la meme partie peut retoucher la prime."""
    prime = defis["tour"]["prime"]
    r = banc(_demarre("""
        return o.attendre().then(function () { return o.attendre(); }).then(function () {
          const lundi = gagner(L, o, 'tour');
          const memeJour = gagner(L, o, 'tour');
          o.defi.repondre({ statut: 200, corps: { date: '""" + D2 + """', defi: 'tour' } });
          return L.Defi.actualiser().then(function () {
            return { lundi: lundi, memeJour: memeJour, mardi: gagner(L, o, 'tour'), noté: L.B.partie.defiDuJour.date };
          });
        });
    """), defi=du_jour("tour", D1))
    assert (r["memeJour"], r["noté"]) == (0, D2)
    assert r["lundi"] == 2 * prime and r["mardi"] == prime


def test_un_defi_de_plus_au_catalogue_ne_paie_pas_deux_fois_le_meme_jour(banc, defis):
    """⚠️ Deployer un defi change la rotation EN PLEINE JOURNEE : le meme jour, un autre defi du
    jour ne doit pas repayer — c'est la DATE qui est payee, pas le slug."""
    r = banc(_demarre("""
        return o.attendre().then(function () { return o.attendre(); }).then(function () {
          gagner(L, o, 'tour');
          o.defi.repondre({ statut: 200, corps: { date: '""" + D1 + """', defi: 'livraison' } });
          return L.Defi.actualiser().then(function () {
            return { premiere: gagner(L, o, 'livraison'), aPayer: L.Defi.aPayer('livraison') };
          });
        });
    """), defi=du_jour("tour", D1))
    assert r["premiere"] == defis["livraison"]["prime"], "sa prime de premiere fois, et pas celle du jour"
    assert r["aPayer"] is False


def test_un_defi_rate_ne_paie_rien_et_ne_note_rien(banc):
    r = banc(_demarre("""
        return o.attendre().then(function () { return o.attendre(); }).then(function () {
          L.Histoire.proposerDefi('tour');
          L.B.menu.items[0].faire();
          const avant = L.B.partie.argent;
          L.Histoire.finirDefi(false, 'TEMPS ÉCOULÉ');
          return { gain: L.B.partie.argent - avant, noté: L.B.partie.defiDuJour, a: L.Defi.aPayer('tour') };
        });
    """), defi=du_jour("tour"))
    assert r == {"gain": 0, "noté": None, "a": True}


# --- Le menu du defi ---------------------------------------------------------------------


def test_le_menu_du_defi_dit_ce_qu_on_va_toucher(banc, defis):
    prime = defis["tour"]["prime"]
    r = banc(_demarre("""
        return o.attendre().then(function () { return o.attendre(); }).then(function () {
          function sur(slug) { L.Histoire.proposerDefi(slug); const s = L.B.menu.sur; L.Hud.fermerMenu(); return s; }
          const avant = { jour: sur('tour'), autre: sur('saut') };
          gagner(L, o, 'tour'); gagner(L, o, 'saut');
          return { avant: avant, apres: { jour: sur('tour'), autre: sur('saut') } };
        });
    """), defi=du_jour("tour"))
    assert r["avant"] == {"jour": f"DÉFI DU JOUR · {2 * prime} $", "autre": f"{defis['saut']['prime']} $"}
    assert r["apres"] == {"jour": "DÉFI DU JOUR — RÉUSSI AUJOURD'HUI", "autre": "DÉJÀ RÉUSSI"}


# --- La partie s'en souvient -------------------------------------------------------------


def test_la_prime_du_jour_se_sauvegarde_et_une_vieille_partie_la_recoit_a_vide(banc):
    r = banc(_demarre("""
        return o.attendre().then(function () { return o.attendre(); }).then(function () {
          gagner(L, o, 'tour');
          L.Missions.sauvegarderPartie();
          const relue = L.Sauvegarde.completer(L.Sauvegarde.lire(1), L.B.defs);
          const vieille = L.Sauvegarde.completer({ jour: 5, argent: 10 }, L.B.defs);
          return { relue: relue.defiDuJour, vieille: vieille.defiDuJour };
        });
    """), defi=du_jour("tour", D1))
    assert r["relue"] == {"date": D1, "slug": "tour", "temps": 600}
    assert r["vieille"] is None


# --- Le rafraichissement -----------------------------------------------------------------


def test_le_titre_ne_redemande_pas_avant_dix_minutes_puis_redemande(banc):
    """Le titre revient souvent, le jour non : au plus une demande / 10 min — mais une page rouverte
    le lendemain matin ne doit pas annoncer le defi d'hier."""
    r = banc("""function (L, o) {
        const reel = Date.now;
        return o.attendre().then(function () { return o.attendre(); }).then(function () {
          const a = o.defi.appels.length;
          return L.Defi.rafraichir().then(function () {
            const b = o.defi.appels.length;                       // trop tot
            o.defi.repondre({ statut: 200, corps: { date: '""" + D2 + """', defi: 'saut' } });
            Date.now = function () { return reel() + L.Defi.REPOS_MS + 1000; };
            return L.Defi.rafraichir().then(function () {
              Date.now = reel;
              return { a: a, b: b, c: o.defi.appels.length, demain: L.Defi.duJour().slug,
                       titre: o.elements['defi-du-jour'].textContent };
            });
          });
        });
    }""", defi=du_jour("tour", D1))
    assert (r["a"], r["b"], r["c"]) == (1, 1, 2)
    assert r["demain"] == "saut" and "Grand Saut" in r["titre"]


def test_le_retour_au_titre_redemande_le_defi_du_jour(banc):
    r = banc("""function (L, o) {
        const reel = Date.now;
        return o.attendre().then(function () { return o.attendre(); }).then(function () {
          L.Jeu.jouerPartie(1); o.frame(3);
          Date.now = function () { return reel() + L.Defi.REPOS_MS + 1000; };
          L.Jeu.retourTitre();
          Date.now = reel;
          return o.attendre().then(function () { return { appels: o.defi.appels.length }; });
        });
    }""", defi=du_jour("tour"))
    assert r["appels"] == 2


def test_le_defi_du_jour_n_entre_jamais_dans_la_coquille_hors_ligne(client):
    """⚠️ Un defi garde par le travailleur passerait minuit sans le savoir — et `/api/defi` est un
    PREFIXE de `/api/definitions`, que la coquille garde, elle : la frontiere se juge."""
    from app import hors_ligne

    page = client.get("/").get_data(as_text=True)
    assert 'data-url-defi="/api/defi"' in page
    coquille = hors_ligne.coquille(page, "/")
    assert not [u for u in coquille if u.split("?")[0] == "/api/defi"], coquille
    assert any(u.startswith("/api/definitions") for u in coquille), "les definitions, elles, y sont"
    assert json.dumps(coquille)  # sérialisable, comme le travailleur la lit
