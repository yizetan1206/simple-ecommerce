# Generated by Django 4.2.7 on 2023-12-11 05:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Iapp', '0011_cart_order'),
    ]

    operations = [
        migrations.AddField(
            model_name='cart',
            name='subtotal',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10),
        ),
    ]
