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
from config import port_de_dev  # noqa: E402  (idem)

app = create_app()


if __name__ == "__main__":
    # APP_HOST=0.0.0.0 ouvre le serveur au wifi de la maison (telephone,
    # tablette). ⚠️ La console interactive de Werkzeug est alors coupee : un
    # shell Python ouvert a tout le reseau local n'a rien a faire la.
    hote = os.getenv("APP_HOST", "127.0.0.1")
    local = hote in ("127.0.0.1", "localhost")
    app.run(
        host=hote,
        debug=app.config.get("DEBUG", False),
        use_debugger=app.config.get("DEBUG", False) and local,
        port=port_de_dev(),
        use_reloader=True,
    )
