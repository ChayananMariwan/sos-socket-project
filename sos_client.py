#   Group 13:
#       ชญาณ์นันท์ มะริวรรณ์ 6709650219
#       ชนิภรณ์ คิมประเสริฐ 6709650243
#       ปุณยนุช แซ่แจ้ง 6709650482
# ----------------------------

import socket
import json
import sys

HOST = "localhost"
PORT = 8080

buffer = ""

#   Send message
# ----------------------------
def send(sock,data):
    message = json.dumps(data) + "\n"
    sock.send(message.encode())

#   Receive message
# ----------------------------
def receive(sock):
    global buffer
    while True:
        data = sock.recv(4096)
        if not data:
            print("Server disconnected")
            exit()

        buffer += data.decode()

        if "\n" in buffer:
            msg, buffer = buffer.split("\n", 1)
            return json.loads(msg)
        
# Print Board
# ----------------------------
#def print_board(board):
    # Add your code here

#   Main
# ----------------------------
def main():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((HOST, PORT))

    print("Connected to server")

    name = input("Enter your name: ")

    send(sock, {
        "type": "register",
        "sender": name
    })

    response = receive(sock)
    print(response.get("msg"))

    while True:
        print("\nMenu")
        print("1. Play")
        print("2. Leaderboard")
        print("3. Exit")

        choose = input("Choose: ")

        if choose == "1":
             print("Pass")
           # play_game(sock, name)
        elif choose == "2":
             print("Pass")
           # show_leaderboard(sock)
        elif choose == "3":
            print("Exit")
            break

        else:
            print("Invalid choice")

    sock.close()



if __name__ == "__main__":
    main()
