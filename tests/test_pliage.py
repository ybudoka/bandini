"""La carte pliée (docs/jalons/charger-les-districts-autour-du-joueur.md, vague 1).

La carte voyage EN COLONNES sur `/api/carte` (`app/pliage.py`) et le navigateur la déplie en arrivant
(`static/js/pliage.js`, dans `Jeu.chargerDefinitions`). Ce que ces juges tiennent, chacun la preuve d'une clé :

- déplier la carte qui voyage rend la ville À L'OCTET PRÈS (son JSON), côté Python ET côté navigateur ;
- le jeu, au banc, reçoit la carte pliée comme du serveur, et c'est la ville dépliée qu'il tient ;
- les plis eux-mêmes : les formes mêlées, les clés absentes, un booléen qui n'est pas un entier, les
  négatifs, les palettes trop grandes, les clés « x,y » qui ne se réécriraient pas pareil, et la marque
  qu'une carte ne doit jamais porter ;
- la carte pliée pèse ce qu'elle promet (le reste du poids : `test_definitions`).
"""

import gzip
import json

import pytest

import villes
from app import pliage
from harnais_js import lancer_node


def _json(v) -> str:
    return json.dumps(v, ensure_ascii=False, separators=(",", ":"), sort_keys=True)


def _comme_le_navigateur(v):
    """`v` tel que `JSON.stringify` l'écrirait : un flottant entier (`1.0`) s'y écrit `1`."""
    if isinstance(v, float) and v.is_integer():
        return int(v)
    if isinstance(v, list):
        return [_comme_le_navigateur(x) for x in v]
    if isinstance(v, dict):
        return {k: _comme_le_navigateur(x) for k, x in v.items()}
    return v


def _pareil(obtenu: str, attendu: str) -> tuple[bool, str]:
    """⚠️ Deux JSON de 700 Ko : `assert a == b` ferait calculer à pytest un écart qui ne finit pas. On dit
    seulement OÙ ils divergent."""
    if obtenu == attendu:
        return True, ""
    i = next((k for k, (a, b) in enumerate(zip(obtenu, attendu)) if a != b), min(len(obtenu), len(attendu)))
    return False, f"premier écart au caractère {i} : …{obtenu[max(0, i - 80):i + 40]}… au lieu de …{attendu[max(0, i - 80):i + 40]}…"


#: Des valeurs qui éprouvent chaque pli, et chaque raison de NE PAS plier.
CAS = {
    "formes_melees": [{"type": "arbre", "x": i, "y": 2 * i} if i % 3 else {"type": "banc", "x": -i, "y": i, "r": 4}
                      for i in range(20)],
    "cles_absentes_et_vides": [{} if i % 4 == 0 else {"a": i} for i in range(12)],
    "booleens_et_nuls": [{"panne": i % 2 == 0, "r": None if i % 5 else 3, "c": 1.5 * i + 0.25} for i in range(10)],
    "palette_trop_grande": [{"texte": f"MOT{i}"} for i in range(200)],
    "palette_repetee": [{"c": ["fenetre", "poteau", "vitrine"][i % 3]} for i in range(30)],
    "imbriquees": [{"arrets": [{"x": i, "y": k} for k in range(9)], "nom": "ligne"} for i in range(8)],
    "paires": [[i * 7 % 13, -i] for i in range(15)],
    "paires_courtes": [[1, 2], [3, 4]],
    "paires_melees": [[1, 2]] * 7 + [[1, True]],
    "arrets": {f"{x},{y}": "v^<>"[x % 4] for x in range(3) for y in range(-2, 2)},
    "arrets_zeros": {f"0{x},{y}": "v" for x in range(9) for y in range(1)},
    "courte": [{"x": 1}, {"x": 2}],
    "chaines": ["abc", "~", "#"],
    "legende": {"~": {"solide": 2}, ".": {}},
}


def test_plier_puis_deplier_rend_chaque_cas():
    for nom, valeur in CAS.items():
        pliee = pliage.plier(valeur)
        assert _json(pliage.deplier(pliee)) == _json(valeur), nom
    assert "~t" in pliage.plier(CAS["formes_melees"]) and "f" in pliage.plier(CAS["formes_melees"])
    assert "~p" in pliage.plier(CAS["paires"])
    assert "~xy" in pliage.plier(CAS["arrets"])
    # ⚠️ Ce qui ne se plierait pas sans perte reste tel quel.
    assert pliage.plier(CAS["arrets_zeros"]) == CAS["arrets_zeros"], "« 01,0 » ne se réécrit pas pareil"
    assert pliage.plier(CAS["paires_melees"]) == CAS["paires_melees"], "un booléen n'est pas un entier"
    assert pliage.plier(CAS["courte"]) == CAS["courte"]
    assert pliage.deplier(pliage.plier(CAS["booleens_et_nuls"]))[0]["panne"] is True


def test_plier_ne_touche_pas_a_ce_qu_il_plie():
    valeur = json.loads(_json(CAS))
    pliage.plier(valeur)
    assert _json(valeur) == _json(CAS)


def test_une_carte_qui_porte_une_marque_est_refusee():
    with pytest.raises(AssertionError, match="marque"):
        pliage.plier({"sol": [], "zones": {"~t": 1}})


def test_la_carte_qui_voyage_est_pliee_et_se_deplie_a_l_octet_pres(paquets):
    """⚠️ La ville ENTIÈRE, contre `definitions.assembler()` : ce qui voyage, une fois déplié, est ce que le
    navigateur tenait avant le pliage — moins les places des cartes de hockey (`/api/collections`), plus son
    empreinte."""
    pliee = json.loads(paquets.carte.corps)
    assert "~t" in pliee["decor"], "le décor ne voyage plus en colonnes"
    attendue = villes.assembler()["carte"]
    attendue.pop("collections", None)
    attendue["empreinte"] = paquets.carte.etag
    ok, ecart = _pareil(_json(pliage.deplier(pliee)), _json(attendue))
    assert ok, ecart


def test_la_carte_pliee_pese_moins(paquets):
    """La vague 1 promettait −18 Ko gzip (70 538 → 52 130 le 30 sept. 2026) : pas un octet de moins qu'un quart."""
    pliee = json.loads(paquets.carte.corps)
    avant = len(gzip.compress(_json(pliage.deplier(pliee)).encode("utf-8"), 6))
    apres = len(gzip.compress(paquets.carte.corps, 6))
    assert apres < 0.8 * avant, (avant, apres)


def _deplier_au_navigateur(pliee):
    """`Pliage.deplier` sous Node, seul (`static/js/pliage.js`), et son JSON."""
    from pathlib import Path
    source = (Path(__file__).resolve().parent.parent / "static" / "js" / "pliage.js").read_text(encoding="utf-8")
    return lancer_node(source + "\nprocess.stdout.write(JSON.stringify(Pliage.deplier(ENTREE)));\n", entree=pliee)


def test_le_navigateur_deplie_chaque_cas_comme_python():
    sortie = json.loads(_deplier_au_navigateur({nom: pliage.plier(v) for nom, v in CAS.items()}))
    for nom, valeur in CAS.items():
        assert _json(sortie[nom]) == _json(valeur), nom


def test_le_navigateur_deplie_la_ville_a_l_octet_pres(paquets):
    """Le JSON que `Pliage.deplier` rend, tel quel (`JSON.stringify`, l'ordre des clés compris), est celui de
    la ville dépliée par Python — l'ordre des clés d'un objet se lit, parfois (la légende, `familles`). Seule
    différence permise, celle de tout `JSON.parse` : un flottant entier s'écrit sans son `.0`."""
    sortie = _deplier_au_navigateur(json.loads(paquets.carte.corps))
    attendue = pliage.deplier(json.loads(paquets.carte.corps))
    ok, ecart = _pareil(sortie, _json(_comme_le_navigateur(attendue)))
    assert ok, ecart


def test_le_jeu_recoit_la_carte_pliee_et_tient_la_ville_depliee(banc, paquet, carte_pliee):
    """Au banc, `/api/carte` sert la carte PLIÉE, comme le serveur (`conftest.carte_pliee`) : la ville que le
    jeu tient (`B.defs.carte`, `Monde.carte.def`) est la ville dépliée."""
    assert "~t" in carte_pliee["decor"]
    r = banc("""function (L, o) {
        const servie = o.fetchs.find(function (f) { return String(f.url).indexOf('/api/carte') === 0; });
        const c = L.B.defs.carte, cles = {};
        // ⚠️ `Monde.charger` annote chaque croisement en place (son rang, son décalage de feux, son stop) :
        // on juge ce qui est ARRIVÉ, sans ce que le jeu y a écrit depuis.
        const annotes = ['i', 'decalage', 'feux', 'stop'];
        Object.keys(c).forEach(function (k) {
            cles[k] = JSON.stringify(k !== 'intersections' ? c[k] : c[k].map(function (inter) {
                const o = {};
                Object.keys(inter).forEach(function (q) { if (annotes.indexOf(q) < 0) o[q] = inter[q]; });
                return o;
            }));
        });
        return { cles: cles, ordre: Object.keys(c), meme: L.Monde.carte.def === c, demandee: !!servie };
    }""")
    assert r["demandee"] and r["meme"]
    attendue = _comme_le_navigateur(paquet["carte"])
    assert r["ordre"] == list(attendue)
    differentes = sorted(k for k in attendue if r["cles"][k] != _json(attendue[k]))
    assert not differentes, f"le jeu ne tient pas la ville que Python a pliée : {differentes}"
