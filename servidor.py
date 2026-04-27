import socket
import sys
import threading

# Crear el socket TCP/IP
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Enlazar el socket a la dirección y puerto
direccion_servidor = ('localhost', 10000)
print('Iniciando servidor en {} puerto {}'.format(*direccion_servidor))
sock.bind(direccion_servidor)

# Escuchar conexiones entrantes
sock.listen(1)

while True:
    print('Esperando una conexión')
    conexion, cliente_direccion = sock.accept()
    try:
        print('Conexión desde', cliente_direccion)

        while True:
            datos = conexion.recv(16)
            print('Recibido {!r}'.format(datos))
            if datos:
                print('Enviando datos de vuelta al cliente')
                conexion.sendall(datos)
            else:
                print('No hay más datos de', cliente_direccion)
                break
    finally:
        conexion.close()