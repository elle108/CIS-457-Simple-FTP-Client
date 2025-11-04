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

# Use the "receptionist" to accept incoming connections
data_receptionist = socket(AF_INET, SOCK_STREAM)
data_receptionist.bind(("0.0.0.0", 12345))
data_receptionist.listen(1)         # max number of pending request

# Use the "data_socket" to perform the actual byte transfer
data_socket = data_receptionist.accept()

# Skeleton Code for FTP Client Functionality
# TODO: Implement functions to handle FTP commands

def open_connection(hostname):
    pass
def authenticate(username, password):
    pass
def send_command(sock, command):
    pass
def list_directory():
    pass
def change_directory(path):
    pass
def download_file(filename):
    pass
def upload_file(filename):
    pass
def close_connection():
    pass

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