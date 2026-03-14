import uuid
import datetime

from flask import Blueprint, render_template, redirect, url_for, flash, request, make_response
from app.models import db, Pizza, Cliente, Pedido, DetallePedido, CarritoTemp

pedidos_bp = Blueprint('pedidos', __name__)

PRECIOS_TAMANO  = {'Chica': 40, 'Mediana': 80, 'Grande': 120}
PRECIO_INGREDIENTE = 10
COOKIE_NAME     = 'cart_id'


# ── helpers ──────────────────────────────────────────────

def _get_cart_id():
    """Devuelve el cart_id de la cookie, o None si no existe."""
    return request.cookies.get(COOKIE_NAME)


def _ensure_cart_id(response):
    """Si la cookie no existe la crea y la añade a response."""
    if not request.cookies.get(COOKIE_NAME):
        new_id = str(uuid.uuid4())
        response.set_cookie(COOKIE_NAME, new_id, max_age=60 * 60 * 24)  # 24 h
        return new_id
    return request.cookies.get(COOKIE_NAME)


def _get_carrito(cart_id):
    """Recupera todos los ítems del carrito desde la BD."""
    if not cart_id:
        return []
    return CarritoTemp.query.filter_by(cart_id=cart_id).all()


# ── rutas ─────────────────────────────────────────────────

@pedidos_bp.route('/', methods=['GET'])
def index():
    from app.forms import PedidoForm
    form   = PedidoForm()
    cart_id = _get_cart_id()
    carrito = _get_carrito(cart_id)

    # Rellenar campos cliente con los datos del último ítem del carrito
    if carrito:
        ultimo = carrito[-1]
        form.nombre.data    = ultimo.nombre
        form.direccion.data = ultimo.direccion
        form.telefono.data  = ultimo.telefono
        form.fecha_dia.data = ultimo.fecha_dia
        form.fecha_mes.data = str(ultimo.fecha_mes) if ultimo.fecha_mes else '1'
        form.fecha_anio.data = ultimo.fecha_anio

    hoy = datetime.date.today()
    ventas_raw = db.session.query(Pedido, Cliente).join(
        Cliente, Pedido.id_cliente == Cliente.id_cliente
    ).filter(Pedido.fecha == hoy).all()

    ventas_hoy = [{'pedido': p, 'cliente': c} for p, c in ventas_raw]
    total_hoy  = sum(float(v['pedido'].total or 0) for v in ventas_hoy)

    resp = make_response(
        render_template('index.html', form=form, carrito=carrito,
                        ventas_hoy=ventas_hoy, total_hoy=total_hoy)
    )
    # Garantiza que exista la cookie aunque el usuario no haya agregado nada aún
    _ensure_cart_id(resp)
    return resp


@pedidos_bp.route('/agregar', methods=['POST'])
def agregar():
    from app.forms import PedidoForm
    form = PedidoForm()

    if form.validate_on_submit():
        cart_id = request.cookies.get(COOKIE_NAME) or str(uuid.uuid4())

        tamano          = form.tamano.data
        ingredientes_sel = form.ingredientes.data or []
        num_pizzas      = form.num_pizzas.data

        precio_base = PRECIOS_TAMANO.get(tamano, 0)
        precio_ingr = len(ingredientes_sel) * PRECIO_INGREDIENTE
        subtotal    = (precio_base + precio_ingr) * num_pizzas

        item = CarritoTemp(
            cart_id      = cart_id,
            tamano       = tamano,
            ingredientes = ', '.join(ingredientes_sel) if ingredientes_sel else 'Sin ingredientes',
            num_pizzas   = num_pizzas,
            subtotal     = subtotal,
            nombre       = form.nombre.data,
            direccion    = form.direccion.data,
            telefono     = form.telefono.data,
            fecha_dia    = form.fecha_dia.data,
            fecha_mes    = int(form.fecha_mes.data),
            fecha_anio   = form.fecha_anio.data,
        )
        db.session.add(item)
        db.session.commit()

        resp = make_response(redirect(url_for('pedidos.index')))
        resp.set_cookie(COOKIE_NAME, cart_id, max_age=60 * 60 * 24)
        return resp
    else:
        for field, errors in form.errors.items():
            for error in errors:
                flash(f'Error en {field}: {error}', 'danger')

    return redirect(url_for('pedidos.index'))


@pedidos_bp.route('/quitar/<int:item_id>', methods=['POST'])
def quitar(item_id):
    cart_id = _get_cart_id()
    if cart_id:
        item = CarritoTemp.query.filter_by(id=item_id, cart_id=cart_id).first()
        if item:
            db.session.delete(item)
            db.session.commit()
    return redirect(url_for('pedidos.index'))


@pedidos_bp.route('/terminar', methods=['POST'])
def terminar():
    cart_id = _get_cart_id()
    carrito = _get_carrito(cart_id)

    if not carrito:
        flash('No hay pizzas en el pedido.', 'warning')
        return redirect(url_for('pedidos.index'))

    primero = carrito[0]
    if not primero.nombre:
        flash('Faltan datos del cliente.', 'warning')
        return redirect(url_for('pedidos.index'))

    total = sum(float(item.subtotal or 0) for item in carrito)

    cliente = Cliente.query.filter_by(
        nombre=primero.nombre,
        telefono=primero.telefono
    ).first()

    if not cliente:
        cliente = Cliente(
            nombre    = primero.nombre,
            direccion = primero.direccion,
            telefono  = primero.telefono,
        )
        db.session.add(cliente)
        db.session.flush()

    try:
        fecha = datetime.date(primero.fecha_anio, primero.fecha_mes, primero.fecha_dia)
    except (ValueError, TypeError):
        fecha = datetime.date.today()

    pedido = Pedido(id_cliente=cliente.id_cliente, fecha=fecha, total=total)
    db.session.add(pedido)
    db.session.flush()

    for item in carrito:
        pizza = Pizza.query.filter_by(tamano=item.tamano).first()
        if not pizza:
            pizza = Pizza.query.first()

        detalle = DetallePedido(
            id_pedido = pedido.id_pedido,
            id_pizza  = pizza.id_pizza,
            cantidad  = item.num_pizzas,
            subtotal  = item.subtotal,
        )
        db.session.add(detalle)

    db.session.commit()

    flash(f'Pedido terminado. Total a pagar: ${total:.2f}', 'success')
    resp = make_response(redirect(url_for('pedidos.index')))
    resp.delete_cookie(COOKIE_NAME)
    return resp
