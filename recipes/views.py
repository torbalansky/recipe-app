from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView
from .models import Recipe, Profile, RecipeIngredient, Ingredient, RecipeComment
from django.contrib import messages
from django.http import Http404
from .forms import SignUpForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .forms import RecipeForm, UserUpdateForm, RecipeSearchForm, CommentForm, ContactForm, ReplyForm
from django.contrib.auth.models import User
import pandas as pd
from django.db.models import Q
import matplotlib.pyplot as plt
import base64
from io import BytesIO
from functools import reduce
from operator import and_
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa
from django.core.mail import send_mail
from django.template.loader import render_to_string

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


@login_required
def update_recipe(request, pk):
    recipe = get_object_or_404(Recipe, id=pk)
   
    if request.user == recipe.author:
        form = RecipeForm(request.POST or None, request.FILES or None, instance=recipe)
        
        if request.method == 'POST':
            if form.is_valid():
                updated_recipe = form.save(commit=False)
                updated_recipe.author = recipe.author  
                updated_recipe.save()
                updated_recipe.ingredients.clear()
                recipe_ingredients_str = request.POST.get('recipe_ingredients', '')
                recipe_ingredients_list = [ingredient.strip() for ingredient in recipe_ingredients_str.split(",")]

                for ingredient_name in recipe_ingredients_list:
                    ingredient, created = Ingredient.objects.get_or_create(name=ingredient_name)
                    updated_recipe.ingredients.add(ingredient)
                updated_recipe.difficulty = updated_recipe.calculate_difficulty()
                updated_recipe.save()

                messages.success(request, "Recipe updated successfully.")
                return redirect('recipes:profile', pk=recipe.author.id)
            else:
                messages.error(request, "Form validation failed. Please check the entered data.")
 
        current_ingredients = ', '.join(recipe.ingredients.values_list('name', flat=True))

        return render(request, "recipes/update_recipe.html", {'form': form, 'recipe': recipe, 'recipe_ingredients': current_ingredients})
    else:
        messages.error(request, "This recipe is not yours.")
        return redirect('recipes:profile')

def delete_recipe(request, pk):
    if request.user.is_authenticated:
        recipe = get_object_or_404(Recipe, id=pk)
        
        if request.user.username == recipe.author.username:
            recipe.delete()
            messages.success(request, "The recipe has been deleted.")
            return redirect('recipes:profile', pk=request.user.id)
        else:
            messages.error(request, "You don't have permission to delete this recipe.")
    else:
        messages.error(request, "You must be logged in to delete a recipe.")
    
    return redirect('recipes:home')

def home(request):
   return render(request, 'recipes/home.html', {})

class RecipesListView(ListView):
    model = Recipe
    template_name = "recipes/recipes_list.html"
    context_object_name = "recipes"
    
    def get_queryset(self):
        queryset = super().get_queryset()
        recipe_name = self.request.GET.get("Recipe_Name")
        ingredients = self.request.GET.getlist("Ingredients")
        combined_query = Q()

        if recipe_name:
            combined_query &= Q(title__icontains=recipe_name)

        if ingredients:
            for ingredient in ingredients:
                combined_query &= Q(ingredients__name__icontains=ingredient)
        queryset = queryset.filter(combined_query).distinct()

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form"] = RecipeSearchForm(self.request.GET)

        if not context["recipes"]:
            error_message = "There are no recipes with that combination of ingredients."
            messages.error(self.request, error_message)
            context["error_message"] = error_message

        if "chart_type" in self.request.GET:
            chart_type = self.request.GET.get("chart_type")
            queryset = self.get_queryset()
            data = pd.DataFrame.from_records(queryset.values('title', 'cooking_time'))

            chart_data = {"title": data.get("title", []), "cooking_time": data.get("cooking_time", [])}

            if chart_type == "#1":
                chart_data["labels"] = chart_data.get("title")
            elif chart_type == "#2":
                chart_data["labels"] = chart_data.get("title")
            else:
                chart_data["labels"] = None
            chart_image = render_chart(self.request, chart_type, chart_data)
            context["chart_image"] = chart_image

        return context
    
def render_chart(request, chart_type, data, **kwargs):
    plt.switch_backend("AGG")
    fig = plt.figure(figsize=(12, 8), dpi=100)
    ax = fig.add_subplot(111)

    if chart_type == "#1":
        plt.title("Cooking Time by Recipe", fontsize=20)
        plt.bar(data["title"], data["cooking_time"])
        plt.xlabel("Recipes", fontsize=16)
        plt.ylabel("Cooking Time (min)", fontsize=16)
    elif chart_type == "#2":
        plt.title("Recipes Cooking Time Comparison", fontsize=20)
        labels = kwargs.get("labels")
        plt.pie(data["cooking_time"], labels=None, autopct="%1.1f%%")
        plt.legend(
            data["title"],
            loc="upper right",
            bbox_to_anchor=(1.0, 1.0),
            fontsize=12,
        )
    elif chart_type == "#3":
        plt.title("Cooking Time by Recipe", fontsize=20)
        x_values = data["title"].to_numpy()  
        y_values = data["cooking_time"].to_numpy()  
        plt.plot(x_values, y_values)
        plt.xlabel("Recipes", fontsize=16)
        plt.ylabel("Cooking Time (min)", fontsize=16)
    else:
        print("Unknown chart type.")

    plt.tight_layout(pad=3.0)

    buffer = BytesIO()
    plt.savefig(buffer, format="png")
    buffer.seek(0)
    chart_image = base64.b64encode(buffer.read()).decode("utf-8")

    return chart_image

class RecipesDetailView(DetailView):
    model = Recipe
    template_name = "recipes/recipes_details.html"
    context_object_name = "recipe"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        ingredients = RecipeIngredient.objects.filter(recipe=self.object).values_list('ingredient__name', flat=True)
        context['ingredients'] = ingredients
        
        all_comments = RecipeComment.objects.filter(recipe=self.object)
        top_level_comments = [comment for comment in all_comments if comment.parent_comment is None]
        
        for comment in top_level_comments:
            comment.replies.all().order_by('-date_posted')

        context['top_level_comments'] = top_level_comments
        context['comment_form'] = CommentForm()
        context['reply_form'] = ReplyForm()

        return context
    
def register_user(request):
    form = SignUpForm()  
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data['username']
            password = form.cleaned_data['password1']
            user = authenticate(username=username, password=password)
            login(request, user)
            messages.success(request, ("You have successfully registered!"))
            return redirect('recipes:home')
    return render(request, "recipes/register.html", {'form': form})

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
            messages.error(request, "Ups, something went wrong. Please try again.")
            return render(request, "recipes/login.html", {})
    else:
        return render(request, "recipes/login.html", {})
    
def logout_user(request):
    logout(request)
    messages.success(request, "Logged out successfully.")
    return redirect('recipes:home')

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

@login_required
def update_user(request, pk):
    if request.user.is_authenticated:
        current_user = User.objects.get(id=request.user.id)
        if request.method == "POST":
            user_form = UserUpdateForm(request.POST, instance=current_user)

            if user_form.is_valid():
                user_form.save()
                login(request, current_user)
                messages.success(request, "Your profile has been updated.")
                return redirect('recipes:home')
            else:
                messages.error(request, "There was an error updating your profile. Please try again.")
        else:
            user_form = UserUpdateForm(instance=current_user)
            return render(request, "recipes/update_user.html", {'user_form': user_form })
    else:
        messages.success(request, "You have to be logged in.")
        return redirect('recipes:home')

def delete_user(request, pk):
    if request.user.is_authenticated:
        user = get_object_or_404(User, id=pk)
        
        if request.user == user:
            user.delete()
            messages.success(request, "Your account has been successfully deleted.")
            return redirect('recipes:home')
        else:
            messages.error(request, "Something went wrong. Please try again.")
    else:
        messages.error(request, "You must be logged in to perform this task.")
    
    return redirect('recipes:home')

def search_recipes(request):
    if request.method == 'POST':
        recipe_name = request.POST.get('Recipe_Name')
        ingredients = request.POST.getlist('Ingredients')
        chart_type = request.POST.get('chart_type')
        queryset = Recipe.objects.all()

        if recipe_name:
            queryset = queryset.filter(title__icontains=recipe_name)

        if ingredients:
            ingredient_filters = [Q(ingredients__name__icontains=ingredient) for ingredient in ingredients]
            combined_filter = reduce(and_, ingredient_filters)
            queryset = queryset.filter(combined_filter).distinct()

        recipes = queryset

        chart_image = None

        if chart_type and recipes:
            chart_data = {
                'labels': [recipe.title for recipe in recipes],
                'data': [recipe.cooking_time for recipe in recipes],
            }
            chart_image = render_chart(request, chart_type, chart_data)

        if not recipes:
            messages.error(request, "There are no recipes with that combination of ingredients.")
            chart_image is None

        return render(request, 'recipes/recipes_list.html', {
            'recipes': recipes,
            'chart_image': chart_image,
            'chart_type': chart_type,
        })

    return render(request, 'recipes/recipes_list.html')

@login_required
def export_recipe_as_pdf(request, pk):
    recipe = get_object_or_404(Recipe, id=pk)

    template_path = 'recipes/pdf_template.html'

    context = {
        'recipe': recipe,
    }

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{recipe.title}.pdf"'

    template = get_template(template_path)
    html = template.render(context)
    pisa_status = pisa.CreatePDF(html, dest=response)

    if pisa_status.err:
        return HttpResponse('We had some errors <pre>' + html + '</pre>')

    return response

def recipe_like(request, pk):
    if request.user.is_authenticated:
        recipe = get_object_or_404(Recipe, id=pk)
        if recipe.likes.filter(id=request.user.id):
            recipe.likes.remove(request.user)
        else:
            recipe.likes.add(request.user)
        return redirect(request.META.get("HTTP_REFERER"))

    else: 
        messages.success(request, ("You must be logged in to perform this task."))
        return redirect('recipes:home')

def add_comment(request, recipe_id):
    if request.user.is_authenticated:
        recipe = get_object_or_404(Recipe, pk=recipe_id)

        if request.method == 'POST':
            form = CommentForm(request.POST)
            if form.is_valid():
                comment = form.save(commit=False)
                comment.user = request.user
                comment.recipe = recipe
                comment.save()
                return redirect('recipes:recipes_details', pk=recipe_id)
        else:
            form = CommentForm()

        return render(request, 'recipes/recipes_details.html', {'recipe': recipe, 'form': form})
    else:
        return HttpResponse("You must be logged in to add a comment.")

def add_reply(request, recipe_id, parent_comment_id):
    if request.user.is_authenticated:
        recipe = get_object_or_404(Recipe, pk=recipe_id)
        parent_comment = get_object_or_404(RecipeComment, pk=parent_comment_id)

        if request.method == 'POST':
            reply_form = ReplyForm(request.POST)
            if reply_form.is_valid():
                reply = reply_form.save(commit=False)
                reply.user = request.user
                reply.recipe = recipe
                reply.parent_comment = parent_comment
                reply.content = f"{reply_form.cleaned_data['content']}"
                reply.save()
                return redirect('recipes:recipes_details', pk=recipe_id)
        else:
            reply_form = ReplyForm(initial={'parent_comment_username': parent_comment.user.username})

        comment_form = CommentForm()
        return render(request, 'recipes/recipes_details.html', {'recipe': recipe, 'comment_form': comment_form, 'reply_form': reply_form, 'parent_comment': parent_comment})
    else:
        return HttpResponse("You must be logged in to add a reply.")

from django.shortcuts import redirect, get_object_or_404

from django.http import HttpResponseForbidden

def delete_comment(request, comment_id):
    comment = get_object_or_404(RecipeComment, pk=comment_id)
    
    if request.user == comment.user:
        if comment.parent_comment is None:
            if comment.replies.exists():
                messages.error(request, "Cannot delete a comment with replies.")
            else:
                comment.delete()
        else:
            comment.delete()
        return redirect('recipes:recipes_details', pk=comment.recipe.id)
    else:
        return HttpResponseForbidden("You are not authorized to delete this comment.")

def delete_reply(request, reply_id):
    reply = get_object_or_404(RecipeComment, pk=reply_id)
    
    if request.user == reply.user:
        reply.delete()
        return redirect('recipes:recipes_details', pk=reply.recipe.id)
    else:
        return HttpResponseForbidden("You are not authorized to delete this reply.")

def about(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)

        if form.is_valid():
            name = form.cleaned_data['name']
            email = form.cleaned_data['email']
            content = form.cleaned_data['content']

            html = render_to_string('recipes/contact_form.html', {
                'name': name,
                'email': email,
                'content': content
            })

            send_mail('The contact form subject', 'This is the message', 'torbalansky@gmail.com', ['torbalansky@gmail.com'], html_message=html)
            messages.success(request, "Message sent. I will get back to you as soon as possible.")
            return redirect('recipes:about')
    else:
        form = ContactForm()

    return render(request, 'recipes/about.html', {
        'form': form
    })