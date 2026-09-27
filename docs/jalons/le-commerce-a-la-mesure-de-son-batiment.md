# Le commerce à la mesure de son bâtiment

← [les jalons livrés](README.md) · [le plan](../plan.md)

## Fiche

Demande de Martin (27 sept. 2026) : « valide la grandeur des bâtiments avec ce qu'il y a
comme commerce, il faut que ce soit logique ». Mesuré sur la ville livrée (98 enseignes
ordinaires, la part de bâtiment derrière chaque vitrine) : un HÔTEL DES QUAIS dans 24
tuiles, un CHANTIER NAVAL dans 42, une MACHINERIE dans 24, une DISCO dans 42 — et à
l'inverse un TATOUAGE dans un hangar de 90, un VIDÉO POKER dans 72. Le nom est tiré sans
regarder le bâtiment, et le renommage du standing non plus.

- ⚠️ Chaque nom reçoit une taille (petit, moyen, grand) ; un passage APRÈS COUP et SANS DÉ,
  comme le standing (`vitrines.py`), renomme ce qui ne tient pas — un nom de la même famille
  (la pièce derrière reste la bonne), qui tient dans le même bandeau et qui n'est pas le
  voisin.
- ⚠️ Choisir le nom à la construction décalerait le dé des devantures (la pancarte, la porte
  peinte) : on ne le fait pas.
- ⚠️ Un juge mesure la part par la construction même, pas par la table qu'il juge.

## Notes

_Livré le 27 sept. 2026._

**La règle** : chaque nom d'enseigne a une taille, lue en **tuiles de bâtiment derrière sa
vitrine** (la « part » qui donne déjà ses mesures à la pièce) — `devantures.TAILLES` :

| Taille | Part | Exemples |
|---|---|---|
| petit | ≤ 49 | tabagie, barbier, dépanneur, tatouage, prêt sur gages, bijouterie |
| moyen | ≤ 130 | tout ce qui n'est pas rangé (`TAILLE_DU_NOM`) : épicerie, taverne, quincaillerie |
| grand | ≥ 60 | hôtel, chantier naval, cinéma, salle de quilles, machinerie, bois de sciage |
| libre | tout | les carrosseries (leur place, c'est la baie) et « À LOUER » |

**Comment** : `vitrines.a_la_mesure`, juste après le standing, sur la ville finie et **sans
un dé**. Une enseigne qui n'a pas la taille de son mur prend un nom de la même famille (la
pièce derrière reste la bonne), qui tient dans le même bandeau, du standing du bloc
d'abord, puis du district, puis de la **réserve** (`devantures.RESERVE` : dans chaque
famille, un nom de chaque taille qui tient sur deux tuiles). Le standing choisit déjà à la
mesure, et les enseignes neuves (`enseignes.poser`) ne prennent plus une porte trop petite.

**Mesuré** sur la ville livrée : 15 enseignes sur 98 hors mesure avant, **0** après ; aucune
tuile, aucun bandeau, aucune couleur, aucune porte ne bouge (le juge le vérifie). Ce qui
change de nom :

| Part | Avant | Après |
|---|---|---|
| 24 et 36 | HÔTEL DES QUAIS | TAVERNE DU PORT, BAR LE MATELOT |
| 42 | CHANTIER NAVAL | FRUITS DE MER |
| 42 | DISCO LE MIRAGE | SALLE DE POOL |
| 24 | MACHINERIE | ÉLECTRIQUE |
| 28 et 48 | FERRAILLE, PALETTES | DÉBOSSELAGE, FERBLANTIER |
| 45 | SABLAGE AU JET | RADIATEURS |
| 72 à 90 | TATOUAGE (trois fois) | BOTTES ET CIRES, BOTTES DE TRAVAIL |
| 63 à 72 | CHÈQUES CASH, BIÈRE ET VIN, VIDÉO POKER | BUREAU DE PAIE, BOULANGERIE, BINGO |

⚠️ **Le bingo et le Rialto changent de porte** : la façade « BINGO » que le bingo préférait
est devenue un VIDÉO POKER (le standing tire dans une liste filtrée, les rangs bougent). Le
bingo ouvre maintenant dans un entrepôt de 126 tuiles de La Shop, le Rialto dans un
bâtiment de 63. Les juges des enseignes, Python et navigateur, sont verts.

⚠️ **Pourquoi pas à la construction** : un nom tiré dans `choisir_enseigne` élargit le
bandeau et change le nombre de tirages de la pancarte — le dé des devantures glisse
(`vitrines.py` l'a déjà écrit). Et la réserve n'entre pas dans `COMMERCES` : un catalogue
plus long change le rang tiré, et toute la ville change de noms.

⚠️ **Le juge mesure par la construction** (`tests/test_commerce_a_la_mesure.py`) : un espion
sur `poser_devanture` compte la part au moment où l'enseigne se pose, sans relire
`aires_des_devantures`. Il mord : sans le passage, 5 enseignes ou plus retombent hors mesure.
Il tient sur les graines 1, 7 et 99 (la graine 1 a exigé la réserve : La Shop n'a que des
petits noms de bouffe).

**Hors de ce jalon, relevé pour Martin** : les seize lieux garantis ont leur plan dessiné et
leur bâtiment se taille à eux ; certains sont petits pour ce qu'ils sont — le **terminus**
fait 9 × 6 comme le dépanneur, l'**hôpital** 12 × 8 sur deux étages. Les agrandir déplace
la ville (voir « grossir un lieu garanti ») : c'est une décision à part.

