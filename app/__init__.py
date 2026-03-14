from flask import Flask
from flask_wtf.csrf import CSRFProtect
from .models import db
from config import Config

csrf = CSRFProtect()


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    csrf.init_app(app)

    from .blueprints.pedidos import pedidos_bp
    from .blueprints.consultas import consultas_bp

    app.register_blueprint(pedidos_bp)
    app.register_blueprint(consultas_bp)

    with app.app_context():
        db.create_all()
        _seed_pizzas()

    return app


def _seed_pizzas():
    from .models import Pizza
    if Pizza.query.count() == 0:
        pizzas = [
            Pizza(tamano='Chica',   ingredientes='',  precio=40),
            Pizza(tamano='Mediana', ingredientes='',  precio=80),
            Pizza(tamano='Grande',  ingredientes='',  precio=120),
        ]
        db.session.add_all(pizzas)
        db.session.commit()
