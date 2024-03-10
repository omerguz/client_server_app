import socket
import struct
import threading
import time
import concurrent
from concurrent.futures import thread
import random
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
        self.teams = []
        self.sol=[]
        self.lock=threading.Lock()
        # self.DevNet = "172.1.0.4"
        self.udpBroadcastPort = 13117
        self.gemeEndTime = 10
        self.bufferSize = 1024

    def brodcastUdpOffer(self):
        ''' 
        This function is responsible for sending out "offer" announcements
        to all clients in the network evry 1 second via UDP
        '''
        # Start and set the thread to send offers every 1 sec.
        ip_parts = self.hostIP.split('.')
        # Change the last value
        ip_parts[-1] = "255"
        # Join the parts back into a string
        modified_ip = '.'.join(ip_parts)

        threading.Timer(1.0, self.brodcastUdpOffer).start()

        # Pack the message in a udp format.
        offerMessage = struct.pack("Ibh", 0xabcddcba, 0x2, self.hostPort)
        # brodacast the message to all clients connected to the net
        self.UDPSocket.sendto(
        offerMessage, (modified_ip, self.udpBroadcastPort))
        # offerMessage, ('<broadcast>', self.udpBroadcastPort))

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
        while (len(self.teams) >= 1 and time.time() - start_time < 10) or len(server.teams) < 1:
            self.TCPSocket.settimeout(10)
            try:
                clientSocket, clientAddress = self.TCPSocket.accept()
                teamName = clientSocket.recv(self.bufferSize).decode("utf-8")
                self.teams.append((clientSocket, clientAddress, teamName))
                if len(self.teams) == 1:    # start the timer when the first client joins
                    start_time = time.time()
            except:
                continue

    def startGameMode(self, player, timer):
        while time.time() - timer < self.gemeEndTime:
            try:
                player[0].settimeout(0.01)
                userSolution = player.recv(self.bufferSize).decode("utf-8")
                with self.lock:
                    self.sol.append(userSolution, player[2])
            except:
                pass
            
def remove_wrong_answer_players(current_players, sol, correct_answer):
    # Get the names of players who gave the wrong answer
    wrong_answer_players = {player_name for solution, player_name in sol if solution != correct_answer}
    not_answered_players = {player_name for _, _, player_name in current_players if player_name not in [player_name for _, player_name in sol]}
    wrong_answer_players = wrong_answer_players.union(not_answered_players)
    
    all_player_names = [player_name for _, _, player_name in current_players]
    all_exist = all(player_name in all_player_names for player_name in wrong_answer_players)
    if not all_exist:
    # Filter out the players who gave the wrong answer
        updated_current_players = [(client_socket, client_address, player_name) for client_socket, client_address, player_name in current_players if player_name not in wrong_answer_players]
    
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
    for i, team in enumerate(server.teams):
        player_names += f"Player Number {i}: {team[2]}\n"
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
        server.teams = []
        # Print start message
        print(f"Server started, listening on IP address {server.hostIP}")
        # Start wait for clients stage
        server.waitForClient()

        if len(server.teams) == 0:
            continue

        welcomeMsg = f"Welcome to the Mystic server, where we are answering trivia questions about English Premier League.\n{getPlayersNames(server)}"

        print(welcomeMsg)
        for team in server.teams:
            team[0].send(bytes(welcomeMsg, "utf-8"))
        counter = 0
        pool =  concurrent.futures.ThreadPoolExecutor(len(server.teams))
        current_players = server.teams
        while len(current_players) >= 1:
            timer = time.time() #round is only 10 seconds
            problem, solution = get_random_question()
            counter += 1
            msg = f"Round {counter}, played by " + format_names([team[2] for team in current_players]) + f": True or false: {problem}\n"
            for team in server.teams:
                team[0].send(bytes(msg, "utf-8"))
            print(msg)
            msg = ""

            for team in server.teams:
                pool.submit(server.startGameMode, team, timer)
            time.sleep(10)
            for i, s in enumerate(server.sol):
                # remove the client from the game if it didn't answer in time\correctly
                if(s[0] == solution):
                    msg += f"{s[1]} is correct!\n"
                else:
                    msg += f"{s[1]} is incorrect!\n"
            current_players = remove_wrong_answer_players(current_players, server.sol, solution)
            for team in server.teams:
                team[0].send(bytes(msg, "utf-8"))
            print(msg)
            msg = ""    
            if(len(current_players) == 1):
                msg += f"{current_players[0][2]} is the winner!"
                for team in server.teams:
                    team[0].send(bytes(msg, "utf-8"))
                print(msg)
                msg = ""      
        for team in server.teams:
            try:
                team[0].close()
            except:
                continue
        print("Game over, sending out offer requests...")
