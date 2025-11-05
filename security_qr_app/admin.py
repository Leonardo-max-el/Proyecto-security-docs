from django.contrib import admin
from .models import Document

@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ['titulo', 'tipo_archivo', 'subido_por', 'fecha_subida', 'descargas']
    list_filter = ['tipo_archivo', 'fecha_subida']
    search_fields = ['titulo', 'descripcion']
    readonly_fields = ['codigo_unico', 'qr_code', 'descargas', 'fecha_subida']