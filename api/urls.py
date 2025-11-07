from django.urls import path
from . import views

urlpatterns = [
    path("analizar_texto/", views.analizar_texto),
    path("analizar_patrones/", views.analizar_patrones),
    path("analizar_similitud/", views.analizar_similitud),
    path("analizar_chat/", views.analizar_chat),
    path('get_nlp_metrics/', views.get_nlp_metrics, name='get_nlp_metrics'),
]
