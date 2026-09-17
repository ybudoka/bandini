# Bandini

Ville ouverte en **pixel art, vue trois-quarts**, dans le navigateur. Tu es
Bandini, débarqué en autobus à **Baie-des-Brumes** avec 50 $ et le garage d'un
oncle mort endetté. Tu marches, tu te bats, tu voles des autos, tu fais de
l'argent — et la police ne t'arrête que si elle **te voit**. La prison coûte
cher. Deux fins : devenir le boss de la ville, ou sacrer ton camp par le
traversier de nuit.

Python (Flask) côté serveur, canvas côté navigateur. Sprites et ville dessinés
en code ; les bruitages sont de vrais échantillons générés par ElevenLabs
(`scripts/audio_elevenlabs.py`), avec repli sur la synthèse si un fichier
manque.

En ligne : <https://bandini.gestiondojo.ca>

## Reprendre le travail

**[docs/plan.md](docs/plan.md)** — la vision, l'architecture, les jalons et
leur état. À lire en premier.

## Démarrage local

```bash
uv sync --all-groups
cp .env.example .env
git config core.hooksPath scripts/git-hooks     # une fois par clone : pose la version
uv run python run.py
```

→ http://127.0.0.1:5400

Le serveur de développement écoute **tout le réseau local** (`APP_HOST=0.0.0.0`,
le défaut) : le terminal imprime aussi une adresse `http://192.168.x.x:5400` —
c'est celle à taper sur le téléphone, la tablette ou l'autre ordinateur de la
maison, sur le même wifi. ⚠️ L'adresse à lire est **celle-là**, pas le
`Running on http://…` de Werkzeug juste au-dessus : celui-là annonce la route
par défaut, donc le tunnel quand un VPN est monté. `APP_HOST=127.0.0.1` referme
le serveur sur la machine (et c'est le seul cas où la console interactive de
Werkzeug s'allume). Si l'appareil ne trouve rien : le pare-feu de macOS demande
une fois l'autorisation d'accepter les connexions entrantes pour Python.

## Tests

```bash
uv run ruff check .
uv run pytest -q --ignore=tests/test_navigateur.py   # Python + moteur sous Node
uv run playwright install chromium                    # une fois
uv run pytest -q tests/test_navigateur.py             # vrai navigateur
```

Le moteur JS est testé **sous Node contre le paquet que le serveur sert
vraiment** (`tests/banc.js`) : marche, collisions, manette, joystick tactile,
niveau de recherche, amendes, sauvegarde, et un singe qui tape au hasard.

## Ce qui est en Python

Le serveur **décide**, le navigateur **calcule**. Les catalogues (véhicules,
armes), l'économie (amendes, pots-de-vin, hôpital, propriétés), la police
(paliers, délits, cônes de vision), la carte, les missions et les magasins
vivent dans `app/` et partent en deux requêtes, chacune revalidée par ETag :
`/api/definitions` (les catalogues) et `/api/carte` (la ville, à part depuis
qu'elle pesait plus de la moitié du paquet).

## Mise en ligne

Voir **[deploy/README.md](deploy/README.md)** : gunicorn sur le port 8006,
service systemd `bandini-gestiondojo`, vhost nginx, hôte dans Caddy, modèle
« releases + current ».

## Structure

```
run.py  config.py          entree, configuration (.env)
app/                       fabrique, routes, definitions, scores, version,
                           vehicules, armes, economie, recherche, carte, missions,
                           magasins, audio
templates/  static/css/    page, voiles DOM, commandes tactiles, styles
static/audio/              bruitages (.mp3) — recette dans app/audio.py
static/js/                 base, atlas, sprites, entree, son, monde, entites,
                           combat, vehicules, police, missions, hud, jeu
tests/                     pytest, banc.js (Node), test_navigateur.py (Playwright)
deploy/                    gunicorn, deploy.sh, installer.sh, systemd, nginx, caddy
docs/plan.md               le plan et l'etat des jalons
```
