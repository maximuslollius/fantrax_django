# Generated by Django 3.1.2 on 2022-06-17 08:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('analysis_app', '0003_auto_20220617_0831'),
    ]

    operations = [
        migrations.AlterField(
            model_name='normscores',
            name='id',
            field=models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
        migrations.AlterField(
            model_name='playerprofilescores',
            name='id',
            field=models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
    ]