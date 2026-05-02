import argparse
import json
import logging
import socket
import time


direccion_servidor = ('localhost', 10000)


def parse_args():
    parser = argparse.ArgumentParser(description='Cliente TCP con medición de latencias')
    parser.add_argument('--host', default=direccion_servidor[0])
    parser.add_argument('--port', type=int, default=direccion_servidor[1])
    parser.add_argument('--iteraciones', type=int, default=10)
    parser.add_argument('--intervalo', type=float, default=1.0)
    parser.add_argument('--log-file', default='latencias.log')
    parser.add_argument('--json-file', default=None)
    parser.add_argument('--mensaje', default='Este mensaje se repetira')
    return parser.parse_args()


def configurar_logging(log_file):
    logging.basicConfig(filename=log_file, level=logging.INFO, format='%(asctime)s - %(message)s', force=True)

def cliente(host, puerto, num_mensajes, intervalo_tiempo, mensaje):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((host, puerto))
    latencias = []

    for i in range(num_mensajes):
        mensaje_bytes = mensaje.encode('utf-8')
        print ('Enviando {!r}'.format(mensaje))
        t_inicio = time.perf_counter()
        sock.sendall(mensaje_bytes)
        cantidad_recibida = 0
        cantidad_esperada = len(mensaje_bytes)
        while cantidad_recibida < cantidad_esperada:
            datos = sock.recv(16)
            if not datos:
                raise ConnectionError('La conexion se cerro antes de recibir la respuesta completa')
            cantidad_recibida += len(datos)
            print('Recibido {!r}'.format(datos))
        t_fin = time.perf_counter()
        latencia = t_fin - t_inicio
        latencias.append(latencia)
        logging.info('Latencia: {}'.format(latencia))
        time.sleep(intervalo_tiempo)
    sock.close()
    return latencias

def calcular_estadisticas(latencias):
    min_latencia = min(latencias)
    max_latencia = max(latencias)
    avg_latencia = sum(latencias) / len(latencias)
    standard_deviation = (sum((x - avg_latencia) ** 2 for x in latencias) / len(latencias)) ** 0.5
    return {'min': min_latencia,
            'max': max_latencia,
            'avg': avg_latencia,
            'std_dev': standard_deviation
    }


def main():
    args = parse_args()
    configurar_logging(args.log_file)
    print('Conectando a {} puerto {}'.format(args.host, args.port))
    resumen = {
        'host': args.host,
        'port': args.port,
        'iteraciones': args.iteraciones,
        'intervalo': args.intervalo,
        'latencies': [],
        'stats': None,
        'log_file': args.log_file,
        'json_file': args.json_file,
        'status': 'ok',
        'error': None,
    }

    try:
        latencias = cliente(args.host, args.port, args.iteraciones, args.intervalo, args.mensaje)
        resumen['latencies'] = latencias
        resumen['stats'] = calcular_estadisticas(latencias)
    except Exception as error:
        resumen['status'] = 'error'
        resumen['error'] = str(error)

    resumen_json = json.dumps(resumen)

    if args.json_file:
        with open(args.json_file, 'w', encoding='utf-8') as archivo_json:
            json.dump(resumen, archivo_json, indent=2)

    print(resumen_json)

if __name__ == '__main__':
    main()