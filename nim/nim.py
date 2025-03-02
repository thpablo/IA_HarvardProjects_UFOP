import math
import random
import time


class Nim():

    def __init__(self, initial=[1, 3, 5, 7]):
        """
        Initialize game board.
        Each game board has
            - `piles`: a list of how many elements remain in each pile
            - `player`: 0 or 1 to indicate which player's turn
            - `winner`: None, 0, or 1 to indicate who the winner is
        """
        self.piles = initial.copy()
        self.player = 0
        self.winner = None

    @classmethod
    def available_actions(cls, piles):
        """
        Nim.available_actions(piles) takes a `piles` list as input
        and returns all of the available actions `(i, j)` in that state.

        Action `(i, j)` represents the action of removing `j` items
        from pile `i` (where piles are 0-indexed).
        """
        actions = set()
        for i, pile in enumerate(piles):
            for j in range(1, pile + 1):
                actions.add((i, j))
        return actions

    @classmethod
    def other_player(cls, player):
        """
        Nim.other_player(player) returns the player that is not
        `player`. Assumes `player` is either 0 or 1.
        """
        return 0 if player == 1 else 1

    def switch_player(self):
        """
        Switch the current player to the other player.
        """
        self.player = Nim.other_player(self.player)

    def move(self, action):
        """
        Make the move `action` for the current player.
        `action` must be a tuple `(i, j)`.
        """
        pile, count = action

        # Check for errors
        if self.winner is not None:
            raise Exception("Game already won")
        elif pile < 0 or pile >= len(self.piles):
            raise Exception("Invalid pile")
        elif count < 1 or count > self.piles[pile]:
            raise Exception("Invalid number of objects")

        # Update pile
        self.piles[pile] -= count
        self.switch_player()

        # Check for a winner
        if all(pile == 0 for pile in self.piles):
            self.winner = self.player


class NimAI():

    def __init__(self, alpha=0.5, epsilon=0.1):
        """
        Initialize AI with an empty Q-learning dictionary,
        an alpha (learning) rate, and an epsilon rate.

        The Q-learning dictionary maps `(state, action)`
        pairs to a Q-value (a number).
         - `state` is a tuple of remaining piles, e.g. (1, 1, 4, 4)
         - `action` is a tuple `(i, j)` for an action
        """
        self.q = dict()
        self.alpha = alpha
        self.epsilon = epsilon

    def update(self, old_state, action, new_state, reward):
        """
        Update Q-learning model, given an old state, an action taken
        in that state, a new resulting state, and the reward received
        from taking that action.
        """
        old = self.get_q_value(old_state, action)
        best_future = self.best_future_reward(new_state)
        self.update_q_value(old_state, action, old, reward, best_future)

    def get_q_value(self, state, action):
        """
        Retorna o valor Q para o estado `state` e a ação `action`.
        Se o par `(state, action)` ainda não tiver um valor armazenado no dicionário `self.q`,
        retorna 0 como valor padrão.
        """
        q_value = (tuple(state), action)  # Converte o estado em tupla para garantir que seja hashável
        return self.q.get(q_value, 0)  # Retorna o valor Q armazenado ou 0 se não existir


    def update_q_value(self, state, action, old_q, reward, future_rewards):
        """
        Atualiza o valor Q para um determinado estado `state` e ação `action`.

        O valor é atualizado de acordo com a fórmula de aprendizado por reforço:

        Q(s, a) <- old value estimate
                   + alpha * (new value estimate - old value estimate)

        onde:
        - `old value estimate` é o valor Q anterior (old_q)
        - `alpha` é a taxa de aprendizado
        - `new value estimate` é a soma da recompensa atual e a melhor estimativa de recompensas futuras
        """
        new_q = old_q + self.alpha * (reward + future_rewards - old_q)  # Aplica a equação de atualização do Q-learning
        
        self.q[(tuple(state), action)] = new_q  # Armazena o novo valor Q no dicionário


    def best_future_reward(self, state):
        """
        Dado um estado `state`, verifica todas as ações possíveis e retorna o maior valor Q entre elas.

        - Se o estado não tiver ações disponíveis, retorna 0.
        - Se não houver valores Q armazenados para essas ações, assume-se 0.
        """
        available_actions = Nim.available_actions(state)  # Obtém todas as ações possíveis no estado

        if len(available_actions) == 0:
            return 0  # Se não houver ações disponíveis, não há recompensa futura possível

        max_q = float('-inf')  # Inicializa com um valor muito baixo
        for action in available_actions:
            q_value = self.get_q_value(state, action)  # Obtém o valor Q para cada ação
            
            if q_value > max_q:
                max_q = q_value  # Atualiza o maior valor Q encontrado

        return max_q  # Retorna o melhor valor Q disponível no estado


    def choose_action(self, state, epsilon=True):
        """
        Dado um estado `state`, retorna a ação `(i, j)` que o agente deve tomar.

        - Se `epsilon` for `False`, escolhe a ação com o maior valor Q.
        - Se `epsilon` for `True`, há uma chance `self.epsilon` de escolher uma ação aleatória
          (exploração) e `1 - self.epsilon` de escolher a melhor ação conhecida (exploração baseada no Q-learning).
        """
        available_actions = Nim.available_actions(state)  # Obtém todas as ações disponíveis

        if len(available_actions) == 0:
            return None  # Se não houver ações disponíveis, não há ação a escolher
        
        # Com probabilidade `epsilon`, escolhe uma ação aleatória (exploração)
        if epsilon and random.uniform(0,1) < self.epsilon:
            return random.choice(list(available_actions))
        
        # Caso contrário, escolhe a ação com o maior valor Q conhecido (exploração baseada em experiência)
        q_values_dict = {}  # Dicionário para armazenar os valores Q de cada ação
        for action in available_actions:
            value = self.get_q_value(state, action)  # Obtém o valor Q da ação
            q_values_dict[action] = value 

        max_action = max(q_values_dict, key=q_values_dict.get)  # Escolhe a ação com maior valor Q
        return max_action


def train(n):
    """
    Train an AI by playing `n` games against itself.
    """

    player = NimAI()

    # Play n games
    for i in range(n):
        print(f"Playing training game {i + 1}")
        game = Nim()

        # Keep track of last move made by either player
        last = {
            0: {"state": None, "action": None},
            1: {"state": None, "action": None}
        }

        # Game loop
        while True:

            # Keep track of current state and action
            state = game.piles.copy()
            action = player.choose_action(game.piles)

            # Keep track of last state and action
            last[game.player]["state"] = state
            last[game.player]["action"] = action

            # Make move
            game.move(action)
            new_state = game.piles.copy()

            # When game is over, update Q values with rewards
            if game.winner is not None:
                player.update(state, action, new_state, -1)
                player.update(
                    last[game.player]["state"],
                    last[game.player]["action"],
                    new_state,
                    1
                )
                break

            # If game is continuing, no rewards yet
            elif last[game.player]["state"] is not None:
                player.update(
                    last[game.player]["state"],
                    last[game.player]["action"],
                    new_state,
                    0
                )

    print("Done training")

    # Return the trained AI
    return player


def play(ai, human_player=None):
    """
    Play human game against the AI.
    `human_player` can be set to 0 or 1 to specify whether
    human player moves first or second.
    """

    # If no player order set, choose human's order randomly
    if human_player is None:
        human_player = random.randint(0, 1)

    # Create new game
    game = Nim()

    # Game loop
    while True:

        # Print contents of piles
        print()
        print("Piles:")
        for i, pile in enumerate(game.piles):
            print(f"Pile {i}: {pile}")
        print()

        # Compute available actions
        available_actions = Nim.available_actions(game.piles)
        time.sleep(1)

        # Let human make a move
        if game.player == human_player:
            print("Your Turn")
            while True:
                pile = int(input("Choose Pile: "))
                count = int(input("Choose Count: "))
                if (pile, count) in available_actions:
                    break
                print("Invalid move, try again.")

        # Have AI make a move
        else:
            print("AI's Turn")
            pile, count = ai.choose_action(game.piles, epsilon=False)
            print(f"AI chose to take {count} from pile {pile}.")

        # Make move
        game.move((pile, count))

        # Check for winner
        if game.winner is not None:
            print()
            print("GAME OVER")
            winner = "Human" if game.winner == human_player else "AI"
            print(f"Winner is {winner}")
            return
