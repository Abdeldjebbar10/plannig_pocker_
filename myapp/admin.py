from django.contrib import admin

# Register your models here.

# myapp/admin.py
from django.contrib import admin
from django.apps import apps

# Get all models from the app
app = apps.get_app_config('myapp')

# Register each model with the admin site
for model_name, model in app.models.items():
    admin.site.register(model)