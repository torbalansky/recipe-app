from django.test import TestCase
from .models import Ingredient, Recipe

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
        # Update the cooking time to be less than 10
        self.recipe.cooking_time = 5  

        # Add more ingredients to reach four
        self.recipe.ingredients.add(
            Ingredient.objects.create(name="Ingredient3"),
            Ingredient.objects.create(name="Ingredient4"),
        )

        self.recipe.save()
        
        # Print some debug information
        calculated_difficulty = self.recipe.calculate_difficulty()
        print(f"Calculated Difficulty: {calculated_difficulty}")
        
        # Test for the expected difficulty level (Medium)
        self.assertEqual(calculated_difficulty, "Medium")




    def test_create_or_update_ingredients_signal(self):
        # Ensure ingredients are created or updated when a recipe is saved
        ingredient3 = Ingredient.objects.create(name="Sugar")
        self.recipe.ingredients.add(ingredient3)
        # Update the recipe to trigger the signal
        self.recipe.save()
        # Check if ingredients are saved
        ingredient1_updated = Ingredient.objects.get(name="Salt")
        self.assertEqual(ingredient1_updated.updated_at.date(), self.recipe.updated_at.date())

class IngredientModelTest(TestCase):
    def test_ingredient_str(self):
        ingredient = Ingredient.objects.create(name="Tomato")
        self.assertEqual(str(ingredient), "Tomato")
