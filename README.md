# YAELCORE-OS

Asistente personal por voz (JARVIS) con una **red de agentes de IA** que gestiona y
ejecuta tareas en tu computadora con Windows: controla los programas abiertos, archivos,
PowerShell, navegador, teclado y ratón, Canva, Trello, campañas, guiones, prompts y las
menciones a **@YaelCS** en grupos.

## Arquitectura

```
                 Voz (micrófono)  /  Texto (consola)
                              │
                     JARVIS (app/core/jarvis.py)
                              │
         comandos rápidos (hora, fecha) ─┐
                              │          │
              YAELCORE · orquestador (app/agents/orchestrator.py)
         decide, divide la tarea y delega a los especialistas
                              │
 ┌──────────┬──────────┬──────┴────┬────────────┬───────────┐
 Apps       Sistema    Web         Escritorio   Contenido   Marketing
 ventanas   archivos   Google      teclado      guiones     campañas
 procesos   PowerShell YouTube     ratón        prompts     publicitarias
                       páginas     capturas
 ┌──────────┬──────────┐
 Diseño     Pendientes Comunidad
 Canva      Trello     menciones @YaelCS (Telegram)
                              │
           Puerta de seguridad (app/agents/safety.py)
   pide confirmación por voz antes de acciones peligrosas
                              │
      Vigilantes en segundo plano (app/watchers/watchers.py)
   avisan de menciones nuevas y pendientes de Trello por vencer
```

- **Cerebro intercambiable** (`app/brain/`): OpenAI o Claude (Anthropic). Se elige con
  `LLM_PROVIDER` en `.env`.
- **Cada agente** tiene un rol, instrucciones y sus herramientas. Razona en un bucle:
  pide un paso al modelo, ejecuta las herramientas y repite hasta terminar.
- **El orquestador** encadena especialistas: por ejemplo, Web investiga, Marketing
  arma la campaña y Diseño crea las piezas en Canva.

## Agentes y herramientas

| Agente | Qué hace | Herramientas |
|---|---|---|
| Aplicaciones | Abrir, cerrar, enfocar, minimizar y maximizar programas activos | `listar_ventanas`, `abrir_aplicacion`, `enfocar_ventana`, `minimizar_ventana`, `maximizar_ventana`, `cerrar_ventana`⚠️, `listar_procesos`, `cerrar_proceso`⚠️ |
| Sistema | Archivos, estado de la PC, PowerShell | `leer_archivo` (txt, docx, pdf…), `listar_carpeta`, `buscar_archivos`, `escribir_archivo`⚠️, `info_sistema`, `ejecutar_powershell`⚠️ |
| Web | Google, YouTube, sitios, leer páginas | `buscar_google`, `buscar_youtube`, `abrir_sitio`, `buscar_en_internet`, `leer_pagina` |
| Escritorio | Teclado, ratón, pantalla | `escribir_texto`⚠️, `atajo_teclado`⚠️, `hacer_clic`⚠️, `mover_raton`, `info_pantalla`, `captura_pantalla` |
| Contenido | Guiones y prompts de especialista | `guardar_documento`, `listar_documentos`, `abrir_documento` + investigación |
| Marketing | Campañas publicitarias completas | documentos + investigación + `abrir_sitio` |
| Diseño | Diseños en Canva + brief creativo | `canva_crear_diseno`, `canva_mis_disenos` + documentos |
| Pendientes | Seguimiento de Trello | `trello_tableros`, `trello_pendientes`, `trello_listas`, `trello_crear_tarjeta`⚠️, `trello_mover_tarjeta`⚠️, `trello_completar_tarjeta`⚠️, `trello_comentar`⚠️ |
| Comunidad | Menciones a @YaelCS en grupos | `menciones_listar`, `menciones_responder`⚠️, `menciones_marcar_atendida` |

⚠️ = acción peligrosa: JARVIS pide confirmación ("¿Procedo?") y espera un "sí".
Todas las acciones quedan registradas en `logs/acciones.log`. Algunos comandos de
PowerShell (formatear discos, borrar particiones, etc.) están bloqueados siempre.

## Instalación (Windows)

```bat
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
```

Edita `.env` y como mínimo pon la clave del cerebro que vas a usar:

- OpenAI: `LLM_PROVIDER=openai` y `OPENAI_API_KEY`.
- Claude: `LLM_PROVIDER=anthropic` y `ANTHROPIC_API_KEY`.

## Uso

```bat
jarvis.bat          :: voz + interfaz YAELCORE
jarvis_texto.bat    :: chat por teclado en la consola
```

O bien `python main.py` / `python main.py --texto`.

Ejemplos de órdenes:

- "Minimiza Chrome y enfoca Excel."
- "¿Qué programas tengo abiertos?"
- "Lee el archivo contrato.docx de mi escritorio y resúmelo."
- "Busca en YouTube tutoriales de Canva."
- "Investiga las tendencias de marketing de este mes y hazme un resumen."
- "Escribe un guion de reel de 30 segundos para lanzar mi curso."
- "Crea un prompt de especialista para generar imágenes de producto."
- "Haz una campaña de Meta Ads para mi tienda y crea el post en Canva."
- "¿Qué pendientes tengo en Trello para hoy?"
- "¿Quién me ha mencionado en los grupos?"
- "Escribe 'Reunión confirmada' en la ventana activa y presiona enter."
- "Toma una captura de pantalla."

Los guiones, prompts, campañas y briefs se guardan en `data/documentos/`.

## Integraciones

### Trello
1. Entra a https://trello.com/power-ups/admin, crea un Power-Up y copia la **API key**.
2. Genera un **Token** desde la misma página.
3. Ponlos en `TRELLO_API_KEY` y `TRELLO_TOKEN`. JARVIS revisará tus pendientes cada
   `TRELLO_CHECK_MINUTES` minutos y te avisará de lo vencido o lo que vence en 24 h.

### Canva
- **Sin configurar:** el Agente de Diseño abre las plantillas de Canva del formato correcto
  y te entrega el brief (textos, colores, tipografías).
- **Con `CANVA_ACCESS_TOKEN`** (Canva Connect API, https://www.canva.dev): crea el diseño
  con las medidas exactas y lo abre listo para editar.

### Menciones en grupos (@YaelCS)
Funciona con grupos de **Telegram**:
1. Habla con @BotFather → `/newbot` → copia el token en `TELEGRAM_BOT_TOKEN`.
2. En @BotFather: `/setprivacy` → elige el bot → **Disable** (para que lea los mensajes del grupo).
3. Agrega el bot a tus grupos.

Cuando alguien escriba `@YaelCS` en un grupo, JARVIS te lo dirá en voz alta, la mención
queda guardada en `data/menciones.json` y puedes pedir "resume mis menciones" o
"responde a la mención 3 diciendo que mañana lo reviso".

## Seguridad

`SAFETY_MODE` en `.env`:

- `confirmar_peligroso` (por defecto): pide permiso solo para acciones marcadas con ⚠️.
- `confirmar_todo`: pide permiso para cualquier acción sobre la PC o las apps.
- `autonomo`: no pide permiso (no recomendado).

Para detener el ratón o el teclado a mitad de una acción, mueve el ratón a una esquina de
la pantalla (failsafe de pyautogui).

## Agregar un agente nuevo

1. Crea sus herramientas en `app/tools/` con el decorador `@tool(...)`.
2. Agrega una entrada en `SPECIALISTS` de `app/agents/specialists.py`.

El orquestador lo detecta automáticamente y podrá delegarle tareas.

## Pruebas

```bat
python -m unittest discover tests
```

Las pruebas usan un cerebro simulado: no gastan créditos de API.
