"""Pasillo y gondola sin espacios y en mayusculas, como los guardan ahora los
formularios (#49): asi una alerta vieja en "a1" se reemplaza con una foto
nueva en "A1"."""

from django.db import migrations


def normalize(apps, schema_editor):
    for analysis in apps.get_model("web", "Analysis").objects.all():
        analysis.pasillo, analysis.gondola = analysis.pasillo.strip().upper(), analysis.gondola.strip().upper()
        analysis.save(update_fields=["pasillo", "gondola"])
    Camera = apps.get_model("web", "Camera")
    for camera in Camera.objects.all():
        pasillo, gondola = camera.pasillo.strip().upper(), camera.gondola.strip().upper()
        # Una camara por gondola: si "a1" y "A1" ya tenian camara cada una, esta queda como estaba.
        if not Camera.objects.filter(pasillo=pasillo, gondola=gondola).exclude(pk=camera.pk).exists():
            camera.pasillo, camera.gondola = pasillo, gondola
            camera.save(update_fields=["pasillo", "gondola"])


class Migration(migrations.Migration):
    dependencies = [("web", "0004_configuracion_y_camaras")]

    operations = [migrations.RunPython(normalize, migrations.RunPython.noop)]
