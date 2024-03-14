import socket
import struct
import threading
import time
import concurrent
from concurrent.futures import thread
import random
import copy
from collections import namedtuple

# from termcolor import colored

# TODO : Use enum instead of self. ...
UDP_PORT = 13117
TCP_PORT = 12345  # Replace with any available port on your machine
BUFFER_SIZE = 1024
MAGIC_COOKIE = b'\xab\xcd\xdc\xba'
MESSAGE_TYPE_OFFER = b'\x02'
SERVER_NAME = "MillionDollarTRIVIA"
IP_ADDR = "172.4.0.1"
Player = namedtuple('Player', ['clientSocket', 'clientAddress', 'playerName'])
QUESTION = "question"
IS_TRUE = "is_true"
TRIVIA_QUESTIONS = [
    {"question": "Manchester United has won the UEFA Champions League 3 times.", "is_true": "True"},
    {"question": "Arsenal FC has never won the UEFA Champions League.", "is_true": "True"},
    {"question": "Liverpool FC has won the UEFA Champions League 6 times.", "is_true": "True"},
    {"question": "Tottenham Hotspur FC has never reached the UEFA Champions League final.", "is_true": "False"},
    {"question": "Chelsea FC has won the UEFA Champions League twice.", "is_true": "False"},
    {"question": "Manchester United has won the Premier League more times than any other club.", "is_true": "True"},
    {"question": "Arsenal FC's home ground is Emirates Stadium.", "is_true": "True"},
    {"question": "Liverpool FC's home ground is Anfield.", "is_true": "True"},
    {"question": "Tottenham Hotspur FC's home ground is White Hart Lane.", "is_true": "False"},
    {"question": "Chelsea FC's home ground is Stamford Bridge.", "is_true": "True"},
    {"question": "Manchester United has never been relegated from the Premier League.", "is_true": "True"},
    {"question": "Arsenal FC has finished in the top four of the Premier League more times than any other club.", "is_true": "True"},
    {"question": "Liverpool FC has won the FIFA Club World Cup twice.", "is_true": "False"},
    {"question": "Tottenham Hotspur FC has won the UEFA Cup Winners' Cup once.", "is_true": "True"},
    {"question": "Chelsea FC has won the UEFA Europa League twice.", "is_true": "True"},
    {"question": "Manchester United's record transfer fee paid is for Cristiano Ronaldo.", "is_true": "True"},
    {"question": "Arsenal FC's all-time top scorer is Thierry Henry.", "is_true": "True"},
    {"question": "Liverpool FC's nickname is the Reds.", "is_true": "True"},
    {"question": "Tottenham Hotspur FC has won the FA Cup 8 times.", "is_true": "False"},
    {"question": "Chelsea FC has won the FA Cup 8 times.", "is_true": "True"}
]



class Server:
    def __init__(self):
        # initialize UDP socket
        self.UDPSocket = socket.socket(
            socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        self.UDPSocket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        # initialize TCP socket
        self.TCPSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.hostName = socket.gethostname()
        self.hostIP = socket.gethostbyname(self.hostName)
        self.hostPort = 2009
        self.playersData = [] # Stores information about players (socket, address, name)
        self.solutionTuples = [] # Stores solutions submitted by players (solution, player_name)
        self.lock = threading.Lock() # Lock for thread safety
        self.udpflg = False # Flag for UDP broadcast
        self.udpBroadcastPort = 13117 # UDP broadcast port
        self.gemeEndTime = 10 # Game end time in seconds
        self.bufferSize = 1024 # Buffer size for socket communication

    def init_tcp_socket(self):
        con = False
        while not con:
            try:
                self.TCPSocket.bind(("", self.hostPort))
                con = True
            except:
                pass
        self.TCPSocket.listen()

    def send_message_to_clients(self, msg):
        """
        Send a message to all connected clients.
        If an exception occurs while sending the message to a client, remove that client from the list.
        """
        print(msg)
        updated_players_data = []
        for player_data in self.playersData:
            try:
                player_data.clientSocket.send(msg.encode("utf-8"))
                updated_players_data.append(player_data)
            except Exception as e:
                print(f"Error sending message to {player_data.playerName}: {e}. Removing from the list.")
        self.playersData = updated_players_data

    def brodcastUdpOffer(self):    
        while self.udpflg==False:
            SERVER_NAME_BYTES = SERVER_NAME.encode('utf-8')
            offerMessage = struct.pack(f"Ibh{len(SERVER_NAME_BYTES)}s", 0xabcddcba, 0x2, self.hostPort, SERVER_NAME_BYTES)

            # brodacast the message to all clients connected to the net
            self.UDPSocket.sendto(
            # offerMessage, (modified_ip, self.udpBroadcastPort))
            offerMessage, ('<broadcast>', self.udpBroadcastPort))
            time.sleep(0.5)


    def waitForClient(self):
        '''
        First stage of the server
        The server start brodcast offers to the clients in the network via UDP 
        while listning to join request from clients via TCP.
        this function update the self.team with the first two teams that request to join
        we leave this this stage when two clients joined the game.
        '''
        start_time = 0
        UdpBroadcastThread = threading.Thread(target=self.brodcastUdpOffer)
        UdpBroadcastThread.start()
        # TODO : Change timeouts
        # while (len(self.playersData) >= 1 and time.time() - start_time < 3) or len(self.playersData) < 1:
        while (len(self.playersData) >= 1 and time.time() - start_time < 10) or len(self.playersData) < 1:
            # self.TCPSocket.settimeout(0.5)
            self.TCPSocket.settimeout(10)
            try:
                clientSocket, clientAddress = self.TCPSocket.accept()
                playerName = clientSocket.recv(self.bufferSize).decode("utf-8")
                self.playersData.append(Player(clientSocket, clientAddress, playerName))
                if len(self.playersData) == 1:    # start the timer when the first client joins
                    start_time = time.time()
            except:
                continue
        self.udpflg = True
        
        

    def startGameMode(self, player, timer):
        start_time = time.time()
        while time.time() - start_time < 10:  # Ensure the loop runs for a maximum of 10 seconds
            try:
                # Set a timeout for the recv call
                player.clientSocket.settimeout(0.5)
                
                # Receive data from the player
                userSolution = player.clientSocket.recv(self.bufferSize).decode("utf-8")
                
                # Append the solution to the list of solution tuples
                with self.lock:
                    self.solutionTuples.append((userSolution, player.playerName))
                    break
            
            except socket.timeout:
                # Handle timeout exception (no data received within the timeout period)
                pass
            except Exception as e:
                # Handle other exceptions
                print(f"Error in startGameMode: {e}")
                break
 
    def getPlayersNames(self):
        """
        Retrieve the names of the players from the server's teams.
        """
        player_names = ""
        for i, playerData in enumerate(self.playersData):
            player_names += f"Player Number {i}: {playerData.playerName}\n"
        # Remove the trailing comma and space
        return player_names

    def get_currect_players(self):
        current_players = []
        for player_tuple in self.playersData:
            current_player = (Player(
                player_tuple.clientSocket,  # Deep copy socket object
                player_tuple.clientAddress,  # Deep copy client address
                player_tuple.playerName  # Player name (no need to copy)
            ))
            current_players.append(current_player)
        return current_players

    def run_trivia_game(self):
        while True:
            self.playersData = []
            self.solutionTuples = []
            self.udpflg = False
            userIncides = []
            # Print start message
            print(f"Server started, listening on IP address {self.hostIP}")
            # Start wait for clients stage
            try:
                self.waitForClient()

                if len(self.playersData) == 0:
                    continue

                welcomeMsg = f"Welcome to the {SERVER_NAME} server, where we are answering trivia questions about English Premier League.\n{self.getPlayersNames()}"
                self.send_message_to_clients(welcomeMsg)
                
                counter = 0
                pool =  concurrent.futures.ThreadPoolExecutor(len(self.playersData))

                current_players = self.get_currect_players()

                while len(current_players) >= 1:
                    timer = time.time() #round is only 10 seconds
                    problem = get_random_question(userIncides)
                    solution = problem[IS_TRUE]
                    counter += 1
                    
                    msg = f"Round {counter}, played by " + format_names([playerData.playerName for playerData in current_players]) + f"\n==\nTrue or false : {problem[QUESTION]}\n"
                    self.send_message_to_clients(msg)
                    msg = ""

                    with self.lock:
                        self.solutionTuples.clear()
                    for playerData in self.playersData:
                        pool.submit(self.startGameMode, playerData, timer)
                    
                    start_time = time.time()
                    while time.time() - start_time < 10:
                        with self.lock:
                            if(len(self.solutionTuples) == len(self.playersData)):
                                break
                        time.sleep(0.5)  # Sleep for 0.5 second before rechecking
                    
                    with self.lock:
                        for i, s in enumerate(self.solutionTuples):
                            # remove the client from the game if it didn't answer in time\correctly
                            print(f"Server got answer : {s[0]}\n")
                            if(s[0] == solution):
                                msg += f"{s[1]} is correct!\n"
                            else:
                                msg += f"{s[1]} is incorrect!\n"
                    
                    #report of all incorrect\correct players
                    self.send_message_to_clients(msg)
                    #remove all unanswered and wring clients. do nothing if none of the clients were rihgt
                    current_players = remove_wrong_answer_players(current_players, self.solutionTuples, solution)
                    
                    msg = "Congratulations to the winner: "    
                    if(len(current_players) == 1):
                            msg += f"{current_players[0].playerName}"
                            self.send_message_to_clients(msg)
                            msg = "Game over, sending out offer requests..." 
                            print(msg)
                            break
                
                for playerData in self.playersData:
                    try:
                        playerData.clientSocket.close()
                    except:
                        continue
            except Exception as e:
                print(f"Error : {e}\n Starting game again..\n")
 


def remove_wrong_answer_players(current_players, solutionTuples, correct_answer):
    # Get the names of players who gave the wrong answer    
    wrong_answer_players = {player_name for solution, player_name in solutionTuples if solution != correct_answer}
    not_answered_players = {player_name for _, _, player_name in current_players if player_name not in [player_name for _, player_name in solutionTuples]}
    wrong_unanswered_players = wrong_answer_players.union(not_answered_players)
    
    all_player_names = [player_name for _, _, player_name in current_players]
    all_exist = all(player_name in wrong_answer_players for player_name in all_player_names)
    updated_current_players = current_players
    if not all_exist:
    # Filter out the players who gave the wrong answer
        updated_current_players = [Player(client_socket, client_address, player_name) for client_socket, client_address, player_name in current_players if player_name not in wrong_unanswered_players]
    
    return updated_current_players

def get_random_question(used_indices):
    if len(used_indices) == len(TRIVIA_QUESTIONS):
            print("No more questions left, start again...")
            used_indices.clear()
    while True:
        question_index = random.randint(0, len(TRIVIA_QUESTIONS) - 1)
        if question_index not in used_indices:
            used_indices.append(question_index)
            return TRIVIA_QUESTIONS[question_index]

def format_names(names):
    if not names:
        return ""
    elif len(names) == 1:
        return names[0]
    else:
        return ", ".join(names[:-1]) + ", and " + names[-1]

def test_trivia():
    userIncides = []
    while True:
        problem = get_random_question(userIncides)
        print(userIncides)
        solution = problem[IS_TRUE]

# Game Flow
if __name__ == '__main__':
    server = Server()
    server.init_tcp_socket()
    server.run_trivia_game()

