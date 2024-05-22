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
        self.incompatible_pieces = []
        self.possible_pieces = np.empty((self.rows, self.cols), dtype=object)

        for r in range(self.rows):
            for c in range(self.cols):
                self.possible_pieces[r, c] = []

        for r in range(self.rows):
            for c in range(self.cols):
                none_neighbors = []
                filtered_neighbors = []
                piece = self.get_value(r, c)
                pecas = pecasL if piece in pecasL else pecasB if piece in pecasB else pecasV if piece in pecasV else pecasF if piece in pecasF else None

                for i in range(4):
                    row, col = self.determine_neighbor_position(r, c, i)
                    if row is not None and col is not None:
                        if len(self.possible_pieces[row, col]) == 1:
                            filtered_neighbors.append((self.possible_pieces[row, col][0], i))
                    else:
                        none_neighbors = none_neighbors + [(None, i)]


                if len(none_neighbors) != 0:
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
                            self.possible_pieces[r, c] = self.possible_pieces[r, c] + [piece_name]

                    if len(self.possible_pieces[r, c]) > 1:
                        self.incompatible_pieces.insert(0, (r, c))
                    else:
                        self.matrix[r][c] = self.possible_pieces[r, c][0]

                else:
                    for piece_name in pecas:
                        orientation = pecasT[piece_name]
                        is_compatible = True
                        for neighbor_piece, index in filtered_neighbors:
                            neighbor_connections = pecasT[neighbor_piece]
                            if piece_name in pecasF and neighbor_piece in pecasF and orientation[index] == 1:
                                is_compatible = False
                                break

                            elif orientation[index] != neighbor_connections[(index + 2) % 4]:
                                is_compatible = False
                                break
                                
                        if is_compatible:
                            self.possible_pieces[r, c] = self.possible_pieces[r, c] + [piece_name]

                    if len(self.possible_pieces[r, c]) > 1:
                        self.incompatible_pieces.insert(0, (r, c))
                    else:
                        self.matrix[r][c] = self.possible_pieces[r, c][0]

        return self

    def action_piece(self, row, col):
        """Determina ações possíveis para a peça na posição (row, col)."""
        filtered_neighbors = []

        for i in range(4):
            r, c = self.determine_neighbor_position(row, col, i)
            if r is not None and c is not None:
                if (r, c) not in self.incompatible_pieces:
                    filtered_neighbors.append((self.get_value(r, c), i))

        c_neighbors = len(filtered_neighbors)

        if c_neighbors != 0:
            for piece_name in self.possible_pieces[row, col]:
                orientation = pecasT[piece_name]
                is_compatible = True
                for neighbor_piece, index in filtered_neighbors:
                    neighbor_connections = pecasT[neighbor_piece]
                    if piece_name in pecasF and neighbor_piece in pecasF and orientation[index] == 1:
                        is_compatible = False
                        break

                    elif orientation[index] != neighbor_connections[(index + 2) % 4]:
                        is_compatible = False
                        break
                    
                if not is_compatible:
                    self.possible_pieces[row, col] = [piece for piece in self.possible_pieces[row, col] if piece != piece_name]
                
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
        lista = state.board.incompatible_pieces
        if len(lista) == 0:
            return []
        
        row , col = lista[0]

        possibilities = state.board.action_piece(row, col)
        return map(lambda piece: (row, col, piece), possibilities)

    def result(self, state: PipeManiaState, action):
        """Retorna o estado resultante de executar a 'action' sobre
        'state' passado como argumento. A ação a executar deve ser uma
        das presentes na lista obtida pela execução de
        self.actions(state)."""
        (row, col, piece) = action
        new_board = Board(np.copy(state.board.matrix))
        new_board.matrix[row][col] = piece

        new_board.incompatible_pieces = state.board.incompatible_pieces[1:]
        new_board.possible_pieces = np.copy(state.board.possible_pieces)

        return PipeManiaState(new_board)

    def goal_test(self, state: PipeManiaState):
        """Retorna True se e só se o estado passado como argumento é
        um estado objetivo. Deve verificar se todas as posições do tabuleiro
        estão preenchidas de acordo com as regras do problema."""
        """Verifica se todas as peças do tabuleiro formam um único componente conectado."""
        visited = np.zeros((state.board.rows, state.board.cols), dtype=bool)
        stack = []
        
        stack.append((0, 0))
        # DFS
        while stack:
            row, col = stack.pop()
            if not visited[row][col]:
                visited[row][col] = True
                neighbors = state.board.get_neighbors(row, col)
                for neighbor_piece, index in neighbors:
                    if neighbor_piece is not None:
                        nr, nc = state.board.determine_neighbor_position(row, col, index)
                        if not visited[nr][nc]:
                            # Verifica se as peças são compatíveis
                            piece_connections = pecasT[state.board.get_value(row, col)]
                            neighbor_connections = pecasT[neighbor_piece]
                            if piece_connections[index] == neighbor_connections[(index + 2) % 4] == 1:
                                stack.append((nr, nc))
                            elif piece_connections[index] != neighbor_connections[(index + 2) % 4]:
                                return False
        
        # Verifica se todas as peças foram visitadas
        for r in range(state.board.rows):
            for c in range(state.board.cols):
                if state.board.matrix[r][c] is not None and not visited[r][c]:
                    return False
        return True
    
    def h(self, node):
        """Função heurística utilizada no problema."""
        return len(node.state.board.incompatible_pieces)

if __name__ == "__main__":
    board = Board.parse_instance()
    problem = PipeMania(board)
    goal_node = depth_first_tree_search(problem)
    goal_node.state.board.print_matrix()