# Generated by Django 4.2.17 on 2025-01-06 08:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0004_shipping_order'),
    ]

    operations = [
        migrations.AddField(
            model_name='cart',
            name='is_order_created',
            field=models.BooleanField(default=False, verbose_name='Is order created'),
        ),
    ]
