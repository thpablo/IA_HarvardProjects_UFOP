import sys
from crossword import *

class CrosswordCreator():
    """Implementa a solução do problema de palavras cruzadas usando CSP (Satisfação de Restrições).

    Essa classe gerencia:
    - Os domínios de cada variável (conjunto de palavras possíveis para cada espaço)
    - A aplicação de algoritmos de consistência e backtracking para encontrar uma solução.
    """

    def __init__(self, crossword):
        """
        Inicializa o gerador de palavras cruzadas com um objeto Crossword.
        
        Cria um dicionário 'domains' que mapeia cada variável para um conjunto de palavras
        disponíveis inicialmente (cópia do vocabulário lido).
        """
        self.crossword = crossword
        self.domains = {
            var: self.crossword.words.copy()
            for var in self.crossword.variables
        }

    def letter_grid(self, assignment):
        """
        Retorna uma matriz 2D (lista de listas) representando a atribuição atual do tabuleiro.
        
        Cada célula da matriz contém a letra correspondente se uma palavra foi atribuída à variável,
        caso contrário, permanece como None.
        """
        letters = [
            [None for _ in range(self.crossword.width)]
            for _ in range(self.crossword.height)
        ]
        # Preenche a matriz com as letras das palavras atribuídas a cada variável
        for variable, word in assignment.items():
            direction = variable.direction
            for k in range(len(word)):
                i = variable.i + (k if direction == Variable.DOWN else 0)
                j = variable.j + (k if direction == Variable.ACROSS else 0)
                letters[i][j] = word[k]
        return letters

    def print(self, assignment):
        """
        Imprime no terminal a atribuição atual do tabuleiro.
        
        Utiliza a função letter_grid para montar a matriz e, em seguida, imprime cada célula.
        Células válidas exibem a letra atribuída (ou espaço se não houver letra) e células bloqueadas
        são representadas por um bloco.
        """
        letters = self.letter_grid(assignment)
        for i in range(self.crossword.height):
            for j in range(self.crossword.width):
                if self.crossword.structure[i][j]:
                    # Se a célula for parte do tabuleiro, imprime a letra ou um espaço em branco
                    print(letters[i][j] or " ", end="")
                else:
                    # Células bloqueadas são mostradas com o caractere '█'
                    print("█", end="")
            print()  # Quebra de linha após cada linha do tabuleiro

    def save(self, assignment, filename):
        """
        Salva a atribuição do tabuleiro em um arquivo de imagem.
        
        Utiliza a biblioteca PIL para criar uma imagem onde cada célula do tabuleiro
        é desenhada com as letras (quando atribuídas) e a estrutura definida.
        
        Parâmetros:
        - assignment: atribuição atual de palavras para as variáveis
        - filename: nome do arquivo onde a imagem será salva
        """
        from PIL import Image, ImageDraw, ImageFont
        cell_size = 100      # Tamanho de cada célula na imagem
        cell_border = 2      # Largura da borda da célula
        interior_size = cell_size - 2 * cell_border  # Tamanho interno da célula (sem a borda)
        letters = self.letter_grid(assignment)

        # Cria uma nova imagem em modo RGBA com fundo preto
        img = Image.new(
            "RGBA",
            (self.crossword.width * cell_size,
             self.crossword.height * cell_size),
            "black"
        )
        # Carrega a fonte para desenhar as letras
        font = ImageFont.truetype("assets/fonts/OpenSans-Regular.ttf", 80)
        draw = ImageDraw.Draw(img)

        # Percorre cada célula do tabuleiro para desenhar retângulos e letras
        for i in range(self.crossword.height):
            for j in range(self.crossword.width):
                # Define as coordenadas do retângulo da célula
                rect = [
                    (j * cell_size + cell_border,
                     i * cell_size + cell_border),
                    ((j + 1) * cell_size - cell_border,
                     (i + 1) * cell_size - cell_border)
                ]
                if self.crossword.structure[i][j]:
                    # Se a célula for válida, desenha um retângulo branco
                    draw.rectangle(rect, fill="white")
                    if letters[i][j]:
                        # Calcula as dimensões da letra para centralizá-la na célula
                        _, _, w, h = draw.textbbox((0, 0), letters[i][j], font=font)
                        draw.text(
                            (rect[0][0] + ((interior_size - w) / 2),
                             rect[0][1] + ((interior_size - h) / 2) - 10),
                            letters[i][j], fill="black", font=font
                        )

        # Salva a imagem no arquivo especificado
        img.save(filename)

    def solve(self):
        """
        Resolve o problema do CSP (Satisfação de Restrições) aplicando:\n
        1. Consistência de nó (node consistency): garante que os domínios das variáveis são compatíveis com restrições locais\n
        2. Algoritmo AC3 (Arc Consistency): elimina valores inconsistentes dos domínios com base em restrições entre variáveis\n
        3. Backtracking: busca recursivamente por uma solução consistente para todas as variáveis
        
        Retorna a atribuição completa se houver solução ou None caso contrário.
        """
        self.enforce_node_consistency()
        self.ac3()
        return self.backtrack(dict())

    def enforce_node_consistency(self):
        """
        Garante a consistência dos nós, removendo do domínio de cada variável as palavras cujo tamanho
        não corresponde ao tamanho esperado para aquele espaço no tabuleiro.
        """
        for var in self.domains:
            # Usa uma cópia do domínio (set) para evitar problemas ao modificar o conjunto durante iteração
            for word in set(self.domains[var]):
                if len(word) != var.length:
                    self.domains[var].remove(word)

    def revise(self, x, y):
        """
        Torna a variável 'x' arc-consistente com a variável 'y'.
        
        Para cada palavra possível em x, verifica se existe pelo menos uma palavra em y que seja compatível
        na célula onde x e y se sobrepõem. Se não houver correspondência, remove a palavra do domínio de x.
        
        Retorna True se o domínio de x foi revisado (pelo menos um valor removido), False caso contrário.
        """
        revised = False  # Flag para indicar se houve modificação no domínio de x
        
        # Obtém a sobreposição (índices das letras) entre x e y
        overlap = self.crossword.overlaps[(x, y)]

        # Se não há sobreposição, não há necessidade de revisão
        if overlap is None:
            return False

        i, j = overlap  # Índices da letra em x e em y na posição de sobreposição

        # Para cada palavra em x, verifica se há alguma palavra em y compatível na posição de sobreposição
        for word_x in set(self.domains[x]):
            has_compatible = False
            for word_y in self.domains[y]:
                if word_x[i] == word_y[j]:
                    has_compatible = True
                    break
            
            # Se não houver nenhuma palavra em y que compatibilize, remove word_x do domínio de x
            if not has_compatible:
                self.domains[x].remove(word_x)
                revised = True

        return revised

    def ac3(self, arcs=None):
        """
        Aplica o algoritmo AC3 para impor consistência de arco em todo o CSP.
        
        Se não for fornecida uma lista de arcos, inicializa com todos os pares de variáveis que se sobrepõem.
        Processa cada arco e, se alguma revisão ocorrer, re-adiciona os arcos relacionados para nova verificação.
        
        Retorna False se algum domínio se tornar vazio (indicando que o problema não tem solução), True caso contrário.
        """
        if arcs is None:
            # Inicializa a lista de arcos com todos os pares (var, vizinho) possíveis
            arcs = []
            for var in self.crossword.variables:
                for neighbor in self.crossword.neighbors(var):
                    arcs.append((var, neighbor))

        processing_queue = list(arcs)  # Fila de processamento dos arcos

        while processing_queue:
            x, y = processing_queue.pop(0)  # Remove o primeiro arco da fila

            if self.revise(x, y):
                # Se o domínio de x ficar vazio após a revisão, o problema não possui solução
                if not self.domains[x]:
                    return False
                
                # Adiciona os arcos relacionados à variável x, exceto aquele que já está sendo considerado
                for z in self.crossword.neighbors(x):
                    if z != y:
                        processing_queue.append((z, x))
        return True

    def assignment_complete(self, assignment):
        """
        Verifica se a atribuição atual é completa, isto é, se todas as variáveis do tabuleiro já possuem uma palavra atribuída.
        """
        return all(var in assignment for var in self.crossword.variables)

    def consistent(self, assignment):
        """
        Verifica se a atribuição atual atende a todas as restrições:
        
        1. Cada palavra atribuída deve ter o tamanho correto para a variável.
        2. Não pode haver palavras duplicadas em diferentes variáveis.
        3. Para variáveis que se sobrepõem, as letras na posição de sobreposição devem coincidir.
        """
        used_words = set()

        for var, word in assignment.items():
            # Verifica se o tamanho da palavra é compatível com o espaço da variável
            if len(word) != var.length:
                return False
            
            # Verifica se a palavra já foi utilizada em outra variável
            if word in used_words:
                return False
            used_words.add(word)
            
            # Para cada vizinho que também está atribuído, verifica a compatibilidade na sobreposição
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
        Ordena os valores do domínio para a variável 'var' usando a heurística LCV (Least Constraining Value).
        
        Para cada palavra candidata, conta quantas restrições (conflitos) ela impõe aos vizinhos não atribuídos.
        Retorna uma lista de palavras ordenadas, da que impõe menos conflitos para a que impõe mais.
        """
        value_conflicts = []  # Lista que armazenará cada palavra e sua contagem de conflitos
        
        for value in self.domains[var]:
            conflict_count = 0
            
            # Para cada vizinho ainda não atribuído, conta quantos valores seriam eliminados se 'value' fosse escolhida
            for neighbor in self.crossword.neighbors(var):
                if neighbor not in assignment:
                    overlap = self.crossword.overlaps[(var, neighbor)]
                    if overlap:
                        i, j = overlap
                        for neighbor_word in self.domains[neighbor]:
                            if value[i] != neighbor_word[j]:
                                conflict_count += 1
            value_conflicts.append((value, conflict_count))
        
        # Ordena a lista com base na quantidade de conflitos (valores com menos conflitos primeiro)
        value_conflicts.sort(key=lambda x: x[1])
        
        # Retorna apenas as palavras, na ordem determinada pela heurística
        return [value for value, _ in value_conflicts]

    def select_unassigned_variable(self, assignment):
        """
        Seleciona a próxima variável (espaço para palavra) que ainda não foi atribuída, utilizando duas heurísticas:
        
        - MRV (Minimum Remaining Values): escolhe a variável com o menor número de valores possíveis no domínio.
        - Grau: em caso de empate, escolhe a variável com o maior número de restrições (mais vizinhos).
        """
        best_candidate = None
        min_remaining = float('inf')
        max_degree = -1

        for var in self.crossword.variables:
            if var not in assignment:
                remaining = len(self.domains[var])  # Número de palavras possíveis para esta variável
                degree = len(self.crossword.neighbors(var))  # Número de variáveis vizinhas (grau de restrição)
                
                # Seleciona a variável que minimiza o domínio e maximiza o grau de restrição
                if (remaining < min_remaining or 
                    (remaining == min_remaining and degree > max_degree)):
                    best_candidate = var
                    min_remaining = remaining
                    max_degree = degree

        return best_candidate

    def backtrack(self, assignment):
        """
        Algoritmo recursivo de backtracking para encontrar uma atribuição completa e consistente para o CSP.
        
        Passos:
        1. Verifica se a atribuição está completa; se sim, retorna a solução.
        2. Seleciona uma variável não atribuída usando MRV e grau.
        3. Para cada valor (palavra) do domínio dessa variável (ordenado pela heurística LCV):\n
           - Cria uma nova atribuição com esse valor.\n
           - Se a nova atribuição é consistente, chama recursivamente o backtracking.\n
           - Se uma solução é encontrada, retorna a atribuição.\n
        4. Se nenhum valor levar a uma solução, retorna None, indicando falha neste ramo.
        """
        if self.assignment_complete(assignment):
            return assignment
        
        var = self.select_unassigned_variable(assignment)
        
        for value in self.order_domain_values(var, assignment):
            new_assignment = assignment.copy()
            new_assignment[var] = value
            
            if self.consistent(new_assignment):
                result = self.backtrack(new_assignment)
                if result is not None:
                    return result
                    
        return None


def main():
    # Verifica se a quantidade de argumentos é adequada.
    if len(sys.argv) not in [3, 4]:
        sys.exit("Uso: python generate.py estrutura palavras [saida]")

    # Processa os argumentos: arquivo de estrutura, arquivo de palavras e opcionalmente o arquivo de saída para imagem.
    structure_file = sys.argv[1]
    words_file = sys.argv[2]
    output_file = sys.argv[3] if len(sys.argv) == 4 else None

    # Cria o objeto Crossword e o gerador CrosswordCreator
    crossword = Crossword(structure_file, words_file)
    creator = CrosswordCreator(crossword)
    solution = creator.solve()

    # Exibe o resultado: imprime no terminal e, se fornecido, salva a imagem
    if solution is None:
        print("Nenhuma solução encontrada.")
    else:
        creator.print(solution)
        if output_file:
            creator.save(solution, output_file)


if __name__ == "__main__":
    main()
