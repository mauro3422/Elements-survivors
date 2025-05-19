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

# --- Configuración del Logger Principal (opcional, pero bueno para AssetManager) ---
# Esto asegura que los logs del AssetManager y otros módulos sean visibles
# si no se ha configurado un logger raíz antes.
if not logging.getLogger().hasHandlers():
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - [%(name)s] - %(message)s')
logger = logging.getLogger(__name__) # Logger para main.py
# --- Fin Configuración Logger ---

# Configurar RUTA_BASE_PROYECTO en settings si aún no está definida.
# Esto es útil si settings.py no puede determinar su propia ubicación de forma fiable.
if not hasattr(settings, 'RUTA_BASE_PROYECTO') or settings.RUTA_BASE_PROYECTO is None:
    settings.RUTA_BASE_PROYECTO = RUTA_BASE_PROYECTO
    logger.info(f"settings.RUTA_BASE_PROYECTO establecida en main.py a: {settings.RUTA_BASE_PROYECTO}")

# Importar la clase Juego DESPUÉS de configurar RUTA_BASE_PROYECTO si es necesario
from juego import Juego

# --- Bucle Principal del Juego ---
def main():
    """Función principal para iniciar y correr el juego."""
    # Determinar el nivel de log basado en MODO_DEBUG_LOGS de settings.py
    if getattr(settings, 'MODO_DEBUG_LOGS', False):
        log_level_str = getattr(settings, 'LOG_LEVEL_VERBOSE', 'DEBUG')
    else:
        log_level_str = getattr(settings, 'LOG_LEVEL_STANDARD', 'INFO')
    
    # Convertir el string del nivel de log a un valor numérico de logging
    numeric_log_level = getattr(logging, log_level_str.upper(), logging.INFO)

    # Reconfigurar el logger básico con el nivel deseado.
    # Eliminar handlers existentes para asegurar una configuración limpia.
    for handler in logging.root.handlers[:]: # Iterar sobre una copia
        logging.root.removeHandler(handler) # Eliminar handlers existentes
    logging.basicConfig(level=numeric_log_level, 
                        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S')

    # Configurar FileHandler para juego_debug.log si MODO_DEBUG_LOGS está activo
    if settings.MODO_DEBUG_LOGS:
        try:
            log_file_path = os.path.join(settings.RUTA_BASE_PROYECTO, 'juego_debug.log')
            file_handler = logging.FileHandler(log_file_path, mode='w') # Sobrescribir en cada ejecución
            file_handler.setLevel(logging.DEBUG) # Captura todos los mensajes DEBUG y superiores
            formatter = logging.Formatter('%(asctime)s - %(name)s - [%(levelname)s] - %(message)s') # Mismo formato o uno más detallado
            file_handler.setFormatter(formatter)
            logging.getLogger().addHandler(file_handler) # Añadir al logger raíz
            logging.info(f"MODO_DEBUG_LOGS activo. Logs DEBUG detallados se escribirán en: {log_file_path}")
        except Exception as e:
            logging.error(f"No se pudo configurar el FileHandler para juego_debug.log: {e}")

    # Establecer RUTA_BASE_PROYECTO en el módulo settings (redundante si ya se hizo arriba, pero asegura)
    if not hasattr(settings, 'RUTA_BASE_PROYECTO') or not settings.RUTA_BASE_PROYECTO:
        settings.RUTA_BASE_PROYECTO = RUTA_BASE_PROYECTO
        logging.info(f"settings.RUTA_BASE_PROYECTO establecida en: {settings.RUTA_BASE_PROYECTO}")
    elif settings.RUTA_BASE_PROYECTO != RUTA_BASE_PROYECTO:
        logging.warning(f"settings.RUTA_BASE_PROYECTO ({settings.RUTA_BASE_PROYECTO}) difiere de la ruta detectada ({RUTA_BASE_PROYECTO}). Usando la detectada.")
        settings.RUTA_BASE_PROYECTO = RUTA_BASE_PROYECTO

    logging.info("Iniciando la aplicación del juego.")
    
    try:
        juego_instancia = Juego()
        juego_instancia.run()
    except Exception as e:
        logging.critical(f"Error fatal durante la ejecución del juego: {e}", exc_info=True)
        pygame.quit()
        sys.exit(1)

if __name__ == '__main__':
    main()