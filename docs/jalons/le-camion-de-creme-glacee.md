# Le camion de crème glacée

← [les jalons livrés](README.md) · [le plan](../plan.md)

## Fiche

_Proposé le 25 sept. 2026, ajouté au plan par Martin (« oui »)._

_Ce que ça donne :_ un boulot d'été avec sa petite musique, les enfants à vélo qui courent après — et le
camion le moins soupçonné de la ville.

- **Le boulot** : un camion de crème glacée (une fiche de véhicule), une tournée des parcs et des Érables ;
  la musique attire les enfants, on vend au klaxon (`boulots`, une sorte de plus comme l'autobus).
- **La police** : elle ne fouille jamais un camion de crème glacée — une mission de contrebande s'en sert
  (la chaleur monte moins vite dedans, tant qu'on ne tire pas).
- **Les enfants à vélo** existent déjà : ils suivent la musique.

⚠️ **Ce qui guette** : la musique en boucle doit rester supportable (un fondu, jamais une coupure franche,
et assez rare) ; un sprite de camion de plus ; les enfants qui suivent ne doivent jamais passer sous les
roues.

**Juges** : la musique attire les enfants et s'arrête quand le camion s'arrête ; la chaleur monte moins
vite dedans ; aucun enfant n'est renversé par la tournée (le camion freine).

### Le plan (26 sept. 2026)

1. **Le camion** : `creme_glacee` au catalogue (`freq` 0 — il ne roule pas dans le trafic, sa naissance
   décalerait tous les dés de la ville), une machine en volume (la caisse haute de l'ambulance, un cornet
   sur le toit, des bandes pastel). Il naît **garé, paresseusement**, dans la rue du dépanneur des Érables,
   quand le joueur approche (un identifiant de plus au démarrage décale des juges sans rapport).
2. **Le boulot** `creme_glacee` : au klaxon, une tournée de trois parcs, payée à chaque arrêt.
3. **La ritournelle** : une pièce de la rue (`musique.RUE`, en notes, et un mp3 ElevenLabs), qui joue en
   fondu quand le camion roule sa tournée et se tait quand il s'arrête (`Son.Rue.demander`).
4. **Les enfants à vélo** la suivent — par leur `poste`, qui garde le cycliste hors de la rue ; et ils sont
   intouchables : le camion les pousse, jamais ne les renverse.
5. **La police** : la chaleur monte moitié moins vite dedans (`discret` sur la fiche), tant qu'on ne tire pas.
6. **Juges** : la fiche (les listes du catalogue), le dessin (32 caps, lampes), le boulot et ses paliers,
   la musique qui joue et se tait, les enfants qui suivent sans toucher la rue, la chaleur.

## Notes

**Livré le 26 sept. 2026.**

- **Le camion** (`vehicules.creme_glacee`) : une machine en volume — la caisse haute de l'ambulance, des
  bandes rose et menthe, la fenêtre de service à auvent côté trottoir, un cornet géant sur le toit, qui
  se voit de loin — et, sur chaque flanc, **un vrai cornet complet, pointu** (Martin : « je veux un vrai
  cornet complet sur le côté », « pointu ») : le biscuit qui s'effile jusqu'à une pointe d'un pixel, le
  rebord roulé, une boule rose qui coule, une boule menthe, la cerise (`cornetDeFlanc`). ⚠️ Pas de
  quadrillage gaufré : à cette taille, deux diagonales lui faisaient un visage. `freq` 0 : il ne roule pas dans le trafic ; il attend **garé** dans la rue du dépanneur
  des Érables, et n'y naît qu'à l'approche du joueur, hors champ (jamais au démarrage).
- **La tournée** (`boulot: "creme_glacee"`, au klaxon) : trois arrêts là où le monde s'arrête (les scènes
  de la ville — parcs, place publique), une vente à chacun ; ses paliers : la ritournelle du quartier (+30 %),
  les kiosques à −25 %, et le camion à toi à cinquante tournées.
- **La ritournelle** (`musique.RITOURNELLE`, en notes, et un mp3 ElevenLabs de 30 s — une boîte à musique en
  do majeur) : elle sort du camion quand il **roule** sa tournée (`Son.Rue.demander`, donc en fondu) et se
  tait quand il s'arrête. ⚠️ Le budget des musiques écrites passe de 52 à 56 Ko, un cran franc, écrit.
- **Les enfants à vélo** du coin la suivent : leur `poste` devient le camion (le garde du cycliste les
  tient sur le trottoir), et ils l'oublient dix secondes après qu'elle s'est tue. Intouchables, le camion les
  pousse, jamais ne les renverse.
- **La police** (`discret: 0.5` sur la fiche, `Police.discretion`) : dans le camion, un délit chauffe moitié
  moins — sauf ceux où l'on a une arme à la main (arme sortie, coup ou mort d'un policier, explosion, otage,
  braquage).
- **Juges** (`tests/test_creme_glacee_js.py`) : il naît garé à l'approche et pas au démarrage ; au klaxon la
  tournée, la ritournelle en roulant et pas à l'arrêt, la vente au premier arrêt ; l'enfant qui suit sans
  une image sur la chaussée ; la chaleur à moitié, l'arme en entier ; l'économie. Trois mutations les font
  rougir. ⚠️ **Personne n'a encore écouté la ritournelle.**

