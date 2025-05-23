# mapa_conceptual_modulos.py
# Este archivo contiene una representación estructurada de los módulos principales
# del proyecto, sus responsabilidades e interacciones, agrupados por categoría.
# Sirve como un "mapa conceptual" para ayudar a entender la arquitectura del juego.

MAPA_MODULOS_POR_CATEGORIA = {
    "Core": [
        {
            "nombre_modulo": "main.py",
            "categoria": "Core", # Aunque 'main.py' quedará en la raíz, conceptualmente es el núcleo.
            "ruta_relativa": "main.py", # Esta ruta se actualizará si main.py se moviera (pero no lo hará).
            "responsabilidad_principal": "Punto de entrada de la aplicación. Inicializa el sistema de logging y el juego, y maneja el bucle principal de alto nivel.",
            "interacciones_principales": {
                "entrantes": [], # Es el punto de partida
                "salientes": ["config_logging.py", "juego.py", "settings.py"]
            },
            "componentes_clave_internos": ["Función main()"],
            "notas_adicionales": "Es el primer script que se ejecuta. Asegura que la RUTA_BASE_PROYECTO esté en sys.path si es necesario (lógica a revisar con la estructura src/)."
        },
        {
            "nombre_modulo": "juego.py",
            "categoria": "Core",
            "ruta_relativa": "juego.py", # Se actualizará a "src/core/juego.py"
            "responsabilidad_principal": "Clase principal que orquesta el flujo del juego. Maneja el bucle de juego, los estados (a través de gestor_estado), eventos (gestor_eventos), actualizaciones de entidades, renderizado (renderer).",
            "interacciones_principales": {
                "entrantes": ["main.py"],
                "salientes": [
                    "settings.py", "game_initializer.py", "gestor_eventos.py",
                    "gestor_estado.py", "gestor_nivel.py", "asset_manager.py", "renderer.py",
                    "hud.py", "camara.py", # CollisionHandler es usado por entidades, no directamente por Juego (a verificar)
                    "logging" # Añadido logging
                ]
            },
            "componentes_clave_internos": ["Clase Juego", "método run()", "método _manejar_eventos()", "método _actualizar()", "método _renderizar()"],
            "notas_adicionales": "Contiene el bucle de juego principal y coordina la mayoría de los sistemas y entidades."
        },
        {
            "nombre_modulo": "settings.py",
            "categoria": "Config", # Actualizado a categoría Config
            "ruta_relativa": "src/config/settings.py", # Actualizada la ruta
            "responsabilidad_principal": "Contiene todas las constantes globales, configuraciones del juego (dimensiones de pantalla, FPS, rutas, categorías de log, etc.) y parámetros de balanceo del juego.",
            "interacciones_principales": {
                "entrantes": ["Prácticamente todos los módulos del proyecto para acceder a configuraciones y constantes."],
                "salientes": [] # Solo define datos.
            },
            "componentes_clave_internos": [
                "Variables de configuración (ej. ANCHO_PANTALLA, ALTO_PANTALLA, FPS)",
                "Rutas (ej. RUTA_ASSETS, RUTA_IMAGENES)",
                "Configuraciones de logging (ej. LOG_CATEGORIAS, MODULOS_CON_LOG_PROPIO)"
            ],
            "notas_adicionales": "Archivo crítico para la configuración global. Se debe revisar y actualizar cuidadosamente."
        },
        {
            "nombre_modulo": "config_logging.py",
            "categoria": "Config", # Movido a categoría Config para agrupar con settings.py
            "ruta_relativa": "src/config/config_logging.py",
            "responsabilidad_principal": "Configura el sistema de logging de la aplicación, incluyendo handlers (RotatingFileHandler para archivos, StreamHandler para consola con colores), formateadores y filtros (CategoryFilter, DuplicateFilter). Es llamado por main.py al inicio.",
            "interacciones_principales": {
                "entrantes": ["main.py"],
                "salientes": ["settings.py (para leer configuraciones de logging)"]
            },
            "componentes_clave_internos": ["Función setup_logging()", "Clase CategoryFilter", "Clase DuplicateFilter"],
            "notas_adicionales": "Centraliza toda la configuración del sistema de logging. Los logs se guardan por sesión y por módulo."
        },
        {
            "nombre_modulo": "game_initializer.py",
            "categoria": "Core",
            "ruta_relativa": "src/core/game_initializer.py",
            "responsabilidad_principal": "Contiene la lógica para crear y configurar los elementos iniciales del juego (jugador, obstáculos, enemigos, cámara, HUD) al inicio del juego.",
            "interacciones_principales": {
                "entrantes": ["juego.py (lo llama para inicializar los elementos)"],
                "salientes": [
                    "settings.py (para configuraciones como ANCHO_MUNDO_JUEGO, etc.)", 
                    "asset_manager.py (para obtener assets como fuentes)", 
                    "jugador.py (para instanciar Jugador)",
                    "enemigo.py (para instanciar Enemigo)", # Asumiendo que podría instanciar enemigos directamente o a través de gestor_nivel
                    "entorno.py (para instanciar Obstaculo, Arbol, etc.)", # Asumiendo que podría instanciar entorno directamente o a través de gestor_nivel
                    "gestor_nivel.py (para cargar elementos del nivel)", 
                    "camara.py (para instanciar Camara2D)", 
                    "hud.py (para instanciar DebugHUD)",
                    "logging (usa getLogger('game_initializer') y la categoría 'log_game_initializer')"
                ]
            },
            "componentes_clave_internos": ["Función crear_elementos_juego(asset_manager, gestor_nivel, factor_zoom_inicial, juego_ref_para_hud)"],
            "variables_config_clave_settings": [
                "ANCHO_PANTALLA", "ALTO_PANTALLA", "ANCHO_MUNDO_JUEGO", "ALTO_MUNDO_JUEGO", 
                "MODO_DEBUG_LOGS", 
                "LOG_CATEGORIAS (específicamente 'log_game_initializer', y condicionalmente 'log_camara')"
            ],
            "notas_adicionales": "Centraliza la creación de los objetos principales del juego. Su logger es 'game_initializer' y su categoría de log principal es 'log_game_initializer'. Es invocado por la clase Juego durante su inicialización."
        }
        # Futuras entradas para config.py aquí (si config.py se separa de settings.py)
    ],
    "Entidades": [
        {
            "nombre_modulo": "jugador.py",
            "categoria": "Entidades",
            "ruta_relativa": "src/entidades/jugador.py",
            "responsabilidad_principal": "Representa al personaje principal controlado por el usuario. Gestiona su movimiento (con ayuda de CollisionHandler), animaciones (heredadas de EntidadBase), la iniciación y lógica de ataques (AttackProfileManager), y la recepción y manejo de empujes (con una instancia de MotorFisica).",
            "interacciones_principales": {
                "entrantes": ["juego.py (para creación y updates)", "gestor_estado.py (para updates)"],
                "salientes": [
                    "entidad_base.py (herencia)",
                    "settings.py (para configuraciones del jugador y control de logging)",
                    "asset_manager.py (para assets de animación)",
                    "collision_handler.py (instancia, para movimiento y colisión)",
                    "motor_fisica.py (instancia para empuje, y para cálculos estáticos si se usaran)",
                    "utils.py (para funciones de utilidad como convertir_deltas_a_enteros_para_colision)",
                    "attack_profile_manager.py (para gestionar perfiles y parámetros de ataque)",
                    "enemigo.py (para aplicar daño a instancias de Enemigo)",
                    "logging (para registrar eventos y depuración)"
                ]
            },
            "componentes_clave_internos": [
                "Clase Jugador(EntidadBase)",
                "__init__(self, x, y, asset_manager_instance): Inicialización, carga de animaciones, config. hitbox, inicialización de AttackProfileManager, instancia de MotorFisica para empuje.",
                "actualizar_movimiento(self, teclas_presionadas, obstaculos, mundo_ancho, mundo_alto, delta_time): Procesa input, aplica empuje de MotorFisica, calcula movimiento flotante, maneja colisiones con límites y llama a _mover_y_colisionar.",
                "_mover_y_colisionar(self, dx, dy, obstaculos): Usa una instancia de CollisionHandler.",
                "aplicar_fuerza_de_empuje(self, vector_empuje): Agrega fuerza al MotorFisica del jugador.",
                "actualizar_empuje(self, delta_time): Este método probablemente ya no exista o su lógica se integró en actualizar_movimiento con MotorFisica.",
                "actualizar_ataque(self, enemigos): Gestiona la lógica de un ataque en curso, calcula hitbox de ataque, detecta colisiones con enemigos y aplica daño.",
                "update(self, teclas_presionadas, obstaculos_solidos, enemigos_sprites_para_ataque, mundo_ancho, mundo_alto, delta_time): Método principal de actualización que llama a actualizar_movimiento y actualizar_ataque.",
                "recibir_dano(self, cantidad, tipo_dano): Sobrescribe para manejar daño específico al jugador (y llama a super).",
                "dibujar(self, superficie): Dibuja el sprite del jugador (heredado o propio si se define).",
                "dibujar_debug_ataque(self, superficie_destino, camara): Dibuja el hitbox de ataque para depuración.",
                "Variables de estado importantes: self.esta_atacando, self.pos_x_flotante, self.pos_y_flotante, self.attack_profile_manager (instancia)"
            ],
            "funciones_clave_publicas": {
                "update": "Punto de entrada principal para actualizar el estado del jugador (movimiento, ataque).",
                "atacar": "Inicia la lógica de ataque del jugador.",
                "recibir_dano": "Procesa el daño recibido por el jugador.",
                "dibujar_debug_ataque": "Visualiza el hitbox de ataque para fines de depuración."
            },
            "variables_config_clave_settings": [
                "VIDA_MAXIMA_JUGADOR", "VELOCIDAD_JUGADOR", "JUGADOR_HITBOX_OFFSET_X", "JUGADOR_HITBOX_OFFSET_Y", 
                "JUGADOR_HITBOX_AJUSTE_INFERIOR", "JUGADOR_DANO_BASE_ATAQUE", "JUGADOR_COOLDOWN_ATAQUE",
                "MODO_DEBUG_LOGS", 
                "LOG_CATEGORIAS (específicamente log_jugador_general, log_jugador_mov_detalle, log_jugador_ataque_calculo, log_jugador_ataque_debug, log_jugador_vida, log_jugador_anim)"
            ],
            "notas_adicionales": "Su hitbox tiene un ajuste específico en la parte inferior. Utiliza posiciones flotantes para un movimiento más preciso antes de aplicar colisiones con deltas enteros."
        },
        {
            "nombre_modulo": "entidad_base.py",
            "categoria": "Entidades",
            "ruta_relativa": "src/entidades/entidad_base.py",
            "responsabilidad_principal": "Clase base abstracta para todas las entidades interactivas del juego (Jugador, Enemigo, etc.). Proporciona funcionalidad común como ID, gestión de assets (imagen/animación), rect, hitbox, atributos de combate (vida, velocidad), recepción de daño y estado de muerte.",
            "interacciones_principales": {
                "entrantes": ["Subclases como jugador.py, enemigo.py (por herencia)", "game_initializer.py o gestor_nivel.py (para instanciación)"],
                "salientes": [
                    "asset_manager.py (para cargar imágenes/animaciones)",
                    "settings.py (para configuraciones por defecto y control de logging mediante MODO_DEBUG_LOGS y LOG_CATEGORIAS)",
                    "logging (para registrar eventos y depuración)"
                ]
            },
            "componentes_clave_internos": [
                "pygame.sprite.Sprite (clase base)",
                "id_entidad (único por instancia)",
                "nombre_log_entidad (para logs)",
                "asset_manager (instancia)",
                "animaciones (dict)",
                "estado_animacion",
                "image, rect, hitbox",
                "vida_maxima, vida_actual, velocidad",
                "ha_muerto (bool)",
                "Método __init__(...): Inicialización básica y carga de assets/animaciones.",
                "Método _cargar_animaciones_desde_config()",
                "Método _actualizar_posicion_hitbox()",
                "Método _actualizar_posicion_rect_desde_hitbox()",
                "Método actualizar_animacion()",
                "Método recibir_dano()",
                "Método morir()",
                "Método update() (generalmente para animación)",
                "Método dibujar_hitbox() (para depuración)"
            ],
            "variables_config_clave_settings": [
                "MODO_DEBUG_LOGS",
                "LOG_CATEGORIAS",
                "DEBUG_VER_HITBOXES"
            ],
            "notas_adicionales": "Gestiona el ciclo de vida básico (daño, muerte) y la actualización de animaciones. El posicionamiento del hitbox por defecto es topleft del rect + offset. La lógica de movimiento es responsabilidad de las subclases."
        },
        {
            "nombre_modulo": "enemigo.py",
            "categoria": "Entidades",
            "ruta_relativa": "src/entidades/enemigo.py",
            "responsabilidad_principal": "Representa a las entidades hostiles del juego. Implementa IA básica de seguimiento, manejo de colisiones (con CollisionHandler y utils.py), aplicación de empuje (con MotorFisica) y atributos de combate. Hereda de EntidadBase.",
            "interacciones_principales": {
                "entrantes": [
                    "gestor_estado.py (para creación, updates y gestión de su ciclo de vida)",
                    "game_initializer.py o gestor_nivel.py (para instanciación)"
                ],
                "salientes": [
                    "entidad_base.py (herencia)",
                    "settings.py (para configuraciones del enemigo y control de logging)",
                    "collision_handler.py (instancia, para gestionar movimiento y colisiones)",
                    "motor_fisica.py (instancia, para aplicar/recibir empuje y gestionar movimiento basado en fuerzas)",
                    "utils.py (para funciones de utilidad como convertir_deltas_a_enteros_para_colision)",
                    "jugador.py (para obtener el rect del jugador como objetivo y aplicar empuje)",
                    "logging (para registrar eventos y depuración)"
                ]
            },
            "componentes_clave_internos": [
                "Clase Enemigo(EntidadBase)",
                "__init__(...): Inicialización específica, incluyendo MotorFisica y CollisionHandler.",
                "update(self, jugador_rect, grupo_obstaculos, delta_time): Lógica de IA, movimiento (usando MotorFisica y _mover_y_colisionar), y empuje.",
                "_mover_y_colisionar(self, dx, dy, obstaculos_colision): Usa una instancia de CollisionHandler.",
                "empujar_jugador(self, jugador_obj, fuerza_base): Calcula y aplica fuerza de empuje al jugador a través del MotorFisica del jugador."
            ],
            "variables_config_clave_settings": [
                "ENEMIGO_VIDA_MAXIMA", "ENEMIGO_VELOCIDAD", "ENEMIGO_HITBOX_OFFSET_X", "ENEMIGO_HITBOX_OFFSET_Y",
                "ENEMIGO_DANO_ATAQUE", "ENEMIGO_RANGO_AGRO", "ENEMIGO_DIST_MIN_JUGADOR",
                "MODO_DEBUG_LOGS",
                "LOG_CATEGORIAS (específicamente log_enemigo, log_enemigo_ia, log_enemigo_mov, log_enemigo_col)"
            ],
            "notas_adicionales": "Actualmente utiliza una imagen estática, pero la herencia de EntidadBase permitiría añadir animaciones. Su hitbox se centra en el rect, a diferencia del comportamiento por defecto de EntidadBase."
        },
        {
            "nombre_modulo": "entorno.py",
            "categoria": "Entidades",
            "ruta_relativa": "src/entidades/entorno.py",
            "responsabilidad_principal": "Define clases para los elementos del entorno del juego, principalmente obstáculos. Proporciona una clase base 'Obstaculo' para manejar características comunes como carga de assets, animación simple, escalado y hitboxes.",
            "interacciones_principales": {
                "entrantes": [
                    "gestor_nivel.py o game_initializer.py (para instanciación y colocación en el nivel)",
                    "collision_handler.py (los hitboxes de estos elementos son considerados obstáculos)",
                    "renderer.py (para dibujarlos)"
                ],
                "salientes": [
                    "pygame.sprite.Sprite (herencia para la clase Obstaculo)",
                    "asset_manager.py (para cargar las imágenes/frames de los elementos)",
                    "settings.py (para configuraciones como DEBUG_VER_HITBOXES y control de logging mediante MODO_DEBUG_LOGS y LOG_CATEGORIAS como log_entorno)",
                    "logging (para registrar eventos y depuración)"
                ]
            },
            "componentes_clave_internos": [
                "Clase Obstaculo(pygame.sprite.Sprite): Clase base para elementos estáticos del entorno. Gestiona assets, animación básica, escalado y hitbox.",
                "  Método Obstaculo.__init__(...): Inicialización y carga de assets.",
                "  Método Obstaculo._cargar_y_escalar_animacion(): Carga y escala frames una vez.",
                "  Método Obstaculo._actualizar_posicion_hitbox()",
                "  Método Obstaculo.update(): Actualiza la animación.",
                "  Método Obstaculo.dibujar_hitbox(): Dibuja el hitbox para depuración.",
                "Clase Arbol(Obstaculo): Representa un árbol, especialización de Obstaculo."
            ],
            "variables_config_clave_settings": [
                "DEBUG_VER_HITBOXES", 
                "MODO_DEBUG_LOGS", 
                "LOG_CATEGORIAS (específicamente log_entorno)"
            ],
            "notas_adicionales": "Contiene elementos estáticos como árboles. La clase base Obstaculo podría extenderse para otros tipos de elementos del entorno."
        }
    ],
    "Sistemas": [
        {
            "nombre_modulo": "collision_handler.py",
            "categoria": "Sistemas",
            "ruta_relativa": "src/sistemas/collision_handler.py",
            "responsabilidad_principal": "Proporciona métodos para detectar y resolver colisiones entre entidades y el entorno. Maneja el movimiento con colisión, asegurando que las entidades no atraviesen obstáculos. Ya no usa @staticmethod, se instancia donde se necesita (ej. en Entidades).",
            "interacciones_principales": {
                "entrantes": [
                    "jugador.py (instanciado y usado para movimiento)", 
                    "enemigo.py (instanciado y usado para movimiento)",
                    "gestor_estado.py (potencialmente para colisiones entre otras entidades)"
                ],
                "salientes": [
                    "settings.py (para constantes como UMBRAL_MOV_FLOTANTE_ENTIDAD_PARA_COLISION, MAX_PASADAS_RESOLUCION_ESTATICA, PIXEL_CONTACT_THRESHOLD)",
                    "logging (para depuración de colisiones)"
                ]
            },
            "componentes_clave_internos": [
                "Clase CollisionHandler",
                "gestionar_movimiento_y_colision_con_entorno(self, entidad_movil_rect_original, hitbox_original, dx, dy, grupo_sprites_colisionables_estaticos, entidad_movil_obj=None): Lógica principal de movimiento y resolución.",
                "resolver_colisiones_multiples_ejes(self, rect_movil, hitbox_movil, dx, dy, sprites_colisionables, entidad_movil_obj=None): Resuelve iterativamente.",
                "Funciones auxiliares internas para detección y resolución de solapamientos por eje."
            ],
            "variables_config_clave_settings": [
                "UMBRAL_MOV_FLOTANTE_ENTIDAD_PARA_COLISION", "MAX_PASADAS_RESOLUCION_ESTATICA", "PIXEL_CONTACT_THRESHOLD",
                "PREVENIR_TELETRANSPORTACION_CH", "MODO_DEBUG_LOGS", "LOG_CATEGORIAS (log_collision_handler, log_collision_handler_detalle)"
            ],
            "notas_adicionales": "Se instancia por entidad que necesite manejar sus propias colisiones de movimiento (Jugador, Enemigo). Las funciones ya no son estáticas. Usa un umbral para convertir deltas flotantes a enteros para la detección de colisión (ahora delegado a utils.py pero el concepto es relevante)."
        },
        {
            "nombre_modulo": "gestor_eventos.py",
            "categoria": "Sistemas",
            "ruta_relativa": "src/sistemas/gestor_eventos.py",
            "responsabilidad_principal": "Maneja todos los eventos de entrada de Pygame (teclado, ratón, cierre de ventana). Traduce estos eventos en acciones dentro del juego, como mover al jugador, atacar, cambiar zoom de cámara, o salir del juego. También interactúa con el HUD para eventos específicos de la UI.",
            "interacciones_principales": {
                "entrantes": ["juego.py (recibe la lista de eventos de pygame)"],
                "salientes": [
                    "settings.py (para leer configuraciones de zoom, control de logging, etc.)",
                    "jugador.py (para invocar acciones como atacar, o acceder a su attack_profile_manager para cambiar perfiles/parámetros)",
                    "hud.py (para pasarle eventos que el HUD pueda necesitar manejar, ej. clicks en botones si existieran)",
                    "juego.py (referencia para actualizar el factor de zoom global)",
                    "logging (usa getLogger('gestor_eventos') y categorías como 'log_gestor_eventos', 'log_gestor_eventos_verbose')"
                ]
            },
            "componentes_clave_internos": [
                "Clase GestorEventos",
                "  __init__(jugador, hud, juego_ref): Guarda referencias a jugador, HUD y la instancia del juego.",
                "  procesar_eventos(eventos_pygame): Itera sobre eventos de Pygame y dispara acciones.",
                "    Manejo de pygame.QUIT y K_ESCAPE para self.solicitud_salir.",
                "    Manejo de pygame.MOUSEWHEEL para el zoom (usa juego_ref.actualizar_factor_zoom).",
                "    Manejo de K_SPACE para jugador.atacar().",
                "    Manejo de K_PAGEUP, K_PAGEDOWN para cambiar perfiles de ataque del jugador.",
                "    Manejo de teclas F1-F10 para modificar parámetros del perfil de ataque activo (usa jugador.attack_profile_manager).",
                "  debe_salir(): Devuelve self.solicitud_salir.",
                "Atributo: solicitud_salir (bool)"
            ],
            "variables_config_clave_settings": [
                "MODO_DEBUG_LOGS",
                "LOG_CATEGORIAS (específicamente 'log_gestor_eventos', 'log_gestor_eventos_verbose')",
                "FACTOR_ZOOM_PASO", "FACTOR_ZOOM_MIN", "FACTOR_ZOOM_MAX"
            ],
            "notas_adicionales": "Mantiene un estado interno 'solicitud_salir'. El bloque if __name__ == '__main__' para pruebas ha sido comentado."
        },
        {
            "nombre_modulo": "gestor_estado.py",
            "categoria": "Sistemas",
            "ruta_relativa": "src/sistemas/gestor_estado.py",
            "responsabilidad_principal": "Mantiene y actualiza el estado de todas las entidades del juego (jugador, enemigos, proyectiles, etc.). Gestiona la creación y eliminación de entidades, y las interacciones básicas entre ellas como el daño por contacto.",
            "interacciones_principales": {
                "entrantes": ["juego.py (para inicialización y llamadas de update)"],
                "salientes": [
                    "settings.py", 
                    "jugador.py", "enemigo.py", "entidad_base.py", "entorno.py", 
                    "utils.py (para funciones como collide_rect_extended)",
                    "pygame.sprite (para gestión de grupos)",
                    "logging (usa getLogger('gestor_estado') y categorías como 'log_gestor_estado', 'log_gestor_estado_detalle', 'log_posiciones_debug')"
                ]
            },
            "componentes_clave_internos": [
                "self.jugador (instancia)",
                "self.todos_los_sprites (pygame.sprite.Group)",
                "self.enemigos (pygame.sprite.Group)",
                "self.obstaculos (pygame.sprite.Group)",
                "self.proyectiles (pygame.sprite.Group)",
                "método actualizar_entidades()",
                "método _eliminar_entidades_muertas()",
                "método _manejar_colision_jugador_enemigo_contacto() (usa settings.ENEMIGO_DANO_CONTACTO_DEFAULT y utils.collide_rect_extended)"
            ],
            "variables_config_clave_settings": [
                "MODO_DEBUG_LOGS", 
                "LOG_CATEGORIAS ('log_gestor_estado', 'log_gestor_estado_detalle', 'log_posiciones_debug')",
                "ANCHO_MUNDO_JUEGO", "ALTO_MUNDO_JUEGO",
                "ENEMIGO_DANO_CONTACTO_DEFAULT"
            ],
            "notas_adicionales": "Centraliza la lógica de 'quién está dónde' y 'qué está pasando'. La detección de daño por contacto entre jugador y enemigo está implementada pero puede activarse/desactivarse fácilmente. Pendiente: Optimizar la creación del grupo de obstáculos para cada enemigo si es necesario."
        },
        {
            "nombre_modulo": "gestor_nivel.py",
            "categoria": "Sistemas",
            "ruta_relativa": "src/sistemas/gestor_nivel.py",
            "responsabilidad_principal": "Gestiona la carga y la disposición de los elementos del nivel, como obstáculos, enemigos, y potencialmente elementos decorativos y zonas especiales. Actualmente carga elementos de forma hardcodeada, con funcionalidad básica para cargar mapas TMX (de Tiled).",
            "interacciones_principales": {
                "entrantes": ["game_initializer.py (para cargar los elementos iniciales del nivel)"],
                "salientes": [
                    "settings.py (para leer configuraciones de nivel, rutas y control de logging)",
                    "asset_manager.py (para pasar a las entidades que crea, como Arbol y Enemigo)",
                    "entorno.py (para instanciar Obstaculo, Arbol)",
                    "enemigo.py (para instanciar Enemigo)",
                    "pytmx (librería externa para cargar mapas .tmx)",
                    "pygame.sprite (para gestionar grupos de sprites internamente)",
                    "logging (usa getLogger('gestor_nivel') y categorías como 'log_gestor_nivel', 'log_gestor_nivel_detalle')"
                ]
            },
            "componentes_clave_internos": [
                "Clase GestorNivel",
                "__init__(self, asset_manager)",
                "cargar_elementos_nivel_inicial(self): Llama a métodos privados para carga hardcodeada.",
                "_cargar_obstaculos_hardcodeados(self)",
                "_generar_enemigos_hardcodeados(self)",
                "cargar_mapa_desde_tmx(self, nombre_mapa_tmx): Lógica para cargar y parsear (parcialmente) un archivo TMX.",
                "get_obstaculos(self), get_enemigos(self), get_elementos_decorativos(self), get_zonas_especiales(self): Getters para los grupos de sprites.",
                "get_tile_data(self, capa_nombre, x, y): Para obtener propiedades de tiles de un mapa TMX.",
                "Atributos: self.mapa_tmx, self.obstaculos (Group), self.enemigos (Group), self.elementos_decorativos (Group), self.zonas_especiales (dict)"
            ],
            "variables_config_clave_settings": [
                "MODO_DEBUG_LOGS",
                "LOG_CATEGORIAS (específicamente 'log_gestor_nivel', 'log_gestor_nivel_detalle')",
                "RUTA_ASSETS_MAPAS (para cargar mapas TMX)"
            ],
            "notas_adicionales": "La funcionalidad de carga de TMX está presente pero el procesamiento detallado de capas y objetos aún está en desarrollo (comentarios en el código). El bloque if __name__ == '__main__' para pruebas ha sido comentado."
        },
        {
            "nombre_modulo": "attack_profile_manager.py",
            "categoria": "Sistemas",
            "ruta_relativa": "src/sistemas/attack_profile_manager.py",
            "responsabilidad_principal": "Gestiona los perfiles de ataque del jugador, incluyendo la creación, carga, guardado, modificación y selección de perfiles. Proporciona una interfaz para acceder y modificar los parámetros de los perfiles de ataque. También calcula valores derivados como el número de segmentos de barrido y la duración de cada segmento.",
            "interacciones_principales": {
                "entrantes": ["jugador.py (para instanciación y uso)"],
                "salientes": [
                    "settings.py (para configuraciones de perfiles de ataque por defecto, ruta de archivo de configuración, nombre de perfil inicial)",
                    "logging (utiliza logging.getLogger('attack_profile_manager') y la categoría 'log_attack_profile_manager')",
                    "os, json (para leer/escribir el archivo JSON de perfiles)"
                ]
            },
            "componentes_clave_internos": [
                "Clase AttackProfileManager",
                "__init__(self, ruta_base_proyecto_settings, archivo_config_settings, nombre_perfil_inicial_settings): Carga o crea perfiles.",
                "_cargar_o_crear_perfiles_ataque(): Lógica para cargar desde JSON o crear perfiles por defecto.",
                "_crear_perfil_ataque_por_defecto(nombre_perfil): Crea un perfil con valores de settings.py.",
                "_forzar_creacion_perfil_default_y_guardar(): Crea y guarda el perfil por defecto.",
                "guardar_todos_perfiles_ataque(): Guarda todos los perfiles en el archivo JSON.",
                "seleccionar_perfil_ataque(nombre_perfil_solicitado): Cambia el perfil activo y recalcula propiedades.",
                "get_parametro_ataque_activo(nombre_parametro, valor_defecto)",
                "set_parametro_ataque_activo(nombre_parametro, valor)",
                "Métodos para modificar parámetros (ej. modificar_ataque_offset)",
                "Propiedades: num_segmentos_barrido_activo, duracion_segmento_barrido_activo",
                "Atributos: perfiles_de_ataque (dict), nombre_perfil_ataque_activo"
            ],
            "variables_config_clave_settings": [
                "RUTA_BASE_PROYECTO",
                "ARCHIVO_CONFIG_ATAQUE",
                "NOMBRE_PERFIL_ATAQUE_INICIAL",
                "ATAQUE_BASE_OFFSET_DISTANCIA",
                "ATAQUE_BASE_EXTENSION",
                "ATAQUE_BASE_GROSOR",
                "ATAQUE_BASE_DURACION_TOTAL_MS",
                "ATAQUE_BASE_PLANTILLA_ANGULOS_GRADOS",
                "ATAQUE_BASE_DANO_MODIFICADOR",
                "ATAQUE_BASE_COOLDOWN_MODIFICADOR",
                "LOG_CATEGORIAS['log_attack_profile_manager']"
            ],
            "notas_adicionales": "Centraliza toda la gestión de los perfiles de ataque del jugador. Los perfiles se guardan en un archivo JSON (config_ataque.json por defecto). El módulo es robusto contra errores de carga o ausencia del archivo, recreando perfiles por defecto si es necesario."
        },
        {
            "nombre_modulo": "motor_fisica.py",
            "categoria": "Sistemas",
            "ruta_relativa": "src/sistemas/motor_fisica.py",
            "responsabilidad_principal": "Clase instanciable que gestiona la acumulación, decaimiento (fricción, umbral) y aplicación de fuerzas (ej. empujes) para una entidad. Cada entidad con física de empuje propia (ej. Jugador) puede tener su propia instancia. También provee métodos estáticos para cálculos de física simples (ej. calcular_vector_empuje_simple).",
            "interacciones_principales": {
                "entrantes": [
                    "jugador.py (para aplicar y actualizar empuje/fuerzas a través de una instancia)",
                    "enemigo.py (para usar el método estático calcular_vector_empuje_simple y potencialmente para instanciar para su propio movimiento si evoluciona)"
                ],
                "salientes": [
                    "settings.py (para constantes como FACTOR_FRICCION_GENERICO, UMBRAL_FUERZA_MINIMA_GENERICO, y control de logging)",
                    "logging (para depuración)"
                ]
            },
            "componentes_clave_internos": [
                "Clase MotorFisica",
                "__init__(self, factor_friccion, umbral_fuerza_minima, nombre_entidad_log)",
                "fuerzas_acumuladas (pygame.math.Vector2)",
                "agregar_fuerza(self, vector_fuerza)",
                "actualizar_estado_fuerzas(self, delta_time)",
                "get_vector_movimiento_resultante_del_frame(self, delta_time)",
                "resetear_fuerzas(self)",
                "tiene_fuerzas_activas(self)",
                "Método estático: calcular_vector_empuje_simple(origen, destino, magnitud)"
            ],
            "variables_config_clave_settings": [
                "FACTOR_FRICCION_EMPUJE_JUGADOR", "UMBRAL_FUERZA_EMPUJE_MINIMA_JUGADOR",
                "FACTOR_FRICCION_GENERICO", "UMBRAL_FUERZA_MINIMA_GENERICO",
                "MODO_DEBUG_LOGS", "LOG_CATEGORIAS (log_motor_fisica, log_motor_fisica_verbose)"
            ],
            "notas_adicionales": "Permite una física de movimiento basada en fuerzas persistentes y con decaimiento. El método estático sigue disponible para cálculos puntuales de vectores de empuje."
        }
    ],
    "Renderizado": [
        {
            "nombre_modulo": "renderer.py",
            "categoria": "Renderizado",
            "ruta_relativa": "src/renderizado/renderer.py",
            "responsabilidad_principal": "Encargado de dibujar todos los elementos visibles del juego en la pantalla, incluyendo el fondo, los sprites (ordenados y escalados por la cámara) y las hitboxes de depuración. Es instanciado por Juego.",
            "interacciones_principales": {
                "entrantes": ["juego.py (para renderizar la escena completa y el HUD)"],
                "salientes": [
                    "settings.py (para colores, grosores de debug, y control de logging)",
                    "asset_manager.py (para obtener assets como el fondo)",
                    "camara.py (para obtener sprites visibles y aplicar transformaciones)",
                    "hud.py (para dibujar la instancia del HUD)",
                    "logging (para depuración del renderizado)"
                ]
            },
            "componentes_clave_internos": [
                "Clase Renderer",
                "__init__(self, pantalla, camara, asset_manager)",
                "_renderizar_fondo_tileado(self, superficie_destino, factor_zoom)",
                "_renderizar_sprites_juego(self, superficie_destino, todos_los_sprites, factor_zoom)",
                "_renderizar_hitboxes_debug(self, superficie_destino, todos_los_sprites, factor_zoom)",
                "render_escena_completa(self, todos_los_sprites, factor_zoom)",
                "render_hud(self, hud_instance)"
            ],
            "variables_config_clave_settings": [
                "DEBUG_VER_HITBOXES", "HITBOX_COLOR_COLISION", "GROSOR_HITBOX_COLISION_DEBUG", 
                "HITBOX_COLOR_RECT_SPRITE", "GROSOR_RECT_SPRITE_DEBUG", "COLOR_ATAQUE_HITBOX", "GROSOR_HITBOX_ATAQUE_DEBUG",
                "NEGRO", "ROJO_ERROR_ASSET", "FUCSIA", "COLOR_FONDO_DEFAULT",
                "MODO_DEBUG_LOGS", "LOG_CATEGORIAS (log_renderer, log_renderer_verbose, log_renderer_hitbox)"
            ],
            "notas_adicionales": "Trabaja en conjunto con Camara2D para el posicionamiento y escalado de elementos en el mundo."
        },
        {
            "nombre_modulo": "hud.py",
            "categoria": "Renderizado",
            "ruta_relativa": "src/renderizado/hud.py",
            "responsabilidad_principal": "Muestra información de depuración en pantalla (DebugHUD), como la posición del jugador, el estado del zoom, detalles del perfil de ataque activo, y los estados de las categorías de log. También permite modificar el estado de MODO_DEBUG_LOGS y las categorías individuales de LOG_CATEGORIAS mediante teclas.",
            "interacciones_principales": {
                "entrantes": [
                    "juego.py (para inicialización y llamadas a draw)", 
                    "gestor_eventos.py (para pasarle eventos de input para el manejo de toggles de log)"
                ],
                "salientes": [
                    "settings.py (para leer y modificar MODO_DEBUG_LOGS y LOG_CATEGORIAS, y para leer constantes de layout y colores del HUD)",
                    "jugador.py (para obtener información del jugador y su attack_profile_manager)",
                    "juego.py (referencia para obtener el factor_zoom_actual)",
                    "pygame (para renderizar texto)",
                    "logging (usa getLogger('hud') y la categoría 'log_hud' para mensajes sobre cambios en los toggles de logging)"
                ]
            },
            "componentes_clave_internos": [
                "Clase DebugHUD",
                "__init__(self, jugador, fuente, juego_ref)",
                "manejar_input_hud(self, event): Procesa teclas para cambiar MODO_DEBUG_LOGS y LOG_CATEGORIAS.",
                "update(self): Recolecta y cachea información a mostrar.",
                "draw(self, superficie): Dibuja la información en la pantalla."
            ],
            "variables_config_clave_settings": [
                "MODO_DEBUG_LOGS", "LOG_CATEGORIAS",
                "BLANCO", "VERDE", "ROJO", # Colores del HUD
                "HUD_PADDING_X", "HUD_PADDING_Y", "HUD_LINE_HEIGHT", "HUD_ESPACIO_ENTRE_SECCIONES" # Layout
            ],
            "notas_adicionales": "Proporciona una interfaz visual para el estado del juego y los controles de logging. Cachea datos en su método update() para optimizar el dibujado."
        },
        {
            "nombre_modulo": "camara.py",
            "categoria": "Renderizado",
            "ruta_relativa": "src/renderizado/camara.py",
            "responsabilidad_principal": "Gestiona la vista del juego, siguiendo a una entidad objetivo (jugador) y aplicando zoom. Calcula qué parte del mundo es visible y transforma las coordenadas del mundo a coordenadas de pantalla. También determina qué sprites son visibles.",
            "interacciones_principales": {
                "entrantes": [
                    "juego.py (para inicialización y llamadas a update)", 
                    "renderer.py (para obtener sprites visibles y aplicar transformaciones a rects)"
                ],
                "salientes": [
                    "settings.py (para leer MODO_DEBUG_LOGS, LOG_CATEGORIAS, y dimensiones físicas de pantalla y del mundo)",
                    "pygame.Rect (para representar la vista de la cámara y los rects transformados)",
                    "logging (usa getLogger('camara') y las categorías 'log_camara', 'log_camara_verbose')"
                ]
            },
            "componentes_clave_internos": [
                "Clase Camara2D",
                "__init__(self, ancho_mundo, alto_mundo, ancho_pantalla_fisica, alto_pantalla_fisica)",
                "update(self, objetivo, factor_zoom_actual): Actualiza la posición y tamaño de la vista de la cámara.",
                "apply(self, rect_mundo, factor_zoom_actual): Transforma un rect del mundo a coordenadas de pantalla.",
                "get_sprites_visibles_ordenados(self, todos_los_sprites): Devuelve sprites visibles y ordenados.",
                "Atributo: self.camera_rect (pygame.Rect que representa la vista de la cámara en el mundo)"
            ],
            "variables_config_clave_settings": [
                "MODO_DEBUG_LOGS",
                "LOG_CATEGORIAS (específicamente 'log_camara', 'log_camara_verbose')",
                "ANCHO_MUNDO_JUEGO", "ALTO_MUNDO_JUEGO",
                "ANCHO_PANTALLA", "ALTO_PANTALLA" # Usadas indirectamente a través de los parámetros del constructor
            ],
            "notas_adicionales": "La cámara se centra en un objetivo y se mantiene dentro de los límites del mundo. El zoom afecta el tamaño de la porción del mundo que es visible."
        }
    ],
    "Assets y Datos": [
        {
            "nombre_modulo": "asset_manager.py",
            "categoria": "Assets y Datos",
            "ruta_relativa": "src/utils/asset_manager.py",
            "responsabilidad_principal": "Gestiona la carga y gestión de assets (texturas, sprites, sonidos, etc.) del juego. Proporciona una interfaz para acceder y gestionar estos assets.",
            "interacciones_principales": {
                "entrantes": [
                    "renderer.py (para obtener assets como el tile de fondo)",
                    "camara.py (para obtener sprites visibles y aplicar transformaciones)",
                    "juego.py (para cargar assets para entidades)",
                    "settings.py (para acceder a rutas de assets)",
                    "gestor_nivel.py (para cargar assets para entidades)",
                    "logging (para registrar eventos y depuración)"
                ],
                "salientes": [
                    "settings.py (para acceder a rutas de assets)",
                    "logging (para registrar eventos y depuración)"
                ]
            },
            "componentes_clave_internos": [
                "Función cargar_asset(ruta_asset)",
                "Función obtener_sprites_visibles(ruta_asset)",
                "Función obtener_tile_de_fondo(ruta_fondo)",
                "Función obtener_sonido(ruta_sonido)",
                "Función obtener_texto(ruta_texto)",
                "Función obtener_animacion(ruta_animacion)",
                "Función obtener_hitbox(ruta_hitbox)",
                "Función obtener_configuracion(ruta_configuracion)",
                "Función obtener_fuentes(ruta_fuentes)",
                "Función obtener_texturas(ruta_texturas)"
            ],
            "variables_config_clave_settings": [
                "MODO_DEBUG_LOGS", "LOG_CATEGORIAS (log_asset_manager)",
                "RUTA_BASE_PROYECTO", "RUTA_ASSETS", "RUTA_IMAGENES", "RUTA_SONIDOS", "RUTA_TEXTOS", "RUTA_ANIMACIONES", "RUTA_HITBOXES", "RUTA_CONFIGURACIONES", "RUTA_FUENTES", "RUTA_TEXTURAS"
            ],
            "notas_adicionales": "Debe manejar errores de carga de forma robusta, devolviendo placeholders si un asset no se encuentra."
        }
        # gestor_nivel.py podría ir aquí o en Sistemas dependiendo de su enfoque.
    ],
    "Utilidades": [
        {
            "nombre_modulo": "utils.py",
            "categoria": "Utilidades",
            "ruta_relativa": "src/utils/utils.py",
            "responsabilidad_principal": "Proporciona funciones de utilidad genéricas que pueden ser usadas por múltiples módulos del proyecto. Ejemplos: manipulación de vectores, conversiones de datos (como deltas flotantes a enteros para colisiones), formateo de strings, etc.",
            "interacciones_principales": {
                "entrantes": [
                    "jugador.py (para convertir_deltas_a_enteros_para_colision)",
                    "enemigo.py (para convertir_deltas_a_enteros_para_colision)",
                    "Cualquier otro módulo que necesite funciones de utilidad comunes."
                ],
                "salientes": [
                    "settings.py (potencialmente para alguna constante de utilidad o control de logging)",
                    "logging (si las funciones de utilidad realizan logging)"
                ]
            },
            "componentes_clave_internos": [
                "Función convertir_deltas_a_enteros_para_colision(dx_float, dy_float, umbral_movimiento)",
                "Función calcular_vector_hacia_objetivo(punto_origen, punto_destino)",
                "Función normalizar_vector(vector)",
                "Función formatear_tiempo(segundos)"
                # ... otras funciones de utilidad ...
            ],
            "variables_config_clave_settings": [
                "MODO_DEBUG_LOGS", "LOG_CATEGORIAS (log_utils)" # Si se añade logging a utils
            ],
            "notas_adicionales": "Módulo destinado a contener código reutilizable y genérico para evitar duplicación y mantener otros módulos más enfocados en su responsabilidad principal."
        }
    ]
}

if __name__ == '__main__':
    # Ejemplo de cómo se podría acceder y usar esta información
    for categoria, modulos in MAPA_MODULOS_POR_CATEGORIA.items():
        print(f"Categoría: {categoria}")
        for modulo in modulos:
            print(f"  Módulo: {modulo['nombre_modulo']}")
            # print(f"    Ruta: {modulo['ruta_relativa']}")
            # print(f"    Responsabilidad: {modulo['responsabilidad_principal']}")
        print("-" * 20) 