# Generated by Django 4.2.6 on 2023-11-08 16:33

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0009_recipecomment_depth_recipecomment_parent_comment'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='recipecomment',
            options={'ordering': ['-date_posted']},
        ),
    ]