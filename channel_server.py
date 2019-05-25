import socket
import threading
import json

clients = []


def server():

    host = ''
    port = 5000

    # Create server socket
    server_socket = socket.socket()
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((host, port))

    server_socket.listen()

    # waiting for client
    #threading.Thread(target=waiting_for_client, args=(server_socket, )).start()
    while True:
        conn, addr = server_socket.accept()
        print(addr, ' connected')
        threading.Thread(target=waiting_for_client, args=(conn,)).start()

    # waiting_for_client(server_socket)

    while True:
        pass    # Server shouldn't die


# Waiting for client
def waiting_for_client(conn):
    while True:
        same_name = False

        # First, you have to get data from client
        json_data = conn.recv(1024).decode()

        # Client will give you json that involves username, channel.
        # username will be a primary key. There can't be more than two users that has same username

        # You have to unwrap json
        data = json.loads(json_data)

        # Check there is a same name in the clients
        new_user_name = data['username']
        for client in clients:
            if client['username'] == new_user_name:
                # In case of there is a same username already
                same_name = True
                # Server have to request reinput username
                data = {
                    'ok': False,
                    'error': 'Existing username',
                    'content': 'Existing username'
                }
                json_data = json.dumps(data)
                conn.send(json_data.encode())

        # If there is a same username, restart from the first line.
        if same_name:

            continue

        # After name check, create new client object, and put that in the clients list
        new_client = {
            'username': data['username'],
            'channel': data['channel'],
            # Client have to have socket so server can send data to the client that server wants
            'socket': conn
        }

        clients.append(new_client)
        # Server should teach client that login successed
        data = {
            'ok': True,
            'error': None,
            'content': 'login success'
        }

        json_data = json.dumps(data)
        conn.send(json_data.encode())
        threading.Thread(target=send_chat, args=(conn, )).start()
        return


# Waiting for data from client
# if server gets data from client, then should send data to the appropriate clients.
def send_chat(conn):
    while True:
        # First get the data from client
        json_data = conn.recv(1024).decode()
        parsed_data = json.loads(json_data)

        # If the message client sent is quit(), then server kill the client in the clients,
        # quit the def.
        message = parsed_data['message']
        username = parsed_data['username']
        channel = parsed_data['channel']
        if message == 'quit()':
            for client in clients:
                if client['username'] == username:

                    data = {
                        'ok': True,
                        'error': None,
                        'content': 'quit'
                    }
                    json_data = json.dumps(data)
                    client['socket'].send(json_data.encode())
                    client['socket'].close()
                    clients.remove(client)
                    print('current clients:', clients)
            return

        # Send chat data to the all clients that share same channel except one who send the message
        data_to_send = {
            'content': None,
            'username': username,
            'message': message
        }

        json_data_to_send = json.dumps(data_to_send)

        for client in clients:
            if channel == client['channel']:
                if username != client['username']:
                    client['socket'].send(json_data_to_send.encode())


# Send data to client


if __name__ == '__main__':
    server()
