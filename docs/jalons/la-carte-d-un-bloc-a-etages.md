# La carte d'un bloc à étages : un étage à la fois

← [le plan](../plan.md) · [les jalons livrés](README.md)

## Fiche

Demande de Martin (30 sept. 2026), capture de la grande carte dans la villa du maire à l'appui : « je ne
veux pas voir tous les étages d'un coup — et valide toutes les missions qui se passent là, pour que ça ne
soit pas incohérent ».

La villa (`app/blocs/villa.py`) tient ses trois étages dans une seule carte : le terrain et le
rez-de-chaussée en haut, l'étage et la cave dessous. La caméra ne sort jamais du **cadre** du joueur
(`Monde.cibleCamera`), mais la grande carte (`Hud.dessinerCarte`) dessinait la carte entière — on y voyait
l'étage et la cave collés sous le terrain, avec les lieux et les marqueurs de tous les étages.

- La grande carte d'un bloc à `cadres` ne montre que **le cadre où se tient le joueur**, à sa propre
  échelle ; ce qui est hors du cadre (lieux, défis, agents) ne se dessine pas.
- Le titre nomme l'étage.
- L'objectif sur un autre étage : le repère va à l'escalier qui y mène, pas dans le vide.
- Puis les missions de la villa (`v01`, `v02`, `v03`, `e07`) rejouées au banc, la carte ouverte à chaque étape.

## Notes

**Livré le 30 sept. 2026.**

- **La grande carte** (`Hud.dessinerCarte`) ne montre que `partieMontree` : dans un bloc à `cadres`, le cadre du
  joueur, à sa propre échelle (l'étage 36 × 23 tuiles remplit l'écran), et le titre le nomme — « LA VILLA DU MAIRE
  — L'ÉTAGE » (`noms_des_cadres`, dans la fiche du bloc ; `blocs.erreurs` refuse un compte qui ne tombe pas). Les
  lieux hors de l'étage ne se dessinent pas, et le reste est rogné au cadre.
- **Les couches de la ville ne se posent plus sur un bloc** : lignes d'autobus, métro, train, territoires, ville du
  boss, traversier, navette. Le pointillé rouge de la capture de Martin était le **train** de la ville, en
  coordonnées de la ville, sur la villa.
- **La mini-carte** (64 × 48 tuiles, plus grande que l'étage) centre l'étage et ne peint que lui : elle montrait la
  cave et le terrain à côté de l'étage.
- **Le GPS** (`Histoire.cible` → `Infiltration.escalierVers`) : un objectif à un autre étage se vise par l'escalier
  à prendre dans l'étage où l'on est — le premier d'un plus court chemin d'étage en étage (de la cave à l'étage, on
  remonte à la cuisine). Il se nomme « L'ESCALIER VERS L'ÉTAGE ». La sortie vers la ville aussi.
- **Les prérequis de la villa** (Martin : « assure-toi que les prérequis des missions soient bien respectés ») :
  v01 → v02 → v03, et e06 → e07. Deux missions donnent la **même clé** (v01 au garde du jardin, e07 au chauffeur).
  ⚠️ Rater l'une avec la clé de l'autre au sac l'effaçait (`Infiltration.rendre` effaçait tout objet nommé par
  un objectif) : la porte de service ne s'ouvrait plus jamais. **C'était la partie de Martin** (jour 479 : v01
  faite, v02 en cours, pas de clé). Maintenant `commencer` retient ce qu'on avait (`mission.avant`), et une mission
  ratée ne fait retomber que ce qu'ELLE a fait prendre ; et `Sauvegarde.completer` rend la clé à une partie qui a
  fini une mission qui la donne (`cles_des_serrures`, calculée des missions par `missions.cles_des_serrures`).
- Un juge Python (`test_chaque_mission_de_la_villa_a_sa_cle_avant_la_maison`) : chaque mission qui entre dans la
  maison (e07, v02, v03) a la clé par un objectif d'avant ou par ses prérequis, de proche en proche.
- Faire e07 avant v01 : le vol de la clé de v01 se fait tout seul en arrivant (l'objectif `obtenir` avance quand
  l'objet est déjà au sac, et le garde ne la porte plus). Cohérent, mais Josée demande encore la clé au combiné.
- Juges au banc : la carte par étage (rez, étage, cave : partie, titre, lieux, mini-carte, pas de train), le GPS
  vers l'escalier, la clé qui survit à une mission ratée et qui revient au chargement — chacun rougit sa mutation.
  v01, v02, v03 et e07 rejouées de bout en bout, vertes.
