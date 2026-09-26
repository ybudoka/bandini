# Le centre d'achat hanté

← [les jalons livrés](README.md) · [le plan](../plan.md)

## Fiche

_Proposé le 25 sept. 2026, ajouté au plan par Martin (« oui »)._

_Ce que ça donne :_ un centre d'achat vide, la nuit, une musique d'ascenseur, et une voix au haut-parleur
qui sait où tu es — une mission de peur douce.

**Aujourd'hui** le compte ElevenLabs a une voix **déjà générée et jamais utilisée** : « annonceur centre
d'achat 2 » — « calme, neutre et légèrement étrange, comme un annonceur de centre d'achat hanté »
(`scripts/audio_elevenlabs.py --libres` la dit libre). Elle a été faite pour ça.

- **Le lieu** : une grande pièce (des vitrines, un escalier roulant arrêté, une fontaine), ouverte le jour,
  vide la nuit.
- **La mission** (M16) : quelqu'un a laissé quelque chose au centre d'achat après la fermeture ; les
  lumières s'éteignent une à une, l'annonceur parle (« Client… en rayon 4… votre mère vous attend. »), et un
  gardien qui n'est peut-être pas un gardien.
- **Le ton** : drôle d'abord, inquiétant ensuite — jamais gore (le jeu est un GTA 1 québécois, pas un jeu
  d'horreur).

⚠️ **Ce qui guette** : une pièce plus grande que les autres (le centre d'achat fait plusieurs vitrines) ;
la voix a été générée « à l'ancienne » (pas d'accent garanti en v3) — une audition que Martin écoute.

**Juges** : le centre d'achat se ferme la nuit sans enfermer un lieu de mission ; la mission se joue au
banc ; l'annonceur a sa voix à lui (la table des voix réservées).

## Notes

_Livré le 26 sept. 2026._ ⚠️ **Sans sa mission M16** : une mission ne sait pas encore viser un lieu DANS un
bloc de carte (le GPS vers le passage, un objectif dans sa pièce — la suite du jalon des blocs). Le lieu,
la nuit et la voix sont là ; la mission viendra s'y poser.

- **Les Galeries de la Baie** (`app/blocs/galeries.py`) : un bloc de carte, comme le ciné-parc et la
  cabane — une grande pièce EN VILLE aurait fait glisser la ville. On y entre par le bord OUEST des Érables
  (rangées 60 à 64) ; un stationnement, la façade de vitrines, et dedans une grande pièce : les boutiques
  (leurs étagères), deux comptoirs, l'escalier roulant arrêté, la fontaine, l'aire de restauration.
- **Le jour**, un centre d'achat ordinaire : des commis et des clients, les comptoirs. **La nuit**, personne
  (`vide_la_nuit`, lu par `Entites.peuplerInterieur` avec l'heure du dehors — dans une pièce, il ne fait
  jamais nuit) — et il ne dort pas (`static/js/galeries.js`) :
  - les lumières s'éteignent **une à une**, toutes les sept secondes (un clac d'interrupteur) ; le noir
    gagne, sauf un halo autour du joueur (peint par-dessus la pièce) ;
  - **la voix au haut-parleur** — « annonceur centre d'achat 2 », générée pour ça et jamais utilisée,
    maintenant **réservée** (`audio.VOIX_RESERVEES`) — accueille, annonce les lumières, et **sait où tu
    es** : la fontaine (« Ne vous retournez pas »), l'escalier roulant (« en panne depuis mil neuf cent
    quatre-vingt-sept »), le rayon 4 (« Votre mère vous attend ») ; huit annonces, sous-titrées, en série
    au paquet (`galeries-*`) ;
  - **le gardien qui n'est peut-être pas un gardien** : dès la deuxième lumière éteinte, une silhouette
    grise à casquette et lampe de poche, loin, à des places écrites ; il s'évanouit quand on approche (« le
    gardien n'est pas un gardien »), et revient plus tard ailleurs ;
  - **l'objet perdu** du rayon 4 : un toutou en peluche sur l'étagère du fond, ACTION, 40 $, une fois par
    nuit. Drôle d'abord, inquiétant ensuite, jamais gore.
- **Juges** : `test_galeries_js.py` (on entre par le bord ouest ; du monde le jour, personne la nuit et la
  voix qui accueille ; les lumières une à une et la voix qui voit la fontaine, l'escalier et le rayon ; le
  gardien loin, qui s'évanouit et revient ailleurs ; l'objet une fois par nuit) ; `test_blocs.py` juge le
  plan ; `test_audio.py` la série ; la voix réservée, `test_parole.py`. Chaque juge a été vu rougir sous sa
  mutation.
- ⚠️ **À écouter** : la voix a été générée sans oreille (durées 4 à 7 s ; elle n'a pas d'accent garanti
  en v3 — « une audition que Martin écoute », disait la fiche).
- **Pas fait, à dire** : **la mission** (M16, les blocs d'abord) ; la **musique d'ascenseur** (une dépense à
  trancher) ; le **Père Noël** des Fêtes viendra ici.
