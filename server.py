import os
import socket
import random
import string
import utils

port_number = 12347


# new file that need to be saved
def new_connect():
    id = id_generator()
    id = "nrIFfGn8dKvPpoFRCxwgvV4y9gZewMDbCFfKonyM7YubZHi33YFdW6xEcTM0eD5X1zZLvKacdJxCljbxs4XsQEBvwALvk8G053UipzIg40RPLPKjpqQ6svmUxckNLLP0"
    # how many members the file have
    num_of_members = 1
    id_dict = {}
    id_dict[0] = num_of_members
    id_dict[1] = []

    dict[id] = id_dict
    # todo - check what the function need to upload a file

    return id


# new user how need to connect a file by id
def connecting_user(id):
    dict[id][0] = dict[id][0] + 1
    dict[id][dict[id][0]] = []
    send_to_new_user(id)
    return dict[id][0]


# same as client
def receive_new_connect(client_socket, id):
    dir = bytes('', 'utf-8')
    while len(dir) < 10000000:
        temp = client_socket.recv(1024)
        dir = dir + temp
        if temp == b'' or len(temp) < 1024:
            break

    os.mkdir(id)
    f = open(id + ".zip", 'wb')
    f.write(dir)
    f.close()
    str2 = "bash -c 'unzip -q " + id + ".zip -d " + id + "'"
    os.system(str2)
    os.remove(id + ".zip")


# same as client
def send_to_new_user(id):
    pass


def new_inf(id, internal_id, data):
    for client in dict[id]:
        if client != int(internal_id) and client != 0:
            dict[id].get(client).append(data)


def id_generator():
    return ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(1, 129))


if __name__ == '__main__':

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(('', port_number))
    server.listen(5)

    dict = {}

    while True:
        client_socket, client_address = server.accept()
        print('Connection from: ', client_address)
        data = bytes('', 'utf-8')
        # getting info
        while len(data) < 10000000:
            temp = client_socket.recv(1024)
            data = data + temp
            if temp == b'' or len(temp) < 1024:
                break

        if data == b'new connection':
            id = new_connect()
            print(id)
            client_socket.send(bytes(id, "utf-8"))
            os.mkdir("./"+id)
            # create folder
            # utils.download_dir(client_socket, id)
            # dir = bytes('', 'utf-8')
            # while len(dir) < 10000000:
            #     temp = client_socket.recv(1024)
            #     dir = dir + temp
            #     if temp == b'' or len(temp) < 1024:
            #         break




        else:
            splited = data.decode('utf-8').split("|")
            try:

                id = splited[0].strip("\'")

                internal_id = splited[1].strip("'")

                flag = splited[2]
                path = splited[3]
                list = dict.get(id)
            except:
                pass

            # if new user wants to connect
            if flag == "connecting user":
                internal_id = connecting_user(id)
                client_socket.send(bytes(str(internal_id), "utf-8"))

            # if want only info
            elif flag == "receive":

                internal_id = int(internal_id)
                if dict[id][int(internal_id)] is not None and len(dict[id][int(internal_id)]) != 0:
                    value = dict[id][int(internal_id)].pop(0)
                    client_socket.send(value)


            # if want to give and receive info
            else:

                new_inf(id, internal_id, data)
                print('Received: ', data)
                utils.receive_info(data, "./" + id)
                if dict[id][int(internal_id)] is not None and len(dict[id][int(internal_id)]) != 0:
                    value = dict[id][int(internal_id)].pop(0)
                    client_socket.send(value)

        client_socket.close()
        print('Client disconnected')
