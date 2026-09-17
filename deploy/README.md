# Mise en ligne — bandini.gestiondojo.ca

Meme recette que le site de jeux et qu'Auto Évasion : Flask sous gunicorn,
service systemd, vhost nginx, hote declare dans Caddy.

```
Internet :443 → Caddy (TLS) → nginx 127.0.0.1:8080 → gunicorn 127.0.0.1:8006
```

| | |
|---|---|
| Sous-domaine | `bandini.gestiondojo.ca` |
| Port gunicorn | **8006** (8003 jeux, 8004 KidTube, 8005 Auto Évasion : ne pas reutiliser) |
| Service | `bandini-gestiondojo` |
| Dossier | `/srv/bandini` |
| Utilisateur du deploiement | `dojoadmin` (cle `~/.ssh/dojo_deploy`) |
| Utilisateur du service | `www-data` |

## Installation initiale (une seule fois)

1. **DNS** : enregistrement A `bandini` → `103.98.215.181` chez NameSilo.
2. **Serveur** : `ssh -i ~/.ssh/dojo_deploy -o IdentitiesOnly=yes dojoadmin@103.98.215.181 'CADDY=1 bash -s' < deploy/installer.sh`
   (arborescence, clone, `.env`, systemd, nginx, hote Caddy, premiere release).
3. **Certificat** : Caddy le demande tout seul. Tant que le DNS n'est pas
   propage, Let's Encrypt repond NXDOMAIN — ce n'est pas un bug. Quand
   `dig +short bandini.gestiondojo.ca @1.1.1.1` repond, relancer
   `sudo systemctl reload caddy` pour ne pas attendre le prochain essai.

## Chaque mise en ligne suivante

⚠️ **D'abord la suite complète, en local, sur le commit qu'on livre** : les tests ne
tournent plus en CI (decision du 17 sept. 2026), et `deploy.sh` prend `origin/main`
tel quel sans rien verifier.

```bash
BANDINI_TESTS_OBLIGATOIRES=1 uv run pytest -q     # verte, navigateur compris
git push origin <sha>:refs/heads/main
```

```bash
ssh -i ~/.ssh/dojo_deploy -o IdentitiesOnly=yes dojoadmin@103.98.215.181 \
  'bash /srv/bandini/repo/deploy/deploy.sh main'
```

## Verifications

```bash
# ⚠️ Toujours un -A : nginx ferme (444) tout User-Agent contenant « curl ».
# ⚠️ --resolve tant que le cache DNS local ne connait pas encore le nom.
curl -s -A navigateur --resolve bandini.gestiondojo.ca:443:103.98.215.181 https://bandini.gestiondojo.ca/sante
curl -sI -A navigateur -H 'Accept-Encoding: gzip' https://bandini.gestiondojo.ca/api/definitions | grep -iE 'content-encoding|etag'
sudo journalctl -u bandini-gestiondojo -n 50
```

## Pieges connus

- **fail2ban** bannit apres trois echecs SSH : toujours `-o IdentitiesOnly=yes`
  avec la bonne cle, jamais d'essais en boucle.
- **Port** : verifier `ss -ltnp | grep 800` avant d'en choisir un ; le 8004
  prevu pour Auto Évasion etait deja pris par KidTube.
- **Vhost nomme** obligatoire : le catch-all nginx enverrait l'hote vers
  gestion-dojo avec un 200.
