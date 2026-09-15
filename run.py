"""Point d'entree local. En production c'est gunicorn qui importe `run:app`."""

import os
from pathlib import Path

from dotenv import load_dotenv

# En production les variables sont injectees par systemd ; on ne charge le .env
# que s'il est lisible, pour ne jamais faire echouer le demarrage.
dotenv_path = Path(__file__).resolve().parent / ".env"
if dotenv_path.exists() and os.access(dotenv_path, os.R_OK):
    load_dotenv(dotenv_path=dotenv_path, override=True)

from app import create_app  # noqa: E402  (apres le chargement du .env)
from config import (  # noqa: E402  (idem)
    adresses_du_reseau_local,
    hote_est_local,
    port_de_dev,
)

app = create_app()


if __name__ == "__main__":
    # Par defaut le serveur ecoute sur TOUTES les interfaces : peu importe
    # comment on le lance (F5, la tache « serveur », `uv run python run.py`,
    # Flask sans rechargement), le telephone et la tablette de la maison le
    # trouvent sur le wifi — l'adresse a taper s'imprime plus bas.
    # APP_HOST=127.0.0.1 referme le serveur sur la machine, et c'est le seul
    # cas ou la console interactive de Werkzeug s'allume : ⚠️ des que l'hote
    # n'est plus local elle reste coupee, un shell Python ouvert a tout le
    # reseau de la maison n'a rien a faire la.
    hote = os.getenv("APP_HOST", "0.0.0.0")
    local = hote_est_local(hote)
    port = port_de_dev()

    # L'adresse a taper sur le telephone. ⚠️ On l'imprime nous-memes parce que
    # celle de Werkzeug (« Running on http://… », juste en dessous) est celle
    # de la route par defaut : VPN monte, il annonce le tunnel, qui ne se joint
    # pas du salon. Une seule fois : avec le rechargement, c'est le processus
    # fils qui sert (WERKZEUG_RUN_MAIN), le pere ne fait que le surveiller.
    if not local and os.getenv("WERKZEUG_RUN_MAIN") == "true":
        for adresse in adresses_du_reseau_local():
            print(f" * Sur le reseau de la maison : http://{adresse}:{port}")

    app.run(
        host=hote,
        debug=app.config.get("DEBUG", False),
        use_debugger=app.config.get("DEBUG", False) and local,
        port=port,
        use_reloader=True,
    )
