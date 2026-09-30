"""Des chocs qui sonnent ce qu'ils frappent, et des pas qui sonnent le sol (30 sept. 2026).

_Demande de Martin :_ « ajoute plusieurs effets audio pour les différents impacts avec les
véhicules et aussi pour les pas sur les différentes surfaces » — tranché « Go + pas des passants ».

Avant : huit gestes de char jouaient la même tôle froissée (`choc`) — l'orignal, la clôture, la
barrière, la remorque qu'on accroche — et le passant renversé ne faisait AUCUN bruit ; un seul
`pas`, cuir sur béton, sur le sable, le quai, le tapis et dans trente centimètres de neige.

⚠️ Ces juges lisent le CÂBLAGE (quel son part à quel moment), pas les octets : la qualité des
fichiers se juge dans `test_audio.py`, et l'oreille de Martin décide du reste.
"""

import re
from pathlib import Path

from app import audio, carte, vehicules

RACINE_JS = Path(__file__).resolve().parent.parent / "static" / "js"


# --- Ce que Python garantit --------------------------------------------------------------------

def test_chaque_glyphe_ou_l_on_marche_a_son_pas():
    """Un glyphe neuf où l'on marche doit être RANGÉ : sinon il sonne le béton sans que personne
    l'ait décidé (une plage de galets neuve, un plancher de marbre)."""
    marchables = {g for g in carte.LEGENDE if carte.marchable(g)}
    assert set(audio.SOLS_DES_PAS) == marchables, set(audio.SOLS_DES_PAS) ^ marchables
    assert set(audio.SOLS_DES_PAS.values()) <= set(audio.SLUGS)


def test_les_sols_se_chargent_ensemble_et_le_beton_reste_au_premier_ecran():
    sols = set(audio.SOLS_DES_PAS.values()) - {"pas"}
    assert set(audio.LIEUX["pas"]) == sols | {"pas_neige"}
    for lieu, slugs in audio.LIEUX.items():
        assert "pas" not in slugs and "choc" not in slugs, f"le filet est dans un lieu : {lieu}"


def test_les_sols_voyagent_sans_le_beton(paquet):
    """Le paquet ne porte que les sols qui ne sont pas du béton : le reste est le défaut du JS."""
    sols = paquet["audio"]["sols_des_pas"]
    assert sols[","] == "pas_herbe" and sols["s"] == "pas_sable" and sols["u"] == "pas_carrelage"
    assert "." not in sols and "#" not in sols
    assert paquet["audio"]["pas_des_passants"] == audio.PAS_DES_PASSANTS


def test_chaque_choc_neuf_est_joue_quelque_part():
    """Un son payé que rien ne joue est un son perdu : chaque slug de `LIEUX["chocs"]` est nommé
    par un appel de `vehicules.js` ou par la matière d'un décor (`CHOC_DU_DECOR`, `son.js`)."""
    vehicules_js = (RACINE_JS / "vehicules.js").read_text(encoding="utf-8")
    son_js = (RACINE_JS / "son.js").read_text(encoding="utf-8")
    decor = son_js[son_js.index("const CHOC_DU_DECOR"):son_js.index("const SFX = {")]
    nommes = set(re.findall(r"choc\('([a-z_]+)'", vehicules_js)) | set(re.findall(r"'([a-z_]+)'", decor))
    manquants = set(audio.LIEUX["chocs"]) - nommes
    assert not manquants, f"payés, jamais joués : {manquants}"


def test_la_tole_froissee_ne_sert_plus_qu_au_carambolage_et_a_l_epave():
    """⚠️ LE juge de cette demande côté chocs : `Son.SFX.choc()` sans genre était partout. Il ne
    reste que l'épave (le char qui meurt) ; le carambolage passe `null` au-dessus du seuil."""
    source = (RACINE_JS / "vehicules.js").read_text(encoding="utf-8")
    assert source.count("Son.SFX.choc()") == 1, "un choc de char joue encore la tôle froissée sans dire ce qu'il frappe"
    assert "choc_leger_vitesse" in vehicules.PHYSIQUE and "atterrissage_vz_min" in vehicules.PHYSIQUE


# --- Ce que le navigateur en fait --------------------------------------------------------------

#: Une tuile de chaque glyphe voulu, et le sol entendu dessus. `hiver`/`neige` posent la saison :
#: ⚠️ une partie commence en JANVIER (voir « Un juge de couleur pose sa saison ») — sans ça, l'herbe
#: est sous la neige et le juge de l'herbe mesure l'hiver.
SOLS = """function (L, o) {
    L.Jeu.commencer();
    const c = L.Monde.carte, TT = L.TT, out = {};
    function trouver(g) {
        for (let y = 0; y < c.h; y++) for (let x = 0; x < c.w; x++) if (L.Monde.glyphe(x, y) === g) return [x, y];
        return null;
    }
    function sur(g, hiver, neige) {
        const t = trouver(g);
        if (!t) return 'absent';
        L.Saisons.enHiver = function () { return hiver; };
        L.Neige.couverture = function () { return neige; };
        return L.Son.solDuPas(t[0] * TT + 8, t[1] * TT + 8);
    }
    ['.', '#', ',', 's', 'g', 'Q'].forEach(function (g) { out['ete' + g] = sur(g, false, 0); });
    ['.', ',', 's'].forEach(function (g) { out['hiver' + g] = sur(g, true, 0); });
    out['tempete.'] = sur('.', true, 0.8);
    const t = trouver('.');
    L.Neige.deneiger(t[0], t[1], 0);
    out['deneige.'] = sur('.', true, 0.8);
    return out;
}"""


def test_le_pas_sonne_le_sol_sous_le_pied(banc):
    r = banc(SOLS)
    assert r["ete."] == "pas" and r["ete#"] == "pas", r
    assert r["ete,"] == "pas_herbe", r
    assert r["etes"] == "pas_sable", r
    assert r["eteg"] == "pas_gravier", r
    assert r["eteQ"] == "pas_bois", r


def test_l_hiver_la_terre_est_sous_la_neige_et_la_rue_deneigee_reste_nette(banc):
    """Tout l'hiver, l'herbe et le sable sont sous la neige ; le trottoir, lui, ne crisse qu'après
    une tempête — et plus du tout où la charrue vient de passer."""
    r = banc(SOLS)
    assert r["hiver,"] == "pas_neige" and r["hivers"] == "pas_neige", r
    assert r["hiver."] == "pas", r
    assert r["tempete."] == "pas_neige", r
    assert r["deneige."] == "pas", r


def test_le_joueur_qui_marche_demande_le_sol_de_ses_pieds(banc):
    """Le câblage de `majJoueur` : un pas d'herbe, en marchant pour vrai sur l'herbe."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        L.Saisons.enHiver = function () { return false; };
        L.Neige.couverture = function () { return 0; };
        const c = L.Monde.carte, TT = L.TT, j = L.B.joueur;
        let pre = null;
        for (let y = 4; y < c.h - 4 && !pre; y++) for (let x = 4; x < c.w - 12; x++) {
            let ok = true;
            for (let k = 0; k < 8; k++) if (L.Monde.glyphe(x + k, y) !== ',' || !L.Monde.marchablePieton(x + k, y)) ok = false;
            if (ok) { pre = [x, y]; break; }
        }
        if (!pre) return { pre: false };
        j.x = pre[0] * TT + 8; j.y = pre[1] * TT + 8;
        L.Monde.centrerCamera(j.x, j.y);
        const sols = [], vrai = L.Son.SFX.pas;
        L.Son.SFX.pas = function (sol) { sols.push(sol); return vrai.apply(null, arguments); };
        o.frame(1);
        L.Hud.fermerOnglets && L.Hud.fermerOnglets();
        o.touche('KeyD');
        for (let i = 0; i < 60; i++) o.frame(1);
        o.relacher('KeyD');
        return { pre: true, sols: sols };
    }""")
    assert r["pre"], "aucun pré de huit tuiles : le juge ne prouve rien"
    assert r["sols"], "on a marché sans un pas"
    assert "pas_herbe" in r["sols"], r["sols"]


PASSANTS = """async function (L, o) {
    o.brancherAudio(true);
    L.Jeu.commencer();
    L.Son.reveiller();
    const j = L.B.joueur, cfg = L.B.defs.audio.pas_des_passants;
    L.Monde.centrerCamera(j.x, j.y);
    const sols = [], vrai = L.Son.SFX.pas;
    L.Son.SFX.pas = function (sol) { sols.push(sol); return vrai.apply(null, arguments); };
    function passant(dx) { return { x: j.x + dx, y: j.y, pasDist: 0 }; }
    const out = {};
    L.B.t = 1000;
    L.Son.pasDePassant(passant(30), cfg.pas_px + 1);
    out.pres = sols.length;
    L.B.t = 1001;
    L.Son.pasDePassant(passant(cfg.portee_px + 10), cfg.pas_px + 1);
    out.loin = sols.length - out.pres;
    L.B.t = 1002;
    const n = sols.length;
    for (let k = 0; k < 5; k++) L.Son.pasDePassant(passant(20 + k), cfg.pas_px + 1);
    out.foule = sols.length - n;
    L.B.t = 1003;
    const e = passant(20), m = sols.length;
    L.Son.pasDePassant(e, cfg.pas_px / 2);
    out.demi = sols.length - m;
    L.Son.pasDePassant(e, cfg.pas_px / 2 + 1);
    out.entier = sols.length - m;
    out.parImage = cfg.par_image;
    return out;
}"""


def test_les_passants_tout_pres_font_leurs_pas_et_la_foule_ne_grele_pas(banc):
    r = banc(PASSANTS)
    assert r["pres"] == 1, f"un passant à côté ne fait pas de pas : {r}"
    assert r["loin"] == 0, f"on entend les pas d'un passant hors de portée : {r}"
    assert r["foule"] == r["parImage"], f"cinq passants dans la même image : {r}"
    assert r["demi"] == 0 and r["entier"] == 1, f"le pas ne suit pas la distance marchée : {r}"
