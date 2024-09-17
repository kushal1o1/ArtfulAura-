
from django.contrib import admin
from django.urls import path
from .views import HomeView


app_name='core'

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', HomeView.as_view(), name='home'),
    
   
]
