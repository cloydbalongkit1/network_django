# Generated by Django 5.1.2 on 2024-11-14 03:21

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('network', '0009_remove_user_followers_user_followers'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Follow',
        ),
    ]
