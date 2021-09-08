# Start Date: 8/9/2021
# Last Updated: 8/9/2021
# Author: Lucifer 14
# App Name: Simple File Transfer
# Version: CLI Version 1.0
# Type: Server


import socket
import os
import threading
import base64
import random
import sys

ip_address = "127.0.0.1"
server_name = "FT"
cmd_channel = 4444
data_channel = 4445

cmd_list = ['upload', 'download', 'ls', 'read', 'pwd', 'exit']

def commands(cmd, connn):
    global conn
    global connection_alive
    root_dir = "home"
    cmd_segments = cmd.split(" ")
    cmd_keyword = cmd_segments[0]
    #cmd_segments.append(" > tmp")
    if cmd_keyword == cmd_list[0]:
        pass
    elif cmd_keyword == cmd_list[1]:
        new_segments = cmd_segments
        del new_segments[0]
        filename = ' '.join(new_segments)
        path_to_file = os.path.join(os.getcwd(), root_dir, filename) 
        basefile_name = os.path.basename(path_to_file).encode('utf-8')
        separator = '<SEPARATOR>'.encode('utf-8')
        encoded_data = ""
        try:
            file = open(path_to_file, 'rb')
            file_data = file.read(1)
            while True:
                file_data_tmp = file.read(2)
                if not file_data_tmp: break
                file_data+=file_data_tmp
                
            file.close()
            data = basefile_name + separator + file_data
            encoded_data = base64.b64encode(data)
        except FileNotFoundError:
            encoded_data = base64.b64encode("[-] File not found.".encode('utf-8'))

        finally:
            conn.send(base64.b64encode(bytes(str(len(encoded_data)), 'utf-8'))) 
            conn.send(encoded_data)
        pass
    elif cmd_keyword == cmd_list[2]:
        pass
    elif cmd_keyword == cmd_list[3]:
        pass
    elif cmd_keyword == cmd_list[4]:
        pass
    elif cmd_keyword == cmd_list[5]:
        conn.close()
        connection_alive = False
        print("[+] Connection terminated")
        #sys.exit()
    else:
        response = "[-] Command not found! Type 'help' to see available commands."
        encoded_response = base64.b64encode(response.encode('utf-8'))
        conn.send(base64.b64encode(bytes(str(len(encoded_response)), 'utf-8')))
        conn.send(encoded_response)
    


    #os.system("") remove tmp


s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((ip_address, cmd_channel))
print("[+] Server started.")
s.listen()
conn, addr = s.accept()
print("[+] Connection accepted.")
welcome_msg = "Welcome to " + server_name + " file server.\nType 'help' to see available commands."
conn.send(base64.b64encode(welcome_msg.encode('utf-8')))
connection_alive = True
while connection_alive == True:
    cmd = conn.recv(1024)
    cmd = base64.b64decode(cmd).decode('utf-8')
    commands(cmd, conn)