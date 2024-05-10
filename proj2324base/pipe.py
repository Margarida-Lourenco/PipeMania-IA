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
                neighbors = self.get_neighbors(r, c) 
                self.first_action(r, c, neighbors)
   
        return self
 
    def set_piece(self, row: int, col: int, piece: tuple):
        """Coloca uma peça no tabuleiro."""
        matrix2 = self.matrix.copy()
        matrix2[row][col] = piece

        # Criar uma nova instância de Board com a matriz atualizada
        new_board = Board(matrix2)

        new_board.possible_pieces = self.possible_pieces.copy()
        new_board.incompatible_pieces = self.incompatible_pieces.copy()

        if len(new_board.possible_pieces[(row, col)]) == 1:
            new_board.incompatible_pieces.remove((row, col))

        return new_board
        
    def get_incompatible_pieces_count(self):
        """Devolve o número de peças incompatíveis."""
        return len(self.incompatible_pieces)
    
    def get_next_incompatible_piece(self):
        """Devolve a próxima peça incompatível."""
        return self.incompatible_pieces[-1]
    
    def get_possible_pieces(self, row, col):
        """Devolve todas as possíveis peças que podem ser colocadas na posição (row, col)."""
        return self.possible_pieces[(row, col)]
    
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


    def first_action(self, row, col, neighbors):
        """Determina as possíveis configurações de uma peça do tabuleiro."""
        piece = self.get_value(row, col)
 
        none_neighbors = [(neighbor_piece, index) for neighbor_piece, index in neighbors if neighbor_piece is None]

        if (piece in pecasV and len(none_neighbors) == 2) or ((piece in pecasL or piece in pecasB) and len(none_neighbors) == 1):
            pecas = pecasL if piece in pecasL else pecasB if piece in pecasB else pecasV if piece in pecasV else None
            for piece_name, orientation in pecas.items():
                is_compatible = True
                for _, index in none_neighbors:
                    if orientation[index] == 1:
                        is_compatible = False
                        break
                if is_compatible:
                    self.matrix[row][col] = piece_name
                    self.possible_pieces[(row, col)].append(piece_name)
        
        else:
            pecas = pecasB if piece in pecasB else pecasV if piece in pecasV else pecasL if piece in pecasL else pecasF if piece in pecasF else None
            for piece_name, orientation in pecas.items():
                is_compatible = True
                for neighbor_piece, neighbor_index in neighbors:

                    if neighbor_piece is None:
                        if orientation[neighbor_index] == 1:
                            is_compatible = False   

                    elif piece_name in pecasF and neighbor_piece in pecasF:
                        neighbor_connections = pecasF[neighbor_piece]
                        opposite_index = (neighbor_index + 2) % 4

                        if orientation[neighbor_index] == neighbor_connections[opposite_index] == 1:      
                            is_compatible = False
    
                    elif neighbor_piece in self.possible_pieces[self.determine_neighbor_position(row, col, neighbor_index)]\
                        and len(self.possible_pieces[self.determine_neighbor_position(row, col, neighbor_index)]) == 1:
                        neighbor_connections = pecasT[neighbor_piece]
                        opposite_index = (neighbor_index + 2) % 4
                        if (piece_name in pecasF and neighbor_piece in pecasF) and orientation[neighbor_index] == 1:
                            is_compatible = False

                        elif orientation[neighbor_index] != neighbor_connections[opposite_index]:
                            is_compatible = False

                if is_compatible:
                    self.possible_pieces[(row, col)].append(piece_name)

        
        if len(self.possible_pieces[(row, col)]) > 1 or len(self.possible_pieces[(row, col)]) == 0:
            self.incompatible_pieces.append((row, col))
        else:
            self.matrix[row][col] = self.possible_pieces[(row, col)][0]

        print(self.possible_pieces)


    def action_piece(self, row, col):
        """Determina as possíveis configurações de uma peça no meio do tabuleiro, considerando apenas os vizinhos que não estão em self.incompatible_pieces."""
        piece = self.get_value(row, col)
        pecas = pecasF if piece in pecasF else pecasB if piece in pecasB else pecasV if piece in pecasV else pecasL if piece in pecasL else None

        neighbors = self.get_neighbors(row, col)

        filtered_neighbors = [
            (neighbor_piece, i) for i, (neighbor_piece, _) in enumerate(neighbors)
            if self.determine_neighbor_position(row, col, i) is col is not None and row is not None  # Verifica se a posição do vizinho é válida
            and len(self.possible_pieces[self.determine_neighbor_position(row, col, i)]) == 1  # Verifica se há apenas uma possibilidade de peça
        ]
        #print(piece)

        for piece_name, orientation in pecas.items():
            is_compatible = True
            # Verifica a compatibilidade com vizinhos filtrados
            for neighbor_piece, neighbor_index in filtered_neighbors:
                neighbor_connections = pecasT[neighbor_piece]
                opposite_index = (neighbor_index + 2) % 4
                if orientation[neighbor_index] != neighbor_connections[opposite_index]:
                    is_compatible = False
                    break

            if is_compatible:
                self.possible_pieces[(row, col)].append(piece_name)
                #print(self.possible_pieces)
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
        node.state.board
        return node.state.board.get_incompatible_pieces_count()

if __name__ == "__main__":
    # TODO:
    # Ler o ficheiro do standard input,
    # Usar uma técnica de procura para resolver a instância,
    # Retirar a solução a partir do nó resultante,
    # Imprimir para o standard output no formato indicado.
    board = Board.parse_instance()
    problem = PipeMania(board)
    goal_node = depth_first_tree_search(problem)
    goal_node.state.board.print_matrix()