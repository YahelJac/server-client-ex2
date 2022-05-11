import socket
import sys
import time
from watchdog.observers import Observer
from watchdog.events import *
import utils

last_file_created = None
counter = 0
port_number = int(sys.argv[2])
dir_path = sys.argv[3]
ip = sys.argv[1]
observer = Observer()
id = ""
internal_id = ""
stop = False
tempPath = None


def first_connection():
    """
    Responsible on first user connection
    :return:  None
    """

    global id
    global internal_id

    # connection to the server
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((ip, port_number))

    # sending first message  to inform connection
    data = bytes('new connection', 'utf-8')
    s.send(bytes(str(len(data)), 'utf-8'))

    # waiting for id
    s.recv(1024)
    s.send(data)
    data = s.recv(1024)
    print(data.decode('utf-8'))
    id = str(data)[2:-1]
    internal_id = "1"

    # upload all files from dir to server
    list_of_files = utils.upload_dir(dir_path, internal_id, id)
    for packet in list_of_files:
        changes.append(packet)
    s.close()


def connecting_user(id):
    """
    When a user wants to connect to saved dir and loud the dir content and get updates about the dir.
    :param id: exist ID in server
    :return: None
    """
    global internal_id

    # opening socket, informing to server that a new user want to connect exist dir
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((ip, port_number))
    data = bytes(str(id) + "|" + "temp" + "|connecting user" + "|", 'utf-8')

    # sending the length of the message that about to be sent
    s.send(bytes(str(len(data)), 'utf-8'))
    s.recv(1024)
    s.send(data)

    # getting the internal id
    data = s.recv(1024)
    print("my internal id: ", data)
    internal_id = str(data)[2:]
    s.close()


def receive_info(s):
    """
    The client receive info about the dir
    :param s: socket
    :return: None
    """
    global tempPath
    data = bytes('', 'utf-8')
    try:

        # getting the length of the message that about to get in
        len_of_data = s.recv(1024).decode()
        s.send(b'len')

        # getting the message
        while True:
            temp = s.recv(10000)
            data = data + temp
            if len(data) == int(len_of_data):
                break

    except:
        return

    if len(data) == 0:
        return

    # getting info about a file that have been change
    splited = data.split(b'|', maxsplit=4)
    num, flag, path = splited[0][:-1].decode('utf-8'), splited[2].decode('utf-8'), os.path.join(dir_path,
                                                                                                splited[3].decode(
                                                                                                    'utf-8'))
    tempPath = path

    # change the file by the orders from the server
    utils.receive_info(data, dir_path)
    time.sleep(2)

    tempPath = None


def activate_change(src_path, flag, new_path):
    """
    When there is a change, append the change to the changes list.
    :param src_path: path to the file
    :param flag: witch change has occurred
    :param new_path: if the file moved
    :return: None
    """
    res = utils.add_change(src_path, flag, new_path, dir_path, id, internal_id)
    if res:
        changes.append(res)


def on_created(event):
    """
    When a new file hase been created
    :param event: watch dog event
    :return: None
    """
    # take care of watch dog problem
    if tempPath == event.src_path:
        return

    activate_change(event.src_path, event.event_type, None)
    print(f"hey, {event.src_path} has been created!")


def on_deleted(event):
    """
    When a new file hase been deleted
    :param event: watch dog event
    :return: None
    """
    # take care of watch dog problem
    if tempPath in event.src_path:
        return
    activate_change(event.src_path, event.event_type, None)
    print(f"hey, {event.src_path} has been deleted!")

    print(f"what the f**k! Someone deleted {event.src_path}!")


def on_modified(event):
    """
    When a new file hase been modified
    :param event: watch dog event
    :return: None
    """
    # take care of watch dog problem
    if tempPath == event.src_path:
        return
    if isinstance(event, DirModifiedEvent):
        return
    activate_change(event.src_path, event.event_type, None)

    print(f"hey buddy, {event.src_path} has been modified")


def on_moved(event):
    """
    When a new file hase been moved
    :param event: watch dog event
    :return: None
    """
    # take care of watch dog problem
    if tempPath == event.src_path:
        return
    time.sleep(1)
    activate_change(event.src_path, event.event_type, event.dest_path)

    print(f"ok ok ok, someone  yoavyoav moved {event.src_path} to {event.dest_path}")


def connect():
    """
    Connecting to the server to let him Know on new changes if exists or receive info about changes from parallel dir
    :return: None
    """
    # creating a new socket
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((ip, port_number))

    # if there is changes, let the server know
    if changes:
        data = changes.pop(0)

    # if not, ask for changes
    else:
        data = bytes(str(id) + "|" + internal_id + "|receive" + "|", 'utf-8')

    s.send(bytes(str(len(data)), 'utf-8'))
    s.recv(1024)
    s.send(data)
    receive_info(s)
    s.close()


if __name__ == "__main__":
    changes = []
    if len(sys.argv) == 6:
        if not os.path.isdir(dir_path):
            os.makedirs(dir_path)
        connecting_user(sys.argv[5])
        id = sys.argv[5]
    else:
        first_connection()

    # Watch Dog:
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s - %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S')
    tracking_path = dir_path if len(sys.argv) > 1 else '.'
    my_event_handler = LoggingEventHandler()

    my_event_handler.on_created = on_created
    my_event_handler.on_deleted = on_deleted
    my_event_handler.on_modified = on_modified
    my_event_handler.on_moved = on_moved

    observer = Observer(timeout=0.5)
    observer.schedule(my_event_handler, tracking_path, recursive=True)
    observer.start()
    time_to_sleep = int(sys.argv[4])

    # connect to the server every time_to_sleep (getting from the user)
    try:
        while True:
            connect()
            time.sleep(time_to_sleep)
    finally:
        observer.stop()
        observer.join()
