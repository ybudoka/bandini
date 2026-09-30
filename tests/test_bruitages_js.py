"""Générer les bruitages qui n'ont aucun équivalent payé (docs/jalons/les-bruitages-qui-n-ont-aucun-equivalent-paye.md).

Quatorze sons que `son.js` synthétisait faute de fichier ont leur échantillon, rangé dans un LIEU (`audio.LIEUX`) :
le premier geste qui le joue demande son lieu et garde sa synthèse ; les suivants ont le fichier."""

from app import audio

ATTENDUS = {
    "cloche": "foire", "sifflet_train": "foire",
    "rumeur_incendie": "incendie", "eau": "incendie",
    "borne_cassee": "borne", "borne_jet": "borne",
    "rideau_garage": "garage",
    "distributrice": "distributrice", "machine_brassee": "distributrice", "monnaie": "distributrice",
    "nid_de_poule": "chaussee", "conteneur": "chaussee", "tas": "chaussee", "plaque": "chaussee",
}


def test_chaque_bruitage_a_son_fichier_et_son_lieu():
    """Chacun est au catalogue, a son fichier, et vit dans UN lieu — celui qu'on attend."""
    catalogue = {e["slug"]: e for e in audio.CATALOGUE}
    for slug, lieu in ATTENDUS.items():
        assert slug in catalogue, slug
        assert audio.fichiers_presents(catalogue[slug]), f"{slug} : pas de fichier"
        lieux = [nom for nom, slugs in audio.LIEUX.items() if slug in slugs]
        assert lieux == [lieu], (slug, lieux)
    # Les deux sons TENUS sont des boucles ; les autres, des gestes brefs.
    assert {s for s in ATTENDUS if catalogue[s]["boucle"]} == {"rumeur_incendie", "borne_jet"}


def test_le_premier_geste_demande_son_lieu(banc):
    """Chaque geste, la première fois, demande le lieu de son son (sa synthèse joue en attendant). ⚠️ Les
    témoins : un son TENU à force nulle ne demande rien, et un son qui a déjà son fichier (le coup de poing,
    du premier écran) ne demande aucun lieu."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const S = L.Son, j = L.B.joueur, demandes = {};
        let courant = null;
        const vrai = S.Lieu.charger;
        S.Lieu.charger = function (l) { (demandes[courant] = demandes[courant] || []).push(l); };
        const gestes = {
            cloche: function () { S.SFX.cloche(); }, sifflet_train: function () { S.SFX.sifflet_train(); },
            rumeur_incendie: function () { S.SFX.rumeur_incendie(1); }, eau: function () { S.SFX.eau(); },
            borne_cassee: function () { S.SFX.borne_cassee(); }, borne_jet: function () { S.SFX.borne_jet(1); },
            rideau_garage: function () { S.SFX.rideau_garage(); },
            distributrice: function () { S.SFX.distributrice(); }, machine_brassee: function () { S.SFX.machine_brassee(); },
            monnaie: function () { S.SFX.monnaie(); }, nid_de_poule: function () { S.SFX.nid_de_poule(); },
            conteneur: function () { S.SFX.chantier('conteneur', j.x + 20, j.y, 260); },
            tas: function () { S.SFX.chantier('tas', j.x + 20, j.y, 300); },
            plaque: function () { S.SFX.chantier('plaque', j.x + 20, j.y, 300); },
            feuMuet: function () { S.SFX.rumeur_incendie(0); }, jetMuet: function () { S.SFX.borne_jet(0); },
            coup: function () { S.SFX.coup(); },
        };
        Object.keys(gestes).forEach(function (k) { courant = k; gestes[k](); });
        S.Lieu.charger = vrai;
        return demandes;
    }""")
    attendus = {slug: [lieu] for slug, lieu in ATTENDUS.items()}
    assert {k: v for k, v in r.items() if k in ATTENDUS} == attendus, r
    assert "feuMuet" not in r and "jetMuet" not in r, r
    assert "coup" not in r, r
