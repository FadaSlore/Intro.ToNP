#!/usr/bin/env python3

import socket
import argparse
import sqlite3
import select
import datetime
import threading
import random

parser = argparse.ArgumentParser()
parser.add_argument('port')
args = parser.parse_args()

if not args.port.isdecimal():
    print('port should be an interger')
    exit()

host = 'localhost'
port = int(args.port)

address = (host, port)

TCPsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
UDPsocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
TCPsocket.bind(address)
UDPsocket.bind(address)
TCPsocket.listen(20)

inputs = []
inputs.append(TCPsocket.fileno())
inputs.append(UDPsocket.fileno())

# shared memory

class User():
    def __init__(self, userName, email, password):
        self.userName = userName
        self.email = email
        self.password = password
Users = []

class Client():
    def __init__(self, randomNumber, userName):
        self.randomNumber = randomNumber
        self.userName = userName
Clients = []

class Board():
    def __init__(self, ID, boardName, moderator):
        self.ID = ID
        self.boardName = boardName
        self.moderator = moderator
BoardIndex = 1
Boards = []

class Comment:
    def __init__(self, userName, comment):
        self.userName = userName
        self.comment = comment

class Post():
    def __init__(self, postID, boardName, author, title, content, postDate):
        self.postID = postID
        self.boardName = boardName
        self.author = author
        self.title = title
        self.content = content
        self.postDate = postDate
        self.comments = []
    def addComment(self, userName, comment):
        self.comments.append(Comment(userName, comment))
PostIndex = 1
Posts = []
PostLock = threading.Lock()


# UDP related function & command: register, whoami

def UDPsend(message, address):
    UDPsocket.sendto(message.encode('utf-8'), address)


def exe_register(commands, address):
    if len(commands) != 4:
        UDPsend('Usage: register <username> <email> <password>', address)
    else:
        for user in Users:
            if commands[1] == user.userName:
                UDPsend('Username is already used.', address)
                return
        Users.append(User(commands[1], commands[2], commands[3]))
        UDPsend('Register successfully.', address)


def exe_whoami(commands, address):
    randomNumber = int(commands[1])
    if randomNumber == -1:
        UDPsend('Please login first.', address)
    else:
        for client in Clients:
            if randomNumber == client.randomNumber:
                UDPsend(client.userName, address)
                return
        UDPsend('Error in whoami.', address)


# TCP related function & command

class TCPThread(threading.Thread):
    def __init__(self, socketfd, address, currentUser, randomNumber):
        threading.Thread.__init__(self)
        self.socketfd = socketfd
        self.address = address
        self.currentUser = currentUser
        self.randomNumber = randomNumber

    def run(self):
        while True:
            commands = self.getTCPcommand().strip().split()

            if commands:
                # exit
                if commands[0] == 'exit':
                    self.TCPsend('exit')
                    break
                elif commands[0] == 'login':
                    self.exe_login(commands)
                elif commands[0] == 'logout':
                    self.exe_logout()
                elif commands[0] == 'list-user':
                    self.exe_listUser()
                elif commands[0] == 'create-board':
                    self.exe_createBoard(commands)
                elif commands[0] == 'create-post':
                    self.exe_createPost(commands)
                elif commands[0] == 'list-board':
                    self.exe_listBoard()
                elif commands[0] == 'list-post':
                    self.exe_listPost(commands)
                elif commands[0] == 'read':
                    self.exe_read(commands)
                elif commands[0] == 'delete-post':
                    self.exe_deletePost(commands)
                elif commands[0] == 'update-post':
                    self.exe_updatePost(commands)
                elif commands[0] == 'comment':
                    self.exe_comment(commands)
                else:
                    self.TCPsend('Unsupport command.')
        self.socketfd.close()

    def getTCPcommand(self):
        command = []
        while True:
            part = self.socketfd.recv(1024)
            command.append(str(part, 'utf-8'))
            if len(part) < 1024:
                break
        commands = ''.join(command)
        return commands

    def TCPsend(self, message):
        self.socketfd.sendall(message.encode('utf-8'))

    def exe_login(self, commands):
        if len(commands) != 3:
            self.TCPsend('Usage: login <username> <password>')
        elif self.currentUser:
            self.TCPsend('Please logout first.')
        else:
            for user in Users:
                if commands[1] == user.userName:
                    if commands[2] == user.password:
                        self.currentUser = user.userName
                        self.randomNumber = random.randint(1, 100000)
                        Clients.append(Client(self.randomNumber, user.userName))
                        # check userName & randomnumber
                        # print(self.currentUser, ': ', self.randomNumber)
                        self.TCPsend(f'Welcome, {self.currentUser}. {self.randomNumber}')
                        return
            self.TCPsend('Login failed.')

    def exe_logout(self):
        if not self.currentUser:
            self.TCPsend('Please login first.')
        else:
            for client in Clients:
                if self.randomNumber == client.randomNumber:
                    if self.currentUser == client.userName:
                        Clients.remove(client)
                        self.TCPsend(f'Bye, {self.currentUser}')
                        self.randomNumber = -1
                        self.currentUser = None
                        return
            self.TCPsend('Error in logout.')

    def exe_listUser(self):
        message = '{:<20}{:<20}'.format('Name', 'Email')
        for user in Users:
            message += '\n{:<20}{:<20}'.format(user.userName, user.email)
        self.TCPsend(message)

    def exe_createBoard(self, commands):
        global BoardIndex
        if len(commands) != 2:
            self.TCPsend('Usage: create-board <name>')
        elif not self.currentUser:
            self.TCPsend('Please login first.')
        else:
            for board in Boards:
                if commands[1] == board.boardName:
                    self.TCPsend('Board already exists.')
                    return
            Boards.append(Board(BoardIndex, commands[1], self.currentUser))
            BoardIndex += 1
            self.TCPsend('Create board successfully.')

    def exe_createPost(self, commands):
        global PostIndex
        if '--title' not in commands or '--content' not in commands:
            self.TCPsend('Usage: create-post <board-name> --title <title> --content <content>')
            return

        title_index = commands.index('--title')
        content_index = commands.index('--content')
        if title_index == 1 or content_index == title_index + 1 or len(commands) == content_index + 1:
            self.TCPsend('Usage: create-post <board-name> --title <title> --content <content>')
            return

        boardName = None
        for board in Boards:
            if commands[1] == board.boardName:
                boardName = board.boardName
                break
        if not boardName:
            self.TCPsend('Board does not exist.')
            return

        title = ' '.join(commands[title_index + 1:content_index])
        content = ' '.join(commands[content_index + 1:])
        content = content.replace('<br>', '\n')
        date = str(datetime.datetime.now().date()).split('-')
        postDate = date[1] + '/' + date[2]
        # start lock
        PostLock.acquire()
        try:
            Posts.append(Post(PostIndex, boardName, self.currentUser, title, content, postDate))
            PostIndex += 1
        finally:
            PostLock.release()
        # end lock
        self.TCPsend('Create post successfully.')

    def exe_listBoard(self):
        message = '{:<10}{:<20}{:<20}'.format('Index', 'Name', 'Moderator')
        for board in Boards:
            message += '\n{:<10}{:<20}{:<20}'.format(board.ID, board.boardName, board.moderator)
        self.TCPsend(message)

    def exe_listPost(self, commands):
        if len(commands) != 2:
            self.TCPsend('Usage: list-post <board-name>')
        else:
            existFlag = False
            for board in Boards:
                if board.boardName == commands[1]:
                    existFlag = True
            if not existFlag:
                self.TCPsend('Board does not exist.')
                return

            # start lock
            PostLock.acquire()
            try:
                message = '{:<10}{:<20}{:<20}{:<6}'.format('S/N', 'Title', 'Author', 'Date')
                for post in Posts:
                    if post.boardName == commands[1]:
                        message += '\n{:<10}{:<20}{:<20}{:<6}'.format(post.postID, post.title, post.author, post.postDate)
            finally:
                PostLock.release()
            # end lock
            self.TCPsend(message)

    def exe_read(self, commands):
        if len(commands) != 2:
            self.TCPsend('Usage: read <post-id>')
            return
        if not commands[1].isdecimal():
            self.TCPsend('Usage: read <post-id>')
            return

        # start lock
        PostLock.acquire()
        try:
            message = None
            for post in Posts:
                if int(commands[1]) == post.postID:
                    message = f'Author: {post.author}\nTitle: {post.title}\nDate: {post.postDate}\n--\n{post.content}\n--'
                    for comment in post.comments:
                        message += f'\n{comment.userName}: {comment.comment}'
                    break
            if not message:
                self.TCPsend('Post does not exist.')
                return
        finally:
                PostLock.release()
        # end lock
        self.TCPsend(message)

    def exe_deletePost(self, commands):
        if len(commands) != 2:
            self.TCPsend('Usage: delete-post <post-id>')
            return
        if not commands[1].isdecimal():
            self.TCPsend('Usage: delete-post <post-id>')
            return

        if not self.currentUser:
            self.TCPsend('Please login first.')
            return

        # start lock
        PostLock.acquire()
        try:
            for post in Posts:
                if int(commands[1]) == post.postID:
                    if self.currentUser == post.author:
                        Posts.remove(post)
                        self.TCPsend('Delete successfully.')
                        return
                    else:
                        self.TCPsend('Not the post owner.')
                        return
        finally:
                PostLock.release()
        # end lock
        self.TCPsend('Post does not exist.')

    def exe_updatePost(self, commands):
        if len(commands) < 4:
            self.TCPsend('Usage: update-post <post-id> --title/content <new>')
            return

        if not commands[1].isdecimal():
            self.TCPsend('Usage: update-post <post-id> --title/content <new>')
            return

        if not self.currentUser:
            self.TCPsend('Please login first.')
            return

        if commands[2] != '--title' and commands[2] != '--content':
            self.TCPsend('Usage: update-post <post-id> --title/content <new>')
            return

        update = ' '.join(commands[3:])
        update = update.replace('<br>', '\n')

        # start lock
        PostLock.acquire()
        try:
            for post in Posts:
                if int(commands[1]) == post.postID:
                    if self.currentUser == post.author:
                        if commands[2] == '--title':
                            post.title = update
                        elif commands[2] == '--content':
                            post.content = update
                        self.TCPsend('Update successfully.')
                        return
                    else:
                        self.TCPsend('Not the post owner.')
                        return
        finally:
                PostLock.release()
        # end lock
        self.TCPsend('Post does not exist.')

    def exe_comment(self, commands):
        if len(commands) < 3:
            self.TCPsend('Usage: comment <post-id> <comment>')
            return

        if not commands[1].isdecimal():
            self.TCPsend('Usage: comment <post-id> <comment>')
            return

        if not self.currentUser:
            self.TCPsend('Please login first.')
            return

        comment = ' '.join(commands[2:])

        # start lock
        PostLock.acquire()
        try:
            for post in Posts:
                if int(commands[1]) == post.postID:
                    post.addComment(self.currentUser, comment)
                    self.TCPsend('Comment successfully.')
                    return
        finally:
                PostLock.release()
        # end lock
        self.TCPsend('Post does not exist.')






# Server execution

def exeServer():
    while True:
        readable, _, err = select.select(inputs, [], [])

        for sockfd in readable:
            if sockfd is TCPsocket.fileno():
                client, address = TCPsocket.accept()
                print('New connection.')
                # print(f'TCP connetion: {address[0]}:{address[1]}')
                thread = TCPThread(client, address, None, -1)
                thread.start()
            elif sockfd is UDPsocket.fileno():
                raw_data, address = UDPsocket.recvfrom(1024)
                command = raw_data.decode('utf-8')
                # print(f'UDP connection: {address[0]}:{address[1]}')
                # print('Command: ', command)
                commands = command.strip().split()

                if commands[0] == 'register':
                    exe_register(commands, address)
                elif commands[0] == 'whoami':
                    exe_whoami(commands, address)




if __name__ == '__main__':
    print('Turn on the Server.')
    try:
        exeServer()
    except KeyboardInterrupt:
        print('\nExit Server.')
        TCPsocket.close()
        UDPsocket.close()


