# Des bruitages déjà payés là où le jeu n'avait que des oscillateurs

← [les jalons livrés](README.md) · [le plan](../plan.md)

## Fiche

Martin : « prends des effets spéciaux existants pour les utiliser aux endroits utiles avant
d'en générer ». L'API ElevenLabs n'a pas de bibliothèque d'effets à fouiller et le quota est
à sec (7 crédits jusqu'au 17 oct.) : on branche les 74 bruitages déjà dans static/audio sur
les sons encore synthétisés et les gestes muets, sans un octet de plus au seau ; ce qui n'a
aucun équivalent devient la liste à générer le 17 oct.

## Notes

**Livré le 22 sept. 2026.** Aucun crédit dépensé, aucun fichier ajouté : tout emprunte un
échantillon déjà dans `static/audio/`, et la synthèse reste le filet de chacun.

- **Le tiroir-caisse à chaque achat.** `Missions.payer` joue `argent` (comme `encaisser`) ; une
  quinzaine d'achats payaient en silence (billet de foire, métro, autobus, amende, hôpital,
  pot-de-vin, coupe, tenue, armes, réparation, peinture, assurance, skimmer…). Les appelants qui
  le rejouaient derrière `payer` ne le font plus : un café sonnait deux tiroirs, un stool aussi.
  Le doublon de la fouille des tiroirs (`encaisser` puis `argent`) est parti avec.
- **Le décor qui cède s'entend** (`Entites.briser` → `Son.SFX.bris`, par `Son.depuis` : muet hors
  de l'écran, dosé à la distance). Par matière, dans `MATIERE_DU_BRIS` de `son.js` : le bois et le
  plastique `casse`, le métal `pelle` (le clang), le verre des abribus `bouteille`. Le buisson, le
  château de sable, le matelas et la manche à air n'ont que leur poussière ; la borne, le guichet
  et les distributrices gardent leur son. **Un bris par image** : l'explosion d'un char en couche
  six d'un coup.
- **Le maillet** de la foire prend le coup de bâton (`batte`) ; **la passe du pistolet à
  peinture** le souffle de l'extincteur, à mi-volume et **coupé à 0,4 s en fondu** (`bref()`,
  nouveau dans `son.js` : la boucle fait deux secondes).
- **Les refus écrits jouent le refus** (`erreur`) : rien à accrocher, char sur la fourche, recule
  d'abord sous le toit, fontaine sèche, « PLUS TARD », une barrière, le canard déjà dans le seau,
  hors piste.

Juges : `tests/test_bruitages_empruntes_js.py` (le fichier parti se reconnaît au gain de sa
fiche) ; sept mutations les font rougir.

**Ce qui n'a aucun équivalent payé** reste synthétisé et part dans la ligne
[« Générer les bruitages qui n'ont aucun équivalent payé »](les-bruitages-qui-n-ont-aucun-equivalent-paye.md#fiche).
Je ne peux pas écouter : c'est Martin qui dira si un emprunt sonne faux (le clang du métal, surtout).
