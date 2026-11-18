# Product

<!-- impeccable:product-schema 1 -->

## Platform

web

## Stack

Streamlit (requisito de la guía del curso: Streamlit o Shiny), con CSS propio y componentes HTML/JS embebidos para las piezas que Streamlit no ofrece de forma nativa (el mapamundi de celdas en canvas con su regla de años y sus animaciones). Se ejecuta en un contenedor Docker, en el puerto 8501, dentro del `docker-compose.yml` del proyecto, junto a MongoDB y al servicio de procesamiento.

## Users

Público general: cualquier persona interesada en la violencia armada que llega a explorar los datos por su cuenta, sin conocimientos técnicos previos. La aplicación también se presenta en la sustentación del proyecto (en vivo y en video) y la evalúa el profesor del curso, así que cada sección exigida por la guía debe poder encontrarse y demostrarse con facilidad.

## Product Purpose

Mostrar, con datos oficiales, que la violencia armada no es un solo fenómeno: distinguir la violencia militarizada del conflicto armado de la criminalidad urbana (sicariato, atracos, riñas), primero en el mundo y luego a fondo en Colombia. La aplicación muestra datos ya procesados, tablas, gráficas, los resultados de un modelo de Machine Learning con un formulario de predicción, y los insights y el reporte PDF guardados en MongoDB. El éxito es que un visitante entienda en pocos minutos dónde y de qué tipo es la violencia armada, y que pueda explorar las cifras por su cuenta.

## Positioning

Une dos fuentes oficiales que normalmente se miran por separado: los eventos de violencia organizada del mundo registrados por UCDP (Uppsala University), clasificados en conflicto estatal, no estatal y unilateral, y los homicidios de Colombia del Ministerio de Defensa, con el arma usada y la modalidad. Eso permite pasar de la escala global a la nacional y separar el conflicto armado de la criminalidad urbana con datos de 1989 a 2026.

## Operating Context

- Se usa en el navegador de un computador de escritorio o portátil; también debe verse bien en pantalla de proyector durante la sustentación.
- La aplicación solo lee resultados ya calculados: Parquet en `data/processed/`, el modelo en `models/` y el documento de análisis en MongoDB (`violencia_armada.analisis`). No repite el ETL ni reentrena al abrirse.
- La guía exige estas secciones: Resumen (KPIs), Datos (tabla filtrable y agregaciones), Visualizaciones con filtros (año, región, categoría…), Modelo (métricas, comparación y formulario de predicción) e Insights y reporte (leídos de MongoDB, con descarga del PDF).

## Capabilities and Constraints

- Datos disponibles: 434.601 eventos UCDP (1989–sep 2026) con país, región, coordenadas, tipo de violencia y muertes estimadas; 345.195 registros de homicidios en Colombia (2003–sep 2026) con departamento, municipio, zona, arma, modalidad y 6 categorías de violencia; cubos OLAP y panel mensual UCDP por departamento.
- Modelo: Random Forest que clasifica un homicidio en 4 categorías (conflicto armado, crimen organizado y sicariato, convivencia y riñas, delincuencia común). F1 macro 0,54 frente a 0,20 de la línea base; recall de conflicto armado 0,41 en la prueba. Los resultados deben presentarse con esa honestidad.
- Módulos reutilizables: `src/estilo_graficos.py`, `src/olap.py`, `src/modelo.py`; opciones del formulario en `models/metadatos_modelo.json`.
- UCDP mide eventos y muertes, no tasas por población: no hay datos de población en el proyecto. Cualquier "intensidad de violencia" por país debe definirse con las medidas disponibles y decirse explícitamente cuál es.
- Pendiente de decidir: despliegue fuera del equipo local (por ahora solo diseño).
- Todo el texto de la interfaz va en español.

## Brand Commitments

Restricciones visuales fijadas explícitamente por el usuario:
- Paleta exclusivamente negro, blanco y rojo, con sus variantes (grises; rojos más oscuros o más claros). Ningún otro tono.
- Estética ASCII / dither. Referencias: https://dribbble.com/shots/27133561-AI-Research-Website-Hero y https://dribbble.com/shots/27063621-Card-Design-3D-shape-Dither-effect, además de mapas del mundo hechos con caracteres o celdas hexagonales.
- Al inicio de la página, un mapamundi grande hecho de caracteres o puntos, en una proyección de áreas iguales (no Mercator), con cada país coloreado según la intensidad de la violencia en los datos: rojo intenso para los más violentos, gris o blanco para los más tranquilos.

## Evidence on Hand

- Datos y resultados reales en `data/processed/*.parquet`, `models/modelo_categoria_violencia.joblib`, `models/metadatos_modelo.json` y MongoDB (`violencia_armada.analisis`): 9 insights, 4 recomendaciones, métricas del modelo y agregaciones.
- 11 figuras del análisis en `reports/figuras/` y el reporte `reports/reporte_violencia_armada.pdf`.
- Fuentes: UCDP GED 26.1 y Candidate 2026 (https://ucdp.uu.se/downloads/), homicidios del Ministerio de Defensa (https://www.datos.gov.co/d/m8fd-ahd9).
- No existen testimonios, usuarios reales ni métricas de uso: no se deben inventar.

## Product Principles

1. **Las cifras son oficiales y se citan.** Cada número muestra su fuente y su periodo; los datos parciales (2026) se marcan como parciales.
2. **Del mundo a Colombia.** La narrativa va de la escala global (UCDP) a la nacional (homicidios), y separa siempre el conflicto armado de la criminalidad urbana.
3. **Honestidad sobre los límites.** El modelo y los datos se presentan con sus limitaciones (recall del conflicto, falta de datos de población, filas sin modalidad), sin exagerar.
4. **Explorar sin saber de datos.** Un visitante sin formación técnica debe poder filtrar, leer y entender sin instrucciones.
5. **Respeto por las víctimas.** Se trata de muertes reales: el tono es sobrio y no sensacionalista.
