from socket import socket, AF_INET, SOCK_STREAM
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
    # Create the socket
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
    data_receptionist.bind(("0.0.0.0", 12345))
    data_receptionist.listen(1) 

    ip = open_sock.getsockname()[0]
    port = open_sock.getsockname()[1]
    
    hi = port // 8
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

def list_directory():
    if not open_sock:
        print("No open connection to list directory")
        return
    
    ftp_command(open_sock, "TYPE A")
    
    data_receptionist = data_reception()
    if not data_receptionist:
        return
    
    status_code = ftp_command(open_sock, "LIST")
    
    if status_code == 125 or status_code == 150:
        data_sock, addr = data_receptionist.accept()
        
        listing = bytearray()
        buff = bytearray(1024)
        
        while True:
            nbytes = data_sock.recv_into(buff)
            if nbytes == 0:
                break
            listing.extend(buff[:nbytes])
        
        print("Directory listing:")
        print(listing.decode())
        data_sock.close()
        
        data_receptionist.close()
      
def change_directory(path):
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
    print("user <username> - Set username")
    print("pass <password> - Set password")
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
            elif cmd == "user":
                username = command[1]
                authenticate(username, password)
            elif cmd == "pass":
                password = command[1]
                authenticate(username, password)
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