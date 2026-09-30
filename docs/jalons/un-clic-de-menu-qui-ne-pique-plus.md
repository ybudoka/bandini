# Un clic de menu qui ne pique plus

← [le plan](../plan.md)

## Fiche

Demande de Martin (30 sept. 2026) : « change le son de sélection dans le menu pour un son moins
agressant ».

**Ce que la mesure a montré** — `menu-1.mp3`, le « blip rétro » d'ElevenLabs : 99 % de son énergie
au-dessus de 3 kHz, une fondamentale à 4,4 kHz, un centroïde à 7 kHz, une attaque en 0,1 ms. Et il
part à **chaque** déplacement du curseur (23 appels : menus, pages, onglets, retour). Le filet
synthétisé ne valait pas mieux : un carré à 660 Hz, tout en harmoniques impaires.

**Ce qu'on fait** — la même famille que le refus (`erreur`, 15 sept.) : un petit « tok » rond et
feutré, dans le médium, une attaque adoucie, court ; un peu moins fort. Le filet synthétisé suit :
un sinus bref au lieu du carré.

## Notes

✅ **Livré le 30 sept. 2026.** Écouté et approuvé par Martin, l'ancien et le neuf joués à la suite.

| | avant | après |
|---|---|---|
| fondamentale | 4 402 Hz | 323 Hz |
| centroïde | 7 149 Hz | 324 Hz |
| énergie au-dessus de 3 kHz | 99,4 % | 0,0 % |
| durée du son | 479 ms | 317 ms |
| `volume` | 0,38 | 0,30 |

- Recette neuve dans `app/audio.py` (un maillet feutré sur une petite lame de marimba), régénérée
  par `scripts/audio_elevenlabs.py --refaire menu`. Le fichier garde son nom et son poids
  (6 627 o) : rien ne bouge au paquet.
- Le filet synthétisé (`Son.SFX.menu`, joué tant que le mp3 n'est pas là) passe d'un carré à
  660 Hz à un sinus à 523 Hz.
