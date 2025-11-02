#  BitPacking 2025

##  Présentation du projet

Le projet **BitPacking 2025** a pour objectif d’implémenter une **technique de compression d’entiers sans perte**, afin de réduire la taille mémoire tout en conservant un accès rapide aux données.

Cette méthode est largement utilisée dans :
- les **bases de données**  
- les **systèmes embarqués**  
- les **protocoles réseau**  
- et les **applications d’intelligence artificielle** manipulant de grands volumes de données numériques.


Le projet implémente **trois variantes** principales du BitPacking :

- **Crossing** → Compression maximale avec chevauchement de bits  

- **Non-crossing** → Alignement sur mots mémoire pour une lecture plus simple  

- **Overflow** → Gestion robuste des valeurs dépassant la capacité binaire  

---

##  Architecture du projet

```
bitpackingproject/
│
├──bitpacking/                # Noyau du projet : algorithmes de compression
│   ├── __init__.py
│   ├── core.py
│   ├── crossing.py
│   ├── noncrossing.py
│   ├── overflow.py
│   └── factory.py
│
├── cli/                       # Interface ligne de commande
│   ├── __init__.py
│   ├── bitpacking_cli.py
│   └── overflow_cli.py
│
├── tests/                     # Tests unitaires
│   ├── __init__.py
│   ├── test_core_bits.py
│   ├── test_crossing.py
│   ├── test_overflow.py
│   └── test_smoke.py
│
├── benchmark.py
├── data.txt
├── requirements.txt
├── README.md
└── .gitignore
```




##  Installation

### 1- Cloner le dépôt

```powershell
git clone https://github.com/raniataha049/bitpackingproject.git
```

### 2- Se deplacer dans le dossier `bitpackingproject`

```powershell
cd bitpackingproject
```

### 3- Installer les dépendances

```powershell
pip install -r requirements.txt
```

### 4- Création du fichier de test data.txt

Avant de lancer les commandes de compression, crée un fichier d’exemple contenant une suite d’entiers :

```powershell
Set-Content -Path data.txt -Value "1 2 3 1024 4 5 2048" -Encoding utf8
```

>Le fichier data.txt contiendra :  
>1 2 3 1024 4 5 2048


## Execution 

### 1- Compression et décompression standard

#### 1.1- Mode Crossing

**Compression**
```powershell
python -m cli.bitpacking_cli compress -i data.txt -o data.cross.bin -m crossing
```
**Decompression**
```powershell
python -m cli.bitpacking_cli decompress -i data.cross.bin -o data_out.txt
```

**Résultats affichés** :  
```
OK: 7 integers -> 3 words (k=12, mode=crossing)
OK: decompressed 7 integers (reconstructed mode: k=12, mode=crossing)
```

#### 1.2- Mode Non-crossing

**Compression**
```powershell
python -m cli.bitpacking_cli compress -i data.txt -o data.noncross.bin -m non_crossing
```

**Decompression**
```powershell
python -m cli.bitpacking_cli decompress -i data.noncross.bin -o data_out2.txt
```

**Résultats affichés** :
```
OK: 7 integers -> 4 words (k=12, mode=non_crossing)

OK: decompressed 7 integers (reconstructed mode: k=12, mode=non_crossing)
```

**Vérification** :

```powershell
cmd /c fc data.txt data_out2.txt
```

**Comparaison des fichiers data.txt et DATA_OUT2.TXT** : 

>FC : aucune différence trouvée

#### 1.3- Mode Overflow
**Compression**
```powershell
python -m cli.overflow_cli compress --input data.txt --output data.ovf
```

**Decompression**
```powershell
python -m cli.overflow_cli decompress --input data.ovf --output data_out3.txt
```
**Résultats affichés** :
```
OK: 7 integers -> overflow binary (37 bytes)

OK: decompressed 7 integers (overflow)
```

**Vérification** :
```powershell
cmd /c fc data.txt data_out3.txt
```

**Comparaison des fichiers data.txt et DATA_OUT3.TXT** :
>FC : aucune différence trouvée


<br>

### 2- Accès direct à une valeur compressée (fonction get) 
Le projet implémente une commande spéciale permettant **d’accéder directement à une valeur compressée sans décompresser** tout le fichier.  
Cette opération est très rapide (complexité O(1)).

**Exemple d’utilisation** :
```powershell
python -m cli.overflow_cli get --input data.ovf --index 3
```

**Résultat attendu** :
```
3
```

>Cela signifie que le 4ᵉ entier compressé (index 3) vaut 3.

Cette fonctionnalité prouve que la structure binaire permet un accès aléatoire direct, idéal pour les applications Big Data et systèmes embarqués.

## Tests unitaires

### Execution de l'ensemble des tests 
```powershell
python -m pytest -v
```
Tous les tests doivent passer :  
```
14 passed in 0.3s
```

## Benchmark

Pour mesurer les performances :

```powershell
python benchmark.py
```

**Exemple de sortie** :

```
=== BENCHMARK BITPACKING 2025 ===

Mode : crossing

Type de données : petites valeurs

n = 1000 entiers

Gain : 87.5 %

Tcomp : 0.9881 ms

Tdecomp : 0.6676 ms

Tget : 0.0032 ms

Latence seuil t_seuil : 0.00005913 ms/bit

Résultats principaux

Mode	Type de données	Gain (%)	Tcomp (ms)	Tdecomp (ms)	Tget (ms)

Crossing	Aléatoire	62.5	1.66	1.05	0.0076

Non-crossing	Aléatoire	62.5	1.64	0.89	0.0071

Overflow	Aléatoire	0.0	2.32	1.61	0.0706

Crossing	Petites valeurs	87.5	0.9881	0.6676	0.0032


Types de données testées

Type	Structure	Objectif	Gain observé	Mode optimal

Aléatoires	Dispersée	Mesure de stabilité	62.5 %	Crossing / Non-crossing

Croissantes	Ordonnée	Vérification de cohérence	62.5 %	Crossing

Mélangées	Inhomogène	Gestion des débordements	0–40 %	Overflow

Petites valeurs	Homogène	Gain maximal	87.5 %	Crossing

```

## Rapport complet
Le rapport détaillé est disponible dans le fichier :
📄 Rania_Taha_BitPacking_Report.pdf

### 1-  Structure du rapport 
Il contient :

* la méthodologie complète
* les analyses expérimentales
* la comparaison des trois modes 
* l’étude de la latence et de la complexité.

### 2- Limitations et perspectives
* Ne gère pas encore les entiers négatifs.
* Aucune parallélisation CPU (pas de SIMD).
* Une interface graphique (GUI) est envisagée pour une prochaine version.

### 3- Conclusion
Le projet BitPacking 2025 démontre l’efficacité d’une approche modulaire et performante pour la compression d’entiers sans perte.  
Grâce à ses trois modes de fonctionnement, il offre un excellent compromis entre vitesse, compacité et fiabilité, tout en restant simple à utiliser et à tester.

## Auteurs et encadrement
**Autrice** : Rania Taha — Étudiante en Master 1 Informatique, parcours Intelligence Artificielle  

**Encadrant** : Jean-Charles Régin  

Université Côte d’Azur — Année universitaire 2025–2026

