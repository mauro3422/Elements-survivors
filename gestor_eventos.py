import pygame
import settings
import logging

# Logger para GestorEventos
logger_ge = logging.getLogger(__name__) # Usará el nombre del módulo, ej. 'gestor_eventos'
# No establecemos nivel aquí, se controla desde la configuración raíz y MODO_DEBUG_LOGS

class GestorEventos:
    def __init__(self, jugador, hud):
        """
        Inicializa el GestorEventos.

        Args:
            jugador: Instancia del jugador para interactuar con él (ataque, perfiles).
            hud: Instancia del HUD para pasarle eventos.
        """
        self.jugador = jugador
        self.hud = hud
        
        # Estado interno que puede ser consultado por la clase Juego
        self.solicitud_salir = False
        self.nuevo_factor_zoom = None # Se actualiza si hay MOUSEWHEEL

        if settings.MODO_DEBUG_LOGS and settings.LOG_CATEGORIAS.get("log_event_handler", False): # Categoria nueva
            logger_ge.debug("GestorEventos inicializado.")

    def procesar_eventos(self, eventos, factor_zoom_actual):
        """
        Procesa la lista de eventos de Pygame.

        Args:
            eventos: La lista de eventos obtenida de pygame.event.get().
            factor_zoom_actual: El valor actual del zoom en la clase Juego.

        Returns:
            float or None: El nuevo factor de zoom si cambió, sino el original.
                           (Decidí devolverlo directamente en vez de un flag)
        """
        if settings.MODO_DEBUG_LOGS and settings.LOG_CATEGORIAS.get("log_event_handler_verbose", False): # Categoria más detallada
            logger_ge.debug(f"Procesando {len(eventos)} eventos...")

        self.nuevo_factor_zoom = factor_zoom_actual # Empezamos con el actual

        for event in eventos:
            if settings.MODO_DEBUG_LOGS and settings.LOG_CATEGORIAS.get("log_event_handler_verbose", False):
                logger_ge.debug(f"  Evento: {pygame.event.event_name(event.type)} ({event})")

            if event.type == pygame.QUIT:
                self.solicitud_salir = True
                if settings.MODO_DEBUG_LOGS and settings.LOG_CATEGORIAS.get("log_event_handler", False):
                    logger_ge.info("GestorEventos: Solicitud de SALIR recibida (QUIT).")
            
            if hasattr(self.hud, 'manejar_input_hud'):
                # Dejamos que el HUD maneje el evento si lo necesita
                # Si HUD consume el evento, podría devolver True, y podríamos no procesarlo más.
                # Por ahora, simplemente lo pasamos.
                self.hud.manejar_input_hud(event) 

            if event.type == pygame.MOUSEWHEEL: 
                delta_zoom = settings.FACTOR_ZOOM_PASO if event.y > 0 else -settings.FACTOR_ZOOM_PASO
                self.nuevo_factor_zoom = max(settings.FACTOR_ZOOM_MIN, min(factor_zoom_actual + delta_zoom, settings.FACTOR_ZOOM_MAX))
                if settings.MODO_DEBUG_LOGS and settings.LOG_CATEGORIAS.get("log_event_handler", False):
                    logger_ge.debug(f"GestorEventos: MOUSEWHEEL (y:{event.y}). Zoom: {factor_zoom_actual:.2f} -> {self.nuevo_factor_zoom:.2f}")

            if event.type == pygame.KEYDOWN:
                if settings.MODO_DEBUG_LOGS and settings.LOG_CATEGORIAS.get("log_event_handler", False):
                    logger_ge.debug(f"GestorEventos: KEYDOWN {pygame.key.name(event.key)} ({event.key})")

                if event.key == pygame.K_ESCAPE:
                    self.solicitud_salir = True
                    if settings.MODO_DEBUG_LOGS and settings.LOG_CATEGORIAS.get("log_event_handler", False):
                        logger_ge.info("GestorEventos: Solicitud de SALIR recibida (ESCAPE).")
                
                if event.key == pygame.K_SPACE: 
                    if self.jugador:
                        self.jugador.atacar() # Jugador.atacar() tiene sus propios logs
                        if settings.MODO_DEBUG_LOGS and settings.LOG_CATEGORIAS.get("log_event_handler", False):
                            logger_ge.debug("GestorEventos: K_SPACE (Atacar jugador) procesado.")
                    else:
                        if settings.MODO_DEBUG_LOGS and settings.LOG_CATEGORIAS.get("log_event_handler", False):
                            logger_ge.warning("GestorEventos: K_SPACE presionado, pero no hay instancia de jugador.")


                if self.jugador and hasattr(self.jugador, 'attack_profile_manager'):
                    apm = self.jugador.attack_profile_manager
                    nombres_perfiles = apm.get_nombres_perfiles_disponibles()

                    if not nombres_perfiles:
                        if settings.MODO_DEBUG_LOGS and settings.LOG_CATEGORIAS.get("log_event_handler", False):
                            logger_ge.warning("GestorEventos: No hay perfiles de ataque disponibles para cambiar.")
                    else:
                        try:
                            indice_actual = nombres_perfiles.index(apm.nombre_perfil_ataque_activo)
                        except ValueError:
                            # El perfil activo actual no está en la lista, algo raro. Seleccionar el primero.
                            if settings.MODO_DEBUG_LOGS and settings.LOG_CATEGORIAS.get("log_event_handler", False):
                                logger_ge.warning(f"GestorEventos: Perfil activo '{apm.nombre_perfil_ataque_activo}' no en lista. Seleccionando el primero.")
                            apm.seleccionar_perfil_ataque(nombres_perfiles[0])
                            indice_actual = 0 # Asumir el primero

                        nuevo_indice = indice_actual
                        if event.key == pygame.K_PAGEUP:
                            nuevo_indice = (indice_actual - 1 + len(nombres_perfiles)) % len(nombres_perfiles)
                            apm.seleccionar_perfil_ataque(nombres_perfiles[nuevo_indice])
                            if settings.MODO_DEBUG_LOGS and settings.LOG_CATEGORIAS.get("log_event_handler", False):
                                logger_ge.debug(f"GestorEventos: K_PAGEUP. Nuevo perfil ataque: {apm.nombre_perfil_ataque_activo}")
                        
                        elif event.key == pygame.K_PAGEDOWN:
                            nuevo_indice = (indice_actual + 1) % len(nombres_perfiles)
                            apm.seleccionar_perfil_ataque(nombres_perfiles[nuevo_indice])
                            if settings.MODO_DEBUG_LOGS and settings.LOG_CATEGORIAS.get("log_event_handler", False):
                                logger_ge.debug(f"GestorEventos: K_PAGEDOWN. Nuevo perfil ataque: {apm.nombre_perfil_ataque_activo}")

                    param_map = {
                        pygame.K_F1: ("offset_distancia", 0.1), pygame.K_F2: ("offset_distancia", -0.1), # Asumiendo que offset_distancia existe
                        pygame.K_F3: ("extension", 1), pygame.K_F4: ("extension", -1), # Asumiendo que extension existe
                        # Los parámetros originales eran hitbox_amplitude y hitbox_duration_ratio que no parecen estar en APM ahora.
                        # Uso damage y attack_cooldown como estaban, y añado otros basados en los métodos de APM.
                        pygame.K_F5: ("dano_modificador", 0.1), pygame.K_F6: ("dano_modificador", -0.1),
                        pygame.K_F7: ("cooldown_modificador", 0.05), pygame.K_F8: ("cooldown_modificador", -0.05),
                        # Los parámetros de F9 y F10 se mapeaban a attack_cooldown y damage en tu código original.
                        # Voy a mantener la idea de modificar damage y cooldown con F9/F10, pero usando los modificadores
                        # ya que APM usa "dano_modificador" y "cooldown_modificador".
                        # Si quieres modificar el "damage" base de un arma, se necesitaría otra interfaz.
                        # O, si los parámetros directos como "damage" y "attack_cooldown" existen en los JSON, se pueden usar.
                        # Por ahora, asumiré que los parámetros en el JSON son los que se listan en _crear_perfil_ataque_por_defecto
                        # y que queremos modificar esos.
                        # Si "damage" y "attack_cooldown" no son modificadores sino valores base, el APM debería tener métodos para ellos.
                        # Revisando APM, tiene `_crear_perfil_ataque_por_defecto` con `dano_modificador` y `cooldown_modificador`.
                        # Y los métodos `modificar_...` como `modificar_ataque_offset`.
                        # El error original era con "damage". Voy a asumir que "damage" es un parámetro válido en el JSON.
                        # Y "attack_cooldown" también.
                        # El error era float(None). Vamos a pedir a get_parametro_ataque_activo un default de 0.0.
                        pygame.K_F9: ("duracion_total_ms", 50), pygame.K_F10: ("duracion_total_ms", -50), # Ejemplo, usando duracion_total_ms
                    }
                    if event.key in param_map:
                        param_name, delta = param_map[event.key]
                        try:
                            # Pedir valor con default numérico para evitar float(None)
                            current_value = float(apm.get_parametro_ataque_activo(param_name, 0.0)) 
                            new_value = current_value + delta
                            
                            # Aplicar restricciones específicas del parámetro
                            if param_name == "dano_modificador" and new_value < 0: new_value = 0.0
                            if param_name == "cooldown_modificador" and new_value < 0: new_value = 0.0
                            if param_name == "duracion_total_ms" and new_value < 50: new_value = 50 # Duración mínima
                            if param_name == "offset_distancia" and new_value < 0: new_value = 0.0
                            if param_name == "extension" and new_value < 1: new_value = 1.0

                            apm.set_parametro_ataque_activo(param_name, new_value)
                            if settings.MODO_DEBUG_LOGS and settings.LOG_CATEGORIAS.get("log_event_handler", False): 
                                logger_ge.debug(f"GestorEventos: {pygame.key.name(event.key)}. Param '{param_name}' -> {new_value:.2f}")
                        except ValueError as e:
                            logger_ge.error(f"GestorEventos Error: F-Key Convert '{param_name}' a float. Valor era: {apm.get_parametro_ataque_activo(param_name)}. Error: {e}")
                        except AttributeError:
                            logger_ge.error(f"GestorEventos Error: F-Key APM no disponible en jugador.")
                        except Exception as e:
                            logger_ge.error(f"GestorEventos Error: F-Key '{param_name}' mod: {e}")
                elif event.key >= pygame.K_F1 and event.key <= pygame.K_F10 : # Si se presiona Fkey pero no hay jugador/APM
                    if settings.MODO_DEBUG_LOGS and settings.LOG_CATEGORIAS.get("log_event_handler", False):
                        logger_ge.warning(f"GestorEventos: {pygame.key.name(event.key)} presionado, pero no hay jugador o attack_profile_manager.")

        return self.nuevo_factor_zoom # Devuelve el factor de zoom (puede ser el mismo o uno nuevo)

    def debe_salir(self):
        """Chequea si se ha solicitado salir del juego."""
        return self.solicitud_salir

# Ejemplo de uso (requiere un settings.py mínimo y stubs para Jugador/HUD si se prueba aislado)
if __name__ == '__main__':
    # Configuración mínima de logging para prueba
    if not logging.getLogger().hasHandlers():
        logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - [%(levelname)s] - %(message)s')

    # Crear stubs para las dependencias
    class MockJugador:
        def __init__(self):
            self.attack_profile_manager = MockAttackProfileManager()
        def atacar(self):
            logger_ge.info("MockJugador.atacar() llamado")

    class MockAttackProfileManager:
        def __init__(self):
            self.perfil_actual_nombre = "default"
            self.params = {"damage": 10, "attack_cooldown": 500}
        def seleccionar_perfil_anterior(self): 
            logger_ge.info("MockAPM.seleccionar_perfil_anterior()")
        def seleccionar_perfil_siguiente(self): 
            logger_ge.info("MockAPM.seleccionar_perfil_siguiente()")
        def get_parametro_ataque_activo(self, nombre_param):
            return self.params.get(nombre_param, 0)
        def modificar_parametro_perfil_activo(self, nombre_param, valor):
            self.params[nombre_param] = valor
            logger_ge.info(f"MockAPM.modificar_parametro_perfil_activo({nombre_param}, {valor})")

    class MockHUD:
        def manejar_input_hud(self, event):
            # logger_ge.debug(f"MockHUD.manejar_input_hud({event})")
            pass

    # Simular settings
    class SettingsSim:
        MODO_DEBUG_LOGS = True
        LOG_CATEGORIAS = {
            "log_event_handler": True,
            "log_event_handler_verbose": True, # Para ver todos los eventos
        }
        FACTOR_ZOOM_PASO = 0.1
        FACTOR_ZOOM_MIN = 0.5
        FACTOR_ZOOM_MAX = 3.0
    
    settings = SettingsSim() # Sobrescribir el import de settings real para la prueba

    pygame.init() # Necesario para pygame.event y nombres de teclas
    pantalla_stub = pygame.display.set_mode((100,100)) # Para que pygame.event.get() no falle

    # Crear instancias
    jugador_mock = MockJugador()
    hud_mock = MockHUD()
    gestor_evt = GestorEventos(jugador_mock, hud_mock)

    # Simular bucle de eventos
    print("\n--- Probando GestorEventos --- (Presiona ESC para 'salir', rueda del mouse para zoom, ESPACIO para atacar, F1-F2 para cambiar 'damage')")
    running_test = True
    current_zoom = 1.0
    while running_test:
        eventos_pygame = pygame.event.get()
        
        # Aquí es donde la clase Juego llamaría a procesar_eventos
        current_zoom = gestor_evt.procesar_eventos(eventos_pygame, current_zoom)

        if gestor_evt.debe_salir():
            running_test = False
            logger_ge.info("Prueba: detectada solicitud_salir. Terminando bucle.")
        
        # Pequeña pausa para no consumir 100% CPU en el test
        pygame.time.wait(50) 

    pygame.quit()
    print("--- Fin Prueba GestorEventos ---") 