import pygame
import settings
import logging
import os

# Unificar loggers
logger = logging.getLogger("entidad_base")

class EntidadBase(pygame.sprite.Sprite):
    """Clase base para entidades del juego como Jugador y Enemigo."""
    id_counter = 0 # Contador de clase para ID único opcional

    def __init__(self, x, y, asset_manager_instance,
                 vida_maxima, velocidad,
                 hitbox_offset_x, hitbox_offset_y, 
                 nombre_asset_imagen_inicial=None, # Clave para una imagen estática inicial
                 dict_animaciones_config=None, # Opcional: {nombre_anim: {claves_assets: [c1,c2], retraso: ms}}
                 estado_anim_inicial="idle",
                 nombre_entidad_tipo="EntidadDesconocida"):
        super().__init__()
        
        self.id_entidad = EntidadBase.id_counter
        EntidadBase.id_counter += 1
        self.nombre_entidad_tipo = nombre_entidad_tipo
        self.nombre_log_entidad = f"[{self.nombre_entidad_tipo}_{self.id_entidad}]"

        log_msg_creacion = f"{self.nombre_log_entidad} Creando en ({x}, {y})"
        if settings.MODO_DEBUG_LOGS and settings.LOG_CATEGORIAS.get("log_entidad_base", False):
            # logging.getLogger("log_general").info(log_msg_creacion) # Usa el logger global para creación
            logger.info(log_msg_creacion, extra={"categoria_log": "log_entidad_base"})
        elif not settings.MODO_DEBUG_LOGS: # Loguear siempre la creación si no estamos en modo debug verboso, pero con nivel INFO
             # logging.getLogger("log_general").info(log_msg_creacion)
             logger.info(log_msg_creacion, extra={"categoria_log": "log_entidad_base"})

        self.asset_manager = asset_manager_instance
        self.animaciones = {}
        self.estado_animacion = estado_anim_inicial
        self.indice_fotograma = 0
        self.tiempo_ultimo_fotograma = pygame.time.get_ticks()
        self.retraso_animacion = 150 # Valor por defecto, puede ser sobrescrito por dict_animaciones_config
        self.ha_muerto = False # Atributo para rastrear si la entidad ha muerto

        if dict_animaciones_config:
            self._cargar_animaciones_desde_config(dict_animaciones_config)
        elif nombre_asset_imagen_inicial:
            self.image = self.asset_manager.get_image(nombre_asset_imagen_inicial)
            if settings.MODO_DEBUG_LOGS and settings.LOG_CATEGORIAS.get("log_assets", False):
                # logger_assets_entidad.debug(f"{self.nombre_log_entidad} Imagen estática '{nombre_asset_imagen_inicial}' asignada.")
                logger.debug(f"{self.nombre_log_entidad} Imagen estática '{nombre_asset_imagen_inicial}' asignada.", extra={"categoria_log": "log_assets"})
        else:
            # logger_entidad_gen.warning(f"{self.nombre_log_entidad} Sin imagen inicial ni config de animación. Usando placeholder.")
            logger.warning(f"{self.nombre_log_entidad} Sin imagen inicial ni config de animación. Usando placeholder.", extra={"categoria_log": "log_entidad_base"})
            self.image = pygame.Surface((32, 32))
            self.image.fill(settings.ROJO_ERROR_ASSET if hasattr(settings, 'ROJO_ERROR_ASSET') else (255, 0, 0))

        if self.animaciones.get(self.estado_animacion) and self.animaciones[self.estado_animacion]:
            self.image = self.animaciones[self.estado_animacion][self.indice_fotograma]
            if settings.MODO_DEBUG_LOGS and settings.LOG_CATEGORIAS.get("log_animacion", False):
                 # logger_anim.debug(f"{self.nombre_log_entidad} Imagen inicial asignada desde animación '{self.estado_animacion}', frame {self.indice_fotograma}")
                 logger.debug(f"{self.nombre_log_entidad} Imagen inicial asignada desde animación '{self.estado_animacion}', frame {self.indice_fotograma}", extra={"categoria_log": "log_animacion"})
        elif not hasattr(self, 'image') or self.image is None: 
            # logger_entidad_gen.error(f"{self.nombre_log_entidad} Imagen no asignada después de init de assets/anim. Usando placeholder final.")
            logger.error(f"{self.nombre_log_entidad} Imagen no asignada después de init de assets/anim. Usando placeholder final.", extra={"categoria_log": "log_entidad_base"})
            self.image = pygame.Surface((32, 32)); self.image.fill((255,0,0))
        
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)

        # Atributos comunes
        self.vida_maxima = vida_maxima
        self.vida_actual = vida_maxima
        self.velocidad = velocidad

        # Hitbox
        self.hitbox_offset_x = hitbox_offset_x
        self.hitbox_offset_y = hitbox_offset_y
        # Los tamaños del hitbox pueden depender del tamaño de self.image, así que se calculan después
        hb_ancho = self.rect.width - (2 * self.hitbox_offset_x)
        hb_alto = self.rect.height - (2 * self.hitbox_offset_y) # Ajustar según la entidad específica si es necesario
        hb_ancho = max(1, hb_ancho)
        hb_alto = max(1, hb_alto)
        self.hitbox = pygame.Rect(0, 0, hb_ancho, hb_alto)
        self._actualizar_posicion_hitbox() # Posicionar hitbox inicial
        if settings.MODO_DEBUG_LOGS and settings.LOG_CATEGORIAS.get("log_entidad_base", False): # O una categoría "log_entidad_init"
            # logging.getLogger("log_general").debug(f"{self.nombre_log_entidad} Hitbox inicial: {self.hitbox} en {self.hitbox.topleft}")
            logger.debug(f"{self.nombre_log_entidad} Hitbox inicial: {self.hitbox} en {self.hitbox.topleft}", extra={"categoria_log": "log_entidad_base"})

        self.ultimo_ataque_recibido = 0 # Tiempo del último golpe recibido (para cooldown de invencibilidad)
        self.cooldown_dano_general = 1000 # Cooldown de invencibilidad general, puede ser ajustado por subclase

    def _cargar_animaciones_desde_config(self, dict_animaciones_config):
        """Carga animaciones basadas en un diccionario de configuración.
           Ejemplo de dict_animaciones_config:
           {
               "idle": {"claves_assets": ["player_reposo_1", "player_reposo_2"], "retraso": 150},
               "corriendo": {"claves_assets": ["player_run_1", "player_run_2"], "retraso": 100}
           }
        """
        if settings.MODO_DEBUG_LOGS and settings.LOG_CATEGORIAS.get("log_assets", False):
            # logger_assets_entidad.debug(f"{self.nombre_log_entidad} Iniciando carga de animaciones con config: {dict_animaciones_config}")
            logger.debug(f"{self.nombre_log_entidad} Iniciando carga de animaciones con config: {dict_animaciones_config}", extra={"categoria_log": "log_assets"})

        for nombre_anim, config_anim in dict_animaciones_config.items():
            self.animaciones[nombre_anim] = []
            if not config_anim.get("claves_assets"):
                # logger_entidad_gen.warning(f"{self.nombre_log_entidad} Animación '{nombre_anim}' sin 'claves_assets'. Saltando.")
                logger.warning(f"{self.nombre_log_entidad} Animación '{nombre_anim}' sin 'claves_assets'. Saltando.", extra={"categoria_log": "log_entidad_base"})
                continue

            if settings.MODO_DEBUG_LOGS and settings.LOG_CATEGORIAS.get("log_assets", False):
                # logger_assets_entidad.debug(f"{self.nombre_log_entidad} Cargando assets para '{nombre_anim}': {config_anim['claves_assets']}")
                logger.debug(f"{self.nombre_log_entidad} Cargando assets para '{nombre_anim}': {config_anim['claves_assets']}", extra={"categoria_log": "log_assets"})

            for clave_asset in config_anim["claves_assets"]:
                imagen = self.asset_manager.get_image(clave_asset) # AssetManager se encargará de sus propios logs detallados
                self.animaciones[nombre_anim].append(imagen)
            
            if not self.animaciones[nombre_anim] or all(img is self.asset_manager.placeholder_surface for img in self.animaciones[nombre_anim]):
                # logger_entidad_gen.warning(f"{self.nombre_log_entidad} Para anim '{nombre_anim}', no se cargaron frames válidos o solo placeholders.")
                logger.warning(f"{self.nombre_log_entidad} Para anim '{nombre_anim}', no se cargaron frames válidos o solo placeholders.", extra={"categoria_log": "log_entidad_base"})
                self.animaciones[nombre_anim] = [self.asset_manager.placeholder_surface]
            
            if nombre_anim == self.estado_animacion and "retraso" in config_anim:
                self.retraso_animacion = config_anim["retraso"]
                if settings.MODO_DEBUG_LOGS and settings.LOG_CATEGORIAS.get("log_animacion", False):
                    # logger_anim.debug(f"{self.nombre_log_entidad} Anim inicial '{nombre_anim}': retraso {self.retraso_animacion}ms.")
                    logger.debug(f"{self.nombre_log_entidad} Anim inicial '{nombre_anim}': retraso {self.retraso_animacion}ms.", extra={"categoria_log": "log_animacion"})

    def _actualizar_posicion_hitbox(self):
        """Actualiza la posición del hitbox basándose en la posición del rect principal y los offsets.
           Las subclases pueden necesitar sobreescribir esto si su hitbox se calcula diferente (ej. centrado).
        """
        self.hitbox.topleft = (self.rect.x + self.hitbox_offset_x, 
                               self.rect.y + self.hitbox_offset_y)
    
    def _actualizar_posicion_rect_desde_hitbox(self):
        """Actualiza la posición del rect principal basándose en la posición del hitbox y los offsets."""
        self.rect.topleft = (self.hitbox.x - self.hitbox_offset_x,
                             self.hitbox.y - self.hitbox_offset_y)

    def actualizar_animacion(self):
        """Actualiza el fotograma actual de la animación de la entidad basado en el tiempo."""
        if not self.animaciones or not self.estado_animacion in self.animaciones or not self.animaciones[self.estado_animacion]:
            if settings.MODO_DEBUG_LOGS and settings.LOG_CATEGORIAS.get("log_animacion", False):
                # logger_anim.debug(f"{self.nombre_log_entidad} No hay animación '{self.estado_animacion}' o está vacía. Saltando act. animación.")
                logger.debug(f"{self.nombre_log_entidad} No hay animación '{self.estado_animacion}' o está vacía. Saltando act. animación.", extra={"categoria_log": "log_animacion"})
            return

        ahora = pygame.time.get_ticks()
        if ahora - self.tiempo_ultimo_fotograma > self.retraso_animacion:
            self.tiempo_ultimo_fotograma = ahora
            self.indice_fotograma = (self.indice_fotograma + 1) % len(self.animaciones[self.estado_animacion])
            self.image = self.animaciones[self.estado_animacion][self.indice_fotograma]
            
            if settings.MODO_DEBUG_LOGS and settings.LOG_CATEGORIAS.get("log_animacion", False):
                # logger_anim.debug(f"{self.nombre_log_entidad} Anim '{self.estado_animacion}': Frame -> {self.indice_fotograma}/{len(self.animaciones[self.estado_animacion])-1}. Retraso: {self.retraso_animacion}ms")
                logger.debug(f"{self.nombre_log_entidad} Anim '{self.estado_animacion}': Frame -> {self.indice_fotograma}/{len(self.animaciones[self.estado_animacion])-1}. Retraso: {self.retraso_animacion}ms", extra={"categoria_log": "log_animacion"})

    def recibir_dano(self, cantidad, tipo_dano="generico"):
        """Procesa el daño recibido por la entidad."""
        # Determinar la categoría de log de combate correcta (jugador o enemigo)
        categoria_combate_log = "log_general" # Fallback
        if "Jugador" in self.nombre_entidad_tipo:
            categoria_combate_log = "log_jugador_cmb"
        elif "Enemigo" in self.nombre_entidad_tipo:
            categoria_combate_log = "log_enemigo_cmb"

        if self.ha_muerto: 
            if settings.MODO_DEBUG_LOGS and settings.LOG_CATEGORIAS.get(categoria_combate_log, False):
                 # logging.getLogger(categoria_combate_log).debug(f"{self.nombre_log_entidad} Ya está muerto. Daño de {cantidad} ({tipo_dano}) ignorado.")
                 logger.debug(f"{self.nombre_log_entidad} Ya está muerto. Daño de {cantidad} ({tipo_dano}) ignorado.", extra={"categoria_log": categoria_combate_log})
            return False 

        ahora = pygame.time.get_ticks()
        if hasattr(self, 'cooldown_dano_general') and (ahora - self.ultimo_ataque_recibido < self.cooldown_dano_general):
            if settings.MODO_DEBUG_LOGS and settings.LOG_CATEGORIAS.get(categoria_combate_log, False):
                # logging.getLogger(categoria_combate_log).debug(f"{self.nombre_log_entidad} En cooldown de daño ({self.cooldown_dano_general}ms), daño ignorado. Ahora: {ahora}, Ultimo: {self.ultimo_ataque_recibido}")
                logger.debug(f"{self.nombre_log_entidad} En cooldown de daño ({self.cooldown_dano_general}ms), daño ignorado. Ahora: {ahora}, Ultimo: {self.ultimo_ataque_recibido}", extra={"categoria_log": categoria_combate_log})
            return False

        self.vida_actual -= cantidad
        self.ultimo_ataque_recibido = ahora
        
        # Log INFO del daño siempre se hace, pero el logger específico depende del tipo de entidad.
        # logger_especifico_info = logging.getLogger(categoria_combate_log) if categoria_combate_log != "log_general" else logger_entidad_gen
        # logger_especifico_info.info(f"{self.nombre_log_entidad} Recibe {cantidad} de daño ({tipo_dano}). Vida: {self.vida_actual}/{self.vida_maxima}")
        logger.info(f"{self.nombre_log_entidad} Recibe {cantidad} de daño ({tipo_dano}). Vida: {self.vida_actual}/{self.vida_maxima}", extra={"categoria_log": categoria_combate_log})
        
        if settings.MODO_DEBUG_LOGS and settings.LOG_CATEGORIAS.get(categoria_combate_log, False):
            # logging.getLogger(categoria_combate_log).debug(f"{self.nombre_log_entidad} Detalle daño: Antes: {self.vida_actual + cantidad}, Recibido: {cantidad}, Ahora: {self.vida_actual}")
            logger.debug(f"{self.nombre_log_entidad} Detalle daño: Antes: {self.vida_actual + cantidad}, Recibido: {cantidad}, Ahora: {self.vida_actual}", extra={"categoria_log": categoria_combate_log})
        
        if self.vida_actual <= 0:
            self.vida_actual = 0
            self.morir()
        return True

    def morir(self):
        """Maneja la muerte de la entidad."""
        if self.ha_muerto: 
            return
        self.ha_muerto = True
        
        categoria_combate_log = "log_general" # Fallback si no es Jugador ni Enemigo
        if "Jugador" in self.nombre_entidad_tipo:
            categoria_combate_log = "log_jugador_cmb"
        elif "Enemigo" in self.nombre_entidad_tipo:
            categoria_combate_log = "log_enemigo_cmb"
            
        # logger_especifico_info = logging.getLogger(categoria_combate_log) if categoria_combate_log != "log_general" else logger_entidad_gen
        # logger_especifico_info.info(f"{self.nombre_log_entidad} Ha MUERTO en {self.rect.topleft}!")
        logger.info(f"{self.nombre_log_entidad} Ha MUERTO en {self.rect.topleft}!", extra={"categoria_log": categoria_combate_log})
        
        if settings.MODO_DEBUG_LOGS and settings.LOG_CATEGORIAS.get(categoria_combate_log, False):
            # logging.getLogger(categoria_combate_log).debug(f"{self.nombre_log_entidad} Método morir() llamado. Sprite será eliminado.")
            logger.debug(f"{self.nombre_log_entidad} Método morir() llamado. Sprite será eliminado.", extra={"categoria_log": categoria_combate_log})
        self.kill()

    def update(self, *args, **kwargs):
        """Método de actualización base. Las subclases deben extender esto.
           Llama a actualizar_animacion por defecto.
        """
        self.actualizar_animacion() # Ya tiene sus propios logs de animación internos
        # Lógica de movimiento, IA, colisiones, etc., irá en las subclases.

    # --- Métodos que las subclases probablemente implementarán o extenderán ---
    # def _cargar_animaciones_especificas(self): # Las subclases definirán cómo cargar sus animaciones
    #     pass

    # def _manejar_movimiento_y_colisiones(self, dx, dy, obstaculos): # Lógica de movimiento
    #     pass 