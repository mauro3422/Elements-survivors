import pygame
import logging
import settings

# Logger específico para CollisionHandler
logger_ch = logging.getLogger("log_collision_handler")
logger_ch.setLevel(logging.DEBUG) # Permitir que pasen todos los mensajes DEBUG

class CollisionHandler:
    @staticmethod
    def _resolver_solapamientos_estaticos_eje(entidad_hitbox, entidad_rect, hitbox_offset_x, hitbox_offset_y, obstaculos, eje, movimiento_input_en_eje):
        if not (settings.MODO_DEBUG_LOGS and settings.LOG_CATEGORIAS.get("log_collision_handler", False)):
            # Si la categoría está desactivada, esta función interna no necesita ejecutarse con logs.
            # La lógica de resolución sí debe ejecutarse siempre.
            # Considerar si los logs son esenciales para la función o si la función puede operar sin ellos.
            # Por ahora, se asume que la función puede operar y solo se omiten los logs.
            pass # Esto es solo para la condición del log, la lógica sigue

        if settings.MODO_DEBUG_LOGS and settings.LOG_CATEGORIAS.get("log_collision_handler", False):
            logger_ch.debug(f"    --- CH: Inicio _resolver_solapamientos_estaticos_eje ({eje}) --- Input: {movimiento_input_en_eje}, HB_in: {entidad_hitbox.topleft}")
        for pasada in range(settings.MAX_PASADAS_RESOLUCION_ESTATICA):
            colision_resuelta_en_pasada = False
            if settings.MODO_DEBUG_LOGS and settings.LOG_CATEGORIAS.get("log_collision_handler", False):
                logger_ch.debug(f"      CH: Pasada {pasada + 1} res. estática eje {eje}")

            for i, obstaculo in enumerate(obstaculos):
                rect_colision_obstaculo = obstaculo.hitbox if hasattr(obstaculo, 'hitbox') else obstaculo.rect
                # Usar nombre_log_entidad si existe, sino un fallback descriptivo.
                obst_id_log = getattr(obstaculo, 'nombre_log_entidad', f"{type(obstaculo).__name__}_idx{i}")

                if entidad_hitbox.colliderect(rect_colision_obstaculo):
                    if settings.MODO_DEBUG_LOGS and settings.LOG_CATEGORIAS.get("log_collision_handler", False):
                        logger_ch.debug(f"        CH: SOLAP. ESTÁTICO EJE {eje} con {obst_id_log} (Pasada {pasada+1}). HB_Ent: {entidad_hitbox.topleft}, HB_Obs: {rect_colision_obstaculo.topleft}")
                    
                    hitbox_modificado_este_obstaculo = False
                    if eje == 'x':
                        x_antes = entidad_hitbox.x
                        # Determinar la dirección del solapamiento basado en los centros
                        # Si el centro de la entidad está a la izquierda del centro del obstáculo,
                        # el solapamiento probable es del lado derecho de la entidad con el lado izquierdo del obstáculo.
                        if entidad_hitbox.centerx < rect_colision_obstaculo.centerx:
                            overlap = entidad_hitbox.right - rect_colision_obstaculo.left
                            if overlap > 0: # Hay solapamiento real en este lado
                                if settings.MODO_DEBUG_LOGS and settings.LOG_CATEGORIAS.get("log_collision_handler", False):
                                    logger_ch.debug(f"          CH: Estático EJE X vs {obst_id_log}: Entidad a la IZQ del Obs. Overlap (Ent.R - Obs.L): {overlap:.2f}. Ajustando Ent.Right.")
                                entidad_hitbox.right = rect_colision_obstaculo.left
                        else: # El centro de la entidad está a la derecha (o coincide) con el centro del obstáculo
                              # el solapamiento probable es del lado izquierdo de la entidad con el lado derecho del obstáculo.
                            overlap = rect_colision_obstaculo.right - entidad_hitbox.left
                            if overlap > 0: # Hay solapamiento real en este lado
                                if settings.MODO_DEBUG_LOGS and settings.LOG_CATEGORIAS.get("log_collision_handler", False):
                                    logger_ch.debug(f"          CH: Estático EJE X vs {obst_id_log}: Entidad a la DER del Obs. Overlap (Obs.R - Ent.L): {overlap:.2f}. Ajustando Ent.Left.")
                                entidad_hitbox.left = rect_colision_obstaculo.right
                        
                        if entidad_hitbox.x != x_antes: 
                            hitbox_modificado_este_obstaculo = True
                            if settings.MODO_DEBUG_LOGS and settings.LOG_CATEGORIAS.get("log_collision_handler", False): # Log adicional si hubo cambio
                                logger_ch.debug(f"          CH: Estático EJE X vs {obst_id_log}: Cambio aplicado. HB_Ent.x antes: {x_antes:.2f}, después: {entidad_hitbox.x:.2f}")
                                
                    elif eje == 'y':
                        y_antes = entidad_hitbox.y
                        # Determinar la dirección del solapamiento basado en los centros
                        # Si el centro de la entidad está arriba del centro del obstáculo,
                        # el solapamiento probable es del lado inferior de la entidad con el lado superior del obstáculo.
                        if entidad_hitbox.centery < rect_colision_obstaculo.centery:
                            overlap = entidad_hitbox.bottom - rect_colision_obstaculo.top
                            if overlap > 0: # Hay solapamiento real en este lado
                                if settings.MODO_DEBUG_LOGS and settings.LOG_CATEGORIAS.get("log_collision_handler", False):
                                    logger_ch.debug(f"          CH: Estático EJE Y vs {obst_id_log}: Entidad ARRIBA del Obs. Overlap (Ent.B - Obs.T): {overlap:.2f}. Ajustando Ent.Bottom.")
                                entidad_hitbox.bottom = rect_colision_obstaculo.top
                        else: # El centro de la entidad está abajo (o coincide) con el centro del obstáculo
                              # el solapamiento probable es del lado superior de la entidad con el lado inferior del obstáculo.
                            overlap = rect_colision_obstaculo.bottom - entidad_hitbox.top
                            if overlap > 0: # Hay solapamiento real en este lado
                                if settings.MODO_DEBUG_LOGS and settings.LOG_CATEGORIAS.get("log_collision_handler", False):
                                    logger_ch.debug(f"          CH: Estático EJE Y vs {obst_id_log}: Entidad ABAJO del Obs. Overlap (Obs.B - Ent.T): {overlap:.2f}. Ajustando Ent.Top.")
                                entidad_hitbox.top = rect_colision_obstaculo.bottom

                        if entidad_hitbox.y != y_antes:
                            hitbox_modificado_este_obstaculo = True
                            if settings.MODO_DEBUG_LOGS and settings.LOG_CATEGORIAS.get("log_collision_handler", False): # Log adicional si hubo cambio
                                logger_ch.debug(f"          CH: Estático EJE Y vs {obst_id_log}: Cambio aplicado. HB_Ent.y antes: {y_antes:.2f}, después: {entidad_hitbox.y:.2f}")

                    if hitbox_modificado_este_obstaculo:
                        colision_resuelta_en_pasada = True
                        if settings.MODO_DEBUG_LOGS and settings.LOG_CATEGORIAS.get("log_collision_handler", False):
                            logger_ch.debug(f"          CH: Post-Pre-Corrección EJE {eje} (estática) vs {obst_id_log}: HB_Ent: {entidad_hitbox.topleft}")
            
            if not colision_resuelta_en_pasada: 
                if settings.MODO_DEBUG_LOGS and settings.LOG_CATEGORIAS.get("log_collision_handler", False):
                    logger_ch.debug(f"      CH: No más solapamientos estáticos eje {eje} en pasada {pasada + 1}. Saliendo.")
                break 
        
        if settings.MODO_DEBUG_LOGS and settings.LOG_CATEGORIAS.get("log_collision_handler", False):
            logger_ch.debug(f"    --- CH: Fin _resolver_solapamientos_estaticos_eje ({eje}) --- HB_out: {entidad_hitbox.topleft}")

    @staticmethod
    def _aplicar_movimiento_y_colision_eje_x(entidad_hitbox, dx_aplicado, obstaculos):
        if settings.MODO_DEBUG_LOGS and settings.LOG_CATEGORIAS.get("log_collision_handler", False):
            logger_ch.debug(f"    --- CH: Inicio _aplicar_movimiento_y_colision_eje_x --- dx: {dx_aplicado}, HB_in: {entidad_hitbox.topleft}")
        
        x_original_hb = entidad_hitbox.x # Guardar para comparar

        if dx_aplicado != 0:
            # entidad_hitbox.x += dx_aplicado # Asignación directa anterior
            entidad_hitbox.x = int(x_original_hb + dx_aplicado) # Truncamiento explícito
            
            if settings.MODO_DEBUG_LOGS and settings.LOG_CATEGORIAS.get("log_collision_handler", False):
                logger_ch.debug(f"      CH: Fase 2 (X): dx_aplicado={dx_aplicado:.4f}. HB.x original={x_original_hb}, HB.x post-int-trunc={entidad_hitbox.x}")

            for obstaculo in obstaculos:
                rect_colision_obstaculo = obstaculo.hitbox if hasattr(obstaculo, 'hitbox') else obstaculo.rect
                if entidad_hitbox.colliderect(rect_colision_obstaculo):
                    obst_id_log = getattr(obstaculo, 'nombre_log_entidad', f"{type(obstaculo).__name__}_Desconocido")
                    if settings.MODO_DEBUG_LOGS and settings.LOG_CATEGORIAS.get("log_collision_handler", False):
                        logger_ch.debug(f"      CH: Fase 2 (X): Colisión X detectada con {obst_id_log} después de mov. tentativo. HB_Ent: {entidad_hitbox.topleft}, HB_Obs: {rect_colision_obstaculo.topleft}")
                    
                    if dx_aplicado > 0: # Se movía hacia la derecha y colisionó
                        entidad_hitbox.right = rect_colision_obstaculo.left
                        if settings.MODO_DEBUG_LOGS and settings.LOG_CATEGORIAS.get("log_collision_handler", False):
                            logger_ch.debug(f"        CH: Fase 2 (X): Ajustado. Entidad mov. a DER. HB_Ent.right = Obs.left ({entidad_hitbox.right:.2f})")
                    elif dx_aplicado < 0: # Se movía hacia la izquierda y colisionó
                        entidad_hitbox.left = rect_colision_obstaculo.right
                        if settings.MODO_DEBUG_LOGS and settings.LOG_CATEGORIAS.get("log_collision_handler", False):
                            logger_ch.debug(f"        CH: Fase 2 (X): Ajustado. Entidad mov. a IZQ. HB_Ent.left = Obs.right ({entidad_hitbox.left:.2f})")
                    # Una vez que se maneja una colisión en este eje, rompemos el bucle de obstáculos.
                    # La posición ya está ajustada al primer obstáculo encontrado en la dirección del movimiento.
                    break 
        
        if settings.MODO_DEBUG_LOGS and settings.LOG_CATEGORIAS.get("log_collision_handler", False):
            logger_ch.debug(f"    --- CH: Fin _aplicar_movimiento_y_colision_eje_x --- HB_out X: {entidad_hitbox.x:.2f}")

    @staticmethod
    def _aplicar_movimiento_y_colision_eje_y(entidad_hitbox, dy_aplicado, obstaculos):
        if settings.MODO_DEBUG_LOGS and settings.LOG_CATEGORIAS.get("log_collision_handler", False):
            logger_ch.debug(f"    --- CH: Inicio _aplicar_movimiento_y_colision_eje_y --- dy: {dy_aplicado}, HB_in: {entidad_hitbox.topleft}")
        
        y_original_hb = entidad_hitbox.y # Guardar para comparar

        if dy_aplicado != 0:
            # entidad_hitbox.y += dy_aplicado # Asignación directa anterior
            entidad_hitbox.y = int(y_original_hb + dy_aplicado) # Truncamiento explícito

            if settings.MODO_DEBUG_LOGS and settings.LOG_CATEGORIAS.get("log_collision_handler", False):
                logger_ch.debug(f"      CH: Fase 2 (Y): dy_aplicado={dy_aplicado:.4f}. HB.y original={y_original_hb}, HB.y post-int-trunc={entidad_hitbox.y}")

            for obstaculo in obstaculos:
                rect_colision_obstaculo = obstaculo.hitbox if hasattr(obstaculo, 'hitbox') else obstaculo.rect
                if entidad_hitbox.colliderect(rect_colision_obstaculo):
                    obst_id_log = getattr(obstaculo, 'nombre_log_entidad', f"{type(obstaculo).__name__}_Desconocido")
                    if settings.MODO_DEBUG_LOGS and settings.LOG_CATEGORIAS.get("log_collision_handler", False):
                        logger_ch.debug(f"      CH: Fase 2 (Y): Colisión Y detectada con {obst_id_log} después de mov. tentativo. HB_Ent: {entidad_hitbox.topleft}, HB_Obs: {rect_colision_obstaculo.topleft}")

                    if dy_aplicado > 0: # Se movía hacia abajo y colisionó
                        entidad_hitbox.bottom = rect_colision_obstaculo.top
                        if settings.MODO_DEBUG_LOGS and settings.LOG_CATEGORIAS.get("log_collision_handler", False):
                            logger_ch.debug(f"        CH: Fase 2 (Y): Ajustado. Entidad mov. ABAJO. HB_Ent.bottom = Obs.top ({entidad_hitbox.bottom:.2f})")
                    elif dy_aplicado < 0: # Se movía hacia arriba y colisionó
                        entidad_hitbox.top = rect_colision_obstaculo.bottom
                        if settings.MODO_DEBUG_LOGS and settings.LOG_CATEGORIAS.get("log_collision_handler", False):
                            logger_ch.debug(f"        CH: Fase 2 (Y): Ajustado. Entidad mov. ARRIBA. HB_Ent.top = Obs.bottom ({entidad_hitbox.top:.2f})")
                    # Una vez que se maneja una colisión en este eje, rompemos el bucle de obstáculos.
                    break

        if settings.MODO_DEBUG_LOGS and settings.LOG_CATEGORIAS.get("log_collision_handler", False):
            logger_ch.debug(f"    --- CH: Fin _aplicar_movimiento_y_colision_eje_y --- HB_out Y: {entidad_hitbox.y:.2f}")

    @staticmethod
    def _verificar_y_revertir_colision_post_fase2(entidad_hitbox, obstaculos, pos_segura_fase1_x, pos_segura_fase1_y, 
                                               pos_original_global_x, pos_original_global_y):
        if settings.MODO_DEBUG_LOGS and settings.LOG_CATEGORIAS.get("log_collision_handler", False):
            logger_ch.debug(f"    --- CH: Inicio _verificar_y_revertir_colision_post_fase2 --- HB_in: {entidad_hitbox.topleft}")
        
        colision_global_tras_fase2, obstaculo_colisionante_global = False, None
        for obstaculo in obstaculos:
            rect_colision_obstaculo = obstaculo.hitbox if hasattr(obstaculo, 'hitbox') else obstaculo.rect
            if entidad_hitbox.colliderect(rect_colision_obstaculo):
                colision_global_tras_fase2, obstaculo_colisionante_global = True, obstaculo
                break
        
        hubo_reversion_global = False
        if colision_global_tras_fase2:
            # Estos son WARNING y CRITICAL, se loguearán más fácilmente si MODO_DEBUG_LOGS está activo
            # pero también si su categoría específica está activa, o siempre si se decide así para niveles altos.
            # Por ahora, los dejamos condicionados a la categoría "log_collision_handler" también para verbosidad.
            if settings.MODO_DEBUG_LOGS and settings.LOG_CATEGORIAS.get("log_collision_handler", False):
                # Usar nombre_log_entidad si existe, sino un fallback descriptivo.
                obst_id_log = getattr(obstaculo_colisionante_global, 'nombre_log_entidad', f"{type(obstaculo_colisionante_global).__name__}_Desconocido")
                logger_ch.warning(f"CH WARN Global (post-F2): Entidad AÚN colisiona con {obst_id_log} DESPUÉS de Fase 2. HB_Ent: {entidad_hitbox.topleft}. Revertiendo a Fase 1: ({pos_segura_fase1_x}, {pos_segura_fase1_y})")
            entidad_hitbox.x, entidad_hitbox.y = pos_segura_fase1_x, pos_segura_fase1_y
            hubo_reversion_global = True
            if settings.MODO_DEBUG_LOGS and settings.LOG_CATEGORIAS.get("log_collision_handler", False):
                 logger_ch.warning(f"  CH WARN Global (post-F2): Posición REVERTIDA A FASE 1. HB_Ent: {entidad_hitbox.topleft}")

            col_aun_despues_rev_f1, obst_critico_final = False, None
            for obst_check_critico in obstaculos:
                if entidad_hitbox.colliderect(obst_check_critico.hitbox if hasattr(obst_check_critico, 'hitbox') else obst_check_critico.rect):
                    col_aun_despues_rev_f1, obst_critico_final = True, obst_check_critico
                    break
            
            if col_aun_despues_rev_f1:
                if settings.MODO_DEBUG_LOGS and settings.LOG_CATEGORIAS.get("log_collision_handler", False):
                    # Usar nombre_log_entidad si existe, sino un fallback descriptivo.
                    obst_id_log_crit = getattr(obst_critico_final, 'nombre_log_entidad', f"{type(obst_critico_final).__name__}_Desconocido")
                    logger_ch.critical(f"CH CRITICAL POST-REVERSION (Fase1): Entidad AÚN COLISIONA con {obst_id_log_crit} DESPUÉS de revertir a Fase 1 ({entidad_hitbox.topleft}). Revertiendo a ORIGINAL GLOBAL: ({pos_original_global_x}, {pos_original_global_y})")
                entidad_hitbox.x, entidad_hitbox.y = pos_original_global_x, pos_original_global_y
                if settings.MODO_DEBUG_LOGS and settings.LOG_CATEGORIAS.get("log_collision_handler", False):
                    logger_ch.critical(f"  CH CRITICAL: Posición REVERTIDA A ORIGINAL GLOBAL. HB_Ent: {entidad_hitbox.topleft}")
        
        if settings.MODO_DEBUG_LOGS and settings.LOG_CATEGORIAS.get("log_collision_handler", False):
            logger_ch.debug(f"    --- CH: Fin _verificar_y_revertir_colision_post_fase2 --- HB_out: {entidad_hitbox.topleft}, ReversionGlobal: {hubo_reversion_global}")
        return hubo_reversion_global

    @staticmethod
    def _prevenir_teletransportacion(entidad_hitbox, dx_solicitado, dy_solicitado, pos_segura_fase1_x, pos_segura_fase1_y):
        # Esta función es principalmente para logs CRITICAL, así que se loguearán si la categoría está activa.
        if not (settings.MODO_DEBUG_LOGS and settings.LOG_CATEGORIAS.get("log_collision_handler", False)):
            return False # No hacer nada si los logs están desactivados

        dist_mov_x = abs(entidad_hitbox.x - pos_segura_fase1_x)
        dist_mov_y = abs(entidad_hitbox.y - pos_segura_fase1_y)
        umbral_tp_x = max(abs(dx_solicitado) + entidad_hitbox.width, entidad_hitbox.width * settings.FACTOR_UMBRAL_TELETRANSPORTACION)
        umbral_tp_y = max(abs(dy_solicitado) + entidad_hitbox.height, entidad_hitbox.height * settings.FACTOR_UMBRAL_TELETRANSPORTACION)

        reversion_por_tp = False
        if (dist_mov_x > umbral_tp_x or dist_mov_y > umbral_tp_y):
            logger_ch.critical(f"CH FATAL_WARN (Anti-TP): ¡Teletransportación POTENCIAL! HB_actual: {entidad_hitbox.topleft}, Pos_F1: ({pos_segura_fase1_x}, {pos_segura_fase1_y}). Input: dx={dx_solicitado}, dy={dy_solicitado}")
            logger_ch.critical(f"  Dist X: {dist_mov_x} (Umbral: {umbral_tp_x}), Dist Y: {dist_mov_y} (Umbral: {umbral_tp_y}). Revertiendo a Fase 1.")
            entidad_hitbox.x, entidad_hitbox.y = pos_segura_fase1_x, pos_segura_fase1_y
            reversion_por_tp = True
            logger_ch.critical(f"  CH Anti-TP: Posición REVERTIDA. HB_Ent: {entidad_hitbox.topleft}")
        return reversion_por_tp

    @staticmethod
    def gestionar_movimiento_y_colision(entidad_hitbox, entidad_rect, hitbox_offset_x, hitbox_offset_y, dx, dy, obstaculos):
        # El logger ya no se pasa, CollisionHandler usa su propio logger_ch.
        if settings.MODO_DEBUG_LOGS and settings.LOG_CATEGORIAS.get("log_collision_handler", False):
            logger_ch.debug(f"[CH.gestionar] Entrando. dx={dx}, dy={dy}. HB INICIAL: {entidad_hitbox.topleft}")
        
        pos_original_hitbox_antes_de_todo_x, pos_original_hitbox_antes_de_todo_y = entidad_hitbox.x, entidad_hitbox.y

        if settings.MODO_DEBUG_LOGS and settings.LOG_CATEGORIAS.get("log_collision_handler", False):
            logger_ch.debug("CH: ********** Fase 1: Pre-Correccion Estatica **********")
        CollisionHandler._resolver_solapamientos_estaticos_eje(entidad_hitbox, entidad_rect, hitbox_offset_x, hitbox_offset_y, obstaculos, 'x', dx)
        CollisionHandler._resolver_solapamientos_estaticos_eje(entidad_hitbox, entidad_rect, hitbox_offset_x, hitbox_offset_y, obstaculos, 'y', dy)
        
        entidad_rect.x, entidad_rect.y = entidad_hitbox.x - hitbox_offset_x, entidad_hitbox.y - hitbox_offset_y
        if settings.MODO_DEBUG_LOGS and settings.LOG_CATEGORIAS.get("log_collision_handler", False):
            logger_ch.debug(f"CH: --- Fin Fase 1. HB_Ent: {entidad_hitbox.topleft}, Rect_Ent: {entidad_rect.topleft} ---")

        pos_segura_hitbox_x_tras_fase1, pos_segura_hitbox_y_tras_fase1 = entidad_hitbox.x, entidad_hitbox.y

        if settings.MODO_DEBUG_LOGS and settings.LOG_CATEGORIAS.get("log_collision_handler", False):
            logger_ch.debug("CH: ********** Fase 2: Movimiento y Colision **********")
        CollisionHandler._aplicar_movimiento_y_colision_eje_x(entidad_hitbox, dx, obstaculos)
        CollisionHandler._aplicar_movimiento_y_colision_eje_y(entidad_hitbox, dy, obstaculos)
            
        entidad_rect.x, entidad_rect.y = entidad_hitbox.x - hitbox_offset_x, entidad_hitbox.y - hitbox_offset_y
        if settings.MODO_DEBUG_LOGS and settings.LOG_CATEGORIAS.get("log_collision_handler", False):
            logger_ch.debug(f"CH: --- Fin Fase 2. HB_Ent: {entidad_hitbox.topleft}, Rect_Ent: {entidad_rect.topleft} ---")
            
        hubo_reversion_global = CollisionHandler._verificar_y_revertir_colision_post_fase2(
            entidad_hitbox, obstaculos, 
            pos_segura_hitbox_x_tras_fase1, pos_segura_hitbox_y_tras_fase1, 
            pos_original_hitbox_antes_de_todo_x, pos_original_hitbox_antes_de_todo_y
        )
        if hubo_reversion_global:
            entidad_rect.x, entidad_rect.y = entidad_hitbox.x - hitbox_offset_x, entidad_hitbox.y - hitbox_offset_y

        if settings.MODO_DEBUG_LOGS and settings.LOG_CATEGORIAS.get("log_collision_handler", False):
            # Anti-TP logs (la función _prevenir_teletransportacion tiene sus propios logs críticos internos)
            logger_ch.debug(f"CH: Pre-Anti-TP Check: HB_actual=({entidad_hitbox.x},{entidad_hitbox.y}), Pos_Segura_F1=({pos_segura_hitbox_x_tras_fase1},{pos_segura_hitbox_y_tras_fase1})")
        
        # La llamada a _prevenir_teletransportacion se mantiene, pero ya no se usa su resultado directamente para revertir aquí.
        # Esa lógica de reversión (si se reactiva) estaría dentro de la propia función _prevenir_teletransportacion.
        CollisionHandler._prevenir_teletransportacion(entidad_hitbox, dx, dy, pos_segura_hitbox_x_tras_fase1, pos_segura_hitbox_y_tras_fase1)
        
        # Asegurar que el rect visual siempre coincida con el hitbox lógico final,
        # especialmente si _prevenir_teletransportacion hizo un cambio.
        entidad_rect.x, entidad_rect.y = entidad_hitbox.x - hitbox_offset_x, entidad_hitbox.y - hitbox_offset_y
        
        if settings.MODO_DEBUG_LOGS and settings.LOG_CATEGORIAS.get("log_collision_handler", False):
            logger_ch.debug(f"CH: --- Fin gestionar_movimiento_y_colision --- Pos FINAL HB: {entidad_hitbox.topleft}, Rect: {entidad_rect.topleft}") 