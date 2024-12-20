from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.conf import settings
from django.contrib.staticfiles import finders
from django.utils import timezone
import time
from .models import Partie, Fonctionnalite, Vote, ValidationFonctionnalite, Participant
from .forms import PartieForm, VoteForm, ParticipantForm
import json
import os
from django.contrib import messages

def liste_parties(request):
    """
    @fn liste_parties
    @brief Vue pour afficher toutes les parties.
    @param request Objet de requête HTTP.
    @return Réponse HTTP avec la liste des parties.
    """
    parties = Partie.objects.all()
    return render(request, 'parties/liste_parties.html', {'parties': parties})

def creer_partie(request):
    """
    @fn creer_partie
    @brief Vue pour créer une nouvelle partie.
    @param request Objet de requête HTTP.
    @return Réponse HTTP après la création de la partie.
    """
    fichier_json = finders.find('data/backlog.json')  # Chemin vers le fichier JSON

    if request.method == 'POST':
        form = PartieForm(request.POST)
        if form.is_valid():
            # Traitez la partie et les participants
            partie = form.save(commit=False)
            administrateur = form.cleaned_data['administrateur']
            participants = form.cleaned_data['participants']

            # Ajouter l'administrateur aux participants s'il n'est pas déjà présent
            participants = list(participants)
            if administrateur not in participants:
                participants.append(administrateur)

            partie.admin = administrateur
            partie.save()
            partie.participants.set(participants)
            form.save_m2m()

            # Importer ou mettre à jour les fonctionnalités
            with open(fichier_json, 'r') as file:
                data = json.load(file)
                noms_fonctionnalites = [item['name'] for item in data]

                # Mettre à jour les fonctionnalités existantes
                for fonctionnalite in Fonctionnalite.objects.all():
                    if fonctionnalite.name in noms_fonctionnalites:
                        fonctionnalite.valide = False  # Remettre à non valide
                        fonctionnalite.save()

                # Ajouter les nouvelles fonctionnalités
                for item in data:
                    fonctionnalite, created = Fonctionnalite.objects.get_or_create(
                        name=item['name'],
                        defaults={'description': item['description']}
                    )
                    if created:
                        fonctionnalite.valide = False  # Par défaut, non valide
                        fonctionnalite.save()

            # Associer toutes les fonctionnalités à la partie
            toutes_fonctionnalites = Fonctionnalite.objects.all()
            partie.fonctionnalites.set(toutes_fonctionnalites)

            # Message de succès et redirection
            messages.success(request, "La partie a été créée avec succès.")
            return redirect('lister_parties')
        else:
            # En cas d'erreurs de validation
            messages.error(request, "Le formulaire contient des erreurs. Veuillez vérifier vos entrées.")
    else:
        form = PartieForm()

    return render(request, 'parties/cree_partie.html', {'form': form})

def detail_partie(request, id):
    """
    @fn detail_partie
    @brief Vue pour afficher les détails d'une partie.
    @param request Objet de requête HTTP.
    @param id Identifiant de la partie.
    @return Réponse HTTP avec les détails de la partie.
    """
    partie = get_object_or_404(Partie, id=id)
    votes = Vote.objects.filter(partie=partie)
    return render(request, 'parties/detail_partie.html', {
        'partie': partie,
        'votes': votes,
    })

def reprendre_partie(request, partie_id):
    """
    @fn reprendre_partie
    @brief Vue pour reprendre une partie existante.
    @param request Objet de requête HTTP.
    @param partie_id Identifiant de la partie.
    @return Réponse HTTP après la reprise de la partie.
    """
    partie = get_object_or_404(Partie, id=partie_id)
    fichier_etat = os.path.join(settings.BASE_DIR, 'static/data/etat_partie.json')

    if os.path.exists(fichier_etat):
        with open(fichier_etat, 'r') as fichier:
            etat_data = json.load(fichier)

            # Appliquer l'état sauvegardé
            partie.statut = "en_attente"
            for fonctionnalite in etat_data['fonctionnalites']:
                fonction, created = Fonctionnalite.objects.get_or_create(
                    name=fonctionnalite['name'],
                    description=fonctionnalite['description']
                )
                # Ajouter la fonctionnalité à la partie 
                partie.fonctionnalites.add(fonction)
                for vote_data in fonctionnalite.get('votes', []):
                    participant = Participant.objects.get(pseudo=vote_data['participant'])
                    if not Vote.objects.filter(
                        participant=participant,
                        fonctionnalite=fonction,
                        partie=partie,
                        vote=vote_data['vote']
                    ).exists():
                        Vote.objects.create(
                            participant=participant,
                            fonctionnalite=fonction,
                            partie=partie,
                            vote=vote_data['vote']
                        )

            partie.save()
        messages.success(request, "La partie a été reprise avec succès.")
    else:
        messages.error(request, "Impossible de trouver l'état sauvegardé de la partie.")

    return redirect('detail_partie', id=partie.id)

def creer_participant(request):
    """
    @fn creer_participant
    @brief Vue pour créer un nouveau participant.
    @param request Objet de requête HTTP.
    @return Réponse HTTP après la création du participant.
    """
    if request.method == 'POST':
        form = ParticipantForm(request.POST)
        if form.is_valid():
            form.save()  # Sauvegarde le participant dans la base de données
            return redirect('lister_participants')  # Redirige vers la liste des participants après la création
    else:
        form = ParticipantForm()  # Si la requête est en GET, on crée un formulaire vide

    return render(request, 'participants/creer_participant.html', {'form': form})

def menu_principal(request):
    """
    @fn menu_principal
    @brief Vue pour afficher le menu principal.
    @param request Objet de requête HTTP.
    @return Réponse HTTP avec le menu principal.
    """
    participants = Participant.objects.all()
    parties = Partie.objects.all()

    return render(request, 'parties/menu_principal.html', {
        'participants': participants,
        'parties': parties,
    })

def liste_participants(request):
    """
    @fn liste_participants
    @brief Vue pour afficher la liste des participants.
    @param request Objet de requête HTTP.
    @return Réponse HTTP avec la liste des participants.
    """
    participants = Participant.objects.all()
    return render(request, 'participants/liste_participants.html', {'participants': participants})

def lancer_partie(request, partie_id):
    """
    @fn lancer_partie
    @brief Vue pour lancer une partie.
    @param request Objet de requête HTTP.
    @param partie_id Identifiant de la partie.
    @return Réponse HTTP après le lancement de la partie.
    """
    partie = get_object_or_404(Partie, id=partie_id)
    
    if partie.statut == "new":
        partie.statut = "en_attente"
        partie.save()
        # Rediriger vers le vote
        return redirect('demarrer_vote', partie_id=partie.id)
    return redirect('lister_parties')

def demarrer_vote(request, partie_id):
    """
    @fn demarrer_vote
    @brief Vue pour démarrer le vote pour une partie.
    @param request Objet de requête HTTP.
    @param partie_id Identifiant de la partie.
    @return Réponse HTTP pour démarrer le vote.
    """
    partie = get_object_or_404(Partie, id=partie_id)
    fonctionnalite_en_cours = partie.fonctionnalites.filter(valide=False).first()

    if not fonctionnalite_en_cours:
        # Toutes les fonctionnalités ont été votées
        partie.statut = "fin"
        fichier_backlog = partie.sauvegarder_backlog()
        partie.save()
        messages.success(request, "La partie est terminée et le backlog a été mis à jour !")
        return redirect('lister_parties')

    participants = partie.participants.all()
    participant_index = request.session.get('participant_index', 0)
    participant_en_cours = participants[participant_index % participants.count()]

    if request.method == "POST":
        # Enregistrer le vote
        carte_vote = request.POST.get('vote')
        if carte_vote != "interro":  # Ignorer la carte "interro"
            Vote.objects.create(
                participant=participant_en_cours,
                fonctionnalite=fonctionnalite_en_cours,
                partie=partie,
                vote=int(carte_vote) if carte_vote.isdigit() else carte_vote,
                mode_jeu=partie.mode_jeu
            )

        # Passer au prochain participant
        participant_index = (participant_index + 1) % participants.count()
        request.session['participant_index'] = participant_index

        # Si tous les participants ont voté
        if participant_index == 0:
            # Récupérer tous les votes pour la fonctionnalité en cours
            votes = Vote.objects.filter(fonctionnalite=fonctionnalite_en_cours, partie=partie)
            votes_valides = [v.vote for v in votes if isinstance(v.vote, int)]  # Exclure "interro"
            votes_normalises = [int(v.vote) for v in votes if isinstance(v.vote, (int, str)) and str(v.vote).isdigit()]
            votes_unanimes = votes.values_list('vote', flat=True).distinct()
            # Gérer la carte "café"
            if len(votes) == participants.count() and all(v.vote == "cafe" for v in votes):
                fichier_etat = partie.sauvegarder_etat_partie()
                messages.warning(request, f"La partie a été mise en pause. État sauvegardé dans {fichier_etat}.")
                return redirect('lister_parties')

            # Mode Strict : Tous les votes doivent être identiques
            if partie.mode_jeu == "strict":
                if len(votes_unanimes) == 1:
                    fonctionnalite_en_cours.valide = True
                    fonctionnalite_en_cours.save()
                else:
                    votes.delete()
                    messages.warning(request, "Les votes ne sont pas unanimes. Recommencez pour cette fonctionnalité.")

            # Mode Moyenne : Gestion des tours
            elif partie.mode_jeu == "moyenne":
                if not request.session.get('premier_tour_fini', False):
                    # Premier tour : Unanimité obligatoire
                    if len(votes_unanimes) == 1:
                        fonctionnalite_en_cours.valide = True
                        fonctionnalite_en_cours.save()
                        request.session['premier_tour_fini'] = True
                    else:
                        votes.delete()
                        messages.warning(request, "Les votes ne sont pas unanimes. Recommencez pour cette fonctionnalité.")
                        # Premier tour unanime
      
                else:
                    # Deuxième tour et suivants : Calcul de la moyenne
                    if len(votes_unanimes) == 1:
                        fonctionnalite_en_cours.valide = True
                        fonctionnalite_en_cours.save()
                    else:
                        moyenne = partie.calculer_moyenne_votes(votes)
                        messages.info(request, f"Temps de discussion : Moyenne des votes = {moyenne}")
                        time.sleep(10)  # Pause de 10 secondes
                        fonctionnalite_en_cours.valide = True
                        fonctionnalite_en_cours.save()
            request.session['participant_index'] = 0
        return redirect('demarrer_vote', partie_id=partie.id)

    cartes = [0, 1, 2, 3, 5, 8, 13, 20, 40, 100, "cafe", "interro"]
    context = {
        'partie': partie,
        'fonctionnalite_en_cours': fonctionnalite_en_cours,
        'participant_en_cours': participant_en_cours,
        'cartes': cartes,
        # 'discussion_activee': request.session.pop('discussion_activee', False),
        # 'moyenne_vote': request.session.pop('moyenne_vote', None),  # Récupérer la moyenne pour affichage
    }
    return render(request, 'parties/vote.html', context)


# from django.shortcuts import render, redirect ,get_object_or_404
# from django.http import JsonResponse
# from django.conf import settings

# from django.contrib.staticfiles import finders
# from django.utils import timezone
# import time
# from .models import Partie, Fonctionnalite, Vote, ValidationFonctionnalite, Participant
# from .forms import PartieForm, VoteForm , ParticipantForm
# import json
# import os
# from django.contrib import messages

# # Vue pour afficher toutes les parties
# def liste_parties(request):
#     parties = Partie.objects.all()
#     return render(request, 'parties/liste_parties.html', {'parties': parties})

# # Vue pour créer une nouvelle partie
# # def creer_partie(request):
# #     participants = Participant.objects.all()  # Récupère tous les participants

# #     if request.method == 'POST':
# #         form = PartieForm(request.POST)
# #         if form.is_valid():
# #             partie = form.save(commit=False)
# #             partie.admin = form.cleaned_data['administrateur']

# #             partie.save()
# #             form.save_m2m()  # Sauvegarde les relations ManyToMany pour les participants
            
# #             # Redirection vers la page liste des parties
# #             return redirect('lister_parties')  # Assurez-vous que 'liste_parties' est bien défini dans les URLs
# #     else:
# #         form = PartieForm()

# #     return render(request, 'parties/cree_partie.html', {
# #         'form': form,
# #         'participants': participants,
# #     })


# def creer_partie(request):
#     fichier_json = finders.find('data/backlog.json')  # Chemin vers le fichier JSON

#     if request.method == 'POST':
#         form = PartieForm(request.POST)
#         if form.is_valid():
#             # Traitez la partie et les participants
#             partie = form.save(commit=False)
#             administrateur = form.cleaned_data['administrateur']
#             participants = form.cleaned_data['participants']

#             # Ajouter l'administrateur aux participants s'il n'est pas déjà présent
#             participants = list(participants)
#             if administrateur not in participants:
#                 participants.append(administrateur)

#             partie.admin = administrateur
#             partie.save()
#             partie.participants.set(participants)
#             form.save_m2m()

#             # Importer ou mettre à jour les fonctionnalités
#             with open(fichier_json, 'r') as file:
#                 data = json.load(file)
#                 noms_fonctionnalites = [item['name'] for item in data]

#                 # Mettre à jour les fonctionnalités existantes
#                 for fonctionnalite in Fonctionnalite.objects.all():
#                     if fonctionnalite.name in noms_fonctionnalites:
#                         fonctionnalite.valide = False  # Remettre à non valide
#                         fonctionnalite.save()

#                 # Ajouter les nouvelles fonctionnalités
#                 for item in data:
#                     fonctionnalite, created = Fonctionnalite.objects.get_or_create(
#                         name=item['name'],
#                         defaults={'description': item['description']}
#                     )
#                     if created:
#                         fonctionnalite.valide = False  # Par défaut, non valide
#                         fonctionnalite.save()

#             # Associer toutes les fonctionnalités à la partie
#             toutes_fonctionnalites = Fonctionnalite.objects.all()
#             partie.fonctionnalites.set(toutes_fonctionnalites)

#             # Message de succès et redirection
#             messages.success(request, "La partie a été créée avec succès.")
#             return redirect('lister_parties')
#         else:
#             # En cas d'erreurs de validation
#             messages.error(request, "Le formulaire contient des erreurs. Veuillez vérifier vos entrées.")
#     else:
#         form = PartieForm()

#     return render(request, 'parties/cree_partie.html', {'form': form})


# # Vue pour afficher les détails d'une partie    
# def detail_partie(request, id):
#     # Récupère la partie spécifique
#     partie = get_object_or_404(Partie, id=id)

#     # Récupérer tous les votes liés à la partie
#     votes = Vote.objects.filter(partie=partie)

#     return render(request, 'parties/detail_partie.html', {
#         'partie': partie,
#         'votes': votes,  # Passez les votes au template
#     })

# def reprendre_partie(request, partie_id):
#     partie = get_object_or_404(Partie, id=partie_id)
#     fichier_etat = os.path.join(settings.BASE_DIR, 'static/data/etat_partie.json')

#     if os.path.exists(fichier_etat):
#         with open(fichier_etat, 'r') as fichier:
#             etat_data = json.load(fichier)

#             # Appliquer l'état sauvegardé
#             partie.statut = "en_attente"
#             for fonctionnalite in etat_data['fonctionnalites']:
#                 fonction, created = Fonctionnalite.objects.get_or_create(
#                     name=fonctionnalite['name'],
#                     description=fonctionnalite['description']
#                 )
#                 # Ajouter la fonctionnalité à la partie 
#                 partie.fonctionnalites.add(fonction)
#                 for vote_data in fonctionnalite.get('votes', []):
#                     participant = Participant.objects.get(pseudo=vote_data['participant'])
#                     if not Vote.objects.filter(
#                         participant=participant,
#                         fonctionnalite=fonction,
#                         partie=partie,
#                         vote=vote_data['vote']
#                     ).exists():
#                         Vote.objects.create(
#                             participant=participant,
#                             fonctionnalite=fonction,
#                             partie=partie,
#                             vote=vote_data['vote']
#                         )

            

#             partie.save()   

#         messages.success(request, "La partie a été reprise avec succès.")
#     else:
#         messages.error(request, "Impossible de trouver l'état sauvegardé de la partie.")

#     return redirect('detail_partie', id=partie.id)

# def creer_participant(request):
#     if request.method == 'POST':
#         form = ParticipantForm(request.POST)
#         if form.is_valid():
#             form.save()  # Sauvegarde le participant dans la base de données
#             return redirect('lister_participants')  # Redirige vers la liste des participants après la création
#     else:
#         form = ParticipantForm()  # Si la requête est en GET, on crée un formulaire vide

#     return render(request, 'participants/creer_participant.html', {'form': form})


# def menu_principal(request):
#     # Ici, tu peux récupérer les participants et les parties pour les afficher dans le menu
#     participants = Participant.objects.all()
#     parties = Partie.objects.all()

#     return render(request, 'parties/menu_principal.html', {
#         'participants': participants,
#         'parties': parties,
#     })


# def liste_participants(request):
#     participants = Participant.objects.all()
#     return render(request, 'participants/liste_participants.html', {'participants': participants})

# def lancer_partie(request, partie_id):
#     partie = get_object_or_404(Partie, id=partie_id)
    
#     if partie.statut == "new":
#         partie.statut = "en_attente"
#         partie.save()
#         # Rediriger vers le vote
#         return redirect('demarrer_vote', partie_id=partie.id)
#     return redirect('lister_parties')





# # def demarrer_vote(request, partie_id):
# #     # Récupérer la partie
# #     partie = get_object_or_404(Partie, id=partie_id)
    
# #     # Vérifier les fonctionnalités restantes à voter
# #     fonctionnalite_en_cours = partie.fonctionnalites.filter(valide=False).first()
    
# #     if not fonctionnalite_en_cours:
# #         # Toutes les fonctionnalités ont été votées
# #         partie.statut = "fin"
# #         fichier_backlog = partie.sauvegarder_backlog()  
# #         partie.save()
# #         messages.success(request, "La partie est terminée et le backlog a été mis à jour !")
# #         return redirect('lister_parties')
    
# #     # Récupérer le participant suivant
# #     participants = partie.participants.all()
# #     participant_en_cours = participants[(request.session.get('participant_index', 0)) % participants.count()]
    
# #     if request.method == "POST":
# #         # Enregistrer le vote
# #         carte_vote = request.POST.get('vote')
# #         Vote.objects.create(
# #             participant=participant_en_cours,
# #             fonctionnalite=fonctionnalite_en_cours,
# #             partie=partie,
# #             vote=int(carte_vote) if carte_vote.isdigit() else carte_vote,
# #             mode_jeu=partie.mode_jeu
# #         )
        
# #         # Passer au prochain participant
# #         participant_index = (request.session.get('participant_index', 0) + 1) % participants.count()
# #         request.session['participant_index'] = participant_index
        
# #         # Si tous les participants ont voté pour cette fonctionnalité
# #         if participant_index == 0:
# #             # Récupérer tous les votes pour la fonctionnalité en cours
# #             votes = Vote.objects.filter(fonctionnalite=fonctionnalite_en_cours, partie=partie)
# #             votes_valides = [v.vote for v in votes if isinstance(v.vote, int)]  # Exclure "interro"
# #             votes_normalises = [int(v.vote) for v in votes if isinstance(v.vote, (int, str)) and str(v.vote).isdigit()]
# #             # Vérifier si tous les votes sont "café"
# #             if votes.count() == participants.count() and all(v.vote == "cafe" for v in votes):
# #                 fichier_etat = partie.sauvegarder_etat_partie()
# #                 messages.warning(request, f"La partie a été sauvegardée car tous les joueurs ont voté 'café'. État enregistré dans {fichier_etat}.")
# #                 return redirect('lister_parties')
# #             if partie.mode_jeu == "strict":
# #                 votes_unanimes = set(votes_normalises)
# #                 if len(votes_unanimes) == 1:
# #                     fonctionnalite_en_cours.valide = True
# #                     fonctionnalite_en_cours.save()
# #                 else:
# #                     votes.delete()
# #                     messages.warning(request, "Les votes ne sont pas unanimes. Recommencez pour cette fonctionnalité.")
# #             elif partie.mode_jeu == "moyenne":
# #                 if not request.session.get('premier_tour_fini', False):
# #                     # Premier tour : Unanimité requise
# #                     votes_unanimes = set(votes_normalises)
# #                     if len(votes_unanimes) > 1:
# #                         votes.delete()
# #                         messages.warning(request, "Les votes ne sont pas unanimes. Recommencez pour cette fonctionnalité.")
# #                     else:
# #                         request.session['premier_tour_fini'] = True
# #                         fonctionnalite_en_cours.valide = True
# #                         fonctionnalite_en_cours.save()
# #                 else:
# #                     # Calculer la moyenne après discussion
# #                     moyenne = round(sum(votes_valides) / len(votes_valides), 2) if votes_valides else 0
# #                     messages.info(request, f"La moyenne des votes est {moyenne}.")
# #                     request.session['moyenne_vote'] = moyenne  # Stocker la moyenne pour l'affichage
# #                     request.session['discussion_activee'] = True  # Activer le chrono côté client
# #                     messages.info(request, f"La moyenne des votes est {moyenne}.")
# #                     fonctionnalite_en_cours.valide = True
# #                     fonctionnalite_en_cours.save()
# #         return redirect('demarrer_vote', partie_id=partie.id)                  
            
# #     # Charger les cartes de vote (simulées à partir d'un fichier CSV par exemple)
# #     cartes = [0, 1, 2, 3, 5, 8, 13, 20, 40, 100, "cafe", "interro"]
    
# #     context = {
# #         'partie': partie,
# #         'fonctionnalite_en_cours': fonctionnalite_en_cours,
# #         'participant_en_cours': participant_en_cours,
# #         'cartes': cartes,
# #         'discussion_activee': request.session.pop('discussion_activee', False),
# #         'moyenne_vote': request.session.pop('moyenne_vote', None), 
# #     }
# #     return render(request, 'parties/vote.html', context)
# def demarrer_vote(request, partie_id):
#     # Récupérer la partie et la fonctionnalité en cours
#     partie = get_object_or_404(Partie, id=partie_id)
#     fonctionnalite_en_cours = partie.fonctionnalites.filter(valide=False).first()

#     if not fonctionnalite_en_cours:
#         # Toutes les fonctionnalités ont été votées
#         partie.statut = "fin"
#         fichier_backlog = partie.sauvegarder_backlog()
#         partie.save()
#         messages.success(request, "La partie est terminée et le backlog a été mis à jour !")
#         return redirect('lister_parties')

#     participants = partie.participants.all()
#     participant_index = request.session.get('participant_index', 0)
#     participant_en_cours = participants[participant_index % participants.count()]

#     if request.method == "POST":
#         # Enregistrer le vote
#         carte_vote = request.POST.get('vote')
#         if carte_vote != "interro":  # Ignorer la carte "interro"
#             Vote.objects.create(
#                 participant=participant_en_cours,
#                 fonctionnalite=fonctionnalite_en_cours,
#                 partie=partie,
#                 vote=int(carte_vote) if carte_vote.isdigit() else carte_vote,
#                 mode_jeu=partie.mode_jeu
#             )

#         # Passer au prochain participant
#         participant_index = (participant_index + 1) % participants.count()
#         request.session['participant_index'] = participant_index

#         # Si tous les participants ont voté
#         if participant_index == 0:
#             # Récupérer tous les votes pour la fonctionnalité en cours
#             votes = Vote.objects.filter(fonctionnalite=fonctionnalite_en_cours, partie=partie)
#             votes_valides = [v.vote for v in votes if isinstance(v.vote, int)]  # Exclure "interro"
#             votes_normalises = [int(v.vote) for v in votes if isinstance(v.vote, (int, str)) and str(v.vote).isdigit()]
#             votes_unanimes = votes.values_list('vote', flat=True).distinct()
#             # Gérer la carte "café"
#             if len(votes) == participants.count() and all(v.vote == "cafe" for v in votes):
#                 fichier_etat = partie.sauvegarder_etat_partie()
#                 messages.warning(request, f"La partie a été mise en pause. État sauvegardé dans {fichier_etat}.")
#                 return redirect('lister_parties')

#             # Mode Strict : Tous les votes doivent être identiques
#             if partie.mode_jeu == "strict":
#                 if len(votes_unanimes) == 1:
#                     fonctionnalite_en_cours.valide = True
#                     fonctionnalite_en_cours.save()
#                 else:
#                     votes.delete()
#                     messages.warning(request, "Les votes ne sont pas unanimes. Recommencez pour cette fonctionnalité.")

#             # Mode Moyenne : Gestion des tours
#             elif partie.mode_jeu == "moyenne":
#                 if not request.session.get('premier_tour_fini', False):
#                     # Premier tour : Unanimité obligatoire
#                     if len(votes_unanimes) == 1:
#                         fonctionnalite_en_cours.valide = True
#                         fonctionnalite_en_cours.save()
#                         request.session['premier_tour_fini'] = True
#                     else:
#                         votes.delete()
#                         messages.warning(request, "Les votes ne sont pas unanimes. Recommencez pour cette fonctionnalité.")
#                         # Premier tour unanime
      
#                 else:
#                     # Deuxième tour et suivants : Calcul de la moyenne
#                     if len(votes_unanimes) == 1:
#                         fonctionnalite_en_cours.valide = True
#                         fonctionnalite_en_cours.save()
#                     else:
#                         moyenne = partie.calculer_moyenne_votes(votes)
#                         messages.info(request, f"Temps de discussion : Moyenne des votes = {moyenne}")
#                         time.sleep(10)  # Pause de 10 secondes
#                         fonctionnalite_en_cours.valide = True
#                         fonctionnalite_en_cours.save()
#             request.session['participant_index'] = 0
#         return redirect('demarrer_vote', partie_id=partie.id)

#     cartes = [0, 1, 2, 3, 5, 8, 13, 20, 40, 100, "cafe", "interro"]
#     context = {
#         'partie': partie,
#         'fonctionnalite_en_cours': fonctionnalite_en_cours,
#         'participant_en_cours': participant_en_cours,
#         'cartes': cartes,
#         # 'discussion_activee': request.session.pop('discussion_activee', False),
#         # 'moyenne_vote': request.session.pop('moyenne_vote', None),  # Récupérer la moyenne pour affichage
#     }
#     return render(request, 'parties/vote.html', context)
