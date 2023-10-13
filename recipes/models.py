from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

# Model for individual ingredients
class Ingredient(models.Model):
    name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

# Model for recipes, which have a many-to-many relationship with ingredients
class Recipe(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    ingredients = models.ManyToManyField(Ingredient)  # Many-to-many relationship
    cooking_time = models.IntegerField()
    instructions = models.TextField()
    DIFFICULTY_CHOICES = [
        ('Easy', 'Easy'),
        ('Medium', 'Medium'),
        ('Intermediate', 'Intermediate'),
        ('Hard', 'Hard'),
    ]
    difficulty = models.CharField(max_length=20, choices=DIFFICULTY_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def calculate_difficulty(self):
        ingredients = self.ingredients.all()  # Use .all() to get all related ingredients
        num_ingredients = ingredients.count()
        if self.cooking_time < 10 and num_ingredients < 4:
            return 'Easy'
        elif self.cooking_time < 10 and num_ingredients >= 4:
            return 'Medium'
        elif self.cooking_time >= 10 and num_ingredients < 4:
            return 'Intermediate'
        elif self.cooking_time >= 10 and num_ingredients >= 4:
            return 'Hard'
        return 'Unknown'  # Handle the case where difficulty is not determined

    def __str__(self):
        return self.title

# A signal receiver that is triggered after a Recipe is created or updated
@receiver(post_save, sender=Recipe)
def create_or_update_ingredients(sender, instance, created, **kwargs):
    # Iterate through the ingredients associated with the recipe
    for ingredient in instance.ingredients.all():
        ingredient_name = ingredient.name
        # Check if an ingredient with the same name already exists in the Ingredient model
        existing_ingredient = Ingredient.objects.filter(name=ingredient_name).first()
        if existing_ingredient:
            existing_ingredient.save()
        else:
            # Create a new ingredient in the Ingredient model if it doesn't exist
            Ingredient.objects.create(
                name=ingredient.name,
            )
