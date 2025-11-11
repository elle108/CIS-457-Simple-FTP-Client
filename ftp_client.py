from socket import socket, AF_INET, SOCK_STREAM
import os
import re

def ftp_command(s, cmd):
    # Send command
    print(f"Sending command {cmd}")
    s.sendall((cmd + "\r\n").encode())

    # Accumulate response bytes in case message is longer than one recv() call
    resp_bytes = bytearray()
    first_code = None
    multiline = False
    
    # Loop to receive the complete response message
    while True:
        chunk = s.recv(1024)
        if not chunk:
            break
        resp_bytes.extend(chunk)
        resp_text = resp_bytes.decode('utf-8', errors='replace')
        lines = resp_text.splitlines()
        # Check if first line starts with 3 digits
        if lines:
            first_line = lines[0]
            if len(first_line) >= 3 and first_line[:3].isdigit():
                if first_code is None:
                    first_code = first_line[:3]
                    # Multiline if 4th character is '-'
                    multiline = len(first_line) > 3 and first_line[3] == '-'
                if not multiline:
                    break
                
                # For multiline, look for final line with space after code
                else:
                    for line in lines[1:]:
                        if line.startswith(first_code + ' '):
                            done = True
                            break
                    else:
                        done = False
                    if done:
                        break

    # Print response
    text = resp_bytes.decode('utf-8', errors='replace')
    print(f"{len(resp_bytes)} bytes:\n{text}")
    
    # Return the numeric status code
    try:
        status = int(first_code) if first_code is not None else int(text[:3])
    except Exception:
        status = -1
    return status

def open_connection(hostname):
    global open_sock
    
    try:
        # Create TCP socket
        open_sock = socket(AF_INET, SOCK_STREAM)
        # Connect to FTP server on port 21
        open_sock.connect((hostname, 21))
        # Receive welcome message from server
        buffer = bytearray(2048)
        nbytes = open_sock.recv_into(buffer)
        response = buffer[:nbytes].decode('utf-8', errors='replace')
        print(response)
        
        # Parse status code from welcome message
        status_code = None
        for line in response.splitlines():
            if len(line) >= 3 and line[:3].isdigit():
                status_code = int(line[:3])
                break

        # Status 220 means server is ready
        if status_code == 220:
            print("Connection established")
            print("Enter username to authenticate")
            username = input("Username: ")
            authenticate(username, "")
    except Exception as e:
        print("Error connecting to server")
        open_sock = None
        return
    
def authenticate(username, password):
    global open_sock
    if not open_sock:
        print("No open connection to authenticate")
        return
    
    # Send USER command with username
    status_code = ftp_command(open_sock, f"USER {username}")
    
    # If server needs password, prompt and send PASS command
    if status_code == 331:
        if not password:
            print("Enter password")
            password = input("Password: ")
        status_code = ftp_command(open_sock, f"PASS {password}")
    
    # Check authentication result
    if status_code == 230:
        print("Authentication successful")
        return
    
    elif status_code == 332:
        print("Need account for login")
        return
    
    elif (status_code == 421 or status_code == 500 or status_code == 501 or status_code == 530):
        print("Error in connection or authentication")
        return
    
    else:
        print("Unknown response from server")
        return

def data_reception():
    """Set up a passive data connection (emailed Prof regarding this)"""
    global open_sock

    # Send PASV command
    print("Sending command PASV")
    open_sock.sendall(b"PASV\r\n")

    # Receive response with IP and port information
    resp = open_sock.recv(1024).decode('utf-8', errors='replace')
    print(f"{len(resp)} bytes:\n{resp}")

    # Check for successful passive mode
    if not resp.startswith("227"):
        print("Failed to enter passive mode")
        return None

    # Extract the IP and port
    match = re.search(r'\((\d+,\d+,\d+,\d+,\d+,\d+)\)', resp)
    if not match:
        print("Failed to parse PASV response")
        return None

    # Parse the values
    parts = match.group(1).split(',')
    ip = '.'.join(parts[:4])
    port = (int(parts[4]) << 8) + int(parts[5])

    # Create new socket and connect to port
    data_sock = socket(AF_INET, SOCK_STREAM)
    data_sock.connect((ip, port))
    return data_sock
    
def list_directory():
    global open_sock
    if not open_sock:
        print("Not connected")
        return

    # Set ASCII mode
    ftp_command(open_sock, "TYPE A")
    
    # Data connection
    data_sock = data_reception()
    if not data_sock:
        return

    # Send LIST command
    status_code = ftp_command(open_sock, "LIST")
    
    # Receive directory listing data over data connection
    if status_code in [125, 150]:
        received_data = bytearray()
        while True:
            chunk = data_sock.recv(1024)
            if not chunk:
                break
            received_data.extend(chunk)
        print(received_data.decode('utf-8', errors='replace'))

        # Close data connection 
        data_sock.close()

        # Receive final response from control connection
        buff = bytearray(512)
        nbytes = open_sock.recv_into(buff)
        if nbytes > 0:
            print(buff[:nbytes].decode('utf-8', errors='replace'))
    else:
        print("Failed to list directory")
    
def change_directory(path):
    global open_sock
    if not open_sock:
        print("Not connected")
        return
    
    # Send CWD command
    status_code = ftp_command(open_sock, f"CWD {path}")
    
    # Status 250 success
    if status_code == 250:
        print(f"Changed to {path}")
    else:
        print(f"Failed to change directory")

def download_file(filename):
    global open_sock
    if not open_sock:
        print("Not connected")
        return

    # Set binary mode
    ftp_command(open_sock, "TYPE I")

    # Data connection
    data_sock = data_reception()
    if not data_sock:
        return

    # Send RETR command to retrieve file
    status_code = ftp_command(open_sock, f"RETR {filename}")

    # Receive file data over data connection
    if status_code in [125, 150]:
        received_data = bytearray()
        while True:
            data_chunk = data_sock.recv(4096)
            if not data_chunk:
                break
            received_data.extend(data_chunk)

        # Close data connection
        data_sock.close()

        # Write data to local file
        with open(filename, 'wb') as f:
            f.write(received_data)
        print(f"Downloaded {filename} ({len(received_data)} bytes)")

        # Receive final response
        buff = bytearray(512)
        nbytes = open_sock.recv_into(buff)
        if nbytes > 0:
            print(buff[:nbytes].decode('utf-8', errors='replace'))
    else:
        print(f"Failed to download {filename}")
        data_sock.close()

def upload_file(filename):
    global open_sock
    if not open_sock:
        print("Not connected")
        return
    
    # Check if local file exists
    if not os.path.exists(filename):
        print(f"Local file {filename} not found")
        return
    
    # Read local file
    with open(filename, 'rb') as f:
        file_data = f.read()

    # Set binary mode
    ftp_command(open_sock, "TYPE I")
    
    # Data connection
    data_sock = data_reception()
    if not data_sock:
        return
    
    # Send STOR command 
    status_code = ftp_command(open_sock, f"STOR {filename}")

    # Send file data over data connection
    if status_code in [125, 150]:
        data_sock.sendall(file_data)
        data_sock.close()
        print(f"Uploaded {filename} ({len(file_data)} bytes)")

        # Receive final response
        buff = bytearray(512)
        nbytes = open_sock.recv_into(buff)
        if nbytes > 0:
            print(buff[:nbytes].decode('utf-8', errors='replace'))
    else:
        print(f"Failed to upload {filename}")
        data_sock.close()

def close_connection(): #halie
    global open_sock
    if not open_sock:
        print("No connection to close")
        return
    
    # Close the socket
    try:
        open_sock.close()
        open_sock = None
        print("Connection closed")
    except Exception as e:
        print("Error closing connection")
        open_sock = None

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

    while True:
        try:
            # Read user input
            command = input("ftp> ").strip().split()
            if not command:
                continue
            cmd = command[0].lower()
            input_arg = command[1] if len(command) > 1 else None
            
            # Process user commands
            if cmd == "open":
                if input_arg:
                    open_connection(input_arg)
                else:
                    print("Usage: open <hostname>")
                    
            elif cmd == "dir":
                list_directory()
                
            elif cmd == "cd":
                if input_arg:
                    change_directory(input_arg)
                else:
                    print("Usage: cd <path>")
                    
            elif cmd == "get":
                if input_arg:
                    download_file(input_arg)
                else:
                    print("Usage: get <filename>")
                    
            elif cmd == "put":
                if input_arg:
                    upload_file(input_arg)
                else:
                    print("Usage: put <filename>")
                    
            elif cmd == "close":
                close_connection()
                
            elif cmd == "quit":
                if open_sock:
                    close_connection()
                print("Goodbye!")
                break
                
            else:
                print(f"Unknown command: {cmd}")
                
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    main()