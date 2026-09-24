# Toutes les façons de lancer ouvrent le réseau local

← [les jalons livrés](README.md) · [le plan](../plan.md)

## Notes

demande de Martin (« je veux que toutes les run soit accessible depuis mon reseau
interne ») : `APP_HOST` valait `127.0.0.1` par défaut, et **une seule** des cinq façons de
lancer ouvrait le wifi de la maison — la configuration VS Code « réseau local ». F5
« Jouer », la tâche `serveur`, `uv run python run.py` et Flask sans rechargement restaient
sourds au téléphone. Le défaut est maintenant `0.0.0.0` (`run.py`), la configuration « sans
rechargement » écoute pareil, et celle qui disait « réseau local » devient **son
contraire** : « local seulement », la seule fermée — et la seule où la console interactive
de Werkzeug s'allume.

- ⚠️ **La bannière mentait**, et c'est le vrai piège : Werkzeug annonce une adresse trouvée
  en ouvrant une socket vers une adresse privée quelconque (`get_interface_ip`), donc celle
  de la **route par défaut** — VPN monté sur le Mac de Martin, il imprimait
  `http://10.14.0.2:5400`, un tunnel que le téléphone du salon ne joint **pas**, pendant que
  le wifi répondait en `192.168.4.188`. `config.adresses_du_reseau_local()` lit plutôt ce
  que le nom de la machine résout (les vraies interfaces, loopback et `169.254.x` écartés),
  et `run.py` imprime l'adresse **en dernier**, après la bannière, dans le processus qui
  sert vraiment (`WERKZEUG_RUN_MAIN`) pour ne pas la dire deux fois.
- ⚠️ Et `APP_HOST` **reste commenté** dans `.env.example` : le `.env` est chargé avec
  `override=True`, donc une ligne écrite là gagnerait sur le `env` des configurations VS
  Code et « local seulement » mentirait à son tour. La règle de sécurité sort du bloc
  `__main__` où personne ne pouvait la tester — `config.hote_est_local()` décide de
  `use_debugger`, et un juge rougit le jour où `0.0.0.0` entrerait dans la liste des hôtes
  « locaux » : un shell Python ouvert à toute la maison n'a rien à faire là. La production
  ne bouge pas (gunicorn sur `127.0.0.1:8006` derrière nginx). 7 juges neufs, 14 cas
