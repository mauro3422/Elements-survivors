import pygame
import os
import settings  # Para RUTA_ASSETS, ROJO_ERROR_ASSET, y ahora configuraciones de FUENTES
import logging

# Logger específico para mensajes de depuración detallados sobre carga/gestión de assets.
logger_assets_debug = logging.getLogger("log_assets")
logger_assets_debug.setLevel(logging.DEBUG)

# Logger para mensajes generales (INFO, WARNING, ERROR, CRITICAL) del AssetManager.
logger_am_general = logging.getLogger("juego.asset_manager.general")
logger_am_general.setLevel(logging.INFO)

class AssetManager:
    def __init__(self, ruta_base_proyecto):
        self.images = {}
        self.fonts = {}
        self.sounds = {} # Preparado para sonidos en el futuro
        
        # Crear una superficie placeholder estándar
        self.placeholder_surface = pygame.Surface((32, 32))
        self.placeholder_surface.fill(getattr(settings, 'ROJO_ERROR_ASSET', (255, 0, 0)))
        
        nombre_subcarpeta_assets = getattr(settings, 'RUTA_ASSETS', 'assets')
        self.ruta_assets_completa = os.path.join(ruta_base_proyecto, nombre_subcarpeta_assets)
        
        # Este INFO es general e importante, no depende de la categoría "log_assets"
        logger_am_general.info(f"AssetManager: Ruta base de assets: {self.ruta_assets_completa}")
        if not os.path.isdir(self.ruta_assets_completa):
            logger_am_general.error(f"AssetManager: ¡RUTA DE ASSETS NO EXISTE!: {self.ruta_assets_completa}")

    def _construir_ruta_completa(self, subcarpeta_relativa_a_assets, nombre_archivo):
        """Construye la ruta completa al archivo del asset, relativa a la ruta_assets_completa."""       
        return os.path.join(self.ruta_assets_completa, subcarpeta_relativa_a_assets, nombre_archivo)

    def load_image(self, subcarpeta_asset, nombre_archivo, nombre_clave_asset, usar_alpha=True, colorkey=None):
        """
        Carga una imagen, la almacena y la devuelve.

        Args:
            subcarpeta_asset (str): La subcarpeta dentro de la carpeta principal de assets (ej: "character/animaciones/Player/reposo").
            nombre_archivo (str): El nombre del archivo de imagen (ej: "1.png").
            nombre_clave_asset (str): La clave única para almacenar y recuperar esta imagen (ej: "player_reposo_1").
            usar_alpha (bool): True si la imagen tiene transparencia y se debe usar convert_alpha().
            colorkey (tuple, opcional): Color a establecer como transparente usando set_colorkey().
        
        Returns:
            pygame.Surface: La superficie de la imagen cargada, o un placeholder si falla.
        """
        if nombre_clave_asset in self.images:
            if settings.MODO_DEBUG_LOGS and settings.LOG_CATEGORIAS.get("log_assets", False):
                logger_assets_debug.debug(f"AM: Imagen '{nombre_clave_asset}' ya cargada. Devolviendo existente.")
            return self.images[nombre_clave_asset]

        ruta_completa = self._construir_ruta_completa(subcarpeta_asset, nombre_archivo)
        try:
            image = pygame.image.load(ruta_completa)
            image = image.convert_alpha() if usar_alpha else image.convert()
            if colorkey: image.set_colorkey(colorkey)
            self.images[nombre_clave_asset] = image
            
            # Log INFO de carga exitosa. Se muestra si MODO_DEBUG_LOGS es True, independientemente de la categoría "log_assets".
            if settings.MODO_DEBUG_LOGS:
                logger_am_general.info(f"AM: Imagen '{nombre_clave_asset}' cargada desde: {ruta_completa}")
            return image
        except pygame.error as e:
            logger_am_general.error(f"AM: Error pygame al cargar '{nombre_clave_asset}' ({ruta_completa}): {e}")
            self.images[nombre_clave_asset] = self.placeholder_surface 
            return self.placeholder_surface
        except FileNotFoundError:
            logger_am_general.error(f"AM: Archivo NO ENCONTRADO para '{nombre_clave_asset}': {ruta_completa}")
            self.images[nombre_clave_asset] = self.placeholder_surface
            return self.placeholder_surface

    def get_image(self, nombre_clave_asset):
        """Recupera una imagen previamente cargada."""
        image = self.images.get(nombre_clave_asset)
        if image is None:
            logger_am_general.warning(f"AM: get_image '{nombre_clave_asset}' no encontrada. Devolviendo placeholder.")
            return self.placeholder_surface
        # El debug de "recuperada" solo si la categoría está activa.
        if settings.MODO_DEBUG_LOGS and settings.LOG_CATEGORIAS.get("log_assets", False):
            logger_assets_debug.debug(f"AM: get_image '{nombre_clave_asset}' recuperada.")
        return image

    def load_font(self, nombre_fuente_o_ruta_relativa, tamano, nombre_clave_asset):
        """
        Carga una fuente (del sistema o desde archivo relativo a la carpeta 'fonts' en assets) y la almacena.
        Si 'nombre_fuente_o_ruta_relativa' contiene '.ttf' o '.otf', se tratará como un nombre de archivo
        y se buscará en 'assets/fonts/'. De lo contrario, se tratará como un nombre de fuente del sistema.
        """
        if nombre_clave_asset in self.fonts:
            if settings.MODO_DEBUG_LOGS and settings.LOG_CATEGORIAS.get("log_assets", False):
                logger_assets_debug.debug(f"AM: Fuente '{nombre_clave_asset}' (T:{tamano}) ya cargada. Devolviendo existente.")
            return self.fonts[nombre_clave_asset]
        
        ruta_final_fuente, es_ruta_de_archivo = nombre_fuente_o_ruta_relativa, False
        if ".ttf" in nombre_fuente_o_ruta_relativa.lower() or ".otf" in nombre_fuente_o_ruta_relativa.lower():
            ruta_final_fuente = os.path.join(self.ruta_assets_completa, "fonts", nombre_fuente_o_ruta_relativa)
            es_ruta_de_archivo = True
        
        try:
            font = pygame.font.Font(ruta_final_fuente, tamano) if es_ruta_de_archivo else pygame.font.SysFont(ruta_final_fuente, tamano)
            self.fonts[nombre_clave_asset] = font
            tipo_log = "archivo" if es_ruta_de_archivo else "sistema"
            # INFO de carga exitosa de fuente, visible si MODO_DEBUG_LOGS es True.
            if settings.MODO_DEBUG_LOGS:
                logger_am_general.info(f"AM: Fuente ({tipo_log}) '{nombre_clave_asset}' cargada: {ruta_final_fuente}, T:{tamano}")
            return font
        except pygame.error as e:
            logger_am_general.error(f"AM: Error pygame al cargar fuente '{nombre_clave_asset}' ({ruta_final_fuente}, T:{tamano}): {e}")
        except FileNotFoundError as e:
             logger_am_general.error(f"AM: Archivo NO ENCONTRADO para fuente '{nombre_clave_asset}': {ruta_final_fuente} : {e}")
        # Fallback a fuente por defecto de Pygame (los logs de warning/critical ya usan logger_am_general)
        try:
            font = pygame.font.Font(None, tamano) 
            self.fonts[nombre_clave_asset] = font
            logger_am_general.warning(f"AM: Usando fuente Pygame default para '{nombre_clave_asset}' (T:{tamano}) tras error.")
            return font
        except Exception as ex_default:
            logger_am_general.critical(f"AM CRITICAL: Fallo al cargar fuente especificada Y Pygame default para '{nombre_clave_asset}': {ex_default}")
            return pygame.font.Font(None, tamano) 

    def get_font(self, nombre_clave_asset):
        """Recupera una fuente previamente cargada."""
        font = self.fonts.get(nombre_clave_asset)
        if font is None:
            logger_am_general.warning(f"AM: get_font '{nombre_clave_asset}' no cargada. Devolviendo Pygame default (24px).")
            return pygame.font.Font(None, 24) 
        if settings.MODO_DEBUG_LOGS and settings.LOG_CATEGORIAS.get("log_assets", False):
            logger_assets_debug.debug(f"AM: get_font '{nombre_clave_asset}' recuperada.")
        return font

    def preload_player_animations(self):
        """Carga todas las animaciones del jugador."""
        ruta_base_player = os.path.join("character", "animaciones", "Player")
        ruta_reposo = os.path.join(ruta_base_player, "reposo")
        for i in range(1, 5):
            self.load_image(ruta_reposo, f"{i}.png", f"player_reposo_{i}", usar_alpha=True) # load_image ya loguea individualmente
        if settings.MODO_DEBUG_LOGS: logger_am_general.info("AM: Preload animaciones reposo jugador completado.")

    def preload_enemy_images(self):
        """Carga las imágenes de los enemigos."""
        self.load_image(os.path.join("character", "animaciones", "Enemy"), "chicken.png", "enemy_chicken", usar_alpha=True)
        if settings.MODO_DEBUG_LOGS: logger_am_general.info("AM: Preload imágenes enemigos completado.")

    def preload_environment_images(self):
        """Carga las imágenes del entorno."""
        self.load_image(os.path.join("scenary", "texture"), "T_Tierra32x32.png", "background_tierra", usar_alpha=False)
        self.load_image(os.path.join("scenary", "texture"), "T_Tierra32x32.png", "fondo_nivel_1", usar_alpha=False)
        ruta_anim_arbol = os.path.join("scenary", "animaciones", "tree")
        for i in range(1, 7):
            self.load_image(ruta_anim_arbol, f"Tree_idle_{i}.png", f"tree_frame_{i}", usar_alpha=True)
        if settings.MODO_DEBUG_LOGS: logger_am_general.info("AM: Preload imágenes entorno completado.")

    def preload_fonts(self):
        """Carga las fuentes comunes definidas en settings.py."""
        nombre_fuente_hud = getattr(settings, 'NOMBRE_FUENTE_HUD', 'Arial') # Fallback a Arial
        tamano_fuente_hud = getattr(settings, 'TAMANO_FUENTE_HUD', 18)
        self.load_font(nombre_fuente_hud, tamano_fuente_hud, "hud_font") # Clave genérica "hud_font"

        nombre_fuente_debug = getattr(settings, 'NOMBRE_FUENTE_DEBUG', 'Consolas') # Fallback a Consolas
        tamano_fuente_debug = getattr(settings, 'TAMANO_FUENTE_DEBUG', 16)
        # La clase Juego busca la fuente de debug con la clave 'debug_font'
        self.load_font(nombre_fuente_debug, tamano_fuente_debug, "debug_font")
        
        if settings.MODO_DEBUG_LOGS: logger_am_general.info("AM: Preload fuentes (HUD, Debug) completado.")

    def preload_all(self):
        """Carga todos los assets definidos en los métodos preload_*."""
        # Estos logs son generales y resumen el proceso.
        logger_am_general.info("--- AM: Iniciando Preload General de Assets ---")
        self.preload_player_animations()
        self.preload_enemy_images()
        self.preload_environment_images()
        self.preload_fonts()
        logger_am_general.info("--- AM: Preload General de Assets Completado ---")

# Ejemplo de cómo se podría usar (esto iría en main.py o clase Juego)
if __name__ == '__main__':
    pygame.init() # Pygame debe estar inicializado para cargar fuentes e imágenes
    pygame.font.init() # Asegurar que el módulo font esté inicializado

    # Simular settings para prueba si es necesario
    if not hasattr(settings, 'RUTA_ASSETS'):
        # Esta es una ruta de ejemplo, ajústala a tu estructura real si pruebas esto directamente
        # Debería apuntar a la carpeta que CONTIENE 'character', 'scenary', etc.
        settings.RUTA_ASSETS = os.path.join(os.path.dirname(__file__), '..', 'assets') 
        print(f"settings.RUTA_ASSETS no definido, usando para prueba: {settings.RUTA_ASSETS}")

    if not hasattr(settings, 'ROJO_ERROR_ASSET'):
        settings.ROJO_ERROR_ASSET = (255, 100, 100)

    if not hasattr(settings, 'NOMBRE_FUENTE_HUD'): settings.NOMBRE_FUENTE_HUD = "Arial"
    if not hasattr(settings, 'TAMANO_FUENTE_HUD'): settings.TAMANO_FUENTE_HUD = 18
    if not hasattr(settings, 'NOMBRE_FUENTE_DEBUG'): settings.NOMBRE_FUENTE_DEBUG = "Consolas"
    if not hasattr(settings, 'TAMANO_FUENTE_DEBUG'): settings.TAMANO_FUENTE_DEBUG = 16

    # Configurar un logger básico para ver los mensajes si se ejecuta directamente
    if not logging.getLogger().hasHandlers():
        logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - [%(module)s] - %(message)s')

    # Simular RUTA_BASE_PROYECTO (directorio padre de 'assets')
    ruta_proyecto_simulada = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    manager = AssetManager(ruta_proyecto_simulada)
    manager.preload_all()

    # Ejemplo de obtención
    # img_jugador = manager.get_image("player_reposo_1")
    # font_hud = manager.get_font("hud_font_arial_18")

    # if img_jugador:
    #     print(f"Imagen jugador obtenida: {type(img_jugador)}")
    # if font_hud:
    #     print(f"Fuente HUD obtenida: {type(font_hud)}")

    # Aquí podrías tener una pequeña pantalla para mostrar los assets cargados
    # screen = pygame.display.set_mode((200,200))
    # if img_jugador:
    #    screen.blit(img_jugador, (50,50))
    # pygame.display.flip()
    # running = True
    # while running:
    #     for event in pygame.event.get():
    #         if event.type == pygame.QUIT:
    #             running = False
    # pygame.quit()
    print("Prueba de AssetManager completada (ver logs).") 