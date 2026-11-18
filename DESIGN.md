---
name: Violencia armada · conflicto global y homicidios en Colombia
description: Dashboard en Streamlit construido como un espécimen tipográfico en rejilla, en negro, blanco y rojo.
colors:
  rojo: "#FF3B2A"
  rojo-2: "#E0190F"
  rojo-3: "#A31010"
  rojo-4: "#4A0806"
  tinta: "#0A0A0A"
  tinta-2: "#121212"
  filete: "#262626"
  filete-2: "#3A3A3A"
  gris-1: "#5A5A5A"
  gris-2: "#8A8A8A"
  gris-3: "#B8B8B8"
  blanco: "#F2F2F2"
typography:
  display:
    fontFamily: "Chakra Petch, sans-serif"
    fontSize: "clamp(40px, 5vw, 76px)"
    fontWeight: 700
    lineHeight: 0.86
    letterSpacing: "-0.01em"
    fontFeature: "tnum"
  headline:
    fontFamily: "Chakra Petch, sans-serif"
    fontSize: "clamp(2.1rem, 3.4vw, 3.15rem)"
    fontWeight: 700
    lineHeight: 1
    letterSpacing: "-0.005em"
  cifra:
    fontFamily: "Chakra Petch, sans-serif"
    fontSize: "clamp(2rem, 3.4vw, 3.2rem)"
    fontWeight: 700
    lineHeight: 0.9
    fontFeature: "tnum"
  title:
    fontFamily: "Chakra Petch, sans-serif"
    fontSize: "1.75rem"
    fontWeight: 700
    letterSpacing: "-0.005em"
  subtitle:
    fontFamily: "Chakra Petch, sans-serif"
    fontSize: "1.15rem"
    fontWeight: 600
    letterSpacing: "0.06em"
  label:
    fontFamily: "Chakra Petch, sans-serif"
    fontWeight: 600
    letterSpacing: "0.07em"
  entrada:
    fontFamily: "Barlow, system-ui, sans-serif"
    fontSize: "1.08rem"
    fontWeight: 400
    lineHeight: 1.5
  body:
    fontFamily: "Barlow, system-ui, sans-serif"
    fontSize: "1rem"
    fontWeight: 400
  nota:
    fontFamily: "Barlow, system-ui, sans-serif"
    fontSize: "0.82rem"
    fontWeight: 400
  data:
    fontFamily: "Martian Mono, monospace"
    fontSize: "11.5px"
    fontWeight: 400
rounded:
  none: "0px"
spacing:
  celda: "5px"
  rejilla: "24px"
  contenido-max: "1480px"
  contenido-arriba: "3.6rem"
  contenido-abajo: "4rem"
components:
  button-primary:
    backgroundColor: "{colors.blanco}"
    textColor: "{colors.tinta}"
    typography: "{typography.label}"
    rounded: "{rounded.none}"
  button-primary-hover:
    backgroundColor: "{colors.rojo}"
    textColor: "{colors.tinta}"
  button-secondary:
    backgroundColor: "{colors.tinta}"
    textColor: "{colors.blanco}"
    typography: "{typography.label}"
    rounded: "{rounded.none}"
  button-secondary-hover:
    backgroundColor: "{colors.rojo}"
    textColor: "{colors.tinta}"
  input:
    backgroundColor: "{colors.tinta-2}"
    textColor: "{colors.blanco}"
    rounded: "{rounded.none}"
  chip-seleccion:
    backgroundColor: "{colors.rojo-4}"
    textColor: "{colors.blanco}"
    rounded: "{rounded.none}"
  nav-link:
    textColor: "{colors.blanco}"
    typography: "{typography.label}"
    rounded: "{rounded.none}"
  cifra:
    backgroundColor: "{colors.tinta}"
    textColor: "{colors.blanco}"
    typography: "{typography.cifra}"
    padding: "14px 18px 12px"
  cifra-plano-rojo:
    backgroundColor: "{colors.rojo}"
    textColor: "{colors.tinta}"
    typography: "{typography.cifra}"
    padding: "14px 18px 12px"
  modulo-grafica:
    backgroundColor: "{colors.tinta}"
    textColor: "{colors.blanco}"
    rounded: "{rounded.none}"
    padding: "6px 10px 2px"
  accion-explorar:
    backgroundColor: "{colors.blanco}"
    textColor: "{colors.tinta}"
    typography: "{typography.label}"
    padding: "12px 16px 12px 20px"
  accion-explorar-hover:
    backgroundColor: "{colors.rojo}"
    textColor: "{colors.tinta}"
---

# Design System: Violencia armada · conflicto global y homicidios en Colombia

## Overview

**Creative North Star: "El espécimen en rejilla"**

Cada vista es una lámina de un espécimen tipográfico al estilo de Wim Crouwel: el mapa, las cifras y las gráficas se montan sobre una única rejilla de construcción visible (filetes de tinta cada 24 px sobre fondo negro) y los datos son la prueba. El sistema es plano, ortogonal y cerrado: tinta negra, tinta blanca, una rampa de seis grises y una rampa de cuatro rojos; nada más. La densidad es alta pero ordenada, con módulos delimitados por filetes de 1 px y radio cero en todas partes.

La unidad mínima es la celda de 5 px (4 px de tinta y 1 px de separación). El mapamundi está hecho de esas celdas, y las barras de las gráficas y las franjas HTML repiten el mismo paso, de modo que toda la aplicación parece salir de la misma trama. La única rebeldía es la diagonal: un trazo oblicuo marca lo activo, la acción y lo seleccionado, y nada más es oblicuo.

El tono es sobrio. Se trata de muertes reales: el rojo mide intensidad y nombra el conflicto armado; nunca decora. La aplicación rechaza el tablero oscuro genérico de filtros en barra lateral y tarjetas de KPI redondeadas.

**Key Characteristics:**
- Rejilla de construcción visible de 24 px sobre tinta, que se traza al cargar.
- Paleta cerrada: tinta, seis grises, blanco y cuatro rojos.
- Radio cero y filetes de 1 px; sin sombras salvo el tooltip del mapa.
- Celda de 5 px compartida por mapa, barras y franjas.
- Chakra Petch para cifras y títulos, Barlow para la interfaz, Martian Mono para los datos.
- Diagonal roja como único gesto oblicuo.
- Movimiento constructivo: las cosas se arman, se trazan y cuentan; nunca rebotan.

## Colors

Negro, blanco y rojo con sus variantes, y ningún otro tono (compromiso de marca de PRODUCT.md).

### Primary
- **Rojo señal** (rojo): el acento único. Plano de la cifra destacada, subrayado diagonal de la sección activa, hover de botones, contorno de foco, rango de la regla de años, focos del mapa, nivel máximo de la escala, selección de texto. En las categorías siempre es "Conflicto armado" y en UCDP "Conflicto estatal".
- **Rojo vivo** (rojo-2): penúltimo nivel del mapa y barras del ranking del hero.
- **Rojo sangre** (rojo-3): nivel 5 del mapa, tramo alto de la escala de calor, barras secundarias o descartadas cuando la principal va en rojo señal.
- **Rojo hondo** (rojo-4): fondo de las etiquetas seleccionadas en los multiselect y primer tramo rojo de la escala de calor.

### Neutral
- **Tinta** (tinta): fondo de la aplicación, de los módulos de gráfica y del tooltip; color del texto sobre el plano rojo.
- **Tinta 2** (tinta-2): líneas de la rejilla de fondo, fondo de campos de formulario, celdas apagadas del mapa, cero de la escala de calor, cuadrícula del eje x.
- **Filete** (filete): filetes de las filas de cifras y listas, borde inferior de la barra superior, primer nivel del mapa, puntos del océano, categoría "Sin información".
- **Filete 2** (filete-2): borde de botones secundarios, módulos de gráfica, tablas, formularios y expanders; trazo bajo los h2; barra de desplazamiento; "Otras modalidades".
- **Gris 1** (gris-1): filete central de las fronteras del mapa, marcas mayores de la regla, "Delincuencia común", barras atenuadas.
- **Gris 2** (gris-2): notas, marcas de eje en Martian Mono, "Convivencia y riñas", "Violencia unilateral".
- **Gris 3** (gris-3): texto secundario (entradas, leyendas, rótulos bajo las cifras, etiquetas del eje y).
- **Blanco** (blanco): texto principal, botón primario, "Crimen organizado y sicariato" y "Conflicto no estatal", contorno de hover y de focos.

### Named Rules
**The Paleta Cerrada Rule.** Solo los doce tokens existen. Toda gráfica, plantilla y componente HTML los lee de `tema.py` (o de `tokens_css()` en los iframes); ningún hex nuevo entra al código.

**The Rojo Es Conflicto Rule.** En cualquier codificación categórica el rojo es la violencia del conflicto armado y el blanco el crimen organizado; los grises ordenan el resto. Nunca se reasigna.

**The Más Rojo Más Claro Rule.** Las escalas secuenciales suben en luminosidad y en rojo a la vez: tinta-2, rojo-4, rojo-3, rojo. Lo más intenso es lo más claro.

## Typography

**Display Font:** Chakra Petch 600/700 (con sans-serif)
**Body Font:** Barlow 400/500/600 (con system-ui, sans-serif)
**Label/Mono Font:** Martian Mono variable 100–800 (con monospace)

**Character:** Chakra Petch, achaflanada y construida sobre rejilla, da a cifras y títulos un aire de instrumento; Barlow, grotesca de linaje DIN, mantiene la lectura tranquila; Martian Mono alinea los números de ejes, tooltips y celdas. Las tres fuentes se sirven localmente.

### Hierarchy
- **Display** (700, clamp(40px, 5vw, 76px), 0.86): las tres cifras monumentales del hero, con cifras tabulares.
- **Headline** (700, clamp(2.1rem, 3.4vw, 3.15rem), 1): el h1 de cada página, formulado como pregunta o afirmación.
- **Cifra** (700, clamp(2rem, 3.4vw, 3.2rem), 0.9): valores de las filas de cifras y de `st.metric`, tabulares.
- **Title** (700, 1.75rem): h2 de sección, con un filete de 1 px que se traza debajo.
- **Subtitle** (600, 1.15rem, mayúsculas, 0.06em): h3; suele enunciar el hallazgo de la gráfica que sigue.
- **Label** (600, mayúsculas, 0.07em): navegación, botones, controles segmentados y pills.
- **Entrada** (400, 1.08rem, 1.5, máx. 68ch, gris-3): párrafo que abre cada bloque.
- **Body** (400, 1rem): texto de interfaz.
- **Nota** (400, 0.82rem, gris-2): fuentes, periodos parciales y advertencias.
- **Data** (Martian Mono, 11.5px en ejes numéricos, 12.5px en tooltips y rótulos de celda): todo número que se lee en una gráfica.

### Named Rules
**The Números En Mono Rule.** En las gráficas los números (eje x, tooltips, rótulos de barras y de calor) van en Martian Mono; las categorías (países, clases, eje y) van en Barlow.

**The Cifra Tabular Rule.** Toda cifra grande usa `tabular-nums` y el formato colombiano (punto de miles, coma decimal), para que el conteo no salte.

## Layout

La rejilla de fondo es literal: dos degradados lineales de 1 px en tinta-2 cada 24 px cubren la aplicación y se despliegan al cargar (1,2 s). El contenido vive en una columna de hasta 1480 px con 3.6rem arriba y 4rem abajo; la marca de la barra superior se alinea con el borde izquierdo de esa columna (margen de 5rem; 1rem por debajo de 735 px).

La navegación es superior, sin barra lateral. Las cifras se organizan en filas de N columnas iguales separadas por filetes verticales, cerradas arriba y abajo por filetes horizontales; en el hero la central es 1.15 veces más ancha. El mapa ocupa el ancho completo, con el ranking superpuesto abajo a la izquierda y la regla de años debajo, con leyenda y acción a la derecha.

Comportamiento adaptable: por debajo de 760 px las filas de cifras pasan a 2 columnas con filetes cruzados y las barras de probabilidad saltan a su propia fila; por debajo de 860 px el hero apila las cifras, el ranking sale del mapa y la regla y su leyenda se apilan; por debajo de 700 px la celda del mapa baja a 4 px y solo se marcan los países pequeños en rojo.

**The Celda Compartida Rule.** El paso de 5 px (4 + 1) es el mismo en el mapa, en el patrón de las barras Plotly y en las franjas HTML (`repeating-linear-gradient` 4 px / 1 px). Una trama nueva usa ese paso.

## Elevation & Depth

El sistema es plano. La profundidad se expresa con filetes de 1 px y con el cambio de tinta a tinta-2, nunca con sombras ni capas flotantes. La única excepción es el tooltip del mapa, que flota sobre el canvas con una sombra difusa.

### Shadow Vocabulary
- **Tooltip del mapa** (`box-shadow: 0 18px 40px -12px rgba(0,0,0,.9)`): separa el tooltip del mapa de celdas que tiene debajo. No se usa en ningún otro sitio.

### Named Rules
**The Filete No Sombra Rule.** Un módulo se delimita con un filete de 1 px (filete o filete-2), no con elevación.

## Shapes

Radio cero en todo: botones, campos, etiquetas, pills, controles segmentados, el pulgar del slider (14 × 20 px), expanders, formularios, alertas y la navegación. Los bordes son filetes de 1 px. Las formas son rectángulos y cuadrados: celdas del mapa, marcadores de leyenda de 10 px, focos cuadrados con un marco blanco separado 2 px.

La diagonal es la única forma oblicua y siempre es un trazo fino (3 px o menos), nunca un plano: el subrayado de 3 px en paralelogramo de la sección activa, el trazo de 14 px a −45° al final de cada botón, el trazo rojo de 16 px que encabeza cada elemento de las listas, los extremos inclinados del rango de años, la flecha diagonal de la acción "Explorar los datos" y la línea de tinta que cruza el plano rojo del hero.

## Components

### Buttons
- **Shape:** rectos (0px), filete de 1 px en filete-2, con un trazo diagonal de 14 × 2 px en `currentColor` a la derecha (padding derecho 2.6rem).
- **Primary:** fondo blanco, texto tinta; Chakra Petch 600, mayúsculas, 0.07em. Lo usan también los botones de formulario y de descarga.
- **Hover / Focus:** el fondo y el borde pasan a rojo con texto tinta (0.2s); foco visible con contorno rojo de 2 px separado 2 px.
- **Secondary:** fondo tinta, texto blanco, mismo filete; mismo hover rojo.

### Chips
- **Style:** las etiquetas seleccionadas de los multiselect son rectángulos rojo-4 con texto blanco; pills y controles segmentados van rectos en Chakra Petch, mayúsculas, 0.06em.
- **State:** el color de selección lo da el tema de Streamlit (primario rojo).

### Cards / Containers
- **Corner Style:** 0px.
- **Background:** tinta para módulos de gráfica; tinta-2 al 85 % para formularios.
- **Shadow Strategy:** ninguna (ver Elevation & Depth).
- **Border:** filete-2 de 1 px en módulos de gráfica, tablas, formularios y expanders; `st.metric` solo lleva filete superior.
- **Internal Padding:** módulo de gráfica 6px 10px 2px; estado vacío 28px.

### Inputs / Fields
- **Style:** fondo tinta-2, radio 0, borde del tema (filete-2).
- **Focus:** contorno rojo de 2 px con separación de 2 px, también en el slider.

### Navigation
- **Style:** barra superior de tinta con filete inferior; marca a la izquierda alineada con la columna de contenido; las cinco secciones a la derecha en Chakra Petch 600, mayúsculas, 0.07em. La activa no cambia de fondo: la subraya un paralelogramo rojo de 3 px. Sin barra lateral.

### Fila de cifras
Hasta cuatro cifras sobre la rejilla, separadas por filetes. Cada valor sube con desenfoque al aparecer (0.9s, escalonado 80 ms). Una sola cifra por fila puede ir sobre el plano rojo, con todo su texto en tinta.

### Lista diagonal
Lista sin viñetas: cada elemento abre con un trazo rojo a −45°, título en Chakra Petch, detalle en gris-3 y el tema en gris-2 mayúsculas, separados por filetes. Se usa para hallazgos, recomendaciones y fuentes.

### Franjas de composición y probabilidad
Barras HTML rellenas con la trama de celda (4 px de color, 1 px de hueco) que crecen desde la izquierda (1–1.1s) y toman el color de su categoría. La composición apila las categorías con 2 px de separación; la probabilidad usa una rejilla etiqueta / barra / valor en Chakra Petch tabular.

### Estado vacío
Recuadro con filete-2, 28 px de relleno y textura de puntos desfasados (puntos de 1 px cada 12 px), con texto en gris-3 que dice qué hacer.

### Gráficas (plantilla "rejilla")
Fondo transparente dentro de un módulo con filete; títulos en Chakra Petch 20 px alineados a la izquierda; cuadrícula en tinta-2 y filete; leyenda horizontal debajo o rótulo directo al final de cada serie; sin barra de herramientas; separadores decimales en español; transición de 600 ms. Las barras llevan la trama de celda superpuesta. En los mapas de calor el rótulo es tinta cuando la celda supera el 86 % del máximo y blanco en el resto, para mantener un contraste de al menos 4,5:1.

### Mapamundi de celdas (componente firma)
Proyección Equal Earth en canvas, a todo el ancho. Cada país se rellena con celdas de 5 px según siete niveles de muertes por 1.000 km² (filete, filete-2, gris-1, gris-2, rojo-3, rojo-2, rojo), con dither por densidad, leídos de los tokens. Las fronteras son una calle de tinta de 2.2 px con un filete gris-1 de 1 px en el centro. El océano lleva puntos desfasados en filete. Los países sin celdas se marcan en su centro con una celda enmarcada. Hasta 16 focos (zonas de 1°) laten en rojo con marco blanco.

Movimiento: al cargar, el mapa se arma celda a celda, los países claros primero y los más rojos al final; al mover la regla de años las celdas cambiadas se voltean; las cifras cuentan con salida exponencial (1,1 s). El hover traza el país en blanco y abre un tooltip con Martian Mono para los valores. La regla de años es el selector de periodo: marcas cada año, mayores cada cinco, rango rojo con extremos inclinados y asas en Chakra Petch. Con `prefers-reduced-motion` todo aparece en su estado final y los focos quedan quietos.

## Do's and Don'ts

### Do:
- **Do** leer cada color de `tema.py` o de las variables de `tokens_css()`; doce tokens, ningún otro.
- **Do** delimitar cada módulo con un filete de 1 px y radio 0px.
- **Do** usar el paso de celda de 5 px (4 + 1) en toda trama nueva, ya sea Plotly (`tema.celdas`) o HTML.
- **Do** poner los números de las gráficas en Martian Mono y las categorías en Barlow.
- **Do** reservar el rojo para intensidad, conflicto armado, estado activo, acción y foco.
- **Do** dejar como máximo una cifra por fila sobre el plano rojo, con el texto en tinta.
- **Do** usar la curva `cubic-bezier(.16,1,.3,1)` para todo lo que se arma, traza o crece, y respetar `prefers-reduced-motion`.
- **Do** citar la fuente y marcar el periodo parcial (2026*) en una nota gris-2.

### Don't:
- **Don't** redondear esquinas ni usar tarjetas de KPI redondeadas.
- **Don't** introducir tonos fuera del negro, blanco, gris y rojo.
- **Don't** reasignar el rojo de "Conflicto armado" a otra categoría.
- **Don't** añadir sombras a módulos, botones o cifras; la única sombra es la del tooltip del mapa.
- **Don't** introducir formas oblicuas más allá de los trazos diagonales finos (3 px o menos); todo lo demás es ortogonal.
- **Don't** volver a la barra lateral de filtros; los filtros van en el cuerpo, sobre la rejilla.
- **Don't** mostrar la barra de herramientas de Plotly.
