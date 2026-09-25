"""Les rabais gagnés en mission se paient vraiment moins cher (P1, 25 sept. 2026).

f02, f03 et s01 affichaient un rabais à leur récompense ; seul le kiosque le lisait.
Ces juges partent du CATALOGUE : une mission qui promet un rabais à une clé que le jeu
ne lit nulle part fait rougir le premier, sans qu'on ait à l'inscrire ici."""

import json

from app import missions

#: Comment on VOIT le prix d'une clé, au banc : une fonction JS qui rend un prix.
#: ⚠️ Une clé de `donne.rabais` absente d'ici est une promesse que personne ne tient.
OBSERVER = {
    "kiosque": "function (L) { return L.Missions.prixAmbulant(L.B.joueur, "
               "{ slug: 'x', tarif: 'hotdog' }); }",
    "armurerie": "function (L) { const i = L.Missions.menuArmurerie().items.find(function (x) {"
                 " return /\\$/.test(x.detail); }); return parseInt(i.detail, 10); }",
    "vetements": "function (L) { const i = L.Missions.menuVetements().items.find(function (x) {"
                 " return /\\$/.test(x.detail || ''); }); return parseInt(i.detail, 10); }",
    "fourriere": "function (L) { return L.Missions.prixRachat('luxe'); }",
    # Les pièces qui servent au comptoir du casse-croûte (`hotdog`) : le prix de la pièce.
    "cantine": "function (L) { L.B.interieur = { slug: 'cantine', nom: 'Cantine' };"
               " const i = L.Missions.menuDuPoint({ type: 'hotdog' }).items[0];"
               " L.B.interieur = null; return parseInt(i.detail, 10); }",
    "casse_croute": "function (L) { L.B.interieur = { slug: 'casse_croute', nom: 'Casse' };"
                    " const i = L.Missions.menuDuPoint({ type: 'hotdog' }).items[0];"
                    " L.B.interieur = null; return parseInt(i.detail, 10); }",
}


def _promis():
    return {cle: (m["slug"], v) for m in missions.CATALOGUE
            for cle, v in (m.get("donne", {}).get("rabais") or {}).items()}


def test_chaque_rabais_promis_par_une_mission_se_lit_quelque_part():
    orphelins = {cle: slug for cle, (slug, _) in _promis().items() if cle not in OBSERVER}
    assert not orphelins, f"des rabais que le jeu ne lit nulle part : {orphelins}"


def test_chaque_rabais_promis_baisse_le_prix_au_comptoir(banc):
    promis = _promis()
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const voir = %s, promis = %s, sortie = {};
        L.B.partie.argent = 100000;
        for (const cle in promis) {
            L.B.partie.rabais = {};
            const plein = voir[cle](L);
            L.B.partie.rabais[cle] = promis[cle];
            sortie[cle] = { plein: plein, rabais: voir[cle](L) };
        }
        return sortie;
    }""" % ("{" + ",".join(f"{json.dumps(k)}: {OBSERVER[k]}" for k in promis) + "}",
            json.dumps({k: v for k, (_, v) in promis.items()})))
    for cle, (slug, facteur) in promis.items():
        vu = r[cle]
        assert vu["plein"] > 0, f"{cle} : aucun prix à voir"
        assert abs(vu["rabais"] - vu["plein"] * facteur) <= 1 and vu["rabais"] < vu["plein"], (
            f"{slug} promet {cle} à {facteur}, et le prix passe de {vu['plein']} à {vu['rabais']}")


def test_on_paie_le_prix_affiche_pas_le_plein_prix(banc):
    """Le libellé ne suffit pas : c'est la caisse qui juge."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const p = L.B.partie;
        p.argent = 5000; p.rabais = {}; p.armes = {};
        const premier = function () { return L.Missions.menuArmurerie().items.find(function (x) { return /\\$/.test(x.detail); }); };
        const plein = parseInt(premier().detail, 10);
        p.rabais = { armurerie: 0.5 };
        const i = premier(), affiche = parseInt(i.detail, 10), avant = p.argent;
        i.faire();
        return { plein: plein, affiche: affiche, paye: avant - p.argent };
    }""")
    # `Math.round` arrondit 12,5 à 13 ; le `round` de Python, au pair (12).
    assert r["paye"] == r["affiche"] == int(r["plein"] * 0.5 + 0.5), r


def test_le_cafe_du_chauffeur_ne_suit_pas_le_joueur_chez_gus(banc):
    """Un palier `rabais` porte sa clé (le kiosque) : `avantage('rabais')` les confondait."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const p = L.B.partie;
        const gus = function () { return parseInt(L.Missions.menuArmurerie().items.find(function (x) {
            return /\\$/.test(x.detail); }).detail, 10); };
        const kiosque = function () { return L.Missions.prixAmbulant(L.B.joueur, { slug: 'x', tarif: 'hotdog' }); };
        p.rabais = {}; p.paliers = {};
        const avant = { gus: gus(), kiosque: kiosque() };
        p.paliers['taxi:25'] = true;
        return { avant: avant, apres: { gus: gus(), kiosque: kiosque() } };
    }""")
    assert r["apres"]["gus"] == r["avant"]["gus"], "le rabais du kiosque vaut aussi chez Gus"
    assert r["apres"]["kiosque"] < r["avant"]["kiosque"], "le palier du chauffeur ne baisse plus le kiosque"
