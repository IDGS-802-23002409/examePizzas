import datetime

from flask import Blueprint, render_template, redirect, url_for, flash, request
from app.models import db, Pizza, Cliente, Pedido, DetallePedido
from app.carrito_file import agregar_item, quitar_item, leer_carrito, limpiar_carrito

pedidos_bp = Blueprint('pedidos', __name__)

PRECIOS_TAMANO     = {'Chica': 40, 'Mediana': 80, 'Grande': 120}
PRECIO_INGREDIENTE = 10


@pedidos_bp.route('/', methods=['GET'])
def index():
    from app.forms import PedidoForm
    form = PedidoForm()

    # Pre-llenar campos del cliente con lo guardado en el archivo
    data = leer_carrito()
    cliente_guardado = data.get('cliente', {})
    if cliente_guardado:
        form.nombre.data     = cliente_guardado.get('nombre', '')
        form.direccion.data  = cliente_guardado.get('direccion', '')
        form.telefono.data   = cliente_guardado.get('telefono', '')
        form.fecha_dia.data  = cliente_guardado.get('fecha_dia')
        form.fecha_mes.data  = str(cliente_guardado.get('fecha_mes', '1'))
        form.fecha_anio.data = cliente_guardado.get('fecha_anio')

    carrito = data.get('items', [])

    hoy = datetime.date.today()
    ventas_raw = db.session.query(Pedido, Cliente).join(
        Cliente, Pedido.id_cliente == Cliente.id_cliente
    ).filter(Pedido.fecha == hoy).all()

    ventas_hoy = [{'pedido': p, 'cliente': c} for p, c in ventas_raw]
    total_hoy  = sum(float(v['pedido'].total or 0) for v in ventas_hoy)

    return render_template('index.html', form=form, carrito=carrito,
                           ventas_hoy=ventas_hoy, total_hoy=total_hoy)


@pedidos_bp.route('/agregar', methods=['POST'])
def agregar():
    from app.forms import PedidoForm
    form = PedidoForm()

    if form.validate_on_submit():
        tamano           = form.tamano.data
        ingredientes_sel = form.ingredientes.data or []
        num_pizzas       = form.num_pizzas.data

        precio_base = PRECIOS_TAMANO.get(tamano, 0)
        precio_ingr = len(ingredientes_sel) * PRECIO_INGREDIENTE
        subtotal    = (precio_base + precio_ingr) * num_pizzas

        ingredientes_str = ', '.join(ingredientes_sel) if ingredientes_sel else 'Sin ingredientes'

        cliente = {
            'nombre':     form.nombre.data,
            'direccion':  form.direccion.data,
            'telefono':   form.telefono.data,
            'fecha_dia':  form.fecha_dia.data,
            'fecha_mes':  int(form.fecha_mes.data),
            'fecha_anio': form.fecha_anio.data,
        }

        agregar_item(cliente, tamano, ingredientes_str, num_pizzas, subtotal)
    else:
        for field, errors in form.errors.items():
            for error in errors:
                flash(f'Error en {field}: {error}', 'danger')

    return redirect(url_for('pedidos.index'))


@pedidos_bp.route('/quitar/<int:indice>', methods=['POST'])
def quitar(indice):
    quitar_item(indice)
    return redirect(url_for('pedidos.index'))


@pedidos_bp.route('/terminar', methods=['POST'])
def terminar():
    data    = leer_carrito()
    carrito = data.get('items', [])
    cliente_data = data.get('cliente', {})

    if not carrito:
        flash('No hay pizzas en el pedido.', 'warning')
        return redirect(url_for('pedidos.index'))

    if not cliente_data.get('nombre'):
        flash('Faltan datos del cliente.', 'warning')
        return redirect(url_for('pedidos.index'))

    total = sum(float(item['subtotal']) for item in carrito)

    # Guardar o reutilizar cliente en la BD
    cliente = Cliente.query.filter_by(
        nombre=cliente_data['nombre'],
        telefono=cliente_data['telefono']
    ).first()

    if not cliente:
        cliente = Cliente(
            nombre    = cliente_data['nombre'],
            direccion = cliente_data['direccion'],
            telefono  = cliente_data['telefono'],
        )
        db.session.add(cliente)
        db.session.flush()

    try:
        fecha = datetime.date(
            int(cliente_data['fecha_anio']),
            int(cliente_data['fecha_mes']),
            int(cliente_data['fecha_dia'])
        )
    except (ValueError, TypeError):
        fecha = datetime.date.today()

    pedido = Pedido(id_cliente=cliente.id_cliente, fecha=fecha, total=total)
    db.session.add(pedido)
    db.session.flush()

    for item in carrito:
        pizza = Pizza.query.filter_by(tamano=item['tamano']).first()
        if not pizza:
            pizza = Pizza.query.first()

        detalle = DetallePedido(
            id_pedido = pedido.id_pedido,
            id_pizza  = pizza.id_pizza,
            cantidad  = item['num_pizzas'],
            subtotal  = item['subtotal'],
        )
        db.session.add(detalle)

    db.session.commit()

    # Eliminar el archivo temporal
    limpiar_carrito()

    flash(f'Pedido terminado. Total a pagar: ${total:.2f}', 'success')
    return redirect(url_for('pedidos.index'))
