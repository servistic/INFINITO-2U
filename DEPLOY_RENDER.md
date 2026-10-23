# 📦 GUÍA DE DEPLOYMENT A RENDER.COM - INFINITO-2U

**Objetivo:** Publicar el proyecto en Render para exposición universitaria en 30 minutos

---

## ✅ ESTADO DE LA BASE DE DATOS

**BUENA NOTICIA:** El proyecto SÍ maneja base de datos correctamente.

### BD Implementada:
- ✅ SQLite con 10 tablas:
  1. **residentes** - Propietarios/Arrendatarios
  2. **usuarios** - Login/autenticación
  3. **apartamentos** - Unidades del edificio
  4. **vehiculos** - Vehículos de residentes
  5. **reservas** - Reservas de zonas comunes
  6. **pqrs** - Peticiones/Quejas/Reclamos/Sugerencias
  7. **trasteos** - Registro de mudanzas
  8. **visitantes** - Control de acceso
  9. **zonas_comunes** - Áreas del edificio
  10. **notificaciones** - Sistema de notificaciones

### Inicialización:
- ✅ Función `crear_base_datos()` en `base_datos.py`
- ✅ Tablas se crean automáticamente al conectar
- ✅ Foreign keys habilitadas
- ⚠️ NO se llama explícitamente en `app.py` → NECESITA ARREGLO

---

## 🔴 ANTES DE PUBLICAR: AJUSTES MÍNIMOS (CRÍTICO)

### 1. Llamar a crear_base_datos() al iniciar la app

**En `app.py`, línea ~90-100, busca la función `preparar_base_datos()`:**

```python
def preparar_base_datos():
    
    conexion = conectar()
    conexion.close()
```

**Cambiar a:**
```python
def preparar_base_datos():
    from base_datos import crear_base_datos
    crear_base_datos()  # ← AGREGAR ESTA LÍNEA
    conexion = conectar()
    conexion.close()
```

**O crear este código al inicio de app.py (después de `app = Flask(...)`):**

```python
# ============================================================
# INICIALIZAR BASE DE DATOS
# ============================================================

def inicializar_app():
    """Inicializa la aplicación y la base de datos"""
    from base_datos import crear_base_datos
    try:
        crear_base_datos()
        print("✓ Base de datos inicializada")
    except Exception as e:
        print(f"✗ Error inicializando BD: {e}")

# Llamar al iniciar
inicializar_app()
```

**Tiempo:** 2 minutos

---

### 2. Cambiar host/port para Render

**En `app.py`, línea ~3318:**

**Actual:**
```python
app.run(
    host="127.0.0.1",
    port=5000,
    debug=True
)
```

**Cambiar a:**
```python
import os
from dotenv import load_dotenv

load_dotenv()

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    debug = os.getenv("FLASK_ENV") == "development"
    
    app.run(
        host="0.0.0.0",      # ← CAMBIAR (Render requiere esto)
        port=port,            # ← CAMBIAR
        debug=debug           # ← CAMBIAR
    )
```

**Tiempo:** 2 minutos

---

### 3. Crear archivo .env para Render

**Crear archivo `.env` en la raíz del proyecto:**

```env
FLASK_ENV=production
PORT=5000
SECRET_KEY=your_secret_key_here_change_in_production
DATABASE_URL=sqlite:///infinito2u.db
DEBUG=False
```

**Tiempo:** 1 minuto

---

### 4. Actualizar requirements.txt

**Verificar que esté completo:**

```bash
pip freeze > requirements.txt
```

O agregue estos si faltan:

```
Flask>=2.0.0
PyMuPDF>=1.23.0
Pillow>=9.0.0
qrcode>=7.3.0
python-dotenv>=0.19.0
gunicorn>=20.1.0
```

**Tiempo:** 1 minuto

---

### 5. Crear archivo Procfile (IMPORTANTE para Render)

**Crear archivo `Procfile` en la raíz:**

```
web: gunicorn app:app
```

**Tiempo:** 1 minuto

---

### 6. Crear archivo build.sh (para Render)

**Crear archivo `build.sh` en la raíz:**

```bash
#!/bin/bash
pip install -r requirements.txt
python -c "from base_datos import crear_base_datos; crear_base_datos()"
```

**Permiso de ejecución:**
```bash
chmod +x build.sh
```

**Tiempo:** 1 minuto

---

## 📋 CHECKLIST PRE-DEPLOYMENT

- [ ] 1. Agregar `inicializar_app()` en app.py
- [ ] 2. Cambiar host a "0.0.0.0" y port dinámico
- [ ] 3. Crear `.env`
- [ ] 4. Actualizar `requirements.txt`
- [ ] 5. Crear `Procfile`
- [ ] 6. Crear `build.sh`
- [ ] 7. Probar localmente con `gunicorn app:app`
- [ ] 8. Commit a GitHub
- [ ] 9. Desplegar en Render

---

## 🚀 PASOS DE DEPLOYMENT A RENDER (10 minutos)

### Paso 1: Preparar repositorio GitHub

```bash
# Si no es un repo git aún
cd /home/desarrollo/INFINITO-2U
git init
git add .
git commit -m "Initial commit - INFINITO-2U"
git remote add origin https://github.com/TU_USUARIO/INFINITO-2U.git
git push -u origin main
```

### Paso 2: Crear cuenta en Render

1. Ir a: https://render.com
2. Clickear "Sign Up"
3. Conectar con GitHub
4. Autorizar acceso a repositorios

### Paso 3: Crear nuevo servicio

1. Dashboard de Render → "New +" → "Web Service"
2. Seleccionar repositorio `INFINITO-2U`
3. Configurar:
   - **Name:** infinito-2u
   - **Environment:** Python
   - **Build Command:** `pip install -r requirements.txt && python -c "from base_datos import crear_base_datos; crear_base_datos()"`
   - **Start Command:** `gunicorn app:app`
   - **Plan:** Free (suficiente para exposición)

### Paso 4: Agregar variables de entorno

En Render → Settings → Environment:

```
FLASK_ENV=production
SECRET_KEY=your_very_secret_key_12345678901234567890
PORT=5000
```

### Paso 5: Deploy

- Clickear "Deploy"
- Esperar 2-3 minutos
- Ver logs
- Abrirá URL como: `https://infinito-2u.onrender.com`

---

## ⚠️ IMPORTANTE PARA LA EXPOSICIÓN

### Credenciales de Admin (CAMBIAR DESPUÉS):
```
Usuario: admin
Contraseña: admin123
```

### Base de datos en Render:
- SQLite se guardará en `/tmp/infinito2u.db`
- **ATENCIÓN:** Se perderá si Render reinicia (cada 15 min sin actividad)
- Para datos permanentes, usar PostgreSQL (de pago)

### Duración del Free Tier de Render:
- ✅ Exposición/demo = SIN PROBLEMA
- ⚠️ Producción permanente = cambiar a plan pagado

---

## ✅ TESTING LOCAL ANTES DE PUBLICAR

### 1. Instalar gunicorn localmente

```bash
pip install gunicorn
```

### 2. Probar con gunicorn (como en Render)

```bash
gunicorn app:app --bind 0.0.0.0:5000
```

### 3. Acceder a http://localhost:5000

- Debería verse igual que con `python app.py`
- Probar login con admin/admin123

### 4. Si hay errores

```bash
gunicorn app:app --bind 0.0.0.0:5000 --log-level debug
```

---

## 📝 ARCHIVO COMPLETO PARA app.py

**Agregar al inicio de app.py (después de imports):**

```python
import os
from dotenv import load_dotenv

load_dotenv()

# ============================================================
# INICIALIZAR BASE DE DATOS
# ============================================================

def inicializar_base_datos():
    """Inicializa la aplicación y crea la BD si no existe"""
    try:
        from base_datos import crear_base_datos
        crear_base_datos()
        print("✓ Base de datos inicializada correctamente")
    except Exception as e:
        print(f"✗ Error inicializando base de datos: {e}")

# Inicializar al importar el módulo
inicializar_base_datos()
```

**Cambiar final de app.py:**

```python
if __name__ == "__main__":
    # Configuración para desarrollo local
    port = int(os.getenv("PORT", 5000))
    
    app.run(
        host="0.0.0.0",
        port=port,
        debug=os.getenv("FLASK_ENV") == "development"
    )
```

---

## 📦 Archivos a crear/modificar

```
INFINITO-2U/
├── app.py                    (MODIFICAR - agregar inicialización BD)
├── base_datos.py            (OK - no cambiar)
├── requirements.txt          (CREAR/ACTUALIZAR)
├── .env                      (CREAR)
├── Procfile                  (CREAR)
├── build.sh                  (CREAR)
└── ... (resto igual)
```

---

## 🎯 TIEMPO TOTAL

| Tarea | Tiempo |
|-------|--------|
| Modificar app.py | 5 min |
| Crear archivos | 5 min |
| Testing local | 10 min |
| Push a GitHub | 5 min |
| Deploy en Render | 10 min |
| **TOTAL** | **~35 minutos** |

---

## 🔒 PARA DESPUÉS (No urgente para exposición)

- [ ] Cambiar contraseña de admin
- [ ] Agregar validación de formularios
- [ ] Implementar hash de contraseñas
- [ ] Agregar rate limiting
- [ ] Cambiar a PostgreSQL
- [ ] Implementar HTTPS

---

## ❓ PREGUNTAS FRECUENTES

**P: ¿Se borrarán los datos?**  
R: Sí, cada que Render reinicia (cada 15 min sin actividad). Es normal en free tier.

**P: ¿Puedo mantener datos permanentemente?**  
R: SÍ, pero requiere upgrade a plan pagado o usar base de datos externa.

**P: ¿Cuánto cuesta?**  
R: Free tier = $0 (pero con limitaciones). Plan pagado desde $7/mes.

**P: ¿Funciona todo?**  
R: SÍ, todo funciona igual que localmente. Solo la BD se limpia.

**P: ¿Cómo comparto el link?**  
R: Render genera URL pública como `https://infinito-2u.onrender.com`

---

## 📞 SOPORTE RENDER

- Docs: https://render.com/docs
- Status: https://render-status.com/
- Help: https://render.com/support

---

**Listo para exposición en 35 minutos 🚀**

**Después de la exposición:** Implementar correcciones de seguridad del REPORTE_SEGURIDAD.md
