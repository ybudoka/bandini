"""`libere` et `calme` (M16) lus par la rue — la fiche : « `libere` retire la zone du gang et
`calme` retire l'hostilité, et les deux survivent à une sauvegarde ».

⚠️ Avant le 28 sept. 2026, `libere` n'était qu'une liste qu'on comptait (_Le Boss_ en veut
quatre) et `calme` n'était lu par personne. Pire : `faubourgLibere` (m5) coupait la naissance
des membres de TOUS les gangs — après m5, plus une Morue ni un Chevreuil ne sortait en ville."""

#: Planté au milieu d'une zone de gang, on compte ses membres qui naissent (hors mission).
COMPTER = """
  function compter(L, o, zone, arch, n) {
    const B = L.B, j = B.joueur, c = L.Histoire.resoudre('zone:' + zone, null);
    const nes = {};
    for (let i = 0; i < n; i++) {
      j.x = c.x; j.y = c.y; j.vx = 0; j.vy = 0;
      o.frame(1);
      for (const e of B.entites) if (e.type === 'pieton' && e.arch === arch && !e.mission) nes[e.id] = 1;
    }
    return Object.keys(nes).length;
  }
  function vider(L, arch) {
    L.B.entites.filter(function (e) { return e.type === 'pieton' && e.arch === arch; }).forEach(function (e) { L.Entites.retirer(e); });
  }
"""


def test_liberer_un_district_vide_la_zone_de_son_gang_et_pas_les_autres(banc):
    r = banc("function (L, o) {" + COMPTER + """
        L.Jeu.commencer(); L.graine(6);
        const B = L.B, p = B.partie; B.joueur.invincible = 1e6;
        // Le Faubourg libéré (m5) : les Morues, elles, tiennent encore les Quais.
        p.faubourgLibere = true; p.libere = ['faubourg'];
        const avant = compter(L, o, 'morues', 'morue', 3000);
        const cravates = compter(L, o, 'cravates', 'cravate', 3000);
        // Les Quais libérés : plus une Morue ne sort.
        p.libere.push('quais'); vider(L, 'morue');
        const apres = compter(L, o, 'morues', 'morue', 3000);
        // Et ça survit à une sauvegarde (le même `completer` que le chargement).
        const relue = L.Sauvegarde.completer(JSON.parse(JSON.stringify(p)), B.defs);
        return { avant: avant, cravates: cravates, apres: apres, relue: relue.libere,
                 chasse: L.Entites.gangChasse('morue') === false && L.Entites.gangChasse('morues') };
    }""")
    assert r["avant"] > 0, "après m5, les Morues ne sortent plus dans leur propre coin du port"
    assert r["cravates"] == 0, "le Faubourg libéré, des Cravates traînent encore dans leur zone"
    assert r["apres"] == 0, f"les Quais libérés, {r['apres']} Morue(s) sortent quand même"
    assert r["relue"] == ["faubourg", "quais"] and r["chasse"], r


def test_un_gang_calme_ne_saute_plus_sur_un_joueur_arme(banc):
    corps = """function (L, o) {
        L.Jeu.commencer(); L.graine(6);
        const B = L.B, p = B.partie, j = B.joueur; j.invincible = 1e6;
        p.calmes = %s;
        const c = L.Histoire.resoudre('zone:chevreuils', null);
        const place = L.Histoire.tuileLibre(c.x, c.y, 8);
        const e = L.Entites.creerPieton(place.x, place.y, L.Entites.archetype('chevreuil'));
        p.armes.batte = { mun: null, usure: 0 }; j.arme = 'batte'; p.arme = 'batte';
        let saute = false;
        for (let i = 0; i < 240 && !saute; i++) {
            j.x = e.x + 30; j.y = e.y; j.vx = 0; j.vy = 0;
            if (e.etat === 'attaque_joueur') saute = true;
            else if (e.etat !== 'flane') e.etat = 'flane';
            o.frame(1);
        }
        const relue = L.Sauvegarde.completer(JSON.parse(JSON.stringify(p)), B.defs);
        return { saute: saute, zone: (L.Monde.zoneA(e.x, e.y) || {}).gang || null, relue: relue.calmes };
    }"""
    fache = banc(corps % "[]")
    calme = banc(corps % "['chevreuils']")
    assert fache["zone"] == "chevreuils", fache
    assert fache["saute"] is True, "le juge ne voit pas un Chevreuil provoqué par une batte : il ne mord pas"
    assert calme["saute"] is False, "un gang calmé saute encore sur qui tient une arme"
    assert calme["relue"] == ["chevreuils"]
