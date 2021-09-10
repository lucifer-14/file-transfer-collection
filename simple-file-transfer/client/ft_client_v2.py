# Start Date: 10/9/2021
# Last Updated: 10/9/2021
# Author: Lucifer 14
# App Name: Simple File Transfer
# Version: CLI Version 2.0
# Type: Client


import socket
import os
import threading
import base64
import sys
import time

ip_address = "127.0.0.1"
cmd_channel = 4444
data_channel = 4445

connection_is_alive = True
data_channel_is_alive = True

connections = {"command" : "", "data" : ""}

cmd_list = ['upload', 'download', 'list', 'read', 'pwd', 'help', 'exit']

def data_channel_connection():
    global data_channel_is_alive, connections
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((ip_address, data_channel))
        connections['data'] = s
        print("\n[+] Connected to data channel.")
    except:
        print("[-] Data channel connection error.")
    

#file server functions -- start
def upload_data(path_to_file):
    data_channel_connection()
    global connections
    conn = connections['data']
    basefilename = os.path.basename(path_to_file).encode('utf-8')
    separator = '<SEPARATOR>'.encode('utf-8')
    try:
        file = open(path_to_file, 'rb')
    except FileNotFoundError:
        data = "[-] File not found on pc!"
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
        conn.send(encoded_data)
        print("[+] File transfer completed.")
        conn.close()
        print("[+] Data channel terminated.")
        connections['data'] = ''

def download_data():
    data_channel_connection()
    global connections
    conn = connections['data']
    print("[+] Getting file ....")
    data = b""
    while True:
        tmp = conn.recv(1)
        if not tmp : break
        data += tmp
    decoded_data = data.decode()
    conn.close()
    print("[+] Disconnected from data channel.")
    if '<SEPARATOR>' in decoded_data:
        filename, data = decoded_data.split('<SEPARATOR>')
        file = open(filename, 'w')
        file.write(data)
        file.close()
        print("[+] File saved as", filename)
    else:
        print(decoded_data)


def get_directory():
    pass

def read_data():
    data_channel_connection()
    global connections
    conn = connections['data']
    print("[+] Reading file ....")
    data = b""
    while True:
        tmp = conn.recv(1)
        if not tmp : break
        data += tmp
    decoded_data = data.decode()
    conn.close()
    print("[+] Disconnected from data channel.")
    print(decoded_data)

def get_pwd():
    pass

def get_help():
    pass

def end_connection():
    global connection_is_alive
    connection_is_alive = False
    print("[+] Connection Terminated.")

# file server functions -- stop

def command_manager(cmd):
    global connections
    conn = connections['command']
    encoded_cmd = cmd.encode()
    if encoded_cmd:
        conn.send(encoded_cmd)
        cmd_segments = cmd.split(" ")
        cmd_keyword = cmd_segments[0]
        tmp_segments = cmd_segments
        filename = ""
        if len(cmd_segments) > 1:
            del tmp_segments[0]
            filename = " ".join(cmd_segments)
        if os.path.isabs(filename):
            path_to_file = filename
        else:
            path_to_file = os.path.join(os.getcwd(), filename)

        if cmd_keyword == cmd_list[0]: 
            upload_data_channel_thread = threading.Thread(target=upload_data, args=(path_to_file,))
            upload_data_channel_thread.start()
        elif cmd_keyword == cmd_list[1]:
            download_data_channel_thread = threading.Thread(target=download_data, args=())
            download_data_channel_thread.start()
        elif cmd_keyword == cmd_list[3]:
            read_data_channel_thread = threading.Thread(target=read_data, args=())
            read_data_channel_thread.start()
        elif cmd_keyword == cmd_list[6]:
            end_connection()
        else:
            response = conn.recv(1024)
            decoded_response = response.decode()
            print(decoded_response)

def send_commands():
    try:
        cmd = input("ft_client> ")
    except KeyboardInterrupt:
        cmd = "exit"
        print()
    finally:
        command_manager(cmd)

def ini_connection():
    global connection_is_alive
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((ip_address, cmd_channel))
        connections['command'] = s
        print("[+] Connected to command channel.")
    except:
        print("[-] Command channel connection error.")
    else:
        recv_welcome = s.recv(1024)
        print(recv_welcome.decode())
        while connection_is_alive == True:
            send_commands()
    finally:
        s.close()


if __name__ == "__main__":
    ini_connection()
