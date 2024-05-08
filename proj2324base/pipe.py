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

pecasF = {'FE': (1, 0, 0, 0), 'FC': (0, 1, 0, 0), 'FD': (0, 0, 1, 0), 'FB': (0, 0, 0, 1)}
pecasB = {'BE': (1, 1, 0, 1), 'BC': (1, 1, 1, 0), 'BD': (0, 1, 1, 1), 'BB': (1, 0, 1, 1)}
pecasV = {'VE': (1, 0, 0, 1), 'VC': (1, 1, 0, 0), 'VD': (0, 1, 1, 0), 'VB': (0, 0, 1, 1)}
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

    @staticmethod
    def parse_instance():
        """Lê o texto do standard input (stdin) e retorna uma instância da classe Board."""
        input_lines = sys.stdin.read().splitlines()
        matrix = [line.split() for line in input_lines if line.strip()]
        return Board(matrix).calculate_state()
    
    def calculate_state(self):
        """Calcula os valores do estado interno, para ser usado no tabuleiro inicial."""
        self.incompatible_pieces = []
        self.possible_pieces = {(r, c): [] for r in range(self.rows) for c in range(self.cols)}

        for r in range(self.rows):
            for c in range(self.cols):
                self.action_piece(r, c)
                if len(self.possible_pieces[(r, c)]) > 1:
                    self.incompatible_pieces.append((r, c))
                elif len(self.possible_pieces[(r, c)]) == 0:
                    return self
                else:
                    self.incompatible_pieces.insert(0, (r, c))

        return self
 
    def set_piece(self, row: int, col: int, piece: tuple):
        """Coloca uma peça no tabuleiro."""
        self.matrix[row][col] = piece
        if len(self.possible_pieces[(row, col)]) == 0:
            return self
        
        elif len(self.possible_pieces[(row, col)]) == 1:
            self.incompatible_pieces.remove((row, col))

        self.action_piece(row, col)
        
    def get_incompatible_pieces_count(self):
        """Devolve o número de peças incompatíveis."""
        return len(self.incompatible_pieces)
    
    def get_next_incompatible_piece(self):
        """Devolve a próxima peça incompatível."""
        return self.incompatible_pieces[0]
    
    def get_possible_pieces(self, row, col):
        """Devolve todas as possíveis peças que podem ser colocadas na posição (row, col)."""
        return self.possible_pieces[(row, col)]
    
    def action_piece(self, row, col):
        """Determina as possíveis configurações de uma peça, dependendo da posição no tabuleiro."""
        neighbors = self.get_neighbors(row, col)  # Lista de peças adjacentes

        if any(neighbor_piece is None for neighbor_piece, _ in neighbors):
            self.action_piece_edge(row, col, neighbors)
        else:
            self.action_piece_middle(row, col, neighbors)

    def action_piece_edge(self, row, col, neighbors):
        """Determina as possíveis configurações de uma peça nas bordas do tabuleiro."""
        piece = self.get_value(row, col)
        pecas = pecasF if piece in pecasF else pecasB if piece in pecasB else pecasV \
            if piece in pecasV else pecasL if piece in pecasL else None

        for piece_name, orientation in pecas.items():
            is_compatible = True
            for _, (neighbor_piece, index) in enumerate(neighbors):
                if neighbor_piece is None:
                    # Verifica apenas as conexões que são None
                    if orientation[index] == 1:
                        is_compatible = False
                        break

            if is_compatible and piece != piece_name:
                self.possible_pieces[(row, col)].append(piece_name)


    def action_piece_middle(self, row, col, neighbors):
        """Determina as possíveis configurações de uma peça no meio do tabuleiro."""
        piece = self.get_value(row, col)
        pecas = pecasF if piece in pecasF else pecasB if piece in pecasB else pecasV \
            if piece in pecasV else pecasL if piece in pecasL else None

        for piece_name, orientation in pecas.items():
            is_compatible = True
            for _, (neighbor_piece, index) in enumerate(neighbors):
                if neighbor_piece is None:
                    continue  # Não faz verificação, pois estamos no meio do tabuleiro
                else:
                    neighbor_connections = pecasT[neighbor_piece]
                    opposite_index = (index + 2) % 4
                    if orientation[index] != neighbor_connections[opposite_index]:
                        is_compatible = False
                        break

            if is_compatible and piece != piece_name:
                self.possible_pieces[(row, col)].append(piece_name)
        
        if len(self.possible_pieces[(row, col)]) == 0:
            for piece_name, _ in pecas.items():
                self.possible_pieces[(row, col)].append(piece_name)
            

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

        possibilities = state.board.get_possible_pieces(row, col)
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
        if node.state.board:
            return node.state.board.get_incompatible_pieces_count()
        else:
            return 0


if __name__ == "__main__":
    # TODO:
    # Ler o ficheiro do standard input,
    # Usar uma técnica de procura para resolver a instância,
    # Retirar a solução a partir do nó resultante,
    # Imprimir para o standard output no formato indicado.
    board = Board.parse_instance()
    problem = PipeMania(board)
    goal_node = astar_search(problem)
    goal_node.state.board.print_matrix()