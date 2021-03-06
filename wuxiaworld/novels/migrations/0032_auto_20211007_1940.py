# Generated by Django 3.1.12 on 2021-10-07 19:40

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('novels', '0031_auto_20211007_0754'),
    ]

    operations = [
        migrations.CreateModel(
            name='Settings',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fontSize', models.IntegerField(default=16)),
                ('autoBookMark', models.BooleanField(default=False)),
                ('lowData', models.BooleanField(default=False)),
                ('darkMode', models.BooleanField(default=False)),
            ],
        ),
        migrations.AddField(
            model_name='profile',
            name='settings',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='novels.settings'),
        ),
    ]
