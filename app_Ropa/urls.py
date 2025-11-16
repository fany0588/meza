from django.urls import path
from . import views

urlpatterns = [
    # Páginas principales
    path('', views.inicio, name='inicio'),
    
    # Autenticación cliente
    path('inicio-sesion/', views.inicio_sesion, name='inicio_sesion'),
    path('registro/', views.registro, name='registro'),
    path('cerrar-sesion/', views.cerrar_sesion, name='cerrar_sesion'),
    
    # Perfil
    path('perfil/', views.perfil_cliente, name='perfil_cliente'),
    path('perfil/editar/', views.editar_perfil, name='editar_perfil'),
    
    # Categorías
    path('mujer/', views.mujer, name='mujer'),
    path('hombre/', views.hombre, name='hombre'),
    path('ninas/', views.ninas, name='ninas'),
    path('ninos/', views.ninos, name='ninos'),
    
    # Carrito y favoritos
    path('carrito/', views.carrito, name='carrito'),
    path('favoritos/', views.favoritos, name='favoritos'),
    
    # Reseñas
    path('reseñas/', views.reseñas, name='reseñas'),
    path('reseñas/eliminar/<int:id>/', views.eliminar_reseña, name='eliminar_reseña'),
    
    # Panel Admin
    path('admin/login/', views.admin_login, name='admin_login'),
    path('admin/panel/', views.panel_admin, name='panel_admin'),
    # CRUD Productos
    path('admin/productos/', views.admin_productos, name='admin_productos'),
    path('admin/productos/crear/', views.crear_producto, name='crear_producto'),
    path('admin/productos/editar/<int:producto_id>/', views.editar_producto, name='editar_producto'),
    path('admin/productos/eliminar/<int:producto_id>/', views.eliminar_producto, name='eliminar_producto'),
    # Categorías
    path('admin/categorias/', views.admin_categorias, name='admin_categorias'),
    path('admin/categorias/crear/', views.crear_categoria, name='crear_categoria'),
    path('admin/categorias/eliminar/<int:categoria_id>/', views.eliminar_categoria, name='eliminar_categoria'),
    
    # Pedidos
    path('admin/pedidos/', views.admin_pedidos, name='admin_pedidos'),
    path('admin/pedidos/<int:pedido_id>/', views.detalle_pedido, name='detalle_pedido'),
    
    # Reseñas admin
    path('admin/resenas/', views.admin_resenas, name='admin_resenas'),
    path('admin/resenas/aprobar/<int:resena_id>/', views.aprobar_resena, name='aprobar_resena'),
    path('admin/resenas/eliminar/<int:resena_id>/', views.eliminar_resena_admin, name='eliminar_resena_admin'),
    
    # Clientes admin
    path('admin/clientes/', views.admin_clientes, name='admin_clientes'),
    path('admin/clientes/<int:cliente_id>/', views.detalle_cliente, name='detalle_cliente'),
]