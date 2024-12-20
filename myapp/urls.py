from django.urls import path
from . import views

urlpatterns = [
    path('partie/<int:partie_id>/reprendre/', views.reprendre_partie, name='reprendre_partie'),
    
    path('partie/<int:id>/', views.detail_partie, name='detail_partie'),

    path('', views.menu_principal, name='menu_principal'),  # Menu principal
    path('creer/', views.creer_partie, name='creer_partie'),
    path('parties/', views.liste_parties, name='lister_parties'), 
    path('reprendre/', views.reprendre_partie, name='reprendre_partie'),
    
    path('creer_participant/', views.creer_participant, name='creer_participant'),  # Créer un participant
    path('lister_participants/', views.liste_participants, name='lister_participants'),  # Lister les participants

    path('partie/<int:partie_id>/lancer/', views.lancer_partie, name='lancer_partie'),
    path('partie/<int:partie_id>/reprendre/', views.reprendre_partie, name='reprendre_partie'),

    path('partie/<int:partie_id>/vote/', views.demarrer_vote, name='demarrer_vote'),


]
