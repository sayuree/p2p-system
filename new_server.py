

import socket 
import os 
import threading
from datetime import datetime


ONLINE_CLIENTS = {}
MAP = {}
PEERS_FILES = {}
SERVER_PORT = 10024
SERVER_HOST = '0.0.0.0'
BUFF_SIZE = 1024

HELLO = str.encode("HELLO")
HI = str.encode("HI")
SEARCH = "SEARCH: "

def search_in_map(file_name):
    print(f"server MAP: {MAP}")
    if file_name in MAP:
        candidates = MAP[file_name]
        candidates_str = ""
        for index, candidate in enumerate(candidates):
            candidates_str += candidate
            if not index == len(candidates) - 1:
                candidates_str += '|'
            
        return f"FOUND: {candidates_str}"
    return "NOT FOUND"


def add_to_map(client_file_details, addr):
    print(f"server: {client_file_details}")
    # client attributes
    try:
        last_modified = datetime.today().strftime('%d/%m/%Y')
        file_type,file_name,file_size,ip_address,port_number = client_file_details
        if not file_name in MAP: 
            MAP[file_name] = []
        MAP[file_name].append(f"<{file_type},{file_size},{last_modified},{ip_address},{port_number}>")
        if not addr in PEERS_FILES:
            PEERS_FILES[addr] = []
        PEERS_FILES[addr].append((file_name, file_type, ip_address, port_number))
    except Exception as e:
        print(e)
        raise Exception("WRONG DATA FORMAT")

def client_handle(conn, addr):
    global MAP
     # first message is expected to be file names
    data = conn.recv(BUFF_SIZE)
    data = data.decode('utf-8')

    if data == "HELLO":
        print("server: got HELLO, sending HI") 
        conn.send(HI)
    else:
        print(f"server: UNEXPECTED GREETINGS FROM CLIENT {data}")
        conn.close()
        return

    # expecting format of file information from client
    '''
        format: filetype/filename/filesize,...
        note: filesize in bytes
    '''
    
    client_files_raw = conn.recv(BUFF_SIZE)
    client_files = client_files_raw.decode('utf-8')
    if not client_files == "[]":
        conn.send(str.encode("ACCEPTED"))
        if "," in client_files:
            client_files = client_files.split(",")
        else:
            client_files = [client_files]
        # adding client files to the map
        print(f'server: file data {client_files}')

        try:
            for client_file_details in client_files:
                add_to_map(client_file_details.split("/"), addr)
        except Exception as err:
            print(f"server: {err}")
            conn.close()
            return

        ONLINE_CLIENTS[conn.fileno()] = conn

        while True: 
            # other messages of the client
            message = conn.recv(BUFF_SIZE)
            message = message.decode('utf-8')

            # if bye, simple terminate
            if message == "BYE":
                print(f"server: BYE BYE client")
                break
            
            if len(message) > 0:
                print(f"server: {message}")
                # if message is the file name request
                # sending the search result to a client
                # already decoded
                file_name = message.split(" ")[1]
                print(f"server: file request {file_name}")
                search_result = search_in_map(file_name)
                print(f"server: search result {search_result}")
                search_result = str.encode(search_result)
                conn.send(search_result)


        # deleting client from system 
        del ONLINE_CLIENTS[conn.fileno()]
        # deleting client files
        # deleting [('spider_seven', 'png', '127.0.0.1', '61390')]
        peer_files = PEERS_FILES[addr]
        print(f"server: deleting peer files {peer_files}")
        for peer_file in peer_files:
            # PEERS_FILES format of value (file_name, file_type, ip_address, port_number)
            # MAP format of value <{file_type},{file_size},{last_modified},{ip_address},{port_number}>
            file_name,file_type,ip_address,port_number = peer_file
            candidate_to_delete = MAP[file_name]
            to_delete_ind = -1
            for (index, candidate) in enumerate(candidate_to_delete):
                raw = candidate[1:len(candidate)-1]
                specifics = raw.split(",")
        
                if specifics[0] == file_type and specifics[3] == ip_address and int(specifics[4]) == int(port_number):
                    to_delete_ind = index
                    break

            if to_delete_ind >= 0:
                del candidate_to_delete[to_delete_ind]
                if len(candidate_to_delete) == 0:
                    del MAP[file_name]
                else:
                    MAP[file_name] = candidate_to_delete
    else:
        print("server: got nothing, good bye unfair client")
        conn.send(str.encode("UNACCEPTED"))

    conn.close()

def main_thread():
    # TCP connection 
    # one socket for server connection 
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # bining to local machine
    s.bind((SERVER_HOST, SERVER_PORT))
    s.listen()
    while True:
        conn = None
        try:
            # conn is somehow socket from client 
            # addre - tuple of [IP, PORT]
            conn, addr = s.accept()
            threading.Thread(target=client_handle, args=(conn,addr)).start()
        except KeyboardInterrupt:
            if conn:
                conn.close()
            break

if __name__ == '__main__':
    main_thread()
