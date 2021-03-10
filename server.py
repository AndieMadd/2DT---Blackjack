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


# def handleClientIncoming(conn, addr):
#     global userList, msgList, ROOM_OPEN, room
#     if not ROOM_OPEN:
#         sendMsg(conn, "Room Closed")
#         conn.close()
#     connected = False
#     while not connected:
#         user_len = int(conn.recv(HEADER).decode('utf-8'))
#         user_name = conn.recv(user_len).decode('utf-8')
#         in_users = False
#         if len(userList):
#             if any([user[0] == user_name for user in userList]):
#                 sendMsg(conn, '0')
#                 in_users = True
#         if not in_users:
#             userList.append((user_name, conn))
#             sendMsg(conn, '1')
#             connected = True
#     while connected:
#         msg_len = int(conn.recv(HEADER).decode('utf-8'))
#         msg = conn.recv(msg_len).decode('utf-8')
#         if msg == DISCONNECT_MSG:
#             connected = False
#             msgList.append(("SERVER", f"{user_name} Disconnected"))
#             userList.pop(userList.index((user_name, conn)))
#         else:
#             msgList.append((user_name, msg))
#     conn.close()

def handleClientIncoming(conn, addr):
    global room
    user_len = conn.recv(HEADER).decode('utf-8')
    username = conn.recv(int(user_len)).decode('utf-8')
    if username in room:
        sendMsg(conn, '0')
    else:
        room.append(username)
        sendMsg(conn, '1')
    while True:
        msg_len = conn.recv(HEADER).decode('utf-8')
        msg = conn.recv(int(msg_len)).decode('utf-8')


def messagesOutgoing():
    global msgList, userList
    while True:
        if len(msgList):
            for msg in msgList:
                for user in userList:
                    sendMsg(user[1], msg)
            msgList.pop(0)


def sendMsg(conn, msg):
    message = json.dumps(msg).encode("utf-8")
    msg_len = len(message)
    send_len = str(msg_len).encode('utf-8')
    send_len += b' ' * (HEADER - len(send_len))
    conn.send(send_len)
    conn.send(message)


def start():
    server.listen()
    outGoingThread = threading.Thread(target=messagesOutgoing).start()
    while True:
        conn, addr = server.accept()
        incomingThread = threading.Thread(
            target=handleClientIncoming, args=(conn, addr)).start()


print(f"Starting server on {HOST}")

if __name__ == "__main__":
    start()
