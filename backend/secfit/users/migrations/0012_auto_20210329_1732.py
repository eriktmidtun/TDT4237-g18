# Generated by Django 3.1 on 2021-03-29 15:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0011_user_is_verified'),
    ]

    operations = [
        migrations.CreateModel(
            name='RememberMe',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('remember_me', models.CharField(max_length=500)),
            ],
        ),
        migrations.AddField(
            model_name='user',
            name='secret2fa',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
    ]
