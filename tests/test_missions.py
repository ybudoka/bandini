import re

from app import armes, audio, blocs, caisse, carte, casino, economie, ile, mantes, missions, pietons, tripot


def test_chaque_personnage_qu_on_aborde_dit_son_repos_de_sa_voix():
    """⚠️ Martin, 20 sept. 2026 : « fais parler les personnages ». Lulu, sans mission, disait
    « le Faubourg est tranquille » en silence — comme les autres. `civil` et `narrateur`
    n'ont pas de `ou` : on ne leur parle jamais, ils n'ont pas de repos."""
    assert [p["slug"] for p in missions.PERSONNAGES if p.get("ou")] == [
        "ti_guy", "thibodeau", "marco", "bouchard", "josee", "tipaul", "lulu", "raymonde", "ovila",
        "mo", "fern", "mado", "gege", "xavier", "lachance", "gus", "rosa", "ginette", "gilles",
        "bonimenteur", "sven", "berube", "mireille", "jeanne", "leo", "norbert", "irene", "maitre", "cindy", "diane", "jo", "bilodeau", "zed", "trappeur", "tiloup", "boulon",
        "prevost", "maire", "louise", "sal", "roy"]
    # Cindy n'est devant la cantine qu'entre q04 et q05, et q05 l'attend toujours : pas de repos, comme Ti-Guy.
    # Mireille (le DOJO DION) ouvre ses COURS a chaque fois : pas de repos, comme le -2 de Josee.
    # Ti-Guy s'en va apres m1 (il a m1 a donner tant qu'il est la) ; Josee ouvre le marche noir
    # apres M5 (`marche_noir.apres`) au lieu de dire son repos : pas de voix pour ce qui ne s'entend pas.
    attendus = [f"{qui}-repos-{n}" for qui in ("thibodeau", "marco", "bouchard", "josee", "tipaul", "lulu",
                                              "raymonde", "ovila", "mo", "fern", "mado", "gege",
                                              "xavier", "lachance", "gus", "rosa", "ginette", "gilles",
                                              "bonimenteur", "sven", "berube", "jeanne", "leo", "norbert", "irene",
                                              "maitre", "diane", "bilodeau", "zed", "trappeur", "tiloup",
                                              "boulon", "prevost", "maire", "sal", "roy")
                for n in (1, 2)
                # Le vieux maître n'arrive qu'après c04 (`arrive_apres`), bien après m5 : son premier repos ne
                # s'entend jamais.
                if (qui, n) not in (("josee", 2), ("maitre", 1), ("diane", 1), ("bilodeau", 1), ("zed", 1),
                                           ("trappeur", 1), ("tiloup", 1), ("boulon", 1), ("prevost", 1),
                                           ("maire", 1), ("sal", 1), ("roy", 1))]
    repos = missions.repliques_de_repos()
    assert [r["slug"] for r in repos] == attendus, "quarante-sept voix, pas quarante-huit"
    # ⚠️ Le même texte pour tous — sauf qui a le sien (`repos` : l'île, loin du Faubourg).
    for r in repos:
        p = missions.personnage(r["qui"])
        attendu = p.get("repos") or (missions.REPOS["texte"], missions.REPOS["texte_apres"])
        assert r["texte"] == attendu[int(r["slug"][-1]) - 1], r["slug"]
    assert {r["texte"] for r in repos if "repos" not in missions.personnage(r["qui"])} == {
        missions.REPOS["texte"], missions.REPOS["texte_apres"]}
    assert all(r["mission"] == "repos" and not r["telephone"] for r in repos)
    voix = {v["slug"]: v for v in audio.voix_repos()}
    assert set(voix) == {r["slug"] for r in repos}
    for slug, v in voix.items():
        assert v["voix"] == missions.personnage(v["qui"])["voix"], slug


def test_types_et_ordre():
    assert "aller" in missions.TYPES_OBJECTIFS
    # ⚠️ Sans `ordre_topologique() == sorted(...) or True` (toujours vrai) : l'ordre est
    # juge par `test_les_cinq_missions_se_suivent` et `test_pas_de_cycle`, le type de chaque
    # objectif par `test_chaque_mission_a_un_donneur_place_et_des_objectifs_lisibles`.
    for m in missions.CATALOGUE:
        # ⚠️ Une FIN DE PARTIE ne paie rien (M13) : on ne part pas avec une prime, on part avec
        # un générique. Seules les missions qui en jouent un sont à 0 $.
        assert m["recompense"] > 0 or (m.get("donne") or {}).get("generique"), m["slug"]
        assert set(m["echec"]) <= set(missions.ECHECS)


def test_pas_de_cycle(monkeypatch):
    monkeypatch.setattr(missions, "CATALOGUE", [
        {"slug": "a", "prerequis": ["b"]}, {"slug": "b", "prerequis": ["a"]},
    ])
    import pytest

    with pytest.raises(ValueError):
        missions.ordre_topologique()


def test_les_cinq_missions_se_suivent():
    # ⚠️ Les cinq missions de la v1 ouvrent la ville, dans cet ordre-là ; M16
    # pose ensuite son tronc (`m6` et `m97`) sur `m5`, sans le casser.
    assert [m["slug"] for m in missions.CATALOGUE][:5] == ["m1", "m2", "m3", "m4", "m5"]
    assert missions.ordre_topologique()[:5] == ["m1", "m2", "m3", "m4", "m5"]
    for precedente, mission in zip(missions.CATALOGUE[:5], missions.CATALOGUE[1:5]):
        assert mission["prerequis"] == [precedente["slug"]], "chaque mission de la v1 ouvre la suivante"
    # ⚠️ Trois défis de char depuis la v1, plus les trois jeux d'adresse de la
    # foire : un jeu d'adresse est un DÉFI, pas un moteur.
    # ⚠️ Et une course par quartier depuis le 22 sept. 2026 (le Tour du
    # Faubourg, plus les Érables, la Shop, les Quais et la Pointe).
    # ⚠️ Et, depuis le 23 sept. 2026, des défis qui se DÉBLOQUENT : les dix
    # d'avant restent les seuls qu'on a dès le départ.
    assert len([d for d in missions.DEFIS if not d.get("debloque")]) == 10
    assert sorted(d["district"] for d in missions.DEFIS if d.get("circuit")) == sorted(
        d["slug"] for d in carte.DISTRICTS if d["slug"] != "baie")
    assert len(missions.defis_de_foire()) == 3


#: Les bâtiments de l'île qu'on peut nommer (une porte à lieu) : on y accoste, on n'y marche pas depuis la ville.
LIEUX_DE_L_ILE = {f["slug"] for f in ile.BATIMENTS.values() if f.get("porte") in ("lieu", "visite")}


def _mot_d_enseigne(mot: str) -> bool:
    """Un mot que `Histoire.boutiquex` trouve : un genre de devanture, ou un mot peint sur une enseigne."""
    from villes import exporter

    import unicodedata

    def nu(t: str) -> str:
        return "".join(c for c in unicodedata.normalize("NFD", t.upper()) if unicodedata.category(c) != "Mn")

    devs = exporter()["devantures"]
    return any(nu(mot) in nu(d.get("texte") or "") for d in devs)


def test_chaque_mission_a_un_donneur_place_et_des_objectifs_lisibles():
    # ⚠️ Et les lieux des BLOCS (la villa, l'infiltration) : un lieu de mission peut être derrière un
    # passage — `blocs.erreurs` juge qu'on l'y rejoint à pied.
    # ⚠️ Et le Dragon d'or : un lieu garanti de la BANDE du nord (`casino.CASINO`), pas de `carte.SPECIAUX` — c01
    # y ramène le jeton. Et l'ÉCOLE LA MANTE (`mantes.SLUG`), posée par `mantes.poser` sur la bande : c07 y livre
    # Monsieur Bois.
    # Et la CAISSE POPULAIRE (`caisse.SLUG`, posée par `caisse.poser` sur la ville finie) : le casse, x01–x04.
    lieux = ({p["slug"] for p in carte.SPECIAUX.values()} | {"kiosque", "planque"} | set(blocs.lieux_des_blocs())
             | {casino.CASINO["slug"], mantes.SLUG, caisse.SLUG})
    # Les zones qu'un `ou: zone:<x>` peut nommer : celle de chaque gang (`pietons.GANGS`, que
    # `Histoire.resoudre` trouve dans `carte.zones`), plus le port et le Faubourg. ⚠️ Lue, pas
    # recopiée : la liste à la main n'avait appris `boulonneux` qu'avec s01, et q01 (les Morues,
    # 25 sept. 2026) l'a fait rougir pour une zone qui existait.
    zones = {"port", "faubourg"} | {g["zone"] for g in pietons.GANGS}
    for m in missions.CATALOGUE:
        perso = missions.personnage(m["donneur"])
        assert perso and perso["ou"], f"{m['slug']} : le donneur doit se tenir quelque part"
        assert m["objectifs"], m["slug"]
        for o in m["objectifs"]:
            assert o["type"] in missions.TYPES_OBJECTIFS
            assert o["texte"] == o["texte"].upper() and len(o["texte"]) <= 60, "l'objectif s'affiche en une ligne"
            if "lieu" in o:
                # ⚠️ Livrer une COQUE, c'est la ramener à son mouillage (`navires.py`) :
                # il n'y a pas de baie de garage sur l'eau, `carte.SPECIAUX` n'en sait rien.
                # Ou l'amarrer ailleurs, au pied d'un lieu connu (`amarrage:<lieu>`, m53).
                # ⚠️ Et l'île (arc I) : on y accoste sous un de ses bâtiments (`amarrage:hangar_ile`), jamais on n'y
                # marche depuis la ville — ses lieux ne sont que des amarrages (`ile.BATIMENTS`).
                amarre = o["lieu"].startswith("amarrage:") and o["lieu"].split(":", 1)[1] in (lieux | LIEUX_DE_L_ILE)
                assert o["lieu"] in lieux or amarre or o["lieu"].startswith(("mouillage:", "traversier:")), \
                    f"{m['slug']} : lieu inconnu {o['lieu']}"
            # `course` (p04) : ses points, des lieux que `Histoire.resoudre` connaît. ⚠️ Et `boutique:<mot>` (h06, les
            # trois comptoirs des ordonnances) : un mot d'ENSEIGNE (`Histoire.boutiquex`), jamais une porte qui
            # deviendrait lieu de mission — la ville ne glisse pas ; le mot doit être peint quelque part.
            for point in o.get("points", []):
                enseigne = point.startswith("boutique:") and _mot_d_enseigne(point.split(":", 1)[1])
                assert (point in lieux or point in ("pont", "bois", "foire") or enseigne
                        or point.startswith(("zone:", "rampe:"))), f"{m['slug']} : point de course inconnu {point}"
            for etape in o.get("par", []):
                assert etape in lieux, f"{m['slug']} : lieu du détour inconnu {etape}"
            if o.get("ou", "").startswith("zone:"):
                assert o["ou"][5:] in zones
            if o.get("groupe"):
                assert any(g["slug"] == o["groupe"] for g in pietons.GANGS)
            # `pieton` (q13, les matelots de Sven) : QUI on envoie — un piéton de mission, qui ne naît jamais dans
            # la foule (fréquence 0), sinon la mission changerait la rue.
            if o.get("pieton"):
                arch = next((p for p in pietons.CATALOGUE if p["slug"] == o["pieton"]), None)
                assert o["type"] == "tuer" and arch and arch["frequence"] == 0.0, f"{m['slug']} : pieton {o['pieton']}"
            if o.get("vehicule"):
                assert o["vehicule"] in {v["slug"] for v in __import__("app.vehicules", fromlist=["CATALOGUE"]).CATALOGUE}
        donne = m["donne"]
        if donne.get("arme"):
            assert armes.par_slug(donne["arme"]), donne["arme"]
        if donne.get("propriete"):
            assert any(p["slug"] == donne["propriete"] for p in economie.PROPRIETES)



def test_un_char_prete_dit_a_qui_il_est():
    """⚠️ Le taxi de M3 dort a `porte:garage` — la porte MEME du garage ou
    Ti-Guy rachete n'importe quel char gare devant. `prete` est ce qui l'en
    protege, et il est ICI, pas en JavaScript : le navigateur lit un slug de
    personnage et affiche son nom (« IL EST A MARCO »). Un char prete ne se
    vend jamais, ni pendant la mission ni apres."""
    pretes = [(m, o) for m in missions.CATALOGUE for o in m["objectifs"] if o.get("prete")]
    assert pretes, "aucun char prete : le taxi de Marco en est un"
    for m, o in pretes:
        assert o["type"] == "monter", f"{m['slug']} : seul le vehicule d'un objectif `monter` se prete"
        assert missions.personnage(o["prete"]), f"{m['slug']} : {o['prete']} n'est pas un personnage connu"
    taxi = next(o for m, o in pretes if m["slug"] == "m3")
    assert taxi["prete"] == missions.par_slug("m3")["donneur"] == "marco", "le taxi de M3 est a Marco"

def test_chaque_replique_a_une_voix_et_tient_en_deux_phrases():
    """⚠️ Ces textes sont la source des voix generees : un texte qui change
    regenere un fichier (au caractere). Court, quebecois, une voix connue."""
    vues = set()
    for r in missions.repliques():
        assert r["slug"] not in vues, "deux repliques avec le meme slug de voix"
        vues.add(r["slug"])
        perso = missions.personnage(r["qui"])
        assert perso, f"{r['slug']} : personnage inconnu"
        assert perso["voix"] and not perso["voix"].startswith("__")
        assert 8 <= len(r["texte"]) <= 110, r["slug"]
        assert r["texte"].count(". ") + r["texte"].count("! ") + r["texte"].count("? ") <= 2, \
            f"{r['slug']} : plus de deux phrases"
    # ⚠️ Le budget se juge PAR MISSION, jamais par un total global : les voix se
    # génèrent (et se paient) par tranche, et un nombre fixe obligerait à
    # retoucher ce test à CHAQUE mission ajoutée — exactement ce qu'on veut
    # arrêter. Ce qui reste borné ici, c'est qu'UNE mission ne déborde pas :
    # `REPLIQUES_PAR_MISSION` répliques au plus (les cinq de la v1 font 7–8),
    # et une réplique reste déjà bornée au-dessus (8–110 caractères, ≤ 2 phrases).
    # ⚠️ Relevé de 10 à 18 le 22 sept. 2026, sur demande de Martin (« des missions plus longues, le
    # plus possible ») : deux à quatre étapes de plus par mission, chacune avec sa réplique `pendant`,
    # et des intros et des fins plus étoffées — 11 à 14 répliques par mission après ce passage.
    REPLIQUES_PAR_MISSION = 18
    # ⚠️ m6 : quatre répliques de plus (la poignée de main de ses quatre contacts, `accueil`) — Martin,
    # 20 sept. 2026, « enrichir leur dialogue » : une chacune, donc 12. Un plafond par mission qui le
    # demande, jamais un plafond global relevé : les autres restent à 10.
    # ⚠️ m98, _Le Boss_ (M13, 29 sept. 2026) : la fin du jeu — six étapes et leurs six `pendant` (Josée, Zed,
    # Gros-Boulon, Bouchard, Norbert deux fois), la poignée de main du maire et les cinq phrases du générique : 21.
    PLAFONDS = {"m6": 20, "m98": 21}
    par_mission: dict[str, int] = {}
    for r in missions.repliques():
        par_mission[r["mission"]] = par_mission.get(r["mission"], 0) + 1
    # ⚠️ Un CHAPITRE (30 sept. 2026, docs/jalons/des-missions-en-chapitres.md) a le plafond d'une mission PAR ACTE :
    # La Pointe, six missions devenues six actes, garde leurs répliques.
    for m in missions.CATALOGUE:
        actes = sum(1 for o in m["objectifs"] if o["type"] == "acte")
        if actes:
            PLAFONDS[m["slug"]] = REPLIQUES_PAR_MISSION * actes
    for slug, n in par_mission.items():
        assert n <= PLAFONDS.get(slug, REPLIQUES_PAR_MISSION), (
            f"{slug} : {n} répliques pour un plafond de {PLAFONDS.get(slug, REPLIQUES_PAR_MISSION)} "
            "— une mission bavarde, c'est une voix de plus à générer par ligne"
        )
    # Le filet global suit le catalogue : il se détend tout seul quand on ajoute
    # une mission, et serre toujours la moyenne (~7 répliques/mission).
    plafond = REPLIQUES_PAR_MISSION * len(missions.CATALOGUE)
    assert 30 <= len(vues) <= plafond
    assert sum(len(r["texte"]) for r in missions.repliques()) < 75 * plafond, \
        "les répliques raccourcissent avec le nombre de missions, pas l'inverse"
    for m in missions.CATALOGUE:
        for partie in ("intro", "fin", "echec"):
            assert m["dialogue"][partie], f"{m['slug']} : pas de {partie}"
        if m["prerequis"]:
            assert m["dialogue"]["appel"], f"{m['slug']} : apres la premiere, le donneur appelle"
            assert all(ligne["qui"] == m["donneur"] for ligne in m["dialogue"]["appel"])


def test_chaque_donneur_a_son_mot_pour_t_interpeller():
    """⚠️ La bulle d'un donneur est ce qui le distingue d'un figurant : sans
    mot, Bouchard redevient un client de plus au fond du casse-croute. Le mot
    est court PAR FORCE (police 3x5 au-dessus d'une tete de 12 px de large), et
    il ne s'ecrit pas en JavaScript : ici, avec les autres repliques."""
    donneurs = {m["donneur"] for m in missions.CATALOGUE}
    for perso in missions.PERSONNAGES:
        assert "heler" in perso, f"{perso['slug']} : pas de mot de bulle"
        mot = perso["heler"]
        assert len(mot) <= missions.HELER_MAX, f"{perso['slug']} : « {mot} » deborde de sa bulle"
        if perso["slug"] in donneurs:
            assert mot, f"{perso['slug']} donne une mission : il doit pouvoir t'interpeller"
    # Le client du taxi hele lui aussi — c'est le meme geste, au bord du trottoir.
    assert missions.personnage("civil")["heler"], "le client du taxi doit lever le bras"
    assert not missions.personnage("narrateur")["heler"], "le narrateur n'est nulle part : il ne hele personne"


# --- Les dix-huit défis au doigt, à la manette et au clavier (23 sept. 2026) ----------------


def test_chaque_defi_dit_avec_quoi_il_se_joue():
    """`appareils` : une liste non vide, sans doublon, prise parmi les trois ; les dix de la v1
    se jouent avec les trois. Et un défi qui en EXCLUT un le fait pour une raison écrite dans
    le catalogue — ce juge-ci ne lit pas les commentaires, il en tient la liste."""
    for d in missions.DEFIS:
        assert d["appareils"], d["slug"]
        assert len(set(d["appareils"])) == len(d["appareils"])
        assert set(d["appareils"]) <= set(missions.APPAREILS), d["slug"]
        if not d.get("debloque"):
            assert sorted(d["appareils"]) == sorted(missions.APPAREILS), d["slug"]
    exclus = {d["slug"]: sorted(set(missions.APPAREILS) - set(d["appareils"])) for d in missions.DEFIS}
    assert {s: e for s, e in exclus.items() if e} == {
        "danse": ["doigts"], "crochet": ["clavier"], "coffre": ["clavier"],
        "lait": ["clavier"], "remorquage": ["clavier"]}


def test_ce_qui_debloque_un_defi_existe():
    slugs = {d["slug"] for d in missions.DEFIS}
    faites = {m["slug"] for m in missions.CATALOGUE}
    for d in missions.DEFIS:
        r = d.get("debloque")
        if not r:
            continue
        assert set(r) <= {"defis", "missions", "apres"}, d["slug"]
        assert r.get("defis", 1) >= 1
        assert set(r.get("missions", [])) <= faites, d["slug"]
        assert set(r.get("apres", [])) <= slugs - {d["slug"]}, d["slug"]
        # ⚠️ Un défi qu'on attend doit s'ouvrir AVANT lui (ou être là dès le départ).
        for autre in r.get("apres", []):
            assert missions.DEFIS.index(next(q for q in missions.DEFIS if q["slug"] == autre)) \
                < missions.DEFIS.index(d), d["slug"]


def test_un_defi_neuf_ne_nomme_aucune_porte_neuve():
    """⚠️ `devants.lieux_de_mission` lit ce catalogue : une porte que rien ne nommait avant
    élargirait son devant, et toute la ville glisserait. Un défi qui se débloque ne se plante
    que devant une porte qu'une mission, un personnage ou un défi de la v1 nomme déjà."""
    deja = set()
    for m in missions.CATALOGUE:
        deja |= set(__import__("re").findall(r"porte:([a-z_]+)", repr(m)))
        deja |= {o["lieu"] for o in m["objectifs"] if o.get("lieu")}
    for d in missions.DEFIS:
        if not d.get("debloque") and d["ou"].startswith("porte:"):
            deja.add(d["ou"][6:])
    for p in missions.PERSONNAGES:
        if p["ou"].startswith("porte:"):
            deja.add(p["ou"].split(":")[1])
    for d in missions.DEFIS:
        if d.get("debloque") and d["ou"].startswith("porte:"):
            assert d["ou"][6:] in deja, d["slug"]
        if d["ou"].startswith("foire:"):
            assert d["ou"][6:] in carte.FOIRE["kiosques"] + carte.FOIRE["jeux"], d["slug"]


def test_une_epreuve_a_ses_regles_et_se_joue_debout():
    for d in missions.DEFIS:
        if d.get("epreuve"):
            assert d.get("a_pied") and isinstance(d.get("regles"), dict) and d.get("consigne"), d["slug"]
            assert d["chrono_s"] > 0 and 0 < d["prime"] <= 150, d["slug"]


def test_toute_mission_qui_a_des_prerequis_s_annonce_au_telephone():
    """⚠️ `histoire.js` choisit la mission qui va sonner sur ses PREREQUIS seuls, depuis
    que les repliques ont quitte le paquet (24 sept. 2026) : il ne peut plus regarder
    `m.dialogue.appel.length`, qui n'y est plus.

    C'etait deja une tautologie — la seule mission sans replique d'appel est la
    premiere, et elle n'a pas de prerequis — mais une tautologie que rien ne tenait.
    Celle-ci la tient : une mission avec des prerequis et sans appel ne sonnerait jamais,
    et le joueur attendrait un telephone muet.

    ⚠️ Et l'inverse : une mission SANS prerequis qui ecrirait un appel l'ecrirait pour
    rien — personne n'irait le chercher."""
    for mission in missions.CATALOGUE:
        appel = mission["dialogue"].get("appel") or []
        assert bool(mission.get("prerequis")) == bool(appel), (
            f"{mission['slug']} : prerequis={mission.get('prerequis')} et {len(appel)} replique(s) d'appel"
        )


def test_ce_qu_on_vient_obtenir_se_trouve():
    """`obtenir` (l'infiltration) : un objet qui a un nom de sac, un dessin connu, et un endroit où le
    trouver — un lieu, ou la poche d'un garde qui fait sa ronde dans le bloc de ce lieu. Sans endroit,
    l'objectif attendrait un objet qui n'est nulle part ; un garde inconnu n'en porterait aucun."""
    lieux = blocs.lieux_des_blocs()
    vus = 0
    for m in missions.CATALOGUE:
        for o in m["objectifs"]:
            if o.get("objet"):
                assert re.fullmatch(r"[a-z_]+", o["objet"]), (m["slug"], o["objet"])
            if o["type"] != "obtenir":
                continue
            vus += 1
            assert o.get("objet") and o.get("ou"), f"{m['slug']} : `obtenir` veut un `objet` et un `ou`"
            assert o.get("dessin", "sac") in missions.DESSINS_D_OBJET, (m["slug"], o.get("dessin"))
            # ⚠️ Un objet qui vient d'une TABLE de jeu (c02 : les dés du Pouce, glissés au sous-sol) : la table doit
            # le donner — sinon rien ne le mettrait jamais dans le sac, et rien ne le pose en ville non plus.
            # La CAISSE POPULAIRE (le casse, x01–x04) donne aussi : chaque objet de `caisse.OBJETS` (`caisse.js`).
            if o.get("table"):
                donne = {"tripot": {tripot.PREUVE["objet"]}, "caisse": set(caisse.OBJETS)}.get(o["table"], set())
                assert o["objet"] in donne, f"{m['slug']} : la table {o['table']!r} ne donne pas {o['objet']!r}"
                assert not o.get("garde"), f"{m['slug']} : un objet de table n'est dans aucune poche"
            if o.get("garde"):
                bloc = blocs.par_slug(lieux[o["ou"]])
                gardes = {g["slug"]: g for g in bloc.get("gardes", ())}
                assert o["garde"] in gardes, f"{m['slug']} : aucun garde {o['garde']!r} à {bloc['slug']}"
                assert gardes[o["garde"]].get("porte") == o["objet"], \
                    f"{m['slug']} : le garde {o['garde']} n'a pas {o['objet']} dans la poche"
    assert vus, "aucune mission n'obtient rien : le juge est à vide"


def test_le_paquet_ne_porte_pas_l_echec_ni_la_phase_qui_valent_leur_defaut():
    """M16, le reste (30 sept. 2026) : `"echec":["mort","arrete"]` et `"phase":1` se répétaient dans chaque mission
    du paquet ; le navigateur remet l'échec par défaut (`Histoire.echecsDe`) et ne lit pas la phase d'une mission.
    Ce qui ne vaut PAS son défaut voyage : m3 rate si le taxi de Marco est détruit."""
    paquet = {m["slug"]: m for m in missions.pour_le_navigateur()}
    d05 = paquet["d05"]
    assert missions.par_slug("d05")["echec"] == ["mort", "arrete"]
    assert "echec" not in d05 and "phase" not in d05, d05
    assert paquet["m3"]["echec"] == ["arrete", "vehicule_detruit"]
    # Et ce qu'elle donne voyage avec la mission (`pour_jouer`) : il ne se lit qu'en la réussissant.
    assert "donne" not in d05, d05
    assert missions.pour_jouer("d05")["donne"] == missions.par_slug("d05")["donne"]


def test_si_et_sauf_nomment_une_mission_et_ne_touchent_ni_le_depart_ni_les_scenes():
    """`si`/`sauf` (le casse, 1er oct. 2026) : ce qu'on a préparé change la suite. Ils nomment une mission du catalogue ;
    jamais sur le PREMIER objectif (la mission doit commencer quelque part) ; sur une réplique, seulement `pendant` — les
    scènes d'intro et de fin choisissent leurs répliques par leur rang, et une réplique tue le décalerait."""
    slugs = {m["slug"] for m in missions.CATALOGUE}
    vus = 0
    for m in missions.CATALOGUE:
        for k, o in enumerate(m["objectifs"]):
            for cle in ("si", "sauf"):
                if o.get(cle):
                    vus += 1
                    assert o[cle] in slugs and o[cle] != m["slug"], (m["slug"], cle, o[cle])
                    assert k > 0, f"{m['slug']} : le premier objectif ne se saute pas"
        for partie, lignes in m["dialogue"].items():
            for ligne in lignes:
                for cle in ("si", "sauf"):
                    if ligne.get(cle):
                        vus += 1
                        assert partie == "pendant", f"{m['slug']} : `{cle}` sur une réplique {partie}"
                        assert ligne[cle] in slugs, (m["slug"], ligne[cle])
    assert vus, "aucune mission ne prépare rien : le juge est à vide"


def test_deux_missions_n_ont_jamais_le_meme_titre():
    """Le saut de mission (le menu des triches) et le carnet choisissent une mission par son TITRE : x01 s'appelait
    « Le repérage », comme m52, et le saut lançait m52."""
    from collections import Counter
    doubles = [t for t, n in Counter(m["titre"].upper() for m in missions.CATALOGUE).items() if n > 1]
    assert not doubles, doubles

