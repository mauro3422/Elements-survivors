import pygame
import logging
from src.config import settings
from src.utils.utils import collide_rect_extended

# Unificar logger
logger = logging.getLogger("gestor_estado")

class GestorEstado:
    def __init__(self, jugador, enemigos_grupo, obstaculos_grupo, todos_los_sprites_grupo):
        """
        Inicializa el GestorEstado.

        Args:
            jugador: La instancia del jugador.
            enemigos_grupo: Grupo de sprites de enemigos.
            obstaculos_grupo: Grupo de sprites de obstáculos.
            todos_los_sprites_grupo: Grupo con todos los sprites para actualizaciones generales (si es necesario).
        """
        self.jugador = jugador
        self.enemigos_grupo = enemigos_grupo
        self.obstaculos_grupo = obstaculos_grupo
        self.todos_los_sprites_grupo = todos_los_sprites_grupo # Puede no ser necesario si actualizamos selectivamente

        log_gs_enabled = settings.MODO_DEBUG_LOGS and settings.LOG_CATEGORIAS.get("log_gestor_estado", False)
        if log_gs_enabled:
            logger.debug("GestorEstado inicializado.", extra={"categoria_log": "log_gestor_estado"})

    def actualizar_entidades_y_logica(self, teclas_presionadas, delta_time, mundo_ancho, mundo_alto):
        logger.debug("GestorEstado.actualizar_entidades_y_logica() - INICIO", extra={"categoria_log": "log_gestor_estado_detalle"})
        """
        Actualiza el estado de todas las entidades relevantes y maneja la lógica principal del juego.

        Args:
            teclas_presionadas: El estado actual de las teclas presionadas (de pygame.key.get_pressed()).
            delta_time: El tiempo transcurrido desde el último frame, en segundos.
            mundo_ancho (int): Ancho total del mundo del juego.
            mundo_alto (int): Alto total del mundo del juego.
        """
        log_gs_enabled = settings.MODO_DEBUG_LOGS and settings.LOG_CATEGORIAS.get("log_gestor_estado", False)
        log_gs_detalle_enabled = settings.MODO_DEBUG_LOGS and settings.LOG_CATEGORIAS.get("log_gestor_estado_detalle", False)

        if log_gs_detalle_enabled:
            logger.debug(f"GestorEstado: Inicio actualizar_entidades_y_logica. Delta: {delta_time:.4f}s", extra={"categoria_log": "log_gestor_estado_detalle"})

        logger.debug("GestorEstado - ANTES de actualizar enemigos", extra={"categoria_log": "log_gestor_estado_detalle"})
        # 1. Actualizar Enemigos
        if log_gs_enabled:
            if not self.enemigos_grupo:
                logger.debug("  GestorEstado: No hay enemigos para actualizar.", extra={"categoria_log": "log_gestor_estado"})
            else:
                logger.debug(f"  GestorEstado: Actualizando {len(self.enemigos_grupo)} enemigos...", extra={"categoria_log": "log_gestor_estado"})
        
        logger.debug("GestorEstado - INICIO BUCLE ENEMIGOS", extra={"categoria_log": "log_gestor_estado_detalle"})
        for i, enemigo_actual in enumerate(self.enemigos_grupo):
            logger.debug(f"GestorEstado - Iteracion {i}, Enemigo: {getattr(enemigo_actual, 'nombre_log_entidad', 'N/A')}", extra={"categoria_log": "log_gestor_estado_detalle"})
            # Crear grupo de obstáculos específico para este enemigo
            obstaculos_para_enemigo_actual = pygame.sprite.Group(self.obstaculos_grupo.sprites())
            for j, otro_enemigo in enumerate(self.enemigos_grupo):
                if i != j: # No añadir el enemigo actual a sus propios obstáculos
                    obstaculos_para_enemigo_actual.add(otro_enemigo)
            
            if self.jugador: 
                obstaculos_para_enemigo_actual.add(self.jugador)

            if hasattr(enemigo_actual, 'update'):
                logger.debug(f"GestorEstado - ANTES de llamar a update() para {getattr(enemigo_actual, 'nombre_log_entidad', 'N/A')}", extra={"categoria_log": "log_gestor_estado_detalle"})
                enemigo_actual.update(self.jugador, obstaculos_para_enemigo_actual, delta_time, mundo_ancho, mundo_alto)
                logger.debug(f"GestorEstado - DESPUÉS de llamar a update() para {getattr(enemigo_actual, 'nombre_log_entidad', 'N/A')}", extra={"categoria_log": "log_gestor_estado_detalle"})

        logger.debug("GestorEstado - DESPUÉS de actualizar enemigos", extra={"categoria_log": "log_gestor_estado_detalle"})

        logger.debug("GestorEstado - ANTES de eliminar enemigos muertos", extra={"categoria_log": "log_gestor_estado_detalle"})
        # Eliminar enemigos muertos de los grupos de sprites
        enemigos_a_eliminar = []
        for enemigo in self.enemigos_grupo:
            if hasattr(enemigo, 'ha_muerto') and enemigo.ha_muerto:
                enemigos_a_eliminar.append(enemigo)
        
        for enemigo_muerto in enemigos_a_eliminar:
            if log_gs_enabled:
                logger.info(f"  GestorEstado: Eliminando enemigo muerto {getattr(enemigo_muerto, 'nombre_log_entidad', str(enemigo_muerto))} de los grupos de sprites", extra={"categoria_log": "log_gestor_estado"})
            self.enemigos_grupo.remove(enemigo_muerto)
            if enemigo_muerto in self.todos_los_sprites_grupo:
                self.todos_los_sprites_grupo.remove(enemigo_muerto)

        logger.debug("GestorEstado - DESPUÉS de eliminar enemigos muertos", extra={"categoria_log": "log_gestor_estado_detalle"})

        logger.debug("GestorEstado - ANTES de actualizar jugador", extra={"categoria_log": "log_gestor_estado_detalle"})
        # 2. Actualizar Jugador
        logger.debug("GestorEstado - ANTES de crear obstaculos_para_jugador", extra={"categoria_log": "log_gestor_estado_detalle"})
        obstaculos_para_jugador = pygame.sprite.Group(self.obstaculos_grupo.sprites(), self.enemigos_grupo.sprites())
        logger.debug(f"GestorEstado - DESPUÉS de crear obstaculos_para_jugador. Contiene {len(obstaculos_para_jugador)} sprites.", extra={"categoria_log": "log_gestor_estado_detalle"})
        if log_gs_enabled:
            logger.debug("  GestorEstado: Actualizando jugador...", extra={"categoria_log": "log_gestor_estado"})
        
        if hasattr(self.jugador, 'update'):
            logger.debug("GestorEstado - ANTES de self.jugador.update()", extra={"categoria_log": "log_gestor_estado_detalle"})
            self.jugador.update(teclas_presionadas, obstaculos_para_jugador, self.enemigos_grupo, mundo_ancho, mundo_alto, delta_time)
            logger.debug("GestorEstado - DESPUÉS de self.jugador.update()", extra={"categoria_log": "log_gestor_estado_detalle"})
        logger.debug("GestorEstado - DESPUÉS de actualizar jugador", extra={"categoria_log": "log_gestor_estado_detalle"})

        logger.debug("GestorEstado - ANTES de actualizar otros sprites", extra={"categoria_log": "log_gestor_estado_detalle"})
        # 3. Actualizar otros sprites (ej. árboles)
        if log_gs_detalle_enabled:
            num_otros_sprites = 0
            if self.todos_los_sprites_grupo:
                num_otros_sprites = sum(1 for s in self.todos_los_sprites_grupo if s != self.jugador and s not in self.enemigos_grupo and hasattr(s, 'update'))
            if num_otros_sprites > 0:
                logger.debug(f"  GestorEstado: Actualizando {num_otros_sprites} otros sprites (ej. Arbol)...", extra={"categoria_log": "log_gestor_estado_detalle"})

        if self.todos_los_sprites_grupo:
            for sprite in self.todos_los_sprites_grupo:
                if sprite != self.jugador and sprite not in self.enemigos_grupo: 
                    if hasattr(sprite, 'update'):
                        try:
                            sprite.update(delta_time) 
                        except TypeError:
                            sprite.update() 

        logger.debug("GestorEstado - DESPUÉS de actualizar otros sprites", extra={"categoria_log": "log_gestor_estado_detalle"})

        logger.debug("GestorEstado - ANTES de manejar colisiones por contacto", extra={"categoria_log": "log_gestor_estado_detalle"})
        # 4. Manejar colisiones para daño por contacto jugador <-> enemigos
        colisiones_contacto = pygame.sprite.spritecollide(self.jugador, self.enemigos_grupo, False, collide_rect_extended)
        if colisiones_contacto:
            if log_gs_enabled:
                nombres_enemigos_col = [getattr(e, 'nombre_log_entidad', type(e).__name__) for e in colisiones_contacto]
                logger.debug(f"  GestorEstado: Jugador colisiona por contacto con: {nombres_enemigos_col}", extra={"categoria_log": "log_gestor_estado"})
            for enemigo_colisionado in colisiones_contacto:
                dano = getattr(enemigo_colisionado, 'dano_ataque', settings.ENEMIGO_DANO_CONTACTO_DEFAULT)
                tipo_dano = "contacto_enemigo"
                
                if hasattr(self.jugador, 'recibir_dano'):
                    # self.jugador.recibir_dano(dano, tipo_dano) # <--- DAÑO POR CONTACTO ACTUALMENTE DESACTIVADO PARA PRUEBAS
                    if log_gs_enabled: 
                        logger.debug(f"    GestorEstado: Jugador en contacto con {getattr(enemigo_colisionado, 'nombre_log_entidad', type(enemigo_colisionado).__name__)}. Daño de {dano} NO aplicado (actualmente desactivado).", extra={"categoria_log": "log_gestor_estado"})
                else:
                    if log_gs_enabled:
                        logger.error(f"  GestorEstado: Jugador no tiene método 'recibir_dano'. No se aplicó daño de {getattr(enemigo_colisionado, 'nombre_log_entidad', type(enemigo_colisionado).__name__)}.", extra={"categoria_log": "log_gestor_estado"})
        logger.debug("GestorEstado - DESPUÉS de manejar colisiones por contacto", extra={"categoria_log": "log_gestor_estado_detalle"})
        
        # --- INICIO NUEVO LOG DE POSICIONES ---
        log_pos_debug_enabled = settings.MODO_DEBUG_LOGS and settings.LOG_CATEGORIAS.get("log_posiciones_debug", False)
        if log_pos_debug_enabled:
            if self.jugador and hasattr(self.jugador, 'hitbox'):
                logger.debug(f"[POS_DEBUG] Jugador: {getattr(self.jugador, 'nombre_log_entidad', 'JUGADOR')} HB: {self.jugador.hitbox.topleft}, Size: {self.jugador.hitbox.size}", extra={"categoria_log": "log_posiciones_debug"})
            
            if self.enemigos_grupo:
                for enemigo in self.enemigos_grupo:
                    if hasattr(enemigo, 'hitbox'):
                        logger.debug(f"[POS_DEBUG] Enemigo: {getattr(enemigo, 'nombre_log_entidad', type(enemigo).__name__)} HB: {enemigo.hitbox.topleft}, Size: {enemigo.hitbox.size}", extra={"categoria_log": "log_posiciones_debug"})
            else:
                logger.debug("[POS_DEBUG] No hay enemigos activos.", extra={"categoria_log": "log_posiciones_debug"})
        # --- FIN NUEVO LOG DE POSICIONES ---

        if log_gs_detalle_enabled:
            logger.debug("GestorEstado: Fin actualizar_entidades_y_logica.", extra={"categoria_log": "log_gestor_estado_detalle"})

        logger.debug("GestorEstado.actualizar_entidades_y_logica() - FIN", extra={"categoria_log": "log_gestor_estado_detalle"})

    def limpiar_grupos_y_estado(self):
        """Limpia todos los grupos de sprites y resetea referencias internas."""
        logger.info("Limpiando grupos de sprites y estado en GestorEstado...", extra={"categoria_log": "log_gestor_estado"})
        
        if self.todos_los_sprites_grupo:
            self.todos_los_sprites_grupo.empty()
        if self.enemigos_grupo:
            self.enemigos_grupo.empty()
        if self.obstaculos_grupo:
            self.obstaculos_grupo.empty()
        
        self.jugador = None 
        
        logger.info("GestorEstado limpiado.", extra={"categoria_log": "log_gestor_estado"})

# Ejemplo de cómo podría usarse (esto no iría aquí en el código final)
# if __name__ == '__main__':
#     # Se necesitarían mocks o instancias reales de Jugador, AssetManager, etc.
#     # para probar GestorEstado completamente.
#     print("Ejecutando un placeholder de __main__ para GestorEstado")
# 
#     # Inicialización básica de Pygame para poder crear sprites y grupos
#     pygame.init()
#     pantalla_dummy = pygame.display.set_mode((100,100)) # Necesario para pygame.sprite.Sprite
# 
#     # Crear instancias dummy (simplificado)
#     # En un caso real, se usaría el AssetManager
#     class DummyPlayer(pygame.sprite.Sprite):
# ... existing code ... 