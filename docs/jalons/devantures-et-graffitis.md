# Devantures et graffitis

← [les jalons livrés](README.md) · [le plan](../plan.md)

## Notes

demande de Martin (« ajoute des façades distinctes et vraiment commerciales, pour les
commerces et avec du lettrage et pancartes ; ajoute des graffitis sur certains bâtiments »).
Avant, tous les commerces étaient le même mur percé d'une porte : on savait qu'un bâtiment
était un commerce parce que le générateur le disait, pas parce qu'on le voyait. **118
devantures** (`app/devantures.py`) — un BANDEAU sombre, le NOM en lettres pixel (la police
3×5 du HUD, 4 px par lettre : 16 caractères sur quatre tuiles), un AUVENT rayé, une VITRINE
au pied du mur et une PANCARTE qui dépasse sur le trottoir. Sept familles de couleurs
(bouffe, service, artisan, nuit, commerce, marine, industrie) et **des noms par district** :
une poissonnerie aux Quais, un atelier de soudure à La Shop, une garderie aux Érables — un
juge interdit de les mélanger, sinon les cinq districts redeviennent le même quartier
repeint. Les lieux garantis portent leur vraie enseigne (CHEZ GUS, LE BROUILLARD, CHEZ
TI-PAUL) ; ⚠️ **la planque n'en a pas** — une planque avec son nom sur le mur n'est plus une
planque. **54 graffitis** : les gangs signent **chez eux** (voir « CRAVATES » sur un mur
apprend au joueur chez qui il est, sans un mot de HUD — un juge vérifie qu'aucun nom de gang
ne traîne hors de son territoire), les autres taguent ROCCO, ICITTE, PAS DE JOBS.

- ⚠️ **Deux règles portent tout le reste.** (1) Une devanture est une **couche peinte** :
  elle ne déplace aucune tuile et ne change aucune solidité (elle transforme des `F` en `W`,
  qui ont exactement la même) — un juge garde cette frontière, parce que la violer ferait
  tomber les juges de circulation trois fichiers plus loin. (2) Elle tire dans **son propre
  dé** : avec le dé commun, choisir un nom d'enseigne décalait toute la suite du hasard et
  déplaçait des arbres à l'autre bout de la ville (deux tests de banc sont tombés
  là-dessus). Le dessin vit dans le **morceau de décor**, cuit une fois : une rue
  commerçante ne coûte pas une image de plus — et une enseigne à cheval sur deux morceaux
  est rangée dans **les deux**, sinon le nom est coupé net au milieu d'un mot. Chaque
  devanture pose une **lueur de vitrine** (basse, courte, chaude) : sans elle tout ce
  travail disparaissait la moitié du temps de jeu. 25 juges Python + 5 de banc ; rythme
  **0,7 ms** par image de nuit à 5★ (0,6 avant), paquet **341 Ko bruts / 35 Ko gzip**.
- ⚠️ **On voit toujours une porte** (retour de Martin) : le bandeau, l'auvent et la vitrine
  couvraient toute la bande — on lisait le nom du commerce et on ne voyait plus par où
  entrer. La devanture porte donc `motifs`, une lettre par tuile, qui dit au peintre ce
  qu'il y a dessous : `W` vitrine, `D` porte qu'on ouvre, `d` condamnée, `G` garage, `P`
  porte **peinte**. Une porte garde toute sa hauteur (pas d'auvent ni de vitrine
  par-dessus), et **celle où l'on peut entrer se reconnaît de loin** : vitre claire, poignée
  dorée, rai de lumière au seuil — les autres sont sombres, planches en travers pour les
  condamnées. Un tiers des bandes n'avaient **aucune** ouverture (le bâtiment avait tiré
  « pas de porte ») : on en peint une (`P`) sur la tuile qui donne sur le trottoir, sans
  toucher au sol — elle ne promet donc rien qu'on ne tienne. 11 juges de plus, dont un qui
  vérifie que `D` correspond à une **vraie** porte du catalogue : peindre une poignée dorée
  sur un mur serait une promesse qu'on ne tient pas. 473 tests
