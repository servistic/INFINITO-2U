import os
import re
import unicodedata


# ============================================================
# CONFIGURACIÓN
# ============================================================

CARPETA_ACTUAL = os.path.dirname(
    os.path.abspath(__file__)
)

CARPETA_NORMATIVIDAD = os.path.join(
    CARPETA_ACTUAL,
    "assets",
    "Normatividad"
)


# ============================================================
# LECTOR DE PDF
# ============================================================

try:
    import pymupdf
    PDF_DISPONIBLE = True
except ImportError:
    PDF_DISPONIBLE = False


# ============================================================
# DOCUMENTOS NORMATIVOS
# ============================================================

DOCUMENTOS_NORMATIVOS = {

    "constitucion": [
        "constitucion-politica-colombia-1991",
        "constitucion politica colombia 1991"
    ],

    "ley 675": [
        "ley 675 de 2001",
        "ley_675_de_2001",
        "ley-675-de-2001"
    ],

    "ley 1801": [
        "ley_1801_de_2016",
        "ley 1801 de 2016",
        "ley-1801-de-2016"
    ],

    "codigo civil": [
        "codigo_civil_colombia",
        "codigo civil colombia"
    ],

    "codigo general del proceso": [
        "ley_1564_de_2012_codigo_general_del_proceso",
        "ley 1564 de 2012",
        "codigo general del proceso"
    ],

    "ley 640": [
        "ley_640_de_2001",
        "ley 640 de 2001"
    ],

    "ley 1581": [
        "ley_1581_de_2012",
        "ley 1581 de 2012",
        "proteccion de datos personales"
    ],

    "ley 1437": [
        "ley_1437_de_2011",
        "ley 1437 de 2011",
        "codigo de procedimiento administrativo"
    ],

    "codigo penal": [
        "codigo_penal_colombia",
        "codigo penal colombia"
    ],

    "guia jurisprudencial": [
        "guia_jurisprudencial_sobre_conceptos_acusatori",
        "guia jurisprudencial sobre conceptos acusatori"
    ],

    "ley 2450": [
        "ley 2450 del 4 de marzo de 2025",
        "ley 2450 de 2025",
        "ley acustica"
    ],

    "ordenamiento territorial": [
        "ordenamiento territorial para el desarrollo",
        "ordenamiento territorial"
    ],

    "sustento juridico": [
        "sustento juridico solido para sus actuaciones",
        "sustento juridico",
        "principales normas vigentes"
    ],

    "manual juridico comite": [
        "manual juridico del comite de convivencia",
        "manual juridico del comite",
        "comite de convivencia ph infinito"
    ],

    "manual convivencia": [
        "manual de convivencia y uso de zonas comunes",
        "uso de zonas comunes infinito 2u",
        "manual de convivencia"
    ]
}


# ============================================================
# NOMBRES PARA MOSTRAR AL USUARIO
# ============================================================

NOMBRES_DOCUMENTOS = {

    "constitucion":
        "Constitución Política de Colombia de 1991",

    "ley 675":
        "Ley 675 de 2001 - Régimen de Propiedad Horizontal",

    "ley 1801":
        "Ley 1801 de 2016 - Código Nacional de Seguridad y Convivencia Ciudadana",

    "codigo civil":
        "Código Civil de Colombia",

    "codigo general del proceso":
        "Ley 1564 de 2012 - Código General del Proceso",

    "ley 640":
        "Ley 640 de 2001 - Conciliación",

    "ley 1581":
        "Ley 1581 de 2012 - Protección de Datos Personales",

    "ley 1437":
        "Ley 1437 de 2011 - CPACA",

    "codigo penal":
        "Código Penal de Colombia",

    "guia jurisprudencial":
        "Guía jurisprudencial sobre conceptos acusatorios",

    "ley 2450":
        "Ley 2450 de 2025 - Ley acústica",

    "ordenamiento territorial":
        "Ordenamiento territorial para el desarrollo",

    "sustento juridico":
        "Sustento jurídico sólido para sus actuaciones",

    "manual juridico comite":
        "Manual Jurídico del Comité de Convivencia PH Infinito 2U",

    "manual convivencia":
        "Manual de Convivencia y Uso de Zonas Comunes - Infinito 2U"
}


# ============================================================
# SINÓNIMOS
# ============================================================

SINONIMOS_NORMATIVOS = {

    "excremento": [
        "excremento",
        "excrementos",
        "popo",
        "caca",
        "heces",
        "deposiciones",
        "materia fecal"
    ],

    "ruido": [
        "ruido",
        "ruidos",
        "bulla",
        "escandalo",
        "volumen alto",
        "musica fuerte",
        "musica alta",
        "ruido excesivo",
        "ruido molesto",
        "taladro",
        "decibeles",
        "decibelios",
        "emision de ruido",
        "contaminacion acustica"
    ],

    "conflicto": [
        "pelea",
        "peleas",
        "peleando",
        "rina",
        "rinas",
        "discusion",
        "discusiones",
        "agresion",
        "agresiones",
        "altercado",
        "altercados",
        "conflicto entre vecinos"
    ],

    "escombros": [
        "escombro",
        "escombros",
        "residuo de obra",
        "residuos de obra",
        "materiales de obra",
        "materiales de construccion",
        "restos de obra",
        "desechos de construccion"
    ]
}


# ============================================================
# EXPANSIONES PARA BÚSQUEDA
# ============================================================

EXPANSIONES_BUSQUEDA = {

    "popo": [
        "excremento",
        "heces",
        "deposiciones"
    ],

    "caca": [
        "excremento",
        "heces"
    ],

    "heces": [
        "excremento",
        "deposiciones"
    ],

    "bulla": [
        "ruido",
        "emision",
        "acustica"
    ],

    "escandalo": [
        "ruido",
        "perturbacion"
    ],

    "volumen alto": [
        "ruido",
        "emision"
    ],

    "musica fuerte": [
        "ruido"
    ],

    "musica alta": [
        "ruido"
    ],

    "ruido molesto": [
        "ruido",
        "perturbacion"
    ],

    "ruido excesivo": [
        "ruido",
        "emision"
    ],

    "taladro": [
        "ruido"
    ],

    "decibeles": [
        "ruido",
        "emision"
    ],

    "decibelios": [
        "ruido",
        "emision"
    ],

    "peleando": [
        "pelea",
        "conflicto",
        "agresion"
    ],

    "pelea": [
        "conflicto",
        "agresion"
    ],

    "rina": [
        "pelea",
        "conflicto"
    ],

    "discusion": [
        "conflicto"
    ],

    "agresion": [
        "conflicto",
        "violencia"
    ],

    "altercado": [
        "conflicto",
        "convivencia"
    ],

    "conflicto entre vecinos": [
        "conflicto",
        "convivencia",
        "comite"
    ],

    "escombros": [
        "residuos",
        "obra",
        "construccion"
    ],

    "escombro": [
        "residuos",
        "obra"
    ],

    "residuos de obra": [
        "escombros",
        "obra",
        "construccion"
    ],

    "materiales de construccion": [
        "obra",
        "residuos"
    ],

    "restos de obra": [
        "escombros",
        "residuos",
        "obra"
    ]
}


# ============================================================
# NORMALIZAR TEXTO
# ============================================================

def normalizar_texto(texto):

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

    texto = texto.replace("_", " ")
    texto = texto.replace("-", " ")

    texto = re.sub(
        r"\s+",
        " ",
        texto
    )

    return texto.strip()


# ============================================================
# OBTENER ARCHIVOS PDF
# ============================================================

def obtener_archivos_pdf():

    archivos = []

    if not os.path.exists(CARPETA_NORMATIVIDAD):
        return archivos

    try:

        for archivo in os.listdir(
            CARPETA_NORMATIVIDAD
        ):

            if archivo.lower().endswith(".pdf"):

                ruta = os.path.join(
                    CARPETA_NORMATIVIDAD,
                    archivo
                )

                if os.path.isfile(ruta):
                    archivos.append(ruta)

    except Exception:
        pass

    return archivos


# ============================================================
# IDENTIFICAR DOCUMENTOS
# ============================================================

def identificar_documentos(pregunta):

    pregunta = normalizar_texto(pregunta)

    reglas = {

        "ley 675": [
            "ley 675",
            "675 de 2001",
            "propiedad horizontal",
            "asamblea",
            "administrador",
            "administracion",
            "cuota de administracion",
            "bienes comunes",
            "bienes privados",
            "escombros",
            "residuos de obra",
            "materiales de construccion",
            "restos de obra"
        ],

        "ley 1801": [
            "ley 1801",
            "1801 de 2016",
            "convivencia ciudadana",
            "ruido",
            "bulla",
            "escandalo",
            "volumen alto",
            "musica fuerte",
            "ruido molesto",
            "ruido excesivo",
            "perturbacion",
            "pelea",
            "peleando",
            "rina",
            "discusion",
            "agresion",
            "altercado",
            "conflicto entre vecinos",
            "policia"
        ],

        "codigo civil": [
            "codigo civil",
            "responsabilidad civil",
            "danos",
            "perjuicios",
            "propietario",
            "arrendatario"
        ],

        "codigo general del proceso": [
            "ley 1564",
            "codigo general del proceso",
            "demanda",
            "notificacion",
            "proceso civil"
        ],

        "ley 640": [
            "ley 640",
            "conciliacion",
            "conciliatorio",
            "audiencia de conciliacion"
        ],

        "ley 1581": [
            "ley 1581",
            "proteccion de datos",
            "datos personales",
            "tratamiento de datos",
            "habeas data"
        ],

        "ley 1437": [
            "ley 1437",
            "cpaca",
            "codigo de procedimiento administrativo",
            "acto administrativo",
            "contencioso administrativo"
        ],

        "codigo penal": [
            "codigo penal",
            "delito",
            "hurto",
            "amenaza",
            "lesiones",
            "violencia",
            "agresion"
        ],

        "guia jurisprudencial": [
            "guia jurisprudencial",
            "jurisprudencia",
            "acusatorio",
            "acusatorios"
        ],

        "ley 2450": [
            "ley 2450",
            "2450 de 2025",
            "ley acustica",
            "ruido",
            "bulla",
            "escandalo",
            "volumen alto",
            "musica fuerte",
            "musica alta",
            "ruido excesivo",
            "ruido molesto",
            "taladro",
            "decibeles",
            "decibelios",
            "emision de ruido",
            "contaminacion acustica"
        ],

        "ordenamiento territorial": [
            "ordenamiento territorial",
            "pot",
            "uso del suelo",
            "desarrollo territorial"
        ],

        "sustento juridico": [
            "sustento juridico",
            "normas vigentes",
            "principales normas",
            "fundamento juridico"
        ],

        "manual juridico comite": [
            "manual juridico",
            "comite de convivencia",
            "procedimiento del comite",
            "conflicto entre vecinos",
            "pelea",
            "peleando",
            "rina",
            "discusion",
            "agresion",
            "altercado"
        ],

        "manual convivencia": [
            "manual de convivencia",
            "uso de zonas comunes",
            "reglamento interno",
            "horarios del conjunto",
            "trasteo",
            "trasteos",
            "pelea",
            "peleando",
            "rina",
            "discusion",
            "agresion",
            "altercado",
            "conflicto entre vecinos",
            "excremento",
            "popo",
            "caca",
            "heces",
            "escombros",
            "residuos de obra"
        ]
    }

    documentos = []

    for documento, palabras in reglas.items():

        patrones_normalizados = [
            normalizar_texto(palabra)
            for palabra in palabras
        ]

        if any(
            palabra in pregunta
            for palabra in patrones_normalizados
        ):
            documentos.append(documento)

    return documentos


# ============================================================
# ENCONTRAR PDF
# ============================================================

def encontrar_pdf(documento):

    archivos = obtener_archivos_pdf()

    patrones = DOCUMENTOS_NORMATIVOS.get(
        documento,
        []
    )

    patrones = [
        normalizar_texto(patron)
        for patron in patrones
    ]

    for ruta in archivos:

        nombre = os.path.splitext(
            os.path.basename(ruta)
        )[0]

        nombre = normalizar_texto(nombre)

        for patron in patrones:

            if patron in nombre:
                return ruta

    return None


# ============================================================
# EXTRAER TEXTO DEL PDF
# ============================================================

def extraer_texto_pdf(ruta):

    if not PDF_DISPONIBLE:
        return ""

    if not ruta:
        return ""

    if not os.path.exists(ruta):
        return ""

    try:

        documento = pymupdf.open(ruta)

        paginas = []

        for pagina in documento:

            try:

                texto = pagina.get_text()

                if texto:
                    paginas.append(texto)

            except Exception:
                continue

        documento.close()

        return "\n".join(paginas)

    except Exception:
        return ""


# ============================================================
# DIVIDIR TEXTO
# ============================================================

def dividir_en_fragmentos(
    texto,
    tamano=2000
):

    texto = texto.strip()

    if not texto:
        return []

    parrafos = re.split(
        r"\n\s*\n",
        texto
    )

    fragmentos = []
    actual = ""

    for parrafo in parrafos:

        parrafo = re.sub(
            r"\s+",
            " ",
            parrafo
        ).strip()

        if not parrafo:
            continue

        if len(actual) + len(parrafo) <= tamano:

            if actual:
                actual += " "

            actual += parrafo

        else:

            if actual:
                fragmentos.append(
                    actual.strip()
                )

            actual = parrafo

    if actual:
        fragmentos.append(
            actual.strip()
        )

    return fragmentos


# ============================================================
# PALABRAS VACÍAS
# ============================================================

PALABRAS_VACIAS = {

    "que",
    "como",
    "cual",
    "cuales",
    "donde",
    "cuando",
    "porque",
    "para",
    "por",
    "con",
    "una",
    "uno",
    "unos",
    "unas",
    "los",
    "las",
    "del",
    "de",
    "la",
    "el",
    "sobre",
    "dice",
    "diga",
    "decir",
    "me",
    "puede",
    "puedo",
    "quiero",
    "necesito",
    "hay",
    "es",
    "son",
    "se",
    "al",
    "en",
    "y",
    "o",
    "a",
    "un",
    "su",
    "sus",
    "esta",
    "este",
    "estas",
    "estos",
    "tiene",
    "tienen",
    "informacion",
    "norma",
    "normas",
    "ley",
    "codigo",
    "documento"
}


# ============================================================
# PALABRAS IMPORTANTES
# ============================================================

def obtener_palabras_importantes(pregunta):

    pregunta = normalizar_texto(
        pregunta
    )

    palabras = re.findall(
        r"[a-z0-9]+",
        pregunta
    )

    resultado = []

    for palabra in palabras:

        if len(palabra) < 3:
            continue

        if palabra in PALABRAS_VACIAS:
            continue

        if palabra not in resultado:
            resultado.append(palabra)

    # Agregar términos relacionados
    # para mejorar la búsqueda en PDF

    for alias, expansion in EXPANSIONES_BUSQUEDA.items():

        alias_normalizado = normalizar_texto(alias)

        if alias_normalizado in pregunta:

            for termino in expansion:

                termino_normalizado = normalizar_texto(
                    termino
                )

                for palabra in re.findall(
                    r"[a-z0-9]+",
                    termino_normalizado
                ):

                    if (
                        palabra not in resultado
                        and palabra not in PALABRAS_VACIAS
                    ):
                        resultado.append(palabra)

    return resultado


# ============================================================
# NOMBRE DEL DOCUMENTO
# ============================================================

def nombre_documento_desde_archivo(ruta):

    nombre = normalizar_texto(
        os.path.basename(ruta)
    )

    for clave, patrones in DOCUMENTOS_NORMATIVOS.items():

        for patron in patrones:

            if normalizar_texto(patron) in nombre:

                return NOMBRES_DOCUMENTOS.get(
                    clave,
                    clave
                )

    return os.path.splitext(
        os.path.basename(ruta)
    )[0]


# ============================================================
# BÚSQUEDA EN TODOS LOS DOCUMENTOS
# ============================================================

def buscar_en_todos_los_documentos(pregunta):

    archivos = obtener_archivos_pdf()

    palabras = obtener_palabras_importantes(
        pregunta
    )

    if not archivos or not palabras:
        return []

    prioritarios = identificar_documentos(
        pregunta
    )

    candidatos = []

    for ruta in archivos:

        texto = extraer_texto_pdf(
            ruta
        )

        if not texto:
            continue

        nombre_norm = normalizar_texto(
            os.path.basename(ruta)
        )

        prioridad = 0

        for doc in prioritarios:

            for patron in DOCUMENTOS_NORMATIVOS.get(
                doc,
                []
            ):

                patron_norm = normalizar_texto(
                    patron
                )

                if patron_norm in nombre_norm:
                    prioridad += 5

        fragmentos = dividir_en_fragmentos(
            texto,
            tamano=1800
        )

        for fragmento in fragmentos:

            frag_norm = normalizar_texto(
                fragmento
            )

            coincidencias = 0

            for palabra in palabras:

                if re.search(
                    r"(?<![a-z0-9])"
                    + re.escape(palabra)
                    + r"(?![a-z0-9])",
                    frag_norm
                ):
                    coincidencias += 1

            if coincidencias:

                porcentaje = (
                    coincidencias /
                    len(palabras)
                )

                puntaje = (
                    coincidencias * 10
                    + porcentaje * 10
                    + prioridad
                )

                candidatos.append({

                    "puntaje": puntaje,

                    "documento":
                        nombre_documento_desde_archivo(
                            ruta
                        ),

                    "archivo":
                        os.path.basename(ruta),

                    "fragmento":
                        fragmento
                })

    candidatos.sort(
        key=lambda x: x["puntaje"],
        reverse=True
    )

    seleccionados = []

    cantidad_por_documento = {}

    for item in candidatos:

        doc = item["documento"]

        if cantidad_por_documento.get(
            doc,
            0
        ) >= 2:
            continue

        seleccionados.append(item)

        cantidad_por_documento[doc] = (
            cantidad_por_documento.get(
                doc,
                0
            ) + 1
        )

        if len(seleccionados) >= 8:
            break

    return seleccionados


# ============================================================
# CONSULTAR NORMATIVIDAD
# ============================================================

def consultar_normatividad(pregunta):

    if not PDF_DISPONIBLE:

        return """
⚠️ El lector de documentos PDF no está disponible.

Para habilitar la consulta normativa instala PyMuPDF:

py -m pip install pymupdf
"""

    if not os.path.exists(
        CARPETA_NORMATIVIDAD
    ):

        return """
⚠️ No encontré la carpeta de normatividad.

La aplicación está buscando los documentos en:

assets\\normatividad
"""

    resultados = buscar_en_todos_los_documentos(
        pregunta
    )

    if not resultados:
        return None

    respuesta = [

        "📚 FUENTES NORMATIVAS ENCONTRADAS",
        "",

        "Sí, encontré información relacionada "
        "en los documentos disponibles:",
        ""
    ]

    for item in resultados:

        fragmento = item["fragmento"].strip()

        if len(fragmento) > 1800:

            fragmento = (
                fragmento[:1800].rstrip()
                + "..."
            )

        respuesta.extend([

            f"📖 {item['documento']}",

            f"📄 Documento: {item['archivo']}",

            "",

            "🔎 Información encontrada:",

            fragmento,

            "",

            "────────────────────────────",

            ""
        ])

    respuesta.extend([

        "ℹ️ La información anterior fue localizada "
        "directamente dentro de los PDF de la carpeta "
        "assets\\normatividad.",

        "",

        "⚖️ Esta respuesta corresponde a una localización "
        "de información dentro de los documentos disponibles "
        "y no sustituye la revisión integral del documento "
        "ni la verificación de vigencia de la norma."
    ])

    return "\n".join(
        respuesta
    )


# ============================================================
# RESPUESTAS GENERALES
# ============================================================

RESPUESTAS = {

    "residentes": """
Los residentes son las personas que habitan en las unidades privadas
del conjunto residencial.

En INFINITO 2U se pueden registrar:

• Documento de identidad.
• Nombre completo.
• Teléfono.
• Correo electrónico.
• Apartamento.
• Tipo de residente.
• Estado.

Es importante mantener esta información actualizada para facilitar
la administración y la comunicación dentro de la propiedad horizontal.
""",

    "registrar residente": """
Para registrar un residente:

1. Ingrese al módulo RESIDENTES.
2. Digite el documento.
3. Escriba el nombre completo.
4. Registre el teléfono.
5. Registre el correo electrónico.
6. Indique el apartamento.
7. Seleccione el tipo de residente.
8. Seleccione el estado.
9. Presione AGREGAR.

También puede editar, eliminar y consultar los residentes registrados.
""",

    "propietario": """
El propietario es la persona que posee legalmente una unidad privada
dentro de la propiedad horizontal.

Debe cumplir las normas establecidas por la administración,
el reglamento de propiedad horizontal y las normas de convivencia.
""",

    "arrendatario": """
El arrendatario es la persona que ocupa una unidad privada mediante
un contrato de arrendamiento.

Aunque no sea propietario, debe cumplir las normas de convivencia,
seguridad, uso de zonas comunes y demás disposiciones de la
propiedad horizontal.
""",

    "visitantes": """
Los visitantes deben respetar las normas de seguridad y convivencia
del conjunto residencial.

Se recomienda:

• Registrar el ingreso cuando sea solicitado.
• Respetar los horarios establecidos.
• Cumplir las indicaciones de vigilancia.
• Cuidar las zonas comunes.
• Evitar generar ruido excesivo.
• Respetar a residentes y trabajadores.
• No ingresar a zonas restringidas.
""",

    "visitas": """
Las visitas deben cumplir los protocolos establecidos por la
administración y vigilancia.

El ingreso puede estar sujeto a identificación, autorización
del residente y registro de visitante.
""",

    "vigilancia": """
El personal de vigilancia apoya el control de acceso y la seguridad
de la propiedad horizontal.

Los residentes y visitantes deben seguir las instrucciones de seguridad
y colaborar con los procedimientos establecidos.
""",

    "mascotas": """
Las mascotas requieren una tenencia responsable y respetuosa.

Los propietarios o tenedores deben:

• Mantener a sus mascotas bajo control.
• Recoger inmediatamente sus excrementos.
• Evitar daños en las zonas comunes.
• Evitar ruidos que afecten a otros residentes.
• Utilizar correa cuando corresponda.
• Respetar las áreas donde existan restricciones.
• Garantizar condiciones adecuadas de bienestar.
""",

    "perros": """
Los perros deben mantenerse bajo control de su responsable.

En las zonas comunes se recomienda utilizar correa y recoger
inmediatamente sus excrementos.

El propietario o tenedor debe evitar situaciones que representen
un riesgo para otros residentes, visitantes o animales.
""",

    "gatos": """
Los gatos también deben mantenerse bajo condiciones adecuadas
de cuidado y responsabilidad.

Su tenedor debe evitar que ocasionen daños, molestias o riesgos
para otros residentes y para las zonas comunes.
""",

    "excrementos": """
Los excrementos de las mascotas deben recogerse inmediatamente
y depositarse correctamente.

No deben dejarse residuos de mascotas en pasillos, ascensores,
jardines, zonas comunes o espacios de circulación.
""",

    "normas": """
Las normas de convivencia buscan garantizar el respeto,
la seguridad, la tranquilidad y el buen uso de los espacios comunes.

Entre las principales recomendaciones están:

• Respetar a los demás residentes.
• Evitar ruidos excesivos.
• Cuidar las zonas comunes.
• Manejar correctamente los residuos.
• Respetar las normas para mascotas.
• Cumplir las reglas de parqueaderos.
• Respetar los horarios de reparaciones.
• Atender las normas de seguridad.
""",

    "convivencia": """
La convivencia en propiedad horizontal se basa en el respeto,
la tolerancia, la comunicación y el cumplimiento de las normas.

Ante un conflicto se recomienda:

1. Mantener la calma.
2. Intentar solucionar el problema mediante el diálogo.
3. Informar a la administración cuando sea necesario.
4. Acudir al comité de convivencia cuando corresponda.
5. Utilizar los mecanismos establecidos.
""",

    "ruido": """
Se debe evitar generar ruidos que afecten la tranquilidad
de los demás residentes.

Se recomienda:

• Evitar música a volumen elevado.
• Respetar los horarios de descanso.
• Controlar los ruidos producidos por mascotas.
• Evitar golpes innecesarios.
• Respetar los horarios establecidos para reparaciones.

Si existe un conflicto por ruido, se recomienda intentar primero
el diálogo y posteriormente acudir a la administración.
""",

    "fiestas": """
Las reuniones y fiestas deben realizarse respetando las normas
de convivencia y los horarios establecidos.

El volumen de la música debe mantenerse en un nivel que no afecte
la tranquilidad de los demás residentes.
""",

    "residuos": """
Los residuos deben manejarse correctamente para mantener la limpieza
y salubridad del conjunto.

Recuerde:

• Separar los residuos correctamente.
• Utilizar las canecas correspondientes.
• No arrojar basura en zonas comunes.
• No dejar bolsas en pasillos o escaleras.
• Depositar los residuos en los lugares establecidos.
• Respetar los horarios de disposición cuando existan.
""",

    "basura": """
La basura debe depositarse únicamente en los puntos destinados
para su disposición.

No se deben dejar bolsas en pasillos, ascensores, escaleras,
jardines o zonas comunes.
""",

    "reciclaje": """
Para realizar una correcta separación de residuos:

• Aprovechables: materiales que pueden ser reciclados.
• Orgánicos: residuos de alimentos y materia orgánica.
• No aprovechables: residuos que no pueden recuperarse.

Siempre deben utilizarse los recipientes establecidos por el conjunto.
""",

    "zonas comunes": """
Las zonas comunes son espacios destinados al uso colectivo
de residentes y visitantes.

Deben utilizarse de manera responsable:

• No causar daños.
• Mantener la limpieza.
• Respetar los horarios.
• Respetar a los demás usuarios.
• No utilizar espacios restringidos.
• Seguir las instrucciones de la administración.
""",

    "parqueaderos": """
Los parqueaderos deben utilizarse únicamente para el fin establecido.

Se recomienda:

• Respetar los espacios asignados.
• No ocupar espacios ajenos.
• Respetar las zonas de circulación.
• No bloquear accesos.
• Mantener una velocidad segura.
• Respetar las normas para visitantes.
""",

    "reparaciones": """
Las reparaciones dentro de una unidad privada deben realizarse
respetando las normas de la propiedad horizontal.

Antes de realizar una obra se recomienda:

• Consultar las reglas del conjunto.
• Respetar los horarios autorizados.
• Evitar afectar zonas comunes.
• Evitar ruidos excesivos.
• Informar a la administración cuando sea necesario.
• Cumplir los requisitos de seguridad.
""",

    "obras": """
Las obras y modificaciones deben respetar el reglamento de propiedad
horizontal y las disposiciones de la administración.

No se deben realizar trabajos que afecten elementos comunes,
estructuras o instalaciones sin las autorizaciones correspondientes.
""",

    "comité de convivencia": """
El comité de convivencia es un mecanismo para apoyar la solución
pacífica de conflictos entre residentes.

Puede intervenir en situaciones relacionadas con:

• Problemas de convivencia.
• Conflictos entre vecinos.
• Ruido.
• Mascotas.
• Uso de zonas comunes.
• Situaciones que afecten la tranquilidad.

Su objetivo es promover el diálogo y la convivencia.
""",

    "conflictos": """
Ante un conflicto entre vecinos se recomienda:

1. Mantener una comunicación respetuosa.
2. Intentar solucionar la situación mediante el diálogo.
3. Informar a la administración si el problema continúa.
4. Acudir al comité de convivencia cuando corresponda.
5. Utilizar los mecanismos establecidos.
""",

    "emergencia": """
Ante una emergencia:

1. Mantenga la calma.
2. Identifique el tipo de emergencia.
3. Avise a vigilancia o administración.
4. Siga las instrucciones de evacuación.
5. Utilice las rutas de evacuación señalizadas.
6. No utilice ascensores durante una evacuación por incendio.
7. Ayude a quienes necesiten apoyo.
""",

    "incendio": """
En caso de incendio:

• Mantenga la calma.
• Avise inmediatamente a vigilancia o administración.
• Active la alarma si existe.
• Evacúe utilizando las rutas señalizadas.
• No utilice ascensores.
• No regrese por objetos personales.
• Siga las instrucciones del personal encargado.
""",

    "seguridad": """
Para mejorar la seguridad del conjunto:

• No permita el ingreso de personas desconocidas.
• Informe situaciones sospechosas.
• Respete los controles de acceso.
• Mantenga puertas y accesos cerrados.
• No comparta información de seguridad con desconocidos.
• Siga las instrucciones del personal de vigilancia.
""",

    "administracion": """
La administración se encarga de apoyar la gestión de la propiedad
horizontal y el cumplimiento de las disposiciones establecidas.

Los residentes pueden acudir a la administración para reportar
situaciones relacionadas con convivencia, mantenimiento, seguridad,
zonas comunes y otros asuntos del conjunto.
""",

    "normatividad": """
La propiedad horizontal en Colombia está regulada principalmente
por la Ley 675 de 2001, además de otras normas que puedan resultar
aplicables según la situación.

También deben tenerse en cuenta el reglamento de propiedad horizontal,
los manuales y las normas internas de convivencia del conjunto.
""",

    "manual": """
El Manual Interactivo permite consultar diferentes temas relacionados
con la propiedad horizontal de manera sencilla.

Puede encontrar información sobre:

• Residentes.
• Visitantes.
• Mascotas.
• Residuos.
• Reparaciones.
• Comité de convivencia.
• Emergencias.
• Normas de convivencia.
""",

    "codigo qr": """
El código QR permite acceder desde un celular a la encuesta o servicio
habilitado por INFINITO 2U.

Para utilizarlo:

1. Abra la cámara de su celular.
2. Apunte hacia el código QR.
3. Abra el enlace que aparece.
4. Siga las instrucciones.
"""
}


# ============================================================
# OBTENER RESPUESTA
# ============================================================

def obtener_respuesta(pregunta):

    if not pregunta:
        return """
Escribe una pregunta para poder ayudarte.
"""

    pregunta_original = str(
        pregunta
    )

    pregunta = normalizar_texto(
        pregunta_original
    )


    # ========================================================
    # PRIMERO: BUSCAR EN LOS PDF
    # ========================================================

    respuesta_normativa = consultar_normatividad(
        pregunta_original
    )

    if respuesta_normativa:
        return respuesta_normativa


    # ========================================================
    # SALUDOS
    # ========================================================

    saludos = [
        "hola",
        "holi",
        "buenos dias",
        "buenas tardes",
        "buenas noches",
        "hey"
    ]

    if pregunta in saludos:

        return """
¡Hola! 👋

Soy el asistente virtual de INFINITO 2U.

Puedo ayudarte con:

• Residentes
• Visitantes
• Mascotas
• Normas de convivencia
• Residuos
• Zonas comunes
• Parqueaderos
• Reparaciones
• Emergencias
• Seguridad
• Normatividad

También puedo consultar los documentos normativos
almacenados en la carpeta assets\\normatividad.

¿Sobre qué tema deseas información?
"""


    # ========================================================
    # DESPEDIDA
    # ========================================================

    if pregunta in [
        "gracias",
        "muchas gracias",
        "ok gracias",
        "gracias chatbot"
    ]:

        return """
¡Con mucho gusto! 😊

Estoy aquí para ayudarte con cualquier consulta relacionada
con INFINITO 2U y la propiedad horizontal.
"""


    # ========================================================
    # PALABRAS CLAVE
    # ========================================================

    palabras_clave = {

        "registrar residente":
            "registrar residente",

        "residentes":
            "residentes",

        "residente":
            "residentes",

        "habitante":
            "residentes",

        "habitantes":
            "residentes",

        "propietarios":
            "propietario",

        "propietario":
            "propietario",

        "dueño":
            "propietario",

        "dueno":
            "propietario",

        "arrendatarios":
            "arrendatario",

        "arrendatario":
            "arrendatario",

        "inquilino":
            "arrendatario",

        "inquilinos":
            "arrendatario",

        "visitantes":
            "visitantes",

        "visitante":
            "visitantes",

        "visitas":
            "visitas",

        "visita":
            "visitas",

        "invitado":
            "visitas",

        "invitados":
            "visitas",

        "vigilancia":
            "vigilancia",

        "vigilante":
            "vigilancia",

        "porteria":
            "vigilancia",

        "mascotas":
            "mascotas",

        "mascota":
            "mascotas",

        "perros":
            "perros",

        "perro":
            "perros",

        "canino":
            "perros",

        "gatos":
            "gatos",

        "gato":
            "gatos",

        "felino":
            "gatos",

        "excrementos":
            "excrementos",

        "excremento":
            "excrementos",

        "heces":
            "excrementos",

        "popo":
            "excrementos",

        "caca":
            "excrementos",

        "normas":
            "normas",

        "norma":
            "normas",

        "reglas":
            "normas",

        "regla":
            "normas",

        "convivencia":
            "convivencia",

        "ruidos":
            "ruido",

        "ruido":
            "ruido",

        "bulla":
            "ruido",

        "escandalo":
            "ruido",

        "volumen alto":
            "ruido",

        "musica":
            "ruido",

        "musica fuerte":
            "ruido",

        "musica alta":
            "ruido",

        "ruido molesto":
            "ruido",

        "ruido excesivo":
            "ruido",

        "taladro":
            "ruido",

        "decibeles":
            "ruido",

        "decibelios":
            "ruido",

        "fiestas":
            "fiestas",

        "fiesta":
            "fiestas",

        "parranda":
            "fiestas",

        "residuos":
            "residuos",

        "residuo":
            "residuos",

        "desechos":
            "residuos",

        "escombro":
            "residuos",

        "escombros":
            "residuos",

        "residuos de obra":
            "residuos",

        "materiales de obra":
            "residuos",

        "materiales de construccion":
            "residuos",

        "restos de obra":
            "residuos",

        "basura":
            "basura",

        "reciclaje":
            "reciclaje",

        "reciclar":
            "reciclaje",

        "zonas comunes":
            "zonas comunes",

        "zona comun":
            "zonas comunes",

        "ascensor":
            "ascensor",

        "ascensores":
            "ascensor",

        "pasillos":
            "pasillos",

        "pasillo":
            "pasillos",

        "escaleras":
            "escaleras",

        "escalera":
            "escaleras",

        "parqueaderos":
            "parqueaderos",

        "parqueadero":
            "parqueaderos",

        "estacionamiento":
            "parqueaderos",

        "bicicletas":
            "bicicletas",

        "bicicleta":
            "bicicletas",

        "reparaciones":
            "reparaciones",

        "reparacion":
            "reparaciones",

        "remodelacion":
            "reparaciones",

        "remodelaciones":
            "reparaciones",

        "arreglo":
            "reparaciones",

        "arreglos":
            "reparaciones",

        "obras":
            "obras",

        "obra":
            "obras",

        "construccion":
            "obras",

        "trasteo":
            "reparaciones",

        "trasteos":
            "reparaciones",

        "comite de convivencia":
            "comité de convivencia",

        "comite":
            "comité de convivencia",

        "comité":
            "comité de convivencia",

        "conflictos":
            "conflictos",

        "conflicto":
            "conflictos",

        "pelea":
            "conflictos",

        "peleas":
            "conflictos",

        "peleando":
            "conflictos",

        "rina":
            "conflictos",

        "rinas":
            "conflictos",

        "altercado":
            "conflictos",

        "discusion":
            "conflictos",

        "agresion":
            "conflictos",

        "vecino":
            "conflictos",

        "vecinos":
            "conflictos",

        "emergencias":
            "emergencia",

        "emergencia":
            "emergencia",

        "incendio":
            "incendio",

        "fuego":
            "incendio",

        "humo":
            "incendio",

        "temblor":
            "temblor",

        "sismo":
            "temblor",

        "terremoto":
            "temblor",

        "fuga de gas":
            "fuga de gas",

        "seguridad":
            "seguridad",

        "inseguridad":
            "seguridad",

        "robo":
            "seguridad",

        "hurto":
            "seguridad",

        "administracion":
            "administracion",

        "administrador":
            "administracion",

        "normatividad":
            "normatividad",

        "propiedad horizontal":
            "normatividad",

        "manual interactivo":
            "manual",

        "manual completo":
            "manual",

        "manual":
            "manual",

        "codigo qr":
            "codigo qr",

        "qr":
            "codigo qr"
    }


    # ========================================================
    # BUSCAR RESPUESTA
    # ========================================================

    for palabra, respuesta in sorted(
        palabras_clave.items(),
        key=lambda elemento: len(
            elemento[0]
        ),
        reverse=True
    ):

        palabra_normalizada = normalizar_texto(
            palabra
        )

        if palabra_normalizada in pregunta:

            return RESPUESTAS.get(
                respuesta,
                RESPUESTAS.get(
                    "normatividad",
                    "No encontré información."
                )
            )


    # ========================================================
    # RESPUESTA POR DEFECTO
    # ========================================================

    return """
🤔 No encontré una respuesta específica para esa pregunta.

Puedo ayudarte con:

👥 Residentes
🚪 Visitantes
🐶 Mascotas
📖 Normas de convivencia
🔊 Ruido
♻️ Residuos y reciclaje
🏢 Zonas comunes
🚗 Parqueaderos
🔧 Reparaciones
🤝 Comité de convivencia
🚨 Emergencias
🛡️ Seguridad
⚖️ Normatividad
📚 Manual
📱 Código QR

También puedo consultar los documentos normativos
que se encuentran en:

assets\\normatividad

Puedes preguntarme, por ejemplo:

• ¿Qué dice la Ley 675 sobre las cuotas de administración?
• ¿Qué establece la Ley 1801 sobre convivencia?
• ¿Qué dice la Ley 1581 sobre protección de datos?
• ¿Qué dice el Código Civil?
• ¿Qué dice la Ley 2450 sobre el ruido?
• ¿Qué puedo hacer si un vecino hace mucho ruido?
• ¿Qué hago si hay una pelea entre vecinos?
• ¿Qué hago con los escombros de una obra?
• ¿Qué dice la norma sobre los excrementos de las mascotas?
"""