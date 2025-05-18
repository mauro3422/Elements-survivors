import pygame
import os
import settings
import json
import math
import logging
from collision_handler import CollisionHandler # <--- IMPORTAR CollisionHandler

# --- Configuración del Logger ---
# Crear un logger específico para este módulo o para la depuración del movimiento
logger = logging.getLogger('movimiento_jugador')
logger.setLevel(logging.DEBUG) # Capturar todos los niveles desde DEBUG hacia arriba

# Evitar añadir múltiples handlers si el módulo se recarga o la función se llama varias veces
if not logger.handlers:
    try:
        log_file_path = os.path.join(settings.RUTA_BASE_PROYECTO, 'movimiento_debug.log')
    except AttributeError: 
        log_file_path = 'movimiento_debug.log'

    file_handler = logging.FileHandler(log_file_path, mode='w') 
    file_handler.setLevel(logging.DEBUG)
    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    stream_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)

logger.info("Logger para Jugador configurado.")
# --- Fin Configuración del Logger ---

class Jugador(pygame.sprite.Sprite):
    def __init__(self, x, y, asset_manager_instance):
        """Constructor de la clase Jugador.

        Args:
            x (int): Posición inicial en el eje X del jugador en el mundo del juego.
            y (int): Posición inicial en el eje Y del jugador en el mundo del juego.
            asset_manager_instance: Instancia de AssetManager para cargar imágenes.
        """
        super().__init__()
        self.asset_manager = asset_manager_instance
        self.animaciones = {}
        self._cargar_animaciones()

        # Variables calculadas del perfil activo (se actualizan al seleccionar perfil)
        # Se inicializan aquí ANTES de la primera llamada a seleccionar_perfil_ataque
        self.num_segmentos_barrido_activo = 0
        self.duracion_segmento_barrido_activo = 0

        # Estado inicial de la animación
        self.estado_animacion = "descanso"
        self.indice_fotograma = 0
        if self.animaciones.get(self.estado_animacion) and self.animaciones[self.estado_animacion]:
            self.image = self.animaciones[self.estado_animacion][self.indice_fotograma]
        else:
            logger.error(f"Error: Animación inicial '{self.estado_animacion}' no encontrada o vacía para el Jugador. Usando placeholder.")
            self.image = pygame.Surface((32, 32)); self.image.fill(settings.ROJO if hasattr(settings, 'ROJO') else (255,0,0))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        
        # --- Definición del Hitbox Personalizado ---
        self.hitbox_offset_x = 4
        self.hitbox_offset_y = 6
        hb_ancho = self.rect.width - (2 * self.hitbox_offset_x)
        hb_alto = self.rect.height - (self.hitbox_offset_y + 4)
        
        hb_ancho = max(1, hb_ancho)
        hb_alto = max(1, hb_alto)

        self.hitbox = pygame.Rect(0, 0, hb_ancho, hb_alto)
        self.hitbox.topleft = (self.rect.x + self.hitbox_offset_x, self.rect.y + self.hitbox_offset_y)
        
        self.velocidad = 3
        self.tiempo_ultimo_fotograma = pygame.time.get_ticks()
        self.retraso_animacion = 150 # Milisegundos entre fotogramas (ajustar según sea necesario)

        # Dirección del último movimiento (para orientar ataques, etc.)
        # (1, 0) -> Derecha; (-1, 0) -> Izquierda; (0, -1) -> Arriba; (0, 1) -> Abajo
        self.ultima_direccion_mov_x = 1 # Por defecto, mirando a la derecha
        self.ultima_direccion_mov_y = 0

        # Atributos de combate
        self.vida_maxima = 10
        self.vida_actual = self.vida_maxima
        self.ultimo_ataque_recibido = 0 # Tiempo del último golpe recibido (para cooldown)
        self.cooldown_dano = 1000 # 1 segundo de invencibilidad después de ser golpeado

        # Atributos generales de ataque (pueden ser parte del perfil también si varían mucho)
        self.dano_base_ataque = 5 # Daño que podría ser modificado por el perfil
        self.cooldown_general_ataque = 700 # Cooldown base

        # Gestión de perfiles de ataque
        self.perfiles_de_ataque = {}
        self.nombre_perfil_ataque_activo = settings.NOMBRE_PERFIL_ATAQUE_INICIAL
        self._cargar_o_crear_perfiles_ataque()

        # Asegurar que el perfil activo inicial sea válido antes de seleccionarlo
        perfil_actual_es_valido = isinstance(self.perfiles_de_ataque.get(self.nombre_perfil_ataque_activo), dict)

        if not perfil_actual_es_valido:
            logger.warning(f"Advertencia: Perfil activo inicial '{self.nombre_perfil_ataque_activo}' no es válido.")
            
            primer_perfil_valido_nombre = None
            for nombre, perfil_data in self.perfiles_de_ataque.items():
                if isinstance(perfil_data, dict):
                    primer_perfil_valido_nombre = nombre
                    break
            
            if primer_perfil_valido_nombre:
                self.nombre_perfil_ataque_activo = primer_perfil_valido_nombre
                logger.info(f"Cambiando a primer perfil válido: '{self.nombre_perfil_ataque_activo}'")
            else:
                logger.warning("No hay perfiles válidos. Forzando creación del perfil por defecto.")
                self._forzar_creacion_perfil_default_y_guardar() # Esto actualiza nombre_perfil_ataque_activo

        # Ahora seleccionamos el perfil. Esta llamada debe ser segura.
        # Las variables como duracion_segmento_barrido_activo se calculan dentro de seleccionar_perfil_ataque
        self.seleccionar_perfil_ataque(self.nombre_perfil_ataque_activo)

        # Estado del ataque actual
        self.tiempo_inicio_ataque = 0
        self.esta_atacando = False
        self.ultimo_ataque_realizado = 0
        self.enemigos_golpeados_este_ataque = set()
        self.hitbox_ataque_actual_rect = pygame.Rect(0, 0, 0, 0) # Rect del hitbox del ataque actual

    def _crear_perfil_ataque_por_defecto(self, nombre_perfil):
        return {
            "offset_distancia": 25,
            "extension": 30,
            "grosor": 15,
            "duracion_total_ms": 300,
            "plantilla_angulos_grados": [-45, -22, 0, 22, 45],
            "dano_modificador": 1.0, # Multiplicador al daño base
            "cooldown_modificador": 1.0 # Multiplicador al cooldown base
        }

    def _cargar_o_crear_perfiles_ataque(self):
        try:
            ruta_completa_config = os.path.join(settings.RUTA_BASE_PROYECTO, settings.ARCHIVO_CONFIG_ATAQUE)
            with open(ruta_completa_config, 'r') as f:
                data_cargada = json.load(f)
                if isinstance(data_cargada, dict):
                    self.perfiles_de_ataque = data_cargada
                    logger.info(f"Perfiles de ataque cargados desde {settings.ARCHIVO_CONFIG_ATAQUE}")
                    # Validar cada perfil cargado
                    for nombre_perfil, perfil_data in list(self.perfiles_de_ataque.items()): # Usar list() para poder modificar el dict
                        if not isinstance(perfil_data, dict):
                            logger.warning(f"Alerta: Perfil '{nombre_perfil}' en JSON no es un diccionario. Recreando por defecto.")
                            self.perfiles_de_ataque[nombre_perfil] = self._crear_perfil_ataque_por_defecto(nombre_perfil)
                            # Considerar guardar aquí si se repara un perfil, o al final
                else:
                    logger.warning(f"Error: '{settings.ARCHIVO_CONFIG_ATAQUE}' no contiene un diccionario de perfiles. Creando estructura por defecto.")
                    self._forzar_creacion_perfil_default_y_guardar()
        except FileNotFoundError:
            logger.warning(f"Archivo '{settings.ARCHIVO_CONFIG_ATAQUE}' no encontrado. Creando perfil por defecto.")
            self._forzar_creacion_perfil_default_y_guardar()
        except json.JSONDecodeError:
            logger.warning(f"Error JSON en '{settings.ARCHIVO_CONFIG_ATAQUE}'. Creando perfil por defecto.")
            self._forzar_creacion_perfil_default_y_guardar()
        except Exception as e:
            logger.error(f"Error cargando perfiles: {e}. Creando perfil por defecto.")
            self._forzar_creacion_perfil_default_y_guardar()

    def _forzar_creacion_perfil_default_y_guardar(self):
        self.perfiles_de_ataque = {}
        self.perfiles_de_ataque[settings.NOMBRE_PERFIL_ATAQUE_INICIAL] = self._crear_perfil_ataque_por_defecto(settings.NOMBRE_PERFIL_ATAQUE_INICIAL)
        self.nombre_perfil_ataque_activo = settings.NOMBRE_PERFIL_ATAQUE_INICIAL # Asegurar que el activo sea este
        self.guardar_todos_perfiles_ataque()

    def guardar_todos_perfiles_ataque(self):
        try:
            ruta_completa_config = os.path.join(settings.RUTA_BASE_PROYECTO, settings.ARCHIVO_CONFIG_ATAQUE)
            with open(ruta_completa_config, 'w') as f:
                json.dump(self.perfiles_de_ataque, f, indent=4)
            logger.info(f"Todos los perfiles de ataque guardados en {settings.ARCHIVO_CONFIG_ATAQUE}")
        except Exception as e:
            logger.error(f"Error al guardar todos los perfiles de ataque: {e}")

    def seleccionar_perfil_ataque(self, nombre_perfil_solicitado):
        if nombre_perfil_solicitado in self.perfiles_de_ataque and isinstance(self.perfiles_de_ataque[nombre_perfil_solicitado], dict):
            self.nombre_perfil_ataque_activo = nombre_perfil_solicitado
            perfil_activo_data = self.perfiles_de_ataque[self.nombre_perfil_ataque_activo]
            
            plantilla = perfil_activo_data.get("plantilla_angulos_grados", [0])
            if not isinstance(plantilla, list): plantilla = [0] # Fallback si la plantilla no es lista
            self.num_segmentos_barrido_activo = len(plantilla)
            
            duracion_total = perfil_activo_data.get("duracion_total_ms", 100)
            if not isinstance(duracion_total, (int, float)) or duracion_total <= 0: duracion_total = 100 # Fallback
            
            if self.num_segmentos_barrido_activo > 0 and duracion_total > 0:
                self.duracion_segmento_barrido_activo = duracion_total / self.num_segmentos_barrido_activo
            else:
                # Si no hay segmentos válidos o duración total, la duración del segmento es 0
                self.duracion_segmento_barrido_activo = 0 
            logger.info(f"Perfil activo: '{self.nombre_perfil_ataque_activo}'. Dur seg: {self.duracion_segmento_barrido_activo:.2f}ms. Num_seg: {self.num_segmentos_barrido_activo}. Dur_total: {duracion_total}")
        else:
            logger.error(f"Error: Perfil '{nombre_perfil_solicitado}' no encontrado o no es un dict. Intentando fallback.")
            
            # Estrategia de Fallback Simplificada:
            # 1. Intentar el perfil inicial por defecto (si es diferente del que falló).
            # 2. Si no, intentar el primer perfil válido encontrado (que no sea el que falló).
            # 3. Si no, forzar creación del perfil por defecto y seleccionarlo.

            nombre_perfil_default = settings.NOMBRE_PERFIL_ATAQUE_INICIAL
            
            # Intento 1: Perfil por defecto (si es diferente y válido)
            if nombre_perfil_solicitado != nombre_perfil_default and \
               isinstance(self.perfiles_de_ataque.get(nombre_perfil_default), dict):
                logger.info(f"Fallback al perfil por defecto: {nombre_perfil_default}")
                self.seleccionar_perfil_ataque(nombre_perfil_default)
                return # Salir para evitar más fallbacks en esta llamada

            # Intento 2: Primer perfil válido encontrado (diferente del que falló)
            primer_otro_perfil_valido = None
            for nombre, datos_perfil in self.perfiles_de_ataque.items():
                if isinstance(datos_perfil, dict) and nombre != nombre_perfil_solicitado:
                    primer_otro_perfil_valido = nombre
                    break
            
            if primer_otro_perfil_valido:
                logger.info(f"Fallback al primer otro perfil válido encontrado: {primer_otro_perfil_valido}")
                self.seleccionar_perfil_ataque(primer_otro_perfil_valido)
                return # Salir

            # Intento 3: Forzar creación y selección del perfil por defecto
            # Esto ocurre si el perfil solicitado era el default y falló, o no hay otros perfiles válidos.
            logger.warning("Forzando recreación del perfil por defecto y seleccionándolo.")
            self._forzar_creacion_perfil_default_y_guardar() # Esto actualiza nombre_perfil_ataque_activo
            # Después de forzar la creación, el perfil activo debería ser el default.
            # Seleccionarlo explícitamente para asegurar que todo se actualice.
            if isinstance(self.perfiles_de_ataque.get(self.nombre_perfil_ataque_activo), dict):
                 self.seleccionar_perfil_ataque(self.nombre_perfil_ataque_activo)
            else:
                 logger.critical(f"CRÍTICO: No se pudo seleccionar un perfil válido incluso después de forzar la creación.")
                 # Aquí podría ser necesario un estado de "error irrecuperable" o usar valores hardcodeados mínimos.
                 # Por ahora, las variables de duración de segmento serán 0.

    def get_parametro_ataque_activo(self, nombre_parametro, valor_defecto=None):
        perfil = self.perfiles_de_ataque.get(self.nombre_perfil_ataque_activo)
        if isinstance(perfil, dict):
            return perfil.get(nombre_parametro, valor_defecto)
        # print(f"Advertencia (get_parametro): Perfil activo '{self.nombre_perfil_ataque_activo}' no es un dict o no existe.")
        return valor_defecto

    def set_parametro_ataque_activo(self, nombre_parametro, valor):
        perfil = self.perfiles_de_ataque.get(self.nombre_perfil_ataque_activo)
        if isinstance(perfil, dict):
            perfil[nombre_parametro] = valor
            if nombre_parametro == "duracion_total_ms" or nombre_parametro == "plantilla_angulos_grados":
                # Re-seleccionar para actualizar num_segmentos y duracion_segmento
                self.seleccionar_perfil_ataque(self.nombre_perfil_ataque_activo)
        else:
            logger.warning(f"Advertencia (set_parametro): No se pudo setear '{nombre_parametro}' en perfil '{self.nombre_perfil_ataque_activo}'.")

    # --- Métodos para ajustar parámetros del PERFIL ACTIVO en tiempo real ---
    def modificar_ataque_offset(self, cantidad):
        actual = self.get_parametro_ataque_activo("offset_distancia", 0)
        nuevo = max(0, actual + cantidad)
        self.set_parametro_ataque_activo("offset_distancia", nuevo)
        logger.debug(f"Perfil '{self.nombre_perfil_ataque_activo}' - offset_distancia: {nuevo}")

    def modificar_ataque_extension(self, cantidad):
        actual = self.get_parametro_ataque_activo("extension", 1)
        nuevo = max(1, actual + cantidad)
        self.set_parametro_ataque_activo("extension", nuevo)
        logger.debug(f"Perfil '{self.nombre_perfil_ataque_activo}' - extension: {nuevo}")

    def modificar_ataque_grosor(self, cantidad):
        actual = self.get_parametro_ataque_activo("grosor", 1)
        nuevo = max(1, actual + cantidad)
        self.set_parametro_ataque_activo("grosor", nuevo)
        logger.debug(f"Perfil '{self.nombre_perfil_ataque_activo}' - grosor: {nuevo}")

    def modificar_duracion_ataque_total(self, cantidad):
        actual = self.get_parametro_ataque_activo("duracion_total_ms", 50)
        nuevo = max(50, actual + cantidad)
        self.set_parametro_ataque_activo("duracion_total_ms", nuevo) # Esto llama a seleccionar_perfil_ataque para recalcular
        logger.debug(f"Perfil '{self.nombre_perfil_ataque_activo}' - duracion_total_ms: {nuevo}, seg_dur: {self.duracion_segmento_barrido_activo:.2f}")

    def _cargar_animaciones(self):
        """Carga los fotogramas para las animaciones del jugador usando AssetManager."""
        self.animaciones["descanso"] = []
        for i in range(1, 5): # Asumiendo player_reposo_1 a player_reposo_4
            clave_asset = f"player_reposo_{i}"
            imagen = self.asset_manager.get_image(clave_asset)
            # get_image ya devuelve un placeholder si falla, así que no necesitamos más fallbacks aquí
            # a menos que queramos un comportamiento específico si una animación está incompleta.
            if imagen:
                 self.animaciones["descanso"].append(imagen)
            else:
                logger.warning(f"No se pudo obtener la imagen '{clave_asset}' para la animación de descanso del jugador.")
                # Podríamos añadir un placeholder específico para animación aquí si es necesario
                # o simplemente la animación tendrá menos fotogramas.
        
        if not self.animaciones["descanso"]:
            logger.critical("CRITICAL: No se cargaron fotogramas para la animación de descanso del Jugador DESDE ASSET MANAGER.")
            # Crear un placeholder si la lista está completamente vacía.
            placeholder_img = pygame.Surface((32,32)); placeholder_img.fill(settings.ROJO if hasattr(settings, 'ROJO') else (255,0,0))
            self.animaciones["descanso"] = [placeholder_img]
        
        # Ejemplo para futuras animaciones:
        # self.animaciones["corriendo"] = []
        # for i in range(1, 7):
        #     clave_asset = f"player_corriendo_{i}"
        #     self.animaciones["corriendo"].append(self.asset_manager.get_image(clave_asset))

    def actualizar_animacion(self):
        """Actualiza el fotograma actual de la animación del jugador basado en el tiempo.
        Se llama en cada fotograma del bucle principal del juego.
        """
        ahora = pygame.time.get_ticks()
        if ahora - self.tiempo_ultimo_fotograma > self.retraso_animacion:
            self.tiempo_ultimo_fotograma = ahora
            if self.estado_animacion in self.animaciones and self.animaciones[self.estado_animacion]:
                 self.indice_fotograma = (self.indice_fotograma + 1) % len(self.animaciones[self.estado_animacion])
                 self.image = self.animaciones[self.estado_animacion][self.indice_fotograma]
            else:
                logger.warning(f"Estado de animación '{self.estado_animacion}' no encontrado o vacío en Jugador. No se actualizó la imagen.")

    def _actualizar_posicion_hitbox(self):
        self.hitbox.topleft = (self.rect.x + self.hitbox_offset_x, self.rect.y + self.hitbox_offset_y)

    def _mover_y_colisionar(self, dx, dy, obstaculos):
        CollisionHandler.gestionar_movimiento_y_colision(
            self.hitbox, 
            self.rect, 
            self.hitbox_offset_x, 
            self.hitbox_offset_y, 
            dx, 
            dy, 
            obstaculos, 
            logger 
        )

    def actualizar_movimiento(self, teclas_presionadas, obstaculos):
        """Actualiza la posición del jugador basándose en las teclas presionadas.
        Se llama en cada fotograma del bucle principal.

        Args:
            teclas_presionadas: Un diccionario o secuencia de booleanos de pygame.key.get_pressed()
                    que indica el estado de todas las teclas.
        """
        mov_x_final = 0
        mov_y_final = 0

        if teclas_presionadas[pygame.K_LEFT] or teclas_presionadas[pygame.K_a]:
            mov_x_final = -self.velocidad
        if teclas_presionadas[pygame.K_RIGHT] or teclas_presionadas[pygame.K_d]:
            mov_x_final = self.velocidad
        if teclas_presionadas[pygame.K_UP] or teclas_presionadas[pygame.K_w]:
            mov_y_final = -self.velocidad
        if teclas_presionadas[pygame.K_DOWN] or teclas_presionadas[pygame.K_s]:
            mov_y_final = self.velocidad
        
        logger.debug(f"[actualizar_movimiento] Input: mov_x={mov_x_final}, mov_y={mov_y_final}")
        
        if mov_x_final != 0 or mov_y_final != 0:
            if mov_x_final != 0:
                self.ultima_direccion_mov_x = int(mov_x_final / self.velocidad)
                self.ultima_direccion_mov_y = 0
            elif mov_y_final != 0:
                self.ultima_direccion_mov_x = 0
                self.ultima_direccion_mov_y = int(mov_y_final / self.velocidad)
            
            self._mover_y_colisionar(mov_x_final, mov_y_final, obstaculos)
        # No es necesario _actualizar_posicion_hitbox() aquí porque _mover_y_colisionar 
        # (a través de CollisionHandler) ya opera sobre self.hitbox y self.rect está sincronizado.

    def dibujar(self, superficie):
        """Dibuja el sprite actual del jugador en la superficie dada.
        Nota: Con el sistema de cámara, este método se vuelve menos relevante si la cámara
        dibuja directamente el jugador.image. Sin embargo, es una buena práctica tenerlo.

        Args:
            superficie (pygame.Surface): La superficie donde se dibujará el jugador.
        """
        superficie.blit(self.image, self.rect)
        # Opcional: Dibujar el hitbox para depuración
        # if settings.DEBUG_VER_HITBOXES:
        #     pygame.draw.rect(superficie, (255,0,0), self.hitbox, 1)

    def recibir_dano(self, cantidad):
        ahora = pygame.time.get_ticks()
        if ahora - self.ultimo_ataque_recibido > self.cooldown_dano:
            self.vida_actual -= cantidad
            self.ultimo_ataque_recibido = ahora
            logger.info(f"Jugador recibe {cantidad} de daño. Vida restante: {self.vida_actual}")
            if self.vida_actual <= 0:
                self.morir()
        # else: print("Jugador en cooldown, daño ignorado") # Para depuración

    def morir(self):
        logger.info("Jugador ha muerto!")
        # Por ahora, solo un print. Podríamos hacer que el juego termine, reiniciar, etc.
        # self.kill() # Si quisiéramos que el sprite del jugador desaparezca (podría no ser deseable)
        # O cambiar su estado a "muerto" para una animación de muerte, etc.
        pass 

    def atacar(self, grupo_enemigos):
        ahora = pygame.time.get_ticks()
        cooldown_ataque_actual = self.cooldown_general_ataque * self.get_parametro_ataque_activo("cooldown_modificador", 1.0)
        if ahora - self.ultimo_ataque_realizado > cooldown_ataque_actual:
            if not self.esta_atacando:
                self.esta_atacando = True
                self.tiempo_inicio_ataque = ahora
                self.ultimo_ataque_realizado = ahora
                self.enemigos_golpeados_este_ataque.clear()
                logger.info(f"Jugador inicia ataque con perfil '{self.nombre_perfil_ataque_activo}'!")

    def actualizar_ataque(self, enemigos):
        if not self.esta_atacando:
            self.hitbox_ataque_actual_rect.size = (0,0) 
            return

        offset_dist = self.get_parametro_ataque_activo("offset_distancia", 25)
        extension = self.get_parametro_ataque_activo("extension", 30)
        grosor = self.get_parametro_ataque_activo("grosor", 15)
        duracion_total_ms = self.get_parametro_ataque_activo("duracion_total_ms", 300)
        plantilla_angulos = self.get_parametro_ataque_activo("plantilla_angulos_grados", [0])
        dano_actual = self.dano_base_ataque * self.get_parametro_ataque_activo("dano_modificador", 1.0)
        
        num_segmentos = self.num_segmentos_barrido_activo
        dur_segmento = self.duracion_segmento_barrido_activo

        # logger.debug(f"DEBUG actualizar_ataque: perfil='{self.nombre_perfil_ataque_activo}', atacando={self.esta_atacando}, num_seg={num_segmentos}, dur_seg={dur_segmento:.2f}")

        ahora = pygame.time.get_ticks()
        tiempo_transcurrido_ataque = ahora - self.tiempo_inicio_ataque

        if tiempo_transcurrido_ataque <= duracion_total_ms and num_segmentos > 0 and dur_segmento > 0:
            segmento_actual_indice = int(tiempo_transcurrido_ataque / dur_segmento)
            segmento_actual_indice = min(segmento_actual_indice, num_segmentos - 1)
            
            angulo_offset_grados = plantilla_angulos[segmento_actual_indice]
            ataque_es_principalmente_horizontal = (self.ultima_direccion_mov_x != 0)
            angulo_base_direccion_grados = 0
            if ataque_es_principalmente_horizontal:
                if self.ultima_direccion_mov_x > 0: angulo_base_direccion_grados = 0
                else: angulo_base_direccion_grados = 180
            else: 
                if self.ultima_direccion_mov_y < 0: angulo_base_direccion_grados = -90
                else: angulo_base_direccion_grados = 90
            
            angulo_total_segmento_grados = angulo_base_direccion_grados + angulo_offset_grados
            angulo_total_segmento_rad = math.radians(angulo_total_segmento_grados)

            centro_segmento_x = self.rect.centerx + offset_dist * math.cos(angulo_total_segmento_rad)
            centro_segmento_y = self.rect.centery + offset_dist * math.sin(angulo_total_segmento_rad)
            
            cos_abs = abs(math.cos(angulo_total_segmento_rad))
            sin_abs = abs(math.sin(angulo_total_segmento_rad))
            epsilon = 0.0001
            final_ancho, final_alto = 0,0

            if ataque_es_principalmente_horizontal:
                if cos_abs >= sin_abs - epsilon:
                    final_ancho = extension; final_alto = grosor
                else: 
                    final_ancho = grosor; final_alto = extension
            else: 
                if sin_abs >= cos_abs - epsilon:
                    final_ancho = grosor; final_alto = extension
                else: 
                    final_ancho = extension; final_alto = grosor
            
            self.hitbox_ataque_actual_rect.width = final_ancho
            self.hitbox_ataque_actual_rect.height = final_alto
            self.hitbox_ataque_actual_rect.center = (int(centro_segmento_x), int(centro_segmento_y))

            for enemigo in enemigos:
                if enemigo not in self.enemigos_golpeados_este_ataque:
                    if self.hitbox_ataque_actual_rect.colliderect(enemigo.hitbox):
                        # logger.debug(f"ATAQUE '{self.nombre_perfil_ataque_activo}' (seg {segmento_actual_indice}) golpea enemigo")
                        enemigo.recibir_dano(dano_actual)
                        self.enemigos_golpeados_este_ataque.add(enemigo)
        else:
            self.esta_atacando = False
            self.hitbox_ataque_actual_rect.size = (0,0)