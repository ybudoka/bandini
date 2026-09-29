# Les Mantes provoquent, et le Petit-Canton a sa musique

← [les jalons livrés](README.md) · [le plan](../plan.md)

## Fiche

Tranché par Martin le 29 sept. 2026, deux choses pour [le Petit-Canton](le-quartier-chinois.md#fiche), après
[les Mantes](l-ecole-rivale.md#notes).

**Les Mantes provoquent.** Sur LEUR territoire (le coin de l'école, au nord-ouest du quartier), un Mante qui te voit
de près vient te défier même à mains nues, avec une réplique en bulle — frimeuse, ils se croient dans un film
([écrire drôle](../ecrire-drole.md), jamais aux dépens de l'origine). Hors de leur territoire, ils font comme les
autres gangs (l'arme au poing, ou un coup). Aucun dé : qui provoque et ce qu'il dit se tirent à l'empreinte, comme
leur combat.

- ⚠️ Ce qui rend ça juste : pas au moment où l'on sort de l'école, pas pendant une mission qui n'a rien à voir avec
  eux, pas un joueur à terre ou dans un char, et un délai avant qu'un deuxième ne remette ça.
- **Juges** : un joueur qui TRAVERSE le territoire se fait défier ; hors du territoire, non ; les Cravates d'à côté
  n'ont pas changé ; la ville d'avant ne bouge pas.

**Une musique de quartier.** Une ambiance de district pour le Petit-Canton (`amb_canton` : `musique.AMBIANCES`,
`AMBIANCES_DE_DISTRICT`, et sa recette mp3 dans `audio.MUSIQUES`), comme `amb_faubourg` — elle joue SOUS la rumeur,
sans batterie ni mélodie qui accroche : un quartier chinois québécois le soir, une touche de guzheng, d'erhu et de
dizi sur une nappe douce, respectueuse, pas une carte postale. Générée par ElevenLabs (Martin : « lâche-toi
lousse »). Elle tranche ce que [une seule musique pour toute la ville](une-seule-musique-pour-toute-la-ville.md) et
la fiche du quartier laissaient « à revoir avec Martin » : il l'a demandée.

- ⚠️ Le poids du catalogue de musique (`test_musique`) et celui du paquet.

## Notes

### Livré le 29 sept. 2026

**Le défi des Mantes** (`Entites.defier`, réglé par `mantes.PROVOCATION`). Sur leur territoire — le joueur ET le Mante
dans la zone `mantes` (`Territoires.gangA`), le coin de l'école —, un Mante qui te voit de près (cinq tuiles, une ligne
libre) vient te défier à mains nues : il s'arrête, se tourne vers toi et dit sa réplique en bulle (`salut`, 50 images,
le temps de la lire et de choisir entre la garde et les jambes), puis attaque avec son répertoire. Frappe-le pendant
sa pose, et il la laisse tomber pour se battre. Hors de leur territoire, rien ne change : l'arme au poing, ou un coup,
comme les autres gangs.

- **Huit répliques** frimeuses (« TON KUNG-FU EST FAIBLE! », « ATTENDS, J’PRENDS LA POSE. », « PREMIÈRE LEÇON :
  GRATIS. », « LE MAÎTRE EST EN FLORIDE. »…) : on rit du gars qui se prend pour un héros de film et de son maître parti
  en Floride, jamais d'un accent ni d'une origine.
- **Aucun dé** : le Mante qui provoque est le premier dont le tour de regard tombe (`e.t % 15`, le tic de l'arme au
  poing) ; sa réplique, à l'empreinte de son numéro et du compte des défis (`hash2`). Aucun décor, aucune entité de
  plus : la ville d'avant et les numéros ne bougent pas.
- **Les garde-fous**, un chiffre chacun : jamais dedans (l'école et ses élèves ne sautent pas sur qui entre), ni dans
  les **6 s** qui suivent une porte (`sortie_images`, l'heure de sortie posée par `Jeu.quitterLaPiece` : `j.sortiA`) ;
  jamais un joueur à terre, assommé, en l'air, tenu, dans un char, l'arme au poing (c'est l'autre règle), ni occupé —
  un défi, une frénésie, une épreuve, ou une mission qui ne les nomme pas (un objectif `groupe: "mantes"` les
  autorise). **Un défi à la fois** (un Mante sur toi, les autres regardent le film), **30 s** avant qu'un deuxième ne
  remette ça (`delai_images`), et chaque Mante ne défie **qu'une fois** dans sa vie.
- ⚠️ **Vu au banc avant de juger** : le premier Mante croisé était `arret` (une pause devant une vitrine, trois fois
  sur dix qu'il choisit sa route), et l'`arret` sort AVANT la règle de l'arme au poing — il a laissé passer le joueur à
  un pas. Le défi se regarde aussi à l'arrêt (jugé : un Mante planté là te voit passer) ; l'arme au poing, elle, n'a
  pas changé.

**La musique du quartier** : `amb_canton`, « Lanternes du Petit-Canton » — `musique.AMBIANCES` (en notes : la
pentatonique `PENTATONIQUE`, 66 bpm, ré ; le filet), `AMBIANCES_DE_DISTRICT["canton"]`, et sa recette dans
`audio.MUSIQUES` : un quartier chinois québécois le soir, guzheng, erhu et dizi sur une nappe douce, « not a
postcard, no gong, no drums ». Générée par ElevenLabs (`--musiques`) : **60,0 s**, 480 280 octets à 64 kbit/s,
−13,4 LUFS (les autres ambiances sont à −13,7), 0,6 s de silence au bout (le Faubourg en a 2,2). **825 crédits**
(32 933 → 33 758 sur 121 007 ; 87 249 restants, remise le 23 oct.). Martin l'a demandée : c'est écrit dans [une seule
musique pour toute la ville](une-seule-musique-pour-toute-la-ville.md#notes) et la fiche du quartier. ⚠️ Personne
ne l'a écoutée : c'est à Martin de dire si elle reste (`--refaire amb_canton`).

- **Le poids** : le catalogue de musique passe 62 097 octets (59 491 avant) — plafond de `test_musique` relevé d'un cran
  franc, 62 → 68 Ko ; les définitions 278 071 bruts / 62 234 gzip (275 603 / 61 557 avant) — plafond gzip 62 → 64 Ko,
  la mesure écrite dans `test_definitions`. Le dossier des musiques : 9,45 Mo, sous ses 12.

**Juges** : `tests/test_mantes_defi_js.py` (au banc : un joueur qui TRAVERSE leur territoire sur la rangée 17 se fait
défier dès la première colonne, par un seul Mante, qui prend la pose ; la même marche sous leur territoire, rien ; les
Cravates chez elles laissent passer un joueur à mains nues et attaquent l'arme au poing, sans bulle ; en sortant de
l'école, pas avant `sortie_images` ; les garde-fous un à un, le délai, un à la fois, une fois par Mante, et **aucun
`B.rng()`** ; les répliques tiennent dans une bulle) et `tests/test_musique_du_canton.py` (l'ambiance déclarée, son
prompt, son mp3 au paquet, et au banc c'est elle qui joue au Petit-Canton).
