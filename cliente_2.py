import socket
import sys

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

direccion_servidor = ('localhost', 10000)
print('Conectando a {} puerto {}'.format(*direccion_servidor))
sock.connect(direccion_servidor)

def main():
    try:
        mensaje = b'Cliente 2: Este mensaje se repetiras'
        print ('Enviando {!r}'.format(mensaje))
        sock.sendall(mensaje)

        cantidad_recibida = 0
        cantidad_esperada = len(mensaje)

        while cantidad_recibida < cantidad_esperada:
            datos = sock.recv(16)
            cantidad_recibida += len(datos)
            print('Recibido {!r}'.format(datos))
    finally:
        #print('Cerrando socket')
        #sock.close()
        pass

if __name__ == '__main__':
    while True:
        main()