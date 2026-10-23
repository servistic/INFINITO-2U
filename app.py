from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    session,
    flash,
    jsonify,
    send_from_directory
)

import os
import sqlite3
import unicodedata
import json

try:
    import pymupdf as fitz
except ImportError:
    fitz = None

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

from base_datos import conectar, crear_base_datos
from chatbot import obtener_respuesta


# ============================================================
# CONFIGURACIÓN
# ============================================================

CARPETA_ACTUAL = os.path.dirname(
    os.path.abspath(__file__)
)

CARPETA_ASSETS = os.path.join(
    CARPETA_ACTUAL,
    "assets"
)

CARPETA_NORMATIVIDAD = os.path.join(
    CARPETA_ASSETS,
    "Normatividad"
)

CARPETA_MANUAL_CONVIVENCIA = os.path.join(
    CARPETA_ASSETS,
    "Manual de convivencia"
)

CARPETA_MANUAL_JURIDICO = os.path.join(
    CARPETA_ASSETS,
    "Manual juridico"
)


app = Flask(
    __name__,
    static_folder="static",
    template_folder="templates"
)

app.secret_key = os.getenv("SECRET_KEY", "INFINITO_2U_CLAVE_SECRETA_DEV")

# ============================================================
# INICIALIZAR BASE DE DATOS
# ============================================================

try:
    crear_base_datos()
except Exception as e:
    print(f"Nota: Base de datos ya existe o error al crear: {e}")

# ============================================================
# FUNCIONES GENERALES
# ============================================================

def normalizar(texto):

    if texto is None:
        return ""

    texto = str(texto).lower()

    texto = unicodedata.normalize(
        "NFD",
        texto
    )

    texto = "".join(
        caracter
        for caracter in texto
        if unicodedata.category(caracter) != "Mn"
    )

    return texto


# ============================================================
# OBTENER RESIDENTE DEL USUARIO LOGUEADO
# ============================================================

def obtener_residente_sesion():

    if "usuario" not in session:
        return None

    usuario_sesion = session.get("usuario")
    residente_id = session.get("residente_id")

    conexion = conectar()

    try:

        cursor = conexion.cursor()
        residente = None

        if residente_id:

            cursor.execute(
                """
                SELECT
                    residentes.id,
                    residentes.documento,
                    residentes.nombre,
                    residentes.telefono,
                    residentes.correo,
                    residentes.apartamento,
                    residentes.tipo,
                    residentes.estado,
                    usuarios.usuario
                FROM residentes
                LEFT JOIN usuarios
                    ON usuarios.residente_id = residentes.id
                WHERE residentes.id = ?
                """,
                (residente_id,)
            )

            residente = cursor.fetchone()

        if residente is None and usuario_sesion:

            cursor.execute(
                """
                SELECT
                    residentes.id,
                    residentes.documento,
                    residentes.nombre,
                    residentes.telefono,
                    residentes.correo,
                    residentes.apartamento,
                    residentes.tipo,
                    residentes.estado,
                    usuarios.usuario
                FROM usuarios
                INNER JOIN residentes
                    ON residentes.id = usuarios.residente_id
                WHERE usuarios.usuario = ?
                AND usuarios.rol = 'residente'
                AND usuarios.activo = 1
                """,
                (usuario_sesion,)
            )

            residente = cursor.fetchone()

        if residente:

            try:
                session["residente_id"] = residente["id"]
            except Exception:
                session["residente_id"] = residente[0]

    finally:
        conexion.close()

    return residente


# ============================================================
# PREPARAR BASE DE DATOS
# ============================================================

def preparar_base_datos():

    conexion = conectar()

    try:

        cursor = conexion.cursor()

        cursor.execute(
            "PRAGMA table_info(apartamentos)"
        )

        columnas = cursor.fetchall()
        nombres_columnas = []

        for columna in columnas:

            try:
                nombres_columnas.append(
                    columna["name"]
                )
            except Exception:
                nombres_columnas.append(
                    columna[1]
                )

        if "bloque" not in nombres_columnas:

            cursor.execute(
                """
                ALTER TABLE apartamentos
                ADD COLUMN bloque TEXT
                """
            )

        if "piso" not in nombres_columnas:

            cursor.execute(
                """
                ALTER TABLE apartamentos
                ADD COLUMN piso TEXT
                """
            )

        # ----------------------------------------------------
        # DATOS DEL VEHÍCULO
        # Se agregan solo si las columnas todavía no existen.
        # Esto conserva los apartamentos existentes.
        # ----------------------------------------------------

        columnas_vehiculo = {
            "vehiculo_tipo": "TEXT",
            "vehiculo_color": "TEXT",
            "vehiculo_placa": "TEXT",
            "vehiculo_cilindraje": "TEXT",
            "vehiculo_soat": "TEXT",
            "vehiculo_propietario": "TEXT"
        }

        for nombre_columna, tipo_columna in columnas_vehiculo.items():

            if nombre_columna not in nombres_columnas:

                cursor.execute(
                    f"""
                    ALTER TABLE apartamentos
                    ADD COLUMN {nombre_columna} {tipo_columna}
                    """
                )

        cursor.execute(
            """
            SELECT id
            FROM usuarios
            WHERE usuario = ?
            """,
            ("admin",)
        )

        admin = cursor.fetchone()

        if admin is None:

            cursor.execute(
                """
                INSERT INTO usuarios
                (
                    usuario,
                    contrasena,
                    rol,
                    residente_id,
                    activo
                )
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    "admin",
                    "admin123",
                    "admin",
                    None,
                    1
                )
            )

        conexion.commit()

    except Exception as error:

        conexion.rollback()

        print(
            "Advertencia preparando base de datos:",
            error
        )

    finally:
        conexion.close()


# ============================================================
# ASSETS
# ============================================================

@app.route("/assets/<path:filename>")
def assets(filename):

    return send_from_directory(
        CARPETA_ASSETS,
        filename
    )


# ============================================================
# LOGIN
# ============================================================

@app.route(
    "/",
    methods=["GET", "POST"]
)
@app.route(
    "/login",
    methods=["GET", "POST"]
)
def login():

    if request.method == "POST":

        usuario = request.form.get(
            "usuario",
            ""
        ).strip()

        contrasena = request.form.get(
            "contrasena",
            ""
        ).strip()

        if not usuario or not contrasena:

            flash(
                "Ingrese usuario y contraseña.",
                "error"
            )

            return render_template(
                "login.html"
            )

        conexion = conectar()

        try:

            cursor = conexion.cursor()

            cursor.execute(
                """
                SELECT
                    id,
                    usuario,
                    contrasena,
                    rol,
                    residente_id,
                    activo
                FROM usuarios
                WHERE usuario = ?
                AND contrasena = ?
                AND activo = 1
                """,
                (
                    usuario,
                    contrasena
                )
            )

            usuario_db = cursor.fetchone()

        finally:
            conexion.close()

        if usuario_db:

            session.clear()

            try:

                session["usuario"] = usuario_db["usuario"]
                session["rol"] = usuario_db["rol"]
                session["usuario_id"] = usuario_db["id"]
                session["residente_id"] = usuario_db["residente_id"]

            except Exception:

                session["usuario"] = usuario_db[1]
                session["rol"] = usuario_db[3]
                session["usuario_id"] = usuario_db[0]
                session["residente_id"] = usuario_db[4]

            if session.get("rol") == "admin":

                return redirect(
                    url_for("panel_admin")
                )

            return redirect(
                url_for("panel_residente")
            )

        if (
            usuario == "admin"
            and contrasena == "admin123"
        ):

            session.clear()

            session["usuario"] = "admin"
            session["rol"] = "admin"
            session["usuario_id"] = None
            session["residente_id"] = None

            return redirect(
                url_for("panel_admin")
            )

        flash(
            "Usuario o contraseña incorrectos.",
            "error"
        )

    return render_template(
        "login.html"
    )


# ============================================================
# CERRAR SESIÓN
# ============================================================

@app.route("/logout")
def logout():

    session.clear()

    return redirect(
        url_for("login")
    )


# ============================================================
# REGISTRO
# ============================================================

@app.route(
    "/registro",
    methods=["GET", "POST"]
)
def registro():

    if request.method == "POST":

        documento = request.form.get(
            "documento",
            ""
        ).strip()

        nombre = request.form.get(
            "nombre",
            ""
        ).strip()

        telefono = request.form.get(
            "telefono",
            ""
        ).strip()

        correo = request.form.get(
            "correo",
            ""
        ).strip()

        apartamento = request.form.get(
            "apartamento",
            ""
        ).strip()

        tipo = request.form.get(
            "tipo",
            "Residente"
        ).strip()

        usuario = request.form.get(
            "usuario",
            ""
        ).strip()

        contrasena = request.form.get(
            "contrasena",
            ""
        ).strip()

        if not documento or not nombre:

            flash(
                "Documento y nombre son obligatorios.",
                "error"
            )

            return render_template(
                "registro.html"
            )

        if not usuario:
            usuario = "residente" + documento[-4:]

        if not contrasena:
            contrasena = "1234"

        conexion = conectar()

        try:

            cursor = conexion.cursor()

            cursor.execute(
                """
                INSERT INTO residentes
                (
                    documento,
                    nombre,
                    telefono,
                    correo,
                    apartamento,
                    tipo,
                    estado
                )
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    documento,
                    nombre,
                    telefono,
                    correo,
                    apartamento,
                    tipo,
                    "Activo"
                )
            )

            residente_id = cursor.lastrowid

            cursor.execute(
                """
                INSERT INTO usuarios
                (
                    usuario,
                    contrasena,
                    rol,
                    residente_id,
                    activo
                )
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    usuario,
                    contrasena,
                    "residente",
                    residente_id,
                    1
                )
            )

            conexion.commit()

            flash(
                "Registro realizado correctamente.",
                "success"
            )

            return redirect(
                url_for("login")
            )

        except sqlite3.IntegrityError:

            conexion.rollback()

            flash(
                "El documento o usuario ya existe.",
                "error"
            )

        except Exception as error:

            conexion.rollback()

            flash(
                f"Error en el registro: {error}",
                "error"
            )

        finally:
            conexion.close()

    return render_template(
        "registro.html"
    )


# ============================================================
# PANEL USUARIO
# ============================================================

@app.route("/panel_usuario")
def panel_usuario():

    if "usuario" not in session:
        return redirect(url_for("login"))

    if session.get("rol") == "admin":
        return redirect(url_for("panel_admin"))

    return redirect(url_for("panel_residente"))


# ============================================================
# PANEL ADMIN
# ============================================================

@app.route("/panel_admin")
def panel_admin():

    if "usuario" not in session:
        return redirect(url_for("login"))

    if session.get("rol") != "admin":
        return redirect(url_for("panel_residente"))

    conexion = conectar()

    try:

        cursor = conexion.cursor()

        cursor.execute(
            """
            SELECT COUNT(*) AS total
            FROM residentes
            """
        )

        total_residentes = cursor.fetchone()["total"]

        cursor.execute(
            """
            SELECT COUNT(*) AS total
            FROM apartamentos
            """
        )

        total_apartamentos = cursor.fetchone()["total"]

    except Exception:

        total_residentes = 0
        total_apartamentos = 0

    finally:
        conexion.close()

    return render_template(
        "panel_admin.html",
        total_residentes=total_residentes,
        total_apartamentos=total_apartamentos
    )


# ============================================================
# PANEL RESIDENTE
# ============================================================

@app.route("/panel_residente")
def panel_residente():

    if "usuario" not in session:
        return redirect(url_for("login"))

    if session.get("rol") == "admin":
        return redirect(url_for("panel_admin"))

    residente = obtener_residente_sesion()

    return render_template(
        "panel_usuario.html",
        residente=residente,
        usuario=session.get("usuario")
    )


# ============================================================
# RESIDENTES
# ============================================================

@app.route("/residentes")
def residentes():

    if "usuario" not in session:
        return redirect(url_for("login"))

    if session.get("rol") != "admin":
        return redirect(url_for("panel_residente"))

    conexion = conectar()

    try:

        cursor = conexion.cursor()

        cursor.execute(
            """
            SELECT
                residentes.id AS id_residente,
                residentes.documento,
                residentes.nombre,
                residentes.telefono,
                residentes.correo,
                residentes.apartamento,
                residentes.tipo,
                residentes.estado,
                usuarios.usuario,
                usuarios.contrasena
            FROM residentes
            LEFT JOIN usuarios
                ON usuarios.residente_id = residentes.id
            ORDER BY residentes.id DESC
            """
        )

        lista_residentes = cursor.fetchall()

    finally:
        conexion.close()

    return render_template(
        "residentes.html",
        residentes=lista_residentes
    )


# ============================================================
# AGREGAR RESIDENTE - ADMIN
# ============================================================

@app.route(
    "/residentes/agregar",
    methods=["GET", "POST"]
)
@app.route(
    "/agregar_residente",
    methods=["GET", "POST"]
)
def agregar_residente():

    if "usuario" not in session:
        return redirect(url_for("login"))

    if session.get("rol") != "admin":
        return redirect(url_for("panel_residente"))

    if request.method == "POST":

        documento = request.form.get("documento", "").strip()
        nombre = request.form.get("nombre", "").strip()
        telefono = request.form.get("telefono", "").strip()
        correo = request.form.get("correo", "").strip()
        apartamento = request.form.get("apartamento", "").strip()
        tipo = request.form.get("tipo", "Residente").strip()
        usuario = request.form.get("usuario", "").strip()
        contrasena = request.form.get("contrasena", "").strip()

        if not documento or not nombre:

            flash(
                "Documento y nombre son obligatorios.",
                "error"
            )

            return render_template(
                "crear_residente.html"
            )

        if not usuario:
            usuario = "residente" + documento[-4:]

        if not contrasena:
            contrasena = "1234"

        conexion = conectar()

        try:

            cursor = conexion.cursor()

            cursor.execute(
                """
                INSERT INTO residentes
                (
                    documento,
                    nombre,
                    telefono,
                    correo,
                    apartamento,
                    tipo,
                    estado
                )
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    documento,
                    nombre,
                    telefono,
                    correo,
                    apartamento,
                    tipo,
                    "Activo"
                )
            )

            residente_id = cursor.lastrowid

            cursor.execute(
                """
                INSERT INTO usuarios
                (
                    usuario,
                    contrasena,
                    rol,
                    residente_id,
                    activo
                )
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    usuario,
                    contrasena,
                    "residente",
                    residente_id,
                    1
                )
            )

            conexion.commit()

            flash(
                "Residente creado correctamente.",
                "success"
            )

            return redirect(url_for("residentes"))

        except sqlite3.IntegrityError:

            conexion.rollback()

            flash(
                "El documento o usuario ya existe.",
                "error"
            )

        except Exception as error:

            conexion.rollback()

            flash(
                f"Error: {error}",
                "error"
            )

        finally:
            conexion.close()

    return render_template(
        "crear_residente.html"
    )


# ============================================================
# EDITAR RESIDENTE - ADMIN
# ============================================================

@app.route(
    "/residentes/editar/<int:id_residente>",
    methods=["GET", "POST"]
)
def editar_residente(id_residente):

    if "usuario" not in session:
        return redirect(url_for("login"))

    if session.get("rol") != "admin":
        return redirect(url_for("panel_residente"))

    conexion = conectar()

    try:

        cursor = conexion.cursor()

        if request.method == "POST":

            documento = request.form.get("documento", "").strip()
            nombre = request.form.get("nombre", "").strip()
            telefono = request.form.get("telefono", "").strip()
            correo = request.form.get("correo", "").strip()
            apartamento = request.form.get("apartamento", "").strip()
            tipo = request.form.get("tipo", "Residente").strip()
            estado = request.form.get("estado", "Activo").strip()
            usuario = request.form.get("usuario", "").strip()
            contrasena = request.form.get("contrasena", "").strip()

            cursor.execute(
                """
                UPDATE residentes
                SET
                    documento = ?,
                    nombre = ?,
                    telefono = ?,
                    correo = ?,
                    apartamento = ?,
                    tipo = ?,
                    estado = ?
                WHERE id = ?
                """,
                (
                    documento,
                    nombre,
                    telefono,
                    correo,
                    apartamento,
                    tipo,
                    estado,
                    id_residente
                )
            )

            if usuario:

                if contrasena:

                    cursor.execute(
                        """
                        UPDATE usuarios
                        SET
                            usuario = ?,
                            contrasena = ?
                        WHERE residente_id = ?
                        """,
                        (
                            usuario,
                            contrasena,
                            id_residente
                        )
                    )

                else:

                    cursor.execute(
                        """
                        UPDATE usuarios
                        SET usuario = ?
                        WHERE residente_id = ?
                        """,
                        (
                            usuario,
                            id_residente
                        )
                    )

            conexion.commit()

            flash(
                "Residente actualizado correctamente.",
                "success"
            )

            return redirect(url_for("residentes"))

        cursor.execute(
            """
            SELECT
                residentes.*,
                usuarios.usuario,
                usuarios.contrasena
            FROM residentes
            LEFT JOIN usuarios
                ON usuarios.residente_id = residentes.id
            WHERE residentes.id = ?
            """,
            (id_residente,)
        )

        residente = cursor.fetchone()

    finally:
        conexion.close()

    if not residente:

        flash(
            "Residente no encontrado.",
            "error"
        )

        return redirect(url_for("residentes"))

    return render_template(
        "crear_residente.html",
        residente=residente,
        editar=True
    )


# ============================================================
# ELIMINAR RESIDENTE - ADMIN
# ============================================================

@app.route(
    "/residentes/eliminar/<int:id_residente>",
    methods=["GET", "POST"]
)
@app.route(
    "/eliminar_residente/<int:id_residente>",
    methods=["GET", "POST"]
)
def eliminar_residente(id_residente):

    if "usuario" not in session:
        return redirect(url_for("login"))

    if session.get("rol") != "admin":
        return redirect(url_for("panel_residente"))

    conexion = conectar()

    try:

        cursor = conexion.cursor()

        cursor.execute(
            """
            DELETE FROM usuarios
            WHERE residente_id = ?
            """,
            (id_residente,)
        )

        cursor.execute(
            """
            DELETE FROM residentes
            WHERE id = ?
            """,
            (id_residente,)
        )

        conexion.commit()

        flash(
            "Residente eliminado correctamente.",
            "success"
        )

    except Exception as error:

        conexion.rollback()

        flash(
            f"No se pudo eliminar: {error}",
            "error"
        )

    finally:
        conexion.close()

    return redirect(url_for("residentes"))


# ============================================================
# DETALLE RESIDENTE
# ============================================================

@app.route("/residente/<int:id_residente>")
def detalle_residente(id_residente):

    if "usuario" not in session:
        return redirect(url_for("login"))

    conexion = conectar()

    try:

        cursor = conexion.cursor()

        cursor.execute(
            """
            SELECT
                residentes.*,
                usuarios.usuario,
                usuarios.contrasena
            FROM residentes
            LEFT JOIN usuarios
                ON usuarios.residente_id = residentes.id
            WHERE residentes.id = ?
            """,
            (id_residente,)
        )

        residente = cursor.fetchone()

    finally:
        conexion.close()

    if not residente:

        flash(
            "Residente no encontrado.",
            "error"
        )

        return redirect(url_for("residentes"))

    return render_template(
        "residente_detalle.html",
        residente=residente
    )


# ============================================================
# APARTAMENTOS - ADMIN
# ============================================================

@app.route("/apartamentos")
def apartamentos():

    if "usuario" not in session:
        return redirect(url_for("login"))

    if session.get("rol") != "admin":
        return redirect(url_for("panel_residente"))

    conexion = conectar()

    try:

        cursor = conexion.cursor()

        cursor.execute(
            """
            SELECT
                id AS id_apartamento,
                apartamento AS numero,
                bloque,
                piso,
                propietario,
                residente,
                area,
                habitaciones,
                parqueadero,
                estado,
                vehiculo_tipo,
                vehiculo_color,
                vehiculo_placa,
                vehiculo_cilindraje,
                vehiculo_soat,
                vehiculo_propietario
            FROM apartamentos
            ORDER BY id ASC
            """
        )

        lista_apartamentos = cursor.fetchall()

    finally:
        conexion.close()

    ruta_1 = os.path.join(
        CARPETA_ACTUAL,
        "templates",
        "apartamento.html"
    )

    if os.path.exists(ruta_1):
        plantilla = "apartamento.html"
    else:
        plantilla = "apartamentos.html"

    return render_template(
        plantilla,
        apartamentos=lista_apartamentos
    )


# ============================================================
# AGREGAR APARTAMENTO - ADMIN
# ============================================================

@app.route(
    "/apartamentos/agregar",
    methods=["GET", "POST"]
)
@app.route(
    "/agregar_apartamento",
    methods=["GET", "POST"]
)
def agregar_apartamento():

    if "usuario" not in session:
        return redirect(url_for("login"))

    if session.get("rol") != "admin":
        return redirect(url_for("panel_residente"))

    if request.method == "POST":

        numero = request.form.get(
            "numero",
            request.form.get("apartamento", "")
        ).strip()

        bloque = request.form.get("bloque", "").strip()
        piso = request.form.get("piso", "").strip()
        propietario = request.form.get("propietario", "").strip()
        residente = request.form.get("residente", propietario).strip()
        area = request.form.get("area", "").strip()
        habitaciones = request.form.get("habitaciones", "").strip()
        parqueadero = request.form.get("parqueadero", "").strip()
        estado = request.form.get("estado", "Ocupado").strip()

        vehiculo_tipo = request.form.get("vehiculo_tipo", "").strip()
        vehiculo_color = request.form.get("vehiculo_color", "").strip()
        vehiculo_placa = request.form.get("vehiculo_placa", "").strip().upper()
        vehiculo_cilindraje = request.form.get("vehiculo_cilindraje", "").strip()
        vehiculo_soat = request.form.get("vehiculo_soat", "").strip()
        vehiculo_propietario = request.form.get("vehiculo_propietario", "").strip()

        if not numero:

            flash(
                "El número del apartamento es obligatorio.",
                "error"
            )

            return render_template(
                "crear_apartamento.html"
            )

        conexion = conectar()

        try:

            cursor = conexion.cursor()

            cursor.execute(
                """
                INSERT INTO apartamentos
                (
                    apartamento,
                    bloque,
                    piso,
                    propietario,
                    residente,
                    area,
                    habitaciones,
                    parqueadero,
                    estado,
                    vehiculo_tipo,
                    vehiculo_color,
                    vehiculo_placa,
                    vehiculo_cilindraje,
                    vehiculo_soat,
                    vehiculo_propietario
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    numero,
                    bloque,
                    piso,
                    propietario,
                    residente,
                    float(area) if area else None,
                    int(habitaciones) if habitaciones else None,
                    parqueadero,
                    estado,
                    vehiculo_tipo,
                    vehiculo_color,
                    vehiculo_placa,
                    vehiculo_cilindraje,
                    vehiculo_soat,
                    vehiculo_propietario
                )
            )

            conexion.commit()

            flash(
                "Apartamento creado correctamente.",
                "success"
            )

            return redirect(url_for("apartamentos"))

        except sqlite3.IntegrityError:

            conexion.rollback()

            flash(
                "Ese apartamento ya existe.",
                "error"
            )

        except Exception as error:

            conexion.rollback()

            flash(
                f"Error: {error}",
                "error"
            )

        finally:
            conexion.close()

    return render_template(
        "crear_apartamento.html"
    )


# ============================================================
# EDITAR APARTAMENTO - ADMIN
# ============================================================

@app.route(
    "/apartamentos/editar/<int:id_apartamento>",
    methods=["GET", "POST"]
)
def editar_apartamento(id_apartamento):

    if "usuario" not in session:
        return redirect(url_for("login"))

    if session.get("rol") != "admin":
        return redirect(url_for("panel_residente"))

    conexion = conectar()

    try:

        cursor = conexion.cursor()

        if request.method == "POST":

            numero = request.form.get(
                "numero",
                request.form.get("apartamento", "")
            ).strip()

            bloque = request.form.get("bloque", "").strip()
            piso = request.form.get("piso", "").strip()
            propietario = request.form.get("propietario", "").strip()
            residente = request.form.get("residente", propietario).strip()
            area = request.form.get("area", "").strip()
            habitaciones = request.form.get("habitaciones", "").strip()
            parqueadero = request.form.get("parqueadero", "").strip()
            estado = request.form.get("estado", "Ocupado").strip()

            vehiculo_tipo = request.form.get("vehiculo_tipo", "").strip()
            vehiculo_color = request.form.get("vehiculo_color", "").strip()
            vehiculo_placa = request.form.get("vehiculo_placa", "").strip().upper()
            vehiculo_cilindraje = request.form.get("vehiculo_cilindraje", "").strip()
            vehiculo_soat = request.form.get("vehiculo_soat", "").strip()
            vehiculo_propietario = request.form.get("vehiculo_propietario", "").strip()

            cursor.execute(
                """
                UPDATE apartamentos
                SET
                    apartamento = ?,
                    bloque = ?,
                    piso = ?,
                    propietario = ?,
                    residente = ?,
                    area = ?,
                    habitaciones = ?,
                    parqueadero = ?,
                    estado = ?,
                    vehiculo_tipo = ?,
                    vehiculo_color = ?,
                    vehiculo_placa = ?,
                    vehiculo_cilindraje = ?,
                    vehiculo_soat = ?,
                    vehiculo_propietario = ?
                WHERE id = ?
                """,
                (
                    numero,
                    bloque,
                    piso,
                    propietario,
                    residente,
                    float(area) if area else None,
                    int(habitaciones) if habitaciones else None,
                    parqueadero,
                    estado,
                    vehiculo_tipo,
                    vehiculo_color,
                    vehiculo_placa,
                    vehiculo_cilindraje,
                    vehiculo_soat,
                    vehiculo_propietario,
                    id_apartamento
                )
            )

            conexion.commit()

            flash(
                "Apartamento actualizado correctamente.",
                "success"
            )

            return redirect(url_for("apartamentos"))

        cursor.execute(
            """
            SELECT
                id AS id_apartamento,
                apartamento AS numero,
                apartamento,
                bloque,
                piso,
                propietario,
                residente,
                area,
                habitaciones,
                parqueadero,
                estado,
                vehiculo_tipo,
                vehiculo_color,
                vehiculo_placa,
                vehiculo_cilindraje,
                vehiculo_soat,
                vehiculo_propietario
            FROM apartamentos
            WHERE id = ?
            """,
            (id_apartamento,)
        )

        apartamento = cursor.fetchone()

    finally:
        conexion.close()

    if not apartamento:

        flash(
            "Apartamento no encontrado.",
            "error"
        )

        return redirect(url_for("apartamentos"))

    return render_template(
        "crear_apartamento.html",
        apartamento=apartamento,
        editar=True
    )


# ============================================================
# ELIMINAR APARTAMENTO - ADMIN
# ============================================================

@app.route(
    "/apartamentos/eliminar/<int:id_apartamento>",
    methods=["GET", "POST"]
)
@app.route(
    "/eliminar_apartamento/<int:id_apartamento>",
    methods=["GET", "POST"]
)
def eliminar_apartamento(id_apartamento):

    if "usuario" not in session:
        return redirect(url_for("login"))

    if session.get("rol") != "admin":
        return redirect(url_for("panel_residente"))

    conexion = conectar()

    try:

        cursor = conexion.cursor()

        cursor.execute(
            """
            DELETE FROM apartamentos
            WHERE id = ?
            """,
            (id_apartamento,)
        )

        conexion.commit()

        flash(
            "Apartamento eliminado correctamente.",
            "success"
        )

    except Exception as error:

        conexion.rollback()

        flash(
            f"No se pudo eliminar: {error}",
            "error"
        )

    finally:
        conexion.close()

    return redirect(url_for("apartamentos"))


# ============================================================
# DETALLE APARTAMENTO
# ============================================================

@app.route("/apartamento/<int:id_apartamento>")
def detalle_apartamento(id_apartamento):

    if "usuario" not in session:
        return redirect(url_for("login"))

    conexion = conectar()

    try:

        cursor = conexion.cursor()

        cursor.execute(
            """
            SELECT
                id AS id_apartamento,
                apartamento AS numero,
                apartamento,
                bloque,
                piso,
                propietario,
                residente,
                area,
                habitaciones,
                parqueadero,
                estado,
                vehiculo_tipo,
                vehiculo_color,
                vehiculo_placa,
                vehiculo_cilindraje,
                vehiculo_soat,
                vehiculo_propietario
            FROM apartamentos
            WHERE id = ?
            """,
            (id_apartamento,)
        )

        apartamento = cursor.fetchone()

    finally:
        conexion.close()

    if not apartamento:

        flash(
            "Apartamento no encontrado.",
            "error"
        )

        return redirect(url_for("apartamentos"))

    return render_template(
        "apartamento_detalle.html",
        apartamento=apartamento
    )


# ============================================================
# ASIGNAR APARTAMENTO - ADMIN
# ============================================================

@app.route(
    "/residentes/asignar-apartamento/<int:id_residente>",
    methods=["GET", "POST"]
)
def asignar_apartamento(id_residente):

    if "usuario" not in session:
        return redirect(url_for("login"))

    if session.get("rol") != "admin":
        return redirect(url_for("panel_residente"))

    conexion = conectar()

    try:

        cursor = conexion.cursor()

        if request.method == "POST":

            apartamento = request.form.get(
                "apartamento",
                ""
            ).strip()

            cursor.execute(
                """
                UPDATE residentes
                SET apartamento = ?
                WHERE id = ?
                """,
                (
                    apartamento,
                    id_residente
                )
            )

            conexion.commit()

            flash(
                "Apartamento asignado correctamente.",
                "success"
            )

            return redirect(url_for("residentes"))

        cursor.execute(
            """
            SELECT *
            FROM residentes
            WHERE id = ?
            """,
            (id_residente,)
        )

        residente = cursor.fetchone()

        cursor.execute(
            """
            SELECT
                apartamento,
                bloque,
                piso,
                propietario,
                estado
            FROM apartamentos
            ORDER BY apartamento
            """
        )

        apartamentos_disponibles = cursor.fetchall()

    finally:
        conexion.close()

    return render_template(
        "asignar_apartamento.html",
        residente=residente,
        apartamentos=apartamentos_disponibles
    )


# ============================================================
# MI INFORMACIÓN
# ============================================================

@app.route("/mi_informacion")
def mi_informacion():

    if "usuario" not in session:
        return redirect(url_for("login"))

    if session.get("rol") == "admin":
        return redirect(url_for("panel_admin"))

    residente = obtener_residente_sesion()

    return render_template(
        "mi_informacion.html",
        residente=residente,
        usuario=session.get("usuario"),
        modo=None
    )


# ============================================================
# AGREGAR MI INFORMACIÓN
# ============================================================

@app.route(
    "/mi_informacion/agregar",
    methods=["GET", "POST"]
)
def agregar_mi_informacion():

    if "usuario" not in session:
        return redirect(url_for("login"))

    if session.get("rol") == "admin":
        return redirect(url_for("panel_admin"))

    residente_actual = obtener_residente_sesion()

    if residente_actual:

        flash(
            "Ya tienes información registrada.",
            "info"
        )

        return redirect(url_for("mi_informacion"))

    if request.method == "POST":

        documento = request.form.get("documento", "").strip()
        nombre = request.form.get("nombre", "").strip()
        telefono = request.form.get("telefono", "").strip()
        correo = request.form.get("correo", "").strip()
        apartamento = request.form.get("apartamento", "").strip()
        tipo = request.form.get("tipo", "Propietario").strip()

        if not documento or not nombre:

            flash(
                "El documento y el nombre son obligatorios.",
                "error"
            )

            return render_template(
                "mi_informacion.html",
                residente=None,
                usuario=session.get("usuario"),
                modo="agregar"
            )

        conexion = conectar()

        try:

            cursor = conexion.cursor()

            cursor.execute(
                """
                SELECT id
                FROM residentes
                WHERE documento = ?
                """,
                (documento,)
            )

            existente = cursor.fetchone()

            if existente:

                flash(
                    "Ya existe un residente con ese documento.",
                    "error"
                )

                return render_template(
                    "mi_informacion.html",
                    residente=None,
                    usuario=session.get("usuario"),
                    modo="agregar"
                )

            cursor.execute(
                """
                INSERT INTO residentes
                (
                    documento,
                    nombre,
                    telefono,
                    correo,
                    apartamento,
                    tipo,
                    estado
                )
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    documento,
                    nombre,
                    telefono,
                    correo,
                    apartamento,
                    tipo or "Propietario",
                    "Activo"
                )
            )

            residente_id = cursor.lastrowid
            usuario_id = session.get("usuario_id")

            if usuario_id:

                cursor.execute(
                    """
                    UPDATE usuarios
                    SET residente_id = ?
                    WHERE id = ?
                    """,
                    (
                        residente_id,
                        usuario_id
                    )
                )

            conexion.commit()

            session["residente_id"] = residente_id

            flash(
                "Tu información fue registrada correctamente.",
                "success"
            )

            return redirect(url_for("mi_informacion"))

        except sqlite3.IntegrityError:

            conexion.rollback()

            flash(
                "No fue posible registrar la información. "
                "El documento puede estar repetido.",
                "error"
            )

        except Exception as error:

            conexion.rollback()

            flash(
                f"Error: {error}",
                "error"
            )

        finally:
            conexion.close()

    return render_template(
        "mi_informacion.html",
        residente=None,
        usuario=session.get("usuario"),
        modo="agregar"
    )


# ============================================================
# EDITAR MI INFORMACIÓN
# ============================================================

@app.route(
    "/mi_informacion/editar",
    methods=["GET", "POST"]
)
def editar_mi_informacion():

    if "usuario" not in session:
        return redirect(url_for("login"))

    if session.get("rol") == "admin":
        return redirect(url_for("panel_admin"))

    residente = obtener_residente_sesion()

    if not residente:

        flash(
            "Primero debes registrar tu información.",
            "info"
        )

        return redirect(url_for("agregar_mi_informacion"))

    if request.method == "POST":

        documento = request.form.get("documento", "").strip()
        nombre = request.form.get("nombre", "").strip()
        telefono = request.form.get("telefono", "").strip()
        correo = request.form.get("correo", "").strip()
        apartamento = request.form.get("apartamento", "").strip()
        tipo = request.form.get("tipo", "Propietario").strip()

        if not documento or not nombre:

            flash(
                "El documento y el nombre son obligatorios.",
                "error"
            )

            return render_template(
                "mi_informacion.html",
                residente=residente,
                usuario=session.get("usuario"),
                modo="editar"
            )

        conexion = conectar()

        try:

            cursor = conexion.cursor()

            cursor.execute(
                """
                SELECT id
                FROM residentes
                WHERE documento = ?
                AND id != ?
                """,
                (
                    documento,
                    residente["id"]
                )
            )

            duplicado = cursor.fetchone()

            if duplicado:

                flash(
                    "Ese documento ya pertenece a otro residente.",
                    "error"
                )

                return render_template(
                    "mi_informacion.html",
                    residente=residente,
                    usuario=session.get("usuario"),
                    modo="editar"
                )

            cursor.execute(
                """
                UPDATE residentes
                SET
                    documento = ?,
                    nombre = ?,
                    telefono = ?,
                    correo = ?,
                    apartamento = ?,
                    tipo = ?
                WHERE id = ?
                """,
                (
                    documento,
                    nombre,
                    telefono,
                    correo,
                    apartamento,
                    tipo or "Propietario",
                    residente["id"]
                )
            )

            conexion.commit()

            flash(
                "Tu información fue actualizada correctamente.",
                "success"
            )

            return redirect(url_for("mi_informacion"))

        except sqlite3.IntegrityError:

            conexion.rollback()

            flash(
                "No se pudo actualizar la información.",
                "error"
            )

        except Exception as error:

            conexion.rollback()

            flash(
                f"Error: {error}",
                "error"
            )

        finally:
            conexion.close()

    return render_template(
        "mi_informacion.html",
        residente=residente,
        usuario=session.get("usuario"),
        modo="editar"
    )

# ============================================================
# ELIMINAR MI INFORMACIÓN
# ============================================================

@app.route(
    "/mi_informacion/eliminar",
    methods=["POST"]
)
def eliminar_mi_informacion():

    if "usuario" not in session:
        return redirect(url_for("login"))

    if session.get("rol") == "admin":
        return redirect(url_for("panel_admin"))

    residente = obtener_residente_sesion()

    if not residente:

        flash(
            "No tienes información registrada.",
            "info"
        )

        return redirect(url_for("mi_informacion"))

    conexion = conectar()

    try:

        cursor = conexion.cursor()
        usuario_id = session.get("usuario_id")

        if usuario_id:

            cursor.execute(
                """
                UPDATE usuarios
                SET residente_id = NULL
                WHERE id = ?
                """,
                (usuario_id,)
            )

        cursor.execute(
            """
            DELETE FROM residentes
            WHERE id = ?
            """,
            (residente["id"],)
        )

        conexion.commit()

        session["residente_id"] = None

        flash(
            "Tu información fue eliminada correctamente.",
            "success"
        )

    except Exception as error:

        conexion.rollback()

        flash(
            f"No se pudo eliminar la información: {error}",
            "error"
        )

    finally:
        conexion.close()

    return redirect(url_for("mi_informacion"))


# ============================================================
# MI APARTAMENTO
# ============================================================

@app.route("/mi_apartamento")
def mi_apartamento():

    if "usuario" not in session:
        return redirect(url_for("login"))

    if session.get("rol") == "admin":
        return redirect(url_for("panel_admin"))

    residente = obtener_residente_sesion()
    apartamento = None

    if residente:

        try:
            numero = residente["apartamento"]
        except Exception:
            numero = residente[5]

        if numero:

            conexion = conectar()

            try:

                cursor = conexion.cursor()

                cursor.execute(
                    """
                    SELECT
                        id AS id_apartamento,
                        apartamento AS numero,
                        apartamento,
                        bloque,
                        piso,
                        propietario,
                        residente,
                        area,
                        habitaciones,
                        parqueadero,
                        estado,
                        vehiculo_tipo,
                        vehiculo_color,
                        vehiculo_placa,
                        vehiculo_cilindraje,
                        vehiculo_soat,
                        vehiculo_propietario
                    FROM apartamentos
                    WHERE apartamento = ?
                    """,
                    (numero,)
                )

                apartamento = cursor.fetchone()

            finally:
                conexion.close()

    return render_template(
        "mi_apartamento.html",
        apartamento=apartamento,
        residente=residente,
        usuario=session.get("usuario"),
        modo=None
    )


# ============================================================
# AGREGAR MI APARTAMENTO
# ============================================================

@app.route(
    "/mi_apartamento/agregar",
    methods=["GET", "POST"]
)
def agregar_mi_apartamento():

    if "usuario" not in session:
        return redirect(url_for("login"))

    if session.get("rol") == "admin":
        return redirect(url_for("panel_admin"))

    residente = obtener_residente_sesion()

    if not residente:

        flash(
            "Primero debes registrar tu información personal.",
            "error"
        )

        return redirect(url_for("agregar_mi_informacion"))

    if residente["apartamento"]:

        flash(
            "Ya tienes un apartamento asociado.",
            "info"
        )

        return redirect(url_for("mi_apartamento"))

    if request.method == "POST":

        numero = request.form.get("apartamento", "").strip()
        bloque = request.form.get("bloque", "").strip()
        piso = request.form.get("piso", "").strip()
        propietario = request.form.get("propietario", "").strip()
        residente_nombre = request.form.get("residente", "").strip()
        area = request.form.get("area", "").strip()
        habitaciones = request.form.get("habitaciones", "").strip()
        parqueadero = request.form.get("parqueadero", "").strip()
        estado = request.form.get("estado", "Ocupado").strip()

        vehiculo_tipo = request.form.get("vehiculo_tipo", "").strip()
        vehiculo_color = request.form.get("vehiculo_color", "").strip()
        vehiculo_placa = request.form.get("vehiculo_placa", "").strip().upper()
        vehiculo_cilindraje = request.form.get("vehiculo_cilindraje", "").strip()
        vehiculo_soat = request.form.get("vehiculo_soat", "").strip()
        vehiculo_propietario = request.form.get("vehiculo_propietario", "").strip()

        if not numero:

            flash(
                "El número del apartamento es obligatorio.",
                "error"
            )

            return render_template(
                "mi_apartamento.html",
                residente=residente,
                apartamento=None,
                usuario=session.get("usuario"),
                modo="agregar"
            )

        if not propietario:
            propietario = residente["nombre"]

        if not residente_nombre:
            residente_nombre = residente["nombre"]

        conexion = conectar()

        try:

            cursor = conexion.cursor()

            cursor.execute(
                """
                SELECT id
                FROM apartamentos
                WHERE apartamento = ?
                """,
                (numero,)
            )

            existente = cursor.fetchone()

            if existente:

                flash(
                    "Ese apartamento ya está registrado.",
                    "error"
                )

                return render_template(
                    "mi_apartamento.html",
                    residente=residente,
                    apartamento=None,
                    usuario=session.get("usuario"),
                    modo="agregar"
                )

            area_valor = float(area) if area else None
            habitaciones_valor = int(habitaciones) if habitaciones else None

            cursor.execute(
                """
                INSERT INTO apartamentos
                (
                    apartamento,
                    propietario,
                    residente,
                    area,
                    habitaciones,
                    parqueadero,
                    estado,
                    bloque,
                    piso,
                    vehiculo_tipo,
                    vehiculo_color,
                    vehiculo_placa,
                    vehiculo_cilindraje,
                    vehiculo_soat,
                    vehiculo_propietario
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    numero,
                    propietario,
                    residente_nombre,
                    area_valor,
                    habitaciones_valor,
                    parqueadero,
                    estado or "Ocupado",
                    bloque,
                    piso,
                    vehiculo_tipo,
                    vehiculo_color,
                    vehiculo_placa,
                    vehiculo_cilindraje,
                    vehiculo_soat,
                    vehiculo_propietario
                )
            )

            cursor.execute(
                """
                UPDATE residentes
                SET apartamento = ?
                WHERE id = ?
                """,
                (
                    numero,
                    residente["id"]
                )
            )

            conexion.commit()

            flash(
                "Tu apartamento fue registrado correctamente.",
                "success"
            )

            return redirect(url_for("mi_apartamento"))

        except sqlite3.IntegrityError:

            conexion.rollback()

            flash(
                "No se pudo registrar el apartamento. "
                "Ese número puede estar ocupado.",
                "error"
            )

        except (ValueError, TypeError) as error:

            conexion.rollback()

            flash(
                f"Revisa los valores numéricos: {error}",
                "error"
            )

        except Exception as error:

            conexion.rollback()

            flash(
                f"Error: {error}",
                "error"
            )

        finally:
            conexion.close()

    return render_template(
        "mi_apartamento.html",
        residente=residente,
        apartamento=None,
        usuario=session.get("usuario"),
        modo="agregar"
    )


# ============================================================
# EDITAR MI APARTAMENTO
# ============================================================

@app.route(
    "/mi_apartamento/editar",
    methods=["GET", "POST"]
)
def editar_mi_apartamento():

    if "usuario" not in session:
        return redirect(url_for("login"))

    if session.get("rol") == "admin":
        return redirect(url_for("panel_admin"))

    residente = obtener_residente_sesion()

    if not residente or not residente["apartamento"]:

        flash(
            "No tienes un apartamento asociado.",
            "info"
        )

        return redirect(url_for("agregar_mi_apartamento"))

    conexion = conectar()

    try:

        cursor = conexion.cursor()

        cursor.execute(
            """
            SELECT
                id AS id_apartamento,
                apartamento AS numero,
                apartamento,
                bloque,
                piso,
                propietario,
                residente,
                area,
                habitaciones,
                parqueadero,
                estado,
                vehiculo_tipo,
                vehiculo_color,
                vehiculo_placa,
                vehiculo_cilindraje,
                vehiculo_soat,
                vehiculo_propietario
            FROM apartamentos
            WHERE apartamento = ?
            """,
            (
                residente["apartamento"],
            )
        )

        apartamento = cursor.fetchone()

    finally:
        conexion.close()

    if not apartamento:

        flash(
            "No se encontró el apartamento asociado.",
            "error"
        )

        return redirect(url_for("mi_apartamento"))

    if request.method == "POST":

        numero = request.form.get("apartamento", "").strip()
        bloque = request.form.get("bloque", "").strip()
        piso = request.form.get("piso", "").strip()
        propietario = request.form.get("propietario", "").strip()
        residente_nombre = request.form.get("residente", "").strip()
        area = request.form.get("area", "").strip()
        habitaciones = request.form.get("habitaciones", "").strip()
        parqueadero = request.form.get("parqueadero", "").strip()
        estado = request.form.get("estado", "Ocupado").strip()

        vehiculo_tipo = request.form.get("vehiculo_tipo", "").strip()
        vehiculo_color = request.form.get("vehiculo_color", "").strip()
        vehiculo_placa = request.form.get("vehiculo_placa", "").strip().upper()
        vehiculo_cilindraje = request.form.get("vehiculo_cilindraje", "").strip()
        vehiculo_soat = request.form.get("vehiculo_soat", "").strip()
        vehiculo_propietario = request.form.get("vehiculo_propietario", "").strip()

        if not numero:

            flash(
                "El número del apartamento es obligatorio.",
                "error"
            )

            return render_template(
                "mi_apartamento.html",
                residente=residente,
                apartamento=apartamento,
                usuario=session.get("usuario"),
                modo="editar"
            )

        if not propietario:
            propietario = residente["nombre"]

        if not residente_nombre:
            residente_nombre = residente["nombre"]

        conexion = conectar()

        try:

            cursor = conexion.cursor()

            cursor.execute(
                """
                SELECT id
                FROM apartamentos
                WHERE apartamento = ?
                AND id != ?
                """,
                (
                    numero,
                    apartamento["id_apartamento"]
                )
            )

            duplicado = cursor.fetchone()

            if duplicado:

                flash(
                    "Ese número de apartamento ya está registrado.",
                    "error"
                )

                return render_template(
                    "mi_apartamento.html",
                    residente=residente,
                    apartamento=apartamento,
                    usuario=session.get("usuario"),
                    modo="editar"
                )

            area_valor = float(area) if area else None
            habitaciones_valor = int(habitaciones) if habitaciones else None

            cursor.execute(
                """
                UPDATE apartamentos
                SET
                    apartamento = ?,
                    bloque = ?,
                    piso = ?,
                    propietario = ?,
                    residente = ?,
                    area = ?,
                    habitaciones = ?,
                    parqueadero = ?,
                    estado = ?,
                    vehiculo_tipo = ?,
                    vehiculo_color = ?,
                    vehiculo_placa = ?,
                    vehiculo_cilindraje = ?,
                    vehiculo_soat = ?,
                    vehiculo_propietario = ?
                WHERE id = ?
                """,
                (
                    numero,
                    bloque,
                    piso,
                    propietario,
                    residente_nombre,
                    area_valor,
                    habitaciones_valor,
                    parqueadero,
                    estado or "Ocupado",
                    vehiculo_tipo,
                    vehiculo_color,
                    vehiculo_placa,
                    vehiculo_cilindraje,
                    vehiculo_soat,
                    vehiculo_propietario,
                    apartamento["id_apartamento"]
                )
            )

            cursor.execute(
                """
                UPDATE residentes
                SET apartamento = ?
                WHERE id = ?
                """,
                (
                    numero,
                    residente["id"]
                )
            )

            conexion.commit()

            flash(
                "La información de tu apartamento fue actualizada.",
                "success"
            )

            return redirect(url_for("mi_apartamento"))

        except sqlite3.IntegrityError:

            conexion.rollback()

            flash(
                "No se pudo actualizar el apartamento.",
                "error"
            )

        except (ValueError, TypeError) as error:

            conexion.rollback()

            flash(
                f"Revisa los valores numéricos: {error}",
                "error"
            )

        except Exception as error:

            conexion.rollback()

            flash(
                f"Error: {error}",
                "error"
            )

        finally:
            conexion.close()

    return render_template(
        "mi_apartamento.html",
        residente=residente,
        apartamento=apartamento,
        usuario=session.get("usuario"),
        modo="editar"
    )


# ============================================================
# ELIMINAR MI APARTAMENTO
# ============================================================

@app.route(
    "/mi_apartamento/eliminar",
    methods=["POST"]
)
def eliminar_mi_apartamento():

    if "usuario" not in session:
        return redirect(url_for("login"))

    if session.get("rol") == "admin":
        return redirect(url_for("panel_admin"))

    residente = obtener_residente_sesion()

    if not residente or not residente["apartamento"]:

        flash(
            "No tienes un apartamento asociado.",
            "info"
        )

        return redirect(url_for("mi_apartamento"))

    conexion = conectar()

    try:

        cursor = conexion.cursor()
        numero = residente["apartamento"]

        cursor.execute(
            """
            DELETE FROM apartamentos
            WHERE apartamento = ?
            """,
            (numero,)
        )

        cursor.execute(
            """
            UPDATE residentes
            SET apartamento = NULL
            WHERE id = ?
            """,
            (
                residente["id"],
            )
        )

        conexion.commit()

        flash(
            "El apartamento fue eliminado correctamente.",
            "success"
        )

    except Exception as error:

        conexion.rollback()

        flash(
            f"No se pudo eliminar el apartamento: {error}",
            "error"
        )

    finally:
        conexion.close()

    return redirect(url_for("mi_apartamento"))


# ============================================================
# CHATBOT
# ============================================================

@app.route("/chatbot")
def chatbot():

    if "usuario" not in session:
        return redirect(url_for("login"))

    return render_template(
        "chatbot.html"
    )


# ============================================================
# RESPUESTAS DEL CHATBOT
# ============================================================

def respuesta_chatbot(pregunta):

    try:

        return obtener_respuesta(
            pregunta
        )

    except Exception as error:

        print(
            "ERROR EN CHATBOT:",
            error
        )

        return (
            "⚠️ Se presentó un error al procesar "
            "tu consulta.\n\n"
            "Por favor, intenta nuevamente."
        )


# ============================================================
# API CHATBOT
# ============================================================

@app.route(
    "/api/chatbot",
    methods=["POST"]
)
@app.route(
    "/chatbot_responder",
    methods=["POST"]
)
@app.route(
    "/chatbot/responder",
    methods=["POST"]
)
def api_chatbot():

    if "usuario" not in session:

        return jsonify({
            "ok": False,
            "respuesta": (
                "Tu sesión ha terminado. "
                "Por favor inicia sesión nuevamente."
            )
        }), 401

    datos = request.get_json(
        silent=True
    )

    if not datos:

        return jsonify({
            "ok": False,
            "respuesta": "No se recibió ninguna pregunta."
        }), 400

    pregunta = datos.get(
        "pregunta",
        datos.get(
            "message",
            datos.get(
                "mensaje",
                ""
            )
        )
    )

    respuesta = respuesta_chatbot(
        pregunta
    )

    return jsonify({
        "ok": True,
        "respuesta": respuesta,
        "response": respuesta,
        "mensaje": respuesta
    })


# ============================================================
# MANUAL INTERACTIVO
# ============================================================

@app.route("/manual_interactivo")
def manual_interactivo():

    if "usuario" not in session:
        return redirect(url_for("login"))

    return render_template(
        "manual_interactivo.html"
    )


# ============================================================
# MANUAL COMPLETO
# ============================================================

@app.route("/manual_completo")
def manual_completo():

    if "usuario" not in session:
        return redirect(url_for("login"))

    return render_template(
        "manual_completo.html"
    )


# ============================================================
# DOCUMENTOS DE NORMATIVIDAD
# ============================================================

DOCUMENTOS_NORMATIVIDAD = [

    {
        "numero": "1",
        "archivo": "1 constitucion-politica-colombia-1991.pdf",
        "titulo": "Constitución Política de Colombia",
        "descripcion": "Constitución Política de Colombia de 1991.",
        "icono": "🇨🇴",
        "color": "#2563eb",
        "color_claro": "#eff6ff"
    },

    {
        "numero": "2",
        "archivo": "2 Ley 675 de 2001 expide el régimen de propiedad horizontal.pdf",
        "titulo": "Ley 675 de 2001 - Propiedad Horizontal",
        "descripcion": "Régimen de Propiedad Horizontal en Colombia.",
        "icono": "⚖️",
        "color": "#7c3aed",
        "color_claro": "#f5f3ff"
    },

    {
        "numero": "3",
        "archivo": "3 Ley_1801_de_2016 Código Nacional de Seguridad y Convivencia Ciudadana_.pdf",
        "titulo": "Ley 1801 de 2016 - Código Nacional de Seguridad y Convivencia",
        "descripcion": "Código Nacional de Seguridad y Convivencia Ciudadana.",
        "icono": "🛡️",
        "color": "#dc2626",
        "color_claro": "#fef2f2"
    },

    {
        "numero": "4",
        "archivo": "4 codigo_civil_colombia.pdf",
        "titulo": "Código Civil Colombiano",
        "descripcion": "Normas del Código Civil Colombiano.",
        "icono": "📕",
        "color": "#059669",
        "color_claro": "#ecfdf5"
    },

    {
        "numero": "5",
        "archivo": "5 ley_1564_de_2012_codigo_general_del_proceso.pdf",
        "titulo": "Ley 1564 de 2012 - Código General del Proceso",
        "descripcion": "Código General del Proceso.",
        "icono": "📘",
        "color": "#d97706",
        "color_claro": "#fffbeb"
    },

    {
        "numero": "6",
        "archivo": "6 Ley_640_de_2001 Por la cual se modiﬁcan normas relativas a la conciliación y se dictan otras disposiciones.pdf",
        "titulo": "Ley 640 de 2001 - Conciliación",
        "descripcion": "Normas relacionadas con la conciliación.",
        "icono": "🤝",
        "color": "#0891b2",
        "color_claro": "#ecfeff"
    },

    {
        "numero": "7",
        "archivo": "7 Ley_1581_de_2012 protección de datos personales.pdf",
        "titulo": "Ley 1581 de 2012 - Protección de Datos Personales",
        "descripcion": "Protección de datos personales en Colombia.",
        "icono": "🔐",
        "color": "#4f46e5",
        "color_claro": "#eef2ff"
    },

    {
        "numero": "8",
        "archivo": "8 Ley_1437_de_2011 Código de Procedimiento Administrativo y de lo Contencioso Administrativo.pdf",
        "titulo": "Ley 1437 de 2011 - Código de Procedimiento Administrativo y de lo Contencioso Administrativo",
        "descripcion": "Código de Procedimiento Administrativo y CPACA.",
        "icono": "📜",
        "color": "#9333ea",
        "color_claro": "#faf5ff"
    },

    {
        "numero": "9",
        "archivo": "9 codigo_penal_colombia.pdf",
        "titulo": "Código Penal Colombiano",
        "descripcion": "Normativa del Código Penal Colombiano.",
        "icono": "⚠️",
        "color": "#be123c",
        "color_claro": "#fff1f2"
    },

    {
        "numero": "10",
        "archivo": "10 guia_jurisprudencial_sobre_conceptos_acusatori.pdf",
        "titulo": "Guía Jurisprudencial sobre Conceptos Acusatorios",
        "descripcion": "Guía jurisprudencial relacionada con conceptos acusatorios.",
        "icono": "📚",
        "color": "#15803d",
        "color_claro": "#f0fdf4"
    },

    {
        "numero": "11",
        "archivo": "11 LEY 2450 DEL 4 DE MARZO DE 2025_Ley acustica. (2).pdf",
        "titulo": "Ley 2450 de 2025 - Ley Acústica",
        "descripcion": "Normativa relacionada con contaminación acústica y ruido.",
        "icono": "🔊",
        "color": "#c2410c",
        "color_claro": "#fff7ed"
    },

    {
        "numero": "12",
        "archivo": "12 Ordenamiento territorial para el desarrollo.pdf",
        "titulo": "Ordenamiento Territorial para el Desarrollo",
        "descripcion": "Documento relacionado con ordenamiento territorial.",
        "icono": "🏙️",
        "color": "#0369a1",
        "color_claro": "#f0f9ff"
    }
]


# ============================================================
# VERIFICAR PDF
# ============================================================

def obtener_documentos_normatividad():

    documentos = []

    for documento in DOCUMENTOS_NORMATIVIDAD:

        ruta = os.path.join(
            CARPETA_NORMATIVIDAD,
            documento["archivo"]
        )

        copia = documento.copy()

        copia["existe"] = os.path.exists(ruta)

        documentos.append(copia)

    return documentos


# ============================================================
# PÁGINA NORMATIVIDAD
# ============================================================

@app.route("/normatividad")
def normatividad():

    if "usuario" not in session:
        return redirect(url_for("login"))

    documentos = obtener_documentos_normatividad()

    return render_template(
        "normatividad.html",
        documentos=documentos,
        normatividad_json=json.dumps(
            documentos,
            ensure_ascii=False
        )
    )


# ============================================================
# BÚSQUEDA DENTRO DE LOS PDF
# ============================================================

@app.route("/normatividad/buscar/<numero>")
def buscar_normatividad(numero):

    if "usuario" not in session:

        return jsonify({
            "ok": False,
            "mensaje": "Sesión no válida."
        }), 401

    documento = next(
        (
            item
            for item in DOCUMENTOS_NORMATIVIDAD
            if str(item["numero"]) == str(numero)
        ),
        None
    )

    if documento is None:

        return jsonify({
            "ok": False,
            "mensaje": "Documento no encontrado."
        }), 404

    pregunta = request.args.get(
        "q",
        ""
    ).strip()

    if not pregunta:

        return jsonify({
            "ok": True,
            "resultados": [],
            "total": 0
        })

    if fitz is None:

        return jsonify({
            "ok": False,
            "mensaje": (
                "PyMuPDF no está instalado. "
                "Ejecute: py -m pip install PyMuPDF"
            )
        }), 500

    ruta_pdf = os.path.join(
        CARPETA_NORMATIVIDAD,
        documento["archivo"]
    )

    if not os.path.exists(ruta_pdf):

        return jsonify({
            "ok": False,
            "mensaje": (
                "No se encontró el PDF:\n"
                + documento["archivo"]
            )
        }), 404

    resultados = []

    try:

        archivo_pdf = fitz.open(ruta_pdf)

        texto_busqueda = normalizar(pregunta)

        for numero_pagina in range(len(archivo_pdf)):

            pagina = archivo_pdf[numero_pagina]

            texto = pagina.get_text("text")

            texto_normalizado = normalizar(texto)

            posicion = texto_normalizado.find(
                texto_busqueda
            )

            if posicion != -1:

                inicio = max(
                    0,
                    posicion - 180
                )

                fin = min(
                    len(texto),
                    posicion + len(pregunta) + 250
                )

                contexto = texto[inicio:fin].strip()

                resultados.append({
                    "pagina": numero_pagina + 1,
                    "contexto": contexto
                })

            if len(resultados) >= 10:
                break

        archivo_pdf.close()

    except Exception as error:

        return jsonify({
            "ok": False,
            "mensaje": f"Error leyendo el PDF: {error}"
        }), 500

    return jsonify({
        "ok": True,
        "resultados": resultados,
        "total": len(resultados)
    })


# ============================================================
# MANUALES
# ============================================================

@app.route("/manuales")
def manuales():

    if "usuario" not in session:
        return redirect(url_for("login"))

    return render_template(
        "manuales.html"
    )


# ============================================================
# MANUAL DE CONVIVENCIA
# ============================================================

@app.route("/manuales/convivencia")
def manual_convivencia():

    if "usuario" not in session:
        return redirect(url_for("login"))

    archivo = (
        "2 MANUAL DE CONVIVENCIA Y USO DE ZONAS COMUNES "
        "Infinito 2U okkkk (2).pdf"
    )

    ruta_archivo = os.path.join(
        CARPETA_MANUAL_CONVIVENCIA,
        archivo
    )

    if os.path.exists(ruta_archivo):

        return send_from_directory(
            CARPETA_MANUAL_CONVIVENCIA,
            archivo
        )

    if os.path.exists(CARPETA_MANUAL_CONVIVENCIA):

        archivos = os.listdir(
            CARPETA_MANUAL_CONVIVENCIA
        )

        archivo_encontrado = next(
            (
                nombre
                for nombre in archivos
                if normalizar(nombre).startswith(
                    normalizar(
                        "2 MANUAL DE CONVIVENCIA Y USO DE ZONAS COMUNES"
                    )
                )
                and nombre.lower().endswith(".pdf")
            ),
            None
        )

        if archivo_encontrado:

            return send_from_directory(
                CARPETA_MANUAL_CONVIVENCIA,
                archivo_encontrado
            )

    return (
        "No se encontró el Manual de Convivencia. "
        "Verifique que el PDF esté dentro de "
        "assets/manual de convivencia/",
        404
    )


# ============================================================
# MANUAL JURÍDICO
# ============================================================

@app.route("/manuales/juridico")
def manual_juridico():

    if "usuario" not in session:
        return redirect(url_for("login"))

    archivo = (
        "MANUAL JURÍDICO DEL COMITÉ DE CONVIVENCIA PH "
        "Infinito Segunda 2 Roma Kennedy OKKK.pdf"
    )

    ruta_archivo = os.path.join(
        CARPETA_MANUAL_JURIDICO,
        archivo
    )

    if os.path.exists(ruta_archivo):

        return send_from_directory(
            CARPETA_MANUAL_JURIDICO,
            archivo
        )

    if os.path.exists(CARPETA_MANUAL_JURIDICO):

        archivos = os.listdir(
            CARPETA_MANUAL_JURIDICO
        )

        archivo_encontrado = next(
            (
                nombre
                for nombre in archivos
                if normalizar(nombre).startswith(
                    normalizar(
                        "MANUAL JURIDICO DEL COMITE DE CONVIVENCIA PH"
                    )
                )
                and nombre.lower().endswith(".pdf")
            ),
            None
        )

        if archivo_encontrado:

            return send_from_directory(
                CARPETA_MANUAL_JURIDICO,
                archivo_encontrado
            )

    return (
        "No se encontró el Manual Jurídico. "
        "Verifique que el PDF esté dentro de "
        "assets/manual juridico/",
        404
    )


# ============================================================
# CÓDIGO QR
# ============================================================

@app.route("/codigo_qr")
def codigo_qr():

    if "usuario" not in session:
        return redirect(url_for("login"))

    return render_template(
        "codigo_qr.html"
    )


# ============================================================
# ERROR 404
# ============================================================

@app.errorhandler(404)
def pagina_no_encontrada(error):

    if "usuario" in session:
        return redirect(url_for("panel_usuario"))

    return redirect(url_for("login"))


# ============================================================
# PREPARAR BASE DE DATOS
# ============================================================

preparar_base_datos()


# ============================================================
# INICIAR APLICACIÓN
# ============================================================

if __name__ == "__main__":

    port = int(os.getenv("PORT", 5000))
    is_production = os.getenv("FLASK_ENV") == "production"
    
    print()
    print("=" * 60)
    print("             INFINITO 2U")
    print("       Sistema de Propiedad Horizontal")
    print("=" * 60)
    print()
    print("Servidor:")
    print(f"http://0.0.0.0:{port}")
    print()
    print("Administrador:")
    print("Usuario: admin")
    print("Contraseña: admin123")
    print()
    print("Documentos de normatividad configurados: 12")
    print()
    print("Manuales configurados: 2")
    print()
    print("Manual de convivencia:")
    print("assets/manual de convivencia/")
    print()
    print("Manual jurídico:")
    print("assets/manual juridico/")
    print()
    print("=" * 60)
    print()

    app.run(
        host="0.0.0.0",
        port=port,
        debug=not is_production
    )
