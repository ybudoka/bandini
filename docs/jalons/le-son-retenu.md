# Le son retenu

← [les jalons livrés](README.md) · [le plan](../plan.md)

## Notes

retour de Martin (« regarde pourquoi je n'ai pas de son ») : un `AudioContext` naît
**suspended** tant que la page n'a reçu aucun **vrai geste** (clic, touche, toucher), et
`resume()` est alors refusé — or **l'API Manette ne compte pas comme un geste**. Depuis
qu'on peut commencer la partie au pad (0.16.0), un joueur à la manette traversait donc toute
la ville en silence, et le refus était avalé par un `.catch()` vide : **rien** ne le disait.

- ⚠️ La panne n'était ni dans les fichiers (79 mp3 servis en 200) ni dans le serveur (le
  paquet annonce bien ses 20 échantillons) ni dans le code du son — elle était dans **la
  permission du navigateur**, qu'on ne pensait même pas à demander. `Son.etatSon()`
  distingue maintenant quatre silences très différents : `actif`, `attente` (il manque un
  geste), `coupe` (choix du joueur, OPTIONS) et `absent` (pas d'audio du tout — le banc) ;
  un bandeau sur l'écran titre dit quoi faire **avant** qu'on joue, un message le redit si
  on commence quand même au pad, et OPTIONS porte une ligne **SON** qui n'est pas un réglage
  mais un **diagnostic** — sans elle, on cherche la panne dans ses haut-parleurs. `resume()`
  étant asynchrone, l'état revient par `onstatechange`, sinon le bandeau resterait affiché
  alors que le son est revenu.
- ⚠️ Le banc a maintenant un **faux AudioContext** (`o.brancherAudio(false)`) qui refuse
  `resume()` : c'est le seul endroit où l'on peut reproduire le silence à volonté — et le
  vrai Chromium des tests le confirme, il charge la page avec un contexte `suspended`
