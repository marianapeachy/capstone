"""Ubicacion de la gondola (pasillo y numero) y ciclo de la alerta (CU02)."""

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


def open_existing_alerts(apps, schema_editor):
    apps.get_model("web", "Analysis").objects.filter(critical=True).update(estado="activa")


class Migration(migrations.Migration):
    dependencies = [("web", "0002_roles")]

    operations = [
        migrations.AddField(
            model_name="analysis", name="pasillo",
            field=models.CharField(default="?", max_length=20), preserve_default=False),
        migrations.AddField(
            model_name="analysis", name="gondola",
            field=models.CharField(default="?", max_length=20, verbose_name="góndola"), preserve_default=False),
        migrations.AddField(
            model_name="analysis", name="estado",
            field=models.CharField(blank=True, max_length=12, choices=[
                ("activa", "Activa"), ("en_proceso", "En proceso"), ("completada", "Completada"),
                ("reemplazada", "Reemplazada por una foto más nueva")])),
        migrations.AddField(
            model_name="analysis", name="taken_by",
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL,
                                    related_name="+", to=settings.AUTH_USER_MODEL)),
        migrations.AddField(
            model_name="analysis", name="estado_at", field=models.DateTimeField(blank=True, null=True)),
        migrations.RunPython(open_existing_alerts, migrations.RunPython.noop),
    ]
