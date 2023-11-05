from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User

# Model for individual ingredients
class Ingredient(models.Model):
    name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(
        "Recipe", on_delete=models.CASCADE, related_name="ingredients_used"
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="recipes_used",
    )

    def __str__(self):
        return f"{self.ingredient} - {self.recipe}"

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
    pic = models.ImageField(upload_to='recipes', default='no_picture.png')
    author = models.ForeignKey(User, on_delete=models.CASCADE, default=1)
    likes = models.ManyToManyField(User, related_name="recipe_like", blank=True)

    def number_of_likes(self):
        return self.likes.count()

    def calculate_difficulty(self):
        num_ingredients = self.ingredients.count()
        if self.cooking_time < 10 and num_ingredients < 4:
            return 'Easy'
        elif self.cooking_time < 10 and num_ingredients >= 4:
            return 'Medium'
        elif self.cooking_time > 10 and num_ingredients < 4:
            return 'Intermediate'
        else:
            return "Hard"

    def __str__(self):
        return self.title

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    date_modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.user.username

def create_profile(sender, instance, created, **kwargs):
    if created:
        user_profile = Profile(user=instance)
        user_profile.save()

post_save.connect(create_profile, sender=User)

class RecipeComment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    content = models.TextField()
    date_posted = models.DateTimeField(auto_now_add=True)
    parent_comment = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='replies'
    )
    depth = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"Comment by {self.user.username}"
    
    class Meta:
        ordering = ['-date_posted']