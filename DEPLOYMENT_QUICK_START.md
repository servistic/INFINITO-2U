# 🚀 INFINITO-2U - GUÍA RÁPIDA DE DEPLOYMENT A RENDER

**Estado:** Listo para exposición universitaria  
**Tiempo de deploy:** 20 minutos  
**Costo:** Gratis en Free Tier (ideal para demo)

---

## 📋 CAMBIOS REALIZADOS AL PROYECTO

✅ Agregados archivos necesarios:
- `requirements.txt` - Dependencias de Python
- `Procfile` - Configuración para Render
- `.env` - Variables de entorno
- `build.sh` - Script de inicialización de BD
- `DEPLOY_RENDER.md` - Guía detallada
- Modificado `app.py` para inicializar BD automáticamente

El proyecto está **100% listo** para Render.

---

## 🎯 PASO 1: PREPARAR GITHUB (5 minutos)

### Si NO tienes repositorio Git:

```bash
cd /home/desarrollo/INFINITO-2U

# Inicializar git
git init

# Agregar archivos
git add .

# Commit inicial
git commit -m "Proyecto INFINITO-2U - Gestión de Condominios"

# Agregar remoto (cambiar TU_USUARIO por tu usuario de GitHub)
git remote add origin https://github.com/TU_USUARIO/INFINITO-2U.git

# Crear rama main y push
git branch -M main
git push -u origin main
```

### Si YA tienes repositorio:

```bash
cd /home/desarrollo/INFINITO-2U
git add .
git commit -m "Preparado para deployment en Render"
git push
```

---

## 🔧 PASO 2: CREAR CUENTA EN RENDER (3 minutos)

1. Ir a: **https://render.com**
2. Clickear **"Sign Up"**
3. Conectar con **GitHub**
4. Autorizar acceso al repositorio

---

## 📦 PASO 3: CREAR SERVICIO WEB (5 minutos)

### En el Dashboard de Render:

1. **New +** → **Web Service**
2. Seleccionar repositorio: **INFINITO-2U**
3. Configurar:

| Campo | Valor |
|-------|-------|
| Name | `infinito-2u` |
| Environment | `Python 3` |
| Build Command | `pip install -r requirements.txt && python -c "from base_datos import crear_base_datos; crear_base_datos()"` |
| Start Command | `gunicorn app:app` |
| Plan | **Free** |

4. Clickear **Create Web Service**

---

## 🔐 PASO 4: AGREGAR VARIABLES DE ENTORNO (3 minutos)

En Render Dashboard → Settings → **Environment**

Agregar estas variables:

```
FLASK_ENV = production
PORT = 10000
SECRET_KEY = infinito2u_secret_key_exposicion_2024
DEBUG = False
```

---

## 🚀 PASO 5: DEPLOY (2 minutos)

1. Render automáticamente detectará cambios en GitHub
2. O manualmente: **Manual Deploy** → **Deploy latest commit**
3. Esperar 2-3 minutos
4. Ver logs en "Logs"
5. Si todo está OK, verás:
   ```
   =====  Build successful
   ```

---

## 🌐 ACCEDER A TU APLICACIÓN

Una vez deployado, Render generará una URL como:

```
https://infinito-2u.onrender.com
```

O similar. La puedes encontrar en:
- Render Dashboard → Web Service → URL arriba a la izquierda

---

## 🔑 CREDENCIALES DE ACCESO

**Usuario:** `admin`  
**Contraseña:** `admin123`

(Cambiar después de la exposición)

---

## ⚠️ COSAS IMPORTANTES A SABER

### Base de Datos
- ✅ SQLite funciona en Render
- ⚠️ Los datos se BORRAN si Render reinicia (cada ~15 min sin actividad)
- ✅ Para la exposición/demo es perfecto
- ❌ Para datos permanentes = necesitas PostgreSQL (de pago)

### Límites del Free Tier
- RAM: 512 MB
- CPU: Compartido
- Uptime: 750 horas/mes (suficiente)
- Inactividad: Se pausa después de 15 min sin requests

### Tiempo de respuesta
- Primera carga: ~5 segundos (reinicia la app si estaba dormida)
- Resto de cargas: Normal (1-2 segundos)

---

## ✅ TESTING ANTES DE PUBLICAR (Recomendado)

### Localmente con gunicorn (como en Render):

```bash
pip install gunicorn
gunicorn app:app --bind 0.0.0.0:5000
```

Luego acceder a: **http://localhost:5000**

Si funciona localmente, funcionará en Render.

---

## 🆘 SOLUCIÓN DE PROBLEMAS

### "Error: Module not found"
→ Falta agregar a `requirements.txt`

### "Error: Port is already in use"
→ Cambiar puerto en `.env`

### "Error: Database locked"
→ Reiniciar aplicación en Render

### "Error en logs: ImportError"
→ Falta dependencia en `requirements.txt`

### "Application timeout"
→ Render reinició. Requiere mejorar rendimiento.

---

## 📊 MONITOREO EN RENDER

En tu Dashboard puedes ver:
- **Logs** - Errores y eventos
- **Metrics** - CPU, RAM, requets
- **Events** - Deploys, cambios

Si algo falla, los logs te dirán qué está mal.

---

## 📝 PARA LA EXPOSICIÓN

### Lo que debes presentar:

1. ✅ Diapositivas con screenshots de INFINITO-2U
2. ✅ Demo en vivo en Render (URL pública)
3. ✅ Mostrar funcionalidades:
   - Login
   - Panel admin
   - Gestión de residentes
   - Chatbot
   - Normatividad

### Recomendaciones:

- 📱 Tener versión local de respaldo
- 🌐 Compartir URL de Render en diapositivas
- ⏱️ Tener internet estable para demo
- 📞 Tener número telefónico para contacto

---

## 🔄 DESPUÉS DE LA EXPOSICIÓN

Deberías:

1. **Implementar seguridad** (Ver REPORTE_SEGURIDAD.md)
   - Hash de contraseñas
   - Variables de entorno
   - Validación de entrada

2. **Cambiar a PostgreSQL** para datos permanentes

3. **Cambiar credenciales de admin**

4. **Agregar tests**

5. **Mejorar performance**

---

## 📞 SOPORTE Y RECURSOS

| Recurso | Link |
|---------|------|
| Documentación Render | https://render.com/docs |
| Status Page | https://render-status.com/ |
| Soporte | https://render.com/support |
| Flask Docs | https://flask.palletsprojects.com/ |
| Gunicorn Docs | https://gunicorn.org/ |

---

## ✨ ESTADO DEL PROYECTO PARA RENDER

```
✅ app.py                - Modificado para BD automática
✅ base_datos.py        - Funciona con SQLite
✅ requirements.txt     - Actualizado con deps
✅ Procfile             - Configurado para Render
✅ .env                 - Variables de entorno
✅ build.sh             - Script de inicialización
✅ Templates HTML       - Listos
✅ Assets               - Listos
✅ Normatividad PDFs    - Listos

Estado: 🟢 LISTO PARA RENDER
Tiempo estimado: 20 minutos
```

---

## 🎯 RESUMEN RÁPIDO

```bash
# 1. Commitar a GitHub
git add . && git commit -m "Deploy prep" && git push

# 2. Crear cuenta en Render.com y conectar GitHub

# 3. New Web Service → Configurar como arriba

# 4. Agregar variables de entorno

# 5. Deploy automático

# 6. Acceder a URL pública (2-3 min después)
```

---

## ❓ CHECKLIST ANTES DE PRESENTAR

- [ ] URL de Render está funcionando
- [ ] Login funciona (admin/admin123)
- [ ] BD se inicializa correctamente
- [ ] Chatbot responde
- [ ] Todas las funcionalidades trabajando
- [ ] Compartir URL con profesores
- [ ] Diapositivas mencionan Render

---

**¡Listo! Tu proyecto está 100% preparado para Render.com** 🚀

Cualquier duda, revisar `DEPLOY_RENDER.md` para más detalles.

---

*Generado: 2026-10-23*  
*Proyecto: INFINITO-2U v1.0*  
*Estado: Listo para exposición universitaria*
