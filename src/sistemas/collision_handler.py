import pygame
import logging
from src.config import settings # MODIFICADO: Importación de settings actualizada
from typing import TYPE_CHECKING # <--- AÑADIR IMPORT

# # --- IMPORTACIONES MOVIDAS TEMPORALMENTE PARA DEBUG (REVERTIDAS) ---
# from src.entidades.jugador import Jugador 
# from src.entidades.enemigo import Enemigo
# # --- FIN IMPORTACIONES MOVIDAS ---

# Ya no importamos Jugador y Enemigo aquí en el ámbito global para evitar el ciclo
# if TYPE_CHECKING: # Se usaría si tuviéramos anotaciones de tipo que los necesitaran globalmente
#     from src.entidades.jugador import Jugador
#     from src.entidades.enemigo import Enemigo

# Cambiar nombre del logger y eliminar setLevel
# logger_ch = logging.getLogger("log_collision_handler")
# logger_ch.setLevel(logging.DEBUG)
logger = logging.getLogger("collision_handler")

class CollisionHandler:
    def __init__(self): # Método __init__ añadido
        pass

    def _check_touch_or_overlap(self, r1, r2, eje):
        """
        Verifica si dos rectángulos se tocan o se solapan.
        Para el eje principal de verificación, usa <= y >= para incluir el contacto de bordes.
        Para el eje secundario, usa <= y >= para asegurar un solapamiento/contacto en ese eje.
        """
        if eje == 'x':
            # Verifica solapamiento/contacto en X, y solapamiento/contacto en Y
            return (r1.left <= r2.right and r1.right >= r2.left and
                    r1.top <= r2.bottom and r1.bottom >= r2.top)
        elif eje == 'y':
            # Verifica solapamiento/contacto en Y, y solapamiento/contacto en X
            return (r1.top <= r2.bottom and r1.bottom >= r2.top and
                    r1.left <= r2.right and r1.right >= r2.left)
        return False # Eje no válido

    def _resolver_solapamientos_estaticos_eje(self, entidad_actual, entidad_hitbox, obstaculos, eje, movimiento_input_en_eje):
        # --- IMPORTACIONES LOCALES PARA EVITAR CICLOS (RESTAURADAS) ---
        from src.entidades.jugador import Jugador
        from src.entidades.enemigo import Enemigo
        # --- FIN IMPORTACIONES LOCALES ---

        ent_name_for_print = getattr(entidad_actual, 'nombre_log_entidad', type(entidad_actual).__name__)
        
        log_habilitado = settings.MODO_DEBUG_LOGS and settings.LOG_CATEGORIAS.get("log_collision_handler", False)
        log_detalle_habilitado = settings.MODO_DEBUG_LOGS and settings.LOG_CATEGORIAS.get("log_collision_handler_detalle", False)

        if log_detalle_habilitado: # Print convertido a log
            logger.debug(f"RSE: Entrando para: {ent_name_for_print}, Eje: {eje}, Input: {movimiento_input_en_eje:.2f}, HB_Inicial: {entidad_hitbox.topleft}", extra={"categoria_log": "log_collision_handler_detalle"})

        es_jugador_actual = isinstance(entidad_actual, Jugador)
        # Constante corregida
        input_actual_en_eje_es_cero = (abs(movimiento_input_en_eje) < settings.UMBRAL_MOV_FLOTANTE_ENTIDAD_PARA_COLISION)
        
        for pasada in range(settings.MAX_PASADAS_RESOLUCION_ESTATICA):
            colision_resuelta_en_pasada = False
            if log_detalle_habilitado: # Print convertido a log
                logger.debug(f"RSE ({ent_name_for_print}, Eje: {eje}): --- INICIO Pasada {pasada + 1} --- HB_Actual: {entidad_hitbox.topleft}", extra={"categoria_log": "log_collision_handler_detalle"})

            for obstaculo in obstaculos:
                if obstaculo == entidad_actual: 
                    continue
            
                rect_colision_obstaculo = obstaculo.hitbox if hasattr(obstaculo, 'hitbox') else obstaculo.rect
                obst_id_log = getattr(obstaculo, 'nombre_log_entidad', type(obstaculo).__name__)
                
                if log_detalle_habilitado: # Print convertido a log
                    logger.debug(f"RSE ({ent_name_for_print}): Verificando Obst: {obst_id_log} (HB_Obs: {rect_colision_obstaculo.topleft}, Size: {rect_colision_obstaculo.size}) vs HB_Ent: {entidad_hitbox.topleft}", extra={"categoria_log": "log_collision_handler_detalle"})
                
                colisiona_general = entidad_hitbox.colliderect(rect_colision_obstaculo)

                if not colisiona_general:
                    if log_detalle_habilitado: # Print convertido a log
                        logger.debug(f"RSE ({ent_name_for_print}): NO colisión general con {obst_id_log}. Continuando.", extra={"categoria_log": "log_collision_handler_detalle"})
                    continue

                if log_habilitado: # Print convertido a log (usando log_habilitado para info un poco menos verbosa)
                    logger.debug(f"RSE ({ent_name_for_print}): SÍ colisión con {obst_id_log}. HB_Ent: {entidad_hitbox.topleft}, HB_Obs: {rect_colision_obstaculo.topleft}, MovInputEje: {movimiento_input_en_eje:.2f}", extra={"categoria_log": "log_collision_handler"})

                x_antes = entidad_hitbox.x
                y_antes = entidad_hitbox.y
                hitbox_modificado_este_obstaculo = False
                if log_detalle_habilitado: # Print convertido a log
                    logger.debug(f"RSE ({ent_name_for_print} vs {obst_id_log}): HB_Ent_Antes_Ajuste: ({x_antes},{y_antes})", extra={"categoria_log": "log_collision_handler_detalle"})

                if eje == 'x':
                    if movimiento_input_en_eje > 0: 
                        if rect_colision_obstaculo.centerx > entidad_hitbox.centerx: 
                            entidad_hitbox.right = rect_colision_obstaculo.left
                            if log_detalle_habilitado: # Print convertido a log
                                logger.debug(f"RSE_AJUSTE_X ({ent_name_for_print}): Mov DER, Obs DER. HB.right ({entidad_hitbox.right}) to Obs.left ({rect_colision_obstaculo.left})", extra={"categoria_log": "log_collision_handler_detalle"})
                    elif movimiento_input_en_eje < 0: 
                        if rect_colision_obstaculo.centerx < entidad_hitbox.centerx: 
                            entidad_hitbox.left = rect_colision_obstaculo.right
                            if log_detalle_habilitado: # Print convertido a log
                                logger.debug(f"RSE_AJUSTE_X ({ent_name_for_print}): Mov IZQ, Obs IZQ. HB.left ({entidad_hitbox.left}) to Obs.right ({rect_colision_obstaculo.right})", extra={"categoria_log": "log_collision_handler_detalle"})
                    else: # Movimiento CERO en X
                        if entidad_hitbox.centerx < rect_colision_obstaculo.centerx:
                            entidad_hitbox.right = rect_colision_obstaculo.left
                            if log_detalle_habilitado: # Print convertido a log
                                logger.debug(f"RSE_AJUSTE_X ({ent_name_for_print}): Mov CERO, Ent IZQ Obs. HB.right ({entidad_hitbox.right}) to Obs.left ({rect_colision_obstaculo.left})", extra={"categoria_log": "log_collision_handler_detalle"})
                        else: 
                            entidad_hitbox.left = rect_colision_obstaculo.right
                            if log_detalle_habilitado: # Print convertido a log
                                logger.debug(f"RSE_AJUSTE_X ({ent_name_for_print}): Mov CERO, Ent DER Obs. HB.left ({entidad_hitbox.left}) to Obs.right ({rect_colision_obstaculo.right})", extra={"categoria_log": "log_collision_handler_detalle"})
                    hitbox_modificado_este_obstaculo = (entidad_hitbox.x != x_antes)

                elif eje == 'y':
                    if movimiento_input_en_eje > 0: 
                        if rect_colision_obstaculo.centery > entidad_hitbox.centery: 
                            entidad_hitbox.bottom = rect_colision_obstaculo.top
                            if log_detalle_habilitado: # Print convertido a log
                                logger.debug(f"RSE_AJUSTE_Y ({ent_name_for_print}): Mov ABA, Obs ABA. HB.bottom ({entidad_hitbox.bottom}) to Obs.top ({rect_colision_obstaculo.top})", extra={"categoria_log": "log_collision_handler_detalle"})
                    elif movimiento_input_en_eje < 0: 
                        if rect_colision_obstaculo.centery < entidad_hitbox.centery: 
                            entidad_hitbox.top = rect_colision_obstaculo.bottom
                            if log_detalle_habilitado: # Print convertido a log
                                logger.debug(f"RSE_AJUSTE_Y ({ent_name_for_print}): Mov ARR, Obs ARR. HB.top ({entidad_hitbox.top}) to Obs.bottom ({rect_colision_obstaculo.bottom})", extra={"categoria_log": "log_collision_handler_detalle"})
                    else: # Movimiento CERO en Y
                        if entidad_hitbox.centery < rect_colision_obstaculo.centery: 
                            entidad_hitbox.bottom = rect_colision_obstaculo.top
                            if log_detalle_habilitado: # Print convertido a log
                                logger.debug(f"RSE_AJUSTE_Y ({ent_name_for_print}): Mov CERO, Ent ARR Obs. HB.bottom ({entidad_hitbox.bottom}) to Obs.top ({rect_colision_obstaculo.top})", extra={"categoria_log": "log_collision_handler_detalle"})
                        else: 
                            entidad_hitbox.top = rect_colision_obstaculo.bottom
                            if log_detalle_habilitado: # Print convertido a log
                                logger.debug(f"RSE_AJUSTE_Y ({ent_name_for_print}): Mov CERO, Ent ABA Obs. HB.top ({entidad_hitbox.top}) to Obs.bottom ({rect_colision_obstaculo.bottom})", extra={"categoria_log": "log_collision_handler_detalle"})
                    hitbox_modificado_este_obstaculo = (entidad_hitbox.y != y_antes)

                if hitbox_modificado_este_obstaculo:
                    colision_resuelta_en_pasada = True
                if log_detalle_habilitado: # Print convertido a log
                    logger.debug(f"RSE ({ent_name_for_print} vs {obst_id_log}): HB_Ent_Modificado: {entidad_hitbox.topleft}", extra={"categoria_log": "log_collision_handler_detalle"})
            # Fin del bucle for obstaculo
            
            if log_detalle_habilitado: # Print convertido a log
                 logger.debug(f"RSE ({ent_name_for_print}, Eje: {eje}): --- FIN Pasada {pasada + 1} --- HB_Actual: {entidad_hitbox.topleft}, Resuelta: {colision_resuelta_en_pasada}", extra={"categoria_log": "log_collision_handler_detalle"})
            if not colision_resuelta_en_pasada:
                if log_detalle_habilitado: # Print convertido a log
                    logger.debug(f"RSE ({ent_name_for_print}, Eje: {eje}): No más mods en pasada. Break.", extra={"categoria_log": "log_collision_handler_detalle"})
                break
        # Fin del bucle for pasada

        if log_detalle_habilitado: # Print convertido a log
            logger.debug(f"RSE: Saliendo para: {ent_name_for_print}, Eje: {eje}, HB_Final: {entidad_hitbox.topleft}", extra={"categoria_log": "log_collision_handler_detalle"})

    def _aplicar_movimiento_y_colision_eje_x(self, entidad_hitbox, dx_aplicado, obstaculos, mundo_ancho, mundo_alto):
        log_habilitado = settings.MODO_DEBUG_LOGS and settings.LOG_CATEGORIAS.get("log_collision_handler", False)
        log_detalle_habilitado = settings.MODO_DEBUG_LOGS and settings.LOG_CATEGORIAS.get("log_collision_handler_detalle", False)
        
        if log_habilitado: # Print convertido a log
            logger.debug(f"AMCE_X: Entrando, dx_aplicado: {dx_aplicado:.2f}, HB_In: {entidad_hitbox.topleft}", extra={"categoria_log": "log_collision_handler"})

        dx_total_aplicado_al_hb_original = 0.0
        hb_temporal_eje_actual = entidad_hitbox.copy()
            
        if abs(dx_aplicado) < settings.UMBRAL_MOV_FLOTANTE_ENTIDAD_PARA_COLISION:
            if log_detalle_habilitado:
                logger.debug(f"AMCE_X: dx_aplicado ({dx_aplicado:.4f}) muy pequeño, no se aplica.", extra={"categoria_log": "log_collision_handler_detalle"})
            return dx_total_aplicado_al_hb_original

        paso_mov_truncado = int(dx_aplicado)
        dx_restante_flotante = dx_aplicado - paso_mov_truncado

        if log_detalle_habilitado:
            logger.debug(f"AMCE_X: dx_aplicado={dx_aplicado:.4f}. HB.x original={hb_temporal_eje_actual.x}, PasoTrunc={paso_mov_truncado}, RestoFloat={dx_restante_flotante:.4f}", extra={"categoria_log": "log_collision_handler_detalle"})

        if paso_mov_truncado != 0:
            dx_signo = 1 if paso_mov_truncado > 0 else -1
            for _ in range(abs(paso_mov_truncado)):
                hb_pos_anterior_al_paso = hb_temporal_eje_actual.x
                hb_temporal_eje_actual.x += dx_signo
                dx_total_aplicado_al_hb_original += dx_signo
                colision_en_este_paso = False

                if hb_temporal_eje_actual.left < 0:
                    hb_temporal_eje_actual.left = 0
                    dx_total_aplicado_al_hb_original = hb_temporal_eje_actual.left - entidad_hitbox.left
                    colision_en_este_paso = True
                    if log_detalle_habilitado: logger.debug(f"    AMCE_X_LIMITE_MUNDO: X Colisión con límite IZQUIERDO. HB.left ajustado a 0. Mov real hasta aquí: {dx_total_aplicado_al_hb_original}", extra={"categoria_log": "log_collision_handler_detalle"})
                elif hb_temporal_eje_actual.right > mundo_ancho:
                    hb_temporal_eje_actual.right = mundo_ancho
                    dx_total_aplicado_al_hb_original = hb_temporal_eje_actual.left - entidad_hitbox.left
                    colision_en_este_paso = True
                    if log_detalle_habilitado: logger.debug(f"    AMCE_X_LIMITE_MUNDO: X Colisión con límite DERECHO. HB.right ajustado a {mundo_ancho}. Mov real hasta aquí: {dx_total_aplicado_al_hb_original}", extra={"categoria_log": "log_collision_handler_detalle"})

                if not colision_en_este_paso:
                    for obstaculo in obstaculos:
                        rect_colision_obstaculo = obstaculo.hitbox if hasattr(obstaculo, 'hitbox') else obstaculo.rect
                        if hb_temporal_eje_actual.colliderect(rect_colision_obstaculo):
                            hb_temporal_eje_actual.x = hb_pos_anterior_al_paso
                            dx_total_aplicado_al_hb_original -= dx_signo
                            colision_en_este_paso = True
                            if log_detalle_habilitado: 
                                obst_id_log = getattr(obstaculo, 'nombre_log_entidad', type(obstaculo).__name__)
                                logger.debug(f"    AMCE_X_DETALLE: Fase 2 (X) Colisión PASO con {obst_id_log} en x={hb_temporal_eje_actual.x+dx_signo}. Revertido a x={hb_temporal_eje_actual.x}. Acumulado: {dx_total_aplicado_al_hb_original}", extra={"categoria_log": "log_collision_handler_detalle"})
                            break
                
                if colision_en_este_paso:
                    break

        if abs(dx_restante_flotante) >= settings.UMBRAL_MOV_FLOTANTE_ENTIDAD_PARA_COLISION:
            colision_despues_de_parte_entera = False
            for obstaculo in obstaculos:
                rect_colision_obstaculo = obstaculo.hitbox if hasattr(obstaculo, 'hitbox') else obstaculo.rect
                if hb_temporal_eje_actual.colliderect(rect_colision_obstaculo):
                    colision_despues_de_parte_entera = True
                    break 
        
            if hb_temporal_eje_actual.left <= 0 or hb_temporal_eje_actual.right >= mundo_ancho:
                colision_despues_de_parte_entera = True

            if not colision_despues_de_parte_entera:
                hb_pos_anterior_flotante = hb_temporal_eje_actual.x
                hb_temporal_eje_actual.x += dx_restante_flotante
                dx_total_aplicado_al_hb_original += dx_restante_flotante
                colision_parte_flotante = False

                if hb_temporal_eje_actual.left < 0:
                    hb_temporal_eje_actual.left = 0
                    dx_total_aplicado_al_hb_original = hb_temporal_eje_actual.left - entidad_hitbox.left
                    colision_parte_flotante = True
                    if log_detalle_habilitado: logger.debug(f"    AMCE_X_LIMITE_MUNDO_FLOAT: X Colisión FLOTANTE con límite IZQUIERDO. HB.left ajustado a 0.", extra={"categoria_log": "log_collision_handler_detalle"})
                elif hb_temporal_eje_actual.right > mundo_ancho:
                    hb_temporal_eje_actual.right = mundo_ancho
                    dx_total_aplicado_al_hb_original = hb_temporal_eje_actual.left - entidad_hitbox.left 
                    colision_parte_flotante = True
                    if log_detalle_habilitado: logger.debug(f"    AMCE_X_LIMITE_MUNDO_FLOAT: X Colisión FLOTANTE con límite DERECHO. HB.right ajustado a {mundo_ancho}. Mov real: {dx_total_aplicado_al_hb_original}", extra={"categoria_log": "log_collision_handler_detalle"})

                if not colision_parte_flotante:
                    for obstaculo in obstaculos:
                        rect_colision_obstaculo = obstaculo.hitbox if hasattr(obstaculo, 'hitbox') else obstaculo.rect
                        if hb_temporal_eje_actual.colliderect(rect_colision_obstaculo):
                            hb_temporal_eje_actual.x = hb_pos_anterior_flotante
                            dx_total_aplicado_al_hb_original -= dx_restante_flotante
                            colision_parte_flotante = True
                            if log_detalle_habilitado: 
                                obst_id_log = getattr(obstaculo, 'nombre_log_entidad', type(obstaculo).__name__)
                                logger.debug(f"    AMCE_X_DETALLE: Fase 2 (X) Colisión FLOTANTE con {obst_id_log} en x={hb_pos_anterior_flotante+dx_restante_flotante:.4f}. Revertido a x={hb_temporal_eje_actual.x:.4f}. Acumulado: {dx_total_aplicado_al_hb_original:.4f}", extra={"categoria_log": "log_collision_handler_detalle"})
                            break
                
                if colision_parte_flotante and log_detalle_habilitado:
                    logger.debug(f"    AMCE_X_DETALLE: Movimiento flotante ({dx_restante_flotante:.4f}) causó colisión y fue revertido o ajustado por límite.", extra={"categoria_log": "log_collision_handler_detalle"})
                elif log_detalle_habilitado:
                    logger.debug(f"    AMCE_X_DETALLE: Movimiento flotante ({dx_restante_flotante:.4f}) aplicado. HB.x post-float={hb_temporal_eje_actual.x:.4f}. Acumulado: {dx_total_aplicado_al_hb_original:.4f}", extra={"categoria_log": "log_collision_handler_detalle"})
            elif log_detalle_habilitado:
                 logger.debug(f"    AMCE_X_DETALLE: Movimiento flotante ({dx_restante_flotante:.4f}) NO aplicado debido a colisión previa con parte entera o límite.", extra={"categoria_log": "log_collision_handler_detalle"})
        elif log_detalle_habilitado:
            logger.debug(f"    AMCE_X_DETALLE: dx_restante_flotante ({dx_restante_flotante:.4f}) muy pequeño, no se aplica.", extra={"categoria_log": "log_collision_handler_detalle"})

        entidad_hitbox.x = hb_temporal_eje_actual.x
        
        if log_habilitado: # Print convertido a log
            logger.debug(f"AMCE_X: Saliendo. dx_total_aplicado: {dx_total_aplicado_al_hb_original:.2f}, HB_Out: {entidad_hitbox.topleft}", extra={"categoria_log": "log_collision_handler"})
        return dx_total_aplicado_al_hb_original

    def _aplicar_movimiento_y_colision_eje_y(self, entidad_hitbox, dy_aplicado, obstaculos, mundo_ancho, mundo_alto):
        log_habilitado = settings.MODO_DEBUG_LOGS and settings.LOG_CATEGORIAS.get("log_collision_handler", False)
        log_detalle_habilitado = settings.MODO_DEBUG_LOGS and settings.LOG_CATEGORIAS.get("log_collision_handler_detalle", False)
        
        if log_detalle_habilitado:
            logger.debug(f"AMCE_Y: Entrando, dy_aplicado: {dy_aplicado:.2f}, HB_In: {entidad_hitbox.topleft}", extra={"categoria_log": "log_collision_handler"})

        dy_total_aplicado_al_hb_original = 0.0
        hb_temporal_eje_actual = entidad_hitbox.copy()

        if abs(dy_aplicado) < settings.UMBRAL_MOV_FLOTANTE_ENTIDAD_PARA_COLISION:
            if log_detalle_habilitado:
                logger.debug(f"AMCE_Y: dy_aplicado ({dy_aplicado:.4f}) muy pequeño, no se aplica.", extra={"categoria_log": "log_collision_handler_detalle"})
            return dy_total_aplicado_al_hb_original

        paso_mov_truncado = int(dy_aplicado) 
        dy_restante_flotante = dy_aplicado - paso_mov_truncado

        if log_detalle_habilitado:
            logger.debug(f"AMCE_Y: dy_aplicado={dy_aplicado:.4f}. HB.y original={hb_temporal_eje_actual.y}, PasoTrunc={paso_mov_truncado}, RestoFloat={dy_restante_flotante:.4f}", extra={"categoria_log": "log_collision_handler_detalle"})

        if paso_mov_truncado != 0:
            dy_signo = 1 if paso_mov_truncado > 0 else -1
            for _ in range(abs(paso_mov_truncado)):
                hb_pos_anterior_al_paso = hb_temporal_eje_actual.y
                hb_temporal_eje_actual.y += dy_signo
                colision_en_este_paso = False

                if hb_temporal_eje_actual.top < 0:
                    hb_temporal_eje_actual.top = 0
                    colision_en_este_paso = True
                    if log_detalle_habilitado: logger.debug(f"    AMCE_Y_LIMITE_MUNDO: Y Colisión con límite SUPERIOR. HB.top ajustado a 0.", extra={"categoria_log": "log_collision_handler_detalle"})
                elif hb_temporal_eje_actual.bottom > mundo_alto:
                    hb_temporal_eje_actual.bottom = mundo_alto
                    colision_en_este_paso = True
                    if log_detalle_habilitado: logger.debug(f"    AMCE_Y_LIMITE_MUNDO: Y Colisión con límite INFERIOR. HB.bottom ajustado a {mundo_alto}.", extra={"categoria_log": "log_collision_handler_detalle"})

                if not colision_en_este_paso:
                    for obstaculo in obstaculos:
                        rect_colision_obstaculo = obstaculo.hitbox if hasattr(obstaculo, 'hitbox') else obstaculo.rect
                        if hb_temporal_eje_actual.colliderect(rect_colision_obstaculo):
                            hb_temporal_eje_actual.y = hb_pos_anterior_al_paso
                            colision_en_este_paso = True
                            if log_detalle_habilitado:
                                obst_id_log = getattr(obstaculo, 'nombre_log_entidad', type(obstaculo).__name__)
                                logger.debug(f"    AMCE_Y_DETALLE: Fase 2 (Y) Colisión PASO con {obst_id_log} en y={hb_temporal_eje_actual.y+dy_signo}. Revertido a y={hb_temporal_eje_actual.y}.", extra={"categoria_log": "log_collision_handler_detalle"})
                            break
                
                if colision_en_este_paso:
                    break

        if abs(dy_restante_flotante) >= settings.UMBRAL_MOV_FLOTANTE_ENTIDAD_PARA_COLISION:
            colision_despues_de_parte_entera = False
            for obstaculo in obstaculos:
                rect_colision_obstaculo = obstaculo.hitbox if hasattr(obstaculo, 'hitbox') else obstaculo.rect
                if hb_temporal_eje_actual.colliderect(rect_colision_obstaculo):
                    colision_despues_de_parte_entera = True
                    break
        
            if hb_temporal_eje_actual.top <= 0 or hb_temporal_eje_actual.bottom >= mundo_alto:
                colision_despues_de_parte_entera = True

            if not colision_despues_de_parte_entera:
                hb_pos_anterior_flotante = hb_temporal_eje_actual.y
                hb_temporal_eje_actual.y += dy_restante_flotante
                
                colision_parte_flotante_limites = False
                if hb_temporal_eje_actual.top < 0:
                    hb_temporal_eje_actual.top = 0
                    colision_parte_flotante_limites = True
                    if log_detalle_habilitado: logger.debug(f"    AMCE_Y_LIMITE_MUNDO_FLOAT: Y Colisión FLOTANTE con límite SUPERIOR. HB.top ajustado a 0.", extra={"categoria_log": "log_collision_handler_detalle"})
                elif hb_temporal_eje_actual.bottom > mundo_alto:
                    hb_temporal_eje_actual.bottom = mundo_alto
                    colision_parte_flotante_limites = True
                    if log_detalle_habilitado: logger.debug(f"    AMCE_Y_LIMITE_MUNDO_FLOAT: Y Colisión FLOTANTE con límite INFERIOR. HB.bottom ajustado a {mundo_alto}.", extra={"categoria_log": "log_collision_handler_detalle"})

                if not colision_parte_flotante_limites:
                    for obstaculo in obstaculos:
                        rect_colision_obstaculo = obstaculo.hitbox if hasattr(obstaculo, 'hitbox') else obstaculo.rect
                        if hb_temporal_eje_actual.colliderect(rect_colision_obstaculo):
                            hb_temporal_eje_actual.y = hb_pos_anterior_flotante
                            if log_detalle_habilitado:
                                obst_id_log = getattr(obstaculo, 'nombre_log_entidad', type(obstaculo).__name__)
                                logger.debug(f"    AMCE_Y_DETALLE: Fase 2 (Y) Colisión FLOTANTE con {obst_id_log} en y={hb_pos_anterior_flotante + dy_restante_flotante}. Revertido a y={hb_temporal_eje_actual.y}.", extra={"categoria_log": "log_collision_handler_detalle"})
                            break

        entidad_hitbox.y = hb_temporal_eje_actual.y

        if log_habilitado: # Print convertido a log
            logger.debug(f"AMCE_Y: Saliendo. dy_total_aplicado: {dy_total_aplicado_al_hb_original:.2f}, HB_Out: {entidad_hitbox.topleft}", extra={"categoria_log": "log_collision_handler"})
        return dy_total_aplicado_al_hb_original

    def _verificar_y_revertir_colision_post_fase2(self, entidad_actual, entidad_hitbox, obstaculos, 
                                               pos_segura_fase1_x, pos_segura_fase1_y, 
                                               pos_original_global_x, pos_original_global_y,
                                               intento_mov_x_frame, intento_mov_y_frame):
        # --- IMPORTACIONES LOCALES PARA EVITAR CICLOS ---
        from src.entidades.jugador import Jugador
        from src.entidades.enemigo import Enemigo
        # --- FIN IMPORTACIONES LOCALES ---

        ent_name_for_print = getattr(entidad_actual, 'nombre_log_entidad', type(entidad_actual).__name__)
        log_habilitado = settings.MODO_DEBUG_LOGS and settings.LOG_CATEGORIAS.get("log_collision_handler", False)
        log_detalle_habilitado = settings.MODO_DEBUG_LOGS and settings.LOG_CATEGORIAS.get("log_collision_handler_detalle", False)
        
        if log_detalle_habilitado: # Print convertido a log
            logger.debug(f"VYR_POST_F2 ({ent_name_for_print}): Entrando. HB Actual: {entidad_hitbox.topleft}, PosSeguraF1: ({pos_segura_fase1_x},{pos_segura_fase1_y})", extra={"categoria_log": "log_collision_handler_detalle"})

        colision_final_detectada = False
        obstaculo_colision_final = None

        for obstaculo in obstaculos:
            if obstaculo == entidad_actual:
                continue
            rect_colision_obstaculo = obstaculo.hitbox if hasattr(obstaculo, 'hitbox') else obstaculo.rect
            if entidad_hitbox.colliderect(rect_colision_obstaculo):
                obst_id_log = getattr(obstaculo, 'nombre_log_entidad', type(obstaculo).__name__)
                colision_final_detectada = True
                obstaculo_colision_final = obst_id_log
                if log_habilitado: # Print convertido a log
                    logger.warning(f"VYR_POST_F2 ({ent_name_for_print}): ¡ALERTA! Colisión detectada con {obst_id_log} DESPUÉS de Fase 2. HB_Ent: {entidad_hitbox.topleft}, HB_Obs: {rect_colision_obstaculo.topleft}", extra={"categoria_log": "log_collision_handler"})
                break
        
        if colision_final_detectada:
            if log_habilitado: # Print convertido a log
                 logger.warning(f"VYR_POST_F2 ({ent_name_for_print}): Revertiendo HB a pos_segura_fase1 ({pos_segura_fase1_x},{pos_segura_fase1_y}).", extra={"categoria_log": "log_collision_handler"})
            entidad_hitbox.topleft = (pos_segura_fase1_x, pos_segura_fase1_y)
            
            # Intentar resolver solapamientos estáticos desde la posición segura de Fase 1
            if log_habilitado: # Print convertido a log
                logger.debug(f"VYR_POST_F2 ({ent_name_for_print}): Llamando a RSE en X desde pos segura F1.", extra={"categoria_log": "log_collision_handler"})
            self._resolver_solapamientos_estaticos_eje(entidad_actual, entidad_hitbox, obstaculos, 'x', intento_mov_x_frame)
            
            if log_habilitado: # Print convertido a log
                logger.debug(f"VYR_POST_F2 ({ent_name_for_print}): Llamando a RSE en Y desde pos segura F1.", extra={"categoria_log": "log_collision_handler"})
            self._resolver_solapamientos_eje(entidad_actual, entidad_hitbox, obstaculos, 'y', intento_mov_y_frame)

            if log_habilitado: # Print convertido a log
                logger.debug(f"VYR_POST_F2 ({ent_name_for_print}): HB después de RSE desde F1: {entidad_hitbox.topleft}", extra={"categoria_log": "log_collision_handler"})

        if log_detalle_habilitado: # Print convertido a log
            logger.debug(f"VYR_POST_F2 ({ent_name_for_print}): Saliendo. ColisionFinal: {colision_final_detectada} (con {obstaculo_colision_final if obstaculo_colision_final else 'N/A'}). HB Final: {entidad_hitbox.topleft}", extra={"categoria_log": "log_collision_handler_detalle"})
        return colision_final_detectada

    def _prevenir_teletransportacion(self, entidad_hitbox, dx_solicitado, dy_solicitado, pos_segura_fase1_x, pos_segura_fase1_y):
        log_habilitado = settings.MODO_DEBUG_LOGS and settings.LOG_CATEGORIAS.get("log_collision_handler", False)
        mov_real_x = entidad_hitbox.x - pos_segura_fase1_x
        mov_real_y = entidad_hitbox.y - pos_segura_fase1_y

        # Aquí usamos UMBRAL_MOV_FLOTANTE_ENTIDAD_PARA_COLISION porque dx/dy_solicitado son los del frame, no acumulados subpixel.
        umbral_tele_x = abs(dx_solicitado * settings.FACTOR_UMBRAL_TELETRANSPORTACION) + entidad_hitbox.width * 0.5 
        umbral_tele_y = abs(dy_solicitado * settings.FACTOR_UMBRAL_TELETRANSPORTACION) + entidad_hitbox.height * 0.5

        teletransportacion_x = abs(mov_real_x) > umbral_tele_x and abs(dx_solicitado) > settings.UMBRAL_MOV_FLOTANTE_ENTIDAD_PARA_COLISION
        teletransportacion_y = abs(mov_real_y) > umbral_tele_y and abs(dy_solicitado) > settings.UMBRAL_MOV_FLOTANTE_ENTIDAD_PARA_COLISION

        if teletransportacion_x or teletransportacion_y:
            if log_habilitado: # Print convertido a log
                logger.warning(f"TELETRANSPORTACIÓN DETECTADA! Sol:({dx_solicitado:.2f},{dy_solicitado:.2f}), Real:({mov_real_x:.2f},{mov_real_y:.2f}), Umbrales:({umbral_tele_x:.2f},{umbral_tele_y:.2f}). Revertiendo a pos F1: ({pos_segura_fase1_x},{pos_segura_fase1_y})", extra={"categoria_log": "log_collision_handler"})
            entidad_hitbox.topleft = (pos_segura_fase1_x, pos_segura_fase1_y)
            return True # Teletransportación ocurrida y revertida
        return False

    def gestionar_movimiento_y_colision(self, entidad_actual, entidad_hitbox, entidad_rect, hitbox_offset_x, hitbox_offset_y, dx, dy, obstaculos, mundo_ancho, mundo_alto):
        # --- IMPORTACIONES LOCALES PARA EVITAR CICLOS ---
        from src.entidades.jugador import Jugador
        from src.entidades.enemigo import Enemigo
        # --- FIN IMPORTACIONES LOCALES ---
        
        ent_name_for_print = getattr(entidad_actual, 'nombre_log_entidad', type(entidad_actual).__name__)
        log_habilitado = settings.MODO_DEBUG_LOGS and settings.LOG_CATEGORIAS.get("log_collision_handler", False)
        log_detalle_habilitado = settings.MODO_DEBUG_LOGS and settings.LOG_CATEGORIAS.get("log_collision_handler_detalle", False)

        if not isinstance(dx, (int, float)) or not isinstance(dy, (int, float)):
            if log_habilitado:
                logger.error(f"GESTIONAR_MOV: dx o dy no son numéricos! dx:{dx}({type(dx)}), dy:{dy}({type(dy)}) para {ent_name_for_print}", extra={"categoria_log": "log_collision_handler"})
            return 0.0, 0.0 # Devuelve 0 movimiento si la entrada no es válida

        if log_habilitado: # Print convertido a log
            logger.debug(f"GESTIONAR_MOV ({ent_name_for_print}): --- INICIO --- dx={dx:.2f}, dy={dy:.2f}. HB In: {entidad_hitbox.topleft}, Rect In: {entidad_rect.topleft}", extra={"categoria_log": "log_collision_handler"})

        # Fase 0: Guardar posición original global del hitbox
        pos_original_global_x, pos_original_global_y = entidad_hitbox.x, entidad_hitbox.y
        if log_detalle_habilitado:
            logger.debug(f"  GM_DETALLE ({ent_name_for_print}): Fase 0: Pos Original HB: ({pos_original_global_x},{pos_original_global_y})", extra={"categoria_log": "log_collision_handler_detalle"})

        # Fase 1: Resolver solapamientos estáticos existentes ANTES de aplicar el movimiento del frame actual.
        # Esto es crucial si la entidad ya está solapada al inicio del frame.
        if log_detalle_habilitado:
            logger.debug(f"  GM_DETALLE ({ent_name_for_print}): Fase 1: Resolviendo solapamientos estáticos (X) ANTES de mov. Input Eje X para RSE: {dx:.2f}", extra={"categoria_log": "log_collision_handler_detalle"})
        self._resolver_solapamientos_estaticos_eje(entidad_actual, entidad_hitbox, obstaculos, 'x', dx)
        
        if log_detalle_habilitado:
            logger.debug(f"  GM_DETALLE ({ent_name_for_print}): Fase 1: Resolviendo solapamientos estáticos (Y) ANTES de mov. Input Eje Y para RSE: {dy:.2f}", extra={"categoria_log": "log_collision_handler_detalle"})
        self._resolver_solapamientos_estaticos_eje(entidad_actual, entidad_hitbox, obstaculos, 'y', dy)

        pos_segura_fase1_x, pos_segura_fase1_y = entidad_hitbox.x, entidad_hitbox.y
        if log_detalle_habilitado:
            logger.debug(f"  GM_DETALLE ({ent_name_for_print}): Fase 1: Pos Segura post-RSE (Fase 1): ({pos_segura_fase1_x},{pos_segura_fase1_y})", extra={"categoria_log": "log_collision_handler_detalle"})

        # Fase 2: Aplicar movimiento del frame actual y manejar colisiones dinámicas, eje por eje.
        # El movimiento se aplica al hitbox que ya fue corregido en Fase 1.
        dx_real_aplicado_hb = self._aplicar_movimiento_y_colision_eje_x(entidad_hitbox, dx, obstaculos, mundo_ancho, mundo_alto)
        dy_real_aplicado_hb = self._aplicar_movimiento_y_colision_eje_y(entidad_hitbox, dy, obstaculos, mundo_ancho, mundo_alto)
        
        if log_detalle_habilitado:
            logger.debug(f"  GM_DETALLE ({ent_name_for_print}): Fase 2: Mov Real Aplicado (dx:{dx_real_aplicado_hb:.2f}, dy:{dy_real_aplicado_hb:.2f}). HB post F2: {entidad_hitbox.topleft}", extra={"categoria_log": "log_collision_handler_detalle"})
        
        # Fase 3: Verificación final y posible reversión si aún hay solapamiento.
        # Esta fase es una salvaguarda. Si la lógica de Fase 1 y 2 es perfecta, no debería ser necesaria.
        hubo_colision_post_fase2 = self._verificar_y_revertir_colision_post_fase2(
            entidad_actual, entidad_hitbox, obstaculos, 
            pos_segura_fase1_x, pos_segura_fase1_y,
            pos_original_global_x, pos_original_global_y,
            dx, dy # Pasamos el intento de movimiento del frame para la lógica de RSE dentro de VYR
        )
        if log_detalle_habilitado:
            logger.debug(f"  GM_DETALLE ({ent_name_for_print}): Fase 3: Hubo Colisión Post-F2 y Reversión: {hubo_colision_post_fase2}. HB post F3: {entidad_hitbox.topleft}", extra={"categoria_log": "log_collision_handler_detalle"})

        # Fase 4: Detección y prevención de teletransportación (comparando con pos_segura_fase1)
        # Esto se hace DESPUÉS de la Fase 3 porque la Fase 3 podría haber revertido a pos_segura_fase1.
        if settings.PREVENIR_TELETRANSPORTACION_CH:
            tele_revertida = self._prevenir_teletransportacion(entidad_hitbox, dx, dy, pos_segura_fase1_x, pos_segura_fase1_y)
            if tele_revertida and log_habilitado:
                 logger.warning(f"GESTIONAR_MOV ({ent_name_for_print}): Teletransportación revertida. HB final: {entidad_hitbox.topleft}", extra={"categoria_log": "log_collision_handler"})
            if log_detalle_habilitado:
                logger.debug(f"  GM_DETALLE ({ent_name_for_print}): Fase 4: Teletransportación Revertida: {tele_revertida}. HB post F4: {entidad_hitbox.topleft}", extra={"categoria_log": "log_collision_handler_detalle"})

        # Fase 5: Sincronizar el rect de la entidad con la posición final del hitbox
        entidad_rect.left = entidad_hitbox.left - hitbox_offset_x
        entidad_rect.top = entidad_hitbox.top - hitbox_offset_y
        if log_detalle_habilitado:
            logger.debug(f"  GM_DETALLE ({ent_name_for_print}): Fase 5: Sincronización Rect. Rect Final: {entidad_rect.topleft}, HB Final: {entidad_hitbox.topleft}", extra={"categoria_log": "log_collision_handler_detalle"})

        # Calcular el movimiento real final del hitbox basado en su posición original al inicio de esta función.
        mov_final_real_hb_x = entidad_hitbox.x - pos_original_global_x
        mov_final_real_hb_y = entidad_hitbox.y - pos_original_global_y

        if log_habilitado: # Print convertido a log
            logger.debug(f"GESTIONAR_MOV ({ent_name_for_print}): --- FIN --- Mov Real Final HB (x:{mov_final_real_hb_x:.2f}, y:{mov_final_real_hb_y:.2f}). HB Out: {entidad_hitbox.topleft}, Rect Out: {entidad_rect.topleft}", extra={"categoria_log": "log_collision_handler"})
        
        return mov_final_real_hb_x, mov_final_real_hb_y