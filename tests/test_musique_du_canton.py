"""La musique du Petit-Canton (docs/jalons/les-mantes-provoquent-et-le-petit-canton-a-sa-musique.md).

Martin (29 sept. 2026) l'a demandée : le quartier jouait l'ambiance du dernier district traversé. Une ambiance de
district comme les autres — écrite en notes (le filet), jouée par un mp3 ElevenLabs quand il est là, sous la rumeur.
"""

from app import audio, musique


def test_le_petit_canton_a_son_ambiance():
    assert musique.AMBIANCES_DE_DISTRICT["canton"] == "amb_canton"
    style = next(s for s in musique.AMBIANCES if s["slug"] == "amb_canton")
    assert style["gamme"] == musique.PENTATONIQUE
    piece = audio.piece_par_slug("amb_canton")
    assert piece is not None
    # ⚠️ Le prompt reprend la fiche du morceau écrit : même tempo, même tonalité.
    assert f"{style['bpm']} bpm" in piece["prompt"] and "D major pentatonic" in piece["prompt"]
    # La touche du Sud de la Chine, sur une nappe — et pas une carte postale : ni gong, ni batterie.
    for instrument in ("guzheng", "erhu", "dizi", "pad"):
        assert instrument in piece["prompt"], instrument
    for jamais in ("no gong", "no drums", "no vocals", "not a postcard"):
        assert jamais in piece["prompt"], jamais
    assert piece["volume"] <= 0.3, "une ambiance de district joue sous la rumeur"


def test_son_mp3_est_la_et_voyage_au_paquet():
    assert audio.chemin_musique("amb_canton").is_file()
    morceau = next(m for m in audio.exporter()["musiques"] if m["slug"] == "amb_canton")
    assert morceau["fichier"] and morceau["voix"], "le fichier ET le filet"


def test_a_pied_au_petit_canton_c_est_sa_musique(banc):
    """Au banc : le joueur pose le pied au Petit-Canton, sous le territoire des Mantes (rangée 47), et c'est
    `amb_canton` qui joue — au premier district, sans hystérésis."""
    r = banc("""function (L, o) {
        L.Jeu.commencer();
        const j = L.B.joueur;
        j.x = 150 * L.TT + 8; j.y = 47 * L.TT + 8;
        L.Monde.centrerCamera(j.x, j.y);
        L.Son.Chef.district = null;
        o.frame(3);
        const z = L.Monde.zoneA(j.x, j.y);
        return { district: z && z.district, joue: L.Son.Mus.courante };
    }""")
    assert r == {"district": "canton", "joue": "amb_canton"}, r
