import json
import os
from django.db import models
from django.conf import settings

class Participant(models.Model):
    """
    @class Participant
    @brief Modèle pour représenter un joueur.
    """
    pseudo = models.CharField(max_length=200, unique=True)
    est_admin = models.BooleanField(default=False)  # Pour déterminer si le joueur est admin

    def __str__(self):
        """
        @brief Retourne le pseudo du participant.
        @return Le pseudo du participant.
        """
        return self.pseudo

class Fonctionnalite(models.Model):
    """
    @class Fonctionnalite
    @brief Modèle pour représenter une fonctionnalité dans le backlog.
    """
    name = models.CharField(max_length=200)
    description = models.TextField()
    valide = models.BooleanField(default=False)  # Indique si la fonctionnalité a été validée par tous
    difficulte = models.FloatField(null=True, blank=True)  # Moyenne des votes

    def __str__(self):
        """
        @brief Retourne le nom de la fonctionnalité.
        @return Le nom de la fonctionnalité.
        """
        return self.name

class Partie(models.Model):
    """
    @class Partie
    @brief Modèle pour représenter une partie.
    """
    nom = models.CharField(max_length=200, unique=True)
    admin = models.ForeignKey(Participant, on_delete=models.SET_NULL, null=True, related_name='parties_gerees')
    participants = models.ManyToManyField(Participant, related_name='parties')
    statut = models.CharField(max_length=20, default="new")
    mode_jeu = models.CharField(
        max_length=50,
        choices=[('strict', 'Strict'), ('moyenne', 'Moyenne')],
        default='strict'
    )
    fonctionnalites = models.ManyToManyField(Fonctionnalite, related_name='parties', blank=True)  # Ajout des fonctionnalités

    def sauvegarder_backlog(self):
        """
        @brief Sauvegarde le backlog validé dans un fichier JSON.
        @return Le chemin du fichier JSON sauvegardé.
        """
        fichier_json = os.path.join(settings.BASE_DIR, 'static/data/backlog_valide.json')
        fonctionnalites_validees = self.fonctionnalites.filter(valide=True)
        backlog_data = []
        for f in fonctionnalites_validees:
            votes = Vote.objects.filter(fonctionnalite=f, partie=self)
            moyenne = self.calculer_moyenne_votes(votes)
            votes_data = [
                {
                    "participant": vote.participant.pseudo,
                    "vote": vote.vote
                }
                for vote in votes
            ]

            backlog_data.append({
                'name': f.name,
                'description': f.description,
                'moyenne_difficulte': moyenne,
                'votes': votes_data
            })
        with open(fichier_json, 'w') as fichier:
            json.dump(backlog_data, fichier, indent=4)
        return fichier_json

    def calculer_moyenne_votes(self, votes):
        """
        @brief Calcule la moyenne des votes.
        @param votes Liste des votes.
        @return La moyenne des votes.
        """
        valeurs_valides = [vote.vote for vote in votes if isinstance(vote.vote, int)]
        return round(sum(valeurs_valides) / len(valeurs_valides), 2) if valeurs_valides else 0

    def sauvegarder_etat_partie(self):
        """
        @brief Sauvegarde l'état complet de la partie dans un fichier JSON, y compris les votes précédents.
        @return Le chemin du fichier JSON sauvegardé.
        """
        fichier_etat = os.path.join(settings.BASE_DIR, 'static/data/etat_partie.json')

        # Préparer les fonctionnalités restantes et validées avec les votes
        fonctionnalites_data = []
        for fonctionnalite in self.fonctionnalites.all():
            votes = Vote.objects.filter(fonctionnalite=fonctionnalite, partie=self)
            votes_data = [
                {
                    "participant": vote.participant.pseudo,
                    "vote": vote.vote
                }
                for vote in votes
            ]
            fonctionnalites_data.append({
                "name": fonctionnalite.name,
                "description": fonctionnalite.description,
                "valide": fonctionnalite.valide,  # Indique si la fonctionnalité est validée
                "votes": votes_data  # Inclut tous les votes pour cette fonctionnalité
            })

        # Préparer les données générales de la partie
        etat_data = {
            "partie": self.nom,
            "statut": self.statut,
            "fonctionnalites": fonctionnalites_data,  # Inclut toutes les fonctionnalités (validées et restantes)
            "participants": [p.pseudo for p in self.participants.all()]
        }

        # Sauvegarder les données dans un fichier JSON
        with open(fichier_etat, 'w') as fichier:
            json.dump(etat_data, fichier, indent=4)

        return fichier_etat

    def __str__(self):
        """
        @brief Retourne le nom de la partie.
        @return Le nom de la partie.
        """
        return self.nom

class Vote(models.Model):
    """
    @class Vote
    @brief Modèle pour représenter un vote.
    """
    PARTIE_CHOICES = [
        ('strict', 'Strict'),
        ('moyenne', 'Moyenne'),
        ('mediane', 'Médiane'),
        ('majorite_absolue', 'Majorité absolue'),
        ('majorite_relative', 'Majorité relative'),
    ]

    participant = models.ForeignKey(Participant, on_delete=models.CASCADE)
    fonctionnalite = models.ForeignKey(Fonctionnalite, on_delete=models.CASCADE)
    partie = models.ForeignKey(Partie, on_delete=models.CASCADE)
    vote = models.CharField(max_length=20)  # Permet des valeurs numériques ou textuelles
    mode_jeu = models.CharField(max_length=20, choices=PARTIE_CHOICES)
    fonctionnalite_valide = models.BooleanField(default=False)  # Sauvegarde l'état valide/non-valide

    def save(self, *args, **kwargs):
        """
        @brief Sauvegarde le vote et met à jour l'état de la fonctionnalité.
        """
        if self.fonctionnalite:  # Copier l'état valide de la fonctionnalité
            self.fonctionnalite_valide = self.fonctionnalite.valide
        super().save(*args, **kwargs)

    def __str__(self):
        """
        @brief Retourne une représentation textuelle du vote.
        @return Une chaîne décrivant le vote.
        """
        return f"Vote de {self.participant.pseudo} pour {self.fonctionnalite.name if self.fonctionnalite else 'Fonctionnalité supprimée'}"

    def est_unanime(self):
        """
        @brief Vérifie si tous les joueurs ont voté de manière unanime dans le mode strict.
        @return True si tous les votes sont identiques, sinon False.
        """
        votes = Vote.objects.filter(fonctionnalite=self.fonctionnalite, partie=self.partie)
        votes_unique = votes.values_list('vote', flat=True).distinct()

        # Si tous les votes sont identiques (unanimité), on valide la fonctionnalité
        if len(votes_unique) == 1:
            return True
        return False

class ValidationFonctionnalite(models.Model):
    """
    @class ValidationFonctionnalite
    @brief Modèle pour suivre l'état du vote et valider la fonctionnalité selon le mode de jeu.
    """
    fonctionnalite = models.ForeignKey(Fonctionnalite, on_delete=models.CASCADE)
    partie = models.ForeignKey(Partie, on_delete=models.CASCADE)
    validée = models.BooleanField(default=False)

    def valider_fonctionnalite_strict(self):
        """
        @brief Validation des votes en mode strict : Unanimité.
        @return True si la fonctionnalité est validée, sinon False.
        """
        votes = Vote.objects.filter(fonctionnalite=self.fonctionnalite, partie=self.partie)
        votes_unique = votes.values_list('vote', flat=True).distinct()

        if len(votes_unique) == 1:  # Si tous les votes sont identiques (unanimité)
            self.validée = True
            self.save()
            return True
        return False

    def valider_fonctionnalite_autres_modes(self):
        """
        @brief Validation des votes pour d'autres modes (Moyenne, Médiane, etc.).
        @return False pour l'instant, à implémenter selon les modes de validation.
        """
        votes = Vote.objects.filter(fonctionnalite=self.fonctionnalite, partie=self.partie)
        if self.partie.statut == 'en_cours':
            # Calculer la méthode de validation selon le mode choisi dans la partie
            if self.partie.mode_jeu == 'moyenne':
                # Exemple de calcul pour la moyenne
                pass
            elif self.partie.mode_jeu == 'mediane':
                # Exemple de calcul pour la médiane
                pass
            # Ajouter les autres modes de validation ici...
            pass
        return False










































# import json
# import os
# from django.db import models
# from django.conf import settings

# # Modèle pour représenter un joueur
# class Participant(models.Model):
#     pseudo = models.CharField(max_length=200,unique=True)
#     est_admin = models.BooleanField(default=False)  # Pour déterminer si le joueur est admin

#     def __str__(self):
#         return self.pseudo

# # Modèle pour représenter une fonctionnalité dans le backlog



# class Fonctionnalite(models.Model):
#     name = models.CharField(max_length=200)
#     description = models.TextField()
#     valide = models.BooleanField(default=False)  # Indique si la fonctionnalité a été validée par tous
#     difficulte = models.FloatField(null=True, blank=True)  # Moyenne des votes

#     def __str__(self):
#         return self.name


# class Partie(models.Model):


#     nom = models.CharField(max_length=200,unique=True)
#     admin = models.ForeignKey(Participant, on_delete=models.SET_NULL, null=True, related_name='parties_gerees')
#     participants = models.ManyToManyField(Participant, related_name='parties')
#     statut = models.CharField(max_length=20,default="new")
#     mode_jeu = models.CharField(
#         max_length=50,
#         choices=[('strict', 'Strict'), ('moyenne', 'Moyenne')],
#         default='strict'
#     )
#     fonctionnalites = models.ManyToManyField(Fonctionnalite, related_name='parties', blank=True)  # Ajout des fonctionnalités

#     # def importer_fonctionnalites(self, fichier_json):
#     #     """
#     #     Charge les fonctionnalités depuis le fichier backlog.json et les insère dans la base de données
#     #     """
#     #     import json
#     #     with open(fichier_json, 'r') as file:
#     #         data = json.load(file)
#     #         for item in data:
#     #             fonction, created = Fonctionnalite.objects.get_or_create(
#     #                 name=item['name'],
#     #                 description=item['description'],                )
#     #             self.fonctionnalites.add(fonction)  # Ajoute la fonctionnalité à la partie\
#     def sauvegarder_backlog(self):
#         """Sauvegarde le backlog validé dans un fichier JSON."""     
#         fichier_json = os.path.join(settings.BASE_DIR, 'static/data/backlog_valide.json')  
#         fonctionnalites_validees = self.fonctionnalites.filter(valide=True)
#         backlog_data = []
#         for f in fonctionnalites_validees:
#             votes = Vote.objects.filter(fonctionnalite=f, partie=self)
#             moyenne = self.calculer_moyenne_votes(votes)
#             votes_data = [
#             {
#                 "participant": vote.participant.pseudo,
#                 "vote": vote.vote
#             }
#             for vote in votes
#         ]

#             backlog_data.append({
#             'name': f.name,
#             'description': f.description,
#             'moyenne_difficulte': moyenne,
#             'votes': votes_data
#         })
#         with open(fichier_json, 'w') as fichier:
#             json.dump(backlog_data, fichier, indent=4)
#         return fichier_json 
                 

#     def calculer_moyenne_votes(self, votes):
#         """Calcule la moyenne des votes."""
#         valeurs_valides = [vote.vote for vote in votes if isinstance(vote.vote, int)]
#         return round(sum(valeurs_valides) / len(valeurs_valides), 2) if valeurs_valides else 0


#     # def sauvegarder_etat_partie(self):

#     #     """Sauvegarde l'état de la partie dans un fichier JSON, y compris les votes précédents."""
#     #     fichier_etat = os.path.join(settings.BASE_DIR, 'static/data/etat_partie.json')

#     # # Préparer les fonctionnalités restantes et inclure les votes
#     #     fonctionnalites_restantes = []
#     #     for fonctionnalite in self.fonctionnalites.filter(valide=False):
#     #         votes = Vote.objects.filter(fonctionnalite=fonctionnalite, partie=self)
#     #         votes_data = [
#     #         {
#     #             "participant": vote.participant.pseudo,
#     #             "vote": vote.vote
#     #         }
#     #         for vote in votes
#     #     ]
#     #         fonctionnalites_restantes.append({
#     #         "name": fonctionnalite.name,
#     #         "description": fonctionnalite.description,
#     #         "valide": fonctionnalite.valide,
#     #         "votes": votes_data  # Include the votes for this fonctionnalité
#     #     })

#     # # Préparer les données générales de la partie
#     #     etat_data = {
#     #     "partie": self.nom,
#     #     "statut": self.statut,
#     #     "fonctionnalites_restantes": fonctionnalites_restantes,
#     #     "participants": [p.pseudo for p in self.participants.all()]
#     # }

#     # # Sauvegarder les données dans un fichier JSON
#     #     with open(fichier_etat, 'w') as fichier:
#     #         json.dump(etat_data, fichier, indent=4)

#     #     return fichier_etat

#     def sauvegarder_etat_partie(self):
#         """Sauvegarde l'état complet de la partie dans un fichier JSON, y compris les votes précédents."""
#         fichier_etat = os.path.join(settings.BASE_DIR, 'static/data/etat_partie.json')

#     # Préparer les fonctionnalités restantes et validées avec les votes
#         fonctionnalites_data = []
#         for fonctionnalite in self.fonctionnalites.all():
#             votes = Vote.objects.filter(fonctionnalite=fonctionnalite, partie=self)
#             votes_data = [
#             {
#                 "participant": vote.participant.pseudo,
#                 "vote": vote.vote
#             }
#             for vote in votes
#         ]
#             fonctionnalites_data.append({
#             "name": fonctionnalite.name,
#             "description": fonctionnalite.description,
#             "valide": fonctionnalite.valide,  # Indique si la fonctionnalité est validée
#             "votes": votes_data  # Inclut tous les votes pour cette fonctionnalité
#         })

#     # Préparer les données générales de la partie
#         etat_data = {
#         "partie": self.nom,
#         "statut": self.statut,
#         "fonctionnalites": fonctionnalites_data,  # Inclut toutes les fonctionnalités (validées et restantes)
#         "participants": [p.pseudo for p in self.participants.all()]
#         }

#     # Sauvegarder les données dans un fichier JSON
#         with open(fichier_etat, 'w') as fichier:
#             json.dump(etat_data, fichier, indent=4)

#         return fichier_etat



#     def __str__(self):
#         return self.nom




# # Modèle pour représenter un vote
# class Vote(models.Model):
#     PARTIE_CHOICES = [
#         ('strict', 'Strict'),
#         ('moyenne', 'Moyenne'),
#         ('mediane', 'Médiane'),
#         ('majorite_absolue', 'Majorité absolue'),
#         ('majorite_relative', 'Majorité relative'),
#     ]

#     participant = models.ForeignKey(Participant, on_delete=models.CASCADE)
#     fonctionnalite = models.ForeignKey(Fonctionnalite, on_delete=models.CASCADE)
#     partie = models.ForeignKey(Partie, on_delete=models.CASCADE)
#     vote = models.CharField(max_length=20)  # Permet des valeurs numériques ou textuelles
#     mode_jeu = models.CharField(max_length=20, choices=PARTIE_CHOICES)
#     fonctionnalite_valide = models.BooleanField(default=False)  # Sauvegarde l'état valide/non-valide
#     def save(self, *args, **kwargs):
#         if self.fonctionnalite:  # Copier l'état valide de la fonctionnalité
#             self.fonctionnalite_valide = self.fonctionnalite.valide
#         super().save(*args, **kwargs)

#     def __str__(self):
#         return f"Vote de {self.participant.pseudo} pour {self.fonctionnalite.name if self.fonctionnalite else 'Fonctionnalité supprimée'}"    
#     def __str__(self):
#         return f"Vote de {self.participant.pseudo} pour {self.fonctionnalite.name}"

#     def est_unanime(self):
#         """
#         Vérifie si tous les joueurs ont voté de manière unanime dans le mode strict.
#         """
#         votes = Vote.objects.filter(fonctionnalite=self.fonctionnalite, partie=self.partie)
#         votes_unique = votes.values_list('vote', flat=True).distinct()

#         # Si tous les votes sont identiques (unanimité), on valide la fonctionnalité
#         if len(votes_unique) == 1:
#             return True
#         return False

# # Modèle pour suivre l'état du vote et valider la fonctionnalité selon le mode de jeu
# class ValidationFonctionnalite(models.Model):
#     fonctionnalite = models.ForeignKey(Fonctionnalite, on_delete=models.CASCADE)
#     partie = models.ForeignKey(Partie, on_delete=models.CASCADE)
#     validée = models.BooleanField(default=False)

#     def valider_fonctionnalite_strict(self):
#         """
#         Validation des votes en mode strict : Unanimité
#         """
#         votes = Vote.objects.filter(fonctionnalite=self.fonctionnalite, partie=self.partie)
#         votes_unique = votes.values_list('vote', flat=True).distinct()

#         if len(votes_unique) == 1:  # Si tous les votes sont identiques (unanimité)
#             self.validée = True
#             self.save()
#             return True
#         return False

#     def valider_fonctionnalite_autres_modes(self):
#         """
#         Validation des votes pour d'autres modes (Moyenne, Médiane, etc.)
#         """
#         votes = Vote.objects.filter(fonctionnalite=self.fonctionnalite, partie=self.partie)
#         if self.partie.statut == 'en_cours':
#             # Calculer la méthode de validation selon le mode choisi dans la partie
#             if self.partie.mode_jeu == 'moyenne':
#                 # Exemple de calcul pour la moyenne
#                 pass
#             elif self.partie.mode_jeu == 'mediane':
#                 # Exemple de calcul pour la médiane
#                 pass
#             # Ajouter les autres modes de validation ici...
#             pass
#         return False
# # Modèle pour représenter une partie