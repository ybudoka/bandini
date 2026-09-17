#!/usr/bin/env bash
# Installation INITIALE de Bandini sur le serveur de gestiondojo.ca — une fois.
#
#   ssh -i ~/.ssh/dojo_deploy -o IdentitiesOnly=yes dojoadmin@103.98.215.181 \
#     'bash -s' < deploy/installer.sh
#
# Idempotent : relancer ne casse rien. Ne fait PAS le DNS ni le Caddyfile
# (voir deploy/caddy/README.md) — mais insere l'hote dans Caddy si demande
# avec CADDY=1. Les mises en ligne suivantes passent par deploy/deploy.sh.

set -euo pipefail

BASE=/srv/bandini
DEPOT_URL=https://github.com/ybudoka/bandini.git
SERVICE=bandini-gestiondojo
PORT=8006
HOTE=bandini.gestiondojo.ca

echo "==> Port $PORT libre ?"
if ss -ltnp 2>/dev/null | grep -q ":$PORT "; then
  if ! systemctl is-active --quiet "$SERVICE"; then
    echo "!! Le port $PORT est pris par autre chose que $SERVICE — arret." >&2
    exit 1
  fi
fi

echo "==> Arborescence"
sudo -n mkdir -p "$BASE/releases" "$BASE/shared/donnees" "$BASE/shared/maison" "$BASE/shared/copies"
sudo -n chown -R dojoadmin:dojoadmin "$BASE"
# ⚠️ `maison` est le HOME de gunicorn : sans lui, son serveur de controle
# echoue a chaque demarrage sur /var/www/.gunicorn (voir le service).
# `copies` : le vidage quotidien de la base (M14), ecrit par www-data.
sudo -n chown www-data:www-data "$BASE/shared/donnees" "$BASE/shared/maison" "$BASE/shared/copies"

echo "==> Depot"
if [ ! -d "$BASE/repo/.git" ]; then
  git clone -q "$DEPOT_URL" "$BASE/repo"
fi
git -C "$BASE/repo" fetch -q origin main
git -C "$BASE/repo" reset -q --hard origin/main

echo "==> .env partage"
if [ ! -f "$BASE/shared/.env" ]; then
  CLE="$(python3 -c 'import secrets; print(secrets.token_hex(32))')"
  cat > "$BASE/shared/.env" <<ENV
SECRET_KEY=$CLE
SITE_NAME=Bandini
SITE_TAGLINE=Baie-des-Brumes t'attend. La police aussi.
APP_BASE_URL=https://$HOTE
DONNEES_DIR=$BASE/shared/donnees
STATIC_MAX_AGE=604800
FLASK_DEBUG=false
ENV
  sudo -n chown dojoadmin:www-data "$BASE/shared/.env"
  sudo -n chmod 640 "$BASE/shared/.env"
fi

echo "==> systemd"
sudo -n install -m 644 "$BASE/repo/deploy/systemd/$SERVICE.service.example" "/etc/systemd/system/$SERVICE.service"
sudo -n systemctl daemon-reload
sudo -n systemctl enable -q "$SERVICE"
# Le vidage quotidien de la base des comptes (M14) : une base sans copie de
# surete est une perte de donnees qui attend sa date.
for unite in bandini-sauvegarde-bd.service bandini-sauvegarde-bd.timer; do
  sudo -n install -m 644 "$BASE/repo/deploy/systemd/$unite.example" "/etc/systemd/system/$unite"
done
sudo -n systemctl daemon-reload
sudo -n systemctl enable -q --now bandini-sauvegarde-bd.timer

echo "==> nginx"
sudo -n install -m 644 "$BASE/repo/deploy/nginx/$SERVICE.conf.example" "/etc/nginx/sites-available/$SERVICE.conf"
sudo -n ln -sfn "/etc/nginx/sites-available/$SERVICE.conf" "/etc/nginx/sites-enabled/$SERVICE.conf"
sudo -n nginx -t
sudo -n systemctl reload nginx

if [ "${CADDY:-0}" = "1" ]; then
  echo "==> Caddy"
  F=/etc/caddy/Caddyfile
  if ! sudo -n grep -q "$HOTE" "$F"; then
    sudo -n cp -p "$F" "$F.bak-$(date +%Y%m%d-%H%M%S)"
    sudo -n sed -i "0,/auto\.gestiondojo\.ca,/s//auto.gestiondojo.ca, $HOTE,/" "$F"
  fi
  sudo -n caddy validate --config "$F" --adapter caddyfile > /dev/null
  sudo -n systemctl reload caddy
fi

echo "==> Premiere release"
bash "$BASE/repo/deploy/deploy.sh" main

echo "==> Verifications"
curl -fsS "http://127.0.0.1:$PORT/sante"; echo
curl -fsS -A navigateur -H "Host: $HOTE" http://127.0.0.1:8080/sante; echo
