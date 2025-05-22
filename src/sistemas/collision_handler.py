import pygame
import logging
from src.config import settings # MODIFICADO: Importación de settings actualizada
from typing import TYPE_CHECKING # <--- AÑADIR IMPORT

# Ya no importamos Jugador y Enemigo aquí en el ámbito global para evitar el ciclo
# if TYPE_CHECKING: # Se usaría si tuviéramos anotaciones de tipo que los necesitaran globalmente
#     from src.entidades.jugador import Jugador
#     from src.entidades.enemigo import Enemigo

# Cambiar nombre del logger y eliminar setLevel
# logger_ch = logging.getLogger("log_collision_handler")
# logger_ch.setLevel(logging.DEBUG)
logger = logging.getLogger("collision_handler")

class CollisionHandler:
    @staticmethod
    def _check_touch_or_overlap(r1, r2, eje):
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

    @staticmethod
    def _resolver_solapamientos_estaticos_eje(entidad_actual, entidad_hitbox, obstaculos, eje, movimiento_input_en_eje):
        # --- IMPORTACIONES LOCALES PARA EVITAR CICLOS ---
        from src.entidades.jugador import Jugador
        from src.entidades.enemigo import Enemigo
        # --- FIN IMPORTACIONES LOCALES ---

        ent_name_for_print = getattr(entidad_actual, 'nombre_log_entidad', type(entidad_actual).__name__)
        print(f"DEBUG_CH_RSE_ENTRADA: Entrando a _resolver_solapamientos_estaticos_eje para: {ent_name_for_print}, Eje: {eje}, Input: {movimiento_input_en_eje:.2f}, HB_Ent_Inicial: {entidad_hitbox.topleft}")

        log_habilitado = settings.MODO_DEBUG_LOGS and settings.LOG_CATEGORIAS.get("log_collision_handler", False)
        log_detalle_habilitado = settings.MODO_DEBUG_LOGS and settings.LOG_CATEGORIAS.get("log_collision_handler_detalle", False)

        es_jugador_actual = isinstance(entidad_actual, Jugador)
        input_actual_en_eje_es_cero = (abs(movimiento_input_en_eje) < settings.UMBRAL_MOV_FLOTANTE_ENTIDAD)
        
        for pasada in range(settings.MAX_PASADAS_RESOLUCION_ESTATICA):
            colision_resuelta_en_pasada = False
            print(f"DEBUG_CH_RSE_PASADA_INICIO: ({ent_name_for_print}, Eje: {eje}) --- INICIO Pasada {pasada + 1} --- HB_Actual: {entidad_hitbox.topleft}")

            for obstaculo in obstaculos:
                if obstaculo == entidad_actual: 
                    continue
            
                rect_colision_obstaculo = obstaculo.hitbox if hasattr(obstaculo, 'hitbox') else obstaculo.rect
                obst_id_log = getattr(obstaculo, 'nombre_log_entidad', type(obstaculo).__name__)
                
                print(f"DEBUG_CH_RSE_OBST_LOOP: ({ent_name_for_print}) Verificando Obst: {obst_id_log} (HB_Obs: {rect_colision_obstaculo.topleft}, Size_Obs: {rect_colision_obstaculo.size}) vs HB_Ent: {entidad_hitbox.topleft}")
                
                colisiona_general = entidad_hitbox.colliderect(rect_colision_obstaculo)

                if not colisiona_general:
                    print(f"DEBUG_CH_RSE_OBST_LOOP: ({ent_name_for_print}) NO hay colisión general con {obst_id_log}. Continuando con siguiente obstáculo.")
                    continue

                print(f"DEBUG_CH_RSE_COLISION_DETECTADA: ({ent_name_for_print}) SÍ hay colisión con {obst_id_log}. HB_Ent: {entidad_hitbox.topleft}, HB_Obs: {rect_colision_obstaculo.topleft}, MovInputEje: {movimiento_input_en_eje:.2f}")

                    x_antes = entidad_hitbox.x
                    y_antes = entidad_hitbox.y
                print(f"DEBUG_CH_RSE_PRE_AJUSTE_LOGICA: ({ent_name_for_print} vs {obst_id_log}) HB_Ent_Antes_De_Logica_Ajuste: ({x_antes},{y_antes})")

                        if eje == 'x':
                    if movimiento_input_en_eje > 0: 
                        if rect_colision_obstaculo.centerx > entidad_hitbox.centerx: 
                                entidad_hitbox.right = rect_colision_obstaculo.left
                            print(f"DEBUG_CH_RSE_AJUSTE_X_CASO1: ({ent_name_for_print}) Mov DERECHA, Obs a DERECHA. HB.right ({entidad_hitbox.right}) ajustado a Obs.left ({rect_colision_obstaculo.left})")
                    elif movimiento_input_en_eje < 0: 
                        if rect_colision_obstaculo.centerx < entidad_hitbox.centerx: 
                                entidad_hitbox.left = rect_colision_obstaculo.right
                            print(f"DEBUG_CH_RSE_AJUSTE_X_CASO2: ({ent_name_for_print}) Mov IZQUIERDA, Obs a IZQUIERDA. HB.left ({entidad_hitbox.left}) ajustado a Obs.right ({rect_colision_obstaculo.right})")
                    else: 
                            if entidad_hitbox.centerx < rect_colision_obstaculo.centerx:
                                entidad_hitbox.right = rect_colision_obstaculo.left
                            print(f"DEBUG_CH_RSE_AJUSTE_X_CASO3: ({ent_name_for_print}) Mov CERO, Ent a IZQ de Obs. HB.right ({entidad_hitbox.right}) ajustado a Obs.left ({rect_colision_obstaculo.left})")
                            else:
                                entidad_hitbox.left = rect_colision_obstaculo.right
                            print(f"DEBUG_CH_RSE_AJUSTE_X_CASO4: ({ent_name_for_print}) Mov CERO, Ent a DER de Obs. HB.left ({entidad_hitbox.left}) ajustado a Obs.right ({rect_colision_obstaculo.right})")
                        hitbox_modificado_este_obstaculo = (entidad_hitbox.x != x_antes)

                    elif eje == 'y':
                    if movimiento_input_en_eje > 0: 
                        if rect_colision_obstaculo.centery > entidad_hitbox.centery: 
                                entidad_hitbox.bottom = rect_colision_obstaculo.top
                            print(f"DEBUG_CH_RSE_AJUSTE_Y_CASO1: ({ent_name_for_print}) Mov ABAJO, Obs ABAJO. HB.bottom ({entidad_hitbox.bottom}) ajustado a Obs.top ({rect_colision_obstaculo.top})")
                    elif movimiento_input_en_eje < 0: 
                        if rect_colision_obstaculo.centery < entidad_hitbox.centery: 
                                entidad_hitbox.top = rect_colision_obstaculo.bottom
                            print(f"DEBUG_CH_RSE_AJUSTE_Y_CASO2: ({ent_name_for_print}) Mov ARRIBA, Obs ARRIBA. HB.top ({entidad_hitbox.top}) ajustado a Obs.bottom ({rect_colision_obstaculo.bottom})")
                    else: 
                            if entidad_hitbox.centery < rect_colision_obstaculo.centery:
                                entidad_hitbox.bottom = rect_colision_obstaculo.top
                            print(f"DEBUG_CH_RSE_AJUSTE_Y_CASO3: ({ent_name_for_print}) Mov CERO, Ent ARRIBA de Obs. HB.bottom ({entidad_hitbox.bottom}) ajustado a Obs.top ({rect_colision_obstaculo.top})")
                            else:
                                entidad_hitbox.top = rect_colision_obstaculo.bottom
                            print(f"DEBUG_CH_RSE_AJUSTE_Y_CASO4: ({ent_name_for_print}) Mov CERO, Ent ABAJO de Obs. HB.top ({entidad_hitbox.top}) ajustado a Obs.bottom ({rect_colision_obstaculo.bottom})")
                        hitbox_modificado_este_obstaculo = (entidad_hitbox.y != y_antes)

                    if hitbox_modificado_este_obstaculo:
                        colision_resuelta_en_pasada = True
                    print(f"DEBUG_CH_RSE_POST_AJUSTE_OBST: ({ent_name_for_print} vs {obst_id_log}) HB_Ent_Modificado: {entidad_hitbox.topleft}")
            
            print(f"DEBUG_CH_RSE_PASADA_FIN: ({ent_name_for_print}, Eje: {eje}) --- FIN Pasada {pasada + 1} --- HB_Actual: {entidad_hitbox.topleft}, ColisionResueltaEnPasada: {colision_resuelta_en_pasada}")
            if not colision_resuelta_en_pasada:
                print(f"DEBUG_CH_RSE_PASADA_BREAK: ({ent_name_for_print}, Eje: {eje}) No hubo más modificaciones en esta pasada. Saliendo del bucle de pasadas.")
                break

        print(f"DEBUG_CH_RSE_SALIDA: Saliendo de _resolver_solapamientos_estaticos_eje para: {ent_name_for_print}, Eje: {eje}, HB_Out_Final: {entidad_hitbox.topleft}")

    @staticmethod
    def _aplicar_movimiento_y_colision_eje_x(entidad_hitbox, dx_aplicado, obstaculos, mundo_ancho, mundo_alto):
        log_habilitado = settings.MODO_DEBUG_LOGS and settings.LOG_CATEGORIAS.get("log_collision_handler", False)
        log_detalle_habilitado = settings.MODO_DEBUG_LOGS and settings.LOG_CATEGORIAS.get("log_collision_handler_detalle", False)
        
        print(f"DEBUG_CH: Entrando a _aplicar_movimiento_y_colision_eje_x, dx_aplicado: {dx_aplicado:.2f}, HB_In: {entidad_hitbox.topleft}")

        dx_total_aplicado_al_hb_original = 0.0
        hb_temporal_eje_actual = entidad_hitbox.copy() # Copia para manipular en este eje
            
        if abs(dx_aplicado) < settings.UMBRAL_MOV_FLOTANTE_ENTIDAD:
            if log_detalle_habilitado:
                logger.debug(f"      CH_DETALLE: Fase 2 (X): dx_aplicado ({dx_aplicado:.4f}) muy pequeño, no se aplica movimiento.", extra={"categoria_log": "log_collision_handler_detalle"})
            return dx_total_aplicado_al_hb_original # Devuelve 0.0

        paso_mov_truncado = int(dx_aplicado) # Tomar la parte entera para el bucle principal
        dx_restante_flotante = dx_aplicado - paso_mov_truncado # Guardar la parte flotante

        if log_detalle_habilitado:
            logger.debug(f"      CH_DETALLE: Fase 2 (X): dx_aplicado={dx_aplicado:.4f}. HB.x original={hb_temporal_eje_actual.x}, PasoTrunc={paso_mov_truncado}, RestoFloat={dx_restante_flotante:.4f}", extra={"categoria_log": "log_collision_handler_detalle"})

        # Mover pixel a pixel la parte entera
        if paso_mov_truncado != 0:
            dx_signo = 1 if paso_mov_truncado > 0 else -1
            for _ in range(abs(paso_mov_truncado)):
                hb_pos_anterior_al_paso = hb_temporal_eje_actual.x
                hb_temporal_eje_actual.x += dx_signo
                dx_total_aplicado_al_hb_original += dx_signo
                colision_en_este_paso = False

                # --- INICIO: Chequeo Límites del Mundo --- 
                if hb_temporal_eje_actual.left < 0:
                    hb_temporal_eje_actual.left = 0
                    dx_total_aplicado_al_hb_original = hb_temporal_eje_actual.left - entidad_hitbox.left # Movimiento real hasta el límite
                    colision_en_este_paso = True
                    if log_detalle_habilitado: logger.debug(f"        CH_LIMITE_MUNDO: X Colisión con límite IZQUIERDO. HB.left ajustado a 0. Mov real hasta aquí: {dx_total_aplicado_al_hb_original}", extra={"categoria_log": "log_collision_handler_detalle"})
                elif hb_temporal_eje_actual.right > mundo_ancho:
                    hb_temporal_eje_actual.right = mundo_ancho
                    dx_total_aplicado_al_hb_original = hb_temporal_eje_actual.left - entidad_hitbox.left # Movimiento real hasta el límite
                    colision_en_este_paso = True
                    if log_detalle_habilitado: logger.debug(f"        CH_LIMITE_MUNDO: X Colisión con límite DERECHO. HB.right ajustado a {mundo_ancho}. Mov real hasta aquí: {dx_total_aplicado_al_hb_original}", extra={"categoria_log": "log_collision_handler_detalle"})
                # --- FIN: Chequeo Límites del Mundo --- 

                if not colision_en_este_paso: # Solo chequear obstáculos si no colisionó con límites
                    for obstaculo in obstaculos:
                        rect_colision_obstaculo = obstaculo.hitbox if hasattr(obstaculo, 'hitbox') else obstaculo.rect
                        if hb_temporal_eje_actual.colliderect(rect_colision_obstaculo):
                            hb_temporal_eje_actual.x = hb_pos_anterior_al_paso # Revertir el paso
                            dx_total_aplicado_al_hb_original -= dx_signo # Revertir el acumulado
                            colision_en_este_paso = True
                            if log_detalle_habilitado: 
                                obst_id_log = getattr(obstaculo, 'nombre_log_entidad', type(obstaculo).__name__)
                                logger.debug(f"        CH_DETALLE: Fase 2 (X) Colisión PASO con {obst_id_log} en x={hb_temporal_eje_actual.x+dx_signo}. Revertido a x={hb_temporal_eje_actual.x}. Acumulado: {dx_total_aplicado_al_hb_original}", extra={"categoria_log": "log_collision_handler_detalle"})
                            break # Salir del bucle de obstáculos
                
                if colision_en_este_paso:
                    break # Salir del bucle de movimiento pixel a pixel

        # Aplicar la parte flotante restante si no hubo colisión con la parte entera
        # Y si la parte flotante es significativa.
        # Además, chequear colisión con límites del mundo también para la parte flotante.
        if abs(dx_restante_flotante) >= settings.UMBRAL_MOV_FLOTANTE_ENTIDAD:
            colision_despues_de_parte_entera = False
            # Verificar si el movimiento entero ya causó una colisión con un obstáculo (no límite)
            for obstaculo in obstaculos:
                rect_colision_obstaculo = obstaculo.hitbox if hasattr(obstaculo, 'hitbox') else obstaculo.rect
                if hb_temporal_eje_actual.colliderect(rect_colision_obstaculo):
                    colision_despues_de_parte_entera = True
                    break 
        
            # También verificar si el movimiento entero ya causó colisión con límites del mundo
            if hb_temporal_eje_actual.left <= 0 or hb_temporal_eje_actual.right >= mundo_ancho:
                colision_despues_de_parte_entera = True # Considerar colisión con límite como una colisión que detiene parte flotante

            if not colision_despues_de_parte_entera:
                hb_pos_anterior_flotante = hb_temporal_eje_actual.x
                hb_temporal_eje_actual.x += dx_restante_flotante
                dx_total_aplicado_al_hb_original += dx_restante_flotante
                colision_parte_flotante = False

                # --- INICIO: Chequeo Límites del Mundo para parte flotante --- 
                if hb_temporal_eje_actual.left < 0:
                    hb_temporal_eje_actual.left = 0
                    dx_total_aplicado_al_hb_original = hb_temporal_eje_actual.left - entidad_hitbox.left
                    colision_parte_flotante = True
                    if log_detalle_habilitado: logger.debug(f"        CH_LIMITE_MUNDO: X Colisión FLOTANTE con límite IZQUIERDO. HB.left ajustado a 0.", extra={"categoria_log": "log_collision_handler_detalle"})
                elif hb_temporal_eje_actual.right > mundo_ancho:
                    hb_temporal_eje_actual.right = mundo_ancho
                    dx_total_aplicado_al_hb_original = hb_temporal_eje_actual.left - entidad_hitbox.left 
                    colision_parte_flotante = True
                    if log_detalle_habilitado: logger.debug(f"        CH_LIMITE_MUNDO: X Colisión FLOTANTE con límite DERECHO. HB.right ajustado a {mundo_ancho}. Mov real: {dx_total_aplicado_al_hb_original}", extra={"categoria_log": "log_collision_handler_detalle"})
                # --- FIN: Chequeo Límites del Mundo para parte flotante --- 

                if not colision_parte_flotante:
                    for obstaculo in obstaculos:
                        rect_colision_obstaculo = obstaculo.hitbox if hasattr(obstaculo, 'hitbox') else obstaculo.rect
                        if hb_temporal_eje_actual.colliderect(rect_colision_obstaculo):
                            hb_temporal_eje_actual.x = hb_pos_anterior_flotante # Revertir solo la parte flotante
                            dx_total_aplicado_al_hb_original -= dx_restante_flotante
                            colision_parte_flotante = True # Marcar colisión para log
                            if log_detalle_habilitado: 
                                obst_id_log = getattr(obstaculo, 'nombre_log_entidad', type(obstaculo).__name__)
                                logger.debug(f"        CH_DETALLE: Fase 2 (X) Colisión FLOTANTE con {obst_id_log} en x={hb_pos_anterior_flotante+dx_restante_flotante:.4f}. Revertido a x={hb_temporal_eje_actual.x:.4f}. Acumulado: {dx_total_aplicado_al_hb_original:.4f}", extra={"categoria_log": "log_collision_handler_detalle"})
                            break # Salir del bucle de obstáculos
                
                if colision_parte_flotante and log_detalle_habilitado:
                    logger.debug(f"      CH_DETALLE: Fase 2 (X): Movimiento flotante ({dx_restante_flotante:.4f}) causó colisión y fue revertido o ajustado por límite.", extra={"categoria_log": "log_collision_handler_detalle"})
                elif log_detalle_habilitado:
                    logger.debug(f"      CH_DETALLE: Fase 2 (X): Movimiento flotante ({dx_restante_flotante:.4f}) aplicado. HB.x post-float={hb_temporal_eje_actual.x:.4f}. Acumulado: {dx_total_aplicado_al_hb_original:.4f}", extra={"categoria_log": "log_collision_handler_detalle"})
            elif log_detalle_habilitado:
                 logger.debug(f"      CH_DETALLE: Fase 2 (X): Movimiento flotante ({dx_restante_flotante:.4f}) NO aplicado debido a colisión previa con parte entera o límite.", extra={"categoria_log": "log_collision_handler_detalle"})
        elif log_detalle_habilitado:
            logger.debug(f"      CH_DETALLE: Fase 2 (X): dx_restante_flotante ({dx_restante_flotante:.4f}) muy pequeño, no se aplica.", extra={"categoria_log": "log_collision_handler_detalle"})

        print(f"DEBUG_CH: Saliendo de _aplicar_movimiento_y_colision_eje_x, dx_real_aplicado: {dx_total_aplicado_al_hb_original:.2f}, HB.x final (temporal): {hb_temporal_eje_actual.x}")
        return dx_total_aplicado_al_hb_original

    @staticmethod
    def _aplicar_movimiento_y_colision_eje_y(entidad_hitbox, dy_aplicado, obstaculos, mundo_ancho, mundo_alto):
        log_habilitado = settings.MODO_DEBUG_LOGS and settings.LOG_CATEGORIAS.get("log_collision_handler", False)
        log_detalle_habilitado = settings.MODO_DEBUG_LOGS and settings.LOG_CATEGORIAS.get("log_collision_handler_detalle", False)
        
        print(f"DEBUG_CH: Entrando a _aplicar_movimiento_y_colision_eje_y, dy_aplicado: {dy_aplicado:.2f}, HB_In: {entidad_hitbox.topleft}")

        if log_habilitado:
            logger.debug(f"    --- CH: Inicio _aplicar_movimiento_y_colision_eje_y --- dy: {dy_aplicado}, HB_in: {entidad_hitbox.topleft}", extra={"categoria_log": "log_collision_handler"})
        
        y_original_hb = entidad_hitbox.y
        hb_temporal_eje_actual = entidad_hitbox.copy() # Usar una copia para la lógica de este eje

        if abs(dy_aplicado) < settings.UMBRAL_MOV_FLOTANTE_ENTIDAD:
            if log_detalle_habilitado:
                logger.debug(f"      CH_DETALLE: Fase 2 (Y): dy_aplicado ({dy_aplicado:.4f}) muy pequeño, no se aplica movimiento.", extra={"categoria_log": "log_collision_handler_detalle"})
            return 0.0 # Devuelve 0.0 si el movimiento es insignificante

        # Aplicar el movimiento deseado al hitbox temporal
        hb_temporal_eje_actual.y = round(y_original_hb + dy_aplicado)

        if log_detalle_habilitado:
            logger.debug(f"      CH_DETALLE: Fase 2 (Y): dy_aplicado={dy_aplicado:.4f}. HB.y original={y_original_hb}, HB_temporal.y post-round={hb_temporal_eje_actual.y}", extra={"categoria_log": "log_collision_handler_detalle"})

        # --- INICIO: Chequeo Límites del Mundo --- 
        if hb_temporal_eje_actual.top < 0:
            hb_temporal_eje_actual.top = 0
            if log_detalle_habilitado: logger.debug(f"        CH_LIMITE_MUNDO: Y Colisión con límite SUPERIOR. HB.top ajustado a 0.", extra={"categoria_log": "log_collision_handler_detalle"})
        elif hb_temporal_eje_actual.bottom > mundo_alto:
            hb_temporal_eje_actual.bottom = mundo_alto
            if log_detalle_habilitado: logger.debug(f"        CH_LIMITE_MUNDO: Y Colisión con límite INFERIOR. HB.bottom ajustado a {mundo_alto}.", extra={"categoria_log": "log_collision_handler_detalle"})
        # --- FIN: Chequeo Límites del Mundo --- 

        # Chequeo de colisiones con obstáculos DESPUÉS de aplicar límites del mundo
            for obstaculo in obstaculos:
                rect_colision_obstaculo = obstaculo.hitbox if hasattr(obstaculo, 'hitbox') else obstaculo.rect
            if hb_temporal_eje_actual.colliderect(rect_colision_obstaculo):
                    obst_id_log = getattr(obstaculo, 'nombre_log_entidad', f"{type(obstaculo).__name__}_Desconocido")
                if log_detalle_habilitado:
                    logger.debug(f"      CH_DETALLE: Fase 2 (Y): Colisión Y detectada con {obst_id_log}. HB_Ent_temp: {hb_temporal_eje_actual.topleft}, HB_Obs: {rect_colision_obstaculo.topleft}", extra={"categoria_log": "log_collision_handler_detalle"})

                # Ajustar la posición del hitbox temporal basado en la dirección del movimiento original
                if dy_aplicado > 0: # Moviéndose hacia abajo, colisionó desde arriba
                    hb_temporal_eje_actual.bottom = rect_colision_obstaculo.top
                    if log_detalle_habilitado:
                            logger.debug(f"        CH_DETALLE: Fase 2 (Y): Ajustado (ABAJO). HB_Ent_temp.bottom corregido a {hb_temporal_eje_actual.bottom}", extra={"categoria_log": "log_collision_handler_detalle"})
                elif dy_aplicado < 0: # Moviéndose hacia arriba, colisionó desde abajo
                    hb_temporal_eje_actual.top = rect_colision_obstaculo.bottom
                        if log_detalle_habilitado:
                            logger.debug(f"        CH_DETALLE: Fase 2 (Y): Ajustado (ARRIBA). HB_Ent_temp.top corregido a {hb_temporal_eje_actual.top}", extra={"categoria_log": "log_collision_handler_detalle"})
                break # Colisión resuelta con este obstáculo, no necesita chequear más para este movimiento

        # El movimiento real aplicado es la diferencia entre la posición final del hb_temporal y la original
        dy_real_aplicado_hb = float(hb_temporal_eje_actual.y - y_original_hb) 

        if log_habilitado:
            logger.debug(f"    --- CH: Fin _aplicar_movimiento_y_colision_eje_y --- HB_temporal_Y: {hb_temporal_eje_actual.y:.2f}, dy_real_aplicado: {dy_real_aplicado_hb:.4f}", extra={"categoria_log": "log_collision_handler"})
        
        print(f"DEBUG_CH: Saliendo de _aplicar_movimiento_y_colision_eje_y, dy_real_aplicado: {dy_real_aplicado_hb:.2f}, HB.y final (temporal): {hb_temporal_eje_actual.y}")
        return dy_real_aplicado_hb # <--- RETORNAR EL VALOR CALCULADO

    @staticmethod
    def _verificar_y_revertir_colision_post_fase2(entidad_actual, entidad_hitbox, obstaculos, 
                                               pos_segura_fase1_x, pos_segura_fase1_y, 
                                               pos_original_global_x, pos_original_global_y,
                                               intento_mov_x_frame, intento_mov_y_frame):
        log_habilitado = settings.MODO_DEBUG_LOGS and settings.LOG_CATEGORIAS.get("log_collision_handler", False)
        log_detalle_habilitado = settings.MODO_DEBUG_LOGS and settings.LOG_CATEGORIAS.get("log_collision_handler_detalle", False)
        revertido_a_fase1 = False
        revertido_a_original = False
        ent_name_for_print = getattr(entidad_actual, 'nombre_log_entidad', type(entidad_actual).__name__)
        print(f"DEBUG_CH: Entrando a _verificar_y_revertir_colision_post_fase2 para: {ent_name_for_print}, HB_In: {entidad_hitbox.topleft}")

        if log_habilitado:
            logger.debug(f"    --- CH: Inicio _verificar_y_revertir_colision_post_fase2 --- HB_Entrada: {entidad_hitbox.topleft}", extra={"categoria_log": "log_collision_handler"})

        for obstaculo in obstaculos:
            rect_colision_obstaculo = obstaculo.hitbox if hasattr(obstaculo, 'hitbox') else obstaculo.rect
            if entidad_hitbox.colliderect(rect_colision_obstaculo):
                obst_id_log = getattr(obstaculo, 'nombre_log_entidad', f"{type(obstaculo).__name__}_Desconocido")
                if log_habilitado:
                    logger.warning(f"      CH_ALERTA: Fase 3: Colisión POST FASE 2 con {obst_id_log}. HB_Ent: {entidad_hitbox.topleft}, HB_Obs: {rect_colision_obstaculo.topleft}. Intentando revertir a Fase 1.", extra={"categoria_log": "log_collision_handler"})
                
                entidad_hitbox.x, entidad_hitbox.y = pos_segura_fase1_x, pos_segura_fase1_y
                revertido_a_fase1 = True
                if log_habilitado:
                    logger.warning(f"        CH_ALERTA: Fase 3: REVERTIDO a pos segura Fase 1: ({pos_segura_fase1_x}, {pos_segura_fase1_y})", extra={"categoria_log": "log_collision_handler"})

                if entidad_hitbox.colliderect(rect_colision_obstaculo):
                    if log_habilitado:
                        logger.error(f"        CH_ERROR_GRAVE: Fase 3: Colisión INCLUSO DESPUÉS DE REVERTIR a Fase 1 con {obst_id_log}! HB_Ent: {entidad_hitbox.topleft}, HB_Obs: {rect_colision_obstaculo.topleft}. Revertiendo a posición ORIGINAL GLOBAL.", extra={"categoria_log": "log_collision_handler"})
                    entidad_hitbox.x, entidad_hitbox.y = pos_original_global_x, pos_original_global_y
                    revertido_a_original = True
                    logger.critical(f"          CH_CRITICO: Fase 3: REVERTIDO A POSICIÓN ORIGINAL GLOBAL ({pos_original_global_x}, {pos_original_global_y}) debido a colisión persistente.", extra={"categoria_log": "log_collision_handler"})
                break

        if log_habilitado:
            logger.debug(f"    --- CH: Fin _verificar_y_revertir_colision_post_fase2 --- RevertidoF1: {revertido_a_fase1}, RevertidoORIG: {revertido_a_original}, HB_Salida: {entidad_hitbox.topleft}", extra={"categoria_log": "log_collision_handler"})

        print(f"DEBUG_CH: Saliendo de _verificar_y_revertir_colision_post_fase2 para: {ent_name_for_print}, RevertidoF1: {revertido_a_fase1}, RevertidoORIG: {revertido_a_original}, HB_Out: {entidad_hitbox.topleft}")
        return revertido_a_fase1, revertido_a_original

    @staticmethod
    def _prevenir_teletransportacion(entidad_hitbox, dx_solicitado, dy_solicitado, pos_segura_fase1_x, pos_segura_fase1_y):
        log_habilitado = settings.MODO_DEBUG_LOGS and settings.LOG_CATEGORIAS.get("log_collision_handler", False)
        print(f"DEBUG_CH_TP: Entrando a _prevenir_teletransportacion, dx_sol: {dx_solicitado:.2f}, dy_sol: {dy_solicitado:.2f}, HB_In: {entidad_hitbox.topleft}, PosSeguraF1: ({pos_segura_fase1_x},{pos_segura_fase1_y})")
        
        pos_actual_x = entidad_hitbox.x
        pos_actual_y = entidad_hitbox.y
        print(f"DEBUG_CH_TP: pos_actual_x={pos_actual_x}, pos_actual_y={pos_actual_y}")

        distancia_movida_x = abs(pos_actual_x - pos_segura_fase1_x)
        distancia_movida_y = abs(pos_actual_y - pos_segura_fase1_y)
        print(f"DEBUG_CH_TP: dist_mov_x={distancia_movida_x:.2f}, dist_mov_y={distancia_movida_y:.2f}")

        distancia_solicitada_x = abs(dx_solicitado)
        distancia_solicitada_y = abs(dy_solicitado)
        print(f"DEBUG_CH_TP: dist_sol_x={distancia_solicitada_x:.2f}, dist_sol_y={distancia_solicitada_y:.2f}")
        
        # ----> PRINT DE INSPECCIÓN ELIMINADO <----
        
        factor_teleport = settings.FACTOR_UMBRAL_TELETRANSPORTACION
        # Añadimos un umbral absoluto mínimo para evitar falsos positivos cuando el movimiento solicitado es muy pequeño.
        # Por ejemplo, si dx_solicitado es 0.1, 0.1 * 1.5 = 0.15. Un movimiento de 0.5 ya sería > 0.15.
        # Queremos evitar que pequeños ajustes/rebotes se consideren teletransporte.
        # Este umbral mínimo podría ser un valor como 2-5 píxeles.
        min_mov_para_factor_check = 2.0 # Píxeles. Si el mov solicitado es menor, usamos un umbral absoluto más grande.
        umbral_abs_teleport_peq_mov = 5.0 # Píxeles. Si el mov solicitado es < min_mov_para_factor_check, entonces un mov real > umbral_abs_teleport_peq_mov es teleport.

        print(f"DEBUG_CH_TP: factor_teleport={factor_teleport}, min_mov_para_factor_check={min_mov_para_factor_check}, umbral_abs_teleport_peq_mov={umbral_abs_teleport_peq_mov}")

        teleport_detectado_x = False
        teleport_detectado_y = False
        print(f"DEBUG_CH_TP: Antes de checkear teleport X")

        # Comprobar teletransporte en X
        if distancia_solicitada_x < min_mov_para_factor_check: # Movimiento solicitado muy pequeño
            if distancia_movida_x > umbral_abs_teleport_peq_mov:
                teleport_detectado_x = True
                print(f"DEBUG_CH_TP: TELEPORTE X DETECTADO (solicitado < {min_mov_para_factor_check}, movido > {umbral_abs_teleport_peq_mov})")
        elif distancia_movida_x > (distancia_solicitada_x * factor_teleport): # Movimiento solicitado normal, aplicar factor
            # Adicionalmente, para que no salte por movimientos pequeños aunque el factor se cumpla:
            # El movimiento real también debe superar un mínimo absoluto si el solicitado era pequeño.
            # Ejemplo: sol=1, mov=1.6 (1.6 > 1*1.5). Esto podría ser un ajuste normal.
            # Queremos que también distancia_movida_x sea significativamente grande en sí misma.
            # Podríamos añadir: and distancia_movida_x > umbral_abs_teleport_peq_mov (o un valor similar)
            if distancia_movida_x > umbral_abs_teleport_peq_mov: # Solo considera teletransporte si el movimiento real supera un mínimo
                teleport_detectado_x = True
                print(f"DEBUG_CH_TP: TELEPORTE X DETECTADO (solicitado >= {min_mov_para_factor_check}, movido > solicitado * {factor_teleport} Y movido > {umbral_abs_teleport_peq_mov})")
            else:
                print(f"DEBUG_CH_TP: NO TELEPORTE X (movido ({distancia_movida_x:.2f}) no superó umbral absoluto {umbral_abs_teleport_peq_mov} aunque factor se cumplió)")
        
        if teleport_detectado_x and log_habilitado:
            logger.warning(f"CH_TELEPORT_DETECT: X. Movido: {distancia_movida_x:.2f} (Actual: {pos_actual_x}, SeguraF1: {pos_segura_fase1_x}) vs Solicitado: {distancia_solicitada_x:.2f} (Factor: {factor_teleport})", extra={"categoria_log": "log_collision_handler"})
        
        print(f"DEBUG_CH_TP: Antes de checkear teleport Y. teleport_detectado_x={teleport_detectado_x}")
        
        # Comprobar teletransporte en Y
        if distancia_solicitada_y < min_mov_para_factor_check: # Movimiento solicitado muy pequeño
            if distancia_movida_y > umbral_abs_teleport_peq_mov:
                teleport_detectado_y = True
                print(f"DEBUG_CH_TP: TELEPORTE Y DETECTADO (solicitado < {min_mov_para_factor_check}, movido > {umbral_abs_teleport_peq_mov})")
        elif distancia_movida_y > (distancia_solicitada_y * factor_teleport): # Movimiento solicitado normal, aplicar factor
            if distancia_movida_y > umbral_abs_teleport_peq_mov:
                teleport_detectado_y = True
                print(f"DEBUG_CH_TP: TELEPORTE Y DETECTADO (solicitado >= {min_mov_para_factor_check}, movido > solicitado * {factor_teleport} Y movido > {umbral_abs_teleport_peq_mov})")
            else:
                print(f"DEBUG_CH_TP: NO TELEPORTE Y (movido ({distancia_movida_y:.2f}) no superó umbral absoluto {umbral_abs_teleport_peq_mov} aunque factor se cumplió)")

        if teleport_detectado_y and log_habilitado:
            logger.warning(f"CH_TELEPORT_DETECT: Y. Movido: {distancia_movida_y:.2f} (Actual: {pos_actual_y}, SeguraF1: {pos_segura_fase1_y}) vs Solicitado: {distancia_solicitada_y:.2f} (Factor: {factor_teleport})", extra={"categoria_log": "log_collision_handler"})

        print(f"DEBUG_CH_TP: Antes de if (teleport_detectado_x or teleport_detectado_y). X={teleport_detectado_x}, Y={teleport_detectado_y}")
        if teleport_detectado_x or teleport_detectado_y:
            if log_habilitado:
                logger.warning(f"CH_TELEPORT_CORRECT: Revirtiendo a posición segura de Fase 1: ({pos_segura_fase1_x}, {pos_segura_fase1_y})", extra={"categoria_log": "log_collision_handler"})
            print(f"DEBUG_CH_TP: _prevenir_teletransportacion - TELEPORTE DETECTADO (general). Revirtiendo a pos_segura_fase1: ({pos_segura_fase1_x},{pos_segura_fase1_y})")
            return pos_segura_fase1_x, pos_segura_fase1_y
        else:
            print(f"DEBUG_CH_TP: _prevenir_teletransportacion - SIN TELEPORTE (general). Devolviendo pos_actual: ({pos_actual_x},{pos_actual_y})")
            return pos_actual_x, pos_actual_y

    @staticmethod
    def gestionar_movimiento_y_colision(entidad_actual, entidad_hitbox, entidad_rect, hitbox_offset_x, hitbox_offset_y, dx, dy, obstaculos, mundo_ancho, mundo_alto):
        ent_name_for_print = getattr(entidad_actual, 'nombre_log_entidad', type(entidad_actual).__name__)
        print(f"DEBUG_CH: Entrando a GESTIONAR_MOVIMIENTO_Y_COLISION para: {ent_name_for_print}, dx: {dx:.2f}, dy: {dy:.2f}, HB_In: {entidad_hitbox.topleft}")
        # --- IMPORTACIONES LOCALES PARA EVITAR CICLOS (si no están ya globales con TYPE_CHECKING) ---
        from src.entidades.jugador import Jugador
        # from src.entidades.enemigo import Enemigo # Ya no se usa directamente aquí para lógica específica

        # Obtener referencias a las funciones miembro para acortar las llamadas
        resolver_solapamientos_estaticos_eje_func = CollisionHandler._resolver_solapamientos_estaticos_eje
        aplicar_movimiento_y_colision_eje_x_func = CollisionHandler._aplicar_movimiento_y_colision_eje_x
        aplicar_movimiento_y_colision_eje_y_func = CollisionHandler._aplicar_movimiento_y_colision_eje_y
        verificar_y_revertir_colision_post_fase2_func = CollisionHandler._verificar_y_revertir_colision_post_fase2
        prevenir_teletransportacion_func = CollisionHandler._prevenir_teletransportacion

        # --- Logging y Referencias Iniciales ---
        log_habilitado = settings.MODO_DEBUG_LOGS and settings.LOG_CATEGORIAS.get("log_collision_handler", False)
        if log_habilitado:
            ent_name = getattr(entidad_actual, 'nombre_log_entidad', type(entidad_actual).__name__)
            ent_id = getattr(entidad_actual, 'id_entidad', 'N/A')
            logger.info(f"--- CH_GMC Entrando a gestionar_movimiento_y_colision para: {ent_name}_ID:{ent_id} ---", extra={"categoria_log": "log_collision_handler"})
            logger.debug(f"    CH_GMC_INPUT: dx={dx:.4f}, dy={dy:.4f}, HB_Ent_Inicial: {entidad_hitbox.topleft}, Rect_Ent_Inicial: {entidad_rect.topleft}", extra={"categoria_log": "log_collision_handler"})

        hb_original_x = entidad_hitbox.x
        hb_original_y = entidad_hitbox.y

        # --- Fase 1: Resolver Solapamientos Estáticos ---
        # Primero, asegurar que la entidad no esté ya solapada con obstáculos estáticos.
        # Esto se hace en dos sub-pasos, uno para cada eje, sin aplicar el movimiento del frame actual aún.
        if log_habilitado: logger.debug("    CH_GMC: Iniciando Fase 1 - Resolver Solapamientos Estáticos (Eje X)", extra={"categoria_log": "log_collision_handler"})
        resolver_solapamientos_estaticos_eje_func(entidad_actual, entidad_hitbox, obstaculos, 'x', dx)
        if log_habilitado: logger.debug(f"    CH_GMC: Después de Fase 1 (Eje X). HB_Ent: {entidad_hitbox.topleft}", extra={"categoria_log": "log_collision_handler"})
        
        if log_habilitado: logger.debug("    CH_GMC: Iniciando Fase 1 - Resolver Solapamientos Estáticos (Eje Y)", extra={"categoria_log": "log_collision_handler"})
        resolver_solapamientos_estaticos_eje_func(entidad_actual, entidad_hitbox, obstaculos, 'y', dy)
        if log_habilitado: logger.debug(f"    CH_GMC: Después de Fase 1 (Eje Y). HB_Ent: {entidad_hitbox.topleft}", extra={"categoria_log": "log_collision_handler"})
        print(f"DEBUG_CH: GESTIONAR_MOVIMIENTO_Y_COLISION ({ent_name_for_print}) - Después de Fase 1 (Resolver Solap. Estáticos Eje Y), HB: {entidad_hitbox.topleft}")

        # Guardar la posición después de la Fase 1 como una "posición segura"
        hb_pos_segura_fase1_x = entidad_hitbox.x
        hb_pos_segura_fase1_y = entidad_hitbox.y
        
        # --- Fase 2: Aplicar Movimiento y Resolver Colisiones (Eje por Eje) ---
        # El movimiento se aplica primero en X, luego en Y.
        if log_habilitado: logger.debug(f"    --- CH: Inicio _aplicar_movimiento_y_colision_eje_x --- dx: {dx}, HB_in: {entidad_hitbox.topleft} (Esta HB_in es post-Fase1)", extra={"categoria_log": "log_collision_handler"})
        dx_real_aplicado_a_hb_fase1 = aplicar_movimiento_y_colision_eje_x_func(entidad_hitbox, dx, obstaculos, mundo_ancho, mundo_alto)
        entidad_hitbox.x = round(hb_pos_segura_fase1_x + dx_real_aplicado_a_hb_fase1) # Aplicar delta a la X de después de Fase 1
        if log_habilitado: logger.debug(f"    --- CH: Fin _aplicar_movimiento_y_colision_eje_x --- HB_out X: {entidad_hitbox.x:.2f}", extra={"categoria_log": "log_collision_handler"})
        if log_habilitado: logger.debug(f"    CH_GMC: Después de Fase 2 (Eje X). HB_Ent.x: {entidad_hitbox.x}", extra={"categoria_log": "log_collision_handler"})
        print(f"DEBUG_CH: GESTIONAR_MOVIMIENTO_Y_COLISION ({ent_name_for_print}) - Después de Fase 2 (Aplicar Movimiento Eje X), HB.x: {entidad_hitbox.x}")

        # La entidad_hitbox que entra a _aplicar_movimiento_y_colision_eje_y_func
        # ya tiene su .x actualizado por el paso anterior. Su .y sigue siendo hb_pos_segura_fase1_y (el de después de Fase 1Y).
        if log_habilitado: logger.debug(f"    --- CH: Inicio _aplicar_movimiento_y_colision_eje_y --- dy: {dy}, HB_in: {entidad_hitbox.topleft} (Esta HB_in es post-Fase1Y y post-Fase2X)", extra={"categoria_log": "log_collision_handler"})
        dy_real_aplicado_a_hb_fase1 = aplicar_movimiento_y_colision_eje_y_func(entidad_hitbox, dy, obstaculos, mundo_ancho, mundo_alto)
        entidad_hitbox.y = round(hb_pos_segura_fase1_y + dy_real_aplicado_a_hb_fase1) # Aplicar delta a la Y de después de Fase 1
        if log_habilitado: logger.debug(f"    --- CH: Fin _aplicar_movimiento_y_colision_eje_y --- HB_out Y: {entidad_hitbox.y:.2f}", extra={"categoria_log": "log_collision_handler"})
        if log_habilitado: logger.debug(f"    CH_GMC: Después de Fase 2 (Eje Y). HB_Ent.y: {entidad_hitbox.y}", extra={"categoria_log": "log_collision_handler"})
        print(f"DEBUG_CH: GESTIONAR_MOVIMIENTO_Y_COLISION ({ent_name_for_print}) - Después de Fase 2 (Aplicar Movimiento Eje Y), HB.y: {entidad_hitbox.y}")
        
        # --- Fase 3: Verificación Post-Fase2 y Prevención de Atascamientos ---
        print(f"DEBUG_CH: GESTIONAR_MOVIMIENTO_Y_COLISION ({ent_name_for_print}) - ANTES de llamar a Fase 3 (_verificar_y_revertir_colision_post_fase2), HB: {entidad_hitbox.topleft}")
        if log_habilitado: logger.debug(f"    --- CH: Inicio _verificar_y_revertir_colision_post_fase2 --- HB_Entrada: {entidad_hitbox.topleft}", extra={"categoria_log": "log_collision_handler"})
        
        # Guardamos los valores retornados por si los necesitamos, aunque la función modifica el hitbox por referencia.
        revertido_f1, revertido_orig = verificar_y_revertir_colision_post_fase2_func(
            entidad_actual, entidad_hitbox, obstaculos, 
            hb_pos_segura_fase1_x, hb_pos_segura_fase1_y,
            hb_original_x, hb_original_y,
            dx, dy # Pasamos el intento de movimiento original del frame
        )
        print(f"DEBUG_CH: GESTIONAR_MOVIMIENTO_Y_COLISION ({ent_name_for_print}) - DESPUÉS de llamar a Fase 3 (_verificar_y_revertir_colision_post_fase2), HB: {entidad_hitbox.topleft}, RevertidoF1: {revertido_f1}, RevertidoORIG: {revertido_orig}")

        if log_habilitado: logger.debug(f"    CH_GMC: Después de Fase 3. HB_Ent: {entidad_hitbox.topleft}", extra={"categoria_log": "log_collision_handler"})
        # print(f"DEBUG_CH: GESTIONAR_MOVIMIENTO_Y_COLISION ({ent_name_for_print}) - Después de Fase 3 (Verificar y Revertir), HB: {entidad_hitbox.topleft}") # <--- PRINT ANTERIOR COMENTADO/ELIMINADO

        # --- Fase 4: Prevención de Teletransportación (Comparar con Fase 1 Segura) ---
        print(f"DEBUG_CH: GESTIONAR_MOVIMIENTO_Y_COLISION ({ent_name_for_print}) - ANTES de llamar a Fase 4 (_prevenir_teletransportacion), HB: {entidad_hitbox.topleft}")
        entidad_hitbox.x, entidad_hitbox.y = prevenir_teletransportacion_func(
            entidad_hitbox, dx, dy, hb_pos_segura_fase1_x, hb_pos_segura_fase1_y
        )

        # --- Fase 5: Sincronizar Rect con Hitbox Final ---
        # El rect de la entidad (usado para renderizar) debe actualizarse con la posición final del hitbox.
        # La forma de hacerlo depende de cómo se relacione el rect con el hitbox (ej. hitbox centrado en rect).
        # Asumimos la lógica de EntidadBase: rect.topleft se ajusta por los offsets.
        entidad_rect.x = entidad_hitbox.x - hitbox_offset_x
        entidad_rect.y = entidad_hitbox.y - hitbox_offset_y
        # O si el hitbox está centrado: entidad_rect.center = entidad_hitbox.center
        if log_habilitado: logger.debug(f"    CH_GMC: Fase 5 - Sincronización Rect. Rect_Ent Final: {entidad_rect.topleft} (desde HB: {entidad_hitbox.topleft})", extra={"categoria_log": "log_collision_handler"})

        # Calcular el delta de movimiento real del hitbox
        delta_x_real_hb = entidad_hitbox.x - hb_original_x
        delta_y_real_hb = entidad_hitbox.y - hb_original_y

        if log_habilitado:
            logger.info(f"--- CH_GMC Saliendo de gestionar_movimiento_y_colision para: {ent_name}_ID:{ent_id} ---", extra={"categoria_log": "log_collision_handler"})
            logger.debug(f"    CH_GMC_OUTPUT: Delta Real (dx,dy): ({delta_x_real_hb}, {delta_y_real_hb}). HB_Ent Final: {entidad_hitbox.topleft}, Rect_Ent Final: {entidad_rect.topleft}", extra={"categoria_log": "log_collision_handler"})

        print(f"DEBUG_CH: Saliendo de GESTIONAR_MOVIMIENTO_Y_COLISION para: {ent_name_for_print}, HB_Out: {entidad_hitbox.topleft}")
        return delta_x_real_hb, delta_y_real_hb

    @staticmethod
    def resolver_colisiones_dinamicas_entidad_a_entidad(entidad_actual, otra_entidad):
        log_habilitado = settings.MODO_DEBUG_LOGS and settings.LOG_CATEGORIAS.get("log_collision_handler", False)
        if not hasattr(entidad_actual, 'hitbox') or not hasattr(otra_entidad, 'hitbox'):
            if log_habilitado:
                logger.warning("CH_RCD: Intento de resolver colisión dinámica, pero una o ambas entidades no tienen hitbox.", extra={"categoria_log": "log_collision_handler"})
            return False, None, None

        if entidad_actual.hitbox.colliderect(otra_entidad.hitbox):
            overlap_x = min(entidad_actual.hitbox.right, otra_entidad.hitbox.right) - max(entidad_actual.hitbox.left, otra_entidad.hitbox.left)
            overlap_y = min(entidad_actual.hitbox.bottom, otra_entidad.hitbox.bottom) - max(entidad_actual.hitbox.top, otra_entidad.hitbox.top)
            
            if log_habilitado:
                nombre_actual_log = getattr(entidad_actual, 'nombre_log_entidad', type(entidad_actual).__name__)
                id_actual_log = getattr(entidad_actual, 'id_entidad', 'N/A')
                nombre_otra_log = getattr(otra_entidad, 'nombre_log_entidad', type(otra_entidad).__name__)
                id_otra_log = getattr(otra_entidad, 'id_entidad', 'N/A')
                logger.info(f"CH_RCD: Colisión detectada entre {nombre_actual_log}_ID:{id_actual_log} y {nombre_otra_log}_ID:{id_otra_log}. Overlap (x,y): ({overlap_x}, {overlap_y})", extra={"categoria_log": "log_collision_handler"})
            return True, overlap_x, overlap_y
        
        return False, None, None 