import pygame
import settings # Importa todas las constantes de settings.py (ANCHO_PANTALLA, FPS, RUTA_ASSETS, etc.)
import os                   # Módulo del sistema operativo, usado aquí para os.path.join
import logging # <--- Añadir import para configurar logger principal
import sys # Para asegurar que la ruta base del proyecto se añada al path si es necesario
# Determinar la RUTA_BASE_PROYECTO y añadirla al sys.path si es necesario
# para que los módulos como 'settings' y 'config' se puedan importar correctamente.
RUTA_BASE_PROYECTO = os.path.dirname(os.path.abspath(__file__))
if RUTA_BASE_PROYECTO not in sys.path:
    sys.path.insert(0, RUTA_BASE_PROYECTO)

# Ahora se pueden importar settings y config
import config # Asegurarse que config.py está accesible
from config_logging import setup_logging # <--- NUEVA IMPORTACIÓN
from juego import Juego # <--- AÑADIR IMPORTACIÓN DE LA CLASE JUEGO

# --- Configurar Logging --- 
# Llamar a la función centralizada de configuración de logging.
setup_logging() # <--- LLAMADA A LA FUNCIÓN

# Obtener un logger para main.py DESPUÉS de que setup_logging haya configurado el sistema.
logger = logging.getLogger(__name__) # Logger para main.py

# --- Bucle Principal del Juego ---
def main():
    """Función principal para iniciar y correr el juego."""
    # La configuración de logging ya se hizo arriba, antes de definir main().

    # Verificación de RUTA_BASE_PROYECTO.
    # En este punto, settings.RUTA_BASE_PROYECTO ya debería estar establecida por el bloque
    # de código que se ejecuta al importar main.py, antes de setup_logging().
    # Aquí solo verificamos si, por alguna razón externa o error, ha cambiado o es incorrecta.
    if not hasattr(settings, 'RUTA_BASE_PROYECTO') or not settings.RUTA_BASE_PROYECTO:
        # Esto sería un escenario inesperado si el bloque anterior funcionó.
        logger.error("CRITICAL ERROR: settings.RUTA_BASE_PROYECTO no está configurada incluso después del intento inicial. Usando la ruta detectada localmente, pero esto puede indicar un problema.")
        settings.RUTA_BASE_PROYECTO = RUTA_BASE_PROYECTO # Forzar de nuevo como último recurso
    elif settings.RUTA_BASE_PROYECTO != RUTA_BASE_PROYECTO:
        logger.warning(f"settings.RUTA_BASE_PROYECTO ({settings.RUTA_BASE_PROYECTO}) difiere de la ruta detectada en main() ({RUTA_BASE_PROYECTO}). Esto es inusual. Se mantendrá el valor establecido inicialmente en settings.")
        # No la reasignamos aquí, confiamos en la primera asignación que ocurrió antes de setup_logging.

    logger.info("Iniciando la aplicación del juego desde main.py.")
    
    try:
        juego_instancia = Juego()
        juego_instancia.run()
    except Exception as e:
        logger.critical(f"Error fatal durante la ejecución del juego: {e}", exc_info=True)
        pygame.quit()
        sys.exit(1)

if __name__ == '__main__':
    main()