import socket
import threading
import json
import os
import random

os.system('title Server')

HEADER = 64
HOST = socket.gethostbyname(socket.gethostname())
PORT = 5050
DISCONNECT_MSG = "!DC"
READY_MSG = "!READY"
ROOM_OPEN = True

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))

msgList = []  # (conn, message)
room = []  # [username, conn]
scores = {}
#connected = False


def handleClientIncoming(conn, addr):
    global room, ROOM_OPEN, scores, prev_winner
    if not ROOM_OPEN:
        conn.close()
        return 0
    user_len = conn.recv(HEADER).decode('utf-8')
    username = conn.recv(int(user_len)).decode('utf-8')
    while any([username in user for user in room]):
        sendMsg(conn, '0')
        try:
            user_len = conn.recv(HEADER).decode('utf-8')
            username = conn.recv(int(user_len)).decode('utf-8')
        except:
            pass
    else:
        user = [username, conn]
        room.append(user)
        sendMsg(conn, len(room))
    while ROOM_OPEN:
        if room.index(user) == 0:
            msg_len = conn.recv(HEADER).decode('utf-8')
            if msg_len:
                msg = conn.recv(int(msg_len)).decode('utf-8')
                if msg == READY_MSG and ROOM_OPEN == True:
                    ROOM_OPEN = False
                    users = [user[0] for user in room]
                    sendAll('1')
                    sendAll(users)
                    scores = {user: [0, 1] for user in users}
                    sendAll(scores)
                    print(scores)
    while not ROOM_OPEN:
        if not any([scores[user][1] == 1 for user in scores]):
            print('all have finished')
            sendAll(checkWinner(scores))
            scores = {user: [0, 1] for user in scores}
            sendAll(True)
            sendAll(scores)
        msg_len = conn.recv(HEADER).decode('utf-8')
        if msg_len:
            msg = conn.recv(int(msg_len)).decode('utf-8')
            if msg.lower() in ['h', 'hit']:
                scores[username][0] += random.randint(1, 11)
                if scores[username][0] > 21:
                    scores[username][1] = 0
            elif msg.lower() in ['s', 'sit']:
                scores[username][1] = 0
            sendAll(scores)


def checkWinner(scoreDict):
    potentialWinners = {
        user: scoreDict[user][0] for user in scoreDict if scoreDict[user][0] <= 21}
    if len(potentialWinners) == 0:
        return 0
    winnerValue = max(potentialWinners.values())
    winningUsers = [k for k, v in potentialWinners.items() if v == winnerValue]
    winners = {user: winnerValue for user in winningUsers}
    if len(winningUsers) == 1:
        return f"{winningUsers[0]} won with {winnerValue} points."
    else:
        return f"{[user for user in winningUsers]} all won with {winnerValue} points."


def sendMsg(conn, msg):
    message = json.dumps(msg).encode("utf-8")
    msg_len = len(message)
    send_len = str(msg_len).encode('utf-8')
    send_len += b' ' * (HEADER - len(send_len))
    conn.send(send_len)
    conn.send(message)


def sendAll(msg):
    global room
    for user in room:
        sendMsg(user[1], msg)


def start():
    server.listen()
    while True:
        conn, addr = server.accept()
        incomingThread = threading.Thread(
            target=handleClientIncoming, args=(conn, addr)).start()


print(f"Starting server on {HOST}")

if __name__ == "__main__":
    start()
