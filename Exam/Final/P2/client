#!/usr/bin/env python3
import socket
import argparse
import threading
import select
import sys

parser = argparse.ArgumentParser()
parser.add_argument('serverIP')
parser.add_argument('serverPort')
args = parser.parse_args()

if not args.serverPort.isdecimal():
    print('Port should be an interger.')
    exit()

serverIP = args.serverIP
serverPort = int(args.serverPort)
serverAddress = (serverIP, serverPort)

TCPsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
TCPsocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
TCPsocket.connect(serverAddress)


def exeClient():
    # Welcome message
    printTCPresponse()

    while True:
        command = input('')
        commands = command.strip().split()
        if commands:
            TCPsocket.sendall(command.encode('utf-8'))
            
            printTCPresponse()

            if commands[0] == 'exit':
                break
    TCPsocket.close()


def printTCPresponse():
    response = []
    while True:
        part = TCPsocket.recv(1024)
        response.append(str(part, 'utf-8'))
        if len(part) < 1024:
            break
    TCPresponse = ''.join(response)
    if response:
        print(TCPresponse)
    return TCPresponse


if __name__ == "__main__":
    try:
        exeClient()
    except (KeyboardInterrupt, OSError, Exception) as e:
        TCPsocket.sendall('exit'.encode('utf-8'))
        TCPsocket.close()
        print(e)







