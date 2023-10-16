from django.urls import path
from . import views

app_name = 'recipes'

urlpatterns = [
    path('', views.home, name='home'),
    path('recipes_list/', views.RecipesListView.as_view(), name='recipes_list'),
    path('recipes_details/<int:pk>/', views.RecipesDetailView.as_view(), name='recipes_details'),
]