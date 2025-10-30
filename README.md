🧮 Bit Packing Project – Software Engineering 2025



Université Côte d’Azur — Rania Taha



🎯 Objectif du projet



Ce projet vise à implémenter une méthode efficace de compression et décompression d’entiers appelée Bit Packing, afin d’accélérer la transmission de données numériques sur le réseau. L’objectif est de réduire le nombre de bits à transmettre tout en préservant un accès direct à l’i-ème élément du tableau original, même après compression. Trois variantes ont été développées :



BitPacking Crossing → compression avec chevauchement sur plusieurs entiers.



BitPacking Non-Crossing → compression sans chevauchement (alignement 32 bits).



BitPacking Overflow → gestion des valeurs exceptionnelles dans une zone d’overflow pour éviter le gaspillage de bits.



🧱 Structure du projet

bitpackingproject/

├── bitpacking/           → Code source principal (BitPacking, BitPackerOverflow)

├── cli/                  → Interface en ligne de commande (Click CLI)

├── tests/                → Tests unitaires Pytest (14 tests)

├── bench/                → Scripts de benchmarks (temps + ratio)

├── requirements.txt      → Dépendances Python

├── README.md             → Documentation du projet

└── report.pdf            → Rapport final du projet



⚙️ Installation et environnement



1️⃣ Cloner le dépôt



git clone https://github.com/raniataha049/bitpackingproject.git

cd bitpackingproject





2️⃣ Créer et activer un environnement virtuel

Sous Windows PowerShell :



python -m venv env

Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass

.\\env\\Scripts\\activate





Sous macOS / Linux :



python3 -m venv env

source env/bin/activate





3️⃣ Installer les dépendances



pip install -r requirements.txt



🧪 Exécution des tests unitaires



Tous les tests sont réalisés avec pytest et couvrent l’ensemble du code.



python -m pytest -v





✅ Résultat attendu :



==================== 14 passed in ...s ====================





Les tests valident la cohérence des opérations bit à bit, la compression et la décompression, l’accès direct get(i) sans décompression complète, et la bonne gestion du mode Overflow.



💻 Utilisation du programme (CLI)



Le dossier cli/ contient une interface de commande basée sur Click.



Compression (mode Overflow)



python -m cli.overflow\_cli compress --input data.txt --output data\_overflow.bin





Décompression



python -m cli.overflow\_cli decompress --input data\_overflow.bin --output restored.txt





Lecture d’un élément par index



python -m cli.overflow\_cli get --input data\_overflow.bin --index 5





Longueur du tableau compressé



python -m cli.overflow\_cli len --input data\_overflow.bin



📈 Benchmarks et performances



Des scripts PowerShell sont fournis dans le dossier bench/ pour mesurer les temps de compression/décompression, le gain de taille et le seuil de latence t\*.

Exécution :



pwsh bench/run\_bench.ps1





Les résultats sont exportés dans bench/results.csv.



🧮 Calcul du seuil de latence (t\*)



Sans compression :



T\_raw = L + (S\_raw / B)





Avec compression :



T\_comp = Tcompress + L + (S\_comp / B) + Tdecompress





Compression avantageuse si T\_comp < T\_raw.

Seuil :



L\* = (Tcompress + Tdecompress) + (S\_comp - S\_raw) / B





avec L = latence, B = bande passante, S\_raw/S\_comp = tailles.



🧠 Détails techniques



Représentation sur k bits par entier.



Codage bit à bit via décalages et masques.



Accès direct calculé par (i\*k)//32 et (i\*k)%32.



Overflow area : 1 bit de flag (0=normal, 1=overflow), payload et zone séparée pour les grandes valeurs.



📚 Validation et couverture de tests

Test	Statut	Description

Compression simple	✅	Comparaison entrée/sortie

Overflow handling	✅	Cas 1024, 2048 testés

Accès direct get(i)	✅	Lecture directe sans décompression

Cas sans overflow	✅	Données homogènes

Cas extrêmes	✅	Zéros et valeurs maximales

CLI import	✅	Vérification de l’exécution des commandes

Total	✅ 14 / 14 tests réussis	

✨ Auteur



Rania Taha

Université Côte d’Azur

Licence Sciences et Technologies – Projet Software Engineering 2025

Encadrant : JC Régin

