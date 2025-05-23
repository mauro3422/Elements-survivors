import pygame
import logging
from src.config import settings

# Constantes de física (podrían moverse a settings.py si son globales)
# Por ahora, ejemplos locales:

logger = logging.getLogger("motor_fisica")

class MotorFisica:
    """
    Gestiona cálculos relacionados con la física del juego, como empujes,
    fuerzas y movimiento basado en vectores. Puede ser instanciado por entidad
    para manejar fuerzas persistentes como empujes con fricción.
    """

    def __init__(self, factor_friccion=None, umbral_fuerza_minima=None, nombre_entidad_log="[MOTOR_FISICA_GENERICO]"):
        self.fuerzas_acumuladas = pygame.math.Vector2(0, 0)
        
        self.factor_friccion = factor_friccion if factor_friccion is not None else getattr(settings, "FACTOR_FRICCION_GENERICO", 0.85)
        self.umbral_fuerza_minima = umbral_fuerza_minima if umbral_fuerza_minima is not None else getattr(settings, "UMBRAL_FUERZA_MINIMA_GENERICO", 0.5)
        self.nombre_entidad_log = nombre_entidad_log

        if settings.MODO_DEBUG_LOGS and settings.LOG_CATEGORIAS.get("log_motor_fisica", False):
            logger.debug(f"{self.nombre_entidad_log} MotorFisica instanciado. Fricción: {self.factor_friccion}, Umbral: {self.umbral_fuerza_minima}", extra={"categoria_log": "log_motor_fisica"})

    def agregar_fuerza(self, vector_fuerza: pygame.math.Vector2):
        if not isinstance(vector_fuerza, pygame.math.Vector2):
            if settings.MODO_DEBUG_LOGS and settings.LOG_CATEGORIAS.get("log_motor_fisica", False):
                logger.warning(f"{self.nombre_entidad_log} Intento de agregar fuerza NO VÁLIDA (no es Vector2): {vector_fuerza}", extra={"categoria_log": "log_motor_fisica"})
            return
        
        if vector_fuerza.length_squared() == 0:
             # No loguear como warning si es cero, podría ser intencional para "cancelar"
            if settings.MODO_DEBUG_LOGS and settings.LOG_CATEGORIAS.get("log_motor_fisica_verbose", False): # Usar categoría verbose
                 logger.debug(f"{self.nombre_entidad_log} Intento de agregar fuerza CERO. No se acumula. Vector: {vector_fuerza}", extra={"categoria_log": "log_motor_fisica_verbose"})
            return

        self.fuerzas_acumuladas += vector_fuerza
        if settings.MODO_DEBUG_LOGS and settings.LOG_CATEGORIAS.get("log_motor_fisica", False):
            logger.debug(f"{self.nombre_entidad_log} Fuerza agregada: {vector_fuerza}. Acumulado ahora: {self.fuerzas_acumuladas}", extra={"categoria_log": "log_motor_fisica"})

    def actualizar_estado_fuerzas(self, delta_time): # delta_time no se usa aquí pero podría en el futuro si la fricción depende del tiempo
        self.fuerzas_acumuladas *= self.factor_friccion
        if self.fuerzas_acumuladas.length_squared() < self.umbral_fuerza_minima**2:
            if self.fuerzas_acumuladas.length_squared() > 0: # Log solo si realmente había algo que resetear
                if settings.MODO_DEBUG_LOGS and settings.LOG_CATEGORIAS.get("log_motor_fisica", False):
                    logger.debug(f"{self.nombre_entidad_log} Fuerzas acumuladas ({self.fuerzas_acumuladas}) por debajo del umbral. Reseteando a (0,0).", extra={"categoria_log": "log_motor_fisica"})
            self.fuerzas_acumuladas.xy = (0, 0)

    def get_vector_movimiento_resultante_del_frame(self, delta_time):
        """Devuelve el vector de movimiento (desplazamiento) para este frame basado en las fuerzas acumuladas."""
        # Asumimos que fuerzas_acumuladas representa una "velocidad de empuje"
        return self.fuerzas_acumuladas * delta_time
        
    def resetear_fuerzas(self):
        self.fuerzas_acumuladas.xy = (0,0)
        if settings.MODO_DEBUG_LOGS and settings.LOG_CATEGORIAS.get("log_motor_fisica", False):
            logger.debug(f"{self.nombre_entidad_log} Fuerzas reseteadas explícitamente.", extra={"categoria_log": "log_motor_fisica"})

    def tiene_fuerzas_activas(self):
        return self.fuerzas_acumuladas.length_squared() > 0

    @staticmethod
    def calcular_vector_empuje_simple(origen_pos_center: pygame.math.Vector2, 
                                      destino_pos_center: pygame.math.Vector2, 
                                      fuerza_magnitud: float) -> pygame.math.Vector2:
        """
        Calcula un vector de empuje simple desde una posición de origen hacia una de destino.

        Args:
            origen_pos_center: pygame.math.Vector2 del centro de la entidad que empuja.
            destino_pos_center: pygame.math.Vector2 del centro de la entidad empujada.
            fuerza_magnitud: La magnitud de la fuerza de empuje.

        Returns:
            pygame.math.Vector2: El vector de empuje. Devuelve Vector2(0,0) si origen y destino son iguales.
        """
        if origen_pos_center == destino_pos_center:
            return pygame.math.Vector2(0, 0) # No hay dirección si las posiciones son iguales

        direccion_vector = destino_pos_center - origen_pos_center
        
        if settings.MODO_DEBUG_LOGS and settings.LOG_CATEGORIAS.get("log_motor_fisica", False):
            logger.debug(f"MF_CVE: Origen={origen_pos_center}, Destino={destino_pos_center}, Mag_entrada={fuerza_magnitud}", extra={"categoria_log": "log_motor_fisica"})
            logger.debug(f"MF_CVE: Direccion_vector_no_norm={direccion_vector} (Longitud: {direccion_vector.length() if direccion_vector.length_squared() > 0 else 0.0:.4f})", extra={"categoria_log": "log_motor_fisica"})

        # Normalizar para obtener solo la dirección, luego aplicar magnitud
        if direccion_vector.length_squared() > 0: # Evitar división por cero si el vector es nulo (aunque ya lo chequeamos arriba)
            direccion_normalizada = direccion_vector.normalize()
            vector_empuje = direccion_normalizada * fuerza_magnitud
            if settings.MODO_DEBUG_LOGS and settings.LOG_CATEGORIAS.get("log_motor_fisica", False):
                logger.debug(f"MF_CVE: Direccion_normalizada={direccion_normalizada}, Vector_empuje_FINAL={vector_empuje}", extra={"categoria_log": "log_motor_fisica"})
            return vector_empuje
        else:
            if settings.MODO_DEBUG_LOGS and settings.LOG_CATEGORIAS.get("log_motor_fisica", False):
                logger.warning("MF_CVE: Direccion_vector con longitud cero inesperadamente. Retornando (0,0).", extra={"categoria_log": "log_motor_fisica"})
            return pygame.math.Vector2(0, 0)

    # Aquí podrían ir más funciones estáticas o métodos de instancia:
    # - aplicar_friccion(vector_movimiento, coeficiente_friccion) # Ahora es parte de actualizar_estado_fuerzas
    # - calcular_impacto_con_masa(vector_fuerza, masa_objeto_1, masa_objeto_2)
    # - etc.

if __name__ == '__main__':
    # Pequeña prueba (esto no se ejecutará en el juego, solo para testing directo del módulo)
    
    # Simulación de settings para prueba
    class SettingsMock:
        MODO_DEBUG_LOGS = True
        LOG_CATEGORIAS = {
            "log_motor_fisica": True,
            "log_motor_fisica_verbose": True
        }
        FACTOR_FRICCION_GENERICO = 0.9
        UMBRAL_FUERZA_MINIMA_GENERICO = 0.1
    
    # Aplicar el mock a settings para que el logger lo use
    original_settings = settings 
    settings = SettingsMock()

    # Configurar logging básico si no está configurado
    if not logging.getLogger().hasHandlers():
        logging.basicConfig(level=logging.DEBUG)

    # Pruebas del método estático
    v_origen = pygame.math.Vector2(0, 0)
    v_destino = pygame.math.Vector2(10, 0) # Empuje hacia la derecha
    magnitud = 5.0

    empuje = MotorFisica.calcular_vector_empuje_simple(v_origen, v_destino, magnitud)
    print(f"Estático - Origen: {v_origen}, Destino: {v_destino}, Magnitud: {magnitud} -> Empuje: {empuje} (Longitud: {empuje.length()})")

    # Pruebas de la instancia
    mf_instance = MotorFisica(factor_friccion=0.8, umbral_fuerza_minima=0.5, nombre_entidad_log="[TEST_MF]")
    print(f"Instancia creada: {mf_instance.fuerzas_acumuladas}")

    fuerza_1 = pygame.math.Vector2(10, 0)
    mf_instance.agregar_fuerza(fuerza_1)
    print(f"Después de agregar {fuerza_1}: {mf_instance.fuerzas_acumuladas}")

    # Simular algunos frames
    for i in range(5):
        mf_instance.actualizar_estado_fuerzas(delta_time=0.1) # delta_time no usado aún pero buen hábito pasarlo
        mov_resultante = mf_instance.get_vector_movimiento_resultante_del_frame(delta_time=0.1)
        print(f"Frame {i+1}: Fuerzas acum: {mf_instance.fuerzas_acumuladas}, Mov result: {mov_resultante}")
        if not mf_instance.tiene_fuerzas_activas():
            print(f"Fuerzas inactivas en frame {i+1}. Deteniendo simulación.")
            break
    
    mf_instance.resetear_fuerzas()
    print(f"Después de reset: {mf_instance.fuerzas_acumuladas}")

    # Restaurar settings originales si es necesario para otras pruebas en el mismo entorno
    settings = original_settings 