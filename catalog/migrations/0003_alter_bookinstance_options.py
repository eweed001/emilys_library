# Generated by Django 3.2.4 on 2021-07-01 15:27

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0002_auto_20210701_1108'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='bookinstance',
            options={'permissions': (('can_marked_returned', 'Set book as returned'),)},
        ),
    ]
