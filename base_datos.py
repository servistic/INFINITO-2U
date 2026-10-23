import sqlite3
import os


# ============================================================
# CONFIGURACIÓN
# ============================================================

CARPETA_BASE = os.path.dirname(os.path.abspath(__file__))

ARCHIVO_BD = os.path.join(
    CARPETA_BASE,
    "infinito2u.db"
)


# ============================================================
# CONEXIÓN
# ============================================================

def conectar():

    conexion = sqlite3.connect(ARCHIVO_BD)

    conexion.row_factory = sqlite3.Row

    conexion.execute(
        "PRAGMA foreign_keys = ON"
    )

    return conexion


# ============================================================
# CREAR / ACTUALIZAR BASE DE DATOS
# ============================================================

def crear_base_datos():

    conexion = conectar()

    cursor = conexion.cursor()

    # ========================================================
    # RESIDENTES
    # ========================================================

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS residentes (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            documento TEXT NOT NULL UNIQUE,

            nombre TEXT NOT NULL,

            telefono TEXT,

            correo TEXT,

            apartamento TEXT,

            tipo TEXT,

            estado TEXT DEFAULT 'Activo'

        )
    """)


    # ========================================================
    # USUARIOS
    # ========================================================

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            usuario TEXT NOT NULL UNIQUE,

            contrasena TEXT NOT NULL,

            rol TEXT NOT NULL DEFAULT 'residente',

            residente_id INTEGER,

            activo INTEGER NOT NULL DEFAULT 1,

            FOREIGN KEY (residente_id)

                REFERENCES residentes(id)

                ON DELETE SET NULL

        )
    """)


    # ========================================================
    # VERIFICAR COLUMNAS DE USUARIOS
    # ========================================================

    cursor.execute(
        "PRAGMA table_info(usuarios)"
    )

    columnas_usuarios = [
        columna["name"]
        for columna in cursor.fetchall()
    ]


    if "residente_id" not in columnas_usuarios:

        cursor.execute("""
            ALTER TABLE usuarios
            ADD COLUMN residente_id INTEGER
        """)


    if "activo" not in columnas_usuarios:

        cursor.execute("""
            ALTER TABLE usuarios
            ADD COLUMN activo INTEGER DEFAULT 1
        """)


    # ========================================================
    # APARTAMENTOS
    # ========================================================

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS apartamentos (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            apartamento TEXT NOT NULL UNIQUE,

            propietario TEXT,

            residente TEXT,

            area REAL,

            habitaciones INTEGER,

            parqueadero TEXT,

            estado TEXT DEFAULT 'Ocupado'

        )
    """)


    # ========================================================
    # ACTUALIZAR APARTAMENTOS EXISTENTES
    # ========================================================

    cursor.execute(
        "PRAGMA table_info(apartamentos)"
    )

    columnas_apartamentos = [
        columna["name"]
        for columna in cursor.fetchall()
    ]


    if "bloque" not in columnas_apartamentos:

        cursor.execute("""
            ALTER TABLE apartamentos
            ADD COLUMN bloque TEXT
        """)


    if "piso" not in columnas_apartamentos:

        cursor.execute("""
            ALTER TABLE apartamentos
            ADD COLUMN piso TEXT
        """)


    # ========================================================
    # VEHÍCULOS
    # ========================================================

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS vehiculos (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            apartamento TEXT,

            tipo TEXT,

            placa TEXT UNIQUE,

            color TEXT,

            cilindraje TEXT,

            soat TEXT,

            propietario TEXT

        )
    """)


    # ========================================================
    # RESERVAS
    # ========================================================

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS reservas (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            residente_id INTEGER,

            apartamento TEXT,

            zona TEXT NOT NULL,

            fecha TEXT NOT NULL,

            hora_inicio TEXT NOT NULL,

            hora_fin TEXT NOT NULL,

            estado TEXT NOT NULL DEFAULT 'Pendiente',

            observaciones TEXT,

            FOREIGN KEY (residente_id)

                REFERENCES residentes(id)

                ON DELETE CASCADE

        )
    """)


    # ========================================================
    # PQRS
    # ========================================================

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS pqrs (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            residente_id INTEGER,

            apartamento TEXT,

            tipo TEXT NOT NULL,

            asunto TEXT NOT NULL,

            descripcion TEXT NOT NULL,

            fecha TEXT NOT NULL,

            estado TEXT NOT NULL DEFAULT 'Pendiente',

            respuesta TEXT,

            FOREIGN KEY (residente_id)

                REFERENCES residentes(id)

                ON DELETE CASCADE

        )
    """)


    # ========================================================
    # TRASTEOS
    # ========================================================

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS trasteos (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            residente_id INTEGER,

            apartamento TEXT,

            fecha TEXT NOT NULL,

            hora TEXT NOT NULL,

            tipo TEXT NOT NULL,

            descripcion TEXT,

            estado TEXT NOT NULL DEFAULT 'Pendiente',

            FOREIGN KEY (residente_id)

                REFERENCES residentes(id)

                ON DELETE CASCADE

        )
    """)


    # ========================================================
    # VISITANTES
    # ========================================================

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS visitantes (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            residente_id INTEGER,

            apartamento TEXT,

            nombre TEXT NOT NULL,

            documento TEXT,

            telefono TEXT,

            fecha TEXT NOT NULL,

            hora_entrada TEXT,

            hora_salida TEXT,

            estado TEXT DEFAULT 'Activo',

            FOREIGN KEY (residente_id)

                REFERENCES residentes(id)

                ON DELETE CASCADE

        )
    """)


    # ========================================================
    # ZONAS COMUNES
    # ========================================================

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS zonas_comunes (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            nombre TEXT NOT NULL UNIQUE,

            descripcion TEXT,

            capacidad INTEGER,

            horario_inicio TEXT,

            horario_fin TEXT,

            estado TEXT DEFAULT 'Disponible'

        )
    """)


    # ========================================================
    # NOTIFICACIONES
    # ========================================================

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS notificaciones (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            residente_id INTEGER,

            titulo TEXT NOT NULL,

            mensaje TEXT NOT NULL,

            fecha TEXT NOT NULL,

            leida INTEGER NOT NULL DEFAULT 0,

            FOREIGN KEY (residente_id)

                REFERENCES residentes(id)

                ON DELETE CASCADE

        )
    """)


    # ========================================================
    # MASCOTAS
    # ========================================================

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS mascotas (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            residente_id INTEGER,

            apartamento TEXT,

            nombre TEXT NOT NULL,

            especie TEXT,

            raza TEXT,

            color TEXT,

            estado TEXT DEFAULT 'Activo',

            FOREIGN KEY (residente_id)

                REFERENCES residentes(id)

                ON DELETE CASCADE

        )
    """)


    # ========================================================
    # ZONAS INICIALES
    # ========================================================

    zonas_iniciales = [

        (
            "Salón social",
            "Espacio para reuniones y eventos",
            30,
            "08:00",
            "22:00"
        ),

        (
            "Zona BBQ",
            "Zona para reuniones y parrilladas",
            15,
            "09:00",
            "21:00"
        ),

        (
            "Cancha",
            "Cancha deportiva del conjunto",
            20,
            "06:00",
            "21:00"
        ),

        (
            "Gimnasio",
            "Zona de ejercicio",
            15,
            "05:00",
            "22:00"
        )

    ]


    for zona in zonas_iniciales:

        cursor.execute("""
            INSERT OR IGNORE INTO zonas_comunes
            (
                nombre,
                descripcion,
                capacidad,
                horario_inicio,
                horario_fin
            )

            VALUES (?, ?, ?, ?, ?)
        """, zona)


    # ========================================================
    # APARTAMENTO DE PRUEBA
    # ========================================================

    cursor.execute("""
        INSERT OR IGNORE INTO apartamentos
        (
            apartamento,
            propietario,
            residente,
            area,
            habitaciones,
            parqueadero,
            estado
        )

        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (

        "101",
        "Residente de Prueba",
        "Residente de Prueba",
        65.5,
        3,
        "P-101",
        "Ocupado"

    ))


    # ========================================================
    # RESIDENTE DE PRUEBA
    # ========================================================

    cursor.execute("""
        INSERT OR IGNORE INTO residentes
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
    """, (

        "1000000000",
        "Residente de Prueba",
        "3000000000",
        "residente@infinito2u.com",
        "101",
        "Propietario",
        "Activo"

    ))


    # ========================================================
    # RELACIÓN RESIDENTE DE PRUEBA
    # ========================================================

    cursor.execute("""
        SELECT id
        FROM residentes
        WHERE documento = ?
    """, ("1000000000",))


    residente = cursor.fetchone()


    if residente:

        residente_id = residente["id"]


        cursor.execute("""
            INSERT OR IGNORE INTO usuarios
            (
                usuario,
                contrasena,
                rol,
                residente_id,
                activo
            )

            VALUES (?, ?, ?, ?, ?)
        """, (

            "residente1",
            "1234",
            "residente",
            residente_id,
            1

        ))


        cursor.execute("""
            UPDATE usuarios

            SET residente_id = ?,
                activo = 1

            WHERE usuario = ?
        """, (

            residente_id,
            "residente1"

        ))


    # ========================================================
    # ADMINISTRADOR
    # ========================================================

    cursor.execute("""
        INSERT OR IGNORE INTO usuarios
        (
            usuario,
            contrasena,
            rol,
            residente_id,
            activo
        )

        VALUES (?, ?, ?, ?, ?)
    """, (

        "admin",
        "admin123",
        "admin",
        None,
        1

    ))


    # ========================================================
    # ASEGURAR ADMIN ACTIVO
    # ========================================================

    cursor.execute("""
        UPDATE usuarios

        SET rol = 'admin',
            residente_id = NULL,
            activo = 1

        WHERE usuario = 'admin'
    """)


    conexion.commit()

    conexion.close()


# ============================================================
# BUSCAR USUARIO
# ============================================================

def buscar_usuario(usuario, contrasena):

    conexion = conectar()

    cursor = conexion.cursor()

    cursor.execute("""
        SELECT

            usuarios.*,

            residentes.nombre,

            residentes.documento,

            residentes.telefono,

            residentes.correo,

            residentes.apartamento

        FROM usuarios

        LEFT JOIN residentes

            ON usuarios.residente_id = residentes.id

        WHERE usuarios.usuario = ?

        AND usuarios.contrasena = ?

        AND usuarios.activo = 1

    """, (

        usuario,
        contrasena

    ))

    resultado = cursor.fetchone()

    conexion.close()

    return resultado


# ============================================================
# OBTENER RESIDENTE
# ============================================================

def obtener_residente(id_residente):

    conexion = conectar()

    cursor = conexion.cursor()

    cursor.execute("""
        SELECT *

        FROM residentes

        WHERE id = ?
    """, (

        id_residente,

    ))

    resultado = cursor.fetchone()

    conexion.close()

    return resultado


# ============================================================
# OBTENER APARTAMENTO
# ============================================================

def obtener_apartamento(apartamento):

    conexion = conectar()

    cursor = conexion.cursor()

    cursor.execute("""
        SELECT *

        FROM apartamentos

        WHERE apartamento = ?
    """, (

        apartamento,

    ))

    resultado = cursor.fetchone()

    conexion.close()

    return resultado


# ============================================================
# INICIALIZAR
# ============================================================

crear_base_datos()


print("==============================================")
print(" BASE DE DATOS INFINITO 2U")
print("==============================================")
print("Base de datos creada/actualizada correctamente.")
print(f"Ubicación: {ARCHIVO_BD}")
print("==============================================")