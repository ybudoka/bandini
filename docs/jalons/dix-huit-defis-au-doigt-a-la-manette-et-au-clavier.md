# Dix-huit défis au doigt, à la manette et au clavier

← [les jalons livrés](README.md) · [le plan](../plan.md)

## Fiche

Demande de Martin (22-23 sept. 2026). Il a d'abord demandé « une série d'idées de défis à réussir
avec une manette ou un clavier pour avancer les missions ou les défis » ; on lui en a proposé
dix-huit. Il a répondu : « parfait, je veux tout ça sur la carte, on doit les voir selon s'il est
possible de les faire avec les doigts ou avec la manette ou le clavier. Je veux qu'ils
n'apparaissent pas tous en même temps, mais graduellement quand on passe des défis ou qu'on avance
dans l'histoire. »

**Trois choses, dans cet ordre** :

1. **Chaque défi dit avec quoi il se joue** : `appareils` dans `missions.DEFIS`, une liste parmi
   `doigts`, `manette` et `clavier`. Les dix défis déjà livrés se jouent avec les trois. Un défi neuf
   n'en exclut un que pour une raison **mécanique**, écrite à côté de lui :
   - le **clavier** est tout ou rien : il ne dose ni le gaz ni un angle (huit directions) ;
   - le **doigt**, c'est un seul stick virtuel et quatre boutons : il dose, mais il enchaîne mal les
     appels rapides qui alternent direction et bouton ;
   - la **manette** fait tout, et elle vibre.
2. **Les défis sont sur la carte** (la grande carte, touche N) : un drapeau par défi **débloqué**. Sa
   couleur dit s'il se joue avec **l'appareil qu'on tient** (`Entree.appareil`). Sur la carte, ARME
   change le filtre : l'appareil qu'on tient, puis les deux autres, puis TOUS. Un filtre d'appareil
   ne montre que les défis jouables avec lui, et l'en-tête dessine l'appareil choisi. La proposition
   du défi (COMMENCER / PAS MAINTENANT) dit aussi « SE JOUE AU DOIGT · À LA MANETTE · AU CLAVIER »,
   et prévient quand l'appareil qu'on tient n'y est pas.
3. **Ils arrivent peu à peu** : `debloque` dans le catalogue. Ce sont des conditions qui doivent
   toutes tenir : un nombre de défis réussis (`defis`), des missions faites (`missions`), des défis
   précis réussis (`apres`). Un défi débloqué s'annonce (« NOUVEAU DÉFI »), s'inscrit au journal et bat
   sur la carte tant qu'on n'a pas lu son panneau. Les dix défis de la v1 n'ont pas de `debloque` :
   on ne cache pas ce que le joueur avait déjà.

**Les dix-huit**, par vague. Chacune est jouable, jugée et atterrie avant la suivante.

**Vague 1 — le socle et les jeux debout** (`a_pied`, un nouveau module `adresse.js` : une épreuve
dessinée par-dessus la ville, qu'on joue debout devant son panneau ou son comptoir) :

| Défi | Où | Débloqué par | Appareils | Le geste |
|---|---|---|---|---|
| La roue de Madame Thibodeau | porte du kiosque | 1 défi réussi | les trois | ACTION freine la roue ; elle doit s'arrêter sur le gros lot (3 essais) |
| Le lancer d'anneaux | foire, `lance_anneaux` | 3 défis | les trois | tenir ACTION charge, relâcher dans la bande verte (5 anneaux) |
| Les ratons du kiosque à peluches | foire, `peluches` | 3 défis | les trois | trois trous sur la croix (gauche, haut, droite), taper celui du raton |
| La danse du Bonimenteur | foire, `ballons` | mission `p13` | manette, clavier | « HAUT ! GAUCHE ! FRAPPE ! » de plus en plus vite (doigt exclu : le stick doit revenir au centre entre deux appels) |
| Le mannequin à clochettes | porte du magasin de vêtements | mission `m6` | les trois | une aiguille oscille ; ACTION dans la zone verte, sinon la clochette sonne |
| La radio de la police | porte du poste | mission `m4` | les trois | gauche/droite accorde la fréquence ; la tenir jusqu'à ce que la voix sorte du grésillement |
| Le vieux camion de la cantine | porte de la cantine | mission `e01` | les trois | le moteur tousse en cadence ; ACTION sur chaque toux, cinq de suite |
| Le cadenas de l'armurier | porte de l'armurerie | mission `m53` | manette, doigt | le stick cherche un angle ; tout près, le cadenas tremble (et la manette vibre) ; on tient, la goupille tombe (clavier exclu : ses huit directions ne tombent jamais sur l'angle) |
| Le coffre du bar | porte du bar | mission `m54` et le cadenas réussi | manette, doigt | quatre directions à reproduire, puis deux goupilles au stick, en 60 s |

**Vague 2 — au volant** :

| Défi | Débloqué par | Appareils | Le geste |
|---|---|---|---|
| Le frein pile | 1 défi | les trois | lancé, s'arrêter dans une case peinte d'une tuile |
| Le démarrage au feu | mission `m1` | les trois | partir au vert ; partir avant, c'est un faux départ |
| Le créneau | mission `m3` | les trois | se garer entre deux chars en 20 s, sans toucher personne |
| Le slalom des cônes | 5 défis | les trois | une chicane de cônes ; chaque cône renversé coûte 2 s |
| Le verre de lait | la livraison réussie | manette, doigt | aller au bar sans que le lait déborde : aucun coup de gaz ni de frein brusque (clavier exclu : tout ou rien) |
| Le remorquage | mission `f08` | manette, doigt | tirer un char jusqu'à la fourrière ; un frein brusque le met en portefeuille |

**Vague 3 — dans la rue** :

| Défi | Débloqué par | Appareils | Le geste |
|---|---|---|---|
| La filature | mission `f06` | les trois | rester entre 3 et 6 tuiles de quelqu'un : trop près il se retourne, trop loin on le perd |
| L'esquive du Grand Mo | mission `f04` | les trois | 30 s contre Mo, sans frapper une seule fois : on ne fait qu'esquiver |
| Le défi du chef | le créneau, le frein pile et le slalom réussis | les trois | les trois d'un seul souffle |

⚠️ **Contraintes connues** :

- **Aucun panneau neuf ne nomme une porte neuve.** `devants.lieux_de_mission` lit `missions.DEFIS` :
  une porte que rien ne nommait élargirait son devant, et toute la ville glisserait (voir
  « Grossir un lieu garanti déplace la ville »). On ne prend que des lieux déjà nommés.
- **Un panneau neuf ne naît qu'une fois son défi débloqué**, en fin d'image. Une partie neuve ne
  crée aucune entité de plus au démarrage, et les numéros tirés à l'empreinte ne bougent pas.
- **Le défi du jour ne tourne que sur les défis sans `debloque`** : la rotation d'aujourd'hui ne
  change pas, et le serveur, qui ne connaît pas la partie, ne désigne jamais un défi encore caché.
- **La triche SAUT VERS UN DÉFI débloque le défi qu'elle vise** : c'est une triche.

## Notes
