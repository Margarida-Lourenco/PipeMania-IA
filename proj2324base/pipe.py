# pipe.py: Template para implementação do projeto de Inteligência Artificial 2023/2024.
# Devem alterar as classes e funções neste ficheiro de acordo com as instruções do enunciado.
# Além das funções e classes sugeridas, podem acrescentar outras que considerem pertinentes.

# Grupo 24:
# 107137 Margarida Lourenço
# 107028 Inês Paredes

import sys
import numpy as np
import random

from search import (
    Problem,
    Node,
    astar_search,
    breadth_first_tree_search,
    depth_first_tree_search,
    greedy_search,
    recursive_best_first_search,
)

pecasT = {'FC': (0, 1, 0, 0), 'FB': (0, 0, 0, 1), 'FD': (0, 0, 1, 0), 'FE': (1, 0, 0, 0),
            'BC': (1, 1, 1, 0), 'BB': (1, 0, 1, 1), 'BD': (0, 1, 1, 1), 'BE': (1, 1, 0, 1),
            'VC': (1, 1, 0, 0), 'VB': (0, 0, 1, 1), 'VD': (0, 1, 1, 0), 'VE': (1, 0, 0, 1),
            'LH': (1, 0, 1, 0), 'LV': (0, 1, 0, 1)}

pecasF = {'FE', 'FC', 'FD', 'FB'}
pecasB = {'BE', 'BC', 'BD', 'BB'}
pecasV = {'VE', 'VC', 'VD', 'VB'}
pecasL = {'LH', 'LV'}

class PipeManiaState:
    state_id = 0

    def __init__(self, board):
        self.board = board
        self.id = PipeManiaState.state_id
        PipeManiaState.state_id += 1

    def __lt__(self, other):
        return self.id < other.id

class Board:
    """Representação interna de um tabuleiro de PipeMania."""
    
    def __init__(self, matrix):
        self.matrix = np.array(matrix)
        self.rows, self.cols = self.matrix.shape
        self.incompatible_pieces = []

    def print_matrix(self):
        for row in self.matrix:
            print("\t".join(str(item) for item in row))

    def get_value(self, row: int, col: int) -> tuple:
        """Devolve a peça na respetiva posição do tabuleiro."""
        if 0 <= row < self.rows and 0 <= col < self.cols:
            return self.matrix[row][col]
        return None

    def get_neighbors(self, row, col):
        """Retorna uma lista de tuplas contendo os valores dos vizinhos e seus índices de direção."""
        neighbors = [
            (self.get_value(row, col-1), 0),  # Esquerda
            (self.get_value(row-1, col), 1),  # Cima
            (self.get_value(row, col+1), 2),  # Direita
            (self.get_value(row+1, col), 3)   # Baixo
        ]
        return neighbors
    
    def determine_neighbor_position(self, row, col, index):
        """Determina a posição do vizinho com base no índice."""
        if index == 0:  # Esquerda
            return row, col-1 if col-1 >= 0 else None
        elif index == 1:  # Cima
            return row-1, col if row-1 >= 0 else None
        elif index == 2:  # Direita
            return row, col+1 if col+1 < self.cols else None
        elif index == 3:  # Baixo
            return row+1, col if row+1 < self.rows else None

    @staticmethod
    def parse_instance():
        """Lê o texto do standard input (stdin) e retorna uma instância da classe Board."""
        input_lines = sys.stdin.read().splitlines()
        matrix = [line.split() for line in input_lines if line.strip()]
        return Board(matrix).calculate_state()

    def calculate_state(self):
        """Calcula os valores do estado interno, para ser usado no tabuleiro inicial."""
        corners = []
        edges = []
        middles = []

        for r in range(self.rows):
            for c in range(self.cols):
                if (r in [0, self.rows - 1] and c in [0, self.cols - 1]):
                    corners.append((r, c))
                elif (r in [0, self.rows - 1] or c in [0, self.cols - 1]):
                    edges.append((r, c))
                else:
                    middles.append((r, c))
        
        self.incompatible_pieces = corners + edges + middles
        return self
 
    def set_piece(self, row: int, col: int, piece: tuple):
        """Coloca uma peça no tabuleiro."""
        self.matrix[row][col] = piece

        # Atualiza a lista de peças incompatíveis
        if (row, col) in self.incompatible_pieces:
            self.incompatible_pieces.remove((row, col))
            self.incompatible_pieces.append((row, col))

        return self
        
    def get_incompatible_pieces_count(self):
        """Devolve o número de peças incompatíveis."""
        return len(self.incompatible_pieces)
    
    def get_next_incompatible_piece(self):
        """Devolve a próxima peça incompatível."""
        return self.incompatible_pieces[0]

    def action_piece(self, row, col):
        """Determina ações possíveis para a peça na posição (row, col)."""
        filtered_neighbors = []
        possible_pieces = []
        piece = self.get_value(row, col)
        neighbors = self.get_neighbors(row, col)
        pecas = pecasL if piece in pecasL else pecasB if piece in pecasB else pecasV if piece in pecasV else pecasF if piece in pecasF else None

        none_neighbors = [(neighbor_piece, index) for neighbor_piece, index in neighbors if neighbor_piece is None]

        for i in range(4):
            if None not in self.determine_neighbor_position(row, col, i):
                r, c = self.determine_neighbor_position(row, col, i)
                if (r, c) not in self.incompatible_pieces:
                    filtered_neighbors.append((self.get_value(r, c), i))

        c_neighbors = len(filtered_neighbors)
        c_none_neighbors = len(none_neighbors)

        if c_neighbors == 0 and c_none_neighbors != 0:
            for piece_name in pecas:
                orientation = pecasT[piece_name]
                is_compatible = all(orientation[index] != 1 for _, index in none_neighbors)
                if is_compatible:
                    possible_pieces.append(piece_name)
        
        elif c_neighbors != 0 and c_none_neighbors != 0:
            for piece_name in pecas:
                orientation = pecasT[piece_name]
                is_compatible = all(orientation[index] != 1 for _, index in none_neighbors)
                for neighbor_piece, index in filtered_neighbors:
                    neighbor_connections = pecasT[neighbor_piece]
                    if piece_name in pecasF and neighbor_piece in pecasF and orientation[index] == 1:
                        is_compatible = False
                        break

                    elif orientation[index] != neighbor_connections[(index + 2) % 4]:
                        is_compatible = False
                        break
                    
                if is_compatible:
                    possible_pieces.append(piece_name)
        
        elif c_neighbors != 0 and c_none_neighbors == 0:
            for piece_name in pecas:
                is_compatible = True
                orientation = pecasT[piece_name]
                for neighbor_piece, index in filtered_neighbors:
                    neighbor_connections = pecasT[neighbor_piece]
                    if piece_name in pecasF and neighbor_piece in pecasF and orientation[index] == 1:
                        is_compatible = False
                        break
                    elif orientation[index] != neighbor_connections[(index + 2) % 4]:
                        is_compatible = False
                        break
                    
                if is_compatible:
                    possible_pieces.append(piece_name)
        else:
            pecas_list = list(pecas)
            possible_pieces = random.sample(pecas_list, min(2, len(pecas_list)))

        if len(possible_pieces) == 1:
            self.incompatible_pieces.remove((row, col))
                
        return possible_pieces

    def connections_count(self):
        """Conta o número de peças que não estão ligadas corretamente."""
        count = 0
        for row in range(self.rows):
            for col in range(self.cols):
                piece = self.get_value(row, col)
                neighbors = self.get_neighbors(row, col)
                for neighbor_piece, index in neighbors:
                    if neighbor_piece is not None:
                        piece_connections = pecasT[piece]
                        neighbor_connections = pecasT[neighbor_piece]
                        if piece_connections[index] != neighbor_connections[(index + 2) % 4]:
                            count += 1
                    elif neighbor_piece is None:
                        piece_connections = pecasT[piece]
                        if piece_connections[index] == 1:
                            count += 1
        return count

class PipeMania(Problem):
    def __init__(self, board: Board):
        """O construtor especifica o estado inicial."""
        state = PipeManiaState(board)
        super().__init__(state)
        pass

    def actions(self, state: PipeManiaState):
        """Retorna uma lista de ações que podem ser executadas a
        partir do estado passado como argumento."""
        if state.board.get_incompatible_pieces_count() == 0:
            return []

        row , col = state.board.get_next_incompatible_piece()

        possibilities = state.board.action_piece(row, col)
        return map(lambda piece: (row, col, piece), possibilities)

    def result(self, state: PipeManiaState, action):
        """Retorna o estado resultante de executar a 'action' sobre
        'state' passado como argumento. A ação a executar deve ser uma
        das presentes na lista obtida pela execução de
        self.actions(state)."""
        (row, col, piece) = action
        return PipeManiaState(state.board.set_piece(row, col, piece))

    def goal_test(self, state: PipeManiaState):
        """Retorna True se e só se o estado passado como argumento é
        um estado objetivo. Deve verificar se todas as posições do tabuleiro
        estão preenchidas de acordo com as regras do problema."""
        return state.board.get_incompatible_pieces_count() == 0
    
    def h(self, node):
        total_pieces = node.state.board.rows * node.state.board.cols
        correct_pieces = total_pieces - node.state.board.get_incompatible_pieces_count()
        return correct_pieces

if __name__ == "__main__":
    board = Board.parse_instance()
    problem = PipeMania(board)
    goal_node = recursive_best_first_search(problem)
    goal_node.state.board.print_matrix()