import json
import os
import subprocess
import sys
import time


def parse_args():
    import argparse

    parser = argparse.ArgumentParser(description='Generador de carga concurrente para cliente.py')
    parser.add_argument('--host', default='localhost')
    parser.add_argument('--port', type=int, default=10000)
    parser.add_argument('--clientes', type=int, default=5)
    parser.add_argument('--iteraciones', type=int, default=10)
    parser.add_argument('--intervalo', type=float, default=0.1)
    parser.add_argument('--mensaje', default='Este mensaje se repetira')
    parser.add_argument('--report-file', default='reporte_carga.json')
    return parser.parse_args()


def lanzar_clientes(num_clientes, host, port, iteraciones, intervalo, mensaje):
    """Lanza N instancias del cliente en paralelo."""

    procesos = []
    t_inicio_total = time.time()

    for i in range(num_clientes):
        log_file = f'latencias_cliente_{i + 1}.log'
        json_file = f'resumen_cliente_{i + 1}.json'
        cmd = [
            sys.executable,
            os.path.join(os.path.dirname(__file__), 'cliente.py'),
            '--host', host,
            '--port', str(port),
            '--iteraciones', str(iteraciones),
            '--intervalo', str(intervalo),
            '--log-file', log_file,
            '--json-file', json_file,
            '--mensaje', mensaje,
        ]
        proceso = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        procesos.append(proceso)
        print(f"Lanzado cliente {i+1}/{num_clientes}")

    return procesos, t_inicio_total

def esperar_clientes(procesos):
    """Espera a que todos los procesos terminen y recopila su salida."""

    salidas = []
    for indice, proceso in enumerate(procesos, start=1):
        stdout, stderr = proceso.communicate()
        salidas.append({
            'returncode': proceso.returncode,
            'stdout': stdout,
            'stderr': stderr,
            'json_file': f'resumen_cliente_{indice}.json',
        })

    t_fin_total = time.time()
    return salidas, t_fin_total


def leer_resumen_json(ruta_json):
    with open(ruta_json, 'r', encoding='utf-8') as archivo_json:
        return json.load(archivo_json)

def calcular_estadisticas_globales(resultados):
    """Calcula estadísticas globales a partir de los resultados de los clientes."""

    latencias_globales = []
    latencias_por_cliente = []
    errores_clientes = []

    for resultado in resultados:
        resumen = leer_resumen_json(resultado['json_file'])
        latencias = resumen.get('latencies', [])
        estado = resumen.get('status', 'ok')

        if estado == 'error':
            errores_clientes.append({
                'json_file': resultado['json_file'],
                'error': resumen.get('error'),
            })

        if latencias:
            latencias_globales.extend(latencias)

        latencias_por_cliente.append({
            'json_file': resultado['json_file'],
            'status': estado,
            'stats': resumen.get('stats', {}),
            'latencies': latencias,
            'error': resumen.get('error'),
        })

    if not latencias_globales:
        raise ValueError(f'No se recopilaron latencias de los clientes. Errores: {errores_clientes}')

    tiempo_promedio = sum(latencias_globales) / len(latencias_globales)
    tiempo_maximo = max(latencias_globales)
    tiempo_minimo = min(latencias_globales)


    return {
        'tiempo_promedio': tiempo_promedio,
        'tiempo_maximo': tiempo_maximo,
        'tiempo_minimo': tiempo_minimo,
        'latencias_globales': latencias_globales,
        'latencias_por_cliente': latencias_por_cliente,
        'errores_clientes': errores_clientes,
    }


def guardar_reporte(ruta_reporte, resultados, estadisticas, tiempo_total_ejecucion):
    reporte = {
        'tiempo_total_ejecucion': tiempo_total_ejecucion,
        'clientes_ejecutados': len(resultados),
        'estadisticas_globales': estadisticas,
        'resultados_clientes': [leer_resumen_json(resultado['json_file']) for resultado in resultados],
    }

    with open(ruta_reporte, 'w', encoding='utf-8') as archivo_reporte:
        json.dump(reporte, archivo_reporte, indent=2)


def main():
    args = parse_args()

    # Lanzar los clientes y obtener los procesos
    procesos, t_inicio_total = lanzar_clientes(args.clientes, args.host, args.port, args.iteraciones, args.intervalo, args.mensaje)

    # Esperar a que todos los clientes terminen y obtener el tiempo total
    resultados, t_fin_total = esperar_clientes(procesos)

    # Calcular el tiempo total de ejecución
    tiempo_total_ejecucion = t_fin_total - t_inicio_total
    estadisticas = calcular_estadisticas_globales(resultados)
    guardar_reporte(args.report_file, resultados, estadisticas, tiempo_total_ejecucion)

    print(f"Tiempo total de ejecución para {args.clientes} clientes: {tiempo_total_ejecucion:.2f} segundos")
    print(json.dumps({
        'tiempo_total_ejecucion': tiempo_total_ejecucion,
        'clientes_ejecutados': args.clientes,
        'estadisticas_globales': estadisticas,
        'report_file': args.report_file,
    }, indent=2))

if __name__ == "__main__":
    main()