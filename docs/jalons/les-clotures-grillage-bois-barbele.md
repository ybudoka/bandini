# Les clôtures : grillage, bois, barbelé

← [les jalons livrés](README.md) · [le plan](../plan.md)

## Fiche

_Titre d'origine dans le plan : Les clôtures : grillage, bois ou barbelé (**correctif**, taille 1) — **livré le 13 sept. 2026**_

_Demande de Martin :_ « il faut des clôtures, mais si elles ne sont pas barbelées, qu'on
puisse passer par-dessus. » Puis, en cours de route : « ajoute aussi des clôtures de bois
pour de la variété. »

⚠️ **On passait par-dessus toutes les clôtures — sans même ralentir.** `f` était solide **3** :
le masque des véhicules la voyait, celui des piétons non (`MASQUE_PIETON = MUR | EAU`). Une
clôture n'arrêtait donc que les chars, et à pied elle n'existait pas. C'est ce qui la rendait
muette : on la traversait en courant comme si elle n'était pas là.

Les clôtures ont maintenant **leur solidité à elles**, et c'est la légende — elle seule — qui
dit laquelle fait quoi :

- **4, ça s'enjambe** : le **grillage** (`f`) et la **palissade de bois** (`w`). Une pose de
  48 images (0,8 s), pendant laquelle on ne frappe pas, on ne tire pas, on ne court pas — et
  on est une cible immobile, soulevée de 5 px, en haut d'une clôture. C'est ce prix-là qui
  fait d'une clôture un **choix** : couper par la cour, ou faire le tour.
- **5, ça ne se passe pas** : le **barbelé** (`X`). Ni à pied, ni en char. Il se met là où
  quelqu'un a payé pour que personne n'entre : les cours de gang (avec leur seule entrée de
  chars) et les cours de ferraille de La Shop.
- ⚠️ **Aucune n'est solide 1** : on **voit** à travers une clôture, donc un cône de police la
  traverse (`ligneLibre` ne s'arrête qu'au 1). Une clôture qui cache serait un autre
  mécanisme, avec ses propres juges.

⚠️ **Le piège, et c'était le plus gros : la police sait enjamber.** Le A\* des piétons
travaillait sur `MASQUE_PIETON` ; si le grillage n'avait été un coût que pour le joueur, la
première clôture venue serait devenue l'exploit qui gagne toutes les poursuites. Il y a donc
un **masque de chemin** à part (`MASQUE_A_PIED` : le barbelé bloque, le grillage non) et un
**coût** de 5 tuiles par clôture traversée — les deux chiffres, la durée et le coût, vivent
dans les mêmes données (`recherche.CLOTURES`) parce qu'ils disent la même chose. Un agent
lancé derrière le joueur franchit la même clôture, au même prix. ⚠️ Et devant une clôture
d'une seule tuile, il fait le **tour** — c'est moins cher, et il a raison : le juge se pose
donc au milieu d'un grillage de neuf tuiles.

**La palissade de bois** ne change aucune règle : c'est de la **variété**, et elle a sa place.
Une banlieue dont les cours arrière sont en grillage industriel n'a pas l'air d'une banlieue.
Elle ne se pose donc que dans **Les Érables** (188 tuiles), toujours avec une **barrière**, et
jamais devant une façade.

- ⚠️ **Trois pièges de génération, tous payés comptant** (mesures à l'appui) :
  - En clôturant aussi les quartiers de maisons du Faubourg, 274 tuiles de palissade tombaient
    au milieu du vieux quartier : le carré où l'on commence la partie devenait un labyrinthe
    de cours, et quatre juges de banc ne trouvaient plus une tuile libre autour du joueur.
  - Une barrière qui s'ouvre sur le mur du voisin fait de la cour une **poche** :
    `boucher_les_poches` la mure en silence — huit tuiles, dont le devant d'une porte, et un
    commerce se retrouvait sans entrée. La barrière s'ouvre donc sur du marchable, sinon la
    cour reste ouverte.
  - Les clôtures tirent dans **leur propre dé** (`des_cloture`), comme les devantures et les
    rampes : avec le dé commun, la trouée d'un terrain vague décalait toute la suite du hasard
    et la ville livrée changeait de gabarits.
- **Deux prédicats, et il fallait les deux** : `marchable` (ce qu'un piéton peut **fouler** —
  une clôture, non) et `franchissable` (ce qu'il peut **traverser**, en enjambant s'il le
  faut). La connexité et le bouchage des poches passent par le second : une cour derrière un
  grillage fait partie de la ville, une cour derrière du barbelé n'en fait pas partie. C'est
  ce qui fait du vieux juge « tout ce qui est marchable est relié » la garantie qu'**un
  barbelé ne referme jamais une poche**.
- **Juges (6 neufs)** : les trois clôtures disent ce qu'elles font (solidité, jamais foulables,
  aucune franchissable en char) ; la ville porte les trois **là où elles ont un sens** (le bois
  aux Érables seulement, du barbelé à La Shop, et la fourrière **garde son grillage** — « on le
  reprend par-dessus la clôture » est la moitié de ce qui la rend intéressante) ; un barbelé ne
  referme jamais une poche ; un grillage relie ses deux côtés et un barbelé coupe (sur une
  petite carte à la main) ; on ne traverse plus une clôture en courant (on l'enjambe, ça dure
  ce que les données disent, on ne frappe pas pendant, on retombe de l'autre côté) ; le barbelé
  ne se passe ni à pied ni en char ; et **une poursuite ne se gagne pas en enjambant**.

## Notes

demande de Martin (« il faut des clôtures, mais si elles ne sont pas barbelées, qu'on puisse
passer par-dessus », puis « ajoute aussi des clôtures de bois pour la variété ») : on
passait par-dessus **toutes** les clôtures — sans même ralentir, parce que `f` était solide
3 et que le masque des piétons ne la voyait pas. Elles ont maintenant leur solidité à
elles : **4 s'enjambe** (grillage, palissade de bois — 48 images en haut, immobile, sans
frapper ni courir), **5 ne se passe pas** (barbelé). Franchir est une capacité de **tout le
monde**, au même prix : l'A\* des agents traverse le grillage à 5 tuiles de coût et l'agent
l'enjambe pour de vrai — une poursuite ne se gagne pas en escaladant. Du barbelé dans les
cours de gang et de La Shop, du grillage à la fourrière (décision) et sur les terrains
vagues, **de la palissade de bois dans les cours arrière des Érables** (188 tuiles). 6 juges
neufs
