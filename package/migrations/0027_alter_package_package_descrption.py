# Generated by Django 4.0 on 2022-01-27 09:51

import ckeditor_uploader.fields
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('package', '0026_alter_subcategory_description'),
    ]

    operations = [
        migrations.AlterField(
            model_name='package',
            name='Package_descrption',
            field=ckeditor_uploader.fields.RichTextUploadingField(),
        ),
    ]