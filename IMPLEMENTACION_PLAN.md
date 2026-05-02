# LOG DE IMPLEMENTACION: Cliente Generador de Carga TCP

## Estado Actual: Hito 5 de 5

### Hito 1: Cliente con envío continuo y medición de tiempos

#### Objetivo
Transformar `cliente.py` para que:
- Envíe mensajes en un bucle continuo
- Mida el tiempo que tarda cada mensaje en recibir respuesta
- Registre estadísticas: min, max, promedio de tiempo de respuesta
- Permita configurar parámetros (host, puerto, intervalo entre mensajes, número de mensajes)

#### Lógica de Negocio

**Estructura del cliente:**
```
1. Conectar al servidor
2. Para cada iteración (N veces):
   a. Registrar tiempo inicial (t_inicio)
   b. Enviar mensaje
   c. Recibir respuesta
   d. Registrar tiempo final (t_fin)
   e. Calcular latencia = t_fin - t_inicio
   f. Guardar en lista de latencias
3. Cerrar conexión
4. Calcular y mostrar estadísticas
```

**Tiempo de respuesta:**
- Usar `time.time()` o `time.perf_counter()` (más preciso)
- Registrar timestamp ANTES de `sendall()` y DESPUÉS de `recv()`
- Esto mide latencia de red + tiempo del servidor

#### Conceptos Clave

- **Módulo `time`**: `perf_counter()` es más preciso que `time()` para medir duraciones cortas
- **Estadísticas descriptivas**: min, max, promedio (suma / cantidad), desviación estándar
- **Logging**: usar `logging` o imprimir con timestamp para registrar cada transacción
- **Argumentos configurables**: usar `argparse` o parámetros globales (host, puerto, intervalo, iteraciones)
- **Manejo de errores**: qué ocurre si el servidor no responde o la conexión se cierra

#### Documentación API Relevante

- `socket.socket().connect(addr)` → abre conexión TCP
- `socket.sendall(data)` → envía todos los bytes (bloqueante)
- `socket.recv(bufsize)` → recibe hasta bufsize bytes (bloqueante)
- `time.perf_counter()` → retorna float con tiempo de reloj de pared (precisión de microsegundos)
- `socket.close()` → cierra la conexión

#### Esqueleto Sugerido (Pseudocódigo)

```python
import socket
import time

def cliente_con_medicion(host, puerto, num_mensajes, intervalo_segundos):
    """
    Conecta, envía mensajes, mide tiempo de respuesta.
    Retorna lista de latencias en segundos.
    """
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # conectar
    # crear lista latencias vacía

    for i in range(num_mensajes):
        # t_inicio = perf_counter
        # sendall(mensaje)
        # recv(respuesta)
        # t_fin = perf_counter
        # latencia = t_fin - t_inicio
        # agregar a lista latencias
        # opcional: dormir intervalo_segundos

    # sock.close()
    return latencias

def calcular_estadisticas(latencias):
    """
    Retorna dict con min, max, promedio, etc.
    """
    # implementar lógica de estadísticas
    pass

if __name__ == '__main__':
    latencias = cliente_con_medicion('localhost', 10000, 10, 0.1)
    stats = calcular_estadisticas(latencias)
    print(stats)
```

**Preguntas antes de implementar Hito 1:**
1. ¿Quieres que el cliente registre CADA medición en un archivo (CSV o log)? ¿O solo mostrar resumen final?
2. ¿Qué formato de mensaje enviarás? ¿Siempre el mismo o variable?
3. ¿Intervalo entre mensajes fijo (ej: 100ms) o variable?
4. ¿Número total de mensajes fijo (ej: 1000) o indefinido?

---

## ✅ HITO 1 COMPLETADO

- [x] Cliente con envío continuo: bucle de N iteraciones
- [x] Medición de latencias: `perf_counter()` antes/después de recv
- [x] Estadísticas: min, max, avg, std_dev
- [x] Logging: archivo `latencias.log`
- [x] Pausa configurable entre mensajes: `time.sleep(intervalo_tiempo)`

---

## Hito 2: Generador de Carga Concurrente

### Objetivo

Crear script `load_generator.py` que:
- Lance N instancias de `cliente.py` en **paralelo** (no secuencial)
- Cada instancia ejecuta de forma independiente
- Recopile resultados de todos los clientes
- Genere resumen agregado: tiempo total, clientes completados, latencia global (min, max, avg)

### Lógica de Negocio

**Estructura del generador:**
```
1. Definir número de clientes concurrentes (N)
2. Lanzar N procesos, cada uno ejecutando cliente.py
   - Usar subprocess.Popen() o multiprocessing.Process()
   - Pasar parámetros (iteraciones, intervalo)
3. Esperar a que TODOS los procesos terminen
   - subprocess: poll() o wait()
   - multiprocessing: join()
4. Recopilar salida de cada cliente
   - Parsear stdout o leer archivos de log
5. Calcular estadísticas agregadas
6. Generar reporte: archivo CSV o JSON con resultados por cliente
```

**Decisión de diseño: ¿subprocess o multiprocessing?**
- **subprocess**: Recomendado aquí porque:
  - Cada cliente.py es un script independiente
  - Fácil de configurar parámetros vía argumentos CLI
  - Cada proceso es aislado (no comparte memoria)

- **multiprocessing**: Alternativa si necesitas acceso a memoria compartida

### Conceptos Clave

- **subprocess.Popen()**: Lanza proceso hijo, devuelve objeto para monitorearlo
- **poll()**: Revisa si proceso terminó (no bloqueante)
- **communicate()**: Espera a proceso y captura stdout/stderr
- **Paralelismo vs Secuencial**: Todos los procesos deben iniciarse casi simultáneamente, no uno tras otro
- **Recopilación de resultados**: Leer `latencias.log` de cada cliente o capturar stdout
- **Timestamps**: Para medir tiempo TOTAL de prueba (desde inicio de primer cliente hasta fin del último)

### Documentación API Relevante

- `subprocess.Popen(cmd, stdout=PIPE, stderr=PIPE)` → lanza proceso
- `popen.poll()` → retorna None si activo, código de salida si terminó
- `popen.communicate()` → espera y captura salida completa
- `time.time()` → capturar momento inicio y fin de prueba
- `os.path.join()` → construir rutas de archivos log

### Esqueleto Sugerido (Pseudocódigo)

```python
import subprocess
import time
import os

def lanzar_clientes(num_clientes, iteraciones, intervalo):
    """
    Lanza N instancias de cliente.py en paralelo.
    Retorna lista de procesos.
    """
    procesos = []
    t_inicio_total = time.time()

    for i in range(num_clientes):
        cmd = ['python3', 'cliente.py']  # O pasar parámetros si cliente.py los acepta
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        procesos.append(proc)

    # procesos creados simultáneamente
    return procesos, t_inicio_total

def esperar_clientes(procesos):
    """
    Espera a que TODOS los procesos terminen.
    """
    for proc in procesos:
        proc.wait()  # bloqueante: espera a que termine

def recopilar_resultados(num_clientes):
    """
    Lee latencias.log de cada cliente.
    Agrupa por cliente.
    """
    # lógica para parsear logs o archivos de salida

def calcular_estadisticas_globales(resultados):
    """
    Calcula min, max, avg de TODOS los clientes combinados.
    """
    # agregar todas las latencias
    # calcular estadísticas

if __name__ == '__main__':
    num_clientes = 5
    iteraciones = 100
    intervalo = 0.1

    procesos, t_inicio = lanzar_clientes(num_clientes, iteraciones, intervalo)
    esperar_clientes(procesos)
    t_fin = time.time()

    print(f"Tiempo total: {t_fin - t_inicio:.2f}s")

    # recopilar y mostrar resultados
```

### Preguntas de Validación

**A1.** ¿Cómo pasarás parámetros de `load_generator.py` a `cliente.py`?
- Opción A: Crear archivos de configuración por cliente (cliente_0.ini, cliente_1.ini)
- Opción B: Pasar argumentos CLI (`python cliente.py --iteraciones 100 --intervalo 0.1`)
- Opción C: Usar variables de entorno

**A2.** ¿Dónde guardar resultados agregados?
- Archivo CSV: `resultados_carga_N5.csv` (con N=número de clientes)
- Archivo JSON: `resultados_carga.json`
- Solo consola

**A3.** ¿Qué incluir en reporte?
- Min/max/avg latencia de CADA cliente
- Min/max/avg latencia GLOBAL (todos combinados)
- Tiempo total de ejecución
- Número de mensajes exitosos/fallidos

---

## Hitos siguientes (resumen)

- **Hito 3**: Pruebas incrementales variando N (1, 5, 10, 20, 50 clientes) y recopilación de resultados comparativos
- **Hito 4**: Modificar servidor para introducir `time.sleep()` en `manejar_cliente()`, simular congestión
- **Hito 5**: Repetir Hito 3 con servidor congestionado y generar gráfico comparativo

---

## Hito 3: Pruebas Incrementales y Comparación

### Objetivo

Ejecutar el generador de carga con distintos valores de clientes concurrentes y construir una base comparativa para medir el impacto de la concurrencia sobre la latencia y el tiempo total de ejecución.

Los valores mínimos a probar son:
- `N = 1`
- `N = 5`
- `N = 10`
- `N = 20`
- `N = 50`

### Lógica de Negocio

**Proceso de prueba:**
```
1. Elegir un valor de N.
2. Lanzar `load_generator.py` con `--clientes N`.
3. Repetir con la misma configuración de iteraciones e intervalo.
4. Guardar el reporte por corrida.
5. Comparar tiempo total y latencia global entre corridas.
```

**Qué comparar en cada corrida:**
- Tiempo total de ejecución
- Latencia global mínima, máxima y promedio
- Latencia promedio por cliente
- Cantidad de mensajes procesados por cliente

**Criterio práctico de análisis:**
- Si el sistema escala bien, el tiempo total debería crecer de forma más lenta que el número de clientes hasta cierto punto.
- Un aumento brusco en latencia promedio o máxima sugiere saturación del servidor o del sistema operativo.

### Conceptos Clave

- **Carga controlada**: mantener constantes iteraciones, mensaje e intervalo para aislar el efecto de `N`
- **Comparación entre corridas**: medir tendencias, no solo valores absolutos
- **Repetibilidad**: usar la misma configuración base para cada valor de clientes
- **Observabilidad**: conservar un reporte por corrida para no mezclar resultados

### Documentación API Relevante

- `subprocess.Popen()` → útil para automatizar la ejecución repetida del generador desde un script externo, si se decide después
- `json.dump()` → guardar cada reporte de corrida
- `json.load()` → recuperar reportes anteriores para comparar resultados
- `time.time()` → registrar duración total por corrida

### Esqueleto Sugerido (Pseudocódigo)

```python
valores_n = [1, 5, 10, 20, 50]
for n in valores_n:
    ejecutar carga con n clientes
    guardar reporte con nombre específico
    extraer tiempo total y estadísticas
comparar todos los reportes
```

### Checklist de Progreso

- [x] Hito 1: Cliente con envío continuo y medición
- [x] Hito 2: Generador de carga concurrente
- [x] Hito 3: Pruebas incrementales y recopilación
- [x] Hito 4: Servidor con retrasos
- [x] Hito 5: Análisis comparativo

### Preguntas de Validación

1. ¿Quieres que el Hito 3 se automatice con un script adicional o prefieres ejecutar manualmente cada valor de `N`?
2. ¿El reporte comparativo debe quedar solo en JSON o también en CSV?
3. ¿Mantenemos fijas las iteraciones e intervalo para todas las corridas, o quieres una segunda variable además de `N`?

### Implementación Automática

- Script de automatización: `hito3_automate.py`
- Barrido validado: N=1 y N=2 para prueba corta
- Artefactos generados: `comparativo_hito3.json`, `comparativo_hito3.csv`, y un reporte por corrida `reporte_carga_n<N>.json`

### Hitos 4 y 5

- Servidor con retardo configurable: `servidor.py --delay <segundos>`
- Comparador congestionado vs normal: `hito5_compare.py`
- Artefactos generados: `comparativo_hito5.json`, `comparativo_hito5.csv`, `comparativo_hito5.png`
- Barrido validado: N=1 y N=2 con servidor normal y con retardo

### Checklist de Progreso

- [x] Hito 1: Cliente con envío continuo y medición
- [x] Hito 2: Generador de carga concurrente
- [x] Hito 3: Pruebas incrementales y recopilación
- [x] Hito 4: Servidor con retrasos
- [x] Hito 5: Análisis comparativo

---

### Ciclo de Verificación Interna
1. No entregar `load_generator.py` completo sin validar decisiones de A1, A2, A3.
2. Pseudocódigo primero; implementación después de validación.
3. Probar con N=2 ó N=3 clientes antes de N grandes.
