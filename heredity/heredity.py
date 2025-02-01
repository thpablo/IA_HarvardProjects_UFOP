import csv
import itertools
import sys

PROBS = {

    # Unconditional probabilities for having gene
    "gene": {
        2: 0.01,
        1: 0.03,
        0: 0.96
    },

    "trait": {

        # Probability of trait given two copies of gene
        2: {
            True: 0.65,
            False: 0.35
        },

        # Probability of trait given one copy of gene
        1: {
            True: 0.56,
            False: 0.44
        },

        # Probability of trait given no gene
        0: {
            True: 0.01,
            False: 0.99
        }
    },

    # Mutation probability
    "mutation": 0.01
}


def main():

    # Check for proper usage
    if len(sys.argv) != 2:
        sys.exit("Usage: python heredity.py data.csv")
    people = load_data(sys.argv[1])

    # Keep track of gene and trait probabilities for each person
    probabilities = {
        person: {
            "gene": {
                2: 0,
                1: 0,
                0: 0
            },
            "trait": {
                True: 0,
                False: 0
            }
        }
        for person in people
    }

    # Loop over all sets of people who might have the trait
    names = set(people)
    for have_trait in powerset(names):

        # Check if current set of people violates known information
        fails_evidence = any(
            (people[person]["trait"] is not None and
             people[person]["trait"] != (person in have_trait))
            for person in names
        )
        if fails_evidence:
            continue

        # Loop over all sets of people who might have the gene
        for one_gene in powerset(names):
            for two_genes in powerset(names - one_gene):

                # Update probabilities with new joint probability
                p = joint_probability(people, one_gene, two_genes, have_trait)
                update(probabilities, one_gene, two_genes, have_trait, p)

    # Ensure probabilities sum to 1
    normalize(probabilities)

    # Print results
    for person in people:
        print(f"{person}:")
        for field in probabilities[person]:
            print(f"  {field.capitalize()}:")
            for value in probabilities[person][field]:
                p = probabilities[person][field][value]
                print(f"    {value}: {p:.4f}")


def load_data(filename):
    """
    Load gene and trait data from a file into a dictionary.
    File assumed to be a CSV containing fields name, mother, father, trait.
    mother, father must both be blank, or both be valid names in the CSV.
    trait should be 0 or 1 if trait is known, blank otherwise.
    """
    data = dict()
    with open(filename) as f:
        reader = csv.DictReader(f)
        for row in reader:
            name = row["name"]
            data[name] = {
                "name": name,
                "mother": row["mother"] or None,
                "father": row["father"] or None,
                "trait": (True if row["trait"] == "1" else
                          False if row["trait"] == "0" else None)
            }
    return data


def powerset(s):
    """
    Return a list of all possible subsets of set s.
    """
    s = list(s)
    return [
        set(s) for s in itertools.chain.from_iterable(
            itertools.combinations(s, r) for r in range(len(s) + 1)
        )
    ]

def parent_prob(num_genes):
    """
    Calcula a probabilidade de um pai passar um gene para o filho, considerando a mutação.
    :param num_genes: Número de cópias do gene que o pai possui (0, 1 ou 2).
    :return: Probabilidade de o pai passar o gene ao filho.
    """
    pass_gene = num_genes / 2  # Probabilidade de passar o gene sem mutação (0, 0.5 ou 1).
    return pass_gene * (1 - PROBS["mutation"]) + (1 - pass_gene) * PROBS["mutation"]
    # Retorna a probabilidade de passar o gene, considerando a mutação:
    # - pass_gene * (1 - mutation): Probabilidade de passar o gene sem mutação.
    # - (1 - pass_gene) * mutation: Probabilidade de passar o gene por mutação.


def joint_probability(people, one_gene, two_genes, have_trait):
    """
    Calcula a probabilidade conjunta de uma configuração específica de genes e traços para todas as pessoas.
    :param people: Dicionário contendo informações sobre as pessoas.
    :param one_gene: Conjunto de pessoas com uma cópia do gene.
    :param two_genes: Conjunto de pessoas com duas cópias do gene.
    :param have_trait: Conjunto de pessoas que possuem o traço.
    :return: Probabilidade conjunta da configuração.
    """
    prob = 1.0  # Inicializa a probabilidade conjunta como 1 (neutro para multiplicação).
    for person in people:  # Itera sobre cada pessoa no dicionário.
        # Determina quantas cópias do gene a pessoa possui (0, 1 ou 2).
        quant_genes = 1 if person in one_gene else 2 if person in two_genes else 0
        # Verifica se a pessoa possui o traço.
        trait_status = person in have_trait

        if people[person]['mother'] is None:  # Se a pessoa não tem pais (é uma raiz da árvore genealógica).
            gene_prob = PROBS['gene'][quant_genes]  # Usa a probabilidade incondicional do gene.
            prob *= gene_prob * PROBS['trait'][quant_genes][trait_status]  # Atualiza a probabilidade conjunta.
        else:  # Se a pessoa tem pais.
            mother = people[person]['mother']  # Nome da mãe.
            father = people[person]['father']  # Nome do pai.

            # Determina quantas cópias do gene a mãe possui (0, 1 ou 2).
            mother_genes = 1 if mother in one_gene else 2 if mother in two_genes else 0
            # Determina quantas cópias do gene o pai possui (0, 1 ou 2).
            father_genes = 1 if father in one_gene else 2 if father in two_genes else 0

            # Calcula a probabilidade de a mãe passar o gene ao filho, considerando mutação.
            prob_mother = parent_prob(mother_genes)
            # Calcula a probabilidade de o pai passar o gene ao filho, considerando mutação.
            prob_father = parent_prob(father_genes)

            # Calcula a probabilidade da pessoa ter a quantidade de genes especificada.
            if quant_genes == 0:  # Se a pessoa não tem cópias do gene.
                p = (1 - prob_father) * (1 - prob_mother)  # Ambos os pais não passam o gene.
            elif quant_genes == 1:  # Se a pessoa tem uma cópia do gene.
                p = (1 - prob_father) * prob_mother + prob_father * (1 - prob_mother)  # Um dos pais passa o gene.
            elif quant_genes == 2:  # Se a pessoa tem duas cópias do gene.
                p = prob_father * prob_mother  # Ambos os pais passam o gene.
            else:  # Caso inválido (não deve ocorrer).
                p = 0

            # Atualiza a probabilidade conjunta com a probabilidade do gene e do traço.
            prob *= p * PROBS['trait'][quant_genes][trait_status]

    return prob  # Retorna a probabilidade conjunta calculada.

def update(probabilities, one_gene, two_genes, have_trait, p):
    """
    Add to `probabilities` a new joint probability `p`.
    Each person should have their "gene" and "trait" distributions updated.
    Which value for each distribution is updated depends on whether
    the person is in `have_gene` and `have_trait`, respectively.
    """
    for person in probabilities:
        ## Check how many genes the person has
        quant_genes = 1 if person in one_gene else 2 if person in two_genes else 0

        ## Check if person has trait
        trait_status = False
        if person in have_trait:
            trait_status = True

        probabilities[person]['gene'][quant_genes] += p
        probabilities[person]['trait'][trait_status] += p

    return probabilities

def normalize(probabilities):
    """
    Update `probabilities` such that each probability distribution
    is normalized (i.e., sums to 1, with relative proportions the same).
    """

    for person in probabilities:
        total_genes = sum(probabilities[person]['gene'].values())
        total_trait = sum(probabilities[person]['trait'].values())

        for gene in probabilities[person]['gene']:
            probabilities[person]['gene'][gene] = probabilities[person]['gene'][gene] / total_genes
        for trait in probabilities[person]['trait']:
            probabilities[person]['trait'][trait] = probabilities[person]['trait'][trait] / total_trait

    return


if __name__ == "__main__":
    main()
