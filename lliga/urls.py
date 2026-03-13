from django.urls import path
from . import views

app_name = 'lliga'

urlpatterns = [
    path('', views.index, name='index'),
    path('menu/', views.menu, name='menu'),
    path('lliga/<int:lliga_id>/partits/', views.partits, name='partits'),
    path('lliga/<int:lliga_id>/classificacio/', views.classificacio, name='classificacio'),
    path('lliga/<int:lliga_id>/pichichi/', views.pichichi, name='pichichi'),
    path('partit/<int:partit_id>/', views.partit_detall, name='partit_detall'),
]
