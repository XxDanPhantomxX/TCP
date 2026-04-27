import socket
from threading import Lock, Thread


clientes_activos = 0
clientes_lock = Lock()


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
                conexion.sendall(datos)
            else:
                print('Cliente desconectado:', cliente_direccion)
                break
    finally:
        conexion.close()
        decrementar_clientes()


def main():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    direccion_servidor = ('localhost', 10000)
    print('Iniciando servidor en {} puerto {}'.format(*direccion_servidor))
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