# M8 Les cinq districts

← [les jalons livrés](README.md) · [le plan](../plan.md)

## Fiche

_Titre d'origine dans le plan : M8 — Les cinq districts (taille 4) — **livré le 13 sept. 2026**_

_Ce que ça donne :_ la ville cesse d'être un quartier. **421 × 213 tuiles** au lieu de
157 × 112 (5,1 ×), quatre quartiers de plus autour d'une baie, chacun avec sa trame, son
gang, son bruit et une raison d'y aller. Le Faubourg n'a pas bougé d'une tuile.

- `carte.py` : **une seule grille de blocs** (20 × 12), un district par rectangle,
  assemblés par `_assembler()`. C'est ce qui garde la ville d'un seul tenant — les artères
  traversent les frontières, rien ne se charge en roulant. Un district ne fusionne **jamais**
  par-dessus sa frontière (sinon déplacer un quartier en casserait un autre) : le juge est
  dans l'assembleur.
- ⚠️ **La règle qui fait la géographie** : une rue dont _tous_ les blocs voisins sont de
  l'eau est **noyée** — elle n'est ni bâtie ni carrossable, et l'eau reste dessous. Une rue
  de rive (eau d'un bord, terre de l'autre) reste une rue : c'est le boulevard du bassin.
  Cette seule règle ferme la baie, arrête la rue du pourtour au bord de l'eau et coupe pour
  de bon le chenal de La Pointe. Et `PONTS` fait l'exception : **un** pont, tablier de
  planches, que le juge défait pour vérifier qu'il est bien le seul lien.
- Les trames se distinguent à l'œil, et un juge le mesure sur trois chiffres (rues au mètre
  carré, taux de fusion, largeur moyenne des colonnes) : Les Quais = blocs longs de trois
  blocs, hangars, quais ; Les Érables = grandes parcelles, maisons détachées sur gazon ;
  La Shop = des 2 × 2 partout, presque pas de rues, stationnements ; La Pointe = bois,
  sentiers de terre, quatre maisons et un phare.
- ⚠️ **Pas de vrai cul-de-sac.** Un croisement à un seul bras piège un char : il y entre et
  la seule sortie est la voie qui pointe sur lui. La banlieue a donc des rues qui s'arrêtent
  en **T** (déjà gérées : STOP à la tige) et des ruelles sans issue dans les îlots, pas des
  culs-de-sac routiers — et `test_les_croisements_sont_des_croisements` interdit le reste.
- `pietons.py` : Les Morues, Les Chevreuils, Les Boulonneux (les seuls hostiles sans qu'on
  sorte une arme), Les Skateux ; et quatre passants de quartier — débardeur, banlieusard,
  machiniste, promeneur de chien — que le champ `districts` **enferme chez eux**.
- `carte.zones()` : police, véhicules et piétons par district, plus un **rythme**
  (nuit, matin, soir) : La Shop tombe à 0,15 la nuit, les Quais montent à 1,4 le matin.
- 5 lieux de plus, un par district : dépanneur Chez Ti-Paul (caisse, journal), **Hôtel
  Bandini** (un deuxième lit, donc une deuxième sauvegarde — et la propriété qui
  l'attendait existe enfin), cantine des Quais (hot-dog), usine Prévost, phare de La Pointe.
- `audio.py` : _10-4_ (auto-patrouille) et _Radio-Traversier_ (camion). **À générer et à
  écouter** : `uv run python scripts/audio_elevenlabs.py --refaire dix_quatre traversier`.
- **Le paquet, mesuré** : 319 Ko bruts, **33 Ko gzip** (prévu : 360 / 60), `generer()`
  94 ms **une fois au démarrage du serveur** — le paquet est construit à la création de
  l'app, pas par requête. Budget du test relevé à 400 Ko bruts (puis à **600** le 13 sept. : le brut n'est qu'un indicateur, voir « Dettes »), et un second juge tient le
  gzip sous 70 Ko : c'est lui qui voyage. La carte reste dans le paquet ; le déclencheur du
  découpage est toujours écrit d'avance (plus de 2 s entre « Jouer » et la ville sur le
  téléphone de Martin → `/api/carte`, ETag, districts chargés autour du joueur).
- **Rythme** : 0,29 ms par image de nuit à 5★ (0,26 avant M8). La ville a quintuplé, pas le
  coût de l'image : rien ne parcourt la carte par image.
- ⚠️ **Le chien de garde mordait un char sage.** Un feu rouge dure jusqu'à 480 images ;
  l'attente de boîte qui suit, jusqu'à 400. 480 + 110 = 600, exactement le seuil du chien —
  et le mode TRACE signalait une anomalie sur un char parfaitement poli. `immobileT` ne
  compte plus le temps d'une **attente légitime** (feu rouge, stop qui s'égrène, boîte
  encore prise), chacune bornée. L'anomalie garde en plus l'état d'**avant** le déblocage.
- **Une vieille sauvegarde** ne place plus rien dans un mur : l'empreinte du catalogue a
  changé, donc la position du joueur _et_ celle du char gardé devant la planque sont
  oubliées ; le char revient sur la rue la plus proche de la porte.

## Notes

la ville passe de 157×112 à **421×213 tuiles** (5,1 ×) : Les Érables (banlieue, Les
Chevreuils), La Shop (industriel, Les Boulonneux), Les Quais (port, Les Morues), La Pointe
(parc, Les Skateux) et **la baie** — une seule grille de blocs, un district par rectangle,
aucune fusion par-dessus une frontière ; une rue dont tous les blocs voisins sont de l'eau
est **noyée** (c'est ce qui ferme la baie et coupe le chenal), et **un pont** relie La
Pointe ; 5 nouveaux lieux (dépanneur, Hôtel Bandini, cantine des Quais, usine Prévost,
phare) ; 4 gangs + 4 passants de quartier (`districts` les enferme chez eux) ; densité **et
rythme** par district (La Shop déserte la nuit, les Quais le matin) ; radios _10-4_ et
_Radio-Traversier_ ; paquet **319 Ko bruts / 33 Ko gzip**, `generer()` 94 ms au démarrage,
**0,29 ms par image** de nuit à 5★ (0,26 avant) ; chien de garde du trafic corrigé (480
images de feu rouge **puis** l'attente de boîte faisaient 600 : il mordait un char sage)
