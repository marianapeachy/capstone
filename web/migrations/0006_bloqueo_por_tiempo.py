"""Bloqueo de 15 minutos por intentos fallidos en vez de desactivar la cuenta (#51)."""

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('web', '0005_normalizar_ubicacion'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='locked_until',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
