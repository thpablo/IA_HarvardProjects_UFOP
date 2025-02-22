import sys

from crossword import *


class CrosswordCreator():

    def __init__(self, crossword):
        """
        Create new CSP crossword generate.
        """
        self.crossword = crossword
        self.domains = {
            var: self.crossword.words.copy()
            for var in self.crossword.variables
        }

    def letter_grid(self, assignment):
        """
        Return 2D array representing a given assignment.
        """
        letters = [
            [None for _ in range(self.crossword.width)]
            for _ in range(self.crossword.height)
        ]
        for variable, word in assignment.items():
            direction = variable.direction
            for k in range(len(word)):
                i = variable.i + (k if direction == Variable.DOWN else 0)
                j = variable.j + (k if direction == Variable.ACROSS else 0)
                letters[i][j] = word[k]
        return letters

    def print(self, assignment):
        """
        Print crossword assignment to the terminal.
        """
        letters = self.letter_grid(assignment)
        for i in range(self.crossword.height):
            for j in range(self.crossword.width):
                if self.crossword.structure[i][j]:
                    print(letters[i][j] or " ", end="")
                else:
                    print("█", end="")
            print()

    def save(self, assignment, filename):
        """
        Save crossword assignment to an image file.
        """
        from PIL import Image, ImageDraw, ImageFont
        cell_size = 100
        cell_border = 2
        interior_size = cell_size - 2 * cell_border
        letters = self.letter_grid(assignment)

        # Create a blank canvas
        img = Image.new(
            "RGBA",
            (self.crossword.width * cell_size,
             self.crossword.height * cell_size),
            "black"
        )
        font = ImageFont.truetype("assets/fonts/OpenSans-Regular.ttf", 80)
        draw = ImageDraw.Draw(img)

        for i in range(self.crossword.height):
            for j in range(self.crossword.width):

                rect = [
                    (j * cell_size + cell_border,
                     i * cell_size + cell_border),
                    ((j + 1) * cell_size - cell_border,
                     (i + 1) * cell_size - cell_border)
                ]
                if self.crossword.structure[i][j]:
                    draw.rectangle(rect, fill="white")
                    if letters[i][j]:
                        _, _, w, h = draw.textbbox((0, 0), letters[i][j], font=font)
                        draw.text(
                            (rect[0][0] + ((interior_size - w) / 2),
                             rect[0][1] + ((interior_size - h) / 2) - 10),
                            letters[i][j], fill="black", font=font
                        )

        img.save(filename)

    def solve(self):
        """
        Enforce node and arc consistency, and then solve the CSP.
        """
        self.enforce_node_consistency()
        self.ac3()
        return self.backtrack(dict())

    def enforce_node_consistency(self):
        """
        Garante consistência dos nós: remove palavras que não correspondem ao tamanho da variável.
        """
        for var in self.domains:
            # Usar set para evitar erro de modificar durante a iteração
            for word in set(self.domains[var]):
                if len(word) != var.length:
                    self.domains[var].remove(word)

    def revise(self, x, y):
        """
        Torna 'x' arc-consistente com 'y'. Remove valores inviáveis de x que não têm correspondência em y.
        Retorna True se houve modificação no domínio.
        """
        revised = False  # Variável renomeada para evitar conflito de nomes
        overlap = self.crossword.overlaps[(x, y)]

        # Não há sobreposição, nada a fazer
        if overlap is None:
            return False

        i, j = overlap  # Posições de sobreposição

        # Verificar cada palavra de x contra todas de y
        for word_x in set(self.domains[x]):
            has_compatible = False
            for word_y in self.domains[y]:
                # Verifica compatibilidade na posição de sobreposição
                if word_x[i] == word_y[j]:
                    has_compatible = True
                    break
            
            # Remove palavra sem correspondência e marca revisão
            if not has_compatible:
                self.domains[x].remove(word_x)
                revised = True

        return revised

    def ac3(self, arcs=None):
        """
        Algoritmo AC3 para consistência de arco. Processa arcos até que todos sejam consistentes.
        Retorna False se algum domínio ficar vazio, True caso contrário.
        """
        # Inicializa lista de arcos se não for fornecida
        if arcs is None:
            arcs = []
            for var in self.crossword.variables:
                for neighbor in self.crossword.neighbors(var):
                    arcs.append((var, neighbor))   

        processing_queue = list(arcs)  # Fila de processamento renomeada

        while processing_queue:
            x, y = processing_queue.pop(0)
            if self.revise(x, y):
                # Domínio vazio indica problema insolúvel
                if not self.domains[x]:
                    return False
                # Adiciona novos arcos para verificação
                for z in self.crossword.neighbors(x):
                    if z != y:
                        processing_queue.append((z, x))
        return True

    def assignment_complete(self, assignment):
        """
        Verifica se todas as variáveis do crossword têm atribuição.
        """
        return all(var in assignment for var in self.crossword.variables)

    def consistent(self, assignment):
        """
        Valida a consistência da atribuição atual:
        1. Palavras com tamanho correto
        2. Sem palavras duplicadas
        3. Respeita todas sobreposições com vizinhos
        """
        used_words = set()
        for var, word in assignment.items():
            # Verifica tamanho da palavra
            if len(word) != var.length:
                return False
            
            # Verifica duplicatas
            if word in used_words:
                return False
            used_words.add(word)
            
            # Verifica consistência com vizinhos
            for neighbor in self.crossword.neighbors(var):
                if neighbor in assignment:
                    overlap = self.crossword.overlaps[(var, neighbor)]
                    if overlap:
                        i, j = overlap
                        if word[i] != assignment[neighbor][j]:
                            return False
        return True

    def order_domain_values(self, var, assignment):
        """
        Ordena os valores do domínio pela heurística LCV (Least Constraining Value).
        Retorna valores que eliminam menos opções dos vizinhos primeiro.
        """
        value_conflicts = []  # Lista renomeada para maior clareza
        
        for value in self.domains[var]:
            conflict_count = 0
            
            # Conta conflitos potenciais com vizinhos não atribuídos
            for neighbor in self.crossword.neighbors(var):
                if neighbor not in assignment:
                    overlap = self.crossword.overlaps[(var, neighbor)]
                    if overlap:
                        i, j = overlap
                        # Verifica incompatibilidades com cada palavra do vizinho
                        for neighbor_word in self.domains[neighbor]:
                            if value[i] != neighbor_word[j]:
                                conflict_count += 1
                                
            value_conflicts.append((value, conflict_count))
        
        # Ordena pelos que causam menos conflitos primeiro
        value_conflicts.sort(key=lambda x: x[1])
        
        return [value for value, _ in value_conflicts]

    def select_unassigned_variable(self, assignment):
        """
        Seleciona a próxima variável para atribuir usando heurísticas MRV e grau.
        Prioriza variáveis com menor domínio restante e maior grau de conectividade.
        """
        best_candidate = None
        min_remaining = float('inf')
        max_degree = -1

        for var in self.crossword.variables:
            if var not in assignment:
                remaining = len(self.domains[var])
                degree = len(self.crossword.neighbors(var))
                
                # Atualiza melhor candidato baseado nas heurísticas
                if (remaining < min_remaining or 
                    (remaining == min_remaining and degree > max_degree)):
                    best_candidate = var
                    min_remaining = remaining
                    max_degree = degree

        return best_candidate

    def backtrack(self, assignment):
        """
        Algoritmo de backtracking recursivo para completar a atribuição.
        Tenta valores ordenados e verifica consistência a cada passo.
        """
        # Atribuição completa: retorna solução
        if self.assignment_complete(assignment):
            return assignment
        
        # Seleciona variável para atribuir
        var = self.select_unassigned_variable(assignment)
        
        # Tenta cada valor ordenado por heurística
        for value in self.order_domain_values(var, assignment):
            new_assignment = assignment.copy()
            new_assignment[var] = value
            
            if self.consistent(new_assignment):
                # Chamada recursiva
                result = self.backtrack(new_assignment)
                if result is not None:
                    return result
                    
        # Nenhuma solução encontrada neste ramo
        return None


def main():
    # Verificação de argumentos
    if len(sys.argv) not in [3, 4]:
        sys.exit("Uso: python generate.py estrutura palavras [saida]")

    # Processa argumentos
    structure_file = sys.argv[1]
    words_file = sys.argv[2]
    output_file = sys.argv[3] if len(sys.argv) == 4 else None

    # Gera crossword
    crossword = Crossword(structure_file, words_file)
    creator = CrosswordCreator(crossword)
    solution = creator.solve()

    # Exibe resultado
    if solution is None:
        print("Nenhuma solução encontrada.")
    else:
        creator.print(solution)
        if output_file:
            creator.save(solution, output_file)


if __name__ == "__main__":
    main()