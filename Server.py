import socket
import struct
import threading
import time
import concurrent
from concurrent.futures import thread
import random
import copy
# from termcolor import colored


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
        self.playersTuple = [] # Stores information about players (socket, address, name)
        self.solutionTuples = [] # Stores solutions submitted by players (solution, player_name)
        self.lock = threading.Lock() # Lock for thread safety
        self.udpflg = False # Flag for UDP broadcast
        self.udpBroadcastPort = 13117 # UDP broadcast port
        self.gemeEndTime = 10 # Game end time in seconds
        self.bufferSize = 1024 # Buffer size for socket communication

    def brodcastUdpOffer(self):    
        while self.udpflg==False:
            offerMessage = struct.pack("Ibh", 0xabcddcba, 0x2, self.hostPort)
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
        UdpBroadcastThread = threading.Thread(target=server.brodcastUdpOffer)
        UdpBroadcastThread.start()
        # TODO : Change timeouts
        while (len(self.playersTuple) >= 1 and time.time() - start_time < 3) or len(server.playersTuple) < 1:
        # while (len(self.playersTuple) >= 1 and time.time() - start_time < 10) or len(server.playersTuple) < 1:
            self.TCPSocket.settimeout(0.5)
            # self.TCPSocket.settimeout(10)
            try:
                clientSocket, clientAddress = self.TCPSocket.accept()
                playerName = clientSocket.recv(self.bufferSize).decode("utf-8")
                self.playersTuple.append((clientSocket, clientAddress, playerName))
                if len(self.playersTuple) == 1:    # start the timer when the first client joins
                    start_time = time.time()
            except:
                continue
        self.udpflg = True
        
        

    def startGameMode(self, player, timer):
        start_time = time.time()
        while time.time() - start_time < 10:  # Ensure the loop runs for a maximum of 10 seconds
            try:
                # Set a timeout for the recv call
                player[0].settimeout(0.5)
                
                # Receive data from the player
                userSolution = player[0].recv(self.bufferSize).decode("utf-8")
                
                # Append the solution to the list of solution tuples
                with self.lock:
                    self.solutionTuples.append((userSolution, player[2]))
                    break
            
            except socket.timeout:
                # Handle timeout exception (no data received within the timeout period)
                pass
            except Exception as e:
                # Handle other exceptions
                print(f"Error in startGameMode: {e}")

            
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
        updated_current_players = [(client_socket, client_address, player_name) for client_socket, client_address, player_name in current_players if player_name not in wrong_unanswered_players]
    
    return updated_current_players

trivia_questions = [
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

def get_random_question():
    random_question = random.choice(trivia_questions)
    question = random_question["question"]
    answer = random_question["is_true"]
    return question, answer

def getPlayersNames(server):
    """
    Retrieve the names of the players from the server's teams.
    """
    player_names = ""
    for i, playerTuple in enumerate(server.playersTuple):
        player_names += f"Player Number {i}: {playerTuple[2]}\n"
    # Remove the trailing comma and space
    return player_names

def format_names(names):
    if not names:
        return ""
    elif len(names) == 1:
        return names[0]
    else:
        return ", ".join(names[:-1]) + ", and " + names[-1]

# Game Flow
if __name__ == '__main__':
    server = Server()
    con = False
    while not con:
        try:
            server.TCPSocket.bind(("", server.hostPort))
            con = True
        except:
            pass
    server.TCPSocket.listen()
    while True:
        server.playersTuple = []
        server.solutionTuples=[]
        server.udpflg = False
        # Print start message
        print(f"Server started, listening on IP address {server.hostIP}")
        # Start wait for clients stage
        server.waitForClient()

        if len(server.playersTuple) == 0:
            continue

        welcomeMsg = f"Welcome to the Mystic server, where we are answering trivia questions about English Premier League.\n{getPlayersNames(server)}"

        print(welcomeMsg)
        for playerTuple in server.playersTuple:
            playerTuple[0].send(bytes(welcomeMsg, "utf-8"))
        counter = 0
        pool =  concurrent.futures.ThreadPoolExecutor(len(server.playersTuple))

        current_players=[]
        for player_tuple in server.playersTuple:
            current_player = (player_tuple[0],  # Deep copy socket object
                            player_tuple[1],  # Deep copy client address
                            player_tuple[2])                 # Player name (no need to copy)
            current_players.append(current_player)


        while len(current_players) >= 1:
            timer = time.time() #round is only 10 seconds
            problem, solution = get_random_question()
            counter += 1
            msg = f"Round {counter}, played by " + format_names([playerTuple[2] for playerTuple in current_players]) + f": True or false: {problem}\n"
            for playerTuple in server.playersTuple:
                playerTuple[0].send(msg.encode("utf-8"))
            print(msg)
            msg = ""
            with server.lock:
                server.solutionTuples = []
            for playerTuple in server.playersTuple:
                pool.submit(server.startGameMode, playerTuple, timer)
            
            start_time = time.time()
            while time.time() - start_time < 10:
                with server.lock:
                    if(len(server.solutionTuples) == len(server.playersTuple)):
                        break
                    time.sleep(0.5)  # Sleep for 1 second before rechecking
            
            with server.lock:
                for i, s in enumerate(server.solutionTuples):
                    # remove the client from the game if it didn't answer in time\correctly
                    if(s[0] == solution):
                        msg += f"{s[1]} is correct!\n"
                    else:
                        msg += f"{s[1]} is incorrect!\n"

            #remove all unanswered and wring clients. do nothing if none of the clients were rihgt
            current_players = remove_wrong_answer_players(current_players, server.solutionTuples, solution)
            #report of all incorrect\correct players
            for playerTuple in server.playersTuple:
                playerTuple[0].send(msg.encode("utf-8"))
            print(msg)
            msg = "Congratulations to the winner: "    
            if(len(current_players) == 1):
                    msg += f"{current_players[0][2]}"
                    for playerTuple in server.playersTuple:
                        playerTuple[0].send(msg.encode("utf-8"))
                    print(msg)
                    msg = "Game over, sending out offer requests..." 
                    print(msg)
                    break
        
        for playerTuple in server.playersTuple:
            try:
                playerTuple[0].close()
            except:
                continue
        
        
         
        
