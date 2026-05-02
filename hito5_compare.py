import argparse
import json
import socket
import subprocess
import sys
import time
from pathlib import Path


DEFAULT_VALUES = [1, 5, 10, 20, 50]


def parse_args():
    parser = argparse.ArgumentParser(description='Compara Hito 3 con servidor normal y servidor con retardo')
    parser.add_argument('--host', default='localhost')
    parser.add_argument('--port', type=int, default=10001)
    parser.add_argument('--iteraciones', type=int, default=10)
    parser.add_argument('--intervalo', type=float, default=0.1)
    parser.add_argument('--mensaje', default='Este mensaje se repetira')
    parser.add_argument('--valores', nargs='+', type=int, default=DEFAULT_VALUES)
    parser.add_argument('--delay', type=float, default=0.5)
    parser.add_argument('--output-dir', default='hito5_resultados')
    return parser.parse_args()


def esperar_puerto_abierto(host, port, timeout=10.0):
    limite = time.time() + timeout
    while time.time() < limite:
        try:
            with socket.create_connection((host, port), timeout=0.5):
                return
        except OSError:
            time.sleep(0.1)
    raise TimeoutError(f'El servidor no respondió en {host}:{port}')


def iniciar_servidor(base_dir, host, port, delay, log_path):
    server_path = base_dir / 'servidor.py'
    log_handle = open(log_path, 'w', encoding='utf-8')
    proceso = subprocess.Popen(
        [
            sys.executable,
            str(server_path),
            '--host', host,
            '--port', str(port),
            '--delay', str(delay),
        ],
        stdout=log_handle,
        stderr=log_handle,
        text=True,
    )
    return proceso, log_handle


def detener_servidor(proceso, log_handle):
    proceso.terminate()
    try:
        proceso.wait(timeout=5)
    except subprocess.TimeoutExpired:
        proceso.kill()
        proceso.wait(timeout=5)
    log_handle.close()


def ejecutar_hito3(base_dir, host, port, iteraciones, intervalo, mensaje, valores, output_dir):
    hito3_path = base_dir / 'hito3_automate.py'
    cmd = [
        sys.executable,
        str(hito3_path),
        '--host', host,
        '--port', str(port),
        '--iteraciones', str(iteraciones),
        '--intervalo', str(intervalo),
        '--mensaje', mensaje,
        '--output-dir', str(output_dir),
        '--valores', *[str(valor) for valor in valores],
    ]
    resultado = subprocess.run(cmd, capture_output=True, text=True)
    if resultado.returncode != 0:
        raise RuntimeError(
            f'Hito 3 falló en {output_dir}\nSTDOUT:\n{resultado.stdout}\nSTDERR:\n{resultado.stderr}'
        )
    return resultado


def cargar_json(ruta_json):
    with open(ruta_json, 'r', encoding='utf-8') as archivo_json:
        return json.load(archivo_json)


def construir_comparacion(base_dir, host, port, iteraciones, intervalo, mensaje, valores, output_dir, delay):
    escenario_dir = output_dir / ('congestionado' if delay > 0 else 'normal')
    escenario_dir.mkdir(parents=True, exist_ok=True)
    server_log = escenario_dir / 'servidor.log'

    servidor, log_handle = iniciar_servidor(base_dir, host, port, delay, server_log)
    try:
        esperar_puerto_abierto(host, port)
        ejecutar_hito3(
            base_dir=base_dir,
            host=host,
            port=port,
            iteraciones=iteraciones,
            intervalo=intervalo,
            mensaje=mensaje,
            valores=valores,
            output_dir=escenario_dir,
        )
        comparativo = cargar_json(escenario_dir / 'comparativo_hito3.json')
        return {
            'escenario': 'congestionado' if delay > 0 else 'normal',
            'delay': delay,
            'datos': comparativo,
            'output_dir': str(escenario_dir),
        }
    finally:
        detener_servidor(servidor, log_handle)


def guardar_json(ruta_salida, datos):
    with open(ruta_salida, 'w', encoding='utf-8') as archivo_salida:
        json.dump(datos, archivo_salida, indent=2)


def guardar_csv(ruta_salida, comparaciones):
    import csv

    campos = [
        'escenario',
        'clientes',
        'tiempo_total_ejecucion',
        'latencia_promedio',
        'latencia_maxima',
        'latencia_minima',
        'delay',
    ]
    with open(ruta_salida, 'w', encoding='utf-8', newline='') as archivo_salida:
        escritor = csv.DictWriter(archivo_salida, fieldnames=campos)
        escritor.writeheader()
        for comparacion in comparaciones:
            for fila in comparacion['datos']:
                escritor.writerow({
                    'escenario': comparacion['escenario'],
                    'clientes': fila['clientes'],
                    'tiempo_total_ejecucion': fila['tiempo_total_ejecucion'],
                    'latencia_promedio': fila['latencia_promedio'],
                    'latencia_maxima': fila['latencia_max'],
                    'latencia_minima': fila['latencia_min'],
                    'delay': comparacion['delay'],
                })


def generar_grafico(ruta_salida, comparaciones):
    import matplotlib.pyplot as plt

    fig, (ax_tiempo, ax_latencia) = plt.subplots(1, 2, figsize=(12, 5))

    for comparacion in comparaciones:
        clientes = [fila['clientes'] for fila in comparacion['datos']]
        tiempos = [fila['tiempo_total_ejecucion'] for fila in comparacion['datos']]
        latencias = [fila['latencia_promedio'] for fila in comparacion['datos']]
        etiqueta = f"{comparacion['escenario']} (delay={comparacion['delay']})"
        ax_tiempo.plot(clientes, tiempos, marker='o', label=etiqueta)
        ax_latencia.plot(clientes, latencias, marker='o', label=etiqueta)

    ax_tiempo.set_title('Tiempo total de ejecución')
    ax_tiempo.set_xlabel('Clientes concurrentes')
    ax_tiempo.set_ylabel('Segundos')
    ax_tiempo.grid(True, alpha=0.3)
    ax_tiempo.legend()

    ax_latencia.set_title('Latencia promedio')
    ax_latencia.set_xlabel('Clientes concurrentes')
    ax_latencia.set_ylabel('Segundos')
    ax_latencia.grid(True, alpha=0.3)
    ax_latencia.legend()

    fig.suptitle('Comparación Hito 5: servidor normal vs congestionado')
    fig.tight_layout()
    fig.savefig(ruta_salida, dpi=160)
    plt.close(fig)


def main():
    args = parse_args()
    base_dir = Path(__file__).resolve().parent
    output_dir = base_dir / args.output_dir
    output_dir.mkdir(parents=True, exist_ok=True)

    comparaciones = [
        construir_comparacion(
            base_dir=base_dir,
            host=args.host,
            port=args.port,
            iteraciones=args.iteraciones,
            intervalo=args.intervalo,
            mensaje=args.mensaje,
            valores=args.valores,
            output_dir=output_dir,
            delay=0.0,
        ),
        construir_comparacion(
            base_dir=base_dir,
            host=args.host,
            port=args.port,
            iteraciones=args.iteraciones,
            intervalo=args.intervalo,
            mensaje=args.mensaje,
            valores=args.valores,
            output_dir=output_dir,
            delay=args.delay,
        ),
    ]

    comparativo_json = output_dir / 'comparativo_hito5.json'
    comparativo_csv = output_dir / 'comparativo_hito5.csv'
    comparativo_png = output_dir / 'comparativo_hito5.png'

    guardar_json(comparativo_json, comparaciones)
    guardar_csv(comparativo_csv, comparaciones)

    try:
        generar_grafico(comparativo_png, comparaciones)
    except ModuleNotFoundError:
        print('matplotlib no está disponible; se omite la generación del gráfico PNG')

    print('Resumen Hito 5')
    for comparacion in comparaciones:
        print(f"Escenario: {comparacion['escenario']} (delay={comparacion['delay']})")
        for fila in comparacion['datos']:
            print(
                f"N={fila['clientes']}: tiempo_total={fila['tiempo_total_ejecucion']:.4f}s, "
                f"latencia_promedio={fila['latencia_promedio']:.6f}s, "
                f"latencia_max={fila['latencia_max']:.6f}s"
            )

    print(f'Reportes guardados en {comparativo_json}, {comparativo_csv} y {comparativo_png}')


if __name__ == '__main__':
    main()