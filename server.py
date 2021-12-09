import os
import socket
import random
import string
import sys
import utils

# program variable
port_number = int(sys.argv[1])
dict = {}
id_sets = {}


# new file that need to be saved
def new_connect():
    # generate new id
    id = id_generator()
    num_of_members = 1
    # creating dict for the user
    id_dict = {}
    id_dict[0] = num_of_members
    id_dict[1] = []
    # inserting user dict in the general dict
    dict[id] = id_dict
    return id


# connect user to an existing user, generate internal id
def connecting_user(id):
    dict[id][0] = dict[id][0] + 1
    dict[id][dict[id][0]] = []
    internal_id = dict[id][0]

    # send saved files the stored in the server for that user
    send_to_new_user(id, internal_id)
    return dict[id][0]


# sand user stored data.
def send_to_new_user(id, internal_id):
    list_of_files = utils.upload_dir("./" + id, internal_id, id)
    for packet in list_of_files:
        dict[id][internal_id].append(packet)


# inserting new information that arrived from the server and stored it in the other users queue
def new_inf(id, internal_id, data):
    for client in dict[id]:
        if client != int(internal_id) and client != 0:
            dict[id].get(client).append(data)


# generate id
def id_generator():
    temp_id = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(1, 129))

    # make sure tht the id is uniq
    while temp_id in id_sets:
        temp_id = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(1, 129))
    return temp_id


# main function of the program
def main():
    # initialize server
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(('', port_number))
    server.listen(5)

    while True:
        # connecting to a client
        client_socket, client_address = server.accept()
        # print('Connection from: ', client_address)
        data = bytes('', 'utf-8')

        # receive info
        lenOfData = client_socket.recv(1024).decode()
        client_socket.send(b'len')
        while True:
            temp = client_socket.recv(10000)
            data = data + temp
            if len(data) == int(lenOfData):
                break

        # check if its a new user
        if data == b'new connection':
            id = new_connect()
            print(id)
            client_socket.send(bytes(id, "utf-8"))
            os.mkdir("./" + id)

        else:
            # split data
            splited = data.split(b'|')
            id = splited[0].decode('utf-8').strip("\'")
            internal_id = splited[1].decode('utf-8').strip("'")
            flag = splited[2].decode('utf-8')

            # if new user wants to connect
            if flag == "connecting user":
                internal_id = connecting_user(id)
                client_socket.send(bytes(str(internal_id), "utf-8"))

            # if want only info
            elif flag == "receive":

                internal_id = int(internal_id)
                # send info if there is something to send
                if dict[id][int(internal_id)] is not None and len(dict[id][int(internal_id)]) != 0:
                    packet = dict[id][int(internal_id)].pop(0)
                    client_socket.send(bytes(str(len(packet)), 'utf-8'))
                    client_socket.recv(1024)
                    client_socket.send(packet)


            # if want to give and receive info
            else:
                # deal with the new information given
                new_inf(id, internal_id, data)
                # print('Received: ', len(data))

                # analyze changes and update server clone folder
                utils.analyze_receive_info(data, "./" + id)

                # create packets for the other clone users
                if dict[id][int(internal_id)] is not None and len(dict[id][int(internal_id)]) != 0:
                    packet = dict[id][int(internal_id)].pop(0)
                    client_socket.send(packet)

        client_socket.close()
        # print('Client disconnected')


if __name__ == '__main__':
    main()
