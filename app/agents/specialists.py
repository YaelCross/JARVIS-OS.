from app.agents.base_agent import Agent
from app.tools import apps, canva, desktop, documents, mentions, system, trello, web


# ==================================================
# DEFINICIÓN DE LOS AGENTES ESPECIALISTAS
# ==================================================
# Para agregar un agente nuevo: añade una entrada a esta
# lista con sus herramientas. El orquestador lo detecta solo.

SPECIALISTS = [
    {
        "key": "apps",
        "name": "Agente de Aplicaciones",
        "role": "abrir, cerrar, enfocar, minimizar y maximizar programas "
                "y ventanas; ver qué procesos están activos.",
        "instructions": (
            "Antes de enfocar, minimizar o cerrar, usa listar_ventanas para "
            "encontrar el título exacto. Cierra procesos solo si te lo piden."
        ),
        "tools": apps.TOOLS,
    },
    {
        "key": "sistema",
        "name": "Agente de Sistema",
        "role": "leer, buscar y escribir archivos; revisar el estado de la "
                "PC; ejecutar comandos de PowerShell.",
        "instructions": (
            "La PC usa Windows. Prefiere las herramientas de archivos antes "
            "que PowerShell. Cuando uses PowerShell, escribe comandos "
            "concretos y seguros, y explica en tu respuesta qué hicieron. "
            "Al leer documentos largos, resume lo importante."
        ),
        "tools": system.TOOLS,
    },
    {
        "key": "web",
        "name": "Agente Web",
        "role": "buscar en Google y YouTube, abrir sitios e investigar en "
                "internet leyendo el contenido de páginas.",
        "instructions": (
            "Si Yael quiere VER algo, ábrelo en el navegador (buscar_google, "
            "buscar_youtube, abrir_sitio). Si quiere SABER algo, investiga con "
            "buscar_en_internet y leer_pagina y responde con un resumen y las "
            "fuentes."
        ),
        "tools": web.TOOLS,
    },
    {
        "key": "escritorio",
        "name": "Agente de Escritorio",
        "role": "controlar teclado y ratón: escribir texto en la app activa, "
                "atajos de teclado, clics y capturas de pantalla.",
        "instructions": (
            "Escribe y presiona teclas sobre la ventana que esté activa. Si "
            "necesitas otra ventana al frente, dilo en tu respuesta para que "
            "el Agente de Aplicaciones la enfoque primero. Para clics, usa "
            "info_pantalla para conocer la resolución."
        ),
        "tools": desktop.TOOLS,
    },
    {
        "key": "contenido",
        "name": "Agente de Contenido",
        "role": "escribir guiones (videos, reels, TikTok, YouTube, podcasts, "
                "ventas) y crear prompts de nivel especialista para otras IA.",
        "instructions": (
            "GUIONES: incluye gancho en los primeros 3 segundos, desarrollo, "
            "llamado a la acción, duración estimada e indicaciones de escena "
            "(toma, texto en pantalla, música). Adapta tono y duración a la "
            "plataforma.\n"
            "PROMPTS: redacta prompts listos para usar con rol experto, "
            "contexto, tarea, pasos, restricciones, formato de salida y un "
            "ejemplo si ayuda. Para prompts de imagen/video incluye estilo, "
            "composición, iluminación, cámara y relación de aspecto.\n"
            "Guarda siempre el resultado con guardar_documento (categoría "
            "'guiones' o 'prompts') y entrega el texto completo en tu respuesta."
        ),
        "tools": documents.TOOLS + web.TOOLS_INVESTIGACION + system.TOOLS_ARCHIVOS,
    },
    {
        "key": "marketing",
        "name": "Agente de Marketing",
        "role": "diseñar campañas publicitarias completas para Meta "
                "(Facebook/Instagram), TikTok, Google y YouTube.",
        "instructions": (
            "Una campaña incluye: objetivo y KPI, público y buyer persona, "
            "oferta y propuesta de valor, estructura (campaña / conjuntos / "
            "anuncios), 3 a 5 variantes de copy (fórmulas AIDA y PAS), ideas de "
            "creatividades con formato y medidas, presupuesto sugerido y "
            "distribución, calendario y plan de pruebas A/B. Si hace falta, "
            "investiga a la competencia en internet. Guarda la campaña con "
            "guardar_documento (categoría 'campanas'). Puedes abrir Meta Ads "
            "Manager o Google Ads con abrir_sitio, pero nunca publicas anuncios."
        ),
        "tools": documents.TOOLS + web.TOOLS_INVESTIGACION + [web.abrir_sitio],
    },
    {
        "key": "diseno",
        "name": "Agente de Diseño",
        "role": "crear diseños en Canva (posts, historias, anuncios, "
                "miniaturas, flyers, logos, presentaciones) y escribir el "
                "brief creativo.",
        "instructions": (
            "Para cada diseño: elige el formato correcto, crea el diseño en "
            "Canva y redacta un brief breve (textos exactos, jerarquía, "
            "paleta de colores, tipografías, imágenes sugeridas). Guarda el "
            "brief con guardar_documento (categoría 'disenos') y entrégalo "
            "en tu respuesta para que Yael lo aplique en Canva."
        ),
        "tools": canva.TOOLS + documents.TOOLS,
    },
    {
        "key": "trello",
        "name": "Agente de Pendientes",
        "role": "dar seguimiento a los pendientes de Trello: ver qué vence, "
                "crear, mover, completar y comentar tarjetas.",
        "instructions": (
            "Cuando reportes pendientes, prioriza lo vencido y lo que vence "
            "hoy o mañana, y sugiere un orden de trabajo. Para modificar una "
            "tarjeta, primero obtén su id con trello_pendientes."
        ),
        "tools": trello.TOOLS,
    },
    {
        "key": "comunidad",
        "name": "Agente de Comunidad",
        "role": "dar seguimiento a los grupos donde mencionan a Yael "
                "(@YaelCS): resumir menciones, proponer y enviar respuestas.",
        "instructions": (
            "Resume las menciones pendientes agrupadas por grupo y urgencia. "
            "Propón respuestas cordiales y profesionales en nombre de Yael. "
            "Solo envía una respuesta si Yael lo pide explícitamente."
        ),
        "tools": mentions.TOOLS,
    },
]


def build_specialists(safety):
    return {
        spec["key"]: Agent(
            key=spec["key"],
            name=spec["name"],
            role=spec["role"],
            instructions=spec["instructions"],
            tools=spec["tools"],
            safety=safety,
        )
        for spec in SPECIALISTS
    }
