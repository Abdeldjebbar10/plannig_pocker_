from django import forms
from .models import Partie, Vote, Fonctionnalite, Participant
import json

# class PartieForm(forms.ModelForm):
#     administrateur = forms.ModelChoiceField(queryset=Participant.objects.filter(est_admin=True), required=True)  # Sélectionner un administrateur parmi les participants qui sont administrateurs

#     participants = forms.ModelMultipleChoiceField(queryset=Participant.objects.all(), widget=forms.CheckboxSelectMultiple)  # Sélectionner plusieurs participants

#     class Meta:
#         model = Partie
#         fields = ['nom','mode_jeu', 'administrateur', 'participants']  # Le formulaire va contenir le nom, l'administrateur et les participants

#     def clean_nom(self):
#         nom = self.cleaned_data.get('nom')
#         if Partie.objects.filter(nom=nom).exists():
#             raise forms.ValidationError("Le nom de la partie doit être unique.")
#         return nom
class PartieForm(forms.ModelForm):
    administrateur = forms.ModelChoiceField(queryset=Participant.objects.filter(est_admin=True), required=True)
    participants = forms.ModelMultipleChoiceField(queryset=Participant.objects.all(), widget=forms.CheckboxSelectMultiple)
    fonctionnalites_json = forms.FileField(required=False)  # Champ pour importer le fichier JSON

    class Meta:
        model = Partie
        fields = ['nom', 'mode_jeu', 'administrateur', 'participants', 'fonctionnalites_json']
        widgets = {
            'nom': forms.TextInput(attrs={'class': 'form-control'}),
            'mode_jeu': forms.Select(attrs={'class': 'form-control'}),
        }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'administrateur' in self.data:
            admin_id = self.data.get('administrateur')
            if admin_id:
                self.fields['participants'].queryset = self.fields['participants'].queryset.exclude(id=admin_id)
    def clean_fonctionnalites_json(self):
        fichier = self.cleaned_data.get('fonctionnalites_json')
        if fichier:
            try:
                json.load(fichier)  # Vérifie que le fichier est un JSON valide
            except json.JSONDecodeError:
                raise forms.ValidationError("Le fichier JSON est invalide.")
        return fichier

    def save(self, commit=True):
        instance = super().save(commit=False)
        if self.cleaned_data.get('fonctionnalites_json'):
            fichier_json = self.cleaned_data['fonctionnalites_json']
            self.importer_fonctionnalites(fichier_json, instance)
        if commit:
            instance.save()
        return instance

    def importer_fonctionnalites(self, fichier_json, partie):
        data = json.load(fichier_json)
        for item in data:
            fonctionnalite = Fonctionnalite.objects.create(
                name=item['name'],
                description=item['description'],
            )
            partie.fonctionnalites.add(fonctionnalite)

# Formulaire pour voter sur une fonctionnalité
class VoteForm(forms.Form):
    fonctionnalite = forms.ModelChoiceField(queryset=Fonctionnalite.objects.all())
    vote = forms.IntegerField(min_value=1, max_value=13)  # Exemple de vote avec des valeurs de 1 à 13


class ParticipantForm(forms.ModelForm):
    class Meta:
        model = Participant
        fields = ['pseudo', 'est_admin']  # On inclut le pseudo et l'admin dans le formulaire
        widgets = {
            'est_admin': forms.CheckboxInput()  # Utiliser un widget checkbox pour le champ booléen
        }
    def clean_pseudo(self):
        pseudo = self.cleaned_data.get('pseudo')
        if Participant.objects.filter(pseudo=pseudo).exists():
            raise forms.ValidationError("Ce pseudo est déjà pris. Veuillez en choisir un autre.")
        return pseudo