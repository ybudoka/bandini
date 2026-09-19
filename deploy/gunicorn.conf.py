# Gunicorn de Bandini.
#
# ⚠️ Le port 8006 n'est pas arbitraire : sur le serveur de gestiondojo.ca,
# 8000 = production, 8001 = dev, 8002 = conceptk, 8003 = site de jeux,
# 8004 = KidTube, 8005 = Auto Évasion. Reprendre un port occupe ferait echouer
# le demarrage du service — ou pire, ferait servir un autre site. Verifier
# avec `ss -ltnp | grep 800` avant d'en choisir un nouveau.
bind = "127.0.0.1:8006"

# Une page, deux paquets JSON et une petite base SQLite : des workers synchrones
# suffisent largement.
workers = 2
threads = 4
timeout = 60
graceful_timeout = 30
accesslog = "-"
errorlog = "-"
capture_output = True
