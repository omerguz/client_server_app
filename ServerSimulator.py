import socket
import random
import struct
import threading
import time


UDP_PORT = 13117
TCP_PORT = 12345  # Replace with any available port on your machine
BUFFER_SIZE = 1024
MAGIC_COOKIE = b'\xab\xcd\xdc\xba'
MESSAGE_TYPE_OFFER = b'\x02'
SERVER_NAME = "SimulatorServer"
IP_ADDR = "172.4.0.1"

def handle_tcp_connection(client_socket):
    print("TCP connection established with client.")
    # Implement further communication logic here if needed
    client_socket.close()

def send_offer(udp_socket):
    """Send offer message via UDP broadcast."""
    offer_message = struct.pack("Ibh", 0xabcddcba, 0x2, 2009)
    udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

    while True:
        udp_socket.sendto(offer_message, ('<broadcast>', UDP_PORT))
        time.sleep(1)

def udp_server():
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    udp_socket.bind(("", UDP_PORT))
    print("UDP server started, listening for connections...")

    while True:
            send_offer(udp_socket)
            # Open TCP connection upon client's request
            tcp_server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            tcp_server_socket.bind(("", TCP_PORT))
            tcp_server_socket.listen(1)
            client_tcp_socket, _ = tcp_server_socket.accept()
            threading.Thread(target=handle_tcp_connection, args=(client_tcp_socket,)).start()

# Start UDP server in a separate thread
udp_server()
