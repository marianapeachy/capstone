from django.contrib.auth import views as auth_views
from django.urls import path, reverse_lazy

from web import views
from web.forms import LoginForm

urlpatterns = [
    path("", views.inicio, name="inicio"),
    path("login/", auth_views.LoginView.as_view(authentication_form=LoginForm), name="login"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("clave/<uidb64>/<token>/",
         auth_views.PasswordResetConfirmView.as_view(success_url=reverse_lazy("login")), name="definir_clave"),
    path("usuarios/", views.usuarios, name="usuarios"),
    path("usuarios/nuevo/", views.usuario_form, name="usuario_nuevo"),
    path("usuarios/<int:pk>/", views.usuario_form, name="usuario_editar"),
    path("usuarios/<int:pk>/enlace/", views.usuario_enlace, name="usuario_enlace"),
    path("analisis/", views.analisis, name="analisis"),
    path("analisis/<int:pk>/", views.analisis_detalle, name="analisis_detalle"),
    path("analisis/<int:pk>/imagen.jpg", views.analisis_imagen, name="analisis_imagen"),
    path("alertas/", views.alertas, name="alertas"),
    path("reportes/", views.reportes, name="reportes"),
    path("alertas/<int:pk>/<str:accion>/", views.alerta_accion, name="alerta_accion"),
]
