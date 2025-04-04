import os
import random
import re
import sys

DAMPING = 0.85
SAMPLES = 10000


def main():
    if len(sys.argv) != 2:
        sys.exit("Usage: python pagerank.py corpus")
    corpus = crawl(sys.argv[1])
    ranks = sample_pagerank(corpus, DAMPING, SAMPLES)
    print(f"PageRank Results from Sampling (n = {SAMPLES})")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")
    ranks = iterate_pagerank(corpus, DAMPING)
    print(f"PageRank Results from Iteration")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")


def crawl(directory):
    """
    Parse a directory of HTML pages and check for links to other pages.
    Return a dictionary where each key is a page, and values are
    a list of all other pages in the corpus that are linked to by the page.
    """
    pages = dict()

    # Extract all links from HTML files
    for filename in os.listdir(directory):
        if not filename.endswith(".html"):
            continue
        with open(os.path.join(directory, filename)) as f:
            contents = f.read()
            links = re.findall(r"<a\s+(?:[^>]*?)href=\"([^\"]*)\"", contents)
            pages[filename] = set(links) - {filename}

    # Only include links to other pages in the corpus
    for filename in pages:
        pages[filename] = set(
            link for link in pages[filename]
            if link in pages
        )

    return pages

def transition_model(corpus, current_page, damping_factor):
    """
    Retorna uma distribuição de probabilidade sobre qual página visitar a seguir,
    dada uma página atual.

    Com probabilidade `damping_factor`, escolhe um link aleatório da página atual.
    Com probabilidade `1 - damping_factor`, escolhe uma página aleatória de todo o corpus.
    """
    prob_distribution = {}

    # Inicializa todas as probabilidades como 0
    for page in corpus:
        prob_distribution[page] = 0

    total_pages = len(corpus)  # Número total de páginas no corpus

    # Verifica se a página atual tem links para outras páginas
    if corpus[current_page]:
        outgoing_links = corpus[current_page]  # Lista de links da página atual
    else:
        outgoing_links = corpus.keys()  # Se não houver links, considera todas as páginas do corpus

    # Calcula a probabilidade para cada página
    for target_page in prob_distribution:
        # Probabilidade base (1 - damping_factor) distribuída igualmente entre todas as páginas
        prob_distribution[target_page] = (1 - damping_factor) / total_pages
        # Se a página estiver nos links da página atual, adiciona a probabilidade do damping_factor
        if target_page in outgoing_links:
            prob_distribution[target_page] += damping_factor / len(outgoing_links)

    return prob_distribution


def sample_pagerank(corpus, damping_factor, num_samples):
    """
    Retorna os valores de PageRank para cada página amostrando `n` páginas
    de acordo com o modelo de transição, começando em uma página aleatória.

    Retorna um dicionário onde as chaves são os nomes das páginas e os valores são
    seus valores estimados de PageRank (um valor entre 0 e 1). Todos os valores
    de PageRank devem somar 1.
    """
    rank_counts = {}
    # Inicializa o contador de visitas de todas as páginas como 0
    for page in corpus:
        rank_counts[page] = 0

    # Escolhe uma página inicial aleatória
    current_page = random.choice(list(corpus.keys()))

    # Realiza a amostragem `num_samples` vezes
    for _ in range(num_samples):
        rank_counts[current_page] += 1  # Incrementa o contador da página atual
        transition_probs = transition_model(corpus, current_page, damping_factor)  # Obtém o modelo de transição

        # Escolhe a próxima página com base nas probabilidades do modelo de transição
        pages = list(transition_probs.keys())
        weights = list(transition_probs.values())
        current_page = random.choices(pages, weights)[0]

    # Normaliza os valores de PageRank para que a soma seja 1
    normalized_ranks = {}
    for page in rank_counts:
        normalized_ranks[page] = rank_counts[page] / num_samples

    return normalized_ranks


def iterate_pagerank(corpus, damping_factor):
    """
    Retorna os valores de PageRank para cada página atualizando iterativamente
    os valores de PageRank até a convergência.

    Retorna um dicionário onde as chaves são os nomes das páginas e os valores são
    seus valores estimados de PageRank (um valor entre 0 e 1). Todos os valores
    de PageRank devem somar 1.
    """
    ranks = {}
    total_pages = len(corpus)
    # Inicializa o PageRank de todas as páginas com o mesmo valor (1 / número de páginas)
    for page in corpus:
        ranks[page] = 1 / total_pages

    convergence_threshold = 0.001  # Limiar de convergência para determinar quando parar as iterações
    updated_ranks = ranks.copy()  # Cria uma cópia para armazenar os novos valores

    while True:
        for target_page in corpus:
            # Calcula a contribuição base (1 - damping_factor) distribuída igualmente
            rank_sum = (1 - damping_factor) / total_pages
            # Calcula a contribuição dos links de outras páginas
            for source_page in corpus:
                if target_page in corpus[source_page]:  # Se a página atual é linkada por outra página `source_page`
                    rank_sum += damping_factor * (ranks[source_page] / len(corpus[source_page]))
                if not corpus[source_page]:  # Se a página `source_page` não tem links, considera todas as páginas
                    rank_sum += damping_factor * (ranks[source_page] / total_pages)
            updated_ranks[target_page] = rank_sum  # Atualiza o novo valor de PageRank

        # Verifica se a convergência foi atingida
        has_converged = True
        for page in ranks:
            if abs(updated_ranks[page] - ranks[page]) >= convergence_threshold:
                has_converged = False
                break
        if has_converged:
            break  # Se convergiu, sai do loop
        else:
            ranks = updated_ranks.copy()  # Atualiza os valores de PageRank para a próxima iteração

    # Normaliza os resultados para garantir que a soma seja exatamente 1
    rank_total = sum(updated_ranks.values())
    for page in updated_ranks:
        updated_ranks[page] /= rank_total

    return updated_ranks

if __name__ == "__main__":
    main()
