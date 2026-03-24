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
    width = 18
    print()
    for i, row in enumerate(board):
        line = " | ".join(row)
        print(line.center(width))

        if i < len(board):
            print(("-" * 10).center(width))
    print()


# get_move
# ----------------------------
def get_move(board):
    while True:
        try:
            row, col, letter = input("row col letter: ").split()

            row = int(row)
            col = int(col)
            letter = letter.upper()

            # check letter
            if letter not in ["S", "O"]:
                print("Invalid letter (use S or O)")
                continue

            # check range
            if not (0 <= row <= 2 and 0 <= col <= 2):
                print("Row/Col must be 0-2")
                continue

            # check ตำแหน่งซ้ำ 
            if board[row][col] != " ":
                print("This position is already taken!")
                continue

            return row, col, letter

        except:
            print("Invalid input. Example: 1 2 S")


# Play
# -----------------------
def play_game(sock, name):
    width = 18

    send(sock, {
        "type": "play",
        "sender": name
    })

    #เก็บ history
    history = [] 

    while True:
        data = receive(sock)
        msg = data.get("msg")

        # WAIT
        if msg == "Waiting for opponent...":
            print("Waiting for opponent...")

        # GAME START
        elif msg == "Game Start":
            print("\n=== Game Start ===".center(width))

            board = data["game"]["board"]
            scores = data["game"]["scores"]
            turn = data["game"]["turn"]

            print_board(board)
            print("Scores:", scores)
            print("Turn:", turn)

            if turn == name:
                row, col, letter = get_move(board)

                # save history
                history.append(f"{name}: ({row},{col}) = {letter}")

                send(sock, {
                    "type": "move",
                    "sender": name,
                    "row": row,
                    "col": col,
                    "letter": letter
                })
            else:
                print("Waiting for opponent...")


        # UPDATE
        elif msg == "UPDATE":
            board = data["board"]
            scores = data["scores"]
            turn = data["turn"]

            print_board(board)
            print("Scores:", scores)
            print("Turn:", turn)

            if turn == name:
                row, col, letter = get_move(board)

                # save history
                history.append(f"{name}: ({row},{col}) = {letter}")

                send(sock, {
                    "type": "move",
                    "sender": name,
                    "row": row,
                    "col": col,
                    "letter": letter
                })
            else:
                print("Waiting for opponent...")

            
        elif msg == "ERROR":
            print("Error:", data.get("message", "Invalid move"))


        # GAME OVER
        elif msg == "GAME_OVER":
            print("\n=== GAME OVER ===")

            print_board(data["board"])
            print("Scores:", data["scores"])

            winner = data.get("winner")

            if winner:
                print("Winner:", winner)
            else:
                print("It's a tie!")

             # show history
            print("\n=== Game History ===")
            for h in history:
                print(h)

            if "reason" in data:
                print("Reason:", data["reason"])

            break


# Leaderboard
# -----------------------
def show_leaderboard(sock):
    send(sock, {
        "type": "leaderboard"
    })

    data = receive(sock)

    if data["msg"] == "LEADERBOARD":
        print("\nLeaderboard: ")
       
        print("Player     Win   Lose   Tie")
        print("-" * 30)

        for player, stat in data["scores"].items():
            print(f"{player:<10} {stat['win']:<5} {stat['lose']:<5} {stat['tie']:<5}")


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
           play_game(sock, name)
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
