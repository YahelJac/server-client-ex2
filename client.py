import socket
import sys
import time
from watchdog.observers import Observer
from watchdog.events import *
import utils

# program variables
changes = []
port_number = int(sys.argv[2])
dir_path = sys.argv[3]
ip = sys.argv[1]
observer = Observer()
id = ""
internal_id = ""
tempPath = None


# first connection function - in case it is a new user
def first_connection():
    global id
    global internal_id
    # connecting to server ask for id
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((ip, port_number))

    # sending request for generate id key
    data = bytes('new connection', 'utf-8')
    s.send(bytes(str(len(data)), 'utf-8'))

    # receive id
    s.recv(1024)
    s.send(data)
    data = s.recv(1024)
    print(data.decode('utf-8'))
    id = str(data)[2:-1]

    # set internal_id
    internal_id = "1"

    # generate list of files in the tracking folder
    list_of_files = utils.upload_dir(dir_path, internal_id, id)

    # for each folder or file, creating packet
    for packet in list_of_files:
        changes.append(packet)
    s.close()


# connect another computer to an existing user
def connecting_user(id):
    global internal_id

    # connection to the server
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((ip, port_number))

    # send request for an internal_id
    data = bytes(str(id) + "|" + "temp" + "|connecting user" + "|", 'utf-8')
    s.send(bytes(str(len(data)), 'utf-8'))
    s.recv(1024)
    s.send(data)
    data = s.recv(1024)
    # print("my internal id: ", data)
    internal_id = str(data)[2:]
    s.close()


# receive info from the server - get changes that happened
def receive_info(s):
    global tempPath
    # receive data from the server
    data = bytes('', 'utf-8')
    try:
        lenOfData = s.recv(1024).decode()
        s.send(b'len')
        while True:
            temp = s.recv(10000)
            data = data + temp
            if len(data) == int(lenOfData):
                break
    except:
        return

    # return if there nothing to update
    if (len(data) == 0):
        return

    # split the data
    splited = data.split(b'|', maxsplit=4)
    num, flag, path = splited[0][:-1].decode('utf-8'), splited[2].decode('utf-8'), os.path.join(dir_path,
                                                                                                splited[3].decode(
                                                                                                    'utf-8'))
    # mark last path visited for duplicates avoiding
    tempPath = path
    # analyze the data received
    utils.analyze_receive_info(data, dir_path)
    time.sleep(2)
    # todo check sleep location
    tempPath = None


# create chang packet, letting know something changed
def activate_change(src_path, flag, new_path):
    res = utils.add_change(src_path, flag, new_path, dir_path, id, internal_id)
    if res:
        changes.append(res)


# handle file\dir created after watchdoog noticed.
def on_created(event):
    if tempPath == event.src_path:
        return
    activate_change(event.src_path, event.event_type, None)
    # print(f"{event.src_path} has been created!")


# handle file\dir deleted after watchdoog noticed.
def on_deleted(event):
    if tempPath and tempPath in event.src_path:
        return
    activate_change(event.src_path, event.event_type, None)
    # print(f"{event.src_path} has been deleted!")


# handle file\dir modified after watchdoog noticed.
def on_modified(event):
    if tempPath == event.src_path:
        return
    if isinstance(event, DirModifiedEvent):
        return
    activate_change(event.src_path, event.event_type, None)
    # print(f"{event.src_path} has been modified")


# handle file\dir moved after watchdoog noticed.
def on_moved(event):
    if tempPath == event.src_path:
        return
    time.sleep(1)
    activate_change(event.src_path, event.event_type, event.dest_path)
    # print(f" moved {event.src_path} to {event.dest_path}")


# connect to server for asking and giving changes
def connect():
    # connecting the server
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((ip, port_number))
    # checking if there is something to update
    if changes:
        data = changes.pop(0)
    else:  # send request for updates from the server
        data = bytes(str(id) + "|" + internal_id + "|receive" + "|", 'utf-8')
    s.send(bytes(str(len(data)), 'utf-8'))
    s.recv(1024)
    s.send(data)

    # dealing with the information received
    receive_info(s)
    s.close()


# main function, run the program
def main():
    global id
    # watchdog start
    if len(sys.argv) == 6:
        if not os.path.isdir(dir_path):
            os.makedirs(dir_path)
        connecting_user(sys.argv[5])
        id = sys.argv[5]
    else:
        first_connection()

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

    # setting sleep interval
    time_to_sleep = int(sys.argv[4])
    try:
        # main loop - connect with the server switch information and sleep and so on
        while True:
            connect()
            time.sleep(time_to_sleep)
    finally:
        observer.stop()
        observer.join()


if __name__ == "__main__":
    main()
