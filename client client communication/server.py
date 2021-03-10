import socket
import threading

HEADER = 64
HOST = socket.gethostbyname(socket.gethostname())
PORT = 5050
DISCONNECT_MSG = "!DC"

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))

pendingMessages = []
# message structure: (addr, msg)


def handleClientIncoming(conn, addr):
    global pendingMessages
    print(f"New Connection: {addr}")
    connected = True
    while connected:
        msg_len = conn.recv(HEADER).decode("utf-8")
        if msg_len:
            msg_len = int(msg_len)
            msg = conn.recv(msg_len).decode("utf-8")
            pendingMessages.append((addr, msg))
            if msg == DISCONNECT_MSG:
                connected = False
            print(f"[{addr}] {msg}")
    print("disconnected")
    conn.close()


def handleClientOutgoing(conn, addr):
    global pendingMessages
    connected = True
    while connected:
        try:
            nextMsg = pendingMessages[0]
            if nextMsg[0] == addr and nextMsg[1] == DISCONNECT_MSG:
                connected = False
                break
            if nextMsg[0] != addr:
                # conn.send(nextMsg[1].encode('utf8'))
                msg = nextMsg[1].encode('utf-8')
                msg_len = len(msg)
                send_len = str(msg_len).encode('utf-8')
                send_len += b' ' * (HEADER - len(send_len))
                conn.send(send_len)
                conn.send(msg)
                pendingMessages.pop(0)
        except IndexError:
            pass


def start():
    server.listen()
    while True:
        conn, addr = server.accept()
        incomingThread = threading.Thread(
            target=handleClientIncoming, args=(conn, addr)).start()
        outgoingThread = threading.Thread(
            target=handleClientOutgoing, args=(conn, addr)).start()
        print(f"Active Connections: {(threading.activeCount() - 1)/2}")


print(f"Starting server on {HOST}")

if __name__ == "__main__":
    start()
