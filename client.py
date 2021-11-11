import socket


# s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# s.connect(('127.0.0.1', 12345))
# s.send(b'Yahel Jacoby 208384420 Yoav Tamir 316554724')
# data = s.recv(100)
# print("Server sent: ", data)
# s.close()

import sys
import time
import logging
from watchdog.observers import Observer
from watchdog.events import LoggingEventHandler

id= ""

def first_connection():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(('127.0.0.1', 12345))
    s.send(b'new connection')
    data = s.recv(100)
    print("my id: ", data)
    id = str(data)
    s.close()


def push(path, flag, new_path):


    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(('127.0.0.1', 12345))
    #protocol = |id|flag|path|new_path(?)|binaryfile(?)

    delimiter_byte = bytes(("|"), "utf-8")

    protocol = id + "|" + flag + "|" + path
    protocols_bytes = bytes((str(protocol)), "utf-8")

    if flag == "created":
        f = open(path,'rb')
        l = f.read()
        protocols_bytes=protocols_bytes + delimiter_byte + l

    if flag == "delete":
        pass

    if flag == "on_modified":
        f = open(path, 'rb')
        l = f.read()
        protocols_bytes = protocols_bytes + delimiter_byte + l

    if flag == "move":
        new_path_bytes = bytes((str(new_path)), "utf-8")
        protocols_bytes = protocols_bytes + delimiter_byte + new_path_bytes

    # while len(protocols_bytes)<1024:
    #     temp = s.recv(6)

    s.send(protocols_bytes)
    s.close()

    # data = s.recv(1024)
    # print("Server sent: ", data)
    # s.close()



def on_created(event):
    push(event.src_path,event.event_type,None)
    # push:
    #   notify create
    #   send file name and path
    #   send file to server

    # pull:
    #   received file , name and path
    #   save by its name in the path



    print(f"hey, {event.src_path} has been created!")

def on_deleted(event):
    push(event.src_path,event.event_type,None)

    # push:
    #   notify delete
    #   send file name and path

    # pull:
    #   received name and path
    #   delete by its name in the path
    print(f"what the f**k! Someone deleted {event.src_path}!")

def on_modified(event):
    push(event.src_path,event.event_type,None)

    # push:
    #   notify modify
    #   send file
    #   send file name and path

    # pull:
    #   received file name and path
    #   delete old file by its name in the path
    #   save new file in path

    print(f"hey buddy, {event.src_path} has been modified")

def on_moved(event):
    print(f"hey buddy, {event.src_path} has been modified")

    # push:
    #   notify move
    #   send old file name and path
    #   send new file name and path

    # pull:
    #   received old file name and path
    #   received new file name and path
    #   change file location;lk

    print(f"ok ok ok, someone moved {event.src_path} to {event.dest_path}")





if __name__ == "__main__":


    if id == "":
        first_connection()

    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s - %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S')
    path = sys.argv[1] if len(sys.argv) > 1 else '.'
    my_event_handler = LoggingEventHandler()

    # my_event_handler.on_created=on_created
    # my_event_handler.on_deleted=on_deleted
    # my_event_handler.on_modified=on_modified
    # my_event_handler.on_moved=on_moved


    observer = Observer()
    observer.schedule(my_event_handler, path, recursive=True)
    observer.start()
    try:
        while True:
            ###############
        # ask for changes()
        # apply changes
            ###############
            time.sleep(1)
    finally:
        observer.stop()
        observer.join()



