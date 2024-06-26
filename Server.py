import socket
import struct
import threading
import time
import concurrent
from concurrent.futures import thread
import random
from collections import namedtuple
import socket

ANSI_YELLOW = "\033[33m"
ANSI_RESET = "\033[0m" 
ANSI_GREEN = "\033[32m"
ANSI_RED = "\033[31m"
ANSI_BLUE = "\033[34m"

GAME_TIME_SEC = 10
UDP_PORT = 13117
TCP_PORT = 9999
BUFFER_SIZE = 1024
MAGIC_COOKIE = b'\xab\xcd\xdc\xba'
MESSAGE_TYPE_OFFER = b'\x02'
SERVER_NAME = "MillionDollarTRIVIA"
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


def print_with_color(message, color):
        print(color + message + ANSI_RESET)

class Server:
    def __init__(self):
        # initialize UDP socket
        self.udpBroadcastPort = UDP_PORT # UDP broadcast port
        self.UDPSocket = socket.socket(
            socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        self.UDPSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.UDPSocket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        self.UDPSocket.bind(('', self.udpBroadcastPort))
        # initialize TCP socket
        self.TCPSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.hostName = socket.gethostname()
        self.hostIP = socket.gethostbyname(self.hostName)
        self.playersData = [] # Stores information about players (socket, address, name)
        self.current_players = []
        self.solutionTuples = [] # Stores solutions submitted by players (solution, player_name)
        self.solutionTupleLock = threading.Lock() # Lock for thread safety
        self.playerDataLock = threading.Lock() # Lock for thread safety
        self.udpflg = False # Flag for UDP broadcast
        self.playersAnswersAmount = {}

            
    def init_tcp_socket(self):
        con = False
        while not con:
            try:
                self.TCPSocket.bind(("", TCP_PORT))
                con = True
            except:
                pass
        self.TCPSocket.listen()

    def send_message_to_clients(self, msg):
        """
        Send a message to all connected clients.
        If an exception occurs while sending the message to a client, remove that client from the list.
        """
        print_with_color(msg, ANSI_GREEN)
        updated_players_data = []
        for player_data in self.playersData:
            try:
                player_data.clientSocket.send(msg.encode("utf-8"))
                updated_players_data.append(player_data) #append each player that received the welcome message, to the player array.
            except Exception as e:
                print_with_color(f"Error sending message to {player_data.playerName}: {e}. Removing from the list.", ANSI_RED)
        self.playersData = updated_players_data
       
    def brodcastUdpOffer(self):    
        while self.udpflg==False:
            SERVER_NAME_BYTES = SERVER_NAME.encode('utf-8')
            offerMessage = struct.pack(f"Ibh{len(SERVER_NAME_BYTES)}s", 0xabcddcba, 0x2, TCP_PORT, SERVER_NAME_BYTES)
            broadcast_address = get_wifi_ip_and_broadcast() #get the broadcast address of the current computer network

            self.UDPSocket.sendto(offerMessage, (broadcast_address, self.udpBroadcastPort))

            time.sleep(0.5)


    def waitForClient(self):
        start_time = 0
        UdpBroadcastThread = threading.Thread(target=self.brodcastUdpOffer)
        UdpBroadcastThread.start()

        while (len(self.playersData) >= 1 and time.time() - start_time < GAME_TIME_SEC) or len(self.playersData) < 1:
            self.TCPSocket.settimeout(GAME_TIME_SEC)
            try:
                clientSocket, clientAddress = self.TCPSocket.accept()
                playerName = clientSocket.recv(BUFFER_SIZE).decode("utf-8")
                self.playersData.append(Player(clientSocket, clientAddress, playerName))
                if len(self.playersData) == 1:    # start the timer when the first client joins
                    start_time = time.time()
            except socket.timeout:
                # Timeout occurred, do nothing and continue
                pass
            except Exception as e:
                    print_with_color(f"Error at open a TCP socket for a: {e}",ANSI_RED)
                    if not clientSocket.close:
                        clientSocket.close()  # Close the socket if it's open
                    continue
        self.udpflg = True
        
    def removePlayerFromGame(self,player: Player):
        try:
            player.clientSocket.close()
        except Exception as e:
            print_with_color("Client socket already closed\n")
            # Remove the player from playerData
            self.playersData = [p for p in self.playersData if p.playerName != player.playerName]
        
            # Remove the player from current_players
            self.current_players = [p for p in self.current_players  if p.playerName != player.playerName]    

    def startGame(self, player:Player, timer):
        start_time = time.time()
        while time.time() - start_time < GAME_TIME_SEC:  # Ensure the loop runs for a maximum of GAME_TIME_SEC seconds
            try:
                # Set a timeout for the recv call
                player.clientSocket.settimeout(0.5)
                
                # Receive data from the player
                userSolution = player.clientSocket.recv(BUFFER_SIZE).decode("utf-8")
                
                # Append the solution to the list of solution tuples
                with self.solutionTupleLock:
                    self.solutionTuples.append((userSolution, player.playerName))
                    break
            
            except socket.timeout:
                # Handle timeout exception (no data received within the timeout period)
                pass
            except Exception as e:
                # Handle other exceptions
                with self.playerDataLock:
                    self.removePlayerFromGame(player)
                    print_with_color(f"The user {player.playerName} was disconnected.", ANSI_RED)
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

    def get_current_players(self):
        self.current_players = []
        for player_tuple in self.playersData:
            current_player = (Player(
                player_tuple.clientSocket,  # Deep copy socket object
                player_tuple.clientAddress,  # Deep copy client address
                player_tuple.playerName  # Player name (no need to copy)
            ))
            self.current_players.append(current_player)

    def getPlayersAnswerMsg(self):
        players_answers_msg = "The number of correct answers for each player is:\n"
        sorted_players_answers = dict(sorted(self.playersAnswersAmount.items(), key=lambda x: x[1], reverse=True))

        # Iterate over each player and accumulate their message
        for player_name, answer_count in sorted_players_answers.items():
            players_answers_msg += f"{player_name}: {answer_count}\n"
        
        return players_answers_msg
    
    def run_trivia_game(self):
        while True:
            self.playersData = []
            self.solutionTuples = []
            self.udpflg = False
            userIncides = []
            print_with_color(f"Server started, listening on IP address {self.hostIP}", ANSI_YELLOW)
            try:
                self.waitForClient() #wait until 2 players or more joined the game, or timeout ocurred

                if len(self.playersData) == 0:
                    continue

                welcomeMsg = f"Welcome to the {SERVER_NAME} server, where we are answering trivia questions about English Premier League.\n{self.getPlayersNames()}"
                self.send_message_to_clients(welcomeMsg)
                
                counter = 0
                
                pool = concurrent.futures.ThreadPoolExecutor(len(self.playersData))

                self.get_current_players() # initiate the current player array, at first to the player_data array

                while len(self.current_players) >= 1:
                    timer = time.time() #round is only GAME_TIME_SEC seconds
                    problem = get_random_question(userIncides)
                    solution = problem[IS_TRUE]
                    counter += 1
                    
                    msg = f"Round {counter}, played by " + format_names([playerData.playerName for playerData in self.current_players]) + f"\n==\nTrue or false : {problem[QUESTION]}\n"
                    self.send_message_to_clients(msg)
                    msg = ""

                    with self.solutionTupleLock:
                        self.solutionTuples.clear()
                    for playerData in self.current_players:
                        pool.submit(self.startGame, playerData, timer)
                    
                    start_time = time.time()
                    while time.time() - start_time < GAME_TIME_SEC:
                        with self.solutionTupleLock: #lock the solution array, to prevent collisions
                            if(len(self.solutionTuples) == len(self.current_players)):
                                break
                        time.sleep(0.5)  # Sleep for 0.5 second before rechecking
                    
                    with self.solutionTupleLock:
                        for i, s in enumerate(self.solutionTuples):
                            # remove the client from the game if it didn't answer in time\correctly
                            print_with_color(f"Server got answer : {s[0]}\n", ANSI_BLUE)
                            value = self.playersAnswersAmount.get(s[1], 0)
                            if value == 0:
                                self.playersAnswersAmount[s[1]] = 0
                            if(s[0] == solution):
                                msg += f"{s[1]} is correct!\n"
                                self.playersAnswersAmount[s[1]] = value + 1
                            else:
                                msg += f"{s[1]} is incorrect!\n"
                        
                    
                    #report of all incorrect\correct players
                    self.send_message_to_clients(msg)
                    #remove all unanswered and wring clients. do nothing if none of the clients were rihgt
                    self.current_players = remove_wrong_answer_players(self.current_players, self.solutionTuples, solution)

                    if(len(self.current_players) == 1) or len(self.solutionTuples) == 1:
                            winner_name = None
                            if(len(self.current_players) == 1):
                                winner_name = self.current_players[0].playerName
                            else:
                                winner_name = self.solutionTuples[0][1]
                            msg = "Congratulations to the winner: "
                            msg += f"{winner_name}\n"
                            msg += "Here some statistics about this game:\n"
                            msg += self.get_longest_player_name()
                            msg += self.getPlayersAnswerMsg()
                            self.send_message_to_clients(msg)
                            self.playersAnswersAmount = {}
                            msg = "Game over, sending out offer requests..." 
                            print_with_color(msg, ANSI_YELLOW)
                            break
                
                pool.shutdown(wait = False)
                
                # with self.playerDataLock(self.playersData):
                for playerData in self.playersData:
                    try:
                        if not playerData.clientSocket._closed:
                            playerData.clientSocket.close()
                    except:
                        continue

            except Exception as e:
                print_with_color(f"Error : {e}\n Starting game again..\n", ANSI_RED) 

    def get_longest_player_name(self):
        longest_names = []  # Initialize with an empty list
        max_length = 0  # Initialize max_length to track the length of the longest name

        for player in self.playersData:
            # Check if the length of the player's name is longer than the current longest length
            if len(player.playerName) > max_length:
                max_length = len(player.playerName)
                longest_names = [player.playerName]  # Reset the list with the new longest name
            elif len(player.playerName) == max_length:
                longest_names.append(player.playerName)  # Add to the list if name length is same as longest
            longest_names_str = ""
            for name in longest_names:
                longest_names_str += f"{name}, "
            longest_names_str = longest_names_str[:-2]  # Remove the trailing comma and space
        return f"The player(s) with the longest name(s) are: {longest_names_str}\n"    
        
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
            print_with_color("No more questions left, start again...", ANSI_YELLOW)
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
        print_with_color(userIncides, ANSI_GREEN)
        solution = problem[IS_TRUE]


def get_wifi_ip_and_broadcast():
    # Create a UDP socket
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    try:
        # Connect to an external server (doesn't actually send any data)
        udp_socket.connect(("8.8.8.8", 80))
        
        # Get the local IP address associated with the socket
        ip_address = udp_socket.getsockname()[0]
        
        # Extract the subnet address
        subnet_address = '.'.join(ip_address.split('.')[:-1])
        
        # Construct the broadcast address
        broadcast_address = f"{subnet_address}.255"
        
    finally:
        # Close the socket to release resources
        udp_socket.close()
    
    return broadcast_address

# Game Flow
if __name__ == '__main__':
    server = Server()
    server.init_tcp_socket()
    server.run_trivia_game()

