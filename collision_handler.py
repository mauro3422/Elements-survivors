import pygame
import logging

class CollisionHandler:
    @staticmethod
    def _resolver_solapamientos_estaticos_eje(entidad_hitbox, entidad_rect, hitbox_offset_x, hitbox_offset_y, obstaculos, eje, movimiento_input_en_eje, logger):
        # El logger ya no se obtiene de self, sino que se pasa como argumento
        logger.debug(f"    --- Inicio _resolver_solapamientos_estaticos_eje ({eje}) --- Input en eje: {movimiento_input_en_eje}")
        MAX_PASADAS_RESOLUCION_ESTATICA = 5
        for pasada in range(MAX_PASADAS_RESOLUCION_ESTATICA):
            colision_resuelta_en_pasada = False
            logger.debug(f"      Pasada {pasada + 1} de resolución estática eje {eje}")

            for i, obstaculo in enumerate(obstaculos):
                rect_colision_obstaculo = obstaculo.hitbox if hasattr(obstaculo, 'hitbox') else obstaculo.rect
                obst_id_log = f"{type(obstaculo).__name__}_{getattr(obstaculo, 'id_enemigo', i)}"

                if entidad_hitbox.colliderect(rect_colision_obstaculo):
                    logger.debug(f"        SOLAPAMIENTO ESTÁTICO EJE {eje} DETECTADO con {obst_id_log} en pasada {pasada + 1}")
                    logger.debug(f"          Entidad Hitbox ANTES: {entidad_hitbox.topleft}, Obstáculo {obst_id_log} Hitbox: rect={rect_colision_obstaculo.topleft}, size={rect_colision_obstaculo.size}")
                    
                    hitbox_modificado_este_obstaculo = False
                    if eje == 'x':
                        x_antes_de_ajuste_actual = entidad_hitbox.x
                        obstaculo_a_la_derecha = rect_colision_obstaculo.centerx > entidad_hitbox.centerx
                        
                        if obstaculo_a_la_derecha:
                            entidad_hitbox.x -= 1
                            logger.debug(f"          Pre-Corrección X (estática) FORZADA: Obstáculo a la DERECHA. Mover ENTIDAD 1px IZQUIERDA. Input dx={movimiento_input_en_eje}")
                        else: 
                            entidad_hitbox.x += 1
                            logger.debug(f"          Pre-Corrección X (estática) FORZADA: Obstáculo a la IZQUIERDA. Mover ENTIDAD 1px DERECHA. Input dx={movimiento_input_en_eje}")
                        
                        if entidad_hitbox.x != x_antes_de_ajuste_actual:
                            hitbox_modificado_este_obstaculo = True

                    elif eje == 'y':
                        y_antes_de_ajuste_actual = entidad_hitbox.y
                        obstaculo_abajo = rect_colision_obstaculo.centery > entidad_hitbox.centery

                        if obstaculo_abajo:
                            entidad_hitbox.y -= 1
                            logger.debug(f"          Pre-Corrección Y (estática) FORZADA: Obstáculo ABAJO. Mover ENTIDAD 1px ARRIBA. Input dy={movimiento_input_en_eje}")
                        else: 
                            entidad_hitbox.y += 1
                            logger.debug(f"          Pre-Corrección Y (estática) FORZADA: Obstáculo ARRIBA. Mover ENTIDAD 1px ABAJO. Input dy={movimiento_input_en_eje}")

                        if entidad_hitbox.y != y_antes_de_ajuste_actual:
                            hitbox_modificado_este_obstaculo = True

                    if hitbox_modificado_este_obstaculo:
                        colision_resuelta_en_pasada = True
                        # Actualizar rect de la entidad para el logging, si es necesario (opcional aquí)
                        # entidad_rect.x = entidad_hitbox.x - hitbox_offset_x
                        # entidad_rect.y = entidad_hitbox.y - hitbox_offset_y
                        logger.debug(f"            Post-Pre-Corrección EJE {eje} (estática) contra {obst_id_log}: Entidad Hitbox: {entidad_hitbox.topleft}") # Rect logueado por la func principal
            
            if not colision_resuelta_en_pasada: 
                logger.debug(f"      No más solapamientos estáticos detectados/resueltos en eje {eje} en pasada {pasada + 1}. Saliendo.")
                break 
            else: 
                logger.debug(f"      Fin de pasada {pasada + 1} de resolución estática eje {eje}. Hubo correcciones. Hitbox actual: {entidad_hitbox.topleft}")
        
        logger.debug(f"    --- Fin _resolver_solapamientos_estaticos_eje ({eje}) --- Hitbox final: {entidad_hitbox.topleft}")

    @staticmethod
    def _aplicar_movimiento_y_colision_eje_x(entidad_hitbox, dx_aplicado, obstaculos, pos_original_hitbox_x_antes_de_intento_f2, logger):
        logger.debug(f"    --- Inicio _aplicar_movimiento_y_colision_eje_x --- dx_aplicado: {dx_aplicado}")
        if dx_aplicado != 0:
            entidad_hitbox.x += dx_aplicado
            logger.debug(f"      PRINT CHECK Fase 2 (eje X): Intento mov X a {entidad_hitbox.x} (dx: {dx_aplicado})")

            colision_inicial_x_detectada = False
            for i, obstaculo in enumerate(obstaculos):
                rect_colision_obstaculo = obstaculo.hitbox if hasattr(obstaculo, 'hitbox') else obstaculo.rect
                if entidad_hitbox.colliderect(rect_colision_obstaculo):
                    colision_inicial_x_detectada = True
                    logger.debug(f"      PRINT CHECK Fase 2 (eje X): Colisión X INMEDIATA tras mov con obstaculo {i} ({type(obstaculo).__name__})")
                    
                    if dx_aplicado > 0:
                        entidad_hitbox.x -= 1
                        logger.debug(f"        PRINT CHECK Fase 2 (eje X): Empujón X (-1). Hitbox.x={entidad_hitbox.x}")
                    elif dx_aplicado < 0:
                        entidad_hitbox.x += 1
                        logger.debug(f"        PRINT CHECK Fase 2 (eje X): Empujón X (+1). Hitbox.x={entidad_hitbox.x}")
                    
                    colision_persiste_tras_empujon_x = False
                    obstaculo_persistente_x = None
                    for obst_check_x in obstaculos:
                        rect_obst_check_x = obst_check_x.hitbox if hasattr(obst_check_x, 'hitbox') else obst_check_x.rect
                        if entidad_hitbox.colliderect(rect_obst_check_x):
                            colision_persiste_tras_empujon_x = True
                            obstaculo_persistente_x = obst_check_x
                            break 
                    
                    if colision_persiste_tras_empujon_x:
                        logger.warning(f"        WARN Fase 2 X: Colisión persiste con {type(obstaculo_persistente_x).__name__} DESPUÉS de empujón. Revertiendo X.")
                        entidad_hitbox.x = pos_original_hitbox_x_antes_de_intento_f2
                        logger.warning(f"          WARN Fase 2 X: Movimiento en X CANCELADO. Hitbox X revertido a: {entidad_hitbox.x}")
                    else:
                        logger.debug(f"        PRINT CHECK Fase 2 X: Empujón resolvió colisión en X.")
                    break 
            
            if not colision_inicial_x_detectada:
                 logger.debug(f"      PRINT CHECK Fase 2 X: No hubo colisión inmediata en X. Movimiento X aplicado final: {entidad_hitbox.x}")
        
        logger.debug(f"    --- Fin _aplicar_movimiento_y_colision_eje_x --- Hitbox X final: {entidad_hitbox.x}")

    @staticmethod
    def _aplicar_movimiento_y_colision_eje_y(entidad_hitbox, dy_aplicado, obstaculos, pos_original_hitbox_y_antes_de_intento_f2, logger):
        logger.debug(f"    --- Inicio _aplicar_movimiento_y_colision_eje_y --- dy_aplicado: {dy_aplicado}")
        if dy_aplicado != 0:
            entidad_hitbox.y += dy_aplicado
            logger.debug(f"      PRINT CHECK Fase 2 (eje Y): Intento mov Y a {entidad_hitbox.y} (dy: {dy_aplicado})")

            colision_inicial_y_detectada = False
            for i, obstaculo in enumerate(obstaculos):
                rect_colision_obstaculo = obstaculo.hitbox if hasattr(obstaculo, 'hitbox') else obstaculo.rect
                if entidad_hitbox.colliderect(rect_colision_obstaculo):
                    colision_inicial_y_detectada = True
                    logger.debug(f"      PRINT CHECK Fase 2 (eje Y): Colisión Y INMEDIATA tras mov con obstaculo {i} ({type(obstaculo).__name__})")

                    if dy_aplicado > 0:
                        entidad_hitbox.y -= 1
                        logger.debug(f"        PRINT CHECK Fase 2 (eje Y): Empujón Y (-1). Hitbox.y={entidad_hitbox.y}")
                    elif dy_aplicado < 0:
                        entidad_hitbox.y += 1
                        logger.debug(f"        PRINT CHECK Fase 2 (eje Y): Empujón Y (+1). Hitbox.y={entidad_hitbox.y}")
                    
                    colision_persiste_tras_empujon_y = False
                    obstaculo_persistente_y = None
                    for obst_check_y in obstaculos:
                        rect_obst_check_y = obst_check_y.hitbox if hasattr(obst_check_y, 'hitbox') else obst_check_y.rect
                        if entidad_hitbox.colliderect(rect_obst_check_y):
                            colision_persiste_tras_empujon_y = True
                            obstaculo_persistente_y = obst_check_y
                            break
                            
                    if colision_persiste_tras_empujon_y:
                        logger.warning(f"        WARN Fase 2 Y: Colisión persiste con {type(obstaculo_persistente_y).__name__} DESPUÉS de empujón. Revertiendo Y.")
                        entidad_hitbox.y = pos_original_hitbox_y_antes_de_intento_f2
                        logger.warning(f"          WARN Fase 2 Y: Movimiento en Y CANCELADO. Hitbox Y revertido a: {entidad_hitbox.y}")
                    else:
                        logger.debug(f"        PRINT CHECK Fase 2 Y: Empujón resolvió colisión en Y.")
                    break 
            
            if not colision_inicial_y_detectada:
                logger.debug(f"      PRINT CHECK Fase 2 Y: No hubo colisión inmediata en Y. Movimiento Y aplicado final: {entidad_hitbox.y}")
        
        logger.debug(f"    --- Fin _aplicar_movimiento_y_colision_eje_y --- Hitbox Y final: {entidad_hitbox.y}")

    @staticmethod
    def _verificar_y_revertir_colision_post_fase2(entidad_hitbox, obstaculos, pos_segura_fase1_x, pos_segura_fase1_y, logger):
        logger.debug("    --- Inicio _verificar_y_revertir_colision_post_fase2 ---")
        colision_global_tras_fase2 = False
        obstaculo_colisionante_global = None
        for obstaculo in obstaculos:
            rect_colision_obstaculo = obstaculo.hitbox if hasattr(obstaculo, 'hitbox') else obstaculo.rect
            if entidad_hitbox.colliderect(rect_colision_obstaculo):
                colision_global_tras_fase2 = True
                obstaculo_colisionante_global = obstaculo
                break
        
        hubo_reversion_global = False
        if colision_global_tras_fase2:
            # La corrección del AttributeError ya está aquí
            logger.warning(f"WARN Global (post-F2): Entidad AÚN colisiona con {type(obstaculo_colisionante_global).__name__} ({getattr(getattr(obstaculo_colisionante_global, 'rect', None), 'topleft', 'N/A')}) DESPUÉS de Fase 2 completa.")
            logger.warning(f"  Entidad Hitbox: {entidad_hitbox.topleft}. Pos Segura Fase 1: ({pos_segura_fase1_x}, {pos_segura_fase1_y})")
            logger.warning(f"  Revertiendo AMBOS EJES a posición segura de Fase 1.")
            entidad_hitbox.x = pos_segura_fase1_x
            entidad_hitbox.y = pos_segura_fase1_y
            hubo_reversion_global = True
            logger.warning(f"  WARN Global (post-F2): Posición REVERTIDA A FASE 1. Hitbox: {entidad_hitbox.topleft}")

            colision_aun_despues_de_reversion_a_fase1 = False
            obstaculo_critico_final = None
            rect_obst_critico_info = "N/A"
            for obst_check_critico in obstaculos:
                rect_obst_check_critico = obst_check_critico.hitbox if hasattr(obst_check_critico, 'hitbox') else obst_check_critico.rect
                if entidad_hitbox.colliderect(rect_obst_check_critico):
                    colision_aun_despues_de_reversion_a_fase1 = True
                    obstaculo_critico_final = obst_check_critico
                    rect_obst_critico_info = rect_obst_check_critico
                    break
            if colision_aun_despues_de_reversion_a_fase1:
                nombre_obst_critico = type(obstaculo_critico_final).__name__ if obstaculo_critico_final else "ObstaculoDesconocido"
                pos_obst_critico_info = getattr(rect_obst_critico_info, 'topleft', 'N/A')
                logger.critical(f"CRITICAL POST-REVERSION (Fase1): Entidad AÚN COLISIONA con {nombre_obst_critico} DESPUÉS de revertir. Hitbox: {entidad_hitbox.topleft}, Rect Obst: {pos_obst_critico_info}")
        
        logger.debug("    --- Fin _verificar_y_revertir_colision_post_fase2 ---")
        return hubo_reversion_global

    @staticmethod
    def _prevenir_teletransportacion(entidad_hitbox, dx_solicitado, dy_solicitado, pos_segura_fase1_x, pos_segura_fase1_y, logger):
        logger.debug("    --- Inicio _prevenir_teletransportacion ---")
        distancia_movimiento_x_desde_segura = abs(entidad_hitbox.x - pos_segura_fase1_x)
        distancia_movimiento_y_desde_segura = abs(entidad_hitbox.y - pos_segura_fase1_y)
        
        # Usar entidad_hitbox.width/height directamente
        umbral_x = abs(dx_solicitado) + entidad_hitbox.width 
        umbral_y = abs(dy_solicitado) + entidad_hitbox.height
        UMBRAL_TELETRANSPORTACION_X = max(umbral_x, entidad_hitbox.width * 1.5)
        UMBRAL_TELETRANSPORTACION_Y = max(umbral_y, entidad_hitbox.height * 1.5)

        reversion_por_tp = False
        if (distancia_movimiento_x_desde_segura > UMBRAL_TELETRANSPORTACION_X or
            distancia_movimiento_y_desde_segura > UMBRAL_TELETRANSPORTACION_Y):
            logger.critical(f"FATAL_WARN (Anti-TP): ¡Teletransportación POTENCIAL detectada!")
            logger.critical(f"  Hitbox actual: {entidad_hitbox.topleft}, Pos Segura Fase 1: ({pos_segura_fase1_x}, {pos_segura_fase1_y})")
            logger.critical(f"  Input frame: dx={dx_solicitado}, dy={dy_solicitado}")
            logger.critical(f"  Dist X: {distancia_movimiento_x_desde_segura} (Umbral: {UMBRAL_TELETRANSPORTACION_X}), Dist Y: {distancia_movimiento_y_desde_segura} (Umbral: {UMBRAL_TELETRANSPORTACION_Y})")
            logger.critical(f"  Revirtiendo a posición segura de Fase 1.")
            entidad_hitbox.x = pos_segura_fase1_x
            entidad_hitbox.y = pos_segura_fase1_y
            reversion_por_tp = True
            logger.critical(f"  Posición REVERTIDA POR CORTAFUEGOS (Anti-TP). Hitbox: {entidad_hitbox.topleft}")
        
        logger.debug("    --- Fin _prevenir_teletransportacion ---")
        return reversion_por_tp

    @staticmethod
    def gestionar_movimiento_y_colision(entidad_hitbox, entidad_rect, hitbox_offset_x, hitbox_offset_y, dx, dy, obstaculos, logger):
        logger.debug(f"[CollisionHandler.gestionar_movimiento_y_colision] Entrando. dx={dx}, dy={dy}.")
        
        # Fase 1: Pre-Corrección Estática
        logger.debug("******************** CollisionHandler: Inicio Fase 1: Pre-Correccion Estatica ********************")
        CollisionHandler._resolver_solapamientos_estaticos_eje(entidad_hitbox, entidad_rect, hitbox_offset_x, hitbox_offset_y, obstaculos, 'x', dx, logger)
        CollisionHandler._resolver_solapamientos_estaticos_eje(entidad_hitbox, entidad_rect, hitbox_offset_x, hitbox_offset_y, obstaculos, 'y', dy, logger)
        
        entidad_rect.x = entidad_hitbox.x - hitbox_offset_x
        entidad_rect.y = entidad_hitbox.y - hitbox_offset_y
        logger.debug(f"CollisionHandler: --- Fin Fase 1. Entidad Hitbox: {entidad_hitbox.topleft}, Entidad Rect: {entidad_rect.topleft} ---")

        pos_segura_hitbox_x_tras_fase1 = entidad_hitbox.x
        pos_segura_hitbox_y_tras_fase1 = entidad_hitbox.y

        # Fase 2: Movimiento y Colisión por Ejes
        logger.debug("CollisionHandler: --- Inicio Fase 2: Movimiento y Colision --- ")
        CollisionHandler._aplicar_movimiento_y_colision_eje_x(entidad_hitbox, dx, obstaculos, pos_segura_hitbox_x_tras_fase1, logger)
        CollisionHandler._aplicar_movimiento_y_colision_eje_y(entidad_hitbox, dy, obstaculos, pos_segura_hitbox_y_tras_fase1, logger)
            
        entidad_rect.x = entidad_hitbox.x - hitbox_offset_x
        entidad_rect.y = entidad_hitbox.y - hitbox_offset_y
        logger.debug(f"CollisionHandler: --- Fin Fase 2. Entidad Hitbox: {entidad_hitbox.topleft}, Entidad Rect: {entidad_rect.topleft} ---")
            
        # Medida de Seguridad Adicional
        hubo_reversion_global = CollisionHandler._verificar_y_revertir_colision_post_fase2(entidad_hitbox, obstaculos, pos_segura_hitbox_x_tras_fase1, pos_segura_hitbox_y_tras_fase1, logger)
        if hubo_reversion_global:
            entidad_rect.x = entidad_hitbox.x - hitbox_offset_x
            entidad_rect.y = entidad_hitbox.y - hitbox_offset_y

        # Cortafuegos Anti-Teletransportación
        hubo_reversion_por_tp = CollisionHandler._prevenir_teletransportacion(entidad_hitbox, dx, dy, pos_segura_hitbox_x_tras_fase1, pos_segura_hitbox_y_tras_fase1, logger)
        if hubo_reversion_por_tp:
            entidad_rect.x = entidad_hitbox.x - hitbox_offset_x
            entidad_rect.y = entidad_hitbox.y - hitbox_offset_y

        logger.debug(f"CollisionHandler: --- Fin gestionar_movimiento_y_colision --- Pos FINAL Hitbox: {entidad_hitbox.topleft}, Rect: {entidad_rect.topleft}") 