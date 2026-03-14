from flask import Blueprint, render_template, request
from app.models import db, Pedido, Cliente, DetallePedido, Pizza
from app.forms import ConsultaDiaForm, ConsultaMesForm
from sqlalchemy import func
import datetime

consultas_bp = Blueprint('consultas', __name__, url_prefix='/consultas')

DIAS_SEMANA = {
    'lunes': 0, 'martes': 1, 'miercoles': 2, 'miércoles': 2,
    'jueves': 3, 'viernes': 4, 'sabado': 5, 'sábado': 5, 'domingo': 6
}

MESES = {
    '1': 'Enero', '2': 'Febrero', '3': 'Marzo', '4': 'Abril',
    '5': 'Mayo', '6': 'Junio', '7': 'Julio', '8': 'Agosto',
    '9': 'Septiembre', '10': 'Octubre', '11': 'Noviembre', '12': 'Diciembre'
}


@consultas_bp.route('/', methods=['GET', 'POST'])
def index():
    form_dia = ConsultaDiaForm()
    form_mes = ConsultaMesForm()
    return render_template('consultas.html', form_dia=form_dia, form_mes=form_mes)


@consultas_bp.route('/dia', methods=['GET', 'POST'])
def por_dia():
    form_dia = ConsultaDiaForm()
    form_mes = ConsultaMesForm()
    resultados = []
    dia_nombre = ''
    total_dia = 0

    if form_dia.validate_on_submit():
        dia_nombre = form_dia.dia.data
        num_dia = DIAS_SEMANA.get(dia_nombre.lower())

        if num_dia is not None:
            todos = db.session.query(Pedido, Cliente).join(
                Cliente, Pedido.id_cliente == Cliente.id_cliente
            ).all()

            for pedido, cliente in todos:
                if pedido.fecha and pedido.fecha.weekday() == num_dia:
                    resultados.append({'pedido': pedido, 'cliente': cliente})
                    total_dia += float(pedido.total or 0)

    return render_template('consultas.html',
                           form_dia=form_dia, form_mes=form_mes,
                           resultados_dia=resultados,
                           dia_nombre=dia_nombre,
                           total_dia=total_dia)


@consultas_bp.route('/mes', methods=['GET', 'POST'])
def por_mes():
    form_dia = ConsultaDiaForm()
    form_mes = ConsultaMesForm()
    resultados = []
    mes_nombre = ''
    total_mes = 0

    if form_mes.validate_on_submit():
        mes_num = form_mes.mes.data
        mes_nombre = MESES.get(mes_num, '')

        todos = db.session.query(Pedido, Cliente).join(
            Cliente, Pedido.id_cliente == Cliente.id_cliente
        ).filter(
            func.month(Pedido.fecha) == int(mes_num)
        ).all()

        for pedido, cliente in todos:
            resultados.append({'pedido': pedido, 'cliente': cliente})
            total_mes += float(pedido.total or 0)

    return render_template('consultas.html',
                           form_dia=form_dia, form_mes=form_mes,
                           resultados_mes=resultados,
                           mes_nombre=mes_nombre,
                           total_mes=total_mes)


@consultas_bp.route('/detalle/<int:id_pedido>')
def detalle(id_pedido):
    pedido = Pedido.query.get_or_404(id_pedido)
    cliente = Cliente.query.get(pedido.id_cliente)
    detalles = db.session.query(DetallePedido, Pizza).join(
        Pizza, DetallePedido.id_pizza == Pizza.id_pizza
    ).filter(DetallePedido.id_pedido == id_pedido).all()

    return render_template('detalle_venta.html',
                           pedido=pedido, cliente=cliente, detalles=detalles)
