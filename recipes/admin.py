from django.contrib import admin
from .models import Recipe, Ingredient

@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('title', 'cooking_time', 'calculate_difficulty')  

@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', ) 
