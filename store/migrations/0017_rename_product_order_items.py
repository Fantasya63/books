# Generated by Django 5.0.5 on 2024-05-23 03:25

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0016_alter_order_product'),
    ]

    operations = [
        migrations.RenameField(
            model_name='order',
            old_name='product',
            new_name='items',
        ),
    ]
