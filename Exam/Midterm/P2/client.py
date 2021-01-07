import socket
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('serverIP')
parser.add_argument('serverPort')
args = parser.parse_args()

serverIP = args.serverIP
serverPort = int(args.serverPort)
serverAddress = (serverIP, serverPort)

TCPsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
TCPsocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
TCPsocket.connect(serverAddress)

def exeClient():
    response = getTCPresponse()
    TCPresponse = response.strip().split()
    print(response)
    while True:
        command = input('% ').strip()
        commands = command.split()
        if commands:
            TCPsocket.sendall(command.encode('utf-8'))
            response = getTCPresponse()
            TCPresponse = response.strip().split()
            print(response)
            if TCPresponse[0] == 'Bye,':
                break
    TCPsocket.close()


def getTCPresponse():
    response = []
    while True:
        part = TCPsocket.recv(1024)
        response.append(str(part, 'utf-8'))
        if len(part) < 1024:
            break
    TCPresponse = ''.join(response)
    return TCPresponse


if __name__ == "__main__":
    try:
        exeClient()
    except (KeyboardInterrupt, OSError, Exception) as e:
        TCPsocket.sendall('exit'.encode('utf-8'))
        TCPsocket.close()
        print(e)







