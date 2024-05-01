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
    iterative_deepening_search,
)


class PipeManiaState:
    state_id = 0

    def __init__(self, board):
        self.board = board
        self.id = PipeManiaState.state_id
        PipeManiaState.state_id += 1

    def __lt__(self, other):
        return self.id < other.id

    # TODO: outros metodos da classe

class Piece:
    def __init__(self, piece_type, orientation):
        self.piece_type = piece_type
        self.orientation = orientation

class Board:
    """Representação interna de um tabuleiro de PipeMania."""
    
    def __init__(self, matrix):
        self.matrix = np.array(matrix)
        self.rows, self.cols = self.matrix.shape
        self.colors = {}  # Dicionário para armazenar as cores das peças
        self.is_invalid = False

    def get_value(self, row: int, col: int) -> Piece:
        """Devolve a peça na respetiva posição do tabuleiro."""
        if 0 <= row < self.rows and 0 <= col < self.cols:
            piece_info = self.matrix[row][col]
            if isinstance(piece_info, Piece):
                return piece_info
            # Se não for, criar uma nova instância de Piece
            piece = Piece(piece_info[0], piece_info[1])
            return piece
        return None  # Retorna None se a posição estiver fora dos limites
    
    def get_row(self, row: int) -> list[Piece]:
        """Devolve a linha correspondente ao índice passado como argumento."""
        return [self.get_value(row, col) for col in range(self.cols)]
    
    def get_col(self, col: int) -> list[Piece]:
        """Devolve a coluna correspondente ao índice passado como argumento."""
        return [self.get_value(row, col) for row in range(self.rows)]

    def adjacent_vertical_values(self, row: int, col: int) -> tuple[Piece, Piece]:
        """Devolve os valores imediatamente acima e abaixo, respectivamente."""
        above = self.get_value(row-1, col)
        below = self.get_value(row+1, col)
        return (above, below)

    def adjacent_horizontal_values(self, row: int, col: int) -> tuple[Piece, Piece]:
        """Devolve os valores imediatamente à esquerda e à direita, respectivamente."""
        left = self.get_value(row, col-1)
        right = self.get_value(row, col+1)
        return (left, right)

    @staticmethod
    def parse_instance():
        """Lê o texto do standard input (stdin) e retorna uma instância da classe Board."""
        input_lines = sys.stdin.read().splitlines()
        matrix = [line.split() for line in input_lines if line.strip()] # Verifica se a linha está vazia após remover os espaços
        return Board(matrix)


    # TODO: outros metodos da classe

    def calculate_state(self):
        """Calcula o estado do tabuleiro."""
        self.colors = {}  # Limpa o dicionário de cores
        color = 1  # Começa com a cor 1

        for row in range(self.rows):
            for col in range(self.cols):
                piece = self.get_value(row, col)
                if piece:
                    if (row, col) not in self.colors:
                        self._dfs_coloring(row, col, piece, color)
                        color += 1

        # Verifica se há subconjuntos de cores
        self.is_completed()

    def _dfs_coloring(self, row: int, col: int, piece: Piece, color: int):
        """Método auxiliar para colorir as peças."""
        if (row, col) in self.colors:
            return
        self.colors[(row, col)] = color

        above, below = self.adjacent_vertical_values(row, col)
        left, right = self.adjacent_horizontal_values(row, col)

        if above and above.piece_type == piece.piece_type:
            self._dfs_coloring(row-1, col, above, color)
        if below and below.piece_type == piece.piece_type:
            self._dfs_coloring(row+1, col, below, color)
        if left and left.piece_type == piece.piece_type:
            self._dfs_coloring(row, col-1, left, color)
        if right and right.piece_type == piece.piece_type:
            self._dfs_coloring(row, col+1, right, color)

    def set_piece(self, row: int, col: int, piece: str):
        """Coloca uma peça no tabuleiro."""
        self.matrix[row][col] = piece

    
    def get_possibilities(self, row: int, col: int):
        """Devolve as possibilidades de peças que podem ser colocadas numa determinada posição."""
        piece = self.get_value(row, col)
        if piece:
            return []
        
        above, below = self.adjacent_vertical_values(row, col)
        left, right = self.adjacent_horizontal_values(row, col)
        possibilities = []
        for piece in ['A', 'B', 'C', 'D', 'E']:
            new_piece = self.get_piece_orientation(piece, above, below, left, right)
            possibilities.append((row, col, new_piece))
        return possibilities

    def is_completed(self):
        """Verifica se o tabuleiro está completo."""
        unique_colors = set(self.colors.values())
        if len(unique_colors) > 1:
            self.is_invalid = True
        else:
            self.is_invalid = False

    def get_heuristic_value(self):
        """Devolve o valor heurístico do tabuleiro."""
        self.calculate_state()
        return len(self.colors)

    def get_piece_orientation(piece: str, above: str, below: str, left: str, right: str) -> str:
        """Determina a orientação correta da peça com base nas peças adjacentes."""
        if piece[1] == 'C':  # Se a orientação atual for "C"
            if above and above[1] == 'B':
                return piece[0] + 'B'
            elif below and below[1] == 'B':
                return piece[0] + 'E'
            elif left and left[1] == 'D':
                return piece[0] + 'D'
            elif right and right[1] == 'D':
                return piece[0] + 'C'
        elif piece[1] == 'B':  # Se a orientação atual for "B"
            if above and above[1] == 'C':
                return piece[0] + 'C'
            elif below and below[1] == 'C':
                return piece[0] + 'D'
            elif left and left[1] == 'E':
                return piece[0] + 'E'
            elif right and right[1] == 'E':
                return piece[0] + 'B'
        elif piece[1] == 'D':  # Se a orientação atual for "D"
            if above and above[1] == 'C':
                return piece[0] + 'C'
            elif below and below[1] == 'C':
                return piece[0] + 'D'
            elif left and left[1] == 'E':
                return piece[0] + 'E'
            elif right and right[1] == 'E':
                return piece[0] + 'B'
        elif piece[1] == 'E':  # Se a orientação atual for "E"
            if above and above[1] == 'B':
                return piece[0] + 'B'
            elif below and below[1] == 'B':
                return piece[0] + 'E'
            elif left and left[1] == 'D':
                return piece[0] + 'D'
            elif right and right[1] == 'D':
                return piece[0] + 'C'
        return piece

    def process_board(input_board: list[list[str]]) -> list[list[str]]:
        """Processa o tabuleiro, determinando a orientação correta para cada peça."""
        output_board = []
        for i, row in enumerate(input_board):
            new_row = []
            for j, piece in enumerate(row):
                above = input_board[i - 1][j] if i > 0 else None
                below = input_board[i + 1][j] if i < len(input_board) - 1 else None
                left = input_board[i][j - 1] if j > 0 else None
                right = input_board[i][j + 1] if j < len(row) - 1 else None
                new_piece = board.get_piece_orientation(piece, above, below, left, right)
                new_row.append(new_piece)
            output_board.append(new_row)
        return output_board


class PipeMania(Problem):
    def __init__(self, board: Board):
        """O construtor especifica o estado inicial."""
        state = PipeManiaState(board)
        super().__init__(state)
        pass

    def actions(self, state: PipeManiaState):
        """Retorna uma lista de ações que podem ser executadas a
        partir do estado passado como argumento."""
        if state.board.is_invalid or state.board.is_completed():
            return []
        
        rows, cols = state.board.rows, state.board.cols

        possibilites = state.board.get_possibilities(rows, cols)
        return possibilites

    def result(self, state: PipeManiaState, action):
        """Retorna o estado resultante de executar a 'action' sobre
        'state' passado como argumento. A ação a executar deve ser uma
        das presentes na lista obtida pela execução de
        self.actions(state)."""

        (row, col, piece) = action
        return PipeManiaState(state.board.place_piece(row, col, piece))

    def goal_test(self, state: PipeManiaState):
        """Retorna True se e só se o estado passado como argumento é
        um estado objetivo. Deve verificar se todas as posições do tabuleiro
        estão preenchidas de acordo com as regras do problema."""
        return state.board.is_invalid

    def h(self, node: Node):
        """Função heuristica utilizada para a procura A*."""
        board = node.state.board
        return board.get_heuristic_value()

    # TODO: outros metodos da classe


if __name__ == "__main__":
    # TODO:
    # Ler o ficheiro do standard input,
    # Usar uma técnica de procura para resolver a instância,
    # Retirar a solução a partir do nó resultante,
    # Imprimir para o standard output no formato indicado.
    board = Board.parse_instance()
    pipe = PipeMania(board)
    goal_node = iterative_deepening_search(pipe)
    solution = goal_node.solution()

    pass
