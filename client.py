import socket
import threading
import os
import json
import keyboard

os.system('title Client')

HEADER = 64
HOST = '10.70.5.28'
PORT = 5050
DISCONNECT_MSG = "!DC"
READY_MSG = "!READY"
MSG_MAX = 20
USER_NAME = ""
USER_LIST = []
active = 1

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

client.connect((HOST, PORT))

addr = []
connected = False
messages = []
prev_winner = ""

# -----TIMELINE
# Client Connects
# Username resolution
# Enters Room (Server Side)
# Recieve Room List
# Closes Room, Starts Game

# ----- Game Timeline
# Deals 2 Cards To Each Player + Dealer
# Each Player Sees Their Card and Dealer's Cards
# Players Can Hit (draw) or Sit (pass) at any time
# If a player goes over 21 in value, they Bust (lose)
# Once all players finish, everybody sees all other hands and a winner is decleared
# Players are prompted to play again


def send(msg):
    global connected
    message = msg.encode("utf-8")
    msg_len = len(message)
    send_len = str(msg_len).encode('utf-8')
    send_len += b' ' * (HEADER - len(send_len))
    client.send(send_len)
    client.send(message)
    if msg == DISCONNECT_MSG:
        connected = False


def recieve():
    global connected, messages, USER_LIST, active, prev_winner
    while connected:
        try:
            recv_len = client.recv(HEADER).decode('utf-8')
            newMsg = json.loads(client.recv(int(recv_len)).decode('utf-8'))
            if type(newMsg) == list:
                USER_LIST = newMsg
                messages.append('')
            elif type(newMsg) == dict:
                messages = []
                for user in newMsg:
                    if newMsg[user][1]:
                        messages.append(
                            f'{user} is at {newMsg[user][0]} points.')
                    else:
                        messages.append(
                            f'{user} is sitting at {newMsg[user][0]}')
                if newMsg[USER_NAME][1]:
                    messages.append('\nWould you like to Hit (h) or Sit (s) ?')
                else:
                    messages.append(
                        '\nPlease wait until all users have finished')
                    active = 0
            elif type(newMsg) == bool:
                active = 1
                messages.append('')
            else:
                messages.append(newMsg)
                prev_winner = newMsg
        except:
            pass


def show():
    global messages, connected, USER_NAME, prev_winner
    printedMessages = []
    while connected:
        if messages != printedMessages:
            os.system('cls')
            printedMessages = []
            print("USERS: ", end='')
            for user in USER_LIST:
                print(f"[{user}]", end=' ')
            print()
            print(prev_winner)
            print('-' * 20)
            for message in messages:
                print(message)
                printedMessages.append(message)


def start():
    global connected, USER_NAME
    while not connected:
        username = input("What Is Your Username: ")
        send(username)
        status_len = client.recv(HEADER).decode('utf-8')
        status = int(json.loads(client.recv(int(status_len)).decode('utf-8')))
        if status != 0:
            USER_NAME = username
            connected = True
    if status == 1:
        input("Press Enter When All Clients Are Ready. ")
        send(READY_MSG)
        status_len = client.recv(HEADER).decode('utf-8')
        status = json.loads(client.recv(int(status_len)).decode('utf-8'))
    else:
        print("Please Wait Until ALl Clients Are Ready.")
        status_len = client.recv(HEADER).decode('utf-8')
        status = json.loads(client.recv(int(status_len)).decode('utf-8'))
    incomingThread.start()
    printThread.start()
    while True:
        if active:
            send(input())


outgoingThread = threading.Thread(target=start).start()
incomingThread = threading.Thread(target=recieve)
printThread = threading.Thread(target=show)
