# Generated by Django 3.1.12 on 2021-08-21 21:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('novels', '0009_auto_20210821_2109'),
    ]

    operations = [
        migrations.AlterField(
            model_name='novel',
            name='slug',
            field=models.SlugField(blank=True, default=None, max_length=200, primary_key=True, serialize=False),
        ),
    ]
