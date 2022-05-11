import os
import socket
import random
import string
import sys

import utils

port_number = int(sys.argv[1])


def new_connect():
    """
    New dir that need to be saved
    :return: id
    """
    id = id_generator()
    # how many members the dir have
    num_of_members = 1
    # creating a dict for the dir
    id_dict = {0: num_of_members, 1: []}
    dict[id] = id_dict
    return id


#
def connecting_user(id):
    """
    New user hwo need to connect a dir by existing id
    :param id:
    :return: the internal id
    """
    dict[id][0] = dict[id][0] + 1
    dict[id][dict[id][0]] = []
    internal_id = dict[id][0]
    send_to_new_user(id, internal_id)
    return dict[id][0]


# same as client
def send_to_new_user(id, internal_id):
    """
    Send all the information of the dir to initialise the dir to be the same
    :param id: ID of the dir that exists
    :param internal_id: the id of the user that want to be sync
    :return:
    """
    list_of_files = utils.upload_dir("./" + id, internal_id, id)
    for packet in list_of_files:
        dict[id][internal_id].append(packet)


def new_inf(id, internal_id, data):
    """
    When client send new change, update all other that connect to the dir
    :param id: id of dit
    :param internal_id: the client that send the change
    :param data: the change
    :return:
    """
    for client in dict[id]:
        if client != int(internal_id) and client != 0:
            dict[id].get(client).append(data)


def id_generator():
    # creating a new id by the orders
    return ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(1, 129))


if __name__ == '__main__':

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(('', port_number))
    server.listen(5)

    dict = {}

    # listening for new client to connect
    while True:
        client_socket, client_address = server.accept()
        print('Connection from: ', client_address)
        data = bytes('', 'utf-8')
        # getting info
        lenOfData = client_socket.recv(1024).decode()
        client_socket.send(b'len')

        # getting all the data that the client sends
        while True:
            temp = client_socket.recv(10000)
            data = data + temp
            if len(data) == int(lenOfData):
                break

        # whan the client is a new client with new dir
        if data == b'new connection':
            id = new_connect()
            print(id)
            client_socket.send(bytes(id, "utf-8"))
            os.mkdir("./" + id)

        else:
            # separate the message to id, internal id, flag, path
            splited = data.split(b'|')
            id = splited[0].decode('utf-8').strip("\'")
            internal_id = splited[1].decode('utf-8').strip("'")
            flag = splited[2].decode('utf-8')
            path = splited[3].decode('utf-8')
            list = dict.get(id)

            # if new user wants to connect
            if flag == "connecting user":
                internal_id = connecting_user(id)
                client_socket.send(bytes(str(internal_id), "utf-8"))

            # if he wants only info
            elif flag == "receive":

                internal_id = int(internal_id)
                if dict[id][int(internal_id)] is not None and len(dict[id][int(internal_id)]) != 0:
                    value = dict[id][int(internal_id)].pop(0)
                    client_socket.send(bytes(str(len(value)), 'utf-8'))
                    client_socket.recv(1024)
                    client_socket.send(value)

            # if he wants to give and receive info
            else:
                new_inf(id, internal_id, data)
                print('Received: ', data)
                utils.receive_info(data, "./" + id)
                if dict[id][int(internal_id)] is not None and len(dict[id][int(internal_id)]) != 0:
                    value = dict[id][int(internal_id)].pop(0)
                    client_socket.send(value)

        client_socket.close()
        print('Client disconnected')
