# Generated by Django 3.1.12 on 2021-09-13 17:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('novels', '0014_chapter_scrapelink'),
    ]

    operations = [
        migrations.AddField(
            model_name='novel',
            name='imageThumb',
            field=models.URLField(blank=True),
        ),
    ]
