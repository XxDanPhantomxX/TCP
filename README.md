# Pruebas de Carga TCP - Proyecto MSC

Este proyecto implementa un sistema de pruebas de carga para medir el rendimiento de un servidor TCP concurrente bajo diferentes escenarios de carga.

## Estructura del Proyecto

- **cliente.py**: Cliente TCP que envía mensajes y mide latencias
- **servidor.py**: Servidor TCP concurrente que atiende múltiples clientes
- **load_generator.py**: Generador de carga concurrente que lanza N clientes en paralelo
- **hito3_automate.py**: Automatización del Hito 3 (barrido de N valores)
- **hito5_compare.py**: Comparación entre servidor normal y congestionado

## Comparación Normal vs Congestionado

### Escenario 1: Servidor Normal (sin retardo)

| Clientes | Tiempo Total (s) | Latencia Avg (ms) | Latencia Max (ms) | Delay (s) |
|----------|------------------|-------------------|-------------------|-----------|
| 1        | 1.0490           | 0.293             | 0.603             | 0.0       |
| 5        | 1.0675           | 0.279             | 0.574             | 0.0       |
| 10       | 1.0853           | 0.312             | 1.106             | 0.0       |
| 20       | 1.1475           | 0.359             | 2.758             | 0.0       |
| 50       | 1.3298           | 0.663             | 18.919            | 0.0       |

**Observaciones:**

- Baseline de rendimiento sin congestión
- Escalabilidad razonable hasta N=20
- Degradación notable con N=50

---

### Escenario 2: Servidor Congestionado (retardo 0.5s por respuesta)

| Clientes | Tiempo Total (s) | Latencia Avg (ms) | Latencia Max (ms) | Delay (s) |
|----------|------------------|-------------------|-------------------|-----------|
| 1        | 11.0630          | 1000.804          | 1000.939          | 0.5       |
| 5        | 11.0658          | 1000.655          | 1001.087          | 0.5       |
| 10       | 11.1035          | 1000.745          | 1001.501          | 0.5       |
| 20       | 11.1494          | 1000.744          | 1004.232          | 0.5       |
| 50       | 11.3253          | 1000.862          | 1008.721          | 0.5       |

**Observaciones:**

- Latencia se incrementa ~1 segundo (el retardo configurado)
- Escala de forma más lineal que el caso normal
- El impacto del retardo es dominante sobre la concurrencia

---

## Análisis Comparativo

### Impacto de la Concurrencia

**Servidor Normal:**

- Escalabilidad buena para N ≤ 20
- A partir de N=50 hay contención notable
- Latencia máxima crece exponencialmente

**Servidor Congestionado:**

- Latencia prácticamente constante (~1s por retardo)
- Tiempo total se incrementa linealmente
- La congestión domina el comportamiento del sistema

### Recomendaciones

1. **Para N ≤ 20**: Sistema puede manejar carga sin degradación significativa
2. **Para N > 20**: Considerar balanceo de carga o más recursos
3. **Latencia crítica**: El retardo del servidor es el factor dominante
4. **Escalabilidad**: Mejor investigar contención del sistema operativo en N=50

---

## Hito 5: Tabla Comparativa (Normal vs Congestionado)

Comparación directa entre ambos escenarios para cada número de clientes.

| Clientes | Escenario | Tiempo Total (s) | Latencia Avg (ms) | Latencia Max (ms) | Overhead (ms) |
|----------|-----------|------------------|-------------------|-------------------|---------------|
| 1        | Normal    | 1.0490           | 0.293             | 0.603             | -             |
| 1        | Congestionado | 11.0630      | 1000.804          | 1000.939          | 1000.51       |
| 5        | Normal    | 1.0675           | 0.279             | 0.574             | -             |
| 5        | Congestionado | 11.0658      | 1000.655          | 1001.087          | 1000.38       |
| 10       | Normal    | 1.0853           | 0.312             | 1.106             | -             |
| 10       | Congestionado | 11.1035      | 1000.745          | 1001.501          | 1000.43       |
| 20       | Normal    | 1.1475           | 0.359             | 2.758             | -             |
| 20       | Congestionado | 11.1494      | 1000.744          | 1004.232          | 1000.39       |
| 50       | Normal    | 1.3298           | 0.663             | 18.919            | -             |
| 50       | Congestionado | 11.3253      | 1000.862          | 1008.721          | 1000.20       |

**Interpretación:**

- **Overhead (ms)**: Incremento de latencia promedio debido al retardo del servidor (≈ 1000 ms)
- El retardo añadido (~0.5s) genera un incremento ~1000ms en latencia por cliente
- La concurrencia tiene impacto mínimo cuando el servidor está congestionado
- En modo normal, el impacto de la concurrencia es más visible (18.919ms máximo en N=50 vs 1000.939ms en congestionado)

---

## Observaciones del Comportamiento del Sistema

### Modo Normal (sin congestión)

- **N=1 a N=20**: Comportamiento lineal predecible; latencia máxima < 3ms
- **N=50**: Cambio abrupto; latencia máxima salta a 18.919ms indicando contención en el scheduler del SO
- **Causa**: Cambio de contexto entre más hilos que cores disponibles

### Modo Congestionado (retardo 0.5s)

- **Linealidad perfecta**: Latencia promedio ≈ 1000.7ms independiente de N
- **Invariancia**: El retardo artificial domina; efectos de concurrencia son negligibles (~0.1ms de variación)
- **Implicación**: El cuello de botella está en el servidor, no en la red ni en el cliente

### Degradación Observada

- **Servidor Normal**: Degradación NO lineal; punto de inflexión en N=50
- **Servidor Congestionado**: Degradación lineal; cada cliente añade ~0.2s (10ms × 10 iteraciones con 0.1s intervalo)

---

## Preguntas y Respuestas

### 1. ¿Cómo cambia la latencia al aumentar el número de clientes?

En modo normal, la latencia permanece estable hasta N=20 (~0.3ms promedio), pero con N=50 salta a 0.8ms promedio y 18.9ms máximo. Esto indica que hasta 20 clientes concurrentes el servidor maneja la carga sin contención, pero con 50 hay competencia por recursos del SO (context switching entre hilos).

En modo congestionado, la latencia se mantiene constante (~1000ms) porque el retardo del servidor es el factor dominante, enmascarando cualquier efecto de concurrencia.

---

### 2. ¿Qué ocurre cuando el servidor se satura?

Observamos dos fases de saturación:

- **Fase 1 (N=20→50)**: Contención en CPU/scheduler; latencia máxima crece exponencialmente (2.7ms → 18.9ms)
- **Fase 2 (retardo fijo)**: El servidor responde cada ~1 segundo; la cola de clientes se agranda pero todos reciben respuesta eventualmente

---

### 3. ¿El sistema deja de responder o solo se vuelve más lento?

El sistema **nunca deja de responder**. Incluso con N=50 o con retardo de 0.5s por respuesta:

- Todos los clientes completaron sus iteraciones exitosamente
- No hay timeouts ni desconexiones no controladas
- TCP garantiza entrega incluso bajo carga extrema (ver pregunta 4)

El sistema se vuelve más lento, pero mantiene confiabilidad.

---

### 4. ¿Por qué TCP mantiene la entrega confiable aun bajo carga?

TCP utiliza tres mecanismos clave:

1. **Buffers de kernel**: El SO bufferiza datos en cola cuando el receptor no consume rápido
2. **Control de flujo (ventana deslizante)**: El receptor anuncia cuántos bytes puede recibir; el emisor respeta este límite
3. **Retransmisión con timeout**: Si no llega ACK, TCP reenvía el segmento automáticamente

En nuestro test, los buffers de TCP fueron suficientes porque el servidor eventualmente procesa todos los datos, aunque lentamente. Los clientes esperan pacientemente (pueden dormir en recv) sin forzar desconexión.

---

### 5. ¿Qué diferencias se esperarían si se utilizara UDP?

Con UDP observaríamos cambios drásticos:

| Aspecto | TCP (actual) | UDP |
|--------|------------|-----|
| **Entrega** | 100% garantizada | ~95-98% (pérdidas posibles) |
| **Latencia** | Variable pero consistente | Mucho más baja inicialmente |
| **Bajo carga** | Se vuelve lento pero confiable | Puede perder paquetes silenciosamente |
| **Comportamiento N=50** | 18.9ms max | Podría ser 1-2ms max, pero ≈5% de mensajes perdidos |
| **Debugging** | Fácil; se ve todo | Difícil; pérdidas silenciosas |

**Conclusión**: TCP es más lento pero predecible y confiable; UDP es rápido pero requiere lógica de aplicación para detectar/recuperar pérdidas.

---

## Ejecución

### Hito 3 (Servidor Normal)

```bash
python hito3_automate.py --valores 1 5 10 20 50
```

### Hito 5 (Comparación Normal vs Congestionado)

```bash
python hito5_compare.py --valores 1 5 10 20 50 --delay 0.5
```

### Servidor Standalone

```bash
# Sin retardo (normal)
python servidor.py

# Con retardo (congestionado)
python servidor.py --delay 0.05
```

---

## Resultados Almacenados

- **hito3_resultados/**: Resultados del Hito 3 (servidor normal)
  - `comparativo_hito3.json`: Datos completos en JSON
  - `comparativo_hito3.csv`: Datos en formato CSV
  - `reporte_carga_n<N>.json`: Reporte detallado por corrida

- **hito5_resultados/**: Resultados del Hito 5 (comparación)
  - `comparativo_hito5.json`: Datos de ambos escenarios
  - `comparativo_hito5.csv`: Datos comparativos en CSV
  - `comparativo_hito5.png`: Gráfico de comparación
  - `normal/`: Reportes del escenario normal
  - `congestionado/`: Reportes del escenario congestionado
