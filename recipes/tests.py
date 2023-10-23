from django.test import TestCase
from .models import Ingredient, Recipe
from django.urls import reverse
from django.contrib.auth.models import User
from .forms import RecipeSearchForm 

class RecipeModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="testpassword")
        self.ingredient1 = Ingredient.objects.create(name="Salt")
        self.ingredient2 = Ingredient.objects.create(name="Pepper")
        self.recipe = Recipe.objects.create(
            title="Sample Recipe",
            description="A test recipe",
            cooking_time=30,
            instructions="Test instructions",
            difficulty="Hard",
            author=self.user,  
        )
        self.recipe.ingredients.add(self.ingredient1, self.ingredient2)

    def test_recipe_has_ingredients(self):
        self.assertEqual(self.recipe.ingredients.count(), 2)

    def test_calculate_difficulty_hard(self):
        self.recipe.cooking_time = 30
        self.recipe.ingredients.add(
            Ingredient.objects.create(name="Ingredient3"),
            Ingredient.objects.create(name="Ingredient4"),
            Ingredient.objects.create(name="Ingredient5"),
            Ingredient.objects.create(name="Ingredient6"),
        )
        self.recipe.save()
        calculated_difficulty = self.recipe.calculate_difficulty()
        print(f"Calculated Difficulty: {calculated_difficulty}")
        self.assertEqual(calculated_difficulty, "Hard")

    def test_calculate_difficulty_medium(self):
        self.recipe.cooking_time = 9
        self.recipe.ingredients.add(
            Ingredient.objects.create(name="Ingredient3"),
            Ingredient.objects.create(name="Ingredient4"),
            Ingredient.objects.create(name="Ingredient5"),
            Ingredient.objects.create(name="Ingredient6"),
            Ingredient.objects.create(name="Ingredient7"),
        )
        self.recipe.save()
        calculated_difficulty = self.recipe.calculate_difficulty()
        print(f"Calculated Difficulty: {calculated_difficulty}")
        self.assertEqual(calculated_difficulty, "Medium")

    def test_create_or_update_ingredients_signal(self):
        ingredient3 = Ingredient.objects.create(name="Sugar")
        self.recipe.ingredients.add(ingredient3)
        self.recipe.save()
        ingredient1_updated = Ingredient.objects.get(name="Salt")
        self.assertEqual(ingredient1_updated.updated_at.date(), self.recipe.updated_at.date())

class IngredientModelTest(TestCase):
    def test_ingredient_str(self):
        ingredient = Ingredient.objects.create(name="Tomato")
        self.assertEqual(str(ingredient), "Tomato")

class RecipesListViewTest(TestCase):
    def test_recipes_list_view(self):
        user = User.objects.create_user(username="testuser", password="testpassword")
        recipe1 = Recipe.objects.create(title="Recipe 1", description="Description 1", cooking_time=30, author=user)
        recipe2 = Recipe.objects.create(title="Recipe 2", description="Description 2", cooking_time=40, author=user)
        url = reverse('recipes:recipes_list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        recipes_in_context = list(response.context['recipes'])
        self.assertIn(recipe1, recipes_in_context)
        self.assertIn(recipe2, recipes_in_context)

class RecipesDetailViewTest(TestCase):
    def test_recipe_detail_view(self):
        user = User.objects.create_user(username="testuser", password="testpassword")
        recipe = Recipe.objects.create(title="Recipe", description="Description", cooking_time=25, author=user)
        url = reverse('recipes:recipes_details', args=[recipe.pk])  # Correct the URL name
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['recipe'], recipe)

class RecipeSearchFormTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        ingredient1 = Ingredient.objects.create(name="Ingredient 1")
        ingredient2 = Ingredient.objects.create(name="Ingredient 2")
        recipe1 = Recipe.objects.create(title="Recipe 1", cooking_time=30)
        recipe2 = Recipe.objects.create(title="Recipe 2", cooking_time=60)
        recipe1.ingredients.add(ingredient1)
        recipe2.ingredients.add(ingredient2)

        
        for i in range(3, 13):  
            recipe = Recipe.objects.create(
                title=f"Recipe {i}",
                cooking_time=(i + 1) * 10
            )
            recipe.ingredients.add(ingredient1)
            recipe.ingredients.add(ingredient2)

    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", password="testpassword"
        )
        self.client.login(username="testuser", password="testpassword")

    def test_form_fields(self):
        form_data = {
            "Recipe_Name": "Recipe 1",
            "Ingredients": [1],
            "chart_type": "#1",
        }
        form = RecipeSearchForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_form_missing_data(self):
        form_data = {} 
        form = RecipeSearchForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.errors["__all__"][0],
            "Please enter a recipe name or ingredient.",
        )

    def test_recipe_list_view(self):
        response = self.client.get(reverse('recipes:recipes_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "recipes/recipes_list.html")

    def test_chart_generation(self):
        form_data = {
            "Recipe_Name": "",
            "Ingredients": [1],
            "chart_type": "#1",
        }
        response = self.client.get(reverse('recipes:recipes_list'), form_data)
        self.assertEqual(response.status_code, 200)
        self.assertTrue("chart_image" in response.context)