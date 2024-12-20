# Application Web Planning Poker

Cette application permet de jouer au **Planning Poker** en ligne, permettant à plusieurs participants d'estimer la difficulté des fonctionnalités d'un projet. Les règles sont flexibles (strict, moyenne, médiane, etc.) et l'application génère un fichier JSON avec les résultats à la fin.

## Fonctionnalités

- **Création de joueurs** : Permet de définir des joueurs avec des rôles (admin ou non).
- **Création de parties** : Sélection des participants et de l'admin pour chaque partie.
- **Vote de fonctionnalités** : Chaque joueur vote avec une carte, et les votes sont validés selon les règles choisies.
- **Mode de jeu** : Strict, moyenne, médiane, etc.
- **Gestion des parties** : Suivi de l'état des parties (en cours, terminé, non commencé).
- **Export JSON** : Sauvegarde des résultats des votes et des fonctionnalités dans un fichier JSON.
- **Reprise de la partie** : Reprise d'une partie en cours à partir d'un fichier JSON sauvegardé.

## Installation

### Prérequis

Avant de démarrer le projet, assurez-vous d'avoir les éléments suivants installés :

- Python 3.x
- pip (gestionnaire de paquets Python)
- Node.js (pour le frontend React)

### Étapes d'installation

1. Clonez ce projet :
   ```bash
   git clone https://votre-repository-url.git
   cd nom_du_dossier

## Technologies
- **Backend** : Django, Django REST Framework
- **Frontend** : React, Axios
- **Base de données** : PostgreSQL
- **Autres** : Docker, CORS


Activer l'environnement virtuel :

Sous Linux/Mac :

source env/bin/activate
Sous Windows :

.\env\Scripts\activate
Une fois activé, tu devrais voir (env) devant ton invite de commande.

Installer Django :

Dans ton environnement virtuel activé, installe Django :

pip install django
Installer d'autres dépendances nécessaires :

Pour ton projet, nous aurons besoin de Django REST Framework (pour créer des API) et django-cors-headers (pour gérer les requêtes du frontend).

pip install djangorestframework django-cors-headers

Créer un projet Django :

Dans ton terminal, exécute cette commande pour créer un nouveau projet Django :

django-admin startproject planning_poker .

Vérifier le projet :

Lance le serveur Django pour t'assurer que tout fonctionne correctement.


python manage.py runserver
Tu devrais voir un message indiquant que le serveur est en cours d'exécution, généralement à l'adresse http://127.0.0.1:8000/.

Ouvre ton navigateur et va à l'adresse http://127.0.0.1:8000/. Si tu vois la page d'accueil Django, cela signifie que tout est correctement installé.

pip install django-widget-tweaks

python manage.py collectstatic





<!-- # Application Web Planning Poker

Cette application permet de jouer au **Planning Poker** en ligne, permettant à plusieurs participants d'estimer la difficulté des fonctionnalités d'un projet. Les règles sont flexibles (strict, moyenne, médiane, etc.) et l'application génère un fichier JSON avec les résultats à la fin.

## Fonctionnalités

- **Création de joueurs** : Permet de définir des joueurs avec des rôles (admin ou non).
- **Création de parties** : Sélection des participants et de l'admin pour chaque partie.
- **Vote de fonctionnalités** : Chaque joueur vote avec une carte, et les votes sont validés selon les règles choisies.
- **Mode de jeu** : Strict, moyenne, médiane, etc.
- **Gestion des parties** : Suivi de l'état des parties (en cours, terminé, non commencé).
- **Export JSON** : Sauvegarde des résultats des votes et des fonctionnalités dans un fichier JSON.
- **Reprise de la partie** : Reprise d'une partie en cours à partir d'un fichier JSON sauvegardé.

## Installation

### Prérequis

Avant de démarrer le projet, assurez-vous d'avoir les éléments suivants installés :

- Python 3.x
- pip (gestionnaire de paquets Python)
- Node.js (pour le frontend React)

### Étapes d'installation

1. Clonez ce projet :
   ```bash
   git clone https://votre-repository-url.git
   cd nom_du_dossier

## Technologies
- **Backend** : Django, Django REST Framework
- **Frontend** : React, Axios
- **Base de données** : PostgreSQL
- **Autres** : Docker, CORS


Activer l'environnement virtuel :

Sous Linux/Mac :

source env/bin/activate
Sous Windows :

.\env\Scripts\activate
Une fois activé, tu devrais voir (env) devant ton invite de commande.

Installer Django :

Dans ton environnement virtuel activé, installe Django :

pip install django
Installer d'autres dépendances nécessaires :

Pour ton projet, nous aurons besoin de Django REST Framework (pour créer des API) et django-cors-headers (pour gérer les requêtes du frontend).

pip install djangorestframework django-cors-headers

Créer un projet Django :

Dans ton terminal, exécute cette commande pour créer un nouveau projet Django :

django-admin startproject planning_poker .

Vérifier le projet :

Lance le serveur Django pour t'assurer que tout fonctionne correctement.


python manage.py runserver
Tu devrais voir un message indiquant que le serveur est en cours d'exécution, généralement à l'adresse http://127.0.0.1:8000/.

Ouvre ton navigateur et va à l'adresse http://127.0.0.1:8000/. Si tu vois la page d'accueil Django, cela signifie que tout est correctement installé.

pip install django-widget-tweaks

python manage.py collectstatic -->
