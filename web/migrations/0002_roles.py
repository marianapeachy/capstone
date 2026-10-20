"""Crea los tres perfiles del sistema como grupos (CU00, CU06)."""

from django.db import migrations

ROLES = ("Reponedor", "Jefe de Salón", "Administrador")


def create_roles(apps, schema_editor):
    Group = apps.get_model("auth", "Group")
    for name in ROLES:
        Group.objects.get_or_create(name=name)


def delete_roles(apps, schema_editor):
    apps.get_model("auth", "Group").objects.filter(name__in=ROLES).delete()


class Migration(migrations.Migration):
    dependencies = [("web", "0001_initial")]
    operations = [migrations.RunPython(create_roles, delete_roles)]
