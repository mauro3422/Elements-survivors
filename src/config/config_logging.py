import logging
import logging.handlers
import os
import sys 
import colorlog
# import settings # Esta importación se manejará con la nueva estructura (from src.config import settings)
from datetime import datetime

# Cuando este archivo esté en src/config/config_logging.py, 
# RUTA_BASE_PROYECTO_PARA_CONFIG_LOG debe apuntar a la raíz del proyecto.
# os.path.abspath(__file__) -> .../src/config/config_logging.py
# os.path.dirname(...) -> .../src/config/
# os.path.dirname(...) -> .../src/
# os.path.dirname(...) -> .../ (raíz del proyecto)
RUTA_BASE_PROYECTO_PARA_CONFIG_LOG = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if RUTA_BASE_PROYECTO_PARA_CONFIG_LOG not in sys.path:
    sys.path.insert(0, RUTA_BASE_PROYECTO_PARA_CONFIG_LOG)

# Ahora podemos importar settings correctamente desde su nueva ubicación
from src.config import settings

# Directorio base para todos los logs (ej: 'logs/')
BASE_LOGS_DIR = os.path.join(settings.RUTA_BASE_PROYECTO, "logs")

# Variable global para el directorio de logs de la sesión actual
SESSION_LOGS_DIR = BASE_LOGS_DIR 

class CategoryFilter(logging.Filter):
    def __init__(self, default_category_key="log_general"):
        super().__init__()
        self.default_category_key = default_category_key

    def filter(self, record):
        categoria_especifica = getattr(record, 'categoria_log', None)
        if categoria_especifica:
            if categoria_especifica in settings.LOG_CATEGORIAS:
                return settings.LOG_CATEGORIAS[categoria_especifica]
            else:
                # Podríamos añadir un log de advertencia aquí si MODO_DEBUG_LOGS es True
                # y la categoría no existe, para ayudar a depurar errores tipográficos en categorías.
                # Ejemplo:
                # if settings.MODO_DEBUG_LOGS:
                #     logging.getLogger(__name__).warning(f"Categoría de log desconocida: '{categoria_especifica}' usada en logger '{record.name}'.", extra={'skip_duplicate_check': True, 'categoria_log': 'log_config_logging'})
                return False 
        else:
            return settings.LOG_CATEGORIAS.get(self.default_category_key, True)

class DuplicateFilter(logging.Filter):
    def __init__(self, name=""):
        super(DuplicateFilter, self).__init__(name)
        self.last_log_info = {}

    def filter(self, record):
        if getattr(record, 'skip_duplicate_check', False):
            return True
        current_message = record.getMessage()
        key = (record.name, record.levelno, current_message) 
        current_timestamp = record.created 
        last_timestamp = self.last_log_info.get(key)
        if last_timestamp:
            delta_ms = (current_timestamp - last_timestamp) * 1000
            if delta_ms < settings.LOG_DUPLICATE_MESSAGE_TIMEDELTA_MS:
                return False 
        self.last_log_info[key] = current_timestamp
        return True

def setup_logging():
    # Usar logger para los mensajes de depuración de esta función
    logger_config = logging.getLogger("config_logging") 

    logger_config.debug("DEBUG: config_logging.py - INICIO setup_logging()", extra={"categoria_log": "log_config_logging"})
    global SESSION_LOGS_DIR
    if not os.path.exists(BASE_LOGS_DIR):
        try:
            os.makedirs(BASE_LOGS_DIR)
        except OSError as e:
            # Usar print a stderr para errores muy tempranos antes de que el logger esté completamente configurado
            print(f"Error al crear el directorio base de logs '{BASE_LOGS_DIR}': {e}", file=sys.stderr)
            # logger_config.error(f"Error al crear el directorio base de logs '{BASE_LOGS_DIR}': {e}", exc_info=True, extra={"categoria_log": "log_config_logging", "skip_duplicate_check": True})

    logger_config.debug("DEBUG: config_logging.py - Antes de crear SESSION_LOGS_DIR", extra={"categoria_log": "log_config_logging"})
    try:
        timestamp_actual = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        SESSION_LOGS_DIR = os.path.join(BASE_LOGS_DIR, timestamp_actual)
        if not os.path.exists(SESSION_LOGS_DIR):
            os.makedirs(SESSION_LOGS_DIR)
    except OSError as e:
        print(f"Error al crear el directorio de logs de sesión '{SESSION_LOGS_DIR}': {e}", file=sys.stderr)
        # logger_config.error(f"Error al crear el directorio de logs de sesión '{SESSION_LOGS_DIR}': {e}", exc_info=True, extra={"categoria_log": "log_config_logging", "skip_duplicate_check": True})
        SESSION_LOGS_DIR = BASE_LOGS_DIR 
    logger_config.debug(f"DEBUG: config_logging.py - Después de crear SESSION_LOGS_DIR: {SESSION_LOGS_DIR}", extra={"categoria_log": "log_config_logging"})

    log_level_str = settings.LOG_LEVEL_VERBOSE if settings.MODO_DEBUG_LOGS else settings.LOG_LEVEL_STANDARD
    numeric_log_level = getattr(logging, log_level_str.upper(), logging.INFO)
    logger_config.debug(f"DEBUG: config_logging.py - Nivel de log numérico: {numeric_log_level}", extra={"categoria_log": "log_config_logging"})

    shared_category_filter = CategoryFilter()
    shared_duplicate_filter = DuplicateFilter()

    root_logger = logging.getLogger()
    root_logger.setLevel(numeric_log_level)
    logger_config.debug("DEBUG: config_logging.py - Root logger nivel seteado", extra={"categoria_log": "log_config_logging"})

    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
        handler.close()
    logger_config.debug("DEBUG: config_logging.py - Handlers antiguos removidos", extra={"categoria_log": "log_config_logging"})

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
    
    console_handler = logging.StreamHandler(sys.stdout) 
    console_handler.setFormatter(console_formatter)
    console_handler.setLevel(numeric_log_level) 
    console_handler.addFilter(shared_category_filter) 
    console_handler.addFilter(shared_duplicate_filter) 
    root_logger.addHandler(console_handler)
    logger_config.debug("DEBUG: config_logging.py - Console handler añadido", extra={"categoria_log": "log_config_logging"})

    file_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - [%(levelname)s] - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    if settings.MODO_DEBUG_LOGS and hasattr(settings, 'MODULOS_CON_LOG_PROPIO'):
        logger_config.debug("DEBUG: config_logging.py - Configurando file handlers para módulos específicos", extra={"categoria_log": "log_config_logging"})
        for module_name in settings.MODULOS_CON_LOG_PROPIO:
            try:
                module_logger = logging.getLogger(module_name)
                module_logger.setLevel(numeric_log_level)

                # MODIFICACIÓN INICIO: Crear subcarpeta para cada módulo
                module_log_dir = os.path.join(SESSION_LOGS_DIR, module_name)
                if not os.path.exists(module_log_dir):
                    os.makedirs(module_log_dir)
                log_file_path = os.path.join(module_log_dir, f"{module_name}.log")
                # MODIFICACIÓN FIN
                logger_config.debug(f"DEBUG: config_logging.py - Preparando file handler para {module_name} en {log_file_path}", extra={"categoria_log": "log_config_logging"})

                file_handler = logging.handlers.RotatingFileHandler(
                    log_file_path, mode='a', maxBytes=28*1024, backupCount=10, encoding='utf-8'
                )
                file_handler.setFormatter(file_formatter)
                file_handler.setLevel(numeric_log_level) 
                file_handler.addFilter(shared_category_filter) 
                file_handler.addFilter(shared_duplicate_filter) 
                
                for h in module_logger.handlers[:]:
                    if isinstance(h, logging.FileHandler) and h.baseFilename == log_file_path:
                        module_logger.removeHandler(h)
                        h.close()
                module_logger.addHandler(file_handler)
                # module_logger.propagate = False # Decidimos dejarlo True por ahora

            except Exception as e:
                # Usamos el root_logger aquí o un logger 'config_logging' si está disponible.
                # Para errores durante la configuración del logging, el root logger es una apuesta segura si otros fallan.
                logging.getLogger().error(f"No se pudo configurar el FileHandler para el módulo '{module_name}': {e}", exc_info=True, extra={'skip_duplicate_check': True, 'categoria_log': 'log_config_logging'})
        logger_config.debug("DEBUG: config_logging.py - File handlers para módulos específicos configurados", extra={"categoria_log": "log_config_logging"})
    
    # Usar el root logger para estos mensajes finales, ya que logger_config es local a setup_logging
    # y queremos que estos mensajes importantes siempre aparezcan si el logging base funciona.
    if settings.MODO_DEBUG_LOGS:
        logging.getLogger().info(f"Sistema de Logging configurado. MODO_DEBUG_LOGS activo. Nivel: {log_level_str}", extra={"skip_duplicate_check": True, "categoria_log": "log_config_logging"})
        logging.getLogger().info(f"Logs de módulos específicos se guardarán en: {SESSION_LOGS_DIR}", extra={"skip_duplicate_check": True, "categoria_log": "log_config_logging"})
    else:
        logging.getLogger().info(f"Sistema de Logging configurado. Nivel: {log_level_str}", extra={"skip_duplicate_check": True, "categoria_log": "log_config_logging"})
    logger_config.debug("DEBUG: config_logging.py - FIN setup_logging()", extra={"categoria_log": "log_config_logging"}) 