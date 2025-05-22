import pygame
from src.config import settings # MODIFICADO
import logging

# Logger para GestorEventos
# logger_ge = logging.getLogger(__name__) # Usará el nombre del módulo, ej. 'gestor_eventos'
logger = logging.getLogger("gestor_eventos")
# No establecemos nivel aquí, se controla desde la configuración raíz y MODO_DEBUG_LOGS

class GestorEventos:
    def __init__(self, jugador, hud, juego_ref):
        """
        Inicializa el GestorEventos.

        Args:
            jugador: Instancia del jugador para interactuar con él (ataque, perfiles).
            hud: Instancia del HUD para pasarle eventos.
            juego_ref: Referencia a la instancia principal del juego.
        """
        print("DEBUG: GestorEventos.__init__()") # Print de prueba
        self.jugador = jugador
        self.hud = hud
        self.juego_ref = juego_ref
        
        # Estado interno que puede ser consultado por la clase Juego
        self.solicitud_salir = False
        self.ultimo_scroll_time = 0
        self.scroll_delay = 100 # ms, ajustar según sea necesario

        # Evaluar condición de log una vez
        log_ev_handler_enabled = settings.MODO_DEBUG_LOGS and settings.LOG_CATEGORIAS.get("log_gestor_eventos", False)
        if log_ev_handler_enabled:
            logger.debug("GestorEventos inicializado.", extra={"categoria_log": "log_gestor_eventos"})

    def procesar_eventos(self, eventos_pygame):
        """
        Procesa la lista de eventos de Pygame.

        Args:
            eventos_pygame: La lista de eventos obtenida de pygame.event.get().
        """
        print("DEBUG: GestorEventos.procesar_eventos() - INICIO")
        # Evaluar condiciones de log una vez al inicio del método
        log_ev_handler_enabled = settings.MODO_DEBUG_LOGS and settings.LOG_CATEGORIAS.get("log_gestor_eventos", False)
        log_ev_verbose_enabled = settings.MODO_DEBUG_LOGS and settings.LOG_CATEGORIAS.get("log_gestor_eventos_verbose", False)

        if log_ev_verbose_enabled:
            logger.debug(f"Procesando {len(eventos_pygame)} eventos...", extra={"categoria_log": "log_gestor_eventos_verbose"})

        # Obtener el factor de zoom actual desde la instancia de Juego
        factor_zoom_actual = self.juego_ref.factor_zoom_actual

        # Primero, verificar si hay eventos. Si no, salir temprano.
        if not eventos_pygame:
            # Este log es útil para saber si Pygame no está generando eventos o si se están consumiendo en otro lado.
            if settings.MODO_DEBUG_LOGS and settings.LOG_CATEGORIAS.get("log_gestor_eventos_verbose", False):
                logger.debug("Procesar eventos llamado sin eventos en la lista.", extra={"categoria_log": "log_gestor_eventos_verbose"})
            print("DEBUG: GestorEventos.procesar_eventos() - No hay eventos, retornando.")
            return

        for event in eventos_pygame:
            try:
                if log_ev_verbose_enabled:
                    logger.debug(f"Evento: {event}", extra={"categoria_log": "log_gestor_eventos_verbose"})

                if event.type == pygame.QUIT:
                    self.solicitud_salir = True
                    if log_ev_handler_enabled:
                        logger.info("GestorEventos: Solicitud de SALIR recibida (QUIT).", extra={"categoria_log": "log_gestor_eventos"})
                
                if hasattr(self.hud, 'manejar_input_hud'):
                    self.hud.manejar_input_hud(event) 

                if event.type == pygame.MOUSEWHEEL: 
                    delta_zoom = settings.FACTOR_ZOOM_PASO if event.y > 0 else -settings.FACTOR_ZOOM_PASO
                    calculo_nuevo_zoom = factor_zoom_actual + delta_zoom # Calculamos el zoom deseado
                    nuevo_factor_zoom = max(settings.FACTOR_ZOOM_MIN, min(calculo_nuevo_zoom, settings.FACTOR_ZOOM_MAX)) # Aplicamos límites
                    
                    if nuevo_factor_zoom != factor_zoom_actual: # Solo actualizar si realmente cambió
                        self.juego_ref.actualizar_factor_zoom(nuevo_factor_zoom)
                        factor_zoom_actual = nuevo_factor_zoom # ACTUALIZAMOS LA VARIABLE LOCAL
                        if log_ev_handler_enabled:
                            logger.debug(f"GestorEventos: MOUSEWHEEL. Zoom actual: {factor_zoom_actual:.2f}, Solicitado nuevo: {calculo_nuevo_zoom:.2f}, Aplicado: {nuevo_factor_zoom:.2f}", extra={"categoria_log": "log_gestor_eventos"})

                if event.type == pygame.KEYDOWN:
                    if log_ev_handler_enabled:
                        logger.debug(f"GestorEventos: KEYDOWN {pygame.key.name(event.key)} ({event.key})", extra={"categoria_log": "log_gestor_eventos"})

                    if event.key == pygame.K_ESCAPE:
                        self.solicitud_salir = True
                        if log_ev_handler_enabled:
                            logger.info("GestorEventos: Solicitud de SALIR recibida (ESCAPE).", extra={"categoria_log": "log_gestor_eventos"})
                    
                    if event.key == pygame.K_SPACE: 
                        if self.jugador:
                            self.jugador.atacar()
                            if log_ev_handler_enabled:
                                logger.debug("GestorEventos: K_SPACE (Atacar jugador) procesado.", extra={"categoria_log": "log_gestor_eventos"})
                        else:
                            if log_ev_handler_enabled:
                                logger.warning("GestorEventos: K_SPACE presionado, pero no hay instancia de jugador.", extra={"categoria_log": "log_gestor_eventos"})


                    if self.jugador and hasattr(self.jugador, 'attack_profile_manager'):
                        apm = self.jugador.attack_profile_manager
                        nombres_perfiles = apm.get_nombres_perfiles_disponibles()

                        if not nombres_perfiles:
                            if log_ev_handler_enabled:
                                logger.warning("GestorEventos: No hay perfiles de ataque disponibles para cambiar.", extra={"categoria_log": "log_gestor_eventos"})
                        else:
                            try:
                                indice_actual = nombres_perfiles.index(apm.nombre_perfil_ataque_activo)
                            except ValueError:
                                if log_ev_handler_enabled:
                                    logger.warning(f"GestorEventos: Perfil activo '{apm.nombre_perfil_ataque_activo}' no en lista. Seleccionando el primero.", extra={"categoria_log": "log_gestor_eventos"})
                                apm.seleccionar_perfil_ataque(nombres_perfiles[0])
                                indice_actual = 0 # Asumir el primero

                            nuevo_indice = indice_actual
                            if event.key == pygame.K_PAGEUP:
                                nuevo_indice = (indice_actual - 1 + len(nombres_perfiles)) % len(nombres_perfiles)
                                apm.seleccionar_perfil_ataque(nombres_perfiles[nuevo_indice])
                                if log_ev_handler_enabled:
                                    logger.debug(f"GestorEventos: K_PAGEUP. Nuevo perfil ataque: {apm.nombre_perfil_ataque_activo}", extra={"categoria_log": "log_gestor_eventos"})
                            
                            elif event.key == pygame.K_PAGEDOWN:
                                nuevo_indice = (indice_actual + 1) % len(nombres_perfiles)
                                apm.seleccionar_perfil_ataque(nombres_perfiles[nuevo_indice])
                                if log_ev_handler_enabled:
                                    logger.debug(f"GestorEventos: K_PAGEDOWN. Nuevo perfil ataque: {apm.nombre_perfil_ataque_activo}", extra={"categoria_log": "log_gestor_eventos"})

                        param_map = {
                            pygame.K_F1: ("offset_distancia", 0.1), pygame.K_F2: ("offset_distancia", -0.1),
                            pygame.K_F3: ("extension", 1), pygame.K_F4: ("extension", -1),
                            pygame.K_F5: ("dano_modificador", 0.1), pygame.K_F6: ("dano_modificador", -0.1),
                            pygame.K_F7: ("cooldown_modificador", 0.05), pygame.K_F8: ("cooldown_modificador", -0.05),
                            pygame.K_F9: ("duracion_total_ms", 50), pygame.K_F10: ("duracion_total_ms", -50),
                        }
                        if event.key in param_map:
                            param_name, delta = param_map[event.key]
                            try:
                                current_value = float(apm.get_parametro_ataque_activo(param_name, 0.0)) 
                                new_value = current_value + delta
                                
                                if param_name == "dano_modificador" and new_value < 0: new_value = 0.0
                                if param_name == "cooldown_modificador" and new_value < 0: new_value = 0.0
                                if param_name == "duracion_total_ms" and new_value < 50: new_value = 50
                                if param_name == "offset_distancia" and new_value < 0: new_value = 0.0
                                if param_name == "extension" and new_value < 1: new_value = 1.0

                                apm.set_parametro_ataque_activo(param_name, new_value)
                                if log_ev_handler_enabled: 
                                    logger.debug(f"GestorEventos: {pygame.key.name(event.key)}. Param '{param_name}' -> {new_value:.2f}", extra={"categoria_log": "log_gestor_eventos"})
                            except ValueError as e:
                                logger.error(f"GestorEventos Error: F-Key Convert '{param_name}' a float. Valor era: {apm.get_parametro_ataque_activo(param_name)}. Error: {e}", extra={"categoria_log": "log_gestor_eventos"})
                            except AttributeError:
                                logger.error(f"GestorEventos Error: F-Key APM no disponible en jugador.", extra={"categoria_log": "log_gestor_eventos"})
                            except Exception as e:
                                logger.error(f"GestorEventos Error: F-Key '{param_name}' mod: {e}", extra={"categoria_log": "log_gestor_eventos"})
                    elif event.key >= pygame.K_F1 and event.key <= pygame.K_F10 : 
                        if log_ev_handler_enabled:
                            logger.warning(f"GestorEventos: {pygame.key.name(event.key)} presionado, pero no hay jugador o attack_profile_manager.", extra={"categoria_log": "log_gestor_eventos"})
            except Exception as e:
                logger.error(f"GestorEventos Error no manejado al procesar evento {event}: {e}", extra={"categoria_log": "log_gestor_eventos", "skip_duplicate_check": True})
                import traceback
                logger.error(f"Traza de error: {traceback.format_exc()}", extra={"categoria_log": "log_gestor_eventos", "skip_duplicate_check": True})

        print("DEBUG: GestorEventos.procesar_eventos() - FIN")

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
            logger.info("MockJugador.atacar() llamado", extra={"categoria_log": "log_gestor_eventos"})

    class MockAttackProfileManager:
        def __init__(self):
            self.perfil_actual_nombre = "default"
            self.params = {"damage": 10, "attack_cooldown": 500}
            self.nombres_perfiles_disponibles = ["default", "otro"]
            self.nombre_perfil_ataque_activo = "default"
        def get_nombres_perfiles_disponibles(self):
            return self.nombres_perfiles_disponibles
        def seleccionar_perfil_ataque(self, nombre_perfil):
            self.nombre_perfil_ataque_activo = nombre_perfil
            logger.info(f"MockAPM.seleccionar_perfil_ataque({nombre_perfil})", extra={"categoria_log": "log_gestor_eventos"})
        def get_parametro_ataque_activo(self, nombre_param, default=None):
            return self.params.get(nombre_param, default)
        def set_parametro_ataque_activo(self, nombre_param, valor):
            self.params[nombre_param] = valor
            logger.info(f"MockAPM.set_parametro_ataque_activo({nombre_param}, {valor})", extra={"categoria_log": "log_gestor_eventos"})

    class MockHUD:
        def manejar_input_hud(self, event):
            pass

    class MockJuego:
        def __init__(self):
            self.factor_zoom_actual = 1.0
        def actualizar_factor_zoom(self, nuevo_zoom):
            self.factor_zoom_actual = nuevo_zoom
            logger.info(f"MockJuego.actualizar_factor_zoom({nuevo_zoom})", extra={"categoria_log": "log_gestor_eventos"})

    # Para que este __main__ funcione con el settings.py real, nos aseguramos que MODO_DEBUG_LOGS está True
    # y las categorías relevantes también.
    # Idealmente, settings sería inyectado o mockeado de forma más robusta en un framework de test.
    
    # Guardar estado original de settings y modificarlo para la prueba
    original_modo_debug_logs = settings.MODO_DEBUG_LOGS
    original_log_event_handler = settings.LOG_CATEGORIAS.get("log_gestor_eventos")
    original_log_event_handler_verbose = settings.LOG_CATEGORIAS.get("log_gestor_eventos_verbose")

    settings.MODO_DEBUG_LOGS = True
    settings.LOG_CATEGORIAS["log_gestor_eventos"] = True
    settings.LOG_CATEGORIAS["log_gestor_eventos_verbose"] = True

    pygame.init()
    pantalla = pygame.display.set_mode((settings.ANCHO_PANTALLA, settings.ALTO_PANTALLA))
    pygame.display.set_caption("Test GestorEventos")

    jugador_mock = MockJugador()
    hud_mock = MockHUD()
    juego_mock = MockJuego()

    gestor = GestorEventos(jugador_mock, hud_mock, juego_mock)

    print("\n--- Probando GestorEventos --- Triggear eventos manualmente ---")
    print("Presiona ESCAPE para salir, ESPACIO para atacar, PAGEUP/PAGEDOWN para cambiar perfil, F-keys para params, rueda del mouse para zoom.")

    # Simulación de bucle de juego para pruebas
    reloj = pygame.time.Clock()
    running = True
    while running:
        eventos = pygame.event.get()
        gestor.procesar_eventos(eventos)

        if gestor.debe_salir():
            running = False

        pygame.display.flip()
        reloj.tick(settings.FPS)
    
    print("--- Fin Prueba GestorEventos ---")
    # Restaurar settings
    settings.MODO_DEBUG_LOGS = original_modo_debug_logs
    if original_log_event_handler is not None: settings.LOG_CATEGORIAS["log_gestor_eventos"] = original_log_event_handler
    if original_log_event_handler_verbose is not None: settings.LOG_CATEGORIAS["log_gestor_eventos_verbose"] = original_log_event_handler_verbose
    
    pygame.quit() 