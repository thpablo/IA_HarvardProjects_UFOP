from logic import *

AKnight = Symbol("A is a Knight")
AKnave = Symbol("A is a Knave")

BKnight = Symbol("B is a Knight")
BKnave = Symbol("B is a Knave")

CKnight = Symbol("C is a Knight")
CKnave = Symbol("C is a Knave")

# Puzzle 0
# A says "I am both a knight and a knave."
knowledge0 = And(
    # A is either a knight or a knave
    Or(AKnight, AKnave),
    # If A is a knight, then A is not a knave
    Implication(AKnight, Not(AKnave)),
    # If A is a knave, then A is not a knight
    Implication(AKnave, Not(AKnight)),
    # If A is a knight, then A is both a knight and a knave
    Implication(AKnight, And(AKnight, AKnave)),
)

# Puzzle 1
# A says "We are both knaves."
# B says nothing.
knowledge1 = And(
    # A is either a knight or a knave
    Or(AKnight, AKnave),
    # B is either a knight or a knave
    Or(BKnight, BKnave),
    # If A is a knight, then A is not a knave
    Implication(AKnight, Not(AKnave)),
    # If A is a knave, then A is not a knight
    Implication(BKnight, Not(BKnave)),
    # If A is a knight, then A is both a knight and a knave
    Implication(AKnight, And(AKnave, BKnave)),
    # If A is a knave, then A is not both a knight and a knave
    Implication(AKnave, Not(And(AKnave, BKnave))),
)

# Puzzle 2
# A says "We are the same kind."
# B says "We are of different kinds."
knowledge2 = And(
    # A is either a knight or a knave
    Or(AKnight, AKnave),
    # B is either a knight or a knave
    Or(BKnight, BKnave),
    # If A is a knight, then A is not a knave
    Implication(AKnight, Not(AKnave)),
    # If A is a knave, then A is not a knight
    Implication(AKnave, Not(AKnight)),
    # If B is a knight, then A and B are the same kind
    Implication(AKnight, Or(And(AKnight, BKnight), And(AKnave, BKnave))),
    # If B is a knave, then A and B are not the same kind
    Implication(AKnave, Not(Or(And(AKnight, BKnight), And(AKnave, BKnave)))),
    # If B is a knight, then A abd B are not the same kind
    Implication(BKnight, Or(And(AKnight, BKnave), And(AKnave, BKnight))),
    # If B is a knave, then A and B are the same kind
    Implication(BKnave, Not(Or(And(AKnight, BKnave), And(AKnave, BKnight)))),
)

# Puzzle 3
# A says either "I am a knight." or "I am a knave.", but you don't know which.
# B says "A said 'I am a knave'."
# B says "C is a knave."
# C says "A is a knight."
knowledge3 = And(
     # A is either a knight or a knave
    Or(AKnight, AKnave),
    # B is either a knight or a knave
    Or(BKnight, BKnave),
    # C is either a knight or a knave
    Or(CKnight, CKnave),
    # If A is a knight, then A is not a knave
    Implication(AKnight, Not(AKnave)),
    # If A is a knave, then A is not a knight
    Implication(AKnave, Not(AKnight)),
    # If B is a knight, then A is a knave
    Implication(BKnight, AKnave),
    # If B is a knave, then A is a knight
    Implication(BKnave, AKnight),
    # If C is a knight, then C is not a knave
    Implication(CKnight, Not(CKnave)),
    # If C is a knave, then C is not a knight
    Implication(CKnave, Not(CKnight)),
    # If C is a knight, then A is a knight
    Implication(CKnight, AKnight),
    # If C is a knave, then A is not a knight
    Implication(CKnave, Not(AKnight)),
    # If B is a knight, then C is a knave and A is a knave
    Implication(BKnight, And(CKnave, AKnave)),
    # If B is a knave, then C is a knight and A is a knight
    Implication(BKnave, And(CKnight, AKnight)),
    # If A is a knave, then A are not a knight and a knave, because A always lies
    Implication(AKnave, Not(Or(AKnight, AKnave))),
)


def main():
    symbols = [AKnight, AKnave, BKnight, BKnave, CKnight, CKnave]
    puzzles = [
        ("Puzzle 0", knowledge0),
        ("Puzzle 1", knowledge1),
        ("Puzzle 2", knowledge2),
        ("Puzzle 3", knowledge3)
    ]
    for puzzle, knowledge in puzzles:
        print(puzzle)
        if len(knowledge.conjuncts) == 0:
            print("    Not yet implemented.")
        else:
            for symbol in symbols:
                if model_check(knowledge, symbol):
                    print(f"    {symbol}")


if __name__ == "__main__":
    main()
