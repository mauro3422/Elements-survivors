import pygame
from src.config import settings # Importa todas las constantes de settings.py
from src.core.juego import Juego
from src.config import config_logging

# --- Configuración del Logging ---
# Importar el módulo de configuración de logging y ejecutar la configuración.
# Esto debe hacerse ANTES de que cualquier otro módulo intente obtener un logger,
# para asegurar que todos los handlers y filtros se apliquen correctamente desde el inicio.
config_logging.setup_logging() 
# --- Fin Configuración del Logging ---

# No se necesita importar 'os', 'sys', 'logging', 'config', 'config_logging' directamente aquí.
# La configuración de logging y sys.path debe ser manejada internamente por los módulos de src si es necesario.

# --- Bucle Principal del Juego ---
def main():
    """Función principal para iniciar y correr el juego."""
    
    # La inicialización de Pygame y la creación de la instancia del juego
    # se manejan dentro de la clase Juego o sus componentes.
    
    # El logger principal también se configura dentro de los módulos de src,
    # específicamente en config_logging.py y se importa donde sea necesario.
    # No es necesario obtener un logger aquí si main.py solo inicia el juego.

    print(f"Ruta base del proyecto configurada en settings: {settings.RUTA_BASE_PROYECTO}")
    print(f"Assets path: {settings.RUTA_ASSETS}")
    print(f"Attack profiles path: {settings.RUTA_DATOS_PERFILES_ATAQUE}")
    
    try:
        juego_instancia = Juego()
        juego_instancia.run()
    except Exception as e:
        # Idealmente, el logger ya estaría configurado por src.config.config_logging
        # y se podría usar aquí si se importara logging.
        # Por ahora, un print simple para errores críticos en main.
        print(f"Error fatal durante la ejecución del juego: {e}")
        # Considerar si el logger de src.utils podría usarse aquí si se propaga la configuración.
        # from src.utils.logger_config import logger # (Ejemplo, si existiera y estuviera configurado)
        # logger.critical(f"Error fatal durante la ejecución del juego: {e}", exc_info=True)
        pygame.quit()
        # import sys # Mover import sys aquí si solo se usa para sys.exit
        # sys.exit(1) # sys no está importado globalmente ahora.

if __name__ == '__main__':
    main()