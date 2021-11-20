import socket
import random
import string
port_number= 12346

def new_connect():
    id = id_generator()
    dict[id] = []
    return id


def new_inf(id, data):
    for client in dict:
        if client != id:
            dict.get(client).append(data)




def id_generator():
    return ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(128))


server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(('', port_number))
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
        try:
            id= splited[0][:-1]
            flag= splited[1]
            path = splited[2]
            list = dict.get(id)
        except:
            pass

        #if want only info
        if flag == "receive":
            if dict.get(id) is not None and len(dict.get(id)) != 0:
                value = dict.get(id).pop(0)
                client_socket.send(value)


        #if want to give and receive info
        else:

            new_inf(id, data)
            print('Received: ', data)

            if dict.get(id) is not None and len(dict.get(id)) != 0:
                value = dict.get(id).pop(0)
                client_socket.send(value)







    #client_socket.send(data.upper())

    client_socket.close()
    print('Client disconnected')

