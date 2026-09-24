# Le serveur ne redémarre plus pour un test

← [les jalons livrés](README.md) · [le plan](../plan.md)

## Notes

demande de Martin : « il ne faut pas reloader l'app quand les tests ou autres dossier non
impactant sont changé ». Sans `watchdog`, le rechargeur de Werkzeug **parcourt tout
`sys.path`** — donc toute la racine du dépôt : **104 des 129 fichiers surveillés ne
changeaient rien au serveur** (95 dans `tests/`, 7 dans `scripts/`, 1 dans `deploy/`), et
avec plusieurs sessions qui écrivent des juges en même temps, le jeu ouvert dans Chrome
perdait son serveur à tout bout de champ. **Livré** : `run.py` passe
`exclude_patterns=ce_que_le_rechargeur_ignore()` à `app.run` (`config.py`) — **la liste de
ce qui compte** (`CE_QUI_REDEMARRE_LE_SERVEUR` : `app/`, `config.py`, `run.py`), pas celle
de ce qui ne compte pas : un dossier ajouté à la racine est ignoré dès le démarrage suivant.
`templates/` et `static/` n'ont jamais demandé de redémarrage (Jinja relit ses gabarits en
debug).

- ⚠️ Les motifs sont des `fnmatch` : le chemin passe par `glob.escape`, sinon un `[` dans le
  nom du dossier devient une classe de caractères et **plus rien n'est ignoré**. Épreuve sur
  le vrai serveur (worktree, `run.py` lancé, fichiers touchés) : `tests/`, `scripts/` et
  `deploy/` redémarraient Flask **avant**, plus rien **après** ; `app/__init__.py` le
  redémarre toujours. 2 juges neufs (`tests/test_rechargement.py` : `run.py` joué par
  `runpy` et lu avec `_find_stat_paths` de Werkzeug lui-même ; une racine neuve avec un
  `outils/` et un `[` dans son nom), vus rouges tous les deux une fois leur règle retirée.
