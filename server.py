# ----- Imports
import socket
import threading
import json
import os
import random

os.system('title Server')
# ----- Initial Variables
HEADER = 64
HOST = socket.gethostbyname(socket.gethostname())
PORT = 5050
DISCONNECT_MSG = "!DC"
READY_MSG = "!READY"
ROOM_OPEN = True
ROOM = []  # holds clients

# ----- Initialises the Server
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))


class Client:
    # A Simple class to manage a Client
    def __init__(self, user_, conn_):
        self.username = user_
        self.conn = conn_
        self.score = 0
        self.active = 1
        self.wins = 0

    def send(self, msg):
        # Sends a message to the client
        # First calculates the message length
        message = json.dumps(msg).encode("utf-8")
        msg_len = len(message)
        send_len = str(msg_len).encode('utf-8')
        send_len += b' ' * (HEADER - len(send_len))
        # Sends the message length, then the message
        self.conn.send(send_len)
        self.conn.send(message)

    def recieve(self):
        # Recieves a message from the client
        # First recieves the message length, then the message itself
        msg = ""
        recv_len = self.conn.recv(HEADER).decode('utf-8')
        if recv_len:
            msg = self.conn.recv(int(recv_len)).decode('utf-8')
        return msg


def handleClientIncoming(conn, addr):
    # Function to handle a connection from a client
    global ROOM, ROOM_OPEN
    if not ROOM_OPEN:
        # If the room is already closed, the user cannot join and is kicked
        conn.close()
        return False
    # Recieves a username from the client
    user_len = conn.recv(HEADER).decode('utf-8')
    new_username = conn.recv(int(user_len)).decode('utf-8')
    while any([new_username == user.username for user in ROOM]):
        # if the username is already in the room, then the client has to send a new one
        sendMsg(conn, '0')
        user_len = conn.recv(HEADER).decode('utf-8')
        if user_len:
            new_username = conn.recv(int(user_len)).decode('utf-8')
    # Creates a new client object for the user, and adds it to the room.
    user = Client(new_username, conn)
    ROOM.append(user)
    user.send(len(ROOM))
    while ROOM_OPEN:
        # Waits for the first user to send the ready message
        if ROOM.index(user) == 0:
            user_ready = user.recieve()
            if user_ready == READY_MSG and ROOM_OPEN == True:
                # Closes the room, then sends the users a buffer message and the user list
                ROOM_OPEN = False
                sendAll('1')
                sendAll([user.username for user in ROOM])
    while not ROOM_OPEN:
        # Main Game Loop
        if not any([user.active == 1 for user in ROOM]):
            # if all the users are no longer active, then it checks the winner and sends it
            sendAll(checkWinner(ROOM))
            for other in ROOM:
                # sets all the scores back to 0, and the active back to 1
                other.score = 0
                other.active = 1
        else:
            # Recieves the user's intended action
            action = user.recieve().lower()
            if action in ['h', 'hit'] and user.active == 1:
                # if the user hits, and they are still active, then increase their score by a random int 1 - 11
                user.score += random.randint(1, 11)
                if user.score > 21:
                    # if the user goes over, then set their active status to 0
                    user.active = 0
            elif action in ['s', 'sit']:
                # else if the user sits, set their active status to 0
                user.active = 0
            # send all users a dict with the game state in it
            sendAll({user.username: [user.score, user.active, user.wins]
                     for user in ROOM})


def checkWinner(scoreDict):
    # A Function to check which user(s) won the last round
    # First takes all the users who's scores are not over 21
    potentialWinners = {
        user.username: user.score for user in ROOM if user.score <= 21}

    # If all the users went over 21, then all users tied
    if len(potentialWinners) == 0:
        # \033[043m is a code for a yellow highlight, \033[m clears the formatting for the next line
        return "\033[043mEverybody Went Over 21\033[m"

    # Gets the highest score amongst the potential winners
    winnerValue = max(potentialWinners.values())
    # All the users who's score is equal to the winner score, as there may be more than one
    winningUsers = [name for name,
                    score in potentialWinners.items() if score == winnerValue]

    # Increases the user's win count if they are a winner
    for client in ROOM:
        if client.username in winningUsers:
            client.wins += 1
            print(client.wins)

    winners = {user: winnerValue for user in winningUsers}
    if len(winningUsers) == 1:
        # if there is only one winner, returns this winner message
        return f"\033[42m{winningUsers[0]} won with {winnerValue} points.\033[m"
    else:
        # if there are multiple winners, returns a message listing all the winners
        return f"\033[42m{' and '.join(winningUsers)} all won with {winnerValue} points.\033[m"


def sendAll(msg):
    # A minor function to send a message to all clients at once
    global ROOM
    for user in ROOM:
        user.send(msg)


def start():
    # The server listens for an incoming connection
    server.listen()
    while True:
        # Accepts the connection, then starts a thread to handle that client
        conn, addr = server.accept()
        incomingThread = threading.Thread(
            target=handleClientIncoming, args=(conn, addr)).start()


print(f"Starting server on {HOST}")

if __name__ == "__main__":
    start()
