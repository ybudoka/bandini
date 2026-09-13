#!/usr/bin/env python3
"""Genere les sons manquants de `app/audio.py` — par le serveur MCP elevenlabs.

⚠️ Ce script N'APPELLE PAS l'API ElevenLabs lui-meme. Il parle au serveur MCP
`elevenlabs` exactement comme Claude Code le fait (JSON-RPC sur stdio) : une
seule integration a maintenir, une seule cle a poser, et le meme chemin que
celui qu'on utilise a la main depuis l'agent.

    uv run python scripts/audio_elevenlabs.py --essai     # ce qui serait genere
    uv run python scripts/audio_elevenlabs.py             # genere ce qui manque
    uv run python scripts/audio_elevenlabs.py --refaire coup pas

⚠️ CHAQUE GENERATION COUTE DES CREDITS. Le script ne touche jamais a un
fichier deja present (sauf `--refaire`), et ne tourne jamais en CI.

La cle vit dans ~/.mcp-servers/elevenlabs/cle.txt (chmod 600) ou dans
ELEVENLABS_API_KEY. Le chemin du lanceur se change par BANDINI_MCP_ELEVENLABS.
"""

from __future__ import annotations

import argparse
import json
import os
import queue
import subprocess
import sys
import threading
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RACINE))

from app import audio  # noqa: E402

LANCEUR = Path(os.environ.get(
    "BANDINI_MCP_ELEVENLABS",
    Path.home() / ".mcp-servers" / "elevenlabs" / "run.sh",
)).expanduser()

#: 22 kHz mono a 32 kbit/s : un bruitage de jeu pese alors 3 a 5 Ko. Le
#: 44 kHz du catalogue ElevenLabs serait trois fois plus lourd pour un son
#: qu'on entend une demi-seconde a travers un haut-parleur de telephone.
FORMAT = "mp3_22050_32"


class ClientMCP:
    """Un client MCP minuscule : poignee de main, puis des appels d'outils.

    ⚠️ stdin reste OUVERT tant qu'on n'a pas fini : un serveur MCP s'arrete sur
    l'EOF, et les dernieres reponses se perdraient.
    """

    def __init__(self, lanceur: Path) -> None:
        self.proc = subprocess.Popen(
            ["/bin/sh", str(lanceur)], stdin=subprocess.PIPE, stdout=subprocess.PIPE,
            stderr=subprocess.PIPE, text=True, bufsize=1,
        )
        self.lignes: queue.Queue[str | None] = queue.Queue()
        threading.Thread(target=self._lire, daemon=True).start()
        self.identifiant = 0
        self._envoyer({"jsonrpc": "2.0", "id": self._suivant(), "method": "initialize",
                       "params": {"protocolVersion": "2024-11-05", "capabilities": {},
                                  "clientInfo": {"name": "bandini", "version": "1"}}})
        self._attendre(self.identifiant)
        self._envoyer({"jsonrpc": "2.0", "method": "notifications/initialized"})

    def _lire(self) -> None:
        for ligne in self.proc.stdout:
            self.lignes.put(ligne)
        self.lignes.put(None)

    def _suivant(self) -> int:
        self.identifiant += 1
        return self.identifiant

    def _envoyer(self, message: dict) -> None:
        self.proc.stdin.write(json.dumps(message) + "\n")
        self.proc.stdin.flush()

    def _attendre(self, identifiant: int, delai: float = 300.0) -> dict:
        while True:
            ligne = self.lignes.get(timeout=delai)
            if ligne is None:
                raise RuntimeError("le serveur MCP s'est arrete :\n" + self.proc.stderr.read()[-2000:])
            ligne = ligne.strip()
            if not ligne.startswith("{"):
                continue
            charge = json.loads(ligne)
            if charge.get("id") == identifiant:
                if "error" in charge:
                    raise RuntimeError(charge["error"].get("message", charge["error"]))
                return charge["result"]

    def appeler(self, outil: str, arguments: dict) -> dict:
        identifiant = self._suivant()
        self._envoyer({"jsonrpc": "2.0", "id": identifiant, "method": "tools/call",
                       "params": {"name": outil, "arguments": {"params": arguments}}})
        resultat = self._attendre(identifiant)
        return json.loads(resultat["content"][0]["text"])

    def fermer(self) -> None:
        self.proc.stdin.close()
        self.proc.terminate()
        self.proc.wait(timeout=10)


def a_faire(refaire: list[str]) -> list[tuple[dict, int]]:
    if not refaire:
        return audio.manquants()
    inconnus = [s for s in refaire if not audio.par_slug(s)]
    if inconnus:
        raise SystemExit(f"slugs inconnus : {inconnus} (voir app/audio.py)")
    return [(e, i) for e in audio.CATALOGUE if e["slug"] in refaire
            for i in range(1, e["variantes"] + 1)]


def radios_a_faire(refaire: list[str]) -> list[dict]:
    if not refaire:
        return audio.radios_manquantes()
    return [r for r in audio.RADIOS if r["slug"] in refaire]


def main() -> int:
    argus = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    argus.add_argument("--essai", action="store_true", help="dire quoi generer, sans rien depenser")
    argus.add_argument("--refaire", nargs="*", default=[], metavar="SLUG",
                       help="regenerer ces sons meme s'ils existent")
    argus.add_argument("--radios", action="store_true",
                       help="generer aussi les stations de radio (musique : CHER)")
    options = argus.parse_args()

    if os.environ.get("CI"):
        print("⚠️  Jamais en CI : la generation coute des credits.", file=sys.stderr)
        return 2

    travail = a_faire(options.refaire)
    radios = radios_a_faire(options.refaire) if (options.radios or options.refaire) else []
    radios = [r for r in radios if options.radios or r["slug"] in options.refaire]
    if not travail and not radios:
        print("Rien a generer : les", sum(e["variantes"] for e in audio.CATALOGUE),
              "fichiers sont la.")
        orphelins = audio.orphelins()
        if orphelins:
            print("Fichiers que le catalogue ne reclame plus :", ", ".join(orphelins))
        return 0

    print(f"{len(travail) + len(radios)} fichier(s) a generer dans static/{audio.DOSSIER}/ :")
    for echantillon, indice in travail:
        print(f"  {audio.nom_fichier(echantillon, indice):>22}  "
              f"{echantillon['duree_s']:>4} s  {'boucle  ' if echantillon['boucle'] else '        '}"
              f"{echantillon['prompt'][:60]}…")
    for radio in radios:
        print(f"  {audio.nom_fichier_radio(radio):>22}  {radio['duree_s']:>4} s  MUSIQUE  "
              f"{radio['style']} — {radio['prompt'][:48]}…")
    if options.essai:
        print("\n(--essai : rien n'a ete genere)")
        return 0
    if not LANCEUR.is_file():
        raise SystemExit(f"lanceur MCP introuvable : {LANCEUR}")

    dossier = str(audio.RACINE_STATIQUE / audio.DOSSIER)
    client = ClientMCP(LANCEUR)
    faits, rates = 0, []
    try:
        etat = client.appeler("elevenlabs_status", {})
        print("\nElevenLabs :", etat.get("cle", "?"), "·", etat.get("quota", etat.get("caracteres_restants", "?")))
        for echantillon, indice in travail:
            nom = audio.nom_fichier(echantillon, indice)
            cible = audio.chemin(echantillon, indice)
            if cible.exists():
                cible.unlink()          # --refaire : le serveur n'ecrase jamais
            reponse = client.appeler("elevenlabs_sound_effect", {
                "prompt": echantillon["prompt"],
                "duration_seconds": echantillon["duree_s"],
                "prompt_influence": 0.6,
                "loop": echantillon["boucle"],
                "output_format": FORMAT,
                "output_dir": dossier,
                "nom": nom[:-4],
            })
            if reponse.get("ok"):
                faits += 1
                print(f"  ✓ {nom:>16}  {reponse['octets']:>6} octets")
            else:
                rates.append((nom, reponse.get("erreur")))
                print(f"  ✗ {nom:>16}  {reponse.get('erreur')}")
        for radio in radios:
            nom = audio.nom_fichier_radio(radio)
            cible = audio.chemin_radio(radio)
            if cible.exists():
                cible.unlink()
            reponse = client.appeler("elevenlabs_music", {
                "prompt": radio["prompt"],
                "music_length_ms": radio["duree_s"] * 1000,
                "force_instrumental": True,
                "output_format": audio.FORMAT_RADIO,
                "output_dir": dossier,
                "nom": nom[:-4],
            })
            if reponse.get("ok"):
                faits += 1
                print(f"  ✓ {nom:>22}  {reponse['octets']:>7} octets")
            else:
                rates.append((nom, reponse.get("erreur")))
                print(f"  ✗ {nom:>22}  {reponse.get('erreur')}")
    finally:
        client.fermer()

    print(f"\n{faits} son(s) generes, {len(rates)} en echec.")
    for nom, erreur in rates:
        print(f"  {nom} : {erreur}")
    if faits:
        print("\n⚠️  ECOUTE-LES avant de committer : personne d'autre ne peut juger un son.")
    return 1 if rates else 0


if __name__ == "__main__":
    sys.exit(main())
