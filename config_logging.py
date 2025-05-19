import logging
import os
import settings

def setup_logging():
    """Configura el sistema de logging para el juego."""
    if getattr(settings, 'MODO_DEBUG_LOGS', False):
        log_level_str = getattr(settings, 'LOG_LEVEL_VERBOSE', 'DEBUG')
    else:
        log_level_str = getattr(settings, 'LOG_LEVEL_STANDARD', 'INFO')
    
    numeric_log_level = getattr(logging, log_level_str.upper(), logging.INFO)

    # Eliminar handlers existentes para asegurar una configuración limpia.
    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)
    
    logging.basicConfig(level=numeric_log_level, 
                        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S')

    if settings.MODO_DEBUG_LOGS:
        try:
            # Asegurarse de que RUTA_BASE_PROYECTO está disponible y es correcta
            ruta_base = getattr(settings, 'RUTA_BASE_PROYECTO', None)
            if not ruta_base:
                # Intenta obtenerla desde el os si no está en settings, aunque debería estar.
                ruta_base = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) # Sube un nivel porque config_logging.py puede estar en un subdirectorio
                # Esta es una suposición, es mejor asegurar que settings.RUTA_BASE_PROYECTO esté bien definida antes.
                # Si settings.py define RUTA_BASE_PROYECTO basado en su propia ubicación, eso es más robusto.
                # Consideramos que settings.RUTA_BASE_PROYECTO ya está definida correctamente por main.py o settings.py mismo.


            log_file_path = os.path.join(settings.RUTA_BASE_PROYECTO, 'juego_debug.log')
            file_handler = logging.FileHandler(log_file_path, mode='w')
            file_handler.setLevel(logging.DEBUG)
            formatter = logging.Formatter('%(asctime)s - %(name)s - [%(levelname)s] - %(message)s')
            file_handler.setFormatter(formatter)
            logging.getLogger().addHandler(file_handler)
            logging.info(f"MODO_DEBUG_LOGS activo. Logs DEBUG detallados se escribirán en: {log_file_path}")
        except Exception as e:
            logging.error(f"No se pudo configurar el FileHandler para juego_debug.log: {e}", exc_info=True)

if __name__ == '__main__':
    # Para pruebas directas de este módulo, si fuera necesario.
    # Primero, asegurar que RUTA_BASE_PROYECTO se defina en settings para que la prueba funcione.
    # Esto es solo un ejemplo, la configuración real la hará main.
    print("Probando configuración de logging (esto requiere que settings.py sea accesible y RUTA_BASE_PROYECTO esté definida):")
    if not hasattr(settings, 'RUTA_BASE_PROYECTO') or not settings.RUTA_BASE_PROYECTO:
        settings.RUTA_BASE_PROYECTO = os.path.dirname(os.path.abspath(__file__)) # Simula que settings está en el mismo dir
        print(f"RUTA_BASE_PROYECTO simulada para prueba: {settings.RUTA_BASE_PROYECTO}")

    # Simular un modo debug para probar la creación del archivo.
    settings.MODO_DEBUG_LOGS = True 
    settings.LOG_LEVEL_VERBOSE = "DEBUG"
    
    setup_logging()
    logging.debug("Este es un mensaje de debug de prueba desde config_logging.py.")
    logging.info("Este es un mensaje de info de prueba desde config_logging.py.")
    if settings.MODO_DEBUG_LOGS:
        print(f"Prueba de logging completada. Verifica 'juego_debug.log' en {settings.RUTA_BASE_PROYECTO}") 