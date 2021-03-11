import socket
import threading
import json


HEADER = 64
HOST = socket.gethostbyname(socket.gethostname())
PORT = 5050
DISCONNECT_MSG = "!DC"
READY_MSG = "!READY"
ROOM_OPEN = True

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))

userList = []  # (username, conn)
msgList = []  # (conn, message)
room = []
#connected = False


def handleClientIncoming(conn, addr):
    global room, ROOM_OPEN
    user_len = conn.recv(HEADER).decode('utf-8')
    username = conn.recv(int(user_len)).decode('utf-8')
    while any([username in user for user in room]):
        sendMsg(conn, '0')
        user_len = conn.recv(HEADER).decode('utf-8')
        username = conn.recv(int(user_len)).decode('utf-8')
    else:
        room.append((username, conn))
        sendMsg(conn, '1')
    while ROOM_OPEN:
        msg_len = conn.recv(HEADER).decode('utf-8')
        msg = conn.recv(int(msg_len)).decode('utf-8')
        if msg == READY_MSG:
            ROOM_OPEN = False
            startRoom(room)


def startRoom(userList):
    users = [user[0] for user in userList]
    for user in userList:
        sendMsg(user[1], users)


# def messagesOutgoing():
#     global msgList, userList
#     while True:
#         if len(msgList):
#             for msg in msgList:
#                 for user in userList:
#                     sendMsg(user[1], msg)
#             msgList.pop(0)


def sendMsg(conn, msg):
    message = json.dumps(msg).encode("utf-8")
    msg_len = len(message)
    send_len = str(msg_len).encode('utf-8')
    send_len += b' ' * (HEADER - len(send_len))
    conn.send(send_len)
    conn.send(message)


def start():
    server.listen()
    # outGoingThread = threading.Thread(target=messagesOutgoing).start()
    while True:
        conn, addr = server.accept()
        incomingThread = threading.Thread(
            target=handleClientIncoming, args=(conn, addr)).start()


print(f"Starting server on {HOST}")

if __name__ == "__main__":
    start()
