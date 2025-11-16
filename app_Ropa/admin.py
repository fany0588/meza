from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from django.contrib.auth.models import User
from .models import Producto, Categoria, Cliente, Pedido, Reseña

# Personalizar el admin site
admin.site.site_header = "FamFashion - Administración"
admin.site.site_title = "Panel de Administración FamFashion"
admin.site.index_title = "Bienvenido al Panel de Administración"

class ProductoAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'precio', 'stock', 'categoria', 'tipo', 'destacado']
    list_filter = ['categoria', 'tipo', 'destacado']
    search_fields = ['nombre', 'descripcion']

class CustomUserAdmin(admin.ModelAdmin):
    list_display = ['username', 'email', 'first_name', 'last_name', 'is_staff', 'panel_personalizado']
    
    def panel_personalizado(self, obj):
        if obj.is_staff:
            url = reverse('panel_admin')
            return format_html('<a href="{}" class="button">🚀 Ir al Panel Personalizado</a>', url)
        return "No disponible"
    panel_personalizado.short_description = "Panel Personalizado"

# Re-registrar User admin si ya estaba registrado
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)

admin.site.register(Producto, ProductoAdmin)
admin.site.register(Categoria)
admin.site.register(Cliente)
admin.site.register(Pedido)
admin.site.register(Reseña)