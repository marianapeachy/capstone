from web.models import ABIERTAS, Analysis


def open_alerts(request):
    """Alertas abiertas para el contador de la barra superior."""
    if not getattr(request, "user", None) or not request.user.is_authenticated:
        return {}
    return {"open_alerts": Analysis.objects.filter(estado__in=ABIERTAS).count()}
