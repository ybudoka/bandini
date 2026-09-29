"""Des photos pour le Clairon, au banc (docs/jalons/des-photos-pour-le-clairon.md) : au déclic, le cadre se juge
(un char en feu cadré se vend, le même hors du cadre ne vaut rien) ; Louise achète une photo par jour ; la une du
lendemain nomme le sujet ; ta face en une, et la police t'a vu."""

from app import photos

OUTILS = """
  const TT = 16;
  function feu(L, x, y) {
    const v = L.Vehicules.creer('auto', x, y, 0, { etat: 'stationne', couleur: '#c0392b' });
    v.vie = v.vieMax * 0.1;
    return v;
  }
  function cadre(L, x, y) { return { x: x - 240, y: y - 135 }; }
"""


def test_un_char_en_feu_cadre_se_vend_et_le_meme_hors_du_cadre_ne_vaut_rien(banc):
    r = banc("function (L, o) {" + OUTILS + """
        L.Jeu.commencer();
        const B = L.B, P = L.Photos, j = B.joueur;
        const v = feu(L, j.x + 200, j.y);
        B.photo = { dx: 0, dy: 0, filtre: 0 };
        const dedans = P.declic(cadre(L, v.x, v.y)), gardee = Object.assign({}, B.partie.photo);
        B.partie.photo = null;
        const dehors = P.declic({ x: v.x + 2000, y: v.y + 2000 });
        const dit = B.photo.dit;
        // En vol : un char en l'air au-dessus du seuil.
        v.vie = v.vieMax; v.z = 20;
        const vol = P.juger(cadre(L, v.x, v.y));
        B.photo = null;
        return { dedans: dedans, gardee: gardee, dehors: dehors, dit: dit, vol: vol, jour: B.partie.jour };
    }""")
    assert r["dedans"] == "feu" and r["gardee"] == {"sujet": "feu", "prix": photos.SUJETS["feu"]["prix"], "jour": r["jour"]}, r
    assert r["dehors"] is None and "RIEN" in r["dit"], r
    assert r["vol"] == "vol", r


def test_une_poursuite_vaut_plus_a_chaque_etoile_et_toi_dedans_plus_encore(banc):
    r = banc("function (L, o) {" + OUTILS + """
        L.Jeu.commencer();
        const B = L.B, P = L.Photos, j = B.joueur;
        const flic = L.Vehicules.creer('police', j.x + 300, j.y, 0, { etat: 'stationne', couleur: '#ffffff' });
        flic.conducteur = 'police';
        B.recherche.etoiles = 2;
        const sans = P.juger(cadre(L, flic.x, flic.y));      // le joueur est a 300 px : hors du cadre (240 de demi-largeur)
        const prix = P.prix('poursuite');
        const avec = P.juger(cadre(L, (flic.x + j.x) / 2, j.y));
        B.recherche.etoiles = 0;
        const calme = P.juger(cadre(L, flic.x, flic.y));
        return { sans: sans, prix: prix, avec: avec, calme: calme };
    }""")
    assert r["sans"] == "poursuite" and r["prix"] == photos.SUJETS["poursuite"]["prix"] + 2 * photos.REGLES["par_etoile"], r
    assert r["avec"] == "toi", r
    assert r["calme"] not in ("poursuite", "toi"), "une auto-patrouille garée, sans étoile, n'est pas une poursuite"


def test_au_bouton_le_declic_du_mode_photo_juge_le_cadre(banc):
    """⚠️ Par le vrai bouton (Entrée capture) : un juge qui appellerait `declic` ne verrait pas le branchement."""
    r = banc("function (L, o) {" + OUTILS + """
        L.Jeu.commencer();
        const B = L.B, j = B.joueur;
        if (B.menu) L.Hud.fermerMenu();
        feu(L, j.x + 60, j.y);
        o.tape('Escape', 2);
        B.menu.items.find(function (i) { return i.libelle === 'MODE PHOTO'; }).faire();
        o.tape('Enter', 2);
        const photo = B.partie.photo, dit = B.photo && B.photo.dit;
        o.tape('Backspace', 2);
        return { photo: photo, dit: dit };
    }""")
    assert r["photo"] and r["photo"]["sujet"] == "feu", r
    assert "LOUISE" in r["dit"], r


def test_louise_achete_une_photo_par_jour_et_la_une_du_lendemain_la_nomme(banc):
    r = banc("function (L, o) {" + OUTILS + """
        L.Jeu.commencer();
        const B = L.B, p = B.partie, H = L.Histoire, V = L.Son.Voix, M = L.Missions;
        V.demandees.length = 0;
        H.parler('louise');
        const salut = V.demandees.slice(); B.dialogue = null;
        H.parler('louise');
        const rien = V.demandees.slice(-1)[0]; B.dialogue = null;
        p.photo = { sujet: 'feu', prix: 150, jour: p.jour };
        H.parler('louise');
        const menu = B.menu && B.menu.items.map(function (i) { return i.libelle + '|' + i.detail; });
        const avant = p.argent;
        B.menu.items[0].faire(); L.Hud.fermerMenu(); B.dialogue = null;
        const paye = p.argent - avant, achat = V.demandees.slice(-1)[0];
        p.photo = { sujet: 'vol', prix: 120, jour: p.jour };
        H.parler('louise');
        const deja = V.demandees.slice(-1)[0]; B.dialogue = null;
        // Le lendemain matin : la une.
        p.jour += 1;
        const une = L.Photos.ligneDuClairon();
        // Une photo d'avant-hier ne se vend plus.
        p.photo = { sujet: 'vol', prix: 120, jour: p.jour - 2 };
        H.parler('louise');
        const vieille = V.demandees.slice(-1)[0]; B.dialogue = null;
        return { salut: salut, rien: rien, menu: menu, paye: paye, achat: achat, deja: deja, une: une, vieille: vieille,
                 photoApres: p.photo };
    }""")
    assert "louise-clairon-salut" in r["salut"], r
    assert r["rien"] == "louise-clairon-rien", r
    assert r["menu"] == ["VENDRE : UN CHAR EN FEU|150 $"], r
    assert r["paye"] == 150 and r["achat"] == "louise-clairon-achat", r
    assert r["deja"] == "louise-clairon-deja", "une une par jour"
    assert r["une"] and photos.SUJETS["feu"]["titre"] in r["une"], r
    assert r["vieille"] == "louise-clairon-vieille" and r["photoApres"] is None, r


def test_ta_face_en_une_et_la_police_t_a_vu_le_lendemain(banc):
    r = banc("function (L, o) {" + OUTILS + """
        L.Jeu.commencer();
        const B = L.B, p = B.partie, P = L.Photos;
        L.Histoire.parler('louise'); B.dialogue = null;      // la premiere fois, elle se presente
        p.photo = { sujet: 'toi', prix: 300, jour: p.jour };
        P.vendre(); B.dialogue = null;
        B.recherche.etoiles = 0;
        const avant = P.matin();
        p.jour += 1;
        const matin = P.matin(), etoiles = B.recherche.etoiles, deuxFois = P.matin();
        return { avant: avant, matin: matin, etoiles: etoiles, deuxFois: deuxFois, une: P.ligneDuClairon() };
    }""")
    assert r["avant"] is False and r["matin"] is True and r["deuxFois"] is False, r
    assert r["etoiles"] >= photos.REGLES["etoiles_toi"], r
    assert "L'INSAISISSABLE" in r["une"], r
