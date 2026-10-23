from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from src.pipeline import CRITICAL_FREE_FRACTION

REPONEDOR, JEFE, ADMIN = ROLES = ("Reponedor", "Jefe de Salón", "Administrador")

# Ciclo de una alerta de quiebre (CU02). Un analisis sin quiebre no tiene estado.
ACTIVA, EN_PROCESO, COMPLETADA, REEMPLAZADA = "activa", "en_proceso", "completada", "reemplazada"
ABIERTAS = (ACTIVA, EN_PROCESO)
ESTADOS = [(ACTIVA, "Activa"), (EN_PROCESO, "En proceso"), (COMPLETADA, "Completada"),
           (REEMPLAZADA, "Reemplazada por una foto más nueva")]


class User(AbstractUser):
    """Usuario del sistema. `username` guarda el RUT normalizado
    (12345678-5); se entra con RUT o correo (CU00), por eso el correo es unico."""

    email = models.EmailField("correo", unique=True)
    failed_logins = models.PositiveSmallIntegerField(default=0)
    locked_until = models.DateTimeField(null=True, blank=True)  # bloqueo por intentos fallidos (#51)

    @property
    def role(self) -> str:
        """Perfil del usuario: el grupo que le asigno el Administrador."""
        if self.is_superuser:
            return ADMIN
        group = self.groups.first()
        return group.name if group else ""


class Analysis(models.Model):
    """Una foto de gondola analizada con el pipeline (CU01) y, si hay
    quiebre, su alerta (CU02)."""

    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL)
    pasillo = models.CharField(max_length=20)
    gondola = models.CharField("góndola", max_length=20)
    photo_name = models.CharField(max_length=255)
    free_fraction = models.FloatField()
    critical = models.BooleanField()
    result = models.JSONField()  # PipelineResult.to_dict()
    annotated = models.FileField(upload_to="analisis/")
    estado = models.CharField(max_length=12, blank=True, choices=ESTADOS)
    taken_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True,
                                 on_delete=models.SET_NULL, related_name="+")
    estado_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]

    @property
    def location(self) -> str:
        return f"Pasillo {self.pasillo} · Góndola {self.gondola}"

    @property
    def strips(self) -> list[dict]:
        """Una franja por repisa, como el fleje del borde de la repisa: cada
        hueco como tramo en % del ancho de esa repisa (geometria del pipeline).
        Sin % ni alerta por repisa: se informan solo los de la gondola (#40)."""
        strips = []
        for number, shelf in enumerate(self.result["shelves"], start=1):
            left, right = _x_range(shelf["polygon"])
            width = (right - left) or 1.0
            gaps = []
            for gap in shelf["gaps"]:
                start, end = _x_range(gap)
                # Estilo armado aqui: en la plantilla, los decimales salen con coma (es).
                gaps.append(f"left:{(start - left) / width * 100:.2f}%;width:{(end - start) / width * 100:.2f}%")
            strips.append({"number": number, "gaps": gaps})
        return strips


def _x_range(polygon) -> tuple[float, float]:
    xs = [point[0] for point in polygon]
    return min(xs), max(xs)


class Config(models.Model):
    """Parametros de la tienda que configura el Administrador (CU05). Una
    sola fila: `Config.get()`."""

    umbral = models.PositiveSmallIntegerField(
        "umbral de espacio libre (%)", default=round(CRITICAL_FREE_FRACTION * 100),
        validators=[MinValueValidator(1), MaxValueValidator(100)])

    @classmethod
    def get(cls) -> "Config":
        return cls.objects.get_or_create(pk=1)[0]


class Camera(models.Model):
    """Camara de sala asociada a un pasillo y una gondola (CU05). Su
    calibracion de lente (formato de OpenCV, ver LensCalibration) se aplica
    a las fotos de esa gondola; sin ella solo se corrige el contraste."""

    nombre = models.CharField(max_length=60, unique=True)
    pasillo = models.CharField(max_length=20)
    gondola = models.CharField("góndola", max_length=20)
    calibracion = models.JSONField("calibración de lente", null=True, blank=True)

    class Meta:
        ordering = ["pasillo", "gondola"]
        # shortcut: una camara por gondola; si una gondola necesita dos, elegir la camara al subir la foto.
        constraints = [models.UniqueConstraint(fields=["pasillo", "gondola"], name="una_camara_por_gondola",
                                               violation_error_message="Esa góndola ya tiene una cámara.")]

    @property
    def location(self) -> str:
        return f"Pasillo {self.pasillo} · Góndola {self.gondola}"
