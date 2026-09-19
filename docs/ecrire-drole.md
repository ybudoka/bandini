# Écrire drôle — blagues, ressorts et types de texte de Bandini

Guide d'écriture pour toute personne (ou IA) qui écrit des répliques, des
manchettes, des pubs ou des enseignes. Deux moitiés, dans cet ordre :

1. **comment faire rire** — les ressorts de l'humour, ramenés au concret de
   ce qu'on peut écrire en une phrase ou deux dans un jeu ;
2. **les types de texte du jeu** — l'inventaire de tout ce qui se lit ou
   s'entend dans Bandini, avec où ça vit dans le code et la forme que ça prend.

> Ce document ne remplace ni `docs/comment-monter-les-missions.md` (la
> *recette* d'une mission) ni `docs/carte.md` (l'inventaire de la ville) :
> il ne parle que de **texte** — et de ce qui le rend drôle.

---

## 1. Pourquoi on rit — les trois moteurs (et le bonus)

Les recherches sur l'humour se disputent depuis des siècles, mais trois
moteurs reviennent tout le temps (c'est la triade de *Theories of humor*, et
Aristote en parlait déjà). Une bonne blague en allume souvent deux à la fois.

### 1.1 L'incongruité — le moteur principal

On rit quand **deux attentes contradictoires se percutent**. On croyait A, le
texte bascule en B d'un coup, et le cerveau savoure le court-circuit. C'est le
ressort de fond de presque toutes les blagues : la **chute** n'existe que parce
qu'elle contredit ce qu'on pensait.

> « Le propriétaire l'avait laissé tourner. Il ne tourne plus. »
> — *un_char_vole* (`journal.py`) : on croit à une plainte de vol, la chute
> joue sur « tourner » (le moteur / tourner en rond). Deux sens d'un même mot,
> l'un enterre l'autre.

C'est de là que viennent les deux formes les plus fiables :

- **le calembour / double sens** : un mot qui veut dire deux choses, la chute
  en révèle le second (exemple ci-dessus) ;
- **la fusion de deux cadres** (Koestler appelait ça la « bisociation ») : deux
  mondes qui n'ont rien à faire ensemble se croisent soudain — le gangster qui
  parle comme un comptable, le sergent bourru qui dit « j'ai une job » comme
  un vendeur.

### 1.2 La supériorité — rire de quelqu'un, jamais trop méchant

On rit de la **chute des autres** parce qu'on se sent un cran au-dessus
(Hobbes parlait de « gloire soudaine »). Mais — règle d'or pour un jeu qu'on
aime — on rit **deux fois plus** quand la victime *mérite* sa place (c'est la
théorie de la disposition : le sort du méchant amuse, celui du gentil fait
pitié).

Traduction pour Bandini : les Cravates, la police corrompue, un propriétaire
négligent qui laisse tourner son char — on peut se moquer d'eux sans jamais
blesser. **Frapper en haut, jamais en bas** : on ne rit pas des pauvres, de
la maladie, des accidents de gens ordinaires.

### 1.3 Le soulagement — le rire qui relâche la tension

Un moment qui fait peur (une bagarre, une poursuite, une menace) rend la
moindre détente **plus drôle**. C'est le « comic relief » : après José qui
menace, une replique terre-à-terre fait retomber la pression et déclenche le
rire là où une blague seule ne l'aurait pas fait. **Une blague placée juste
après un pic de tension vaut deux fois sa valeur.**

### 1.4 Le bonus moderne : la « violation bénigne »

La théorie la plus citée aujourd'hui (McGraw & Warren) tient en **deux mots** :
le rire naît d'une **transgression… qui reste inoffensive**. Il faut qu'une
norme soit légèrement bousculée (un politiquement incorrect, un jeu de mots
osé, un gros mensonge), mais pas au point de blesser. Si c'est trop violent,
ça répugne ; si c'est trop tiède, ça n'amuse pas. **La zone drôle est pile
au milieu : frotte, mais ne casse pas.**

---

## 2. La recette d'une blague courte (le format du jeu)

Les répliques de Bandini tiennent en **une ou deux phrases**. Voici la
mécanique qui marche à cette taille.

### 2.1 Setup → chute

1. **Le setup** plante UNE seule attente claire, sans bavardage (« Le
   propriétaire l'avait laissé tourner »).
2. **La chute** renverse cette attente en peu de mots (« Il ne tourne plus »).

Règle d'économie : **tout détail qui ne sert pas la chute est en trop.**
Une suite de faits sans surprise n'est pas une blague, c'est une phrase.

### 2.2 La règle de trois

Deux éléments plantent un motif, **le troisième le casse**. C'est le rythme
comique le plus ancien du monde (le plus vieux « joke » connu, vers 1200 av.
J.-C., est déjà un trio).

> Leçon de `journal.py` : « Un coup de klaxon vous trouve un client. Ça marche
> aussi avec la pizza… l'ambulance et la remorqueuse. »
> — *lecon_klaxon* : klaxon (logique), pizza (déjà drôle), ambulance et
> remorqueuse (la bascule absurde). La liste **monte** avant de casser.

### 2.3 Le mot le plus fort à la fin

La tension culmine **sur la toute dernière syllabe**. Ne rien ajouter après :
fixer un détail après la chute la tue. C'est pour ça que le juge
d'`interpretation.py` exige la chute en fin de replique, et que le « … » de
pause ne se pose **jamais** après le dernier mot utile.

### 2.4 Le timing, c'est du son

En jeu, la moitié du rire vient de la **voix** : un « … » bien placé, un soupir
(`[sighs]`), un rire (`[laughs]`) au bon endroit. Voir `docs/` + le module
`app/interpretation.py` : c'est lui qui porte les pauses et les émotions, pas
les balises à l'écran.

### 2.5 L'anti-blague, avec parcimonie

Parfois, **ne pas faire la blague** est la blague (le « shaggy dog story »,
l'anti-humour). Le narrateur du journal en joue : « Brume sur le bassin. Le
traversier a pris du retard… rien à signaler. » La tension d'une manchette
retombe dans le vide. **À doser très rarement**, sinon ça devient juste plat.

---

## 3. Les types de texte du jeu (l'inventaire)

Où ça vit, ce que c'est, la forme attendue. Le code fait foi ; ce tableau doit
le suivre, pas le précéder.

| Type | Où ça vit | Forme | Notes d'écriture |
|---|---|---|---|
| **Répliques de rue** | `audio.py` (VOIX, `salut_h` à `ca_va_f`) + `interpretation.py` (JEU) | 2-3 mots, une émotion, rarement une pause | Les passants qu'on frôle : une seule émotion, vite dite. |
| **Le crieur** | `audio.py` (`approchez_c`…) | 3 phrases courtes, pleine voix, « icitte » | Il vend, ne murmure jamais. |
| **La fille de la Brume** | `audio.py` (`compagnie_b`…) + JEU | accroche douce, invitation | Elle accoste ; la pause est dans l'invitation, jamais dans le prix. |
| **Radio La Brume** | `audio.py` (genre `radio_brume`) | animatrice de nuit, posée | « Il est minuit passé… sur le port. » |
| **Radio Taxi** | `audio.py` (genre `radio_taxi`) | matinale, bonne humeur pleine voix | Balance les embouteillages avec le sourire. |
| **Pubs** | `audio.py` (genre `pub`) + leurs jumelles `_a_toi_` | slogan, 1-2 phrases | Slogan ; la jumelle « a toi » annonce le nouveau proprio. |
| **Manchettes** | `journal.py` (`REGLES`) | `titre` (casse manchette) + `texte` + `lu` (casse naturelle) | Lues au matin selon les stats de la veille, du plus grave au plus banal. |
| **Matins calmes** | `journal.py` (`MATINS`) | mêmes 4 clés que les manchettes | Le repli qui **varie** : jamais le même deux matins de suite. |
| **Leçons du journal** | `journal.py` (`lecon_*` → `narrateur-journal-lecon_*` dans JEU) | micro-tutoriel drôle | Enseigne une mécanique *avec* une blague (klaxon, fourrière, café…). |
| **Ouverture** | `audio.py` `voix_ouverture()` + JEU (`narrateur-ouverture-*`) | 4-5 phrases, une pause par phrase | La minute d'un nouveau joueur ; ne pas la gâcher. |
| **Dialogues de mission** | `app/missions/m*.py` (`dialogue`) | listes `appel`/`intro`/`pendant`/`client`/`fin`/`echec` | Chaque temps a sa voix ; voir `comment-monter-les-missions.md`. |
| **Enseignes / devantures** | `app/devantures.py` (`COMMERCES_COSSUS`, `COMMERCES_PAUVRES`, `A_LOUER`) | un nom de commerce, court, évocateur | Renommées et **placardées** par `app/vitrines.py` ; les cossus vs pauvres. |
| **Graffitis / placardage** | `app/vitrines.py` (motifs de placardage) | motif visuel + texte court | Une vitrine sur trois en pauvre ; jamais au-dessus d'une enseigne visitable. |

---

## 4. Les règles maison (à ne pas casser)

Ce sont les contraintes du projet elles-mêmes ; les oublier, c'est écrire un
texte que le juge refuse ou que la voix massacre.

1. **Le texte affiché = le texte dit.** Un juge (dans `test_inter​pretation.py`)
   retire les balises et les silences et exige **exactement les mêmes mots** que
   la boîte de dialogue. On n'écrit jamais une chose pour l'œil et une autre
   pour l'oreille. Le jeu d'émotion se met **dans** `interpretation.py` (JEU),
   pas en réinventant le texte.

2. **Le slug suit la place, pas le contenu.** Une réplique insérée dans une
   mission décale les slugs d'en dessous ; le même juge l'attrape. La blague
   d'une réplique se corrige *sur place*, on ne ré-ordonne pas.

3. **Une pause par réplique, en tête de respiration.** v3 (ElevenLabs) pèse
   une pause très lourd : « … » + balise au milieu d'une phrase peut doubler la
   durée. Une balise d'émotion par réplique dès qu'elle respire ; « … » au seul
   endroit qui respire vraiment, jamais après un mot seul. (Tout est mesuré et
   expliqué dans `interpretation.py`.)

4. **Jamais de pause avant la chute.** Le temps mort final est ajouté par le
   script (`TEMPS_MORT_S`), pas demandé au modèle ; et une pause posée juste
   avant le mot-clé d'une blague la tue — la chute doit tomber **nette**.

5. **Français canadien, accents corrects.** Tout ce qui est visible ou entendu
   est en québécois naturel (icitte, char, pis, ben) **avec** les accents.
   Voir la règle équivalente pour l'UI dans les préférences du projet.

6. **Frapper en haut, jamais en bas.** On rit des Cravates, de la police
   corrompue, des négligents — pas des pauvres ni de la misère. Une blague qui
   fait mal est une blague qui sort (cf. § 1.2 et § 1.4).

7. **Chaque « bruit de fond » tire un dé qui décale tout le hasard.** Quand on
   ajoute une réplique de rue ou un matin calme, on ne tire **jamais** `B.rng()`
   pour choisir : on passe par l'empreinte stable (voir la leçon du dépôt sur
   les événements continus). Sinon dix juges sans rapport tombent.

---

## 5. Une phrase d'exemple, démontée

Reprenons la réplique en tête de ce guide pour montrer les deux moteurs en une
ligne :

> **« Un char volé au Faubourg. Le propriétaire l'avait laissé tourner. Il ne tourne plus. »**

- **Setup** (2 phrases) : un fait de manchette, puis une circonstance — tout
  le monde croit à une plainte.
- **Chute** (3 mots) : le double sens de « tourner » bascule du moteur au
  *tourner en rond*. Deux cadres, un mot (incongruité).
- **Supériorité douce** : le propriétaire a *mérité* sa place en laissant tourner
  un char — personne n'est blessé, on se sent malin de l'avoir vu.
- **Ton** : `[serious]` sur le fait, `[wryly]` sur la chute (`interpretation.py`)
  — le sarcasme arrive *après* le sérieux, c'est le contraste qui fait rire, pas
  un ton pince-sans-rire du début à la fin.

---

## Sources

Les idées de fond (triade soulagement / supériorité / incongruité, la fusion
de cadres de Koestler, la « violation bénigne » de McGraw-Warren, la règle de
trois et sa plus vieille occurrence, l'anti-blague) viennent des articles
Wikipédia *Theories of humor*, *Joke*, *Comedy* et *Video game writing*,
consultés le 18 septembre 2026. Elles sont reformulées et ancrées dans le code
de Bandini ; le code fait foi.