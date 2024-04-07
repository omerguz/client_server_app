import random
import socket
import struct
import threading
import time
import sys

ANSI_YELLOW = "\033[33m"
ANSI_RESET = "\033[0m"
ANSI_GREEN = "\033[32m"
ANSI_RED = "\033[31m"
ANSI_BLUE = "\033[34m"

BUFFER_SIZE = 1024

class Client:
    def __init__(self, index, debug_mode=False, bot_mode=False, bot_size=None):
        self.DEBUG_MODE = debug_mode
        self.BOT_MODE = bot_mode
        # Server configuration
        self.id = index
        self.SERVER_PORT = 13117
        self.BOT_SIZE = bot_size
        self.MAGIC_COOKIE = b'\xab\xcd\xdc\xba'
        self.MESSAGE_TYPE_OFFER = b'\x02'
        self.SERVER_PORT_TCP_INDEX = 36

    def print_with_color(self, message, color):
        print(color + message + ANSI_RESET)

    def recvData(self, socket):
        data = None
        if self.DEBUG_MODE:
            # Generate debug response when in debug mode
            data = "Choose to random question a random answer"
        else:
            try:
                data = socket.recv(BUFFER_SIZE).decode("utf-8")
                return data
            except Exception as e:
                self.print_with_color(f"Error receiving data from socket: {e}", ANSI_RED)
                return None

    # Wrapper function for sending data to the server
    def sendData(self,socket, data):
        if self.DEBUG_MODE:
            self.print_with_color(f"Send message : {data}", ANSI_GREEN)
        else:
            try:
                socket.send(data.encode("utf-8"))
            except Exception as e:
                self.print_with_color(f"Error sending data to socket: {e}", ANSI_RED)

    def udpRecvData(self, socket):
        data = None
        addr = None
        if self.DEBUG_MODE:
            # Generate debug response when in debug mode
            print("Update custom data")
            addr = ('192.168.56.1', 50677)
            data = b'\xba\xdc\xcd\xab\x02\x00\xd9\x07'
        else:
            data, addr = socket.recvfrom(BUFFER_SIZE)

        return data, addr

    # Function to handle receiving data from the server
    def receive_data_from_server(self, client_socket):
        while True:
            try:
                data = client_socket.recv(BUFFER_SIZE)
                if not data:
                    break
                self.print_with_color(data.decode("utf-8"), ANSI_BLUE)
            except Exception as e:
                self.print_with_color(f"Error receiving data from server: {e}", ANSI_RED)
                break

    def getServerConnection(self):
    # Create a UDP socket to listen for offer messages
        udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR , 1)
        udp_socket.bind(("", self.SERVER_PORT))

        msgAndAddr = None
        offerMsgArrived = False
        # Listen for offer messages
        while not offerMsgArrived:
            try:
                # data, addr = udp_socket.recvfrom(BUFFER_SIZE)
                data, addr = self.udpRecvData(udp_socket)
                string_length = len(data) - struct.calcsize("Ibh")

                # Create the unpacking format string
                unpack_format = f"Ibh{string_length}s"

                # Unpack the offerMessage
                msgUnPack = struct.unpack(unpack_format, data)
                # msgUnPack = struct.unpack("Ibh", data)
                cookie_int = int.from_bytes(self.MAGIC_COOKIE, byteorder='big')
                magicCookieValid = msgUnPack[0] == cookie_int
                msgTypeOfferValid = msgUnPack[1] == self.MESSAGE_TYPE_OFFER[0]
                if magicCookieValid and msgTypeOfferValid:
                    offerMsgArrived = True
                    msgAndAddr = msgUnPack[2], addr
                    server_info_string = msgUnPack[3].decode('utf-8')
                    self.print_with_color(f"Received offer from server \"{server_info_string}\" at address {addr[0]}, attempting to connect...",ANSI_YELLOW)
                
            except Exception as e:
                self.print_with_color(f"Error receiving offer message: {e}", ANSI_RED)

        return msgAndAddr   

    def run_client(self):
        # Listen for offer messages
        while True:
            self.print_with_color("Client started, listening for offer requests...", ANSI_GREEN)
            self.PLAYER_IS_ACTIVE = True
            server_port_tcp, server_addr = self.getServerConnection()
            self.user_name = None
            if not self.BOT_MODE:
                self.print_with_color("Hello client! Enter your name : ", ANSI_GREEN)
                self.user_name = input().strip()
            else:
                self.user_name = "BOT_" + f"{self.id}"
                self.print_with_color(f"I'm a BOT ! My name is : {self.user_name}\n", ANSI_GREEN)
            # Process offer message and extract server information
            if server_port_tcp:
                # Connect to the server over TCP
                client_tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                if(not self.DEBUG_MODE):
                    try:
                        client_tcp_socket.connect((server_addr[0], server_port_tcp))
                        self.print_with_color("Connected to the server over TCP.", ANSI_GREEN)
                    except Exception as e:
                        self.print_with_color(f"Error connecting to the server over TCP: {e}",ANSI_RED)

                # Send team name to the server
                self.sendData(client_tcp_socket, f"{self.user_name}")

                # Enter game mode
                self.handle_game_mode(client_tcp_socket)  

    def get_input_from_user(self):
        if self.BOT_MODE:
            if random.random() > 0.5:
                self.print_with_color(f"{self.user_name} Choose value Y\n",ANSI_GREEN)
                return "Y"
            else:
                print(f"{self.user_name} Choose value F\n", ANSI_GREEN)
                return "F"
        else:
            return input("Enter your answer (Y/T/1 for True or N/F/0 for False): ")      

    # Function to handle game mode
    def handle_game_mode(self, client_tcp_socket):
        try:
            # Receive and print trivia questions, and send answers
            while True:
                msg = self.recvData(client_tcp_socket)
                self.print_with_color(msg, ANSI_BLUE)
                if msg.startswith("Congratulations"):
                    break
                elif f"{self.user_name} is incorrect" in msg and " correct" in msg:
                    self.PLAYER_IS_ACTIVE = False 
                elif msg.startswith("Round"):
                    if(self.PLAYER_IS_ACTIVE):
                        attempts_left = 3
                        while attempts_left > 0:
                            user_input_answer = self.get_input_from_user()
                            answer = validAnswer(user_input_answer)
                            if answer is not None:
                                self.sendData(client_tcp_socket, answer)
                                break
                            else:
                                self.print_with_color("Invalid input, enter your answer again\n", ANSI_GREEN)
                                attempts_left -= 1
                                self.print_with_color(f"Attempts left: {attempts_left}\n", ANSI_GREEN)

        except Exception as e:
            self.print_with_color(f"Error in game mode: {e}", ANSI_RED)
        finally:
            client_tcp_socket.close()

def validAnswer(answer):
    true_values = {'Y', 'T', '1'}
    false_values = {'N', 'F', '0'}

    if answer.upper() in true_values:
        return "True"
    elif answer.upper() in false_values:
        return "False"
    else:
        return None  # Invalid answer

def extract_args():
    debug_mode = False
    bot_mode = False
    bot_size = 0

    args = sys.argv[1:]  # Exclude the script name itself

    # Check for -d flag
    if '-d' in args:
        debug_mode = True
        args.remove('-d')

    # Check for -b flag
    if '-b' in args:
        bot_mode = True
        args.remove('-b')
        # Check for -s flag and its argument
        if '-s' in args:
            index_s = args.index('-s')
            if index_s < len(args) - 1:
                bot_size_arg = args[index_s + 1]
                try:
                    bot_size = int(bot_size_arg)
                    args.remove('-s')
                    args.remove(bot_size_arg)
                except ValueError:
                    print("Error: Bot size must be an integer.")
                    sys.exit(1)

    return debug_mode, bot_mode, bot_size

if __name__ == "__main__":
    debug_mode, bot_mode, bot_size = extract_args()

    defaultIndex = 0
    # Create clients with different buffer sizes in separate threads
    if bot_size > 1:
        clients = []
        for i in range(bot_size):
            client = Client(i, debug_mode, bot_mode)
            clients.append(client)
            t = threading.Thread(target=client.run_client)
            t.start()
    else:
        client = Client(defaultIndex, debug_mode, bot_mode)
        client.run_client()
