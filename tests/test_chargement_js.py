"""Une barre de chargement, et l'icône qui tourne — côté jeu.

Demande de Martin (17 sept. 2026) : « je prendrais bien une barre de chargement
au lancement du jeu. et s'il y a des chargements dans le jeu, un petit icône
s'animant dans un coin de l'écran ».

⚠️ La barre du lancement se juge dans un vrai navigateur (`test_navigateur.py`) :
elle vit dans le DOM et suit de vrais octets. Ici, l'icône : le compte des
chargements (`Chargements`), le son qui s'y inscrit, et le HUD qui la montre
seulement quand ça dure — et jamais par-dessus autre chose.
"""


def test_un_chargement_se_compte_et_se_decompte_une_seule_fois(banc):
    """Chaque début rend SA fin : appelée deux fois, elle ne décompte qu'une fois ;
    et `suivre` décompte sur l'échec comme sur la réussite — sinon un son raté
    laisserait l'icône tourner pour toujours."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const C = L.Chargements, avant = C.nombre();
        const fin = C.debut();
        const pendant = C.nombre();
        fin(); fin();
        const apres = C.nombre();
        C.suivre(Promise.reject(new Error('rate'))).catch(function () {});
        C.suivre(Promise.resolve(1));
        const deux = C.nombre();
        return o.attendre().then(function () {
            return { avant: avant, pendant: pendant, apres: apres, deux: deux, fini: C.nombre() };
        });
    }""")
    assert r["pendant"] == r["avant"] + 1
    assert r["apres"] == r["avant"], "une fin appelee deux fois a decompte deux fois"
    assert r["deux"] == r["avant"] + 2
    assert r["fini"] == r["avant"], "un chargement rate ou reussi est reste compte"


def test_le_son_compte_ce_qu_il_telecharge(banc):
    """Le préchauffage des mp3 passe par le compte, jusqu'à ce que le corps soit lu."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        return o.attendre().then(function () {
            const C = L.Chargements, avant = C.nombre();
            const demandes = L.Son.prechauffer(['un-son-jamais-demande.mp3', 'un-autre.mp3']);
            const pendant = C.nombre();
            return o.attendre().then(function () { return o.attendre(); }).then(function () {
                return { demandes: demandes, avant: avant, pendant: pendant, apres: C.nombre() };
            });
        });
    }""")
    assert r["demandes"] == 2
    assert r["pendant"] == r["avant"] + 2, r
    assert r["apres"] == r["avant"], r


def test_l_icone_tourne_quand_ca_dure_et_s_efface_apres(banc):
    """⚠️ Pas au premier fichier : un bruitage déjà dans le cache se décode en
    quelques images, et une icône qui clignote à chaque coup de poing se lit
    comme un défaut. Un chargement bref ne la montre pas ; un long, oui ; et
    elle s'attarde un instant après le dernier, sans rester."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const C = L.Chargements;
        function vue() {
            L.Jeu.rendre();
            return L.Hud.ancres().find(function (a) { return a.nom === 'chargement'; }) || null;
        }
        // Rien ne charge : pas d'icone.
        o.frame(30);
        const auRepos = vue();
        // Un chargement bref : quatre images, et c'est fini.
        let fin = C.debut();
        for (let i = 0; i < 4; i++) { o.frame(1); L.Jeu.rendre(); }
        fin();
        const bref = vue();
        // Un chargement long.
        fin = C.debut();
        for (let i = 0; i < 40; i++) { o.frame(1); L.Jeu.rendre(); }
        const long = vue();
        const autres = L.Hud.ancres().filter(function (a) { return a.nom !== 'chargement'; });
        fin();
        for (let i = 0; i < 5; i++) { o.frame(1); L.Jeu.rendre(); }
        const sAttarde = vue();
        for (let i = 0; i < 40; i++) { o.frame(1); L.Jeu.rendre(); }
        return { auRepos: auRepos, bref: bref, long: long, sAttarde: sAttarde, eteinte: vue(),
                 autres: autres, VW: L.VW, VH: L.VH, reste: C.nombre() };
    }""")
    assert r["auRepos"] is None, "l'icone tourne alors que rien ne charge"
    assert r["bref"] is None, "un chargement de quatre images a fait clignoter l'icone"
    icone = r["long"]
    assert icone, "un long chargement ne montre rien"
    assert r["sAttarde"], "l'icone disparait a la seconde ou le chargement finit : elle clignotera"
    assert r["eteinte"] is None, "l'icone reste allumee alors que tout est charge"
    # Dans un coin, dans l'ecran, et par-dessus rien.
    assert icone["x"] <= 6 and icone["y"] + icone["h"] >= r["VH"] - 6, f"pas dans le coin bas-gauche : {icone}"
    assert 0 <= icone["x"] and icone["x"] + icone["l"] <= r["VW"] and icone["y"] + icone["h"] <= r["VH"]
    for autre in r["autres"]:
        chevauche = (icone["x"] < autre["x"] + autre["l"] and autre["x"] < icone["x"] + icone["l"]
                     and icone["y"] < autre["y"] + autre["h"] and autre["y"] < icone["y"] + icone["h"])
        assert not chevauche, f"l'icone passe sur « {autre['nom']} »"
    # ⚠️ Et elle laisse la boite de dialogue tranquille : celle-ci commence a x = 12.
    assert icone["x"] + icone["l"] <= 12, "l'icone mord sur la boite de dialogue"
