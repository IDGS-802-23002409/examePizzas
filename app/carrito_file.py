"""
carrito_file.py
Maneja el carrito temporal usando un archivo de texto JSON.
El archivo se guarda en la carpeta temp/ del proyecto.
"""
import json
import os

# Ruta del archivo temporal
_BASE = os.path.dirname(os.path.abspath(__file__))
TEMP_DIR  = os.path.join(_BASE, '..', 'temp')
TEMP_FILE = os.path.join(TEMP_DIR, 'carrito.json')


def _asegurar_directorio():
    os.makedirs(TEMP_DIR, exist_ok=True)


def leer_carrito():
    """Devuelve el diccionario guardado en carrito.json, o un carrito vacío."""
    _asegurar_directorio()
    if not os.path.exists(TEMP_FILE):
        return {'cliente': {}, 'items': []}
    try:
        with open(TEMP_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return {'cliente': {}, 'items': []}


def guardar_carrito(data):
    """Escribe el carrito en carrito.json."""
    _asegurar_directorio()
    with open(TEMP_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def agregar_item(cliente, tamano, ingredientes, num_pizzas, subtotal):
    """Añade un ítem al carrito y actualiza los datos del cliente."""
    data = leer_carrito()
    data['cliente'] = cliente
    item = {
        'tamano':       tamano,
        'ingredientes': ingredientes,
        'num_pizzas':   num_pizzas,
        'subtotal':     subtotal,
    }
    data['items'].append(item)
    guardar_carrito(data)


def quitar_item(indice):
    """Elimina el ítem en la posición `indice`."""
    data = leer_carrito()
    if 0 <= indice < len(data['items']):
        data['items'].pop(indice)
    guardar_carrito(data)


def limpiar_carrito():
    """Borra el archivo temporal (carrito vacío)."""
    if os.path.exists(TEMP_FILE):
        os.remove(TEMP_FILE)
