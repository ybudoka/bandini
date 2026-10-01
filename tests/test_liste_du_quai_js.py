"""La liste du quai — la quatrième des « quatre activités que le jeu n'a pas »
(docs/jalons/quatre-activites-que-le-jeu-n-a-pas.md).

Sven affiche quatre modèles ; on lui en livre un par jour, à l'arrêt au bout de sa jetée, sans bosse ;
la liste se renouvelle. Il paie mieux que le garage, jamais le neuf. Et elle s'ouvre après q14, _La liste du
Norvégien_ (Martin, 1er oct. 2026 : la fiche la donnait en récompense) — avant, Sven ne prend rien.
"""

import pytest

from app import economie, vehicules

REGLES = economie.LISTE_DU_QUAI


def test_la_liste_ne_demande_que_des_chars_que_la_ville_fait_rouler():
    for slug in REGLES["modeles"]:
        v = vehicules.par_slug(slug)
        assert v, slug
        assert not v.get("eau") and not v.get("sirene") and not v.get("police"), slug
    assert REGLES["nombre"] < len(REGLES["modeles"]), "la liste ne changerait jamais"
    assert economie.VENTE_FRACTION < REGLES["fraction"] < 1, "Sven paie mieux que le garage, jamais le neuf"


#: Au volant d'un modèle, à l'arrêt, au bout de la jetée de Sven.
AU_QUAI = """
  function auQuai(L, o, slug) {
    const B = L.B, j = B.joueur, M = L.Missions;
    const poste = M.posteDuQuai();
    if (j.dansVehicule) L.Vehicules.descendre(j, true);
    const v = o.char(slug, 0, 0, 0);
    L.Vehicules.monter(j, v);
    v.x = poste.x; v.y = poste.y; j.x = v.x; j.y = v.y; v.vitesse = 0; v.vx = 0; v.vy = 0;
    L.Entites.indexer();
    return v;
  }
"""


#: ⚠️ UN SEUL BANC pour les deux juges du navigateur (vague C, 28 sept. 2026) : la livraison se
#: joue, puis on relit la liste sous deux graines. `listeDuQuai(jour)` ne lit que le jour — c'est
#: la règle même que le second juge tient : une liste qui dépendrait d'autre chose (le dé, ou ce
#: que la livraison a changé) ferait différer les deux graines, ou le renouvellement.
@pytest.fixture(scope="module")
def _quai(banc):
    return banc("function (L, o) {" + AU_QUAI + """
        L.Jeu.commencer(); L.B.partie.jour = 21;  // ⚠️ EN JUILLET : l'hiver, motos et vélos sont remisés (test_motos_velos_remises_js.py)
        const B = L.B, M = L.Missions, p = B.partie;
        const liste = M.listeDuQuai(p.jour);
        // AVANT q14 : pas d'ardoise. Un modele de la liste, propre, a l'arret au bout de la jetee : rien.
        const jetee = L.Histoire.lieuDuPersonnage('sven');
        delete p.missionsFaites.q14;
        if (B.joueur.dansVehicule) L.Vehicules.descendre(B.joueur, true);
        const va = o.char(liste[0], 0, 0, 0); L.Vehicules.monter(B.joueur, va);
        va.x = jetee.x; va.y = jetee.y; B.joueur.x = va.x; B.joueur.y = va.y; va.vitesse = 0; va.vx = 0; va.vy = 0;
        L.Entites.indexer();
        let argent = p.argent; M.majQuai();
        const avantQ14 = { qui: M.donneurDuQuai(), paye: p.argent - argent, garde: B.joueur.dansVehicule === va,
                           info: M.texteDuQuai(B.joueur), livres: M.etatDuQuai().livres.length };
        p.missionsFaites.q14 = true;                            // sa liste, en recompense de q14
        const hors = ['auto', 'taxi', 'moto', 'camion', 'sport', 'luxe', 'cabriolet'].find(function (s) { return liste.indexOf(s) < 0; });
        // Un modele hors liste : rien.
        argent = p.argent;
        const v0 = auQuai(L, o, hors); M.majQuai();
        const horsListe = { paye: p.argent - argent, garde: !!B.joueur.dansVehicule };
        // Cabosse : refuse.
        const v1 = auQuai(L, o, liste[0]); v1.vie = v1.vieMax * 0.5; argent = p.argent; M.majQuai();
        const bosse = { paye: p.argent - argent, garde: B.joueur.dansVehicule === v1, msg: B.msg };
        // Propre : paye, le char part a Sven.
        const v2 = auQuai(L, o, liste[0]); argent = p.argent; M.majQuai();
        const livre = { paye: p.argent - argent, parti: B.entites.indexOf(v2) < 0, pied: !B.joueur.dansVehicule, attendu: M.prixAuQuai(liste[0]) };
        // Un autre modele de la liste, le meme jour : demain.
        const v3 = auQuai(L, o, liste[1]); argent = p.argent; M.majQuai();
        const memeJour = { paye: p.argent - argent };
        // Le lendemain : oui.
        p.jour += 1; argent = p.argent; M.majQuai();
        const lendemain = { paye: p.argent - argent };
        // La periode suivante : une autre liste, et le compte repart.
        const avant = M.listeDuQuai(p.jour).join();
        p.jour += B.defs.economie.liste_du_quai.renouvelle_jours;
        const apres = M.listeDuQuai(p.jour).join();
        const livraison = { liste: liste, horsListe: horsListe, bosse: bosse, livre: livre, memeJour: memeJour, lendemain: lendemain,
                            change: avant !== apres, livres: M.etatDuQuai().livres.length, info: M.texteDuQuai(B.joueur) };
        // Le second juge : la meme liste pour tout le monde, quelle que soit la graine.
        const graines = [];
        for (const g of [1, 4242]) { L.graine(g); graines.push([1, 5, 9, 13].map(function (j) { return M.listeDuQuai(j).join(); })); }
        return { avantQ14: avantQ14, livraison: livraison, graines: graines };
    }""")


def test_la_liste_s_ouvre_apres_q14(_quai):
    """Avant _La liste du Norvégien_, Sven n'a pas d'ardoise : au bout de sa jetée, un modèle de la liste, propre, à
    l'arrêt — il ne le prend pas, ne paie rien, et la ligne du bas se tait. (Le reste du banc : q14 faite.)"""
    assert REGLES["ouvre"] == "q14"
    r = _quai["avantQ14"]
    assert r["qui"] is None, f"Sven tient l'ardoise avant q14 : {r}"
    assert r["paye"] == 0 and r["garde"] and r["livres"] == 0, f"Sven prend un char avant q14 : {r}"
    assert r["info"] is None, f"la ligne du bas dit la liste avant q14 : {r}"


def test_une_livraison_par_jour_sans_bosse_et_la_liste_se_renouvelle(_quai):
    r = _quai["livraison"]
    assert len(r["liste"]) == REGLES["nombre"] and len(set(r["liste"])) == REGLES["nombre"], r["liste"]
    assert r["horsListe"]["paye"] == 0 and r["horsListe"]["garde"], r
    assert r["bosse"]["paye"] == 0 and r["bosse"]["garde"], r
    assert r["livre"]["paye"] == r["livre"]["attendu"] > 0 and r["livre"]["parti"] and r["livre"]["pied"], r
    assert r["memeJour"]["paye"] == 0, "deux livraisons le même jour"
    assert r["lendemain"]["paye"] > 0, r
    assert r["change"] and r["livres"] == 0, r
    assert r["info"] and r["info"].startswith("LA LISTE DE SVEN"), r["info"]


def test_la_meme_liste_pour_tout_le_monde(_quai):
    r = _quai["graines"]
    assert r[0] == r[1]
    assert len(set(r[0])) > 1, "la liste ne se renouvelle jamais"
