# Generated by Django 3.1.12 on 2021-09-18 08:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('novels', '0018_auto_20210914_0820'),
    ]

    operations = [
        migrations.AlterField(
            model_name='chapter',
            name='index',
            field=models.IntegerField(blank=True, default=None, unique=True),
        ),
    ]