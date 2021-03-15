# Generated by Django 3.1 on 2021-03-10 09:08

from django.db import migrations, models
import workouts.models
import workouts.validators


class Migration(migrations.Migration):

    dependencies = [
        ('workouts', '0002_auto_20200910_0222'),
    ]

    operations = [
        migrations.CreateModel(
            name='RememberMe',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('remember_me', models.CharField(max_length=500)),
            ],
        ),
        migrations.AlterField(
            model_name='workoutfile',
            name='file',
            field=models.FileField(upload_to=workouts.models.workout_directory_path, validators=[workouts.validators.ImageValidator]),
        ),
    ]
