# Generated by Django 4.2.7 on 2023-12-14 03:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Iapp', '0016_alter_cart_unique_together'),
    ]

    operations = [
        migrations.AlterField(
            model_name='products',
            name='id',
            field=models.CharField(max_length=20, primary_key=True, serialize=False),
        ),
    ]
