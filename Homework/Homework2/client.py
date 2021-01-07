import socket
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('serverIP')
parser.add_argument('serverPort')
args = parser.parse_args()

serverIP = args.serverIP
serverPort = int(args.serverPort)

serverAddress = (serverIP, serverPort)

def getTCPresponse(sock):
    response = []
    while True:
        part = sock.recv(1024)
        response.append(str(part, 'utf-8'))
        if len(part) < 1024:
            break
    TCPresponse = ''.join(response)
    return TCPresponse

def exeClient():
    TCPConnect = 0
    randomNumber = -1
    print('********************************\n** Welcome to the BBS server. **\n********************************')

    while True:
        command = input('% ')
        commands = command.strip().split()
        if commands:
            # register: UDP
            if commands[0] == 'register':
                UDPsocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                UDPsocket.sendto(command.encode('utf-8'), serverAddress)
                response, addr = UDPsocket.recvfrom(2048)
                UDPresponse = response.decode('utf-8')
                print(UDPresponse)
                UDPsocket.close()
            # whoami: UDP
            elif commands[0] == 'whoami':
                UDPsocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                sendMessage = str(command + ' ' + str(randomNumber))

                UDPsocket.sendto(sendMessage.encode('utf-8'), serverAddress)
                response, addr = UDPsocket.recvfrom(1024)
                UDPresponse = response.decode('utf-8')
                print(UDPresponse)
                UDPsocket.close()
            else:
                if TCPConnect == 0 :
                    TCPsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    TCPsocket.connect(serverAddress)
                    TCPConnect = 1

                TCPsocket.send(command.encode('utf-8'))
                response = getTCPresponse(TCPsocket)
                TCPresponse = response.strip().split()

                if TCPresponse[0] == 'Welcome,':
                    randomNumber = TCPresponse[2]
                    # check randomNumber
                    # print('randomNumber: ', randomNumber)
                    print(TCPresponse[0], TCPresponse[1])
                elif TCPresponse[0] == 'Bye,':
                    randomNumber = -1
                    print(response)
                elif TCPresponse[0] == 'exit':
                    TCPsocket.close()
                    break
                else:
                    print(response)


if __name__ == '__main__':
    exeClient()
