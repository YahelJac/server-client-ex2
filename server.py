import socket
import random
import string

def new_connect():
    id = id_generator()
    dict[id] = []
    return id


def new_inf(id, data):
    for client in dict:
        if client != id:
            dict.get(client).append(data)



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
        if temp == b'' or len(temp)<1024:
            break

    #data = client_socket.recv(100)
    if data == b'new connection':
        pass
        id = new_connect()

        client_socket.send(bytes(id, "utf-8"))
    else:
        splited = data.decode('utf-8').split("|")
        id, flag, path = splited[0][2:-1], splited[1], splited[2]
        list = dict.get(id)
        #if want only info
        if flag == b'receive' and len(dict.get(id)) != 0 :
            value = list.pop(0)
            client_socket.send(bytes(value, "utf-8"))

        #if want to give and receive info
        else:

            new_inf(id, data.decode('utf-8'))
            print('Received: ', data)

            if len(dict.get(id)) != 0 :

                value = dict.get(id).pop(0)
                client_socket.send(bytes(value, "utf-8"))







    #client_socket.send(data.upper())

    client_socket.close()
    print('Client disconnected')

