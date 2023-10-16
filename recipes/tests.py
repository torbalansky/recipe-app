from django.test import TestCase
from .models import Ingredient, Recipe
from django.urls import reverse

class RecipeModelTest(TestCase):
    def setUp(self):
        self.ingredient1 = Ingredient.objects.create(name="Salt")
        self.ingredient2 = Ingredient.objects.create(name="Pepper")
        self.recipe = Recipe.objects.create(
            title="Sample Recipe",
            description="A test recipe",
            cooking_time=30,
            instructions="Test instructions",
            difficulty="Hard",
        )
        self.recipe.ingredients.add(self.ingredient1, self.ingredient2)

    def test_recipe_has_ingredients(self):
        self.assertEqual(self.recipe.ingredients.count(), 2)

    def test_calculate_difficulty(self):
        self.recipe.cooking_time = 5  

        self.recipe.ingredients.add(
            Ingredient.objects.create(name="Ingredient3"),
            Ingredient.objects.create(name="Ingredient4"),
        )

        self.recipe.save()
  
        calculated_difficulty = self.recipe.calculate_difficulty()
        print(f"Calculated Difficulty: {calculated_difficulty}")

        self.assertEqual(calculated_difficulty, "Easy")
    
    def test_calculate_difficulty(self):
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

    def test_calculate_difficulty(self):
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
        recipe1 = Recipe.objects.create(title="Recipe 1", description="Description 1", cooking_time=30)
        recipe2 = Recipe.objects.create(title="Recipe 2", description="Description 2", cooking_time=40)
        url = reverse('recipes:recipes_list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        recipes_in_context = list(response.context['recipes'])
        self.assertIn(recipe1, recipes_in_context)
        self.assertIn(recipe2, recipes_in_context)

class RecipesDetailViewTest(TestCase):
    def test_recipe_detail_view(self):
        recipe = Recipe.objects.create(title="Recipe", description="Description", cooking_time=25)
        url = reverse('recipes:recipes_details', args=[recipe.pk])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['recipe'], recipe)
