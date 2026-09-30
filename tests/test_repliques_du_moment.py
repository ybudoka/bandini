"""Les répliques disent le bon moment (docs/jalons/les-repliques-disent-le-bon-moment.md).

⚠️ La Brume annonçait « Il est minuit passé sur le port » en plein midi, et le passant comme la
fille de la Brume lançaient « Fait frette, hein? » en pleine canicule (Martin, 30 sept. 2026).
Une réplique qui dit le froid porte `froid`, une qui dit l'heure porte `heures`, et un seul garde
(`Son.Voix.deSaison`) sert aux trois endroits où l'on choisit : le tirage des passants, le choix
de la fille de la Brume, le tour de rôle des ondes.
"""

import re

from app import audio, saisons

#: Le froid qu'on dit. ⚠️ « Bière frette » est une bière, pas un temps : il n'y est pas.
_MOTS_DU_FROID = re.compile(r"\b(fait frette|fait froid|on gèle|on g[eè]le)\b", re.IGNORECASE)
#: L'heure qu'on dit.
_MOTS_DE_L_HEURE = re.compile(r"\b(minuit|midi)\b", re.IGNORECASE)

_ANIMATEURS = sorted({g for genres in audio.ONDES["stations"].values() for g in genres
                      if g.startswith("radio_")})


def test_une_replique_qui_dit_le_froid_le_porte():
    marquees = []
    for v in audio.VOIX:
        if _MOTS_DU_FROID.search(v["texte"]):
            assert v.get("froid") is True, f"{v['slug']} dit le froid par tous les temps : « {v['texte']} »"
            marquees.append(v["slug"])
    assert {"frette_h", "frette_b"} <= set(marquees)


def test_une_replique_qui_dit_l_heure_la_porte():
    for v in audio.VOIX:
        if _MOTS_DE_L_HEURE.search(v["texte"]):
            assert "heures" in v, f"{v['slug']} dit l'heure à toute heure : « {v['texte']} »"
        if "heures" in v:
            de, a = v["heures"]
            assert 0 <= de < a <= 24, f"{v['slug']} : {v['heures']}"


def test_a_toute_heure_sous_tout_ciel_l_animateur_a_de_quoi_dire():
    """Une réplique qui se tait ne laisse pas un disque rayé : à chaque heure et sous chaque
    ciel, chaque animateur garde au moins deux répliques."""
    for genre in _ANIMATEURS:
        for ciel in audio.METEOS:
            for h in range(24):
                dites = [v["slug"] for v in audio.VOIX if v["genre"] == genre
                         and v.get("meteo") in (None, ciel)
                         and ("heures" not in v or v["heures"][0] <= h < v["heures"][1])]
                assert len(dites) >= 2, f"{genre} à {h} h sous « {ciel} » : {dites}"


def test_le_paquet_porte_le_froid_et_l_heure():
    exporte = {v["slug"]: v for v in audio.exporter()["voix"]}
    for v in audio.VOIX:
        assert exporte[v["slug"]].get("froid") == v.get("froid"), v["slug"]
        assert exporte[v["slug"]].get("heures") == v.get("heures"), v["slug"]
    assert "frais" in saisons.HABITS, "le seuil du froid a changé de nom : `Voix.deSaison` le lit"


# --- Au banc ---------------------------------------------------------------------------------

#: Un jour d'été sans pluie à midi, et un jour de grand froid. ⚠️ L'année a quarante jours et le
#: jour 21 est le 1er JUILLET (`calendrier.MOIS`) : c'est l'été des juges de couleur, pas l'hiver.
_JOURS = """
    function jourDEte(L) {
        const H = L.B.defs.saisons.habits;
        for (let j = 1; j < 400; j++) {
            if (L.Saisons.paletteA(j, 0.5).froid < H.chaud && !L.Pluie.intensiteA(j, 0.5)) return j;
        }
        return null;
    }
    function jourDHiver(L) {
        const H = L.B.defs.saisons.habits;
        for (let j = 1; j < 400; j++) if (L.Saisons.paletteA(j, 0.5).froid >= H.grand_froid) return j;
        return null;
    }
"""


def test_personne_ne_dit_fait_frette_en_ete(banc):
    """Par le vrai chemin : `Voix.dire` d'un passant (avec ses mp3) et `Voix.choisir` de la fille
    de la Brume. L'été, « frette » ne sort jamais ; en janvier, il sort."""
    r = banc("""async function (L, o) {
        o.brancherAudio(true);
        L.Son.reveiller();
        await o.attendre(); await o.attendre(); await o.attendre();
        L.Jeu.commencer();
        L.Son.Voix.charger();
        for (let i = 0; i < 6; i++) await o.attendre();
        %s
        const V = L.Son.Voix;
        function ecouter(jour) {
            L.B.partie.jour = jour; L.B.partie.heure = 0.5;
            const passant = [], brume = [];
            let sauf = null;
            for (let i = 0; i < 150; i++) {
                V.dernierT = -99999;
                const s = V.dire('homme', 0, 0);
                if (s) passant.push(s);
                const b = V.choisir('brume', sauf);
                if (b) { brume.push(b.slug); sauf = b.slug; }
            }
            return { froid: L.Saisons.palette().froid, passant: passant, brume: brume };
        }
        const ete = jourDEte(L);
        return { ete: ete, juillet: ete && ecouter(ete), janvier: ecouter(jourDHiver(L)),
                 aTampon: !!V.liste().find(function (v) { return v.slug === 'frette_h' && v.fichier; }) };
    }""" % _JOURS)
    assert r["ete"], "aucun jour d'été en 400 jours"
    assert r["aTampon"], "frette_h n'a pas de mp3 : `dire` ne peut pas le dire, le juge ne mesure rien"
    ete, hiver = r["juillet"], r["janvier"]
    assert ete["passant"] and ete["brume"], f"personne ne parle l'été : {ete}"
    assert "frette_h" not in ete["passant"], f"un passant dit « fait frette » par {ete['froid']} de froid"
    assert "frette_b" not in ete["brume"], f"la fille de la Brume dit « fait frette » par {ete['froid']} de froid"
    assert "frette_h" in hiver["passant"], f"en janvier, plus personne ne dit qu'il fait frette : {hiver}"
    assert "frette_b" in hiver["brume"], f"en janvier, la fille de la Brume ne dit plus qu'il fait frette : {hiver}"


def test_la_brume_ne_dit_minuit_qu_apres_minuit(banc):
    """La Brume tourne vingt minutes à midi, puis à deux heures du matin, un jour clair. « Il est
    minuit passé » ne passe qu'à deux heures — et y passe."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const O = L.Son.Ondes, B = L.B;
        const CLES = ['enCours', 'dites', 'tours', 'station', 'prochaineT', 'n', 'policeT', 'derniers', 'bulletins'];
        const copie = function (x) { return x === undefined ? undefined : JSON.parse(JSON.stringify(x)); };
        const zero = {};
        CLES.forEach(function (k) { zero[k] = copie(O[k]); });
        function clair(j, h) {
            return !L.Pluie.intensiteA(j, h) && !L.Neige.intensiteA(j, h);
        }
        function ecouter(heure) {
            let j = 21;
            while (!clair(j, heure)) j++;
            B.partie.jour = j; B.partie.heure = heure;
            CLES.forEach(function (k) { O[k] = copie(zero[k]); });
            L.Son.Voix.enCours = null;
            B.partie.derniereManchette = null;
            L.Son.Radio.jouer('la_brume');
            for (let i = 0; i < 1200 * 60; i++) { B.t++; O.maj(); }
            return O.dites.map(function (d) { return d.slug; });
        }
        return { midi: ecouter(0.5), nuit: ecouter(2 / 24) };
    }""")
    assert r["midi"], "La Brume se tait à midi"
    assert "brume_nuit_r" not in r["midi"], f"« minuit passé » à midi : {r['midi']}"
    assert "brume_nuit_r" in r["nuit"], f"à deux heures du matin, La Brume ne dit plus l'heure : {r['nuit']}"
