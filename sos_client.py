# Group 13:
#   นางสาวชญาณ์นันท์ มะริวรรณ์ 6709650219
#   นางสาวชนิภรณ์ คิมประเสริฐ  6709650243
#   นางสาวปุณยนุช แซ่แจ้ง     6709650482
# ----------------------------

# คำตอบจากคำถามชวนคิด: 
#   ไม่สามารถรองรับผู้เล่นมากกว่า 1 คนได้ เนื่องจากไม่มีการจัดการ concurrent connection ทำให้ server ติดต่อได้ทีละ client เท่านั้น 
#   และไม่สามารถจับคู่ผู้เล่นหรือจัดการหลายเกมพร้อมกันได้
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
            print("Disconnected from server")
            exit()

        buffer += data.decode()

        if "\n" in buffer:
            msg, buffer = buffer.split("\n", 1)
            return json.loads(msg)
        

# Print Board
# ----------------------------
def print_board(board):
    print()
    for i, row in enumerate(board):
        print(" | ".join(row))
        if i < len(board) - 1:
            print("-" * 5)
    print()


# Play
# -----------------------
#def play_game(sock, name):
    


# Leaderboard
# -----------------------
def show_leaderboard(sock):

    send(sock, {
        "type": "leaderboard"
    })

    data = receive(sock)

    if data["msg"] == "LEADERBOARD":
        print("\nLeaderboard: ")
       

        for player, stat in data["scores"].items():
            print(player, ":", 
              "{ 'win': ", stat["win"], 
              ", 'lose': ", stat["lose"], 
              ", 'tie': ", stat["win"], "}")


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
             show_leaderboard(sock)
        elif choose == "3":
            print("Exit")
            break

        else:
            print("Invalid choice")

    sock.close()



if __name__ == "__main__":
    main()
