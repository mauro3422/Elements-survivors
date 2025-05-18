import pygame
import os
import settings
import json
import math # <--- Importar math

class Jugador(pygame.sprite.Sprite):
    def __init__(self, x, y, ruta_assets):
        """Constructor de la clase Jugador.

        Args:
            x (int): Posición inicial en el eje X del jugador en el mundo del juego.
            y (int): Posición inicial en el eje Y del jugador en el mundo del juego.
            ruta_assets (str): Ruta a la carpeta principal de 'assets'.
        """
        super().__init__()
        self.ruta_assets = ruta_assets
        self.animaciones = {}
        self._cargar_animaciones()

        # Variables calculadas del perfil activo (se actualizan al seleccionar perfil)
        # Se inicializan aquí ANTES de la primera llamada a seleccionar_perfil_ataque
        self.num_segmentos_barrido_activo = 0
        self.duracion_segmento_barrido_activo = 0

        # Estado inicial de la animación
        self.estado_animacion = "descanso"
        self.indice_fotograma = 0
        if self.animaciones.get(self.estado_animacion):
            self.image = self.animaciones[self.estado_animacion][self.indice_fotograma]
        else:
            print(f"Error: Animación '{self.estado_animacion}' no encontrada para el Jugador. Usando placeholder.")
            self.image = pygame.Surface((32, 32))
            self.image.fill((255, 0, 0))
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
            print(f"Advertencia: Perfil activo inicial '{self.nombre_perfil_ataque_activo}' no es válido o no es un dict.")
            
            primer_perfil_valido_nombre = None
            for nombre, perfil_data in self.perfiles_de_ataque.items():
                if isinstance(perfil_data, dict):
                    primer_perfil_valido_nombre = nombre
                    break
            
            if primer_perfil_valido_nombre:
                self.nombre_perfil_ataque_activo = primer_perfil_valido_nombre
                print(f"Cambiando a primer perfil válido: '{self.nombre_perfil_ataque_activo}'")
            else:
                print("No hay perfiles válidos. Forzando creación del perfil por defecto.")
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
                    print(f"Perfiles de ataque cargados desde {settings.ARCHIVO_CONFIG_ATAQUE}")
                    # Validar cada perfil cargado
                    for nombre_perfil, perfil_data in list(self.perfiles_de_ataque.items()): # Usar list() para poder modificar el dict
                        if not isinstance(perfil_data, dict):
                            print(f"Alerta: Perfil '{nombre_perfil}' en JSON no es un diccionario. Recreando por defecto.")
                            self.perfiles_de_ataque[nombre_perfil] = self._crear_perfil_ataque_por_defecto(nombre_perfil)
                            # Considerar guardar aquí si se repara un perfil, o al final
                else:
                    print(f"Error: '{settings.ARCHIVO_CONFIG_ATAQUE}' no contiene un diccionario de perfiles. Creando estructura por defecto.")
                    self._forzar_creacion_perfil_default_y_guardar()
        except FileNotFoundError:
            print(f"Archivo '{settings.ARCHIVO_CONFIG_ATAQUE}' no encontrado. Creando perfil por defecto.")
            self._forzar_creacion_perfil_default_y_guardar()
        except json.JSONDecodeError:
            print(f"Error JSON en '{settings.ARCHIVO_CONFIG_ATAQUE}'. Creando perfil por defecto.")
            self._forzar_creacion_perfil_default_y_guardar()
        except Exception as e:
            print(f"Error cargando perfiles: {e}. Creando perfil por defecto.")
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
            print(f"Todos los perfiles de ataque guardados en {settings.ARCHIVO_CONFIG_ATAQUE}")
        except Exception as e:
            print(f"Error al guardar todos los perfiles de ataque: {e}")

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
            print(f"Perfil activo: '{self.nombre_perfil_ataque_activo}'. Dur seg: {self.duracion_segmento_barrido_activo:.2f}ms. Num_seg: {self.num_segmentos_barrido_activo}. Dur_total: {duracion_total}")
        else:
            print(f"Error: Perfil '{nombre_perfil_solicitado}' no encontrado o no es un dict. Intentando fallback.")
            
            # Estrategia de Fallback Simplificada:
            # 1. Intentar el perfil inicial por defecto (si es diferente del que falló).
            # 2. Si no, intentar el primer perfil válido encontrado (que no sea el que falló).
            # 3. Si no, forzar creación del perfil por defecto y seleccionarlo.

            nombre_perfil_default = settings.NOMBRE_PERFIL_ATAQUE_INICIAL
            
            # Intento 1: Perfil por defecto (si es diferente y válido)
            if nombre_perfil_solicitado != nombre_perfil_default and \
               isinstance(self.perfiles_de_ataque.get(nombre_perfil_default), dict):
                print(f"Fallback al perfil por defecto: {nombre_perfil_default}")
                self.seleccionar_perfil_ataque(nombre_perfil_default)
                return # Salir para evitar más fallbacks en esta llamada

            # Intento 2: Primer perfil válido encontrado (diferente del que falló)
            primer_otro_perfil_valido = None
            for nombre, datos_perfil in self.perfiles_de_ataque.items():
                if isinstance(datos_perfil, dict) and nombre != nombre_perfil_solicitado:
                    primer_otro_perfil_valido = nombre
                    break
            
            if primer_otro_perfil_valido:
                print(f"Fallback al primer otro perfil válido encontrado: {primer_otro_perfil_valido}")
                self.seleccionar_perfil_ataque(primer_otro_perfil_valido)
                return # Salir

            # Intento 3: Forzar creación y selección del perfil por defecto
            # Esto ocurre si el perfil solicitado era el default y falló, o no hay otros perfiles válidos.
            print("Forzando recreación del perfil por defecto y seleccionándolo.")
            self._forzar_creacion_perfil_default_y_guardar() # Esto actualiza nombre_perfil_ataque_activo
            # Después de forzar la creación, el perfil activo debería ser el default.
            # Seleccionarlo explícitamente para asegurar que todo se actualice.
            if isinstance(self.perfiles_de_ataque.get(self.nombre_perfil_ataque_activo), dict):
                 self.seleccionar_perfil_ataque(self.nombre_perfil_ataque_activo)
            else:
                 print(f"CRÍTICO: No se pudo seleccionar un perfil válido incluso después de forzar la creación.")
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
            print(f"Advertencia (set_parametro): No se pudo setear '{nombre_parametro}' en perfil '{self.nombre_perfil_ataque_activo}'.")

    # --- Métodos para ajustar parámetros del PERFIL ACTIVO en tiempo real ---
    def modificar_ataque_offset(self, cantidad):
        actual = self.get_parametro_ataque_activo("offset_distancia", 0)
        nuevo = max(0, actual + cantidad)
        self.set_parametro_ataque_activo("offset_distancia", nuevo)
        print(f"Perfil '{self.nombre_perfil_ataque_activo}' - offset_distancia: {nuevo}")

    def modificar_ataque_extension(self, cantidad):
        actual = self.get_parametro_ataque_activo("extension", 1)
        nuevo = max(1, actual + cantidad)
        self.set_parametro_ataque_activo("extension", nuevo)
        print(f"Perfil '{self.nombre_perfil_ataque_activo}' - extension: {nuevo}")

    def modificar_ataque_grosor(self, cantidad):
        actual = self.get_parametro_ataque_activo("grosor", 1)
        nuevo = max(1, actual + cantidad)
        self.set_parametro_ataque_activo("grosor", nuevo)
        print(f"Perfil '{self.nombre_perfil_ataque_activo}' - grosor: {nuevo}")

    def modificar_duracion_ataque_total(self, cantidad):
        actual = self.get_parametro_ataque_activo("duracion_total_ms", 50)
        nuevo = max(50, actual + cantidad)
        self.set_parametro_ataque_activo("duracion_total_ms", nuevo) # Esto llama a seleccionar_perfil_ataque para recalcular
        print(f"Perfil '{self.nombre_perfil_ataque_activo}' - duracion_total_ms: {nuevo}, seg_dur: {self.duracion_segmento_barrido_activo:.2f}")

    def _cargar_animaciones(self):
        """Carga los fotogramas para las animaciones del jugador.
        Por ahora, solo carga la animación de "descanso".
        """
        ruta_anim_descanso = os.path.join(self.ruta_assets, "character", "animaciones", "Player", "reposo")
        self.animaciones["descanso"] = []
        for i in range(1, 5): # Asumiendo 4 fotogramas: 1.png, 2.png, 3.png, 4.png
            try:
                img_path = os.path.join(ruta_anim_descanso, f"{i}.png")
                imagen = pygame.image.load(img_path).convert_alpha()
                # Escalar si es necesario, por ejemplo a 32x32
                # imagen = pygame.transform.scale(imagen, (32, 32))
                self.animaciones["descanso"].append(imagen)
            except pygame.error as e:
                print(f"Error al cargar la imagen de animación del jugador {img_path}: {e}")
                # Podríamos añadir una imagen placeholder si falla la carga
                placeholder = pygame.Surface((32,32))
                placeholder.fill((255,0,0)) # Rojo
                self.animaciones["descanso"].append(placeholder)
        
        if not self.animaciones["descanso"]:
            print("CRITICAL: No se cargaron fotogramas para la animación de descanso del Jugador.")
            placeholder = pygame.Surface((32,32)); placeholder.fill((255,0,0))
            self.animaciones["descanso"] = [placeholder]

    def actualizar_animacion(self):
        """Actualiza el fotograma actual de la animación del jugador basado en el tiempo.
        Se llama en cada fotograma del bucle principal del juego.
        """
        ahora = pygame.time.get_ticks()
        if ahora - self.tiempo_ultimo_fotograma > self.retraso_animacion:
            self.tiempo_ultimo_fotograma = ahora
            self.indice_fotograma = (self.indice_fotograma + 1) % len(self.animaciones[self.estado_animacion])
            self.image = self.animaciones[self.estado_animacion][self.indice_fotograma]

    def _actualizar_posicion_hitbox(self):
        self.hitbox.topleft = (self.rect.x + self.hitbox_offset_x, self.rect.y + self.hitbox_offset_y)

    def _mover_y_colisionar(self, dx, dy, obstaculos):
        # Guardar la posición original por si necesitamos revertir completamente un movimiento
        # (aunque con la corrección por ejes, esto es menos crucial aquí que en colisiones más simples)
        # pos_original_x = self.rect.x
        # pos_original_y = self.rect.y

        # --- Movimiento y colisiones en Eje X ---
        self.rect.x += dx
        self._actualizar_posicion_hitbox() # Actualizar hitbox a la nueva posición tentativa X

        # Comprobar límites del mundo en X
        if self.hitbox.left < 0:
            # El hitbox ha cruzado el borde izquierdo del mundo (0)
            # Ajustamos self.rect.x para que self.hitbox.left sea 0
            self.rect.x = 0 - self.hitbox_offset_x 
        elif self.hitbox.right > settings.ANCHO_MUNDO_JUEGO:
            # El hitbox ha cruzado el borde derecho del mundo
            # Ajustamos self.rect.x para que self.hitbox.right sea ANCHO_MUNDO_JUEGO
            self.rect.x = settings.ANCHO_MUNDO_JUEGO - self.hitbox_offset_x - self.hitbox.width
        self._actualizar_posicion_hitbox() # Re-sincronizar hitbox después de corrección de límites en X

        # Comprobar colisiones con obstáculos en X
        for obstaculo in obstaculos:
            if self.hitbox.colliderect(obstaculo.rect):
                if dx > 0: # Moviéndose a la derecha, choca con el lado izquierdo del obstáculo
                    self.rect.x = obstaculo.rect.left - self.hitbox_offset_x - self.hitbox.width
                elif dx < 0: # Moviéndose a la izquierda, choca con el lado derecho del obstáculo
                    self.rect.x = obstaculo.rect.right - self.hitbox_offset_x
                self._actualizar_posicion_hitbox() # Re-sincronizar hitbox después de la corrección por colisión en X
        
        # --- Movimiento y colisiones en Eje Y ---
        self.rect.y += dy
        self._actualizar_posicion_hitbox() # Actualizar hitbox a la nueva posición tentativa Y

        # Comprobar límites del mundo en Y
        if self.hitbox.top < 0:
            # El hitbox ha cruzado el borde superior del mundo (0)
            # Ajustamos self.rect.y para que self.hitbox.top sea 0
            self.rect.y = 0 - self.hitbox_offset_y
        elif self.hitbox.bottom > settings.ALTO_MUNDO_JUEGO:
            # El hitbox ha cruzado el borde inferior del mundo
            # Ajustamos self.rect.y para que self.hitbox.bottom sea ALTO_MUNDO_JUEGO
            self.rect.y = settings.ALTO_MUNDO_JUEGO - self.hitbox_offset_y - self.hitbox.height
        self._actualizar_posicion_hitbox() # Re-sincronizar hitbox después de corrección de límites en Y

        # Comprobar colisiones con obstáculos en Y
        for obstaculo in obstaculos:
            if self.hitbox.colliderect(obstaculo.rect):
                if dy > 0: # Moviéndose hacia abajo, choca con la parte superior del obstáculo
                    self.rect.y = obstaculo.rect.top - self.hitbox_offset_y - self.hitbox.height
                elif dy < 0: # Moviéndose hacia arriba, choca con la parte inferior del obstáculo
                    self.rect.y = obstaculo.rect.bottom - self.hitbox_offset_y
                self._actualizar_posicion_hitbox() # Re-sincronizar hitbox después de la corrección por colisión en Y

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
        
        # Actualizar la última dirección de movimiento solo si hay movimiento efectivo
        if mov_x_final != 0 or mov_y_final != 0:
            # Priorizar horizontal si hay movimiento en ambos ejes para la última dirección principal
            # Esto es una simplificación; podría ser más complejo para 8 direcciones si es necesario.
            if mov_x_final != 0:
                self.ultima_direccion_mov_x = int(mov_x_final / self.velocidad) # Normalizar a 1 o -1
                self.ultima_direccion_mov_y = 0 # Si hay mov X, se considera la dirección principal
            elif mov_y_final != 0: # Solo si no hay mov_x_final
                self.ultima_direccion_mov_x = 0
                self.ultima_direccion_mov_y = int(mov_y_final / self.velocidad) # Normalizar a 1 o -1
            
            # Si se permite movimiento diagonal y se quiere guardar la componente diagonal exacta:
            # if mov_x_final != 0:
            #     self.ultima_direccion_mov_x = int(mov_x_final / self.velocidad)
            # else:
            #     self.ultima_direccion_mov_x = 0 # Mantener en 0 si no hay input horizontal
            # if mov_y_final != 0:
            #     self.ultima_direccion_mov_y = int(mov_y_final / self.velocidad)
            # else:
            #     self.ultima_direccion_mov_y = 0 # Mantener en 0 si no hay input vertical
            
            # Corregir si ambos son cero por alguna razón (aunque la condición externa lo evita)
            # if self.ultima_direccion_mov_x == 0 and self.ultima_direccion_mov_y == 0:
                # Forzar una dirección por defecto si se queda en (0,0) después de moverse
                # self.ultima_direccion_mov_x = 1 # Derecha por defecto

            self._mover_y_colisionar(mov_x_final, mov_y_final, obstaculos)
        
        # # --- AÑADIMOS MOVIMIENTO SIMPLE SIN COLISIÓN ---
        # self.rect.x += mov_x_final
        # self.rect.y += mov_y_final
        # # self._actualizar_posicion_hitbox() 

    def dibujar(self, superficie):
        """Dibuja el sprite actual del jugador en la superficie dada.
        Nota: Con el sistema de cámara, este método se vuelve menos relevante si la cámara
        dibuja directamente el jugador.image. Sin embargo, es una buena práctica tenerlo.

        Args:
            superficie (pygame.Surface): La superficie donde se dibujará el jugador.
        """
        superficie.blit(self.image, self.rect)
        # Opcional: Dibujar el hitbox para depuración
        # pygame.draw.rect(superficie, (255,0,0), self.hitbox, 1) 

    def recibir_dano(self, cantidad):
        ahora = pygame.time.get_ticks()
        if ahora - self.ultimo_ataque_recibido > self.cooldown_dano:
            self.vida_actual -= cantidad
            self.ultimo_ataque_recibido = ahora
            print(f"Jugador recibe {cantidad} de daño. Vida restante: {self.vida_actual}")
            if self.vida_actual <= 0:
                self.morir()
        # else: print("Jugador en cooldown, daño ignorado") # Para depuración

    def morir(self):
        print("Jugador ha muerto!")
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
                print(f"Jugador inicia ataque con perfil '{self.nombre_perfil_ataque_activo}'!")

    def actualizar_ataque(self, enemigos):
        if not self.esta_atacando:
            self.hitbox_ataque_actual_rect.size = (0,0) 
            return

        # Obtener parámetros del perfil activo
        offset_dist = self.get_parametro_ataque_activo("offset_distancia", 25)
        extension = self.get_parametro_ataque_activo("extension", 30)
        grosor = self.get_parametro_ataque_activo("grosor", 15)
        duracion_total_ms = self.get_parametro_ataque_activo("duracion_total_ms", 300)
        plantilla_angulos = self.get_parametro_ataque_activo("plantilla_angulos_grados", [0])
        dano_actual = self.dano_base_ataque * self.get_parametro_ataque_activo("dano_modificador", 1.0)
        
        # Usar las variables calculadas en seleccionar_perfil_ataque
        num_segmentos = self.num_segmentos_barrido_activo
        dur_segmento = self.duracion_segmento_barrido_activo

        # DEBUG PRINT
        print(f"DEBUG actualizar_ataque: perfil='{self.nombre_perfil_ataque_activo}', esta_atacando={self.esta_atacando}, num_seg={num_segmentos}, dur_seg={dur_segmento:.2f}, dur_total_ms_perfil={duracion_total_ms}")

        ahora = pygame.time.get_ticks()
        tiempo_transcurrido_ataque = ahora - self.tiempo_inicio_ataque

        if tiempo_transcurrido_ataque <= duracion_total_ms and num_segmentos > 0:
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
                    if self.hitbox_ataque_actual_rect.colliderect(enemigo.rect):
                        print(f"ATAQUE '{self.nombre_perfil_ataque_activo}' (seg {segmento_actual_indice}) golpea enemigo")
                        enemigo.recibir_dano(dano_actual)
                        self.enemigos_golpeados_este_ataque.add(enemigo)
        else:
            self.esta_atacando = False
            self.hitbox_ataque_actual_rect.size = (0,0)