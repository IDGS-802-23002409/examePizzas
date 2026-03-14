"""
crear_respaldo.py
Genera un respaldo SQL de la base de datos 'pizzas'
y lo guarda en la carpeta respaldos/ con marca de tiempo.
"""
import pymysql
import datetime
import os

# Configuración de conexión
HOST     = 'localhost'
USUARIO  = 'root'
PASSWORD = 'root'
BASE     = 'pizzas'

RESPALDOS_DIR = os.path.join(os.path.dirname(__file__), 'respaldos')
os.makedirs(RESPALDOS_DIR, exist_ok=True)


def exportar_tabla(cursor, tabla):
    lines = []
    cursor.execute(f"SHOW CREATE TABLE `{tabla}`")
    create = cursor.fetchone()[1]
    lines.append(f"-- Tabla: {tabla}")
    lines.append(f"DROP TABLE IF EXISTS `{tabla}`;")
    lines.append(create + ";")
    lines.append("")

    cursor.execute(f"SELECT * FROM `{tabla}`")
    filas = cursor.fetchall()
    columnas = [d[0] for d in cursor.description]
    for fila in filas:
        valores = []
        for v in fila:
            if v is None:
                valores.append("NULL")
            else:
                valores.append("'" + str(v).replace("'", "''") + "'")
        cols_str = ', '.join(f"`{c}`" for c in columnas)
        vals_str = ', '.join(valores)
        lines.append(f"INSERT INTO `{tabla}` ({cols_str}) VALUES ({vals_str});")
    lines.append("")
    return '\n'.join(lines)


def crear_respaldo():
    conn = pymysql.connect(host=HOST, user=USUARIO, password=PASSWORD, database=BASE)
    cursor = conn.cursor()

    ahora = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    nombre_archivo = os.path.join(RESPALDOS_DIR, f'pizzas_{ahora}.sql')

    cursor.execute("SHOW TABLES")
    tablas = [row[0] for row in cursor.fetchall()]

    with open(nombre_archivo, 'w', encoding='utf-8') as f:
        f.write(f"-- Respaldo de la base de datos: {BASE}\n")
        f.write(f"-- Fecha: {datetime.datetime.now()}\n\n")
        f.write(f"CREATE DATABASE IF NOT EXISTS `{BASE}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;\n")
        f.write(f"USE `{BASE}`;\n\n")
        f.write("SET FOREIGN_KEY_CHECKS = 0;\n\n")
        for tabla in tablas:
            f.write(exportar_tabla(cursor, tabla))
            f.write("\n")
        f.write("SET FOREIGN_KEY_CHECKS = 1;\n")

    cursor.close()
    conn.close()
    print(f"Respaldo generado: {nombre_archivo}")
    return nombre_archivo


if __name__ == '__main__':
    crear_respaldo()
