# Generated by Django 4.0 on 2022-01-26 10:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('package', '0021_subcategory_slug'),
    ]

    operations = [
        migrations.AddField(
            model_name='category',
            name='slug',
            field=models.SlugField(blank=True),
        ),
    ]
