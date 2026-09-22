"""VISER UNE CIBLE, c'est la gachette de droite — a pied.

Demande de Martin, 22 sept. 2026 : « le bouton RT doit servir pour viser une
cible au lieu du bouton 2 ». Sur sa 8BitDo en Bluetooth (disposition
`bt_dinput`), VISER etait le bouton 2 : un numero que DirectInput saute, que
rien sur la manette ne porte. L'aide disait « BOUTON 2 », et rien ne visait.

VISER suit maintenant la PEDALE DE GAZ du profil (`Entree`, `gachetteVise`) —
un bouton ou un axe, disposition sauvee ou reapprise. Au volant, la meme
gachette reste le gaz : `Combat` ne lit le verrou qu'a pied.

⚠️ Juges PAR LE BOUTON (`o.pad` + `o.frame`), jamais par `Combat.majCible` :
c'est le bouton qui etait casse, pas la fonction.
"""

#: Sa manette, telle que le navigateur la voit : pas de `mapping`, la croix sur
#: l'axe 9 (1.2857 au repos), les gachettes aux boutons 8 et 9.
MARTIN = """
    const REPOS = [0, 0, 0, 0, 0, 0, 0, 0, 0, 1.2857];
    function pad(o, boutons, axes) {
      const b = []; for (let k = 0; k <= 11; k++) b.push(boutons.indexOf(k) >= 0 ? 1 : 0);
      o.pad(axes || REPOS, b, { id: 'Pro Controller (Vendor: 057e Product: 2009)', mapping: '' });
      o.frame(2);
    }
    function surLaRue(L, o) {
      const j = L.B.joueur, ligne = o.ligneDroite();
      j.x = ligne.x; j.y = ligne.y;
      L.Monde.centrerCamera(j.x, j.y);
      L.Entites.indexer();
      return j;
    }
"""


def test_la_gachette_de_droite_vise_et_le_bouton_2_ne_fait_plus_rien(banc):
    """Sa disposition SAUVEE d'avant (`verrouiller: [2]`) : RT tapee verrouille
    le passant d'a cote, le 2 ne fait plus rien, et RT tenue deverrouille."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        %s
        const bloc = L.B.defs.manettes;
        const sauvee = JSON.parse(JSON.stringify(bloc.profils.find(function (q) { return q.slug === 'bt_dinput'; })));
        sauvee.boutons.verrouiller = [2];                 // ce que ses options gardent d'avant
        L.Entree.reglerManette(sauvee);
        L.B.options.manetteProfil = 'bt_dinput';
        const j = surLaRue(L, o);
        const cible = o.poser(null, 14, 0);
        pad(o, []);
        const menu = !!L.B.menu;
        pad(o, [2]); pad(o, []);
        const surDeux = j.cible || null;
        pad(o, [9]); pad(o, []);
        const surRT = j.cible === cible;
        for (let i = 0; i < 12; i++) pad(o, [9]);          // tenue : deverrouille
        const tenue = j.cible || null;
        pad(o, []);
        const apresTenue = j.cible || null;
        o.pad(null); o.frame(2);
        return { menu: menu, surDeux: surDeux === null, surRT: surRT,
                 tenue: tenue === null, apresTenue: apresTenue === null };
    }""" % MARTIN)
    assert r["menu"] is False, "un menu ouvert fige la ville : le juge ne mesurerait rien"
    assert r["surDeux"] is True, "le bouton 2 vise encore"
    assert r["surRT"] is True, "la gachette de droite ne vise pas le passant d'a cote"
    assert r["tenue"] is True, "RT tenue doit deverrouiller"
    assert r["apresTenue"] is True, "relacher apres l'avoir tenue re-verrouille (une tape de trop)"


def test_une_gachette_sur_un_axe_vise_aussi(banc):
    """Une gachette que le navigateur rend en AXE (reapprise comme GAZ) : VISER
    la suit — il n'y a rien d'autre a reapprendre."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        %s
        L.Entree.reglerManette({ gaz: { type: 'axe', i: 5, repos: -1, plein: 1 } });
        const j = surLaRue(L, o);
        const cible = o.poser(null, 14, 0);
        const repos = [0, 0, 0, 0, 0, -1];
        pad(o, [], repos);
        const presse = repos.slice(); presse[5] = 1;
        pad(o, [], presse); pad(o, [], repos);
        const vise = j.cible === cible;
        o.pad(null); o.frame(2);
        return { vise: vise };
    }""" % MARTIN)
    assert r["vise"] is True


def test_au_volant_la_gachette_reste_le_gaz(banc):
    """La meme gachette, dans un char : elle accelere, et ne verrouille rien."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        %s
        const bloc = L.B.defs.manettes;
        L.Entree.reglerManette(bloc.profils.find(function (q) { return q.slug === 'bt_dinput'; }));
        const j = surLaRue(L, o);
        o.poser(null, 0, 40);
        const v = o.char('auto', 0, 0, 0);
        v.aToi = true;
        L.Vehicules.monter(j, v);
        L.Entites.indexer();
        pad(o, []);
        for (let i = 0; i < 20; i++) pad(o, [9]);
        const vitesse = v.vitesse;
        pad(o, []);
        const cible = j.cible || null;
        o.pad(null); o.frame(2);
        return { vitesse: vitesse, cible: cible === null };
    }""" % MARTIN)
    assert r["vitesse"] > 0, "au volant, RT doit rester le gaz"
    assert r["cible"] is True, "au volant, RT a verrouille une cible"


def test_l_aide_montre_rt_pour_viser(banc):
    """L'ecran COMMANDES, a la manette de Martin : VISER UNE CIBLE se lit sur la
    gachette de droite (RT, lettres Xbox), plus « BOUTON 2 »."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        %s
        const bloc = L.B.defs.manettes;
        L.Entree.reglerManette(bloc.profils.find(function (q) { return q.slug === 'bt_dinput'; }));
        L.B.options.manetteProfil = 'bt_dinput';
        pad(o, []);
        const viser = L.Hud.lignesDAide(bloc.pages[0], 'manette').find(function (li) { return li.c === 'verrouiller'; });
        pad(o, [9]);
        const allumee = L.Hud.lignesDAide(bloc.pages[0], 'manette').find(function (li) { return li.c === 'verrouiller'; }).allume;
        o.pad(null); o.frame(2);
        return { texte: viser.glyphes.map(function (g) { return g.texte; }), pieces: viser.pieces, allumee: allumee };
    }""" % MARTIN)
    assert r["texte"] == ["RT"]
    assert r["pieces"] == ["gachette_d"]
    assert r["allumee"] is True, "appuyer sur RT n'allume pas la ligne VISER"
