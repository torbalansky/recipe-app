from django.urls import path
from . import views
from django.contrib.auth.decorators import login_required

app_name = 'recipes'

urlpatterns = [
    path('', views.home, name='home'),
    path('recipes_list/', views.RecipesListView.as_view(), name='recipes_list'),
    path('recipes_details/<int:pk>/', views.RecipesDetailView.as_view(), name='recipes_details'),
    path('profile/<int:pk>/', views.profile, name='profile'),
    path('login/', views.login_user, name='login'),
    path('logout', views.logout_user, name='logout'),
    path('register/', views.register_user, name='register'),
     path('update_recipe/<int:pk>/', views.update_recipe, name='update_recipe'),
    path('delete_recipe/<int:pk>/', views.delete_recipe, name='delete_recipe'),
]