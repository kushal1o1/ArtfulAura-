
from django.contrib import admin
from django.urls import path
from .views import(
    HomeView,ItemDetailView,
)

app_name='core'

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', HomeView.as_view(), name='home'),
    path('product/<slug>/', ItemDetailView.as_view(), name='product'),
    
    
   
]
