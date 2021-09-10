# Start Date: 10/9/2021
# Last Updated: 10/9/2021
# Author: Lucifer 14
# App Name: Simple File Transfer
# Version: CLI Version 2.0
# Type: Server


import socket
import os
import threading
import base64
import sys
import time

ip_address = "127.0.0.1"
server_name = "FT"
root_dir = "home"
cmd_channel = 4444
data_channel = 4445

connection_is_alive = True
data_channel_is_alive = True

connections = {"command" : "", "data" : ""}

cmd_list = ['upload', 'download', 'list', 'read', 'pwd', 'help', 'exit']

# creating data channel
def data_channel_connection():
    global connections, ip_address, data_channel, connection_is_alive   
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind((ip_address, data_channel))
        print("[+] Data channel created.\n")
        s.listen()
    except:
        print("[-] Data channel creation error.\n")
    else:
        while connection_is_alive == True:
            print("[+] Listening for connection to data channel ...\n")
            conn, addr = s.accept()
            print("[+] Data channel established.\n")
            connections['data'] = conn
    finally:
        pass

# file server functions -- start

def upload_data():
    global connections
    while True:
        conn = connections['data']
        if conn != "": break
        time.sleep(1)
    print("[+] Getting file ....\n")
    data = b""
    while True:
        tmp = conn.recv(1)
        if not tmp : break
        data += tmp
    decoded_data = data.decode()
    conn.close()
    print("[+] Data channel terminated.")
    if '<SEPARATOR>' in decoded_data:
        filename, data = decoded_data.split('<SEPARATOR>')
        file = open(os.path.join(root_dir, filename), 'w')
        file.write(data)
        file.close()
        print("[+] File saved as", filename)
    else:
        print(decoded_data)
    connections['data'] = ''



def download_data(path_to_file):
    global connections
    basefilename = os.path.basename(path_to_file).encode('utf-8')
    separator = '<SEPARATOR>'.encode('utf-8')
    try:
        file = open(path_to_file, 'rb')
    except FileNotFoundError:
        data = "[-] File not found on server!"
        encoded_data = data.encode()
    else:
        data = file.read(1)
        while True:
            data_tmp = file.read(2)
            if not data_tmp: 
                break
            data+=data_tmp
        file.close()
        encoded_data = basefilename + separator + data
    finally:
        while True:
            conn = connections['data']
            if conn != "": break
            time.sleep(1)
        conn.send(encoded_data)
        print("[+] File transfer completed.\n")
        conn.close()
        print("[+] Data channel terminated.\n")
        connections['data'] = ''

def get_directory():
    pass

def read_data(path_to_file):
    global connections
    try:
        file = open(path_to_file, 'rb')
    except FileNotFoundError:
        data = "[-] File not found on server!"
        encoded_data = data.encode()
    else:
        data = file.read(1)
        while True:
            data_tmp = file.read(2)
            if not data_tmp: 
                break
            data+=data_tmp
        file.close()
        encoded_data = data
    finally:
        while True:
            conn = connections['data']
            if conn != "": break
            time.sleep(1)
        conn.send(encoded_data)
        print("[+] Data transfer completed.\n")
        conn.close()
        print("[+] Data channel terminated.\n")
        connections['data'] = ''

def get_pwd():
    pass

def get_help():
    pass

def end_connection():
    global connection_is_alive
    connection_is_alive = False
    print("[+] Command channel terminated.\n")
# file server functions -- stop

# manages commands
def cmd_manager(cmd):
    global root_dir, connections, cmd_list
    conn = connections['command']
    cmd_segments = cmd.split(" ")
    cmd_keyword = cmd_segments[0]
    tmp_segments = cmd_segments
    filename = ""
    if len(cmd_segments) > 1:
        del tmp_segments[0]
        filename = " ".join(cmd_segments)
    if os.path.isabs(filename) and root_dir in filename:
        path_to_file = filename
    else:
        path_to_file = os.path.join(os.getcwd(), root_dir, filename)
    if cmd_keyword == cmd_list[0]:
        upload_data()
    elif cmd_keyword == cmd_list[1]:
        download_data(path_to_file)
    elif cmd_keyword == cmd_list[2]:
        pass
    elif cmd_keyword == cmd_list[3]:
        read_data(path_to_file)
    elif cmd_keyword == cmd_list[4]:
        pass
    elif cmd_keyword == cmd_list[5]:
        pass
    elif cmd_keyword == cmd_list[6]:
        end_connection()
    else:
        response = "[-] Command not found! Type 'help' to see available commands."
        encoded_response = response.encode()
        conn.send(encoded_response)
    pass

# recevie commnads
def recv_commands():
    global connections
    conn = connections['command']
    cmd = conn.recv(1024)
    decoded_cmd = cmd.decode()
    print("[+] Command received:", decoded_cmd, "\n")
    return decoded_cmd

# set up initial connections command channel and data channel 
def ini_connection():
    global connections, ip_address, cmd_channel, data_channel_is_alive, connection_is_alive
    data_channel_thread = threading.Thread(target=data_channel_connection)
    data_channel_thread.start()
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind((ip_address, cmd_channel))
        print("[+] Command channel created.\n")
        s.listen()
    except:
        print("[-] Command channel creation error.\n")
    else:
        while True:
            print("[+] Listening for connection to command channel ...\n")
            conn, addr = s.accept()
            print("[+] Command channel established.\n")
            connection_is_alive = True
            connections["command"] = conn

            welcome_msg = f"Welcome to {server_name} file server.\nType 'help' to see available commands."
            conn.send(welcome_msg.encode())
            while connection_is_alive == True:
                cmd = recv_commands()
                cmd_manager(cmd)
    finally:
        data_channel_is_alive = False
        data_channel_thread.join()
        conn.close()
        s.close()


if __name__ == "__main__":
    ini_connection()