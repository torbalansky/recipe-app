# Generated by Django 4.2.6 on 2023-10-15 09:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0002_remove_ingredient_description'),
    ]

    operations = [
        migrations.AddField(
            model_name='recipe',
            name='pic',
            field=models.ImageField(default='no_picture.png', upload_to='recipes'),
        ),
    ]
