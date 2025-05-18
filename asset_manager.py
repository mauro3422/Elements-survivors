import pygame
import os
import settings  # Para RUTA_ASSETS y RUTA_BASE_PROYECTO
import logging

logger = logging.getLogger(__name__) # Un logger para este módulo

class AssetManager:
    def __init__(self):
        self.images = {}
        self.fonts = {}
        self.sounds = {} # Preparado para sonidos en el futuro
        self.ruta_assets_base = settings.RUTA_ASSETS
        logger.info("AssetManager inicializado.")

    def _construir_ruta_completa(self, subcarpeta_asset, nombre_archivo):
        """Construye la ruta completa al archivo del asset."""
        return os.path.join(self.ruta_assets_base, subcarpeta_asset, nombre_archivo)

    def load_image(self, subcarpeta_asset, nombre_archivo, nombre_clave_asset, usar_alpha=True, colorkey=None):
        """
        Carga una imagen, la almacena y la devuelve.

        Args:
            subcarpeta_asset (str): La subcarpeta dentro de RUTA_ASSETS (ej: "character/animaciones/Player/reposo").
            nombre_archivo (str): El nombre del archivo de imagen (ej: "1.png").
            nombre_clave_asset (str): La clave única para almacenar y recuperar esta imagen (ej: "player_reposo_1").
            usar_alpha (bool): True si la imagen tiene transparencia y se debe usar convert_alpha().
            colorkey (tuple, opcional): Color a establecer como transparente usando set_colorkey().
        
        Returns:
            pygame.Surface: La superficie de la imagen cargada, o None si falla.
        """
        if nombre_clave_asset in self.images:
            logger.debug(f"Imagen '{nombre_clave_asset}' ya estaba cargada. Devolviendo existente.")
            return self.images[nombre_clave_asset]

        ruta_completa = self._construir_ruta_completa(subcarpeta_asset, nombre_archivo)
        try:
            image = pygame.image.load(ruta_completa)
            if usar_alpha:
                image = image.convert_alpha()
            else:
                image = image.convert()
            
            if colorkey:
                image.set_colorkey(colorkey)
            
            self.images[nombre_clave_asset] = image
            logger.info(f"Imagen cargada y almacenada como '{nombre_clave_asset}': {ruta_completa}")
            return image
        except pygame.error as e:
            logger.error(f"Error al cargar imagen '{nombre_clave_asset}' desde {ruta_completa}: {e}")
            # Podríamos cargar una imagen placeholder aquí si es necesario
            placeholder = pygame.Surface((32,32))
            placeholder.fill(settings.ROJO_ERROR_ASSET if hasattr(settings, 'ROJO_ERROR_ASSET') else (255,0,0))
            self.images[nombre_clave_asset] = placeholder # Almacenar placeholder para evitar reintentos fallidos
            return placeholder
        except FileNotFoundError:
            logger.error(f"Archivo de imagen no encontrado '{nombre_clave_asset}': {ruta_completa}")
            placeholder = pygame.Surface((32,32))
            placeholder.fill(settings.ROJO_ERROR_ASSET if hasattr(settings, 'ROJO_ERROR_ASSET') else (255,0,0))
            self.images[nombre_clave_asset] = placeholder
            return placeholder


    def get_image(self, nombre_clave_asset):
        """Recupera una imagen previamente cargada."""
        image = self.images.get(nombre_clave_asset)
        if image is None:
            logger.warning(f"Se intentó obtener la imagen '{nombre_clave_asset}' pero no estaba cargada.")
            # Devolver un placeholder estándar si no se encuentra y se quiere evitar None
            placeholder = pygame.Surface((32,32))
            placeholder.fill(settings.ROJO_ERROR_ASSET if hasattr(settings, 'ROJO_ERROR_ASSET') else (255,0,0))
            return placeholder
        return image

    def load_font(self, nombre_fuente_o_ruta, tamano, nombre_clave_asset):
        """
        Carga una fuente (del sistema o desde archivo) y la almacena.

        Args:
            nombre_fuente_o_ruta (str): Nombre de la fuente del sistema o ruta al archivo .ttf/.otf.
            tamano (int): Tamaño de la fuente.
            nombre_clave_asset (str): La clave única para almacenar y recuperar esta fuente.

        Returns:
            pygame.font.Font: El objeto Font cargado, o None si falla.
        """
        if nombre_clave_asset in self.fonts:
            logger.debug(f"Fuente '{nombre_clave_asset}' ya estaba cargada. Devolviendo existente.")
            return self.fonts[nombre_clave_asset]
        
        try:
            # Intentar como fuente del sistema primero
            font = pygame.font.SysFont(nombre_fuente_o_ruta, tamano)
            self.fonts[nombre_clave_asset] = font
            logger.info(f"Fuente del sistema cargada y almacenada como '{nombre_clave_asset}': {nombre_fuente_o_ruta}, tamaño {tamano}")
            return font
        except pygame.error: # SysFont no la encontró o falló
            try:
                # Intentar como archivo de fuente si no es una fuente del sistema común
                # La ruta para pygame.font.Font debe ser completa o relativa al CWD
                # Para consistencia, podríamos querer que las fuentes también estén en la carpeta assets
                ruta_completa_fuente = nombre_fuente_o_ruta 
                if not os.path.isabs(nombre_fuente_o_ruta) and not nombre_fuente_o_ruta.startswith(self.ruta_assets_base):
                    # Si es un nombre de archivo simple, asumimos que está en una subcarpeta 'fonts' de assets
                    # Esto es una convención, podrías ajustarla
                    ruta_completa_fuente = os.path.join(self.ruta_assets_base, "fonts", nombre_fuente_o_ruta)

                font = pygame.font.Font(ruta_completa_fuente, tamano)
                self.fonts[nombre_clave_asset] = font
                logger.info(f"Fuente de archivo cargada y almacenada como '{nombre_clave_asset}': {ruta_completa_fuente}, tamaño {tamano}")
                return font
            except pygame.error as e:
                logger.error(f"Error al cargar fuente '{nombre_clave_asset}' ({nombre_fuente_o_ruta}, tamaño {tamano}): {e}")
                # Fallback a una fuente default de Pygame si todo falla
                try:
                    font = pygame.font.Font(None, tamano) # Fuente por defecto de Pygame
                    self.fonts[nombre_clave_asset] = font
                    logger.warning(f"Usando fuente por defecto de Pygame para '{nombre_clave_asset}'.")
                    return font
                except Exception as ex_default:
                    logger.critical(f"CRITICAL: No se pudo cargar ni la fuente especificada ni la fuente por defecto de Pygame para '{nombre_clave_asset}': {ex_default}")
                    return None # Absolutamente no se pudo cargar nada


    def get_font(self, nombre_clave_asset):
        """Recupera una fuente previamente cargada."""
        font = self.fonts.get(nombre_clave_asset)
        if font is None:
            logger.warning(f"Se intentó obtener la fuente '{nombre_clave_asset}' pero no estaba cargada.")
            # Podrías intentar cargar una fuente por defecto aquí si quieres evitar None
            # o simplemente devolver None y que el llamador maneje el error.
            # Por ahora, si no está, es un problema del preload.
            return pygame.font.Font(None, 24) # Fallback muy básico
        return font

    def preload_player_animations(self):
        """Carga todas las animaciones del jugador."""
        ruta_base_player = os.path.join("character", "animaciones", "Player")
        
        # Animación de Reposo
        ruta_reposo = os.path.join(ruta_base_player, "reposo")
        for i in range(1, 5): # Asumiendo 1.png a 4.png
            nombre_archivo = f"{i}.png"
            clave_asset = f"player_reposo_{i}"
            self.load_image(ruta_reposo, nombre_archivo, clave_asset, usar_alpha=True)
        logger.info("Preload de animaciones de reposo del jugador completado.")

        # Aquí podrías añadir la carga de otras animaciones (correr, atacar, etc.)
        # Ejemplo:
        # ruta_correr = os.path.join(ruta_base_player, "corriendo")
        # for i in range(1, 7): # Si hay 6 fotogramas para correr
        #     nombre_archivo = f"{i}.png"
        #     clave_asset = f"player_corriendo_{i}"
        #     self.load_image(ruta_correr, nombre_archivo, clave_asset, usar_alpha=True)
        # logger.info("Preload de animaciones de correr del jugador completado.")


    def preload_enemy_images(self):
        """Carga las imágenes de los enemigos."""
        # Ejemplo para un tipo de enemigo. Se podría expandir para múltiples tipos.
        ruta_enemigos = os.path.join("character", "animaciones", "Enemy")
        self.load_image(ruta_enemigos, "chicken.png", "enemy_chicken", usar_alpha=True)
        # Si hay más enemigos:
        # self.load_image(ruta_enemigos, "slime.png", "enemy_slime", usar_alpha=True)
        logger.info("Preload de imágenes de enemigos completado.")

    def preload_environment_images(self):
        """Carga las imágenes del entorno."""
        # Fondo
        self.load_image(os.path.join("scenary", "texture"), "T_Tierra32x32.png", "background_tierra", usar_alpha=False)
        
        # Animación del Árbol
        ruta_anim_arbol = os.path.join("scenary", "animaciones", "tree")
        for i in range(1, 7): # Cargar 6 fotogramas (1.png a 6.png)
            nombre_archivo = f"{i}.png"
            clave_asset = f"tree_frame_{i}"
            self.load_image(ruta_anim_arbol, nombre_archivo, clave_asset, usar_alpha=True)
        
        logger.info("Preload de imágenes de entorno completado.")

    def preload_fonts(self):
        """Carga las fuentes comunes."""
        self.load_font("Arial", 18, "hud_font_arial_18")
        self.load_font("Consolas", 16, "debug_font_consolas_16") # Ejemplo para debug
        logger.info("Preload de fuentes completado.")

    def preload_all(self):
        """Carga todos los assets definidos en los métodos preload_*."""
        logger.info("--- Iniciando Preload General de Assets ---")
        self.preload_player_animations()
        self.preload_enemy_images()
        self.preload_environment_images()
        self.preload_fonts()
        logger.info("--- Preload General de Assets Completado ---")

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


    # Configurar un logger básico para ver los mensajes si se ejecuta directamente
    if not logging.getLogger().hasHandlers():
        logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - [%(module)s] - %(message)s')

    manager = AssetManager()
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