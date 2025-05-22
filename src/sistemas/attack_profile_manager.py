import os
import json
import logging
# import settings
from src.config import settings # MODIFICADO

logger = logging.getLogger("attack_profile_manager")

class AttackProfileManager:
    def __init__(self, ruta_base_proyecto_settings, archivo_config_settings, nombre_perfil_inicial_settings):
        self.ruta_base_proyecto = ruta_base_proyecto_settings
        self.archivo_config_nombre = archivo_config_settings
        self.nombre_perfil_inicial_predeterminado = nombre_perfil_inicial_settings

        self.perfiles_de_ataque = {}
        self.nombre_perfil_ataque_activo = self.nombre_perfil_inicial_predeterminado # Se actualizará al cargar/crear
        
        # Estos se calcularán cuando se seleccione un perfil
        self._num_segmentos_barrido_activo = 0
        self._duracion_segmento_barrido_activo = 0

        self._cargar_o_crear_perfiles_ataque()
        # Asegurar que el perfil activo (potencialmente cargado) tenga sus segmentos calculados
        if self.nombre_perfil_ataque_activo in self.perfiles_de_ataque:
            self.seleccionar_perfil_ataque(self.nombre_perfil_ataque_activo)
        elif self.perfiles_de_ataque: # Si el activo no existe pero hay otros, tomar el primero
            primer_perfil = next(iter(self.perfiles_de_ataque))
            logger.warning(f"Perfil activo '{self.nombre_perfil_ataque_activo}' no encontrado tras carga. Usando el primero disponible: '{primer_perfil}'", extra={"categoria_log": "log_attack_profile_manager"})
            self.seleccionar_perfil_ataque(primer_perfil)
        else: # No hay perfiles (debería haberse creado uno por defecto en _cargar_o_crear_perfiles_ataque)
            logger.error("No se encontraron perfiles después de la inicialización. Esto no debería ocurrir.", extra={"categoria_log": "log_attack_profile_manager"})


    @property
    def num_segmentos_barrido_activo(self):
        return self._num_segmentos_barrido_activo

    @property
    def duracion_segmento_barrido_activo(self):
        return self._duracion_segmento_barrido_activo

    # --- Métodos que se moverán/adaptarán desde Jugador ---

    def _crear_perfil_ataque_por_defecto(self, nombre_perfil):
        # Esta función se moverá aquí desde Jugador
        logger.debug(f"Creando perfil de ataque por defecto con nombre: {nombre_perfil}", extra={"categoria_log": "log_attack_profile_manager"})
        return {
            "offset_distancia": settings.ATAQUE_BASE_OFFSET_DISTANCIA,
            "extension": settings.ATAQUE_BASE_EXTENSION,
            "grosor": settings.ATAQUE_BASE_GROSOR,
            "duracion_total_ms": settings.ATAQUE_BASE_DURACION_TOTAL_MS,
            "plantilla_angulos_grados": settings.ATAQUE_BASE_PLANTILLA_ANGULOS_GRADOS,
            "dano_modificador": settings.ATAQUE_BASE_DANO_MODIFICADOR,
            "cooldown_modificador": settings.ATAQUE_BASE_COOLDOWN_MODIFICADOR
        }

    def _cargar_o_crear_perfiles_ataque(self):
        # Esta función se moverá aquí desde Jugador
        # Necesitará self.ruta_base_proyecto y self.archivo_config_nombre
        # Y llamará a self._forzar_creacion_perfil_default_y_guardar() si es necesario
        logger.info(f"Intentando cargar perfiles de ataque desde: {self.archivo_config_nombre}", extra={"categoria_log": "log_attack_profile_manager"})
        try:
            ruta_completa_config = os.path.join(self.ruta_base_proyecto, self.archivo_config_nombre)
            with open(ruta_completa_config, 'r') as f:
                data_cargada = json.load(f)
                if isinstance(data_cargada, dict):
                    self.perfiles_de_ataque = data_cargada
                    logger.info(f"Perfiles de ataque cargados desde {self.archivo_config_nombre}", extra={"categoria_log": "log_attack_profile_manager"})
                    # Validar perfiles cargados
                    for nombre_perfil, perfil_data in list(self.perfiles_de_ataque.items()):
                        if not isinstance(perfil_data, dict):
                            logger.warning(f"Alerta: Perfil '{nombre_perfil}' en JSON no es un diccionario. Recreando por defecto.", extra={"categoria_log": "log_attack_profile_manager"})
                            self.perfiles_de_ataque[nombre_perfil] = self._crear_perfil_ataque_por_defecto(nombre_perfil)
                    # Asegurar que el perfil activo exista
                    if self.nombre_perfil_ataque_activo not in self.perfiles_de_ataque:
                        logger.warning(f"Perfil activo '{self.nombre_perfil_ataque_activo}' no encontrado en el archivo. Intentando usar el predeterminado.", extra={"categoria_log": "log_attack_profile_manager"})
                        if self.nombre_perfil_inicial_predeterminado in self.perfiles_de_ataque:
                            self.nombre_perfil_ataque_activo = self.nombre_perfil_inicial_predeterminado
                        elif self.perfiles_de_ataque: # Si el inicial tampoco, tomar el primero disponible
                            self.nombre_perfil_ataque_activo = next(iter(self.perfiles_de_ataque))
                            logger.info(f"Usando el primer perfil disponible como activo: {self.nombre_perfil_ataque_activo}", extra={"categoria_log": "log_attack_profile_manager"})
                        else: # No hay perfiles, forzar creación del default.
                            logger.warning(f"No hay perfiles válidos tras la carga. Forzando creación del perfil por defecto.", extra={"categoria_log": "log_attack_profile_manager"})
                            self._forzar_creacion_perfil_default_y_guardar() # Esto también setea nombre_perfil_ataque_activo
                else:
                    logger.warning(f"Error: '{self.archivo_config_nombre}' no contiene un diccionario de perfiles. Creando estructura por defecto.", extra={"categoria_log": "log_attack_profile_manager"})
                    self._forzar_creacion_perfil_default_y_guardar()
        except FileNotFoundError:
            logger.warning(f"Archivo '{self.archivo_config_nombre}' no encontrado. Creando perfil por defecto.", extra={"categoria_log": "log_attack_profile_manager"})
            self._forzar_creacion_perfil_default_y_guardar()
        except json.JSONDecodeError:
            logger.warning(f"Error JSON en '{self.archivo_config_nombre}'. Creando perfil por defecto.", extra={"categoria_log": "log_attack_profile_manager"})
            self._forzar_creacion_perfil_default_y_guardar()
        except Exception as e:
            logger.error(f"Error cargando perfiles: {e}. Creando perfil por defecto.", extra={"categoria_log": "log_attack_profile_manager"})
            self._forzar_creacion_perfil_default_y_guardar()

    def _forzar_creacion_perfil_default_y_guardar(self):
        # Esta función se moverá aquí desde Jugador
        logger.info(f"Forzando creación y guardado de perfil por defecto: {self.nombre_perfil_inicial_predeterminado}", extra={"categoria_log": "log_attack_profile_manager"})
        self.perfiles_de_ataque = {}
        self.perfiles_de_ataque[self.nombre_perfil_inicial_predeterminado] = self._crear_perfil_ataque_por_defecto(self.nombre_perfil_inicial_predeterminado)
        self.nombre_perfil_ataque_activo = self.nombre_perfil_inicial_predeterminado
        self.guardar_todos_perfiles_ataque() # Guardar inmediatamente

    def guardar_todos_perfiles_ataque(self):
        # Esta función se moverá aquí desde Jugador
        logger.info(f"Guardando todos los perfiles de ataque en: {self.archivo_config_nombre}", extra={"categoria_log": "log_attack_profile_manager"})
        try:
            ruta_completa_config = os.path.join(self.ruta_base_proyecto, self.archivo_config_nombre)
            with open(ruta_completa_config, 'w') as f:
                json.dump(self.perfiles_de_ataque, f, indent=4)
            logger.info(f"Todos los perfiles de ataque guardados en {self.archivo_config_nombre}", extra={"categoria_log": "log_attack_profile_manager"})
        except Exception as e:
            logger.error(f"Error al guardar todos los perfiles de ataque: {e}", extra={"categoria_log": "log_attack_profile_manager"})

    def seleccionar_perfil_ataque(self, nombre_perfil_solicitado):
        # Esta función se moverá aquí desde Jugador
        # Actualizará self.nombre_perfil_ataque_activo, 
        # self._num_segmentos_barrido_activo, self._duracion_segmento_barrido_activo
        logger.debug(f"Intento de seleccionar perfil de ataque: {nombre_perfil_solicitado}", extra={"categoria_log": "log_attack_profile_manager"})
        perfil_original = self.nombre_perfil_ataque_activo

        if nombre_perfil_solicitado in self.perfiles_de_ataque and isinstance(self.perfiles_de_ataque[nombre_perfil_solicitado], dict):
            self.nombre_perfil_ataque_activo = nombre_perfil_solicitado
            perfil_activo_data = self.perfiles_de_ataque[self.nombre_perfil_ataque_activo]
            
            plantilla = perfil_activo_data.get("plantilla_angulos_grados", [0])
            if not isinstance(plantilla, list) or not plantilla: plantilla = [0] # Asegurar que no sea lista vacía
            self._num_segmentos_barrido_activo = len(plantilla)
            
            duracion_total = perfil_activo_data.get("duracion_total_ms", 100)
            if not isinstance(duracion_total, (int, float)) or duracion_total <= 0: duracion_total = 100
            
            if self._num_segmentos_barrido_activo > 0 and duracion_total > 0:
                self._duracion_segmento_barrido_activo = duracion_total / self._num_segmentos_barrido_activo
            else:
                self._duracion_segmento_barrido_activo = 0
                if self._num_segmentos_barrido_activo == 0: logger.warning("Num segmentos es 0, duracion_segmento será 0.", extra={"categoria_log": "log_attack_profile_manager"})

            logger.info(f"Perfil activo cambiado a: '{self.nombre_perfil_ataque_activo}'. Dur seg: {self._duracion_segmento_barrido_activo:.2f}ms. Num_seg: {self._num_segmentos_barrido_activo}. Dur_total: {duracion_total}", extra={"categoria_log": "log_attack_profile_manager"})
            return True
        else:
            logger.error(f"Error: Perfil '{nombre_perfil_solicitado}' no encontrado o no es dict. Intentando fallback.", extra={"categoria_log": "log_attack_profile_manager"})
            # Lógica de fallback similar a la original de Jugador
            # Si el perfil solicitado no es el default, intentar el default
            if nombre_perfil_solicitado != self.nombre_perfil_inicial_predeterminado and \
               self.nombre_perfil_inicial_predeterminado in self.perfiles_de_ataque and \
               isinstance(self.perfiles_de_ataque.get(self.nombre_perfil_inicial_predeterminado), dict):
                logger.info(f"Fallback al perfil por defecto: {self.nombre_perfil_inicial_predeterminado}", extra={"categoria_log": "log_attack_profile_manager"})
                return self.seleccionar_perfil_ataque(self.nombre_perfil_inicial_predeterminado) # Llamada recursiva segura

            # Si eso falla, intentar el primer perfil válido que no sea el solicitado (si hay otros)
            primer_otro_perfil_valido = next((n for n, p in self.perfiles_de_ataque.items() if isinstance(p, dict) and n != nombre_perfil_solicitado), None)
            if primer_otro_perfil_valido:
                logger.info(f"Fallback al primer otro perfil válido encontrado: {primer_otro_perfil_valido}", extra={"categoria_log": "log_attack_profile_manager"})
                return self.seleccionar_perfil_ataque(primer_otro_perfil_valido) # Llamada recursiva segura
            
            # Si todo falla, forzar creación del default y seleccionarlo.
            # (Solo si el perfil activo actual no es válido o no existe)
            # Esto evita bucles si _forzar_creacion ya fue llamado y falló en crear algo seleccionable.
            if not (self.nombre_perfil_ataque_activo in self.perfiles_de_ataque and isinstance(self.perfiles_de_ataque[self.nombre_perfil_ataque_activo], dict)):
                logger.warning("Ningún perfil válido disponible. Forzando recreación del perfil por defecto y seleccionándolo.", extra={"categoria_log": "log_attack_profile_manager"})
                self._forzar_creacion_perfil_default_y_guardar() # Esto setea nombre_perfil_activo y guarda
                # Después de forzar, el perfil predeterminado DEBERÍA existir.
                if self.nombre_perfil_inicial_predeterminado in self.perfiles_de_ataque:
                    return self.seleccionar_perfil_ataque(self.nombre_perfil_inicial_predeterminado)
            
            logger.critical(f"CRÍTICO: No se pudo seleccionar un perfil válido ('{nombre_perfil_solicitado}' intentado) incluso después de intentar fallbacks y forzar creación. Perfil activo actual: '{self.nombre_perfil_ataque_activo}'", extra={"categoria_log": "log_attack_profile_manager"})
            return False


    def get_parametro_ataque_activo(self, nombre_parametro, valor_defecto=None):
        # Esta función se moverá aquí desde Jugador
        perfil = self.perfiles_de_ataque.get(self.nombre_perfil_ataque_activo)
        if isinstance(perfil, dict):
            return perfil.get(nombre_parametro, valor_defecto)
        logger.warning(f"Perfil activo '{self.nombre_perfil_ataque_activo}' no encontrado o no es dict al obtener '{nombre_parametro}'. Usando valor por defecto.", extra={"categoria_log": "log_attack_profile_manager"})
        return valor_defecto

    def set_parametro_ataque_activo(self, nombre_parametro, valor):
        # Esta función se moverá aquí desde Jugador
        perfil = self.perfiles_de_ataque.get(self.nombre_perfil_ataque_activo)
        if isinstance(perfil, dict):
            perfil[nombre_parametro] = valor
            logger.debug(f"Parámetro '{nombre_parametro}' seteado a '{valor}' en perfil '{self.nombre_perfil_ataque_activo}'", extra={"categoria_log": "log_attack_profile_manager"})
            # Si se cambian parámetros que afectan la estructura del barrido, recalcularlos
            if nombre_parametro == "duracion_total_ms" or nombre_parametro == "plantilla_angulos_grados":
                logger.info(f"Parámetro clave '{nombre_parametro}' modificado. Reseleccionando perfil para recalcular derivados.", extra={"categoria_log": "log_attack_profile_manager"})
                self.seleccionar_perfil_ataque(self.nombre_perfil_ataque_activo) # Recalcular duraciones de segmento, etc.
        else:
            logger.warning(f"Advertencia (set_parametro): No se pudo setear '{nombre_parametro}' en perfil '{self.nombre_perfil_ataque_activo}'. Perfil no encontrado o no es dict.", extra={"categoria_log": "log_attack_profile_manager"})

    # Métodos de modificación directa de parámetros (usados por DEBUG F-keys)
    def modificar_ataque_offset(self, cantidad):
        actual = self.get_parametro_ataque_activo("offset_distancia", 0)
        nuevo = max(0, float(actual) + float(cantidad))
        self.set_parametro_ataque_activo("offset_distancia", nuevo)
        logger.debug(f"Perfil '{self.nombre_perfil_ataque_activo}' - offset_distancia: {nuevo}", extra={"categoria_log": "log_attack_profile_manager"})

    def modificar_ataque_extension(self, cantidad):
        actual = self.get_parametro_ataque_activo("extension", 0)
        nuevo = max(0, float(actual) + float(cantidad))
        self.set_parametro_ataque_activo("extension", nuevo)
        logger.debug(f"Perfil '{self.nombre_perfil_ataque_activo}' - extension: {nuevo}", extra={"categoria_log": "log_attack_profile_manager"})

    def modificar_ataque_grosor(self, cantidad):
        actual = self.get_parametro_ataque_activo("grosor", 0)
        nuevo = max(1, float(actual) + float(cantidad)) # Grosor mínimo de 1
        self.set_parametro_ataque_activo("grosor", nuevo)
        logger.debug(f"Perfil '{self.nombre_perfil_ataque_activo}' - grosor: {nuevo}", extra={"categoria_log": "log_attack_profile_manager"})

    def modificar_duracion_ataque_total(self, cantidad):
        actual = self.get_parametro_ataque_activo("duracion_total_ms", 100)
        nuevo = max(10, float(actual) + float(cantidad)) # Duración mínima de 10ms
        self.set_parametro_ataque_activo("duracion_total_ms", nuevo)
        logger.debug(f"Perfil '{self.nombre_perfil_ataque_activo}' - duracion_total_ms: {nuevo}", extra={"categoria_log": "log_attack_profile_manager"})
        # Este cambio requiere recalcular segmentos, set_parametro_ataque_activo ya lo hace

    def get_nombres_perfiles_disponibles(self):
        return list(self.perfiles_de_ataque.keys()) 