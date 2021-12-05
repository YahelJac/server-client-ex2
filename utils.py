import os

import time
import sys


def receive_info(data, dir_path):
    if (len(data) == 0):
        return

    splited = data.split(b'|', maxsplit = 4)
    num, flag, path = splited[0][:-1].decode('utf-8'), splited[2].decode('utf-8'), os.path.join(dir_path, splited[3].decode('utf-8'))
    other = None
    if (flag == "created"):
        is_file = False
        try:
            other = splited[4]
            is_file = True
        except:
            pass
        need_created(path, other,is_file)
    elif (flag == "deleted"):
        need_delete(path)
    elif (flag == "modified"):
        other = splited[4]
        need_modify(path, other)
    elif (flag == "moved"):
        other = splited[3]
        need_move(path, os.path.join(dir_path, splited[4]))


def need_delete(path):
    os.remove(path)
    print("deleted:" + path)


def need_move(src_path, dest_path):
    os.replace(src_path, dest_path)
    print("moved from:" + src_path + "to" + dest_path)


def need_created(path, data,is_file):
    if not is_file:
        os.mkdir(path)
        print("dir created")
    else:
        f = open(path, 'wb')
        f.write(data)
        f.close()
        print("file created")


def need_modify(path, data):
    os.remove(path)
    f = open(path, 'wb')
    f.close()
    f = open(path, 'wb')
    f.write(data)
    f.close()
    print("file modify")

def from_dir_to_list(dir):
    res = []
    for root, dirs, files in os.walk(dir, topdown=False):
        for name in files:
            res.append(os.path.join(root, name)[len(dir) + 1:])

        for name in dirs:
            res.append(os.path.join(root, name)[len(dir) + 1:])
    return list(reversed(res))



def add_change(src_path, flag, new_path,dir_path,id,internal_id):
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
