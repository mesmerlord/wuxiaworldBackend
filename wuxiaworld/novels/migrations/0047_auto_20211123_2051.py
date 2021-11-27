# Generated by Django 3.1.12 on 2021-11-23 20:51

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('novels', '0046_auto_20211123_2039'),
    ]

    operations = [
        migrations.AddField(
            model_name='novel',
            name='rating',
            field=models.CharField(blank=True, default='5.0', max_length=5),
        ),
        migrations.AddField(
            model_name='review',
            name='novel',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to='novels.novel'),
            preserve_default=False,
        ),
    ]
