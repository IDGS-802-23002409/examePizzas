from flask import Blueprint, render_template, redirect, url_for, session, flash, request
from app.models import db, Pizza, Cliente, Pedido, DetallePedido
from app.forms import PedidoForm
import datetime

pedidos_bp = Blueprint('pedidos', __name__)

PRECIOS_TAMANO = {'Chica': 40, 'Mediana': 80, 'Grande': 120}
PRECIO_INGREDIENTE = 10


@pedidos_bp.route('/', methods=['GET', 'POST'])
def index():
    form = PedidoForm()
    carrito = session.get('carrito', [])

    hoy = datetime.date.today()
    ventas_raw = db.session.query(Pedido, Cliente).join(
        Cliente, Pedido.id_cliente == Cliente.id_cliente
    ).filter(Pedido.fecha == hoy).all()

    ventas_hoy = [{'pedido': p, 'cliente': c} for p, c in ventas_raw]
    total_hoy = sum(float(v['pedido'].total or 0) for v in ventas_hoy)

    return render_template('index.html', form=form, carrito=carrito,
                           ventas_hoy=ventas_hoy, total_hoy=total_hoy)


@pedidos_bp.route('/agregar', methods=['POST'])
def agregar():
    form = PedidoForm()
    carrito = session.get('carrito', [])

    if form.validate_on_submit():
        tamano = form.tamano.data
        ingredientes_sel = form.ingredientes.data or []
        num_pizzas = form.num_pizzas.data

        precio_base = PRECIOS_TAMANO.get(tamano, 0)
        precio_ingr = len(ingredientes_sel) * PRECIO_INGREDIENTE
        subtotal = (precio_base + precio_ingr) * num_pizzas

        item = {
            'tamano': tamano,
            'ingredientes': ', '.join(ingredientes_sel) if ingredientes_sel else 'Sin ingredientes',
            'num_pizzas': num_pizzas,
            'subtotal': subtotal
        }
        carrito.append(item)
        session['carrito'] = carrito

        # Guardar datos del cliente en sesión
        session['cliente'] = {
            'nombre': form.nombre.data,
            'direccion': form.direccion.data,
            'telefono': form.telefono.data,
            'fecha_dia': form.fecha_dia.data,
            'fecha_mes': form.fecha_mes.data,
            'fecha_anio': form.fecha_anio.data
        }
    else:
        for field, errors in form.errors.items():
            for error in errors:
                flash(f'Error en {field}: {error}', 'danger')

    return redirect(url_for('pedidos.index'))


@pedidos_bp.route('/quitar/<int:indice>', methods=['POST'])
def quitar(indice):
    carrito = session.get('carrito', [])
    if 0 <= indice < len(carrito):
        carrito.pop(indice)
        session['carrito'] = carrito
    return redirect(url_for('pedidos.index'))


@pedidos_bp.route('/terminar', methods=['POST'])
def terminar():
    carrito = session.get('carrito', [])
    cliente_data = session.get('cliente', {})

    if not carrito:
        flash('No hay pizzas en el pedido.', 'warning')
        return redirect(url_for('pedidos.index'))

    if not cliente_data:
        flash('Faltan datos del cliente.', 'warning')
        return redirect(url_for('pedidos.index'))

    total = sum(item['subtotal'] for item in carrito)

    cliente = Cliente.query.filter_by(
        nombre=cliente_data['nombre'],
        telefono=cliente_data['telefono']
    ).first()

    if not cliente:
        cliente = Cliente(
            nombre=cliente_data['nombre'],
            direccion=cliente_data['direccion'],
            telefono=cliente_data['telefono']
        )
        db.session.add(cliente)
        db.session.flush()

    try:
        dia = int(cliente_data['fecha_dia'])
        mes = int(cliente_data['fecha_mes'])
        anio = int(cliente_data['fecha_anio'])
        fecha = datetime.date(anio, mes, dia)
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
            id_pedido=pedido.id_pedido,
            id_pizza=pizza.id_pizza,
            cantidad=item['num_pizzas'],
            subtotal=item['subtotal']
        )
        db.session.add(detalle)

    db.session.commit()

    session.pop('carrito', None)
    session.pop('cliente', None)

    flash(f'Pedido terminado. Total a pagar: ${total:.2f}', 'success')
    return redirect(url_for('pedidos.index'))
