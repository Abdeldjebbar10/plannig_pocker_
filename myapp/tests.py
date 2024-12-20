from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from .models import Partie, Joueur, Fonctionnalite
import json

class PartieTests(TestCase):
    def setUp(self):
        # Créer un joueur (utilisateur)
        self.joueur = Joueur.objects.create(nom='Alice', email='alice@example.com')
        # Créer un joueur admin
        self.admin = Joueur.objects.create(nom='Admin', email='admin@example.com')
        
        # Créer une partie
        self.partie = Partie.objects.create(nom='Test Partie', admin=self.admin)
        
        # Ajouter des joueurs à la partie
        self.partie.participants.add(self.joueur)
        
        # Créer des fonctionnalités
        self.fonctionnalite_data = [
            {
                "id": 1,
                "name": "Authentification",
                "description": "Se connecter avec email et mot de passe",
                "priority": "haute"
            },
            {
                "id": 2,
                "name": "Création de profil",
                "description": "Créer et modifier un profil utilisateur",
                "priority": "moyenne"
            }
        ]
        # Sauvegarder les fonctionnalités dans la base de données
        for data in self.fonctionnalite_data:
            Fonctionnalite.objects.create(**data)

    def test_creation_partie(self):
        """Test de la création de partie et de l'ajout de participants"""
        response = self.client.get(reverse('liste_parties'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Partie')  # Vérifie si la partie apparaît dans la liste des parties
    
    def test_importer_fonctionnalites(self):
        """Vérifier si les fonctionnalités sont correctement importées depuis un fichier JSON"""
        with open('backlog.json', 'w', encoding='utf-8') as f:
            json.dump(self.fonctionnalite_data, f, ensure_ascii=False, indent=4)
        
        self.partie.importer_fonctionnalites('backlog.json')  # Importer les fonctionnalités depuis le fichier JSON
        
        # Vérifie que les fonctionnalités ont bien été ajoutées à la base de données
        self.assertEqual(Fonctionnalite.objects.count(), len(self.fonctionnalite_data))
        
    def test_voter_partie(self):
        """Test de l'enregistrement d'un vote"""
        response = self.client.post(reverse('detail_partie', kwargs={'partie_id': self.partie.id}), {
            'fonctionnalite': 1,
            'vote': 5
        })
        
        # Vérifie que le vote a bien été enregistré (vérifie l'URL de la réponse)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('detail_partie', kwargs={'partie_id': self.partie.id}))
