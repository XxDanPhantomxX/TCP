import argparse
import csv
import json
import subprocess
import sys
from pathlib import Path


DEFAULT_VALUES = [1, 5, 10, 20, 50]


def parse_args():
    parser = argparse.ArgumentParser(description='Automatiza el Hito 3 ejecutando pruebas incrementales de carga')
    parser.add_argument('--host', default='localhost')
    parser.add_argument('--port', type=int, default=10000)
    parser.add_argument('--iteraciones', type=int, default=10)
    parser.add_argument('--intervalo', type=float, default=0.1)
    parser.add_argument('--mensaje', default='Este mensaje se repetira')
    parser.add_argument('--valores', nargs='+', type=int, default=DEFAULT_VALUES)
    parser.add_argument('--output-dir', default='hito3_resultados')
    return parser.parse_args()


def ejecutar_carga(base_dir, host, port, clientes, iteraciones, intervalo, mensaje, report_file):
    script_path = base_dir / 'load_generator.py'
    cmd = [
        sys.executable,
        str(script_path),
        '--host', host,
        '--port', str(port),
        '--clientes', str(clientes),
        '--iteraciones', str(iteraciones),
        '--intervalo', str(intervalo),
        '--mensaje', mensaje,
        '--report-file', str(report_file),
    ]
    resultado = subprocess.run(cmd, capture_output=True, text=True)
    return resultado


def cargar_reporte(ruta_reporte):
    with open(ruta_reporte, 'r', encoding='utf-8') as archivo_reporte:
        return json.load(archivo_reporte)


def resumir_corrida(clientes, ruta_reporte):
    reporte = cargar_reporte(ruta_reporte)
    estadisticas = reporte.get('estadisticas_globales', {})
    return {
        'clientes': clientes,
        'report_file': str(ruta_reporte),
        'tiempo_total_ejecucion': reporte.get('tiempo_total_ejecucion'),
        'latencia_min': estadisticas.get('tiempo_minimo'),
        'latencia_max': estadisticas.get('tiempo_maximo'),
        'latencia_promedio': estadisticas.get('tiempo_promedio'),
        'clientes_ejecutados': reporte.get('clientes_ejecutados'),
        'errores_clientes': estadisticas.get('errores_clientes', []),
    }


def guardar_json(ruta_salida, datos):
    with open(ruta_salida, 'w', encoding='utf-8') as archivo_salida:
        json.dump(datos, archivo_salida, indent=2)


def guardar_csv(ruta_salida, filas):
    campos = [
        'clientes',
        'clientes_ejecutados',
        'tiempo_total_ejecucion',
        'latencia_min',
        'latencia_max',
        'latencia_promedio',
        'report_file',
    ]
    with open(ruta_salida, 'w', encoding='utf-8', newline='') as archivo_salida:
        escritor = csv.DictWriter(archivo_salida, fieldnames=campos)
        escritor.writeheader()
        for fila in filas:
            escritor.writerow({campo: fila.get(campo) for campo in campos})


def imprimir_resumen(filas):
    print('Resumen Hito 3')
    for fila in filas:
        print(
            f"N={fila['clientes']}: tiempo_total={fila['tiempo_total_ejecucion']:.4f}s, "
            f"latencia_promedio={fila['latencia_promedio']:.6f}s, "
            f"latencia_max={fila['latencia_max']:.6f}s"
        )


def main():
    args = parse_args()
    base_dir = Path(__file__).resolve().parent
    output_dir = base_dir / args.output_dir
    output_dir.mkdir(parents=True, exist_ok=True)

    corridas = []

    for clientes in args.valores:
        report_file = output_dir / f'reporte_carga_n{clientes}.json'
        print(f'Ejecutando carga con N={clientes}')
        resultado = ejecutar_carga(
            base_dir=base_dir,
            host=args.host,
            port=args.port,
            clientes=clientes,
            iteraciones=args.iteraciones,
            intervalo=args.intervalo,
            mensaje=args.mensaje,
            report_file=report_file,
        )

        if resultado.returncode != 0:
            raise RuntimeError(
                f'load_generator.py falló para N={clientes}\nSTDOUT:\n{resultado.stdout}\nSTDERR:\n{resultado.stderr}'
            )

        corridas.append(resumir_corrida(clientes, report_file))

    resumen_json = output_dir / 'comparativo_hito3.json'
    resumen_csv = output_dir / 'comparativo_hito3.csv'

    guardar_json(resumen_json, corridas)
    guardar_csv(resumen_csv, corridas)
    imprimir_resumen(corridas)
    print(f'Reportes guardados en {resumen_json} y {resumen_csv}')


if __name__ == '__main__':
    main()