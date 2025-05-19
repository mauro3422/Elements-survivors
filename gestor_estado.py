import pygame
import logging
import settings
import config # Para DANO_CONTACTO_ENEMIGO_DEFAULT y ANCHO_MUNDO, ALTO_MUNDO

# Loggers para GestorEstado
logger_gs = logging.getLogger(__name__) # Usará el nombre del módulo, ej. 'gestor_estado'
logger_gs_detalle = logging.getLogger(f"{__name__}_detalle") # Para logs más verbosos

# Definición temporal de collide_rect_extended si no está en utils.py
# El usuario debe asegurarse de que esta función esté correctamente importada o definida.
def collide_rect_extended(sprite1, sprite2):
    if hasattr(sprite1, 'hitbox') and hasattr(sprite2, 'hitbox'):
        return sprite1.hitbox.colliderect(sprite2.hitbox)
    elif hasattr(sprite1, 'rect') and hasattr(sprite2, 'rect'):
        return sprite1.rect.colliderect(sprite2.rect) # Fallback a rect si no hay hitbox
    return False

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

        if settings.MODO_DEBUG_LOGS and settings.LOG_CATEGORIAS.get("log_gestor_estado", False): # Nueva categoría
            logger_gs.debug("GestorEstado inicializado.")

    def actualizar_entidades_y_logica(self, teclas_presionadas, delta_time):
        """
        Actualiza el estado de todas las entidades relevantes y maneja la lógica principal del juego.

        Args:
            teclas_presionadas: El estado actual de las teclas presionadas (de pygame.key.get_pressed()).
            delta_time: El tiempo transcurrido desde el último frame, en segundos.
        """
        if settings.MODO_DEBUG_LOGS and settings.LOG_CATEGORIAS.get("log_gestor_estado_detalle", False): # Nueva categoría detallada
            logger_gs_detalle.debug(f"GestorEstado: Inicio actualizar_entidades_y_logica. Delta: {delta_time:.4f}s")

        # 1. Actualizar Enemigos
        if settings.MODO_DEBUG_LOGS and settings.LOG_CATEGORIAS.get("log_gestor_estado", False):
            if not self.enemigos_grupo:
                logger_gs.debug("  GestorEstado: No hay enemigos para actualizar.")
            else:
                logger_gs.debug(f"  GestorEstado: Actualizando {len(self.enemigos_grupo)} enemigos...")
        
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

        # 2. Actualizar Jugador
        # El jugador necesita los obstáculos y los enemigos para sus colisiones.
        obstaculos_para_jugador = pygame.sprite.Group(self.obstaculos_grupo.sprites(), self.enemigos_grupo.sprites())
        if settings.MODO_DEBUG_LOGS and settings.LOG_CATEGORIAS.get("log_gestor_estado", False):
            logger_gs.debug("  GestorEstado: Actualizando jugador...")
        
        # Asumimos que Jugador.update() toma (teclas, obstaculos, enemigos, ancho_mundo, alto_mundo, delta_time)
        # Jugador.update() tiene sus propios logs internos categóricos.
        if hasattr(self.jugador, 'update'):
            self.jugador.update(teclas_presionadas, obstaculos_para_jugador, self.enemigos_grupo, config.ANCHO_MUNDO, config.ALTO_MUNDO, delta_time)

        # 3. Actualizar otros sprites (ej. árboles)
        # Esto es si los sprites en `todos_los_sprites_grupo` que no son jugador ni enemigos necesitan update.
        # Por ejemplo, un árbol con animación.
        if settings.MODO_DEBUG_LOGS and settings.LOG_CATEGORIAS.get("log_gestor_estado_detalle", False):
            num_otros_sprites = 0
            if self.todos_los_sprites_grupo:
                num_otros_sprites = sum(1 for s in self.todos_los_sprites_grupo if s != self.jugador and s not in self.enemigos_grupo and hasattr(s, 'update'))
            if num_otros_sprites > 0:
                logger_gs_detalle.debug(f"  GestorEstado: Actualizando {num_otros_sprites} otros sprites (ej. Arbol)...")

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
            if settings.MODO_DEBUG_LOGS and settings.LOG_CATEGORIAS.get("log_gestor_estado", False):
                nombres_enemigos_col = [getattr(e, 'nombre_log_entidad', type(e).__name__) for e in colisiones_contacto]
                logger_gs.debug(f"  GestorEstado: Jugador colisiona por contacto con: {nombres_enemigos_col}")
            for enemigo_colisionado in colisiones_contacto:
                dano = getattr(enemigo_colisionado, 'dano_ataque', config.DANO_CONTACTO_ENEMIGO_DEFAULT)
                tipo_dano = "contacto_enemigo"
                
                # Asegurarse de que el jugador tiene el método recibir_dano
                if hasattr(self.jugador, 'recibir_dano'):
                    # self.jugador.recibir_dano tiene sus propios logs (incluyendo CMB del jugador)
                    # self.jugador.recibir_dano(dano, tipo_dano) # <--- DESCOMENTAR CUANDO SE QUIERA DAÑO
                    if settings.MODO_DEBUG_LOGS and settings.LOG_CATEGORIAS.get("log_jugador_cmb", False):
                        logger_gs.debug(f"    GestorEstado: Jugador intentaría recibir {dano} de daño por contacto de {getattr(enemigo_colisionado, 'nombre_log_entidad', type(enemigo_colisionado).__name__)}. (DAÑO DESACTIVADO TEMPORALMENTE)")
                else:
                    if settings.MODO_DEBUG_LOGS and settings.LOG_CATEGORIAS.get("log_gestor_estado", False):
                        logger_gs.error(f"  GestorEstado: Jugador no tiene método 'recibir_dano'. No se aplicó daño de {getattr(enemigo_colisionado, 'nombre_log_entidad', type(enemigo_colisionado).__name__)}.")
        
        if settings.MODO_DEBUG_LOGS and settings.LOG_CATEGORIAS.get("log_gestor_estado_detalle", False):
            logger_gs_detalle.debug("GestorEstado: Fin actualizar_entidades_y_logica.")

        # No es necesario devolver nada, las actualizaciones modifican los objetos directamente. 