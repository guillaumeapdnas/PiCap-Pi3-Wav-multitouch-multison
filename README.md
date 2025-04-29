# PiCap-Pi3-Wav-multitouch-multison
Ce projet sur Raspberry Pi3 propose une interface graphique pour configurer et déclencher des sons en simultanée via les mesures aux électrodes capacitives (MPR121 via PiCap) et en fonction des intervalles désirées.

** Matériels **  
          ⁃    Raspberry Pi 3  
          ⁃    PiCap BareConductive


![PiCap-Pi3-Wav-multitouch-multison.png](https://github.com/guillaumeapdnas/PiCap-Pi3-Wav-multitouch-multison/blob/main/PiCap-Pi3-Wav-multitouch-multison.png)

Cette interface graphique propose de :\
\
          •    Changer la sensibilité des capteurs\
          •    Sauvegarder/charger la configuration via un fichier ``.JSON`` \
          •    Activer/désactiver la lecture des sons\
          •    Label d'état "Lecture: ON" ou "OFF" en vert ou rouge\
          •    Contrôler le volume global\        
          •    Configurer les plages de seuils de chaque son pour chaque électrode\
          •    Case de synchronisation sous chacune des colonnes : Pour reporter la valeur S[] de E0 pour l'ensemble de la colonne  \
          •    Voir la cellule active (Plage active//son joué) en vert en fonction de la valeur à l'électrode \


**1-Installation du système d’exploitation Raspbian**

**2-Mise à jour du Rasp**

``sudo apt-get update``

``sudo apt-get dist-upgrade``

``sync && sudo reboot``

**3-Installation du paquet PiCap**

``sudo apt-get install picap``

``picap-setup``

Le script picap-setup configure automatiquement les bons GPIOs pour la Pi-Cap

**4-installation des dépendances Python** 

``pip install pygame``

``pip install mpr121``

**5-Arborescence des fichiers sons**
Chaque dossier E0 à E11 contient jusqu'à 12 fichiers .wav nommés 000.wav à 011.wav
.

```
├── diff_sound_player_V2.py
├── MPR121.py
├── tracks/
│   ├── E0/
│   │   ├── 000.wav
│   │   ├── ...
│   ├── E1/
│   │   ├── ...
│   └── ...
└── config.json (optionnel, généré à l'utilisation)
```

**6-Lancer le programme**

``python3 diff_sound_player_V2.py ``

**7- Configuration**
Vous pouvez sauvegarder la configuration actuelle dans un fichier ``.json``, ou en charger un existant.

Le fichier contient :

```
{
  "touch_threshold": 40,
  "release_threshold": 20,
  "plages": [
    [1, 20, 21, 40, ...],  // Pour E0
    ...
  ]
}
```
