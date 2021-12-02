import os
import time

#
# def download_dir(client_socket, id):
#     dir = bytes('', 'utf-8')
#     while len(dir) < 10000000:
#         temp = client_socket.recv(1024)
#         dir = dir + temp
#         if temp == b'' or len(temp) < 1024:
#             break
#
#     os.mkdir(id)
#     f = open(id + ".zip",'wb')
#     f.write(dir)
#     f.close()
#     time.sleep(4)
#     str2 = "bash -c 'unzip -q " + id + ".zip -d "+id +"'"
#     os.system(str2)
#     time.sleep(4)
#     os.remove(id+".zip")
#
# def upload_dir(file_dir, s, id):
#     owd = os.getcwd()
#     os.chdir(file_dir)
#     str2 = "bash -c 'zip -q -r " + id + ".zip " + "./*" + "'"
#     os.system(str2)
#     f = open(id+".zip", 'rb')
#     l = f.read()
#     f.close()
#     time.sleep(4)
#     os.remove(id+".zip")
#     os.chdir(owd)
#     s.send(l)


def receive_info(data, dir_path):

    if (len(data) == 0):
        return

    splited = data.decode('utf-8').split("|")
    num, flag, path = splited[0][:-1], splited[2], os.path.join(dir_path,splited[3])
    other = None
    if (flag == "created" ):
        try:
            other = bytes(splited[4], 'utf-8')
        except:
            pass
        need_created(path, other)
    elif (flag == "deleted"):
        need_delete(path)
    elif (flag == "modified"):
        other = bytes(splited[4], 'utf-8')
        need_modify(path, other)
    elif (flag == "moved"):
        other = bytes(splited[3], 'utf-8')
        need_move(path, os.path.join(dir_path, splited[4]))



def need_delete(path):
    os.remove(path)
    print("deleted:" + path)


def need_move(src_path, dest_path):
    os.replace(src_path, dest_path)
    print("moved from:" + src_path + "to" + dest_path)


def need_created(path, data):
    if data is None:
        os.mkdir(path)
        print("dir created")
    else:
        f = open(path, 'wb')
        f.write(data)
        f.close()
        print("file created")


def need_modify(path, data):
    os.remove(path)
    f = open('path', 'wb')
    f.write(data)
    f.close()
    print("file modify")

