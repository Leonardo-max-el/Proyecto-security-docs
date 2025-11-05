from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.http import HttpResponse, FileResponse
from .models import Document
from .forms import DocumentForm
import mimetypes
from django.conf import settings
from django.urls import reverse
from django.http import Http404


def login_view(request):
    """Vista de login"""
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            if user.is_staff:
                return redirect('dashboard')
            else:
                messages.warning(request, 'Solo administradores pueden acceder al panel')
                logout(request)
        else:
            messages.error(request, 'Usuario o contraseña incorrectos')
    
    return render(request, 'security_qr_app/login.html')

def logout_view(request):
    """Vista de logout"""
    logout(request)
    messages.success(request, 'Sesión cerrada correctamente')
    return redirect('login')

@login_required
def dashboard(request):
    """Panel principal del administrador"""
    if not request.user.is_staff:
        messages.error(request, 'No tienes permisos para acceder')
        return redirect('login')
    
    documentos = Document.objects.all()
    return render(request, 'security_qr_app/dashboard.html', {
        'documentos': documentos
    })

@login_required
def subir_documento(request):
    """Vista para subir documentos"""
    if not request.user.is_staff:
        messages.error(request, 'No tienes permisos para acceder')
        return redirect('login')
    
    if request.method == 'POST':
        form = DocumentForm(request.POST, request.FILES)
        if form.is_valid():
            documento = form.save(commit=False)
            documento.subido_por = request.user
            documento.save()
            messages.success(request, 'Documento subido correctamente')
            return redirect('ver_documento_admin', codigo=documento.codigo_unico)
    else:
        form = DocumentForm()
    
    return render(request, 'security_qr_app/subir_documento.html', {
        'form': form
    })

@login_required
def ver_documento_admin(request, codigo):
    """Vista del documento para el admin (con descarga de QR)"""
    if not request.user.is_staff:
        messages.error(request, 'No tienes permisos para acceder')
        return redirect('login')
    
    documento = get_object_or_404(Document, codigo_unico=codigo)
    return render(request, 'security_qr_app/ver_documento_admin.html', {
        'documento': documento
    })

def ver_documento_publico(request, codigo):
    """
    Vista pública del documento (para usuarios que escanean QR).
    Muestra el documento directamente en la página con vista previa.
    """
    documento = get_object_or_404(Document, codigo_unico=codigo)

    # Verificar que el archivo exista físicamente
    if not documento.archivo:
        raise Http404("El archivo del documento no se encuentra disponible.")

    # (Opcional) Incrementar contador de vistas/descargas
    documento.incrementar_descargas()

    # Renderizar la plantilla (NO redirigir)
    return render(request, 'security_qr_app/ver_documento_publico.html', {
        'documento': documento
    })

def descargar_archivo(request, codigo):
    """Descarga el archivo del documento"""
    documento = get_object_or_404(Document, codigo_unico=codigo)
    documento.incrementar_descargas()
    
    # Obtener el archivo
    archivo = documento.archivo
    
    # Determinar el tipo MIME
    content_type, _ = mimetypes.guess_type(archivo.name)
    
    # Crear respuesta con el archivo
    response = FileResponse(archivo.open('rb'), content_type=content_type)
    response['Content-Disposition'] = f'attachment; filename="{archivo.name}"'
    
    return response

@login_required
def descargar_qr(request, codigo):
    """Descarga el código QR"""
    if not request.user.is_staff:
        messages.error(request, 'No tienes permisos para acceder')
        return redirect('login')
    
    documento = get_object_or_404(Document, codigo_unico=codigo)
    
    if not documento.qr_code:
        messages.error(request, 'El QR no está disponible')
        return redirect('dashboard')
    
    # Crear respuesta con la imagen QR
    response = FileResponse(documento.qr_code.open('rb'), content_type='image/png')
    response['Content-Disposition'] = f'attachment; filename="QR_{documento.titulo}.png"'
    
    return response

@login_required
def eliminar_documento(request, codigo):
    """Elimina un documento"""
    if not request.user.is_staff:
        messages.error(request, 'No tienes permisos para acceder')
        return redirect('login')
    
    documento = get_object_or_404(Document, codigo_unico=codigo)
    
    if request.method == 'POST':
        documento.delete()
        messages.success(request, 'Documento eliminado correctamente')
        return redirect('dashboard')
    
    return render(request, 'security_qr_app/eliminar_documento.html', {
        'documento': documento
    })