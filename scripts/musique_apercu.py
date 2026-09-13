"""Rend un morceau de `app/musique.py` en WAV, pour l'ecouter sans lancer le jeu.

    uv run python scripts/musique_apercu.py             # le theme du menu
    uv run python scripts/musique_apercu.py titre --tours 2 --sortie /tmp/x.wav

⚠️ Ce n'est PAS le moteur du jeu : le vrai rendu, c'est `Mus` dans `son.js`,
avec les oscillateurs du navigateur. Ce script refait le meme calcul en Python
pour qu'on puisse juger une musique a l'oreille avant de la deployer — et pour
qu'une note fausse s'entende ici plutot qu'en ligne. Il ne coute rien, ne
depend de rien (bibliotheque standard), et n'ecrit jamais dans `static/`.
"""

from __future__ import annotations

import argparse
import math
import struct
import sys
import wave
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app import musique  # noqa: E402

TAUX = 44100
#: Le meme volume maitre que `son.js` (VOLUME_MAITRE), pour entendre ce que
#: le joueur entendra, et pas une version deux fois trop forte.
VOLUME_MAITRE = 0.18


def frequence(midi: float) -> float:
    return 440.0 * 2.0 ** ((midi - 69) / 12)


def _onde(forme: str, phase: float) -> float:
    """Une periode de l'onde, `phase` dans [0, 1)."""
    if forme == "sine":
        return math.sin(2 * math.pi * phase)
    if forme == "square":
        return 1.0 if phase < 0.5 else -1.0
    if forme == "triangle":
        return 4 * abs(phase - 0.5) - 1
    if forme == "sawtooth":
        return 2 * phase - 1
    raise ValueError(f"forme inconnue : {forme}")


def _enveloppe(i: int, n: int) -> float:
    """Attaque tres courte puis decroissance, comme les rampes de `tonA`."""
    if n <= 1:
        return 0.0
    attaque = max(1, int(0.01 * TAUX))
    if i < attaque:
        return i / attaque
    reste = (n - i) / max(1, n - attaque)
    return reste ** 1.6


def _poser_ton(sortie: list[float], depart: int, duree: int, hz: float, forme: str, volume: float) -> None:
    pas_phase = hz / TAUX
    phase = 0.0
    for i in range(duree):
        j = depart + i
        if j >= len(sortie):
            break
        sortie[j] += _onde(forme, phase) * volume * _enveloppe(i, duree)
        phase = (phase + pas_phase) % 1.0


def _poser_bruit(sortie: list[float], depart: int, duree: int, coupure: float, volume: float,
                 graine: list[int]) -> None:
    """Bruit blanc passe-haut a un pole — l'equivalent grossier du filtre du jeu."""
    alpha = 1.0 / (1.0 + 2 * math.pi * coupure / TAUX)
    precedent = 0.0
    sortie_filtre = 0.0
    for i in range(duree):
        j = depart + i
        if j >= len(sortie):
            break
        # Un generateur pseudo-aleatoire a nous : le rendu doit etre le meme
        # d'une fois sur l'autre, sinon on ne peut pas comparer deux versions.
        graine[0] = (graine[0] * 1103515245 + 12345) & 0x7FFFFFFF
        blanc = graine[0] / 0x3FFFFFFF - 1.0
        sortie_filtre = alpha * (sortie_filtre + blanc - precedent)
        precedent = blanc
        sortie[j] += sortie_filtre * volume * _enveloppe(i, duree)


def rendre(morceau: dict, tours: int = 1) -> list[float]:
    pas_s = 60.0 / morceau["bpm"] / morceau["pas_par_temps"]
    total_pas = morceau["pas"] * tours
    # Une seconde de queue : la derniere note a le droit de finir.
    n = int((total_pas * pas_s + 1.0) * TAUX)
    sortie = [0.0] * n
    graine = [12345]
    for voix in morceau["voix"]:
        motif = voix.get("motif", morceau["pas"])
        for p in range(total_pas):
            dans = p % motif
            for note in voix["notes"]:
                if note[0] != dans:
                    continue
                relatif = note[3] if len(note) > 3 else 1
                volume = voix["volume"] * relatif * morceau["volume"] * VOLUME_MAITRE
                depart = int(p * pas_s * TAUX)
                if voix["forme"] == "bruit":
                    duree = int(min(0.12, note[2] * pas_s) * TAUX)
                    _poser_bruit(sortie, depart, duree, note[1], volume, graine)
                else:
                    duree = int(note[2] * pas_s * 0.92 * TAUX)
                    _poser_ton(sortie, depart, duree, frequence(note[1]), voix["forme"], volume)
    return sortie


def ecrire_wav(echantillons: list[float], chemin: Path) -> tuple[float, float]:
    crete = max((abs(v) for v in echantillons), default=0.0)
    chemin.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(chemin), "wb") as f:
        f.setnchannels(1)
        f.setsampwidth(2)
        f.setframerate(TAUX)
        f.writeframes(b"".join(
            struct.pack("<h", int(max(-1.0, min(1.0, v)) * 32767)) for v in echantillons))
    return crete, len(echantillons) / TAUX


def main() -> int:
    a = argparse.ArgumentParser(description="Rend un morceau du catalogue en WAV.")
    a.add_argument("slug", nargs="?", default="titre")
    a.add_argument("--tours", type=int, default=1, help="combien de fois la boucle")
    a.add_argument("--sortie", type=Path, default=None)
    a.add_argument("--normaliser", action="store_true",
                   help="monte le niveau pour l'ecoute au casque (ce n'est plus le niveau du jeu)")
    args = a.parse_args()

    morceau = musique.par_slug(args.slug)
    if morceau is None:
        connus = ", ".join(m["slug"] for m in musique.MORCEAUX)
        print(f"morceau inconnu : {args.slug} (connus : {connus})", file=sys.stderr)
        return 1

    sortie = args.sortie or Path(f"{args.slug}.wav")
    echantillons = rendre(morceau, args.tours)
    crete_jeu = max((abs(v) for v in echantillons), default=0.0)
    if args.normaliser and crete_jeu > 0:
        gain = 0.89 / crete_jeu
        echantillons = [v * gain for v in echantillons]
        print(f"⚠️ normalise (×{gain:.1f}) : ce n'est PAS le niveau du jeu")
    crete, duree = ecrire_wav(echantillons, sortie)
    print(f"{morceau['nom']} — {morceau['bpm']} bpm, {len(morceau['voix'])} voix, "
          f"{duree:.1f} s ({args.tours} tour{'s' if args.tours > 1 else ''})")
    print(f"crete en jeu {crete_jeu:.2f}" + ("  ⚠️ ecretage" if crete_jeu > 1.0 else ""))
    print(f"→ {sortie}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
