import pygame
import logging
from src.config import settings # MODIFICADO
from src.utils.utils import collide_rect_extended # NUEVA IMPORTACIÓN

# Unificar logger
logger = logging.getLogger("gestor_estado")

# Definición temporal de collide_rect_extended si no está en utils.py
# El usuario debe asegurarse de que esta función esté correctamente importada o definida.
# TODO: Mover collide_rect_extended a un módulo de utilidades (ej. src/utils/physics_utils.py o similar)
# y luego importarla aquí: from src.utils.physics_utils import collide_rect_extended
# def collide_rect_extended(sprite1, sprite2): # ELIMINADA DEFINICIÓN LOCAL
#     if hasattr(sprite1, 'hitbox') and hasattr(sprite2, 'hitbox'):
#         return sprite1.hitbox.colliderect(sprite2.hitbox)
#     elif hasattr(sprite1, 'rect') and hasattr(sprite2, 'rect'):
#         return sprite1.rect.colliderect(sprite2.rect) # Fallback a rect si no hay hitbox
#     return False

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

    def actualizar_entidades_y_logica(self, teclas_presionadas, delta_time):
        """
        Actualiza el estado de todas las entidades relevantes y maneja la lógica principal del juego.

        Args:
            teclas_presionadas: El estado actual de las teclas presionadas (de pygame.key.get_pressed()).
            delta_time: El tiempo transcurrido desde el último frame, en segundos.
        """
        log_gs_enabled = settings.MODO_DEBUG_LOGS and settings.LOG_CATEGORIAS.get("log_gestor_estado", False)
        log_gs_detalle_enabled = settings.MODO_DEBUG_LOGS and settings.LOG_CATEGORIAS.get("log_gestor_estado_detalle", False)
        log_jugador_cmb_enabled = settings.MODO_DEBUG_LOGS and settings.LOG_CATEGORIAS.get("log_jugador_cmb", False) # Para el log de daño al jugador

        if log_gs_detalle_enabled:
            logger.debug(f"GestorEstado: Inicio actualizar_entidades_y_logica. Delta: {delta_time:.4f}s", extra={"categoria_log": "log_gestor_estado_detalle"})

        # 1. Actualizar Enemigos
        if log_gs_enabled:
            if not self.enemigos_grupo:
                logger.debug("  GestorEstado: No hay enemigos para actualizar.", extra={"categoria_log": "log_gestor_estado"})
            else:
                logger.debug(f"  GestorEstado: Actualizando {len(self.enemigos_grupo)} enemigos...", extra={"categoria_log": "log_gestor_estado"})
        
        # Los enemigos necesitan al jugador (para la IA) y los obstáculos (para colisiones)
        # También necesitan otros enemigos como obstáculos.
        for i, enemigo_actual in enumerate(self.enemigos_grupo):
            # Crear grupo de obstáculos específico para este enemigo
            obstaculos_para_enemigo_actual = pygame.sprite.Group(self.obstaculos_grupo.sprites())
            for j, otro_enemigo in enumerate(self.enemigos_grupo):
                if i != j: # No añadir el enemigo actual a sus propios obstáculos
                    obstaculos_para_enemigo_actual.add(otro_enemigo)
            
            # Asumimos que Enemigo.update() toma (objetivo_jugador, obstaculos_lista, delta_time)
            # Los logs internos de enemigo_actual.update() ya usan sus categorías.
            if hasattr(enemigo_actual, 'update'):
                 # Pasar la hitbox del jugador como objetivo
                enemigo_actual.update(self.jugador.hitbox, obstaculos_para_enemigo_actual, delta_time)

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

        # 2. Actualizar Jugador
        # El jugador necesita los obstáculos y los enemigos para sus colisiones.
        obstaculos_para_jugador = pygame.sprite.Group(self.obstaculos_grupo.sprites(), self.enemigos_grupo.sprites())
        if log_gs_enabled:
            logger.debug("  GestorEstado: Actualizando jugador...", extra={"categoria_log": "log_gestor_estado"})
        
        # Asumimos que Jugador.update() toma (teclas, obstaculos, enemigos, ancho_mundo, alto_mundo, delta_time)
        # Jugador.update() tiene sus propios logs internos categóricos.
        if hasattr(self.jugador, 'update'):
            self.jugador.update(teclas_presionadas, obstaculos_para_jugador, self.enemigos_grupo, settings.ANCHO_MUNDO_JUEGO, settings.ALTO_MUNDO_JUEGO, delta_time)

        # 3. Actualizar otros sprites (ej. árboles)
        # Esto es si los sprites en `todos_los_sprites_grupo` que no son jugador ni enemigos necesitan update.
        # Por ejemplo, un árbol con animación.
        if log_gs_detalle_enabled:
            num_otros_sprites = 0
            if self.todos_los_sprites_grupo:
                num_otros_sprites = sum(1 for s in self.todos_los_sprites_grupo if s != self.jugador and s not in self.enemigos_grupo and hasattr(s, 'update'))
            if num_otros_sprites > 0:
                logger.debug(f"  GestorEstado: Actualizando {num_otros_sprites} otros sprites (ej. Arbol)...", extra={"categoria_log": "log_gestor_estado_detalle"})

        if self.todos_los_sprites_grupo:
            for sprite in self.todos_los_sprites_grupo:
                if sprite != self.jugador and sprite not in self.enemigos_grupo: # Evitar doble actualización
                    if hasattr(sprite, 'update'):
                        # Si el update de estos sprites necesita delta_time, hay que pasarlo.
                        # Por ahora, asumimos un update simple sin args o con delta_time.
                        try:
                            sprite.update(delta_time) # Intentar pasar delta_time
                        except TypeError:
                            sprite.update() # Fallback si no acepta delta_time


        # 4. Manejar colisiones para daño por contacto jugador <-> enemigos
        colisiones_contacto = pygame.sprite.spritecollide(self.jugador, self.enemigos_grupo, False, collide_rect_extended)
        if colisiones_contacto:
            if log_gs_enabled:
                nombres_enemigos_col = [getattr(e, 'nombre_log_entidad', type(e).__name__) for e in colisiones_contacto]
                logger.debug(f"  GestorEstado: Jugador colisiona por contacto con: {nombres_enemigos_col}", extra={"categoria_log": "log_gestor_estado"})
            for enemigo_colisionado in colisiones_contacto:
                dano = getattr(enemigo_colisionado, 'dano_ataque', settings.ENEMIGO_DANO_CONTACTO_DEFAULT)
                tipo_dano = "contacto_enemigo"
                
                # Asegurarse de que el jugador tiene el método recibir_dano
                if hasattr(self.jugador, 'recibir_dano'):
                    # self.jugador.recibir_dano(dano, tipo_dano) # <--- DESACTIVADO TEMPORALMENTE PARA PRUEBAS
                    if log_gs_enabled: # Esta categoría es para el gestor de estado
                        # Loguear que el daño SE HABRÍA aplicado
                        logger.debug(f"    GestorEstado: Jugador HABRÍA recibido {dano} de daño por contacto de {getattr(enemigo_colisionado, 'nombre_log_entidad', type(enemigo_colisionado).__name__)}. (DAÑO DESACTIVADO)", extra={"categoria_log": "log_gestor_estado"})
                else:
                    if log_gs_enabled:
                        logger.error(f"  GestorEstado: Jugador no tiene método 'recibir_dano'. No se aplicó daño de {getattr(enemigo_colisionado, 'nombre_log_entidad', type(enemigo_colisionado).__name__)}.", extra={"categoria_log": "log_gestor_estado"})
        
        if log_gs_detalle_enabled:
            logger.debug("GestorEstado: Fin actualizar_entidades_y_logica.", extra={"categoria_log": "log_gestor_estado_detalle"})

        # No es necesario devolver nada, las actualizaciones modifican los objetos directamente. 