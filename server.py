import socket
import random
import string

def new_connect():
    id = id_generator()
    dict[id] = None
    return id


def new_inf(id, data):
    for client in dict:
        if client is not id:
            dict.update({client, client + data})


# TODO ask about import rendom and string
def id_generator():
    return ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(128))


server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(('', 12345))
server.listen(5)

dict = {}

while True:
    client_socket, client_address = server.accept()
    print('Connection from: ', client_address)
    data = bytes('', 'utf-8')
    while len(data) < 100000:
        temp = client_socket.recv(1024)
        data = data + temp
        if temp == b'':
            break

    #data = client_socket.recv(100)
    if data == b'new connection':
        id = new_connect()

        client_socket.send(bytes(id, "utf-8"))
    else:
        id, flag, path = data.decode('utf-8').split("|")

        if flag == "receive":
            if dict.get(id) is not None:
                client_socket.send(bytes(dict.get(id), "utf-8"))

            dict.update({id, None})
        else:

            new_inf(id, data)
            print('Received: ', data)
            if dict.get(id) is not None:
                client_socket.send(bytes(dict.get(id), "utf-8"))

            dict.update({id, None})



    #client_socket.send(data.upper())

    client_socket.close()
    print('Client disconnected')

