import pygame
import math
import logging
from typing import Tuple, List, Optional, Union, Dict, Any
import json
import os

logger = logging.getLogger(__name__)

def calcular_distancia(punto1: Tuple[float, float], punto2: Tuple[float, float]) -> float:
    """Calcula la distancia euclidiana entre dos puntos."""
    return math.sqrt((punto2[0] - punto1[0])**2 + (punto2[1] - punto1[1])**2)

def normalizar_vector(vector: Tuple[float, float]) -> Tuple[float, float]:
    """Normaliza un vector 2D a longitud 1."""
    magnitud = math.sqrt(vector[0]**2 + vector[1]**2)
    if magnitud == 0:
        return (0, 0)
    return (vector[0]/magnitud, vector[1]/magnitud)

def rotar_punto(punto: Tuple[float, float], centro: Tuple[float, float], angulo_grados: float) -> Tuple[float, float]:
    """Rota un punto alrededor de un centro por un ángulo en grados."""
    angulo_rad = math.radians(angulo_grados)
    x = punto[0] - centro[0]
    y = punto[1] - centro[1]
    x_rot = x * math.cos(angulo_rad) - y * math.sin(angulo_rad)
    y_rot = x * math.sin(angulo_rad) + y * math.cos(angulo_rad)
    return (x_rot + centro[0], y_rot + centro[1])

def crear_superficie_con_alpha(ancho: int, alto: int, color: Tuple[int, int, int, int]) -> pygame.Surface:
    """Crea una superficie con canal alpha."""
    superficie = pygame.Surface((ancho, alto), pygame.SRCALPHA)
    superficie.fill(color)
    return superficie

def interpolar_color(color1: Tuple[int, int, int], color2: Tuple[int, int, int], factor: float) -> Tuple[int, int, int]:
    """Interpola entre dos colores RGB basado en un factor (0-1)."""
    return tuple(int(c1 + (c2 - c1) * factor) for c1, c2 in zip(color1, color2))

def clamp(valor: float, minimo: float, maximo: float) -> float:
    """Asegura que un valor esté dentro de un rango."""
    return max(minimo, min(valor, maximo))

def debug_dibujar_rect(superficie: pygame.Surface, rect: pygame.Rect, color: Tuple[int, int, int], grosor: int = 1):
    """Dibuja un rectángulo para debug."""
    pygame.draw.rect(superficie, color, rect, grosor)

def debug_dibujar_circulo(superficie: pygame.Surface, centro: Tuple[float, float], radio: float, color: Tuple[int, int, int], grosor: int = 1):
    """Dibuja un círculo para debug."""
    pygame.draw.circle(superficie, color, (int(centro[0]), int(centro[1])), int(radio), grosor)

def debug_dibujar_linea(superficie: pygame.Surface, inicio: Tuple[float, float], fin: Tuple[float, float], color: Tuple[int, int, int], grosor: int = 1):
    """Dibuja una línea para debug."""
    pygame.draw.line(superficie, color, inicio, fin, grosor)

def debug_log_rect(rect: pygame.Rect, nombre: str = "Rect"):
    """Loggea información de un rectángulo para debug."""
    logger.debug(f"{nombre}: x={rect.x}, y={rect.y}, w={rect.width}, h={rect.height}")

def debug_log_vector(vector: Tuple[float, float], nombre: str = "Vector"):
    """Loggea información de un vector para debug."""
    logger.debug(f"{nombre}: x={vector[0]}, y={vector[1]}")

def interpolar_valor(valor_inicial: float, valor_final: float, factor: float) -> float:
    """Interpola linealmente entre dos valores basado en un factor (0-1)."""
    return valor_inicial + (valor_final - valor_inicial) * factor

def calcular_angulo_entre_puntos(punto1: Tuple[float, float], punto2: Tuple[float, float]) -> float:
    """Calcula el ángulo en grados entre dos puntos."""
    return math.degrees(math.atan2(punto2[1] - punto1[1], punto2[0] - punto1[0]))

def calcular_velocidad_por_angulo(velocidad: float, angulo_grados: float) -> Tuple[float, float]:
    """Calcula las componentes x,y de una velocidad basada en un ángulo."""
    angulo_rad = math.radians(angulo_grados)
    return (velocidad * math.cos(angulo_rad), velocidad * math.sin(angulo_rad))

def cargar_json(ruta: str) -> Dict[str, Any]:
    """Carga un archivo JSON y retorna su contenido como diccionario."""
    try:
        with open(ruta, 'r', encoding='utf-8') as archivo:
            return json.load(archivo)
    except Exception as e:
        logger.error(f"Error al cargar JSON {ruta}: {e}")
        return {}

def guardar_json(datos: Dict[str, Any], ruta: str) -> bool:
    """Guarda un diccionario en un archivo JSON."""
    try:
        with open(ruta, 'w', encoding='utf-8') as archivo:
            json.dump(datos, archivo, indent=4)
        return True
    except Exception as e:
        logger.error(f"Error al guardar JSON {ruta}: {e}")
        return False

def rectangulos_colisionan(rect1: pygame.Rect, rect2: pygame.Rect) -> bool:
    """Verifica si dos rectángulos colisionan."""
    return rect1.colliderect(rect2)

def punto_en_rectangulo(punto: Tuple[float, float], rect: pygame.Rect) -> bool:
    """Verifica si un punto está dentro de un rectángulo."""
    return rect.collidepoint(punto)

def circulo_colisiona_rectangulo(
    centro: Tuple[float, float],
    radio: float,
    rect: pygame.Rect
) -> bool:
    """Verifica si un círculo colisiona con un rectángulo."""
    # Encontrar el punto más cercano en el rectángulo al centro del círculo
    x = max(rect.left, min(centro[0], rect.right))
    y = max(rect.top, min(centro[1], rect.bottom))
    
    # Calcular la distancia entre el punto más cercano y el centro del círculo
    distancia = calcular_distancia((x, y), centro)
    
    return distancia <= radio

def crear_superficie_con_borde(
    ancho: int,
    alto: int,
    color_fondo: Tuple[int, int, int, int],
    color_borde: Tuple[int, int, int, int],
    grosor_borde: int = 1
) -> pygame.Surface:
    """Crea una superficie con fondo y borde."""
    superficie = crear_superficie_con_alpha(ancho, alto, color_fondo)
    pygame.draw.rect(superficie, color_borde, superficie.get_rect(), grosor_borde)
    return superficie

def dibujar_texto_con_sombra(
    superficie: pygame.Surface,
    texto: str,
    fuente: pygame.font.Font,
    color: Tuple[int, int, int],
    posicion: Tuple[int, int],
    offset_sombra: int = 2,
    color_sombra: Tuple[int, int, int] = (0, 0, 0)
) -> None:
    """Dibuja texto con sombra para mejor legibilidad."""
    texto_sombra = fuente.render(texto, True, color_sombra)
    texto_normal = fuente.render(texto, True, color)
    
    superficie.blit(texto_sombra, (posicion[0] + offset_sombra, posicion[1] + offset_sombra))
    superficie.blit(texto_normal, posicion)

def debug_dibujar_poligono(
    superficie: pygame.Surface,
    puntos: List[Tuple[float, float]],
    color: Tuple[int, int, int],
    grosor: int = 1
) -> None:
    """Dibuja un polígono para debug."""
    if len(puntos) < 3:
        return
    pygame.draw.polygon(superficie, color, puntos, grosor)

def debug_dibujar_texto(
    superficie: pygame.Surface,
    texto: str,
    posicion: Tuple[int, int],
    color: Tuple[int, int, int] = (255, 255, 255),
    tamano: int = 16
) -> None:
    """Dibuja texto de debug en la pantalla."""
    fuente = pygame.font.Font(None, tamano)
    texto_surface = fuente.render(texto, True, color)
    superficie.blit(texto_surface, posicion)

def debug_log_estado(estado: str, detalles: Dict[str, Any] = None) -> None:
    """Loggea el estado actual de una entidad o sistema."""
    mensaje = f"Estado: {estado}"
    if detalles:
        mensaje += f" - Detalles: {detalles}"
    logger.debug(mensaje)

def asegurar_directorio(ruta: str) -> bool:
    """Asegura que un directorio existe, creándolo si es necesario."""
    try:
        os.makedirs(ruta, exist_ok=True)
        return True
    except Exception as e:
        logger.error(f"Error al crear directorio {ruta}: {e}")
        return False

def obtener_tiempo_actual() -> float:
    """Retorna el tiempo actual en segundos."""
    return pygame.time.get_ticks() / 1000.0

def formatear_tiempo(segundos: float) -> str:
    """Formatea segundos en formato MM:SS."""
    minutos = int(segundos // 60)
    segundos = int(segundos % 60)
    return f"{minutos:02d}:{segundos:02d}" 