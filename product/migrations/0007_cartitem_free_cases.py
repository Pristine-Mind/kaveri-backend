# Generated by Django 4.2.17 on 2025-01-07 07:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0006_alter_cart_user'),
    ]

    operations = [
        migrations.AddField(
            model_name='cartitem',
            name='free_cases',
            field=models.PositiveIntegerField(default=0, verbose_name='Free Cases'),
        ),
    ]
