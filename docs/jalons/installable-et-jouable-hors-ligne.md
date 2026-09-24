# Installable, et jouable hors ligne

← [les jalons livrés](README.md) · [le plan](../plan.md)

## Notes

demande de Martin : « est-ce compliqué de faire du jeu une webapp installable ? », puis
« jouable hors ligne ».

- ⚠️ **Mesuré : sur iPhone, la moitié est déjà faite, et personne ne l'a voulu** —
  `base.html` porte déjà `apple-mobile-web-app-capable`, `mobile-web-app-capable`,
  `theme-color` et `viewport-fit=cover` : « Ajouter à l'écran d'accueil » donne
  **aujourd'hui** une app plein écran sans barre Safari. Il n'y manque qu'une **icône** —
  iOS ne prend pas un `favicon.svg` et colle une capture d'écran floue à la place. Android
  et Chrome bureau, eux, exigent trois choses : un `manifest.webmanifest`, des icônes PNG
  (192, 512, une *maskable* — Chromium est **déjà là** pour Playwright, il rend le SVG sans
  rien ajouter au projet) et un service worker **qui a un gestionnaire `fetch`** : sans lui,
  Chrome ne propose pas l'installation du tout.
- ⚠️ **Le worker se sert à la RACINE, et c'est le seul vrai piège** : Flask sert tout sous
  `/static/`, or un worker ne contrôle que son dossier — `/static/js/sw.js` ne verrait
  jamais `/`. Il lui faut sa route à lui dans `routes.py`, en `no-cache` : nginx met
  `expires 7d` sur `/static/`, et un worker figé une semaine est un piège qui se referme sur
  la session suivante.
- ⚠️ **Le poids est mesuré, et c'est lui qui décide** : la coquille pèse **300 Ko** de JS
  gzippé et **65 Ko** de définitions (492 Ko brut) — précachée sans y penser ; l'audio pèse
  **12 Mo en 166 fichiers**, chargés à la demande (`son.js` : `fetch` puis
  `decodeAudioData`). Avaler 12 Mo en silence sur un forfait cellulaire n'est pas une
  fonctionnalité : l'audio se cache **à l'usage**, et « toute la ville hors ligne » est un
  **bouton** qu'on choisit.
- ⚠️ **Le cache se nomme par l'EMPREINTE, jamais par la version** — `definitions.py` calcule
  déjà un sha256 du paquet, et la sauvegarde s'en sert pour oublier une position qui
  n'existe plus (`jeu.js`). Un paquet caché qui ne correspond plus au JS servi ne ressemble
  pas à un bogue de cache : il ressemble à un bogue de jeu. C'est mot pour mot ce que
  `version.py` dit déjà dans sa propre docstring.
- ⚠️ Et **un worker naïf casserait la revalidation 304** montée dans `api_definitions` —
  celle qui accepte l'ETag **faible** de nginx.
- ⚠️ **Les mp3 ne portent pas `?v=`**, contrairement au JS : un bruitage regénéré garde son
  nom, donc un cache d'usage servirait l'ancien pour toujours. Il faut une règle de purge,
  et elle n'a pas de version à quoi se raccrocher.
- ⚠️ **Les scores restent en ligne** : `horsLigne` existe (`jeu.js`) mais ne couvre que
  l'échec de chargement des définitions — l'écran des scores n'a aucun chemin hors-ligne, et
  un tableau vide qui ment est pire qu'un tableau qui dit « pas de réseau ».
- ⚠️ À **vérifier sur le serveur** : le snippet de sécurité nginx
  (`gestion-dojo-security-server.conf`, hors dépôt) peut porter un CSP qui bloque
  `worker-src` ou `manifest-src` — et ça ne se verra qu'en prod. Deux vagues : **(1)
  l'installation** (manifeste, icônes, worker minimal — ~2 h ; ⚠️ **le manifeste et les
  icônes sont livrés**, 16 sept. 2026, ligne « Une icône, un favicon et un logo » : il n'en
  reste que le worker), **(2) le hors-ligne pour vrai** (coquille précachée, audio à
  l'usage, définitions par empreinte, scores qui disent la vérité — ~1 jour). Les juges ont
  déjà leur banc : `test_navigateur.py` lance un vrai Chromium, donc le worker se juge en
  coupant le réseau après le premier chargement.

**Livré** (17 sept. 2026) — les deux vagues d'un coup. Un **travailleur**
(`static/js/travailleur.js`, servi à la racine par `/travailleur.js`, `no-cache` et ETag),
inscrit après `load` par `hors-ligne.js`, garde **la coquille** — ce que la page d'accueil
demande, **lu dans la page rendue** (`app/hors_ligne.py`), jamais tenu à la main — et les
sons **à l'usage**. **LES SONS HORS LIGNE**, dans les OPTIONS, dit ce qu'il reste
(« 13 MO »), les télécharge d'un coup sur ACTION (« 42 % », puis « OUI ») et demande au
navigateur de ne pas les effacer. (Les scores, eux, disaient « Pas de réseau » au lieu de
« Personne encore » — le tableau a été retiré du jeu le lendemain même de sa livraison, et
ce juge-là avec.)

- ⚠️ **Mesuré : le travailleur ne rend PAS le jeu installable.** Chromium le dit
  installable avec ou sans lui (`Page.getInstallabilityErrors` vide dans les deux cas) : le
  critère du gestionnaire `fetch` est tombé, le manifeste et les icônes du 16 sept.
  suffisaient. Le travailleur, c'est le hors-ligne.
- ⚠️ **Le CSP de la prod est vu : il n'y en a pas** (`curl -sI -A navigateur`, 17 sept.
  2026 — `referrer-policy` et `x-frame-options` seulement) : rien ne bloque `worker-src` ni
  `manifest-src`. ⚠️ Sans `-A`, la prod répond **502** : nginx ferme tout agent qui
  contient « curl » et Caddy le rapporte comme une panne — une fausse alerte de dix
  minutes ce jour-là.
- ⚠️ **Une seule règle : le réseau d'abord, toujours** — le cache ne répond que quand le
  réseau se tait **ou répond 5xx** (un déploiement qui redémarre est une ville qu'on ne peut
  pas ouvrir, pas une ville qui n'existe pas). « Le cache d'abord » aurait servi, en dev,
  l'ancien script sous le même `?v=` : recharger deux fois pour voir sa propre
  modification. En ligne, le cache HTTP rend le réseau d'abord gratuit, et chaque réponse
  remet le cache à jour (sauf si l'ETag dit que c'est la même).
- ⚠️ **Les paquets se demandent par leur empreinte** (`/api/definitions?e=…`,
  `/api/carte?e=…`, que le serveur ignore) : c'est la clé du cache, et une page gardée n'y
  retrouve que la ville de SA construction. Le cache de la coquille se nomme par
  l'empreinte du travailleur (sha256 de la coquille, des sons et de son code), et
  l'activation efface les autres.
- ⚠️ **La purge des mp3**, qui n'ont pas de `?v=` : la même règle — un son rejoué en ligne
  se remplace — et un nom sorti du dossier sort du cache à l'activation.
- ⚠️ **Tout ce qu'il ne nomme pas passe sans lui** : le compte et les parties de M14.
  Rien d'autre qu'un GET.
- ⚠️ `test_navigateur.py` tourne **sans** travailleur (`service_workers: block`) : il
  remplirait son cache pendant chaque juge, et `page.route` ne voit pas ce qu'un
  travailleur sert. Ses juges sont dans `test_hors_ligne.py`, sur un serveur à soi qu'on
  coupe ou qu'on met en 502 ; chacun a son témoin sans travailleur, et quatre mutations (la
  navigation, le 5xx, les sons) font chacune rougir le sien.
- ⚠️ Rien en http sur le réseau local (`192.168.x.x:5400`, pas de contexte sécurisé) : la
  ligne des OPTIONS dit INDISPONIBLE et le jeu se joue comme avant.
