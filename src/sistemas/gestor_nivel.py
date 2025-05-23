import pygame
import pytmx # Para cargar mapas Tiled
import os
import random
from src.entidades.entidad_base import EntidadBase
from src.entidades.enemigo import Enemigo
from src.config import settings
from src.entidades.entorno import Arbol, Obstaculo # Asegúrate que las clases necesarias estén importadas

import logging
logger = logging.getLogger("gestor_nivel")

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

        logger.info("GestorNivel inicializado.", extra={"categoria_log": "log_gestor_nivel"})

    def cargar_elementos_nivel_inicial(self):
        """
        Carga los elementos iniciales del nivel (obstáculos y enemigos).
        Esto reemplaza la lógica hardcodeada que estaba en juego.py.
        En el futuro, esto podría cargar desde un archivo TMX o generar aleatoriamente.
        """
        self._cargar_obstaculos_hardcodeados()
        self._generar_enemigos_hardcodeados()
        logger.info("Elementos del nivel inicial cargados (obstáculos y enemigos).", extra={"categoria_log": "log_gestor_nivel"})

    def _cargar_obstaculos_hardcodeados(self):
        """
        Carga obstáculos (árboles) basados en una configuración hardcodeada.
        Esta es la lógica extraída de juego.py/_crear_entidades.
        """
        if settings.MODO_DEBUG_LOGS and settings.LOG_CATEGORIAS.get("log_gestor_nivel", False):
            logger.debug("GestorNivel: Cargando obstáculos hardcodeados (árboles).", extra={"categoria_log": "log_gestor_nivel"})

        arbol_config_list = [
            {"x": 300, "y": 150}, {"x": 500, "y": 300}, {"x": 100, "y": 400}
        ]
        for i, config_arbol_item in enumerate(arbol_config_list):
            arbol = Arbol(config_arbol_item["x"], config_arbol_item["y"], self.asset_manager)
            self.obstaculos.add(arbol)
            if settings.MODO_DEBUG_LOGS and settings.LOG_CATEGORIAS.get("log_gestor_nivel_detalle", False):
                 logger.debug(f"  GestorNivel: Árbol creado en ({config_arbol_item['x']}, {config_arbol_item['y']}) y añadido a obstáculos.", extra={"categoria_log": "log_gestor_nivel_detalle"})
        
        if settings.MODO_DEBUG_LOGS:
             logger.info(f"GestorNivel: {len(self.obstaculos)} obstáculos (árboles) cargados.", extra={"categoria_log": "log_gestor_nivel"})

    def _generar_enemigos_hardcodeados(self, jugador_pos=None):
        """
        Genera enemigos basados en una configuración hardcodeada.
        Esta es la lógica extraída de juego.py/_crear_entidades.
        """
        if settings.MODO_DEBUG_LOGS and settings.LOG_CATEGORIAS.get("log_gestor_nivel", False):
            logger.debug("GestorNivel: Generando enemigos hardcodeados.", extra={"categoria_log": "log_gestor_nivel"})

        enemigo_config_list = [
            {"x": 600, "y": 200}, {"x": 400, "y": 500}
        ]
        for config_enemigo_item in enemigo_config_list:
            enemigo = Enemigo(config_enemigo_item["x"], config_enemigo_item["y"], self.asset_manager)
            self.enemigos.add(enemigo)
            if settings.MODO_DEBUG_LOGS and settings.LOG_CATEGORIAS.get("log_gestor_nivel_detalle", False):
                 logger.debug(f"  GestorNivel: Enemigo creado en ({config_enemigo_item['x']}, {config_enemigo_item['y']}) y añadido a enemigos.", extra={"categoria_log": "log_gestor_nivel_detalle"})

        if settings.MODO_DEBUG_LOGS:
             logger.info(f"GestorNivel: {len(self.enemigos)} enemigos generados.", extra={"categoria_log": "log_gestor_nivel"})

    def cargar_mapa_desde_tmx(self, nombre_mapa_tmx):
        """
        Carga un mapa desde un archivo TMX (Tiled) y procesa sus capas.
        Popula los grupos de sprites de obstáculos, elementos decorativos, etc.
        (Implementación futura)
        """
        ruta_completa_mapa = os.path.join(settings.RUTA_ASSETS_MAPAS, nombre_mapa_tmx)
        if not os.path.exists(ruta_completa_mapa):
            logger.error(f"GestorNivel: No se encontró el archivo de mapa TMX: {ruta_completa_mapa}", extra={"categoria_log": "log_gestor_nivel"})
            return

        try:
            self.mapa_tmx = pytmx.load_pygame(ruta_completa_mapa, pixelalpha=True)
            logger.info(f"GestorNivel: Mapa TMX '{nombre_mapa_tmx}' cargado exitosamente.", extra={"categoria_log": "log_gestor_nivel"})
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
            logger.error(f"GestorNivel: Error al cargar o procesar el mapa TMX '{nombre_mapa_tmx}': {e}", exc_info=True, extra={"categoria_log": "log_gestor_nivel"})
            self.mapa_tmx = None

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
            logger.warning("Intento de obtener tile_data sin mapa TMX cargado.", extra={"categoria_log": "log_gestor_nivel"})
            return None
        try:
            capa = self.mapa_tmx.get_layer_by_name(capa_nombre)
            gid = capa.data[y][x]
            if gid != 0:
                propiedades = self.mapa_tmx.get_tile_properties_by_gid(gid)
                if propiedades:
                    return propiedades
            return None
        except Exception as e:
            logger.error(f"Error al obtener tile_data para la capa {capa_nombre} en ({x},{y}): {e}", extra={"categoria_log": "log_gestor_nivel"})
            return None

# if __name__ == '__main__':
#     # Configuración mínima para prueba (requiere que settings.py y config.py sean accesibles)
#     # Esto es solo para una prueba muy básica y local.
#     # ADVERTENCIA: Este bloque __main__ puede tener problemas con la nueva estructura de rutas
#     # y la forma en que accede a settings.py y config.py. Revisar si se va a usar.
#     if not logging.getLogger().hasHandlers():
#         logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - [%(name)s] - %(message)s')
#     
#     # Simular que RUTA_BASE_PROYECTO está definida en settings
#     # Esta lógica para encontrar la raíz del proyecto es propensa a errores
#     # y depende de dónde se ejecute el script.
#     if not hasattr(settings, 'RUTA_BASE_PROYECTO'):
#         # Intentar determinar la ruta base del proyecto para el ejemplo
#         # Esto es una suposición y puede no ser correcto.
#         script_dir = os.path.dirname(os.path.abspath(__file__))
#         # Si __file__ es src/sistemas/gestor_nivel.py, necesitamos subir dos niveles.
#         # Si __file__ es gestor_nivel.py en la raíz, necesitamos subir un nivel (o ninguno si está junto a main.py).
#         # Dada la estructura actual (src/sistemas), subir dos niveles para llegar a la raíz del proyecto.
#         settings.RUTA_BASE_PROYECTO = os.path.dirname(os.path.dirname(script_dir)) 
#         print(f"RUTA_BASE_PROYECTO (simulada para prueba __main__ en gestor_nivel.py): {settings.RUTA_BASE_PROYECTO}")
# 
#     # Simular AssetManager (muy básico)
#     class MockAssetManager:
#         def __init__(self, base_path):
#             logger.info(f"MockAssetManager inicializado con base_path: {base_path}", extra={"categoria_log": "log_gestor_nivel"})
#         def get_sprite(self, *args, **kwargs):
#             # Devuelve una superficie placeholder para que no falle la creación de entidades
#             return pygame.Surface((32,32)) 
#         def get_animation_frames(self, *args, **kwargs):
#             return [pygame.Surface((32,32))]
#         def get_image(self, nombre_asset, escalado_por_zoom=True, nuevo_ancho=None, nuevo_alto=None, escala_especifica=None, clave_color_transparente=None):
#             # Devuelve una superficie placeholder
#             surf = pygame.Surface((32,32))
#             surf.fill((100,100,100)) # Gris para que sea visible
#             return surf
# 
#     # Configurar settings y otras dependencias necesarias para la prueba
#     settings.MODO_DEBUG_LOGS = True
#     if "log_gestor_nivel" not in settings.LOG_CATEGORIAS:
#         settings.LOG_CATEGORIAS["log_gestor_nivel"] = True
#     if "log_gestor_nivel_detalle" not in settings.LOG_CATEGORIAS:
#         settings.LOG_CATEGORIAS["log_gestor_nivel_detalle"] = True
#     if not hasattr(settings, 'RUTA_ASSETS_MAPAS'):
#         settings.RUTA_ASSETS_MAPAS = os.path.join(settings.RUTA_BASE_PROYECTO, "assets", "data", "niveles")
#         print(f"RUTA_ASSETS_MAPAS (simulada para prueba): {settings.RUTA_ASSETS_MAPAS}")
# 
#     # Crear el directorio de mapas si no existe (para la prueba de carga TMX)
#     if not os.path.exists(settings.RUTA_ASSETS_MAPAS):
#         os.makedirs(settings.RUTA_ASSETS_MAPAS)
#         print(f"Directorio de mapas creado para prueba: {settings.RUTA_ASSETS_MAPAS}")
# 
#     # Crear un archivo TMX de prueba muy básico (opcional, si se quiere probar la carga)
#     # nombre_mapa_prueba = "mapa_prueba.tmx"
#     # ruta_mapa_prueba = os.path.join(settings.RUTA_ASSETS_MAPAS, nombre_mapa_prueba)
#     # with open(ruta_mapa_prueba, "w") as f:
#     #     f.write("<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n")
#     #     f.write("<map version=\"1.0\" tiledversion=\"1.2.4\" orientation=\"orthogonal\" renderorder=\"right-down\" width=\"10\" height=\"10\" tilewidth=\"32\" tileheight=\"32\" infinite=\"0\" nextobjectid=\"1\">\n")
#     #     f.write(" <tileset firstgid=\"1\" name=\"terrain\" tilewidth=\"32\" tileheight=\"32\" tilecount=\"1\" columns=\"1\">\n")
#     #     f.write("  <image source=\"../textures/terrain.png\" width=\"32\" height=\"32\"/>\n") # Asume una textura de prueba
#     #     f.write(" </tileset>\n")
#     #     f.write(" <layer name=\"CapaDeFondo\" width=\"10\" height=\"10\">\n")
#     #     f.write("  <data encoding=\"csv\">1,1,1,1,1,1,1,1,1,1,\n1,1,1,1,1,1,1,1,1,1,\n1,1,1,1,1,1,1,1,1,1,\n1,1,1,1,1,1,1,1,1,1,\n1,1,1,1,1,1,1,1,1,1,\n1,1,1,1,1,1,1,1,1,1,\n1,1,1,1,1,1,1,1,1,1,\n1,1,1,1,1,1,1,1,1,1,\n1,1,1,1,1,1,1,1,1,1,\n1,1,1,1,1,1,1,1,1,1</data>\n")
#     #     f.write(" </layer>\n")
#     #     f.write("</map>")
#     # print(f"Archivo TMX de prueba creado en: {ruta_mapa_prueba}")
# 
#     # Crear instancia de AssetManager (mock)
#     pygame.init() # Pygame necesita estar inicializado para algunas operaciones de Surface
#     asset_m = MockAssetManager(settings.RUTA_BASE_PROYECTO) 
# 
#     # Crear instancia de GestorNivel
#     gestor_nivel = GestorNivel(asset_m)
# 
#     # Probar la carga hardcodeada
#     logger.info("--- PROBANDO CARGA HARDCODEADA ---", extra={"categoria_log": "log_gestor_nivel"})
#     gestor_nivel.cargar_elementos_nivel_inicial()
#     print(f"Obstáculos cargados: {len(gestor_nivel.get_obstaculos())}")
#     print(f"Enemigos generados: {len(gestor_nivel.get_enemigos())}")
# 
#     # Probar la carga desde TMX (si se creó el archivo de prueba)
#     # logger.info("--- PROBANDO CARGA DESDE TMX ---", extra={"categoria_log": "log_gestor_nivel"})
#     # if os.path.exists(ruta_mapa_prueba):
#     #     gestor_nivel.cargar_mapa_desde_tmx(nombre_mapa_prueba)
#     #     if gestor_nivel.mapa_tmx:
#     #         print(f"Mapa TMX '{nombre_mapa_prueba}' cargado. Ancho: {gestor_nivel.mapa_tmx.width}, Alto: {gestor_nivel.mapa_tmx.height}")
#     # else:
#     #     print(f"Archivo TMX de prueba '{nombre_mapa_prueba}' no encontrado. Saltando prueba de carga TMX.")
#     
#     pygame.quit() 