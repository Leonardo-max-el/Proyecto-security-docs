from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('subir/', views.subir_documento, name='subir_documento'),
    path('ver/<uuid:codigo>/', views.ver_documento_publico, name='ver_documento_publico'),
    path('ver_admin/<uuid:codigo>/', views.ver_documento_admin, name='ver_documento_admin'),
    path('descargar/<uuid:codigo>/', views.descargar_archivo, name='descargar_archivo'),
    path('descargar_qr/<uuid:codigo>/', views.descargar_qr, name='descargar_qr'),
    path('eliminar/<uuid:codigo>/', views.eliminar_documento, name='eliminar_documento'),
]
