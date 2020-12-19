from django.shortcuts import render

from django.views.generic import ListView

from einhorn_core.models import GameObject

class GameObjectList(ListView):
    model = GameObject
    template_name = 'einhorn_core/gameobject_list_view.html'

gameobject_list_view = GameObjectList.as_view()

# GameObject
    # List View
    # Detail View
    # Delete View

    # Create View
    # Update View
