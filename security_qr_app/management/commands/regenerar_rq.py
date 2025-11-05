from django.core.management.base import BaseCommand
from security_qr_app.models import Document
from django.conf import settings

class Command(BaseCommand):
    help = 'Regenera los códigos QR de todos los documentos usando el dominio actual del settings.py'

    def handle(self, *args, **kwargs):
        total_docs = Document.objects.count()
        self.stdout.write(self.style.NOTICE(f'🔍 Se encontraron {total_docs} documentos en la base de datos.'))

        actualizados = 0
        for doc in Document.objects.all():
            try:
                doc.generar_qr()
                actualizados += 1
                self.stdout.write(f'✅ QR regenerado para: {doc.titulo} ({doc.codigo_unico})')
            except Exception as e:
                self.stderr.write(f'❌ Error en {doc.titulo}: {e}')

        self.stdout.write(self.style.SUCCESS(f'\n🎉 Proceso completado. {actualizados}/{total_docs} QR actualizados.'))
        self.stdout.write(self.style.HTTP_INFO(f'Usando dominio: {settings.SITE_DOMAIN}'))
