import numpy as np
import matplotlib
import time
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib import animation, rc
from IPython.display import HTML, clear_output
import random
from collections import deque
from queue import Queue
import json

class PlayerAgent:
    def __init__(self, player_id, iterative_max_depth=8):
        self.player_id = player_id
        self.iterative_max_depth = iterative_max_depth
        self.board_size = 0
        self.game = 0

    def bfs(self, board):
        position_x, position_y, enemy_x, enemy_y = self.get_position_by_board(board)
        frontier = Queue()
        frontier.put((position_x, position_y))
        expanded_set = set()
        while not frontier.empty():
            current_board = frontier.get()
            if current_board[0] == enemy_x and current_board[1] == enemy_y:
                return True
            elif str(current_board) not in expanded_set:
                for move in self.get_legal_moves_tree(board, self.player_id):
                    board_tmp = self.examine_move_tree(board, move, self.player_id)
                    if str(board_tmp) not in expanded_set:
                        x, y, _, _ = self.get_position_by_board(board_tmp)
                        frontier.put((x, y))
                expanded_set.add(str(current_board))
        return False

    def choose_move(self, game):
        # Get an array of legal moves from your current position.
        self.board_size = game.size
        self.game = game

        return self.find_best_move(game)
        # Choose an action to take based on the algorithm you
        # decide to implement. This method should return
        # one of the items in the 'legal_moves' array.

    def get_position_by_board(self, board):
        position_x = np.where(board == self.player_id)[0][0]
        position_y = np.where(board == self.player_id)[1][0]
        enemy_x = np.where(board == self.game.agent2)[0][0]
        enemy_y = np.where(board == self.game.agent2)[1][0]
        return position_x, position_y, enemy_x, enemy_y

    def examine_move_tree(self, board, move, player):
        board2 = board.copy()
        if player == self.player_id:
            position_x = np.where(board == self.player_id)[0][0]
            position_y = np.where(board == self.player_id)[1][0]
            board2[position_x, position_y] = 4
            board2[move[0], move[1]] = player
        else:
            enemy_x = np.where(board == self.game.agent2)[0][0]
            enemy_y = np.where(board == self.game.agent2)[1][0]
            board2[enemy_x, enemy_y] = 4
            board2[move[0], move[1]] = player
        return board2

    def escape_from_corner(self, board, position_x, position_y):
        total = 0
        if len(self.get_legal_moves_tree(board, self.player_id)) == 1:
            total -= 0.5
        if len(self.get_legal_moves_tree(board, self.player_id)) == 3:
            total += 0.25
        if not (0 < position_x < self.board_size - 1 and 0 < position_y < self.board_size - 1):
            total -= 0.1
        return total

    def grid_neighbors(self, row, col):
        maxrow = self.board_size
        maxcol = self.board_size
        l = []
        if (row + 1 < maxrow):
            l += [(row + 1, col)]
        if (row > 0):
            l += [(row - 1, col)]
        if (col + 1 < maxcol):
            l += [(row, col + 1)]
        if (col > 0):
            l += [(row, col - 1)]
        return l

    def dijkstra(self, board, x, y):
        distance = np.zeros((self.board_size, self.board_size))
        distance[:] = np.inf
        distance[x, y] = 0
        visited = np.zeros((self.board_size, self.board_size))
        # get neighborhood point
        neighbor = self.grid_neighbors(x, y)
        for n in neighbor:
            r, c = n
            distance[r, c] = 1
        q = deque(self.grid_neighbors(x, y))

        # use queue to boost dijkstra algorithm
        while len(q) != 0:
            cr, cc = q.popleft()
            ndist = distance[cr, cc] + 1
            for n in self.grid_neighbors(cr, cc):
                nr, nc = n
                # check status
                if (board[nr, nc] != 0):
                    continue
                # update distance
                if ndist < distance[nr, nc]:
                    distance[nr, nc] = ndist
                # check visited
                if visited[nr, nc] == 0:
                    q.append(n)
                    visited[nr, nc] = 1
        return distance

    def compute_voronoi(self, board):
        position_x, position_y, enemy_x, enemy_y = self.get_position_by_board(board)
        player_costs = self.dijkstra(board, position_x, position_y)
        op_costs = self.dijkstra(board, enemy_x, enemy_y)
        pcount = 0
        opcount = 0
        maxcost = self.board_size * 2
        for r in range(self.board_size):
            for c in range(self.board_size):
                if player_costs[r, c] < op_costs[r, c] and player_costs[r, c] <= maxcost:
                    pcount += 1
                if op_costs[r, c] < player_costs[r, c] and op_costs[r, c] <= maxcost:
                    opcount += 1

        v = (pcount - opcount)
        return v

    def get_empty(self, board, depth, total):
        if depth <= 0:
            return total
        total += len(self.get_legal_moves_tree(board, self.player_id))
        for move in self.get_legal_moves_tree(board, self.player_id):
            board_tmp = self.examine_move_tree(board, move, self.player_id)
            total = self.get_empty(board_tmp, depth-1, total)
        return total

    def evaluate(self, board, player_id, connected):
        position_x, position_y, enemy_x, enemy_y = self.get_position_by_board(board)
        if not (-1 < position_x < self.board_size and -1 < position_y < self.board_size):
            if player_id == self.player_id:
                return -1000, True
            else:
                return 1000, True

        #return 0, False
        if player_id == self.player_id:
            # return self.compute_voronoi(board) + self.escape_from_corner(board, position_x, position_y), False
            if connected == "connected":
                return self.compute_voronoi(board), False
            else:
                return self.get_empty(board, 5, 0), False
        else:
            return random.random(), False


    def get_legal_moves_tree(self, board, player):
        position_x, position_y, enemy_x, enemy_y = self.get_position_by_board(board)
        moves = []
        if player == self.player_id:
            x = position_x
            y = position_y
        else:
            x = enemy_x
            y = enemy_y
        if (x != 0) and (board[x - 1, y] == 0):
            moves.append([x - 1, y])
        if (x != self.board_size - 1) and (board[x + 1, y] == 0):
            moves.append([x + 1, y])
        if (y != 0) and (board[x, y - 1] == 0):
            moves.append([x, y - 1])
        if (y != self.board_size - 1) and (board[x, y + 1] == 0):
            moves.append([x, y + 1])
        return moves

    def minimax_pruning(self, board, max_or_min, player, alpha, beta, depth, connected):
        score, is_finish = self.evaluate(board, player, connected)
        if is_finish or len(self.get_legal_moves_tree(board, player)) == 0 or depth <= 0:
            return score
        if player == self.player_id:
            player = 3
        else:
            player = 1
        if max_or_min == "max":
            best = -1000
            for move in self.get_legal_moves_tree(board, player):
                board_tmp = self.examine_move_tree(board, move, player)
                best = max(best, self.minimax_pruning(board_tmp, "min", player, alpha, beta, depth-1, connected))
                alpha = max(best, alpha)
                if alpha >= beta:
                    break
            return best
        else:
            best = 1000
            for move in self.get_legal_moves_tree(board, player):
                board_tmp = self.examine_move_tree(board, move, player)
                best = min(best, self.minimax_pruning(board_tmp, "max", player, alpha, beta, depth-1, connected))
                beta = min(best, beta)
                if alpha >= beta:
                    break
            return best

    # iterative deepening search with pruning
    def find_best_move(self, game):
        best_mov = game.get_legal_moves(self.player_id)[0]
        startTime = time.time()
        for depth in range(1, self.iterative_max_depth):
            best_val = -1000
            for move in game.get_legal_moves(self.player_id):
                board_tmp = self.examine_move_tree(game.board, move, self.player_id)
                if self.bfs(game.board) == True:
                    mov_val = self.minimax_pruning(board_tmp, "max", self.player_id, -1000, 1000, depth, "connected")
                else:
                    mov_val = self.minimax_pruning(board_tmp, "max", self.player_id, -1000, 1000, depth, "disconnected")
                if mov_val > best_val:
                    best_mov = move
                    best_val = mov_val
            # if process time bigger than 0.5, break
            if time.time() - startTime > 0.5:
                #print("more than 0.5 here, break")
                break
        return best_mov


class RandomAgent:

    def __init__(self, player_id):
        self.player_id = player_id

    def choose_move(self, game):
        # Get an array of legal moves from your current position.
        legal_moves = game.get_legal_moves(self.player_id)

        # Shuffle the legal moves and pick the first one. This is equivalent
        # to choosing a move randomly with no logic.
        np.random.shuffle(legal_moves)
        return legal_moves[0]

class TronGame:

    def __init__(self, board):
        self.size = 20
        self.board = board
        # Initialize our agents.
        self.agent1 = 1
        self.agent2 = 3

    def get_player_position(self, player_id, board=None):
        """
        Helper method which finds the coordinate of the specified player ID
        on the board.
        """

        if board is None:
            board = self.board
        coords = np.asarray(board == player_id).nonzero()
        coords = np.stack((coords[0], coords[1]), 1)
        coords = np.reshape(coords, (-1, 2))
        return coords[0]

    def get_legal_moves(self, player, board=None):
        """
        This method returns a list of legal moves for a given player ID and
        board.
        """

        if board is None:
            board = self.board

        # Get the current player position and then check for all possible
        # legal moves.
        prev = self.get_player_position(player, board)
        moves = []

        # Up
        if (prev[0] != 0) and (board[prev[0] - 1, prev[1]] == 0):
            moves.append([prev[0] - 1, prev[1]])
        # Down
        if (prev[0] != self.size - 1) and (board[prev[0] + 1, prev[1]] == 0):
            moves.append([prev[0] + 1, prev[1]])
        # Left
        if (prev[1] != 0) and (board[prev[0], prev[1] - 1] == 0):
            moves.append([prev[0], prev[1] - 1])
        # Right
        if (prev[1] != self.size - 1) and (board[prev[0], prev[1] + 1] == 0):
            moves.append([prev[0], prev[1] + 1])

        return moves

    def examine_move(self, player, coordinate, board):
        board_clone = board.copy()
        prev = self.get_player_position(player, board_clone)
        board_clone[prev] = 4
        board_clone[coordinate] = player
        return board_clone


def build_board(position, my_position, opponent_position):
    board = np.zeros((20, 20))
    all_position = position[1: -1].split('"},')
    player = json.loads(my_position)
    opponent = json.loads(opponent_position)
    player_x = int(np.floor(player["x"] / 30))
    player_y = int(np.floor(player["y"] / 30))
    #print("now position:", player_x, " ", player_y)
    board[player_x, player_y] = 1
    opponent_x = int(np.floor(opponent["x"] / 30))
    opponent_y = int(np.floor(opponent["y"] / 30))
    board[opponent_x, opponent_y] = 3

    for i in range(len(all_position)):
        if i != len(all_position) - 1:
            every_point = json.loads(all_position[i] + '"}')
        elif len(all_position[i]) > 0:
            every_point = json.loads(all_position[i])
        else:
            continue
        x = int(np.floor(every_point["point"]["x"] / 30))
        y = int(np.floor(every_point["point"]["y"] / 30))
        if (x != player_x or y != player_y) and (x != opponent_x or y != opponent_y):
            board[x, y] = 4

    return board, player_x, player_y
