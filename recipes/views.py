from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView
from .models import Recipe, Profile, Ingredient
from django.contrib import messages
from django.http import Http404
from .forms import SignUpForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from .forms import RecipeForm
from django.contrib.auth.models import User

def create_recipe(request, pk):
    user = get_object_or_404(User, pk=pk)

    if request.method == 'POST':
        if request.user.is_authenticated:
            form = RecipeForm(request.POST, request.FILES)
            if form.is_valid():
                recipe = form.save(commit=False)
                recipe.author = user
                ingredient_input = form.cleaned_data.get('ingredients')

                if ingredient_input:
                    ingredient_names = [name.strip() for name in ingredient_input.split(',') if name.strip()]
                    selected_ingredients = []

                    for ingredient_name in ingredient_names:
                        ingredient, created = Ingredient.objects.get_or_create(name=ingredient_name)
                        selected_ingredients.append(ingredient)

                    recipe.save()
                    recipe.ingredients.set(selected_ingredients)  
                    return redirect('recipes:recipe_detail', pk=recipe.pk)
            else:
                return render(request, 'recipes/create_recipe.html', {'form': form})
        else:
            return redirect('login')
    else:
        form = RecipeForm()

    return render(request, 'recipes/create_recipe.html', {'form': form})


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

    @method_decorator(login_required(login_url='/login/'))
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)
    
    def get_object(self):
        # Fetch the Recipe object by primary key
        return get_object_or_404(Recipe, pk=self.kwargs.get('pk'))
    
def profile(request, pk):
    if request.user.is_authenticated:
        try:
            profile = Profile.objects.get(user_id=pk)
            user = profile.user

            if request.method == 'POST':
                # Handle recipe creation form submission
                form = RecipeForm(request.POST)
                if form.is_valid():
                    recipe = form.save(commit=False)
                    recipe.author = user
                    recipe.save()
                    messages.success(request, "Recipe created successfully.")
                    return redirect('recipes:profile', pk=pk)  # Redirect to the same profile page

            else:
                form = RecipeForm()

            # Fetch the recipes created by this user
            user_recipes = Recipe.objects.filter(author=user)

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
