import pygame
import pytmx # Para cargar mapas Tiled
import os
import random
from entidad_base import EntidadBase # O la clase base para tus obstáculos
from enemigo import Enemigo # O la clase base para tus enemigos
import settings # Para acceder a configuraciones globales como RUTA_ASSETS
from entorno import Arbol # Necesitamos Arbol para los obstáculos
import config # Necesitaremos config para las posiciones iniciales si las mantenemos temporalmente

# Podríamos necesitar un logger específico para este módulo también
import logging
logger_gn = logging.getLogger(__name__)

class GestorNivel:
    def __init__(self, asset_manager):
        """
        Inicializa el GestorNivel.

        Args:
            asset_manager: Instancia de AssetManager para cargar assets.
        """
        self.asset_manager = asset_manager
        self.mapa_tmx = None
        self.obstaculos = pygame.sprite.Group()
        self.enemigos = pygame.sprite.Group()
        self.elementos_decorativos = pygame.sprite.Group() # Si tienes elementos solo visuales
        self.zonas_especiales = {} # Para zonas de colisión, triggers, etc.

        logger_gn.info("GestorNivel inicializado.")

    def cargar_elementos_nivel_inicial(self):
        """
        Carga los elementos iniciales del nivel (obstáculos y enemigos).
        Esto reemplaza la lógica hardcodeada que estaba en juego.py.
        En el futuro, esto podría cargar desde un archivo TMX o generar aleatoriamente.
        """
        self._cargar_obstaculos_hardcodeados()
        self._generar_enemigos_hardcodeados()
        logger_gn.info("Elementos del nivel inicial cargados (obstáculos y enemigos).")

    def _cargar_obstaculos_hardcodeados(self):
        """
        Carga obstáculos (árboles) basados en una configuración hardcodeada.
        Esta es la lógica extraída de juego.py/_crear_entidades.
        """
        if settings.MODO_DEBUG_LOGS and settings.LOG_CATEGORIAS.get("log_general", False): # Asumimos log_general para esto
            logger_gn.debug("GestorNivel: Cargando obstáculos hardcodeados (árboles).")

        # Lógica original de juego.py para crear árboles
        arbol_config_list = [
            {"x": 300, "y": 150}, {"x": 500, "y": 300}, {"x": 100, "y": 400}
        ]
        for i, config_arbol_item in enumerate(arbol_config_list):
            # Asumimos que la clase Arbol se importa correctamente
            arbol = Arbol(config_arbol_item["x"], config_arbol_item["y"], self.asset_manager)
            self.obstaculos.add(arbol)
            # No necesitamos añadirlo a todos_los_sprites aquí, eso lo hará la clase Juego
            if settings.MODO_DEBUG_LOGS and settings.LOG_CATEGORIAS.get("log_gn_detalle", False): # Nueva categoría de log opcional
                 logger_gn.debug(f"  GestorNivel: Árbol creado en ({config_arbol_item['x']}, {config_arbol_item['y']}) y añadido a obstáculos.")
        
        if settings.MODO_DEBUG_LOGS:
             logger_gn.info(f"GestorNivel: {len(self.obstaculos)} obstáculos (árboles) cargados.")

    def _generar_enemigos_hardcodeados(self, jugador_pos=None): # jugador_pos por si lo necesitamos en el futuro
        """
        Genera enemigos basados en una configuración hardcodeada.
        Esta es la lógica extraída de juego.py/_crear_entidades.
        """
        if settings.MODO_DEBUG_LOGS and settings.LOG_CATEGORIAS.get("log_general", False):
            logger_gn.debug("GestorNivel: Generando enemigos hardcodeados.")

        # Lógica original de juego.py para crear enemigos
        enemigo_config_list = [
            {"x": 600, "y": 200}, {"x": 400, "y": 500}
        ]
        for config_enemigo_item in enemigo_config_list:
            # Asumimos que la clase Enemigo se importa correctamente
            enemigo = Enemigo(config_enemigo_item["x"], config_enemigo_item["y"], self.asset_manager)
            self.enemigos.add(enemigo)
            # No necesitamos añadirlo a todos_los_sprites aquí, eso lo hará la clase Juego
            if settings.MODO_DEBUG_LOGS and settings.LOG_CATEGORIAS.get("log_gn_detalle", False):
                 logger_gn.debug(f"  GestorNivel: Enemigo creado en ({config_enemigo_item['x']}, {config_enemigo_item['y']}) y añadido a enemigos.")

        if settings.MODO_DEBUG_LOGS:
             logger_gn.info(f"GestorNivel: {len(self.enemigos)} enemigos generados.")

    def cargar_mapa_desde_tmx(self, nombre_mapa_tmx):
        """
        Carga un mapa desde un archivo TMX (Tiled) y procesa sus capas.
        Popula los grupos de sprites de obstáculos, elementos decorativos, etc.
        (Implementación futura)
        """
        ruta_completa_mapa = os.path.join(settings.RUTA_ASSETS_MAPAS, nombre_mapa_tmx) # Asegúrate que RUTA_ASSETS_MAPAS exista en settings
        if not os.path.exists(ruta_completa_mapa):
            logger_gn.error(f"GestorNivel: No se encontró el archivo de mapa TMX: {ruta_completa_mapa}")
            return

        try:
            self.mapa_tmx = pytmx.load_pygame(ruta_completa_mapa, pixelalpha=True)
            logger_gn.info(f"GestorNivel: Mapa TMX '{nombre_mapa_tmx}' cargado exitosamente.")
            # Aquí procesaríamos las capas para popular self.obstaculos, self.elementos_decorativos, self.zonas_especiales
            # Ejemplo:
            # for layer in self.mapa_tmx.visible_layers:
            #     if isinstance(layer, pytmx.TiledTileLayer):
            #         if layer.name == 'CapaDeObstaculos':
            #             # Procesar tiles de esta capa para crear obstáculos
            #             pass
            #     elif isinstance(layer, pytmx.TiledObjectGroup):
            #         if layer.name == 'PuntosDeSpawnEnemigos':
            #             # Procesar objetos para generar enemigos
            #             pass
            #         elif layer.name == 'ZonasEspeciales':
            #             # Procesar objetos para definir zonas
            #             pass
            
        except Exception as e:
            logger_gn.error(f"GestorNivel: Error al cargar o procesar el mapa TMX '{nombre_mapa_tmx}': {e}", exc_info=True)
            self.mapa_tmx = None # Asegurar que no quede un estado inconsistente

        # Por ahora, mantenemos la carga hardcodeada como fallback o inicial
        # self._cargar_obstaculos_hardcodeados()
        # self._generar_enemigos_hardcodeados()

    def get_obstaculos(self):
        return self.obstaculos

    def get_enemigos(self):
        return self.enemigos

    def get_elementos_decorativos(self):
        return self.elementos_decorativos

    def get_zonas_especiales(self):
        return self.zonas_especiales

    def get_tile_data(self, capa_nombre, x, y):
        """
        Obtiene datos de un tile específico en una capa del mapa TMX.
        Útil para obtener propiedades personalizadas de los tiles.
        """
        if not self.mapa_tmx:
            logger_gn.warning("Intento de obtener tile_data sin mapa TMX cargado.")
            return None
        try:
            capa = self.mapa_tmx.get_layer_by_name(capa_nombre)
            gid = capa.data[y][x] # Obtener el GID (Global ID) del tile
            if gid != 0:
                # Obtener propiedades del tile. Las propiedades se definen en Tiled.
                propiedades = self.mapa_tmx.get_tile_properties_by_gid(gid)
                if propiedades:
                    return propiedades
            return None
        except Exception as e:
            logger_gn.error(f"Error al obtener tile_data para la capa {capa_nombre} en ({x},{y}): {e}")
            return None

if __name__ == '__main__':
    # Configuración mínima para prueba (requiere que settings.py y config.py sean accesibles)
    # Esto es solo para una prueba muy básica y local.
    if not logging.getLogger().hasHandlers():
        logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - [%(name)s] - %(message)s')
    
    # Simular que RUTA_BASE_PROYECTO está definida en settings
    if not hasattr(settings, 'RUTA_BASE_PROYECTO'):
        settings.RUTA_BASE_PROYECTO = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) # Sube un nivel si gestor_nivel.py está en una subcarpeta, o ajústalo según tu estructura. Asumimos que está al mismo nivel que main.py
        print(f"RUTA_BASE_PROYECTO (simulada para prueba): {settings.RUTA_BASE_PROYECTO}")

    # Simular AssetManager (muy básico)
    class MockAssetManager:
        def __init__(self, base_path):
            logger_gn.info(f"MockAssetManager inicializado con base_path: {base_path}")
        def get_sprite(self, *args, **kwargs):
            # Devuelve una superficie placeholder para que no falle la creación de entidades
            return pygame.Surface((32,32)) 
        def get_animation_frames(self, *args, **kwargs):
            return [pygame.Surface((32,32))]

    print("Probando GestorNivel (esto es una prueba básica)...")
    
    # Necesitamos inicializar pygame para pygame.sprite.Group y pygame.Surface
    pygame.init() 

    # Asegurar que tenemos un AssetManager (aunque sea mock) y config
    # Si AssetManager espera RUTA_ASSETS, y este a su vez RUTA_BASE_PROYECTO, debemos asegurarlos.
    # settings.RUTA_ASSETS = os.path.join(settings.RUTA_BASE_PROYECTO, "assets") # Ejemplo
    # if not os.path.isdir(settings.RUTA_ASSETS):
    #     os.makedirs(settings.RUTA_ASSETS, exist_ok=True) # Crear si no existe para que no falle AM

    try:
        asset_mgr_mock = MockAssetManager(settings.RUTA_BASE_PROYECTO if hasattr(settings, 'RUTA_BASE_PROYECTO') else ".")
        
        # Crear una instancia de GestorNivel
        gestor = GestorNivel(asset_mgr_mock)
        
        # Llamar al método que ahora agrupa la carga de obstáculos y enemigos
        gestor.cargar_elementos_nivel_inicial()
        
        print(f"Obstáculos cargados: {len(gestor.get_obstaculos())}")
        print(f"Enemigos generados: {len(gestor.get_enemigos())}")

        # Prueba de carga TMX (requeriría un archivo .tmx y assets configurados)
        # Suponiendo que tienes una constante RUTA_ASSETS_MAPAS en settings.py
        # if hasattr(settings, 'RUTA_ASSETS_MAPAS'):
        #     print("\nProbando carga TMX (fallará si 'mapa_prueba.tmx' no existe o pytmx no está instalado)...")
        #     gestor.cargar_mapa_desde_tmx("mapa_prueba.tmx") # Reemplazar con un mapa real en tu carpeta de assets/mapas
        # else:
        # print("\nSkipping TMX test: settings.RUTA_ASSETS_MAPAS no definida.")

    except Exception as e:
        print(f"Error durante la prueba de GestorNivel: {e}")
    finally:
        pygame.quit()
        print("Prueba de GestorNivel finalizada.") 