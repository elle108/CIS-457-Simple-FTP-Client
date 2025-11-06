# Simple FTP Client (Python)

## Overview
This project is a basic FTP client implemented in Python using TCP sockets.  
It replicates core FTP functionalities described in **RFC 959**, including connecting to a remote FTP server, authenticating a user, transferring files, and listing directories.

The client demonstrates:
- Creating and managing TCP sockets
- Handling single-line and multi-line FTP responses
- File transfer using separate data connections
- Using threads to handle concurrent control and data traffic

## Supported Commands
| User Command | FTP Command | Description |
|---------------|--------------|--------------|
| `open <host>` | N/A | Connect to an FTP server |
| `dir` | `LIST` | List remote directory contents |
| `cd <path>` | `CWD` | Change directory on remote host |
| `get <file>` | `RETR` | Download file |
| `put <file>` | `STOR` | Upload file |
| `close` | `QUIT` | Close current FTP session |
| `quit` | `QUIT` | Exit the program |

## How It Works
1. The program first creates a **command socket** for communication with the FTP server (port 21).
2. A second **data socket** is opened using the `PORT` command to transfer files or directory listings.
3. **Threads** are used to handle both control and data channels concurrently without blocking.
4. The program reads user input in a loop and performs the corresponding FTP actions.

## Usage
Run the program:
```bash
python3 ftp_client.py
