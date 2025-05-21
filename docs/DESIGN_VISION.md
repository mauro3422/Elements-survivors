# Visión de Diseño del Juego: [Nombre del Juego Tentativo]

*Fecha de Creación: 2025-05-20*
*Última Actualización: 2025-05-20*

## 1. Resumen del Juego (Elevator Pitch)
*(¿De qué trata el juego en una o dos frases?)*

## 2. Género y Plataforma
*   **Género Principal:**
*   **Subgéneros (si aplica):**
*   **Plataforma Objetivo Inicial:** (Ej: PC - Windows)
*   **Motor/Librería Principal:** Pygame

## 3. Pilares del Diseño (Core Pillars)
*(¿Cuáles son las 3-5 ideas o experiencias fundamentales que definen el juego y que deben sentirse en todo momento?)*
*   Pilar 1:
*   Pilar 2:
*   Pilar 3:

## 4. Experiencia del Jugador (Player Experience)
*(¿Qué se supone que debe sentir el jugador? ¿Qué tipo de emociones o desafíos queremos evocar?)*

## 5. Mecánicas Principales (Core Mechanics)
*(Descripción de las acciones y sistemas más importantes con los que interactuará el jugador.)*
*   **Movimiento:**
    *   *(Aquí irán los detalles del movimiento del jugador, incluyendo la mecánica de ser empujado y la posibilidad de resistir activamente el empuje.)*
*   **Combate:**
    *   **Sistema Elemental Dinámico:** Inspirado en la idea de "maestros elementales", los jugadores podrán controlar y manipular diferentes elementos (Tierra, Fuego, Agua, Aire).
        *   Los jugadores pueden invocar/lanzar habilidades elementales (ej. muros de tierra, proyectiles de fuego, ráfagas de aire, chorros de agua que pueden congelarse en hielo).
        *   **Interacciones Elementales:** Se buscará crear un sistema rico donde los elementos puedan interactuar entre sí (ej. agua apagando fuego, fuego derritiendo hielo, aire avivando fuego o dispersando efectos, etc.). La transformación de elementos (agua a hielo) también será una característica.
    *   **Sistema de Impacto Físico (Peso/Fuerza Aplicable a Habilidades Sólidas/Físicas):**
        *   Los personajes y ciertas habilidades (especialmente las de tipo Tierra o Hielo, u otras con manifestación física contundente) poseen un atributo de "peso" o "fuerza", que puede depender del nivel del jugador, estadísticas, o poder de la habilidad.
        *   Las colisiones entre entidades y/o estas habilidades físicas tienen resultados variables basados en la interacción de estas fuerzas y resistencias.
    *   **Interacción Jugador vs. Habilidad Física (Ej: Muro de Tierra/Hielo):**
        *   **Resistencia Pasiva:** El jugador puede resistir el impacto de una habilidad física sin efectos si su resistencia (derivada de armadura, nivel, estadísticas, o afinidad elemental) es suficiente.
        *   **Empuje:** Si la fuerza de la habilidad física supera la resistencia del jugador, este es empujado.
            *   El jugador puede ser empujado contra otros objetos (paredes, otros jugadores), causando efectos secundarios (daño, stun, ruptura de objetos).
            *   **Mecánica de Resistencia Activa:** Se contempla una mecánica donde el jugador puede intentar activamente (ej. mediante inputs específicos, o usando una habilidad defensiva elemental) aumentar su resistencia para detener o mitigar un empuje en curso.
        *   **Stun/Daño por Impacto:** Impactos fuertes pueden causar aturdimiento o daño directo, especialmente si el jugador es empujado contra obstáculos o si su vida/resistencia es baja. Existirá resistencia al stun (posiblemente influenciada por elementos).
    *   **Interacción Habilidad vs. Habilidad (Físicas y Elementales):**
        *   Dos habilidades (ej. dos muros de tierra, un muro de tierra vs. una bola de fuego) pueden colisionar o interactuar.
        *   El resultado (ej. un muro se rompe, la bola de fuego se disipa, se genera vapor, etc.) dependerá de la "fuerza" o "nivel" comparativo de cada habilidad y de sus propiedades elementales.
*   **Progresión del Personaje:**
    *   *(¿Niveles, habilidades, equipamiento?)*
*   **Interacción con el Mundo/NPCs:**
*   **(Otras mecánicas clave):**

## 6. Características Únicas (Unique Selling Points - USPs)
*(¿Qué hace a este juego diferente o especial?)*

## 7. Inspiraciones y Referencias
*(Juegos, películas, libros u otras obras que sirvan de inspiración.)*

## 8. Público Objetivo
*(¿A qué tipo de jugador va dirigido este juego?)*

## 9. Alcance Tentativo (Scope)
*(Una idea inicial del tamaño y complejidad del juego. ¿Será un proyecto pequeño, mediano, grande? ¿Cuántos niveles/zonas, enemigos, objetos, etc., de forma aproximada? Esto se refinará con el tiempo.)*

## 10. Sensación del Juego (Game Feel)
*(Detalles sobre cómo deberían sentirse las acciones del jugador. Ej: ¿El movimiento es rápido y ágil, o pesado y deliberado? ¿El combate es impactante y visceral, o más táctico?)*
*   **Control del Jugador:**
*   **Feedback Visual y Auditivo:**
*   **Impacto de las Acciones:**

## 11. Dirección Artística y Estilo Visual
*(¿Cuál es el estilo visual deseado? ¿Pixel art, cartoon, realista, etc.? ¿Paleta de colores predominante?)*

## 12. Narrativa y Mundo (Si aplica)
*   **Premisa Básica de la Historia:**
*   **Ambientación del Mundo:**
*   **Personajes Clave (si los hay):**

## 13. Monetización (Si se considera a futuro)
*(Inicialmente no relevante, pero se puede añadir si el proyecto crece.)*

## 14. Notas Adicionales / Ideas por Explorar
*(Cualquier otra idea, pregunta o concepto que aún no encaje en las secciones anteriores.)* 