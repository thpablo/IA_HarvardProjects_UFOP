import csv
import sys

from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier

TEST_SIZE = 0.4


def main():
    # Check command-line arguments; expects exactly one argument (the CSV file)
    if len(sys.argv) != 2:
        sys.exit("Usage: python shopping.py data")

    # Load data from CSV file and split it into training and testing sets
    evidence, labels = load_data(sys.argv[1])
    X_train, X_test, y_train, y_test = train_test_split(
        evidence, labels, test_size=TEST_SIZE
    )

    # Train the k-nearest neighbor model (k=1) and make predictions on test data
    model = train_model(X_train, y_train)
    predictions = model.predict(X_test)
    
    # Evaluate the model performance calculating sensitivity and specificity
    sensitivity, specificity = evaluate(y_test, predictions)

    # Print out the results: counts and rates
    print(f"Correct: {(y_test == predictions).sum()}")
    print(f"Incorrect: {(y_test != predictions).sum()}")
    print(f"True Positive Rate: {100 * sensitivity:.2f}%")
    print(f"True Negative Rate: {100 * specificity:.2f}%")


def load_data(filename):
    """
    Carrega os dados de compras a partir de um arquivo CSV `filename` e converte 
    em uma lista de listas de features e uma lista de rótulos (target_labels).
    Retorna uma tupla (features, target_labels).

    Cada lista de features contém os seguintes valores, na ordem:
        - Administrative, um inteiro
        - Administrative_Duration, um número de ponto flutuante
        - Informational, um inteiro
        - Informational_Duration, um número de ponto flutuante
        - ProductRelated, um inteiro
        - ProductRelated_Duration, um número de ponto flutuante
        - BounceRates, um número de ponto flutuante
        - ExitRates, um número de ponto flutuante
        - PageValues, um número de ponto flutuante
        - SpecialDay, um número de ponto flutuante
        - Month, um índice de 0 (Janeiro) a 11 (Dezembro)
        - OperatingSystems, um inteiro
        - Browser, um inteiro
        - Region, um inteiro
        - TrafficType, um inteiro
        - VisitorType, um inteiro 0 (não retorna) ou 1 (retorna)
        - Weekend, um inteiro 0 (se falso) ou 1 (se verdadeiro)

    A lista target_labels contém o rótulo correspondente, onde cada rótulo é 1 se Revenue for TRUE, e 0 caso contrário.
    """
    # Inicializa as listas para armazenar as features e os rótulos
    features = []
    target_labels = []

    # Dicionário que mapeia as abreviações dos meses para índices (0 para Janeiro, 11 para Dezembro)
    month_to_index = {
        "Jan": 0,
        "Feb": 1,
        "Mar": 2,
        "Apr": 3,
        "May": 4,
        "June": 5,
        "Jul": 6,
        "Aug": 7,
        "Sep": 8,
        "Oct": 9,
        "Nov": 10,
        "Dec": 11,
    }

    # Abre o arquivo CSV para leitura
    with open(filename, mode="r") as csv_file:
        csv_reader = csv.reader(csv_file)
        # Pula a linha de cabeçalho
        next(csv_reader)
        # Itera por cada registro no arquivo CSV
        for record in csv_reader:
            # Adiciona à lista 'features' uma nova lista com os valores convertidos para seus tipos apropriados
            features.append(
                [
                    int(record[0]),                      # Administrative
                    float(record[1]),                    # Administrative_Duration
                    int(record[2]),                      # Informational
                    float(record[3]),                    # Informational_Duration
                    int(record[4]),                      # ProductRelated
                    float(record[5]),                    # ProductRelated_Duration
                    float(record[6]),                    # BounceRates
                    float(record[7]),                    # ExitRates
                    float(record[8]),                    # PageValues
                    float(record[9]),                    # SpecialDay
                    month_to_index[record[10]],          # Converte o mês para um índice
                    int(record[11]),                     # OperatingSystems
                    int(record[12]),                     # Browser
                    int(record[13]),                     # Region
                    int(record[14]),                     # TrafficType
                    1 if record[15] == "Returning_Visitor" else 0,  # VisitorType: 1 se "Returning_Visitor", senão 0
                    1 if record[16] == "TRUE" else 0       # Weekend: 1 se "TRUE", senão 0
                ]
            )
            # Adiciona o rótulo (1 se Revenue for "TRUE", senão 0) para o registro atual
            target_labels.append(1 if record[17] == "TRUE" else 0)
        
    # Retorna as listas de features e rótulos como uma tupla
    return features, target_labels


def train_model(features, target_labels):
    """
    Recebe uma lista de listas de features e uma lista de rótulos e retorna um 
    modelo k-vizinhos mais próximos (k=1) já treinado com esses dados.
    """
    # Cria o classificador KNN com 1 vizinho
    knn_model = KNeighborsClassifier(n_neighbors=1)
    # Treina o modelo utilizando as features e os rótulos fornecidos
    knn_model.fit(features, target_labels)
    # Retorna o modelo treinado
    return knn_model


def evaluate(true_labels, predicted_labels):
    """
    Recebe uma lista de rótulos reais e uma lista de rótulos previstos e retorna uma tupla 
    (sensibilidade, especificidade).

    Cada rótulo é 1 (positivo) ou 0 (negativo).

    - Sensibilidade: taxa de verdadeiro positivo, ou seja, a proporção de rótulos positivos reais 
      que foram corretamente identificados.
    - Especificidade: taxa de verdadeiro negativo, ou seja, a proporção de rótulos negativos reais 
      que foram corretamente identificados.
    """
    # Calcula o número de verdadeiros positivos (quando ambos os rótulos real e previsto são 1)
    true_positive_count = sum(
        [1 for i in range(len(true_labels)) if true_labels[i] == predicted_labels[i] == 1]
    )
    # Total de casos positivos reais
    total_positives = sum(true_labels)
    # Calcula a sensibilidade (taxa de verdadeiro positivo)
    sensitivity = true_positive_count / total_positives

    # Calcula o número de verdadeiros negativos (quando ambos os rótulos real e previsto são 0)
    true_negative_count = sum(
        [1 for i in range(len(true_labels)) if true_labels[i] == predicted_labels[i] == 0]
    )
    # Total de casos negativos reais
    total_negatives = len(true_labels) - sum(true_labels)
    # Calcula a especificidade (taxa de verdadeiro negativo)
    specificity = true_negative_count / total_negatives

    # Retorna a sensibilidade e a especificidade como uma tupla
    return sensitivity, specificity

if __name__ == "__main__":
    main()