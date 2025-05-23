import logging # Añadir import
print("DEBUG: main.py - Inicio del archivo")
import pygame
from src.config import settings # Importa todas las constantes de settings.py
from src.core.juego import Juego
from src.config import config_logging

# --- Configuración del Logging ---
# Importar el módulo de configuración de logging y ejecutar la configuración.
# Esto debe hacerse ANTES de que cualquier otro módulo intente obtener un logger,
# para asegurar que todos los handlers y filtros se apliquen correctamente desde el inicio.
print("DEBUG: main.py - Antes de config_logging.setup_logging()")
config_logging.setup_logging()
print("DEBUG: main.py - Después de config_logging.setup_logging()")
# --- Fin Configuración del Logging ---

# No se necesita importar 'os', 'sys', 'logging', 'config', 'config_logging' directamente aquí.
# La configuración de logging y sys.path debe ser manejada internamente por los módulos de src si es necesario.

# --- Bucle Principal del Juego ---
def main():
    """Función principal para iniciar y correr el juego."""
    print("DEBUG: main.py - Inicio de la función main()")
    logger = logging.getLogger('main') # Obtener logger para 'main'
    logger.info("Iniciando función main()", extra={"categoria_log": "log_main"})
    
    # La inicialización de Pygame y la creación de la instancia del juego
    # se manejan dentro de la clase Juego o sus componentes.
    
    logger.info(f"Ruta base del proyecto configurada en settings: {settings.RUTA_BASE_PROYECTO}", extra={"categoria_log": "log_main"})
    logger.info(f"Assets path: {settings.RUTA_ASSETS}", extra={"categoria_log": "log_main"})
    logger.info(f"Attack profiles path: {settings.RUTA_DATOS_PERFILES_ATAQUE}", extra={"categoria_log": "log_main"})
    
    try:
        print("DEBUG: main.py - Antes de crear instancia de Juego()")
        logger.info("Creando instancia de Juego...", extra={"categoria_log": "log_main"})
        juego_instancia = Juego()
        print("DEBUG: main.py - Después de crear instancia de Juego()")
        logger.info("Instancia de Juego creada. Ejecutando juego_instancia.run()...", extra={"categoria_log": "log_main"})
        juego_instancia.run()
    except Exception as e:
        logger.critical(f"Error fatal durante la ejecución del juego: {e}", exc_info=True, extra={"categoria_log": "log_main"})
        pygame.quit()
        # import sys # Mover import sys aquí si solo se usa para sys.exit
        # sys.exit(1) # sys no está importado globalmente ahora.
    
    logger.info("Función main() completada.", extra={"categoria_log": "log_main"})

if __name__ == '__main__':
    main() 