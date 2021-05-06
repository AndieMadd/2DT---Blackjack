#---------- Imports
import socket
import threading
import os
import json

# ---------- Initial Variables
HEADER = 64
HOST = '192.168.86.29'
PORT = 5050
READY_MSG = "!READY"
USER_NAME = ""
USER_LIST = []
ACTIVE = True
DISPLAY_LIST = []
CONNECTED = False
WINNER_STATUS = ""

# ---------- Connects to Server
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((HOST, PORT))


def send(msg):
    # ----- Minor Function to send messages to the server
    # Calculates the message length
    message = msg.encode("utf-8")
    msg_len = len(message)
    send_len = str(msg_len).encode('utf-8')
    send_len += b' ' * (HEADER - len(send_len))
    # Sends the message length, then the message
    client.send(send_len)
    client.send(message)


def recieveMsg():
    # ----- Minor Function to receive messages from server
    # First recieves how long the message will be, then recieves the message itself
    recv_len = client.recv(HEADER).decode('utf-8')
    if recv_len:
        data = json.loads(client.recv(int(recv_len)).decode('utf-8'))
    return data


def gameState():
    # ----- The Main Function, runs the core game loop
    global CONNECTED, DISPLAY_LIST, USER_LIST, ACTIVE, WINNER_STATUS

    # Recieves a list of usernames, and generates a list of users
    # Then for each user, it adds the the display queue a string saying they are at 0 points
    # This runs on the first round, so users have no score to calculate
    USER_LIST = [[user, 0] for user in list(recieveMsg())]
    for user in USER_LIST:
        DISPLAY_LIST.append(f"{user[0]} is at 0 points")
    # Starts the thread to manage display
    PrintThread.start()
    while CONNECTED:
        # Recieves information from the server
        msg = recieveMsg()
        # If the information is a string, it must be the winner's status
        if type(msg) == str:
            WINNER_STATUS = msg
            # Updates how many wins each user has, and sets their activity status back to true
            USER_LIST = [
                [user[0], user[1]+(1 if user[0] in msg else 0)] for user in USER_LIST]
            ACTIVE = True
            # Clears the display queue, and then adds a string for each user, putting their score to 0
            DISPLAY_LIST = []
            for user in USER_LIST:
                DISPLAY_LIST.append(f"{user[0]} is at 0 points")
        # If the information is a dict, then it is a game state
        elif type(msg) == dict:
            # Clears the display queue
            DISPLAY_LIST = []
            # Sets the active status equal to the user's active status on the server
            ACTIVE = msg[USER_NAME][1]
            # Makes sure the user list is up to date
            USER_LIST = [[user[0], msg[user[0]][2]] for user in USER_LIST]
            # Adds a string to the display queue for each user
            for user in USER_LIST:
                name = user[0]
                if msg[name][1] == 1:
                    # if the user is still playing, add the intial string with their score
                    DISPLAY_LIST.append(
                        f"{name} is at {msg[name][0]} points")
                else:
                    # else add the alternitive string stating the score they are sitting on
                    DISPLAY_LIST.append(
                        f"{name} is sitting at {msg[name][0]} points")


def show():
    # ----- Function that manages the console screen
    global DISPLAY_LIST, CONNECTED, USER_NAME, WINNER_STATUS
    printedMessages = []
    while CONNECTED:
        if DISPLAY_LIST != printedMessages:
            # if the display queue has been updated, then clear the screen
            os.system('cls')
            printedMessages = []
            # Prints the header with each user and their win count
            print("USERS: ", end='')
            for user in USER_LIST:
                print(f"{user[0]} ({user[1]})", end=' ')
            print()
            # Prints the string showing the last winner(s)
            print(WINNER_STATUS)
            print('-' * 20)
            # Prints the messages in the display queue and adds them to the printed messages
            for message in DISPLAY_LIST:
                print(message)
                printedMessages.append(message)


def start():
    # ----- Function that runs before the game loop, handles connection and user creation
    global CONNECTED, USER_NAME, ACTIVE

    while not CONNECTED:
        # Asks the user for a username, and sends it to the server
        username = input("What Is Your Username: ")
        send(username)
        user_index = int(recieveMsg())
        if user_index == 0:
            # If the username is already taken, the user will need to choose a new one
            print("That username is already taken")

        # If the username isn't already taken, then it is accepted and the user connects
        USER_NAME = username
        os.system(f"title Blackjack - {USER_NAME}")
        CONNECTED = True

    if user_index == 1:
        # if the user is the first to connect, then they are prompted to send the signal that all users are ready
        input("Press Enter When All Clients Are Ready. ")
        send(READY_MSG)
        # This line waits until the server is ready
        recieveMsg()
    else:
        # If the user isn't the first to connect, they are prompted to wait
        print("Please Wait Until ALl Clients Are Ready.")
        # This line waits until the server is ready
        recieveMsg()
    # Starts the game loop
    GameThread.start()

    while True:
        # Takes the user's input, and sends it to the server as long as they are still active
        if ACTIVE:
            msg = input()
            # If the user sits, then they are no longer active
            if msg.lower() in ['s', 'sit']:
                ACTIVE = False
                send(msg)
                continue
            send(msg)


# ---- Sets up the different threads, and starts the first one
InitalThread = threading.Thread(target=start).start()
GameThread = threading.Thread(target=gameState)
PrintThread = threading.Thread(target=show)
