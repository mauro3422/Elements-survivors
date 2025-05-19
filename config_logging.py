import logging
import logging.handlers
import os
import sys # Añadido para asegurar que settings se importa correctamente
import colorlog
import settings
from datetime import datetime # <--- Añadir import

# Asegurar que la ruta base del proyecto se añada al sys.path si es necesario.
# Esto es crucial si config_logging.py es importado antes que main.py en algún contexto de prueba
# o si la estructura del proyecto cambia.
RUTA_BASE_PROYECTO_PARA_CONFIG_LOG = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if RUTA_BASE_PROYECTO_PARA_CONFIG_LOG not in sys.path:
    sys.path.insert(0, RUTA_BASE_PROYECTO_PARA_CONFIG_LOG)

# No es necesario reimportar settings si ya se hizo arriba.
# import settings

# Directorio base para todos los logs (ej: 'logs/')
BASE_LOGS_DIR = os.path.join(settings.RUTA_BASE_PROYECTO, "logs")

# Variable global para el directorio de logs de la sesión actual
# Se establecerá en setup_logging()
SESSION_LOGS_DIR = BASE_LOGS_DIR # Valor por defecto antes de crear la carpeta de sesión

class CategoryFilter(logging.Filter):
    """
    Filtra los mensajes de log basado en si su 'categoria_log' (pasada en 'extra')
    está activa en settings.LOG_CATEGORIAS.
    """
    def __init__(self, default_category_key="log_general"):
        super().__init__()
        self.default_category_key = default_category_key

    def filter(self, record):
        # Si MODO_DEBUG_LOGS es False, y el nivel del record es DEBUG, no lo procesamos.
        # Esta lógica es mejor manejarla con los niveles de los handlers/loggers.
        # El filtro se enfoca en la activación por categoría.

        categoria_especifica = getattr(record, 'categoria_log', None)
        
        if categoria_especifica:
            # Si el mensaje tiene una categoría específica, verificar si está activa
            if categoria_especifica in settings.LOG_CATEGORIAS:
                return settings.LOG_CATEGORIAS[categoria_especifica]
            else:
                # Si la categoría no está en LOG_CATEGORIAS, por defecto no la mostramos
                # para evitar logs no deseados. Se podría añadir un warning aquí si se desea.
                # print(f"Advertencia: Categoría de log desconocida '{categoria_especifica}' para el mensaje: {record.getMessage()}", file=sys.stderr)
                return False # Política estricta: si la categoría no está definida, no se loguea.
        else:
            # Si no hay 'categoria_log' en 'extra', usamos la categoría por defecto del filtro (log_general).
            return settings.LOG_CATEGORIAS.get(self.default_category_key, True)

class DuplicateFilter(logging.Filter):
    """
    Filtra mensajes de log que son idénticos a su predecesor inmediato
    (mismo logger, nivel y mensaje) si ocurren dentro de un umbral de tiempo.
    """
    def __init__(self, name=""):
        super(DuplicateFilter, self).__init__(name)
        self.last_log_info = {} # Clave: (logger_name, levelno, message_hash), Valor: timestamp
        # print(f"DuplicateFilter INSTANCIADO (id: {id(self)})", file=sys.stderr) # DEBUG

    def filter(self, record):
        # Permitir que ciertos mensajes se salten el filtro de duplicados
        if getattr(record, 'skip_duplicate_check', False):
            # print(f"[DF id:{id(self)}] SKIP_DUPLICATE_CHECK para: {record.getMessage()[:50]}...", file=sys.stderr) # DEBUG
            return True

        current_message = record.getMessage()
        key = (record.name, record.levelno, current_message) 
        current_timestamp = record.created # Segundos desde epoch

        last_timestamp = self.last_log_info.get(key)

        # msg_preview = current_message[:70].replace('\\n', ' ') # Preview del mensaje DEBUG

        if last_timestamp:
            delta_ms = (current_timestamp - last_timestamp) * 1000
            # print(f"[DF id:{id(self)}] Record: {record.name} '{msg_preview}...' - Delta: {delta_ms:.2f}ms", file=sys.stderr) # DEBUG
            if delta_ms < settings.LOG_DUPLICATE_MESSAGE_TIMEDELTA_MS:
                # print(f"[DF id:{id(self)}] SUPRIMIENDO (delta {delta_ms:.2f}ms < {settings.LOG_DUPLICATE_MESSAGE_TIMEDELTA_MS}ms): {record.name} - '{msg_preview}...'", file=sys.stderr) # DEBUG
                return False # Suprimir mensaje duplicado rápido
            # else:
                # print(f"[DF id:{id(self)}] PERMITIENDO (delta OK): {record.name} - '{msg_preview}...'", file=sys.stderr) # DEBUG
                # pass 
        # else:
            # print(f"[DF id:{id(self)}] PERMITIENDO (nuevo mensaje): {record.name} - '{msg_preview}...'", file=sys.stderr) # DEBUG
            # pass

        self.last_log_info[key] = current_timestamp
        return True

def setup_logging():
    """Configura el sistema de logging para el juego con handlers y filtros."""
    
    global SESSION_LOGS_DIR # Necesitamos modificar la variable global

    # Crear directorio base de logs si no existe
    if not os.path.exists(BASE_LOGS_DIR):
        try:
            os.makedirs(BASE_LOGS_DIR)
        except OSError as e:
            print(f"Error al crear el directorio base de logs '{BASE_LOGS_DIR}': {e}", file=sys.stderr)
            # Si no se puede crear el directorio base, los logs de archivo no funcionarán.
            # Podríamos optar por no continuar con los file handlers.

    # Crear subdirectorio para la sesión actual basado en fecha y hora
    try:
        timestamp_actual = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        SESSION_LOGS_DIR = os.path.join(BASE_LOGS_DIR, timestamp_actual)
        if not os.path.exists(SESSION_LOGS_DIR):
            os.makedirs(SESSION_LOGS_DIR)
    except OSError as e:
        print(f"Error al crear el directorio de logs de sesión '{SESSION_LOGS_DIR}': {e}", file=sys.stderr)
        SESSION_LOGS_DIR = BASE_LOGS_DIR # Fallback al directorio base

    log_level_str = settings.LOG_LEVEL_VERBOSE if settings.MODO_DEBUG_LOGS else settings.LOG_LEVEL_STANDARD
    numeric_log_level = getattr(logging, log_level_str.upper(), logging.INFO)

    # Instanciar filtros UNA SOLA VEZ para ser compartidos
    shared_category_filter = CategoryFilter()
    shared_duplicate_filter = DuplicateFilter()

    # Configuración del Root Logger
    root_logger = logging.getLogger()
    root_logger.setLevel(numeric_log_level) 

    # Limpiar handlers existentes del root logger para evitar duplicados en recargas
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
        handler.close()

    # Formato para la consola con colorlog
    console_formatter = colorlog.ColoredFormatter(
        "%(log_color)s%(asctime)s - %(name)s - [%(levelname)s] - %(message)s%(reset)s",
        datefmt='%Y-%m-%d %H:%M:%S',
        reset=True,
        log_colors={
            'DEBUG': 'cyan',
            'INFO': 'green',
            'WARNING': 'yellow',
            'ERROR': 'red',
            'CRITICAL': 'red,bg_white',
        },
        secondary_log_colors={},
        style='%'
    )

    # Handler para la consola
    console_handler = logging.StreamHandler(sys.stdout) 
    console_handler.setFormatter(console_formatter)
    console_handler.setLevel(numeric_log_level) 
    
    console_handler.addFilter(shared_category_filter) # Usar instancia compartida
    console_handler.addFilter(shared_duplicate_filter) # Usar instancia compartida
    root_logger.addHandler(console_handler)

    # Formato estándar para archivos
    file_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - [%(levelname)s] - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # Crear FileHandlers para módulos específicos definidos en settings
    if settings.MODO_DEBUG_LOGS and hasattr(settings, 'MODULOS_CON_LOG_PROPIO'):
        for module_name in settings.MODULOS_CON_LOG_PROPIO:
            try:
                module_logger = logging.getLogger(module_name)
                # Asegurarse de que el logger del módulo también tenga el nivel adecuado
                # Si no, aunque el handler lo tenga, el logger podría bloquear los mensajes antes.
                module_logger.setLevel(numeric_log_level) 

                log_file_path = os.path.join(SESSION_LOGS_DIR, f"{module_name}.log")
                
                file_handler = logging.handlers.RotatingFileHandler(
                    log_file_path, mode='w', maxBytes=5*1024*1024, backupCount=3, encoding='utf-8'
                )
                file_handler.setFormatter(file_formatter)
                file_handler.setLevel(numeric_log_level) 
                
                file_handler.addFilter(shared_category_filter) # Usar instancia compartida
                file_handler.addFilter(shared_duplicate_filter) # Usar instancia compartida
                
                module_logger.addHandler(file_handler)
                # La propagación al root logger es deseable para que los mensajes también
                # lleguen al console_handler (que está en el root_logger).
                # No es necesario establecer propagate = False a menos que queramos evitarlo explícitamente.
                # module_logger.propagate = True # Es el valor por defecto

            except Exception as e:
                # Usar el root_logger para loguear este error es más seguro,
                # ya que podría haber un problema con el module_logger que se está configurando.
                logging.getLogger().error(f"No se pudo configurar el FileHandler para el módulo '{module_name}': {e}", exc_info=True, extra={"skip_duplicate_check": True})
    
    if settings.MODO_DEBUG_LOGS:
        logging.getLogger().info(f"Sistema de Logging configurado. MODO_DEBUG_LOGS activo. Nivel: {log_level_str}", extra={"skip_duplicate_check": True})
        logging.getLogger().info(f"Logs de módulos específicos se guardarán en: {SESSION_LOGS_DIR}", extra={"skip_duplicate_check": True})
    else:
        logging.getLogger().info(f"Sistema de Logging configurado. Nivel: {log_level_str}", extra={"skip_duplicate_check": True})


if __name__ == '__main__':
    # Para pruebas directas de este módulo:
    print("Probando configuración de logging avanzada...")

    # Simular algunas configuraciones de settings.py para la prueba
    if not hasattr(settings, 'RUTA_BASE_PROYECTO'):
        settings.RUTA_BASE_PROYECTO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        print(f"RUTA_BASE_PROYECTO simulada para prueba: {settings.RUTA_BASE_PROYECTO}")

    settings.MODO_DEBUG_LOGS = True
    settings.LOG_LEVEL_VERBOSE = "DEBUG"
    settings.LOG_LEVEL_STANDARD = "INFO"
    
    # Definir algunas LOG_CATEGORIAS para la prueba
    settings.LOG_CATEGORIAS = {
        "log_general": True,
        "log_prueba_especifica": True,
        "log_prueba_desactivada": False,
        "log_animacion": True # Para probar con un logger de módulo
    }
    # Definir MODULOS_CON_LOG_PROPIO para la prueba
    settings.MODULOS_CON_LOG_PROPIO = ["main_test", "juego_test", "animaciones_test"]

    # Asegurar que LOG_DUPLICATE_MESSAGE_TIMEDELTA_MS esté disponible para la prueba
    if not hasattr(settings, 'LOG_DUPLICATE_MESSAGE_TIMEDELTA_MS'):
        settings.LOG_DUPLICATE_MESSAGE_TIMEDELTA_MS = 50 # ms, valor por defecto para prueba

    setup_logging()

    # Logs de prueba
    logger_main = logging.getLogger("main_test") # Coincide con MODULOS_CON_LOG_PROPIO
    logger_juego = logging.getLogger("juego_test") # Coincide con MODULOS_CON_LOG_PROPIO
    logger_anim = logging.getLogger("animaciones_test") # Coincide con MODULOS_CON_LOG_PROPIO
    logger_otro = logging.getLogger("otro_modulo_sin_archivo") # No en MODULOS_CON_LOG_PROPIO

    logger_main.debug("Mensaje DEBUG desde main_test (general).")
    logger_main.info("Mensaje INFO desde main_test (general).")
    
    logger_juego.info("Mensaje INFO desde juego_test (general).")
    logger_juego.warning("Mensaje WARNING desde juego_test (general).")
    logger_juego.error("Mensaje ERROR desde juego_test (general).")
    logger_juego.critical("Mensaje CRITICAL desde juego_test (general).")

    logger_juego.debug("Mensaje DEBUG para categoría específica (activa).", extra={"categoria_log": "log_prueba_especifica"})
    logger_juego.debug("Mensaje DEBUG para categoría específica (DESACTIVADA).", extra={"categoria_log": "log_prueba_desactivada"})
    
    logger_anim.info("Inicio de animación compleja.", extra={"categoria_log": "log_animacion"})
    logger_anim.debug("Detalle frame X de animación Y.", extra={"categoria_log": "log_animacion"})

    logger_otro.info("Mensaje desde un logger sin archivo propio (debería ir a consola).")
    logger_otro.debug("Mensaje DEBUG desde otro logger (debería ir a consola si log_general está ON).")
    
    # Simular desactivar una categoría en tiempo de ejecución
    print("\\n--- CAMBIANDO LOG_CATEGORIAS[\'log_prueba_especifica\'] a False ---")
    settings.LOG_CATEGORIAS["log_prueba_especifica"] = False
    logger_juego.debug("NUEVO Mensaje DEBUG para categoría específica (ahora DESACTIVADA).", extra={"categoria_log": "log_prueba_especifica"})
    logger_juego.info("NUEVO Mensaje INFO para categoría específica (ahora DESACTIVADA, pero INFO siempre pasa si la cat. está desactivada y el nivel es INFO).", extra={"categoria_log": "log_prueba_especifica"})

    # Prueba del filtro de duplicados
    logger_main.info("Primer mensaje (debería aparecer).")
    logger_main.info("Segundo mensaje idéntico (debería ser suprimido si es rápido).")
    logger_main.info("Segundo mensaje idéntico (debería ser suprimido si es rápido).")
    
    import time
    time.sleep(settings.LOG_DUPLICATE_MESSAGE_TIMEDELTA_MS / 1000 + 0.01) # Esperar más que el umbral
    
    logger_main.info("Tercer mensaje idéntico pero después de pausa (debería aparecer).")
    logger_main.info("Cuarto mensaje, diferente.")

    logger_juego.debug("Mensaje DEBUG repetido.", extra={"categoria_log": "log_prueba_especifica"})
    logger_juego.debug("Mensaje DEBUG repetido.", extra={"categoria_log": "log_prueba_especifica"})
    
    print(f"\\nPrueba de logging completada. Verifica la consola y la carpeta '{SESSION_LOGS_DIR}'") # Usar SESSION_LOGS_DIR
    print(f"Archivos esperados: main_test.log, juego_test.log, animaciones_test.log dentro de la subcarpeta de sesión.") 