import socket
import threading
import time

# Server configuration
SERVER_PORT = 13117
BUFFER_SIZE = 1024
IP_ADDRESS = "172.1.0.4"
MAGIC_COOKIE = b'\xab\xcd\xdc\xba'
MESSAGE_TYPE_OFFER = b'\x02'
SERVER_PORT_TCP_INDEX = 36

# Function to handle receiving data from the server
def receive_data_from_server(client_socket):
    while True:
        try:
            data = client_socket.recv(BUFFER_SIZE)
            if not data:
                break
            print(data.decode())
        except Exception as e:
            print(f"Error receiving data from server: {e}")
            break

def getServerConnection():
# Create a UDP socket to listen for offer messages
    # TODO : check if ok
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR , 1)
    udp_socket.bind(("", SERVER_PORT))
    # udp_socket.bind((IP_ADDRESS, SERVER_PORT))

    msgAndAddr = None
    offerMsgArrived = False
    # Listen for offer messages
    while not offerMsgArrived:
        try:
            data, addr = udp_socket.recvfrom(BUFFER_SIZE)
            msgAndAddr = data, addr
            if len(data) >= 37 and data[:4] == MAGIC_COOKIE and data[4] == MESSAGE_TYPE_OFFER:
                offerMsgArrived = True

        except Exception as e:
            print(f"Error receiving offer message: {e}")

    return msgAndAddr
        

def run_client():
    print("Client started, listening for offer requests...")
    clientBot = False
    # Listen for offer messages
    while True:
        print("Hello client! Enter your name : ")
        # TODO : implement the name from terminal
        USER_NAME = None
        if clientBot:
            USER_NAME = "Liran"
        else:
            #TODO : implement..
            USER_NAME = "BOT"

        data, server_addr = getServerConnection()
        # Process offer message and extract server information
        if data:
            server_port_tcp = int.from_bytes(data[SERVER_PORT_TCP_INDEX:SERVER_PORT_TCP_INDEX+2], byteorder='big')
            # Connect to the server over TCP
            client_tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_tcp_socket.connect((server_addr[0], server_port_tcp))
            print("Connected to the server over TCP.")

            # Send team name to the server
            client_tcp_socket.send(f"{USER_NAME}\n".encode())

            # Enter game mode
            threading.Thread(target=handle_game_mode, args=(client_tcp_socket,)).start()

# Function to handle game mode
def handle_game_mode(client_tcp_socket):
    try:
        # Receive welcome message from the server
        welcome_message = client_tcp_socket.recv(BUFFER_SIZE).decode()
        print(welcome_message)
        # Receive and print trivia questions, and send answers
        while True:
            question = client_tcp_socket.recv(BUFFER_SIZE).decode()
            print(question)
            answer = input("Enter your answer (Y/N): ")
            client_tcp_socket.send(answer.upper().encode())
    except Exception as e:
        print(f"Error in game mode: {e}")
    finally:
        client_tcp_socket.close()

if __name__ == "__main__":
    run_client()
