# Generated by Django 4.2.7 on 2023-11-21 07:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Iapp', '0003_delete_admin_alter_cart_user_alter_ordereditems_user_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='productscategories',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True),
        ),
        migrations.AlterField(
            model_name='productscategories',
            name='modified_at',
            field=models.DateTimeField(auto_now=True),
        ),
    ]
