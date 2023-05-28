#!/usr/bin/python3

"""
Simple HTTP Server.

Features:
- Listens for incoming HTTP requests.
- Handles basic HTTP methods (GET).
- Serves requested files from the "resources" directory.
- Sends appropriate HTTP responses (200 OK, 404 Not Found).
- Handles multiple requests at the same time.
"""

# Libraries ------------------------------------------------------------------>

import os
import sys
from signal import SIGINT, signal
from socket import AF_INET, SOCK_STREAM, socket
from threading import Thread
from typing import List

# Authorship ----------------------------------------------------------------->

__author__ = "Kirill Shkirov"
__license__ = "MIT"
__email__ = "kichkiro@student.42firenze.it"
__slack__ = "kichkiro"
__status__ = "Finished"

# Functions ------------------------------------------------------------------>


def signal_handler(_signal_received: int, __frame: object) -> None:
    """
    Handles the SIGINT signal.
    If SIGINT signal is received, the server will be stopped.

    Params
    --------------------------------------------------------------------
    None

    Returns
    --------------------------------------------------------------------
    None
    """
    print("\nServer has been stopped.")
    os.kill(os.getpid(), 9)
    sys.exit()


def connection_handler(conn_socket: socket) -> None:
    """
    Handles the connection with a client.

    Params
    --------------------------------------------------------------------
    conn_socket : socket
        The socket object representing the connection.

    Returns:
    --------------------------------------------------------------------
    None
    """
    message: str
    resource: str
    outputdata: str

    try:
        message = conn_socket.recv(1024).decode()
        resource = message.split()[1]

        # Open and read the file if it exists -------------------------------->
        with open(f"resources/{resource}", "r", encoding="utf-8") as file:
            outputdata = file.read()

        # Send HTTP headers into socket -------------------------------------->
        conn_socket.send("HTTP/1.1 200 OK\r\n".encode())
        conn_socket.send("Content-Type: text/html\r\n".encode())
        conn_socket.send(f"Content-Length: {len(outputdata)}\r\n".encode())
        conn_socket.send("\r\n".encode())

        # Send the content of the requested file to the client --------------->
        for _i, data in enumerate(outputdata):
            conn_socket.send(data.encode())
        conn_socket.send("\r\n".encode())
        print(f"Resource: {resource} - has been sent.")

        conn_socket.close()
    except (IOError, IndexError):
        # Send response message for file not found --------------------------->
        conn_socket.send("HTTP/1.1 404 Not Found\r\n".encode())
        conn_socket.close()
        print("File not found.")
    print("Connection closed. - Thread has been stopped.")


def main(argv: List[str]) -> None:
    """
    Main function that starts the server.

    Params
    --------------------------------------------------------------------
    argv: List[str]
        List of command line arguments.

    Returns
    --------------------------------------------------------------------
    None
    """
    server_socket: socket
    server_port: int
    conn_socket: socket
    addr: tuple
    thread: Thread

    if len(argv) != 2:
        print(f"Usage: {argv[0]} <port>")
        sys.exit()

    # Prepare a sever socket ------------------------------------------------->
    server_socket = socket(AF_INET, SOCK_STREAM)
    server_port = int(argv[1])
    server_socket.bind(('', server_port))
    server_socket.listen(1)

    while True:

        # Establish the connection ------------------------------------------->
        print('\nReady to serve...')
        conn_socket, addr = server_socket.accept()
        print(f"Connection from {addr} has been established.")

        # Creating new thread for handle the connection ---------------------->
        thread = Thread(target=connection_handler, args=(conn_socket, ))
        thread.start()


if __name__ == "__main__":
    signal(SIGINT, signal_handler)
    main(sys.argv)
