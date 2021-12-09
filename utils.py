import os
import time


# utils function for both client and server

# analyze the info received and calling to the function that should deal with the change
def analyze_receive_info(data, dir_path):
    if len(data) == 0:
        return

    # spilt the data
    splited = data.split(b'|', maxsplit=4)
    num, flag, path = splited[0][:-1].decode('utf-8'), splited[2].decode('utf-8'), os.path.join(dir_path,
                                                                                                splited[3].decode(
                                                                                                    'utf-8'))
    other = None
    # check which case it is
    if (flag == "created"):
        # check if its file or dir
        is_file = False
        try:
            other = splited[4]
            is_file = True
        except:
            pass
        need_created(path, other, is_file)

    elif (flag == "deleted"):
        need_delete(path)

    elif (flag == "modified"):
        other = splited[4]
        need_modify(path, other)

    elif (flag == "moved"):
        need_move(path, os.path.join(dir_path, splited[4].decode('utf-8')))


# deal with deletion change
def need_delete(path):
    # wait until the file is in the correct size-> completed download
    until_wait(path)

    # remove recursively
    if os.path.isdir(path):
        for root, dirs, files in os.walk(path, topdown=False):
            for name in files:
                os.remove(os.path.join(root, name))
            for name in dirs:
                os.rmdir(os.path.join(root, name))
        os.rmdir(path)
        return
    os.remove(path)


# deal with move change
def need_move(src_path, dest_path):
    # wait until the file is in the correct size-> completed download
    until_wait(src_path)
    os.replace(src_path, dest_path)


# deal with creation change
def need_created(path, data, is_file):
    # check if its a dir
    if not is_file:
        os.mkdir(path)
        # print("dir created")
    else:
        f = open(path, 'wb')
        f.write(data)
        f.close()
        # print("file created")


# deal with modify change
def need_modify(path, data):
    until_wait(path)
    os.remove(path)
    f = open(path, 'wb')
    f.close()
    f = open(path, 'wb')
    f.write(data)
    f.close()
    # print("file modify")


# traverse dir files and sub dirs and return list with all paths
def from_dir_to_list(dir):
    res = []
    for root, dirs, files in os.walk(dir, topdown=False):
        # files
        for name in files:
            res.append(os.path.join(root, name)[len(dir) + 1:])
        # dirs
        for name in dirs:
            res.append(os.path.join(root, name)[len(dir) + 1:])
    return list(reversed(res))


# adding change to the queue
def add_change(src_path, flag, new_path, dir_path, id, internal_id):
    send_src_path = src_path[(len(dir_path)) + 1:]
    # in case of move
    if new_path is not None:
        send_new_path = new_path[(len(dir_path)) + 1:]

    # for avoiding duplicate purposes
    if flag == "modified" and not os.path.isfile(src_path):
        return False

    # split data
    delimiter_byte = bytes(("|"), "utf-8")
    protocol = id + "|" + str(internal_id) + "|" + flag + "|" + send_src_path
    protocols_bytes = bytes((str(protocol)), "utf-8")

    # checking which action to do
    if flag == "created":
        if os.path.isdir(src_path):
            pass
        else:
            until_wait(src_path)
            f = open(src_path, 'rb')
            l = f.read()
            f.close()
            protocols_bytes = protocols_bytes + delimiter_byte + l

    elif flag == "deleted":
        pass

    elif flag == "modified":
        until_wait(src_path)
        f = open(src_path, 'rb')
        l = f.read()
        protocols_bytes = protocols_bytes + delimiter_byte + l

    elif flag == "moved":
        new_path_bytes = bytes((str(send_new_path)), "utf-8")
        protocols_bytes = protocols_bytes + delimiter_byte + new_path_bytes

    # return the complete packet ready to be sent
    return protocols_bytes


# wait until the file download completed
# Hoe its work - check if the size stay stable and not grow
def until_wait(path):
    # print(str(path) + " - wating.............")
    copying = True
    size2 = -1
    while copying:
        size = os.path.getsize(path)
        if size == size2:
            break
        else:
            size2 = os.path.getsize(path)
            time.sleep(1)
    #         print(".............")
    # print("file copy has now finished")


# create packets of creation files and dirs for the cases in which:
# existing user connected for the server or new user with non empty dir, connect to the server
def upload_dir(path, internal_id, id):
    dir_path = path

    # create list of files
    list_of_files = from_dir_to_list(dir_path)
    list_of_packets = []

    # create packets of changes
    for file in list_of_files:
        packet = add_change(os.path.join(dir_path, file), 'created', None, dir_path, id, internal_id)
        if packet:
            list_of_packets.append(packet)
    return list_of_packets
