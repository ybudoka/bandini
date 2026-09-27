# Les chantiers restent en ville

← [les jalons livrés](README.md) · [le plan](../plan.md)

## Fiche

Trouvé le 26 sept. 2026 en corrigeant le traversier (le même trou lui laissait un pont fantôme), et
Martin : « va-y ». Dans un bloc de carte (le chalet du rang), `B.interieur` est nul et `Monde.carte` est
le BLOC. `Chantiers.maj` ne se gardait que des pièces : un jour qui change au chalet (on y dort) posait la
phase d'un chantier de la ville dans la carte du bloc, la croyait posée — et la ville ne la recevait
jamais. L'équipe et la benne naissaient dans le bloc, aux coordonnées de la ville ; `efface` et `peindre`
répondent à `Monde` quelle que soit la carte qu'il peint, et les invites « MONTER : PELLETEUSE / GRUE »
lisaient les machines de la ville avec la position du joueur dans le bloc.
