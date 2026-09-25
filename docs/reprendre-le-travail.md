# Bandini — reprendre le travail

← [le plan](plan.md), qui ne garde que ce qui reste à faire

À lire en début de session. Le plan a été approuvé par Martin le 12 septembre 2026 ; depuis le 20 sept. 2026, `docs/plan.md` ne garde que **ce qui reste à faire** — à chaque jalon livré, sa ligne passe dans [jalons/README.md](jalons/README.md). Où est le reste : « Où est le reste », dans le plan.

⚠️ **`docs/carte.md` est l'inventaire de la carte** (districts, bâtiments,
véhicules, personnages, gangs, piétons, barrières). Il reflète `app/carte.py`
et doit être **mis à jour à chaque changement de la ville** — un nouveau
bâtiment, un district, un gang, un véhicule ou une sorte de piéton. La carte
se génère depuis le code : c'est le code qui fait foi, et ce document ne doit
pas prendre de retard dessus.

## Reprendre le travail

```bash
cd ~/dev/bandini
uv sync --all-groups && cp -n .env.example .env
git config core.hooksPath scripts/git-hooks
uv run ruff check . && uv run pytest -q --ignore=tests/test_navigateur.py
uv run python scripts/verifier_missions.py --detail   # les missions sont-elles finies ?
# ⚠️ AVANT DE POUSSER SUR `main` : la suite COMPLETE, navigateur compris, sur le commit
# exact qu'on livre. Les tests ne tournent plus en CI (decision du 17 sept. 2026).
BANDINI_TESTS_OBLIGATOIRES=1 uv run pytest -q
uv run python run.py          # http://127.0.0.1:5400 — et http://192.168.x.x:5400
                              # depuis le telephone (APP_HOST=0.0.0.0 par defaut)
```

Les sons manquants se regénèrent par le serveur MCP `elevenlabs` (clé dans
`~/.mcp-servers/elevenlabs/cle.txt`) :

```bash
uv run python scripts/audio_elevenlabs.py --essai       # ce qui serait généré
uv run python scripts/audio_elevenlabs.py               # génère les bruitages qui manquent
uv run python scripts/audio_elevenlabs.py --radios      # … et les stations de radio (musique : cher)
uv run python scripts/audio_elevenlabs.py --voix        # … et les voix (passants + histoire, au caractère ; eleven_v3 ; leur jeu : `jeu=` dans chaque fichier de mission, et app/interpretation.py pour le reste)
uv run python scripts/audio_elevenlabs.py --musiques    # … et les 15 musiques du jeu (30 crédits/seconde)
uv run python scripts/audio_elevenlabs.py --refaire coup pas la_brume titre amb_quais ti_guy-m1-1
uv run python scripts/audio_elevenlabs.py --dictionnaire  # le dictionnaire de prononciation (app/prononciation.pls) : le téléverser, et les voix déjà faites qu'il changerait (gratuit)
uv run python scripts/audio_elevenlabs.py --libres        # chaque voix du compte, et qui parle déjà avec elle — AVANT de donner une voix (gratuit)
```

La musique se génère **et** s'écrit. Les quinze morceaux sont des mp3 ElevenLabs
(recette dans `audio.MUSIQUES`) **et** restent écrits en notes dans
`app/musique.py` : le fichier joue, les notes sont le **filet**. Elles se rendent
en WAV pour l'oreille, gratuitement et hors ligne :

```bash
uv run python scripts/musique_apercu.py                       # le thème du menu, en notes
uv run python scripts/musique_apercu.py titre --tours 2 --normaliser --sortie /tmp/t.wav
```

Les répliques de l'histoire vivent dans `app/missions.py` (`CATALOGUE[…]["dialogue"]`) ;
le slug de voix `<qui>-<mission>-<n>` suit la place de la réplique (appel, intro,
client, fin, échec). Changer un mot = régénérer cette ligne (`--refaire`). Les voix
des personnages sont nommées dans `missions.PERSONNAGES` (compte ElevenLabs de Martin).

**Mode trace** (quand un char reste pris, tourne en rond, sort de la rue) : ouvrir
`https://bandini.gestiondojo.ca/?trace=1` (ou PAUSE → OPTIONS → TRACE DES VÉHICULES).
Chaque char du trafic traîne son trajet (vert : roule, jaune : attend un feu, un stop ou
la boîte, rouge : immobile depuis 2 s), une ligne bleue vers sa tuile cible, un carré sur
la sortie choisie, et son état au-dessus (`FEU 4S`, `BOITE`, `DANS`…). Le jeu se surveille
lui-même : **chien de garde** déclenché, **tourne en rond** (trois fois la même boîte en
20 s), **hors voie** (90 images hors de la chaussée) — l'anomalie s'affiche en rouge sur
place pendant dix secondes avec le trajet des huit dernières secondes, et s'écrit dans la
console (`[trace] …`) et dans `BANDINI.B.trace.anomalies`. Le bilan est en bas à droite.
Une capture d'écran de l'anomalie suffit pour la reproduire au banc.

Mise en ligne : `deploy/README.md`. Chaque jalon terminé est déployé et testé
par Martin sur téléphone (tactile) et ordinateur (manette).

---
