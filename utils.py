import os
import time
import sys


def receive_info(data, dir_path):
    """
    when a new change hase arrived, call to the function that responsible for that type of change
    :param data: the info
    :param dir_path: the path for the dir
    :return:
    """
    if len(data) == 0:
        return

    splited = data.split(b'|', maxsplit=4)
    num, flag, path = splited[0][:-1].decode('utf-8'), splited[2].decode('utf-8'), os.path.join(dir_path,
                                                                                                splited[3].decode(
                                                                                                    'utf-8'))
    other = None
    if flag == "created":
        is_file = False
        try:
            other = splited[4]
            is_file = True
        except:
            pass
        need_created(path, other, is_file)

    elif flag == "deleted":
        need_delete(path)

    elif flag == "modified":
        other = splited[4]
        need_modify(path, other)

    elif flag == "moved":
        other = splited[3]
        need_move(path, os.path.join(dir_path, splited[4].decode('utf-8')))


def need_delete(path):
    """
    take care of deleting file
    :param path: path to file
    :return:
    """
    until_wait(path)
    if os.path.isdir(path):
        for root, dirs, files in os.walk(path, topdown=False):
            for name in files:
                os.remove(os.path.join(root, name))

            for name in dirs:
                os.rmdir(os.path.join(root, name))
        os.rmdir(path)
        return
    os.remove(path)


def need_move(src_path, dest_path):
    """
    take care of moving file
    :param src_path: path to file
    :param dest_path: path to the new place
    :return:
    """
    until_wait(src_path)
    os.replace(src_path, dest_path)
    print("moved from:" + src_path + "to" + dest_path)


def need_created(path, data, is_file):
    """
    take care of creating file
    :param path: path to dir
    :param data: the data in the file
    :param is_file: bool, if tile True ,if it is then dir False
    :return:
    """
    if not is_file:
        os.mkdir(path)
        print("dir created")
    else:
        f = open(path, 'wb')
        f.write(data)
        f.close()
        print("file created")


def need_modify(path, data):
    """
    take care of modifying file
    :param path: path to file
    :param data: new data
    :return:
    """
    until_wait(path)
    os.remove(path)
    f = open(path, 'wb')
    f.close()
    f = open(path, 'wb')
    f.write(data)
    f.close()
    print("file modify")


def from_dir_to_list(dir):
    """
    making a list of all the files than in a dir.
    :param dir: path to dir
    :return:
    """
    res = []
    for root, dirs, files in os.walk(dir, topdown=False):
        for name in files:
            res.append(os.path.join(root, name)[len(dir) + 1:])

        for name in dirs:
            res.append(os.path.join(root, name)[len(dir) + 1:])
    return list(reversed(res))


def add_change(src_path, flag, new_path, dir_path, id, internal_id):
    """
    creating the protocol in bites when ever a new change hase been happened.
    :param src_path: path to the file
    :param flag: with change happened
    :param new_path: if there is, new path for file
    :param dir_path: path to dir
    :param id: the id of the dir
    :param internal_id: the id of user that use the dir
    :return: the info in the protocol
    """
    send_src_path = src_path[(len(dir_path)) + 1:]
    if new_path is not None:
        send_new_path = new_path[(len(dir_path)) + 1:]

    if flag == "modified" and not os.path.isfile(src_path):
        return False

    delimiter_byte = bytes(("|"), "utf-8")

    protocol = id + "|" + str(internal_id) + "|" + flag + "|" + send_src_path
    protocols_bytes = bytes((str(protocol)), "utf-8")

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

    return protocols_bytes


def until_wait(path):
    """
    wait until the change finish
    :param path: path to file
    :return:
    """
    print(str(path) + " - wating.............")
    copying = True
    size2 = -1
    while copying:
        size = os.path.getsize(path)
        if size == size2:
            break
        else:
            size2 = os.path.getsize(path)
            time.sleep(1)
            print(".............")
    print("file copy has now finished")


def upload_dir(path, internal_id, id):
    """
    when a new dir has connected, this function pass all the files and creat a list of all the changes to send to a new
    dir
    :param path: path to dir
    :param internal_id: user id
    :param id: dir id
    :return:
    """
    dir_path = path
    list_of_files = from_dir_to_list(dir_path)
    list_of_packets = []
    for file in list_of_files:
        packet = add_change(os.path.join(dir_path, file), 'created', None, dir_path, id, internal_id)
        if packet:
            list_of_packets.append(packet)

    return list_of_packets
