"""Borra las fotos analizadas mas antiguas que N dias (RNF05, item #45).

Las fotos de tienda pueden mostrar clientes, y RNF05 pide no guardar
rostros ni datos personales. Se borra solo la imagen: el analisis queda
(% libre, alerta, estado e historial), asi que el dashboard (CU03) y los
reportes (CU04) siguen funcionando. Pensado para correr una vez al dia
(cron o el programador del servidor del CITT, #39):

    python manage.py borrar_fotos --dias 30
"""

from datetime import timedelta

from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone

from web.models import Analysis


class Command(BaseCommand):
    help = "Borra las fotos analizadas con mas de N dias y conserva sus resultados (RNF05)."

    def add_arguments(self, parser):
        # 30 dias es una propuesta: el plazo lo confirma Walmart (#24).
        parser.add_argument("--dias", type=int, default=30, help="antiguedad minima de las fotos a borrar (30)")

    def handle(self, *args, dias, **options):
        if dias < 1:
            raise CommandError("--dias debe ser al menos 1.")
        old = Analysis.objects.filter(created_at__lt=timezone.now() - timedelta(days=dias)).exclude(annotated="")
        count = 0
        for analysis in old.only("pk", "annotated"):
            analysis.annotated.delete(save=False)  # borra el archivo
            analysis.save(update_fields=["annotated"])
            count += 1
        self.stdout.write(f"{count} foto{'s' if count != 1 else ''} con más de {dias} días borrada{'s' if count != 1 else ''}.")
