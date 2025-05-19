import pygame
import sys
import logging
# import math # Ya no es necesario directamente en juego.py para el renderizado de fondo

import config
import settings

from asset_manager import AssetManager
from jugador import Jugador
# from enemigo import Enemigo # Enemigos se gestionan a través de GestorNivel y GestorEstado
# from entorno import Arbol # Obstáculos se gestionan a través de GestorNivel y GestorEstado
from camara import Camara2D
from hud import DebugHUD
from gestor_nivel import GestorNivel
from gestor_eventos import GestorEventos
from gestor_estado import GestorEstado
from renderer import Renderer # <--- NUEVA IMPORTACIÓN
from game_initializer import crear_elementos_juego # <--- NUEVA IMPORTACIÓN

# Logger para el módulo juego
logger = logging.getLogger("juego")

class Juego:
    def __init__(self):
        logger.info("Iniciando Pygame y módulos del juego...", extra={"categoria_log": "log_general"})
        pygame.init()
        pygame.font.init()
        if settings.MODO_DEBUG_LOGS:
            logger.debug("Pygame y fuentes inicializados.", extra={"categoria_log": "log_general"})

        self.pantalla = pygame.display.set_mode((config.ANCHO_PANTALLA, config.ALTO_PANTALLA))
        pygame.display.set_caption(config.TITULO_JUEGO)
        self.reloj = pygame.time.Clock()

        if not hasattr(settings, 'RUTA_BASE_PROYECTO') or not settings.RUTA_BASE_PROYECTO:
            logger.error("Juego ERROR: RUTA_BASE_PROYECTO no configurada en settings.py.", extra={"categoria_log": "log_general"})
        
        self.asset_manager = AssetManager(settings.RUTA_BASE_PROYECTO)
        self.asset_manager.preload_all()
        if settings.MODO_DEBUG_LOGS:
            logger.debug("AssetManager inicializado y assets precargados.", extra={"categoria_log": "log_assets"}) # Usar log_assets si existe o log_general

        self.gestor_nivel = GestorNivel(self.asset_manager)
        if settings.MODO_DEBUG_LOGS:
            logger.debug("GestorNivel instanciado.", extra={"categoria_log": "log_general"})

        self.factor_zoom_actual = settings.FACTOR_ZOOM_MIN 
        
        # En su lugar, llamamos a la función del nuevo módulo
        (self.jugador, self.obstaculos, self.enemigos, self.todos_los_sprites,
         self.camara, self.hud) = crear_elementos_juego(
            asset_manager=self.asset_manager,
            gestor_nivel=self.gestor_nivel,
            factor_zoom_inicial=self.factor_zoom_actual,
            juego_ref_para_hud=self  # Pasamos la instancia de Juego para el HUD
        )

        self.gestor_eventos = GestorEventos(self.jugador, self.hud, self) # Pasar self (Juego) para control de zoom
        if settings.MODO_DEBUG_LOGS:
            logger.debug("GestorEventos instanciado.", extra={"categoria_log": "log_event_handler"}) # o log_general

        self.gestor_estado = GestorEstado(
            self.jugador, 
            self.enemigos, 
            self.obstaculos, 
            self.todos_los_sprites
        )
        if settings.MODO_DEBUG_LOGS:
            logger.debug("GestorEstado instanciado.", extra={"categoria_log": "log_gestor_estado"}) # o log_general

        # Crear instancia del Renderer
        self.renderer = Renderer(self.pantalla, self.camara, self.asset_manager)
        if settings.MODO_DEBUG_LOGS:
            logger.debug("Renderer instanciado.", extra={"categoria_log": "log_general"}) # Asumimos una categoría general para renderer por ahora

        self.running = True
        logger.info("Juego inicializado y listo para ejecutarse.", extra={"categoria_log": "log_general"})
        if settings.MODO_DEBUG_LOGS and settings.LOG_CATEGORIAS.get("log_general", False):
            logger.debug(f"  Detalles inicialización: Pantalla: {config.ANCHO_PANTALLA}x{config.ALTO_PANTALLA}, Zoom inicial: {self.factor_zoom_actual}", extra={"categoria_log": "log_general"})

    def _manejar_eventos(self):
        if settings.MODO_DEBUG_LOGS and settings.LOG_CATEGORIAS.get("log_input", False):
            logger.debug("Procesando eventos Pygame...", extra={"categoria_log": "log_input"})
        eventos_pygame = pygame.event.get()
        self.gestor_eventos.procesar_eventos(eventos_pygame)

        if self.gestor_eventos.debe_salir():
            self.running = False
            if settings.MODO_DEBUG_LOGS and settings.LOG_CATEGORIAS.get("log_input", False):
                 logger.debug("Solicitud de salir del juego procesada.", extra={"categoria_log": "log_input"})

    # Método para que GestorEventos actualice el zoom en Juego
    def actualizar_factor_zoom(self, nuevo_zoom):
        self.factor_zoom_actual = nuevo_zoom
        if settings.MODO_DEBUG_LOGS and settings.LOG_CATEGORIAS.get("log_camara", False): # Usar log_camara o log_input
            logger.info(f"Factor de zoom actualizado a {self.factor_zoom_actual:.2f}", extra={"categoria_log": "log_camara"})

    def _actualizar_estado(self, delta_time):
        if settings.MODO_DEBUG_LOGS and settings.LOG_CATEGORIAS.get("log_juego_estado", False):
            logger.debug(f"Inicio de actualización de estado. Delta: {delta_time:.4f}s.", extra={"categoria_log": "log_juego_estado"})
        
        teclas_presionadas = pygame.key.get_pressed()
        self.gestor_estado.actualizar_entidades_y_logica(teclas_presionadas, delta_time)

        if settings.MODO_DEBUG_LOGS and settings.LOG_CATEGORIAS.get("log_juego_estado", False):
            logger.debug("Actualizando cámara y HUD...", extra={"categoria_log": "log_juego_estado"})
        
        self.camara.update(self.jugador, self.factor_zoom_actual)
        self.hud.update() 
        
        if settings.MODO_DEBUG_LOGS and settings.LOG_CATEGORIAS.get("log_juego_estado", False):
            logger.debug("Fin de actualización de estado.", extra={"categoria_log": "log_juego_estado"})
    
    def _renderizar(self):
        """Delega el renderizado de la escena y el HUD al Renderer."""
        if settings.MODO_DEBUG_LOGS and settings.LOG_CATEGORIAS.get("log_general", False): # O una categoría "log_render"
            logger.debug("Iniciando ciclo de renderizado...", extra={"categoria_log": "log_general"})
        
        self.renderer.render_escena_completa(self.todos_los_sprites, self.factor_zoom_actual)
        self.renderer.render_hud(self.hud) 
        pygame.display.flip()

        if settings.MODO_DEBUG_LOGS and settings.LOG_CATEGORIAS.get("log_general", False):
            logger.debug("Ciclo de renderizado completado (flip ejecutado).", extra={"categoria_log": "log_general"})

    def run(self):
        self.running = True
        logger.info("Bucle principal iniciado.", extra={"categoria_log": "log_general"})
        while self.running:
            delta_time_secs = self.reloj.tick(settings.FPS) / 1000.0
            # Log de prueba para DuplicateFilter
            logger.debug("MENSAJE DE PRUEBA REPETIDO PARA FILTRO", extra={"categoria_log": "log_general"})

            # Manejo de eventos
            self._manejar_eventos()
            if not self.running:
                break
            self._actualizar_estado(delta_time_secs)
            self._renderizar()
        
        self.quit()

    def quit(self):
        logger.info("Saliendo de Pygame y del sistema...", extra={"categoria_log": "log_general"})
        pygame.quit()
        sys.exit()

# La función collide_rect_extended ha sido movida a utils.py