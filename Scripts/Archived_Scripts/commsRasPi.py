import socket

# Configuration
RASPI_IP = "192.168.68.79"  # Replace with your Raspberry Pi's IP address
PORT = 5000  # Choose a port number


# function to connect to raspi
def connect_to_raspi():
    try:
        # Create a socket object
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # Connect to the Raspberry Pi
        sock.connect((RASPI_IP, PORT))
        print("Connected to Raspberry Pi at {}:{}".format(RASPI_IP, PORT))
        return sock
    except Exception as e:
        print("Failed to connect to Raspberry Pi: {}".format(e))
        return None

# function to disconnect from raspi
def disconnect_from_raspi(sock):
    try:
        if sock:
            sock.close()
            print("Disconnected from Raspberry Pi")
    except Exception as e:
        print("Failed to disconnect from Raspberry Pi: {}".format(e))

# function to send command as a string to raspi and print the response
def send_command(sock, command):
    try:
        if sock:
            # Send the command to the Raspberry Pi
            sock.sendall(command.encode())
            print("Sent command: {}".format(command))
            # Receive the response from the Raspberry Pi
            response = sock.recv(1024).decode()
            print("Received response: {}".format(response))
    except Exception as e:
        print("Failed to send command: {}".format(e))

# open the connection to the raspi
sock = connect_to_raspi()

# while loop that accepts user input and sends it to the raspi until the user types "exit"
while True:
    user_input = input("Enter a command to send to the Raspberry Pi (or type 'exit' to quit): ")
    if user_input.lower() == "exit":
        send_command(sock, "exit")  # Optionally send an exit command to the Raspberry Pi
        break
    send_command(sock, user_input)

# close the connection to the raspi
disconnect_from_raspi(sock)