# Generated by Django 4.0 on 2021-12-29 09:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('package', '0013_alter_coupon_coupon_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='package',
            name='final_cost',
            field=models.FloatField(blank=True, default=1, max_length=50),
            preserve_default=False,
        ),
    ]