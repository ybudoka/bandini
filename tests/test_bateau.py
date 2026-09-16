"""Le bord de l'eau, 3e vague — l'eau porte enfin quelque chose.

⚠️ **La dette nommée depuis M3.** « Phase 2 » voulait dire « sans sprite et sans
trafic » : la fiche de la chaloupe existait depuis M3 — eau, friction 0,995,
adhérence 0,05, trois cercles — et rien ne l'avait jamais fait flotter. Il ne
manquait ni physique à part ni quai : **un dessin, et une règle de tuile**.
"""

from app import carte, vehicules


def test_la_chaloupe_est_du_parc_maintenant():
    """Plus un seul véhicule en phase 2 : le catalogue roule en entier."""
    b = next(v for v in vehicules.CATALOGUE if v["slug"] == "bateau")
    assert b["phase"] == 1, "la chaloupe est encore une promesse"
    assert b["eau"] is True
    # ⚠️ Elle ne naît PAS dans le trafic : une chaloupe qui suit une voie de la
    # rue Principale est exactement ce que la règle de tuile interdit.
    assert b["frequence"] == 0, "la chaloupe est entrée dans le trafic de rue"
    assert not [v for v in vehicules.CATALOGUE if v["phase"] != 1]


def test_la_ville_a_des_amarrages_et_ils_sont_sur_l_eau():
    """⚠️ **Contre la rive BÂTIE, jamais contre le sable** : on amarre à un quai,
    à un trottoir du port, à une allée — on ne s'amarre pas à une plage, on y
    échoue. Sans endroit où la trouver, un véhicule de plus au catalogue ne
    change rien à la ville."""
    ville = carte.exporter()
    places = ville["amarrages"]
    mini, maxi = carte.AMARRAGES["par_ville"]
    assert mini <= len(places) <= maxi, f"{len(places)} amarrages"
    sol = ville["sol"]
    for p in places:
        assert sol[p["y"]][p["x"]] == "~", f"un amarrage au sec en ({p['x']}, {p['y']})"
        rive = False
        for cx, cy in ((p["x"] + 1, p["y"]), (p["x"] - 1, p["y"]),
                       (p["x"], p["y"] + 1), (p["x"], p["y"] - 1)):
            glyphe = sol[cy][cx]
            prop = carte.LEGENDE[glyphe]
            if glyphe in ("~", "s") or prop.get("solide") or prop.get("route"):
                continue
            rive = True
        assert rive, f"l'amarrage en ({p['x']}, {p['y']}) ne touche aucune rive bâtie"
    ecart = carte.AMARRAGES["ecart"]
    for i, a in enumerate(places):
        for b in places[i + 1:]:
            assert abs(a["x"] - b["x"]) + abs(a["y"] - b["y"]) >= ecart, (a, b)


def test_aucun_amarrage_au_pied_d_un_pont():
    """Un char lancé qui traverse n'a pas à trouver une coque en travers — la
    même règle que le mobilier de grève, et elle avait été trouvée par le juge
    du pont lui-même."""
    ville = carte.exporter()
    garde = carte.GREVE["pont_ecart"]
    for pont in ville["ponts"]:
        for p in ville["amarrages"]:
            dedans = (pont["x"] - garde <= p["x"] < pont["x"] + pont["l"] + garde
                      and pont["y"] - garde <= p["y"] < pont["y"] + pont["h"] + garde)
            assert not dedans, f"un amarrage au pied du pont {pont['sens']}"


def test_une_coque_ne_roule_pas_sur_la_terre_et_un_char_ne_flotte_pas(banc, paquet):
    """⚠️ **LE JUGE QUI COMPTE**, et c'est toute la règle des deux mondes : le
    char est arrêté par les murs et **passe** sur l'eau (il coule, c'est son
    affaire) ; la coque est arrêtée par **tout ce qui n'est pas de l'eau**."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const c = L.Monde.carte, TT = L.TT;
        // Une tuile d'eau franche, et une tuile de trottoir franche.
        let eau = null, terre = null;
        for (let ty = 4; ty < c.h - 4 && (!eau || !terre); ty++) {
          for (let tx = 4; tx < c.w - 4 && (!eau || !terre); tx++) {
            if (!eau && L.Monde.estEau(tx, ty)) eau = { tx: tx, ty: ty };
            if (!terre && L.Monde.glyphe(tx, ty) === '.') terre = { tx: tx, ty: ty };
          }
        }
        const bateau = L.Vehicules.creer('bateau', eau.tx * TT + 8, eau.ty * TT + 8, 0, { etat: 'stationne' });
        const auto = L.Vehicules.creer('auto', terre.tx * TT + 8, terre.ty * TT + 8, 0, { etat: 'stationne' });
        return {
          // La coque : libre sur l'eau, arrêtée sur la terre.
          coqueSurEau: L.Vehicules.tuileInterdite(bateau, eau.tx, eau.ty),
          coqueSurTerre: L.Vehicules.tuileInterdite(bateau, terre.tx, terre.ty),
          // Le char : libre sur le trottoir ET sur l'eau (il coule ensuite).
          charSurTerre: L.Vehicules.tuileInterdite(auto, terre.tx, terre.ty),
          charSurEau: L.Vehicules.tuileInterdite(auto, eau.tx, eau.ty),
        };
    }""")
    assert r["coqueSurEau"] is False, "une chaloupe est arrêtée par l'eau"
    assert r["coqueSurTerre"] is True, "une chaloupe roule sur le trottoir"
    assert r["charSurTerre"] is False, "un char est arrêté par le trottoir"
    # ⚠️ Le char PASSE sur l'eau : c'est le fond de la baie qui l'arrête, pas
    # une façade invisible au bord de l'eau. `majNoyade` s'en charge.
    assert r["charSurEau"] is False, "l'eau est redevenue un mur pour les chars"


def test_une_chaloupe_flotte_au_lieu_de_couler(banc, paquet):
    """⚠️ `majNoyade` exempte déjà `def.eau` depuis que l'eau n'est plus un mur —
    et c'est sa fiche qui le dit, pas une classe écrite à part. Le juge le tient
    maintenant tout haut."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const c = L.Monde.carte, TT = L.TT;
        let eau = null;
        for (let ty = 6; ty < c.h - 6 && !eau; ty++) {
          for (let tx = 6; tx < c.w - 6 && !eau; tx++) {
            // Au large : de l'eau sur trois tuiles autour, pour que la coque
            // ne s'échoue pas pendant la mesure.
            let plein = true;
            for (let d = -2; d <= 2 && plein; d++) {
              if (!L.Monde.estEau(tx + d, ty) || !L.Monde.estEau(tx, ty + d)) plein = false;
            }
            if (plein) eau = { tx: tx, ty: ty };
          }
        }
        if (!eau) return { eau: false };
        // ⚠️ Le joueur se met AU BORD : `peupler` oublie tout véhicule trop
        // loin, et une coque oubliée par la distance ressemble à une coque
        // coulée — le juge aurait accusé la flottaison d'un oubli de cache.
        L.B.joueur.x = eau.tx * TT + 8; L.B.joueur.y = (eau.ty - 3) * TT + 8;
        L.Monde.centrerCamera(L.B.joueur.x, L.B.joueur.y);
        L.B.joueur.invincible = 99999;
        const v = L.Vehicules.creer('bateau', eau.tx * TT + 8, eau.ty * TT + 8, 0, { etat: 'stationne' });
        const a = L.Vehicules.creer('auto', eau.tx * TT + 8, (eau.ty + 1) * TT + 8, 0, { etat: 'stationne' });
        o.frame(300);
        return { eau: true,
                 coque: L.B.entites.indexOf(v) >= 0 && v.etat !== 'epave',
                 coule: v.coule || 0,
                 char: L.B.entites.indexOf(a) >= 0 && a.etat !== 'epave' };
    }""")
    assert r["eau"], "pas de plein large sur la carte"
    assert r["coque"], "la chaloupe a coulé"
    assert r["coule"] == 0, "la chaloupe s'enfonce (%s images)" % r["coule"]
    assert r["char"] is False, "un char posé au large n'a pas coulé"
