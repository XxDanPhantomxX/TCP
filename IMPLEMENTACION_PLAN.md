# LOG DE IMPLEMENTACION: servidor TCP concurrente
## Estado Actual: Hito 1 de 2
### Instrucciones Tecnicas
Objetivo: Transformar el servidor TCP secuencial en un servidor concurrente que atienda múltiples clientes mediante hilos.

Lógica principal:
- Crear socket TCP y `listen()`.
- Aceptar conexiones en un bucle principal.`accept()` devuelve `(conn, addr)`.
- Por cada conexión aceptada, incrementar contador de clientes activos protegido por un `Lock`.
- Lanzar un `Thread` (daemon) que ejecute `handle_client(conn, addr)` para atender la sesión.
- `handle_client` debe recibir datos en un bucle (`recv`), procesarlos (eco), enviar respuesta (`sendall`) y cerrar la conexión al terminar. Al finalizar, decrementar el contador de clientes activos.

Requisitos de salida por consola:
- Imprimir cuando un cliente se conecta: cliente conectado y su dirección.
- Imprimir los mensajes recibidos con su contenido.
- Imprimir cuando un cliente se desconecta.
- Imprimir el número de clientes activos tras cada conexión y desconexión.

### Conceptos Clave
- Servidor bloqueante vs concurrente: el `accept()` es bloqueante en el hilo principal, pero cada conexión debe ser atendida en su propio hilo para evitar bloquear otras conexiones.
- `Thread` (de la librería `threading`) para concurrencia ligera I/O-bound.
- `Lock` para sincronizar el acceso al contador de clientes activos.
- Cada hilo deberá ser `daemon=True` para facilitar el cierre del proceso si el hilo principal finaliza.

### Checklist de Progreso
- [x] Revisar `servidor.py`
- [ ] Hito actual: Implementar servidor concurrente (en desarrollo)
- [ ] Probar el servidor y validar comportamiento con múltiples clientes

## Ciclo de Verificacion Interna
1. No entregar implementación completa sin validar este hito.
2. No incluir bloques de código mayores a 5 líneas en esta fase; sólo firmas y pseudocódigo.
3. Mantener el checklist actualizado.

### Esqueleto sugerido (firmas / pseudocódigo)
```
from threading import Thread, Lock

active_clients = 0
clients_lock = Lock()

def handle_client(conn, addr):
    # bucle: recv -> procesar -> sendall; cerrar conn; actualizar contador
    pass

def main():
    sock = socket.socket(...)
    sock.bind(...)
    sock.listen(5)
    while True:
        conn, addr = sock.accept()
        with clients_lock: active_clients += 1
        Thread(target=handle_client, args=(conn, addr), daemon=True).start()
```

---
Preguntas de validación:
- ¿Confirmas que proceda a implementar el `handle_client` y modificar `servidor.py` siguiendo este plan?
