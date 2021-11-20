import os
import time


def download_dir(client_socket, id):
    dir = bytes('', 'utf-8')
    while len(dir) < 10000000:
        temp = client_socket.recv(1024)
        dir = dir + temp
        if temp == b'' or len(temp) < 1024:
            break

    os.mkdir(id)
    f = open(id + ".zip",'wb')
    f.write(dir)
    f.close()
    time.sleep(4)
    str2 = "bash -c 'unzip -q " + id + ".zip -d "+id +"'"
    os.system(str2)
    time.sleep(4)
    os.remove(id+".zip")

def upload_dir(file_dir, s, id):
    owd = os.getcwd()
    os.chdir(file_dir)
    str2 = "bash -c 'zip -q -r " + id + ".zip " + "./*" + "'"
    os.system(str2)
    f = open(id+".zip", 'rb')
    l = f.read()
    f.close()
    time.sleep(4)
    os.remove(id+".zip")
    os.chdir(owd)
    s.send(l)