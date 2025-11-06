from socket import socket, AF_INET, SOCK_STREAM
from threading import Thread

FTP_SERVER = "ftp.cs.brown.edu"

buffer = bytearray(512)

# TODO: Send FTP command and recieve response while handling multiline messages"""
# Starter Code

def ftp_command(s, cmd):
    print(f"Sending command {cmd}")
    buff = bytearray(512)
    s.sendall((cmd + "\r\n").encode())
    
    # TODO: Fix this part to parse multiline responses
    nbytes = s.recv_into(buff)
    print(f"{nbytes} bytes: {buff.decode()}")
  
command_sock = socket(AF_INET, SOCK_STREAM)
command_sock.connect((FTP_SERVER, 21))
my_ip, my_port = command_sock.getsockname()
len = command_sock.recv_into(buffer)
print(f"Server response {len} bytes: {buffer.decode()}")

ftp_command(command_sock, "USER anonymous")
ftp_command(command_sock, "QUIT")

# Skeleton Code for FTP Client Functionality
# TODO: Implement functions to handle FTP commands

def open_connection(hostname):
    global open_sock
    
    open_sock = socket(AF_INET, SOCK_STREAM)
    open_sock.connect((hostname, 21))
    buffer = bytearray(512)
    nbytes = open_sock.recv_into(buffer)
    response = buffer[:nbytes].decode()
    status_code = int(response[:3])

    if status_code == 220:
        print("Connection established")
        print("Enter username to authenticate")
        username = input("Username: ")
        authenticate(username, "")
    
def authenticate(username, password):
    if not open_sock:
        print("No open connection to authenticate")
        return
    
    status_code = ftp_command(command_sock, f"USER {username}")
    
    if status_code == 331:
        if password == "":
            print("Username accepted, enter password")
            password = input("Password: ")
        else:
            print("Username accepted, using provided password")
        status_code = ftp_command(command_sock, f"PASS {password}")
        
        if status_code == 230:
            print("Authentication successful")
            return
        else:
            print("Authentication failed")
            return
        
    elif status_code == 230:
        print("Authentication successful")
        return
    
    elif status_code == 332:
        print("Need account for login")
        return
    
    elif (status_code == 421 | status_code == 500 | status_code == 501 | status_code == 530):
        print("Error in connection or authentication")
        return
    
    else:
        print("Unknown response from server")
        return

def data_reception():
    data_receptionist = socket(AF_INET, SOCK_STREAM)
    data_receptionist.bind(("0.0.0.0", 0))
    data_receptionist.listen(1) 

    ip = open_sock.getsockname()[0]
    port = open_sock.getsockname()[1]
    
    hi = port // 256
    lo = port % 256
    
    split_ip = ip.split(".")
    port_command = f"PORT {split_ip[0]}, {split_ip[1]}, {split_ip[2]}, {split_ip[3]}, {hi}, {lo}"
    
    status_code = ftp_command(open_sock, port_command)
    
    if status_code == 200:
        return data_receptionist
    else:
        print("Failed to set up data connection")
        data_receptionist.close()
        return None
    
def handle_data_reception(data_receptionist, result):
    data_sock, addr = data_receptionist.accept()
    
    received_data = bytearray()
    buff = bytearray(1024)
    
    while True:
        nbytes = data_sock.recv_into(buff)
        if nbytes == 0:
            break
        received_data.extend(buff[:nbytes])
        
    result.append(received_data)
    data_sock.close()

def handle_data_sending(data_receptionist, data):
    data_sock, addr = data_receptionist.accept()
    data_sock.sendall(data)
        
    data_sock.close()
    
def list_directory():
    open_sock = socket(AF_INET, SOCK_STREAM)
    open_sock.connect((hostname, 21))
    open_sock.recv_into(buffer)
    status_code = int(buffer[:3].decode())
    
    

def change_directory(path):
    if not open_sock:
        print("No open connection to change directory")
        return
    
    status_code = ftp_command(open_sock, f"CWD {path}")
def download_file(filename):
    status_code = ftp_command(open_sock, f"RETR {filename}")
def upload_file(filename):
    status_code = ftp_command(open_sock, f"STOR {filename}")
def close_connection():
    status_code = ftp_command(open_sock, "QUIT")

# Print options to user
def print_menu():
    print("Simple FTP Client Commands:")
    print("open <host> - Connect to FTP server")
    print("dir - List directory")
    print("cd <path> - Change directory")
    print("get <file> - Download file")
    print("put <file> - Upload file")
    print("close - Close connection")
    print("quit - Exit program")
    
def main():
    print_menu()
    
    username = None
    password = None
    
    while True:
        try:
            command = input("ftp> ").strip().split()
            if not command:
                continue
            cmd = command[0].lower()
            
            if cmd == "open":
                open_connection(command[1])
            elif cmd == "dir":
                list_directory()
            elif cmd == "cd":
                change_directory(command[1])
            elif cmd == "get":
                download_file(command[1])
            elif cmd == "put":
                upload_file(command[1])
            elif cmd == "close":
                close_connection()
            elif cmd == "quit":
                break
            else:
                print("Unknown command")  
        except Exception as e:
            print(f"Error: {e}")  

if __name__ == "__main__":
    main()