# Generated by Django 3.1.12 on 2021-11-23 22:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('novels', '0047_auto_20211123_2051'),
    ]

    operations = [
        migrations.AlterField(
            model_name='novel',
            name='rating',
            field=models.DecimalField(blank=True, decimal_places=2, default=5.0, max_digits=3),
        ),
    ]
