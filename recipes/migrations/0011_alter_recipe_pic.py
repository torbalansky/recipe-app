# Generated by Django 4.2.6 on 2023-11-09 08:03

import cloudinary.models
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0010_alter_recipecomment_options'),
    ]

    operations = [
        migrations.AlterField(
            model_name='recipe',
            name='pic',
            field=cloudinary.models.CloudinaryField(blank=True, max_length=255, null=True, verbose_name='recipe_pics'),
        ),
    ]
