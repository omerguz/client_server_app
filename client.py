import socket
import struct
import threading
import time

# Server configuration
SERVER_PORT = 13117
BUFFER_SIZE = 1024
IP_ADDRESS = "172.1.0.4"
MAGIC_COOKIE = b'\xab\xcd\xdc\xba'
MESSAGE_TYPE_OFFER = b'\x02'
SERVER_PORT_TCP_INDEX = 36
DEBUG_MODE = False

def recvData(socket):
    data = None
    if DEBUG_MODE:
        # Generate debug response when in debug mode
        # Your debug response logic here
        data = "WELCOME DEBUG!"
    else:
        data = socket.recv(BUFFER_SIZE).decode("utf-8")
    return data

# Wrapper function for sending data to the server
def sendData(socket, data):
    if DEBUG_MODE:
        # Handle debug mode logic when sending
        # Your debug mode logic here
        print("Send message : ",data)
    else:
        socket.send(data.encode("utf-8"))

def udpRecvData(socket):
    data = None
    addr = None
    if DEBUG_MODE:
        # Generate debug response when in debug mode
        # Your debug response logic here
        addr = ('192.168.56.1', 50677)
        data = b'\xba\xdc\xcd\xab\x02\x00\xd9\x07'
    else:
        data, addr = socket.recvfrom(BUFFER_SIZE)

    return data, addr

# Function to handle receiving data from the server
def receive_data_from_server(client_socket):
    while True:
        try:
            data = client_socket.recv(BUFFER_SIZE)
            if not data:
                break
            print(data.decode("utf-8"))
        except Exception as e:
            print(f"Error receiving data from server: {e}")
            break

def getServerConnection():
# Create a UDP socket to listen for offer messages
    # TODO : check if ok
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR , 1)
    udp_socket.bind(('172.1.255.255', SERVER_PORT))

    msgAndAddr = None
    offerMsgArrived = False
    # Listen for offer messages
    while not offerMsgArrived:
        try:
            # data, addr = udp_socket.recvfrom(BUFFER_SIZE)
            data, addr = udpRecvData(udp_socket)
            msgUnPack = struct.unpack("Ibh", data)
            cookie_int = int.from_bytes(MAGIC_COOKIE, byteorder='big')
            magicCookieValid = msgUnPack[0] == cookie_int
            msgTypeOfferValid = msgUnPack[1] == MESSAGE_TYPE_OFFER[0]
            if magicCookieValid and msgTypeOfferValid:
                offerMsgArrived = True
                msgAndAddr = msgUnPack[2], addr

        except Exception as e:
            print(f"Error receiving offer message: {e}")

    return msgAndAddr
        

def run_client():
    clientBot = False
    # Listen for offer messages
    while True:
        print("Client started, listening for offer requests...")
        server_port_tcp, server_addr = getServerConnection()
        # TODO : implement the name from terminal
        USER_NAME = None
        if not clientBot:
            print("Hello client! Enter your name : ")
            USER_NAME = "Liran2"
        else:
            #TODO : implement..
            USER_NAME = "BOT"
        # Process offer message and extract server information
        if server_port_tcp:
            # Connect to the server over TCP
            client_tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            if(not DEBUG_MODE):
                client_tcp_socket.connect((server_addr[0], server_port_tcp))

            print("Connected to the server over TCP.")

            # Send team name to the server
            sendData(client_tcp_socket, f"{USER_NAME}\n")

            # Enter game mode
            handle_game_mode(client_tcp_socket)

def validAnswer(answer):
    true_values = {'Y', 'T', '1'}
    false_values = {'N', 'F', '0'}

    if answer.upper() in true_values:
        return "True"
    elif answer.upper() in false_values:
        return "False"
    else:
        return None  # Invalid answer
    

# Function to handle game mode
def handle_game_mode(client_tcp_socket):
    try:
        # Receive welcome message from the server
        welcome_message = recvData(client_tcp_socket)
        print(welcome_message)
        # Receive and print trivia questions, and send answers
        while True:
            question = recvData(client_tcp_socket)
            print(question)
            user_input_aswer = input("Enter your answer (Y/T/1 for True or N/F/0 for False): ")
            answer = validAnswer(user_input_aswer)
            if answer is not None:
                sendData(client_tcp_socket, answer)
            else:
                print("Invalid input")
    except Exception as e:
        print(f"Error in game mode: {e}")
    finally:
        client_tcp_socket.close()

if __name__ == "__main__":
    run_client()
