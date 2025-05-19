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

# --- Loggers Categóricos para Juego ---
logger_juego_gen = logging.getLogger("log_general")
logger_juego_input = logging.getLogger("log_input")
logger_juego_estado = logging.getLogger("log_juego_estado")
# logger_juego_render ya no es necesario aquí, se usará en renderer.py

class Juego:
    def __init__(self):
        pygame.init()
        pygame.font.init()
        if settings.MODO_DEBUG_LOGS:
            logger_juego_gen.info("Juego: Pygame y módulos inicializados.")

        self.pantalla = pygame.display.set_mode((config.ANCHO_PANTALLA, config.ALTO_PANTALLA))
        pygame.display.set_caption(config.TITULO_JUEGO)
        self.reloj = pygame.time.Clock()

        if not hasattr(settings, 'RUTA_BASE_PROYECTO') or not settings.RUTA_BASE_PROYECTO:
            logger_juego_gen.error("Juego ERROR: RUTA_BASE_PROYECTO no configurada en settings.py.")
        
        self.asset_manager = AssetManager(settings.RUTA_BASE_PROYECTO)
        self.asset_manager.preload_all()
        if settings.MODO_DEBUG_LOGS:
            logger_juego_gen.info("Juego: AssetManager inicializado y assets precargados.")

        self.gestor_nivel = GestorNivel(self.asset_manager)
        if settings.MODO_DEBUG_LOGS:
            logger_juego_gen.info("Juego: GestorNivel instanciado.")

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
            logger_juego_gen.info("Juego: GestorEventos instanciado.")

        self.gestor_estado = GestorEstado(
            self.jugador, 
            self.enemigos, 
            self.obstaculos, 
            self.todos_los_sprites
        )
        if settings.MODO_DEBUG_LOGS:
            logger_juego_gen.info("Juego: GestorEstado instanciado.")

        # Crear instancia del Renderer
        self.renderer = Renderer(self.pantalla, self.camara, self.asset_manager)
        if settings.MODO_DEBUG_LOGS:
            logger_juego_gen.info("Juego: Renderer instanciado.")

        self.running = True
        if settings.MODO_DEBUG_LOGS:
            logger_juego_gen.info("Juego: Elementos del juego inicializados. Juego listo.")
        if settings.MODO_DEBUG_LOGS and settings.LOG_CATEGORIAS.get("log_general", False):
            logger_juego_gen.debug(f"  Juego init: Pantalla: {config.ANCHO_PANTALLA}x{config.ALTO_PANTALLA}, Zoom inicial: {self.factor_zoom_actual}")

    def _manejar_eventos(self):
        eventos_pygame = pygame.event.get()
        self.gestor_eventos.procesar_eventos(eventos_pygame)

        if self.gestor_eventos.debe_salir():
            self.running = False
            if settings.MODO_DEBUG_LOGS and settings.LOG_CATEGORIAS.get("log_input", False):
                 logger_juego_input.debug("Juego: Solicitud de salir procesada.")

    # Método para que GestorEventos actualice el zoom en Juego
    def actualizar_factor_zoom(self, nuevo_zoom):
        self.factor_zoom_actual = nuevo_zoom
        if settings.MODO_DEBUG_LOGS and settings.LOG_CATEGORIAS.get("log_input", False): # O log_camara
            logger_juego_input.info(f"Juego: Factor de zoom actualizado a {self.factor_zoom_actual:.2f} por GestorEventos")

    def _actualizar_estado(self, delta_time):
        if settings.MODO_DEBUG_LOGS and settings.LOG_CATEGORIAS.get("log_juego_estado", False):
            logger_juego_estado.debug(f"Juego _actualizar_estado: Inicio. Delta: {delta_time:.4f}s.")
        
        teclas_presionadas = pygame.key.get_pressed()
        self.gestor_estado.actualizar_entidades_y_logica(teclas_presionadas, delta_time)

        if settings.MODO_DEBUG_LOGS and settings.LOG_CATEGORIAS.get("log_juego_estado", False):
            logger_juego_estado.debug("  Juego _actualizar_estado: Actualizando cámara y HUD...")
        
        self.camara.update(self.jugador, self.factor_zoom_actual)
        self.hud.update() 
        
        if settings.MODO_DEBUG_LOGS and settings.LOG_CATEGORIAS.get("log_juego_estado", False):
            logger_juego_estado.debug("Juego _actualizar_estado: Fin.")
    
    def _renderizar(self):
        """Delega el renderizado de la escena y el HUD al Renderer."""
        # El Renderer se encarga de limpiar la pantalla y dibujar el fondo.
        # Los sprites ya están en self.todos_los_sprites.
        # El HUD es self.hud.
        # El factor de zoom es self.factor_zoom_actual.

        # 1. Renderizar la escena principal (fondo, sprites, hitboxes de debug)
        # El método render_escena_completa de Renderer ya no hace flip().
        # Tampoco renderiza el HUD directamente para mayor control aquí.
        self.renderer.render_escena_completa(self.todos_los_sprites, self.factor_zoom_actual)

        # 2. Renderizar el HUD sobre la escena
        # Asumimos que self.hud tiene un método render(superficie_destino)
        # o que self.renderer.render_hud puede manejarlo.
        self.renderer.render_hud(self.hud) 

        # 3. Actualizar la pantalla completa
        pygame.display.flip()

        if settings.MODO_DEBUG_LOGS and settings.LOG_CATEGORIAS.get("log_general", False): # Un log general para el ciclo de renderizado
            logger_juego_gen.debug("Juego: Ciclo de renderizado completado (flip ejecutado).")

    def run(self):
        if settings.MODO_DEBUG_LOGS:
            logger_juego_gen.info("Juego: Iniciando bucle principal...")
        while self.running:
            delta_time = self.reloj.tick(config.FPS) / 1000.0
            
            self._manejar_eventos()
            if not self.running: # Salir pronto si _manejar_eventos cambió self.running
                break
            self._actualizar_estado(delta_time)
            self._renderizar()
        
        self.quit()

    def quit(self):
        if settings.MODO_DEBUG_LOGS:
            logger_juego_gen.info("Juego: Saliendo de Pygame y del sistema...")
        pygame.quit()
        sys.exit()

# Definición temporal de collide_rect_extended si no está en utils.py
# Esta definición debería moverse a un archivo de utilidades apropiado.
# def collide_rect_extended(sprite1, sprite2):
#     if hasattr(sprite1, 'hitbox') and hasattr(sprite2, 'hitbox'):
#         return sprite1.hitbox.colliderect(sprite2.hitbox)
#     elif hasattr(sprite1, 'rect') and hasattr(sprite2, 'rect'):
#         return sprite1.rect.colliderect(sprite2.rect) # Fallback a rect si no hay hitbox
#     return False