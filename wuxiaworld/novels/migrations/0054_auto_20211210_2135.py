# Generated by Django 3.1.12 on 2021-12-10 21:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('novels', '0053_auto_20211207_0657'),
    ]

    operations = [
        migrations.AddField(
            model_name='novel',
            name='new_image',
            field=models.ImageField(default='', upload_to=''),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='novel',
            name='new_image_thumb',
            field=models.ImageField(default='', upload_to=''),
            preserve_default=False,
        ),
    ]