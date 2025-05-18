import pygame
import settings
import logging
import os

logger = logging.getLogger(__name__) # Logger para este módulo

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
        logger.info(f"Creando {self.nombre_entidad_tipo} ID: {self.id_entidad} en ({x}, {y})")

        self.asset_manager = asset_manager_instance
        self.animaciones = {}
        self.estado_animacion = estado_anim_inicial
        self.indice_fotograma = 0
        self.tiempo_ultimo_fotograma = pygame.time.get_ticks()
        self.retraso_animacion = 150 # Valor por defecto, puede ser sobrescrito por dict_animaciones_config

        if dict_animaciones_config:
            self._cargar_animaciones_desde_config(dict_animaciones_config)
        elif nombre_asset_imagen_inicial:
            # Si solo se provee una imagen estática inicial
            self.image = self.asset_manager.get_image(nombre_asset_imagen_inicial)
        else:
            # Fallback a un placeholder si no hay imagen ni animación definida
            logger.warning(f"{self.nombre_entidad_tipo} ID: {self.id_entidad} - No se proporcionó imagen inicial ni config de animación. Usando placeholder.")
            self.image = pygame.Surface((32, 32))
            self.image.fill(settings.ROJO_ERROR_ASSET if hasattr(settings, 'ROJO_ERROR_ASSET') else (255, 0, 0))

        # Configurar imagen inicial si se cargaron animaciones
        if self.animaciones.get(self.estado_animacion) and self.animaciones[self.estado_animacion]:
            self.image = self.animaciones[self.estado_animacion][self.indice_fotograma]
        elif not hasattr(self, 'image'): # Si no se cargó ni estática ni de animación
            logger.error(f"{self.nombre_entidad_tipo} ID: {self.id_entidad} - Fallo crítico al cargar imagen/animación. Usando placeholder final.")
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
        for nombre_anim, config_anim in dict_animaciones_config.items():
            self.animaciones[nombre_anim] = []
            if not config_anim.get("claves_assets"):
                logger.warning(f"{self.nombre_entidad_tipo} ID: {self.id_entidad} - Config de animación '{nombre_anim}' no tiene 'claves_assets'. Saltando.")
                continue

            for clave_asset in config_anim["claves_assets"]:
                imagen = self.asset_manager.get_image(clave_asset)
                self.animaciones[nombre_anim].append(imagen)
            
            if not self.animaciones[nombre_anim] or all(img.get_width() == 32 and img.get_height() == 32 for img in self.animaciones[nombre_anim]): # Heurística placeholder
                logger.warning(f"{self.nombre_entidad_tipo} ID: {self.id_entidad} - No se cargaron fotogramas válidos para '{nombre_anim}' o solo placeholders.")
                if not self.animaciones[nombre_anim]: # Si está completamente vacío
                    ph = pygame.Surface((32,32)); ph.fill(settings.ROJO_ERROR_ASSET if hasattr(settings, 'ROJO_ERROR_ASSET') else (255,0,0))
                    self.animaciones[nombre_anim] = [ph]
            
            # Si este es el estado de animación inicial, actualizar el retraso de animación de la entidad
            if nombre_anim == self.estado_animacion and "retraso" in config_anim:
                self.retraso_animacion = config_anim["retraso"]

    def _actualizar_posicion_hitbox(self):
        """Actualiza la posición del hitbox basándose en la posición del rect principal y los offsets.
           Las subclases pueden necesitar sobreescribir esto si su hitbox se calcula diferente (ej. centrado).
        """
        self.hitbox.topleft = (self.rect.x + self.hitbox_offset_x, 
                               self.rect.y + self.hitbox_offset_y)
    
    def actualizar_animacion(self):
        """Actualiza el fotograma actual de la animación de la entidad basado en el tiempo."""
        if not self.animaciones or not self.estado_animacion in self.animaciones or not self.animaciones[self.estado_animacion]:
            # logger.debug(f"{self.nombre_entidad_tipo} ID: {self.id_entidad} - No hay animación '{self.estado_animacion}' o está vacía.")
            return

        ahora = pygame.time.get_ticks()
        if ahora - self.tiempo_ultimo_fotograma > self.retraso_animacion:
            self.tiempo_ultimo_fotograma = ahora
            self.indice_fotograma = (self.indice_fotograma + 1) % len(self.animaciones[self.estado_animacion])
            self.image = self.animaciones[self.estado_animacion][self.indice_fotograma]
            # Importante: Si las imágenes de la animación tienen diferentes tamaños,
            # el rect y el hitbox podrían necesitar re-calcularse o ajustarse aquí.
            # Por ahora, asumimos que todas las imágenes de una animación tienen el mismo tamaño.
            # Si no, se necesitaría algo como:
            # old_center = self.rect.center
            # self.image = self.animaciones[self.estado_animacion][self.indice_fotograma]
            # self.rect = self.image.get_rect(center=old_center)
            # self._actualizar_posicion_hitbox() # Si el tamaño del sprite cambia

    def recibir_dano(self, cantidad, tipo_dano="generico"):
        """Procesa el daño recibido por la entidad."""
        ahora = pygame.time.get_ticks()
        # Aplicar cooldown de invencibilidad si se define uno para la entidad
        if hasattr(self, 'cooldown_dano_general') and (ahora - self.ultimo_ataque_recibido < self.cooldown_dano_general):
            # logger.debug(f"{self.nombre_entidad_tipo} ID: {self.id_entidad} en cooldown, daño ignorado.")
            return False # No se aplicó daño

        self.vida_actual -= cantidad
        self.ultimo_ataque_recibido = ahora
        logger.info(f"{self.nombre_entidad_tipo} ID: {self.id_entidad} recibe {cantidad} de daño ({tipo_dano}). Vida: {self.vida_actual}/{self.vida_maxima}")
        
        if self.vida_actual <= 0:
            self.vida_actual = 0
            self.morir()
        return True # Se aplicó daño

    def morir(self):
        """Maneja la muerte de la entidad."""
        logger.info(f"{self.nombre_entidad_tipo} ID: {self.id_entidad} ha muerto en {self.rect.topleft}!")
        self.kill() # Elimina el sprite de todos los grupos a los que pertenece

    def update(self, *args, **kwargs):
        """Método de actualización base. Las subclases deben extender esto.
           Llama a actualizar_animacion por defecto.
        """
        self.actualizar_animacion()
        # Lógica de movimiento, IA, colisiones, etc., irá en las subclases.

    # --- Métodos que las subclases probablemente implementarán o extenderán ---
    # def _cargar_animaciones_especificas(self): # Las subclases definirán cómo cargar sus animaciones
    #     pass

    # def _manejar_movimiento_y_colisiones(self, dx, dy, obstaculos): # Lógica de movimiento
    #     pass 