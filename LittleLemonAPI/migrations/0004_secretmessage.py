# Generated by Django 5.0.6 on 2024-05-24 02:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('LittleLemonAPI', '0003_alter_menuitem_category'),
    ]

    operations = [
        migrations.CreateModel(
            name='SecretMessage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(db_index=True, max_length=255)),
            ],
        ),
    ]
