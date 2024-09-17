from django.shortcuts import render
from django.views.generic import ListView
from .models import Item
# Create your views here.
class HomeView(ListView):
    model = Item
    paginate_by = 8
    template_name = "home.html"