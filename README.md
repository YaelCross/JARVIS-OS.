# YAELCORE-OS

Asistente personal de escritorio para Windows.

## Iniciar manualmente

- `jarvis.bat` — abre YAELCORE-OS con ventana de consola (útil para ver errores).
- `iniciar_yaelcore.vbs` — abre YAELCORE-OS sin ventana de consola.

Ambos usan el entorno virtual `.venv` dentro de esta carpeta.

## Iniciar automáticamente al encender la computadora

1. Asegúrate de que `.venv` existe y tiene las dependencias instaladas
   (prueba primero con `jarvis.bat`).
2. Haz doble clic en **`instalar_inicio_automatico.bat`**.

Esto crea el acceso directo `YAELCORE-OS` en la carpeta **Inicio** de Windows
(`shell:startup`), así que el sistema arrancará cada vez que inicies sesión.

Para desactivarlo, haz doble clic en **`quitar_inicio_automatico.bat`**.

> Si mueves la carpeta del proyecto a otro lugar, vuelve a ejecutar
> `instalar_inicio_automatico.bat` para actualizar el acceso directo.
