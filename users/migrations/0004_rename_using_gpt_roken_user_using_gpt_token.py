# Generated by Django 4.2.3 on 2023-07-27 07:39

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("users", "0003_remove_user_name_user_created_at_and_more"),
    ]

    operations = [
        migrations.RenameField(
            model_name="user",
            old_name="using_gpt_roken",
            new_name="using_gpt_token",
        ),
    ]
