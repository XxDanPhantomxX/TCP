import argparse
import socket
import time
from threading import Lock, Thread


clientes_activos = 0
clientes_lock = Lock()
retraso_respuesta = 0.0


def parse_args():
    parser = argparse.ArgumentParser(description='Servidor TCP concurrente')
    parser.add_argument('--host', default='localhost')
    parser.add_argument('--port', type=int, default=10000)
    parser.add_argument('--delay', type=float, default=0.0, help='Retardo en segundos antes de responder a cada mensaje')
    return parser.parse_args()


def mostrar_clientes_activos(cantidad):
    print('Clientes activos:', cantidad)


def incrementar_clientes():
    global clientes_activos
    with clientes_lock:
        clientes_activos += 1
        mostrar_clientes_activos(clientes_activos)


def decrementar_clientes():
    global clientes_activos
    with clientes_lock:
        clientes_activos -= 1
        mostrar_clientes_activos(clientes_activos)


def manejar_cliente(conexion, cliente_direccion):
    print('Cliente conectado:', cliente_direccion)
    try:
        while True:
            datos = conexion.recv(16)
            print('Recibido {!r} de {}'.format(datos, cliente_direccion))
            if datos:
                if retraso_respuesta > 0:
                    time.sleep(retraso_respuesta)
                conexion.sendall(datos)
            else:
                print('Cliente desconectado:', cliente_direccion)
                break
    finally:
        conexion.close()
        decrementar_clientes()


def main():
    global retraso_respuesta

    args = parse_args()
    retraso_respuesta = args.delay

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    direccion_servidor = (args.host, args.port)
    print('Iniciando servidor en {} puerto {}'.format(*direccion_servidor))
    if retraso_respuesta > 0:
        print('Aplicando retardo por respuesta de {} segundos'.format(retraso_respuesta))
    sock.bind(direccion_servidor)

    sock.listen(5)
    while True:
        print('Esperando una conexión')
        conexion, cliente_direccion = sock.accept()
        incrementar_clientes()
        hilo_cliente = Thread(target=manejar_cliente, args=(conexion, cliente_direccion), daemon=True)
        hilo_cliente.start()


if __name__ == '__main__':
    main()