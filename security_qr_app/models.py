from django.db import models
from django.contrib.auth.models import User
import uuid
import qrcode
from io import BytesIO
from django.core.files import File
from PIL import Image
from django.conf import settings
from django.urls import reverse


class Document(models.Model):
    TIPO_ARCHIVO = [
        ('pdf', 'PDF'),
        ('imagen', 'Imagen'),
        ('video', 'Video'),
        ('otro', 'Otro'),
    ]

    # Campos básicos
    titulo = models.CharField(max_length=200)
    descripcion = models.TextField(blank=True, null=True)
    tipo_archivo = models.CharField(max_length=10, choices=TIPO_ARCHIVO, default='otro')
    archivo = models.FileField(upload_to='documentos/')

    # QR único
    codigo_unico = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    qr_code = models.ImageField(upload_to='qr_codes/', blank=True)

    # Metadatos
    subido_por = models.ForeignKey(User, on_delete=models.CASCADE)
    fecha_subida = models.DateTimeField(auto_now_add=True)
    descargas = models.IntegerField(default=0)

    class Meta:
        ordering = ['-fecha_subida']
        verbose_name = 'Documento'
        verbose_name_plural = 'Documentos'

    def __str__(self):
        return f"{self.titulo} ({self.codigo_unico})"

    def save(self, *args, **kwargs):
        """Guarda el documento y genera el QR si no existe"""
        # Detectar tipo de archivo automáticamente
        if self.archivo:
            extension = self.archivo.name.split('.')[-1].lower()
            if extension == 'pdf':
                self.tipo_archivo = 'pdf'
            elif extension in ['jpg', 'jpeg', 'png', 'gif', 'bmp']:
                self.tipo_archivo = 'imagen'
            elif extension in ['mp4', 'avi', 'mov', 'wmv', 'mkv']:
                self.tipo_archivo = 'video'

        # Guardar primero para tener el ID
        super().save(*args, **kwargs)

        # Generar QR si no existe
        if not self.qr_code:
            self.generar_qr()

    def generar_qr(self):
        """Genera el código QR con la URL del documento"""
        # Asegúrate de que en settings.py esté configurado SITE_DOMAIN
        url = f"{settings.SITE_DOMAIN}{reverse('ver_documento_publico', args=[self.codigo_unico])}"

        # Crear QR
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(url)
        qr.make(fit=True)

        # Crear imagen del QR
        img = qr.make_image(fill_color="black", back_color="white")

        # Guardar en BytesIO
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        buffer.seek(0)

        # Guardar en el modelo
        filename = f'qr_{self.codigo_unico}.png'
        self.qr_code.save(filename, File(buffer), save=False)
        super().save(update_fields=['qr_code'])

    def incrementar_descargas(self):
        """Incrementa el contador de descargas"""
        self.descargas += 1
        self.save(update_fields=['descargas'])
