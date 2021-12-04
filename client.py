import socket

import sys
import time
from watchdog.observers import Observer
from os import path
from watchdog.events import *

import utils

port_number = int(sys.argv[2])
dir_path = sys.argv[3]
ip = sys.argv[1]
observer = Observer()
id = ""
internal_id = ""
stop = False


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
    s.close()


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
    global just_updated
    global stop
    data = s.recv(1024)
    if (len(data) == 0):
        return

    stop = True
    just_updated = True
    utils.receive_info(data, dir_path)
    stop = False


def activate_change(src_path, flag, new_path):
    res = utils.add_change(src_path, flag, new_path, dir_path,id, internal_id)
    if res:
        changes.append(res)

def on_created(event):
    if stop:
        return
    activate_change(event.src_path, event.event_type, None)

    print(f"hey, {event.src_path} has been created!")


def on_deleted(event):
    if stop:
        return
    activate_change(event.src_path, event.event_type, None)
    print(f"hey, {event.src_path} has been deleted!")

    print(f"what the f**k! Someone deleted {event.src_path}!")


def on_modified(event):
    if stop:
        return
    if isinstance(event, DirModifiedEvent):
        return

    activate_change(event.src_path, event.event_type, None)

    print(f"hey buddy, {event.src_path} has been modified")


def on_moved(event):
    if stop:
        return
    activate_change(event.src_path, event.event_type, event.dest_path)

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
