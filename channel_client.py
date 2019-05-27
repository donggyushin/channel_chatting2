import socket
import json
import threading
import sys


def client():
    host = 'localhost'
    port = 5000

    client_socket = socket.socket()
    client_socket.connect((host, port))

    login(client_socket)
    print('before return')
    return


def login(socket):
    while True:
        print('Please Input username')
        username = input()
        print('Which channel do you want to join in? from 0 to 999')
        channel = int(input())

        data = {
            'username': username,
            'channel': channel
        }

        json_data = json.dumps(data)
        socket.send(json_data.encode())
        json_result = socket.recv(1024).decode()
        result = json.loads(json_result)

        if result['ok']:
            print('Login Success!')
            t = threading.Thread(target=send_chat, args=(
                socket, username, channel))
            t.start()
            receive_chat(socket)
            t._delete()
            return
        else:
            print('There is already existing username')
            print('Please fill the form again')
            print('----------------------------------')


def send_chat(socket, username, channel):
    while True:
        message = input()
        data = {
            'username': username,
            'message': message,
            'channel': channel
        }
        json_data = json.dumps(data)
        socket.send(json_data.encode())


def receive_chat(socket):
    while True:
        json_data = socket.recv(1024).decode()
        data = json.loads(json_data)
        # If the data['content'] is 'quit', then terminate program
        if data['content'] == 'quit':
            print('program terminated')
            sys.exit()
            return
        username = data['username']
        message = data['message']
        print(username, ':', message)


if __name__ == '__main__':
    client()
