import socket
import threading
import json
import os

HOST = "localhost"
PORT = 8080
BOARD_SIZE = 3
LEADERBOARD_FILE = "leaderboard.json"

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind((HOST, PORT))
server.listen()

print("Multithreaded Server running...")

clients = {}
waiting_queue = []
active_games = {}
leaderboard = {}

lock = threading.Lock()  # Protect shared resources

# ----------------------------
# Leaderboard Functions
# ----------------------------

def load_leaderboard():
    global leaderboard
    if os.path.exists(LEADERBOARD_FILE):
        with open(LEADERBOARD_FILE, "r") as f:
            leaderboard.update(json.load(f))

def save_leaderboard():
    with open(LEADERBOARD_FILE, "w") as f:
        json.dump(leaderboard, f, indent=4)

# ----------------------------
# Utility
# ----------------------------

def send(sock, data):
    sock.send((json.dumps(data) + "\n").encode())

def check_sos(board, r, c):
    directions = [(0,1),(1,0),(1,1),(1,-1)]
    count = 0

    for dr, dc in directions:

        # Case 1: Placed letter is middle O
        if board[r][c] == "O":
            try:
                if board[r-dr][c-dc] == "S" and board[r+dr][c+dc] == "S":
                    count += 1
            except:
                pass

        # Case 2: Placed letter is starting S
        if board[r][c] == "S":
            try:
                if board[r+dr][c+dc] == "O" and board[r+2*dr][c+2*dc] == "S":
                    count += 1
            except:
                pass

        # Case 3: Placed letter is ending S
        if board[r][c] == "S":
            try:
                if board[r-dr][c-dc] == "O" and board[r-2*dr][c-2*dc] == "S":
                    count += 1
            except:
                pass

    return count

def board_full(board):
    return all(cell!=" " for row in board for cell in row)

# ----------------------------
# Game Class
# ----------------------------

class Game:
    def __init__(self, p1, p2):
        self.players = [p1, p2]
        self.board = [[" "]*BOARD_SIZE for _ in range(BOARD_SIZE)]
        self.scores = {p1:0, p2:0}
        self.turn = 0

# ----------------------------
# Client Handler
# ----------------------------

def handle_client(conn):
    name = None
    try:
        while True:
            data = conn.recv(4096)
            if not data:
                break

            messages = data.decode().split("\n")

            for message in messages:
                if not message.strip():
                    continue

                payload = json.loads(message)
                ptype = payload.get("type")
                sender = payload.get("sender")

                # ---------------- REGISTER ----------------
                if ptype == "register":
                    with lock:
                        clients[conn] = sender
                        name = sender

                        if sender not in leaderboard:
                            leaderboard[sender] = {
                                "win":0,
                                "lose":0,
                                "tie":0
                            }
                            save_leaderboard()

                    send(conn, {"msg":"Registered successfully"})

                # ---------------- PLAY ----------------
                elif ptype == "play":
                    with lock:
                        waiting_queue.append(sender)

                        if len(waiting_queue) >= 2:
                            p1 = waiting_queue.pop(0)
                            p2 = waiting_queue.pop(0)

                            game = Game(p1,p2)
                            active_games[p1] = game
                            active_games[p2] = game

                            for i,p in enumerate(game.players):
                                sock = next(s for s,n in clients.items() if n==p)
                                send(sock,{
                                    "msg":"Game Start",
                                    "mark":"P"+str(i+1),
                                    "game":{
                                        "board":game.board,
                                        "scores":game.scores,
                                        "turn":game.players[game.turn]
                                    }
                                })
                        else:
                            send(conn, {"msg":"Waiting for opponent..."})

                # ---------------- MOVE ----------------
                elif ptype == "move":
                    with lock:
                        game = active_games.get(sender)
                        if not game:
                            continue

                        if game.players[game.turn] != sender:
                            continue

                        r = payload["row"]
                        c = payload["col"]
                        letter = payload["letter"]

                        if game.board[r][c] != " ":
                            continue

                        game.board[r][c] = letter
                        score = check_sos(game.board,r,c)
                        game.scores[sender]+=score

                        if score==0:
                            game.turn = 1-game.turn

                        if board_full(game.board):
                            p1, p2 = game.players
                            s1 = game.scores[p1]
                            s2 = game.scores[p2]

                            if s1 > s2:
                                winner = p1
                                leaderboard[p1]["win"]+=1
                                leaderboard[p2]["lose"]+=1
                            elif s2 > s1:
                                winner = p2
                                leaderboard[p2]["win"]+=1
                                leaderboard[p1]["lose"]+=1
                            else:
                                winner = None
                                leaderboard[p1]["tie"]+=1
                                leaderboard[p2]["tie"]+=1

                            save_leaderboard()

                            for p in game.players:
                                sock = next(s for s,n in clients.items() if n==p)
                                send(sock,{
                                    "msg":"GAME_OVER",
                                    "board":game.board,
                                    "scores":game.scores,
                                    "winner":winner
                                })
                                del active_games[p]
                            continue

                        for p in game.players:
                            sock = next(s for s,n in clients.items() if n==p)
                            send(sock,{
                                "msg":"UPDATE",
                                "board":game.board,
                                "scores":game.scores,
                                "turn":game.players[game.turn]
                            })

                # ---------------- LEADERBOARD ----------------
                elif ptype == "leaderboard":
                    with lock:
                        sorted_board = dict(sorted(
                            leaderboard.items(),
                            key=lambda x: x[1]["win"],
                            reverse=True
                        ))
                    send(conn,{
                        "msg":"LEADERBOARD",
                        "scores":sorted_board
                    })

    except:
        pass

    finally:
        with lock:
            if name:
                print(name, "disconnected")
                clients.pop(conn, None)
                if name in waiting_queue:
                    waiting_queue.remove(name)
        conn.close()

# ----------------------------
# Main
# ----------------------------

def main():
    load_leaderboard()

    while True:
        conn, addr = server.accept()
        print("Connected:", addr)
        threading.Thread(
            target=handle_client,
            args=(conn,),
            daemon=True
        ).start()

if __name__ == "__main__":
    main()