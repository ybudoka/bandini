# La cabane et le casino s'entendent

← [les jalons livrés](README.md) · [le plan](../plan.md)

## Fiche

Demande de Martin (28 sept. 2026), après la cabane à sucre pour vrai et le casino du Dragon d'or :
« lâche-toi lousse pour ElevenLabs » et « je veux une musique pour le casino et des effets spéciaux pour
ça aussi ». Les deux endroits sont neufs et presque muets : le musicien de la cabane joue le reel du
trottoir à la guitare, la calèche roule sans un bruit de sabot, et le casino joue le silence d'un poste de
police.

- **La cabane** : un vrai violoneux (un reel au violon, le pied qui tape — la toune du musicien de la
  cabane, qui n'emprunte plus celle du trottoir) ; les sabots des deux chevaux au trot et les grelots de la
  calèche, dosés à la distance quand elle roule ; un hennissement quand on monte ; le bouillon de
  l'évaporateur près de la cabane, au temps des sucres.
- **Le casino** : sa musique d'intérieur (une musique de commerce, `MUSIQUES_DE_COMMERCE`), la rumeur de la
  grande salle en boucle, et les gestes : le bras qu'on tire et les rouleaux qui tournent, le gain qui
  sonne et les pièces qui tombent, les cartes du vidéopoker.
- Chaque son a son filet synthétisé, comme partout : un mp3 manquant ne fait pas un silence.

## Notes

**Livré le 28 sept. 2026.** Dix-sept fichiers ElevenLabs, 1 642 crédits (restent 91 508 jusqu'au 23 oct.).

- **Le violoneux** (`musique.VIOLON`, `cabane_violon`) : un reel au violon, le pied qui tape. C'est la toune du
  musicien de la cabane ; il est HORS de `musique.RUE`, un guitariste du Faubourg ne tombe jamais dessus.
- **La calèche** (`caleche`, une boucle : sabots, grelots, roues) : dosée à la distance des chevaux quand elle
  roule, à 0,8 à bord, muette à l'arrêt. **Le hennissement** (deux variantes) quand on monte.
- **L'évaporateur** (`evaporateur`, une boucle) : près de la porte de la cabane au temps des sucres, au plus fort
  dedans ; muet l'hiver.
- **Le casino** : sa musique d'intérieur (`com_casino`, un lounge au vibraphone avec un erhu,
  `MUSIQUES_DE_COMMERCE["nord_casino"]`), la rumeur de la salle en boucle tant qu'on y est, le bras de la machine
  à sous et ses rouleaux, le gain, le gros lot (la table la plus haute), les cinq bips du vidéopoker (au
  Dragon d'or comme au Brouillard).
- **Pour la vague 2 du casino** : `roulette_bille`, `cartes_donnees`, `jetons`, `des_sic_bo`, et leurs gestes
  dans `Son.SFX` — chacun avec son repli synthétisé.
- ⚠️ **LES SONS D'UN LIEU** (`audio.LIEUX`, `Son.Lieu.charger`) : comme les bruits de quartier, ils ne se
  chargent pas au démarrage — la cabane dès qu'on arrive au rang, le casino près de sa porte. Le démarrage
  portait déjà 2,48 Mo sur son plafond de 2,5 ; les 440 Ko de ces deux lieux ont leur plafond de dépôt à part
  (1 Mo), comme les quartiers.
- ⚠️ **LE PAQUET MAIGRIT** : l'export des bruitages envoyait au navigateur le prompt ElevenLabs, la durée
  demandée et l'influence de chaque son — 32 Ko bruts que seul le script de génération lit (dans le
  CATALOGUE, pas dans le paquet). Les définitions passent de 270 194 à 259 451 octets bruts et de 61 038 à
  57 261 gzip, sons neufs compris : de la marge sous les plafonds pour tout le monde.
- Le catalogue des musiques (les notes du filet) monte d'un cran franc, de 56 à 62 Ko (`test_musique`).
- Juges : `tests/test_la_cabane_et_le_casino_s_entendent_js.py` (cinq, un espion posé sur `Son.SFX` ; sept
  mutations, toutes rouges). `test_rang` compte maintenant la villa (quatre blocs), oubliée par
  l'infiltration.
- **Personne n'a écouté les sons** : c'est à Martin de les juger, manette en main.
