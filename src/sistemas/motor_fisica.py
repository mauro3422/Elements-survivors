import pygame
import logging
from src.config import settings

# Constantes de física (podrían moverse a settings.py si son globales)
# Por ahora, ejemplos locales:

logger = logging.getLogger("motor_fisica")

class MotorFisica:
    """
    Gestiona cálculos relacionados con la física del juego, como empujes,
    fuerzas y movimiento basado en vectores.
    """

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

    # Aquí podrían ir más funciones:
    # - aplicar_friccion(vector_movimiento, coeficiente_friccion)
    # - calcular_impacto_con_masa(vector_fuerza, masa_objeto_1, masa_objeto_2)
    # - etc.

if __name__ == '__main__':
    # Pequeña prueba (esto no se ejecutará en el juego, solo para testing directo del módulo)
    v_origen = pygame.math.Vector2(0, 0)
    v_destino = pygame.math.Vector2(10, 0) # Empuje hacia la derecha
    magnitud = 5.0

    empuje = MotorFisica.calcular_vector_empuje_simple(v_origen, v_destino, magnitud)
    print(f"Origen: {v_origen}, Destino: {v_destino}, Magnitud: {magnitud} -> Empuje: {empuje} (Longitud: {empuje.length()})")

    v_destino_2 = pygame.math.Vector2(0, 5) # Empuje hacia abajo
    empuje_2 = MotorFisica.calcular_vector_empuje_simple(v_origen, v_destino_2, magnitud)
    print(f"Origen: {v_origen}, Destino: {v_destino_2}, Magnitud: {magnitud} -> Empuje_2: {empuje_2} (Longitud: {empuje_2.length()})")

    v_destino_3 = pygame.math.Vector2(3, 4) # Empuje diagonal (vector 3,4 tiene longitud 5)
    empuje_3 = MotorFisica.calcular_vector_empuje_simple(v_origen, v_destino_3, magnitud)
    print(f"Origen: {v_origen}, Destino: {v_destino_3}, Magnitud: {magnitud} -> Empuje_3: {empuje_3} (Longitud: {empuje_3.length()})")
    
    v_destino_igual = pygame.math.Vector2(0,0)
    empuje_igual = MotorFisica.calcular_vector_empuje_simple(v_origen, v_destino_igual, magnitud)
    print(f"Origen: {v_origen}, Destino: {v_destino_igual}, Magnitud: {magnitud} -> Empuje_Igual: {empuje_igual}") 