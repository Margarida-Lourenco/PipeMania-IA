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


class Board:
    """Representação interna de um tabuleiro de PipeMania."""
    
    def __init__(self, matrix):
        self.matrix = np.array(matrix)
        self.rows, self.cols = self.matrix.shape
        self.is_invalid = False

    def get_value(self, row: int, col: int) -> str:
        """Devolve o valor na respetiva posição do tabuleiro."""
        if 0 <= row < self.rows and 0 <= col < self.cols:
            return self.matrix[row][col]
        return None  # Retorna None se a posição estiver fora dos limites
    
    def get_row(self, row: int) -> list[str]:
        """Devolve a linha correspondente ao índice passado como argumento."""
        return self.matrix[row]
    
    def get_col(self, col: int) -> list[str]:
        """Devolve a coluna correspondente ao índice passado como argumento."""
        return self.matrix[:, col]

    def adjacent_vertical_values(self, row: int, col: int) -> tuple[str, str]:
        """Devolve os valores imediatamente acima e abaixo, respectivamente."""
        above = self.get_value(row-1, col)
        below = self.get_value(row+1, col)
        return (above, below)

    def adjacent_horizontal_values(self, row: int, col: int) -> tuple[str, str]:
        """Devolve os valores imediatamente à esquerda e à direita, respectivamente."""
        left = self.get_value(row, col-1)
        right = self.get_value(row, col+1)
        return (left, right)

    @staticmethod
    def parse_instance():
        """Lê o texto do standard input (stdin) e retorna uma instância da classe Board."""
        input_lines = sys.stdin.read().splitlines()
        matrix = [np.array(line.split()) for line in input_lines if line.strip()] # Verifica se a linha está vazia após rem os espaços
        #print(input_lines)
        #print(matrix)
        return Board(matrix)


    # TODO: outros metodos da classe

    def calculate_state(self, state: PipeManiaState):
        """Calcula o estado do tabuleiro."""
        pass

    def set_piece(self, row: int, col: int, piece: str):
        """Coloca uma peça no tabuleiro."""
        pass
    
    def get_possibilities(self, row: int, col: int):
        """Devolve as possibilidades de peças que podem ser colocadas numa determinada posição."""
        pass

    def is_completed(self):
        """Verifica se o tabuleiro está completo."""
        pass

    def get_heuristic_value(self):
        """Devolve o valor heurístico do tabuleiro."""
        pass
    

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
        return state.board.is_completed()

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
    #pipe = PipeMania(board)
    #goal_node = iterative_deepening_search(pipe)
    #print(goal_node.state.board.matrix)
    #piece = board.adjacent_vertical_values(2, 2)
    #print(piece)
    print(board.matrix)

    pass
