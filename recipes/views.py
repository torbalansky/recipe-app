from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView
from .models import Recipe, Profile, RecipeIngredient, Ingredient
from django.contrib import messages
from django.http import Http404
from .forms import SignUpForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .forms import RecipeForm

@login_required
def create_recipe(request, user_id):
    form = RecipeForm(request.POST or None, request.FILES or None)
    
    if request.method == 'POST':
        recipe_ingredients_str = request.POST.get('recipe_ingredients', '') 
        
        if recipe_ingredients_str:
            recipe_ingredients_list = [ingredient.strip() for ingredient in recipe_ingredients_str.split(",")]
            
        if form.is_valid():
            recipe = form.save(commit=False)
            
            recipe_ingredients_count = 0
            profile = Profile.objects.get(user_id=user_id)
            recipe.author = profile.user
            recipe.save()

            for ingredient_name in recipe_ingredients_list:
                ingredient, created = Ingredient.objects.get_or_create(name=ingredient_name)

                if created:
                    recipe_ingredients_count += 1
                recipe.ingredients.add(ingredient)  

            recipe.difficulty = recipe.calculate_difficulty()
            recipe.save()

            messages.success(request, "Recipe added successfully.")
            return redirect('recipes:profile', pk=user_id)
        else:
            messages.error(request, "Form validation failed. Please check the entered data.")
    
    return form

def profile(request, pk):
    if request.user.is_authenticated:
        try:
            profile = Profile.objects.get(user_id=pk)
            user = profile.user
            user_recipes = Recipe.objects.filter(author=user)
            
            form = create_recipe(request, pk)  

            context = {
                "profile": profile,
                "user_recipes": user_recipes,
                "form": form,
            }

            return render(request, "recipes/profile.html", context)
        except Profile.DoesNotExist:
            raise Http404("Profile does not exist")
    else:
        messages.error(request, "You must be logged in to access this!")
        return redirect('recipes:login')

def login_user(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)  
            messages.success(request, "You are logged in.")
            return redirect('recipes:home')
        else:
            messages.error(request, "An error occurred. Please try again.")
            return redirect('recipes:user_login')
    else:
        return render(request, "recipes/login.html", {})
    
def logout_user(request):
    logout(request)
    messages.success(request, "Logged out successfully.")
    return redirect('recipes:home')


def home(request):
   return render(request, 'recipes/home.html', {})

class RecipesListView(ListView):
    model = Recipe
    template_name = "recipes/recipes_list.html"
    context_object_name = "recipes"

class RecipesDetailView(DetailView):
    model = Recipe
    template_name = "recipes/recipes_details.html"
    context_object_name = "recipe"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Fetch the related ingredients for the specific recipe
        ingredients = RecipeIngredient.objects.filter(recipe=self.object).values_list('ingredient__name', flat=True)
        context['ingredients'] = ingredients

        return context
    
def register_user(request):
    form = SignUpForm()  
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data['username']
            password = form.cleaned_data['password1']

            # Login user
            user = authenticate(username=username, password=password)
            login(request, user)
            messages.success(request, ("You have successfully registered!"))
            return redirect('recipes:home')
    return render(request, "recipes/register.html", {'form': form})
