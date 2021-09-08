# Start Date: 8/9/2021
# Last Updated: 8/9/2021
# Author: Lucifer 14
# App Name: Simple File Transfer
# Version: CLI Version 1.0
# Type: Client


import socket
import threading
import base64
import os
import sys

ip_address = "127.0.0.1"
cmd_channel = 4444
data_channel = 4445

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((ip_address, cmd_channel))
print("[+] Connected to server.")
data = s.recv(1024)
print(base64.b64decode(data).decode('utf-8'))
while True:
    cmd = input("ft_client> ")
    s.send(base64.b64encode(cmd.encode('utf-8')))
    if cmd == "exit":
        print("[+] Connection Terminated.")
        s.close()
        sys.exit()
    data_len = s.recv(1024)
    data_len = base64.b64decode(data_len).decode('utf-8')
    data=b""
    for i in range (0, int(data_len), 1):
        data+=s.recv(1)
    decoded_data = base64.b64decode(data).decode('utf-8')

    if '<SEPARATOR>' in decoded_data: 
        decoded_data = decoded_data.split("<SEPARATOR>")
        print("Type 'y' or type custom filename WITH extension.")
        custom_filename = input("Save with default filename?: ")
        if custom_filename.lower() == "y":
            custom_filename = decoded_data[0]
        file = open(os.path.join(os.getcwd(), custom_filename), 'w')
        file.write(decoded_data[1])
        file.close()
        print("[+] File saved as " + custom_filename + ".")
    else:
        print(decoded_data)
   
