import socket

# s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# s.connect(('127.0.0.1', 12345))
# s.send(b'Yahel Jacoby 208384420 Yoav Tamir 316554724')
# data = s.recv(100)
# print("Server sent: ", data)
# s.close()
import os
import sys
import time
import logging
from watchdog.observers import Observer
from watchdog.events import LoggingEventHandler
from os import path
from watchdog.events import *

import utils

just_updated = False
port_number = int(sys.argv[2])
dir_path = sys.argv[3]
ip = sys.argv[1]
observer = Observer()
id = ""
internal_id = ""


def first_connection():
    global id
    global internal_id
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((ip, port_number))
    data = bytes('new connection', 'utf-8')
    s.send(data)
    data = s.recv(1024)
    print("my id: ", data)
    id = str(data)[2:-1]
    internal_id = "1"
    ###################################
    #save to zip
    # owd = os.getcwd()
    # os.chdir(dir_path)
    # str2 = "bash -c 'zip -q -r " + id + ".zip " + "./*" + "'"
    # os.system(str2)
    # f = open(id+".zip", 'rb')
    # l = f.read()
    # f.close()
    # os.remove(id+".zip")
    # os.chdir(owd)
    # s.send(l)
    s.close()





    ###################################




def connecting_user(id):
    global internal_id
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((ip, port_number))
    data = bytes(str(id) + "|" + "temp" + "|connecting user" + "|", 'utf-8')
    s.send(data)
    data = s.recv(1024)
    print("my internal id: ", data)
    internal_id = str(data)[2:]
    s.close()


def receive_info(s):
    global observer
    global just_updated
    observer.stop()
    data = s.recv(1024)
    if (len(data) == 0):
        observer = Observer()
        observer.schedule(my_event_handler, tracking_path, recursive=True)
        observer.start()
        return
    just_updated = True
    utils.receive_info(data,dir_path)
    observer = Observer()
    observer.schedule(my_event_handler, tracking_path, recursive=True)
    observer.start()

def add_change(src_path, flag, new_path):
    # s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # s.connect(('127.0.0.1', 12345))
    # protocol = |id|flag|path|new_path(?)|binaryfile(?)
    send_src_path = src_path[(len(dir_path))+1:]
    if new_path is not None:
        send_new_path = new_path[(len(dir_path)):]

    if flag == "modified" and not path.isfile(src_path):
        return False

    global just_updated
    # if just_updated:
    #     just_updated = False
    #     return
    delimiter_byte = bytes(("|"), "utf-8")

    protocol = id + "|" + internal_id + "|" + flag + "|" + send_src_path
    protocols_bytes = bytes((str(protocol)), "utf-8")

    if flag == "created":
        if path.isdir(src_path):
            pass
        else:

            f = open(src_path, 'rb')
            l = f.read()
            f.close()
            protocols_bytes = protocols_bytes + delimiter_byte + l

    if flag == "deleted":
        pass

    if flag == "modified":
        f = open(src_path, 'rb')
        l = f.read()
        protocols_bytes = protocols_bytes + delimiter_byte + l

    if flag == "moved":
        new_path_bytes = bytes((str(send_new_path)), "utf-8")
        protocols_bytes = protocols_bytes + delimiter_byte + new_path_bytes

    changes.append(protocols_bytes)
    # s.send(protocols_bytes)
    # receive_info(s)
    # s.close()


def on_created(event):
    add_change(event.src_path, event.event_type, None)

    print(f"hey, {event.src_path} has been created!")


def on_deleted(event):
    add_change(event.src_path, event.event_type, None)
    print(f"hey, {event.src_path} has been deleted!")



    print(f"what the f**k! Someone deleted {event.src_path}!")


def on_modified(event):
    if isinstance(event,DirModifiedEvent):
        return
    add_change(event.src_path, event.event_type, None)



    print(f"hey buddy, {event.src_path} has been modified")


def on_moved(event):
    add_change(event.src_path, event.event_type, event.dest_path)

    print(f"ok ok ok, someone  yoavyoav moved {event.src_path} to {event.dest_path}")


def connect():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((ip, port_number))
    if changes:
        data = changes.pop(0)
    else:
        data = bytes(str(id) + "|" + internal_id + "|receive" + "|", 'utf-8')
    s.send(data)
    receive_info(s)
    s.close()


if __name__ == "__main__":
    if len(sys.argv) == 6:
        connecting_user(sys.argv[5])
        id = sys.argv[5]
    else:
        first_connection()

    changes = []


    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s - %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S')
    tracking_path = dir_path if len(sys.argv) > 1 else '.'
    my_event_handler = LoggingEventHandler()

    my_event_handler.on_created = on_created
    my_event_handler.on_deleted = on_deleted
    my_event_handler.on_modified = on_modified
    my_event_handler.on_moved = on_moved

    observer = Observer()
    observer.schedule(my_event_handler, tracking_path, recursive=True)
    observer.start()
    time_to_sleep = int(sys.argv[4])

    try:
        while True:
            connect()

            time.sleep(time_to_sleep)
    finally:
        observer.stop()
        observer.join()
