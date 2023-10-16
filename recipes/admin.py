from django.contrib import admin
from .models import Recipe, Ingredient
from django.contrib.auth.models import Group, User

@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('title', 'cooking_time', 'calculate_difficulty')  

@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', ) 

admin.site.unregister(Group)

#expand user model
class UserAdmin(admin.ModelAdmin):
    model = User
    fields = ["username"]

#unregister user
admin.site.unregister(User)

#register user and profile
admin.site.register(User, UserAdmin)
#admin.site.register(Profile)