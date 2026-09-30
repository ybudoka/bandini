# Les klaxons de Ti-Guy, deuxième vague

← [le plan](../plan.md) · [les jalons livrés](README.md) · [la première vague](les-klaxons-de-ti-guy.md)

## Fiche

_Demandé par Martin le 30 sept. 2026, après la première vague : « la voix de Ti-Guy doit utiliser plus
l'accent anglais pour les mots en anglais, et ajoute les autres klaxons de la liste »._

- **L'accent anglais des mots anglais** (« Cracker Jack », « whoop-whoop », « Camaro ») : des règles IPA
  au dictionnaire de prononciation (`app/prononciation.pls`), qui ne touchent que ces mots — une balise
  d'accent (`interpretation.ACCENTS`) colorerait toute la réplique. ⚠️ Une règle n'entre qu'après une écoute
  sans/avec : les deux versions vont à Martin.
- **Le reste de la liste** : des airs à la corne — « Dixie », « Charge! », « Alouette », la ritournelle du
  camion de crème glacée (les enfants accourent), la marche nuptiale (des canettes traînent derrière le char),
  « Bip-bip » — et des bruitages ElevenLabs : l'a-ou-ga d'un Ford T, la vache, le pouet de clown, le klaxon
  enroué qui tousse et meurt.
- ⚠️ **La Soirée du hockey** : pas de transcription fiable de l'air — elle attend une partition, comme
  « Gens du pays » l'a attendue.

⚠️ **Ce qui guette** : la suite du paquet (`klaxons`) est à 650 octets de son plafond — les airs s'écrivent
plus serré ; le menu de Ti-Guy passe de six à seize klaxons.

## Notes

**Livré le 30 sept. 2026.** Dix klaxons de plus au menu de Ti-Guy (seize en tout), sept règles anglaises au
dictionnaire ; juges `tests/test_klaxons_de_ti_guy_js.py` (neuf juges ; trois mutations neuves, toutes mordent).

- **Les airs** (`garage.AIR_*`, écrits en notes par `_air`) : « Dixie » 200 $, « Charge! » 150 $,
  « Alouette » 150 $, la ritournelle de crème glacée 200 $ (les enfants à vélo du coin accourent :
  `Missions.attirerLesEnfants`, la boucle même du camion, sortie de `ritournelleDuCamion`), la marche
  nuptiale 250 $ (trois canettes au bout de trois ficelles, qui sautillent en roulant : `Vehicules.dessinerCanettes` ;
  ⚠️ l'attache s'écrase sur l'axe nord-sud comme l'ombre, la ficelle garde sa longueur — regardé à la capture,
  vers le sud elles passaient sous la caisse), « Bip-bip » 100 $.
- **Les bruitages** (ElevenLabs, lieu `klaxons`) : l'a-ou-ga 150 $, la vache 150 $ (baissée à 0,6 : elle sortait à
  −9,8 LUFS en jeu), le pouet de clown 100 $, le klaxon enroué 50 $ — chacun avec un filet synthétisé.
- **Les airs voyagent SERRÉS** (`garage.air_serre` : « 440:1 392:1 523:3 » et `unite`), `Garage.notesDe` les
  déplie. La suite passait quand même à 24 529 bruts / 10 024 gzip : **plafond relevé à 25 000 / 10 500,
  tranché par Martin** (proposé : relever, la voix seule sans texte, ou charger les klaxons au garage).
- **L'accent anglais** : sept règles IPA (`Cracker Jack`, `whoop-whoop`, `Camaro`, `Dukes of Hazzard`, `Dixie`,
  `Road Runner`, `Just married`), et le juge de l'IPA apprend ɹ, æ, ʌ, ɚ. Les trois voix déjà faites que le
  dictionnaire touchait (crie-3, cucaracha, police) sont refaites ; ⚠️ SANS et AVEC à comparer par Martin
  (`captures/klaxons/accent/`) — une règle qui ne gagne pas s'en va.
- ⚠️ **La Soirée du hockey n'y est pas** : pas de transcription fiable de l'air. Elle attend une partition.
- Dix voix de Ti-Guy et quatre bruitages : générés, ⚠️ **pas écoutés** par une oreille humaine.
