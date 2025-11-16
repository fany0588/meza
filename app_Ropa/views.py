from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import user_passes_test, login_required
from django.contrib.auth.hashers import make_password, check_password
from django.db.models import Q, Count, Sum
from django.utils import timezone
from datetime import datetime, timedelta
from .models import Cliente, Producto, Categoria, Pedido, Reseña

# ====================================
# INICIO
# ====================================
def inicio(request):
    productos_destacados = Producto.objects.filter(destacado=True)[:4]
    return render(request, 'inicio.html', {'productos_destacados': productos_destacados})
# ====================================
# AUTENTICACIÓN DE CLIENTE
# ====================================
def inicio_sesion(request):
    if request.method == "POST":
        email = request.POST.get('email')
        contraseña = request.POST.get('contraseña')

        try:
            cliente = Cliente.objects.get(email=email)
            if check_password(contraseña, cliente.contraseña):
                request.session['cliente_id'] = cliente.id
                messages.success(request, f"¡Bienvenido/a {cliente.nombre}!")
                return redirect('inicio')
            else:
                messages.error(request, "Contraseña incorrecta.")
        except Cliente.DoesNotExist:
            messages.error(request, "Correo no registrado.")
    return render(request, 'inicio_sesion.html')

def registro(request):
    if request.method == "POST":
        if Cliente.objects.filter(email=request.POST['email']).exists():
            messages.error(request, "Este correo ya está registrado.")
            return redirect('registro')

        Cliente.objects.create(
            nombre=request.POST['nombre'],
            apellido=request.POST['apellido'],
            email=request.POST['email'],
            telefono=request.POST['telefono'],
            contraseña=make_password(request.POST['contraseña']),
            calle=request.POST['calle'],
            numero_casa=request.POST['numero_casa'],
            colonia=request.POST['colonia'],
            ciudad=request.POST['ciudad'],
            codigo_postal=request.POST['codigo_postal'],
            descripcion_direccion=request.POST['descripcion_direccion'],
            metodo_pago=request.POST['metodo_pago']
        )
        messages.success(request, "Registro exitoso. Ahora puedes iniciar sesión.")
        return redirect('inicio_sesion')
    return render(request, 'registro.html')

def cerrar_sesion(request):
    if 'cliente_id' in request.session:
        del request.session['cliente_id']
    logout(request)
    messages.info(request, "Sesión cerrada correctamente.")
    return redirect('inicio')


def inicio_sesion(request):
    if request.method == "POST":
        # Verificar si es login de cliente o admin
        tipo_usuario = request.POST.get('tipo_usuario')
        
        if tipo_usuario == 'cliente':
            # Login para clientes (tu código actual)
            email = request.POST.get('email')
            contraseña = request.POST.get('contraseña')

            try:
                cliente = Cliente.objects.get(email=email)
                if check_password(contraseña, cliente.contraseña):
                    request.session['cliente_id'] = cliente.id
                    messages.success(request, f"¡Bienvenido/a {cliente.nombre}!")
                    return redirect('inicio')
                else:
                    messages.error(request, "Contraseña incorrecta.")
            except Cliente.DoesNotExist:
                messages.error(request, "Correo no registrado.")
                
        elif tipo_usuario == 'admin':
            # Redirigir al login de administradores
            return redirect('admin_login')
    
    return render(request, 'inicio_sesion.html')


# ====================================
# PERFIL DEL CLIENTE
# ====================================
def perfil_cliente(request):
    cliente_id = request.session.get('cliente_id')
    if not cliente_id:
        return redirect('inicio_sesion')

    cliente = Cliente.objects.get(id=cliente_id)
    pedidos = Pedido.objects.filter(cliente=cliente)
    return render(request, 'perfil.html', {'cliente': cliente, 'pedidos': pedidos})

def editar_perfil(request):
    cliente_id = request.session.get('cliente_id')
    if not cliente_id:
        return redirect('inicio_sesion')

    cliente = Cliente.objects.get(id=cliente_id)
    if request.method == "POST":
        for campo in ['nombre', 'apellido', 'telefono', 'calle', 'colonia', 'ciudad', 'codigo_postal', 'metodo_pago']:
            setattr(cliente, campo, request.POST.get(campo))
        cliente.save()
        messages.success(request, "Perfil actualizado correctamente.")
        return redirect('perfil_cliente')
    return render(request, 'editar_perfil.html', {'cliente': cliente})

# ====================================
# CATEGORÍAS DE PRODUCTOS (ACTUALIZADO)
# ====================================
def mujer(request):
    productos = Producto.objects.filter(tipo='mujer')
    return render(request, 'mujer.html', {'productos': productos})

def hombre(request):
    productos = Producto.objects.filter(tipo='hombre')
    return render(request, 'hombre.html', {'productos': productos})

def ninas(request):
    productos = Producto.objects.filter(tipo='ninas')
    return render(request, 'ninas.html', {'productos': productos})

def ninos(request):
    productos = Producto.objects.filter(tipo='ninos')
    return render(request, 'ninos.html', {'productos': productos})
# ====================================
# CARRITO
# ====================================
def carrito(request):
    cliente_id = request.session.get('cliente_id')
    if not cliente_id:
        messages.warning(request, "Debes iniciar sesión para acceder al carrito.")
        return redirect('inicio_sesion')
    return render(request, 'carrito.html')

# ====================================
# FAVORITOS
# ====================================
def favoritos(request):
    cliente_id = request.session.get('cliente_id')
    if not cliente_id:
        return redirect('inicio_sesion')
    # En el futuro, puedes mostrar los productos favoritos del cliente aquí
    return render(request, 'favoritos.html')

# ====================================
# RESEÑAS
# ====================================
def reseñas(request):
    reseñas_list = Reseña.objects.filter(aprobado=True)

    if request.method == "POST":
        cliente_id = request.session.get('cliente_id')
        if not cliente_id:
            return redirect('inicio_sesion')

        cliente = Cliente.objects.get(id=cliente_id)
        Reseña.objects.create(
            cliente=cliente,
            producto_id=request.POST['producto'],
            calificacion=request.POST['calificacion'],
            comentario=request.POST['comentario']
        )
        messages.success(request, "Reseña enviada correctamente.")
        return redirect('reseñas')

    return render(request, 'reseñas.html', {'reseñas': reseñas_list})

def eliminar_reseña(request, id):
    reseña = Reseña.objects.get(id=id)
    reseña.delete()
    messages.success(request, "Reseña eliminada.")
    return redirect('reseñas')

# ====================================
# PANEL ADMINISTRADOR (CRUD COMPLETO)
# ====================================
def es_admin(user):
    return user.is_staff

def admin_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        
        if user is not None and user.is_staff:
            login(request, user)
            messages.success(request, f"¡Bienvenido/a administrador {user.username}!")
            return redirect('panel_admin')  # Esto redirige a tu panel personalizado
        else:
            messages.error(request, 'Credenciales inválidas o no tienes permisos de administrador')
            return render(request, 'admin/admin_login.html')
    
    # Si el usuario ya está autenticado como admin, redirigir al panel personalizado
    if request.user.is_authenticated and request.user.is_staff:
        return redirect('panel_admin')  # Redirige a tu panel personalizado
        
    return render(request, 'admin/admin_login.html')
def panel_admin(request):
    # Estadísticas para el dashboard
    total_productos = Producto.objects.count()
    total_clientes = Cliente.objects.count()
    total_pedidos = Pedido.objects.count()
    pedidos_pendientes = Pedido.objects.filter(estado='pendiente').count()
    
    # Ventas del mes
    inicio_mes = timezone.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    ventas_mes = Pedido.objects.filter(
        fecha_pedido__gte=inicio_mes,
        estado__in=['entregado', 'enviado']
    ).aggregate(total=Sum('total'))['total'] or 0
    
    # Productos bajos en stock
    productos_bajo_stock = Producto.objects.filter(stock__lte=5)
    
    # Pedidos recientes
    pedidos_recientes = Pedido.objects.select_related('cliente').order_by('-fecha_pedido')[:5]
    
    context = {
        'total_productos': total_productos,
        'total_clientes': total_clientes,
        'total_pedidos': total_pedidos,
        'pedidos_pendientes': pedidos_pendientes,
        'ventas_mes': ventas_mes,
        'productos_bajo_stock': productos_bajo_stock,
        'pedidos_recientes': pedidos_recientes,
    }
    return render(request, 'admin/panel_admin.html', context)

# ====================================
# CRUD PRODUCTOS
# ====================================
@user_passes_test(es_admin)
def admin_productos(request):
    productos = Producto.objects.select_related('categoria').all()
    categorias = Categoria.objects.all()
    
    # Filtros
    categoria_id = request.GET.get('categoria')
    tipo = request.GET.get('tipo')
    search = request.GET.get('search')
    
    if categoria_id:
        productos = productos.filter(categoria_id=categoria_id)
    if tipo:
        productos = productos.filter(tipo=tipo)
    if search:
        productos = productos.filter(
            Q(nombre__icontains=search) | 
            Q(descripcion__icontains=search)
        )
    
    context = {
        'productos': productos,
        'categorias': categorias,
        'TIPOS': ['mujer', 'hombre', 'ninas', 'ninos']
    }
    return render(request, 'admin/productos/listar.html', context)

@user_passes_test(es_admin)
def crear_producto(request):
    categorias = Categoria.objects.all()
    
    if request.method == 'POST':
        try:
            producto = Producto.objects.create(
                nombre=request.POST['nombre'],
                descripcion=request.POST['descripcion'],
                precio=request.POST['precio'],
                precio_original=request.POST.get('precio_original') or request.POST['precio'],
                stock=request.POST['stock'],
                categoria_id=request.POST['categoria'],
                tipo=request.POST['tipo'],
                destacado=request.POST.get('destacado') == 'on'
            )
            
            if 'imagen' in request.FILES:
                producto.imagen = request.FILES['imagen']
                producto.save()
            
            messages.success(request, f'Producto "{producto.nombre}" creado exitosamente.')
            return redirect('admin_productos')
            
        except Exception as e:
            messages.error(request, f'Error al crear el producto: {str(e)}')
    
    return render(request, 'admin/productos/crear.html', {
        'categorias': categorias,
        'TIPOS': ['mujer', 'hombre', 'ninas', 'ninos']
    })

@user_passes_test(es_admin)
def editar_producto(request, producto_id):
    producto = get_object_or_404(Producto, id=producto_id)
    categorias = Categoria.objects.all()
    
    if request.method == 'POST':
        try:
            producto.nombre = request.POST['nombre']
            producto.descripcion = request.POST['descripcion']
            producto.precio = request.POST['precio']
            producto.precio_original = request.POST.get('precio_original') or request.POST['precio']
            producto.stock = request.POST['stock']
            producto.categoria_id = request.POST['categoria']
            producto.tipo = request.POST['tipo']
            producto.destacado = request.POST.get('destacado') == 'on'
            
            if 'imagen' in request.FILES:
                producto.imagen = request.FILES['imagen']
            
            producto.save()
            messages.success(request, f'Producto "{producto.nombre}" actualizado exitosamente.')
            return redirect('admin_productos')
            
        except Exception as e:
            messages.error(request, f'Error al actualizar el producto: {str(e)}')
    
    return render(request, 'admin/productos/editar.html', {
        'producto': producto,
        'categorias': categorias,
        'TIPOS': ['mujer', 'hombre', 'ninas', 'ninos']
    })

@user_passes_test(es_admin)
def eliminar_producto(request, producto_id):
    producto = get_object_or_404(Producto, id=producto_id)
    
    if request.method == 'POST':
        nombre_producto = producto.nombre
        producto.delete()
        messages.success(request, f'Producto "{nombre_producto}" eliminado exitosamente.')
        return redirect('admin_productos')
    
    return render(request, 'admin/productos/eliminar.html', {'producto': producto})

# ====================================
# CRUD CATEGORÍAS
# ====================================
@user_passes_test(es_admin)
def admin_categorias(request):
    categorias = Categoria.objects.annotate(
        total_productos=Count('producto')
    )
    return render(request, 'admin/categorias/listar.html', {'categorias': categorias})

@user_passes_test(es_admin)
def crear_categoria(request):
    if request.method == 'POST':
        try:
            Categoria.objects.create(
                nombre=request.POST['nombre'],
                descripcion=request.POST.get('descripcion', '')
            )
            messages.success(request, 'Categoría creada exitosamente.')
            return redirect('admin_categorias')
        except Exception as e:
            messages.error(request, f'Error al crear la categoría: {str(e)}')
    
    return render(request, 'admin/categorias/crear.html')

@user_passes_test(es_admin)
def eliminar_categoria(request, categoria_id):
    categoria = get_object_or_404(Categoria, id=categoria_id)
    
    if request.method == 'POST':
        # Verificar si hay productos en esta categoría
        if categoria.producto_set.exists():
            messages.error(request, 'No se puede eliminar la categoría porque tiene productos asociados.')
            return redirect('admin_categorias')
        
        categoria.delete()
        messages.success(request, 'Categoría eliminada exitosamente.')
        return redirect('admin_categorias')
    
    return render(request, 'admin/categorias/eliminar.html', {'categoria': categoria})

# ====================================
# GESTIÓN DE PEDIDOS
# ====================================
@user_passes_test(es_admin)
def admin_pedidos(request):
    pedidos = Pedido.objects.select_related('cliente').all()
    
    # Filtros
    estado = request.GET.get('estado')
    fecha_inicio = request.GET.get('fecha_inicio')
    fecha_fin = request.GET.get('fecha_fin')
    
    if estado:
        pedidos = pedidos.filter(estado=estado)
    if fecha_inicio:
        pedidos = pedidos.filter(fecha_pedido__gte=fecha_inicio)
    if fecha_fin:
        pedidos = pedidos.filter(fecha_pedido__lte=fecha_fin)
    
    context = {
        'pedidos': pedidos,
        'ESTADOS': ['pendiente', 'procesando', 'enviado', 'entregado', 'cancelado']
    }
    return render(request, 'admin/pedidos/listar.html', context)

@user_passes_test(es_admin)
def detalle_pedido(request, pedido_id):
    pedido = get_object_or_404(Pedido.objects.select_related('cliente'), id=pedido_id)
    items = pedido.itempedido_set.select_related('producto')
    
    if request.method == 'POST':
        nuevo_estado = request.POST.get('estado')
        if nuevo_estado in dict(Pedido.ESTADO_CHOICES):
            pedido.estado = nuevo_estado
            pedido.save()
            messages.success(request, f'Estado del pedido actualizado a {nuevo_estado}.')
        return redirect('detalle_pedido', pedido_id=pedido_id)
    
    return render(request, 'admin/pedidos/detalle.html', {
        'pedido': pedido,
        'items': items,
        'ESTADOS': Pedido.ESTADO_CHOICES
    })

# ====================================
# GESTIÓN DE RESEÑAS
# ====================================
@user_passes_test(es_admin)
def admin_resenas(request):
    reseñas_list = Reseña.objects.select_related('cliente', 'producto').all()
    
    # Filtros
    aprobado = request.GET.get('aprobado')
    calificacion = request.GET.get('calificacion')
    
    if aprobado is not None:
        reseñas_list = reseñas_list.filter(aprobado=(aprobado == 'true'))
    if calificacion:
        reseñas_list = reseñas_list.filter(calificacion=calificacion)
    
    return render(request, 'admin/resenas/listar.html', {'reseñas': reseñas_list})

@user_passes_test(es_admin)
def aprobar_resena(request, resena_id):
    resena = get_object_or_404(Reseña, id=resena_id)
    resena.aprobado = True
    resena.save()
    messages.success(request, 'Reseña aprobada exitosamente.')
    return redirect('admin_resenas')

@user_passes_test(es_admin)
def eliminar_resena_admin(request, resena_id):
    resena = get_object_or_404(Reseña, id=resena_id)
    
    if request.method == 'POST':
        resena.delete()
        messages.success(request, 'Reseña eliminada exitosamente.')
        return redirect('admin_resenas')
    
    return render(request, 'admin/resenas/eliminar.html', {'resena': resena})

# ====================================
# GESTIÓN DE CLIENTES
# ====================================
@user_passes_test(es_admin)
def admin_clientes(request):
    clientes = Cliente.objects.all()
    
    search = request.GET.get('search')
    if search:
        clientes = clientes.filter(
            Q(nombre__icontains=search) |
            Q(apellido__icontains=search) |
            Q(email__icontains=search)
        )
    
    return render(request, 'admin/clientes/listar.html', {'clientes': clientes})

@user_passes_test(es_admin)
def detalle_cliente(request, cliente_id):
    cliente = get_object_or_404(Cliente, id=cliente_id)
    pedidos = Pedido.objects.filter(cliente=cliente).order_by('-fecha_pedido')
    reseñas = Reseña.objects.filter(cliente=cliente).select_related('producto')
    
    return render(request, 'admin/clientes/detalle.html', {
        'cliente': cliente,
        'pedidos': pedidos,
        'reseñas': reseñas
    })