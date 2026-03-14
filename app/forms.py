from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, RadioField, SelectMultipleField, widgets, SelectField
from wtforms.validators import DataRequired, Optional, NumberRange


class MultiCheckboxField(SelectMultipleField):
    widget = widgets.ListWidget(prefix_label=False)
    option_widget = widgets.CheckboxInput()


class PedidoForm(FlaskForm):
    nombre = StringField('Nombre', validators=[DataRequired()])
    direccion = StringField('Dirección', validators=[DataRequired()])
    telefono = StringField('Teléfono', validators=[DataRequired()])
    fecha_dia = IntegerField('Día', validators=[DataRequired(), NumberRange(min=1, max=31)])
    fecha_mes = SelectField('Mes', choices=[
        ('1', 'Enero'), ('2', 'Febrero'), ('3', 'Marzo'), ('4', 'Abril'),
        ('5', 'Mayo'), ('6', 'Junio'), ('7', 'Julio'), ('8', 'Agosto'),
        ('9', 'Septiembre'), ('10', 'Octubre'), ('11', 'Noviembre'), ('12', 'Diciembre')
    ])
    fecha_anio = IntegerField('Año', validators=[DataRequired(), NumberRange(min=2000, max=2100)])
    tamano = RadioField('Tamaño', choices=[
        ('Chica', 'Chica $40'),
        ('Mediana', 'Mediana $80'),
        ('Grande', 'Grande $120')
    ], validators=[DataRequired()])
    ingredientes = MultiCheckboxField('Ingredientes', choices=[
        ('Jamón', 'Jamón $10'),
        ('Piña', 'Piña $10'),
        ('Champiñones', 'Champiñones $10')
    ], validators=[Optional()])
    num_pizzas = IntegerField('Núm. Pizzas', validators=[DataRequired(), NumberRange(min=1)])


class ConsultaDiaForm(FlaskForm):
    dia = SelectField('Día de la semana', choices=[
        ('lunes', 'Lunes'), ('martes', 'Martes'), ('miercoles', 'Miércoles'),
        ('jueves', 'Jueves'), ('viernes', 'Viernes'), ('sabado', 'Sábado'),
        ('domingo', 'Domingo')
    ])


class ConsultaMesForm(FlaskForm):
    mes = SelectField('Mes', choices=[
        ('1', 'Enero'), ('2', 'Febrero'), ('3', 'Marzo'), ('4', 'Abril'),
        ('5', 'Mayo'), ('6', 'Junio'), ('7', 'Julio'), ('8', 'Agosto'),
        ('9', 'Septiembre'), ('10', 'Octubre'), ('11', 'Noviembre'), ('12', 'Diciembre')
    ])
