
import socket
import os
import threading
import random
from sys import getsizeof
from tkinter import *
from tkinter import filedialog
from os import listdir
from os.path import isfile, join
# server detail
SERVER_PORT = 10024
SERVER_HOST = '0.0.0.0'
BUFF_SIZE = 1024

# static names
HELLO = str.encode("HELLO")
BYE = str.encode("BYE")
HI = "HI"
INFO = str.encode("INFO")
SEARCH = "SEARCH"


FILE_DIR = os.getcwd() + "/CLIENT_FILES"
NOT_FOUND = "NOT FOUND"
FOUND = "FOUND: "
FILE_NAME = "spider_one"

PEER_DOWNLOADED_FOLDER = "peers_downloaded"
IMAGES_FOLDER = os.getcwd() + "/" + "CLIENT_FILES"

FILE_MAP = {}

SEARCH_MAP = {}


host_ip = "127.0.0.1"
host_port_number = 0

specific_for_peer = ""


def break_connection(s, is_good_response):
    if not is_good_response:
        print("CONNECTION CLOSED DUE TO ERROR")
    s.close()


def peer_handle(s):
    s.listen()
    # waiting for a new peer
    try:
        while True:
            # conn is somehow socket from client
            # addre - tuple of [IP, PORT]
            conn, addr = s.accept()
            download_request = conn.recv(BUFF_SIZE)
            download_request = download_request.decode("utf-8")
            variable_download_len = len("DOWNLOAD: ")
            # details of the requested file for download
            details_raw = download_request[variable_download_len:]
            details = details_raw.split(",")
            file_name, file_type, file_size = details
            print(FILE_MAP)
            was_found = False

            if file_name in FILE_MAP:
                candidates = FILE_MAP[file_name]
                for candidate in candidates:
                    if candidate == file_type:
                        image_to_send = f"{file_name}.{file_type}"
                        was_found = True
                        break

            if was_found:
                file_dir = f"{IMAGES_FOLDER}/{image_to_send}"
                f = open(file_dir, 'rb')
                data = f.read(BUFF_SIZE)
                ind = getsizeof(data)
                while(data):
                    conn.send(data)
                    data = f.read(BUFF_SIZE)
                    ind += getsizeof(data)
                    
                f.close()
            else:
                print("client: request file from peer was not found")
            # conn.send(b"FINISH")

        conn.close()
    except:
        print("client: good bye user")



# FileName, type, size
# <file type, file size, file last modified date (DD/MM/YY), IP address, port number>
# file_name, file_type, file_size = first_record.split()
# expecting format of file information for server
'''
    format: filetype/filename/filesize,...
    note: filesize in bytes
'''


def send_files(s, peer_details, files_dirs):
    files_str = ""
    for index, file_dir in enumerate(files_dirs):
        file_size = os.stat(file_dir).st_size
        specifics = file_dir.split("/")[-1]
        file_name, file_type = specifics.split(".")
        files_str += f"{file_type}/{file_name}/{file_size}/{peer_details[0]}/{peer_details[1]}"
        if not index == len(files_dirs) - 1:
            files_str += ","

    if files_str == "":
        files_str = "[]"

    print(f"client: sending {files_str}")
    files_str = str.encode(files_str)
    s.sendall(files_str)


# when a client clicks on exit button
def leave_system(s, peers):
    s.sendall(BYE)
    break_connection(s, True)
    break_connection(peers, True)


def setup_files():
    global specific_for_peer
    # creating folder for future downloaded images
    path_of_downloaded_folders = os.getcwd() + "/" + PEER_DOWNLOADED_FOLDER

    if not os.path.isdir(path_of_downloaded_folders):
        os.mkdir(path_of_downloaded_folders)

    specific_for_peer = f"{path_of_downloaded_folders}/{host_port_number}"

    if not os.path.isdir(specific_for_peer):
        os.mkdir(specific_for_peer)

    # folder from which we take five random images
    image_number_to_take = random.randint(2, 6)
    global image_names
    image_names = os.listdir(IMAGES_FOLDER)
    image_paths_to_take = []
    for image in image_names:
        choice = random.randint(1, len(image_names) + 1)

        if choice <= image_number_to_take:

            image_paths_to_take.append(f"{IMAGES_FOLDER}/{image}")
            dwnl_list.insert(END, image)
            # saving to client map of files
            image_specifics = image.split(".")
            image_name = image_specifics[0]
            image_type = image_specifics[1]

            if not image_name in FILE_MAP:
                FILE_MAP[image_name] = []

            FILE_MAP[image_name].append(image_type)
    
    return image_paths_to_take


def main_thread():
    global host_port_number
    # one socker for server connection
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # one socker for listenining other peers
    peers = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    peers.bind((host_ip, 0))

    # for peers handling
    peers_specifics = peers.getsockname()
    # port number requiered for managing other peers
    host_port_number = peers_specifics[1]
    # create folder for future downloaded images
    # file selection from shared folder for automation sending to server
    global dwnl_list
    dwnl_list = Listbox(top)
    dwnl_list.place(x='450', y='80', width='150', height='300')
    image_paths_to_take = setup_files()

    try:
        threading.Thread(target=peer_handle, args=(peers,)).start()
        
        s.connect((SERVER_HOST, SERVER_PORT))
        s.sendall(HELLO)
        # blocking function
        data = s.recv(BUFF_SIZE)
        data = data.decode("utf-8")
        print(f"client first response: {data}")

        def download(): 
            global current,host_port_number,FILE_MAP
            
            try:
                current = file_list.get(file_list.curselection())
                
                if (not current in SEARCH_MAP):
                    print(f"client: the selected item  {current} is not valid for search")
                else:
                    
                    entry, file_type, file_size, last_modified, ip_address, port_number = SEARCH_MAP[current]

                    client_file_versions = []

                    if entry in FILE_MAP:
                        client_file_types = FILE_MAP[entry]
                        for client_file_type in client_file_types:
                            client_file_versions.append(f"{entry}.{client_file_type}")

                    # print(f"FILE_MAP : {FILE_MAP}")
                    # print(f"client_file_versions: {client_file_versions}")
                    print(file_list.get(file_list.curselection()))

                    if int(port_number) == host_port_number or f"{entry}.{file_type}" in client_file_versions:
                        print(f"client: client has this file already {entry}")
                        warning["text"] = "client has this file already"
                        warning["fg"] = 'red'
                        return
                    
                    # recently_downloaded = False

                    # if entry in FILE_MAP:
                    #     print("GOOOO")
                    #     if file_type in FILE_MAP[entry]:
                    #         print("GOOOORRR")
                    #         recently_downloaded = True
                    #         print("client: recently downloaded")
                    #         warning["text"] = f'you have recently downloaded it'
                    #         warning["fg"] = 'red'
                    
                    # if not recently_downloaded:

                    download_message = str.encode(f"DOWNLOAD: {entry},{file_type},{file_size}")


                    # starting downloading a file
                    peer_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    try:
                        peer_socket.connect((ip_address, int(port_number)))
                    except:
                        print("client: peer already has gone")
                        warning["text"] = f'peer already has gone, click search again'
                        warning["fg"] = 'red'
                        raise Exception("no peer")

                    peer_socket.sendall(download_message)
                    
                    path_to_file = specific_for_peer + \
                        "/" + f"{entry}.{file_type}"
                    
                    f = open(path_to_file, 'wb')
                    
                    data_chunk = peer_socket.recv(BUFF_SIZE)
                    index = getsizeof(data_chunk)
                    # downloading in chunks
                    while(data_chunk):
                        if len(data_chunk) < 1024:
                            print("client: finished downloading")
                            break
                        index += getsizeof(data_chunk)
                        f.write(data_chunk)
                        data_chunk = peer_socket.recv(BUFF_SIZE)

                    warning["text"] = f'succesfully downloaded, check file in peers_downloaded/{host_port_number}'
                    warning["fg"] = 'green'
                    dwnl_list.insert(END, f"{entry}.{file_type} (server does not know about this file)")
                    FILE_MAP[entry] = [file_type]
                    f.close()
                        
            except Exception as e:
                pass
                # if not e == "no peer":
                #     print("client: can not download anything")
                #     warning["text"] = f'can not download anything, click on the searched item'
                #     warning["fg"] = 'red'

        def delete_window():
            try:
                top.destroy()
                print("DESTROYED")
                leave_system(s, peers)
            except:
                print("client: could not be destroyed???")

        def search():

            global entry, SEARCH_MAP,specific_for_peer,FILE_MAP
            entry = search_box.get()
            STATIC_FILE = str.encode(f"{SEARCH}: {entry}")
            
            # updating the searching map before further searching of new element
            SEARCH_MAP = {}
            
            file_list.delete(0, END)

            # no need for static search
            # for item in all_files:
            #     if entry.lower() in item.lower():
            #         file_list.insert(END, item)

            print(STATIC_FILE)
            s.sendall(STATIC_FILE)
            respone_on_peers = s.recv(BUFF_SIZE)
            print(respone_on_peers)
            respone_on_peers = respone_on_peers.decode("utf-8")

            if respone_on_peers == NOT_FOUND:
                warning["text"] = f"{respone_on_peers} in other peers for {entry}\nYou can type the whole file name"
                warning["fg"] = 'red'
                print("client: server did not find a file")
            else:
                records_raw = respone_on_peers[len(FOUND):]
                records = records_raw.split("|")
                warning["text"] = f"{len(records)} files were found in your search"
                warning["fg"] = 'green'

                for record in records:
                    record = record[1:len(record) - 1]

                    file_type, file_size, last_modified, ip_address, port_number = record.split(",")

                    # print(f"{port_number} - {host_port_number}")

                    file_list.insert(END, f"{entry}.{file_type}")
                    SEARCH_MAP[f"{entry}.{file_type}"] = (entry, file_type, file_size, last_modified, ip_address, port_number)


                #     if int(port_number) == host_port_number or f"{entry}.{file_type}" in client_file_versions:
                #         print(f"client: client has this file already {entry}")
                #         continue
                #     else:
                #         found = True
                #         # searched elements are recorded to the MAP
                #         SEARCH_MAP[f"{entry}.{file_type}"] = (entry, file_type, file_size, last_modified, ip_address, port_number)
                
                # if not found:
                #     file_list.insert(END, f"This file already ")

          
            # break_connection(s, True)

        # mypath = '/home/zaripovasb/Desktop/hw-cs33/images'
        # onlyfiles = [f for f in listdir(mypath) if isfile(join(mypath, f))]
        # print('---')

        top.protocol('WM_DELETE_WINDOW', delete_window)
        file_list = Listbox(top)
        file_list.place(x='50', y='80', width='300', height='300')
        # for file in image_names:
        #     file_list.insert(END, file)
        # file_list.bind('<<ListboxSelect>>', on_selection)

        # mypath = '/home/zaripovasb/Desktop/hw-cs33/images'
        # onlyfiles = [f for f in listdir(mypath) if isfile(join(mypath, f))]
        top.title('FileTracker System')
        top.configure(width=650, height=600)

        warning = Label(top, text = "")
        warning.place(x='100', y='400', width='450', height='200')

        filename = Label(top, text="File name:")
        filename.place(x='50', y='50', width='80', height='20')
        peername = Label(top, text="Peer Files")
        peername.place(x='450', y='50', width='80', height='20')
        global search_box
        search_box = Entry(top)

        search_box.place(x='130', y='50', width='215', height='20')
        search_button = Button(
            top, text="Search", command=search)
        search_button.place(x='360', y='50', width='80', height='20')
        # dwnl_box = Entry(top)
        # dwnl_box.place(x='250', y='430', width='130', height='50')
        dwnl_button = Button(top, text="Download", command = download)
        dwnl_button.place(x='200', y='400', width='130', height='20')
        # dwnl_button.bind('<Button-1>', peer_handle(s))
        # message = Text(dwnl_box)
        # message.pack()
       
        scrollbar = Scrollbar(file_list, orient="vertical")
        scrollbar.config(command=file_list.yview)
        scrollbar.pack(side=RIGHT, fill=Y)
        file_list.config(yscrollcommand=scrollbar.set)
        all_files = file_list.get(0, END)
      
        # dwnl_list.bind('<<ListboxSelect>>', on_selection)
        scroll2 = Scrollbar(dwnl_list, orient="vertical")
        scroll2.config(command=dwnl_list.yview)
        scroll2.pack(side=RIGHT, fill=Y)
        # dwnl_list.config(yscrollcommand=scroll2.set)

        if data == HI:
            send_files(s, peers_specifics, files_dirs=image_paths_to_take) 
            decision = s.recv(BUFF_SIZE)
            decision = decision.decode("utf-8")
            if (decision == "UNACCEPTED"):
                print("client: I send nothing, I am not fair, launch me again maybe I will send something next time")
                top.destroy()
                break_connection(s, TRUE)
                break_connection(peers, TRUE)
        else:
            print("client: NOT HI")
            top.destroy()
            break_connection(s, TRUE)
            break_connection(peers, TRUE)

    except Exception as e:
        print("No server detected")
        top.destroy()
        break_connection(s, True)
        break_connection(peers, True)


if __name__ == '__main__':
    top = Tk()
    main_thread()
    # filez = tkFileDialog.askopenfilenames(parent=top, title='Choose a file')
    # print top.tk.splitlist(filez)
    # search_box = Entry(top)
    # search_box.pack()

    # top.filename = filedialog.askopenfilenames(
    #     initialdir="/images", title="Select file", filetypes=(("jpeg files", "*.jpg"), ("all files", "*.*")))
    top.mainloop()
