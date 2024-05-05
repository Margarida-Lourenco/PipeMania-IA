# pipe.py: Template para implementação do projeto de Inteligência Artificial 2023/2024.
# Devem alterar as classes e funções neste ficheiro de acordo com as instruções do enunciado.
# Além das funções e classes sugeridas, podem acrescentar outras que considerem pertinentes.

# Grupo 24:
# 107137 Margarida Lourenço
# 107028 Inês Paredes

import sys
import numpy as np

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

pecasF = {'FC': (0, 1, 0, 0), 'FB': (0, 0, 0, 1), 'FD': (0, 0, 1, 0), 'FE': (1, 0, 0, 0)}
pecasB = {'BC': (1, 1, 1, 0), 'BB': (1, 0, 1, 1), 'BD': (0, 1, 1, 1), 'BE': (1, 1, 0, 1)}
pecasV = {'VC': (1, 1, 0, 0), 'VB': (0, 0, 1, 1), 'VD': (0, 1, 1, 0), 'VE': (1, 0, 0, 1)}
pecasL = {'LH': (1, 0, 1, 0), 'LV': (0, 1, 0, 1)}

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
        self.is_completed = False

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

    @staticmethod
    def parse_instance():
        """Lê o texto do standard input (stdin) e retorna uma instância da classe Board."""
        input_lines = sys.stdin.read().splitlines()
        matrix = [line.split() for line in input_lines if line.strip()]
        return Board(matrix).calculate_state()
    
    def calculate_state(self):
        """Calcula os valores do estado interno, para ser usado
        no tabuleiro inicial."""
        self.incompatible_pieces = []
        self.possible_pieces = {(r, c): [] for r in range(self.rows) for c in range(self.cols)}

        for r in range(self.rows):
            for c in range(self.cols):
                if self.is_piece_compatible(r, c):
                    self.incompatible_pieces.append((r, c))

        print(self.incompatible_pieces)
        for i in self.incompatible_pieces:
            print(i)
            print(self.possible_pieces[i])
            print(len(self.possible_pieces[i]))
            if len(self.possible_pieces[i]) == 1:
                self.set_piece(i[0], i[1], self.possible_pieces[i][0])
                self.get_next_possible_piece(i[0], i[1])
                self.incompatible_pieces.remove(i)

        return self
    
    def is_piece_compatible(self, row, col):
        """Verifica se a peça na posição (row, col) é compatível com as peças adjacentes."""
        # Verificar se a peça é compatível com suas peças adjacentes
        neighbors = self.get_neighbors(row, col)

        piece = self.get_value(row, col)

        self.corner_possibilities(row, col)

        if len(self.possible_pieces[(row, col)]) <= 1:
            return True

        pecas = pecasF if piece in pecasF else pecasB if piece in pecasB else pecasV \
            if piece in pecasV else pecasL if piece in pecasL else None
        if pecas is None:
            return False

        piece_connections = pecas[piece]
        
        for neighbor_piece, index in neighbors:
            if neighbor_piece is not None:
                neighbor_connections = pecasT[neighbor_piece]
                # Verificar se a conexão é mútua (ex: direita de uma deve conectar com esquerda da outra)
                opposite_index = (index + 2) % 4  # Acha o índice oposto
                if piece_connections[index] == neighbor_connections[opposite_index]:
                    return True
        return False  # Não há orientação compatível
    
    def get_incompatible_pieces(self):
        """Devolve uma lista de peças incompatíveis."""
        return self.incompatible_pieces
    
    def set_piece(self, row: int, col: int, piece: tuple):
        """Coloca uma peça no tabuleiro."""
        self.matrix[row][col] = piece

    def get_incompatible_pieces_count(self):
        """Devolve o número de peças incompatíveis."""
        return len(self.incompatible_pieces)
    
    def get_next_incompatible_piece(self):
        """Devolve a próxima peça incompatível."""
        return self.incompatible_pieces[0]
    
    def get_possible_pieces(self, row, col):
        """Devolve todas as possíveis peças que podem ser colocadas na posição (row, col)."""
        return self.possible_pieces[row][col]
    
    def corner_possibilities(self, row, col):
        """Devolve todas as possíveis peças que podem ser colocadas nas posições de canto."""
        piece = self.get_value(row, col)
        if piece in pecasF:
            possibilities = pecasF
        elif piece in pecasB:
            possibilities = pecasB
        elif piece in pecasV:
            possibilities = pecasV
        elif piece in pecasL:
            possibilities = pecasL
        else:
            return False
        
        neighbors = self.get_neighbors(row, col)
        esquerda, cima, direita, baixo = [neighbor[0] for neighbor in neighbors]

        if esquerda is None:
            possibilities = {piece_name: connections for piece_name, connections \
                             in possibilities.items() if connections[0] != 1}
        if baixo is None:
            possibilities = {piece_name: connections for piece_name, connections \
                             in possibilities.items() if connections[3] != 1}
        if direita is None:
            possibilities = {piece_name: connections for piece_name, connections \
                             in possibilities.items() if connections[2] != 1}
        if cima is None:
            possibilities = {piece_name: connections for piece_name, connections \
                             in possibilities.items() if connections[1] != 1}
        
        self.possible_pieces[(row, col)].extend(list(possibilities.keys()))

    
    def action_piece(self, row, col):
        """Devolve todas as possíveis peças que podem ser colocadas na posição (row, col)."""

        neighbors = self.get_neighbors(row, col)

        piece = self.get_value(row, col)

        pecas = pecasF if piece in pecasF else pecasB if piece in pecasB else pecasV \
            if piece in pecasV else pecasL if piece in pecasL else None

        if pecas is None:
            return
                   
        piece_connections = pecas[piece]

        for neighbor_piece, index in neighbors:
            if neighbor_piece is None:
                self.corner_possibilities(row, col)
                break
            neighbor_connections = pecasT[neighbor_piece]
            opposite_index = (index + 2) % 4
            # Verificar se a conexão é mútua (ex: direita de uma deve conectar com esquerda da outra)
            if piece_connections[index] != neighbor_connections[opposite_index]:
                # Se esta orientação for incompatível
                for possible_piece, possible_connections in pecas.items():
                    if possible_connections[index] == neighbor_connections[opposite_index]:
                        self.possible_pieces[(row, col)].extend(possible_piece)
    
    def get_next_possible_piece(self, row, col):
        """Recebe a posição que foi alterada, de forma a atualizar os valores
        possíveis para as posições afetadas"""
        if row and col is None:
            return None

        neighbors = self.get_neighbors(row, col)

        for neighbor_piece, index in neighbors:
            if neighbor_piece is not None:
                self.action_piece(row, col)

        return self.possible_pieces[(row, col)]

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
        possibilities = state.board.get_next_possible_piece(row, col)
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
        pass


if __name__ == "__main__":
    # TODO:
    # Ler o ficheiro do standard input,
    # Usar uma técnica de procura para resolver a instância,
    # Retirar a solução a partir do nó resultante,
    # Imprimir para o standard output no formato indicado.
    board = Board.parse_instance()
    problem = PipeMania(board)
    print(board.matrix)