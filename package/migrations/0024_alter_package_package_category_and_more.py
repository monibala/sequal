# Generated by Django 4.0 on 2022-01-26 13:14

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('package', '0023_alter_category_name_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='package',
            name='package_category',
            field=models.ManyToManyField(blank=True, null=True, related_name='package', to='package.Subcategory'),
        ),
        migrations.AlterField(
            model_name='subcategory',
            name='category',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='subcategory', to='package.category'),
        ),
    ]